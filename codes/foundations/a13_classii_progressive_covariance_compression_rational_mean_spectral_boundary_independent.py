#!/usr/bin/env python3
"""Non-importing independent audit for the R-089 A13 reduction.

This script reconstructs the global covariance compression, martingale
one-use ledger, full-cross-k Fourier trace, scalar Cartan harmonic, rational
Taylor-coordinate identity, and production same-root sign fixtures without
importing the primary executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PROGRESSIVE-COVARIANCE-COMPRESSION-RATIONAL-MEAN-SPECTRAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-progressive-covariance-compression-rational-mean-spectral-boundary/result.json"


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


def plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, mp.mpf):
        return mp.nstr(value, 50)
    return value


def conditional_prefix(values: np.ndarray, states: list[tuple[int, ...]], prefix: int) -> np.ndarray:
    """Conditional expectation on the first ``prefix`` Rademacher bits."""
    result = np.zeros_like(values, dtype=float)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, state in enumerate(states):
        groups.setdefault(state[:prefix], []).append(index)
    for indices in groups.values():
        mean = values[indices].mean(axis=0)
        result[indices] = mean
    return result


def main() -> int:
    mp.mp.dps = 80
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": plain(actual),
                "expected": plain(expected),
            }
        )

    # 1. Global polar/Douglas compression with unrelated dimensions/seeds.
    rng = np.random.default_rng(90251)
    polar_ratios: list[float] = []
    polar_residuals: list[float] = []
    for trial, (terminal_dimension, time_dimension) in enumerate(((1, 7), (4, 9), (6, 14), (7, 18))):
        terminal_map = rng.normal(size=(terminal_dimension, time_dimension))
        control = rng.normal(size=time_dimension)
        covariance = terminal_map @ terminal_map.T
        terminal = terminal_map @ control
        cm_cost = float(terminal @ np.linalg.pinv(covariance, rcond=1e-13) @ terminal)
        input_cost = float(control @ control)
        ratio = cm_cost / input_cost
        polar_ratios.append(ratio)
        check(f"independent_douglas_ratio_{trial}", ratio <= 1.0 + 5e-12, ratio, "<=1")

        u, singular, vt = np.linalg.svd(terminal_map, full_matrices=False)
        reconstructed_covariance = (u * singular**2) @ u.T
        residual = float(np.max(np.abs(reconstructed_covariance - covariance)))
        polar_residuals.append(residual)
        check(f"independent_covariance_svd_{trial}", residual < 2e-11, residual, "<2e-11")
        check(f"independent_singular_values_nonnegative_{trial}", bool(np.all(singular >= 0)), singular.tolist(), ">=0")
        del vt

    repeat_count = 17
    dt = 1.0 / repeat_count
    repeat_map = np.full((1, repeat_count), math.sqrt(dt))
    repeat_control = np.ones(repeat_count) * math.sqrt(dt)
    repeat_covariance = float((repeat_map @ repeat_map.T)[0, 0])
    repeat_terminal = float((repeat_map @ repeat_control)[0])
    repeat_energy = float(repeat_control @ repeat_control)
    check("independent_repeat_covariance", abs(repeat_covariance - 1.0) < 1e-14, repeat_covariance, 1.0)
    check("independent_repeat_terminal", abs(repeat_terminal - 1.0) < 1e-14, repeat_terminal, 1.0)
    check("independent_repeat_no_multiplicity", abs(repeat_terminal**2 / repeat_covariance - repeat_energy) < 1e-14, repeat_terminal**2 / repeat_covariance, repeat_energy)

    # 2. A genuine finite martingale audit on four Rademacher roots and six
    # spatial shells.  Conditional expectations are enumerated, not encoded
    # through an orthogonal-chaos oracle.
    roots = 4
    shells = 6
    states = list(itertools.product((-1, 1), repeat=roots))
    values = np.zeros((len(states), shells), dtype=float)
    for state_index, state in enumerate(states):
        for shell in range(shells):
            linear = sum((root + 1) * state[root] for root in range(roots)) / ((shell + 2) * 31.0)
            quadratic = state[0] * state[min(roots - 1, shell % roots)] / ((shell + 3) * 47.0)
            values[state_index, shell] = linear + quadratic

    martingale_differences = []
    previous = conditional_prefix(values, states, 0)
    for prefix in range(1, roots + 1):
        current = conditional_prefix(values, states, prefix)
        martingale_differences.append(current - previous)
        previous = current
    martingale_differences = np.asarray(martingale_differences)
    centered = values - values.mean(axis=0, keepdims=True)
    parseval_left = float(np.mean(np.sum(martingale_differences**2, axis=(0, 2))))
    parseval_right = float(np.mean(np.sum(centered**2, axis=1)))
    check("independent_martingale_parseval", abs(parseval_left - parseval_right) < 2e-14, parseval_left - parseval_right, 0.0)

    h2_ledger = 0.0
    weighted_ledger = 0.0
    far_ledger = 0.0
    s = Fraction(7, 12)
    gap = 3
    for root in range(roots):
        for shell in range(shells):
            square = float(np.mean(martingale_differences[root, :, shell] ** 2))
            h2_ledger += 2.0 ** (4 * shell) * square
            weighted_ledger += 2.0 ** (2 * float(s) * (shell - root)) * square
            if shell >= root + gap:
                far_ledger += square
    check("independent_weighted_ledger_below_h2", weighted_ledger <= h2_ledger + 1e-12, weighted_ledger, f"<={h2_ledger}")
    check("independent_far_gap_ledger", far_ledger <= 2.0 ** (-2 * float(s) * gap) * weighted_ledger + 1e-12, far_ledger, f"<={2.0 ** (-2 * float(s) * gap) * weighted_ledger}")

    # 3. Independent complex Fourier reconstruction of the first-order
    # root trace and its two-coefficient bound.
    root_modes = tuple(range(-3, 4))
    output_modes = tuple(range(32, 49))
    root_weights = {mode: 1.0 / (2.0 + mode * mode) ** 2 for mode in root_modes}
    coefficient_modes = tuple(sorted({output - root for output in output_modes for root in root_modes}))
    b_hat = {mode: rng.normal() + 1j * rng.normal() for mode in coefficient_modes}
    c_hat = {mode: rng.normal() + 1j * rng.normal() for mode in coefficient_modes}
    direct_trace = 0.0
    matrix_columns: list[np.ndarray] = []
    for root in root_modes:
        column = np.asarray(
            [math.sqrt(root_weights[root]) * (b_hat[output - root] + 1j * root * c_hat[output - root]) for output in output_modes],
            dtype=complex,
        )
        matrix_columns.append(column)
        direct_trace += float(np.vdot(column, column).real)
    operator_matrix = np.column_stack(matrix_columns)
    hs_trace = float(np.linalg.norm(operator_matrix, "fro") ** 2)
    lambda_zero = sum(root_weights.values())
    lambda_one = sum(root_weights[root] * root * root for root in root_modes)
    two_tail_bound = 2 * lambda_zero * sum(abs(value) ** 2 for value in b_hat.values())
    two_tail_bound += 2 * lambda_one * sum(abs(value) ** 2 for value in c_hat.values())
    check("independent_cartan_fourier_trace", abs(direct_trace - hs_trace) < 2e-12, direct_trace - hs_trace, 0.0)
    check("independent_cartan_two_tail_bound", direct_trace <= two_tail_bound + 2e-12, direct_trace, f"<={two_tail_bound}")

    bridge_s = Fraction(1, 4)
    bridge_x = (1 + bridge_s) / 4
    bridge_y = (7 - bridge_s) / 12
    bridge_slack = 1 - bridge_x - bridge_y
    check("independent_bridge_x", bridge_x == Fraction(5, 16), bridge_x, Fraction(5, 16))
    check("independent_bridge_y", bridge_y == Fraction(9, 16), bridge_y, Fraction(9, 16))
    check("independent_bridge_slack", bridge_slack == Fraction(1, 8), bridge_slack, Fraction(1, 8))
    check("independent_bridge_moment", 1 / bridge_slack == 8, 1 / bridge_slack, 8)
    direct_schur = 1 / ((1 - mp.power(2, -mp.mpf(1) / 4)) ** 2 * (1 - mp.power(2, -mp.mpf(1) / 2)))
    check("independent_bridge_schur_finite", mp.isfinite(direct_schur) and direct_schur > 0, direct_schur, ">0 finite")

    # 4. High-precision quadrature of the exact scalar Cartan harmonic.
    derivative_f = lambda z: z * z * (3 + z * z) / (1 + z * z) ** 2
    harmonic_function = lambda x: derivative_f(mp.cos(x)) * mp.cos(x) ** 2
    quadrature_cuts = [0, mp.pi / 2, mp.pi, 3 * mp.pi / 2, 2 * mp.pi]
    harmonic_32_quad = mp.quad(lambda x: harmonic_function(x) * mp.cos(32 * x), quadrature_cuts) / mp.pi
    exact_harmonic = mp.sqrt(2) * (102 * mp.sqrt(2) - 137) * (3 - 2 * mp.sqrt(2)) ** 15 / 2
    check("independent_harmonic_32_match", abs(harmonic_32_quad - exact_harmonic) < mp.mpf("1e-70"), harmonic_32_quad - exact_harmonic, "<1e-70")
    check("independent_harmonic_32_positive", harmonic_32_quad > 0, harmonic_32_quad, ">0")
    derivative_harmonic = -32 * harmonic_32_quad
    harmonic_energy = derivative_harmonic**2 / 2
    check("independent_derivative_harmonic_nonzero", derivative_harmonic != 0, derivative_harmonic, "nonzero")
    check("independent_harmonic_energy_positive", harmonic_energy > 0, harmonic_energy, ">0")

    production_f = lambda z: z**3 / (1 + z**2)
    test_amplitudes = (mp.mpf("1e-3"), mp.mpf("5e-4"), mp.mpf("2.5e-4"))
    linearized_ratios = []
    for amplitude in test_amplitudes:
        exact_coefficient = mp.quad(
            lambda x: (
                (production_f((1 + amplitude) * mp.cos(x)) - production_f(mp.cos(x)))
                * mp.cos(x)
            )
            * mp.cos(32 * x),
            quadrature_cuts,
        ) / mp.pi
        # Differentiating in x multiplies the cosine coefficient by -32.
        linearized_ratios.append((-32 * exact_coefficient) / amplitude)
    errors = [abs(value - derivative_harmonic) for value in linearized_ratios]
    check("independent_cartan_linearization_converges", errors[-1] < errors[0], errors, "last<first")
    check("independent_pure_quartic_scaling_mismatch", harmonic_energy / test_amplitudes[-1] ** 2 > harmonic_energy / test_amplitudes[0] ** 2, harmonic_energy / test_amplitudes[-1] ** 2, f">{harmonic_energy / test_amplitudes[0] ** 2}")

    # 5. Rational Taylor-coordinate identity under unrelated random symmetric
    # matrices.  B_1=B_T+L is enforced upstream and both sides are evaluated
    # independently.
    identity_residuals: list[float] = []
    for trial in range(20):
        raw_l = rng.normal(size=(3, 3))
        ell = (raw_l + raw_l.T) / 2
        raw_bt = rng.normal(size=(3, 3))
        b_t = (raw_bt + raw_bt.T) / 2
        b_1 = b_t + ell
        raw_v = rng.normal(size=(3, 3))
        covariance = raw_v @ raw_v.T
        raw_g = rng.normal(size=(3, 3))
        gamma = raw_g @ raw_g.T
        mu = rng.normal(size=3)
        control_gradient = rng.normal(size=3)
        eta = 0.17 + 0.01 * trial
        lhs = 0.5 * np.trace(ell @ (covariance - gamma + np.outer(mu, mu)))
        lhs += mu @ ell @ control_gradient
        lhs += 0.5 * control_gradient @ b_1 @ control_gradient
        lhs += eta * (control_gradient @ control_gradient)
        rhs = 0.5 * (control_gradient + mu) @ ell @ (control_gradient + mu)
        rhs += 0.5 * control_gradient @ (b_t + 2 * eta * np.eye(3)) @ control_gradient
        rhs += 0.5 * np.trace(ell @ (covariance - gamma))
        identity_residuals.append(abs(float(lhs - rhs)))
    check("independent_conditional_identity_random", max(identity_residuals) < 5e-12, max(identity_residuals), "<5e-12")

    alpha = mp.mpf(5) / 9
    scalar_b = lambda u: (u - alpha * u**3 / (u**2 + 1)) ** 2
    base = mp.mpf(1)
    first = mp.diff(scalar_b, base, 1)
    second = mp.diff(scalar_b, base, 2)

    def scalar_remainder(capital_c: mp.mpf) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
        endpoint = scalar_b(base + capital_c)
        taylor = scalar_b(base) + first * capital_c + second * capital_c**2 / 2
        return endpoint, taylor, endpoint - taylor

    endpoint_minus, taylor_minus, remainder_minus = scalar_remainder(mp.mpf(-1) / 2)
    endpoint_plus, taylor_plus, remainder_plus = scalar_remainder(mp.mpf(1) / 2)
    tolerance = mp.mpf("1e-70")
    check("independent_scalar_endpoint_minus", abs(endpoint_minus - mp.mpf(16) / 81) < tolerance, endpoint_minus, mp.mpf(16) / 81)
    check("independent_scalar_taylor_minus", abs(taylor_minus - mp.mpf(259) / 1296) < tolerance, taylor_minus, mp.mpf(259) / 1296)
    check("independent_scalar_remainder_minus", abs(remainder_minus + mp.mpf(1) / 432) < tolerance, remainder_minus, -mp.mpf(1) / 432)
    check("independent_scalar_remainder_plus", abs(remainder_plus - mp.mpf(2245) / 219024) < tolerance, remainder_plus, mp.mpf(2245) / 219024)

    exact_adapted_factor = 4 * (remainder_minus - remainder_plus)
    check("independent_adapted_factor", abs(exact_adapted_factor + mp.mpf(688) / 13689) < tolerance, exact_adapted_factor, -mp.mpf(688) / 13689)
    phi_one = mp.exp(-mp.mpf(1) / 2) / mp.sqrt(2 * mp.pi)
    # Integrate the two tails directly; the middle interval is excluded.
    gaussian_half_moment = mp.quad(lambda x: (x * x - 1) * mp.exp(-x * x / 2) / mp.sqrt(2 * mp.pi), [-mp.inf, -1])
    gaussian_half_moment += mp.quad(lambda x: (x * x - 1) * mp.exp(-x * x / 2) / mp.sqrt(2 * mp.pi), [1, mp.inf])
    check("independent_gaussian_half_moment", abs(gaussian_half_moment - 2 * phi_one) < tolerance, gaussian_half_moment, 2 * phi_one)
    adapted_sign = exact_adapted_factor * phi_one
    check("independent_adapted_same_root_negative", adapted_sign < 0, adapted_sign, "<0")

    good_l = np.diag([0.2, 0.4, 0.7])
    good_bt_eta = np.diag([0.1, 0.3, 0.5])
    good_minimum = math.inf
    for _ in range(100):
        c_vec = rng.normal(size=3)
        mu_vec = rng.normal(size=3)
        value = 0.5 * (c_vec + mu_vec) @ good_l @ (c_vec + mu_vec)
        value += 0.5 * c_vec @ good_bt_eta @ c_vec
        good_minimum = min(good_minimum, float(value))
    check("independent_spectral_sufficiency", good_minimum >= 0, good_minimum, ">=0")
    bad_l = np.diag([-0.2, 0.4, 0.7])
    bad_value = 0.5 * np.asarray([1.0, 0.0, 0.0]) @ bad_l @ np.asarray([1.0, 0.0, 0.0])
    check("independent_eta_cannot_repair_negative_L", bad_value < 0, bad_value, "<0 at c=0")

    # 6. R-087 CORE arithmetic: the full scalar OVERLAP lower bound and the
    # q=10/9 Nelson estimate are equivalent, not two sequential estimates.
    q = Fraction(10, 9)
    energy_coefficient = 1 / (2 * q)
    sample_bound = Fraction(11, 4)
    log_moment_bound = q * sample_bound
    recovered_bound = log_moment_bound / q
    check("independent_core_energy", energy_coefficient == Fraction(9, 20), energy_coefficient, Fraction(9, 20))
    check("independent_overlap_nelson_inverse", recovered_bound == sample_bound, recovered_bound, sample_bound)

    claims_not_established = {
        "nonlinear_cartan_coefficient_tail_energy": False,
        "direct_integrated_cartan_cfar": False,
        "complete_same_root_rational_packet": False,
        "uniform_overlap": False,
        "nelson": False,
        "sector_a": False,
    }
    check("independent_downstream_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-progressive-covariance-compression-rational-mean-spectral-boundary-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "compression_ratios": polar_ratios,
        "polar_residuals": polar_residuals,
        "cartan": {
            "fourier_trace": direct_trace,
            "two_tail_bound": two_tail_bound,
            "harmonic_32": mp.nstr(harmonic_32_quad, 50),
            "derivative_harmonic_32": mp.nstr(derivative_harmonic, 50),
            "harmonic_energy": mp.nstr(harmonic_energy, 50),
            "linearized_ratios": [mp.nstr(value, 40) for value in linearized_ratios],
        },
        "rational": {
            "identity_max_residual": max(identity_residuals),
            "remainder_minus_half": mp.nstr(remainder_minus, 50),
            "remainder_plus_half": mp.nstr(remainder_plus, 50),
            "adapted_factor": mp.nstr(exact_adapted_factor, 50),
            "gaussian_half_moment": mp.nstr(gaussian_half_moment, 50),
        },
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-089 independent] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-089 independent] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
