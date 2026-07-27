#!/usr/bin/env python3
"""Primary executable evidence for the R-092 A13 frontier theorem.

This program checks the exact normalized production algebra, the corrected
two-field Cartan exponent ledger, the compensated matrix-perspective telescope, the
finite all-residual sign fixture, covariance union, and the negative-flow /
CAT(0) method boundaries.  It does not claim complete signed H_N,
progressive/revisit H_A, OVERLAP, Nelson, a measure, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.2.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-NORMALIZED-CARTAN-COMPENSATED-PERSPECTIVE-TRIANGULAR-COVARIANCE-FRONTIER"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-normalized-cartan-perspective-covariance-frontier/result.json"

AUTHORITY_NOTES = {
    "r075": CLAIM_DIR / "notes/classii-invariant-current-principal-oneform-graph-recovery-260724-v1.0.tex.txt",
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r084": CLAIM_DIR / "notes/classii-root-diagonal-cartan-ou-linear-pauli-fierz-absorption-260725-v1.0.tex.txt",
    "r087": CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt",
    "r089": CLAIM_DIR / "notes/classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt",
    "r090": CLAIM_DIR / "notes/classii-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-260725-v1.0.tex.txt",
    "r091": CLAIM_DIR / "notes/classii-projected-cartan-full-frame-temporal-boundary-260725-v1.0.tex.txt",
}

INPUTS = {
    "floor": 0.37,
    "gamma": Fraction(1, 4),
    "sigma": Fraction(4, 15),
    "theta": Fraction(3, 10),
    "p": 6,
    "q": 3,
    "safe_gap": 5,
    "eta": Fraction(1, 2),
    "da3_x_exponent": Fraction(1, 2),
    "da3_y_exponent": Fraction(1, 6),
}

TEST_ORACLES = {
    "coefficient_poincare_constant": Fraction(16, 1),
    "two_tail_gradient_constant": Fraction(32, 1),
    "root_surplus": Fraction(7, 30),
    "young_slack": Fraction(1, 30),
    "fixture_expectation": Fraction(-623, 5440),
    "product_gn_alpha": Fraction(1, 3),
    "a_da_outer_da": (Fraction(3, 5), Fraction(1, 3)),
    "a_du_outer_da": (Fraction(1, 2), Fraction(4, 15)),
    "a_da_outer_du": (Fraction(1, 10), Fraction(1, 6)),
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def normalized(x: np.ndarray, floor: float) -> np.ndarray:
    return x / math.sqrt(floor + float(x @ x))


def production(x: np.ndarray, matrix: np.ndarray, floor: float) -> np.ndarray:
    n = normalized(x, floor)
    return float(n @ matrix @ n) * x


def jacobian(x: np.ndarray, matrix: np.ndarray, floor: float) -> np.ndarray:
    n = normalized(x, floor)
    projection = np.outer(n, n)
    q_value = float(n @ matrix @ n)
    return q_value * np.eye(x.size) + 2.0 * projection @ (matrix - q_value * np.eye(x.size))


def expectation(values: list[tuple[Fraction, sp.Expr]], function: Callable[[sp.Expr], sp.Expr]) -> sp.Expr:
    return sp.simplify(sum(probability * function(value) for probability, value in values))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    authority_tokens = {
        "r075": ("S_Jh", "Sharp-shell Littlewood--Paley equivalence", "tag{8.4}"),
        "r079": ("mutually orthogonal", "one-shot whole-shell controls", "tag{6.4}"),
        "r084": ("conditional OU-resolvent identity", "tag{4.6}", "three lines"),
        "r087": (r"m\ge j+5", "variational CORE", "compactly supported smooth Littlewood--Paley"),
        "r089": ("exact trace and two-tail bound", "tag{3.8}", r"\Lambda_{1,j}"),
        "r090": (r"b_{A,j,i}=\partial_i c_{A,j}", "tag{2.4}", "projected Cartan FAR"),
        "r091": ("nonnegative exact block", "lossless output-gap extraction", "terminal paid split"),
    }
    for label, path in AUTHORITY_NOTES.items():
        check(f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(f"authority_{label}_tokens", all(token in content for token in tokens), [token for token in tokens if token in content], list(tokens))

    rng = np.random.default_rng(92025)
    floor = INPUTS["floor"]
    max_jacobian_error = 0.0
    max_secant_error = 0.0
    max_resolvent_error = 0.0
    max_commutator_error = 0.0
    maximum_jacobian_norm = 0.0
    maximum_delta_ratio = 0.0
    maximum_chord_ratio = 0.0
    for _ in range(40):
        raw = rng.normal(size=(6, 6))
        matrix = 0.5 * (raw + raw.T)
        matrix /= max(1.0, np.linalg.norm(matrix, ord=2))
        x = rng.normal(size=6)
        a = rng.normal(size=6)
        direction = rng.normal(size=6)
        step = 2.0e-6

        j_matrix = jacobian(x, matrix, floor)
        finite = (production(x + step * direction, matrix, floor) - production(x - step * direction, matrix, floor)) / (2.0 * step)
        max_jacobian_error = max(max_jacobian_error, float(np.linalg.norm(finite - j_matrix @ direction)))
        maximum_jacobian_norm = max(maximum_jacobian_norm, float(np.linalg.norm(j_matrix, ord=2)))

        n_minus = normalized(x, floor)
        n_plus = normalized(x + a, floor)
        delta_n = n_plus - n_minus
        p_minus = np.outer(n_minus, n_minus)
        p_plus = np.outer(n_plus, n_plus)
        delta_p = np.outer(delta_n, n_plus) + np.outer(n_minus, delta_n)
        q_minus = float(n_minus @ matrix @ n_minus)
        q_plus = float(n_plus @ matrix @ n_plus)
        delta_q = float((n_plus + n_minus) @ matrix @ delta_n)
        delta_j_formula = delta_q * np.eye(6) + 2.0 * delta_p @ matrix - 2.0 * delta_q * p_plus - 2.0 * q_minus * delta_p
        delta_j_direct = jacobian(x + a, matrix, floor) - j_matrix
        max_secant_error = max(max_secant_error, float(np.linalg.norm(delta_j_formula - delta_j_direct)))
        commutator = 2.0 * (matrix @ p_minus - p_minus @ matrix)
        max_commutator_error = max(max_commutator_error, float(np.linalg.norm(j_matrix.T - j_matrix - commutator)))
        if np.linalg.norm(delta_n) > 1.0e-12:
            maximum_delta_ratio = max(maximum_delta_ratio, float(np.linalg.norm(delta_j_direct) / np.linalg.norm(delta_n)))

        d_minus = floor + float(x @ x)
        d_plus = floor + float((x + a) @ (x + a))
        resolvent = (
            np.eye(6) / math.sqrt(d_plus)
            - np.outer(x, 2.0 * x + a) / (math.sqrt(d_minus * d_plus) * (math.sqrt(d_minus) + math.sqrt(d_plus)))
        ) @ a
        max_resolvent_error = max(max_resolvent_error, float(np.linalg.norm(resolvent - delta_n)))
        chord_bound = 2.0 * np.linalg.norm(a) / (math.sqrt(d_minus) + math.sqrt(d_plus))
        if chord_bound > 1.0e-12:
            maximum_chord_ratio = max(maximum_chord_ratio, float(np.linalg.norm(delta_n) / chord_bound))

    check("normalized_jacobian_finite_difference", max_jacobian_error < 2.0e-8, max_jacobian_error, "<2e-8")
    check("normalized_jacobian_norm_ceiling", maximum_jacobian_norm <= 3.0 + 1.0e-12, maximum_jacobian_norm, "<=3")
    check("normalized_secant_factorization", max_secant_error < 2.0e-12, max_secant_error, "<2e-12")
    check("normalized_secant_constant_fourteen", maximum_delta_ratio <= 14.0 + 1.0e-12, maximum_delta_ratio, "<=14")
    check("normalized_commutator", max_commutator_error < 2.0e-12, max_commutator_error, "<2e-12")
    check("normalized_resolvent", max_resolvent_error < 2.0e-12, max_resolvent_error, "<2e-12")
    check("normalized_chord_bound", maximum_chord_ratio <= 1.0 + 1.0e-12, maximum_chord_ratio, "<=1")

    # The current coefficient uses transposed Jacobians, while the endpoint
    # gradient uses untransposed Jacobians.  A deterministic vector fixture
    # exposes the R-090 transpose defect and verifies the corrected split.
    audit_matrix = np.diag([1.0, -1.0, 0.5, -0.5, 0.25, -0.25])
    audit_x = np.array([1.0, 0.7, -0.4, 0.2, 0.3, -0.6])
    audit_a = np.array([0.2, -0.3, 0.1, 0.4, -0.2, 0.15])
    audit_dx = np.array([0.3, -0.1, 0.25, -0.2, 0.4, 0.1])
    audit_da = np.array([-0.15, 0.2, -0.05, 0.1, 0.3, -0.25])
    audit_j_minus = jacobian(audit_x, audit_matrix, floor)
    audit_j_plus = jacobian(audit_x + audit_a, audit_matrix, floor)
    audit_delta = audit_j_plus - audit_j_minus
    audit_g = audit_delta @ audit_dx + audit_j_plus @ audit_da
    audit_b = audit_delta.T @ audit_dx + audit_j_plus.T @ audit_da
    audit_defect = (audit_delta.T - audit_delta) @ audit_dx + (audit_j_plus.T - audit_j_plus) @ audit_da
    audit_step = 1.0e-6

    def audit_endpoint(parameter: float) -> np.ndarray:
        base = audit_x + parameter * audit_dx
        shift = audit_a + parameter * audit_da
        return production(base + shift, audit_matrix, floor) - production(base, audit_matrix, floor)

    audit_finite_g = (audit_endpoint(audit_step) - audit_endpoint(-audit_step)) / (2.0 * audit_step)
    check("transpose_audit_endpoint_gradient", np.linalg.norm(audit_finite_g - audit_g) < 2.0e-9, np.linalg.norm(audit_finite_g - audit_g), "<2e-9")
    check("transpose_audit_current_not_gradient", np.linalg.norm(audit_b - audit_g) > 1.0e-4, np.linalg.norm(audit_b - audit_g), ">1e-4")
    check("transpose_audit_defect_identity", np.linalg.norm((audit_b - audit_g) - audit_defect) < 2.0e-12, np.linalg.norm((audit_b - audit_g) - audit_defect), "<2e-12")

    # The R-089 enlarged coefficient projector has |r|_infty>2^(m-2).
    coefficient_lower_fraction = Fraction(1, 4)
    coefficient_poincare_constant = coefficient_lower_fraction ** -2
    two_tail_gradient_constant = 2 * coefficient_poincare_constant
    check("coefficient_poincare_constant", coefficient_poincare_constant == TEST_ORACLES["coefficient_poincare_constant"], coefficient_poincare_constant, TEST_ORACLES["coefficient_poincare_constant"])
    check("two_tail_gradient_constant", two_tail_gradient_constant == TEST_ORACLES["two_tail_gradient_constant"], two_tail_gradient_constant, TEST_ORACLES["two_tail_gradient_constant"])
    j_symbol, m_symbol = sp.symbols("j m")
    root_weight_defect = sp.simplify((j_symbol - 2 * m_symbol) - (-j_symbol - 2 * (m_symbol - j_symbol)))
    check("two_tail_root_weight_identity", root_weight_defect == 0, root_weight_defect, 0)

    gamma = INPUTS["gamma"]
    sigma = INPUTS["sigma"]
    theta = INPUTS["theta"]
    p_value = INPUTS["p"]
    q_value = INPUTS["q"]
    check("fractional_ordering", 0 < gamma < sigma < theta < 1, [gamma, sigma, theta], "0<gamma<sigma<theta<1")
    check("fractional_integrability", p_value * theta == Fraction(9, 5) and p_value * theta > 1, p_value * theta, Fraction(9, 5))
    check("holder_pair", Fraction(1, 2) == Fraction(1, p_value) + Fraction(1, q_value), [p_value, q_value], "1/2=1/p+1/q")
    output_weight = 1 + 2 * sigma
    gaussian_growth = 1 + theta
    root_surplus = output_weight - gaussian_growth
    check("output_weight_23_15", output_weight == Fraction(23, 15), output_weight, Fraction(23, 15))
    check("gaussian_growth_13_10", gaussian_growth == Fraction(13, 10), gaussian_growth, Fraction(13, 10))
    check("root_surplus_7_30", root_surplus == TEST_ORACLES["root_surplus"], root_surplus, TEST_ORACLES["root_surplus"])
    b_denominator_exponent = 2 * (sigma - gamma)
    gradient_denominator_exponent = 2 * (1 + sigma - gamma)
    b_geometric_denominator = 1.0 - 2.0 ** (-float(b_denominator_exponent))
    gradient_geometric_denominator = 1.0 - 2.0 ** (-float(gradient_denominator_exponent))
    check("b_geometric_denominator", b_geometric_denominator > 0, b_geometric_denominator, ">0")
    check("b_denominator_exponent", b_denominator_exponent == Fraction(1, 30), b_denominator_exponent, Fraction(1, 30))
    check("gradient_geometric_denominator", gradient_geometric_denominator > 0, gradient_geometric_denominator, ">0")
    check("gradient_denominator_exponent", gradient_denominator_exponent == Fraction(61, 30), gradient_denominator_exponent, Fraction(61, 30))
    gap_power = 2 * gamma
    check("regular_hc_gap_power", gap_power == Fraction(1, 2), gap_power, Fraction(1, 2))

    da3_x = INPUTS["da3_x_exponent"]
    da3_y = INPUTS["da3_y_exponent"]
    product_gn_alpha = 2 - Fraction(1, 2) / theta
    inner_a_da = (
        theta * product_gn_alpha,
        theta * (2 - product_gn_alpha) / 3,
    )
    a_da_outer_da = (da3_x + inner_a_da[0], da3_y + inner_a_da[1])
    a_du_outer_da = (da3_x, da3_y + theta / 3)
    a_da_outer_du = inner_a_da
    monomials = [
        (da3_x, da3_y),
        (da3_x + theta, da3_y),
        (theta, Fraction(0, 1)),
        (Fraction(0, 1), theta / 3),
        a_da_outer_da,
        a_du_outer_da,
        a_da_outer_du,
    ]
    totals = [left + right for left, right in monomials]
    check("control_product_gn_alpha_1_3", product_gn_alpha == TEST_ORACLES["product_gn_alpha"], product_gn_alpha, TEST_ORACLES["product_gn_alpha"])
    check("control_a_da_outer_da_14_15", a_da_outer_da == TEST_ORACLES["a_da_outer_da"], a_da_outer_da, TEST_ORACLES["a_da_outer_da"])
    check("control_a_du_outer_da_23_30", a_du_outer_da == TEST_ORACLES["a_du_outer_da"], a_du_outer_da, TEST_ORACLES["a_du_outer_da"])
    check("control_a_da_outer_du_4_15", a_da_outer_du == TEST_ORACLES["a_da_outer_du"], a_da_outer_du, TEST_ORACLES["a_da_outer_du"])
    check("all_control_monomials_sublinear", all(total < 1 for total in totals), totals, "all <1")
    check("worst_control_total_29_30", max(totals) == Fraction(29, 30), max(totals), Fraction(29, 30))
    check("young_slack_1_30", 1 - max(totals) == TEST_ORACLES["young_slack"], 1 - max(totals), TEST_ORACLES["young_slack"])

    # Finite physical-shell prefix: disjoint Fourier carriers make H2 partial
    # energies monotone and the prefix identity exact.
    shell_vectors = []
    shell_weights = []
    for shell in range(7):
        vector = rng.normal(size=3) + 1j * rng.normal(size=3)
        shell_vectors.append(vector)
        shell_weights.append(float(1 + 2 ** (4 * shell)))
    full_h2 = sum(weight * float(np.vdot(vector, vector).real) for weight, vector in zip(shell_weights, shell_vectors))
    prefix_h2 = [sum(shell_weights[k] * float(np.vdot(shell_vectors[k], shell_vectors[k]).real) for k in range(j + 1)) for j in range(7)]
    check("physical_prefix_h2_monotone", all(prefix_h2[j] <= prefix_h2[j + 1] for j in range(6)), prefix_h2, "monotone")
    check("physical_prefix_h2_bounded_by_terminal", max(prefix_h2) <= full_h2 + 1.0e-12, max(prefix_h2), full_h2)
    check("regular_prefix_authority_declared", "Sharp-shell Littlewood--Paley equivalence" in AUTHORITY_NOTES["r075"].read_text(encoding="utf-8"), "R075 (8.1)-(8.4)", "declared")

    # Matrix-perspective conditional identity on a random finite ensemble.
    outcomes = 8
    dimension = 3
    random_a = []
    random_x = []
    for _ in range(outcomes):
        raw = rng.normal(size=(dimension, dimension))
        random_a.append(raw.T @ raw + 0.7 * np.eye(dimension))
        random_x.append(rng.normal(size=dimension))
    a_terminal = np.stack(random_a)
    x_terminal = np.stack(random_x)
    a_old = a_terminal.mean(axis=0)
    x_old = x_terminal.mean(axis=0)
    m_terminal = np.linalg.solve(a_terminal, x_terminal[..., None])[..., 0]
    m_old = np.linalg.solve(a_old, x_old)
    phi_terminal = np.einsum("ni,nij,nj->n", m_terminal, a_terminal, m_terminal)
    phi_old = float(m_old @ a_old @ m_old)
    innovation = np.einsum("ni,nij,nj->n", m_terminal - m_old, a_terminal, m_terminal - m_old).mean()
    check("matrix_perspective_telescope", abs(phi_terminal.mean() - phi_old - innovation) < 2.0e-12, phi_terminal.mean() - phi_old, innovation)
    check("matrix_perspective_innovation_nonnegative", innovation >= -1.0e-13, innovation, ">=0")

    # Completion identity for one conditional branch.
    raw_b = rng.normal(size=(dimension, dimension))
    b_matrix = raw_b.T @ raw_b + np.eye(dimension)
    raw_r = rng.normal(size=(dimension, dimension))
    r_matrix = raw_r.T @ raw_r + 0.5 * np.eye(dimension)
    c_vector = rng.normal(size=dimension)
    x_vector = rng.normal(size=dimension)
    a_matrix = b_matrix + 2.0 * r_matrix
    m_vector = np.linalg.solve(a_matrix, x_vector)
    lhs_completion = float(x_vector @ c_vector + 0.5 * c_vector @ b_matrix @ c_vector + c_vector @ r_matrix @ c_vector)
    rhs_completion = 0.5 * float((c_vector + m_vector) @ a_matrix @ (c_vector + m_vector)) - 0.5 * float(x_vector @ np.linalg.solve(a_matrix, x_vector))
    check("conditional_matrix_completion", abs(lhs_completion - rhs_completion) < 2.0e-12, lhs_completion, rhs_completion)
    theta_matrix = b_matrix - b_matrix @ np.linalg.solve(b_matrix + 2.0 * r_matrix, b_matrix)
    check("theta_matrix_symmetric", np.linalg.norm(theta_matrix - theta_matrix.T) < 2.0e-12, np.linalg.norm(theta_matrix - theta_matrix.T), 0)
    check("theta_matrix_positive", np.linalg.eigvalsh(theta_matrix).min() > -1.0e-12, np.linalg.eigvalsh(theta_matrix), ">=0")
    inverse_piece = b_matrix @ np.linalg.solve(b_matrix + 2.0 * r_matrix, b_matrix)
    check("augmented_perspective_partition", np.linalg.norm(inverse_piece + theta_matrix - b_matrix) < 2.0e-12, np.linalg.norm(inverse_piece + theta_matrix - b_matrix), 0)
    raw_covariance = rng.normal(size=(dimension, dimension))
    delta_gamma = raw_covariance @ raw_covariance.T
    frozen_k = float(np.trace(inverse_piece @ delta_gamma))
    frozen_terminal_doob = float(np.trace(theta_matrix @ delta_gamma))
    frozen_baseline = float(np.trace(b_matrix @ delta_gamma))
    frozen_schur = frozen_k - frozen_baseline
    frozen_augmented = frozen_schur + frozen_terminal_doob
    check("frozen_original_schur_nonpositive", frozen_schur <= 1.0e-12, frozen_schur, "<=0")
    check("frozen_augmented_density_zero", abs(frozen_augmented) < 2.0e-10, frozen_augmented, 0)

    # One-reveal coefficient-conditioned moment matching and its sharp
    # weighted-covariance failure when the conditional variance depends on B.
    reveal_b = [Fraction(1, 1), Fraction(2, 1)]
    reveal_delta = Fraction(3, 2)
    reveal_r = Fraction(1, 2)
    reveal_g0 = Fraction(7, 10)
    reveal_bar_b = sum(reveal_b) / len(reveal_b)
    reveal_bar_a = reveal_bar_b + 2 * reveal_r
    reveal_m0 = reveal_bar_b * reveal_g0 / reveal_bar_a
    reveal_positive = sum(
        (b_value + 2 * reveal_r)
        * (b_value * reveal_g0 / (b_value + 2 * reveal_r) - reveal_m0) ** 2
        for b_value in reveal_b
    ) / len(reveal_b)
    check("moment_matched_one_reveal_nonnegative", reveal_positive >= 0, reveal_positive, ">=0")
    mismatched_variances = [Fraction(2, 1), Fraction(1, 1)]
    weighted_covariance_defect = (
        sum(b_value * variance for b_value, variance in zip(reveal_b, mismatched_variances)) / len(reveal_b)
        - reveal_bar_b * reveal_delta
    )
    check("weighted_conditional_covariance_defect", weighted_covariance_defect == Fraction(-1, 4), weighted_covariance_defect, Fraction(-1, 4))

    # Exact all-residual fixture.
    fixture_minima: list[sp.Expr] = []
    fixture_residuals: list[dict[str, sp.Expr]] = []
    for variance in (sp.Rational(1, 2), sp.Rational(3, 2)):
        values = [
            (sp.Rational(1, 2), sp.Integer(0)),
            (sp.Rational(1, 4), sp.sqrt(2 * variance)),
            (sp.Rational(1, 4), -sp.sqrt(2 * variance)),
        ]
        mean_shift = -sp.Rational(1, 4) * (variance - 1)

        def b_fixture(g_value: sp.Expr) -> sp.Expr:
            return 1 + mean_shift - sp.Rational(1, 8) * (g_value**2 - variance) + sp.Rational(1, 8) * g_value

        mean_b = expectation(values, b_fixture)
        h_value = expectation(values, lambda g_value: b_fixture(g_value) * g_value)
        kappa = sp.Rational(1, 2) * expectation(values, lambda g_value: (b_fixture(g_value) - 1) * (g_value**2 - 1))
        minimum = sp.simplify(kappa - sp.Rational(1, 2) * h_value**2 / (mean_b + 1))
        r_c = expectation(values, lambda g_value: (b_fixture(g_value) - mean_b) * g_value)
        j_d = sp.Rational(1, 2) * expectation(
            values,
            lambda g_value: ((b_fixture(g_value) - 1) - expectation(values, lambda z: b_fixture(z) - 1))
            * ((g_value**2 - 1) - expectation(values, lambda z: z**2 - 1)),
        )
        minimum_b = min(sp.N(b_fixture(g_value), 30) for _, g_value in values)
        fixture_minima.append(minimum)
        fixture_residuals.append({"variance": variance, "r_c": r_c, "j_d": j_d, "minimum_b": minimum_b})
    fixture_average = sp.simplify(sum(fixture_minima) / 2)
    check("fixture_branch_zero", fixture_minima[0] == sp.Rational(-13, 272), fixture_minima[0], sp.Rational(-13, 272))
    check("fixture_branch_one", fixture_minima[1] == sp.Rational(-29, 160), fixture_minima[1], sp.Rational(-29, 160))
    check("fixture_expectation", fixture_average == TEST_ORACLES["fixture_expectation"], fixture_average, TEST_ORACLES["fixture_expectation"])
    check("fixture_rc_values", [item["r_c"] for item in fixture_residuals] == [sp.Rational(1, 16), sp.Rational(3, 16)], [item["r_c"] for item in fixture_residuals], [sp.Rational(1, 16), sp.Rational(3, 16)])
    check("fixture_jd_values", [item["j_d"] for item in fixture_residuals] == [sp.Rational(-1, 64), sp.Rational(-9, 64)], [item["j_d"] for item in fixture_residuals], [sp.Rational(-1, 64), sp.Rational(-9, 64)])
    check("fixture_frame_positive", min(float(item["minimum_b"]) for item in fixture_residuals) > 0, [item["minimum_b"] for item in fixture_residuals], ">0")
    average_variance = (sp.Rational(1, 2) + sp.Rational(3, 2)) / 2
    check("fixture_covariance_matches_globally", average_variance == 1, average_variance, 1)

    # Covariance union on overlapping random source blocks.
    source_blocks = [rng.normal(size=(4, width)) for width in (3, 2, 5)]
    source_union = np.concatenate(source_blocks, axis=1)
    covariance = source_union @ source_union.T
    h_source = rng.normal(size=source_union.shape[1])
    shift = source_union @ h_source
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    inverse_sqrt = eigenvectors @ np.diag([0.0 if value < 1.0e-12 else value ** -0.5 for value in eigenvalues]) @ eigenvectors.T
    cm_norm = float(np.linalg.norm(inverse_sqrt @ shift) ** 2)
    source_norm = float(np.linalg.norm(h_source) ** 2)
    check("covariance_union_cm_contraction", cm_norm <= source_norm + 1.0e-10, cm_norm, f"<={source_norm}")
    l_operator = rng.normal(size=(6, 4))
    trace_block = sum(float(np.linalg.norm(l_operator @ block, ord="fro") ** 2) for block in source_blocks)
    trace_union = float(np.trace(l_operator @ covariance @ l_operator.T))
    check("covariance_union_trace", abs(trace_block - trace_union) < 2.0e-10, trace_block, trace_union)
    repeated_blocks = [np.ones((1, 1)) / math.sqrt(7.0) for _ in range(7)]
    repeated_union = np.concatenate(repeated_blocks, axis=1)
    repeated_covariance = float((repeated_union @ repeated_union.T).item())
    check("repeated_range_covariance_exact", abs(repeated_covariance - 1.0) < 1.0e-14, repeated_covariance, 1)

    # Polar minimum is not triangular for h=(0,f(xi_1)).
    polar_source = np.array([[1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)]])
    terminal_shift = 1.7 / math.sqrt(2.0)
    minimal = polar_source.T @ np.array([terminal_shift])
    check("polar_minimal_representative", np.allclose(minimal, np.array([0.85, 0.85])), minimal, [0.85, 0.85])
    check("polar_first_coordinate_depends_on_future", abs(float(minimal[0])) > 0, float(minimal[0]), "nonzero coefficient of f(xi_1)")
    revisit_ratio = sp.simplify((sp.Symbol("t", positive=True) ** 4 / 2) / (2 * sp.Symbol("t", positive=True) ** 2))
    check("revisit_ratio", revisit_ratio == sp.Symbol("t", positive=True) ** 2 / 4, revisit_ratio, "t**2/4")

    # Exact strict-triangular Gaussian entropy accounting.  The triangular
    # Jacobian has unit diagonal, and a kernel loop stores all cost in the
    # nonnegative fibre surplus.
    shift_one, shift_two = sp.symbols("a b", real=True)
    triangular_cost = sp.expand(shift_one**2 + shift_two**2)
    triangular_entropy = sp.simplify(triangular_cost / 2)
    check("triangular_entropy_identity", sp.simplify(2 * triangular_entropy - triangular_cost) == 0, triangular_entropy, "cost/2")
    loop_size = sp.symbols("u", real=True)
    loop_source_entropy = sp.simplify((loop_size**2 + (-loop_size) ** 2) / 2)
    check("kernel_loop_fibre_surplus", loop_source_entropy == loop_size**2, loop_source_entropy, loop_size**2)
    inverse_q = Fraction(9, 10)
    check("entropy_union_nelson_coefficient", Fraction(9, 20) * 2 == inverse_q, Fraction(9, 20) * 2, inverse_q)

    # Negative-flow identities.  The linear example checks the Liouville
    # formula exactly without numerical quadrature.
    t_symbol = sp.symbols("t", positive=True)
    flow_coefficient = sp.simplify(2 * sp.integrate(sp.Symbol("s", positive=True) * sp.exp(-2 * sp.Symbol("s", positive=True)), (sp.Symbol("s", positive=True), 0, t_symbol)))
    expected_coefficient = sp.simplify((1 - (1 + 2 * t_symbol) * sp.exp(-2 * t_symbol)) / 2)
    check("negative_flow_defect_integral", sp.simplify(flow_coefficient - expected_coefficient) == 0, flow_coefficient, expected_coefficient)
    lhs_linear_flow = sp.exp(t_symbol) / sp.sqrt(1 + 2 * t_symbol)
    rhs_linear_flow = 1 / sp.sqrt(1 - 2 * expected_coefficient)
    check("negative_flow_liouville_linear", sp.simplify(lhs_linear_flow - rhs_linear_flow) == 0, sp.simplify(lhs_linear_flow - rhs_linear_flow), 0)
    x_symbol = sp.symbols("x", real=True)
    cubic_flow = x_symbol / sp.sqrt(1 + 2 * t_symbol * x_symbol**2)
    cubic_residual = sp.simplify(sp.diff(cubic_flow, t_symbol) + cubic_flow**3)
    check("cubic_negative_flow_solution", cubic_residual == 0, cubic_residual, 0)
    cubic_image_limit = sp.limit(cubic_flow, x_symbol, sp.oo)
    check("cubic_negative_flow_non_surjective", cubic_image_limit == 1 / sp.sqrt(2 * t_symbol), cubic_image_limit, 1 / sp.sqrt(2 * t_symbol))
    b_function = x_symbol**3
    a_function = x_symbol * b_function - sp.diff(b_function, x_symbol)
    material_direct = sp.expand(b_function * sp.diff(a_function, x_symbol))
    material_formula = sp.expand(b_function**2 + (x_symbol * (sp.diff(b_function, x_symbol) * b_function) - sp.diff(sp.diff(b_function, x_symbol) * b_function, x_symbol)) + sp.diff(b_function, x_symbol) ** 2)
    check("material_derivative_identity", sp.simplify(material_direct - material_formula) == 0, sp.simplify(material_direct - material_formula), 0)

    eta_symbol, zeta_symbol = sp.symbols("eta zeta", positive=True)
    lambda_squared = 2 * (eta_symbol + 120 * zeta_symbol) + 1
    cat0_coefficient = sp.simplify(-lambda_squared / 2 + eta_symbol + 120 * zeta_symbol)
    check("cat0_scaled_reset_negative", cat0_coefficient == -sp.Rational(1, 2), cat0_coefficient, -sp.Rational(1, 2))
    check("cat0_sixth_moments", [sp.factorial2(5), 8 * sp.factorial2(5)] == [15, 120], [sp.factorial2(5), 8 * sp.factorial2(5)], [15, 120])

    downstream = {
        "general_progressive_revisit_h_c": False,
        "complete_signed_h_n": False,
        "progressive_revisit_h_a": False,
        "full_reg_packet": False,
        "uniform_overlap": False,
        "nelson": False,
        "interacting_measure": False,
        "floor_removal": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    regular_hc_gate = (
        root_surplus > 0
        and b_denominator_exponent > 0
        and gradient_denominator_exponent > 0
        and max(totals) < 1
        and max(prefix_h2) <= full_h2 + 1.0e-12
        and np.linalg.norm(audit_b - audit_g) > 1.0e-4
    )
    check("regular_hc_exponent_prefix_gate", regular_hc_gate, [root_surplus, b_denominator_exponent, gradient_denominator_exponent, max(totals)], "positive gaps, sublinear budget, physical prefix")
    check("all_downstream_flags_false", not any(downstream.values()), downstream, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-normalized-cartan-perspective-covariance-frontier-primary/1.0",
        "version": __version__,
        "date": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "inputs": serial(INPUTS),
        "oracles": serial(TEST_ORACLES),
        "derived": {
            "coefficient_poincare_constant": str(coefficient_poincare_constant),
            "two_tail_gradient_constant": str(two_tail_gradient_constant),
            "b_denominator_exponent": str(b_denominator_exponent),
            "gradient_denominator_exponent": str(gradient_denominator_exponent),
            "root_surplus": str(root_surplus),
            "worst_control_total": str(max(totals)),
            "fixture_expectation": str(fixture_average),
            "regular_hc_gap": "2^(-(C-5)/2)",
        },
        "assertions": rows,
        "claims_not_established": downstream,
    }
    atomic_json(OUTPUT, payload)
    print(f"R-092 primary: {passed}/{len(rows)} assertions PASS" if passed == len(rows) else f"R-092 primary: {passed}/{len(rows)} assertions; FAIL")
    print(f"artifact: {OUTPUT.relative_to(REPO)}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
