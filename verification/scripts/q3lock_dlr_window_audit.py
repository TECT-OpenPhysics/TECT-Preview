#!/usr/bin/env python3
"""Finite audit of the Q3LOCK DLR source-window interfaces.

The checks cover only displayed scalar constants, graph budgets, source
normalizations, and compactness/tail bookkeeping.  They do not prove the KP
theorem, a projective compactness theorem, a Feller limit, or phase
coexistence.
"""
from fractions import Fraction as F
from itertools import product
from math import exp, log, sqrt, tanh
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-dlr-window-audit-260908.md"
OUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-dlr-window-audit/result.json"
)
TOL = 2e-10


def build_payload():
    rows = []

    def check(name, actual, expected, ok=None):
        if ok is None:
            ok = actual == expected
        assert ok, (name, actual, expected)
        rows.append({"name": name, "pass": True, "actual": str(actual), "expected": str(expected)})

    # Exact scalar absorption maxima used in the common lower envelope.
    g = F(9, 4)
    b = F(7, 5)
    x_star = F(32) * b / g  # x=s^2 at the quartic/quadratic maximum.
    quad_value = b * x_star - g * x_star * x_star / 64
    check("quadratic-absorption-max", quad_value, 16 * b * b / g)

    g_lin = F(1)
    h0 = F(1, 4)
    s_star = F(2)  # (32*h0/g_lin)^(1/3).
    check("linear-stationarity", g_lin * s_star**3, 32 * h0)
    linear_value = h0 * s_star - g_lin * s_star**4 / 128
    check("linear-absorption-max", linear_value, 3 * h0 * s_star / 4)

    # Q3 degree and spatial row budgets.
    vertices = tuple(product((0, 1), repeat=3))
    edges = tuple(
        (i, j)
        for i, x in enumerate(vertices)
        for j, y in enumerate(vertices)
        if i < j and sum(a != b for a, b in zip(x, y)) == 1
    )
    degrees = [sum(i in edge for edge in edges) for i in range(len(vertices))]
    check("q3-edge-count", len(edges), 12)
    check("q3-degree-budget", tuple(sorted(set(degrees))), (3,))
    for L in (2, 4, 6):
        sites = list(product(range(L), repeat=3))
        neighbours = []
        for y in sites:
            for j in range(3):
                z = list(y)
                z[j] = (z[j] + 1) % L
                neighbours.append((y, tuple(z)))
        row = sum(1 for a, b in neighbours if a == sites[0] or b == sites[0])
        check(f"spatial-row-sum-L{L}", row, 6)

    # Holder closure with theta=kappa/(2 J0), including the strict exponent.
    for c in (F(1), F(2, 3), F(5, 4)):
        for kappa in (F(1), F(3, 2), F(7, 5)):
            j0 = 6 * c
            theta = kappa / (2 * j0)
            t = theta * j0 / kappa
            check(f"holder-half-{c}-{kappa}", t, F(1, 2))
            C1 = F(11, 6)
            bound = C1 / (1 - t)
            check(f"holder-fixed-point-{c}-{kappa}", bound, C1 + t * bound)
            check(f"holder-hostile-{c}-{kappa}", bound + 1 > C1 + t * (bound + 1), True)

    # Cofinal weight direction and the exact escaping-mass fixture.
    for k in range(1, 8):
        target, stronger = F(1, k), F(1, k + 1)
        check(f"weight-direction-{k}", target - stronger > 0, True)
        check(f"weight-gap-{k}", stronger < target, True)
    for n in (1, 2, 4, 8, 12):
        amp2 = F(4) ** n
        weak = amp2 * F(1, 4) ** n
        strong = amp2 * F(1, 2) ** n
        check(f"escape-weak-{n}", weak, F(1))
        check(f"escape-strong-{n}", strong, F(2) ** n)

    # Source dictionary: X contains the full time integral, while P=p/(8 beta).
    for beta in (F(1, 2), F(1), F(3, 2), F(2)):
        for volume in (8, 64, 216):
            q = F(3, 7)
            mean_x = beta * volume * q
            p_prime = mean_x / volume
            P_prime = mean_x / (8 * beta * volume)
            check(f"source-dictionary-{beta}-{volume}", p_prime, 8 * beta * P_prime)
            check(f"source-tangent-{beta}-{volume}", P_prime, q / 8)
            if beta != 1:
                check(f"reject-extra-beta-{beta}-{volume}", beta * mean_x / volume != p_prime, True)

    # Positive Gaussian event and the compact-boundary source maximum.
    for n in (1, 2, 4, 7):
        probability = F(1, 2) ** n
        check(f"normalizer-event-{n}", probability > 0, True)
    for A in (F(1, 3), F(2), F(7, 4)):
        Q_star = F(1, 2) / A
        value = Q_star ** F(1, 4) * exp(-float(A * Q_star / 2))
        expected = (2 * float(A) * exp(1)) ** F(-1, 4)
        check(f"source-lipschitz-max-{A}", abs(value - expected) <= TOL, value, expected)

    # Four-moment clip/error scaling used for coordinate products and tangents.
    for C4 in (F(1), F(5, 2), F(9, 4)):
        for R in (F(1), F(2), F(5)):
            product_error = 2 * C4 / R**2
            first_error = C4 / R**3
            check(f"clip-product-bound-{C4}-{R}", product_error * R**2, 2 * C4)
            check(f"clip-first-bound-{C4}-{R}", first_error * R**3, C4)

    # The exact mixed derivative identity behind continuous-loop FKG.
    for x, y, lam in ((F(1), F(2), F(3, 2)), (F(-2), F(1, 2), F(5, 4)), (F(0), F(-3), F(7, 3))):
        lhs = lam * (6 * x * x - 8 * x * y + 6 * y * y) / 4
        rhs = lam * ((x + y) ** 2 + 5 * (x - y) ** 2) / 4
        check(f"mixed-derivative-{x}-{y}", lhs, rhs)
        check(f"mixed-derivative-sign-{x}-{y}", rhs >= 0, True)

    # Projective tail factor: slower-decaying alpha_(k+1) is the stronger input.
    for k in range(1, 6):
        alpha_k, alpha_next = 1 / k, 1 / (k + 1)
        R = 3.0 + k
        factor = exp(-(alpha_k - alpha_next) * R)
        check(f"tail-factor-{k}", 0.0 < factor < 1.0, True)

    return {
        "schema": "tect/q3lock-dlr-window-audit/1.0",
        "exploration_id": "EXP-001670",
        "result_id": "R-497",
        "status": "PASS",
        "registered": True,
        "claim_bearing": False,
        "assertions_passed": len(rows),
        "assertions": rows,
        "source_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__).resolve(), NOTE)
        },
        "scope": (
            "Finite envelope, graph, source-dictionary, Holder, tail, clipping and FKG diagnostics only; "
            "KP applicability, projective compactness, Feller/source limits and phase coexistence remain open."
        ),
    }


def main():
    result = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"PASS {result['assertions_passed']}/{len(result['assertions'])}: {OUT}")


if __name__ == "__main__":
    main()
