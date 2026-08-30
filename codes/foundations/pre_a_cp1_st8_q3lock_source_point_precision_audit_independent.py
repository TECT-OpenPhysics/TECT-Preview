#!/usr/bin/env python3
"""Independent double-source control for R-430.

The lane does not import the R-430 mpmath module.  It reconstructs the same
finite row from the declared R-419/R-416/R-402 sources and uses a separate
NumPy residual projection.  It is a control on row selection and sign
separation, not an interval certificate.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
PRIMARY_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-source_point_precision_audit/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-source_point_precision_audit/independent.json"

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


def reconstruct() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    volume, dimension = int(target["volume"]), int(target["cutoff_dimension"])
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    coordinate_basis = r419.r399.coordinate_basis(dimension, volume)
    beta = float(target["beta"])
    log_reference, _, _ = r416.log_coordinate_distribution(hamiltonian, coordinate_basis, beta, dimension, volume)
    order = list(range(volume)) if target["orientation"] == "right" else list(reversed(range(volume)))
    selected: np.ndarray | None = None
    for index, (weights, _minimum_log_row) in enumerate(
        r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"]))
    ):
        if index == int(target["conditional_row_index"]) - 1:
            selected = np.asarray(weights, dtype=float)
            break
    if selected is None:
        raise AssertionError("fixed conditional row is absent")
    _levels, _vectors, momentum = r402.coordinate_data(dimension)
    graph = r416.projected_graph(selected, momentum, float(fixture["chi"]))
    pi = np.asarray(graph["weights"], dtype=float)
    conductance = np.asarray(graph["conductance"], dtype=float)
    threshold = float(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"])
    phi = np.max(np.log(pi)) - np.log(pi)
    tail = phi >= threshold
    blocks = [np.flatnonzero(~tail), np.flatnonzero(tail)]
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    operator = laplacian / np.sqrt(pi[:, None] * pi[None, :])
    operator = (operator + operator.T) / 2.0
    basis = np.column_stack([r422.zero_mean_basis(pi, block) for block in blocks])
    compressed = (basis.T @ operator @ basis)
    compressed = (compressed + compressed.T) / 2.0
    gap = float(np.linalg.eigvalsh(compressed)[0])
    return pi, conductance, blocks, np.asarray([gap], dtype=float)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    pi, conductance, blocks, values = reconstruct()
    gap = values[0]
    reference = float(target["r422_residual_gap"])
    mismatch = abs(gap - reference)
    comparison = float(thresholds["comparison_tolerance"])
    checks = [
        {"name": "manifest identity", "status": "PASS" if manifest["result_id"] == "R-430" and manifest["exploration_id"] == "EXP-001275" and manifest["claim_bearing"] is False else "FAIL", "actual": [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "expected": "R-430/EXP-001275/false"},
        {"name": "fixed source row", "status": "PASS" if [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7] else "FAIL", "actual": [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]], "expected": "V2/d16/beta8/right/row7"},
        {"name": "positive normalized row", "status": "PASS" if np.all(np.isfinite(pi)) and np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= float(thresholds["row_reconstruction_tolerance"]) else "FAIL", "actual": [float(np.min(pi)), float(np.max(pi)), float(np.sum(pi))], "expected": "positive normalized"},
        {"name": "reversible graph", "status": "PASS" if np.all(np.isfinite(conductance)) and np.all(conductance >= 0.0) and float(np.max(np.abs(conductance - conductance.T))) <= comparison else "FAIL", "actual": float(np.max(np.abs(conductance - conductance.T))), "expected": f"<={comparison}"},
        {"name": "block dimensions", "status": "PASS" if [len(block) for block in blocks] == [int(target["core_size"]), int(target["tail_size"])] else "FAIL", "actual": [len(block) for block in blocks], "expected": [target["core_size"], target["tail_size"]]},
        {"name": "source gap positive", "status": "PASS" if np.isfinite(gap) and gap > 0.0 else "FAIL", "actual": gap, "expected": ">0"},
        {"name": "source gap separated", "status": "PASS" if mismatch > comparison else "FAIL", "actual": mismatch, "expected": f">{comparison}"},
        {"name": "point-only firewall", "status": "PASS" if primary["verdict"] == "SOURCE_POINT_AUDIT_NO_INTERVAL" and primary["derived"]["source_interval_certified"] is False and primary["derived"]["exact_original_input_certified"] is False else "FAIL", "actual": [primary["verdict"], primary["derived"]["source_interval_certified"], primary["derived"]["exact_original_input_certified"]], "expected": "point audit without interval"},
        {"name": "source precision sensitivity recorded", "status": "PASS" if abs(gap - float(primary["derived"]["source_residual_gap_decimal"])) > comparison else "FAIL", "actual": abs(gap - float(primary["derived"]["source_residual_gap_decimal"])), "expected": f">{comparison} (independent double versus mpmath point)"},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r430-independent/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-430",
        "exploration_id": "EXP-001275",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_SOURCE_SENSITIVITY_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])}, "source_residual_gap_double": gap, "primary_mpmath_gap": float(primary["derived"]["source_residual_gap_decimal"]), "source_point_gap_difference": abs(gap - float(primary["derived"]["source_residual_gap_decimal"])), "r422_reference": reference, "mismatch_r422": mismatch, "source_interval_certified": False, "exact_original_input_certified": False, "residual_reuse_closed": False, "r426_route_failure_preserved": True},
        "source_hashes": {"independent": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "primary_run": sha256(PRIMARY_OUTPUT)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED INDEPENDENT DOUBLE-SOURCE CONTROL; NO INTERVAL CERTIFICATION",
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "independence_scope": "Separate NumPy reconstruction from R-419/R-416/R-402 with independent residual projection; the mpmath primary module is not imported.",
    }
    atomic_json(output, payload)
    print(f"R-430 INDEPENDENT SOURCE_POINT_AUDIT_NO_INTERVAL {len(checks)}/{len(checks)} gap={gap:.17g} mismatch={mismatch:.17g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_SOURCE_SENSITIVITY_CONTROL"
        print("R-430 INDEPENDENT SELFTEST: PASS (double-source control)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
