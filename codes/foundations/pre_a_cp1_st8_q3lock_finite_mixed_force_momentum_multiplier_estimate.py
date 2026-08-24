#!/usr/bin/env python3
"""Primary finite-Q3 mixed force--momentum multiplier audit for EXP-001081.

The calculation proves and tests a finite-dimensional two-sided Gibbs estimate
for ``M_L p_1`` with ``M_L=W_L partial_q B``.  It deliberately keeps the
multiplier norms explicit, so their oscillator-cutoff growth is visible rather
than silently promoted to an energy-weighted uniform estimate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-mixed-force-momentum-multiplier-estimate"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-primary-{SLUG}/primary.json"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_structured_cutoff_orbit_modular_derivative as q3  # noqa: E402


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


def cutoff_data(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    eta = np.where(
        scaled <= 1.0,
        1.0,
        np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0),
    )
    eta_prime = np.where(
        scaled <= 1.0,
        0.0,
        np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0),
    )
    eta_second = np.where(
        scaled <= 1.0,
        0.0,
        np.where(scaled < 2.0, -0.5 * np.pi**2 * np.cos(np.pi * (scaled - 1.0)), 0.0),
    )
    q_cut = values * eta
    q_prime = eta + scaled * eta_prime
    q_second = np.where(
        np.abs(values) <= np.finfo(float).eps,
        0.0,
        np.sign(values) * (2.0 * eta_prime + scaled * eta_second) / radius,
    )
    return q_cut, q_prime, q_second


def bond_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference**2 / 2.0 + lam * difference**2 * (q_value**2 + v_value**2) / 4.0


def force_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference + lam * difference * (2.0 * q_value**2 - q_value * v_value + v_value**2) / 2.0


def force_prime_scalar(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c + lam * (q_value**2 + v_value**2 + difference**2 + 4.0 * q_value * difference) / 2.0


def scalar_mixed(q_value: float, v_value: float, radius: float, c: float, lam: float) -> float:
    q_cut, _, _ = cutoff_data(np.asarray(q_value), radius)
    v_cut, _, _ = cutoff_data(np.asarray(v_value), radius)
    return float((bond_scalar(np.asarray(q_value), np.asarray(v_value), c, lam) - bond_scalar(q_cut, v_cut, c, lam)) * force_scalar(np.asarray(q_value), np.asarray(v_value), c, lam))


def scalar_mixed_prime(q_value: float, v_value: float, radius: float, c: float, lam: float) -> float:
    q_array = np.asarray(q_value)
    v_array = np.asarray(v_value)
    q_cut, q_prime, q_second = cutoff_data(q_array, radius)
    v_cut, _, _ = cutoff_data(v_array, radius)
    difference = q_array - v_array
    difference_cut = q_cut - v_cut
    bond_tail = bond_scalar(q_array, v_array, c, lam) - bond_scalar(q_cut, v_cut, c, lam)
    force = force_scalar(q_array, v_array, c, lam)
    force_prime = force_prime_scalar(q_array, v_array, c, lam)
    force_cut = force_scalar(q_cut, v_cut, c, lam)
    force_cut_prime = force_prime_scalar(q_cut, v_cut, c, lam)
    tail_prime = force - force_cut * q_prime
    mixed_prime = tail_prime * force + bond_tail * force_prime
    _ = difference, difference_cut, q_second, force_cut_prime
    return float(mixed_prime)


def matrix_from_coordinate_values(values: np.ndarray, eigenvectors: np.ndarray) -> np.ndarray:
    joint_vectors = np.kron(eigenvectors, eigenvectors)
    return joint_vectors @ np.diag(values.reshape(-1)) @ joint_vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001081" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001081/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("positive finite parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["hbar"] > 0 and fixture["g"] > 0 and fixture["c"] >= 0 and fixture["lambda"] >= 0, fixture, "positive finite parameters", "model")
    check("scope firewall", scope["finite_two_sided_mixed_multiplier_bound_closed"] and scope["unweighted_multiplier_scaling_diagnostic_closed"] and not scope["unweighted_cutoff_uniformity_proved"] and not scope["energy_weighted_mixed_bound_closed"], scope, "finite mixed bound with uniformity open", "scope")

    tolerance = float(fixture["bound_tolerance"])
    derivative_tolerance = float(fixture["derivative_tolerance"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    hbar = float(fixture["hbar"])
    beta = float(fixture["beta"])
    dimension_rows: list[dict[str, Any]] = []
    fixed_radius_u: list[float] = []

    for n_value in fixture["n_values"]:
        n = int(n_value)
        matrices = q3.q3_matrices(n, fixture)
        q_matrix, _ = q3.oscillator(n)
        eigenvalues, eigenvectors = np.linalg.eigh((q_matrix + q_matrix.conj().T) / 2.0)
        full_h = matrices["onsite"] + matrices["bond"]
        rho = q3.gibbs_state(full_h, beta)
        p1 = matrices["p1"]
        kappa = float(np.sqrt(max(0.0, np.trace(rho @ (p1 @ p1)).real)))
        radius_rows: list[dict[str, Any]] = []

        for radius in fixture["radius_values"]:
            radius_float = float(radius)
            q_values, v_values = np.meshgrid(eigenvalues, eigenvalues, indexing="ij")
            q_cut, q_prime, q_second = cutoff_data(q_values, radius_float)
            v_cut, _, _ = cutoff_data(v_values, radius_float)
            difference = q_values - v_values
            difference_cut = q_cut - v_cut
            bond = bond_scalar(q_values, v_values, c, lam)
            cut_bond = bond_scalar(q_cut, v_cut, c, lam)
            tail = bond - cut_bond
            force = force_scalar(q_values, v_values, c, lam)
            force_prime = force_prime_scalar(q_values, v_values, c, lam)
            cut_force = force_scalar(q_cut, v_cut, c, lam)
            tail_prime = force - cut_force * q_prime
            mixed = tail * force
            mixed_prime = tail_prime * force + tail * force_prime
            _ = q_second, difference, difference_cut

            mixed_matrix = matrix_from_coordinate_values(mixed, eigenvectors)
            mixed_prime_matrix = matrix_from_coordinate_values(mixed_prime, eigenvectors)
            actual_root = q3.norms(rho, mixed_matrix @ p1)[0]
            multiplier_norm = float(np.max(np.abs(mixed)))
            derivative_norm = float(np.max(np.abs(mixed_prime)))
            bound_squared = (multiplier_norm * kappa) ** 2 + (multiplier_norm * kappa + hbar * derivative_norm) ** 2
            bound_root = float(np.sqrt(max(0.0, bound_squared)))
            check(f"n={n} L={radius_float} mixed bound", actual_root**2 <= bound_squared + tolerance * (1.0 + bound_squared), [actual_root, bound_root], "actual<=finite multiplier bound", "mixed bound")
            check(f"n={n} L={radius_float} multiplier finite", np.isfinite(multiplier_norm) and np.isfinite(derivative_norm), [multiplier_norm, derivative_norm], "finite", "multiplier")
            radius_rows.append({"radius": radius_float, "actual_root": actual_root, "bound_root": bound_root, "multiplier_norm": multiplier_norm, "derivative_norm": derivative_norm, "kinetic_root": kappa, "bound_squared": bound_squared, "bound_margin": bound_root - actual_root})
            if abs(radius_float - float(fixture["scaling_radius"])) <= tolerance:
                fixed_radius_u.append(multiplier_norm)
        dimension_rows.append({"n": n, "dimension": n * n, "kinetic_root": kappa, "radii": radius_rows})

    # The scalar chain rule is checked away from taper junctions, where a
    # centered finite difference is an independent local derivative test.
    for radius in fixture["radius_values"]:
        for q_value, v_value in ((0.2, -0.4), (1.2, -0.3), (-1.3, 0.4)):
            epsilon = 1.0e-6
            numerical = (scalar_mixed(q_value + epsilon, v_value, float(radius), c, lam) - scalar_mixed(q_value - epsilon, v_value, float(radius), c, lam)) / (2.0 * epsilon)
            analytic = scalar_mixed_prime(q_value, v_value, float(radius), c, lam)
            check(f"chain rule L={radius} q={q_value} v={v_value}", abs(numerical - analytic) < derivative_tolerance, [numerical, analytic], f"<{derivative_tolerance}", "chain rule")

    nondecreasing = all(next_value + float(fixture["scaling_tolerance"]) >= current for current, next_value in zip(fixed_radius_u, fixed_radius_u[1:]))
    check("finite cutoff growth diagnostic", nondecreasing, fixed_radius_u, "nondecreasing at fixed radius", "scaling")
    check("all rows finite", all(np.isfinite(row["bound_root"]) and np.isfinite(row["actual_root"]) for item in dimension_rows for row in item["radii"]), dimension_rows, "finite", "diagnostic")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-MIXED-FORCE-MOMENTUM-MULTIPLIER-ESTIMATE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "dimension_rows": dimension_rows,
            "fixed_radius_multiplier_norms": fixed_radius_u,
            "finite_two_sided_mixed_multiplier_bound_closed": True,
            "unweighted_multiplier_scaling_diagnostic_closed": True,
            "unweighted_cutoff_uniformity_proved": False,
            "energy_weighted_mixed_bound_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
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
    print(f"PRIMARY FINITE-MIXED-FORCE-MOMENTUM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
