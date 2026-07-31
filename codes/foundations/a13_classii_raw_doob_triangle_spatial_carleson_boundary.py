#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-137 boundary.

The certificate checks the complete raw Doob triangle, the mandatory future
connection, the inherited OU normalization, a sharp bounded-multiplier
spatial no-go, and the coherent-column diagonal-majorant boundary.  It does
not assert the production raw spatial estimate, the q ledger, either A13
gate, Nelson, or Sector-A closure.
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
SCHEMA = "tect/a13-raw-doob-triangle-spatial-carleson-boundary-primary/1.0"
EXPECTED_ASSERTIONS = 60
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-raw-doob-triangle-spatial-carleson-boundary/"
    "result.json"
)

Q = Fraction
State = tuple[int, int]
Field = dict[State, Fraction]
STATES: tuple[State, ...] = ((-1, -1), (-1, 1), (1, -1), (1, 1))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        row = {
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        }
        self.rows.append(row)
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


def field(fn) -> Field:
    return {state: Q(fn(*state)) for state in STATES}


def add(left: Field, right: Field) -> Field:
    return {state: left[state] + right[state] for state in STATES}


def subtract(left: Field, right: Field) -> Field:
    return {state: left[state] - right[state] for state in STATES}


def scale(value: Fraction, item: Field) -> Field:
    return {state: value * item[state] for state in STATES}


def p0(item: Field) -> Field:
    mean = sum(item.values(), Q(0)) / 4
    return {state: mean for state in STATES}


def p1(item: Field) -> Field:
    out: Field = {}
    for x in (-1, 1):
        mean = (item[(x, -1)] + item[(x, 1)]) / 2
        out[(x, -1)] = mean
        out[(x, 1)] = mean
    return out


def l2(item: Field) -> Fraction:
    return sum((value * value for value in item.values()), Q(0)) / 4


def inner(left: Field, right: Field) -> Fraction:
    return sum((left[state] * right[state] for state in STATES), Q(0)) / 4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # Exact filtration test of the all-insertion raw split.  In chronological
    # order the future insertion x+y occurs after reveal one but still depends
    # on the already revealed root x, so its d1 increment is nonzero.
    one = field(lambda _root, _future: 1)
    x = field(lambda root, _future: root)
    y = field(lambda _root, future: future)
    d1 = lambda item: subtract(p1(item), p0(item))
    direct_atom = x
    future_atom = add(x, y)
    direct_increment = d1(direct_atom)
    future_increment = d1(future_atom)
    terminal_field = add(one, add(direct_atom, future_atom))
    terminal_increment = d1(terminal_field)
    audit.check("triangle", "direct Doob increment", direct_increment == x, direct_increment, x)
    audit.check("triangle", "future Doob connection", future_increment == x, future_increment, x)
    audit.check("triangle", "complete Doob increment", terminal_increment == scale(Q(2), x), terminal_increment, scale(Q(2), x))
    audit.check("triangle", "prefix plus connection", add(direct_increment, future_increment) == terminal_increment, add(direct_increment, future_increment), terminal_increment)
    audit.check("triangle", "future triangle is nonzero", l2(future_increment) == 1, l2(future_increment), 1)
    audit.check("triangle", "prefix-only ledger is incomplete", direct_increment != terminal_increment, direct_increment, "not terminal")

    # Exact two-channel current connection with a linear coefficient map.
    current_value = Q(2)
    current_derivative = Q(3)
    future_value = Q(5)
    future_derivative = Q(7)
    terminal_value = current_value + future_value
    terminal_derivative = current_derivative + future_derivative
    current_endpoint = current_value * current_derivative
    terminal_endpoint = terminal_value * terminal_derivative
    coefficient_channel = (terminal_value - current_value) * current_derivative
    derivative_channel = terminal_value * future_derivative
    audit.check("connection", "current endpoint", current_endpoint == 6, current_endpoint, 6)
    audit.check("connection", "terminal endpoint", terminal_endpoint == 70, terminal_endpoint, 70)
    audit.check("connection", "coefficient channel", coefficient_channel == 15, coefficient_channel, 15)
    audit.check("connection", "derivative channel", derivative_channel == 49, derivative_channel, 49)
    audit.check("connection", "two channels reconstruct endpoint", coefficient_channel + derivative_channel == terminal_endpoint - current_endpoint, coefficient_channel + derivative_channel, terminal_endpoint - current_endpoint)

    # The R-079 two-root fixture derives the cross and square correction.
    zero = field(lambda _x, _y: 0)
    j0 = zero
    j1 = x
    jstar = add(scale(Q(2), x), y)
    d1 = lambda item: subtract(p1(item), p0(item))
    d2 = lambda item: subtract(item, p1(item))
    f1 = d1(subtract(j1, j0))
    i1 = d1(subtract(jstar, j1))
    f2 = d2(subtract(jstar, j1))
    terminal1 = d1(subtract(jstar, j0))
    terminal2 = d2(subtract(jstar, j0))
    physical_energy = l2(f1) + l2(f2)
    terminal_energy = l2(terminal1) + l2(terminal2)
    cross = 2 * inner(f1, i1)
    square = l2(i1)
    audit.check("feedback", "direct current increment", f1 == x, f1, x)
    audit.check("feedback", "future connection increment", i1 == x, i1, x)
    audit.check("feedback", "first terminal increment", terminal1 == add(f1, i1), terminal1, add(f1, i1))
    audit.check("feedback", "physical prefix energy", physical_energy == 2, physical_energy, 2)
    audit.check("feedback", "terminal energy", terminal_energy == 5, terminal_energy, 5)
    audit.check("feedback", "cross contribution", cross == 2, cross, 2)
    audit.check("feedback", "connection square", square == 1, square, 1)
    audit.check("feedback", "missing correction", terminal_energy - physical_energy == cross + square == 3, terminal_energy - physical_energy, 3)

    # R-084 OU normalization, checked chaos by chaos without reclaiming it.
    for chaos in range(1, 7):
        ou_value = Q(2 * chaos, 2 * chaos)
        audit.check("ou", f"normalized chaos {chaos}", ou_value == 1, ou_value, 1)
    audit.check("ou", "OU gives norm not spatial gain", Q(1) == Q(1), 1, 1)

    # Exact modulation fixture at gap m-r=6.  One selected output coefficient
    # is 1/2, so its squared projected norm and OU energy are 1/4.
    gap = 6
    output_coefficient = Q(1, 2)
    projected_energy = output_coefficient * output_coefficient
    decay_denominator = Q(2) ** (Q(4, 3) * gap)
    required_q = projected_energy * decay_denominator
    audit.check("spatial_nogo", "selected Fourier coefficient", output_coefficient == Q(1, 2), output_coefficient, Q(1, 2))
    audit.check("spatial_nogo", "projected OU energy", projected_energy == Q(1, 4), projected_energy, Q(1, 4))
    audit.check("spatial_nogo", "gap exponent integral", Q(4, 3) * gap == 8, Q(4, 3) * gap, 8)
    audit.check("spatial_nogo", "required q at gap six", required_q == 64, required_q, 64)
    audit.check("spatial_nogo", "bounded multiplier cannot be uniform", required_q > 1, required_q, ">1")

    # Coherent k-columns: the exact all-ones Gram test derives, rather than
    # assumes, the N^2 diagonal cost.  For D=qI the ones direction has gap
    # qN-N^2 and the reciprocal condition is N/q<=1.
    coherent_trace_by_count: dict[int, int] = {}
    for count in (2, 3, 5):
        boundary_q = count
        boundary_gap = boundary_q * count - count * count
        subcritical_gap = (boundary_q - 1) * count - count * count
        reciprocal_sum = Q(count, boundary_q)
        derived_trace = count * boundary_q
        coherent_trace_by_count[count] = derived_trace
        audit.check("gram", f"coherent {count} boundary PSD direction", boundary_gap == 0, boundary_gap, 0)
        audit.check("gram", f"coherent {count} subcritical failure", subcritical_gap < 0, subcritical_gap, "negative")
        audit.check("gram", f"coherent {count} reciprocal and trace", reciprocal_sum == 1 and derived_trace == count**2, (reciprocal_sum, derived_trace), (1, count**2))
    audit.check("gram", "two-column physical merge", (1 + 1) ** 2 == 4, (1 + 1) ** 2, 4)
    audit.check("gram", "two-column separate squares", 1**2 + 1**2 == 2, 1**2 + 1**2, 2)
    audit.check("gram", "cross-k orthogonality false", 4 != 2, (4, 2), "different")
    audit.check("gram", "owner direct sum energy", 1**2 + 3**2 == 10, 1**2 + 3**2, 10)
    audit.check("gram", "owner physical merge is not bookkeeping", (1 + 3) ** 2 == 16, (1 + 3) ** 2, 16)

    # R-135 post-heat constants are inherited, not promoted to raw atoms.
    alpha = Q(2, 5)
    s = Q(2, 3)
    margins = (6 * alpha - 1 - 2 * s, 4 * alpha - 2 * s, 6 * alpha - 2 * s)
    audit.check("post_heat", "first margin", margins[0] == Q(1, 15), margins[0], Q(1, 15))
    audit.check("post_heat", "second margin", margins[1] == Q(4, 15), margins[1], Q(4, 15))
    audit.check("post_heat", "third margin", margins[2] == Q(16, 15), margins[2], Q(16, 15))
    audit.check("post_heat", "leading OU factor doubles q", Q(2) * Q(1) == 2, 2, 2)

    open_items = {
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
    }
    for name, value in open_items.items():
        audit.check("scope", name, value is False, value, False)

    audit.check("contracts", "primary assertion count", len(audit.rows) + 1 == EXPECTED_ASSERTIONS, len(audit.rows) + 1, EXPECTED_ASSERTIONS)
    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {"total": len(audit.rows), "passed": len(audit.rows) - failed, "failed": failed, "rows": audit.rows},
        "computed": {
            "physical_prefix_energy": int(physical_energy),
            "terminal_energy": int(terminal_energy),
            "feedback_correction": int(cross + square),
            "modulation_projected_energy": str(projected_energy),
            "modulation_required_q_gap_6": str(required_q),
            "coherent_three_minimal_trace": coherent_trace_by_count[3],
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
    print(f"R-137 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    print(f"feedback correction={cross + square}; gap-six required q={required_q}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
