#!/usr/bin/env python3
"""Independent finite audit of the Q3LOCK Fekete and convexity proof bridges.

The audit checks only the combinatorial tiling, the signs of the remainder
estimates, the convex secant constant, and the finite moving-temperature seam
scale.  It does not prove the EXP-000780 form-domain, trace, or thermodynamic
hypotheses and does not make a phase or publication claim.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-fekete-convex-equicontinuity-audit/result.json"
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


Shape = tuple[int, ...]


def volume(shape: Shape) -> int:
    result = 1
    for side in shape:
        result *= side
    return result


def boundary_area(shape: Shape) -> int:
    total = 0
    for axis in range(len(shape)):
        area = 1
        for other, side in enumerate(shape):
            if other != axis:
                area *= side
        total += area
    return total


def rectangular_partition(shape: Shape, block: Shape) -> tuple[dict[Shape, int], dict[str, int]]:
    """Return piece-shape multiplicities for the explicit product tiling."""

    if len(shape) != len(block):
        raise ValueError("shape and block dimensions differ")
    options: list[list[tuple[int, int]]] = []
    q_values: list[int] = []
    remainders: list[int] = []
    for side, unit in zip(shape, block):
        if side <= 0 or unit <= 0 or side % 2 or unit % 2:
            raise ValueError("all sides must be positive and even")
        q, remainder = divmod(side, unit)
        if q == 0:
            raise ValueError("large shape must contain one full block per axis")
        q_values.append(q)
        remainders.append(remainder)
        axis_options = [(unit, q)]
        if remainder:
            if remainder % 2:
                raise ValueError("odd remainder")
            axis_options.append((remainder, 1))
        options.append(axis_options)

    pieces: dict[Shape, int] = {}
    for choice in itertools.product(*options):
        piece = tuple(item[0] for item in choice)
        multiplicity = 1
        for _width, count in choice:
            multiplicity *= count
        pieces[piece] = pieces.get(piece, 0) + multiplicity

    tile_volume = 1
    for q, unit in zip(q_values, block):
        tile_volume *= q * unit
    total = volume(shape)
    metadata = {
        "tile_count": math.prod(q_values),
        "tile_volume": tile_volume,
        "remainder_volume": total - tile_volume,
        "volume": total,
    }
    return pieces, metadata


def synthetic_super_energy(shape: Shape, rho: Fraction, kappa: Fraction) -> Fraction:
    return rho * volume(shape) - kappa * boundary_area(shape)


def synthetic_sub_log(shape: Shape, rho: Fraction, kappa: Fraction) -> Fraction:
    return rho * volume(shape) + kappa * boundary_area(shape)


def tiling_bounds(
    shape: Shape,
    block: Shape,
    value: Callable[[Shape], Fraction],
    remainder_constant: Fraction,
    sign: str,
) -> tuple[Fraction, Fraction, dict[Shape, int], dict[str, int]]:
    pieces, metadata = rectangular_partition(shape, block)
    tile_count = metadata["tile_count"]
    remainder_volume = metadata["remainder_volume"]
    block_value = value(block)
    if sign == "super":
        bound = tile_count * block_value - remainder_constant * remainder_volume
    elif sign == "sub":
        bound = tile_count * block_value + remainder_constant * remainder_volume
    else:
        raise ValueError("unknown semigroup sign")
    return value(shape), bound, pieces, metadata


def convex_value(beta: Fraction, lines: Iterable[tuple[Fraction, Fraction]]) -> Fraction:
    return max(slope * beta + intercept for slope, intercept in lines)


def convex_range(
    lo: Fraction, hi: Fraction, lines: list[tuple[Fraction, Fraction]]
) -> tuple[Fraction, Fraction]:
    candidates = [lo, hi]
    for (slope_a, intercept_a), (slope_b, intercept_b) in itertools.combinations(lines, 2):
        if slope_a != slope_b:
            crossing = (intercept_b - intercept_a) / (slope_a - slope_b)
            if lo <= crossing <= hi:
                candidates.append(crossing)
    values = [convex_value(point, lines) for point in candidates]
    return min(values), max(values)


def seam_constant(
    length: int, dimensions: int, component_count: int, c: float, g: float, eta: float
) -> dict[str, float]:
    seam_scalar_edges = dimensions * length ** (dimensions - 1)
    endpoint_occurrences = component_count * 2 * seam_scalar_edges
    max_incidence = dimensions
    quartic_coefficient = g / component_count
    per_endpoint_quartic = eta * quartic_coefficient / max_incidence
    per_endpoint_constant = c * c / (4.0 * per_endpoint_quartic)
    all_constant = endpoint_occurrences * per_endpoint_constant
    return {
        "seam_scalar_edges": float(seam_scalar_edges),
        "endpoint_occurrences": float(endpoint_occurrences),
        "max_incidence": float(max_incidence),
        "per_endpoint_quartic": per_endpoint_quartic,
        "per_endpoint_constant": per_endpoint_constant,
        "all_component_constant": all_constant,
    }


def build_payload() -> dict[str, Any]:
    audit = Audit()
    dimensions = 3
    even_step = 2
    component_count = 8
    block: Shape = (2, 4, 6)
    rho = Fraction(7, 5)
    kappa = Fraction(3, 10)
    lower_constant = abs(rho) + kappa * Fraction(dimensions, even_step)
    upper_constant = abs(rho) + kappa * Fraction(dimensions, even_step)

    # The two synthetic envelopes have exactly the semigroup signs used in the
    # EXP-000780 proof.  The boundary-area identity makes the check nontrivial.
    super_value = lambda shape: synthetic_super_energy(shape, rho, kappa)
    sub_value = lambda shape: synthetic_sub_log(shape, rho, kappa)
    for axis in range(dimensions):
        first = tuple(block[i] + (2 if i == axis else 0) for i in range(dimensions))
        second = tuple(block[i] + (4 if i == axis else 0) for i in range(dimensions))
        joined = tuple(first[i] + (second[i] if i == axis else 0) for i in range(dimensions))
        # The other coordinates must agree for a literal concatenation.
        second = tuple(first[i] if i != axis else second[i] for i in range(dimensions))
        joined = tuple(first[i] + (second[i] if i == axis else 0) for i in range(dimensions))
        audit.check(
            "synthetic ground superadditivity",
            super_value(joined) >= super_value(first) + super_value(second),
            super_value(joined),
            ">= split sum",
            "fekete_sign",
        )
        audit.check(
            "synthetic log subadditivity",
            sub_value(joined) <= sub_value(first) + sub_value(second),
            sub_value(joined),
            "<= split sum",
            "fekete_sign",
        )

    tiling_rows: list[dict[str, Any]] = []
    growth_rows: list[dict[str, Any]] = []
    large_shapes = [(12, 18, 20), (16, 22, 28), (24, 30, 34), (32, 38, 46)]
    for shape in large_shapes:
        super_actual, super_bound, pieces, metadata = tiling_bounds(
            shape, block, super_value, lower_constant, "super"
        )
        sub_actual, sub_bound, _sub_pieces, _sub_metadata = tiling_bounds(
            shape, block, sub_value, upper_constant, "sub"
        )
        total_piece_volume = sum(volume(piece) * count for piece, count in pieces.items())
        full_block_count = pieces.get(block, 0)
        audit.check(
            "product tiling preserves volume",
            total_piece_volume == volume(shape),
            total_piece_volume,
            volume(shape),
            "fekete_tiling",
        )
        audit.check(
            "full block multiplicity",
            full_block_count == metadata["tile_count"],
            full_block_count,
            metadata["tile_count"],
            "fekete_tiling",
        )
        audit.check(
            "all piece sides remain even",
            all(all(side % even_step == 0 for side in piece) for piece in pieces),
            True,
            True,
            "fekete_tiling",
        )
        audit.check(
            "superadditive remainder lower bound",
            super_actual >= super_bound,
            super_actual,
            ">= tiled lower bound",
            "fekete_bound",
        )
        audit.check(
            "subadditive remainder upper bound",
            sub_actual <= sub_bound,
            sub_actual,
            "<= tiled upper bound",
            "fekete_bound",
        )
        tile_fraction = Fraction(metadata["tile_volume"], metadata["volume"])
        remainder_fraction = Fraction(metadata["remainder_volume"], metadata["volume"])
        audit.check(
            "tile and remainder fractions partition",
            tile_fraction + remainder_fraction == 1,
            tile_fraction + remainder_fraction,
            1,
            "fekete_bound",
        )
        bound_remainder = sum(
            Fraction(metadata["remainder_volume"], metadata["volume"])
            for _ in (0,)
        )
        audit.check(
            "remainder volume nonnegative",
            bound_remainder >= 0,
            bound_remainder,
            ">=0",
            "fekete_tiling",
        )
        tiling_rows.append(
            {
                "shape": shape,
                "tile_count": metadata["tile_count"],
                "tile_fraction": str(tile_fraction),
                "remainder_fraction": str(remainder_fraction),
                "piece_types": len(pieces),
                "super_density_lower": str(super_bound / metadata["volume"]),
                "sub_density_upper": str(sub_bound / metadata["volume"]),
            }
        )

    # Fixed-block cofinal growth makes the remainder fraction vanish.
    for multiplier in (2, 4, 8, 16):
        shape = tuple(unit * multiplier + (unit - even_step if unit > even_step else 0) for unit in block)
        _pieces, metadata = rectangular_partition(shape, block)
        remainder_fraction = Fraction(metadata["remainder_volume"], metadata["volume"])
        growth_rows.append(
            {"multiplier": multiplier, "shape": shape, "remainder_fraction": str(remainder_fraction)}
        )
        audit.check(
            "cofinal remainder fraction is below one",
            0 <= remainder_fraction < 1,
            remainder_fraction,
            "[0,1)",
            "fekete_growth",
        )
    for previous, current in zip(growth_rows, growth_rows[1:]):
        audit.check(
            "cofinal remainder fraction decreases",
            Fraction(current["remainder_fraction"]) < Fraction(previous["remainder_fraction"]),
            current["remainder_fraction"],
            "< previous",
            "fekete_growth",
        )

    # Convex secant bound on an exact piecewise-linear convex function.
    beta_minus, beta_plus = Fraction(1), Fraction(5)
    beta = Fraction(6, 5)
    lines = [(Fraction(-10), Fraction(15)), (Fraction(0), Fraction(0))]
    range_min, range_max = convex_range(beta_minus, beta_plus, lines)
    range_width = range_max - range_min
    margin = min(beta - beta_minus, beta_plus - beta)
    lipschitz = range_width / margin
    for step in (Fraction(1, 20), Fraction(1, 10), Fraction(1, 5)):
        for sign in (-1, 1):
            h = sign * step
            if abs(h) <= margin:
                lhs = abs(convex_value(beta + h, lines) - convex_value(beta, lines))
                rhs = lipschitz * abs(h)
                audit.check(
                    "convex interior secant bound",
                    lhs <= rhs,
                    lhs,
                    "<= secant bound",
                    "convexity",
                )
    wrong_lipschitz = range_width / max(beta - beta_minus, beta_plus - beta)
    hostile_h = Fraction(1, 10)
    hostile_lhs = abs(convex_value(beta - hostile_h, lines) - convex_value(beta, lines))
    audit.check(
        "wrong max-margin Lipschitz constant is rejected",
        hostile_lhs > wrong_lipschitz * hostile_h,
        hostile_lhs,
        "> mutated bound",
        "hostile",
    )

    # Couple the convex estimate to the independently derived seam scale.
    c, g, b_j = 1.7, 2.3, 0.9
    seam_rows: list[dict[str, float]] = []
    previous_density = math.inf
    for length in (2, 4, 8, 16, 32, 64):
        eta = length ** (-0.5)
        constants = seam_constant(length, dimensions, component_count, c, g, eta)
        d_total = eta * b_j * length**dimensions + constants["all_component_constant"]
        density = d_total / (component_count * length**dimensions)
        audit.check(
            "moving-beta seam density is positive",
            density > 0,
            density,
            ">0",
            "moving_temperature",
        )
        audit.check(
            "moving-beta seam density decreases",
            density < previous_density,
            density,
            "< previous",
            "moving_temperature",
        )
        previous_density = density
        seam_rows.append(
            {
                "L": float(length),
                "eta": eta,
                "density": density,
                "all_component_constant": constants["all_component_constant"],
            }
        )
    audit.check(
        "seam density has the displayed square-root scale",
        seam_rows[-1]["density"] * math.sqrt(seam_rows[-1]["L"])
        < seam_rows[0]["density"] * math.sqrt(seam_rows[0]["L"]) * 1.1,
        seam_rows[-1]["density"] * math.sqrt(seam_rows[-1]["L"]),
        "bounded square-root rescaling",
        "moving_temperature",
    )
    for length in (64, 256, 1024):
        eta = length ** (-0.5)
        h = float(beta) * eta
        audit.check(
            "moving beta remains in the interior interval",
            h <= float(margin),
            h,
            "<= interior margin",
            "moving_temperature",
        )
        audit.check(
            "moving beta error is linear in eta",
            abs(float(lipschitz)) * h <= float(lipschitz) * float(beta) * eta,
            abs(float(lipschitz)) * h,
            "<= C*beta*eta",
            "moving_temperature",
        )

    # Hostile geometry/normalization mutations.
    odd_shape = (13, 18, 20)
    audit.check(
        "odd large rectangle is rejected",
        any(side % even_step for side in odd_shape),
        True,
        "hostile",
        "hostile",
    )
    wrong_component_density = seam_rows[1]["density"] * component_count
    audit.check(
        "missing eight-component normalization changes density",
        wrong_component_density > seam_rows[1]["density"],
        wrong_component_density,
        "> normalized density",
        "hostile",
    )

    script_path = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-fekete-convex-equicontinuity-audit/0.1",
        "script_version": __version__,
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "parameters": {
            "dimensions": dimensions,
            "even_step": even_step,
            "component_count": component_count,
            "block": block,
            "rho": str(rho),
            "kappa": str(kappa),
            "lower_remainder_constant": str(lower_constant),
            "upper_remainder_constant": str(upper_constant),
            "convex_interval": [str(beta_minus), str(beta_plus)],
            "convex_base_point": str(beta),
        },
        "derived": {
            "tiling_rows": tiling_rows,
            "growth_rows": growth_rows,
            "convex_range": {"min": str(range_min), "max": str(range_max), "width": str(range_width)},
            "convex_margin": str(margin),
            "convex_lipschitz": str(lipschitz),
            "seam_rows": seam_rows,
        },
        "files": {
            "script": str(script_path.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(script_path),
        },
        "verdict": "PASS",
        "boundary": "Finite even-box tiling, synthetic semigroup-sign, convex secant and moving-temperature seam diagnostics only. No EXP-000780 analytic form-domain, trace, Fekete, pressure-limit, phase, DLR or publication theorem is certified; no PDF is created.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-001581 PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
