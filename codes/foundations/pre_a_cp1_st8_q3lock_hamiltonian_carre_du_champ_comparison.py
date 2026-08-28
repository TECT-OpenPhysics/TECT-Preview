#!/usr/bin/env python3
"""Finite Hamiltonian carré-du-champ comparison for R-402.

The R-401 coordinate Dirichlet form is compared with the kinetic form induced
by the actual finite Q3 Hamiltonian.  For a local coordinate multiplier
F=f(q), coordinate-only potentials commute with F, so only p^2/(2 chi) enters
the finite carré-du-champ.  This is a route checkpoint, not a common-core or
thermodynamic theorem.
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
from typing import Any, Iterable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-comparison-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
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


def coordinate_data(dimension: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(dimension)
    levels, vectors = np.linalg.eigh(hermitian(q_single))
    p_coordinate = hermitian(vectors.conj().T @ p_single @ vectors)
    if not np.all(np.isfinite(levels)) or np.any(np.diff(levels) <= 0.0):
        raise AssertionError("coordinate levels are not strictly ordered")
    if not np.allclose(p_coordinate, p_coordinate.conj().T, atol=1.0e-12):
        raise AssertionError("coordinate-basis momentum is not Hermitian")
    return levels.real, vectors, p_coordinate


def coordinate_form(probabilities: np.ndarray, likelihood: np.ndarray, spacings: np.ndarray) -> float:
    pi = np.asarray(probabilities, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    if pi.ndim != 1 or f.shape != pi.shape or pi.size < 2:
        raise AssertionError("invalid coordinate form row")
    if not np.all(np.isfinite(pi)) or not np.all(np.isfinite(f)) or np.any(pi <= 0.0):
        raise AssertionError("nonfinite or nonpositive coordinate form input")
    if spacings.shape != (pi.size - 1,) or np.any(spacings <= 0.0):
        raise AssertionError("invalid coordinate spacing")
    pi = pi / float(np.sum(pi))
    difference = np.diff(f)
    conductances = np.minimum(pi[:-1], pi[1:])
    return float(np.sum(conductances * np.square(difference / spacings)))


def kinetic_form(probabilities: np.ndarray, likelihood: np.ndarray, p_coordinate: np.ndarray, chi: float) -> float:
    pi = np.asarray(probabilities, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    if pi.ndim != 1 or f.shape != pi.shape or p_coordinate.shape != (pi.size, pi.size):
        raise AssertionError("invalid kinetic form row")
    if not np.all(np.isfinite(pi)) or not np.all(np.isfinite(f)) or np.any(pi <= 0.0) or chi <= 0.0:
        raise AssertionError("invalid kinetic form input")
    pi = pi / float(np.sum(pi))
    multiplier = np.diag(f.astype(complex))
    commutator = p_coordinate @ multiplier - multiplier @ p_coordinate
    gram = commutator.conj().T @ commutator
    value = float(np.real(np.sum(pi * np.diag(gram)))) / (2.0 * chi)
    if value < -1.0e-10:
        raise AssertionError(f"kinetic form is negative: {value}")
    return max(0.0, value)


def q_mutation_form(probabilities: np.ndarray, likelihood: np.ndarray, levels: np.ndarray, chi: float) -> float:
    """Hostile replacement of p by q; it must vanish for F=f(q)."""
    pi = np.asarray(probabilities, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    q_coordinate = np.diag(levels.astype(complex))
    multiplier = np.diag(f.astype(complex))
    commutator = q_coordinate @ multiplier - multiplier @ q_coordinate
    gram = commutator.conj().T @ commutator
    value = float(np.real(np.sum((pi / float(np.sum(pi))) * np.diag(gram)))) / (2.0 * chi)
    return max(0.0, value)


def conditional_rows(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, floor: float) -> Iterable[tuple[int, np.ndarray, np.ndarray]]:
    """Yield (radius, conditional reference law, conditional likelihood)."""
    for radius in range(len(order)):
        prefix_sites = order[: radius + 1]
        p_prefix = r399.marginal(reference, prefix_sites, dimension)
        q_prefix = r399.marginal(sample, prefix_sites, dimension)
        if float(np.min(p_prefix)) <= floor:
            raise AssertionError(f"reference marginal floor at radius {radius}")
        likelihood = q_prefix / p_prefix
        if radius == 0:
            parent_probability = np.ones((1,), dtype=float)
        else:
            parent_probability = r399.marginal(reference, order[:radius], dimension).reshape(-1)
        p_rows = p_prefix.reshape(-1, dimension)
        f_rows = likelihood.reshape(-1, dimension)
        for parent_mass, p_row, f_row in zip(parent_probability, p_rows, f_rows):
            if float(parent_mass) <= floor or not np.all(np.isfinite(f_row)):
                raise AssertionError("invalid conditional likelihood row")
            conditional = p_row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0:
                raise AssertionError("conditional probability is not positive")
            yield radius, conditional, f_row


def potential_commutator_residual(dimension: int, volume: int, fixture: dict[str, Any], levels: np.ndarray) -> float:
    """Check a site potential and a Q3 bond in the coordinate tensor basis."""
    identity = np.eye(dimension, dtype=complex)
    q = np.diag(levels.astype(complex))
    probe = np.diag(np.arange(dimension, dtype=float).astype(complex))
    onsite = float(Fraction(str(fixture["r"]))) * (q @ q) / 2.0 + float(Fraction(str(fixture["g"]))) * (q @ q @ q @ q) / 4.0
    residuals = [float(np.linalg.norm(onsite @ probe - probe @ onsite, ord="fro"))]
    if volume >= 2:
        q0 = np.kron(q, identity)
        q1 = np.kron(identity, q)
        f0 = np.kron(probe, identity)
        difference = q0 - q1
        difference2 = difference @ difference
        c = float(Fraction(str(fixture["c"])))
        lam = float(Fraction(str(fixture["lambda"])))
        bond = c * difference2 / 2.0 + lam * difference2 @ (q0 @ q0 + q1 @ q1) / 4.0
        residuals.append(float(np.linalg.norm(bond @ f0 - f0 @ bond, ord="fro")))
    return max(residuals)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    ratio_floor = float(fixture["ratio_floor"])
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

    check("identity", manifest["exploration_id"] == "EXP-001247" and manifest["result_id"] == "R-402" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001247/R-402/false", "provenance")
    finite_flags = ("finite_kinetic_carre_du_champ_closed", "finite_coordinate_kinetic_comparison_closed", "finite_potential_commutator_isolation_closed", "finite_orientation_history_comparison_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite kinetic comparison only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("positive kinetic prefactor", chi > 0.0, chi, ">0", "fixture")

    records: list[dict[str, Any]] = []
    system_profiles: dict[str, dict[str, Any]] = {}
    ratio_values: list[float] = []
    coordinate_values: list[float] = []
    kinetic_values: list[float] = []
    potential_residuals: list[float] = []
    comparison_rows = 0
    zero_coordinate_rows = 0

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, single_basis, p_coordinate = coordinate_data(dimension)
        spacings = np.diff(levels)
        potential_residual = potential_commutator_residual(dimension, volume, fixture, levels)
        potential_residuals.append(potential_residual)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} potential commutator", potential_residual <= tolerance, potential_residual, f"<={tolerance}", "potential isolation")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        system_key = f"V={volume}/d={dimension}"
        profile = system_profiles.setdefault(system_key, {"context_count": 0, "row_count": 0, "minimum_ratio": float("inf"), "maximum_ratio": 0.0, "minimum_coordinate_form": float("inf"), "maximum_coordinate_form": 0.0, "minimum_kinetic_form": float("inf"), "maximum_kinetic_form": 0.0, "maximum_absolute_difference": 0.0})
        for beta in betas:
            reference, raw_reference_minimum = r399.coordinate_distribution(states[beta], basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference_minimum >= -tolerance, [float(np.min(reference)), raw_reference_minimum], f">{floor}, >=-{tolerance}", "Gibbs")
            generator_cache: dict[tuple[int, ...], np.ndarray] = {}
            for support in supports:
                generator_cache[support] = sum((q_ops[site] for site in support), np.zeros_like(q_ops[0]))
            for support in supports:
                generator = generator_cache[support]
                source = q3.character(generator, source_signs[0] * amplitude, hbar)
                for source_sign in source_signs:
                    if source_sign != source_signs[0]:
                        source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = r399.hermitian(source @ states[beta] @ source.conj().T)
                    orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
                    for order_name, order in orders.items():
                        for history_sign in history_signs:
                            prefixes = r399.all_prefixes(terms, order, history_sign, delta, hbar)
                            for prefix_length, prefix in prefixes:
                                for history_adjoint in adjoints:
                                    state = r399.hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else r399.hermitian(prefix.conj().T @ seeded @ prefix)
                                    sample, raw_sample_minimum = r399.coordinate_distribution(state, basis, dimension, volume)
                                    check(f"V={volume} d={dimension} beta={beta} prefix={prefix_length} sample", raw_sample_minimum >= -tolerance, raw_sample_minimum, f">=-{tolerance}", "coordinates")
                                    for orientation in orientations:
                                        collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                        local_coordinate: list[float] = []
                                        local_kinetic: list[float] = []
                                        local_ratios: list[float] = []
                                        for _, conditional, likelihood in conditional_rows(reference, sample, collar_order, dimension, floor):
                                            coordinate_energy = coordinate_form(conditional, likelihood, spacings)
                                            kinetic_energy = kinetic_form(conditional, likelihood, p_coordinate, chi)
                                            coordinate_values.append(coordinate_energy)
                                            kinetic_values.append(kinetic_energy)
                                            comparison_rows += 1
                                            local_coordinate.append(coordinate_energy)
                                            local_kinetic.append(kinetic_energy)
                                            if coordinate_energy > ratio_floor:
                                                ratio = kinetic_energy / coordinate_energy
                                                if not math.isfinite(ratio) or ratio < 0.0:
                                                    raise AssertionError("nonfinite kinetic/coordinate ratio")
                                                ratio_values.append(ratio)
                                                local_ratios.append(ratio)
                                            else:
                                                zero_coordinate_rows += 1
                                        if not local_coordinate:
                                            raise AssertionError("empty conditional comparison")
                                        context = {
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
                                            "row_count": len(local_coordinate),
                                            "minimum_coordinate_form": min(local_coordinate),
                                            "maximum_coordinate_form": max(local_coordinate),
                                            "minimum_kinetic_form": min(local_kinetic),
                                            "maximum_kinetic_form": max(local_kinetic),
                                            "minimum_ratio": min(local_ratios, default=None),
                                            "maximum_ratio": max(local_ratios, default=None),
                                        }
                                        records.append(context)
                                        profile["context_count"] += 1
                                        profile["row_count"] += len(local_coordinate)
                                        profile["minimum_coordinate_form"] = min(profile["minimum_coordinate_form"], min(local_coordinate))
                                        profile["maximum_coordinate_form"] = max(profile["maximum_coordinate_form"], max(local_coordinate))
                                        profile["minimum_kinetic_form"] = min(profile["minimum_kinetic_form"], min(local_kinetic))
                                        profile["maximum_kinetic_form"] = max(profile["maximum_kinetic_form"], max(local_kinetic))
                                        if local_ratios:
                                            profile["minimum_ratio"] = min(profile["minimum_ratio"], min(local_ratios))
                                            profile["maximum_ratio"] = max(profile["maximum_ratio"], max(local_ratios))
                                        profile["maximum_absolute_difference"] = max(profile["maximum_absolute_difference"], max(abs(k - d) for k, d in zip(local_kinetic, local_coordinate)))
                                        check(f"V={volume} d={dimension} beta={beta} {orientation} form positivity", min(local_coordinate) >= -tolerance and min(local_kinetic) >= -tolerance, [min(local_coordinate), min(local_kinetic)], f">=-{tolerance}", "forms")
        check(f"V={volume} d={dimension} p basis", float(np.linalg.norm(p_coordinate - p_coordinate.conj().T, ord="fro")) <= tolerance, float(np.linalg.norm(p_coordinate - p_coordinate.conj().T, ord="fro")), f"<={tolerance}", "kinetic basis")

    expected_contexts = sum(2 * volume * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for volume, _ in pairs)
    check("context coverage", len(records) == expected_contexts, len(records), expected_contexts, "coverage")
    check("comparison coverage", comparison_rows > len(records) and comparison_rows > 0, comparison_rows, f">{len(records)}", "coverage")
    check("finite forms", all(math.isfinite(value) and value >= -tolerance for value in coordinate_values + kinetic_values), [min(coordinate_values, default=0.0), min(kinetic_values, default=0.0)], ">= -tolerance and finite", "numerics")
    check("finite ratios", bool(ratio_values) and all(math.isfinite(value) and value >= 0.0 for value in ratio_values), [min(ratio_values, default=0.0), max(ratio_values, default=0.0)], "finite nonnegative ratios", "comparison")
    check("potential isolation aggregate", max(potential_residuals, default=0.0) <= tolerance, max(potential_residuals, default=0.0), f"<={tolerance}", "potential isolation")

    derived = {
        "system_count": len(pairs),
        "context_count": len(records),
        "comparison_row_count": comparison_rows,
        "nonzero_coordinate_row_count": len(ratio_values),
        "zero_coordinate_row_count": zero_coordinate_rows,
        "minimum_coordinate_form": min(coordinate_values, default=0.0),
        "maximum_coordinate_form": max(coordinate_values, default=0.0),
        "minimum_kinetic_form": min(kinetic_values, default=0.0),
        "maximum_kinetic_form": max(kinetic_values, default=0.0),
        "minimum_kinetic_to_coordinate_ratio": min(ratio_values, default=0.0),
        "maximum_kinetic_to_coordinate_ratio": max(ratio_values, default=0.0),
        "maximum_potential_commutator_residual": max(potential_residuals, default=0.0),
        "maximum_absolute_form_difference": max((abs(k - d) for k, d in zip(kinetic_values, coordinate_values)), default=0.0),
        "system_profiles": system_profiles,
        "contexts": records,
    }
    payload = {
        "schema": "tect/pre-a-r402-primary/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-402",
        "exploration_id": "EXP-001247",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": check_count,
        "derived": derived,
        "scope": scope,
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-402 PRIMARY PASS {check_count}/{check_count} contexts={len(records)} rows={comparison_rows} ratio=[{derived['minimum_kinetic_to_coordinate_ratio']:.6g},{derived['maximum_kinetic_to_coordinate_ratio']:.6g}]")
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
