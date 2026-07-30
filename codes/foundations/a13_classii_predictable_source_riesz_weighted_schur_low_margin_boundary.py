#!/usr/bin/env python3
"""Primary exact audit for the scoped R-127 A13 checkpoint."""

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
RESULT_ID = "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY"
SCHEMA = "tect/a13-predictable-source-riesz-weighted-schur-low-margin-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"
R120_OUTPUT = CLAIM_DIR / "runs/2026-07-29-primary-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
R093_OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-augmented-perspective-gibbs-gap-information-boundary/result.json"
R126_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-total-symbol-euler-low-injected-loewner-boundary/result.json"


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
                "predictable_source_adjoint_and_quotient_riesz_symbolically_audited": True,
                "unrestricted_covariance_collapse_counterfixture_executed": True,
                "source_completion_coefficient_derived_from_r093_q": True,
                "weighted_schur_constants_and_domains_audited": True,
                "augmented_low_loewner_algebra_audited": True,
                "loewner_saturation_incompatibility_fixture_executed": True,
                "constant_gauge_requires_absolute_anchor_verified": True,
                "coherent_residual_curvature_audited_for_fixed_base_and_s_independent_data": True,
                "production_projected_force_identification_proved": False,
                "unified_production_bound_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-127 proves exact source-space, weighted-Schur, augmented-Loewner, "
                "and boundary identities. It does not identify the complete production endpoint "
                "Hessian with the admissible root-shell block, bound the production force, close "
                "the forward/legal-reverse/balanced/low estimate, prove OVERLAP_src or Nelson, "
                "remove cutoffs, construct the interacting measure, or close Sector A."
            ),
        }


def exact_total_symbol_hessian(audit: Audit) -> dict[str, Any]:
    s, t = sp.symbols("s t", real=True)
    weights = (sp.Rational(1, 3), sp.Rational(2, 3))
    states = (sp.Rational(1, 2), sp.Rational(-3, 2))
    directions_h = (sp.Rational(2, 3), sp.Rational(-1, 4))
    directions_k = (sp.Rational(-2, 5), sp.Rational(3, 7))
    velocities = (sp.Rational(4, 3), sp.Rational(-2, 5))
    velocity_h = (sp.Rational(1, 6), sp.Rational(5, 8))
    velocity_k = (sp.Rational(-3, 10), sp.Rational(2, 9))
    gamma = sp.Rational(7, 11)
    c0, c1, c2 = sp.Rational(3, 5), sp.Rational(-2, 7), sp.Rational(5, 13)

    def coeff(w: sp.Expr) -> sp.Expr:
        return c0 + c1 * w + c2 * w**2

    moved_w = [w + s * h + t * k for w, h, k in zip(states, directions_h, directions_k)]
    moved_v = [v + s * dh + t * dk for v, dh, dk in zip(velocities, velocity_h, velocity_k)]
    coefficients = [coeff(w) for w in moved_w]
    phi = sum(p * c * v for p, c, v in zip(weights, coefficients, moved_v))
    total = gamma * sum(p * c**2 for p, c in zip(weights, coefficients)) - phi**2
    direct = sp.diff(total, s, t).subs({s: 0, t: 0})

    base_c = [coeff(w) for w in states]
    dc_h = [(c1 + 2 * c2 * w) * h for w, h in zip(states, directions_h)]
    dc_k = [(c1 + 2 * c2 * w) * k for w, k in zip(states, directions_k)]
    d2c = [2 * c2 * h * k for h, k in zip(directions_h, directions_k)]
    base_phi = sum(p * c * v for p, c, v in zip(weights, base_c, velocities))
    dot_phi_h = sum(
        p * (ch * v + c * dh)
        for p, ch, v, c, dh in zip(weights, dc_h, velocities, base_c, velocity_h)
    )
    dot_phi_k = sum(
        p * (ck * v + c * dk)
        for p, ck, v, c, dk in zip(weights, dc_k, velocities, base_c, velocity_k)
    )
    ddot_phi = sum(
        p * (d2 * v + ch * dk + ck * dh)
        for p, d2, v, ch, dk, ck, dh in zip(
            weights, d2c, velocities, dc_h, velocity_k, dc_k, velocity_h
        )
    )
    ddot_b = sum(
        p * 2 * (ch * ck + c * d2)
        for p, ch, ck, c, d2 in zip(weights, dc_h, dc_k, base_c, d2c)
    )
    assembled = sp.simplify(gamma * ddot_b - 2 * (dot_phi_h * dot_phi_k + base_phi * ddot_phi))
    audit.check("hessian", "finite_atom_cross_derivative", sp.simplify(direct - assembled) == 0, direct, assembled)
    audit.check("hessian", "second_current_term_present", ddot_phi != 0, ddot_phi, "nonzero")
    audit.check("hessian", "polarized_first_variations_present", dot_phi_h * dot_phi_k != 0, dot_phi_h * dot_phi_k, "nonzero")
    return {
        "direct_cross_derivative": direct,
        "assembled_cross_derivative": assembled,
        "ddot_phi": ddot_phi,
    }


def predictable_source_riesz(audit: Audit) -> dict[str, Any]:
    # Two equiprobable terminal atoms xi=+/-1.  Block one sees the trivial
    # sigma-field; block two sees xi.  S_1=S_2=1.
    xis = (sp.Integer(-1), sp.Integer(1))
    probability = sp.Rational(1, 2)
    g1 = sum(probability * xi for xi in xis)
    g2 = xis
    legal_riesz = tuple(g1 + xi for xi in xis)
    unrestricted = tuple(2 * xi for xi in xis)
    source_norm_sq = g1**2 + sum(probability * xi**2 for xi in g2)
    covariance_energy = sum(probability * xi * (2 * xi) for xi in xis)
    audit.check("riesz", "first_predictable_projection", g1 == 0, g1, 0)
    audit.check("riesz", "legal_riesz", legal_riesz == xis, legal_riesz, xis)
    audit.check("riesz", "unrestricted_covariance_factor_two", unrestricted == tuple(2 * x for x in legal_riesz), unrestricted, tuple(2 * x for x in legal_riesz))
    audit.check("riesz", "source_norm", source_norm_sq == 1, source_norm_sq, 1)
    audit.check("riesz", "covariance_energy_upper", source_norm_sq <= covariance_energy, (source_norm_sq, covariance_energy), "source <= covariance")

    a, b, c = sp.symbols("a b c", real=True)
    lhs = sum(probability * xi * (a + b + c * xi) for xi in xis)
    rhs = g1 * a + sum(probability * (b + c * xi) * xi for xi in xis)
    audit.check("riesz", "legal_adjoint_duality", sp.simplify(lhs - rhs) == 0, lhs, rhs)
    quotient_norm = sp.expand(a**2 + sum(probability * (xi - a) ** 2 for xi in xis))
    audit.check("riesz", "quotient_norm_minimum", sp.simplify(quotient_norm - (1 + 2 * a**2)) == 0, quotient_norm, 1 + 2 * a**2)

    r120 = json.loads(R120_OUTPUT.read_text(encoding="utf-8"))
    cm_squared = sp.Float(str(r120["diagnostics"]["horizontal_synthesis"]["c_cm"]), 40)
    cm_norm = sp.sqrt(cm_squared)
    audit.check("riesz", "r120_squared_constant_positive", cm_squared > 9, cm_squared, "> 9")
    audit.check("riesz", "r120_norm_constant_interval", sp.Float("3.03") < cm_norm < sp.Float("3.04"), cm_norm, "between 3.03 and 3.04")

    r093 = json.loads(R093_OUTPUT.read_text(encoding="utf-8"))
    q_inverse_rows = [row for row in r093["assertions"] if row["name"] == "q_inverse"]
    audit.check("completion", "r093_q_inverse_unique", len(q_inverse_rows) == 1, len(q_inverse_rows), 1)
    q_inverse = sp.Rational(q_inverse_rows[0]["actual"])
    q_production = 1 / q_inverse
    source_cost = 1 / (2 * q_production)
    adverse_cost = 1 / (4 * source_cost)
    h, g = sp.symbols("h g", real=True)
    completed = source_cost * (h + g / (2 * source_cost)) ** 2 - adverse_cost * g**2
    original = h * g + source_cost * h**2
    audit.check("completion", "q_ten_ninths_identity", sp.expand(completed - original) == 0, sp.expand(completed), original)
    audit.check("completion", "source_cost_from_q", source_cost == sp.Rational(9, 20), source_cost, sp.Rational(9, 20))
    audit.check("completion", "adverse_force_square_coefficient", adverse_cost == sp.Rational(5, 9), adverse_cost, sp.Rational(5, 9))
    return {
        "legal_riesz_atoms": legal_riesz,
        "unrestricted_covariance_atoms": unrestricted,
        "source_norm_squared": source_norm_sq,
        "covariance_energy": covariance_energy,
        "r120_cm_squared": cm_squared,
        "r120_cm_norm": cm_norm,
        "production_q": q_production,
        "source_energy_coefficient": source_cost,
        "source_completion_cost": adverse_cost,
    }


def weighted_schur(audit: Audit) -> dict[str, Any]:
    d, q = sp.symbols("d q", positive=True)
    t_weight = q / (1 - d)
    column_constant = sp.simplify(1 / (1 - q * t_weight))
    audit.check(
        "schur",
        "column_constant_formula",
        sp.simplify(column_constant - 1 / (1 - q**2 / (1 - d))) == 0,
        column_constant,
        1 / (1 - q**2 / (1 - d)),
    )
    # Row constants obey R_0=1 and R_(p+1)=(1-d)^(p+1)+d R_p;
    # for d<=1/2 induction gives R_p<=1.
    mixed_d, mixed_q = sp.Rational(1, 2), sp.Rational(1, 4)
    audit.check("schur", "mixed_domain_d", 0 < mixed_d <= sp.Rational(1, 2), mixed_d, "0 < d <= 1/2")
    audit.check("schur", "mixed_domain_q", mixed_q**2 < 1 - mixed_d, mixed_q**2, f"< {1 - mixed_d}")
    mixed_factor = sp.sqrt(1 / (1 - mixed_q**2 / (1 - mixed_d)))
    mixed_collar_one = mixed_factor / 4
    mixed_hs_collar_one = sp.Rational(2, 1) / sp.sqrt(45)
    audit.check("schur", "mixed_factor", mixed_factor == sp.sqrt(sp.Rational(8, 7)), mixed_factor, sp.sqrt(sp.Rational(8, 7)))
    audit.check("schur", "mixed_improves_hilbert_schmidt", mixed_collar_one < mixed_hs_collar_one, mixed_collar_one, mixed_hs_collar_one)

    far_d, far_q = sp.Rational(1, 8), sp.Rational(1, 16)
    audit.check("schur", "far_domain_d", 0 < far_d <= sp.Rational(1, 2), far_d, "0 < d <= 1/2")
    audit.check("schur", "far_domain_q", far_q**2 < 1 - far_d, far_q**2, f"< {1 - far_d}")
    far_factor = sp.sqrt(1 / (1 - far_q**2 / (1 - far_d)))
    far_collar_one = far_factor / 16
    far_hs_collar_one = sp.Rational(8, 1) / sp.sqrt(16065)
    audit.check("schur", "far_factor", far_factor == sp.sqrt(sp.Rational(224, 223)), far_factor, sp.sqrt(sp.Rational(224, 223)))
    audit.check("schur", "far_improves_hilbert_schmidt", far_collar_one < far_hs_collar_one, far_collar_one, far_hs_collar_one)

    r126 = json.loads(R126_OUTPUT.read_text(encoding="utf-8"))
    operator_budget = sp.sympify(
        r126["diagnostics"]["loewner_shells"]["production_operator_budget"]
    )
    new_threshold = sp.sqrt(14) * operator_budget
    old_threshold = sp.sqrt(45) * operator_budget / 2
    improvement_percent = sp.N(100 * (new_threshold / old_threshold - 1), 18)
    audit.check("schur", "new_acceptance_threshold_larger", new_threshold > old_threshold, new_threshold, old_threshold)
    audit.check("schur", "threshold_interval", sp.Float("3.44") < new_threshold < sp.Float("3.45"), sp.N(new_threshold, 18), "between 3.44 and 3.45")
    audit.check("schur", "improvement_percent_interval", sp.Float("11.5") < improvement_percent < sp.Float("11.6"), improvement_percent, "between 11.5 and 11.6")

    j0, j, k, collar = sp.symbols("j0 j k collar", integer=True, nonnegative=True)
    root = j0 + j
    shell = root + collar + k
    mixed_relabel = sp.simplify(2 ** (root - 2 * shell) / (2 ** (-j0 - 2 * collar) * mixed_d**j * mixed_q**k))
    far_relabel = sp.simplify(2 ** (root - 4 * shell) / (2 ** (-3 * j0 - 4 * collar) * far_d**j * far_q**k))
    audit.check("schur", "mixed_exponent_relabel", mixed_relabel == 1, mixed_relabel, 1)
    audit.check("schur", "far_exponent_relabel", far_relabel == 1, far_relabel, 1)

    row_values = []
    for p in range(9):
        row = sum(mixed_d**j * (1 - mixed_d) ** (p - j) for j in range(p + 1))
        row_values.append(row)
    audit.check("schur", "mixed_row_induction_fixture", max(row_values) == 1, max(row_values), 1)
    return {
        "general_column_constant": column_constant,
        "mixed_operator_factor": mixed_factor,
        "mixed_collar_one_coefficient": mixed_collar_one,
        "mixed_hilbert_schmidt_coefficient": mixed_hs_collar_one,
        "far_operator_factor": far_factor,
        "far_collar_one_coefficient": far_collar_one,
        "far_hilbert_schmidt_coefficient": far_hs_collar_one,
        "production_operator_budget": operator_budget,
        "new_collar_one_mixed_only_Cmix_times_2_minus_j0_ceiling": new_threshold,
        "old_Cmix_times_2_minus_j0_threshold": old_threshold,
        "threshold_improvement_percent": improvement_percent,
    }


def augmented_loewner(audit: Audit) -> dict[str, Any]:
    eta, zeta = sp.Rational(2, 5), sp.Rational(3, 7)
    r, s, a = sp.Rational(1, 9), sp.Rational(1, 10), sp.Rational(1, 8)
    b, c, d_low = sp.Rational(1, 11), sp.Rational(-1, 13), sp.Rational(5, 6)
    m2 = sp.Matrix([[2 * eta - r, -a / 2], [-a / 2, 2 * zeta - s]])
    coupling = sp.Matrix([b, c])
    m3 = m2.row_join(-coupling)
    m3 = m3.col_join(sp.Matrix([[-b, -c, d_low]]))
    schur = sp.simplify(m2 - coupling * coupling.T / d_low)
    audit.check("loewner", "three_by_three_positive_fixture", all(minor > 0 for minor in (m3[0, 0], sp.det(m3[:2, :2]), sp.det(m3))), [m3[0, 0], sp.det(m3[:2, :2]), sp.det(m3)], "positive")
    audit.check("loewner", "schur_complement_positive_fixture", schur[0, 0] > 0 and sp.det(schur) > 0, (schur[0, 0], sp.det(schur)), "positive")
    audit.check("loewner", "determinant_factorization", sp.simplify(sp.det(m3) - d_low * sp.det(schur)) == 0, sp.det(m3), d_low * sp.det(schur))
    nonzero_boundary_coupling = sp.Matrix([[sp.Integer(1), -sp.Rational(1, 3)], [-sp.Rational(1, 3), 0]])
    audit.check("loewner", "zero_low_diagonal_forces_zero_coupling", sp.det(nonzero_boundary_coupling) < 0, sp.det(nonzero_boundary_coupling), "negative")

    eta_s, zeta_s, theta = sp.Rational(4, 9), sp.Rational(9, 16), sp.Rational(1, 4)
    a_sat = 4 * sp.sqrt(eta_s * zeta_s)
    m_sat = sp.Matrix([[2 * eta_s, -a_sat / 2], [-a_sat / 2, 2 * zeta_s]])
    null_vector = sp.Matrix([sp.sqrt(zeta_s), sp.sqrt(eta_s)])
    audit.check("loewner", "saturated_null_vector", m_sat * null_vector == sp.zeros(2, 1), m_sat * null_vector, sp.zeros(2, 1))
    b_sat, c_sat = sp.sqrt(eta_s), -sp.sqrt(zeta_s)
    cancellation = sp.simplify(b_sat * sp.sqrt(zeta_s) + c_sat * sp.sqrt(eta_s))
    audit.check("loewner", "saturation_weighted_cancellation", cancellation == 0, cancellation, 0)
    incompatible = m_sat.row_join(-sp.Matrix([1, 0]))
    incompatible = incompatible.col_join(sp.Matrix([[-1, 0, 1]]))
    audit.check("loewner", "saturation_noncancelling_determinant", sp.det(incompatible) == -sp.Rational(9, 8), sp.det(incompatible), -sp.Rational(9, 8))
    compatible_d = sp.Matrix([sp.sqrt(eta_s), -sp.sqrt(zeta_s)])
    incompatible_d = sp.Matrix([1, 0])
    projector = sp.simplify(m_sat * m_sat.pinv())
    audit.check("loewner", "singular_range_compatible", sp.simplify(projector * compatible_d - compatible_d) == sp.zeros(2, 1), projector * compatible_d, compatible_d)
    audit.check("loewner", "singular_range_incompatible", sp.simplify(projector * incompatible_d - incompatible_d) != sp.zeros(2, 1), projector * incompatible_d, "not d")

    a_strict = (1 - theta) * a_sat
    m_strict = sp.Matrix([[2 * eta_s, -a_strict / 2], [-a_strict / 2, 2 * zeta_s]])
    lambda_min = eta_s + zeta_s - sp.sqrt((eta_s - zeta_s) ** 2 + a_strict**2 / 4)
    lambda_min_negative = eta_s + zeta_s - sp.sqrt(
        (eta_s - zeta_s) ** 2 + (-a_strict) ** 2 / 4
    )
    lower = 2 * eta_s * zeta_s * (2 * theta - theta**2) / (eta_s + zeta_s)
    audit.check(
        "loewner",
        "strict_margin_lower_bound_and_sign_symmetry",
        sp.N(lambda_min - lower, 40) >= 0
        and sp.simplify(lambda_min_negative - lambda_min) == 0,
        (lambda_min, lambda_min_negative),
        (f">= {lower}", "equal under a -> -a"),
    )

    eta_a, zeta_a, a_a, bb, cc = sp.symbols("eta_a zeta_a a_a bb cc", nonzero=True)
    affine_matrix = sp.Matrix([[2 * eta_a, -a_a / 2], [-a_a / 2, 2 * zeta_a]])
    affine_cost = sp.simplify((sp.Matrix([bb, cc]).T * affine_matrix.inv() * sp.Matrix([bb, cc]))[0])
    expected_cost = (2 * zeta_a * bb**2 + a_a * bb * cc + 2 * eta_a * cc**2) / (4 * eta_a * zeta_a - a_a**2 / 4)
    audit.check("loewner", "affine_low_cost_formula", sp.simplify(affine_cost - expected_cost) == 0, affine_cost, expected_cost)
    return {
        "augmented_matrix_fixture": m3,
        "low_schur_complement_fixture": schur,
        "saturation_null_vector": null_vector,
        "strict_margin_lambda_min": lambda_min,
        "strict_margin_lower_bound": lower,
        "affine_low_cost": affine_cost,
    }


def boundary_identities(audit: Audit) -> dict[str, Any]:
    # Strict-past legality gives duality, not a sign for the reverse middle.
    tanh_square = sp.symbols("T2", positive=True)
    c_pos, c_neg = sp.Rational(1, 2), sp.Rational(-1, 2)
    reverse_pos = sp.simplify(tanh_square * (c_pos + c_pos**2 / 2))
    reverse_neg = sp.simplify(tanh_square * (c_neg + c_neg**2 / 2))
    audit.check("boundary", "legal_reverse_positive_fixture", reverse_pos > 0, reverse_pos, "positive")
    audit.check("boundary", "legal_reverse_negative_fixture", reverse_neg < 0, reverse_neg, "negative")
    forward = tanh_square / 2
    terminal_pos = tanh_square * (1 + c_pos) ** 2 / 2
    terminal_neg = tanh_square * (1 + c_neg) ** 2 / 2
    audit.check("boundary", "two_step_endpoint_checksum_positive", sp.simplify(forward + reverse_pos - terminal_pos) == 0, forward + reverse_pos, terminal_pos)
    audit.check("boundary", "two_step_endpoint_checksum_negative", sp.simplify(forward + reverse_neg - terminal_neg) == 0, forward + reverse_neg, terminal_neg)

    q, constant, partition = sp.symbols("q constant partition", positive=True)
    shifted_partition = sp.exp(-q * constant) * partition
    shifted_free_energy = sp.simplify(-sp.log(shifted_partition) / q)
    base_free_energy = -sp.log(partition) / q
    audit.check("gibbs", "constant_gauge_shift", sp.simplify(sp.expand_log(shifted_free_energy, force=True) - base_free_energy - constant) == 0, sp.expand_log(shifted_free_energy, force=True), base_free_energy + constant)
    e1, e2 = sp.symbols("e1 e2", real=True)
    z_base = sp.exp(-q * e1) + sp.exp(-q * e2)
    z_shift = sp.exp(-q * (e1 + constant)) + sp.exp(-q * (e2 + constant))
    probability_base = sp.exp(-q * e1) / z_base
    probability_shift = sp.exp(-q * (e1 + constant)) / z_shift
    audit.check("gibbs", "normalized_two_atom_law_invariant", sp.simplify(probability_base - probability_shift) == 0, probability_shift, probability_base)

    # Exact two-atom residual interpolation checked at s=0.
    u = sp.symbols("u", real=True)
    q0 = sp.Rational(10, 9)
    b0, a0, delta_tau = sp.Rational(2, 5), sp.Rational(3, 4), sp.Rational(1, 7)
    xis = (-1, 1)
    residuals = (sp.Rational(1, 3), sp.Rational(-2, 5))
    p_atoms = [((b0 + a0 * xi + u * rr) ** 2 - (a0**2 + u * delta_tau)) / 2 for xi, rr in zip(xis, residuals)]
    partition_u = sum(sp.exp(-q0 * p) for p in p_atoms) / 2
    psi = sp.log(partition_u)
    psi_second_expression = sp.diff(psi, u, 2)
    weights_u = [sp.exp(-q0 * p) for p in p_atoms]
    normalizer_u = sum(weights_u)
    probabilities_u = [w / normalizer_u for w in weights_u]
    pdot = [sp.diff(p, u) for p in p_atoms]
    mean_dot = sum(p * value for p, value in zip(probabilities_u, pdot))
    variance_dot = sum(p * (value - mean_dot) ** 2 for p, value in zip(probabilities_u, pdot))
    residual_square = sum(p * rr**2 for p, rr in zip(probabilities_u, residuals))
    curvature_expression = q0**2 * variance_dot - q0 * residual_square
    for index, point in enumerate((sp.Rational(-1, 3), sp.Integer(0), sp.Rational(2, 5))):
        psi_second = sp.simplify(psi_second_expression.subs(u, point))
        curvature = sp.simplify(curvature_expression.subs(u, point))
        audit.check(
            "interpolation",
            f"variance_minus_curvature_fixture_{index}",
            sp.simplify(psi_second - curvature) == 0,
            psi_second,
            curvature,
        )
    audit.check("interpolation", "linear_anchor_nonzero_fixture", sp.diff(psi, u).subs(u, 0) != 0, sp.diff(psi, u).subs(u, 0), "nonzero")
    return {
        "reverse_positive": reverse_pos,
        "reverse_negative": reverse_neg,
        "gauge_free_energy_shift": constant,
        "coherent_interpolation_second_derivative_at_zero": sp.simplify(psi_second_expression.subs(u, 0)),
        "coherent_interpolation_linear_anchor": sp.diff(psi, u).subs(u, 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "hessian": exact_total_symbol_hessian(audit),
        "predictable_source": predictable_source_riesz(audit),
        "weighted_schur": weighted_schur(audit),
        "augmented_loewner": augmented_loewner(audit),
        "boundaries": boundary_identities(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-127 primary {payload['status']} {payload['assertions_passed']}/{payload['assertions_total']}")
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} expected={row['expected']!r}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
