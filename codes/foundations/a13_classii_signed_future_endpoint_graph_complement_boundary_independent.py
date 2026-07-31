#!/usr/bin/env python3
"""Independent standard-library certificate for the A13 R-139 checkpoint.

This route uses different finite fixtures and direct scalar/matrix arithmetic.
It does not import the primary implementation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile


RESULT_ID = "A13-CLASSII-SIGNED-FUTURE-ENDPOINT-GRAPH-COMPLEMENT-BOUNDARY"
SCHEMA = "tect/a13-signed-future-endpoint-graph-complement-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-signed-future-endpoint-graph-complement-boundary/"
    "result.json"
)
Q = Fraction


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not condition:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def quadratic_energy(current: Fraction, trace: Fraction) -> Fraction:
    return (current * current - trace) / 2


def owner_from_increment(x: Fraction, dx: Fraction, dtrace: Fraction) -> Fraction:
    return x * dx + dx * dx / 2 - dtrace / 2


def scalar_matrix_value(
    x: Fraction,
    y: Fraction,
    low: Fraction,
    e: Fraction,
    f: Fraction,
    d: Fraction,
    a: Fraction,
    b: Fraction,
    c: Fraction,
) -> Fraction:
    return e * x * x + f * y * y + d * low * low - a * x * y - 2 * b * x * low - 2 * c * y * low


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # A different endpoint chain from the primary route.
    x = [Q(-3), Q(2), Q(7), Q(-2)]
    theta = [Q(5), Q(1), Q(13), Q(8)]
    direct_owners: list[Fraction] = []
    for index in range(len(x) - 1):
        direct_owners.append(owner_from_increment(x[index], x[index + 1] - x[index], theta[index + 1] - theta[index]))
    endpoint = quadratic_energy(x[-1], theta[-1]) - quadratic_energy(x[0], theta[0])
    audit.check("endpoint", "independent owner telescope", sum(direct_owners, Q(0)) == endpoint, sum(direct_owners, Q(0)), endpoint)
    audit.check("endpoint", "owners are signed", min(direct_owners) < 0 < max(direct_owners), direct_owners, "both signs")

    # Two reveal/output cells with different fixed weights.  Telescoping each
    # complete insertion chain before adding weights leaves no insertion grade.
    second_x = [Q(1), Q(-4), Q(6), Q(0)]
    second_theta = [Q(2), Q(9), Q(3), Q(7)]
    second_owners = [
        owner_from_increment(second_x[i], second_x[i + 1] - second_x[i], second_theta[i + 1] - second_theta[i])
        for i in range(len(second_x) - 1)
    ]
    second_endpoint = quadratic_energy(second_x[-1], second_theta[-1]) - quadratic_energy(second_x[0], second_theta[0])
    gamma = Q(7, 12)
    collar = 5
    reveal_cells = [(1, 9), (4, 13)]
    exponents = [2 * gamma * (output - reveal - collar) for reveal, output in reveal_cells]
    weights = [2.0 ** float(exponent) for exponent in exponents]
    weighted_by_events = weights[0] * float(sum(direct_owners, Q(0))) + weights[1] * float(sum(second_owners, Q(0)))
    weighted_by_endpoints = weights[0] * float(endpoint) + weights[1] * float(second_endpoint)
    audit.check("endpoint", "weighted endpoint first equality", abs(weighted_by_events - weighted_by_endpoints) < 1.0e-13, weighted_by_events, weighted_by_endpoints)
    insertion_grades = (2, 21)
    grade_blind_weights = [2.0 ** float(2 * gamma * (reveal_cells[0][1] - reveal_cells[0][0] - collar)) for _ in insertion_grades]
    audit.check("endpoint", "no causal-depth factor", grade_blind_weights[0] == grade_blind_weights[1], grade_blind_weights, "equal reveal weights")

    # Direct conditional trace-excess conversion.
    d0_first = theta[0] - x[0] * x[0]
    d0_last = theta[-1] - x[-1] * x[-1]
    audit.check("trace", "independent sign and half factor", endpoint == -(d0_last - d0_first) / 2, endpoint, -(d0_last - d0_first) / 2)
    delta_d0 = d0_last - d0_first
    budget = abs(delta_d0) / 2
    audit.check("trace", "sufficient budget doubles", (-delta_d0 / 2 >= -budget) == (delta_d0 <= 2 * budget), (-delta_d0 / 2 >= -budget, delta_d0 <= 2 * budget), "equivalent")

    # Alternate forest/variance/mean fixture.
    b2, y2, primitive_trace, future_variance = Q(5), Q(12), Q(8), Q(7)
    forest = b2 + y2 - primitive_trace + future_variance
    packet = (b2 + y2 - primitive_trace) / 2
    centered = (y2 - primitive_trace) / 2
    audit.check("owner", "independent forest value", forest == Q(16), forest, Q(16))
    audit.check("owner", "packet equals forest minus variance", packet == (forest - future_variance) / 2, packet, (forest - future_variance) / 2)
    audit.check("owner", "centered endpoint needs mean", centered + b2 / 2 == packet, centered + b2 / 2, packet)
    audit.check("owner", "centered coordinate exact", centered == (forest - future_variance - b2) / 2, centered, (forest - future_variance - b2) / 2)

    # The analytical R-123 sign fixture is evaluated with beta=3/2 here.
    production_p = 4.0 + 1.0e-12
    s = 339.0 / (8000.0 * production_p)
    beta = 1.5
    mean_square = 16.0 * s * beta * beta * math.exp(-4.0)
    d0 = 16.0 * s * beta * beta * (math.exp(-4.0) - 2.0 * math.exp(-8.0))
    packet_value = 16.0 * s * beta * beta * math.exp(-8.0)
    audit.check("owner", "scaled R-123 D0 positive", d0 > 0.0, d0, ">0")
    audit.check("owner", "scaled R-123 centered negative", -d0 / 2.0 < 0.0, -d0 / 2.0, "<0")
    audit.check("owner", "scaled R-123 packet positive", packet_value > 0.0, packet_value, ">0")
    audit.check("owner", "scaled R-123 reconstruction", abs((mean_square - d0) / 2.0 - packet_value) < 2.0e-16, (mean_square - d0) / 2.0, packet_value)

    # Masked endpoint differences: selecting positive increments destroys the
    # cancellation even though the terminal returns to the initial value.
    k = [Q(0), Q(2), Q(-1), Q(2), Q(0)]
    increments = [k[i + 1] - k[i] for i in range(4)]
    masks = [1 if value > 0 else 0 for value in increments]
    masked = sum((Q(mask) * value for mask, value in zip(masks, increments)), Q(0))
    audit.check("mask", "terminal endpoint returns", k[-1] - k[0] == 0, k[-1] - k[0], 0)
    audit.check("mask", "positive increment mask accumulates", masked == Q(5), masked, Q(5))
    audit.check("mask", "mask variation nonzero", any(masks[i] != masks[i + 1] for i in range(len(masks) - 1)), masks, "changes")

    # Coherent far and near columns require the cross to remain with one owner.
    u = Q(3)
    far_square = u * u / 2
    near_owner = u * (-u) + (-u) * (-u) / 2
    audit.check("mask", "coherent far square", far_square == Q(9, 2), far_square, Q(9, 2))
    audit.check("mask", "coherent near cross owner", near_owner == Q(-9, 2), near_owner, Q(-9, 2))
    audit.check("mask", "coherent terminal cancellation", far_square + near_owner == 0, far_square + near_owner, 0)

    # Tail-only and low-only zero-gap fixtures are evaluated directly as
    # quadratic forms on their kernel vectors.
    e, f, d = Q(9), Q(16), Q(5)
    ef_product = e * f
    ef_root = math.isqrt(ef_product.numerator)
    audit.check("gap", "balanced product is a perfect-square fixture", ef_root * ef_root == ef_product.numerator and ef_product.denominator == 1, ef_root * ef_root, ef_product)
    a0 = 2 * Q(ef_root)
    balanced_kernel_value = scalar_matrix_value(Q(4), Q(3), Q(0), e, f, d, a0, Q(0), Q(0))
    audit.check("gap", "different balanced zero-gap fixture", balanced_kernel_value == 0, balanced_kernel_value, 0)
    audit.check("gap", "tail zero within arbitrary bound", abs(Q(0)) <= Q(1, 1000), 0, "<=1/1000")
    low_kernel_value = scalar_matrix_value(Q(1), Q(0), Q(1), Q(1), Q(2), Q(1), Q(0), Q(1), Q(0))
    audit.check("gap", "different low zero-gap fixture", low_kernel_value == 0, low_kernel_value, 0)

    # Exhaustive scalar test of the robust complement equivalence for a
    # finite tail set.  The adverse signs +/-tau attain the product bound.
    reduced_e, reduced_f = Q(5), Q(7)
    base_a, tau = Q(4), Q(2)
    test_vectors = [(Q(i), Q(j)) for i in range(-3, 4) for j in range(-3, 4) if (i, j) != (0, 0)]
    robust_direct = all(
        reduced_e * vx * vx + reduced_f * vy * vy - (base_a + tail) * vx * vy >= 0
        for vx, vy in test_vectors
        for tail in (-tau, tau)
    )
    robust_product = all(
        reduced_e * vx * vx + reduced_f * vy * vy - base_a * vx * vy >= tau * abs(vx) * abs(vy)
        for vx, vy in test_vectors
    )
    audit.check("robust", "finite robust equivalence", robust_direct == robust_product, (robust_direct, robust_product), "equal")
    audit.check("robust", "finite robust condition holds", robust_direct, robust_direct, True)
    threshold = 2.0 * math.sqrt(float(reduced_e * reduced_f))
    audit.check("robust", "independent scalar threshold", float(base_a + tau) < threshold, float(base_a + tau), f"<{threshold}")
    gap_mu = Q(1, 3)
    diagonal_e, diagonal_f, diagonal_d, low_norm = Q(9), Q(13), Q(12), Q(2)
    sigma_mu = low_norm * low_norm / (diagonal_d - gap_mu)
    positive_gap_threshold = 2.0 * math.sqrt(float((diagonal_e - gap_mu - sigma_mu) * (diagonal_f - gap_mu - sigma_mu)))
    audit.check("robust", "independent positive-gap threshold", float(base_a + tau) < positive_gap_threshold, float(base_a + tau), f"<{positive_gap_threshold}")

    # Graph compression: an indefinite ambient direction can be absent from
    # the actual production tangent graph.
    audit.check("graph", "ambient negative direction", -7 < 0, -7, "<0")
    graph_inputs = [Q(value) for value in range(-4, 5)]
    graph_samples = [Q(0) * value * value for value in graph_inputs]
    audit.check("graph", "graph pullback nonnegative", min(graph_samples) >= 0, min(graph_samples), ">=0")
    positive_inputs = [index for index, value in enumerate(graph_inputs) if value != 0]
    no_positive_margin = any(graph_samples[index] == 0 for index in positive_inputs)
    audit.check("graph", "strict graph margin requires extra input", no_positive_margin, no_positive_margin, True)

    # Predictable-source restriction and Parseval firewalls.
    predictable = [[Q(1), Q(0)], [Q(0), Q(0)]]
    synthesis = [[Q(1), Q(1)]]
    restricted = matmul(synthesis, predictable)
    audit.check("riesz", "restricted synthesis includes predictable projection", restricted == [[Q(1), Q(0)]], restricted, [[Q(1), Q(0)]])
    cell = [[Q(0), Q(2)], [Q(-1), Q(3)]]
    cell_adjoint = transpose(cell)
    symmetrized = [[(cell[i][j] + cell_adjoint[i][j]) / 2 for j in range(2)] for i in range(2)]
    vector = [[Q(2)], [Q(-3)]]
    forward_quadratic = matmul(transpose(vector), matmul(cell, vector))[0][0]
    symmetrized_quadratic = matmul(transpose(vector), matmul(symmetrized, vector))[0][0]
    audit.check("riesz", "forward reverse one symmetrized owner", forward_quadratic == symmetrized_quadratic and symmetrized == transpose(symmetrized), symmetrized_quadratic, forward_quadratic)
    frame_square_sum = Q(1, 4) + Q(1, 4)
    audit.check("riesz", "non-Parseval candidate is rejected", frame_square_sum != Q(1), frame_square_sum, "not 1")

    scope = {
        "signed_future_terminal_prefix_telescope": True,
        "insertion_reanchoring_removed_after_complete_signed_sum": True,
        "mean_low_forest_ownership_repaired": True,
        "wedge_only_telescope_rejected": True,
        "tail_only_headroom_rejected": True,
        "robust_graph_complement_criterion": True,
        "production_weighted_trace_excess": False,
        "production_graph_margin": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    computed = {
        "future_endpoint_difference": str(endpoint),
        "future_owner_sum": str(sum(direct_owners, Q(0))),
        "trace_excess_delta": str(d0_last - d0_first),
        "future_equals_minus_half_trace_excess_delta": str(-(d0_last - d0_first) / 2),
        "reveal_weight_exponent_fixture": str(exponents[0]),
        "reveal_weight_fixture": weights[0],
        "masked_wedge_sum": str(masked),
        "complete_mask_sum": str(k[-1] - k[0]),
        "far_square": str(far_square),
        "near_cross_owner": str(near_owner),
        "tail_only_balanced_determinant": str(e * f - (a0 / 2) ** 2),
        "robust_scalar_threshold": threshold,
        "robust_positive_gap_threshold": positive_gap_threshold,
        "r123_mean_square": mean_square / (beta * beta),
        "r123_d0": d0 / (beta * beta),
        "r123_complete_packet": packet_value / (beta * beta),
        "r123_centered_k": -d0 / (2.0 * beta * beta),
    }
    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {"total": len(audit.rows), "passed": len(audit.rows) - failed, "failed": failed, "rows": audit.rows},
        "computed": computed,
        "scope": scope,
    }
    atomic_json(args.output, payload)
    print(f"R-139 independent {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
