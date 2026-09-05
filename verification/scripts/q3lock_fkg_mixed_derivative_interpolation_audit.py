#!/usr/bin/env python3
"""Finite Q3LOCK FKG mixed-derivative and interpolation audit.

The verifier checks exact rational identities for the Q3 edge potential, the
quadratic difference term, finite-coordinate supermodularity, periodic
piecewise-linear interpolation, and clipped coordinate products.  It is a
diagnostic for the P-06 proof text.  It does not prove a loop limit, a
thermodynamic limit, a source cusp, or a DLR theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-fkg-mixed-derivative-interpolation-audit/result.json"
)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def q3_potential(x: Fraction, y: Fraction, lam: Fraction) -> Fraction:
    return lam * Fraction(1, 4) * (x - y) ** 2 * (x**2 + y**2)


def q3_mixed_derivative(x: Fraction, y: Fraction, lam: Fraction) -> Fraction:
    return lam * Fraction(1, 4) * (6 * x**2 - 8 * x * y + 6 * y**2)


def q3_sum_of_squares(x: Fraction, y: Fraction, lam: Fraction) -> Fraction:
    return lam * Fraction(1, 4) * ((x + y) ** 2 + 5 * (x - y) ** 2)


def quadratic_pair(x: Fraction, y: Fraction, kappa: Fraction) -> Fraction:
    return -kappa * Fraction(1, 2) * (x - y) ** 2


def quadratic_mixed_derivative(kappa: Fraction) -> Fraction:
    return kappa


def rectangle_increment(
    pair_function: Callable[[Fraction, Fraction], Fraction],
    first: tuple[Fraction, Fraction],
    second: tuple[Fraction, Fraction],
) -> Fraction:
    meet = (min(first[0], second[0]), min(first[1], second[1]))
    join = (max(first[0], second[0]), max(first[1], second[1]))
    return (
        pair_function(*meet)
        + pair_function(*join)
        - pair_function(*first)
        - pair_function(*second)
    )


def interpolate(values: tuple[Fraction, ...], index: int, theta: Fraction) -> Fraction:
    successor = (index + 1) % len(values)
    return (1 - theta) * values[index] + theta * values[successor]


def hostile_interpolate(
    values: tuple[Fraction, ...], index: int, theta: Fraction
) -> Fraction:
    successor = (index + 1) % len(values)
    return (1 + theta) * values[index] - theta * values[successor]


def clip(value: Fraction, radius: Fraction) -> Fraction:
    return max(-radius, min(value, radius))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    lam = Fraction(3, 2)
    kappa = Fraction(5, 4)
    values = [
        Fraction(-3),
        Fraction(-1),
        Fraction(0),
        Fraction(2),
        Fraction(4),
    ]

    mixed_rows: list[dict[str, str]] = []
    for x in values:
        for y in values:
            mixed = q3_mixed_derivative(x, y, lam)
            sum_of_squares = q3_sum_of_squares(x, y, lam)
            audit.check(
                "Q3 mixed derivative identity",
                mixed == sum_of_squares,
                mixed,
                sum_of_squares,
                "q3_derivative",
            )
            audit.check(
                "Q3 mixed derivative nonnegative",
                mixed >= 0,
                mixed,
                ">=0",
                "q3_derivative",
            )
            mixed_rows.append({"x": str(x), "y": str(y), "mixed": str(mixed)})

    q3_pair = lambda x, y: -q3_potential(x, y, lam)
    quadratic = lambda x, y: quadratic_pair(x, y, kappa)
    pair_fixtures = [
        (Fraction(-3), Fraction(2), Fraction(1), Fraction(4)),
        (Fraction(2), Fraction(-1), Fraction(-2), Fraction(3)),
        (Fraction(-1), Fraction(-1), Fraction(4), Fraction(0)),
        (Fraction(0), Fraction(4), Fraction(-3), Fraction(2)),
    ]
    rectangle_rows: list[dict[str, str]] = []
    for first_x, first_y, second_x, second_y in pair_fixtures:
        first = (first_x, first_y)
        second = (second_x, second_y)
        q3_increment = rectangle_increment(q3_pair, first, second)
        quadratic_increment = rectangle_increment(quadratic, first, second)
        audit.check(
            "Q3 rectangle supermodularity",
            q3_increment >= 0,
            q3_increment,
            ">=0",
            "supermodularity",
        )
        audit.check(
            "quadratic rectangle supermodularity",
            quadratic_increment >= 0,
            quadratic_increment,
            ">=0",
            "supermodularity",
        )
        rectangle_rows.append(
            {
                "first": [str(item) for item in first],
                "second": [str(item) for item in second],
                "q3_increment": str(q3_increment),
                "quadratic_increment": str(quadratic_increment),
            }
        )

    audit.check(
        "quadratic mixed derivative identity",
        quadratic_mixed_derivative(kappa) == kappa,
        quadratic_mixed_derivative(kappa),
        kappa,
        "quadratic_derivative",
    )
    hostile_q3 = q3_mixed_derivative(Fraction(1), Fraction(-1), -lam)
    audit.check(
        "negative lambda mutation is rejected",
        hostile_q3 < 0,
        hostile_q3,
        "<0",
        "hostile",
    )
    hostile_kappa_increment = rectangle_increment(
        lambda x, y: quadratic_pair(x, y, -kappa),
        pair_fixtures[1][:2],
        pair_fixtures[1][2:],
    )
    audit.check(
        "negative quadratic coupling mutation is rejected",
        hostile_kappa_increment < 0,
        hostile_kappa_increment,
        "<0",
        "hostile",
    )

    x_loop = (Fraction(0), Fraction(-2), Fraction(1), Fraction(3), Fraction(-1))
    y_loop = (Fraction(1), Fraction(-1), Fraction(2), Fraction(4), Fraction(0))
    assert all(left <= right for left, right in zip(x_loop, y_loop))
    theta_values = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)]
    interpolation_rows: list[dict[str, str | int]] = []
    for index in range(len(x_loop)):
        for theta in theta_values:
            interpolated_x = interpolate(x_loop, index, theta)
            interpolated_y = interpolate(y_loop, index, theta)
            audit.check(
                "periodic interpolation preserves order",
                interpolated_x <= interpolated_y,
                interpolated_x,
                "<=" + str(interpolated_y),
                "interpolation",
            )
            interpolation_rows.append(
                {
                    "index": index,
                    "theta": str(theta),
                    "x": str(interpolated_x),
                    "y": str(interpolated_y),
                }
            )

    hostile_x = (Fraction(0), Fraction(0))
    hostile_y = (Fraction(0), Fraction(10))
    hostile_theta = Fraction(1, 2)
    hostile_x_value = hostile_interpolate(hostile_x, 0, hostile_theta)
    hostile_y_value = hostile_interpolate(hostile_y, 0, hostile_theta)
    audit.check(
        "negative interpolation coefficient reverses order",
        hostile_x_value > hostile_y_value,
        hostile_x_value,
        "> " + str(hostile_y_value),
        "hostile",
    )

    clip_values = [Fraction(-7), Fraction(-3), Fraction(-1), Fraction(0), Fraction(2), Fraction(6)]
    clip_rows: list[dict[str, str | int]] = []
    for radius in (Fraction(1), Fraction(2), Fraction(5)):
        for value in clip_values:
            shifted = clip(value, radius) + radius
            audit.check(
                "shifted clip lower bound",
                0 <= shifted,
                shifted,
                ">=0",
                "clip",
            )
            audit.check(
                "shifted clip upper bound",
                shifted <= 2 * radius,
                shifted,
                "<=2R",
                "clip",
            )
            clip_rows.append(
                {"R": str(radius), "value": str(value), "shifted": str(shifted)}
            )
        for lower in clip_values:
            for upper in clip_values:
                if lower <= upper:
                    audit.check(
                        "clip is increasing",
                        clip(lower, radius) <= clip(upper, radius),
                        (clip(lower, radius), clip(upper, radius)),
                        "<=",
                        "clip",
                    )

    product_pairs = [
        (Fraction(-7), Fraction(-3), Fraction(-1), Fraction(2)),
        (Fraction(-1), Fraction(0), Fraction(2), Fraction(6)),
        (Fraction(0), Fraction(-7), Fraction(6), Fraction(-1)),
    ]
    product_rows: list[dict[str, str]] = []
    radius = Fraction(2)
    for y0, z0, y1, z1 in product_pairs:
        lower = (y0, z0)
        upper = (y1, z1)
        lower_product = (clip(y0, radius) + radius) * (clip(z0, radius) + radius)
        upper_product = (clip(y1, radius) + radius) * (clip(z1, radius) + radius)
        audit.check(
            "shifted clipped product is increasing",
            lower_product <= upper_product,
            lower_product,
            "<=" + str(upper_product),
            "clip_product",
        )
        product_rows.append(
            {
                "lower": [str(item) for item in lower],
                "upper": [str(item) for item in upper],
                "lower_product": str(lower_product),
                "upper_product": str(upper_product),
            }
        )

    domination_rows: list[dict[str, str]] = []
    for radius in (Fraction(1), Fraction(2), Fraction(5)):
        for y in clip_values:
            for z in clip_values:
                clipped_product = clip(y, radius) * clip(z, radius)
                original_product = y * z
                audit.check(
                    "clip product domination",
                    abs(clipped_product) <= abs(original_product),
                    abs(clipped_product),
                    "<=" + str(abs(original_product)),
                    "clip_domination",
                )
                domination_rows.append(
                    {
                        "R": str(radius),
                        "Y": str(y),
                        "Z": str(z),
                        "clipped_abs": str(abs(clipped_product)),
                        "original_abs": str(abs(original_product)),
                    }
                )

    parity_pairs = [
        (Fraction(-2), Fraction(-1)),
        (Fraction(2), Fraction(1)),
        (Fraction(-1), Fraction(-2)),
        (Fraction(1), Fraction(2)),
    ]
    for radius in (Fraction(1), Fraction(2), Fraction(5)):
        shifted = [
            (clip(y, radius) + radius, clip(z, radius) + radius)
            for y, z in parity_pairs
        ]
        mean_y = sum(row[0] for row in shifted) / len(shifted)
        mean_z = sum(row[1] for row in shifted) / len(shifted)
        mean_product = sum(row[0] * row[1] for row in shifted) / len(shifted)
        covariance = mean_product - mean_y * mean_z
        audit.check(
            "parity-symmetric clipped Y mean",
            mean_y == radius,
            mean_y,
            radius,
            "parity_clip",
        )
        audit.check(
            "parity-symmetric clipped Z mean",
            mean_z == radius,
            mean_z,
            radius,
            "parity_clip",
        )
        audit.check(
            "parity-symmetric clipped covariance",
            covariance >= 0,
            covariance,
            ">=0",
            "parity_clip",
        )

    script_path = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-fkg-mixed-derivative-interpolation-audit/0.1",
        "script_version": __version__,
        "result_id": "R-499",
        "exploration_id": "EXP-001583",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "parameters": {
            "lambda": str(lam),
            "kappa": str(kappa),
            "coordinate_fixture_values": [str(value) for value in values],
            "interpolation_mesh_sites": len(x_loop),
            "clip_radii": ["1", "2", "5"],
        },
        "derived": {
            "mixed_derivative_rows": mixed_rows,
            "rectangle_rows": rectangle_rows,
            "interpolation_rows": interpolation_rows,
            "clip_rows": clip_rows,
            "product_rows": product_rows,
            "domination_rows": domination_rows,
        },
        "files": {
            "script": str(script_path.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(script_path),
        },
        "verdict": "PASS",
        "boundary": (
            "Finite mixed-derivative, supermodularity, interpolation and clip "
            "diagnostics only. No KP/Feynman--Kac topology, loop weak-limit, "
            "uniform-integrability theorem, pressure, cusp, phase, DLR, claim "
            "promotion, manuscript or PDF is certified."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-001583 PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
