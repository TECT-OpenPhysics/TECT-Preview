#!/usr/bin/env python3
"""Independent source-wise reconstruction for EXP-001171.

No primary audit module is imported: the finite Q3 matrices, Gibbs state,
complex split inverse and all source-site residuals are rebuilt here.
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
SLUG = "pre-a-cp1-st8-q3lock-finite-split-gibbs-kms-source-stress"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def save_json(path: Path, payload: dict[str, Any]) -> None:
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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for j in range(size - 1):
        lowering[j, j + 1] = np.sqrt(float(j + 1))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def tensor_at(local: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result: np.ndarray | None = None
    for j in range(volume):
        factor = local if j == site else identity
        result = factor if result is None else np.kron(result, factor)
    assert result is not None
    return result


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def spectrum(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(sym(matrix))


def factor(values: np.ndarray, vectors: np.ndarray, z: complex, hbar: float) -> np.ndarray:
    return (vectors * np.exp((-1j / hbar) * z * values)) @ vectors.conj().T


def split_pair(spectra: list[tuple[np.ndarray, np.ndarray]], order: list[int], z: complex, hbar: float) -> tuple[np.ndarray, np.ndarray]:
    size = spectra[0][1].shape[0]
    forward = np.eye(size, dtype=complex)
    inverse = np.eye(size, dtype=complex)
    for index in order:
        values, vectors = spectra[index]
        forward = factor(values, vectors, z, hbar) @ forward
        inverse = inverse @ factor(values, vectors, -z, hbar)
    return forward, inverse


def density(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    weights = np.exp(-beta * (values - np.min(values)))
    weights /= np.sum(weights)
    return (vectors * weights) @ vectors.conj().T


def character(local: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = spectrum(local)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def graph_edges(graph: str) -> list[tuple[int, int]]:
    volume = int(graph[4:])
    return [(j, j + 1) for j in range(volume - 1)]


def make_terms(graph: str, size: int, params: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    volume = int(graph[4:])
    q, p = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q, j, volume, identity) for j in range(volume)]
    p_ops = [tensor_at(p, j, volume, identity) for j in range(volume)]
    chi, r, g = (float(Fraction(params[key])) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(params[key])) for key in ("c", "lambda"))
    terms = [p_op @ p_op / (2.0 * chi) + r * q_op @ q_op / 2.0 + g * q_op @ q_op @ q_op @ q_op / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    for left, right in graph_edges(graph):
        difference = q_ops[left] - q_ops[right]
        square = difference @ difference
        terms.append(c * square / 2.0 + lam * square @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
    return terms, q, p


def norm2(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def trace_norm(matrix: np.ndarray) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(sym(matrix)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001171" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001171/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and scope["common_alpha_closed"] is False, [manifest["claim_bearing"], scope["common_alpha_closed"]], "nonbearing/open", "scope")
    size = int(fixture["oscillator_dimension"])
    check("dimension", size == 3, size, 3, "nondegenerate d=3")
    check("sources", fixture["graphs"]["path4"]["source_sites"] == [0, 1, 2, 3] and fixture["graphs"]["path6"]["source_sites"] == [0, 1, 2, 3, 4, 5], fixture["graphs"], "all source sites", "fixture")
    betas = [float(x) for x in fixture["beta_values"]]
    deltas = [float(x) for x in fixture["delta_values"]]
    signs = [int(x) for x in fixture["time_signs"]]
    horizon = float(fixture["horizon"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    exact_tolerance = float(fixture["exact_kms_tolerance"])
    finite_tolerance = float(fixture["finite_tolerance"])
    product_tolerance = float(fixture["agreement_tolerance"])
    kms_floor = float(fixture["kms_witness_floor"])
    stationarity_floor = float(fixture["stationarity_witness_floor"])
    noncommutation_floor = float(fixture["noncommutation_witness_floor"])
    orders = ["onsite_then_lexicographic_bonds", "reverse_term_order"]
    rows: list[dict[str, Any]] = []
    exact_rows: list[dict[str, Any]] = []
    mesh_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    params = manifest["model_parameters"]

    for graph, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        declared_edges = [tuple(int(v) for v in edge) for edge in declaration["edges"]]
        check(f"{graph} edges", graph_edges(graph) == declared_edges, graph_edges(graph), declared_edges, "graph")
        terms, q_local, p_local = make_terms(graph, size, params)
        hamiltonian = sym(sum(terms, np.zeros_like(terms[0])))
        h_values, h_vectors = spectrum(hamiltonian)
        term_spectra = [spectrum(term) for term in terms]
        noncommutation = norm2(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
        check(f"{graph} noncommutation", noncommutation >= noncommutation_floor, noncommutation, f">={noncommutation_floor}", "nondegenerate Q3")
        identity = np.eye(size, dtype=complex)
        observables = {site: (tensor_at(character(q_local, amplitude, hbar), site, volume, identity), tensor_at(character(p_local, amplitude, hbar), site, volume, identity)) for site in declaration["source_sites"]}

        for beta in betas:
            rho = density(h_values, h_vectors, beta)
            for sign in signs:
                t = sign * horizon
                real = factor(h_values, h_vectors, t, hbar)
                real_inverse = factor(h_values, h_vectors, -t, hbar)
                z = t + 1j * beta * hbar
                imaginary = factor(h_values, h_vectors, z, hbar)
                imaginary_inverse = factor(h_values, h_vectors, -z, hbar)
                state_error = trace_norm(real @ rho @ real_inverse - rho)
                check(f"{graph} beta={beta} sign={sign} exact state", state_error <= exact_tolerance, state_error, f"<={exact_tolerance}", "exact Gibbs control")
                for site, (a_obs, b_obs) in observables.items():
                    kms_error = abs(np.trace(rho @ a_obs @ (real @ b_obs @ real_inverse)) - np.trace(rho @ (imaginary @ b_obs @ imaginary_inverse) @ a_obs))
                    check(f"{graph} site={site} beta={beta} sign={sign} exact KMS", kms_error <= exact_tolerance, kms_error, f"<={exact_tolerance}", "exact KMS control")
                    exact_rows.append({"graph": graph, "source_site": int(site), "beta": beta, "sign": sign, "stationarity_defect": state_error, "kms_residual": float(kms_error)})

        products: dict[tuple[str, float, int], tuple[np.ndarray, np.ndarray]] = {}
        for order_name in orders:
            order = list(range(len(terms))) if order_name == orders[0] else list(reversed(range(len(terms))))
            for delta in deltas:
                steps_float = horizon / delta
                steps = int(round(steps_float))
                check(f"{graph} {order_name} delta={delta} steps", abs(steps_float - steps) <= finite_tolerance and steps > 0, steps_float, steps, "mesh")
                for sign in signs:
                    step, step_inverse = split_pair(term_spectra, order, sign * delta, hbar)
                    real_product = np.linalg.matrix_power(step, steps)
                    real_inverse = np.linalg.matrix_power(step_inverse, steps)
                    inverse_error = norm2(real_product @ real_inverse - np.eye(real_product.shape[0], dtype=complex))
                    check(f"{graph} {order_name} delta={delta} sign={sign} inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "product algebra")
                    products[(order_name, delta, sign)] = (real_product, real_inverse)

        for beta in betas:
            rho = density(h_values, h_vectors, beta)
            for order_name in orders:
                order = list(range(len(terms))) if order_name == orders[0] else list(reversed(range(len(terms))))
                for delta in deltas:
                    steps = int(round(horizon / delta))
                    for sign in signs:
                        real_product, real_inverse = products[(order_name, delta, sign)]
                        complex_step, complex_step_inverse = split_pair(term_spectra, order, sign * delta + 1j * beta * hbar / steps, hbar)
                        complex_product = np.linalg.matrix_power(complex_step, steps)
                        complex_inverse = np.linalg.matrix_power(complex_step_inverse, steps)
                        inverse_error = norm2(complex_product @ complex_inverse - np.eye(complex_product.shape[0], dtype=complex))
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} complex inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "complex product algebra")
                        stationarity = trace_norm(real_product @ rho @ real_inverse - rho)
                        for site, (a_obs, b_obs) in observables.items():
                            kms = abs(np.trace(rho @ a_obs @ (real_product @ b_obs @ real_inverse)) - np.trace(rho @ (complex_product @ b_obs @ complex_inverse) @ a_obs))
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} finite", np.isfinite(stationarity) and np.isfinite(kms), [stationarity, kms], "finite", "source rows")
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} KMS witness", kms >= kms_floor, kms, f">={kms_floor}", "split not exact KMS")
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} state witness", stationarity >= stationarity_floor, stationarity, f">={stationarity_floor}", "split not exact stationary")
                            rows.append({"graph": graph, "volume": volume, "source_site": int(site), "beta": beta, "delta": delta, "steps": steps, "sign": sign, "order": order_name, "stationarity_defect": stationarity, "kms_residual": float(kms), "complex_inverse_error": inverse_error})

        for site in declaration["source_sites"]:
            site = int(site)
            for beta in betas:
                for order_name in orders:
                    for sign in signs:
                        coarse = next(item for item in rows if item["graph"] == graph and item["source_site"] == site and item["beta"] == beta and item["delta"] == deltas[0] and item["order"] == order_name and item["sign"] == sign)
                        fine = next(item for item in rows if item["graph"] == graph and item["source_site"] == site and item["beta"] == beta and item["delta"] == deltas[-1] and item["order"] == order_name and item["sign"] == sign)
                        check(f"{graph} site={site} {order_name} beta={beta} sign={sign} KMS decrease", fine["kms_residual"] <= coarse["kms_residual"] + finite_tolerance, [coarse["kms_residual"], fine["kms_residual"]], "fine<=coarse+tolerance", "mesh trend")
                        check(f"{graph} site={site} {order_name} beta={beta} sign={sign} state decrease", fine["stationarity_defect"] <= coarse["stationarity_defect"] + finite_tolerance, [coarse["stationarity_defect"], fine["stationarity_defect"]], "fine<=coarse+tolerance", "mesh trend")
                        mesh_rows.append({"graph": graph, "source_site": site, "beta": beta, "order": order_name, "sign": sign, "coarse_delta": deltas[0], "fine_delta": deltas[-1], "kms_ratio": fine["kms_residual"] / max(coarse["kms_residual"], np.finfo(float).tiny), "stationarity_ratio": fine["stationarity_defect"] / max(coarse["stationarity_defect"], np.finfo(float).tiny)})
            source_rows = [item for item in rows if item["graph"] == graph and item["source_site"] == site]
            source_summaries.append({"graph": graph, "source_site": site, "max_kms_residual": max(item["kms_residual"] for item in source_rows), "max_stationarity_defect": max(item["stationarity_defect"] for item in source_rows), "min_kms_residual": min(item["kms_residual"] for item in source_rows), "min_stationarity_defect": min(item["stationarity_defect"] for item in source_rows)})

    source_count = sum(len(declaration["source_sites"]) for declaration in fixture["graphs"].values())
    expected_rows = source_count * len(betas) * len(deltas) * len(orders) * len(signs)
    expected_exact = source_count * len(betas) * len(signs)
    expected_mesh = source_count * len(betas) * len(orders) * len(signs)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("exact coverage", len(exact_rows) == expected_exact, len(exact_rows), expected_exact, "coverage")
    check("mesh coverage", len(mesh_rows) == expected_mesh, len(mesh_rows), expected_mesh, "coverage")
    check("source summary coverage", len(source_summaries) == source_count, len(source_summaries), source_count, "coverage")
    check("finite outputs", all(np.isfinite(row[key]) for row in rows for key in ("stationarity_defect", "kms_residual", "complex_inverse_error")), len(rows), "all finite", "numerics")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SPLIT-GIBBS-KMS-SOURCE-STRESS",
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
        "source_summaries": source_summaries,
        "derived": {
            "row_count": len(rows),
            "source_count": len(source_summaries),
            "exact_gibbs_kms_control_closed": True,
            "finite_source_stationarity_rows_closed": True,
            "finite_source_kms_residual_rows_closed": True,
            "source_uniformity_diagnostic_closed": True,
            "mesh_decrease_diagnostic_closed": True,
            "path_exhaustion_diagnostic_closed": True,
            "min_kms_residual": min(row["kms_residual"] for row in rows),
            "max_kms_residual": max(row["kms_residual"] for row in rows),
            "min_stationarity_defect": min(row["stationarity_defect"] for row in rows),
            "max_stationarity_defect": max(row["stationarity_defect"] for row in rows),
            "source_uniform_direct_d_cauchy_closed": False,
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
    print(f"INDEPENDENT FINITE-SPLIT-GIBBS-KMS-SOURCE-STRESS PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} sources={payload['derived']['source_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
