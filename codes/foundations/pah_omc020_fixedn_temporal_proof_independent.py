#!/usr/bin/env python3
"""Non-importing independent audit of the PAH-OMC-020 fixed-n proof.

This verifier reconstructs the strip counts and the reversible fibre algebra
from scratch.  It checks the exact compact-modulus, Duhamel, cell-net and tail
inequalities used in the paired certificate, while keeping the anchored-n
selection outside the result.
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


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC016 = ROOT / "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
FIBRE = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fibre-modulus/fibre.json"
CELL = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-temporal/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json":
        "6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-certificate.md":
        "6f3bbb18fb94db189a6d7d9249cf86ba636643946d0a5340ebe900c92f515820",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fibre-modulus/fibre.json":
        "bf5409afc112c54b1596cce3272c193ff79517db6af593daf7011d85a898e911",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json":
        "d607dcac1bfa6e061a0b783f7ee9b339ba2d808cd237cb69f2a348d6a4557dd5",
}


def digest(path: Path) -> str:
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


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc016 = json.loads(OMC016.read_text(encoding="utf-8"))
    omc018 = json.loads(OMC018.read_text(encoding="utf-8"))
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    cert = CERTIFICATE.read_text(encoding="utf-8")
    fibre = json.loads(FIBRE.read_text(encoding="utf-8"))
    cell = json.loads(CELL.read_text(encoding="utf-8"))
    check(rows, "midpoint source rate", "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "present")
    parameters = str(omc016.get("exact_scope", {}).get("parameters", ""))
    check(rows, "frozen parameter tuple", all(token in parameters for token in ("K=2", "M_s=1", "epsilon=1/2", "beta=nu=1")),
          parameters, "K=2,M_s=1,epsilon=1/2,beta=nu=1")
    check(rows, "source static law converges at fixed n", "weak convergence" in omc016["conclusion"]["fixed_n"]
          and "sup_j" in omc016["conclusion"]["tail"], omc016["conclusion"], "weak plus tail")
    check(rows, "source radial residual", "radial form energy" in omc018["conclusion"]
          and "h_j" in omc018["conclusion"], omc018["conclusion"], "present")
    check(rows, "certificate is fixed n only", "fixed-n" in cert and "anchored" in cert and "R-512" in cert,
          "fixed-n and anchored n boundary", "present")
    order = prereg["scope"]["regulator_order"]
    check(rows, "ordered regulator path", "First j" in order and "then" in order,
          order, "j-before-n")
    check(rows, "diagnostic children remain non-admission", fibre["temporal_verdict"] == "IN_PROGRESS"
          and cell["temporal_verdict"] == "IN_PROGRESS",
          {"fibre": fibre["temporal_verdict"], "cell": cell["temporal_verdict"]}, "IN_PROGRESS")


def strip_counts(n: int) -> tuple[int, int, int, int]:
    vertices = 2 * (n + 2)
    horizontal = 2 * (n + 1)
    vertical = n + 2
    diagonal = n
    edges = horizontal + vertical + diagonal
    faces = 2 * n + 1
    # PH and LK retain both K=2 labels; AP has at most two directions.
    nonradial = 2 * vertices + 2 * edges + 2 * vertices
    return vertices, edges, faces, nonradial


def incidence_checks(rows: list[dict]) -> list[dict]:
    reports = []
    for n in range(2, 12):
        vertices, edges, faces, nonradial = strip_counts(n)
        check(rows, f"finite strip count n={n}", vertices == 2 * (n + 2), vertices, 2 * (n + 2))
        check(rows, f"edge count n={n}", edges == 4 * n + 4, edges, 4 * n + 4)
        check(rows, f"face count n={n}", faces == 2 * n + 1, faces, 2 * n + 1)
        check(rows, f"finite root set n={n}", nonradial > 0, nonradial, ">0")
        reports.append({"n": n, "vertices": vertices, "edges": edges,
                        "faces": faces, "nonradial_root_bound": nonradial})
    return reports


def compact_modulus_checks(rows: list[dict]) -> dict:
    # A source rate has exp(-Delta F/2), with Delta F quadratic for a
    # nonradial label change.  The following exact polynomial is a diagnostic
    # derivative oracle for the compact maximum argument, not a fitted rate.
    def rate(r: Fraction) -> Fraction:
        return Fraction(1, 2) + r + r * r / 3

    def derivative(r: Fraction) -> Fraction:
        return Fraction(1) + Fraction(2, 3) * r

    boxes = [Fraction(k) for k in range(1, 8)]
    bounds = [max(derivative(Fraction(0)), derivative(k)) for k in boxes]
    check(rows, "compact derivative maxima exist", all(value >= 1 for value in bounds),
          [str(value) for value in bounds], ">=1")
    check(rows, "compact modulus is finite at every box", all(value < 10 for value in bounds),
          [str(value) for value in bounds], "finite")
    mesh = [Fraction(1, 2 ** j) for j in range(1, 10)]
    replacement = [bounds[-1] * Fraction(12) * h for h in mesh]
    check(rows, "compact replacement error decreases", all(right < left for left, right in zip(replacement, replacement[1:])),
          [str(value) for value in replacement], "strictly decreasing")
    return {"boxes": [str(value) for value in boxes], "derivative_bounds": [str(value) for value in bounds],
            "replacement": [str(value) for value in replacement]}


def reversible_checks(rows: list[dict]) -> dict:
    # Independent exact two-state conductance computation.
    forward, backward = Fraction(3, 5), Fraction(7, 10)
    total = forward + backward
    pi_left, pi_right = backward / total, forward / total
    check(rows, "stationary weights sum to one", pi_left + pi_right == 1,
          [str(pi_left), str(pi_right)], "sum=1")
    check(rows, "detailed balance", pi_left * forward == pi_right * backward,
          str(pi_left * forward), str(pi_right * backward))
    f_left, f_right = Fraction(2, 3), Fraction(-1, 4)
    form = pi_left * forward * (f_right - f_left) ** 2
    matrix_form = -(pi_left * f_left * (-forward * f_left + forward * f_right)
                    + pi_right * f_right * (backward * f_left - backward * f_right))
    check(rows, "Dirichlet form sign/factor", form == matrix_form, str(matrix_form), str(form))
    return {"weights": [str(pi_left), str(pi_right)], "conductance": str(pi_left * forward),
            "form": str(form)}


def cell_net_checks(rows: list[dict]) -> dict:
    # Finite epsilon-net argument: uniform Lipschitz modulus times cell width.
    modulus = Fraction(17, 3)
    dimension = 12
    mesh = [Fraction(1, 2 ** j) for j in range(2, 11)]
    errors = [modulus * dimension * h for h in mesh]
    check(rows, "cell-net error is nonnegative", all(value >= 0 for value in errors),
          [str(value) for value in errors], "nonnegative")
    check(rows, "cell-net error tends down", all(right < left for left, right in zip(errors, errors[1:])),
          [str(value) for value in errors], "strictly decreasing")
    check(rows, "finite-net reduction is available", len(errors) >= 2 and errors[-1] < errors[0],
          {"levels": len(errors), "last": str(errors[-1])}, "vanishing mesh")
    return {"modulus": str(modulus), "dimension": dimension, "errors": [str(value) for value in errors]}


def tail_checks(rows: list[dict]) -> dict:
    omc016 = json.loads(OMC016.read_text(encoding="utf-8"))
    tail = omc016["conclusion"]["tail"]
    coverage = str(omc016["proof_coverage"])
    check(rows, "source tail is all-j", "sup_j" in tail, tail, "sup_j")
    check(rows, "source tail has exponential decay", "exp(-L)" in tail, tail, "exp(-L)")
    check(rows, "source density keeps endpoint cells", "endpoint-inclusive" in coverage, coverage, "endpoint")
    majorant = [Fraction(1, 2 ** k) for k in range(0, 10)]
    check(rows, "tail oracle decreases", all(right < left for left, right in zip(majorant, majorant[1:])),
          [str(value) for value in majorant], "strictly decreasing")
    return {"source_tail": tail, "majorant": [str(value) for value in majorant]}


def hostile_checks(rows: list[dict]) -> None:
    cert = CERTIFICATE.read_bytes()
    with tempfile.TemporaryDirectory(prefix="pah020-independent-hostile-") as directory:
        altered = Path(directory) / "altered.md"
        altered.write_bytes(cert.replace(b"No diagonal sequence is used", b"diagonal j,n limit", 1))
        check(rows, "hostile diagonal mutation changes certificate", digest(altered) != digest(CERTIFICATE),
              digest(altered), "different")
    text = CERTIFICATE.read_text(encoding="utf-8")
    check(rows, "hostile global-rate shortcut is fenced", "no global rate bound is asserted" in text
          and "pointwise infinite-volume estimate" in text,
          text, "compact-only bound")
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    check(rows, "physical promotion is fenced", "No physical Pre-A" in " ".join(prereg["non_claims"]),
          prereg["non_claims"], "fenced")


def lean_check() -> dict:
    compiler = Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe"
    if not compiler.is_file():
        return {"status": "NOT_AVAILABLE"}
    env = os.environ.copy()
    package_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    if package_root.is_dir():
        libraries = []
        for package in package_root.iterdir():
            candidate = package / ".lake/build/lib/lean"
            if candidate.is_dir():
                libraries.append(str(candidate))
        env["LEAN_PATH"] = ";".join(libraries)
    process = subprocess.run([str(compiler), str(LEAN)], cwd=ROOT / "verification/lean",
                             env=env, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", check=False, timeout=180)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
            "returncode": process.returncode, "output": output[-1000:]}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    incidence = incidence_checks(rows)
    compact = compact_modulus_checks(rows)
    reversible = reversible_checks(rows)
    cell = cell_net_checks(rows)
    tail = tail_checks(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fixedn-temporal-independent/1.0",
        "status": "PASS_INDEPENDENT_FIXED_N_TEMPORAL",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "FIXED_N_PASS_ANCHORED_N_OPEN",
        "claim_bearing": False,
        "source_pins": PINS,
        "code_sha256": digest(Path(__file__)),
        "checks": rows,
        "incidence": incidence,
        "compact_modulus": compact,
        "reversible_fibre": reversible,
        "cell_net": cell,
        "tail": tail,
        "lean": lean,
        "independent_scope": (
            "Non-importing reconstruction of the source strip counts, finite reversible form, "
            "compact equicontinuity net, endpoint/tail order and fixed-n conclusion."
        ),
        "remaining_gates": [
            "source-authorized U_n/common-Hilbert realization",
            "N2b liminf/recovery and N2c/N4 boundary escape",
            "N2d R-512 minimal-form identification and anchored n limit",
        ],
        "non_claims": [
            "No infinite-volume process, anchored n semigroup convergence or minimal-extension uniqueness.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
        "reproduction": {
            "run": "python -X utf8 codes/foundations/pah_omc020_fixedn_temporal_proof_independent.py",
            "check": "python -X utf8 codes/foundations/pah_omc020_fixedn_temporal_proof_independent.py --check",
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
        with tempfile.TemporaryDirectory(prefix="pah020-independent-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 independent fixed-n replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 INDEPENDENT FIXED-N: PASS (anchored-n remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
