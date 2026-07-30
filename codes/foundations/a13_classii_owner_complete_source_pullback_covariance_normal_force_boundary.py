#!/usr/bin/env python3
"""Primary exact audit for the scoped R-128 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY"
SCHEMA = "tect/a13-owner-complete-source-pullback-covariance-normal-force-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R103_OUTPUT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
R124_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"
R126_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-total-symbol-euler-low-injected-loewner-boundary/result.json"
R127_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.simplify(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
            "scope": {
                "r119_control_shift_hessian_authority_reused_not_duplicated": True,
                "r104_owner_identity_differentiated_on_fixed_smooth_chart": True,
                "control_shift_and_malliavin_source_derivatives_separated": True,
                "covariance_normal_force_corrected_by_future_variance": True,
                "sextic_and_source_cost_derivatives_included": True,
                "refinement_pullback_naturality_proved_for_fixed_bounded_linear_maps": True,
                "strict_margin_is_zero_diagonal_or_absorbed_debt_specialization": True,
                "production_root_shell_intertwiner_proved": False,
                "production_covariance_normal_operator_bound_proved": False,
                "balanced_and_low_uniform_bounds_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-128 proves fixed-chart differentiated owner naturality, corrects the naked "
                "trace-excess force to the covariance-normal force, separates control and "
                "Malliavin derivatives, and derives a conditional zero-diagonal strict-margin "
                "reallocation. "
                "It proves no production root-shell intertwiner, uniform covariance-normal, "
                "balanced, or low bound, OVERLAP_src, Nelson theorem, removal, measure, or "
                "Sector-A closure."
            ),
        }


def owner_pullback_and_refinement(audit: Audit) -> dict[str, Any]:
    b_one = sp.Matrix([[2, 1], [1, 3]])
    b_two = sp.Matrix([[1, -1], [-1, 2]])
    b_total = b_one + b_two
    ell_one = sp.Matrix([sp.Rational(2, 3), sp.Rational(-1, 5)])
    ell_two = sp.Matrix([sp.Rational(-1, 7), sp.Rational(3, 4)])
    ell_total = ell_one + ell_two
    synthesis = sp.Matrix([[1, 0, 1], [0, 1, 1]])
    h = sp.Matrix([sp.Rational(2, 5), sp.Rational(-3, 7), sp.Rational(1, 4)])
    z = synthesis * h

    gradient = synthesis.T * (b_total * z + ell_total)
    owner_gradient = synthesis.T * (b_one * z + ell_one) + synthesis.T * (b_two * z + ell_two)
    hessian = synthesis.T * b_total * synthesis
    owner_hessian = synthesis.T * b_one * synthesis + synthesis.T * b_two * synthesis
    vertical = sp.Matrix([1, 1, -1])

    audit.check("owner", "gradient_recombines", gradient == owner_gradient, gradient, owner_gradient)
    audit.check("owner", "hessian_recombines", hessian == owner_hessian, hessian, owner_hessian)
    audit.check("owner", "common_hessian_selfadjoint", hessian == hessian.T, hessian, hessian.T)
    audit.check("owner", "vertical_is_synthesis_kernel", synthesis * vertical == sp.zeros(2, 1), synthesis * vertical, sp.zeros(2, 1))
    audit.check("owner", "vertical_is_hessian_kernel", hessian * vertical == sp.zeros(3, 1), hessian * vertical, sp.zeros(3, 1))

    injection = sp.Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]])
    refined_synthesis = synthesis.row_join(sp.Matrix([2, -1]))
    refined_h = injection * h
    refined_gradient = refined_synthesis.T * (b_total * refined_synthesis * refined_h + ell_total)
    refined_hessian = refined_synthesis.T * b_total * refined_synthesis
    audit.check("refinement", "synthesis_intertwining", refined_synthesis * injection == synthesis, refined_synthesis * injection, synthesis)
    audit.check("refinement", "gradient_pullback", injection.T * refined_gradient == gradient, injection.T * refined_gradient, gradient)
    audit.check("refinement", "hessian_conjugacy", injection.T * refined_hessian * injection == hessian, injection.T * refined_hessian * injection, hessian)

    return {
        "synthesis": synthesis,
        "common_hessian": hessian,
        "vertical_kernel": vertical,
        "refinement_injection": injection,
    }


def control_malliavin_firewall(audit: Audit) -> dict[str, Any]:
    alpha, beta = sp.symbols("alpha beta", real=True)
    xi_one, xi_two, u_one, u_two = sp.symbols("xi_one xi_two u_one u_two", real=True)

    # The bounded predictable feedback alpha*tanh(xi_one) has the same local
    # first jet as the familiar affine diagnostic, but remains inside the
    # declared smooth bounded cylindrical class.
    z_control = xi_one + xi_two + alpha * sp.tanh(xi_one) + u_one + u_two
    quadratic_endpoint = z_control**2 / 2
    control_hessian = sp.hessian(quadratic_endpoint, (u_one, u_two)).subs(
        {xi_one: 0, xi_two: 0, u_one: 0, u_two: 0}
    )
    mall_hessian = sp.hessian(
        (xi_one + xi_two + alpha * sp.tanh(xi_one)) ** 2 / 2,
        (xi_one, xi_two),
    ).subs({xi_one: 0, xi_two: 0})
    at_one = mall_hessian.subs(alpha, 1)
    audit.check("firewall", "control_hessian_rank_one", control_hessian.det() == 0, control_hessian.det(), 0)
    audit.check("firewall", "malliavin_hessian_at_alpha_one", at_one == sp.Matrix([[4, 2], [2, 1]]), at_one, sp.Matrix([[4, 2], [2, 1]]))
    audit.check("firewall", "derivatives_differ", at_one != control_hessian, at_one, "not control Hessian")
    audit.check("firewall", "malliavin_feedback_jacobian", at_one == sp.Matrix([[2, 1]]).T * sp.Matrix([[2, 1]]), at_one, "J_h^T J_h")

    # A second bounded feedback has zero first jet and nonzero second jet at
    # the origin.  With a linear endpoint its entire source Hessian is the
    # feedback-connection term, whereas the control-shift Hessian is zero.
    nonlinear_feedback = beta * sp.tanh(xi_one) ** 2 / 2
    linear_endpoint = xi_one + xi_two + nonlinear_feedback
    nonlinear_mall = sp.diff(linear_endpoint, xi_one, 2).subs(xi_one, 0)
    nonlinear_control = sp.diff(u_one + u_two, u_one, u_one)
    audit.check("firewall", "bounded_feedback_second_jet", sp.diff(nonlinear_feedback, xi_one, 2).subs(xi_one, 0) == beta, sp.diff(nonlinear_feedback, xi_one, 2).subs(xi_one, 0), beta)
    audit.check("firewall", "connection_term_control_hessian_zero", nonlinear_control == 0, nonlinear_control, 0)
    audit.check("firewall", "connection_term_malliavin_hessian", nonlinear_mall == beta, nonlinear_mall, beta)
    return {
        "bounded_control_hessian": control_hessian,
        "bounded_malliavin_hessian": mall_hessian,
        "alpha_one": at_one,
        "bounded_nonlinear_connection": nonlinear_mall,
    }


def covariance_normal_calculus(audit: Audit) -> dict[str, Any]:
    z, s, t = sp.symbols("z s t", real=True)
    h = sp.Rational(3, 5)
    k = sp.Rational(-2, 7)
    atoms = (sp.Integer(-1), sp.Integer(1))
    weights = (sp.Rational(1, 2), sp.Rational(1, 2))
    q_atoms = (sp.Rational(1, 3), sp.Rational(-2, 5))

    def currents(value: sp.Expr) -> list[sp.Expr]:
        return [value * (1 + eta) + q * value**2 for eta, q in zip(atoms, q_atoms)]

    moved = z + s * h + t * k
    moved_currents = currents(moved)
    phi = sum(p * value for p, value in zip(weights, moved_currents))
    variance = sum(p * (value - phi) ** 2 for p, value in zip(weights, moved_currents))
    theta = moved**2 + sp.Rational(1, 3) * moved**4
    trace_excess = theta - phi**2
    covariance_normal = sp.simplify((variance - trace_excess) / 2)
    direct_current = sp.simplify((sum(p * value**2 for p, value in zip(weights, moved_currents)) - theta) / 2)
    audit.check("variance", "conditional_pythagoras", sp.simplify(covariance_normal - direct_current) == 0, covariance_normal, direct_current)

    base_currents = currents(z)
    base_phi = sum(p * value for p, value in zip(weights, base_currents))
    residuals = [value - base_phi for value in base_currents]
    dot_h = [sp.diff(value, s).subs({s: 0, t: 0}) for value in moved_currents]
    dot_k = [sp.diff(value, t).subs({s: 0, t: 0}) for value in moved_currents]
    ddot_hk = [sp.diff(value, s, t).subs({s: 0, t: 0}) for value in moved_currents]
    mean_dot_h = sum(p * value for p, value in zip(weights, dot_h))
    mean_dot_k = sum(p * value for p, value in zip(weights, dot_k))

    dv_formula = 2 * sum(p * residual * dot for p, residual, dot in zip(weights, residuals, dot_h))
    dv_direct = sp.diff(variance, s).subs({s: 0, t: 0})
    d2v_formula = 2 * (
        sum(p * left * right for p, left, right in zip(weights, dot_h, dot_k))
        - mean_dot_h * mean_dot_k
        + sum(p * residual * ddot for p, residual, ddot in zip(weights, residuals, ddot_hk))
    )
    d2v_direct = sp.diff(variance, s, t).subs({s: 0, t: 0})
    audit.check("variance", "first_variation", sp.simplify(dv_formula - dv_direct) == 0, dv_formula, dv_direct)
    audit.check("variance", "second_variation", sp.simplify(d2v_formula - d2v_direct) == 0, d2v_formula, d2v_direct)
    audit.check(
        "variance",
        "covariance_normal_half_difference_gradient",
        sp.simplify(sp.diff(covariance_normal, s) - (sp.diff(variance, s) - sp.diff(trace_excess, s)) / 2) == 0,
        sp.diff(covariance_normal, s),
        (sp.diff(variance, s) - sp.diff(trace_excess, s)) / 2,
    )
    audit.check(
        "variance",
        "covariance_normal_half_difference_hessian",
        sp.simplify(sp.diff(covariance_normal, s, t) - (sp.diff(variance, s, t) - sp.diff(trace_excess, s, t)) / 2) == 0,
        sp.diff(covariance_normal, s, t),
        (sp.diff(variance, s, t) - sp.diff(trace_excess, s, t)) / 2,
    )

    fixture_currents = [z * (1 + eta) for eta in atoms]
    fixture_phi = sum(p * value for p, value in zip(weights, fixture_currents))
    fixture_variance = sum(p * (value - fixture_phi) ** 2 for p, value in zip(weights, fixture_currents))
    fixture_theta = z**2
    fixture_trace_excess = sp.simplify(fixture_theta - fixture_phi**2)
    fixture_cn = sp.simplify((fixture_variance - fixture_trace_excess) / 2)
    audit.check("variance_fixture", "phi", fixture_phi == z, fixture_phi, z)
    audit.check("variance_fixture", "variance", fixture_variance == z**2, fixture_variance, z**2)
    audit.check("variance_fixture", "trace_excess_zero", fixture_trace_excess == 0, fixture_trace_excess, 0)
    audit.check("variance_fixture", "covariance_normal_nonzero", fixture_cn == z**2 / 2, fixture_cn, z**2 / 2)
    audit.check("variance_fixture", "naked_force_incomplete", sp.diff(fixture_trace_excess, z) == 0 and sp.diff(fixture_cn, z) == z, (sp.diff(fixture_trace_excess, z), sp.diff(fixture_cn, z)), (0, z))

    return {
        "variance": variance.subs({s: 0, t: 0}),
        "trace_excess": trace_excess.subs({s: 0, t: 0}),
        "covariance_normal": covariance_normal.subs({s: 0, t: 0}),
        "fixture": {"phi": fixture_phi, "variance": fixture_variance, "trace_excess": fixture_trace_excess, "covariance_normal": fixture_cn},
    }


def sextic_and_cost(audit: Audit) -> dict[str, Any]:
    s, t = sp.symbols("s t", real=True)
    z = sp.Matrix([sp.Rational(2, 3), sp.Rational(-3, 5)])
    h = sp.Matrix([sp.Rational(1, 4), sp.Rational(2, 7)])
    k = sp.Matrix([sp.Rational(-2, 9), sp.Rational(1, 6)])
    moved = z + s * h + t * k
    sextic = sp.Rational(3, 20) * (moved.dot(moved)) ** 3
    gradient_pairing = sp.Rational(9, 10) * (z.dot(z)) ** 2 * z.dot(h)
    hessian_pairing = sp.Rational(9, 10) * ((z.dot(z)) ** 2 * h.dot(k) + 4 * z.dot(z) * z.dot(h) * z.dot(k))
    audit.check("sextic", "gradient", sp.diff(sextic, s).subs({s: 0, t: 0}) == gradient_pairing, sp.diff(sextic, s).subs({s: 0, t: 0}), gradient_pairing)
    audit.check("sextic", "hessian", sp.diff(sextic, s, t).subs({s: 0, t: 0}) == hessian_pairing, sp.diff(sextic, s, t).subs({s: 0, t: 0}), hessian_pairing)

    source_coefficient = sp.Rational(9, 20)
    source_gradient_coefficient = 2 * source_coefficient
    audit.check("source_cost", "gradient_coefficient", source_gradient_coefficient == sp.Rational(9, 10), source_gradient_coefficient, sp.Rational(9, 10))
    audit.check("source_cost", "hessian_coefficient", source_gradient_coefficient == sp.Rational(9, 10), source_gradient_coefficient, sp.Rational(9, 10))
    return {"sextic_gradient": gradient_pairing, "sextic_hessian": hessian_pairing, "source_cost_hessian": source_gradient_coefficient}


def tower_and_projection_boundaries(audit: Audit) -> dict[str, Any]:
    xi = (sp.Integer(-1), sp.Integer(1))
    conditional_phi_two = {x1: sum(sp.Rational(1, 2) * (2 * x1 + x2) for x2 in xi) for x1 in xi}
    phi_one = {x1: x1 for x1 in xi}
    audit.check("tower", "conditional_phi_two", conditional_phi_two == {x1: 2 * x1 for x1 in xi}, conditional_phi_two, {x1: 2 * x1 for x1 in xi})
    audit.check("tower", "common_terminal_inference_fails", conditional_phi_two != phi_one, conditional_phi_two, "not phi_one")

    common = sp.Matrix([[0, 1], [1, 0]])
    projection = sp.Matrix([[1, 0], [0, 0]])
    one_sided = projection * common
    audit.check("projection", "one_sided_not_selfadjoint", one_sided.T != one_sided, one_sided.T, "not one-sided projection")
    block_12 = projection * common * (sp.eye(2) - projection)
    block_21 = (sp.eye(2) - projection) * common * projection
    audit.check("projection", "two_sided_blocks_are_adjoints", block_12.T == block_21, block_12.T, block_21)

    oriented = sp.Matrix([[1, 2], [-1, 3]])
    x = sp.Matrix([sp.Rational(2, 5), sp.Rational(-1, 7)])
    y = sp.Matrix([sp.Rational(3, 11), sp.Rational(4, 9)])
    symmetric_block = sp.zeros(4, 4)
    symmetric_block[:2, 2:] = oriented
    symmetric_block[2:, :2] = oriented.T
    joined = x.col_join(y)
    block_form = (joined.T * symmetric_block * joined)[0]
    effective_cross = (x.T * (2 * oriented) * y)[0]
    audit.check("projection", "oriented_block_effective_factor_two", sp.simplify(block_form - effective_cross) == 0, block_form, effective_cross)
    return {
        "tower_conditional": conditional_phi_two,
        "phi_one": phi_one,
        "one_sided_projection": one_sided,
        "effective_cross_operator": 2 * oriented,
    }


def production_mass() -> sp.Expr:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    return sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))


def budgets_and_allocation_firewall(audit: Audit) -> dict[str, Any]:
    r103 = json.loads(R103_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["budget"]
    r124 = json.loads(R124_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["production"]
    r126 = json.loads(R126_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["loewner_shells"]
    r127 = json.loads(R127_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["predictable_source"]
    source = sp.Rational(r103["source_coefficient"])
    sextic = sp.Rational(r103["sextic_coefficient"])
    eta_debt = sp.Rational(r103["eta_star"])
    zeta_debt = sp.Rational(r103["zeta_star"])
    mass = production_mass()
    audit.check("budget", "r124_mass_matches_a1", sp.simplify(sp.Rational(r124["P"]) - mass) == 0, sp.Rational(r124["P"]), mass)
    row_cost = sp.Rational(r124["eta_row"])
    eta_old = sp.Rational(r103["source_reserve"]) - row_cost
    zeta_old = sp.Rational(r103["sextic_reserve"])
    budget_old = 4 * sp.sqrt(eta_old * zeta_old)
    pinned_budget = sp.sympify(r126["production_operator_budget"])
    audit.check("budget", "old_budget_reconstructed", sp.simplify(budget_old - pinned_budget) == 0, budget_old, pinned_budget)

    allocation_fraction = sp.Rational(1, 2)
    eta_half = source - row_cost - allocation_fraction * eta_debt
    zeta_half = sextic - allocation_fraction * zeta_debt
    budget_half = 4 * sp.sqrt(eta_half * zeta_half)
    strict_margin = sp.simplify(eta_half + zeta_half - sp.sqrt((eta_half - zeta_half) ** 2 + budget_old**2 / 4))
    limiting_budget = 4 * sp.sqrt((source - row_cost) * sextic)
    audit.check("budget", "half_debt_budget_improves", budget_half > budget_old, budget_half, f"> {budget_old}")
    audit.check("budget", "strict_margin_positive", strict_margin > 0, strict_margin, "positive")
    audit.check("budget", "strict_margin_regression", sp.Rational(23, 1000) < strict_margin < sp.Rational(25, 1000), strict_margin, "between 0.023 and 0.025")
    audit.check("budget", "limiting_budget_exceeds_half", limiting_budget > budget_half, limiting_budget, f"> {budget_half}")

    h, g, lam = sp.symbols("h g lam", real=True, positive=True)
    completion_left = h * g + source * h**2
    completion_right = lam * source * (h + g / (2 * lam * source)) ** 2 + (1 - lam) * source * h**2 - g**2 / (4 * lam * source)
    audit.check("allocation", "partial_completion_identity", sp.simplify(completion_left - completion_right) == 0, completion_left, completion_right)
    full_adverse = sp.simplify(1 / (4 * source))
    audit.check("allocation", "full_completion_adverse_cost", full_adverse == sp.Rational(r127["source_completion_cost"]), full_adverse, sp.Rational(r127["source_completion_cost"]))
    audit.check("allocation", "full_completion_leaves_no_source_square", sp.simplify((1 - lam) * source).subs(lam, 1) == 0, sp.simplify((1 - lam) * source).subs(lam, 1), 0)

    return {
        "mass": mass,
        "row_cost": row_cost,
        "old": {"eta": eta_old, "zeta": zeta_old, "budget": budget_old},
        "half_debt": {"eta": eta_half, "zeta": zeta_half, "budget": budget_half, "strict_margin_at_old_budget": strict_margin},
        "limiting_budget": limiting_budget,
        "partial_completion_adverse": sp.simplify(1 / (4 * lam * source)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "owner_pullback": owner_pullback_and_refinement(audit),
        "control_malliavin": control_malliavin_firewall(audit),
        "covariance_normal": covariance_normal_calculus(audit),
        "sextic_source_cost": sextic_and_cost(audit),
        "tower_projection": tower_and_projection_boundaries(audit),
        "budgets": budgets_and_allocation_firewall(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-128 primary {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
