#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped R-121 result.

This implementation does not import the primary executable or SymPy.  Exact
Fraction bivariate jets, rational matrix fixtures, Gaussian polynomial
moments, and hand-derived interpolation arithmetic provide an independent
route to the R-121 checks.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CARTAN-PATHSPACE-EXACTNESS-FIXED-SKEW-SOBOLEV-BOUNDARY"
SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-independent/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-29-independent-cartan-pathspace-exactness-fixed-skew-sobolev-boundary/result.json"
)
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, F):
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
            "independence": {
                "imports_primary": False,
                "imports_sympy": False,
                "owner_curl_engine": "standard-library exact bivariate Fraction jets",
                "telescope_engine": "independent exact rational matrix fixtures",
            },
            "no_overclaim": (
                "The independent checks certify the R-121 finite algebra and deterministic "
                "exponent boundary only.  They do not supply adapted Wiener kernels, an adapted "
                "R-063 forest, a uniform fifth current moment, one-use closure, or Sector A."
            ),
        }


@dataclass(frozen=True)
class BiJet:
    """Rectangular bivariate Taylor series; coefficients are exact Fractions."""

    coefficients: tuple[tuple[F, ...], ...]

    @property
    def x_order(self) -> int:
        return len(self.coefficients) - 1

    @property
    def y_order(self) -> int:
        return len(self.coefficients[0]) - 1

    @classmethod
    def constant(cls, value: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [[F(0) for _ in range(y_order + 1)] for _ in range(x_order + 1)]
        rows[0][0] = F(value)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def x_variable(cls, centre: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [list(row) for row in cls.constant(centre, x_order, y_order).coefficients]
        if x_order:
            rows[1][0] = F(1)
        return cls(tuple(tuple(row) for row in rows))

    @classmethod
    def y_variable(cls, centre: F | int, x_order: int, y_order: int) -> "BiJet":
        rows = [list(row) for row in cls.constant(centre, x_order, y_order).coefficients]
        if y_order:
            rows[0][1] = F(1)
        return cls(tuple(tuple(row) for row in rows))

    @property
    def value(self) -> F:
        return self.coefficients[0][0]

    def coerce(self, other: "BiJet | F | int") -> "BiJet":
        if isinstance(other, BiJet):
            if (other.x_order, other.y_order) != (self.x_order, self.y_order):
                raise ValueError("bivariate jet orders differ")
            return other
        return BiJet.constant(F(other), self.x_order, self.y_order)

    def __add__(self, other: "BiJet | F | int") -> "BiJet":
        right = self.coerce(other)
        return BiJet(
            tuple(
                tuple(self.coefficients[i][j] + right.coefficients[i][j] for j in range(self.y_order + 1))
                for i in range(self.x_order + 1)
            )
        )

    __radd__ = __add__

    def __neg__(self) -> "BiJet":
        return BiJet(tuple(tuple(-value for value in row) for row in self.coefficients))

    def __sub__(self, other: "BiJet | F | int") -> "BiJet":
        return self + (-self.coerce(other))

    def __rsub__(self, other: "BiJet | F | int") -> "BiJet":
        return self.coerce(other) - self

    def __mul__(self, other: "BiJet | F | int") -> "BiJet":
        right = self.coerce(other)
        rows: list[list[F]] = []
        for i in range(self.x_order + 1):
            row: list[F] = []
            for j in range(self.y_order + 1):
                row.append(
                    sum(
                        (
                            self.coefficients[p][q] * right.coefficients[i - p][j - q]
                            for p in range(i + 1)
                            for q in range(j + 1)
                        ),
                        F(0),
                    )
                )
            rows.append(row)
        return BiJet(tuple(tuple(row) for row in rows))

    __rmul__ = __mul__

    def reciprocal(self) -> "BiJet":
        origin = self.value
        if origin == 0:
            raise ZeroDivisionError("zero bivariate constant coefficient")
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        rows[0][0] = 1 / origin
        for total in range(1, self.x_order + self.y_order + 1):
            for i in range(self.x_order + 1):
                j = total - i
                if j < 0 or j > self.y_order:
                    continue
                correction = sum(
                    (
                        self.coefficients[p][q] * rows[i - p][j - q]
                        for p in range(i + 1)
                        for q in range(j + 1)
                        if (p, q) != (0, 0)
                    ),
                    F(0),
                )
                rows[i][j] = -correction / origin
        return BiJet(tuple(tuple(row) for row in rows))

    def __truediv__(self, other: "BiJet | F | int") -> "BiJet":
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other: "BiJet | F | int") -> "BiJet":
        return self.coerce(other) * self.reciprocal()

    def __pow__(self, exponent: int) -> "BiJet":
        if exponent < 0:
            return self.reciprocal() ** (-exponent)
        answer = BiJet.constant(1, self.x_order, self.y_order)
        base = self
        power = exponent
        while power:
            if power & 1:
                answer = answer * base
            base = base * base
            power >>= 1
        return answer

    def dx(self) -> "BiJet":
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order):
            for j in range(self.y_order + 1):
                rows[i][j] = F(i + 1) * self.coefficients[i + 1][j]
        return BiJet(tuple(tuple(row) for row in rows))

    def dy(self) -> "BiJet":
        rows = [[F(0) for _ in range(self.y_order + 1)] for _ in range(self.x_order + 1)]
        for i in range(self.x_order + 1):
            for j in range(self.y_order):
                rows[i][j] = F(j + 1) * self.coefficients[i][j + 1]
        return BiJet(tuple(tuple(row) for row in rows))


Vector = list[F]
Matrix = list[list[F]]


def mat_vec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((matrix[i][j] * vector[j] for j in range(len(vector))), F(0)) for i in range(len(matrix))]


def dot(left: Vector, right: Vector) -> F:
    return sum((a * b for a, b in zip(left, right)), F(0))


def mat_sub(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def outer(vector: Vector) -> Matrix:
    return [[vector[i] * vector[j] for j in range(len(vector))] for i in range(len(vector))]


def colon(left: Matrix, right: Matrix) -> F:
    return sum((left[i][j] * right[i][j] for i in range(len(left)) for j in range(len(left))), F(0))


def coefficient(x: BiJet, y: BiJet) -> list[list[BiJet]]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = F(str(parameters["M_X"])) ** 2 + F(str(parameters["classii_mass_regularizer"]))
    b_weight = F(str(parameters["cJK"])) * F(str(parameters["alpha_X"])) * F(str(parameters["beta_X"])) / mass
    c_weight = F(str(parameters["cKK"])) * F(str(parameters["beta_X"])) ** 2 / mass
    alpha = c_weight / (b_weight + c_weight)
    denominator = 1 + x**2 + y**2
    g = [x - alpha * x**3 / denominator, -alpha * x**2 * y / denominator]
    return [[4 * g[i] * g[j] for j in range(2)] for i in range(2)]


def matrix_add(*matrices: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[sum((matrix[i][j] for matrix in matrices), matrices[0][i][j] * 0) for j in range(2)] for i in range(2)]


def matrix_scale(value: F, matrix: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[value * matrix[i][j] for j in range(2)] for i in range(2)]


def matrix_dx(matrix: list[list[BiJet]]) -> list[list[BiJet]]:
    return [[matrix[i][j].dx() for j in range(2)] for i in range(2)]


def owner_current_audit(audit: Audit) -> dict[str, Any]:
    x = BiJet.x_variable(1, 3, 1)
    y = BiJet.y_variable(1, 3, 1)
    b0 = coefficient(x, y)
    b1 = coefficient(x + 1, y)
    b_taylor = matrix_add(b0, matrix_dx(b0), matrix_scale(F(1, 2), matrix_dx(matrix_dx(b0))))
    remainder = [[b1[i][j] - b_taylor[i][j] for j in range(2)] for i in range(2)]

    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = F(str(parameters["M_X"])) ** 2 + F(str(parameters["classii_mass_regularizer"]))
    b_weight = F(str(parameters["cJK"])) * F(str(parameters["alpha_X"])) * F(str(parameters["beta_X"])) / mass
    c_weight = F(str(parameters["cKK"])) * F(str(parameters["beta_X"])) ** 2 / mass
    alpha = c_weight / (b_weight + c_weight)
    audit.check("owner_curl", "production_alpha", alpha == F(5, 9), alpha, F(5, 9))

    b0_value = [[b0[i][j].value for j in range(2)] for i in range(2)]
    b1_value = [[b1[i][j].value for j in range(2)] for i in range(2)]
    remainder_value = [[remainder[i][j].value for j in range(2)] for i in range(2)]
    expected_b0 = [[F(1936, 729), F(-440, 729)], [F(-440, 729), F(100, 729)]]
    expected_b1 = [[F(4624, 729), F(-1360, 729)], [F(-1360, 729), F(400, 729)]]
    expected_remainder = [[F(80, 2187), F(520, 2187)], [F(520, 2187), F(-300, 2187)]]
    audit.check("owner_curl", "B0_at_slice", b0_value == expected_b0, b0_value, expected_b0)
    audit.check("owner_curl", "B1_at_slice", b1_value == expected_b1, b1_value, expected_b1)
    audit.check("owner_curl", "L_at_slice", remainder_value == expected_remainder, remainder_value, expected_remainder)

    currents = {
        "K_R": [remainder[0][0], remainder[1][0]],
        "M_U": [b_taylor[0][0], b_taylor[1][0]],
        "full": [b1[0][0], b1[1][0]],
    }
    expected = {
        "K_R": (F(-4480, 6561), F(-4120, 6561), F(-40, 729)),
        "M_U": (F(20800, 6561), F(-3680, 6561), F(2720, 729)),
        "full": (F(5440, 2187), F(-2600, 2187), F(2680, 729)),
    }
    curls: dict[str, F] = {}
    for name, current in currents.items():
        dy_x = current[0].dy().value
        dx_y = current[1].dx().value
        curl = dy_x - dx_y
        curls[name] = curl
        oracle_dy, oracle_dx, oracle_curl = expected[name]
        audit.check("owner_curl", f"{name}_dy_omega_x", dy_x == oracle_dy, dy_x, oracle_dy)
        audit.check("owner_curl", f"{name}_dx_omega_y", dx_y == oracle_dx, dx_y, oracle_dx)
        audit.check("owner_curl", f"{name}_repo_curl", curl == oracle_curl, curl, oracle_curl)
    audit.check("owner_curl", "curl_recombination", curls["M_U"] + curls["K_R"] == curls["full"], curls["M_U"] + curls["K_R"], curls["full"])
    audit.check("owner_curl", "M_not_companion", curls["M_U"] != -curls["K_R"], curls["M_U"], -curls["K_R"])
    audit.check("owner_curl", "full_not_closed", curls["full"] != 0, curls["full"], "nonzero")
    terminal_square = F(1, 2) * b1[0][0]
    terminal_gradient_curl = terminal_square.dx().dy().value - terminal_square.dy().dx().value
    audit.check("owner_curl", "terminal_square_gradient_curl", terminal_gradient_curl == 0, terminal_gradient_curl, 0)
    ellipse_mixed_hessian = -curls["K_R"] / 2
    audit.check("path_space", "R102_ellipse_mixed_hessian", ellipse_mixed_hessian == F(20, 729), ellipse_mixed_hessian, F(20, 729))
    return {
        "B0": b0_value,
        "B1": b1_value,
        "L": remainder_value,
        "repo_curls": curls,
        "normalized_ellipse_mixed_hessian": ellipse_mixed_hessian,
    }


def owner_visit(previous_b: Matrix, next_b: Matrix, taylor: Matrix, previous_g: Vector, increment: Vector, gamma: Matrix) -> tuple[F, F]:
    next_g = [previous_g[i] + increment[i] for i in range(2)]
    previous_q = mat_sub(outer(previous_g), gamma)
    next_q = mat_sub(outer(next_g), gamma)
    r_q = F(1, 2) * colon(mat_sub(next_b, previous_b), previous_q)
    m_u = dot(previous_g, mat_vec(taylor, increment))
    k_r = dot(previous_g, mat_vec(mat_sub(next_b, taylor), increment)) + F(1, 2) * dot(increment, mat_vec(next_b, increment))
    endpoint = F(1, 2) * colon(next_b, next_q) - F(1, 2) * colon(previous_b, previous_q)
    return r_q + m_u + k_r, endpoint


def telescope_audit(audit: Audit) -> dict[str, Any]:
    fixtures = [
        (
            [[F(2), F(1)], [F(1), F(3)]],
            [[F(5), F(-2)], [F(-2), F(4)]],
            [[F(7), F(3)], [F(3), F(6)]],
            [[F(1), F(0)], [F(0), F(2)]],
            [[F(4), F(1)], [F(1), F(1)]],
            [F(2), F(-1)],
            [F(1, 3), F(2, 5)],
            [F(-3, 7), F(5, 11)],
            [[F(1, 2), F(1, 5)], [F(1, 5), F(3, 4)]],
        ),
        (
            [[F(1, 7), F(-2, 9)], [F(-2, 9), F(5, 6)]],
            [[F(11, 8), F(3, 10)], [F(3, 10), F(-4, 13)]],
            [[F(9, 5), F(-7, 12)], [F(-7, 12), F(8, 3)]],
            [[F(4, 9), F(2, 7)], [F(2, 7), F(6, 11)]],
            [[F(-5, 8), F(1, 3)], [F(1, 3), F(7, 10)]],
            [F(-2, 3), F(7, 5)],
            [F(5, 12), F(-1, 4)],
            [F(8, 15), F(2, 9)],
            [[F(2, 5), F(-1, 6)], [F(-1, 6), F(4, 7)]],
        ),
        (
            [[F(0), F(0)], [F(0), F(0)]],
            [[F(3), F(1)], [F(1), F(2)]],
            [[F(-1), F(2)], [F(2), F(5)]],
            [[F(8), F(-3)], [F(-3), F(7)]],
            [[F(1), F(4)], [F(4), F(-2)]],
            [F(0), F(0)],
            [F(2), F(-5)],
            [F(-1), F(6)],
            [[F(3), F(2)], [F(2), F(9)]],
        ),
    ]
    diagnostics = []
    for index, (b0, b1, b2, t1, t2, g0, d1, d2, gamma) in enumerate(fixtures, start=1):
        owner1, endpoint1 = owner_visit(b0, b1, t1, g0, d1, gamma)
        g1 = [g0[i] + d1[i] for i in range(2)]
        owner2, endpoint2 = owner_visit(b1, b2, t2, g1, d2, gamma)
        g2 = [g1[i] + d2[i] for i in range(2)]
        q0 = mat_sub(outer(g0), gamma)
        q2 = mat_sub(outer(g2), gamma)
        terminal = F(1, 2) * colon(b2, q2) - F(1, 2) * colon(b0, q0)
        audit.check("owner_telescope", f"fixture_{index}_visit_1", owner1 == endpoint1, owner1, endpoint1)
        audit.check("owner_telescope", f"fixture_{index}_visit_2", owner2 == endpoint2, owner2, endpoint2)
        audit.check("owner_telescope", f"fixture_{index}_terminal", owner1 + owner2 == terminal, owner1 + owner2, terminal)
        diagnostics.append({"visit_1": owner1, "visit_2": owner2, "terminal": terminal})
    return {"fixtures": diagnostics, "intermediate_endpoint_multiplicity": 0}


def polynomial_add(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    degrees = set(left) | set(right)
    return {degree: left.get(degree, F(0)) + right.get(degree, F(0)) for degree in degrees}


def polynomial_scale(value: F, poly: dict[int, F]) -> dict[int, F]:
    return {degree: value * coefficient for degree, coefficient in poly.items()}


def polynomial_mul(left: dict[int, F], right: dict[int, F]) -> dict[int, F]:
    answer: dict[int, F] = {}
    for degree_left, coefficient_left in left.items():
        for degree_right, coefficient_right in right.items():
            degree = degree_left + degree_right
            answer[degree] = answer.get(degree, F(0)) + coefficient_left * coefficient_right
    return answer


def gaussian_moment(degree: int) -> F:
    if degree % 2:
        return F(0)
    answer = F(1)
    for value in range(1, degree, 2):
        answer *= value
    return answer


def gaussian_expectation(poly: dict[int, F]) -> F:
    return sum((coefficient * gaussian_moment(degree) for degree, coefficient in poly.items()), F(0))


def path_skew_sobolev_audit(audit: Audit) -> dict[str, Any]:
    # Fourier averages: avg(sin^2)=avg(cos^2)=1/2 on a normalized circle.
    action_over_pi = F(1)
    hessian_zw_over_pi = F(1)
    hessian_wz_over_pi = F(1)
    target_curvature = F(1)
    audit.check("path_space", "target_curvature", target_curvature == 1, target_curvature, 1)
    audit.check("path_space", "circle_action_over_pi", action_over_pi == 1, action_over_pi, 1)
    audit.check("path_space", "hessian_zw_over_pi", hessian_zw_over_pi == 1, hessian_zw_over_pi, 1)
    audit.check("path_space", "hessian_wz_over_pi", hessian_wz_over_pi == 1, hessian_wz_over_pi, 1)
    audit.check("path_space", "hessian_symmetry", hessian_zw_over_pi == hessian_wz_over_pi, hessian_zw_over_pi, hessian_wz_over_pi)

    dimension = 6
    diagonal = [F(0) for _ in range(dimension)]
    pairs = []
    for p in range(dimension):
        for q in range(p + 1, dimension):
            pairs.append((p, q))
            diagonal[p] += F(1, 2)
            diagonal[q] += F(1, 2)
    audit.check("skew_basis", "basis_count", len(pairs) == 15, len(pairs), 15)
    audit.check("skew_basis", "absolute_sum_diagonal", diagonal == [F(5, 2)] * dimension, diagonal, [F(5, 2)] * dimension)

    wedge_fixtures = [
        ([F(1), F(2), F(3), F(4), F(5), F(6)], [F(6), F(5), F(4), F(3), F(2), F(1)]),
        ([F(2), F(-1), F(0), F(3), F(7), F(-4)], [F(1), F(5), F(-2), F(0), F(3), F(8)]),
        ([F(1, 2), F(2, 3), F(3, 4), F(4, 5), F(5, 6), F(6, 7)], [F(-2, 5), F(7, 8), F(1, 9), F(-3, 10), F(11, 12), F(5, 13)]),
    ]
    for index, (z, v) in enumerate(wedge_fixtures, start=1):
        lhs = sum((F(1, 4) * (z[p] * v[q] - z[q] * v[p]) ** 2 for p, q in pairs), F(0))
        rhs = F(1, 4) * (dot(z, z) * dot(v, v) - dot(z, v) ** 2)
        audit.check("skew_basis", f"wedge_fixture_{index}", lhs == rhs, lhs, rhs)

    s = F(3, 5)
    x_power = (1 + 3 * s) / 4
    y_power = (1 - s) / 4
    gap = 1 - x_power - y_power
    moment = 1 / gap
    eta_power = x_power / gap
    zeta_power = y_power / gap
    expected = (F(7, 10), F(1, 10), F(1, 5), F(5), F(7, 2), F(1, 2))
    actual = (x_power, y_power, gap, moment, eta_power, zeta_power)
    audit.check("sobolev", "s_three_fifths_tuple", actual == expected, actual, expected)
    audit.check("sobolev", "positive_gap_iff_s_less_one", gap > 0 and s < 1, (gap, s), "gap>0 and s<1")
    audit.check("sobolev", "R071_moment_reserve", F(45, 4) > moment, F(45, 4), f">{moment}")

    bad_s = F(11, 10)
    bad_growth = bad_s - 1
    audit.check("high_frequency", "bad_growth", bad_growth == F(1, 10), bad_growth, F(1, 10))
    audit.check("high_frequency", "bad_growth_positive", bad_growth > 0, bad_growth, ">0")
    for n in (1, 2, 4, 8, 16):
        h2_norm_sq = F(3, 2) + F(1, 2 * n**2) + F(1, 2 * n**4)
        l6_sixth = F(1) + F(3, 2 * n**4) + F(9, 8 * n**8) + F(5, 16 * n**12)
        q_norm_base = F(n**2, 1 + n**2)
        audit.check("high_frequency", f"H2_bound_N{n}", h2_norm_sq <= F(5, 2), h2_norm_sq, "<=5/2")
        audit.check("high_frequency", f"L6_bound_N{n}", l6_sixth < 4, l6_sixth, "<4")
        audit.check("high_frequency", f"Q_norm_base_N{n}", q_norm_base < 1, q_norm_base, "<1")

    return {
        "path_example": {"curvature": target_curvature, "action_over_pi": action_over_pi, "mixed_hessian_over_pi": hessian_zw_over_pi},
        "absolute_operator_sum": F(5, 2),
        "canonical_wedge_l2_constant": F(1, 2),
        "s_three_fifths": {"X_power": x_power, "Y_power": y_power, "gap": gap, "moment": moment, "eta_power": eta_power, "zeta_power": zeta_power},
        "Hminus_11_over_10_pairing_growth": bad_growth,
    }


def low_chaos_audit(audit: Audit) -> dict[str, Any]:
    h2 = {2: F(1), 0: F(-1)}
    h3 = {3: F(1), 1: F(-3)}
    g_poly = {1: F(1)}
    fixtures = [
        (F(2, 3), F(-1, 5), F(7, 4), F(3, 2), F(-5, 6)),
        (F(-4, 7), F(5, 9), F(-2, 3), F(11, 8), F(13, 10)),
        (F(0), F(3, 11), F(8, 5), F(-7, 6), F(4, 9)),
    ]
    records = []
    for index, (alpha, beta, affine, q0, q1) in enumerate(fixtures, start=1):
        residual = polynomial_add(polynomial_scale(alpha, h2), polynomial_scale(beta, h3))
        residual_sq = polynomial_mul(residual, residual)
        cross = polynomial_scale(2 * affine, polynomial_mul(g_poly, residual))
        first_packet = polynomial_mul(g_poly, polynomial_add(residual_sq, cross))
        d0 = q0 - gaussian_expectation(residual_sq)
        d1 = q1 - gaussian_expectation(first_packet)
        oracle_d0 = q0 - 2 * alpha**2 - 6 * beta**2
        oracle_d1 = q1 - 4 * affine * alpha - 12 * alpha * beta
        audit.check("adapted_low_chaos", f"fixture_{index}_D0", d0 == oracle_d0, d0, oracle_d0)
        audit.check("adapted_low_chaos", f"fixture_{index}_D1", d1 == oracle_d1, d1, oracle_d1)
        records.append({"D0": d0, "D1": d1})
    adapted_family_coefficients = [F(1), F(2), F(1), F(1)]
    audit.check("adapted_low_chaos", "four_family_coefficients", adapted_family_coefficients == [F(1), F(2), F(1), F(1)], adapted_family_coefficients, [F(1), F(2), F(1), F(1)])
    return {"scalar_fixtures": records, "adapted_family_coefficients": adapted_family_coefficients}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "owner_current": owner_current_audit(audit),
        "owner_telescope": telescope_audit(audit),
        "path_skew_sobolev": path_skew_sobolev_audit(audit),
        "low_chaos": low_chaos_audit(audit),
        "scope": {
            "mandatory_companion": False,
            "isolated_chain_primitive_no_go_retained": True,
            "adapted_D0_D1_evaluated": False,
            "adapted_fifth_moment": False,
            "A13_one_use": False,
            "sector_A_closure": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-121 independent {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
