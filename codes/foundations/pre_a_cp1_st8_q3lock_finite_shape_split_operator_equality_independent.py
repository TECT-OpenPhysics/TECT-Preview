#!/usr/bin/env python3
"""Independent reconstruction of the EXP-001168 finite matrix shape test.

No project Q3 helper or primary module is imported.  The duplication is
intentional: it checks the graph, oscillator, Q3 terms, spectral factors and
embedded-operator comparison independently.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-shape-split-operator-equality"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def save(path: Path, payload: dict[str, Any]) -> None:
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


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def ladder(name: str) -> list[tuple[int, int]]:
    count = {"path4": 4, "path6": 6}[name]
    return [(index, index + 1) for index in range(count - 1)]


def local_oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(float(index + 1))
    raising = lowering.conj().T
    position = (lowering + raising) / np.sqrt(2.0)
    momentum = (lowering - raising) / (1j * np.sqrt(2.0))
    return position, momentum


def tensor_at(single: np.ndarray, site: int, count: int, identity: np.ndarray) -> np.ndarray:
    result = None
    for index in range(count):
        factor = single if index == site else identity
        result = factor.copy() if result is None else np.kron(result, factor)
    if result is None:
        raise ValueError("empty graph")
    return result


def symmetrize(matrix: np.ndarray) -> np.ndarray:
    return 0.5 * (matrix + matrix.conj().T)


def exponential(generator: np.ndarray, signed_time: float, hbar: float, phase: int) -> np.ndarray:
    values, vectors = np.linalg.eigh(symmetrize(generator))
    return (vectors * np.exp(phase * 1j * signed_time * values / hbar)) @ vectors.conj().T


def q3_bond(left: np.ndarray, right: np.ndarray, params: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    c = float(Fraction(params["c"]))
    nonlinear = float(Fraction(params["lambda"]))
    return c * square / 2.0 + nonlinear * square @ (left @ left + right @ right) / 4.0


def assemble(name: str, dimension: int, params: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, int, list[tuple[int, int]]]:
    vertices = int(name[4:])
    position, momentum = local_oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    positions = [tensor_at(position, site, vertices, identity) for site in range(vertices)]
    momenta = [tensor_at(momentum, site, vertices, identity) for site in range(vertices)]
    chi = float(Fraction(params["chi"]))
    mass = float(Fraction(params["r"]))
    quartic = float(Fraction(params["g"]))
    terms = [p @ p / (2.0 * chi) + mass * q @ q / 2.0 + quartic * q @ q @ q @ q / 4.0 for q, p in zip(positions, momenta)]
    edges = ladder(name)
    terms.extend(q3_bond(positions[left], positions[right], params) for left, right in edges)
    return terms, position, vertices, edges


def split(terms: list[np.ndarray], order_name: str, sign: int, delta: float, hbar: float, volume: int) -> np.ndarray:
    order = list(range(len(terms)))
    if order_name == "reverse_term_order":
        order.reverse()
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = exponential(terms[index], sign * delta, hbar, -1) @ result
    return result


def source_character(position: np.ndarray, dimension: int, amplitude: float, hbar: float, volume: int, source_site: int) -> np.ndarray:
    values, vectors = np.linalg.eigh(symmetrize(position))
    local = (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T
    return tensor_at(local, source_site, volume, np.eye(dimension, dtype=complex))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    checks = Checks()
    checks.add("identity", manifest["exploration_id"] == "EXP-001168" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001168/T-054", "provenance")
    checks.add("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    checks.add("source and radius", int(fixture["source_site"]) == 1 and int(fixture["rooted_radius"]) == 2, [fixture["source_site"], fixture["rooted_radius"]], "1 and 2", "fixture")
    checks.add("scope firewall", scope["finite_operator_shape_equality_closed"] and scope["finite_first_external_step_witness_closed"] and not scope["analytic_trotter_rate_closed"] and not scope["N_to_infinity_common_alpha_closed"], scope, "finite matrix only", "scope")

    dimension = int(fixture["oscillator_dimension"])
    hbar = float(Fraction(fixture["hbar"]))
    amplitude = float(Fraction(fixture["character_amplitude"]))
    delta = float(Fraction(fixture["time_step"]))
    tolerance = float(fixture["finite_tolerance"])
    comparison_tolerance = float(fixture["comparison_tolerance"])
    floor = float(fixture["first_external_step_floor"])
    radius = int(fixture["rooted_radius"])
    source_site = int(fixture["source_site"])
    steps = [int(value) for value in fixture["steps"]]
    params = manifest["model_parameters"]
    data: dict[str, dict[str, Any]] = {}
    for name, declaration in fixture["graphs"].items():
        terms, position, volume, edges = assemble(name, dimension, params)
        declared = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
        checks.add(f"{name} edge reconstruction", edges == declared, edges, declared, "graph")
        hermitian_error = max((float(np.linalg.norm(term - term.conj().T, ord=2)) for term in terms), default=0.0)
        checks.add(f"{name} hermitian terms", hermitian_error <= tolerance, hermitian_error, f"<={tolerance}", "matrix")
        observable = source_character(position, dimension, amplitude, hbar, volume, source_site)
        checks.add(f"{name} observable shape", observable.shape == (dimension**volume, dimension**volume), observable.shape, (dimension**volume, dimension**volume), "matrix")
        data[name] = {"terms": terms, "volume": volume, "observable": observable, "edges": edges}
    checks.add("rooted edge agreement", data["path4"]["edges"] == [(0, 1), (1, 2), (2, 3)] and data["path6"]["edges"][:3] == [(0, 1), (1, 2), (2, 3)], "common induced radius-2 path", "same", "shape")

    rows: list[dict[str, Any]] = []
    for order_name in fixture["term_orders"]:
        for sign in (int(value) for value in fixture["time_signs"]):
            operators = {name: split(item["terms"], order_name, sign, delta, hbar, item["volume"]) for name, item in data.items()}
            for name, operator in operators.items():
                error = float(np.linalg.norm(operator.conj().T @ operator - np.eye(operator.shape[0]), ord=2))
                checks.add(f"{name} unitary {order_name} {sign}", error <= comparison_tolerance, error, f"<={comparison_tolerance}", "unitary")
            for adjoint in (0, 1):
                current = {name: item["observable"].conj().T.copy() if adjoint else item["observable"].copy() for name, item in data.items()}
                context_rows: list[dict[str, Any]] = []
                for step in steps:
                    lift = np.kron(current["path4"], np.eye(dimension**2, dtype=complex))
                    difference = current["path6"] - lift
                    norm = float(np.linalg.norm(difference, ord=2))
                    fro = float(np.linalg.norm(difference, ord="fro"))
                    checks.add(f"finite shape {order_name} {sign} {adjoint} {step}", np.isfinite(norm) and np.isfinite(fro), [norm, fro], "finite", "shape")
                    row = {"order": order_name, "time_sign": sign, "adjoint": adjoint, "step": step, "operator_norm": norm, "frobenius_norm": fro}
                    context_rows.append(row)
                    rows.append(row)
                    if step < max(steps):
                        for name, operator in operators.items():
                            current[name] = operator @ current[name] @ operator.conj().T
                first_external_step = int(fixture["first_external_step_by_order"][order_name])
                checks.add(f"first-step fixture {order_name}", first_external_step in steps and first_external_step > radius, first_external_step, f">{radius} and present", "fixture")
                inside = max(row["operator_norm"] for row in context_rows if row["step"] < first_external_step)
                external = min(row["operator_norm"] for row in context_rows if row["step"] == first_external_step)
                checks.add(f"common ball {order_name} {sign} {adjoint}", inside <= tolerance, inside, f"<={tolerance}", "shape")
                checks.add(f"external witness {order_name} {sign} {adjoint}", external >= floor, external, f">={floor}", "adversarial off-by-one")
    expected = len(fixture["term_orders"]) * len(fixture["time_signs"]) * 2 * len(steps)
    checks.add("row coverage", len(rows) == expected, len(rows), expected, "coverage")
    first_steps = {name: int(value) for name, value in fixture["first_external_step_by_order"].items()}
    inside_max = max(row["operator_norm"] for row in rows if row["step"] < first_steps[row["order"]])
    external_min = min(row["operator_norm"] for row in rows if row["step"] == first_steps[row["order"]])
    checks.add("extrema finite", np.isfinite(inside_max) and np.isfinite(external_min), [inside_max, external_min], "finite", "coverage")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks.rows),
        "total": len(checks.rows),
        "failed": 0,
        "assertions": checks.rows,
        "shape_rows": rows,
        "shape_equivalence": {"left": "path4", "right": "path6", "source_site": source_site, "rooted_radius": radius, "steps_checked": steps},
        "derived": {
            "finite_operator_shape_equality_closed": True,
            "finite_first_external_step_witness_closed": True,
            "rooted_ball_hypothesis_explicit": True,
            "shape_context_count": len(fixture["term_orders"]) * len(fixture["time_signs"]) * 2,
            "shape_row_count": len(rows),
            "max_inside_operator_norm": inside_max,
            "min_first_external_operator_norm": external_min,
            "first_external_step_by_order": first_steps,
            "analytic_trotter_rate_closed": False,
            "uniform_graph_lipschitz_closed": False,
            "common_core_domain_closed": False,
            "direct_d_delta_d_cauchy_closed": False,
            "N_to_infinity_common_alpha_closed": False,
            "exhaustion_independence_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "no_new_negative_result": True,
            "no_tier_change": True,
            "no_pdf": True
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY PASS {payload['passed']}/{payload['total']} rows={payload['derived']['shape_row_count']} min_external={payload['derived']['min_first_external_operator_norm']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
