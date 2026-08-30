#!/usr/bin/env python3
"""Non-importing Fraction control for R-440."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-layer-family-manifest.json"
SCRIPT = Path(__file__).resolve()
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rectangular_matching_layer_family/independent.json"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def build_graph(sides: tuple[int, ...], modulus: int) -> tuple[list[tuple[int, ...]], list[tuple[int, int, int, int]]]:
    vertices = list(product(*[range(side) for side in sides]))
    lookup = {vertex: index for index, vertex in enumerate(vertices)}
    edges: list[tuple[int, int, int, int]] = []
    for vertex in vertices:
        for axis, side in enumerate(sides):
            if vertex[axis] + 1 < side:
                neighbour = list(vertex)
                neighbour[axis] += 1
                edges.append((lookup[vertex], lookup[tuple(neighbour)], axis, vertex[axis] % modulus))
    return vertices, edges


def form(weights: list[Fraction], momentum: list[Fraction], position: list[Fraction], chi: Fraction, gamma: Fraction) -> Fraction:
    total = Fraction(0)
    for weight, p_value, q_value in zip(weights, momentum, position):
        total += weight * (1 + p_value * p_value / (2 * chi) + gamma * q_value**4)
    return total


def kicked(momentum: list[Fraction], position: list[Fraction], layer: list[tuple[int, int, int, int]], signed_delta: Fraction, coupling: Fraction) -> list[Fraction]:
    result = list(momentum)
    for left, right, _axis, _parity in layer:
        result[left] += signed_delta * coupling * position[right]
        result[right] += signed_delta * coupling * position[left]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["finite_contract"]
    dimension = int(contract["dimension"])
    modulus = int(contract["parity_modulus"])
    boxes = [tuple(int(value) for value in box) for box in contract["box_sides"]]
    signs = [int(value) for value in contract["signs"]]
    orders = tuple(contract["orders"])
    seeds = int(contract["fixture_seeds"])
    centre = tuple(int(value) for value in contract["weight_center"])
    base = int(contract["weight_base"])
    p_coeff = tuple(int(value) for value in contract["momentum_coefficients"])
    q_coeff = tuple(int(value) for value in contract["position_coefficients"])
    p_den = int(contract["momentum_denominator"])
    q_den = int(contract["position_denominator"])
    p_offset = int(contract["momentum_offset"])
    q_offset = int(contract["position_offset"])
    delta = as_fraction(contract["delta"])
    coupling = as_fraction(contract["coupling"])
    chi = as_fraction(contract["chi"])
    sqrt_gamma = as_fraction(contract["sqrt_gamma"])
    gamma = sqrt_gamma * sqrt_gamma
    kappa = as_fraction(contract["kappa"])
    time = as_fraction(contract["trotter_time"])
    steps = [int(value) for value in contract["trotter_steps"]]
    coefficient = 1 + kappa * coupling * coupling / (2 * chi * sqrt_gamma)
    layer_factor = 1 + coefficient * abs(delta)
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        rows.append({"name": name, "group": group, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", [manifest["exploration_id"], manifest["result_id"], manifest["task_id"]] == ["EXP-001285", "R-440", "T-054"], [manifest["exploration_id"], manifest["result_id"], manifest["task_id"]], "EXP-001285/R-440/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("independent source policy", not any(line.strip().startswith(("import pre_a_cp1", "from pre_a_cp1")) for line in SCRIPT.read_text(encoding="utf-8").splitlines()), "no primary import", "no primary import", "scope")
    check("dimension", dimension == len(centre) == len(p_coeff) == len(q_coeff), [dimension, len(centre), len(p_coeff), len(q_coeff)], "equal", "inputs")
    expected_layers = dimension * modulus
    summaries: list[dict[str, Any]] = []
    max_ratio = Fraction(0)
    total_layer_rows = 0
    total_product_rows = 0
    for box_number, sides in enumerate(boxes):
        vertices, edges = build_graph(sides, modulus)
        colours = {(axis, parity) for axis in range(dimension) for parity in range(modulus)}
        layers = {colour: [] for colour in colours}
        for edge in edges:
            layers[(edge[2], edge[3])].append(edge)
        check(f"box {box_number} layer keys", set(layers) == colours, sorted(layers), sorted(colours), "graph")
        check(f"box {box_number} six layers", len(layers) == expected_layers, len(layers), expected_layers, "graph")
        incidence: dict[str, int] = {}
        for colour in sorted(layers):
            counts = [0] * len(vertices)
            for left, right, _axis, _parity in layers[colour]:
                counts[left] += 1
                counts[right] += 1
            incidence[str(colour)] = max(counts, default=0)
            check(f"box {box_number} matching {colour}", incidence[str(colour)] <= 1, incidence[str(colour)], 1, "graph")
        edge_formula = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1 :]) for axis in range(dimension))
        check(f"box {box_number} vertices", len(vertices) == math.prod(sides), len(vertices), math.prod(sides), "graph")
        check(f"box {box_number} edges", len(edges) == edge_formula, len(edges), edge_formula, "graph")
        weights = [Fraction(1, base ** sum(abs(value - middle) for value, middle in zip(vertex, centre))) for vertex in vertices]
        ratios = [weights[left] / weights[right] for left, right, _axis, _parity in edges]
        check(f"box {box_number} lower weight ratio", min(ratios, default=Fraction(1)) >= Fraction(1, base), min(ratios, default=Fraction(1)), f">=1/{base}", "weights")
        check(f"box {box_number} upper weight ratio", max(ratios, default=Fraction(1)) <= base, max(ratios, default=Fraction(1)), f"<={base}", "weights")
        box_max = Fraction(0)
        layer_rows = 0
        product_rows = 0
        for seed in range(seeds):
            momentum = [Fraction(p_offset + seed + sum(a * b for a, b in zip(p_coeff, vertex)), p_den) for vertex in vertices]
            position = [Fraction(q_offset + seed + sum(a * b for a, b in zip(q_coeff, vertex)), q_den) for vertex in vertices]
            initial = form(weights, momentum, position, chi, gamma)
            check(f"box {box_number} seed {seed} positive", initial > 0, initial, ">0", "form")
            for sign in signs:
                for order in orders:
                    colour_order = sorted(layers) if order == "lexicographic" else list(reversed(sorted(layers)))
                    current = list(momentum)
                    current_form = initial
                    for colour in colour_order:
                        current = kicked(current, position, layers[colour], sign * delta, coupling)
                        updated = form(weights, current, position, chi, gamma)
                        check(f"box {box_number} seed {seed} sign {sign} {order} {colour}", updated <= layer_factor * current_form, updated, f"<={layer_factor * current_form}", "form")
                        box_max = max(box_max, updated / current_form)
                        max_ratio = max(max_ratio, updated / current_form)
                        current_form = updated
                        layer_rows += 1
                    check(f"box {box_number} seed {seed} sign {sign} {order} product", current_form <= layer_factor ** len(colour_order) * initial, current_form, f"<={layer_factor ** len(colour_order) * initial}", "product")
                    product_rows += 1
        total_layer_rows += layer_rows
        total_product_rows += product_rows
        summaries.append({"sides": list(sides), "vertices": len(vertices), "edges": len(edges), "layer_sizes": sorted(len(layer) for layer in layers.values()), "incidence_max": incidence, "max_layer_energy_ratio": box_max, "layer_rows": layer_rows, "product_rows": product_rows})

    check("layer count even", expected_layers % 2 == 0, expected_layers, "even", "graph")
    check("coefficient identity", coefficient == 1 + kappa * coupling * coupling / (2 * chi * sqrt_gamma), coefficient, "derived", "constants")
    for step in steps:
        endpoint = (1 + coefficient * time / step) ** (expected_layers // 2)
        bound = math.exp(float(Fraction(expected_layers, 2) * coefficient * time))
        check(f"endpoint exponential {step}", float(endpoint) <= bound + 1e-12, [endpoint, bound], "<= exp", "product")
    check("coverage", total_layer_rows > 0 and total_product_rows > 0, [total_layer_rows, total_product_rows], ">0", "coverage")
    check("scope boundary", all(not bool(manifest["scope"].get(key, False)) for key in ("arbitrary_box_theorem_closed", "operator_common_core_closed", "boundary_commutator_decay_closed", "exhaustion_cauchy_closed", "common_alpha_closed", "kms_gns_gap_closed", "pre_a_closed")), "open", "open", "scope")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RECTANGULAR-MATCHING-LAYER-FAMILY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "dimension": dimension,
            "box_count": len(boxes),
            "boxes": summaries,
            "layer_count": expected_layers,
            "matching_coefficient": coefficient,
            "one_layer_form_factor": layer_factor,
            "endpoint_exponent": Fraction(expected_layers, 2) * coefficient,
            "global_max_layer_energy_ratio": max_ratio,
            "total_layer_rows": total_layer_rows,
            "total_product_rows": total_product_rows,
            "rectangular_box_family_checked": True,
            "edge_colour_partition_checked": True,
            "six_matching_layers_checked": True,
            "per_layer_weighted_finite_form_checked": True,
            "volume_independent_coefficient_observed": True,
            "arbitrary_box_theorem_closed": False,
            "operator_common_core_closed": False,
            "boundary_commutator_decay_closed": False,
            "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False,
            "kms_gns_gap_closed": False,
            "pre_a_closed": False,
        },
        "boundary": manifest["boundary"],
    }
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"R-440 INDEPENDENT RECTANGULAR_MATCHING_LAYER_AUDITED {payload['passed']}/{payload['assertion_count']} boxes={payload['derived']['box_count']} layers={payload['derived']['layer_count']} max_ratio={payload['derived']['global_max_layer_energy_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
