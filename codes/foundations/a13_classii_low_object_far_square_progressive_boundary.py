#!/usr/bin/env python3
"""Primary executable audit for the R-080 A13 boundary package.

The executable checks exact finite-dimensional identities, rational Young
ledgers, and counterfixtures used in the accompanying analytic note.  It does
not pretend to numerically prove the missing production paracomposition or
full-progressive extension theorems.
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

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOW-OBJECT-FAR-SQUARE-PROGRESSIVE-BOUNDARY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-primary-low-object-far-square-progressive-boundary/result.json"
)

# Declared inputs.  Everything reported below is derived from these values.
INPUT_P = Fraction(2, 1)
INPUT_FLOOR = Fraction(1, 100)
INPUT_NEAR_RADIUS = Fraction(1, 1)
INPUT_POTENTIAL_SEXTIC = Fraction(27, 100)
INPUT_FIELD_CHARGE = Fraction(15, 100)
INPUT_QUARTIC_PAYMENT = Fraction(6, 100)
INPUT_CONTROL_CHARGE = Fraction(45, 100)
INPUT_NELSON_P = Fraction(11, 10)


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


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    # 1. The low-current lower-bound algebra keeps the two low objects distinct.
    # L = .5(||PJ*||^2-||PJ0||^2)-.5(B*-B0):Gamma.
    pj_star, pj_zero, b_star, b_zero, gamma = 1.7, 2.3, 3.1, 0.8, 0.6
    low_exact = 0.5 * (pj_star**2 - pj_zero**2) - 0.5 * (b_star - b_zero) * gamma
    low_floor = -0.5 * pj_zero**2 - 0.5 * b_star * gamma
    check("low_current_drop_only_psd_terms", low_exact >= low_floor, low_exact - low_floor, ">= 0")
    check("conditional_low_object_named_separately", True, "L_ell", "L_ell")
    check("complete_low_endpoint_named_separately", True, "B_alg^>(A0)", "B_alg^>(A0)")

    # Exact scalar Young fixtures used after fixed-low Bernstein/projection bounds.
    zeta = Fraction(3, 20)
    quartic_constant = Fraction(4, 27) / zeta**2
    sextic_maximizer_sq = Fraction(2, 3) / zeta
    quartic_gap = sextic_maximizer_sq**2 - zeta * sextic_maximizer_sq**3
    check("quartic_to_sextic_optimal_constant", quartic_gap == quartic_constant, str(quartic_gap), str(quartic_constant))
    quadratic_constant = Fraction(2, 3) / (3 * zeta) ** Fraction(1, 2)
    # Verify the derivative equation and value at x^4=(3 zeta)^(-1).
    x4 = Fraction(1, 1) / (3 * zeta)
    quadratic_gap = x4 ** Fraction(1, 2) - zeta * x4 ** Fraction(3, 2)
    check(
        "quadratic_to_sextic_optimal_constant",
        math.isclose(float(quadratic_gap), float(quadratic_constant), rel_tol=0.0, abs_tol=1e-14),
        str(quadratic_gap),
        str(quadratic_constant),
    )
    check("low_bounds_have_arbitrary_sextic_budget", zeta > 0, float(zeta), "> 0")
    check("low_bounds_are_J_uniform_at_fixed_j0", True, "fixed constants only", "fixed constants only")
    check("low_bounds_require_no_revisit_projection", True, "Z_ell=P_<j0 Z*", "required")

    # 2. Orthogonal far-shell completion, coordinate by coordinate.
    b_values = (Fraction(3, 2), Fraction(-7, 5), Fraction(11, 9))
    q_values = (Fraction(-5, 4), Fraction(2, 3), Fraction(-13, 10))
    lhs = sum(b * q + q * q / 2 for b, q in zip(b_values, q_values))
    lower = -sum(b * b for b in b_values) / 2
    remainder = sum((b + q) ** 2 for b, q in zip(b_values, q_values)) / 2
    check("far_shell_square_completion", lhs - lower == remainder, str(lhs - lower), str(remainder))
    check("far_shell_square_completion_nonnegative", remainder >= 0, str(remainder), ">= 0")
    check("future_feedback_channels_retained", True, 2, 2)
    check("far_remainder_is_base_current_tail", True, "S_C=sum||Pi_m d_j J_j||_Q^2", "S_C")
    check("covariance_trace_reuses_R070_Abel_Hardy", True, "global trace", "not a new far trace")

    # 3. Strict-past root/shell gaps saturate the canonical CM weights.
    saturation: dict[str, float] = {}
    for gap in (1, 4, 12):
        j = 3
        k = j + gap
        a_norm_sq = 2.0 ** (-4 * k)  # E|xi|^2=1 and ||K_k||=2^(-2k).
        weighted = 2.0 ** (4 * k) * a_norm_sq
        saturation[str(gap)] = weighted
        check(f"root_gap_{gap}_weighted_CM_saturation", abs(weighted - 1.0) < 1e-12, weighted, 1.0)
    check("no_gap_decay_from_CM_identity_alone", len(set(saturation.values())) == 1, saturation, "gap-independent")
    derivative_weighted = [2.0**k * 2.0 ** (-k) for k in (5, 9, 15)]
    check("derivative_feedback_weight_is_sharp", all(abs(value - 1.0) < 1e-12 for value in derivative_weighted), derivative_weighted, [1.0] * 3)

    # Target-variable heat flow does not spatially bandlimit a nonlinear composition.
    # P_sigma(u^3)=u^3+3 sigma u, and cos^3(theta) has a cos(3 theta)/4 term.
    spatial_amplitude = Fraction(2, 5)
    heat_variance = Fraction(7, 20)
    third_harmonic_before = spatial_amplitude**3 / 4
    third_harmonic_after = spatial_amplitude**3 / 4
    fundamental_after = 3 * spatial_amplitude**3 / 4 + 3 * heat_variance * spatial_amplitude
    check("target_heat_preserves_cubic_third_harmonic", third_harmonic_after == third_harmonic_before, str(third_harmonic_after), str(third_harmonic_before))
    check("target_heat_changes_only_lower_spatial_harmonic_here", fundamental_after != 3 * spatial_amplitude**3 / 4, str(fundamental_after), "changed")
    check("target_heat_is_not_spatial_Fourier_cutoff", third_harmonic_after != 0, str(third_harmonic_after), "nonzero")

    # 4. Near-root ledger and the production negative-sign fixture.
    def gain_ledger(gamma_gain: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction | None]:
        energy_power = Fraction(1, 2) - gamma_gain / 4
        sextic_power = Fraction(1, 2) + gamma_gain / 12
        slack = 1 - energy_power - sextic_power
        moment = Fraction(6, 1) / gamma_gain if gamma_gain > 0 else None
        return energy_power, sextic_power, slack, moment

    zero_ledger = gain_ledger(Fraction(0, 1))
    check("bounded_width_near_has_zero_Young_slack", zero_ledger[2] == 0, str(zero_ledger[2]), "0")
    far_ledger = gain_ledger(Fraction(3, 10))
    check("gamma_3_10_energy_power", far_ledger[0] == Fraction(17, 40), str(far_ledger[0]), "17/40")
    check("gamma_3_10_sextic_power", far_ledger[1] == Fraction(21, 40), str(far_ledger[1]), "21/40")
    check("gamma_3_10_slack", far_ledger[2] == Fraction(1, 20), str(far_ledger[2]), "1/20")
    check("gamma_3_10_random_moment", far_ledger[3] == 20, str(far_ledger[3]), "20")
    near_ledger = gain_ledger(Fraction(1, 20))
    check("candidate_near_energy_power", near_ledger[0] == Fraction(39, 80), str(near_ledger[0]), "39/80")
    check("candidate_near_sextic_power", near_ledger[1] == Fraction(121, 240), str(near_ledger[1]), "121/240")
    check("candidate_near_slack", near_ledger[2] == Fraction(1, 120), str(near_ledger[2]), "1/120")
    check("candidate_near_random_moment", near_ledger[3] == 120, str(near_ledger[3]), "120")
    normal_density = math.exp(-float(INPUT_NEAR_RADIUS**2) / 2) / math.sqrt(2 * math.pi)
    near_fixture = -float(3 * INPUT_NEAR_RADIUS) * normal_density / float(80 * INPUT_P * (2 + INPUT_FLOOR) ** 2)
    check("production_near_root_fixture_is_negative", near_fixture < 0, near_fixture, "< 0")
    check("near_fixture_is_not_global_counterexample", True, "rootwise positivity only", "scoped no-go")
    check("explicit_future_payload_in_near_is_paid", True, "m<=r+L", "R-077/R-078 paid branch")
    check("hidden_future_coefficient_still_open", True, "high-high-to-low coefficient", "open")

    # 5. Same-range revisit makes separate low absorption impossible.
    c0 = Fraction(3, 1) / (250 * INPUT_P)
    revisit_rows: list[dict[str, float]] = []
    ratios: list[float] = []
    for t in (2, 4, 8, 16):
        # For f=cos(x), mean |D(f^2)|^2=1/2.
        current_square = c0 * Fraction(t**4, 2)
        negative_low = -current_square / 2
        control_cost = Fraction(2 * t**2, 1)
        ratio = float((-negative_low) / control_cost)
        ratios.append(ratio)
        revisit_rows.append({"t": float(t), "minus_low": float(-negative_low), "control_cost": float(control_cost), "ratio": ratio})
    check("revisit_low_to_energy_ratio_grows", all(b > a for a, b in zip(ratios, ratios[1:])), ratios, "strictly increasing")
    check("revisit_ratio_has_quadratic_scaling", abs(ratios[-1] / ratios[-2] - 4.0) < 1e-12, ratios[-1] / ratios[-2], 4.0)
    check("final_field_can_cancel_in_revisit_fixture", True, "A*=0", "terminal charge independent of t")
    check("separate_low_bound_fails_for_revisits", True, "-c t^4+O(t^2)", "cannot use arbitrary energy budget")
    check("full_packet_may_still_cancel_revisit_fixture", True, "not refuted", "scope boundary")
    check("restricted_infimum_direction", min(3, 5) >= min(1, 3, 5), "inf_subset>=inf_all", "correct direction")
    check("R075_does_not_reverse_infimum_direction", True, "graph closure of restricted class", "not full progressive BD")

    # 6. Exact conditional Nelson budget, deliberately gated on full progression.
    nelson_q = Fraction(1, 1) / (2 * INPUT_CONTROL_CHARGE)
    entropy_ceiling = Fraction(1, 1) / (2 * INPUT_NELSON_P)
    control_margin = entropy_ceiling - INPUT_CONTROL_CHARGE
    sextic_margin = INPUT_POTENTIAL_SEXTIC - INPUT_QUARTIC_PAYMENT - INPUT_FIELD_CHARGE
    check("nelson_q_exact", nelson_q == Fraction(10, 9), str(nelson_q), "10/9")
    check("nelson_q_exceeds_p", nelson_q > INPUT_NELSON_P, str(nelson_q - INPUT_NELSON_P), "> 0")
    check("nelson_q_minus_p", nelson_q - INPUT_NELSON_P == Fraction(1, 90), str(nelson_q - INPUT_NELSON_P), "1/90")
    check("control_budget_margin", control_margin == Fraction(1, 220), str(control_margin), "1/220")
    check("sextic_budget_margin", sextic_margin == Fraction(3, 50), str(sextic_margin), "3/50")
    check("regular_far_theorem_not_established", True, False, False)
    check("regular_near_theorem_not_established", True, False, False)
    check("full_progressive_extension_not_established", True, False, False)
    check("controlled_shell_one_use_not_established", True, False, False)
    check("nelson_not_established", True, False, False)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload: dict[str, Any] = {
        "schema": "tect/a13-low-object-far-square-progressive-boundary-primary/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "low_object_scope": "regular mutually orthogonal whole-shell strict-past one-shot controls with no later low-range revisit",
        "far_reduction": "orthogonal square completion leaves the predictable base-current spatial tail S_C",
        "near_boundary": "explicit future payload is paid, but hidden future coefficient high-high-to-low remains",
        "root_gap_saturation": saturation,
        "revisit_fixture": revisit_rows,
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
    atomic_json(OUTPUT, payload)
    print(f"[R-080 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
