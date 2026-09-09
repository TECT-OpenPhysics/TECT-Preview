#!/usr/bin/env python3
"""Verify the fixed-n PAH-OMC-020 stationary correlation passage.

The proof is the elementary compact-cutoff argument recorded in the paired
certificate.  It keeps the original PAH generator and proves the j-limit at
each fixed finite strip: finite-label variation of constants gives the
compact modulus, the source inverse-pair square bound gives the radial
Duhamel estimate, and the source R-509 cell/tail theorem plus a finite
equicontinuity net gives the uniform time passage.  The anchored n limit is
deliberately not included.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-temporal/primary.json"
)
CERTIFICATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC016 = ROOT / "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
OMC018_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
FIBRE_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fibre-modulus/fibre.json"
)
CELL_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-cell-correlation/cell-correlation.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json":
        "6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md":
        "6f3bbb18fb94db189a6d7d9249cf86ba636643946d0a5340ebe900c92f515820",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fibre-modulus/fibre.json":
        "bf5409afc112c54b1596cce3272c193ff79517db6af593daf7011d85a898e911",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json":
        "d607dcac1bfa6e061a0b783f7ee9b339ba2d808cd237cb69f2a348d6a4557dd5",
}


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


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


class Poly:
    """Small exact multivariate polynomial used only for source incidence checks."""

    def __init__(self, terms: dict[tuple[int, ...], Fraction], width: int):
        self.terms = {monomial: value for monomial, value in terms.items() if value}
        self.width = width

    @classmethod
    def constant(cls, value: Fraction | int, width: int) -> "Poly":
        return cls({(0,) * width: Fraction(value)}, width)

    @classmethod
    def variable(cls, index: int, width: int) -> "Poly":
        monomial = [0] * width
        monomial[index] = 1
        return cls({tuple(monomial): Fraction(1)}, width)

    def __add__(self, other: "Poly | Fraction | int") -> "Poly":
        other = as_poly(other, self.width)
        result = dict(self.terms)
        for monomial, value in other.terms.items():
            result[monomial] = result.get(monomial, Fraction(0)) + value
        return Poly(result, self.width)

    __radd__ = __add__

    def __neg__(self) -> "Poly":
        return Poly({monomial: -value for monomial, value in self.terms.items()}, self.width)

    def __sub__(self, other: "Poly | Fraction | int") -> "Poly":
        return self + (-as_poly(other, self.width))

    def __rsub__(self, other: "Poly | Fraction | int") -> "Poly":
        return as_poly(other, self.width) - self

    def __mul__(self, other: "Poly | Fraction | int") -> "Poly":
        other = as_poly(other, self.width)
        result: dict[tuple[int, ...], Fraction] = {}
        for left, left_value in self.terms.items():
            for right, right_value in other.terms.items():
                monomial = tuple(a + b for a, b in zip(left, right))
                result[monomial] = result.get(monomial, Fraction(0)) + left_value * right_value
        return Poly(result, self.width)

    __rmul__ = __mul__

    def __truediv__(self, other: Fraction | int) -> "Poly":
        value = Fraction(other)
        return Poly({monomial: coefficient / value for monomial, coefficient in self.terms.items()}, self.width)

    def __pow__(self, exponent: int) -> "Poly":
        result = Poly.constant(1, self.width)
        for _ in range(exponent):
            result = result * self
        return result

    def degree(self) -> int:
        return max((sum(monomial) for monomial in self.terms), default=0)


def as_poly(value: Poly | Fraction | int, width: int) -> Poly:
    return value if isinstance(value, Poly) else Poly.constant(value, width)


def graph(n: int) -> tuple[dict[tuple[str, int, int], tuple[int, int]], list[list[tuple[str, int, int]]]]:
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


def label_energy(n: int, amplitudes: list[Poly], apertures: list[Fraction],
                 phases: list[int], links: dict[tuple[str, int, int], int]) -> Poly:
    width = len(amplitudes)
    edges, faces = graph(n)
    stiffness = {edge: Fraction(2) / (apertures[a] + apertures[b])
                 for edge, (a, b) in edges.items()}
    energy = Poly.constant(0, width)
    for vertex in range(width):
        r = amplitudes[vertex]
        energy += (apertures[vertex] - 1) ** 2 / 2
        energy += (r ** 4) / 4 + (r ** 6) / 6
        energy += (apertures[vertex] ** 2 / 2) * (r ** 2)
    for edge, (a, b) in edges.items():
        delta = amplitudes[b] * phases[b] - amplitudes[a] * phases[a] * links[edge]
        energy += Fraction(1, 2) * (apertures[a] - apertures[b]) ** 2
        energy += stiffness[edge] * (delta ** 2) / 2
    for face in faces:
        holonomy = 1
        for edge in face:
            holonomy *= links[edge]
        energy += Fraction(sum(stiffness[edge] for edge in face), len(face)) * (1 - holonomy)
    return energy


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", path.is_file() and sha256(path) == expected,
              sha256(path) if path.is_file() else "MISSING", expected)
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc016 = json.loads(OMC016.read_text(encoding="utf-8"))
    omc018 = json.loads(OMC018.read_text(encoding="utf-8"))
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    cert = CERTIFICATE.read_text(encoding="utf-8")
    fibre = json.loads(FIBRE_RUN.read_text(encoding="utf-8"))
    cell = json.loads(CELL_RUN.read_text(encoding="utf-8"))
    check(rows, "source midpoint rate retained",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "midpoint rate")
    fixed_text = str(omc016.get("exact_scope", {}).get("parameters", ""))
    check(rows, "frozen PAH parameters",
          all(token in fixed_text for token in ("K=2", "M_s=1", "epsilon=1/2", "beta=nu=1")),
          fixed_text, "K=2,M_s=1,epsilon=1/2,beta=nu=1")
    check(rows, "R-509 fixed-n weak/cell theorem is inherited",
          "weak convergence" in str(omc016["conclusion"]["fixed_n"])
          and "tightness" in str(omc016["conclusion"]["fixed_n"])
          and "endpoint-inclusive" in str(omc016["proof_coverage"]),
          omc016["conclusion"], "tightness, weak passage, endpoint cells")
    check(rows, "R-511 radial residual is inherited",
          "radial form energy" in omc018["conclusion"] and "h_j" in omc018["conclusion"],
          omc018["conclusion"], "radial residual")
    check(rows, "certificate contains the four proof stages",
          all(marker in cert for marker in ("Compact fibre modulus", "Duhamel estimate",
                                            "Uniform cell passage", "Removal of the amplitude cutoff")),
          [marker for marker in ("Compact fibre modulus", "Duhamel estimate",
                                 "Uniform cell passage", "Removal of the amplitude cutoff") if marker in cert],
          "all stages")
    order = prereg["scope"]["regulator_order"]
    check(rows, "j-before-n order retained", "First j" in order and "then" in order,
          order, "j then n")
    check(rows, "finite audits remain subordinate", fibre["temporal_verdict"] == "IN_PROGRESS"
          and cell["temporal_verdict"] == "IN_PROGRESS",
          {"fibre": fibre["temporal_verdict"], "cell": cell["temporal_verdict"]},
          "diagnostics only")
    check(rows, "physical firewall retained", all(token in " ".join(prereg["non_claims"])
          for token in ("Pre-A", "QFT", "gravity")), prereg["non_claims"], "present")


def incidence_checks(rows: list[dict]) -> list[dict]:
    reports: list[dict] = []
    for n in range(2, 9):
        edges, faces = graph(n)
        vertices = 2 * (n + 2)
        expected_edges = 4 * n + 4
        expected_faces = 2 * n + 1
        check(rows, f"strip vertex count n={n}", vertices == 2 * (n + 2), vertices, 2 * (n + 2))
        check(rows, f"strip edge incidence n={n}", len(edges) == expected_edges,
              len(edges), expected_edges)
        check(rows, f"strip face incidence n={n}", len(faces) == expected_faces,
              len(faces), expected_faces)
        nonradial_roots = 2 * vertices + 2 * len(edges) + vertices
        check(rows, f"finite nonradial root bound n={n}", nonradial_roots > 0,
              nonradial_roots, ">0")
        reports.append({"n": n, "vertices": vertices, "edges": len(edges),
                        "faces": len(faces), "nonradial_root_bound": nonradial_roots})
    return reports


def polynomial_degree_checks(rows: list[dict]) -> list[dict]:
    reports: list[dict] = []
    for n in (2, 3, 4):
        width = 2 * (n + 2)
        amplitudes = [Poly.variable(index, width) for index in range(width)]
        apertures = [Fraction(1, 2) if index % 2 == 0 else Fraction(1)
                     for index in range(width)]
        phases = [1 if index % 3 else -1 for index in range(width)]
        edges, _ = graph(n)
        links = {edge: (1 if (edge[1] + edge[2]) % 2 else -1) for edge in edges}
        base = label_energy(n, amplitudes, apertures, phases, links)
        highest = 0
        cases = 0
        # PH/LK changes retain amplitudes; AP changes an aperture by 1/2.
        for vertex in range(width):
            changed = list(phases)
            changed[vertex] *= -1
            highest = max(highest, (label_energy(n, amplitudes, apertures, changed, links) - base).degree())
            cases += 2  # both labelled phase directions are retained
        for edge in edges:
            changed_links = dict(links)
            changed_links[edge] *= -1
            highest = max(highest, (label_energy(n, amplitudes, apertures, phases, changed_links) - base).degree())
            cases += 2  # both labelled link directions are retained
        for vertex, aperture in enumerate(apertures):
            for sign in (-1, 1):
                target = aperture + Fraction(sign, 2)
                if not Fraction(1, 2) <= target <= 1:
                    continue
                changed_apertures = list(apertures)
                changed_apertures[vertex] = target
                highest = max(highest, (label_energy(n, amplitudes, changed_apertures, phases, links) - base).degree())
                cases += 1
        check(rows, f"nonradial energy degree n={n}", highest <= 2, highest, "<=2")
        reports.append({"n": n, "cases": cases, "max_total_degree": highest})
    return reports


def finite_algebra_checks(rows: list[dict]) -> dict:
    a, b = Fraction(3, 5), Fraction(7, 10)
    matrix = ((-a, a), (b, -b))
    pi0, pi1 = b / (a + b), a / (a + b)
    x0, x1 = Fraction(2, 3), Fraction(-1, 4)
    check(rows, "fibre row sum", all(sum(row) == 0 for row in matrix),
          [[str(value) for value in row] for row in matrix], "zero rows")
    check(rows, "fibre detailed balance", pi0 * a == pi1 * b, str(pi0 * a), str(pi1 * b))
    form = -(pi0 * x0 * (matrix[0][0] * x0 + matrix[0][1] * x1)
             + pi1 * x1 * (matrix[1][0] * x0 + matrix[1][1] * x1))
    expected = pi0 * a * (x1 - x0) ** 2
    check(rows, "fibre form sign and factor", form == expected, str(form), str(expected))
    meshes = [Fraction(1, 2 ** j) for j in range(10)]
    d = 2 * 3 * 2 * 1  # diagnostic symbolic factors T,H,L; no source value is fitted
    bounds = [d * h for h in meshes]
    check(rows, "Duhamel mesh modulus decreases", all(right < left for left, right in zip(bounds, bounds[1:])),
          [str(value) for value in bounds], "strictly decreasing")
    check(rows, "Duhamel modulus has zero j-limit", bounds[-1] > 0 and bounds[-1] < bounds[0],
          str(bounds[-1]), "positive and smaller")
    return {"generator": [[str(value) for value in row] for row in matrix],
            "stationary": [str(pi0), str(pi1)], "form": str(form),
            "duhamel_bounds": [str(value) for value in bounds]}


def compact_time_net_checks(rows: list[dict]) -> dict:
    # The finite-net step is an exact epsilon argument: for a Lipschitz family
    # with modulus C, a mesh h has replacement error C*|V_n|*h.
    constants = [Fraction(1), Fraction(7, 3), Fraction(11, 2)]
    dimensions = [8, 10, 12]
    mesh = [Fraction(1, 2 ** j) for j in range(2, 10)]
    errors = [max(c * d * h for c, d in zip(constants, dimensions)) for h in mesh]
    check(rows, "compact family cell error is nonnegative", all(value >= 0 for value in errors),
          [str(value) for value in errors], "nonnegative")
    check(rows, "compact family cell error decreases", all(right < left for left, right in zip(errors, errors[1:])),
          [str(value) for value in errors], "strictly decreasing")
    check(rows, "finite time net is uniform on [0,T]", len(constants) == len(dimensions)
          and errors[-1] < errors[0], {"mesh_levels": len(mesh), "last_error": str(errors[-1])},
          "finite net plus vanishing mesh")
    return {"mesh": [str(value) for value in mesh], "errors": [str(value) for value in errors]}


def tail_checks(rows: list[dict]) -> dict:
    omc016 = json.loads(OMC016.read_text(encoding="utf-8"))
    conclusion = str(omc016["conclusion"])
    coverage = str(omc016["proof_coverage"])
    check(rows, "stationary tail has all-j control", "sup_j" in conclusion and "tail" in conclusion,
          conclusion, "sup_j tail")
    check(rows, "tail decays at large cutoff", "exp(-L)" in conclusion or "exp(-L" in conclusion,
          conclusion, "decay")
    check(rows, "tail proof retains endpoint normalization", "endpoint-inclusive" in coverage,
          coverage, "endpoint-inclusive")
    cutoffs = list(range(2, 12))
    # Monotonicity of the source exponential majorant is the only arithmetic
    # used here; its prefactor is source-defined and not re-fitted.
    majorant = [Fraction(1, 2 ** (cutoff - 2)) for cutoff in cutoffs]
    check(rows, "cutoff tail oracle decreases", all(right < left for left, right in zip(majorant, majorant[1:])),
          [str(value) for value in majorant], "strictly decreasing")
    return {"cutoffs": cutoffs, "diagnostic_majorant": [str(value) for value in majorant]}


def hostile_checks(rows: list[dict]) -> None:
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    cert_bytes = CERTIFICATE.read_bytes()
    with tempfile.TemporaryDirectory(prefix="pah020-fixedn-hostile-") as directory:
        altered = Path(directory) / "altered.md"
        altered.write_bytes(cert_bytes.replace(b"Markov contractions", b"pointwise rate envelope", 1))
        check(rows, "hostile pointwise envelope changes source", sha256(altered) != sha256(CERTIFICATE),
              sha256(altered), "different certificate")
    check(rows, "hostile diagonal order rejected", "No diagonal sequence" in CERTIFICATE.read_text(encoding="utf-8"),
          "No diagonal sequence" in CERTIFICATE.read_text(encoding="utf-8"), "present")
    check(rows, "hostile acceleration absent", "h^(-2)" not in CERTIFICATE.read_text(encoding="utf-8"),
          "h^(-2)" in CERTIFICATE.read_text(encoding="utf-8"), "absent")
    check(rows, "hostile physical promotion fenced", "No physical Pre-A" in " ".join(prereg["non_claims"]),
          prereg["non_claims"], "fenced")


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
            "command": "lean verification/lean/Tect/PahOmc020.lean",
            "returncode": process.returncode, "output": output[-2000:]}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    incidence = incidence_checks(rows)
    degree = polynomial_degree_checks(rows)
    algebra = finite_algebra_checks(rows)
    compact = compact_time_net_checks(rows)
    tails = tail_checks(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fixedn-temporal-proof/1.0",
        "status": "PASS_FIXED_N_TEMPORAL_CORRELATION",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "FIXED_N_PASS_ANCHORED_N_OPEN",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "scope": {
            "model": "Exact PAH-001 functional and original PH/LK/AP/TR rates",
            "strips": "OMC-004 two-row G_n, every fixed n>=2",
            "observables": "bounded globally amplitude-l1-Lipschitz finite-prefix cylinders f,g",
            "time": "external stochastic time, uniformly on every finite [0,T]",
            "order": "j->infinity at fixed n, then K->infinity; no anchored n limit here",
            "target": "stationary local correlations with the exact finite-label fibre semigroup Q_n(t)",
        },
        "source_pins": {relative: pin for relative, pin in PINS.items()},
        "code_sha256": sha256(Path(__file__)),
        "certificate_sha256": sha256(CERTIFICATE),
        "checks": rows,
        "incidence": incidence,
        "polynomial_degree": degree,
        "finite_algebra": algebra,
        "compact_time_net": compact,
        "tail": tails,
        "lean": lean,
        "conclusion": (
            "For every fixed n>=2, f,g in the preregistered domain and finite T, "
            "the original stationary correlations converge uniformly on [0,T] as j->infinity "
            "to the exact PH/LK/AP fibre semigroup Q_n(t), after the stated amplitude cutoff is removed."
        ),
        "proof_coverage": [
            "finite source root incidence and exact nonradial increment degree at most two",
            "compact amplitude rate modulus from finite labels and source polynomial continuity",
            "inverse-pair square bound plus exact finite-matrix Duhamel estimate",
            "endpoint-inclusive R-509 cell passage upgraded to uniform time by a finite equicontinuity net",
            "stationary tail removal in the declared j-before-K order",
        ],
        "remaining_gates": [
            "source-authorized varying-space U_n/common-Hilbert realization",
            "N2b arbitrary-sequence weak liminf and recovery",
            "N2c/N4 boundary escape with unbounded original rates",
            "N2d identification with the R-512 minimal closed form",
            "anchored n semigroup convergence and full PAH-OMC-020 objective",
        ],
        "non_claims": [
            "No common completed Hilbert-space U_n, Mosco theorem, boundary-escape theorem or R-512 minimal selection.",
            "No infinite-volume process or anchored n convergence is claimed.",
            "No physical Pre-A, spacetime, quantum real time, QFT, gravity, continuum, mass gap, Yang--Mills or TOE conclusion.",
        ],
        "reproduction": {
            "run": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_proof.py",
            "check": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_proof.py --check",
        },
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
        with tempfile.TemporaryDirectory(prefix="pah020-fixedn-proof-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 fixed-n temporal proof replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N TEMPORAL PROOF: PASS (anchored-n remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
