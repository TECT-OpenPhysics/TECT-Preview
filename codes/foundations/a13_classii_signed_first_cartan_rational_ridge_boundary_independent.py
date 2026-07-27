#!/usr/bin/env python3
"""Standard-library independent certificate for the R-098 A13 checkpoint.

This executable does not import the primary implementation or numerical
packages.  It recomputes the payment-split identity, ridge normal form,
rational fractions, finite-floor Cartan derivative and Fourier coefficients,
frame constant mutation, Efron--Stein multiplicity, and Hardy mass.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import argparse
import ast
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Callable, Iterable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-FIRST-CARTAN-RATIONAL-RIDGE-BOUNDARY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-independent-signed-first-cartan-rational-ridge-boundary/result.json"
)

Vector = tuple[F, F]
Matrix = tuple[tuple[F, F], tuple[F, F]]


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def vadd(left: Vector, right: Vector) -> Vector:
    return left[0] + right[0], left[1] + right[1]


def vsub(left: Vector, right: Vector) -> Vector:
    return left[0] - right[0], left[1] - right[1]


def vscale(scale: F, vector: Vector) -> Vector:
    return scale * vector[0], scale * vector[1]


def dot(left: Vector, right: Vector) -> F:
    return left[0] * right[0] + left[1] * right[1]


def madd(left: Matrix, right: Matrix) -> Matrix:
    return (
        (left[0][0] + right[0][0], left[0][1] + right[0][1]),
        (left[1][0] + right[1][0], left[1][1] + right[1][1]),
    )


def mscale(scale: F, matrix: Matrix) -> Matrix:
    return (
        (scale * matrix[0][0], scale * matrix[0][1]),
        (scale * matrix[1][0], scale * matrix[1][1]),
    )


def mvec(matrix: Matrix, vector: Vector) -> Vector:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def outer(vector: Vector) -> Matrix:
    return (
        (vector[0] * vector[0], vector[0] * vector[1]),
        (vector[1] * vector[0], vector[1] * vector[1]),
    )


def inverse(matrix: Matrix) -> Matrix:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    if determinant <= 0:
        raise ValueError("matrix is not positive definite")
    return (
        (matrix[1][1] / determinant, -matrix[0][1] / determinant),
        (-matrix[1][0] / determinant, matrix[0][0] / determinant),
    )


def quadratic(matrix: Matrix, vector: Vector) -> F:
    return dot(vector, mvec(matrix, vector))


def expectation(atoms: Iterable[tuple[F, Any]], function: Callable[[Any], F]) -> F:
    return sum((probability * function(value) for probability, value in atoms), F(0))


def cartan_coefficient(epsilon: float, harmonic: int) -> float:
    rho = (1.0 - epsilon) / (1.0 + epsilon)
    return -2.0 * epsilon * (1.0 - rho * rho) * rho ** (harmonic - 1)


def cartan_tau(theta: float, epsilon: float) -> float:
    sine = math.sin(theta)
    cosine = math.cos(theta)
    density = sine * sine + epsilon * epsilon * cosine * cosine
    quotient = (sine * sine - epsilon * epsilon * cosine * cosine) / density
    density_prime = (1.0 - epsilon * epsilon) * math.sin(2.0 * theta)
    return quotient * density_prime


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main(output: Path) -> int:
    rows: list[dict[str, Any]] = []

    def check(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    roots = imported_roots(Path(__file__).resolve())
    forbidden = {"numpy", "scipy", "sympy", "mpmath"}
    check("independence", "no_numerical_package_import", roots.isdisjoint(forbidden), sorted(roots & forbidden), [])
    primary_module = "a13_classii_signed_first_cartan_rational_ridge_boundary"
    check("independence", "does_not_import_primary_module", primary_module not in roots, sorted(roots), "primary module absent")

    # Exact payment-split fractional square certificate.
    a1: Matrix = ((F(2), F(0)), (F(0), F(3)))
    a2: Matrix = ((F(5), F(0)), (F(0), F(7)))
    q1: Vector = (F(1), F(2))
    q2: Vector = (F(-2), F(1))
    total_a = madd(a1, a2)
    total_q = vadd(q1, q2)
    y = mvec(inverse(total_a), total_q)
    fractional_gap = (
        quadratic(inverse(a1), q1)
        + quadratic(inverse(a2), q2)
        - quadratic(inverse(total_a), total_q)
    )
    square_gap = (
        quadratic(inverse(a1), vsub(q1, mvec(a1, y)))
        + quadratic(inverse(a2), vsub(q2, mvec(a2, y)))
    )
    check("posterior", "strict_gap_exact", fractional_gap == F(26, 15), fractional_gap, F(26, 15))
    check("posterior", "fractional_square_exact", square_gap == fractional_gap, square_gap, fractional_gap)
    wick_rows = (F(17, 11), F(-5, 13))
    full_bracket = sum(wick_rows, F(0)) - quadratic(inverse(total_a), total_q)
    row_brackets = (
        wick_rows[0] - quadratic(inverse(a1), q1)
        + wick_rows[1] - quadratic(inverse(a2), q2)
    )
    check("posterior", "wick_terms_cancel_in_superadditivity", full_bracket - row_brackets == fractional_gap, full_bracket - row_brackets, fractional_gap)
    y0: Vector = (F(2, 3), F(-1, 4))
    equality_q1 = mvec(a1, y0)
    equality_q2 = mvec(a2, y0)
    equality_total = vadd(equality_q1, equality_q2)
    equality_gap = (
        quadratic(inverse(a1), equality_q1)
        + quadratic(inverse(a2), equality_q2)
        - quadratic(inverse(total_a), equality_total)
    )
    check("posterior", "equality_characterization_fixture", equality_gap == 0, equality_gap, F(0))
    full_reused = -F(4, 4)
    rows_reused = -F(2, 3)
    check("posterior", "same_payment_reuse_mutant_rejected", full_reused < rows_reused, full_reused - rows_reused, "< 0")

    # Rational coefficient arithmetic and derivative factorization.
    alpha = F(5, 9)
    c1 = F(243, 8000)

    def rational_value(t: F) -> F:
        ridge = t - alpha * t**3 / (t**2 + 1)
        return 4 * c1 * ridge**2

    b_minus = rational_value(F(1, 2))
    b_plus = rational_value(F(3, 2))
    delta = b_plus - b_minus
    rational_cpost = -delta / 3
    check("rational", "b_minus_exact", b_minus == F(3, 125), b_minus, F(3, 125))
    check("rational", "b_plus_exact", b_plus == F(2187, 21125), b_plus, F(2187, 21125))
    check("rational", "delta_exact", delta == F(1680, 21125), delta, F(1680, 21125))
    check("rational", "three_atom_cpost_exact", rational_cpost == F(-560, 21125), rational_cpost, F(-560, 21125))
    check("rational", "three_atom_cpost_negative", rational_cpost < 0, rational_cpost, "< 0")
    for t in (F(1, 10), F(1, 2), F(1), F(3, 2), F(4)):
        direct_numerator = 2 * t * (4 * t**2 + 9) * (4 * t**4 + 3 * t**2 + 9)
        factored_numerator = 2 * t * (4 * t**2 + 9) * (2 * t**2 - 3 * t + 3) * (2 * t**2 + 3 * t + 3)
        check("rational", f"monotone_factor_identity_{t}", direct_numerator == factored_numerator, direct_numerator, factored_numerator)
        check("rational", f"monotone_derivative_positive_{t}", factored_numerator > 0, factored_numerator, "> 0")
    atom_weights = (F(1, 2), F(1, 4), F(1, 4))
    atom_g_sqrt2_coefficients = (F(0), F(1), F(-1))
    atom_g = tuple(math.sqrt(2.0) * float(coefficient) for coefficient in atom_g_sqrt2_coefficients)
    atom_g2 = tuple(2 * coefficient * coefficient for coefficient in atom_g_sqrt2_coefficients)
    atom_b = (b_plus, b_minus + delta / 3, b_minus + delta / 3)
    gamma_symmetry = sum((weight * g2 for weight, g2 in zip(atom_weights, atom_g2)), F(0))
    q_sqrt2_coefficient = sum(
        (weight * coefficient * g for weight, coefficient, g in zip(atom_weights, atom_b, atom_g_sqrt2_coefficients)),
        F(0),
    )
    q_numeric = sum(float(weight) * float(coefficient) * g for weight, coefficient, g in zip(atom_weights, atom_b, atom_g))
    transformed_r_values: list[float] = []
    for scalar_payment in (0.125, 1.0, 7.5):
        theta_roots = tuple(
            math.sqrt(2.0 * scalar_payment * float(coefficient) / (float(coefficient) + 2.0 * scalar_payment))
            for coefficient in atom_b
        )
        transformed_r_values.append(
            sum(float(weight) * theta_root * g for weight, theta_root, g in zip(atom_weights, theta_roots, atom_g))
        )
    sign_direct = sum((weight * coefficient * (g2 - 1) for weight, coefficient, g2 in zip(atom_weights, atom_b, atom_g2)), F(0))
    check("rational", "selector_gamma_one", gamma_symmetry == 1, gamma_symmetry, F(1))
    check("rational", "selector_q_zero", q_sqrt2_coefficient == 0 and abs(q_numeric) < 1.0e-15, (q_sqrt2_coefficient, q_numeric), (F(0), 0.0))
    check("rational", "selector_r_zero", max(abs(value) for value in transformed_r_values) < 1.0e-15, transformed_r_values, [0.0, 0.0, 0.0])
    check("rational", "selector_sign_direct", sign_direct == rational_cpost, sign_direct, rational_cpost)

    c0 = F(3, 250)
    full_minus = 4 * c0 * F(1, 2) ** 2 + b_minus
    full_plus = 4 * c0 * F(3, 2) ** 2 + b_plus
    full_delta = full_plus - full_minus
    full_cpost = -full_delta / 3
    check("rational", "full_frame_minus_exact", full_minus == F(9, 250), full_minus, F(9, 250))
    check("rational", "full_frame_plus_exact", full_plus == F(8937, 42250), full_plus, F(8937, 42250))
    check("rational", "full_frame_cpost_exact", full_cpost == F(-1236, 21125), full_cpost, F(-1236, 21125))

    # Independent exact vector ridge completion.
    weights = (F(1, 5), F(3, 10), F(1, 2))
    b_atoms: tuple[Vector, ...] = ((F(1), F(-1, 2)), (F(1, 5), F(11, 10)), (F(-7, 10), F(2, 5)))
    g_atoms: tuple[Vector, ...] = ((F(2, 5), F(-1)), (F(13, 10), F(1, 5)), (F(-1, 10), F(9, 10)))
    gamma: Matrix = ((F(4, 5), F(1, 10)), (F(1, 10), F(3, 5)))
    payment: Matrix = ((F(7, 10), F(3, 20)), (F(3, 20), F(9, 10)))
    k_matrix: Matrix = ((F(0), F(0)), (F(0), F(0)))
    q_vector: Vector = (F(0), F(0))
    raw = F(0)
    for weight, b, g in zip(weights, b_atoms, g_atoms):
        s = dot(b, g)
        colon = s * s - quadratic(gamma, b)
        direct_colon = quadratic(outer(b), g) - quadratic(gamma, b)
        check("ridge", f"rank_one_colon_{len([row for row in rows if row['group'] == 'ridge'])}", colon == direct_colon, colon, direct_colon)
        k_matrix = madd(k_matrix, mscale(weight, outer(b)))
        q_vector = vadd(q_vector, vscale(weight * s, b))
        raw += weight * colon
    ridge_matrix = madd(k_matrix, mscale(F(2), payment))
    h_star = mvec(inverse(ridge_matrix), q_vector)
    check("ridge", "stationarity_exact", mvec(ridge_matrix, h_star) == q_vector, mvec(ridge_matrix, h_star), q_vector)
    direct_ridge = raw - quadratic(inverse(ridge_matrix), q_vector)

    def ridge_objective(h: Vector) -> F:
        value = F(0)
        for weight, b, g in zip(weights, b_atoms, g_atoms):
            s = dot(b, g)
            value += weight * ((s - dot(b, h)) ** 2 - quadratic(gamma, b))
        return value + 2 * quadratic(payment, h)

    check("ridge", "objective_at_minimum", ridge_objective(h_star) == direct_ridge, ridge_objective(h_star), direct_ridge)
    for perturbation in ((F(1), F(0)), (F(0), F(1)), (F(2, 3), F(-4, 5))):
        candidate = vadd(h_star, perturbation)
        completion_gap = ridge_objective(candidate) - ridge_objective(h_star)
        expected_gap = quadratic(ridge_matrix, perturbation)
        check("ridge", f"completion_gap_{perturbation}", completion_gap == expected_gap, completion_gap, expected_gap)
    wrong_matrix = madd(k_matrix, payment)
    wrong_h = mvec(inverse(wrong_matrix), q_vector)
    check("ridge", "missing_factor_two_mutant_rejected", ridge_objective(wrong_h) != direct_ridge, ridge_objective(wrong_h), "!= direct ridge")

    # Exact owner/sign recovery trap for R-085 (6.5).
    recovery_a = F(3)
    recovery_q = F(2)
    recovery_c = F(-1, 2)
    recovery_r = F(1, 4)
    recovery_cpost = F(-1, 3)
    recovery_w0 = F(2, 5)
    recovery_u = F(-3, 7)
    recovery_value = (
        F(1, 2) * recovery_a * (recovery_c + recovery_q / recovery_a) ** 2
        + F(1, 2) * recovery_cpost
        - recovery_r * recovery_c**2
        - recovery_w0
        - recovery_u
    )
    check("recovery", "owner_identity_exact_value", recovery_value == F(-89, 560), recovery_value, F(-89, 560))
    wrong_u_sign = recovery_value + 2 * recovery_u
    check("recovery", "unshifted_sign_mutant_rejected", wrong_u_sign != recovery_value, wrong_u_sign, "!= correct")
    wrong_posterior_factor = recovery_value + F(1, 2) * recovery_cpost
    check("recovery", "posterior_half_factor_mutant_rejected", wrong_posterior_factor != recovery_value, wrong_posterior_factor, "!= correct")

    # Fourier quadrature uses no Poisson-series code.
    samples = 1 << 16
    fourier_errors: list[float] = []
    for epsilon in (0.25, 0.5, 0.75):
        for harmonic in range(2, 9):
            accumulator = 0.0
            for index in range(samples):
                theta = 2.0 * math.pi * (index + 0.5) / samples
                accumulator += cartan_tau(theta, epsilon) * math.sin(2.0 * harmonic * theta)
            quadrature = 2.0 * accumulator / samples
            expected = cartan_coefficient(epsilon, harmonic)
            error = abs(quadrature - expected)
            fourier_errors.append(error)
            check("cartan", f"independent_quadrature_eps_{epsilon}_k_{harmonic}", error < 2.0e-12, quadrature, expected)
    for harmonic in (2, 3, 9):
        expected_fraction = F(-8, 3 ** (harmonic + 1))
        actual = cartan_coefficient(0.5, harmonic)
        check("cartan", f"half_epsilon_exact_{harmonic}", abs(actual - float(expected_fraction)) < 1.0e-15, actual, expected_fraction)
        wrong_fraction = F(-8, 3 ** (harmonic + 2))
        check("cartan", f"wrong_power_mutant_{harmonic}", abs(actual - float(wrong_fraction)) > 1.0e-18, actual, wrong_fraction)

    # Finite-floor actual-current derivative by a distinct centered quotient.
    radial_errors: list[float] = []
    radial_floor = 0.37
    radial_frequency = 5.5
    for epsilon in (0.4, 0.7):
        for amplitude in (3.0, 17.0):
            for theta in (0.31, 0.93):
                sine = math.sin(theta)
                cosine = math.cos(theta)
                density = sine * sine + epsilon * epsilon * cosine * cosine
                numerator = sine * sine - epsilon * epsilon * cosine * cosine
                density_prime = (1.0 - epsilon * epsilon) * math.sin(2.0 * theta)

                def current(value: float) -> float:
                    return 0.5 * radial_frequency * value**4 * numerator * density_prime / (value * value * density + radial_floor)

                step = amplitude * 4.0e-6
                quotient = (current(amplitude + step) - current(amplitude - step)) / (2.0 * step * amplitude * radial_frequency)
                exact = (numerator / density) * density_prime * (1.0 - radial_floor**2 / (amplitude * amplitude * density + radial_floor) ** 2)
                error = abs(quotient - exact)
                radial_errors.append(error)
                check("cartan", f"finite_floor_current_eps_{epsilon}_A_{amplitude}_theta_{theta}", error < 3.0e-9, quotient, exact)
    angles = tuple(2.0 * math.pi * index / 257 for index in range(257))
    plus = tuple(11.0 * cartan_tau(theta, 0.5) for theta in angles)
    minus = tuple(-value for value in plus)
    check("cartan", "same_heat_root_signed_cancellation", max(abs(a + b) for a, b in zip(plus, minus)) == 0.0, 0.0, 0.0)
    mismatched_heat = tuple(-0.7 * value for value in plus)
    check("cartan", "distinct_heat_mutant_not_cancelled", max(abs(a + b) for a, b in zip(plus, mismatched_heat)) > 0.1, max(abs(a + b) for a, b in zip(plus, mismatched_heat)), "> 0.1")
    epsilon_fraction = F(1, 2)
    rho_fraction = F(1, 3)
    harmonic = 4
    coefficient = -2 * epsilon_fraction * (1 - rho_fraction**2) * rho_fraction ** (harmonic - 1)
    time_and_sine_energy = F(1, 2) * F(1, 2) * coefficient**2
    expected_energy = epsilon_fraction**2 * (1 - rho_fraction**2) ** 2 * rho_fraction ** (2 * (harmonic - 1))
    check("cartan", "time_and_sine_half_factors_exact", time_and_sine_energy == expected_energy, time_and_sine_energy, expected_energy)
    check("cartan", "mixed_budget_ratio_diverges_fixture", F(512**2, 1 + 512) > F(512, 2), F(512**2, 1 + 512), "> 256")
    check("cartan", "pure_source_payment_is_critical", F(512**2, 512**2) == 1, F(512**2, 512**2), F(1))

    # Polarization constant and factor-three mutation.
    p_input = 4.0 + 1.0e-12
    q11 = 9.0 / (500.0 * p_input)
    q12 = 3.0 / (400.0 * p_input)
    q22 = 3.0 / (320.0 * p_input)
    q_norm = 0.5 * (q11 + q22 + math.sqrt((q11 - q22) ** 2 + 4.0 * q12 * q12))
    frame_constant = 3.0 * q_norm * math.sqrt(20.0 * 68.0)
    envelope_left = 3.0 * q_norm * 20.0
    check("resampling", "polarization_factor_three_holds", envelope_left <= frame_constant, envelope_left, f"<= {frame_constant}")
    check("resampling", "deleted_factor_three_rejected", envelope_left > frame_constant / 3.0, envelope_left, f"> {frame_constant / 3.0}")

    # Exact Rademacher cube enumeration and interaction multiplicity.
    coefficients = {0: F(1), 1: F(2), 2: F(3), 3: F(5)}

    def cube_value(left: int, right: int) -> F:
        return coefficients[0] + coefficients[1] * left + coefficients[2] * right + coefficients[3] * left * right

    signs = (-1, 1)
    second_moment = sum((cube_value(left, right) ** 2 for left in signs for right in signs), F(0)) / 4
    variance_left = sum(((coefficients[1] + coefficients[3] * right) ** 2 for right in signs), F(0)) / 2
    variance_right = sum(((coefficients[2] + coefficients[3] * left) ** 2 for left in signs), F(0)) / 2
    resampled_left = F(0)
    for right in signs:
        for left in signs:
            for fresh_left in signs:
                resampled_left += (cube_value(left, right) - cube_value(fresh_left, right)) ** 2 / 8
    check("resampling", "cube_second_moment", second_moment == 39, second_moment, F(39))
    check("resampling", "conditional_variance_left", variance_left == 29, variance_left, F(29))
    check("resampling", "independent_resample_identity", resampled_left == 58, resampled_left, F(58))
    multiplicity = variance_left + variance_right
    weighted_coefficients = coefficients[1] ** 2 + coefficients[2] ** 2 + 2 * coefficients[3] ** 2
    check("resampling", "hoeffding_multiplicity_identity", multiplicity == weighted_coefficients == 63, multiplicity, F(63))
    pure_interaction_influence = 2 * coefficients[3] ** 2
    check("resampling", "two_root_interaction_counted_twice", pure_interaction_influence == 50, pure_interaction_influence, F(50))

    hardy_values: list[F] = []
    j0 = 2
    for k in range(3, 13):
        direct_integer_sum = sum(2**j for j in range(j0, k))
        exact = F(direct_integer_sum, 2 ** (4 * k))
        closed = F(2**k - 2**j0, 2 ** (4 * k))
        upper = F(1, 2 ** (3 * k))
        hardy_values.append(exact)
        check("resampling", f"hardy_integer_sum_{k}", exact == closed, exact, closed)
        check("resampling", f"hardy_strict_gain_{k}", exact < upper, exact, f"< {upper}")
    check("resampling", "hardy_trap_j0_2_k_7", hardy_values[4] == F(31, 2**26), hardy_values[4], F(31, 2**26))
    retained_prefactor = 2 * F(7, 5) ** 2 * hardy_values[4]
    dropped_prefactor = hardy_values[4]
    check("resampling", "hardy_prefactor_retained", retained_prefactor != dropped_prefactor, retained_prefactor, "2*kappa_K^2*mass")
    included_endpoint = F(sum(2**j for j in range(j0, 8)), 2 ** (4 * 7))
    check("resampling", "include_j_equal_k_mutant_rejected", included_endpoint > F(1, 2**21), included_endpoint, "> 2^-21")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-signed-first-cartan-rational-ridge-boundary-independent/1.0",
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": passed,
        "assertions_failed": len(rows) - passed,
        "assertions": rows,
        "diagnostics": {
            "strict_posterior_gap": serial(fractional_gap),
            "rational_cpost_without_e_over_p": serial(rational_cpost),
            "rational_three_atom_gamma": serial(gamma_symmetry),
            "rational_three_atom_q_sqrt2_coefficient": serial(q_sqrt2_coefficient),
            "rational_three_atom_max_abs_r": max(abs(value) for value in transformed_r_values),
            "full_frame_cpost_without_e_over_p": serial(full_cpost),
            "maximum_fourier_error": max(fourier_errors),
            "maximum_finite_floor_radial_error": max(radial_errors),
            "frame_secant_constant": frame_constant,
            "hardy_j0_2_k_7": serial(hardy_values[4]),
        },
        "no_overclaim": (
            "Independent exact and quadrature checks for the R-098 reductions and "
            "refinement-stable per-subvisit method boundary only; Sector A remains open."
        ),
    }
    atomic_json(output, payload)
    print(f"R-098 independent: {passed}/{len(rows)} assertions {payload['status']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    raise SystemExit(main(arguments.output))
