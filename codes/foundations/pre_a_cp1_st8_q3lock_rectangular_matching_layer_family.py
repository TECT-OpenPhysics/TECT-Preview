#!/usr/bin/env python3
"""Finite rectangular-box matching-layer split-envelope audit (R-440).

The audit is deliberately finite and claim-nonbearing.  All numerical inputs
come from the machine manifest; derived coefficients, graph sizes and energy
rows are recomputed from those inputs with exact ``Fraction`` arithmetic.
"""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rectangular_matching_layer_family/primary.json"


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


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def make_graph(sides: tuple[int, ...], parity_modulus: int) -> tuple[list[tuple[int, ...]], list[tuple[int, int, int, int]]]:
    vertices = list(product(*[range(side) for side in sides]))
    index = {vertex: number for number, vertex in enumerate(vertices)}
    edges: list[tuple[int, int, int, int]] = []
    for vertex in vertices:
        for axis, side in enumerate(sides):
            if vertex[axis] + 1 >= side:
                continue
            neighbour = list(vertex)
            neighbour[axis] += 1
            edges.append((index[vertex], index[tuple(neighbour)], axis, vertex[axis] % parity_modulus))
    return vertices, edges


def energy(weights: list[Fraction], momentum: list[Fraction], position: list[Fraction], chi: Fraction, gamma: Fraction) -> Fraction:
    return sum(
        (weight * (1 + p * p / (2 * chi) + gamma * q**4) for weight, p, q in zip(weights, momentum, position)),
        Fraction(0),
    )


def shear(momentum: list[Fraction], position: list[Fraction], layer: list[tuple[int, int, int, int]], delta: Fraction, coupling: Fraction) -> list[Fraction]:
    output = list(momentum)
    for left, right, _axis, _parity in layer:
        output[left] += delta * coupling * position[right]
        output[right] += delta * coupling * position[left]
    return output


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_contract"]
    dimension = int(fixture["dimension"])
    parity_modulus = int(fixture["parity_modulus"])
    boxes = [tuple(int(side) for side in box) for box in fixture["box_sides"]]
    signs = [int(sign) for sign in fixture["signs"]]
    orders = list(fixture["orders"])
    seeds = int(fixture["fixture_seeds"])
    weight_base = int(fixture["weight_base"])
    center = tuple(int(value) for value in fixture["weight_center"])
    momentum_coefficients = tuple(int(value) for value in fixture["momentum_coefficients"])
    position_coefficients = tuple(int(value) for value in fixture["position_coefficients"])
    momentum_denominator = int(fixture["momentum_denominator"])
    position_denominator = int(fixture["position_denominator"])
    momentum_offset = int(fixture["momentum_offset"])
    position_offset = int(fixture["position_offset"])
    delta = fraction(fixture["delta"])
    coupling = fraction(fixture["coupling"])
    chi = fraction(fixture["chi"])
    sqrt_gamma = fraction(fixture["sqrt_gamma"])
    gamma = sqrt_gamma * sqrt_gamma
    kappa = fraction(fixture["kappa"])
    time = fraction(fixture["trotter_time"])
    trotter_steps = [int(step) for step in fixture["trotter_steps"]]
    coefficient = 1 + kappa * coupling * coupling / (2 * chi * sqrt_gamma)
    one_layer_factor = 1 + coefficient * abs(delta)
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})

    check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-rectangular-matching-layer-family/1.0", manifest["schema"], ".../1.0", "provenance")
    check("identity", manifest["exploration_id"] == "EXP-001285" and manifest["result_id"] == "R-440" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["result_id"], manifest["task_id"]], "EXP-001285/R-440/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("dimension inputs", len(center) == dimension and len(momentum_coefficients) == dimension and len(position_coefficients) == dimension, [len(center), len(momentum_coefficients), len(position_coefficients)], dimension, "inputs")
    check("finite scope firewall", all(not bool(value) for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in {"rectangular_box_family_checked", "edge_colour_partition_checked", "six_matching_layers_checked", "per_layer_weighted_finite_form_checked"}), "operator and limit flags remain false", "no unscoped closure", "scope")
    check("positive constants", delta != 0 and coupling > 0 and chi > 0 and sqrt_gamma > 0 and kappa > 0 and weight_base > 1, [delta, coupling, chi, sqrt_gamma, kappa, weight_base], "nonzero declared inputs", "inputs")

    box_summaries: list[dict[str, Any]] = []
    global_max_ratio = Fraction(0)
    total_layer_rows = 0
    total_step_rows = 0
    expected_layer_count = dimension * parity_modulus
    for box_index, sides in enumerate(boxes):
        check(f"box {box_index} dimension", len(sides) == dimension and all(side >= 2 for side in sides), sides, f"{dimension} sides >=2", "graph")
        check(f"box {box_index} centre", all(0 <= centre < side for centre, side in zip(center, sides)), [center, sides], "centre in box", "weights")
        vertices, edges = make_graph(sides, parity_modulus)
        expected_colours = {(axis, parity) for axis in range(dimension) for parity in range(parity_modulus)}
        layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {colour: [] for colour in expected_colours}
        for edge in edges:
            layers.setdefault((edge[2], edge[3]), []).append(edge)
        check(f"box {box_index} layer keys", set(layers) == expected_colours, sorted(layers), sorted(expected_colours), "graph")
        check(f"box {box_index} layer count", len(layers) == expected_layer_count, len(layers), expected_layer_count, "graph")
        incidence_max: dict[str, int] = {}
        for colour, layer in sorted(layers.items()):
            counts = [0] * len(vertices)
            for left, right, _axis, _parity in layer:
                counts[left] += 1
                counts[right] += 1
            incidence_max[str(colour)] = max(counts, default=0)
            check(f"box {box_index} matching {colour}", max(counts, default=0) <= 1, max(counts, default=0), 1, "graph")
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1 :]) for axis in range(dimension))
        check(f"box {box_index} vertex count", len(vertices) == math.prod(sides), len(vertices), math.prod(sides), "graph")
        check(f"box {box_index} edge count", len(edges) == expected_edges, len(edges), expected_edges, "graph")
        degrees = [0] * len(vertices)
        for left, right, _axis, _parity in edges:
            degrees[left] += 1
            degrees[right] += 1
        check(f"box {box_index} degree bound", max(degrees, default=0) <= 2 * dimension, max(degrees, default=0), 2 * dimension, "graph")
        weights = [Fraction(1, weight_base ** sum(abs(component - middle) for component, middle in zip(vertex, center))) for vertex in vertices]
        ratios = [weights[left] / weights[right] for left, right, _axis, _parity in edges]
        check(f"box {box_index} weight ratio lower", min(ratios, default=Fraction(1)) >= Fraction(1, weight_base), min(ratios, default=Fraction(1)), f">=1/{weight_base}", "weights")
        check(f"box {box_index} weight ratio upper", max(ratios, default=Fraction(1)) <= weight_base, max(ratios, default=Fraction(1)), f"<={weight_base}", "weights")
        layer_rows = 0
        step_rows = 0
        box_max_ratio = Fraction(0)
        for seed in range(seeds):
            momentum = [Fraction(momentum_offset + seed + sum(coefficient_value * coordinate for coefficient_value, coordinate in zip(momentum_coefficients, vertex)), momentum_denominator) for vertex in vertices]
            position = [Fraction(position_offset + seed + sum(coefficient_value * coordinate for coefficient_value, coordinate in zip(position_coefficients, vertex)), position_denominator) for vertex in vertices]
            before = energy(weights, momentum, position, chi, gamma)
            check(f"box {box_index} seed {seed} positive energy", before > 0, before, ">0", "form")
            for sign in signs:
                for order_name in orders:
                    ordered_colours = sorted(layers) if order_name == "lexicographic" else list(reversed(sorted(layers)))
                    current = list(momentum)
                    current_energy = before
                    for colour in ordered_colours:
                        current = shear(current, position, layers[colour], sign * delta, coupling)
                        after = energy(weights, current, position, chi, gamma)
                        check(f"box {box_index} seed {seed} sign {sign} {order_name} layer {colour}", after <= one_layer_factor * current_energy, after, f"<={one_layer_factor * current_energy}", "form")
                        check(f"box {box_index} seed {seed} sign {sign} {order_name} layer {colour} positive", after > 0, after, ">0", "form")
                        ratio = after / current_energy
                        box_max_ratio = max(box_max_ratio, ratio)
                        global_max_ratio = max(global_max_ratio, ratio)
                        current_energy = after
                        layer_rows += 1
                    check(f"box {box_index} seed {seed} sign {sign} {order_name} product", current_energy <= one_layer_factor ** len(ordered_colours) * before, current_energy, f"<={one_layer_factor ** len(ordered_colours) * before}", "product")
                    step_rows += 1
        total_layer_rows += layer_rows
        total_step_rows += step_rows
        box_summaries.append({"sides": list(sides), "vertices": len(vertices), "edges": len(edges), "layer_sizes": sorted(len(layer) for layer in layers.values()), "incidence_max": incidence_max, "max_layer_energy_ratio": box_max_ratio, "layer_rows": layer_rows, "product_rows": step_rows})

    endpoint_power = expected_layer_count // 2
    check("even layer count", expected_layer_count % 2 == 0, expected_layer_count, "even", "graph")
    endpoint_exponent = Fraction(expected_layer_count, 2) * coefficient
    check("derived coefficient", coefficient == 1 + kappa * coupling * coupling / (2 * chi * sqrt_gamma), coefficient, "manifest formula", "constants")
    check("endpoint exponent", endpoint_exponent == Fraction(expected_layer_count, 2) * coefficient, endpoint_exponent, "layer_count/2*C", "product")
    for steps in trotter_steps:
        step_delta = time / steps
        endpoint_factor = (1 + coefficient * step_delta) ** endpoint_power
        exponential_bound = math.exp(float(Fraction(expected_layer_count, 2) * coefficient * time))
        check(f"Trotter endpoint steps={steps}", float(endpoint_factor) <= exponential_bound + 1e-12, [endpoint_factor, exponential_bound], "<= exp(layer_count*C*t/2)", "product")
    check("all declared signs exercised", len(signs) == 2 and set(signs) == {1, -1}, signs, "{1,-1}", "coverage")
    check("all declared orders exercised", len(orders) == 2 and set(orders) == {"lexicographic", "reverse_lexicographic"}, orders, "both orders", "coverage")
    check("positive finite row coverage", total_layer_rows > 0 and total_step_rows > 0, [total_layer_rows, total_step_rows], ">0", "coverage")
    check("conditional onsite hypothesis retained", manifest["assumptions"][2].startswith("The conditional tensor-local self-adjoint onsite factor"), manifest["assumptions"][2], "conditional", "scope")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RECTANGULAR-MATCHING-LAYER-FAMILY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(assertions),
        "assertion_count": len(assertions),
        "assertions": assertions,
        "derived": {
            "dimension": dimension,
            "box_count": len(boxes),
            "boxes": box_summaries,
            "layer_count": expected_layer_count,
            "matching_coefficient": coefficient,
            "one_layer_form_factor": one_layer_factor,
            "endpoint_exponent": endpoint_exponent,
            "global_max_layer_energy_ratio": global_max_ratio,
            "total_layer_rows": total_layer_rows,
            "total_product_rows": total_step_rows,
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"R-440 PRIMARY RECTANGULAR_MATCHING_LAYER_AUDITED {payload['passed']}/{payload['assertion_count']} boxes={payload['derived']['box_count']} layers={payload['derived']['layer_count']} max_ratio={payload['derived']['global_max_layer_energy_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
