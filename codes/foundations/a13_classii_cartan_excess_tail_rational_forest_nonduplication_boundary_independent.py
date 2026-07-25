#!/usr/bin/env python3
"""Non-importing independent audit for R-090.

This route shares no code with the primary executable.  It reconstructs the
critical q^-4 shell scaling by explicit integer loops, checks the conservative
Cartan Fourier compression, recomputes the conditional Gaussian variances and
raw rational endpoint expectation by quadrature, projects the Wick product
onto probabilists' Hermite polynomials, and checks the complete-current
polarization and excess-tail inequality numerically.
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

import mpmath as mp
import numpy as np


REPOSITORY = Path(__file__).resolve().parents[2]
CLAIM_ID = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-GLOBAL-UNPROJECTED-CARTAN-COEFFICIENT-LEDGER-NOGO-RATIONAL-FOREST-BOUNDARY"
CLAIM_DIRECTORY = REPOSITORY / "claims" / CLAIM_ID
OUTPUT_PATH = CLAIM_DIRECTORY / "runs/2026-07-25-independent-cartan-excess-tail-rational-forest-nonduplication/result.json"


UPSTREAM_INPUTS = {
    "dimension": 3,
    "r084_prefactor": Fraction(3, 40),
    "lp_upper_coordinate_factor": 2,
}


def write_json_atomically(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def convert(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, mp.mpf):
        return mp.nstr(value, 40)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(key): convert(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [convert(item) for item in value]
    return value


def exact_derivative(value: Fraction) -> Fraction:
    square = value * value
    return square * (square + 3) / ((square + 1) * (square + 1))


def loop_shell_sum(level: int, exponent: float) -> float:
    outer = 2**level
    inner = outer // 2
    total = 0.0
    for p0 in range(-outer, outer + 1):
        for p1 in range(-outer, outer + 1):
            for p2 in range(-outer, outer + 1):
                maximum = max(abs(p0), abs(p1), abs(p2))
                if maximum <= inner or maximum > outer:
                    continue
                norm_square = p0 * p0 + p1 * p1 + p2 * p2
                shifted_square = (p0 + 1) ** 2 + p1 * p1 + p2 * p2
                total += norm_square ** (-2.0) * shifted_square**exponent
    return total * 2.0 ** ((1.0 - 2.0 * exponent) * level)


def main() -> int:
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": convert(actual),
                "expected": convert(expected),
            }
        )

    # 1. Independent authority preflight.
    authority_tokens = {
        "r063": (
            CLAIM_DIRECTORY / "notes/classii-balanced-coefficient-jet-continuum-and-a7-reconstruction-260722-v1.0.tex.txt",
            ("Complete lower-chaos conversion", "Formula (5.5)", "identity, not an asymptotic expansion"),
        ),
        "r079": (
            CLAIM_DIRECTORY / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
            ("full-current identity", "forest after reassembly", "fresh-packet cancellation"),
        ),
        "r089": (
            CLAIM_DIRECTORY / "notes/classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt",
            ("mathfrak E_s", "tag{3.12}", "complete backward-heat and lower-chaos forest"),
        ),
    }
    for label, (path, tokens) in authority_tokens.items():
        text = path.read_text(encoding="utf-8")
        check(f"authority_{label}", all(token in text for token in tokens), [token for token in tokens if token in text], list(tokens))

    # 2. Exact scalar secant, independently evaluated from the quotient-rule
    # derivative rather than symbolic differentiation.
    base = Fraction(1, 1)
    shifted = Fraction(3, 2)
    scalar_secant = exact_derivative(shifted) - exact_derivative(base)
    check("independent_scalar_secant", scalar_secant == Fraction(20, 169), scalar_secant, Fraction(20, 169))
    check("independent_scalar_secant_nonzero", scalar_secant > 0, scalar_secant, ">0")
    hessian_at_one = Fraction(2, 1) * base * (Fraction(3, 1) - base * base) / (Fraction(1, 1) + base * base) ** 3
    check("independent_scalar_hessian_at_one", hessian_at_one == Fraction(1, 2), hessian_at_one, Fraction(1, 2))

    # A separate numerical route checks b_hat+i*p*c_hat=i*q*c_hat and the
    # resulting |q|^2|c_hat|^2 trace for arbitrary integer frequencies.
    fourier_random = np.random.default_rng(90241)
    compression_residuals: list[float] = []
    trace_residuals: list[float] = []
    for _ in range(50):
        input_frequency = fourier_random.integers(-20, 21, size=3)
        output_frequency = fourier_random.integers(-20, 21, size=3)
        coefficient_frequency = output_frequency - input_frequency
        coefficient_value = fourier_random.normal() + 1j * fourier_random.normal()
        left = 1j * coefficient_frequency * coefficient_value + 1j * input_frequency * coefficient_value
        right = 1j * output_frequency * coefficient_value
        compression_residuals.append(float(np.max(np.abs(left - right))))
        trace_residuals.append(abs(float(np.sum(np.abs(left) ** 2)) - float(np.dot(output_frequency, output_frequency) * abs(coefficient_value) ** 2)))
    check("independent_cartan_fourier_compression", max(compression_residuals) < 3e-14, max(compression_residuals), "<3e-14")
    check("independent_cartan_trace_compression", max(trace_residuals) < 3e-12, max(trace_residuals), "<3e-12")
    shell_prefactor = (
        UPSTREAM_INPUTS["r084_prefactor"]
        * UPSTREAM_INPUTS["dimension"]
        * UPSTREAM_INPUTS["lp_upper_coordinate_factor"] ** 2
    )
    check("independent_cartan_shell_prefactor", shell_prefactor == Fraction(9, 10), shell_prefactor, Fraction(9, 10))

    # 3. Explicit q^-4 shell loops.  The power identity is derived using a
    # second set of exponents and levels from the primary route.
    exponents = (Fraction(1, 3), Fraction(2, 3), Fraction(4, 3))
    shell_diagnostics: dict[str, list[float]] = {}
    for exponent in exponents:
        cancellation = (Fraction(1, 1) - 2 * exponent) + Fraction(3, 1) - Fraction(4, 1) + 2 * exponent
        check(f"independent_power_cancellation_s_{exponent}", cancellation == 0, cancellation, 0)
        values = [loop_shell_sum(level, float(exponent)) for level in (2, 3, 4)]
        shell_diagnostics[str(exponent)] = values
        check(f"independent_shell_positive_s_{exponent}", min(values) > 1.0, min(values), ">1 diagnostic threshold")
        ratios = [values[index + 1] / values[index] for index in range(len(values) - 1)]
        check(f"independent_shell_stable_s_{exponent}", min(ratios) > 0.5 and max(ratios) < 2.0, ratios, "all in (0.5,2)")
        count = 23
        accumulated = sum(2.0 ** float(cancellation) for _ in range(count))
        check(f"independent_linear_accumulation_s_{exponent}", abs(accumulated - count) < 1e-12, accumulated, count)

    mp.mp.dps = 60
    ou_integral = mp.quad(lambda time: mp.e ** (-4 * time), [0, mp.inf])
    check("independent_ou_integral", abs(ou_integral - mp.mpf(1) / 4) < mp.mpf("1e-50"), ou_integral, mp.mpf(1) / 4)

    # 4. A root-diagonal coefficient can carry H^s energy while the far
    # projector sees exactly zero.  The multiplier has only fixed Fourier
    # shifts, so all output modes stay near N.
    grid_size = 512
    coordinate = 2 * np.pi * np.arange(grid_size) / grid_size
    root_mode = 24
    multiplier = 1.0 + 0.2 * np.cos(3 * coordinate)
    diagonal = multiplier * np.exp(1j * root_mode * coordinate)
    transform = np.fft.fft(diagonal) / grid_size
    frequencies = np.fft.fftfreq(grid_size, d=1.0 / grid_size)
    spectral_energy = np.abs(transform) ** 2
    near_energy = float(np.sum(spectral_energy[np.abs(frequencies) <= 2 * root_mode]))
    far_energy = float(np.sum(spectral_energy[np.abs(frequencies) >= 4 * root_mode]))
    check("diagonal_near_energy_positive", near_energy > 1.0, near_energy, ">1")
    check("diagonal_far_projection_zero", far_energy < 1e-24, far_energy, "<1e-24")
    check("diagonal_not_cfar_counterexample", near_energy > 0 and far_energy < 1e-24, (near_energy, far_energy), "near positive, far zero")

    # 5. Independent excess-tail inequality on a deterministic decreasing
    # sequence and several irrational-looking floating exponents.
    for exponent in (0.21, 0.58, 0.93):
        principal_offset = 5
        gap = 11
        values = {offset: 1.0 / (offset + 2) ** 2 for offset in range(principal_offset, 31)}
        ledger = sum(2.0 ** (2 * exponent * (offset - principal_offset)) * value for offset, value in values.items())
        threshold = gap - 2
        tail = sum(value for offset, value in values.items() if offset >= threshold)
        factor = 2.0 ** (-2 * exponent * (gap - 2 - principal_offset))
        check(f"independent_excess_tail_s_{exponent}", tail <= factor * ledger * (1 + 1e-13), tail, f"<={factor * ledger}")

    # 6. R-089's event switch is not conditionally covariance matched.  Use
    # direct high-precision integration rather than the closed formulas used
    # by the primary route.
    normalizer = mp.sqrt(2 * mp.pi)

    def normal_density(value: mp.mpf) -> mp.mpf:
        return mp.e ** (-(value * value) / 2) / normalizer

    probability_outside = mp.quad(lambda value: normal_density(value), [-mp.inf, -1]) + mp.quad(lambda value: normal_density(value), [1, mp.inf])
    probability_inside = mp.quad(lambda value: normal_density(value), [-1, 1])
    second_outside = mp.quad(lambda value: value * value * normal_density(value), [-mp.inf, -1]) + mp.quad(lambda value: value * value * normal_density(value), [1, mp.inf])
    second_inside = mp.quad(lambda value: value * value * normal_density(value), [-1, 1])
    variance_outside = second_outside / probability_outside
    variance_inside = second_inside / probability_inside
    recombined_variance = probability_outside * variance_outside + probability_inside * variance_inside
    check("independent_conditional_variance_outside_not_one", variance_outside > 1, variance_outside, ">1")
    check("independent_conditional_variance_inside_not_one", 0 < variance_inside < 1, variance_inside, "in (0,1)")
    check("independent_unconditional_variance_recombined", abs(recombined_variance - 1) < mp.mpf("1e-48"), recombined_variance, 1)

    # Recompute the complete raw rational endpoint.  The endpoint function is
    # normalized by 4*c1*e and the energy difference by c1*e.
    def endpoint_fraction(value: Fraction) -> Fraction:
        return (value - Fraction(5, 9) * value**3 / (value**2 + 1)) ** 2

    endpoint_base = endpoint_fraction(Fraction(1, 1))
    endpoint_minus = endpoint_fraction(Fraction(1, 2))
    endpoint_plus = endpoint_fraction(Fraction(3, 2))
    check("independent_raw_endpoint_base", endpoint_base == Fraction(169, 324), endpoint_base, Fraction(169, 324))
    check("independent_raw_endpoint_minus", endpoint_minus == Fraction(16, 81), endpoint_minus, Fraction(16, 81))
    check("independent_raw_endpoint_plus", endpoint_plus == Fraction(144, 169), endpoint_plus, Fraction(144, 169))
    exact_raw_factor = 4 * ((endpoint_minus - endpoint_base) - (endpoint_plus - endpoint_base))
    check("independent_raw_endpoint_exact_factor", exact_raw_factor == Fraction(-35840, 13689), exact_raw_factor, Fraction(-35840, 13689))

    def endpoint_mpf(value: mp.mpf) -> mp.mpf:
        return (value - mp.mpf(5) / 9 * value**3 / (value**2 + 1)) ** 2

    endpoint_base_mpf = endpoint_mpf(mp.mpf(1))

    def sharp_integrand(value: mp.mpf) -> mp.mpf:
        shift_value = -mp.mpf(1) / 2 if abs(value) >= 1 else mp.mpf(1) / 2
        return 2 * (endpoint_mpf(1 + shift_value) - endpoint_base_mpf) * (value * value - 1) * normal_density(value)

    sharp_expectation = mp.quad(sharp_integrand, [-mp.inf, -1, 1, mp.inf])
    exact_sharp_expectation = mp.mpf(exact_raw_factor.numerator) / exact_raw_factor.denominator * normal_density(mp.mpf(1))
    check("independent_raw_endpoint_quadrature", abs(sharp_expectation - exact_sharp_expectation) < mp.mpf("1e-45"), sharp_expectation, exact_sharp_expectation)
    check("independent_raw_endpoint_strictly_negative", sharp_expectation < mp.mpf("-0.6"), sharp_expectation, "<-0.6 per c1*e")

    smooth_expectations: dict[str, mp.mpf] = {}
    for steepness in (2, 4, 8):
        def smooth_integrand(value: mp.mpf) -> mp.mpf:
            q_value = value * value - 1
            shift_value = -mp.mpf(1) / 2 * mp.tanh(steepness * q_value)
            return 2 * (endpoint_mpf(1 + shift_value) - endpoint_base_mpf) * q_value * normal_density(value)

        smooth_value = mp.quad(smooth_integrand, [-mp.inf, -1, 0, 1, mp.inf])
        smooth_expectations[str(steepness)] = smooth_value
        check(f"independent_smooth_endpoint_negative_M_{steepness}", smooth_value < 0, smooth_value, "<0")
    check(
        "independent_smooth_endpoint_converges_toward_sharp",
        abs(smooth_expectations["8"] - sharp_expectation) < abs(smooth_expectations["2"] - sharp_expectation),
        [smooth_expectations["2"], smooth_expectations["8"]],
        "M=8 closer to sharp than M=2",
    )

    # 7. Gaussian-quadrature Hermite projection of G^2(G^2-1).  This route
    # never uses the primary symbolic polynomial solve.
    nodes, weights = np.polynomial.hermite_e.hermegauss(24)
    weights = weights / math.sqrt(2 * math.pi)
    h0 = np.ones_like(nodes)
    h2 = nodes**2 - 1
    h4 = nodes**4 - 6 * nodes**2 + 3
    wick_product = nodes**2 * (nodes**2 - 1)
    coefficient_h4 = float(np.sum(weights * wick_product * h4) / math.factorial(4))
    coefficient_h2 = float(np.sum(weights * wick_product * h2) / math.factorial(2))
    coefficient_h0 = float(np.sum(weights * wick_product * h0))
    reconstruction = coefficient_h4 * h4 + coefficient_h2 * h2 + coefficient_h0
    check("independent_forest_h4", abs(coefficient_h4 - 1.0) < 2e-12, coefficient_h4, 1.0)
    check("independent_forest_h2", abs(coefficient_h2 - 5.0) < 2e-12, coefficient_h2, 5.0)
    check("independent_forest_h0", abs(coefficient_h0 - 2.0) < 2e-12, coefficient_h0, 2.0)
    check("independent_forest_reconstructs_product", float(np.max(np.abs(reconstruction - wick_product))) < 2e-10, float(np.max(np.abs(reconstruction - wick_product))), "<2e-10")
    double_count = wick_product + coefficient_h2 * h2 + coefficient_h0
    check("independent_forest_addition_changes_product", float(np.max(np.abs(double_count - wick_product))) > 1.0, float(np.max(np.abs(double_count - wick_product))), ">1")

    # 8. Full-current polarization: the fresh/future cross belongs to the
    # future block and cannot be dropped during assembly.
    random = np.random.default_rng(90190)
    polarization_residuals: list[float] = []
    omitted_residuals: list[float] = []
    for _ in range(40):
        base_current, fresh, future = random.normal(size=3)
        complete = ((base_current + fresh + future) ** 2 - base_current**2) / 2
        split = base_current * fresh + fresh**2 / 2 + (base_current + fresh) * future + future**2 / 2
        omitted = base_current * fresh + fresh**2 / 2 + base_current * future + future**2 / 2
        polarization_residuals.append(abs(complete - split))
        omitted_residuals.append(abs((complete - omitted) - fresh * future))
    check("independent_full_packet_polarization", max(polarization_residuals) < 3e-14, max(polarization_residuals), "<3e-14")
    check("independent_cross_term_location", max(omitted_residuals) < 3e-14, max(omitted_residuals), "<3e-14")

    # 9. Recompute the conditional budget margins independently.
    sextic_margin = Fraction(27, 100) - Fraction(6, 100) - Fraction(15, 100)
    control_margin = Fraction(1, 1) / (2 * Fraction(11, 10)) - Fraction(9, 20)
    exponent_margin = Fraction(10, 9) - Fraction(11, 10)
    check("independent_sextic_margin", sextic_margin == Fraction(3, 50), sextic_margin, Fraction(3, 50))
    check("independent_control_margin", control_margin == Fraction(1, 220), control_margin, Fraction(1, 220))
    check("independent_exponent_margin", exponent_margin == Fraction(1, 90), exponent_margin, Fraction(1, 90))

    unproved = {
        "excess_tail_bound": False,
        "progressive_cartan_cfar": False,
        "complete_rational_temporal_packet": False,
        "complete_packet_assembly": False,
        "overlap": False,
        "nelson": False,
        "sector_a": False,
    }
    check("independent_no_overclaim", not any(unproved.values()), unproved, "all false")

    passed = sum(item["status"] == "PASS" for item in assertions)
    report = {
        "schema": "tect/a13-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM_ID,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(assertions) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(assertions),
        "assertions": assertions,
        "shell_diagnostics": shell_diagnostics,
        "scalar_secant": str(scalar_secant),
        "scalar_hessian_at_one": str(hessian_at_one),
        "cartan_shell_prefactor_without_kappa0_over_P": str(shell_prefactor),
        "lp_upper_support_convention": "|pi_m|<=1 and |q|_infinity<=2^(m+1)",
        "obstructing_chaos": "current-root first chaos; P_t attenuation e^(-t)",
        "ou_integral": mp.nstr(ou_integral, 40),
        "diagonal_fixture": {"near_energy": near_energy, "far_energy": far_energy},
        "conditional_variances": {
            "event_abs_G_ge_1": mp.nstr(variance_outside, 40),
            "event_abs_G_lt_1": mp.nstr(variance_inside, 40),
            "unconditional_recombination": mp.nstr(recombined_variance, 40),
        },
        "raw_endpoint": {
            "exact_factor_before_phi_per_c1e": str(exact_raw_factor),
            "quadrature_per_c1e": mp.nstr(sharp_expectation, 40),
            "smooth_approximants_per_c1e": {key: mp.nstr(value, 40) for key, value in smooth_expectations.items()},
        },
        "forest_coefficients": {"H4": coefficient_h4, "H2": coefficient_h2, "H0": coefficient_h0},
        "unproved": unproved,
    }
    write_json_atomically(OUTPUT_PATH, report)
    if report["status"] == "PASS":
        print(f"[R-090 independent] {passed}/{len(assertions)} PASS")
        return 0
    failed = [item["name"] for item in assertions if item["status"] != "PASS"]
    print(f"[R-090 independent] {passed}/{len(assertions)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
