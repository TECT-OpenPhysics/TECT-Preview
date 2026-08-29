#!/usr/bin/env python3
"""Independent reconstruction of the R-417 core-tail Lyapunov corridor."""

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
SLUG = "lyapunov_core_tail_corridor"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-lyapunov-core-tail-corridor-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"
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


def model(volume: int, dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [embed(q_single, site, volume, identity) for site in range(volume)]
    momenta = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    coupling, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    zero = np.zeros_like(coordinates[0])
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(coordinates, momenta)]
    bonds: list[np.ndarray] = []
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        bonds.append(coupling * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
    return hermitian(sum(onsite + bonds, zero))


def coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def logsumexp(values: np.ndarray) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0 or not np.all(np.isfinite(array)):
        raise AssertionError("invalid log-sum-exp row")
    maximum = float(np.max(array))
    return maximum + math.log(float(np.sum(np.exp(array - maximum))))


def log_distribution(hamiltonian: np.ndarray, basis: np.ndarray, beta: float, dimension: int, volume: int) -> np.ndarray:
    energies, vectors = np.linalg.eigh(hermitian(hamiltonian))
    shifted = energies - float(np.min(energies))
    coefficients = np.log(np.maximum(np.abs(basis.conj().T @ vectors), np.finfo(float).tiny))
    terms = -beta * shifted[None, :] + 2.0 * coefficients
    logs = np.array([logsumexp(row) for row in terms], dtype=float)
    logs -= logsumexp(logs)
    return logs.reshape((dimension,) * volume)


def log_marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    if not sites:
        return np.asarray([logsumexp(np.asarray(values).reshape(-1))])
    rest = [axis for axis in range(values.ndim) if axis not in sites]
    moved = np.transpose(values, sites + rest)
    flat = moved.reshape(dimension ** len(sites), -1)
    return np.array([logsumexp(row) for row in flat], dtype=float).reshape((dimension,) * len(sites))


def conditional_rows(log_reference: np.ndarray, order: list[int], dimension: int, floor: float) -> Iterable[np.ndarray]:
    for radius in range(len(order)):
        prefix = log_marginal(log_reference, order[: radius + 1], dimension)
        parent = np.asarray([0.0]) if radius == 0 else log_marginal(log_reference, order[:radius], dimension).reshape(-1)
        if not np.all(np.isfinite(prefix)) or not np.all(np.isfinite(parent)):
            raise AssertionError("nonfinite log marginal")
        for parent_log, row in zip(parent, prefix.reshape(-1, dimension)):
            log_row = row - float(parent_log)
            weights = np.exp(log_row - float(np.max(log_row)))
            weights /= float(np.sum(weights))
            if float(np.min(weights)) <= floor or not np.all(np.isfinite(weights)):
                raise AssertionError("conditional row lost positivity")
            yield weights


def momentum_matrix(dimension: int) -> np.ndarray:
    q_single, p_single = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(hermitian(q_single))
    return hermitian(vectors.conj().T @ p_single @ vectors)


def conductance(weights: np.ndarray, momentum: np.ndarray, chi: float) -> np.ndarray:
    pi = np.asarray(weights, dtype=float)
    if np.any(pi <= 0.0) or not np.all(np.isfinite(pi)):
        raise AssertionError("nonpositive graph weights")
    pi = pi / float(np.sum(pi))
    p = np.asarray(momentum, dtype=complex)
    c = (pi[:, None] + pi[None, :]) * np.square(np.abs(p)) / (2.0 * chi)
    np.fill_diagonal(c, 0.0)
    return c


def projected_gap(weights: np.ndarray, edges: np.ndarray) -> float:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    laplacian = np.diag(np.sum(edges, axis=1)) - edges
    inverse = 1.0 / np.sqrt(pi)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = hermitian(operator)
    root = np.sqrt(pi)
    root /= float(np.linalg.norm(root))
    frame = np.column_stack((root, np.eye(pi.size)))
    basis, _ = np.linalg.qr(frame, mode="complete")
    values = np.linalg.eigvalsh(hermitian(basis[:, 1:].T @ operator @ basis[:, 1:]))
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("graph is disconnected")
    return float(values[0])


def core_info(weights: np.ndarray, edges: np.ndarray, core: np.ndarray) -> dict[str, Any]:
    pi = np.asarray(weights, dtype=float)
    mask = np.asarray(core, dtype=bool)
    indices = np.flatnonzero(mask)
    if indices.size < 2:
        raise AssertionError("core is too small")
    mass = float(np.sum(pi[indices]))
    if mass <= 0.0 or not math.isfinite(mass):
        raise AssertionError("invalid core mass")
    local = pi[indices] / mass
    local_edges = edges[np.ix_(indices, indices)] / mass
    return {"size": int(indices.size), "mass": mass, "gap": projected_gap(local, local_edges), "minimum_local_mass": float(np.min(local))}


def drift_info(weights: np.ndarray, edges: np.ndarray, alpha: float, theta: float) -> dict[str, Any]:
    pi = np.asarray(weights, dtype=float)
    pi = pi / float(np.sum(pi))
    if alpha <= 0.0 or theta <= 0.0:
        raise AssertionError("positive alpha and theta required")
    logs = np.log(pi)
    phi = float(np.max(logs)) - logs
    exponent = alpha * phi
    if float(np.max(exponent)) >= 700.0:
        raise AssertionError("Lyapunov overflow")
    potential = np.exp(exponent)
    generator_potential = (edges @ potential - np.sum(edges, axis=1) * potential) / pi
    rates = -generator_potential / potential
    tail = phi >= theta
    core = ~tail
    tail_mass = float(np.sum(pi[tail]))
    core_mass = float(np.sum(pi[core]))
    if core.any() and tail.any():
        boundary = np.sum(edges[np.ix_(core, tail)], axis=1) / pi[core]
        maximum_boundary_rate = float(np.max(boundary))
    else:
        maximum_boundary_rate = 0.0
    minimum = float(np.min(rates[tail])) if tail.any() else float("inf")
    maximum = float(np.max(rates[tail])) if tail.any() else float("inf")
    return {"tail": tail, "core": core, "tail_count": int(np.sum(tail)), "core_count": int(np.sum(core)), "tail_mass": tail_mass, "core_mass": core_mass, "minimum_tail_drift": minimum, "maximum_tail_drift": maximum, "maximum_boundary_rate": maximum_boundary_rate}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["crosscheck_tolerance"])
    gap_floor = float(fixture["gap_floor"])
    drift_floor = float(fixture["drift_floor"])
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
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 500:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = ("finite_log_domain_rows_closed", "finite_lyapunov_drift_closed", "finite_core_gap_closed", "finite_tail_mass_accounting_closed", "finite_boundary_rate_closed", "finite_alpha_theta_cutoff_stress_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("identity", manifest["result_id"] == "R-417" and manifest["exploration_id"] == "EXP-001262" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-417/EXP-001262/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("fixture", volume == 2 and dimensions == sorted(set(dimensions)) and len(dimensions) >= 10 and betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"] and alphas == [0.025, 0.05, 0.1] and thetas == [4.0, 8.0, 12.0], [volume, dimensions, betas, orientations, alphas, thetas], "volume two, ordered cutoff/beta/orientation/alpha/theta grid", "fixture")

    minimum_core_gap = float("inf")
    maximum_core_gap = 0.0
    minimum_core_mass = float("inf")
    maximum_tail_mass = 0.0
    full_gaps: list[float] = []
    boundary_rates: list[float] = []
    drift_values: dict[str, list[float]] = {f"alpha={alpha:g}/theta={theta:g}": [] for alpha in alphas for theta in thetas}
    tail_masses: dict[str, list[float]] = {f"theta={theta:g}": [] for theta in thetas}
    tail_counts = {f"theta={theta:g}": 0 for theta in thetas}
    drift_counts = {key: 0 for key in drift_values}
    profiles: list[dict[str, Any]] = []
    total_rows = 0
    total_profiles = 0

    for dimension in dimensions:
        hamiltonian = model(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        momentum = momentum_matrix(dimension)
        check(f"d={dimension} basis", basis.shape == (dimension ** volume, dimension ** volume), basis.shape, (dimension ** volume, dimension ** volume), "coordinates")
        for beta in betas:
            logs = log_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"d={dimension} beta={beta} log Gibbs", np.all(np.isfinite(logs)) and abs(float(np.sum(np.exp(logs))) - 1.0) <= tolerance, [float(np.min(logs)), float(np.max(logs)), float(np.sum(np.exp(logs)))], "finite normalized log mass", "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = {"dimension": dimension, "beta": beta, "orientation": orientation, "row_count": 0, "minimum_core_gap": float("inf"), "minimum_core_mass": float("inf"), "maximum_tail_mass": {f"theta={theta:g}": 0.0 for theta in thetas}, "minimum_tail_drift": {key: float("inf") for key in drift_values}, "maximum_boundary_rate": 0.0}
                for weights in conditional_rows(logs, order, dimension, float(fixture["probability_floor"])):
                    edges = conductance(weights, momentum, chi)
                    full_gaps.append(projected_gap(weights, edges))
                    row = {"row": profile["row_count"], "theta": {}}
                    for theta in thetas:
                        base = drift_info(weights, edges, alphas[0], theta)
                        info = core_info(weights, edges, base["core"])
                        check(f"d={dimension} beta={beta} {orientation} row theta={theta} core", info["gap"] > gap_floor and base["core_mass"] > core_mass_floor and base["tail_mass"] < tail_mass_cap, [info["gap"], base["core_mass"], base["tail_mass"]], f"gap>{gap_floor}, core mass>{core_mass_floor}, tail mass<{tail_mass_cap}", "core-tail")
                        minimum_core_gap = min(minimum_core_gap, info["gap"])
                        maximum_core_gap = max(maximum_core_gap, info["gap"])
                        minimum_core_mass = min(minimum_core_mass, base["core_mass"])
                        maximum_tail_mass = max(maximum_tail_mass, base["tail_mass"])
                        boundary_rates.append(base["maximum_boundary_rate"])
                        theta_key = f"theta={theta:g}"
                        tail_masses[theta_key].append(base["tail_mass"])
                        profile["minimum_core_gap"] = min(profile["minimum_core_gap"], info["gap"])
                        profile["minimum_core_mass"] = min(profile["minimum_core_mass"], base["core_mass"])
                        profile["maximum_tail_mass"][theta_key] = max(profile["maximum_tail_mass"][theta_key], base["tail_mass"])
                        profile["maximum_boundary_rate"] = max(profile["maximum_boundary_rate"], base["maximum_boundary_rate"])
                        if base["tail_count"] > 0:
                            tail_counts[theta_key] += 1
                        row["theta"][theta_key] = {"tail_count": base["tail_count"], "tail_mass": base["tail_mass"], "core_mass": base["core_mass"], "core_size": base["core_count"], "core_gap": info["gap"], "boundary_rate": base["maximum_boundary_rate"], "drift": {}}
                        for alpha in alphas:
                            certificate = drift_info(weights, edges, alpha, theta)
                            key = f"alpha={alpha:g}/theta={theta:g}"
                            check(f"d={dimension} beta={beta} {orientation} row {key} drift", (certificate["tail_count"] == 0 or (math.isfinite(certificate["minimum_tail_drift"]) and certificate["minimum_tail_drift"] > drift_floor)), [certificate["tail_count"], certificate["minimum_tail_drift"]], f"positive tail drift when nonempty, floor {drift_floor}", "Lyapunov")
                            if certificate["tail_count"] > 0:
                                drift_values[key].append(certificate["minimum_tail_drift"])
                                drift_counts[key] += 1
                                profile["minimum_tail_drift"][key] = min(profile["minimum_tail_drift"][key], certificate["minimum_tail_drift"])
                            row["theta"][theta_key]["drift"][f"alpha={alpha:g}"] = {"tail_count": certificate["tail_count"], "minimum": certificate["minimum_tail_drift"], "maximum": certificate["maximum_tail_drift"]}
                    profiles.append(row)
                    profile["row_count"] += 1
                    total_rows += 1
                check(f"d={dimension} beta={beta} {orientation} coverage", profile["row_count"] == dimension + 1, profile["row_count"], dimension + 1, "one-site conditional coverage")
                profiles.append({"profile": profile})
                total_profiles += 1

    check("profile coverage", total_profiles == len(dimensions) * len(betas) * len(orientations), total_profiles, len(dimensions) * len(betas) * len(orientations), "coverage")
    expected_rows = len(orientations) * len(betas) * sum(dimension + 1 for dimension in dimensions)
    check("row coverage", total_rows == expected_rows, total_rows, expected_rows, "coverage")
    check("core gap positive", minimum_core_gap > gap_floor, minimum_core_gap, f">{gap_floor}", "core-tail")
    check("core and tail mass", minimum_core_mass > core_mass_floor and maximum_tail_mass < tail_mass_cap, [minimum_core_mass, maximum_tail_mass], [f">{core_mass_floor}", f"<{tail_mass_cap}"], "core-tail")
    check("tail coverage", all(value > 0 for value in tail_counts.values()), tail_counts, "positive tail rows at every threshold", "coverage")
    for key, values in drift_values.items():
        check(f"aggregate {key} drift", values and min(values) > drift_floor, [len(values), min(values) if values else None], f"nonempty and >{drift_floor}", "Lyapunov")
    check("boundary rate finite", all(math.isfinite(value) and value >= 0.0 for value in boundary_rates), [min(boundary_rates), max(boundary_rates)], "finite nonnegative", "boundary")
    check("full gap positive", min(full_gaps) > gap_floor, [min(full_gaps), max(full_gaps)], f">{gap_floor}", "comparison")
    derived = {"system_count": len(dimensions), "profile_count": total_profiles, "comparison_row_count": total_rows, "cutoff_dimensions": dimensions, "beta_values": betas, "alpha_values": alphas, "tail_thresholds": thetas, "minimum_full_projected_gap": min(full_gaps), "maximum_full_projected_gap": max(full_gaps), "minimum_core_gap": minimum_core_gap, "maximum_core_gap": maximum_core_gap, "minimum_core_mass": minimum_core_mass, "maximum_tail_mass": maximum_tail_mass, "minimum_tail_drift_by_alpha_theta": {key: min(values) for key, values in drift_values.items()}, "maximum_tail_drift_by_alpha_theta": {key: max(values) for key, values in drift_values.items()}, "tail_row_count_by_theta": tail_counts, "drift_row_count_by_alpha_theta": drift_counts, "maximum_boundary_rate": max(boundary_rates), "minimum_boundary_rate": min(boundary_rates), "tail_mass_ranges": {key: [min(values), max(values)] for key, values in tail_masses.items()}, "profiles": profiles, "finite_log_domain_rows_closed": True, "finite_lyapunov_drift_closed": True, "finite_core_gap_closed": True, "finite_tail_mass_accounting_closed": True, "finite_boundary_rate_closed": True, "finite_alpha_theta_cutoff_stress_closed": True, "cutoff_uniform_lyapunov_closed": False, "volume_uniform_lyapunov_closed": False, "observable_tail_control_closed": False, "global_poincare_closed": False, "common_core_closed": False, "common_split_rule_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}
    payload = {"schema": "tect/pre-a-r417-independent/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-417", "exploration_id": "EXP-001262", "verdict": "PASS", "checks": checks, "assertion_count": assertion_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-417 INDEPENDENT PASS {assertion_count}/{assertion_count} cutoffs={len(dimensions)} profiles={total_profiles} rows={total_rows} core_gap=[{minimum_core_gap:.6g},{maximum_core_gap:.6g}] tail_drift_min={min(min(values) for values in drift_values.values()):.6g} tail_mass_max={maximum_tail_mass:.6g}")
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
