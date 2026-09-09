#!/usr/bin/env python3
"""Primary finite semigroup-lift audit for PAH-OMC-020.

The source model is unchanged.  This checkpoint proves the finite algebraic
implication ``A I = I B -> exp(t A) I = I exp(t B)`` conditionally and then
audits whether R-493 supplies its stronger all-function/invariant-core
hypothesis.  The matrix values are exact rational regression inputs only;
they do not define a new PAH carrier, rate, state or time evolution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-finite-semigroup-lift-contract-v1.json"
R493 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
R493_LEAN = ROOT / "verification/lean/Tect/R493.lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-finite-semigroup-lift/primary.json"

EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R493-Lean": "c350035719b939c429a9e09d163015d34a471c3e6ea7c4678d4a88049060bc88",
}

Matrix = list[list[Fraction]]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(serial(payload), ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrices")
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def matrix_equal(left: Matrix, right: Matrix) -> bool:
    return left == right


def identity(size: int) -> Matrix:
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def powers(matrix: Matrix, depth: int) -> list[Matrix]:
    result = [identity(len(matrix))]
    for _ in range(depth):
        result.append(matmul(result[-1], matrix))
    return result


def series(matrix: Matrix, intertwiner: Matrix, t: Fraction, depth: int) -> Matrix:
    total = [[Fraction(0) for _ in range(len(intertwiner[0]))] for _ in range(len(intertwiner))]
    power = identity(len(matrix))
    factorial = 1
    for k in range(depth + 1):
        if k:
            power = matmul(power, matrix)
            factorial *= k
        coefficient = (t ** k) / factorial
        term = matmul(power, intertwiner)
        for i in range(len(total)):
            for j in range(len(total[0])):
                total[i][j] += coefficient * term[i][j]
    return total


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contract = load(CONTRACT)
    r493 = load(R493)
    paths = {"PAH-001": PAH001, "PAH-OMC-012": OMC012, "PAH-OMC-013": R493, "R493-Lean": R493_LEAN}
    actual = {key: sha(path) for key, path in paths.items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual_value: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual_value, "expected": expected})

    check("parent hashes", actual == EXPECTED, actual, EXPECTED)
    check(
        "contract identity",
        contract.get("contract_id") == "PAH-OMC-020-FINITE-SEMIGROUP-LIFT"
        and contract.get("result_id") == "R-550"
        and contract.get("task_id") == "T-082",
        {key: contract.get(key) for key in ("contract_id", "result_id", "task_id")},
        {"contract_id": "PAH-OMC-020-FINITE-SEMIGROUP-LIFT", "result_id": "R-550", "task_id": "T-082"},
    )
    check("preservation firewall", all(value is True for value in contract["preservation_firewall"].values()), contract["preservation_firewall"], "all true")
    check("external time firewall", "external stochastic" in contract["exact_scope"]["model"].lower() and "not quantum" in contract["non_claims"][3].lower(), contract["exact_scope"]["model"], "external Markov time only")

    # Exact finite-dimensional regression input.  A is constructed so that the
    # displayed I-range is invariant; this is a theorem oracle, not a PAH
    # replacement model.
    B: Matrix = [[Fraction(1), Fraction(2)], [Fraction(0), Fraction(-1)]]
    I: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)], [Fraction(1), Fraction(1)]]
    A: Matrix = [[Fraction(1), Fraction(2), Fraction(0)], [Fraction(0), Fraction(-1), Fraction(0)], [Fraction(1), Fraction(1), Fraction(0)]]
    generator_identity = matmul(A, I) == matmul(I, B)
    check("finite generator identity oracle", generator_identity, matmul(A, I), matmul(I, B))

    depth = 12
    a_powers = powers(A, depth)
    b_powers = powers(B, depth)
    power_rows = [matmul(a_powers[k], I) == matmul(I, b_powers[k]) for k in range(depth + 1)]
    check("all power coefficients", all(power_rows), {"depth": depth, "rows": power_rows}, "all coefficients equal")

    t = Fraction(1, 3)
    left_series = series(A, I, t, depth)
    right_series = series(B, identity(len(I[0])), t, depth)
    right_series = matmul(I, right_series)
    check("finite exponential-series coefficients", left_series == right_series, left_series, right_series)

    # R-493 source audit: local eventual equality is present, while the
    # stronger invariant/all-iterate fields are absent.
    proof = r493["eventual_intertwining_proof"]
    support = r493["root_support_contract"]
    missing_fields = [key for key in ("invariant_core", "invariant_subspace", "all_iterates", "operator_identity") if key not in r493]
    local_only = "N(f)=max(2,m_f+1)" in support["N_of_f"] and "for every active fine root" in proof["root_correspondence"].lower()
    check("R-493 local eventual input", local_only, {"N_of_f": support["N_of_f"], "root_correspondence": proof["root_correspondence"]}, "support-dependent pointwise identity")
    check("R-493 invariant/all-iterate field absent", len(missing_fields) == 4, missing_fields, "no stronger field declared")
    check("R-493 stage remains open", r493["status"]["stage2_status"] == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP" and r493["status"]["infinite_volume"] == "NOT_PROVED", r493["status"], "semigroup still open")
    check("no physical promotion", contract["status"]["claim_bearing"] is False and contract["status"]["active_gate_change"] is False and contract["status"]["physical_promotion"] is False, contract["status"], "non-bearing/no gate change")

    failed = [row for row in checks if row["status"] != "PASS"]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-finite-semigroup-lift-primary/1.0",
        "audit_id": "PAH-OMC-020-FINITE-SEMIGROUP-LIFT-PRIMARY-001",
        "result_id": "R-550",
        "task_id": "T-082",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional_finite_bridge": "PROVED_CONDITIONALLY",
        "paH_omc013_semigroup": "NOT_PROVED",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual,
        "fixture": {"A": A, "B": B, "I": I, "t": t, "iterate_depth": depth, "power_rows": power_rows},
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "finding": "The finite power/exponential bridge is exact under an all-function operator intertwining or an invariant subspace closed under every coarse generator iterate. R-493 supplies only a support-dependent first-order cylinder identity and does not hash-pin the stronger invariant/all-iterate premise, so its result cannot yet be promoted to finite semigroup intertwining.",
        "missing_assumptions": contract["missing_assumptions"],
        "single_next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    atomic_json(output, payload)
    print(f"PAH-OMC-020 FINITE SEMIGROUP LIFT PRIMARY: {payload['verification']} {payload['checks_passed']}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    run(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
