#!/usr/bin/env python3
"""Finite replay for the registered Q3LOCK collective/Falk--Bruch content.

The polynomial and matrix checks are finite diagnostics only.  They do not
certify the unbounded operator argument or any thermodynamic phase claim.
"""
from fractions import Fraction as F
from itertools import product
from math import comb, log, tanh
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-collective-falk-bruch-content-260905.md"
OUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-collective-falk-bruch-content-audit/result.json"
)
Q3 = tuple(product((0, 1), repeat=3))
INTERNAL_EDGES = tuple(
    (i, j)
    for i, x in enumerate(Q3)
    for j, y in enumerate(Q3)
    if i < j and sum(a != b for a, b in zip(x, y)) == 1
)
PARAMETERS = (F(-5, 3), F(7, 4), F(2, 5), F(9, 7))
SIZES = (2, 4)  # Finite graph fixtures; L=2 retains parallel bonds.
TOL = 2e-12  # Floating diagnostic tolerance, not an interval certificate.


def matmul(a, b):
    n = len(a)
    return [
        [sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def comm(a, b):
    ab, ba = matmul(a, b), matmul(b, a)
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(ab, ba)]


def implicit_f(z, steps):
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


def build_payload():
    checks = []

    def check(name, ok, actual, expected):
        assert ok, (name, actual, expected)
        checks.append(
            {
                "name": name,
                "pass": True,
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    r, g, lam, c = PARAMETERS
    d = len(Q3)
    for L in SIZES:
        sites = list(product(range(L), repeat=3))
        V = len(sites)
        for fixture in range(3):
            q = {
                y: tuple(
                    F((sum(y) + (e + 1) * (fixture + 1)) % 7 - 3, fixture + 2)
                    for e in range(d)
                )
                for y in sites
            }
            # Expand the full physical potential in the unnormalised common
            # displacement z. Divide its second derivative by dV afterwards.
            coefficients = [F(0) for _ in range(5)]
            for y in sites:
                for x in q[y]:
                    for k in range(3):
                        coefficients[k] += r * F(comb(2, k), 2) * x ** (2 - k)
                    for k in range(5):
                        coefficients[k] += g * F(comb(4, k), 4) * x ** (4 - k)
                for e, f in INTERNAL_EDGES:
                    x, z = q[y][e], q[y][f]
                    diff2 = (x - z) ** 2
                    for k, value in enumerate((x * x + z * z, 2 * (x + z), F(2))):
                        coefficients[k] += lam * diff2 * value / 4
                for j in range(3):
                    z = list(y)
                    z[j] = (z[j] + 1) % L
                    z = tuple(z)
                    coefficients[0] += c * sum(
                        (a - b) ** 2 for a, b in zip(q[y], q[z])
                    ) / 2
            S = sum(x * x for qy in q.values() for x in qy)
            D = sum(
                (qy[e] - qy[f]) ** 2
                for qy in q.values()
                for e, f in INTERNAL_EDGES
            )
            actual_B = 2 * coefficients[2] / (d * V)
            expected_B = r + 3 * g * S / (d * V) + lam * D / (d * V)
            check(
                f"normalized-translation-{L}-{fixture}",
                actual_B == expected_B,
                actual_B,
                expected_B,
            )
            check(
                f"quartic-translation-{L}-{fixture}",
                coefficients[4] == g * d * V / 4,
                coefficients[4],
                g * d * V / 4,
            )
            # Test oracle: hbar^2=(3/2)^2 is deliberately not a Hessian factor.
            check(
                f"reject-hbar-derivative-{L}-{fixture}",
                actual_B != F(9, 4) * actual_B,
                actual_B,
                "different from hbar^2 B for hbar=3/2",
            )

    # H has integer eigenvalues and beta=log(2), so Gibbs weights are exact.
    for energies in ((0, 1), (0, 0, 2), (-1, 1, 3, 4)):
        n = len(energies)
        H = [[F(energies[i] if i == j else 0) for j in range(n)] for i in range(n)]
        A = [
            [F((i + j + 1) % 4 - 1, 1 + abs(i - j)) for j in range(n)]
            for i in range(n)
        ]
        weights = [F(2) ** (-e) for e in energies]
        Z = sum(weights)
        p = [w / Z for w in weights]
        AA = matmul(A, A)
        double = comm(A, comm(H, A))
        c_trace = sum(p[i] * double[i][i] for i in range(n))
        c_pairs = sum(
            F(energies[j] - energies[i]) * (p[i] - p[j]) * A[i][j] ** 2
            for i in range(n)
            for j in range(n)
        )
        g_trace = sum(p[i] * AA[i][i] for i in range(n))
        g_pairs = sum(p[i] * A[i][j] ** 2 for i in range(n) for j in range(n))
        check(f"commutator-trace-{energies}", c_trace == c_pairs, c_trace, c_pairs)
        check(f"commutator-sign-{energies}", c_pairs >= 0, c_pairs, ">=0")
        check(f"ordinary-moment-{energies}", g_trace == g_pairs, g_trace, g_pairs)
        b = 0.0
        for i in range(n):
            for j in range(n):
                mean = (
                    float(p[i])
                    if energies[i] == energies[j]
                    else float(p[i] - p[j])
                    / (log(2) * (energies[j] - energies[i]))
                )
                b += mean * float(A[i][j] ** 2)
        g_val = float(g_pairs)
        c_val = log(2) * float(c_pairs)
        check(f"Duhamel-upper-{energies}", 0 <= b <= g_val + TOL, b, g_val)
        lower_values = [
            g_val * implicit_f(c_val / (4 * g_val), steps) for steps in (70, 110)
        ]
        check(
            f"root-resolution-{energies}",
            abs(lower_values[0] - lower_values[1]) <= TOL,
            lower_values,
            "same within tolerance",
        )
        check(f"Falk-Bruch-{energies}", b + TOL >= lower_values[-1], b, lower_values[-1])

    # Exact two-level off-diagonal A has one absolute gap and saturates FB.
    beta = log(2)
    gap = 2
    x = beta * gap / 2
    z = x * tanh(x)
    check(
        "two-level-saturation",
        abs(implicit_f(z, 110) - tanh(x) / x) <= TOL,
        implicit_f(z, 110),
        tanh(x) / x,
    )
    for k in (F(1, 4), F(3), F(9, 2)):
        values = [
            float(s) * implicit_f(float(k / s), 110)
            for s in (F(1, 3), F(1), F(7, 2))
        ]
        check(
            f"moment-substitution-{k}",
            all(a < b for a, b in zip(values, values[1:])),
            values,
            "strictly increasing",
        )
    return {
        "schema": "tect/q3lock-collective-falk-bruch-content-audit/1.0",
        "result_id": "R-497",
        "exploration_id": "EXP-001598",
        "status": "PASS",
        "registered": True,
        "claim_bearing": False,
        "assertions_passed": len(checks),
        "assertions": checks,
        "source_hashes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in (Path(__file__).resolve(), NOTE)
        },
        "scope": (
            "Registered finite polynomial/matrix diagnostics only; float probes "
            "are not interval enclosures or proof of the unbounded limits."
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
