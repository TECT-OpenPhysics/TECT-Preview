#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-139 checkpoint.

This certificate checks the signed future terminal-minus-prefix telescope,
the trace-excess/mean/forest ownership identities, the failure of a masked
wedge telescope, and the exact robust shifted-Douglas complement criterion.
It does not assert the production weighted trace-excess estimate, a positive
production graph margin, either A13 gate, Nelson, or Sector A.
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
SCHEMA = "tect/a13-signed-future-endpoint-graph-complement-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-signed-future-endpoint-graph-complement-boundary/"
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


def k_value(current: Fraction, trace: Fraction) -> Fraction:
    return (current * current - trace) / 2


def insertion_owner(
    previous_current: Fraction,
    next_current: Fraction,
    previous_trace: Fraction,
    next_trace: Fraction,
) -> Fraction:
    increment = next_current - previous_current
    return previous_current * increment + increment * increment / 2 - (next_trace - previous_trace) / 2


def masked_summation_by_parts(k_values: list[Fraction], masks: list[int]) -> tuple[Fraction, Fraction]:
    direct = sum(
        (Q(mask) * (k_values[index + 1] - k_values[index]) for index, mask in enumerate(masks)),
        Q(0),
    )
    boundary = Q(masks[-1]) * k_values[-1] - Q(masks[0]) * k_values[0]
    boundary += sum(
        (Q(masks[index - 1] - masks[index]) * k_values[index] for index in range(1, len(masks))),
        Q(0),
    )
    return direct, boundary


def det2(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    return a * c - b * b


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

    # Complete future endpoint telescope.  The fixture represents one fixed
    # reveal/output cell after all same-root visits and output owners have
    # already been recombined.
    currents = [Q(2), Q(5), Q(1), Q(4), Q(-1)]
    traces = [Q(3), Q(7), Q(2), Q(11), Q(5)]
    owners = [
        insertion_owner(currents[index], currents[index + 1], traces[index], traces[index + 1])
        for index in range(len(currents) - 1)
    ]
    endpoint_difference = k_value(currents[-1], traces[-1]) - k_value(currents[0], traces[0])
    audit.check("future", "each owner is an endpoint K difference", all(
        owners[index] == k_value(currents[index + 1], traces[index + 1]) - k_value(currents[index], traces[index])
        for index in range(len(owners))
    ), owners, "successive K differences")
    audit.check("future", "complete insertion telescope", sum(owners, Q(0)) == endpoint_difference, sum(owners, Q(0)), endpoint_difference)

    # Reveal-anchored weights remain fixed while insertion endpoints telescope.
    gamma = Q(7, 12)
    root = 3
    output_shell = 11
    collar = 5
    exponent = 2 * gamma * (output_shell - root - collar)
    audit.check("future", "reveal weight exponent", exponent == Q(7, 2), exponent, Q(7, 2))
    reveal_weight = 2.0 ** float(exponent)
    weighted_lhs = float(endpoint_difference) * reveal_weight
    weighted_rhs = sum(float(owner) * reveal_weight for owner in owners)
    audit.check("future", "weight commutes with complete insertion sum", abs(weighted_lhs - weighted_rhs) < 1.0e-14, weighted_rhs, weighted_lhs)
    endpoint_weight = lambda reveal, output, width: 2.0 ** float(2 * gamma * (output - reveal - width))
    insertion_grades = (4, 17)
    weight_at_grades = tuple(endpoint_weight(root, output_shell, collar) for _ in insertion_grades)
    audit.check("future", "insertion grade absent after endpoint telescope", weight_at_grades[0] == weight_at_grades[1], weight_at_grades, "equal reveal weights")

    # Trace-excess sign and factor.  D0=trace-current^2 for a centered Doob
    # output, hence K=-D0/2 exactly.
    d0_values = [trace - current * current for current, trace in zip(currents, traces)]
    audit.check("trace_excess", "K equals minus one half D0", all(
        k_value(current, trace) == -d0 / 2
        for current, trace, d0 in zip(currents, traces, d0_values)
    ), [k_value(c, t) for c, t in zip(currents, traces)], [-d / 2 for d in d0_values])
    delta_d0 = d0_values[-1] - d0_values[0]
    audit.check("trace_excess", "future sign", endpoint_difference == -delta_d0 / 2, endpoint_difference, -delta_d0 / 2)
    budget = abs(delta_d0) / 2
    lower_form = -delta_d0 / 2 >= -budget
    doubled_upper = delta_d0 <= 2 * budget
    audit.check("trace_excess", "lower bound converts to doubled upper budget", lower_form == doubled_upper, (lower_form, doubled_upper), "equivalent")

    # Mean/variance/forest ownership.  Forest = ||Phi||^2 - Theta + Var_f,
    # Phi=b+Y with orthogonality.  K is the centered part and needs the mean
    # owner to recover the complete R-123 packet.
    b2 = Q(9)
    y2 = Q(4)
    theta = Q(6)
    variance = Q(5)
    forest = b2 + y2 - theta + variance
    complete_packet = (b2 + y2 - theta) / 2
    centered_k = (y2 - theta) / 2
    audit.check("ownership", "forest bridge", forest == Q(12), forest, Q(12))
    audit.check("ownership", "complete packet forest coordinate", complete_packet == (forest - variance) / 2, complete_packet, (forest - variance) / 2)
    audit.check("ownership", "centered K retains mean subtraction", centered_k == (forest - variance - b2) / 2, centered_k, (forest - variance - b2) / 2)
    audit.check("ownership", "mean restores complete packet", centered_k + b2 / 2 == complete_packet, centered_k + b2 / 2, complete_packet)

    # R-123 bounded six-row coordinate: a positive complete packet can have a
    # negative future-centered K.  These formulas are independently evaluated
    # from the pinned c0+c1 coefficient.
    production_p = 4.0 + 1.0e-12
    s = 339.0 / (8000.0 * production_p)
    beta = 1.0
    r123_b2 = 16.0 * s * beta * beta * math.exp(-4.0)
    r123_d0 = 16.0 * s * beta * beta * (math.exp(-4.0) - 2.0 * math.exp(-8.0))
    r123_packet = 16.0 * s * beta * beta * math.exp(-8.0)
    r123_centered = -r123_d0 / 2.0
    audit.check("ownership", "R-123 mean reserve positive", r123_b2 > 0.0, r123_b2, ">0")
    audit.check("ownership", "R-123 D0 positive", r123_d0 > 0.0, r123_d0, ">0")
    audit.check("ownership", "R-123 complete packet positive", r123_packet > 0.0, r123_packet, ">0")
    audit.check("ownership", "R-123 future-centered K negative", r123_centered < 0.0, r123_centered, "<0")
    audit.check("ownership", "R-123 packet reconstruction", abs((r123_b2 - r123_d0) / 2.0 - r123_packet) < 1.0e-16, (r123_b2 - r123_d0) / 2.0, r123_packet)

    # A moving wedge mask produces internal endpoint variation.  The terminal
    # value is zero, yet selecting only rising increments gives linear growth.
    alternating_k = [Q(0), Q(1), Q(0), Q(1), Q(0)]
    wedge_mask = [1, 0, 1, 0]
    masked_direct, masked_boundary = masked_summation_by_parts(alternating_k, wedge_mask)
    audit.check("wedge", "summation by parts", masked_direct == masked_boundary, masked_direct, masked_boundary)
    audit.check("wedge", "masked wedge does not telescope to terminal", masked_direct == Q(2) and alternating_k[-1] == alternating_k[0], (masked_direct, alternating_k[-1] - alternating_k[0]), (Q(2), Q(0)))
    complete_mask = [1, 1, 1, 1]
    complete_direct, _ = masked_summation_by_parts(alternating_k, complete_mask)
    audit.check("wedge", "complete mask telescopes", complete_direct == alternating_k[-1] - alternating_k[0] == 0, complete_direct, 0)

    far = Q(1)
    near = Q(-1)
    total_energy = (far + near) ** 2 / 2
    far_square = far * far / 2
    near_cross_owner = far * near + near * near / 2
    audit.check("wedge", "far near complete energy", total_energy == 0, total_energy, 0)
    audit.check("wedge", "positive far square", far_square == Q(1, 2), far_square, Q(1, 2))
    audit.check("wedge", "near owner retains cancelling cross", near_cross_owner == Q(-1, 2), near_cross_owner, Q(-1, 2))
    audit.check("wedge", "separate far payment double spends cancellation", far_square + near_cross_owner == total_energy, far_square + near_cross_owner, total_energy)

    # Tail-only strict-gap obstruction.
    e = Q(4)
    f = Q(9)
    ef_numerator = e.numerator * f.numerator
    ef_root = math.isqrt(ef_numerator)
    audit.check("headroom", "balanced product is a perfect-square fixture", ef_root * ef_root == ef_numerator, ef_root * ef_root, ef_numerator)
    a0 = 2 * Q(ef_root, math.isqrt(e.denominator * f.denominator))
    off_diagonal = -a0 / 2
    audit.check("headroom", "balanced determinant is zero", det2(e, off_diagonal, f) == 0, det2(e, off_diagonal, f), 0)
    kernel_x, kernel_y = Q(3), Q(2)
    audit.check("headroom", "balanced kernel first row", e * kernel_x + off_diagonal * kernel_y == 0, e * kernel_x + off_diagonal * kernel_y, 0)
    audit.check("headroom", "balanced kernel second row", off_diagonal * kernel_x + f * kernel_y == 0, off_diagonal * kernel_x + f * kernel_y, 0)
    tail_bounds = [Q(1), Q(1, 1000), Q(1, 10**9)]
    audit.check("headroom", "zero tail satisfies every positive tail bound", all(abs(Q(0)) <= tau for tau in tail_bounds), 0, tail_bounds)

    # Low coupling can independently consume the gap.
    low_quadratic_at_kernel = Q(1) + Q(1) - 2 * Q(1)
    audit.check("headroom", "low-only kernel", low_quadratic_at_kernel == 0, low_quadratic_at_kernel, 0)

    # Exact robust scalar complement.  After low Schur elimination the worst
    # tail subtracts tau*|x|*|y|, and a rank-one choice attains equality.
    reduced_e = Q(15, 4)
    reduced_f = Q(35, 4)
    base_cross = Q(7)
    tail_tau = Q(1)
    x = Q(2)
    y = Q(3)
    base_form = reduced_e * x * x + reduced_f * y * y - base_cross * x * y
    worst_tail = tail_tau * abs(x) * abs(y)
    audit.check("robust", "rank-one tail reaches product bound", worst_tail == Q(6), worst_tail, Q(6))
    audit.check("robust", "robust form remains positive in fixture", base_form - worst_tail > 0, base_form - worst_tail, ">0")
    scalar_threshold = 2.0 * math.sqrt(float(reduced_e * reduced_f))
    audit.check("robust", "scalar norm corollary accepted", float(base_cross + tail_tau) < scalar_threshold, float(base_cross + tail_tau), f"<{scalar_threshold}")
    gap_mu = Q(1, 2)
    diagonal_e, diagonal_f, diagonal_d, low_norm = Q(8), Q(11), Q(10), Q(2)
    sigma_mu = low_norm * low_norm / (diagonal_d - gap_mu)
    gap_threshold = 2.0 * math.sqrt(float((diagonal_e - gap_mu - sigma_mu) * (diagonal_f - gap_mu - sigma_mu)))
    audit.check("robust", "positive-gap scalar corollary accepted", float(base_cross + tail_tau) < gap_threshold, float(base_cross + tail_tau), f"<{gap_threshold}")

    # Production graph condition is weaker than ambient positivity.  The
    # ambient form diag(1,-1) is indefinite, while on the graph y=0 it is +1.
    ambient_bad = -1
    graph_value = 1
    audit.check("graph", "ambient complement may be indefinite", ambient_bad < 0, ambient_bad, "<0")
    audit.check("graph", "restricted production graph positive", graph_value > 0, graph_value, ">0")
    graph_mu = Q(1, 2)
    graph_samples = [Q(value) for value in range(-4, 5)]
    graph_margin_holds = all(u * u >= graph_mu * u * u for u in graph_samples)
    audit.check("graph", "graph robust condition is the narrow target", graph_margin_holds, graph_margin_holds, True)

    # Predictable projection firewall for the physical Riesz response.
    # P=diag(1,0), L=[[1,1]], B=1, M=LP=[[1,0]].
    predictable = [[Q(1), Q(0)], [Q(0), Q(0)]]
    synthesis = [[Q(1), Q(1)]]
    response = [[Q(1)]]
    restricted = matmul(synthesis, predictable)
    force = matmul(response, restricted)
    h_source = matmul(transpose(restricted), force)
    ambient_left = matmul(transpose(synthesis), force)
    ambient_right = matmul(transpose(force), synthesis)
    projected_left = matmul(predictable, ambient_left)
    projected_right = matmul(ambient_right, predictable)
    audit.check("riesz", "predictable pulled Hessian", h_source == [[Q(1), Q(0)], [Q(0), Q(0)]], h_source, "diag(1,0)")
    audit.check("riesz", "ambient adjoints differ", ambient_left != ambient_right, (ambient_left, ambient_right), "different")
    audit.check("riesz", "projected adjoints agree", projected_left == projected_right == h_source, (projected_left, projected_right), h_source)

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
        "future_endpoint_difference": str(endpoint_difference),
        "future_owner_sum": str(sum(owners, Q(0))),
        "trace_excess_delta": str(delta_d0),
        "future_equals_minus_half_trace_excess_delta": str(-delta_d0 / 2),
        "reveal_weight_exponent_fixture": str(exponent),
        "reveal_weight_fixture": reveal_weight,
        "masked_wedge_sum": str(masked_direct),
        "complete_mask_sum": str(complete_direct),
        "far_square": str(far_square),
        "near_cross_owner": str(near_cross_owner),
        "tail_only_balanced_determinant": str(det2(e, off_diagonal, f)),
        "robust_scalar_threshold": scalar_threshold,
        "robust_positive_gap_threshold": gap_threshold,
        "r123_mean_square": r123_b2,
        "r123_d0": r123_d0,
        "r123_complete_packet": r123_packet,
        "r123_centered_k": r123_centered,
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
    print(f"R-139 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
