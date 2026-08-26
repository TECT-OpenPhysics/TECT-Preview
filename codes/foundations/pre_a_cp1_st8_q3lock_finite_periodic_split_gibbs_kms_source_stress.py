#!/usr/bin/env python3
"""Primary finite periodic-control Q3 Gibbs/KMS source and shape audit for EXP-001172.

This is a bounded d=3 matrix diagnostic on the manifest's bond2, square4 and
grid2x3 controls.  It keeps the thermodynamic, common-core and OS/KMS
identification obligations explicitly open.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-periodic-split-gibbs-kms-source-stress"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_split_gibbs_kms_residual as base  # noqa: E402


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


def trace_norm(matrix: np.ndarray) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(base.hermitian(matrix)))))


def periodic_terms(edges: list[tuple[int, int]], volume: int, dimension: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = base.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [base.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [base.embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [base.bond_term(q_ops[left], q_ops[right], parameters) for left, right in edges]
    return onsite + bonds, q_single, p_single


def edge_checks(declaration: dict[str, Any], volume: int) -> tuple[list[tuple[int, int]], list[int], int, int, float]:
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    sources = [int(value) for value in declaration["source_sites"]]
    canonical = [(min(left, right), max(left, right)) for left, right in edges]
    if any(left == right or left < 0 or right >= volume for left, right in edges):
        raise AssertionError(f"invalid edge set: {edges!r}")
    if len(set(canonical)) != len(canonical):
        raise AssertionError(f"duplicate edge set: {edges!r}")
    if sources != list(range(volume)):
        raise AssertionError(f"source coverage: {sources!r} != {list(range(volume))!r}")
    degrees = [0] * volume
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
    return edges, sources, min(degrees), max(degrees), float(sum(degrees) / volume)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001172" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001172/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("periodic graph fixture", list(fixture["graphs"]) == ["bond2", "square4", "grid2x3"], list(fixture["graphs"]), "bond2/square4/grid2x3", "fixture")
    check("dimension fixture", int(fixture["oscillator_dimension"]) == 3, fixture["oscillator_dimension"], 3, "nondegenerate d=3")
    check("source coverage fixture", all(declaration["source_sites"] == list(range(int(declaration["vertices"]))) for declaration in fixture["graphs"].values()), fixture["graphs"], "all finite sites", "fixture")
    check("scope firewall", scope["finite_exact_gibbs_control_closed"] and scope["finite_periodic_source_stationarity_rows_closed"] and scope["finite_periodic_source_kms_residual_rows_closed"] and scope["source_uniformity_diagnostic_closed"] and scope["shape_degree_diagnostic_closed"] and not scope["source_uniform_direct_d_cauchy_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite periodic diagnostic", "scope")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    deltas = [float(value) for value in fixture["delta_values"]]
    horizon = float(fixture["horizon"])
    signs = [int(value) for value in fixture["time_signs"]]
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    exact_tolerance = float(fixture["exact_kms_tolerance"])
    finite_tolerance = float(fixture["finite_tolerance"])
    product_tolerance = float(fixture["agreement_tolerance"])
    kms_floor = float(fixture["kms_witness_floor"])
    stationarity_floor = float(fixture["stationarity_witness_floor"])
    noncommutation_floor = float(fixture["noncommutation_witness_floor"])
    order_names = ["onsite_then_manifest_bonds", "reverse_term_order"]
    parameters = manifest["model_parameters"]
    rows: list[dict[str, Any]] = []
    exact_rows: list[dict[str, Any]] = []
    mesh_rows: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    shape_summaries: list[dict[str, Any]] = []

    for graph, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        edges, source_sites, degree_min, degree_max, degree_mean = edge_checks(declaration, volume)
        check(f"{graph} edge validity", len(edges) > 0 and degree_min > 0, {"edges": edges, "degree_min": degree_min, "degree_max": degree_max}, "nonempty connected-control candidate", "graph")
        terms, q_single, p_single = periodic_terms(edges, volume, dimension, parameters)
        hamiltonian = base.hermitian(sum(terms, np.zeros_like(terms[0])))
        h_values, h_vectors = base.eigensystem(hamiltonian)
        term_caches = [base.eigensystem(term) for term in terms]
        noncommutation = base.operator_norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
        check(f"{graph} noncommutation", noncommutation >= noncommutation_floor, noncommutation, f">={noncommutation_floor}", "nondegenerate Q3")
        identity = np.eye(dimension, dtype=complex)
        observables = {
            site: (
                base.embed(base.character(q_single, amplitude, hbar), site, volume, identity),
                base.embed(base.character(p_single, amplitude, hbar), site, volume, identity),
            )
            for site in source_sites
        }

        for beta in beta_values:
            rho = base.gibbs(h_values, h_vectors, beta)
            for sign in signs:
                real_z = sign * horizon
                exact_real = base.spectral_factor(h_values, h_vectors, real_z, hbar)
                exact_real_inverse = base.spectral_factor(h_values, h_vectors, -real_z, hbar)
                complex_z = real_z + 1j * beta * hbar
                exact_complex = base.spectral_factor(h_values, h_vectors, complex_z, hbar)
                exact_complex_inverse = base.spectral_factor(h_values, h_vectors, -complex_z, hbar)
                exact_state = trace_norm(exact_real @ rho @ exact_real_inverse - rho)
                check(f"{graph} beta={beta} sign={sign} exact state", exact_state <= exact_tolerance, exact_state, f"<={exact_tolerance}", "exact Gibbs control")
                for site, (observable_a, observable_b) in observables.items():
                    exact_kms = abs(np.trace(rho @ observable_a @ (exact_real @ observable_b @ exact_real_inverse)) - np.trace(rho @ (exact_complex @ observable_b @ exact_complex_inverse) @ observable_a))
                    check(f"{graph} site={site} beta={beta} sign={sign} exact KMS", exact_kms <= exact_tolerance, exact_kms, f"<={exact_tolerance}", "exact KMS control")
                    exact_rows.append({"graph": graph, "source_site": site, "beta": beta, "sign": sign, "stationarity_defect": exact_state, "kms_residual": float(exact_kms)})

        real_products: dict[tuple[str, float, int], tuple[np.ndarray, np.ndarray]] = {}
        for order_name in order_names:
            order = base.order_indices(order_name.replace("manifest_bonds", "lexicographic_bonds"), len(terms)) if order_name == order_names[0] else list(reversed(range(len(terms))))
            for delta in deltas:
                steps_float = horizon / delta
                steps = int(round(steps_float))
                check(f"{graph} {order_name} delta={delta} steps", abs(steps_float - steps) <= finite_tolerance and steps > 0, steps_float, steps, "mesh")
                for sign in signs:
                    one_step, one_inverse = base.product_pair(term_caches, order, sign * delta, hbar)
                    real_product = np.linalg.matrix_power(one_step, steps)
                    real_inverse = np.linalg.matrix_power(one_inverse, steps)
                    inverse_error = base.operator_norm(real_product @ real_inverse - np.eye(real_product.shape[0], dtype=complex))
                    check(f"{graph} {order_name} delta={delta} sign={sign} real inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "product algebra")
                    real_products[(order_name, delta, sign)] = (real_product, real_inverse)

        for beta in beta_values:
            rho = base.gibbs(h_values, h_vectors, beta)
            for order_name in order_names:
                order = base.order_indices("onsite_then_lexicographic_bonds", len(terms)) if order_name == order_names[0] else list(reversed(range(len(terms))))
                for delta in deltas:
                    steps = int(round(horizon / delta))
                    for sign in signs:
                        real_product, real_inverse = real_products[(order_name, delta, sign)]
                        complex_step, complex_inverse_step = base.product_pair(term_caches, order, sign * delta + 1j * beta * hbar / steps, hbar)
                        complex_product = np.linalg.matrix_power(complex_step, steps)
                        complex_inverse = np.linalg.matrix_power(complex_inverse_step, steps)
                        inverse_error = base.operator_norm(complex_product @ complex_inverse - np.eye(complex_product.shape[0], dtype=complex))
                        check(f"{graph} {order_name} beta={beta} delta={delta} sign={sign} complex inverse", inverse_error <= product_tolerance, inverse_error, f"<={product_tolerance}", "complex product algebra")
                        stationarity = trace_norm(real_product @ rho @ real_inverse - rho)
                        for site, (observable_a, observable_b) in observables.items():
                            evolved_b = real_product @ observable_b @ real_inverse
                            shifted_b = complex_product @ observable_b @ complex_inverse
                            kms_residual = abs(np.trace(rho @ observable_a @ evolved_b) - np.trace(rho @ shifted_b @ observable_a))
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} finite", np.isfinite(stationarity) and np.isfinite(kms_residual), [stationarity, kms_residual], "finite", "source rows")
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} KMS witness", kms_residual >= kms_floor, kms_residual, f">={kms_floor}", "split not exact KMS")
                            check(f"{graph} site={site} {order_name} beta={beta} delta={delta} sign={sign} state witness", stationarity >= stationarity_floor, stationarity, f">={stationarity_floor}", "split not exact stationary")
                            rows.append({"graph": graph, "volume": volume, "edge_count": len(edges), "source_site": site, "degree": sum(site in edge for edge in edges), "beta": beta, "delta": delta, "steps": steps, "sign": sign, "order": order_name, "stationarity_defect": stationarity, "kms_residual": float(kms_residual), "complex_inverse_error": inverse_error})

        for site in source_sites:
            for beta in beta_values:
                for order_name in order_names:
                    for sign in signs:
                        coarse = next(item for item in rows if item["graph"] == graph and item["source_site"] == site and item["beta"] == beta and item["delta"] == deltas[0] and item["order"] == order_name and item["sign"] == sign)
                        fine = next(item for item in rows if item["graph"] == graph and item["source_site"] == site and item["beta"] == beta and item["delta"] == deltas[-1] and item["order"] == order_name and item["sign"] == sign)
                        check(f"{graph} site={site} {order_name} beta={beta} sign={sign} KMS mesh decrease", fine["kms_residual"] <= coarse["kms_residual"] + finite_tolerance, [coarse["kms_residual"], fine["kms_residual"]], "fine<=coarse+tolerance", "mesh trend")
                        check(f"{graph} site={site} {order_name} beta={beta} sign={sign} state mesh decrease", fine["stationarity_defect"] <= coarse["stationarity_defect"] + finite_tolerance, [coarse["stationarity_defect"], fine["stationarity_defect"]], "fine<=coarse+tolerance", "mesh trend")
                        mesh_rows.append({"graph": graph, "source_site": site, "beta": beta, "order": order_name, "sign": sign, "coarse_delta": deltas[0], "fine_delta": deltas[-1], "kms_ratio": fine["kms_residual"] / max(coarse["kms_residual"], np.finfo(float).tiny), "stationarity_ratio": fine["stationarity_defect"] / max(coarse["stationarity_defect"], np.finfo(float).tiny)})
            source_rows = [item for item in rows if item["graph"] == graph and item["source_site"] == site]
            source_summaries.append({"graph": graph, "source_site": site, "degree": sum(site in edge for edge in edges), "max_kms_residual": max(item["kms_residual"] for item in source_rows), "max_stationarity_defect": max(item["stationarity_defect"] for item in source_rows), "min_kms_residual": min(item["kms_residual"] for item in source_rows), "min_stationarity_defect": min(item["stationarity_defect"] for item in source_rows)})

        shape_rows = [item for item in rows if item["graph"] == graph]
        shape_summaries.append({"graph": graph, "volume": volume, "edge_count": len(edges), "degree_min": degree_min, "degree_max": degree_max, "degree_mean": degree_mean, "source_count": len(source_sites), "max_kms_residual": max(item["kms_residual"] for item in shape_rows), "min_kms_residual": min(item["kms_residual"] for item in shape_rows), "max_stationarity_defect": max(item["stationarity_defect"] for item in shape_rows), "min_stationarity_defect": min(item["stationarity_defect"] for item in shape_rows)})

    source_count = sum(len(declaration["source_sites"]) for declaration in fixture["graphs"].values())
    expected_rows = source_count * len(beta_values) * len(deltas) * len(order_names) * len(signs)
    expected_exact = source_count * len(beta_values) * len(signs)
    expected_mesh = source_count * len(beta_values) * len(order_names) * len(signs)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("exact coverage", len(exact_rows) == expected_exact, len(exact_rows), expected_exact, "coverage")
    check("mesh coverage", len(mesh_rows) == expected_mesh, len(mesh_rows), expected_mesh, "coverage")
    check("source summary coverage", len(source_summaries) == source_count, len(source_summaries), source_count, "coverage")
    check("shape summary coverage", len(shape_summaries) == len(fixture["graphs"]), len(shape_summaries), len(fixture["graphs"]), "coverage")
    check("all finite", all(np.isfinite(row[key]) for row in rows for key in ("stationarity_defect", "kms_residual", "complex_inverse_error")), len(rows), "all finite", "numerics")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-PERIODIC-SPLIT-GIBBS-KMS-SOURCE-STRESS",
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
        "shape_summaries": shape_summaries,
        "derived": {
            "row_count": len(rows),
            "source_count": len(source_summaries),
            "shape_count": len(shape_summaries),
            "exact_gibbs_kms_control_closed": True,
            "finite_periodic_source_stationarity_rows_closed": True,
            "finite_periodic_source_kms_residual_rows_closed": True,
            "source_uniformity_diagnostic_closed": True,
            "shape_degree_diagnostic_closed": True,
            "mesh_decrease_diagnostic_closed": True,
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
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-PERIODIC-SPLIT-GIBBS-KMS-SOURCE-STRESS PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} sources={payload['derived']['source_count']} shapes={payload['derived']['shape_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
