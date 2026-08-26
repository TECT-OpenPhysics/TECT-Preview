#!/usr/bin/env python3
"""Independent kinetic-inclusive Q3 transfer diagnostic (EXP-001193).

The finite matrices and exact 2x2 boundary witness are rebuilt without
importing the primary audit or its Q3 helper.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-kinetic-inclusive-transfer-boundary"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("unexpected finite volume")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def build_volume(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [bond_term(q_ops[left], q_ops[right], fixture) for left, right in graph_edges(volume)]
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds, zero)
    return q_ops, (full + full.conj().T) / 2.0


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def inverse_square(matrix: np.ndarray) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    floor = float(np.min(values))
    if floor <= 0.0:
        raise ValueError("matrix is not strictly positive")
    return (vectors * np.power(values, -2.0)) @ vectors.conj().T, floor


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
    difference = hermitian(K @ K @ K @ K - A @ A @ A @ A)
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
        q_ops, hamiltonian = build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        k_full = hermitian(hamiltonian + (1.0 + volume * shift) * identity)
        potential = sum((r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q in q_ops[:2]), np.zeros_like(hamiltonian))
        k_pot = hermitian(potential + (1.0 + 2.0 * shift) * identity)
        full4 = k_full @ k_full @ k_full @ k_full
        pot4 = k_pot @ k_pot @ k_pot @ k_pot
        defect = hermitian(full4 - pot4)
        inv2, floor = inverse_square(k_full)
        relative = hermitian(inv2 @ pot4 @ inv2)
        quotient = operator_norm(relative)
        min_defect = float(np.min(np.linalg.eigvalsh(defect)))
        check(f"V={volume} full floor", floor > 0.0, floor, ">0", "finite kinetic")
        check(f"V={volume} direct fourth defect", min_defect >= -tolerance, min_defect, ">=0 within finite tolerance", "finite kinetic")
        for beta in (float(value) for value in fixture["beta_values"]):
            rho = gibbs(hamiltonian, beta)
            potential_moment = float(np.real(np.trace(rho @ pot4)))
            full_moment = float(np.real(np.trace(rho @ full4)))
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

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-KINETIC-INCLUSIVE-TRANSFER-BOUNDARY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"generic_A": A.tolist(), "generic_B": B.tolist(), "generic_K": K.tolist(), "generic_fourth_difference": difference.tolist(), "generic_fourth_difference_determinant": float(np.linalg.det(difference)), "generic_fourth_difference_min_eigenvalue": float(np.min(np.linalg.eigvalsh(difference))), "rows": rows, "summary_rows": summaries, "shift_per_site": shift, "generic_form_order_shortcut_refuted": True, "finite_q3_kinetic_diagnostic_closed": True, "finite_q3_relative_quotient_rows_closed": True, "finite_q3_trace_rows_closed": True, "uniform_kinetic_inclusive_operator_order_closed": False, "uniform_gibbs_potential_moment_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT KINETIC-INCLUSIVE-TRANSFER-BOUNDARY PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['derived']['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())