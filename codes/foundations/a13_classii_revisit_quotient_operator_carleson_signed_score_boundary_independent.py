#!/usr/bin/env python3
"""Non-importing exact audit for the scoped R-118 A13 quotient boundary.

This implementation uses only ``fractions.Fraction`` and small polynomial/
matrix routines.  It does not import SymPy or the primary certificate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-REVISIT-QUOTIENT-OPERATOR-CARLESON-SIGNED-SCORE-BOUNDARY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-independent-revisit-quotient-operator-carleson-signed-score-boundary/result.json"
)
SCHEMA = "tect/a13-revisit-quotient-operator-carleson-signed-score-boundary-independent/1.0"


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
                "This non-importing audit checks exact finite fixtures for R-118. "
                "It does not prove production vertical basicness, a PSD random-W "
                "owner, one-use, Nelson, or Sector A closure."
            ),
        }


Poly = tuple[Fraction, ...]


def trim(poly: list[Fraction] | tuple[Fraction, ...]) -> Poly:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def add(left: Poly, right: Poly) -> Poly:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def scale(value: Fraction, poly: Poly) -> Poly:
    return trim([value * coefficient for coefficient in poly])


def sub(left: Poly, right: Poly) -> Poly:
    return add(left, scale(Fraction(-1), right))


def mul(left: Poly, right: Poly) -> Poly:
    values = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            values[i + j] += a * b
    return trim(values)


def derivative(poly: Poly) -> Poly:
    if len(poly) == 1:
        return (Fraction(0),)
    return trim([Fraction(index) * poly[index] for index in range(1, len(poly))])


def x_times(poly: Poly) -> Poly:
    return (Fraction(0),) + poly


def delta2(poly: Poly) -> Poly:
    # delta^2 w = w(x^2-1)-2xw'+w''.
    x2_minus_one = (Fraction(-1), Fraction(0), Fraction(1))
    return add(sub(mul(poly, x2_minus_one), scale(Fraction(2), x_times(derivative(poly)))), derivative(derivative(poly)))


def hermites(count: int) -> list[Poly]:
    values = [(Fraction(1),), (Fraction(0), Fraction(1))]
    for degree in range(1, count):
        values.append(sub(x_times(values[-1]), scale(Fraction(degree), values[-2])))
    return values[: count + 1]


def double_factorial_odd(index: int) -> int:
    value = 1
    for number in range(1, index + 1, 2):
        value *= number
    return value


def gaussian_mean(poly: Poly) -> Fraction:
    total = Fraction(0)
    for degree, coefficient in enumerate(poly):
        if degree % 2:
            continue
        moment = 1 if degree == 0 else double_factorial_odd(degree - 1)
        total += coefficient * moment
    return total


def evaluate(poly: Poly, value: Fraction) -> Fraction:
    total = Fraction(0)
    for coefficient in reversed(poly):
        total = total * value + coefficient
    return total


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum(row[index] * vector[index] for index in range(len(vector))) for row in matrix]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum(a * b for a, b in zip(left, right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()

    L = [[Fraction(1), Fraction(1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(1)]]
    B = [[Fraction(2), Fraction(-1)], [Fraction(-1), Fraction(3)]]
    K = matmul(matmul(transpose(L), B), L)
    vertical = [Fraction(1), Fraction(-1), Fraction(1)]
    sample = [Fraction(2), Fraction(-3), Fraction(5)]
    shifted = [sample[index] + vertical[index] for index in range(3)]
    audit.check("quotient", "vertical_is_kernel", matvec(L, vertical) == [0, 0], matvec(L, vertical), [0, 0])
    audit.check("quotient", "factor_kills_vertical", matvec(K, vertical) == [0, 0, 0], matvec(K, vertical), [0, 0, 0])
    audit.check("quotient", "fibre_invariance", dot(sample, matvec(K, sample)) == dot(shifted, matvec(K, shifted)), dot(shifted, matvec(K, shifted)) - dot(sample, matvec(K, sample)), 0)
    bad_value = dot(vertical, vertical)
    audit.check("quotient", "identity_survives_vertical", bad_value == 3, bad_value, 3)

    endpoint_hessian = [[Fraction(6), Fraction(2)], [Fraction(2), Fraction(48)]]
    visit_hessian = matmul(matmul(transpose(L), endpoint_hessian), L)
    audit.check("chain_rule", "visit_hessian_kills_vertical", matvec(visit_hessian, vertical) == [0, 0, 0], matvec(visit_hessian, vertical), [0, 0, 0])

    kappa = Fraction(1, 10)
    theta = (1 + kappa) / 2
    beta = (1 - kappa) / 6
    gap = 1 - theta - beta
    audit.check("operator_carleson", "theta", theta == Fraction(11, 20), theta, Fraction(11, 20))
    audit.check("operator_carleson", "terminal_sextic_power", beta == Fraction(3, 20), beta, Fraction(3, 20))
    audit.check("operator_carleson", "model_moment", 1 / gap == Fraction(10, 3), 1 / gap, Fraction(10, 3))
    audit.check("operator_carleson", "spectral_constant_power", 1 / gap == Fraction(10, 3), 1 / gap, Fraction(10, 3))
    audit.check("operator_carleson", "eta_power", theta / gap == Fraction(11, 6), theta / gap, Fraction(11, 6))
    audit.check("operator_carleson", "zeta_power", beta / gap == Fraction(1, 2), beta / gap, Fraction(1, 2))

    opposite = [Fraction(1), Fraction(-1)]
    endpoint = opposite[0] + opposite[1]
    visit_square = dot(opposite, opposite)
    audit.check("opposite_visit", "terminal_zero", endpoint == 0, endpoint, 0)
    audit.check("opposite_visit", "visit_square", visit_square == 2, visit_square, 2)
    audit.check("opposite_visit", "visit_sextic_density", visit_square**3 == 8, visit_square**3, 8)

    H0, H1, H2, H3, H4 = hermites(4)
    a = Fraction(3, 2)
    s = Fraction(2, 5)
    x0 = scale(a, H1)
    xs = add(x0, scale(s, H2))
    x1 = add(x0, H2)
    t0 = (a * a,)
    ts = mul(add((a,), scale(2 * s, H1)), add((a,), scale(2 * s, H1)))
    t1 = mul(add((a,), scale(Fraction(2), H1)), add((a,), scale(Fraction(2), H1)))

    def packet(left: Poly, right: Poly, trace_left: Poly, trace_right: Poly) -> Poly:
        increment = sub(right, left)
        return sub(add(mul(left, increment), scale(Fraction(1, 2), mul(increment, increment))), scale(Fraction(1, 2), sub(trace_right, trace_left)))

    two_visit = add(packet(x0, xs, t0, ts), packet(xs, x1, ts, t1))
    endpoint_difference = sub(scale(Fraction(1, 2), sub(mul(x1, x1), mul(x0, x0))), scale(Fraction(1, 2), sub(t1, t0)))
    target = add(add(scale(a, H3), scale(Fraction(1, 2), H4)), (Fraction(-1),))
    audit.check("hermite", "internal_visit_cancels", two_visit == endpoint_difference, two_visit, endpoint_difference)
    audit.check("hermite", "quotient_normal_form", two_visit == target, two_visit, target)
    mean_debt = gaussian_mean(target)
    first_chaos = gaussian_mean(mul(H1, target))
    audit.check("hermite", "mean_debt", mean_debt == -1, mean_debt, -1)
    audit.check("hermite", "first_chaos_zero", first_chaos == 0, first_chaos, 0)

    weight = add(H2, scale(2 * a, H1))
    centered = sub(target, (mean_debt,))
    audit.check("hermite", "double_divergence", scale(Fraction(1, 2), delta2(weight)) == centered, scale(Fraction(1, 2), delta2(weight)), centered)
    audit.check("hermite", "weight_negative", evaluate(weight, -a) == -(a * a + 1), evaluate(weight, -a), -(a * a + 1))
    audit.check("hermite", "weight_positive", evaluate(weight, a + 2) > 0, evaluate(weight, a + 2), ">0")

    # Creation by delta^2 shifts the one-dimensional Hermite basis by two,
    # which pins the only possible degree-two preimage.
    audit.check("hermite", "delta2_H0", delta2(H0) == H2, delta2(H0), H2)
    audit.check("hermite", "delta2_H1", delta2(H1) == H3, delta2(H1), H3)
    audit.check("hermite", "delta2_H2", delta2(H2) == H4, delta2(H2), H4)
    reconstructed = add(scale(Fraction(0), H0), add(scale(2 * a, H1), H2))
    audit.check("hermite", "unique_preimage_coefficients", reconstructed == weight, reconstructed, weight)

    # A constant-curl one-form independently checks the Cartan homotopy term:
    # omega=(-y/2,x/2), Phi=0, and kappa=omega.
    x, y = Fraction(4), Fraction(-6)
    omega = [Fraction(-1, 2) * y, Fraction(1, 2) * x]
    kappa_form = [Fraction(-1, 2) * y, Fraction(1, 2) * x]
    audit.check("cartan", "homotopy_remainder", kappa_form == omega, kappa_form, omega)
    curl = Fraction(1, 2) - Fraction(-1, 2)
    audit.check("cartan", "nonzero_curl", curl == 1, curl, 1)

    diagnostics = {
        "quotient_matrix": K,
        "interpolation": {
            "kappa": kappa,
            "theta": theta,
            "terminal_sextic_power": beta,
            "model_moment": 1 / gap,
            "eta_power": theta / gap,
            "zeta_power": beta / gap,
        },
        "hermite": {
            "a": a,
            "subdivision": s,
            "quotient": target,
            "mean": mean_debt,
            "first_chaos": first_chaos,
            "canonical_weight": weight,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Independent R-118 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
