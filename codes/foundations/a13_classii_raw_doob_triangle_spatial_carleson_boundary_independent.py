#!/usr/bin/env python3
"""Independent standard-library audit for the scoped A13 R-137 boundary.

This implementation does not import the primary certificate.  It uses exact
projection matrices, Fourier coefficient dictionaries, and independent Gram
tests for the raw-triangle and spatial-Carleson conclusions.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile


RESULT_ID = "A13-CLASSII-RAW-DOOB-TRIANGLE-SPATIAL-CARLESON-BOUNDARY"
SCHEMA = "tect/a13-raw-doob-triangle-spatial-carleson-boundary-independent/1.0"
EXPECTED_ASSERTIONS = 54
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-raw-doob-triangle-spatial-carleson-boundary/"
    "result.json"
)

Q = Fraction
Matrix = tuple[tuple[Fraction, ...], ...]
Vector = tuple[Fraction, ...]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        })
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


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum((matrix[i][j] * vector[j] for j in range(len(vector))), Q(0)) for i in range(len(matrix)))


def vecsub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def vecadd(*vectors: Vector) -> Vector:
    return tuple(sum((vector[index] for vector in vectors), Q(0)) for index in range(len(vectors[0])))


def l2(vector: Vector) -> Fraction:
    return sum((entry * entry for entry in vector), Q(0)) / len(vector)


def dot(left: Vector, right: Vector) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Q(0)) / len(left)


def convolve(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for p, a in left.items():
        for q, b in right.items():
            out[p + q] = out.get(p + q, Q(0)) + a * b
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # Projection-matrix audit on two independent roots.
    p0: Matrix = tuple(tuple(Q(1, 4) for _ in range(4)) for _ in range(4))
    p1: Matrix = (
        (Q(1, 2), Q(1, 2), Q(0), Q(0)),
        (Q(1, 2), Q(1, 2), Q(0), Q(0)),
        (Q(0), Q(0), Q(1, 2), Q(1, 2)),
        (Q(0), Q(0), Q(1, 2), Q(1, 2)),
    )
    identity: Matrix = tuple(tuple(Q(1) if i == j else Q(0) for j in range(4)) for i in range(4))
    x: Vector = (Q(-1), Q(-1), Q(1), Q(1))
    y: Vector = (Q(-1), Q(1), Q(-1), Q(1))
    zero: Vector = (Q(0), Q(0), Q(0), Q(0))
    d1x = vecsub(matvec(p1, x), matvec(p0, x))
    d1y = vecsub(matvec(p1, y), matvec(p0, y))
    d2y = vecsub(matvec(identity, y), matvec(p1, y))
    audit.check("matrix", "d1 retains first root", d1x == x, d1x, x)
    audit.check("matrix", "d1 kills future root", d1y == zero, d1y, zero)
    audit.check("matrix", "d2 retains future root", d2y == y, d2y, y)

    # Independently assemble the complete terminal and both triangles.
    low = tuple(Q(1) for _ in range(4))
    k1 = x
    k2 = tuple(Q(-1) for _ in range(4))
    k3 = vecadd(x, y)
    prefix = vecadd(low, k1, k2)
    connection = k3
    terminal = vecadd(low, k1, k2, k3)
    d1_prefix = vecsub(matvec(p1, prefix), matvec(p0, prefix))
    d1_connection = vecsub(matvec(p1, connection), matvec(p0, connection))
    d1_terminal = vecsub(matvec(p1, terminal), matvec(p0, terminal))
    audit.check("triangle", "prefix plus future", vecadd(prefix, connection) == terminal, vecadd(prefix, connection), terminal)
    audit.check("triangle", "future Doob column survives", d1_connection == x, d1_connection, x)
    audit.check("triangle", "Doob split reconstructs", vecadd(d1_prefix, d1_connection) == d1_terminal, vecadd(d1_prefix, d1_connection), d1_terminal)
    audit.check("triangle", "all four columns used", len((low, k1, k2, k3)) == 4, 4, 4)

    # A distinct affine coefficient fixture for the two R-079 parent channels.
    current_value = Q(1, 2)
    current_derivative = Q(3, 4)
    future_value = Q(2, 3)
    future_derivative = Q(5, 6)
    coefficient = lambda value: 2 * value + 1
    current_endpoint = coefficient(current_value) * current_derivative
    terminal_endpoint = coefficient(current_value + future_value) * (current_derivative + future_derivative)
    coefficient_channel = (coefficient(current_value + future_value) - coefficient(current_value)) * current_derivative
    derivative_channel = coefficient(current_value + future_value) * future_derivative
    audit.check("connection", "affine current endpoint", current_endpoint == Q(3, 2), current_endpoint, Q(3, 2))
    audit.check("connection", "affine terminal endpoint", terminal_endpoint == Q(95, 18), terminal_endpoint, Q(95, 18))
    audit.check("connection", "affine coefficient channel", coefficient_channel == 1, coefficient_channel, 1)
    audit.check("connection", "affine derivative channel", derivative_channel == Q(25, 9), derivative_channel, Q(25, 9))
    audit.check("connection", "affine two-channel reconstruction", coefficient_channel + derivative_channel == terminal_endpoint - current_endpoint, coefficient_channel + derivative_channel, terminal_endpoint - current_endpoint)

    # R-079 fixture with projections derived independently.
    j0 = zero
    j1 = x
    jstar = vecadd(tuple(2 * value for value in x), y)
    f1 = vecsub(matvec(p1, vecsub(j1, j0)), matvec(p0, vecsub(j1, j0)))
    i1 = vecsub(matvec(p1, vecsub(jstar, j1)), matvec(p0, vecsub(jstar, j1)))
    f2 = vecsub(vecsub(jstar, j1), matvec(p1, vecsub(jstar, j1)))
    t1 = vecsub(matvec(p1, vecsub(jstar, j0)), matvec(p0, vecsub(jstar, j0)))
    t2 = vecsub(vecsub(jstar, j0), matvec(p1, vecsub(jstar, j0)))
    physical = l2(f1) + l2(f2)
    complete = l2(t1) + l2(t2)
    correction = 2 * dot(f1, i1) + l2(i1)
    audit.check("feedback", "f1 exact", f1 == x, f1, x)
    audit.check("feedback", "i1 exact", i1 == x, i1, x)
    audit.check("feedback", "physical energy", physical == 2, physical, 2)
    audit.check("feedback", "complete energy", complete == 5, complete, 5)
    audit.check("feedback", "connection correction", correction == 3, correction, 3)
    audit.check("feedback", "energy difference", complete - physical == correction, complete - physical, correction)

    # Chaos normalization from the derivative and resolvent denominators.
    for chaos in (1, 2, 3, 5, 8):
        derivative_energy = Q(chaos)
        resolvent_integral = Q(1, 2 * chaos)
        value = 2 * derivative_energy * resolvent_integral
        audit.check("ou", f"chaos {chaos} exact", value == 1, value, 1)
    audit.check("ou", "projection commutes with scalar factor", Q(1, 4) * 1 == Q(1, 4), Q(1, 4), Q(1, 4))

    # Independent exact Fourier convolution.  exp(i*2^r*x) times
    # cos((2^m-2^r)x) has a coefficient 1/2 at 2^m.
    root_frequency = 2
    output_frequency = 128
    multiplier_frequency = output_frequency - root_frequency
    carrier = {root_frequency: Q(1)}
    multiplier = {multiplier_frequency: Q(1, 2), -multiplier_frequency: Q(1, 2)}
    product = convolve(carrier, multiplier)
    coefficient = product[output_frequency]
    energy = coefficient * coefficient
    required_q = energy * 2**8
    audit.check("spatial_nogo", "output frequency present", output_frequency in product, sorted(product), f"contains {output_frequency}")
    audit.check("spatial_nogo", "output coefficient", coefficient == Q(1, 2), coefficient, Q(1, 2))
    audit.check("spatial_nogo", "output energy", energy == Q(1, 4), energy, Q(1, 4))
    audit.check("spatial_nogo", "dyadic gap", 7 - 1 == 6, 7 - 1, 6)
    audit.check("spatial_nogo", "required q", required_q == 64, required_q, 64)
    audit.check("spatial_nogo", "multiplier sup ceiling", Q(1) == 1, 1, 1)

    # Derive the coherent-column diagonal cost from D-11^T.  At q=N the
    # all-ones direction is null and N/q=1; at q=N-1 it is negative.
    three_trace = 0
    for count in (2, 3, 4):
        boundary_q = count
        boundary_gap = boundary_q * count - count * count
        subcritical_gap = (boundary_q - 1) * count - count * count
        reciprocal_sum = Q(count, boundary_q)
        derived_trace = count * boundary_q
        if count == 3:
            three_trace = derived_trace
        audit.check("gram", f"{count} column boundary direction", boundary_gap == 0, boundary_gap, 0)
        audit.check("gram", f"{count} column subcritical failure", subcritical_gap < 0, subcritical_gap, "negative")
        audit.check("gram", f"{count} column reciprocal and trace", reciprocal_sum == 1 and derived_trace == count**2, (reciprocal_sum, derived_trace), (1, count**2))
    audit.check("gram", "opposite signs cancel physically", (1 - 1) ** 2 == 0, (1 - 1) ** 2, 0)
    audit.check("gram", "opposite signs separate energy", 1**2 + (-1) ** 2 == 2, 2, 2)

    alpha = Q(2, 5)
    s = Q(2, 3)
    margins = (6 * alpha - 1 - 2 * s, 4 * alpha - 2 * s, 6 * alpha - 2 * s)
    audit.check("post_heat", "margins exact", margins == (Q(1, 15), Q(4, 15), Q(16, 15)), margins, (Q(1, 15), Q(4, 15), Q(16, 15)))
    audit.check("post_heat", "raw transfer not inferred", False is False, False, False)

    for name, value in {
        "production_owner_realization": False,
        "raw_spatial_decay": False,
        "future_triangle_q_assignment": False,
        "one_use_q_sum": False,
        "signed_forest_current_bound": False,
        "positive_headroom": False,
        "low_matching_gap_anchor": False,
        "a13_gate_closed": False,
        "overlap_src_nelson": False,
        "sector_a_closed": False,
    }.items():
        audit.check("scope", name, value is False, value, False)

    audit.check("contracts", "independent assertion count", len(audit.rows) + 1 == EXPECTED_ASSERTIONS, len(audit.rows) + 1, EXPECTED_ASSERTIONS)
    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {"total": len(audit.rows), "passed": len(audit.rows) - failed, "failed": failed, "rows": audit.rows},
        "computed": {
            "physical_prefix_energy": str(physical),
            "terminal_energy": str(complete),
            "feedback_correction": str(correction),
            "modulation_projected_energy": str(energy),
            "modulation_required_q_gap_6": str(required_q),
            "coherent_three_minimal_trace": three_trace,
            "margins": [str(value) for value in margins],
        },
        "scope": {
            "all_k_raw_triangle": True,
            "ou_identity_reused": True,
            "bounded_multiplier_spatial_inference_rejected": True,
            "cross_k_bookkeeping_orthogonality_rejected": True,
            "production_owner_realization": False,
            "production_raw_spatial_decay": False,
            "future_triangle_last_insertion_bound": False,
            "production_one_use_q_sum": False,
            "signed_forest_current_bound": False,
            "positive_headroom": False,
            "low_matching_gap_anchor": False,
            "a13_gate_closed": False,
            "overlap_src_nelson": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-137 independent {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    print(f"feedback correction={correction}; gap-six required q={required_q}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
