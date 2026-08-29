#!/usr/bin/env python3
"""Finite log-domain Lyapunov core-tail corridor audit for R-417.

The route treats very small conditional masses as a tail.  A positive drift of
V_i=exp(alpha*(log(pi_max)-log(pi_i))) is recorded outside the tail, while the
induced core graph gap, core mass and core-to-tail jump rate are kept as
separate finite inputs.  This is a route discriminator, not a global
Poincare or thermodynamic theorem.
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
SLUG = "lyapunov_core_tail_corridor"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-lyapunov-core-tail-corridor-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402
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


def induced_core_gap(weights: np.ndarray, conductance: np.ndarray, core: np.ndarray, raw_zero_threshold: float) -> dict[str, Any]:
    """Return the projected positive gap on the induced core graph."""
    pi = np.asarray(weights, dtype=float)
    c = np.asarray(conductance, dtype=float)
    mask = np.asarray(core, dtype=bool)
    indices = np.flatnonzero(mask)
    if indices.size < 2:
        raise AssertionError("core has fewer than two vertices")
    mass = float(np.sum(pi[indices]))
    if not math.isfinite(mass) or mass <= 0.0:
        raise AssertionError("core mass is nonpositive")
    local = pi[indices] / mass
    local_c = c[np.ix_(indices, indices)] / mass
    laplacian = np.diag(np.sum(local_c, axis=1)) - local_c
    inverse = 1.0 / np.sqrt(local)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    raw_values = np.linalg.eigvalsh(operator)
    if raw_values.size < 2 or not np.all(np.isfinite(raw_values)):
        raise AssertionError("core graph spectrum is nonfinite")
    root = np.sqrt(local)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(indices.size)))
    basis, _ = np.linalg.qr(frame, mode="complete")
    projected_values = np.linalg.eigvalsh((basis[:, 1:].T @ operator @ basis[:, 1:] + basis[:, 1:].T @ operator @ basis[:, 1:]) / 2.0)
    if projected_values.size == 0 or not np.all(np.isfinite(projected_values)) or float(projected_values[0]) <= 0.0:
        raise AssertionError("induced core is disconnected or nonpositive")
    return {
        "size": int(indices.size),
        "mass": mass,
        "raw_zero_residual": abs(float(raw_values[0])),
        "projected_gap": float(projected_values[0]),
        "minimum_local_mass": float(np.min(local)),
        "raw_zero_threshold": raw_zero_threshold,
    }


def lyapunov_certificate(weights: np.ndarray, conductance: np.ndarray, alpha: float, theta: float) -> dict[str, Any]:
    """Compute the log-potential, tail drift and boundary rate."""
    pi = np.asarray(weights, dtype=float)
    c = np.asarray(conductance, dtype=float)
    if pi.ndim != 1 or c.shape != (pi.size, pi.size) or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid positive graph law")
    if not math.isfinite(alpha) or alpha <= 0.0 or not math.isfinite(theta) or theta <= 0.0:
        raise AssertionError("alpha and theta must be positive")
    pi = pi / float(np.sum(pi))
    log_pi = np.log(pi)
    phi = float(np.max(log_pi)) - log_pi
    scaled = alpha * phi
    if not np.all(np.isfinite(scaled)) or float(np.max(scaled)) >= 700.0:
        raise AssertionError("Lyapunov exponent overflow")
    potential = np.exp(scaled)
    row_sum = np.sum(c, axis=1)
    generator_potential = (c @ potential - row_sum * potential) / pi
    rates = -generator_potential / potential
    if not np.all(np.isfinite(rates)) or not np.all(np.isfinite(potential)):
        raise AssertionError("nonfinite Lyapunov drift")
    tail = phi >= theta
    core = ~tail
    tail_mass = float(np.sum(pi[tail]))
    core_mass = float(np.sum(pi[core]))
    if tail.any():
        minimum_tail_drift = float(np.min(rates[tail]))
        maximum_tail_drift = float(np.max(rates[tail]))
    else:
        minimum_tail_drift = float("inf")
        maximum_tail_drift = float("inf")
    if core.any() and tail.any():
        boundary_rates = np.sum(c[np.ix_(core, tail)], axis=1) / pi[core]
        maximum_boundary_rate = float(np.max(boundary_rates))
    else:
        maximum_boundary_rate = 0.0
    return {
        "alpha": alpha,
        "theta": theta,
        "tail_count": int(np.sum(tail)),
        "core_count": int(np.sum(core)),
        "tail_mass": tail_mass,
        "core_mass": core_mass,
        "minimum_tail_drift": minimum_tail_drift,
        "maximum_tail_drift": maximum_tail_drift,
        "maximum_boundary_rate": maximum_boundary_rate,
        "minimum_potential": float(np.min(potential)),
        "maximum_potential": float(np.max(potential)),
        "minimum_phi": float(np.min(phi)),
        "maximum_phi": float(np.max(phi)),
        "rates": rates,
        "core": core,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    numerical_tolerance = float(fixture["numerical_tolerance"])
    crosscheck_tolerance = float(fixture["crosscheck_tolerance"])
    gap_floor = float(fixture["gap_floor"])
    drift_floor = float(fixture["drift_floor"])
    raw_zero_threshold = float(fixture["raw_zero_threshold"])
    core_mass_floor = float(fixture["core_mass_floor"])
    tail_mass_cap = float(fixture["tail_mass_cap"])
    chi = float(Fraction(str(fixture["chi"])))
    volume = int(fixture["volume"])
    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    alphas = [float(Fraction(value)) for value in fixture["alpha_values"]]
    thetas = [float(value) for value in fixture["tail_thresholds"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
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
        "finite_alpha_theta_cutoff_stress_closed",
    )
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("identity", manifest["result_id"] == "R-417" and manifest["exploration_id"] == "EXP-001262" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-417/EXP-001262/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("fixture", volume == 2 and dimensions == sorted(set(dimensions)) and len(dimensions) >= 10 and betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"] and alphas == [0.025, 0.05, 0.1] and thetas == [4.0, 8.0, 12.0], [volume, dimensions, betas, orientations, alphas, thetas], "volume two, ordered cutoffs, beta/alpha/theta grid", "fixture")
    check("positive chi", chi > 0.0, chi, ">0", "fixture")

    profile_records: list[dict[str, Any]] = []
    drift_ranges: dict[str, list[float]] = {f"alpha={alpha:g}/theta={theta:g}": [] for alpha in alphas for theta in thetas}
    tail_mass_ranges: dict[str, list[float]] = {f"theta={theta:g}": [] for theta in thetas}
    core_gap_values: list[float] = []
    boundary_rates: list[float] = []
    core_masses: list[float] = []
    tail_masses: list[float] = []
    full_gaps: list[float] = []
    total_rows = 0
    total_profiles = 0
    tail_rows = {f"theta={theta:g}": 0 for theta in thetas}
    drift_rows = {f"alpha={alpha:g}/theta={theta:g}": 0 for alpha in alphas for theta in thetas}

    for dimension in dimensions:
        _q_ops, hamiltonian, _terms = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        for beta in betas:
            log_reference, _direct_reference, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"d={dimension} beta={beta} log Gibbs", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= crosscheck_tolerance, [float(np.min(log_reference)), float(np.max(log_reference)), float(np.sum(np.exp(log_reference)))], "finite normalized log mass", "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_core_gap": float("inf"), "minimum_tail_drift": {f"alpha={alpha:g}/theta={theta:g}": float("inf") for alpha in alphas for theta in thetas}, "maximum_tail_mass": {f"theta={theta:g}": 0.0 for theta in thetas}, "minimum_core_mass": float("inf"), "maximum_boundary_rate": 0.0, "tail_rows": {f"theta={theta:g}": 0 for theta in thetas}}
                for weights, minimum_log_row in r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"])):
                    data = r416.projected_graph(weights, momentum, chi)
                    full_gaps.append(float(data["projected_gap"]))
                    check(f"d={dimension} beta={beta} {orientation} row log", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "log-domain")
                    row_profile = {"row": profile["row_count"], "minimum_log_mass": minimum_log_row, "theta": {}}
                    for theta in thetas:
                        base = lyapunov_certificate(weights, data["conductance"], alphas[0], theta)
                        core_info = induced_core_gap(weights, data["conductance"], base["core"], raw_zero_threshold)
                        check(f"d={dimension} beta={beta} {orientation} row theta={theta} core", core_info["projected_gap"] > gap_floor and base["core_mass"] > core_mass_floor and base["tail_mass"] < tail_mass_cap, [core_info["projected_gap"], base["core_mass"], base["tail_mass"]], f"gap>{gap_floor}, core mass>{core_mass_floor}, tail mass<{tail_mass_cap}", "core-tail")
                        core_gap_values.append(core_info["projected_gap"])
                        core_masses.append(base["core_mass"])
                        tail_masses.append(base["tail_mass"])
                        boundary_rates.append(base["maximum_boundary_rate"])
                        tail_key = f"theta={theta:g}"
                        tail_mass_ranges[tail_key].append(base["tail_mass"])
                        profile["minimum_core_gap"] = min(profile["minimum_core_gap"], core_info["projected_gap"])
                        profile["minimum_core_mass"] = min(profile["minimum_core_mass"], base["core_mass"])
                        profile["maximum_boundary_rate"] = max(profile["maximum_boundary_rate"], base["maximum_boundary_rate"])
                        profile["maximum_tail_mass"][tail_key] = max(profile["maximum_tail_mass"][tail_key], base["tail_mass"])
                        if base["tail_count"] > 0:
                            tail_rows[tail_key] += 1
                            profile["tail_rows"][tail_key] += 1
                        row_profile["theta"][tail_key] = {"tail_count": base["tail_count"], "tail_mass": base["tail_mass"], "core_mass": base["core_mass"], "core_size": base["core_count"], "core_gap": core_info["projected_gap"], "boundary_rate": base["maximum_boundary_rate"], "drift": {}}
                        for alpha in alphas:
                            certificate = lyapunov_certificate(weights, data["conductance"], alpha, theta)
                            key = f"alpha={alpha:g}/theta={theta:g}"
                            check(f"d={dimension} beta={beta} {orientation} row {key} drift", np.all(np.isfinite(certificate["rates"])) and (certificate["tail_count"] == 0 or certificate["minimum_tail_drift"] > drift_floor), [certificate["tail_count"], certificate["minimum_tail_drift"]], f"positive tail drift when nonempty, floor {drift_floor}", "Lyapunov")
                            if certificate["tail_count"] > 0:
                                drift_rows[key] += 1
                                drift_ranges[key].append(certificate["minimum_tail_drift"])
                                profile["minimum_tail_drift"][key] = min(profile["minimum_tail_drift"][key], certificate["minimum_tail_drift"])
                            row_profile["theta"][tail_key]["drift"][f"alpha={alpha:g}"] = {"tail_count": certificate["tail_count"], "minimum": certificate["minimum_tail_drift"], "maximum": certificate["maximum_tail_drift"]}
                    total_rows += 1
                    profile["row_count"] += 1
                    profile_records.append(row_profile)
                check(f"d={dimension} beta={beta} {orientation} coverage", profile["row_count"] == dimension + 1, profile["row_count"], dimension + 1, "one-site conditional coverage")
                total_profiles += 1
                profile_records.append({"profile": profile})

    check("profile coverage", total_profiles == len(dimensions) * len(betas) * len(orientations), total_profiles, len(dimensions) * len(betas) * len(orientations), "coverage")
    expected_rows = len(orientations) * len(betas) * sum(dimension + 1 for dimension in dimensions)
    check("row coverage", total_rows == expected_rows, total_rows, expected_rows, "coverage")
    check("core gap positive", min(core_gap_values) > gap_floor, min(core_gap_values), f">{gap_floor}", "core-tail")
    check("core mass and tail cap", min(core_masses) > core_mass_floor and max(tail_masses) < tail_mass_cap, [min(core_masses), max(tail_masses)], [f">{core_mass_floor}", f"<{tail_mass_cap}"], "core-tail")
    check("tail rows present", all(tail_rows[key] > 0 for key in tail_rows), tail_rows, "nonempty tails at every threshold", "coverage")
    for key, values in drift_ranges.items():
        check(f"aggregate {key} drift", values and min(values) > drift_floor, [len(values), min(values) if values else None], f"nonempty and >{drift_floor}", "Lyapunov")
    check("boundary rates finite", all(math.isfinite(value) and value >= 0.0 for value in boundary_rates), [min(boundary_rates), max(boundary_rates)], "finite nonnegative", "boundary")
    check("full graph gap finite", min(full_gaps) > gap_floor, [min(full_gaps), max(full_gaps)], f">{gap_floor}", "comparison")

    derived = {
        "system_count": len(dimensions),
        "profile_count": total_profiles,
        "comparison_row_count": total_rows,
        "cutoff_dimensions": dimensions,
        "beta_values": betas,
        "alpha_values": alphas,
        "tail_thresholds": thetas,
        "minimum_full_projected_gap": min(full_gaps),
        "maximum_full_projected_gap": max(full_gaps),
        "minimum_core_gap": min(core_gap_values),
        "maximum_core_gap": max(core_gap_values),
        "minimum_core_mass": min(core_masses),
        "maximum_tail_mass": max(tail_masses),
        "minimum_tail_drift_by_alpha_theta": {key: min(values) for key, values in drift_ranges.items()},
        "maximum_tail_drift_by_alpha_theta": {key: max(values) for key, values in drift_ranges.items()},
        "tail_row_count_by_theta": tail_rows,
        "drift_row_count_by_alpha_theta": drift_rows,
        "maximum_boundary_rate": max(boundary_rates),
        "minimum_boundary_rate": min(boundary_rates),
        "tail_mass_ranges": {key: [min(values), max(values)] for key, values in tail_mass_ranges.items()},
        "profiles": profile_records,
        "finite_log_domain_rows_closed": True,
        "finite_lyapunov_drift_closed": True,
        "finite_core_gap_closed": True,
        "finite_tail_mass_accounting_closed": True,
        "finite_boundary_rate_closed": True,
        "finite_alpha_theta_cutoff_stress_closed": True,
        "cutoff_uniform_lyapunov_closed": False,
        "volume_uniform_lyapunov_closed": False,
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
    payload = {"schema": "tect/pre-a-r417-primary/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-417", "exploration_id": "EXP-001262", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-417 PRIMARY PASS {check_count}/{check_count} cutoffs={len(dimensions)} profiles={total_profiles} rows={total_rows} core_gap=[{min(core_gap_values):.6g},{max(core_gap_values):.6g}] tail_drift_min={min(min(values) for values in drift_ranges.values()):.6g} tail_mass_max={max(tail_masses):.6g}")
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
