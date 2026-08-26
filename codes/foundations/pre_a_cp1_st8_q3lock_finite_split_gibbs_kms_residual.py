#!/usr/bin/env python3
"""Primary finite Q3 split Gibbs/KMS residual audit for EXP-001170.

This is a bounded d=3 matrix diagnostic.  It tests the equilibrium interface
of the registered onsite-plus-all-bond Lie--Trotter products, while keeping the
thermodynamic, common-core and OS/KMS identification obligations open.
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
SLUG = "pre-a-cp1-st8-q3lock-finite-split-gibbs-kms-residual"
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
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(index + 1.0)
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def spectral_factor(values: np.ndarray, vectors: np.ndarray, z: complex, hbar: float) -> np.ndarray:
    return (vectors * np.exp(-1j * z * values / hbar)) @ vectors.conj().T


def product_pair(caches: list[tuple[np.ndarray, np.ndarray]], order: list[int], z: complex, hbar: float) -> tuple[np.ndarray, np.ndarray]:
    size = caches[0][1].shape[0]
    product = np.eye(size, dtype=complex)
    inverse = np.eye(size, dtype=complex)
    for index in order:
        values, vectors = caches[index]
        product = spectral_factor(values, vectors, z, hbar) @ product
        inverse = inverse @ spectral_factor(values, vectors, -z, hbar)
    return product, inverse


def gibbs(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = eigensystem(generator)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def bond_term(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    coupling = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    square = difference @ difference
    return coupling * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def graph_edges(name: str) -> list[tuple[int, int]]:
    volume = int(name.removeprefix("path"))
    return [(index, index + 1) for index in range(volume - 1)]


def terms_for(name: str, dimension: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    volume = int(name.removeprefix("path"))
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [bond_term(q_ops[left], q_ops[right], parameters) for left, right in graph_edges(name)]
    return onsite + bonds, q_single, p_single


def order_indices(order_name: str, term_count: int) -> list[int]:
    if order_name == "onsite_then_lexicographic_bonds":
        return list(range(term_count))
    if order_name == "reverse_term_order":
        return list(reversed(range(term_count)))
    raise ValueError(order_name)


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def trace_norm(matrix: np.ndarray) -> float:
    values = np.linalg.eigvalsh(hermitian(matrix))
    return float(np.sum(np.abs(values)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001170" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001170/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph fixture", list(fixture["graphs"]) == ["path4", "path6"], list(fixture["graphs"]), "path4/path6", "fixture")
    check("dimension fixture", int(fixture["oscillator_dimension"]) == 3, fixture["oscillator_dimension"], 3, "nondegenerate d=3")
    check("mesh fixture", list(fixture["delta_values"]) == [0.1, 0.05], fixture["delta_values"], "coarse/fine", "fixture")
    check("scope firewall", scope["finite_exact_gibbs_control_closed"] and scope["finite_split_stationarity_rows_closed"] and scope["finite_split_kms_residual_rows_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite diagnostic only", "scope")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    deltas = [float(value) for value in fixture["delta_values"]]
    horizon = float(fixture["horizon"])
    signs = [int(value) for value in fixture["time_signs"]]
    source_site = int(fixture["source_site"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    exact_tolerance = float(fixture["exact_kms_tolerance"])
    finite_tolerance = float(fixture["finite_tolerance"])
    agreement_tolerance = float(fixture["agreement_tolerance"])
    kms_floor = float(fixture["kms_witness_floor"])
    stationarity_floor = float(fixture["stationarity_witness_floor"])
    noncommutation_floor = float(fixture["noncommutation_witness_floor"])
    parameters = manifest["model_parameters"]
    order_names = ["onsite_then_lexicographic_bonds", "reverse_term_order"]
    rows: list[dict[str, Any]] = []
    exact_rows: list[dict[str, Any]] = []
    mesh_rows: list[dict[str, Any]] = []
    shape_rows: list[dict[str, Any]] = []

    for graph_name, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        declared_edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
        check(f"{graph_name} edge fixture", graph_edges(graph_name) == declared_edges, graph_edges(graph_name), declared_edges, "graph")
        terms, q_single, p_single = terms_for(graph_name, dimension, parameters)
        hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
        h_values, h_vectors = eigensystem(hamiltonian)
        h_cache = (h_values, h_vectors)
        q_observable = embed(character(q_single, amplitude, hbar), source_site, volume, np.eye(dimension, dtype=complex))
        p_observable = embed(character(p_single, amplitude, hbar), source_site, volume, np.eye(dimension, dtype=complex))
        term_caches = [eigensystem(term) for term in terms]
        noncommutation = operator_norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
        check(f"{graph_name} noncommutation", noncommutation >= noncommutation_floor, noncommutation, f">={noncommutation_floor}", "nondegenerate Q3")

        exact_by_beta_sign: dict[tuple[float, int], dict[str, float]] = {}
        for beta in beta_values:
            rho = gibbs(h_values, h_vectors, beta)
            for sign in signs:
                real_z = sign * horizon
                exact_real = spectral_factor(h_values, h_vectors, real_z, hbar)
                exact_real_inverse = spectral_factor(h_values, h_vectors, -real_z, hbar)
                exact_complex_z = real_z + 1j * beta * hbar
                exact_complex = spectral_factor(h_values, h_vectors, exact_complex_z, hbar)
                exact_complex_inverse = spectral_factor(h_values, h_vectors, -exact_complex_z, hbar)
                exact_state = trace_norm(exact_real @ rho @ exact_real_inverse - rho)
                exact_kms = abs(
                    np.trace(rho @ q_observable @ (exact_real @ p_observable @ exact_real_inverse))
                    - np.trace(rho @ (exact_complex @ p_observable @ exact_complex_inverse) @ q_observable)
                )
                check(f"{graph_name} beta={beta} sign={sign} exact stationarity", exact_state <= exact_tolerance, exact_state, f"<={exact_tolerance}", "exact Gibbs control")
                check(f"{graph_name} beta={beta} sign={sign} exact KMS", exact_kms <= exact_tolerance, exact_kms, f"<={exact_tolerance}", "exact KMS control")
                exact_by_beta_sign[(beta, sign)] = {"stationarity": exact_state, "kms": float(exact_kms)}
                exact_rows.append({"graph": graph_name, "beta": beta, "sign": sign, "stationarity_defect": exact_state, "kms_residual": float(exact_kms)})

        real_products: dict[tuple[str, float, int], tuple[np.ndarray, np.ndarray]] = {}
        for order_name in order_names:
            order = order_indices(order_name, len(terms))
            for delta in deltas:
                steps_float = horizon / delta
                steps = int(round(steps_float))
                check(f"{graph_name} {order_name} delta={delta} integral steps", abs(steps_float - steps) <= finite_tolerance and steps > 0, steps_float, steps, "mesh")
                for sign in signs:
                    one_step, one_step_inverse = product_pair(term_caches, order, sign * delta, hbar)
                    real_product = np.linalg.matrix_power(one_step, steps)
                    real_inverse = np.linalg.matrix_power(one_step_inverse, steps)
                    inverse_error = operator_norm(real_product @ real_inverse - np.eye(real_product.shape[0], dtype=complex))
                    check(f"{graph_name} {order_name} delta={delta} sign={sign} real inverse", inverse_error <= agreement_tolerance, inverse_error, f"<={agreement_tolerance}", "product algebra")
                    real_products[(order_name, delta, sign)] = (real_product, real_inverse)

        for beta in beta_values:
            rho = gibbs(h_values, h_vectors, beta)
            for order_name in order_names:
                order = order_indices(order_name, len(terms))
                for delta in deltas:
                    steps = int(round(horizon / delta))
                    for sign in signs:
                        real_product, real_inverse = real_products[(order_name, delta, sign)]
                        complex_step, complex_step_inverse = product_pair(term_caches, order, sign * delta + 1j * beta * hbar / steps, hbar)
                        complex_product = np.linalg.matrix_power(complex_step, steps)
                        complex_inverse = np.linalg.matrix_power(complex_step_inverse, steps)
                        complex_inverse_error = operator_norm(complex_product @ complex_inverse - np.eye(complex_product.shape[0], dtype=complex))
                        check(f"{graph_name} {order_name} beta={beta} delta={delta} sign={sign} complex inverse", complex_inverse_error <= agreement_tolerance, complex_inverse_error, f"<={agreement_tolerance}", "complex product algebra")
                        evolved_b = real_product @ p_observable @ real_inverse
                        shifted_b = complex_product @ p_observable @ complex_inverse
                        stationarity = trace_norm(real_product @ rho @ real_inverse - rho)
                        kms_residual = abs(np.trace(rho @ q_observable @ evolved_b) - np.trace(rho @ shifted_b @ q_observable))
                        check(f"{graph_name} {order_name} beta={beta} delta={delta} sign={sign} finite", np.isfinite(stationarity) and np.isfinite(kms_residual), [stationarity, kms_residual], "finite", "finite split rows")
                        check(f"{graph_name} {order_name} beta={beta} delta={delta} sign={sign} positive", stationarity >= -finite_tolerance and kms_residual >= -finite_tolerance, [stationarity, kms_residual], ">=-tolerance", "residuals")
                        check(f"{graph_name} {order_name} beta={beta} delta={delta} sign={sign} KMS witness", kms_residual >= kms_floor, kms_residual, f">={kms_floor}", "split not exact KMS")
                        check(f"{graph_name} {order_name} beta={beta} delta={delta} sign={sign} stationarity witness", stationarity >= stationarity_floor, stationarity, f">={stationarity_floor}", "split not exact stationary")
                        rows.append({"graph": graph_name, "volume": volume, "beta": beta, "delta": delta, "steps": steps, "sign": sign, "order": order_name, "stationarity_defect": stationarity, "kms_residual": float(kms_residual), "complex_inverse_error": complex_inverse_error})

        for beta in beta_values:
            for order_name in order_names:
                for sign in signs:
                    coarse = next(row for row in rows if row["graph"] == graph_name and row["beta"] == beta and row["order"] == order_name and row["sign"] == sign and row["delta"] == deltas[0])
                    fine = next(row for row in rows if row["graph"] == graph_name and row["beta"] == beta and row["order"] == order_name and row["sign"] == sign and row["delta"] == deltas[-1])
                    check(f"{graph_name} {order_name} beta={beta} sign={sign} KMS mesh decrease", fine["kms_residual"] <= coarse["kms_residual"] + finite_tolerance, [coarse["kms_residual"], fine["kms_residual"]], "fine<=coarse+tolerance", "mesh trend")
                    check(f"{graph_name} {order_name} beta={beta} sign={sign} stationarity mesh decrease", fine["stationarity_defect"] <= coarse["stationarity_defect"] + finite_tolerance, [coarse["stationarity_defect"], fine["stationarity_defect"]], "fine<=coarse+tolerance", "mesh trend")
                    mesh_rows.append({"graph": graph_name, "beta": beta, "order": order_name, "sign": sign, "coarse_delta": deltas[0], "fine_delta": deltas[-1], "kms_ratio": fine["kms_residual"] / max(coarse["kms_residual"], np.finfo(float).tiny), "stationarity_ratio": fine["stationarity_defect"] / max(coarse["stationarity_defect"], np.finfo(float).tiny)})

        for beta in beta_values:
            for delta in deltas:
                for order_name in order_names:
                    for sign in signs:
                        row = next(item for item in rows if item["graph"] == graph_name and item["beta"] == beta and item["delta"] == delta and item["order"] == order_name and item["sign"] == sign)
                        shape_rows.append({"graph": graph_name, "beta": beta, "delta": delta, "order": order_name, "sign": sign, "kms_residual": row["kms_residual"], "stationarity_defect": row["stationarity_defect"]})

    expected_rows = len(fixture["graphs"]) * len(beta_values) * len(deltas) * len(order_names) * len(signs)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("mesh coverage", len(mesh_rows) == len(fixture["graphs"]) * len(beta_values) * len(order_names) * len(signs), len(mesh_rows), "declared", "coverage")
    check("all finite", all(np.isfinite(row[key]) for row in rows for key in ("stationarity_defect", "kms_residual", "complex_inverse_error")), len(rows), "all finite", "numerics")
    max_kms = max(row["kms_residual"] for row in rows)
    max_stationarity = max(row["stationarity_defect"] for row in rows)
    min_kms = min(row["kms_residual"] for row in rows)
    min_stationarity = min(row["stationarity_defect"] for row in rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SPLIT-GIBBS-KMS-RESIDUAL",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "exact_rows": exact_rows,
        "rows": rows,
        "mesh_rows": mesh_rows,
        "shape_rows": shape_rows,
        "derived": {
            "row_count": len(rows),
            "exact_gibbs_kms_control_closed": True,
            "finite_split_stationarity_rows_closed": True,
            "finite_split_kms_residual_rows_closed": True,
            "mesh_decrease_diagnostic_closed": True,
            "path_exhaustion_diagnostic_closed": True,
            "min_kms_residual": min_kms,
            "max_kms_residual": max_kms,
            "min_stationarity_defect": min_stationarity,
            "max_stationarity_defect": max_stationarity,
            "volume_uniform_direct_d_cauchy_closed": False,
            "beta_uniform_direct_d_cauchy_closed": False,
            "modular_domain_transfer_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
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
    print(f"PRIMARY FINITE-SPLIT-GIBBS-KMS-RESIDUAL PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} max_kms={payload['derived']['max_kms_residual']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
