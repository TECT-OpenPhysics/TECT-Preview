#!/usr/bin/env python3
"""Finite two-block coarse Schur assembly after the R-422 residual split.

The block-constant span is retained rather than discarded.  R-406's harmonic
extension computes the coarse Schur gap and the residual gap on the same
core/tail partition; their conservative half-minimum is recorded as a finite
combined lower envelope.  No limit or physical interpretation is inferred.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-manifest.json"
R422_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
SLUG = "coarse_schur_assembly"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def residual_gap(weights: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> float:
    """Independent direct residual projection for the R-422 comparison."""
    pi = np.asarray(weights, dtype=float)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(pi)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    core_basis = r422.zero_mean_basis(pi, np.flatnonzero(core))
    tail_basis = r422.zero_mean_basis(pi, np.flatnonzero(tail))
    block = np.column_stack((core_basis, tail_basis))
    values = np.linalg.eigvalsh((block.T @ operator @ block + (block.T @ operator @ block).T) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)) or float(values[0]) <= 0.0:
        raise AssertionError("direct residual projection is not positive")
    return float(values[0])


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(R422_MANIFEST.read_text(encoding="utf-8"))
    r419_manifest = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    parent_fixture = r419_manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    comparison_tolerance = float(fixture["comparison_tolerance"])
    probability_floor = float(fixture["probability_floor"])
    gap_floor = float(fixture["gap_floor"])
    chi = float(Fraction(str(parent_fixture["chi"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    alpha = float(Fraction(str(fixture["alpha"])))
    theta = float(Fraction(str(fixture["tail_threshold"])))
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

    finite_flags = ["finite_harmonic_coarse_schur_closed", "finite_residual_reuse_closed", "finite_combined_lower_envelope_closed", "finite_coarse_rows_recorded"]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-424" and manifest["exploration_id"] == "EXP-001269" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-424/EXP-001269/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("R-422 identity", parent["result_id"] == "R-422" and parent["exploration_id"] == "EXP-001267", [parent["result_id"], parent["exploration_id"]], "R-422/EXP-001267", "authority")
    check("fixture grid", pairs == [(2, 3), (2, 6), (2, 12), (3, 3), (3, 4), (4, 4)], pairs, "declared Q3 systems", "fixture")
    check("beta/orientation", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed R-422 grid", "fixture")
    check("positive parameters", alpha > 0.0 and theta > 0.0 and chi > 0.0 and gap_floor > 0.0, [alpha, theta, chi, gap_floor], ">0", "fixture")

    row_count = 0
    tail_rows = 0
    eligible_rows = 0
    combined_rows = 0
    coarse_gaps: list[float] = []
    residual_gaps: list[float] = []
    combined_gaps: list[float] = []
    residual_differences: list[float] = []
    lower_margins: list[float] = []
    systems: list[dict[str, Any]] = []

    for volume, dimension in pairs:
        _q_ops, hamiltonian, _terms = r422.r419.r399.split_system(volume, dimension, parent_fixture)
        basis = r422.r419.r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r422.r419.r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        system_rows = 0
        system_tail_rows = 0
        system_eligible = 0
        system_combined = 0
        system_min_coarse = float("inf")
        system_min_residual = float("inf")
        system_min_combined = float("inf")
        for beta in betas:
            log_reference, _direct, _shifted = r422.r419.r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} normalized", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= comparison_tolerance, float(np.sum(np.exp(log_reference))), 1.0, "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                for weights, minimum_log_row in r422.r419.r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    row_count += 1
                    system_rows += 1
                    check(f"V={volume} d={dimension} {orientation} row positivity", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "rows")
                    graph = r422.r419.r416.projected_graph(weights, momentum, chi)
                    pi = np.asarray(graph["weights"], dtype=float)
                    conductance = np.asarray(graph["conductance"], dtype=float)
                    phi = float(np.max(np.log(pi))) - np.log(pi)
                    tail = phi >= theta
                    core = ~tail
                    if bool(np.any(tail)):
                        tail_rows += 1
                        system_tail_rows += 1
                    if int(np.sum(tail)) < 2 or int(np.sum(core)) < 2:
                        continue
                    eligible_rows += 1
                    system_eligible += 1
                    blocks = [np.flatnonzero(core), np.flatnonzero(tail)]
                    data = r406.harmonic_split(pi, conductance, blocks)
                    direct_residual = residual_gap(pi, conductance, core, tail)
                    coarse = float(data["coarse_gap"])
                    residual = float(data["residual_gap"])
                    combined = float(data["decomposition_gap"])
                    check(f"V={volume} d={dimension} {orientation} coarse Schur", coarse > gap_floor and math.isfinite(coarse), coarse, f">{gap_floor}", "coarse Schur")
                    check(f"V={volume} d={dimension} {orientation} residual positivity", residual > gap_floor and math.isfinite(residual), residual, f">{gap_floor}", "residual")
                    check(f"V={volume} d={dimension} {orientation} residual reuse", abs(residual - direct_residual) <= comparison_tolerance, [residual, direct_residual], f"|difference|<={comparison_tolerance}", "R-422 reuse")
                    check(f"V={volume} d={dimension} {orientation} combined envelope", combined > gap_floor and combined <= 0.5 * min(coarse, residual) + comparison_tolerance, [combined, coarse, residual], f"positive and <= half minimum+{comparison_tolerance}", "combined")
                    check(f"V={volume} d={dimension} {orientation} harmonic energy split", float(data["max_energy_residual"]) <= tolerance and float(data["max_variance_envelope_deficit"]) <= tolerance and float(data["minimum_lower_bound_margin"]) >= -tolerance, [data["max_energy_residual"], data["max_variance_envelope_deficit"], data["minimum_lower_bound_margin"]], f"split residuals <= {tolerance}", "harmonic split")
                    coarse_gaps.append(coarse)
                    residual_gaps.append(residual)
                    combined_gaps.append(combined)
                    residual_differences.append(abs(residual - direct_residual))
                    lower_margins.append(float(data["minimum_lower_bound_margin"]))
                    system_min_coarse = min(system_min_coarse, coarse)
                    system_min_residual = min(system_min_residual, residual)
                    system_min_combined = min(system_min_combined, combined)
                    combined_rows += 1
                    system_combined += 1
        check(f"V={volume} d={dimension} coverage", system_rows > 0 and system_eligible == system_combined, [system_rows, system_tail_rows, system_eligible, system_combined], "eligible rows assembled", "coverage")
        systems.append({"volume": volume, "dimension": dimension, "row_count": system_rows, "tail_row_count": system_tail_rows, "eligible_row_count": system_eligible, "combined_row_count": system_combined, "minimum_coarse_schur_gap": system_min_coarse if system_eligible else None, "minimum_residual_gap": system_min_residual if system_eligible else None, "minimum_combined_gap": system_min_combined if system_eligible else None})

    check("row coverage", row_count > 0 and tail_rows > 0, [row_count, tail_rows], "finite rows with tail", "coverage")
    check("eligible coverage", eligible_rows > 0 and combined_rows == eligible_rows, [eligible_rows, combined_rows], "all eligible rows assembled", "coverage")
    check("coarse aggregate", min(coarse_gaps, default=0.0) > gap_floor, min(coarse_gaps, default=0.0), f">{gap_floor}", "aggregate")
    check("residual aggregate", min(residual_gaps, default=0.0) > gap_floor, min(residual_gaps, default=0.0), f">{gap_floor}", "aggregate")
    check("combined aggregate", min(combined_gaps, default=0.0) > gap_floor, min(combined_gaps, default=0.0), f">{gap_floor}", "aggregate")
    check("residual comparison aggregate", max(residual_differences, default=0.0) <= comparison_tolerance, max(residual_differences, default=0.0), f"<={comparison_tolerance}", "R-422 reuse")
    check("lower-margin aggregate", min(lower_margins, default=-math.inf) >= -tolerance, min(lower_margins, default=-math.inf), f">=-{tolerance}", "harmonic split")

    derived = {
        "system_count": len(pairs),
        "conditional_row_count": row_count,
        "tail_row_count": tail_rows,
        "eligible_row_count": eligible_rows,
        "combined_row_count": combined_rows,
        "minimum_coarse_schur_gap": min(coarse_gaps, default=0.0),
        "maximum_coarse_schur_gap": max(coarse_gaps, default=0.0),
        "minimum_residual_gap": min(residual_gaps, default=0.0),
        "maximum_residual_gap": max(residual_gaps, default=0.0),
        "minimum_combined_lower_envelope": min(combined_gaps, default=0.0),
        "maximum_combined_lower_envelope": max(combined_gaps, default=0.0),
        "maximum_residual_reuse_difference": max(residual_differences, default=0.0),
        "minimum_harmonic_lower_margin": min(lower_margins, default=0.0),
        "systems": systems,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r424-primary/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "primary",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r422_manifest": sha256(R422_MANIFEST), "r419_manifest": sha256(R419_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-424 PRIMARY PASS {assertion_count}/{assertion_count} rows={row_count} eligible={eligible_rows} combined={combined_rows} coarse=[{min(coarse_gaps):.6g},{max(coarse_gaps):.6g}] residual=[{min(residual_gaps):.6g},{max(residual_gaps):.6g}] combined=[{min(combined_gaps):.6g},{max(combined_gaps):.6g}]")
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
