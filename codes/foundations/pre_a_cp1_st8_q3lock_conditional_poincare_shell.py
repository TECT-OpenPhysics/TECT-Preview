#!/usr/bin/env python3
"""Finite conditional Poincare transfer for the R-398 Doob shell ledger.

For every oriented collar prefix, the R-398 shell variance is evaluated as a
conditional variance of the coordinate likelihood.  A reversible
nearest-neighbour birth-death form on the ordered finite coordinate levels
then supplies an exact finite Poincare upper bound.  The calculation is a
route discriminator only: a finite conditional gap is not promoted to a
cutoff- or volume-uniform estimate.
"""

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
SLUG = "pre_a_cp1_st8_q3lock_conditional_poincare_shell"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-poincare-shell-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
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


def split_system(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [embed(q_single, site, volume, identity) for site in range(volume)]
    momenta = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(coordinates, momenta)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
    zero = np.zeros_like(coordinates[0])
    full = hermitian(sum(onsite + bonds, zero))
    return coordinates, full, onsite + bonds


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return hermitian((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


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


def coordinate_distribution(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    raw_minimum = float(np.min(diagonal))
    probabilities = np.maximum(diagonal, 0.0)
    total = float(np.sum(probabilities))
    if total <= 0.0:
        raise AssertionError("coordinate distribution has zero mass")
    probabilities /= total
    return probabilities.reshape((dimension,) * volume), raw_minimum


def marginal(probabilities: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    volume = probabilities.ndim
    rest = [site for site in range(volume) if site not in sites]
    transposed = np.transpose(probabilities, sites + rest)
    left = dimension ** len(sites)
    return transposed.reshape(left, -1).sum(axis=1).reshape((dimension,) * len(sites))


def all_prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    identity = np.eye(terms[0].shape[0], dtype=complex)
    current = identity
    rows = [(0, identity.copy())]
    for position, index in enumerate(order, start=1):
        current = unitary(terms[index], sign * delta, hbar) @ current
        rows.append((position, current.copy()))
    return rows


def birth_death_gap(probabilities: np.ndarray) -> float:
    """Return the first nonzero gap for min-neighbour conductances."""
    pi = np.asarray(probabilities, dtype=float)
    if pi.ndim != 1 or pi.size < 2 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid conditional law for birth-death gap")
    pi = pi / float(np.sum(pi))
    conductances = np.minimum(pi[:-1], pi[1:])
    laplacian = np.zeros((pi.size, pi.size), dtype=float)
    for index, conductance in enumerate(conductances):
        laplacian[index, index] += conductance
        laplacian[index + 1, index + 1] += conductance
        laplacian[index, index + 1] -= conductance
        laplacian[index + 1, index] -= conductance
    inv_sqrt = np.diag(1.0 / np.sqrt(pi))
    spectrum = np.linalg.eigvalsh((inv_sqrt @ laplacian @ inv_sqrt + inv_sqrt @ laplacian @ inv_sqrt) / 2.0)
    spectrum.sort()
    gap = float(spectrum[1])
    if not math.isfinite(gap) or gap <= 0.0:
        raise AssertionError(f"nonpositive birth-death gap: {gap}")
    return gap


def shell_metrics(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, mu: float, probability_tolerance: float) -> dict[str, Any]:
    local_reference = marginal(reference, [order[0]], dimension)
    local_sample = marginal(sample, [order[0]], dimension)
    if float(np.min(local_reference)) <= probability_tolerance:
        raise AssertionError("local reference probability floor too small")
    local_likelihood = local_sample / local_reference
    local_chi = float(np.sum(local_reference * (local_likelihood - 1.0) ** 2))
    local_q2 = float(np.sum(local_reference * local_likelihood**2))
    shell_rows: list[dict[str, Any]] = []
    parent_likelihood: np.ndarray | None = None
    gaps: list[float] = []
    poincare_slacks: list[float] = []
    gradient_values: list[float] = []
    bound_values: list[float] = []
    for radius in range(len(order)):
        prefix = order[: radius + 1]
        p_prefix = marginal(reference, prefix, dimension)
        q_prefix = marginal(sample, prefix, dimension)
        if float(np.min(p_prefix)) <= probability_tolerance:
            raise AssertionError(f"collar reference probability floor too small at radius {radius}")
        likelihood = q_prefix / p_prefix
        if radius == 0:
            parent = np.ones_like(likelihood)
            parent_probability = np.ones((1,), dtype=float)
            parent_likelihood_flat = np.ones((1,), dtype=float)
            p_rows = p_prefix.reshape(1, dimension)
            q_rows = q_prefix.reshape(1, dimension)
            f_rows = likelihood.reshape(1, dimension)
        else:
            if parent_likelihood is None:
                raise AssertionError("missing parent likelihood")
            parent = np.expand_dims(parent_likelihood, axis=-1)
            p_parent = marginal(reference, order[:radius], dimension)
            parent_probability = p_parent.reshape(-1)
            parent_likelihood_flat = parent_likelihood.reshape(-1)
            p_rows = p_prefix.reshape(-1, dimension)
            q_rows = q_prefix.reshape(-1, dimension)
            f_rows = likelihood.reshape(-1, dimension)
        increment = likelihood - parent
        energy = float(np.sum(p_prefix * increment**2))
        gradient_energy = 0.0
        poincare_bound = 0.0
        minimum_gap = float("inf")
        maximum_gap = 0.0
        maximum_slack = 0.0
        if radius > 0:
            for parent_index, (p_row, q_row, f_row) in enumerate(zip(p_rows, q_rows, f_rows)):
                parent_mass = float(parent_probability[parent_index])
                conditional = p_row / parent_mass
                conditional /= float(np.sum(conditional))
                mean = float(parent_likelihood_flat[parent_index])
                variance = float(np.sum(conditional * (f_row - mean) ** 2))
                conductance = np.minimum(conditional[:-1], conditional[1:])
                dirichlet = float(np.sum(conductance * np.diff(f_row) ** 2))
                gap = birth_death_gap(conditional)
                bound = dirichlet / gap
                slack = bound - variance
                if slack < -probability_tolerance * 1000.0:
                    raise AssertionError(f"conditional Poincare violation: {slack}")
                gradient_energy += parent_mass * dirichlet
                poincare_bound += parent_mass * bound
                minimum_gap = min(minimum_gap, gap)
                maximum_gap = max(maximum_gap, gap)
                maximum_slack = max(maximum_slack, slack)
                gaps.append(gap)
                poincare_slacks.append(slack)
                gradient_values.append(parent_mass * dirichlet)
                bound_values.append(parent_mass * bound)
        shell_rows.append({
            "radius": radius,
            "prefix_sites": prefix,
            "reference_mass": float(np.sum(p_prefix)),
            "sample_mass": float(np.sum(q_prefix)),
            "increment_energy": energy,
            "weighted_increment_energy": float(math.exp(2.0 * mu * radius) * energy) if radius > 0 else 0.0,
            "conditional_gradient_energy": gradient_energy,
            "conditional_poincare_bound": poincare_bound,
            "minimum_conditional_gap": minimum_gap if radius > 0 else None,
            "maximum_conditional_gap": maximum_gap if radius > 0 else None,
            "maximum_conditional_slack": maximum_slack if radius > 0 else 0.0,
            "weighted_poincare_bound": float(math.exp(2.0 * mu * radius) * poincare_bound) if radius > 0 else 0.0,
        })
        parent_likelihood = likelihood
    full_likelihood = sample / reference
    global_chi = float(np.sum(reference * (full_likelihood - 1.0) ** 2))
    shell_energy = float(sum(row["increment_energy"] for row in shell_rows[1:]))
    weighted_shell = float(sum(row["weighted_increment_energy"] for row in shell_rows[1:]))
    poincare_total = float(sum(row["conditional_poincare_bound"] for row in shell_rows[1:]))
    weighted_poincare_total = float(sum(row["weighted_poincare_bound"] for row in shell_rows[1:]))
    return {
        "local_q2": local_q2,
        "local_chi2": local_chi,
        "global_chi2": global_chi,
        "shell_energy": shell_energy,
        "weighted_shell_energy": weighted_shell,
        "poincare_bound": poincare_total,
        "weighted_poincare_bound": weighted_poincare_total,
        "poincare_residual": poincare_total - shell_energy,
        "weighted_poincare_residual": weighted_poincare_total - weighted_shell,
        "shell_rows": shell_rows,
        "minimum_conditional_gap": min(gaps, default=float("inf")),
        "maximum_conditional_gap": max(gaps, default=0.0),
        "maximum_conditional_slack": max(poincare_slacks, default=0.0),
        "total_gradient_energy": float(sum(gradient_values)),
        "full_likelihood_min": float(np.min(full_likelihood)),
        "full_likelihood_max": float(np.max(full_likelihood)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    probability_tolerance = float(fixture["probability_tolerance"])
    mu = float(Fraction(str(fixture["shell_weight_mu"])))
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
        if len(checks) < 160:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001244" and manifest["result_id"] == "R-399" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001244/R-399/false", "provenance")
    finite_flags = ("finite_conditional_variance_identity_closed", "finite_birth_death_poincare_transfer_closed", "finite_oriented_shell_gradient_profile_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite conditional Poincare only", "all promoted flags false", "scope")
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("system grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct systems", "fixture")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")

    contexts: list[dict[str, Any]] = []
    shell_values: list[float] = []
    weighted_shell_values: list[float] = []
    poincare_values: list[float] = []
    weighted_poincare_values: list[float] = []
    residuals: list[float] = []
    weighted_residuals: list[float] = []
    gaps: list[float] = []
    slacks: list[float] = []
    raw_probability_mins: list[float] = []
    profile_by_system: dict[str, dict[str, float]] = {}

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = split_system(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        references = {beta: coordinate_distribution(states[beta], basis, dimension, volume)[0] for beta in betas}
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        check(f"V={volume} d={dimension} coordinate basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        for beta in betas:
            reference = references[beta]
            for support in supports:
                generator = sum((q_ops[site] for site in support), np.zeros_like(q_ops[0]))
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = hermitian(source @ states[beta] @ source.conj().T)
                    for order_name, order in orders.items():
                        for history_sign in history_signs:
                            prefixes = all_prefixes(terms, order, history_sign, delta, hbar)
                            for prefix_length, prefix in prefixes:
                                for history_adjoint in adjoints:
                                    state = hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else hermitian(prefix.conj().T @ seeded @ prefix)
                                    sample, raw_minimum = coordinate_distribution(state, basis, dimension, volume)
                                    raw_probability_mins.append(raw_minimum)
                                    check(f"V={volume} d={dimension} coordinate positivity", raw_minimum >= -tolerance, raw_minimum, f">=-{tolerance}", "coordinates")
                                    for orientation in orientations:
                                        collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                        metrics = shell_metrics(reference, sample, collar_order, dimension, mu, probability_tolerance)
                                        check(f"V={volume} d={dimension} {orientation} prefix={prefix_length} Poincare", metrics["poincare_residual"] >= -tolerance and metrics["weighted_poincare_residual"] >= -tolerance, [metrics["poincare_residual"], metrics["weighted_poincare_residual"]], ">=-tolerance", "conditional Poincare")
                                        check(f"V={volume} d={dimension} {orientation} prefix={prefix_length} finite shell", metrics["shell_energy"] >= -tolerance and metrics["weighted_shell_energy"] >= -tolerance, [metrics["shell_energy"], metrics["weighted_shell_energy"]], ">=-tolerance", "shell variance")
                                        row = {
                                            "volume": volume,
                                            "dimension": dimension,
                                            "beta": beta,
                                            "source_support": list(support),
                                            "source_sign": source_sign,
                                            "order": order_name,
                                            "history_sign": history_sign,
                                            "prefix_length": prefix_length,
                                            "history_adjoint": history_adjoint,
                                            "orientation": orientation,
                                            "shell_energy": metrics["shell_energy"],
                                            "weighted_shell_energy": metrics["weighted_shell_energy"],
                                            "poincare_bound": metrics["poincare_bound"],
                                            "weighted_poincare_bound": metrics["weighted_poincare_bound"],
                                            "poincare_residual": metrics["poincare_residual"],
                                            "weighted_poincare_residual": metrics["weighted_poincare_residual"],
                                            "minimum_conditional_gap": metrics["minimum_conditional_gap"],
                                            "maximum_conditional_gap": metrics["maximum_conditional_gap"],
                                            "maximum_conditional_slack": metrics["maximum_conditional_slack"],
                                            "total_gradient_energy": metrics["total_gradient_energy"],
                                            "shell_rows": metrics["shell_rows"],
                                        }
                                        contexts.append(row)
                                        shell_values.append(metrics["shell_energy"])
                                        weighted_shell_values.append(metrics["weighted_shell_energy"])
                                        poincare_values.append(metrics["poincare_bound"])
                                        weighted_poincare_values.append(metrics["weighted_poincare_bound"])
                                        residuals.append(metrics["poincare_residual"])
                                        weighted_residuals.append(metrics["weighted_poincare_residual"])
                                        gaps.append(metrics["minimum_conditional_gap"])
                                        slacks.append(metrics["maximum_conditional_slack"])
                                        key = f"V={volume}/d={dimension}/{orientation}"
                                        profile = profile_by_system.setdefault(key, {"max_shell_energy": 0.0, "max_weighted_shell_energy": 0.0, "max_poincare_bound": 0.0, "max_weighted_poincare_bound": 0.0, "max_poincare_residual": 0.0, "max_weighted_poincare_residual": 0.0, "min_conditional_gap": float("inf"), "max_conditional_slack": 0.0, "max_gradient_energy": 0.0})
                                        profile["max_shell_energy"] = max(profile["max_shell_energy"], metrics["shell_energy"])
                                        profile["max_weighted_shell_energy"] = max(profile["max_weighted_shell_energy"], metrics["weighted_shell_energy"])
                                        profile["max_poincare_bound"] = max(profile["max_poincare_bound"], metrics["poincare_bound"])
                                        profile["max_weighted_poincare_bound"] = max(profile["max_weighted_poincare_bound"], metrics["weighted_poincare_bound"])
                                        profile["max_poincare_residual"] = max(profile["max_poincare_residual"], metrics["poincare_residual"])
                                        profile["max_weighted_poincare_residual"] = max(profile["max_weighted_poincare_residual"], metrics["weighted_poincare_residual"])
                                        profile["min_conditional_gap"] = min(profile["min_conditional_gap"], metrics["minimum_conditional_gap"])
                                        profile["max_conditional_slack"] = max(profile["max_conditional_slack"], metrics["maximum_conditional_slack"])
                                        profile["max_gradient_energy"] = max(profile["max_gradient_energy"], metrics["total_gradient_energy"])

    expected_contexts = sum(2 * volume * len(betas) * len(supports) * len(source_signs) * len(orders) * len(history_signs) * len(adjoints) * len(orientations) for volume, _ in pairs)
    check("context coverage", len(contexts) == expected_contexts, len(contexts), expected_contexts, "coverage")
    check("finite aggregates", all(np.isfinite(value) for values in (shell_values, weighted_shell_values, poincare_values, weighted_poincare_values, residuals, weighted_residuals, gaps, slacks) for value in values), "all finite", "all finite", "numerics")
    check("Poincare aggregate", min(residuals, default=0.0) >= -tolerance and min(weighted_residuals, default=0.0) >= -tolerance, [min(residuals, default=0.0), min(weighted_residuals, default=0.0)], ">=-tolerance", "conditional Poincare")
    check("shell aggregate", min(shell_values, default=0.0) >= -tolerance and min(weighted_shell_values, default=0.0) >= -tolerance, [min(shell_values, default=0.0), min(weighted_shell_values, default=0.0)], ">=-tolerance", "shell variance")
    check("gap positivity", min(gaps, default=0.0) > 0.0, min(gaps, default=0.0), ">0", "conditional gap")
    check("likelihood coverage", min(raw_probability_mins, default=0.0) >= -tolerance and len(contexts) > 0, [min(raw_probability_mins, default=0.0), len(contexts)], "nonempty coordinate rows", "coordinates")

    payload = {
        "schema": "tect/pre-a-r399-primary/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-399",
        "exploration_id": "EXP-001244",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": check_count,
        "derived": {
            "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
            "system_count": len(pairs),
            "context_count": len(contexts),
            "max_shell_energy": max(shell_values, default=0.0),
            "max_weighted_shell_energy": max(weighted_shell_values, default=0.0),
            "max_poincare_bound": max(poincare_values, default=0.0),
            "max_weighted_poincare_bound": max(weighted_poincare_values, default=0.0),
            "max_poincare_residual": max(residuals, default=0.0),
            "max_weighted_poincare_residual": max(weighted_residuals, default=0.0),
            "min_conditional_gap": min(gaps, default=0.0),
            "max_conditional_gap": max(gaps, default=0.0),
            "max_conditional_slack": max(slacks, default=0.0),
            "max_gradient_energy": max((row["total_gradient_energy"] for row in contexts), default=0.0),
            "min_coordinate_probability_roundoff": min(raw_probability_mins, default=0.0),
            "profile_by_system": profile_by_system,
            "finite_conditional_variance_identity_closed": True,
            "finite_birth_death_poincare_transfer_closed": True,
            "finite_oriented_shell_gradient_profile_closed": True,
            "cutoff_independent_conditional_gap_closed": False,
            "volume_independent_conditional_gap_closed": False,
            "source_independent_conditional_gap_closed": False,
            "uniform_gradient_decay_closed": False,
            "phase_conditioned_influence_closed": False,
            "folded_positive_replica_domination_closed": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "actual_split_limit_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
        },
        "records": contexts,
        "scope": scope,
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-399 PRIMARY PASS {check_count}/{check_count} contexts={len(contexts)} min_gap={payload['derived']['min_conditional_gap']:.6g} max_poincare={payload['derived']['max_poincare_bound']:.6g}")
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
