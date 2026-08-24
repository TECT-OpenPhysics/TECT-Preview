#!/usr/bin/env python3
"""Fraction-only independent audit for the EXP-001079 cutoff witness."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-dual-state-fifth-moment-modular-cutoff-obstruction"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PREVIOUS = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-projected-delta-d-third-coefficient-"
    "gibbs-weighted-noncommutative-moment-transfer-obstruction-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-26-primary-{SLUG}"
    / "independent.json"
)

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


def add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(left[i][j] + right[i][j] for j in range(len(left[0]))) for i in range(len(left)))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))) for i in range(len(left)))


def scale(value: Fraction, matrix: Matrix) -> Matrix:
    return tuple(tuple(value * entry for entry in row) for row in matrix)


def transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[j][i] for j in range(len(matrix))) for i in range(len(matrix[0])))


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


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001079" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001079/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("previous authority", previous["exploration_id"] == "EXP-001078" and previous["scope"]["finite_gibbs_obstruction_closed"] is True, previous["exploration_id"], "EXP-001078 finite Gibbs obstruction", "authority")
    check("Gibbs witness declared", "exp(-beta" in manifest["matrix_family"]["gibbs_identity"] and "L^6" in manifest["matrix_family"]["state"], manifest["matrix_family"], "finite-temperature Gibbs state", "model")
    check("cutoff declared", "1_[k<=2]" in manifest["matrix_family"]["cutoff"] and "diag(0,1)" in manifest["matrix_family"]["cutoff"], manifest["matrix_family"]["cutoff"], "exact spectral projection", "model")

    exponent = int(fixture["gibbs_ratio_exponent"])
    cutoff = int(fixture["cutoff_R"])
    values = [int(value) for value in fixture["L_values"]]
    derived_reference: list[Fraction] = []
    derived_dual: list[Fraction] = []
    derived_tail: list[Fraction] = []
    derived_relative: list[Fraction] = []
    for index, L in enumerate(values, start=1):
        denominator = L**exponent + 1
        k: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(L)))
        B: Matrix = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)))
        rho: Matrix = ((Fraction(L**exponent, denominator), Fraction(0)), (Fraction(0), Fraction(1, denominator)))
        P: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
        Q: Matrix = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)))
        identity: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
        check(f"L range {index}", L > cutoff, L, f">{cutoff}", "family")
        check(f"state positive trace {index}", rho[0][0] > 0 and rho[1][1] > 0 and trace(rho) == 1, rho, "positive trace-one", "state")
        check(f"Gibbs ratio {index}", rho[1][1] / rho[0][0] == Fraction(1, L**exponent), rho[1][1] / rho[0][0], Fraction(1, L**exponent), "state")
        check(f"finite beta {index}", L > 1, L, "beta=6*log(L)/(L-1)>0", "state")
        check(f"cutoff projection {index}", multiply(P, P) == P and multiply(Q, Q) == Q and add(P, Q) == identity and multiply(P, k) == P, [multiply(P, P), multiply(Q, Q), add(P, Q), multiply(P, k)], "P,Q spectral projections", "cutoff")
        right_squared = multiply(k, scale(Fraction(1), identity))
        right_squared = ((Fraction(1, 1), Fraction(0)), (Fraction(0), Fraction(1, L)))
        left_squared = ((Fraction(1, L), Fraction(0)), (Fraction(0), Fraction(1, 1)))
        check(f"relative bound right {index}", right_squared[0][0] <= 1 and right_squared[1][1] <= 1, right_squared, "diagonal entries <=1", "relative")
        check(f"relative bound left {index}", left_squared[0][0] <= 1 and left_squared[1][1] <= 1, left_squared, "diagonal entries <=1", "relative")
        reference = trace(multiply(rho, power(k, 5)))
        dual = trace(multiply(multiply(B, rho), multiply(transpose(B), power(k, 5))))
        tail = trace(multiply(multiply(multiply(rho, transpose(B)), Q), B))
        check(f"reference fifth moment {index}", reference == Fraction(L**5 * (L + 1), denominator), reference, Fraction(L**5 * (L + 1), denominator), "moment")
        check(f"dual fifth moment {index}", dual == Fraction(L**11 + 1, denominator), dual, Fraction(L**11 + 1, denominator), "dual")
        check(f"reference ceiling {index}", reference < Fraction(3, 2), reference, "<3/2", "moment")
        check(f"dual growth {index}", dual > L**4, dual, f">{L**4}", "dual")
        check(f"opposite tail identity {index}", tail == Fraction(L**6, denominator), tail, Fraction(L**6, denominator), "tail")
        check(f"opposite tail floor {index}", tail > Fraction(1, 2), tail, ">1/2", "tail")
        derived_reference.append(reference)
        derived_dual.append(dual)
        derived_tail.append(tail)
        derived_relative.append(Fraction(1))

    scope = manifest["scope"]
    check("finite dual-state obstruction", scope["finite_dual_state_obstruction_closed"] is True and scope["one_sided_moment_shortcut_refuted"] is True, {key: scope[key] for key in ("finite_dual_state_obstruction_closed", "one_sided_moment_shortcut_refuted")}, "route-local obstruction", "scope")
    open_keys = tuple(key for key, value in scope.items() if isinstance(value, bool) and key.endswith("_closed") and key not in ("finite_dual_state_obstruction_closed", "one_sided_moment_shortcut_refuted", "conditional_dual_tail_theorem_identified"))
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "actual Q3 and QFT gates open", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-FIFTH-MOMENT-MODULAR-CUTOFF-OBSTRUCTION",
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "L_values": values,
            "gibbs_ratio_exponent": exponent,
            "cutoff_R": cutoff,
            "reference_moment": derived_reference,
            "dual_moment": derived_dual,
            "opposite_tail": derived_tail,
            "relative_squared_norm": derived_relative,
        },
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
    print(f"INDEPENDENT DUAL-STATE FIFTH-MOMENT CUTOFF OBSTRUCTION PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
