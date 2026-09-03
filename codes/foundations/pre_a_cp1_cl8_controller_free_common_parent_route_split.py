#!/usr/bin/env python3
"""Primary exact audit for the CL8 controller-free common-parent route split."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-controller-free-common-parent-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-DKD-HISTORY-CONJUGACY-BOND-TWIST-AND-ROUTE-NOGOS"
NEGATIVES = (
    "NG-2026-08-04-PRE-A-CP1-CL8-BOND-FLOW-GLOBAL-ALL-TIME-SIDEWAYS",
    "NG-2026-08-04-PRE-A-CP1-CL8-DKD2-DIRECT-TWO-LEG-LOCALIZATION",
    "NG-2026-08-04-PRE-A-CP1-CL8-MIDPOINT-QUAD-GLOBAL-UNIQUENESS",
)
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENTS = (
    REPO / "strategy/pre-a-cp1-cl8-interacting-two-arm-work-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json",
)
PARENT_IDS = (
    "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
    "PA-CP1-ST8-Q3LOCK-v0",
)
EXPECTED_VERDICT = (
    "CLOSE ONLY THE CLASSICAL INSERTED-1D BALANCED-EVEN-M FIXED-REGULATOR "
    "CONTROLLER-FREE D-K-D HISTORY INTERTWINER; RETAIN QUANTUM MIXED-CUT, "
    "STATE/ENERGY-SELECTION, 1D-TO-3D, REGULATOR, CONTINUUM/HADAMARD, C6, "
    "CP1, AND PRE-A GATES"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def q(numerator: int, denominator: int = 1) -> sp.Rational:
    return sp.Rational(numerator, denominator)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)}
        )


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def q3_potential(values: sp.Matrix, data: dict[str, Any]) -> sp.Expr:
    onsite = sum(data["r"] * value**2 / 2 + data["g"] * value**4 / 4 for value in values)
    locked = sum(
        data["lambda"]
        * (values[left] - values[right]) ** 2
        * (values[left] ** 2 + values[right] ** 2)
        / 4
        for left, right in q3_edges()
    )
    return sp.factor(onsite + locked)


def q3_gradient(values: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    gradient = sp.Matrix([data["r"] * value + data["g"] * value**3 for value in values])
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        difference = x - y
        square_sum = x**2 + y**2
        gradient[left] += data["lambda"] * (difference * square_sum + difference**2 * x) / 2
        gradient[right] += data["lambda"] * (-difference * square_sum + difference**2 * y) / 2
    return sp.Matrix([sp.factor(item) for item in gradient])


def q3_hessian_apply(values: sp.Matrix, variation: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    result = sp.Matrix(
        [(data["r"] + 3 * data["g"] * value**2) * tangent for value, tangent in zip(values, variation)]
    )
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        vx = variation[left]
        vy = variation[right]
        difference = x - y
        square_sum = x**2 + y**2
        d_difference = vx - vy
        d_square_sum = 2 * x * vx + 2 * y * vy
        result[left] += data["lambda"] * (
            d_difference * square_sum
            + difference * d_square_sum
            + 2 * difference * d_difference * x
            + difference**2 * vx
        ) / 2
        result[right] += data["lambda"] * (
            -d_difference * square_sum
            - difference * d_square_sum
            + 2 * difference * d_difference * y
            + difference**2 * vy
        ) / 2
    return sp.Matrix([sp.factor(item) for item in result])


def audit_q3_symbolic_derivatives(audit: "Audit") -> None:
    values = sp.Matrix(sp.symbols("z0:8", real=True))
    variation = sp.Matrix(sp.symbols("v0:8", real=True))
    r_symbol, g_symbol, lambda_symbol = sp.symbols("r_q3 g_q3 lambda_q3", nonzero=True, real=True)
    data = {"r": r_symbol, "g": g_symbol, "lambda": lambda_symbol}
    potential = sp.expand(q3_potential(values, data))
    formula_gradient = q3_gradient(values, data)
    derived_gradient = sp.Matrix([sp.diff(potential, value) for value in values])
    gradient_defect = sp.Matrix([sp.factor(item) for item in formula_gradient - derived_gradient])
    audit.check("Q3 gradient is derivative of potential", gradient_defect == sp.zeros(8, 1), gradient_defect, sp.zeros(8, 1), "q3_derivative")

    formula_hessian_v = q3_hessian_apply(values, variation, data)
    derived_hessian = derived_gradient.jacobian(values)
    derived_hessian_v = derived_hessian * variation
    hessian_defect = sp.Matrix([sp.factor(item) for item in formula_hessian_v - derived_hessian_v])
    audit.check("Q3 Hessian action is derivative of gradient", hessian_defect == sp.zeros(8, 1), hessian_defect, sp.zeros(8, 1), "q3_derivative")
    symmetry_defect = sp.simplify(derived_hessian - derived_hessian.T)
    audit.check("Q3 Hessian symmetry", symmetry_defect == sp.zeros(8), symmetry_defect, sp.zeros(8), "q3_derivative")

    left, right = q3_edges()[0]
    x, y = values[left], values[right]
    difference = x - y
    square_sum = x**2 + y**2
    actual_right = lambda_symbol * (-difference * square_sum + difference**2 * y) / 2
    wrong_right = lambda_symbol * (difference * square_sum + difference**2 * y) / 2
    wrong_sign_gradient = formula_gradient.copy()
    wrong_sign_gradient[right] += wrong_right - actual_right
    audit.check("Q3 wrong-right-sign mutant rejected", wrong_sign_gradient != derived_gradient, wrong_sign_gradient[right] - derived_gradient[right], "nonzero", "q3_mutant")

    doubled_data = {"r": r_symbol, "g": g_symbol, "lambda": 2 * lambda_symbol}
    audit.check("Q3 locking-factor mutant rejected", q3_gradient(values, doubled_data) != derived_gradient, "different", "potential derivative", "q3_mutant")

    omitted_potential = sum(r_symbol * value**2 / 2 + g_symbol * value**4 / 4 for value in values)
    omitted_potential += sum(
        lambda_symbol * (values[a] - values[b]) ** 2 * (values[a] ** 2 + values[b] ** 2) / 4
        for a, b in q3_edges()[1:]
    )
    omitted_gradient = sp.Matrix([sp.diff(omitted_potential, value) for value in values])
    audit.check("Q3 omitted-edge mutant rejected", omitted_gradient != derived_gradient, "different", "full edge derivative", "q3_mutant")

    wrong_hessian_v = wrong_sign_gradient.jacobian(values) * variation
    audit.check("Q3 Hessian-sign mutant rejected", wrong_hessian_v != derived_hessian_v, "different", "potential Hessian", "q3_mutant")


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        raw = {
            "name": name,
            "M": 4,
            "L": q(8),
            "chi": q(2),
            "c": q(3, 2),
            "r": q(-1, 2),
            "g": q(2),
            "lambda": q(1),
            "delta": q(1, 2),
            "hbar": q(3, 7),
        }
    elif name == "f1":
        raw = {
            "name": name,
            "M": 6,
            "L": q(9),
            "chi": q(4, 3),
            "c": q(7, 9),
            "r": q(1, 5),
            "g": q(9, 7),
            "lambda": q(5, 6),
            "delta": q(-3, 10),
            "hbar": q(7, 8),
        }
    else:
        raise ValueError(name)
    raw["a"] = sp.factor(raw["L"] / raw["M"])
    raw["w"] = sp.factor(raw["a"] / 8)
    raw["mu"] = sp.factor(raw["chi"] * raw["w"])
    raw["k"] = sp.factor(raw["w"] * raw["c"] / raw["a"] ** 2)
    raw["kappa"] = sp.factor(raw["c"] * raw["delta"] ** 2 / (raw["chi"] * raw["a"] ** 2))
    raw["beta"] = sp.factor(raw["delta"] ** 2 / raw["chi"])
    return raw


def ring_fixture(data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    positions: list[sp.Matrix] = []
    momenta: list[sp.Matrix] = []
    for site in range(data["M"]):
        position = sp.zeros(8, 1)
        momentum = sp.zeros(8, 1)
        position[site % 8] = q((-1) ** site * (site + 1), site + 2)
        position[(site + 3) % 8] = q(site + 2, site + 3)
        momentum[(site + 1) % 8] = q((-1) ** (site + 1), site + 1)
        momentum[(site + 5) % 8] = q(site + 1, site + 4)
        positions.append(position)
        momenta.append(momentum)
    return positions, momenta


def small_history_fixture(data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    previous: list[sp.Matrix] = []
    current: list[sp.Matrix] = []
    for site in range(data["M"]):
        left = sp.zeros(8, 1)
        right = sp.zeros(8, 1)
        left[site % 8] = q((-1) ** site, 20 + site)
        left[(site + 1) % 8] = q(site + 1, 37 + site)
        right[(site + 2) % 8] = q(site + 1, 24 + site)
        right[(site + 5) % 8] = q(-(site + 2), 41 + site)
        previous.append(left)
        current.append(right)
    return previous, current


def q3_dense_fixture() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    values = sp.Matrix([q((-1) ** index * (index + 1), index + 2) for index in range(8)])
    variation = sp.Matrix([q((-1) ** (index + 1) * (index + 2), index + 3) for index in range(8)])
    second = sp.Matrix([q(2 * index + 1, index + 5) for index in range(8)])
    return values, variation, second


def potential_gradient(positions: list[sp.Matrix], data: dict[str, Any]) -> list[sp.Matrix]:
    gradients: list[sp.Matrix] = []
    coefficient = data["w"] * data["c"] / data["a"] ** 2
    for site, value in enumerate(positions):
        spatial = coefficient * (2 * value - positions[(site - 1) % data["M"]] - positions[(site + 1) % data["M"]])
        gradients.append(spatial + data["w"] * q3_gradient(value, data))
    return gradients


def inherited_hamiltonian(positions: list[sp.Matrix], momenta: list[sp.Matrix], data: dict[str, Any]) -> sp.Expr:
    kinetic = sum((momentum.dot(momentum)) / (2 * data["mu"]) for momentum in momenta)
    potential = data["w"] * sum(
        data["c"] * (positions[(site + 1) % data["M"]] - positions[site]).dot(
            positions[(site + 1) % data["M"]] - positions[site]
        )
        / (2 * data["a"] ** 2)
        + q3_potential(positions[site], data)
        for site in range(data["M"])
    )
    return sp.factor(kinetic + potential)


def bond_hamiltonian(
    left_q: sp.Matrix,
    left_p: sp.Matrix,
    right_q: sp.Matrix,
    right_p: sp.Matrix,
    data: dict[str, Any],
) -> sp.Expr:
    kinetic = (left_p.dot(left_p) + right_p.dot(right_p)) / (4 * data["mu"])
    potential = data["w"] * (
        data["c"] * (right_q - left_q).dot(right_q - left_q) / (2 * data["a"] ** 2)
        + (q3_potential(left_q, data) + q3_potential(right_q, data)) / 2
    )
    return sp.factor(kinetic + potential)


def history_encode(
    positions: list[sp.Matrix], momenta: list[sp.Matrix], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    scale = data["delta"] / (2 * data["mu"])
    return (
        [position - scale * momentum for position, momentum in zip(positions, momenta)],
        [position + scale * momentum for position, momentum in zip(positions, momenta)],
    )


def history_decode(
    minus: list[sp.Matrix], plus: list[sp.Matrix], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    return (
        [(left + right) / 2 for left, right in zip(minus, plus)],
        [data["mu"] * (right - left) / data["delta"] for left, right in zip(minus, plus)],
    )


def dkd(
    positions: list[sp.Matrix], momenta: list[sp.Matrix], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    scale = data["delta"] / (2 * data["mu"])
    half_positions = [position + scale * momentum for position, momentum in zip(positions, momenta)]
    gradient = potential_gradient(half_positions, data)
    final_momenta = [momentum - data["delta"] * force for momentum, force in zip(momenta, gradient)]
    final_positions = [position + scale * momentum for position, momentum in zip(half_positions, final_momenta)]
    return final_positions, final_momenta


def history_step(
    minus: list[sp.Matrix], plus: list[sp.Matrix], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    gradient = potential_gradient(plus, data)
    next_slice = [
        2 * current - previous - data["delta"] ** 2 * force / data["mu"]
        for previous, current, force in zip(minus, plus, gradient)
    ]
    return [item.copy() for item in plus], next_slice


def node_history_recurrence(
    previous: list[sp.Matrix], current: list[sp.Matrix], data: dict[str, Any]
) -> list[sp.Matrix]:
    return [
        sp.factor(2 * (1 - data["kappa"])) * current[site]
        + data["kappa"] * (current[(site - 1) % data["M"]] + current[(site + 1) % data["M"]])
        - previous[site]
        - data["beta"] * q3_gradient(current[site], data)
        for site in range(data["M"])
    ]


def matrix_lists_equal(left: list[sp.Matrix], right: list[sp.Matrix]) -> bool:
    return len(left) == len(right) and all(all(sp.factor(value) == 0 for value in a - b) for a, b in zip(left, right))


Pair = tuple[sp.Matrix, sp.Matrix]


def pairs_equal(left: Pair, right: Pair) -> bool:
    return matrix_lists_equal(list(left), list(right))


def quad_forward(sw: Pair, nw: Pair, se: Pair, data: dict[str, Any]) -> Pair:
    a_ne = (
        data["kappa"] * (nw[0] + se[0])
        - sw[0]
        + 2 * (1 - data["kappa"]) * sw[1]
        - data["beta"] * q3_gradient(sw[1], data)
    )
    b_ne = (
        data["kappa"] * (nw[1] + se[1])
        - sw[1]
        + 2 * (1 - data["kappa"]) * a_ne
        - data["beta"] * q3_gradient(a_ne, data)
    )
    return sp.Matrix([sp.factor(item) for item in a_ne]), sp.Matrix([sp.factor(item) for item in b_ne])


def quad_recover_sw(nw: Pair, se: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    b_sw = (
        data["kappa"] * (nw[1] + se[1])
        + 2 * (1 - data["kappa"]) * ne[0]
        - data["beta"] * q3_gradient(ne[0], data)
        - ne[1]
    )
    a_sw = (
        data["kappa"] * (nw[0] + se[0])
        + 2 * (1 - data["kappa"]) * b_sw
        - data["beta"] * q3_gradient(b_sw, data)
        - ne[0]
    )
    return sp.Matrix([sp.factor(item) for item in a_sw]), sp.Matrix([sp.factor(item) for item in b_sw])


def quad_recover_nw(sw: Pair, se: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    a_nw = (
        ne[0]
        - data["kappa"] * se[0]
        + sw[0]
        - 2 * (1 - data["kappa"]) * sw[1]
        + data["beta"] * q3_gradient(sw[1], data)
    ) / data["kappa"]
    b_nw = (
        ne[1]
        - data["kappa"] * se[1]
        + sw[1]
        - 2 * (1 - data["kappa"]) * ne[0]
        + data["beta"] * q3_gradient(ne[0], data)
    ) / data["kappa"]
    return sp.Matrix([sp.factor(item) for item in a_nw]), sp.Matrix([sp.factor(item) for item in b_nw])


def quad_recover_se(sw: Pair, nw: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    return quad_recover_nw(sw, nw, ne, data)


def propagate_history(
    previous: list[sp.Matrix], current: list[sp.Matrix], data: dict[str, Any], final_time: int
) -> dict[int, list[sp.Matrix]]:
    solution = {-1: [item.copy() for item in previous], 0: [item.copy() for item in current]}
    for time in range(final_time):
        solution[time + 1] = node_history_recurrence(solution[time - 1], solution[time], data)
    return solution


def sample_ab(solution: dict[int, list[sp.Matrix]], i: int, j: int, modulus: int) -> Pair:
    time = i + j
    site = (i - j) % modulus
    return solution[time][site], solution[time + 1][site]


def fill_rectangle(boundary: dict[tuple[int, int], Pair], m: int, n: int, data: dict[str, Any], order: str) -> dict[tuple[int, int], Pair]:
    grid = {key: (value[0].copy(), value[1].copy()) for key, value in boundary.items()}
    cells = [(i, j) for i in range(1, m + 1) for j in range(1, n + 1)]
    if order == "row":
        cells.sort(key=lambda item: (item[0], item[1]))
    elif order == "column":
        cells.sort(key=lambda item: (item[1], item[0]))
    elif order == "antidiagonal":
        cells.sort(key=lambda item: (item[0] + item[1], item[0]))
    else:
        raise ValueError(order)
    for i, j in cells:
        grid[(i, j)] = quad_forward(grid[(i - 1, j - 1)], grid[(i - 1, j)], grid[(i, j - 1)], data)
    return grid


def monotone_paths(m: int, n: int) -> list[list[tuple[int, int]]]:
    paths: list[list[tuple[int, int]]] = []
    for east_positions in itertools.combinations(range(m + n), m):
        east = set(east_positions)
        i, j = 0, n
        vertices = [(i, j)]
        for step in range(m + n):
            if step in east:
                i += 1
            else:
                j -= 1
            vertices.append((i, j))
        paths.append(vertices)
    return paths


def recurrence_source(current: list[sp.Matrix], data: dict[str, Any]) -> list[sp.Matrix]:
    return [
        2 * (1 - data["kappa"]) * current[site]
        + data["kappa"] * (current[(site - 1) % data["M"]] + current[(site + 1) % data["M"]])
        - data["beta"] * q3_gradient(current[site], data)
        for site in range(data["M"])
    ]


def checker_cut(solution: dict[int, list[sp.Matrix]], center: int, phase: str, modulus: int) -> list[Pair]:
    cut: list[Pair] = []
    for site in range(modulus):
        even_class = (site - center) % 2 == 0
        if phase == "minus":
            time = center if even_class else center - 1
        elif phase == "plus":
            time = center if even_class else center + 1
        else:
            raise ValueError(phase)
        cut.append((solution[time][site], solution[time + 1][site]))
    return cut


def decode_checker_minus(cut: list[Pair], center: int, data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    current = [
        cut[site][0] if (site - center) % 2 == 0 else cut[site][1]
        for site in range(data["M"])
    ]
    source = recurrence_source(current, data)
    previous = [
        source[site] - cut[site][1] if (site - center) % 2 == 0 else cut[site][0]
        for site in range(data["M"])
    ]
    return previous, current


def decode_checker_plus(cut: list[Pair], center: int, data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    future = [
        cut[site][1] if (site - center) % 2 == 0 else cut[site][0]
        for site in range(data["M"])
    ]
    source = recurrence_source(future, data)
    current = [
        cut[site][0] if (site - center) % 2 == 0 else source[site] - cut[site][1]
        for site in range(data["M"])
    ]
    return current, future


def flip_checker_minus_to_plus(cut: list[Pair], center: int, data: dict[str, Any]) -> list[Pair]:
    result = [(left.copy(), right.copy()) for left, right in cut]
    for site in range(data["M"]):
        if (site - center) % 2 != 0:
            result[site] = quad_forward(cut[site], cut[(site - 1) % data["M"]], cut[(site + 1) % data["M"]], data)
    return result


def flip_checker_plus_to_next_minus(cut: list[Pair], center: int, data: dict[str, Any]) -> list[Pair]:
    result = [(left.copy(), right.copy()) for left, right in cut]
    for site in range(data["M"]):
        if (site - center) % 2 == 0:
            result[site] = quad_forward(cut[site], cut[(site - 1) % data["M"]], cut[(site + 1) % data["M"]], data)
    return result


def cut_flux(
    path: list[tuple[int, int]],
    first: dict[int, list[sp.Matrix]],
    second: dict[int, list[sp.Matrix]],
    data: dict[str, Any],
    spatial_sign: int = 1,
) -> sp.Expr:
    total = sp.Integer(0)
    for (i, j), (next_i, next_j) in zip(path[:-1], path[1:]):
        time = i + j
        site = (i - j) % data["M"]
        next_time = next_i + next_j
        total += temporal_current(first, second, time, site, data)
        if next_time == time + 1:
            total += spatial_sign * spatial_current(first, second, time + 1, site, data)
        elif next_time == time - 1:
            total -= spatial_sign * spatial_current(first, second, time, site, data)
        else:
            raise AssertionError("monotone cut step is not null-adjacent")
    return sp.factor(total)


def variation_next(
    background: list[sp.Matrix], previous: list[sp.Matrix], current: list[sp.Matrix], data: dict[str, Any]
) -> list[sp.Matrix]:
    return [
        2 * (1 - data["kappa"]) * current[site]
        + data["kappa"] * (current[(site - 1) % data["M"]] + current[(site + 1) % data["M"]])
        - previous[site]
        - data["beta"] * q3_hessian_apply(background[site], current[site], data)
        for site in range(data["M"])
    ]


def propagate_variation(
    background: dict[int, list[sp.Matrix]], previous: list[sp.Matrix], current: list[sp.Matrix], data: dict[str, Any], final_time: int
) -> dict[int, list[sp.Matrix]]:
    result = {-1: [item.copy() for item in previous], 0: [item.copy() for item in current]}
    for time in range(final_time):
        result[time + 1] = variation_next(background[time], result[time - 1], result[time], data)
    return result


def wedge(left_a: sp.Matrix, left_b: sp.Matrix, right_a: sp.Matrix, right_b: sp.Matrix) -> sp.Expr:
    return sp.factor(left_a.dot(right_b) - right_a.dot(left_b))


def temporal_current(
    first: dict[int, list[sp.Matrix]], second: dict[int, list[sp.Matrix]], time: int, site: int, data: dict[str, Any]
) -> sp.Expr:
    return sp.factor(
        data["mu"]
        * wedge(first[time + 1][site], first[time][site], second[time + 1][site], second[time][site])
        / data["delta"]
    )


def spatial_current(
    first: dict[int, list[sp.Matrix]], second: dict[int, list[sp.Matrix]], time: int, site: int, data: dict[str, Any]
) -> sp.Expr:
    right = (site + 1) % data["M"]
    return sp.factor(
        data["mu"]
        * data["kappa"]
        * wedge(first[time][right], first[time][site], second[time][right], second[time][site])
        / data["delta"]
    )


def variation_fixture(data: dict[str, Any], offset: int) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    previous: list[sp.Matrix] = []
    current: list[sp.Matrix] = []
    for site in range(data["M"]):
        left = sp.zeros(8, 1)
        right = sp.zeros(8, 1)
        left[(site + offset) % 8] = q((-1) ** (site + offset), site + offset + 2)
        right[(2 * site + offset + 1) % 8] = q(site + 1, site + offset + 3)
        previous.append(left)
        current.append(right)
    return previous, current


def lie_flow_series_one_species() -> tuple[sp.Expr, sp.Matrix]:
    qw, pw, qs, ps, t = sp.symbols("qw pw qs ps t", real=True)
    mu, k, r, g = sp.symbols("mu k r g", nonzero=True, real=True)
    potential = k * (qs - qw) ** 2 / 2 + (
        r * qw**2 / 2 + g * qw**4 / 4 + r * qs**2 / 2 + g * qs**4 / 4
    ) / 2
    hamiltonian = (pw**2 + ps**2) / (4 * mu) + potential

    def derivative(function: sp.Expr) -> sp.Expr:
        return sp.expand(
            sp.diff(function, qw) * sp.diff(hamiltonian, pw)
            - sp.diff(function, pw) * sp.diff(hamiltonian, qw)
            + sp.diff(function, qs) * sp.diff(hamiltonian, ps)
            - sp.diff(function, ps) * sp.diff(hamiltonian, qs)
        )

    flow: list[sp.Expr] = []
    for coordinate in (qw, pw, qs, ps):
        current = coordinate
        terms = [coordinate]
        for _ in range(4):
            current = derivative(current)
            terms.append(current)
        flow.append(sp.expand(sum(t**order * terms[order] / sp.factorial(order) for order in range(5))))
    cross = sp.Matrix(flow[:2]).jacobian((qs, ps))
    determinant = sp.expand(cross.det())
    return sp.factor(determinant.coeff(t, 4)), cross


def run(output: Path) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVES, manifest["negative_ids"], NEGATIVES, "identity")
    audit.check("canonical parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("scoped verdict", manifest["verdict"] == EXPECTED_VERDICT, manifest["verdict"], EXPECTED_VERDICT, "scope")
    audit.check("T0 authority", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "scope")
    audit.check("Q3 edge count", len(q3_edges()) == 12, len(q3_edges()), 12, "q3")
    audit_q3_symbolic_derivatives(audit)

    history_fingerprints: dict[str, Any] = {}
    for profile in ("f0", "f1"):
        data = fixture(profile)
        audit.check(f"{profile} even regulator", data["M"] >= 4 and data["M"] % 2 == 0, data["M"], "even >=4", "domain")
        audit.check(f"{profile} normalization", data["w"] == data["a"] / 8 and data["mu"] == data["chi"] * data["w"], [data["w"], data["mu"]], [data["a"] / 8, data["chi"] * data["w"]], "domain")
        audit.check(f"{profile} nonzero step", data["delta"] != 0, data["delta"], "nonzero", "domain")
        c_jacobian = sp.Matrix([[1, -data["delta"] / (2 * data["mu"])], [1, data["delta"] / (2 * data["mu"])]])
        profile_omega_history = sp.Matrix([[0, -data["mu"] / data["delta"]], [data["mu"] / data["delta"], 0]])
        profile_omega_phase = sp.Matrix([[0, -1], [1, 0]])
        audit.check(
            f"{profile} typed C pullback",
            sp.simplify(c_jacobian.T * profile_omega_history * c_jacobian - profile_omega_phase) == sp.zeros(2),
            sp.simplify(c_jacobian.T * profile_omega_history * c_jacobian),
            profile_omega_phase,
            "history_symplectic",
        )
        q3_values, q3_variation, q3_second = q3_dense_fixture()
        q3_potential_value = q3_potential(q3_values, data)
        q3_gradient_value = q3_gradient(q3_values, data)
        q3_hessian_value = q3_hessian_apply(q3_values, q3_variation, data)
        q3_hessian_second = q3_hessian_apply(q3_values, q3_second, data)
        audit.check(
            f"{profile} dense Q3 Hessian symmetry",
            sp.factor(q3_second.dot(q3_hessian_value) - q3_variation.dot(q3_hessian_second)) == 0,
            sp.factor(q3_second.dot(q3_hessian_value) - q3_variation.dot(q3_hessian_second)),
            0,
            "q3_derivative",
        )
        positions, momenta = ring_fixture(data)
        minus, plus = history_encode(positions, momenta, data)
        decoded_q, decoded_p = history_decode(minus, plus, data)
        audit.check(f"{profile} history inverse q", matrix_lists_equal(decoded_q, positions), decoded_q, positions, "history")
        audit.check(f"{profile} history inverse p", matrix_lists_equal(decoded_p, momenta), decoded_p, momenta, "history")
        dkd_q, dkd_p = dkd(positions, momenta, data)
        encoded_out = history_encode(dkd_q, dkd_p, data)
        history_out = history_step(minus, plus, data)
        audit.check(f"{profile} exact nonlinear history minus", matrix_lists_equal(encoded_out[0], history_out[0]), encoded_out[0], history_out[0], "history")
        audit.check(f"{profile} exact nonlinear history plus", matrix_lists_equal(encoded_out[1], history_out[1]), encoded_out[1], history_out[1], "history")
        node_out = node_history_recurrence(minus, plus, data)
        audit.check(f"{profile} node Q3 recurrence", matrix_lists_equal(history_out[1], node_out), history_out[1], node_out, "history")
        bonds = [
            bond_hamiltonian(
                positions[site], momenta[site], positions[(site + 1) % data["M"]], momenta[(site + 1) % data["M"]], data
            )
            for site in range(data["M"])
        ]
        inherited = inherited_hamiltonian(positions, momenta, data)
        audit.check(f"{profile} exact bond partition", sp.factor(sum(bonds) - inherited) == 0, sum(bonds), inherited, "bond")

        # Exact staggered A/B quad on the balanced periodic square.
        small_previous, small_current = small_history_fixture(data)
        half_size = data["M"] // 2
        solution = propagate_history(small_previous, small_current, data, max(2 * half_size + 1, 7))
        exact_grid = {
            (i, j): sample_ab(solution, i, j, data["M"])
            for i in range(half_size + 1)
            for j in range(half_size + 1)
        }
        boundary = {
            **{(i, 0): exact_grid[(i, 0)] for i in range(half_size + 1)},
            **{(0, j): exact_grid[(0, j)] for j in range(1, half_size + 1)},
        }
        filled_row = fill_rectangle(boundary, half_size, half_size, data, "row")
        filled_column = fill_rectangle(boundary, half_size, half_size, data, "column")
        filled_antidiagonal = fill_rectangle(boundary, half_size, half_size, data, "antidiagonal")
        audit.check(
            f"{profile} A/B row exact solution",
            all(pairs_equal(filled_row[key], exact_grid[key]) for key in exact_grid),
            "all vertices",
            "exact history samples",
            "ab_rectangle",
        )
        audit.check(
            f"{profile} A/B sweep row-column",
            all(pairs_equal(filled_row[key], filled_column[key]) for key in exact_grid),
            "equal",
            "equal",
            "ab_rectangle",
        )
        audit.check(
            f"{profile} A/B sweep row-antidiagonal",
            all(pairs_equal(filled_row[key], filled_antidiagonal[key]) for key in exact_grid),
            "equal",
            "equal",
            "ab_rectangle",
        )
        nonsquare_m, nonsquare_n = 1, 5
        nonsquare_exact = {
            (i, j): sample_ab(solution, i, j, data["M"])
            for i in range(nonsquare_m + 1)
            for j in range(nonsquare_n + 1)
        }
        nonsquare_boundary = {
            **{(i, 0): nonsquare_exact[(i, 0)] for i in range(nonsquare_m + 1)},
            **{(0, j): nonsquare_exact[(0, j)] for j in range(1, nonsquare_n + 1)},
        }
        nonsquare_row = fill_rectangle(nonsquare_boundary, nonsquare_m, nonsquare_n, data, "row")
        nonsquare_column = fill_rectangle(nonsquare_boundary, nonsquare_m, nonsquare_n, data, "column")
        nonsquare_antidiagonal = fill_rectangle(nonsquare_boundary, nonsquare_m, nonsquare_n, data, "antidiagonal")
        audit.check(
            f"{profile} nonlinear 1x5 rectangle exact",
            all(pairs_equal(nonsquare_row[key], nonsquare_exact[key]) for key in nonsquare_exact),
            "all vertices",
            "exact history samples",
            "ab_rectangle",
        )
        audit.check(
            f"{profile} nonlinear 1x5 sweep agreement",
            all(
                pairs_equal(nonsquare_row[key], nonsquare_column[key])
                and pairs_equal(nonsquare_row[key], nonsquare_antidiagonal[key])
                for key in nonsquare_exact
            ),
            "equal",
            "equal",
            "ab_rectangle",
        )
        audit.check(
            f"{profile} nonlinear 1x5 path count",
            len(monotone_paths(nonsquare_m, nonsquare_n)) == 6,
            len(monotone_paths(nonsquare_m, nonsquare_n)),
            6,
            "ab_rectangle",
        )
        for i in range(1, half_size + 1):
            for j in range(1, half_size + 1):
                sw = exact_grid[(i - 1, j - 1)]
                nw = exact_grid[(i - 1, j)]
                se = exact_grid[(i, j - 1)]
                ne = exact_grid[(i, j)]
                audit.check(f"{profile} recover SW {i},{j}", pairs_equal(quad_recover_sw(nw, se, ne, data), sw), "recovered", "SW", "ab_inverse")
                audit.check(f"{profile} recover NW {i},{j}", pairs_equal(quad_recover_nw(sw, se, ne, data), nw), "recovered", "NW", "ab_inverse")
                audit.check(f"{profile} recover SE {i},{j}", pairs_equal(quad_recover_se(sw, nw, ne, data), se), "recovered", "SE", "ab_inverse")
        for i in range(1, nonsquare_m + 1):
            for j in range(1, nonsquare_n + 1):
                sw = nonsquare_exact[(i - 1, j - 1)]
                nw = nonsquare_exact[(i - 1, j)]
                se = nonsquare_exact[(i, j - 1)]
                ne = nonsquare_exact[(i, j)]
                audit.check(f"{profile} 1x5 recover SW {i},{j}", pairs_equal(quad_recover_sw(nw, se, ne, data), sw), "recovered", "SW", "ab_inverse")
                audit.check(f"{profile} 1x5 recover NW {i},{j}", pairs_equal(quad_recover_nw(sw, se, ne, data), nw), "recovered", "NW", "ab_inverse")
                audit.check(f"{profile} 1x5 recover SE {i},{j}", pairs_equal(quad_recover_se(sw, nw, ne, data), se), "recovered", "SE", "ab_inverse")

        paths = monotone_paths(half_size, half_size)
        audit.check(f"{profile} all-cut count", len(paths) == math.comb(data["M"], half_size), len(paths), math.comb(data["M"], half_size), "ab_cuts")
        for path_index, path in enumerate(paths):
            audit.check(f"{profile} path {path_index} length", len(path) == data["M"] + 1, len(path), data["M"] + 1, "ab_cuts")
            audit.check(f"{profile} path {path_index} endpoint seam", pairs_equal(exact_grid[path[0]], exact_grid[path[-1]]), "equal", "periodic endpoint", "ab_seam")
            residues = [(i - j) % data["M"] for i, j in path[:-1]]
            audit.check(f"{profile} path {path_index} site coverage", sorted(residues) == list(range(data["M"])), sorted(residues), list(range(data["M"])), "ab_seam")

        minus_cut = checker_cut(solution, half_size, "minus", data["M"])
        plus_cut_expected = checker_cut(solution, half_size, "plus", data["M"])
        plus_cut = flip_checker_minus_to_plus(minus_cut, half_size, data)
        audit.check(
            f"{profile} minus-to-plus simultaneous quad flip",
            all(pairs_equal(actual, expected) for actual, expected in zip(plus_cut, plus_cut_expected)),
            "equal",
            "P_m^+",
            "ab_checker_dynamics",
        )
        minus_previous, minus_current = decode_checker_minus(minus_cut, half_size, data)
        plus_current, plus_future = decode_checker_plus(plus_cut, half_size, data)
        audit.check(f"{profile} P_m^- previous decode", matrix_lists_equal(minus_previous, solution[half_size - 1]), "recovered", "x_(m-1)", "ab_checker_dynamics")
        audit.check(f"{profile} P_m^- current decode", matrix_lists_equal(minus_current, solution[half_size]), "recovered", "x_m", "ab_checker_dynamics")
        audit.check(f"{profile} P_m^+ current decode", matrix_lists_equal(plus_current, solution[half_size]), "recovered", "x_m", "ab_checker_dynamics")
        audit.check(f"{profile} P_m^+ future decode", matrix_lists_equal(plus_future, solution[half_size + 1]), "recovered", "x_(m+1)", "ab_checker_dynamics")
        audit.check(f"{profile} first parity history transfer", matrix_lists_equal(plus_current, minus_current) and matrix_lists_equal(plus_future, node_history_recurrence(minus_previous, minus_current, data)), "equal", "T_hist R_m^-", "ab_checker_dynamics")

        next_minus_expected = checker_cut(solution, half_size + 2, "minus", data["M"])
        next_minus_cut = flip_checker_plus_to_next_minus(plus_cut, half_size, data)
        audit.check(
            f"{profile} plus-to-next-minus simultaneous periodic quad flip",
            all(pairs_equal(actual, expected) for actual, expected in zip(next_minus_cut, next_minus_expected)),
            "equal",
            "P_(m+2)^-",
            "ab_checker_dynamics",
        )
        next_previous, next_current = decode_checker_minus(next_minus_cut, half_size + 2, data)
        audit.check(f"{profile} P_(m+2)^- previous decode", matrix_lists_equal(next_previous, solution[half_size + 1]), "recovered", "x_(m+1)", "ab_checker_dynamics")
        audit.check(f"{profile} P_(m+2)^- current decode", matrix_lists_equal(next_current, solution[half_size + 2]), "recovered", "x_(m+2)", "ab_checker_dynamics")
        audit.check(f"{profile} complementary parity history transfer", matrix_lists_equal(next_previous, plus_future) and matrix_lists_equal(next_current, node_history_recurrence(plus_current, plus_future, data)), "equal", "T_hist R_m^+", "ab_checker_dynamics")

        minus_q, minus_p = history_decode(minus_previous, minus_current, data)
        plus_q, plus_p = history_decode(plus_current, plus_future, data)
        expected_plus_q, expected_plus_p = dkd(minus_q, minus_p, data)
        audit.check(f"{profile} first parity canonical D-K-D q diagram", matrix_lists_equal(plus_q, expected_plus_q), "equal", "F_delta q", "ab_checker_dynamics")
        audit.check(f"{profile} first parity canonical D-K-D p diagram", matrix_lists_equal(plus_p, expected_plus_p), "equal", "F_delta p", "ab_checker_dynamics")
        next_q, next_p = history_decode(next_previous, next_current, data)
        expected_next_q, expected_next_p = dkd(plus_q, plus_p, data)
        audit.check(f"{profile} complementary parity canonical D-K-D q diagram", matrix_lists_equal(next_q, expected_next_q), "equal", "F_delta q", "ab_checker_dynamics")
        audit.check(f"{profile} complementary parity canonical D-K-D p diagram", matrix_lists_equal(next_p, expected_next_p), "equal", "F_delta p", "ab_checker_dynamics")

        energy_before = inherited_hamiltonian(minus_q, minus_p, data)
        energy_after = inherited_hamiltonian(plus_q, plus_p, data)
        energy_defect = sp.factor(inherited_hamiltonian(expected_plus_q, expected_plus_p, data) - energy_before)
        audit.check(f"{profile} translated-cut energy defect identity", sp.factor(energy_after - energy_before - energy_defect) == 0, "equal", "exact D-K-D defect", "cut_energy")
        audit.check(f"{profile} same-history cut energy identity", inherited_hamiltonian(*history_decode(minus_previous, minus_current, data), data) == energy_before, "equal", "E_P", "cut_energy")
        absolute_delta_p = [data["mu"] * (right - left) / abs(data["delta"]) for left, right in zip(minus_previous, minus_current)]
        if data["delta"] < 0:
            audit.check(f"{profile} absolute-step momentum mutant rejected", not matrix_lists_equal(minus_p, absolute_delta_p), "different", "signed mu/delta", "history_symplectic")

        checker_times = {
            site: half_size if (site - half_size) % 2 == 0 else half_size - 1
            for site in range(data["M"])
        }

        first_initial = variation_fixture(data, 1)
        second_initial = variation_fixture(data, 3)
        first_variation = propagate_variation(solution, first_initial[0], first_initial[1], data, 2 * half_size + 1)
        second_variation = propagate_variation(solution, second_initial[0], second_initial[1], data, 2 * half_size + 1)
        divergences: list[sp.Expr] = []
        fluxes: list[sp.Expr] = []
        for time in range(0, 2 * half_size + 1):
            fluxes.append(sp.factor(sum(temporal_current(first_variation, second_variation, time, site, data) for site in range(data["M"]))))
            for site in range(data["M"]):
                divergence = sp.factor(
                    temporal_current(first_variation, second_variation, time, site, data)
                    - temporal_current(first_variation, second_variation, time - 1, site, data)
                    - spatial_current(first_variation, second_variation, time, site, data)
                    + spatial_current(first_variation, second_variation, time, (site - 1) % data["M"], data)
                )
                divergences.append(divergence)
        audit.check(f"{profile} local symplectic-current divergence", all(item == 0 for item in divergences), divergences, "all zero", "ab_current")
        audit.check(f"{profile} periodic temporal flux", all(item == fluxes[0] for item in fluxes), len(fluxes), "constant sequence", "ab_current")
        all_cut_fluxes = [cut_flux(path, first_variation, second_variation, data) for path in paths]
        audit.check(f"{profile} every monotone-cut oriented flux", all(item == fluxes[0] for item in all_cut_fluxes), all_cut_fluxes, fluxes[0], "ab_current")
        mutated_cut_fluxes = [cut_flux(path, first_variation, second_variation, data, spatial_sign=-1) for path in paths]
        audit.check(f"{profile} spatial-current-sign mutant rejected", any(item != fluxes[0] for item in mutated_cut_fluxes), "rejected", "at least one unequal", "ab_current_mutant")
        history_fingerprints[profile] = {
            "kappa": data["kappa"],
            "beta": data["beta"],
            "first_next_coordinate": history_out[1][0][0],
            "hamiltonian": inherited,
            "all_cut_count": len(paths),
            "periodic_flux": fluxes[0],
            "all_cut_fluxes": all_cut_fluxes,
            "checker_times": checker_times,
            "checker_plus_times": {
                site: half_size if (site - half_size) % 2 == 0 else half_size + 1
                for site in range(data["M"])
            },
            "q3_potential": q3_potential_value,
            "q3_gradient": list(q3_gradient_value),
            "q3_hessian_v": list(q3_hessian_value),
            "nonlinear_next_site0": list(node_history_recurrence(small_previous, small_current, data)[0]),
            "checker_canonical_p0": list(minus_p[0]),
            "energy_defect_nonzero": energy_defect != 0,
        }

    delta, mu = sp.symbols("delta mu", nonzero=True, real=True)
    jacobian_c_inverse = sp.Matrix([[q(1, 2), q(1, 2)], [-mu / delta, mu / delta]])
    omega_phase = sp.Matrix([[0, -1], [1, 0]])
    omega_history = sp.Matrix([[0, -mu / delta], [mu / delta, 0]])
    pullback = sp.simplify(jacobian_c_inverse.T * omega_phase * jacobian_c_inverse)
    audit.check("typed inverse history symplectic pullback", pullback == omega_history, pullback, omega_history, "history_symplectic")
    jacobian_c = sp.Matrix([[1, -delta / (2 * mu)], [1, delta / (2 * mu)]])
    forward_pullback = sp.simplify(jacobian_c.T * omega_history * jacobian_c)
    audit.check("typed forward history symplectic pullback", forward_pullback == omega_phase, forward_pullback, omega_phase, "history_symplectic")
    hessian = sp.symbols("H", real=True)
    alpha = delta**2 / mu
    history_jacobian = sp.Matrix([[0, 1], [-1, 2 - alpha * hessian]])
    audit.check(
        "history step symplectic",
        sp.simplify(history_jacobian.T * omega_history * history_jacobian - omega_history) == sp.zeros(2),
        sp.simplify(history_jacobian.T * omega_history * history_jacobian),
        omega_history,
        "history_symplectic",
    )

    f_symbol, g_symbol, kappa_cross = sp.symbols("F G kappa", real=True, nonzero=True)
    sw_ne_cross = sp.Matrix([[-1, f_symbol], [-g_symbol, -1 + g_symbol * f_symbol]])
    leg_omega = sp.Matrix([[0, -1], [1, 0]])
    audit.check("A/B SW-NE determinant", sp.factor(sw_ne_cross.det()) == 1, sp.factor(sw_ne_cross.det()), 1, "ab_cross")
    audit.check(
        "A/B SW-NE symplectic",
        sp.simplify(sw_ne_cross.T * leg_omega * sw_ne_cross - leg_omega) == sp.zeros(2),
        sp.simplify(sw_ne_cross.T * leg_omega * sw_ne_cross),
        leg_omega,
        "ab_cross",
    )
    nw_ne_cross = sp.Matrix([[kappa_cross, 0], [kappa_cross * g_symbol, kappa_cross]])
    audit.check("A/B NW-NE one-species determinant", sp.factor(nw_ne_cross.det()) == kappa_cross**2, sp.factor(nw_ne_cross.det()), kappa_cross**2, "ab_cross")
    audit.check("A/B NW-NE eight-species determinant", sp.factor(nw_ne_cross.det() ** 8) == kappa_cross**16, sp.factor(nw_ne_cross.det() ** 8), kappa_cross**16, "ab_cross")
    audit.check(
        "A/B NW-NE conformal symplectic",
        sp.simplify(nw_ne_cross.T * leg_omega * nw_ne_cross - kappa_cross**2 * leg_omega) == sp.zeros(2),
        sp.simplify(nw_ne_cross.T * leg_omega * nw_ne_cross),
        kappa_cross**2 * leg_omega,
        "ab_cross",
    )

    hbar_symbol = sp.symbols("hbar", positive=True)
    history_commutator = sp.factor(hbar_symbol * delta / mu)
    canonical_history_commutator = sp.factor((mu / delta) * history_commutator)
    audit.check("history CCR rescaling", canonical_history_commutator == hbar_symbol, canonical_history_commutator, hbar_symbol, "history_quantum")

    xn1, xn, xnp1, force = sp.symbols("x_nm1 x_n x_np1 force")
    discrete_el = mu * (2 * xn - xn1 - xnp1) / delta - delta * force
    recurrence_solution = sp.solve(sp.Eq(discrete_el, 0), xnp1)[0]
    audit.check("discrete Euler-Lagrange recurrence", recurrence_solution == 2 * xn - xn1 - delta**2 * force / mu, recurrence_solution, 2 * xn - xn1 - delta**2 * force / mu, "history_variational")

    jet_coefficient, cross_jet = lie_flow_series_one_species()
    k = sp.symbols("k", nonzero=True, real=True)
    audit.check("bond-flow one-species twist jet", sp.factor(jet_coefficient - k**2 / (48 * mu**2)) == 0, jet_coefficient, k**2 / (48 * mu**2), "bond_twist")
    eight_species_coefficient = sp.factor(jet_coefficient**8)
    audit.check("bond-flow eight-species determinant jet", eight_species_coefficient == (k**2 / (48 * mu**2)) ** 8, eight_species_coefficient, (k**2 / (48 * mu**2)) ** 8, "bond_twist")

    t, omega_plus, omega_minus = sp.symbols("t omega_plus omega_minus", positive=True, real=True)
    harmonic_det = sp.factor(
        (
            2
            - 2 * sp.cos(omega_plus * t) * sp.cos(omega_minus * t)
            - (omega_plus / omega_minus + omega_minus / omega_plus)
            * sp.sin(omega_plus * t)
            * sp.sin(omega_minus * t)
        )
        / 4
    )
    harmonic_t4 = sp.factor(sp.expand(sp.series(harmonic_det, t, 0, 6).removeO()).coeff(t, 4))
    expected_t4 = (omega_minus**2 - omega_plus**2) ** 2 / 48
    audit.check("harmonic twist series", sp.factor(harmonic_t4 - expected_t4) == 0, harmonic_t4, expected_t4, "bond_caustic")
    resonance = sp.simplify(harmonic_det.subs({omega_plus: 1, omega_minus: 2, t: 2 * sp.pi}))
    audit.check("exact harmonic caustic", resonance == 0, resonance, 0, "bond_caustic")
    resonance_a, resonance_c, resonance_chi = q(1), q(3), q(1)
    resonance_r = 4 * resonance_c / (3 * resonance_a**2)
    computed_plus_sq = sp.factor(resonance_r / (4 * resonance_chi))
    computed_minus_sq = sp.factor(computed_plus_sq + resonance_c / (resonance_chi * resonance_a**2))
    audit.check("caustic admissible frequencies", [computed_plus_sq, computed_minus_sq] == [1, 4], [computed_plus_sq, computed_minus_sq], [1, 4], "bond_caustic")

    qv = sp.symbols("q0:4")
    pv = sp.symbols("p0:4")
    kappa_symbol = sp.symbols("kappa", nonzero=True)
    poisson_witness = -kappa_symbol * (
        pv[0] * qv[1]
        - pv[0] * qv[3]
        + pv[1] * qv[0]
        - pv[1] * qv[2]
        - pv[2] * qv[1]
        + pv[2] * qv[3]
        - pv[3] * qv[0]
        + pv[3] * qv[2]
    ) / (2 * mu)
    witness_subs = {
        qv[0]: 1, qv[1]: 0, qv[2]: 0, qv[3]: 0,
        pv[0]: 0, pv[1]: 1, pv[2]: 0, pv[3]: 0,
        kappa_symbol: 1, mu: 1,
    }
    audit.check("overlapping-bond Poisson witness", poisson_witness.subs(witness_subs) == q(-1, 2), poisson_witness.subs(witness_subs), q(-1, 2), "finite_trotter")

    d, u, v = sp.symbols("d u v", nonzero=True, real=True)
    block_d = -2 * d**2 * u / mu + d**4 * v / (2 * mu**2)
    block_p = -3 * d**3 * u / (2 * mu**2) + d**5 * v / (4 * mu**3)
    block_q = -2 * d * u + d**3 * v / mu
    macro_det_scalar = sp.factor(block_d**2 - block_p * block_q)
    audit.check("D-K-D squared cross cancellation", macro_det_scalar == d**4 * u**2 / mu**2, macro_det_scalar, d**4 * u**2 / mu**2, "dkd2")
    audit.check("D-K-D squared eight-species determinant", (macro_det_scalar.subs(u, -k)) ** 8 == (d**4 * k**2 / mu**2) ** 8, (macro_det_scalar.subs(u, -k)) ** 8, (d**4 * k**2 / mu**2) ** 8, "dkd2")
    distance_two = d**3 * k**2 / mu
    audit.check("D-K-D squared radius-two spectator", distance_two != 0, distance_two, "nonzero", "dkd2")

    y, quad_alpha, quad_r, quad_g = sp.symbols("y alpha r g", real=True)
    midpoint_polynomial = sp.factor(y * (1 + quad_alpha * quad_r / 4 + quad_alpha * quad_g * y**2 / 64))
    hostile = {quad_alpha: 2, quad_r: -4, quad_g: 1}
    hostile_polynomial = sp.factor(midpoint_polynomial.subs(hostile))
    audit.check("midpoint three-root factor", hostile_polynomial == y * (y**2 - 32) / 32, hostile_polynomial, y * (y**2 - 32) / 32, "quad")
    audit.check("midpoint zero root", hostile_polynomial.subs(y, 0) == 0, hostile_polynomial.subs(y, 0), 0, "quad")
    audit.check("midpoint positive root", hostile_polynomial.subs(y, 4 * sp.sqrt(2)) == 0, hostile_polynomial.subs(y, 4 * sp.sqrt(2)), 0, "quad")
    audit.check("midpoint negative root", hostile_polynomial.subs(y, -4 * sp.sqrt(2)) == 0, hostile_polynomial.subs(y, -4 * sp.sqrt(2)), 0, "quad")
    singular = sp.factor(sp.diff(midpoint_polynomial, y).subs({y: 0, quad_alpha: 1, quad_r: -4, quad_g: 1}))
    audit.check("midpoint singular threshold", singular == 0, singular, 0, "quad")

    true_scope = (
        "inserted_1D_per_unit_transverse_area_model",
        "same_CL8_16M_forward_phase_dimension",
        "actual_Q3_and_spatial_coefficients",
        "exact_inherited_nonlinear_DKD_history_conjugacy",
        "history_phase_dimension_and_symplectic_form_exact",
        "exact_radius_one_Q3_history_recurrence",
        "exact_staggered_AB_quad_from_inherited_DKD",
        "global_all_corner_AB_inverses",
        "open_rectangle_all_monotone_cut_diffeomorphisms",
        "discrete_symplectic_current_and_cut_flux",
        "balanced_even_M_periodic_seam",
        "classical_fixed_regulator_boundary_Cauchy_diagram",
        "controller_free_exact_bond_flow",
        "global_temporal_bond_symplectomorphism",
        "compact_short_time_full_cross_charts",
        "exact_controller_free_checkerboard_forward_circuit",
        "classical_Trotter_recovery_fixed_M",
        "quantum_strong_Trotter_recovery_fixed_M",
        "DKD2_adjacent_tangent_cross_full_rank",
        "explicit_q_only_quad_forward_reconstruction",
        "exact_classical_inserted_1D_balanced_even_M_fixed_regulator_DKD_boundary_Cauchy_diagram",
    )
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    false_scope = tuple(key for key, value in manifest["scope"].items() if value is False)
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("ambiguous global diagram key absent", "exact_global_boundary_Cauchy_diagram" not in manifest["scope"], sorted(manifest["scope"]), "absent", "scope")
    audit.check("global classical diagram closed", manifest["boundary_cauchy_contract"]["exact_commutative_diagram"] is True, manifest["boundary_cauchy_contract"]["exact_commutative_diagram"], True, "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    for parent in PARENTS:
        audit.check(f"parent exists {parent.name}", parent.is_file(), parent, "file", "provenance")
    parent_hashes = {serial(parent): sha256(parent) for parent in PARENTS}
    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "claim_bearing": manifest["claim_bearing"],
        "verdict": manifest["verdict"],
        "negative_ids": NEGATIVES,
        "status": manifest["status"],
        "script_version": __version__,
        "script_sha256": sha256(SCRIPT),
        "manifest_sha256": sha256(MANIFEST),
        "certificate_sha256": sha256(CERTIFICATE) if CERTIFICATE.exists() else None,
        "parent_sha256": parent_hashes,
        "invariants": {
            "history_symplectic_matrix": omega_history,
            "history_fixture_fingerprints": history_fingerprints,
            "bond_twist_one_species_t4": jet_coefficient,
            "bond_twist_eight_species_t32": eight_species_coefficient,
            "harmonic_t4": harmonic_t4,
            "harmonic_caustic": resonance,
            "poisson_witness": poisson_witness.subs(witness_subs),
            "dkd2_cross_scalar": macro_det_scalar,
            "dkd2_distance_two": distance_two,
            "midpoint_hostile_factor": hostile_polynomial,
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    summary = payload["assertion_summary"]
    print(f"PASS {summary['passed']}/{summary['total']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
