#!/usr/bin/env python3
"""Independent finite-Q3 Gibbs condition-number lane for EXP-001126."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_gibbs_isometry_condition_number_audit"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.diag(np.sqrt(np.arange(1, size, dtype=float)), 1).astype(complex)
    return (lower + lower.T.conj()) / np.sqrt(2.0), (lower - lower.T.conj()) / (1j * np.sqrt(2.0))


def site(single: np.ndarray, index: int, volume: int, size: int) -> np.ndarray:
    result = single if index == 0 else np.eye(size, dtype=complex)
    for position in range(1, volume):
        result = np.kron(result, single if position == index else np.eye(size, dtype=complex))
    return result


def edge_list(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, pair)) for pair in fixture["edges_by_volume"][str(volume)]]


def cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.T.conj()) / 2.0)
    scale = np.abs(values) / radius
    eta = np.where(scale <= 1.0, 1.0, np.where(scale < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scale - 1.0))), 0.0))
    return vectors @ np.diag(values * eta) @ vectors.T.conj()


def build(volume: int, size: int, fixture: dict[str, Any], radius: float | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(size)
    qs = [site(q, index, volume, size) for index in range(volume)]
    ps = [site(p, index, volume, size) for index in range(volume)]
    qcut = [site(cutoff(q, radius), index, volume, size) for index in range(volume)] if radius is not None else qs
    dim = size**volume
    onsite = np.zeros((dim, dim), dtype=complex)
    for qx, px in zip(qs, ps):
        onsite += px @ px / (2.0 * float(fixture["chi"])) + float(fixture["r"]) * qx @ qx / 2.0 + float(fixture["g"]) * np.linalg.matrix_power(qx, 4) / 4.0
    bond = np.zeros_like(onsite)
    cut_bond = np.zeros_like(onsite)
    for left, right in edge_list(volume, fixture):
        diff = qs[left] - qs[right]
        diff2 = diff @ diff
        bond += float(fixture["c"]) * diff2 / 2.0 + float(fixture["lambda"]) * diff2 @ (qs[left] @ qs[left] + qs[right] @ qs[right]) / 4.0
        c_diff = qcut[left] - qcut[right]
        c_diff2 = c_diff @ c_diff
        cut_bond += float(fixture["c"]) * c_diff2 / 2.0 + float(fixture["lambda"]) * c_diff2 @ (qcut[left] @ qcut[left] + qcut[right] @ qcut[right]) / 4.0
    raw = onsite + bond
    raw_cut = onsite + cut_bond
    return (raw + raw.T.conj()) / 2.0, (raw_cut + raw_cut.T.conj()) / 2.0, qs[0]


def expm(matrix: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    return vectors @ np.diag(np.exp(coefficient * values)) @ vectors.T.conj()


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    weights = np.exp(-beta * (values - values.min()))
    return vectors @ np.diag(weights / weights.sum()) @ vectors.T.conj()


def deriv(matrix: np.ndarray, operator: np.ndarray, hbar: float) -> np.ndarray:
    return 1j * (matrix @ operator - operator @ matrix) / hbar


def seminorm(state: np.ndarray, operator: np.ndarray) -> float:
    right = float(np.trace(state @ operator.T.conj() @ operator).real)
    left = float(np.trace(state @ operator @ operator.T.conj()).real)
    return float(np.sqrt(max(0.0, right + left)))


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001126" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001126/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_gibbs_condition_number_identity_closed"] and scope["finite_dual_spectrum_invariance_closed"] and not scope["global_gibbs_isometry_uniform_closed"], scope, "finite checkpoint", "scope")

    hbar = float(fixture["hbar"])
    state_tol = float(fixture["state_tolerance"])
    compare_tol = float(fixture["comparison_tolerance"])
    logs: list[float] = []
    ratios_log: list[float] = []
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        for size in map(int, fixture["oscillator_dimensions_by_volume"][str(volume)]):
            H, _, q0 = build(volume, size, fixture)
            rho = gibbs(H, float(fixture["beta"]))
            A = expm(q0, 1j * float(fixture["character_amplitude"]) / hbar)
            dual = A @ rho @ A.T.conj()
            energies = np.linalg.eigvalsh((H + H.T.conj()) / 2.0)
            eigenvalues = np.linalg.eigvalsh((rho + rho.T.conj()) / 2.0)
            log_kappa = float(fixture["beta"]) * float(energies[-1] - energies[0])
            dual_values = np.sort(np.linalg.eigvalsh((dual + dual.T.conj()) / 2.0))
            ref_values = np.sort(eigenvalues)
            check(f"V={volume} n={size} faithful", float(np.min(eigenvalues)) > 0.0, float(np.min(eigenvalues)), ">0", "state")
            check(f"V={volume} n={size} dual spectrum", np.max(np.abs(dual_values - ref_values)) <= 100.0 * state_tol, np.max(np.abs(dual_values - ref_values)), f"<={100.0 * state_tol}", "dual")
            B = deriv(H, A, hbar)
            C = deriv(H, B, hbar)
            radius_rows: list[dict[str, Any]] = []
            for radius in map(float, fixture["radius_values"]):
                _, cut_h, _ = build(volume, size, fixture, radius)
                W = H - cut_h
                E = deriv(W, B, hbar)
                sign_rows: list[dict[str, Any]] = []
                for sign in map(int, fixture["sign_values"]):
                    K = H + sign * W
                    time_rows: list[dict[str, Any]] = []
                    for time in map(float, fixture["time_values"]):
                        unitary_rows = {"H": expm(H, -1j * time / hbar), "signed": expm(K, -1j * time / hbar)}
                        obs_rows: list[dict[str, Any]] = []
                        for label, X in (("C", C), ("E", E)):
                            base_ref, base_dual = seminorm(rho, X), seminorm(dual, X)
                            ratio_rows: dict[str, float] = {}
                            for name, U in unitary_rows.items():
                                ratio_rows[f"reference_{name}"] = seminorm(rho, U.T.conj() @ X @ U) / max(base_ref, 1.0e-300)
                                ratio_rows[f"dual_{name}"] = seminorm(dual, U.T.conj() @ X @ U) / max(base_dual, 1.0e-300)
                            ratios_log.extend(float(np.log(max(value, 1.0e-300))) for value in ratio_rows.values())
                            check(f"V={volume} n={size} L={radius} t={time} sign={sign} {label} finite", all(np.isfinite(value) for value in ratio_rows.values()), ratio_rows, "finite", "isometry")
                            check(f"V={volume} n={size} L={radius} t={time} sign={sign} {label} bound", np.log(max(max(ratio_rows.values()), 1.0e-300)) <= 0.5 * log_kappa + compare_tol, [max(ratio_rows.values()), log_kappa], "log ratio bound", "isometry")
                            obs_rows.append({"label": label, "reference_base": base_ref, "dual_base": base_dual, "ratios": ratio_rows})
                        time_rows.append({"time": time, "observables": obs_rows})
                    sign_rows.append({"sign": sign, "times": time_rows})
                logs.append(log_kappa)
                radius_rows.append({"radius": radius, "cross_operator_norm": norm(E), "double_commutator_operator_norm": norm(C), "signs": sign_rows})
            volume_rows.append({"volume": volume, "oscillator_dimension": size, "hilbert_dimension": size**volume, "log_condition_number": log_kappa, "sqrt_condition_log": 0.5 * log_kappa, "rho_min": float(np.min(eigenvalues)), "rho_max": float(np.max(eigenvalues)), "radii": radius_rows})

    check("coverage", len(volume_rows) == sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) for v in fixture["volume_values"]), len(volume_rows), "declared", "coverage")
    check("condition logs", min(logs) > 0.0 and all(np.isfinite(value) for value in logs), [min(logs), max(logs)], ">0", "condition")
    check("ratio logs", all(np.isfinite(value) for value in ratios_log), [min(ratios_log), max(ratios_log)], "finite", "isometry")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-GIBBS-ISOMETRY-CONDITION-NUMBER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"volume_rows": volume_rows, "finite_gibbs_condition_number_identity_closed": True, "finite_dual_spectrum_invariance_closed": True, "finite_state_isometry_comparison_closed": True, "finite_q3_condition_number_audit_closed": True, "min_log_condition_number": min(logs), "max_log_condition_number": max(logs), "min_log_state_isometry_ratio": min(ratios_log), "max_log_state_isometry_ratio": max(ratios_log), "global_gibbs_isometry_uniform_closed": False, "local_modular_weight_uniform_closed": False, "actual_q3_evolved_dual_integrand_uniform_closed": False, "actual_q3_unbounded_common_core_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT GIBBS-CONDITION-NUMBER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
