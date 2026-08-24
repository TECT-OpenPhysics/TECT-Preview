#!/usr/bin/env python3
"""Fraction-only independent Gibbs-weighted audit for EXP-001078."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-gibbs-weighted-noncommutative-moment-transfer-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-noncommutative-moment-transfer-obstruction-manifest.json"
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
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))) for i in range(len(left)))


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

    check("identity", manifest["exploration_id"] == "EXP-001078" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001078/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001077" and previous["scope"]["finite_matrix_obstruction_closed"] is True, previous["exploration_id"], "EXP-001077 finite obstruction", "authority")
    check("Gibbs witness declared", "exp(-beta" in manifest["matrix_family"]["gibbs_identity"] and "L^6" in manifest["matrix_family"]["state"], manifest["matrix_family"], "finite-temperature Gibbs state", "model")
    check("candidate declared", "Q_sigma^2" in manifest["candidate_test"]["from_EXP_001076"] and manifest["candidate_test"]["powered_comparison"].startswith("(Q_sigma^2)^10"), manifest["candidate_test"], "powered Q candidate", "model")

    coefficient = frac(fixture["candidate_coefficient"])
    exponent = int(fixture["candidate_power"])
    gibbs_exponent = int(fixture["gibbs_ratio_exponent"])
    pairs = [(int(t), int(s)) for t, s in fixture["pell_pairs"]]
    derived_m5: list[Fraction] = []
    derived_q: list[Fraction] = []
    derived_ratio: list[Fraction] = []
    for index, (t, s) in enumerate(pairs, start=1):
        L = t * t
        denominator = L**gibbs_exponent + 1
        A: Matrix = ((Fraction(1, 2), Fraction(t, 2)), (Fraction(t, 2), Fraction(L, 2)))
        P: Matrix = ((Fraction(1, 2), Fraction(-t, 2)), (Fraction(-t, 2), Fraction(L, 2)))
        K: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(L)))
        rho: Matrix = ((Fraction(L**gibbs_exponent, denominator), Fraction(0)), (Fraction(0), Fraction(1, denominator)))
        u = (Fraction(1), Fraction(t))
        w = (Fraction(1), Fraction(-t))
        check(f"Pell equation {index}", t * t - 2 * s * s == -1, t * t - 2 * s * s, -1, "family")
        check(f"positive L {index}", L > 1, L, ">1", "family")
        check(f"A factor {index}", A == scale(Fraction(1, 2), outer(u)), A, "rank-one factor", "positivity")
        check(f"P factor {index}", P == scale(Fraction(1, 2), outer(w)), P, "rank-one factor", "positivity")
        check(f"K sum {index}", add(A, P) == K, add(A, P), K, "form")
        check(f"rho positive trace {index}", rho[0][0] > 0 and rho[1][1] > 0 and trace(rho) == 1, rho, "positive trace-one", "state")
        check(f"Gibbs ratio {index}", rho[1][1] / rho[0][0] == Fraction(1, L**gibbs_exponent), rho[1][1] / rho[0][0], Fraction(1, L**gibbs_exponent), "state")
        commutator = add(multiply(rho, A), scale(Fraction(-1), multiply(A, rho)))
        check(f"nontracial commutator {index}", commutator != ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))), commutator, "nonzero", "state")
        check(f"Pell square {index}", Fraction(1 + L, 2) == s * s, Fraction(1 + L, 2), s * s, "family")
        check(f"A power identity {index}", multiply(A, A) == scale(Fraction(s * s), A), multiply(A, A), scale(Fraction(s * s), A), "power")
        A32 = scale(Fraction(s), A)
        m5 = trace(multiply(rho, power(K, 5)))
        q_squared = 2 * trace(multiply(rho, A32))
        right_power = coefficient**exponent * m5**3
        powered_ratio = q_squared**exponent / right_power
        check(f"finite beta {index}", L > 1, L, "beta=6*log(L)/(L-1)>0", "state")
        check(f"K fifth Gibbs moment {index}", m5 == Fraction(L**5 * (L + 1), denominator), m5, Fraction(L**5 * (L + 1), denominator), "moment")
        check(f"Q squared Gibbs identity {index}", q_squared == Fraction(s * (L**gibbs_exponent + L), denominator), q_squared, Fraction(s * (L**gibbs_exponent + L), denominator), "moment")
        check(f"powered candidate violation {index}", q_squared**exponent > right_power, q_squared**exponent, f"> {right_power}", "obstruction")
        check(f"powered ratio {index}", powered_ratio > 1, powered_ratio, ">1", "obstruction")
        derived_m5.append(m5)
        derived_q.append(q_squared)
        derived_ratio.append(powered_ratio)

    scope = manifest["scope"]
    check("obstruction scope", scope["finite_gibbs_obstruction_closed"] is True and scope["gibbs_weight_only_transfer_refuted"] is True, {key: scope[key] for key in ("finite_gibbs_obstruction_closed", "gibbs_weight_only_transfer_refuted")}, "route-local Gibbs obstruction", "scope")
    open_keys = ("actual_q3_gibbs_transfer_refuted", "actual_q3_m5_to_q_transfer_refuted", "actual_q3_mixed_moment_bound_closed", "actual_q3_multiplication_domination_closed", "noncommutative_quadratic_form_transfer_closed", "modular_companion_bound_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_projected_d_duhamel_cauchy_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual Q3 and QFT gates open", "scope")

    derived = {"candidate_coefficient": coefficient, "candidate_power": exponent, "gibbs_ratio_exponent": gibbs_exponent, "m5": derived_m5, "matrix_Q_squared": derived_q, "powered_violation_ratio": derived_ratio}
    passed = len(rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-PROJECTED-DELTA-D-THIRD-COEFFICIENT-GIBBS-WEIGHTED-NONCOMMUTATIVE-MOMENT-TRANSFER-OBSTRUCTION",
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
    print(f"INDEPENDENT GIBBS-WEIGHTED NONCOMMUTATIVE M5-TO-Q OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
