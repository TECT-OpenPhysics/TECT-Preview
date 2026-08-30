#!/usr/bin/env python3
"""Exact all-box audit for the R-442 rectangular axis-parity matching lemma.

The executable lane enumerates every ordered side triple in the declared
finite range.  The general local incidence proposition is proved separately
in Lean; this script does not treat the finite sweep as an unbounded operator
or physical theorem.
"""

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


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-general-lemma-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rectangular_matching_general_lemma/primary.json"


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


def graph(sides: tuple[int, ...], parity_modulus: int) -> tuple[list[tuple[int, ...]], list[tuple[int, int, int, int]]]:
    vertices = list(product(*[range(side) for side in sides]))
    index = {vertex: number for number, vertex in enumerate(vertices)}
    edges: list[tuple[int, int, int, int]] = []
    for lower in vertices:
        for axis, side in enumerate(sides):
            if lower[axis] + 1 >= side:
                continue
            upper = list(lower)
            upper[axis] += 1
            edges.append((index[lower], index[tuple(upper)], axis, lower[axis] % parity_modulus))
    return vertices, edges


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_contract"]
    dimension = int(fixture["dimension"])
    parity_modulus = int(fixture["parity_modulus"])
    side_min = int(fixture["side_min"])
    side_max = int(fixture["side_max"])
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-rectangular-matching-general-lemma/1.0", manifest["schema"], ".../1.0", "provenance")
    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]] == ["R-442", "EXP-001287", "T-054", False, "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]], "R-442/EXP-001287/T-054/false/audited", "provenance")
    check("dimension and parity", dimension == 3 and parity_modulus == 2, [dimension, parity_modulus], [3, 2], "contract")
    check("side range", side_min >= 2 and side_max >= side_min, [side_min, side_max], "2 <= min <= max", "contract")
    check("edge colour rule", fixture["lower_endpoint_colour"] == "(axis, lower_coordinate[axis] mod parity_modulus)", fixture["lower_endpoint_colour"], "declared lower-endpoint rule", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for key in ("arbitrary_box_edge_colouring_closed", "weighted_operator_form_closed", "boundary_commutator_decay_closed", "history_tail_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    all_sides = list(product(range(side_min, side_max + 1), repeat=dimension))
    expected_box_count = (side_max - side_min + 1) ** dimension
    check("complete declared box family", len(all_sides) == expected_box_count, len(all_sides), expected_box_count, "coverage")
    expected_colours = {(axis, parity) for axis in range(dimension) for parity in range(parity_modulus)}
    expected_layer_count = dimension * parity_modulus
    check("derived colour count", len(expected_colours) == expected_layer_count, len(expected_colours), expected_layer_count, "graph")

    box_summaries: list[dict[str, Any]] = []
    total_vertices = 0
    total_edges = 0
    total_empty_layers = 0
    maximum_degree = 0
    maximum_layer_size = 0
    for box_index, sides in enumerate(all_sides):
        vertices, edges = graph(sides, parity_modulus)
        layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {colour: [] for colour in expected_colours}
        for edge in edges:
            layers[(edge[2], edge[3])].append(edge)
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1 :]) for axis in range(dimension))
        check(f"box {box_index} sides", len(sides) == dimension and all(side >= side_min for side in sides), sides, f"{dimension} sides >= {side_min}", "graph")
        check(f"box {box_index} vertex count", len(vertices) == math.prod(sides), len(vertices), math.prod(sides), "graph")
        check(f"box {box_index} edge count", len(edges) == expected_edges, len(edges), expected_edges, "graph")
        check(f"box {box_index} layer keys", set(layers) == expected_colours, sorted(layers), sorted(expected_colours), "graph")

        degrees = [0] * len(vertices)
        incidence_max: dict[str, int] = {}
        for colour, layer in sorted(layers.items()):
            counts = [0] * len(vertices)
            for left, right, axis, parity in layer:
                check(f"box {box_index} edge colour {colour}", (axis, parity) == colour, [axis, parity], list(colour), "graph")
                counts[left] += 1
                counts[right] += 1
                degrees[left] += 1
                degrees[right] += 1
            maximum = max(counts, default=0)
            incidence_max[str(colour)] = maximum
            check(f"box {box_index} matching {colour}", maximum <= 1, maximum, 1, "matching")
            maximum_layer_size = max(maximum_layer_size, len(layer))
            if not layer:
                total_empty_layers += 1
        maximum_degree = max(maximum_degree, max(degrees, default=0))
        check(f"box {box_index} degree bound", max(degrees, default=0) <= 2 * dimension, max(degrees, default=0), 2 * dimension, "graph")

        # Directly enumerate the at-most-two incident lower endpoints at each
        # vertex.  Their parity differs, so a single colour cannot be repeated.
        for vertex_index, vertex in enumerate(vertices):
            for axis, side in enumerate(sides):
                candidates: list[tuple[int, int]] = []
                if vertex[axis] + 1 < side:
                    candidates.append((vertex[axis], vertex[axis] % parity_modulus))
                if vertex[axis] > 0:
                    lower = vertex[axis] - 1
                    candidates.append((lower, lower % parity_modulus))
                for colour in range(parity_modulus):
                    same = [item for item in candidates if item[1] == colour]
                    check(f"box {box_index} vertex {vertex_index} axis {axis} parity {colour} local incidence", len(same) <= 1, len(same), 1, "matching")

        total_vertices += len(vertices)
        total_edges += len(edges)
        box_summaries.append({
            "sides": list(sides),
            "vertices": len(vertices),
            "edges": len(edges),
            "layer_sizes": {str(colour): len(layer) for colour, layer in sorted(layers.items())},
            "empty_layer_count": sum(1 for layer in layers.values() if not layer),
            "incidence_max": incidence_max,
        })

    check("all matching layers", all(max(value for value in box["incidence_max"].values()) <= 1 for box in box_summaries), True, True, "matching")
    check("general local lemma flag", manifest["scope"]["general_local_incidence_lemma_lean_checked"] is True, manifest["scope"]["general_local_incidence_lemma_lean_checked"], True, "Lean")
    check("empty slots retained", manifest["scope"]["layer_keys_retained_including_empty"] is True, manifest["scope"]["layer_keys_retained_including_empty"], True, "graph")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r442-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-442",
        "exploration_id": "EXP-001287",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {
            "dimension": dimension,
            "parity_modulus": parity_modulus,
            "box_count": len(all_sides),
            "expected_box_count": expected_box_count,
            "layer_count": expected_layer_count,
            "total_vertices": total_vertices,
            "total_edges": total_edges,
            "total_empty_layers": total_empty_layers,
            "maximum_degree": maximum_degree,
            "maximum_layer_size": maximum_layer_size,
            "boxes": box_summaries,
            "edge_count_formula_checked": True,
            "matching_property_checked": True,
            "general_local_incidence_lemma_lean_checked": True,
            "weighted_operator_form_closed": False,
            "boundary_commutator_decay_closed": False,
            "history_tail_closed": False,
            "common_core_closed": False,
            "pre_a_closed": False,
        },
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-442 PRIMARY {payload['verdict']} {len(assertions)}/{len(assertions)} boxes={len(all_sides)} layers={expected_layer_count} edges={total_edges}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "GENERAL_RECTANGULAR_MATCHING_LEMMA_AUDITED"
        assert payload["derived"]["matching_property_checked"] is True
        assert payload["derived"]["general_local_incidence_lemma_lean_checked"] is True
        print("R-442 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
