#!/usr/bin/env python3
"""Finite intrinsic kinetic-graph Poincare stress for Q3 likelihood rows."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-intrinsic-kinetic-poincare-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_hamiltonian_intrinsic_kinetic_poincare" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def intrinsic_graph(probabilities: np.ndarray, p_coordinate: np.ndarray, chi: float) -> tuple[float, np.ndarray, np.ndarray]:
    """Return the weighted graph gap, Laplacian, and symmetric conductances."""
    pi = np.asarray(probabilities, dtype=float)
    p_matrix = np.asarray(p_coordinate, dtype=complex)
    if pi.ndim != 1 or p_matrix.shape != (pi.size, pi.size) or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0) or chi <= 0.0:
        raise AssertionError("invalid intrinsic graph input")
    pi = pi / float(np.sum(pi))
    conductance = (pi[:, None] + pi[None, :]) * np.square(np.abs(p_matrix)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse_sqrt = 1.0 / np.sqrt(pi)
    weighted = inverse_sqrt[:, None] * laplacian * inverse_sqrt[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if eigenvalues.size < 2 or not np.all(np.isfinite(eigenvalues)):
        raise AssertionError("invalid intrinsic graph spectrum")
    if abs(float(eigenvalues[0])) > 1.0e-8:
        raise AssertionError(f"graph constant mode is not zero: {eigenvalues[0]}")
    gap = float(eigenvalues[1])
    if gap <= 0.0:
        raise AssertionError(f"intrinsic graph is disconnected: {eigenvalues}")
    return gap, laplacian, conductance


def graph_energy(laplacian: np.ndarray, likelihood: np.ndarray) -> float:
    values = np.asarray(likelihood, dtype=float)
    return max(0.0, float(np.real(values @ laplacian @ values)))


def variance(probabilities: np.ndarray, likelihood: np.ndarray) -> float:
    pi = np.asarray(probabilities, dtype=float)
    values = np.asarray(likelihood, dtype=float)
    pi = pi / float(np.sum(pi))
    mean = float(np.sum(pi * values))
    return max(0.0, float(np.sum(pi * np.square(values - mean))))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    variance_floor = float(fixture["variance_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
    supports = [tuple(int(site) for site in support) for support in fixture["source_support_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 220:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001249" and manifest["result_id"] == "R-404" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001249/R-404/false", "provenance")
    finite_flags = ("finite_intrinsic_kinetic_graph_closed", "finite_weighted_poincare_gap_closed", "finite_likelihood_row_test_closed", "finite_cutoff_profile_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite intrinsic graph only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive kinetic prefactor", chi > 0.0, chi, ">0", "fixture")

    system_profiles: dict[str, dict[str, Any]] = {}
    gap_values: list[float] = []
    ratio_values: list[float] = []
    kinetic_values: list[float] = []
    variance_values: list[float] = []
    trace_residual_values: list[float] = []
    residual_values: list[float] = []
    total_contexts = 0
    total_rows = 0
    zero_variance_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, p_coordinate = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} momentum", p_coordinate.shape == (dimension, dimension) and np.all(np.isfinite(p_coordinate)), p_coordinate.shape, (dimension, dimension), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        system_key = f"V={volume}/d={dimension}"
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "nonzero_variance_count": 0, "zero_variance_count": 0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_ratio": float("inf"), "maximum_ratio": 0.0, "minimum_kinetic_form": float("inf"), "maximum_kinetic_form": 0.0, "minimum_variance": float("inf"), "maximum_variance": 0.0, "minimum_poincare_residual": float("inf"), "maximum_poincare_residual": 0.0}
        for beta in betas:
            reference, raw_reference = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            generator_cache = {support: sum((q_ops[site] for site in support), np.zeros_like(q_ops[0])) for support in supports}
            prefixes_by_key = {(order_name, history_sign): r399.all_prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms))))) ) for history_sign in history_signs}
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator_cache[support], source_sign * amplitude, hbar)
                    seeded = r399.hermitian(source @ states[beta] @ source.conj().T)
                    for (order_name, history_sign), prefixes in prefixes_by_key.items():
                        for prefix_length, prefix in prefixes:
                            for history_adjoint in adjoints:
                                state = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = r399.coordinate_distribution(state, basis, dimension, volume)
                                check(f"V={volume} d={dimension} beta={beta} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for _radius, conditional, likelihood in r402.conditional_rows(reference, sample, collar_order, dimension, floor):
                                        gap, laplacian, _conductance = intrinsic_graph(conditional, p_coordinate, chi)
                                        kinetic = r402.kinetic_form(conditional, likelihood, p_coordinate, chi)
                                        energy = graph_energy(laplacian, likelihood)
                                        var = variance(conditional, likelihood)
                                        residual = kinetic - energy
                                        if not math.isfinite(residual) or abs(residual) > tolerance:
                                            raise AssertionError(f"graph/trace mismatch: {residual}")
                                        poincare_residual = kinetic - gap * var
                                        if not math.isfinite(poincare_residual) or poincare_residual < -tolerance:
                                            raise AssertionError(f"intrinsic Poincare inequality failed: {poincare_residual}")
                                        gap_values.append(gap)
                                        kinetic_values.append(kinetic)
                                        variance_values.append(var)
                                        trace_residual_values.append(residual)
                                        residual_values.append(poincare_residual)
                                        total_rows += 1
                                        profile["row_count"] += 1
                                        profile["minimum_gap"] = min(profile["minimum_gap"], gap)
                                        profile["maximum_gap"] = max(profile["maximum_gap"], gap)
                                        profile["minimum_kinetic_form"] = min(profile["minimum_kinetic_form"], kinetic)
                                        profile["maximum_kinetic_form"] = max(profile["maximum_kinetic_form"], kinetic)
                                        profile["minimum_variance"] = min(profile["minimum_variance"], var)
                                        profile["maximum_variance"] = max(profile["maximum_variance"], var)
                                        profile["minimum_poincare_residual"] = min(profile["minimum_poincare_residual"], poincare_residual)
                                        profile["maximum_poincare_residual"] = max(profile["maximum_poincare_residual"], poincare_residual)
                                        if var > variance_floor:
                                            ratio = kinetic / var
                                            if not math.isfinite(ratio) or ratio < 0.0:
                                                raise AssertionError("invalid kinetic/variance ratio")
                                            ratio_values.append(ratio)
                                            profile["nonzero_variance_count"] += 1
                                            profile["minimum_ratio"] = min(profile["minimum_ratio"], ratio)
                                            profile["maximum_ratio"] = max(profile["maximum_ratio"], ratio)
                                        else:
                                            zero_variance_rows += 1
                                            profile["zero_variance_count"] += 1
                                    profile["context_count"] += 1
                                    total_contexts += 1
        check(f"V={volume} d={dimension} connected gaps", profile["minimum_gap"] > 0.0 and math.isfinite(profile["minimum_gap"]), [profile["minimum_gap"], profile["maximum_gap"]], ">0 finite", "intrinsic graph")
        system_profiles[system_key] = profile

    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(system_profiles) == len(pairs), len(system_profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("intrinsic gaps", all(math.isfinite(value) and value > 0.0 for value in gap_values), [min(gap_values), max(gap_values)], ">0 finite", "intrinsic graph")
    check("finite kinetic forms", all(math.isfinite(value) and value >= -tolerance for value in kinetic_values), [min(kinetic_values), max(kinetic_values)], ">=-tolerance and finite", "forms")
    check("graph trace identity", all(math.isfinite(value) and abs(value) <= tolerance for value in trace_residual_values), [min(trace_residual_values), max(trace_residual_values)], "absolute residual <= tolerance", "forms")
    check("intrinsic Poincare rows", all(math.isfinite(value) and value >= -tolerance for value in residual_values), [min(residual_values), max(residual_values)], ">=-tolerance", "Poincare")
    check("kinetic variance ratios", all(math.isfinite(value) and value >= 0.0 for value in ratio_values), [min(ratio_values), max(ratio_values)], "finite nonnegative", "Poincare")
    dimensions = [dimension for _volume, dimension in pairs]
    derived = {"system_count": len(pairs), "context_count": total_contexts, "comparison_row_count": total_rows, "nonzero_variance_row_count": len(ratio_values), "zero_variance_row_count": zero_variance_rows, "minimum_intrinsic_gap": min(gap_values), "maximum_intrinsic_gap": max(gap_values), "minimum_kinetic_form": min(kinetic_values), "maximum_kinetic_form": max(kinetic_values), "minimum_variance": min(variance_values), "maximum_variance": max(variance_values), "minimum_kinetic_to_variance_ratio": min(ratio_values), "maximum_kinetic_to_variance_ratio": max(ratio_values), "minimum_graph_trace_residual": min(trace_residual_values), "maximum_graph_trace_residual": max(trace_residual_values), "minimum_poincare_residual": min(residual_values), "maximum_poincare_residual": max(residual_values), "cutoff_dimensions": dimensions, "system_profiles": system_profiles}
    payload = {"schema": "tect/pre-a-r404-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-404", "exploration_id": "EXP-001249", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-404 PRIMARY PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} gap=[{derived['minimum_intrinsic_gap']:.6g},{derived['maximum_intrinsic_gap']:.6g}] ratio=[{derived['minimum_kinetic_to_variance_ratio']:.6g},{derived['maximum_kinetic_to_variance_ratio']:.6g}]")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
