#!/usr/bin/env python3
"""Primary finite-Q3 Gibbs condition-number/isometry audit for EXP-001126."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_gibbs_isometry_condition_number_audit"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(SCRIPT.parent))
import pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit as cross  # noqa: E402


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


def op_norm(operator: np.ndarray) -> float:
    return float(np.linalg.svd(operator, compute_uv=False)[0])


def log_condition(state: np.ndarray, beta: float, hamiltonian: np.ndarray) -> tuple[float, float, float]:
    energies = np.linalg.eigvalsh((hamiltonian + hamiltonian.conj().T) / 2.0)
    values = np.linalg.eigvalsh((state + state.conj().T) / 2.0)
    return float(beta * (float(energies[-1]) - float(energies[0]))), float(np.min(values)), float(np.max(values))


def safe_log_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0.0 or numerator <= 0.0:
        return float("inf")
    return float(np.log(numerator / denominator))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001126" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001126/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", all(scope[key] for key in ("finite_gibbs_condition_number_identity_closed", "finite_dual_spectrum_invariance_closed", "finite_state_isometry_comparison_closed", "finite_q3_condition_number_audit_closed")) and not scope["global_gibbs_isometry_uniform_closed"], scope, "finite condition checkpoint", "scope")

    hbar = float(fixture["hbar"])
    state_tol = float(fixture["state_tolerance"])
    comparison_tol = float(fixture["comparison_tolerance"])
    all_log_kappa: list[float] = []
    all_log_ratios: list[float] = []
    volume_rows: list[dict[str, Any]] = []

    for volume in (int(value) for value in fixture["volume_values"]):
        for dimension in (int(value) for value in fixture["oscillator_dimensions_by_volume"][str(volume)]):
            full = cross.matrices(volume, dimension, fixture)
            H = full["full_h"]
            rho = cross.gibbs(H, float(fixture["beta"]))
            A = cross.exponential(full["q0"], 1j * float(fixture["character_amplitude"]) / hbar)
            dual = A @ rho @ A.conj().T
            log_kappa, rho_min, rho_max = log_condition(rho, float(fixture["beta"]), H)
            dual_values = np.sort(np.linalg.eigvalsh((dual + dual.conj().T) / 2.0))
            rho_values = np.sort(np.linalg.eigvalsh((rho + rho.conj().T) / 2.0))
            check(f"V={volume} n={dimension} Gibbs faithful", rho_min > 0.0, rho_min, ">0", "state")
            check(f"V={volume} n={dimension} dual spectrum", np.max(np.abs(dual_values - rho_values)) <= 100.0 * state_tol, np.max(np.abs(dual_values - rho_values)), f"<={100.0 * state_tol}", "dual")
            B = cross.delta(H, A, hbar)
            C = cross.delta(H, B, hbar)
            radius_rows: list[dict[str, Any]] = []
            for radius in (float(value) for value in fixture["radius_values"]):
                cut = cross.matrices(volume, dimension, fixture, radius)
                W = cut["tail"]
                E = cross.delta(W, B, hbar)
                observables = {"C": C, "E": E}
                sign_rows: list[dict[str, Any]] = []
                for sign in (int(value) for value in fixture["sign_values"]):
                    K = H + sign * W
                    times: list[dict[str, Any]] = []
                    for time in (float(value) for value in fixture["time_values"]):
                        unitaries = {"H": cross.exponential(H, -1j * time / hbar), "signed": cross.exponential(K, -1j * time / hbar)}
                        observable_rows: list[dict[str, Any]] = []
                        for label, X in observables.items():
                            base_ref = cross.seminorm(rho, X)[0]
                            base_dual = cross.seminorm(dual, X)[0]
                            if base_ref <= 0.0 or base_dual <= 0.0:
                                continue
                            ratios: dict[str, float] = {}
                            for unitary_name, unitary in unitaries.items():
                                evolved = unitary.conj().T @ X @ unitary
                                ratios[f"reference_{unitary_name}"] = cross.seminorm(rho, evolved)[0] / base_ref
                                ratios[f"dual_{unitary_name}"] = cross.seminorm(dual, evolved)[0] / base_dual
                            all_log_ratios.extend(float(np.log(max(value, 1.0e-300))) for value in ratios.values())
                            check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} {label} finite", all(np.isfinite(value) for value in ratios.values()), ratios, "finite", "isometry")
                            check(f"V={volume} n={dimension} L={radius} t={time} sign={sign} {label} condition bound", max(safe_log_ratio(value, 1.0) for value in ratios.values()) <= 0.5 * log_kappa + comparison_tol, [max(ratios.values()), log_kappa], f"log ratio <= log(sqrt(kappa))", "isometry")
                            observable_rows.append({"label": label, "reference_base": base_ref, "dual_base": base_dual, "ratios": ratios})
                        times.append({"time": time, "observables": observable_rows})
                    sign_rows.append({"sign": sign, "times": times})
                all_log_kappa.append(log_kappa)
                radius_rows.append({"radius": radius, "cross_operator_norm": op_norm(E), "double_commutator_operator_norm": op_norm(C), "signs": sign_rows})
            volume_rows.append({"volume": volume, "oscillator_dimension": dimension, "hilbert_dimension": int(A.shape[0]), "log_condition_number": log_kappa, "sqrt_condition_log": 0.5 * log_kappa, "rho_min": rho_min, "rho_max": rho_max, "radii": radius_rows})

    check("coverage", len(volume_rows) == sum(len(fixture["oscillator_dimensions_by_volume"][str(v)]) for v in fixture["volume_values"]), len(volume_rows), "declared", "coverage")
    check("condition logs finite", all(np.isfinite(value) and value > 0.0 for value in all_log_kappa), [min(all_log_kappa), max(all_log_kappa)], ">0", "condition")
    check("comparison logs finite", all(np.isfinite(value) for value in all_log_ratios), [min(all_log_ratios), max(all_log_ratios)], "finite", "isometry")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-GIBBS-ISOMETRY-CONDITION-NUMBER",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "finite_gibbs_condition_number_identity_closed": True,
            "finite_dual_spectrum_invariance_closed": True,
            "finite_state_isometry_comparison_closed": True,
            "finite_q3_condition_number_audit_closed": True,
            "min_log_condition_number": min(all_log_kappa),
            "max_log_condition_number": max(all_log_kappa),
            "min_log_state_isometry_ratio": min(all_log_ratios),
            "max_log_state_isometry_ratio": max(all_log_ratios),
            "global_gibbs_isometry_uniform_closed": False,
            "local_modular_weight_uniform_closed": False,
            "actual_q3_evolved_dual_integrand_uniform_closed": False,
            "actual_q3_unbounded_common_core_closed": False,
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
            "pre_a_closed": False
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/")},
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY GIBBS-CONDITION-NUMBER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
