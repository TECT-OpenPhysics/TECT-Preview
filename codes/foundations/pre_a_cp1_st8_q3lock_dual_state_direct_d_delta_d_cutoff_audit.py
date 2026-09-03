#!/usr/bin/env python3
"""Finite dual-state direct-D/delta-D audit for EXP-001123.

This is a matrix-level checkpoint for the missing dual modular companion.  It
does not assert a CCR, common-core, thermodynamic, OS, or continuum theorem.
"""

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
SLUG = "pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit"
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


def graph_edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(value) for value in edge) for edge in fixture["edges_by_volume"][str(volume)]]


def matrices(volume: int, dimension: int, fixture: dict[str, Any], cut_radius: float | None = None) -> dict[str, Any]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)

    def cutoff(q: np.ndarray) -> np.ndarray:
        if cut_radius is None:
            return q
        values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
        scaled = np.abs(values) / cut_radius
        taper = np.where(
            scaled <= 1.0,
            1.0,
            np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0),
        )
        return (vectors * (values * taper)) @ vectors.conj().T

    q_sites = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_sites = [embed(p_single, site, volume, identity) for site in range(volume)]
    q_cut = [embed(cutoff(q_single), site, volume, identity) for site in range(volume)] if cut_radius is not None else q_sites
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite = np.zeros_like(q_sites[0])
    for q_site, p_site in zip(q_sites, p_sites):
        onsite += p_site @ p_site / (2.0 * chi) + r * (q_site @ q_site) / 2.0 + g * np.linalg.matrix_power(q_site, 4) / 4.0

    full_bond = np.zeros_like(q_sites[0])
    cut_bond = np.zeros_like(q_sites[0])
    for left, right in graph_edges(volume, fixture):
        difference = q_sites[left] - q_sites[right]
        square = difference @ difference
        full_bond += c * square / 2.0 + lam * square @ (q_sites[left] @ q_sites[left] + q_sites[right] @ q_sites[right]) / 4.0
        cut_difference = q_cut[left] - q_cut[right]
        cut_square = cut_difference @ cut_difference
        cut_bond += c * cut_square / 2.0 + lam * cut_square @ (q_cut[left] @ q_cut[left] + q_cut[right] @ q_cut[right]) / 4.0
    full_h = (onsite + full_bond + (onsite + full_bond).conj().T) / 2.0
    cut_h = (onsite + cut_bond + (onsite + cut_bond).conj().T) / 2.0
    return {"q_sites": q_sites, "full_h": full_h, "cut_h": cut_h, "tail": full_bond - cut_bond}


def exponential(hermitian: np.ndarray, coefficient: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((hermitian + hermitian.conj().T) / 2.0)
    return (vectors * np.exp(coefficient * values)) @ vectors.conj().T


def gibbs(hermitian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hermitian + hermitian.conj().T) / 2.0)
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def seminorm(state: np.ndarray, operator: np.ndarray) -> tuple[float, float, float]:
    right = float(np.trace(state @ operator.conj().T @ operator).real)
    left = float(np.trace(state @ operator @ operator.conj().T).real)
    return float(np.sqrt(max(0.0, right + left))), max(0.0, right), max(0.0, left)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001123" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001123/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["g"] > 0 and fixture["hbar"] > 0, [fixture["beta"], fixture["chi"], fixture["g"], fixture["hbar"]], "positive", "model")
    check("graph geometry", graph_edges(2, fixture) == [(0, 1)] and len(graph_edges(4, fixture)) == 4, [graph_edges(2, fixture), len(graph_edges(4, fixture))], "target and square", "geometry")
    check("scope firewall", all(scope[key] for key in ("finite_reference_direct_D_closed", "finite_reference_delta_D_closed", "finite_dual_direct_D_closed", "finite_dual_delta_D_closed", "finite_two_orientation_signs_closed", "finite_dual_state_construction_closed", "finite_ratio_audit_closed")) and not scope["actual_q3_dual_state_uniform_closed"] and not scope["actual_q3_modular_tail_uniform_closed"], scope, "finite dual checkpoint", "scope")

    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    hermitian_tol = float(fixture["hermitian_tolerance"])
    state_tol = float(fixture["state_tolerance"])
    commutation_tol = float(fixture["commutation_tolerance"])
    ratio_floor = float(fixture["finite_ratio_floor"])
    volume_rows: list[dict[str, Any]] = []

    for volume in (int(value) for value in fixture["volume_values"]):
        for dimension in (int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]):
            full = matrices(volume, dimension, fixture)
            q0 = full["q_sites"][0]
            full_h = full["full_h"]
            rho = gibbs(full_h, beta)
            observable = exponential(q0, 1j * amplitude / hbar)
            rho_dual = observable @ rho @ observable.conj().T
            h_error = float(np.linalg.norm(full_h - full_h.conj().T, ord=2))
            state_error = max(abs(float(np.trace(rho).real) - 1.0), abs(float(np.trace(rho_dual).real) - 1.0))
            unitary_error = float(np.linalg.norm(observable.conj().T @ observable - np.eye(observable.shape[0]), ord=2))
            check(f"V={volume} n={dimension} H Hermitian", h_error <= hermitian_tol, h_error, f"<={hermitian_tol}", "matrix")
            check(f"V={volume} n={dimension} states normalized", state_error <= 100.0 * state_tol, state_error, f"<={100.0 * state_tol}", "state")
            check(f"V={volume} n={dimension} character unitary", unitary_error <= 100.0 * hermitian_tol, unitary_error, f"<={100.0 * hermitian_tol}", "character")
            check(f"V={volume} n={dimension} dual positive", float(np.min(np.linalg.eigvalsh((rho_dual + rho_dual.conj().T) / 2.0))) >= -100.0 * state_tol, float(np.min(np.linalg.eigvalsh((rho_dual + rho_dual.conj().T) / 2.0))), ">=0", "state")
            radius_rows: list[dict[str, Any]] = []
            for radius in (float(value) for value in fixture["radius_values"]):
                cut = matrices(volume, dimension, fixture, radius)
                tail = cut["tail"]
                tail_root_ref, tail_right_ref, tail_left_ref = seminorm(rho, tail)
                tail_root_dual, tail_right_dual, tail_left_dual = seminorm(rho_dual, tail)
                commutation = float(np.linalg.norm(tail @ observable - observable @ tail, ord=2))
                check(f"V={volume} n={dimension} L={radius} tail finite", np.isfinite(tail_root_ref) and np.isfinite(tail_root_dual), [tail_root_ref, tail_root_dual], "finite", "cutoff")
                check(f"V={volume} n={dimension} L={radius} character commutation", commutation <= commutation_tol, commutation, f"<={commutation_tol}", "CCR-core")
                time_rows: list[dict[str, Any]] = []
                for time in (float(value) for value in fixture["time_values"]):
                    reference_u = exponential(full_h, -1j * time / hbar)
                    evolved_reference = reference_u.conj().T @ observable @ reference_u
                    sign_rows: list[dict[str, Any]] = []
                    for sign in (int(value) for value in fixture["sign_values"]):
                        signed_u = exponential(full_h + sign * tail, -1j * time / hbar)
                        difference = signed_u.conj().T @ observable @ signed_u - evolved_reference
                        modular_difference = 1j * (full_h @ difference - difference @ full_h) / hbar
                        ref_d = seminorm(rho, difference)
                        ref_delta = seminorm(rho, modular_difference)
                        dual_d = seminorm(rho_dual, difference)
                        dual_delta = seminorm(rho_dual, modular_difference)
                        finite_values = (ref_d[0], ref_delta[0], dual_d[0], dual_delta[0])
                        check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} finite", all(np.isfinite(value) for value in finite_values), finite_values, "finite", "Duhamel")
                        check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} signed H Hermitian", np.linalg.norm((full_h + sign * tail) - (full_h + sign * tail).conj().T, ord=2) <= hermitian_tol, np.linalg.norm((full_h + sign * tail) - (full_h + sign * tail).conj().T, ord=2), f"<={hermitian_tol}", "Duhamel")
                        sign_rows.append({
                            "sign": sign,
                            "reference_D": {"root": ref_d[0], "right": ref_d[1], "left": ref_d[2]},
                            "reference_delta_D": {"root": ref_delta[0], "right": ref_delta[1], "left": ref_delta[2]},
                            "dual_D": {"root": dual_d[0], "right": dual_d[1], "left": dual_d[2]},
                            "dual_delta_D": {"root": dual_delta[0], "right": dual_delta[1], "left": dual_delta[2]},
                            "reference_D_to_time_tail": ref_d[0] / max(time * tail_root_ref, 1.0e-300),
                            "dual_D_to_time_tail": dual_d[0] / max(time * tail_root_dual, 1.0e-300),
                            "reference_delta_to_tail": ref_delta[0] / max(tail_root_ref, 1.0e-300),
                            "dual_delta_to_tail": dual_delta[0] / max(tail_root_dual, 1.0e-300),
                        })
                    time_rows.append({"time": time, "sign_rows": sign_rows})
                radius_rows.append({
                    "radius": radius,
                    "tail_reference": {"root": tail_root_ref, "right": tail_right_ref, "left": tail_left_ref},
                    "tail_dual": {"root": tail_root_dual, "right": tail_right_dual, "left": tail_left_dual},
                    "character_commutation_2norm": commutation,
                    "times": time_rows,
                })
            volume_rows.append({"volume": volume, "oscillator_dimension": dimension, "hilbert_dimension": int(observable.shape[0]), "radius_rows": radius_rows})

    check("volume/dimension rows", len(volume_rows) == sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) for v in fixture["volume_values"]), len(volume_rows), "declared rows", "coverage")
    all_ratios = [
        ratio
        for row in volume_rows
        for radius_row in row["radius_rows"]
        for time_row in radius_row["times"]
        for sign_row in time_row["sign_rows"]
        for ratio in (sign_row["reference_D_to_time_tail"], sign_row["dual_D_to_time_tail"], sign_row["reference_delta_to_tail"], sign_row["dual_delta_to_tail"])
    ]
    check("ratio audit finite", all(np.isfinite(value) and value >= ratio_floor for value in all_ratios), [min(all_ratios), max(all_ratios)], f">={ratio_floor} and finite", "diagnostic")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-DIRECT-D-DELTA-D-CUTOFF",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_reference_direct_D_closed": True,
            "finite_reference_delta_D_closed": True,
            "finite_dual_direct_D_closed": True,
            "finite_dual_delta_D_closed": True,
            "finite_two_orientation_signs_closed": True,
            "finite_dual_state_construction_closed": True,
            "finite_ratio_audit_closed": True,
            "actual_q3_dual_state_uniform_closed": False,
            "actual_q3_modular_tail_uniform_closed": False,
            "actual_unbounded_q3_common_core_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "max_ratio": max(all_ratios),
            "min_ratio": min(all_ratios),
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": normalized_sha256(MANIFEST)},
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
    print(f"PRIMARY DUAL-STATE-D-DELTA-D-CUTOFF PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
