#!/usr/bin/env python3
"""Finite semigroup-dressed Petz collar discriminator (R-397).

The collar is a smooth local functional-calculus filter, not a hard energy
projector.  This script checks finite positivity, the exact first-moment mass
inequality, semigroup composition, a candidate normalized-filter envelope,
and the fixed-reference Petz transport triangle on the declared pilot grid.
It is deliberately claim-nonbearing: no cutoff or volume limit is inferred.
"""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-semigroup-dressed-petz-collar-finite-discriminator-manifest.json"
PARENT_PATH = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "primary.json"


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("r391_semigroup_parent", PARENT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load finite Gibbs/Petz parent")
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
    d_a, d_b, d_c = dimensions
    sqrt_bc = PARENT.spectral_power(reference_bc, 0.5, tolerance)
    inverse_sqrt_b = PARENT.spectral_power(reference_b, -0.5, tolerance)
    dressing = np.kron(np.eye(d_a, dtype=complex), inverse_sqrt_b)
    source = (dressing @ input_ab @ dressing).reshape(d_a, d_b, d_a, d_b)
    kernel = sqrt_bc.reshape(d_b, d_c, d_b, d_c)
    recovered = np.einsum("bcuv,auAx,xvBC->abcABC", kernel, source, kernel, optimize=True)
    return PARENT.hermitian(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def shifted_local(dimension: int, width: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(PARENT.build_system(dimension, width, fixture))
    shifted = values - float(values.min())
    hamiltonian = PARENT.hermitian((vectors * shifted) @ vectors.conj().T)
    return shifted, vectors, hamiltonian


def collar_filter(shifted: np.ndarray, vectors: np.ndarray, scale: float) -> np.ndarray:
    weights = np.exp(-scale * shifted / 2.0)
    return PARENT.hermitian((vectors * weights) @ vectors.conj().T)


def profile(rows: list[dict[str, Any]], field: str, tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["buffer_width"], row["orientation"], row["beta"], row["scale"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row[field]))
    records: list[dict[str, Any]] = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = [{"dimension": dimension, "count": len(values), "maximum": max(values)} for dimension, values in sorted(by_dimension.items())]
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "ratio": float(right["maximum"]) / denominator if denominator > tolerance else 0.0})
        values = [value for group in by_dimension.values() for value in group]
        records.append({"key": list(key), "dimensions": dimensions, "minimum": min(values), "maximum": max(values), "adjacent_ratios": ratios, "maximum_adjacent_ratio": max((item["ratio"] for item in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "profiles_with_adjacent_cutoff": sum(len(item["dimensions"]) >= 2 for item in records), "maximum_adjacent_ratio": max((item["maximum_adjacent_ratio"] for item in records), default=0.0)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    semigroup_tolerance = float(fixture["semigroup_tolerance"])
    scales = [float(Fraction(value)) for value in fixture["filter_scales"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    widths = [int(value) for value in fixture["core_widths"]]
    buffers = [int(value) for value in fixture["buffer_widths"]]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001241" and manifest["result_id"] == "R-397" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001241/R-397/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all semigroup collar rows", "coverage")
    finite_flags = ("finite_shifted_filter_positivity_closed", "finite_mass_moment_bound_closed", "finite_semigroup_composition_closed", "finite_normalized_filter_candidate_envelope_closed", "finite_petz_transport_closed", "finite_cutoff_profile_record_closed", "finite_hostile_mutation_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite smooth collar only", "all promoted flags false", "scope")
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct systems", "fixture")
    check("scale grid", len(scales) == len(fixture["filter_scales"]) and all(scale > 0.0 for scale in scales), scales, "positive declared scales", "fixture")

    local_data: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    local_minimum = float("inf")
    local_maximum = 0.0
    semigroup_residuals: list[float] = []
    for _, dimension in pairs:
        for width in widths:
            key = (dimension, width)
            if key in local_data:
                continue
            shifted, vectors, hamiltonian = shifted_local(dimension, width, fixture)
            local_data[key] = (shifted, vectors, hamiltonian)
            local_minimum = min(local_minimum, float(np.min(shifted)))
            local_maximum = max(local_maximum, float(np.max(shifted)))
            for scale_s in scales:
                for scale_t in scales:
                    left = collar_filter(shifted, vectors, scale_s) @ collar_filter(shifted, vectors, scale_t)
                    right = collar_filter(shifted, vectors, scale_s + scale_t)
                    residual = float(np.linalg.norm(left - right, ord="fro") / max(1.0, np.linalg.norm(right, ord="fro")))
                    semigroup_residuals.append(residual)
                    check(f"d={dimension} width={width} s={scale_s} t={scale_t} semigroup", residual <= semigroup_tolerance, residual, f"<={semigroup_tolerance}", "semigroup")
            check(f"d={dimension} width={width} shifted positivity", float(np.min(shifted)) >= -positivity_tolerance, float(np.min(shifted)), ">=-positivity_tolerance", "positivity")

    rows: list[dict[str, Any]] = []
    mass_defects: list[float] = []
    moments: list[float] = []
    mass_slacks: list[float] = []
    disturbances: list[float] = []
    envelopes: list[float] = []
    projected_errors: list[float] = []
    transported_errors: list[float] = []
    budgets: list[float] = []
    candidate_violations = mass_violations = normalization_violations = contractivity_violations = triangle_violations = two_delta_violations = 0
    partition_count = 0
    for volume, dimension in pairs:
        values, vectors = np.linalg.eigh(PARENT.build_system(dimension, volume, fixture))
        states = {beta: PARENT.gibbs_from_spectrum(values, vectors, beta) for beta in betas}
        partitions = PARENT.tripartitions(volume, widths, buffers)
        partition_count += len(partitions)
        for beta in betas:
            for partition in partitions:
                core, buffer, environment = partition["core"], partition["buffer"], partition["environment"]
                core_width, buffer_width = int(partition["core_width"]), int(partition["buffer_width"])
                dimensions = (dimension**len(core), dimension**len(buffer), dimension**len(environment))
                rho_abc = PARENT.partial_trace_sites(states[beta], dimension, volume, core + buffer + environment)
                rho_ab = PARENT.partial_trace_groups(rho_abc, list(dimensions), [0, 1])
                shifted, local_vectors, local_k = local_data[(dimension, core_width)]
                identity_bc = np.eye(dimensions[1] * dimensions[2], dtype=complex)
                lifted_k = np.kron(local_k, identity_bc)
                moment = float(np.trace(rho_abc @ lifted_k).real)
                moment = max(moment, 0.0)
                for scale in scales:
                    filt = collar_filter(shifted, local_vectors, scale)
                    lifted_filter = np.kron(filt, identity_bc)
                    raw_sigma = PARENT.hermitian(lifted_filter @ rho_abc @ lifted_filter)
                    mass = float(np.trace(raw_sigma).real)
                    mass_defect = 1.0 - mass
                    mass_bound = scale * moment
                    mass_slack = mass_bound - mass_defect
                    normalization_violations += int(not (mass > tolerance and mass <= 1.0 + tolerance))
                    mass_violations += int(mass_defect > mass_bound + tolerance)
                    if not (mass > tolerance):
                        raise AssertionError(f"zero collar mass: {volume=} {dimension=} {core=} {scale=}")
                    sigma_abc = PARENT.hermitian(raw_sigma / mass)
                    sigma_minimum = float(np.min(np.linalg.eigvalsh(sigma_abc)).real)
                    sigma_trace = float(np.trace(sigma_abc).real)
                    normalization_violations += int(abs(sigma_trace - 1.0) > tolerance or sigma_minimum < -positivity_tolerance)
                    sigma_ab = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [0, 1])
                    sigma_b = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [1])
                    sigma_bc = PARENT.partial_trace_groups(sigma_abc, list(dimensions), [1, 2])
                    recovered_sigma = petz_fast(sigma_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    recovered_rho = petz_fast(rho_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    delta_abc = trace_distance(rho_abc, sigma_abc)
                    delta_ab = trace_distance(rho_ab, sigma_ab)
                    projected = trace_distance(sigma_abc, recovered_sigma)
                    transported = trace_distance(rho_abc, recovered_rho)
                    recovered_input = trace_distance(recovered_rho, recovered_sigma)
                    budget = projected + delta_abc + delta_ab
                    two_delta = projected + 2.0 * delta_abc
                    candidate_envelope = float(np.sqrt(max(0.0, mass_defect)) + mass_defect / 2.0)
                    envelope_slack = candidate_envelope - delta_abc
                    contractivity_violations += int(recovered_input > delta_ab + tolerance or delta_ab > delta_abc + tolerance)
                    triangle_violations += int(transported > budget + tolerance)
                    two_delta_violations += int(transported > two_delta + tolerance)
                    candidate_violations += int(delta_abc > candidate_envelope + tolerance)
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} s={scale} collar", mass > tolerance and mass <= 1.0 + tolerance and mass_defect <= mass_bound + tolerance and sigma_trace == sigma_trace and sigma_trace >= 1.0 - tolerance and sigma_minimum >= -positivity_tolerance, [mass, mass_defect, mass_bound, sigma_trace, sigma_minimum], "positive normalized collar and mass bound", "filter")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} s={scale} candidate envelope", delta_abc <= candidate_envelope + tolerance, [delta_abc, candidate_envelope], "disturbance <= candidate envelope", "disturbance")
                    check(f"V={volume} d={dimension} {partition['orientation']} core={core} buffer={buffer} beta={beta} s={scale} transport", recovered_input <= delta_ab + tolerance and delta_ab <= delta_abc + tolerance and transported <= budget + tolerance and transported <= two_delta + tolerance, [recovered_input, delta_ab, delta_abc, transported, budget, two_delta], "contractive Petz triangle", "transport")
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": partition["orientation"], "core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": buffer_width, "scale": scale, "moment": moment, "projection_mass": mass, "mass_defect": mass_defect, "mass_bound": mass_bound, "mass_slack": mass_slack, "delta_abc": delta_abc, "delta_ab": delta_ab, "candidate_envelope": candidate_envelope, "candidate_envelope_slack": envelope_slack, "projected_error": projected, "transported_error": transported, "recovered_input_distance": recovered_input, "triangle_budget": budget, "two_delta_budget": two_delta, "sigma_minimum": sigma_minimum, "sigma_trace": sigma_trace})
                    mass_defects.append(mass_defect); moments.append(moment); mass_slacks.append(mass_slack); disturbances.append(delta_abc); envelopes.append(candidate_envelope); projected_errors.append(projected); transported_errors.append(transported); budgets.append(budget)
    check("row aggregate", partition_count > 0 and len(rows) > 0, [partition_count, len(rows)], "positive collar rows", "coverage")
    check("finite row values", all(np.isfinite(value) for values in (mass_defects, moments, mass_slacks, disturbances, envelopes, projected_errors, transported_errors, budgets) for value in values), "all finite", "all finite", "numerics")
    check("violation aggregates", normalization_violations == 0 and mass_violations == 0 and candidate_violations == 0 and contractivity_violations == 0 and triangle_violations == 0 and two_delta_violations == 0, [normalization_violations, mass_violations, candidate_violations, contractivity_violations, triangle_violations, two_delta_violations], "zero finite violations", "inequalities")
    transport_profiles = profile(rows, "transported_error", tolerance)
    disturbance_profiles = profile(rows, "delta_abc", tolerance)
    check("adjacent cutoff coverage", transport_profiles["count"] > 0 and transport_profiles["profiles_with_adjacent_cutoff"] > 0, [transport_profiles["count"], transport_profiles["profiles_with_adjacent_cutoff"]], "at least one adjacent cutoff profile", "profiles")
    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "system_count": len(pairs),
        "partition_count": partition_count,
        "row_count": len(rows),
        "beta_values": betas,
        "filter_scales": scales,
        "shifted_local_minimum": local_minimum,
        "shifted_local_maximum": local_maximum,
        "semigroup_residual_max": max(semigroup_residuals, default=0.0),
        "mass_min": min(1.0 - value for value in mass_defects),
        "mass_max": max(1.0 - value for value in mass_defects),
        "mass_defect_max": max(mass_defects),
        "moment_max": max(moments),
        "mass_bound_slack_min": min(mass_slacks),
        "disturbance_max": max(disturbances),
        "candidate_envelope_max": max(envelopes),
        "candidate_envelope_slack_min": min(float(row["candidate_envelope_slack"]) for row in rows),
        "projected_error_max": max(projected_errors),
        "transported_error_max": max(transported_errors),
        "triangle_budget_max": max(budgets),
        "normalization_violation_count": normalization_violations,
        "mass_violation_count": mass_violations,
        "candidate_envelope_violation_count": candidate_violations,
        "contractivity_violation_count": contractivity_violations,
        "triangle_violation_count": triangle_violations,
        "two_delta_violation_count": two_delta_violations,
        "transport_profiles": transport_profiles,
        "disturbance_profiles": disturbance_profiles
    }
    payload = {"schema": "tect/pre-a-r397-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-397", "exploration_id": "EXP-001241", "verdict": "PASS", "checks": checks, "derived": derived}
    atomic_json(output, payload)
    print(f"R-397 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={partition_count} rows={len(rows)} mass_defect_max={derived['mass_defect_max']:.6g} disturbance_max={derived['disturbance_max']:.6g} transport_max={derived['transported_error_max']:.6g} ratio_max={transport_profiles['maximum_adjacent_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
