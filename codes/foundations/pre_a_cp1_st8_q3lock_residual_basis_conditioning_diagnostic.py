#!/usr/bin/env python3
"""Diagnose the R-426 high-cutoff residual-basis mismatch.

The fixed failing row is reconstructed from the pinned upstream finite inputs.
Several bases for the same weighted-zero-mean residual subspace are compared.
The output is an inconclusive conditioning diagnostic, never a repair or a
uniform gap claim.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R416_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-preconditioned-schur-cutoff-stress-manifest.json"
R422_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
R406_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-residual_basis_conditioning_diagnostic/primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_residual_core_tail_reserve as r422  # noqa: E402
import pre_a_cp1_st8_q3lock_harmonic_schur_capacity as r406  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def row_inputs() -> tuple[np.ndarray, np.ndarray, list[np.ndarray], np.ndarray, float]:
    local = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = local["diagnostic_contract"]["fixed_failure_row"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    volume = int(target["volume"])
    dimension = int(target["cutoff_dimension"])
    beta = float(Fraction(str(target["beta"])))
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _, _ = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
    order = list(range(volume)) if target["orientation"] == "right" else list(reversed(range(volume)))
    selected: tuple[np.ndarray, float] | None = None
    for index, (weights, minimum_log_row) in enumerate(r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"]))):
        if index == int(target["conditional_row_index"]):
            selected = (np.asarray(weights, dtype=float), float(minimum_log_row))
            break
    if selected is None:
        raise AssertionError("target conditional row not found")
    weights, minimum_log_row = selected
    momentum = r402.coordinate_data(dimension)[2]
    graph = r416.projected_graph(weights, momentum, float(Fraction(str(fixture["chi"]))))
    pi = np.asarray(graph["weights"], dtype=float)
    conductance = np.asarray(graph["conductance"], dtype=float)
    phi = float(np.max(np.log(pi))) - np.log(pi)
    tail = phi >= float(Fraction(str(target.get("tail_threshold", fixture.get("tail_threshold", "4")))))
    # R-426 fixes the threshold at four; the manifest is the source of truth.
    tail = phi >= float(Fraction(str(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"])))
    core = ~tail
    blocks = [np.flatnonzero(core), np.flatnonzero(tail)]
    return pi, conductance, blocks, weights, minimum_log_row


def operator_from_graph(pi: np.ndarray, conductance: np.ndarray) -> np.ndarray:
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    root = np.sqrt(pi)
    operator = (laplacian / root[:, None]) / root[None, :]
    return (operator + operator.T) / 2.0


def normalized_constraints(pi: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    rows = np.zeros((len(blocks), len(pi)), dtype=float)
    for row, block in enumerate(blocks):
        mass = float(np.sum(pi[block]))
        if not math.isfinite(mass) or mass <= 0.0:
            raise AssertionError("invalid block mass")
        rows[row, block] = np.sqrt(pi[block] / mass)
    return rows


def residual_gap(operator: np.ndarray, basis: np.ndarray) -> float:
    compressed = basis.T @ operator @ basis
    values = np.linalg.eigvalsh((compressed + compressed.T) / 2.0)
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise AssertionError("nonfinite residual spectrum")
    return float(values[0])


def max_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(matrix, dtype=float))))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    pi, conductance, blocks, _raw_row, minimum_log_row = row_inputs()
    operator = operator_from_graph(pi, conductance)
    u, r406_basis = r406.block_basis(pi, blocks)
    r422_basis = np.column_stack([r422.zero_mean_basis(pi, block) for block in blocks])
    constraints = normalized_constraints(pi, blocks)
    projector = np.eye(len(pi)) - constraints.T @ constraints
    projector = (projector + projector.T) / 2.0
    householder_full, _ = np.linalg.qr(constraints.T, mode="complete")
    householder_basis = householder_full[:, len(blocks):]
    projector_values, projector_vectors = np.linalg.eigh(projector)
    projector_basis = projector_vectors[:, projector_values > 0.5]
    bases = {"r406_complement": r406_basis, "r422_weighted_zero_mean": r422_basis, "householder_constraint_nullspace": householder_basis, "spectral_projector_nullspace": projector_basis}
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-428" and manifest["exploration_id"] == "EXP-001273" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-428/EXP-001273/false", "provenance")
    check("fixed failure row identity", [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7], [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]], "V2/d16/beta8/right/row7", "fixture")
    check("parent hashes", sha256(R426_MANIFEST) == manifest["upstream_authority"]["r426_sha256"] and sha256(R419_MANIFEST) == manifest["upstream_authority"]["r419_sha256"] and sha256(R416_MANIFEST) == manifest["upstream_authority"]["r416_sha256"] and sha256(R422_MANIFEST) == manifest["upstream_authority"]["r422_sha256"] and sha256(R406_MANIFEST) == manifest["upstream_authority"]["r406_sha256"], "hash-pinned parents", "declared parent SHA-256 values", "authority")
    check("positive row", np.all(np.isfinite(pi)) and np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= float(thresholds["comparison_tolerance"]), [float(np.min(pi)), float(np.max(pi)), float(np.sum(pi))], "positive normalized pi", "graph")
    check("reversible conductance", np.all(np.isfinite(conductance)) and np.all(conductance >= 0.0) and max_abs(conductance - conductance.T) <= float(thresholds["comparison_tolerance"]), max_abs(conductance - conductance.T), "symmetric nonnegative conductance", "graph")
    check("row sizes", [len(block) for block in blocks] == [target["core_size"], target["tail_size"]], [len(block) for block in blocks], [target["core_size"], target["tail_size"]], "fixture")
    check("minimum log row", math.isfinite(minimum_log_row), minimum_log_row, "finite", "graph")
    check("constraint rows orthonormal", max_abs(constraints @ constraints.T - np.eye(len(blocks))) <= float(thresholds["orthogonality_tolerance"]), max_abs(constraints @ constraints.T - np.eye(len(blocks))), f"<={thresholds['orthogonality_tolerance']}", "constraints")

    metrics: dict[str, dict[str, float]] = {}
    for name, basis in bases.items():
        metrics[name] = {
            "columns": float(basis.shape[1]),
            "orthogonality_error": max_abs(basis.T @ basis - np.eye(basis.shape[1])),
            "constraint_residual": max_abs(constraints @ basis),
            "residual_gap": residual_gap(operator, basis),
        }
        check(f"{name} dimension", basis.shape == (len(pi), len(pi) - len(blocks)), basis.shape, (len(pi), len(pi) - len(blocks)), "basis")
        check(f"{name} orthogonality", metrics[name]["orthogonality_error"] <= float(thresholds["orthogonality_tolerance"]), metrics[name]["orthogonality_error"], f"<={thresholds['orthogonality_tolerance']}", "basis")
        check(f"{name} constraints", metrics[name]["constraint_residual"] <= float(thresholds["constraint_tolerance"]), metrics[name]["constraint_residual"], f"<={thresholds['constraint_tolerance']}", "basis")

    projector_r406 = r406_basis @ r406_basis.T
    projector_r422 = r422_basis @ r422_basis.T
    projector_distance = float(np.linalg.norm(projector_r406 - projector_r422, 2))
    cross_singular = np.linalg.svd(r406_basis.T @ r422_basis, compute_uv=False)
    operator_eigenvalues = np.linalg.eigvalsh(operator)
    operator_norm = float(np.max(np.abs(operator_eigenvalues)))
    dynamic_range = float(np.max(pi) / np.min(pi))
    gap_values = [value["residual_gap"] for value in metrics.values()]
    gap_spread = float(max(gap_values) - min(gap_values))
    mismatch = abs(float(metrics["r422_weighted_zero_mean"]["residual_gap"]) - float(metrics["r406_complement"]["residual_gap"]))
    conditioning_budget = 2.0 * operator_norm * projector_distance
    check("cross-basis projector distance", projector_distance <= float(thresholds["projector_tolerance"]), projector_distance, f"<={thresholds['projector_tolerance']}", "crosswalk")
    check("cross-Gram singular values", float(np.max(np.abs(cross_singular - 1.0))) <= float(thresholds["cross_gram_tolerance"]), float(np.max(np.abs(cross_singular - 1.0))), f"<={thresholds['cross_gram_tolerance']}", "crosswalk")
    check("projector nullspace agreement", float(np.linalg.norm(projector_r406 - projector, 2)) <= float(thresholds["projector_tolerance"]), float(np.linalg.norm(projector_r406 - projector, 2)), f"<={thresholds['projector_tolerance']}", "crosswalk")
    check("operator finite", math.isfinite(operator_norm) and operator_norm > 0.0, operator_norm, ">0", "conditioning")
    check("dynamic range exposes stress", dynamic_range > float(thresholds["dynamic_range_floor"]), dynamic_range, f">{thresholds['dynamic_range_floor']}", "conditioning")
    check("fixed mismatch reproduced", abs(float(metrics["r406_complement"]["residual_gap"]) - float(target["r422_residual_gap"])) <= float(thresholds["reconstruction_tolerance"]), metrics["r406_complement"]["residual_gap"], target["r422_residual_gap"], "reconstruction")
    check("R-426 direct gap reproduced", abs(float(metrics["r422_weighted_zero_mean"]["residual_gap"]) - float(target["r426_direct_residual_gap"])) <= float(thresholds["reconstruction_tolerance"]), metrics["r422_weighted_zero_mean"]["residual_gap"], target["r426_direct_residual_gap"], "reconstruction")
    check("fixed mismatch exceeds tolerance", mismatch > float(thresholds["comparison_tolerance"]), mismatch, f">{thresholds['comparison_tolerance']}", "reconstruction")
    check("basis spread exceeds tolerance", gap_spread > float(thresholds["comparison_tolerance"]), gap_spread, f">{thresholds['comparison_tolerance']}", "conditioning")
    check("conditioning budget exceeds tolerance", conditioning_budget > float(thresholds["comparison_tolerance"]), conditioning_budget, f">{thresholds['comparison_tolerance']}", "conditioning")
    classification = "INCONCLUSIVE_CONDITIONING" if dynamic_range > float(thresholds["dynamic_range_floor"]) and conditioning_budget > float(thresholds["comparison_tolerance"]) and gap_spread > float(thresholds["comparison_tolerance"]) and mismatch > float(thresholds["comparison_tolerance"]) else "INCONCLUSIVE_OTHER"
    check("diagnostic classification", classification == "INCONCLUSIVE_CONDITIONING", classification, "INCONCLUSIVE_CONDITIONING", "verdict")

    derived = {
        "fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])},
        "pi_min": float(np.min(pi)),
        "pi_max": float(np.max(pi)),
        "pi_dynamic_range": dynamic_range,
        "minimum_log_row": minimum_log_row,
        "operator_norm_two": operator_norm,
        "projector_distance_two": projector_distance,
        "projector_r406_constraint_distance_two": float(np.linalg.norm(projector_r406 - projector, 2)),
        "cross_gram_singular_min": float(np.min(cross_singular)),
        "cross_gram_singular_max": float(np.max(cross_singular)),
        "conditioning_amplification_budget": conditioning_budget,
        "r422_residual_gap": float(metrics["r406_complement"]["residual_gap"]),
        "r426_direct_residual_gap": float(metrics["r422_weighted_zero_mean"]["residual_gap"]),
        "recomputed_mismatch": mismatch,
        "basis_gap_spread": gap_spread,
        "basis_metrics": metrics,
        "classification": classification,
        "precision_certified": False,
        "residual_reuse_closed": False,
        "r426_route_failure_preserved": True,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r428-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": classification,
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r416_manifest": sha256(R416_MANIFEST), "r422_manifest": sha256(R422_MANIFEST), "r406_manifest": sha256(R406_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-428 PRIMARY {classification} {assertion_count}/{assertion_count} row=V2/d16/beta8/right/7 projector={projector_distance:.6g} A_norm={operator_norm:.6g} budget={conditioning_budget:.6g} spread={gap_spread:.6g} mismatch={mismatch:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "INCONCLUSIVE_CONDITIONING"
        assert payload["derived"]["r426_route_failure_preserved"] is True
        print("R-428 PRIMARY SELFTEST: PASS (fixed row crosswalk and conditioning diagnostic)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
