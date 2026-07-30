#!/usr/bin/env python3
"""Primary exact audit for the scoped R-129 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY"
SCHEMA = "tect/a13-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary/result.json"
R103_OUTPUT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
R128_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"


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
                "absolute_conditional_covariance_normal_dominates_trace_packet": True,
                "r123_action_lower_bound_from_covariance_normal_dominance": False,
                "endpoint_difference_bypass_proved": False,
                "direct_covariance_normal_mean_cancellation_proved": True,
                "separate_variance_trace_hessian_norms_not_logically_required_if_direct_signed_bound_is_proved": True,
                "shell_coanalysis_reverse_proved_conditionally": True,
                "temporal_increment_shell_commutation_required": False,
                "owner_complete_physical_response_map_required": True,
                "ambient_physical_hessian_realization_required": False,
                "shifted_douglas_gap_criterion_proved": True,
                "production_forward_decay_proved": False,
                "balanced_and_low_uniform_bounds_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-129 proves the absolute-endpoint identity E_CN=P_comp+V/2, but that "
                "dominance does not lower-bound the R-123 action, whose owner is P_comp. "
                "It also proves a conditional "
                "shell-analysis/coanalysis legal reverse for an owner-complete response map, "
                "direct covariance-normal derivative "
                "cancellation, and exact shifted-Douglas acceptance criteria. It proves no "
                "production forward block constants, balanced or low estimate, common-terminal "
                "anchor, OVERLAP_src, Nelson theorem, removal, measure, or Sector-A closure."
            ),
        }


def endpoint_trace_excess(audit: Audit) -> dict[str, Any]:
    # Test-oracle inputs for a two-atom conditional current.
    z = sp.symbols("z", real=True)
    atoms = (sp.Integer(-1), sp.Integer(2))
    weights = (sp.Rational(2, 3), sp.Rational(1, 3))
    currents = [z * (1 + atom) for atom in atoms]
    phi = sum(weight * current for weight, current in zip(weights, currents))
    variance = sp.simplify(
        sum(weight * (current - phi) ** 2 for weight, current in zip(weights, currents))
    )
    theta = sp.Rational(5, 4) * z**2
    trace_excess = sp.simplify(theta - phi**2)
    covariance_normal = sp.simplify((variance - trace_excess) / 2)
    raw_current = sp.simplify(
        (sum(weight * current**2 for weight, current in zip(weights, currents)) - theta) / 2
    )
    packet = sp.simplify(-trace_excess / 2)
    audit.check("endpoint", "conditional_pythagoras", covariance_normal == raw_current, covariance_normal, raw_current)
    audit.check("endpoint", "positive_variance_remainder", sp.simplify(covariance_normal - packet - variance / 2) == 0, covariance_normal - packet, variance / 2)
    audit.check("endpoint", "covariance_normal_dominates_trace_packet", sp.simplify(covariance_normal - packet) == variance / 2, covariance_normal - packet, "nonnegative variance/2")

    # R-125 constant-translation direction fixture: the actual R-123 owner is
    # the lower packet, so an E_CN lower bound cannot be transferred to it.
    s_owner = sp.symbols("s_owner", positive=True)
    owner_variance = 4 * s_owner
    owner_trace = 4 * s_owner
    owner_packet = -owner_trace / 2
    owner_covariance_normal = (owner_variance - owner_trace) / 2
    audit.check("endpoint_scope", "r123_owner_is_strictly_lower", owner_packet < owner_covariance_normal, owner_packet, f"< {owner_covariance_normal}")
    audit.check("endpoint_scope", "r123_transfer_direction", owner_covariance_normal == 0 and owner_packet == -2 * s_owner, [owner_covariance_normal, owner_packet], [0, -2 * s_owner])

    # Endpoint-difference test oracle: J_0=eta, J_h=0, both means and traces zero.
    variance_zero = sp.Integer(1)
    variance_moved = sp.Integer(0)
    trace_zero = sp.Integer(0)
    trace_moved = sp.Integer(0)
    delta_cn = sp.simplify((variance_moved - trace_moved - variance_zero + trace_zero) / 2)
    delta_packet = sp.simplify((-trace_moved + trace_zero) / 2)
    audit.check("endpoint_scope", "difference_counterexample", delta_cn < delta_packet, delta_cn, f"< {delta_packet}")
    audit.check("endpoint_scope", "difference_counterexample_exact", delta_cn == -sp.Rational(1, 2), delta_cn, -sp.Rational(1, 2))

    r103 = json.loads(R103_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["budget"]
    source = sp.Rational(r103["source_coefficient"])
    sextic = sp.Rational(r103["sextic_coefficient"])
    eta = source / 2
    zeta = sextic / 2
    audit.check("endpoint_budget", "source_allocation_strict", eta < source, eta, f"< {source}")
    audit.check("endpoint_budget", "sextic_allocation_strict", zeta < sextic, zeta, f"< {sextic}")
    return {
        "phi": phi,
        "variance": variance,
        "trace_excess": trace_excess,
        "covariance_normal": covariance_normal,
        "trace_packet": packet,
        "difference_fixture": {"delta_covariance_normal": delta_cn, "delta_trace_packet": delta_packet},
        "r123_owner_direction_fixture": {"variance": owner_variance, "trace_excess": owner_trace, "covariance_normal": owner_covariance_normal, "trace_packet": owner_packet},
        "acceptance_test_allocation_only": {"source": source, "sextic": sextic, "test_eta": eta, "test_zeta": zeta},
    }


def direct_covariance_normal_hessian(audit: Audit) -> dict[str, Any]:
    z, s, t = sp.symbols("z s t", real=True)
    h, k = sp.symbols("h k", real=True)
    atoms = (sp.Integer(-1), sp.Integer(1))
    weights = (sp.Rational(1, 2), sp.Rational(1, 2))
    quadratic = (sp.Rational(1, 3), sp.Rational(-2, 5))
    moved = z + s * h + t * k
    currents = [moved * (1 + atom) + q * moved**2 for atom, q in zip(atoms, quadratic)]
    mean = sum(weight * current for weight, current in zip(weights, currents))
    variance = sum(weight * (current - mean) ** 2 for weight, current in zip(weights, currents))
    theta = moved**2 + moved**4 / 3
    trace_excess = theta - mean**2
    covariance_normal = sp.simplify((variance - trace_excess) / 2)
    direct = sp.simplify(
        (sum(weight * current**2 for weight, current in zip(weights, currents)) - theta) / 2
    )
    direct_hessian = sp.diff(direct, s, t).subs({s: 0, t: 0})
    dot_h = [sp.diff(current, s).subs({s: 0, t: 0}) for current in currents]
    dot_k = [sp.diff(current, t).subs({s: 0, t: 0}) for current in currents]
    ddot = [sp.diff(current, s, t).subs({s: 0, t: 0}) for current in currents]
    base = [current.subs({s: 0, t: 0}) for current in currents]
    formula = sp.simplify(
        sum(weight * (left * right + value * second) for weight, left, right, value, second in zip(weights, dot_h, dot_k, base, ddot))
        - sp.diff(theta, s, t).subs({s: 0, t: 0}) / 2
    )
    audit.check("direct_hessian", "raw_current_identity", sp.simplify(covariance_normal - direct) == 0, covariance_normal, direct)
    audit.check("direct_hessian", "conditional_mean_derivatives_cancel", sp.simplify(direct_hessian - formula) == 0, direct_hessian, formula)

    n = sp.symbols("n", positive=True, integer=True)
    variance_fixture = (n + 1) * z**2
    trace_fixture = n * z**2
    cn_fixture = sp.simplify((variance_fixture - trace_fixture) / 2)
    audit.check("separate_norm", "variance_hessian_diverges", sp.simplify(sp.diff(variance_fixture, z, 2) - (2 * n + 2)) == 0, sp.diff(variance_fixture, z, 2), 2 * n + 2)
    audit.check("separate_norm", "trace_hessian_diverges", sp.simplify(sp.diff(trace_fixture, z, 2) - 2 * n) == 0, sp.diff(trace_fixture, z, 2), 2 * n)
    audit.check("separate_norm", "signed_hessian_uniform", sp.diff(cn_fixture, z, 2) == 1, sp.diff(cn_fixture, z, 2), 1)
    return {
        "direct_hessian": direct_hessian,
        "signed_formula": formula,
        "separate_norm_fixture": {
            "variance_hessian": sp.diff(variance_fixture, z, 2),
            "trace_hessian": sp.diff(trace_fixture, z, 2),
            "covariance_normal_hessian": sp.diff(cn_fixture, z, 2),
        },
    }


def analytic_shortcut_boundaries(audit: Audit) -> dict[str, Any]:
    n = sp.symbols("n", positive=True, integer=True)
    z = sp.symbols("z", real=True)
    gaussian_coordinate = sp.symbols("gaussian_coordinate", real=True)
    gaussian_current = sp.cos(n * z) * gaussian_coordinate
    poincare_variance = sp.expand(gaussian_current**2).subs(gaussian_coordinate**2, 1)
    poincare_energy = sp.diff(gaussian_current, gaussian_coordinate) ** 2
    parameter_hessian = sp.diff(poincare_variance, z, 2).subs(z, 0)
    audit.check("poincare", "poincare_equality_fixture", sp.simplify(poincare_variance - poincare_energy) == 0, poincare_variance, poincare_energy)
    audit.check("poincare", "parameter_hessian_unbounded", parameter_hessian == -2 * n**2, parameter_hessian, -2 * n**2)

    epsilon = sp.symbols("epsilon", positive=True)
    entropy_upper = epsilon**2 / 2
    fisher_lower = epsilon**2 * n**2 * (1 + sp.exp(-2 * n**2)) / (2 * (1 + epsilon))
    ratio = sp.simplify(fisher_lower / entropy_upper)
    audit.check("entropy_score", "entropy_uniform_upper", entropy_upper == epsilon**2 / 2, entropy_upper, epsilon**2 / 2)
    audit.check("entropy_score", "fisher_entropy_ratio_diverges", sp.limit(ratio, n, sp.oo) == sp.oo, sp.limit(ratio, n, sp.oo), sp.oo)

    u, v = sp.symbols("u v", positive=True)
    second_score_norm_sq = u**2 * v**2 + (u * v) ** 2
    audit.check("gaussian_score", "parallel_score_constant", sp.sqrt(second_score_norm_sq) == sp.sqrt(2) * u * v, sp.sqrt(second_score_norm_sq), sp.sqrt(2) * u * v)
    return {
        "poincare_variance": poincare_variance,
        "poincare_derivative_energy": poincare_energy,
        "parameter_hessian_at_zero": parameter_hessian,
        "entropy_upper": entropy_upper,
        "fisher_lower": fisher_lower,
        "fisher_entropy_ratio": ratio,
        "parallel_second_score_norm": sp.sqrt(second_score_norm_sq),
    }


def temporal_increment_and_shell_coanalysis(audit: Audit) -> dict[str, Any]:
    half = sp.Rational(1, 2)
    shell = sp.diag(1, 0)
    plus = half * sp.Matrix([[1, 1], [1, 1]])
    minus = half * sp.Matrix([[1, -1], [-1, 1]])
    audit.check("temporal_increment", "increments_are_projections", plus**2 == plus and minus**2 == minus, [plus**2, minus**2], [plus, minus])
    audit.check("temporal_increment", "total_covariance_identity", plus + minus == sp.eye(2), plus + minus, sp.eye(2))
    audit.check("temporal_increment", "total_commutes_with_shell", (plus + minus) * shell == shell * (plus + minus), (plus + minus) * shell, shell * (plus + minus))
    audit.check("temporal_increment", "block_commutation_fails", plus * shell != shell * plus, plus * shell, shell * plus)
    h_one = sp.Matrix([0, 1])
    h_two = sp.zeros(2, 1)
    lq = plus * shell * h_one + minus * shell * h_two
    pl = shell * (plus * h_one + minus * h_two)
    audit.check("temporal_increment", "intertwiner_fails", lq != pl, lq, pl)

    # Test-oracle finite-dimensional source/physical realization.
    synthesis = sp.Matrix([[1, 2], [0, 1]])
    pi_zero = sp.diag(1, 0)
    pi_one = sp.diag(0, 1)
    physical_hessian = sp.Matrix([[2, 1], [1, 3]])
    e_zero = sp.diag(1, 0)
    e_one = sp.diag(0, 1)
    r_zero = pi_zero * synthesis
    r_one = pi_one * synthesis
    audit.check("coanalysis", "shell_analysis_parseval", r_zero.T * r_zero + r_one.T * r_one == synthesis.T * synthesis, r_zero.T * r_zero + r_one.T * r_one, synthesis.T * synthesis)

    blocks = []
    for projection in (pi_zero, pi_one):
        for temporal in (e_zero, e_one):
            blocks.append(synthesis.T * projection * physical_hessian * synthesis * temporal)
    source_hessian = synthesis.T * physical_hessian * synthesis
    audit.check("coanalysis", "owner_complete_sum", sum(blocks, sp.zeros(2)) == source_hessian, sum(blocks, sp.zeros(2)), source_hessian)
    test_block = synthesis.T * pi_one * physical_hessian * synthesis * e_zero
    legal_reverse = e_zero * synthesis.T * physical_hessian * pi_one * synthesis
    audit.check("coanalysis", "legal_reverse_is_true_adjoint", test_block.T == legal_reverse, test_block.T, legal_reverse)
    audit.check("coanalysis", "forward_reverse_singular_polynomial", (test_block.T * test_block).charpoly().as_expr() == (test_block * test_block.T).charpoly().as_expr(), (test_block.T * test_block).charpoly().as_expr(), (test_block * test_block.T).charpoly().as_expr())

    # Response-map factorization: H=L^*A is enough; no ambient B or source-shell
    # commutation is required.  The chosen response is derived from a symmetric
    # test-oracle source Hessian and an invertible synthesis.
    response_hessian = sp.Matrix([[3, 1], [1, 2]])
    response = synthesis.T.inv() * response_hessian
    analysis_blocks = [pi_zero * synthesis, pi_one * synthesis]
    forward_blocks = [pi_zero * response, pi_one * response]
    analysis_forward = sum(
        (analysis.T * forward for analysis, forward in zip(analysis_blocks, forward_blocks)),
        sp.zeros(2),
    )
    forward_analysis = sum(
        (forward.T * analysis for analysis, forward in zip(analysis_blocks, forward_blocks)),
        sp.zeros(2),
    )
    audit.check("response_factorization", "source_hessian_is_response_pullback", synthesis.T * response == response_hessian, synthesis.T * response, response_hessian)
    audit.check("response_factorization", "analysis_forward_equals_hessian", analysis_forward == response_hessian, analysis_forward, response_hessian)
    audit.check("response_factorization", "reverse_aggregate_equals_hessian", forward_analysis == response_hessian, forward_analysis, response_hessian)
    audit.check("response_factorization", "quadratic_owner_not_doubled", sp.simplify((analysis_forward + forward_analysis) / 2 - response_hessian) == sp.zeros(2), (analysis_forward + forward_analysis) / 2, response_hessian)

    # The true adjoint orientation is not generally a swapped-label geometric
    # cell, even when every global hypothesis is satisfied.
    root_two = sp.sqrt(2)
    unitary_synthesis = sp.Matrix([[1, 1], [1, -1]]) / root_two
    asymmetric_hessian = sp.Matrix([[0, 1], [1, -1]])
    t_two_one = unitary_synthesis.T * pi_one * asymmetric_hessian * unitary_synthesis * e_zero
    t_one_two = unitary_synthesis.T * pi_zero * asymmetric_hessian * unitary_synthesis * e_one
    audit.check("coanalysis_scope", "swapped_geometric_cell_not_adjoint", t_two_one.T != t_one_two, t_two_one.T, t_one_two)
    source_shell_image = unitary_synthesis.T * pi_zero * sp.Matrix([1, 0])
    audit.check("coanalysis_scope", "coanalysis_not_source_shell_local", source_shell_image[0] != 0 and source_shell_image[1] != 0, source_shell_image, "both source coordinates nonzero")

    quotient_synthesis = sp.Matrix([[1, 1]])
    quotient_kernel = sp.Matrix([1, -1])
    quotient_hessian = quotient_synthesis.T * quotient_synthesis
    quotient_cell_one = quotient_hessian * e_zero
    quotient_cell_two = quotient_hessian * e_one
    audit.check("refinement_scope", "individual_cell_not_quotient_basic", quotient_cell_one * quotient_kernel != sp.zeros(2, 1), quotient_cell_one * quotient_kernel, "nonzero")
    audit.check("refinement_scope", "aggregate_is_quotient_basic", (quotient_cell_one + quotient_cell_two) * quotient_kernel == sp.zeros(2, 1), (quotient_cell_one + quotient_cell_two) * quotient_kernel, sp.zeros(2, 1))

    smooth_one = sp.eye(2) / 2
    smooth_two = sp.eye(2) / 2
    smooth_analysis_gram = synthesis.T * (smooth_one.T * smooth_one + smooth_two.T * smooth_two) * synthesis
    audit.check("frame_scope", "partition_of_unity_not_parseval", smooth_one + smooth_two == sp.eye(2) and smooth_analysis_gram != synthesis.T * synthesis, smooth_analysis_gram, synthesis.T * synthesis)

    # Same pulled Hessian, different ambient shell splits.
    line = sp.Matrix([1, 1]) / sp.sqrt(2)
    ambient_one = sp.eye(2)
    ambient_two = sp.diag(2, 0)
    pulled_one = (line.T * ambient_one * line)[0]
    pulled_two = (line.T * ambient_two * line)[0]
    split_one = (line.T * shell * ambient_one * line)[0]
    split_two = (line.T * shell * ambient_two * line)[0]
    audit.check("ambient_scope", "same_pulled_hessian", pulled_one == pulled_two, pulled_one, pulled_two)
    audit.check("ambient_scope", "shell_split_not_determined", split_one != split_two, split_one, split_two)

    # Pullback may enlarge a physical forward constant by the synthesis norm.
    gain_synthesis = sp.Matrix([2, 0])
    physical_forward = shell * sp.eye(2) * gain_synthesis
    pulled_forward = gain_synthesis.T * physical_forward
    audit.check("coanalysis_scope", "physical_forward_fixture_norm", sp.sqrt((physical_forward.T * physical_forward)[0]) == 2, sp.sqrt((physical_forward.T * physical_forward)[0]), 2)
    audit.check("coanalysis_scope", "pulled_forward_fixture_norm", sp.Abs(pulled_forward[0]) == 4, sp.Abs(pulled_forward[0]), 4)
    return {
        "temporal_increments": {"plus": plus, "minus": minus, "shell": shell, "LQ": lq, "PiL": pl},
        "shell_analysis": {"synthesis": synthesis, "source_hessian": source_hessian, "test_forward": test_block, "test_reverse": legal_reverse},
        "response_factorization": {"response": response, "hessian": response_hessian, "analysis_forward": analysis_forward, "forward_analysis": forward_analysis},
        "geometric_reverse_scope": {"t_two_one": t_two_one, "t_one_two": t_one_two, "source_shell_image": source_shell_image},
        "quotient_cell_scope": {"kernel": quotient_kernel, "cell_one_on_kernel": quotient_cell_one * quotient_kernel, "aggregate_on_kernel": quotient_hessian * quotient_kernel},
        "smooth_frame_scope": {"analysis_gram": smooth_analysis_gram, "parseval_gram": synthesis.T * synthesis},
        "ambient_nonuniqueness": {"pulled": pulled_one, "split_one": split_one, "split_two": split_two},
        "pullback_factor_fixture": {"physical_norm": 2, "pulled_norm": 4},
    }


def shifted_douglas(audit: Audit) -> dict[str, Any]:
    e, f, a, d, k = sp.symbols("e f a d k", positive=True)
    m_two = sp.simplify((e + f - sp.sqrt((e - f) ** 2 + a**2)) / 2)
    mu_three = sp.simplify((m_two + d - sp.sqrt((m_two - d) ** 2 + 4 * k**2)) / 2)
    audit.check("shifted_douglas", "two_channel_characteristic_root", sp.simplify(m_two**2 - (e + f) * m_two + e * f - a**2 / 4) == 0, sp.simplify(m_two**2 - (e + f) * m_two + e * f - a**2 / 4), 0)
    audit.check("shifted_douglas", "full_scalar_characteristic_root", sp.simplify(mu_three**2 - (m_two + d) * mu_three + m_two * d - k**2) == 0, sp.simplify(mu_three**2 - (m_two + d) * mu_three + m_two * d - k**2), 0)

    eta, zeta, b, c = sp.symbols("eta zeta b c", real=True)
    scalar_full = sp.Matrix(
        [
            [2 * eta, -a / 2, -b],
            [-a / 2, 2 * zeta, -c],
            [-b, -c, d],
        ]
    )
    schur_det = sp.simplify(
        d
        * (
            (2 * eta - b**2 / d) * (2 * zeta - c**2 / d)
            - (a / 2 + b * c / d) ** 2
        )
    )
    audit.check("shifted_douglas", "scalar_three_channel_determinant", sp.simplify(scalar_full.det() - schur_det) == 0, scalar_full.det(), schur_det)

    # Desired-gap test-oracle inputs; every threshold is derived below.
    e_test = sp.Rational(4)
    f_test = sp.Rational(3)
    a_test = sp.Rational(1)
    d_test = sp.Rational(5)
    k_test = sp.Rational(1)
    mu_test = sp.Rational(1, 2)
    tau = sp.simplify(mu_test + k_test**2 / (d_test - mu_test))
    audit.check("shifted_gap", "desired_gap_diagonal_one", e_test > tau, e_test, f"> {tau}")
    audit.check("shifted_gap", "desired_gap_diagonal_two", f_test > tau, f_test, f"> {tau}")
    audit.check("shifted_gap", "desired_gap_cross", a_test < 2 * sp.sqrt((e_test - tau) * (f_test - tau)), a_test, f"< {2 * sp.sqrt((e_test - tau) * (f_test - tau))}")

    r128 = json.loads(R128_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["budgets"]["half_debt"]
    half_margin = sp.sympify(r128["strict_margin_at_old_budget"])
    low_d = sp.Integer(1)
    low_k_sq_inside = half_margin / 2
    low_k_sq_edge = half_margin
    inside_mu = sp.simplify((half_margin + low_d - sp.sqrt((half_margin - low_d) ** 2 + 4 * low_k_sq_inside)) / 2)
    edge_mu = sp.simplify((half_margin + low_d - sp.sqrt((half_margin - low_d) ** 2 + 4 * low_k_sq_edge)) / 2)
    audit.check("half_debt", "registered_margin_positive", half_margin > 0, half_margin, "positive")
    audit.check("half_debt", "strict_low_coupling_inside", inside_mu > 0, inside_mu, "positive")
    audit.check("half_debt", "low_coupling_boundary_zero", sp.simplify(edge_mu) == 0, edge_mu, 0)
    return {
        "two_channel_lower_bound": m_two,
        "three_channel_lower_bound": mu_three,
        "desired_gap_fixture": {"mu": mu_test, "tau": tau, "e": e_test, "f": f_test, "a": a_test, "d": d_test, "k": k_test},
        "half_debt": {"margin": half_margin, "inside_k_squared": low_k_sq_inside, "inside_gap": inside_mu, "edge_k_squared": low_k_sq_edge, "edge_gap": edge_mu},
        "scalar_determinant": scalar_full.det(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "endpoint": endpoint_trace_excess(audit),
        "direct_hessian": direct_covariance_normal_hessian(audit),
        "shortcut_boundaries": analytic_shortcut_boundaries(audit),
        "shell_coanalysis": temporal_increment_and_shell_coanalysis(audit),
        "shifted_douglas": shifted_douglas(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-129 primary {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions; "
        f"output={arguments.output}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
