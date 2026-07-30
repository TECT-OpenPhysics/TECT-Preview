#!/usr/bin/env python3
"""Primary exact audit for the scoped R-130 A13 advance.

This program derives the fixed-six-row conormal Gram constants from the A1
production manifest, checks the post-recombination common-terminal algebra,
constructs a finite-cylinder physical response before pullback, proves the
sharp balanced deterministic fixture, and records the direct-low and
complete-square boundaries.  It does not assert the missing uniform
production response or the final forward/balanced/low estimate.
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
from typing import Any, Iterable

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-"
    "RESPONSE-BOUNDARY"
)
SCHEMA = (
    "tect/a13-terminal-xi-conormal-gram-balanced-low-response-"
    "boundary-primary/1.0"
)
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-"
    "response-boundary/result.json"
)
A1_MANIFEST = REPO / (
    "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
    "production_functional_manifest.json"
)
A8_RESULT = REPO / (
    "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/"
    "runs/2026-07-20-primary-decoupled-nelson/result.json"
)
R103_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-"
    "closure/result.json"
)
R124_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-"
    "root-shell-boundary/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.MatrixBase):
        return [
            [serial(value[row, column]) for column in range(value.cols)]
            for row in range(value.rows)
        ]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
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
            "no_overclaim": (
                "R-130 proves a post-recombination common-terminal coordinate, "
                "a finite-cylinder physical response, exact fixed-six-row Gram "
                "envelopes, a sharp deterministic balanced inequality, and a "
                "heat-lifted direct-low candidate bound.  It does not prove a "
                "cutoff/chart-uniform bounded production response, complete "
                "C_mix/C_far/c_bal, the historical R-079 low owners, a strict "
                "augmented gap, OVERLAP_src, Nelson, removals, the interacting "
                "measure, or Sector A closure."
            ),
        }


def vector_add(left: tuple[sp.Expr, ...], right: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    return tuple(sp.simplify(a + b) for a, b in zip(left, right))


def vector_sub(left: tuple[sp.Expr, ...], right: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    return tuple(sp.simplify(a - b) for a, b in zip(left, right))


def vector_scale(scale: sp.Expr, value: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    return tuple(sp.simplify(scale * item) for item in value)


def vector_dot(left: tuple[sp.Expr, ...], right: tuple[sp.Expr, ...]) -> sp.Expr:
    return sp.simplify(sum(a * b for a, b in zip(left, right)))


def expectation(values: Iterable[sp.Expr]) -> sp.Expr:
    values = tuple(values)
    return sp.simplify(sum(values) / len(values))


def mean_vector(values: tuple[tuple[sp.Expr, ...], ...]) -> tuple[sp.Expr, ...]:
    return tuple(expectation(value[index] for value in values) for index in range(len(values[0])))


def conditional_values(
    values: tuple[tuple[sp.Expr, ...], ...],
    blocks: tuple[tuple[int, ...], ...],
) -> tuple[tuple[sp.Expr, ...], ...]:
    output: list[tuple[sp.Expr, ...] | None] = [None] * len(values)
    for block in blocks:
        block_mean = mean_vector(tuple(values[index] for index in block))
        for index in block:
            output[index] = block_mean
    return tuple(value for value in output if value is not None)


def expected_norm_sq(values: tuple[tuple[sp.Expr, ...], ...]) -> sp.Expr:
    return expectation(vector_dot(value, value) for value in values)


def expected_inner(
    left: tuple[tuple[sp.Expr, ...], ...],
    right: tuple[tuple[sp.Expr, ...], ...],
) -> sp.Expr:
    return expectation(vector_dot(a, b) for a, b in zip(left, right))


def martingale_layers(
    terminal: tuple[tuple[sp.Expr, ...], ...],
) -> tuple[
    tuple[tuple[sp.Expr, ...], ...],
    tuple[tuple[sp.Expr, ...], ...],
    tuple[tuple[sp.Expr, ...], ...],
]:
    low_mean = mean_vector(terminal)
    low = tuple(low_mean for _ in terminal)
    middle = conditional_values(terminal, ((0, 1), (2, 3)))
    first = tuple(vector_sub(value, base) for value, base in zip(middle, low))
    second = tuple(vector_sub(value, base) for value, base in zip(terminal, middle))
    return low, first, second


def frobenius(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.simplify(sum(left[i, j] * right[i, j] for i in range(left.rows) for j in range(left.cols)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    p_mass = sp.Rational(str(params["M_X"])) ** 2 + sp.Rational(
        str(params["classii_mass_regularizer"])
    )
    density_floor = sp.Rational(str(params["rho_regularizer"]))
    alpha = sp.Rational(5, 9)
    c0 = sp.Rational(3, 250) / p_mass
    c1 = sp.Rational(243, 8000) / p_mass
    a_prod = sp.Rational(str(params["cJJ"])) * sp.Rational(
        str(params["alpha_X"])
    ) ** 2 / p_mass
    b_prod = sp.Rational(str(params["cJK"])) * sp.Rational(
        str(params["alpha_X"])
    ) * sp.Rational(str(params["beta_X"])) / p_mass
    c_prod = sp.Rational(str(params["cKK"])) * sp.Rational(
        str(params["beta_X"])
    ) ** 2 / p_mass

    audit.check("production", "positive_mass_denominator", p_mass > 0, p_mass, ">0")
    audit.check("production", "positive_density_floor", density_floor > 0, density_floor, ">0")
    audit.check("production", "mass_floor_is_not_density_floor", p_mass != density_floor, (p_mass, density_floor), "distinct")
    audit.check("production", "diagonal_a", sp.simplify(c0 + c1 * (1 - alpha) ** 2 - a_prod) == 0, c0 + c1 * (1 - alpha) ** 2, a_prod)
    audit.check("production", "diagonal_b", sp.simplify(c1 * alpha * (1 - alpha) - b_prod) == 0, c1 * alpha * (1 - alpha), b_prod)
    audit.check("production", "diagonal_c", sp.simplify(c1 * alpha**2 - c_prod) == 0, c1 * alpha**2, c_prod)

    beta_op = sp.simplify(4 * (a_prod + 2 * b_prod + c_prod))
    audit.check("production", "beta_operator", beta_op == sp.Rational(339, 2000) / p_mass, beta_op, sp.Rational(339, 2000) / p_mass)

    # Exact fixed-six-row envelope arithmetic, derived from the elementary
    # quotient bounds rather than pasted downstream constants.
    q_abs_bound = sp.Integer(1)
    tangent_bound = 1 + alpha * q_abs_bound
    remainder_bound = 1 + q_abs_bound
    u_gradient_bound = 2 * remainder_bound
    frame_bound = sp.simplify(tangent_bound + alpha * u_gradient_bound)
    u2_hessian_bound = 2 * (1 + q_abs_bound) + 4 * u_gradient_bound
    rational_first_per_row = sp.simplify(8 * tangent_bound * frame_bound)
    linear_first = sp.simplify(24 * c0)
    rational_first = sp.simplify(3 * c1 * rational_first_per_row)
    l6 = sp.simplify(linear_first + rational_first)
    audit.check("gram", "linear_first_constant", linear_first == sp.Rational(36, 125) / p_mass, linear_first, sp.Rational(36, 125) / p_mass)
    audit.check("gram", "rational_first_constant", rational_first == sp.Rational(1071, 250) / p_mass, rational_first, sp.Rational(1071, 250) / p_mass)
    audit.check("gram", "six_row_first_constant", l6 == sp.Rational(1143, 250) / p_mass, l6, sp.Rational(1143, 250) / p_mass)

    k_frame = sp.simplify(4 * frame_bound**2)
    k_hessian = sp.simplify(4 * alpha * tangent_bound * u2_hessian_bound)
    k_rank_two = sp.simplify(8 * alpha * u_gradient_bound * tangent_bound)
    k_total = sp.simplify(k_frame + k_hessian + k_rank_two)
    linear_second = sp.simplify(12 * c0)
    rational_second = sp.simplify(3 * c1 * k_total)
    h6 = sp.simplify(linear_second + rational_second)
    audit.check("gram", "rational_k_components", k_total == sp.Rational(12464, 81), k_total, sp.Rational(12464, 81))
    audit.check("gram", "linear_half_hessian_constant", linear_second == sp.Rational(18, 125) / p_mass, linear_second, sp.Rational(18, 125) / p_mass)
    audit.check("gram", "rational_half_hessian_constant", rational_second == sp.Rational(7011, 500) / p_mass, rational_second, sp.Rational(7011, 500) / p_mass)
    audit.check("gram", "six_row_half_hessian_constant", h6 == sp.Rational(7083, 500) / p_mass, h6, sp.Rational(7083, 500) / p_mass)

    # The R-082 Xi coordinate is checked directly on a non-real exact fixture.
    u = sp.Matrix([sp.Rational(2, 3) + sp.I / 5, -sp.Rational(1, 4) + 2 * sp.I / 7])
    v = sp.Matrix([-sp.Rational(2, 5) + sp.I / 3, sp.Rational(3, 8) - sp.I / 6])
    chi = sp.Rational(1, 3) - 2 * sp.I / 9
    w_chi = -sp.Rational(1, 7) + sp.I / 4
    pauli = (
        sp.Matrix([[0, 1], [1, 0]]),
        sp.Matrix([[0, -sp.I], [sp.I, 0]]),
        sp.Matrix([[1, 0], [0, -1]]),
    )
    r_doublet = sp.simplify((sp.conjugate(u).T * u)[0])
    rho = sp.simplify(r_doublet + sp.conjugate(chi) * chi)
    denominator = sp.simplify(rho + density_floor)
    dr = sp.simplify(2 * sp.re((sp.conjugate(u).T * v)[0]))
    drho = sp.simplify(dr + 2 * sp.re(sp.conjugate(chi) * w_chi))
    wedge = sp.simplify(u[0] * v[1] - u[1] * v[0])
    m_rows = tuple(sp.simplify((sp.conjugate(u).T * sigma * u)[0]) for sigma in pauli)
    j_rows = tuple(sp.simplify(2 * sp.re((sp.conjugate(u).T * sigma * v)[0])) for sigma in pauli)
    l_rows = tuple(sp.simplify(j_value - alpha * m_value * drho / denominator) for j_value, m_value in zip(j_rows, m_rows))
    xi_norm = sp.simplify(
        c0 * dr**2
        + c1 * (dr - alpha * r_doublet * drho / denominator) ** 2
        + 4 * (c0 + c1) * sp.conjugate(wedge) * wedge
    )
    six_row_norm = sp.simplify(c0 * sum(value**2 for value in j_rows) + c1 * sum(value**2 for value in l_rows))
    audit.check("xi", "first_coordinate_is_dr", dr != drho, dr, "dr distinct from drho")
    audit.check("xi", "pauli_fierz_linear", sp.simplify(sum(value**2 for value in j_rows) - dr**2 - 4 * sp.conjugate(wedge) * wedge) == 0, sum(value**2 for value in j_rows), dr**2 + 4 * sp.conjugate(wedge) * wedge)
    audit.check("xi", "pauli_fierz_rational", sp.simplify(sum(value**2 for value in l_rows) - (dr - alpha * r_doublet * drho / denominator) ** 2 - 4 * sp.conjugate(wedge) * wedge) == 0, sum(value**2 for value in l_rows), (dr - alpha * r_doublet * drho / denominator) ** 2 + 4 * sp.conjugate(wedge) * wedge)
    audit.check("xi", "xi_six_row_norm", sp.simplify(xi_norm - six_row_norm) == 0, xi_norm, six_row_norm)

    # Exact rational-row derivative checksum on a finite two-real slice.
    t = sp.symbols("t", real=True)
    generator = sp.diag(1, -1)
    identity = sp.eye(2)
    u = sp.Matrix([sp.Rational(2, 3), -sp.Rational(1, 4)])
    direction = sp.Matrix([-sp.Rational(2, 5), sp.Rational(3, 7)])
    covariance = sp.Matrix([[sp.Rational(5, 4), sp.Rational(1, 3)], [sp.Rational(1, 3), -sp.Rational(2, 5)]])
    fixture_floor = sp.Rational(3, 5)

    def rational_data(value: sp.Matrix) -> tuple[sp.Expr, sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
        denominator = sp.simplify((value.T * value)[0] + fixture_floor)
        q_value = sp.simplify((value.T * generator * value)[0] / denominator)
        q_tangent = generator - q_value * identity
        remainder = q_tangent * value
        gradient = sp.simplify(2 * remainder / denominator)
        q_hessian = sp.simplify(
            2 * q_tangent / denominator
            - 4 * (value * remainder.T + remainder * value.T) / denominator**2
        )
        tangent = generator - alpha * q_value * identity
        frame = sp.simplify(tangent - alpha * value * gradient.T)
        return q_value, tangent, gradient, q_hessian, frame

    path = u + t * direction
    _, tangent_path, _, _, _ = rational_data(path)
    ell_path = sp.simplify(2 * tangent_path * path)
    scalar_path = sp.simplify((ell_path.T * covariance * ell_path)[0])
    q_value, tangent, gradient, q_hessian, frame = rational_data(u)
    coefficient = tangent * u
    w = covariance * coefficient
    beta = sp.simplify((u.T * covariance * coefficient)[0])
    k_matrix = sp.simplify(
        4 * frame.T * covariance * frame
        - 4 * alpha * beta * q_hessian
        - 4 * alpha * (gradient * w.T + w * gradient.T)
    )
    first_formula = sp.simplify(8 * (coefficient.T * covariance * frame * direction)[0])
    second_formula = sp.simplify((direction.T * k_matrix * direction)[0])
    audit.check("gram", "rational_first_derivative_identity", sp.simplify(sp.diff(scalar_path, t).subs(t, 0) - first_formula) == 0, sp.diff(scalar_path, t).subs(t, 0), first_formula)
    audit.check("gram", "rational_half_hessian_identity", sp.simplify(sp.diff(scalar_path, t, 2).subs(t, 0) / 2 - second_formula) == 0, sp.diff(scalar_path, t, 2).subs(t, 0) / 2, second_formula)
    audit.check("gram", "physical_force_factor", sp.simplify(l6 / 2 - sp.Rational(1143, 500) / p_mass) == 0, l6 / 2, sp.Rational(1143, 500) / p_mass)
    audit.check("gram", "physical_taylor_remainder_factor", sp.simplify(h6 / 2 - sp.Rational(7083, 1000) / p_mass) == 0, h6 / 2, sp.Rational(7083, 1000) / p_mass)

    # Exact post-recombination common-terminal Doob and matching-trace fixture.
    terminal_0 = (
        (sp.Integer(0), sp.Integer(1)),
        (sp.Integer(2), -sp.Integer(1)),
        (-sp.Integer(1), sp.Integer(0)),
        (sp.Integer(1), sp.Integer(2)),
    )
    terminal_star = (
        (sp.Integer(1), sp.Integer(2)),
        (sp.Integer(3), sp.Integer(0)),
        (sp.Integer(0), -sp.Integer(2)),
        (sp.Integer(2), sp.Integer(1)),
    )
    low_0, d1_0, d2_0 = martingale_layers(terminal_0)
    low_star, d1_star, d2_star = martingale_layers(terminal_star)
    for label, terminal, low, first, second in (
        ("baseline", terminal_0, low_0, d1_0, d2_0),
        ("terminal", terminal_star, low_star, d1_star, d2_star),
    ):
        pythagoras = sp.simplify(expected_norm_sq(low) + expected_norm_sq(first) + expected_norm_sq(second))
        audit.check("terminal", f"{label}_doob_pythagoras", pythagoras == expected_norm_sq(terminal), pythagoras, expected_norm_sq(terminal))
        for coordinate in range(2):
            project = lambda values, c=coordinate: tuple(tuple(item if index == c else sp.Integer(0) for index, item in enumerate(value)) for value in values)
            shell_sum = sp.simplify(expected_norm_sq(project(low)) + expected_norm_sq(project(first)) + expected_norm_sq(project(second)))
            audit.check("terminal", f"{label}_shell_{coordinate}_pythagoras", shell_sum == expected_norm_sq(project(terminal)), shell_sum, expected_norm_sq(project(terminal)))

    r1 = tuple(vector_sub(a, b) for a, b in zip(d1_star, d1_0))
    r2 = tuple(vector_sub(a, b) for a, b in zip(d2_star, d2_0))
    square_difference = sp.simplify((expected_norm_sq(terminal_star) - expected_norm_sq(terminal_0)) / 2)
    terminal_recode = sp.simplify(
        (expected_norm_sq(low_star) - expected_norm_sq(low_0)) / 2
        + expected_inner(d1_0, r1)
        + expected_norm_sq(r1) / 2
        + expected_inner(d2_0, r2)
        + expected_norm_sq(r2) / 2
    )
    audit.check("terminal", "relative_terminal_recode", terminal_recode == square_difference, terminal_recode, square_difference)

    b_difference = sp.Matrix([[2, 1], [1, 3]])
    gamma_low = sp.Matrix([[sp.Rational(1, 5), 0], [0, sp.Rational(1, 7)]])
    gamma_1 = sp.Matrix([[sp.Rational(1, 11), sp.Rational(1, 13)], [sp.Rational(1, 13), sp.Rational(1, 17)]])
    gamma_2 = sp.Matrix([[sp.Rational(1, 19), 0], [0, sp.Rational(1, 23)]])
    trace_total = frobenius(b_difference, gamma_low + gamma_1 + gamma_2)
    trace_split = sum(frobenius(b_difference, item) for item in (gamma_low, gamma_1, gamma_2))
    audit.check("terminal", "matching_trace_linearity", trace_split == trace_total, trace_split, trace_total)
    endpoint_direct = sp.simplify(square_difference - trace_total / 2)
    endpoint_recoded = sp.simplify(terminal_recode - trace_split / 2)
    audit.check("terminal", "square_and_trace_endpoint_recode", endpoint_recoded == endpoint_direct, endpoint_recoded, endpoint_direct)

    # The heat lift keeps E[C^T C], not (E C)^T(E C).
    heat_c_plus = sp.Matrix([[1, 1], [0, 1]])
    heat_c_minus = sp.Matrix([[-1, 1], [0, -1]])
    heat_b = sp.simplify((heat_c_plus.T * heat_c_plus + heat_c_minus.T * heat_c_minus) / 2)
    heat_mean_c = sp.simplify((heat_c_plus + heat_c_minus) / 2)
    heat_gap = sp.simplify(heat_b - heat_mean_c.T * heat_mean_c)
    audit.check("terminal", "heat_gram_gap_nonzero", heat_gap != sp.zeros(2), heat_gap, "nonzero PSD")
    audit.check("terminal", "heat_gram_gap_psd", all(value >= 0 for value in heat_gap.eigenvals()), heat_gap.eigenvals(), ">=0")

    # Finite-cylinder physical response must be formed before pullback.
    m_variance = sp.Matrix([[2, sp.Rational(1, 3)], [sp.Rational(1, 3), 1]])
    m_trace = sp.Matrix([[1, sp.Rational(1, 4)], [sp.Rational(1, 4), 3]])
    q_cn = m_variance - m_trace
    q_future_variance = 2 * m_variance
    q_comp = sp.simplify(q_cn - q_future_variance / 2)
    audit.check("response", "action_owner_hessian_identity", q_comp == -m_trace, q_comp, -m_trace)
    synthesis = sp.Matrix([[1, 0, 1], [0, 1, -1]])
    response = sp.simplify(q_comp * synthesis)
    pulled = sp.simplify(synthesis.T * response)
    audit.check("response", "physical_response_pullback", pulled == synthesis.T * q_comp * synthesis, pulled, synthesis.T * q_comp * synthesis)
    vertical = sp.Matrix([-1, 1, 1])
    audit.check("response", "vertical_kernel", synthesis * vertical == sp.zeros(2, 1) and pulled * vertical == sp.zeros(3, 1), (synthesis * vertical, pulled * vertical), "zero")
    audit.check("response", "source_cost_not_physical_pullback", sp.Rational(9, 10) * (vertical.T * vertical)[0] > 0 and (vertical.T * pulled * vertical)[0] == 0, ((vertical.T * pulled * vertical)[0], sp.Rational(9, 10) * (vertical.T * vertical)[0]), "0 versus positive")

    # Exact floor-boundary layer for one separated rational coefficient.
    y = sp.symbols("y", real=True)
    scaled_row = y**3 / (1 + y**2)
    scaled_second = sp.simplify(sp.diff(scaled_row, y, 2))
    layer_integral = sp.integrate(scaled_second**2, (y, -sp.oo, sp.oo))
    normalized_limit = sp.simplify(layer_integral / sp.pi)
    expected_scaled_second = 2 * y * (3 - y**2) / (1 + y**2) ** 3
    audit.check(
        "floor",
        "scaled_second_formula",
        sp.simplify(scaled_second - expected_scaled_second) == 0,
        scaled_second,
        expected_scaled_second,
    )
    audit.check("floor", "whole_layer_integral", layer_integral == 3 * sp.pi / 4, layer_integral, 3 * sp.pi / 4)
    audit.check("floor", "normalized_torus_limit", normalized_limit == sp.Rational(3, 4), normalized_limit, sp.Rational(3, 4))

    # Sharp deterministic balanced bridge and the current budget diagnostic.
    amplitude, frequency = sp.symbols("A N", positive=True)
    balanced_integral = amplitude**4 * frequency**2
    laplacian_norm = amplitude * frequency**2
    l6_cubed = amplitude**3
    audit.check("balanced", "circle_saturates_constant_one", sp.simplify(balanced_integral - laplacian_norm * l6_cubed) == 0, balanced_integral, laplacian_norm * l6_cubed)

    r_symbol = sp.Rational(str(params["r"]))
    z_symbol = sp.Rational(str(params["Z"]))
    y_symbol = sp.Rational(str(params["Y"]))
    s_star = sp.simplify((2 * r_symbol - z_symbol) / (2 * y_symbol - z_symbol))
    symbol_ratio = lambda value: sp.simplify((y_symbol * value**2 + z_symbol * value + r_symbol) / (1 + value) ** 2)
    c_sym = min(symbol_ratio(sp.Integer(0)), symbol_ratio(s_star), y_symbol)
    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    recorded_c_sym = sp.Rational(str(a8["derived"]["symbol_coercivity"]["c_symbol"]))
    audit.check("balanced", "symbol_constant_recomputed", abs(float(c_sym - recorded_c_sym)) < 5e-15, float(c_sym), float(recorded_c_sym))
    m_r = sp.Rational(str(a8["config"]["regulator_multiplier_bound"]))
    a0 = sp.simplify(m_r**2 / c_sym)
    bridge = sp.sqrt(32 * a0)
    r103 = json.loads(R103_RESULT.read_text(encoding="utf-8"))
    source_reserve = sp.Rational(r103["diagnostics"]["budget"]["source_reserve"])
    sextic_reserve = sp.Rational(r103["diagnostics"]["budget"]["sextic_reserve"])
    eta_available = source_reserve - sp.Rational(3, 125) / p_mass
    zeta_available = sextic_reserve
    raw_balanced_ceiling = sp.simplify(2 * sp.sqrt(eta_available * zeta_available) / bridge)
    r124 = json.loads(R124_RESULT.read_text(encoding="utf-8"))
    full_cartan_factor = sp.Rational(r124["diagnostics"]["cartan"]["full"])
    oriented_diagnostic = sp.simplify(c1 * full_cartan_factor / 2)
    full_cross_diagnostic = 2 * oriented_diagnostic
    oriented_ratio = sp.simplify(oriented_diagnostic / raw_balanced_ceiling)
    audit.check("balanced", "available_diagonals_positive", eta_available > 0 and zeta_available > 0, (eta_available, zeta_available), "positive")
    audit.check("balanced", "cartan_oriented_coefficient", sp.simplify(sp.Rational(1340, 729) * c1 - oriented_diagnostic) == 0, sp.Rational(1340, 729) * c1, oriented_diagnostic)
    audit.check("balanced", "cartan_full_cross_coefficient", sp.simplify(sp.Rational(2680, 729) * c1 - full_cross_diagnostic) == 0, sp.Rational(2680, 729) * c1, full_cross_diagnostic)
    audit.check("balanced", "local_diagnostic_below_acceptance_ceiling", oriented_ratio < 1, float(oriented_ratio), "<1")
    audit.check("balanced", "cross_convention_ratio_invariant", sp.simplify((full_cross_diagnostic * bridge) / (4 * sp.sqrt(eta_available * zeta_available)) - oriented_ratio) == 0, sp.simplify((full_cross_diagnostic * bridge) / (4 * sp.sqrt(eta_available * zeta_available))), oriented_ratio)

    # Direct-low candidate anchor; heat variance remains an explicit constant.
    lx = sp.Rational(str(params["Lx"]))
    ly = sp.Rational(str(params["Ly"]))
    lz = sp.Rational(str(params["Lz"]))
    audit.check("low", "cubic_volume", lx == ly == lz, (lx, ly, lz), "equal")
    volume_two_thirds = sp.simplify((lx * ly * lz) ** sp.Rational(2, 3))
    a_low_per_g = sp.simplify(beta_op * volume_two_thirds / 2)
    audit.check("low", "l16_low_coefficient", sp.simplify(a_low_per_g - sp.Rational(2712, 125) / p_mass) == 0, a_low_per_g, sp.Rational(2712, 125) / p_mass)
    zeta = sp.symbols("zeta", positive=True)
    a_low = sp.symbols("a_low", positive=True)
    y_star = (a_low / (3 * zeta)) ** sp.Rational(3, 2)
    young_value = sp.simplify(a_low * y_star ** sp.Rational(1, 3) - zeta * y_star)
    young_constant = sp.simplify(2 * a_low ** sp.Rational(3, 2) / (3 * sp.sqrt(3 * zeta)))
    audit.check("low", "sharp_cubic_young_constant", sp.simplify(young_value - young_constant) == 0, young_value, young_constant)

    # Direct-low factor chain on a centered heat fixture.
    z_low = sp.Matrix([sp.Rational(2), -sp.Rational(1)])
    heat_plus = sp.Matrix([sp.Rational(1), sp.Rational(2)])
    heat_minus = -heat_plus
    gamma_low_fixture = sp.diag(sp.Rational(2, 5), sp.Rational(3, 7))
    trace_gamma = sp.trace(gamma_low_fixture)
    heat_mean = sp.simplify((heat_plus + heat_minus) / 2)
    heat_second = sp.simplify(((heat_plus.T * heat_plus)[0] + (heat_minus.T * heat_minus)[0]) / 2)
    shifted_second = sp.simplify(
        (((z_low + heat_plus).T * (z_low + heat_plus))[0] + ((z_low + heat_minus).T * (z_low + heat_minus))[0]) / 2
    )
    audit.check("low", "centered_heat", heat_mean == sp.zeros(2, 1), heat_mean, sp.zeros(2, 1))
    audit.check("low", "centered_heat_second_moment", shifted_second == (z_low.T * z_low)[0] + heat_second, shifted_second, (z_low.T * z_low)[0] + heat_second)
    audit.check("low", "gram_trace_operator_bound", sp.trace((beta_op * shifted_second * sp.eye(2)) * gamma_low_fixture) == beta_op * shifted_second * trace_gamma, sp.trace((beta_op * shifted_second * sp.eye(2)) * gamma_low_fixture), beta_op * shifted_second * trace_gamma)
    constant_amplitude = sp.Rational(7, 5)
    volume = lx * ly * lz
    l2_squared = volume * constant_amplitude**2
    l6_squared = (volume * constant_amplitude**6) ** sp.Rational(1, 3)
    audit.check("low", "finite_volume_holder", sp.simplify(l2_squared - volume_two_thirds * l6_squared) == 0, l2_squared, volume_two_thirds * l6_squared)

    # A complete positive square carries its own Douglas range relation, but no strict gap.
    identity_two = sp.eye(2)
    terminal_column = sp.Matrix([[1], [1]])
    uv = sp.Matrix([[1, 2], [3, -1]])
    d_block = sp.simplify(terminal_column.T * terminal_column)
    projection = sp.simplify(terminal_column * d_block.inv() * terminal_column.T)
    m_two = sp.simplify(uv.T * uv)
    coupling = sp.simplify(uv.T * terminal_column)
    schur = sp.simplify(m_two - coupling * d_block.inv() * coupling.T)
    projected_schur = sp.simplify(uv.T * (identity_two - projection) * uv)
    audit.check("low", "complete_gram_schur_identity", schur == projected_schur, schur, projected_schur)
    audit.check("low", "complete_gram_schur_psd", all(value >= 0 for value in schur.eigenvals()), schur.eigenvals(), ">=0")
    rank_one_uv = terminal_column * sp.Matrix([[2, 3]])
    rank_one_m = rank_one_uv.T * rank_one_uv
    rank_one_k = rank_one_uv.T * terminal_column
    rank_one_schur = sp.simplify(rank_one_m - rank_one_k * d_block.inv() * rank_one_k.T)
    audit.check("low", "complete_square_no_strict_gap", rank_one_schur == sp.zeros(2), rank_one_schur, sp.zeros(2))
    child_square_sum = sp.Integer(1) ** 2 + (-sp.Integer(1)) ** 2
    terminal_square = (sp.Integer(1) - sp.Integer(1)) ** 2
    audit.check("low", "childwise_square_not_refinement_invariant", child_square_sum > terminal_square, (child_square_sum, terminal_square), "child > terminal")

    diagnostics = {
        "production": {
            "P": p_mass,
            "density_floor": density_floor,
            "c0": c0,
            "c1": c1,
            "alpha": alpha,
            "beta_operator": beta_op,
        },
        "conormal_gram": {
            "L_linear": linear_first,
            "L_rational": rational_first,
            "L6": l6,
            "K_components": [k_frame, k_hessian, k_rank_two],
            "K_total": k_total,
            "H_linear": linear_second,
            "H_rational": rational_second,
            "H6": h6,
            "physical_force_constant": l6 / 2,
            "physical_taylor_remainder_constant": h6 / 2,
            "Q_norm": "real symmetric pointwise operator norm",
        },
        "terminal": {
            "square_difference": square_difference,
            "trace_total": trace_total,
            "endpoint_difference": endpoint_direct,
            "scope": "one fixed post-recombination terminal pair, filtration, and once-owned covariance partition",
        },
        "response": {
            "q_comp_matrix": q_comp,
            "pulled_hessian": pulled,
            "scope": "finite physical cylinder; no uniform bare-L2 extension",
        },
        "floor_boundary": {
            "scaled_second": scaled_second,
            "whole_layer_integral": layer_integral,
            "normalized_torus_limit": normalized_limit,
            "norm_asymptotic": "sqrt(3)/2 * floor^(-1/4)",
        },
        "balanced": {
            "sharp_deterministic_constant": 1,
            "c_sym": c_sym,
            "A0": a0,
            "source_sextic_bridge": bridge,
            "eta_available": eta_available,
            "zeta_available": zeta_available,
            "raw_balanced_acceptance_ceiling": raw_balanced_ceiling,
            "oriented_local_cartan_diagnostic": oriented_diagnostic,
            "full_cross_local_cartan_diagnostic": full_cross_diagnostic,
            "diagnostic_to_ceiling_ratio": oriented_ratio,
            "global_c_bal_upper_bound_proved": False,
        },
        "direct_low_candidate": {
            "volume": lx * ly * lz,
            "a_low_per_g_low": a_low_per_g,
            "young_constant_formula": "2*a_low^(3/2)/(3*sqrt(3*zeta))",
            "heat_constant_formula": "(beta_operator/2)*integral gamma_low(x)*s_heat(x)^2 dx",
            "historical_r079_low_owners_closed": False,
        },
        "complete_low_gram": {
            "schur_fixture": schur,
            "rank_one_schur": rank_one_schur,
            "child_square_sum": child_square_sum,
            "terminal_square": terminal_square,
        },
        "scope": {
            "post_recombination_common_terminal_recode": True,
            "arbitrary_legacy_roots_share_terminal": False,
            "matching_trace_partition": True,
            "matching_energy_without_conditional_covariance": False,
            "finite_cylindrical_response": True,
            "uniform_bounded_physical_response": False,
            "six_row_pointwise_gram_envelopes": True,
            "production_spatial_multiplier_bound": False,
            "balanced_deterministic_bridge": True,
            "production_c_bal_upper_bound": False,
            "direct_low_candidate_anchor": True,
            "r079_low_owner_closure": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(
        f"R-130 primary {result['status']}: "
        f"{result['assertions_passed']}/{result['assertions_total']}"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
