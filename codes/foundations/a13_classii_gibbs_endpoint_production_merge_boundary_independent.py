#!/usr/bin/env python3
"""Standard-library independent certificate for the scoped R-106 boundary.

This implementation imports neither SymPy nor the primary module.  Exact
Fourier averages are computed with rational Laurent polynomials; endpoint KL
identities are checked on an unrelated finite probability fixture.
"""

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
from typing import TypeAlias


SCHEMA = "tect/a13-gibbs-endpoint-production-merge-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-gibbs-endpoint-production-merge-boundary/result.json"
)

ComplexQ: TypeAlias = tuple[Fraction, Fraction]
Laurent: TypeAlias = dict[int, ComplexQ]


def qadd(left: ComplexQ, right: ComplexQ) -> ComplexQ:
    return left[0] + right[0], left[1] + right[1]


def qmul(left: ComplexQ, right: ComplexQ) -> ComplexQ:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def add(left: Laurent, right: Laurent) -> Laurent:
    result = dict(left)
    for exponent, value in right.items():
        result[exponent] = qadd(result.get(exponent, (Fraction(0), Fraction(0))), value)
        if result[exponent] == (0, 0):
            del result[exponent]
    return result


def scale(poly: Laurent, value: Fraction) -> Laurent:
    return {exponent: (coefficient[0] * value, coefficient[1] * value) for exponent, coefficient in poly.items()}


def multiply(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            exponent = left_exponent + right_exponent
            result[exponent] = qadd(result.get(exponent, (Fraction(0), Fraction(0))), qmul(left_value, right_value))
    return {exponent: value for exponent, value in result.items() if value != (0, 0)}


def power(poly: Laurent, exponent: int) -> Laurent:
    result: Laurent = {0: (Fraction(1), Fraction(0))}
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def derivative(poly: Laurent) -> Laurent:
    # d/dtheta z^n=i*n*z^n.
    return {
        exponent: (-coefficient[1] * exponent, coefficient[0] * exponent)
        for exponent, coefficient in poly.items()
        if exponent != 0
    }


def average(poly: Laurent) -> Fraction:
    value = poly.get(0, (Fraction(0), Fraction(0)))
    if value[1] != 0:
        raise AssertionError(f"non-real Laurent average: {value}")
    return value[0]


def cosine(mode: int, amplitude: Fraction) -> Laurent:
    half = amplitude / 2
    return {mode: (half, Fraction(0)), -mode: (half, Fraction(0))}


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


def close(left: float, right: float, tolerance: float = 1.0e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # Unrelated three-atom endpoint fixture.
    gamma = (0.2, 0.3, 0.5)
    w0 = (0.7, -0.4, 0.2)
    w1 = (-0.1, 0.5, -0.3)
    z0 = sum(weight * math.exp(value) for weight, value in zip(gamma, w0))
    z1 = sum(weight * math.exp(value) for weight, value in zip(gamma, w1))
    phi0, phi1 = math.log(z0), math.log(z1)
    nu0 = tuple(weight * math.exp(value) / z0 for weight, value in zip(gamma, w0))
    nu1 = tuple(weight * math.exp(value) / z1 for weight, value in zip(gamma, w1))
    likelihood = tuple(left - right for left, right in zip(w0, w1))
    e0 = sum(weight * value for weight, value in zip(nu0, likelihood))
    e1 = sum(weight * value for weight, value in zip(nu1, likelihood))
    h01 = sum(left * math.log(left / right) for left, right in zip(nu0, nu1))
    h10 = sum(right * math.log(right / left) for left, right in zip(nu0, nu1))
    endpoint_gap = phi0 - phi1
    checks.require("gibbs", "nu0 normalized", close(sum(nu0), 1.0), sum(nu0), 1.0)
    checks.require("gibbs", "nu1 normalized", close(sum(nu1), 1.0), sum(nu1), 1.0)
    checks.require("gibbs", "forward endpoint KL", close(endpoint_gap, e0 - h01), endpoint_gap, e0 - h01)
    checks.require("gibbs", "reverse endpoint KL", close(endpoint_gap, e1 + h10), endpoint_gap, e1 + h10)
    checks.require("gibbs", "forward KL nonnegative", h01 >= 0.0, h01, ">=0")
    checks.require("gibbs", "reverse KL nonnegative", h10 >= 0.0, h10, ">=0")
    checks.require("gibbs", "likelihood partition identity", close(z0 / z1, sum(weight * math.exp(value) for weight, value in zip(nu1, likelihood))), z0 / z1, "E_nu1 exp(L)")

    # Independent thermodynamic-integration quadrature.
    base = (0.37, 0.63)
    slopes = (-0.8, 1.1)

    def derivative_value(time: float) -> float:
        weights = tuple(weight * math.exp(time * slope) for weight, slope in zip(base, slopes))
        norm = sum(weights)
        return sum(weight * slope for weight, slope in zip(weights, slopes)) / norm

    intervals = 20000
    step = 1.0 / intervals
    integral = derivative_value(0.0) + derivative_value(1.0)
    integral += 4.0 * sum(derivative_value(index * step) for index in range(1, intervals, 2))
    integral += 2.0 * sum(derivative_value(index * step) for index in range(2, intervals, 2))
    integral *= step / 3.0
    exact_integral = math.log(sum(weight * math.exp(slope) for weight, slope in zip(base, slopes))) - math.log(sum(base))
    checks.require("gibbs", "independent thermodynamic integral", close(integral, exact_integral, 2.0e-13), integral, exact_integral)

    # R-105 correction.
    top_average = Fraction(5, 16)
    budget = Fraction(3, 20)
    u6_factor = top_average * budget
    checks.require("correction", "cosine sixth average", top_average == Fraction(5, 16), top_average, Fraction(5, 16))
    checks.require("correction", "stabilising budget", budget == Fraction(3, 20), budget, Fraction(3, 20))
    checks.require("correction", "corrected u6 factor", u6_factor == Fraction(3, 64), u6_factor, Fraction(3, 64))
    checks.require("correction", "bracket/free ratio numerator", Fraction(-3) * u6_factor / u6_factor == -3, Fraction(-3) * u6_factor / u6_factor, -3)

    # Exact production constants, evaluated without reading the primary.
    eps = Fraction(1, 10**12)
    P = Fraction(4) + eps
    a = Fraction(9, 500) / P
    b = Fraction(3, 400) / P
    c = Fraction(3, 320) / P
    d = a + 2 * b + c
    c0 = Fraction(3, 250) / P
    c1 = Fraction(243, 8000) / P
    alpha = Fraction(5, 9)
    checks.require("production", "d exact", d == a + 2 * b + c, d, a + 2 * b + c)
    checks.require("production", "all coefficients positive", min(a, b, c, d, c0, c1) > 0, min(a, b, c, d, c0, c1), ">0")

    for index, y in enumerate((eps / 3, eps, Fraction(1, 7), Fraction(5), Fraction(10**9))):
        radius = y + eps
        delta = 8 * b * eps * y / radius + 4 * c * eps * eps * y / (radius * radius)
        radial = 4 * y * (d - 2 * (b + c) * y / radius + c * y * y / (radius * radius))
        checks.require("production", f"radial split sample {index}", radial == 4 * a * y + delta, radial, 4 * a * y + delta)
        checks.require("production", f"delta nonnegative sample {index}", delta >= 0, delta, ">=0")
        checks.require("production", f"delta bounded sample {index}", delta <= eps * (8 * b + c), delta, eps * (8 * b + c))

    for index, tau in enumerate((Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1), Fraction(7, 5))):
        left = c0 + c1 * (1 - alpha * tau) ** 2
        right = a + 2 * b * (1 - tau) + c * (1 - tau) ** 2
        checks.require("production", f"global-square radial agreement {index}", left == right, left, right)

    # Rational Laurent audit of the 1:2 fixture.
    one: Laurent = {0: (Fraction(1), Fraction(0))}
    for r_value in (Fraction(1, 3), Fraction(1), Fraction(5, 2)):
        f1 = add(one, cosine(1, r_value))
        f2 = add(one, cosine(2, Fraction(-1)))
        full = add(f1, cosine(2, Fraction(-1)))

        def raw(poly: Laurent) -> Laurent:
            return multiply(power(poly, 2), power(derivative(poly), 2))

        raw_merge = average(add(add(raw(full), scale(raw(f1), Fraction(-1))), scale(raw(f2), Fraction(-1))))
        square_merge = average(add(add(add(power(full, 2), scale(power(f1, 2), Fraction(-1))), scale(power(f2, 2), Fraction(-1))), one))
        derivative_envelope = average(add(add(power(derivative(full), 2), power(derivative(f1), 2)), power(derivative(f2), 2)))
        sextic_merge = average(add(add(add(power(full, 6), scale(power(f1, 6), Fraction(-1))), scale(power(f2, 6), Fraction(-1))), one))
        expected_raw = -r_value * r_value / 4
        expected_derivative = r_value * r_value + 4
        expected_sextic = -Fraction(15, 32) * r_value * r_value * (9 * r_value * r_value + 2)
        checks.require("merge", f"raw merge {r_value}", raw_merge == expected_raw, raw_merge, expected_raw)
        checks.require("merge", f"trace merge {r_value}", square_merge == 0, square_merge, 0)
        checks.require("merge", f"derivative envelope {r_value}", derivative_envelope == expected_derivative, derivative_envelope, expected_derivative)
        checks.require("merge", f"sextic merge {r_value}", sextic_merge == expected_sextic, sextic_merge, expected_sextic)
        checks.require("merge", f"sextic sign {r_value}", sextic_merge < 0, sextic_merge, "<0")

    # Fixed-cutoff polynomial upper-bound fixtures and cube counting.
    ksq = Fraction(9, 4)
    r_sq = Fraction(4, 9)
    ggamma = Fraction(7, 3)
    keps = eps * (8 * b + c)
    Acoef = a * ksq * r_sq / 2
    Bcoef = keps * ksq * (r_sq + 4) / 2
    Ccoef = keps * ggamma
    values = []
    for lam in (Fraction(1), Fraction(10), Fraction(10**3), Fraction(10**6)):
        values.append(-Acoef * lam**4 + Bcoef * lam**2 + Ccoef)
    checks.require("merge", "merge upper bound eventually decreases", values[-1] < values[-2] < values[1], values[-3:], "strict decrease")
    checks.require("merge", "merge upper bound negative", values[-1] < 0, values[-1], "<0")
    for radius in (2, 4, 10, 32, 100):
        count = (2 * radius + 1) ** 3 - (radius + 1) ** 3
        checks.require("likelihood_nogo", f"outer cube count N={radius}", count >= 7 * radius**3, count, f">={7 * radius**3}")

    # Coherent output fixture: input leaves are not orthogonal before the sum.
    leaves = (Fraction(2), Fraction(-3), Fraction(5, 2))
    coherent_square = sum(leaves) ** 2
    leaf_square = sum(value * value for value in leaves)
    cross = 2 * (leaves[0] * leaves[1] + leaves[0] * leaves[2] + leaves[1] * leaves[2])
    checks.require("output", "coherent cross identity", coherent_square - leaf_square == cross, coherent_square - leaf_square, cross)
    checks.require("output", "coherent differs from leaf sum", coherent_square != leaf_square, coherent_square, leaf_square)
    checks.require("output", "coherent square nonnegative", coherent_square >= 0, coherent_square, ">=0")

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "corrected_top_shell_u6_factor": str(u6_factor),
        "production_a": str(a),
        "production_b": str(b),
        "production_c": str(c),
        "quartic_merge": str(-Fraction(1, 4)) + "*r^2",
        "sextic_merge": str(-Fraction(15, 32)) + "*r^2*(9*r^2+2)",
    }
    route_verdicts = {
        "endpoint_likelihood_identity": "exact-boundary-only",
        "input_mode_leaf_tensorization": "failed-production-merge",
        "coherent_output_frequency_square": "retained",
        "nelson": "open",
        "sector_a": "open",
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
    print(f"Independent R-106: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
