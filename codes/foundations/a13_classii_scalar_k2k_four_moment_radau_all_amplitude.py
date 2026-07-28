#!/usr/bin/env python3
"""Primary fail-closed Arb certificate for the R-115 four-moment Radau route.

The program reconstructs all moments from the exact R-112 scalar packet, derives the
three-node left Gauss--Radau law, and certifies the all-tilt skew sufficient
gate on b >= 643/200 and c in [0,1].
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import tempfile
import time

from flint import arb, ctx
import flint
import sympy as sp


SCHEMA = "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-primary/1.0"
VERSION = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-28-primary-scalar-k2k-four-moment-radau-all-amplitude/result.json"
B_MIN = Fraction(643, 200)
D_MAX = 1 / B_MIN
DEFAULT_D_SPLITS = 16
DEFAULT_C_SPLITS = 32
DEFAULT_DPS = 60
DEFAULT_MAX_EVALS = 60_000
# Algorithm-regression oracles, not mathematical inputs.
EXPECTED_EVALUATIONS = 46_714
EXPECTED_ACCEPTED_LEAVES = 23_613


def qtext(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def to_arb(value: int | Fraction | arb) -> arb:
    if isinstance(value, arb):
        return value
    if isinstance(value, Fraction):
        return arb(value.numerator) / value.denominator
    return arb(value)


def exact_packet_scaled_moments() -> tuple[list[list[list[Fraction]]], dict[str, object]]:
    """Derive d^n E[Z^n] from the exact packet, never from pasted moments."""
    b, c, t, u, d = sp.symbols("b c t u d", nonnegative=True)
    rho = c * t / 2
    sigma = (1 - c) * u / 8
    centered_even = sp.expand(
        b * (rho + 4 * sigma - sp.Rational(1, 2))
        + rho**2
        + 10 * rho * sigma
        + 4 * sigma**2
        - rho
        - sigma
    )
    phase_square = sp.expand(36 * b * rho**2 * sigma)

    def exp_expect(poly: sp.Expr) -> sp.Expr:
        result = sp.Integer(0)
        for (i, j), coefficient in sp.Poly(sp.expand(poly), t, u).terms():
            result += coefficient * sp.factorial(i) * sp.factorial(j)
        return sp.factor(result)

    def centered_moment(order: int) -> sp.Expr:
        result = sp.Integer(0)
        for even_power in range(0, order + 1, 2):
            phase_order = even_power // 2
            phase_average = sp.binomial(2 * phase_order, phase_order) / 4**phase_order
            result += (
                sp.binomial(order, even_power)
                * phase_average
                * exp_expect(centered_even ** (order - even_power) * phase_square**phase_order)
            )
        return sp.factor(result)

    mu = [centered_moment(n) for n in range(5)]
    raw = [
        sp.factor(sum(sp.binomial(n, j) * (b / 2) ** (n - j) * mu[j] for j in range(n + 1)))
        for n in range(5)
    ]
    scaled = [sp.Poly(sp.expand(sp.cancel(d**n * raw[n].subs(b, 1 / d))), d, c) for n in range(5)]

    K = sp.factor(
        b**2 * (c**2 - c + sp.Rational(1, 2))
        + b * (-3 * c**3 + 5 * c**2 + c + 1) / 4
        + (153 * c**4 - 156 * c**3 + 82 * c**2 - 4 * c + 5) / 64
    )
    Delta = (33 * c**4 - 36 * c**3 + 22 * c**2 - 4 * c + 1) / 64
    identity_checks = {
        "centered_mean_zero": bool(sp.expand(mu[1]) == 0),
        "variance_identity": bool(sp.simplify(mu[2] - (K - Delta) / 2) == 0),
        "scaled_mass_one": bool(scaled[0].as_expr() == 1),
        "scaled_mean_half": bool(scaled[1].as_expr() == sp.Rational(1, 2)),
    }
    assert all(identity_checks.values())

    projective_expected = [
        sp.Integer(1),
        sp.Rational(1, 2),
        (c**2 - c + 1) / 2,
        3 * (2 * c**2 - 2 * c + 1) / 4,
        3 * (c**4 - 2 * c**3 + 4 * c**2 - 3 * c + 1) / 2,
    ]
    projective_checks = [
        bool(sp.simplify(poly.as_expr().subs(d, 0) - expected) == 0)
        for poly, expected in zip(scaled, projective_expected)
    ]
    assert all(projective_checks)

    A, B, C, v, gap = sp.symbols("A B C v gap", positive=True)
    big = v + gap
    total = A + B + C
    mean = (B * v + C * big) / total
    direct_skew = sp.expand(total**3 * (
        A * (0 - mean) ** 3 + B * (v - mean) ** 3 + C * (big - mean) ** 3
    ) / total)
    cross = (gap - v) * (gap + 2 * v) * (2 * gap + v)
    grouped_skew = (
        A * B * (A - B) * v**3
        + A * C * (A - C) * big**3
        + B * C * (B - C) * gap**3
        + A * B * C * cross
    )
    skew_identity = bool(sp.simplify(direct_skew - grouped_skew) == 0)
    assert skew_identity

    # Exact adverse fixture: structural ordering alone does not imply skew.
    # Nodes 0,1,2; weights 1/10,4/5,1/10; tilt t=log 2 gives masses
    # 1/10,2/5,1/40 and normalized third central moment -16/343.
    fixture_masses = [Fraction(1, 10), Fraction(2, 5), Fraction(1, 40)]
    fixture_total = sum(fixture_masses)
    fixture_mean = (fixture_masses[1] + 2 * fixture_masses[2]) / fixture_total
    fixture_skew = sum(
        mass * (Fraction(node) - fixture_mean) ** 3
        for node, mass in enumerate(fixture_masses)
    ) / fixture_total
    assert fixture_skew == Fraction(-16, 343)

    def dense(poly: sp.Poly) -> list[list[Fraction]]:
        degree_d, degree_c = poly.degree(d), poly.degree(c)
        data = [[Fraction(0) for _ in range(degree_c + 1)] for _ in range(degree_d + 1)]
        for (i, j), coefficient in poly.terms():
            data[i][j] = Fraction(int(sp.numer(coefficient)), int(sp.denom(coefficient)))
        return data

    M = [poly.as_expr() for poly in scaled]
    H = sp.Poly(sp.expand(M[1] * M[3] - M[2] ** 2), d, c)
    J = sp.Poly(sp.expand(M[1] * M[4] - M[2] * M[3]), d, c)
    N = sp.Poly(sp.expand(J.as_expr() * M[2] - H.as_expr() * M[3]), d, c)
    discriminant_numerator = sp.Poly(
        sp.expand(J.as_expr() ** 2 * M[1] - 4 * N.as_expr() * H.as_expr()), d, c
    )
    dense_data = [dense(poly) for poly in scaled] + [dense(H), dense(J), dense(N), dense(discriminant_numerator)]
    metadata = {
        "identity_checks": identity_checks,
        "projective_moment_checks": projective_checks,
        "three_point_skew_identity": skew_identity,
        "exact_adverse_fixture": {
            "support": ["0", "1", "2"],
            "base_weights": ["1/10", "4/5", "1/10"],
            "tilt": "log(2)",
            "tilted_masses": [qtext(x) for x in fixture_masses],
            "normalized_third_central_moment": qtext(fixture_skew),
        },
        "scaled_moment_total_degrees": [poly.total_degree() for poly in scaled],
        "scaled_moment_term_counts": [len(poly.terms()) for poly in scaled],
        "derived_polynomial_term_counts": {
            "H": len(H.terms()),
            "J": len(J.terms()),
            "N": len(N.terms()),
            "discriminant_numerator": len(discriminant_numerator.terms()),
        },
    }
    return dense_data, metadata


class Jet:
    """Rigorous first-order centered form, recentered after each operation."""

    __slots__ = ("value", "d_derivative", "c_derivative", "d_radius", "c_radius")

    def __init__(self, value, d_derivative=0, c_derivative=0, d_radius=0, c_radius=0):
        self.value = to_arb(value)
        self.d_derivative = to_arb(d_derivative)
        self.c_derivative = to_arb(c_derivative)
        self.d_radius = to_arb(d_radius)
        self.c_radius = to_arb(c_radius)

    def range(self) -> arb:
        return self.value + self.d_derivative * self.d_radius + self.c_derivative * self.c_radius

    def coerce(self, other) -> "Jet":
        if isinstance(other, Jet):
            return other
        return Jet(other, d_radius=self.d_radius, c_radius=self.c_radius)

    def __add__(self, other):
        other = self.coerce(other)
        return Jet(
            self.value + other.value,
            self.d_derivative + other.d_derivative,
            self.c_derivative + other.c_derivative,
            self.d_radius,
            self.c_radius,
        )

    __radd__ = __add__

    def __neg__(self):
        return Jet(-self.value, -self.d_derivative, -self.c_derivative, self.d_radius, self.c_radius)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        self_range, other_range = self.range(), other.range()
        return Jet(
            self.value * other.value,
            self.d_derivative * other_range + self_range * other.d_derivative,
            self.c_derivative * other_range + self_range * other.c_derivative,
            self.d_radius,
            self.c_radius,
        )

    __rmul__ = __mul__

    def inverse(self):
        value_range = self.range()
        return Jet(
            1 / self.value,
            -self.d_derivative / value_range**2,
            -self.c_derivative / value_range**2,
            self.d_radius,
            self.c_radius,
        )

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other):
        return self.coerce(other) * self.inverse()

    def __pow__(self, exponent: int):
        if not isinstance(exponent, int):
            raise TypeError("Jet powers must be integral")
        if exponent == 0:
            return Jet(1, d_radius=self.d_radius, c_radius=self.c_radius)
        if exponent < 0:
            return (self ** (-exponent)).inverse()
        value_range = self.range()
        return Jet(
            self.value**exponent,
            exponent * value_range ** (exponent - 1) * self.d_derivative,
            exponent * value_range ** (exponent - 1) * self.c_derivative,
            self.d_radius,
            self.c_radius,
        )

    def sqrt(self):
        root_range = self.range().sqrt()
        return Jet(
            self.value.sqrt(),
            self.d_derivative / (2 * root_range),
            self.c_derivative / (2 * root_range),
            self.d_radius,
            self.c_radius,
        )

    def log(self):
        value_range = self.range()
        return Jet(
            self.value.log(),
            self.d_derivative / value_range,
            self.c_derivative / value_range,
            self.d_radius,
            self.c_radius,
        )

    def exp(self):
        exponential_range = self.range().exp()
        return Jet(
            self.value.exp(),
            exponential_range * self.d_derivative,
            exponential_range * self.c_derivative,
            self.d_radius,
            self.c_radius,
        )


def evaluate_dense(data: list[list[Fraction]], d_value: Jet, c_value: Jet) -> Jet:
    degree_d, degree_c = len(data) - 1, len(data[0]) - 1
    rows: list[Jet] = []
    for i in range(degree_d + 1):
        value = Jet(0, d_radius=d_value.d_radius, c_radius=d_value.c_radius)
        for j in range(degree_c, -1, -1):
            value = value * c_value + data[i][j]
        rows.append(value)
    result = Jet(0, d_radius=d_value.d_radius, c_radius=d_value.c_radius)
    for i in range(degree_d, -1, -1):
        result = result * d_value + rows[i]
    return result


def radau_quantities(d_value: Jet, c_value: Jet, polynomials: list[list[list[Fraction]]]) -> dict[str, Jet]:
    m0, m1, m2, m3, m4, h_data, j_data, n_data, disc_data = polynomials
    m0, m1, m2, m3, m4 = [evaluate_dense(x, d_value, c_value) for x in (m0, m1, m2, m3, m4)]
    H = evaluate_dense(h_data, d_value, c_value)
    J = evaluate_dense(j_data, d_value, c_value)
    N = evaluate_dense(n_data, d_value, c_value)
    disc_numerator = evaluate_dense(disc_data, d_value, c_value)
    node_sum = J / H
    node_discriminant = disc_numerator / (H**2 * m1)
    gap = node_discriminant.sqrt()
    v = (node_sum - gap) / 2
    big = (node_sum + gap) / 2
    q = (m1 * big - m2) / (v * gap)
    p = (m2 - m1 * v) / (big * gap)
    a = 1 - p - q
    k = gap / v
    stationary = k * q / ((k + 1) * a)
    positive_part = (
        (k - 1) * (k + 2) * (2 * k + 1)
        + k**3 * (q - p) / q
        + (k + 1) ** 3 * (a - p) / q
    )
    first_branch = (q - a) / p
    second_branch = q / (p * (k + 1)) * (k * stationary.log()).exp()
    return {
        "H": H,
        "node_discriminant": node_discriminant,
        "v": v,
        "gap_minus_v": gap - v,
        "p": p,
        "q": q,
        "a": a,
        "q_minus_p": q - p,
        "a_minus_p": a - p,
        "q_minus_a": q - a,
        "stationary": stationary,
        "first_branch_margin": positive_part - first_branch,
        "second_branch_margin": positive_part - second_branch,
    }


@dataclass(frozen=True)
class Box:
    d_lower: Fraction
    d_upper: Fraction
    c_lower: Fraction
    c_upper: Fraction

    def split(self) -> tuple["Box", "Box"]:
        if (self.d_upper - self.d_lower) * B_MIN >= self.c_upper - self.c_lower:
            midpoint = (self.d_lower + self.d_upper) / 2
            return (
                Box(self.d_lower, midpoint, self.c_lower, self.c_upper),
                Box(midpoint, self.d_upper, self.c_lower, self.c_upper),
            )
        midpoint = (self.c_lower + self.c_upper) / 2
        return (
            Box(self.d_lower, self.d_upper, self.c_lower, midpoint),
            Box(self.d_lower, self.d_upper, midpoint, self.c_upper),
        )

    def serialize(self) -> list[str]:
        return [qtext(x) for x in (self.d_lower, self.d_upper, self.c_lower, self.c_upper)]

    @staticmethod
    def deserialize(data: list[str]) -> "Box":
        return Box(*(Fraction(value) for value in data))


def initial_boxes(d_splits: int, c_splits: int) -> deque[Box]:
    return deque(
        Box(
            D_MAX * i / d_splits,
            D_MAX * (i + 1) / d_splits,
            Fraction(j, c_splits),
            Fraction(j + 1, c_splits),
        )
        for i in range(d_splits)
        for j in range(c_splits)
    )


def certify_box(box: Box, polynomials: list[list[list[Fraction]]]) -> tuple[bool, str, arb | None]:
    d_midpoint = (box.d_lower + box.d_upper) / 2
    c_midpoint = (box.c_lower + box.c_upper) / 2
    d_radius = arb(0, qtext((box.d_upper - box.d_lower) / 2))
    c_radius = arb(0, qtext((box.c_upper - box.c_lower) / 2))
    quantities = radau_quantities(
        Jet(to_arb(d_midpoint), 1, 0, d_radius, c_radius),
        Jet(to_arb(c_midpoint), 0, 1, d_radius, c_radius),
        polynomials,
    )
    ranges = {name: value.range() for name, value in quantities.items()}
    for name, value in ranges.items():
        if not value.is_finite():
            return False, f"nonfinite::{name}", None
    for name in (
        "H",
        "node_discriminant",
        "v",
        "gap_minus_v",
        "p",
        "q",
        "a",
        "q_minus_p",
        "a_minus_p",
        "stationary",
    ):
        if ranges[name].lower() <= 0:
            return False, f"sign::{name}", None
    if ranges["q_minus_a"].upper() <= 0:
        return True, "automatic::q<=a", None
    if ranges["stationary"].upper() <= 1:
        required = ("first_branch_margin",)
    elif ranges["stationary"].lower() >= 1:
        required = ("second_branch_margin",)
    else:
        required = ("first_branch_margin", "second_branch_margin")
    lower_bounds = []
    for name in required:
        lower = ranges[name].lower()
        if lower <= 0:
            return False, f"margin::{name}", None
        lower_bounds.append(lower)
    weakest = min(lower_bounds)
    return True, "margin", weakest


def write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--checkpoint")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--d-splits", type=int, default=DEFAULT_D_SPLITS)
    parser.add_argument("--c-splits", type=int, default=DEFAULT_C_SPLITS)
    parser.add_argument("--dps", type=int, default=DEFAULT_DPS)
    parser.add_argument("--max-evals", type=int, default=DEFAULT_MAX_EVALS)
    parser.add_argument("--save-every", type=int, default=10_000)
    args = parser.parse_args()
    if args.d_splits <= 0 or args.c_splits <= 0 or args.max_evals <= 0:
        parser.error("split counts and max-evals must be positive")
    ctx.dps = args.dps
    started = time.perf_counter()
    polynomials, self_tests = exact_packet_scaled_moments()
    derivation_seconds = time.perf_counter() - started

    checkpoint_path = Path(args.checkpoint) if args.checkpoint else None
    if args.resume:
        if checkpoint_path is None or not checkpoint_path.exists():
            parser.error("--resume requires an existing --checkpoint")
        saved = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        pending = deque(Box.deserialize(item) for item in saved["pending"])
        accepted = int(saved["accepted_leaves"])
        evaluations = int(saved["evaluations"])
        weakest_value = saved.get("weakest_outward_lower")
        weakest_float = float(arb(weakest_value)) if weakest_value is not None else None
    else:
        pending = initial_boxes(args.d_splits, args.c_splits)
        accepted = 0
        evaluations = 0
        weakest_value = None
        weakest_float = None

    reasons: dict[str, int] = {}
    while pending and evaluations < args.max_evals:
        box = pending.popleft()
        certified, reason, margin = certify_box(box, polynomials)
        evaluations += 1
        if certified:
            accepted += 1
            if margin is not None:
                margin_float = float(margin)
                if weakest_float is None or margin_float < weakest_float:
                    weakest_float, weakest_value = margin_float, str(margin)
        else:
            reasons[reason] = reasons.get(reason, 0) + 1
            pending.extend(box.split())
        if checkpoint_path is not None and evaluations % args.save_every == 0:
            write_json_atomic(
                checkpoint_path,
                {
                    "schema": f"{SCHEMA}/checkpoint",
                    "accepted_leaves": accepted,
                    "evaluations": evaluations,
                    "pending": [item.serialize() for item in pending],
                    "weakest_outward_lower": weakest_value,
                },
            )

    complete = not pending
    regression_counts_match = (
        evaluations == EXPECTED_EVALUATIONS
        and accepted == EXPECTED_ACCEPTED_LEAVES
    )
    strict_margin = weakest_float is not None and weakest_float > 0
    passed = complete and regression_counts_match and strict_margin
    elapsed = time.perf_counter() - started
    source_path = Path(__file__).resolve()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if passed else "FAIL",
        "domain": {
            "b": f"[{qtext(B_MIN)},+infinity)",
            "d_equals_inverse_b": f"[0,{qtext(D_MAX)}]",
            "c": "[0,1]",
        },
        "theorem_gate": {
            "support": "{0,v,v+u}",
            "base_conditions": ["u>=v>0", "p<=q", "p<=a"],
            "certified_conclusion": "the sufficient all-negative-tilt third-central-moment gate is strictly positive",
            "consequence": "the Radau proxy tilted variance is nonincreasing for every tilt t>=0",
        },
        "cover": {
            "initial_d_splits": args.d_splits,
            "initial_c_splits": args.c_splits,
            "evaluations": evaluations,
            "accepted_leaves": accepted,
            "pending_boxes": len(pending),
            "weakest_outward_lower": weakest_value,
            "algorithm_regression_oracles": {
                "expected_evaluations": EXPECTED_EVALUATIONS,
                "expected_accepted_leaves": EXPECTED_ACCEPTED_LEAVES,
                "evaluations_match": evaluations == EXPECTED_EVALUATIONS,
                "accepted_leaves_match": accepted == EXPECTED_ACCEPTED_LEAVES,
            },
        },
        "self_tests": self_tests,
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "sympy": sp.__version__,
            "arb_decimal_digits": args.dps,
            "source_path": str(source_path),
            "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        },
        "failure_reasons_this_run": reasons,
        "assertions": {
            "complete_cover": complete,
            "regression_counts_match": regression_counts_match,
            "strict_outward_margin": strict_margin,
            "moment_and_identity_self_tests": (
                all(self_tests["identity_checks"].values())
                and all(self_tests["projective_moment_checks"])
                and self_tests["three_point_skew_identity"] is True
                and self_tests["exact_adverse_fixture"]["normalized_third_central_moment"]
                == "-16/343"
            ),
        },
    }
    write_json_atomic(Path(args.output), payload)
    if checkpoint_path is not None:
        write_json_atomic(
            checkpoint_path,
            {
                "schema": f"{SCHEMA}/checkpoint",
                "accepted_leaves": accepted,
                "evaluations": evaluations,
                "pending": [item.serialize() for item in pending],
                "weakest_outward_lower": weakest_value,
                "complete": complete,
            },
        )
    print(json.dumps({"status": payload["status"], "output": str(Path(args.output)), "evaluations": evaluations, "accepted_leaves": accepted, "pending_boxes": len(pending), "weakest_outward_lower": weakest_value, "seconds": elapsed}, indent=2))
    if not passed:
        raise SystemExit(2)
    assert evaluations == EXPECTED_EVALUATIONS
    assert accepted == EXPECTED_ACCEPTED_LEAVES
    assert weakest_float is not None and weakest_float > 0


if __name__ == "__main__":
    main()
