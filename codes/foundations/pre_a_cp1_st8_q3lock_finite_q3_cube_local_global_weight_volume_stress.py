#!/usr/bin/env python3
"""Primary finite Q3-cube local/full energy-weight stress test (EXP-001083)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-q3-cube-local-global-weight-volume-stress"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_structured_cutoff_orbit_modular_derivative as q3  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def cube_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    vertices = list(product((0, 1), repeat=3))
    return [(left, right) for left in range(8) for right in range(left + 1, 8) if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1]


def embedded(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def build_volume(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, np.ndarray, tuple[np.ndarray, np.ndarray]]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embedded(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embedded(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite_terms = [p_ops[site] @ p_ops[site] / (2.0 * chi) + r * (q_ops[site] @ q_ops[site]) / 2.0 + g * (q_ops[site] @ q_ops[site] @ q_ops[site] @ q_ops[site]) / 4.0 for site in range(volume)]
    bond_terms: dict[tuple[int, int], np.ndarray] = {}
    for left, right in cube_edges(volume):
        difference = q_ops[left] - q_ops[right]
        bond_terms[(left, right)] = c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0
    full = sum(onsite_terms, np.zeros_like(q_ops[0])) + sum(bond_terms.values(), np.zeros_like(q_ops[0]))
    local = onsite_terms[0] + onsite_terms[1] + bond_terms[(0, 1)]
    return q_ops, p_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, (q_single, p_single)


def cutoff_data(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    eta = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    eta_prime = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0))
    return values * eta, eta + scaled * eta_prime


def bond_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference**2 / 2.0 + lam * difference**2 * (q_value**2 + v_value**2) / 4.0


def force_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference + lam * difference * (2.0 * q_value**2 - q_value * v_value + v_value**2) / 2.0


def force_prime_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c + lam * (q_value**2 + v_value**2 + difference**2 + 4.0 * q_value * difference) / 2.0


def coordinate_matrix(values: np.ndarray, vectors: np.ndarray, volume: int) -> np.ndarray:
    joint = vectors
    for _ in range(volume - 1):
        joint = np.kron(joint, vectors)
    return joint @ np.diag(values.reshape(-1)) @ joint.conj().T


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-10:
        raise ValueError(f"nonpositive weight spectrum: {float(np.min(values))}")
    values = np.maximum(values, 0.0)
    if exponent < 0.0 and float(np.min(values)) <= 0.0:
        raise ValueError("negative power requires strict positivity")
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def hs_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001083" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001083/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("Q3 cube geometry", len(cube_edges(8)) == 12 and cube_edges(2) == [(0, 1)], [len(cube_edges(8)), cube_edges(2)], "12 edges and target edge", "geometry")
    check("scope firewall", scope["finite_q3_cube_matrix_model_closed"] and scope["finite_support_local_weight_defined"] and scope["finite_full_volume_weight_defined"] and not scope["volume_uniform_local_weight_proved"], scope, "finite local/full comparison only", "scope")

    tol = float(fixture["bound_tolerance"])
    factor_tol = float(fixture["factorization_tolerance"])
    c, lam, hbar, beta = float(fixture["c"]), float(fixture["lambda"]), float(fixture["hbar"]), float(fixture["beta"])
    volume_rows: list[dict[str, Any]] = []
    for volume_value in fixture["volume_values"]:
        volume = int(volume_value); n = int(fixture["oscillator_dimension"])
        q_ops, p_ops, full_h, local_h, (q_single, _) = build_volume(volume, n, fixture)
        rho = q3.gibbs_state(full_h, beta)
        rho_sqrt = spectral_power(rho, 0.5)
        q_values_single, q_vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
        q_values, v_values = np.meshgrid(q_values_single, q_values_single, indexing="ij")
        q_cut, q_prime = cutoff_data(q_values, float(fixture["radius"]))
        v_cut, _ = cutoff_data(v_values, float(fixture["radius"]))
        tail = bond_scalar(q_values, v_values, c, lam) - bond_scalar(q_cut, v_cut, c, lam)
        force = force_scalar(q_values, v_values, c, lam)
        force_prime = force_prime_scalar(q_values, v_values, c, lam)
        cut_force = force_scalar(q_cut, v_cut, c, lam)
        tail_prime = force - cut_force * q_prime
        mixed = tail * force
        mixed_prime = tail_prime * force + tail * force_prime
        values_shape = (n, n) + (1,) * (volume - 2)
        mixed_values = np.broadcast_to(mixed.reshape(values_shape), (n,) * volume)
        mixed_prime_values = np.broadcast_to(mixed_prime.reshape(values_shape), (n,) * volume)
        multiplier = coordinate_matrix(mixed_values, q_vectors, volume)
        coordinate_derivative = coordinate_matrix(mixed_prime_values, q_vectors, volume)
        p0 = p_ops[0]
        residual = p0 @ multiplier - multiplier @ p0 + 1j * hbar * coordinate_derivative
        right_leg = hs_norm(multiplier @ p0 @ rho_sqrt)
        left_leg = hs_norm(p0 @ multiplier @ rho_sqrt)
        actual_root = float(np.sqrt(max(0.0, right_leg**2 + left_leg**2)))
        weight_rows: dict[str, Any] = {}
        for kind, base in (("local", local_h), ("full", full_h)):
            eigenvalues = np.linalg.eigvalsh(base)
            weight = base - float(np.min(eigenvalues)) * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex)
            weight_34, weight_minus34 = spectral_power(weight, 0.75), spectral_power(weight, -0.75)
            k_plus, k_zero = hs_norm(weight_34 @ p0 @ rho_sqrt), hs_norm(weight_34 @ rho_sqrt)
            u_energy, v_energy, residual_energy = operator_norm(multiplier @ weight_minus34), operator_norm(coordinate_derivative @ weight_minus34), operator_norm(residual @ weight_minus34)
            right_bound = u_energy * k_plus
            left_bound = right_bound + hbar * v_energy * k_zero + residual_energy * k_zero
            corrected_root = float(np.sqrt(max(0.0, right_bound**2 + left_bound**2)))
            check(f"V={volume} {kind} weight positive", float(np.min(np.linalg.eigvalsh(weight))) >= 1.0 - float(fixture["positive_tolerance"]), float(np.min(np.linalg.eigvalsh(weight))), ">=1", "weight")
            check(f"V={volume} {kind} right factor", hs_norm(multiplier @ p0 - (multiplier @ weight_minus34) @ (weight_34 @ p0)) < factor_tol, "finite", f"<{factor_tol}", "factorization")
            check(f"V={volume} {kind} corrected bound", actual_root**2 <= right_bound**2 + left_bound**2 + tol * (1.0 + corrected_root**2), [actual_root, corrected_root], "actual<=corrected", "weighted bound")
            check(f"V={volume} {kind} data finite", all(np.isfinite(value) for value in (u_energy, v_energy, residual_energy, k_plus, k_zero, corrected_root)), "finite", "finite", "diagnostic")
            weight_rows[kind] = {"u_energy": u_energy, "v_energy": v_energy, "residual_energy": residual_energy, "k_plus": k_plus, "k_zero": k_zero, "corrected_bound_root": corrected_root}
        volume_rows.append({"volume": volume, "dimension": n**volume, "actual_root": actual_root, "right_leg": right_leg, "left_leg": left_leg, "weights": weight_rows})

    check("both support and full weights present", all(set(item["weights"]) == {"local", "full"} for item in volume_rows), volume_rows, "local/full", "scope")
    check("volume rows finite", len(volume_rows) == len(fixture["volume_values"]), len(volume_rows), len(fixture["volume_values"]), "volume")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-CUBE-LOCAL-GLOBAL-WEIGHT-VOLUME-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_support_local_weight_defined": True, "finite_full_volume_weight_defined": True, "finite_corrected_two_sided_bound_closed": True, "local_full_weight_equivalence_proved": False, "volume_uniform_local_weight_proved": False, "cutoff_uniformity_proved": False, "exact_ccr_domain_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "all_bond_graph_lipschitz_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(); payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-Q3-CUBE-LOCAL-GLOBAL-WEIGHT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
