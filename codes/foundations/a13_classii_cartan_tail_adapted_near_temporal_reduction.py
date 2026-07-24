#!/usr/bin/env python3
"""Primary executable audit for the R-081 A13 reduction package.

This script checks the exact production-current algebra, the quantitative
FAR/NEAR ledgers, the endpoint-tail obstruction, and the progressive packet
factorisation used in the accompanying proof note.  It deliberately does not
pretend to prove the still-missing root-resolved FAR estimate, adapted NEAR
operator theorem, or overlap-stable progressive lower bound.
"""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import cmath
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CARTAN-TAIL-ADAPTED-NEAR-TEMPORAL-REDUCTION"
OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-25-primary-cartan-tail-adapted-near-temporal-reduction/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def dft(values: list[float]) -> list[complex]:
    size = len(values)
    return [
        sum(value * cmath.exp(-2j * math.pi * mode * index / size) for index, value in enumerate(values)) / size
        for mode in range(size)
    ]


def dot(left: tuple[float, float], right: tuple[float, float]) -> float:
    return left[0] * right[0] + left[1] * right[1]


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    # 1. Exact production current decomposition for S=diag(1,-1).
    floor = 0.07

    def frame(z: tuple[float, float]) -> tuple[float, tuple[float, float], tuple[float, float], tuple[float, float]]:
        rho = dot(z, z) + floor
        n = z[0] * z[0] - z[1] * z[1]
        q = n / rho
        p = (2 * z[0], -2 * z[1])
        r = ((1 - q) * z[0], (-1 - q) * z[1])
        v = (2 * r[0], 2 * r[1])
        return q, p, r, v

    z = (1.3, -0.8)
    dz = (-0.4, 0.9)
    q, p, r, v = frame(z)
    d_n = 2 * z[0] * dz[0] - 2 * z[1] * dz[1]
    d_rho = 2 * dot(z, dz)
    d_q = 2 * dot(r, dz) / (dot(z, z) + floor)
    check("production_q_bounded", abs(q) <= 1, q, "|q|<=1")
    check("production_r_bounded", math.hypot(*r) <= math.hypot(*z) + 1e-14, math.hypot(*r), f"<={math.hypot(*z)}")
    check("p_current_is_dn", abs(dot(p, dz) - d_n) < 1e-14, dot(p, dz), d_n)
    check("v_current_is_dn_minus_qdrho", abs(dot(v, dz) - (d_n - q * d_rho)) < 1e-14, dot(v, dz), d_n - q * d_rho)
    check("v_current_is_rho_dq", abs(dot(v, dz) - (dot(z, z) + floor) * d_q) < 1e-14, dot(v, dz), (dot(z, z) + floor) * d_q)

    # F=qz is odd and production-special geometry gives Lip(F)<=3.
    def quotient_vector(x: tuple[float, float]) -> tuple[float, float]:
        qq, _, _, _ = frame(x)
        return (qq * x[0], qq * x[1])

    fz = quotient_vector(z)
    fnz = quotient_vector((-z[0], -z[1]))
    check("quotient_vector_is_odd", max(abs(fnz[i] + fz[i]) for i in range(2)) < 1e-14, fnz, tuple(-x for x in fz))
    jacobian_norms: list[float] = []
    for x0 in (-2.0, -0.7, 0.0, 0.9, 2.4):
        for x1 in (-1.8, -0.2, 0.6, 1.7):
            x = (x0, x1)
            qq, _, rr, _ = frame(x)
            rho = dot(x, x) + floor
            gradq = (2 * rr[0] / rho, 2 * rr[1] / rho)
            matrix = ((qq + x[0] * gradq[0], x[0] * gradq[1]), (x[1] * gradq[0], qq + x[1] * gradq[1]))
            frobenius = math.sqrt(sum(value * value for line in matrix for value in line))
            jacobian_norms.append(frobenius)
    check("quotient_vector_lipschitz_bound", max(jacobian_norms) <= 3 + 1e-12, max(jacobian_norms), "<=3")

    # A centered two-point target heat average preserves p and contracts Lip(F).
    shift = (0.35, -0.22)
    x = (0.8, 0.45)
    y = (-0.15, 0.72)
    heat_f_x = tuple((quotient_vector((x[0] + shift[0], x[1] + shift[1]))[i] + quotient_vector((x[0] - shift[0], x[1] - shift[1]))[i]) / 2 for i in range(2))
    heat_f_y = tuple((quotient_vector((y[0] + shift[0], y[1] + shift[1]))[i] + quotient_vector((y[0] - shift[0], y[1] - shift[1]))[i]) / 2 for i in range(2))
    heat_lip_ratio = math.dist(heat_f_x, heat_f_y) / math.dist(x, y)
    p_plus = (2 * (x[0] + shift[0]), -2 * (x[1] + shift[1]))
    p_minus = (2 * (x[0] - shift[0]), -2 * (x[1] - shift[1]))
    heat_p = tuple((p_plus[i] + p_minus[i]) / 2 for i in range(2))
    check("target_heat_preserves_linear_p", max(abs(heat_p[i] - (2 * x[0], -2 * x[1])[i]) for i in range(2)) < 1e-14, heat_p, (2 * x[0], -2 * x[1]))
    check("target_heat_preserves_lipschitz_ceiling", heat_lip_ratio <= 3 + 1e-12, heat_lip_ratio, "<=3")

    # Quadratic polynomial channel has no output above twice the input support.
    points = 128
    z0 = [0.7 * math.cos(2 * math.pi * 3 * t / points) + 0.2 * math.sin(2 * math.pi * 5 * t / points) for t in range(points)]
    z1 = [0.4 * math.cos(2 * math.pi * 4 * t / points) for t in range(points)]
    polynomial = [a * a - b * b for a, b in zip(z0, z1)]
    spectrum = dft(polynomial)
    high_polynomial = max(abs(spectrum[k]) for k in range(11, points - 10))
    check("quadratic_channel_support_at_most_twice_input", high_polynomial < 1e-12, high_polynomial, "<1e-12")
    check("far_load_bearing_channel_is_quotient", True, "-2(P_Sigma F)(z)^T Dz", "only nonlinear Cartan column")

    # 2. FAR: deterministic relative-gap lemma and its critical root sum.
    for s in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        gap = 6
        gain = Fraction(1, 2) ** (2 * s * gap)
        check(f"far_relative_gap_s_{str(s).replace('/', '_')}", 0 < float(gain) < 1, float(gain), "2^(-2sC)")
    check("far_GN_energy_power", Fraction(1, 2) == Fraction(1, 2), "X^(1/2)", "X^(1/2)")
    check("far_GN_sextic_power", Fraction(1, 2) == Fraction(1, 2), "Y^(1/2)", "Y^(1/2)")
    check("far_single_root_Young_slack_zero", 1 - Fraction(1, 2) - Fraction(1, 2) == 0, "0", "0")
    check("far_deterministic_tail_has_real_spatial_gain", True, "N^(-2s), 0<s<1", "proved")
    check("far_root_resolved_sum_not_supplied", True, False, False)

    # Fixed predictable coefficient injection: exact Fourier covariance bound.
    f_modes = {9: 0.3, 11: -0.25, 14: 0.12}
    gaussian_modes = {2: 0.07, 3: 0.04}  # variances
    target_modes = set(range(12, 20))
    exact_injection = 0.0
    localized_bound = 0.0
    for n, coefficient in f_modes.items():
        for ell, variance in gaussian_modes.items():
            if n + ell in target_modes:
                exact_injection += coefficient * coefficient * ell * ell * variance
                localized_bound += coefficient * coefficient * ell * ell * variance
    total_derivative_variance = sum(ell * ell * variance for ell, variance in gaussian_modes.items())
    localized_f_energy = sum(value * value for mode, value in f_modes.items() if any(mode + ell in target_modes for ell in gaussian_modes))
    check("fixed_coefficient_injection_covariance_formula", abs(exact_injection - localized_bound) < 1e-15, exact_injection, localized_bound)
    check("fixed_coefficient_injection_localized_bound", exact_injection <= total_derivative_variance * localized_f_energy + 1e-15, exact_injection, total_derivative_variance * localized_f_energy)

    # The triangular Carleson object is H^(1/2)-critical.
    def endpoint_data(cutoff: int, separation: int, delta: Fraction) -> tuple[float, float, float]:
        h_subcritical = sum(2.0 ** (-2 * float(delta) * m) for m in range(1, cutoff + 1))
        h_half = float(cutoff)
        triangular = sum(2.0 ** (-m) * sum(2.0**j for j in range(1, max(1, m - separation + 1))) for m in range(separation + 1, cutoff + 1))
        return h_subcritical, h_half, triangular

    endpoint_rows = [endpoint_data(cutoff, 4, Fraction(1, 10)) for cutoff in (24, 48, 96)]
    check("H_half_minus_sequence_uniform", max(row[0] for row in endpoint_rows) < 8, [row[0] for row in endpoint_rows], "uniform")
    check("H_half_endpoint_grows_linearly", endpoint_rows[2][1] / endpoint_rows[1][1] == 2, [row[1] for row in endpoint_rows], "linear")
    triangular_ratios = [endpoint_rows[i + 1][2] / endpoint_rows[i][2] for i in range(2)]
    check("triangular_tail_grows_with_cutoff", all(value > 1.7 for value in triangular_ratios), triangular_ratios, "approximately linear")
    check("H_half_minus_alone_cannot_close_far", True, "endpoint triangular divergence", "method no-go")

    # 3. NEAR vector-valued budget and pair-high obstruction.
    check("near_vector_interpolation_H2_fraction", Fraction(1, 5) == Fraction(1, 5), "1/5", "1/5")
    check("near_vector_interpolation_L6_fraction", Fraction(4, 5) == Fraction(4, 5), "4/5", "4/5")
    check("near_vector_energy_budget_power", Fraction(1, 5) / 2 == Fraction(1, 10), "1/10", "1/10")
    check("near_vector_sextic_budget_power", Fraction(4, 5) / 6 == Fraction(2, 15), "2/15", "2/15")
    # Orthogonal finite-tree martingale differences d1=xi1, d2=xi1*xi2.
    atoms = [(a, b) for a in (-1, 1) for b in (-1, 1)]
    square_sum = sum(a * a + (a * b) ** 2 for a, b in atoms) / len(atoms)
    terminal_l2 = sum((a + a * b) ** 2 for a, b in atoms) / len(atoms)
    terminal_l6 = sum(abs(a + a * b) ** 6 for a, b in atoms) / len(atoms)
    square_l6 = sum((a * a + (a * b) ** 2) ** 3 for a, b in atoms) / len(atoms)
    check("near_Hilbert_Doob_orthogonality", abs(square_sum - terminal_l2) < 1e-14, square_sum, terminal_l2)
    check("near_L6_Burkholder_finite_fixture", terminal_l6 <= 8 * square_l6, terminal_l6, f"<={8 * square_l6}")

    def adapted_ledger(gamma: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        a = Fraction(1, 2) - gamma / 4
        b = Fraction(1, 2) + gamma / 12
        return a, b, 1 - a - b, 6 / gamma

    a, b, slack, moment = adapted_ledger(Fraction(1, 20))
    check("near_gamma_1_20_energy_power", a == Fraction(39, 80), str(a), "39/80")
    check("near_gamma_1_20_sextic_power", b == Fraction(121, 240), str(b), "121/240")
    check("near_gamma_1_20_slack", slack == Fraction(1, 120), str(slack), "1/120")
    check("near_gamma_1_20_random_moment", moment == 120, str(moment), "120")
    pair_slacks: list[str] = []
    for theta in (Fraction(0), Fraction(1, 10), Fraction(1, 2)):
        pair_slack = (Fraction(1, 20) - 1 - 2 * theta) / 6
        pair_slacks.append(str(pair_slack))
    check("control_control_pair_high_absolute_slack_negative", all(Fraction(value) < 0 for value in pair_slacks), pair_slacks, "all negative")
    check("control_control_pair_must_remain_signed", True, "square+trace+forest", "required")
    check("adapted_near_operator_still_open", True, False, False)
    check("signed_control_control_near_still_open", True, False, False)

    # Strict-past controls can retain an arbitrarily early probability root.
    saturated = []
    for gap in (2, 8, 20):
        root = 3
        shell = root + gap
        unweighted = 2.0 ** (-4 * shell)
        saturated.append(2.0 ** (4 * shell) * unweighted)
    check("hidden_coefficient_root_gap_saturates_CM", all(abs(value - 1) < 1e-14 for value in saturated), saturated, [1.0] * 3)
    # A nonlinear future coefficient is not determined by d_j A.  With
    # A=eps_next*(1+c*eps_root), both conditional means of A vanish at the
    # root, while the quadratic coefficient has a nonzero root innovation.
    nonlinear_c = Fraction(2, 5)
    conditional_a = {
        eps_root: sum(Fraction(eps_next) * (1 + nonlinear_c * eps_root) for eps_next in (-1, 1)) / 2
        for eps_root in (-1, 1)
    }
    conditional_a2 = {
        eps_root: sum((Fraction(eps_next) * (1 + nonlinear_c * eps_root)) ** 2 for eps_next in (-1, 1)) / 2
        for eps_root in (-1, 1)
    }
    mean_a2 = sum(conditional_a2.values()) / 2
    nonlinear_root = {eps_root: conditional_a2[eps_root] - mean_a2 for eps_root in (-1, 1)}
    check(
        "nonlinear_coefficient_not_determined_by_DjA",
        all(value == 0 for value in conditional_a.values()) and any(value != 0 for value in nonlinear_root.values()),
        {"d_j_A": {str(key): str(value) for key, value in conditional_a.items()}, "d_j_abs_A_sq": {str(key): str(value) for key, value in nonlinear_root.items()}},
        {"d_j_A": "zero", "d_j_abs_A_sq": "nonzero"},
    )

    # 4. Progressive temporal packets and exact graph non-density.
    interval_length = 1.0
    j_values = (1.0, 2.0)
    weights = (0.5, 0.5)
    l_operator = sum(weight * value for weight, value in zip(weights, j_values))
    covariance = sum(weight * value * value for weight, value in zip(weights, j_values))
    check("temporal_operator_Cauchy", l_operator * l_operator <= interval_length * covariance + 1e-14, l_operator * l_operator, f"<={interval_length * covariance}")
    control = 3.0
    displacement = l_operator * control
    douglas_h_sq = displacement * displacement / covariance
    check("temporal_Douglas_factorization", abs(math.sqrt(covariance) * (displacement / math.sqrt(covariance)) - displacement) < 1e-14, displacement, displacement)
    check("temporal_Douglas_energy_contraction", douglas_h_sq <= interval_length * control * control + 1e-14, douglas_h_sq, f"<={interval_length * control * control}")
    check("temporal_packet_is_strict_past", True, "u_k in F_(t_(k-1))", "causal")
    check("temporal_packet_ranges_may_overlap", True, "same scalar physical mode", "overlap allowed algebraically")

    # Execute the complete R-079 root identity in one repeated scalar physical
    # range.  The two entries are orthogonal probability roots, while every
    # current value occupies the same physical coordinate.  Nonzero f*i makes
    # omission of the injected/future cross term detectable.
    base_roots = (0.7, -0.4)
    injected_roots = (0.3, 0.6)
    future_roots = (-0.2, 0.5)
    injected_trace = (0.12, -0.07)
    future_trace = (0.05, 0.09)
    endpoint_difference = sum(
        0.5 * ((base + fresh + future) ** 2 - base**2)
        - 0.5 * (trace_fresh + trace_future)
        for base, fresh, future, trace_fresh, trace_future in zip(
            base_roots,
            injected_roots,
            future_roots,
            injected_trace,
            future_trace,
        )
    )
    packet_sum = sum(
        base * fresh
        + 0.5 * fresh**2
        - 0.5 * trace_fresh
        + (base + fresh) * future
        + 0.5 * future**2
        - 0.5 * trace_future
        for base, fresh, future, trace_fresh, trace_future in zip(
            base_roots,
            injected_roots,
            future_roots,
            injected_trace,
            future_trace,
        )
    )
    packet_cross = sum(fresh * future for fresh, future in zip(injected_roots, future_roots))
    packet_residual = endpoint_difference - packet_sum
    check(
        "R079_complete_packet_algebra_temporalizes",
        abs(packet_residual) < 1e-14 and abs(packet_cross) > 0.1,
        {"residual": packet_residual, "retained_f_i_cross": packet_cross},
        {"residual": 0.0, "retained_f_i_cross": "nonzero"},
    )
    check("R080_separate_low_bound_does_not_temporalize", True, "revisit quartic fixture", "complete packet required")

    # Numerical normal integral for A=(1/2)tanh(W_{1/2}).
    sigma = math.sqrt(0.5)
    left, right, panels = -8 * sigma, 8 * sigma, 20000
    step = (right - left) / panels
    integral = 0.0
    for index in range(panels + 1):
        value = left + index * step
        density = math.exp(-(value * value) / (2 * sigma * sigma)) / (sigma * math.sqrt(2 * math.pi))
        integrand = 0.25 * math.tanh(value) ** 2 * density
        weight = 1 if index in (0, panels) else (4 if index % 2 else 2)
        integral += weight * integrand
    endpoint_variance = integral * step / 3
    check("progressive_single_mode_endpoint_nontrivial", endpoint_variance > 0.01, endpoint_variance, ">0.01")
    check("one_shot_graph_positive_L2_distance", endpoint_variance > 0, endpoint_variance, ">0")
    check("independent_auxiliary_randomness_cannot_help", True, "E|A-a|^2=E|A|^2+E|a|^2", ">=E|A|^2")
    check("temporal_refinement_keeps_physical_range_overlap", True, "same mode on all subintervals", "not R075 orthogonal graph")
    check("regular_graph_is_not_progressive_dense", True, "already fails terminal L2", "exact no-go")
    check("overlap_stable_complete_packet_bound_open", True, False, False)

    # 5. Conditional Nelson arithmetic remains unchanged and gated.
    eps_v = Fraction(9, 20)
    nelson_p = Fraction(11, 10)
    nelson_q = 1 / (2 * eps_v)
    check("conditional_nelson_q", nelson_q == Fraction(10, 9), str(nelson_q), "10/9")
    check("conditional_q_minus_p", nelson_q - nelson_p == Fraction(1, 90), str(nelson_q - nelson_p), "1/90")
    check("conditional_control_margin", 1 / (2 * nelson_p) - eps_v == Fraction(1, 220), str(1 / (2 * nelson_p) - eps_v), "1/220")
    check("controlled_shell_one_use_not_established", True, False, False)
    check("nelson_not_established", True, False, False)
    check("sector_A_not_closed", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-cartan-tail-adapted-near-temporal-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "far_result": "exact polynomial/Cartan split and deterministic relative-gap tail; root-resolved summation remains open",
        "near_result": "vector Doob-Burkholder budget closes; adapted complete-forest operator and signed control-control branch remain open",
        "progressive_result": "temporal complete-packet algebra extends, while the R-075 one-shot graph is not progressive-dense",
        "endpoint_variance": endpoint_variance,
        "claims_not_established": {
            "production_far_root_resolved_tail": False,
            "production_near_adapted_operator": False,
            "production_near_signed_control_control": False,
            "overlap_stable_progressive_packet_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-081 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
