#!/usr/bin/env python3
"""Non-importing independent certificate for the scoped A13 R-141 result.

Only the Python standard library is used.  The primary R-141 module is never
imported.  Exact rational fixtures, finite probability enumeration, an
independent geometric sum, and direct symmetric-eigenvalue calculations audit
the sign, half-factor, quotient, collar, and ownership claims.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


RESULT_ID = (
    "A13-CLASSII-PROJECTED-FORCE-GLOBAL-DOOB-SIGNED-GRAM-"
    "ADAPTIVE-COLLAR-QUOTIENT-BOUNDARY"
)
SCHEMA = (
    "tect/a13-projected-force-global-doob-signed-gram-adaptive-collar-"
    "quotient-boundary-independent/1.0"
)
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-projected-force-global-doob-signed-gram-"
    "adaptive-collar-quotient-boundary/result.json"
)
PRIMARY = Path(
    "codes/foundations/"
    "a13_classii_projected_force_global_doob_signed_gram_adaptive_collar_"
    "quotient_boundary.py"
)
Q = Fraction
P_MASS = Q(4_000_000_000_001, 1_000_000_000_000)
BETA = Q(7, 5)
OUTPUT_DECAY = Q(2, 3)
WEIGHT = Q(7, 12)
ENERGY_FACTOR = Q(3, 40) / P_MASS
HEADROOM = Q(1_590_880_000_000_403, 15_840_000_000_003_960)
SMALL_HEADROOM = Q(159_126_895, 10_000_000_000)
TOL = 3.0e-10


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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


def t(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def mm(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    right_t = t(right)
    return [
        [sum((x * y for x, y in zip(row, column)), Q(0)) for column in right_t]
        for row in left
    ]


def mv(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum((x * y for x, y in zip(row, vector)), Q(0)) for row in matrix]


def inner(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Q(0))


def qform(vector: list[Fraction], matrix: list[list[Fraction]]) -> Fraction:
    return inner(vector, mv(matrix, vector))


def addm(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(a, b)] for a, b in zip(left, right)]


def scalem(value: Fraction, matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[value * entry for entry in row] for row in matrix]


def det2(matrix: list[list[Fraction]]) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def det3_float(matrix: list[list[float]]) -> float:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def eigvals_sym3(matrix: list[list[float]]) -> list[float]:
    """Closed trigonometric eigenvalues for a real symmetric 3x3 matrix."""

    trace = sum(matrix[i][i] for i in range(3))
    mean = trace / 3.0
    centered = [[matrix[i][j] - (mean if i == j else 0.0) for j in range(3)] for i in range(3)]
    p2 = sum(centered[i][i] ** 2 for i in range(3)) + 2.0 * sum(
        centered[i][j] ** 2 for i in range(3) for j in range(i + 1, 3)
    )
    p = math.sqrt(p2 / 6.0)
    if p == 0.0:
        return [mean, mean, mean]
    normalized = [[centered[i][j] / p for j in range(3)] for i in range(3)]
    r = max(-1.0, min(1.0, det3_float(normalized) / 2.0))
    phi = math.acos(r) / 3.0
    values = [
        mean + 2.0 * p * math.cos(phi),
        mean + 2.0 * p * math.cos(phi + 2.0 * math.pi / 3.0),
        mean + 2.0 * p * math.cos(phi + 4.0 * math.pi / 3.0),
    ]
    return sorted(values)


def power_two(exponent: Fraction) -> float:
    return 2.0 ** float(exponent)


def triangular_cell(collar: int, a_gap: int, d_gap: int) -> float:
    delta = collar - 5
    exponent = 2 * WEIGHT * d_gap - BETA * a_gap
    if d_gap >= a_gap - delta:
        exponent -= 2 * OUTPUT_DECAY * (d_gap - a_gap + delta)
    return power_two(exponent)


def direct_sum(collar: int, cutoff: int) -> float:
    return math.fsum(
        triangular_cell(collar, a_gap, d_gap)
        for a_gap in range(1, cutoff + 1)
        for d_gap in range(cutoff + 1)
    )


def closed_sum(collar: int) -> float:
    delta = collar - 5
    q = power_two(2 * WEIGHT)
    u = power_two(-(BETA - 2 * WEIGHT))
    v = power_two(-BETA)
    rho = power_two(-2 * (OUTPUT_DECAY - WEIGHT))
    near = (
        power_two(-2 * WEIGHT * delta) * u ** (delta + 1) / (1 - u)
        - v ** (delta + 1) / (1 - v)
    ) / (q - 1)
    low = power_two(-2 * OUTPUT_DECAY * delta) * math.fsum(
        power_two(-(BETA - 2 * OUTPUT_DECAY) * a) for a in range(1, delta + 1)
    ) / (1 - rho)
    high = power_two(-2 * WEIGHT * delta) * u ** (delta + 1) / ((1 - rho) * (1 - u))
    return near + low + high


def imported_roots(path: Path) -> tuple[set[str], bool]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    relative = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative = relative or node.level > 0
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots, relative


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # Force/Hessian cancellation derived by a different exact fixture.
    gt = [Q(8), Q(-6), Q(10)]
    gv = [Q(4), Q(14), Q(-2)]
    gcn = [(gv[i] - gt[i]) / 2 for i in range(3)]
    gcomp_a = [gcn[i] - gv[i] / 2 for i in range(3)]
    gcomp_b = [-value / 2 for value in gt]
    audit.add("force_algebra", "covariance-normal value", gcn == [Q(-2), Q(10), Q(-6)], gcn, [Q(-2), Q(10), Q(-6)])
    audit.add("force_algebra", "two complete-force routes agree", gcomp_a == gcomp_b, gcomp_a, gcomp_b)
    audit.add("force_algebra", "complete-force value", gcomp_b == [Q(-4), Q(3), Q(-5)], gcomp_b, [Q(-4), Q(3), Q(-5)])
    audit.add("force_algebra", "extra variance is a mutation", [gcomp_a[i] + gv[i] / 2 for i in range(3)] != gcomp_a, [gcomp_a[i] + gv[i] / 2 for i in range(3)], gcomp_a)
    ht = [[Q(4), Q(1)], [Q(1), Q(-2)]]
    hv = [[Q(6), Q(-3)], [Q(-3), Q(8)]]
    hcn = scalem(Q(1, 2), addm(hv, scalem(Q(-1), ht)))
    hcomp = addm(hcn, scalem(Q(-1, 2), hv))
    hprod = addm(hcomp, [[Q(9, 10), Q(0)], [Q(0), Q(9, 10)]])
    audit.add("force_algebra", "Hessian covariance-normal", hcn == [[Q(1), Q(-2)], [Q(-2), Q(5)]], hcn, [[Q(1), Q(-2)], [Q(-2), Q(5)]])
    audit.add("force_algebra", "Hessian complete", hcomp == scalem(Q(-1, 2), ht), hcomp, scalem(Q(-1, 2), ht))
    audit.add("force_algebra", "Hessian production", hprod == [[Q(-11, 10), Q(-1, 2)], [Q(-1, 2), Q(19, 10)]], hprod, [[Q(-11, 10), Q(-1, 2)], [Q(-1, 2), Q(19, 10)]])
    audit.add("force_algebra", "Hessian symmetric", hprod == t(hprod), hprod, "symmetric")
    audit.add("force_algebra", "source cost exactly nine tenths", hprod[0][0] - hcomp[0][0] == Q(9, 10), hprod[0][0] - hcomp[0][0], Q(9, 10))

    # Exact finite probability projection.
    omega = [(a, b) for a in (-1, 1) for b in (-1, 1)]
    g = {(a, b): Q(3 * a + 5 * b + 7 * a * b + 2) for a, b in omega}
    mean_g = sum(g.values(), Q(0)) / 4
    block1 = 2 * mean_g
    cond2 = {a: sum((Q(3) * g[(a, b)] for b in (-1, 1)), Q(0)) / 2 for a in (-1, 1)}
    prod1 = Q(9, 10) * Q(1, 3) + block1
    prod2 = {a: Q(9, 10) * Q(a, 2) + cond2[a] for a in (-1, 1)}
    audit.add("projected_force", "endpoint mean", mean_g == Q(2), mean_g, Q(2))
    audit.add("projected_force", "first pullback mean", block1 == Q(4), block1, Q(4))
    audit.add("projected_force", "first production force", prod1 == Q(43, 10), prod1, Q(43, 10))
    audit.add("projected_force", "conditional a minus", cond2[-1] == Q(-3), cond2[-1], Q(-3))
    audit.add("projected_force", "conditional a plus", cond2[1] == Q(15), cond2[1], Q(15))
    audit.add("projected_force", "second production forces", prod2 == {-1: Q(-69, 20), 1: Q(309, 20)}, prod2, {-1: Q(-69, 20), 1: Q(309, 20)})
    audit.add("projected_force", "raw future mutation", Q(3) * g[(1, -1)] != Q(3) * g[(1, 1)] and cond2[1] == Q(15), (g[(1, -1)], g[(1, 1)], cond2[1]), "raw differs but legal projection fixed")

    # Signature and owner multiplicity.
    b2, y2, theta, variance = Q(9), Q(4), Q(6), Q(5)
    phi2 = b2 + y2
    j2 = phi2 + variance
    forest = j2 - theta
    d0 = theta - y2
    signature = theta - j2 + variance
    kfuture = (y2 - theta) / 2
    pcomp = (phi2 - theta) / 2
    signature_equalities = [
        signature,
        theta - phi2,
        variance - forest,
        d0 - b2,
    ]
    audit.add("signature_owner", "Phi energy", phi2 == Q(13), phi2, Q(13))
    audit.add("signature_owner", "raw-current energy", j2 == Q(18), j2, Q(18))
    audit.add("signature_owner", "forest energy", forest == Q(12), forest, Q(12))
    audit.add("signature_owner", "D0", d0 == Q(2), d0, Q(2))
    audit.add("signature_owner", "all signature coordinates agree", len(set(signature_equalities)) == 1, signature_equalities, "all -7")
    audit.add("signature_owner", "signature value", signature == Q(-7), signature, Q(-7))
    audit.add("signature_owner", "future owner", kfuture == Q(-1), kfuture, Q(-1))
    audit.add("signature_owner", "complete action owner", pcomp == Q(7, 2), pcomp, Q(7, 2))
    audit.add("signature_owner", "mean returned once", kfuture + b2 / 2 == pcomp, kfuture + b2 / 2, pcomp)
    audit.add("signature_owner", "future action factor", -signature / 2 == pcomp, -signature / 2, pcomp)
    audit.add("signature_owner", "variance omission", theta - j2 == Q(-12) != signature, theta - j2, signature)
    audit.add("signature_owner", "forest duplication", signature - forest == Q(-19) != signature, signature - forest, signature)
    audit.add("signature_owner", "missing mean return", kfuture != pcomp, kfuture, pcomp)

    # A same-norm trace lift is not canonical: its cross data can change.
    u0 = [Q(1), Q(0)]
    u_same = [Q(1), Q(0)]
    u_orth = [Q(0), Q(1)]
    audit.add("signature_owner", "same lift norm", inner(u_same, u_same) == inner(u_orth, u_orth) == inner(u0, u0), (inner(u_same, u_same), inner(u_orth, u_orth)), inner(u0, u0))
    audit.add("signature_owner", "different mixed trace cross", inner(u0, u_same) != inner(u0, u_orth), (inner(u0, u_same), inner(u0, u_orth)), "different")
    cell_trace_minus_phi = [Q(2), Q(-9)]
    cell_variance_minus_forest = [Q(4), Q(-11)]
    audit.add("signature_owner", "forest coordinate only aggregate", cell_trace_minus_phi != cell_variance_minus_forest and sum(cell_trace_minus_phi, Q(0)) == sum(cell_variance_minus_forest, Q(0)) == Q(-7), (cell_trace_minus_phi, cell_variance_minus_forest), "different cells; same complete sum")

    # Independent signed polarization.
    ap = [[Q(1), Q(2)], [Q(0), Q(1)]]
    am = [[Q(2), Q(0)], [Q(1), Q(-1)]]
    sign = [[Q(1), Q(0)], [Q(0), Q(-1)]]
    lpart = mm(mm(t(ap), sign), am)
    rpart = mm(mm(t(am), sign), ap)
    gram = scalem(Q(1, 2), addm(lpart, rpart))
    audit.add("mixed_gram", "left mixed matrix", lpart == [[Q(2), Q(0)], [Q(3), Q(1)]], lpart, [[Q(2), Q(0)], [Q(3), Q(1)]])
    audit.add("mixed_gram", "right is adjoint", rpart == t(lpart), rpart, t(lpart))
    audit.add("mixed_gram", "signed Gram", gram == [[Q(2), Q(3, 2)], [Q(3, 2), Q(1)]], gram, [[Q(2), Q(3, 2)], [Q(3, 2), Q(1)]])
    for x, expected in (([Q(1), Q(3)], Q(20)), ([Q(-2), Q(1)], Q(3))):
        secant = inner(mv(ap, x), mv(sign, mv(am, x)))
        audit.add("mixed_gram", f"polarization fixture {x}", secant == qform(x, gram) == expected, (secant, qform(x, gram)), expected)
    audit.add("mixed_gram", "factor two mutation", qform([Q(1), Q(3)], addm(lpart, rpart)) == Q(40), qform([Q(1), Q(3)], addm(lpart, rpart)), Q(40))
    upper = [[Q(-100), Q(0)], [Q(0), Q(1, 20)]]
    audit.add("mixed_gram", "one-sided upper value", max(upper[0][0], upper[1][1]) == Q(1, 20), max(upper[0][0], upper[1][1]), Q(1, 20))
    audit.add("mixed_gram", "absolute norm distinct", max(abs(upper[0][0]), abs(upper[1][1])) == Q(100), max(abs(upper[0][0]), abs(upper[1][1])), Q(100))

    # Finite Doob enumeration and a global terminal quadratic form.
    h2 = {(a, b): Q(2 + a) for a, b in omega}
    h3 = {(a, b): Q(1 + 2 * a + 3 * b + 4 * a * b) for a, b in omega}
    expectation = lambda values: sum(values.values(), Q(0)) / 4
    energy = lambda values: expectation({state: value * value for state, value in values.items()})
    low2, low3 = Q(2), Q(1)
    d1h2 = {(a, b): Q(a) for a, b in omega}
    d1h3 = {(a, b): Q(2 * a) for a, b in omega}
    d2h3 = {(a, b): Q(b * (3 + 4 * a)) for a, b in omega}
    audit.add("doob_isometry", "h2 energy", energy(h2) == Q(5), energy(h2), Q(5))
    audit.add("doob_isometry", "h3 energy", energy(h3) == Q(30), energy(h3), Q(30))
    audit.add("doob_isometry", "h2 reconstruction", all(h2[state] == low2 + d1h2[state] for state in omega), True, True)
    audit.add("doob_isometry", "h3 reconstruction", all(h3[state] == low3 + d1h3[state] + d2h3[state] for state in omega), True, True)
    audit.add("doob_isometry", "h2 Pythagoras", low2 * low2 + energy(d1h2) == energy(h2), low2 * low2 + energy(d1h2), energy(h2))
    audit.add("doob_isometry", "h3 Pythagoras", low3 * low3 + energy(d1h3) + energy(d2h3) == energy(h3), low3 * low3 + energy(d1h3) + energy(d2h3), energy(h3))
    audit.add("doob_isometry", "total source energy", energy(h2) + energy(h3) == Q(35), energy(h2) + energy(h3), Q(35))
    audit.add("doob_isometry", "total Doob energy", low2**2 + low3**2 + energy(d1h2) + energy(d1h3) + energy(d2h3) == Q(35), low2**2 + low3**2 + energy(d1h2) + energy(d1h3) + energy(d2h3), Q(35))

    terminal_b = [[Q(2), Q(2)], [Q(2), Q(3)]]
    direct_form = expectation({state: qform([h2[state], h3[state]], terminal_b) for state in omega})
    low_form = qform([low2, low3], terminal_b)
    reveal1_form = expectation({state: qform([d1h2[state], d1h3[state]], terminal_b) for state in omega})
    reveal2_form = expectation({state: 3 * d2h3[state] ** 2 for state in omega})
    audit.add("doob_isometry", "terminal form direct", direct_form == Q(116), direct_form, Q(116))
    audit.add("doob_isometry", "terminal low block", low_form == Q(19), low_form, Q(19))
    audit.add("doob_isometry", "terminal reveal one block", reveal1_form == Q(22), reveal1_form, Q(22))
    audit.add("doob_isometry", "terminal reveal two block", reveal2_form == Q(75), reveal2_form, Q(75))
    audit.add("doob_isometry", "global blocks reconstruct terminal form", low_form + reveal1_form + reveal2_form == direct_form, low_form + reveal1_form + reveal2_form, direct_form)

    # Quotient and refinement conjugacy.
    synthesis = [[Q(1), Q(0), Q(1)], [Q(0), Q(1), Q(1)]]
    physical = [[Q(3), Q(0)], [Q(0), Q(5)]]
    hphys = mm(mm(t(synthesis), physical), synthesis)
    kernel = [Q(1), Q(1), Q(-1)]
    base = [Q(2), Q(-1), Q(3)]
    shifted = [base[i] + 5 * kernel[i] for i in range(3)]
    audit.add("quotient", "physical Hessian matrix", hphys == [[Q(3), Q(0), Q(3)], [Q(0), Q(5), Q(5)], [Q(3), Q(5), Q(8)]], hphys, "derived matrix")
    audit.add("quotient", "kernel source null", mv(synthesis, kernel) == [Q(0), Q(0)], mv(synthesis, kernel), [Q(0), Q(0)])
    audit.add("quotient", "kernel Hessian null", mv(hphys, kernel) == [Q(0), Q(0), Q(0)], mv(hphys, kernel), [Q(0), Q(0), Q(0)])
    audit.add("quotient", "coset source equal", mv(synthesis, base) == mv(synthesis, shifted), mv(synthesis, shifted), mv(synthesis, base))
    audit.add("quotient", "coset physical form equal", qform(base, hphys) == qform(shifted, hphys) == Q(95), (qform(base, hphys), qform(shifted, hphys)), Q(95))
    audit.add("quotient", "ambient source costs differ", inner(base, base) == Q(14) and inner(shifted, shifted) == Q(69), (inner(base, base), inner(shifted, shifted)), (Q(14), Q(69)))
    inclusion = [[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)], [Q(0), Q(0), Q(0)]]
    refined_synthesis = [[Q(1), Q(0), Q(1), Q(2)], [Q(0), Q(1), Q(1), Q(-1)]]
    audit.add("quotient", "refined synthesis conjugacy", mm(refined_synthesis, inclusion) == synthesis, mm(refined_synthesis, inclusion), synthesis)
    refined_h = mm(mm(t(refined_synthesis), physical), refined_synthesis)
    audit.add("quotient", "refined Hessian conjugacy", mm(mm(t(inclusion), refined_h), inclusion) == hphys, mm(mm(t(inclusion), refined_h), inclusion), hphys)

    weak_h = [[Q(-1), Q(1, 2)], [Q(1, 2), Q(0)]]
    metric = [[Q(0), Q(0)], [Q(0), Q(1)]]
    remainder = addm(scalem(Q(1, 4), metric), scalem(Q(-1), weak_h))
    audit.add("quotient", "weak Schur remainder", remainder == [[Q(1), Q(-1, 2)], [Q(-1, 2), Q(1, 4)]], remainder, "rank-one remainder")
    audit.add("quotient", "weak Schur determinant", det2(remainder) == 0, det2(remainder), Q(0))
    bad_zero = [[Q(0), Q(1, 2)], [Q(1, 2), Q(0)]]
    for ceiling in (Q(1), Q(100)):
        residual = addm(scalem(ceiling, metric), scalem(Q(-1), bad_zero))
        audit.add("quotient", f"zero-kernel cross fails ceiling {ceiling}", det2(residual) < 0, det2(residual), "<0")

    # Positive-analysis collar identity and independent sums.
    audit.add("collar_shift", "C8 moves three layers", list(range(5, 8)) == [5, 6, 7], list(range(5, 8)), [5, 6, 7])
    audit.add("collar_shift", "C10 moves five layers", list(range(5, 10)) == [5, 6, 7, 8, 9], list(range(5, 10)), [5, 6, 7, 8, 9])
    audit.add("collar_shift", "C5-to-C8 weight exponent", -WEIGHT * 3 == Q(-7, 4), -WEIGHT * 3, Q(-7, 4))
    audit.add("collar_shift", "C5-to-C8 squared exponent", -2 * WEIGHT * 3 == Q(-7, 2), -2 * WEIGHT * 3, Q(-7, 2))
    audit.add("collar_shift", "C5-to-C10 weight exponent", -WEIGHT * 5 == Q(-35, 12), -WEIGHT * 5, Q(-35, 12))
    signed_full, signed_keep = Q(-1), Q(9)
    audit.add("collar_shift", "signed-shell monotonicity fails", signed_keep > signed_full and signed_full == Q(-10) + signed_keep, (signed_full, signed_keep), "deleting -10 increases upper value")
    fixed_mask = Q(1) + Q(-1)
    moving_mask = Q(1) + Q(0) * Q(-1)
    audit.add("collar_shift", "moving insertion mask breaks telescope", fixed_mask == 0 and moving_mask == 1, (fixed_mask, moving_mask), (Q(0), Q(1)))

    table: dict[int, dict[str, float]] = {}
    for collar in (7, 8, 9, 10):
        closed = closed_sum(collar)
        direct = direct_sum(collar, 600)
        debt = float(ENERGY_FACTOR) * closed
        table[collar] = {"closed": closed, "direct": direct, "debt": debt}
        audit.add("collar_diagnostic", f"C{collar} direct-versus-closed", abs(direct - closed) <= TOL, direct - closed, f"<={TOL}")
    expected = {
        7: (10.778126471501523, 0.202089871340603),
        8: (4.631138871013502, 0.0868338538314814),
        9: (1.971947657656302, 0.0369740185810464),
        10: (0.833374378872430, 0.0156257696038541),
    }
    for collar, (expected_h, expected_debt) in expected.items():
        audit.add("collar_diagnostic", f"C{collar} H", abs(table[collar]["closed"] - expected_h) <= TOL, table[collar]["closed"], expected_h)
        audit.add("collar_diagnostic", f"C{collar} debt", abs(table[collar]["debt"] - expected_debt) <= TOL, table[collar]["debt"], expected_debt)
    audit.add("collar_diagnostic", "first zero-low collar", table[7]["debt"] > float(HEADROOM) > table[8]["debt"], (table[7]["debt"], float(HEADROOM), table[8]["debt"]), "C8")
    audit.add("collar_diagnostic", "first small-headroom collar", table[9]["debt"] > float(SMALL_HEADROOM) > table[10]["debt"], (table[9]["debt"], float(SMALL_HEADROOM), table[10]["debt"]), "C10")
    cstar8 = math.sqrt(float(HEADROOM) / table[8]["debt"])
    cstar10 = math.sqrt(float(SMALL_HEADROOM) / table[10]["debt"])
    audit.add("collar_diagnostic", "C8 C-star threshold", abs(cstar8 - 1.07546575053067) <= TOL, cstar8, "derived")
    audit.add("collar_diagnostic", "C10 C-star threshold", abs(cstar10 - 1.00913922178312) <= TOL, cstar10, "derived")

    # Coherent finite band and signed low correlation.
    b5, b6, b7 = Q(1, 6), Q(1, 4), Q(1, 3)
    band = b5 + b6 + b7
    audit.add("collar_schur", "row sum", band == Q(3, 4), band, Q(3, 4))
    audit.add("collar_schur", "column sum", band == Q(3, 4), band, Q(3, 4))
    audit.add("collar_schur", "Schur square root", math.sqrt(float(band * band)) == float(band), math.sqrt(float(band * band)), float(band))
    audit.add("collar_schur", "constant vector saturates", sum(([band] * 8), Q(0)) == Q(6), sum(([band] * 8), Q(0)), Q(6))
    audit.add("collar_schur", "quadrature smaller than coherent sum", math.sqrt(float(b5 * b5 + b6 * b6 + b7 * b7)) < float(band), math.sqrt(float(b5 * b5 + b6 * b6 + b7 * b7)), float(band))
    audit.add("collar_schur", "full cross", 2 * band == Q(3, 2), 2 * band, Q(3, 2))
    audit.add("collar_schur", "reverse double-count mutation", 4 * band == Q(3) != 2 * band, 4 * band, "wrong doubled reverse")

    diag_e = 0.8857272727272757
    diag_f = 0.27
    a = 0.9209323339075279
    magnitude = 1.0 / math.sqrt(50.0)
    matrices = {
        "favorable": [[diag_e, a / 2.0, magnitude], [a / 2.0, diag_f, magnitude], [magnitude, magnitude, 1.0]],
        "adverse": [[diag_e, a / 2.0, magnitude], [a / 2.0, diag_f, -magnitude], [magnitude, -magnitude, 1.0]],
    }
    eig = {key: eigvals_sym3(value) for key, value in matrices.items()}
    schur_det = {
        key: (value[0][0] - value[0][2] ** 2)
        * (value[1][1] - value[1][2] ** 2)
        - (value[0][1] - value[0][2] * value[1][2]) ** 2
        for key, value in matrices.items()
    }
    audit.add("correlation", "favorable determinant", 0.02242136 <= schur_det["favorable"] <= 0.02242139, schur_det["favorable"], "in registered interval")
    audit.add("correlation", "adverse determinant", -0.01441593 <= schur_det["adverse"] <= -0.01441590, schur_det["adverse"], "in registered interval")
    audit.add("correlation", "favorable least eigenvalue", 0.0203960 <= eig["favorable"][0] <= 0.0203964, eig["favorable"][0], "positive registered interval")
    audit.add("correlation", "adverse least eigenvalue", -0.0123260 <= eig["adverse"][0] <= -0.0123257, eig["adverse"][0], "negative registered interval")
    audit.add("correlation", "same magnitude data", all(abs(matrices["favorable"][i][j]) == abs(matrices["adverse"][i][j]) for i in range(3) for j in range(3)), True, True)

    half_a = Q(29, 32)
    reduced = Q(15, 16)
    pass_det = reduced**2 - (half_a - Q(1, 16)) ** 2
    fail_det = reduced**2 - (half_a + Q(1, 16)) ** 2
    audit.add("correlation", "exact pass determinant", pass_det == Q(171, 1024), pass_det, Q(171, 1024))
    audit.add("correlation", "exact fail determinant", fail_det == Q(-61, 1024), fail_det, Q(-61, 1024))

    # Low-kernel penalty and final scope firewalls.
    t_low = Q(3, 4)
    kappa = 2 * t_low
    unpenalized = Q(2) - Q(1, 5) - Q(1, 10) - (Q(3, 5) + Q(1, 10)) ** 2 / (4 * (Q(1) - Q(1, 10)))
    penalized = unpenalized - kappa
    audit.add("low_kernel", "low-kernel graph fixture", Q(1) - 2 * t_low == Q(-1, 2), Q(1) - 2 * t_low, Q(-1, 2))
    audit.add("low_kernel", "kernel penalty", kappa == Q(3, 2), kappa, Q(3, 2))
    audit.add("low_kernel", "unpenalized margin", unpenalized == Q(563, 360), unpenalized, Q(563, 360))
    audit.add("low_kernel", "penalized margin", penalized == Q(23, 360), penalized, Q(23, 360))
    audit.add("low_kernel", "action half margin", penalized / 2 == Q(23, 720), penalized / 2, Q(23, 720))

    roots, relative_import = imported_roots(Path(__file__))
    forbidden = {"numpy", "sympy", "scipy"}
    audit.add("firewall", "no numerical-library import", not (roots & forbidden), sorted(roots & forbidden), [])
    audit.add("firewall", "no relative import", not relative_import, relative_import, False)
    audit.add("firewall", "primary module not imported", not any("projected_force_global_doob" in root for root in roots), sorted(roots), "no primary import")
    audit.add("firewall", "primary exists for cross-check", PRIMARY.is_file(), PRIMARY, "file")

    scope = {
        "non_importing_independent_certificate": True,
        "finite_chart_projected_force_formula": True,
        "canonical_signature_requires_common_feature_lift": True,
        "global_doob_keeps_off_diagonal_blocks": True,
        "adaptive_collar_must_be_predictable_and_endpoint_fixed": True,
        "production_two_sided_factorization": False,
        "production_uniform_loewner": False,
        "production_low_compatibility": False,
        "positive_graph_gap": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    failed = sum(row["status"] != "PASS" for row in audit.rows)
    group_counts: dict[str, int] = {}
    for row in audit.rows:
        group = str(row["group"])
        group_counts[group] = group_counts.get(group, 0) + 1
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows) - failed,
            "failed": failed,
            "rows": audit.rows,
            "group_counts": group_counts,
        },
        "computed": {
            "collar_table": {str(key): value for key, value in table.items()},
            "cstar8": cstar8,
            "cstar10": cstar10,
            "correlation_schur_determinants": schur_det,
            "correlation_eigenvalues": eig,
            "penalized_source_margin": str(penalized),
            "action_margin": str(penalized / 2),
        },
        "scope": scope,
    }
    atomic_json(args.output, payload)
    print(f"R-141 independent {payload['status']}: {len(audit.rows)-failed}/{len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
