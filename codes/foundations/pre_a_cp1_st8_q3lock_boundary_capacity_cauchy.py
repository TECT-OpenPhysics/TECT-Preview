#!/usr/bin/env python3
"""Finite boundary-capacity Cauchy audit for the R-422 residual split.

For disjoint core/tail supports the transformed Laplacian cross block has
entries c_ij/sqrt(pi_i*pi_j).  A weighted Cauchy--Schwarz estimate bounds its
operator norm by sqrt(rho_C*rho_T), where rho_C and rho_T are the two directed
boundary capacities.  This is a finite sufficient-budget diagnostic; it does
not assert a uniform Q3 estimate or a physical spectral gap.
"""

from __future__ import annotations

import argparse
import hashlib
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-boundary-capacity-cauchy-manifest.json"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R421_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-tail-hardy-ground-state-transform-manifest.json"
SLUG = "boundary_capacity_cauchy"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_residual_core_tail_reserve as r422  # noqa: E402


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def boundary_capacities(pi: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> tuple[float, float, float]:
    """Return directed core/tail rates and the Cauchy capacity envelope."""
    weights = np.asarray(pi, dtype=float)
    c = np.asarray(conductance, dtype=float)
    core_indices = np.flatnonzero(np.asarray(core, dtype=bool))
    tail_indices = np.flatnonzero(np.asarray(tail, dtype=bool))
    if core_indices.size < 1 or tail_indices.size < 1:
        raise AssertionError("capacity requires nonempty core and tail")
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("capacity requires positive weights")
    if not np.all(np.isfinite(c)) or np.any(c < 0.0):
        raise AssertionError("capacity requires nonnegative conductance")
    core_rates = np.sum(c[np.ix_(core_indices, tail_indices)], axis=1) / weights[core_indices]
    tail_rates = np.sum(c[np.ix_(core_indices, tail_indices)], axis=0) / weights[tail_indices]
    rho_core = float(np.max(core_rates))
    rho_tail = float(np.max(tail_rates))
    if not all(math.isfinite(value) and value >= 0.0 for value in (rho_core, rho_tail)):
        raise AssertionError("invalid directed boundary capacity")
    return rho_core, rho_tail, math.sqrt(rho_core * rho_tail)


def edge_cauchy_bound(x: np.ndarray, y: np.ndarray, pi: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> tuple[float, float]:
    """Check the edgewise Cauchy factors for one normalized transformed probe."""
    core_indices = np.flatnonzero(np.asarray(core, dtype=bool))
    tail_indices = np.flatnonzero(np.asarray(tail, dtype=bool))
    c = np.asarray(conductance, dtype=float)
    weights = np.asarray(pi, dtype=float)
    block = c[np.ix_(core_indices, tail_indices)]
    edge = block / np.sqrt(weights[core_indices, None] * weights[tail_indices][None, :])
    lhs = abs(float(x @ edge @ y))
    first = float(np.sum(block * (x[:, None] ** 2) / weights[core_indices, None]))
    second = float(np.sum(block * (y[None, :] ** 2) / weights[tail_indices][None, :]))
    if first < -1.0e-12 or second < -1.0e-12:
        raise AssertionError("negative Cauchy factor")
    return lhs, math.sqrt(max(first, 0.0) * max(second, 0.0))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    r419_manifest = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))
    r421_manifest = json.loads(R421_MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    parent_fixture = r419_manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    crosscheck_tolerance = float(fixture["crosscheck_tolerance"])
    reserve_tolerance = float(fixture["reserve_tolerance"])
    probability_floor = float(fixture["probability_floor"])
    rate_floor = float(fixture["rate_floor"])
    spectral_floor = float(fixture["spectral_floor"])
    alpha = float(Fraction(str(fixture["alpha"])))
    theta = float(Fraction(str(fixture["tail_threshold"])))
    chi = float(Fraction(str(parent_fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["q3_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 700:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = [
        "finite_directed_capacity_closed",
        "finite_cauchy_cross_bound_closed",
        "finite_capacity_reserve_closed",
        "finite_capacity_boundary_rows_recorded",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-423" and manifest["exploration_id"] == "EXP-001268" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-423/EXP-001268/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("parent identity", parent["result_id"] == "R-422" and parent["exploration_id"] == "EXP-001267", [parent["result_id"], parent["exploration_id"]], "R-422/EXP-001267", "authority")
    check("R-421 identity", r421_manifest["result_id"] == "R-421" and r421_manifest["exploration_id"] == "EXP-001266", [r421_manifest["result_id"], r421_manifest["exploration_id"]], "R-421/EXP-001266", "authority")
    check("fixture grid", pairs == [(2, 3), (2, 6), (2, 12), (3, 3), (3, 4), (4, 4)], pairs, "declared Q3 systems", "fixture")
    check("beta/orientation", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed R-422 grid", "fixture")
    check("positive parameters", alpha > 0.0 and theta > 0.0 and chi > 0.0 and rate_floor > 0.0 and spectral_floor > 0.0, [alpha, theta, chi, rate_floor, spectral_floor], ">0", "fixture")

    row_count = 0
    tail_rows = 0
    eligible_rows = 0
    positive_rows = 0
    nonpositive_rows = 0
    exact_cross: list[float] = []
    capacities: list[float] = []
    safe_capacity_reserves: list[float] = []
    cauchy_margins: list[float] = []
    systems: list[dict[str, Any]] = []

    for volume, dimension in pairs:
        _q_ops, hamiltonian, _terms = r422.r419.r399.split_system(volume, dimension, parent_fixture)
        basis = r422.r419.r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r422.r419.r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        system_rows = 0
        system_tail_rows = 0
        system_eligible = 0
        system_positive = 0
        system_nonpositive = 0
        system_min_capacity = float("inf")
        system_min_reserve = float("inf")
        for beta in betas:
            log_reference, _direct, _shifted = r422.r419.r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} normalized", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= crosscheck_tolerance, float(np.sum(np.exp(log_reference))), 1.0, "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                for weights, minimum_log_row in r422.r419.r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    row_count += 1
                    system_rows += 1
                    check(f"V={volume} d={dimension} {orientation} row positivity", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "rows")
                    graph = r422.r419.r416.projected_graph(weights, momentum, chi)
                    pi = np.asarray(graph["weights"], dtype=float)
                    conductance = np.asarray(graph["conductance"], dtype=float)
                    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
                    inverse = 1.0 / np.sqrt(pi)
                    operator = inverse[:, None] * laplacian * inverse[None, :]
                    operator = (operator + operator.T) / 2.0
                    phi = float(np.max(np.log(pi))) - np.log(pi)
                    potential = np.exp(alpha * phi)
                    rates = -(conductance @ potential - np.sum(conductance, axis=1) * potential) / pi / potential
                    tail = phi >= theta
                    core = ~tail
                    if bool(np.any(tail)):
                        tail_rows += 1
                        system_tail_rows += 1
                        check(f"V={volume} d={dimension} {orientation} tail rate", float(np.min(rates[tail])) > rate_floor, float(np.min(rates[tail])), f">{rate_floor}", "tail Hardy")
                    if int(np.sum(tail)) < 2 or int(np.sum(core)) < 2:
                        continue
                    eligible_rows += 1
                    system_eligible += 1
                    core_basis = r422.zero_mean_basis(pi, np.where(core)[0])
                    tail_basis = r422.zero_mean_basis(pi, np.where(tail)[0])
                    core_matrix = (core_basis.T @ operator @ core_basis)
                    tail_matrix = (tail_basis.T @ operator @ tail_basis)
                    cross_matrix = core_basis.T @ operator @ tail_basis
                    core_matrix = (core_matrix + core_matrix.T) / 2.0
                    tail_matrix = (tail_matrix + tail_matrix.T) / 2.0
                    core_gap = float(np.linalg.eigvalsh(core_matrix)[0])
                    direct_tail_gap = float(np.linalg.eigvalsh(tail_matrix)[0])
                    cross_norm = float(np.linalg.svd(cross_matrix, compute_uv=False)[0]) if cross_matrix.size else 0.0
                    kappa = float(np.min(rates[tail]))
                    rho_core, rho_tail, capacity = boundary_capacities(pi, conductance, core, tail)
                    capacity_reserve = min(core_gap, kappa) - capacity
                    residual = np.block([[core_matrix, cross_matrix], [cross_matrix.T, tail_matrix]])
                    residual = (residual + residual.T) / 2.0
                    actual_gap = float(np.linalg.eigvalsh(residual)[0])
                    check(f"V={volume} d={dimension} {orientation} core positivity", core_gap > spectral_floor and math.isfinite(core_gap), core_gap, f">{spectral_floor}", "core form")
                    check(f"V={volume} d={dimension} {orientation} tail reuse", direct_tail_gap + reserve_tolerance >= kappa and direct_tail_gap > spectral_floor, [direct_tail_gap, kappa], f"direct tail >= kappa-{reserve_tolerance}", "tail Hardy")
                    check(f"V={volume} d={dimension} {orientation} capacity inputs", rho_core >= 0.0 and rho_tail >= 0.0 and math.isfinite(capacity), [rho_core, rho_tail, capacity], "finite nonnegative directed capacities", "capacity")
                    check(f"V={volume} d={dimension} {orientation} cross Cauchy", cross_norm <= capacity + crosscheck_tolerance, [cross_norm, capacity], f"cross norm <= capacity+{crosscheck_tolerance}", "capacity")
                    check(f"V={volume} d={dimension} {orientation} capacity reserve", actual_gap + reserve_tolerance >= capacity_reserve, [actual_gap, capacity_reserve], f"actual gap >= capacity reserve-{reserve_tolerance}", "reserve")
                    # Four deterministic normalized probes independently exercise the edgewise factors.
                    for probe_index in range(4):
                        x = np.sin((np.arange(core_basis.shape[1], dtype=float) + 1.0) * (probe_index + 1.0))
                        y = np.cos((np.arange(tail_basis.shape[1], dtype=float) + 1.0) * (probe_index + 0.5))
                        x /= max(float(np.linalg.norm(x)), 1.0)
                        y /= max(float(np.linalg.norm(y)), 1.0)
                        x_full = core_basis @ x
                        y_full = tail_basis @ y
                        lhs, edge_bound = edge_cauchy_bound(x_full[np.flatnonzero(core)], y_full[np.flatnonzero(tail)], pi, conductance, core, tail)
                        check(f"V={volume} d={dimension} {orientation} probe={probe_index} edge Cauchy", lhs <= edge_bound + crosscheck_tolerance and edge_bound <= capacity + crosscheck_tolerance, [lhs, edge_bound, capacity], f"lhs<=edge<=capacity+{crosscheck_tolerance}", "capacity")
                        cauchy_margins.append(edge_bound - lhs)
                    exact_cross.append(cross_norm)
                    capacities.append(capacity)
                    safe_capacity_reserves.append(capacity_reserve)
                    system_min_capacity = min(system_min_capacity, capacity)
                    system_min_reserve = min(system_min_reserve, capacity_reserve)
                    if capacity_reserve > reserve_tolerance:
                        positive_rows += 1
                        system_positive += 1
                    else:
                        nonpositive_rows += 1
                        system_nonpositive += 1
        check(f"V={volume} d={dimension} coverage", system_rows > 0 and system_eligible == system_positive + system_nonpositive, [system_rows, system_tail_rows, system_eligible, system_positive, system_nonpositive], "eligible rows partitioned", "coverage")
        systems.append({"volume": volume, "dimension": dimension, "row_count": system_rows, "tail_row_count": system_tail_rows, "eligible_row_count": system_eligible, "positive_capacity_reserve_rows": system_positive, "nonpositive_capacity_reserve_rows": system_nonpositive, "minimum_capacity": system_min_capacity if system_eligible else None, "minimum_capacity_reserve": system_min_reserve if system_eligible else None})

    check("row coverage", row_count > 0 and tail_rows > 0, [row_count, tail_rows], "positive finite row and tail coverage", "coverage")
    check("eligible coverage", eligible_rows == positive_rows + nonpositive_rows and eligible_rows > 0, [eligible_rows, positive_rows, nonpositive_rows], "eligible rows partitioned and nonempty", "coverage")
    check("capacity aggregate", all(math.isfinite(value) and value >= 0.0 for value in capacities), [min(capacities), max(capacities)], "finite nonnegative capacities", "aggregate")
    check("cross domination aggregate", all(lhs <= bound + crosscheck_tolerance for lhs, bound in zip(exact_cross, capacities)), [max(exact_cross), max(capacities)], f"cross<=capacity+{crosscheck_tolerance}", "aggregate")
    check("capacity boundary retained", nonpositive_rows > 0 and positive_rows >= 0, [positive_rows, nonpositive_rows], "nonpositive capacity-budget rows retained without clipping", "boundary")
    check("probe margins", min(cauchy_margins, default=0.0) + crosscheck_tolerance >= 0.0, min(cauchy_margins, default=0.0), f">=-{crosscheck_tolerance}", "aggregate")

    derived = {
        "system_count": len(pairs),
        "conditional_row_count": row_count,
        "tail_row_count": tail_rows,
        "eligible_row_count": eligible_rows,
        "positive_capacity_reserve_row_count": positive_rows,
        "nonpositive_capacity_reserve_row_count": nonpositive_rows,
        "minimum_exact_cross_norm": min(exact_cross, default=0.0),
        "maximum_exact_cross_norm": max(exact_cross, default=0.0),
        "minimum_capacity": min(capacities, default=0.0),
        "maximum_capacity": max(capacities, default=0.0),
        "minimum_capacity_reserve": min(safe_capacity_reserves, default=0.0),
        "maximum_capacity_reserve": max(safe_capacity_reserves, default=0.0),
        "minimum_probe_cauchy_margin": min(cauchy_margins, default=0.0),
        "systems": systems,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r423-primary/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "primary",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "parent": sha256(PARENT), "r419_manifest": sha256(R419_MANIFEST), "r421_manifest": sha256(R421_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-423 PRIMARY PASS {assertion_count}/{assertion_count} rows={row_count} eligible={eligible_rows} positive={positive_rows} nonpositive={nonpositive_rows} capacity=[{min(capacities):.6g},{max(capacities):.6g}] reserve=[{min(safe_capacity_reserves):.6g},{max(safe_capacity_reserves):.6g}]")
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
