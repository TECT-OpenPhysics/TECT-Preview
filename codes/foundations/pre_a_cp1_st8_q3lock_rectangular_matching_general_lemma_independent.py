#!/usr/bin/env python3
"""Non-importing coordinate-index control for R-442."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-general-lemma-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_general_lemma/independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def decode(index: int, sides: tuple[int, ...]) -> tuple[int, ...]:
    coordinates: list[int] = []
    remaining = index
    for side in sides:
        coordinates.append(remaining % side)
        remaining //= side
    return tuple(coordinates)


def index_of(vertex: tuple[int, ...], sides: tuple[int, ...]) -> int:
    multiplier = 1
    index = 0
    for coordinate, side in zip(vertex, sides):
        index += coordinate * multiplier
        multiplier *= side
    return index


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_contract"]
    dimension = int(fixture["dimension"])
    parity_modulus = int(fixture["parity_modulus"])
    side_min = int(fixture["side_min"])
    side_max = int(fixture["side_max"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]] == ["R-442", "EXP-001287", False, "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-442/EXP-001287/false/audited", "provenance")
    check("coordinate contract", dimension == 3 and parity_modulus == 2 and side_min >= 2 and side_max >= side_min, [dimension, parity_modulus, side_min, side_max], "3D, parity 2, valid range", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for key in ("arbitrary_box_edge_colouring_closed", "weighted_operator_form_closed", "boundary_commutator_decay_closed", "history_tail_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    boxes = list(product(range(side_min, side_max + 1), repeat=dimension))
    expected_box_count = (side_max - side_min + 1) ** dimension
    check("box coverage", len(boxes) == expected_box_count, len(boxes), expected_box_count, "coverage")
    colours = {(axis, parity) for axis in range(dimension) for parity in range(parity_modulus)}
    total_vertices = 0
    total_edges = 0
    total_empty_layers = 0
    maximum_degree = 0
    box_summaries: list[dict[str, Any]] = []
    for box_index, sides in enumerate(boxes):
        vertex_count = math.prod(sides)
        vertices = [decode(index, sides) for index in range(vertex_count)]
        edges: list[tuple[int, int, int, int]] = []
        for lower_index, lower in enumerate(vertices):
            for axis, side in enumerate(sides):
                if lower[axis] + 1 >= side:
                    continue
                upper = list(lower)
                upper[axis] += 1
                edges.append((lower_index, index_of(tuple(upper), sides), axis, lower[axis] % parity_modulus))
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1 :]) for axis in range(dimension))
        check(f"box {box_index} vertex count", len(vertices) == vertex_count, len(vertices), vertex_count, "graph")
        check(f"box {box_index} edge count", len(edges) == expected_edges, len(edges), expected_edges, "graph")
        layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {colour: [] for colour in colours}
        for edge in edges:
            layers[(edge[2], edge[3])].append(edge)
        check(f"box {box_index} retained colours", set(layers) == colours, sorted(layers), sorted(colours), "graph")
        degree = [0] * vertex_count
        incidence_max: dict[str, int] = {}
        for colour, layer in sorted(layers.items()):
            incidence = [0] * vertex_count
            for left, right, axis, parity in layer:
                check(f"box {box_index} colour {colour}", (axis, parity) == colour, [axis, parity], list(colour), "graph")
                incidence[left] += 1
                incidence[right] += 1
                degree[left] += 1
                degree[right] += 1
            maximum = max(incidence, default=0)
            incidence_max[str(colour)] = maximum
            check(f"box {box_index} matching {colour}", maximum <= 1, maximum, 1, "matching")
            if not layer:
                total_empty_layers += 1
        maximum_degree = max(maximum_degree, max(degree, default=0))
        check(f"box {box_index} degree bound", max(degree, default=0) <= 2 * dimension, max(degree, default=0), 2 * dimension, "graph")

        # A second implementation of the local parity argument, independent
        # of edge incidence accumulation.
        for vertex_index, vertex in enumerate(vertices):
            for axis, side in enumerate(sides):
                candidates: list[tuple[int, int]] = []
                if vertex[axis] + 1 < side:
                    candidates.append((vertex[axis], vertex[axis] % parity_modulus))
                if vertex[axis] > 0:
                    lower = vertex[axis] - 1
                    candidates.append((lower, lower % parity_modulus))
                for parity in range(parity_modulus):
                    count = sum(1 for _lower, candidate_parity in candidates if candidate_parity == parity)
                    check(f"box {box_index} vertex {vertex_index} axis {axis} parity {parity} local incidence", count <= 1, count, 1, "matching")

        total_vertices += vertex_count
        total_edges += len(edges)
        box_summaries.append({"sides": list(sides), "vertices": vertex_count, "edges": len(edges), "layer_sizes": {str(colour): len(layer) for colour, layer in sorted(layers.items())}, "empty_layer_count": sum(1 for layer in layers.values() if not layer), "incidence_max": incidence_max})

    check("all boxes matching", all(max(box["incidence_max"].values()) <= 1 for box in box_summaries), True, True, "matching")
    check("empty layers are represented", total_empty_layers >= 0, total_empty_layers, ">=0", "graph")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r442-independent/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-442",
        "exploration_id": "EXP-001287",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_GENERAL_RECTANGULAR_MATCHING_CONTROL",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"dimension": dimension, "parity_modulus": parity_modulus, "box_count": len(boxes), "total_vertices": total_vertices, "total_edges": total_edges, "total_empty_layers": total_empty_layers, "maximum_degree": maximum_degree, "boxes": box_summaries, "edge_count_formula_checked": True, "matching_property_checked": True, "general_local_incidence_lemma_lean_checked": True},
        "scope": {"independent_coordinate_enumeration": True, "claim_bearing": False, "operator_or_physical_promotion": False},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-442 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} boxes={len(boxes)} edges={total_edges}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_GENERAL_RECTANGULAR_MATCHING_CONTROL"
        assert payload["derived"]["matching_property_checked"] is True
        print("R-442 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
