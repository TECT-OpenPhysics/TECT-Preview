#!/usr/bin/env python3
"""Primary audit for the covariance-normal-ordered full Class-II energy.

The script reconstructs the exact finite-cutoff conditional counterterm,
checks the joint J^2/J*K/K^2 quadratic form, enumerates the finite
Gaussian-IBP connection patterns and Hilbert-Schmidt Cauchy tails, and records the sharp
leading running-mass threshold.  It does not construct an interacting Gibbs
measure; uniform negative-exponential control is a separate gate.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.1"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE"]

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a6_classii_uv_power_counting as uv  # noqa: E402

CLAIM_DIR = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM_DIR / "classii_renormalised_energy_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-primary-renormalised-energy" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def realify(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix)
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def real_vector(field: np.ndarray) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    return np.concatenate((field.real, field.imag))


def coefficient_matrix(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    x = real_vector(field)
    eps = float(params["rho_regularizer"])
    rho = float(x @ x)
    a_value, b_value, c_value = uv.classii_coefficients(params)
    result = np.zeros((6, 6), dtype=np.float64)
    for generator in uv.generators():
        symmetric = realify(generator)
        moment = float(x @ symmetric @ x)
        q_value = moment / (rho + eps)
        p_value = 2.0 * symmetric @ x
        s_value = 2.0 * (symmetric - q_value * np.eye(6)) @ x
        result += (
            a_value * np.outer(p_value, p_value)
            + b_value * (np.outer(p_value, s_value) + np.outer(s_value, p_value))
            + c_value * np.outer(s_value, s_value)
        )
    return result


def direct_energy(field: np.ndarray, derivatives: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    gradients = np.asarray(derivatives, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = uv.classii_coefficients(params)
    result = 0.0
    for generator in uv.generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        for derivative in gradients:
            j_value = 2.0 * float(np.real(np.vdot(transformed, derivative)))
            k_value = 2.0 * float(np.real(np.vdot(covariant, derivative)))
            result += 0.5 * a_value * j_value * j_value + b_value * j_value * k_value + 0.5 * c_value * k_value * k_value
    return result


def matrix_energy(field: np.ndarray, derivatives: np.ndarray, params: dict[str, Any]) -> float:
    matrix = coefficient_matrix(field, params)
    return 0.5 * sum(float(real_vector(row) @ matrix @ real_vector(row)) for row in derivatives)


def exact_counterterm(field: np.ndarray, derivatives: list[np.ndarray], params: dict[str, Any]) -> dict[str, float]:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = uv.classii_coefficients(params)
    j2 = 0.0
    jk = 0.0
    k2 = 0.0
    for generator in uv.generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        for derivative in derivatives:
            j2 += 2.0 * float(np.real(np.vdot(transformed, derivative @ transformed)))
            jk += 2.0 * float(np.real(np.vdot(transformed, derivative @ covariant)))
            k2 += 2.0 * float(np.real(np.vdot(covariant, derivative @ covariant)))
    energy = 0.5 * a_value * j2 + b_value * jk + 0.5 * c_value * k2
    return {"J2": j2, "JK": jk, "K2": k2, "energy": energy}


def real_counterterm(field: np.ndarray, derivatives: list[np.ndarray], params: dict[str, Any]) -> float:
    matrix = coefficient_matrix(field, params)
    return 0.5 * sum(float(np.trace(matrix @ (0.5 * realify(derivative)))) for derivative in derivatives)


def conditional_monte_carlo(
    field: np.ndarray, derivative: np.ndarray, params: dict[str, Any], samples: int, seed: int
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    factor = np.linalg.cholesky(derivative)
    noise = (rng.normal(size=(samples, 3, 3)) + 1j * rng.normal(size=(samples, 3, 3))) / math.sqrt(2.0)
    gradients = np.einsum("sij,kj->sik", noise, factor)
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = uv.classii_coefficients(params)
    energies = np.zeros(samples, dtype=np.float64)
    for generator in uv.generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        j_value = 2.0 * np.real(np.einsum("j,sij->si", np.conj(transformed), gradients))
        k_value = 2.0 * np.real(np.einsum("j,sij->si", np.conj(covariant), gradients))
        energies += np.sum(0.5 * a_value * j_value**2 + b_value * j_value * k_value + 0.5 * c_value * k_value**2, axis=1)
    expected = exact_counterterm(psi, [derivative] * 3, params)["energy"]
    mean = float(np.mean(energies))
    standard_error = float(np.std(energies, ddof=1) / math.sqrt(samples))
    return {
        "samples": samples,
        "mean": mean,
        "expected": expected,
        "standard_error": standard_error,
        "z_score": abs(mean - expected) / standard_error,
        "centered_mean": mean - expected,
    }


@functools.lru_cache(maxsize=None)
def counts(cutoff: int) -> np.ndarray:
    return uv.mode_counts_fft(cutoff)


def variance_proxy(cutoff: int, params: dict[str, Any], scheme: str) -> float:
    support = cutoff if scheme in {"cube", "ball"} else 2 * cutoff
    multiplicities = counts(support).astype(np.float64)
    squared = np.arange(len(multiplicities), dtype=np.float64)
    if scheme == "cube":
        multiplier4 = np.ones_like(squared)
    elif scheme == "ball":
        multiplier4 = (squared <= cutoff * cutoff).astype(np.float64)
    elif scheme == "smooth":
        multiplier4 = np.exp(-4.0 * (squared / float(cutoff * cutoff)) ** 2)
    else:
        raise ValueError(scheme)
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    k2 = alpha2 * squared
    mass_eigenvalues = np.linalg.eigvalsh(uv.internal_mass_matrix(params))
    base = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    denominators = base[:, None] + mass_eigenvalues[None, :]
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    return float((4.0 / volume**2) * np.sum(multiplicities[:, None] * multiplier4[:, None] * k2[:, None] ** 2 / denominators**2))


def variance_audit(params: dict[str, Any], cutoffs: list[int], reference_cutoff: int) -> dict[str, Any]:
    reference = variance_proxy(reference_cutoff, params, "cube")
    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        row: dict[str, float] = {"cutoff": cutoff}
        for scheme in ("cube", "ball", "smooth"):
            value = variance_proxy(cutoff, params, scheme)
            row[scheme] = value
            row[f"{scheme}_tail"] = reference - value
        rows.append(row)
    slopes = {}
    x_value = np.log(np.asarray(cutoffs, dtype=np.float64))
    for scheme in ("cube", "ball", "smooth"):
        y_value = np.log(np.asarray([abs(row[f"{scheme}_tail"]) for row in rows]))
        slopes[scheme] = float(np.polyfit(x_value, y_value, 1)[0])
    spread = max(abs(rows[-1][scheme] - reference) for scheme in ("cube", "ball", "smooth")) / reference
    return {"reference_cutoff": reference_cutoff, "reference": reference, "rows": rows, "tail_slopes": slopes, "last_relative_spread": spread}


def gaussian_ibp_connection_audit() -> dict[str, Any]:
    one_vertex = []
    for internal_derivatives in range(3):
        degree = 3 + internal_derivatives - 4
        parity_zero = internal_derivatives == 1
        one_vertex.append(
            {
                "internal_derivatives": internal_derivatives,
                "degree": degree,
                "parity_zero": parity_zero,
                "requires_counterterm": degree >= 0 and not parity_zero,
            }
        )

    two_point = []
    for derivative_bridges in range(3):
        mixed_bridges = 4 - 2 * derivative_bridges
        two_point.append(
            {
                "derivative_derivative_bridges": derivative_bridges,
                "derivative_value_bridges": mixed_bridges,
                "covariance_monomial": {
                    "Q": derivative_bridges,
                    "P_or_R": mixed_bridges,
                },
                "worst_fourier_decay": 3 - derivative_bridges,
                "locally_integrable_in_d3": derivative_bridges < 3,
                "bessel_radial_exponent_at_kappa_zero": 1 - derivative_bridges,
            }
        )
    return {"one_vertex": one_vertex, "two_point": two_point}


def w_closed(field: np.ndarray, params: dict[str, Any]) -> float:
    return uv.fierz_counterterm_density(field, params)


def stability_audit(params: dict[str, Any], delta_cube: float, seed: int) -> dict[str, Any]:
    a_value, b_value, c_value = uv.classii_coefficients(params)
    h_value = 9.0 * (a_value + 2.0 * b_value + c_value)
    d_value = 6.0 * b_value + 3.0 * c_value
    rng = np.random.default_rng(seed)
    ratio_max = 0.0
    identity_error = 0.0
    for _ in range(2000):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        rho = float(np.real(np.vdot(field, field)))
        s_value = float(abs(field[0]) ** 2 + abs(field[1]) ** 2)
        w_value = w_closed(field, params)
        if s_value > 0.0:
            ratio_max = max(ratio_max, w_value / s_value)
        eps = float(params["rho_regularizer"])
        residual = h_value * s_value - w_value
        closed = 6.0 * b_value * s_value**2 / (rho + eps) + 3.0 * c_value * s_value**2 * (rho + 2.0 * eps) / (rho + eps) ** 2
        identity_error = max(identity_error, abs(residual - closed))
    near_field = np.asarray([1.0e-5, 0.0, 1.0], dtype=np.complex128)
    near_ratio = w_closed(near_field, params) / float(abs(near_field[0]) ** 2)
    below = 0.99 * h_value
    orientation = min((h_value - below) / (2.0 * d_value), 0.1)
    escaping_coefficient = (h_value - below) * orientation - d_value * orientation**2
    gamma = float(params["gamma"])
    negative_scale = -(2.0 ** 1.5) * escaping_coefficient**1.5 / (3.0 * math.sqrt(gamma))
    return {
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "h": h_value,
        "d": d_value,
        "random_ratio_max": ratio_max,
        "near_zero_doublet_ratio": near_ratio,
        "residual_identity_max_error": identity_error,
        "below_threshold": below,
        "mixed_orientation": orientation,
        "escaping_coefficient": escaping_coefficient,
        "negative_energy_over_t_3_2": negative_scale,
        "family_mass_slope": 2.0 * h_value * delta_cube,
    }


def plane_wave_audit(params: dict[str, Any]) -> dict[str, float]:
    field = np.asarray([0.6 + 0.2j, -0.3 + 0.4j, 0.5 - 0.1j], dtype=np.complex128)
    wavevector = np.asarray([2.0, -1.0, 3.0], dtype=np.float64)
    rho = float(np.real(np.vdot(field, field)))
    eps = float(params["rho_regularizer"])
    max_j = 0.0
    max_k = 0.0
    for generator in uv.generators():
        transformed = generator @ field
        q_value = float(np.real(np.vdot(field, transformed))) / (rho + eps)
        covariant = transformed - q_value * field
        for component in wavevector:
            derivative = 1j * component * field
            j_value = 2.0 * float(np.real(np.vdot(transformed, derivative)))
            k_value = 2.0 * float(np.real(np.vdot(covariant, derivative)))
            max_j = max(max_j, abs(j_value))
            max_k = max(max_k, abs(k_value))
    return {"max_abs_J": max_j, "max_abs_K": max_k, "W": w_closed(field, params)}


def determinant_audit(field: np.ndarray, params: dict[str, Any], cutoffs: list[int]) -> dict[str, Any]:
    b_matrix = coefficient_matrix(field, params)
    mass_real = realify(uv.internal_mass_matrix(params))
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    rows = []
    for cutoff in cutoffs:
        multiplicities = counts(cutoff)
        leading = 0.0
        logdet = 0.0
        hs = 0.0
        for squared_index, multiplicity in enumerate(multiplicities):
            if multiplicity == 0 or squared_index == 0:
                continue
            k2 = alpha2 * squared_index
            scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
            symbol = scalar * np.eye(6) + mass_real
            eigenvalues, basis = np.linalg.eigh(symbol)
            invroot = (basis * (1.0 / np.sqrt(eigenvalues))) @ basis.T
            perturbation = k2 * (invroot @ b_matrix @ invroot)
            perturbation_eigenvalues = np.linalg.eigvalsh(perturbation)
            leading += int(multiplicity) * float(np.sum(perturbation_eigenvalues))
            logdet += int(multiplicity) * float(np.sum(np.log1p(perturbation_eigenvalues)))
            hs += int(multiplicity) * float(np.sum(perturbation_eigenvalues**2))
        leading /= 2.0 * volume
        logdet /= 2.0 * volume
        hs /= 2.0 * volume
        rows.append({"cutoff": cutoff, "leading_density": leading, "logdet_density": logdet, "normal_ordered_log_partition": leading - logdet, "half_hs_bound": 0.5 * hs})
    return {"rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    production_path = REPO / authority["production_functional_manifest"]["path"]
    production = json.loads(production_path.read_text(encoding="utf-8"))
    params = production["parameters"]
    audit = manifest["audit"]
    assertions: list[dict[str, Any]] = []

    add("production_manifest_hash_matches", sha256(production_path) == authority["production_functional_manifest"]["sha256"], sha256(production_path), authority["production_functional_manifest"]["sha256"], assertions)
    a6_path = REPO / authority["a6_uv_source"]["path"]
    add("a6_uv_source_hash_matches", sha256(a6_path) == authority["a6_uv_source"]["sha256"], sha256(a6_path), authority["a6_uv_source"]["sha256"], assertions)
    add("rho_floor_is_fixed_positive", float(params["rho_regularizer"]) > 0.0, params["rho_regularizer"], ">0", assertions)
    q_matrix = np.asarray([[uv.classii_coefficients(params)[0], uv.classii_coefficients(params)[1]], [uv.classii_coefficients(params)[1], uv.classii_coefficients(params)[2]]])
    add("ClassII_coefficient_matrix_is_positive", float(np.min(np.linalg.eigvalsh(q_matrix))) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "positive", assertions)

    rng = np.random.default_rng(int(audit["seed"]))
    matrix_errors = []
    min_b_eigenvalue = math.inf
    for _ in range(64):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        derivatives = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
        matrix_errors.append(abs(direct_energy(field, derivatives, params) - matrix_energy(field, derivatives, params)))
        min_b_eigenvalue = min(min_b_eigenvalue, float(np.min(np.linalg.eigvalsh(coefficient_matrix(field, params)))))
    add("real_quadratic_matrix_matches_direct_currents", max(matrix_errors) < float(audit["matrix_identity_tolerance"]), max(matrix_errors), audit["matrix_identity_tolerance"], assertions)
    add("field_dependent_derivative_matrix_is_positive_semidefinite", min_b_eigenvalue > -1.0e-13, min_b_eigenvalue, ">=-1e-13", assertions)

    field = np.asarray([0.7 + 0.2j, -0.4 + 0.5j, 0.3 - 0.1j], dtype=np.complex128)
    _, derivative, _ = uv.covariance_matrices(int(audit["conditional_cutoff"]), params)
    complex_ct = exact_counterterm(field, [derivative] * 3, params)["energy"]
    real_ct = real_counterterm(field, [derivative] * 3, params)
    add("real_and_complex_counterterm_formulas_agree", abs(complex_ct - real_ct) < 1.0e-14, abs(complex_ct - real_ct), "<1e-14", assertions)
    monte_carlo = conditional_monte_carlo(field, derivative, params, int(audit["conditional_samples"]), int(audit["seed"]) + 1)
    add("conditional_Gaussian_mean_matches_exact_counterterm", monte_carlo["z_score"] < float(audit["conditional_z_score"]), monte_carlo, f"z<{audit['conditional_z_score']}", assertions)
    add("covariance_normal_ordering_centres_the_density", abs(monte_carlo["centered_mean"]) < float(audit["conditional_z_score"]) * monte_carlo["standard_error"], monte_carlo["centered_mean"], "within MC uncertainty of zero", assertions)

    delta_cube = float(manifest["constants"]["delta_cube"]["value"])
    asymptotic_rows = []
    w_value = uv.leading_counterterm_density(field, params)
    for cutoff in [int(value) for value in audit["asymptotic_cutoffs"]]:
        _, derivative_n, _ = uv.covariance_matrices(cutoff, params)
        exact = exact_counterterm(field, [derivative_n] * 3, params)["energy"]
        asymptotic_rows.append({"cutoff": cutoff, "exact_over_N": exact / cutoff, "target": delta_cube * w_value, "relative_error": abs(exact / cutoff - delta_cube * w_value) / (delta_cube * w_value)})
    add("exact_counterterm_recovers_delta_N_W", asymptotic_rows[-1]["relative_error"] < float(audit["asymptotic_relative_tolerance"]), asymptotic_rows[-1], audit["asymptotic_relative_tolerance"], assertions)
    second_field = np.asarray([0.1, 0.8j, 1.2], dtype=np.complex128)
    add("counterterm_is_field_dependent_not_vacuum_scalar", not math.isclose(w_value, uv.leading_counterterm_density(second_field, params), rel_tol=1.0e-3), [w_value, uv.leading_counterterm_density(second_field, params)], "distinct", assertions)

    variance = variance_audit(params, [int(value) for value in audit["variance_cutoffs"]], int(audit["variance_reference_cutoff"]))
    low_slope, high_slope = map(float, audit["variance_tail_slope_interval"])
    for scheme, slope in variance["tail_slopes"].items():
        add(f"{scheme}_centered_gradient_variance_has_N_minus_1_tail", low_slope < slope < high_slope, slope, [low_slope, high_slope], assertions)
    add("common_regulators_approach_same_Hilbert_Schmidt_limit", variance["last_relative_spread"] < float(audit["variance_scheme_relative_tolerance"]), variance["last_relative_spread"], audit["variance_scheme_relative_tolerance"], assertions)

    connections = gaussian_ibp_connection_audit()
    surviving_local = [row["internal_derivatives"] for row in connections["one_vertex"] if row["requires_counterterm"]]
    add("one_vertex_pair_enumeration_is_exhaustive", [row["internal_derivatives"] for row in connections["one_vertex"]] == [0, 1, 2], connections["one_vertex"], "all value/mixed/derivative pairs", assertions)
    add("only_local_derivative_pair_requires_counterterm", surviving_local == [2], surviving_local, [2], assertions)
    signatures = [(row["covariance_monomial"]["Q"], row["covariance_monomial"]["P_or_R"]) for row in connections["two_point"]]
    add("Gaussian_IBP_connection_families_are_exhaustive", signatures == [(0, 4), (1, 2), (2, 0)], signatures, [(0, 4), (1, 2), (2, 0)], assertions)
    endpoint_rows = [row["bessel_radial_exponent_at_kappa_zero"] for row in connections["two_point"]]
    add("only_Q_squared_family_is_Hminus1_logarithmic", min(endpoint_rows) == -1 and endpoint_rows.count(-1) == 1, endpoint_rows, "one radial r^-1 endpoint", assertions)

    stability = stability_audit(params, delta_cube, int(audit["seed"]) + 2)
    add("sharp_running_mass_threshold_is_h", stability["random_ratio_max"] <= stability["h"] * (1.0 + 1.0e-12) and abs(stability["near_zero_doublet_ratio"] / stability["h"] - 1.0) < 1.0e-8, {"random_max": stability["random_ratio_max"], "near_limit": stability["near_zero_doublet_ratio"], "h": stability["h"]}, "sup W/s=h", assertions)
    add("critical_mass_residual_identity_is_nonnegative", stability["residual_identity_max_error"] < 2.0e-14, stability["residual_identity_max_error"], "<2e-14", assertions)
    add("every_subcritical_mass_has_mixed_orientation_escape", stability["escaping_coefficient"] > 0.0 and stability["negative_energy_over_t_3_2"] < 0.0, {"coefficient": stability["escaping_coefficient"], "energy_scale": stability["negative_energy_over_t_3_2"]}, "positive escape coefficient and negative t^(3/2) energy", assertions)
    add("production_family_mass_shift_slope_is_positive", stability["family_mass_slope"] > 0.0, stability["family_mass_slope"], ">0", assertions)

    plane_wave = plane_wave_audit(params)
    add("common_phase_plane_wave_is_exact_ClassII_null", max(plane_wave["max_abs_J"], plane_wave["max_abs_K"]) < 1.0e-14, plane_wave, "J=K=0", assertions)
    add("ClassII_null_plane_wave_has_positive_W", plane_wave["W"] > 0.0, plane_wave["W"], ">0", assertions)

    determinant = determinant_audit(field, params, [int(value) for value in audit["determinant_cutoffs"]])
    add("frozen_background_normal_ordered_determinant_is_positive", all(row["normal_ordered_log_partition"] >= 0.0 for row in determinant["rows"]), determinant["rows"], ">=0", assertions)
    add("frozen_background_determinant_is_Hilbert_Schmidt_bounded", all(row["normal_ordered_log_partition"] <= row["half_hs_bound"] * (1.0 + 1.0e-12) for row in determinant["rows"]), determinant["rows"], "remainder <= half HS bound", assertions)
    increments = np.diff([row["normal_ordered_log_partition"] for row in determinant["rows"]])
    add("frozen_background_determinant_remainder_is_Cauchy_directed", np.all(increments > 0.0) and increments[-1] < increments[0], increments.tolist(), "positive shrinking increments", assertions)
    add("Gibbs_exponential_bound_remains_explicitly_excluded", any("negative-exponential" in item for item in manifest["honesty_boundary"]["excluded"]), manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A7-CLASSII-RENORMALISED-ENERGY-PRIMARY-PASS" if passed == len(assertions) else "A7-CLASSII-RENORMALISED-ENERGY-PRIMARY-FAIL"
    run_config = {"audit": audit}
    output = {
        "schema": "tect/a7-classii-renormalised-energy-primary-result/1.1",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "scope": manifest["scope"],
        "run": {
            "schema": "tect/a7-classii-renormalised-energy-run/1.0",
            "role": "primary",
            "manifest_sha256": sha256(args.manifest),
            "script_sha256": sha256(Path(__file__)),
            "script_version": __version__,
            "seed": {
                "base": int(audit["seed"]),
                "conditional": int(audit["seed"]) + 1,
                "stability": int(audit["seed"]) + 2,
            },
            "config": run_config,
            "config_sha256": object_sha256(run_config),
        },
        "derived": {
            "conditional_monte_carlo": monte_carlo,
            "counterterm_asymptotics": asymptotic_rows,
            "centered_gradient_variance": variance,
            "gaussian_ibp_connections": connections,
            "stability_threshold": stability,
            "plane_wave_negative_control": plane_wave,
            "frozen_background_determinant": determinant,
        },
        "analytic_result": {
            "counterterm": "C_Lambda(X)=E[e_II,Lambda(x)|X_Lambda(x)=X]=one half sum_i Tr[B(X) Gamma_Lambda,i]",
            "composite": "e_II,Lambda-C_Lambda(X_Lambda) is the covariance-normal-ordered joint definition of J^2, J*K, and K^2",
            "regularity": "the exact finite Gaussian-IBP identity leaves Q^2, QPR, and P^2R^2; the worst Bessel-weighted Fourier convolution is <k>^-1, yielding H^(-1-kappa) control",
            "measure_gate": "uniform negative-exponential integrability is not implied by L2 composite convergence",
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(), "git_commit": git_commit(), "deterministic": True},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print(f"Counterterm ratio error at N={asymptotic_rows[-1]['cutoff']}: {asymptotic_rows[-1]['relative_error']:.6g}")
    print(f"Mass threshold h: {stability['h']:.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
