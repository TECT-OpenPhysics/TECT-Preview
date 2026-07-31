#!/usr/bin/env python3
"""Primary exact certificate for the scoped A13 R-136 boundary.

This executable distinguishes current-root Doob centring from future-owner
centring, proves the common-heat two-replica variance identities on exact
finite models, checks the raw sequential telescope and owner-by-reveal
accounting, and records the production-graph Taylor boundary.  It does not
assert the production raw-current spatial estimate, the one-use q ledger,
either A13 gate, Nelson, or Sector-A closure.
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
from typing import Callable, Iterable, TypeVar


RESULT_ID = "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY"
SCHEMA = "tect/a13-common-heat-replica-raw-sequential-owner-boundary-primary/1.0"
EXPECTED_ASSERTIONS = 71
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-common-heat-replica-raw-sequential-owner-boundary/"
    "result.json"
)

State = tuple[int, int]
ScalarField = dict[State, Fraction]
VectorField = dict[State, tuple[Fraction, ...]]
T = TypeVar("T")

STATES: tuple[State, ...] = ((-1, -1), (-1, 1), (1, -1), (1, 1))
WEIGHT = Fraction(1, len(STATES))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
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


def scalar(fn: Callable[[int, int], int | Fraction]) -> ScalarField:
    return {state: Fraction(fn(*state)) for state in STATES}


def vector(fn: Callable[[int, int], Iterable[int | Fraction]]) -> VectorField:
    return {
        state: tuple(Fraction(value) for value in fn(*state)) for state in STATES
    }


def add(a: ScalarField, b: ScalarField) -> ScalarField:
    return {state: a[state] + b[state] for state in STATES}


def subtract(a: ScalarField, b: ScalarField) -> ScalarField:
    return {state: a[state] - b[state] for state in STATES}


def scale(c: Fraction, a: ScalarField) -> ScalarField:
    return {state: c * a[state] for state in STATES}


def expectation(field: ScalarField) -> Fraction:
    return sum((WEIGHT * field[state] for state in STATES), Fraction(0))


def expectation_vector(field: VectorField) -> tuple[Fraction, ...]:
    width = len(next(iter(field.values())))
    return tuple(
        sum((WEIGHT * field[state][index] for state in STATES), Fraction(0))
        for index in range(width)
    )


def conditional_x(field: ScalarField) -> ScalarField:
    out: ScalarField = {}
    for x in (-1, 1):
        value = sum((Fraction(1, 2) * field[(x, y)] for y in (-1, 1)), Fraction(0))
        for y in (-1, 1):
            out[(x, y)] = value
    return out


def conditional_x_vector(field: VectorField) -> VectorField:
    width = len(next(iter(field.values())))
    out: VectorField = {}
    for x in (-1, 1):
        value = tuple(
            sum(
                (Fraction(1, 2) * field[(x, y)][index] for y in (-1, 1)),
                Fraction(0),
            )
            for index in range(width)
        )
        for y in (-1, 1):
            out[(x, y)] = value
    return out


def constant_expectation(field: ScalarField) -> ScalarField:
    value = expectation(field)
    return {state: value for state in STATES}


def l2_square(field: ScalarField) -> Fraction:
    return expectation({state: value * value for state, value in field.items()})


def l2_inner(left: ScalarField, right: ScalarField) -> Fraction:
    return expectation({state: left[state] * right[state] for state in STATES})


def dot(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def vector_l2_square(field: VectorField) -> Fraction:
    return sum((WEIGHT * dot(field[state], field[state]) for state in STATES), Fraction(0))


def equal_scalar(left: ScalarField, right: ScalarField) -> bool:
    return all(left[state] == right[state] for state in STATES)


def pair_expectation(values: dict[int, tuple[Fraction, ...]], fn: Callable[[tuple[Fraction, ...], tuple[Fraction, ...]], Fraction]) -> Fraction:
    return sum(
        (
            Fraction(1, 4) * fn(values[y], values[yp])
            for y in (-1, 1)
            for yp in (-1, 1)
        ),
        Fraction(0),
    )


def raw_owner_current(
    replica: int,
    increments: tuple[Fraction, ...],
    *,
    freeze_feedback: bool = False,
) -> tuple[Fraction, Fraction]:
    """Nonlinear endpoint fixture with replica-specific later feedback."""
    total = sum(increments, Fraction(0))
    feedback = Fraction(replica) if freeze_feedback else Fraction(replica) * (1 + total)
    return 1 + total + feedback, total * total + feedback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    one = scalar(lambda _x, _y: 1)
    x_field = scalar(lambda x, _y: x)
    y_field = scalar(lambda _x, y: y)
    zero = scalar(lambda _x, _y: 0)

    # Exact orthogonal filtration projections on two independent roots.
    p0_x = constant_expectation(x_field)
    p1_x = conditional_x(x_field)
    p1_y = conditional_x(y_field)
    audit.check("filtration", "P0 kills first root", equal_scalar(p0_x, zero), p0_x, zero)
    audit.check("filtration", "P1 retains first root", equal_scalar(p1_x, x_field), p1_x, x_field)
    audit.check("filtration", "P1 kills future root", equal_scalar(p1_y, zero), p1_y, zero)
    audit.check(
        "filtration",
        "P1 idempotent",
        equal_scalar(conditional_x(p1_x), p1_x),
        conditional_x(p1_x),
        p1_x,
    )
    audit.check(
        "filtration",
        "P0 after P1 equals P0",
        equal_scalar(constant_expectation(p1_x), p0_x),
        constant_expectation(p1_x),
        p0_x,
    )
    d1_x = subtract(p1_x, p0_x)
    future_x = subtract(x_field, p1_x)
    audit.check("filtration", "current-root increment is nonzero", l2_square(d1_x) == 1, l2_square(d1_x), 1)
    audit.check("filtration", "future residual kills retained data", l2_square(future_x) == 0, l2_square(future_x), 0)

    # Conditional centring contraction after a deterministic output projection.
    hilbert_y = vector(lambda x, y: (x + y, 2 * y))
    projected_y = vector(lambda x, y: (x + y,))
    projected_mean = conditional_x_vector(projected_y)
    projected_centred: VectorField = {
        state: tuple(a - b for a, b in zip(projected_y[state], projected_mean[state]))
        for state in STATES
    }
    total_projected = vector_l2_square(projected_y)
    mean_projected = vector_l2_square(projected_mean)
    centred_projected = vector_l2_square(projected_centred)
    audit.check("centring", "deterministic projection energy", total_projected == 2, total_projected, 2)
    audit.check("centring", "retained mean energy", mean_projected == 1, mean_projected, 1)
    audit.check("centring", "conditional Pythagoras", centred_projected == total_projected - mean_projected, centred_projected, total_projected - mean_projected)
    audit.check("centring", "centring is contractive", centred_projected <= total_projected, centred_projected, "<=2")
    audit.check("centring", "unused Hilbert coordinate is nontrivial", vector_l2_square(hilbert_y) == 6, vector_l2_square(hilbert_y), 6)

    # A future-dependent multiplier does not commute with future conditioning.
    q = scalar(lambda _x, y: 1 if y == 1 else 0)
    qz = {state: q[state] * y_field[state] for state in STATES}
    centred_qz = subtract(qz, conditional_x(qz))
    centred_z = subtract(y_field, conditional_x(y_field))
    q_centred_z = {state: q[state] * centred_z[state] for state in STATES}
    commutator = subtract(centred_qz, q_centred_z)
    minus_half = scalar(lambda _x, _y: Fraction(-1, 2))
    audit.check("commutator", "future multiplier defect", equal_scalar(commutator, minus_half), commutator, minus_half)
    audit.check("commutator", "future multiplier defect norm", l2_square(commutator) == Fraction(1, 4), l2_square(commutator), Fraction(1, 4))

    # Literal post-heat R-088 data are retained-data measurable.
    post_heat_atom = add(scale(Fraction(3, 2), x_field), scale(Fraction(1, 5), one))
    post_heat_mean = conditional_x(post_heat_atom)
    post_heat_future_residual = subtract(post_heat_atom, post_heat_mean)
    audit.check("post_heat", "post-heat atom is retained", equal_scalar(post_heat_mean, post_heat_atom), post_heat_mean, post_heat_atom)
    audit.check("post_heat", "post-heat future centring vanishes", l2_square(post_heat_future_residual) == 0, l2_square(post_heat_future_residual), 0)
    audit.check("post_heat", "current-root centring remains nonzero", l2_square(subtract(post_heat_atom, constant_expectation(post_heat_atom))) == Fraction(9, 4), l2_square(subtract(post_heat_atom, constant_expectation(post_heat_atom))), Fraction(9, 4))

    # Mean-only information cannot recover future variance.
    x0 = zero
    x1 = y_field
    mean0 = conditional_x(x0)
    mean1 = conditional_x(x1)
    var0 = l2_square(subtract(x0, mean0))
    var1 = l2_square(subtract(x1, mean1))
    audit.check("mean_only_nogo", "post-heat means coincide", equal_scalar(mean0, mean1), mean0, mean1)
    audit.check("mean_only_nogo", "zero-current variance", var0 == 0, var0, 0)
    audit.check("mean_only_nogo", "future-current variance", var1 == 1, var1, 1)
    audit.check("mean_only_nogo", "variance data separate", var0 != var1, (var0, var1), "different")

    # Common-heat conditional replicas: mean square, variance, and owner identity.
    replica_values = {
        -1: (Fraction(0), Fraction(3)),
        1: (Fraction(2), Fraction(1)),
    }
    replica_mean = tuple((replica_values[-1][i] + replica_values[1][i]) / 2 for i in range(2))
    mean_square = dot(replica_mean, replica_mean)
    second_moment = sum((Fraction(1, 2) * dot(value, value) for value in replica_values.values()), Fraction(0))
    pair_dot = pair_expectation(replica_values, dot)
    pair_difference = pair_expectation(
        replica_values,
        lambda a, b: dot(tuple(x - y for x, y in zip(a, b)), tuple(x - y for x, y in zip(a, b))),
    )
    variance = second_moment - mean_square
    audit.check("replica", "replica mean", replica_mean == (1, 2), replica_mean, (1, 2))
    audit.check("replica", "mean square", mean_square == 5, mean_square, 5)
    audit.check("replica", "second moment", second_moment == 7, second_moment, 7)
    audit.check("replica", "paired mean polarization", pair_dot == mean_square, pair_dot, mean_square)
    audit.check("replica", "half replica difference is variance", pair_difference / 2 == variance, pair_difference / 2, variance)
    audit.check("replica", "variance value", variance == 2, variance, 2)
    audit.check("replica", "Pythagoras in replica coordinates", mean_square + variance == second_moment, mean_square + variance, second_moment)
    theta = Fraction(3)
    forest = second_moment - theta
    p_comp = (mean_square - theta) / 2
    audit.check("owner", "forest value", forest == 4, forest, 4)
    audit.check("owner", "trace-excess owner", p_comp == 1, p_comp, 1)
    audit.check("owner", "forest-minus-variance owner", (forest - variance) / 2 == p_comp, (forest - variance) / 2, p_comp)
    audit.check("owner", "replica owner coefficient", forest / 2 - pair_difference / 4 == p_comp, forest / 2 - pair_difference / 4, p_comp)

    # Exact raw sequential telescope from endpoint evaluations in each replica.
    prefixes = ((), (Fraction(1),), (Fraction(1), Fraction(2)))
    raw_paths = {
        y: tuple(raw_owner_current(y, prefix) for prefix in prefixes)
        for y in (-1, 1)
    }
    raw_low = {y: raw_paths[y][0] for y in (-1, 1)}
    raw_atoms = {
        y: tuple(
            tuple(raw_paths[y][step][i] - raw_paths[y][step - 1][i] for i in range(2))
            for step in range(1, len(prefixes))
        )
        for y in (-1, 1)
    }
    raw_terminal_direct = {
        y: raw_owner_current(y, prefixes[-1])
        for y in (-1, 1)
    }
    raw_terminal = {
        y: tuple(
            raw_low[y][i] + sum((atom[i] for atom in raw_atoms[y]), Fraction(0))
            for i in range(2)
        )
        for y in (-1, 1)
    }
    replica_delta_terminal = tuple(raw_terminal[1][i] - raw_terminal[-1][i] for i in range(2))
    replica_delta_atoms = tuple(
        (raw_low[1][i] - raw_low[-1][i])
        + sum(
            (raw_atoms[1][step][i] - raw_atoms[-1][step][i] for step in range(2)),
            Fraction(0),
        )
        for i in range(2)
    )
    audit.check("raw_telescope", "pathwise endpoint evaluations", raw_terminal == raw_terminal_direct, raw_terminal, raw_terminal_direct)
    audit.check("raw_telescope", "minus replica endpoint", raw_terminal[-1] == (0, 5), raw_terminal[-1], (0, 5))
    audit.check("raw_telescope", "plus replica endpoint", raw_terminal[1] == (8, 13), raw_terminal[1], (8, 13))
    audit.check("raw_telescope", "replica difference telescopes", replica_delta_terminal == replica_delta_atoms, replica_delta_terminal, replica_delta_atoms)
    low_delta = tuple(raw_low[1][i] - raw_low[-1][i] for i in range(2))
    audit.check("raw_telescope", "low replica difference retained", low_delta == (2, 2), low_delta, (2, 2))
    frozen_terminal = {y: raw_owner_current(y, prefixes[-1], freeze_feedback=True) for y in (-1, 1)}
    audit.check("raw_telescope", "frozen feedback changes endpoint", frozen_terminal != raw_terminal_direct, frozen_terminal, "different from recomputed feedback")

    # Owner-by-reveal Doob accounting derived from the same projections.
    owner_a = add(scale(Fraction(2), x_field), y_field)
    owner_b = add(x_field, scale(Fraction(3), y_field))
    owner_a_total = l2_square(subtract(owner_a, constant_expectation(owner_a)))
    owner_b_future = l2_square(subtract(owner_b, conditional_x(owner_b)))
    delta_a_one = subtract(conditional_x(owner_a), constant_expectation(owner_a))
    delta_a_two = subtract(owner_a, conditional_x(owner_a))
    delta_b_two = subtract(owner_b, conditional_x(owner_b))
    reveal_one = l2_square(delta_a_one)
    reveal_two_direct_sum = l2_square(delta_a_two) + l2_square(delta_b_two)
    audit.check("doob", "owner A terminal variance", owner_a_total == 4 + 1, owner_a_total, 5)
    audit.check("doob", "owner B future variance", owner_b_future == 9, owner_b_future, 9)
    audit.check("doob", "owner sum equals reveal transpose", owner_a_total + owner_b_future == reveal_one + reveal_two_direct_sum, owner_a_total + owner_b_future, reveal_one + reveal_two_direct_sum)
    audit.check("doob", "direct-sum reveal energy", reveal_two_direct_sum == 10, reveal_two_direct_sum, 10)
    audit.check("doob", "physical scalar merging would be false", (1 + 3) ** 2 != reveal_two_direct_sum, (1 + 3) ** 2, "!=10")

    # R-079 fixture computed from P0, P1, and P2 rather than stored energies.
    d1_project = lambda field: subtract(conditional_x(field), constant_expectation(field))
    d2_project = lambda field: subtract(field, conditional_x(field))
    j0 = zero
    j1 = x_field
    jstar = add(scale(Fraction(2), x_field), y_field)
    f1 = d1_project(subtract(j1, j0))
    i1 = d1_project(subtract(jstar, j1))
    f2 = d2_project(subtract(jstar, j1))
    terminal_one = d1_project(subtract(jstar, j0))
    terminal_two = d2_project(subtract(jstar, j0))
    physical_energy = l2_square(f1) + l2_square(f2)
    terminal_energy = l2_square(terminal_one) + l2_square(terminal_two)
    connection_correction = 2 * l2_inner(f1, i1) + l2_square(i1)
    audit.check("feedback", "first physical increment", equal_scalar(f1, x_field), f1, x_field)
    audit.check("feedback", "future connection increment", equal_scalar(i1, x_field), i1, x_field)
    audit.check("feedback", "terminal first increment splits", equal_scalar(add(f1, i1), terminal_one), add(f1, i1), terminal_one)
    audit.check("feedback", "physical-prefix energy", physical_energy == 2, physical_energy, 2)
    audit.check("feedback", "full terminal energy", terminal_energy == 5, terminal_energy, 5)
    audit.check("feedback", "missing connection correction", terminal_energy - physical_energy == connection_correction, terminal_energy - physical_energy, connection_correction)
    audit.check("feedback", "future-feedback channel is nonzero", connection_correction == 3, connection_correction, 3)

    # Gaussian OU-resolvent factors on chaos one and chaos two.
    chaos_one_variance = Fraction(1)
    chaos_one_ou = Fraction(2) * Fraction(1, 2)
    chaos_two_variance = Fraction(2)
    chaos_two_ou = Fraction(2) * Fraction(4) * Fraction(1, 4)
    audit.check("ou", "chaos-one OU factor", chaos_one_ou == chaos_one_variance, chaos_one_ou, chaos_one_variance)
    audit.check("ou", "chaos-two OU factor", chaos_two_ou == chaos_two_variance, chaos_two_ou, chaos_two_variance)
    n = 3
    smooth_feedback_variance = (1.0 - math.exp(-2.0 * n * n)) / (2.0 * n * n)
    audit.check("ou", "smooth feedback variance is positive", smooth_feedback_variance > 0.0, smooth_feedback_variance, ">0")
    audit.check("ou", "smooth feedback variance below one over eighteen", smooth_feedback_variance < 1.0 / 18.0, smooth_feedback_variance, "<1/18")

    # Product-space Loewner positivity is sufficient, not necessary on an abstract graph.
    product_eigenvalues = (1, 1, -1)
    graph_value = 1 + 1 - 1
    audit.check("graph", "product matrix is indefinite", min(product_eigenvalues) < 0, product_eigenvalues, "one negative eigenvalue")
    audit.check("graph", "abstract graph is strictly positive", graph_value == 1, graph_value, 1)
    audit.check("graph", "full product PSD is not graph-necessary", min(product_eigenvalues) < 0 and graph_value > 0, (product_eigenvalues, graph_value), "indefinite product and positive graph")

    # Direct Taylor spends the source and sextic margins once.
    eta = Fraction(1, 5)
    eta0 = Fraction(1, 10)
    zeta = Fraction(1, 20)
    zeta0 = Fraction(1, 40)
    source_margin = Fraction(9, 20) - eta - eta0
    sextic_margin = Fraction(3, 20) - zeta - zeta0
    force_completion = Fraction(1, 1) / (4 * Fraction(9, 20))
    audit.check("taylor", "Taylor half-weight", Fraction(1, 2) * 2 == 1, Fraction(1, 2) * 2, 1)
    audit.check("taylor", "positive source margin fixture", source_margin == Fraction(3, 20), source_margin, Fraction(3, 20))
    audit.check("taylor", "positive sextic margin fixture", sextic_margin == Fraction(3, 40), sextic_margin, Fraction(3, 40))
    audit.check("taylor", "full force completion coefficient", force_completion == Fraction(5, 9), force_completion, Fraction(5, 9))
    audit.check("taylor", "force completion consumes displayed source square", force_completion * Fraction(9, 20) == Fraction(1, 4), force_completion * Fraction(9, 20), Fraction(1, 4))

    # Scope firewalls are executable assertions, not prose-only promises.
    open_obligations = {
        "raw_spatial_intertwiner": False,
        "one_use_q_ledger": False,
        "signed_forest_current_bound": False,
        "positive_headroom": False,
        "complete_low_anchor": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    for name, value in open_obligations.items():
        audit.check("scope", name, value is False, value, False)

    audit.check(
        "contracts",
        "primary assertion count",
        len(audit.rows) + 1 == EXPECTED_ASSERTIONS,
        len(audit.rows) + 1,
        EXPECTED_ASSERTIONS,
    )
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
            "replica_mean_square": str(mean_square),
            "replica_variance": str(variance),
            "replica_second_moment": str(second_moment),
            "owner_trace_excess": str(p_comp),
            "owner_reveal_total": int(owner_a_total + owner_b_future),
            "post_heat_future_residual": str(l2_square(post_heat_future_residual)),
            "physical_only_energy": int(physical_energy),
            "terminal_energy": int(terminal_energy),
            "graph_compressed_value": int(graph_value),
            "source_margin_fixture": str(source_margin),
            "sextic_margin_fixture": str(sextic_margin),
        },
        "scope": {
            "common_heat_replica_identity": True,
            "raw_replica_telescope": True,
            "post_heat_mean_only_no_go": True,
            "production_raw_spatial_intertwiner": False,
            "production_one_use_q_ledger": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-136 primary {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    print(f"replica variance={variance}; owner/reveal total={owner_a_total + owner_b_future}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
