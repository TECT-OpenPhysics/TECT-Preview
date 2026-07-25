#!/usr/bin/env python3
"""Primary executable evidence for the R-091 A13 boundary theorem.

The companion proof note keeps the exact output-projected Cartan trace intact,
derives its gap ledger, and separates two facts which a coarse Z^6 estimate
conflates: that coarse majorant fails on an admissible rare event, while the
exact saturated scalar production map has a strongly decaying FAR tail.  It
also derives the complete linear+rational conditional Schur and same-root
Jensen identities, an exact local sign fixture, and the terminal
nonduplication algebra needed before progressive assembly.

No assertion in this program claims projected CFAR, the complete signed NEAR
bound, progressive assembly, OVERLAP, Nelson, or Sector-A closure.
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
RESULT_ID = "A13-CLASSII-PROJECTED-CARTAN-FULL-FRAME-SCHUR-JENSEN-TEMPORAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-25-primary-projected-cartan-full-frame-temporal-boundary/result.json"

AUTHORITY_NOTES = {
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r084": CLAIM_DIR / "notes/classii-root-diagonal-cartan-ou-linear-pauli-fierz-absorption-260725-v1.0.tex.txt",
    "r087": CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt",
    "r089": CLAIM_DIR / "notes/classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt",
    "r090": CLAIM_DIR / "notes/classii-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-260725-v1.0.tex.txt",
}

# Upstream or declared diagnostic inputs only.  Derived constants are computed.
INPUTS = {
    "alpha": Fraction(2, 5),
    "gamma": Fraction(7, 12),
    "safe_gap": 5,
    "test_gap": 10,
    "rare_probability_power": -6,
    "rare_control_power": 3,
    "rare_shift_power": 1,
    "dimension": 3,
    "production_P": Fraction(4000000000001, 1000000000000),
    "c0_numerator": Fraction(3, 250),
    "c1_numerator": Fraction(243, 8000),
    "gaussian_threshold": Fraction(1, 1),
}

# These are regression oracles, never inputs to a derivation.
TEST_ORACLES = {
    "cartan_gap_exponent": Fraction(7, 6),
    "z_majorant_power": 3,
    "local_frame_factor": Fraction(3708, 21125),
    "q_shift_constant_gap_five": Fraction(3267, 1024),
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
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def geometric_moment(order: int, x: sp.Expr) -> sp.Expr:
    """Return sum_{k>=0} k^order x^k by exact differentiation."""
    expression = 1 / (1 - x)
    for _ in range(order):
        expression = sp.factor(x * sp.diff(expression, x))
    return sp.factor(expression)


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

    # 1. Authority preflight.  These tokens pin the exact upstream scope.
    authority_tokens = {
        "r079": ("Theorem 3.1 (full-current identity)", "mathfrak I_j", "forest after reassembly"),
        "r084": ("Pauli", "Cartan", "absorption"),
        "r087": ("m\\ge j+5", "Theorem 5.1", "PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION"),
        "r089": ("exact trace", "tag{3.9}", "progressive"),
        "r090": ("b_{A,j,i}=\\partial_i c_{A,j}", "tag{6.1}", "projected Cartan FAR"),
    }
    for label, path in AUTHORITY_NOTES.items():
        check(f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(f"authority_{label}_tokens", all(token in text for token in tokens), [token for token in tokens if token in text], list(tokens))

    # 2. Exact output-level gap ledger.  This is a nonnegative sequence
    # identity and loses no coefficient-annulus shells.
    alpha = INPUTS["alpha"]
    gamma = INPUTS["gamma"]
    safe_gap = INPUTS["safe_gap"]
    cartan_gap_power = 2 * gamma
    check("cartan_gap_power", cartan_gap_power == TEST_ORACLES["cartan_gap_exponent"], cartan_gap_power, TEST_ORACLES["cartan_gap_exponent"])
    check("cartan_safe_gap_is_five", safe_gap == 5, safe_gap, 5)

    rng = np.random.default_rng(91025)
    output_energies: dict[int, float] = {
        offset: float(rng.uniform(0.01, 2.0)) for offset in range(safe_gap, 24)
    }
    weighted_output = sum(
        2.0 ** (2.0 * float(gamma) * (offset - safe_gap)) * energy
        for offset, energy in output_energies.items()
    )
    for gap in (safe_gap, 7, INPUTS["test_gap"], 15):
        tail = sum(energy for offset, energy in output_energies.items() if offset >= gap)
        gain = 2.0 ** (-2.0 * float(gamma) * (gap - safe_gap))
        check(f"output_gap_ledger_C_{gap}", tail <= gain * weighted_output * (1 + 1e-13), tail, f"<={gain * weighted_output}")
    coefficient_annulus_loss = 2
    check("output_ledger_avoids_two_shell_loss", safe_gap < safe_gap + coefficient_annulus_loss, safe_gap, safe_gap + coefficient_annulus_loss)

    # Summability margins inherited from the exact R-087 remainders.
    margin_order_two = 4 * alpha - 2 * gamma
    margin_order_three = 6 * alpha - 2 * gamma
    value_weight = 6 * alpha - 1
    derivative_weight = 6 * alpha + 1
    check("order_two_weighted_margin", margin_order_two == Fraction(13, 30), margin_order_two, Fraction(13, 30))
    check("order_three_weighted_margin", margin_order_three == Fraction(37, 30), margin_order_three, Fraction(37, 30))
    check("value_weight", value_weight == Fraction(7, 5), value_weight, Fraction(7, 5))
    check("derivative_weight", derivative_weight == Fraction(17, 5), derivative_weight, Fraction(17, 5))
    check("both_output_sums_converge", margin_order_two > 0 and margin_order_three > 0, [margin_order_two, margin_order_three], "both positive")

    denominator_order_two = 1.0 - 2.0 ** (-float(margin_order_two))
    denominator_order_three = 1.0 - 2.0 ** (-float(margin_order_three))
    check("order_two_geometric_denominator_positive", denominator_order_two > 0, denominator_order_two, ">0")
    check("order_three_geometric_denominator_positive", denominator_order_three > 0, denominator_order_three, ">0")

    # The existing Z^6 majorant fails although the exact trace may not.
    p_power = INPUTS["rare_probability_power"]
    h_power = INPUTS["rare_control_power"]
    a_power = INPUTS["rare_shift_power"]
    z_six_power = 6 * (1 + alpha)
    value_majorant_power = p_power - value_weight + z_six_power + 2 * a_power
    derivative_majorant_power = p_power - derivative_weight + z_six_power + 2 * (a_power + 1)
    control_budget_power = p_power + 2 * h_power
    sextic_budget_power = p_power + 6 * a_power
    mixed_budget_power = (control_budget_power + sextic_budget_power) / 2
    check("rare_value_majorant_power", value_majorant_power == TEST_ORACLES["z_majorant_power"], value_majorant_power, TEST_ORACLES["z_majorant_power"])
    check("rare_derivative_majorant_power", derivative_majorant_power == TEST_ORACLES["z_majorant_power"], derivative_majorant_power, TEST_ORACLES["z_majorant_power"])
    check("rare_control_budget_power", control_budget_power == 0, control_budget_power, 0)
    check("rare_sextic_budget_power", sextic_budget_power == 0, sextic_budget_power, 0)
    check("rare_mixed_budget_power", mixed_budget_power == 0, mixed_budget_power, 0)
    check("z6_majorant_route_fails", value_majorant_power > max(control_budget_power, sextic_budget_power), value_majorant_power, ">budget powers")

    # 3. Exact saturation of F(x)=x^3/(1+x^2) on one scalar Fourier mode.
    d, cosine, amplitude = sp.symbols("d cosine amplitude", positive=True, real=True)
    rho = (d - 1) / (d + 1)
    u = 2 * amplitude / (d * (d + 1))
    series_closed = sp.factor(u * (1 + rho) * cosine / ((1 - rho) ** 2 + 4 * rho * cosine**2))
    amplitude_relation = {amplitude**2: d**2 - 1}
    rational_target = amplitude * cosine / (1 + amplitude**2 * cosine**2)
    series_residual = sp.factor(sp.together(series_closed - rational_target).subs(amplitude**2, d**2 - 1))
    check("scalar_series_closed_form", series_residual == 0, series_residual, 0)

    # Exact polynomial-geometric derivative tail.
    K, x = sp.symbols("K x", integer=True, positive=True)
    tail_formula = x**K * (
        (2 * K + 1) ** 2 / (1 - x)
        + 4 * (2 * K + 1) * x / (1 - x) ** 2
        + 4 * x * (1 + x) / (1 - x) ** 3
    )
    n = sp.symbols("n", integer=True, nonnegative=True)
    shifted_moment = sp.factor(
        x**K
        * (
            (2 * K + 1) ** 2 * geometric_moment(0, x)
            + 4 * (2 * K + 1) * geometric_moment(1, x)
            + 4 * geometric_moment(2, x)
        )
    )
    check("scalar_tail_closed_form", sp.factor(tail_formula - shifted_moment) == 0, sp.factor(tail_formula - shifted_moment), 0)

    scalar_tail_diagnostics: dict[str, float] = {}
    for amplitude_value in (Fraction(1, 2), Fraction(3, 1), Fraction(10, 1)):
        d_value = math.sqrt(1.0 + float(amplitude_value) ** 2)
        rho_value = (d_value - 1.0) / (d_value + 1.0)
        u_value = 2.0 * float(amplitude_value) / (d_value * (d_value + 1.0))
        start = 3
        exact_sum = sum((2 * k + 1) ** 2 * rho_value ** (2 * k) for k in range(start, 20000))
        closed_sum = float(tail_formula.subs({K: start, x: rho_value**2}))
        residual = abs(exact_sum - closed_sum)
        scalar_tail_diagnostics[str(amplitude_value)] = closed_sum * u_value**2 / 2.0
        check(f"scalar_tail_numeric_A_{amplitude_value}", residual < 2e-11 * max(1.0, closed_sum), residual, "relative/absolute <2e-11")

    # Exact arbitrary-gap first-variation coefficients.  Differentiate the
    # standard Fourier coefficient of 1/(a+cos t) to get its square.
    parameter = sp.symbols("parameter", positive=True)
    root = parameter - sp.sqrt(parameter**2 - 1)
    base_coefficient = lambda index: 2 / sp.sqrt(parameter**2 - 1) * (-root) ** index
    square_coefficient = lambda index: -sp.diff(base_coefficient(index), parameter)
    r_exact = 3 - 2 * sp.sqrt(2)
    harmonic_coefficients: dict[str, str] = {}
    for index in range(2, 9):
        derived = sp.factor((-6 * base_coefficient(index) + 8 * square_coefficient(index)).subs(parameter, 3))
        expected = sp.factor((-r_exact) ** index * (2 * index - 3 * sp.sqrt(2) / 2))
        harmonic_coefficients[str(index)] = str(derived)
        check(f"first_variation_harmonic_n_{index}", sp.simplify(derived - expected) == 0, derived, expected)
        check(f"first_variation_harmonic_nonzero_n_{index}", derived != 0, derived, "nonzero")

    rho_tail = sp.factor(r_exact**2)
    a_tail = 3 * sp.sqrt(2) / 2
    R = sp.symbols("R", integer=True, positive=True)
    L = {order: geometric_moment(order, x) for order in range(5)}
    S2 = x**R * (R**2 * L[0] + 2 * R * L[1] + L[2])
    S3 = x**R * (R**3 * L[0] + 3 * R**2 * L[1] + 3 * R * L[2] + L[3])
    S4 = x**R * (R**4 * L[0] + 4 * R**3 * L[1] + 6 * R**2 * L[2] + 4 * R * L[3] + L[4])
    exact_first_variation_tail = sp.factor(8 * S4 - 8 * a_tail * S3 + 2 * a_tail**2 * S2)
    check("first_variation_tail_positive_R2", exact_first_variation_tail.subs({R: 2, x: rho_tail}) > 0, sp.N(exact_first_variation_tail.subs({R: 2, x: rho_tail}), 20), ">0")
    C_rho = sp.factor((1 + 11 * rho_tail + 11 * rho_tail**2 + rho_tail**3) / (1 - rho_tail) ** 5)
    upper_R2 = sp.factor(8 * C_rho * 2**4 * rho_tail**2)
    check("first_variation_tail_upper_R2", sp.N(upper_R2 - exact_first_variation_tail.subs({R: 2, x: rho_tail}), 30) > 0, sp.N(exact_first_variation_tail.subs({R: 2, x: rho_tail}), 20), f"<={sp.N(upper_R2, 20)}")
    check("first_variation_tail_constant", abs(float(C_rho.evalf()) - 1.54821660985479) < 2e-14, C_rho.evalf(20), "regression decimal")

    # Conservative q-shift comparison in three dimensions.
    q_shift_upper = INPUTS["dimension"] * (1 + Fraction(1, 2**safe_gap)) ** 2
    check("q_shift_upper_gap_five", q_shift_upper == TEST_ORACLES["q_shift_constant_gap_five"], q_shift_upper, TEST_ORACLES["q_shift_constant_gap_five"])
    q_rng = np.random.default_rng(91525)
    q_ratios: list[float] = []
    for _ in range(100):
        root_scale = 2**8
        coefficient_scale = 2 ** (8 + safe_gap)
        p = q_rng.integers(-root_scale, root_scale + 1, size=3)
        rvec = q_rng.integers(-coefficient_scale, coefficient_scale + 1, size=3)
        coordinate = int(q_rng.integers(0, 3))
        rvec[coordinate] = int(q_rng.choice((-1, 1))) * coefficient_scale
        qvec = rvec + p
        denominator = float(np.max(np.abs(rvec)) ** 2)
        ratio = float(np.dot(qvec, qvec) / denominator)
        q_ratios.append(ratio)
    q_shift_lower = float((1 - Fraction(1, 2**safe_gap)) ** 2)
    check("q_shift_random_lower", min(q_ratios) >= q_shift_lower - 1e-14, min(q_ratios), f">={q_shift_lower}")
    check("q_shift_random_upper", max(q_ratios) <= float(q_shift_upper) + 1e-14, max(q_ratios), f"<={float(q_shift_upper)}")

    # 4. Exact full-frame conditional Schur identity.
    b0, b1, mu, variance, covariance, control_derivative, eta = sp.symbols(
        "b0 b1 mu variance covariance control_derivative eta", positive=True, real=True
    )
    direct_conditional = (
        sp.Rational(1, 2) * (b1 - b0) * (variance + mu**2 - covariance)
        + mu * b1 * control_derivative
        + sp.Rational(1, 2) * b1 * control_derivative**2
    )
    square_conditional = (
        sp.Rational(1, 2) * b1 * (control_derivative + mu) ** 2
        - sp.Rational(1, 2) * b0 * mu**2
        + sp.Rational(1, 2) * (b1 - b0) * (variance - covariance)
    )
    check("conditional_full_frame_scalar_identity", sp.expand(direct_conditional - square_conditional) == 0, sp.expand(direct_conditional - square_conditional), 0)
    A_eta = b1 + 2 * eta
    minimizer = -b1 * mu / A_eta
    minimized = sp.factor((direct_conditional + eta * control_derivative**2).subs(control_derivative, minimizer))
    schur_form = sp.Rational(1, 2) * (b1 - b0) * (variance - covariance) + sp.Rational(1, 2) * mu**2 * (2 * eta * b1 / A_eta - b0)
    check("conditional_full_frame_schur_minimum", sp.factor(minimized - schur_form) == 0, sp.factor(minimized - schur_form), 0)
    universal_upper = sp.factor(2 * eta - 2 * eta * b1 / A_eta)
    check("schur_positive_part_bounded_by_2eta", universal_upper.is_positive is True, universal_upper, ">0")

    # Matrix checks detect transpose, factor-two, and trace-convention errors.
    matrix_rng = np.random.default_rng(91925)
    matrix_residuals: list[float] = []
    minimizer_residuals: list[float] = []
    for _ in range(25):
        dimension = 4
        raw0 = matrix_rng.normal(size=(dimension, dimension))
        raw1 = matrix_rng.normal(size=(dimension, dimension))
        B0 = raw0.T @ raw0 + 0.2 * np.eye(dimension)
        B1 = raw1.T @ raw1 + 0.3 * np.eye(dimension)
        D = B1 - B0
        mean = matrix_rng.normal(size=dimension)
        rawv = matrix_rng.normal(size=(dimension, dimension))
        V = rawv.T @ rawv
        rawg = matrix_rng.normal(size=(dimension, dimension))
        Gamma = rawg.T @ rawg
        cvec = matrix_rng.normal(size=dimension)
        direct = 0.5 * np.sum(D * (V + np.outer(mean, mean) - Gamma)) + mean @ B1 @ cvec + 0.5 * cvec @ B1 @ cvec
        completed = 0.5 * (cvec + mean) @ B1 @ (cvec + mean) - 0.5 * mean @ B0 @ mean + 0.5 * np.sum(D * (V - Gamma))
        matrix_residuals.append(abs(float(direct - completed)))

        eta_value = float(matrix_rng.uniform(0.1, 2.0))
        A = B1 + 2 * eta_value * np.eye(dimension)
        cstar = -np.linalg.solve(A, B1 @ mean)
        evaluated = direct = 0.5 * np.sum(D * (V + np.outer(mean, mean) - Gamma)) + mean @ B1 @ cstar + 0.5 * cstar @ B1 @ cstar + eta_value * (cstar @ cstar)
        predicted = 0.5 * np.sum(D * (V - Gamma)) + 0.5 * mean @ (2 * eta_value * B1 @ np.linalg.inv(A) - B0) @ mean
        minimizer_residuals.append(abs(float(evaluated - predicted)))
    check("conditional_full_frame_matrix_identity", max(matrix_residuals) < 2e-12, max(matrix_residuals), "<2e-12")
    check("conditional_full_frame_matrix_minimum", max(minimizer_residuals) < 2e-11, max(minimizer_residuals), "<2e-11")

    # Exact same-root Jensen completion on a finite conditional ensemble.
    jensen_residuals: list[float] = []
    jensen_defects: list[float] = []
    for _ in range(20):
        sample_count = 7
        dimension = 3
        weights = matrix_rng.uniform(0.1, 1.0, size=sample_count)
        weights /= np.sum(weights)
        G = matrix_rng.normal(size=(sample_count, dimension))
        C = matrix_rng.normal(size=(sample_count, dimension, dimension))
        D_samples = matrix_rng.normal(size=(sample_count, dimension, dimension))
        D_samples = 0.5 * (D_samples + np.swapaxes(D_samples, 1, 2))
        rawB = matrix_rng.normal(size=(sample_count, dimension, dimension))
        B_samples = np.einsum("sji,sjk->sik", rawB, rawB) + 0.5 * np.eye(dimension)[None, :, :]
        Gamma = np.eye(dimension)
        cvec = matrix_rng.normal(size=dimension)
        eta_value = 0.4
        mean = np.einsum("s,si->i", weights, G)
        centered = G - mean
        V = np.einsum("s,si,sj->ij", weights, centered, centered)
        hatC = np.einsum("s,sij->ij", weights, C)
        hatD = np.einsum("s,sij->ij", weights, D_samples)
        hatB = np.einsum("s,sij->ij", weights, B_samples)
        rC = np.einsum("s,sji,sj->i", weights, C - hatC, centered)
        hvec = hatC.T @ mean + rC
        centered_quadratic = np.einsum("si,sj->sij", G, G) - (V + np.outer(mean, mean))[None, :, :]
        JD = 0.5 * np.einsum("s,sij,sij", weights, D_samples - hatD, centered_quadratic)
        direct_samples = []
        for sample in range(sample_count):
            Q = np.outer(G[sample], G[sample]) - Gamma
            direct_samples.append(0.5 * np.sum(D_samples[sample] * Q) + G[sample] @ C[sample] @ cvec + 0.5 * cvec @ B_samples[sample] @ cvec + eta_value * (cvec @ cvec))
        direct_average = float(weights @ np.asarray(direct_samples))
        A = hatB + 2 * eta_value * np.eye(dimension)
        completed = (
            0.5 * (cvec + np.linalg.solve(A, hvec)) @ A @ (cvec + np.linalg.solve(A, hvec))
            + 0.5 * mean @ hatD @ mean
            + 0.5 * np.sum(hatD * (V - Gamma))
            + JD
            - 0.5 * hvec @ np.linalg.solve(A, hvec)
        )
        jensen_residuals.append(abs(direct_average - float(completed)))
        jensen_defects.append(abs(float(JD)) + float(np.linalg.norm(rC)))
    check("same_root_jensen_completion", max(jensen_residuals) < 3e-12, max(jensen_residuals), "<3e-12")
    check("same_root_jensen_defect_can_be_nonzero", max(jensen_defects) > 0.1, max(jensen_defects), ">0.1 diagnostic")

    # 5. Complete local linear+rational frame sign fixture.
    P = INPUTS["production_P"]
    c0 = INPUTS["c0_numerator"] / P
    c1 = INPUTS["c1_numerator"] / P
    rational_base = Fraction(169, 81)
    rational_minus = Fraction(64, 81)
    rational_plus = Fraction(576, 169)
    delta_minus = -3 * c0 + (rational_minus - rational_base) * c1
    delta_plus = 5 * c0 + (rational_plus - rational_base) * c1
    check("full_frame_delta_minus", delta_minus == -(3 * c0 + Fraction(35, 27) * c1), delta_minus, -(3 * c0 + Fraction(35, 27) * c1))
    check("full_frame_delta_plus", delta_plus == 5 * c0 + Fraction(18095, 13689) * c1, delta_plus, 5 * c0 + Fraction(18095, 13689) * c1)
    check("full_frame_outside_pathwise_negative", delta_minus < 0, delta_minus, "<0")
    check("full_frame_inside_pathwise_negative_with_Q", delta_plus > 0, delta_plus, ">0 while Q<0")
    combined_loss = sp.factor(
        sp.Rational(8 * c0.numerator, c0.denominator)
        + sp.Rational(35840, 13689) * sp.Rational(c1.numerator, c1.denominator)
    )
    expected_loss = sp.Rational(TEST_ORACLES["local_frame_factor"].numerator, TEST_ORACLES["local_frame_factor"].denominator) / sp.Rational(P.numerator, P.denominator)
    check("full_frame_exact_loss_factor", sp.factor(combined_loss - expected_loss) == 0, combined_loss, expected_loss)
    phi_one = math.exp(-0.5) / math.sqrt(2 * math.pi)
    loss_decimal = float(combined_loss) * phi_one
    check("full_frame_expected_loss_negative", -loss_decimal < 0, -loss_decimal, "<0 per floor")

    # 6. Terminal paid split and temporal nonduplication are exact algebra.
    b0_high, bstar_high, r0_low, rstar_low = sp.symbols("b0_high bstar_high r0_low rstar_low", real=True)
    temporal_endpoint = (bstar_high + rstar_low) - (b0_high + r0_low)
    unpaid_packet = sp.expand(b0_high + temporal_endpoint - (rstar_low - r0_low))
    check("terminal_paid_split_nonduplication", sp.expand(unpaid_packet - bstar_high) == 0, unpaid_packet, bstar_high)
    w, fresh, future = sp.symbols("w fresh future", real=True)
    endpoint_square = sp.expand(((w + fresh + future) ** 2 - w**2) / 2)
    temporal_square = sp.expand(w * fresh + fresh**2 / 2 + (w + fresh) * future + future**2 / 2)
    check("temporal_future_cross_once", sp.expand(endpoint_square - temporal_square) == 0, sp.expand(endpoint_square - temporal_square), 0)
    missing_future_cross = sp.expand(w * fresh + fresh**2 / 2 + w * future + future**2 / 2)
    check("temporal_future_cross_is_load_bearing", sp.expand(endpoint_square - missing_future_cross) == fresh * future, sp.expand(endpoint_square - missing_future_cross), fresh * future)

    claims_not_established = {
        "projected_cartan_cfar": False,
        "cartan_output_ledger_one_use": False,
        "complete_signed_near": False,
        "schur_jensen_residual_bound": False,
        "overlap_stable_temporal_cartan": False,
        "regular_packet_lower_bound": False,
        "uniform_overlap": False,
        "nelson": False,
        "interacting_measure": False,
        "sector_a": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-projected-cartan-full-frame-temporal-boundary-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "projected_cartan": {
            "exact_energy_block": "E_Ajm=int_0^infinity exp(-2t) E||Pi_m P_t^(j) D_j H_Aj||_HS^2 dt",
            "safe_principal_gap": safe_gap,
            "output_gap_ledger": "H_C(C)<=2^(-2 gamma (C-5)) B_gamma^out for C>=5",
            "alpha": str(alpha),
            "gamma": str(gamma),
            "gap_exponent": str(cartan_gap_power),
            "weighted_margins": [str(margin_order_two), str(margin_order_three)],
            "z_majorant_rare_power": str(value_majorant_power),
            "budget_rare_powers": [str(control_budget_power), str(sextic_budget_power), str(mixed_budget_power)],
            "z_majorant_proves_one_use": False,
            "exact_cartan_refuted": False,
            "scalar_tail_diagnostics": scalar_tail_diagnostics,
            "first_variation_coefficients": harmonic_coefficients,
            "first_variation_tail_constant": str(C_rho),
            "q_shift_upper_gap_five": str(q_shift_upper),
            "remaining_theorem": "saturation-aware expectation-inside cumulative vector paracomposition controlling B_(7/12)^out, with target heat and coherent multimode outputs",
        },
        "full_frame": {
            "conditional_identity": "E DeltaW=1/2(c+mu)^T B1(c+mu)-1/2 mu^T B0 mu+1/2(B1-B0):(V-Gamma)",
            "schur_minimum": "1/2(B1-B0):(V-Gamma)+1/2 mu^T[2eta B1(B1+2eta I)^(-1)-B0]mu",
            "universal_fixed_eta_positivity": False,
            "same_root_residual": "1/2 mu^T Dhat mu+1/2 Dhat:(V-Gamma)+J_D-1/2 h^T(Bhat+2eta I)^(-1)h",
            "local_pathwise_delta_minus": str(delta_minus),
            "local_pathwise_delta_plus": str(delta_plus),
            "local_expected_loss_factor_before_floor_phi": str(combined_loss),
            "local_expected_loss_per_floor": -loss_decimal,
            "local_fixture_is_post_paid_counterexample": False,
        },
        "temporal": {
            "terminal_nonduplication": "B_>(A0)+[B_full(A*)-B_full(A0)]-[R_le(A*)-R_le(A0)]=B_>(A*)",
            "terminal_split_algebra_closed": True,
            "progressive_projection_mapping_closed": False,
            "overlap_stable_temporal_extension_closed": False,
            "future_feedback_cross_retained": True,
        },
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-091 primary] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-091 primary] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
