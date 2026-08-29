#!/usr/bin/env python3
"""Primary finite audit of the R-422 residual core/tail reserve.

The audit reuses the R-419 conditional Q3 rows and the R-421 Lyapunov tail
definition.  On the residual complement of the two block-mean modes it keeps
the core/tail cross block instead of discarding it.  The certified reserve is
the conservative bound min(a, kappa) - eta; the sharper two-by-two eigenvalue
is recorded only as a diagnostic.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
R421_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-tail-hardy-ground-state-transform-manifest.json"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
SLUG = "residual_core_tail_reserve"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def zero_mean_basis(pi: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """Orthonormal basis for vectors supported on indices with pi-mean zero."""
    weights = np.asarray(pi, dtype=float)
    selected = np.asarray(indices, dtype=int)
    basis = np.zeros((weights.size, max(0, selected.size - 1)), dtype=float)
    if selected.size <= 1:
        return basis
    square_root = np.sqrt(weights[selected])
    for column in range(selected.size - 1):
        basis[selected[column], column] = square_root[column + 1]
        basis[selected[column + 1], column] = -square_root[column]
    orthonormal, _ = np.linalg.qr(basis, mode="reduced")
    return orthonormal


def safe_reserve(core_gap: float, tail_floor: float, cross_norm: float) -> float:
    """Conservative reserve from 2|xy| <= x^2+y^2."""
    values = (float(core_gap), float(tail_floor), float(cross_norm))
    if not all(math.isfinite(value) for value in values):
        raise AssertionError("nonfinite reserve input")
    if values[0] < 0.0 or values[1] < 0.0 or values[2] < 0.0:
        raise AssertionError("reserve inputs must be nonnegative")
    return min(values[0], values[1]) - values[2]


def sharp_diagnostic(core_gap: float, tail_floor: float, cross_norm: float) -> float:
    """Return the sharper 2x2 eigenvalue, never used as the certified floor."""
    discriminant = (core_gap - tail_floor) ** 2 + 4.0 * cross_norm**2
    if discriminant < 0.0 or not math.isfinite(discriminant):
        raise AssertionError("invalid two-by-two discriminant")
    return 0.5 * (core_gap + tail_floor - math.sqrt(discriminant))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r421_manifest = json.loads(R421_MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    fixture = parent["finite_fixture"]
    local = manifest["finite_fixture"]
    tolerance = float(local["numerical_tolerance"])
    crosscheck_tolerance = float(local["crosscheck_tolerance"])
    reserve_tolerance = float(local["reserve_tolerance"])
    probability_floor = float(local["probability_floor"])
    rate_floor = float(local["rate_floor"])
    spectral_floor = float(local["spectral_floor"])
    alpha = float(Fraction(str(local["alpha"])))
    theta = float(Fraction(str(local["tail_threshold"])))
    chi = float(Fraction(str(fixture["chi"])))
    betas = [float(Fraction(value)) for value in local["beta_values"]]
    orientations = list(local["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in local["q3_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 650:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = [
        "finite_block_mean_zero_split_closed",
        "finite_tail_hardy_reuse_closed",
        "finite_cross_block_norm_closed",
        "finite_two_by_two_reserve_closed",
        "finite_positive_reserve_rows_recorded",
        "finite_negative_reserve_rows_recorded",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-422" and manifest["exploration_id"] == "EXP-001267" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-422/EXP-001267/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    check("R-421 manifest hash", sha256(R421_MANIFEST) == manifest["upstream_authority"]["r421_sha256"], sha256(R421_MANIFEST), manifest["upstream_authority"]["r421_sha256"], "authority")
    check("R-421 manifest identity", r421_manifest["result_id"] == "R-421" and r421_manifest["exploration_id"] == "EXP-001266", [r421_manifest["result_id"], r421_manifest["exploration_id"]], "R-421/EXP-001266", "authority")
    check("fixture grid", pairs == [(2, 3), (2, 6), (2, 12), (3, 3), (3, 4), (4, 4)], pairs, "declared Q3 systems", "fixture")
    check("beta/orientation", betas == [0.5, 2.0, 8.0] and orientations == ["right", "left"], [betas, orientations], "fixed R-419 grid", "fixture")
    check("positive parameters", alpha > 0.0 and theta > 0.0 and chi > 0.0 and rate_floor > 0.0 and spectral_floor > 0.0, [alpha, theta, chi, rate_floor, spectral_floor], ">0", "fixture")

    row_count = 0
    tail_row_count = 0
    eligible_rows = 0
    positive_rows = 0
    nonpositive_rows = 0
    residual_gaps: list[float] = []
    core_gaps: list[float] = []
    direct_tail_gaps: list[float] = []
    tail_floors: list[float] = []
    cross_norms: list[float] = []
    safe_reserves: list[float] = []
    sharp_reserves: list[float] = []
    bound_margins: list[float] = []
    systems: list[dict[str, Any]] = []

    for volume, dimension in pairs:
        _q_ops, hamiltonian, _terms = r419.r399.split_system(volume, dimension, fixture)
        basis = r419.r399.coordinate_basis(dimension, volume)
        _levels, _single_basis, momentum = r402.coordinate_data(dimension)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        system_rows = 0
        system_tail_rows = 0
        system_eligible = 0
        system_positive = 0
        system_nonpositive = 0
        system_min_safe = float("inf")
        system_min_sharp = float("inf")
        for beta in betas:
            log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, beta, dimension, volume)
            check(f"V={volume} d={dimension} beta={beta} normalized", np.all(np.isfinite(log_reference)) and abs(float(np.sum(np.exp(log_reference))) - 1.0) <= crosscheck_tolerance, float(np.sum(np.exp(log_reference))), 1.0, "log-domain")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                for weights, minimum_log_row in r416.conditional_rows(log_reference, order, dimension, probability_floor):
                    row_count += 1
                    system_rows += 1
                    check(f"V={volume} d={dimension} {orientation} row positivity", math.isfinite(minimum_log_row) and np.all(np.isfinite(weights)) and float(np.min(weights)) > 0.0, minimum_log_row, "finite positive conditional row", "rows")
                    graph = r416.projected_graph(weights, momentum, chi)
                    pi = np.asarray(graph["weights"], dtype=float)
                    conductance = np.asarray(graph["conductance"], dtype=float)
                    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
                    inverse = 1.0 / np.sqrt(pi)
                    operator = inverse[:, None] * laplacian * inverse[None, :]
                    operator = (operator + operator.T) / 2.0
                    check(f"V={volume} d={dimension} {orientation} operator", np.all(np.isfinite(operator)) and np.max(np.abs(operator - operator.T)) <= tolerance, float(np.max(np.abs(operator - operator.T))), f"<={tolerance}", "operator")
                    phi = float(np.max(np.log(pi))) - np.log(pi)
                    potential = np.exp(alpha * phi)
                    rates = -(conductance @ potential - np.sum(conductance, axis=1) * potential) / pi / potential
                    tail = phi >= theta
                    core = ~tail
                    if bool(np.any(tail)):
                        tail_row_count += 1
                        system_tail_rows += 1
                        check(f"V={volume} d={dimension} {orientation} tail rate", float(np.min(rates[tail])) > rate_floor, float(np.min(rates[tail])), f">{rate_floor}", "tail Hardy")
                    if int(np.sum(tail)) < 2 or int(np.sum(core)) < 2:
                        continue
                    eligible_rows += 1
                    system_eligible += 1
                    core_basis = zero_mean_basis(pi, np.where(core)[0])
                    tail_basis = zero_mean_basis(pi, np.where(tail)[0])
                    check(f"V={volume} d={dimension} {orientation} core basis", core_basis.shape[1] == int(np.sum(core)) - 1 and np.max(np.abs(core_basis.T @ core_basis - np.eye(core_basis.shape[1]))) <= crosscheck_tolerance, core_basis.shape, "orthonormal core block-mean-zero basis", "split")
                    check(f"V={volume} d={dimension} {orientation} tail basis", tail_basis.shape[1] == int(np.sum(tail)) - 1 and np.max(np.abs(tail_basis.T @ tail_basis - np.eye(tail_basis.shape[1]))) <= crosscheck_tolerance, tail_basis.shape, "orthonormal tail block-mean-zero basis", "split")
                    core_mean_vector = np.sqrt(pi) * core.astype(float)
                    tail_mean_vector = np.sqrt(pi) * tail.astype(float)
                    check(f"V={volume} d={dimension} {orientation} core mean", np.linalg.norm(core_basis.T @ core_mean_vector) <= crosscheck_tolerance, float(np.linalg.norm(core_basis.T @ core_mean_vector)), f"<={crosscheck_tolerance}", "split")
                    check(f"V={volume} d={dimension} {orientation} tail mean", np.linalg.norm(tail_basis.T @ tail_mean_vector) <= crosscheck_tolerance, float(np.linalg.norm(tail_basis.T @ tail_mean_vector)), f"<={crosscheck_tolerance}", "split")
                    core_matrix = (core_basis.T @ operator @ core_basis)
                    tail_matrix = (tail_basis.T @ operator @ tail_basis)
                    cross_matrix = core_basis.T @ operator @ tail_basis
                    core_matrix = (core_matrix + core_matrix.T) / 2.0
                    tail_matrix = (tail_matrix + tail_matrix.T) / 2.0
                    core_values = np.linalg.eigvalsh(core_matrix)
                    tail_values = np.linalg.eigvalsh(tail_matrix)
                    core_gap = float(core_values[0])
                    direct_tail_gap = float(tail_values[0])
                    cross_norm = float(np.linalg.svd(cross_matrix, compute_uv=False)[0]) if cross_matrix.size else 0.0
                    kappa = float(np.min(rates[tail]))
                    safe = safe_reserve(core_gap, kappa, cross_norm)
                    sharp = sharp_diagnostic(core_gap, kappa, cross_norm)
                    residual_matrix = np.block([[core_matrix, cross_matrix], [cross_matrix.T, tail_matrix]])
                    residual_matrix = (residual_matrix + residual_matrix.T) / 2.0
                    actual_residual_gap = float(np.linalg.eigvalsh(residual_matrix)[0])
                    check(f"V={volume} d={dimension} {orientation} core gap", core_gap > spectral_floor and np.all(np.isfinite(core_values)), core_gap, f">{spectral_floor}", "core form")
                    check(f"V={volume} d={dimension} {orientation} tail Hardy reuse", direct_tail_gap + reserve_tolerance >= kappa and direct_tail_gap > spectral_floor, [direct_tail_gap, kappa], f"direct tail gap >= kappa-{reserve_tolerance}", "tail Hardy")
                    check(f"V={volume} d={dimension} {orientation} cross norm", cross_norm >= 0.0 and math.isfinite(cross_norm), cross_norm, ">=0 finite", "cross block")
                    check(f"V={volume} d={dimension} {orientation} reserve bound", actual_residual_gap + reserve_tolerance >= safe, [actual_residual_gap, safe], f"actual gap >= safe-{reserve_tolerance}", "two-block reserve")
                    check(f"V={volume} d={dimension} {orientation} sharp ordering", sharp + reserve_tolerance >= safe, [sharp, safe], f"sharp >= safe-{reserve_tolerance}", "two-block reserve")
                    # Deterministic normalized probes exercise the cross term and
                    # the exact conservative inequality independently of eigensolver ordering.
                    for probe_index in range(4):
                        x = np.sin((np.arange(core_basis.shape[1], dtype=float) + 1.0) * (probe_index + 1.0))
                        y = np.cos((np.arange(tail_basis.shape[1], dtype=float) + 1.0) * (probe_index + 0.5))
                        x /= max(float(np.linalg.norm(x)), 1.0)
                        y /= max(float(np.linalg.norm(y)), 1.0)
                        vector = np.concatenate((x, y))
                        form_value = float(vector @ (residual_matrix @ vector))
                        margin = form_value - safe * float(vector @ vector)
                        bound_margins.append(margin)
                        check(f"V={volume} d={dimension} {orientation} probe={probe_index} reserve", margin + reserve_tolerance >= 0.0, margin, f">=-{reserve_tolerance}", "two-block reserve")
                    residual_gaps.append(actual_residual_gap)
                    core_gaps.append(core_gap)
                    direct_tail_gaps.append(direct_tail_gap)
                    tail_floors.append(kappa)
                    cross_norms.append(cross_norm)
                    safe_reserves.append(safe)
                    sharp_reserves.append(sharp)
                    system_min_safe = min(system_min_safe, safe)
                    system_min_sharp = min(system_min_sharp, sharp)
                    if safe > reserve_tolerance:
                        positive_rows += 1
                        system_positive += 1
                    else:
                        nonpositive_rows += 1
                        system_nonpositive += 1
        check(f"V={volume} d={dimension} coverage", system_rows > 0 and system_tail_rows >= 0 and system_eligible == system_positive + system_nonpositive, [system_rows, system_tail_rows, system_eligible, system_positive, system_nonpositive], "eligible rows partitioned", "coverage")
        systems.append({"volume": volume, "dimension": dimension, "row_count": system_rows, "tail_row_count": system_tail_rows, "eligible_row_count": system_eligible, "positive_reserve_rows": system_positive, "nonpositive_reserve_rows": system_nonpositive, "minimum_safe_reserve": system_min_safe if system_eligible else None, "minimum_sharp_diagnostic": system_min_sharp if system_eligible else None})

    check("row coverage", row_count > 0 and tail_row_count > 0, [row_count, tail_row_count], "positive finite row and tail coverage", "coverage")
    check("eligible coverage", eligible_rows == positive_rows + nonpositive_rows and eligible_rows > 0, [eligible_rows, positive_rows, nonpositive_rows], "eligible rows partitioned and nonempty", "coverage")
    check("reserve aggregate", all(math.isfinite(value) for value in safe_reserves + sharp_reserves + residual_gaps), [min(safe_reserves), max(safe_reserves), min(sharp_reserves), max(sharp_reserves)], "finite reserves", "aggregate")
    check("conservative reserve probes", min(bound_margins, default=-math.inf) + reserve_tolerance >= 0.0, min(bound_margins, default=-math.inf), f">=-{reserve_tolerance}", "aggregate")
    check("positive and failure rows recorded", positive_rows > 0 and nonpositive_rows > 0, [positive_rows, nonpositive_rows], "both finite outcomes retained", "boundary")

    derived = {
        "system_count": len(pairs),
        "conditional_row_count": row_count,
        "tail_row_count": tail_row_count,
        "eligible_row_count": eligible_rows,
        "positive_reserve_row_count": positive_rows,
        "nonpositive_reserve_row_count": nonpositive_rows,
        "minimum_core_gap": min(core_gaps, default=0.0),
        "minimum_direct_tail_gap": min(direct_tail_gaps, default=0.0),
        "minimum_tail_hardy_floor": min(tail_floors, default=0.0),
        "maximum_cross_norm": max(cross_norms, default=0.0),
        "minimum_safe_reserve": min(safe_reserves, default=0.0),
        "maximum_safe_reserve": max(safe_reserves, default=0.0),
        "minimum_sharp_diagnostic": min(sharp_reserves, default=0.0),
        "maximum_sharp_diagnostic": max(sharp_reserves, default=0.0),
        "minimum_actual_residual_gap": min(residual_gaps, default=0.0),
        "minimum_probe_margin": min(bound_margins, default=0.0),
        "systems": systems,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r422-primary/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "primary",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r421_manifest": sha256(R421_MANIFEST), "r419_manifest": sha256(PARENT)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-422 PRIMARY PASS {assertion_count}/{assertion_count} assertions; rows={row_count} eligible={eligible_rows} positive={positive_rows} nonpositive={nonpositive_rows}; safe_reserve=[{min(safe_reserves, default=0.0):.6g},{max(safe_reserves, default=0.0):.6g}] max_cross={max(cross_norms, default=0.0):.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)


if __name__ == "__main__":
    main()
