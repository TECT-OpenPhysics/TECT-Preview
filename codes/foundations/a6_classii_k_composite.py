#!/usr/bin/env python3
"""Primary audit for the fixed-floor Class-II K composite and split follow-ups.

The script checks the analytic ingredients of the canonical common-even
spectral lift, the exact Pauli/Fierz counterterm algebra, the homogeneous
instability of the literal leading-contraction subtraction, and two local
bare-concentration proxies.  It does not construct a full interacting Gibbs
measure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-K-COMPOSITE-DEFINITION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_k_composite_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-primary-k-composite" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, condition: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected}
    )


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def mass_matrix(params: dict[str, Any]) -> np.ndarray:
    z0 = np.asarray(params["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return np.diag(np.asarray(params["family_masses"], dtype=np.float64)) + float(params["k_lock"]) * (
        np.eye(3) - projector
    )


def component_variance(squared_index: np.ndarray, params: dict[str, Any], component: int = 0) -> np.ndarray:
    eigenvalues, basis = np.linalg.eigh(mass_matrix(params))
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    k2 = alpha2 * np.asarray(squared_index, dtype=np.float64)
    kernel = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2 * k2
    denominators = kernel[:, None] + eigenvalues[None, :]
    if float(np.min(denominators)) <= 0.0:
        raise AssertionError("production quadratic symbol is not positive")
    return np.sum((basis[component, :] ** 2)[None, :] / denominators, axis=1)


def cube_radius_counts(cutoff: int) -> np.ndarray:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    one = np.bincount(axis * axis, minlength=cutoff * cutoff + 1).astype(np.float64)
    target_length = 3 * cutoff * cutoff + 1
    transform_length = 1 << (target_length - 1).bit_length()
    transformed = np.fft.rfft(one, n=transform_length)
    counts = np.rint(np.fft.irfft(transformed**3, n=transform_length)[:target_length]).astype(np.int64)
    if int(counts.sum()) != (2 * cutoff + 1) ** 3:
        raise AssertionError("cube multiplicity reconstruction failed")
    return counts


def area_variance(
    counts: np.ndarray,
    params: dict[str, Any],
    multiplier: Callable[[np.ndarray], np.ndarray] | None = None,
) -> float:
    squared_index = np.arange(len(counts), dtype=np.float64)
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    one_axis_k2 = alpha2 * squared_index / 3.0
    variance = component_variance(squared_index, params)
    weight = np.ones_like(squared_index) if multiplier is None else np.asarray(multiplier(squared_index))
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    return float(np.sum(counts * one_axis_k2 * variance * variance * weight**4) / volume)


def spectral_area_audit(params: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    reference_cutoff = int(audit["area_reference_cutoff"])
    cutoffs = [int(value) for value in audit["area_cutoffs"]]
    reference_counts = cube_radius_counts(reference_cutoff)
    reference = area_variance(reference_counts, params)
    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        counts = cube_radius_counts(cutoff)
        cube_value = area_variance(counts, params)
        ball_value = area_variance(
            counts,
            params,
            lambda squared, n=cutoff: (squared <= float(n * n)).astype(np.float64),
        )
        smooth_value = area_variance(
            reference_counts,
            params,
            lambda squared, n=cutoff: np.exp(-np.power(np.sqrt(squared) / float(n), 8.0)),
        )
        rows.append(
            {
                "cutoff": cutoff,
                "sharp_cube": cube_value,
                "sharp_ball": ball_value,
                "smooth_even": smooth_value,
                "cube_variance_tail": reference - cube_value,
                "ball_variance_tail": reference - ball_value,
                "smooth_variance_tail": reference - smooth_value,
            }
        )
    slope_rows: dict[str, float] = {}
    for key in ("cube_variance_tail", "ball_variance_tail", "smooth_variance_tail"):
        x = np.log(np.asarray([row["cutoff"] for row in rows[-3:]], dtype=np.float64))
        y = np.log(np.asarray([row[key] for row in rows[-3:]], dtype=np.float64))
        slope_rows[key] = float(np.polyfit(x, y, 1)[0])
    return {
        "reference_cutoff": reference_cutoff,
        "reference_variance": reference,
        "rows": rows,
        "variance_tail_slopes": slope_rows,
        "rms_tail_slopes": {key: 0.5 * value for key, value in slope_rows.items()},
    }


def one_form(x: np.ndarray, generator: np.ndarray, eps: float) -> np.ndarray:
    rho = float(x @ x)
    moment = float(x @ generator @ x)
    q_value = moment / (rho + eps)
    return 2.0 * (generator @ x - q_value * x)


def curvature(x: np.ndarray, generator: np.ndarray, eps: float) -> np.ndarray:
    rho = float(x @ x)
    transformed = generator @ x
    return 4.0 * (np.outer(x, transformed) - np.outer(transformed, x)) / (rho + eps)


def finite_difference_curvature(x: np.ndarray, generator: np.ndarray, eps: float, step: float) -> np.ndarray:
    jacobian = np.empty((len(x), len(x)), dtype=np.float64)
    for column in range(len(x)):
        direction = np.zeros_like(x)
        direction[column] = step
        jacobian[:, column] = (
            one_form(x + direction, generator, eps) - one_form(x - direction, generator, eps)
        ) / (2.0 * step)
    return jacobian.T - jacobian


def smooth_chain_rule_audit(eps: float, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    points = rng.normal(size=(64, 6))
    directions = rng.normal(size=(64, 3, 6))
    generator = realify(generators()[1])
    max_chain_error = 0.0
    max_current_error = 0.0
    for x, derivative_rows in zip(points, directions):
        rho = float(x @ x)
        moment = float(x @ generator @ x)
        q_value = moment / (rho + eps)
        omega = one_form(x, generator, eps)
        grad_rho = 2.0 * derivative_rows @ x
        grad_moment = 2.0 * derivative_rows @ (generator @ x)
        grad_q = (grad_moment * (rho + eps) - moment * grad_rho) / (rho + eps) ** 2
        k_one_form = derivative_rows @ omega
        k_chain = (rho + eps) * grad_q
        k_current = grad_moment - q_value * grad_rho
        scale = max(1.0, float(np.max(np.abs(k_one_form))))
        max_chain_error = max(max_chain_error, float(np.max(np.abs(k_one_form - k_chain))) / scale)
        max_current_error = max(max_current_error, float(np.max(np.abs(k_one_form - k_current))) / scale)
    return {"one_form_vs_floor_grad_q": max_chain_error, "one_form_vs_J_minus_q_grad_rho": max_current_error}


def classii_coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def w_generator(field: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = classii_coefficients(params)
    total = 0.0
    for generator in generators():
        transformed = generator @ psi
        moment = float(np.real(np.vdot(psi, transformed)))
        covariant = transformed - moment * psi / (rho + eps)
        total += (
            a_value * float(np.real(np.vdot(transformed, transformed)))
            + 2.0 * b_value * float(np.real(np.vdot(transformed, covariant)))
            + c_value * float(np.real(np.vdot(covariant, covariant)))
        )
    return 3.0 * total


def w_fierz(field: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    s_value = float(abs(psi[0]) ** 2 + abs(psi[1]) ** 2)
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = classii_coefficients(params)
    return float(
        9.0 * (a_value + 2.0 * b_value + c_value) * s_value
        - 6.0 * b_value * s_value**2 / (rho + eps)
        - 3.0 * c_value * s_value**2 * (rho + 2.0 * eps) / (rho + eps) ** 2
    )


def counterterm_audit(params: dict[str, Any], delta_cube: float, seed: int) -> dict[str, Any]:
    a_value, b_value, c_value = classii_coefficients(params)
    coefficient_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    eigenvalues = np.linalg.eigvalsh(coefficient_matrix)
    g_value = a_value + 2.0 * b_value + c_value
    h_value = 9.0 * g_value
    w_infinity = 9.0 * a_value + 12.0 * b_value + 6.0 * c_value
    rng = np.random.default_rng(seed)
    samples = rng.normal(size=(512, 3)) + 1j * rng.normal(size=(512, 3))
    generator_values = np.asarray([w_generator(sample, params) for sample in samples])
    fierz_values = np.asarray([w_fierz(sample, params) for sample in samples])
    s_values = np.sum(np.abs(samples[:, :2]) ** 2, axis=1)
    lower = 9.0 * float(eigenvalues[0]) * s_values
    upper = h_value * s_values

    eps = float(params["rho_regularizer"])
    pure_third = w_fierz(np.asarray([0.0, 0.0, 2.0 + 1.0j]), params)
    first_component = w_fierz(np.asarray([1.0, 0.0, 0.0]), params)

    z0 = np.asarray(params["z0"], dtype=np.float64)
    lock_fraction = 1.0 - float(z0[0] ** 2 / (z0 @ z0))
    quadratic = 0.5 * (
        float(params["r"]) + float(params["family_masses"][0]) + float(params["k_lock"]) * lock_fraction
    )

    def w_e1(rho: float) -> float:
        return float(
            h_value * rho
            - 6.0 * b_value * rho * rho / (rho + eps)
            - 3.0 * c_value * rho * rho * (rho + 2.0 * eps) / (rho + eps) ** 2
        )

    cutoff_rows: list[dict[str, float]] = []
    gamma = float(params["gamma"])
    lam = float(params["lambda"])
    predicted_density_coefficient = (
        -(2.0 / 3.0)
        * delta_cube
        * w_infinity
        * math.sqrt(2.0 * delta_cube * w_infinity / gamma)
    )
    amplitude_coefficient = (2.0 * delta_cube * w_infinity / gamma) ** 0.25
    density_coefficient = math.sqrt(2.0 * delta_cube * w_infinity / gamma)
    for cutoff in (10_000, 1_000_000, 100_000_000, 10_000_000_000):
        t_value = delta_cube * cutoff
        rho_trial = math.sqrt(2.0 * t_value * w_infinity / gamma)
        density = (
            quadratic * rho_trial
            + 0.25 * lam * rho_trial**2
            + (gamma / 6.0) * rho_trial**3
            - t_value * w_e1(rho_trial)
        )
        cutoff_rows.append(
            {
                "cutoff": cutoff,
                "rho_trial": rho_trial,
                "amplitude_trial": math.sqrt(rho_trial),
                "energy_density": density,
                "energy_over_N_3_2": density / cutoff**1.5,
            }
        )
    return {
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "g": g_value,
        "h": h_value,
        "coefficient_eigenvalues": eigenvalues.tolist(),
        "lower_bound_coefficient": 9.0 * float(eigenvalues[0]),
        "w_infinity": w_infinity,
        "fierz_max_absolute_error": float(np.max(np.abs(generator_values - fierz_values))),
        "minimum_lower_margin": float(np.min(generator_values - lower)),
        "minimum_upper_margin": float(np.min(upper - generator_values)),
        "pure_third_W": pure_third,
        "first_component_W": first_component,
        "homogeneous_instability": {
            "quadratic_coefficient": quadratic,
            "amplitude_over_N_quarter_limit": amplitude_coefficient,
            "rho_over_sqrt_N_limit": density_coefficient,
            "energy_density_over_N_3_2_limit": predicted_density_coefficient,
            "rows": cutoff_rows,
        },
    }


def direct_gradient_factor(y: np.ndarray, g_value: float) -> dict[str, Any]:
    matrices = generators()
    linear = np.vstack(
        [2.0 * np.concatenate(((matrix @ y).real, (matrix @ y).imag)) for matrix in matrices]
    )
    covariance = 0.5 * linear @ linear.T
    one_axis = float(np.linalg.det(np.eye(3) + g_value * covariance) ** -0.5)
    direct = one_axis**3
    radius = float(abs(y[0]) ** 2 + abs(y[1]) ** 2)
    closed = (1.0 + 2.0 * g_value * radius) ** -4.5
    return {"covariance": covariance.tolist(), "direct_factor": direct, "closed_factor": closed}


def local_proxy_audit(params: dict[str, Any], delta_cube: float) -> dict[str, Any]:
    a_value, b_value, c_value = classii_coefficients(params)
    g_value = a_value + 2.0 * b_value + c_value
    h_value = 9.0 * g_value
    mean_proxy = {
        "normalization_radial_without_pi2": 1.0 / h_value**2,
        "rescaled_mean_t_s": 2.0 / h_value,
        "rescaled_variance_t_s": 2.0 / h_value**2,
        "mean_N_s": 2.0 / (delta_cube * h_value),
        "limit_law": "Gamma(shape=2, rate=h)",
    }
    beta_normalization = math.gamma(2.0) * math.gamma(2.5) / math.gamma(4.5) / (2.0 * g_value) ** 2
    exact_proxy = {
        "normalization_radial_without_pi2": beta_normalization,
        "closed_normalization": 1.0 / (35.0 * g_value**2),
        "rescaled_mean_t_s": 2.0 / (3.0 * g_value),
        "rescaled_variance_t_s": 14.0 / (9.0 * g_value**2),
        "mean_N_s": 2.0 / (3.0 * delta_cube * g_value),
        "limit_density": "35*g^2*r*(1+2*g*r)^(-9/2)",
    }
    determinant_rows = [
        direct_gradient_factor(np.asarray(vector, dtype=np.complex128), g_value)
        for vector in ([1.0, 0.0, 0.0], [1.0 + 0.5j, -0.25j, 0.0], [0.3, -0.2j, 0.7])
    ]
    return {"mean_contraction_proxy": mean_proxy, "derivative_integrated_proxy": exact_proxy, "determinant_rows": determinant_rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    production_path = REPO / manifest["authority"]["production_functional_manifest"]["path"]
    a6_source_path = REPO / manifest["authority"]["a6_uv_source"]["path"]
    production = json.loads(production_path.read_text(encoding="utf-8"))
    params = production["parameters"]
    audit = manifest["audit"]
    assertions: list[dict[str, Any]] = []

    add(
        "production_manifest_hash_matches",
        sha256(production_path) == manifest["authority"]["production_functional_manifest"]["sha256"],
        sha256(production_path),
        manifest["authority"]["production_functional_manifest"]["sha256"],
        assertions,
    )
    add(
        "a6_uv_source_hash_matches",
        sha256(a6_source_path) == manifest["authority"]["a6_uv_source"]["sha256"],
        sha256(a6_source_path),
        manifest["authority"]["a6_uv_source"]["sha256"],
        assertions,
    )
    eps = float(params["rho_regularizer"])
    add("rho_floor_is_fixed_positive", eps > 0.0, eps, ">0", assertions)

    real_generators = tuple(realify(matrix) for matrix in generators())
    add(
        "realified_generators_are_symmetric",
        all(np.allclose(matrix, matrix.T, rtol=0.0, atol=1.0e-15) for matrix in real_generators),
        "all three",
        "real symmetric",
        assertions,
    )
    x = np.asarray([1.0, 2.0, -0.4, 0.3, -0.2, 0.7], dtype=np.float64)
    analytic_curvature = curvature(x, real_generators[2], eps)
    numeric_curvature = finite_difference_curvature(x, real_generators[2], eps, float(audit["curvature_step"]))
    curvature_error = float(np.max(np.abs(analytic_curvature - numeric_curvature)))
    add("one_form_curvature_formula_matches_finite_difference", curvature_error < float(audit["curvature_tolerance"]), curvature_error, audit["curvature_tolerance"], assertions)
    add("one_form_is_generically_non_exact", float(np.max(np.abs(analytic_curvature))) > 0.1, float(np.max(np.abs(analytic_curvature))), ">0.1", assertions)
    slice_x = np.asarray([1.0, 2.0, 0.0, 0.0, 0.0, 0.0])
    slice_curvature = curvature(slice_x, real_generators[2], eps)[0, 1]
    slice_expected = -8.0 * slice_x[0] * slice_x[1] / (float(slice_x @ slice_x) + eps)
    add("T3_real_slice_curvature_has_expected_sign_and_factor", abs(slice_curvature - slice_expected) < 1.0e-14, slice_curvature, slice_expected, assertions)

    chain = smooth_chain_rule_audit(eps, int(audit["seed"]))
    add("smooth_chain_rule_omega_equals_floor_grad_q", chain["one_form_vs_floor_grad_q"] < 1.0e-12, chain["one_form_vs_floor_grad_q"], "<1e-12", assertions)
    add("smooth_chain_rule_omega_equals_J_minus_q_grad_rho", chain["one_form_vs_J_minus_q_grad_rho"] < 1.0e-12, chain["one_form_vs_J_minus_q_grad_rho"], "<1e-12", assertions)
    pure_third_x = np.asarray([0.0, 0.0, 1.0, 0.0, 0.0, -0.5])
    add("K_one_form_vanishes_on_pure_third_component_subspace", all(np.linalg.norm(one_form(pure_third_x, matrix, eps)) < 1.0e-15 for matrix in real_generators), [np.linalg.norm(one_form(pure_third_x, matrix, eps)) for matrix in real_generators], "all zero", assertions)

    area = spectral_area_audit(params, audit)
    for scheme, slope in area["variance_tail_slopes"].items():
        add(f"{scheme}_has_N_minus_3_tail", -3.8 < slope < -2.2, slope, "between -3.8 and -2.2", assertions)
    for scheme, slope in area["rms_tail_slopes"].items():
        add(f"{scheme}_has_N_minus_3_over_2_rms_tail", -1.9 < slope < -1.1, slope, "between -1.9 and -1.1", assertions)
    last_area = area["rows"][-1]
    scheme_spread = max(last_area[key] for key in ("sharp_cube", "sharp_ball", "smooth_even")) - min(last_area[key] for key in ("sharp_cube", "sharp_ball", "smooth_even"))
    add("admissible_even_regulators_approach_common_area_limit", scheme_spread / area["reference_variance"] < float(audit["scheme_relative_tolerance"]), scheme_spread / area["reference_variance"], audit["scheme_relative_tolerance"], assertions)
    axis = np.arange(-int(audit["odd_sum_cutoff"]), int(audit["odd_sum_cutoff"]) + 1, dtype=np.float64)
    odd_sum = float(np.sum(axis / (1.0 + axis * axis) ** 2))
    add("common_even_regulator_has_zero_value_derivative_contraction", abs(odd_sum) < 1.0e-15, odd_sum, "zero by oddness", assertions)

    delta_cube = float(manifest["constants"]["delta_cube"])
    counterterm = counterterm_audit(params, delta_cube, int(audit["seed"]) + 1)
    add("Pauli_Fierz_W_formula_matches_generator_sum", counterterm["fierz_max_absolute_error"] < 2.0e-14, counterterm["fierz_max_absolute_error"], "<2e-14", assertions)
    add("W_lower_bound_by_9_lambda_min_s", counterterm["minimum_lower_margin"] > -2.0e-14, counterterm["minimum_lower_margin"], ">=-2e-14", assertions)
    add("W_upper_bound_by_h_s", counterterm["minimum_upper_margin"] > -2.0e-14, counterterm["minimum_upper_margin"], ">=-2e-14", assertions)
    add("W_zero_set_contains_exact_pure_third_subspace", abs(counterterm["pure_third_W"]) < 1.0e-15 and counterterm["first_component_W"] > 0.0, {"pure_third": counterterm["pure_third_W"], "first_component": counterterm["first_component_W"]}, "0 and positive", assertions)
    instability = counterterm["homogeneous_instability"]
    last_instability = instability["rows"][-1]["energy_over_N_3_2"]
    instability_error = abs(last_instability - instability["energy_density_over_N_3_2_limit"]) / abs(instability["energy_density_over_N_3_2_limit"])
    add("literal_W_subtraction_has_negative_N_3_over_2_trial_energy", last_instability < 0.0 and instability_error < float(audit["instability_relative_tolerance"]), {"last": last_instability, "limit": instability["energy_density_over_N_3_2_limit"], "relative_error": instability_error}, "negative and converged", assertions)

    proxies = local_proxy_audit(params, delta_cube)
    exact_proxy = proxies["derivative_integrated_proxy"]
    add("beta_prime_normalization_identity", abs(exact_proxy["normalization_radial_without_pi2"] - exact_proxy["closed_normalization"]) < 1.0e-12, {"beta": exact_proxy["normalization_radial_without_pi2"], "closed": exact_proxy["closed_normalization"]}, "absolute error <1e-12", assertions)
    determinant_error = max(abs(row["direct_factor"] - row["closed_factor"]) for row in proxies["determinant_rows"])
    covariance_error = max(float(np.max(np.abs(np.asarray(row["covariance"]) - np.eye(3) * np.trace(np.asarray(row["covariance"])) / 3.0))) for row in proxies["determinant_rows"])
    add("derivative_integrated_proxy_determinant_is_closed_form", determinant_error < 2.0e-14, determinant_error, "<2e-14", assertions)
    add("Pauli_current_covariance_is_isotropic", covariance_error < 2.0e-14, covariance_error, "<2e-14", assertions)
    add("local_proxy_concentration_scales_are_positive", proxies["mean_contraction_proxy"]["mean_N_s"] > 0.0 and exact_proxy["mean_N_s"] > 0.0, {"mean_proxy": proxies["mean_contraction_proxy"]["mean_N_s"], "derivative_proxy": exact_proxy["mean_N_s"]}, "both positive", assertions)
    add("full_field_bare_concentration_remains_explicitly_excluded", "full-field bare concentration theorem" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)
    add("K_square_remains_explicitly_excluded", "renormalised J*K and |K|^2 products" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A6-CLASSII-K-COMPOSITE-PRIMARY-PASS" if passed == len(assertions) else "A6-CLASSII-K-COMPOSITE-PRIMARY-FAIL"
    output = {
        "schema": "tect/a6-classii-k-composite-primary-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "scope": manifest["scope"],
        "theorem_boundary": manifest["theorem_boundary"],
        "derived": {
            "chain_rule": chain,
            "curvature_maximum": float(np.max(np.abs(analytic_curvature))),
            "area_lift": area,
            "counterterm": counterterm,
            "local_proxies": proxies,
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
        },
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print(f"Area-tail slopes: {area['variance_tail_slopes']}")
    print(f"Naive subtraction energy coefficient: {instability['energy_density_over_N_3_2_limit']:.12g}")
    print(f"Local proxy E[N s]: {proxies['mean_contraction_proxy']['mean_N_s']:.12g} / {exact_proxy['mean_N_s']:.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
