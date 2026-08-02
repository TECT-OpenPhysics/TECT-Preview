#!/usr/bin/env python3
"""Independent standard-library certificate for the scoped A13 R-144 result.

This implementation does not import the primary certificate and does not use
NumPy, SymPy, or SciPy.  All arithmetic is exact Fraction arithmetic.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-"
    "LOW-COMPLETION-BOUNDARY"
)
SCHEMA = (
    "tect/a13-uniform-douglas-one-use-projected-force-"
    "low-completion-boundary-independent/1.0"
)
SLUG = "uniform-douglas-one-use-projected-force-low-completion-boundary"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / f"runs/2026-08-02-independent-{SLUG}/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
GATES_PATH = REPO / "claims/GATES.md"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
Q = Fraction


# Registered or explicitly selected analytic inputs.  comparison_p is the
# declared T-050 comparison exponent; fixture inputs below are synthetic
# counterexample parameters and never production outputs.
REGISTERED_ANALYTIC_INPUTS = {
    "comparison_p": Q(11, 10),
    "nelson_q": Q(10, 9),
    "sextic_stabilizer": Q(3, 20),
}
FIXTURE_INPUTS = {
    "rho": Q(1, 2),
    "sigma": Q(3, 4),
    "residual": Q(2),
    "mu": Q(1, 5),
    "theta": Q(1, 2),
    "force_squared": Q(3, 7),
    "fibre_r": Q(7, 5),
    "fibre_s": Q(3, 4),
    "fibre_floor": Q(1, 9),
    "layer_edge": Q(3, 4),
    "returned_low_core_cross": Q(29, 32),
}


# Regression oracles only; all coefficients used in formulas are derived.
TEST_ORACLES = {
    "phase_dets": (Q(5, 32), Q(-49, 32)),
    "low_dets": (Q(171, 1024), Q(-61, 1024)),
    "double_count_det": Q(-585, 256),
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, col)) for col in right_t] for row in left]


def matadd(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum(a * b for a, b in zip(left, right))


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    size = len(matrix)
    if size == 0:
        return Q(1)
    work = [row[:] for row in matrix]
    sign = Q(1)
    det = Q(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Q(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        det *= value
        for row in range(column + 1, size):
            factor = work[row][column] / value
            for entry in range(column + 1, size):
                work[row][entry] -= factor * work[column][entry]
        
    return sign * det


def exact_ldl_inertia(matrix: list[list[Fraction]]) -> tuple[int, int, int]:
    """Exact inertia when every leading principal minor is nonzero."""
    previous = Q(1)
    positive = negative = 0
    for size in range(1, len(matrix) + 1):
        current = determinant([row[:size] for row in matrix[:size]])
        if current == 0:
            raise ValueError("zero leading pivot in exact LDL inertia")
        pivot = current / previous
        if pivot > 0:
            positive += 1
        elif pivot < 0:
            negative += 1
        else:
            raise ValueError("undecidable exact pivot sign")
        previous = current
    return positive, negative, len(matrix) - positive - negative


def tensor_inertia(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, int, int]:
    lp, ln, lz = left
    rp, rn, rz = right
    positive = lp * rp + ln * rn
    negative = lp * rn + ln * rp
    zero = (lp + ln + lz) * (rp + rn + rz) - positive - negative
    return positive, negative, zero


def identity(size: int) -> list[list[Fraction]]:
    return [[Q(int(i == j)) for j in range(size)] for i in range(size)]


def polynomial_square(coefficients: list[Fraction]) -> list[Fraction]:
    result = [Q(0)] * (2 * len(coefficients) - 1)
    for i, left in enumerate(coefficients):
        for j, right in enumerate(coefficients):
            result[i + j] += left * right
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    a1 = load_json(A1_MANIFEST)
    gates_text = GATES_PATH.read_text(encoding="utf-8")
    gate_heading = "### **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE**"
    gate_start = gates_text.index(gate_heading)
    gate_tail = gates_text[gate_start:]
    gate_stop = gate_tail.find("\n### ", len(gate_heading))
    t050_gate_text = gate_tail if gate_stop < 0 else gate_tail[:gate_stop]
    audit.add(
        "authority",
        "A1 manifest",
        a1.get("claim_id") == "A1-PRODUCTION-FUNCTIONAL-REALISATION",
        a1.get("claim_id"),
        "A1-PRODUCTION-FUNCTIONAL-REALISATION",
    )
    audit.add(
        "authority",
        "canonical T-050 sextic threshold pinned",
        "epsilon_6<gamma/6=0.27" in t050_gate_text,
        "epsilon_6<gamma/6=0.27" in t050_gate_text,
        True,
    )
    audit.add(
        "authority",
        "canonical T-050 source threshold pinned",
        "epsilon_v<1/(2p)" in t050_gate_text,
        "epsilon_v<1/(2p)" in t050_gate_text,
        True,
    )
    audit.add("firewall", "primary file exists", PRIMARY.is_file(), PRIMARY, "file")

    # 1. Sharp affine-residual inequality and one-use coefficients.
    rho = FIXTURE_INPUTS["rho"]
    sigma = FIXTURE_INPUTS["sigma"]
    residual = FIXTURE_INPUTS["residual"]
    delta = sigma**2 - rho**2
    sharp = sigma**2 / delta
    audit.add(
        "affine_residual",
        "strict radii",
        Q(0) <= rho < sigma < 1,
        (rho, sigma),
        "0 <= rho < sigma < 1",
    )
    audit.add(
        "affine_residual", "sharp constant", sharp == Q(9, 5), sharp, Q(9, 5)
    )
    gap_coefficients = (
        delta,
        -2 * rho * residual,
        (sharp - 1) * residual**2,
    )
    square_coefficients = (
        delta,
        -2 * rho * residual,
        rho**2 * residual**2 / delta,
    )
    audit.add(
        "affine_residual",
        "universal polynomial square identity",
        gap_coefficients == square_coefficients,
        gap_coefficients,
        square_coefficients,
    )
    for index, value in enumerate([Q(0), Q(1), Q(16, 5), Q(7), Q(31, 3)]):
        gap = sigma**2 * value**2 + sharp * residual**2 - (rho * value + residual) ** 2
        square = (delta * value - rho * residual) ** 2 / delta
        audit.add(
            "affine_residual",
            f"exact square identity sample {index}",
            gap == square >= 0,
            gap,
            square,
        )
    equality_y = rho * residual / delta
    audit.add(
        "affine_residual",
        "sharp equality direction",
        (rho * equality_y + residual) ** 2
        == sigma**2 * equality_y**2 + sharp * residual**2,
        equality_y,
        Q(16, 5),
    )
    comparison_p = REGISTERED_ANALYTIC_INPUTS["comparison_p"]
    nelson_q = REGISTERED_ANALYTIC_INPUTS["nelson_q"]
    source_weight = Q(1, 2) / nelson_q
    canonical_source_threshold = Q(1, 2) / comparison_p
    source_hessian_weight = 2 * source_weight
    sextic_weight = REGISTERED_ANALYTIC_INPUTS["sextic_stabilizer"]
    gamma = frac(a1["parameters"]["gamma"])
    eps_source = source_weight * sigma**2
    eps_sextic = sextic_weight * sigma**2
    audit.add(
        "one_use",
        "Nelson and comparison exponents",
        nelson_q - comparison_p == Q(1, 90),
        nelson_q - comparison_p,
        Q(1, 90),
    )
    audit.add(
        "one_use",
        "stronger q-source target clears canonical p-threshold",
        source_weight == Q(9, 20)
        and source_weight < canonical_source_threshold
        and canonical_source_threshold - source_weight == Q(1, 220),
        (source_weight, canonical_source_threshold),
        (Q(9, 20), Q(5, 11)),
    )
    audit.add(
        "one_use",
        "source coefficient strict",
        eps_source == Q(81, 320) < source_weight < canonical_source_threshold,
        eps_source,
        Q(81, 320),
    )
    audit.add(
        "one_use",
        "sextic coefficient strict",
        eps_sextic == Q(27, 320) < sextic_weight < gamma / 6,
        eps_sextic,
        Q(27, 320),
    )
    audit.add(
        "one_use",
        "residual action penalty",
        sharp * residual**2 / 2 == Q(18, 5),
        sharp * residual**2 / 2,
        Q(18, 5),
    )

    mu = FIXTURE_INPUTS["mu"]
    theta = FIXTURE_INPUTS["theta"]
    force_sq = FIXTURE_INPUTS["force_squared"]
    fallback_source = source_weight - (1 - theta) * mu / 2
    fallback_constant = force_sq / (2 * theta * mu)
    audit.add(
        "hessian_fallback",
        "source gap improvement",
        fallback_source == Q(2, 5),
        fallback_source,
        Q(2, 5),
    )
    audit.add(
        "hessian_fallback",
        "origin force penalty",
        fallback_constant == Q(15, 7),
        fallback_constant,
        Q(15, 7),
    )
    audit.add(
        "hessian_fallback",
        "retained sextic is strictly admissible",
        sextic_weight == Q(3, 20) < gamma / 6
        and gamma / 6 - sextic_weight == Q(3, 25),
        (sextic_weight, gamma / 6 - sextic_weight),
        (Q(3, 20), Q(3, 25)),
    )

    # 2. Exact endpoint factor-two oracle on an affine feature chart.
    y0 = [Q(1), Q(2)]
    u0 = [Q(1, 2)]
    dy = [[Q(1), Q(1)], [Q(0), Q(1)]]  # columns are feature increments
    du = [[Q(1, 2), Q(-1, 2)]]
    gram = matadd(matmul(transpose(dy), dy), [[-x for x in row] for row in matmul(transpose(du), du)])
    baseline = [
        dot(y0, [dy[row][column] for row in range(2)])
        - dot(u0, [du[row][column] for row in range(1)])
        for column in range(2)
    ]
    a0 = Q(1, 2) * (dot(y0, y0) - dot(u0, u0))
    audit.add("secant", "baseline action", a0 == Q(19, 8), a0, Q(19, 8))
    audit.add(
        "secant",
        "linear owner",
        baseline == [Q(3, 4), Q(13, 4)],
        baseline,
        [Q(3, 4), Q(13, 4)],
    )
    audit.add(
        "secant",
        "action Hessian",
        gram == [[Q(3, 4), Q(5, 4)], [Q(5, 4), Q(7, 4)]],
        gram,
        [[Q(3, 4), Q(5, 4)], [Q(5, 4), Q(7, 4)]],
    )
    coefficients = [Q(2), Q(-1)]
    a_sec = a0 + dot(baseline, coefficients) + Q(1, 2) * dot(coefficients, matvec(gram, coefficients))
    audit.add("secant", "test endpoint action", a_sec == Q(1, 2), a_sec, Q(1, 2))
    audit.add(
        "secant",
        "mixed difference is A Hessian entry",
        gram[0][1] == Q(5, 4),
        gram[0][1],
        Q(5, 4),
    )
    audit.add(
        "secant",
        "twice-action mixed difference",
        2 * gram[0][1] == Q(5, 2),
        2 * gram[0][1],
        Q(5, 2),
    )

    # 3. Source kernel, graph-low mutation, and refinement congruence.
    source_hessian = [
        [Q(29, 10), Q(1, 3), Q(0)],
        [Q(1, 3), Q(2, 5), Q(0)],
        [Q(0), Q(0), source_hessian_weight],
    ]
    vertical = [Q(0), Q(0), Q(1)]
    audit.add(
        "source_typing",
        "vertical complete Hessian",
        matvec(source_hessian, vertical) == [Q(0), Q(0), source_hessian_weight],
        matvec(source_hessian, vertical),
        [Q(0), Q(0), source_hessian_weight],
    )
    good_low = [Q(1, 4), Q(-1, 5), Q(0)]
    bad_low = [Q(1, 4), Q(-1, 5), Q(1, 7)]
    audit.add(
        "source_typing",
        "independent low kills source kernel",
        dot(vertical, good_low) == 0,
        dot(vertical, good_low),
        0,
    )
    audit.add(
        "source_typing",
        "graph-low mutation sees source kernel",
        dot(vertical, bad_low) == Q(1, 7),
        dot(vertical, bad_low),
        Q(1, 7),
    )
    bad_null = [[Q(0), Q(1, 7)], [Q(1, 7), Q(1)]]
    audit.add(
        "source_typing",
        "source-null range failure",
        determinant(bad_null) == Q(-1, 49),
        determinant(bad_null),
        Q(-1, 49),
    )

    inclusion = [[Q(1), Q(0)], [Q(0), Q(3, 5)], [Q(0), Q(4, 5)]]
    delta_u_f = [[Q(1, 2), Q(1, 3), Q(1, 4)]]
    gram_f = matadd(identity(3), [[-x for x in row] for row in matmul(transpose(delta_u_f), delta_u_f)])
    gram_c = matmul(transpose(inclusion), matmul(gram_f, inclusion))
    audit.add(
        "refinement",
        "isometric inclusion",
        matmul(transpose(inclusion), inclusion) == identity(2),
        matmul(transpose(inclusion), inclusion),
        identity(2),
    )
    audit.add(
        "refinement",
        "exact congruence",
        gram_c == [[Q(3, 4), Q(-1, 5)], [Q(-1, 5), Q(21, 25)]],
        gram_c,
        [[Q(3, 4), Q(-1, 5)], [Q(-1, 5), Q(21, 25)]],
    )
    audit.add(
        "refinement",
        "coarse determinant",
        determinant(gram_c) == Q(59, 100),
        determinant(gram_c),
        Q(59, 100),
    )

    # 4. q567 phase cycle and registered active fibre positivity.
    parameters = a1["parameters"]
    p_mass = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    aa = frac(parameters["cJJ"]) * frac(parameters["alpha_X"]) ** 2 / p_mass
    cb = frac(parameters["cJK"]) * frac(parameters["alpha_X"]) * frac(parameters["beta_X"]) / p_mass
    cc = frac(parameters["cKK"]) * frac(parameters["beta_X"]) ** 2 / p_mass
    c0 = aa - cb**2 / cc
    c1 = (cb + cc) ** 2 / cc
    alpha = cc / (cb + cc)
    r = FIXTURE_INPUTS["fibre_r"]
    s = FIXTURE_INPUTS["fibre_s"]
    floor = FIXTURE_INPUTS["fibre_floor"]
    audit.add(
        "phase_cycle",
        "registered fibre coefficients and audit point",
        c0 == Q(3, 250) / p_mass
        and c1 == Q(243, 8000) / p_mass
        and alpha == Q(5, 9)
        and (r, s, floor) == (Q(7, 5), Q(3, 4), Q(1, 9)),
        (c0, c1, alpha, r, s, floor),
        (Q(3, 250) / p_mass, Q(243, 8000) / p_mass, Q(5, 9), Q(7, 5), Q(3, 4), Q(1, 9)),
    )
    ratio = r * r / (r * r + s * s + floor)
    transverse = Q(4) * (c0 + c1) * r * r
    radial_a = Q(4) * r * r * (c0 + c1 * (1 - alpha * ratio) ** 2)
    radial_c = Q(-4) * c1 * alpha * ratio * (1 - alpha * ratio) * r * s
    radial_d = Q(4) * c1 * alpha**2 * ratio**2 * s**2
    radial_det = radial_a * radial_d - radial_c**2
    fibre = [
        [transverse, Q(0), Q(0), Q(0)],
        [Q(0), transverse, Q(0), Q(0)],
        [Q(0), Q(0), radial_a, radial_c],
        [Q(0), Q(0), radial_c, radial_d],
    ]
    audit.add(
        "phase_cycle",
        "active fibre positive",
        transverse > 0 and radial_a > 0 and radial_det > 0,
        (transverse, radial_det),
        "positive",
    )
    layer_edge = FIXTURE_INPUTS["layer_edge"]
    layer_plus = [
        [Q(1), layer_edge, layer_edge],
        [layer_edge, Q(1), layer_edge],
        [layer_edge, layer_edge, Q(1)],
    ]
    layer_minus = [
        [Q(1), layer_edge, layer_edge],
        [layer_edge, Q(1), -layer_edge],
        [layer_edge, -layer_edge, Q(1)],
    ]
    audit.add(
        "phase_cycle",
        "same entry magnitudes",
        all(abs(layer_plus[i][j]) == abs(layer_minus[i][j]) for i in range(3) for j in range(3)),
        True,
        True,
    )
    cycle_products = (
        layer_plus[0][1] * layer_plus[1][2] * layer_plus[2][0],
        layer_minus[0][1] * layer_minus[1][2] * layer_minus[2][0],
    )
    audit.add(
        "phase_cycle",
        "opposite gauge-invariant cycle",
        cycle_products == (Q(27, 64), Q(-27, 64)),
        cycle_products,
        (Q(27, 64), Q(-27, 64)),
    )
    phase_dets = (determinant(layer_plus), determinant(layer_minus))
    audit.add(
        "phase_cycle",
        "opposite determinant signs",
        phase_dets == TEST_ORACLES["phase_dets"],
        phase_dets,
        TEST_ORACLES["phase_dets"],
    )
    plus_minors = (
        layer_plus[0][0],
        determinant([row[:2] for row in layer_plus[:2]]),
        determinant(layer_plus),
    )
    minus_minors = (
        layer_minus[0][0],
        determinant([row[:2] for row in layer_minus[:2]]),
        determinant(layer_minus),
    )
    audit.add(
        "phase_cycle",
        "positive layer Sylvester data",
        plus_minors == (Q(1), Q(7, 16), Q(5, 32)),
        plus_minors,
        (Q(1), Q(7, 16), Q(5, 32)),
    )
    audit.add(
        "phase_cycle",
        "adverse layer inertia data",
        minus_minors[:2] == (Q(1), Q(7, 16)) and minus_minors[2] < 0,
        minus_minors,
        "two positive LDL pivots and one negative",
    )
    fibre_inertia = exact_ldl_inertia(fibre)
    layer_plus_inertia = exact_ldl_inertia(layer_plus)
    layer_minus_inertia = exact_ldl_inertia(layer_minus)
    h_plus_inertia = tensor_inertia(layer_plus_inertia, fibre_inertia)
    h_minus_inertia = tensor_inertia(layer_minus_inertia, fibre_inertia)
    audit.add(
        "phase_cycle",
        "positive completion inertia",
        h_plus_inertia == (12, 0, 0),
        h_plus_inertia,
        (12, 0, 0),
    )
    audit.add(
        "phase_cycle",
        "adverse completion inertia",
        h_minus_inertia == (8, 4, 0),
        h_minus_inertia,
        (8, 4, 0),
    )
    mixed = [[Q(int(i == j)) - Q(3, 8) for j in range(3)] for i in range(3)]
    audit.add(
        "phase_cycle",
        "positive diagonal mixed fixture",
        [mixed[i][i] for i in range(3)] == [Q(5, 8)] * 3,
        [mixed[i][i] for i in range(3)],
        [Q(5, 8)] * 3,
    )
    audit.add(
        "phase_cycle",
        "mixed fixture adverse",
        determinant(mixed) == Q(-1, 8),
        determinant(mixed),
        Q(-1, 8),
    )
    audit.add(
        "phase_cycle",
        "mixed generalized edge",
        Q(3, 8) * 3 == Q(9, 8),
        Q(3, 8) * 3,
        Q(9, 8),
    )

    # 5. Returned low and legal-reverse one-owner factor.
    half_cross = FIXTURE_INPUTS["returned_low_core_cross"]
    core = [[Q(1), half_cross], [half_cross, Q(1)]]
    plus_low = [
        [Q(1), half_cross, Q(1, 4)],
        [half_cross, Q(1), Q(1, 4)],
        [Q(1, 4), Q(1, 4), Q(1)],
    ]
    minus_low = [
        [Q(1), half_cross, Q(1, 4)],
        [half_cross, Q(1), Q(-1, 4)],
        [Q(1, 4), Q(-1, 4), Q(1)],
    ]
    audit.add(
        "returned_low",
        "positive core determinant",
        determinant(core) == Q(183, 1024),
        determinant(core),
        Q(183, 1024),
    )
    audit.add(
        "returned_low",
        "same low completion magnitudes",
        all(abs(plus_low[i][j]) == abs(minus_low[i][j]) for i in range(3) for j in range(3)),
        True,
        True,
    )
    low_dets = (determinant(plus_low), determinant(minus_low))
    audit.add(
        "returned_low",
        "opposite low verdicts",
        low_dets == TEST_ORACLES["low_dets"],
        low_dets,
        TEST_ORACLES["low_dets"],
    )
    double_count = [[Q(1), 2 * half_cross], [2 * half_cross, Q(1)]]
    audit.add(
        "returned_low",
        "legal reverse double count fails",
        determinant(double_count) == TEST_ORACLES["double_count_det"],
        determinant(double_count),
        TEST_ORACLES["double_count_det"],
    )

    # 6. Same base/first jet but opposite true nonlinear Hessians.
    u_poly = [Q(0), Q(1)]
    phi_plus = [Q(1), Q(1), Q(1)]
    phi_minus = [Q(1), Q(1), Q(-1)]
    u_square = polynomial_square(u_poly)
    plus_square = polynomial_square(phi_plus)
    minus_square = polynomial_square(phi_minus)
    length = max(len(u_square), len(plus_square), len(minus_square))
    u_square += [Q(0)] * (length - len(u_square))
    plus_square += [Q(0)] * (length - len(plus_square))
    minus_square += [Q(0)] * (length - len(minus_square))
    raw_plus = [u_square[i] - plus_square[i] for i in range(length)]
    raw_minus = [u_square[i] - minus_square[i] for i in range(length)]
    raw_hessians = (2 * raw_plus[2], 2 * raw_minus[2])
    action_hessians = tuple(-value / 2 for value in raw_hessians)
    audit.add(
        "second_jet",
        "same bases and first jets",
        phi_plus[:2] == phi_minus[:2] == [Q(1), Q(1)],
        (phi_plus[:2], phi_minus[:2]),
        ([Q(1), Q(1)], [Q(1), Q(1)]),
    )
    audit.add(
        "second_jet",
        "opposite raw Hessians",
        raw_hessians == (Q(-4), Q(4)),
        raw_hessians,
        (Q(-4), Q(4)),
    )
    audit.add(
        "second_jet",
        "action sign-half conversion",
        action_hessians == (Q(2), Q(-2)),
        action_hessians,
        (Q(2), Q(-2)),
    )
    full_hessians = tuple(value + source_hessian_weight for value in action_hessians)
    audit.add(
        "second_jet",
        "full action still has opposite signs",
        full_hessians == (Q(29, 10), Q(-11, 10)),
        full_hessians,
        (Q(29, 10), Q(-11, 10)),
    )
    chord_hessians = (
        (sum(phi_plus) - phi_plus[0]) ** 2 - Q(1),
        (sum(phi_minus) - phi_minus[0]) ** 2 - Q(1),
    )
    audit.add(
        "second_jet",
        "signed feature-chord quadratic values",
        chord_hessians == (Q(3), Q(-1)),
        chord_hessians,
        (Q(3), Q(-1)),
    )
    audit.add(
        "second_jet",
        "finite chord is not local Hessian",
        chord_hessians != action_hessians,
        (chord_hessians, action_hessians),
        "different",
    )

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(audit.rows) else "FAIL",
        "tier": "T4",
        "authority_hashes": {"A1": sha256(A1_MANIFEST), "GATES": sha256(GATES_PATH)},
        "implementation": {
            "imports_primary": False,
            "third_party_dependencies": [],
            "arithmetic": "fractions.Fraction only",
        },
        "exact_values": {
            "test_rho": str(rho),
            "test_sigma": str(sigma),
            "sharp_residual_constant": str(sharp),
            "test_epsilon_source": str(eps_source),
            "test_epsilon_sextic": str(eps_sextic),
            "comparison_p": str(comparison_p),
            "nelson_q": str(nelson_q),
            "canonical_source_threshold": str(canonical_source_threshold),
            "q_source_target": str(source_weight),
            "source_threshold_margin": str(canonical_source_threshold - source_weight),
            "hessian_epsilon_source": str(fallback_source),
            "hessian_epsilon_sextic": str(sextic_weight),
            "hessian_sextic_margin": str(gamma / 6 - sextic_weight),
            "fibre_c0": str(c0),
            "fibre_c1": str(c1),
            "fibre_alpha": str(alpha),
            "fibre_audit_point": [str(r), str(s), str(floor)],
            "phase_cycle_determinants": [str(value) for value in phase_dets],
            "phase_cycle_inertia": [list(h_plus_inertia), list(h_minus_inertia)],
            "returned_low_determinants": [str(value) for value in low_dets],
            "double_count_determinant": str(determinant(double_count)),
            "same_jet_action_hessians": [str(value) for value in action_hessians],
            "same_jet_full_action_hessians": [str(value) for value in full_hessians],
        },
        "scope": {
            "affine_residual_one_use_theorem_reproduced": True,
            "hessian_sufficient_condition_reproduced": True,
            "source_low_typing_reproduced": True,
            "endpoint_factor_two_reproduced": True,
            "refinement_congruence_reproduced": True,
            "phase_cycle_nonidentifiability_reproduced": True,
            "returned_low_nonidentifiability_reproduced": True,
            "second_jet_nonidentifiability_reproduced": True,
            "production_bound_proved": False,
            "production_origin_force_bound_proved": False,
            "t050_closed": False,
            "sector_a_closed": False,
        },
        "assertions": {
            "passed": passed,
            "failed": len(audit.rows) - passed,
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "no_overclaim": (
            "This independent exact certificate reproduces the conditional R-144 theorem "
            "and its information boundaries.  It supplies no production chart, common-output "
            "contraction, bounded low residual, anchor, production Hessian gap, origin-force "
            "bound, T-050 closure, or Sector-A closure."
        ),
    }
    atomic_json(args.output, payload)
    print(f"R-144 independent: {passed}/{len(audit.rows)} PASS")
    print(f"output: {args.output}")
    return 0 if passed == len(audit.rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
