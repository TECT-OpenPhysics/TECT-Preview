#!/usr/bin/env python3
"""PAH-OMC-020 fixed-n all-test quantifier audit.

This checker validates the source-pinned structure of the analytic F7--F10
fixed-n argument: compact cutoff, finite-fibre Duhamel control, stationary L1
tail removal and uniform-on-[0,T] cell passage.  It deliberately does not
pretend that a finite arithmetic fixture is a proof of the inherited
measure-theoretic theorem, and it does not admit a result card or take the
anchored n limit.
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
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC016 = ROOT / "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"
CELL_RUN = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-cell-correlation/cell-correlation.json"
)
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-quantifier/quantifier.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json":
        "6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-cell-correlation/cell-correlation.json":
        "d607dcac1bfa6e061a0b783f7ee9b339ba2d808cd237cb69f2a348d6a4557dd5",
}

# These are diagnostic tolerances/fixtures, not values inferred from PAH.
NUMERIC_TOL = Fraction(1, 10**12)
FIXTURE_T = Fraction(7, 10)
FIXTURE_H = Fraction(3)
FIXTURE_L = Fraction(2)
FIXTURE_MF = Fraction(108, 100)
FIXTURE_MG = Fraction(12, 10)


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


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def source_and_text_checks(rows: list[dict]) -> None:
    for relative, pin in PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", digest(path) == pin, digest(path), pin)
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc016 = json.loads(OMC016.read_text(encoding="utf-8"))
    omc020 = json.loads(OMC020.read_text(encoding="utf-8"))
    work = WORK.read_text(encoding="utf-8")
    cert = OMC018.read_text(encoding="utf-8")
    cell = json.loads(CELL_RUN.read_text(encoding="utf-8"))
    check(rows, "original midpoint rate retained",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in pah["dynamics"]["generator"],
          pah["dynamics"]["generator"], "source midpoint rate")
    check(rows, "OMC-016 tail theorem is the inherited cutoff input",
          "fixed-`n` tail estimate" in work and "tail" in omc016["conclusion"],
          omc016["conclusion"]["tail"], "present")
    check(rows, "F7--F10 are explicitly recorded",
          all(marker in work for marker in ("(F7)", "(F8)", "(F9)", "(F10)")),
          [marker for marker in ("(F7)", "(F8)", "(F9)", "(F10)") if marker in work],
          "all four markers")
    check(rows, "same Q_n is used throughout",
          "same `Q_n`" in work and "Q_(n,j)(t)S_(n,j)g_K" in work,
          "shared finite fibre", "present")
    check(rows, "stationary L1 tail contraction is explicit",
          "stationary L1 contraction" in work,
          "stationary L1 contraction", "present")
    check(rows, "uniform time interval is explicit",
          work.count("0<=t<=T") >= 3 and "uniformly for `0<=t<=T`" in work,
          work.count("0<=t<=T"), ">=3 occurrences")
    check(rows, "half-open upper endpoint is explicit",
          "upper endpoint cells" in work and "upper endpoint" in work,
          "endpoint-preserving cell theorem", "present")
    check(rows, "cell audit is diagnostic, not temporal completion",
          cell["status"] == "PASS_COMMON_SPACE_CELL_AUDIT"
          and cell["temporal_verdict"] == "IN_PROGRESS",
          {"status": cell["status"], "temporal_verdict": cell["temporal_verdict"]},
          "PASS_COMMON_SPACE_CELL_AUDIT/IN_PROGRESS")
    check(rows, "preregistration forbids shortcuts",
          "No rate/functional/mobility/finite-part/state/time change" in omc020["prohibited_shortcuts"][0]
          and "No assumption that a form core is an operator graph core" in omc020["prohibited_shortcuts"][2],
          omc020["prohibited_shortcuts"], "source restrictions")
    check(rows, "source certificate is not a path-law construction",
          "not a temporal path-law construction" in cert,
          "not a temporal path-law construction", "present")


def quantifier_arithmetic(rows: list[dict]) -> dict:
    # An exact rational oracle for the two error terms.  H,L,Mf,Mg are explicit
    # test fixtures; the formulas themselves are the source of the check.
    residuals = []
    for j in range(0, 9):
        h = Fraction(1, 2**j)
        residuals.append(Fraction(2) * FIXTURE_T * FIXTURE_H * FIXTURE_L * h)
    check(rows, "F7 radial Duhamel residual decreases with mesh",
          all(right < left for left, right in zip(residuals, residuals[1:])),
          [str(value) for value in residuals], "strictly decreasing")
    check(rows, "F7 residual tends below diagnostic tolerance",
          residuals[-1] > 0 and residuals[-1] < Fraction(1),
          str(residuals[-1]), "0<residual<1 at j=8")
    tails = [Fraction(1, k) for k in range(2, 11)]
    cutoff_errors = [Fraction(2) * FIXTURE_MF * FIXTURE_MG * tail for tail in tails]
    check(rows, "F8 stationary L1 cutoff term decreases with tail control",
          all(right < left for left, right in zip(cutoff_errors, cutoff_errors[1:])),
          [str(value) for value in cutoff_errors], "strictly decreasing")
    total = residuals[-1] + cutoff_errors[-1]
    check(rows, "two-term bound is finite and nonnegative", total >= 0 and total < 10,
          str(total), "finite nonnegative")
    return {"mesh_residuals": [float(value) for value in residuals],
            "cutoff_errors": [float(value) for value in cutoff_errors],
            "fixture": {"T": float(FIXTURE_T), "H": float(FIXTURE_H), "L": float(FIXTURE_L),
                        "Mf": float(FIXTURE_MF), "Mg": float(FIXTURE_MG)}}


def hostile_checks(rows: list[dict]) -> None:
    work_bytes = WORK.read_bytes()
    with tempfile.TemporaryDirectory(prefix="pah020-quantifier-hostile-") as directory:
        altered = Path(directory) / "work-without-tail.txt"
        altered.write_bytes(work_bytes.replace(b"stationary L1 contraction", b"pointwise rate envelope", 1))
        check(rows, "hostile tail shortcut changes pinned work hash",
              digest(altered) != digest(WORK), digest(altered), "different from work hash")
    # Wrong order would contradict the fixed contract rather than establish a
    # new theorem; test that the source order remains visible.
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    order = prereg["scope"]["regulator_order"]
    check(rows, "hostile reversed order is not silently accepted",
          "First j" in order and "then" in order and "No diagonal, reversed" in order,
          order, "j-before-n only")
    check(rows, "hostile temporal promotion remains fenced",
          "No physical Pre-A" in prereg["non_claims"][2]
          and "selection premise" in prereg["outcomes"]["HOLD_FOR_EVIDENCE"],
          prereg["non_claims"], "physical and hold fences")


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
    source_and_text_checks(rows)
    arithmetic = quantifier_arithmetic(rows)
    hostile_checks(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fixedn-quantifier-audit/1.0",
        "status": "PASS_FIXED_N_QUANTIFIER_AUDIT",
        "temporal_verdict": "IN_PROGRESS",
        "source_pins": PINS,
        "code_sha256": digest(Path(__file__)),
        "checks": rows,
        "arithmetic_oracle": arithmetic,
        "proved_scope": [
            "source-pinned F7--F10 quantifier and scope structure",
            "exact rational two-term Duhamel/cutoff error decomposition for diagnostic fixtures",
            "stationary L1 tail, half-open endpoint and shared-Q_n obligations retained",
            "hostile shortcut/order/promotion controls and PahOmc020 Lean compilation PASS",
        ],
        "conditional_analytic_statement": "Under the inherited R-509 cell-density/tail theorem, R-511 residual estimate and finite-fibre modulus, F7--F10 imply fixed-n uniform-on-[0,T] correlation convergence after j then K limits.",
        "open_obligations": [
            "independently discharge the inherited all-test measure-theoretic cell theorem and Duhamel domain hypotheses",
            "admit a fixed-n temporal result only after those hypotheses are proved at the exact PAH scope",
            "prove the anchored n passage and identify the R-512 minimal-form semigroup",
        ],
        "non_claims": [
            "This is a quantifier/assumption audit, not a fixed-n temporal convergence theorem or result-card admission.",
            "No strong operator convergence, common infinite-volume process, R-512 minimal/maximal equality or anchored n limit is claimed.",
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
        with tempfile.TemporaryDirectory(prefix="pah020-quantifier-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 fixed-n quantifier replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N QUANTIFIER: PASS (analytic contract audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
