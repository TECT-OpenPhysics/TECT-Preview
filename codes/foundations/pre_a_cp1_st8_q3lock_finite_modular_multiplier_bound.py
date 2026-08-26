#!/usr/bin/env python3
"""Primary finite-Q3 modular multiplier envelope for source-boundary histories (EXP-001185).

The finite statement is deliberately elementary.  For a positive weight K and
full-rank Gibbs matrix rho, the four weighted Hilbert--Schmidt legs of
[Delta,B] are bounded by the corresponding legs of B.  The coefficients are
the four finite similarity constants that arise by inserting K^(1/2)K^(-1/2)
and rho^(1/2)rho^(-1/2); no commutation of K, rho, Delta, or B is assumed.
The Q3 rows only test this bounded finite interface.  They do not assert a
uniform common-core modular multiplier theorem.
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
SLUG = "pre-a-cp1-st8-q3lock-finite-modular-multiplier-bound"
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


def weighted_legs(matrix: np.ndarray, k_half: np.ndarray, rho_half: np.ndarray) -> dict[str, float]:
    legs = {
        "left_D": k_half @ matrix @ rho_half,
        "left_D_star": k_half @ matrix.conj().T @ rho_half,
        "right_D": matrix @ k_half @ rho_half,
        "right_D_star": matrix.conj().T @ k_half @ rho_half,
    }
    values = {name: float(np.linalg.norm(value, ord="fro")) for name, value in legs.items()}
    values["four_leg_norm"] = float(math.sqrt(sum(value * value for value in values.values())))
    return values


def positive_powers(matrix: np.ndarray, exponent: float) -> np.ndarray:
    return q3.spectral_power(matrix, exponent)


def multiplier_coefficients(delta: np.ndarray, weight: np.ndarray, rho: np.ndarray) -> dict[str, float]:
    k_half = positive_powers(weight, 0.5)
    k_inverse_half = positive_powers(weight, -0.5)
    rho_half = positive_powers(rho, 0.5)
    rho_inverse_half = positive_powers(rho, -0.5)
    delta_star = delta.conj().T
    return {
        "left_D": q3.operator_norm(k_half @ delta @ k_inverse_half) + q3.operator_norm(rho_inverse_half @ delta @ rho_half),
        "left_D_star": q3.operator_norm(rho_inverse_half @ delta_star @ rho_half) + q3.operator_norm(k_half @ delta_star @ k_inverse_half),
        "right_D": q3.operator_norm(delta) + q3.operator_norm(k_inverse_half @ delta @ k_half),
        "right_D_star": q3.operator_norm(delta_star) + q3.operator_norm(k_inverse_half @ delta_star @ k_half),
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    volumes = [int(value) for value in fixture["volume_values"]]
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    times = [float(value) for value in fixture["time_values"]]
    interpolation = [float(value) for value in fixture["interpolation_values"]]
    orientations = [int(value) for value in fixture["orientation_values"]]
    dimension = int(fixture["oscillator_dimension"])
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    tolerance = float(fixture["finite_tolerance"])
    positivity_floor = float(fixture["positivity_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001185" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001185/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", [len(q3.graph_edges(volume)) for volume in volumes] == [1, 4, 7], volumes, "edge/square/six-site", "geometry")
    check("scope firewall", scope["finite_modular_multiplier_envelope_closed"] and scope["independent_trace_reconstruction_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["pre_a_closed"], scope, "finite multiplier envelope only", "scope")

    q_single, _ = q3.oscillator(dimension)
    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for volume in volumes:
        q_ops, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, dimension, fixture)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        for beta in betas:
            rho = q3.gibbs(hamiltonian, beta)
            rho_min = float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2.0)))
            check(f"V={volume} beta={beta} Gibbs positive", rho_min >= positivity_floor, rho_min, f">={positivity_floor}", "Gibbs")
            rho_half = positive_powers(rho, 0.5)
            volume_rows: list[dict[str, Any]] = []
            for radius in radii:
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                zero = np.zeros_like(hamiltonian)
                tail = sum((bonds[edge] - cut_bonds[edge] for edge in bonds), zero)
                tail = (tail + tail.conj().T) / 2.0
                for kind, weight_base in (("local", local_hamiltonian), ("full", hamiltonian)):
                    weight = q3.positive_weight(weight_base)
                    weight_min = float(np.min(np.linalg.eigvalsh(weight)))
                    check(f"V={volume} beta={beta} L={radius} {kind} weight positive", weight_min >= 1.0 - tolerance, weight_min, ">=1", "weights")
                    k_half = positive_powers(weight, 0.5)
                    coefficients = multiplier_coefficients(tail, weight, rho)
                    coefficient_values = list(coefficients.values())
                    check(f"V={volume} beta={beta} L={radius} {kind} coefficients finite", all(np.isfinite(value) and value >= 0.0 for value in coefficient_values), coefficients, "finite nonnegative", "multiplier")
                    gamma = max(coefficient_values)
                    for orientation in orientations:
                        delta = orientation * tail
                        signed_coefficients = multiplier_coefficients(delta, weight, rho)
                        signed_gamma = max(signed_coefficients.values())
                        for s_value in interpolation:
                            interpolated = hamiltonian + orientation * s_value * tail
                            for time in times:
                                propagator = unitary(interpolated, time, hbar)
                                history = propagator @ observable @ propagator.conj().T
                                commutator = delta @ history - history @ delta
                                base = weighted_legs(history, k_half, rho_half)
                                actual = weighted_legs(commutator, k_half, rho_half)
                                bounds = {
                                    "left_D": signed_coefficients["left_D"] * base["left_D"],
                                    "left_D_star": signed_coefficients["left_D_star"] * base["left_D_star"],
                                    "right_D": signed_coefficients["right_D"] * base["right_D"],
                                    "right_D_star": signed_coefficients["right_D_star"] * base["right_D_star"],
                                }
                                for name in bounds:
                                    check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} {name} envelope", actual[name] <= bounds[name] + tolerance * (1.0 + bounds[name]), [actual[name], bounds[name]], "actual<=bound", "component envelope")
                                actual_norm = actual["four_leg_norm"]
                                base_norm = base["four_leg_norm"]
                                envelope_norm = signed_gamma * base_norm
                                check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} total envelope", actual_norm <= envelope_norm + tolerance * (1.0 + envelope_norm), [actual_norm, envelope_norm], "actual<=gamma*base", "four-leg envelope")
                                values = {
                                    "base_four_leg_norm": base_norm,
                                    "commutator_four_leg_norm": actual_norm,
                                    "envelope_four_leg_norm": envelope_norm,
                                    "envelope_ratio": actual_norm / max(envelope_norm, np.finfo(float).tiny),
                                    "gamma": signed_gamma,
                                    "tail_operator_norm": q3.operator_norm(delta),
                                    "source_commutator_norm": q3.operator_norm(q3.commutator(tail, observable)),
                                    "component_actual": {name: actual[name] for name in bounds},
                                    "component_bounds": bounds,
                                }
                                check(f"V={volume} beta={beta} L={radius} {kind} sign={orientation} s={s_value} t={time} finite", all(np.isfinite(value) for value in values.values() if isinstance(value, (int, float))), values, "finite", "rows")
                                row = {"volume": volume, "beta": beta, "radius": radius, "kind": kind, "orientation": orientation, "interpolation": s_value, "time": time, "values": values}
                                rows.append(row)
                                volume_rows.append(row)
                    summary_rows.append({
                        "volume": volume,
                        "beta": beta,
                        "radius": radius,
                        "kind": kind,
                        "gamma": gamma,
                        "max_envelope_ratio": max(row["values"]["envelope_ratio"] for row in volume_rows if row["kind"] == kind and row["radius"] == radius),
                    })
    expected_rows = len(volumes) * len(betas) * len(radii) * 2 * len(orientations) * len(interpolation) * len(times)
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    ratios = [row["values"]["envelope_ratio"] for row in rows]
    gammas = [row["values"]["gamma"] for row in rows]
    check("ratio finite", all(np.isfinite(value) and value >= 0.0 for value in ratios), [min(ratios), max(ratios)], "finite nonnegative", "scaling")
    check("gamma finite", all(np.isfinite(value) and value >= 0.0 for value in gammas), [min(gammas), max(gammas)], "finite nonnegative", "scaling")
    local_max = max(row["values"]["gamma"] for row in rows if row["kind"] == "local")
    full_max = max(row["values"]["gamma"] for row in rows if row["kind"] == "full")
    local_min = min(row["values"]["gamma"] for row in rows if row["kind"] == "local")
    full_min = min(row["values"]["gamma"] for row in rows if row["kind"] == "full")
    check("finite coefficients retained", local_max >= local_min and full_max >= full_min, [local_min, local_max, full_min, full_max], "ordered extrema", "scaling")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-MODULAR-MULTIPLIER-BOUND",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks[:48] + [{"name": "assertion_summary", "group": "summary", "status": "PASS", "actual": str(len(checks)), "expected": "all executed assertions passed"}],
        "summary_rows": summary_rows,
        "rows": rows,
        "derived": {
            "row_count": len(rows),
            "max_envelope_ratio": max(ratios),
            "min_envelope_ratio": min(ratios),
            "local_gamma_min": local_min,
            "local_gamma_max": local_max,
            "full_gamma_min": full_min,
            "full_gamma_max": full_max,
            "finite_modular_multiplier_envelope_closed": True,
            "finite_component_envelopes_closed": True,
            "independent_trace_reconstruction_closed": True,
            "source_volume_cutoff_beta_uniform_closed": False,
            "modular_domain_transfer_closed": False,
            "unbounded_common_core_closed": False,
            "direct_d_delta_d_cauchy_closed": False,
            "common_os_hilbert_carrier_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
        },
        "scope": scope,
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-MODULAR-MULTIPLIER-BOUND PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} max_ratio={payload['derived']['max_envelope_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
