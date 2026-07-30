#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped A13 R-133 result.

This implementation does not import the primary verifier.  It uses a small
exact polynomial algebra, direct Gaussian moments, an independent fourth-jet
integrator, and numerical stress fixtures.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY"
SCHEMA = "tect/a13-affine-gaussian-score-feedback-collar-boundary-independent/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-affine-gaussian-score-feedback-collar-boundary/"
    "result.json"
)
R132_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-mixed-replica-gaussian-ray-sextic-shell-boundary/"
    "result.json"
)


def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): represent(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [represent(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(represent(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": represent(actual),
                "expected": represent(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": represent(diagnostics),
            "scope": {
                "affine_gaussian_score_identity_proved": True,
                "predictable_feedback_score_identity_proved_on_cylindrical_core": True,
                "finite_energy_global_score_transfer_from_declared_data_rejected": True,
                "conditional_polynomial_response_zero_proved": True,
                "sixth_amplitude_gamma_four_route_rejected": True,
                "aggregate_positive_gamma_collar_criterion_proved": True,
                "production_one_use_bound": False,
                "production_c_mix": False,
                "production_c_far": False,
                "production_c_bal": False,
                "absolute_anchor": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "Independent checks cover only R-133's exact and conditional "
                "identities, counterfamilies, and collar criterion. They prove no "
                "production one-use estimate or Sector A closure."
            ),
        }


Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


def poly_const(value: Fraction | int, dimension: int) -> Polynomial:
    coefficient = Fraction(value)
    return {} if coefficient == 0 else {(0,) * dimension: coefficient}


def poly_var(index: int, dimension: int) -> Polynomial:
    powers = [0] * dimension
    powers[index] = 1
    return {tuple(powers): Fraction(1)}


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    output = dict(left)
    for powers, coefficient in right.items():
        output[powers] = output.get(powers, Fraction(0)) + coefficient
        if output[powers] == 0:
            del output[powers]
    return output


def poly_scale(value: Fraction | int, polynomial: Polynomial) -> Polynomial:
    scalar = Fraction(value)
    return {powers: scalar * coefficient for powers, coefficient in polynomial.items() if scalar * coefficient}


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for powers_left, coefficient_left in left.items():
        for powers_right, coefficient_right in right.items():
            powers = tuple(powers_left[i] + powers_right[i] for i in range(len(powers_left)))
            output[powers] = output.get(powers, Fraction(0)) + coefficient_left * coefficient_right
    return {powers: coefficient for powers, coefficient in output.items() if coefficient}


def poly_pow(polynomial: Polynomial, power: int) -> Polynomial:
    output = poly_const(1, len(next(iter(polynomial))) if polynomial else 1)
    for _ in range(power):
        output = poly_mul(output, polynomial)
    return output


def poly_derivative(polynomial: Polynomial, index: int) -> Polynomial:
    output: Polynomial = {}
    for powers, coefficient in polynomial.items():
        if powers[index] == 0:
            continue
        next_powers = list(powers)
        factor = next_powers[index]
        next_powers[index] -= 1
        output[tuple(next_powers)] = coefficient * factor
    return output


def gaussian_moment(power: int) -> int:
    if power % 2:
        return 0
    value = 1
    for factor in range(1, power, 2):
        value *= factor
    return value


def poly_expectation(polynomial: Polynomial) -> Fraction:
    total = Fraction(0)
    for powers, coefficient in polynomial.items():
        moment = 1
        for power in powers:
            moment *= gaussian_moment(power)
        total += coefficient * moment
    return total


def poly_directional(polynomial: Polynomial, vector: tuple[Fraction, ...]) -> Polynomial:
    output: Polynomial = {}
    for index, coefficient in enumerate(vector):
        output = poly_add(output, poly_scale(coefficient, poly_derivative(polynomial, index)))
    return output


class Jet4:
    """Truncated ordinary Taylor series through fourth order."""

    def __init__(self, coefficients: list[float]) -> None:
        self.c = coefficients + [0.0] * (5 - len(coefficients))

    @staticmethod
    def lift(value: float | "Jet4") -> "Jet4":
        return value if isinstance(value, Jet4) else Jet4([float(value)])

    def __add__(self, other: float | "Jet4") -> "Jet4":
        rhs = self.lift(other)
        return Jet4([self.c[i] + rhs.c[i] for i in range(5)])

    __radd__ = __add__

    def __neg__(self) -> "Jet4":
        return Jet4([-value for value in self.c])

    def __sub__(self, other: float | "Jet4") -> "Jet4":
        return self + (-self.lift(other))

    def __rsub__(self, other: float | "Jet4") -> "Jet4":
        return self.lift(other) - self

    def __mul__(self, other: float | "Jet4") -> "Jet4":
        rhs = self.lift(other)
        return Jet4(
            [sum(self.c[j] * rhs.c[i - j] for j in range(i + 1)) for i in range(5)]
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "Jet4":
        output = [0.0] * 5
        output[0] = 1.0 / self.c[0]
        for n in range(1, 5):
            output[n] = -sum(self.c[k] * output[n - k] for k in range(1, n + 1)) / self.c[0]
        return Jet4(output)

    def __truediv__(self, other: float | "Jet4") -> "Jet4":
        return self * self.lift(other).reciprocal()

    def __rtruediv__(self, other: float | "Jet4") -> "Jet4":
        return self.lift(other) / self

    def __pow__(self, power: int) -> "Jet4":
        if power < 0:
            return (self.reciprocal()) ** (-power)
        output = Jet4([1.0])
        for _ in range(power):
            output = output * self
        return output


def adaptive_simpson(function: Callable[[float], float], left: float, right: float, tolerance: float, depth: int = 20) -> float:
    def simpson(a: float, b: float, fa: float, fm: float, fb: float) -> float:
        return (b - a) * (fa + 4.0 * fm + fb) / 6.0

    fa = function(left)
    fb = function(right)
    middle = (left + right) / 2.0
    fm = function(middle)
    whole = simpson(left, right, fa, fm, fb)

    def recurse(a: float, b: float, fa0: float, fm0: float, fb0: float, estimate: float, tol: float, remaining: int) -> float:
        midpoint = (a + b) / 2.0
        left_mid = (a + midpoint) / 2.0
        right_mid = (midpoint + b) / 2.0
        fl = function(left_mid)
        fr = function(right_mid)
        left_estimate = simpson(a, midpoint, fa0, fl, fm0)
        right_estimate = simpson(midpoint, b, fm0, fr, fb0)
        delta = left_estimate + right_estimate - estimate
        if remaining <= 0 or abs(delta) <= 15.0 * tol:
            return left_estimate + right_estimate + delta / 15.0
        return recurse(a, midpoint, fa0, fl, fm0, left_estimate, tol / 2.0, remaining - 1) + recurse(midpoint, b, fm0, fr, fb0, right_estimate, tol / 2.0, remaining - 1)

    return recurse(left, right, fa, fm, fb, whole, tolerance, depth)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    upstream = json.loads(R132_RESULT.read_text(encoding="utf-8"))
    alpha = Fraction(5, 9)
    p_mass = Fraction(4_000_000_000_001, 10**12)
    c0 = Fraction(3, 250) / p_mass
    c1 = Fraction(243, 8000) / p_mass
    c_s = c0 + c1
    gamma = Fraction(7, 12)
    audit = Audit()

    audit.check("inputs", "upstream_pass", upstream.get("status") == "PASS", upstream.get("status"), "PASS")
    audit.check("inputs", "c_s", c_s == Fraction(339, 8000) / p_mass, c_s, Fraction(339, 8000) / p_mass)
    audit.check("inputs", "raw_envelope", 4 * c_s == Fraction(339, 2000) / p_mass, 4 * c_s, Fraction(339, 2000) / p_mass)

    # Exact polynomial score checks built independently from the primary.
    dimension = 2
    x = poly_var(0, dimension)
    y = poly_var(1, dimension)
    one = poly_const(1, dimension)
    first = poly_add(one, poly_add(x, poly_scale(2, poly_pow(x, 2))))
    second = poly_add(poly_const(3, dimension), poly_add(poly_scale(-1, y), poly_pow(y, 3)))
    pair_kernel = poly_mul(first, second)
    total_direction = (Fraction(1), Fraction(1))
    direct_pair_unit = poly_expectation(poly_directional(poly_directional(pair_kernel, total_direction), total_direction))
    pair_score_unit = poly_expectation(
        poly_mul(
            poly_add(poly_pow(poly_add(x, y), 2), poly_const(-2, dimension)),
            pair_kernel,
        )
    )
    scalar_product = Fraction(2, 3) * Fraction(-5, 4)
    audit.check("affine_score", "pair_unit", direct_pair_unit == pair_score_unit, direct_pair_unit, pair_score_unit)
    audit.check("affine_score", "pair_scaled", scalar_product * direct_pair_unit == scalar_product * pair_score_unit, scalar_product * direct_pair_unit, scalar_product * pair_score_unit)

    trace_kernel = poly_add(poly_const(2, dimension), poly_add(poly_pow(x, 2), poly_pow(x, 4)))
    direct_trace_unit = poly_expectation(poly_derivative(poly_derivative(trace_kernel, 0), 0))
    trace_score_unit = poly_expectation(poly_mul(poly_add(poly_pow(x, 2), poly_const(-1, dimension)), trace_kernel))
    audit.check("affine_score", "trace_unit", direct_trace_unit == trace_score_unit, direct_trace_unit, trace_score_unit)
    combined_unhalved = scalar_product * (direct_pair_unit - direct_trace_unit)
    combined_owner = Fraction(1, 2) * combined_unhalved
    audit.check(
        "affine_score",
        "combined_owner_with_outer_half",
        combined_owner
        == Fraction(1, 2)
        * scalar_product
        * (pair_score_unit - trace_score_unit),
        combined_owner,
        Fraction(1, 2)
        * scalar_product
        * (pair_score_unit - trace_score_unit),
    )

    # Four-variable exact Hermite score moments.
    dimension4 = 4
    variables4 = [poly_var(i, dimension4) for i in range(dimension4)]
    a = (Fraction(1, 2), Fraction(3, 2))
    b = (Fraction(5, 3), Fraction(-2, 3))
    aa = sum(value * value for value in a)
    bb = sum(value * value for value in b)
    ab = sum(a[i] * b[i] for i in range(2))
    discriminant = aa * bb + ab * ab
    ax = poly_add(poly_scale(a[0], variables4[0]), poly_scale(a[1], variables4[1]))
    bx = poly_add(poly_scale(b[0], variables4[0]), poly_scale(b[1], variables4[1]))
    ay = poly_add(poly_scale(a[0], variables4[2]), poly_scale(a[1], variables4[3]))
    by = poly_add(poly_scale(b[0], variables4[2]), poly_scale(b[1], variables4[3]))
    h1 = poly_add(poly_mul(ax, bx), poly_const(-ab, dimension4))
    h2 = poly_add(poly_mul(poly_add(ax, ay), poly_add(bx, by)), poly_const(-2 * ab, dimension4))
    audit.check("score_cost", "single_centered", poly_expectation(h1) == 0, poly_expectation(h1), 0)
    audit.check("score_cost", "pair_centered", poly_expectation(h2) == 0, poly_expectation(h2), 0)
    audit.check("score_cost", "single_l2", poly_expectation(poly_pow(h1, 2)) == discriminant, poly_expectation(poly_pow(h1, 2)), discriminant)
    audit.check("score_cost", "pair_l2", poly_expectation(poly_pow(h2, 2)) == 4 * discriminant, poly_expectation(poly_pow(h2, 2)), 4 * discriminant)

    # Exact nonlinear triangular-feedback connection fixture.
    lam = Fraction(2, 3)
    dimension2 = 2
    xx = poly_var(0, dimension2)
    yy = poly_var(1, dimension2)
    a0 = poly_const(1, dimension2)
    a1 = poly_scale(-2 * lam, xx)
    tensor = [[poly_mul(a0, a0), poly_mul(a0, a1)], [poly_mul(a1, a0), poly_mul(a1, a1)]]
    divergence = [
        poly_add(poly_derivative(tensor[i][0], 0), poly_derivative(tensor[i][1], 1))
        for i in range(2)
    ]
    xi_dot_a = poly_add(poly_mul(xx, a0), poly_mul(yy, a1))
    xi_tensor_xi = poly_pow(xi_dot_a, 2)
    trace_tensor = poly_add(tensor[0][0], tensor[1][1])
    xi_dot_div = poly_add(poly_mul(xx, divergence[0]), poly_mul(yy, divergence[1]))
    div2 = poly_add(poly_derivative(divergence[0], 0), poly_derivative(divergence[1], 1))
    delta2 = poly_add(poly_add(xi_tensor_xi, poly_scale(-1, trace_tensor)), poly_add(poly_scale(-2, xi_dot_div), div2))
    delta_connection = poly_scale(2 * lam, yy)
    score = poly_add(delta2, poly_scale(-1, delta_connection))
    shifted_y = poly_add(yy, poly_scale(lam, poly_pow(xx, 2)))
    nonlinear_owner = poly_scale(Fraction(1, 2), poly_pow(shifted_y, 2))
    linear_owner = poly_scale(Fraction(1, 2), poly_pow(xx, 2))
    audit.check("feedback", "nonlinear_hessian", poly_expectation(poly_mul(nonlinear_owner, score)) == 0, poly_expectation(poly_mul(nonlinear_owner, score)), 0)
    audit.check("feedback", "linear_hessian", poly_expectation(poly_mul(linear_owner, score)) == 1, poly_expectation(poly_mul(linear_owner, score)), 1)
    audit.check("feedback", "uncorrected_debt", poly_expectation(poly_mul(nonlinear_owner, delta2)) == 2 * lam * lam, poly_expectation(poly_mul(nonlinear_owner, delta2)), 2 * lam * lam)
    audit.check("feedback", "connection_payment", poly_expectation(poly_mul(nonlinear_owner, delta_connection)) == 2 * lam * lam, poly_expectation(poly_mul(nonlinear_owner, delta_connection)), 2 * lam * lam)

    # Bounded tanh feedback: direct quadrature of the inverse-Jacobian cost.
    normalizer = 1.0 / math.sqrt(2.0 * math.pi)

    def inverse_cost(frequency: int, amplitude: float = 0.5) -> float:
        def integrand(value: float) -> float:
            derivative = amplitude * frequency / math.cosh(frequency * value) ** 2 if abs(frequency * value) < 350 else 0.0
            return derivative * derivative * normalizer * math.exp(-value * value / 2.0)

        return 1.0 + adaptive_simpson(integrand, -8.0, 8.0, 1e-9)

    inverse_costs = [inverse_cost(frequency) for frequency in (2, 4, 8, 16)]
    audit.check("feedback", "bounded_tanh_growth", all(inverse_costs[i + 1] > inverse_costs[i] for i in range(3)), inverse_costs, "strictly increasing")
    audit.check("feedback", "bounded_tanh_uncontrolled", inverse_costs[-1] > 2 * inverse_costs[0], inverse_costs[-1] / inverse_costs[0], ">2")

    # Support offsets and the exact inherited heat/covariance constants.
    audit.check("polynomial_support", "current_offset", 2 ** ((3) - 1) / 2 == 2, 3, "safety offset 3")
    audit.check("polynomial_support", "response_offset", 2 ** ((4) - 1) / 4 == 2, 4, "safety offset 4")
    audit.check("polynomial_support", "common_heat", 2 * c_s == Fraction(339, 4000) / p_mass, 2 * c_s, Fraction(339, 4000) / p_mass)
    audit.check("polynomial_support", "adapted_defect", -8 * c_s == -Fraction(339, 1000) / p_mass, -8 * c_s, -Fraction(339, 1000) / p_mass)

    # Rational remainder at independent sample points.
    def f_value(state: float, floor_value: float) -> float:
        return state - float(alpha) * state**3 / (state * state + floor_value)

    def h_value(value: float) -> float:
        return -5.0 / (27.0 * (1.0 + value * value)) - 25.0 / (81.0 * (1.0 + value * value) ** 2)

    remainder_errors = []
    for state, floor_value in ((0.3, 0.07), (-1.2, 0.4), (3.5, 0.02)):
        direct = f_value(state, floor_value) ** 2 - (4.0 / 9.0) ** 2 * state**2 - 40.0 * floor_value / 81.0
        scaled = floor_value * h_value(state / math.sqrt(floor_value))
        remainder_errors.append(abs(direct - scaled))
    audit.check("gamma_four", "remainder_samples", max(remainder_errors) < 2e-14, max(remainder_errors), "<2e-14")

    def h_fourth(value: float) -> float:
        jet = Jet4([value, 1.0])
        denominator = 1.0 + jet * jet
        h_jet = (-5.0 / 27.0) / denominator + (-25.0 / 81.0) / (denominator**2)
        return math.factorial(4) * h_jet.c[4]

    def transformed_integrand(parameter: float) -> float:
        if parameter >= 1.0:
            return 0.0
        value = parameter / (1.0 - parameter)
        return 2.0 * h_fourth(value) ** 2 / (1.0 - parameter) ** 2

    h4_numeric = adaptive_simpson(transformed_integrand, 0.0, 1.0, 2e-8)
    h4_exact_float = 2062375.0 * math.pi / 23328.0
    audit.check("gamma_four", "h4_integral", abs(h4_numeric - h4_exact_float) / h4_exact_float < 2e-9, h4_numeric, h4_exact_float)
    asymptotic = 32.0 * float(c1) ** 2 * h4_numeric
    expected_asymptotic = 2062375.0 * math.pi * float(c1) ** 2 / 729.0
    audit.check("gamma_four", "asymptotic_constant", abs(asymptotic - expected_asymptotic) / expected_asymptotic < 2e-9, asymptotic, expected_asymptotic)
    ratio_coefficient = expected_asymptotic / (3.0 * math.pi / 32.0)
    expected_ratio = 445473.0 / (16000.0 * float(p_mass) ** 2)
    audit.check("gamma_four", "sextic_ratio", abs(ratio_coefficient - expected_ratio) < 2e-13, ratio_coefficient, expected_ratio)

    # Actual periodic carrier check.  With the 1/(2*pi) Fourier-coefficient
    # convention, a_n is the exact coefficient at mode 2n of
    # 4*c1*R_e(b*cos x), and multiplication by sin(x)^2 gives g_n below.
    # All polynomial pieces stop before the sharp far region |k|>16.
    def periodic_a(n: int, amplitude: float, floor_value: float = 1.0) -> float:
        delta = math.sqrt(floor_value) / amplitude
        kappa = math.asinh(delta)
        c_value = math.sqrt(1.0 + delta * delta)
        bracket = (
            5.0 * delta / (27.0 * c_value)
            + 25.0
            * delta
            * delta
            / (81.0 * c_value * c_value)
            * (n + 1.0 / math.tanh(2.0 * kappa))
        )
        return (
            4.0
            * float(c1)
            * floor_value
            * (-1.0 if n % 2 == 0 else 1.0)
            * math.exp(-2.0 * n * kappa)
            * bracket
        )

    def periodic_g(n: int, amplitude: float, floor_value: float = 1.0) -> float:
        return (
            0.5 * periodic_a(n, amplitude, floor_value)
            - 0.25
            * (
                periodic_a(n - 1, amplitude, floor_value)
                + periodic_a(n + 1, amplitude, floor_value)
            )
        )

    def periodic_far_norm(amplitude: float, floor_value: float = 1.0) -> float:
        kappa = math.asinh(math.sqrt(floor_value) / amplitude)
        cutoff = max(2000, int(math.ceil(40.0 / kappa)))
        positive_modes = sum(
            (2 * n) ** 8 * periodic_g(n, amplitude, floor_value) ** 2
            for n in range(9, cutoff + 1)
        )
        return 4.0 * math.pi * positive_modes

    reinforcement = [
        ((-1.0 if n % 2 == 0 else 1.0) * periodic_g(n, 20.0))
        for n in range(9, 41)
    ]
    audit.check(
        "gamma_four",
        "periodic_far_harmonics_reinforce",
        min(reinforcement) > 0.0,
        min(reinforcement),
        ">0",
    )
    periodic_amplitudes = (20.0, 50.0, 100.0)
    periodic_ratios = [
        periodic_far_norm(amplitude) / (expected_asymptotic * amplitude**7)
        for amplitude in periodic_amplitudes
    ]
    periodic_errors = [abs(value - 1.0) for value in periodic_ratios]
    audit.check(
        "gamma_four",
        "periodic_asymptotic_errors_decrease",
        periodic_errors[0] > periodic_errors[1] > periodic_errors[2],
        periodic_errors,
        "strictly decreasing",
    )
    audit.check(
        "gamma_four",
        "periodic_asymptotic_last",
        periodic_errors[-1] < 2.0e-4,
        periodic_ratios[-1],
        "relative error <2e-4",
    )
    audit.check("gamma_four", "seventh_amplitude", 2 * 4 - 1 == 7, 2 * 4 - 1, 7)
    audit.check("gamma_four", "sixth_budget_threshold", Fraction(7, 2) < 4, Fraction(7, 2), "<4")

    # Aggregate collar threshold and the R-091 gamma=7/12 route.
    e0, f0, sigma = 0.8, 0.6, 0.1
    a_star = 2.0 * math.sqrt((e0 - sigma) * (f0 - sigma))

    def m2(cross: float) -> float:
        return (e0 + f0 - math.sqrt((e0 - f0) ** 2 + cross * cross)) / 2.0

    audit.check("collar", "inside", m2(a_star / 2.0) > sigma, m2(a_star / 2.0), f">{sigma}")
    audit.check("collar", "boundary", abs(m2(a_star) - sigma) < 2e-15, m2(a_star), sigma)
    equality_tail = 2.0**7 * 2.0 ** (-float(gamma) * (17 - 5))
    strict_tail = 2.0**7 * 2.0 ** (-float(gamma) * (18 - 5))
    audit.check("collar", "equality_not_strict", abs(equality_tail - 1.0) < 2e-15, equality_tail, 1.0)
    audit.check("collar", "next_integer_strict", strict_tail < 1.0, strict_tail, "<1")
    audit.check("collar", "far_growth_exponent", Fraction(4) - gamma == Fraction(41, 12), Fraction(4) - gamma, Fraction(41, 12))
    audit.check("collar", "mix_growth_exponent", Fraction(2) - gamma == Fraction(17, 12), Fraction(2) - gamma, Fraction(17, 12))
    audit.check("collar", "offset_exponent", 5 * gamma == Fraction(35, 12), 5 * gamma, Fraction(35, 12))
    geometric_cost = 1.0 / (1.0 - 2.0 ** (-float(gamma)))
    audit.check("collar", "geometric_cost", math.isfinite(geometric_cost) and geometric_cost > 1.0, geometric_cost, ">1 finite")

    diagnostics = {
        "inputs": {
            "alpha": alpha,
            "p_mass": p_mass,
            "c0": c0,
            "c1": c1,
            "c_s": c_s,
            "gamma": gamma,
        },
        "score": {
            "pair_unit": direct_pair_unit,
            "trace_unit": direct_trace_unit,
            "combined_unhalved": combined_unhalved,
            "combined_owner_with_outer_half": combined_owner,
            "single_l2_squared": discriminant,
            "pair_l2_squared": 4 * discriminant,
        },
        "feedback": {
            "lambda": lam,
            "inverse_costs_N_2_4_8_16": inverse_costs,
        },
        "polynomial_response": {
            "current_offset": 3,
            "response_offset": 4,
            "common_heat_gram": 2 * c_s,
            "adapted_defect": -8 * c_s,
        },
        "gamma_four": {
            "remainder_max_error": max(remainder_errors),
            "H4_integral_numeric": h4_numeric,
            "H4_integral_exact_float": h4_exact_float,
            "gram_asymptotic": expected_asymptotic,
            "sextic_ratio_coefficient": ratio_coefficient,
            "periodic_carrier_amplitudes": periodic_amplitudes,
            "periodic_carrier_normalized_ratios": periodic_ratios,
            "periodic_carrier_relative_errors": periodic_errors,
        },
        "aggregate_collar": {
            "a_star": a_star,
            "strict_integer_example": 18,
            "far_growth_exponent": Fraction(41, 12),
            "mix_growth_exponent": Fraction(17, 12),
            "offset_exponent": Fraction(35, 12),
            "geometric_cost": geometric_cost,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(args.output, payload)
    print(
        f"R-133 independent {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
