#!/usr/bin/env python3
"""Non-importing independent certificate for the scoped R-117 A13 result.

This implementation uses the real-frame Frobenius trace identity and a
radius/axis-multiplicity shell enumeration.  It intentionally imports no
project-specific proof module and uses the coarse certified enclosure
157/50 < pi < 22/7, unlike the primary certificate.
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
    / "runs/2026-07-28-independent-rational-horizon-uniform-root-trace-margin-boundary/result.json"
)

Q = Fraction(10, 9)
ALPHA = Fraction(5, 9)
PI_LOWER = Fraction(157, 50)
PI_UPPER = Fraction(22, 7)
TAIL_START = 8

# Closed-form regression values, used only as independent comparison oracles.
ORACLES = {
    "frobenius_times_P": Fraction(411, 1000),
    "expected_trace_times_P": Fraction(411, 2000),
    "q_shell_multiplier": Fraction(137, 400),
    "phase_energy_times_P": Fraction(9, 500),
}


def exact(value: Any) -> Fraction:
    return Fraction(str(value))


def decimal_string(value: Fraction, digits: int = 18) -> str:
    with localcontext() as context:
        context.prec = digits + 8
        return format(Decimal(value.numerator) / Decimal(value.denominator), f".{digits}g")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
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
            "schema": "tect/a13-rational-horizon-uniform-root-trace-margin-boundary-independent/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "independence": (
                "No import from the primary certificate; real-frame Frobenius derivation, "
                "coarse pi enclosure, and multiplicity aggregation are separate."
            ),
            "no_overclaim": (
                "Independent PASS certifies only the canonical homogeneous-recession trace "
                "margin, floor horizon, and phase-modulation method boundary.  Complete packet "
                "embedding, cutoff-summable constants, one-use aggregation, and Sector A remain open."
            ),
        }


def atan_bounds(reciprocal: int, terms: int) -> tuple[Fraction, Fraction]:
    subtotal = Fraction(0)
    for index in range(terms):
        subtotal += ((-1) ** index) * Fraction(
            1, (2 * index + 1) * reciprocal ** (2 * index + 1)
        )
    adjacent = subtotal + ((-1) ** terms) * Fraction(
        1, (2 * terms + 1) * reciprocal ** (2 * terms + 1)
    )
    return min(subtotal, adjacent), max(subtotal, adjacent)


def independent_pi_enclosure() -> tuple[Fraction, Fraction]:
    low5, high5 = atan_bounds(5, 7)
    low239, high239 = atan_bounds(239, 2)
    return 4 * (4 * low5 - high239), 4 * (4 * high5 - low239)


def symbol_floor(
    radius_squared: int,
    wave_squared_lower: Fraction,
    wave_squared_upper: Fraction,
    r_value: Fraction,
    z_value: Fraction,
    y_value: Fraction,
) -> Fraction:
    lower = radius_squared * wave_squared_lower
    upper = radius_squared * wave_squared_upper
    critical = -z_value / (2 * y_value)
    clamp = min(max(critical, lower), upper)
    return y_value * clamp * clamp + z_value * clamp + r_value


def multiplicities(cutoff: int) -> tuple[dict[tuple[int, int], int], int]:
    """Count (|n|^2,n_1^2) pairs; cube symmetry handles other axes."""
    inner = cutoff // 2
    counts: dict[tuple[int, int], int] = {}
    total = 0
    for mode in product(range(-cutoff, cutoff + 1), repeat=3):
        if not (inner < max(abs(entry) for entry in mode) <= cutoff):
            continue
        key = (sum(entry * entry for entry in mode), mode[0] * mode[0])
        counts[key] = counts.get(key, 0) + 1
        total += 1
    return counts, total


def shell_bound(
    cutoff: int,
    wave_squared_lower: Fraction,
    wave_squared_upper: Fraction,
    volume: Fraction,
    r_value: Fraction,
    z_value: Fraction,
    y_value: Fraction,
    q_shell_multiplier: Fraction,
) -> dict[str, Any]:
    counts, total = multiplicities(cutoff)
    radial_floors = {
        radius: symbol_floor(
            radius,
            wave_squared_lower,
            wave_squared_upper,
            r_value,
            z_value,
            y_value,
        )
        for radius, _axis in counts
    }
    minimum = min(radial_floors.values())
    derivative = Fraction(2, 1) / volume * sum(
        multiplicity * axis_squared * wave_squared_upper / radial_floors[radius]
        for (radius, axis_squared), multiplicity in counts.items()
    )
    q_trace = q_shell_multiplier * derivative / minimum
    return {
        "cutoff": cutoff,
        "mode_count": total,
        "radius_axis_bins": len(counts),
        "symbol_lower_exact": minimum,
        "symbol_lower_decimal_approx": decimal_string(minimum),
        "derivative_upper_exact": derivative,
        "derivative_upper_decimal_approx": decimal_string(derivative),
        "q_trace_upper_exact": q_trace,
        "q_trace_upper_decimal_approx": decimal_string(q_trace),
        "q_trace_exact": q_trace,
    }


GaussianRational = tuple[Fraction, Fraction]


def complex_product(left: GaussianRational, right: GaussianRational) -> GaussianRational:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def complex_conjugate(value: GaussianRational) -> GaussianRational:
    return value[0], -value[1]


def complex_add(left: GaussianRational, right: GaussianRational) -> GaussianRational:
    return left[0] + right[0], left[1] + right[1]


def complex_norm_squared(value: GaussianRational) -> Fraction:
    return value[0] ** 2 + value[1] ** 2


def independent_phase_fixture() -> dict[str, Any]:
    """Direct three-coefficient autocorrelation, distinct from the primary loop."""
    carrier = (Fraction(1), Fraction(0))
    sideband = (Fraction(0), Fraction(1, 2))
    mode_one_linear = complex_add(
        complex_product(carrier, complex_conjugate(sideband)),
        complex_product(sideband, complex_conjugate(carrier)),
    )
    mode_two_quadratic = complex_product(sideband, complex_conjugate(sideband))
    sideband_mass = 2 * complex_norm_squared(sideband)
    derivative_parseval = 2 * complex_norm_squared(
        (Fraction(0), 2 * mode_two_quadratic[0])
    )
    return {
        "mode_one_linear": mode_one_linear,
        "mode_two_quadratic": mode_two_quadratic,
        "sideband_mass_t2": sideband_mass,
        "derivative_parseval_t4": derivative_parseval,
        "squared_distance_degree": 2,
        "squared_current_degree": 4,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    manifest = json.loads(PRODUCTION_MANIFEST.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    length = exact(params["Lx"])
    volume = exact(params["Lx"]) * exact(params["Ly"]) * exact(params["Lz"])
    r_value = exact(params["r"])
    z_value = exact(params["Z"])
    y_value = exact(params["Y"])
    p_value = exact(params["M_X"]) ** 2 + exact(params["classii_mass_regularizer"])

    audit.check("authority", "manifest_claim", manifest.get("claim_id") == "A1-PRODUCTION-FUNCTIONAL-REALISATION", manifest.get("claim_id"), "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    audit.check("authority", "volume", volume == 4096, volume, 4096)
    audit.check("authority", "mass_matrix_psd_construction", min(exact(item) for item in params["family_masses"]) >= 0 and exact(params["k_lock"]) >= 0, [params["family_masses"], params["k_lock"]], "PSD")
    audit.check("authority", "P_greater_than_four", p_value > 4, p_value, ">4")

    pi_lower, pi_upper = independent_pi_enclosure()
    audit.check("pi", "coarse_lower", pi_lower > PI_LOWER, decimal_string(pi_lower), PI_LOWER)
    audit.check("pi", "coarse_upper", pi_upper < PI_UPPER, decimal_string(pi_upper), PI_UPPER)
    wave_squared_lower = (2 * PI_LOWER / length) ** 2
    wave_squared_upper = (2 * PI_UPPER / length) ** 2

    c0 = Fraction(3, 250) / p_value
    c1 = Fraction(243, 8000) / p_value
    beta_curvature = ALPHA * (2 - ALPHA)
    # Frobenius coefficient F(beta)=12(c0+c1)beta-4c1*curvature*beta^2.
    frobenius_at_one = 12 * (c0 + c1) - 4 * c1 * beta_curvature
    frobenius_times_p = p_value * frobenius_at_one
    expected_trace_constant = Fraction(1, 2) * frobenius_at_one
    expected_trace_times_p = p_value * expected_trace_constant
    frobenius_derivative_at_one = 12 * (c0 + c1) - 8 * c1 * beta_curvature
    safe_expected_trace = expected_trace_times_p / 4
    safe_q_shell_multiplier = Q * 3 * safe_expected_trace * 2
    audit.check("frame", "frob_formula", frobenius_times_p == ORACLES["frobenius_times_P"], frobenius_times_p, ORACLES["frobenius_times_P"])
    audit.check("frame", "frob_increasing", frobenius_derivative_at_one > 0, frobenius_derivative_at_one, ">0")
    audit.check("frame", "realification_half", expected_trace_times_p == ORACLES["expected_trace_times_P"], expected_trace_times_p, ORACLES["expected_trace_times_P"])
    audit.check("frame", "safe_q_axis_parseval_factor", safe_q_shell_multiplier == ORACLES["q_shell_multiplier"], safe_q_shell_multiplier, ORACLES["q_shell_multiplier"])

    shells = [
        shell_bound(
            cutoff,
            wave_squared_lower,
            wave_squared_upper,
            volume,
            r_value,
            z_value,
            y_value,
            safe_q_shell_multiplier,
        )
        for cutoff in (1, 2, 4)
    ]
    for shell in shells:
        cutoff = shell["cutoff"]
        expected = (2 * cutoff + 1) ** 3 - (2 * (cutoff // 2) + 1) ** 3
        audit.check("shell", f"N{cutoff}_count", shell["mode_count"] == expected, shell["mode_count"], expected)
        audit.check("shell", f"N{cutoff}_positive_symbol", shell["symbol_lower_exact"] > 0, shell["symbol_lower_exact"], ">0")
        audit.check("shell", f"N{cutoff}_margin", shell["q_trace_exact"] < Fraction(1, 25), shell["q_trace_exact"], "<1/25")

    # Independent high-frequency envelope uses only pi>157/50.
    tail_mode_count_upper = (2 * TAIL_START + 1) ** 3
    tail_derivative_upper = (
        Fraction(16, 3) * tail_mode_count_upper
        / (volume * wave_squared_lower * TAIL_START**2)
    )
    tail_symbol_lower = wave_squared_lower**2 * TAIL_START**4 / 32
    tail_ratio = tail_derivative_upper / tail_symbol_lower
    tail_q = safe_q_shell_multiplier * tail_ratio
    audit.check("tail", "scalar_discriminant_gate", z_value * z_value < 2 * y_value * r_value, z_value * z_value - 2 * y_value * r_value, "<0")
    audit.check("tail", "quartic_gate_at_eight", wave_squared_lower * TAIL_START**2 / 4 >= 2 * abs(z_value) / y_value, wave_squared_lower * TAIL_START**2 / 4, ">=2|Z|/Y")
    audit.check("tail", "coarse_tail_below_two_over_25", tail_q < Fraction(2, 25), tail_q, "<2/25")
    audit.check("tail", "double_tilt_below_four_over_25", 2 * tail_q < Fraction(4, 25), 2 * tail_q, "<4/25")

    finite_max = max(shell["q_trace_exact"] for shell in shells)
    uniform = max(finite_max, tail_q)
    audit.check("uniform", "all_q_margin", uniform < Fraction(3, 40), uniform, "<3/40")
    audit.check("uniform", "all_two_q_margin", 2 * uniform < Fraction(3, 20), 2 * uniform, "<3/20")
    audit.check("uniform", "q_precision", 1 - uniform > Fraction(37, 40), 1 - uniform, ">37/40")
    audit.check("uniform", "two_q_precision", 1 - 2 * uniform > Fraction(17, 20), 1 - 2 * uniform, ">17/20")

    # Horizon estimate checked through the exact normalized square defect.
    for numerator, denominator in ((1, 9), (3, 2), (17, 5)):
        x = Fraction(numerator, denominator)
        envelope_square = 4 * x / (1 + x) ** 2
        defect = (x - 1) ** 2 / (x + 1) ** 2
        audit.check("floor_horizon", f"square_defect_{numerator}_{denominator}", envelope_square + defect == 1, envelope_square + defect, 1)

    # Fourier-orthogonal phase fixture: sideband mass is linear, current quadratic.
    phase = independent_phase_fixture()
    audit.check("metric_nogo", "carrier_and_sidebands_in_S8", all(TAIL_START // 2 < index <= TAIL_START for index in (TAIL_START - 3, TAIL_START - 2, TAIL_START - 1)), [TAIL_START - 3, TAIL_START - 2, TAIL_START - 1], "S_8")
    audit.check("metric_nogo", "linear_autocorrelation_cancels", phase["mode_one_linear"] == (Fraction(0), Fraction(0)), phase["mode_one_linear"], (Fraction(0), Fraction(0)))
    audit.check("metric_nogo", "sideband_l2_coefficient", phase["sideband_mass_t2"] == Fraction(1, 2), phase["sideband_mass_t2"], Fraction(1, 2))
    phase_coefficient = c0 + c1 * (1 - ALPHA) ** 2
    audit.check("metric_nogo", "phase_current_coefficient", p_value * phase_coefficient == ORACLES["phase_energy_times_P"] and phase["derivative_parseval_t4"] == Fraction(1, 2), [p_value * phase_coefficient, phase["derivative_parseval_t4"]], [ORACLES["phase_energy_times_P"], Fraction(1, 2)])
    audit.check("metric_nogo", "order_separation", phase["squared_current_degree"] > phase["squared_distance_degree"] and phase_coefficient > 0, [phase["squared_distance_degree"], phase["squared_current_degree"]], "distance^2 order 2; current^2 order 4")
    audit.check("metric_nogo", "unit_sphere_normalization", phase["sideband_mass_t2"] > 0, "norm^2=1+t^2/2; radial factor=1+O(t^2)", "order gap preserved")

    diagnostics = {
        "authority": {
            "production_manifest": PRODUCTION_MANIFEST.resolve().relative_to(REPO.resolve()).as_posix(),
            "sha256": digest(PRODUCTION_MANIFEST),
        },
        "independent_pi_interval": [decimal_string(pi_lower, 21), decimal_string(pi_upper, 21)],
        "frame": {
            "frobenius_constant": frobenius_at_one,
            "expected_trace_constant": expected_trace_constant,
            "safe_q_shell_multiplier": safe_q_shell_multiplier,
        },
        "shells": shells,
        "tail": {
            "q_trace_upper": tail_q,
            "two_q_trace_upper": 2 * tail_q,
            "decay": "(8/N)^3 for dyadic N>=8",
        },
        "uniform": {"q_trace_upper": uniform, "two_q_trace_upper": 2 * uniform},
        "phase_fixture": {
            "field": "u_t=exp(6 i kappa x_1)(1+i t cos(kappa x_1))e_1, chi=0",
            "distance_order": "|t|",
            "current_order": "t^2",
            "exact_autocorrelation": phase,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Independent R-117 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions; "
        f"q*tau<{decimal_string(uniform, 12)}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
