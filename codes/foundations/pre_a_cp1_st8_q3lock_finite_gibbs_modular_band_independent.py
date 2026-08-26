#!/usr/bin/env python3
"""Independent finite-Q3 reconstruction for EXP-001186.

No primary audit is imported.  The oscillator tensors, Q3 Hamiltonians,
cutoff bonds, Gibbs powers, spectral representation and finite history rows
are rebuilt here to cross-check the modular-band identity.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-gibbs-modular-band"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((n, n), dtype=complex)
    for i in range(n - 1):
        a[i, i + 1] = np.sqrt(i + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    values = {2: [(0, 1)], 4: [(0, 1), (0, 2), (1, 3), (2, 3)], 6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]}
    return values[volume]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if i == site else identity for i in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(u, v): bond(q_ops[u], q_ops[v], fixture) for u, v in edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return q_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, bonds


def cut(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    eta = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * eta)) @ vectors.conj().T


def cut_bonds(volume: int, n: int, fixture: dict[str, Any], bond_q: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    identity = np.eye(n, dtype=complex)
    bond_ops = [embed(bond_q, site, volume, identity) for site in range(volume)]
    return {(u, v): bond(bond_ops[u], bond_ops[v], fixture) for u, v in edges(volume)}


def gibbs(hamiltonian: np.ndarray, beta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = energies - float(np.min(energies))
    probabilities = np.exp(-beta * shifted)
    probabilities /= float(np.sum(probabilities))
    rho = (vectors * probabilities) @ vectors.conj().T
    return rho, energies, vectors, probabilities


def power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("matrix is not positive")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def positive_weight(base: np.ndarray) -> np.ndarray:
    hermitian = (base + base.conj().T) / 2.0
    minimum = float(np.min(np.linalg.eigvalsh(hermitian)))
    return hermitian - minimum * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex)


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def opnorm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def constants(delta: np.ndarray, weight: np.ndarray, rho: np.ndarray) -> dict[str, float]:
    k_half, k_inv = power(weight, 0.5), power(weight, -0.5)
    rho_half, rho_inv = power(rho, 0.5), power(rho, -0.5)
    adjoint = delta.conj().T
    return {"rho_left": opnorm(rho_inv @ delta @ rho_half), "rho_right": opnorm(rho_half @ delta @ rho_inv), "k_left": opnorm(k_half @ delta @ k_inv), "k_right": opnorm(k_inv @ delta @ k_half), "rho_left_star": opnorm(rho_inv @ adjoint @ rho_half), "rho_right_star": opnorm(rho_half @ adjoint @ rho_inv), "k_left_star": opnorm(k_half @ adjoint @ k_inv), "k_right_star": opnorm(k_inv @ adjoint @ k_half)}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    scenarios = fixture["scenarios"]
    betas = [float(x) for x in fixture["beta_values"]]
    radii = [float(x) for x in fixture["radius_values"]]
    times = [float(x) for x in fixture["time_values"]]
    interpolation = [float(x) for x in fixture["interpolation_values"]]
    orientations = [int(x) for x in fixture["orientation_values"]]
    amplitude, hbar = float(fixture["character_amplitude"]), float(fixture["hbar"])
    tolerance, identity_tolerance, floor = float(fixture["finite_tolerance"]), float(fixture["spectral_identity_tolerance"]), float(fixture["positivity_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001186" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001186/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_gibbs_modular_band_identity_closed"] and scope["finite_similarity_band_envelope_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["pre_a_closed"], scope, "finite spectral interface", "scope")
    check("scenario geometry", [int(x["volume"]) for x in scenarios] == [2, 4, 6] and [int(x["oscillator_dimension"]) for x in scenarios] == [3, 3, 2], scenarios, "2/4 at n=3 and 6 at n=2", "geometry")
    q_cache: dict[int, np.ndarray] = {}
    coefficient_rows: list[dict[str, Any]] = []
    history_rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        volume, n = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_single = q_cache.setdefault(n, oscillator(n)[0])
        q_ops, hamiltonian, local_hamiltonian, bonds = build(volume, n, fixture)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        for beta in betas:
            rho, energies, vectors, probabilities = gibbs(hamiltonian, beta)
            p_min, p_max = float(np.min(probabilities)), float(np.max(probabilities))
            check(f"V={volume} n={n} beta={beta} Gibbs rank", p_min >= floor and p_max > 0.0, [p_min, p_max], f">={floor}", "Gibbs")
            rho_half, rho_inv = power(rho, 0.5), power(rho, -0.5)
            shifted = energies - float(np.min(energies))
            bandwidth = float(np.max(shifted) - np.min(shifted))
            band = math.exp(beta * bandwidth / 2.0)
            for radius in radii:
                q_cut = cut(q_single, radius)
                cut_map = cut_bonds(volume, n, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_map[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                delta_norm = opnorm(tail)
                tail_hat = vectors.conj().T @ tail @ vectors
                diag_hi = np.diag(np.sqrt(probabilities))
                diag_lo = np.diag(1.0 / np.sqrt(probabilities))
                spectral_left = vectors @ (diag_lo @ tail_hat @ diag_hi) @ vectors.conj().T
                spectral_right = vectors @ (diag_hi @ tail_hat @ diag_lo) @ vectors.conj().T
                direct_left, direct_right = rho_inv @ tail @ rho_half, rho_half @ tail @ rho_inv
                residual = max(opnorm(direct_left - spectral_left), opnorm(direct_right - spectral_right))
                check(f"V={volume} n={n} beta={beta} L={radius} spectral identity", residual <= identity_tolerance, residual, f"<={identity_tolerance}", "spectral identity")
                check(f"V={volume} n={n} beta={beta} L={radius} Gibbs band", opnorm(direct_left) <= band * delta_norm + tolerance * (1.0 + band * delta_norm) and opnorm(direct_right) <= band * delta_norm + tolerance * (1.0 + band * delta_norm), [opnorm(direct_left), opnorm(direct_right), band * delta_norm], "both<=band*Delta", "Gibbs envelope")
                for kind, base_weight in (("local", local_hamiltonian), ("full", hamiltonian)):
                    weight = positive_weight(base_weight)
                    k_values = np.linalg.eigvalsh(weight)
                    k_band = math.sqrt(float(np.max(k_values)) / float(np.min(k_values)))
                    similarity = constants(tail, weight, rho)
                    check(f"V={volume} n={n} beta={beta} L={radius} {kind} constants finite", all(np.isfinite(v) and v >= 0.0 for v in similarity.values()), similarity, "finite nonnegative", "similarity")
                    check(f"V={volume} n={n} beta={beta} L={radius} {kind} K band", similarity["k_left"] <= k_band * delta_norm + tolerance * (1.0 + k_band * delta_norm) and similarity["k_right"] <= k_band * delta_norm + tolerance * (1.0 + k_band * delta_norm), [similarity["k_left"], similarity["k_right"], k_band * delta_norm], "both<=band*Delta", "energy envelope")
                    coefficient_rows.append({"volume": volume, "oscillator_dimension": n, "beta": beta, "radius": radius, "kind": kind, "energy_min": float(np.min(energies)), "energy_max": float(np.max(energies)), "energy_band": bandwidth, "gibbs_band": band, "tail_operator_norm": delta_norm, "gibbs_left": opnorm(direct_left), "gibbs_right": opnorm(direct_right), "k_band": k_band, "constants": similarity, "spectral_identity_residual": residual})
                    for orientation in orientations:
                        delta = orientation * tail
                        for s_value in interpolation:
                            for time in times:
                                propagator = unitary(hamiltonian + orientation * s_value * tail, time, hbar)
                                history = propagator @ observable @ propagator.conj().T
                                actual = opnorm(rho_inv @ (delta @ history - history @ delta) @ rho_half)
                                base = opnorm(rho_inv @ history @ rho_half)
                                envelope = band * delta_norm * base
                                check(f"V={volume} n={n} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} history envelope", actual <= envelope + tolerance * (1.0 + envelope), [actual, envelope], "actual<=band*Delta*base", "history")
                                history_rows.append({"volume": volume, "oscillator_dimension": n, "beta": beta, "radius": radius, "kind": kind, "orientation": orientation, "interpolation": s_value, "time": time, "actual": actual, "base": base, "envelope": envelope, "ratio": actual / max(envelope, np.finfo(float).tiny), "history_hat_norm": opnorm(vectors.conj().T @ history @ vectors)})
    expected_coefficients = len(scenarios) * len(betas) * len(radii) * 2
    expected_history = expected_coefficients * len(orientations) * len(interpolation) * len(times)
    check("coefficient coverage", len(coefficient_rows) == expected_coefficients, len(coefficient_rows), expected_coefficients, "coverage")
    check("history coverage", len(history_rows) == expected_history, len(history_rows), expected_history, "coverage")
    ratios = [float(row["ratio"]) for row in history_rows]
    bands = [float(row["gibbs_band"]) for row in coefficient_rows]
    check("finite diagnostics", all(np.isfinite(value) and value >= 0.0 for value in ratios + bands), [min(ratios), max(ratios), min(bands), max(bands)], "finite nonnegative", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GIBBS-MODULAR-BAND", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks[:64] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}], "coefficient_rows": coefficient_rows, "history_rows": history_rows, "derived": {"coefficient_row_count": len(coefficient_rows), "history_row_count": len(history_rows), "min_history_ratio": min(ratios), "max_history_ratio": max(ratios), "min_gibbs_band": min(bands), "max_gibbs_band": max(bands), "finite_gibbs_modular_band_identity_closed": True, "finite_similarity_band_envelope_closed": True, "source_volume_cutoff_beta_uniform_closed": False, "modular_domain_transfer_closed": False, "unbounded_common_core_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_os_hilbert_carrier_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "scope": scope, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-GIBBS-MODULAR-BAND PASS {payload['passed']}/{payload['assertion_count']} coefficients={payload['derived']['coefficient_row_count']} histories={payload['derived']['history_row_count']} max_band={payload['derived']['max_gibbs_band']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
