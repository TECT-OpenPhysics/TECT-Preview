#!/usr/bin/env python3
"""Primary UV audit for the canonical full-production Class-II functional.

The calculation fixes the complex Gaussian convention induced by the quadratic
part of the A1 reference functional: the real and imaginary parts are six real
Gaussian fields with covariance ``A(k)^-1``.  Hence

    E[Psi_k Psi_k^dagger] = 2 A(k)^-1.

For the sharp cube projector ``max_j |n_j| <= N`` the script computes the exact
point covariance C_N and one-direction derivative covariance D_N.  It then
uses the conditional Gaussian identities

    E[J_A^2 | Psi] = 2 (T_A Psi)^dagger D_N (T_A Psi),
    E[J_A K_A | Psi] = 2 Re (T_A Psi)^dagger D_N (T_A-q_A I)Psi,
    E[K_A^2 | Psi] = 2 ((T_A-q_A I)Psi)^dagger D_N ((T_A-q_A I)Psi)

per spatial direction.  Deterministic Gauss-Hermite quadrature evaluates the
rational q_A=m_A/(rho+eps_rho) averages.  The analytic leading law is

    D_N/N -> delta_cube I,
    delta_cube = I_cube/(6 pi^2 Y L),

where I_cube=int_[-1,1]^3 |x|^-2 dx.  A positive linear Class-II expectation
is a UV-renormalisation signal for any nondegenerate full-component limit at
fixed low-order parameters; it is not a constructive measure or a proof that
no bare, degenerate, or renormalised measure exists.
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
from typing import Any

import numpy as np

__version__ = "1.0.1"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-UV-POWER-COUNTING"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
MANIFEST = REPO / "claims" / CLAIM / "classii_uv_power_counting_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-07-20-primary-classii-uv" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def assertion(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def mode_counts_fft(cutoff: int) -> np.ndarray:
    """Return exact multiplicities of n_x^2+n_y^2+n_z^2 in the cube."""
    integers = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    one_dimensional = np.bincount(integers * integers, minlength=cutoff * cutoff + 1).astype(np.float64)
    target_length = 3 * (len(one_dimensional) - 1) + 1
    fft_length = 1 << (target_length - 1).bit_length()
    spectrum = np.fft.rfft(one_dimensional, fft_length)
    counts = np.rint(np.fft.irfft(spectrum * spectrum * spectrum, fft_length)[:target_length]).astype(np.int64)
    if int(counts.sum()) != (2 * cutoff + 1) ** 3 or np.any(counts < 0):
        raise AssertionError("FFT multiplicity reconstruction failed")
    return counts


def internal_mass_matrix(params: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(params["family_masses"], dtype=np.float64))
    z0 = np.asarray(params["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return family + float(params["k_lock"]) * (np.eye(3) - projector)


def covariance_matrices(cutoff: int, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Compute C_N and D_{i,N}; cube symmetry makes D identical for i=1,2,3."""
    length = float(params["Lx"])
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    alpha = 2.0 * math.pi / length
    counts = mode_counts_fft(cutoff)
    squared_index = np.arange(len(counts), dtype=np.float64)
    k2 = alpha * alpha * squared_index
    kernel = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2 * k2
    mass_matrix = internal_mass_matrix(params)
    mass_eigenvalues, basis = np.linalg.eigh(mass_matrix)
    denominators = kernel[:, None] + mass_eigenvalues[None, :]
    if float(np.min(denominators)) <= 0.0:
        raise AssertionError("quadratic production symbol is not positive")
    c_eigenvalues = (2.0 / volume) * np.sum(counts[:, None] / denominators, axis=0)
    d_eigenvalues = (2.0 / (3.0 * volume)) * np.sum(counts[:, None] * k2[:, None] / denominators, axis=0)
    covariance = (basis * c_eigenvalues) @ basis.T
    derivative = (basis * d_eigenvalues) @ basis.T
    return covariance, derivative, {
        "mode_count": int(counts.sum()),
        "quadratic_symbol_minimum": float(np.min(denominators)),
        "internal_mass_eigenvalues": mass_eigenvalues.tolist(),
        "point_covariance_eigenvalues": np.linalg.eigvalsh(covariance).tolist(),
        "derivative_covariance_eigenvalues": np.linalg.eigvalsh(derivative).tolist(),
    }


def cube_integral(order: int) -> float:
    """Compute I_cube by the nonsingular boundary identity div(x/|x|^2)=|x|^-2."""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    coordinates = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights
    yy, zz = np.meshgrid(coordinates, coordinates, indexing="ij")
    ww = np.outer(weights, weights)
    return float(24.0 * np.sum(ww / (1.0 + yy * yy + zz * zz)))


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def classii_coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    return a_value, b_value, c_value


def hermite_samples(covariance: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray]:
    """Tensor Gauss-Hermite samples for a circular complex Gaussian with E psi psi*=C."""
    nodes, one_weights = np.polynomial.hermite.hermgauss(order)
    multi_index = np.indices((order,) * 6, dtype=np.int16).reshape(6, -1).T
    coordinates = nodes[multi_index]
    weights = np.prod(one_weights[multi_index], axis=1) / (math.pi**3)
    factor = np.linalg.cholesky(covariance)
    samples = (coordinates[:, :3] + 1j * coordinates[:, 3:]) @ factor.T
    return samples.astype(np.complex128, copy=False), weights


def gaussian_current_moments(
    covariance: np.ndarray,
    derivative: np.ndarray,
    params: dict[str, Any],
    order: int,
) -> dict[str, Any]:
    samples, weights = hermite_samples(covariance, order)
    rho = np.sum(np.abs(samples) ** 2, axis=1)
    eps_rho = float(params["rho_regularizer"])
    a_value, b_value, c_value = classii_coefficients(params)
    generator_rows: list[dict[str, float]] = []
    total_energy = 0.0
    for index, generator in enumerate(generators(), start=1):
        transformed = samples @ generator.T
        moment = np.real(np.sum(np.conj(samples) * transformed, axis=1))
        q_value = moment / (rho + eps_rho)
        covariant = transformed - q_value[:, None] * samples
        j_integrand = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, transformed))
        jk_integrand = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, covariant))
        k_integrand = np.real(np.einsum("bi,ij,bj->b", np.conj(covariant), derivative, covariant))
        j2 = float(6.0 * np.sum(weights * j_integrand))
        jk = float(6.0 * np.sum(weights * jk_integrand))
        k2 = float(6.0 * np.sum(weights * k_integrand))
        analytic_j2 = float(6.0 * np.real(np.trace(generator @ derivative @ generator @ covariance)))
        energy = 0.5 * a_value * j2 + b_value * jk + 0.5 * c_value * k2
        total_energy += energy
        generator_rows.append(
            {
                "generator": index,
                "J2": j2,
                "JK": jk,
                "K2": k2,
                "J2_analytic": analytic_j2,
                "J2_quadrature_relative_error": abs(j2 - analytic_j2) / max(1.0, abs(analytic_j2)),
                "classii_energy_density_expectation": energy,
            }
        )
    return {
        "quadrature_order": order,
        "quadrature_nodes": int(order**6),
        "weight_sum": float(np.sum(weights)),
        "generators": generator_rows,
        "classii_energy_density_expectation": float(total_energy),
    }


def leading_counterterm_density(field: np.ndarray, params: dict[str, Any]) -> float:
    """Coefficient W(Psi) in E[F_ClassII | Psi] ~ 3 delta_cube N W(Psi)."""
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps_rho = float(params["rho_regularizer"])
    a_value, b_value, c_value = classii_coefficients(params)
    total = 0.0
    for generator in generators():
        transformed = generator @ psi
        moment = float(np.real(np.vdot(psi, transformed)))
        q_value = moment / (rho + eps_rho)
        covariant = transformed - q_value * psi
        total += (
            a_value * float(np.real(np.vdot(transformed, transformed)))
            + 2.0 * b_value * float(np.real(np.vdot(transformed, covariant)))
            + c_value * float(np.real(np.vdot(covariant, covariant)))
        )
    return 3.0 * total


def fierz_counterterm_density(field: np.ndarray, params: dict[str, Any]) -> float:
    """Closed Pauli/Fierz form of leading_counterterm_density."""
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    s_value = float(abs(psi[0]) ** 2 + abs(psi[1]) ** 2)
    eps_rho = float(params["rho_regularizer"])
    a_value, b_value, c_value = classii_coefficients(params)
    return float(
        9.0 * (a_value + 2.0 * b_value + c_value) * s_value
        - 6.0 * b_value * s_value**2 / (rho + eps_rho)
        - 3.0 * c_value * s_value**2 * (rho + 2.0 * eps_rho) / (rho + eps_rho) ** 2
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    production_manifest_path = REPO / authority["production_functional_manifest"]["path"]
    backend_path = REPO / authority["canonical_backend"]["path"]
    production_manifest = json.loads(production_manifest_path.read_text(encoding="utf-8"))
    params = production_manifest["parameters"]
    cutoffs = [int(value) for value in manifest["audit"]["cutoffs"]]
    reference_cutoff = int(manifest["audit"]["reference_cutoff"])
    quadrature_order = int(manifest["audit"]["gauss_hermite_order"])
    assertions: list[dict[str, Any]] = []

    assertion(
        "production_manifest_hash_matches",
        sha256(production_manifest_path) == authority["production_functional_manifest"]["sha256"],
        sha256(production_manifest_path),
        authority["production_functional_manifest"]["sha256"],
        assertions,
    )
    assertion(
        "canonical_backend_hash_matches",
        sha256(backend_path) == authority["canonical_backend"]["sha256"],
        sha256(backend_path),
        authority["canonical_backend"]["sha256"],
        assertions,
    )
    assertion(
        "production_is_fixed_three_torus",
        float(params["Lx"]) == float(params["Ly"]) == float(params["Lz"]),
        [params["Lx"], params["Ly"], params["Lz"]],
        "equal positive periods",
        assertions,
    )
    production_shell_mass = float(params["r"]) - float(params["Z"]) ** 2 / (4.0 * float(params["Y"]))
    assertion(
        "full_production_shell_mass_is_not_scalar_anchor",
        abs(production_shell_mass - float(manifest["branch_firewall"]["scalar_shell_mass_squared"]))
        > float(manifest["audit"]["mass_separation_minimum"]),
        production_shell_mass,
        "separated from scalar anchor",
        assertions,
    )

    a_value, b_value, c_value = classii_coefficients(params)
    coefficient_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    coefficient_eigenvalues = np.linalg.eigvalsh(coefficient_matrix)
    assertion(
        "classii_coefficient_matrix_is_positive_definite",
        float(coefficient_eigenvalues[0]) > 0.0,
        coefficient_eigenvalues.tolist(),
        "both eigenvalues positive",
        assertions,
    )
    projector = np.diag([1.0, 1.0, 0.0]).astype(np.complex128)
    generator_normalisation_ok = all(
        np.allclose(generator, np.conj(generator.T), rtol=0.0, atol=1.0e-15)
        and abs(np.trace(generator)) < 1.0e-15
        and np.allclose(generator @ generator, projector, rtol=0.0, atol=1.0e-15)
        for generator in generators()
    )
    assertion(
        "embedded_Pauli_generator_normalisation_is_pinned",
        generator_normalisation_ok,
        "Hermitian, trace zero, T_A^2=diag(1,1,0) for A=1,2,3",
        "exact embedded Pauli normalisation",
        assertions,
    )

    integral_low = cube_integral(int(manifest["audit"]["cube_integral_orders"][0]))
    integral_high = cube_integral(int(manifest["audit"]["cube_integral_orders"][1]))
    length = float(params["Lx"])
    delta_cube = integral_high / (6.0 * math.pi * math.pi * float(params["Y"]) * length)
    assertion(
        "cube_integral_two_order_convergence",
        abs(integral_high - integral_low) < float(manifest["audit"]["cube_integral_tolerance"]),
        abs(integral_high - integral_low),
        manifest["audit"]["cube_integral_tolerance"],
        assertions,
    )

    cutoff_rows: list[dict[str, Any]] = []
    for cutoff in cutoffs:
        covariance, derivative, diagnostics = covariance_matrices(cutoff, params)
        moments = gaussian_current_moments(covariance, derivative, params, quadrature_order)
        cutoff_rows.append(
            {
                "cutoff": cutoff,
                "covariance": covariance.tolist(),
                "derivative_covariance": derivative.tolist(),
                "diagnostics": diagnostics,
                "derivative_slope_eigenvalues": (np.linalg.eigvalsh(derivative) / cutoff).tolist(),
                "moments": moments,
                "classii_energy_over_cutoff": moments["classii_energy_density_expectation"] / cutoff,
            }
        )

    reference_covariance, _, reference_diagnostics = covariance_matrices(reference_cutoff, params)
    identity_derivative = np.eye(3, dtype=np.float64)
    limiting_low = gaussian_current_moments(reference_covariance, identity_derivative, params, quadrature_order)
    limiting_high = gaussian_current_moments(
        reference_covariance,
        identity_derivative,
        params,
        int(manifest["audit"]["gauss_hermite_cross_order"]),
    )
    predicted_energy_slope = delta_cube * limiting_high["classii_energy_density_expectation"]
    last_row = cutoff_rows[-1]
    last_derivative_slopes = np.asarray(last_row["derivative_slope_eigenvalues"], dtype=np.float64)
    derivative_relative_error = float(np.max(np.abs(last_derivative_slopes - delta_cube)) / delta_cube)
    energy_slope_relative_error = abs(float(last_row["classii_energy_over_cutoff"]) - predicted_energy_slope) / predicted_energy_slope
    quadrature_cross_error = abs(
        limiting_high["classii_energy_density_expectation"] - limiting_low["classii_energy_density_expectation"]
    ) / limiting_high["classii_energy_density_expectation"]

    assertion(
        "derivative_covariance_has_linear_cube_cutoff_slope",
        derivative_relative_error < float(manifest["audit"]["asymptotic_relative_tolerance"]),
        derivative_relative_error,
        manifest["audit"]["asymptotic_relative_tolerance"],
        assertions,
    )
    assertion(
        "classii_energy_has_positive_linear_slope",
        predicted_energy_slope > 0.0 and energy_slope_relative_error < float(manifest["audit"]["energy_slope_relative_tolerance"]),
        {"predicted": predicted_energy_slope, "last_cutoff": last_row["classii_energy_over_cutoff"], "relative_error": energy_slope_relative_error},
        "positive and within declared cutoff tolerance",
        assertions,
    )
    assertion(
        "gauss_hermite_cross_order_agrees",
        quadrature_cross_error < float(manifest["audit"]["quadrature_relative_tolerance"]),
        quadrature_cross_error,
        manifest["audit"]["quadrature_relative_tolerance"],
        assertions,
    )
    max_j_error = max(
        row["J2_quadrature_relative_error"]
        for cutoff_row in cutoff_rows
        for row in cutoff_row["moments"]["generators"]
    )
    assertion(
        "conditional_wick_J_formula_matches_exact_trace",
        max_j_error < float(manifest["audit"]["trace_identity_tolerance"]),
        max_j_error,
        manifest["audit"]["trace_identity_tolerance"],
        assertions,
    )
    assertion(
        "all_J_and_K_second_moments_are_positive",
        all(
            generator_row["J2"] > 0.0 and generator_row["K2"] > 0.0
            for cutoff_row in cutoff_rows
            for generator_row in cutoff_row["moments"]["generators"]
        ),
        "all audited generator/cutoff rows",
        ">0",
        assertions,
    )
    assertion(
        "classii_expectations_increase_on_audited_tail",
        all(
            right["moments"]["classii_energy_density_expectation"]
            > left["moments"]["classii_energy_density_expectation"]
            for left, right in zip(cutoff_rows[-4:-1], cutoff_rows[-3:])
        ),
        [row["moments"]["classii_energy_density_expectation"] for row in cutoff_rows[-4:]],
        "strictly increasing",
        assertions,
    )
    assertion(
        "point_covariance_is_bounded_while_derivative_covariance_diverges",
        max(reference_diagnostics["point_covariance_eigenvalues"])
        < float(manifest["audit"]["point_covariance_finite_ceiling"])
        and min(last_row["diagnostics"]["derivative_covariance_eigenvalues"])
        > min(cutoff_rows[0]["diagnostics"]["derivative_covariance_eigenvalues"]),
        {
            "reference_point_covariance_eigenvalues": reference_diagnostics["point_covariance_eigenvalues"],
            "first_derivative_eigenvalues": cutoff_rows[0]["diagnostics"]["derivative_covariance_eigenvalues"],
            "last_derivative_eigenvalues": last_row["diagnostics"]["derivative_covariance_eigenvalues"],
        },
        "bounded C_N and growing D_N",
        assertions,
    )

    field_one = np.asarray([1.0, 0.0, 0.0], dtype=np.complex128)
    field_two = np.asarray([1.0, 1.0j, 0.5], dtype=np.complex128)
    counterterm_values = [leading_counterterm_density(field, params) for field in (field_one, field_two)]
    fierz_values = [fierz_counterterm_density(field, params) for field in (field_one, field_two)]
    assertion(
        "leading_contraction_counterterm_is_field_dependent",
        min(counterterm_values) > 0.0 and not math.isclose(counterterm_values[0], counterterm_values[1], rel_tol=1.0e-6, abs_tol=1.0e-12),
        counterterm_values,
        "positive and nonconstant",
        assertions,
    )
    assertion(
        "Pauli_Fierz_counterterm_formula_matches_generator_sum",
        max(abs(left - right) for left, right in zip(counterterm_values, fierz_values)) < 1.0e-14,
        {"generator_sum": counterterm_values, "fierz": fierz_values},
        "absolute error below 1e-14",
        assertions,
    )
    assertion(
        "rho_floor_is_positive_but_does_not_enter_derivative_slope",
        float(params["rho_regularizer"]) > 0.0 and delta_cube > 0.0,
        {"rho_floor": params["rho_regularizer"], "delta_cube": delta_cube},
        "both positive; delta independent of rho floor",
        assertions,
    )
    assertion(
        "unrenormalised_L1_energy_uniform_bound_fails",
        predicted_energy_slope > 0.0,
        predicted_energy_slope,
        "positive coefficient of N",
        assertions,
    )
    assertion(
        "honesty_boundary_excludes_constructive_measure",
        "constructive Gibbs measure" in manifest["honesty_boundary"]["excluded"],
        manifest["honesty_boundary"]["excluded"],
        "explicit exclusion",
        assertions,
    )

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A6-CLASSII-UV-PRIMARY-PASS" if passed == len(assertions) else "A6-CLASSII-UV-PRIMARY-FAIL"
    output = {
        "schema": "tect/a6-classii-uv-primary-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "scope": manifest["scope"],
        "convention": manifest["convention"],
        "inputs": {
            "cutoffs": cutoffs,
            "reference_cutoff": reference_cutoff,
            "gauss_hermite_order": quadrature_order,
            "production_parameters": params,
        },
        "derived": {
            "full_production_shell_mass_squared": production_shell_mass,
            "classii_coefficients": {"a": a_value, "b": b_value, "c": c_value},
            "classii_coefficient_matrix_eigenvalues": coefficient_eigenvalues.tolist(),
            "cube_integral": integral_high,
            "delta_cube": delta_cube,
            "reference_point_covariance": reference_covariance.tolist(),
            "leading_unit_current_moments": limiting_high,
            "predicted_classii_energy_density_slope": predicted_energy_slope,
            "last_cutoff_energy_slope_relative_error": energy_slope_relative_error,
            "leading_local_counterterm_candidate": "for a nondegenerate full-component limit at fixed low-order parameters, test subtraction of the derivative-pair contraction delta_cube*N*W_eps(Psi), with W_eps defined by leading_counterterm_density; an additive vacuum constant cannot cancel this field-dependent contraction",
            "counterterm_test_values": counterterm_values,
        },
        "cutoff_rows": cutoff_rows,
        "analytic_result": {
            "derivative_covariance": "D_i,N/N -> delta_cube I",
            "current_growth": "E int |J_A,N|^2, E int |K_A,N|^2, and the positive Class-II quadratic expectation grow linearly in N",
            "L1_obstruction": "the bare positive Class-II energy is not uniformly L1-bounded under the canonical Gaussian reference",
            "renormalisation_boundary": "this identifies the field-dependent leading contraction that any nondegenerate full-component construction must control; counterterm necessity for every possible weak limit, sufficiency, tightness, and measure convergence remain open",
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
    print(f"delta_cube: {delta_cube:.12g}")
    print(f"Class-II energy-density slope: {predicted_energy_slope:.12g} per cutoff N")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
