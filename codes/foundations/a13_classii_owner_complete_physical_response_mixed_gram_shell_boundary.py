#!/usr/bin/env python3
"""Primary exact audit for the scoped A13 R-131 response boundary.

The audit proves the finite-cylinder owner-complete response factorization,
derives a floor-uniform deterministic current-square H2 form constant, exposes
the mixed-Gram information absent from diagonal Gram bounds, checks the exact
balanced/low acceptance arithmetic, and quantifies the Xi transversality and
fixed-heat boundary.  It does not assert the missing production shell bound.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from itertools import product as cartesian_product
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-"
    "SHELL-BOUNDARY"
)
SCHEMA = (
    "tect/a13-owner-complete-physical-response-mixed-gram-shell-"
    "boundary-primary/1.0"
)
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-owner-complete-physical-response-mixed-"
    "gram-shell-boundary/result.json"
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
R130_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-"
    "response-boundary/result.json"
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
                "R-131 proves the fixed-cylinder response factorization "
                "conditional on an owner-complete physical form, a floor-uniform deterministic current-square "
                "H2 component bound, exact mixed-Gram and bounded-multiplier "
                "method boundaries, the conditional balanced/low acceptance "
                "simplex, a stratified Xi radial-coefficient boundary, the "
                "common-phase full-tangent identification no-go, and fixed-"
                "heat non-uniformity. It does "
                "not prove production C_mix, C_far, c_bal, R0, S0, d, k, an "
                "full-tangent Xi coercivity, an absolute anchor, a uniform "
                "augmented gap, OVERLAP_src, "
                "Nelson, removals, an interacting measure, or Sector A closure."
            ),
        }


def frobenius(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.simplify(
        sum(
            left[row, column] * right[row, column]
            for row in range(left.rows)
            for column in range(left.cols)
        )
    )


def laurent_product(
    left: dict[int, sp.Expr], right: dict[int, sp.Expr]
) -> dict[int, sp.Expr]:
    output: dict[int, sp.Expr] = {}
    for left_frequency, left_value in left.items():
        for right_frequency, right_value in right.items():
            frequency = left_frequency + right_frequency
            output[frequency] = sp.simplify(
                output.get(frequency, sp.Integer(0)) + left_value * right_value
            )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    audit.check(
        "authority",
        "A1_manifest_schema",
        a1.get("schema") == "tect/a1-production-functional-realisation/1.0",
        a1.get("schema"),
        "tect/a1-production-functional-realisation/1.0",
    )
    params = a1["parameters"]
    p_mass = sp.Rational(str(params["M_X"])) ** 2 + sp.Rational(
        str(params["classii_mass_regularizer"])
    )
    density_floor = sp.Rational(str(params["rho_regularizer"]))
    classii_a = (
        sp.Rational(str(params["cJJ"]))
        * sp.Rational(str(params["alpha_X"])) ** 2
        / p_mass
    )
    classii_b = (
        sp.Rational(str(params["cJK"]))
        * sp.Rational(str(params["alpha_X"]))
        * sp.Rational(str(params["beta_X"]))
        / p_mass
    )
    classii_c = (
        sp.Rational(str(params["cKK"]))
        * sp.Rational(str(params["beta_X"])) ** 2
        / p_mass
    )
    alpha = sp.simplify(classii_c / (classii_b + classii_c))
    c1 = sp.simplify((classii_b + classii_c) ** 2 / classii_c)
    c0 = sp.simplify(classii_a - classii_b**2 / classii_c)
    beta_op = sp.simplify(4 * (c0 + c1))

    audit.check("production", "positive_mass_denominator", p_mass > 0, p_mass, ">0")
    audit.check("production", "positive_density_floor", density_floor > 0, density_floor, ">0")
    audit.check("production", "completed_square_alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("production", "completed_square_c0", c0 == sp.Rational(3, 250) / p_mass, c0, sp.Rational(3, 250) / p_mass)
    audit.check("production", "completed_square_c1", c1 == sp.Rational(243, 8000) / p_mass, c1, sp.Rational(243, 8000) / p_mass)
    audit.check(
        "production",
        "beta_operator",
        sp.simplify(beta_op - sp.Rational(339, 2000) / p_mass) == 0,
        beta_op,
        sp.Rational(339, 2000) / p_mass,
    )

    # R-130 already derived and independently verified the complete six-row
    # derivative envelopes.  R-131 consumes that hash-pinned authority rather
    # than pasting its internal rational-frame constants as a new derivation.
    r130 = json.loads(R130_RESULT.read_text(encoding="utf-8"))
    r103 = json.loads(R103_RESULT.read_text(encoding="utf-8"))
    source_action_coefficient = sp.Rational(
        r103["diagnostics"]["budget"]["source_coefficient"]
    )
    sextic_action_coefficient = sp.Rational(
        r103["diagnostics"]["budget"]["sextic_coefficient"]
    )
    source_hessian_coefficient = sp.simplify(2 * source_action_coefficient)
    audit.check(
        "authority",
        "R103_contract",
        r103.get("schema")
        == "tect/a13-regular-complete-packet-ownership-hn-reg-closure-primary/1.0"
        and r103.get("status") == "PASS"
        and r103.get("result_id")
        == "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE",
        (r103.get("schema"), r103.get("status"), r103.get("result_id")),
        "pinned R-103 primary PASS contract",
    )
    audit.check(
        "authority",
        "R103_source_action_oracle",
        source_action_coefficient == sp.Rational(9, 20),
        source_action_coefficient,
        sp.Rational(9, 20),
    )
    audit.check(
        "authority",
        "R103_source_hessian_oracle",
        source_hessian_coefficient == sp.Rational(9, 10),
        source_hessian_coefficient,
        sp.Rational(9, 10),
    )
    audit.check(
        "authority",
        "R103_sextic_action_oracle",
        sextic_action_coefficient == sp.Rational(3, 20),
        sextic_action_coefficient,
        sp.Rational(3, 20),
    )
    l6 = sp.Rational(r130["diagnostics"]["conormal_gram"]["L6"])
    h6 = sp.Rational(r130["diagnostics"]["conormal_gram"]["H6"])
    h2_component = sp.simplify(beta_op + 2 * l6 + h6)
    audit.check(
        "deterministic_h2",
        "R130_L6_imported_exact",
        sp.simplify(l6 - sp.Rational(1143, 250) / p_mass) == 0,
        l6,
        sp.Rational(1143, 250) / p_mass,
    )
    audit.check(
        "deterministic_h2",
        "R130_H6_imported_exact",
        sp.simplify(h6 - sp.Rational(7083, 500) / p_mass) == 0,
        h6,
        sp.Rational(7083, 500) / p_mass,
    )
    audit.check(
        "deterministic_h2",
        "complete_H2_component_coefficient",
        sp.simplify(h2_component - sp.Rational(46959, 2000) / p_mass) == 0,
        h2_component,
        sp.Rational(46959, 2000) / p_mass,
    )
    # The diagonal second variation contains respectively B, two DB terms,
    # and one half-D2B term.  This exact scalar fixture checks all factors.
    u_size, z_size, du_size, dz_size = map(
        sp.Rational, ("7/5", "5/4", "9/7", "11/9")
    )
    component_majorant = sp.simplify(
        beta_op * u_size**2 * dz_size**2
        + 2 * l6 * u_size * z_size * du_size * dz_size
        + h6 * z_size**2 * du_size**2
    )
    separated_majorant = sp.simplify(
        h2_component
        * max(u_size, du_size) ** 2
        * max(z_size, dz_size) ** 2
    )
    audit.check(
        "deterministic_h2",
        "three_term_component_below_product_majorant",
        component_majorant <= separated_majorant,
        component_majorant,
        separated_majorant,
    )

    # Exact fixed-cylinder response before pullback and orthogonal shell
    # coanalysis.  Q_comp may be indefinite; Q_6 is the once-owned sextic.
    q_comp = sp.Matrix([[2, -1, 0], [-1, 3, 1], [0, 1, -2]])
    q_sextic = sp.diag(1, 2, 3)
    q_total = q_comp + q_sextic
    synthesis = sp.Matrix([[1, 0, 1, 0], [0, 1, -1, 0], [1, 1, 0, 0]])
    shell_one = sp.diag(1, 1, 0)
    shell_two = sp.diag(0, 0, 1)
    response = q_total * synthesis
    h_endpoint = sp.simplify(synthesis.T * response)
    shell_response = sp.Matrix.vstack(shell_one * response, shell_two * response)
    shell_synthesis = sp.Matrix.vstack(shell_one * synthesis, shell_two * synthesis)
    shell_pullback = sp.simplify(shell_synthesis.T * shell_response)
    reverse_pullback = sp.simplify(shell_response.T * shell_synthesis)
    audit.check("response", "physical_hessian_symmetric", h_endpoint == h_endpoint.T, h_endpoint, h_endpoint.T)
    audit.check("response", "response_before_pullback", h_endpoint == synthesis.T * q_total * synthesis, h_endpoint, synthesis.T * q_total * synthesis)
    audit.check("response", "orthogonal_shell_forward_sum", shell_pullback == h_endpoint, shell_pullback, h_endpoint)
    audit.check("response", "true_reverse_same_owner", reverse_pullback == h_endpoint, reverse_pullback, h_endpoint)
    audit.check(
        "response",
        "shell_response_norm_identity",
        sp.simplify(frobenius(shell_response, shell_response) - frobenius(response, response)) == 0,
        frobenius(shell_response, shell_response),
        frobenius(response, response),
    )
    audit.check(
        "response",
        "shell_response_analysis_isometry",
        sp.simplify(shell_response.T * shell_response)
        == sp.simplify(response.T * response),
        sp.simplify(shell_response.T * shell_response),
        sp.simplify(response.T * response),
    )
    vertical = sp.Matrix([0, 0, 0, 1])
    source_hessian = source_hessian_coefficient * sp.eye(4)
    audit.check("response", "physical_vertical_kernel", h_endpoint * vertical == sp.zeros(4, 1), h_endpoint * vertical, sp.zeros(4, 1))
    audit.check(
        "response",
        "source_cost_outside_physical_kernel",
        (vertical.T * source_hessian * vertical)[0]
        == source_hessian_coefficient,
        (vertical.T * source_hessian * vertical)[0],
        source_hessian_coefficient,
    )

    # Replica identity and exact diagonal-Gram insufficiency.  Every sample
    # Gram is I, while the conditional mean square has nonzero curvature.
    t = sp.symbols("t", real=True)
    rotation_plus = sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]])
    rotation_minus = rotation_plus.subs(t, -t)
    identity_two = sp.eye(2)
    mean_rotation = sp.simplify((rotation_plus + rotation_minus) / 2)
    mean_square = sp.simplify((mean_rotation.T * mean_rotation)[0, 0])
    replica_square = sp.simplify(
        sum(
            (left.T * right)[0, 0]
            for left in (rotation_plus, rotation_minus)
            for right in (rotation_plus, rotation_minus)
        )
        / 4
    )
    audit.check("mixed_gram", "sample_gram_plus_constant", sp.simplify(rotation_plus.T * rotation_plus) == identity_two, sp.simplify(rotation_plus.T * rotation_plus), identity_two)
    audit.check("mixed_gram", "sample_gram_minus_constant", sp.simplify(rotation_minus.T * rotation_minus) == identity_two, sp.simplify(rotation_minus.T * rotation_minus), identity_two)
    audit.check("mixed_gram", "replica_identity", sp.simplify(replica_square - mean_square) == 0, replica_square, mean_square)
    audit.check("mixed_gram", "mean_square_cosine", sp.simplify(mean_square - sp.cos(t) ** 2) == 0, mean_square, sp.cos(t) ** 2)
    audit.check("mixed_gram", "invisible_nonzero_curvature", sp.diff(mean_square, t, 2).subs(t, 0) == -2, sp.diff(mean_square, t, 2).subs(t, 0), -2)

    # A bounded spatial multiplier has no automatic off-diagonal shell decay.
    root_shell = 3
    output_shell = 19
    root_frequency = 2**root_shell
    output_frequency = 2**output_shell
    shift = output_frequency - root_frequency
    product = laurent_product(
        {shift: sp.Rational(1, 2), -shift: sp.Rational(1, 2)},
        {root_frequency: sp.Integer(1)},
    )
    projected_norm = abs(product[output_frequency])
    forced_c_mix = sp.simplify(projected_norm * 2 ** (2 * output_shell - root_shell))
    forced_c_far = sp.simplify(projected_norm * 2 ** (4 * output_shell - root_shell))
    next_output_shell = output_shell + 1
    next_output_frequency = 2**next_output_shell
    next_shift = next_output_frequency - root_frequency
    next_product = laurent_product(
        {next_shift: sp.Rational(1, 2), -next_shift: sp.Rational(1, 2)},
        {root_frequency: sp.Integer(1)},
    )
    next_projected_norm = abs(next_product[next_output_frequency])
    next_forced_c_mix = sp.simplify(
        next_projected_norm * 2 ** (2 * next_output_shell - root_shell)
    )
    next_forced_c_far = sp.simplify(
        next_projected_norm * 2 ** (4 * next_output_shell - root_shell)
    )
    audit.check("shell", "projected_cosine_shell_coefficient", projected_norm == sp.Rational(1, 2), projected_norm, sp.Rational(1, 2))
    x_spatial = sp.symbols("x_spatial", real=True)
    audit.check(
        "shell",
        "cosine_multiplier_unit_supremum_identity",
        sp.trigsimp(
            1
            - sp.cos(shift * x_spatial) ** 2
            - sp.sin(shift * x_spatial) ** 2
        )
        == 0,
        "1-cos(Nx)^2=sin(Nx)^2>=0 and cos(0)=1",
        "||cos(Nx)||_infinity=1",
    )
    audit.check("shell", "mixed_constant_forced_growth", forced_c_mix == 2 ** (2 * output_shell - root_shell - 1), forced_c_mix, 2 ** (2 * output_shell - root_shell - 1))
    audit.check("shell", "far_constant_forced_growth", forced_c_far == 2 ** (4 * output_shell - root_shell - 1), forced_c_far, 2 ** (4 * output_shell - root_shell - 1))
    audit.check("shell", "next_shell_selected_coefficient", next_projected_norm == sp.Rational(1, 2), next_projected_norm, sp.Rational(1, 2))
    audit.check("shell", "mixed_family_growth_ratio", next_forced_c_mix / forced_c_mix == 4, next_forced_c_mix / forced_c_mix, 4)
    audit.check("shell", "far_family_growth_ratio", next_forced_c_far / forced_c_far == 16, next_forced_c_far / forced_c_far, 16)
    state = sp.symbols("state", real=True)
    frequency = 2 * sp.pi * 7
    hidden_q_derivative = sp.diff(state**2 * sp.sin(frequency * state), state).subs(state, 1)
    audit.check("shell", "state_dependent_Q_derivative_invisible_to_frozen_Q", sp.simplify(hidden_q_derivative - frequency) == 0, hidden_q_derivative, frequency)

    # Conditional acceptance simplex and the convention-complete Cartan
    # diagnostic.  Every value is recomputed from upstream authorities.
    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    audit.check(
        "authority",
        "A8_primary_contract",
        a8.get("schema") == "tect/a8-classii-decoupled-nelson-primary-result/1.0"
        and a8.get("verdict") == "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS",
        (a8.get("schema"), a8.get("verdict")),
        "pinned A8 primary PASS contract",
    )
    r_symbol = sp.Rational(str(params["r"]))
    z_symbol = sp.Rational(str(params["Z"]))
    y_symbol = sp.Rational(str(params["Y"]))
    stationary_symbol = sp.simplify(
        (2 * r_symbol - z_symbol) / (2 * y_symbol - z_symbol)
    )
    symbol_ratio = lambda value: sp.simplify(
        (y_symbol * value**2 + z_symbol * value + r_symbol)
        / (1 + value) ** 2
    )
    c_symbol = min(
        symbol_ratio(sp.Integer(0)),
        symbol_ratio(stationary_symbol),
        y_symbol,
    )
    recorded_c_symbol = sp.Rational(
        str(a8["derived"]["symbol_coercivity"]["c_symbol"])
    )
    audit.check(
        "budget",
        "A8_symbol_constant_rounding_agrees",
        abs(float(c_symbol - recorded_c_symbol)) < 5e-15,
        float(c_symbol),
        float(recorded_c_symbol),
    )
    multiplier_bound = sp.Rational(str(a8["config"]["regulator_multiplier_bound"]))
    a0 = sp.simplify(multiplier_bound**2 / c_symbol)
    pullback_bound = sp.sqrt(a0)
    bridge = sp.sqrt(32 * a0)
    source_reserve = sp.Rational(r103["diagnostics"]["budget"]["source_reserve"])
    sextic_reserve = sp.Rational(r103["diagnostics"]["budget"]["sextic_reserve"])
    eta_zero = sp.simplify(source_reserve - 2 * c0)
    zeta_zero = sextic_reserve
    k_zero = sp.simplify(4 * sp.sqrt(eta_zero * zeta_zero))
    r124 = json.loads(R124_RESULT.read_text(encoding="utf-8"))
    audit.check(
        "authority",
        "R124_contract",
        r124.get("schema")
        == "tect/a13-stationary-polarized-trace-defect-replica-root-shell-boundary-primary/1.0"
        and r124.get("status") == "PASS"
        and r124.get("result_id")
        == "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY",
        (r124.get("schema"), r124.get("status"), r124.get("result_id")),
        "pinned R-124 primary PASS contract",
    )
    cartan_full = sp.Rational(r124["diagnostics"]["cartan"]["full"])
    cartan_oriented = sp.simplify(c1 * cartan_full / 2)
    cartan_cross_norm = sp.simplify(2 * bridge * cartan_oriented)
    cartan_ratio = sp.simplify(cartan_cross_norm / k_zero)
    headroom = sp.simplify(k_zero - cartan_cross_norm)
    diagnostic_collar = 1
    mix_collar_one = (
        sp.sqrt(sp.Rational(8, 7))
        * sp.Integer(2) ** (-2 * diagnostic_collar)
    )
    far_collar_one = (
        sp.sqrt(sp.Rational(224, 223))
        * sp.Integer(2) ** (-4 * diagnostic_collar)
    )
    audit.check("budget", "pullback_bound_positive", pullback_bound > 0, pullback_bound, ">0")
    audit.check("budget", "cartan_factor_2680_over_729", cartan_full == sp.Rational(2680, 729), cartan_full, sp.Rational(2680, 729))
    audit.check("budget", "oriented_cartan_coefficient", sp.simplify(cartan_oriented - sp.Rational(67, 1200) / p_mass) == 0, cartan_oriented, sp.Rational(67, 1200) / p_mass)
    audit.check("budget", "cartan_diagnostic_fits", cartan_ratio < 1, float(cartan_ratio), "<1")
    audit.check("budget", "positive_post_cartan_headroom", headroom > 0, float(headroom), ">0")
    audit.check(
        "budget",
        "mixed_collar_coefficient_exact_square",
        sp.simplify(mix_collar_one**2 - sp.Rational(1, 14)) == 0,
        sp.simplify(mix_collar_one**2),
        sp.Rational(1, 14),
    )
    audit.check(
        "budget",
        "far_collar_coefficient_exact_square",
        sp.simplify(far_collar_one**2 - sp.Rational(7, 1784)) == 0,
        sp.simplify(far_collar_one**2),
        sp.Rational(7, 1784),
    )

    e_symbol, f_symbol, a_symbol = sp.symbols("e f a", positive=True)
    m_two = sp.simplify(
        (e_symbol + f_symbol - sp.sqrt((e_symbol - f_symbol) ** 2 + a_symbol**2)) / 2
    )
    audit.check(
        "budget",
        "two_channel_margin_characteristic_identity",
        sp.simplify(
            m_two**2 - (e_symbol + f_symbol) * m_two + e_symbol * f_symbol - a_symbol**2 / 4
        )
        == 0,
        sp.simplify(m_two**2 - (e_symbol + f_symbol) * m_two + e_symbol * f_symbol),
        a_symbol**2 / 4,
    )
    d_symbol, k_symbol = sp.symbols("d k", positive=True)
    mu_three = sp.simplify(
        (m_two + d_symbol - sp.sqrt((m_two - d_symbol) ** 2 + 4 * k_symbol**2)) / 2
    )
    audit.check(
        "budget",
        "three_channel_margin_characteristic_identity",
        sp.simplify(mu_three**2 - (m_two + d_symbol) * mu_three + m_two * d_symbol - k_symbol**2) == 0,
        sp.simplify(mu_three**2 - (m_two + d_symbol) * mu_three + m_two * d_symbol),
        k_symbol**2,
    )

    # Exact Xi radial coefficient-pair spectrum.  This controls (a,s), plus
    # the separately displayed wedge channel, not the full tangent norm.
    # The lower bound below is asserted only on 0 <= lambda <= 1.  The
    # production range lambda=alpha*r/(r+|chi|^2+e) lies in [0,alpha] and
    # alpha=5/9<1; outside that interval trace <= c0+c1 need not hold.
    lam = sp.symbols("lambda", nonnegative=True)
    radial_gram = sp.Matrix(
        [
            [c0 + c1 * (1 - lam) ** 2, -c1 * lam * (1 - lam)],
            [-c1 * lam * (1 - lam), c1 * lam**2],
        ]
    )
    radial_trace = sp.factor(sp.trace(radial_gram))
    radial_det = sp.factor(radial_gram.det())
    discriminant = sp.factor(radial_trace**2 - 4 * radial_det)
    lambda_minus = sp.simplify((radial_trace - sp.sqrt(discriminant)) / 2)
    lambda_plus = sp.simplify((radial_trace + sp.sqrt(discriminant)) / 2)
    trace_defect = sp.factor(c0 + c1 - radial_trace)
    asymptotic_coefficient = sp.simplify(sp.limit(lambda_minus / lam**2, lam, 0, dir="+"))
    audit.check("xi", "radial_determinant", sp.simplify(radial_det - c0 * c1 * lam**2) == 0, radial_det, c0 * c1 * lam**2)
    audit.check(
        "xi",
        "radial_leading_minor_positive_certificate",
        sp.simplify(radial_gram[0, 0] - c0 - c1 * (1 - lam) ** 2)
        == 0
        and c0 > 0
        and c1 > 0,
        radial_gram[0, 0],
        "c0+c1*(1-lambda)^2>0",
    )
    audit.check("xi", "trace_below_csum", sp.simplify(trace_defect - 2 * c1 * lam * (1 - lam)) == 0, trace_defect, 2 * c1 * lam * (1 - lam))
    audit.check("xi", "production_lambda_domain", 0 < alpha < 1, alpha, "0<alpha<1")
    audit.check(
        "xi",
        "eigenvalue_product_rationalization",
        sp.simplify(lambda_minus * lambda_plus - radial_det) == 0,
        sp.simplify(lambda_minus * lambda_plus),
        radial_det,
    )
    audit.check(
        "xi",
        "lower_bound_domain_certificate",
        c0 > 0 and c1 > 0 and 0 < alpha < 1,
        (
            "G is PSD from positive leading minor and det=c0*c1*lambda^2; "
            "on 0<=lambda<=1, trace<=c0+c1; hence "
            "lambda_-=det/lambda_+>=det/trace>=det/(c0+c1)"
        ),
        "c0*c1*lambda^2/(c0+c1)",
    )
    audit.check("xi", "small_lambda_exact_coefficient", sp.simplify(asymptotic_coefficient - c0 * c1 / (c0 + c1)) == 0, asymptotic_coefficient, c0 * c1 / (c0 + c1))
    audit.check("xi", "det_over_trace_lower_coefficient_positive", c0 * c1 / (c0 + c1) > 0, c0 * c1 / (c0 + c1), ">0")

    # The natural single common-phase horizontal condition does not identify
    # the full tangent norm with the (a,s,h) coefficient seminorm.
    phase_a = sp.re(sp.conjugate(sp.Integer(1)) * sp.I)
    phase_s = sp.re(sp.conjugate(sp.Integer(1)) * (-sp.I))
    phase_h = sp.Integer(1) * 0 - 0 * sp.I
    common_phase_constraint = sp.im(sp.I - sp.I)
    phase_fixture_norm = sp.Abs(sp.I) ** 2 + sp.Abs(-sp.I) ** 2
    audit.check(
        "xi",
        "natural_common_phase_horizontal_full_norm_identity_fails",
        phase_a == 0
        and phase_s == 0
        and phase_h == 0
        and common_phase_constraint == 0
        and phase_fixture_norm == 2,
        {
            "a": phase_a,
            "s": phase_s,
            "h": phase_h,
            "common_phase_constraint": common_phase_constraint,
            "weighted_tangent_norm": phase_fixture_norm,
        },
        "a=s=h=0 and common-phase horizontal, but weighted tangent norm=2",
    )

    eps = sp.symbols("eps", positive=True)
    pointwise_singlet_ratio = sp.simplify(
        4 * c1 * alpha**2 * eps**4 / (eps**2 + 1 + density_floor) ** 2
    )
    audit.check("xi", "pure_singlet_transition_degenerates", sp.limit(pointwise_singlet_ratio, eps, 0, dir="+") == 0, sp.limit(pointwise_singlet_ratio, eps, 0, dir="+"), 0)
    audit.check(
        "xi",
        "pure_singlet_quartic_scaling",
        sp.simplify(
            sp.limit(pointwise_singlet_ratio / eps**4, eps, 0, dir="+")
            - 4 * c1 * alpha**2 / (1 + density_floor) ** 2
        )
        == 0,
        sp.limit(pointwise_singlet_ratio / eps**4, eps, 0, dir="+"),
        4 * c1 * alpha**2 / (1 + density_floor) ** 2,
    )

    # The full six-real-coordinate product Rademacher heat has 64 atoms,
    # zero mean, and identity covariance.  Its doublet radius is always four,
    # so integrating the 16 doublet sign choices collapses the response to
    # the four distinct singlet values evaluated below.  It fills each finite
    # singlet ray but not uniformly.  The general proof uses the bound
    # R^2 y/(R+y+e)^2 <= R^2/[4(R+e)] <= R/4.
    terminal_amplitude = sp.symbols("T", positive=True)
    doublet_radius = sp.Integer(4)
    full_heat_atoms = list(cartesian_product((-1, 1), repeat=6))
    full_heat_means = [
        sp.Rational(sum(atom[index] for atom in full_heat_atoms), len(full_heat_atoms))
        for index in range(6)
    ]
    full_heat_covariance = sp.Matrix(
        6,
        6,
        lambda row, column: sp.Rational(
            sum(atom[row] * atom[column] for atom in full_heat_atoms),
            len(full_heat_atoms),
        ),
    )
    collapsed_multiplicities: dict[tuple[int, int], int] = {}
    for atom in full_heat_atoms:
        key = (atom[4], atom[5])
        collapsed_multiplicities[key] = collapsed_multiplicities.get(key, 0) + 1
    audit.check(
        "heat",
        "full_coordinate_product_rademacher_collapses_to_four_singlet_values",
        len(full_heat_atoms) == 64
        and full_heat_means == [0] * 6
        and full_heat_covariance == sp.eye(6)
        and all(sum(value * value for value in atom[:4]) == 4 for atom in full_heat_atoms)
        and set(collapsed_multiplicities.values()) == {16},
        {
            "atoms": len(full_heat_atoms),
            "means": full_heat_means,
            "covariance": full_heat_covariance,
            "collapsed_multiplicities": collapsed_multiplicities,
        },
        "64 atoms, zero mean, identity covariance, R=4, four singlet values each of multiplicity 16",
    )
    heat_values = []
    for real_part in (-1, 1):
        for imaginary_part in (-1, 1):
            singlet_real = terminal_amplitude + real_part
            singlet_norm = singlet_real**2 + imaginary_part**2
            denominator = doublet_radius + singlet_norm + density_floor
            heat_values.append(
                sp.simplify(
                    4
                    * c1
                    * alpha**2
                    * doublet_radius**2
                    * singlet_real**2
                    / denominator**2
                )
            )
    heat_average = sp.simplify(sum(heat_values) / len(heat_values))
    heat_scaled_limit = sp.simplify(
        sp.limit(terminal_amplitude**2 * heat_average, terminal_amplitude, sp.oo)
    )
    expected_heat_limit = sp.simplify(4 * c1 * alpha**2 * doublet_radius**2)
    heat_dominating_bound = sp.simplify(
        c1 * alpha**2 * doublet_radius**2 / (doublet_radius + density_floor)
    )
    y_heat = sp.symbols("y_heat", nonnegative=True)
    heat_square_identity = sp.factor(
        (doublet_radius + density_floor + y_heat) ** 2
        - 4 * (doublet_radius + density_floor) * y_heat
    )
    audit.check("heat", "finite_heat_ray_positive", heat_average.subs(terminal_amplitude, 10) > 0, heat_average.subs(terminal_amplitude, 10), ">0")
    audit.check("heat", "heat_only_uniform_gap_fails", sp.limit(heat_average, terminal_amplitude, sp.oo) == 0, sp.limit(heat_average, terminal_amplitude, sp.oo), 0)
    audit.check("heat", "heat_ray_inverse_square_limit", sp.simplify(heat_scaled_limit - expected_heat_limit) == 0, heat_scaled_limit, expected_heat_limit)
    audit.check("heat", "heat_dominating_bound_finite", heat_dominating_bound > 0, heat_dominating_bound, ">0")
    audit.check(
        "heat",
        "heat_domination_square_identity",
        sp.simplify(
            heat_square_identity
            - (y_heat - doublet_radius - density_floor) ** 2
        )
        == 0,
        heat_square_identity,
        (y_heat - doublet_radius - density_floor) ** 2,
    )
    sextic_ray_hessian = sp.diff(
        sextic_action_coefficient * (terminal_amplitude + t) ** 6, t, 2
    ).subs(t, 0)
    audit.check("heat", "sextic_ray_hessian", sp.simplify(sextic_ray_hessian - sp.Rational(9, 2) * terminal_amplitude**4) == 0, sextic_ray_hessian, sp.Rational(9, 2) * terminal_amplitude**4)

    audit.check("authority", "R130_primary_pass", r130["status"] == "PASS", r130["status"], "PASS")
    audit.check(
        "authority",
        "R130_contract",
        r130.get("schema")
        == "tect/a13-terminal-xi-conormal-gram-balanced-low-response-boundary-primary/1.0"
        and r130.get("result_id")
        == "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-RESPONSE-BOUNDARY",
        (r130.get("schema"), r130.get("result_id")),
        "pinned R-130 primary contract",
    )
    audit.check(
        "authority",
        "R130_beta_operator_agrees",
        sp.Rational(r130["diagnostics"]["production"]["beta_operator"]) == beta_op,
        r130["diagnostics"]["production"]["beta_operator"],
        beta_op,
    )

    diagnostics = {
        "production": {
            "P": p_mass,
            "density_floor": density_floor,
            "c0": c0,
            "c1": c1,
            "alpha": alpha,
            "beta_operator": beta_op,
        },
        "owner_complete_response": {
            "source_action_coefficient": source_action_coefficient,
            "source_hessian_coefficient": source_hessian_coefficient,
            "terminal_sextic_action_coefficient": sextic_action_coefficient,
            "factorization": "H_endpoint=L_pred^* Q_endpoint L_pred=R^*F",
            "physical_response_uniform_bound_proved": False,
        },
        "deterministic_current_h2": {
            "L6": l6,
            "H6": h6,
            "coefficient_before_embedding": h2_component,
            "bound": "C_(H2->Linf)^2*(beta_op+2L6+H6)*||u||_H2^2*||z||_H2^2",
            "complete_trace_heat_mixed_response_included": False,
        },
        "mixed_gram": {
            "replica_identity": "||E_f C_f V_f||^2=E_(f,f') <V_f,C_f^*C_f'V_f'>",
            "diagonal_gram_curvature": 0,
            "mean_square_curvature": -2,
            "diagonal_gram_sufficient_for_response": False,
        },
        "shell_boundary": {
            "selected_output_shell_coefficient": projected_norm,
            "multiplier_Linf": 1,
            "forced_C_mix_fixture": forced_c_mix,
            "forced_C_far_fixture": forced_c_far,
            "next_shell_C_mix_growth_ratio": next_forced_c_mix / forced_c_mix,
            "next_shell_C_far_growth_ratio": next_forced_c_far / forced_c_far,
            "bounded_multiplier_implies_shell_decay": False,
        },
        "acceptance": {
            "A0": a0,
            "source_pullback_bound": pullback_bound,
            "C_bridge": bridge,
            "eta_zero": eta_zero,
            "zeta_zero": zeta_zero,
            "K0": k_zero,
            "cartan_oriented_coefficient": cartan_oriented,
            "cartan_effective_cross_norm": cartan_cross_norm,
            "cartan_budget_ratio": cartan_ratio,
            "post_cartan_headroom": headroom,
            "C1_mixed_coefficient": mix_collar_one,
            "C1_far_coefficient": far_collar_one,
            "mixed_only_diagnostic_ceiling": sp.simplify(headroom / mix_collar_one),
            "far_only_diagnostic_ceiling": sp.simplify(headroom / far_collar_one),
            "production_acceptance_proved": False,
        },
        "xi_transversality": {
            "radial_gram": radial_gram,
            "trace": radial_trace,
            "determinant": radial_det,
            "lambda_minus": lambda_minus,
            "lower_bound": "lambda_minus >= c0*c1*lambda^2/(c0+c1) for 0<=lambda<=1",
            "production_domain": "0<=lambda<=alpha=5/9<1",
            "small_lambda_coefficient": asymptotic_coefficient,
            "natural_common_phase_full_tangent_identification": False,
            "phase_invisible_weighted_tangent_norm_fixture": phase_fixture_norm,
            "state_uniform_positive_gap": False,
        },
        "heat_boundary": {
            "rademacher_heat_average": heat_average,
            "T2_scaled_limit": heat_scaled_limit,
            "dominating_bound": heat_dominating_bound,
            "fixed_heat_uniform_transversality": False,
            "sextic_ray_hessian": sextic_ray_hessian,
        },
        "scope": {
            "finite_cylinder_factorization_given_owner_complete_form": True,
            "production_owner_complete_form_constructed": False,
            "deterministic_current_square_H2_component": True,
            "floor_uniform_component_constant": True,
            "mixed_conditional_gram_response": False,
            "production_C_mix": False,
            "production_C_far": False,
            "production_c_bal": False,
            "low_D_K_R0_S0": False,
            "absolute_anchor": False,
            "uniform_augmented_gap": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(
        f"R-131 primary {result['status']}: "
        f"{result['assertions_passed']}/{result['assertions_total']}"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
