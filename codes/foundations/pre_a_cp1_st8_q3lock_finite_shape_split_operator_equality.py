#!/usr/bin/env python3
"""Primary finite Q3 split-operator equality test for EXP-001168.

This is a bounded matrix fixture.  It compares the actual onsite-plus-all-bond
split products on path4 and path6 after lifting the path4 observable by
identities on the two extra sites.  It deliberately does not approximate an
unbounded QFT dynamics or take a split-count limit.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def spectral_unitary(generator: np.ndarray, signed_time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(generator))
    return (vectors * np.exp(-1j * signed_time * values / hbar)) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(generator))
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def graph_edges(name: str) -> list[tuple[int, int]]:
    if name == "path4":
        return [(index, index + 1) for index in range(3)]
    if name == "path6":
        return [(index, index + 1) for index in range(5)]
    raise ValueError(name)


def bond_term(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    coupling = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    square = difference @ difference
    return coupling * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def terms_for(name: str, dimension: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], list[str], np.ndarray, np.ndarray]:
    volume = int(name.removeprefix("path"))
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    edges = graph_edges(name)
    bonds = [bond_term(q_ops[left], q_ops[right], parameters) for left, right in edges]
    labels = [f"onsite:{site}" for site in range(volume)] + [f"bond:{left}-{right}" for left, right in edges]
    return onsite + bonds, labels, q_single, p_single


def order_indices(order_name: str, term_count: int, volume: int) -> list[int]:
    if order_name == "onsite_then_lexicographic_bonds":
        return list(range(term_count))
    if order_name == "reverse_term_order":
        return list(reversed(range(term_count)))
    raise ValueError(order_name)


def split_step(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> np.ndarray:
    result = np.eye(terms[0].shape[0], dtype=complex)
    for index in order:
        result = spectral_unitary(terms[index], sign * delta, hbar) @ result
    return result


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001168" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001168/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph fixture", list(fixture["graphs"]) == ["path4", "path6"], list(fixture["graphs"]), "path4/path6", "fixture")
    check("rooted fixture", int(fixture["source_site"]) == 1 and int(fixture["rooted_radius"]) == 2, [fixture["source_site"], fixture["rooted_radius"]], "source=1 radius=2", "fixture")
    check("step fixture", fixture["steps"] == [0, 1, 2, 3, 4], fixture["steps"], "0,1,2,3,4", "fixture")
    check("scope firewall", scope["finite_operator_shape_equality_closed"] and scope["finite_first_external_step_witness_closed"] and not scope["analytic_trotter_rate_closed"] and not scope["N_to_infinity_common_alpha_closed"], scope, "finite matrix only", "scope")

    dimension = int(fixture["oscillator_dimension"])
    hbar = float(Fraction(fixture["hbar"]))
    amplitude = float(Fraction(fixture["character_amplitude"]))
    delta = float(Fraction(fixture["time_step"]))
    tolerance = float(fixture["finite_tolerance"])
    comparison_tolerance = float(fixture["comparison_tolerance"])
    witness_floor = float(fixture["first_external_step_floor"])
    source_site = int(fixture["source_site"])
    radius = int(fixture["rooted_radius"])
    steps = [int(value) for value in fixture["steps"]]
    paths: dict[str, dict[str, Any]] = {}
    parameters = manifest["model_parameters"]
    for name, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        edges = graph_edges(name)
        declared_edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
        check(f"{name} edge fixture", edges == declared_edges, edges, declared_edges, "graph")
        terms, labels, q_single, _ = terms_for(name, dimension, parameters)
        hermitian_errors = [operator_norm(term - term.conj().T) for term in terms]
        check(f"{name} term hermiticity", max(hermitian_errors, default=0.0) <= tolerance, max(hermitian_errors, default=0.0), f"<={tolerance}", "matrix")
        local_character = character(q_single, amplitude, hbar)
        identity = np.eye(dimension, dtype=complex)
        observable = embed(local_character, source_site, volume, identity)
        check(f"{name} observable dimension", observable.shape == (dimension**volume, dimension**volume), observable.shape, (dimension**volume, dimension**volume), "matrix")
        paths[name] = {"volume": volume, "edges": edges, "terms": terms, "labels": labels, "observable": observable, "identity": identity}

    check("rooted path ball", paths["path4"]["edges"] == [(0, 1), (1, 2), (2, 3)] and paths["path6"]["edges"][:3] == [(0, 1), (1, 2), (2, 3)], "path4/path6 common radius-2 edge set", "rooted radius-2 agreement", "shape")

    shape_rows: list[dict[str, Any]] = []
    for order_name in fixture["term_orders"]:
        for sign in (int(value) for value in fixture["time_signs"]):
            orders = {name: order_indices(order_name, len(data["terms"]), int(data["volume"])) for name, data in paths.items()}
            unitaries = {name: split_step(data["terms"], orders[name], sign, delta, hbar) for name, data in paths.items()}
            for name, unitary in unitaries.items():
                identity_matrix = np.eye(unitary.shape[0], dtype=complex)
                check(f"{name} unitary {order_name} sign={sign}", operator_norm(unitary.conj().T @ unitary - identity_matrix) <= comparison_tolerance, operator_norm(unitary.conj().T @ unitary - identity_matrix), f"<={comparison_tolerance}", "unitary")
            for adjoint in (0, 1):
                context = {"order": order_name, "time_sign": sign, "adjoint": adjoint}
                evolved = {name: data["observable"].conj().T.copy() if adjoint else data["observable"].copy() for name, data in paths.items()}
                rows_for_context: list[dict[str, Any]] = []
                for step in steps:
                    lifted = np.kron(evolved["path4"], np.eye(dimension ** 2, dtype=complex))
                    difference = evolved["path6"] - lifted
                    norm = operator_norm(difference)
                    frobenius = float(np.linalg.norm(difference, ord="fro"))
                    check(f"shape finite {order_name} sign={sign} adjoint={adjoint} step={step}", np.isfinite(norm) and np.isfinite(frobenius), [norm, frobenius], "finite", "shape")
                    row = {**context, "step": step, "operator_norm": norm, "frobenius_norm": frobenius}
                    rows_for_context.append(row)
                    shape_rows.append(row)
                    if step < max(steps):
                        for name, unitary in unitaries.items():
                            evolved[name] = unitary @ evolved[name] @ unitary.conj().T
                first_external_step = int(fixture["first_external_step_by_order"][order_name])
                check(f"first-step fixture {order_name}", first_external_step in steps and first_external_step > radius, first_external_step, f">{radius} and present", "fixture")
                inside = [row["operator_norm"] for row in rows_for_context if row["step"] < first_external_step]
                external = [row["operator_norm"] for row in rows_for_context if row["step"] == first_external_step]
                check(f"common rooted ball {order_name} sign={sign} adjoint={adjoint}", max(inside, default=0.0) <= tolerance, max(inside, default=0.0), f"<={tolerance}", "shape")
                check(f"first external witness {order_name} sign={sign} adjoint={adjoint}", min(external, default=0.0) >= witness_floor, min(external, default=0.0), f">={witness_floor}", "adversarial off-by-one")

    expected_rows = len(fixture["term_orders"]) * len(fixture["time_signs"]) * 2 * len(steps)
    check("shape row coverage", len(shape_rows) == expected_rows, len(shape_rows), expected_rows, "coverage")
    first_steps = {name: int(value) for name, value in fixture["first_external_step_by_order"].items()}
    max_inside = max((row["operator_norm"] for row in shape_rows if row["step"] < first_steps[row["order"]]), default=0.0)
    min_external = min((row["operator_norm"] for row in shape_rows if row["step"] == first_steps[row["order"]]), default=0.0)
    check("shape extrema finite", np.isfinite(max_inside) and np.isfinite(min_external), [max_inside, min_external], "finite", "coverage")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "total": len(checks),
        "failed": 0,
        "assertions": checks,
        "shape_rows": shape_rows,
        "shape_equivalence": {"left": "path4", "right": "path6", "source_site": source_site, "rooted_radius": radius, "steps_checked": steps},
        "derived": {
            "finite_operator_shape_equality_closed": True,
            "finite_first_external_step_witness_closed": True,
            "rooted_ball_hypothesis_explicit": True,
            "shape_context_count": len(fixture["term_orders"]) * len(fixture["time_signs"]) * 2,
            "shape_row_count": len(shape_rows),
            "max_inside_operator_norm": max_inside,
            "min_first_external_operator_norm": min_external,
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
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-SHAPE-SPLIT-OPERATOR-EQUALITY PASS {payload['passed']}/{payload['total']} rows={payload['derived']['shape_row_count']} min_external={payload['derived']['min_first_external_operator_norm']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
