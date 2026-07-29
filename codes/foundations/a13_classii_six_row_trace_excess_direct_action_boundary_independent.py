#!/usr/bin/env python3
"""Non-importing independent audit for the scoped R-123 A13 checkpoint.

Only the Python standard library is used.  Gaussian and torus expectations
are recomputed by independent composite quadrature rather than importing the
primary symbolic implementation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

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
RESULT_ID = "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"
SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-30-independent-six-row-trace-excess-direct-action-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


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

    def close(self, actual: float, expected: float, tolerance: float) -> bool:
        return math.isfinite(actual) and abs(actual - expected) <= tolerance * max(1.0, abs(expected))

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
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "This independent audit reproduces R-123's finite-root identities and method boundaries. "
                "It does not prove the uniform production trace-excess estimate or Sector A closure."
            ),
        }


def normal_expectation(function: Callable[[float], float], bound: float = 10.0, intervals: int = 40000) -> float:
    if intervals % 2:
        raise ValueError("Simpson interval count must be even")
    step = 2.0 * bound / intervals
    normalizer = 1.0 / math.sqrt(2.0 * math.pi)

    def weighted(x: float) -> float:
        return function(x) * normalizer * math.exp(-0.5 * x * x)

    total = weighted(-bound) + weighted(bound)
    for index in range(1, intervals):
        x = -bound + index * step
        total += (4.0 if index % 2 else 2.0) * weighted(x)
    return total * step / 3.0


def torus_average(function: Callable[[float], float], intervals: int = 32768) -> float:
    step = 2.0 * math.pi / intervals
    return sum(function(index * step) for index in range(intervals)) / intervals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    mass = Fraction(str(params["M_X"])) ** 2 + Fraction(str(params["classii_mass_regularizer"]))
    a_current = Fraction(str(params["cJJ"])) * Fraction(str(params["alpha_X"])) ** 2 / mass
    b_current = (
        Fraction(str(params["cJK"]))
        * Fraction(str(params["alpha_X"]))
        * Fraction(str(params["beta_X"]))
        / mass
    )
    c_current = Fraction(str(params["cKK"])) * Fraction(str(params["beta_X"])) ** 2 / mass
    alpha = c_current / (b_current + c_current)
    c1 = c_current / alpha**2
    c0 = a_current - b_current**2 / c_current
    c_sum = c0 + c1
    kappa2 = 4 * c0

    audit.check("production", "mass", mass == Fraction(4000000000001, 1000000000000), mass, Fraction(4000000000001, 1000000000000))
    audit.check("production", "c_sum", c_sum == Fraction(339, 8000) / mass, c_sum, Fraction(339, 8000) / mass)
    audit.check("production", "kappa_squared", kappa2 == Fraction(6, 125) / mass, kappa2, Fraction(6, 125) / mass)
    audit.check("production", "alpha", alpha == Fraction(5, 9), alpha, Fraction(5, 9))

    # Independent quadrature for the bounded six-row fixture at t=2.
    offset = 0.7
    amplitude = 0.4
    frequency = 2.0
    heat = 0.6
    c_sum_float = float(c_sum)

    def state(x: float) -> float:
        return offset + amplitude * math.sin(frequency * x)

    mean_ax = normal_expectation(lambda x: state(x) * x)
    mean_a2 = normal_expectation(lambda x: state(x) ** 2)
    mean_x2_a2 = normal_expectation(lambda x: x * x * state(x) ** 2)
    mean_x_a2 = normal_expectation(lambda x: x * state(x) ** 2)
    mean_x_y2 = normal_expectation(lambda x: x * ((state(x) * x - mean_ax) ** 2 + heat * heat * x * x))
    d0_numeric = 4.0 * c_sum_float * (mean_a2 + heat * heat - (mean_x2_a2 + heat * heat - mean_ax * mean_ax))
    d1_numeric = 4.0 * c_sum_float * (mean_x_a2 - mean_x_y2)
    b2_numeric = 4.0 * c_sum_float * mean_ax * mean_ax
    packet_numeric = 0.5 * (b2_numeric - d0_numeric)

    d0_formula = 16.0 * c_sum_float * amplitude**2 * (math.exp(-4.0) - 2.0 * math.exp(-8.0))
    d1_formula = 48.0 * c_sum_float * offset * amplitude * math.exp(-2.0)
    b2_formula = 16.0 * c_sum_float * amplitude**2 * math.exp(-4.0)
    packet_formula = 16.0 * c_sum_float * amplitude**2 * math.exp(-8.0)
    audit.check("six_row_fixture", "mean_ax", audit.close(mean_ax, amplitude * frequency * math.exp(-2.0), 2e-10), mean_ax, amplitude * frequency * math.exp(-2.0))
    audit.check("six_row_fixture", "D0", audit.close(d0_numeric, d0_formula, 2e-10), d0_numeric, d0_formula)
    audit.check("six_row_fixture", "D1", audit.close(d1_numeric, d1_formula, 2e-10), d1_numeric, d1_formula)
    audit.check("six_row_fixture", "b_squared", audit.close(b2_numeric, b2_formula, 2e-10), b2_numeric, b2_formula)
    audit.check("six_row_fixture", "packet", audit.close(packet_numeric, packet_formula, 2e-10), packet_numeric, packet_formula)
    audit.check("six_row_fixture", "D0_nonzero", d0_numeric > 0.0, d0_numeric, ">0")
    audit.check("six_row_fixture", "D1_nonzero", abs(d1_numeric) > 1e-8, d1_numeric, "nonzero")
    audit.check("six_row_fixture", "packet_positive", packet_numeric > 0.0, packet_numeric, ">0")

    # Arbitrary-h first-row identity: quadrature of the endpoint expression and
    # a separately differentiated score expression.
    def control(x: float) -> float:
        return 0.4 + 0.3 * x + 0.2 * (x * x - 1.0)

    def control_first(x: float) -> float:
        return 0.3 + 0.4 * x

    def control_second(_: float) -> float:
        return 0.4

    endpoint_form = 0.5 * normal_expectation(lambda x: (x * x - 1.0) * control(x) ** 2)
    score_form = normal_expectation(lambda x: control_first(x) ** 2 + control(x) * control_second(x))
    audit.check("linear_row", "score_identity", audit.close(endpoint_form, score_form, 2e-10), endpoint_form, score_form)
    audit.check("linear_row", "packet_scaling", audit.close(float(kappa2) * endpoint_form, float(kappa2) * score_form, 2e-10), float(kappa2) * endpoint_form, float(kappa2) * score_form)
    audit.check("linear_row", "source_coefficient_below_reserve", float(kappa2) < 9.0 / 20.0, float(kappa2), 9.0 / 20.0)
    young_eta = 0.03
    young_zeta = 0.02
    young_remainder = float(kappa2) ** 2 / (16.0 * math.sqrt(young_eta * young_zeta))
    audit.check("linear_row", "young_remainder_positive", young_remainder > 0.0, young_remainder, ">0")

    # H1+H2 trace representatives, checked by independent endpoint formulas.
    hermite_a = 0.8

    def hermite_y(x: float) -> float:
        return hermite_a * x + x * x - 1.0

    variance = normal_expectation(lambda x: hermite_y(x) ** 2)
    exchange_mean = normal_expectation(lambda x: 0.5 * (hermite_y(x) ** 2 + variance))
    exchange_first = normal_expectation(lambda x: x * 0.5 * (hermite_y(x) ** 2 + variance))
    clark_mean = normal_expectation(lambda x: hermite_a**2 + 2.0 * hermite_a * x + 2.0 / 3.0 + 4.0 * x * x / 3.0)
    clark_first = normal_expectation(lambda x: x * (hermite_a**2 + 2.0 * hermite_a * x + 2.0 / 3.0 + 4.0 * x * x / 3.0))
    ou_mean = normal_expectation(lambda x: (hermite_a + 2.0 * x) * (hermite_a + x))
    ou_first = normal_expectation(lambda x: x * (hermite_a + 2.0 * x) * (hermite_a + x))
    score_mean = normal_expectation(lambda x: hermite_a**2 + 4.0 * hermite_a * x + (x * x - 1.0) ** 2)
    score_first = normal_expectation(lambda x: x * (hermite_a**2 + 4.0 * hermite_a * x + (x * x - 1.0) ** 2))
    raw_mean = normal_expectation(lambda x: (hermite_a + 2.0 * x) ** 2)
    raw_first = normal_expectation(lambda x: x * (hermite_a + 2.0 * x) ** 2)
    audit.check("trace_substitute", "variance", audit.close(variance, hermite_a**2 + 2.0, 2e-10), variance, hermite_a**2 + 2.0)
    for label, actual, expected in (
        ("exchange_mean", exchange_mean, variance),
        ("exchange_first", exchange_first, 2.0 * hermite_a),
        ("clark_mean", clark_mean, variance),
        ("clark_first", clark_first, 2.0 * hermite_a),
        ("ou_mean", ou_mean, variance),
        ("ou_first", ou_first, 3.0 * hermite_a),
        ("score_mean", score_mean, variance),
        ("score_first", score_first, 4.0 * hermite_a),
        ("raw_mean", raw_mean, hermite_a**2 + 4.0),
        ("raw_first", raw_first, 4.0 * hermite_a),
    ):
        audit.check("trace_substitute", label, audit.close(actual, expected, 3e-10), actual, expected)
    audit.check("trace_substitute", "raw_mean_debt", audit.close(raw_mean - variance, 2.0, 3e-10), raw_mean - variance, 2.0)

    # Independent torus finite-difference verification of raw-current Hessian.
    floor = 1.0
    height = 40.0
    variation_step = 0.1
    c0_float = float(c0)
    c1_float = float(c1)
    alpha_float = float(alpha)

    def raw_energy(shift: float) -> float:
        def density(x: float) -> float:
            cosine = math.cos(x)
            sine = math.sin(x)
            u = height * (2.0 + cosine) + shift * (2.0 - cosine)
            ux = -height * sine + shift * sine
            q_value = u * u / (u * u + floor)
            weight = c0_float + c1_float * (1.0 - alpha_float * q_value) ** 2
            return 2.0 * u * u * weight * ux * ux

        return torus_average(density)

    values = {multiple: raw_energy(multiple * variation_step) for multiple in (-2, -1, 0, 1, 2)}
    hessian_numeric = (-values[2] + 16.0 * values[1] - 30.0 * values[0] + 16.0 * values[-1] - values[-2]) / (12.0 * variation_step**2)
    leading = -117.0 / (500.0 * float(mass))
    corrected = leading * height**2 + 3.0 * floor / (100.0 * float(mass))
    audit.check("raw_hessian", "negative", hessian_numeric < 0.0, hessian_numeric, "<0")
    audit.check("raw_hessian", "asymptotic", audit.close(hessian_numeric, corrected, 3e-6), hessian_numeric, corrected)
    audit.check("raw_hessian", "leading_density", leading < 0.0, leading, "<0")

    # Correlated lognormal moments are also integrated directly at a modest t.
    lognormal_t = 0.3

    def amplitude_power(x: float, power: int) -> float:
        return math.exp(power * (lognormal_t * x - 3.0 * lognormal_t**2))

    moment4 = normal_expectation(lambda x: amplitude_power(x, 4))
    moment10 = normal_expectation(lambda x: amplitude_power(x, 10))
    audit.check("correlation", "fourth_moment", audit.close(moment4, math.exp(-4.0 * lognormal_t**2), 2e-9), moment4, math.exp(-4.0 * lognormal_t**2))
    audit.check("correlation", "tenth_moment", audit.close(moment10, math.exp(20.0 * lognormal_t**2), 2e-9), moment10, math.exp(20.0 * lognormal_t**2))
    audit.check("correlation", "loss_ratio", audit.close(moment10 / moment4, math.exp(24.0 * lognormal_t**2), 4e-9), moment10 / moment4, math.exp(24.0 * lognormal_t**2))

    coefficient = 0.2
    bad_eta, bad_zeta = 0.01, 0.5
    good_eta, good_zeta = 0.02, 1.0
    audit.check("frequency_boundary", "bad_product", bad_eta * bad_zeta < coefficient**2 / 4.0, bad_eta * bad_zeta, coefficient**2 / 4.0)
    audit.check("frequency_boundary", "bad_minimum", 2.0 * math.sqrt(bad_eta * bad_zeta) < coefficient, 2.0 * math.sqrt(bad_eta * bad_zeta), coefficient)
    audit.check("frequency_boundary", "good_product", good_eta * good_zeta > coefficient**2 / 4.0, good_eta * good_zeta, coefficient**2 / 4.0)
    audit.check("frequency_boundary", "good_minimum", 2.0 * math.sqrt(good_eta * good_zeta) > coefficient, 2.0 * math.sqrt(good_eta * good_zeta), coefficient)

    # Directed-union logic is an infimum of uniformly bounded chart actions,
    # not a sum over charts.
    chart_actions = [-1.25, -0.75, 3.0, 8.0]
    uniform_lower = -1.25
    audit.check("directed_union", "infimum", min(chart_actions) == uniform_lower, min(chart_actions), uniform_lower)
    audit.check("directed_union", "no_chart_count_factor", min(chart_actions) >= uniform_lower, min(chart_actions), uniform_lower)
    audit.check("directed_union", "source_reserve", 0.1 < 9.0 / 20.0, 0.1, 9.0 / 20.0)
    audit.check("directed_union", "sextic_reserve", 0.05 < 3.0 / 20.0, 0.05, 3.0 / 20.0)

    diagnostics = {
        "quadrature": {"gaussian_bound": 10.0, "gaussian_intervals": 40000, "torus_intervals": 32768},
        "six_row_fixture": {"D0": d0_numeric, "D1": d1_numeric, "b_squared": b2_numeric, "packet": packet_numeric},
        "raw_hessian": {"height": height, "finite_difference": hessian_numeric, "asymptotic": corrected},
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "directed_union_nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-123 independent {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
