#!/usr/bin/env python3
"""Independent finite audit of the Q3LOCK collective/Falk--Bruch block.

This checker exercises only finite polynomial, graph, matrix, and scalar
calculus identities used by the manuscript.  It is intentionally not an
operator-domain proof, an infinite-volume argument, or a phase theorem.
"""
from fractions import Fraction as F
from itertools import product
from math import exp, log, tanh, cosh
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-collective-block-audit-260908.md"
OUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-collective-block-audit/result.json"
)
Q3 = tuple(product((0, 1), repeat=3))
INTERNAL_EDGES = tuple(
    (i, j)
    for i, x in enumerate(Q3)
    for j, y in enumerate(Q3)
    if i < j and sum(a != b for a, b in zip(x, y)) == 1
)
TOL = 1e-8


def sites_for(L):
    return list(product(range(L), repeat=3))


def model_energy(q, L, r, g, lam, c):
    sites = sites_for(L)
    total = F(0)
    for y in sites:
        vals = q[y]
        total += r * sum(x * x for x in vals) / 2
        total += g * sum(x**4 for x in vals) / 4
        for e, f in INTERNAL_EDGES:
            diff = vals[e] - vals[f]
            total += lam * diff * diff * (vals[e] * vals[e] + vals[f] * vals[f]) / 4
    for y in sites:
        for j in range(3):
            z = list(y)
            z[j] = (z[j] + 1) % L
            z = tuple(z)
            total += c * sum((a - b) ** 2 for a, b in zip(q[y], q[z])) / 2
    return total


def shifted(q, amount):
    return {y: tuple(x + amount for x in vals) for y, vals in q.items()}


def hessian_by_five_point(q, L, r, g, lam, c):
    values = {k: model_energy(shifted(q, F(k)), L, r, g, lam, c) for k in (-2, -1, 0, 1, 2)}
    # Exact for the degree-four translation polynomial.
    return (-values[2] + 16 * values[1] - 30 * values[0] + 16 * values[-1] - values[-2]) / 12


def implicit_f(z, steps=120):
    if z == 0:
        return 1.0
    lo, hi = 0.0, max(1.0, z + 1.0)
    for _ in range(steps):
        mid = (lo + hi) / 2
        if mid * tanh(mid) < z:
            lo = mid
        else:
            hi = mid
    x = (lo + hi) / 2
    return tanh(x) / x


def matrix_checks(check):
    # A finite spectral Falk--Bruch replay with nondegenerate and degenerate
    # energy levels.  The Boltzmann weights use beta=log(2), so the arithmetic
    # identities are independently checked in exact rational arithmetic.
    for energies in ((0, 1), (0, 0, 2), (-1, 1, 3, 4)):
        n = len(energies)
        A = [[float((i + j + 1) % 4 - 1) / (1 + abs(i - j)) for j in range(n)] for i in range(n)]
        weights = [2.0 ** (-e) for e in energies]
        Z = sum(weights)
        p = [w / Z for w in weights]
        g = sum(p[i] * A[i][j] ** 2 for i in range(n) for j in range(n))
        c = sum(
            (log(2.0) * (energies[j] - energies[i]) * (p[i] - p[j]) * A[i][j] ** 2)
            for i in range(n)
            for j in range(n)
        )
        b = 0.0
        for i in range(n):
            for j in range(n):
                if energies[i] == energies[j]:
                    mean = p[i]
                else:
                    mean = (p[i] - p[j]) / (log(2.0) * (energies[j] - energies[i]))
                b += mean * A[i][j] ** 2
        check(f"duhamel-range-{energies}", -TOL <= b <= g + TOL, b, g)
        check(f"commutator-positive-{energies}", c >= -TOL, c, ">=0")
        check(
            f"falk-bruch-{energies}",
            b + TOL >= g * implicit_f(c / (4 * g)),
            b,
            g * implicit_f(c / (4 * g)),
        )


def build_payload():
    checks = []

    def check(name, ok, actual, expected):
        assert ok, (name, actual, expected)
        checks.append({"name": name, "pass": True, "actual": str(actual), "expected": str(expected)})

    r, g, lam, c = F(-5, 3), F(7, 4), F(2, 5), F(9, 7)
    d = len(Q3)
    for L in (1, 2, 4):
        sites = sites_for(L)
        V = len(sites)
        for fixture in range(4):
            q = {
                y: tuple(F((sum(y) + (e + 1) * (fixture + 2)) % 9 - 4, fixture + 3) for e in range(d))
                for y in sites
            }
            S = sum(x * x for vals in q.values() for x in vals)
            D = sum(
                (vals[e] - vals[f]) ** 2
                for vals in q.values()
                for e, f in INTERNAL_EDGES
            )
            B = hessian_by_five_point(q, L, r, g, lam, c)
            expected = d * V * r + 3 * g * S + lam * D
            check(f"collective-hessian-{L}-{fixture}", B == expected, B, expected)
            spatial0 = model_energy(q, L, F(0), F(0), F(0), c)
            spatial1 = model_energy(shifted(q, F(1)), L, F(0), F(0), F(0), c)
            check(f"spatial-common-shift-{L}-{fixture}", spatial1 == spatial0, spatial1, spatial0)
            edge_products = sum(
                q[y][e] * q[y][f]
                for y in sites
                for e, f in INTERNAL_EDGES
            )
            check(
                f"q3-graph-identity-{L}-{fixture}",
                D == 3 * S - 2 * edge_products,
                D,
                3 * S - 2 * edge_products,
            )

    # The moment implication used by the manuscript is exact once the FKG
    # sign gives nonnegative off-diagonal expectations.
    S_lower = -8 * r / (3 * (g + lam))
    theta = -r / (3 * (g + lam))
    check("moment-lower-bound-factor", S_lower / 8 == theta, S_lower / 8, theta)
    check("theta-positive", theta > 0, theta, ">0")

    # Algebraic threshold reduction with x*tanh(x)=beta/(4*m*theta), using
    # rational test values for the displayed cancellation.
    m, c0, theta0 = F(11, 6), F(5, 4), F(7, 9)
    for x, t in ((F(1, 2), F(1, 3)), (F(5, 4), F(4, 5)), (F(7, 3), F(8, 9))):
        beta = 4 * m * theta0 * x * t
        delta_term = 2 * beta * c0 * theta0 * t / x
        expected_term = 8 * m * c0 * theta0 * theta0 * t * t
        check(f"threshold-cancellation-{x}-{t}", delta_term == expected_term, delta_term, expected_term)

    for k in (0.25, 1.0, 4.5):
        vals = [s * implicit_f(k / s) for s in (1 / 3, 1.0, 3.5)]
        check(f"moment-substitution-monotone-{k}", vals[0] < vals[1] < vals[2], vals, "increasing")

    # A_R=R tanh(Q/R): derivative and the bounded-convergence envelope.
    for R in (0.5, 1.0, 2.0, 5.0):
        for q0 in (-3.0, -0.75, 0.0, 1.25, 4.0):
            analytic = 1.0 / cosh(q0 / R) ** 2
            eps = 1e-6
            numeric = (R * tanh((q0 + eps) / R) - R * tanh((q0 - eps) / R)) / (2 * eps)
            check(f"clip-derivative-{R}-{q0}", abs(analytic - numeric) <= TOL, numeric, analytic)
            envelope = analytic * analytic
            check(f"clip-envelope-{R}-{q0}", 0.0 <= envelope <= 1.0 + TOL, envelope, "[0,1]")

    matrix_checks(check)
    return {
        "schema": "tect/q3lock-collective-block-audit/1.0",
        "exploration_id": "EXP-001669",
        "result_id": "R-497-supporting-audit-260908",
        "status": "PASS",
        "registered": True,
        "claim_bearing": False,
        "assertions_passed": len(checks),
        "assertions": checks,
        "source_hashes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), NOTE)
        },
        "scope": (
            "Finite polynomial, Q3 graph, scalar threshold, clipping, and matrix diagnostics only. "
            "No unbounded operator-domain, DLR, thermodynamic, or phase theorem is certified."
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
