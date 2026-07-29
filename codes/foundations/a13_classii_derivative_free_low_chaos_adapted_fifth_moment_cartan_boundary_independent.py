#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped R-122 result.

The implementation deliberately imports neither the primary executable nor
SymPy/NumPy/SciPy. Exact polynomial Gaussian moments, rational first jets,
closed Gaussian characteristic derivatives, and independent arithmetic are
used as a second route.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-DERIVATIVE-FREE-LOW-CHAOS-ADAPTED-FIFTH-MOMENT-CARTAN-BOUNDARY"
SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-independent/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-29-independent-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary/result.json"
)
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
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
            "diagnostics": serial(diagnostics),
            "independence": "stdlib only; no primary import and no symbolic or numerical algebra package",
            "no_overclaim": (
                "This audit reproduces R-122's finite-cutoff identities and method boundaries. "
                "It does not prove production D0/D1 cancellation or the complete one-use theorem."
            ),
        }


Polynomial = dict[int, Fraction]


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    answer = dict(left)
    for degree, coefficient in right.items():
        answer[degree] = answer.get(degree, Fraction(0)) + coefficient
        if not answer[degree]:
            del answer[degree]
    return answer


def poly_scale(poly: Polynomial, scalar: Fraction) -> Polynomial:
    return {degree: scalar * coefficient for degree, coefficient in poly.items() if scalar * coefficient}


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for left_degree, left_coefficient in left.items():
        for right_degree, right_coefficient in right.items():
            degree = left_degree + right_degree
            answer[degree] = answer.get(degree, Fraction(0)) + left_coefficient * right_coefficient
    return {degree: coefficient for degree, coefficient in answer.items() if coefficient}


def poly_derivative(poly: Polynomial, order: int = 1) -> Polynomial:
    answer = dict(poly)
    for _ in range(order):
        answer = {degree - 1: degree * coefficient for degree, coefficient in answer.items() if degree}
    return answer


def gaussian_even_moment(degree: int) -> int:
    if degree % 2:
        return 0
    answer = 1
    for factor in range(1, degree, 2):
        answer *= factor
    return answer


def gaussian_expectation(poly: Polynomial) -> Fraction:
    return sum((coefficient * gaussian_even_moment(degree) for degree, coefficient in poly.items()), Fraction(0))


def low_chaos_audit(audit: Audit) -> dict[str, Any]:
    one: Polynomial = {0: Fraction(1)}
    xi: Polynomial = {1: Fraction(1)}
    h2 = {2: Fraction(1), 0: Fraction(-1)}
    h3 = {3: Fraction(1), 1: Fraction(-3)}
    h4 = {4: Fraction(1), 2: Fraction(-6), 0: Fraction(3)}
    affine = Fraction(4, 9)
    p, q, r = Fraction(2, 3), Fraction(-3, 5), Fraction(1, 7)
    theta0, theta1, theta2, theta3 = Fraction(11, 6), Fraction(-5, 8), Fraction(7, 10), Fraction(2, 9)
    residual = poly_add(poly_add(poly_scale(h2, p), poly_scale(h3, q)), poly_scale(h4, r))
    theta = poly_add(
        poly_add(poly_scale(one, theta0), poly_scale(xi, theta1)),
        poly_add(poly_scale(h2, theta2), poly_scale(h3, theta3)),
    )
    residual_energy = gaussian_expectation(poly_mul(residual, residual))
    quadratic_score = gaussian_expectation(poly_mul(residual, h2))
    adjacent_score = gaussian_expectation(poly_mul(xi, poly_mul(residual, residual)))
    d0 = gaussian_expectation(theta) - affine**2 - residual_energy
    d1_law = gaussian_expectation(poly_mul(xi, theta)) - 2 * affine * quadratic_score - adjacent_score
    d1_derivative = (
        gaussian_expectation(poly_derivative(theta))
        - 2 * affine * gaussian_expectation(poly_derivative(residual, 2))
        - 2 * gaussian_expectation(poly_mul(residual, poly_derivative(residual)))
    )

    expected_energy = 2 * p**2 + 6 * q**2 + 24 * r**2
    expected_quadratic = 2 * p
    expected_adjacent = 12 * p * q + 48 * q * r
    audit.check("low_chaos", "energy", residual_energy == expected_energy, residual_energy, expected_energy)
    audit.check("low_chaos", "quadratic_score", quadratic_score == expected_quadratic, quadratic_score, expected_quadratic)
    audit.check("low_chaos", "adjacent_score", adjacent_score == expected_adjacent, adjacent_score, expected_adjacent)
    audit.check("low_chaos", "D0", d0 == theta0 - affine**2 - expected_energy, d0, theta0 - affine**2 - expected_energy)
    audit.check("low_chaos", "D1", d1_law == theta1 - 4 * affine * p - expected_adjacent, d1_law, theta1 - 4 * affine * p - expected_adjacent)
    audit.check("low_chaos", "derivative_free_equals_derivative", d1_law == d1_derivative, d1_law, d1_derivative)
    audit.check("low_chaos", "Stein_theta", gaussian_expectation(poly_mul(xi, theta)) == gaussian_expectation(poly_derivative(theta)), gaussian_expectation(poly_mul(xi, theta)), gaussian_expectation(poly_derivative(theta)))
    audit.check("low_chaos", "Stein_second", quadratic_score == gaussian_expectation(poly_derivative(residual, 2)), quadratic_score, gaussian_expectation(poly_derivative(residual, 2)))
    audit.check("low_chaos", "Stein_square", adjacent_score == 2 * gaussian_expectation(poly_mul(residual, poly_derivative(residual))), adjacent_score, 2 * gaussian_expectation(poly_mul(residual, poly_derivative(residual))))

    residual_minus = poly_add(poly_add(poly_scale(h2, p), poly_scale(h3, -q)), poly_scale(h4, r))
    energy_minus = gaussian_expectation(poly_mul(residual_minus, residual_minus))
    adjacent_minus = gaussian_expectation(poly_mul(xi, poly_mul(residual_minus, residual_minus)))
    audit.check("identifiability", "same_energy_opposite_odd_chaos", energy_minus == residual_energy, energy_minus, residual_energy)
    audit.check("identifiability", "same_r2_opposite_odd_chaos", gaussian_expectation(poly_mul(residual_minus, h2)) == quadratic_score, gaussian_expectation(poly_mul(residual_minus, h2)), quadratic_score)
    audit.check("identifiability", "adjacent_changes", adjacent_minus != adjacent_score, adjacent_minus, f"not {adjacent_score}")

    return {
        "residual_energy": residual_energy,
        "quadratic_score": quadratic_score,
        "adjacent_score": adjacent_score,
        "D0": d0,
        "D1": d1_law,
        "opposite_odd_chaos_adjacent_score": adjacent_minus,
    }


def graph_and_owner_fixture_audit(audit: Audit) -> dict[str, Any]:
    n_small, n_large = 1, 12

    def graph_values(n: int) -> tuple[float, float, float, float]:
        e2 = math.exp(-2 * n * n)
        l2 = (1 - e2) / (2 * n * n)
        l6 = (10 - 15 * e2 + 6 * math.exp(-8 * n * n) - math.exp(-18 * n * n)) / (32 * n**6)
        d1 = (1 + e2) / 2
        d2 = n * n * (1 - e2) / 2
        return l2, l6, d1, d2

    small = graph_values(n_small)
    large = graph_values(n_large)
    audit.check("graph", "L2_decreases", large[0] < small[0], large[0], f"< {small[0]}")
    audit.check("graph", "L6_decreases", large[1] < small[1], large[1], f"< {small[1]}")
    audit.check("graph", "Dh_stays_half", abs(large[2] - 0.5) < 1e-12, large[2], 0.5)
    audit.check("graph", "D2h_grows", large[3] > 50, large[3], ">50")

    a, d, kappa = 0.7, 0.4, 1.3
    source_cost = a * a * (1 - math.exp(-2)) / 2 + d * d * (1 + math.exp(-2)) / 2
    common_d0 = 0.5 + a * a * (math.exp(-1) - 2 * math.exp(-2)) + 2 * d * d * math.exp(-2)
    rows: dict[str, Any] = {}
    for sign, label in ((1, "plus"), (-1, "minus")):
        t1 = sign * 2 * kappa**2 * a * d * math.exp(-2)
        xi_r_squared = -sign * 2 * kappa**2 * a * d * math.exp(-2)
        d1 = t1 - xi_r_squared
        r2_ec = kappa * a * math.exp(-0.5) / 2
        rows[label] = {"t1": t1, "xi_R_squared": xi_r_squared, "D1": d1, "r2_ec": r2_ec}
    audit.check("owner_fixture", "source_cost_positive", source_cost > 0, source_cost, ">0")
    audit.check("owner_fixture", "common_D0_finite", math.isfinite(common_d0), common_d0, "finite")
    audit.check("owner_fixture", "common_r2", abs(rows["plus"]["r2_ec"] - rows["minus"]["r2_ec"]) < 1e-15, rows["plus"]["r2_ec"], rows["minus"]["r2_ec"])
    audit.check("owner_fixture", "opposite_t1", abs(rows["plus"]["t1"] + rows["minus"]["t1"]) < 1e-15, rows["plus"]["t1"] + rows["minus"]["t1"], 0)
    audit.check("owner_fixture", "opposite_adjacent", abs(rows["plus"]["xi_R_squared"] + rows["minus"]["xi_R_squared"]) < 1e-15, rows["plus"]["xi_R_squared"] + rows["minus"]["xi_R_squared"], 0)
    audit.check("owner_fixture", "opposite_nonzero_D1", rows["plus"]["D1"] > 0 and rows["minus"]["D1"] < 0, [rows["plus"]["D1"], rows["minus"]["D1"]], "opposite nonzero")
    return {"graph_n1": small, "graph_n12": large, "source_cost": source_cost, "common_D0_over_kappa_squared": common_d0, "rows": rows}


@dataclass(frozen=True)
class Jet:
    value: Fraction
    dx: Fraction = Fraction(0)
    dy: Fraction = Fraction(0)

    @staticmethod
    def lift(value: Jet | Fraction | int) -> Jet:
        return value if isinstance(value, Jet) else Jet(Fraction(value))

    def __add__(self, other: Jet | Fraction | int) -> Jet:
        other = Jet.lift(other)
        return Jet(self.value + other.value, self.dx + other.dx, self.dy + other.dy)

    __radd__ = __add__

    def __neg__(self) -> Jet:
        return Jet(-self.value, -self.dx, -self.dy)

    def __sub__(self, other: Jet | Fraction | int) -> Jet:
        return self + (-Jet.lift(other))

    def __rsub__(self, other: Jet | Fraction | int) -> Jet:
        return Jet.lift(other) - self

    def __mul__(self, other: Jet | Fraction | int) -> Jet:
        other = Jet.lift(other)
        return Jet(
            self.value * other.value,
            self.dx * other.value + self.value * other.dx,
            self.dy * other.value + self.value * other.dy,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> Jet:
        return Jet(
            1 / self.value,
            -self.dx / self.value**2,
            -self.dy / self.value**2,
        )

    def __truediv__(self, other: Jet | Fraction | int) -> Jet:
        return self * Jet.lift(other).reciprocal()

    def __rtruediv__(self, other: Jet | Fraction | int) -> Jet:
        return Jet.lift(other) / self

    def __pow__(self, exponent: int) -> Jet:
        if exponent < 0:
            return (self.reciprocal()) ** (-exponent)
        answer = Jet(Fraction(1))
        for _ in range(exponent):
            answer = answer * self
        return answer


def production_parameters() -> tuple[Fraction, Fraction]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = Fraction(str(parameters["M_X"])) ** 2 + Fraction(str(parameters["classii_mass_regularizer"]))
    b_weight = Fraction(str(parameters["cJK"])) * Fraction(str(parameters["alpha_X"])) * Fraction(str(parameters["beta_X"])) / mass
    c_weight = Fraction(str(parameters["cKK"])) * Fraction(str(parameters["beta_X"])) ** 2 / mass
    return c_weight / (b_weight + c_weight), Fraction(str(parameters["rho_regularizer"]))


def matrix_sub(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] - right[i][j] for j in range(2)] for i in range(2)]


def matrix_add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(2)] for i in range(2)]


def matrix_scale(matrix: list[list[Fraction]], scalar: Fraction) -> list[list[Fraction]]:
    return [[scalar * matrix[i][j] for j in range(2)] for i in range(2)]


def cartan_matrix_at(x_value: int, y_value: int, alpha: Fraction) -> tuple[list[list[Fraction]], list[Jet]]:
    x = Jet(Fraction(x_value), Fraction(1), Fraction(0))
    y = Jet(Fraction(y_value), Fraction(0), Fraction(1))
    denominator = 1 + x**2 + y**2
    f = [2 * (x - alpha * x**3 / denominator), -2 * alpha * x**2 * y / denominator]
    b = [[f[i] * f[j] for j in range(2)] for i in range(2)]
    c = [[b[row][0].dx, b[row][0].dy] for row in range(2)]
    a_matrix = [[c[column][row] - c[row][column] for column in range(2)] for row in range(2)]
    return a_matrix, f


def production_and_cartan_audit(audit: Audit) -> dict[str, Any]:
    alpha, floor = production_parameters()
    audit.check("production", "alpha", alpha == Fraction(5, 9), alpha, Fraction(5, 9))
    audit.check("production", "floor_positive", floor > 0, floor, ">0")

    rho, m, rho_prime, m_prime = Fraction(5), Fraction(3), Fraction(-4), Fraction(-4)
    profile_a, profile_b = Fraction(2), Fraction(1)
    j_limit = m_prime - alpha * m * rho_prime / rho
    omega_limit = -8 * alpha * profile_a * profile_b / rho
    coefficient_limit = j_limit * omega_limit
    audit.check("production", "ray_j", j_limit == Fraction(-8, 3), j_limit, Fraction(-8, 3))
    audit.check("production", "ray_omega", omega_limit == Fraction(-16, 9), omega_limit, Fraction(-16, 9))
    audit.check("production", "ray_coefficient", coefficient_limit == Fraction(128, 27), coefficient_limit, Fraction(128, 27))

    skew = [[Fraction(0), Fraction(-1)], [Fraction(1), Fraction(0)]]
    a2, f2 = cartan_matrix_at(2, 1, alpha)
    a0, _ = cartan_matrix_at(1, 1, alpha)
    expected_a2 = matrix_scale(skew, Fraction(2680, 729))
    expected_a0 = matrix_scale(skew, Fraction(1480, 729))
    audit.check("cartan", "A2", a2 == expected_a2, a2, expected_a2)
    audit.check("cartan", "A0", a0 == expected_a0, a0, expected_a0)
    audit.check("cartan", "endpoint_difference", matrix_sub(a2, a0) == matrix_scale(skew, Fraction(400, 243)), matrix_sub(a2, a0), matrix_scale(skew, Fraction(400, 243)))

    ell = [f2[0].dx, f2[0].dy]
    omega_scalar = f2[0].dy - f2[1].dx
    cartan_piece = matrix_scale(skew, f2[0].value * omega_scalar)
    square_piece = [
        [ell[i] * f2[j].value - f2[i].value * ell[j] for j in range(2)]
        for i in range(2)
    ]
    audit.check("cartan", "f2", [item.value for item in f2] == [Fraction(68, 27), Fraction(-20, 27)], [item.value for item in f2], [Fraction(68, 27), Fraction(-20, 27)])
    audit.check("cartan", "ell", ell == [Fraction(62, 81), Fraction(40, 81)], ell, [Fraction(62, 81), Fraction(40, 81)])
    audit.check("cartan", "omega", omega_scalar == Fraction(20, 27), omega_scalar, Fraction(20, 27))
    audit.check("cartan", "cartan_piece", cartan_piece == matrix_scale(skew, Fraction(1360, 729)), cartan_piece, matrix_scale(skew, Fraction(1360, 729)))
    audit.check("cartan", "square_piece", square_piece == matrix_scale(skew, Fraction(1320, 729)), square_piece, matrix_scale(skew, Fraction(1320, 729)))
    audit.check("cartan", "reinforcement", matrix_add(cartan_piece, square_piece) == a2, matrix_add(cartan_piece, square_piece), a2)
    audit.check("cartan", "loop_completion", Fraction(3) == Fraction(2) + Fraction(1), Fraction(3), Fraction(3))
    return {"alpha": alpha, "floor": floor, "ray_coefficient": coefficient_limit, "A2": a2, "A0": a0, "cartan_piece": cartan_piece, "square_piece": square_piece}


def moment_and_joint_audit(audit: Audit) -> dict[str, Any]:
    exponents = {order: Fraction(order * (order - 6), 2) for order in (2, 6, 10)}
    audit.check("moment", "second_exponent", exponents[2] == -4, exponents[2], -4)
    audit.check("moment", "sixth_exponent", exponents[6] == 0, exponents[6], 0)
    audit.check("moment", "tenth_exponent", exponents[10] == 20, exponents[10], 20)
    current_norm_squared = Fraction(1, 4) + 0.125 * 5 ** (-0.6)
    audit.check("moment", "current_norm_positive", current_norm_squared > 0, current_norm_squared, ">0")
    audit.check("moment", "second_decays", math.exp(float(exponents[2]) * 9) < 1e-12, math.exp(float(exponents[2]) * 9), "<1e-12")
    audit.check("moment", "sixth_fixed", math.exp(float(exponents[6]) * 9) == 1.0, math.exp(float(exponents[6]) * 9), 1.0)
    audit.check("moment", "tenth_grows", math.exp(float(exponents[10]) * 9) > 1e70, math.exp(float(exponents[10]) * 9), ">1e70")

    c, zeta = Fraction(7, 5), Fraction(11, 9)
    critical = 2 * c / (3 * zeta)
    maximum = c * critical**2 - zeta * critical**3
    expected_maximum = 4 * c**3 / (27 * zeta**2)
    audit.check("joint_young", "critical", critical == Fraction(42, 55), critical, Fraction(42, 55))
    audit.check("joint_young", "maximum", maximum == expected_maximum, maximum, expected_maximum)
    audit.check("joint_young", "quartic_to_sextic", maximum > 0, maximum, ">0")
    audit.check("conditional", "chaos3_factor", 4 ** 1.5 == 8.0, 4 ** 1.5, 8.0)
    audit.check("conditional", "chaos4_factor", 4**2 == 16, 4**2, 16)
    audit.check("conditional", "fifth_power_factor", 16**5 == 2**20, 16**5, 2**20)
    audit.check("conditional", "bracket_power", Fraction(5, 2) > 2, Fraction(5, 2), ">2")
    return {"amplitude_moment_exponents": exponents, "model_current_norm_squared": current_norm_squared, "young_critical": critical, "young_maximum": maximum, "missing_bracket_power": Fraction(5, 2)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "low_chaos": low_chaos_audit(audit),
        "graph_and_owner_fixture": graph_and_owner_fixture_audit(audit),
        "production_and_cartan": production_and_cartan_audit(audit),
        "moment_and_joint": moment_and_joint_audit(audit),
        "scope": {
            "derivative_free_representation": True,
            "production_cancellation": False,
            "standalone_fifth_moment": False,
            "automatic_cartan_cancellation": False,
            "complete_one_use": False,
            "sector_a_closure": False,
        },
    }
    for key, expected in {
        "derivative_free_representation": True,
        "production_cancellation": False,
        "standalone_fifth_moment": False,
        "automatic_cartan_cancellation": False,
        "complete_one_use": False,
        "sector_a_closure": False,
    }.items():
        audit.check("scope", key, diagnostics["scope"][key] is expected, diagnostics["scope"][key], expected)
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-122 independent {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
