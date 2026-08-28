#!/usr/bin/env python3
"""Non-importing independent lane for R-402.

The Q3 matrices, Gibbs rows, histories and two quadratic forms are rebuilt
here without importing the primary R-402 implementation.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-comparison-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison" / "independent.json"
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
    coordinates = [embed(q_single, site, volume, identity) for site in range(volume)]
    momenta = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(coordinates, momenta)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        bonds.append(c * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
    zero = np.zeros_like(coordinates[0])
    return coordinates, hermitian(sum(onsite + bonds, zero)), onsite + bonds


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return hermitian((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


def all_prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    identity = np.eye(terms[0].shape[0], dtype=complex)
    current = identity
    rows = [(0, identity.copy())]
    for position, index in enumerate(order, start=1):
        current = unitary(terms[index], sign * delta, hbar) @ current
        rows.append((position, current.copy()))
    return rows


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, coordinate_basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(coordinate_basis.conj().T @ state @ coordinate_basis))
    raw_minimum = float(np.min(diagonal))
    values = np.maximum(diagonal, 0.0)
    total = float(np.sum(values))
    if total <= 0.0:
        raise AssertionError("coordinate distribution has zero mass")
    values /= total
    return values.reshape((dimension,) * volume), raw_minimum


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    left = dimension ** len(sites)
    return moved.reshape(left, -1).sum(axis=1).reshape((dimension,) * len(sites))


def coordinate_data(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    q_single, p_single = q3.oscillator(dimension)
    levels, vectors = np.linalg.eigh(hermitian(q_single))
    p_coordinate = hermitian(vectors.conj().T @ p_single @ vectors)
    if not np.all(np.isfinite(levels)) or np.any(np.diff(levels) <= 0.0):
        raise AssertionError("coordinate levels are not strictly ordered")
    return levels.real, p_coordinate


def coordinate_form(probabilities_row: np.ndarray, likelihood: np.ndarray, spacings: np.ndarray) -> float:
    pi = np.asarray(probabilities_row, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    if pi.ndim != 1 or f.shape != pi.shape or pi.size < 2 or np.any(pi <= 0.0) or not np.all(np.isfinite(f)):
        raise AssertionError("invalid coordinate row")
    pi = pi / float(np.sum(pi))
    return float(np.sum(np.minimum(pi[:-1], pi[1:]) * np.square(np.diff(f) / spacings)))


def kinetic_form(probabilities_row: np.ndarray, likelihood: np.ndarray, p_coordinate: np.ndarray, chi: float) -> float:
    pi = np.asarray(probabilities_row, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    if pi.ndim != 1 or f.shape != pi.shape or np.any(pi <= 0.0) or not np.all(np.isfinite(f)):
        raise AssertionError("invalid kinetic row")
    pi = pi / float(np.sum(pi))
    multiplier = np.diag(f.astype(complex))
    commutator = p_coordinate @ multiplier - multiplier @ p_coordinate
    value = float(np.real(np.sum(pi * np.diag(commutator.conj().T @ commutator)))) / (2.0 * chi)
    if value < -1.0e-10:
        raise AssertionError("negative kinetic form")
    return max(0.0, value)


def rows(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, floor: float) -> Iterable[tuple[np.ndarray, np.ndarray]]:
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


def potential_residual(dimension: int, volume: int, fixture: dict[str, Any], levels: np.ndarray) -> float:
    identity = np.eye(dimension, dtype=complex)
    q = np.diag(levels.astype(complex))
    probe = np.diag(np.arange(dimension, dtype=float).astype(complex))
    onsite = float(Fraction(str(fixture["r"]))) * q @ q / 2.0 + float(Fraction(str(fixture["g"]))) * q @ q @ q @ q / 4.0
    residuals = [float(np.linalg.norm(onsite @ probe - probe @ onsite, ord="fro"))]
    if volume >= 2:
        q0, q1 = np.kron(q, identity), np.kron(identity, q)
        f0 = np.kron(probe, identity)
        difference = q0 - q1
        difference2 = difference @ difference
        c, lam = float(Fraction(str(fixture["c"]))), float(Fraction(str(fixture["lambda"])))
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
    delta, hbar = float(Fraction(str(fixture["time_step"]))), float(Fraction(str(fixture["hbar"])))
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

    records: list[dict[str, Any]] = []
    system_profiles: dict[str, dict[str, Any]] = {}
    coordinate_values: list[float] = []
    kinetic_values: list[float] = []
    ratio_values: list[float] = []
    potential_values: list[float] = []
    zero_coordinate_rows = 0
    comparison_rows = 0

    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = model(volume, dimension, fixture)
        coordinate_basis = basis(dimension, volume)
        levels, p_coordinate = coordinate_data(dimension)
        spacings = np.diff(levels)
        potential_values.append(potential_residual(dimension, volume, fixture, levels))
        check(f"V={volume} d={dimension} basis", coordinate_basis.shape == (dimension**volume, dimension**volume), coordinate_basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        profile = system_profiles.setdefault(f"V={volume}/d={dimension}", {"context_count": 0, "row_count": 0, "minimum_ratio": float("inf"), "maximum_ratio": 0.0, "minimum_coordinate_form": float("inf"), "maximum_coordinate_form": 0.0, "minimum_kinetic_form": float("inf"), "maximum_kinetic_form": 0.0, "maximum_absolute_difference": 0.0})
        for beta in betas:
            reference, raw_reference = probabilities(states[beta], coordinate_basis, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            for support in supports:
                generator = sum((q_ops[site] for site in support), np.zeros_like(q_ops[0]))
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = hermitian(source @ states[beta] @ source.conj().T)
                    for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms)))))):
                        for history_sign in history_signs:
                            for prefix_length, prefix in all_prefixes(terms, order, history_sign, delta, hbar):
                                for history_adjoint in adjoints:
                                    state = hermitian(prefix @ seeded @ prefix.conj().T) if not history_adjoint else hermitian(prefix.conj().T @ seeded @ prefix)
                                    sample, raw_sample = probabilities(state, coordinate_basis, dimension, volume)
                                    check(f"V={volume} d={dimension} prefix={prefix_length} sample", raw_sample >= -tolerance, raw_sample, f">=-{tolerance}", "coordinates")
                                    for orientation in orientations:
                                        collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                        local_coordinate: list[float] = []
                                        local_kinetic: list[float] = []
                                        local_ratios: list[float] = []
                                        for conditional, likelihood in rows(reference, sample, collar_order, dimension, floor):
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
                                                    raise AssertionError("invalid ratio")
                                                ratio_values.append(ratio)
                                                local_ratios.append(ratio)
                                            else:
                                                zero_coordinate_rows += 1
                                        context = {"volume": volume, "dimension": dimension, "beta": beta, "source_support": list(support), "source_sign": source_sign, "order": order_name, "history_sign": history_sign, "prefix_length": prefix_length, "history_adjoint": history_adjoint, "orientation": orientation, "row_count": len(local_coordinate), "minimum_coordinate_form": min(local_coordinate), "maximum_coordinate_form": max(local_coordinate), "minimum_kinetic_form": min(local_kinetic), "maximum_kinetic_form": max(local_kinetic), "minimum_ratio": min(local_ratios, default=None), "maximum_ratio": max(local_ratios, default=None)}
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

    expected_contexts = sum(2 * volume * len(betas) * len(supports) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for volume, _ in pairs)
    check("context coverage", len(records) == expected_contexts, len(records), expected_contexts, "coverage")
    check("comparison coverage", comparison_rows > len(records) and comparison_rows > 0, comparison_rows, f">{len(records)}", "coverage")
    check("finite forms", all(math.isfinite(value) and value >= -tolerance for value in coordinate_values + kinetic_values), [min(coordinate_values, default=0.0), min(kinetic_values, default=0.0)], ">=-tolerance and finite", "numerics")
    check("finite ratios", bool(ratio_values) and all(math.isfinite(value) and value >= 0.0 for value in ratio_values), [min(ratio_values, default=0.0), max(ratio_values, default=0.0)], "finite nonnegative ratios", "comparison")
    check("potential isolation aggregate", max(potential_values, default=0.0) <= tolerance, max(potential_values, default=0.0), f"<={tolerance}", "potential isolation")
    derived = {"system_count": len(pairs), "context_count": len(records), "comparison_row_count": comparison_rows, "nonzero_coordinate_row_count": len(ratio_values), "zero_coordinate_row_count": zero_coordinate_rows, "minimum_coordinate_form": min(coordinate_values, default=0.0), "maximum_coordinate_form": max(coordinate_values, default=0.0), "minimum_kinetic_form": min(kinetic_values, default=0.0), "maximum_kinetic_form": max(kinetic_values, default=0.0), "minimum_kinetic_to_coordinate_ratio": min(ratio_values, default=0.0), "maximum_kinetic_to_coordinate_ratio": max(ratio_values, default=0.0), "maximum_potential_commutator_residual": max(potential_values, default=0.0), "maximum_absolute_form_difference": max((abs(k - d) for k, d in zip(kinetic_values, coordinate_values)), default=0.0), "system_profiles": system_profiles, "contexts": records}
    payload = {"schema": "tect/pre-a-r402-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-402", "exploration_id": "EXP-001247", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-402 INDEPENDENT PASS {check_count}/{check_count} contexts={len(records)} rows={comparison_rows} ratio=[{derived['minimum_kinetic_to_coordinate_ratio']:.6g},{derived['maximum_kinetic_to_coordinate_ratio']:.6g}]")
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
