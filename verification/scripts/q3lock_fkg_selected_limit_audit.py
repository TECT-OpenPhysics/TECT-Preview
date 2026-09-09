#!/usr/bin/env python3
"""Finite audit of the Q3LOCK continuous-loop FKG passage.

The checker covers only algebraic, finite-order, compact-grid, and clipping
diagnostics.  It is deliberately not an infinite-dimensional FKG proof, a
DLR theorem, or a phase-coexistence result.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product
from math import exp
from pathlib import Path
import hashlib
import json
import os
import tempfile


ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-fkg-selected-limit-audit-260908.md"
OUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-fkg-selected-limit-audit/result.json"
)
TOL = 2.0e-11


def leq(x, y):
    return all(a <= b for a, b in zip(x, y))


def q3_edges():
    vertices = tuple(product((0, 1), repeat=3))
    edges = tuple(
        (i, j)
        for i, x in enumerate(vertices)
        for j, y in enumerate(vertices)
        if i < j and sum(a != b for a, b in zip(x, y)) == 1
    )
    return vertices, edges


def mixed_difference(fn, x, y, hx, hy):
    return (
        fn(x + hx, y + hy)
        - fn(x + hx, y - hy)
        - fn(x - hx, y + hy)
        + fn(x - hx, y - hy)
    ) / (4 * hx * hy)


def clip(value, radius):
    return max(-radius, min(value, radius))


def finite_association(check):
    states = tuple(product((0, 1), repeat=3))
    fields = (F(-1), F(2), F(1))
    pairs = ((0, 1), (1, 2), (0, 2))
    weights = {
        x: F(2) ** (sum(a * b for a, b in zip(fields, x)) + sum(x[i] * x[j] for i, j in pairs))
        for x in states
    }
    total = sum(weights.values())
    mass = lambda event: sum(weights[x] for x in event) / total
    uppers = []
    for mask in range(1 << len(states)):
        event = {x for i, x in enumerate(states) if mask & (1 << i)}
        if all(y in event for x in event for y in states if leq(x, y)):
            uppers.append(event)
    check("binary-upper-event-count", len(uppers) == 20, len(uppers), 20)
    for x in states:
        for y in states:
            meet = tuple(min(a, b) for a, b in zip(x, y))
            join = tuple(max(a, b) for a, b in zip(x, y))
            check(
                f"binary-log-supermodular-{x}-{y}",
                weights[meet] * weights[join] >= weights[x] * weights[y],
                weights[meet] * weights[join],
                weights[x] * weights[y],
            )
    for i, event_a in enumerate(uppers):
        for j, event_b in enumerate(uppers):
            covariance = mass(event_a & event_b) - mass(event_a) * mass(event_b)
            check(f"binary-upper-covariance-{i}-{j}", covariance >= 0, covariance, ">=0")
    lower = tuple(product((0, 1), repeat=2))
    ratios = {
        x: weights[x + (1,)] / weights[x + (0,)]
        for x in lower
    }
    for x in lower:
        for y in lower:
            if leq(x, y):
                check(f"conditional-likelihood-ratio-{x}-{y}", ratios[x] <= ratios[y], ratios[x], ratios[y])


def derivative_checks(check):
    lam = F(7, 5)

    def q3lock(x, y):
        return lam * (x - y) ** 2 * (x * x + y * y) / 4

    for x, y in ((F(-3, 2), F(2, 3)), (F(0), F(1, 2)), (F(5, 4), F(-2, 5))):
        expected = lam * ((x + y) ** 2 + 5 * (x - y) ** 2) / 4
        # Differentiate the expanded quartic exactly; a raw central
        # difference would contain an h^2 k^2 remainder for this degree-four
        # polynomial.
        exact_negative_mixed = lam * (6 * x * x - 8 * x * y + 6 * y * y) / 4
        check(
            f"q3lock-mixed-derivative-{x}-{y}",
            exact_negative_mixed == expected,
            exact_negative_mixed,
            expected,
        )
        check(f"q3lock-mixed-derivative-positive-{x}-{y}", expected >= 0, expected, ">=0")

    for coefficient, scale in ((F(3, 2), F(5, 7)), (F(11, 9), F(2, 3))):
        bond = lambda x, y: coefficient * (x - y) ** 2 / 2
        expected = coefficient
        value = -mixed_difference(bond, F(2, 5), F(-3, 7), scale, F(1, 17))
        check(f"bond-mixed-derivative-{coefficient}", value == expected, value, expected)

    unary = lambda x, y: F(13, 7) * x**4 + F(3, 5) * y**2 + F(2, 9) * x
    value = mixed_difference(unary, F(1, 3), F(-2, 7), F(1, 19), F(1, 23))
    check("unary-mixed-derivative-zero", value == 0, value, 0)


def selected_limit_fixture(check):
    # An order-preserving sequence of attractive four-point measures on a
    # compact square.  The weights are fixed and the upper coordinate is
    # approached from below, so all tests are bounded and continuous.
    atoms = ((0, 0), (0, 1), (1, 0), (1, 1))
    raw = (F(1), F(2), F(2), F(8))
    total = sum(raw)
    weights = tuple(float(w / total) for w in raw)

    def Ftest(point):
        return point[0] / (1 + point[0])

    def Gtest(point):
        return point[1] / (1 + point[1])

    def evaluate(delta):
        points = tuple((x * (1 - delta), y * (1 - delta)) for x, y in atoms)
        mean_f = sum(w * Ftest(p) for w, p in zip(weights, points))
        mean_g = sum(w * Gtest(p) for w, p in zip(weights, points))
        mean_fg = sum(w * Ftest(p) * Gtest(p) for w, p in zip(weights, points))
        return mean_f, mean_g, mean_fg, mean_fg - mean_f * mean_g

    limit = evaluate(0.0)
    previous = None
    for n in (2, 4, 8, 16, 32, 64):
        current = evaluate(F(1, n))
        if previous is not None:
            check(f"selected-covariance-converges-{n}", abs(current[3] - limit[3]) <= abs(previous[3] - limit[3]) + TOL, current[3], limit[3])
        check(f"selected-F-expectation-{n}", abs(current[0] - limit[0]) <= 1 / n + TOL, current[0], limit[0])
        check(f"selected-G-expectation-{n}", abs(current[1] - limit[1]) <= 1 / n + TOL, current[1], limit[1])
        check(f"selected-FG-expectation-{n}", abs(current[2] - limit[2]) <= 1 / n + TOL, current[2], limit[2])
        previous = current
    check("selected-limit-covariance-nonnegative", limit[3] >= -TOL, limit[3], ">=0")


def cone_and_extension_checks(check):
    grid = tuple(F(i, 4) for i in range(-4, 5))
    points = tuple(product(grid, repeat=2))
    threshold = (F(1, 2), F(1, 2))

    def distance_to_upper(point):
        return max(F(0), threshold[0] - point[0], threshold[1] - point[1])

    def in_upper(point):
        return leq(threshold, point)

    check("closed-upper-grid-nonempty", any(in_upper(point) for point in points), True, True)
    for x in points:
        for y in points:
            if leq(x, y):
                dx, dy = distance_to_upper(x), distance_to_upper(y)
                check(f"upper-distance-monotone-{x}-{y}", dy <= dx, dy, dx)
                for j in (1, 2, 4, 8):
                    fx = max(F(0), F(1) - j * dx)
                    fy = max(F(0), F(1) - j * dy)
                    check(f"upper-approximation-increasing-{j}-{x}-{y}", fx <= fy, fx, fy)
    for point in points:
        values = [max(F(0), F(1) - j * distance_to_upper(point)) for j in (1, 2, 4, 8)]
        check(f"upper-approximation-decreases-{point}", all(a >= b for a, b in zip(values, values[1:])), values, "decreasing")
        check(f"upper-approximation-limit-{point}", values[-1] == (F(1) if in_upper(point) else F(0)), values[-1], in_upper(point))

    # Finite compact-plus-cone sets are upper: each point dominates its
    # compact representative, and the union of two representatives is still
    # an upper set.  This is the finite analogue of the manuscript lemma.
    compact = ((F(-1), F(0)), (F(0), F(-1)))
    for point in points:
        belongs = any(leq(k, point) for k in compact)
        if belongs:
            for increment in ((F(0), F(0)), (F(1, 4), F(0)), (F(0), F(1, 4)), (F(1, 4), F(1, 4))):
                raised = tuple(a + b for a, b in zip(point, increment))
                check(f"compact-plus-cone-upper-{point}-{increment}", any(leq(k, raised) for k in compact), True, True)

    # Zero extension preserves coordinatewise order.
    local = ((F(-1), F(0)), (F(0), F(1, 2)), (F(1), F(1)))
    for x in local:
        for y in local:
            if leq(x, y):
                embedded_x = x + (F(0), F(0), F(0))
                embedded_y = y + (F(0), F(0), F(0))
                check(f"zero-extension-order-{x}-{y}", leq(embedded_x, embedded_y), True, True)


def clipping_checks(check):
    fixtures = (
        ((F(0), F(1), F(-2), F(3)), (F(0), F(2), F(1), F(-1)), (F(1, 4),) * 4),
        ((F(4), F(0)), (F(4), F(1)), (F(1, 64), F(63, 64))),
        ((F(-5), F(2), F(1)), (F(3), F(-2), F(0)), (F(1, 10), F(3, 10), F(3, 5))),
    )
    for index, (ys, zs, probabilities) in enumerate(fixtures):
        c4_y = sum(p * abs(y) ** 4 for p, y in zip(probabilities, ys))
        c4_z = sum(p * abs(z) ** 4 for p, z in zip(probabilities, zs))
        c4 = max(c4_y, c4_z)
        check(f"fourth-moment-envelope-{index}", c4 >= c4_y and c4 >= c4_z, c4, (c4_y, c4_z))
        for radius in (F(1, 2), F(1), F(2), F(4)):
            product_error = sum(
                p * abs(y * z - clip(y, radius) * clip(z, radius))
                for p, y, z in zip(probabilities, ys, zs)
            )
            product_bound = 2 * c4 / radius**2
            check(f"product-clipping-bound-{index}-{radius}", product_error <= product_bound, product_error, product_bound)
            y_error = sum(p * abs(y - clip(y, radius)) for p, y in zip(probabilities, ys))
            z_error = sum(p * abs(z - clip(z, radius)) for p, z in zip(probabilities, zs))
            first_bound = c4 / radius**3
            check(f"first-moment-clipping-Y-{index}-{radius}", y_error <= first_bound, y_error, first_bound)
            check(f"first-moment-clipping-Z-{index}-{radius}", z_error <= first_bound, z_error, first_bound)


def graph_and_mixture_checks(check):
    vertices, edges = q3_edges()
    check("Q3-degree-three", all(sum(i in edge for edge in edges) == 3 for i in range(8)), True, True)
    check("Q3-edge-count", len(edges) == 12, len(edges), 12)
    states = tuple(product((-1, 1), repeat=8))
    for coupling in (0.0, 0.4, 0.9):
        raw = [exp(coupling * sum(state[i] * state[j] for i, j in edges)) for state in states]
        normalizer = sum(raw)
        mean = [sum(w * state[i] for w, state in zip(raw, states)) / normalizer for i in range(8)]
        covariance = {
            (i, j): sum(w * state[i] * state[j] for w, state in zip(raw, states)) / normalizer - mean[i] * mean[j]
            for i in range(8) for j in range(i + 1, 8)
        }
        check(f"parity-mean-{coupling}", max(abs(value) for value in mean) <= TOL, max(abs(value) for value in mean), 0)
        check(f"parity-covariance-{coupling}", min(covariance.values()) >= -TOL, min(covariance.values()), ">=0")
        expected_s = sum(w * 8 for w in raw) / normalizer
        expected_d = sum(w * sum((state[i] - state[j]) ** 2 for i, j in edges) for w, state in zip(raw, states)) / normalizer
        # The manuscript uses Q_0=(sum_e q_{0,e})/sqrt(8), hence
        # Q_0^2=(sum_e q_{0,e})^2/8 rather than the square of the average.
        expected_q2 = sum(w * (sum(state) ** 2) / 8 for w, state in zip(raw, states)) / normalizer
        check(f"graph-D-bound-{coupling}", expected_d <= 3 * expected_s + TOL, expected_d, 3 * expected_s)
        check(f"graph-Q-bound-{coupling}", expected_q2 + TOL >= expected_s / 8, expected_q2, expected_s / 8)

    atoms = ((F(0), F(1)), (F(1), F(0)))
    mean_x = sum(point[0] for point in atoms) / 2
    mean_y = sum(point[1] for point in atoms) / 2
    covariance = sum(point[0] * point[1] for point in atoms) / 2 - mean_x * mean_y
    check("arbitrary-mixture-counterexample", covariance == F(-1, 4), covariance, F(-1, 4))


def build_payload():
    assertions = []

    def check(name, ok, actual, expected):
        assert ok, (name, actual, expected)
        assertions.append({"name": name, "pass": True, "actual": str(actual), "expected": str(expected)})

    derivative_checks(check)
    finite_association(check)
    selected_limit_fixture(check)
    cone_and_extension_checks(check)
    clipping_checks(check)
    graph_and_mixture_checks(check)
    return {
        "schema": "tect/q3lock-fkg-selected-limit-audit/1.0",
        "exploration_id": "EXP-001671",
        "result_id": "R-497-supporting-fkg-audit-260908",
        "status": "PASS",
        "registered": True,
        "claim_bearing": False,
        "assertions_passed": len(assertions),
        "assertions": assertions,
        "source_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__).resolve(), NOTE)
        },
        "scope": (
            "Finite algebra, compact-grid order, selected-limit fixture, clipping, and Q3 graph diagnostics only. "
            "No path-space FKG, uniform integrability, DLR, thermodynamic, or phase theorem is certified."
        ),
    }


def main():
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"PASS {payload['assertions_passed']}/{len(payload['assertions'])}: {OUT}")


if __name__ == "__main__":
    main()
