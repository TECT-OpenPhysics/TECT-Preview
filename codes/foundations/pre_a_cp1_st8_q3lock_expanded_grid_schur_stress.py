#!/usr/bin/env python3
"""Primary finite expanded-grid stress of the R-424 Schur assembly.

The script keeps the R-419/R-422 inputs fixed and only enlarges the declared
finite (volume, cutoff) sample.  It records the exact finite Schur and
residual calculations without asserting any uniform or physical conclusion.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R422_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
R424_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-manifest.json"
R406_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
SLUG = "expanded_grid_schur_stress"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_residual_core_tail_reserve as r422  # noqa: E402
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def q(value: Any) -> float:
    return float(Fraction(str(value)))


def direct_residual_gap(pi: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> float:
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(pi)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    core_basis = r422.zero_mean_basis(pi, np.flatnonzero(core))
    tail_basis = r422.zero_mean_basis(pi, np.flatnonzero(tail))
    block = np.column_stack((core_basis, tail_basis))
    projected = block.T @ operator @ block
    values = np.linalg.eigvalsh((projected + projected.T) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("direct residual projection is not positive")
    return float(values[0])


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r419_manifest = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))
    fixture = r419_manifest["finite_fixture"]
    local = manifest["finite_fixture"]
    tolerance = q(local["numerical_tolerance"])
    comparison_tolerance = q(local["comparison_tolerance"])
    gap_floor = q(local["gap_floor"])
    probability_floor = q(local["probability_floor"])
    alpha = q(local["alpha"])
    theta = q(local["tail_threshold"])
    chi = q(fixture["chi"])
    betas = [q(value) for value in local["beta_values"]]
    orientations = list(local["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in local["q3_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_pairs = [(2, 3), (2, 4), (2, 5), (2, 6), (2, 8), (2, 10), (2, 12), (3, 3), (3, 4), (3, 5), (3, 6), (4, 4)]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 1000:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = [
        "finite_expanded_grid_assembly_closed",
        "finite_harmonic_coarse_schur_closed",
        "finite_residual_reuse_closed",
        "finite_combined_lower_envelope_closed",
        "finite_coverage_boundary_recorded",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-425" and manifest["exploration_id"] == "EXP-001270" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-425/EXP-001270/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("expanded grid", pairs == expected_pairs and len(pairs) == len(set(pairs)), pairs, expected_pairs, "fixture")
    check("beta/orientation", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed R-424 inputs", "fixture")
    check("fixed alpha/theta", alpha == 0.025 and theta == 4.0 and probability_floor > 0.0 and gap_floor > 0.0, [alpha, theta, probability_floor, gap_floor], "alpha=1/40, theta=4, positive floors", "fixture")
    check("upstream hashes", sha256(R419_MANIFEST) == manifest["upstream_authority"]["r419_sha256"] and sha256(R422_MANIFEST) == manifest["upstream_authority"]["r422_sha256"] and sha256(R424_MANIFEST) == manifest["upstream_authority"]["r424_sha256"] and sha256(R406_MANIFEST) == manifest["upstream_authority"]["r406_sha256"], "hash-pinned parents", "declared SHA-256 values", "authority")

    row_count = 0
    tail_row_count = 0
    eligible_rows = 0
    combined_rows = 0
    coarse_gaps: list[float] = []
    residual_gaps: list[float] = []
    combined_gaps: list[float] = []
    residual_differences: list[float] = []
    lower_margins: list[float] = []
    systems: list[dict[str, Any]] = []

    for volume, dimension in pairs:
        _q_ops, hamiltonian, _terms = r419.r399.split_system(volume, dimension, fixture)
        basis = r419.r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r419.r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        system_rows = 0
        system_tail_rows = 0
        system_eligible = 0
        system_combined = 0
        system_min_coarse = math.inf
        system_min_residual = math.inf
        system_min_combined = math.inf
        for beta in betas:
            log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            normalized = float(np.sum(np.exp(log_reference)))
            check(f"V={volume} d={dimension} beta={beta} normalized", np.all(np.isfinite(log_reference)) and abs(normalized - 1.0) <= comparison_tolerance, normalized, 1.0, "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                for weights, minimum_log_row in r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    row_count += 1
                    system_rows += 1
                    check(f"V={volume} d={dimension} {orientation} row", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "positive conditional row", "rows")
                    graph = r416.projected_graph(weights, momentum, chi)
                    pi = np.asarray(graph["weights"], dtype=float)
                    conductance = np.asarray(graph["conductance"], dtype=float)
                    check(f"V={volume} d={dimension} {orientation} graph", np.all(np.isfinite(pi)) and np.all(pi > 0.0) and np.all(np.isfinite(conductance)) and np.all(conductance >= 0.0) and np.max(np.abs(conductance - conductance.T)) <= tolerance, [float(np.min(pi)), float(np.max(np.abs(conductance - conductance.T)))], "positive reversible graph", "graph")
                    phi = float(np.max(np.log(pi))) - np.log(pi)
                    tail = phi >= theta
                    core = ~tail
                    if bool(np.any(tail)):
                        tail_row_count += 1
                        system_tail_rows += 1
                    if int(np.sum(tail)) < 2 or int(np.sum(core)) < 2:
                        continue
                    eligible_rows += 1
                    system_eligible += 1
                    data = r406.harmonic_split(pi, conductance, [np.flatnonzero(core), np.flatnonzero(tail)])
                    direct = direct_residual_gap(pi, conductance, core, tail)
                    coarse = float(data["coarse_gap"])
                    residual = float(data["residual_gap"])
                    combined = float(data["decomposition_gap"])
                    difference = abs(residual - direct)
                    margin = float(data["minimum_lower_bound_margin"])
                    check(f"V={volume} d={dimension} {orientation} coarse", math.isfinite(coarse) and coarse > gap_floor, coarse, f">{gap_floor}", "coarse Schur")
                    check(f"V={volume} d={dimension} {orientation} residual", math.isfinite(residual) and residual > gap_floor, residual, f">{gap_floor}", "residual")
                    check(f"V={volume} d={dimension} {orientation} residual reuse", difference <= comparison_tolerance, difference, f"<={comparison_tolerance}", "R-422 reuse")
                    check(f"V={volume} d={dimension} {orientation} combined", math.isfinite(combined) and combined > gap_floor and combined <= 0.5 * min(coarse, residual) + comparison_tolerance, [combined, coarse, residual], "positive half-minimum envelope", "combined")
                    check(f"V={volume} d={dimension} {orientation} split", float(data["max_energy_residual"]) <= tolerance and float(data["max_variance_envelope_deficit"]) <= tolerance and margin >= -tolerance, [data["max_energy_residual"], data["max_variance_envelope_deficit"], margin], f"split residuals <= {tolerance}", "harmonic split")
                    coarse_gaps.append(coarse)
                    residual_gaps.append(residual)
                    combined_gaps.append(combined)
                    residual_differences.append(difference)
                    lower_margins.append(margin)
                    system_min_coarse = min(system_min_coarse, coarse)
                    system_min_residual = min(system_min_residual, residual)
                    system_min_combined = min(system_min_combined, combined)
                    combined_rows += 1
                    system_combined += 1
        expected_system_rows = 2 * sum(dimension**radius for radius in range(volume)) * len(betas)
        check(f"V={volume} d={dimension} coverage", system_rows == expected_system_rows and system_eligible == system_combined, [system_rows, expected_system_rows, system_eligible, system_combined], "all prefixes and eligible rows assembled", "coverage")
        systems.append({"volume": volume, "dimension": dimension, "row_count": system_rows, "tail_row_count": system_tail_rows, "eligible_row_count": system_eligible, "combined_row_count": system_combined, "minimum_coarse_schur_gap": system_min_coarse if system_eligible else None, "minimum_residual_gap": system_min_residual if system_eligible else None, "minimum_combined_gap": system_min_combined if system_eligible else None})

    check("row coverage", row_count > 0 and tail_row_count > 0, [row_count, tail_row_count], "finite rows and nonempty tails", "coverage")
    check("eligible coverage", eligible_rows > 0 and combined_rows == eligible_rows, [eligible_rows, combined_rows], "all eligible rows assembled", "coverage")
    check("positive aggregate", min(coarse_gaps) > gap_floor and min(residual_gaps) > gap_floor and min(combined_gaps) > gap_floor, [min(coarse_gaps), min(residual_gaps), min(combined_gaps)], f">{gap_floor}", "aggregate")
    check("residual comparison aggregate", max(residual_differences) <= comparison_tolerance, max(residual_differences), f"<={comparison_tolerance}", "R-422 reuse")
    check("harmonic margins", min(lower_margins) >= -tolerance, min(lower_margins), f">=-{tolerance}", "harmonic split")
    check("support boundary retained", any(item["eligible_row_count"] == 0 for item in systems) and any(item["eligible_row_count"] > 0 for item in systems), [item["eligible_row_count"] for item in systems], "ineligible and eligible systems both retained", "boundary")

    derived = {
        "system_count": len(pairs),
        "conditional_row_count": row_count,
        "tail_row_count": tail_row_count,
        "eligible_row_count": eligible_rows,
        "combined_row_count": combined_rows,
        "minimum_coarse_schur_gap": min(coarse_gaps),
        "maximum_coarse_schur_gap": max(coarse_gaps),
        "minimum_residual_gap": min(residual_gaps),
        "maximum_residual_gap": max(residual_gaps),
        "minimum_combined_lower_envelope": min(combined_gaps),
        "maximum_combined_lower_envelope": max(combined_gaps),
        "maximum_residual_reuse_difference": max(residual_differences),
        "minimum_harmonic_lower_margin": min(lower_margins),
        "systems": systems,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r425-primary/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "run_kind": "primary",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r422_manifest": sha256(R422_MANIFEST), "r424_manifest": sha256(R424_MANIFEST), "r406_manifest": sha256(R406_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-425 PRIMARY PASS {assertion_count}/{assertion_count} systems={len(pairs)} rows={row_count} eligible={eligible_rows} combined={combined_rows} coarse=[{min(coarse_gaps):.6g},{max(coarse_gaps):.6g}] residual=[{min(residual_gaps):.6g},{max(residual_gaps):.6g}] combined=[{min(combined_gaps):.6g},{max(combined_gaps):.6g}]")
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
