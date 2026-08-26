#!/usr/bin/env python3
"""Primary kinetic-inclusive Q3 transfer diagnostic (EXP-001193)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-kinetic-inclusive-transfer-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
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


def load_fixture(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    current = manifest
    lineage: list[str] = []
    while "finite_fixture" not in current:
        lineage.append(str(current.get("exploration_id", "unknown")))
        current = json.loads((REPO / current["fixture_source"]).read_text(encoding="utf-8"))
    lineage.append(str(current.get("exploration_id", "unknown")))
    return current["finite_fixture"], lineage


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def spectral_inverse_square(matrix: np.ndarray) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    minimum = float(np.min(values))
    if minimum <= 0.0:
        raise ValueError(f"matrix is not strictly positive: {minimum}")
    return (vectors * np.power(values, -2.0)) @ vectors.conj().T, minimum


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, lineage = load_fixture(manifest)
    finite_test, scope = manifest["finite_test"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001193" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001193/T-054", "provenance")
    check("fixture lineage", lineage[-1] == "EXP-001188", lineage, "ends at EXP-001188", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["generic_form_order_shortcut_refuted"] and scope["finite_q3_kinetic_diagnostic_closed"] and scope["finite_q3_relative_quotient_rows_closed"] and scope["finite_q3_trace_rows_closed"] and not scope["uniform_kinetic_inclusive_operator_order_closed"] and not scope["uniform_gibbs_potential_moment_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite diagnostic; analytic/QFT gates open", "scope")

    tolerance = float(fixture["unitary_tolerance"])
    A = np.asarray(finite_test["generic_A"], dtype=float)
    B = np.asarray(finite_test["generic_B"], dtype=float)
    K = np.asarray(finite_test["generic_K"], dtype=float)
    expected_difference = np.asarray(finite_test["generic_fourth_difference"], dtype=float)
    A4, K4 = A @ A @ A @ A, K @ K @ K @ K
    difference = hermitian(K4 - A4)
    check("generic A positive", float(np.min(np.linalg.eigvalsh(A))) >= -tolerance, np.linalg.eigvalsh(A).tolist(), ">=0", "generic boundary")
    check("generic B positive", float(np.min(np.linalg.eigvalsh(B))) >= -tolerance, np.linalg.eigvalsh(B).tolist(), ">=0", "generic boundary")
    check("generic K decomposition", np.allclose(K, A + B, atol=tolerance), K.tolist(), "A+B", "generic boundary")
    check("generic K positive", float(np.min(np.linalg.eigvalsh(K))) > tolerance, np.linalg.eigvalsh(K).tolist(), ">0", "generic boundary")
    check("generic fourth arithmetic", np.allclose(difference, expected_difference, atol=tolerance), difference.tolist(), expected_difference.tolist(), "generic boundary")
    check("rank-one B determinant", abs(float(np.linalg.det(B))) <= tolerance, float(np.linalg.det(B)), "0", "generic boundary")
    check("fourth determinant negative", float(np.linalg.det(difference)) < -1.0, float(np.linalg.det(difference)), "< -1", "generic boundary")
    check("fourth order shortcut fails", float(np.min(np.linalg.eigvalsh(difference))) < -tolerance, np.linalg.eigvalsh(difference).tolist(), "not positive semidefinite", "generic boundary")

    c, g, r = float(fixture["c"]), float(fixture["g"]), float(fixture["r"])
    shift = r * r / (4.0 * g)
    rows: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_ops, hamiltonian, _, _ = q3.build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        k_full = hermitian(hamiltonian + (1.0 + volume * shift) * identity)
        potential = sum((r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q in q_ops[:2]), np.zeros_like(hamiltonian))
        k_pot = hermitian(potential + (1.0 + 2.0 * shift) * identity)
        k_full4 = k_full @ k_full @ k_full @ k_full
        k_pot4 = k_pot @ k_pot @ k_pot @ k_pot
        defect = hermitian(k_full4 - k_pot4)
        inverse_square, floor = spectral_inverse_square(k_full)
        relative = hermitian(inverse_square @ k_pot4 @ inverse_square)
        quotient = operator_norm(relative)
        min_defect = float(np.min(np.linalg.eigvalsh(defect)))
        check(f"V={volume} full floor", floor > 0.0, floor, ">0", "finite kinetic")
        check(f"V={volume} direct fourth defect", min_defect >= -tolerance, min_defect, ">=0 within finite tolerance", "finite kinetic")
        for beta in (float(value) for value in fixture["beta_values"]):
            rho = q3.gibbs(hamiltonian, beta)
            potential_moment = float(np.real(np.trace(rho @ k_pot4)))
            full_moment = float(np.real(np.trace(rho @ k_full4)))
            trace_slack = full_moment - potential_moment
            values = {"volume": volume, "oscillator_dimension": dimension, "beta": beta, "full_shifted_floor": floor, "min_fourth_defect": min_defect, "kinetic_relative_quotient": quotient, "potential_fourth_moment": potential_moment, "full_fourth_moment": full_moment, "trace_slack": trace_slack}
            check(f"V={volume} beta={beta} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "finite kinetic")
            check(f"V={volume} beta={beta} trace diagnostic", trace_slack >= -tolerance * (1.0 + full_moment), trace_slack, "finite tolerance", "finite Gibbs")
            rows.append(values)
    expected_rows = len(fixture["scenarios"]) * len(fixture["beta_values"])
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    summaries: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        members = [row for row in rows if row["volume"] == int(scenario["volume"])]
        summaries.append({"volume": int(scenario["volume"]), "oscillator_dimension": int(scenario["oscillator_dimension"]), "max_kinetic_relative_quotient": max(row["kinetic_relative_quotient"] for row in members), "min_fourth_defect": min(row["min_fourth_defect"] for row in members), "max_potential_fourth_moment": max(row["potential_fourth_moment"] for row in members), "max_full_fourth_moment": max(row["full_fourth_moment"] for row in members), "min_trace_slack": min(row["trace_slack"] for row in members)})
    check("summary coverage", len(summaries) == len(fixture["scenarios"]), len(summaries), len(fixture["scenarios"]), "coverage")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-KINETIC-INCLUSIVE-TRANSFER-BOUNDARY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"generic_A": A.tolist(), "generic_B": B.tolist(), "generic_K": K.tolist(), "generic_fourth_difference": difference.tolist(), "generic_fourth_difference_determinant": float(np.linalg.det(difference)), "generic_fourth_difference_min_eigenvalue": float(np.min(np.linalg.eigvalsh(difference))), "rows": rows, "summary_rows": summaries, "shift_per_site": shift, "generic_form_order_shortcut_refuted": True, "finite_q3_kinetic_diagnostic_closed": True, "finite_q3_relative_quotient_rows_closed": True, "finite_q3_trace_rows_closed": True, "uniform_kinetic_inclusive_operator_order_closed": False, "uniform_gibbs_potential_moment_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY KINETIC-INCLUSIVE-TRANSFER-BOUNDARY PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['derived']['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())