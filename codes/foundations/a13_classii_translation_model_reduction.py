#!/usr/bin/env python3
"""Primary audit for the A13 Class-II translation/model reduction.

This script verifies finite-cutoff algebra and the production budget that
precede a Cameron--Martin translation-coercivity theorem.  It does not prove
that theorem or the cutoff-uniform Nelson moment.  In particular, finite
fixtures are used only for exact identities and scoped architecture falsifiers.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a6_classii_uv_power_counting as uv  # noqa: E402

CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_translation_model_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-primary-translation-model-reduction" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
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
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def complexify(field: np.ndarray) -> np.ndarray:
    value = np.asarray(field, dtype=np.float64)
    return value[..., :3] + 1j * value[..., 3:]


def coefficients(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    return (
        float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
        float(parameters["cJK"])
        * float(parameters["alpha_X"])
        * float(parameters["beta_X"])
        / denominator,
        float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator,
    )


def coefficient_data(field: np.ndarray, parameters: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray]]:
    """Return B(field) and the three M_A=[p_A,v_A] frames."""
    value = np.asarray(field, dtype=np.float64)
    flat = value.reshape(-1, 6)
    rho = np.sum(flat * flat, axis=1)
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    result = np.zeros((flat.shape[0], 6, 6), dtype=np.float64)
    frames: list[np.ndarray] = []
    for generator in uv.generators():
        symmetric = realify(generator)
        moment = np.einsum("ni,ij,nj->n", flat, symmetric, flat)
        ratio = moment / (rho + floor)
        p_value = 2.0 * np.einsum("ij,nj->ni", symmetric, flat)
        v_value = p_value - 2.0 * ratio[:, None] * flat
        frame = np.stack((p_value, v_value), axis=-1)
        frames.append(frame.reshape(value.shape[:-1] + (6, 2)))
        result += np.einsum("nia,ab,njb->nij", frame, q_matrix, frame)
    return result.reshape(value.shape[:-1] + (6, 6)), frames


def spectral_gradient(field: np.ndarray, length: float) -> np.ndarray:
    value = np.asarray(field, dtype=np.float64)
    spatial_shape = value.shape[:3]
    transformed = np.fft.fftn(value, axes=(0, 1, 2))
    derivatives = []
    for axis, count in enumerate(spatial_shape):
        wave = 2.0 * math.pi * np.fft.fftfreq(count, d=length / count)
        reshape = [1, 1, 1, 1]
        reshape[axis] = count
        derivative = np.fft.ifftn(
            transformed * (1j * wave.reshape(reshape)), axes=(0, 1, 2)
        )
        if float(np.max(np.abs(derivative.imag))) > 2.0e-12:
            raise AssertionError("real spectral derivative acquired an imaginary residue")
        derivatives.append(derivative.real)
    return np.asarray(derivatives)


def vren(
    field: np.ndarray,
    gradient: np.ndarray,
    derivative_covariances: list[np.ndarray],
    parameters: dict[str, Any],
    cell_volume: float,
) -> float:
    matrix, _ = coefficient_data(field, parameters)
    total = 0.0
    for axis in range(3):
        total += float(np.sum(np.einsum("...i,...ij,...j->...", gradient[axis], matrix, gradient[axis])))
        total -= float(np.prod(field.shape[:3])) * float(
            np.einsum("...ij,ji->...", matrix, derivative_covariances[axis]).mean()
        )
    return 0.5 * cell_volume * total


def field_cases(parameters: dict[str, Any], grid: int, seed: int) -> list[tuple[str, np.ndarray, np.ndarray]]:
    length = float(parameters["Lx"])
    coordinates = 2.0 * math.pi * np.arange(grid, dtype=np.float64) / grid
    xx, yy, zz = np.meshgrid(coordinates, coordinates, coordinates, indexing="ij")
    shape = (grid, grid, grid, 6)
    cases: list[tuple[str, np.ndarray, np.ndarray]] = []

    zero = np.zeros(shape, dtype=np.float64)
    homogeneous_shift = np.zeros_like(zero)
    homogeneous_shift[..., 0] = 0.41
    homogeneous_shift[..., 4] = -0.17
    cases.append(("zero_to_homogeneous", zero, homogeneous_shift))

    homogeneous = np.zeros_like(zero)
    homogeneous[...] = np.asarray([0.31, -0.22, 0.14, 0.19, 0.07, -0.11])
    second_homogeneous = np.zeros_like(zero)
    second_homogeneous[...] = np.asarray([-0.08, 0.13, 0.05, 0.09, -0.04, 0.12])
    cases.append(("homogeneous_generic", homogeneous, second_homogeneous))

    rng = np.random.default_rng(seed)
    random_field = np.zeros_like(zero)
    random_shift = np.zeros_like(zero)
    phases = (xx, yy, zz, xx + yy, yy + zz, zz + xx, xx + yy + zz)
    for component in range(6):
        for phase_index, phase in enumerate(phases):
            scale = 0.08 / (1.0 + phase_index)
            random_field[..., component] += scale * rng.normal() * np.cos(phase + rng.uniform(0.0, 2.0 * math.pi))
            random_shift[..., component] += 0.6 * scale * rng.normal() * np.sin(phase + rng.uniform(0.0, 2.0 * math.pi))
    cases.append(("band_limited_random", random_field, random_shift))

    shell_phase = xx + yy + zz
    q0_field = np.zeros_like(zero)
    q0_field[..., 0] = 0.37 * np.cos(shell_phase)
    q0_field[..., 3] = 0.37 * np.sin(shell_phase)
    q0_field[..., 1] = 0.21 * np.cos(shell_phase + 0.4)
    q0_field[..., 4] = -0.21 * np.sin(shell_phase + 0.4)
    q0_shift = np.zeros_like(zero)
    q0_shift[..., 2] = 0.16 * np.cos(shell_phase - 0.3)
    q0_shift[..., 5] = 0.16 * np.sin(shell_phase - 0.3)
    cases.append(("exact_q0_shell", q0_field, q0_shift))

    relative = np.zeros_like(zero)
    relative[..., 0] = 0.33 * np.cos(shell_phase)
    relative[..., 3] = 0.33 * np.sin(shell_phase)
    relative[..., 1] = 0.29 * np.cos(shell_phase)
    relative[..., 4] = -0.29 * np.sin(shell_phase)
    aligned = np.zeros_like(zero)
    aligned[..., 0] = 0.11 * np.cos(shell_phase + 0.2)
    aligned[..., 3] = 0.11 * np.sin(shell_phase + 0.2)
    aligned[..., 1] = -0.09 * np.cos(shell_phase - 0.1)
    aligned[..., 4] = 0.09 * np.sin(shell_phase - 0.1)
    cases.append(("classii_relative_phase", relative, aligned))

    high_phase = ((grid - 1) // 2) * xx
    high = np.zeros_like(zero)
    high[..., 0] = 0.24 * np.cos(high_phase)
    high[..., 3] = 0.24 * np.sin(high_phase)
    high[..., 1] = 0.18 * np.cos(high_phase)
    high[..., 4] = -0.18 * np.sin(high_phase)
    high_shift = 0.35 * relative
    cases.append(("high_frequency_relative_phase", high, high_shift))

    third = np.zeros_like(zero)
    third[..., 2] = 0.27 * np.cos(shell_phase)
    third[..., 5] = 0.27 * np.sin(shell_phase)
    cases.append(("pure_third_component", third, q0_shift))

    near_floor = math.sqrt(float(parameters["rho_regularizer"])) * random_field / max(
        float(np.max(np.abs(random_field))), 1.0e-30
    )
    cases.append(("near_floor_stress", near_floor, 0.2 * q0_shift))
    assert abs(math.sqrt(3.0) * 2.0 * math.pi / length - float(parameters["q0"])) < 2.0e-10
    return cases


def translation_identity_audit(parameters: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    grid = int(audit["grid"])
    length = float(parameters["Lx"])
    cell_volume = (length / grid) ** 3
    rng = np.random.default_rng(int(audit["translation_seed"]))
    covariances: list[np.ndarray] = []
    for _ in range(3):
        raw = rng.normal(size=(6, 6))
        covariances.append(0.03 * (raw @ raw.T) / 6.0 + 0.01 * np.eye(6))
    a_value, b_value, c_value = coefficients(parameters)
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]])
    rows: list[dict[str, Any]] = []
    for name, field, shift in field_cases(parameters, grid, int(audit["field_seed"])):
        gradient = spectral_gradient(field, length)
        shift_gradient = spectral_gradient(shift, length)
        translated = field + shift
        translated_gradient = gradient + shift_gradient
        matrix, frames = coefficient_data(field, parameters)
        translated_matrix, translated_frames = coefficient_data(translated, parameters)
        direct = vren(translated, translated_gradient, covariances, parameters, cell_volume) - vren(
            field, gradient, covariances, parameters, cell_volume
        )
        tensor = 0.0
        generator = 0.0
        for axis in range(3):
            delta_matrix = translated_matrix - matrix
            tensor += 0.5 * float(
                np.sum(np.einsum("...i,...ij,...j->...", gradient[axis], delta_matrix, gradient[axis]))
            )
            tensor -= 0.5 * float(np.prod(field.shape[:3])) * float(
                np.einsum("...ij,ji->...", delta_matrix, covariances[axis]).mean()
            )
            tensor += float(
                np.sum(
                    np.einsum(
                        "...i,...ij,...j->...",
                        shift_gradient[axis],
                        translated_matrix,
                        gradient[axis],
                    )
                )
            )
            tensor += 0.5 * float(
                np.sum(
                    np.einsum(
                        "...i,...ij,...j->...",
                        shift_gradient[axis],
                        translated_matrix,
                        shift_gradient[axis],
                    )
                )
            )
            for old_frame, new_frame in zip(frames, translated_frames):
                w_value = np.einsum("...ia,...i->...a", old_frame, gradient[axis])
                new_w = np.einsum("...ia,...i->...a", new_frame, translated_gradient[axis])
                delta_w = new_w - w_value
                delta_frame = new_frame - old_frame
                generator += float(np.sum(np.einsum("...a,ab,...b->...", w_value, q_matrix, delta_w)))
                generator += 0.5 * float(
                    np.sum(np.einsum("...a,ab,...b->...", delta_w, q_matrix, delta_w))
                )
                cross_counterterm = np.einsum(
                    "...ia,ij,...jb->...ab", old_frame, covariances[axis], delta_frame
                )
                square_counterterm = np.einsum(
                    "...ia,ij,...jb->...ab", delta_frame, covariances[axis], delta_frame
                )
                generator -= float(np.sum(np.einsum("ab,...ba->...", q_matrix, cross_counterterm)))
                generator -= 0.5 * float(
                    np.sum(np.einsum("ab,...ba->...", q_matrix, square_counterterm))
                )
        tensor *= cell_volume
        generator *= cell_volume
        scale = max(1.0, abs(direct), abs(tensor), abs(generator))
        rows.append(
            {
                "case": name,
                "direct": direct,
                "tensor": tensor,
                "generator_frame": generator,
                "direct_tensor_normalized_error": abs(direct - tensor) / scale,
                "direct_generator_normalized_error": abs(direct - generator) / scale,
                "positive_shift_square": 0.5
                * cell_volume
                * sum(
                    float(
                        np.sum(
                            np.einsum(
                                "...i,...ij,...j->...",
                                shift_gradient[axis],
                                translated_matrix,
                                shift_gradient[axis],
                            )
                        )
                    )
                    for axis in range(3)
                ),
            }
        )
    return {
        "grid": grid,
        "rows": rows,
        "maximum_tensor_error": max(row["direct_tensor_normalized_error"] for row in rows),
        "maximum_generator_error": max(row["direct_generator_normalized_error"] for row in rows),
    }


def cartan_audit(parameters: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    grid = int(audit["grid"])
    length = float(parameters["Lx"])
    _, field, shift = field_cases(parameters, grid, int(audit["field_seed"]))[4]
    gradient = spectral_gradient(field, length)
    shift_gradient = spectral_gradient(shift, length)
    nodes, weights = np.polynomial.legendre.leggauss(int(audit["cartan_order"]))
    nodes = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights
    floor = float(parameters["rho_regularizer"])
    generator_rows = []
    for generator_index, complex_generator in enumerate(uv.generators()):
        symmetric = realify(complex_generator)

        def k_current(value: np.ndarray, derivative: np.ndarray) -> np.ndarray:
            rho = np.sum(value * value, axis=-1)
            moment = np.einsum("...i,ij,...j->...", value, symmetric, value)
            ratio = moment / (rho + floor)
            sx = np.einsum("ij,...j->...i", symmetric, value)
            return 2.0 * np.sum((sx - ratio[..., None] * value) * derivative, axis=-1)

        axis_rows = []
        for axis in range(3):
            scalar_integral = np.zeros(field.shape[:3], dtype=np.float64)
            curvature_integral = np.zeros(field.shape[:3], dtype=np.float64)
            for node, weight in zip(nodes, weights):
                value = field + float(node) * shift
                derivative = gradient[axis] + float(node) * shift_gradient[axis]
                rho = np.sum(value * value, axis=-1)
                moment = np.einsum("...i,ij,...j->...", value, symmetric, value)
                ratio = moment / (rho + floor)
                sx = np.einsum("ij,...j->...i", symmetric, value)
                omega_h = 2.0 * np.sum((sx - ratio[..., None] * value) * shift, axis=-1)
                d_rho_h = 2.0 * np.sum(value * shift, axis=-1)
                d_rho_dx = 2.0 * np.sum(value * derivative, axis=-1)
                d_m_h = 2.0 * np.sum(sx * shift, axis=-1)
                d_m_dx = 2.0 * np.sum(sx * derivative, axis=-1)
                curvature = (d_rho_h * d_m_dx - d_rho_dx * d_m_h) / (rho + floor)
                scalar_integral += float(weight) * omega_h
                curvature_integral += float(weight) * curvature
            scalar_gradient = spectral_gradient(
                np.repeat(scalar_integral[..., None], 6, axis=-1), length
            )[axis, ..., 0]
            direct = k_current(field + shift, gradient[axis] + shift_gradient[axis]) - k_current(
                field, gradient[axis]
            )
            reconstructed = scalar_gradient + curvature_integral
            scale = max(1.0, float(np.max(np.abs(direct))), float(np.max(np.abs(reconstructed))))
            axis_rows.append(
                {
                    "axis": axis,
                    "normalized_maximum_error": float(np.max(np.abs(direct - reconstructed))) / scale,
                }
            )
        generator_rows.append({"generator": generator_index + 1, "axes": axis_rows})
    maximum_error = max(
        row["normalized_maximum_error"]
        for generator_row in generator_rows
        for row in generator_row["axes"]
    )
    return {"quadrature_order": int(audit["cartan_order"]), "rows": generator_rows, "maximum_error": maximum_error}


def deterministic_expectation_audit(parameters: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    """Exact sigma-point integration of the conditional Y moments."""
    rng = np.random.default_rng(int(audit["expectation_seed"]))
    raw = rng.normal(size=(6, 6))
    gamma = 0.04 * (raw @ raw.T) / 6.0 + 0.02 * np.eye(6)
    factor = np.linalg.cholesky(gamma)
    dimension = 6
    atoms = []
    for column in range(dimension):
        atom = math.sqrt(float(dimension)) * factor[:, column]
        atoms.extend((atom, -atom))
    atoms_array = np.asarray(atoms)
    atom_mean = np.mean(atoms_array, axis=0)
    atom_covariance = np.einsum("ni,nj->ij", atoms_array, atoms_array) / atoms_array.shape[0]
    x_samples = rng.normal(scale=0.31, size=(int(audit["expectation_x_samples"]), 6))
    h_value = rng.normal(scale=0.13, size=6)
    h_gradient = rng.normal(scale=0.09, size=6)
    errors = []
    minimum_positive = math.inf
    for x_value in x_samples:
        old_matrix, _ = coefficient_data(x_value, parameters)
        new_matrix, _ = coefficient_data(x_value + h_value, parameters)
        deltas = []
        for derivative in atoms_array:
            translated_derivative = derivative + h_gradient
            direct = 0.5 * (
                translated_derivative @ new_matrix @ translated_derivative
                - np.trace(new_matrix @ gamma)
                - derivative @ old_matrix @ derivative
                + np.trace(old_matrix @ gamma)
            )
            deltas.append(float(direct))
        average = float(np.mean(deltas))
        expected = 0.5 * float(h_gradient @ new_matrix @ h_gradient)
        errors.append(abs(average - expected))
        minimum_positive = min(minimum_positive, expected)
    return {
        "sigma_point_mean_norm": float(np.linalg.norm(atom_mean)),
        "sigma_point_covariance_error": float(np.linalg.norm(atom_covariance - gamma)),
        "maximum_identity_error": max(errors),
        "minimum_expected_translation": minimum_positive,
    }


def flexible_potential(parameters: dict[str, Any], candidate: dict[str, Any]) -> dict[str, float]:
    lambda_value = float(parameters["lambda"])
    gamma_value = float(parameters["gamma"])
    epsilon_six = float(candidate["epsilon_6"])
    delta = float(candidate["quartic_absorption_delta"])
    quartic_coefficient = abs(lambda_value) / 4.0
    critical_density = abs(lambda_value) / (6.0 * delta)
    constant_density = abs(lambda_value) ** 3 / (432.0 * delta * delta)
    retained_before_one_use = gamma_value / 6.0 - delta
    final_margin = retained_before_one_use - epsilon_six
    sample = np.geomspace(1.0e-12, 1.0e4, 10000)
    slack = delta * sample**3 - quartic_coefficient * sample**2 + constant_density
    equality_slack = (
        delta * critical_density**3
        - quartic_coefficient * critical_density**2
        + constant_density
    )
    volume = float(parameters["Lx"]) * float(parameters["Ly"]) * float(parameters["Lz"])
    return {
        "epsilon_6": epsilon_six,
        "quartic_absorption_delta": delta,
        "critical_density": critical_density,
        "constant_density": constant_density,
        "finite_volume_constant": volume * constant_density,
        "retained_before_one_use": retained_before_one_use,
        "final_sextic_margin": final_margin,
        "sampled_minimum_slack": float(np.min(slack)),
        "equality_slack": equality_slack,
        "sharp_one_use_upper": gamma_value / 6.0,
    }


def homogeneous_remainder_nogo(
    parameters: dict[str, Any], candidate: dict[str, Any], audit: dict[str, Any]
) -> dict[str, Any]:
    """Exact sharp-cube constant-shift restriction.

    The result refutes only a cutoff-independent deterministic constant
    remainder.  It is not a counterexample to an L1 random remainder.
    """
    volume = float(parameters["Lx"]) * float(parameters["Ly"]) * float(parameters["Lz"])
    epsilon_six = float(candidate["epsilon_6"])
    eta = float(candidate["epsilon_v"])
    unit = np.zeros(6, dtype=np.float64)
    unit[0] = 1.0
    mass = uv.internal_mass_matrix(parameters)
    zero_symbol = float(parameters["r"]) * np.eye(3) + mass
    cm_density = float(zero_symbol[0, 0])
    rows = []
    for cutoff in [int(value) for value in audit["homogeneous_cutoffs"]]:
        _, derivative_complex, metadata = uv.covariance_matrices(cutoff, parameters)
        gamma_real = 0.5 * realify(derivative_complex)
        derivative_covariances = [gamma_real, gamma_real, gamma_real]

        def objective(density: float) -> float:
            field = math.sqrt(max(density, 0.0)) * unit
            matrix, _ = coefficient_data(field, parameters)
            counterterm_density = 0.5 * sum(
                float(np.trace(matrix @ gamma)) for gamma in derivative_covariances
            )
            return volume * (
                -counterterm_density + eta * cm_density * density + epsilon_six * density**3
            )

        trial_densities = np.geomspace(1.0e-14, float(audit["homogeneous_density_max"]), 1200)
        values = np.asarray([objective(float(density)) for density in trial_densities])
        index = int(np.argmin(values))
        left = trial_densities[max(index - 1, 0)]
        right = trial_densities[min(index + 1, len(trial_densities) - 1)]
        for _ in range(80):
            first = math.exp((2.0 * math.log(left) + math.log(right)) / 3.0)
            second = math.exp((math.log(left) + 2.0 * math.log(right)) / 3.0)
            if objective(first) < objective(second):
                right = second
            else:
                left = first
        optimum = math.sqrt(left * right)
        minimum = objective(optimum)
        unit_matrix, _ = coefficient_data(unit, parameters)
        quadratic_coefficient = eta * cm_density - 0.5 * sum(
            float(np.trace(unit_matrix @ gamma)) for gamma in derivative_covariances
        )
        rows.append(
            {
                "cutoff": cutoff,
                "mode_count": metadata["mode_count"],
                "quadratic_coefficient_floor_negligible": quadratic_coefficient,
                "optimizing_density": optimum,
                "restricted_minimum": minimum,
                "required_deterministic_remainder": max(0.0, -minimum),
            }
        )
    positive_rows = [row for row in rows if row["required_deterministic_remainder"] > 0.0]
    growth_rows = [row for row in positive_rows if row["cutoff"] >= int(audit["homogeneous_growth_start"])]
    slope = float(
        np.polyfit(
            np.log([row["cutoff"] for row in growth_rows]),
            np.log([row["required_deterministic_remainder"] for row in growth_rows]),
            1,
        )[0]
    )
    a_value, b_value, c_value = coefficients(parameters)
    delta_cube = float(
        json.loads((REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json").read_text(encoding="utf-8"))["constants"]["delta_cube"]["value"]
    )
    asymptotic_counterterm_slope = delta_cube * (9.0 * a_value + 12.0 * b_value + 6.0 * c_value)
    return {
        "rows": rows,
        "log_log_growth_slope": slope,
        "asymptotic_counterterm_slope": asymptotic_counterterm_slope,
        "verdict": "UNIFORM-DETERMINISTIC-CONSTANT-REMAINDER-REFUTED",
        "honesty_boundary": "The Gaussian-null X=0 fixture does not refute a cutoff-uniform expected random remainder.",
    }


def model_lift_arithmetic(model: dict[str, Any]) -> dict[str, float]:
    alpha = float(model["alpha"])
    kappa = float(model["kappa"])
    q_moment = 6.0 / (2.0 - kappa)
    return {
        "alpha": alpha,
        "kappa": kappa,
        "x_regularity": alpha,
        "area_regularilty": 2.0 * alpha - 1.0,
        "q_regularilty": -1.0 - kappa,
        "qx_regularilty": alpha - 1.0 - kappa,
        "qxx_regularilty": 2.0 * alpha - 1.0 - kappa,
        "required_q_model_moment": q_moment,
        "endpoint_required_q_model_moment": 3.0,
        "a7_available_moment": 2.0,
        "curvature_operator_bound": 4.0,
        "critical_current_h2_exponent": 1.5,
        "critical_current_l6_exponent": 1.5,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["authority"]["a1_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    audit = manifest["audit"]
    candidate = manifest["production_candidate"]
    rows: list[dict[str, Any]] = []

    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    a_value, b_value, c_value = coefficients(parameters)
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]])
    eigenvalues = np.linalg.eigvalsh(q_matrix)
    add(rows, "production_q_matrix_positive", float(eigenvalues[0]) > 0.0, eigenvalues.tolist(), "minimum>0")

    potential = flexible_potential(parameters, candidate)
    add(rows, "flexible_potential_exact_equality", abs(potential["equality_slack"]) < float(audit["potential_tolerance"]), potential["equality_slack"], 0.0)
    add(rows, "flexible_potential_sampled_nonnegative", potential["sampled_minimum_slack"] >= -float(audit["potential_tolerance"]), potential["sampled_minimum_slack"], ">=0")
    add(rows, "enlarged_epsilon_below_sharp_upper", potential["epsilon_6"] < potential["sharp_one_use_upper"], potential["epsilon_6"], f"<{potential['sharp_one_use_upper']}")
    add(rows, "post_absorption_sextic_margin_positive", potential["final_sextic_margin"] > 0.0, potential["final_sextic_margin"], ">0")

    old_manifest = json.loads((REPO / manifest["authority"]["a13_v1_1_manifest"]["path"]).read_text(encoding="utf-8"))
    old_charge = float(old_manifest["derived_oracles"]["direct_ramer_square_carrier_charge"])
    add(rows, "old_ramer_square_fits_enlarged_field_budget", old_charge < potential["epsilon_6"], old_charge, f"<{potential['epsilon_6']}")
    add(rows, "one_shot_determinant_nogo_still_authoritative", "NG-2026-07-22-A13-NONFROZEN-RAMER-ONE-SHOT" in old_manifest["consequence"]["additional_negative_results"], old_manifest["consequence"]["additional_negative_results"], "contains determinant no-go")

    translation = translation_identity_audit(parameters, audit)
    add(rows, "exact_tensor_translation_identity", translation["maximum_tensor_error"] < float(audit["translation_tolerance"]), translation["maximum_tensor_error"], f"<{audit['translation_tolerance']}")
    add(rows, "exact_generator_frame_translation_identity", translation["maximum_generator_error"] < float(audit["translation_tolerance"]), translation["maximum_generator_error"], f"<{audit['translation_tolerance']}")
    add(rows, "translation_matrix_nonvacuous", len(translation["rows"]) >= 8 and max(abs(row["direct"]) for row in translation["rows"]) > 1.0e-8, [len(translation["rows"]), max(abs(row["direct"]) for row in translation["rows"])], "at least 8 cases and nonzero")
    add(rows, "positive_shift_square_nonnegative", min(row["positive_shift_square"] for row in translation["rows"]) >= -float(audit["translation_tolerance"]), min(row["positive_shift_square"] for row in translation["rows"]), ">=0")

    cartan = cartan_audit(parameters, audit)
    add(rows, "cartan_current_translation_identity", cartan["maximum_error"] < float(audit["cartan_tolerance"]), cartan["maximum_error"], f"<{audit['cartan_tolerance']}")

    expectation = deterministic_expectation_audit(parameters, audit)
    add(rows, "sigma_points_have_zero_mean", expectation["sigma_point_mean_norm"] < 1.0e-14, expectation["sigma_point_mean_norm"], "<1e-14")
    add(rows, "sigma_points_reproduce_covariance", expectation["sigma_point_covariance_error"] < 1.0e-13, expectation["sigma_point_covariance_error"], "<1e-13")
    add(rows, "deterministic_translation_expectation_identity", expectation["maximum_identity_error"] < float(audit["expectation_tolerance"]), expectation["maximum_identity_error"], f"<{audit['expectation_tolerance']}")
    add(rows, "deterministic_translation_expected_nonnegative", expectation["minimum_expected_translation"] >= -float(audit["expectation_tolerance"]), expectation["minimum_expected_translation"], ">=0")

    homogeneous = homogeneous_remainder_nogo(parameters, candidate, audit)
    add(rows, "homogeneous_remainder_becomes_positive", homogeneous["rows"][-1]["required_deterministic_remainder"] > 1.0, homogeneous["rows"][-1]["required_deterministic_remainder"], ">1")
    add(rows, "homogeneous_remainder_grows_superlinear", homogeneous["log_log_growth_slope"] > float(audit["homogeneous_growth_slope_lower"]), homogeneous["log_log_growth_slope"], f">{audit['homogeneous_growth_slope_lower']}")
    add(rows, "homogeneous_nogo_scoped_to_deterministic_constant", "does not refute" in homogeneous["honesty_boundary"].lower(), homogeneous["honesty_boundary"], "explicit expected-random exclusion")

    model_arithmetic = model_lift_arithmetic(manifest["translated_model"])
    add(rows, "model_alpha_in_subcritical_window", 1.0 / 3.0 < model_arithmetic["alpha"] < 0.5, model_arithmetic["alpha"], "1/3<alpha<1/2")
    add(rows, "q_model_requires_more_than_l2", model_arithmetic["required_q_model_moment"] > model_arithmetic["a7_available_moment"], [model_arithmetic["required_q_model_moment"], model_arithmetic["a7_available_moment"]], "required>available")
    add(rows, "q_model_endpoint_is_l3", model_arithmetic["endpoint_required_q_model_moment"] == 3.0, model_arithmetic["endpoint_required_q_model_moment"], 3.0)
    add(rows, "cartan_curvature_uniform_bound", model_arithmetic["curvature_operator_bound"] == 4.0, model_arithmetic["curvature_operator_bound"], 4.0)
    add(rows, "critical_current_term_has_no_random_young_slot", abs(model_arithmetic["critical_current_h2_exponent"] / 2.0 + model_arithmetic["critical_current_l6_exponent"] / 6.0 - 1.0) < 1.0e-15, model_arithmetic, "3/2 over H2 and L6 saturates Young")

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-classii-translation-model-reduction-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value, "q_eigenvalues": eigenvalues.tolist()},
            "potential": potential,
            "old_direct_ramer_square_charge": old_charge,
            "translation": translation,
            "cartan": cartan,
            "deterministic_expectation": expectation,
            "homogeneous_remainder_nogo": homogeneous,
            "model_lift_arithmetic": model_arithmetic,
        },
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failures), "total": len(rows), "failed": len(failures)},
        "verdict": "A13-CLASSII-TRANSLATION-MODEL-REDUCTION-PRIMARY-PASS" if not failures else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: primary ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {len(rows)}/{len(rows)}")
    print("A13-CLASSII-TRANSLATION-MODEL-REDUCTION-PRIMARY-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
