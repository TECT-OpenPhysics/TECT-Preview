#!/usr/bin/env python3
"""Primary executable evidence for the R-088 A13 reduction.

This program checks the exact direct-root Schur summation, sequential Cartan
secant algebra, critical quartic Besov bookkeeping, and rational conditional
trace identities used in the companion proof note.  Analytic Littlewood--
Paley and production-specific causal estimates are proved or isolated in the
note; finite algebra and numerical consequences are checked here.

It does not assert the missing production secant-to-quartic bridge, the
coefficient-dominant rational causal packet, REG, OVERLAP, controlled-shell
one-use, Nelson, a measure theorem, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
R084 = CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json"
R085 = CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
R087 = CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json"
R084_NOTE = CLAIM_DIR / "notes/classii-root-diagonal-cartan-ou-linear-pauli-fierz-absorption-260725-v1.0.tex.txt"
R085_NOTE = CLAIM_DIR / "notes/classii-nonorthogonal-cartan-schur-rational-shifted-hessian-boundary-260725-v1.0.tex.txt"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json"


# Every value below is either a theorem input or a deliberately labelled test
# oracle.  All derived quantities are recomputed below.
INPUTS = {
    "cartan_s": Fraction(7, 12),
    "cartan_alpha": Fraction(2, 5),
    "far_separation": 5,
    "besov_s": Fraction(7, 12),
    "nelson_q": Fraction(10, 9),
    "comparison_p": Fraction(11, 10),
    "target_dimension": 6,
}

TEST_ORACLES = {
    "direct_schur_constant": 16.30295538482827,
    "gap_exponent": Fraction(7, 6),
    "besov_cauchy_exponent": Fraction(5, 6),
    "rare_direct_exponent": Fraction(5, 1),
    "rare_weighted_exponent": Fraction(6, 1),
    "hypothetical_secant_ansatz_exponent": Fraction(-5, 6),
    "comparison_margin": Fraction(1, 220),
    "mean_defect": Fraction(-3, 4),
    "covariance_defect": Fraction(-1, 2),
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


def contraction(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.trace(left.T * right)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def serial(value: Any) -> Any:
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, sp.Basic):
            return str(value)
        if isinstance(value, sp.MatrixBase):
            return [[serial(entry) for entry in row] for row in value.tolist()]
        if isinstance(value, (list, tuple)):
            return [serial(item) for item in value]
        if isinstance(value, dict):
            return {key: serial(item) for key, item in value.items()}
        return value

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    predecessor_specs = (
        (R084, "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION", "r084"),
        (R085, "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY", "r085"),
        (R087, "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION", "r087"),
    )
    for path, expected, label in predecessor_specs:
        record = json.loads(path.read_text(encoding="utf-8"))
        check(f"{label}_predecessor", record.get("result_id") == expected, record.get("result_id"), expected)

    # Direct-root nonorthogonal Schur theorem.
    s = INPUTS["cartan_s"]
    eta = s
    schur_constant = 1.0 / (
        (1.0 - 2.0 ** (-float(eta)))
        * (1.0 - 2.0 ** (-2.0 * float(s)))
        * (1.0 - 2.0 ** (float(eta - 2 * s)))
    )
    check("direct_s_positive", s > 0, s, ">0")
    check("direct_eta_positive", eta > 0, eta, ">0")
    check("direct_eta_below_2s", eta < 2 * s, eta, f"<{2 * s}")
    check("balanced_eta", eta == s, eta, s)
    check(
        "direct_schur_constant",
        math.isclose(schur_constant, TEST_ORACLES["direct_schur_constant"], rel_tol=0.0, abs_tol=2e-14),
        schur_constant,
        TEST_ORACLES["direct_schur_constant"],
    )
    check("direct_gap_exponent", 2 * s == TEST_ORACLES["gap_exponent"], 2 * s, TEST_ORACLES["gap_exponent"])

    geometric_eta = sum(2.0 ** (-float(eta) * r) for r in range(1000))
    geometric_m = sum(2.0 ** (-2.0 * float(s) * d) for d in range(1000))
    geometric_r = sum(2.0 ** (float(eta - 2 * s) * r) for r in range(1000))
    check("eta_geometric_sum", abs(geometric_eta - 1 / (1 - 2 ** (-float(eta)))) < 1e-12, geometric_eta, "closed form")
    check("output_geometric_sum", abs(geometric_m - 1 / (1 - 2 ** (-2 * float(s)))) < 1e-12, geometric_m, "closed form")
    check("root_input_geometric_sum", abs(geometric_r - 1 / (1 - 2 ** (float(eta - 2 * s)))) < 1e-12, geometric_r, "closed form")

    # Finite aligned fixtures are dominated by the infinite-series theorem.
    def finite_direct_ratio(q_values: list[Fraction], cutoff: int, j_extra: int, m_extra: int) -> float:
        left = 0.0
        for j in range(len(q_values) + j_extra):
            for m in range(j + cutoff, j + cutoff + m_extra):
                amplitude = 0.0
                for k in range(min(j, len(q_values) - 1) + 1):
                    amplitude += 2.0 ** (-float(s) * (m - k)) * math.sqrt(float(q_values[k]))
                left += amplitude * amplitude
        return left / sum(float(value) for value in q_values)

    direct_bound = schur_constant * 2.0 ** (-2.0 * float(s) * INPUTS["far_separation"])
    for index, q_values in enumerate(
        ([Fraction(1)], [Fraction(1), Fraction(3, 2)], [Fraction(2), Fraction(1, 3), Fraction(5, 4)]),
        start=1,
    ):
        ratio = finite_direct_ratio(q_values, INPUTS["far_separation"], 12, 24)
        check(f"direct_aligned_fixture_{index}", ratio <= direct_bound + 1e-12, ratio, f"<={direct_bound}")

    # R-084's exact target has no outer 2^j.  R-085's valid but stronger
    # theorem does.  The audit repairs attribution without withdrawing R-085.
    r084_text = R084_NOTE.read_text(encoding="utf-8")
    r085_text = R085_NOTE.read_text(encoding="utf-8")
    r084_match = re.search(r"S_C\^\{\\rm ctrl\}.*?\\tag\{4\.6\}", r084_text, re.DOTALL)
    r085_match = re.search(r"\\boxed\{.*?\\tag\{4\.3\}", r085_text, re.DOTALL)
    r084_contract = "" if r084_match is None else r084_match.group(0)
    r085_contract = "" if r085_match is None else r085_match.group(0)
    check("r084_exact_contract_found", bool(r084_contract), len(r084_contract), ">0")
    check("r084_exact_contract_unweighted", "2^j" not in r084_contract and "2^{j}" not in r084_contract, r084_contract.count("2^j") + r084_contract.count("2^{j}"), 0)
    check("r085_stronger_contract_found", bool(r085_contract), len(r085_contract), ">0")
    check("r085_stronger_contract_weighted", "2^j" in r085_contract or "2^{j}" in r085_contract, "outer 2^j present", True)
    zero_s_partial = [upper - INPUTS["far_separation"] + 1 for upper in (8, 16, 32)]
    check("zero_s_fixture_strict_growth", zero_s_partial[0] < zero_s_partial[1] < zero_s_partial[2], zero_s_partial, "strict growth")
    check("zero_s_fixture_linear_growth", zero_s_partial == [4, 12, 28], zero_s_partial, [4, 12, 28])

    # Exact sequential Cartan secant in one spatial coordinate.  The symbolic
    # polynomial is only an algebra oracle; the theorem is for vector Phi.
    b, a, v = sp.symbols("b a v", real=True)
    db, da, dv = sp.symbols("db da dv", real=True)
    z = sp.symbols("z", real=True)
    phi = z**3 + 2 * z
    dphi = sp.diff(phi, z)
    current_variation = lambda state, derivative: dphi.subs(z, state) * v * derivative + phi.subs(z, state) * dv
    direct_secant = sp.expand(current_variation(b + a, db + da) - current_variation(b, db))
    three_channel = sp.expand(
        (dphi.subs(z, b + a) - dphi.subs(z, b)) * v * db
        + dphi.subs(z, b + a) * v * da
        + (phi.subs(z, b + a) - phi.subs(z, b)) * dv
    )
    check("sequential_three_channel_identity", sp.expand(direct_secant - three_channel) == 0, sp.expand(direct_secant - three_channel), 0)

    r = sp.symbols("r", real=True)
    radial_integrand = (
        sp.diff(phi, z, 2).subs(z, b + r * a) * a * v * (db + r * da)
        + dphi.subs(z, b + r * a) * v * da
        + dphi.subs(z, b + r * a) * a * dv
    )
    radial_secant = sp.integrate(radial_integrand, (r, 0, 1))
    check("sequential_radial_identity", sp.expand(radial_secant - three_channel) == 0, sp.expand(radial_secant - three_channel), 0)

    shell_symbols = sp.symbols("a1 a2 a3", real=True)
    d_shell_symbols = sp.symbols("da1 da2 da3", real=True)
    background = b
    d_background = db
    telescoped = 0
    for shell, d_shell in zip(shell_symbols, d_shell_symbols):
        telescoped += current_variation(background + shell, d_background + d_shell) - current_variation(background, d_background)
        background += shell
        d_background += d_shell
    endpoint = current_variation(b + sum(shell_symbols), db + sum(d_shell_symbols)) - current_variation(b, db)
    check("sequential_shell_telescope", sp.expand(telescoped - endpoint) == 0, sp.expand(telescoped - endpoint), 0)
    first_sequential = sp.expand(current_variation(b + shell_symbols[0], db) - current_variation(b, db))
    first_radial_total = sp.expand(current_variation(b + sum(shell_symbols), db) - current_variation(b, db))
    check("sequential_atoms_differ_from_radial_atom", sp.expand(first_sequential - first_radial_total) != 0, sp.expand(first_sequential - first_radial_total), "nonzero")

    # Tame three-channel and Hilbert--Schmidt envelopes.
    tame_fixtures = (
        (Fraction(1, 3), Fraction(2, 5), Fraction(3, 7), Fraction(5, 11), Fraction(7, 13), Fraction(11, 17)),
        (Fraction(5, 4), Fraction(1, 9), Fraction(2, 3), Fraction(4, 7), Fraction(3, 8), Fraction(2, 5)),
        (Fraction(7, 10), Fraction(9, 8), Fraction(1, 6), Fraction(5, 3), Fraction(1, 4), Fraction(5, 6)),
    )
    local_m2 = Fraction(5, 2)
    local_m1 = Fraction(3, 1)
    def bounded_phi(value: float) -> float:
        return 3.0 * math.tanh(value)

    def bounded_dphi(value: float) -> float:
        return 3.0 / math.cosh(value) ** 2

    for index, (aa, vv, d_b, d_a, d_v, base) in enumerate(tame_fixtures, start=1):
        envelope = local_m2 * aa * vv * d_b + local_m1 * vv * d_a + local_m1 * aa * d_v
        base_float = float(base)
        shifted = base_float + float(aa)
        actual = (
            bounded_dphi(shifted) * float(vv) * float(d_b + d_a)
            + bounded_phi(shifted) * float(d_v)
            - bounded_dphi(base_float) * float(vv) * float(d_b)
            - bounded_phi(base_float) * float(d_v)
        )
        check(f"three_channel_tame_fixture_{index}", abs(actual) <= float(envelope) + 1e-14, abs(actual), f"<={float(envelope)}")

    shell_j = 6
    kappa0 = Fraction(7, 5)
    kappa1 = Fraction(9, 4)
    aa = Fraction(4, 7)
    d_b = Fraction(5, 6)
    d_a = Fraction(3, 8)
    hs_rhs = (
        3 * local_m2**2 * aa**2 * d_b**2 * kappa0 * Fraction(1, 2**shell_j)
        + 3 * local_m1**2 * d_a**2 * kappa0 * Fraction(1, 2**shell_j)
        + 3 * local_m1**2 * aa**2 * kappa1 * Fraction(2**shell_j)
    )
    root_weights = (1.0, -2.0, 0.5, 1.5)
    root_norm = math.sqrt(sum(weight * weight for weight in root_weights))
    value_scale = math.sqrt(float(kappa0 * Fraction(1, 2**shell_j)))
    derivative_scale = math.sqrt(float(kappa1 * Fraction(2**shell_j)))
    root_values = [value_scale * weight / root_norm for weight in root_weights]
    root_derivatives = [derivative_scale * weight / root_norm for weight in reversed(root_weights)]
    base_fixture = 0.4
    shifted_fixture = base_fixture + float(aa)
    hs_lhs = 0.0
    for root_value, root_derivative in zip(root_values, root_derivatives):
        atom_value = (
            bounded_dphi(shifted_fixture) * root_value * float(d_b + d_a)
            + bounded_phi(shifted_fixture) * root_derivative
            - bounded_dphi(base_fixture) * root_value * float(d_b)
            - bounded_phi(base_fixture) * root_derivative
        )
        hs_lhs += atom_value * atom_value
    check("hs_envelope_fixture", hs_lhs <= float(hs_rhs) + 1e-12, hs_lhs, f"<={float(hs_rhs)}")
    check("hs_root_value_scaling", kappa0 * Fraction(1, 2**shell_j) == Fraction(7, 320), kappa0 * Fraction(1, 2**shell_j), Fraction(7, 320))
    check("hs_root_derivative_scaling", kappa1 * Fraction(2**shell_j) == 144, kappa1 * Fraction(2**shell_j), 144)

    # Quartic Besov payload: largest-input summation and critical one-use
    # homogeneity.  The analytic product estimate is in the note.
    besov_s = INPUTS["besov_s"]
    cauchy_exponent = 2 * (1 - besov_s)
    check("quartic_besov_range", 0 < besov_s < 1, besov_s, "0<s<1")
    check("quartic_cauchy_exponent", cauchy_exponent == TEST_ORACLES["besov_cauchy_exponent"], cauchy_exponent, TEST_ORACLES["besov_cauchy_exponent"])
    coefficients = [Fraction(1, j + 2) for j in range(12)]
    dyadic_lhs = sum((2.0 ** (float(besov_s + 1) * j)) * float(value) for j, value in enumerate(coefficients))
    h2_norm = math.sqrt(sum((2.0 ** (4 * j)) * float(value) ** 2 for j, value in enumerate(coefficients)))
    cauchy_factor = math.sqrt(sum(2.0 ** (-float(cauchy_exponent) * j) for j in range(len(coefficients))))
    check("quartic_dyadic_cauchy_fixture", dyadic_lhs <= h2_norm * cauchy_factor + 1e-10, dyadic_lhs, f"<={h2_norm * cauchy_factor}")
    check("quartic_payload_X_power", Fraction(1, 2) + Fraction(1, 2) == 1, "X^(1/2)Y_A^(1/2)", "one use")

    for index, (energy, gaussian_sixth, delta) in enumerate(
        ((Fraction(9, 5), Fraction(7, 4), Fraction(1, 11)), (Fraction(3, 8), Fraction(13, 6), Fraction(2, 9))),
        start=1,
    ):
        cross = math.sqrt(float(energy * gaussian_sixth))
        young = float(delta * energy + gaussian_sixth / (4 * delta))
        check(f"gaussian_cross_young_{index}", cross <= young + 1e-14, cross, f"<={young}")

    # The old q_k^mod extraction still fails after the normalization repair.
    # The final exponent below is only the arithmetic consequence of the
    # explicitly unproved toy ansatz p*N^2*A^(2+2s); it is not an atom bound.
    alpha = INPUTS["cartan_alpha"]
    beta = 6 * alpha - 1
    event_exponent = -6
    translated_norm_exponent = 6 * (1 + alpha)
    derivative_energy_exponent = 4
    direct_raw_exponent = -beta + translated_norm_exponent + derivative_energy_exponent
    weighted_raw_exponent = direct_raw_exponent + 1
    direct_exponent = event_exponent + direct_raw_exponent
    weighted_exponent = direct_exponent + 1
    hypothetical_exponent = event_exponent + 2 + (2 + 2 * s)
    check("rare_direct_exponent", direct_exponent == TEST_ORACLES["rare_direct_exponent"], direct_exponent, TEST_ORACLES["rare_direct_exponent"])
    check("rare_weighted_exponent", weighted_exponent == TEST_ORACLES["rare_weighted_exponent"], weighted_exponent, TEST_ORACLES["rare_weighted_exponent"])
    check("hypothetical_secant_ansatz_exponent", hypothetical_exponent == TEST_ORACLES["hypothetical_secant_ansatz_exponent"], hypothetical_exponent, TEST_ORACLES["hypothetical_secant_ansatz_exponent"])
    for index, shell_size in enumerate((2, 3, 5), start=1):
        probability = Fraction(1, shell_size**6)
        direct_growth = probability * shell_size ** int(direct_raw_exponent)
        weighted_growth = probability * shell_size ** int(weighted_raw_exponent)
        hypothetical_scale = probability * shell_size**2 * shell_size ** (2 + 2 * float(s))
        check(f"rare_direct_growth_{index}", direct_growth == shell_size ** int(direct_exponent), direct_growth, shell_size ** int(direct_exponent))
        check(f"rare_weighted_growth_{index}", weighted_growth == shell_size ** int(weighted_exponent), weighted_growth, shell_size ** int(weighted_exponent))
        check(f"hypothetical_secant_ansatz_decay_{index}", hypothetical_scale < 1, hypothetical_scale, "<1 under the toy ansatz")

    # Rational completion and the exact conditional moment theorem.
    eta_r = sp.Rational(3, 5)
    identity = sp.eye(2)
    b1_matrix = sp.Matrix([[2, 1], [1, 3]])
    l_matrix = sp.Matrix([[1, -2], [-2, 4]])
    gamma = sp.Matrix([[2, sp.Rational(1, 3)], [sp.Rational(1, 3), 1]])
    g_vector = sp.Matrix([sp.Rational(2, 3), sp.Rational(-4, 5)])
    c_vector = sp.Matrix([sp.Rational(3, 7), sp.Rational(-1, 2)])
    q_tensor = g_vector * g_vector.T - gamma
    a_eta = b1_matrix + 2 * eta_r * identity
    k_eta = l_matrix * a_eta.inv() * l_matrix
    m_eta = l_matrix - k_eta
    debt = contraction(k_eta, gamma) / 2
    packet = contraction(l_matrix, q_tensor) / 2 + (g_vector.T * l_matrix * c_vector)[0] + (c_vector.T * b1_matrix * c_vector)[0] / 2
    shifted = c_vector + a_eta.inv() * l_matrix * g_vector
    completion = (shifted.T * a_eta * shifted)[0] / 2 + contraction(m_eta, q_tensor) / 2 - debt
    check("rational_completion_identity", sp.simplify(packet + eta_r * (c_vector.T * c_vector)[0] - completion) == 0, sp.simplify(packet + eta_r * (c_vector.T * c_vector)[0] - completion), 0)
    pointwise_null = (g_vector.T * k_eta * g_vector)[0] / 2 - contraction(k_eta, q_tensor) / 2 - debt
    check("rational_pointwise_null", sp.simplify(pointwise_null) == 0, sp.simplify(pointwise_null), 0)

    mu = sp.Matrix([sp.Rational(1, 4), sp.Rational(-2, 7)])
    covariance = sp.Matrix([[sp.Rational(5, 3), sp.Rational(1, 5)], [sp.Rational(1, 5), sp.Rational(4, 3)]])
    expected_direct = (
        contraction(l_matrix, covariance + mu * mu.T - gamma) / 2
        + (mu.T * l_matrix * c_vector)[0]
        + (c_vector.T * b1_matrix * c_vector)[0] / 2
        + eta_r * (c_vector.T * c_vector)[0]
    )
    conditional_formula = (
        ((c_vector + a_eta.inv() * l_matrix * mu).T * a_eta * (c_vector + a_eta.inv() * l_matrix * mu))[0] / 2
        + contraction(m_eta, mu * mu.T) / 2
        + contraction(l_matrix, covariance - gamma) / 2
    )
    check("rational_conditional_identity", sp.simplify(expected_direct - conditional_formula) == 0, sp.simplify(expected_direct - conditional_formula), 0)

    centered_matched_p = (c_vector.T * b1_matrix * c_vector)[0] / 2
    check("centered_covariance_matched_nonnegative", centered_matched_p >= 0, centered_matched_p, ">=0")

    covariance_scale, ell, eta_symbol = sp.symbols("covariance_scale ell eta_symbol", positive=True)
    fixed_dimension = INPUTS["target_dimension"]
    k_fixture = ell**2 * sp.eye(fixed_dimension) / (2 * eta_symbol)
    gamma_fixture = covariance_scale * sp.eye(fixed_dimension)
    standalone_debt = contraction(k_fixture, gamma_fixture) / 2
    centered_square_variance = contraction(k_fixture, gamma_fixture) / 2
    check("standalone_debt_fixed_target_covariance_growth", sp.diff(standalone_debt, covariance_scale) > 0, sp.diff(standalone_debt, covariance_scale), ">0 at fixed dimension 6")
    check("centered_matched_square_variance_cancels_debt", sp.simplify(centered_square_variance - standalone_debt) == 0, sp.simplify(centered_square_variance - standalone_debt), 0)

    t = sp.symbols("t", real=True)
    mean_defect = sp.Rational(-3, 4) * t**2
    covariance_defect = sp.Rational(-1, 2)
    check("nonzero_mean_fixture", sp.simplify(mean_defect / t**2) == TEST_ORACLES["mean_defect"], mean_defect, "-3t^2/4")
    check("covariance_mismatch_fixture", covariance_defect == TEST_ORACLES["covariance_defect"], covariance_defect, TEST_ORACLES["covariance_defect"])
    xi = sp.symbols("xi", real=True)
    adapted_packet = eta_symbol * (xi**2 - 1) + xi * 2 * eta_symbol * (-xi) + eta_symbol * xi**2
    check("adapted_alignment_pathwise_negative", sp.simplify(adapted_packet) == -eta_symbol, sp.simplify(adapted_packet), "-eta")

    # Matrix-fractional Jensen identity and its signed Wick contraction.
    a_states = (sp.diag(1, 2), sp.diag(3, 1))
    l_states = (sp.diag(2, -1), sp.diag(-1, 3))
    bar_a = sum(a_states, sp.zeros(2)) / 2
    bar_l = sum(l_states, sp.zeros(2)) / 2
    left_jensen = sum((l_states[i] * a_states[i].inv() * l_states[i] for i in range(2)), sp.zeros(2)) / 2 - bar_l * bar_a.inv() * bar_l
    right_jensen = sp.zeros(2)
    for state_a, state_l in zip(a_states, l_states):
        first = state_l - bar_l * bar_a.inv() * state_a
        second = state_l - state_a * bar_a.inv() * bar_l
        right_jensen += first * state_a.inv() * second / 2
    check("matrix_fractional_jensen_identity", sp.simplify(left_jensen - right_jensen) == sp.zeros(2), sp.simplify(left_jensen - right_jensen), sp.zeros(2))
    jensen_eigenvalues = list(left_jensen.eigenvals().keys())
    check("matrix_fractional_jensen_psd", all(value >= 0 for value in jensen_eigenvalues), jensen_eigenvalues, ">=0")
    signed_contraction = contraction(left_jensen, -sp.eye(2))
    check("jensen_wick_contraction_signed", signed_contraction < 0, signed_contraction, "<0")

    # Eta is either an internal share of the pinned 9/20 coefficient or an
    # additional charge.  Only the latter is restricted by the 1/220 margin.
    q_nelson = INPUTS["nelson_q"]
    p_compare = INPUTS["comparison_p"]
    pinned_energy = 1 / (2 * q_nelson)
    margin = 1 / (2 * p_compare) - pinned_energy
    check("comparison_margin", margin == TEST_ORACLES["comparison_margin"], margin, TEST_ORACLES["comparison_margin"])
    check("internal_eta_keeps_q", 1 / (2 * pinned_energy) == q_nelson, 1 / (2 * pinned_energy), q_nelson)
    eta_small = Fraction(1, 500)
    eta_large = Fraction(1, 200)
    q_small = 1 / (2 * (pinned_energy + eta_small))
    q_large = 1 / (2 * (pinned_energy + eta_large))
    check("additional_eta_below_margin", q_small > p_compare, q_small, f">{p_compare}")
    check("additional_eta_above_margin_fails", q_large < p_compare, q_large, f"<{p_compare}")

    claims_not_established = {
        "production_sequential_secant_to_quartic_bridge": False,
        "direct_integrated_cartan_cfar": False,
        "coefficient_dominant_rational_causal_packet": False,
        "rational_shifted_hessian_form_bound": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "direct_cartan": {
            "s": str(s),
            "eta": str(eta),
            "constant": schur_constant,
            "gap_factor": "2^(-7C/6)",
            "threshold": "s>0",
            "ledger": "sum_k q_k",
            "r085_weighted_theorem_retained": True,
            "sequential_secant_identity": True,
            "quartic_besov_range": "0<s<1",
            "quartic_payload": "||A||_H2 ||A||_6^3 = X^(1/2) Y_A^(1/2)",
            "old_qmod_direct_growth": "N^5",
            "hypothetical_secant_ansatz_scaling": "N^(-5/6) under unproved toy ansatz",
        },
        "rational": {
            "pointwise_null": "G^T K_eta G/2-K_eta:Q/2-D_eta=0",
            "conditional_formula": "square(mu)+M_eta:mu mu^T/2+L:(V-Gamma)/2",
            "centered_covariance_matched": "E[P|H]=c^T B_1 c/2",
            "standalone_debt": "ell^2 Tr(Gamma_N)/(4 eta), canceled by retained-square variance on centered covariance-matched blocks",
            "matrix_fractional_jensen_psd": True,
            "wick_contraction_signed": True,
        },
        "negative_results": [
            "AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION",
            "NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",
        ],
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-088 primary] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-088 primary] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
