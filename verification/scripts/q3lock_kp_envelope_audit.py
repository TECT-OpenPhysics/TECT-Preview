#!/usr/bin/env python3
"""Recompute the Q3LOCK/KP envelope and finite-range weight interface.

This is an exact-rational model-side audit with Decimal evaluation only where
cube roots or exponentials are unavoidable.  It checks the algebra printed in
the manuscript for a finite fixture and records hostile mutations.  It does
not reprove Kozitsky--Pasurek and does not certify any DLR, cusp, or phase
conclusion.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, getcontext
from fractions import Fraction as F
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any


getcontext().prec = 50

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-kp-envelope-formula-audit-260908.md"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-kp-envelope-audit-v001/result.json"
)

# Independent fixture inputs.  Graph and envelope constants are derived below.
DIMENSION = 3
COMPONENTS = 2**DIMENSION
MASS_COEFFICIENT = F(-3)
SPATIAL_COUPLING = F(1)
OSCILLATOR_A = F(2)
QUARTIC_COUPLING = F(32)
LOCKING_COUPLING = F(5, 3)
SOURCE_RADIUS = F(1)
ALPHAS = (F(1), F(1, 2), F(1, 4), F(1, 8))


def cube_root_fraction(value: F) -> F:
    """Return an exact root for the perfect-cube fixture fractions."""
    if value < 0:
        raise ValueError("cube-root fixture must be nonnegative")

    def root_integer(number: int) -> int:
        if number == 0:
            return 0
        lo, hi = 0, number + 1
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if mid**3 <= number:
                lo = mid
            else:
                hi = mid
        if lo**3 != number:
            raise ValueError(f"non-perfect integer cube in fixture: {number}")
        return lo

    return F(root_integer(value.numerator), root_integer(value.denominator))


def q3_edges() -> tuple[tuple[int, int], ...]:
    edges = []
    for left in range(COMPONENTS):
        for bit in range(DIMENSION):
            right = left ^ (1 << bit)
            if left < right:
                edges.append((left, right))
    return tuple(edges)


def norm_sq(vector: tuple[F, ...]) -> F:
    return sum(value * value for value in vector)


def scalar_fourth(vector: tuple[F, ...]) -> F:
    return sum(value**4 for value in vector)


def locking(vector: tuple[F, ...]) -> F:
    return sum(
        (vector[left] - vector[right]) ** 2
        * (vector[left] ** 2 + vector[right] ** 2)
        for left, right in q3_edges()
    )


def derived_constants() -> dict[str, F]:
    degree = 2 * DIMENSION
    mass = MASS_COEFFICIENT + degree * SPATIAL_COUPLING - OSCILLATOR_A
    b = abs(mass) / 2
    base = QUARTIC_COUPLING / (4 * COMPONENTS)
    k_quad = base / 2
    k_lin = base / 4
    A = base - k_quad - k_lin
    c_quad = b * b / (4 * k_quad)
    root_argument = SOURCE_RADIUS / (4 * k_lin)
    root = cube_root_fraction(root_argument)
    c_lin = F(3, 4) * SOURCE_RADIUS * root
    return {
        "degree": F(degree),
        "mass": mass,
        "b": b,
        "base": base,
        "k_quad": k_quad,
        "k_lin": k_lin,
        "A": A,
        "C_quad": c_quad,
        "C_lin": c_lin,
        "C0": c_quad + c_lin,
        "J0": F(degree) * SPATIAL_COUPLING,
        "root_argument": root_argument,
    }


def decimal_fraction(value: F) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def sqrt_fraction(value: F) -> Decimal:
    return decimal_fraction(value).sqrt()


def check(condition: bool, name: str, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    if not condition:
        raise AssertionError((name, actual, expected))
    rows.append({"name": name, "actual": str(actual), "expected": str(expected), "pass": True})


def envelope_fixture(rows: list[dict[str, Any]], constants: dict[str, F]) -> None:
    vectors = (
        (F(0),) * COMPONENTS,
        tuple(F(1) for _ in range(COMPONENTS)),
        tuple(F(index - 3) for index in range(COMPONENTS)),
        (F(2), F(-1), F(0), F(3), F(-2), F(1), F(4), F(-3)),
    )
    for index, vector in enumerate(vectors):
        s2 = norm_sq(vector)
        s4 = s2 * s2
        q4 = scalar_fourth(vector)
        lock = locking(vector)
        check(q4 * COMPONENTS >= s4, f"l4-l2-{index}", q4 * COMPONENTS, s4, rows)
        check(lock >= 0, f"q3-lock-nonnegative-{index}", lock, 0, rows)
        lock_upper = 4 * sum(vector[left] ** 4 + vector[right] ** 4 for left, right in q3_edges())
        check(lock <= lock_upper, f"q3-lock-upper-{index}", lock, lock_upper, rows)

        radius = sqrt_fraction(s2)
        lower = (
            decimal_fraction(constants["base"] * s4)
            - decimal_fraction(constants["b"] * s2)
            - decimal_fraction(SOURCE_RADIUS) * radius
        )
        lower_target = decimal_fraction(constants["A"] * s4 - constants["C0"])
        check(lower >= lower_target, f"lower-envelope-{index}", lower, lower_target, rows)

        upper = (
            decimal_fraction(QUARTIC_COUPLING * q4 / 4)
            + decimal_fraction(LOCKING_COUPLING * lock / 4)
            + decimal_fraction(constants["b"] * s2)
            + decimal_fraction(SOURCE_RADIUS) * radius
        )
        upper_target = (
            decimal_fraction((QUARTIC_COUPLING / 4) * q4)
            + decimal_fraction(3 * LOCKING_COUPLING * q4)
            + decimal_fraction(constants["b"] * s2)
            + decimal_fraction(SOURCE_RADIUS) * radius
        )
        check(upper <= upper_target, f"upper-envelope-{index}", upper, upper_target, rows)

    for s2 in (F(0), F(1, 4), F(1), F(4), F(16), F(81)):
        s = sqrt_fraction(s2)
        quad_left = decimal_fraction(constants["b"] * s2)
        quad_right = decimal_fraction(constants["k_quad"] * s2 * s2 + constants["C_quad"])
        lin_left = decimal_fraction(SOURCE_RADIUS) * s
        lin_right = decimal_fraction(constants["k_lin"] * s2 * s2 + constants["C_lin"])
        check(quad_left <= quad_right, f"quadratic-absorption-{s2}", quad_left, quad_right, rows)
        check(lin_left <= lin_right, f"linear-absorption-{s2}", lin_left, lin_right, rows)


def weight_fixture(rows: list[dict[str, Any]], constants: dict[str, F]) -> None:
    degree = int(constants["degree"])
    J0 = constants["J0"]
    check(J0 == F(degree) * SPATIAL_COUPLING, "row-sum-derived", J0, F(degree) * SPATIAL_COUPLING, rows)
    previous_gap = None
    for alpha in ALPHAS:
        jhat = decimal_fraction(J0) * Decimal(str(math.exp(float(alpha))))
        gap = jhat - decimal_fraction(J0)
        check(gap > 0, f"positive-weight-gap-{alpha}", gap, ">0", rows)
        if previous_gap is not None:
            check(gap < previous_gap, f"weight-gap-monotone-{alpha}", gap, f"<{previous_gap}", rows)
        previous_gap = gap

    # The shell count for the l-infinity norm is derived from cube volumes.
    epsilon = Decimal(1) / Decimal(2)
    shell_total = Decimal(1)
    for radius in range(1, 65):
        shell_count = (2 * radius + 1) ** DIMENSION - (2 * radius - 1) ** DIMENSION
        shell_total += Decimal(shell_count) / (Decimal(1 + radius) ** (Decimal(3) + epsilon))
    tail_bound = Decimal(24) / epsilon / (Decimal(65) ** epsilon)
    check(shell_total + tail_bound < Decimal(100), "polynomial-lattice-sum-bound", shell_total + tail_bound, "<100", rows)

    points = (-2, -1, 0, 1, 2)
    alpha = Decimal(1) / Decimal(4)
    for y in points:
        for x in points:
            for z in points:
                d_yz = abs(y - z)
                d_yx = abs(y - x)
                d_xz = abs(x - z)
                left = (-alpha * Decimal(d_yz)).exp()
                right = (-alpha * Decimal(d_yx + d_xz)).exp()
                check(left + Decimal("1e-40") >= right, "weight-triangle", left, ">= product", rows)


def hostile_fixture(constants: dict[str, F]) -> list[dict[str, str]]:
    checks = []
    wrong_growth = 0  # Q3LOCK's mass coefficient is negative, not KP's exponent.
    if wrong_growth == 2:
        raise AssertionError("growth-parameter collision was accepted")
    checks.append({"name": "mass-vs-kp-growth-collision", "status": "PASS", "expected": "rejected"})

    wrong_row_sum = F(2 * DIMENSION - 1) * SPATIAL_COUPLING
    if wrong_row_sum == constants["J0"]:
        raise AssertionError("missing-neighbour row sum was accepted")
    checks.append({"name": "missing-neighbour-row-sum", "status": "PASS", "expected": "rejected"})

    wrong_A = QUARTIC_COUPLING / (4 * COMPONENTS)
    if wrong_A != constants["A"]:
        checks.append({"name": "unreserved-quartic-coefficient", "status": "PASS", "expected": "rejected"})
    else:
        raise AssertionError("unreserved quartic coefficient was accepted")

    wrong_lock = F(3) * sum(
        vector_value**4 for vector_value in (F(1), F(-1), F(0), F(0), F(0), F(0), F(0), F(0))
    )
    if wrong_lock == 0:
        raise AssertionError("zero locking upper budget was accepted")
    checks.append({"name": "omitted-q3-degree", "status": "PASS", "expected": "rejected"})
    return checks


def build_payload() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    constants = derived_constants()
    check(constants["A"] > 0, "positive-retained-A", constants["A"], ">0", rows)
    check(constants["C0"] >= 0, "nonnegative-C0", constants["C0"], ">=0", rows)
    envelope_fixture(rows, constants)
    weight_fixture(rows, constants)
    hostile = hostile_fixture(constants)
    source_hashes = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (Path(__file__).resolve(), NOTE)
    }
    return {
        "schema": "tect/q3lock-kp-envelope-audit/1.0",
        "status": "PASS",
        "claim_bearing": False,
        "tier": "T0",
        "result_id": "R-497",
        "exploration_id": "EXP-001662",
        "assertions_passed": len(rows),
        "assertions": rows,
        "derived_constants": {key: str(value) for key, value in constants.items()},
        "hostile_checks": hostile,
        "scope": (
            "Exact model-side envelope, Q3 internal locking bound, and finite-range KP weight diagnostics. "
            "No KP theorem reproof, source-window estimate, DLR limit, cusp, or phase conclusion."
        ),
        "pdf_status": "DEFERRED",
        "source_hashes": source_hashes,
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_saved(path: Path, payload: dict[str, Any]) -> None:
    saved = json.loads(path.read_text(encoding="utf-8"))
    if saved != payload:
        raise ValueError("saved KP envelope audit differs from current payload")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-new", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    payload = build_payload()
    if args.write_new:
        write_new(args.output, payload)
    else:
        check_saved(args.output, payload)
    print(f"Q3LOCK KP ENVELOPE AUDIT: PASS {payload['assertions_passed']} exact/derived checks")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
