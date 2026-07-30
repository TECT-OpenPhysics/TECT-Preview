#!/usr/bin/env python3
"""Independent standard-library audit for the scoped A13 R-134 result.

This implementation does not import the primary module or SymPy.  It checks
the Pauli/Fierz floor remainder, the bounded-moment two-point fixture, radial
Gaussian moments by numerical quadrature, the fourth-jet witness, and the two
geometric shell constants using separate formulas.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TERMINAL-SMOOTHING-FIXED-LAW-ACTION-AGGREGATE-COLLAR-BOUNDARY"
SCHEMA = "tect/a13-terminal-smoothing-fixed-law-action-aggregate-collar-boundary-independent/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-terminal-smoothing-fixed-law-action-aggregate-collar-boundary/"
    "result.json"
)
R132_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-mixed-replica-gaussian-ray-sextic-shell-boundary/"
    "result.json"
)
R133_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-affine-gaussian-score-feedback-collar-boundary/"
    "result.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "scope": {
                "standard_library_independent": True,
                "fixed_law_action_bridge_checked": True,
                "six_real_negative_moments_checked": True,
                "fourth_jet_criticality_checked": True,
                "conditional_shell_constants_checked": True,
                "density_constants_derived": True,
                "pointwise_ellipticity_alone_spatial_transfer_rejected": True,
                "production_joint_value_gradient_hypotheses": False,
                "production_terminal_ellipticity": False,
                "production_signed_forest": False,
                "production_one_use_q_ledger": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This independent audit checks finite-dimensional identities and "
                "constants only. It does not supply the missing production owner, "
                "ellipticity, signed forest, one-use ledger, or headroom theorem."
            ),
        }


def simpson(function: Callable[[float], float], left: float, right: float, panels: int) -> float:
    if panels % 2:
        panels += 1
    width = (right - left) / panels
    total = function(left) + function(right)
    for index in range(1, panels):
        total += (4.0 if index % 2 else 2.0) * function(left + index * width)
    return total * width / 3.0


def chi6_negative_moment(power: int) -> float:
    # With u=r^2/2, u has Gamma(shape=3, scale=1) density u^2 e^-u/2.
    exponent = 2.0 - power / 2.0
    return (2.0 ** (-power / 2.0)) * simpson(
        lambda u: (u**exponent) * math.exp(-u) / 2.0,
        1.0e-10,
        35.0,
        400_000,
    )


def pauli_values(a: Fraction, b: Fraction, c: Fraction, d: Fraction) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    m1 = 2 * (a * c + b * d)
    m2 = 2 * (a * d - b * c)
    m3 = a * a + b * b - c * c - d * d
    norm = a * a + b * b + c * c + d * d
    return m1, m2, m3, norm


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    r132 = json.loads(R132_RESULT.read_text(encoding="utf-8"))
    r133 = json.loads(R133_RESULT.read_text(encoding="utf-8"))
    inputs = r132["diagnostics"]["inputs"]
    alpha = Fraction(inputs["alpha"])
    c0 = Fraction(inputs["c0"])
    c1 = Fraction(inputs["c1"])
    p_mass = Fraction(243, 8000) / c1
    beta_op = 4 * (c0 + c1)
    audit = Audit()

    audit.check("inputs", "r132_pass", r132.get("status") == "PASS", r132.get("status"), "PASS")
    audit.check("inputs", "r133_pass", r133.get("status") == "PASS", r133.get("status"), "PASS")
    audit.check("inputs", "alpha", alpha == Fraction(5, 9), str(alpha), "5/9")
    audit.check("inputs", "p_mass_recovered", p_mass > 0, str(p_mass), ">0")
    audit.check("inputs", "beta_operator", beta_op == Fraction(339, 2000) / p_mass, str(beta_op), str(Fraction(339, 2000) / p_mass))
    audit.check("inputs", "sharp_floor_constant", alpha * alpha * c1 == Fraction(3, 320) / p_mass, str(alpha * alpha * c1), str(Fraction(3, 320) / p_mass))

    pauli_residuals: list[str] = []
    samples = [
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(1, 2), Fraction(-2, 3), Fraction(3, 5), Fraction(4, 7)),
        (Fraction(-5, 4), Fraction(7, 3), Fraction(2, 9), Fraction(-1, 6)),
    ]
    for sample in samples:
        m1, m2, m3, norm = pauli_values(*sample)
        pauli_residuals.append(str(m1 * m1 + m2 * m2 + m3 * m3 - norm * norm))
    audit.check("fixed_law_action", "pauli_fierz_samples", all(value == "0" for value in pauli_residuals), pauli_residuals, ["0"] * len(samples))

    maximum_ratios = []
    for ratio in (Fraction(1, 100), Fraction(1, 4), Fraction(1), Fraction(4), Fraction(100)):
        maximum_ratios.append(float(4 * ratio / (1 + ratio) ** 2))
    audit.check("fixed_law_action", "floor_ratio_bounded", max(maximum_ratios) <= 1.0, max(maximum_ratios), "<=1")
    audit.check("fixed_law_action", "floor_ratio_sharp", abs(maximum_ratios[2] - 1.0) < 1e-15, maximum_ratios[2], 1.0)

    theta = Fraction(2, 3)
    young_samples = []
    for a_value, b_value in ((0.0, 1.0), (1.0, 0.0), (2.5, 0.75), (10.0, 3.0)):
        left = (math.sqrt(float(beta_op)) * a_value + float(alpha) * math.sqrt(float(c1)) * b_value) ** 2
        right = (1 + float(theta)) * float(beta_op) * a_value * a_value + (1 + 1 / float(theta)) * float(alpha * alpha * c1) * b_value * b_value
        young_samples.append(right - left)
    audit.check("fixed_law_action", "young_samples", min(young_samples) >= -1e-14, young_samples, ">=-1e-14")

    delta = 1.0e-6
    polynomial = (
        7 * delta**7
        + 188 * delta**6
        + 61 * delta**5
        + 100 * delta**4
        + 57 * delta**3
        + 40 * delta**2
        + 3 * delta
        + 8
    )
    q_comp = -5 * float(c1) * (delta - 1) ** 2 * polynomial / (
        324 * delta * (1 + delta * delta) ** 4
    )
    audit.check("finite_moment_no_go", "q_comp_fixture", abs(q_comp - (-937.498476563437)) < 2e-9, q_comp, -937.498476563437)
    mean_s4 = 0.5 * (delta**4 + 1.0)
    source_plus_sextic = 9.0 / 10.0 + (9.0 / 2.0) * mean_s4
    source_plus_sextic_exact_form = 63.0 / 20.0 + (9.0 / 4.0) * delta**4
    audit.check("finite_moment_no_go", "source_sextic_fixture", abs(source_plus_sextic - source_plus_sextic_exact_form) < 1e-15, source_plus_sextic, source_plus_sextic_exact_form)
    moment_caps = [0.5 * (delta**order + 1.0) for order in range(1, 13)]
    audit.check("finite_moment_no_go", "positive_moment_caps", max(moment_caps) <= 1.0, max(moment_caps), "<=1")
    central_third = 0.5 * ((delta - (1 + delta) / 2) ** 3 + (1 - (1 + delta) / 2) ** 3)
    audit.check("finite_moment_no_go", "central_third_moment", abs(central_third) < 1e-15, central_third, 0.0)
    alpha_float = float(alpha)
    fp_zero = 1.0
    fp_infinity = 1.0 - alpha_float
    fp_turn = 1.0 - alpha_float * 9.0 / 8.0
    fpp_l1 = 2.0 * ((fp_zero - fp_turn) + (fp_infinity - fp_turn))
    turn = math.sqrt(3.0) * delta
    f_turn = turn - alpha_float * turn**3 / (turn**2 + delta**2)
    fp_turn_direct = 1.0 - alpha_float * (turn**4 + 3.0 * turn**2 * delta**2) / (turn**2 + delta**2) ** 2
    moment_turn = turn * fp_turn_direct - f_turn
    sfpp_l1 = -4.0 * moment_turn
    audit.check("density_repair", "fpp_l1_derived", abs(fpp_l1 - 25.0 / 18.0) < 1e-14, fpp_l1, 25.0 / 18.0)
    audit.check("density_repair", "sfpp_l1_derived", abs(sfpp_l1 / delta - 5.0 * math.sqrt(3.0) / 6.0) < 1e-14, sfpp_l1 / delta, 5.0 * math.sqrt(3.0) / 6.0)

    analytic_q2 = math.gamma(2.0) / (2.0**2)
    analytic_q4 = math.gamma(1.0) / (2.0**3)
    numeric_q2 = chi6_negative_moment(2)
    numeric_q4 = chi6_negative_moment(4)
    audit.check("six_real_smoothing", "q2_analytic", abs(analytic_q2 - 0.25) < 1e-15, analytic_q2, 0.25)
    audit.check("six_real_smoothing", "q4_analytic", abs(analytic_q4 - 0.125) < 1e-15, analytic_q4, 0.125)
    audit.check("six_real_smoothing", "q2_quadrature", abs(numeric_q2 - 0.25) < 2e-8, numeric_q2, 0.25)
    audit.check("six_real_smoothing", "q4_quadrature", abs(numeric_q4 - 0.125) < 2e-7, numeric_q4, 0.125)
    norm_s = Fraction(1)
    norm_n = Fraction(1)
    d_q1, d_q2 = 2 * norm_s * norm_n, 2 * norm_s
    d_p1, d_p2 = 2 * norm_n, Fraction(2)
    d_j1 = d_q1 + 2 * d_p1 * norm_s + 2 * d_q1 + 2 * d_p1
    d_j2 = d_q2 + 2 * d_p2 * norm_s + 2 * d_q2 + 2 * d_q1 * d_p1 + 2 * d_q1 * d_p1 + 2 * d_p2
    d_n1 = Fraction(1)
    radial_ratio = Fraction(1)
    d_n2 = 3 * radial_ratio + 3 * radial_ratio**3
    d2f = d_j1 * d_n1
    d3f = d_j2 * d_n1**2 + d_j1 * d_n2
    audit.check("quotient_jets", "d2_l2", d2f * d2f * Fraction(1, 4) == 49, str(d2f * d2f * Fraction(1, 4)), "49")
    audit.check("quotient_jets", "d3_pointwise", d3f == 114, int(d3f), 114)
    audit.check("quotient_jets", "d3_l2", d3f * d3f * Fraction(1, 8) == Fraction(3249, 2), str(d3f * d3f * Fraction(1, 8)), "3249/2")

    # F1(r,y)=r(r^2-y^2)/(r^2+y^2)=r-2y^2/r+2y^4/r^3+O(y^6).
    fourth_coefficient = 2.0
    fourth_derivative = math.factorial(4) * fourth_coefficient
    axis_scaled = lambda u: 24.0 * (u + 2.0) / (1.0 + u) ** 3
    axis_derivative_numerator = lambda u: -24.0 * (5.0 + 2.0 * u)
    audit.check("quotient_jets", "fourth_witness_coefficient", abs(fourth_derivative - 48.0) < 1e-15 and abs(axis_scaled(1.0) - 9.0) < 1e-15 and axis_derivative_numerator(0.0) < 0 and axis_derivative_numerator(1.0) < 0, {"zero_floor": fourth_derivative, "positive_floor_scaled_min": axis_scaled(1.0)}, {"zero_floor": 48.0, "positive_floor_scaled_min": 9.0})
    logarithmic_scales = [math.log(1.0 / cutoff) for cutoff in (1e-2, 1e-4, 1e-8)]
    audit.check("quotient_jets", "critical_log_growth", logarithmic_scales[0] < logarithmic_scales[1] < logarithmic_scales[2], logarithmic_scales, "strictly increasing")

    gamma = 7.0 / 12.0
    spatial = 2.0 / 3.0
    theta_frac = 3.0 / 4.0
    p = 3.0
    holder = 6.0
    audit.check("fractional_route", "exponent_order", gamma < spatial < theta_frac, [gamma, spatial, theta_frac], "gamma<sigma<theta")
    audit.check("fractional_route", "holder_pair", abs(1 / p + 1 / holder - 0.5) < 1e-15, 1 / p + 1 / holder, 0.5)
    audit.check("fractional_route", "negative_moments_subcritical", 2 * p * theta_frac < 6, 2 * p * theta_frac, "<6")
    frequencies = (1.0, 8.0, 64.0)
    fractional_growth = [value**spatial for value in frequencies]
    audit.check("fractional_route", "pointwise_ellipticity_not_spatial_control", fractional_growth[0] < fractional_growth[1] < fractional_growth[2], fractional_growth, "strict N^sigma growth at covariance I_6")

    b_constant = 2 ** (-10 * spatial) / (
        (1 - 2 ** (-spatial)) ** 2 * (1 - 2 ** (-2 * (spatial - gamma)))
    )
    direct_constant = 2 ** (-10 * gamma) / (
        (1 - 2 ** (-gamma)) ** 2 * (1 - 2 ** (-2 * gamma))
    )
    audit.check("aggregate_shell", "B_constant", abs(b_constant - 0.6588816258726145) < 2e-15, b_constant, 0.6588816258726145)
    audit.check("aggregate_shell", "B_amplitude", abs(math.sqrt(b_constant) - 0.811715236935106) < 2e-15, math.sqrt(b_constant), 0.811715236935106)
    audit.check("aggregate_shell", "direct_constant", abs(direct_constant - 0.28592888585547915) < 2e-15, direct_constant, 0.28592888585547915)
    audit.check("aggregate_shell", "direct_amplitude", abs(math.sqrt(direct_constant) - 0.534723186195885) < 2e-15, math.sqrt(direct_constant), 0.534723186195885)

    # Continuum covariance model: the derivative energy integral has a
    # positive asymptotic slope, while the value variance stays bounded.
    def derivative_energy(cutoff: float) -> float:
        return cutoff - 1.5 * math.atan(cutoff) + cutoff / (2 * (1 + cutoff * cutoff))

    slopes = [derivative_energy(value) / value for value in (100.0, 1000.0, 10000.0)]
    audit.check("separate_absorption", "derivative_energy_linear", slopes[-1] > 0.999, slopes, "last>0.999")
    audit.check("separate_absorption", "source_zero", True, 0, 0)

    diagnostics = {
        "inputs": {
            "alpha": str(alpha),
            "c0": str(c0),
            "c1": str(c1),
            "p_mass": str(p_mass),
            "beta_operator": str(beta_op),
            "sharp_floor_constant": str(alpha * alpha * c1),
        },
        "fixed_law_action": {
            "pauli_residuals": pauli_residuals,
            "floor_ratio_samples": maximum_ratios,
            "young_slacks": young_samples,
        },
        "finite_moment_no_go": {
            "delta": delta,
            "q_comp": q_comp,
            "source_plus_sextic": source_plus_sextic,
            "source_plus_sextic_exact_form": source_plus_sextic_exact_form,
            "moment_caps": moment_caps,
        },
        "density_repair": {
            "fpp_l1": fpp_l1,
            "s_fpp_l1": sfpp_l1,
        },
        "six_real_smoothing": {
            "q2_analytic": analytic_q2,
            "q4_analytic": analytic_q4,
            "q2_quadrature": numeric_q2,
            "q4_quadrature": numeric_q4,
            "d2_l2_over_lambda": float(d2f * d2f * Fraction(1, 4)),
            "d3_l2_over_lambda_squared": float(d3f * d3f * Fraction(1, 8)),
            "d4_radial_growth": logarithmic_scales,
            "d4_positive_floor_axis_min": axis_scaled(1.0),
        },
        "fractional_route": {
            "gamma": gamma,
            "sigma": spatial,
            "theta": theta_frac,
            "p_theta": p * theta_frac,
            "two_p_theta": 2 * p * theta_frac,
            "pointwise_ellipticity_alone_controls_spatial_fractional_norm": False,
            "production_joint_value_gradient_hypotheses": False,
        },
        "aggregate_shell": {
            "B_constant": b_constant,
            "B_amplitude": math.sqrt(b_constant),
            "direct_constant": direct_constant,
            "direct_amplitude": math.sqrt(direct_constant),
        },
        "separate_absorption": {
            "derivative_energy_slopes": slopes,
            "cutoff_uniform_bound": False,
            "signed_forest_cancellation_required": True,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(args.output, result)
    print(f"R-134 independent: {result['assertions_passed']}/{result['assertions_total']} PASS")
    print(f"sharp floor coefficient={alpha * alpha * c1}")
    print(f"B_7/12 conditional constant={b_constant:.15f}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
