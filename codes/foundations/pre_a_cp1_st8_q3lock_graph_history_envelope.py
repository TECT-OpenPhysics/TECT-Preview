#!/usr/bin/env python3
"""Primary exact audit for a conditional bounded-degree history envelope."""

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
SLUG = "pre-a-cp1-st8-q3lock-graph-history-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fraction(value: str | int) -> Fraction:
    return Fraction(str(value))


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
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


def box_graph(side: int, dimension: int) -> dict[tuple[int, ...], set[tuple[int, ...]]]:
    vertices = list(product(range(side), repeat=dimension))
    graph = {vertex: set() for vertex in vertices}
    for vertex in vertices:
        for axis in range(dimension):
            for direction in (-1, 1):
                shifted = list(vertex)
                shifted[axis] += direction
                neighbour = tuple(shifted)
                if 0 <= shifted[axis] < side:
                    graph[vertex].add(neighbour)
    return graph


def walk_counts(graph: dict[tuple[int, ...], set[tuple[int, ...]]], start: tuple[int, ...], steps: int) -> list[int]:
    current = {start: 1}
    counts = [1]
    for _ in range(steps):
        next_counts: dict[tuple[int, ...], int] = {}
        for vertex, multiplicity in current.items():
            for neighbour in graph[vertex]:
                next_counts[neighbour] = next_counts.get(neighbour, 0) + multiplicity
        current = next_counts
        counts.append(sum(current.values()))
    return counts


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    dimension = int(fixture["dimension"])
    sides = [int(side) for side in fixture["box_sides"]]
    steps = int(fixture["history_steps"])
    degree_bound = 2 * dimension
    C = fraction(fixture["C"])
    J = fraction(fixture["J"])
    delta = fraction(fixture["delta"])
    orientations = int(fixture["orientation_count"])
    branch_factor = 1 + (C + orientations * J) * delta
    iterated_factor = branch_factor**steps
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001036", manifest["exploration_id"], "EXP-001036", "provenance")
    audit.check("task identity", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("Q3 recurrence firewall", manifest["scope"]["actual_q3_recurrence_closed"] is False, manifest["scope"], False, "scope")
    audit.check("dimension", dimension == 3, dimension, 3, "graph")
    audit.check("degree bound", degree_bound == 6, degree_bound, 6, "graph")
    audit.check("two orientations", orientations == 2, orientations, 2, "history")
    audit.check("positive history steps", steps > 0, steps, ">0", "history")

    shape_rows: list[dict[str, Any]] = []
    for side in sides:
        graph = box_graph(side, dimension)
        degrees = [len(neighbours) for neighbours in graph.values()]
        audit.check(f"degree bound side={side}", max(degrees, default=0) <= degree_bound, max(degrees, default=0), f"<={degree_bound}", "graph")
        reverse_graph = {vertex: set() for vertex in graph}
        for vertex, neighbours in graph.items():
            for neighbour in neighbours:
                reverse_graph[neighbour].add(vertex)
        max_walks: list[int] = []
        max_reverse_walks: list[int] = []
        symmetry_rows = 0
        for vertex in graph:
            forward = walk_counts(graph, vertex, steps)
            reverse = walk_counts(reverse_graph, vertex, steps)
            for order, count in enumerate(forward):
                audit.check(f"path bound side={side} vertex={vertex} order={order}", count <= degree_bound**order, count, f"<={degree_bound**order}", "paths")
                audit.check(f"adjoint path bound side={side} vertex={vertex} order={order}", reverse[order] <= degree_bound**order, reverse[order], f"<={degree_bound**order}", "paths")
                audit.check(f"undirected orientation symmetry side={side} vertex={vertex} order={order}", count == reverse[order], [count, reverse[order]], "equal", "paths")
                symmetry_rows += 1
            max_walks.extend(forward)
            max_reverse_walks.extend(reverse)
        shape_rows.append({
            "side": side,
            "site_count": len(graph),
            "maximum_degree": max(degrees, default=0),
            "maximum_walk_count_by_order": [max((walk_counts(graph, vertex, steps)[order] for vertex in graph), default=0) for order in range(steps + 1)],
            "maximum_reverse_walk_count_by_order": [max((walk_counts(reverse_graph, vertex, steps)[order] for vertex in graph), default=0) for order in range(steps + 1)],
            "symmetry_checks": symmetry_rows,
        })

    mass = Fraction(1)
    branch_rows: list[dict[str, Any]] = []
    for step in range(1, steps + 1):
        onsite = (1 + C * delta) * mass
        forward = J * delta * mass
        reverse = J * delta * mass
        after = onsite + forward + reverse
        audit.check(f"two-orientation branch step={step}", after == branch_factor * mass, after, branch_factor * mass, "history")
        audit.check(f"adjoint branch symmetry step={step}", forward == reverse, [forward, reverse], "equal", "history")
        branch_rows.append({"step": step, "before": mass, "onsite": onsite, "forward": forward, "reverse": reverse, "after": after})
        mass = after
    audit.check("iterated branch envelope", mass == iterated_factor, mass, iterated_factor, "history")
    audit.check("volume-independent path expression", "independent of site_count" in manifest["model"]["path_bound"], manifest["model"]["path_bound"], "declares independence", "volume")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "shape_rows": shape_rows,
        "branch_rows": branch_rows,
        "derived": {
            "dimension": dimension,
            "degree_bound": degree_bound,
            "box_sides": sides,
            "history_steps": steps,
            "orientation_count": orientations,
            "branch_factor": branch_factor,
            "iterated_factor": iterated_factor,
            "bounded_degree_path_envelope_closed": True,
            "reverse_orientation_path_envelope_closed": True,
            "conditional_two_orientation_history_closed": True,
            "actual_q3_recurrence_closed": False,
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
    print(f"PRIMARY GRAPH-HISTORY-ENVELOPE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
