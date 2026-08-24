#!/usr/bin/env python3
"""Exact primary audit of an actual local Q3 Duhamel-word coefficient.

The word contains m-1 onsite potential differences at one Q3 coordinate and
one selected spatial-bond potential difference.  It is an actual ordered
local word of the split polynomial, not a claim about the full signed Dyson
sum.  The audit keeps that distinction explicit.
"""

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

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-actual-history-word"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def frac(value: str | int) -> Fraction:
    return Fraction(str(value))


def safe(value: Any) -> Any:
    if isinstance(value, (Fraction, sp.Rational)):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def species() -> tuple[tuple[int, int, int], ...]:
    return tuple(product((0, 1), repeat=3))


def species_edges() -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    result: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    for left in species():
        for axis in range(3):
            if left[axis] == 0:
                right = tuple(1 if index == axis else left[index] for index in range(3))
                result.append((left, right))
    return tuple(result)


def q3_edge_potential(left: sp.Expr, right: sp.Expr, coupling: sp.Expr) -> sp.Expr:
    return coupling * (left - right) ** 2 * (left**2 + right**2) / 4


def restricted_onsite(q: sp.Expr, g: sp.Expr, coupling: sp.Expr) -> sp.Expr:
    """Canonical onsite plus the three Q3 edges incident to 000, others zero."""
    node = (0, 0, 0)
    incident = sum((1 for left, right in species_edges() if left == node or right == node), 0)
    return sp.expand(g * q**4 / 4 + incident * q3_edge_potential(q, sp.Integer(0), coupling))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g = sp.Rational(str(fixture["g"]))
    coupling = sp.Rational(str(fixture["lambda"]))
    spatial = sp.Rational(str(fixture["spatial_coupling"]))
    q, r, a = sp.symbols("q r a")
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001038", manifest["exploration_id"], "EXP-001038", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    node_degree = sum(1 for left, right in species_edges() if left == (0, 0, 0) or right == (0, 0, 0))
    audit.check("Q3 node degree", node_degree == 3, node_degree, 3, "canonical-model")
    G = sp.expand(g + node_degree * coupling)
    expected_G = sp.Rational(str(fixture["G"]))
    audit.check("restricted G", G == expected_G, G, expected_G, "canonical-model")

    restricted = restricted_onsite(q, g, coupling)
    audit.check("restricted potential", restricted == G * q**4 / 4, restricted, G * q**4 / 4, "canonical-model")
    onsite_difference = sp.expand(restricted - restricted.subs(q, q - a))
    expected_difference = sp.expand(G * (q**4 - (q - a) ** 4) / 4)
    audit.check("actual onsite difference", onsite_difference == expected_difference, onsite_difference, expected_difference, "local-word")

    bond_difference = sp.expand(spatial * ((q - r) ** 2 - (q - a - r) ** 2) / 2)
    audit.check("selected bond derivative", sp.diff(bond_difference, r) == -spatial * a, sp.diff(bond_difference, r), -spatial * a, "local-word")

    rows: list[dict[str, Any]] = []
    for m in (int(value) for value in fixture["word_lengths"]):
        ordered = sp.factor(sp.diff(onsite_difference ** (m - 1) * bond_difference, r).subs({q: 0, r: 0}))
        symmetrized = sp.factor(m * ordered)
        degree = int(sp.degree(ordered, a))
        expected_degree = 4 * m - 3
        expected_ordered = sp.factor(-spatial * (-G / 4) ** (m - 1) * a**expected_degree)
        expected_sym = sp.factor(-m * spatial * (-G / 4) ** (m - 1) * a**expected_degree)
        audit.check(f"ordered word identity m={m}", sp.expand(ordered - expected_ordered) == 0, ordered, expected_ordered, "local-word")
        audit.check(f"symmetrized word identity m={m}", sp.expand(symmetrized - expected_sym) == 0, symmetrized, expected_sym, "local-word")
        audit.check(f"word degree m={m}", degree == expected_degree, degree, expected_degree, "local-word")
        audit.check(f"nonzero leading coefficient m={m}", sp.LC(sp.Poly(ordered, a)) != 0, sp.LC(sp.Poly(ordered, a)), "nonzero", "local-word")
        rows.append({"word_length": m, "degree": degree, "ordered": ordered, "symmetrized": symmetrized, "leading_coefficient": sp.LC(sp.Poly(ordered, a))})

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY ACTUAL-Q3-HISTORY-WORD PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
