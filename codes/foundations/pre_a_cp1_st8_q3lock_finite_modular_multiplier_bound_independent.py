#!/usr/bin/env python3
"""Non-importing independent reconstruction for EXP-001185.

This lane rebuilds the finite Q3 matrices and the four similarity constants
without importing the primary audit.  It checks the same component and total
weighted commutator envelopes, leaving all thermodynamic claims open.
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
SLUG = "pre-a-cp1-st8-q3lock-finite-modular-multiplier-bound"
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
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = math.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / math.sqrt(2.0), (annihilation - creation) / (1j * math.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("registered finite graph family is 2,4,6")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def build_volume(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = {(left, right): bond_term(q_ops[left], q_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return q_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, bonds


def build_bond_volume(volume: int, n: int, fixture: dict[str, Any], bond_q: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    q_single, p_single = oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    bond_ops = [embed(bond_q, site, volume, identity) for site in range(volume)]
    bonds = {(left, right): bond_term(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)}
    return bonds


def cut_coordinate(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("spectral power received a non-positive matrix")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def positive_weight(base: np.ndarray) -> np.ndarray:
    hermitian = (base + base.conj().T) / 2.0
    minimum = float(np.min(np.linalg.eigvalsh(hermitian)))
    return hermitian - minimum * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex)


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def weighted_legs(matrix: np.ndarray, k_half: np.ndarray, rho_half: np.ndarray) -> dict[str, float]:
    legs = {
        "left_D": k_half @ matrix @ rho_half,
        "left_D_star": k_half @ matrix.conj().T @ rho_half,
        "right_D": matrix @ k_half @ rho_half,
        "right_D_star": matrix.conj().T @ k_half @ rho_half,
    }
    values = {name: float(np.linalg.norm(value, ord="fro")) for name, value in legs.items()}
    values["four_leg_norm"] = math.sqrt(sum(value * value for value in values.values()))
    return values


def coefficients(delta: np.ndarray, weight: np.ndarray, rho: np.ndarray) -> dict[str, float]:
    k_half = spectral_power(weight, 0.5)
    k_inverse_half = spectral_power(weight, -0.5)
    rho_half = spectral_power(rho, 0.5)
    rho_inverse_half = spectral_power(rho, -0.5)
    delta_star = delta.conj().T
    return {
        "left_D": operator_norm(k_half @ delta @ k_inverse_half) + operator_norm(rho_inverse_half @ delta @ rho_half),
        "left_D_star": operator_norm(rho_inverse_half @ delta_star @ rho_half) + operator_norm(k_half @ delta_star @ k_inverse_half),
        "right_D": operator_norm(delta) + operator_norm(k_inverse_half @ delta @ k_half),
        "right_D_star": operator_norm(delta_star) + operator_norm(k_inverse_half @ delta_star @ k_half),
    }


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    interpolation = [float(value) for value in fixture["interpolation_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    dimension, amplitude = int(fixture["oscillator_dimension"]), float(fixture["character_amplitude"])
    hbar, tolerance = float(fixture["hbar"]), float(fixture["finite_tolerance"])
    positivity_floor = float(fixture["positivity_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001185" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001185/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", [len(graph_edges(volume)) for volume in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_modular_multiplier_envelope_closed"] and scope["independent_trace_reconstruction_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["pre_a_closed"], scope, "finite multiplier envelope only", "scope")

    q_single, _ = oscillator(dimension)
    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, local_hamiltonian, bonds = build_volume(volume, dimension, fixture)
        observable = character(q_ops[0] + q_ops[1], amplitude, hbar)
        for beta in betas:
            rho = gibbs(hamiltonian, beta)
            rho_min = float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2.0)))
            check(f"V={volume} beta={beta} Gibbs positive", rho_min >= positivity_floor, rho_min, f">={positivity_floor}", "Gibbs")
            rho_half = spectral_power(rho, 0.5)
            volume_rows: list[dict[str, Any]] = []
            for radius in radii:
                q_cut = cut_coordinate(q_single, radius)
                cut_bonds = build_bond_volume(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                for kind, weight_base in (("local", local_hamiltonian), ("full", hamiltonian)):
                    weight = positive_weight(weight_base)
                    weight_min = float(np.min(np.linalg.eigvalsh(weight)))
                    check(f"V={volume} beta={beta} L={radius} {kind} weight positive", weight_min >= 1.0 - tolerance, weight_min, ">=1", "weights")
                    k_half = spectral_power(weight, 0.5)
                    coefficients_base = coefficients(tail, weight, rho)
                    check(f"V={volume} beta={beta} L={radius} {kind} coefficients finite", all(np.isfinite(value) and value >= 0.0 for value in coefficients_base.values()), coefficients_base, "finite nonnegative", "multiplier")
                    for orientation in orientations:
                        delta = orientation * tail
                        signed_coefficients = coefficients(delta, weight, rho)
                        signed_gamma = max(signed_coefficients.values())
                        for s_value in interpolation:
                            interpolated = hamiltonian + orientation * s_value * tail
                            for time in times:
                                history = unitary(interpolated, time, hbar) @ observable @ unitary(interpolated, time, hbar).conj().T
                                actual_matrix = commutator(delta, history)
                                base = weighted_legs(history, k_half, rho_half)
                                actual = weighted_legs(actual_matrix, k_half, rho_half)
                                bounds = {"left_D": signed_coefficients["left_D"] * base["left_D"], "left_D_star": signed_coefficients["left_D_star"] * base["left_D_star"], "right_D": signed_coefficients["right_D"] * base["right_D"], "right_D_star": signed_coefficients["right_D_star"] * base["right_D_star"]}
                                for name in bounds:
                                    check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} {name} envelope", actual[name] <= bounds[name] + tolerance * (1.0 + bounds[name]), [actual[name], bounds[name]], "actual<=bound", "component envelope")
                                envelope_norm = signed_gamma * base["four_leg_norm"]
                                check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} total envelope", actual["four_leg_norm"] <= envelope_norm + tolerance * (1.0 + envelope_norm), [actual["four_leg_norm"], envelope_norm], "actual<=gamma*base", "four-leg envelope")
                                values = {"base_four_leg_norm": base["four_leg_norm"], "commutator_four_leg_norm": actual["four_leg_norm"], "envelope_four_leg_norm": envelope_norm, "envelope_ratio": actual["four_leg_norm"] / max(envelope_norm, np.finfo(float).tiny), "gamma": signed_gamma, "tail_operator_norm": operator_norm(delta), "source_commutator_norm": operator_norm(commutator(tail, observable)), "component_actual": {name: actual[name] for name in bounds}, "component_bounds": bounds}
                                check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} finite", all(np.isfinite(value) for value in values.values() if isinstance(value, (int, float))), values, "finite", "rows")
                                row = {"volume": volume, "beta": beta, "radius": radius, "kind": kind, "orientation": orientation, "interpolation": s_value, "time": time, "values": values}
                                rows.append(row)
                                volume_rows.append(row)
                    summary_rows.append({"volume": volume, "beta": beta, "radius": radius, "kind": kind, "gamma": max(coefficients_base.values()), "max_envelope_ratio": max(row["values"]["envelope_ratio"] for row in volume_rows if row["kind"] == kind and row["radius"] == radius)})
    expected_rows = len(volumes) * len(betas) * len(radii) * 2 * len(orientations) * len(interpolation) * len(times)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    ratios = [row["values"]["envelope_ratio"] for row in rows]
    gammas = [row["values"]["gamma"] for row in rows]
    check("ratio finite", all(np.isfinite(value) and value >= 0.0 for value in ratios), [min(ratios), max(ratios)], "finite nonnegative", "scaling")
    check("gamma finite", all(np.isfinite(value) and value >= 0.0 for value in gammas), [min(gammas), max(gammas)], "finite nonnegative", "scaling")
    local_values = [row["values"]["gamma"] for row in rows if row["kind"] == "local"]
    full_values = [row["values"]["gamma"] for row in rows if row["kind"] == "full"]
    check("finite coefficients retained", max(local_values) >= min(local_values) and max(full_values) >= min(full_values), [min(local_values), max(local_values), min(full_values), max(full_values)], "ordered extrema", "scaling")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-MODULAR-MULTIPLIER-BOUND", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks[:48] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}], "summary_rows": summary_rows, "rows": rows, "derived": {"row_count": len(rows), "max_envelope_ratio": max(ratios), "min_envelope_ratio": min(ratios), "local_gamma_min": min(local_values), "local_gamma_max": max(local_values), "full_gamma_min": min(full_values), "full_gamma_max": max(full_values), "finite_modular_multiplier_envelope_closed": True, "finite_component_envelopes_closed": True, "independent_trace_reconstruction_closed": True, "source_volume_cutoff_beta_uniform_closed": False, "modular_domain_transfer_closed": False, "unbounded_common_core_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_os_hilbert_carrier_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "scope": scope, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-MODULAR-MULTIPLIER-BOUND PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} max_ratio={payload['derived']['max_envelope_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
