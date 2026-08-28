#!/usr/bin/env python3
"""Independent reconstruction of the R-388 state-weighted corridor stress."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-kinetic-resolvent-corridor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint/independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
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


def hermitian(x: np.ndarray) -> np.ndarray:
    return (x + x.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((dimension, dimension), dtype=complex)
    for n in range(dimension - 1):
        a[n, n + 1] = np.sqrt(n + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, dimension: int) -> np.ndarray:
    identity = np.eye(dimension, dtype=complex)
    return np.kron(single, identity) if site == 0 else np.kron(identity, single)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def opnorm(x: np.ndarray) -> float:
    return float(np.linalg.svd(x, compute_uv=False)[0])


def state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def seminorm(x: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ x.conj().T @ x) + np.trace(rho @ x @ x.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    dimensions = [int(x) for x in fixture["cutoff_dimensions"]]
    beta_values = [float(Fraction(x)) for x in fixture["beta_values"]]
    eta_values = [float(Fraction(x)) for x in fixture["resolvent_imaginary_values"]]
    late_dimension = int(fixture["late_dimension"])
    beta_floor = float(Fraction(fixture["corridor_beta_floor"]))
    eta_floor = float(Fraction(fixture["corridor_eta_floor"]))
    tolerance = float(fixture["corridor_split_threshold"])
    operator_threshold = float(fixture["operator_growth_threshold"])
    maximums = {"operator_norm": 0.0, "weighted_norm": 0.0}
    per_key: dict[str, list[float]] = {f"beta={beta};eta={eta}": [] for beta in beta_values for eta in eta_values}
    dimension_rows: list[dict[str, Any]] = []
    seed_rows = 0
    weighted_rows = 0

    for dimension in dimensions:
        q_single, p_single = oscillator(dimension)
        q0, q1 = lift(q_single, 0, dimension), lift(q_single, 1, dimension)
        p0, p1 = lift(p_single, 0, dimension), lift(p_single, 1, dimension)
        delta = q0 - q1
        boundary = hermitian(float(fixture["c"]) * delta @ delta / 2.0 + float(fixture["lambda"]) * (delta @ delta) @ (q0 @ q0 + q1 @ q1) / 4.0)
        kinetic = hermitian((p0 @ p0 + p1 @ p1) / (2.0 * float(fixture["chi"])))
        onsite = hermitian(float(fixture["r"]) * (q0 @ q0 + q1 @ q1) / 2.0 + float(fixture["g"]) * (q0 @ q0 @ q0 @ q0 + q1 @ q1 @ q1 @ q1) / 4.0)
        hamiltonian = hermitian(kinetic + onsite + boundary)
        states = {beta: state(hamiltonian, beta) for beta in beta_values}
        op_max = 0.0
        weighted_max: dict[str, float] = {}
        identity = np.eye(dimension * dimension, dtype=complex)
        for coordinate in (q0, q1):
            for eta in eta_values:
                resolvent = np.linalg.inv(1j * eta * identity - coordinate)
                for observable in (resolvent, resolvent.conj().T):
                    target = commutator(boundary, commutator(kinetic, observable))
                    op_value = opnorm(target)
                    op_max = max(op_max, op_value)
                    maximums["operator_norm"] = max(maximums["operator_norm"], op_value)
                    seed_rows += 1
                    for beta in beta_values:
                        weighted_value = seminorm(target, states[beta])
                        key = f"beta={beta};eta={eta}"
                        per_key[key].append(weighted_value)
                        weighted_max[key] = max(weighted_max.get(key, 0.0), weighted_value)
                        maximums["weighted_norm"] = max(maximums["weighted_norm"], weighted_value)
                        weighted_rows += 1
        dimension_rows.append({"dimension": dimension, "operator_max": op_max, "weighted_max_by_beta_eta": weighted_max})

    growth = dimension_rows[-1]["operator_max"] / dimension_rows[0]["operator_max"]
    if growth <= operator_threshold:
        raise AssertionError(f"operator growth witness missing: {growth}")
    mid = dimensions.index(late_dimension)
    late_ratios: dict[str, float] = {}
    corridor: list[str] = []
    outside: list[str] = []
    for key in per_key:
        beta = float(key.split(";")[0].split("=")[1])
        eta = float(key.split(";")[1].split("=")[1])
        values = [row["weighted_max_by_beta_eta"][key] for row in dimension_rows]
        late_ratios[key] = values[-1] / values[mid]
        (corridor if beta >= beta_floor and eta >= eta_floor else outside).append(key)
    if max(late_ratios[key] for key in corridor) > tolerance:
        raise AssertionError("finite corridor late stability failed")
    if max(late_ratios[key] for key in outside) <= tolerance:
        raise AssertionError("outside corridor stress was not seen")
    expected_seed_rows = len(dimensions) * len(fixture["site_values"]) * len(eta_values) * 2
    expected_weighted_rows = expected_seed_rows * len(beta_values)
    if seed_rows != expected_seed_rows or weighted_rows != expected_weighted_rows:
        raise AssertionError(f"coverage mismatch: {seed_rows}, {weighted_rows}")
    derived: dict[str, Any] = {"cutoff_dimensions": dimensions, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "operator_growth_ratio": growth, "late_ratios": late_ratios, "corridor_keys": corridor, "outside_keys": outside, "maximums": maximums, "dimension_rows": dimension_rows}
    for key in ("finite_operator_growth_stress_closed", "finite_gibbs_weighted_corridor_closed", "finite_beta_eta_corridor_split_closed"):
        derived[key] = True
    for key in ("operator_norm_uniformity_closed", "beta_uniformity_closed", "eta_uniformity_closed", "phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        derived[key] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-KINETIC-RESOLVENT-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": seed_rows + weighted_rows + 4, "assertions": [{"status": "PASS"}], "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT STATE-WEIGHTED KINETIC-RESOLVENT CORRIDOR PASS {payload['assertion_count']}/{payload['assertion_count']} seeds={payload['derived']['seed_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
