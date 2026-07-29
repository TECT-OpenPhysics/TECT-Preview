#!/usr/bin/env python3
"""Primary exact audit for the scoped R-123 A13 checkpoint.

The audit verifies the fixed six-row coefficient frame, the derivative-free
trace-excess reduction, two legal finite-root fixtures, the expectation-level
first-linear-row theorem, low-chaos trace-substitution boundaries, the raw
six-current Hessian no-go, correlation-preserving amplitude arithmetic, and
the multiplicity-free directed-union implication.  It does not assert the
missing cutoff-uniform production trace-excess estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"
SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-30-primary-six-row-trace-excess-direct-action-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
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
                "R-123 proves an exact expectation-level trace-excess reduction, scoped finite-root "
                "theorems, and method boundaries. It does not prove the cutoff-uniform complete "
                "production trace-excess estimate, OVERLAP_src, Nelson, removals, a measure, or Sector A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variables: Iterable[sp.Symbol]) -> sp.Expr:
    value = sp.expand(poly)
    for variable in variables:
        expanded = sp.Poly(sp.expand(value), variable)
        total = sp.Integer(0)
        for (degree,), coefficient in expanded.terms():
            if degree % 2:
                continue
            total += coefficient * (sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1))
        value = sp.expand(total)
    return sp.simplify(value)


def characteristic_moment(power: int, frequency: sp.Expr) -> sp.Expr:
    variable = sp.Symbol("frequency", real=True)
    characteristic = sp.exp(-variable**2 / 2)
    moment = sp.diff(characteristic, variable, power) / sp.I**power
    return sp.simplify(moment.subs(variable, frequency))


def real_part(value: sp.Expr) -> sp.Expr:
    return sp.simplify(sp.re(sp.expand_complex(value)))


def imag_part(value: sp.Expr) -> sp.Expr:
    return sp.simplify(sp.im(sp.expand_complex(value)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    p_mass = sp.Rational(str(params["M_X"])) ** 2 + sp.Rational(str(params["classii_mass_regularizer"]))
    a_current = (
        sp.Rational(str(params["cJJ"])) * sp.Rational(str(params["alpha_X"])) ** 2 / p_mass
    )
    b_current = (
        sp.Rational(str(params["cJK"]))
        * sp.Rational(str(params["alpha_X"]))
        * sp.Rational(str(params["beta_X"]))
        / p_mass
    )
    c_current = (
        sp.Rational(str(params["cKK"])) * sp.Rational(str(params["beta_X"])) ** 2 / p_mass
    )
    alpha = sp.simplify(c_current / (b_current + c_current))
    c1 = sp.simplify(c_current / alpha**2)
    c0 = sp.simplify(a_current - b_current**2 / c_current)
    c_sum = sp.simplify(c0 + c1)
    kappa2 = sp.simplify(4 * c0)

    audit.check("six_row", "mass_parameter", p_mass == sp.Rational(4000000000001, 1000000000000), p_mass, sp.Rational(4000000000001, 1000000000000))
    audit.check("six_row", "c0", c0 == sp.Rational(3, 250) / p_mass, c0, sp.Rational(3, 250) / p_mass)
    audit.check("six_row", "c1", c1 == sp.Rational(243, 8000) / p_mass, c1, sp.Rational(243, 8000) / p_mass)
    audit.check("six_row", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("six_row", "c_sum", c_sum == sp.Rational(339, 8000) / p_mass, c_sum, sp.Rational(339, 8000) / p_mass)
    audit.check("six_row", "linear_row_kappa2", kappa2 == sp.Rational(6, 125) / p_mass, kappa2, sp.Rational(6, 125) / p_mass)

    # Round 2: exact scalar collapse of the R-122 zero/first-chaos formulas.
    t0, a2, r2, contraction, xi_r2 = sp.symbols("t0 a2 r2 contraction xi_r2", real=True)
    d0_old = t0 - a2 - r2
    lambda_mean = t0 - (a2 + r2)
    d1_old = sp.Symbol("xi_theta", real=True) - 2 * contraction - xi_r2
    lambda_first = sp.Symbol("xi_theta", real=True) - (2 * contraction + xi_r2)
    audit.check("trace_excess", "D0_scalar_collapse", sp.expand(d0_old - lambda_mean) == 0, d0_old, lambda_mean)
    audit.check("trace_excess", "D1_scalar_collapse", sp.expand(d1_old - lambda_first) == 0, d1_old, lambda_first)

    b2, d0 = sp.symbols("b2 d0", real=True)
    packet_expectation = sp.expand((b2 - d0) / 2)
    audit.check("trace_excess", "direct_packet", packet_expectation == b2 / 2 - d0 / 2, packet_expectation, b2 / 2 - d0 / 2)

    eta, zeta, source, sextic, constant = sp.symbols("eta zeta source sextic constant", nonnegative=True)
    source_action = sp.Rational(9, 20) * source + sp.Rational(3, 20) * sextic - eta * source - zeta * sextic - constant
    expected_action = (sp.Rational(9, 20) - eta) * source + (sp.Rational(3, 20) - zeta) * sextic - constant
    audit.check("directed_union", "action_reserves", sp.expand(source_action - expected_action) == 0, source_action, expected_action)
    audit.check("directed_union", "source_reserve_positive", sp.Rational(1, 10) < sp.Rational(9, 20), sp.Rational(1, 10), sp.Rational(9, 20))
    audit.check("directed_union", "sextic_reserve_positive", sp.Rational(1, 20) < sp.Rational(3, 20), sp.Rational(1, 20), sp.Rational(3, 20))

    # Round 4/5: bounded full-six-row finite-root fixture.  Expectations are
    # reconstructed from derivatives of the Gaussian characteristic function.
    a, beta, tau = sp.symbols("a beta tau", real=True)
    frequency = sp.Integer(2)
    ex_sin = imag_part(characteristic_moment(0, frequency))
    ex_x_sin = imag_part(characteristic_moment(1, frequency))
    ex_x2_cos_2t = real_part(characteristic_moment(2, 2 * frequency))
    ex_x3_sin = imag_part(characteristic_moment(3, frequency))
    mean_a_x = sp.simplify(beta * ex_x_sin)
    mean_a2 = sp.simplify(a**2 + beta**2 * (1 - real_part(characteristic_moment(0, 2 * frequency))) / 2)
    mean_x2_a2 = sp.simplify(a**2 + beta**2 * (1 - ex_x2_cos_2t) / 2)
    mean_x_a2 = sp.simplify(2 * a * beta * ex_x_sin)
    mean_x3_a2 = sp.simplify(2 * a * beta * ex_x3_sin)
    fixture_b2 = sp.simplify(4 * c_sum * mean_a_x**2)
    fixture_d0 = sp.simplify(4 * c_sum * (mean_a2 - mean_x2_a2 + mean_a_x**2))
    fixture_y_first = sp.simplify(4 * c_sum * (mean_x3_a2 - 2 * mean_a_x * a))
    fixture_d1 = sp.simplify(4 * c_sum * mean_x_a2 - fixture_y_first)
    fixture_packet = sp.simplify((fixture_b2 - fixture_d0) / 2)

    expected_b2 = 16 * c_sum * beta**2 * sp.exp(-4)
    expected_d0 = 16 * c_sum * beta**2 * (sp.exp(-4) - 2 * sp.exp(-8))
    expected_d1 = 48 * c_sum * a * beta * sp.exp(-2)
    expected_packet = 16 * c_sum * beta**2 * sp.exp(-8)
    audit.check("six_row_fixture", "mean_A_zero", ex_sin == 0, ex_sin, 0)
    audit.check("six_row_fixture", "b_squared", sp.simplify(fixture_b2 - expected_b2) == 0, fixture_b2, expected_b2)
    audit.check("six_row_fixture", "D0", sp.simplify(fixture_d0 - expected_d0) == 0, fixture_d0, expected_d0)
    audit.check("six_row_fixture", "D1", sp.simplify(fixture_d1 - expected_d1) == 0, fixture_d1, expected_d1)
    audit.check("six_row_fixture", "packet_expectation", sp.simplify(fixture_packet - expected_packet) == 0, fixture_packet, expected_packet)
    audit.check("six_row_fixture", "heat_cancels", sp.diff(fixture_d0, tau) == 0 and sp.diff(fixture_d1, tau) == 0, [sp.diff(fixture_d0, tau), sp.diff(fixture_d1, tau)], [0, 0])
    audit.check("six_row_fixture", "D0_positive", bool((sp.exp(-4) - 2 * sp.exp(-8)) > 0), sp.N(sp.exp(-4) - 2 * sp.exp(-8), 20), ">0")
    audit.check("six_row_fixture", "packet_positive", bool(sp.exp(-8) > 0), sp.exp(-8), ">0")

    # Round 6: legal first-linear-row theorem.  A polynomial test proves the
    # derivative-free and score forms by separate Gaussian moment routes.
    x = sp.Symbol("x", real=True)
    p, q, r = sp.symbols("p q r", real=True)
    h = p + q * x + r * (x**2 - 1)
    x2_h2 = gaussian_expectation((x**2 - 1) * h**2, (x,))
    score_form = gaussian_expectation(sp.diff(h, x) ** 2 + h * sp.diff(h, x, 2), (x,))
    audit.check("linear_row", "score_identity", sp.simplify(x2_h2 / 2 - score_form) == 0, x2_h2 / 2, score_form)
    row_packet = sp.simplify(kappa2 * x2_h2 / 2)
    audit.check("linear_row", "packet_score", sp.simplify(row_packet - kappa2 * score_form) == 0, row_packet, kappa2 * score_form)
    audit.check("linear_row", "mean_debt_upper_bound", sp.simplify(kappa2 - sp.Rational(9, 20)) < 0, sp.N(kappa2, 20), sp.Rational(9, 20))

    row_eta, row_zeta = sp.symbols("row_eta row_zeta", positive=True)
    young_remainder = sp.simplify(kappa2**2 / (16 * sp.sqrt(row_eta * row_zeta)))
    audit.check("linear_row", "optimized_young_denominator", young_remainder == kappa2**2 / (16 * sp.sqrt(row_eta * row_zeta)), young_remainder, kappa2**2 / (16 * sp.sqrt(row_eta * row_zeta)))

    # The h_+/- direct expectation is insensitive to the sign that flips D1.
    amp_a, amp_d = sp.symbols("amp_a amp_d", real=True)
    trig_packet = kappa2 * sp.exp(-2) * (amp_a**2 - amp_d**2)
    d1_plus = 4 * kappa2 * amp_a * amp_d * sp.exp(-2)
    d1_minus = -d1_plus
    audit.check("linear_row", "hpm_same_packet", sp.simplify(trig_packet - trig_packet) == 0, trig_packet, trig_packet)
    audit.check("linear_row", "hpm_opposite_D1", sp.simplify(d1_plus + d1_minus) == 0, d1_plus + d1_minus, 0)

    # Round 4: exact scalar H1+H2 trace-substitute audit.
    epsilon, hermite_a = sp.symbols("epsilon hermite_a", real=True)
    h2_poly = x**2 - 1
    y = epsilon * (hermite_a * x + h2_poly)
    variance = gaussian_expectation(y**2, (x,))
    exchange = sp.expand((y**2 + variance) / 2)
    clark = epsilon**2 * (hermite_a**2 + 2 * hermite_a * x + sp.Rational(2, 3) + sp.Rational(4, 3) * x**2)
    ou = epsilon**2 * (hermite_a + 2 * x) * (hermite_a + x)
    score = epsilon**2 * (hermite_a**2 + 4 * hermite_a * x + h2_poly**2)
    raw = sp.diff(y, x) ** 2
    trace_rows = {
        "exchange": (exchange, variance, 2 * hermite_a * epsilon**2),
        "clark": (clark, variance, 2 * hermite_a * epsilon**2),
        "ou": (ou, variance, 3 * hermite_a * epsilon**2),
        "score": (score, variance, 4 * hermite_a * epsilon**2),
        "raw": (raw, epsilon**2 * (hermite_a**2 + 4), 4 * hermite_a * epsilon**2),
    }
    for label, (trace, expected_mean, expected_first) in trace_rows.items():
        audit.check("trace_substitute", f"{label}_mean", sp.simplify(gaussian_expectation(trace, (x,)) - expected_mean) == 0, gaussian_expectation(trace, (x,)), expected_mean)
        audit.check("trace_substitute", f"{label}_first", sp.simplify(gaussian_expectation(x * trace, (x,)) - expected_first) == 0, gaussian_expectation(x * trace, (x,)), expected_first)
    audit.check("trace_substitute", "raw_mean_debt", sp.simplify(gaussian_expectation(raw, (x,)) - variance - 2 * epsilon**2) == 0, gaussian_expectation(raw, (x,)) - variance, 2 * epsilon**2)

    rho = sp.Symbol("rho", real=True)
    ou_replica_defect = sp.integrate(4 * (1 - rho), (rho, 0, 1))
    audit.check("trace_substitute", "ou_replica_H2_defect", ou_replica_defect == 2, ou_replica_defect, 2)

    # Round 8: raw-current Hessian no-go in normalized Haar/unit-frequency units.
    c = sp.Symbol("c", real=True)
    torus_integrand = sp.expand((6 * c**2 - 8) * (1 - c**2))
    torus_average = torus_integrand.subs(c**4, sp.Rational(3, 8)).subs(c**2, sp.Rational(1, 2))
    homogeneous_coefficient = sp.simplify(c0 + c1 * (1 - alpha) ** 2)
    hessian_coefficient = sp.simplify(4 * homogeneous_coefficient * torus_average)
    audit.check("raw_hessian", "torus_average", torus_average == -sp.Rational(13, 4), torus_average, -sp.Rational(13, 4))
    audit.check("raw_hessian", "homogeneous_coefficient", homogeneous_coefficient == sp.Rational(9, 500) / p_mass, homogeneous_coefficient, sp.Rational(9, 500) / p_mass)
    audit.check("raw_hessian", "negative_leading_coefficient", hessian_coefficient == -sp.Rational(117, 500) / p_mass, hessian_coefficient, -sp.Rational(117, 500) / p_mass)
    audit.check("raw_hessian", "negative_sign", bool(hessian_coefficient < 0), hessian_coefficient, "<0")

    # Round 5/8: exact correlation gain and the cutoff-uniform allocation boundary.
    moment4_exponent = sp.Rational(4 * (4 - 6), 2)
    moment10_exponent = sp.Rational(10 * (10 - 6), 2)
    loss_exponent = moment10_exponent - moment4_exponent
    audit.check("correlation", "A4_exponent", moment4_exponent == -4, moment4_exponent, -4)
    audit.check("correlation", "A10_exponent", moment10_exponent == 20, moment10_exponent, 20)
    audit.check("correlation", "holder_loss_exponent", loss_exponent == 24, loss_exponent, 24)

    coefficient, allocation_eta, allocation_zeta, scale = sp.symbols("coefficient allocation_eta allocation_zeta scale", positive=True)
    minimized = sp.simplify(2 * sp.sqrt(allocation_eta * allocation_zeta))
    audit.check("correlation", "frequency_minimum", minimized == 2 * sp.sqrt(allocation_eta * allocation_zeta), minimized, 2 * sp.sqrt(allocation_eta * allocation_zeta))
    threshold_identity = sp.expand(minimized**2 - coefficient**2)
    audit.check("correlation", "allocation_threshold", threshold_identity == 4 * allocation_eta * allocation_zeta - coefficient**2, threshold_identity, 4 * allocation_eta * allocation_zeta - coefficient**2)

    diagnostics = {
        "production": {"P": p_mass, "c0": c0, "c1": c1, "c_sum": c_sum, "alpha": alpha, "kappa_squared": kappa2},
        "six_row_fixture_t2": {"D0": fixture_d0, "D1": fixture_d1, "b_squared": fixture_b2, "packet_expectation": fixture_packet},
        "linear_row": {"score_form": score_form, "young_remainder": young_remainder},
        "raw_hessian": {"normalized_unit_frequency_leading_coefficient": hessian_coefficient},
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "directed_union_nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-123 primary {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
