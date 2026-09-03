#!/usr/bin/env python3
"""Primary finite-Q3 energy-weighted mixed force--momentum audit (EXP-001082).

The finite matrix calculation factors the right Gibbs leg through the positive
weight A = I + H - min(spec(H)) I.  The truncated oscillator does not satisfy
the exact CCR, so the coordinate-derivative route carries an explicit residual
R = p M - M p + i*hbar*Mdot.  This residual is included in the corrected bound;
the residual-free commutator derivative is checked separately as the ideal
modular-domain target.  No thermodynamic uniformity is inferred.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-energy-weighted-mixed-estimate"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-primary-{SLUG}/primary.json"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_structured_cutoff_orbit_modular_derivative as q3  # noqa: E402


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


def cutoff_data(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    eta = np.where(
        scaled <= 1.0,
        1.0,
        np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0),
    )
    eta_prime = np.where(
        scaled <= 1.0,
        0.0,
        np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0),
    )
    eta_second = np.where(
        scaled <= 1.0,
        0.0,
        np.where(scaled < 2.0, -0.5 * np.pi**2 * np.cos(np.pi * (scaled - 1.0)), 0.0),
    )
    q_cut = values * eta
    q_prime = eta + scaled * eta_prime
    q_second = np.where(
        np.abs(values) <= np.finfo(float).eps,
        0.0,
        np.sign(values) * (2.0 * eta_prime + scaled * eta_second) / radius,
    )
    return q_cut, q_prime, q_second


def bond_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference**2 / 2.0 + lam * difference**2 * (q_value**2 + v_value**2) / 4.0


def force_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference + lam * difference * (2.0 * q_value**2 - q_value * v_value + v_value**2) / 2.0


def force_prime_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c + lam * (q_value**2 + v_value**2 + difference**2 + 4.0 * q_value * difference) / 2.0


def matrix_from_coordinate_values(values: np.ndarray, eigenvectors: np.ndarray) -> np.ndarray:
    joint_vectors = np.kron(eigenvectors, eigenvectors)
    return joint_vectors @ np.diag(values.reshape(-1)) @ joint_vectors.conj().T


def spectral_power(matrix: np.ndarray, power: float) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if float(np.min(values)) < -1.0e-12:
        raise ValueError(f"spectral power requires positivity, min={float(np.min(values))}")
    values = np.maximum(values, 0.0)
    if power < 0.0 and float(np.min(values)) <= 0.0:
        raise ValueError("negative spectral power requires strict positivity")
    return (vectors * np.power(values, power)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def hs_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001082" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001082/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive finite parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["hbar"] > 0 and fixture["g"] > 0 and fixture["c"] >= 0 and fixture["lambda"] >= 0, fixture, "positive finite parameters", "model")
    check("scope firewall", scope["finite_corrected_energy_weighted_bound_closed"] and scope["finite_ccr_residual_measured"] and not scope["finite_ideal_energy_weighted_bound_closed"] and not scope["weighted_cutoff_uniformity_proved"], scope, "corrected finite bound with ideal/uniform gates open", "scope")

    tolerance = float(fixture["bound_tolerance"])
    factor_tolerance = float(fixture["factorization_tolerance"])
    positive_tolerance = float(fixture["positive_tolerance"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    hbar = float(fixture["hbar"])
    beta = float(fixture["beta"])
    dimension_rows: list[dict[str, Any]] = []
    fixed_u: list[float] = []
    fixed_v: list[float] = []
    fixed_r: list[float] = []
    fixed_unweighted_u: list[float] = []

    for n_value in fixture["n_values"]:
        n = int(n_value)
        matrices = q3.q3_matrices(n, fixture)
        q_matrix, _ = q3.oscillator(n)
        eigenvalues, eigenvectors = np.linalg.eigh((q_matrix + q_matrix.conj().T) / 2.0)
        full_h = (matrices["onsite"] + matrices["bond"] + (matrices["onsite"] + matrices["bond"]).conj().T) / 2.0
        rho = q3.gibbs_state(full_h, beta)
        rho_sqrt = spectral_power(rho, 0.5)
        h_values, h_vectors = np.linalg.eigh(full_h)
        shifted = full_h - float(np.min(h_values)) * np.eye(full_h.shape[0], dtype=complex)
        weight = shifted + np.eye(full_h.shape[0], dtype=complex)
        weight_values = np.linalg.eigvalsh(weight)
        check(f"n={n} weight positive", float(np.min(weight_values)) >= 1.0 - positive_tolerance, float(np.min(weight_values)), ">=1", "weight")
        weight_34 = spectral_power(weight, 0.75)
        weight_minus34 = spectral_power(weight, -0.75)
        p1 = matrices["p1"]
        k_plus = hs_norm(weight_34 @ p1 @ rho_sqrt)
        k_zero = hs_norm(weight_34 @ rho_sqrt)
        check(f"n={n} weighted state constants finite", np.isfinite(k_plus) and np.isfinite(k_zero), [k_plus, k_zero], "finite", "weighted state")
        radius_rows: list[dict[str, Any]] = []

        for radius in fixture["radius_values"]:
            radius_float = float(radius)
            q_values, v_values = np.meshgrid(eigenvalues, eigenvalues, indexing="ij")
            q_cut, q_prime, q_second = cutoff_data(q_values, radius_float)
            v_cut, _, _ = cutoff_data(v_values, radius_float)
            bond = bond_scalar(q_values, v_values, c, lam)
            cut_bond = bond_scalar(q_cut, v_cut, c, lam)
            tail = bond - cut_bond
            force = force_scalar(q_values, v_values, c, lam)
            force_prime = force_prime_scalar(q_values, v_values, c, lam)
            cut_force = force_scalar(q_cut, v_cut, c, lam)
            tail_prime = force - cut_force * q_prime
            mixed = tail * force
            mixed_prime = tail_prime * force + tail * force_prime
            _ = q_second

            multiplier = matrix_from_coordinate_values(mixed, eigenvectors)
            coordinate_derivative = matrix_from_coordinate_values(mixed_prime, eigenvectors)
            residual_matrix = p1 @ multiplier - multiplier @ p1 + 1j * hbar * coordinate_derivative
            commutator_derivative = (1j / hbar) * (p1 @ multiplier - multiplier @ p1)
            right_leg = hs_norm(multiplier @ p1 @ rho_sqrt)
            left_leg = hs_norm(p1 @ multiplier @ rho_sqrt)
            actual_root = float(np.sqrt(max(0.0, right_leg**2 + left_leg**2)))
            u_energy = operator_norm(multiplier @ weight_minus34)
            v_coordinate = operator_norm(coordinate_derivative @ weight_minus34)
            residual_energy = operator_norm(residual_matrix @ weight_minus34)
            v_commutator = operator_norm(commutator_derivative @ weight_minus34)
            right_bound = u_energy * k_plus
            corrected_left_bound = right_bound + hbar * v_coordinate * k_zero + residual_energy * k_zero
            corrected_bound_squared = right_bound**2 + corrected_left_bound**2
            corrected_bound_root = float(np.sqrt(max(0.0, corrected_bound_squared)))
            ideal_left_bound = right_bound + hbar * v_coordinate * k_zero
            ideal_bound_squared = right_bound**2 + ideal_left_bound**2
            commutator_left_bound = right_bound + hbar * v_commutator * k_zero
            commutator_bound_squared = right_bound**2 + commutator_left_bound**2
            commutator_bound_root = float(np.sqrt(max(0.0, commutator_bound_squared)))

            factor_right = multiplier @ p1 - (multiplier @ weight_minus34) @ (weight_34 @ p1)
            factor_left = p1 @ multiplier - multiplier @ p1 + 1j * hbar * coordinate_derivative - residual_matrix
            check(f"n={n} L={radius_float} right factorization", hs_norm(factor_right) < factor_tolerance, hs_norm(factor_right), f"<{factor_tolerance}", "energy factorization")
            check(f"n={n} L={radius_float} left residual identity", hs_norm(factor_left) < factor_tolerance, hs_norm(factor_left), f"<{factor_tolerance}", "finite CCR")
            check(f"n={n} L={radius_float} right weighted leg", right_leg <= right_bound + tolerance * (1.0 + right_bound), [right_leg, right_bound], "right<=u_E*K_+", "weighted bound")
            check(f"n={n} L={radius_float} left corrected leg", left_leg <= corrected_left_bound + tolerance * (1.0 + corrected_left_bound), [left_leg, corrected_left_bound], "left<=corrected bound", "weighted bound")
            check(f"n={n} L={radius_float} corrected bound", actual_root**2 <= corrected_bound_squared + tolerance * (1.0 + corrected_bound_squared), [actual_root, corrected_bound_root], "actual<=corrected bound", "weighted bound")
            check(f"n={n} L={radius_float} commutator bound", left_leg <= commutator_left_bound + tolerance * (1.0 + commutator_left_bound), [left_leg, commutator_left_bound], "left<=commutator bound", "ideal derivative")
            check(f"n={n} L={radius_float} finite weighted data", all(np.isfinite(value) for value in (u_energy, v_coordinate, residual_energy, v_commutator, actual_root, corrected_bound_root)), [u_energy, v_coordinate, residual_energy, v_commutator], "finite", "diagnostic")
            radius_rows.append({
                "radius": radius_float,
                "actual_root": actual_root,
                "right_leg": right_leg,
                "left_leg": left_leg,
                "u_energy": u_energy,
                "v_coordinate": v_coordinate,
                "v_commutator": v_commutator,
                "residual_energy": residual_energy,
                "k_plus": k_plus,
                "k_zero": k_zero,
                "corrected_bound_root": corrected_bound_root,
                "ideal_bound_root": float(np.sqrt(max(0.0, ideal_bound_squared))),
                "commutator_bound_root": commutator_bound_root,
                "ideal_bound_margin": float(np.sqrt(max(0.0, ideal_bound_squared)) - actual_root),
                "corrected_bound_margin": corrected_bound_root - actual_root,
                "residual_to_coordinate_ratio": residual_energy / max(v_coordinate, positive_tolerance),
            })
            if abs(radius_float - float(fixture["scaling_radius"])) <= tolerance:
                fixed_u.append(u_energy)
                fixed_v.append(v_coordinate)
                fixed_r.append(residual_energy)
                fixed_unweighted_u.append(float(np.max(np.abs(mixed))))
        dimension_rows.append({"n": n, "dimension": n * n, "k_plus": k_plus, "k_zero": k_zero, "radii": radius_rows})

    check("weighted constants improve the first finite row", fixed_u[0] < fixed_unweighted_u[0], [fixed_u[0], fixed_unweighted_u[0]], "u_E<u", "weighted diagnostic")
    check("global weighted growth remains visible", fixed_u[-1] > fixed_u[0] and fixed_v[-1] > fixed_v[0], [fixed_u, fixed_v], "last>first", "uniformity boundary")
    check("residual is retained", all(value >= 0.0 for value in fixed_r), fixed_r, ">=0", "finite CCR")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-WEIGHTED-MIXED-ESTIMATE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "dimension_rows": dimension_rows,
            "fixed_radius_energy_multiplier_norms": fixed_u,
            "fixed_radius_coordinate_derivative_norms": fixed_v,
            "fixed_radius_ccr_residual_norms": fixed_r,
            "fixed_radius_unweighted_multiplier_norms": fixed_unweighted_u,
            "finite_corrected_energy_weighted_bound_closed": True,
            "finite_ideal_energy_weighted_bound_closed": False,
            "weighted_cutoff_uniformity_proved": False,
            "exact_ccr_domain_closed": False,
            "modular_domain_transfer_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-ENERGY-WEIGHTED-MIXED PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
