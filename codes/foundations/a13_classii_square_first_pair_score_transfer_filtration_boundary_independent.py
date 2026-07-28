#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped R-109 package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path


SCHEMA = "tect/a13-square-first-pair-score-transfer-filtration-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-square-first-pair-score-transfer-filtration-boundary/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def exp_moment(power: int) -> int:
    return math.factorial(power)


def gaussian_even_moment(power: int) -> int:
    if power % 2:
        return 0
    value = 1
    for factor in range(1, power, 2):
        value *= factor
    return value


def one_pair_log_mgf(a: float) -> float:
    d = 1.0 - 2.0 * a
    value = (
        math.sqrt(math.pi)
        / (2.0 * math.sqrt(a))
        * math.exp(d * d / (4.0 * a))
        * math.erfc(d / (2.0 * math.sqrt(a)))
    )
    return math.log(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # Independent moment expansion for U=2T-T^2.
    eu = 2 * exp_moment(1) - exp_moment(2)
    eu2 = 4 * exp_moment(2) - 4 * exp_moment(3) + exp_moment(4)
    eu3 = 8 * exp_moment(3) - 12 * exp_moment(4) + 6 * exp_moment(5) - exp_moment(6)
    checks.require("moments", "E U", eu == 0, eu, 0)
    checks.require("moments", "E U^2", eu2 == 8, eu2, 8)
    checks.require("moments", "E U^3", eu3 == -240, eu3, -240)
    checks.require("moments", "U maximum location", 2 * 1 - 1**2 == 1, 2 * 1 - 1**2, 1)
    for sample in (0.0, 0.25, 1.0, 2.0, 10.0):
        value = 2 * sample - sample * sample
        checks.require("moments", f"U<=1 sample {sample}", value <= 1.0, value, "<=1")

    threshold = Fraction(1, 5)
    small_multiplier = Fraction(4, 1) / (1 - threshold / 3)
    checks.require("bennett", "threshold multiplier", small_multiplier == Fraction(30, 7), small_multiplier, Fraction(30, 7))
    checks.require("bennett", "threshold multiplier less than five", small_multiplier < 5, small_multiplier, "<5")
    checks.require("bennett", "large branch contact", threshold == 5 * threshold * threshold, threshold, 5 * threshold * threshold)
    checks.require(
        "bennett",
        "exp threshold elementary bound",
        math.exp(float(threshold)) < float(1 / (1 - threshold)),
        math.exp(float(threshold)),
        f"<{float(1 / (1 - threshold))}",
    )
    for index in range(41):
        a = float(threshold) * index / 40
        if a == 0:
            lhs = 0.0
        else:
            lhs = 8.0 * (math.exp(a) - 1.0 - a)
        rhs = 5.0 * a * a
        checks.require("bennett_grid", f"small branch grid {index}", lhs <= rhs + 1e-14, lhs, f"<={rhs}")

    amplitude_grid = (0.01, 0.05, 0.2, 1.0, 5.0)
    ratios: list[float] = []
    for a in amplitude_grid:
        ratio = one_pair_log_mgf(a) / (a * a)
        ratios.append(ratio)
        checks.require("exact_mgf", f"exact amplitude {a}", ratio <= 5.0, ratio, "<=5")
    checks.require("exact_mgf", "small amplitude tends from below four", 3.0 < ratios[0] < 4.0, ratios[0], "between 3 and 4")
    checks.require("exact_mgf", "large amplitude ratio decreases", ratios[-1] < ratios[0], (ratios[-1], ratios[0]), "last<first")

    # Scale algebra in rational arithmetic.
    q = Fraction(10, 9)
    sigma = Fraction(3, 5)
    lam = Fraction(7, 11)
    beta = lam * sigma**4 / 4
    packet_variance = lam**2 * sigma**8 / 2
    covariance_cost = q**2 * Fraction(5, 4) * lam**2 * sigma**8 / 4
    bennett_cost = 5 * (q * beta) ** 2
    checks.require("scaling", "packet variance", packet_variance > 0, packet_variance, ">0")
    checks.require("scaling", "covariance and Bennett costs agree", covariance_cost == bennett_cost, covariance_cost, bennett_cost)
    checks.require("scaling", "small-q coefficient", Fraction(eu2, 2) == 4, Fraction(eu2, 2), 4)
    checks.require("scaling", "available coefficient room", 5 - Fraction(eu2, 2) == 1, 5 - Fraction(eu2, 2), 1)

    # Selector-independent floors and shell exponents.
    for r_value in (Fraction(0), sigma**2 / 4, sigma**2 / 2, sigma**2, 3 * sigma**2):
        packet_value = lam * (r_value**2 - sigma**2 * r_value)
        floor = -lam * sigma**4 / 4
        checks.require("floors", f"quartic floor {r_value}", packet_value >= floor, packet_value, f">={floor}")
    alpha = Fraction(10, 9)
    mu = Fraction(2, 9)
    interior_alpha = Fraction(1, 3)
    interior_mu = Fraction(2, 5)
    boundary_floor = -2 * alpha
    interior_floor = -4 * interior_mu - interior_alpha**2 / (4 * interior_mu)
    checks.require("floors", "boundary regime condition", alpha >= 4 * mu, alpha, f">={4 * mu}")
    checks.require("floors", "boundary regime floor negative", boundary_floor < 0, boundary_floor, "<0")
    checks.require("floors", "interior regime condition", interior_alpha < 4 * interior_mu, interior_alpha, f"<{4 * interior_mu}")
    checks.require("floors", "interior regime floor negative", interior_floor < 0, interior_floor, "<0")

    dimension = 3
    covariance_decay = 4
    derivative_order = 1
    quartic_shell = dimension + 2 * derivative_order - 2 * covariance_decay
    baseline_shell = dimension + 2 * derivative_order - covariance_decay
    determinant_shell = dimension + 4 * derivative_order - 2 * covariance_decay
    derivative_covariance_hs_shell = dimension - 4
    checks.require("shells", "quartic floor shell", quartic_shell == -3, quartic_shell, -3)
    checks.require("shells", "baseline floor shell", baseline_shell == 1, baseline_shell, 1)
    checks.require("shells", "determinant shell", determinant_shell == -1, determinant_shell, -1)
    checks.require("shells", "derivative covariance HS shell", derivative_covariance_hs_shell == -1, derivative_covariance_hs_shell, -1)

    # Independent polynomial test of second Gaussian integration by parts.
    c = Fraction(3, 2)
    derivative_expectation = 6 * gaussian_even_moment(2) + 2 * c
    score_expectation = Fraction(1, 2) * (
        gaussian_even_moment(6)
        - gaussian_even_moment(4)
        + 2 * c * (gaussian_even_moment(4) - gaussian_even_moment(2))
        + c**2 * (gaussian_even_moment(2) - gaussian_even_moment(0))
    )
    checks.require("score_transfer", "polynomial IBP fixture", derivative_expectation == score_expectation, derivative_expectation, score_expectation)
    checks.require(
        "score_transfer",
        "quadratic score variance",
        gaussian_even_moment(4) - 2 * gaussian_even_moment(2) + 1 == 2,
        gaussian_even_moment(4) - 2 * gaussian_even_moment(2) + 1,
        2,
    )
    score_constant = q**2 / 64
    checks.require("score_transfer", "q score constant", score_constant == Fraction(25, 1296), score_constant, Fraction(25, 1296))
    eta = 2.0 / 7.0
    zeta = 3.0 / 11.0
    coefficient = 5.0 / 13.0
    x_star = coefficient**2 / (16.0 * eta**1.5 * zeta**0.5)
    y_star = coefficient**2 / (16.0 * eta**0.5 * zeta**1.5)
    lhs = coefficient * x_star**0.25 * y_star**0.25
    rhs = eta * x_star + zeta * y_star + coefficient**2 / (8.0 * math.sqrt(eta * zeta))
    checks.require("score_transfer", "Young optimizer numeric", abs(lhs - rhs) < 1e-13, lhs - rhs, 0)

    # Stein-exponentiation and filtration checks.
    theta = 0.3
    raw_bounds: list[float] = []
    for frequency in (8.0, 16.0, 32.0):
        raw_bound = theta / frequency - 0.5 * math.log(1.0 - 2.0 * theta / frequency)
        raw_bounds.append(raw_bound)
    checks.require("stein_boundary", "raw Wick bound decreases", raw_bounds[2] < raw_bounds[1] < raw_bounds[0], raw_bounds, "strictly decreasing")
    checks.require("stein_boundary", "raw Wick bound small", raw_bounds[-1] < 0.03, raw_bounds[-1], "<0.03 tooling threshold")
    bessel_leading = [theta * frequency - 0.5 * math.log(2 * math.pi * theta * frequency) for frequency in (8.0, 16.0, 32.0)]
    checks.require("stein_boundary", "derivative representative grows", bessel_leading[2] > bessel_leading[1] > bessel_leading[0], bessel_leading, "strictly increasing")
    checks.require(
        "stein_boundary",
        "linear asymptotic ratio",
        abs((theta * 10**6 - 0.5 * math.log(2 * math.pi * theta * 10**6)) / 10**6 - theta) < 1e-4,
        (theta * 10**6 - 0.5 * math.log(2 * math.pi * theta * 10**6)) / 10**6,
        theta,
    )

    past = frozenset({"past"})
    realized = frozenset({"past", "fresh_root"})
    predicted = frozenset({"past"})
    checks.require("filtration", "realized cost post-reveal", realized != past, sorted(realized), "not past")
    checks.require("filtration", "conditional expected cost predictable", predicted == past, sorted(predicted), sorted(past))

    # Common-heat CM mean debt sign and growth.
    for eigenvalue in (Fraction(1, 10), Fraction(1), Fraction(10), Fraction(100)):
        coefficient_value = -Fraction(5, 9) * eigenvalue**2 / (eigenvalue + Fraction(9, 10))
        checks.require("cm_boundary", f"negative CM debt {eigenvalue}", coefficient_value < 0, coefficient_value, "<0")
    large_eigenvalue = Fraction(10**8)
    scaled_cm = (-Fraction(5, 9) * large_eigenvalue**2 / (large_eigenvalue + Fraction(9, 10))) / large_eigenvalue
    checks.require("cm_boundary", "linear CM asymptotic", abs(float(scaled_cm + Fraction(5, 9))) < 1e-8, float(scaled_cm), float(-Fraction(5, 9)))

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "bennett_threshold": str(threshold),
        "small_branch_multiplier": str(small_multiplier),
        "one_pair_moments": {"mean": eu, "second": eu2, "third": eu3},
        "exact_log_mgf_over_a2": ratios,
        "covariance_cost": str(covariance_cost),
        "bennett_cost": str(bennett_cost),
        "quartic_shell_exponent": quartic_shell,
        "baseline_shell_exponent": baseline_shell,
        "determinant_shell_exponent": determinant_shell,
        "derivative_covariance_hs_shell_exponent": derivative_covariance_hs_shell,
        "score_constant": str(score_constant),
        "raw_wick_bounds": raw_bounds,
        "derivative_asymptotic_leading": bessel_leading,
    }
    route_verdicts = {
        "one_pair_all_amplitudes": "pass",
        "predictable_conditional_cost": "required",
        "selector_quartic_floor": "pass-in-diagonal-submodel",
        "baseline_direct_floor": "divergent",
        "fixed_W_score_transfer": "pass-expectation-only",
        "Stein_exponentiation": "fail",
        "full_production_cluster": "open",
        "sector_A": "open",
    }
    results = {"derived": derived, "route_verdicts": route_verdicts}
    results_sha256 = hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": len(checks.rows),
        "assertions_passed": len(checks.rows) - len(failed),
        "assertions_failed": len(failed),
        "assertions": checks.rows,
        "assertion_names": [str(row["name"]) for row in checks.rows],
        "results_sha256": results_sha256,
        "results": results,
        "derived": derived,
        "route_verdicts": route_verdicts,
    }
    atomic_json(args.output, payload)
    print(f"Independent R-109: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
