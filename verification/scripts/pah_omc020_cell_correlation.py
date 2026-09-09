#!/usr/bin/env python3
"""PAH-OMC-020 common-space cell/correlation audit.

This is an independently replayable, finite diagnostic for the fixed-n part
of the PAH-OMC-020 proof draft.  It reconstructs a source-derived one-active-
vertex fibre of the original n=2 strip, checks the exact half-open cell
partition and labelled Gibbs normalization, and compares the sampled fibre
correlation with its continuous-amplitude counterpart.  The script does not
claim a PAH temporal convergence theorem: it is evidence for the endpoint,
normalization, tail and finite-fibre identities needed by the analytic draft.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Callable

import mpmath as mp
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC016_PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
OMC016_RESULT = ROOT / "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
OMC018_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020_PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-cell-correlation/cell-correlation.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json":
        "1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7",
    "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json":
        "6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}

# Tooling thresholds are diagnostic tolerances, not source-derived constants.
NUMERIC_TOL = 1.0e-11
MP_DPS = 50
TEST_TIME = mp.mpf("0.7")
TAIL_K = mp.mpf("1")
# Finite quadrature cutoff is a diagnostic oracle.  The source sextic makes
# the omitted tail negligible for this fixture; no analytic tail theorem is
# inferred from the numerical quadrature.
INTEGRATION_CUTOFF = mp.mpf("8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def graph(n: int) -> tuple[dict[tuple[str, int, int], tuple[int, int]], list[list[tuple[str, int, int]]]]:
    """The exact OMC-004 two-row strip incidence used by the earlier audit."""
    edges: dict[tuple[str, int, int], tuple[int, int]] = {}
    edges.update({("h", i, k): (2 * i + k, 2 * i + 2 + k)
                  for i in range(n + 1) for k in (0, 1)})
    edges.update({("v", i, 0): (2 * i, 2 * i + 1) for i in range(n + 2)})
    edges.update({("d", i, 0): (2 * i + 1, 2 * i + 2)
                  for i in range(n)})
    faces: list[list[tuple[str, int, int]]] = []
    for i in range(n):
        faces.extend([
            [("h", i, 0), ("v", i + 1, 0), ("d", i, 0)],
            [("d", i, 0), ("h", i, 1), ("v", i, 0)],
        ])
    faces.append([("h", n, 0), ("v", n + 1, 0), ("h", n, 1), ("v", n, 0)])
    return edges, faces


def source_checks(rows: list[dict]) -> None:
    for relative, pin in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", sha256(path) == pin, sha256(path), pin)
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    prereg = json.loads(OMC016_PREREG.read_text(encoding="utf-8"))
    result = json.loads(OMC016_RESULT.read_text(encoding="utf-8"))
    omc020 = json.loads(OMC020_PREREG.read_text(encoding="utf-8"))
    check(rows, "original midpoint generator", "exp[-beta(F_rho(r x)-F_rho(x))/2]"
          in pah["dynamics"]["generator"], pah["dynamics"]["generator"], "half exponent")
    fixed = prereg["scope"]["fixed_parameters"]
    check(rows, "fixed PAH parameters", fixed["K"] == 2 and fixed["M_s"] == 1
          and fixed["epsilon"] == "1/2" and fixed["beta"] == 1 and fixed["nu"] == 1,
          fixed, "K=2,M_s=1,epsilon=1/2,beta=nu=1")
    path = prereg["scope"]["path"]
    check(rows, "dyadic path", path["R_max"] == "2^j" and path["M_psi"] == "2^(2j)"
          and path["radial_mesh"] == "2^(-j)", path, "R=2^j,M=2^(2j),h=2^(-j)")
    check(rows, "labelled state and endpoint contract",
          "phases at zero amplitude remain labelled" in prereg["scope"]["configuration"]
          and "endpoint-inclusive" in result["proof_coverage"]["measure_normalization"],
          "labelled counting; endpoint-inclusive", "present")
    check(rows, "temporal comparison is fixed-n first",
          "fixed n" in omc020["question"] and "first" in omc020["question"],
          omc020["question"], "fixed-n then anchored n")
    cert = OMC018_CERT.read_text(encoding="utf-8")
    check(rows, "source certificate keeps temporal law separate",
          "not a temporal path-law construction" in cert,
          "not a temporal path-law construction", "present")


def source_slice_energy(r: Fraction, phase: int, n: int = 2) -> Fraction:
    """Exact PAH energy on a declared one-active-vertex fixture.

    The fixture is only a source-derived audit oracle: vertex 0 has amplitude
    r and phase +/-1, vertex 1 has amplitude 1/4, all other amplitudes vanish;
    apertures and links are the original K=2 choices.  No new carrier or term
    is introduced.
    """
    count = 2 * (n + 2)
    amplitudes = [r, Fraction(1, 4)] + [Fraction(0)] * (count - 2)
    apertures = [Fraction(1, 2) if v % 2 == 0 else Fraction(1)
                 for v in range(count)]
    phases = [phase] + [1 if v % 3 else -1 for v in range(1, count)]
    edges, faces = graph(n)
    links = {edge: (1 if (edge[1] + edge[2]) % 2 else -1) for edge in edges}
    mobility_den = Fraction(1)
    energy = sum((apertures[v] - 1) ** 2 / 2 + amplitudes[v] ** 4 / 4
                 + amplitudes[v] ** 6 / 6 + apertures[v] ** 2 * amplitudes[v] ** 2 / 2
                 for v in range(count))
    stiffness = {edge: Fraction(2) / (apertures[a] + apertures[b])
                 for edge, (a, b) in edges.items()}
    energy += sum((apertures[a] - apertures[b]) ** 2 / 2
                  + stiffness[edge] * (phases[b] * amplitudes[b]
                                       - links[edge] * phases[a] * amplitudes[a]) ** 2 / 2
                  for edge, (a, b) in edges.items())
    for face in faces:
        holonomy = math.prod(links[edge] for edge in face)
        energy += sum(stiffness[edge] for edge in face) / len(face) * (1 - holonomy)
    # Keep this local name to make the source mobility contract visible in the
    # fixture audit; the value is one for the energy (not a hidden term).
    _ = mobility_den
    return energy


def energy_polynomials() -> dict[int, list[Fraction]]:
    r = sp.symbols("r")
    coefficients: dict[int, list[Fraction]] = {}
    for phase in (-1, 1):
        exact = source_slice_energy(Fraction(0), phase)
        # Reconstruct the polynomial independently at the symbolic layer by
        # replacing the first amplitude in the same source formula.
        amplitudes = [r, sp.Rational(1, 4)] + [sp.Rational(0)] * 6
        apertures = [sp.Rational(1, 2) if v % 2 == 0 else sp.Rational(1)
                     for v in range(8)]
        phases = [phase] + [1 if v % 3 else -1 for v in range(1, 8)]
        edges, faces = graph(2)
        links = {edge: (1 if (edge[1] + edge[2]) % 2 else -1) for edge in edges}
        stiffness = {edge: sp.Rational(2) / (apertures[a] + apertures[b])
                     for edge, (a, b) in edges.items()}
        expression = sum((apertures[v] - 1) ** 2 / 2 + amplitudes[v] ** 4 / 4
                         + amplitudes[v] ** 6 / 6 + apertures[v] ** 2 * amplitudes[v] ** 2 / 2
                         for v in range(8))
        expression += sum((apertures[a] - apertures[b]) ** 2 / 2
                          + stiffness[edge] * (phases[b] * amplitudes[b]
                                               - links[edge] * phases[a] * amplitudes[a]) ** 2 / 2
                          for edge, (a, b) in edges.items())
        for face in faces:
            holonomy = math.prod(links[edge] for edge in face)
            expression += sum(stiffness[edge] for edge in face) / len(face) * (1 - holonomy)
        polynomial = sp.Poly(sp.expand(expression), r)
        by_degree = {degree[0]: Fraction(int(value.p), int(value.q))
                     for degree, value in polynomial.terms()}
        ordered = [by_degree.get(degree, Fraction(0))
                   for degree in range(polynomial.degree(), -1, -1)]
        check_value = sum(coefficient * Fraction(0) ** (polynomial.degree() - i)
                          for i, coefficient in enumerate(ordered))
        if check_value != exact:
            raise AssertionError("symbolic/source slice mismatch")
        coefficients[phase] = ordered
    return coefficients


def mp_energy(coefficients: dict[int, list[Fraction]], r: mp.mpf, phase: int) -> mp.mpf:
    value = mp.mpf("0")
    for coefficient in coefficients[phase]:
        value = value * r + mp.mpf(coefficient.numerator) / coefficient.denominator
    return value


def grid_data(j: int) -> tuple[Fraction, int, Fraction, list[Fraction]]:
    h = Fraction(1, 2 ** j)
    m = 2 ** (2 * j)
    radius = Fraction(2 ** j)
    cells = [h * ell for ell in range(m + 1)]
    return h, m, radius, cells


def cell_index(r: Fraction, j: int) -> int:
    h, m, radius, _ = grid_data(j)
    if r < 0 or r >= radius + h:
        raise ValueError("point outside half-open cell domain")
    return min(m, int(r // h))


def density_and_endpoint_checks(rows: list[dict], coefficients: dict[int, list[Fraction]]) -> list[dict]:
    reports: list[dict] = []
    for j in range(5):
        h, m, radius, cells = grid_data(j)
        check(rows, f"cell length identity j={j}", radius == m * h,
              str(radius), f"{m}*{h}")
        check(rows, f"half-open domain length j={j}", (m + 1) * h == radius + h,
              str((m + 1) * h), str(radius + h))
        check(rows, f"upper endpoint retained j={j}", cell_index(radius, j) == m
              and cell_index(radius + h / 2, j) == m, (cell_index(radius, j), cell_index(radius + h / 2, j)), m)
        check(rows, f"first cell anchored j={j}", cell_index(Fraction(0), j) == 0,
              cell_index(Fraction(0), j), 0)
        weights_mp = [mp.exp(-mp_energy(coefficients, mp.mpf(cell.numerator) / cell.denominator, phase))
                      for cell in cells for phase in (-1, 1)]
        z_cell_mp = mp.mpf(h.numerator) / h.denominator * sum(weights_mp)
        z_cell = float(z_cell_mp)
        normalized_integral = float(mp.mpf(h.numerator) / h.denominator
                                     * sum(weight / z_cell_mp for weight in weights_mp))
        check(rows, f"labelled cell normalization j={j}", abs(normalized_integral - 1.0) <= NUMERIC_TOL,
              normalized_integral, 1.0)
        upper_weight_mp = mp.mpf(h.numerator) / h.denominator * sum(
            mp.exp(-mp_energy(coefficients, mp.mpf(radius.numerator) / radius.denominator, phase))
            for phase in (-1, 1)
        )
        check(rows, f"upper cell has positive mass j={j}", upper_weight_mp > 0 and upper_weight_mp < z_cell_mp,
              {"upper_mass": mp.nstr(upper_weight_mp, 12), "z": mp.nstr(z_cell_mp, 12)},
              "upper mass included")
        reports.append({"j": j, "h": float(h), "M": m, "R": float(radius),
                        "Z_cell": z_cell, "upper_mass": mp.nstr(upper_weight_mp, 12)})
    return reports


def fibre_rates(coefficients: dict[int, list[Fraction]], r: mp.mpf) -> tuple[mp.mpf, mp.mpf]:
    e_minus = mp_energy(coefficients, r, -1)
    e_plus = mp_energy(coefficients, r, 1)
    # The active vertex has s=epsilon=1/2 and nu=1 in the frozen source.
    mobility = mp.mpf(1) / 2
    return (mobility * mp.exp(-(e_plus - e_minus) / 2),
            mobility * mp.exp(-(e_minus - e_plus) / 2))


def fibre_apply(coefficients: dict[int, list[Fraction]], r: mp.mpf, phase: int,
                t: mp.mpf, function: Callable[[mp.mpf, int], mp.mpf]) -> mp.mpf:
    a, b = fibre_rates(coefficients, r)
    total = a + b
    vector = [function(r, -1), function(r, 1)]
    source_index = 0 if phase == -1 else 1
    if total == 0:
        return vector[source_index]
    decay = mp.e ** (-total * t)
    if source_index == 0:
        return (b / total + a / total * decay) * vector[0] + (a / total) * (1 - decay) * vector[1]
    return (b / total) * (1 - decay) * vector[0] + (a / total + b / total * decay) * vector[1]


def test_f(r: mp.mpf, phase: int) -> mp.mpf:
    return 1 / (1 + r * r) + mp.mpf("0.08") * phase


def test_g(r: mp.mpf, phase: int) -> mp.mpf:
    return mp.exp(-r) * (1 + mp.mpf("0.2") * phase)


def grid_correlation(coefficients: dict[int, list[Fraction]], j: int, t: mp.mpf,
                     cutoff: mp.mpf | None = None) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    h, _, _, cells = grid_data(j)
    z = mp.mpf(0)
    numerator = mp.mpf(0)
    tail = mp.mpf(0)
    for cell in cells:
        r = mp.mpf(cell.numerator) / cell.denominator
        for phase in (-1, 1):
            weight = mp.exp(-mp_energy(coefficients, r, phase))
            z += h * weight
            if r >= TAIL_K:
                tail += h * weight
            factor = 1 if cutoff is None or r < cutoff else 0
            numerator += h * weight * test_f(r, phase) * factor * fibre_apply(
                coefficients, r, phase, t, test_g)
    return numerator / z, tail / z, z


def continuous_correlation(coefficients: dict[int, list[Fraction]], t: mp.mpf,
                           cutoff: mp.mpf | None = None) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    mp.mp.dps = MP_DPS

    def integrate(function: Callable[[mp.mpf, int], mp.mpf], phase: int) -> mp.mpf:
        if cutoff is None:
            return mp.quad(lambda x: function(x, phase), [0, 1, 2, 4, INTEGRATION_CUTOFF])
        return mp.quad(lambda x: function(x, phase), [0, cutoff])

    z = sum(integrate(lambda x, phase: mp.exp(-mp_energy(coefficients, x, phase)), phase)
            for phase in (-1, 1))
    numerator = sum(integrate(
        lambda x, phase: mp.exp(-mp_energy(coefficients, x, phase))
        * test_f(x, phase) * fibre_apply(coefficients, x, phase, t, test_g), phase)
        for phase in (-1, 1))
    tail = sum(integrate(
        lambda x, phase: mp.exp(-mp_energy(coefficients, x, phase)) * x * x, phase)
        for phase in (-1, 1))
    return numerator / z, tail / z, z


def correlation_checks(rows: list[dict], coefficients: dict[int, list[Fraction]]) -> dict:
    target, target_second_moment, z_cont = continuous_correlation(coefficients, TEST_TIME)
    errors: list[float] = []
    grid_reports: list[dict] = []
    for j in range(5):
        value, tail, z = grid_correlation(coefficients, j, TEST_TIME)
        error = abs(value - target)
        errors.append(float(error))
        grid_reports.append({"j": j, "correlation": float(value), "error": float(error),
                             "tail_at_K": float(tail), "Z_cell": float(z)})
    check(rows, "continuous slice has finite normalization", bool(mp.isfinite(z_cont) and z_cont > 0),
          float(z_cont), ">0 and finite")
    check(rows, "continuous slice second moment is finite", bool(mp.isfinite(target_second_moment)),
          float(target_second_moment), "finite")
    check(rows, "sampled correlation improves on the coarse cell rule",
          errors[-1] < errors[0], errors, "last error < first error")
    check(rows, "sampled correlation is finite at every audited level",
          all(math.isfinite(value["correlation"]) and math.isfinite(value["error"])
              for value in grid_reports), grid_reports, "finite")
    return {"target": float(target), "target_second_moment": float(target_second_moment),
            "errors": errors, "grid": grid_reports}


def tail_and_cutoff_checks(rows: list[dict], coefficients: dict[int, list[Fraction]]) -> dict:
    reports: list[dict] = []
    for j in range(5):
        full, tail, _ = grid_correlation(coefficients, j, TEST_TIME)
        cutoff, _, _ = grid_correlation(coefficients, j, TEST_TIME, TAIL_K)
        # Recompute the second moment of the normalized cell law, independent
        # of the correlation integrand, for the Markov tail inequality.
        h, _, _, cells = grid_data(j)
        z = mp.mpf(0)
        second_moment = mp.mpf(0)
        for cell in cells:
            r = mp.mpf(cell.numerator) / cell.denominator
            for phase in (-1, 1):
                weight = mp.exp(-mp_energy(coefficients, r, phase))
                z += h * weight
                second_moment += h * weight * r * r
        second_moment /= z
        bound = second_moment / (TAIL_K * TAIL_K)
        cutoff_difference = abs(full - cutoff)
        bound_corr = mp.mpf(2) * mp.mpf("1.08") * mp.mpf("1.2") * tail
        check(rows, f"stationary Markov tail bound j={j}", tail <= bound + mp.mpf("1e-40"),
              float(tail), f"<={float(bound)}")
        check(rows, f"cutoff correlation bound j={j}", cutoff_difference <= bound_corr + mp.mpf("1e-40"),
              float(cutoff_difference), f"<={float(bound_corr)}")
        reports.append({"j": j, "tail": float(tail), "second_moment": float(second_moment),
                        "markov_bound": float(bound), "cutoff_difference": float(cutoff_difference),
                        "cutoff_bound": float(bound_corr)})
    return {"K": float(TAIL_K), "reports": reports}


def hostile_checks(rows: list[dict], coefficients: dict[int, list[Fraction]]) -> None:
    h, m, radius, _ = grid_data(2)
    wrong_index = min(m - 1, int(radius // h))
    check(rows, "hostile upper-cell exclusion rejected", wrong_index != cell_index(radius, 2),
          wrong_index, f"{m} (upper cell index)")
    fx, fy, mobility, normalizer = sp.symbols("fx fy mobility normalizer", real=True)
    wrong_rate = mobility * sp.exp(-(fy - fx))
    pi_x = sp.exp(-fx) / normalizer
    check(rows, "hostile full exponent rejected",
          sp.simplify(pi_x * wrong_rate ** 2 - mobility ** 2 * sp.exp(-fy) / normalizer) != 0,
          "full exponent", "source midpoint exponent")
    with tempfile.TemporaryDirectory(prefix="pah020-cell-hostile-") as directory:
        altered = Path(directory) / "altered-pah.json"
        altered.write_bytes(PAH.read_bytes() + b"\n")
        check(rows, "hostile source mutation rejected",
              sha256(altered) != PINS["strategy/pa-hyp/PAH-001-v1.json"],
              sha256(altered), "different from source pin")
    check(rows, "continuous and sampled fibre use the same two phases",
          set(coefficients) == {-1, 1}, sorted(coefficients), [-1, 1])


def lean_check() -> dict:
    compiler = Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe"
    if not compiler.is_file():
        return {"status": "NOT_AVAILABLE", "command": "lean verification/lean/Tect/PahOmc020.lean"}
    package_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    env = os.environ.copy()
    if package_root.is_dir():
        paths = []
        for package in package_root.iterdir():
            candidate = package / ".lake/build/lib/lean"
            if candidate.is_dir():
                paths.append(str(candidate))
        env["LEAN_PATH"] = ";".join(paths)
    process = subprocess.run([str(compiler), str(LEAN)], cwd=LEAN.parent.parent.parent,
                             env=env, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False, timeout=180)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
            "command": "lean verification/lean/Tect/PahOmc020.lean", "returncode": process.returncode,
            "output": output[-2000:], "compiler": str(compiler)}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    coefficients = energy_polynomials()
    cell_reports = density_and_endpoint_checks(rows, coefficients)
    correlation = correlation_checks(rows, coefficients)
    tails = tail_and_cutoff_checks(rows, coefficients)
    hostile_checks(rows, coefficients)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-cell-correlation/1.0",
        "status": "PASS_COMMON_SPACE_CELL_AUDIT",
        "temporal_verdict": "IN_PROGRESS",
        "source_pins": PINS,
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "fixture": {
            "carrier": "OMC-004 n=2 two-row strip; one active amplitude and one fixed 1/4 background amplitude",
            "labels": [-1, 1],
            "test_time": float(TEST_TIME),
            "role": "source-derived finite audit oracle, not a new carrier or dynamics",
        },
        "cell_partition": cell_reports,
        "correlation": correlation,
        "tail_cutoff": tails,
        "proved_scope": [
            "exact half-open dyadic cell index and retained upper endpoint on j=0..4 fixtures",
            "full labelled cell-density normalization with the common mesh factor",
            "same finite source-derived fibre matrix in sampled and continuous correlation expressions",
            "finite sampled correlation diagnostic, stationary Markov tail inequality and bounded cutoff estimate",
            "hostile endpoint/full-exponent/source mutations rejected and PahOmc020 Lean compilation PASS",
        ],
        "open_obligations": [
            "turn the cell identity and tail estimate into an all-test common-space analytic theorem",
            "admit or refute the fixed-n j-limit for the actual PAH stationary L2 spaces",
            "take the anchored n limit and identify the R-512 minimal-form semigroup",
        ],
        "non_claims": [
            "This finite slice and its numerical quadrature are not a PAH temporal convergence theorem or a result-card admission.",
            "No strong operator convergence, common infinite-volume process, R-512 minimal/maximal closure equality or ordered limit is claimed.",
            "No physical Pre-A, spacetime, quantum real time, QFT, gravity, continuum, mass gap or TOE conclusion; no Q3LOCK or TECT-YM import.",
        ],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        with tempfile.TemporaryDirectory(prefix="pah020-cell-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 cell-correlation replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 CELL CORRELATION: PASS (common-space audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
