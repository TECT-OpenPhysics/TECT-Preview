#!/usr/bin/env python3
"""Independent exact audit of the finite-Q3 shifted force."""

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
SLUG = "pre-a-cp1-st8-q3lock-actual-shifted-force"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def f(value: str | int) -> Fraction:
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


def nodes() -> tuple[tuple[int, int, int], ...]:
    return tuple(product((0, 1), repeat=3))


def edges() -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    result = []
    for left in nodes():
        for axis in range(3):
            if left[axis] == 0:
                right = tuple(1 if index == axis else left[index] for index in range(3))
                result.append((left, right))
    return tuple(result)


def neighbour_sites(site: tuple[int, ...], side: int) -> tuple[tuple[int, ...], ...]:
    result = []
    for axis in range(len(site)):
        for direction in (-1, 1):
            shifted = list(site)
            shifted[axis] += direction
            if 0 <= shifted[axis] < side:
                result.append(tuple(shifted))
    return tuple(result)


def edge_force(a: Fraction, b: Fraction, lam: Fraction) -> Fraction:
    return lam * (a**3 - f("3/2") * a**2 * b + a * b**2 - f("1/2") * b**3)


def force(field: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]], site: tuple[int, ...], node: tuple[int, int, int], side: int, g: Fraction, lam: Fraction, c: Fraction) -> Fraction:
    value = g * field[site][node] ** 3
    for left, right in edges():
        if left == node:
            value += edge_force(field[site][left], field[site][right], lam)
        elif right == node:
            value += edge_force(field[site][right], field[site][left], lam)
    value -= c * sum((field[other][node] for other in neighbour_sites(site, side)), Fraction(0))
    return value


def make_fields(side: int) -> tuple[dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]], dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]]]:
    q: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]] = {}
    a: dict[tuple[int, ...], dict[tuple[int, int, int], Fraction]] = {}
    for site_index, site in enumerate(product(range(side), repeat=3)):
        q[site] = {}
        a[site] = {}
        for node_index, node in enumerate(nodes()):
            token = site_index * 8 + node_index
            q[site][node] = f((token % 7) - 3)
            a[site][node] = f(((2 * token + 1) % 5) - 2)
    return q, a


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    side = int(fixture["side"])
    g, lam, c = f(fixture["g"]), f(fixture["lambda"]), f(fixture["spatial_coupling"])
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001037", manifest["exploration_id"], "EXP-001037", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("history remains open", manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], False, "scope")
    table = {1: f(12), 2: f(12), 3: f(4)}
    oracle = {int(key): f(value) for key, value in fixture["edge_shift_l1_oracle"].items()}
    audit.check("edge table oracle", table == oracle, table, oracle, "shifted-force")
    q, source = make_fields(side)
    q_max = max((abs(value) for row in q.values() for value in row.values()))
    source_max = max((abs(value) for row in source.values() for value in row.values()))
    g1 = 3 * g + 3 * table[1] * lam
    g2 = 3 * g + 3 * table[2] * lam
    g3 = g + 3 * table[3] * lam
    rows: list[dict[str, Any]] = []
    for site in product(range(side), repeat=3):
        for node in nodes():
            original = force(q, site, node, side, g, lam, c)
            shifted = {key: dict(value) for key, value in q.items()}
            for source_site in shifted:
                for source_node in nodes():
                    shifted[source_site][source_node] += source[source_site][source_node]
            actual = abs(force(shifted, site, node, side, g, lam, c) - original)
            bound = g1 * q_max**2 * source_max + g2 * q_max * source_max**2 + g3 * source_max**3 + c * 6 * source_max
            audit.check(f"independent bound site={site} node={node}", actual <= bound, actual, f"<={bound}", "shifted-force")
            rows.append({"site": site, "node": node, "actual": actual, "bound": bound})
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "fixture_rows": rows,
        "derived": {
            "dimension": 3,
            "side": side,
            "site_count": side**3,
            "species_count": 8,
            "spatial_degree_bound": 6,
            "q3_degree": 3,
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
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ACTUAL-SHIFTED-Q3-FORCE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
