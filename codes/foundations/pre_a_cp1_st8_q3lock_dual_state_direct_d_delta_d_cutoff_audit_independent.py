#!/usr/bin/env python3
"""Independent NumPy lane for EXP-001123.

The implementation rebuilds the finite tensor matrices and compares the
reference and character-dual Gibbs seminorms without importing the primary
lane.  It remains a finite diagnostic only.
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


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit"
SOURCE = Path(__file__).resolve()
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{NAME}" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def qp(n: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.diag(np.sqrt(np.arange(1, n, dtype=float)), 1).astype(complex)
    return (lower + lower.T.conj()) / np.sqrt(2.0), (lower - lower.T.conj()) / (1j * np.sqrt(2.0))


def tensor(single: np.ndarray, site: int, volume: int, n: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(n, dtype=complex)
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, pair)) for pair in fixture["edges_by_volume"][str(volume)]]


def clipped(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) * 0.5)
    scale = np.abs(values) / radius
    taper = np.ones_like(scale)
    transition = (scale > 1.0) & (scale < 2.0)
    taper[transition] = 0.5 * (1.0 + np.cos(np.pi * (scale[transition] - 1.0)))
    taper[scale >= 2.0] = 0.0
    return (vectors * (values * taper)) @ vectors.conj().T


def build(volume: int, n: int, fixture: dict[str, Any], radius: float | None = None) -> tuple[np.ndarray, list[np.ndarray], np.ndarray]:
    q, p = qp(n)
    q_sites = [tensor(q, site, volume, n) for site in range(volume)]
    p_sites = [tensor(p, site, volume, n) for site in range(volume)]
    q_cut_sites = [tensor(clipped(q, radius), site, volume, n) for site in range(volume)] if radius is not None else q_sites
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    h = np.zeros_like(q_sites[0])
    for q_site, p_site in zip(q_sites, p_sites):
        h = h + p_site @ p_site / (2.0 * chi) + r * (q_site @ q_site) / 2.0 + g * np.linalg.matrix_power(q_site, 4) / 4.0
    bond = np.zeros_like(h)
    for left, right in edges(volume, fixture):
        difference = q_sites[left] - q_sites[right]
        square = difference @ difference
        bond = bond + c * square / 2.0 + lam * square @ (q_sites[left] @ q_sites[left] + q_sites[right] @ q_sites[right]) / 4.0
    if radius is None:
        return (h + bond + (h + bond).T.conj()) * 0.5, q_sites, bond
    cut_bond = np.zeros_like(h)
    for left, right in edges(volume, fixture):
        difference = q_cut_sites[left] - q_cut_sites[right]
        square = difference @ difference
        cut_bond = cut_bond + c * square / 2.0 + lam * square @ (q_cut_sites[left] @ q_cut_sites[left] + q_cut_sites[right] @ q_cut_sites[right]) / 4.0
    return (h + cut_bond + (h + cut_bond).T.conj()) * 0.5, q_sites, bond - cut_bond


def expm(h: np.ndarray, time: complex) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.T.conj()) * 0.5)
    return (vectors * np.exp(time * values)) @ vectors.T.conj()


def state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.T.conj()) * 0.5)
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    return (vectors * weights) @ vectors.T.conj()


def norm_parts(rho: np.ndarray, x: np.ndarray) -> tuple[float, float, float]:
    first = max(0.0, float(np.trace(rho @ x.T.conj() @ x).real))
    second = max(0.0, float(np.trace(rho @ x @ x.T.conj()).real))
    return float(np.sqrt(first + second)), first, second


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001123" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001123/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("declared signs", tuple(fixture["sign_values"]) == (-1, 1), fixture["sign_values"], "[-1,1]", "orientation")
    check("declared volumes", tuple(fixture["volume_values"]) == (2, 4), fixture["volume_values"], "[2,4]", "geometry")

    beta, hbar, amp = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    tolerance = float(fixture["hermitian_tolerance"])
    state_tolerance = float(fixture["state_tolerance"])
    commute_tolerance = float(fixture["commutation_tolerance"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        for n in map(int, fixture["oscillator_dimensions_by_volume"][str(volume)]):
            full_h, q_sites, _ = build(volume, n, fixture)
            rho = state(full_h, beta)
            observable = expm(q_sites[0], 1j * amp / hbar)
            dual = observable @ rho @ observable.T.conj()
            check(f"V={volume} n={n} H Hermitian", np.linalg.norm(full_h - full_h.T.conj(), ord=2) <= tolerance, np.linalg.norm(full_h - full_h.T.conj(), ord=2), f"<={tolerance}", "matrix")
            check(f"V={volume} n={n} state traces", max(abs(np.trace(rho).real - 1.0), abs(np.trace(dual).real - 1.0)) <= 100.0 * state_tolerance, [np.trace(rho), np.trace(dual)], "1", "state")
            check(f"V={volume} n={n} unitary", np.linalg.norm(observable.T.conj() @ observable - np.eye(observable.shape[0]), ord=2) <= 100.0 * tolerance, np.linalg.norm(observable.T.conj() @ observable - np.eye(observable.shape[0]), ord=2), "small", "character")
            radii: list[dict[str, Any]] = []
            for radius in map(float, fixture["radius_values"]):
                cut_h, _, tail = build(volume, n, fixture, radius)
                tail_ref = norm_parts(rho, tail)
                tail_dual = norm_parts(dual, tail)
                commutator = np.linalg.norm(tail @ observable - observable @ tail, ord=2)
                check(f"V={volume} n={n} L={radius} cutoff commutes", commutator <= commute_tolerance, commutator, f"<={commute_tolerance}", "CCR-core")
                times: list[dict[str, Any]] = []
                for time in map(float, fixture["time_values"]):
                    u = expm(full_h, -1j * time / hbar)
                    reference = u.T.conj() @ observable @ u
                    signs: list[dict[str, Any]] = []
                    for sign in map(int, fixture["sign_values"]):
                        signed = expm(full_h + sign * tail, -1j * time / hbar)
                        difference = signed.T.conj() @ observable @ signed - reference
                        derivative = 1j * (full_h @ difference - difference @ full_h) / hbar
                        ref_d, ref_dr, ref_dl = norm_parts(rho, difference)
                        ref_m, ref_mr, ref_ml = norm_parts(rho, derivative)
                        dual_d, dual_dr, dual_dl = norm_parts(dual, difference)
                        dual_m, dual_mr, dual_ml = norm_parts(dual, derivative)
                        check(f"V={volume} n={n} L={radius} t={time} s={sign} finite", all(np.isfinite(v) for v in (ref_d, ref_m, dual_d, dual_m)), [ref_d, ref_m, dual_d, dual_m], "finite", "Duhamel")
                        signs.append({
                            "sign": sign,
                            "reference_D": {"root": ref_d, "right": ref_dr, "left": ref_dl},
                            "reference_delta_D": {"root": ref_m, "right": ref_mr, "left": ref_ml},
                            "dual_D": {"root": dual_d, "right": dual_dr, "left": dual_dl},
                            "dual_delta_D": {"root": dual_m, "right": dual_mr, "left": dual_ml},
                            "reference_D_to_time_tail": ref_d / max(time * tail_ref[0], 1.0e-300),
                            "dual_D_to_time_tail": dual_d / max(time * tail_dual[0], 1.0e-300),
                            "reference_delta_to_tail": ref_m / max(tail_ref[0], 1.0e-300),
                            "dual_delta_to_tail": dual_m / max(tail_dual[0], 1.0e-300),
                        })
                    times.append({"time": time, "sign_rows": signs})
                radii.append({"radius": radius, "tail_reference": {"root": tail_ref[0], "right": tail_ref[1], "left": tail_ref[2]}, "tail_dual": {"root": tail_dual[0], "right": tail_dual[1], "left": tail_dual[2]}, "character_commutation_2norm": float(commutator), "times": times})
            volume_rows.append({"volume": volume, "oscillator_dimension": n, "hilbert_dimension": int(observable.shape[0]), "radius_rows": radii})

    ratios = [
        row[key]
        for volume_row in volume_rows
        for radius_row in volume_row["radius_rows"]
        for time_row in radius_row["times"]
        for row in time_row["sign_rows"]
        for key in ("reference_D_to_time_tail", "dual_D_to_time_tail", "reference_delta_to_tail", "dual_delta_to_tail")
    ]
    check("ratio finite", all(np.isfinite(v) and v >= float(fixture["finite_ratio_floor"]) for v in ratios), [min(ratios), max(ratios)], "finite nonnegative", "diagnostic")
    for key in ("actual_q3_dual_state_uniform_closed", "actual_q3_modular_tail_uniform_closed", "actual_unbounded_q3_common_core_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed"):
        check("scope open " + key, scope[key] is False, scope[key], False, "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-DIRECT-D-DELTA-D-CUTOFF",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
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
            "max_ratio": max(ratios),
            "min_ratio": min(ratios),
        },
        "provenance": {"script": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "script_sha256": digest(SOURCE), "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "manifest_sha256": digest(MANIFEST)},
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT DUAL-STATE-D-DELTA-D-CUTOFF PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
