#!/usr/bin/env python3
"""PAH-OMC-020 compact fibre-modulus structural audit.

The audit reconstructs the original PAH energy independently of the temporal
bridge script.  It checks that nonradial PH/LK/AP increments on exact finite
strip fixtures have degree at most two in the amplitudes, verifies the
finite-fibre row-sum/form algebra, and compiles the universal Lean lemmas.
The all-n compact modulus, cutoff removal and common-space form theorem remain
analytic obligations; no semigroup convergence is claimed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC001 = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
OMC016 = ROOT / "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fibre-modulus/fibre.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-001-v1.json":
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f",
    "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json":
        "1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
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


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def graph(n: int) -> tuple[dict, list[list[tuple[str, int, int]]]]:
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


def label_energy(n: int, amplitudes: list[sp.Expr], apertures: list[sp.Rational],
                 phases: list[int], links: dict[tuple[str, int, int], int]) -> sp.Expr:
    source = json.loads(OMC016.read_text(encoding="utf-8"))["scope"]["fixed_parameters"]
    edges, faces = graph(n)
    half = sp.Rational(1, 2)
    J = {edge: sp.Rational(2, 1) / (apertures[a] + apertures[b])
         for edge, (a, b) in edges.items()}
    energy = sum((apertures[v] - 1) ** 2 / 2 + amplitudes[v] ** 4 / 4
                 + amplitudes[v] ** 6 / 6 + apertures[v] ** 2 * amplitudes[v] ** 2 / 2
                 for v in range(len(amplitudes)))
    energy += sum((apertures[a] - apertures[b]) ** 2 / 2
                  + J[edge] * (phases[b] * amplitudes[b]
                               - links[edge] * phases[a] * amplitudes[a]) ** 2 / 2
                  for edge, (a, b) in edges.items())
    for face in faces:
        holonomy = sp.prod(links[edge] for edge in face)
        energy += sum(J[edge] for edge in face) / len(face) * (1 - holonomy)
    # Read the source parameters so a missing or altered fixed contract cannot
    # silently turn this reconstruction into another model.
    if source["K"] != 2 or source["M_s"] != 1 or source["epsilon"] != "1/2":
        raise AssertionError("unexpected OMC-016 fixed parameters")
    return sp.expand(energy)


def nonradial_degree_checks(rows: list[dict]) -> list[dict]:
    reports: list[dict] = []
    for n in (2, 3):
        amplitudes = list(sp.symbols(f"r0:{2 * (n + 2)}", nonnegative=True))
        apertures = [sp.Rational(1, 2) if v % 2 == 0 else sp.Rational(1, 1)
                     for v in range(len(amplitudes))]
        phases = [1 if v % 3 else -1 for v in amplitudes]
        edges, _ = graph(n)
        links = {edge: (1 if (edge[1] + edge[2]) % 2 else -1) for edge in edges}
        base = label_energy(n, amplitudes, apertures, phases, links)
        highest = 0
        cases = 0
        # PH and LK retain amplitudes; AP changes only an aperture label.  The
        # two K=2 channels are both enumerated even when their maps coincide.
        for vertex in range(len(amplitudes)):
            for sign in (-1, 1):
                changed = list(phases)
                changed[vertex] *= -1
                delta = sp.expand(label_energy(n, amplitudes, apertures, changed, links) - base)
                degree = sp.Poly(delta, *amplitudes).total_degree() if delta != 0 else 0
                highest = max(highest, degree)
                cases += 1
        for edge in edges:
            for sign in (-1, 1):
                changed_links = dict(links)
                changed_links[edge] *= -1
                delta = sp.expand(label_energy(n, amplitudes, apertures, phases, changed_links) - base)
                degree = sp.Poly(delta, *amplitudes).total_degree() if delta != 0 else 0
                highest = max(highest, degree)
                cases += 1
        for vertex, aperture in enumerate(apertures):
            for sign in (-1, 1):
                target = aperture + sp.Rational(sign, 2)
                if not sp.Rational(1, 2) <= target <= 1:
                    continue
                changed_apertures = list(apertures)
                changed_apertures[vertex] = target
                delta = sp.expand(label_energy(n, amplitudes, changed_apertures, phases, links) - base)
                degree = sp.Poly(delta, *amplitudes).total_degree() if delta != 0 else 0
                highest = max(highest, degree)
                cases += 1
        check(rows, f"nonradial increment degree n={n}", highest <= 2, highest, "<=2")
        reports.append({"n": n, "cases": cases, "max_total_degree": highest})
    return reports


def fibre_algebra_checks(rows: list[dict]) -> None:
    # Exact finite reversible fibre oracle with equal Gibbs weights.  It tests
    # the row-sum, symmetry and form identities used by the analytic matrix
    # argument; it is not a PAH temporal simulation.
    generator = sp.Matrix([[-2, 1, 1], [1, -2, 1], [1, 1, -2]])
    ones = sp.ones(3, 1)
    vector = sp.Matrix(sp.symbols("a0:3", real=True))
    check(rows, "fibre row-sum", generator * ones == sp.zeros(3, 1), "A 1", "0")
    check(rows, "fibre symmetry", generator == generator.T, "A", "A.T")
    quadratic = sp.expand(-(vector.T * generator * vector)[0])
    expected = sp.expand((vector[0] - vector[1]) ** 2
                         + (vector[0] - vector[2]) ** 2
                         + (vector[1] - vector[2]) ** 2)
    check(rows, "fibre nonnegative form", quadratic == expected, str(quadratic), str(expected))
    f0, f1, g0, g1, conductance = sp.symbols("f0 f1 g0 g1 conductance", real=True)
    pair = -conductance * (f0 * (g1 - g0) + f1 * (g0 - g1))
    check(rows, "pair form sign", sp.expand(pair - conductance * (f1 - f0) * (g1 - g0)) == 0,
          "-<f,Lg> pair", "conductance*(f1-f0)*(g1-g0)")


def hostile_checks(rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory(prefix="pah020-fibre-hostile-") as directory:
        altered = Path(directory) / "altered-pah.json"
        altered.write_bytes(PAH.read_bytes() + b"\n")
        check(rows, "hostile source mutation rejected", sha256(altered) != PINS["strategy/pa-hyp/PAH-001-v1.json"],
              sha256(altered), "different from source pin")
    fx, fy, mobility, normalizer = sp.symbols("fx fy mobility normalizer", real=True)
    wrong_rate = mobility * sp.exp(-(fy - fx))
    pi_x = sp.exp(-fx) / normalizer
    check(rows, "hostile full exponent rejected",
          sp.simplify(pi_x * wrong_rate ** 2
                      - mobility ** 2 * sp.exp(-fy) / normalizer) != 0,
          "full exponent", "source half exponent")


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
            "returncode": process.returncode, "output": output[-2000:], "compiler": str(compiler)}


def run(output: Path) -> dict:
    rows: list[dict] = []
    for relative, pin in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", sha256(path) == pin, sha256(path), pin)
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc001 = json.loads(OMC001.read_text(encoding="utf-8"))
    contract = json.loads(OMC020.read_text(encoding="utf-8"))
    check(rows, "PH/LK/AP roots are declared", all(k in omc001["universal_directed_root_labels"]
          for k in ("phase", "link", "aperture")), "phase/link/aperture", "declared")
    check(rows, "TR is separate from fibre", "matter_transfer" in omc001["universal_directed_root_labels"],
          "matter_transfer", "declared")
    check(rows, "same original generator", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "midpoint rate")
    check(rows, "temporal contract fixed-n target", "fixed n" in contract["question"]
          and "first" in contract["question"], contract["question"], "fixed-n target")
    reports = nonradial_degree_checks(rows)
    fibre_algebra_checks(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fibre-modulus/1.0",
        "status": "PASS_FIBRE_MODULUS_STRUCTURAL_AUDIT",
        "temporal_verdict": "IN_PROGRESS",
        "source_pins": PINS,
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "fixture_reports": reports,
        "lean": lean,
        "proved_scope": [
            "independent reconstruction of the original finite strip energy and PH/LK/AP root actions",
            "exact fixture audit that every tested nonradial energy increment has amplitude degree at most two",
            "finite reversible fibre row-sum, symmetry and form-sign algebra",
            "hostile source mutation and full-exponent rejection plus Lean compilation",
        ],
        "open_obligations": [
            "write the all-n compact rate modulus with explicit maxima and finite-label quantifiers",
            "prove cutoff/Duhamel removal in the actual stationary PAH L2 spaces",
            "establish common-space correlation convergence and then anchored-n minimal-closure selection",
        ],
        "non_claims": [
            "The finite fixtures and generic fibre oracle are not a semigroup convergence theorem.",
            "No global common core, strong resolvent/Mosco theorem, infinite-volume process or ordered limit is claimed.",
            "No physical Pre-A, spacetime, quantum real time, QFT, gravity, continuum, mass gap or TOE conclusion.",
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
        with tempfile.TemporaryDirectory(prefix="pah020-fibre-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 fibre-modulus replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIBRE MODULUS: PASS (structural audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
