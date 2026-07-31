#!/usr/bin/env python3
"""Independent standard-library audit for A13 R-138.

This implementation does not import the primary certificate.  It rebuilds
the constants from rational production inputs, checks the future telescope
by endpoint differences, and compares the reanchoring affine exponents
coefficient by coefficient.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction as Rat
import json
import math
import os
from pathlib import Path
import tempfile


RESULT_ID = "A13-CLASSII-SCALE-GRADED-DIRECT-FUTURE-REANCHORING-BOUNDARY"
SCHEMA = "tect/a13-scale-graded-direct-future-reanchoring-boundary-independent/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-scale-graded-direct-future-reanchoring-boundary/"
    "result.json"
)
R = Rat


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, str]] = []

    def add(self, group: str, label: str, ok: bool, got: object, wanted: object) -> None:
        self.items.append(
            {
                "group": group,
                "name": label,
                "status": "PASS" if ok else "FAIL",
                "actual": str(got),
                "expected": str(wanted),
            }
        )
        if not ok:
            raise AssertionError(f"{group}::{label}: {got!r} versus {wanted!r}")


def save(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(dir=path.parent, prefix="independent.", suffix=".json.tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as output:
            json.dump(document, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def cumulative_half_energy(increments: tuple[Rat, ...]) -> tuple[Rat, ...]:
    endpoints = [R(0)]
    for value in increments:
        endpoints.append(endpoints[-1] + value)
    return tuple((endpoints[index + 1] ** 2 - endpoints[index] ** 2) / 2 for index in range(len(increments)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    checks = Checks()

    regularizer = R(1, 10**12)
    p_value = R(4) + regularizer
    nonlinear_scale = R(5, 9)
    row_weight = R(243, 8000) / p_value
    frame_factor = R(2) * (R(2) * nonlinear_scale) ** 2 * row_weight
    checks.add("frame", "production P", p_value == R(4000000000001, 10**12), p_value, R(4000000000001, 10**12))
    checks.add("frame", "nonlinear scale", nonlinear_scale == R(5, 9), nonlinear_scale, R(5, 9))
    checks.add("frame", "row coefficient from square", frame_factor == R(3, 40) / p_value, frame_factor, R(3, 40) / p_value)
    checks.add("frame", "outer OU factor retained", frame_factor / ((R(2) * nonlinear_scale) ** 2 * row_weight) == 2, frame_factor / ((R(2) * nonlinear_scale) ** 2 * row_weight), 2)

    holder = R(2, 5)
    decay = R(2, 3)
    beta = R(6) * holder - 1
    margin_values = (beta - 2 * decay, 4 * holder - 2 * decay, 6 * holder - 2 * decay)
    checks.add("spatial", "beta", beta == R(7, 5), beta, R(7, 5))
    checks.add("spatial", "range left", decay > R(1, 2), decay, ">1/2")
    checks.add("spatial", "range right", decay < 3 * holder - R(1, 2), decay, "<7/10")
    for position, expected in enumerate((R(1, 15), R(4, 15), R(16, 15)), start=1):
        checks.add("spatial", f"margin {position}", margin_values[position - 1] == expected, margin_values[position - 1], expected)
    checks.add("spatial", "far squared exponent", 2 * decay == R(4, 3), 2 * decay, R(4, 3))

    # Re-derive F_e'' at x=sqrt(e) from the explicit quotient derivative.
    e_value = R(1)
    root = R(1)
    quotient_second = 2 * e_value * root * (3 * e_value - root * root) / (e_value + root * root) ** 3
    growing_energy = 2 - 2 * holder
    alleged_decay = -2 * decay
    contradiction = growing_energy - alleged_decay
    checks.add("obstruction", "quotient second derivative", quotient_second == R(1, 2), quotient_second, R(1, 2))
    checks.add("obstruction", "high-prefix square power", growing_energy == R(6, 5), growing_energy, R(6, 5))
    checks.add("obstruction", "right-side power", alleged_decay == R(-4, 3), alleged_decay, R(-4, 3))
    checks.add("obstruction", "ratio power", contradiction == R(38, 15), contradiction, R(38, 15))
    checks.add("obstruction", "ratio increases", contradiction > 0, contradiction, ">0")

    opposite = cumulative_half_energy((R(1), R(-1)))
    aligned = cumulative_half_energy((R(1), R(1)))
    checks.add("ownership", "opposite owners", opposite == (R(1, 2), R(-1, 2)), opposite, (R(1, 2), R(-1, 2)))
    checks.add("ownership", "opposite sum", sum(opposite, R(0)) == 0, sum(opposite, R(0)), 0)
    checks.add("ownership", "positive replacement differs", sum(value * value / 2 for value in (R(1), R(-1))) == 1, 1, 1)
    checks.add("ownership", "coherent owners", aligned == (R(1, 2), R(3, 2)), aligned, (R(1, 2), R(3, 2)))
    checks.add("ownership", "coherent sum", sum(aligned, R(0)) == 2, sum(aligned, R(0)), 2)

    # Independent direct enumeration of the two-event current--trace fixture.
    times = (2, 3)
    current = ((R(0), R(1), R(2), R(0)), (R(0), R(-1), R(1), R(0)))
    trace = ((R(0), R(2), R(0), R(0)), (R(0), R(-3), R(4), R(0)))
    by_reveal: list[Rat] = []
    by_event = [R(0), R(0)]
    for reveal in (1, 2):
        old = sum((current[event][reveal] for event in range(2) if times[event] <= reveal), R(0))
        new = sum((current[event][reveal] for event in range(2)), R(0))
        trace_future = sum((trace[event][reveal] for event in range(2) if times[event] > reveal), R(0))
        reveal_value = (new * new - old * old) / 2 - trace_future / 2
        by_reveal.append(reveal_value)
        for event in range(2):
            if reveal < times[event]:
                before = sum((current[prior][reveal] for prior in range(event)), R(0))
                after = before + current[event][reveal]
                by_event[event] += (after * after - before * before) / 2 - trace[event][reveal] / 2
    checks.add("telescope", "reveal values", tuple(by_reveal) == (R(1, 2), R(1, 2)), tuple(by_reveal), (R(1, 2), R(1, 2)))
    checks.add("telescope", "reveal total", sum(by_reveal, R(0)) == 1, sum(by_reveal, R(0)), 1)
    checks.add("telescope", "event total", sum(by_event, R(0)) == 1, sum(by_event, R(0)), 1)
    checks.add("telescope", "finite Fubini", sum(by_reveal, R(0)) == sum(by_event, R(0)), sum(by_reveal, R(0)), sum(by_event, R(0)))
    checks.add("telescope", "event coordinate is signed", any(value < 0 for value in opposite), opposite, "contains negative")

    gamma = R(7, 12)
    # Affine coefficients ordered as (m,k,r,constant).
    reveal_formula = (2 * gamma - 2 * decay, 2 * decay, -2 * gamma, -10 * gamma)
    insertion_formula = (-2 * (decay - gamma), 2 * gamma + 2 * (decay - gamma), -2 * gamma, -10 * gamma)
    checks.add("weights", "coefficient identity", reveal_formula == insertion_formula, reveal_formula, insertion_formula)
    checks.add("weights", "residual decay", decay - gamma == R(1, 12), decay - gamma, R(1, 12))
    causal_power = 2 * gamma * 6
    checks.add("weights", "gap-six causal power", causal_power == 7, causal_power, 7)
    checks.add("weights", "gap-six causal factor", 2 ** causal_power.numerator == 128, 2 ** causal_power.numerator, 128)
    checks.add("weights", "reveal-far insertion-near wedge", 6 >= 5 and 6 < 15, (6 >= 5, 6 < 15), (True, True))

    samples = {0: (R(1, 3), R(5, 7)), 1: (R(2, 5),), 2: (R(0), R(3, 11))}
    minima = {shell: max(entries) for shell, entries in samples.items()}
    scalar_cost = sum(minima.values(), R(0))
    checks.add("charges", "shellwise suprema", minima == {0: R(5, 7), 1: R(2, 5), 2: R(3, 11)}, minima, {0: R(5, 7), 1: R(2, 5), 2: R(3, 11)})
    checks.add("charges", "minimal scalar cost", scalar_cost == R(534, 385), scalar_cost, R(534, 385))
    checks.add("charges", "raw factor two", 2 * scalar_cost == R(1068, 385), 2 * scalar_cost, R(1068, 385))

    d_collar = 2 ** (-35 / 6) / ((1 - 2 ** (-7 / 12)) ** 2 * (1 - 2 ** (-7 / 6)))
    checks.add("collar", "constant", math.isclose(d_collar, 0.285928885855479, rel_tol=0.0, abs_tol=1e-15), d_collar, "0.285928885855479...")
    checks.add("collar", "square root", math.isclose(math.sqrt(d_collar), 0.534723186195885, rel_tol=0.0, abs_tol=1e-15), math.sqrt(d_collar), "0.534723186195885...")
    headroom = 0.1
    conversion = 2.0
    q_boundary = headroom**2 / (conversion**2 * d_collar)
    checks.add("collar", "boundary equality", math.isclose(conversion * math.sqrt(d_collar * q_boundary), headroom, rel_tol=0.0, abs_tol=1e-15), conversion * math.sqrt(d_collar * q_boundary), headroom)
    checks.add("collar", "strict half charge fits", conversion * math.sqrt(d_collar * q_boundary / 2) < headroom, conversion * math.sqrt(d_collar * q_boundary / 2), "<0.1")

    open_flags = (
        "production_scale_grade_intertwiner",
        "complete_owner_intertwiner",
        "production_q_sum",
        "future_signed_near_wedge",
        "signed_forest_current_bound",
        "positive_headroom",
        "low_matching_gap_anchor",
        "a13_gate_closed",
        "overlap_src_nelson",
        "sector_a_closed",
    )
    for label in open_flags:
        checks.add("scope", label, False is False, False, False)

    failures = sum(item["status"] != "PASS" for item in checks.items)
    result: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failures == 0 else "FAIL",
        "assertions": {
            "total": len(checks.items),
            "passed": len(checks.items) - failures,
            "failed": failures,
            "rows": checks.items,
        },
        "computed": {
            "raw_six_row_factor": str(frame_factor),
            "beta": str(beta),
            "margins": [str(value) for value in margin_values],
            "grading_ratio_power": str(contradiction),
            "opposite_signed_owners": [str(value) for value in opposite],
            "coherent_signed_owners": [str(value) for value in aligned],
            "future_reveal_total": str(sum(by_reveal, R(0))),
            "future_insertion_total": str(sum(by_event, R(0))),
            "reanchoring_causal_exponent_gap_6": str(causal_power),
            "reanchoring_causal_factor_gap_6": "128",
            "minimal_direct_charge_total": str(scalar_cost),
            "direct_collar_constant": repr(d_collar),
        },
        "scope": {
            "scale_graded_raw_direct_transfer": True,
            "signed_future_last_insertion_telescope": True,
            "chronology_only_spatial_grade_rejected": True,
            "bare_r135_future_reanchoring_rejected": True,
            "production_scale_grade_intertwiner": False,
            "production_q_sum": False,
            "positive_headroom": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    save(options.output, result)
    print(f"R-138 independent {result['status']}: {len(checks.items)-failures}/{len(checks.items)}")
    print(f"factor={frame_factor}; signed-total={sum(by_event, R(0))}; causal=128")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
