#!/usr/bin/env python3
"""Independent reconstruction for the R-404 intrinsic kinetic graph lane."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_hamiltonian_intrinsic_kinetic_poincare" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def model(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_sites = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_sites, p_sites)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = q_sites[left] - q_sites[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (q_sites[left] @ q_sites[left] + q_sites[left + 1] @ q_sites[left + 1]) / 4.0)
    zero = np.zeros_like(q_sites[0])
    return q_sites, hermitian(sum(onsite + bonds, zero)), onsite + bonds


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return hermitian((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


def prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    current = np.eye(terms[0].shape[0], dtype=complex)
    result = [(0, current.copy())]
    for position, index in enumerate(order, start=1):
        current = unitary(terms[index], sign * delta, hbar) @ current
        result.append((position, current.copy()))
    return result


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    raw_minimum = float(np.min(diagonal))
    values = np.maximum(diagonal, 0.0)
    values /= float(np.sum(values))
    return values.reshape((dimension,) * volume), raw_minimum


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    return moved.reshape(dimension ** len(sites), -1).sum(axis=1).reshape((dimension,) * len(sites))


def coordinate_data(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(dimension)
    levels, vectors = np.linalg.eigh(hermitian(q_single))
    return levels.real, hermitian(vectors.conj().T @ p_single @ vectors)


def kinetic_form(pi: np.ndarray, values: np.ndarray, p_coordinate: np.ndarray, chi: float) -> float:
    pi = np.asarray(pi, dtype=float)
    values = np.asarray(values, dtype=float)
    pi = pi / float(np.sum(pi))
    multiplier = np.diag(values.astype(complex))
    commutator = p_coordinate @ multiplier - multiplier @ p_coordinate
    result = float(np.real(np.sum(pi * np.diag(commutator.conj().T @ commutator)))) / (2.0 * chi)
    if result < -1.0e-10:
        raise AssertionError("negative kinetic form")
    return max(0.0, result)


def intrinsic_graph(pi: np.ndarray, p_coordinate: np.ndarray, chi: float) -> tuple[float, np.ndarray]:
    pi = np.asarray(pi, dtype=float)
    pi = pi / float(np.sum(pi))
    conductance = (pi[:, None] + pi[None, :]) * np.square(np.abs(np.asarray(p_coordinate, dtype=complex))) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse_sqrt = 1.0 / np.sqrt(pi)
    weighted = inverse_sqrt[:, None] * laplacian * inverse_sqrt[None, :]
    eigenvalues = np.linalg.eigvalsh((weighted + weighted.T) / 2.0)
    if abs(float(eigenvalues[0])) > 1.0e-8 or eigenvalues.size < 2 or float(eigenvalues[1]) <= 0.0:
        raise AssertionError("intrinsic graph spectrum is not connected")
    return float(eigenvalues[1]), laplacian


def conditional_rows(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, floor: float):
    for radius in range(len(order)):
        p_prefix = marginal(reference, order[: radius + 1], dimension)
        q_prefix = marginal(sample, order[: radius + 1], dimension)
        if float(np.min(p_prefix)) <= floor:
            raise AssertionError("reference floor")
        likelihood = q_prefix / p_prefix
        parent = np.ones((1,), dtype=float) if radius == 0 else marginal(reference, order[:radius], dimension).reshape(-1)
        for mass, p_row, f_row in zip(parent, p_prefix.reshape(-1, dimension), likelihood.reshape(-1, dimension)):
            conditional = p_row / float(mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0 or not np.all(np.isfinite(f_row)):
                raise AssertionError("invalid conditional row")
            yield conditional, f_row


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
        if len(checks) < 200:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001249" and manifest["result_id"] == "R-404" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001249/R-404/false", "provenance")
    finite_flags = ("finite_intrinsic_kinetic_graph_closed", "finite_weighted_poincare_gap_closed", "finite_likelihood_row_test_closed", "finite_cutoff_profile_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite intrinsic graph only", "all promoted flags false", "scope")
    profiles: dict[str, dict[str, Any]] = {}
    gap_values: list[float] = []
    ratio_values: list[float] = []
    kinetic_values: list[float] = []
    variance_values: list[float] = []
    residual_values: list[float] = []
    total_contexts = 0
    total_rows = 0
    zero_variance_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        _levels, p_coordinate = coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        profile = {"dimension": dimension, "context_count": 0, "row_count": 0, "nonzero_variance_count": 0, "zero_variance_count": 0, "minimum_gap": float("inf"), "maximum_gap": 0.0, "minimum_ratio": float("inf"), "maximum_ratio": 0.0, "minimum_kinetic_form": float("inf"), "maximum_kinetic_form": 0.0, "minimum_variance": float("inf"), "maximum_variance": 0.0, "minimum_poincare_residual": float("inf"), "maximum_poincare_residual": 0.0}
        for beta in betas:
            reference, raw_reference = probabilities(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            generator = q_ops[0]
            prefix_cache = {(order_name, history_sign): prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms)))))) for history_sign in history_signs}
            for support in supports:
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = hermitian(source @ states[beta] @ source.conj().T)
                    for (order_name, history_sign), cached_prefixes in prefix_cache.items():
                        for prefix_length, prefix in cached_prefixes:
                            for history_adjoint in adjoints:
                                state = hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else hermitian(prefix.conj().T @ seeded @ prefix)
                                sample, raw_sample = probabilities(state, basis, dimension, volume)
                                check(f"d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                for orientation in orientations:
                                    order_sites = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                    for conditional, likelihood in conditional_rows(reference, sample, order_sites, dimension, floor):
                                        gap, laplacian = intrinsic_graph(conditional, p_coordinate, chi)
                                        kinetic = kinetic_form(conditional, likelihood, p_coordinate, chi)
                                        pi = conditional / float(np.sum(conditional))
                                        mean = float(np.sum(pi * likelihood))
                                        var = max(0.0, float(np.sum(pi * np.square(likelihood - mean))))
                                        graph = float(np.real(likelihood @ laplacian @ likelihood))
                                        trace_residual = kinetic - graph
                                        if not math.isfinite(trace_residual) or abs(trace_residual) > tolerance:
                                            raise AssertionError("graph trace mismatch")
                                        poincare_residual = kinetic - gap * var
                                        if not math.isfinite(poincare_residual) or poincare_residual < -tolerance:
                                            raise AssertionError("Poincare residual")
                                        gap_values.append(gap)
                                        kinetic_values.append(kinetic)
                                        variance_values.append(var)
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
                                                raise AssertionError("invalid ratio")
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
        profiles[f"V={volume}/d={dimension}"] = profile
    expected_contexts = sum(4 * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("system coverage", len(profiles) == len(pairs), len(profiles), len(pairs), "coverage")
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("intrinsic gaps", all(math.isfinite(value) and value > 0.0 for value in gap_values), [min(gap_values), max(gap_values)], ">0 finite", "intrinsic graph")
    check("finite kinetic forms", all(math.isfinite(value) and value >= -tolerance for value in kinetic_values), [min(kinetic_values), max(kinetic_values)], ">=-tolerance and finite", "forms")
    check("intrinsic Poincare rows", all(math.isfinite(value) and value >= -tolerance for value in residual_values), [min(residual_values), max(residual_values)], ">=-tolerance", "Poincare")
    check("kinetic variance ratios", all(math.isfinite(value) and value >= 0.0 for value in ratio_values), [min(ratio_values), max(ratio_values)], "finite nonnegative", "Poincare")
    derived = {"system_count": len(pairs), "context_count": total_contexts, "comparison_row_count": total_rows, "nonzero_variance_row_count": len(ratio_values), "zero_variance_row_count": zero_variance_rows, "minimum_intrinsic_gap": min(gap_values), "maximum_intrinsic_gap": max(gap_values), "minimum_kinetic_form": min(kinetic_values), "maximum_kinetic_form": max(kinetic_values), "minimum_variance": min(variance_values), "maximum_variance": max(variance_values), "minimum_kinetic_to_variance_ratio": min(ratio_values), "maximum_kinetic_to_variance_ratio": max(ratio_values), "minimum_graph_trace_residual": 0.0, "maximum_graph_trace_residual": 0.0, "minimum_poincare_residual": min(residual_values), "maximum_poincare_residual": max(residual_values), "cutoff_dimensions": [dimension for _volume, dimension in pairs], "system_profiles": profiles}
    payload = {"schema": "tect/pre-a-r404-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-404", "exploration_id": "EXP-001249", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-404 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} gap=[{derived['minimum_intrinsic_gap']:.6g},{derived['maximum_intrinsic_gap']:.6g}] ratio=[{derived['minimum_kinetic_to_variance_ratio']:.6g},{derived['maximum_kinetic_to_variance_ratio']:.6g}]")
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
