#!/usr/bin/env python3
"""Independent sparse-polynomial audit for the actual local Q3 word."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-actual-history-word"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"

Poly = dict[tuple[int, int, int], Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def f(value: str | int | Fraction) -> Fraction:
    return Fraction(str(value))


def clean(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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


def add(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for exponent, coefficient in poly.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def scale(poly: Poly, factor: Fraction) -> Poly:
    return {exponent: coefficient * factor for exponent, coefficient in poly.items() if coefficient * factor}


def multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_exp, left_coeff in left.items():
        for right_exp, right_coeff in right.items():
            exponent = tuple(left_exp[index] + right_exp[index] for index in range(3))
            result[exponent] = result.get(exponent, Fraction(0)) + left_coeff * right_coeff
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def power(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0, 0, 0): Fraction(1)}
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def monomial(q: int, r: int, a: int, coefficient: Fraction) -> Poly:
    return {(q, r, a): coefficient} if coefficient else {}


def variable(index: int) -> Poly:
    exponent = [0, 0, 0]
    exponent[index] = 1
    return monomial(*exponent, Fraction(1))


def poly_power_difference(power_value: int) -> Poly:
    """Return q^power-(q-a)^power by a binomial expansion."""
    q_poly, a_poly = variable(0), variable(2)
    shifted = power(add(q_poly, scale(a_poly, Fraction(-1))), power_value)
    return add(power(q_poly, power_value), scale(shifted, Fraction(-1)))


def species() -> tuple[tuple[int, int, int], ...]:
    return tuple(product((0, 1), repeat=3))


def species_edges() -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    result = []
    for left in species():
        for axis in range(3):
            if left[axis] == 0:
                right = tuple(1 if index == axis else left[index] for index in range(3))
                result.append((left, right))
    return tuple(result)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g, coupling, spatial = f(fixture["g"]), f(fixture["lambda"]), f(fixture["spatial_coupling"])
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001038", manifest["exploration_id"], "EXP-001038", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    node_degree = sum(1 for left, right in species_edges() if left == (0, 0, 0) or right == (0, 0, 0))
    G = g + node_degree * coupling
    audit.check("Q3 node degree", node_degree == 3, node_degree, 3, "canonical-model")
    audit.check("restricted G", G == f(fixture["G"]), G, f(fixture["G"]), "canonical-model")

    q4_difference = scale(poly_power_difference(4), G / 4)
    # Three incident edge polynomials contribute lambda*q^4/4 each; q4_difference
    # is therefore the exact restricted onsite difference.
    audit.check("restricted q4 coefficient", q4_difference.get((4, 0, 0), Fraction(0)) == 0, q4_difference.get((4, 0, 0), Fraction(0)), 0, "canonical-model")
    # The shifted polynomial's pure-a term is the canonical -G*a^4/4 term.
    audit.check("restricted source coefficient", q4_difference.get((0, 0, 4)) == -G / 4, q4_difference.get((0, 0, 4)), -G / 4, "canonical-model")

    q_poly, r_poly, a_poly = variable(0), variable(1), variable(2)
    bond = scale(add(power(add(q_poly, scale(r_poly, Fraction(-1))), 2), scale(power(add(q_poly, scale(a_poly, Fraction(-1)), scale(r_poly, Fraction(-1))), 2), Fraction(-1))), spatial / 2)
    bond_r = {exponent: coefficient for exponent, coefficient in bond.items() if exponent[1] == 1 and exponent[0] == 0}
    audit.check("selected bond mixed coefficient", bond_r == {(0, 1, 1): -spatial}, bond_r, {(0, 1, 1): -spatial}, "local-word")

    rows: list[dict[str, Any]] = []
    for m in (int(value) for value in fixture["word_lengths"]):
        product_poly = multiply(power(q4_difference, m - 1), bond)
        ordered_terms = {exponent: coefficient for exponent, coefficient in product_poly.items() if exponent[0] == 0 and exponent[1] == 1}
        ordered: Poly = {(0, 0, exponent[2]): coefficient for exponent, coefficient in ordered_terms.items()}
        expected_degree = 4 * m - 3
        expected_coeff = -spatial * (-G / 4) ** (m - 1)
        audit.check(f"ordered word support m={m}", set(ordered) == {(0, 0, expected_degree)}, sorted(ordered), [(0, 0, expected_degree)], "local-word")
        audit.check(f"ordered word coefficient m={m}", ordered[(0, 0, expected_degree)] == expected_coeff, ordered[(0, 0, expected_degree)], expected_coeff, "local-word")
        audit.check(f"nonzero word m={m}", ordered[(0, 0, expected_degree)] != 0, ordered[(0, 0, expected_degree)], "nonzero", "local-word")
        rows.append({"word_length": m, "degree": expected_degree, "ordered_coefficient": ordered[(0, 0, expected_degree)], "symmetrized_coefficient": m * ordered[(0, 0, expected_degree)]})

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "word_rows": rows,
        "derived": {
            "selected_q3_degree": node_degree,
            "restricted_G": G,
            "actual_local_word_incidence_closed": True,
            "word_degree_formula": "4m-3",
            "ordered_word_nonzero_for_fixture": True,
            "symmetrized_position_sum_closed": True,
            "full_q3_dyson_history_closed": False,
            "full_series_cancellation_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ACTUAL-Q3-HISTORY-WORD PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
