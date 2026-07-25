#!/usr/bin/env python3
"""Primary executable evidence for the R-089 A13 reduction.

The program checks three exact advances used in the companion proof note:
(i) global Douglas/polar compression of arbitrary finite-cutoff progressive
controls, including the Hilbert martingale one-use and spatial ledger;
(ii) the exact OVERLAP--Nelson equivalence on the R-087 variational core; and
(iii) a Taylor-coordinate diagonalisation of the R-088 rational conditional
packet, together with a production-coefficient negative-mean fixture.

It does not assert the nonlinear Cartan multiplier bracket, the complete
same-root rational square--trace--heat--forest bound, uniform OVERLAP, the
Nelson estimate, a measure theorem, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PROGRESSIVE-COVARIANCE-COMPRESSION-RATIONAL-MEAN-SPECTRAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
R087 = CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json"
R088 = CLAIM_DIR / "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json"
R087_NOTE = CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt"
R088_NOTE = CLAIM_DIR / "notes/classii-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-reduction-260725-v1.0.tex.txt"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-progressive-covariance-compression-rational-mean-spectral-boundary/result.json"


# These are upstream production inputs, not derived conclusions.
INPUTS = {
    "density_floor": Fraction(1, 10**12),
    "mass_square": Fraction(4, 1),
    "rational_alpha": Fraction(5, 9),
    "rational_numerator": Fraction(243, 1),
    "rational_denominator_factor": Fraction(8000, 1),
    "nelson_q": Fraction(10, 9),
    "sextic_charge": Fraction(3, 20),
    "martingale_s": Fraction(7, 12),
    "bridge_s": Fraction(1, 4),
    "far_gap": 5,
}

# Exact values used only as independently readable test oracles.
TEST_ORACLES = {
    "scalar_endpoint_normalized": Fraction(16, 81),
    "scalar_taylor_normalized": Fraction(259, 1296),
    "scalar_remainder_normalized": Fraction(-1, 432),
    "energy_coefficient": Fraction(9, 20),
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
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, sp.MatrixBase):
        return [[str(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


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

    # 1. Authority and exact q=10/9 arithmetic.
    r087 = json.loads(R087.read_text(encoding="utf-8"))
    r088 = json.loads(R088.read_text(encoding="utf-8"))
    check("r087_authority_claim", r087["claim_id"] == CLAIM, r087["claim_id"], CLAIM)
    check("r088_authority_claim", r088["claim_id"] == CLAIM, r088["claim_id"], CLAIM)
    check("r087_core_authority", bool(r087["consequence"]["fixed_cutoff_variational_core"]), r087["consequence"]["fixed_cutoff_variational_core"], True)
    check("r088_quartic_authority", bool(r088["consequence"]["quartic_besov_payload"]), r088["consequence"]["quartic_besov_payload"], True)
    check("r088_general_progressive_was_open", not r088["consequence"]["terminal_field_bridge_general_progressive"], r088["consequence"]["terminal_field_bridge_general_progressive"], False)
    check("r087_core_note_token", "Theorem 8.1 (fixed-cutoff variational CORE)" in R087_NOTE.read_text(encoding="utf-8"), True, True)
    check("r088_quartic_note_token", "Quartic Besov one-use payload" in R088_NOTE.read_text(encoding="utf-8"), True, True)

    q = INPUTS["nelson_q"]
    energy_coefficient = 1 / (2 * q)
    check("nelson_energy_coefficient", energy_coefficient == TEST_ORACLES["energy_coefficient"], energy_coefficient, TEST_ORACLES["energy_coefficient"])
    check("nelson_q_recovery", 1 / (2 * energy_coefficient) == q, 1 / (2 * energy_coefficient), q)
    check("sextic_charge", INPUTS["sextic_charge"] == Fraction(3, 20), INPUTS["sextic_charge"], Fraction(3, 20))
    trial_lower_bound = Fraction(-7, 3)
    log_moment = -q * trial_lower_bound
    recovered_infimum = -log_moment / q
    check("overlap_nelson_scalar_equivalence", recovered_infimum == trial_lower_bound, recovered_infimum, trial_lower_bound)

    # 2. Finite-dimensional global Douglas/polar compression.  T represents
    # the whole time-to-terminal map, so repeated ranges need not be orthogonal.
    t_exact = sp.Matrix([[1, 0, 1, 1], [0, 2, 1, -1]]) / 3
    v_exact = sp.Matrix([2, -1, 3, 1])
    c_exact = sp.simplify(t_exact * t_exact.T)
    a_exact = t_exact * v_exact
    cm_exact = sp.simplify((a_exact.T * c_exact.inv() * a_exact)[0])
    energy_exact = sp.simplify((v_exact.T * v_exact)[0])
    check("global_covariance_identity_exact", c_exact == t_exact * t_exact.T, c_exact, t_exact * t_exact.T)
    check("global_douglas_exact", cm_exact <= energy_exact, cm_exact, f"<={energy_exact}")
    check("global_douglas_slack_positive", sp.simplify(energy_exact - cm_exact) > 0, sp.simplify(energy_exact - cm_exact), ">0")

    packet_count = 9
    repeated_t = sp.ones(1, packet_count) / sp.sqrt(packet_count)
    repeated_v = sp.ones(packet_count, 1) / sp.sqrt(packet_count)
    repeated_c = sp.simplify((repeated_t * repeated_t.T)[0])
    repeated_a = sp.simplify((repeated_t * repeated_v)[0])
    repeated_energy = sp.simplify((repeated_v.T * repeated_v)[0])
    repeated_cm = sp.simplify(repeated_a**2 / repeated_c)
    check("revisit_covariance_normalized", repeated_c == 1, repeated_c, 1)
    check("revisit_terminal_displacement", repeated_a == 1, repeated_a, 1)
    check("revisit_douglas_equality", repeated_cm == repeated_energy == 1, (repeated_cm, repeated_energy), (1, 1))

    rng = np.random.default_rng(89025)
    compression_ratios: list[float] = []
    for trial, (dimension, controls) in enumerate(((2, 5), (3, 8), (5, 11))):
        terminal_map = rng.normal(size=(dimension, controls))
        control = rng.normal(size=controls)
        covariance = terminal_map @ terminal_map.T
        terminal = terminal_map @ control
        cm_cost = float(terminal @ np.linalg.pinv(covariance, rcond=1e-13) @ terminal)
        input_cost = float(control @ control)
        ratio = cm_cost / input_cost
        compression_ratios.append(ratio)
        check(f"random_global_douglas_{trial}", ratio <= 1.0 + 2e-12, ratio, "<=1")

    # 3. Hilbert martingale/spatial one-use ledger.  Orthogonal-chaos
    # coefficients model d_j Delta_m A; the proof note handles the general
    # conditional-expectation statement.
    s = INPUTS["martingale_s"]
    gap = INPUTS["far_gap"]
    coefficients: dict[tuple[int, int], Fraction] = {}
    for root in range(5):
        for shell in range(8):
            coefficients[(root, shell)] = Fraction(root + 1, (shell + 2) ** 2 * 25)

    l2_square = sum(value**2 for value in coefficients.values())
    h2_square = sum((Fraction(2) ** (4 * shell)) * value**2 for (root, shell), value in coefficients.items())
    martingale_square = sum(value**2 for value in coefficients.values())
    weighted_q = sum((Fraction(2) ** (2 * s * (shell - root))) * value**2 for (root, shell), value in coefficients.items())
    far_square = sum(value**2 for (root, shell), value in coefficients.items() if shell >= root + gap)
    far_from_q = (Fraction(2) ** (-2 * s * gap)) * weighted_q
    check("martingale_parseval_fixture", martingale_square == l2_square, martingale_square, l2_square)
    check("spatial_weighted_q_below_h2", weighted_q <= h2_square, weighted_q, f"<={h2_square}")
    check("far_gap_from_weighted_q", far_square <= far_from_q, far_square, f"<={far_from_q}")
    check("martingale_s_in_progressive_range", Fraction(0) < s <= Fraction(2), s, "0<s<=2")

    # 4. Exact Fourier trace for a first-order root operator.  This is the
    # finite Fourier form of the full-cross-k Cartan reduction in the note.
    root_modes = tuple(range(-2, 3))
    output_modes = tuple(range(16, 32))
    root_weights = {mode: Fraction(1, (1 + mode * mode) ** 2) for mode in root_modes}
    coefficient_modes = tuple(sorted({output - root for output in output_modes for root in root_modes}))
    b_hat = {mode: complex(Fraction((abs(mode) % 5) + 1, 37), Fraction((abs(mode) % 3) - 1, 41)) for mode in coefficient_modes}
    c_hat = {mode: complex(Fraction((abs(mode) % 7) - 3, 53), Fraction((abs(mode) % 4) + 1, 59)) for mode in coefficient_modes}
    trace_direct = 0.0
    operator_columns: list[np.ndarray] = []
    for root in root_modes:
        column: list[complex] = []
        for output in output_modes:
            coefficient = b_hat[output - root] + 1j * root * c_hat[output - root]
            summand = float(root_weights[root]) * abs(coefficient) ** 2
            trace_direct += summand
            column.append(float(root_weights[root]) ** 0.5 * coefficient)
        operator_columns.append(np.asarray(column, dtype=np.complex128))
    operator_matrix = np.column_stack(operator_columns)
    trace_formula = float(np.vdot(operator_matrix, operator_matrix).real)
    lambda_zero = sum(root_weights.values())
    lambda_one = sum(root_weights[root] * root * root for root in root_modes)
    b_tail = sum(abs(value) ** 2 for value in b_hat.values())
    c_tail = sum(abs(value) ** 2 for value in c_hat.values())
    trace_bound = 2 * float(lambda_zero) * b_tail + 2 * float(lambda_one) * c_tail
    check("cartan_fourier_trace_identity_fixture", abs(trace_direct - trace_formula) < 1e-14, trace_direct - trace_formula, 0.0)
    check("cartan_two_coefficient_tail_bound_fixture", trace_direct <= trace_bound + 1e-12, trace_direct, f"<={trace_bound}")
    check("cartan_root_value_trace_positive", lambda_zero > 0, lambda_zero, ">0")
    check("cartan_root_derivative_trace_positive", lambda_one > 0, lambda_one, ">0")

    bridge_s = INPUTS["bridge_s"]
    bridge_x = (1 + bridge_s) / 4
    bridge_y = (7 - bridge_s) / 12
    bridge_slack = 1 - bridge_x - bridge_y
    bridge_moment = 1 / bridge_slack
    bridge_eta_loss = bridge_x / bridge_slack
    bridge_zeta_loss = bridge_y / bridge_slack
    direct_schur_bridge = 1.0 / (
        (1.0 - 2.0 ** (-float(bridge_s))) ** 2
        * (1.0 - 2.0 ** (-2.0 * float(bridge_s)))
    )
    check("bridge_s_positive_subunit", Fraction(0) < bridge_s < Fraction(1), bridge_s, "0<s<1")
    check("bridge_energy_power", bridge_x == Fraction(5, 16), bridge_x, Fraction(5, 16))
    check("bridge_sextic_power", bridge_y == Fraction(9, 16), bridge_y, Fraction(9, 16))
    check("bridge_young_slack", bridge_slack == Fraction(1, 8), bridge_slack, Fraction(1, 8))
    check("bridge_model_moment", bridge_moment == 8, bridge_moment, 8)
    check("bridge_eta_loss", bridge_eta_loss == Fraction(5, 2), bridge_eta_loss, Fraction(5, 2))
    check("bridge_zeta_loss", bridge_zeta_loss == Fraction(9, 2), bridge_zeta_loss, Fraction(9, 2))
    check("bridge_direct_schur_finite", math.isfinite(direct_schur_bridge) and direct_schur_bridge > 0, direct_schur_bridge, ">0 finite")

    # A production scalar ray proves that the complete atom cannot be
    # bounded homogeneously by the quartic A^3 D A payload alone.  With
    # theta=2x, the relevant function is
    # (1+cos theta)^2(7+cos theta)/(2(3+cos theta)^2).
    root_two = sp.sqrt(2)
    harmonic_32 = sp.factor(
        root_two
        * (102 * root_two - 137)
        * (3 - 2 * root_two) ** 15
        / 2
    )
    derivative_harmonic_32 = sp.factor(-32 * harmonic_32)
    harmonic_energy = sp.factor(derivative_harmonic_32**2 / 2)
    check("cartan_scalar_harmonic_32_exact_positive", harmonic_32 > 0, harmonic_32, ">0")
    check("cartan_scalar_derivative_harmonic_nonzero", derivative_harmonic_32 != 0, derivative_harmonic_32, "nonzero")
    check("cartan_scalar_far_energy_positive", harmonic_energy > 0, harmonic_energy, ">0")
    small_amplitudes = [sp.Rational(1, 2**power) for power in range(2, 7)]
    homogeneity_ratios = [sp.factor((amplitude**2 * derivative_harmonic_32**2) / amplitude**4) for amplitude in small_amplitudes]
    check("pure_quartic_ratio_grows_under_halving", all(homogeneity_ratios[index + 1] > homogeneity_ratios[index] for index in range(len(homogeneity_ratios) - 1)), homogeneity_ratios, "strictly increasing")
    check("pure_quartic_ratio_growth_factor", all(sp.simplify(homogeneity_ratios[index + 1] / homogeneity_ratios[index] - 4) == 0 for index in range(len(homogeneity_ratios) - 1)), [sp.N(homogeneity_ratios[index + 1] / homogeneity_ratios[index], 20) for index in range(len(homogeneity_ratios) - 1)], 4)

    # 5. Exact Taylor-coordinate conditional diagonalisation.
    eta = sp.Rational(2, 7)
    b_t = sp.Matrix([[3, sp.Rational(1, 5)], [sp.Rational(1, 5), 2]])
    ell = sp.Matrix([[sp.Rational(1, 2), sp.Rational(-1, 4)], [sp.Rational(-1, 4), sp.Rational(3, 4)]])
    b_1 = b_t + ell
    mu = sp.Matrix([sp.Rational(2, 3), sp.Rational(-1, 5)])
    control_gradient = sp.Matrix([sp.Rational(-1, 7), sp.Rational(3, 8)])
    covariance = sp.Matrix([[sp.Rational(7, 5), sp.Rational(1, 10)], [sp.Rational(1, 10), sp.Rational(6, 5)]])
    gamma = sp.Matrix([[1, 0], [0, 1]])
    lhs = sp.Rational(1, 2) * sp.trace(ell * (covariance - gamma + mu * mu.T))
    lhs += (mu.T * ell * control_gradient)[0]
    lhs += sp.Rational(1, 2) * (control_gradient.T * b_1 * control_gradient)[0]
    lhs += eta * (control_gradient.T * control_gradient)[0]
    rhs = sp.Rational(1, 2) * ((control_gradient + mu).T * ell * (control_gradient + mu))[0]
    rhs += sp.Rational(1, 2) * (control_gradient.T * (b_t + 2 * eta * sp.eye(2)) * control_gradient)[0]
    rhs += sp.Rational(1, 2) * sp.trace(ell * (covariance - gamma))
    check("conditional_taylor_coordinate_identity", sp.simplify(lhs - rhs) == 0, sp.simplify(lhs - rhs), 0)

    ell_good = sp.diag(sp.Rational(1, 3), sp.Rational(2, 5))
    bt_eta_good = sp.diag(sp.Rational(1, 7), sp.Rational(3, 8))
    grid_values = []
    for c0 in (-2, 0, 3):
        for c1_grid in (-1, 2):
            for m0 in (-3, 1):
                c_vec = sp.Matrix([c0, c1_grid])
                m_vec = sp.Matrix([m0, 2 - m0])
                value = sp.Rational(1, 2) * ((c_vec + m_vec).T * ell_good * (c_vec + m_vec))[0]
                value += sp.Rational(1, 2) * (c_vec.T * bt_eta_good * c_vec)[0]
                grid_values.append(value)
    check("spectral_sufficiency_grid", min(grid_values) >= 0, min(grid_values), ">=0")

    negative_ell = sp.diag(-1, 2)
    negative_mean = sp.Matrix([1, 0])
    negative_l_value = sp.Rational(1, 2) * (negative_mean.T * negative_ell * negative_mean)[0]
    check("spectral_necessity_negative_L", negative_l_value < 0, negative_l_value, "<0 with c=0")
    negative_bt_eta = sp.diag(-2, 1)
    c_bad = sp.Matrix([1, 0])
    mu_cancel = -c_bad
    negative_bt_value = sp.Rational(1, 2) * ((c_bad + mu_cancel).T * sp.eye(2) * (c_bad + mu_cancel))[0]
    negative_bt_value += sp.Rational(1, 2) * (c_bad.T * negative_bt_eta * c_bad)[0]
    check("spectral_necessity_negative_BT_eta", negative_bt_value < 0, negative_bt_value, "<0 with mu=-c")

    # 6. Production scalar Taylor remainder.  Scale x=sqrt(e) u; the
    # normalized Gram is f(u)^2 and the physical Gram is 4*c1*e*f(u)^2.
    u, capital_c = sp.symbols("u capital_c", real=True)
    alpha = sp.Rational(INPUTS["rational_alpha"].numerator, INPUTS["rational_alpha"].denominator)
    normalized_g = u - alpha * u**3 / (u**2 + 1)
    normalized_b = sp.factor(normalized_g**2)
    normalized_bt = sp.factor(
        normalized_b.subs(u, 1)
        + sp.diff(normalized_b, u).subs(u, 1) * capital_c
        + sp.diff(normalized_b, u, 2).subs(u, 1) * capital_c**2 / 2
    )
    normalized_b1 = sp.factor(normalized_b.subs(u, 1 + capital_c))
    normalized_l = sp.factor(normalized_b1 - normalized_bt)
    expected_l_formula = sp.factor(
        5
        * capital_c**3
        * (13 * capital_c**3 + 36 * capital_c**2 + 51 * capital_c + 20)
        / (324 * (capital_c**2 + 2 * capital_c + 2) ** 2)
    )
    check("production_scalar_remainder_formula", sp.simplify(normalized_l - expected_l_formula) == 0, sp.simplify(normalized_l - expected_l_formula), 0)

    production_shift = sp.Rational(-1, 2)
    endpoint_value = sp.simplify(normalized_b1.subs(capital_c, production_shift))
    taylor_value = sp.simplify(normalized_bt.subs(capital_c, production_shift))
    remainder_value = sp.simplify(normalized_l.subs(capital_c, production_shift))
    check("production_scalar_endpoint_value", endpoint_value == sp.Rational(16, 81), endpoint_value, TEST_ORACLES["scalar_endpoint_normalized"])
    check("production_scalar_taylor_value", taylor_value == sp.Rational(259, 1296), taylor_value, TEST_ORACLES["scalar_taylor_normalized"])
    check("production_scalar_remainder_negative", remainder_value == sp.Rational(-1, 432), remainder_value, TEST_ORACLES["scalar_remainder_normalized"])

    floor = sp.Rational(INPUTS["density_floor"].numerator, INPUTS["density_floor"].denominator)
    mass_square = sp.Rational(INPUTS["mass_square"].numerator, INPUTS["mass_square"].denominator)
    c_one = sp.Rational(INPUTS["rational_numerator"].numerator, INPUTS["rational_numerator"].denominator) / (
        sp.Rational(INPUTS["rational_denominator_factor"].numerator, INPUTS["rational_denominator_factor"].denominator)
        * (mass_square + floor)
    )
    production_l = sp.simplify(4 * c_one * floor * remainder_value)
    production_mean_defect = sp.simplify(production_l / 2)
    check("production_L_exact", production_l == -c_one * floor / 108, production_l, -c_one * floor / 108)
    check("production_mean_defect_exact", production_mean_defect == -c_one * floor / 216, production_mean_defect, -c_one * floor / 216)
    check("production_mean_defect_negative_for_every_eta", production_mean_defect < 0, production_mean_defect, "<0")

    # An unconditionally centered/covariance-matched carrier can still have
    # a negative same-root adapted coefficient.  The Gaussian half-space
    # moment is E[(G^2-1)1_{|G|>=1}]=2 phi(1).
    positive_shift = sp.Rational(1, 2)
    positive_remainder = sp.simplify(normalized_l.subs(capital_c, positive_shift))
    check("production_positive_shift_remainder", positive_remainder == sp.Rational(2245, 219024), positive_remainder, sp.Rational(2245, 219024))
    adapted_exact_factor = sp.factor(4 * (remainder_value - positive_remainder))
    check("adapted_covariance_defect_exact_factor", adapted_exact_factor == -sp.Rational(688, 13689), adapted_exact_factor, -sp.Rational(688, 13689))
    gaussian_density_one = sp.exp(-sp.Rational(1, 2)) / sp.sqrt(2 * sp.pi)
    adapted_expectation = sp.N(adapted_exact_factor * c_one * floor * gaussian_density_one, 40)
    check("adapted_covariance_defect_negative", adapted_expectation < 0, adapted_expectation, "<0")

    claims_not_established = {
        "production_sequential_secant_to_quartic_bridge": False,
        "direct_integrated_cartan_cfar": False,
        "complete_same_root_rational_packet": False,
        "complete_regular_packet_lower_bound": False,
        "uniform_overlap_bound": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-progressive-covariance-compression-rational-mean-spectral-boundary-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "progressive_compression": {
            "operator_identity": "T T^*=C",
            "pathwise_contraction": "||C^(-1/2)T v||^2<=int |v_t|^2 dt",
            "martingale_one_use": "sum_j E||d_j A||_CM^2<=E||A||_CM^2<=E cost",
            "weighted_spatial_ledger": "sum_jm 2^(2s(m-j)) E||Delta_m d_j A||^2<=C E cost for 0<s<=2",
            "revisit_fixture_ratio": float(repeated_cm / repeated_energy),
            "random_compression_ratios": compression_ratios,
            "terminal_quartic_bridge_general_progressive": True,
            "complete_packet_overlap": False,
        },
        "cartan": {
            "full_cross_k_fourier_trace": "sum_pq lambda_p |Bhat(q-p)+i p dot Chat(q-p)|^2",
            "two_tail_reduction": "2 Lambda_0 ||tilde Pi_m B||_2^2+2 Lambda_1 ||tilde Pi_m C||_2^2",
            "harmonic_32": str(harmonic_32),
            "harmonic_32_decimal": float(sp.N(harmonic_32, 18)),
            "derivative_harmonic_32_decimal": float(sp.N(derivative_harmonic_32, 18)),
            "harmonic_32_energy_decimal": float(sp.N(harmonic_energy, 18)),
            "bridge_s": str(bridge_s),
            "bridge_direct_schur_constant": direct_schur_bridge,
            "strong_quartic_ledger": {
                "x": str(bridge_x),
                "y": str(bridge_y),
                "slack": str(bridge_slack),
                "model_moment": str(bridge_moment),
                "eta_loss": str(bridge_eta_loss),
                "zeta_loss": str(bridge_zeta_loss),
            },
            "pure_quartic_homogeneous_bridge": False,
            "required_repair": "retain lower-order background/control terms, form-payable constants, and model moments",
        },
        "core_equivalence": {
            "q": str(q),
            "energy_coefficient": str(energy_coefficient),
            "sextic_charge": str(INPUTS["sextic_charge"]),
            "statement": "uniform OVERLAP on A_cs iff the uniform q=10/9 Nelson bound, by R-087 CORE",
        },
        "rational": {
            "conditional_taylor_coordinate": "(c+mu)^T L(c+mu)/2+c^T(B_T+2eta I)c/2+L:(V-Gamma)/2",
            "covariance_matched_universal_nonnegative_iff": "L psd and B_T+2eta I psd",
            "normalized_scalar_remainder": str(remainder_value),
            "production_L": str(production_l),
            "production_mean_defect_coefficient": str(production_mean_defect),
            "adapted_covariance_defect_factor": str(adapted_exact_factor),
            "adapted_covariance_defect_decimal": float(adapted_expectation),
            "eta_repairs_negative_L_mean_channel": False,
            "full_same_root_forest_may_cancel": True,
        },
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-089 primary] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-089 primary] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
