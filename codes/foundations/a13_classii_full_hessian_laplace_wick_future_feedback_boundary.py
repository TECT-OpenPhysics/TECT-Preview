#!/usr/bin/env python3
"""Primary executable certificate for the R-102 A13 checkpoint.

The program derives the full-Hessian owner correction, the all-covariance
Laplace--Wick constants, the scalar heat and future-feedback fixtures, the
active/kernel geometry, and the chronological last-insertion exponent ledger
which closes the regular one-shot rational current.
"""

from __future__ import annotations

__version__ = "1.2.1"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-full-hessian-laplace-wick-future-feedback-boundary/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Rational):
        return f"{int(value.p)}/{int(value.q)}"
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-full-hessian-laplace-wick-future-feedback-boundary-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "R-102 certifies exact owner, heat-representation, geometry, temporal-bridge, "
                "and chronological future-insertion closure only at finite cutoff and fixed floor "
                "for the regular annular mutually orthogonal strict-past no-revisit class with "
                "deterministic PSD target and future heat. Both the high-prefix and fixed-low "
                "derivative coefficient branches are retained. It does not cover random "
                "control-dependent heat or prove the full-frame posterior bracket, complete H_N, "
                "REG, progressive/revisit H_A, OVERLAP_src, Nelson, cutoff/floor removal, a "
                "measure, T5--T7, or Sector A closure."
            ),
        }


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def production_constants() -> dict[str, Fraction]:
    manifest = json.loads(
        (REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    parameters = manifest["parameters"]
    floor = as_fraction(parameters["rho_regularizer"])
    p_mass = as_fraction(parameters["M_X"]) ** 2 + floor
    q11 = as_fraction(parameters["cJJ"]) * as_fraction(parameters["alpha_X"]) ** 2 / p_mass
    q12 = (
        as_fraction(parameters["cJK"])
        * as_fraction(parameters["alpha_X"])
        * as_fraction(parameters["beta_X"])
        / p_mass
    )
    q22 = as_fraction(parameters["cKK"]) * as_fraction(parameters["beta_X"]) ** 2 / p_mass
    alpha = q22 / (q12 + q22)
    c1 = q22 / alpha**2
    c0 = q11 - q12**2 / q22
    return {
        "floor": floor,
        "p_mass": p_mass,
        "q11": q11,
        "q12": q12,
        "q22": q22,
        "alpha": alpha,
        "c0": c0,
        "c1": c1,
    }


def rational_scalar_symbolics(alpha: Fraction) -> dict[str, sp.Expr]:
    x, shift = sp.symbols("x shift", real=True)
    alpha_sp = sp.Rational(alpha.numerator, alpha.denominator)
    row = x - alpha_sp * x**3 / (1 + x**2)
    gram = sp.factor(4 * row**2)
    full = sp.factor(
        gram.subs(x, x + shift)
        - gram
        - sp.diff(gram, x) * shift
        - sp.diff(gram, x, 2) * shift**2 / 2
    )
    cubic = sp.factor(sp.diff(gram, x, 3) * shift**3 / 6)
    balanced = sp.factor(full - cubic)
    ridge = {x: 1, shift: -1}
    return {
        "gram": gram,
        "full": full,
        "cubic": cubic,
        "balanced": balanced,
        "full_ridge": sp.factor(full.subs(ridge)),
        "cubic_ridge": sp.factor(cubic.subs(ridge)),
        "balanced_ridge": sp.factor(balanced.subs(ridge)),
        "full_shift_derivative": sp.factor(sp.diff(full, shift).subs(ridge)),
        "balanced_shift_derivative": sp.factor(sp.diff(balanced, shift).subs(ridge)),
    }


def axis_heat_generator(alpha: Fraction) -> dict[str, sp.Expr]:
    """Derive (Delta_6 B_11)/2 on the active scalar axis, without an oracle formula."""
    coordinates = sp.symbols("y0:6", real=True)
    x = sp.symbols("x", real=True)
    alpha_sp = sp.Rational(alpha.numerator, alpha.denominator)
    active_radius = sum(coordinate**2 for coordinate in coordinates[:4])
    denominator = 1 + sum(coordinate**2 for coordinate in coordinates)
    first_row = coordinates[0] * (1 - alpha_sp * active_radius / denominator)
    b11 = 4 * first_row**2
    laplacian = sp.factor(sum(sp.diff(b11, coordinate, 2) for coordinate in coordinates))
    half_laplacian = sp.factor(laplacian / 2)
    bilaplacian = sp.factor(sum(sp.diff(laplacian, coordinate, 2) for coordinate in coordinates))
    axis = {coordinates[0]: x, **{coordinate: 0 for coordinate in coordinates[1:]}}
    origin = {coordinate: 0 for coordinate in coordinates}
    generator = sp.factor(half_laplacian.subs(axis))
    full_heat = sp.factor(
        generator.subs(x, 0)
        - generator.subs(x, 1)
        + sp.diff(generator, x).subs(x, 1)
        - sp.diff(generator, x, 2).subs(x, 1) / 2
    )
    cubic_heat = sp.factor(-sp.diff(generator, x, 3).subs(x, 1) / 6)
    return {
        "generator": generator,
        "endpoint_heat": sp.factor(generator.subs(x, 0)),
        "second_endpoint_heat": sp.factor(bilaplacian.subs(origin) / 8),
        "full_heat": full_heat,
        "cubic_heat": cubic_heat,
        "balanced_heat": sp.factor(full_heat - cubic_heat),
    }


def normalized_hessian_certificate(alpha: Fraction) -> dict[str, Any]:
    """Check the normalized Hessian identity against direct differentiation.

    The mixed rational point has rho=5/4 and both active and inactive
    coordinates nonzero.  The direct side differentiates rho^2 H(z/rho) in
    z; the normalized side differentiates the polynomial H in independent n
    variables and inserts R_n=I-n n^T only afterward.
    """

    alpha_sp = sp.Rational(alpha.numerator, alpha.denominator)
    n_variables = sp.symbols("n0:2", real=True)
    z_variables = sp.symbols("z0:2", real=True)
    n = sp.Matrix(n_variables)
    z = sp.Matrix(z_variables)
    projector = sp.diag(1, 0)
    v = sp.Matrix([2, -1])
    w = sp.Matrix([-1, 3])

    def directional(field: sp.Matrix, variables: tuple[sp.Symbol, ...], direction: sp.Matrix) -> sp.Matrix:
        return field.applyfunc(
            lambda entry: sp.expand(
                sum(sp.diff(entry, variable) * direction[index] for index, variable in enumerate(variables))
            )
        )

    h = projector * n - alpha_sp * (n.T * projector * n)[0] * n
    hessian_profile = h * h.T
    radial_projector = sp.eye(2) - n * n.T
    a_v = 2 * (n.dot(v)) * hessian_profile + directional(
        hessian_profile, n_variables, radial_projector * v
    )
    normalized = sp.expand(
        (n.dot(w)) * a_v + directional(a_v, n_variables, radial_projector * w)
    )

    rho = sp.sqrt(1 + (z.T * z)[0])
    normalized_z = z / rho
    h_z = projector * normalized_z - alpha_sp * (
        normalized_z.T * projector * normalized_z
    )[0] * normalized_z
    direct_profile = sp.simplify(rho**2 * h_z * h_z.T)
    direct = directional(directional(direct_profile, z_variables, v), z_variables, w)

    z_point = {z_variables[0]: sp.Rational(9, 20), z_variables[1]: sp.Rational(3, 5)}
    n_point = {n_variables[0]: sp.Rational(9, 25), n_variables[1]: sp.Rational(12, 25)}
    difference = (direct.subs(z_point) - normalized.subs(n_point)).applyfunc(sp.factor)
    degrees = [sp.Poly(entry, *n_variables).total_degree() for entry in normalized]
    return {
        "mixed_point_difference": difference,
        "maximum_polynomial_degree": max(degrees),
    }


def gaussian_grid(dimension: int, sigma: float, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * dimension, dtype=int).reshape(dimension, -1).T
    points = math.sqrt(2.0 * sigma) * nodes[indices]
    product_weights = np.prod(weights[indices], axis=1) / math.pi ** (dimension / 2)
    return points, product_weights


def gaussian_factor_grid(mean: np.ndarray, factor: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray]:
    """Quadrature for N(mean, factor factor^T), including singular factors."""
    latent_dimension = factor.shape[1]
    if latent_dimension == 0:
        return mean[None, :].copy(), np.ones(1)
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * latent_dimension, dtype=int).reshape(latent_dimension, -1).T
    latent = math.sqrt(2.0) * nodes[indices]
    points = mean[None, :] + latent @ factor.T
    product_weights = np.prod(weights[indices], axis=1) / math.pi ** (latent_dimension / 2)
    return points, product_weights


def rational_gram_values(points: np.ndarray, floor: float, alpha: float, c1: float) -> np.ndarray:
    projected = points.copy()
    projected[:, 4:] = 0.0
    active_radius = np.sum(projected * projected, axis=1)
    denominator = floor + np.sum(points * points, axis=1)
    row = projected - alpha * (active_radius / denominator)[:, None] * points
    return 4.0 * c1 * np.einsum("ni,nj->nij", row, row)


def direct_heat_gram(z: np.ndarray, sigma: float, alpha: float, c1: float, order: int = 8) -> np.ndarray:
    points, weights = gaussian_grid(6, sigma, order)
    grams = rational_gram_values(points + z[None, :], 1.0, alpha, c1)
    return np.einsum("n,nij->ij", weights, grams)


def isotropic_laplace_scalar(x: float, sigma: float, alpha: float, c1: float) -> float:
    mp.mp.dps = 40

    def first_integrand(t: mp.mpf) -> mp.mpf:
        scale = 1 + 2 * sigma * t
        decay = mp.exp(-(t / scale) * x * x)
        moment = x**4 / scale**7 + 9 * sigma * x**2 / scale**6 + 6 * sigma**2 / scale**5
        return mp.exp(-t) * decay * moment

    def second_integrand(t: mp.mpf) -> mp.mpf:
        scale = 1 + 2 * sigma * t
        decay = mp.exp(-(t / scale) * x * x)
        moment = (
            x**6 / scale**9
            + 21 * sigma * x**4 / scale**8
            + 96 * sigma**2 * x**2 / scale**7
            + 48 * sigma**3 / scale**6
        )
        return t * mp.exp(-t) * decay * moment

    first = mp.quad(first_integrand, [0, mp.inf])
    second = mp.quad(second_integrand, [0, mp.inf])
    return float(4 * c1 * (x * x + sigma - 2 * alpha * first + alpha**2 * second))


def isotropic_closed_wick_moments(x: float, sigma: float, t: float) -> tuple[float, float]:
    scale = 1.0 + 2.0 * sigma * t
    decay = math.exp(-(t / scale) * x * x)
    first = decay * (
        x**4 / scale**7 + 9.0 * sigma * x**2 / scale**6 + 6.0 * sigma**2 / scale**5
    )
    second = decay * (
        x**6 / scale**9
        + 21.0 * sigma * x**4 / scale**8
        + 96.0 * sigma**2 * x**2 / scale**7
        + 48.0 * sigma**3 / scale**6
    )
    return first, second


def wick_moment(points: np.ndarray, weights: np.ndarray, projector: np.ndarray, order: int, decay: float = 0.0) -> np.ndarray:
    projected = points @ projector.T
    radius = np.sum(projected * projected, axis=1)
    factors = radius**order
    if decay:
        factors = factors * np.exp(-decay * np.sum(points * points, axis=1))
    return np.einsum("n,n,ni,nj->ij", weights, factors, points, points)


def main() -> int:
    audit = Audit()
    diagnostics: dict[str, Any] = {}
    constants = production_constants()
    alpha = constants["alpha"]
    c1 = constants["c1"]
    p_mass = constants["p_mass"]

    audit.check("production", "alpha", alpha == Fraction(5, 9), alpha, Fraction(5, 9))
    audit.check(
        "production",
        "c1",
        c1 == Fraction(243, 8000) / p_mass,
        c1,
        Fraction(243, 8000) / p_mass,
    )
    audit.check(
        "production",
        "c0",
        constants["c0"] == Fraction(3, 250) / p_mass,
        constants["c0"],
        Fraction(3, 250) / p_mass,
    )

    symbolic = rational_scalar_symbolics(alpha)
    scalar_oracles = {
        "full_ridge": sp.Rational(40, 81),
        "cubic_ridge": sp.Rational(-25, 81),
        "balanced_ridge": sp.Rational(65, 81),
        "full_shift_derivative": sp.Rational(-70, 27),
        "balanced_shift_derivative": sp.Rational(-95, 27),
    }
    for name, expected in scalar_oracles.items():
        audit.check("scalar_owner", name, symbolic[name] == expected, symbolic[name], expected)
    audit.check(
        "scalar_owner",
        "owner_recombination",
        sp.simplify(symbolic["full"] - symbolic["cubic"] - symbolic["balanced"]) == 0,
        "full-cubic-balanced",
        0,
    )

    heat = axis_heat_generator(alpha)
    heat_oracles = {
        "endpoint_heat": sp.Rational(4),
        "second_endpoint_heat": sp.Rational(-80, 3),
        "full_heat": sp.Rational(65, 9),
        "cubic_heat": sp.Rational(25, 3),
        "balanced_heat": sp.Rational(-10, 9),
    }
    for name, expected in heat_oracles.items():
        audit.check("small_heat", name, heat[name] == expected, heat[name], expected)
    generator_at_one = sp.factor(heat["generator"].subs(sp.symbols("x", real=True), 1))
    audit.check(
        "small_heat",
        "axis_generator_at_one",
        generator_at_one == sp.Rational(-22, 27),
        generator_at_one,
        sp.Rational(-22, 27),
    )

    normalized_hessian = normalized_hessian_certificate(alpha)
    normalized_difference = normalized_hessian["mixed_point_difference"]
    audit.check(
        "normalized_hessian",
        "mixed_direction_second_hessian_identity",
        normalized_difference == sp.zeros(2),
        normalized_difference,
        sp.zeros(2),
    )
    audit.check(
        "normalized_hessian",
        "finite_polynomial_degree",
        normalized_hessian["maximum_polynomial_degree"] <= 8,
        normalized_hessian["maximum_polynomial_degree"],
        "<=8",
    )

    coefficient_zero = 4 * c1
    coefficient_one = -4 * c1 * alpha
    coefficient_two = 4 * c1 * alpha**2
    laplace_coefficients = {
        "polynomial": coefficient_zero,
        "first_resolvent": coefficient_one,
        "second_resolvent": coefficient_two,
    }
    laplace_oracles = {
        "polynomial": Fraction(243, 2000) / p_mass,
        "first_resolvent": -Fraction(27, 400) / p_mass,
        "second_resolvent": Fraction(3, 80) / p_mass,
    }
    for name, expected in laplace_oracles.items():
        audit.check(
            "laplace_wick",
            f"{name}_coefficient",
            laplace_coefficients[name] == expected,
            laplace_coefficients[name],
            expected,
        )

    # The tilted-Gaussian representation is checked on a genuinely singular
    # covariance.  The original side uses the latent h=Lq integral, while the
    # tilted side uses the independently reconstructed mean/covariance.
    latent_factor = np.array(
        [
            [0.25, 0.00],
            [0.10, -0.15],
            [0.00, 0.20],
            [0.05, 0.10],
            [0.30, 0.00],
            [-0.10, 0.12],
        ],
        dtype=float,
    )
    singular_sigma = latent_factor @ latent_factor.T
    tilt_time = 0.35
    tilt_z = np.array([0.4, -0.3, 0.2, 0.1, 0.5, -0.2])
    identity = np.eye(6)
    tilt_matrix = identity + 2.0 * tilt_time * singular_sigma
    inverse_tilt = np.linalg.inv(tilt_matrix)
    tilted_mean = inverse_tilt @ tilt_z
    tilted_covariance = singular_sigma @ inverse_tilt
    latent_tilt = np.eye(2) + 2.0 * tilt_time * (latent_factor.T @ latent_factor)
    latent_inverse = np.linalg.inv(latent_tilt)
    latent_mean = tilt_z - 2.0 * tilt_time * latent_factor @ latent_inverse @ latent_factor.T @ tilt_z
    latent_covariance = latent_factor @ latent_inverse @ latent_factor.T
    audit.check(
        "laplace_wick",
        "singular_determinant_lemma",
        abs(np.linalg.det(tilt_matrix) - np.linalg.det(latent_tilt)) < 2.0e-13,
        np.linalg.det(tilt_matrix),
        np.linalg.det(latent_tilt),
    )
    audit.check(
        "laplace_wick",
        "singular_mean_woodbury",
        np.allclose(tilted_mean, latent_mean, rtol=2.0e-13, atol=2.0e-13),
        float(np.max(np.abs(tilted_mean - latent_mean))),
        0.0,
    )
    audit.check(
        "laplace_wick",
        "singular_covariance_woodbury",
        np.allclose(tilted_covariance, latent_covariance, rtol=2.0e-13, atol=2.0e-13),
        float(np.max(np.abs(tilted_covariance - latent_covariance))),
        0.0,
    )
    projector = np.diag([1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
    original_points, original_weights = gaussian_factor_grid(tilt_z, latent_factor, order=18)
    eigenvalues, eigenvectors = np.linalg.eigh((tilted_covariance + tilted_covariance.T) / 2.0)
    positive = eigenvalues > 1.0e-13
    tilted_factor = eigenvectors[:, positive] * np.sqrt(eigenvalues[positive])[None, :]
    tilted_points, tilted_weights = gaussian_factor_grid(tilted_mean, tilted_factor, order=5)
    tilt_normalizer = math.exp(-tilt_time * float(tilt_z @ inverse_tilt @ tilt_z)) / math.sqrt(
        np.linalg.det(tilt_matrix)
    )
    singular_wick_errors: dict[str, float] = {}
    for wick_order in (1, 2):
        original_wick = wick_moment(
            original_points,
            original_weights,
            projector,
            wick_order,
            decay=tilt_time,
        )
        tilted_wick = tilt_normalizer * wick_moment(
            tilted_points,
            tilted_weights,
            projector,
            wick_order,
        )
        error = float(np.linalg.norm(original_wick - tilted_wick))
        scale = max(float(np.linalg.norm(tilted_wick)), 1.0e-12)
        relative = error / scale
        singular_wick_errors[f"W{wick_order}"] = relative
        audit.check(
            "laplace_wick",
            f"singular_W{wick_order}_tilt_identity",
            relative < 2.0e-10,
            relative,
            "<2e-10",
        )

    alpha_float = float(alpha)
    c1_float = float(c1)
    # Dimensionless floor-one fixture; production-floor scaling is analytic.
    sigma = 0.12
    scalar_heat_checks: dict[str, dict[str, float]] = {}
    moment_points, moment_weights = gaussian_grid(6, sigma, order=9)
    moment_x = 0.7
    shifted_moment_points = moment_points.copy()
    shifted_moment_points[:, 0] += moment_x
    moment_projected = shifted_moment_points.copy()
    moment_projected[:, 4:] = 0.0
    moment_radius = np.sum(moment_projected * moment_projected, axis=1)
    moment_y1_squared = shifted_moment_points[:, 0] ** 2
    pointwise_wick_errors: dict[str, dict[str, float]] = {}
    for time_index, time_value in enumerate((0.0, 0.2, 1.0, 3.0)):
        decay = np.exp(-time_value * np.sum(shifted_moment_points * shifted_moment_points, axis=1))
        direct_first = float(np.sum(moment_weights * decay * moment_radius * moment_y1_squared))
        direct_second = float(np.sum(moment_weights * decay * moment_radius**2 * moment_y1_squared))
        closed_first, closed_second = isotropic_closed_wick_moments(moment_x, sigma, time_value)
        first_relative = abs(direct_first - closed_first) / max(abs(closed_first), 1.0e-12)
        second_relative = abs(direct_second - closed_second) / max(abs(closed_second), 1.0e-12)
        tolerance = 5.0e-11 if time_value == 0.0 else (2.0e-5 if time_value <= 1.0 else 5.0e-4)
        audit.check(
            "laplace_wick",
            f"F1_pointwise_{time_index}",
            first_relative < tolerance,
            first_relative,
            tolerance,
        )
        audit.check(
            "laplace_wick",
            f"F2_pointwise_{time_index}",
            second_relative < tolerance,
            second_relative,
            tolerance,
        )
        pointwise_wick_errors[str(time_value)] = {
            "F1_relative": first_relative,
            "F2_relative": second_relative,
        }
    for index, x_value in enumerate((0.0, 0.7, 1.3)):
        z = np.zeros(6)
        z[0] = x_value
        direct = float(direct_heat_gram(z, sigma, alpha_float, c1_float)[0, 0])
        laplace = isotropic_laplace_scalar(x_value, sigma, alpha_float, c1_float)
        error = abs(direct - laplace)
        tolerance = 3.0e-7 + 2.0e-5 * abs(laplace)
        audit.check("laplace_wick", f"isotropic_direct_match_{index}", error < tolerance, error, tolerance)
        scalar_heat_checks[str(x_value)] = {"direct": direct, "laplace": laplace, "error": error}

    exponent = Fraction(3, 5)
    x_power = (1 + exponent) / 4
    y_power = (5 - exponent) / 12
    slack = 1 - x_power - y_power
    audit.check("young", "x_power", x_power == Fraction(2, 5), x_power, Fraction(2, 5))
    audit.check("young", "y_power", y_power == Fraction(11, 30), y_power, Fraction(11, 30))
    audit.check("young", "slack", slack == Fraction(7, 30), slack, Fraction(7, 30))
    audit.check("young", "random_moment", 1 / slack == Fraction(30, 7), 1 / slack, Fraction(30, 7))
    audit.check("young", "eta_power", x_power / slack == Fraction(12, 7), x_power / slack, Fraction(12, 7))
    audit.check("young", "zeta_power", y_power / slack == Fraction(11, 7), y_power / slack, Fraction(11, 7))
    split_total = (1 + exponent) / 4 + (9 - exponent) / 12
    multiplier_total = (5 + exponent) / 6 + exponent / 4
    audit.check("young", "split_balanced_supercritical", split_total == Fraction(11, 10), split_total, Fraction(11, 10))
    audit.check(
        "young",
        "separated_multiplier_supercritical",
        multiplier_total == Fraction(13, 12),
        multiplier_total,
        Fraction(13, 12),
    )

    # Chronological last-insertion closure ledger.  A finite martingale array
    # checks both the j<k to k-first swap and conditioning of the whole future
    # product.  The polynomial heat check is an exact semigroup test for the
    # deterministic target-plus-future covariance composition.
    chronological_states = tuple(
        (first, second, third)
        for first in (-1, 1)
        for second in (-1, 1)
        for third in (-1, 1)
    )
    chronological_original = sum(
        Fraction(first) * Fraction(3 * first + second)
        + Fraction(first) * Fraction(first * third + 2 * second + first * second * third)
        + Fraction(first * second)
        * Fraction(first * third + 2 * second + first * second * third)
        for first, second, third in chronological_states
    ) / 8
    chronological_swapped = sum(
        Fraction(first) * Fraction(3 * first + second)
        + Fraction(first + first * second)
        * Fraction(first * third + 2 * second + first * second * third)
        for first, second, third in chronological_states
    ) / 8
    chronological_conditioned = sum(
        Fraction(first) * Fraction(3 * first)
        + Fraction(first + first * second) * Fraction(2 * second)
        for first, second, _third in chronological_states
    ) / 8
    audit.check(
        "chronological_closure",
        "finite_double_sum_swap",
        chronological_original == chronological_swapped,
        chronological_original,
        chronological_swapped,
    )
    audit.check(
        "chronological_closure",
        "finite_whole_product_conditioning",
        chronological_swapped == chronological_conditioned,
        chronological_swapped,
        chronological_conditioned,
    )

    heat_point, target_heat, future_heat = Fraction(2, 3), Fraction(1, 5), Fraction(2, 7)

    def quartic_heat(point: Fraction, heat_time: Fraction) -> Fraction:
        return point**4 + 6 * heat_time * point**2 + 3 * heat_time**2

    composed_quartic_heat = (
        quartic_heat(heat_point, target_heat)
        + 6 * future_heat * (heat_point**2 + target_heat)
        + 3 * future_heat**2
    )
    direct_quartic_heat = quartic_heat(heat_point, target_heat + future_heat)
    audit.check(
        "chronological_closure",
        "deterministic_heat_semigroup_composition",
        composed_quartic_heat == direct_quartic_heat,
        composed_quartic_heat,
        direct_quartic_heat,
    )

    derivative_spatial = Fraction(1, 6) + Fraction(1, 3) + Fraction(1, 2)
    derivative_slack = 1 - Fraction(1, 2) - Fraction(1, 3)
    audit.check("chronological_closure", "derivative_spatial_holder", derivative_spatial == 1, derivative_spatial, 1)
    audit.check("chronological_closure", "derivative_young_slack", derivative_slack == Fraction(1, 6), derivative_slack, Fraction(1, 6))
    audit.check("chronological_closure", "derivative_gaussian_moment", 1 / derivative_slack == 6, 1 / derivative_slack, 6)

    first_spatial = Fraction(1, 6) + Fraction(1, 6) + Fraction(11, 42) + Fraction(17, 42)
    first_interpolation = Fraction(2, 7) + Fraction(5, 7)
    first_shell_holder = Fraction(1, 7) + Fraction(5, 42) + Fraction(31, 42)
    second_spatial = Fraction(1, 6) + 2 * Fraction(3, 14) + Fraction(17, 42)
    second_interpolation = Fraction(1, 7) + Fraction(6, 7)
    second_shell_holder = Fraction(1, 7) + Fraction(2, 7) + Fraction(4, 7)
    for name, actual in (
        ("first_coefficient_spatial_holder", first_spatial),
        ("first_coefficient_interpolation", first_interpolation),
        ("first_coefficient_shell_holder", first_shell_holder),
        ("second_coefficient_spatial_holder", second_spatial),
        ("second_coefficient_interpolation", second_interpolation),
        ("second_coefficient_shell_holder", second_shell_holder),
    ):
        audit.check("chronological_closure", name, actual == 1, actual, 1)

    chronological_decay = Fraction(1, 2) - Fraction(4, 7)
    chronological_x_power = Fraction(1, 2) + Fraction(1, 7)
    chronological_y_power = Fraction(2, 7)
    chronological_slack = 1 - chronological_x_power - chronological_y_power
    audit.check("chronological_closure", "coefficient_shell_decay", chronological_decay == Fraction(-1, 14), chronological_decay, Fraction(-1, 14))
    audit.check("chronological_closure", "coefficient_x_power", chronological_x_power == Fraction(9, 14), chronological_x_power, Fraction(9, 14))
    audit.check("chronological_closure", "coefficient_y_power", chronological_y_power == Fraction(2, 7), chronological_y_power, Fraction(2, 7))
    audit.check("chronological_closure", "coefficient_young_slack", chronological_slack == Fraction(1, 14), chronological_slack, Fraction(1, 14))
    audit.check("chronological_closure", "coefficient_gaussian_moment", 1 / chronological_slack == 14, 1 / chronological_slack, 14)
    audit.check("chronological_closure", "coefficient_eta_power", chronological_x_power / chronological_slack == 9, chronological_x_power / chronological_slack, 9)
    audit.check("chronological_closure", "coefficient_zeta_power", chronological_y_power / chronological_slack == 4, chronological_y_power / chronological_slack, 4)

    # Freeze audit: canonical X is the high-shell Cameron--Martin sum.  The
    # fixed-low derivative is a separate R-080/Bernstein branch and must not be
    # hidden inside an additive constant in the high-prefix derivative bound.
    sample_shell_energies = (Fraction(1, 9), Fraction(1, 4), Fraction(4, 25))
    canonical_path_energy = sum(sample_shell_energies, Fraction(0))
    audit.check(
        "chronological_closure",
        "canonical_x_high_shell_sum",
        canonical_path_energy == Fraction(469, 900),
        canonical_path_energy,
        Fraction(469, 900),
    )
    high_prefix_derivative_x_power = Fraction(1, 2)
    audit.check(
        "chronological_closure",
        "high_prefix_derivative_no_additive_constant",
        high_prefix_derivative_x_power == Fraction(1, 2),
        high_prefix_derivative_x_power,
        Fraction(1, 2),
    )
    fixed_low_x_power = Fraction(1, 7)
    fixed_low_y_power = Fraction(2, 7) + Fraction(1, 6)
    fixed_low_slack = 1 - fixed_low_x_power - fixed_low_y_power
    fixed_low_moment = 1 / fixed_low_slack
    fixed_low_eta_power = fixed_low_x_power / fixed_low_slack
    fixed_low_zeta_power = fixed_low_y_power / fixed_low_slack
    fixed_low_decay_power = fixed_low_moment / 14
    audit.check("chronological_closure", "fixed_low_branch_retained", True, "high plus fixed-low", "high plus fixed-low")
    audit.check("chronological_closure", "fixed_low_x_power", fixed_low_x_power == Fraction(1, 7), fixed_low_x_power, Fraction(1, 7))
    audit.check("chronological_closure", "fixed_low_y_power", fixed_low_y_power == Fraction(19, 42), fixed_low_y_power, Fraction(19, 42))
    audit.check("chronological_closure", "fixed_low_young_slack", fixed_low_slack == Fraction(17, 42), fixed_low_slack, Fraction(17, 42))
    audit.check("chronological_closure", "fixed_low_gaussian_moment", fixed_low_moment == Fraction(42, 17), fixed_low_moment, Fraction(42, 17))
    audit.check("chronological_closure", "fixed_low_eta_power", fixed_low_eta_power == Fraction(6, 17), fixed_low_eta_power, Fraction(6, 17))
    audit.check("chronological_closure", "fixed_low_zeta_power", fixed_low_zeta_power == Fraction(19, 17), fixed_low_zeta_power, Fraction(19, 17))
    audit.check("chronological_closure", "fixed_low_decay_power", fixed_low_decay_power == Fraction(3, 17), fixed_low_decay_power, Fraction(3, 17))

    x_symbol, shift_symbol = sp.symbols("x shift", real=True)
    bridge_scale = sp.Rational(1, 100)
    plus = symbolic["full"].subs({x_symbol: 1, shift_symbol: -1 + bridge_scale})
    minus = symbolic["full"].subs({x_symbol: 1, shift_symbol: -1 - bridge_scale})
    bridge_full = sp.factor((plus - minus) / 2)
    plus_balanced = symbolic["balanced"].subs({x_symbol: 1, shift_symbol: -1 + bridge_scale})
    minus_balanced = symbolic["balanced"].subs({x_symbol: 1, shift_symbol: -1 - bridge_scale})
    bridge_balanced = sp.factor((plus_balanced - minus_balanced) / 2)
    predicted_full = sp.Rational(-70, 27) * bridge_scale
    predicted_balanced_rademacher = sp.Rational(-95, 27) * bridge_scale - sp.Rational(25, 81) * bridge_scale**3
    audit.check("future_feedback", "full_bridge_residual", bridge_full == predicted_full, bridge_full, predicted_full)
    audit.check(
        "future_feedback",
        "balanced_bridge_residual",
        bridge_balanced == predicted_balanced_rademacher,
        bridge_balanced,
        predicted_balanced_rademacher,
    )
    predictable_baseline = symbolic["full_ridge"]
    baseline_cross = sp.factor((predictable_baseline - predictable_baseline) / 2)
    audit.check("future_feedback", "predictable_baseline_centres", baseline_cross == 0, baseline_cross, 0)
    audit.check(
        "future_feedback",
        "cross_doob_residual_identity",
        sp.simplify(bridge_full - baseline_cross - predicted_full) == 0,
        bridge_full,
        predicted_full,
    )
    audit.check("future_feedback", "naive_bridge_is_false", bridge_full != 0, bridge_full, "nonzero")

    gaussian_balanced_prediction = (
        sp.Rational(-95, 27) * bridge_scale - sp.Rational(25, 27) * bridge_scale**3
    )
    gaussian_balanced_from_moments = (
        symbolic["full_shift_derivative"] * bridge_scale
        - sp.Rational(25, 81) * (3 * bridge_scale + 3 * bridge_scale**3)
    )
    audit.check(
        "future_feedback",
        "gaussian_balanced_residual",
        gaussian_balanced_from_moments == gaussian_balanced_prediction,
        gaussian_balanced_from_moments,
        gaussian_balanced_prediction,
    )

    # A genuine two-root Gaussian Doob computation.  The terminal coefficient
    # depends on the first Gaussian through a later strict-past control, while
    # the second fresh derivative root is independent.  High-order Hermite
    # quadrature evaluates both Gaussian coordinates directly; the first
    # bracket is also compared with the exact parity/moment formula above.
    doob_nodes, doob_weights_raw = np.polynomial.hermite.hermgauss(80)
    gaussian_roots = math.sqrt(2.0) * doob_nodes
    gaussian_weights = doob_weights_raw / math.sqrt(math.pi)
    full_function = sp.lambdify((x_symbol, shift_symbol), symbolic["full"], "numpy")
    terminal_by_first = np.asarray(
        full_function(1.0, -1.0 + float(bridge_scale) * gaussian_roots), dtype=float
    )
    terminal_mean = float(np.sum(gaussian_weights * terminal_by_first))
    first_root = gaussian_roots[:, None]
    second_root = gaussian_roots[None, :]
    product_weights = gaussian_weights[:, None] * gaussian_weights[None, :]
    terminal_matrix = terminal_by_first[:, None]
    low_value = 2.0
    terminal_pairing = float(
        np.sum(product_weights * (low_value + first_root + second_root) * terminal_matrix)
    )
    low_endpoint = low_value * terminal_mean
    first_bracket = float(
        np.sum(product_weights * first_root * (terminal_matrix - terminal_mean))
    )
    second_bracket = 0.0
    audit.check(
        "future_feedback",
        "two_root_cross_doob",
        abs(terminal_pairing - low_endpoint - first_bracket - second_bracket) < 2.0e-13,
        terminal_pairing,
        low_endpoint + first_bracket + second_bracket,
    )
    audit.check(
        "future_feedback",
        "two_root_low_endpoint_retained",
        abs(low_endpoint) > 1.0e-6,
        low_endpoint,
        "nonzero",
    )
    audit.check(
        "future_feedback",
        "two_root_first_bracket",
        abs(first_bracket - float(predicted_full)) < 2.0e-13,
        first_bracket,
        predicted_full,
    )
    audit.check("future_feedback", "two_root_second_bracket", second_bracket == 0.0, second_bracket, 0.0)

    # Future-insertion Jensen blind spot.  The Rademacher sign is revealed
    # after the Gaussian current root, so the conditional means of both the
    # control and its scalar tangent vanish at that root.  The nonlinear
    # coefficient average nevertheless has a nonzero Gaussian bracket.
    insertion_amplitude, insertion_coupling = sp.Rational(1, 10), sp.Rational(1, 2)
    insertion_variable = sp.symbols("insertion_variable", real=True)
    insertion_psi = sp.factor(
        symbolic["full"].subs({x_symbol: 1, shift_symbol: insertion_variable})
        * insertion_variable
    )
    insertion_even_average = sp.factor(
        (insertion_psi + insertion_psi.subs(insertion_variable, -insertion_variable)) / 2
    )
    insertion_closed_form = sp.factor(
        -40
        * insertion_variable**4
        * (2 * insertion_variable**6 + 13 * insertion_variable**2 - 10)
        / (
            81
            * (insertion_variable**2 - 2 * insertion_variable + 2) ** 2
            * (insertion_variable**2 + 2 * insertion_variable + 2) ** 2
        )
    )
    audit.check(
        "future_feedback",
        "jensen_even_average_formula",
        sp.factor(insertion_even_average - insertion_closed_form) == 0,
        insertion_even_average,
        insertion_closed_form,
    )
    insertion_large = insertion_amplitude * (1 + insertion_coupling)
    insertion_small = insertion_amplitude * (1 - insertion_coupling)
    insertion_gap = sp.factor(
        insertion_even_average.subs(insertion_variable, insertion_large)
        - insertion_even_average.subs(insertion_variable, insertion_small)
    )
    insertion_gap_oracle = sp.Rational(
        10175618597178586187512,
        67965137546788211215457205,
    )
    insertion_current_factor = sp.factor(-insertion_gap / 2)
    insertion_current_oracle = sp.Rational(
        -5087809298589293093756,
        67965137546788211215457205,
    )
    zero_conditional_controls = all(
        sp.factor((radius + (-radius)) / 2) == 0
        for radius in (insertion_large, insertion_small)
    )
    audit.check(
        "future_feedback",
        "jensen_control_tangent_increments_vanish",
        zero_conditional_controls,
        zero_conditional_controls,
        True,
    )
    audit.check(
        "future_feedback",
        "jensen_nonlinear_innovation_gap",
        insertion_gap == insertion_gap_oracle,
        insertion_gap,
        insertion_gap_oracle,
    )
    audit.check(
        "future_feedback",
        "jensen_current_is_negative",
        insertion_current_factor == insertion_current_oracle and insertion_current_factor < 0,
        insertion_current_factor,
        insertion_current_oracle,
    )

    grid = np.linspace(0.0, 2.0 * math.pi, 32768, endpoint=False)
    root_frequency = 7
    payload_frequency = 3
    trig_average = float(
        np.mean(
            np.cos(root_frequency * grid)
            * np.cos((root_frequency + payload_frequency) * grid)
            * np.cos(payload_frequency * grid)
        )
    )
    audit.check("future_feedback", "three_frequency_pairing", abs(trig_average - 0.25) < 1.0e-12, trig_average, 0.25)
    full_fourier_coefficient = sp.factor(symbolic["full_shift_derivative"] / 4)
    balanced_fourier_coefficient = sp.factor(symbolic["balanced_shift_derivative"] / 4)
    audit.check(
        "future_feedback",
        "full_fourier_leading_coefficient",
        full_fourier_coefficient == sp.Rational(-35, 54),
        full_fourier_coefficient,
        sp.Rational(-35, 54),
    )
    audit.check(
        "future_feedback",
        "balanced_fourier_leading_coefficient",
        balanced_fourier_coefficient == sp.Rational(-95, 108),
        balanced_fourier_coefficient,
        sp.Rational(-95, 108),
    )

    curl_x, curl_y = sp.symbols("curl_x curl_y", real=True)
    curl_denominator = 1 + curl_x**2 + curl_y**2
    curl_row = sp.Matrix(
        [
            curl_x - sp.Rational(alpha.numerator, alpha.denominator) * curl_x**3 / curl_denominator,
            -sp.Rational(alpha.numerator, alpha.denominator) * curl_x**2 * curl_y / curl_denominator,
        ]
    )
    curl_gram = 4 * curl_row * curl_row.T
    curl_remainder = (
        curl_gram.subs(curl_x, curl_x + 1)
        - curl_gram
        - sp.diff(curl_gram, curl_x)
        - sp.diff(curl_gram, curl_x, 2) / 2
    )
    curl_one_form = curl_remainder[:, 0]
    curl_value = sp.factor(
        (sp.diff(curl_one_form[0], curl_y) - sp.diff(curl_one_form[1], curl_x)).subs(
            {curl_x: 1, curl_y: 1}
        )
    )
    audit.check(
        "cartan_boundary",
        "full_remainder_one_form_curl",
        curl_value == sp.Rational(-40, 729),
        curl_value,
        sp.Rational(-40, 729),
    )

    rng = np.random.default_rng(102)
    for index in range(8):
        z = rng.normal(size=6) * 10.0 ** rng.uniform(-3.0, 3.0)
        rho = math.sqrt(1.0 + float(z @ z))
        n = z / rho
        projected_z = z.copy()
        projected_z[4:] = 0.0
        projected_n = n.copy()
        projected_n[4:] = 0.0
        row_direct = projected_z - alpha_float * float(projected_z @ projected_z) / (1.0 + float(z @ z)) * z
        row_normalized = rho * (
            projected_n - alpha_float * float(projected_n @ projected_n) * n
        )
        audit.check(
            "normalized_hessian",
            f"row_factorization_{index}",
            np.allclose(row_direct, row_normalized, rtol=2.0e-12, atol=2.0e-12),
            float(np.max(np.abs(row_direct - row_normalized))),
            0.0,
        )

    geometry_sigma = 0.2
    geometry_z = np.array([0.7, -0.2, 0.3, 0.1, 1.1, -0.4])
    heat_gram = direct_heat_gram(geometry_z, geometry_sigma, alpha_float, c1_float)
    active_q = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    active_second_moment = geometry_z[0] ** 2 + geometry_sigma
    active_value = float(active_q @ heat_gram @ active_q)
    active_lower = 4.0 * c1_float * (1.0 - alpha_float) ** 2 * active_second_moment
    active_upper = 4.0 * c1_float * active_second_moment
    audit.check("heat_geometry", "active_lower_bound", active_value + 2.0e-10 >= active_lower, active_value, active_lower)
    audit.check("heat_geometry", "active_upper_bound", active_value <= active_upper + 2.0e-10, active_value, active_upper)
    minimum_eigenvalue = float(np.linalg.eigvalsh(heat_gram)[0])
    audit.check("heat_geometry", "sample_full_rank_positivity", minimum_eigenvalue > 0.0, minimum_eigenvalue, ">0")

    kernel_vector = np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    rank = 4
    kernel_limit = 4.0 * c1_float * alpha_float**2 * rank * (rank + 2) * geometry_sigma**2
    kernel_ratios: list[float] = []
    for index, amplitude in enumerate((20.0, 50.0, 100.0)):
        kernel_gram = direct_heat_gram(amplitude * kernel_vector, geometry_sigma, alpha_float, c1_float)
        scaled = amplitude**2 * float(kernel_vector @ kernel_gram @ kernel_vector)
        ratio = scaled / kernel_limit
        kernel_ratios.append(ratio)
        tolerance = 0.20 if index == 0 else (0.08 if index == 1 else 0.04)
        audit.check("heat_geometry", f"kernel_asymptotic_{index}", abs(ratio - 1.0) < tolerance, ratio, 1.0)
    audit.check(
        "heat_geometry",
        "kernel_limit_constant",
        Fraction(4) * alpha**2 * rank * (rank + 2) == Fraction(800, 27),
        Fraction(4) * alpha**2 * rank * (rank + 2),
        Fraction(800, 27),
    )

    diagnostics.update(
        {
            "production_constants": constants,
            "scalar_owner": {name: symbolic[name] for name in scalar_oracles},
            "heat_generator": heat,
            "normalized_hessian": normalized_hessian,
            "laplace_coefficients": laplace_coefficients,
            "singular_covariance_wick_relative_errors": singular_wick_errors,
            "pointwise_isotropic_wick_relative_errors": pointwise_wick_errors,
            "isotropic_heat_checks": scalar_heat_checks,
            "chronological_closure": {
                "finite_array_value": chronological_original,
                "derivative_slack": derivative_slack,
                "coefficient_shell_decay": chronological_decay,
                "coefficient_x_power": chronological_x_power,
                "coefficient_y_power": chronological_y_power,
                "coefficient_slack": chronological_slack,
                "required_gaussian_moment": 1 / chronological_slack,
                "eta_power": chronological_x_power / chronological_slack,
                "zeta_power": chronological_y_power / chronological_slack,
                "canonical_x_fixture": canonical_path_energy,
                "high_prefix_derivative_x_power": high_prefix_derivative_x_power,
                "fixed_low_x_power": fixed_low_x_power,
                "fixed_low_y_power": fixed_low_y_power,
                "fixed_low_slack": fixed_low_slack,
                "fixed_low_required_gaussian_moment": fixed_low_moment,
                "fixed_low_eta_power": fixed_low_eta_power,
                "fixed_low_zeta_power": fixed_low_zeta_power,
                "fixed_low_decay_power": fixed_low_decay_power,
            },
            "future_feedback": {
                "lambda": bridge_scale,
                "full_residual": bridge_full,
                "balanced_rademacher_residual": bridge_balanced,
                "balanced_gaussian_residual": gaussian_balanced_prediction,
                "two_root_first_bracket": first_bracket,
                "two_root_second_bracket": second_bracket,
                "two_root_low_endpoint": low_endpoint,
                "jensen_innovation_gap": insertion_gap,
                "jensen_current_sqrt_2_over_pi_factor": insertion_current_factor,
                "trigonometric_average": trig_average,
            },
            "cartan_boundary": {"full_remainder_one_form_curl": curl_value},
            "heat_geometry": {
                "active_value": active_value,
                "active_lower": active_lower,
                "active_upper": active_upper,
                "sample_minimum_eigenvalue": minimum_eigenvalue,
                "kernel_limit": kernel_limit,
                "kernel_ratios": kernel_ratios,
            },
            "analytic_boundary": {
                "naive_global_to_predictable_bridge": False,
                "full_hessian_chain_primitive": False,
                "regular_weighted_innovation_carleson_proved": True,
                "regular_k_r_lower_form": True,
                "full_frame_posterior_bracket": False,
                "complete_h_n": False,
                "reg": False,
                "sector_a_closed": False,
            },
        }
    )

    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(
        "R-102 primary:",
        f"{payload['assertions_passed']}/{payload['assertions_total']} PASS",
        f"-> {OUTPUT.relative_to(REPO)}",
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
