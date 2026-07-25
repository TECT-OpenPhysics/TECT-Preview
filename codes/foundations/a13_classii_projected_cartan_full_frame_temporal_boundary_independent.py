#!/usr/bin/env python3
"""Non-importing independent audit for R-091.

This route shares no code with the primary executable.  It reconstructs the
output-gap inequality from random nonnegative arrays, evaluates the saturated
scalar Fourier series and arbitrary-gap first variation by high-precision
quadrature, measures the rare-fixture asymptotic, checks the full-frame Schur
and Jensen identities on finite conditional ensembles, integrates the local
Gaussian sign fixture, and audits terminal nonduplication numerically.
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


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PROJECTED-CARTAN-FULL-FRAME-SCHUR-JENSEN-TEMPORAL-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-projected-cartan-full-frame-temporal-boundary/result.json"


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
    if isinstance(value, mp.mpf):
        return mp.nstr(value, 40)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def gaussian_density(value: mp.mpf) -> mp.mpf:
    return mp.exp(-value * value / 2) / mp.sqrt(2 * mp.pi)


def scalar_tail(amplitude: mp.mpf, carrier: int, start: int) -> mp.mpf:
    d = mp.sqrt(1 + amplitude * amplitude)
    rho = (d - 1) / (d + 1)
    u = 2 * amplitude / (d * (d + 1))
    x = rho * rho
    polynomial_sum = x**start * (
        (2 * start + 1) ** 2 / (1 - x)
        + 4 * (2 * start + 1) * x / (1 - x) ** 2
        + 4 * x * (1 + x) / (1 - x) ** 3
    )
    return mp.mpf(carrier) ** 2 * u * u * polynomial_sum / 2


def main() -> int:
    mp.mp.dps = 70
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    # 1. Independent authority and output-gap checks.
    authority = {
        "r087": (
            CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt",
            ("C_0=5", "expectation", "one-use obstruction"),
        ),
        "r090": (
            CLAIM_DIR / "notes/classii-global-unprojected-cartan-ledger-nogo-rational-forest-boundary-260725-v1.0.tex.txt",
            ("exact one-coefficient identity", "full endpoint", "progressive assembly"),
        ),
    }
    for label, (path, tokens) in authority.items():
        text = path.read_text(encoding="utf-8")
        check(f"independent_authority_{label}", all(token in text for token in tokens), [token for token in tokens if token in text], list(tokens))

    random = np.random.default_rng(91091)
    gap_residuals: list[float] = []
    for gamma in (1 / 3, 7 / 12, 3 / 4):
        for _ in range(20):
            energies = random.lognormal(mean=0.0, sigma=1.2, size=31)
            offsets = np.arange(5, 36)
            weighted = float(np.sum(2.0 ** (2 * gamma * (offsets - 5)) * energies))
            for gap in (5, 6, 9, 14, 25):
                tail = float(np.sum(energies[offsets >= gap]))
                upper = 2.0 ** (-2 * gamma * (gap - 5)) * weighted
                gap_residuals.append(tail - upper)
    check("independent_output_gap_ledger", max(gap_residuals) <= 2e-10, max(gap_residuals), "<=2e-10 numerical residual")

    alpha = Fraction(2, 5)
    gamma = Fraction(7, 12)
    margins = (4 * alpha - 2 * gamma, 6 * alpha - 2 * gamma)
    check("independent_weighted_margins", margins == (Fraction(13, 30), Fraction(37, 30)), margins, (Fraction(13, 30), Fraction(37, 30)))
    rare_value_power = -6 - (6 * alpha - 1) + 6 * (1 + alpha) + 2
    rare_derivative_power = -6 - (6 * alpha + 1) + 6 * (1 + alpha) + 4
    check("independent_z6_rare_powers", (rare_value_power, rare_derivative_power) == (3, 3), (rare_value_power, rare_derivative_power), (3, 3))

    # 2. Direct Fourier quadrature of the saturated scalar production map.
    scalar_coefficient_errors: list[mp.mpf] = []
    scalar_tail_errors: list[mp.mpf] = []
    for amplitude in (mp.mpf("0.6"), mp.mpf("2.5"), mp.mpf("9.0")):
        d = mp.sqrt(1 + amplitude * amplitude)
        rho = (d - 1) / (d + 1)
        u = 2 * amplitude / (d * (d + 1))

        def production(theta: mp.mpf) -> mp.mpf:
            value = amplitude * mp.cos(theta)
            return value**3 / (1 + value**2)

        for k in range(1, 7):
            frequency = 2 * k + 1
            coefficient = mp.quad(
                lambda theta: production(theta) * mp.cos(frequency * theta),
                [-mp.pi, 0, mp.pi],
            ) / mp.pi
            predicted = -u * (-rho) ** k
            scalar_coefficient_errors.append(abs(coefficient - predicted))

        start = 3
        exact = scalar_tail(amplitude, 1, start)
        partial = u * u / 2 * mp.fsum(
            (2 * k + 1) ** 2 * rho ** (2 * k) for k in range(start, 20000)
        )
        scalar_tail_errors.append(abs(exact - partial))
    check("independent_scalar_fourier_coefficients", max(scalar_coefficient_errors) < mp.mpf("1e-30"), max(scalar_coefficient_errors), "<1e-30")
    check("independent_scalar_tail_closed_form", max(scalar_tail_errors) < mp.mpf("2e-55"), max(scalar_tail_errors), "<2e-55")

    # The rare fixture is repaired by the exact scalar tail: its fixed-gap
    # expected trace has slope -4, unlike the extracted Z^6 majorant's +3.
    rare_levels = (64, 128, 256, 512, 1024, 2048, 4096)
    rare_values: list[mp.mpf] = []
    for level in rare_levels:
        probability = mp.mpf(level) ** -6
        root_value_mass = mp.mpf(level) ** -1
        rare_values.append(probability * root_value_mass * scalar_tail(mp.mpf(level), level, 3))
    rare_slopes = [mp.log(rare_values[index + 1] / rare_values[index], 2) for index in range(len(rare_values) - 1)]
    check("independent_scalar_rare_tail_decreases", all(rare_values[index + 1] < rare_values[index] for index in range(len(rare_values) - 1)), rare_values, "strictly decreasing")
    check("independent_scalar_rare_tail_slope_minus_four", abs(rare_slopes[-1] + 4) < mp.mpf("3e-6"), rare_slopes[-1], "within 3e-6 of -4")

    # 3. Arbitrary-gap first variation reconstructed by quadrature.
    r = 3 - 2 * mp.sqrt(2)

    def first_variation(theta: mp.mpf) -> mp.mpf:
        cosine = mp.cos(theta)
        return cosine**4 * (3 + cosine**2) / (1 + cosine**2) ** 2

    harmonic_errors: list[mp.mpf] = []
    harmonic_values: dict[str, str] = {}
    for index in range(2, 13):
        coefficient = mp.quad(
            lambda theta: first_variation(theta) * mp.cos(2 * index * theta),
            [-mp.pi, 0, mp.pi],
        ) / mp.pi
        predicted = (-r) ** index * (2 * index - 3 * mp.sqrt(2) / 2)
        harmonic_errors.append(abs(coefficient - predicted))
        harmonic_values[str(index)] = mp.nstr(coefficient, 35)
    check("independent_first_variation_harmonics", max(harmonic_errors) < mp.mpf("2e-61"), max(harmonic_errors), "<2e-61")
    check("independent_every_tested_gap_nonzero", all(abs(mp.mpf(value)) > mp.mpf("1e-20") for value in harmonic_values.values()), harmonic_values, "all nonzero")

    rho = r * r
    tail_ratios: list[mp.mpf] = []
    C_rho = (1 + 11 * rho + 11 * rho**2 + rho**3) / (1 - rho) ** 5
    for start in (2, 3, 5, 8, 16):
        exact = mp.fsum(
            ((2 * index) * ((-r) ** index * (2 * index - 3 * mp.sqrt(2) / 2))) ** 2 / 2
            for index in range(start, 2000)
        )
        upper = 8 * C_rho * start**4 * rho**start
        tail_ratios.append(exact / upper)
    check("independent_first_variation_tail_bound", max(tail_ratios) < 1, tail_ratios, "all <1")

    # A three-dimensional max-norm q-shift audit at the safe gap.
    q_ratios: list[float] = []
    for _ in range(500):
        root = random.integers(-64, 65, size=3)
        coefficient = random.integers(-2048, 2049, size=3)
        axis = int(random.integers(0, 3))
        coefficient[axis] = int(random.choice((-2048, 2048)))
        output = coefficient + root
        q_ratios.append(float(output @ output) / float(np.max(np.abs(coefficient)) ** 2))
    lower = (1 - 1 / 32) ** 2
    upper = 3 * (1 + 1 / 32) ** 2
    check("independent_q_shift_lower", min(q_ratios) >= lower - 1e-14, min(q_ratios), f">={lower}")
    check("independent_q_shift_upper", max(q_ratios) <= upper + 1e-14, max(q_ratios), f"<={upper}")

    # 4. Conditional full-frame and same-root Jensen identities on finite
    # ensembles, independent of the primary symbolic derivation.
    schur_residuals: list[float] = []
    stationarity_residuals: list[float] = []
    jensen_residuals: list[float] = []
    for _ in range(30):
        sample_count = 9
        dimension = 3
        weights = random.uniform(0.1, 1.0, size=sample_count)
        weights /= weights.sum()
        samples = random.normal(size=(sample_count, dimension))
        mean = np.einsum("s,si->i", weights, samples)
        centered = samples - mean
        variance = np.einsum("s,si,sj->ij", weights, centered, centered)
        raw0 = random.normal(size=(dimension, dimension))
        raw1 = random.normal(size=(dimension, dimension))
        B0 = raw0.T @ raw0 + 0.4 * np.eye(dimension)
        B1 = raw1.T @ raw1 + 0.3 * np.eye(dimension)
        D = B1 - B0
        gamma_matrix = random.normal(size=(dimension, dimension))
        Gamma = gamma_matrix.T @ gamma_matrix
        c = random.normal(size=dimension)
        direct = 0.0
        for weight, vector in zip(weights, samples):
            direct += weight * (
                0.5 * np.sum(D * (np.outer(vector, vector) - Gamma))
                + vector @ B1 @ c
                + 0.5 * c @ B1 @ c
            )
        completed = 0.5 * (c + mean) @ B1 @ (c + mean) - 0.5 * mean @ B0 @ mean + 0.5 * np.sum(D * (variance - Gamma))
        schur_residuals.append(abs(float(direct - completed)))

        eta = float(random.uniform(0.2, 1.7))
        A = B1 + 2 * eta * np.eye(dimension)
        cstar = -np.linalg.solve(A, B1 @ mean)
        stationarity_residuals.append(float(np.linalg.norm(A @ cstar + B1 @ mean)))

        # Random same-root coefficients.  C is deliberately nonsymmetric to
        # catch the transpose in h=C_hat^T mu+r_C.
        C = random.normal(size=(sample_count, dimension, dimension))
        D_samples = random.normal(size=(sample_count, dimension, dimension))
        D_samples = 0.5 * (D_samples + np.swapaxes(D_samples, 1, 2))
        rawB = random.normal(size=(sample_count, dimension, dimension))
        B_samples = np.einsum("sji,sjk->sik", rawB, rawB) + 0.6 * np.eye(dimension)[None, :, :]
        hatC = np.einsum("s,sij->ij", weights, C)
        hatD = np.einsum("s,sij->ij", weights, D_samples)
        hatB = np.einsum("s,sij->ij", weights, B_samples)
        rC = np.einsum("s,sji,sj->i", weights, C - hatC, centered)
        h = hatC.T @ mean + rC
        centered_quadratic = np.einsum("si,sj->sij", samples, samples) - (variance + np.outer(mean, mean))[None, :, :]
        JD = 0.5 * np.einsum("s,sij,sij", weights, D_samples - hatD, centered_quadratic)
        direct_random = 0.0
        for sample in range(sample_count):
            direct_random += weights[sample] * (
                0.5 * np.sum(D_samples[sample] * (np.outer(samples[sample], samples[sample]) - Gamma))
                + samples[sample] @ C[sample] @ c
                + 0.5 * c @ B_samples[sample] @ c
                + eta * (c @ c)
            )
        AJ = hatB + 2 * eta * np.eye(dimension)
        shift = np.linalg.solve(AJ, h)
        completed_random = (
            0.5 * (c + shift) @ AJ @ (c + shift)
            + 0.5 * mean @ hatD @ mean
            + 0.5 * np.sum(hatD * (variance - Gamma))
            + JD
            - 0.5 * h @ shift
        )
        jensen_residuals.append(abs(float(direct_random - completed_random)))
    check("independent_conditional_full_frame", max(schur_residuals) < 4e-12, max(schur_residuals), "<4e-12")
    check("independent_schur_stationarity", max(stationarity_residuals) < 2e-14, max(stationarity_residuals), "<2e-14")
    check("independent_same_root_jensen", max(jensen_residuals) < 5e-12, max(jensen_residuals), "<5e-12")

    # No fixed eta can force universal positivity: a scalar B0 larger than
    # 2 eta beats the maximal positive Schur term.
    positivity_failures: list[float] = []
    for eta in (0.1, 0.5, 2.0, 10.0):
        B1 = 1.0 + eta
        B0 = 2.0 * eta + 1.0
        residual = 2.0 * eta * B1 / (B1 + 2.0 * eta) - B0
        positivity_failures.append(residual)
    check("independent_fixed_eta_positivity_fails", max(positivity_failures) < 0, positivity_failures, "all negative")

    # 5. High-precision Gaussian integration of the complete local frame.
    floor = mp.mpf("1")
    P = mp.mpf(4) + mp.mpf("1e-12")
    c0 = mp.mpf(3) / (250 * P)
    c1 = mp.mpf(243) / (8000 * P)
    root_floor = mp.sqrt(floor)

    def frame(value: mp.mpf) -> mp.mpf:
        rational = value - mp.mpf(5) / 9 * value**3 / (value**2 + floor)
        return 4 * c0 * value**2 + 4 * c1 * rational**2

    base = frame(root_floor)

    def integrand(g: mp.mpf, shifted: mp.mpf) -> mp.mpf:
        return mp.mpf("0.5") * (frame(shifted) - base) * (g * g - 1) * gaussian_density(g)

    integrated_loss = (
        mp.quad(lambda g: integrand(g, root_floor / 2), [-mp.inf, -1])
        + mp.quad(lambda g: integrand(g, 3 * root_floor / 2), [-1, 1])
        + mp.quad(lambda g: integrand(g, root_floor / 2), [1, mp.inf])
    )
    exact_loss = -mp.mpf(3708) / (mp.mpf(21125) * P) * gaussian_density(mp.mpf(1)) * floor
    check("independent_local_full_frame_quadrature", abs(integrated_loss - exact_loss) < mp.mpf("2e-65"), integrated_loss, exact_loss)
    check("independent_local_full_frame_negative", integrated_loss < 0, integrated_loss, "<0")

    # 6. Terminal split and complete future cross, sampled independently.
    terminal_residuals: list[float] = []
    temporal_residuals: list[float] = []
    omitted_crosses: list[float] = []
    for _ in range(100):
        high0, high1, low0, low1 = random.normal(size=4)
        endpoint = (high1 + low1) - (high0 + low0)
        terminal_residuals.append(abs(high0 + endpoint - (low1 - low0) - high1))
        w, fresh, future = random.normal(size=3)
        full = ((w + fresh + future) ** 2 - w**2) / 2
        packet = w * fresh + fresh**2 / 2 + (w + fresh) * future + future**2 / 2
        omitted = w * fresh + fresh**2 / 2 + w * future + future**2 / 2
        temporal_residuals.append(abs(full - packet))
        omitted_crosses.append(abs((full - omitted) - fresh * future))
    check("independent_terminal_nonduplication", max(terminal_residuals) < 2e-15, max(terminal_residuals), "<2e-15")
    check("independent_complete_future_cross", max(temporal_residuals) < 2e-15, max(temporal_residuals), "<2e-15")
    check("independent_omitted_cross_residual", max(omitted_crosses) < 5e-15, max(omitted_crosses), "<5e-15")

    unproved = {
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
    check("independent_no_overclaim", not any(unproved.values()), unproved, "all false")

    passed = sum(row["status"] == "PASS" for row in assertions)
    payload = {
        "schema": "tect/a13-projected-cartan-full-frame-temporal-boundary-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(assertions) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(assertions),
        "assertions": assertions,
        "scalar": {
            "maximum_coefficient_error": serial(max(scalar_coefficient_errors)),
            "maximum_tail_error": serial(max(scalar_tail_errors)),
            "rare_levels": list(rare_levels),
            "rare_values": serial(rare_values),
            "rare_log2_slopes": serial(rare_slopes),
            "first_variation_harmonics": harmonic_values,
            "first_variation_tail_ratios": serial(tail_ratios),
        },
        "full_frame": {
            "maximum_conditional_residual": max(schur_residuals),
            "maximum_stationarity_residual": max(stationarity_residuals),
            "maximum_jensen_residual": max(jensen_residuals),
            "fixed_eta_schur_examples": positivity_failures,
            "local_quadrature": serial(integrated_loss),
            "local_exact": serial(exact_loss),
        },
        "unproved": unproved,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-091 independent] {passed}/{len(assertions)} PASS")
        return 0
    failed = [row["name"] for row in assertions if row["status"] != "PASS"]
    print(f"[R-091 independent] {passed}/{len(assertions)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
