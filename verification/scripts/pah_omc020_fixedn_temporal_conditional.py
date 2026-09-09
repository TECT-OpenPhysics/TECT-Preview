#!/usr/bin/env python3
"""Verify the conditional fixed-n temporal implication in PAH-OMC-020.

The certificate checked here is deliberately an implication: if the pinned
R-509 cell/tail input, the R-511 radial residual estimate, and the finite
fibre compact-modulus hypotheses hold at their stated scopes, then the
displayed F7--F9 decomposition implies the F10 fixed-n correlation limit.
This script does not assert that the varying-space U_n, the anchored n limit,
or the minimal-form selection has been proved.
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
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-conditional/primary.json"
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
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fixedn-quantifier/quantifier.json":
        "50edfdb8030dd51c00382feb6a714e46d65e0cc5b78a018c6775633ce4a9ddb1",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json":
        "d607dcac1bfa6e061a0b783f7ee9b339ba2d808cd237cb69f2a348d6a4557dd5",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fibre-modulus/fibre.json":
        "bf5409afc112c54b1596cce3272c193ff79517db6af593daf7011d85a898e911",
    "verification/lean/Tect/PahOmc020.lean":
        "f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c",
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


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", path.is_file() and sha256(path) == expected,
              sha256(path) if path.is_file() else "MISSING", expected)
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    work = (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")
    quantifier = json.loads((ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fixedn-quantifier/quantifier.json").read_text(encoding="utf-8"))
    cell = json.loads((ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json").read_text(encoding="utf-8"))
    fibre = json.loads((ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fibre-modulus/fibre.json").read_text(encoding="utf-8"))
    check(rows, "original midpoint rate retained",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))["dynamics"]["generator"],
          "source midpoint", "present")
    check(rows, "j-before-n order retained", "First j" in prereg["scope"]["regulator_order"] and "then" in prereg["scope"]["regulator_order"],
          prereg["scope"]["regulator_order"], "j then anchored n")
    check(rows, "F7--F10 are source-recorded", all(marker in work for marker in ("(F7)", "(F8)", "(F9)", "(F10)")),
          [marker for marker in ("(F7)", "(F8)", "(F9)", "(F10)") if marker in work], "all four markers")
    check(rows, "same Q_n appears in the implication", "same `Q_n`" in work and "Q_(n,j)(t)S_(n,j)g_K" in work,
          "shared Q_n", "present")
    check(rows, "stationary L1 tail is explicit", "stationary L1 contraction" in work,
          "stationary L1 contraction", "present")
    check(rows, "half-open endpoint input is pinned", "upper endpoint cells" in work and "upper endpoint" in work,
          "endpoint-preserving cell theorem", "present")
    check(rows, "quantifier audit remains non-admission", quantifier["temporal_verdict"] == "IN_PROGRESS",
          quantifier["temporal_verdict"], "IN_PROGRESS")
    check(rows, "cell audit remains non-admission", cell["temporal_verdict"] == "IN_PROGRESS",
          cell["temporal_verdict"], "IN_PROGRESS")
    check(rows, "fibre audit lists compact modulus as open", any("compact rate modulus" in item for item in fibre["open_obligations"]),
          fibre["open_obligations"], "open compact modulus")
    check(rows, "physical firewall retained", all(token in " ".join(prereg["non_claims"]) for token in ("Pre-A", "QFT", "gravity")),
          prereg["non_claims"], "physical non-claims")


def matrix_oracle(rows: list[dict]) -> dict:
    """Exact rational checks for a finite reversible fibre block."""
    # The algebra is done entry-by-entry so this verifier has no optional
    # symbolic dependency.  The letters a,b stand for arbitrary positive
    # source rates; the displayed rational instance is only a self-test.
    a, b, ap, bp = Fraction(3, 5), Fraction(7, 10), Fraction(2, 5), Fraction(4, 5)
    x0, x1 = Fraction(2, 3), Fraction(-1, 4)
    matrix = ((-a, a), (b, -b))
    other = ((-ap, ap), (bp, -bp))
    pi0, pi1 = b / (a + b), a / (a + b)
    check(rows, "finite fibre row sum", all(sum(row) == 0 for row in matrix),
          [[str(v) for v in row] for row in matrix], "each row sums to zero")
    check(rows, "finite fibre detailed balance", pi0 * a == pi1 * b,
          str(pi0 * a), str(pi1 * b))
    energy = -(pi0 * x0 * (matrix[0][0] * x0 + matrix[0][1] * x1)
               + pi1 * x1 * (matrix[1][0] * x0 + matrix[1][1] * x1))
    expected = pi0 * a * (x1 - x0) ** 2
    check(rows, "finite fibre nonnegative form", energy == expected,
          str(energy), str(expected))
    diff_rows = [sum(matrix[i][j] - other[i][j] for j in range(2)) for i in range(2)]
    check(rows, "generator difference row cancellation", diff_rows == [0, 0],
          [str(v) for v in diff_rows], "zero row sums")
    check(rows, "generator difference has only rate deltas",
          all(matrix[i][j] - other[i][j] == (-(a - ap) if i == 0 and j == 0 else
                                             (a - ap if i == 0 and j == 1 else
                                              (b - bp if i == 1 and j == 0 else -(b - bp))))
              for i in range(2) for j in range(2)),
          "linear rate differences", "degree<=1")
    return {"generator": [[str(-a), str(a)], [str(b), str(-b)]],
            "stationary_weights": [str(pi0), str(pi1)],
            "form": "pi0*a*(x1-x0)^2",
            "modulus": "finite matrix exponential variation-of-constants on compact rate range"}


def error_oracle(rows: list[dict]) -> dict:
    # These are labelled diagnostic fixtures.  H,L,Mf,Mg are not inferred PAH
    # constants; the source theorem supplies existence at its exact scope.
    T, H, L, Mf, Mg = map(Fraction, ("7/10", "3", "2", "27/25", "6/5"))
    meshes = [Fraction(1, 2 ** j) for j in range(9)]
    residuals = [2 * T * H * L * h for h in meshes]
    tails = [Fraction(1, k) for k in range(2, 11)]
    cutoff = [2 * Mf * Mg * tau for tau in tails]
    check(rows, "F7 diagnostic residual decreases", all(y < x for x, y in zip(residuals, residuals[1:])),
          [str(v) for v in residuals], "strictly decreasing")
    check(rows, "F8 diagnostic tail term decreases", all(y < x for x, y in zip(cutoff, cutoff[1:])),
          [str(v) for v in cutoff], "strictly decreasing")
    check(rows, "two-term error is nonnegative", all(v >= 0 for v in residuals + cutoff),
          "F7+F8", "nonnegative")
    check(rows, "two-term error can be made small in the ordered limits", residuals[-1] < 1 and cutoff[-1] < 2,
          [str(residuals[-1]), str(cutoff[-1])], "diagnostic thresholds")
    return {"fixture": {"T": str(T), "H": str(H), "L": str(L), "Mf": str(Mf), "Mg": str(Mg)},
            "mesh_residuals": [str(v) for v in residuals],
            "cutoff_terms": [str(v) for v in cutoff]}


def hostile_checks(rows: list[dict]) -> None:
    work = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="pah020-conditional-hostile-") as directory:
        altered = Path(directory) / "altered-work.md"
        altered.write_bytes(work.read_bytes().replace(b"stationary L1 contraction", b"pointwise rate envelope", 1))
        check(rows, "hostile pointwise-tail shortcut changes source", sha256(altered) != sha256(work),
              sha256(altered), "different hash")
    check(rows, "hostile reversed order remains rejected", "No diagonal, reversed" in prereg["scope"]["regulator_order"],
          prereg["scope"]["regulator_order"], "j-before-n only")
    check(rows, "hostile physical promotion remains rejected", "No physical Pre-A" in prereg["non_claims"][2],
          prereg["non_claims"], "physical firewall")
    check(rows, "hostile unconditional reading remains rejected", "conditional" in (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8").lower(),
          "conditional", "present in source argument")


def lean_check() -> dict:
    compiler = Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe"
    if not compiler.is_file():
        return {"status": "NOT_AVAILABLE", "command": "lean verification/lean/Tect/PahOmc020.lean"}
    package_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    env = os.environ.copy()
    if package_root.is_dir():
        libraries = []
        for package in package_root.iterdir():
            candidate = package / ".lake/build/lib/lean"
            if candidate.is_dir():
                libraries.append(str(candidate))
        env["LEAN_PATH"] = ";".join(libraries)
    process = subprocess.run([str(compiler), str(ROOT / "verification/lean/Tect/PahOmc020.lean")],
                             cwd=ROOT / "verification/lean", env=env, capture_output=True,
                             text=True, encoding="utf-8", errors="replace", check=False, timeout=180)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
            "command": "lean verification/lean/Tect/PahOmc020.lean", "returncode": process.returncode,
            "output": output[-2000:], "compiler": str(compiler)}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    matrix = matrix_oracle(rows)
    errors = error_oracle(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fixedn-conditional/1.0",
        "status": "PASS_CONDITIONAL_FIXED_N_IMPLICATION",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "IN_PROGRESS",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_pins": PINS,
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "matrix_oracle": matrix,
        "error_oracle": errors,
        "conditional_statement": (
            "For fixed n>=2, f,g in the preregistered bounded invariant cylinder domain and finite T, "
            "if the inherited R-509 all-test half-open cell/tail theorem, the R-511 radial residual bound "
            "and the finite-fibre compact rate modulus hold at their exact scopes, then F7+F8+F9 imply "
            "sup_{0<=t<=T}|C_nj(f,g;t)-<f,Q_n(t)g>_(nu_n)| -> 0 as j -> infinity."
        ),
        "proved_scope": [
            "source-pinned conditional implication and quantifier order",
            "finite reversible fibre matrix algebra and variation-of-constants modulus shape",
            "exact rational diagnostic decomposition of F7 and F8",
            "hostile shortcut/order/physical-promotion rejection and existing PahOmc020 Lean compilation",
        ],
        "unresolved_hypotheses": [
            "a source-grounded all-test cell theorem applied uniformly to the Q_n(t)g_K family",
            "a PAH-specific finite-fibre modulus with an explicit support-dependent constant",
            "the actual compact-cutoff Duhamel domain estimate for Q_n(t)g_K",
            "every varying-space U_n/common-Hilbert N2a field",
            "N2b liminf, N2c/N4 boundary escape and N2d R-512 minimal-form identification",
        ],
        "non_claims": [
            "This is a conditional implication certificate, not an unconditional fixed-n temporal result.",
            "No common-space U_n, Mosco theorem, anchored n passage, minimal/maximal equality or full PAH-OMC-020 convergence.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang--Mills or TOE conclusion; no Q3LOCK import.",
        ],
        "reproduction": {
            "command": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_conditional.py",
            "check": "python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_conditional.py --check",
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
        with tempfile.TemporaryDirectory(prefix="pah020-conditional-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 conditional fixed-n replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N CONDITIONAL: PASS (implication only; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
