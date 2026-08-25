#!/usr/bin/env python3
"""Independent NumPy lane for EXP-001125.

This lane rebuilds the finite oscillator, graph Hamiltonian, Gibbs states and
second-generator cross-term without importing the primary implementation.
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
SLUG = "pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit"
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
    lowering = np.diag(np.sqrt(np.arange(1, size, dtype=float)), 1).astype(complex)
    raising = lowering.T.conj()
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def tensor_at(single: np.ndarray, site: int, volume: int, size: int) -> np.ndarray:
    factors = [single if index == site else np.eye(size, dtype=complex) for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def graph(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, pair)) for pair in fixture["edges_by_volume"][str(volume)]]


def taper(q: np.ndarray, radius: float) -> np.ndarray:
    eigenvalues, vectors = np.linalg.eigh((q + q.conj().T) * 0.5)
    ratio = np.abs(eigenvalues) / radius
    eta = np.ones_like(ratio)
    transition = (ratio > 1.0) & (ratio < 2.0)
    eta[transition] = 0.5 * (1.0 + np.cos(np.pi * (ratio[transition] - 1.0)))
    eta[ratio >= 2.0] = 0.0
    return vectors @ np.diag(eigenvalues * eta) @ vectors.conj().T


def build(volume: int, size: int, fixture: dict[str, Any], radius: float | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(size)
    q_sites = [tensor_at(q, site, volume, size) for site in range(volume)]
    p_sites = [tensor_at(p, site, volume, size) for site in range(volume)]
    q_cut = [tensor_at(taper(q, radius), site, volume, size) for site in range(volume)] if radius is not None else q_sites
    dim = size**volume
    onsite = np.zeros((dim, dim), dtype=complex)
    for q_site, p_site in zip(q_sites, p_sites):
        onsite = onsite + p_site @ p_site / (2.0 * float(fixture["chi"]))
        onsite = onsite + float(fixture["r"]) * q_site @ q_site / 2.0
        onsite = onsite + float(fixture["g"]) * q_site @ q_site @ q_site @ q_site / 4.0
    full_bond = np.zeros_like(onsite)
    cut_bond = np.zeros_like(onsite)
    for left, right in graph(volume, fixture):
        diff = q_sites[left] - q_sites[right]
        diff2 = diff @ diff
        full_bond = full_bond + float(fixture["c"]) * diff2 / 2.0 + float(fixture["lambda"]) * diff2 @ (q_sites[left] @ q_sites[left] + q_sites[right] @ q_sites[right]) / 4.0
        cut_diff = q_cut[left] - q_cut[right]
        cut2 = cut_diff @ cut_diff
        cut_bond = cut_bond + float(fixture["c"]) * cut2 / 2.0 + float(fixture["lambda"]) * cut2 @ (q_cut[left] @ q_cut[left] + q_cut[right] @ q_cut[right]) / 4.0
    raw = onsite + full_bond
    raw_cut = onsite + cut_bond
    return (raw + raw.T.conj()) / 2.0, (raw_cut + raw_cut.T.conj()) / 2.0, q_sites[0]


def unitary_from_hermitian(matrix: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    return vectors @ np.diag(np.exp(coefficient * values)) @ vectors.T.conj()


def state(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T.conj()) / 2.0)
    weights = np.exp(-beta * (values - values.min()))
    return vectors @ np.diag(weights / weights.sum()) @ vectors.T.conj()


def deriv(matrix: np.ndarray, operator: np.ndarray, hbar: float) -> np.ndarray:
    return 1j * (matrix @ operator - operator @ matrix) / hbar


def two_leg_norm(rho: np.ndarray, operator: np.ndarray) -> tuple[float, float, float]:
    right = float(np.trace(rho @ operator.T.conj() @ operator).real)
    left = float(np.trace(rho @ operator @ operator.T.conj()).real)
    return float(np.sqrt(max(0.0, right + left))), max(0.0, right), max(0.0, left)


def spectral_norm(operator: np.ndarray) -> float:
    return float(np.max(np.linalg.svd(operator, compute_uv=False)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001125" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001125/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_cross_term_identity_closed"] and scope["finite_second_order_operator_bound_closed"] and not scope["actual_q3_evolved_dual_integrand_uniform_closed"], scope, "finite checkpoint", "scope")

    hbar = float(fixture["hbar"])
    hermitian_tol = float(fixture["hermitian_tolerance"])
    state_tol = float(fixture["state_tolerance"])
    commutation_tol = float(fixture["commutation_tolerance"])
    bound_tol = float(fixture["bound_tolerance"])
    rows: list[dict[str, Any]] = []
    bound_ratios: list[float] = []
    cross_ratios: list[float] = []
    for volume in map(int, fixture["volume_values"]):
        for size in map(int, fixture["oscillator_dimensions_by_volume"][str(volume)]):
            full_h, _, q0 = build(volume, size, fixture)
            rho = state(full_h, float(fixture["beta"]))
            A = unitary_from_hermitian(q0, 1j * float(fixture["character_amplitude"]) / hbar)
            dual = A @ rho @ A.T.conj()
            B = deriv(full_h, A, hbar)
            C = deriv(full_h, B, hbar)
            radius_rows: list[dict[str, Any]] = []
            for radius in map(float, fixture["radius_values"]):
                _, cut_h, _ = build(volume, size, fixture, radius)
                W = full_h - cut_h
                E = deriv(W, B, hbar)
                comm = spectral_norm(W @ A - A @ W)
                check(f"V={volume} n={size} L={radius} Hermitian", spectral_norm(full_h - full_h.T.conj()) <= hermitian_tol, spectral_norm(full_h - full_h.T.conj()), f"<={hermitian_tol}", "matrix")
                check(f"V={volume} n={size} L={radius} trace", abs(float(np.trace(rho).real) - 1.0) <= 100.0 * state_tol and abs(float(np.trace(dual).real) - 1.0) <= 100.0 * state_tol, [np.trace(rho), np.trace(dual)], "normalized", "state")
                check(f"V={volume} n={size} L={radius} commutation", comm <= commutation_tol, comm, f"<={commutation_tol}", "CCR-core")
                c_norm, e_norm = spectral_norm(C), spectral_norm(E)
                cross_ref, cross_dual = two_leg_norm(rho, E), two_leg_norm(dual, E)
                signs: list[dict[str, Any]] = []
                for sign in map(int, fixture["sign_values"]):
                    K = full_h + sign * W
                    d2 = deriv(K, deriv(K, A, hbar), hbar)
                    residual = spectral_norm(d2 - C - sign * E)
                    d1 = spectral_norm(deriv(K, A, hbar) - B)
                    check(f"V={volume} n={size} L={radius} sign={sign} identity", residual <= 100.0 * commutation_tol, residual, f"<={100.0 * commutation_tol}", "generator")
                    check(f"V={volume} n={size} L={radius} sign={sign} derivative", d1 <= 100.0 * commutation_tol, d1, f"<={100.0 * commutation_tol}", "Duhamel")
                    times: list[dict[str, Any]] = []
                    for time in map(float, fixture["time_values"]):
                        U = unitary_from_hermitian(full_h, -1j * time / hbar)
                        UK = unitary_from_hermitian(K, -1j * time / hbar)
                        D = UK.T.conj() @ A @ UK - U.T.conj() @ A @ U
                        delta_D = deriv(full_h, D, hbar)
                        bound = time**2 * (2.0 * c_norm + e_norm) / 2.0
                        dnorm = spectral_norm(D)
                        ratio = dnorm / max(bound, 1.0e-300)
                        bound_ratios.append(ratio)
                        state_values = [two_leg_norm(rho, D)[0], two_leg_norm(dual, D)[0], two_leg_norm(rho, delta_D)[0], two_leg_norm(dual, delta_D)[0]]
                        check(f"V={volume} n={size} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in [dnorm, spectral_norm(delta_D), *state_values]), "finite", "finite", "Duhamel")
                        check(f"V={volume} n={size} L={radius} t={time} sign={sign} bound", dnorm <= bound + bound_tol, [dnorm, bound], f"D<=bound+{bound_tol}", "operator-bound")
                        times.append({"time": time, "D_operator_norm": dnorm, "delta_D_operator_norm": spectral_norm(delta_D), "operator_bound": bound, "bound_ratio": ratio, "reference_D": two_leg_norm(rho, D), "dual_D": two_leg_norm(dual, D), "reference_delta_D": two_leg_norm(rho, delta_D), "dual_delta_D": two_leg_norm(dual, delta_D)})
                    signs.append({"sign": sign, "generator_identity_residual": residual, "initial_derivative_residual": d1, "times": times})
                tail_ref, tail_dual = two_leg_norm(rho, W), two_leg_norm(dual, W)
                ref_ratio = cross_ref[0] / max(tail_ref[0], 1.0e-300)
                dual_ratio = cross_dual[0] / max(tail_dual[0], 1.0e-300)
                cross_ratios += [ref_ratio, dual_ratio]
                radius_rows.append({"radius": radius, "tail_reference": tail_ref, "tail_dual": tail_dual, "cross_reference": cross_ref, "cross_dual": cross_dual, "cross_operator_norm": e_norm, "double_commutator_operator_norm": c_norm, "cross_to_tail_reference": ref_ratio, "cross_to_tail_dual": dual_ratio, "signs": signs})
            rows.append({"volume": volume, "oscillator_dimension": size, "hilbert_dimension": size**volume, "radii": radius_rows})

    check("coverage", len(rows) == sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) for v in fixture["volume_values"]), len(rows), "declared", "coverage")
    check("bound ratios", max(bound_ratios) <= 1.0 + 1.0e-7, [min(bound_ratios), max(bound_ratios)], "<=1", "operator-bound")
    check("cross ratios", min(cross_ratios) >= 0.0 and all(np.isfinite(value) for value in cross_ratios), [min(cross_ratios), max(cross_ratios)], ">=0", "diagnostic")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-EVOLVED-DUAL-INTEGRAND-CROSS-TERM", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"volume_rows": rows, "finite_cross_term_identity_closed": True, "finite_second_order_operator_bound_closed": True, "finite_reference_cross_term_closed": True, "finite_dual_cross_term_closed": True, "finite_reference_D_closed": True, "finite_dual_D_closed": True, "finite_reference_delta_D_closed": True, "finite_dual_delta_D_closed": True, "finite_small_time_diagnostic_closed": True, "max_operator_bound_ratio": max(bound_ratios), "min_cross_to_tail_ratio": min(cross_ratios), "max_cross_to_tail_ratio": max(cross_ratios), "actual_q3_evolved_dual_integrand_uniform_closed": False, "state_isometry_for_signed_dynamics_closed": False, "actual_q3_unbounded_common_core_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT EVOLVED-DUAL-CROSS-TERM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
