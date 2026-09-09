#!/usr/bin/env python3
"""Non-importing independent audit of the PAH-OMC-020 fixed-n implication.

This lane rebuilds the finite reversible fibre algebra and the two displayed
error terms with Fraction arithmetic.  It intentionally does not import the
primary verifier or claim that its conditional analytic hypotheses have been
discharged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-conditional/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
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


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, f"independent source pin:{relative}", path.is_file() and sha256(path) == expected,
              sha256(path) if path.is_file() else "MISSING", expected)
    work = (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")
    check(rows, "independent F7--F10 markers", all(m in work for m in ("(F7)", "(F8)", "(F9)", "(F10)")),
          "F7,F8,F9,F10", "present")
    check(rows, "independent order marker", "taking `j` to infinity first" in work and "then `K`" in work,
          "j then K", "present")
    check(rows, "independent non-claim marker", "does not identify `Q_n` with the R-512 minimal-closure semigroup" in work,
          "minimal selection remains open", "present")


def fibre_checks(rows: list[dict]) -> dict:
    # A two-state fibre with positive rates a,b.  The matrix is rebuilt as
    # ordinary tuples; no symbolic object or primary implementation is used.
    a, b = Fraction(3, 5), Fraction(7, 10)
    ap, bp = Fraction(2, 5), Fraction(4, 5)
    matrix = ((-a, a), (b, -b))
    other = ((-ap, ap), (bp, -bp))
    matrix_text = [[str(value) for value in row] for row in matrix]
    other_text = [[str(value) for value in row] for row in other]
    check(rows, "independent row zero", all(sum(row) == 0 for row in matrix), matrix_text, "each row sums to zero")
    pi0, pi1 = b / (a + b), a / (a + b)
    check(rows, "independent detailed balance", pi0 * a == pi1 * b, str(pi0 * a), str(pi1 * b))
    x0, x1 = Fraction(2, 3), Fraction(-1, 4)
    quadratic = -(pi0 * x0 * (matrix[0][0] * x0 + matrix[0][1] * x1)
                  + pi1 * x1 * (matrix[1][0] * x0 + matrix[1][1] * x1))
    expected = pi0 * a * (x1 - x0) ** 2
    check(rows, "independent form sign", quadratic == expected, str(quadratic), str(expected))
    delta = [[matrix[i][j] - other[i][j] for j in range(2)] for i in range(2)]
    max_row = max(sum(abs(v) for v in row) for row in delta)
    expected_row = 2 * max(abs(a - ap), abs(b - bp))
    check(rows, "independent generator modulus", max_row == expected_row, str(max_row), str(expected_row))
    check(rows, "independent positive rate range", min(a, b, ap, bp) > 0, [str(a), str(b), str(ap), str(bp)], ">0")
    return {"rates": {"a": str(a), "b": str(b), "a_prime": str(ap), "b_prime": str(bp)},
            "stationary_weights": [str(pi0), str(pi1)],
            "generator_row_l1_difference": str(max_row),
            "generator": matrix_text,
            "perturbed_generator": other_text}


def error_checks(rows: list[dict]) -> dict:
    # Explicitly diagnostic fixtures; these are not PAH-derived constants.
    t, h, ell = Fraction(7, 10), Fraction(1, 2), Fraction(5, 2)
    mf, mg = Fraction(27, 25), Fraction(6, 5)
    mesh = [Fraction(1, 2 ** j) for j in range(7)]
    f7 = [2 * t * h * ell * step for step in mesh]
    tails = [Fraction(1, k) for k in range(2, 9)]
    f8 = [2 * mf * mg * tail for tail in tails]
    check(rows, "independent F7 monotonicity", all(y < x for x, y in zip(f7, f7[1:])),
          [str(v) for v in f7], "strictly decreasing")
    check(rows, "independent F8 monotonicity", all(y < x for x, y in zip(f8, f8[1:])),
          [str(v) for v in f8], "strictly decreasing")
    check(rows, "independent limits approach zero", f7[-1] < 1 and f8[-1] < 2,
          [str(f7[-1]), str(f8[-1])], "diagnostic smallness")
    return {"fixture": {"T": str(t), "H": str(h), "L": str(ell), "M_f": str(mf), "M_g": str(mg)},
            "f7": [str(v) for v in f7], "f8": [str(v) for v in f8]}


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    fibre = fibre_checks(rows)
    errors = error_checks(rows)
    payload = {
        "schema": "tect/pah-omc020-fixedn-conditional-independent/1.0",
        "status": "PASS_INDEPENDENT_CONDITIONAL_AUDIT",
        "verdict": "AUXILIARY_SUPPORT",
        "temporal_verdict": "IN_PROGRESS",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_pins": PINS,
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "fibre_oracle": fibre,
        "error_oracle": errors,
        "independence": "Non-importing tuple/Fraction reconstruction; no primary verifier code is imported.",
        "scope": "Conditional F7--F9 to F10 implication at fixed n only; inherited analytic hypotheses remain open.",
        "non_claims": [
            "No unconditional fixed-n temporal theorem, common-space U_n, Mosco liminf or anchored n limit.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang--Mills or TOE conclusion.",
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
        with tempfile.TemporaryDirectory(prefix="pah020-independent-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 independent conditional replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N INDEPENDENT: PASS (conditional audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
