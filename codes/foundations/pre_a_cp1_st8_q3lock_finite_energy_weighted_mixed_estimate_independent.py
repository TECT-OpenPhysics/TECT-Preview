#!/usr/bin/env python3
"""Independent finite-Q3 lane for EXP-001082.

This implementation rebuilds the oscillator, Q3 Hamiltonian, Gibbs state,
coordinate multiplier, spectral weight and corrected two-sided estimate without
importing the primary audit.
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
SLUG = "pre-a-cp1-st8-q3lock-finite-energy-weighted-mixed-estimate"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-primary-{SLUG}/independent.json"
)


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
    annihilation = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def q3_hamiltonian(size: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_one = np.kron(q, identity)
    q_two = np.kron(identity, q)
    p_one = np.kron(p, identity)
    p_two = np.kron(identity, p)
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    onsite = (p_one @ p_one + p_two @ p_two) / (2.0 * chi) + r * (q_one @ q_one + q_two @ q_two) / 2.0 + g * (q_one @ q_one @ q_one @ q_one + q_two @ q_two @ q_two @ q_two) / 4.0
    difference = q_one - q_two
    bond = c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (q_one @ q_one + q_two @ q_two) / 4.0
    return q_one, q_two, p_one, (onsite + bond + (onsite + bond).conj().T) / 2.0


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = values - np.min(values)
    weights = np.exp(-beta * shifted)
    return (vectors * weights) @ vectors.conj().T / np.sum(weights)


def cutoff(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    first = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0))
    second = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi**2 * np.cos(np.pi * (scaled - 1.0)), 0.0))
    cut = values * taper
    derivative = taper + scaled * first
    second_derivative = np.where(np.abs(values) <= np.finfo(float).eps, 0.0, np.sign(values) * (2.0 * first + scaled * second) / radius)
    return cut, derivative, second_derivative


def bond(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference**2 / 2.0 + lam * difference**2 * (q_value**2 + v_value**2) / 4.0


def force(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference + lam * difference * (2.0 * q_value**2 - q_value * v_value + v_value**2) / 2.0


def force_prime(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c + lam * (q_value**2 + v_value**2 + difference**2 + 4.0 * q_value * difference) / 2.0


def coordinate_matrix(values: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    joint = np.kron(vectors, vectors)
    return joint @ np.diag(values.reshape(-1)) @ joint.conj().T


def power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-12:
        raise ValueError("nonpositive spectral input")
    values = np.maximum(values, 0.0)
    if exponent < 0.0 and float(np.min(values)) <= 0.0:
        raise ValueError("negative spectral power requires strict positivity")
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def op_norm(matrix: np.ndarray) -> float:
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
    check("finite parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["hbar"] > 0 and fixture["g"] > 0, fixture, "positive finite parameters", "model")
    check("scope firewall", scope["finite_corrected_energy_weighted_bound_closed"] and not scope["finite_ideal_energy_weighted_bound_closed"] and not scope["weighted_cutoff_uniformity_proved"], scope, "finite corrected bound only", "scope")

    tolerance = float(fixture["bound_tolerance"])
    factor_tolerance = float(fixture["factorization_tolerance"])
    hbar = float(fixture["hbar"])
    beta = float(fixture["beta"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    all_rows: list[dict[str, Any]] = []
    fixed_u: list[float] = []
    fixed_v: list[float] = []
    fixed_r: list[float] = []
    fixed_unweighted: list[float] = []

    for n_value in fixture["n_values"]:
        n = int(n_value)
        q_one, q_two, p_one, hamiltonian = q3_hamiltonian(n, fixture)
        rho = gibbs(hamiltonian, beta)
        rho_sqrt = power(rho, 0.5)
        q_single, _ = oscillator(n)
        values, vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
        h_values, _ = np.linalg.eigh(hamiltonian)
        weight = hamiltonian - float(np.min(h_values)) * np.eye(n * n, dtype=complex) + np.eye(n * n, dtype=complex)
        weight_34 = power(weight, 0.75)
        weight_minus34 = power(weight, -0.75)
        k_plus = hs_norm(weight_34 @ p_one @ rho_sqrt)
        k_zero = hs_norm(weight_34 @ rho_sqrt)
        radius_rows: list[dict[str, Any]] = []
        for radius_value in fixture["radius_values"]:
            radius = float(radius_value)
            q_values, v_values = np.meshgrid(values, values, indexing="ij")
            q_cut, q_prime, _ = cutoff(q_values, radius)
            v_cut, _, _ = cutoff(v_values, radius)
            tail = bond(q_values, v_values, c, lam) - bond(q_cut, v_cut, c, lam)
            force_value = force(q_values, v_values, c, lam)
            force_prime_value = force_prime(q_values, v_values, c, lam)
            cut_force = force(q_cut, v_cut, c, lam)
            tail_prime = force_value - cut_force * q_prime
            mixed = tail * force_value
            mixed_prime = tail_prime * force_value + tail * force_prime_value
            multiplier = coordinate_matrix(mixed, vectors)
            coordinate_derivative = coordinate_matrix(mixed_prime, vectors)
            residual = p_one @ multiplier - multiplier @ p_one + 1j * hbar * coordinate_derivative
            comm_derivative = (1j / hbar) * (p_one @ multiplier - multiplier @ p_one)
            right_leg = hs_norm(multiplier @ p_one @ rho_sqrt)
            left_leg = hs_norm(p_one @ multiplier @ rho_sqrt)
            actual_root = float(np.sqrt(max(0.0, right_leg**2 + left_leg**2)))
            u_energy = op_norm(multiplier @ weight_minus34)
            v_coordinate = op_norm(coordinate_derivative @ weight_minus34)
            residual_energy = op_norm(residual @ weight_minus34)
            v_comm = op_norm(comm_derivative @ weight_minus34)
            right_bound = u_energy * k_plus
            corrected_left = right_bound + hbar * v_coordinate * k_zero + residual_energy * k_zero
            corrected_root = float(np.sqrt(max(0.0, right_bound**2 + corrected_left**2)))
            comm_left = right_bound + hbar * v_comm * k_zero
            comm_root = float(np.sqrt(max(0.0, right_bound**2 + comm_left**2)))
            check(f"n={n} L={radius} right factor", hs_norm(multiplier @ p_one - (multiplier @ weight_minus34) @ (weight_34 @ p_one)) < factor_tolerance, "finite", f"<{factor_tolerance}", "factorization")
            check(f"n={n} L={radius} corrected estimate", actual_root**2 <= corrected_root**2 + tolerance * (1.0 + corrected_root**2), [actual_root, corrected_root], "actual<=corrected", "weighted bound")
            check(f"n={n} L={radius} commutator estimate", left_leg <= comm_left + tolerance * (1.0 + comm_left), [left_leg, comm_left], "left<=commutator", "ideal derivative")
            check(f"n={n} L={radius} finite", all(np.isfinite(value) for value in (u_energy, v_coordinate, residual_energy, v_comm, actual_root)), "finite", "finite", "diagnostic")
            radius_rows.append({"radius": radius, "actual_root": actual_root, "right_leg": right_leg, "left_leg": left_leg, "u_energy": u_energy, "v_coordinate": v_coordinate, "v_commutator": v_comm, "residual_energy": residual_energy, "k_plus": k_plus, "k_zero": k_zero, "corrected_bound_root": corrected_root, "commutator_bound_root": comm_root})
            if abs(radius - float(fixture["scaling_radius"])) <= tolerance:
                fixed_u.append(u_energy)
                fixed_v.append(v_coordinate)
                fixed_r.append(residual_energy)
                fixed_unweighted.append(float(np.max(np.abs(mixed))))
        all_rows.append({"n": n, "dimension": n * n, "k_plus": k_plus, "k_zero": k_zero, "radii": radius_rows})

    check("weighted improvement", fixed_u[0] < fixed_unweighted[0], [fixed_u[0], fixed_unweighted[0]], "u_E<u", "diagnostic")
    check("weighted growth boundary", fixed_u[-1] > fixed_u[0] and fixed_v[-1] > fixed_v[0], [fixed_u, fixed_v], "last>first", "uniformity")
    check("residual nonnegative", all(value >= 0.0 for value in fixed_r), fixed_r, ">=0", "finite CCR")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ENERGY-WEIGHTED-MIXED-ESTIMATE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"dimension_rows": all_rows, "fixed_radius_energy_multiplier_norms": fixed_u, "fixed_radius_coordinate_derivative_norms": fixed_v, "fixed_radius_ccr_residual_norms": fixed_r, "fixed_radius_unweighted_multiplier_norms": fixed_unweighted, "finite_corrected_energy_weighted_bound_closed": True, "finite_ideal_energy_weighted_bound_closed": False, "weighted_cutoff_uniformity_proved": False, "exact_ccr_domain_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False},
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
    print(f"INDEPENDENT FINITE-ENERGY-WEIGHTED-MIXED PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
