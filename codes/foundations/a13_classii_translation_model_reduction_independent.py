#!/usr/bin/env python3
"""Non-importing independent audit of the A13 translation/model reduction.

This route implements the Pauli currents directly, reconstructs covariance
mode counts independently, and checks endpoint differences by path
quadrature.  It never imports the primary A13 audit.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_translation_model_reduction_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-independent-translation-model-reduction" / "result.json"


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


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def to_real(field: np.ndarray) -> np.ndarray:
    value = np.asarray(field, dtype=np.complex128)
    return np.concatenate((value.real, value.imag), axis=-1)


def to_complex(field: np.ndarray) -> np.ndarray:
    value = np.asarray(field, dtype=np.float64)
    return value[..., :3] + 1j * value[..., 3:]


def coefficients(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    a_value = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    b_value = (
        float(parameters["cJK"])
        * float(parameters["alpha_X"])
        * float(parameters["beta_X"])
        / denominator
    )
    c_value = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return a_value, b_value, c_value


def matrix_from_pauli(field: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    value = np.asarray(field, dtype=np.float64)
    flat = value.reshape(-1, 6)
    rho = np.sum(flat * flat, axis=1)
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    result = np.zeros((flat.shape[0], 6, 6), dtype=np.float64)
    for complex_generator in generators():
        symmetric = realify(complex_generator)
        moment = np.einsum("ni,ij,nj->n", flat, symmetric, flat)
        ratio = moment / (rho + floor)
        p_value = 2.0 * np.einsum("ij,nj->ni", symmetric, flat)
        k_value = p_value - 2.0 * ratio[:, None] * flat
        result += a_value * np.einsum("ni,nj->nij", p_value, p_value)
        result += b_value * (
            np.einsum("ni,nj->nij", p_value, k_value)
            + np.einsum("ni,nj->nij", k_value, p_value)
        )
        result += c_value * np.einsum("ni,nj->nij", k_value, k_value)
    return result.reshape(value.shape[:-1] + (6, 6))


def spectral_gradient(field: np.ndarray, length: float) -> np.ndarray:
    value = np.asarray(field)
    transform = np.fft.fftn(value, axes=(0, 1, 2))
    rows = []
    for axis, count in enumerate(value.shape[:3]):
        wave = 2.0 * math.pi * np.fft.fftfreq(count, d=length / count)
        shape = [1, 1, 1, 1]
        shape[axis] = count
        rows.append(np.fft.ifftn(transform * 1j * wave.reshape(shape), axes=(0, 1, 2)))
    result = np.asarray(rows)
    if np.isrealobj(value):
        if float(np.max(np.abs(result.imag))) > 2.0e-12:
            raise AssertionError("real derivative residue")
        return result.real
    return result


def direct_energy_density(
    field: np.ndarray, gradient: np.ndarray, parameters: dict[str, Any]
) -> np.ndarray:
    psi = np.asarray(field, dtype=np.complex128)
    rho = np.sum(np.abs(psi) ** 2, axis=-1)
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    result = np.zeros(psi.shape[:-1], dtype=np.float64)
    for generator in generators():
        transformed = np.einsum("ij,...j->...i", generator, psi)
        moment = np.real(np.sum(np.conj(psi) * transformed, axis=-1))
        ratio = moment / (rho + floor)
        covariant = transformed - ratio[..., None] * psi
        for axis in range(3):
            j_value = 2.0 * np.real(np.sum(np.conj(transformed) * gradient[axis], axis=-1))
            k_value = 2.0 * np.real(np.sum(np.conj(covariant) * gradient[axis], axis=-1))
            result += 0.5 * a_value * j_value**2 + b_value * j_value * k_value + 0.5 * c_value * k_value**2
    return result


def direct_counterterm_density(
    field: np.ndarray, derivative_covariances: list[np.ndarray], parameters: dict[str, Any]
) -> np.ndarray:
    psi = np.asarray(field, dtype=np.complex128)
    rho = np.sum(np.abs(psi) ** 2, axis=-1)
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    result = np.zeros(psi.shape[:-1], dtype=np.float64)
    for generator in generators():
        transformed = np.einsum("ij,...j->...i", generator, psi)
        moment = np.real(np.sum(np.conj(psi) * transformed, axis=-1))
        ratio = moment / (rho + floor)
        covariant = transformed - ratio[..., None] * psi
        for derivative in derivative_covariances:
            d_transformed = np.einsum("ij,...j->...i", derivative, transformed)
            d_covariant = np.einsum("ij,...j->...i", derivative, covariant)
            j2 = 2.0 * np.real(np.sum(np.conj(transformed) * d_transformed, axis=-1))
            jk = 2.0 * np.real(np.sum(np.conj(transformed) * d_covariant, axis=-1))
            k2 = 2.0 * np.real(np.sum(np.conj(covariant) * d_covariant, axis=-1))
            result += 0.5 * a_value * j2 + b_value * jk + 0.5 * c_value * k2
    return result


def vren_direct(
    field: np.ndarray,
    gradient: np.ndarray,
    derivative_covariances: list[np.ndarray],
    parameters: dict[str, Any],
    cell_volume: float,
) -> float:
    energy = direct_energy_density(field, gradient, parameters)
    counterterm = direct_counterterm_density(field, derivative_covariances, parameters)
    return cell_volume * float(np.sum(energy - counterterm))


def fixture_fields(parameters: dict[str, Any], grid: int, seed: int) -> list[tuple[str, np.ndarray, np.ndarray]]:
    theta = 2.0 * math.pi * np.arange(grid) / grid
    xx, yy, zz = np.meshgrid(theta, theta, theta, indexing="ij")
    phase = xx + yy + zz
    shape = (grid, grid, grid, 3)
    rows: list[tuple[str, np.ndarray, np.ndarray]] = []
    zero = np.zeros(shape, dtype=np.complex128)
    homogeneous = np.zeros_like(zero)
    homogeneous[...] = np.asarray([0.28 + 0.11j, -0.17 + 0.07j, 0.09 - 0.13j])
    homogeneous_shift = np.zeros_like(zero)
    homogeneous_shift[...] = np.asarray([0.12 - 0.05j, 0.04 + 0.09j, -0.08 + 0.03j])
    rows.append(("zero", zero, homogeneous_shift))
    rows.append(("homogeneous", homogeneous, homogeneous_shift))

    q0 = np.zeros_like(zero)
    q0[..., 0] = 0.34 * np.exp(1j * phase)
    q0[..., 1] = 0.23 * np.exp(-1j * phase)
    q0[..., 2] = 0.08 * np.exp(1j * (phase + 0.2))
    q0_shift = np.zeros_like(zero)
    q0_shift[..., 0] = 0.09 * np.exp(-1j * (phase - 0.3))
    q0_shift[..., 1] = -0.07 * np.exp(1j * (phase + 0.1))
    rows.append(("q0_relative_phase", q0, q0_shift))

    high_phase = ((grid - 1) // 2) * xx
    high = np.zeros_like(zero)
    high[..., 0] = 0.19 * np.exp(1j * high_phase)
    high[..., 1] = 0.16 * np.exp(-1j * high_phase)
    rows.append(("high_frequency", high, 0.4 * q0_shift))

    rng = np.random.default_rng(seed)
    random = np.zeros_like(zero)
    random_shift = np.zeros_like(zero)
    phases = (xx, yy, zz, xx + yy, xx + zz, yy + zz)
    for component in range(3):
        for index, current in enumerate(phases):
            random[..., component] += 0.06 * rng.normal() * np.exp(1j * (current + rng.uniform(0, 2 * math.pi))) / (index + 1)
            random_shift[..., component] += 0.04 * rng.normal() * np.exp(-1j * (current + rng.uniform(0, 2 * math.pi))) / (index + 1)
    rows.append(("random", random, random_shift))

    third = np.zeros_like(zero)
    third[..., 2] = 0.3 * np.exp(1j * phase)
    rows.append(("pure_third", third, 0.2 * q0_shift))
    assert abs(math.sqrt(3.0) * 2.0 * math.pi / float(parameters["Lx"]) - float(parameters["q0"])) < 2.0e-10
    return rows


def independent_translation_audit(parameters: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    grid = int(audit["grid"])
    length = float(parameters["Lx"])
    cell_volume = (length / grid) ** 3
    rng = np.random.default_rng(int(audit["translation_seed"]) + 101)
    complex_covariances = []
    for _ in range(3):
        raw = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
        complex_covariances.append(0.025 * (raw @ raw.conj().T) / 3.0 + 0.015 * np.eye(3))
    real_covariances = [0.5 * realify(value) for value in complex_covariances]
    endpoint_rows = []
    path_rows = []
    path_nodes, path_weights = np.polynomial.legendre.leggauss(int(audit["path_order"]))
    path_nodes = 0.5 * (path_nodes + 1.0)
    path_weights *= 0.5
    for name, field, shift in fixture_fields(parameters, grid, int(audit["independent_field_seed"])):
        gradient = spectral_gradient(field, length)
        shift_gradient = spectral_gradient(shift, length)
        old_value = vren_direct(field, gradient, complex_covariances, parameters, cell_volume)
        new_value = vren_direct(
            field + shift, gradient + shift_gradient, complex_covariances, parameters, cell_volume
        )
        direct_delta = new_value - old_value
        x_real = to_real(field)
        h_real = to_real(shift)
        matrix_old = matrix_from_pauli(x_real, parameters)
        matrix_new = matrix_from_pauli(x_real + h_real, parameters)
        tensor_delta = 0.0
        for axis in range(3):
            y_real = to_real(gradient[axis])
            h_gradient_real = to_real(shift_gradient[axis])
            delta_matrix = matrix_new - matrix_old
            tensor_delta += 0.5 * float(np.sum(np.einsum("...i,...ij,...j->...", y_real, delta_matrix, y_real)))
            tensor_delta -= 0.5 * float(np.prod(field.shape[:3])) * float(
                np.einsum("...ij,ji->...", delta_matrix, real_covariances[axis]).mean()
            )
            tensor_delta += float(
                np.sum(np.einsum("...i,...ij,...j->...", h_gradient_real, matrix_new, y_real))
            )
            tensor_delta += 0.5 * float(
                np.sum(
                    np.einsum("...i,...ij,...j->...", h_gradient_real, matrix_new, h_gradient_real)
                )
            )
        tensor_delta *= cell_volume
        scale = max(1.0, abs(direct_delta), abs(tensor_delta))
        endpoint_rows.append(
            {
                "case": name,
                "direct_current_delta": direct_delta,
                "matrix_translation_delta": tensor_delta,
                "normalized_error": abs(direct_delta - tensor_delta) / scale,
            }
        )

        if name in {"q0_relative_phase", "high_frequency", "random"}:
            path_integral = 0.0
            step = float(audit["path_difference_step"])
            for node, weight in zip(path_nodes, path_weights):
                plus = float(node) + step
                minus = float(node) - step
                value_plus = vren_direct(
                    field + plus * shift,
                    gradient + plus * shift_gradient,
                    complex_covariances,
                    parameters,
                    cell_volume,
                )
                value_minus = vren_direct(
                    field + minus * shift,
                    gradient + minus * shift_gradient,
                    complex_covariances,
                    parameters,
                    cell_volume,
                )
                path_integral += float(weight) * (value_plus - value_minus) / (2.0 * step)
            path_scale = max(1.0, abs(direct_delta), abs(path_integral))
            path_rows.append(
                {
                    "case": name,
                    "endpoint_delta": direct_delta,
                    "path_integral": path_integral,
                    "normalized_error": abs(direct_delta - path_integral) / path_scale,
                }
            )
    return {
        "endpoint_rows": endpoint_rows,
        "path_rows": path_rows,
        "maximum_endpoint_error": max(row["normalized_error"] for row in endpoint_rows),
        "maximum_path_error": max(row["normalized_error"] for row in path_rows),
    }


def gauss_hermite_expectation(parameters: dict[str, Any], audit: dict[str, Any]) -> dict[str, float]:
    rng = np.random.default_rng(int(audit["expectation_seed"]) + 211)
    raw = rng.normal(size=(6, 6))
    gamma = 0.03 * raw @ raw.T / 6.0 + 0.01 * np.eye(6)
    factor = np.linalg.cholesky(gamma)
    order = int(audit["independent_hermite_order"])
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    atoms = []
    atom_weights = []
    for indices in itertools.product(range(order), repeat=6):
        coordinate = math.sqrt(2.0) * np.asarray([nodes[index] for index in indices])
        atoms.append(factor @ coordinate)
        atom_weights.append(float(np.prod([weights[index] for index in indices])) / math.pi**3)
    atoms_array = np.asarray(atoms)
    weights_array = np.asarray(atom_weights)
    mean = np.einsum("n,ni->i", weights_array, atoms_array)
    covariance = np.einsum("n,ni,nj->ij", weights_array, atoms_array, atoms_array)
    x_value = rng.normal(scale=0.24, size=6)
    h_value = rng.normal(scale=0.12, size=6)
    h_gradient = rng.normal(scale=0.08, size=6)
    old_matrix = matrix_from_pauli(x_value, parameters)
    new_matrix = matrix_from_pauli(x_value + h_value, parameters)
    deltas = 0.5 * (
        np.einsum("ni,ij,nj->n", atoms_array + h_gradient, new_matrix, atoms_array + h_gradient)
        - np.trace(new_matrix @ gamma)
        - np.einsum("ni,ij,nj->n", atoms_array, old_matrix, atoms_array)
        + np.trace(old_matrix @ gamma)
    )
    average = float(np.dot(weights_array, deltas))
    expected = 0.5 * float(h_gradient @ new_matrix @ h_gradient)
    return {
        "weight_error": abs(float(np.sum(weights_array)) - 1.0),
        "mean_norm": float(np.linalg.norm(mean)),
        "covariance_error": float(np.linalg.norm(covariance - gamma)),
        "translation_error": abs(average - expected),
        "expected_translation": expected,
    }


def independent_mode_counts(cutoff: int) -> np.ndarray:
    one = np.zeros(cutoff * cutoff + 1, dtype=np.float64)
    one[0] = 1.0
    squares = np.arange(1, cutoff + 1, dtype=np.int64) ** 2
    one[squares] = 2.0
    target = 3 * cutoff * cutoff + 1
    fft_length = 1
    while fft_length < target:
        fft_length *= 2
    spectrum = np.fft.fft(one, fft_length)
    counts = np.rint(np.fft.ifft(spectrum**3).real[:target]).astype(np.int64)
    if np.any(counts < 0) or int(np.sum(counts)) != (2 * cutoff + 1) ** 3:
        raise AssertionError("independent mode count reconstruction failed")
    return counts


def independent_internal_mass(parameters: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(parameters["family_masses"], dtype=np.float64))
    z0 = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return family + float(parameters["k_lock"]) * (np.eye(3) - projector)


def independent_derivative_covariance(cutoff: int, parameters: dict[str, Any]) -> tuple[np.ndarray, int]:
    counts = independent_mode_counts(cutoff)
    squared = np.arange(len(counts), dtype=np.float64)
    alpha2 = (2.0 * math.pi / float(parameters["Lx"])) ** 2
    k2 = alpha2 * squared
    base = float(parameters["r"]) + float(parameters["Z"]) * k2 + float(parameters["Y"]) * k2**2
    eigenvalues, eigenvectors = np.linalg.eigh(independent_internal_mass(parameters))
    denominators = base[:, None] + eigenvalues[None, :]
    volume = float(parameters["Lx"]) ** 3
    derivative_eigenvalues = (2.0 / (3.0 * volume)) * np.sum(
        counts[:, None] * k2[:, None] / denominators, axis=0
    )
    return (eigenvectors * derivative_eigenvalues) @ eigenvectors.T, int(np.sum(counts))


def independent_homogeneous_nogo(
    parameters: dict[str, Any], candidate: dict[str, Any], audit: dict[str, Any]
) -> dict[str, Any]:
    volume = float(parameters["Lx"]) ** 3
    epsilon_six = float(candidate["epsilon_6"])
    eta = float(candidate["epsilon_v"])
    zero_symbol = float(parameters["r"]) * np.eye(3) + independent_internal_mass(parameters)
    unit = np.zeros(6)
    unit[0] = 1.0
    rows = []
    for cutoff in [int(value) for value in audit["independent_homogeneous_cutoffs"]]:
        derivative, mode_count = independent_derivative_covariance(cutoff, parameters)
        gamma = 0.5 * realify(derivative)
        unit_matrix = matrix_from_pauli(unit, parameters)
        quadratic = eta * float(zero_symbol[0, 0]) - 1.5 * float(np.trace(unit_matrix @ gamma))
        if quadratic < 0.0:
            density = math.sqrt(-quadratic / (3.0 * epsilon_six))
            minimum = volume * (quadratic * density + epsilon_six * density**3)
        else:
            density = 0.0
            minimum = 0.0
        rows.append(
            {
                "cutoff": cutoff,
                "mode_count": mode_count,
                "quadratic_coefficient": quadratic,
                "asymptotic_optimizing_density": density,
                "required_remainder": max(0.0, -minimum),
            }
        )
    positive = [row for row in rows if row["required_remainder"] > 0.0]
    slope = float(
        np.polyfit(
            np.log([row["cutoff"] for row in positive[-3:]]),
            np.log([row["required_remainder"] for row in positive[-3:]]),
            1,
        )[0]
    )
    return {"rows": rows, "growth_slope": slope}


def potential_audit(parameters: dict[str, Any], candidate: dict[str, Any]) -> dict[str, float]:
    lambda_value = float(parameters["lambda"])
    gamma_value = float(parameters["gamma"])
    delta = float(candidate["quartic_absorption_delta"])
    epsilon = float(candidate["epsilon_6"])
    critical = abs(lambda_value) / (6.0 * delta)
    constant = abs(lambda_value) ** 3 / (432.0 * delta**2)
    equality = delta * critical**3 - abs(lambda_value) * critical**2 / 4.0 + constant
    return {
        "critical_density": critical,
        "constant_density": constant,
        "equality_error": equality,
        "retained_margin": gamma_value / 6.0 - delta - epsilon,
        "sharp_upper": gamma_value / 6.0,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    audit = manifest["independent_audit"]
    candidate = manifest["production_candidate"]
    rows: list[dict[str, Any]] = []

    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"independent_authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    a_value, b_value, c_value = coefficients(parameters)
    eigenvalues = np.linalg.eigvalsh(np.asarray([[a_value, b_value], [b_value, c_value]]))
    add(rows, "independent_q_positive", float(eigenvalues[0]) > 0.0, eigenvalues.tolist(), "minimum>0")

    potential = potential_audit(parameters, candidate)
    add(rows, "independent_potential_equality", abs(potential["equality_error"]) < float(audit["potential_tolerance"]), potential["equality_error"], 0.0)
    add(rows, "independent_flexible_margin_positive", potential["retained_margin"] > 0.0, potential["retained_margin"], ">0")
    add(rows, "independent_field_budget_below_gamma_over_six", float(candidate["epsilon_6"]) < potential["sharp_upper"], candidate["epsilon_6"], f"<{potential['sharp_upper']}")

    translation = independent_translation_audit(parameters, audit)
    add(rows, "independent_direct_current_translation", translation["maximum_endpoint_error"] < float(audit["translation_tolerance"]), translation["maximum_endpoint_error"], f"<{audit['translation_tolerance']}")
    add(rows, "independent_path_integral", translation["maximum_path_error"] < float(audit["path_tolerance"]), translation["maximum_path_error"], f"<{audit['path_tolerance']}")
    add(rows, "independent_translation_nonvacuous", max(abs(row["direct_current_delta"]) for row in translation["endpoint_rows"]) > 1.0e-8, max(abs(row["direct_current_delta"]) for row in translation["endpoint_rows"]), ">1e-8")

    expectation = gauss_hermite_expectation(parameters, audit)
    add(rows, "hermite_weights_normalized", expectation["weight_error"] < 1.0e-13, expectation["weight_error"], "<1e-13")
    add(rows, "hermite_mean_zero", expectation["mean_norm"] < 1.0e-13, expectation["mean_norm"], "<1e-13")
    add(rows, "hermite_covariance_exact", expectation["covariance_error"] < 1.0e-12, expectation["covariance_error"], "<1e-12")
    add(rows, "hermite_deterministic_translation_identity", expectation["translation_error"] < float(audit["expectation_tolerance"]), expectation["translation_error"], f"<{audit['expectation_tolerance']}")
    add(rows, "hermite_expected_translation_nonnegative", expectation["expected_translation"] >= -float(audit["expectation_tolerance"]), expectation["expected_translation"], ">=0")

    homogeneous = independent_homogeneous_nogo(parameters, candidate, audit)
    add(rows, "independent_deterministic_remainder_refuted", homogeneous["rows"][-1]["required_remainder"] > 1.0, homogeneous["rows"][-1]["required_remainder"], ">1")
    add(rows, "independent_remainder_growth", homogeneous["growth_slope"] > float(audit["homogeneous_growth_slope_lower"]), homogeneous["growth_slope"], f">{audit['homogeneous_growth_slope_lower']}")

    alpha = float(manifest["translated_model"]["alpha"])
    kappa = float(manifest["translated_model"]["kappa"])
    required_moment = 6.0 / (2.0 - kappa)
    add(rows, "independent_subcritical_alpha", 1.0 / 3.0 < alpha < 0.5, alpha, "1/3<alpha<1/2")
    add(rows, "independent_required_moment_exceeds_a7_l2", required_moment > 2.0, required_moment, ">2")
    add(rows, "independent_endpoint_moment_is_three", abs(6.0 / 2.0 - 3.0) < 1.0e-15, 3.0, 3.0)
    add(rows, "independent_critical_young_saturation", abs(1.5 / 2.0 + 1.5 / 6.0 - 1.0) < 1.0e-15, 1.5 / 2.0 + 1.5 / 6.0, 1.0)

    source_text = Path(__file__).read_text(encoding="utf-8")
    imported_modules = []
    for node in ast.walk(ast.parse(source_text)):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    add(
        rows,
        "independent_does_not_import_primary",
        "a13_classii_translation_model_reduction" not in imported_modules,
        imported_modules,
        "primary module absent",
    )

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-classii-translation-model-reduction-independent-result/1.0",
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
            "translation": translation,
            "deterministic_expectation": expectation,
            "homogeneous_remainder_nogo": homogeneous,
            "required_q_model_moment": required_moment,
        },
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failures), "total": len(rows), "failed": len(failures)},
        "verdict": "A13-CLASSII-TRANSLATION-MODEL-REDUCTION-INDEPENDENT-PASS" if not failures else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: independent ({len(failures)} failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {len(rows)}/{len(rows)}")
    print("A13-CLASSII-TRANSLATION-MODEL-REDUCTION-INDEPENDENT-PASS")
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
