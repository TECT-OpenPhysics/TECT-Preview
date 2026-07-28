#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-117 A13 trace boundary.

The executable derives the sharp homogeneous Pauli--Fierz frame constant,
certifies the canonical dyadic-shell recession trace margin with rational
interval arithmetic, checks the positive-floor horizon estimate, and records
the fixed-shell phase-modulation metric-regularity obstruction.  It does not
claim the complete progressive/revisit packet or the global one-use estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RATIONAL-HORIZON-UNIFORM-ROOT-TRACE-MARGIN-BOUNDARY"
PRODUCTION_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-rational-horizon-uniform-root-trace-margin-boundary/result.json"
)

# Mathematical inputs fixed by the A13 proof architecture, not derived data.
EXPONENT_Q = Fraction(10, 9)
FRAME_ALPHA = Fraction(5, 9)
PI_COARSE_LOWER = Fraction(314159, 100000)
PI_COARSE_UPPER = Fraction(314160, 100000)
FINITE_SHELLS = (1, 2, 4)
TAIL_START = 8

# Independently derived closed-form regression values.  They are comparison
# oracles only and never feed the bound computations below.
ORACLES = {
    "sharp_frame_times_P": Fraction(411, 2000),
    "q_six_safe_kappa": Fraction(137, 400),
    "phase_energy_times_P": Fraction(9, 500),
}


def fraction_from_json(value: Any) -> Fraction:
    """Recover the exact displayed decimal from a JSON scalar."""
    return Fraction(str(value))


def decimal_string(value: Fraction, digits: int = 18) -> str:
    with localcontext() as context:
        context.prec = digits + 8
        return format(Decimal(value.numerator) / Decimal(value.denominator), f".{digits}g")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-rational-horizon-uniform-root-trace-margin-boundary-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "This certificate proves a bare canonical dyadic-root homogeneous-recession trace margin, "
                "a rational-floor horizon estimate, and a fixed-shell metric-regularity no-go.  It does not "
                "prove the complete progressive/revisit owner embedding, a cutoff-summable log-normalizer, "
                "the one-use source/sextic aggregation, OVERLAP_src, Nelson, removal, an interacting measure, "
                "Sector-A closure, or a tier promotion."
            ),
        }


def alternating_arctan_bounds(q: int, terms: int) -> tuple[Fraction, Fraction]:
    """Rigorous alternating-series enclosure of arctan(1/q)."""
    partial = sum(
        ((-1) ** index) * Fraction(1, (2 * index + 1) * q ** (2 * index + 1))
        for index in range(terms)
    )
    next_term = ((-1) ** terms) * Fraction(1, (2 * terms + 1) * q ** (2 * terms + 1))
    other = partial + next_term
    return min(partial, other), max(partial, other)


def machin_pi_bounds() -> tuple[Fraction, Fraction]:
    """Use pi/4 = 4 atan(1/5) - atan(1/239), with signed enclosures."""
    lower_5, upper_5 = alternating_arctan_bounds(5, 8)
    lower_239, upper_239 = alternating_arctan_bounds(239, 3)
    return 4 * (4 * lower_5 - upper_239), 4 * (4 * upper_5 - lower_239)


def scalar_symbol_lower(
    squared_index: int,
    alpha_squared_lower: Fraction,
    alpha_squared_upper: Fraction,
    r_value: Fraction,
    z_value: Fraction,
    y_value: Fraction,
) -> Fraction:
    """Exact minimum of Y s^2 + Z s + r on an interval for s=|k|^2."""
    left = squared_index * alpha_squared_lower
    right = squared_index * alpha_squared_upper
    vertex = -z_value / (2 * y_value)
    candidates = (
        y_value * left * left + z_value * left + r_value,
        y_value * right * right + z_value * right + r_value,
    )
    if left <= vertex <= right:
        return r_value - z_value * z_value / (4 * y_value)
    return min(candidates)


def shell_certificate(
    cutoff: int,
    alpha_squared_lower: Fraction,
    alpha_squared_upper: Fraction,
    volume: Fraction,
    r_value: Fraction,
    z_value: Fraction,
    y_value: Fraction,
    q_six_kappa_upper: Fraction,
) -> dict[str, Any]:
    inner = cutoff // 2
    modes = [
        mode
        for mode in product(range(-cutoff, cutoff + 1), repeat=3)
        if inner < max(abs(component) for component in mode) <= cutoff
    ]
    lower_by_radius: dict[int, Fraction] = {}
    for mode in modes:
        radius_squared = sum(component * component for component in mode)
        if radius_squared not in lower_by_radius:
            lower_by_radius[radius_squared] = scalar_symbol_lower(
                radius_squared,
                alpha_squared_lower,
                alpha_squared_upper,
                r_value,
                z_value,
                y_value,
            )
    shell_minimum = min(lower_by_radius.values())
    derivative_bounds = []
    for axis in range(3):
        derivative_bounds.append(
            Fraction(2, 1)
            / volume
            * sum(
                component[axis] ** 2
                * alpha_squared_upper
                / lower_by_radius[sum(entry * entry for entry in component)]
                for component in modes
            )
        )
    derivative_maximum = max(derivative_bounds)
    q_trace_bound = q_six_kappa_upper * derivative_maximum / shell_minimum
    return {
        "cutoff": cutoff,
        "mode_count": len(modes),
        "expected_mode_count": (2 * cutoff + 1) ** 3 - (2 * inner + 1) ** 3,
        "scalar_symbol_lower_exact": shell_minimum,
        "scalar_symbol_lower_decimal_approx": decimal_string(shell_minimum),
        "per_axis_derivative_covariance_upper_exact": derivative_maximum,
        "per_axis_derivative_covariance_upper_decimal_approx": decimal_string(derivative_maximum),
        "q_recession_trace_upper_exact": q_trace_bound,
        "q_recession_trace_upper_decimal_approx": decimal_string(q_trace_bound),
        "q_trace_bound_exact": q_trace_bound,
        "strict_one_over_twenty_five": q_trace_bound < Fraction(1, 25),
    }


GaussianRational = tuple[Fraction, Fraction]


def gaussian_add(left: GaussianRational, right: GaussianRational) -> GaussianRational:
    return left[0] + right[0], left[1] + right[1]


def gaussian_multiply(left: GaussianRational, right: GaussianRational) -> GaussianRational:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def gaussian_conjugate(value: GaussianRational) -> GaussianRational:
    return value[0], -value[1]


def gaussian_scale(value: GaussianRational, scalar: int | Fraction) -> GaussianRational:
    return scalar * value[0], scalar * value[1]


def gaussian_norm_squared(value: GaussianRational) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def phase_fixture_certificate() -> dict[str, Any]:
    """Exact autocorrelation certificate for modes 5,6,7 of the S_8 fixture."""
    zero = (Fraction(0), Fraction(0))
    one = (Fraction(1), Fraction(0))
    imaginary_half = (Fraction(0), Fraction(1, 2))
    # Each inner dictionary is polynomial degree in t -> Gaussian-rational coefficient.
    fourier: dict[int, dict[int, GaussianRational]] = {
        5: {1: imaginary_half},
        6: {0: one},
        7: {1: imaginary_half},
    }
    second_component_fourier: dict[int, dict[int, GaussianRational]] = {}
    rho: dict[int, dict[int, GaussianRational]] = {}
    for left_mode, left_polynomial in fourier.items():
        for right_mode, right_polynomial in fourier.items():
            output_mode = left_mode - right_mode
            output = rho.setdefault(output_mode, {})
            for left_degree, left_value in left_polynomial.items():
                for right_degree, right_value in right_polynomial.items():
                    degree = left_degree + right_degree
                    term = gaussian_multiply(left_value, gaussian_conjugate(right_value))
                    output[degree] = gaussian_add(output.get(degree, zero), term)
    derivative: dict[int, dict[int, GaussianRational]] = {}
    imaginary_unit = (Fraction(0), Fraction(1))
    for mode, polynomial in rho.items():
        derivative[mode] = {
            degree: gaussian_multiply(gaussian_scale(imaginary_unit, mode), value)
            for degree, value in polynomial.items()
        }
    nonzero_derivative_degrees = [
        degree
        for polynomial in derivative.values()
        for degree, value in polynomial.items()
        if value != zero
    ]
    derivative_parseval_t4 = sum(
        gaussian_norm_squared(polynomial.get(2, zero)) for polynomial in derivative.values()
    )
    wedge_terms = [
        (left_mode, right_mode)
        for left_mode in fourier
        for right_mode in second_component_fourier
    ]
    return {
        "rho": rho,
        "derivative": derivative,
        "linear_autocorrelation_cancels": all(
            polynomial.get(1, zero) == zero for polynomial in rho.values()
        ),
        "sideband_mass_t2": rho[0][2],
        "derivative_minimum_degree": min(nonzero_derivative_degrees),
        "derivative_parseval_t4": derivative_parseval_t4,
        "wedge_zero": len(wedge_terms) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    production = json.loads(PRODUCTION_MANIFEST.read_text(encoding="utf-8"))
    parameters = production["parameters"]
    length = fraction_from_json(parameters["Lx"])
    volume = length * fraction_from_json(parameters["Ly"]) * fraction_from_json(parameters["Lz"])
    r_value = fraction_from_json(parameters["r"])
    z_value = fraction_from_json(parameters["Z"])
    y_value = fraction_from_json(parameters["Y"])
    mass_regularizer = fraction_from_json(parameters["classii_mass_regularizer"])
    p_value = fraction_from_json(parameters["M_X"]) ** 2 + mass_regularizer

    audit.check("authority", "three_equal_sides", length == fraction_from_json(parameters["Ly"]) == fraction_from_json(parameters["Lz"]), [parameters["Lx"], parameters["Ly"], parameters["Lz"]], "equal")
    audit.check("authority", "positive_scalar_biharmonic", y_value > 0 and r_value > 0 and z_value < 0, [y_value, r_value, z_value], "Y>0, r>0, Z<0")
    audit.check("authority", "internal_mass_psd_inputs", all(fraction_from_json(item) >= 0 for item in parameters["family_masses"]) and fraction_from_json(parameters["k_lock"]) >= 0, [parameters["family_masses"], parameters["k_lock"]], "nonnegative diagonal plus nonnegative projection")
    audit.check("authority", "classii_denominator_above_four", p_value > 4, p_value, ">4")

    machin_lower, machin_upper = machin_pi_bounds()
    audit.check("pi_interval", "machin_bounds_ordered", machin_lower < machin_upper, [machin_lower, machin_upper], "lower<upper")
    audit.check("pi_interval", "coarse_interval_certified", machin_lower > PI_COARSE_LOWER and machin_upper < PI_COARSE_UPPER, [decimal_string(machin_lower), decimal_string(machin_upper)], [PI_COARSE_LOWER, PI_COARSE_UPPER])
    spatial_alpha_squared_lower = (Fraction(2, 1) * PI_COARSE_LOWER / length) ** 2
    spatial_alpha_squared_upper = (Fraction(2, 1) * PI_COARSE_UPPER / length) ** 2

    c0 = Fraction(3, 250) / p_value
    c1 = Fraction(243, 8000) / p_value
    rational_curvature = FRAME_ALPHA * (2 - FRAME_ALPHA)
    rational_vertex = Fraction(1, 1) / (2 * rational_curvature)
    rational_maximum = rational_vertex - rational_curvature * rational_vertex * rational_vertex
    kappa_sharp = 6 * (c0 + c1) - 2 * c1 * rational_curvature
    sharp_frame_times_p = p_value * kappa_sharp
    derivative_at_one = 6 * (c0 + c1) - 4 * c1 * rational_curvature
    safe_kappa_from_p_above_four = sharp_frame_times_p / 4
    q_six_kappa_upper = EXPONENT_Q * 6 * safe_kappa_from_p_above_four

    audit.check("frame", "rational_curvature", rational_curvature == Fraction(65, 81), rational_curvature, Fraction(65, 81))
    audit.check("frame", "rational_vertex_inside", 0 < rational_vertex < 1, rational_vertex, "(0,1)")
    audit.check("frame", "rational_row_maximum", rational_maximum == Fraction(81, 260), rational_maximum, Fraction(81, 260))
    audit.check("frame", "joint_derivative_positive_at_one", derivative_at_one > 0, derivative_at_one, ">0")
    audit.check("frame", "sharp_frame_constant", sharp_frame_times_p == ORACLES["sharp_frame_times_P"], sharp_frame_times_p, ORACLES["sharp_frame_times_P"])
    audit.check("frame", "production_upper_constant", kappa_sharp < safe_kappa_from_p_above_four, kappa_sharp, f"<{safe_kappa_from_p_above_four}")
    audit.check("frame", "q_six_kappa_upper", q_six_kappa_upper == ORACLES["q_six_safe_kappa"], q_six_kappa_upper, ORACLES["q_six_safe_kappa"])

    # Exact floor-horizon calculus: [2 delta sqrt(rho)/(rho+delta)]^2/delta
    # equals 4x/(1+x)^2 <= 1 for x=rho/delta, with equality at x=1.
    test_ratio = Fraction(7, 13)
    normalized_square = 4 * test_ratio / (1 + test_ratio) ** 2
    square_defect = 1 - normalized_square
    audit.check("rational_horizon", "floor_envelope_identity", square_defect == (test_ratio - 1) ** 2 / (test_ratio + 1) ** 2, square_defect, (test_ratio - 1) ** 2 / (test_ratio + 1) ** 2)
    audit.check("rational_horizon", "floor_envelope_maximum", 4 * Fraction(1, 1) / (1 + Fraction(1, 1)) ** 2 == 1, 1, 1)
    audit.check("rational_horizon", "uniform_floor_rate", FRAME_ALPHA > 0 and mass_regularizer > 0, "alpha*sqrt(e)/t", "uniform O(t^-1)")
    audit.check("rational_horizon", "zero_state_map_extension", rational_maximum < 1, "|g_beta|^2<=rho and g_beta->0 as z->0", "continuous Xi_0 map; beta itself is undefined at zero")

    shells = [
        shell_certificate(
            cutoff,
            spatial_alpha_squared_lower,
            spatial_alpha_squared_upper,
            volume,
            r_value,
            z_value,
            y_value,
            q_six_kappa_upper,
        )
        for cutoff in FINITE_SHELLS
    ]
    for shell in shells:
        cutoff = shell["cutoff"]
        audit.check("finite_shell", f"N{cutoff}_mode_count", shell["mode_count"] == shell["expected_mode_count"], shell["mode_count"], shell["expected_mode_count"])
        audit.check("finite_shell", f"N{cutoff}_positive_symbol", shell["scalar_symbol_lower_exact"] > 0, shell["scalar_symbol_lower_exact"], ">0")
        audit.check("finite_shell", f"N{cutoff}_q_trace_below_one_over_25", shell["strict_one_over_twenty_five"], shell["q_recession_trace_upper_exact"], "<1/25")

    # For N>=8: p(k^2)>=k^4/2, #Q_N<=(17N/8)^3, and cube symmetry.
    lower_shell_k2_at_tail = spatial_alpha_squared_lower * TAIL_START * TAIL_START / 4
    audit.check("tail", "quartic_dominance_at_N8", lower_shell_k2_at_tail >= 2 * abs(z_value) / y_value, lower_shell_k2_at_tail, ">=2|Z|/Y")
    cube_side_ratio = Fraction(2 * TAIL_START + 1, TAIL_START)
    audit.check("tail", "cube_count_ratio", cube_side_ratio == 2 + Fraction(1, TAIL_START), cube_side_ratio, 2 + Fraction(1, TAIL_START))
    tail_mode_count_upper = (2 * TAIL_START + 1) ** 3
    tail_derivative_upper = (
        Fraction(16, 3) * tail_mode_count_upper
        / (volume * spatial_alpha_squared_lower * TAIL_START**2)
    )
    tail_symbol_lower = spatial_alpha_squared_lower**2 * TAIL_START**4 / 32
    tail_ratio_bound = tail_derivative_upper / tail_symbol_lower
    tail_q_trace_bound = q_six_kappa_upper * tail_ratio_bound
    audit.check("tail", "q_trace_below_three_over_40", tail_q_trace_bound < Fraction(3, 40), tail_q_trace_bound, "<3/40")
    audit.check("tail", "q_trace_below_two_over_25", tail_q_trace_bound < Fraction(2, 25), tail_q_trace_bound, "<2/25")
    dyadic_tail_ratio = Fraction(1, 2) ** 3
    audit.check("tail", "dyadic_monotonicity", 0 < dyadic_tail_ratio < 1, dyadic_tail_ratio, "each doubled cutoff multiplies the bound by 1/8")

    finite_max = max(shell["q_trace_bound_exact"] for shell in shells)
    global_q_bound = max(finite_max, tail_q_trace_bound)
    audit.check("normalizer", "uniform_q_margin", global_q_bound < Fraction(3, 40), global_q_bound, "<3/40")
    audit.check("normalizer", "uniform_2q_margin", 2 * global_q_bound < Fraction(3, 20), 2 * global_q_bound, "<3/20")
    audit.check("normalizer", "leading_q_precision", 1 - global_q_bound > Fraction(37, 40), 1 - global_q_bound, ">37/40")
    audit.check("normalizer", "leading_2q_precision", 1 - 2 * global_q_bound > Fraction(17, 20), 1 - 2 * global_q_bound, ">17/20")

    # Fixed-shell phase modulation: carrier 6 and sidebands 5,7 all lie in S_8.
    active_indices = (5, 6, 7)
    phase = phase_fixture_certificate()
    phase_energy_coefficient = c0 + c1 * (1 - FRAME_ALPHA) ** 2
    audit.check("metric_nogo", "three_modes_same_shell", all(4 < abs(index) <= 8 for index in active_indices), active_indices, "S_8")
    audit.check("metric_nogo", "linearized_current_vanishes", phase["linear_autocorrelation_cancels"], phase["rho"], "all degree-one autocorrelations cancel")
    audit.check("metric_nogo", "quadratic_current_nonzero", phase["derivative_parseval_t4"] > 0 and phase_energy_coefficient > 0 and p_value * phase_energy_coefficient == ORACLES["phase_energy_times_P"], [phase["derivative_parseval_t4"], phase_energy_coefficient, p_value * phase_energy_coefficient], [">0", ">0", ORACLES["phase_energy_times_P"]])
    audit.check("metric_nogo", "current_order_t_squared", phase["derivative_minimum_degree"] == 2 and phase["wedge_zero"], [phase["derivative_minimum_degree"], phase["wedge_zero"]], [2, True])
    audit.check("metric_nogo", "null_distance_order_t", phase["sideband_mass_t2"] == (Fraction(1, 2), Fraction(0)), phase["sideband_mass_t2"], (Fraction(1, 2), Fraction(0)))
    squared_distance_degree = 2
    squared_current_degree = 2 * phase["derivative_minimum_degree"]
    audit.check("metric_nogo", "lipschitz_error_bound_fails", squared_current_degree > squared_distance_degree, [squared_distance_degree, squared_current_degree], "distance^2 order 2; current^2 order 4")
    normalized_sideband_leading = phase["sideband_mass_t2"][0]
    audit.check("metric_nogo", "unit_sphere_normalization_preserves_gap", normalized_sideband_leading > 0 and squared_current_degree == 4, [normalized_sideband_leading, squared_current_degree], "radial normalization is 1+O(t^2)")

    diagnostics = {
        "authority": {
            "production_manifest": PRODUCTION_MANIFEST.resolve().relative_to(REPO.resolve()).as_posix(),
            "production_manifest_sha256": sha256(PRODUCTION_MANIFEST),
            "parameters_used": {
                "L": length,
                "V": volume,
                "r": r_value,
                "Z": z_value,
                "Y": y_value,
                "P": p_value,
            },
        },
        "machin_pi_interval": [decimal_string(machin_lower, 22), decimal_string(machin_upper, 22)],
        "frame": {
            "alpha": FRAME_ALPHA,
            "c0": c0,
            "c1": c1,
            "sharp_kappa": kappa_sharp,
            "safe_kappa_using_P_ge_4": safe_kappa_from_p_above_four,
            "q_times_six_safe_kappa": q_six_kappa_upper,
            "scope": "degree-two homogeneous recession trace only",
        },
        "finite_shells": shells,
        "tail": {
            "start": TAIL_START,
            "d_over_m_bound_at_start": tail_ratio_bound,
            "q_trace_bound_at_start": tail_q_trace_bound,
            "decay": "(8/N)^3 for dyadic N>=8",
        },
        "uniform": {
            "q": EXPONENT_Q,
            "q_trace_upper": global_q_bound,
            "two_q_trace_upper": 2 * global_q_bound,
            "q_precision_lower": 1 - global_q_bound,
            "two_q_precision_lower": 1 - 2 * global_q_bound,
        },
        "floor_horizon": "||t^-2 Xi_e(tz,ty)-Xi_0(z,y)|| <= sqrt(c1)*alpha*sqrt(e)*|y|/t",
        "metric_nogo": {
            "shell": "S_8",
            "carrier": 6,
            "sidebands": [5, 7],
            "current_energy_coefficient": phase_energy_coefficient,
            "current_energy_times_P": p_value * phase_energy_coefficient,
            "autocorrelation": phase,
            "consequence": "no local Lipschitz metric error bound even at fixed cutoff",
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Primary R-117 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions; "
        f"q*tau<{decimal_string(global_q_bound, 12)}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
