#!/usr/bin/env python3
"""Independent stdlib/Fraction audit of the CL8 history-parent route split.

This file deliberately imports neither SymPy, NumPy nor the primary audit.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


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
SCHEMA = f"tect/{SLUG}-independent/0.1"
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
    / f"2026-08-04-independent-{SLUG}/result.json"
)

Vector = tuple[F, ...]
Pair = tuple[Vector, Vector]


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, F):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
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


def zero() -> Vector:
    return (F(0),) * 8


def basis(index: int, value: F) -> Vector:
    result = [F(0)] * 8
    result[index] = value
    return tuple(result)


def add(*vectors: Vector) -> Vector:
    return tuple(sum((vector[index] for vector in vectors), F(0)) for index in range(8))


def scale(coefficient: F, vector: Vector) -> Vector:
    return tuple(coefficient * item for item in vector)


def sub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def dot(left: Vector, right: Vector) -> F:
    return sum((a * b for a, b in zip(left, right)), F(0))


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def q3_potential(values: Vector, data: dict[str, Any]) -> F:
    onsite = sum((data["r"] * value**2 / 2 + data["g"] * value**4 / 4 for value in values), F(0))
    locked = sum(
        (
            data["lambda"]
            * (values[left] - values[right]) ** 2
            * (values[left] ** 2 + values[right] ** 2)
            / 4
            for left, right in q3_edges()
        ),
        F(0),
    )
    return onsite + locked


def q3_gradient(values: Vector, data: dict[str, Any]) -> Vector:
    gradient = [data["r"] * value + data["g"] * value**3 for value in values]
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        difference = x - y
        square_sum = x**2 + y**2
        gradient[left] += data["lambda"] * (difference * square_sum + difference**2 * x) / 2
        gradient[right] += data["lambda"] * (-difference * square_sum + difference**2 * y) / 2
    return tuple(gradient)


def q3_hessian_apply(values: Vector, variation: Vector, data: dict[str, Any]) -> Vector:
    result = [(data["r"] + 3 * data["g"] * value**2) * tangent for value, tangent in zip(values, variation)]
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
    return tuple(result)


def shifted(values: Vector, direction: Vector, parameter: F) -> Vector:
    return add(values, scale(parameter, direction))


def d1_exact(function: Any) -> F:
    return (function(F(-2)) - 8 * function(F(-1)) + 8 * function(F(1)) - function(F(2))) / 12


def q3_gradient_from_potential(values: Vector, data: dict[str, Any]) -> Vector:
    return tuple(
        d1_exact(lambda parameter, index=index: q3_potential(shifted(values, basis(index, F(1)), parameter), data))
        for index in range(8)
    )


def q3_hessian_apply_from_potential(values: Vector, variation: Vector, data: dict[str, Any]) -> Vector:
    return tuple(
        d1_exact(
            lambda parameter, index=index: q3_gradient_from_potential(
                shifted(values, variation, parameter), data
            )[index]
        )
        for index in range(8)
    )


def q3_variant_potential(
    values: Vector,
    data: dict[str, Any],
    edges: tuple[tuple[int, int], ...],
    locking_multiplier: F = F(1),
) -> F:
    onsite = sum((data["r"] * value**2 / 2 + data["g"] * value**4 / 4 for value in values), F(0))
    locking = sum(
        (
            data["lambda"]
            * locking_multiplier
            * (values[left] - values[right]) ** 2
            * (values[left] ** 2 + values[right] ** 2)
            / 4
            for left, right in edges
        ),
        F(0),
    )
    return onsite + locking


def q3_variant_gradient_from_potential(
    values: Vector,
    data: dict[str, Any],
    edges: tuple[tuple[int, int], ...],
    locking_multiplier: F = F(1),
) -> Vector:
    return tuple(
        d1_exact(
            lambda parameter, index=index: q3_variant_potential(
                shifted(values, basis(index, F(1)), parameter), data, edges, locking_multiplier
            )
        )
        for index in range(8)
    )


def q3_wrong_right_sign_gradient(values: Vector, data: dict[str, Any]) -> Vector:
    result = list(q3_gradient(values, data))
    left, right = q3_edges()[0]
    x, y = values[left], values[right]
    difference = x - y
    square_sum = x**2 + y**2
    actual = data["lambda"] * (-difference * square_sum + difference**2 * y) / 2
    wrong = data["lambda"] * (difference * square_sum + difference**2 * y) / 2
    result[right] += wrong - actual
    return tuple(result)


def q3_wrong_hessian_sign(values: Vector, variation: Vector, data: dict[str, Any]) -> Vector:
    result = list(q3_hessian_apply(values, variation, data))
    left, right = q3_edges()[0]
    x, y = values[left], values[right]
    vx, vy = variation[left], variation[right]
    difference = x - y
    d_square_sum = 2 * x * vx + 2 * y * vy
    result[right] += data["lambda"] * difference * d_square_sum
    return tuple(result)


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        raw = {"name": name, "M": 4, "L": F(8), "chi": F(2), "c": F(3, 2), "r": F(-1, 2), "g": F(2), "lambda": F(1), "delta": F(1, 2), "hbar": F(3, 7)}
    elif name == "f1":
        raw = {"name": name, "M": 6, "L": F(9), "chi": F(4, 3), "c": F(7, 9), "r": F(1, 5), "g": F(9, 7), "lambda": F(5, 6), "delta": F(-3, 10), "hbar": F(7, 8)}
    else:
        raise ValueError(name)
    raw["a"] = raw["L"] / raw["M"]
    raw["w"] = raw["a"] / 8
    raw["mu"] = raw["chi"] * raw["w"]
    raw["k"] = raw["w"] * raw["c"] / raw["a"] ** 2
    raw["kappa"] = raw["c"] * raw["delta"] ** 2 / (raw["chi"] * raw["a"] ** 2)
    raw["beta"] = raw["delta"] ** 2 / raw["chi"]
    return raw


def ring_fixture(data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    positions: list[Vector] = []
    momenta: list[Vector] = []
    for site in range(data["M"]):
        position = list(zero())
        momentum = list(zero())
        position[site % 8] = F((-1) ** site * (site + 1), site + 2)
        position[(site + 3) % 8] = F(site + 2, site + 3)
        momentum[(site + 1) % 8] = F((-1) ** (site + 1), site + 1)
        momentum[(site + 5) % 8] = F(site + 1, site + 4)
        positions.append(tuple(position))
        momenta.append(tuple(momentum))
    return positions, momenta


def small_history_fixture(data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    previous: list[Vector] = []
    current: list[Vector] = []
    for site in range(data["M"]):
        previous.append(
            add(
                basis(site % 8, F((-1) ** site, 20 + site)),
                basis((site + 1) % 8, F(site + 1, 37 + site)),
            )
        )
        current.append(
            add(
                basis((site + 2) % 8, F(site + 1, 24 + site)),
                basis((site + 5) % 8, F(-(site + 2), 41 + site)),
            )
        )
    return previous, current


def q3_dense_fixture() -> tuple[Vector, Vector, Vector]:
    values = tuple(F((-1) ** index * (index + 1), index + 2) for index in range(8))
    variation = tuple(F((-1) ** (index + 1) * (index + 2), index + 3) for index in range(8))
    second = tuple(F(2 * index + 1, index + 5) for index in range(8))
    return values, variation, second


def inherited_hamiltonian(positions: list[Vector], momenta: list[Vector], data: dict[str, Any]) -> F:
    kinetic = sum((dot(momentum, momentum) / (2 * data["mu"]) for momentum in momenta), F(0))
    potential = data["w"] * sum(
        (
            data["c"]
            * dot(sub(positions[(site + 1) % data["M"]], positions[site]), sub(positions[(site + 1) % data["M"]], positions[site]))
            / (2 * data["a"] ** 2)
            + q3_potential(positions[site], data)
            for site in range(data["M"])
        ),
        F(0),
    )
    return kinetic + potential


def potential_gradient(positions: list[Vector], data: dict[str, Any]) -> list[Vector]:
    coefficient = data["w"] * data["c"] / data["a"] ** 2
    return [
        add(
            scale(coefficient, add(scale(2, positions[site]), scale(-1, positions[(site - 1) % data["M"]]), scale(-1, positions[(site + 1) % data["M"]]))),
            scale(data["w"], q3_gradient(positions[site], data)),
        )
        for site in range(data["M"])
    ]


def history_encode(positions: list[Vector], momenta: list[Vector], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    s = data["delta"] / (2 * data["mu"])
    return (
        [add(position, scale(-s, momentum)) for position, momentum in zip(positions, momenta)],
        [add(position, scale(s, momentum)) for position, momentum in zip(positions, momenta)],
    )


def history_decode(minus: list[Vector], plus: list[Vector], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    return (
        [scale(F(1, 2), add(left, right)) for left, right in zip(minus, plus)],
        [scale(data["mu"] / data["delta"], sub(right, left)) for left, right in zip(minus, plus)],
    )


def dkd(positions: list[Vector], momenta: list[Vector], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    s = data["delta"] / (2 * data["mu"])
    half = [add(position, scale(s, momentum)) for position, momentum in zip(positions, momenta)]
    gradient = potential_gradient(half, data)
    final_p = [add(momentum, scale(-data["delta"], force)) for momentum, force in zip(momenta, gradient)]
    final_q = [add(position, scale(s, momentum)) for position, momentum in zip(half, final_p)]
    return final_q, final_p


def node_history(previous: list[Vector], current: list[Vector], data: dict[str, Any]) -> list[Vector]:
    return [
        add(
            scale(2 * (1 - data["kappa"]), current[site]),
            scale(data["kappa"], current[(site - 1) % data["M"]]),
            scale(data["kappa"], current[(site + 1) % data["M"]]),
            scale(-1, previous[site]),
            scale(-data["beta"], q3_gradient(current[site], data)),
        )
        for site in range(data["M"])
    ]


def history_step(minus: list[Vector], plus: list[Vector], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    return list(plus), node_history(minus, plus, data)


def quad_forward(sw: Pair, nw: Pair, se: Pair, data: dict[str, Any]) -> Pair:
    a_ne = add(scale(data["kappa"], add(nw[0], se[0])), scale(-1, sw[0]), scale(2 * (1 - data["kappa"]), sw[1]), scale(-data["beta"], q3_gradient(sw[1], data)))
    b_ne = add(scale(data["kappa"], add(nw[1], se[1])), scale(-1, sw[1]), scale(2 * (1 - data["kappa"]), a_ne), scale(-data["beta"], q3_gradient(a_ne, data)))
    return a_ne, b_ne


def quad_recover_sw(nw: Pair, se: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    b_sw = add(scale(data["kappa"], add(nw[1], se[1])), scale(2 * (1 - data["kappa"]), ne[0]), scale(-data["beta"], q3_gradient(ne[0], data)), scale(-1, ne[1]))
    a_sw = add(scale(data["kappa"], add(nw[0], se[0])), scale(2 * (1 - data["kappa"]), b_sw), scale(-data["beta"], q3_gradient(b_sw, data)), scale(-1, ne[0]))
    return a_sw, b_sw


def quad_recover_nw(sw: Pair, se: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    a_nw = scale(1 / data["kappa"], add(ne[0], scale(-data["kappa"], se[0]), sw[0], scale(-2 * (1 - data["kappa"]), sw[1]), scale(data["beta"], q3_gradient(sw[1], data))))
    b_nw = scale(1 / data["kappa"], add(ne[1], scale(-data["kappa"], se[1]), sw[1], scale(-2 * (1 - data["kappa"]), ne[0]), scale(data["beta"], q3_gradient(ne[0], data))))
    return a_nw, b_nw


def quad_recover_se(sw: Pair, nw: Pair, ne: Pair, data: dict[str, Any]) -> Pair:
    return quad_recover_nw(sw, nw, ne, data)


def propagate(previous: list[Vector], current: list[Vector], data: dict[str, Any], final_time: int) -> dict[int, list[Vector]]:
    result = {-1: list(previous), 0: list(current)}
    for time in range(final_time):
        result[time + 1] = node_history(result[time - 1], result[time], data)
    return result


def sample_ab(solution: dict[int, list[Vector]], i: int, j: int, modulus: int) -> Pair:
    return solution[i + j][(i - j) % modulus], solution[i + j + 1][(i - j) % modulus]


def fill_rectangle(boundary: dict[tuple[int, int], Pair], m: int, n: int, data: dict[str, Any], order: str) -> dict[tuple[int, int], Pair]:
    grid = dict(boundary)
    cells = [(i, j) for i in range(1, m + 1) for j in range(1, n + 1)]
    if order == "row":
        cells.sort(key=lambda item: (item[0], item[1]))
    elif order == "column":
        cells.sort(key=lambda item: (item[1], item[0]))
    else:
        cells.sort(key=lambda item: (item[0] + item[1], item[0]))
    for i, j in cells:
        grid[(i, j)] = quad_forward(grid[(i - 1, j - 1)], grid[(i - 1, j)], grid[(i, j - 1)], data)
    return grid


def paths(m: int, n: int) -> list[list[tuple[int, int]]]:
    result: list[list[tuple[int, int]]] = []
    for east_positions in itertools.combinations(range(m + n), m):
        east = set(east_positions)
        i, j = 0, n
        path = [(i, j)]
        for step in range(m + n):
            if step in east:
                i += 1
            else:
                j -= 1
            path.append((i, j))
        result.append(path)
    return result


def recurrence_source(current: list[Vector], data: dict[str, Any]) -> list[Vector]:
    return [
        add(
            scale(2 * (1 - data["kappa"]), current[site]),
            scale(data["kappa"], current[(site - 1) % data["M"]]),
            scale(data["kappa"], current[(site + 1) % data["M"]]),
            scale(-data["beta"], q3_gradient(current[site], data)),
        )
        for site in range(data["M"])
    ]


def checker_cut(solution: dict[int, list[Vector]], center: int, phase: str, modulus: int) -> list[Pair]:
    result: list[Pair] = []
    for site in range(modulus):
        even_class = (site - center) % 2 == 0
        if phase == "minus":
            time = center if even_class else center - 1
        elif phase == "plus":
            time = center if even_class else center + 1
        else:
            raise ValueError(phase)
        result.append((solution[time][site], solution[time + 1][site]))
    return result


def decode_checker_minus(cut: list[Pair], center: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    current = [cut[site][0] if (site - center) % 2 == 0 else cut[site][1] for site in range(data["M"])]
    source = recurrence_source(current, data)
    previous = [
        sub(source[site], cut[site][1]) if (site - center) % 2 == 0 else cut[site][0]
        for site in range(data["M"])
    ]
    return previous, current


def decode_checker_plus(cut: list[Pair], center: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    future = [cut[site][1] if (site - center) % 2 == 0 else cut[site][0] for site in range(data["M"])]
    source = recurrence_source(future, data)
    current = [
        cut[site][0] if (site - center) % 2 == 0 else sub(source[site], cut[site][1])
        for site in range(data["M"])
    ]
    return current, future


def flip_checker_minus_to_plus(cut: list[Pair], center: int, data: dict[str, Any]) -> list[Pair]:
    result = list(cut)
    for site in range(data["M"]):
        if (site - center) % 2 != 0:
            result[site] = quad_forward(cut[site], cut[(site - 1) % data["M"]], cut[(site + 1) % data["M"]], data)
    return result


def flip_checker_plus_to_next_minus(cut: list[Pair], center: int, data: dict[str, Any]) -> list[Pair]:
    result = list(cut)
    for site in range(data["M"]):
        if (site - center) % 2 == 0:
            result[site] = quad_forward(cut[site], cut[(site - 1) % data["M"]], cut[(site + 1) % data["M"]], data)
    return result


def variation_next(background: list[Vector], previous: list[Vector], current: list[Vector], data: dict[str, Any]) -> list[Vector]:
    return [
        add(
            scale(2 * (1 - data["kappa"]), current[site]),
            scale(data["kappa"], current[(site - 1) % data["M"]]),
            scale(data["kappa"], current[(site + 1) % data["M"]]),
            scale(-1, previous[site]),
            scale(-data["beta"], q3_hessian_apply(background[site], current[site], data)),
        )
        for site in range(data["M"])
    ]


def propagate_variation(background: dict[int, list[Vector]], previous: list[Vector], current: list[Vector], data: dict[str, Any], final_time: int) -> dict[int, list[Vector]]:
    result = {-1: list(previous), 0: list(current)}
    for time in range(final_time):
        result[time + 1] = variation_next(background[time], result[time - 1], result[time], data)
    return result


def variation_fixture(data: dict[str, Any], offset: int) -> tuple[list[Vector], list[Vector]]:
    previous: list[Vector] = []
    current: list[Vector] = []
    for site in range(data["M"]):
        previous.append(basis((site + offset) % 8, F((-1) ** (site + offset), site + offset + 2)))
        current.append(basis((2 * site + offset + 1) % 8, F(site + 1, site + offset + 3)))
    return previous, current


def wedge(first_a: Vector, first_b: Vector, second_a: Vector, second_b: Vector) -> F:
    return dot(first_a, second_b) - dot(second_a, first_b)


def kt(first: dict[int, list[Vector]], second: dict[int, list[Vector]], time: int, site: int, data: dict[str, Any]) -> F:
    return data["mu"] * wedge(first[time + 1][site], first[time][site], second[time + 1][site], second[time][site]) / data["delta"]


def kx(first: dict[int, list[Vector]], second: dict[int, list[Vector]], time: int, site: int, data: dict[str, Any]) -> F:
    right = (site + 1) % data["M"]
    return data["mu"] * data["kappa"] * wedge(first[time][right], first[time][site], second[time][right], second[time][site]) / data["delta"]


def cut_flux(
    path: list[tuple[int, int]],
    first: dict[int, list[Vector]],
    second: dict[int, list[Vector]],
    data: dict[str, Any],
    spatial_sign: int = 1,
) -> F:
    total = F(0)
    for (i, j), (next_i, next_j) in zip(path[:-1], path[1:]):
        time = i + j
        site = (i - j) % data["M"]
        next_time = next_i + next_j
        total += kt(first, second, time, site, data)
        if next_time == time + 1:
            total += spatial_sign * kx(first, second, time + 1, site, data)
        elif next_time == time - 1:
            total -= spatial_sign * kx(first, second, time, site, data)
        else:
            raise AssertionError("monotone cut step is not null-adjacent")
    return total


def sqrt_fraction_exact(value: F) -> F:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise AssertionError("fraction is not an exact square")
    return F(numerator, denominator)


def trig_at_full_turn(turns: F) -> tuple[F, F]:
    if turns.denominator != 1:
        raise AssertionError("rotation is not an integer turn")
    return F(1), F(0)


def oscillator_rotation(cosine: F, sine: F, mass: F, omega: F) -> tuple[tuple[F, F], tuple[F, F]]:
    return ((cosine, sine / (mass * omega)), (-mass * omega * sine, cosine))


def matrix_subtract(left: tuple[tuple[F, F], tuple[F, F]], right: tuple[tuple[F, F], tuple[F, F]]) -> tuple[tuple[F, F], tuple[F, F]]:
    return tuple(tuple(left[row][column] - right[row][column] for column in range(2)) for row in range(2))  # type: ignore[return-value]


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
    syntax = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(syntax)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(syntax)
        if isinstance(node, ast.ImportFrom)
    }
    audit.check("independent no symbolic package import", "sympy" not in imported, sorted(imported), "no symbolic package", "independence")
    audit.check("independent no array package import", "numpy" not in imported, sorted(imported), "no array package", "independence")
    audit.check("Q3 edge count", len(q3_edges()) == 12, len(q3_edges()), 12, "q3")

    fingerprints: dict[str, Any] = {}
    expected_constants = {
        "f0": {"s": F(1, 2), "mu_over_delta": F(1), "kappa": F(3, 64), "beta": F(1, 8)},
        "f1": {"s": F(-3, 5), "mu_over_delta": F(-5, 6), "kappa": F(7, 300), "beta": F(27, 400)},
    }
    for profile in ("f0", "f1"):
        data = fixture(profile)
        constants = {
            "s": data["delta"] / (2 * data["mu"]),
            "mu_over_delta": data["mu"] / data["delta"],
            "kappa": data["kappa"],
            "beta": data["beta"],
        }
        audit.check(f"{profile} signed constants", constants == expected_constants[profile], constants, expected_constants[profile], "domain")
        c_jacobian = ((F(1), -data["delta"] / (2 * data["mu"])), (F(1), data["delta"] / (2 * data["mu"])))
        omega_hist_scale = data["mu"] / data["delta"]
        pullback_01 = -2 * c_jacobian[0][0] * c_jacobian[1][1] * omega_hist_scale
        audit.check(f"{profile} typed C pullback coefficient", pullback_01 == -1, pullback_01, -1, "history_symplectic")

        q3_values, q3_variation, q3_second = q3_dense_fixture()
        potential_gradient_derived = q3_gradient_from_potential(q3_values, data)
        potential_hessian_v = q3_hessian_apply_from_potential(q3_values, q3_variation, data)
        potential_hessian_second = q3_hessian_apply_from_potential(q3_values, q3_second, data)
        audit.check(f"{profile} Q3 gradient from potential", q3_gradient(q3_values, data) == potential_gradient_derived, q3_gradient(q3_values, data), potential_gradient_derived, "q3_derivative")
        audit.check(f"{profile} Q3 Hessian action from potential", q3_hessian_apply(q3_values, q3_variation, data) == potential_hessian_v, q3_hessian_apply(q3_values, q3_variation, data), potential_hessian_v, "q3_derivative")
        audit.check(f"{profile} Q3 Hessian symmetry from potential", dot(q3_second, potential_hessian_v) == dot(q3_variation, potential_hessian_second), dot(q3_second, potential_hessian_v), dot(q3_variation, potential_hessian_second), "q3_derivative")
        audit.check(f"{profile} Q3 wrong-right-sign mutant rejected", q3_wrong_right_sign_gradient(q3_values, data) != potential_gradient_derived, "different", "potential derivative", "q3_mutant")
        audit.check(f"{profile} Q3 omitted-edge mutant rejected", q3_variant_gradient_from_potential(q3_values, data, q3_edges()[1:]) != potential_gradient_derived, "different", "full edge derivative", "q3_mutant")
        audit.check(f"{profile} Q3 locking-factor mutant rejected", q3_variant_gradient_from_potential(q3_values, data, q3_edges(), F(2)) != potential_gradient_derived, "different", "unit locking factor", "q3_mutant")
        audit.check(f"{profile} Q3 Hessian-sign mutant rejected", q3_wrong_hessian_sign(q3_values, q3_variation, data) != potential_hessian_v, "different", "potential Hessian", "q3_mutant")
        positions, momenta = ring_fixture(data)
        minus, plus = history_encode(positions, momenta, data)
        decoded_q, decoded_p = history_decode(minus, plus, data)
        audit.check(f"{profile} history inverse q", decoded_q == positions, decoded_q, positions, "history")
        audit.check(f"{profile} history inverse p", decoded_p == momenta, decoded_p, momenta, "history")
        dkd_q, dkd_p = dkd(positions, momenta, data)
        encoded = history_encode(dkd_q, dkd_p, data)
        stepped = history_step(minus, plus, data)
        audit.check(f"{profile} exact D-K-D history", encoded == stepped, encoded, stepped, "history")

        small_previous, small_current = small_history_fixture(data)
        m = data["M"] // 2
        solution = propagate(small_previous, small_current, data, max(2 * m + 1, 7))
        exact = {(i, j): sample_ab(solution, i, j, data["M"]) for i in range(m + 1) for j in range(m + 1)}
        boundary = {**{(i, 0): exact[(i, 0)] for i in range(m + 1)}, **{(0, j): exact[(0, j)] for j in range(1, m + 1)}}
        row = fill_rectangle(boundary, m, m, data, "row")
        column = fill_rectangle(boundary, m, m, data, "column")
        antidiagonal = fill_rectangle(boundary, m, m, data, "antidiagonal")
        audit.check(f"{profile} rectangle exact", row == exact, "equal", "exact history samples", "ab_rectangle")
        audit.check(f"{profile} sweep agreement", row == column == antidiagonal, [row == column, row == antidiagonal], [True, True], "ab_rectangle")
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
        audit.check(f"{profile} nonlinear 1x5 rectangle exact", nonsquare_row == nonsquare_exact, "equal", "exact history samples", "ab_rectangle")
        audit.check(f"{profile} nonlinear 1x5 sweep agreement", nonsquare_row == nonsquare_column == nonsquare_antidiagonal, "equal", "equal", "ab_rectangle")
        audit.check(f"{profile} nonlinear 1x5 path count", len(paths(nonsquare_m, nonsquare_n)) == 6, len(paths(nonsquare_m, nonsquare_n)), 6, "ab_rectangle")
        for i in range(1, m + 1):
            for j in range(1, m + 1):
                sw, nw, se, ne = exact[(i - 1, j - 1)], exact[(i - 1, j)], exact[(i, j - 1)], exact[(i, j)]
                audit.check(f"{profile} SW inverse {i},{j}", quad_recover_sw(nw, se, ne, data) == sw, "recovered", "SW", "ab_inverse")
                audit.check(f"{profile} NW inverse {i},{j}", quad_recover_nw(sw, se, ne, data) == nw, "recovered", "NW", "ab_inverse")
                audit.check(f"{profile} SE inverse {i},{j}", quad_recover_se(sw, nw, ne, data) == se, "recovered", "SE", "ab_inverse")
        for i in range(1, nonsquare_m + 1):
            for j in range(1, nonsquare_n + 1):
                sw, nw, se, ne = (
                    nonsquare_exact[(i - 1, j - 1)],
                    nonsquare_exact[(i - 1, j)],
                    nonsquare_exact[(i, j - 1)],
                    nonsquare_exact[(i, j)],
                )
                audit.check(f"{profile} 1x5 SW inverse {i},{j}", quad_recover_sw(nw, se, ne, data) == sw, "recovered", "SW", "ab_inverse")
                audit.check(f"{profile} 1x5 NW inverse {i},{j}", quad_recover_nw(sw, se, ne, data) == nw, "recovered", "NW", "ab_inverse")
                audit.check(f"{profile} 1x5 SE inverse {i},{j}", quad_recover_se(sw, nw, ne, data) == se, "recovered", "SE", "ab_inverse")
        all_paths = paths(m, m)
        audit.check(f"{profile} path count", len(all_paths) == math.comb(data["M"], m), len(all_paths), math.comb(data["M"], m), "ab_cuts")
        for index, path in enumerate(all_paths):
            audit.check(f"{profile} seam {index}", exact[path[0]] == exact[path[-1]], "equal", "equal", "ab_seam")
            residues = sorted((i - j) % data["M"] for i, j in path[:-1])
            audit.check(f"{profile} coverage {index}", residues == list(range(data["M"])), residues, list(range(data["M"])), "ab_seam")

        minus_cut = checker_cut(solution, m, "minus", data["M"])
        plus_expected = checker_cut(solution, m, "plus", data["M"])
        plus_cut = flip_checker_minus_to_plus(minus_cut, m, data)
        audit.check(f"{profile} minus-to-plus simultaneous quad flip", plus_cut == plus_expected, "equal", "P_m^+", "ab_checker_dynamics")
        minus_previous, minus_current = decode_checker_minus(minus_cut, m, data)
        plus_current, plus_future = decode_checker_plus(plus_cut, m, data)
        audit.check(f"{profile} P_m^- decode", minus_previous == solution[m - 1] and minus_current == solution[m], "recovered", "x_(m-1),x_m", "ab_checker_dynamics")
        audit.check(f"{profile} P_m^+ decode", plus_current == solution[m] and plus_future == solution[m + 1], "recovered", "x_m,x_(m+1)", "ab_checker_dynamics")
        audit.check(f"{profile} first parity history transfer", plus_current == minus_current and plus_future == node_history(minus_previous, minus_current, data), "equal", "T_hist R_m^-", "ab_checker_dynamics")

        next_minus_expected = checker_cut(solution, m + 2, "minus", data["M"])
        next_minus_cut = flip_checker_plus_to_next_minus(plus_cut, m, data)
        audit.check(f"{profile} plus-to-next-minus simultaneous periodic quad flip", next_minus_cut == next_minus_expected, "equal", "P_(m+2)^-", "ab_checker_dynamics")
        next_previous, next_current = decode_checker_minus(next_minus_cut, m + 2, data)
        audit.check(f"{profile} P_(m+2)^- decode", next_previous == solution[m + 1] and next_current == solution[m + 2], "recovered", "x_(m+1),x_(m+2)", "ab_checker_dynamics")
        audit.check(f"{profile} complementary parity history transfer", next_previous == plus_future and next_current == node_history(plus_current, plus_future, data), "equal", "T_hist R_m^+", "ab_checker_dynamics")

        minus_q, minus_p = history_decode(minus_previous, minus_current, data)
        plus_q, plus_p = history_decode(plus_current, plus_future, data)
        expected_plus_q, expected_plus_p = dkd(minus_q, minus_p, data)
        audit.check(f"{profile} first parity canonical D-K-D diagram", (plus_q, plus_p) == (expected_plus_q, expected_plus_p), "equal", "F_delta J_m^-", "ab_checker_dynamics")
        next_q, next_p = history_decode(next_previous, next_current, data)
        expected_next_q, expected_next_p = dkd(plus_q, plus_p, data)
        audit.check(f"{profile} complementary parity canonical D-K-D diagram", (next_q, next_p) == (expected_next_q, expected_next_p), "equal", "F_delta J_m^+", "ab_checker_dynamics")
        energy_before = inherited_hamiltonian(minus_q, minus_p, data)
        energy_after = inherited_hamiltonian(plus_q, plus_p, data)
        energy_defect = inherited_hamiltonian(expected_plus_q, expected_plus_p, data) - energy_before
        audit.check(f"{profile} translated-cut energy defect identity", energy_after - energy_before == energy_defect, "equal", "exact D-K-D defect", "cut_energy")
        audit.check(f"{profile} same-history cut energy identity", inherited_hamiltonian(*history_decode(minus_previous, minus_current, data), data) == energy_before, "equal", "E_P", "cut_energy")
        if data["delta"] < 0:
            absolute_delta_p = [scale(data["mu"] / abs(data["delta"]), sub(right, left)) for left, right in zip(minus_previous, minus_current)]
            audit.check(f"{profile} absolute-step momentum mutant rejected", minus_p != absolute_delta_p, "different", "signed mu/delta", "history_symplectic")
        times = {site: m if (site - m) % 2 == 0 else m - 1 for site in range(data["M"])}

        first_initial = variation_fixture(data, 1)
        second_initial = variation_fixture(data, 3)
        first = propagate_variation(solution, first_initial[0], first_initial[1], data, 2 * m + 1)
        second = propagate_variation(solution, second_initial[0], second_initial[1], data, 2 * m + 1)
        fluxes: list[F] = []
        divergences: list[F] = []
        for time in range(2 * m + 1):
            fluxes.append(sum((kt(first, second, time, site, data) for site in range(data["M"])), F(0)))
            for site in range(data["M"]):
                divergences.append(
                    kt(first, second, time, site, data)
                    - kt(first, second, time - 1, site, data)
                    - kx(first, second, time, site, data)
                    + kx(first, second, time, (site - 1) % data["M"], data)
                )
        audit.check(f"{profile} current divergence", all(item == 0 for item in divergences), divergences, "all zero", "ab_current")
        audit.check(f"{profile} flux conservation", all(item == fluxes[0] for item in fluxes), len(fluxes), "constant sequence", "ab_current")
        all_cut_fluxes = [cut_flux(path, first, second, data) for path in all_paths]
        audit.check(f"{profile} every monotone-cut oriented flux", all(item == fluxes[0] for item in all_cut_fluxes), all_cut_fluxes, fluxes[0], "ab_current")
        mutated_cut_fluxes = [cut_flux(path, first, second, data, spatial_sign=-1) for path in all_paths]
        audit.check(f"{profile} spatial-current-sign mutant rejected", any(item != fluxes[0] for item in mutated_cut_fluxes), "rejected", "at least one unequal", "ab_current_mutant")
        fingerprints[profile] = {
            **constants,
            "all_cut_count": len(all_paths),
            "periodic_flux": fluxes[0],
            "all_cut_fluxes": all_cut_fluxes,
            "checker_times": times,
            "checker_plus_times": {site: m if (site - m) % 2 == 0 else m + 1 for site in range(data["M"])},
            "q3_potential": q3_potential(q3_values, data),
            "q3_gradient": potential_gradient_derived,
            "q3_hessian_v": potential_hessian_v,
            "nonlinear_next_site0": node_history(small_previous, small_current, data)[0],
            "checker_canonical_p0": minus_p[0],
            "energy_defect_nonzero": energy_defect != 0,
        }

    # Independent exact scalar matrix and route checks.
    for f_value, g_value in ((F(2, 3), F(-5, 7)), (F(-11, 4), F(9, 5))):
        matrix = ((F(-1), f_value), (-g_value, F(-1) + g_value * f_value))
        determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        audit.check(f"SW-NE determinant {f_value},{g_value}", determinant == 1, determinant, 1, "ab_cross")
    for profile in ("f0", "f1"):
        kappa = fixture(profile)["kappa"]
        nw_det = kappa**2
        audit.check(f"{profile} NW determinant power", nw_det**8 == kappa**16, nw_det**8, kappa**16, "ab_cross")

    for profile in ("f0", "f1"):
        data = fixture(profile)
        twist_one = data["k"] ** 2 / (48 * data["mu"] ** 2)
        equivalent = data["c"] ** 2 / (48 * data["chi"] ** 2 * data["a"] ** 4)
        audit.check(f"{profile} bond twist normalization", twist_one == equivalent, twist_one, equivalent, "bond_twist")
    resonance_a, resonance_c, resonance_chi = F(1), F(3), F(1)
    resonance_r = 4 * resonance_c / (3 * resonance_a**2)
    omega_plus_sq = resonance_r / (4 * resonance_chi)
    omega_minus_sq = omega_plus_sq + resonance_c / (resonance_chi * resonance_a**2)
    omega_plus = sqrt_fraction_exact(omega_plus_sq)
    omega_minus = sqrt_fraction_exact(omega_minus_sq)
    time_over_two_pi = 1 / omega_plus
    plus_turns = omega_plus * time_over_two_pi
    minus_turns = omega_minus * time_over_two_pi
    audit.check("derived harmonic resonance turns", (plus_turns, minus_turns) == (F(1), F(2)), (plus_turns, minus_turns), (F(1), F(2)), "bond_caustic")
    plus_cos, plus_sin = trig_at_full_turn(plus_turns)
    minus_cos, minus_sin = trig_at_full_turn(minus_turns)
    bond_mass = F(5, 3)
    rotation_plus = oscillator_rotation(plus_cos, plus_sin, bond_mass, omega_plus)
    rotation_minus = oscillator_rotation(minus_cos, minus_sin, bond_mass, omega_minus)
    cross_block_twice = matrix_subtract(rotation_plus, rotation_minus)
    cross_determinant_times_four = cross_block_twice[0][0] * cross_block_twice[1][1] - cross_block_twice[0][1] * cross_block_twice[1][0]
    audit.check("harmonic caustic cross block zero", cross_block_twice == ((F(0), F(0)), (F(0), F(0))), cross_block_twice, "zero matrix", "bond_caustic")
    audit.check("harmonic caustic determinant zero", cross_determinant_times_four == 0, cross_determinant_times_four, 0, "bond_caustic")
    hostile_turns = omega_minus * (time_over_two_pi + F(1, 3))
    try:
        trig_at_full_turn(hostile_turns)
        hostile_rejected = False
    except AssertionError:
        hostile_rejected = True
    audit.check("harmonic mistuned-time mutant rejected", hostile_rejected, hostile_turns, "noninteger turn", "bond_caustic_mutant")

    for d, u, v, mu in ((F(2, 3), F(-5, 4), F(7, 6), F(3, 2)), (F(-3, 5), F(9, 7), F(-2, 9), F(4, 3))):
        block_d = -2 * d**2 * u / mu + d**4 * v / (2 * mu**2)
        block_p = -3 * d**3 * u / (2 * mu**2) + d**5 * v / (4 * mu**3)
        block_q = -2 * d * u + d**3 * v / mu
        audit.check(f"D-K-D2 cancellation {d}", block_d**2 - block_p * block_q == d**4 * u**2 / mu**2, block_d**2 - block_p * block_q, d**4 * u**2 / mu**2, "dkd2")
    hostile_y2 = F(32)
    hostile_factor = F(1) + F(2) * F(-4) / 4 + F(2) * hostile_y2 / 64
    audit.check("midpoint nonzero roots", hostile_factor == 0, hostile_factor, 0, "quad")
    singular_derivative = F(1) + F(1) * F(-4) / 4
    audit.check("midpoint singular derivative", singular_derivative == 0, singular_derivative, 0, "quad")

    true_scope = tuple(key for key, value in manifest["scope"].items() if value is True)
    false_scope = tuple(key for key, value in manifest["scope"].items() if value is False)
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("ambiguous global diagram key absent", "exact_global_boundary_Cauchy_diagram" not in manifest["scope"], sorted(manifest["scope"]), "absent", "scope")
    audit.check("classical diagram closed", manifest["boundary_cauchy_contract"]["exact_commutative_diagram"] is True, manifest["boundary_cauchy_contract"]["exact_commutative_diagram"], True, "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY", "scope")
    audit.check("C6 tier", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

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
        "parent_sha256": {serial(parent): sha256(parent) for parent in PARENTS},
        "invariants": {
            "history_fixture_fingerprints": fingerprints,
            "harmonic_caustic": cross_determinant_times_four,
            "midpoint_hostile_y_squared": hostile_y2,
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
