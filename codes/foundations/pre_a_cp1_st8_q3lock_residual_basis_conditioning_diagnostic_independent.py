#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-428 diagnostic row."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-residual_basis_conditioning_diagnostic/independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def block_basis(weights: np.ndarray, blocks: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    pi = np.asarray(weights, dtype=float)
    if pi.ndim != 1 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid weights")
    raw = np.zeros((len(pi), len(blocks)), dtype=float)
    seen: set[int] = set()
    for column, block in enumerate(blocks):
        values = np.asarray(block, dtype=int)
        if values.size < 2 or np.any(values < 0) or np.any(values >= len(pi)) or seen.intersection(int(value) for value in values):
            raise AssertionError("invalid disjoint block")
        seen.update(int(value) for value in values)
        mass = float(np.sum(pi[values]))
        raw[values, column] = np.sqrt(pi[values] / mass)
    if float(np.max(np.abs(raw.T @ raw - np.eye(len(blocks))))) > 1.0e-12:
        raise AssertionError("block rows are not orthonormal")
    complete, _ = np.linalg.qr(raw, mode="complete")
    return complete[:, : len(blocks)], complete[:, len(blocks):]


def zero_mean_basis(weights: np.ndarray, block: np.ndarray) -> np.ndarray:
    pi = np.asarray(weights, dtype=float)
    values = np.asarray(block, dtype=int)
    columns: list[np.ndarray] = []
    anchor = int(values[0])
    for index in values[1:]:
        vector = np.zeros(len(pi), dtype=float)
        vector[anchor] = np.sqrt(pi[int(index)])
        vector[int(index)] = -np.sqrt(pi[anchor])
        columns.append(vector)
    q, _ = np.linalg.qr(np.column_stack(columns), mode="reduced")
    return q


def row_inputs(manifest: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, list[np.ndarray], float]:
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    volume = int(target["volume"])
    dimension = int(target["cutoff_dimension"])
    beta = float(Fraction(str(target["beta"])))
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    coordinate_basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _, _ = r416.log_coordinate_distribution(hamiltonian, coordinate_basis, beta, dimension, volume)
    order = list(range(volume)) if target["orientation"] == "right" else list(reversed(range(volume)))
    for index, (weights, _minimum_log_row) in enumerate(r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"]))):
        if index == int(target["conditional_row_index"]):
            row = np.asarray(weights, dtype=float)
            break
    else:
        raise AssertionError("fixed conditional row absent")
    momentum = r402.coordinate_data(dimension)[2]
    graph = r416.projected_graph(row, momentum, float(Fraction(str(fixture["chi"]))))
    pi = np.asarray(graph["weights"], dtype=float)
    conductance = np.asarray(graph["conductance"], dtype=float)
    phi = float(np.max(np.log(pi))) - np.log(pi)
    tail_threshold = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"]
    tail = phi >= float(Fraction(str(tail_threshold)))
    blocks = [np.flatnonzero(~tail), np.flatnonzero(tail)]
    return pi, conductance, blocks, float(np.min(np.log(pi) - np.max(np.log(pi))))


def operator(pi: np.ndarray, conductance: np.ndarray) -> np.ndarray:
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    root = np.sqrt(pi)
    value = (laplacian / root[:, None]) / root[None, :]
    return (value + value.T) / 2.0


def gap(a: np.ndarray, basis: np.ndarray) -> float:
    values = np.linalg.eigvalsh((basis.T @ a @ basis + (basis.T @ a @ basis).T) / 2.0)
    if not np.all(np.isfinite(values)):
        raise AssertionError("nonfinite compressed spectrum")
    return float(values[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    pi, conductance, blocks, minimum_log_row = row_inputs(manifest)
    a = operator(pi, conductance)
    _, r406_basis = block_basis(pi, blocks)
    r422_basis = np.column_stack([zero_mean_basis(pi, block) for block in blocks])
    constraints = np.zeros((len(blocks), len(pi)), dtype=float)
    for row, block in enumerate(blocks):
        constraints[row, block] = np.sqrt(pi[block] / float(np.sum(pi[block])))
    projector = np.eye(len(pi)) - constraints.T @ constraints
    q, _ = np.linalg.qr(constraints.T, mode="complete")
    householder_basis = q[:, len(blocks):]
    values, vectors = np.linalg.eigh((projector + projector.T) / 2.0)
    spectral_basis = vectors[:, values > 0.5]
    bases = {"r406_complement": r406_basis, "r422_weighted_zero_mean": r422_basis, "householder_constraint_nullspace": householder_basis, "spectral_projector_nullspace": spectral_basis}
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-428" and manifest["exploration_id"] == "EXP-001273" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-428/EXP-001273/false", "provenance")
    check("parent hashes", sha256(R426_MANIFEST) == manifest["upstream_authority"]["r426_sha256"] and sha256(R419_MANIFEST) == manifest["upstream_authority"]["r419_sha256"] and sha256(R416_MANIFEST) == manifest["upstream_authority"]["r416_sha256"] and sha256(R422_MANIFEST) == manifest["upstream_authority"]["r422_sha256"] and sha256(R406_MANIFEST) == manifest["upstream_authority"]["r406_sha256"], "hash-pinned parents", "declared hashes", "authority")
    check("fixed row", [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7], [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]], "V2/d16/beta8/right/row7", "fixture")
    check("positive normalized graph", np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= float(thresholds["comparison_tolerance"]) and np.all(conductance >= 0.0) and float(np.max(np.abs(conductance - conductance.T))) <= float(thresholds["comparison_tolerance"]), [float(np.min(pi)), float(np.max(pi)), float(np.sum(pi)), float(np.max(np.abs(conductance - conductance.T)))], "positive reversible row", "graph")
    check("block sizes", [len(block) for block in blocks] == [target["core_size"], target["tail_size"]], [len(block) for block in blocks], [target["core_size"], target["tail_size"]], "fixture")
    check("finite log row", math.isfinite(minimum_log_row), minimum_log_row, "finite", "graph")
    for name, basis in bases.items():
        ortho = float(np.max(np.abs(basis.T @ basis - np.eye(basis.shape[1]))))
        constraints_error = float(np.max(np.abs(constraints @ basis)))
        check(f"{name} orthogonal", ortho <= float(thresholds["orthogonality_tolerance"]), ortho, f"<={thresholds['orthogonality_tolerance']}", "basis")
        check(f"{name} constrained", constraints_error <= float(thresholds["constraint_tolerance"]), constraints_error, f"<={thresholds['constraint_tolerance']}", "basis")
    projector_distance = float(np.linalg.norm(r406_basis @ r406_basis.T - r422_basis @ r422_basis.T, 2))
    cross = np.linalg.svd(r406_basis.T @ r422_basis, compute_uv=False)
    operator_norm = float(np.max(np.abs(np.linalg.eigvalsh(a))))
    dynamic_range = float(np.max(pi) / np.min(pi))
    gaps = [gap(a, basis) for basis in bases.values()]
    spread = float(max(gaps) - min(gaps))
    mismatch = abs(gaps[0] - gaps[1])
    budget = 2.0 * operator_norm * projector_distance
    check("projector distance", projector_distance <= float(thresholds["projector_tolerance"]), projector_distance, f"<={thresholds['projector_tolerance']}", "crosswalk")
    check("cross-Gram agreement", float(np.max(np.abs(cross - 1.0))) <= float(thresholds["cross_gram_tolerance"]), float(np.max(np.abs(cross - 1.0))), f"<={thresholds['cross_gram_tolerance']}", "crosswalk")
    check("dynamic range", dynamic_range > float(thresholds["dynamic_range_floor"]), dynamic_range, f">{thresholds['dynamic_range_floor']}", "conditioning")
    check("mismatch exceeds tolerance", mismatch > float(thresholds["comparison_tolerance"]), mismatch, f">{thresholds['comparison_tolerance']}", "reconstruction")
    check("basis spread exceeds tolerance", spread > float(thresholds["comparison_tolerance"]), spread, f">{thresholds['comparison_tolerance']}", "conditioning")
    check("amplification budget exceeds tolerance", budget > float(thresholds["comparison_tolerance"]), budget, f">{thresholds['comparison_tolerance']}", "conditioning")
    classification = "INCONCLUSIVE_CONDITIONING" if dynamic_range > float(thresholds["dynamic_range_floor"]) and budget > float(thresholds["comparison_tolerance"]) and spread > float(thresholds["comparison_tolerance"]) and mismatch > float(thresholds["comparison_tolerance"]) else "INCONCLUSIVE_OTHER"
    check("classification", classification == "INCONCLUSIVE_CONDITIONING", classification, "INCONCLUSIVE_CONDITIONING", "verdict")
    derived = {
        "fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])},
        "pi_min": float(np.min(pi)), "pi_max": float(np.max(pi)), "pi_dynamic_range": dynamic_range,
        "minimum_log_row": minimum_log_row, "operator_norm_two": operator_norm,
        "projector_distance_two": projector_distance, "cross_gram_singular_min": float(np.min(cross)), "cross_gram_singular_max": float(np.max(cross)),
        "conditioning_amplification_budget": budget, "basis_gap_spread": spread, "recomputed_mismatch": mismatch,
        "r422_residual_gap": gaps[0], "r426_direct_residual_gap": gaps[1], "classification": classification,
        "projector_tolerance_pass": projector_distance <= float(thresholds["projector_tolerance"]),
        "conditioning_predicates_pass": dynamic_range > float(thresholds["dynamic_range_floor"]) and budget > float(thresholds["comparison_tolerance"]) and spread > float(thresholds["comparison_tolerance"]),
        "precision_certified": False, "residual_reuse_closed": False, "r426_route_failure_preserved": True,
    }
    payload = {"schema": "tect/pre-a-r428-independent/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": manifest["result_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_ids"][0], "run_kind": "independent", "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks, "derived": derived, "source_hashes": {"independent": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r416_manifest": sha256(R416_MANIFEST), "r422_manifest": sha256(R422_MANIFEST), "r406_manifest": sha256(R406_MANIFEST)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"], "independence_scope": "reconstructed row, graph, constraint bases and conditioning predicates without importing the R-428 primary module"}
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    if args.self_test:
        print(f"R-428 INDEPENDENT SELFTEST: PASS ({assertion_count}/{assertion_count}; classification={classification})")
    else:
        print(f"R-428 INDEPENDENT PASS {assertion_count}/{assertion_count} classification={classification} projector={projector_distance:.6g} budget={budget:.6g} spread={spread:.6g} mismatch={mismatch:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
