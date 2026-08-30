#!/usr/bin/env python3
"""Independent mixed-radix coordinate audit for R-443."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-arbitrary-box-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_arbitrary_box/independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def decode(index: int, sides: tuple[int, ...]) -> tuple[int, ...]:
    coordinates: list[int] = []
    for side in sides:
        coordinates.append(index % side)
        index //= side
    return tuple(coordinates)


def index_of(vertex: tuple[int, ...], sides: tuple[int, ...]) -> int:
    stride, result = 1, 0
    for coordinate, side in zip(vertex, sides):
        result += coordinate * stride
        stride *= side
    return result


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_contract"]
    dimension, modulus = int(fixture["dimension"]), int(fixture["parity_modulus"])
    side_min, side_max = int(fixture["side_min"]), int(fixture["side_max"])
    colours = {(axis, parity) for axis in range(dimension) for parity in range(modulus)}
    check_count = 0
    check_samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        nonlocal check_count
        check_count += 1
        if len(check_samples) < 24:
            check_samples.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]] == ["R-443", "EXP-001288", False, "ARBITRARY_BOX_MATCHING_THEOREM_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-443/EXP-001288/false/audited", "provenance")
    check("contract", [dimension, modulus, side_min, side_max] == [3, 2, 2, 8], [dimension, modulus, side_min, side_max], "3D parity 2 sides 2..8", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for key in ("arbitrary_box_edge_colouring_closed", "weighted_operator_form_closed", "boundary_commutator_decay_closed", "history_tail_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        expected = key == "arbitrary_box_edge_colouring_closed"
        check(f"scope firewall {key}", manifest["scope"][key] is expected, manifest["scope"][key], expected, "scope")
    boxes = list(product(range(side_min, side_max + 1), repeat=dimension))
    check("box coverage", len(boxes) == (side_max - side_min + 1) ** dimension, len(boxes), (side_max - side_min + 1) ** dimension, "coverage")
    check("layer count", len(colours) == 6, len(colours), 6, "graph")
    summaries: list[dict[str, Any]] = []
    total_vertices = total_edges = total_empty_layers = 0
    maximum_degree = maximum_incidence = 0
    for box_index, sides in enumerate(boxes):
        vertex_count = math.prod(sides)
        vertices = [decode(index, sides) for index in range(vertex_count)]
        edges: list[tuple[int, int, int, int]] = []
        for lower_index, lower in enumerate(vertices):
            for axis, side in enumerate(sides):
                if lower[axis] + 1 < side:
                    upper = list(lower)
                    upper[axis] += 1
                    edges.append((lower_index, index_of(tuple(upper), sides), axis, lower[axis] % modulus))
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1 :]) for axis in range(dimension))
        check(f"box {box_index} vertices", len(vertices) == vertex_count, len(vertices), vertex_count, "graph")
        check(f"box {box_index} index roundtrip", all(index_of(decode(index, sides), sides) == index for index in range(vertex_count)), vertex_count, vertex_count, "graph")
        check(f"box {box_index} edges", len(edges) == expected_edges, len(edges), expected_edges, "graph")
        layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {colour: [] for colour in colours}
        for edge in edges:
            layers[(edge[2], edge[3])].append(edge)
        check(f"box {box_index} keys", set(layers) == colours, sorted(layers), sorted(colours), "graph")
        degrees = [0] * vertex_count
        incidence_max: dict[str, int] = {}
        for colour, layer in sorted(layers.items()):
            counts = [0] * vertex_count
            for left, right, axis, parity in layer:
                if (axis, parity) != colour:
                    raise AssertionError(f"colour mismatch in box {box_index}")
                counts[left] += 1; counts[right] += 1; degrees[left] += 1; degrees[right] += 1
            maximum = max(counts, default=0)
            incidence_max[str(colour)] = maximum
            maximum_incidence = max(maximum_incidence, maximum)
            check(f"box {box_index} matching {colour}", maximum <= 1, maximum, 1, "matching")
            total_empty_layers += int(not layer)
        degree = max(degrees, default=0)
        maximum_degree = max(maximum_degree, degree)
        check(f"box {box_index} degree", degree <= 6, degree, 6, "graph")
        for vertex in vertices:
            for axis, side in enumerate(sides):
                candidates = ([vertex[axis] % modulus] if vertex[axis] + 1 < side else []) + ([(vertex[axis] - 1) % modulus] if vertex[axis] > 0 else [])
                check(f"box {box_index} local axis {axis}", all(candidates.count(parity) <= 1 for parity in range(modulus)), candidates, "at most one per parity", "matching")
        summaries.append({"sides": list(sides), "vertices": vertex_count, "edges": len(edges), "empty_layer_count": sum(int(not layer) for layer in layers.values()), "incidence_max": incidence_max})
        total_vertices += vertex_count; total_edges += len(edges)
    check("all matching layers", maximum_incidence <= 1, maximum_incidence, 1, "matching")
    check("general Lean lemma flag", manifest["scope"]["general_local_incidence_lemma_lean_checked"] is True, manifest["scope"]["general_local_incidence_lemma_lean_checked"], True, "Lean")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r443-independent/1.0", "manifest": MANIFEST.relative_to(ROOT).as_posix(), "result_id": "R-443", "exploration_id": "EXP-001288", "claim_id": manifest["claim_ids"][0], "run_kind": "independent", "verdict": "INDEPENDENT_ARBITRARY_BOX_MATCHING_CONTROL", "passed": check_count, "assertion_count": check_count, "assertions": check_samples, "assertion_samples_truncated": check_count > len(check_samples),
        "derived": {"dimension": dimension, "parity_modulus": modulus, "box_count": len(boxes), "total_vertices": total_vertices, "total_edges": total_edges, "total_empty_layers": total_empty_layers, "maximum_degree": maximum_degree, "maximum_incidence": maximum_incidence, "layer_count": len(colours), "boxes": summaries, "edge_count_formula_checked": True, "matching_property_checked": True, "general_local_incidence_lemma_lean_checked": True, "arbitrary_box_edge_colouring_closed": True, "weighted_operator_form_closed": False, "boundary_commutator_decay_closed": False, "history_tail_closed": False, "exhaustion_cauchy_closed": False, "common_core_closed": False, "common_alpha_closed": False, "pre_a_closed": False, "sector_a_closed": False},
        "scope": {"independent_coordinate_enumeration": True, "claim_bearing": False, "operator_or_physical_promotion": False}, "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-443 INDEPENDENT {payload['verdict']} {check_count}/{check_count} boxes={len(boxes)} vertices={total_vertices} edges={total_edges}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_ARBITRARY_BOX_MATCHING_CONTROL" and payload["derived"]["maximum_incidence"] <= 1
        print("R-443 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
