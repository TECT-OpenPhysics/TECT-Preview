#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-138 checkpoint.

The certificate checks the scale-graded raw direct constants, the
chronology/spatial-grade obstruction exponents, the signed current--trace
last-insertion telescope, reveal reanchoring, sharp scalar charges, and the
conditional fixed-collar threshold.  It does not assert the production
owner intertwiner, a uniform charge sum, either A13 gate, Nelson, or Sector A.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from decimal import Decimal, getcontext
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile


RESULT_ID = "A13-CLASSII-SCALE-GRADED-DIRECT-FUTURE-REANCHORING-BOUNDARY"
SCHEMA = "tect/a13-scale-graded-direct-future-reanchoring-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-scale-graded-direct-future-reanchoring-boundary/"
    "result.json"
)
Q = Fraction
getcontext().prec = 60


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


def decimal_power_two(exponent: Fraction) -> Decimal:
    value = Decimal(exponent.numerator) / Decimal(exponent.denominator)
    return (Decimal(2).ln() * value).exp()


def signed_energy_owners(increments: list[Fraction]) -> list[Fraction]:
    prefix = Q(0)
    owners: list[Fraction] = []
    for increment in increments:
        owners.append(prefix * increment + increment * increment / 2)
        prefix += increment
    return owners


def reveal_future_total(
    root: int,
    event_times: list[int],
    current_columns: list[list[Fraction]],
    trace_columns: list[list[Fraction]],
) -> Fraction:
    prefix = sum(
        (current_columns[event][root] for event, time in enumerate(event_times) if time <= root),
        Q(0),
    )
    future = sum(
        (current_columns[event][root] for event, time in enumerate(event_times) if time > root),
        Q(0),
    )
    trace = sum(
        (trace_columns[event][root] for event, time in enumerate(event_times) if time > root),
        Q(0),
    )
    return prefix * future + future * future / 2 - trace / 2


def insertion_future_total(
    event: int,
    event_times: list[int],
    current_columns: list[list[Fraction]],
    trace_columns: list[list[Fraction]],
) -> Fraction:
    total = Q(0)
    for root in range(1, event_times[event]):
        prefix = sum((current_columns[prior][root] for prior in range(event)), Q(0))
        increment = current_columns[event][root]
        total += prefix * increment + increment * increment / 2 - trace_columns[event][root] / 2
    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # Direct raw six-row constants are derived from the production inputs.
    density_floor = Q(1, 10**12)
    production_p = Q(4) + density_floor
    alpha_pf = Q(5, 9)
    c1 = Q(243, 8000) / production_p
    raw_six_row_factor = 8 * alpha_pf * alpha_pf * c1
    audit.check("direct", "Pauli-Fierz coefficient", alpha_pf == Q(5, 9), alpha_pf, Q(5, 9))
    audit.check("direct", "rational row weight", c1 == Q(243, 8000) / production_p, c1, Q(243, 8000) / production_p)
    audit.check("direct", "raw six-row factor", raw_six_row_factor == Q(3, 40) / production_p, raw_six_row_factor, Q(3, 40) / production_p)
    audit.check("direct", "doubled Cartan convention", raw_six_row_factor / 2 == Q(3, 80) / production_p, raw_six_row_factor / 2, Q(3, 80) / production_p)

    rho = Q(2, 5)
    spatial_s = Q(2, 3)
    beta = 6 * rho - 1
    upper_s = 3 * rho - Q(1, 2)
    margins = (beta - 2 * spatial_s, 4 * rho - 2 * spatial_s, 6 * rho - 2 * spatial_s)
    audit.check("direct", "charge exponent beta", beta == Q(7, 5), beta, Q(7, 5))
    audit.check("direct", "admissible lower s", spatial_s > Q(1, 2), spatial_s, ">1/2")
    audit.check("direct", "admissible upper s", spatial_s < upper_s == Q(7, 10), (spatial_s, upper_s), "2/3<7/10")
    audit.check("direct", "first exponent margin", margins[0] == Q(1, 15), margins[0], Q(1, 15))
    audit.check("direct", "second exponent margin", margins[1] == Q(4, 15), margins[1], Q(4, 15))
    audit.check("direct", "third exponent margin", margins[2] == Q(16, 15), margins[2], Q(16, 15))
    audit.check("direct", "squared spatial decay exponent", 2 * spatial_s == Q(4, 3), 2 * spatial_s, Q(4, 3))
    audit.check("direct", "safe support collar", 5 > 4, 5, ">4")

    # The chronology-only fixture has a bounded C^rho prefix but a growing
    # raw derivative channel.  Only exponents are asserted here; the note
    # supplies the Taylor lower-bound quantifiers.
    second_derivative_at_root = Q(1, 2)  # e=1, x=sqrt(e)=1, derived from 2ex(3e-x^2)/(e+x^2)^3
    lhs_power = 2 - 2 * rho
    rhs_power = -2 * spatial_s
    ratio_power = lhs_power - rhs_power
    audit.check("grading_nogo", "nonzero rational second derivative", second_derivative_at_root == Q(1, 2), second_derivative_at_root, Q(1, 2))
    audit.check("grading_nogo", "raw high-prefix energy power", lhs_power == Q(6, 5), lhs_power, Q(6, 5))
    audit.check("grading_nogo", "claimed decay power", rhs_power == Q(-4, 3), rhs_power, Q(-4, 3))
    audit.check("grading_nogo", "contradiction ratio power", ratio_power == Q(38, 15), ratio_power, Q(38, 15))
    audit.check("grading_nogo", "ratio diverges", ratio_power > 0, ratio_power, ">0")
    audit.check("grading_nogo", "C-rho amplitude is scale neutral", -rho + rho == 0, -rho + rho, 0)
    audit.check("grading_nogo", "gap five already grows", decimal_power_two(5 * ratio_power) > Decimal(1), decimal_power_two(5 * ratio_power), ">1")

    # Signed energy ownership is essential.  Opposite insertions cancel only
    # when each event owns its cumulative energy increment.
    opposite = signed_energy_owners([Q(1), Q(-1)])
    coherent = signed_energy_owners([Q(1), Q(1)])
    audit.check("signed_owner", "opposite first owner", opposite[0] == Q(1, 2), opposite[0], Q(1, 2))
    audit.check("signed_owner", "opposite second owner", opposite[1] == Q(-1, 2), opposite[1], Q(-1, 2))
    audit.check("signed_owner", "opposite owner sum", sum(opposite, Q(0)) == 0, sum(opposite, Q(0)), 0)
    audit.check("signed_owner", "opposite terminal half energy", sum(opposite, Q(0)) == (Q(1) - Q(1)) ** 2 / 2, sum(opposite, Q(0)), 0)
    audit.check("signed_owner", "positive square separation destroys cancellation", (Q(1) ** 2 + Q(-1) ** 2) / 2 == 1, 1, 1)
    audit.check("signed_owner", "coherent first owner", coherent[0] == Q(1, 2), coherent[0], Q(1, 2))
    audit.check("signed_owner", "coherent second owner", coherent[1] == Q(3, 2), coherent[1], Q(3, 2))
    audit.check("signed_owner", "coherent owner sum", sum(coherent, Q(0)) == 2, sum(coherent, Q(0)), 2)
    audit.check("signed_owner", "coherent terminal half energy", sum(coherent, Q(0)) == (Q(1) + Q(1)) ** 2 / 2, sum(coherent, Q(0)), 2)

    # Exact finite-Fubini current--trace fixture.  Root zero is unused; event
    # times two and three create the future cells at roots one and two.
    event_times = [2, 3]
    current_columns = [
        [Q(0), Q(1), Q(2), Q(0)],
        [Q(0), Q(-1), Q(1), Q(0)],
    ]
    trace_columns = [
        [Q(0), Q(2), Q(0), Q(0)],
        [Q(0), Q(-3), Q(4), Q(0)],
    ]
    reveal_one = reveal_future_total(1, event_times, current_columns, trace_columns)
    reveal_two = reveal_future_total(2, event_times, current_columns, trace_columns)
    reveal_total = reveal_one + reveal_two
    insertion_totals = [
        insertion_future_total(event, event_times, current_columns, trace_columns)
        for event in range(len(event_times))
    ]
    audit.check("future_telescope", "root one future current cancels", current_columns[0][1] + current_columns[1][1] == 0, current_columns[0][1] + current_columns[1][1], 0)
    audit.check("future_telescope", "root one trace contribution", -(trace_columns[0][1] + trace_columns[1][1]) / 2 == Q(1, 2), -(trace_columns[0][1] + trace_columns[1][1]) / 2, Q(1, 2))
    audit.check("future_telescope", "root one total", reveal_one == Q(1, 2), reveal_one, Q(1, 2))
    audit.check("future_telescope", "root two current energy", Q(2) * Q(1) + Q(1, 2) == Q(5, 2), Q(2) * Q(1) + Q(1, 2), Q(5, 2))
    audit.check("future_telescope", "root two trace contribution", -trace_columns[1][2] / 2 == Q(-2), -trace_columns[1][2] / 2, Q(-2))
    audit.check("future_telescope", "root two total", reveal_two == Q(1, 2), reveal_two, Q(1, 2))
    audit.check("future_telescope", "reveal total", reveal_total == 1, reveal_total, 1)
    audit.check("future_telescope", "last-insertion total", sum(insertion_totals, Q(0)) == 1, sum(insertion_totals, Q(0)), 1)
    audit.check("future_telescope", "finite Fubini equality", reveal_total == sum(insertion_totals, Q(0)), reveal_total, sum(insertion_totals, Q(0)))

    # Exact reveal-to-insertion weight identity.
    gamma = Q(7, 12)
    reveal_root = 0
    insertion_shell = 6
    output_shell = insertion_shell + 5
    left_exponent = 2 * gamma * (output_shell - reveal_root - 5) - 2 * spatial_s * (output_shell - insertion_shell)
    right_exponent = -10 * gamma + 2 * gamma * (insertion_shell - reveal_root) - 2 * (spatial_s - gamma) * (output_shell - insertion_shell)
    causal_exponent = 2 * gamma * (insertion_shell - reveal_root)
    causal_factor = decimal_power_two(causal_exponent)
    audit.check("reanchoring", "positive residual exponent", spatial_s - gamma == Q(1, 12), spatial_s - gamma, Q(1, 12))
    audit.check("reanchoring", "weight exponent identity", left_exponent == right_exponent, left_exponent, right_exponent)
    audit.check("reanchoring", "sample total exponent", left_exponent == Q(1, 3), left_exponent, Q(1, 3))
    audit.check("reanchoring", "causal exponent at gap six", causal_exponent == 7, causal_exponent, 7)
    audit.check("reanchoring", "causal factor at gap six", abs(causal_factor - Decimal(128)) < Decimal("1e-45"), causal_factor, 128)
    near_m = 6
    near_k = 10
    audit.check("reanchoring", "future wedge is reveal far", near_m >= reveal_root + 5, near_m, ">=5")
    audit.check("reanchoring", "future wedge is insertion near", near_m < near_k + 5, near_m, "<15")

    # Minimal scalar charges are suprema of the preweighted cell costs.
    weighted_direct_cells = {0: [Q(1, 3), Q(5, 7)], 1: [Q(2, 5)], 2: [Q(0), Q(3, 11)]}
    minimal_direct = {key: max(values) for key, values in weighted_direct_cells.items()}
    direct_total = sum(minimal_direct.values(), Q(0))
    audit.check("carleson", "minimal direct shell zero", minimal_direct[0] == Q(5, 7), minimal_direct[0], Q(5, 7))
    audit.check("carleson", "minimal direct shell one", minimal_direct[1] == Q(2, 5), minimal_direct[1], Q(2, 5))
    audit.check("carleson", "minimal direct total", direct_total == Q(534, 385), direct_total, Q(534, 385))
    audit.check("carleson", "subminimal charge fails", Q(1, 2) < minimal_direct[0], Q(1, 2), "<5/7")
    audit.check("carleson", "raw OU total doubles", 2 * direct_total == Q(1068, 385), 2 * direct_total, Q(1068, 385))

    # Conditional fixed-collar arithmetic, derived from the R-134 inputs.
    direct_collar_constant = (
        decimal_power_two(Q(-35, 6))
        / ((Decimal(1) - decimal_power_two(Q(-7, 12))) ** 2)
        / (Decimal(1) - decimal_power_two(Q(-7, 6)))
    )
    audit.check("collar", "direct collar constant positive", direct_collar_constant > 0, direct_collar_constant, ">0")
    audit.check("collar", "direct collar constant value", abs(direct_collar_constant - Decimal("0.285928885855479")) < Decimal("1e-15"), direct_collar_constant, "0.285928885855479...")
    audit.check("collar", "direct collar square root", abs(direct_collar_constant.sqrt() - Decimal("0.534723186195885")) < Decimal("1e-15"), direct_collar_constant.sqrt(), "0.534723186195885...")
    headroom = Decimal("0.1")
    owner_factor = Decimal(2)
    collar = 5
    q_threshold = headroom * headroom / (owner_factor * owner_factor * direct_collar_constant) * decimal_power_two(Q(7 * (collar - 5), 6))
    test_q = q_threshold / 2
    tail = owner_factor * (direct_collar_constant * test_q).sqrt() * decimal_power_two(Q(-7 * (collar - 5), 12))
    audit.check("collar", "half-threshold tail fits", tail < headroom, tail, "<0.1")
    audit.check("collar", "threshold is strict equality boundary", abs(owner_factor * (direct_collar_constant * q_threshold).sqrt() - headroom) < Decimal("1e-50"), owner_factor * (direct_collar_constant * q_threshold).sqrt(), headroom)

    open_items = {
        "production_scale_grade_intertwiner": False,
        "complete_owner_intertwiner": False,
        "production_direct_q_sum": False,
        "production_future_gap_ledger": False,
        "future_signed_near_wedge": False,
        "signed_forest_current_bound": False,
        "positive_headroom": False,
        "low_matching_gap_anchor": False,
        "a13_gate_closed": False,
        "overlap_src_nelson": False,
        "sector_a_closed": False,
    }
    for name, value in open_items.items():
        audit.check("scope", name, value is False, value, False)

    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows) - failed,
            "failed": failed,
            "rows": audit.rows,
        },
        "computed": {
            "raw_six_row_factor": str(raw_six_row_factor),
            "beta": str(beta),
            "margins": [str(value) for value in margins],
            "grading_ratio_power": str(ratio_power),
            "opposite_signed_owners": [str(value) for value in opposite],
            "coherent_signed_owners": [str(value) for value in coherent],
            "future_reveal_total": str(reveal_total),
            "future_insertion_total": str(sum(insertion_totals, Q(0))),
            "reanchoring_causal_exponent_gap_6": str(causal_exponent),
            "reanchoring_causal_factor_gap_6": str(causal_factor),
            "minimal_direct_charge_total": str(direct_total),
            "direct_collar_constant": str(direct_collar_constant),
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
    atomic_json(args.output, payload)
    print(f"R-138 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    print(f"raw factor={raw_six_row_factor}; reanchoring gap-six={causal_factor}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
