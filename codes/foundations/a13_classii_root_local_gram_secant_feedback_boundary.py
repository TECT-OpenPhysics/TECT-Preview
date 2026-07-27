#!/usr/bin/env python3
"""Primary executable evidence for the R-094 A13 root-local boundary.

The executable checks only the algebraic and numerical claims made by R-094:
the distinct dyadic kernels, weighted Hardy constant, mixed-secant scalar
witness, value/heat prefix cost, partial-square allocation, revisit fixture,
and the repaired Young-slack ledger.  It does not assert complete H_N, REG,
Nelson, or Sector-A closure.
"""

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


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ROOT-LOCAL-GRAM-SECANT-FEEDBACK-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-root-local-gram-secant-feedback-boundary/result.json"

AUTHORITIES = {
    "r074": CLAIM_DIR / "notes/classii-invariant-current-principal-oneform-graph-recovery-260724-v1.0.tex.txt",
    "r076": CLAIM_DIR / "notes/classii-signed-transport-besov-bregman-resonance-reduction-260724-v1.0.tex.txt",
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r086": CLAIM_DIR / "notes/classii-rational-translated-wick-payload-comparable-reduction-260725-v1.0.tex.txt",
    "r092": CLAIM_DIR / "notes/classii-normalized-cartan-perspective-triangular-covariance-frontier-260725-v1.0.tex.txt",
    "r093": CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt",
}

# These are independent exact test oracles.  They are never used to derive an
# output; every output is recomputed below from its defining series or moment.
TEST_ORACLES = {
    "quadratic_kernel": Fraction(8, 105),
    "mixed_square_kernel": Fraction(4, 45),
    "prefix_hilbert_schmidt": Fraction(16, 7),
    "hardy_constant_squared_form": "3 + 2*sqrt(2)",
    "h2_second_moment": 2,
    "h2_third_moment": 8,
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
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def geometric_sum(first: Fraction, ratio: Fraction) -> Fraction:
    return first / (1 - ratio)


def gaussian_even_moment(order: int) -> int:
    if order % 2:
        return 0
    value = 1
    for odd in range(1, order, 2):
        value *= odd
    return value


def generalized_young_constant(a: float, b: float, eta: float, zeta: float) -> float:
    slack = 1.0 - a - b
    if slack <= 0.0:
        raise ValueError("positive Young slack required")
    return slack * (a / eta) ** (a / slack) * (b / zeta) ** (b / slack)


def main() -> int:
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

    authority_tokens = {
        "r074": ("A^2DA", "eta^{-3}", "zeta^{-2}"),
        "r076": ("X^{2/5}Y^{8/15}", "positive Young slack $1/15$"),
        "r079": ("future-control commutator has two channels", "tag{5.2}", "tag{6.8}"),
        "r086": ("T_Q^>", "T_G^>", "tag{6.3}"),
        "r092": ("tag{10.10}", "weighted conditional-covariance deficit"),
        "r093": ("2^{j-4k}", "coarse critical current", "coarse graph term"),
    }
    for label, path in AUTHORITIES.items():
        check(f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(
            f"authority_{label}_tokens",
            all(token in content for token in tokens),
            [token for token in tokens if token in content],
            list(tokens),
        )

    # Exact infinite triangular sums, evaluated only from their geometric
    # definitions.  Setting j0=0 isolates the dimensionless constants.
    quadratic_kernel = geometric_sum(Fraction(1, 15), Fraction(1, 8))
    mixed_square_kernel = geometric_sum(Fraction(1, 15), Fraction(1, 4))
    prefix_hilbert_schmidt = 2 * geometric_sum(Fraction(1), Fraction(1, 8))
    check("quadratic_kernel_exact", quadratic_kernel == TEST_ORACLES["quadratic_kernel"], quadratic_kernel, TEST_ORACLES["quadratic_kernel"])
    check("mixed_square_kernel_exact", mixed_square_kernel == TEST_ORACLES["mixed_square_kernel"], mixed_square_kernel, TEST_ORACLES["mixed_square_kernel"])
    check("prefix_hilbert_schmidt_exact", prefix_hilbert_schmidt == TEST_ORACLES["prefix_hilbert_schmidt"], prefix_hilbert_schmidt, TEST_ORACLES["prefix_hilbert_schmidt"])

    for floor in (0, 1, 3, 6):
        finite_quadratic = sum(
            2.0 ** (j - 4 * k)
            for j in range(floor, floor + 48)
            for k in range(j + 1, floor + 64)
        )
        exact_quadratic = float(quadratic_kernel) * 2.0 ** (-3 * floor)
        check(
            f"quadratic_kernel_truncation_floor_{floor}",
            0.0 <= exact_quadratic - finite_quadratic < 1.0e-12,
            finite_quadratic,
            exact_quadratic,
        )
        finite_mixed = sum(
            2.0 ** (2 * j - 4 * k)
            for j in range(floor, floor + 48)
            for k in range(j + 1, floor + 64)
        )
        exact_mixed = float(mixed_square_kernel) * 2.0 ** (-2 * floor)
        check(
            f"mixed_kernel_truncation_floor_{floor}",
            0.0 <= exact_mixed - finite_mixed < 1.0e-12,
            finite_mixed,
            exact_mixed,
        )

    # The weighted Hardy operator becomes one-sided convolution with kernel
    # 2^{-n/2}; Young's l1 convolution norm is sqrt(2)+1.
    hardy_l1_float = sum(2.0 ** (-n / 2.0) for n in range(1, 240))
    hardy_exact = math.sqrt(2.0) + 1.0
    hardy_square = hardy_exact * hardy_exact
    check("hardy_l1_exact", abs(hardy_l1_float - hardy_exact) < 1.0e-14, hardy_l1_float, hardy_exact)
    check("hardy_square_identity", abs(hardy_square - (3.0 + 2.0 * math.sqrt(2.0))) < 1.0e-14, hardy_square, TEST_ORACLES["hardy_constant_squared_form"])
    rng = np.random.default_rng(94027)
    maximum_hardy_ratio = 0.0
    for length in (5, 11, 29, 61):
        for _ in range(8):
            b = rng.normal(size=length)
            left = sum(2.0**j * float(np.sum(b[j + 1 :])) ** 2 for j in range(length))
            right = sum(2.0**k * float(b[k]) ** 2 for k in range(length))
            ratio = 0.0 if right == 0.0 else left / right
            maximum_hardy_ratio = max(maximum_hardy_ratio, ratio)
            check(f"hardy_random_{length}_{_}", left <= hardy_square * right + 1.0e-10, ratio, f"<= {hardy_square}")

    # Product-space interpolation ||a||_3^2 <= ||a||_2 ||a||_6.
    maximum_interpolation_ratio = 0.0
    for index in range(24):
        sample = np.abs(rng.normal(size=257)) * np.exp(0.25 * rng.normal(size=257))
        norm2 = float(np.mean(sample**2) ** 0.5)
        norm3 = float(np.mean(sample**3) ** (1.0 / 3.0))
        norm6 = float(np.mean(sample**6) ** (1.0 / 6.0))
        ratio = norm3 * norm3 / (norm2 * norm6)
        maximum_interpolation_ratio = max(maximum_interpolation_ratio, ratio)
        check(f"l2_l6_interpolation_{index}", ratio <= 1.0 + 1.0e-12, ratio, "<= 1")

    # The Hermite fixture recomputes E H2^2 and E H2^3 from Gaussian moments.
    h2_second = gaussian_even_moment(4) - 2 * gaussian_even_moment(2) + 1
    h2_third = gaussian_even_moment(6) - 3 * gaussian_even_moment(4) + 3 * gaussian_even_moment(2) - 1
    check("hermite_h2_second", h2_second == TEST_ORACLES["h2_second_moment"], h2_second, TEST_ORACLES["h2_second_moment"])
    check("hermite_h2_third", h2_third == TEST_ORACLES["h2_third_moment"], h2_third, TEST_ORACLES["h2_third_moment"])
    for gamma, epsilon, rho in ((1.0, 0.2, 0.7), (2.5, 0.07, 0.1), (0.4, 0.9, 3.0)):
        linear = 2.0 * gamma * epsilon
        quadratic = rho + 4.0 * gamma * epsilon * epsilon
        minimizer = linear / (2.0 * quadratic)
        minimum = quadratic * minimizer * minimizer - linear * minimizer
        expected = -(gamma * gamma * epsilon * epsilon) / quadratic
        check(f"mixed_secant_minimum_{gamma}_{epsilon}_{rho}", abs(minimum - expected) < 1.0e-14, minimum, expected)
        check(f"mixed_secant_negative_{gamma}_{epsilon}_{rho}", minimum < 0.0, minimum, "< 0")

    # Pointwise PSD curvature lower bound: keep the positive square and bound
    # only the covariance trace.  E may be adapted; no independence is used.
    minimum_curvature_gap = math.inf
    for index in range(32):
        raw_q = rng.normal(size=(4, 4))
        q_metric = raw_q.T @ raw_q
        raw_gamma = rng.normal(size=(3, 3))
        covariance = raw_gamma.T @ raw_gamma
        increment = rng.normal(size=(3, 4))
        derivative = rng.normal(size=3)
        positive = float((increment.T @ derivative) @ q_metric @ (increment.T @ derivative))
        trace = float(np.trace((increment @ q_metric @ increment.T) @ covariance))
        atom = 0.5 * (positive - trace)
        lower = -0.5 * trace
        minimum_curvature_gap = min(minimum_curvature_gap, atom - lower)
        check(f"quadratic_curvature_psd_{index}", atom + 1.0e-12 >= lower, atom, f">= {lower}")

    # Exact partial-square allocation and the sign-indefinite leftover.
    minimum_partial_gap = math.inf
    for index in range(32):
        x = rng.normal(size=9)
        y = rng.normal(size=9)
        p = rng.normal(size=9)
        u = rng.normal(size=9)
        theta = float(rng.uniform(0.05, 0.95))
        tau = float(rng.normal())
        left = float(x @ y + 0.5 * theta * (y @ y))
        lower = -float(x @ x) / (2.0 * theta)
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
        minimum_partial_gap = min(minimum_partial_gap, left - lower)
        check(
            f"partial_square_{index}",
            left + 1.0e-12 >= lower and split_error < 1.0e-11,
            {"partial_value": left, "full_split_error": split_error},
            {"partial_lower_bound": lower, "full_split_error": "< 1e-11"},
        )
    c = rng.normal(size=9)
    d = -c
    leftover = float(c @ d + 0.5 * (d @ d))
    check("feedback_leftover_sign_indefinite", leftover < 0.0 and abs(leftover + 0.5 * float(c @ c)) < 1.0e-12, leftover, "-||c||^2/2")

    # Revisit cancellation: a normalized source mode and its nonzero smoothed
    # image have distinct norms.  Source cost stays fixed, terminal
    # displacement vanishes, and per-increment image sixth moments diverge.
    source_mode_h_norm_sq = 1.0
    image_mode_samples = np.array([1.0, -0.5, 0.25, -0.125], dtype=float)
    image_mode_l6_sixth = float(np.mean(np.abs(image_mode_samples) ** 6))
    revisit_values: list[dict[str, float]] = []
    for denominator in (4, 16, 64, 256):
        probability = 1.0 / denominator
        amplitude = probability ** -0.5
        source_cost = 2.0 * probability * amplitude**2 * source_mode_h_norm_sq
        sixth_sum = 2.0 * probability * amplitude**6 * image_mode_l6_sixth
        terminal = amplitude - amplitude
        expected_source_cost = 2.0 * source_mode_h_norm_sq
        expected_sixth_sum = 2.0 * image_mode_l6_sixth * probability**-2
        revisit_values.append({"p": probability, "source_cost": source_cost, "image_mode_l6_sixth": image_mode_l6_sixth, "sixth_sum": sixth_sum})
        check(f"revisit_source_cost_{denominator}", abs(source_cost - expected_source_cost) < 1.0e-12, source_cost, expected_source_cost)
        check(f"revisit_terminal_zero_{denominator}", terminal == 0.0, terminal, 0.0)
        check(f"revisit_sixth_{denominator}", image_mode_l6_sixth > 0.0 and abs(sixth_sum - expected_sixth_sum) < 1.0e-8, sixth_sum, expected_sixth_sum)
    check("revisit_sixth_strict_growth", all(revisit_values[i + 1]["sixth_sum"] > revisit_values[i]["sixth_sum"] for i in range(3)), [row["sixth_sum"] for row in revisit_values], "strictly increasing")

    # Repaired exponent ledger.  These are the accepted sharp replacements
    # for the two historical zero-slack coarse rows in R-093.
    exponent_rows = {
        "sharp_a2_da": (Fraction(1, 2), Fraction(1, 3)),
        "sharp_a3_da": (Fraction(2, 5), Fraction(8, 15)),
        "centered_gram_mixed": (Fraction(1, 2), Fraction(1, 6)),
        "fresh_derivative": (Fraction(1, 2), Fraction(1, 3)),
    }
    exponent_report: dict[str, dict[str, str]] = {}
    expected_slacks = {
        "sharp_a2_da": Fraction(1, 6),
        "sharp_a3_da": Fraction(1, 15),
        "centered_gram_mixed": Fraction(1, 3),
        "fresh_derivative": Fraction(1, 6),
    }
    for label, (a_power, b_power) in exponent_rows.items():
        slack = 1 - a_power - b_power
        moment = 1 / slack
        exponent_report[label] = {"a": str(a_power), "b": str(b_power), "slack": str(slack), "moment": str(moment)}
        check(f"{label}_slack", slack == expected_slacks[label], slack, expected_slacks[label])
        check(f"{label}_positive", slack > 0, slack, "> 0")

    # Direct numerical checks of the exact three-factor Young formula for the
    # two mixed powers.  The constant is derived from a,b,eta,zeta.
    maximum_young_excess = -math.inf
    for a_power, b_power in ((0.5, 1.0 / 6.0), (0.5, 1.0 / 3.0)):
        eta, zeta = 0.17, 0.09
        constant = generalized_young_constant(a_power, b_power, eta, zeta)
        for z_value in (0.03, 0.2, 1.0, 4.0):
            for energy in (0.01, 0.4, 2.0, 11.0):
                for sextic in (0.02, 0.7, 3.0, 17.0):
                    slack = 1.0 - a_power - b_power
                    left = z_value * energy**a_power * sextic**b_power
                    right = eta * energy + zeta * sextic + constant * z_value ** (1.0 / slack)
                    maximum_young_excess = max(maximum_young_excess, left - right)
                    check(
                        f"young_{a_power}_{b_power}_{z_value}_{energy}_{sextic}",
                        left <= right + 1.0e-12,
                        left - right,
                        "<= 0",
                    )

    failures = [row for row in assertions if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-root-local-gram-secant-feedback-boundary-primary/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(assertions),
        "assertions_passed": len(assertions) - len(failures),
        "assertions_failed": len(failures),
        "assertions": assertions,
        "derived": {
            "quadratic_kernel_constant": str(quadratic_kernel),
            "mixed_square_kernel_constant": str(mixed_square_kernel),
            "prefix_hilbert_schmidt_constant": str(prefix_hilbert_schmidt),
            "weighted_hardy_constant": hardy_square,
            "maximum_hardy_random_ratio": maximum_hardy_ratio,
            "maximum_l2_l6_interpolation_ratio": maximum_interpolation_ratio,
            "minimum_curvature_gap": minimum_curvature_gap,
            "minimum_partial_square_gap": minimum_partial_gap,
            "maximum_young_excess": maximum_young_excess,
            "exponent_ledger": exponent_report,
            "revisit_fixture": revisit_values,
        },
        "claims_not_established": [
            "root_local_secant_embedding_into_complete_R079_packet",
            "uniform_H_N",
            "REG",
            "OVERLAP_src",
            "Nelson",
            "Sector_A_closure",
        ],
    }
    atomic_json(OUTPUT, payload)
    print(
        f"R-094 PRIMARY {'PASS' if not failures else 'FAIL'}: "
        f"{len(assertions) - len(failures)}/{len(assertions)} assertions"
    )
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
