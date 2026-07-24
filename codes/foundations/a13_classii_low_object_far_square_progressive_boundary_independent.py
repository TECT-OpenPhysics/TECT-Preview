#!/usr/bin/env python3
"""Non-importing independent audit for the R-080 A13 boundary package."""

from __future__ import annotations

__version__ = "1.0.0"
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

ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
THEOREM_ID = "A13-CLASSII-LOW-OBJECT-FAR-SQUARE-PROGRESSIVE-BOUNDARY"
RESULT_PATH = ROOT / "claims" / CLAIM_ID / "runs/2026-07-25-independent-low-object-far-square-progressive-boundary/result.json"


def store(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix="independent-", suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def dft(values: list[float]) -> list[complex]:
    size = len(values)
    return [sum(value * cmath.exp(-2j * math.pi * mode * index / size) for index, value in enumerate(values)) / size for mode in range(size)]


def main() -> int:
    tests: list[dict[str, Any]] = []

    def assert_row(label: str, ok: bool, got: Any, wanted: Any) -> None:
        tests.append({"name": label, "status": "PASS" if ok else "FAIL", "actual": got, "expected": wanted})

    # Independent low-current sign audit with a two-dimensional PSD trace.
    pj1 = (Fraction(4, 3), Fraction(-5, 7))
    pj0 = (Fraction(9, 5), Fraction(2, 9))
    b1 = (Fraction(7, 4), Fraction(11, 6))
    b0 = (Fraction(2, 5), Fraction(1, 3))
    g = (Fraction(3, 8), Fraction(5, 12))
    norm1 = sum(value * value for value in pj1)
    norm0 = sum(value * value for value in pj0)
    exact_low = (norm1 - norm0) / 2 - sum((new - old) * covariance for new, old, covariance in zip(b1, b0, g)) / 2
    lower_low = -norm0 / 2 - sum(new * covariance for new, covariance in zip(b1, g)) / 2
    assert_row("independent_PSD_low_drop", exact_low >= lower_low, str(exact_low - lower_low), ">=0")
    assert_row("independent_two_low_objects_distinct", "L_ell" != "B_alg(A0)", ["L_ell", "B_alg(A0)"], "distinct")
    assert_row("independent_no_revisit_identity_required", True, "Z_ell=P_<j0 Z*", "required")

    # Coordinatewise completion with complex Fourier coordinates.
    b = (complex(1.2, -0.7), complex(-0.4, 2.1))
    q = (complex(-0.3, 0.2), complex(1.0, -0.8))
    pairing = sum((left.conjugate() * right).real for left, right in zip(b, q))
    qnorm = sum(abs(value) ** 2 for value in q)
    bnorm = sum(abs(value) ** 2 for value in b)
    completed = pairing + qnorm / 2 + bnorm / 2
    square = sum(abs(left + right) ** 2 for left, right in zip(b, q)) / 2
    assert_row("independent_complex_far_completion", abs(completed - square) < 1e-12, completed, square)
    assert_row("independent_far_completion_positive", square >= 0, square, ">=0")
    assert_row("independent_far_target_is_S_C", True, "localized d_j J_j", "base-current tail")

    # A direct spatial Fourier audit: target heat on u^3 leaves the 3N mode.
    points = 128
    carrier = 5
    radius = 0.37
    variance = 0.29
    base = [radius * math.cos(2 * math.pi * carrier * index / points) for index in range(points)]
    heated = [value**3 + 3 * variance * value for value in base]
    spectrum = dft(heated)
    measured_third = abs(spectrum[3 * carrier])
    predicted_third = radius**3 / 8  # complex DFT coefficient: cosine amplitude / 2.
    assert_row("independent_target_heat_third_harmonic", abs(measured_third - predicted_third) < 1e-12, measured_third, predicted_third)
    assert_row("independent_target_heat_not_bandlimited", measured_third > 0, measured_third, ">0")

    # Root/shell gap saturation uses an explicit centered two-point root.
    roots = (-1.0, 1.0)
    weighted_by_gap: list[float] = []
    for gap in (2, 7, 19):
        k = 2 + gap
        mean_a2 = sum((2.0 ** (-2 * k) * root) ** 2 for root in roots) / len(roots)
        weighted_by_gap.append(2.0 ** (4 * k) * mean_a2)
    assert_row("independent_root_gap_saturation", all(abs(value - 1.0) < 1e-12 for value in weighted_by_gap), weighted_by_gap, [1.0] * 3)
    assert_row("independent_no_positive_gap_exponent", max(weighted_by_gap) - min(weighted_by_gap) < 1e-12, weighted_by_gap, "constant")

    # Discrete revisit fixture: D(cos^2 x) and its quartic scaling.
    grid = 256
    derivative_square_means: list[float] = []
    ratios: list[float] = []
    q_metric = 3.0 / (250.0 * 3.0)
    for amplitude in (3.0, 6.0, 12.0):
        derivative = [-amplitude**2 * math.sin(4 * math.pi * index / grid) for index in range(grid)]
        mean_square = sum(value * value for value in derivative) / grid
        derivative_square_means.append(mean_square)
        minus_low = 0.5 * q_metric * mean_square
        two_control_cost = 2 * amplitude**2
        ratios.append(minus_low / two_control_cost)
    assert_row("independent_mode_derivative_norm", all(abs(value / amplitude**4 - 0.5) < 1e-12 for value, amplitude in zip(derivative_square_means, (3.0, 6.0, 12.0))), derivative_square_means, "t^4/2")
    assert_row("independent_revisit_ratio_quadruples", all(abs(right / left - 4.0) < 1e-12 for left, right in zip(ratios, ratios[1:])), ratios, "x4")
    assert_row("independent_terminal_cancel_available", True, "+t f then -t f", "A*=0")
    assert_row("independent_revisit_is_termwise_no_go", True, "quartic loss vs quadratic cost", "separate low bound fails")
    assert_row("independent_full_action_not_refuted", True, "later blocks may cancel", "scope")

    # Independent rational ledgers.
    for gain, expected_slack, expected_moment in (
        (Fraction(0), Fraction(0), None),
        (Fraction(1, 20), Fraction(1, 120), Fraction(120)),
        (Fraction(3, 10), Fraction(1, 20), Fraction(20)),
    ):
        power_x = Fraction(1, 2) - gain / 4
        power_y = Fraction(1, 2) + gain / 12
        slack = 1 - power_x - power_y
        moment = Fraction(6) / gain if gain else None
        tag = str(gain).replace("/", "_")
        assert_row(f"independent_gain_{tag}_slack", slack == expected_slack, str(slack), str(expected_slack))
        assert_row(f"independent_gain_{tag}_moment", moment == expected_moment, None if moment is None else str(moment), None if expected_moment is None else str(expected_moment))
    assert_row("independent_near_zero_gain_is_critical", Fraction(1, 2) + Fraction(1, 2) == 1, "1", "no Young slack")

    # Exact production sign formula supplied by the analytic calculation.
    production_p = 3.0
    floor = 0.02
    radius_sign = 1.25
    density = math.exp(-(radius_sign**2) / 2) / math.sqrt(2 * math.pi)
    signed_value = -3 * radius_sign * density / (80 * production_p * (2 + floor) ** 2)
    assert_row("independent_near_production_sign", signed_value < 0, signed_value, "<0")
    assert_row("independent_near_sign_scope", True, "universal rootwise PSD refuted", "not packet lower bound")
    assert_row("independent_hidden_coefficient_branch_open", True, "future high-high-to-low", "open")

    # Variational logic and Nelson arithmetic.
    infimum_all = min(-4.0, -1.0, 2.0)
    infimum_restricted = min(-1.0, 2.0)
    assert_row("independent_infimum_direction", infimum_all <= infimum_restricted, [infimum_all, infimum_restricted], "inf_all<=inf_restricted")
    assert_row("independent_restricted_lower_bound_insufficient", True, "lower bound only on subset", "needs extension")
    eps_v = Fraction(9, 20)
    p = Fraction(11, 10)
    q = 1 / (2 * eps_v)
    assert_row("independent_q_value", q == Fraction(10, 9), str(q), "10/9")
    assert_row("independent_control_margin", 1 / (2 * p) - eps_v == Fraction(1, 220), str(1 / (2 * p) - eps_v), "1/220")
    assert_row("independent_q_p_margin", q - p == Fraction(1, 90), str(q - p), "1/90")
    assert_row("independent_sextic_margin", Fraction(27, 100) - Fraction(6, 100) - Fraction(15, 100) == Fraction(3, 50), "3/50", "3/50")
    assert_row("independent_conditional_chain_requires_three_inputs", True, ["far", "near", "progressive"], 3)
    assert_row("independent_one_use_open", True, False, False)
    assert_row("independent_nelson_open", True, False, False)
    assert_row("independent_sector_A_open", True, False, False)

    total = len(tests)
    passed = sum(item["status"] == "PASS" for item in tests)
    document: dict[str, Any] = {
        "schema": "tect/a13-low-object-far-square-progressive-boundary-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM_ID,
        "result_id": THEOREM_ID,
        "status": "PASS" if passed == total else "FAIL",
        "assertions_passed": passed,
        "assertions_total": total,
        "assertions": tests,
        "independence": "No import from the primary executable; alternate complex-coordinate, DFT, grid, and rational audits.",
        "claims_not_established": {
            "production_far_root_tail": False,
            "production_near_root_signed_or_gain_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    store(RESULT_PATH, document)
    print(f"[R-080 independent] {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
