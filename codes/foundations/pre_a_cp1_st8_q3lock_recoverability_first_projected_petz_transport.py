#!/usr/bin/env python3
"""Finite recoverability-first projected Petz transport (R-396)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-recoverability-first-projected-petz-transport-manifest.json"
PARENT_PATH = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "primary.json"


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("r391_parent", PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-391 finite Petz model")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()


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


def trace_distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(PARENT.hermitian(left - right)).real)))


def petz_fast(input_ab: np.ndarray, reference_bc: np.ndarray, reference_b: np.ndarray, dimensions: tuple[int, int, int], tolerance: float) -> np.ndarray:
    """Vectorised form of the block Petz map used by R-391."""
    d_a, d_b, d_c = dimensions
    sqrt_bc = PARENT.spectral_power(reference_bc, 0.5, tolerance)
    inverse_sqrt_b = PARENT.spectral_power(reference_b, -0.5, tolerance)
    dressed = np.kron(np.eye(d_a, dtype=complex), inverse_sqrt_b) @ input_ab @ np.kron(np.eye(d_a, dtype=complex), inverse_sqrt_b)
    source = dressed.reshape(d_a, d_b, d_a, d_b)
    kernel = sqrt_bc.reshape(d_b, d_c, d_b, d_c)
    recovered = np.einsum("bcuv,auAx,xvBC->abcABC", kernel, source, kernel, optimize=True)
    return PARENT.hermitian(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def cutoff_profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["buffer_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row["transported_error"]))
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = [{"dimension": dimension, "count": len(values), "transported_error_maximum": max(values)} for dimension, values in sorted(by_dimension.items())]
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["transported_error_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "transported_error_ratio": float(right["transported_error_maximum"]) / denominator if denominator > tolerance else 0.0})
        values = [value for group in by_dimension.values() for value in group]
        records.append({"key": list(key), "dimensions": dimensions, "transported_error_minimum": min(values), "transported_error_maximum": max(values), "adjacent_ratios": ratios, "maximum_adjacent_transport_ratio": max((item["transported_error_ratio"] for item in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_adjacent_transport_ratio": max((item["maximum_adjacent_transport_ratio"] for item in records), default=0.0)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001239" and manifest["result_id"] == "R-396" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001239/R-396/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all projected Petz transport rows", "coverage")
    finite_flags = ("finite_projected_state_normalization_closed", "finite_petz_recovery_closed", "finite_recovery_contractivity_closed", "finite_triangle_transport_closed", "finite_cutoff_transport_profile_closed", "finite_hostile_budget_mutation_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite recoverability transport only", "all promoted flags false", "scope")
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct systems", "fixture")
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    energies = [float(Fraction(value)) for value in fixture["energy_windows"]]
    widths = [int(value) for value in fixture["core_widths"]]
    buffers = [int(value) for value in fixture["buffer_widths"]]
    rows: list[dict[str, Any]] = []
    delta_abc_values: list[float] = []
    delta_ab_values: list[float] = []
    projected_errors: list[float] = []
    transported_errors: list[float] = []
    budgets: list[float] = []
    contractivity_failures = 0
    triangle_failures = 0
    two_delta_failures = 0
    normalization_failures = 0
    partition_count = 0
    for volume, dimension in pairs:
        values, vectors = np.linalg.eigh(PARENT.build_system(dimension, volume, fixture))
        projectors = {}
        for width in widths:
            local_values, local_vectors = np.linalg.eigh(PARENT.build_system(dimension, width, fixture))
            local_minimum = float(local_values.min())
            shifted = local_values - local_minimum
            projectors[width] = {}
            for energy in energies:
                mask = shifted <= energy + positivity_tolerance
                projectors[width][energy] = PARENT.hermitian(local_vectors[:, mask] @ local_vectors[:, mask].conj().T)
        partitions = PARENT.tripartitions(volume, widths, buffers)
        partition_count += len(partitions)
        states = {beta: PARENT.gibbs_from_spectrum(values, vectors, beta) for beta in betas}
        for beta in betas:
            state = states[beta]
            for partition in partitions:
                core, buffer, environment = partition["core"], partition["buffer"], partition["environment"]
                core_width, buffer_width = int(partition["core_width"]), int(partition["buffer_width"])
                dimensions = (dimension**len(core), dimension**len(buffer), dimension**len(environment))
                abc_sites = core + buffer + environment
                rho_abc = PARENT.partial_trace_sites(state, dimension, volume, abc_sites)
                rho_ab = PARENT.partial_trace_groups(rho_abc, list(dimensions), [0, 1])
                for energy in energies:
                    projector = projectors[core_width][energy]
                    identity_bc = np.eye(dimensions[1] * dimensions[2], dtype=complex)
                    lifted = np.kron(projector, identity_bc)
                    projected_unnormalised = PARENT.hermitian(lifted @ rho_abc @ lifted)
                    mass = float(np.trace(projected_unnormalised).real)
                    normalization_failures += int(not (mass > tolerance and mass <= 1.0 + tolerance))
                    sigma_abc = PARENT.hermitian(projected_unnormalised / mass)
                    sigma_ab = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [0, 1])
                    sigma_b = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [1])
                    sigma_bc = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [1, 2])
                    recovered_sigma = petz_fast(sigma_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    recovered_rho = petz_fast(rho_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    delta_abc = trace_distance(rho_abc, sigma_abc)
                    delta_ab = trace_distance(rho_ab, sigma_ab)
                    projected_error = trace_distance(sigma_abc, recovered_sigma)
                    transported_error = trace_distance(rho_abc, recovered_rho)
                    recovered_input_distance = trace_distance(recovered_rho, recovered_sigma)
                    budget = projected_error + delta_abc + delta_ab
                    two_delta_budget = projected_error + 2.0 * delta_abc
                    contractivity_gap = recovered_input_distance - delta_ab
                    recovered_sigma_trace = float(np.trace(recovered_sigma).real)
                    recovered_rho_trace = float(np.trace(recovered_rho).real)
                    recovered_min_eigenvalue = min(float(np.min(np.linalg.eigvalsh(recovered_sigma)).real), float(np.min(np.linalg.eigvalsh(recovered_rho)).real))
                    contractivity_failures += int(recovered_input_distance > delta_ab + tolerance)
                    triangle_failures += int(transported_error > budget + tolerance)
                    two_delta_failures += int(transported_error > two_delta_budget + tolerance)
                    delta_abc_values.append(delta_abc)
                    delta_ab_values.append(delta_ab)
                    projected_errors.append(projected_error)
                    transported_errors.append(transported_error)
                    budgets.append(budget)
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} normalization", mass > tolerance and abs(float(np.trace(sigma_abc).real) - 1.0) <= tolerance and -tolerance <= mass <= 1.0 + tolerance, [mass, float(np.trace(sigma_abc).real)], "positive mass and unit trace", "projection")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} distances", all(np.isfinite(value) and value >= -tolerance for value in (delta_abc, delta_ab, projected_error, transported_error, recovered_input_distance)), [delta_abc, delta_ab, projected_error, transported_error, recovered_input_distance], "finite nonnegative distances", "distance")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} contraction", recovered_input_distance <= delta_ab + tolerance and delta_ab <= delta_abc + tolerance, [recovered_input_distance, delta_ab, delta_abc], "recovery contraction and partial-trace contraction", "contractivity")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} recovery", recovered_sigma_trace >= 1.0 - tolerance and recovered_rho_trace >= 1.0 - tolerance and recovered_min_eigenvalue >= -positivity_tolerance, [recovered_sigma_trace, recovered_rho_trace, recovered_min_eigenvalue], "trace-one positive recovered states", "Petz")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} triangle", transported_error <= budget + tolerance, [transported_error, budget], "transported <= projected + ABC + AB", "triangle")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} E={energy} two-delta", transported_error <= two_delta_budget + tolerance, [transported_error, two_delta_budget], "transported <= projected + 2 ABC", "triangle")
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": partition["orientation"], "core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": buffer_width, "energy_window": energy, "projection_mass": mass, "delta_abc": delta_abc, "delta_ab": delta_ab, "projected_error": projected_error, "transported_error": transported_error, "recovered_input_distance": recovered_input_distance, "triangle_budget": budget, "two_delta_budget": two_delta_budget, "contractivity_gap": contractivity_gap, "recovered_sigma_trace": recovered_sigma_trace, "recovered_rho_trace": recovered_rho_trace, "recovered_min_eigenvalue": recovered_min_eigenvalue})
    check("partition aggregate", partition_count > 0 and len(rows) > 0, [partition_count, len(rows)], "positive rows", "coverage")
    check("aggregate ranges", min(delta_abc_values) >= -tolerance and min(delta_ab_values) >= -tolerance and min(projected_errors) >= -tolerance and min(transported_errors) >= -tolerance and all(np.isfinite(value) for value in delta_abc_values + delta_ab_values + projected_errors + transported_errors + budgets), [min(delta_abc_values), max(delta_abc_values), min(transported_errors), max(transported_errors)], "finite nonnegative distances", "aggregate")
    check("transport aggregates", normalization_failures == 0 and contractivity_failures == 0 and triangle_failures == 0 and two_delta_failures == 0, [normalization_failures, contractivity_failures, triangle_failures, two_delta_failures], "zero violations", "transport")
    profiles = cutoff_profiles(rows, tolerance)
    check("cutoff profiles", profiles["count"] > 0 and all(len(profile["dimensions"]) >= 2 for profile in profiles["profiles"]), profiles["count"], "profiles with adjacent cutoffs", "cutoff stress")
    ratios = [float(item["transported_error_ratio"]) for profile in profiles["profiles"] for item in profile["adjacent_ratios"]]
    check("cutoff ratios finite", all(np.isfinite(value) and value >= -tolerance for value in ratios), [min(ratios, default=0.0), max(ratios, default=0.0)], "finite nonnegative ratios", "cutoff stress")
    derived = {"admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "system_count": len(pairs), "partition_count": partition_count, "row_count": len(rows), "beta_values": betas, "energy_windows": energies, "delta_abc_min": min(delta_abc_values), "delta_abc_max": max(delta_abc_values), "delta_ab_min": min(delta_ab_values), "delta_ab_max": max(delta_ab_values), "projected_error_max": max(projected_errors), "transported_error_max": max(transported_errors), "triangle_budget_max": max(budgets), "contractivity_gap_max": max(float(row["contractivity_gap"]) for row in rows), "normalization_violation_count": normalization_failures, "contractivity_violation_count": contractivity_failures, "triangle_violation_count": triangle_failures, "two_delta_violation_count": two_delta_failures, "cutoff_profiles": profiles}
    payload = {"schema": "tect/pre-a-r396-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-396", "exploration_id": "EXP-001239", "verdict": "PASS", "checks": checks, "derived": derived, "scope": scope, "records": rows}
    atomic_json(output, payload)
    print(f"R-396 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={partition_count} rows={len(rows)} transported_max={max(transported_errors):.6g} ratio_max={profiles['maximum_adjacent_transport_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
