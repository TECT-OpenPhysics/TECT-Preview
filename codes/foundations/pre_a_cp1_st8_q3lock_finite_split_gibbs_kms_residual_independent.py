#!/usr/bin/env python3
"""Independent reconstruction of the EXP-001170 finite Q3 KMS audit.

This lane deliberately does not import the primary implementation.  It uses
the same manifest and finite fixture but rebuilds all tensor matrices,
spectral products and residuals independently.
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


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre-a-cp1-st8-q3lock-finite-split-gibbs-kms-residual"
MANIFEST = ROOT / f"strategy/{NAME}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{NAME}" / "independent.json"


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((size, size), dtype=complex)
    for j in range(size - 1):
        a[j, j + 1] = np.sqrt(float(j + 1))
    adag = a.conj().T
    return (a + adag) / np.sqrt(2.0), (a - adag) / (1j * np.sqrt(2.0))


def tensor_at(local: np.ndarray, site: int, volume: int, ident: np.ndarray) -> np.ndarray:
    result = None
    for j in range(volume):
        factor = local if j == site else ident
        result = factor if result is None else np.kron(result, factor)
    return result


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def spectrum(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(sym(matrix))


def exp_factor(values: np.ndarray, vectors: np.ndarray, z: complex, hbar: float) -> np.ndarray:
    phase = np.exp((-1j / hbar) * z * values)
    return (vectors * phase) @ vectors.conj().T


def split_with_inverse(spectra: list[tuple[np.ndarray, np.ndarray]], order: list[int], z: complex, hbar: float) -> tuple[np.ndarray, np.ndarray]:
    size = spectra[0][1].shape[0]
    forward = np.eye(size, dtype=complex)
    backward = np.eye(size, dtype=complex)
    for j in order:
        values, vectors = spectra[j]
        forward = exp_factor(values, vectors, z, hbar) @ forward
        backward = backward @ exp_factor(values, vectors, -z, hbar)
    return forward, backward


def density(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    shifted = values - np.min(values)
    weights = np.exp(-beta * shifted)
    weights = weights / np.sum(weights)
    return (vectors * weights) @ vectors.conj().T


def character(local: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = spectrum(local)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def edges(graph: str) -> list[tuple[int, int]]:
    number = int(graph[4:])
    return [(j, j + 1) for j in range(number - 1)]


def make_terms(graph: str, size: int, params: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    volume = int(graph[4:])
    q, p = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q, j, volume, identity) for j in range(volume)]
    p_ops = [tensor_at(p, j, volume, identity) for j in range(volume)]
    chi, r, g = (float(Fraction(params[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(params[key])) for key in ("c", "lambda"))
    terms = [p_op @ p_op / (2.0 * chi) + r * q_op @ q_op / 2.0 + g * q_op @ q_op @ q_op @ q_op / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    for left, right in edges(graph):
        difference = q_ops[left] - q_ops[right]
        square = difference @ difference
        terms.append(c * square / 2.0 + lam * square @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
    return terms, q, p


def norm2(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def hermitian_trace_norm(matrix: np.ndarray) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(sym(matrix)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001170" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001170/T-054", "provenance")
    check("independent claim firewall", manifest["claim_bearing"] is False and not scope["common_alpha_closed"], [manifest["claim_bearing"], scope["common_alpha_closed"]], "nonbearing/open", "scope")
    size = int(fixture["oscillator_dimension"])
    check("nondegenerate dimension", size == 3, size, 3, "fixture")
    betas = [float(x) for x in fixture["beta_values"]]
    deltas = [float(x) for x in fixture["delta_values"]]
    signs = [int(x) for x in fixture["time_signs"]]
    horizon = float(fixture["horizon"])
    hbar = float(fixture["hbar"])
    beta_tolerance = float(fixture["exact_kms_tolerance"])
    numerical_tolerance = float(fixture["finite_tolerance"])
    product_tolerance = float(fixture["agreement_tolerance"])
    kms_floor = float(fixture["kms_witness_floor"])
    stationarity_floor = float(fixture["stationarity_witness_floor"])
    noncommutation_floor = float(fixture["noncommutation_witness_floor"])
    orders = ["onsite_then_lexicographic_bonds", "reverse_term_order"]
    rows: list[dict[str, Any]] = []
    exact_rows: list[dict[str, Any]] = []
    mesh_rows: list[dict[str, Any]] = []
    shape_rows: list[dict[str, Any]] = []
    params = manifest["model_parameters"]

    for graph, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        expected_edges = [tuple(int(v) for v in edge) for edge in declaration["edges"]]
        check(f"{graph} edges", edges(graph) == expected_edges, edges(graph), expected_edges, "graph")
        terms, q_local, p_local = make_terms(graph, size, params)
        hamiltonian = sym(sum(terms, np.zeros_like(terms[0])))
        h_values, h_vectors = spectrum(hamiltonian)
        term_spectra = [spectrum(term) for term in terms]
        noncommutation = norm2(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
        check(f"{graph} noncommutation", noncommutation >= noncommutation_floor, noncommutation, f">={noncommutation_floor}", "nondegenerate Q3")
        ident = np.eye(size, dtype=complex)
        observable_a = tensor_at(character(q_local, float(fixture["character_amplitude"]), hbar), int(fixture["source_site"]), volume, ident)
        observable_b = tensor_at(character(p_local, float(fixture["character_amplitude"]), hbar), int(fixture["source_site"]), volume, ident)
        exact_controls: dict[tuple[float, int], dict[str, float]] = {}
        for beta in betas:
            rho = density(h_values, h_vectors, beta)
            for sign in signs:
                t = sign * horizon
                real = exp_factor(h_values, h_vectors, t, hbar)
                real_inverse = exp_factor(h_values, h_vectors, -t, hbar)
                z = t + 1j * beta * hbar
                complex_orbit = exp_factor(h_values, h_vectors, z, hbar)
                complex_inverse = exp_factor(h_values, h_vectors, -z, hbar)
                state_error = hermitian_trace_norm(real @ rho @ real_inverse - rho)
                kms_error = abs(np.trace(rho @ observable_a @ (real @ observable_b @ real_inverse)) - np.trace(rho @ (complex_orbit @ observable_b @ complex_inverse) @ observable_a))
                check(f"{graph} beta={beta} sign={sign} exact state", state_error <= beta_tolerance, state_error, f"<={beta_tolerance}", "exact Gibbs control")
                check(f"{graph} beta={beta} sign={sign} exact KMS", kms_error <= beta_tolerance, kms_error, f"<={beta_tolerance}", "exact KMS control")
                exact_controls[(beta, sign)] = {"stationarity": state_error, "kms": float(kms_error)}
                exact_rows.append({"graph": graph, "beta": beta, "sign": sign, "stationarity_defect": state_error, "kms_residual": float(kms_error)})

        real_products: dict[tuple[str, float, int], tuple[np.ndarray, np.ndarray]] = {}
        for order_name in orders:
            order = list(range(len(terms))) if order_name == orders[0] else list(reversed(range(len(terms))))
            for delta in deltas:
                steps_float = horizon / delta
                steps = int(round(steps_float))
                check(f"{graph} {order_name} delta={delta} steps", abs(steps_float - steps) <= numerical_tolerance and steps > 0, steps_float, steps, "mesh")
                for sign in signs:
                    step, step_inverse = split_with_inverse(term_spectra, order, sign * delta, hbar)
                    real_product = np.linalg.matrix_power(step, steps)
                    real_inverse = np.linalg.matrix_power(step_inverse, steps)
                    inverse_error = norm2(real_product @ real_inverse - np.eye(real_product.shape[0], dtype=complex))
                    check(f"{graph} {order_name} delta={delta} sign={sign} inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "product algebra")
                    real_products[(order_name, delta, sign)] = (real_product, real_inverse)

        for beta in betas:
            rho = density(h_values, h_vectors, beta)
            for order_name in orders:
                order = list(range(len(terms))) if order_name == orders[0] else list(reversed(range(len(terms))))
                for delta in deltas:
                    steps = int(round(horizon / delta))
                    for sign in signs:
                        real_product, real_inverse = real_products[(order_name, delta, sign)]
                        complex_step, complex_step_inverse = split_with_inverse(term_spectra, order, sign * delta + 1j * beta * hbar / steps, hbar)
                        complex_product = np.linalg.matrix_power(complex_step, steps)
                        complex_inverse = np.linalg.matrix_power(complex_step_inverse, steps)
                        inverse_error = norm2(complex_product @ complex_inverse - np.eye(complex_product.shape[0], dtype=complex))
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} complex inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "complex product algebra")
                        evolved_b = real_product @ observable_b @ real_inverse
                        shifted_b = complex_product @ observable_b @ complex_inverse
                        stationarity = hermitian_trace_norm(real_product @ rho @ real_inverse - rho)
                        kms = abs(np.trace(rho @ observable_a @ evolved_b) - np.trace(rho @ shifted_b @ observable_a))
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} finite", np.isfinite(stationarity) and np.isfinite(kms), [stationarity, kms], "finite", "split rows")
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} KMS witness", kms >= kms_floor, kms, f">={kms_floor}", "split not exact KMS")
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} state witness", stationarity >= stationarity_floor, stationarity, f">={stationarity_floor}", "split not exact stationary")
                        rows.append({"graph": graph, "volume": volume, "beta": beta, "delta": delta, "steps": steps, "sign": sign, "order": order_name, "stationarity_defect": stationarity, "kms_residual": float(kms), "complex_inverse_error": inverse_error})

        for beta in betas:
            for order_name in orders:
                for sign in signs:
                    coarse = next(item for item in rows if item["graph"] == graph and item["beta"] == beta and item["delta"] == deltas[0] and item["order"] == order_name and item["sign"] == sign)
                    fine = next(item for item in rows if item["graph"] == graph and item["beta"] == beta and item["delta"] == deltas[-1] and item["order"] == order_name and item["sign"] == sign)
                    check(f"{graph} {order_name} beta={beta} sign={sign} KMS decrease", fine["kms_residual"] <= coarse["kms_residual"] + numerical_tolerance, [coarse["kms_residual"], fine["kms_residual"]], "fine<=coarse+tolerance", "mesh trend")
                    check(f"{graph} {order_name} beta={beta} sign={sign} state decrease", fine["stationarity_defect"] <= coarse["stationarity_defect"] + numerical_tolerance, [coarse["stationarity_defect"], fine["stationarity_defect"]], "fine<=coarse+tolerance", "mesh trend")
                    mesh_rows.append({"graph": graph, "beta": beta, "order": order_name, "sign": sign, "coarse_delta": deltas[0], "fine_delta": deltas[-1], "kms_ratio": fine["kms_residual"] / max(coarse["kms_residual"], np.finfo(float).tiny), "stationarity_ratio": fine["stationarity_defect"] / max(coarse["stationarity_defect"], np.finfo(float).tiny)})
        for row in rows:
            if row["graph"] == graph:
                shape_rows.append({key: row[key] for key in ("graph", "beta", "delta", "order", "sign", "kms_residual", "stationarity_defect")})

    expected = len(fixture["graphs"]) * len(betas) * len(deltas) * len(orders) * len(signs)
    check("row coverage", len(rows) == expected, len(rows), expected, "coverage")
    check("mesh coverage", len(mesh_rows) == len(fixture["graphs"]) * len(betas) * len(orders) * len(signs), len(mesh_rows), "declared", "coverage")
    check("finite outputs", all(np.isfinite(row[key]) for row in rows for key in ("stationarity_defect", "kms_residual", "complex_inverse_error")), len(rows), "all finite", "numerics")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
            "min_kms_residual": min(row["kms_residual"] for row in rows),
            "max_kms_residual": max(row["kms_residual"] for row in rows),
            "min_stationarity_defect": min(row["stationarity_defect"] for row in rows),
            "max_stationarity_defect": max(row["stationarity_defect"] for row in rows),
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
        save_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT FINITE-SPLIT-GIBBS-KMS-RESIDUAL PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} max_kms={payload['derived']['max_kms_residual']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
