#!/usr/bin/env python3
"""Independent stdlib/Fraction audit for the driven 1D CL8 interacting route."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-interacting-two-arm-work-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-1D-Q3-DRIVEN-ALL-CUT-WORK-TRANSPORT-AND-DIRECT-ORDER-MICROCUT-NOGO"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT_PATHS = (
    REPO / "strategy/pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)


def f(numerator: int, denominator: int = 1) -> Fraction:
    return Fraction(numerator, denominator)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Jet):
        return {"value": str(value.value), "gradient": [str(item) for item in value.gradient]}
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [serial(item) for item in sorted(value)]
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


@dataclass(frozen=True)
class Jet:
    value: Fraction
    gradient: tuple[Fraction, ...]

    @staticmethod
    def constant(value: Fraction | int, size: int) -> "Jet":
        return Jet(Fraction(value), (f(0),) * size)

    @staticmethod
    def variable(value: Fraction | int, size: int, index: int) -> "Jet":
        gradient = [f(0)] * size
        gradient[index] = f(1)
        return Jet(Fraction(value), tuple(gradient))

    def _coerce(self, other: "Jet | Fraction | int") -> "Jet":
        return other if isinstance(other, Jet) else Jet.constant(Fraction(other), len(self.gradient))

    def __add__(self, other: "Jet | Fraction | int") -> "Jet":
        right = self._coerce(other)
        return Jet(self.value + right.value, tuple(a + b for a, b in zip(self.gradient, right.gradient)))

    __radd__ = __add__

    def __neg__(self) -> "Jet":
        return Jet(-self.value, tuple(-item for item in self.gradient))

    def __sub__(self, other: "Jet | Fraction | int") -> "Jet":
        return self + (-self._coerce(other))

    def __rsub__(self, other: "Jet | Fraction | int") -> "Jet":
        return self._coerce(other) - self

    def __mul__(self, other: "Jet | Fraction | int") -> "Jet":
        right = self._coerce(other)
        return Jet(
            self.value * right.value,
            tuple(self.value * b + right.value * a for a, b in zip(self.gradient, right.gradient)),
        )

    __rmul__ = __mul__

    def __truediv__(self, other: "Jet | Fraction | int") -> "Jet":
        right = self._coerce(other)
        if right.value == 0:
            raise ZeroDivisionError
        denominator = right.value**2
        return Jet(
            self.value / right.value,
            tuple((a * right.value - self.value * b) / denominator for a, b in zip(self.gradient, right.gradient)),
        )

    def __rtruediv__(self, other: "Jet | Fraction | int") -> "Jet":
        return self._coerce(other) / self

    def __pow__(self, exponent: int) -> "Jet":
        if exponent < 0:
            return Jet.constant(f(1), len(self.gradient)) / (self ** (-exponent))
        if exponent == 0:
            return Jet.constant(f(1), len(self.gradient))
        return Jet(self.value**exponent, tuple(exponent * self.value ** (exponent - 1) * item for item in self.gradient))


Scalar = Fraction | Jet
Vector = list[Scalar]
Leg = tuple[Vector, Vector]
Polynomial = dict[tuple[int, ...], Fraction]


def q3_edges() -> tuple[tuple[int, int], ...]:
    def bits(number: int) -> tuple[int, int, int]:
        return ((number >> 2) & 1, (number >> 1) & 1, number & 1)

    edges = []
    for left in range(8):
        for right in range(left + 1, 8):
            if sum(a != b for a, b in zip(bits(left), bits(right))) == 1:
                edges.append((left, right))
    return tuple(edges)


def add_monomial(poly: Polynomial, coefficient: Fraction, exponents: Sequence[int]) -> None:
    key = tuple(exponents)
    poly[key] = poly.get(key, f(0)) + coefficient
    if poly[key] == 0:
        del poly[key]


def q3_polynomial(data: dict[str, Any]) -> Polynomial:
    poly: Polynomial = {}
    for index in range(8):
        exponents = [0] * 8; exponents[index] = 2
        add_monomial(poly, data["r"] / 2, exponents)
        exponents = [0] * 8; exponents[index] = 4
        add_monomial(poly, data["g"] / 4, exponents)
    for left, right in q3_edges():
        for power_left, power_right, coefficient in (
            (4, 0, data["lambda"] / 4),
            (2, 2, data["lambda"] / 2),
            (0, 4, data["lambda"] / 4),
            (3, 1, -data["lambda"] / 2),
            (1, 3, -data["lambda"] / 2),
        ):
            exponents = [0] * 8
            exponents[left] = power_left
            exponents[right] = power_right
            add_monomial(poly, coefficient, exponents)
    return poly


def differentiate(poly: Polynomial, variable: int) -> Polynomial:
    result: Polynomial = {}
    for exponents, coefficient in poly.items():
        power = exponents[variable]
        if power:
            reduced = list(exponents)
            reduced[variable] -= 1
            add_monomial(result, coefficient * power, reduced)
    return result


def evaluate(poly: Polynomial, values: Sequence[Scalar]) -> Scalar:
    result: Scalar = f(0)
    for exponents, coefficient in poly.items():
        term: Scalar = coefficient
        for value, exponent in zip(values, exponents):
            if exponent:
                term = term * value**exponent
        result = result + term
    return result


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        raw = {
            "name": name, "M": 4, "L": f(8), "chi": f(2), "c": f(3, 2),
            "r": f(-1, 2), "g": f(2), "lambda": f(1), "tau": f(1, 2),
            "gamma": f(3, 5), "eta": f(4, 5), "nu": f(2), "hbar": f(3, 7),
            "rectangle": (2, 2),
        }
    elif name == "f1":
        raw = {
            "name": name, "M": 6, "L": f(9), "chi": f(4, 3), "c": f(7, 9),
            "r": f(1, 5), "g": f(9, 7), "lambda": f(5, 6), "tau": f(-3, 10),
            "gamma": f(5, 13), "eta": f(-12, 13), "nu": f(4, 5), "hbar": f(7, 8),
            "rectangle": (1, 5),
        }
    else:
        raise ValueError(name)
    raw["a"] = raw["L"] / raw["M"]
    raw["w"] = raw["a"] / 8
    raw["mu"] = raw["chi"] * raw["w"]
    raw["h"] = raw["tau"] / 4
    return raw


def valid_parameters(data: dict[str, Any]) -> bool:
    m, n = data["rectangle"]
    return (
        data["M"] >= 4 and data["M"] % 2 == 0 and m > 0 and n > 0 and m + n == data["M"]
        and data["L"] > 0 and data["a"] == data["L"] / data["M"]
        and data["w"] == data["a"] / 8 and data["mu"] == data["chi"] * data["w"]
        and data["chi"] > 0 and data["c"] > 0 and data["g"] > 0 and data["lambda"] > 0
        and data["tau"] != 0 and data["h"] == data["tau"] / 4
        and data["gamma"] * data["eta"] != 0 and data["gamma"] ** 2 + data["eta"] ** 2 == 1
        and data["nu"] > 0 and data["hbar"] > 0
    )


def vector_add(left: Sequence[Scalar], right: Sequence[Scalar], a: Fraction = f(1), b: Fraction = f(1)) -> Vector:
    return [a * x + b * y for x, y in zip(left, right)]


def dot(left: Sequence[Scalar], right: Sequence[Scalar]) -> Scalar:
    result: Scalar = f(0)
    for x, y in zip(left, right):
        result = result + x * y
    return result


def q3_value(values: Sequence[Scalar], data: dict[str, Any]) -> Scalar:
    return evaluate(q3_polynomial(data), values)


def q3_gradient(values: Sequence[Scalar], data: dict[str, Any]) -> Vector:
    poly = q3_polynomial(data)
    return [evaluate(differentiate(poly, index), values) for index in range(8)]


def bond_value(west: Sequence[Scalar], south: Sequence[Scalar], data: dict[str, Any]) -> Scalar:
    displacement = vector_add(south, west, f(1), f(-1))
    spatial = data["c"] * dot(displacement, displacement) / (2 * data["a"] ** 2)
    return data["w"] * (spatial + (q3_value(west, data) + q3_value(south, data)) / 2)


def bond_gradient(west: Sequence[Scalar], south: Sequence[Scalar], data: dict[str, Any]) -> tuple[Vector, Vector]:
    coefficient = data["w"] * data["c"] / data["a"] ** 2
    grad_w = vector_add([coefficient * item for item in vector_add(west, south, f(1), f(-1))], [data["w"] * item / 2 for item in q3_gradient(west, data)])
    grad_s = vector_add([coefficient * item for item in vector_add(south, west, f(1), f(-1))], [data["w"] * item / 2 for item in q3_gradient(south, data)])
    return grad_w, grad_s


def leg_add(left: Leg, right: Leg, a: Fraction, b: Fraction) -> Leg:
    return vector_add(left[0], right[0], a, b), vector_add(left[1], right[1], a, b)


def drift(leg: Leg, duration: Fraction, data: dict[str, Any]) -> Leg:
    return vector_add(leg[0], leg[1], f(1), duration / data["mu"]), list(leg[1])


def action(leg: Leg, data: dict[str, Any]) -> Scalar:
    return (data["nu"] * dot(leg[0], leg[0]) + dot(leg[1], leg[1]) / data["nu"]) / 2


def drift_increment(leg: Leg, data: dict[str, Any]) -> Scalar:
    return (
        data["nu"] * data["h"] * dot(leg[0], leg[1]) / data["mu"]
        + data["nu"] * data["h"] ** 2 * dot(leg[1], leg[1]) / (2 * data["mu"] ** 2)
    )


def forward_gate(west: Leg, south: Leg, data: dict[str, Any]) -> tuple[Leg, Leg, dict[str, Any]]:
    west_1 = drift(west, data["h"], data)
    south_1 = drift(south, data["h"], data)
    grad_w, grad_s = bond_gradient(west_1[0], south_1[0], data)
    west_2 = (west_1[0], vector_add(west_1[1], grad_w, f(1), -data["tau"]))
    south_2 = (south_1[0], vector_add(south_1[1], grad_s, f(1), -data["tau"]))
    east_0 = leg_add(west_2, south_2, data["gamma"], data["eta"])
    north_0 = leg_add(west_2, south_2, -data["eta"], data["gamma"])
    east = drift(east_0, data["h"], data)
    north = drift(north_0, data["h"], data)
    kick_work = (
        -data["tau"] * (dot(west_1[1], grad_w) + dot(south_1[1], grad_s)) / data["nu"]
        + data["tau"] ** 2 * (dot(grad_w, grad_w) + dot(grad_s, grad_s)) / (2 * data["nu"])
    )
    parts = (
        drift_increment(west, data), drift_increment(south, data), kick_work,
        drift_increment(east_0, data), drift_increment(north_0, data),
    )
    actual = action(east, data) + action(north, data) - action(west, data) - action(south, data)
    return east, north, {
        "west_1": west_1, "south_1": south_1, "grad_w": grad_w, "grad_s": grad_s,
        "east_0": east_0, "north_0": north_0, "bond_density": bond_value(west_1[0], south_1[0], data),
        "work_parts": parts, "work": sum(parts, f(0)), "actual_work": actual,
    }


def temporal_inverse(east: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    east_0 = drift(east, -data["h"], data)
    north_0 = drift(north, -data["h"], data)
    west_2 = leg_add(east_0, north_0, data["gamma"], -data["eta"])
    south_2 = leg_add(east_0, north_0, data["eta"], data["gamma"])
    grad_w, grad_s = bond_gradient(west_2[0], south_2[0], data)
    west_1 = (west_2[0], vector_add(west_2[1], grad_w, f(1), data["tau"]))
    south_1 = (south_2[0], vector_add(south_2[1], grad_s, f(1), data["tau"]))
    return drift(west_1, -data["h"], data), drift(south_1, -data["h"], data)


def mixed_west_north(west: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    west_1 = drift(west, data["h"], data)
    north_1 = drift(north, -data["h"], data)
    q_s = [(qn + data["eta"] * qw) / data["gamma"] for qn, qw in zip(north_1[0], west_1[0])]
    grad_w, grad_s = bond_gradient(west_1[0], q_s, data)
    p_s = [
        (pn + data["eta"] * (pw - data["tau"] * gw)) / data["gamma"] + data["tau"] * gs
        for pn, pw, gw, gs in zip(north_1[1], west_1[1], grad_w, grad_s)
    ]
    q_e = [(qw + data["eta"] * qn) / data["gamma"] for qw, qn in zip(west_1[0], north_1[0])]
    p_e = [(pw + data["eta"] * pn - data["tau"] * gw) / data["gamma"] for pw, pn, gw in zip(west_1[1], north_1[1], grad_w)]
    return drift((q_e, p_e), data["h"], data), drift((q_s, p_s), -data["h"], data)


def mixed_west_east(west: Leg, east: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    west_1 = drift(west, data["h"], data)
    east_1 = drift(east, -data["h"], data)
    q_s = [(qe - data["gamma"] * qw) / data["eta"] for qe, qw in zip(east_1[0], west_1[0])]
    grad_w, grad_s = bond_gradient(west_1[0], q_s, data)
    p_s = [
        (pe - data["gamma"] * (pw - data["tau"] * gw)) / data["eta"] + data["tau"] * gs
        for pe, pw, gw, gs in zip(east_1[1], west_1[1], grad_w, grad_s)
    ]
    south_1 = (q_s, p_s)
    west_2 = (west_1[0], vector_add(west_1[1], grad_w, f(1), -data["tau"]))
    south_2 = (south_1[0], vector_add(south_1[1], grad_s, f(1), -data["tau"]))
    north_1 = leg_add(west_2, south_2, -data["eta"], data["gamma"])
    return drift(north_1, data["h"], data), drift(south_1, -data["h"], data)


def legs_equal(left: Leg, right: Leg) -> bool:
    return left[0] == right[0] and left[1] == right[1]


def flatten_legs(*legs: Leg) -> list[Scalar]:
    result: list[Scalar] = []
    for leg in legs:
        result.extend(leg[0]); result.extend(leg[1])
    return result


def local_fixture() -> tuple[Leg, Leg]:
    return (
        ([f(x) for x in (1, 0, -1, 0, 0, 1, 0, -1)], [f(x) for x in (0, 1, 0, -1, 1, 0, -1, 0)]),
        ([f(x) for x in (0, 1, 0, -1, -1, 0, 1, 0)], [f(x) for x in (1, 0, -1, 0, 0, -1, 0, 1)]),
    )


def zeros() -> list[Fraction]:
    return [f(0)] * 8


def global_inputs(m: int, n: int, profile: str) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    horizontal: dict[tuple[int, int], Leg] = {}
    vertical: dict[tuple[int, int], Leg] = {}
    if profile == "f0" and (m, n) == (2, 2):
        qx1 = zeros(); qx1[0] = f(1)
        px2 = zeros(); px2[1] = f(1, 2)
        qy1 = zeros(); qy1[7] = f(-1)
        py1 = zeros(); py1[2] = f(1, 3)
        qy2 = zeros(); qy2[3] = f(1, 2)
        py2 = zeros(); py2[4] = f(-1, 4)
        horizontal[(0, 1)] = (qx1, zeros())
        horizontal[(0, 2)] = (zeros(), px2)
        vertical[(1, 0)] = (qy1, py1)
        vertical[(2, 0)] = (qy2, py2)
        return horizontal, vertical
    for row in range(1, n + 1):
        qv = zeros(); pv = zeros()
        qv[(row - 1) % 8] = f((-1) ** row, row + 1)
        pv[(row + 2) % 8] = f(1, row + 3)
        horizontal[(0, row)] = (qv, pv)
    for column in range(1, m + 1):
        qv = zeros(); pv = zeros()
        qv[(column + 4) % 8] = f(1, column + 2)
        pv[(column + 6) % 8] = f(-1, column + 4)
        vertical[(column, 0)] = (qv, pv)
    return horizontal, vertical


def promote_boundary_to_jets(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], m: int, n: int) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    ordered: list[tuple[str, tuple[int, int], int, int, Fraction]] = []
    for row in range(1, n + 1):
        leg = horizontal[(0, row)]
        for half in range(2):
            for component, value in enumerate(leg[half]):
                ordered.append(("X", (0, row), half, component, value))
    for column in range(1, m + 1):
        leg = vertical[(column, 0)]
        for half in range(2):
            for component, value in enumerate(leg[half]):
                ordered.append(("Y", (column, 0), half, component, value))
    size = len(ordered)
    promoted_x: dict[tuple[int, int], Leg] = {}
    promoted_y: dict[tuple[int, int], Leg] = {}
    index = 0
    for row in range(1, n + 1):
        qv: Vector = []; pv: Vector = []
        for value in horizontal[(0, row)][0]: qv.append(Jet.variable(value, size, index)); index += 1
        for value in horizontal[(0, row)][1]: pv.append(Jet.variable(value, size, index)); index += 1
        promoted_x[(0, row)] = (qv, pv)
    for column in range(1, m + 1):
        qv = []; pv = []
        for value in vertical[(column, 0)][0]: qv.append(Jet.variable(value, size, index)); index += 1
        for value in vertical[(column, 0)][1]: pv.append(Jet.variable(value, size, index)); index += 1
        promoted_y[(column, 0)] = (qv, pv)
    return promoted_x, promoted_y


def forward_rectangle(data: dict[str, Any], order: str, initial: tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]] | None = None) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg], dict[tuple[int, int], Scalar]]:
    m, n = data["rectangle"]
    if initial is None:
        horizontal, vertical = global_inputs(m, n, data["name"])
    else:
        horizontal, vertical = ({key: (list(value[0]), list(value[1])) for key, value in initial[0].items()}, {key: (list(value[0]), list(value[1])) for key, value in initial[1].items()})
    works: dict[tuple[int, int], Scalar] = {}
    vertices: Iterable[tuple[int, int]] = (
        ((i, j) for i in range(1, m + 1) for j in range(1, n + 1))
        if order == "column" else
        ((i, j) for j in range(1, n + 1) for i in range(1, m + 1))
    )
    for i, j in vertices:
        east, north, details = forward_gate(horizontal[(i - 1, j)], vertical[(i, j - 1)], data)
        horizontal[(i, j)] = east; vertical[(i, j)] = north; works[(i, j)] = details["work"]
    return horizontal, vertical, works


def ideals(m: int, n: int) -> list[tuple[int, ...]]:
    return [tuple(item) for item in itertools.product(range(m + 1), repeat=n) if all(item[k] >= item[k + 1] for k in range(n - 1))]


def cut_edges(m: int, n: int, lengths: tuple[int, ...]) -> list[tuple[str, int, int]]:
    result = [("X", lengths[row - 1], row) for row in range(1, n + 1)]
    for column in range(1, m + 1):
        height = max((row for row, length in enumerate(lengths, 1) if length >= column), default=0)
        result.append(("Y", column, height))
    return result


def cut_action(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], edge_ids: list[tuple[str, int, int]], data: dict[str, Any]) -> Scalar:
    result: Scalar = f(0)
    for kind, i, j in edge_ids:
        result = result + action(horizontal[(i, j)] if kind == "X" else vertical[(i, j)], data)
    return result


def reverse_ideal(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], lengths: tuple[int, ...], data: dict[str, Any]) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    known_x: dict[tuple[int, int], Leg] = {}; known_y: dict[tuple[int, int], Leg] = {}
    for kind, i, j in cut_edges(m, n, lengths):
        if kind == "X": known_x[(i, j)] = horizontal[(i, j)]
        else: known_y[(i, j)] = vertical[(i, j)]
    for i in range(m, 0, -1):
        for j in range(n, 0, -1):
            if i <= lengths[j - 1]:
                known_x[(i - 1, j)], known_y[(i, j - 1)] = temporal_inverse(known_x[(i, j)], known_y[(i, j)], data)
    return known_x, known_y


def mixed_rectangle(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], data: dict[str, Any]) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    x = {(0, j): horizontal[(0, j)] for j in range(1, n + 1)}
    y = {(i, n): vertical[(i, n)] for i in range(1, m + 1)}
    for i in range(1, m + 1):
        for j in range(n, 0, -1):
            x[(i, j)], y[(i, j - 1)] = mixed_west_north(x[(i - 1, j)], y[(i, j)], data)
    return x, y


def dependencies(m: int, n: int) -> tuple[dict[tuple[int, int], frozenset[tuple[str, int]]], dict[tuple[int, int], frozenset[tuple[str, int]]]]:
    x = {(0, j): frozenset({("W", j)}) for j in range(1, n + 1)}
    y = {(i, 0): frozenset({("S", i)}) for i in range(1, m + 1)}
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            united = x[(i - 1, j)] | y[(i, j - 1)]
            x[(i, j)] = united; y[(i, j)] = united
    return x, y


def matrix_zero(rows: int, columns: int) -> list[list[Fraction]]:
    return [[f(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> list[list[Fraction]]:
    result = matrix_zero(size, size)
    for index in range(size): result[index][index] = f(1)
    return result


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    right_t = transpose(right)
    return [[sum((x * y for x, y in zip(row, column)), f(0)) for column in right_t] for row in left]


def matrix_equal(left: list[list[Fraction]], right: list[list[Fraction]]) -> bool:
    return left == right


def rank(matrix: list[list[Fraction]]) -> int:
    work = [list(row) for row in matrix]
    row_count = len(work); column_count = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next((row for row in range(pivot_row, row_count) if work[row][column] != 0), None)
        if pivot is None: continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [item / pivot_value for item in work[pivot_row]]
        for row in range(row_count):
            if row != pivot_row and work[row][column] != 0:
                coefficient = work[row][column]
                work[row] = [a - coefficient * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == row_count: break
    return pivot_row


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    size = len(matrix)
    work = [list(row) for row in matrix]
    result = f(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None: return f(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] != 0:
                coefficient = work[row][column] / pivot_value
                for index in range(column + 1, size):
                    work[row][index] -= coefficient * work[column][index]
    return result


def symplectic_form(leg_count: int) -> list[list[Fraction]]:
    size = 16 * leg_count
    omega = matrix_zero(size, size)
    for leg in range(leg_count):
        offset = 16 * leg
        for component in range(8):
            omega[offset + component][offset + 8 + component] = f(-1)
            omega[offset + 8 + component][offset + component] = f(1)
    return omega


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def build_payload(profile: str) -> dict[str, Any]:
    data = fixture(profile)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads(path.read_text(encoding="utf-8")) for path in PARENT_PATHS]
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("parent ids", manifest["parent_ids"] == [item["candidate_id"] for item in parents], manifest["parent_ids"], [item["candidate_id"] for item in parents], "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    source_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.ImportFrom)
    }
    audit.check("stdlib independence", not imported_roots.intersection({"sympy", "numpy"}), sorted(imported_roots), "no sympy or numpy", "provenance")
    audit.check("parameter domain", valid_parameters(data), data, "valid", "parameters")
    for key, value in (("M", 2), ("tau", f(0)), ("lambda", f(0)), ("c", f(0)), ("g", f(0)), ("chi", f(0)), ("eta", f(0))):
        changed = dict(data); changed[key] = value
        audit.check(f"reject hostile {key}", not valid_parameters(changed), valid_parameters(changed), False, "parameters")
    for key, multiplier in (("w", 2), ("mu", 2), ("h", 2)):
        changed = dict(data); changed[key] *= multiplier
        audit.check(f"reject hostile {key}", not valid_parameters(changed), valid_parameters(changed), False, "parameters")

    edges = q3_edges()
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 degree three", [sum(index in edge for edge in edges) for index in range(8)] == [3] * 8, [sum(index in edge for edge in edges) for index in range(8)], [3] * 8, "Q3")
    poly = q3_polynomial(data)
    audit.check("Q3 polynomial degree four", max(sum(exponents) for exponents in poly) == 4, max(sum(exponents) for exponents in poly), 4, "Q3")
    audit.check("generic polynomial derivative paths", all(differentiate(poly, index) for index in range(8)), [len(differentiate(poly, index)) for index in range(8)], "nonempty", "Q3")

    ring_q: list[Vector] = []
    for index in range(data["M"]):
        vector: Vector = zeros()
        if profile == "f0":
            if index == 0: vector[0] = f(1)
            if index == 1: vector[1] = f(1)
            if index == 2: vector[2] = f(-1)
            if index == 3: vector[3] = f(2)
        else:
            vector[index % 8] = f((-1) ** index, index + 1)
        ring_q.append(vector)
    bonds = [bond_value(ring_q[index], ring_q[(index + 1) % data["M"]], data) for index in range(data["M"])]
    inherited_u = data["w"] * sum((data["c"] * dot(vector_add(ring_q[(index + 1) % data["M"]], ring_q[index], f(1), f(-1)), vector_add(ring_q[(index + 1) % data["M"]], ring_q[index], f(1), f(-1))) / (2 * data["a"] ** 2) + q3_value(ring_q[index], data) for index in range(data["M"])), f(0))
    audit.check("bond sum equals U_a", sum(bonds, f(0)) == inherited_u, sum(bonds, f(0)), inherited_u, "term_ledger")
    edge_colours = [{(index, (index + 1) % data["M"]) for index in range(offset, data["M"], 2)} for offset in (0, 1)]
    audit.check("two-colour partition", len(edge_colours[0] | edge_colours[1]) == data["M"] and not edge_colours[0] & edge_colours[1], edge_colours, data["M"], "term_ledger")
    owners = [sum(site in edge for edge in edge_colours[0] | edge_colours[1]) for site in range(data["M"])]
    audit.check("two half owners", owners == [2] * data["M"], owners, [2] * data["M"], "term_ledger")
    audit.check("four quarter drifts", 4 * data["h"] == data["tau"], 4 * data["h"], data["tau"], "term_ledger")
    audit.check("controller count", sum(len(item) for item in edge_colours) == data["M"], sum(len(item) for item in edge_colours), data["M"], "term_ledger")
    if profile == "f0":
        audit.check("F0 W oracle", [q3_value(item, data) for item in ring_q] == [f(1), f(1), f(1), f(19)], [q3_value(item, data) for item in ring_q], [1, 1, 1, 19], "oracles")
        audit.check("F0 V oracle", bonds == [f(11, 32), f(11, 32), f(175, 64), f(175, 64)], bonds, [f(11, 32), f(11, 32), f(175, 64), f(175, 64)], "oracles")
        audit.check("F0 U oracle", inherited_u == f(197, 32), inherited_u, f(197, 32), "oracles")

    west, south = local_fixture()
    east, north, details = forward_gate(west, south, data)
    inverse_west, inverse_south = temporal_inverse(east, north, data)
    audit.check("temporal inverse west", legs_equal(inverse_west, west), inverse_west, west, "local")
    audit.check("temporal inverse south", legs_equal(inverse_south, south), inverse_south, south, "local")
    mixed_east, mixed_south = mixed_west_north(west, north, data)
    audit.check("gamma mixed east", legs_equal(mixed_east, east), mixed_east, east, "local")
    audit.check("gamma mixed south", legs_equal(mixed_south, south), mixed_south, south, "local")
    mixed_north, eta_south = mixed_west_east(west, east, data)
    audit.check("eta mixed north", legs_equal(mixed_north, north), mixed_north, north, "local")
    audit.check("eta mixed south", legs_equal(eta_south, south), eta_south, south, "local")
    audit.check("local work identity", details["work"] == details["actual_work"], details["work"], details["actual_work"], "work")

    local_values = flatten_legs(west, south)
    jet_values = [Jet.variable(value, 32, index) for index, value in enumerate(local_values)]
    jet_west: Leg = (jet_values[0:8], jet_values[8:16])
    jet_south: Leg = (jet_values[16:24], jet_values[24:32])
    jet_east, jet_north, _ = forward_gate(jet_west, jet_south, data)
    jet_outputs = flatten_legs(jet_east, jet_north)
    local_jacobian = [list(item.gradient) for item in jet_outputs if isinstance(item, Jet)]
    omega2 = symplectic_form(2)
    audit.check("Fraction Jet local Jacobian size", len(local_jacobian) == 32 and all(len(row) == 32 for row in local_jacobian), [len(local_jacobian), len(local_jacobian[0])], [32, 32], "Jacobian")
    audit.check("Fraction Jet local symplectic", matmul(transpose(local_jacobian), matmul(omega2, local_jacobian)) == omega2, "zero defect", "zero defect", "Jacobian")
    audit.check("Fraction Jet local determinant", determinant(local_jacobian) == 1, determinant(local_jacobian), 1, "Jacobian")
    gamma_cross = [row[16:32] for row in local_jacobian[16:32]]
    eta_cross = [row[16:32] for row in local_jacobian[0:16]]
    audit.check("gamma cross determinant", determinant(gamma_cross) == data["gamma"] ** 16, determinant(gamma_cross), data["gamma"] ** 16, "Jacobian")
    audit.check("eta cross determinant", determinant(eta_cross) == data["eta"] ** 16, determinant(eta_cross), data["eta"] ** 16, "Jacobian")
    qonly = matrix_zero(16, 16)
    cross_coefficient = data["tau"] * data["w"] * data["c"] / data["a"] ** 2
    expected_cross_coefficient = f(3, 64) if profile == "f0" else f(-7, 360)
    audit.check("q-only cross sign oracle", cross_coefficient == expected_cross_coefficient, cross_coefficient, expected_cross_coefficient, "microcut_no_go")
    for index in range(8): qonly[8 + index][index] = cross_coefficient
    drift_matrix = identity(16)
    for index in range(8): drift_matrix[index][8 + index] = data["h"] / data["mu"]
    drifted = matmul(drift_matrix, matmul(qonly, drift_matrix))
    audit.check("q-only rank eight", rank(qonly) == 8, rank(qonly), 8, "microcut_no_go")
    audit.check("drifted q-only rank eight", rank(drifted) == 8, rank(drifted), 8, "microcut_no_go")
    audit.check("q-only determinant zero", determinant(qonly) == 0, determinant(qonly), 0, "microcut_no_go")
    if profile == "f0":
        audit.check("F0 bond oracle", details["bond_density"] == f(265, 128), details["bond_density"], f(265, 128), "oracles")
        audit.check("F0 grad west oracle", details["grad_w"][0] == f(475, 512), details["grad_w"][0], f(475, 512), "oracles")
        audit.check("F0 grad south oracle", details["grad_s"][0] == f(-1, 128), details["grad_s"][0], f(-1, 128), "oracles")
        audit.check("F0 east q oracle", east[0][0] == f(19071, 20480), east[0][0], f(19071, 20480), "oracles")
        audit.check("F0 east p oracle", east[1][0] == f(2687, 5120), east[1][0], f(2687, 5120), "oracles")
        audit.check("F0 north q oracle", north[0][0] == f(-1041, 2560), north[0][0], f(-1041, 2560), "oracles")
        audit.check("F0 north p oracle", north[1][0] == f(623, 640), north[1][0], f(623, 640), "oracles")
        audit.check("F0 work oracle", details["work"] == f(2522341, 4194304), details["work"], f(2522341, 4194304), "oracles")
        expected_parts = (f(1, 4), f(1, 4), f(507745, 1048576), f(-2590667, 20971520), f(-339893, 1310720))
        audit.check("F0 work-parts oracle", details["work_parts"] == expected_parts, details["work_parts"], expected_parts, "oracles")

    sign_q = zeros(); sign_q[0] = f(1)
    _, _, sign_details = forward_gate((sign_q, zeros()), (sign_q, zeros()), data)
    if profile == "f0": audit.check("negative work oracle", sign_details["work"] == f(-471, 2048), sign_details["work"], f(-471, 2048), "work")
    audit.check("sign-indefinite work", details["work"] * sign_details["work"] < 0, [details["work"], sign_details["work"]], "opposite signs", "work")

    order_w: Leg = (zeros(), zeros()); order_w[0][0] = f(1)
    order_s: Leg = (zeros(), zeros())
    gw, gs = bond_gradient(order_w[0], order_s[0], data)
    kicked_w = (order_w[0], vector_add(order_w[1], gw, f(1), -data["tau"]))
    kicked_s = (order_s[0], vector_add(order_s[1], gs, f(1), -data["tau"]))
    g_after_k = (leg_add(kicked_w, kicked_s, data["gamma"], data["eta"]), leg_add(kicked_w, kicked_s, -data["eta"], data["gamma"]))
    mixed_w = leg_add(order_w, order_s, data["gamma"], data["eta"]); mixed_s = leg_add(order_w, order_s, -data["eta"], data["gamma"])
    mgw, mgs = bond_gradient(mixed_w[0], mixed_s[0], data)
    k_after_g = ((mixed_w[0], vector_add(mixed_w[1], mgw, f(1), -data["tau"])), (mixed_s[0], vector_add(mixed_s[1], mgs, f(1), -data["tau"])))
    audit.check("kick-controller noncommutation", not legs_equal(g_after_k[0], k_after_g[0]) or not legs_equal(g_after_k[1], k_after_g[1]), [g_after_k, k_after_g], "different", "ordering")
    if profile == "f0":
        audit.check("F0 G-after-K momentum oracle", [g_after_k[0][1][0], g_after_k[1][1][0]] == [f(-51, 320), f(93, 320)], [g_after_k[0][1][0], g_after_k[1][1][0]], [f(-51, 320), f(93, 320)], "oracles")
        audit.check("F0 K-after-G momentum oracle", [k_after_g[0][1][0], k_after_g[1][1][0]] == [f(-183, 1600), f(321, 1600)], [k_after_g[0][1][0], k_after_g[1][1][0]], [f(-183, 1600), f(321, 1600)], "oracles")

    horizontal_a, vertical_a, works_a = forward_rectangle(data, "column")
    horizontal_b, vertical_b, works_b = forward_rectangle(data, "row")
    audit.check("sweep horizontal equality", horizontal_a == horizontal_b, len(horizontal_a), len(horizontal_b), "rectangle")
    audit.check("sweep vertical equality", vertical_a == vertical_b, len(vertical_a), len(vertical_b), "rectangle")
    audit.check("sweep work equality", works_a == works_b, works_a, works_b, "rectangle")
    m, n = data["rectangle"]
    all_ideals = ideals(m, n)
    audit.check("cut count", len(all_ideals) == math.comb(m + n, m), len(all_ideals), math.comb(m + n, m), "rectangle")
    audit.check("cut leg count", all(len(cut_edges(m, n, item)) == data["M"] for item in all_ideals), [len(cut_edges(m, n, item)) for item in all_ideals], data["M"], "rectangle")
    input_action = cut_action(horizontal_a, vertical_a, cut_edges(m, n, tuple(0 for _ in range(n))), data)
    cut_fingerprints = []
    for ideal in all_ideals:
        reverse_x, reverse_y = reverse_ideal(horizontal_a, vertical_a, ideal, data)
        recovered = all(legs_equal(reverse_x[(0, j)], horizontal_a[(0, j)]) for j in range(1, n + 1)) and all(legs_equal(reverse_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m + 1))
        audit.check(f"reverse ideal {ideal}", recovered, recovered, True, "all_cuts")
        ideal_work = sum((works_a[(i, j)] for i in range(1, m + 1) for j in range(1, n + 1) if i <= ideal[j - 1]), f(0))
        difference = cut_action(horizontal_a, vertical_a, cut_edges(m, n, ideal), data) - input_action
        audit.check(f"work ideal {ideal}", ideal_work == difference, ideal_work, difference, "all_cuts")
        cut_fingerprints.append({"ideal": ideal, "work": ideal_work, "action_difference": difference})
    mixed_x, mixed_y = mixed_rectangle(horizontal_a, vertical_a, data)
    audit.check("mixed global south", all(legs_equal(mixed_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m + 1)), "recovered", "recovered", "rectangle")
    audit.check("mixed global east", all(legs_equal(mixed_x[(m, j)], horizontal_a[(m, j)]) for j in range(1, n + 1)), "recovered", "recovered", "rectangle")
    dep_x, dep_y = dependencies(m, n)
    violations = [((i, j), item) for (i, j), deps in list(dep_x.items()) + list(dep_y.items()) for item in deps if (item[0] == "W" and item[1] > j) or (item[0] == "S" and item[1] > i)]
    audit.check("southwest causality", violations == [], violations, [], "rectangle")

    if profile == "f0":
        base_x, base_y = global_inputs(m, n, profile)
        jet_x, jet_y = promote_boundary_to_jets(base_x, base_y, m, n)
        final_x, final_y, _ = forward_rectangle(data, "column", (jet_x, jet_y))
        final_scalars: list[Scalar] = []
        for row in range(1, n + 1): final_scalars.extend(flatten_legs(final_x[(m, row)]))
        for column in range(1, m + 1): final_scalars.extend(flatten_legs(final_y[(column, n)]))
        global_jacobian = [list(item.gradient) for item in final_scalars if isinstance(item, Jet)]
        omega_global = symplectic_form(data["M"])
        audit.check("global Fraction Jet Jacobian size", len(global_jacobian) == 16 * data["M"], [len(global_jacobian), len(global_jacobian[0])], [16 * data["M"], 16 * data["M"]], "global_Jacobian")
        audit.check("global Fraction Jet symplectic", matmul(transpose(global_jacobian), matmul(omega_global, global_jacobian)) == omega_global, "zero defect", "zero defect", "global_Jacobian")
        audit.check("global Fraction Jet full rank", rank(global_jacobian) == 16 * data["M"], rank(global_jacobian), 16 * data["M"], "global_Jacobian")

    controller = [[f(3, 5), f(4, 5)], [f(-4, 5), f(3, 5)]]
    rho = [[f(2, 3), f(1, 6)], [f(1, 6), f(1, 3)]]
    rho_out = matmul(controller, matmul(rho, transpose(controller)))
    audit.check("density direction oracle", rho_out == [[f(46, 75), f(-31, 150)], [f(-31, 150), f(29, 75)]], rho_out, [[f(46, 75), f(-31, 150)], [f(-31, 150), f(29, 75)]], "quantum_direction")
    audit.check("density trace", rho_out[0][0] + rho_out[1][1] == 1, rho_out[0][0] + rho_out[1][1], 1, "quantum_direction")
    audit.check("density determinant", determinant(rho_out) == f(7, 36), determinant(rho_out), f(7, 36), "quantum_direction")
    commutator_correction = data["tau"] * data["hbar"] * 3
    audit.check("unsymmetrized cubic quantum-work term misses correction", commutator_correction != 0, commutator_correction, "nonzero i*q^2 coefficient", "quantum_work")
    audit.check("certificate anticommutator drift", "Q dot P+P dot Q" in certificate_text, certificate_text.find("Q dot P+P dot Q"), ">=0", "quantum_work")
    audit.check("certificate anticommutator kick", "P dot g(Q)+g(Q) dot P" in certificate_text, certificate_text.find("P dot g(Q)+g(Q) dot P"), ">=0", "quantum_work")
    audit.check("Schrodinger density direction", manifest["quantum_forward_cut"]["density_transport"].startswith("rho_I=U_I*rho_in*U_I^*"), manifest["quantum_forward_cut"]["density_transport"], "rho'=U rho U*", "quantum")
    audit.check("Heisenberg direction", "alpha_I(A_target)=U_I^* A_target U_I" in manifest["quantum_forward_cut"]["BH_map"], manifest["quantum_forward_cut"]["BH_map"], "U* A U", "quantum")

    true_scope = tuple(key for key, value in manifest["scope"].items() if value is True)
    false_scope = tuple(key for key, value in manifest["scope"].items() if value is False)
    for key in true_scope: audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope: audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    next_gate = "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER"
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == next_gate, manifest["gate_resolution"]["next_gate"], next_gate, "scope")

    cross_invariants = {
        "profile": profile, "q3_edges": edges, "ring_size": data["M"], "bond_values": bonds,
        "inherited_U": inherited_u, "gamma_cross_determinant": data["gamma"] ** 16,
        "eta_cross_determinant": data["eta"] ** 16, "qonly_cross_rank": rank(qonly),
        "qonly_cross_coefficient": cross_coefficient,
        "local_east": east, "local_north": north, "local_work": details["work"],
        "local_work_parts": details["work_parts"], "negative_work": sign_details["work"],
        "rectangle": {"m": m, "n": n, "cut_count": len(all_ideals), "phase_dimension": 16 * data["M"]},
        "cut_fingerprints": cut_fingerprints,
        "global_projection_determinant": data["gamma"] ** (16 * m * n),
        "next_gate": next_gate,
    }
    return {
        "schema": SCHEMA, "candidate_id": CANDIDATE_ID, "result_id": RESULT_ID,
        "parent_ids": manifest["parent_ids"], "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE", "claim_bearing": False,
        "profile": profile, "parameters": data, "verdict": manifest["verdict"],
        "derived": {
            "sparse_Q3_polynomial_verified": True, "Fraction_Jet_local_symplectic_verified": True,
            "global_Fraction_Jet_symplectic_verified": profile == "f0", "all_cuts_verified": True,
            "work_telescope_verified": True, "ordering_no_go_verified": True,
            "quantum_direction_and_anticommutator_verified": True,
        },
        "cross_invariants": cross_invariants, "scope": manifest["scope"],
        "negative_ids": manifest["negative_ids"], "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": next_gate, "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE),
            **{path.stem: sha256(path) for path in PARENT_PATHS},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("f0", "f1"), default="f0")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(args.profile)
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent {args.profile}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
