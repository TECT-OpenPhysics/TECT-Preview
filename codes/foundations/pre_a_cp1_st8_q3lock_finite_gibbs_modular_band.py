#!/usr/bin/env python3
"""Primary finite-Q3 Gibbs modular-band identity and similarity stress (EXP-001186).

For a finite Gibbs matrix rho_beta proportional to exp(-beta H), the
similarity factor rho_beta^(-1/2) Delta rho_beta^(1/2) is evaluated both
directly and in the H eigenbasis.  The finite operator-norm envelope obtained
from the spectral energy band is checked, together with the analogous local
and full shifted-energy factors.  This is a route-local finite diagnostic;
it is not a uniform common-core statement.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-gibbs-modular-band"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
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


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def opnorm(matrix: np.ndarray) -> float:
    return q3.operator_norm(matrix)


def powers(matrix: np.ndarray, exponent: float) -> np.ndarray:
    return q3.spectral_power(matrix, exponent)


def similarity_constants(delta: np.ndarray, weight: np.ndarray, rho: np.ndarray) -> dict[str, float]:
    k_half, k_inverse_half = powers(weight, 0.5), powers(weight, -0.5)
    rho_half, rho_inverse_half = powers(rho, 0.5), powers(rho, -0.5)
    delta_star = delta.conj().T
    return {
        "rho_left": opnorm(rho_inverse_half @ delta @ rho_half),
        "rho_right": opnorm(rho_half @ delta @ rho_inverse_half),
        "k_left": opnorm(k_half @ delta @ k_inverse_half),
        "k_right": opnorm(k_inverse_half @ delta @ k_half),
        "rho_left_star": opnorm(rho_inverse_half @ delta_star @ rho_half),
        "rho_right_star": opnorm(rho_half @ delta_star @ rho_inverse_half),
        "k_left_star": opnorm(k_half @ delta_star @ k_inverse_half),
        "k_right_star": opnorm(k_inverse_half @ delta_star @ k_half),
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    scenarios = fixture["scenarios"]
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    interpolation = [float(value) for value in fixture["interpolation_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    amplitude, hbar = float(fixture["character_amplitude"]), float(fixture["hbar"])
    tolerance, identity_tolerance, positivity_floor = float(fixture["finite_tolerance"]), float(fixture["spectral_identity_tolerance"]), float(fixture["positivity_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001186" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001186/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_gibbs_modular_band_identity_closed"] and scope["finite_similarity_band_envelope_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["pre_a_closed"], scope, "finite spectral interface", "scope")
    check("scenario geometry", [int(item["volume"]) for item in scenarios] == [2, 4, 6] and [int(item["oscillator_dimension"]) for item in scenarios] == [3, 3, 2], scenarios, "2/4 at n=3 and 6 at n=2", "geometry")

    coefficient_rows: list[dict[str, Any]] = []
    history_rows: list[dict[str, Any]] = []
    q_cache: dict[int, np.ndarray] = {}
    for scenario in scenarios:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_single = q_cache.setdefault(dimension, q3.oscillator(dimension)[0])
        q_ops, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, dimension, fixture)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
        shifted = energies - float(np.min(energies))
        bandwidth = float(np.max(shifted) - np.min(shifted))
        for beta in betas:
            probabilities = np.exp(-beta * shifted)
            probabilities /= float(np.sum(probabilities))
            p_min, p_max = float(np.min(probabilities)), float(np.max(probabilities))
            check(f"V={volume} n={dimension} beta={beta} Gibbs rank", p_min >= positivity_floor and p_max > 0.0, [p_min, p_max], f">={positivity_floor}", "Gibbs")
            rho = (vectors * probabilities) @ vectors.conj().T
            rho_half, rho_inverse_half = powers(rho, 0.5), powers(rho, -0.5)
            gibbs_band = math.exp(beta * bandwidth / 2.0)
            for radius in radii:
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                delta_norm = opnorm(tail)
                tail_hat = vectors.conj().T @ tail @ vectors
                spectral_left = vectors @ (np.diag(1.0 / np.sqrt(probabilities)) @ tail_hat @ np.diag(np.sqrt(probabilities))) @ vectors.conj().T
                spectral_right = vectors @ (np.diag(np.sqrt(probabilities)) @ tail_hat @ np.diag(1.0 / np.sqrt(probabilities))) @ vectors.conj().T
                direct_left, direct_right = rho_inverse_half @ tail @ rho_half, rho_half @ tail @ rho_inverse_half
                identity_residual = max(opnorm(direct_left - spectral_left), opnorm(direct_right - spectral_right))
                check(f"V={volume} n={dimension} beta={beta} L={radius} spectral identity", identity_residual <= identity_tolerance, identity_residual, f"<={identity_tolerance}", "spectral identity")
                check(f"V={volume} n={dimension} beta={beta} L={radius} Gibbs band", opnorm(direct_left) <= gibbs_band * delta_norm + tolerance * (1.0 + gibbs_band * delta_norm) and opnorm(direct_right) <= gibbs_band * delta_norm + tolerance * (1.0 + gibbs_band * delta_norm), [opnorm(direct_left), opnorm(direct_right), gibbs_band * delta_norm], "both<=band*Delta", "Gibbs envelope")
                for kind, base_weight in (("local", local_hamiltonian), ("full", hamiltonian)):
                    weight = q3.positive_weight(base_weight)
                    k_values = np.linalg.eigvalsh(weight)
                    k_band = math.sqrt(float(np.max(k_values)) / float(np.min(k_values)))
                    constants = similarity_constants(tail, weight, rho)
                    check(f"V={volume} n={dimension} beta={beta} L={radius} {kind} constants finite", all(np.isfinite(value) and value >= 0.0 for value in constants.values()), constants, "finite nonnegative", "similarity")
                    check(f"V={volume} n={dimension} beta={beta} L={radius} {kind} K band", constants["k_left"] <= k_band * delta_norm + tolerance * (1.0 + k_band * delta_norm) and constants["k_right"] <= k_band * delta_norm + tolerance * (1.0 + k_band * delta_norm), [constants["k_left"], constants["k_right"], k_band * delta_norm], "both<=band*Delta", "energy envelope")
                    coefficient_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "kind": kind, "energy_min": float(np.min(energies)), "energy_max": float(np.max(energies)), "energy_band": bandwidth, "gibbs_band": gibbs_band, "tail_operator_norm": delta_norm, "gibbs_left": opnorm(direct_left), "gibbs_right": opnorm(direct_right), "k_band": k_band, "constants": constants, "spectral_identity_residual": identity_residual})
                    for orientation in orientations:
                        delta = orientation * tail
                        for s_value in interpolation:
                            propagator = unitary(hamiltonian + orientation * s_value * tail, times[0], hbar)
                            for time in times:
                                if time != times[0]:
                                    propagator = unitary(hamiltonian + orientation * s_value * tail, time, hbar)
                                history = propagator @ observable @ propagator.conj().T
                                history_hat = vectors.conj().T @ history @ vectors
                                actual = opnorm(rho_inverse_half @ (delta @ history - history @ delta) @ rho_half)
                                base = opnorm(rho_inverse_half @ history @ rho_half)
                                envelope = gibbs_band * delta_norm * base
                                check(f"V={volume} n={dimension} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} history envelope", actual <= envelope + tolerance * (1.0 + envelope), [actual, envelope], "actual<=band*Delta*base", "history")
                                history_rows.append({"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "kind": kind, "orientation": orientation, "interpolation": s_value, "time": time, "actual": actual, "base": base, "envelope": envelope, "ratio": actual / max(envelope, np.finfo(float).tiny), "history_hat_norm": opnorm(history_hat)})
    expected_coefficients = len(scenarios) * len(betas) * len(radii) * 2
    expected_history = expected_coefficients * len(orientations) * len(interpolation) * len(times)
    check("coefficient coverage", len(coefficient_rows) == expected_coefficients, len(coefficient_rows), expected_coefficients, "coverage")
    check("history coverage", len(history_rows) == expected_history, len(history_rows), expected_history, "coverage")
    all_ratios = [float(row["ratio"]) for row in history_rows]
    all_bands = [float(row["gibbs_band"]) for row in coefficient_rows]
    check("finite diagnostics", all(np.isfinite(value) and value >= 0.0 for value in all_ratios + all_bands), [min(all_ratios), max(all_ratios), min(all_bands), max(all_bands)], "finite nonnegative", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GIBBS-MODULAR-BAND", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks[:64] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}], "coefficient_rows": coefficient_rows, "history_rows": history_rows, "derived": {"coefficient_row_count": len(coefficient_rows), "history_row_count": len(history_rows), "min_history_ratio": min(all_ratios), "max_history_ratio": max(all_ratios), "min_gibbs_band": min(all_bands), "max_gibbs_band": max(all_bands), "finite_gibbs_modular_band_identity_closed": True, "finite_similarity_band_envelope_closed": True, "source_volume_cutoff_beta_uniform_closed": False, "modular_domain_transfer_closed": False, "unbounded_common_core_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_os_hilbert_carrier_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "scope": scope, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-GIBBS-MODULAR-BAND PASS {payload['passed']}/{payload['assertion_count']} coefficients={payload['derived']['coefficient_row_count']} histories={payload['derived']['history_row_count']} max_band={payload['derived']['max_gibbs_band']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
