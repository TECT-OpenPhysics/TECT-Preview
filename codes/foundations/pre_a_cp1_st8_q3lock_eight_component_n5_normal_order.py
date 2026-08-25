#!/usr/bin/env python3
"""Primary exact normal-order audit for the eight-component N^5 bridge."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from itertools import product
from math import comb, factorial
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_eight_component_n5_normal_order"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def zero_multi(dimension: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (tuple(0 for _ in range(dimension)), tuple(0 for _ in range(dimension)))


def number_operator(dimension: int, component: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    creation = [0] * dimension
    annihilation = [0] * dimension
    creation[component] = 1
    annihilation[component] = 1
    return {(tuple(creation), tuple(annihilation)): 1}


def multiply_normal(
    left: dict[tuple[tuple[int, ...], tuple[int, ...]], int],
    right: dict[tuple[tuple[int, ...], tuple[int, ...]], int],
) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    result: defaultdict[tuple[tuple[int, ...], tuple[int, ...]], int] = defaultdict(int)
    for (left_creation, left_annihilation), left_coefficient in left.items():
        for (right_creation, right_annihilation), right_coefficient in right.items():
            dimensions = len(left_creation)
            choices = [range(min(left_annihilation[index], right_creation[index]) + 1) for index in range(dimensions)]
            for contractions in product(*choices):
                coefficient = left_coefficient * right_coefficient
                creation: list[int] = []
                annihilation: list[int] = []
                for index, contraction in enumerate(contractions):
                    coefficient *= comb(left_annihilation[index], contraction) * comb(right_creation[index], contraction) * factorial(contraction)
                    creation.append(left_creation[index] + right_creation[index] - contraction)
                    annihilation.append(left_annihilation[index] + right_annihilation[index] - contraction)
                result[(tuple(creation), tuple(annihilation))] += coefficient
    return {key: value for key, value in result.items() if value != 0}


def normal_power(dimension: int, order: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    current = {zero_multi(dimension): 1}
    operator: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
    for component in range(dimension):
        for key, value in number_operator(dimension, component).items():
            operator[key] = operator.get(key, 0) + value
    for _ in range(order):
        current = multiply_normal(current, operator)
    return current


def total_degree(key: tuple[tuple[int, ...], tuple[int, ...]]) -> int:
    creation, annihilation = key
    return sum(creation) + sum(annihilation)


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    return (annihilation + annihilation.conj().T) / np.sqrt(2.0), (annihilation - annihilation.conj().T) / (1j * np.sqrt(2.0))


def tensor_operator(single: np.ndarray, component: int, components: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    result = np.array([[1.0 + 0.0j]])
    for index in range(components):
        result = np.kron(result, single if index == component else identity)
    return result


def normal_matrix(components: int, dimension: int, terms: dict[tuple[tuple[int, ...], tuple[int, ...]], int]) -> np.ndarray:
    annihilation_single = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation_single[index, index + 1] = np.sqrt(index + 1.0)
    creation_sites = [tensor_operator(annihilation_single.conj().T, component, components, dimension) for component in range(components)]
    annihilation_sites = [tensor_operator(annihilation_single, component, components, dimension) for component in range(components)]
    result = np.zeros((dimension**components, dimension**components), dtype=complex)
    for (creation, annihilation), coefficient in terms.items():
        term = np.eye(dimension**components, dtype=complex)
        for component in range(components):
            term = term @ np.linalg.matrix_power(creation_sites[component], creation[component]) @ np.linalg.matrix_power(annihilation_sites[component], annihilation[component])
        result += coefficient * term
    return result


def number_matrix(components: int, dimension: int) -> np.ndarray:
    annihilation_single = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation_single[index, index + 1] = np.sqrt(index + 1.0)
    creation_single = annihilation_single.conj().T
    sites = [tensor_operator(creation_single @ annihilation_single, component, components, dimension) for component in range(components)]
    return sum(sites, np.zeros_like(sites[0]))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    order = int(fixture["moment_order"])
    maximum_degree = int(fixture["maximum_total_degree"])
    weight = float(fixture["anisotropic_creation_annihilation_weight"])
    tolerance = float(fixture["tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001108" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001108/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("order inputs", order == 5 and maximum_degree == 2 * order and weight == 0.5, [order, maximum_degree, weight], "[5,10,0.5]", "order")
    check("scope firewall", scope["normal_order_expansion_closed"] and scope["eight_component_order_admissibility_closed"] and not scope["uniform_graph_constant_instantiated"], scope, "order audit only", "scope")
    component_rows: list[dict[str, Any]] = []
    for components in [int(value) for value in fixture["component_values"]]:
        terms = normal_power(components, order)
        degrees = [total_degree(key) for key in terms]
        max_total = max(degrees)
        max_anisotropic = max(weight * degree for degree in degrees)
        coefficient_l1 = sum(abs(value) for value in terms.values())
        check(f"components={components} nonempty", len(terms) > 0, len(terms), ">0", "normal order")
        check(f"components={components} degree bound", max_total <= maximum_degree, max_total, f"<={maximum_degree}", "normal order")
        check(f"components={components} anisotropic bound", max_anisotropic <= order + tolerance, max_anisotropic, f"<={order}", "order")
        component_rows.append({"components": components, "term_count": len(terms), "max_total_degree": max_total, "max_anisotropic_order": max_anisotropic, "coefficient_l1": coefficient_l1})
    matrix_rows: list[dict[str, Any]] = []
    for components in [int(value) for value in fixture["matrix_component_values"]]:
        terms = normal_power(components, order)
        for low_dimension in [int(value) for value in fixture["matrix_low_dimensions"]]:
            ambient_dimension = low_dimension + int(fixture["matrix_ambient_padding"])
            expected = np.linalg.matrix_power(number_matrix(components, ambient_dimension), order)
            normal = normal_matrix(components, ambient_dimension, terms)
            low_size = low_dimension**components
            residual = float(np.linalg.norm(expected[:low_size, :low_size] - normal[:low_size, :low_size], ord=2))
            check(f"components={components} low={low_dimension} matrix identity", residual <= tolerance, residual, f"<={tolerance}", "matrix")
            matrix_rows.append({"components": components, "low_dimension": low_dimension, "ambient_dimension": ambient_dimension, "low_block_size": low_size, "residual": residual})
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-EIGHT-COMPONENT-N5-NORMAL-ORDER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"component_rows": component_rows, "matrix_rows": matrix_rows, "normal_order_expansion_closed": True, "eight_component_order_admissibility_closed": True, "low_block_matrix_identity_closed": True, "uniform_graph_constant_instantiated": False, "q_p_to_creation_annihilation_domain_closed": False, "energy_to_number_uniform_form_domination_closed": False, "q3_gibbs_weighted_tail_uniformity_closed": False, "q3_evolved_history_weighted_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_orientation_history_uniform_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY EIGHT-COMPONENT-N5-NORMAL-ORDER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
