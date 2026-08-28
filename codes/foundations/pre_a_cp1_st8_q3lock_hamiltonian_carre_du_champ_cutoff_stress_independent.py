#!/usr/bin/env python3
"""Non-importing independent cutoff lane for R-403."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-carre-du-champ-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_cutoff_stress" / "independent.json"
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
    identity = np.eye(terms[0].shape[0], dtype=complex)
    current = identity
    result = [(0, identity.copy())]
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


def coordinate_form(pi: np.ndarray, f: np.ndarray, spacings: np.ndarray) -> float:
    pi = np.asarray(pi, dtype=float)
    f = np.asarray(f, dtype=float)
    pi /= float(np.sum(pi))
    return float(np.sum(np.minimum(pi[:-1], pi[1:]) * np.square(np.diff(f) / spacings)))


def kinetic_form(pi: np.ndarray, f: np.ndarray, p_coordinate: np.ndarray, chi: float) -> float:
    pi = np.asarray(pi, dtype=float)
    f = np.asarray(f, dtype=float)
    pi /= float(np.sum(pi))
    multiplier = np.diag(f.astype(complex))
    commutator = p_coordinate @ multiplier - multiplier @ p_coordinate
    value = float(np.real(np.sum(pi * np.diag(commutator.conj().T @ commutator)))) / (2.0 * chi)
    if value < -1.0e-10:
        raise AssertionError("negative kinetic form")
    return max(0.0, value)


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
    ratio_floor = float(fixture["ratio_floor"])
    chi = float(Fraction(str(fixture["chi"])))
    delta, hbar = float(Fraction(str(fixture["time_step"]))), float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
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

    check("identity", manifest["exploration_id"] == "EXP-001248" and manifest["result_id"] == "R-403" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001248/R-403/false", "provenance")
    finite_flags = ("finite_cutoff_form_stress_closed", "finite_ratio_profile_closed", "finite_lower_upper_direction_split_closed", "finite_orientation_history_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite cutoff stress only", "all promoted flags false", "scope")
    records: list[dict[str, Any]] = []
    profiles: dict[str, dict[str, Any]] = {}
    coordinate_values: list[float] = []
    kinetic_values: list[float] = []
    ratios: list[float] = []
    total_contexts = 0
    total_rows = 0
    zero_rows = 0
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        levels, p_coordinate = coordinate_data(dimension)
        spacings = np.diff(levels)
        profile = profiles.setdefault(f"d={dimension}", {"dimension": dimension, "context_count": 0, "row_count": 0, "nonzero_ratio_count": 0, "minimum_ratio": float("inf"), "maximum_ratio": 0.0, "minimum_coordinate_form": float("inf"), "maximum_coordinate_form": 0.0, "minimum_kinetic_form": float("inf"), "maximum_kinetic_form": 0.0})
        check(f"d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: gibbs(hamiltonian, beta) for beta in betas}
        prefix_cache = {(order_name, history_sign): prefixes(terms, order, history_sign, delta, hbar) for order_name, order in (("forward", list(range(len(terms)))), ("reverse", list(reversed(range(len(terms)))))) for history_sign in history_signs}
        for beta in betas:
            reference, raw_reference = probabilities(states[beta], basis, dimension, volume)
            check(f"d={dimension} beta={beta} reference", float(np.min(reference)) > floor and raw_reference >= -tolerance, [float(np.min(reference)), raw_reference], f">{floor}, >=-{tolerance}", "Gibbs")
            generator = q_ops[0]
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
                                local_d: list[float] = []
                                local_e: list[float] = []
                                local_r: list[float] = []
                                for conditional, likelihood in conditional_rows(reference, sample, order_sites, dimension, floor):
                                    d_value = coordinate_form(conditional, likelihood, spacings)
                                    e_value = kinetic_form(conditional, likelihood, p_coordinate, chi)
                                    local_d.append(d_value)
                                    local_e.append(e_value)
                                    coordinate_values.append(d_value)
                                    kinetic_values.append(e_value)
                                    total_rows += 1
                                    if d_value > ratio_floor:
                                        value = e_value / d_value
                                        ratios.append(value)
                                        local_r.append(value)
                                    else:
                                        zero_rows += 1
                                total_contexts += 1
                                records.append({"dimension": dimension, "beta": beta, "source_sign": source_sign, "order": order_name, "history_sign": history_sign, "prefix_length": prefix_length, "history_adjoint": history_adjoint, "orientation": orientation, "row_count": len(local_d), "minimum_coordinate_form": min(local_d), "maximum_coordinate_form": max(local_d), "minimum_kinetic_form": min(local_e), "maximum_kinetic_form": max(local_e), "minimum_ratio": min(local_r, default=None), "maximum_ratio": max(local_r, default=None)})
                                profile["context_count"] += 1
                                profile["row_count"] += len(local_d)
                                profile["minimum_coordinate_form"] = min(profile["minimum_coordinate_form"], min(local_d))
                                profile["maximum_coordinate_form"] = max(profile["maximum_coordinate_form"], max(local_d))
                                profile["minimum_kinetic_form"] = min(profile["minimum_kinetic_form"], min(local_e))
                                profile["maximum_kinetic_form"] = max(profile["maximum_kinetic_form"], max(local_e))
                                if local_r:
                                    profile["nonzero_ratio_count"] += len(local_r)
                                    profile["minimum_ratio"] = min(profile["minimum_ratio"], min(local_r))
                                    profile["maximum_ratio"] = max(profile["maximum_ratio"], max(local_r))

    dimensions = [dimension for _, dimension in pairs]
    first_max = profiles[f"d={dimensions[0]}"]["maximum_ratio"]
    last_max = profiles[f"d={dimensions[-1]}"]["maximum_ratio"]
    growth = last_max / first_max
    expected_contexts = sum(4 * len(betas) * len(source_signs) * 2 * len(history_signs) * len(adjoints) * len(orientations) for _volume, _dimension in pairs)
    check("context coverage", total_contexts == expected_contexts, total_contexts, expected_contexts, "coverage")
    check("row coverage", total_rows > total_contexts and total_rows > 0, total_rows, f">{total_contexts}", "coverage")
    check("finite forms", all(math.isfinite(value) and value >= -tolerance for value in coordinate_values + kinetic_values), [min(coordinate_values), min(kinetic_values)], ">=-tolerance and finite", "forms")
    check("finite ratios", all(math.isfinite(value) and value >= 0.0 for value in ratios), [min(ratios), max(ratios)], "finite nonnegative", "ratio profile")
    check("late upper-profile growth", growth > float(fixture["late_growth_threshold"]), growth, f">{fixture['late_growth_threshold']}", "cutoff stress")
    derived = {"system_count": len(pairs), "context_count": total_contexts, "comparison_row_count": total_rows, "nonzero_coordinate_row_count": len(ratios), "zero_coordinate_row_count": zero_rows, "minimum_coordinate_form": min(coordinate_values), "maximum_coordinate_form": max(coordinate_values), "minimum_kinetic_form": min(kinetic_values), "maximum_kinetic_form": max(kinetic_values), "minimum_kinetic_to_coordinate_ratio": min(ratios), "maximum_kinetic_to_coordinate_ratio": max(ratios), "baseline_dimension": dimensions[0], "late_dimension": dimensions[-1], "baseline_maximum_ratio": first_max, "late_maximum_ratio": last_max, "late_upper_profile_growth_ratio": growth, "system_by_dimension": profiles, "profiles": records}
    payload = {"schema": "tect/pre-a-r403-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-403", "exploration_id": "EXP-001248", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-403 INDEPENDENT PASS {check_count}/{check_count} systems={len(pairs)} contexts={total_contexts} rows={total_rows} ratio=[{derived['minimum_kinetic_to_coordinate_ratio']:.6g},{derived['maximum_kinetic_to_coordinate_ratio']:.6g}] late_growth={growth:.6g}")
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
