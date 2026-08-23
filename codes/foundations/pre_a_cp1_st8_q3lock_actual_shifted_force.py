#!/usr/bin/env python3
"""Primary exact audit of the actual finite-Q3 shifted force polynomial.

The force is the onsite cubic plus the Q3-lock edge force and a linear
nearest-neighbour spatial term.  The audit proves an exact one-step source
shift coefficient table and checks a volume-independent finite-lattice bound.
It does not claim that the one-step estimate closes the repeated Q3 history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-actual-shifted-force"
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
    nodes = species()
    return tuple((left, right) for left in nodes for axis in range(3) if left[axis] == 0 for right in [tuple(1 if i == axis else left[i] for i in range(3))])


def sites(side: int, dimension: int) -> tuple[tuple[int, ...], ...]:
    return tuple(product(range(side), repeat=dimension))


def spatial_neighbours(site: tuple[int, ...], side: int) -> tuple[tuple[int, ...], ...]:
    result: list[tuple[int, ...]] = []
    for axis in range(len(site)):
        for direction in (-1, 1):
            shifted = list(site)
            shifted[axis] += direction
            if 0 <= shifted[axis] < side:
                result.append(tuple(shifted))
    return tuple(result)


def q3_edge_force(left: Fraction, right: Fraction, coupling: Fraction) -> Fraction:
    return coupling * (left**3 - Fraction(3, 2) * left**2 * right + left * right**2 - Fraction(1, 2) * right**3)


def q3_force(values: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]], site: tuple[int, ...], node: tuple[int, int, int], g: Fraction, coupling: Fraction) -> Fraction:
    a = values[site][node]
    total = g * a**3
    for left, right in species_edges():
        if left == node:
            total += q3_edge_force(a, values[site][right], coupling)
        elif right == node:
            # The derivative with respect to the second endpoint is the same
            # edge polynomial with the endpoints exchanged.
            total += q3_edge_force(a, values[site][left], coupling)
    return total


def spatial_force(values: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]], site: tuple[int, ...], node: tuple[int, int, int], side: int, coupling: Fraction) -> Fraction:
    return -coupling * sum((values[other][node] for other in spatial_neighbours(site, side)), Fraction(0))


def shifted_edge_coefficient_table() -> dict[int, Fraction]:
    q, r, u, v = sp.symbols("q r u v")
    polynomial = sp.expand((q + u) ** 3 - sp.Rational(3, 2) * (q + u) ** 2 * (r + v) + (q + u) * (r + v) ** 2 - sp.Rational(1, 2) * (r + v) ** 3 - (q**3 - sp.Rational(3, 2) * q**2 * r + q * r**2 - sp.Rational(1, 2) * r**3))
    grouped: defaultdict[int, sp.Rational] = defaultdict(lambda: sp.Rational(0))
    for powers, coefficient in sp.Poly(polynomial, q, r, u, v).terms():
        grouped[sum(powers[2:])] += abs(coefficient)
    return {degree: Fraction(int(value.p), int(value.q)) for degree, value in grouped.items()}


def fixture_values(side: int, dimension: int) -> tuple[dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]], dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]]]:
    all_sites = sites(side, dimension)
    all_species = species()
    q: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]] = {}
    source: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]] = {}
    for site_index, site in enumerate(all_sites):
        q[site] = {}
        source[site] = {}
        for node_index, node in enumerate(all_species):
            token = site_index * len(all_species) + node_index
            q[site][node] = Fraction((token % 7) - 3)
            source[site][node] = Fraction(((2 * token + 1) % 5) - 2)
    return q, source


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    dimension = int(fixture["dimension"])
    side = int(fixture["side"])
    g = frac(fixture["g"])
    coupling = frac(fixture["lambda"])
    spatial_coupling = frac(fixture["spatial_coupling"])
    degree = 2 * dimension
    q3_degree = len([edge for edge in species_edges() if edge[0] == species()[0]])
    table = shifted_edge_coefficient_table()
    table_oracle = {int(key): frac(value) for key, value in fixture["edge_shift_l1_oracle"].items()}
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001037", manifest["exploration_id"], "EXP-001037", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("Q3 history firewall", manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], False, "scope")
    audit.check("dimension", dimension == 3, dimension, 3, "geometry")
    audit.check("spatial degree bound", degree == 6, degree, 6, "geometry")
    audit.check("Q3 degree", q3_degree == 3, q3_degree, 3, "geometry")
    audit.check("edge coefficient table", table == table_oracle, table, table_oracle, "shifted-force")

    g1 = 3 * g + 3 * table[1] * coupling
    g2 = 3 * g + 3 * table[2] * coupling
    g3 = g + 3 * table[3] * coupling
    audit.check("quadratic source coefficient", g1 == g2, [g1, g2], "equal", "shifted-force")
    audit.check("top source coefficient", g3 == g + 12 * coupling, g3, g + 12 * coupling, "shifted-force")

    q, source = fixture_values(side, dimension)
    q_max = max((abs(value) for row in q.values() for value in row.values()), default=Fraction(0))
    source_max = max((abs(value) for row in source.values() for value in row.values()), default=Fraction(0))
    rows: list[dict[str, Any]] = []
    for site in sites(side, dimension):
        for node in species():
            original = q3_force(q, site, node, g, coupling) + spatial_force(q, site, node, side, spatial_coupling)
            shifted_values = {key: dict(row) for key, row in q.items()}
            shifted_values[site][node] += source[site][node]
            # Shift every source coordinate, as a Weyl/source vector does.
            for source_site in sites(side, dimension):
                for source_node in species():
                    shifted_values[source_site][source_node] = q[source_site][source_node] + source[source_site][source_node]
            shifted = q3_force(shifted_values, site, node, g, coupling) + spatial_force(shifted_values, site, node, side, spatial_coupling)
            actual = abs(shifted - original)
            bound = g1 * q_max**2 * source_max + g2 * q_max * source_max**2 + g3 * source_max**3 + spatial_coupling * degree * source_max
            audit.check(f"full shifted force bound site={site} node={node}", actual <= bound, actual, f"<={bound}", "shifted-force")
            rows.append({"site": site, "node": node, "actual": actual, "bound": bound})

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "fixture_rows": rows,
        "derived": {
            "dimension": dimension,
            "side": side,
            "site_count": side**dimension,
            "species_count": len(species()),
            "spatial_degree_bound": degree,
            "q3_degree": q3_degree,
            "edge_shift_l1_by_source_degree": table,
            "shifted_q3_force_bound_closed": True,
            "actual_q3_history_closed": False,
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
    print(f"PRIMARY ACTUAL-SHIFTED-Q3-FORCE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
