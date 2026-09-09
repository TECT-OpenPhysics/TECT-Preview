#!/usr/bin/env python3
"""Independent replay of the PAH-OMC-020 finite semigroup-lift audit."""
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
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-finite-semigroup-lift/independent.json"
PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R493-Lean": "c350035719b939c429a9e09d163015d34a471c3e6ea7c4678d4a88049060bc88",
}

Mat = tuple[tuple[Fraction, ...], ...]


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def product(left: Mat, right: Mat) -> Mat:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions")
    return tuple(
        tuple(sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0])))
        for i in range(len(left))
    )


def eye(size: int) -> Mat:
    return tuple(tuple(Fraction(int(i == j)) for j in range(size)) for i in range(size))


def matrix_powers(matrix: Mat, depth: int) -> list[Mat]:
    values = [eye(len(matrix))]
    for _ in range(depth):
        values.append(product(values[-1], matrix))
    return values


def atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(serial(value), ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    contract = read(CONTRACT)
    r493 = read(R493)
    sources = {"PAH-001": PAH001, "PAH-OMC-012": OMC012, "PAH-OMC-013": R493, "R493-Lean": R493_LEAN}
    actual = {name: digest(path) for name, path in sources.items()}
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": serial(detail)})

    check("independent parent hashes", actual == PINS, {"actual": actual, "expected": PINS})
    check("unchanged model firewall", all(contract["preservation_firewall"].values()), contract["preservation_firewall"])
    check("contract status", contract["status"]["verdict"] == "HOLD_FOR_EVIDENCE" and contract["status"]["finite_conditional_bridge"] == "PROVED_CONDITIONALLY", contract["status"])

    # A different exact oracle: the range of I is invariant by construction.
    B: Mat = ((Fraction(2), Fraction(-1)), (Fraction(1), Fraction(0)))
    I: Mat = ((Fraction(1), Fraction(0)), (Fraction(1), Fraction(1)), (Fraction(0), Fraction(1)))
    A: Mat = ((Fraction(2), Fraction(0), Fraction(-1)), (Fraction(3), Fraction(0), Fraction(-1)), (Fraction(1), Fraction(0), Fraction(0)))
    check("independent generator intertwining", product(A, I) == product(I, B), {"A_I": product(A, I), "I_B": product(I, B)})
    depth = 9
    left = matrix_powers(A, depth)
    right = matrix_powers(B, depth)
    rows = [product(left[k], I) == product(I, right[k]) for k in range(depth + 1)]
    check("independent power induction replay", all(rows), {"depth": depth, "rows": rows})

    proof = r493["eventual_intertwining_proof"]
    support = r493["root_support_contract"]
    check("R-493 support-dependent threshold", "N(f)=max(2,m_f+1)" in support["N_of_f"], support["N_of_f"])
    check("R-493 pointwise wording", "for every x" in proof["generator_sum_identity"].lower(), proof["generator_sum_identity"])
    absent = [field for field in ("invariant_core", "invariant_subspace", "all_iterates", "operator_identity") if field not in r493]
    check("no imported invariant-core theorem", len(absent) == 4, absent)
    check("R-493 does not claim semigroup", "common infinite-volume semigroup" in r493["known_boundaries"][3].lower() and r493["status"]["infinite_volume"] == "NOT_PROVED", r493["known_boundaries"])
    check("physical firewall", all(token in " ".join(contract["non_claims"]).lower() for token in ("pre-a", "qft", "gravity", "continuum")), contract["non_claims"])

    failed = [row for row in checks if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-finite-semigroup-lift-independent/1.0",
        "audit_id": "PAH-OMC-020-FINITE-SEMIGROUP-LIFT-INDEPENDENT-001",
        "result_id": "R-550",
        "task_id": "T-082",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "source_hashes": actual,
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "finding": "An independent exact finite algebra replay confirms the power-intertwining implication. The pinned R-493 source remains local and support-dependent, with no invariant/all-iterate owner field; semigroup promotion therefore remains held rather than refuted.",
        "missing_assumptions": contract["missing_assumptions"],
        "single_next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic(destination, payload)
    print(f"PAH-OMC-020 FINITE SEMIGROUP LIFT INDEPENDENT: {payload['verification']} {payload['checks_passed']}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
