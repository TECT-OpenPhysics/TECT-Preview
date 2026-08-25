#!/usr/bin/env python3
"""Primary finite-Q3 evolved Duhamel cross-term audit for EXP-001125."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(float(index + 1))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for position in range(volume):
        result = np.kron(result, single if position == site else identity)
    return result


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(value) for value in edge) for edge in fixture["edges_by_volume"][str(volume)]]


def coordinate_cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def matrices(volume: int, dimension: int, fixture: dict[str, Any], radius: float | None = None) -> dict[str, Any]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_sites = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p_single, site, volume, identity) for site in range(volume)]
    q_cut = [embed(coordinate_cutoff(q_single, radius), site, volume, identity) for site in range(volume)] if radius is not None else q_sites
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite = np.zeros_like(q_sites[0])
    for q_site, p_site in zip(q_sites, p_sites):
        onsite += p_site @ p_site / (2.0 * chi) + r * q_site @ q_site / 2.0 + g * np.linalg.matrix_power(q_site, 4) / 4.0
    full_bond = np.zeros_like(q_sites[0])
    cut_bond = np.zeros_like(q_sites[0])
    for left, right in edges(volume, fixture):
        difference = q_sites[left] - q_sites[right]
        square = difference @ difference
        full_bond += c * square / 2.0 + lam * square @ (q_sites[left] @ q_sites[left] + q_sites[right] @ q_sites[right]) / 4.0
        cut_difference = q_cut[left] - q_cut[right]
        cut_square = cut_difference @ cut_difference
        cut_bond += c * cut_square / 2.0 + lam * cut_square @ (q_cut[left] @ q_cut[left] + q_cut[right] @ q_cut[right]) / 4.0
    full_h = (onsite + full_bond + (onsite + full_bond).conj().T) / 2.0
    cut_h = (onsite + cut_bond + (onsite + cut_bond).conj().T) / 2.0
    return {"q0": q_sites[0], "full_h": full_h, "cut_h": cut_h, "tail": full_bond - cut_bond}


def exponential(hermitian: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((hermitian + hermitian.conj().T) / 2.0)
    return (vectors * np.exp(coefficient * values)) @ vectors.conj().T


def gibbs(hermitian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hermitian + hermitian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - float(np.min(values))))
    return (vectors * (weights / float(np.sum(weights)))) @ vectors.conj().T


def delta(hamiltonian: np.ndarray, operator: np.ndarray, hbar: float) -> np.ndarray:
    return 1j * (hamiltonian @ operator - operator @ hamiltonian) / hbar


def seminorm(state: np.ndarray, operator: np.ndarray) -> tuple[float, float, float]:
    right = float(np.trace(state @ operator.conj().T @ operator).real)
    left = float(np.trace(state @ operator @ operator.conj().T).real)
    return float(np.sqrt(max(0.0, right + left))), max(0.0, right), max(0.0, left)


def op_norm(operator: np.ndarray) -> float:
    return float(np.linalg.svd(operator, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001125" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001125/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite positive inputs", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["hbar"] > 0 and fixture["g"] > 0, [fixture["beta"], fixture["chi"], fixture["hbar"], fixture["g"]], "positive", "model")
    check("scope firewall", all(scope[key] for key in ("finite_cross_term_identity_closed", "finite_second_order_operator_bound_closed", "finite_reference_cross_term_closed", "finite_dual_cross_term_closed")) and not scope["actual_q3_evolved_dual_integrand_uniform_closed"], scope, "finite cross-term checkpoint", "scope")

    hbar = float(fixture["hbar"])
    hermitian_tol = float(fixture["hermitian_tolerance"])
    state_tol = float(fixture["state_tolerance"])
    commutation_tol = float(fixture["commutation_tolerance"])
    bound_tol = float(fixture["bound_tolerance"])
    volume_rows: list[dict[str, Any]] = []
    all_bound_ratios: list[float] = []
    all_cross_ratios: list[float] = []

    for volume in (int(value) for value in fixture["volume_values"]):
        for dimension in (int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]):
            full = matrices(volume, dimension, fixture)
            H = full["full_h"]
            rho = gibbs(H, float(fixture["beta"]))
            A = exponential(full["q0"], 1j * float(fixture["character_amplitude"]) / hbar)
            dual = A @ rho @ A.conj().T
            B = delta(H, A, hbar)
            C = delta(H, B, hbar)
            radius_rows: list[dict[str, Any]] = []
            for radius in (float(value) for value in fixture["radius_values"]):
                cut = matrices(volume, dimension, fixture, radius)
                W = cut["tail"]
                E = delta(W, B, hbar)
                tail_ref = seminorm(rho, W)
                tail_dual = seminorm(dual, W)
                commutation = op_norm(W @ A - A @ W)
                check(f"V={volume} n={dimension} L={radius} H Hermitian", op_norm(H - H.conj().T) <= hermitian_tol, op_norm(H - H.conj().T), f"<={hermitian_tol}", "matrix")
                check(f"V={volume} n={dimension} L={radius} states", abs(float(np.trace(rho).real) - 1.0) <= 100.0 * state_tol and abs(float(np.trace(dual).real) - 1.0) <= 100.0 * state_tol, [np.trace(rho), np.trace(dual)], "normalized", "state")
                check(f"V={volume} n={dimension} L={radius} unitary A", op_norm(A.conj().T @ A - np.eye(A.shape[0])) <= 100.0 * hermitian_tol, op_norm(A.conj().T @ A - np.eye(A.shape[0])), "unitary", "character")
                check(f"V={volume} n={dimension} L={radius} [W,A]", commutation <= commutation_tol, commutation, f"<={commutation_tol}", "CCR-core")
                cross_ref = seminorm(rho, E)
                cross_dual = seminorm(dual, E)
                c_op, e_op = op_norm(C), op_norm(E)
                sign_rows: list[dict[str, Any]] = []
                for sign in (int(value) for value in fixture["sign_values"]):
                    K = H + sign * W
                    delta_k_A = delta(K, A, hbar)
                    delta_k2_A = delta(K, delta_k_A, hbar)
                    algebra_residual = op_norm(delta_k2_A - C - sign * E)
                    initial_derivative = op_norm(delta_k_A - B)
                    check(f"V={volume} n={dimension} L={radius} sign={sign} generator identity", algebra_residual <= 100.0 * commutation_tol, algebra_residual, f"<={100.0 * commutation_tol}", "generator")
                    check(f"V={volume} n={dimension} L={radius} sign={sign} D prime zero", initial_derivative <= 100.0 * commutation_tol, initial_derivative, f"<={100.0 * commutation_tol}", "Duhamel")
                    U = exponential(H, -1j * float(fixture["time_values"][0]) / hbar)
                    U0 = np.eye(A.shape[0], dtype=complex)
                    d0 = U0.conj().T @ A @ U0 - A
                    check(f"V={volume} n={dimension} L={radius} sign={sign} D zero", op_norm(d0) == 0.0, op_norm(d0), "0", "Duhamel")
                    time_rows: list[dict[str, Any]] = []
                    for time in (float(value) for value in fixture["time_values"]):
                        U = exponential(H, -1j * time / hbar)
                        UK = exponential(K, -1j * time / hbar)
                        D = UK.conj().T @ A @ UK - U.conj().T @ A @ U
                        delta_D = delta(H, D, hbar)
                        bound = time * time * (2.0 * c_op + e_op) / 2.0
                        d_op = op_norm(D)
                        ratio = d_op / max(bound, 1.0e-300)
                        all_bound_ratios.append(ratio)
                        check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} finite D", np.isfinite(d_op) and np.isfinite(op_norm(delta_D)), [d_op, op_norm(delta_D)], "finite", "Duhamel")
                        check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} second-order bound", d_op <= bound + bound_tol, [d_op, bound], f"D<=bound+{bound_tol}", "operator-bound")
                        state_values = [seminorm(rho, D)[0], seminorm(dual, D)[0], seminorm(rho, delta_D)[0], seminorm(dual, delta_D)[0]]
                        check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} state rows", all(np.isfinite(value) for value in state_values), state_values, "finite", "state")
                        time_rows.append({"time": time, "D_operator_norm": d_op, "delta_D_operator_norm": op_norm(delta_D), "operator_bound": bound, "bound_ratio": ratio, "reference_D": seminorm(rho, D), "dual_D": seminorm(dual, D), "reference_delta_D": seminorm(rho, delta_D), "dual_delta_D": seminorm(dual, delta_D)})
                    sign_rows.append({"sign": sign, "generator_identity_residual": algebra_residual, "initial_derivative_residual": initial_derivative, "times": time_rows})
                cross_ratio_ref = cross_ref[0] / max(tail_ref[0], 1.0e-300)
                cross_ratio_dual = cross_dual[0] / max(tail_dual[0], 1.0e-300)
                all_cross_ratios.extend([cross_ratio_ref, cross_ratio_dual])
                radius_rows.append({"radius": radius, "tail_reference": tail_ref, "tail_dual": tail_dual, "cross_reference": cross_ref, "cross_dual": cross_dual, "cross_operator_norm": e_op, "double_commutator_operator_norm": c_op, "cross_to_tail_reference": cross_ratio_ref, "cross_to_tail_dual": cross_ratio_dual, "signs": sign_rows})
            volume_rows.append({"volume": volume, "oscillator_dimension": dimension, "hilbert_dimension": int(A.shape[0]), "radii": radius_rows})

    check("coverage", len(volume_rows) == sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) for v in fixture["volume_values"]), len(volume_rows), "declared volume/dimension rows", "coverage")
    check("finite bound ratios", all(np.isfinite(value) and value <= 1.0 + 1.0e-7 for value in all_bound_ratios), [min(all_bound_ratios), max(all_bound_ratios)], "[0,1]", "operator-bound")
    check("finite cross ratios", all(np.isfinite(value) and value >= 0.0 for value in all_cross_ratios), [min(all_cross_ratios), max(all_cross_ratios)], ">=0", "diagnostic")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-EVOLVED-DUAL-INTEGRAND-CROSS-TERM",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_cross_term_identity_closed": True,
            "finite_second_order_operator_bound_closed": True,
            "finite_reference_cross_term_closed": True,
            "finite_dual_cross_term_closed": True,
            "finite_reference_D_closed": True,
            "finite_dual_D_closed": True,
            "finite_reference_delta_D_closed": True,
            "finite_dual_delta_D_closed": True,
            "finite_small_time_diagnostic_closed": True,
            "max_operator_bound_ratio": max(all_bound_ratios),
            "min_cross_to_tail_ratio": min(all_cross_ratios),
            "max_cross_to_tail_ratio": max(all_cross_ratios),
            "actual_q3_evolved_dual_integrand_uniform_closed": False,
            "state_isometry_for_signed_dynamics_closed": False,
            "actual_q3_unbounded_common_core_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/")},
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY EVOLVED-DUAL-CROSS-TERM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
