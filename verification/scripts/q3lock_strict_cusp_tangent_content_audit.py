#!/usr/bin/env python3
"""Finite replay for the registered Q3LOCK cusp/tangent content.

The parity law, tail example and threshold fixtures are normalization and
logic controls.  The synthetic integral parameter is not the Q3LOCK I_3.
"""
from fractions import Fraction as F
from math import atanh, sqrt, tanh
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-strict-cusp-tangent-content-260905.md"
OUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-strict-cusp-tangent-content-audit/result.json"
)
TOL = 3e-12  # Floating diagnostic tolerance, not an interval enclosure.


def root(z, steps):
    lo, hi = 0.0, max(1.0, z + 1.0)
    for _ in range(steps):
        mid = (lo + hi) / 2
        if mid * tanh(mid) < z:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build_payload():
    rows = []

    def check(name, ok, actual, expected):
        assert ok, (name, actual, expected)
        rows.append(
            {
                "name": name,
                "pass": True,
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    # Derive the exponential tail integral's polynomial from the equation
    # q'(R)-a q(R)=-a R^2, rather than pasting its evaluated tail value.
    for a in (F(1, 3), F(2), F(7, 2)):
        q = [F(0), F(0), F(1)]
        q[1] = 2 * q[2] / a
        q[0] = q[1] / a
        derivative_minus = [
            q[1] - a * q[0],
            2 * q[2] - a * q[1],
            -a * q[2],
        ]
        check(
            f"tail-antiderivative-{a}",
            derivative_minus == [0, 0, -a],
            derivative_minus,
            [0, 0, -a],
        )
        check(
            f"tail-prefactor-{a}",
            q == [2 / a**2, 2 / a, 1],
            q,
            [2 / a**2, 2 / a, 1],
        )

    for beta in (F(1, 3), F(5, 2)):
        for V in (8, 64):
            M = F(7, 5)  # Nonzero two-point test amplitude.
            atoms = (-beta * V * M, beta * V * M)
            EY2 = sum((x / V) ** 2 for x in atoms) / len(atoms)
            Pi = sum((x / (beta * V)) ** 2 for x in atoms) / len(atoms)
            slope_p = beta * M  # Exact limiting log-cosh slope for this law.
            slope_P = slope_p / (8 * beta)
            check(
                f"zero-mode-dictionary-{beta}-{V}",
                EY2 == beta**2 * Pi,
                EY2,
                beta**2 * Pi,
            )
            check(
                f"Griffiths-saturation-{beta}-{V}",
                slope_p**2 == EY2,
                slope_p**2,
                EY2,
            )
            check(f"fine-pressure-factor-{beta}-{V}", 8 * slope_P == M, 8 * slope_P, M)

    # Rare spikes show why weak convergence without source control is not enough.
    for n in (2, 4, 8):
        spike_weight = F(1, n * n)
        moment = spike_weight * n * n
        check(f"rare-spike-moment-{n}", moment == 1, moment, 1)
        check(
            f"rare-spike-probability-{n}",
            0 < spike_weight < 1,
            spike_weight,
            "(0,1)",
        )

    # Check threshold algebra with an explicitly synthetic positive integral J.
    for m, c, theta, ratio in (
        (1.0, 1.5, 0.75, 0.25),
        (2.0, 0.7, 1.25, 0.6),
    ):
        A0 = 8 * c * m * theta**2
        J = ratio * A0
        rho = sqrt(J / A0)
        beta_star = 4 * m * theta * atanh(rho) * rho
        for scale in (0.7, 1.0, 1.8):
            beta = scale * beta_star
            xs = [
                root(beta / (4 * m * theta), steps) for steps in (70, 110)
            ]
            x = xs[-1]
            delta = theta * tanh(x) / x - J / (2 * beta * c)
            rhs = A0 * tanh(x) ** 2 - J
            tag = f"{m}-{c}-{theta}-{scale}"
            check(
                f"root-resolution-{tag}",
                abs(xs[0] - xs[1]) <= TOL,
                xs,
                "same within tolerance",
            )
            check(
                f"threshold-identity-{tag}",
                abs(2 * beta * c * delta - rhs) <= TOL,
                2 * beta * c * delta,
                rhs,
            )
            check(
                f"threshold-sign-{tag}",
                abs(delta) <= TOL if scale == 1 else (delta > 0) == (scale > 1),
                delta,
                scale,
            )

    return {
        "schema": "tect/q3lock-strict-cusp-tangent-content-audit/1.0",
        "result_id": "R-497",
        "exploration_id": "EXP-001598",
        "status": "PASS",
        "registered": True,
        "claim_bearing": False,
        "assertions_passed": len(rows),
        "assertions": rows,
        "source_hashes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in (Path(__file__).resolve(), NOTE)
        },
        "scope": (
            "Registered finite normalization/tail checks and floating synthetic-"
            "threshold probes; not a Q3LOCK phase computation."
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
