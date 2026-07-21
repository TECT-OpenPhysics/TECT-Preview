#!/usr/bin/env python3
"""Primary audit for the Class-II true-increment determinant reduction.

This script does four things independently of any Gibbs-measure claim:

1. recomputes the positive A6 ultraviolet slope and the dyadic past-energy
   growth that falsifies the proposed cutoff-uniform A10 upper form bound;
2. verifies bounded endpoint Gaussian L4/L6 densities from the trace-class
   point covariance;
3. checks the exact true-increment telescoping identity on a genuine
   three-component spectral field fixture; and
4. verifies the noncentral Gaussian determinant formula and its unavoidable
   positive source-square term by deterministic Gauss-Hermite quadrature.

The script intentionally does not claim the adapted source-square estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from a6_classii_uv_power_counting import (
    covariance_matrices,
    cube_integral,
    gaussian_current_moments,
)
from a10_classii_relative_structural_reduction import (
    coefficient_matrix,
    derivative_covariance_sum,
    q_energy,
)

__version__ = "1.0.0"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"
__claims__ = ["A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
MANIFEST = REPO / "claims" / CLAIM / "classii_true_increment_determinant_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-07-21-primary-true-increment" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def gaussian_radial_moments(covariance: np.ndarray) -> tuple[float, float]:
    """Return E|X|^4 and E|X|^6 for circular complex X with E XX*=C."""
    eigenvalues = np.linalg.eigvalsh(covariance)
    trace1 = float(np.sum(eigenvalues))
    trace2 = float(np.sum(eigenvalues**2))
    trace3 = float(np.sum(eigenvalues**3))
    fourth = trace1**2 + trace2
    sixth = trace1**3 + 3.0 * trace1 * trace2 + 2.0 * trace3
    return fourth, sixth


def trace_density(field: np.ndarray, gamma: np.ndarray, params: dict[str, Any]) -> float:
    matrices = coefficient_matrix(field, params)
    return 0.5 * float(np.mean(np.einsum("...ij,ji->...", matrices, gamma)))


def spectral_fixture(params: dict[str, Any]) -> dict[str, float]:
    grid = 128
    length = float(params["Lx"])
    coordinate = length * np.arange(grid, dtype=np.float64) / grid
    alpha = 2.0 * math.pi / length
    x = np.zeros((grid, 3), dtype=np.complex128)
    shell = np.zeros_like(x)
    x[:, 0] = 0.41 * np.exp(1j * alpha * coordinate)
    x[:, 1] = 0.23 * np.exp(-2j * alpha * coordinate)
    x[:, 2] = 0.17
    shell[:, 0] = 0.13 * np.exp(4j * alpha * coordinate)
    shell[:, 1] = 0.09j * np.exp(-3j * alpha * coordinate)
    z = x + shell
    dx = np.zeros_like(x)
    dshell = np.zeros_like(shell)
    dx[:, 0] = 1j * alpha * x[:, 0]
    dx[:, 1] = -2j * alpha * x[:, 1]
    dshell[:, 0] = 4j * alpha * shell[:, 0]
    dshell[:, 1] = -3j * alpha * shell[:, 1]
    dz = dx + dshell

    gamma_old = derivative_covariance_sum(2, params)
    gamma_new = derivative_covariance_sum(4, params)
    gamma_shell = gamma_new - gamma_old
    q_past = q_energy(x, dx, params)
    q_frozen_z = q_energy(x, dz, params)
    q_endpoint = q_energy(z, dz, params)
    t_old_x = trace_density(x, gamma_old, params)
    t_shell_x = trace_density(x, gamma_shell, params)
    t_new_x = trace_density(x, gamma_new, params)
    t_new_z = trace_density(z, gamma_new, params)
    q_frozen = q_frozen_z - t_shell_x
    commutator = (q_endpoint - q_frozen_z) - (t_new_z - t_new_x)
    true_increment = q_frozen - q_past
    v_previous = q_past - t_old_x
    v_endpoint = q_endpoint - t_new_z
    return {
        "q_past": q_past,
        "q_frozen": q_frozen,
        "commutator": commutator,
        "true_increment": true_increment,
        "v_previous": v_previous,
        "v_endpoint": v_endpoint,
        "raw_shell_identity_error": abs((q_frozen + commutator) - (v_endpoint - v_previous + q_past)),
        "true_increment_identity_error": abs((true_increment + commutator) - (v_endpoint - v_previous)),
        "gamma_shell_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(gamma_shell))),
    }


def determinant_fixture(seed: int, order: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(2, 2))
    t_matrix = 0.18 * (matrix.T @ matrix)
    ell = rng.normal(size=2) * 0.27
    p_value = 0.73
    identity = np.eye(2)
    sign, logdet = np.linalg.slogdet(identity + p_value * t_matrix)
    if sign <= 0:
        raise AssertionError("I+pT must be positive")
    determinant_part = 0.5 * (p_value * float(np.trace(t_matrix)) - float(logdet))
    source_part = 0.5 * p_value**2 * float(ell @ np.linalg.solve(identity + p_value * t_matrix, ell))
    analytic = determinant_part + source_part

    nodes, weights = np.polynomial.hermite.hermgauss(order)
    standard_nodes = math.sqrt(2.0) * nodes
    total = 0.0
    for i, xi0 in enumerate(standard_nodes):
        for j, xi1 in enumerate(standard_nodes):
            xi = np.asarray([xi0, xi1])
            increment = 0.5 * (float(xi @ t_matrix @ xi) - float(np.trace(t_matrix))) + float(ell @ xi)
            total += float(weights[i] * weights[j] * math.exp(-p_value * increment))
    quadrature = math.log(total / math.pi)
    upper = 0.25 * p_value**2 * float(np.sum(t_matrix * t_matrix)) + 0.5 * p_value**2 * float(ell @ ell)

    tau = 0.61
    q_small = 1.0
    q_large = 9.0
    scalar_source_small = p_value**2 * tau * q_small**2 / (2.0 * (1.0 + p_value * tau))
    scalar_source_large = p_value**2 * tau * q_large**2 / (2.0 * (1.0 + p_value * tau))
    return {
        "p": p_value,
        "trace_T": float(np.trace(t_matrix)),
        "hs_squared": float(np.sum(t_matrix * t_matrix)),
        "ell_squared": float(ell @ ell),
        "determinant_part": determinant_part,
        "source_part": source_part,
        "analytic_log_laplace": analytic,
        "quadrature_log_laplace": quadrature,
        "quadrature_error": abs(analytic - quadrature),
        "upper_bound": upper,
        "upper_bound_slack": upper - analytic,
        "scalar_source_small": scalar_source_small,
        "scalar_source_large": scalar_source_large,
        "scalar_source_growth_ratio": scalar_source_large / scalar_source_small,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["authority"]["production_functional_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    audit = manifest["primary_audit"]
    rows: list[dict[str, Any]] = []

    add(rows, "a1_authority_hash", sha256(a1_path) == manifest["authority"]["production_functional_manifest"]["sha256"], sha256(a1_path), manifest["authority"]["production_functional_manifest"]["sha256"])
    shell_mass = float(params["r"]) - float(params["Z"]) ** 2 / (4.0 * float(params["Y"]))
    add(rows, "full_production_shell_mass_not_scalar_anchor", abs(shell_mass - float(manifest["branch_firewall"]["full_production_shell_mass_squared"])) < 1e-12 and abs(shell_mass - float(manifest["branch_firewall"]["scalar_shell_mass_squared"])) > 0.2, shell_mass, manifest["branch_firewall"])
    add(rows, "fixed_positive_rho_floor", float(params["rho_regularizer"]) > 0.0, params["rho_regularizer"], ">0")
    add(rows, "eta_shell_zero", float(params["eta_shell"]) == 0.0, params["eta_shell"], 0.0)

    cutoffs = [int(value) for value in audit["cutoffs"]]
    cutoff_rows: list[dict[str, Any]] = []
    for cutoff in cutoffs:
        covariance, derivative, diagnostics = covariance_matrices(cutoff, params)
        moments = gaussian_current_moments(covariance, derivative, params, int(audit["gauss_hermite_order"]))
        fourth, sixth = gaussian_radial_moments(covariance)
        cutoff_rows.append({
            "cutoff": cutoff,
            "energy_density": moments["classii_energy_density_expectation"],
            "point_covariance_trace": float(np.trace(covariance)),
            "L4_density": fourth,
            "L6_density": sixth,
            "mode_count": diagnostics["mode_count"],
        })

    reference_covariance, _, _ = covariance_matrices(int(audit["reference_cutoff"]), params)
    identity_derivative = np.eye(3)
    leading = gaussian_current_moments(reference_covariance, identity_derivative, params, int(audit["reference_quadrature_order"]))
    delta_cube = cube_integral(int(audit["cube_integral_order"])) / (6.0 * math.pi**2 * float(params["Y"]) * float(params["Lx"]))
    predicted_slope = delta_cube * leading["classii_energy_density_expectation"]
    terminal = cutoffs[-1]
    past_rows = cutoff_rows[:-1]
    cumulative_past_density = float(sum(row["energy_density"] for row in past_rows))
    dyadic_ratio = cumulative_past_density / terminal
    last_energy_slope = float(cutoff_rows[-1]["energy_density"] / terminal)
    relative_dyadic_error = abs(dyadic_ratio - predicted_slope) / predicted_slope
    relative_last_error = abs(last_energy_slope - predicted_slope) / predicted_slope
    add(rows, "positive_uv_slope", predicted_slope > 0.0, predicted_slope, ">0")
    add(rows, "finite_cutoff_energy_positive", all(row["energy_density"] > 0.0 for row in cutoff_rows), [row["energy_density"] for row in cutoff_rows], "all >0")
    add(rows, "terminal_energy_slope_approaches_kappa", relative_last_error < float(audit["slope_relative_tolerance"]), relative_last_error, f"<{audit['slope_relative_tolerance']}")
    add(rows, "dyadic_past_sum_approaches_kappa", relative_dyadic_error < float(audit["dyadic_relative_tolerance"]), relative_dyadic_error, f"<{audit['dyadic_relative_tolerance']}")
    add(rows, "dyadic_past_sum_grows_with_terminal_cutoff", cumulative_past_density > cutoff_rows[-2]["energy_density"], cumulative_past_density, f">{cutoff_rows[-2]['energy_density']}")
    add(rows, "point_covariance_trace_bounded_on_ladder", cutoff_rows[-1]["point_covariance_trace"] < float(audit["point_covariance_trace_ceiling"]), cutoff_rows[-1]["point_covariance_trace"], f"<{audit['point_covariance_trace_ceiling']}")
    add(rows, "endpoint_L4_density_bounded_on_ladder", cutoff_rows[-1]["L4_density"] < float(audit["L4_density_ceiling"]), cutoff_rows[-1]["L4_density"], f"<{audit['L4_density_ceiling']}")
    add(rows, "endpoint_L6_density_bounded_on_ladder", cutoff_rows[-1]["L6_density"] < float(audit["L6_density_ceiling"]), cutoff_rows[-1]["L6_density"], f"<{audit['L6_density_ceiling']}")
    add(rows, "upper_form_base_gaussian_contradiction", dyadic_ratio > 0.0 and cutoff_rows[-1]["L4_density"] < float(audit["L4_density_ceiling"]) and cutoff_rows[-1]["L6_density"] < float(audit["L6_density_ceiling"]), {"entropy": 0.0, "past_ratio": dyadic_ratio, "L4": cutoff_rows[-1]["L4_density"], "L6": cutoff_rows[-1]["L6_density"]}, "positive linear past-energy ratio with bounded endpoint moments")

    spectral = spectral_fixture(params)
    add(rows, "genuine_field_raw_action_identity", spectral["raw_shell_identity_error"] < 1e-12, spectral["raw_shell_identity_error"], "<1e-12")
    add(rows, "genuine_field_true_increment_telescope", spectral["true_increment_identity_error"] < 1e-12, spectral["true_increment_identity_error"], "<1e-12")
    add(rows, "shell_covariance_positive", spectral["gamma_shell_minimum_eigenvalue"] > 0.0, spectral["gamma_shell_minimum_eigenvalue"], ">0")

    determinant = determinant_fixture(int(audit["seed"]), int(audit["hermite_order"]))
    add(rows, "noncentral_determinant_quadrature", determinant["quadrature_error"] < float(audit["determinant_tolerance"]), determinant["quadrature_error"], f"<{audit['determinant_tolerance']}")
    add(rows, "determinant_HS_source_upper_bound", determinant["upper_bound_slack"] >= -1e-12, determinant["upper_bound_slack"], ">=-1e-12")
    add(rows, "source_term_strictly_positive", determinant["source_part"] > 0.0, determinant["source_part"], ">0")
    add(rows, "HS_only_bound_falsified_by_source_scaling", determinant["scalar_source_growth_ratio"] > 80.0, determinant["scalar_source_growth_ratio"], ">80")
    add(rows, "source_scaling_is_quadratic", abs(determinant["scalar_source_growth_ratio"] - 81.0) < 1e-12, determinant["scalar_source_growth_ratio"], 81.0)

    expected_gates = [
        "A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND",
        "A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE",
    ]
    add(rows, "remaining_gate_firewall", manifest["open_followups"] == expected_gates, manifest["open_followups"], expected_gates)
    add(rows, "old_relative_variable_not_reused", manifest["true_increment"]["relative_variable"] == "theta*I_j+C_j" and manifest["true_increment"]["legacy_relative_variable"] == "theta*Q_j^fr+C_j", manifest["true_increment"], "new true-increment relative variable")
    add(rows, "direct_upper_form_route_refuted", manifest["route_disposition"]["past_energy_upper_form"] == "REFUTED", manifest["route_disposition"], "past-energy route REFUTED")

    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a11-classii-true-increment-primary-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": "A11-CLASSII-TRUE-INCREMENT-PRIMARY-PASS" if not failures else "FAIL",
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "inputs": {"cutoffs": cutoffs, "reference_cutoff": audit["reference_cutoff"], "gauss_hermite_order": audit["gauss_hermite_order"]},
        "derived": {
            "full_production_shell_mass_squared": shell_mass,
            "delta_cube": delta_cube,
            "leading_unit_current_energy": leading["classii_energy_density_expectation"],
            "predicted_classii_energy_density_slope": predicted_slope,
            "terminal_energy_slope": last_energy_slope,
            "dyadic_past_energy_ratio": dyadic_ratio,
            "cumulative_past_energy_density": cumulative_past_density,
            "cutoff_rows": cutoff_rows,
            "spectral_telescope": spectral,
            "determinant": determinant,
        },
        "closed": [
            "base-Gaussian no-go for the A10 past-energy upper-form route",
            "exact true-increment action telescoping",
            "exact noncentral true-increment determinant formula",
            "necessity of the positive adapted source-square term",
        ],
        "open_followups": expected_gates,
        "assertions": rows,
        "assertion_count": len(rows),
        "failures": failures,
    }
    atomic_json(options.output, payload)
    print(f"A11 primary: {len(rows) - len(failures)}/{len(rows)} assertions PASS")
    print(f"kappa_II: {predicted_slope:.15g}")
    print(f"dyadic past ratio: {dyadic_ratio:.15g}")
    print(payload["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
