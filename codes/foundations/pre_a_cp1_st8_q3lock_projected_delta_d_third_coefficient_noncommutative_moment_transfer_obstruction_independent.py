#!/usr/bin/env python3
"""Fraction-only independent audit for EXP-001077."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-noncommutative-moment-transfer-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-scalar-energy-moment-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "independent.json"

Matrix = tuple[tuple[Fraction, ...], ...]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def frac(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(left[i][j] + right[i][j] for j in range(len(left[0]))) for i in range(len(left)))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0])))
        for i in range(len(left))
    )


def scale(value: Fraction, matrix: Matrix) -> Matrix:
    return tuple(tuple(value * entry for entry in row) for row in matrix)


def power(matrix: Matrix, exponent: int) -> Matrix:
    result: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    base = matrix
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        remaining >>= 1
    return result


def trace(matrix: Matrix) -> Fraction:
    return sum(matrix[index][index] for index in range(len(matrix)))


def outer(vector: tuple[Fraction, Fraction]) -> Matrix:
    return tuple(tuple(vector[i] * vector[j] for j in range(2)) for i in range(2))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001077" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001077/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001076" and previous["scope"]["candidate_P_Q_formula_closed"] is True, previous["exploration_id"], "EXP-001076 scalar candidate", "authority")
    check("matrix family declared", "Pell pairs" in manifest["matrix_family"]["parameters"] and "nontracial" in manifest["candidate_test"]["meaning"], manifest["matrix_family"], "exact matrix family", "model")
    check("candidate bound declared", manifest["candidate_test"]["from_EXP_001076"].startswith("For m5=1"), manifest["candidate_test"]["from_EXP_001076"], "m5=1 candidate", "model")

    bound = frac(fixture["candidate_Q_squared_bound"])
    pairs = [(int(t), int(s)) for t, s in fixture["pell_pairs"]]
    derived_q: list[Fraction] = []
    derived_ratio: list[Fraction] = []
    for index, (t, s) in enumerate(pairs, start=1):
        L = t * t
        A: Matrix = ((Fraction(1, 2), Fraction(t, 2)), (Fraction(t, 2), Fraction(L, 2)))
        P: Matrix = ((Fraction(1, 2), Fraction(-t, 2)), (Fraction(-t, 2), Fraction(L, 2)))
        K: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(L)))
        rho: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
        u = (Fraction(1), Fraction(t))
        w = (Fraction(1), Fraction(-t))
        check(f"pell equation {index}", t * t - 2 * s * s == -1, t * t - 2 * s * s, -1, "family")
        check(f"A factor {index}", A == scale(Fraction(1, 2), outer(u)), A, "rank-one factor", "positivity")
        check(f"P factor {index}", P == scale(Fraction(1, 2), outer(w)), P, "rank-one factor", "positivity")
        check(f"K sum {index}", add(A, P) == K, add(A, P), K, "form")
        check(f"K positive diagonal {index}", K[0][0] == 1 and K[1][1] == L and L > 0, K, "positive diagonal", "form")
        check(f"state trace {index}", trace(rho) == 1 and rho[0][0] >= 0 and rho[1][1] >= 0, rho, "positive trace-one", "state")
        commutator = add(multiply(rho, A), scale(Fraction(-1), multiply(A, rho)))
        check(f"nontracial commutator {index}", commutator != ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))), commutator, "nonzero", "state")
        s_from_t = Fraction(1 + L, 2)
        check(f"Pell square {index}", s_from_t == s * s, s_from_t, s * s, "family")
        check(f"A power identity {index}", multiply(A, A) == scale(Fraction(s * s), A), multiply(A, A), scale(Fraction(s * s), A), "power")
        A32 = scale(Fraction(s), A)
        phi_k5 = trace(multiply(rho, power(K, 5)))
        phi_a32 = trace(multiply(rho, A32))
        q_squared = 2 * phi_a32
        ratio = q_squared / bound
        check(f"K fifth moment {index}", phi_k5 == 1, phi_k5, 1, "moment")
        check(f"Q squared identity {index}", q_squared == s, q_squared, s, "moment")
        check(f"candidate violation {index}", q_squared > bound, q_squared, f"> {bound}", "obstruction")
        check(f"ratio {index}", ratio == Fraction(4, 9) * s, ratio, Fraction(4, 9) * s, "obstruction")
        derived_q.append(q_squared)
        derived_ratio.append(ratio)

    expected_q = [frac(fixture["derived_first_matrix_Q_squared"]), frac(fixture["derived_second_matrix_Q_squared"]), frac(fixture["derived_third_matrix_Q_squared"])]
    expected_ratio = [frac(fixture["derived_first_violation_ratio"]), frac(fixture["derived_second_violation_ratio"]), frac(fixture["derived_third_violation_ratio"])]
    check("Q fixture values", derived_q == expected_q, derived_q, expected_q, "fixture")
    check("ratio fixture values", derived_ratio == expected_ratio, derived_ratio, expected_ratio, "fixture")
    scope = manifest["scope"]
    check("obstruction scope", scope["finite_matrix_obstruction_closed"] is True and scope["form_order_only_transfer_refuted"] is True, {key: scope[key] for key in ("finite_matrix_obstruction_closed", "form_order_only_transfer_refuted")}, "route-local obstruction", "scope")
    open_keys = ("actual_q3_m5_to_q_transfer_refuted", "actual_q3_mixed_moment_bound_closed", "actual_q3_multiplication_domination_closed", "noncommutative_quadratic_form_transfer_closed", "modular_companion_bound_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual Q3 and QFT gates open", "scope")

    derived = {"candidate_Q_squared_bound": bound, "matrix_Q_squared": derived_q, "violation_ratio": derived_ratio, "m5": Fraction(1)}
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-COEFFICIENT-NONCOMMUTATIVE-MOMENT-TRANSFER-OBSTRUCTION",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": passed,
        "assertion_count": passed,
        "assertions": rows,
        "derived": derived,
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if args.output:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT NONCOMMUTATIVE M5-TO-Q TRANSFER OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
