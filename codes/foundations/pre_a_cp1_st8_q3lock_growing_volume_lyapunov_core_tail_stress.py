#!/usr/bin/env python3
"""Growing-volume finite stress for the R-417 core-tail interface.

This keeps the R-417 Q3 construction and conventions fixed while adding
volumes three and four at bounded oscillator cutoffs.  It is deliberately a
finite diagnostic: no minimum observed here is promoted to a uniform bound.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
SLUG = "growing_volume_lyapunov_core_tail_stress"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def induced_core_gap(weights: np.ndarray, conductance: np.ndarray, core: np.ndarray) -> dict[str, float | int]:
    pi = np.asarray(weights, dtype=float)
    indices = np.flatnonzero(np.asarray(core, dtype=bool))
    if indices.size < 2:
        raise AssertionError("core has fewer than two vertices")
    mass = float(np.sum(pi[indices]))
    if not math.isfinite(mass) or mass <= 0.0:
        raise AssertionError("core mass is nonpositive")
    local = pi[indices] / mass
    local_c = np.asarray(conductance, dtype=float)[np.ix_(indices, indices)] / mass
    laplacian = np.diag(np.sum(local_c, axis=1)) - local_c
    inverse = 1.0 / np.sqrt(local)
    operator = (inverse[:, None] * laplacian * inverse[None, :])
    operator = (operator + operator.T) / 2.0
    raw = np.linalg.eigvalsh(operator)
    if raw.size < 2 or not np.all(np.isfinite(raw)):
        raise AssertionError("core spectrum is nonfinite")
    root = np.sqrt(local)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(indices.size)))
    basis, _ = np.linalg.qr(frame, mode="complete")
    complement = basis[:, 1:]
    projected = (complement.T @ operator @ complement)
    values = np.linalg.eigvalsh((projected + projected.T) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("induced core is disconnected or nonpositive")
    return {
        "size": int(indices.size),
        "mass": mass,
        "projected_gap": float(values[0]),
        "minimum_local_mass": float(np.min(local)),
        "raw_zero_residual": abs(float(raw[0])),
    }


def lyapunov(weights: np.ndarray, conductance: np.ndarray, alpha: float, theta: float) -> dict[str, Any]:
    pi = np.asarray(weights, dtype=float)
    if pi.ndim != 1 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid positive conditional law")
    pi = pi / float(np.sum(pi))
    if not math.isfinite(alpha) or alpha <= 0.0 or not math.isfinite(theta) or theta <= 0.0:
        raise AssertionError("alpha and theta must be positive")
    logs = np.log(pi)
    phi = float(np.max(logs)) - logs
    scaled = alpha * phi
    if not np.all(np.isfinite(scaled)) or float(np.max(scaled)) >= 700.0:
        raise AssertionError("Lyapunov exponent overflow")
    potential = np.exp(scaled)
    c = np.asarray(conductance, dtype=float)
    generator = (c @ potential - np.sum(c, axis=1) * potential) / pi
    rates = -generator / potential
    if not np.all(np.isfinite(rates)):
        raise AssertionError("nonfinite Lyapunov rate")
    tail = phi >= theta
    core = ~tail
    tail_mass = float(np.sum(pi[tail]))
    core_mass = float(np.sum(pi[core]))
    if tail.any():
        minimum = float(np.min(rates[tail]))
        maximum = float(np.max(rates[tail]))
    else:
        minimum = float("inf")
        maximum = float("inf")
    if core.any() and tail.any():
        boundary = np.sum(c[np.ix_(core, tail)], axis=1) / pi[core]
        maximum_boundary = float(np.max(boundary))
    else:
        maximum_boundary = 0.0
    return {
        "tail": tail,
        "core": core,
        "tail_count": int(np.sum(tail)),
        "core_count": int(np.sum(core)),
        "tail_mass": tail_mass,
        "core_mass": core_mass,
        "minimum_tail_drift": minimum,
        "maximum_tail_drift": maximum,
        "maximum_boundary_rate": maximum_boundary,
        "minimum_phi": float(np.min(phi)),
        "maximum_phi": float(np.max(phi)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    pairs = [(int(item["volume"]), [int(x) for x in item["cutoff_dimensions"]]) for item in fixture["volume_cutoffs"]]
    dimensions = [(volume, dimension) for volume, values in pairs for dimension in values]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    alphas = [float(Fraction(value)) for value in fixture["alpha_values"]]
    thetas = [float(value) for value in fixture["tail_thresholds"]]
    chi = float(Fraction(str(fixture["chi"])))
    gap_floor = float(fixture["gap_floor"])
    drift_floor = float(fixture["drift_floor"])
    core_mass_floor = float(fixture["core_mass_floor"])
    tail_mass_cap = float(fixture["tail_mass_cap"])
    probability_floor = float(fixture["probability_floor"])
    tolerance = float(fixture["crosscheck_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 500:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = (
        "finite_log_domain_rows_closed",
        "finite_lyapunov_drift_closed",
        "finite_core_gap_closed",
        "finite_tail_mass_accounting_closed",
        "finite_boundary_rate_closed",
        "finite_growing_volume_stress_closed",
    )
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("identity", manifest["result_id"] == "R-419" and manifest["exploration_id"] == "EXP-001264" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-419/EXP-001264/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("volume grid", pairs == [(2, [3, 4, 5, 6, 8, 10, 12]), (3, [3, 4, 5, 6]), (4, [4])], pairs, "declared growing-volume grid", "fixture")
    check("beta/orientation grid", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed beta and orientation grid", "fixture")
    check("alpha/theta grid", alphas == [0.025, 0.05, 0.1] and thetas == [4.0, 8.0, 12.0], [alphas, thetas], "fixed alpha and theta grid", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")

    minimum_full = float("inf")
    maximum_full = 0.0
    minimum_core = float("inf")
    maximum_core = 0.0
    minimum_core_mass = float("inf")
    maximum_tail_mass = 0.0
    minimum_boundary = float("inf")
    maximum_boundary = 0.0
    drift_values = {f"alpha={alpha:g}/theta={theta:g}": [] for alpha in alphas for theta in thetas}
    tail_counts = {f"theta={theta:g}": 0 for theta in thetas}
    drift_counts = {key: 0 for key in drift_values}
    profiles: list[dict[str, Any]] = []
    total_rows = 0
    total_profiles = 0

    for volume, dimension in dimensions:
        q_ops, hamiltonian, _terms = r399.split_system(volume, dimension, fixture)
        del q_ops
        basis = r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        profile_records: list[dict[str, Any]] = []
        for beta in betas:
            log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} log law", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= tolerance, [float(np.min(log_reference)), float(np.max(log_reference)), float(np.sum(np.exp(log_reference)))], "finite normalized log law", "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_full_gap": float("inf"), "minimum_core_gap": float("inf"), "minimum_core_mass": float("inf"), "maximum_tail_mass": {f"theta={theta:g}": 0.0 for theta in thetas}, "minimum_tail_drift": {key: float("inf") for key in drift_values}, "maximum_boundary_rate": 0.0}
                for weights, minimum_log_row in r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    check(f"V={volume} d={dimension} {orientation} row log", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "log-domain")
                    graph = r416.projected_graph(weights, momentum, chi)
                    full_gap = float(graph["projected_gap"])
                    minimum_full = min(minimum_full, full_gap)
                    maximum_full = max(maximum_full, full_gap)
                    profile["minimum_full_gap"] = min(profile["minimum_full_gap"], full_gap)
                    for theta in thetas:
                        base = lyapunov(weights, graph["conductance"], alphas[0], theta)
                        core = induced_core_gap(weights, graph["conductance"], base["core"])
                        check(f"V={volume} d={dimension} beta={beta} {orientation} row theta={theta:g} core-tail", core["projected_gap"] > gap_floor and base["core_mass"] > core_mass_floor and base["tail_mass"] < tail_mass_cap, [core["projected_gap"], base["core_mass"], base["tail_mass"]], f"gap>{gap_floor}, core mass>{core_mass_floor}, tail mass<{tail_mass_cap}", "core-tail")
                        minimum_core = min(minimum_core, float(core["projected_gap"]))
                        maximum_core = max(maximum_core, float(core["projected_gap"]))
                        minimum_core_mass = min(minimum_core_mass, base["core_mass"])
                        maximum_tail_mass = max(maximum_tail_mass, base["tail_mass"])
                        minimum_boundary = min(minimum_boundary, base["maximum_boundary_rate"])
                        maximum_boundary = max(maximum_boundary, base["maximum_boundary_rate"])
                        theta_key = f"theta={theta:g}"
                        profile["minimum_core_gap"] = min(profile["minimum_core_gap"], float(core["projected_gap"]))
                        profile["minimum_core_mass"] = min(profile["minimum_core_mass"], base["core_mass"])
                        profile["maximum_tail_mass"][theta_key] = max(profile["maximum_tail_mass"][theta_key], base["tail_mass"])
                        profile["maximum_boundary_rate"] = max(profile["maximum_boundary_rate"], base["maximum_boundary_rate"])
                        if base["tail_count"] > 0:
                            tail_counts[theta_key] += 1
                        for alpha in alphas:
                            value = lyapunov(weights, graph["conductance"], alpha, theta)
                            check(f"V={volume} d={dimension} beta={beta} {orientation} alpha={alpha:g} theta={theta:g} drift", value["tail_count"] == 0 or value["minimum_tail_drift"] > drift_floor, [value["tail_count"], value["minimum_tail_drift"]], f"positive drift when nonempty, floor {drift_floor}", "Lyapunov")
                            key = f"alpha={alpha:g}/theta={theta:g}"
                            if value["tail_count"] > 0:
                                drift_values[key].append(float(value["minimum_tail_drift"]))
                                drift_counts[key] += 1
                                profile["minimum_tail_drift"][key] = min(profile["minimum_tail_drift"][key], float(value["minimum_tail_drift"]))
                    total_rows += 1
                    profile["row_count"] += 1
                expected_rows = sum(dimension ** radius for radius in range(volume))
                check(f"V={volume} d={dimension} {orientation} prefix coverage", profile["row_count"] == expected_rows, profile["row_count"], expected_rows, "coverage")
                total_profiles += 1
                profile_records.append(profile)
        profiles.extend(profile_records)

    expected_profiles = len(dimensions) * len(betas) * len(orientations)
    expected_rows = sum(2 * len(betas) * sum(dimension ** radius for radius in range(volume)) for volume, dimension in dimensions)
    check("profile coverage", total_profiles == expected_profiles, total_profiles, expected_profiles, "coverage")
    check("row coverage", total_rows == expected_rows, total_rows, expected_rows, "coverage")
    check("full gap envelope", minimum_full > gap_floor, minimum_full, f">{gap_floor}", "full graph")
    check("core envelope", minimum_core > gap_floor and minimum_core_mass > core_mass_floor and maximum_tail_mass < tail_mass_cap, [minimum_core, minimum_core_mass, maximum_tail_mass], f"gap>{gap_floor}, core mass>{core_mass_floor}, tail mass<{tail_mass_cap}", "core-tail")
    check("tail rows covered", all(tail_counts[key] > 0 for key in tail_counts), tail_counts, "positive tail rows for every threshold", "coverage")
    check("drift rows covered", all(drift_counts[key] > 0 for key in drift_counts), drift_counts, "positive drift rows for every alpha/theta", "coverage")
    for key, values in drift_values.items():
        check(f"aggregate {key} drift", values and min(values) > drift_floor, [len(values), min(values) if values else None], f"nonempty and >{drift_floor}", "Lyapunov")
    check("boundary finite", math.isfinite(minimum_boundary) and math.isfinite(maximum_boundary) and minimum_boundary >= 0.0, [minimum_boundary, maximum_boundary], "finite nonnegative", "boundary")

    derived = {
        "system_count": len(dimensions),
        "profile_count": total_profiles,
        "comparison_row_count": total_rows,
        "volume_cutoffs": [{"volume": volume, "cutoff_dimensions": values} for volume, values in pairs],
        "beta_values": betas,
        "orientations": orientations,
        "alpha_values": alphas,
        "tail_thresholds": thetas,
        "minimum_full_projected_gap": minimum_full,
        "maximum_full_projected_gap": maximum_full,
        "minimum_core_gap": minimum_core,
        "maximum_core_gap": maximum_core,
        "minimum_core_mass": minimum_core_mass,
        "maximum_tail_mass": maximum_tail_mass,
        "minimum_tail_drift_by_alpha_theta": {key: min(values) for key, values in drift_values.items()},
        "maximum_tail_drift_by_alpha_theta": {key: max(values) for key, values in drift_values.items()},
        "tail_row_count_by_theta": tail_counts,
        "drift_row_count_by_alpha_theta": drift_counts,
        "minimum_boundary_rate": minimum_boundary,
        "maximum_boundary_rate": maximum_boundary,
        "profiles": profiles,
        "finite_log_domain_rows_closed": True,
        "finite_lyapunov_drift_closed": True,
        "finite_core_gap_closed": True,
        "finite_tail_mass_accounting_closed": True,
        "finite_boundary_rate_closed": True,
        "finite_growing_volume_stress_closed": True,
        "volume_uniform_lyapunov_closed": False,
        "cutoff_uniform_lyapunov_closed": False,
        "phase_uniform_lyapunov_closed": False,
        "exhaustion_uniform_lyapunov_closed": False,
        "observable_tail_control_closed": False,
        "global_poincare_closed": False,
        "common_core_closed": False,
        "common_split_rule_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r419-primary/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-419", "exploration_id": "EXP-001264", "verdict": "PASS", "checks": checks, "assertion_count": assertion_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    minimum_drift = min(value for values in drift_values.values() for value in values)
    print(f"R-419 PRIMARY PASS {assertion_count}/{assertion_count} systems={len(dimensions)} profiles={total_profiles} rows={total_rows} full_gap_min={minimum_full:.6g} core_gap_min={minimum_core:.6g} tail_mass_max={maximum_tail_mass:.6g} drift_min={minimum_drift:.6g}")
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
