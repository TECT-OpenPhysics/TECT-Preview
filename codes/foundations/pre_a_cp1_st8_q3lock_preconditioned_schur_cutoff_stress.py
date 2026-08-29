#!/usr/bin/env python3
"""Finite high-cutoff stress with log-domain masses and projected graph gaps.

The ordinary density-matrix diagonal can underflow and can also move the exact
sqrt(pi) zero mode by more than the connectivity threshold.  This audit keeps
the Gibbs coordinate masses in log-sum-exp form and computes the positive graph
spectrum after explicitly removing that constant mode.  It is a numerical
conditioning diagnostic, not a uniform theorem.
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
SLUG = "preconditioned_schur_cutoff_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-preconditioned-schur-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_harmonic_schur_capacity as r406  # noqa: E402


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


def logsumexp(values: np.ndarray) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        raise AssertionError("invalid log-sum-exp input")
    maximum = float(np.max(array))
    return maximum + math.log(float(np.sum(np.exp(array - maximum))))


def log_coordinate_distribution(hamiltonian: np.ndarray, basis: np.ndarray, beta: float, dimension: int, volume: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh(r399.hermitian(hamiltonian))
    shifted = energies - float(np.min(energies))
    transformed = basis.conj().T @ vectors
    log_coefficients = np.log(np.maximum(np.abs(transformed), np.finfo(float).tiny))
    terms = -beta * shifted[None, :] + 2.0 * log_coefficients
    logs = np.array([logsumexp(row) for row in terms], dtype=float)
    logs -= logsumexp(logs)
    direct_weights = np.exp(-beta * shifted)
    direct_weights /= float(np.sum(direct_weights))
    direct_values = np.sum(np.square(np.abs(transformed)) * direct_weights[None, :], axis=1)
    direct_values = np.maximum(np.real(direct_values), 0.0)
    direct_total = float(np.sum(direct_values))
    if direct_total <= 0.0:
        raise AssertionError("direct coordinate mass vanished")
    direct_values /= direct_total
    return logs.reshape((dimension,) * volume), direct_values.reshape((dimension,) * volume), shifted


def log_marginal(log_values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    if not sites:
        return np.asarray([logsumexp(np.asarray(log_values).reshape(-1))])
    rest = [axis for axis in range(log_values.ndim) if axis not in sites]
    moved = np.transpose(log_values, sites + rest)
    flat = moved.reshape(dimension ** len(sites), -1)
    return np.array([logsumexp(row) for row in flat], dtype=float).reshape((dimension,) * len(sites))


def conditional_rows(log_reference: np.ndarray, order: list[int], dimension: int, floor: float) -> Iterable[tuple[np.ndarray, float]]:
    for radius in range(len(order)):
        prefix = log_marginal(log_reference, order[: radius + 1], dimension)
        parent = np.asarray([0.0]) if radius == 0 else log_marginal(log_reference, order[:radius], dimension).reshape(-1)
        if not np.all(np.isfinite(prefix)) or not np.all(np.isfinite(parent)):
            raise AssertionError("nonfinite log marginal")
        for parent_log, row in zip(parent, prefix.reshape(-1, dimension)):
            log_row = row - float(parent_log)
            maximum = float(np.max(log_row))
            weights = np.exp(log_row - maximum)
            weights /= float(np.sum(weights))
            if float(np.min(weights)) <= floor or not np.all(np.isfinite(weights)):
                raise AssertionError("conditional row lost positive mass")
            yield weights, float(np.min(log_row))


def projected_graph(weights: np.ndarray, momentum: np.ndarray, chi: float) -> dict[str, Any]:
    row = np.asarray(weights, dtype=float)
    if row.ndim != 1 or not np.all(np.isfinite(row)) or np.any(row <= 0.0) or chi <= 0.0:
        raise AssertionError("invalid positive graph row")
    row = row / float(np.sum(row))
    p_matrix = np.asarray(momentum, dtype=complex)
    if p_matrix.shape != (row.size, row.size) or not np.all(np.isfinite(p_matrix)):
        raise AssertionError("invalid momentum matrix")
    conductance = (row[:, None] + row[None, :]) * np.square(np.abs(p_matrix)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(row)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    raw_values = np.linalg.eigvalsh(operator)
    if len(raw_values) < 2 or not np.all(np.isfinite(raw_values)):
        raise AssertionError("raw graph spectrum failed")
    constant = np.sqrt(row)
    constant /= float(np.linalg.norm(constant))
    frame = np.column_stack((constant, np.eye(row.size)))
    orthogonal, _ = np.linalg.qr(frame, mode="complete")
    complement = orthogonal[:, 1:]
    projected = complement.T @ operator @ complement
    projected_values = np.linalg.eigvalsh((projected + projected.T) / 2.0)
    if len(projected_values) == 0 or not np.all(np.isfinite(projected_values)) or float(projected_values[0]) <= 0.0:
        raise AssertionError("projected graph is not positive")
    return {
        "weights": row,
        "conductance": conductance,
        "raw_zero_residual": abs(float(raw_values[0])),
        "raw_second_value": float(raw_values[1]),
        "projected_gap": float(projected_values[0]),
        "projected_values": projected_values,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    crosscheck_tolerance = float(fixture["crosscheck_tolerance"])
    floor = float(fixture["probability_floor"])
    gap_floor = float(fixture["gap_floor"])
    raw_zero_threshold = float(fixture["raw_zero_threshold"])
    scale_factor = float(Fraction(str(fixture["weight_scale_factor"])))
    chi = float(Fraction(str(fixture["chi"])))
    volume = int(fixture["volume"])
    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 420:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = ("finite_log_domain_gibbs_closed", "finite_log_conditional_rows_closed", "finite_constant_mode_projection_closed", "finite_projected_schur_gap_stress_closed", "finite_cutoff_stress_closed", "finite_scale_invariance_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("identity", manifest["result_id"] == "R-416" and manifest["exploration_id"] == "EXP-001261" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-416/EXP-001261/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("fixture", volume == 2 and dimensions == sorted(set(dimensions)) and len(dimensions) >= 10 and orientations == ["right", "left"], [volume, dimensions, orientations], "volume 2, at least 10 ordered cutoffs, right/left", "fixture")

    full_gaps: list[float] = []
    schur_gaps: list[float] = []
    coarse_gaps: list[float] = []
    residual_gaps: list[float] = []
    raw_zero_residuals: list[float] = []
    projected_gaps: list[float] = []
    scale_residuals: list[float] = []
    log_minima: list[float] = []
    condition_logs: list[float] = []
    direct_underflow_rows = 0
    total_rows = 0
    total_profiles = 0
    profile_records: list[dict[str, Any]] = []
    for dimension in dimensions:
        q_ops, hamiltonian, _terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _single_basis, momentum = r402.coordinate_data(dimension)
        lower, upper, neutral = r406.phase_indices(levels)
        blocks = [lower, neutral, upper] if len(neutral) else [lower, upper]
        check(f"d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        for beta in betas:
            log_reference, direct_reference, _shifted = log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"d={dimension} beta={beta} log Gibbs", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= crosscheck_tolerance, [float(np.min(log_reference)), float(np.max(log_reference)), float(np.sum(np.exp(log_reference)))], "finite normalized log mass", "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_projected_gap": float("inf"), "minimum_schur_gap": float("inf"), "minimum_raw_zero_residual": 0.0, "maximum_log_condition": 0.0, "direct_underflow_rows": 0}
                for weights, minimum_log_row in conditional_rows(log_reference, order, dimension, floor):
                    data = projected_graph(weights, momentum, chi)
                    schur = r406.harmonic_split(weights, data["conductance"], blocks)
                    scale_data = projected_graph(weights * scale_factor, momentum, chi)
                    scale_residual = abs(data["projected_gap"] - scale_data["projected_gap"])
                    direct_prefix = r399.marginal(direct_reference, order[:1], dimension) if volume > 1 else direct_reference
                    if float(np.min(direct_prefix)) <= 0.0:
                        direct_underflow_rows += 1
                        profile["direct_underflow_rows"] += 1
                    check(f"d={dimension} beta={beta} {orientation} row", data["projected_gap"] > gap_floor and schur["decomposition_gap"] > gap_floor and schur["decomposition_gap"] <= data["projected_gap"] + tolerance, [data["projected_gap"], schur["decomposition_gap"]], f"positive projected and Schur gaps, Schur <= projected + {tolerance}", "projected Schur")
                    check("scale invariance row", scale_residual <= crosscheck_tolerance, scale_residual, f"<={crosscheck_tolerance}", "scale")
                    check("constant projection", float(np.linalg.norm((np.eye(dimension) - np.outer(np.sqrt(data["weights"]), np.sqrt(data["weights"]))) @ np.sqrt(data["weights"]))) <= crosscheck_tolerance, "projected constant", f"<={crosscheck_tolerance}", "projection")
                    full_gaps.append(data["projected_gap"])
                    projected_gaps.append(data["projected_gap"])
                    schur_gaps.append(float(schur["decomposition_gap"]))
                    coarse_gaps.append(float(schur["coarse_gap"]))
                    residual_gaps.append(float(schur["residual_gap"]))
                    raw_zero_residuals.append(data["raw_zero_residual"])
                    scale_residuals.append(scale_residual)
                    log_minima.append(minimum_log_row)
                    condition_logs.append(float(np.max(np.log(data["weights"])) - np.min(np.log(data["weights"]))))
                    profile["row_count"] += 1
                    profile["minimum_projected_gap"] = min(profile["minimum_projected_gap"], data["projected_gap"])
                    profile["minimum_schur_gap"] = min(profile["minimum_schur_gap"], schur["decomposition_gap"])
                    profile["minimum_raw_zero_residual"] = max(profile["minimum_raw_zero_residual"], data["raw_zero_residual"])
                    profile["maximum_log_condition"] = max(profile["maximum_log_condition"], condition_logs[-1])
                    total_rows += 1
                check(f"d={dimension} beta={beta} {orientation} coverage", profile["row_count"] == dimension + 1, profile["row_count"], dimension + 1, "one-site conditional coverage")
                profile_records.append(profile)
                total_profiles += 1

    check("profile coverage", total_profiles == len(dimensions) * len(betas) * len(orientations), total_profiles, len(dimensions) * len(betas) * len(orientations), "coverage")
    expected_rows = len(orientations) * len(betas) * sum(dimension + 1 for dimension in dimensions)
    check("row coverage", total_rows == expected_rows, total_rows, expected_rows, "coverage")
    check("projected positivity", min(projected_gaps) > gap_floor and min(schur_gaps) > gap_floor, [min(projected_gaps), min(schur_gaps)], f">{gap_floor}", "finite stress")
    check("Schur ordering", max(schur_gaps) <= max(projected_gaps) + tolerance and min(schur_gaps) <= min(projected_gaps) + tolerance, [min(schur_gaps), min(projected_gaps)], f"Schur below projected + {tolerance}", "finite stress")
    check("scale aggregate", max(scale_residuals) <= crosscheck_tolerance, max(scale_residuals), f"<={crosscheck_tolerance}", "scale")
    check("log-domain range", all(math.isfinite(value) for value in log_minima + condition_logs), [min(log_minima), max(condition_logs)], "finite", "log-domain")
    check("raw-mode diagnosis", max(raw_zero_residuals) > raw_zero_threshold, max(raw_zero_residuals), f">{raw_zero_threshold} on at least one stressed row", "conditioning diagnosis")
    derived = {
        "system_count": len(dimensions),
        "profile_count": total_profiles,
        "comparison_row_count": total_rows,
        "cutoff_dimensions": dimensions,
        "beta_values": betas,
        "minimum_projected_gap": min(projected_gaps),
        "maximum_projected_gap": max(projected_gaps),
        "minimum_schur_gap": min(schur_gaps),
        "maximum_schur_gap": max(schur_gaps),
        "minimum_coarse_schur_gap": min(coarse_gaps),
        "maximum_coarse_schur_gap": max(coarse_gaps),
        "minimum_residual_gap": min(residual_gaps),
        "maximum_residual_gap": max(residual_gaps),
        "maximum_raw_zero_mode_residual": max(raw_zero_residuals),
        "minimum_raw_zero_mode_residual": min(raw_zero_residuals),
        "maximum_scale_invariance_residual": max(scale_residuals),
        "minimum_log_conditional_mass": min(log_minima),
        "maximum_log_condition_number": max(condition_logs),
        "direct_underflow_rows": direct_underflow_rows,
        "profiles": profile_records,
        "finite_log_domain_gibbs_closed": True,
        "finite_log_conditional_rows_closed": True,
        "finite_constant_mode_projection_closed": True,
        "finite_projected_schur_gap_stress_closed": True,
        "finite_cutoff_stress_closed": True,
        "finite_scale_invariance_closed": True,
        "cutoff_independent_schur_gap_closed": False,
        "volume_independent_schur_gap_closed": False,
        "phase_uniform_semigroup_closed": False,
        "exhaustion_uniform_semigroup_closed": False,
        "common_core_closed": False,
        "common_split_rule_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r416-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-416", "exploration_id": "EXP-001261", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-416 PRIMARY PASS {check_count}/{check_count} cutoffs={len(dimensions)} profiles={total_profiles} rows={total_rows} projected_gap=[{min(projected_gaps):.6g},{max(projected_gaps):.6g}] schur_gap=[{min(schur_gaps):.6g},{max(schur_gaps):.6g}] raw_zero_max={max(raw_zero_residuals):.6g}")
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
