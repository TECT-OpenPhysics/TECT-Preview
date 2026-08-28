#!/usr/bin/env python3
"""Finite state-weighted corridor stress for the R-387 kinetic target.

The operator norm of K=[B,[T,A_z]] is compared with its two-sided Gibbs
seminorm across oscillator cutoffs, beta values and resolvent scales.  The
purpose is to identify a fixed-beta, sufficiently smoothed corridor; no
cutoff-uniform theorem is inferred from the finite table.
"""

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
SLUG = "pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-kinetic-resolvent-corridor-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, dimension: int, identity: np.ndarray) -> np.ndarray:
    return np.kron(single, identity) if site == 0 else np.kron(identity, single)


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def two_sided_norm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def build_model(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q0, q1 = lift(q_single, 0, dimension, identity), lift(q_single, 1, dimension, identity)
    p0, p1 = lift(p_single, 0, dimension, identity), lift(p_single, 1, dimension, identity)
    difference = q0 - q1
    quadratic = difference @ difference
    boundary = hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quadratic @ (q0 @ q0 + q1 @ q1) / 4.0)
    kinetic = hermitian((p0 @ p0 + p1 @ p1) / (2.0 * float(fixture["chi"])))
    onsite = hermitian(float(fixture["r"]) * (q0 @ q0 + q1 @ q1) / 2.0 + float(fixture["g"]) * (q0 @ q0 @ q0 @ q0 + q1 @ q1 @ q1 @ q1) / 4.0)
    return q0, q1, p0, p1, hermitian(kinetic + onsite + boundary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001231" and manifest["result_id"] == "R-388" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001231/R-388/false", "provenance")
    check("coverage", coverage["all_sites"] and coverage["both_adjoint_seeds"] and coverage["all_cutoff_dimensions"], coverage, "all sites, adjoints and cutoffs", "coverage")
    finite_flags = ("finite_operator_growth_stress_closed", "finite_gibbs_weighted_corridor_closed", "finite_beta_eta_corridor_split_closed")
    open_flags = ("operator_norm_uniformity_closed", "beta_uniformity_closed", "eta_uniformity_closed", "phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(scope[key] for key in open_flags), "finite stress / all uniform limits open", "scope", "scope")

    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    beta_values = [float(Fraction(value)) for value in fixture["beta_values"]]
    eta_values = [float(Fraction(value)) for value in fixture["resolvent_imaginary_values"]]
    beta_floor = float(Fraction(fixture["corridor_beta_floor"]))
    eta_floor = float(Fraction(fixture["corridor_eta_floor"]))
    operator_threshold = float(fixture["operator_growth_threshold"])
    split_threshold = float(fixture["corridor_split_threshold"])
    late_dimension = int(fixture["late_dimension"])
    maxima = {"operator_norm": 0.0, "weighted_norm": 0.0}
    per_beta_eta: dict[str, list[float]] = {f"beta={beta};eta={eta}": [] for beta in beta_values for eta in eta_values}
    dimension_rows: list[dict[str, Any]] = []
    seed_rows = 0
    weighted_rows = 0

    for dimension in dimensions:
        q0, q1, p0, p1, hamiltonian = build_model(dimension, fixture)
        identity = np.eye(dimension * dimension, dtype=complex)
        q_sites = [q0, q1]
        kinetic = hermitian((p0 @ p0 + p1 @ p1) / (2.0 * float(fixture["chi"])))
        difference = q0 - q1
        boundary = hermitian(float(fixture["c"]) * (difference @ difference) / 2.0 + float(fixture["lambda"]) * (difference @ difference) @ (q0 @ q0 + q1 @ q1) / 4.0)
        states = {beta: gibbs(hamiltonian, beta) for beta in beta_values}
        op_values: list[float] = []
        weighted_by_key: dict[str, list[float]] = {key: [] for key in per_beta_eta}
        for site, coordinate in enumerate(q_sites):
            for eta in eta_values:
                seed = np.linalg.inv(1j * eta * identity - coordinate)
                for observable in (seed, seed.conj().T):
                    target = commutator(boundary, commutator(kinetic, observable))
                    op_value = operator_norm(target)
                    op_values.append(op_value)
                    maxima["operator_norm"] = max(maxima["operator_norm"], op_value)
                    seed_rows += 1
                    check(f"d={dimension} site={site} eta={eta} operator", np.isfinite(op_value), op_value, "finite", "operator stress")
                    for beta in beta_values:
                        weighted_value = two_sided_norm(target, states[beta])
                        key = f"beta={beta};eta={eta}"
                        weighted_by_key[key].append(weighted_value)
                        per_beta_eta[key].append(weighted_value)
                        maxima["weighted_norm"] = max(maxima["weighted_norm"], weighted_value)
                        weighted_rows += 1
                        check(f"d={dimension} site={site} eta={eta} beta={beta} weighted", np.isfinite(weighted_value), weighted_value, "finite", "Gibbs weighted")
        per_dimension = {key: max(values) for key, values in weighted_by_key.items()}
        dimension_rows.append({"dimension": dimension, "operator_max": max(op_values), "weighted_max_by_beta_eta": per_dimension})

    first_operator = dimension_rows[0]["operator_max"]
    last_operator = dimension_rows[-1]["operator_max"]
    operator_growth_ratio = last_operator / first_operator
    check("operator growth witness", operator_growth_ratio > operator_threshold, operator_growth_ratio, f">{operator_threshold}", "operator stress")
    late_ratios: dict[str, float] = {}
    mid_index = dimensions.index(late_dimension)
    last_index = len(dimensions) - 1
    corridor_keys: list[str] = []
    noncorridor_keys: list[str] = []
    for key in per_beta_eta:
        beta = float(key.split(";")[0].split("=")[1])
        eta = float(key.split(";")[1].split("=")[1])
        values = [row["weighted_max_by_beta_eta"][key] for row in dimension_rows]
        ratio = values[last_index] / values[mid_index]
        late_ratios[key] = ratio
        if beta >= beta_floor and eta >= eta_floor:
            corridor_keys.append(key)
        else:
            noncorridor_keys.append(key)
    check("corridor samples", bool(corridor_keys) and bool(noncorridor_keys), [corridor_keys, noncorridor_keys], "both corridor and outside samples", "corridor")
    corridor_ratios = [late_ratios[key] for key in corridor_keys]
    outside_ratios = [late_ratios[key] for key in noncorridor_keys]
    check("corridor late stability", max(corridor_ratios) <= split_threshold, max(corridor_ratios), f"<={split_threshold}", "corridor")
    check("outside late stress", max(outside_ratios) > split_threshold, max(outside_ratios), f">{split_threshold}", "corridor")
    expected_seed_rows = len(dimensions) * len(coverage["site_values"]) * len(eta_values) * 2
    expected_weighted_rows = expected_seed_rows * len(beta_values)
    check("row counts", seed_rows == expected_seed_rows and weighted_rows == expected_weighted_rows, [seed_rows, weighted_rows], [expected_seed_rows, expected_weighted_rows], "coverage")
    check("finite maxima", all(np.isfinite(value) for value in maxima.values()), maxima, "finite", "numerics")
    derived: dict[str, Any] = {"cutoff_dimensions": dimensions, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "operator_growth_ratio": operator_growth_ratio, "late_ratios": late_ratios, "corridor_keys": corridor_keys, "outside_keys": noncorridor_keys, "maximums": maxima, "dimension_rows": dimension_rows}
    for key in finite_flags:
        derived[key] = True
    for key in open_flags:
        derived[key] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-KINETIC-RESOLVENT-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY STATE-WEIGHTED KINETIC-RESOLVENT CORRIDOR PASS {payload['passed']}/{payload['assertion_count']} seeds={payload['derived']['seed_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
