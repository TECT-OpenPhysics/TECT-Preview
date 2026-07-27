#!/usr/bin/env python3
"""Non-importing independent audit for the R-094 A13 boundary."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.hermite import hermgauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ROOT-LOCAL-GRAM-SECANT-FEEDBACK-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-independent-root-local-gram-secant-feedback-boundary/result.json"


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


def standard_gaussian_expectation(values: np.ndarray, nodes: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(weights * values) / math.sqrt(math.pi))


def main() -> int:
    rows: list[dict[str, Any]] = []

    def record(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if isinstance(actual, np.generic):
            actual = actual.item()
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    # Alternative exact evaluation: sum the inner k-series first, then the
    # outer j-series.  This code shares no helper with the primary executable.
    quadratic_inner = Fraction(1, 15)
    quadratic_total = quadratic_inner / (1 - Fraction(1, 8))
    mixed_inner = Fraction(1, 15)
    mixed_total = mixed_inner / (1 - Fraction(1, 4))
    prefix_total = Fraction(2, 1) / (1 - Fraction(1, 8))
    record("independent_quadratic_kernel", quadratic_total == Fraction(8, 105), str(quadratic_total), "8/105")
    record("independent_mixed_kernel", mixed_total == Fraction(4, 45), str(mixed_total), "4/45")
    record("independent_prefix_kernel", prefix_total == Fraction(16, 7), str(prefix_total), "16/7")

    # Finite weighted-Hardy matrices: direct eigenvalue computation audits the
    # convolution proof without reusing it.
    hardy_bound = 3.0 + 2.0 * math.sqrt(2.0)
    hardy_norms: dict[str, float] = {}
    for length in (4, 8, 16, 32, 64, 96):
        operator = np.zeros((length, length), dtype=float)
        for j in range(length):
            for k in range(j + 1, length):
                operator[j, k] = 2.0 ** ((j - k) / 2.0)
        squared_norm = float(np.linalg.eigvalsh(operator.T @ operator)[-1])
        hardy_norms[str(length)] = squared_norm
        record(f"independent_hardy_matrix_{length}", squared_norm < hardy_bound, squared_norm, f"< {hardy_bound}")
    record(
        "independent_hardy_norm_monotone",
        all(hardy_norms[str(b)] > hardy_norms[str(a)] for a, b in zip((4, 8, 16, 32, 64), (8, 16, 32, 64, 96))),
        hardy_norms,
        "strict finite-section growth below the infinite bound",
    )

    # Independent Gaussian quadrature for the Hermite mixed-secant fixture.
    raw_nodes, weights = hermgauss(96)
    xi = math.sqrt(2.0) * raw_nodes
    h2 = xi * xi - 1.0
    h2_second = standard_gaussian_expectation(h2**2, raw_nodes, weights)
    h2_third = standard_gaussian_expectation(h2**3, raw_nodes, weights)
    record("independent_h2_second_quadrature", abs(h2_second - 2.0) < 1.0e-12, h2_second, 2.0)
    record("independent_h2_third_quadrature", abs(h2_third - 8.0) < 1.0e-11, h2_third, 8.0)
    fixture_rows: list[dict[str, float]] = []
    for gamma, epsilon, time_value, rho in (
        (1.0, 0.2, 0.7, 0.4),
        (0.5, 0.8, 0.3, 1.3),
        (3.0, 0.05, 2.0, 0.2),
    ):
        g2_centered = gamma * h2
        m1 = 1.0 - epsilon * time_value * h2
        numerical = 0.5 * standard_gaussian_expectation((m1 * m1 - 1.0) * g2_centered, raw_nodes, weights)
        formula = -2.0 * gamma * epsilon * time_value + 4.0 * gamma * epsilon * epsilon * time_value * time_value
        record(f"independent_mixed_fixture_{gamma}_{epsilon}_{time_value}", abs(numerical - formula) < 1.0e-11, numerical, formula)
        optimum_time = gamma * epsilon / (rho + 4.0 * gamma * epsilon * epsilon)
        optimum_value = (
            -2.0 * gamma * epsilon * optimum_time
            + (rho + 4.0 * gamma * epsilon * epsilon) * optimum_time * optimum_time
        )
        closed_value = -(gamma * gamma * epsilon * epsilon) / (rho + 4.0 * gamma * epsilon * epsilon)
        record(f"independent_mixed_minimum_{gamma}_{epsilon}_{rho}", abs(optimum_value - closed_value) < 1.0e-13, optimum_value, closed_value)
        fixture_rows.append({"gamma": gamma, "epsilon": epsilon, "rho": rho, "minimum": optimum_value})

    # Direct finite-prefix matrix check, including operator norm below the
    # Hilbert--Schmidt constant 16/7.
    prefix_norms: dict[str, float] = {}
    for length in (5, 12, 25, 50):
        matrix = np.zeros((length, length), dtype=float)
        for j in range(length):
            for k in range(j + 1):
                matrix[j, k] = 2.0 ** (-j / 2.0) * 2.0 ** (-k)
        operator_norm_squared = float(np.linalg.eigvalsh(matrix.T @ matrix)[-1])
        hilbert_schmidt_squared = float(np.sum(matrix * matrix))
        prefix_norms[str(length)] = operator_norm_squared
        record(f"independent_prefix_op_vs_hs_{length}", operator_norm_squared <= hilbert_schmidt_squared + 1.0e-13, operator_norm_squared, f"<= {hilbert_schmidt_squared}")
        record(f"independent_prefix_hs_bound_{length}", hilbert_schmidt_squared < 16.0 / 7.0, hilbert_schmidt_squared, "< 16/7")

    # Completing the square is checked through its exact residual identity,
    # not merely the inequality.
    rng = np.random.default_rng(9402701)
    maximum_completion_error = 0.0
    for index in range(40):
        x = rng.normal(size=7)
        y = rng.normal(size=7)
        p = rng.normal(size=7)
        u = rng.normal(size=7)
        theta = float(rng.uniform(0.02, 0.98))
        tau = float(rng.normal())
        left = float(x @ y + 0.5 * theta * (y @ y))
        lower = -float(x @ x) / (2.0 * theta)
        residual = 0.5 * theta * float((y + x / theta) @ (y + x / theta))
        completion_error = abs((left - lower) - residual)
        direct_packet = float((p + x) @ (u + y) + 0.5 * ((u + y) @ (u + y)) - tau)
        split_packet = float(
            (p + x) @ u
            + 0.5 * (u @ u)
            - tau
            + (p + u) @ y
            + 0.5 * (1.0 - theta) * (y @ y)
            + x @ y
            + 0.5 * theta * (y @ y)
        )
        split_error = abs(direct_packet - split_packet)
        error = max(completion_error, split_error)
        maximum_completion_error = max(maximum_completion_error, error)
        record(f"independent_completion_identity_{index}", error < 1.0e-11, error, "< 1e-11")

    # The centered secant proof uses product-space interpolation, audited on
    # deliberately spiky finite distributions.
    maximum_interpolation_ratio = 0.0
    for denominator in (8, 27, 64, 125, 216):
        values = np.zeros(denominator, dtype=float)
        values[0] = math.sqrt(float(denominator))
        values[1:] = 1.0 / float(denominator)
        n2 = float(np.mean(values**2) ** 0.5)
        n3 = float(np.mean(values**3) ** (1.0 / 3.0))
        n6 = float(np.mean(values**6) ** (1.0 / 6.0))
        ratio = n3 * n3 / (n2 * n6)
        maximum_interpolation_ratio = max(maximum_interpolation_ratio, ratio)
        record(f"independent_spiky_interpolation_{denominator}", ratio <= 1.0 + 1.0e-13, ratio, "<= 1")

    # Exact revisit scaling uses a normalized source mode and a separately
    # sampled nonzero smoothing image, so source and output norms cannot be
    # conflated.
    image_mode = np.array([1.0, -0.75, 0.5, -0.25, 0.125], dtype=float)
    image_mode_l6_sixth = float(np.mean(np.abs(image_mode) ** 6))
    revisit: list[dict[str, float]] = []
    for population in (16, 64, 256, 1024):
        event = np.zeros(population, dtype=float)
        event[0] = 1.0
        probability = 1.0 / population
        first_source = event / math.sqrt(probability)
        second_source = -first_source
        first_image = first_source[:, None] * image_mode[None, :]
        second_image = -first_image
        source_cost = float(np.mean(first_source**2 + second_source**2))
        sixth_sum = float(np.mean(np.abs(first_image) ** 6 + np.abs(second_image) ** 6))
        terminal_norm = float(np.max(np.abs(first_image + second_image)))
        expected_sixth_sum = 2.0 * image_mode_l6_sixth * population * population
        revisit.append({"population": population, "source_cost": source_cost, "image_mode_l6_sixth": image_mode_l6_sixth, "sixth_sum": sixth_sum})
        record(f"independent_revisit_cost_{population}", abs(source_cost - 2.0) < 1.0e-12, source_cost, 2.0)
        record(f"independent_revisit_terminal_{population}", terminal_norm == 0.0, terminal_norm, 0.0)
        record(f"independent_revisit_sixth_{population}", image_mode_l6_sixth > 0.0 and abs(sixth_sum - expected_sixth_sum) < 1.0e-7, sixth_sum, expected_sixth_sum)

    # Exact rational slack audit for the historical coarse rows and their
    # accepted sharp replacements.
    sharp_rows = {
        "a2_da": (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6), Fraction(6, 1)),
        "a3_da": (Fraction(2, 5), Fraction(8, 15), Fraction(1, 15), Fraction(15, 1)),
        "centered_secant": (Fraction(1, 2), Fraction(1, 6), Fraction(1, 3), Fraction(3, 1)),
    }
    for label, (a_power, b_power, expected_slack, expected_moment) in sharp_rows.items():
        slack = 1 - a_power - b_power
        record(f"independent_{label}_slack", slack == expected_slack, str(slack), str(expected_slack))
        record(f"independent_{label}_moment", 1 / slack == expected_moment, str(1 / slack), str(expected_moment))

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-root-local-gram-secant-feedback-boundary-independent/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "derived": {
            "hardy_finite_section_norms": hardy_norms,
            "prefix_finite_section_norms": prefix_norms,
            "maximum_completion_identity_error": maximum_completion_error,
            "maximum_spiky_interpolation_ratio": maximum_interpolation_ratio,
            "mixed_fixture_rows": fixture_rows,
            "revisit_rows": revisit,
        },
        "independence": {
            "imports_primary": False,
            "methods": [
                "direct finite-section eigenvalues",
                "Gauss-Hermite quadrature",
                "exact square residual",
                "discrete rare-event arrays",
            ],
        },
        "claims_not_established": [
            "complete_H_N",
            "REG",
            "OVERLAP_src",
            "Nelson",
            "Sector_A_closure",
        ],
    }
    atomic_json(OUTPUT, payload)
    print(
        f"R-094 INDEPENDENT {'PASS' if not failures else 'FAIL'}: "
        f"{len(rows) - len(failures)}/{len(rows)} assertions"
    )
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
