#!/usr/bin/env python3
"""Audit the finite conditional-row ordinal used by R-426 and R-430.

The audit is deliberately claim-nonbearing.  It fixes the emission contract
before any interpretation of the residual-reuse mismatch and records the
historical subtract-one lane as a different finite row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-row-ordinal-audit-manifest.json"
R430_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
R430_INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_source_point_precision_audit_independent.py"
R430_INDEPENDENT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-source_point_precision_audit/independent.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R429_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-fixed_row_ordinal_audit/primary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
import pre_a_cp1_st8_q3lock_high_cutoff_schur_stress as r426  # noqa: E402


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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_logsumexp(values: np.ndarray) -> float:
    array = np.asarray(values, dtype=float)
    maximum = float(np.max(array))
    return maximum + float(np.log(np.sum(np.exp(array - maximum))))


def emission_rows(log_reference: np.ndarray, dimension: int) -> list[np.ndarray]:
    """Reproduce the two-site right-oriented emission order explicitly."""
    if log_reference.shape != (dimension, dimension):
        raise AssertionError(f"unexpected log-reference shape: {log_reference.shape}")
    rows: list[np.ndarray] = []
    # radius 0: one unconditional row
    marginal0 = np.array(
        [stable_logsumexp(log_reference[index, :]) for index in range(dimension)],
        dtype=float,
    )
    unconditional = np.exp(marginal0 - stable_logsumexp(marginal0))
    unconditional /= float(np.sum(unconditional))
    rows.append(unconditional)
    # radius 1: one row for each parent coordinate, in parent order.
    for parent in range(dimension):
        log_row = log_reference[parent, :] - marginal0[parent]
        maximum = float(np.max(log_row))
        row = np.exp(log_row - maximum)
        row /= float(np.sum(row))
        rows.append(row)
    return rows


def direct_gap(row: np.ndarray, momentum: np.ndarray, chi: float, threshold: float) -> tuple[float, list[np.ndarray], np.ndarray]:
    weights = np.asarray(row, dtype=float)
    weights /= float(np.sum(weights))
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(momentum)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    phi = float(np.max(np.log(weights))) - np.log(weights)
    tail = phi >= threshold
    core = ~tail
    if int(np.sum(core)) < 2 or int(np.sum(tail)) < 2:
        raise AssertionError("target row is not eligible for the declared core/tail split")
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(weights)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    basis = np.column_stack([r426.r422.zero_mean_basis(weights, block) for block in (np.flatnonzero(core), np.flatnonzero(tail))])
    compressed = (basis.T @ operator @ basis)
    compressed = (compressed + compressed.T) / 2.0
    return float(np.linalg.eigvalsh(compressed)[0]), [np.flatnonzero(core), np.flatnonzero(tail)], conductance


def reconstruct() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["row_contract"]
    source_fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    r426_manifest = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))
    failure = r426_manifest["failure_contract"]
    volume, dimension = 2, 16
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, source_fixture)
    basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, 8.0, dimension, volume)
    rows = emission_rows(log_reference, dimension)
    generator_rows = list(r416.conditional_rows(log_reference, [0, 1], dimension, float(source_fixture["probability_floor"])))
    if len(rows) != len(generator_rows):
        raise AssertionError("explicit emission order disagrees with canonical generator length")
    explicit_error = max(float(np.max(np.abs(left - right[0]))) for left, right in zip(rows, generator_rows))
    target_ordinal = int(target["target_emission_ordinal"])
    wrong_ordinal = int(target["historical_subtract_one_ordinal"])
    selected = rows[target_ordinal]
    wrong = rows[wrong_ordinal]
    momentum = r402.coordinate_data(dimension)[2]
    threshold = float(r426_manifest["finite_fixture"]["tail_threshold"])
    gap, blocks, conductance = direct_gap(selected, momentum, float(source_fixture["chi"]), threshold)
    wrong_gap, wrong_blocks, _wrong_conductance = direct_gap(wrong, momentum, float(source_fixture["chi"]), threshold)
    return {
        "rows": rows,
        "wrong_row": wrong,
        "generator_rows": generator_rows,
        "explicit_error": explicit_error,
        "selected": selected,
        "wrong_ordinal": wrong_ordinal,
        "gap": gap,
        "wrong_gap": wrong_gap,
        "blocks": blocks,
        "wrong_blocks": wrong_blocks,
        "conductance": conductance,
        "failure": failure,
        "momentum": momentum,
        "source_fixture": source_fixture,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["row_contract"]
    failure = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["failure_contract"]
    data = reconstruct()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-432" and manifest["exploration_id"] == "EXP-001277" and manifest["claim_bearing"] is False and manifest["status"] == "ROW_INDEX_CONTRACT_CORRECTED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-432/EXP-001277/false", "provenance")
    check("authority hashes", sha256(R430_MANIFEST) == manifest["upstream_authority"]["r430_manifest_sha256"] and sha256(R430_INDEPENDENT) == manifest["upstream_authority"]["r430_independent_script_sha256"] and sha256(R426_MANIFEST) == manifest["upstream_authority"]["r426_manifest_sha256"] and sha256(R429_MANIFEST) == manifest["upstream_authority"]["r429_manifest_sha256"], "hash-pinned R430/R426/R429 sources", "declared SHA-256 values", "authority")
    check("emission order", len(data["rows"]) == 17 and data["explicit_error"] <= 1e-12, [len(data["rows"]), data["explicit_error"]], "17 rows and explicit/generator agreement", "row contract")
    check("target mapping", contract["target_emission_ordinal"] == 7 and contract["target_parent_coordinate"] == 6 and data["selected"].shape == (16,), [contract["target_emission_ordinal"], contract["target_parent_coordinate"], data["selected"].shape], "ordinal 7 -> parent 6", "row contract")
    check("target positivity", np.all(np.isfinite(data["selected"])) and np.all(data["selected"] > 0.0) and abs(float(np.sum(data["selected"])) - 1.0) <= 1e-12, [float(np.min(data["selected"])), float(np.max(data["selected"])), float(np.sum(data["selected"]))], "positive normalized row", "source")
    check("target blocks", [len(block) for block in data["blocks"]] == [int(failure["core_size"]), int(failure["tail_size"])], [len(block) for block in data["blocks"]], [failure["core_size"], failure["tail_size"]], "tail split")
    check("corrected direct gap finite", np.isfinite(data["gap"]) and data["gap"] > 0.0, data["gap"], ">0", "residual")
    check("R-426 direct reference reproduced", abs(data["gap"] - float(failure["direct_residual_gap"])) <= 1e-12, [data["gap"], failure["direct_residual_gap"]], "same finite direct residual gap", "residual")
    mismatch = abs(data["gap"] - float(failure["r422_residual_gap"]))
    check("R-422 mismatch preserved", mismatch > float(contract["comparison_tolerance"]), mismatch, f">{contract['comparison_tolerance']}", "R-422 reuse")
    check("historical wrong row distinct", int(contract["historical_subtract_one_ordinal"]) == 6 and not np.allclose(data["selected"], data["wrong_row"], rtol=0.0, atol=1e-14) and abs(data["wrong_gap"] - data["gap"]) > float(contract["comparison_tolerance"]), [contract["historical_subtract_one_ordinal"], data["wrong_gap"], data["gap"]], "subtract-one selects a different row", "row correction")
    r430_independent = json.loads(R430_INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    check("R-430 independent value identified", abs(float(r430_independent["derived"]["source_residual_gap_double"]) - data["wrong_gap"]) <= float(contract["comparison_tolerance"]), [r430_independent["derived"]["source_residual_gap_double"], data["wrong_gap"]], f"same ordinal-6 row within {contract['comparison_tolerance']}", "row correction")
    check("R-430 sensitivity interpretation rejected", r430_independent["derived"]["source_interval_certified"] is False and r430_independent["derived"]["residual_reuse_closed"] is False and int(contract["target_emission_ordinal"]) != int(contract["historical_subtract_one_ordinal"]), [r430_independent["derived"]["source_interval_certified"], r430_independent["derived"]["residual_reuse_closed"]], "wrong-row control is not target evidence", "scope")
    scope = manifest["scope"]
    check("scope firewall", scope["row_ordinal_contract_corrected"] is True and scope["corrected_target_reconstructed"] is True and scope["historical_subtract_one_identified"] is True and scope["r426_direct_gap_reproduced"] is True and scope["r430_independent_sensitivity_rejected_for_target"] is True and scope["original_source_interval_certified"] is False and scope["residual_reuse_closed"] is False and scope["no_tier_change"] is True, scope, "finite row correction only", "scope")

    derived = {
        "target_emission_ordinal": int(contract["target_emission_ordinal"]),
        "target_parent_coordinate": int(contract["target_parent_coordinate"]),
        "historical_subtract_one_ordinal": int(contract["historical_subtract_one_ordinal"]),
        "explicit_generator_max_error": data["explicit_error"],
        "target_row_min": float(np.min(data["selected"])),
        "target_row_max": float(np.max(data["selected"])),
        "target_row_sum": float(np.sum(data["selected"])),
        "target_core_size": len(data["blocks"][0]),
        "target_tail_size": len(data["blocks"][1]),
        "corrected_direct_residual_gap": data["gap"],
        "r426_direct_reference": float(failure["direct_residual_gap"]),
        "r422_reference": float(failure["r422_residual_gap"]),
        "r422_mismatch": mismatch,
        "historical_wrong_row_gap": data["wrong_gap"],
        "r430_independent_gap": float(r430_independent["derived"]["source_residual_gap_double"]),
        "original_source_interval_certified": False,
        "residual_reuse_closed": False,
        "r426_route_failure_preserved": True,
        "classification": manifest["status"],
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r432-primary/1.0",
        "result_id": "R-432",
        "exploration_id": "EXP-001277",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "run_kind": "primary",
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {
            "manifest": sha256(MANIFEST),
            "r430_manifest": sha256(R430_MANIFEST),
            "r430_independent_script": sha256(R430_INDEPENDENT),
            "r426_manifest": sha256(R426_MANIFEST),
            "r429_manifest": sha256(R429_MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-432 PRIMARY {len(checks)}/{len(checks)} row-contract PASS target_gap={data['gap']:.15g} wrong_ordinal_gap={data['wrong_gap']:.15g} R426_mismatch={mismatch:.15g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "ROW_INDEX_CONTRACT_CORRECTED"
        assert payload["derived"]["target_emission_ordinal"] == 7
        print("R-432 PRIMARY SELFTEST: PASS (fixed conditional-row ordinal)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
