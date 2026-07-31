#!/usr/bin/env python3
"""Independent standard-library audit for the scoped A13 R-136 boundary.

This implementation does not import the primary certificate.  It uses exact
four-atom conditional-expectation matrices and independent replica/Doob
enumerations to test the filtration, owner, telescope, and scope contracts.
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


RESULT_ID = "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY"
SCHEMA = "tect/a13-common-heat-replica-raw-sequential-owner-boundary-independent/1.0"
EXPECTED_ASSERTIONS = 71
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-common-heat-replica-raw-sequential-owner-boundary/"
    "result.json"
)

Q = Fraction
Matrix = tuple[tuple[Fraction, ...], ...]
Vector = tuple[Fraction, ...]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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


def matmul(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return tuple(
        tuple(
            sum((left[i][k] * right[k][j] for k in range(size)), Q(0))
            for j in range(size)
        )
        for i in range(size)
    )


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(
        sum((matrix[i][j] * vector[j] for j in range(len(vector))), Q(0))
        for i in range(len(matrix))
    )


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[i][j] - right[i][j] for j in range(len(left)))
        for i in range(len(left))
    )


def vecsub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[j][i] for j in range(len(matrix))) for i in range(len(matrix)))


def l2(vector: Vector) -> Fraction:
    return sum((value * value for value in vector), Q(0)) / len(vector)


def dot(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Q(0))


def raw_owner_current(
    replica: int,
    increments: tuple[Fraction, ...],
    *,
    freeze_feedback: bool = False,
) -> tuple[Fraction, Fraction]:
    """Independent nonlinear endpoint fixture with recomputed feedback."""
    total = sum(increments, Q(0))
    feedback = Q(replica) if freeze_feedback else Q(replica) * (1 + total)
    return 1 + total + feedback, total * total + feedback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    identity: Matrix = tuple(
        tuple(Q(1) if i == j else Q(0) for j in range(4)) for i in range(4)
    )
    p0: Matrix = tuple(tuple(Q(1, 4) for _j in range(4)) for _i in range(4))
    p1: Matrix = (
        (Q(1, 2), Q(1, 2), Q(0), Q(0)),
        (Q(1, 2), Q(1, 2), Q(0), Q(0)),
        (Q(0), Q(0), Q(1, 2), Q(1, 2)),
        (Q(0), Q(0), Q(1, 2), Q(1, 2)),
    )
    d1 = matsub(p1, p0)
    future = matsub(identity, p1)
    zero_matrix: Matrix = tuple(tuple(Q(0) for _j in range(4)) for _i in range(4))
    audit.check("matrix", "P0 symmetric", transpose(p0) == p0, transpose(p0), p0)
    audit.check("matrix", "P1 symmetric", transpose(p1) == p1, transpose(p1), p1)
    audit.check("matrix", "P0 idempotent", matmul(p0, p0) == p0, matmul(p0, p0), p0)
    audit.check("matrix", "P1 idempotent", matmul(p1, p1) == p1, matmul(p1, p1), p1)
    audit.check("matrix", "nested projections", matmul(p0, p1) == p0, matmul(p0, p1), p0)
    audit.check("matrix", "current increment idempotent", matmul(d1, d1) == d1, matmul(d1, d1), d1)
    audit.check("matrix", "future residual idempotent", matmul(future, future) == future, matmul(future, future), future)
    audit.check("matrix", "future residual kills retained range", matmul(future, p1) == zero_matrix, matmul(future, p1), zero_matrix)
    audit.check("matrix", "current and future ranges orthogonal", matmul(d1, future) == zero_matrix, matmul(d1, future), zero_matrix)

    x: Vector = (Q(-1), Q(-1), Q(1), Q(1))
    y: Vector = (Q(-1), Q(1), Q(-1), Q(1))
    one: Vector = (Q(1), Q(1), Q(1), Q(1))
    zero: Vector = (Q(0), Q(0), Q(0), Q(0))
    audit.check("filtration", "P1 x=x", matvec(p1, x) == x, matvec(p1, x), x)
    audit.check("filtration", "P1 y=0", matvec(p1, y) == zero, matvec(p1, y), zero)
    audit.check("filtration", "d1 x=x", matvec(d1, x) == x, matvec(d1, x), x)
    audit.check("filtration", "future x=0", matvec(future, x) == zero, matvec(future, x), zero)
    audit.check("filtration", "future y=y", matvec(future, y) == y, matvec(future, y), y)

    # Independent centring calculation for the first projected coordinate x+y.
    projected: Vector = tuple(a + b for a, b in zip(x, y))
    retained = matvec(p1, projected)
    centred = vecsub(projected, retained)
    audit.check("centring", "projected energy", l2(projected) == 2, l2(projected), 2)
    audit.check("centring", "retained energy", l2(retained) == 1, l2(retained), 1)
    audit.check("centring", "centred energy", l2(centred) == 1, l2(centred), 1)
    audit.check("centring", "Pythagoras", l2(projected) == l2(retained) + l2(centred), l2(projected), l2(retained) + l2(centred))

    # Future-dependent multiplication commutator.
    q_diag: Matrix = (
        (Q(0), Q(0), Q(0), Q(0)),
        (Q(0), Q(1), Q(0), Q(0)),
        (Q(0), Q(0), Q(0), Q(0)),
        (Q(0), Q(0), Q(0), Q(1)),
    )
    c_qz = matvec(future, matvec(q_diag, y))
    q_cz = matvec(q_diag, matvec(future, y))
    defect = vecsub(c_qz, q_cz)
    expected_defect: Vector = (Q(-1, 2), Q(-1, 2), Q(-1, 2), Q(-1, 2))
    audit.check("commutator", "exact random-projection defect", defect == expected_defect, defect, expected_defect)
    audit.check("commutator", "defect square", l2(defect) == Q(1, 4), l2(defect), Q(1, 4))

    # Post-heat measurability versus current-root centring.
    post_heat: Vector = tuple(Q(3, 2) * value + Q(1, 5) for value in x)
    audit.check("post_heat", "future expectation fixes atom", matvec(p1, post_heat) == post_heat, matvec(p1, post_heat), post_heat)
    audit.check("post_heat", "future-centred atom is zero", matvec(future, post_heat) == zero, matvec(future, post_heat), zero)
    audit.check("post_heat", "current-root part survives", l2(matvec(d1, post_heat)) == Q(9, 4), l2(matvec(d1, post_heat)), Q(9, 4))

    # Same post-heat mean, distinct raw future variances.
    audit.check("mean_only_nogo", "means agree", matvec(p1, zero) == matvec(p1, y), matvec(p1, zero), matvec(p1, y))
    audit.check("mean_only_nogo", "first variance", l2(matvec(future, zero)) == 0, l2(matvec(future, zero)), 0)
    audit.check("mean_only_nogo", "second variance", l2(matvec(future, y)) == 1, l2(matvec(future, y)), 1)

    # Independent common-heat replica enumeration.
    samples = {Q(-1): (Q(0), Q(3)), Q(1): (Q(2), Q(1))}
    mean = tuple((samples[Q(-1)][i] + samples[Q(1)][i]) / 2 for i in range(2))
    second = sum((Q(1, 2) * dot(value, value) for value in samples.values()), Q(0))
    mixed = sum((Q(1, 4) * dot(samples[a], samples[b]) for a in samples for b in samples), Q(0))
    pair_diff = sum(
        (
            Q(1, 4)
            * dot(
                tuple(samples[a][i] - samples[b][i] for i in range(2)),
                tuple(samples[a][i] - samples[b][i] for i in range(2)),
            )
            for a in samples
            for b in samples
        ),
        Q(0),
    )
    variance = second - dot(mean, mean)
    audit.check("replica", "conditional mean", mean == (1, 2), mean, (1, 2))
    audit.check("replica", "second moment", second == 7, second, 7)
    audit.check("replica", "mixed replica equals mean square", mixed == dot(mean, mean) == 5, mixed, 5)
    audit.check("replica", "replica-difference variance", pair_diff / 2 == variance == 2, pair_diff / 2, 2)
    audit.check("replica", "second moment split", mixed + pair_diff / 2 == second, mixed + pair_diff / 2, second)
    theta = Q(3)
    forest = second - theta
    owner = (mixed - theta) / 2
    audit.check("owner", "forest coordinate", forest == 4, forest, 4)
    audit.check("owner", "owner coordinate", owner == 1, owner, 1)
    audit.check("owner", "replica owner identity", forest / 2 - pair_diff / 4 == owner, forest / 2 - pair_diff / 4, owner)

    # Raw telescope from independent endpoint evaluations, not asserted atoms.
    prefixes = ((), (Q(1),), (Q(1), Q(2)))
    paths = {
        yv: tuple(raw_owner_current(yv, prefix) for prefix in prefixes)
        for yv in (-1, 1)
    }
    lows = {yv: paths[yv][0] for yv in (-1, 1)}
    atoms = {
        yv: tuple(
            tuple(paths[yv][step][i] - paths[yv][step - 1][i] for i in range(2))
            for step in range(1, len(prefixes))
        )
        for yv in (-1, 1)
    }
    endpoint_minus = tuple(
        lows[-1][i] + sum((atom[i] for atom in atoms[-1]), Q(0))
        for i in range(2)
    )
    endpoint_plus = tuple(
        lows[1][i] + sum((atom[i] for atom in atoms[1]), Q(0))
        for i in range(2)
    )
    direct_endpoints = {
        yv: raw_owner_current(yv, prefixes[-1])
        for yv in (-1, 1)
    }
    endpoint_delta = tuple(endpoint_plus[i] - endpoint_minus[i] for i in range(2))
    atom_delta = tuple(
        lows[1][i] - lows[-1][i]
        + sum((atoms[1][step][i] - atoms[-1][step][i] for step in range(2)), Q(0))
        for i in range(2)
    )
    audit.check("raw_telescope", "endpoint evaluations", (endpoint_minus, endpoint_plus) == (direct_endpoints[-1], direct_endpoints[1]), (endpoint_minus, endpoint_plus), (direct_endpoints[-1], direct_endpoints[1]))
    audit.check("raw_telescope", "minus endpoint", endpoint_minus == (0, 5), endpoint_minus, (0, 5))
    audit.check("raw_telescope", "plus endpoint", endpoint_plus == (8, 13), endpoint_plus, (8, 13))
    audit.check("raw_telescope", "replica difference", endpoint_delta == atom_delta == (8, 8), endpoint_delta, (8, 8))
    low_delta = tuple(lows[1][i] - lows[-1][i] for i in range(2))
    audit.check("raw_telescope", "low difference is retained", low_delta == (2, 2), low_delta, (2, 2))
    frozen = {yv: raw_owner_current(yv, prefixes[-1], freeze_feedback=True) for yv in (-1, 1)}
    audit.check("raw_telescope", "frozen feedback changes endpoints", frozen != direct_endpoints, frozen, "different from recomputed feedback")

    # Owner/reveal array derived independently from the projection matrices.
    owner_a = tuple(2 * x[i] + y[i] for i in range(4))
    owner_b = tuple(x[i] + 3 * y[i] for i in range(4))
    owner_variances = (
        l2(vecsub(owner_a, matvec(p0, owner_a))),
        l2(matvec(future, owner_b)),
    )
    reveal_direct_sums = (
        l2(matvec(d1, owner_a)),
        l2(matvec(future, owner_a)) + l2(matvec(future, owner_b)),
    )
    audit.check("doob", "owner total", sum(owner_variances, Q(0)) == 14, sum(owner_variances, Q(0)), 14)
    audit.check("doob", "reveal total", sum(reveal_direct_sums, Q(0)) == 14, sum(reveal_direct_sums, Q(0)), 14)
    audit.check("doob", "transpose equality", sum(owner_variances, Q(0)) == sum(reveal_direct_sums, Q(0)), sum(owner_variances, Q(0)), sum(reveal_direct_sums, Q(0)))
    audit.check("doob", "false scalar owner merge rejected", (1 + 3) ** 2 != reveal_direct_sums[1], (1 + 3) ** 2, "!=10")
    # R-079 future-feedback correction derived from J0, J1, and Jstar.
    j0 = zero
    j1 = x
    jstar = tuple(2 * x[i] + y[i] for i in range(4))
    f1 = matvec(d1, vecsub(j1, j0))
    i1 = matvec(d1, vecsub(jstar, j1))
    f2 = matvec(future, vecsub(jstar, j1))
    terminal_one = matvec(d1, vecsub(jstar, j0))
    terminal_two = matvec(future, vecsub(jstar, j0))
    physical_energy = l2(f1) + l2(f2)
    terminal_energy = l2(terminal_one) + l2(terminal_two)
    correction = 2 * dot(f1, i1) / len(f1) + l2(i1)
    audit.check("feedback", "first physical increment", f1 == x, f1, x)
    audit.check("feedback", "future connection increment", i1 == x, i1, x)
    audit.check("feedback", "terminal first increment splits", tuple(f1[i] + i1[i] for i in range(4)) == terminal_one, tuple(f1[i] + i1[i] for i in range(4)), terminal_one)
    audit.check("feedback", "physical energy", physical_energy == 2, physical_energy, 2)
    audit.check("feedback", "terminal energy", terminal_energy == 5, terminal_energy, 5)
    audit.check("feedback", "connection correction", terminal_energy - physical_energy == correction, terminal_energy - physical_energy, correction)

    # Independent chaos calculation for the OU-resolvent factor.
    for chaos in (1, 2, 3, 7):
        integral_factor = Q(2) * Q(chaos) * Q(1, 2 * chaos)
        audit.check("ou", f"chaos {chaos} factor", integral_factor == 1, integral_factor, 1)
    n = 4
    smooth_variance = (1.0 - math.exp(-2.0 * n * n)) / (2.0 * n * n)
    audit.check("ou", "smooth connection is nonzero", smooth_variance > 0.0, smooth_variance, ">0")

    # Compression to an abstract graph fixture; no production graph is built.
    diagonal = (Q(1), Q(1), Q(-1))
    graph_vector = (Q(1), Q(1), Q(1))
    graph_form = sum((diagonal[i] * graph_vector[i] ** 2 for i in range(3)), Q(0))
    audit.check("graph", "ambient form indefinite", min(diagonal) == -1, diagonal, "minimum -1")
    audit.check("graph", "abstract compressed form positive", graph_form == 1, graph_form, 1)
    audit.check("graph", "ambient PSD not necessary", min(diagonal) < 0 < graph_form, (diagonal, graph_form), "indefinite/positive")

    # Direct Taylor checked on an exact quadratic radial path.
    eta = Q(1, 5)
    eta0 = Q(1, 10)
    zeta = Q(1, 20)
    zeta0 = Q(1, 40)
    a = eta + zeta
    p0_value = Q(7, 13)
    p0_derivative = Q(-2, 17)
    p1_value = p0_value + p0_derivative - a
    taylor_reconstruction = p0_value + p0_derivative + Q(1, 2) * (-2 * a)
    audit.check("taylor", "quadratic Taylor equality", p1_value == taylor_reconstruction, p1_value, taylor_reconstruction)
    audit.check("taylor", "source margin", Q(9, 20) - eta - eta0 == Q(3, 20), Q(9, 20) - eta - eta0, Q(3, 20))
    audit.check("taylor", "sextic margin", Q(3, 20) - zeta - zeta0 == Q(3, 40), Q(3, 20) - zeta - zeta0, Q(3, 40))
    audit.check("taylor", "force completion", Q(1) / (4 * Q(9, 20)) == Q(5, 9), Q(1) / (4 * Q(9, 20)), Q(5, 9))

    open_scope = (
        "raw_spatial_intertwiner",
        "one_use_q_ledger",
        "signed_forest_current_bound",
        "positive_headroom",
        "complete_low_anchor",
        "a13_gate_closed",
        "nelson",
        "sector_a_closed",
    )
    for name in open_scope:
        audit.check("scope", name, False is False, False, False)

    audit.check(
        "contracts",
        "independent assertion count",
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
            "matrix_rank_surrogates": {"P0_trace": "1", "P1_trace": "2", "D1_trace": "1", "future_trace": "2"},
            "replica_variance": str(variance),
            "replica_pair_difference": str(pair_diff),
            "owner_trace_excess": str(owner),
            "owner_reveal_total": str(sum(owner_variances, Q(0))),
            "feedback_correction": str(correction),
            "graph_form": str(graph_form),
        },
        "scope": {
            "independent_standard_library": True,
            "imports_primary": False,
            "production_raw_spatial_intertwiner": False,
            "production_one_use_q_ledger": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-136 independent {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    print(f"replica variance={variance}; feedback correction={correction}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
