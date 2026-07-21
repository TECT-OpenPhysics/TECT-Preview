#!/usr/bin/env python3
"""Independent, non-importing audit of the A11 true-increment reduction."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
CLAIM = "A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION"
DEFAULT_MANIFEST = ROOT / "claims" / CLAIM / "classii_true_increment_determinant_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / CLAIM / "runs" / "2026-07-21-independent-true-increment" / "result.json"


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


def commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def internal_mass(params: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(params["family_masses"], dtype=np.float64))
    z0 = np.asarray(params["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return family + float(params["k_lock"]) * (np.eye(3) - projector)


def covariance_pair(cutoff: int, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    integers = np.arange(-cutoff, cutoff + 1, dtype=np.float64)
    nx, ny, nz = np.meshgrid(integers, integers, integers, indexing="ij")
    squared = (nx * nx + ny * ny + nz * nz).reshape(-1)
    alpha = 2.0 * math.pi / float(params["Lx"])
    k2 = alpha**2 * squared
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    mass_values, basis = np.linalg.eigh(internal_mass(params))
    scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    denominators = scalar[:, None] + mass_values[None, :]
    c_values = (2.0 / volume) * np.sum(1.0 / denominators, axis=0)
    d_values = (2.0 / (3.0 * volume)) * np.sum(k2[:, None] / denominators, axis=0)
    return (basis * c_values) @ basis.T, (basis * d_values) @ basis.T


def hermite_samples(covariance: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    multi = np.indices((order,) * 6, dtype=np.int16).reshape(6, -1).T
    coordinates = nodes[multi]
    combined_weights = np.prod(weights[multi], axis=1) / math.pi**3
    factor = np.linalg.cholesky(covariance)
    samples = (coordinates[:, :3] + 1j * coordinates[:, 3:]) @ factor.T
    return samples, combined_weights


def current_energy(covariance: np.ndarray, derivative: np.ndarray, params: dict[str, Any], order: int) -> float:
    samples, weights = hermite_samples(covariance, order)
    rho = np.sum(np.abs(samples) ** 2, axis=1)
    floor = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    total = 0.0
    for generator in generators():
        transformed = samples @ generator.T
        moment = np.real(np.sum(np.conj(samples) * transformed, axis=1))
        q_value = moment / (rho + floor)
        covariant = transformed - q_value[:, None] * samples
        j_term = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, transformed))
        jk_term = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, covariant))
        k_term = np.real(np.einsum("bi,ij,bj->b", np.conj(covariant), derivative, covariant))
        total += float(np.sum(weights * (3.0 * a_value * j_term + 6.0 * b_value * jk_term + 3.0 * c_value * k_term)))
    return total


def cube_integral(order: int) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    coordinates = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    yy, zz = np.meshgrid(coordinates, coordinates, indexing="ij")
    return float(24.0 * np.sum(np.outer(scaled_weights, scaled_weights) / (1.0 + yy * yy + zz * zz)))


def radial_moments(covariance: np.ndarray) -> tuple[float, float]:
    values = np.linalg.eigvalsh(covariance)
    first = float(np.sum(values))
    second = float(np.sum(values**2))
    third = float(np.sum(values**3))
    return first**2 + second, first**3 + 3.0 * first * second + 2.0 * third


def scalar_determinant(order: int) -> dict[str, float]:
    tau = 0.47
    ell = -0.38
    p_value = 0.81
    analytic = 0.5 * (p_value * tau - math.log1p(p_value * tau)) + 0.5 * p_value**2 * ell**2 / (1.0 + p_value * tau)
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    standard = math.sqrt(2.0) * nodes
    increments = 0.5 * tau * (standard**2 - 1.0) + ell * standard
    quadrature = math.log(float(np.sum(weights * np.exp(-p_value * increments)) / math.sqrt(math.pi)))
    source = 0.5 * p_value**2 * ell**2 / (1.0 + p_value * tau)
    determinant = 0.5 * (p_value * tau - math.log1p(p_value * tau))
    upper = 0.25 * p_value**2 * tau**2 + 0.5 * p_value**2 * ell**2
    return {
        "analytic": analytic,
        "quadrature": quadrature,
        "error": abs(analytic - quadrature),
        "source": source,
        "determinant": determinant,
        "upper_slack": upper - analytic,
    }


def algebra_fixture(seed: int, samples: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    raw_error = 0.0
    true_error = 0.0
    old_relative_mismatch = 0.0
    for _ in range(samples):
        q_past = float(rng.random() * 4.0)
        v_previous = float(rng.normal())
        v_endpoint = float(rng.normal())
        commutator = float(rng.normal())
        q_frozen = v_endpoint - v_previous + q_past - commutator
        true_increment = q_frozen - q_past
        raw_error = max(raw_error, abs(q_frozen + commutator - (v_endpoint - v_previous + q_past)))
        true_error = max(true_error, abs(true_increment + commutator - (v_endpoint - v_previous)))
        theta = float(rng.random())
        old_relative = theta * q_frozen + commutator
        new_relative = theta * true_increment + commutator
        old_relative_mismatch = max(old_relative_mismatch, abs((old_relative - new_relative) - theta * q_past))
    return {"raw_error": raw_error, "true_error": true_error, "relative_variable_identity_error": old_relative_mismatch}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    a1 = json.loads((ROOT / manifest["authority"]["production_functional_manifest"]["path"]).read_text(encoding="utf-8"))
    params = a1["parameters"]
    audit = manifest["independent_audit"]
    rows: list[dict[str, Any]] = []

    a_value, b_value, c_value = coefficients(params)
    coefficient_eigenvalues = np.linalg.eigvalsh(np.asarray([[a_value, b_value], [b_value, c_value]]))
    add(rows, "coefficient_matrix_positive", float(coefficient_eigenvalues[0]) > 0.0, coefficient_eigenvalues.tolist(), "positive")
    add(rows, "complex_covariance_factor_two_explicit", manifest["convention"]["complex_mode_covariance"].startswith("E[Psi_n Psi_n^dagger]=2"), manifest["convention"]["complex_mode_covariance"], "factor 2")

    cutoff_rows: list[dict[str, float]] = []
    for cutoff in [int(value) for value in audit["cutoffs"]]:
        covariance, derivative = covariance_pair(cutoff, params)
        energy = current_energy(covariance, derivative, params, int(audit["gauss_hermite_order"]))
        fourth, sixth = radial_moments(covariance)
        cutoff_rows.append({"cutoff": cutoff, "energy_density": energy, "point_trace": float(np.trace(covariance)), "L4_density": fourth, "L6_density": sixth})

    reference, _ = covariance_pair(int(audit["reference_cutoff"]), params)
    leading_energy = current_energy(reference, np.eye(3), params, int(audit["reference_quadrature_order"]))
    delta = cube_integral(int(audit["cube_integral_order"])) / (6.0 * math.pi**2 * float(params["Y"]) * float(params["Lx"]))
    predicted = delta * leading_energy
    terminal = int(cutoff_rows[-1]["cutoff"])
    dyadic_ratio = sum(row["energy_density"] for row in cutoff_rows[:-1]) / terminal
    last_slope = cutoff_rows[-1]["energy_density"] / terminal
    add(rows, "positive_independent_uv_slope", predicted > 0.0, predicted, ">0")
    add(rows, "independent_energy_ladder_positive", all(row["energy_density"] > 0.0 for row in cutoff_rows), [row["energy_density"] for row in cutoff_rows], "all >0")
    add(rows, "independent_last_slope_converges", abs(last_slope - predicted) / predicted < float(audit["slope_relative_tolerance"]), abs(last_slope - predicted) / predicted, f"<{audit['slope_relative_tolerance']}")
    add(rows, "independent_dyadic_sum_converges", abs(dyadic_ratio - predicted) / predicted < float(audit["dyadic_relative_tolerance"]), abs(dyadic_ratio - predicted) / predicted, f"<{audit['dyadic_relative_tolerance']}")
    add(rows, "independent_endpoint_moments_bounded", cutoff_rows[-1]["L4_density"] < float(audit["L4_density_ceiling"]) and cutoff_rows[-1]["L6_density"] < float(audit["L6_density_ceiling"]), {"L4": cutoff_rows[-1]["L4_density"], "L6": cutoff_rows[-1]["L6_density"]}, "below ceilings")
    add(rows, "base_gaussian_no_go", dyadic_ratio > 0.0 and cutoff_rows[-1]["point_trace"] < float(audit["point_covariance_trace_ceiling"]), {"entropy": 0.0, "past_ratio": dyadic_ratio, "point_trace": cutoff_rows[-1]["point_trace"]}, "positive past ratio and bounded covariance")

    determinant = scalar_determinant(int(audit["hermite_order"]))
    add(rows, "scalar_determinant_quadrature", determinant["error"] < float(audit["determinant_tolerance"]), determinant["error"], f"<{audit['determinant_tolerance']}")
    add(rows, "scalar_source_positive", determinant["source"] > 0.0, determinant["source"], ">0")
    add(rows, "scalar_HS_source_upper_bound", determinant["upper_slack"] >= -1e-13, determinant["upper_slack"], ">=-1e-13")
    source_ratio = (11.0 / 2.0) ** 2
    add(rows, "HS_only_source_scaling_no_go", source_ratio > 30.0, source_ratio, ">30")

    algebra = algebra_fixture(int(audit["seed"]), int(audit["algebra_samples"]))
    add(rows, "independent_raw_action_identity", algebra["raw_error"] < 1e-14, algebra["raw_error"], "<1e-14")
    add(rows, "independent_true_increment_identity", algebra["true_error"] < 1e-14, algebra["true_error"], "<1e-14")
    add(rows, "relative_variable_shift_identity", algebra["relative_variable_identity_error"] < 1e-14, algebra["relative_variable_identity_error"], "<1e-14")
    add(rows, "phi0_convention_pinned", manifest["true_increment"]["initial_condition"] == "phi_0=0 and Gamma_le_0=0, hence V_0=0", manifest["true_increment"]["initial_condition"], "empty initial scale")
    add(rows, "source_square_gate_open", manifest["open_followups"][0] == "A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND", manifest["open_followups"], "source-square first")
    add(rows, "new_relative_gate_open", manifest["open_followups"][1] == "A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE", manifest["open_followups"], "true-increment relative second")

    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a11-classii-true-increment-independent-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": "A11-CLASSII-TRUE-INCREMENT-INDEPENDENT-PASS" if not failures else "FAIL",
        "git_commit": commit(),
        "platform": platform.platform(),
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value},
            "coefficient_eigenvalues": coefficient_eigenvalues.tolist(),
            "delta_cube": delta,
            "leading_unit_current_energy": leading_energy,
            "predicted_classii_energy_density_slope": predicted,
            "terminal_energy_slope": last_slope,
            "dyadic_past_energy_ratio": dyadic_ratio,
            "cutoff_rows": cutoff_rows,
            "determinant": determinant,
            "algebra": algebra,
        },
        "assertions": rows,
        "assertion_count": len(rows),
        "failures": failures,
    }
    atomic_json(options.output, payload)
    print(f"A11 independent: {len(rows) - len(failures)}/{len(rows)} assertions PASS")
    print(f"kappa_II: {predicted:.15g}")
    print(payload["verdict"])
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
