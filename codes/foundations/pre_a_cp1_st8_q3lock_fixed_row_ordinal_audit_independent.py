#!/usr/bin/env python3
"""Non-importing independent lane for the R-432 row-ordinal audit."""

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


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-fixed-row-ordinal-audit-manifest.json"
R419_MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R426_MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R430_INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-source_point_precision_audit/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-fixed_row_ordinal_audit/independent.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_logsumexp(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    maximum = float(np.max(values))
    return maximum + float(np.log(np.sum(np.exp(values - maximum))))


def direct_gap(row: np.ndarray, momentum: np.ndarray, chi: float, threshold: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    weights = np.asarray(row, dtype=float)
    weights /= float(np.sum(weights))
    conductance = (weights[:, None] + weights[None, :]) * np.square(np.abs(momentum)) / (2.0 * chi)
    np.fill_diagonal(conductance, 0.0)
    potential = float(np.max(np.log(weights))) - np.log(weights)
    tail = potential >= threshold
    core = ~tail
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    inverse = 1.0 / np.sqrt(weights)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    core_basis = r422.zero_mean_basis(weights, np.flatnonzero(core))
    tail_basis = r422.zero_mean_basis(weights, np.flatnonzero(tail))
    frame = np.column_stack((core_basis, tail_basis))
    projected = frame.T @ operator @ frame
    gap = float(np.linalg.eigvalsh((projected + projected.T) / 2.0)[0])
    return gap, core, tail, conductance


def reconstruct() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["row_contract"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    failure = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["failure_contract"]
    dimension, volume = 16, 2
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _direct, _shifted = r416.log_coordinate_distribution(hamiltonian, basis, 8.0, dimension, volume)
    # Rebuild the two-site right-oriented emission order without calling the
    # canonical conditional_rows generator.
    marginal0 = np.array([local_logsumexp(log_reference[i, :]) for i in range(dimension)], dtype=float)
    rows = [np.exp(marginal0 - local_logsumexp(marginal0))]
    for parent in range(dimension):
        local = log_reference[parent, :] - marginal0[parent]
        local -= float(np.max(local))
        row = np.exp(local)
        row /= float(np.sum(row))
        rows.append(row)
    target_ordinal = int(contract["target_emission_ordinal"])
    wrong_ordinal = int(contract["historical_subtract_one_ordinal"])
    momentum = r402.coordinate_data(dimension)[2]
    target_gap, core, tail, conductance = direct_gap(rows[target_ordinal], momentum, float(fixture["chi"]), float(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"]))
    wrong_gap, wrong_core, wrong_tail, _wrong_conductance = direct_gap(rows[wrong_ordinal], momentum, float(fixture["chi"]), float(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"]))
    return {"rows": rows, "target_gap": target_gap, "wrong_gap": wrong_gap, "target_row": rows[target_ordinal], "wrong_row": rows[wrong_ordinal], "core": core, "tail": tail, "wrong_core": wrong_core, "wrong_tail": wrong_tail, "conductance": conductance, "failure": failure, "momentum": momentum}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["row_contract"]
    failure = json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["failure_contract"]
    data = reconstruct()
    comparison = float(contract["comparison_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-432" and manifest["exploration_id"] == "EXP-001277" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-432/EXP-001277/false", "provenance")
    check("target ordinal", int(contract["target_emission_ordinal"]) == 7 and int(contract["target_parent_coordinate"]) == 6 and len(data["rows"]) == 17, [contract["target_emission_ordinal"], contract["target_parent_coordinate"], len(data["rows"])], "ordinal 7 -> parent 6", "row contract")
    check("row normalization", np.all(np.isfinite(data["target_row"])) and np.all(data["target_row"] > 0.0) and abs(float(np.sum(data["target_row"])) - 1.0) <= 1e-12, [float(np.min(data["target_row"])), float(np.sum(data["target_row"]))], "positive normalized target row", "source")
    check("target split", [int(np.sum(data["core"])), int(np.sum(data["tail"]))] == [int(failure["core_size"]), int(failure["tail_size"])], [int(np.sum(data["core"])), int(np.sum(data["tail"]))], [failure["core_size"], failure["tail_size"]], "tail split")
    check("target gap positive", np.isfinite(data["target_gap"]) and data["target_gap"] > 0.0, data["target_gap"], ">0", "residual")
    check("target gap matches R-426", abs(data["target_gap"] - float(failure["direct_residual_gap"])) <= comparison, [data["target_gap"], failure["direct_residual_gap"]], f"within {comparison}", "residual")
    mismatch = abs(data["target_gap"] - float(failure["r422_residual_gap"]))
    check("R-422 mismatch", mismatch > comparison, mismatch, f">{comparison}", "R-422 reuse")
    check("subtract-one row differs", int(contract["historical_subtract_one_ordinal"]) == 6 and not np.allclose(data["target_row"], data["wrong_row"], rtol=0.0, atol=1e-14) and abs(data["wrong_gap"] - data["target_gap"]) > comparison, [contract["historical_subtract_one_ordinal"], data["wrong_gap"], data["target_gap"]], "ordinal 6 is not target 7", "row correction")
    historical = json.loads(R430_INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    check("historical lane maps to wrong ordinal", abs(float(historical["derived"]["source_residual_gap_double"]) - data["wrong_gap"]) <= comparison, [historical["derived"]["source_residual_gap_double"], data["wrong_gap"]], f"within {comparison}", "row correction")
    check("source boundary retained", manifest["scope"]["original_source_interval_certified"] is False and manifest["scope"]["residual_reuse_closed"] is False and manifest["scope"]["no_tier_change"] is True, manifest["scope"], "no source interval or tier change", "scope")

    derived = {
        "target_emission_ordinal": int(contract["target_emission_ordinal"]),
        "target_parent_coordinate": int(contract["target_parent_coordinate"]),
        "historical_subtract_one_ordinal": int(contract["historical_subtract_one_ordinal"]),
        "target_row_min": float(np.min(data["target_row"])),
        "target_row_max": float(np.max(data["target_row"])),
        "target_gap": data["target_gap"],
        "r426_direct_reference": float(failure["direct_residual_gap"]),
        "r422_reference": float(failure["r422_residual_gap"]),
        "r422_mismatch": mismatch,
        "historical_wrong_row_gap": data["wrong_gap"],
        "historical_r430_gap": float(historical["derived"]["source_residual_gap_double"]),
        "original_source_interval_certified": False,
        "residual_reuse_closed": False,
        "r426_route_failure_preserved": True,
        "classification": manifest["status"],
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r432-independent/1.0",
        "result_id": "R-432",
        "exploration_id": "EXP-001277",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "independent",
        "verdict": "INDEPENDENT_ROW_INDEX_CORRECTION",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "independent": sha256(Path(__file__)), "historical_r430_independent": sha256(R430_INDEPENDENT_OUTPUT)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "independence_scope": "Manual emission-order reconstruction and direct residual projection; the R-432 primary script and R-430 independent implementation are not imported.",
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-432 INDEPENDENT {len(checks)}/{len(checks)} row-contract PASS target_gap={data['target_gap']:.15g} wrong_ordinal_gap={data['wrong_gap']:.15g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
