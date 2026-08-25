#!/usr/bin/env python3
"""Independent normal-order reconstruction for EXP-001108.

This lane obtains the d-component expansion by multinomially combining the
one-component powers instead of raising the d-component operator directly.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from itertools import product
from math import comb, factorial, factorial as fact
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_eight_component_n5_normal_order"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def one_mul(left: dict[tuple[int, int], int], right: dict[tuple[int, int], int]) -> dict[tuple[int, int], int]:
    result: defaultdict[tuple[int, int], int] = defaultdict(int)
    for (left_creation, left_annihilation), left_coefficient in left.items():
        for (right_creation, right_annihilation), right_coefficient in right.items():
            for contraction in range(min(left_annihilation, right_creation) + 1):
                result[(left_creation + right_creation - contraction, left_annihilation + right_annihilation - contraction)] += left_coefficient * right_coefficient * comb(left_annihilation, contraction) * comb(right_creation, contraction) * fact(contraction)
    return {key: value for key, value in result.items() if value != 0}


def one_power(order: int) -> dict[tuple[int, int], int]:
    number = {(1, 1): 1}
    current = {(0, 0): 1}
    for _ in range(order):
        current = one_mul(current, number)
    return current


def compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    if parts == 1:
        return [(total,)]
    result: list[tuple[int, ...]] = []
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            result.append((first,) + rest)
    return result


def tensor_terms(components: int, order: int) -> dict[tuple[tuple[int, ...], tuple[int, ...]], int]:
    powers = [one_power(index) for index in range(order + 1)]
    result: defaultdict[tuple[tuple[int, ...], tuple[int, ...]], int] = defaultdict(int)
    for allocation in compositions(order, components):
        coefficient = fact(order)
        for value in allocation:
            coefficient //= fact(value)
        choices = [list(powers[value].items()) for value in allocation]
        for selected in product(*choices):
            creation = tuple(item[0][0] for item in selected)
            annihilation = tuple(item[0][1] for item in selected)
            value = coefficient
            for _, item_coefficient in selected:
                value *= item_coefficient
            result[(creation, annihilation)] += value
    return {key: value for key, value in result.items() if value != 0}


def degree(key: tuple[tuple[int, ...], tuple[int, ...]]) -> int:
    return sum(key[0]) + sum(key[1])


def ladder(dimension: int) -> np.ndarray:
    result = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        result[index, index + 1] = np.sqrt(float(index + 1))
    return result


def tensor(single: np.ndarray, index: int, components: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    result = np.array([[1.0 + 0.0j]])
    for component in range(components):
        result = np.kron(result, single if component == index else identity)
    return result


def normal_matrix(components: int, dimension: int, terms: dict[tuple[tuple[int, ...], tuple[int, ...]], int]) -> np.ndarray:
    annihilation = ladder(dimension)
    creation_sites = [tensor(annihilation.T.conj(), index, components, dimension) for index in range(components)]
    annihilation_sites = [tensor(annihilation, index, components, dimension) for index in range(components)]
    result = np.zeros((dimension**components, dimension**components), dtype=complex)
    for (creation, annihilation_exponents), coefficient in terms.items():
        term = np.eye(dimension**components, dtype=complex)
        for index in range(components):
            term = term @ np.linalg.matrix_power(creation_sites[index], creation[index]) @ np.linalg.matrix_power(annihilation_sites[index], annihilation_exponents[index])
        result += coefficient * term
    return result


def number_matrix(components: int, dimension: int) -> np.ndarray:
    annihilation = ladder(dimension)
    single = annihilation.T.conj() @ annihilation
    sites = [tensor(single, index, components, dimension) for index in range(components)]
    return sum(sites, np.zeros_like(sites[0]))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
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
        terms = tensor_terms(components, order)
        degrees = [degree(key) for key in terms]
        max_total = max(degrees)
        max_anisotropic = max(weight * item for item in degrees)
        coefficient_l1 = sum(abs(value) for value in terms.values())
        check(f"components={components} nonempty", len(terms) > 0, len(terms), ">0", "normal order")
        check(f"components={components} degree bound", max_total <= maximum_degree, max_total, f"<={maximum_degree}", "normal order")
        check(f"components={components} anisotropic bound", max_anisotropic <= order + tolerance, max_anisotropic, f"<={order}", "order")
        component_rows.append({"components": components, "term_count": len(terms), "max_total_degree": max_total, "max_anisotropic_order": max_anisotropic, "coefficient_l1": coefficient_l1})
    matrix_rows: list[dict[str, Any]] = []
    for components in [int(value) for value in fixture["matrix_component_values"]]:
        terms = tensor_terms(components, order)
        for low_dimension in [int(value) for value in fixture["matrix_low_dimensions"]]:
            ambient_dimension = low_dimension + int(fixture["matrix_ambient_padding"])
            expected = np.linalg.matrix_power(number_matrix(components, ambient_dimension), order)
            normal = normal_matrix(components, ambient_dimension, terms)
            low_size = low_dimension**components
            residual = float(np.linalg.norm(expected[:low_size, :low_size] - normal[:low_size, :low_size], ord=2))
            check(f"components={components} low={low_dimension} matrix identity", residual <= tolerance, residual, f"<={tolerance}", "matrix")
            matrix_rows.append({"components": components, "low_dimension": low_dimension, "ambient_dimension": ambient_dimension, "low_block_size": low_size, "residual": residual})
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-EIGHT-COMPONENT-N5-NORMAL-ORDER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"component_rows": component_rows, "matrix_rows": matrix_rows, "normal_order_expansion_closed": True, "eight_component_order_admissibility_closed": True, "low_block_matrix_identity_closed": True, "uniform_graph_constant_instantiated": False, "q_p_to_creation_annihilation_domain_closed": False, "energy_to_number_uniform_form_domination_closed": False, "q3_gibbs_weighted_tail_uniformity_closed": False, "q3_evolved_history_weighted_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_orientation_history_uniform_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT EIGHT-COMPONENT-N5-NORMAL-ORDER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
