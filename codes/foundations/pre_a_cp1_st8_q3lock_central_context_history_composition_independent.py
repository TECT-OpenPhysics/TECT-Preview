#!/usr/bin/env python3
"""Independent Fraction audit for EXP-001048.

This lane has its own polynomial and exact-matrix implementations.  It
recomputes the EXP-001045 source rate, checks the four-context insertion on a
finite diagonal fixture, and evaluates only the conditional scalar EGF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-central-context-history-composition"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"
Poly = dict[tuple[int, ...], F]
Matrix = list[list[F]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


def clean_poly(poly: Poly) -> Poly:
    return {monomial: coefficient for monomial, coefficient in poly.items() if coefficient}


def add(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] = result.get(monomial, F(0)) + coefficient
    return clean_poly(result)


def scale(poly: Poly, coefficient: F) -> Poly:
    return clean_poly({monomial: coefficient * value for monomial, value in poly.items()})


def mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
            result[monomial] = result.get(monomial, F(0)) + left_coefficient * right_coefficient
    return clean_poly(result)


def power(poly: Poly, exponent: int) -> Poly:
    result = {(0,) * len(next(iter(poly))): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def variable(index: int, dimension: int) -> Poly:
    exponent = [0] * dimension
    exponent[index] = 1
    return {tuple(exponent): F(1)}


def weighted_rate(poly: Poly, source_radius: F, root_scale: F, neighbour_root: F, neighbour_index: int) -> F:
    return sum(abs(coefficient) * root_scale ** sum(monomial[:-1]) * neighbour_root ** monomial[neighbour_index] * source_radius ** monomial[-1] for monomial, coefficient in poly.items())


def eye(size: int) -> Matrix:
    return [[F(int(row == column)) for column in range(size)] for row in range(size)]


def diag(values: list[F]) -> Matrix:
    return [[values[row] if row == column else F(0) for column in range(len(values))] for row in range(len(values))]


def matrix_scale(value: F, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def matrix_mul(left: Matrix, right: Matrix) -> Matrix:
    return [[sum((left[row][inner] * right[inner][column] for inner in range(len(right))), F(0)) for column in range(len(right[0]))] for row in range(len(left))]


def matrix_norm(matrix: Matrix) -> F:
    return max((sum(abs(entry) for entry in row) for row in matrix), default=F(0))


def matrix_product(factors: list[Matrix]) -> Matrix:
    result = eye(len(factors[0]))
    for factor in factors:
        result = matrix_mul(result, factor)
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = upstream["fixture"]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001048" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001048/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045", "provenance")
    audit.check("four contexts declared", len(manifest["central_context"]["contexts"]) == 4, len(manifest["central_context"]["contexts"]), 4, "hypothesis")

    gamma = F(fixture["gamma"])
    kappa = F(fixture["kappa"])
    root_scale = F(fixture["root_scale"])
    neighbour_root = F(fixture["neighbor_factor_root"])
    source_radius = F(fixture["source_radius"])
    lam = F(fixture["lambda"])
    coupling = F(fixture["spatial_coupling"])
    audit.check("positive upstream inputs", gamma > 0 and kappa > 0 and source_radius > 0, [gamma, kappa, source_radius], ">0", "input")
    audit.check("registered energy ratio", root_scale**4 == kappa / gamma, [root_scale**4, kappa / gamma], "equal", "input")

    q, v, r, a = variable(0, 3), variable(1, 3), variable(1, 3), variable(2, 3)
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a_minus_v = add(q, scale(a, F(-1)), scale(v, F(-1)))
    edge_u = scale(add(mul(power(q_minus_v, 2), add(power(q, 2), power(v, 2))), scale(mul(power(q_minus_a_minus_v, 2), add(power(add(q, scale(a, F(-1))), 2), power(v, 2))), F(-1))), lam / 4)
    q_minus_r = add(q, scale(r, F(-1)))
    q_minus_a_minus_r = add(q, scale(a, F(-1)), scale(r, F(-1)))
    bond_u = scale(add(power(q_minus_r, 2), scale(power(q_minus_a_minus_r, 2), F(-1))), coupling / 2)
    onsite_q, onsite_a = variable(0, 2), variable(1, 2)
    onsite = scale(add(power(onsite_q, 4), scale(power(add(onsite_q, scale(onsite_a, F(-1))), 4), F(-1))), F(3, 20))
    edge_rate = weighted_rate(edge_u, source_radius, root_scale, neighbour_root, 1)
    bond_rate = weighted_rate(bond_u, source_radius, root_scale, neighbour_root, 1)
    onsite_rate = weighted_rate(onsite, source_radius, root_scale, F(1), 0)
    B = onsite_rate + 3 * edge_rate + 6 * bond_rate
    expected_B = F(fixture["expected_local_rate"])
    audit.check("source rate recomputed", B == expected_B, B, expected_B, "source-rate")
    audit.check("source components positive", all(value > 0 for value in (onsite_rate, edge_rate, bond_rate, B)), [onsite_rate, edge_rate, bond_rate, B], ">0", "source-rate")

    A = diag([F(1), F(16), F(256)])
    As = diag([F(1), F(8), F(64)])
    Ais = diag([F(1), F(1, 8), F(1, 64)])
    audit.check("fractional energy fixture", matrix_mul(matrix_mul(matrix_mul(As, As), As), As) == matrix_mul(matrix_mul(A, A), A), True, True, "fixture")
    audit.check("inverse energy fixture", matrix_mul(As, Ais) == eye(3) and matrix_mul(Ais, As) == eye(3), matrix_mul(As, Ais), "I", "fixture")
    coefficients = [B / F(index) for index in range(1, len(manifest["central_context"]["finite_fixture"]["factor_multipliers"]) + 1)]
    factors = [matrix_scale(coefficient, Ais) for coefficient in coefficients]
    contexts = [(0, 0), (0, 1), (1, 0), (1, 1)]
    context_rows: list[dict[str, Any]] = []
    for index, factor in enumerate(factors):
        for left_bit, right_bit in contexts:
            left = As if left_bit else eye(3)
            right = Ais if right_bit else eye(3)
            value = matrix_norm(matrix_mul(matrix_mul(left, factor), right))
            audit.check(f"context bound D{index + 1} ({left_bit},{right_bit})", value <= B, value, f"<={B}", "central-context")
            context_rows.append({"factor": index + 1, "left": left_bit, "right": right_bit, "value": value})

    word_rows: list[dict[str, Any]] = []
    for length in range(1, len(factors) + 1):
        for left_bit, right_bit in contexts:
            left = As if left_bit else eye(3)
            right = Ais if right_bit else eye(3)
            direct = matrix_mul(matrix_mul(left, matrix_product(factors[:length])), right)
            if length == 1:
                inserted = direct
            else:
                pieces = [matrix_mul(matrix_mul(left, factors[0]), Ais)]
                pieces.extend(matrix_mul(matrix_mul(As, factors[index]), Ais) for index in range(1, length - 1))
                pieces.append(matrix_mul(matrix_mul(As, factors[length - 1]), right))
                inserted = matrix_product(pieces)
            norm_value = matrix_norm(direct)
            audit.check(f"central insertion length={length} context={left_bit},{right_bit}", direct == inserted, direct, "inserted product", "insertion")
            audit.check(f"word bound length={length} context={left_bit},{right_bit}", norm_value <= B**length, norm_value, f"<={B**length}", "word-bound")
            word_rows.append({"length": length, "left": left_bit, "right": right_bit, "norm": norm_value, "bound": B**length})

    passage = manifest["first_passage_bridge"]
    orientations = F(passage["orientations"])
    degree = F(passage["degree_bound"])
    base = F(passage["spatial_base"])
    time = F(passage["time"])
    distance = int(passage["distance"])
    eta = orientations * degree * base * B * time
    order = 32
    partial = sum((eta**n) / math.factorial(n) for n in range(order + 1))
    audit.check("factorial EGF exponent positive", eta > 0, eta, ">0", "first-passage")
    audit.check("finite EGF below exponential", float(partial) <= math.exp(float(eta)), partial, "<=exp(eta)", "first-passage")
    audit.check("distance factor exact", base ** (-distance) == F(1, int(base**distance)), base ** (-distance), "exact", "first-passage")
    audit.check("conditional scope", manifest["scope"]["central_context_word_bound_closed_conditionally"] is True and manifest["scope"]["actual_q3_central_context_proved"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "conditional/open", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "context_rows": context_rows,
        "word_rows": word_rows,
        "derived": {
            "energy_exponent": F(3, 4),
            "source_rate_B": B,
            "onsite_rate": onsite_rate,
            "edge_rate": edge_rate,
            "bond_rate": bond_rate,
            "context_count": len(contexts),
            "word_lengths_checked": len(factors),
            "central_context_fixture_closed": True,
            "history_word_bound_closed_conditionally": True,
            "factorial_first_passage_envelope_closed_conditionally": True,
            "factorial_first_passage_hypothesis_supplied": False,
            "eta": eta,
            "partial_order": order,
            "distance": distance,
            "distance_envelope_symbolic": "2^(-10)*exp(eta)",
            "actual_q3_central_context_proved": False,
            "actual_q3_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "upstream_manifest": str(UPSTREAM.relative_to(REPO)).replace("\\", "/"),
            "upstream_manifest_sha256": sha256(UPSTREAM),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT Q3-CENTRAL-CONTEXT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
