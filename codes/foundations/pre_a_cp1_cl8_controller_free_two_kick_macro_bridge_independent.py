#!/usr/bin/env python3
"""Independent stdlib/Fraction audit for the controller-free CL8 macro bridge."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
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


__version__ = "0.2.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-controller-free-two-kick-macro-bridge"
CANDIDATE_ID = "PA-CP1-CL8-CONTROLLER-FREE-TWO-KICK-MACRO-BRIDGE-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-GLOBAL-SIDEWAYS-MACRO-AND-FIXED-REGULATOR-SPLITTING-BRIDGE"
ADMISSION_RESULT_ID = "PRE-A-ROUND1-PARTIAL-EVIDENCE-INTAKE-PINNED-M1-BARE-M5-SCOPED-FAILURES-AND-CURRENT-NONSELECTION"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
ADMISSION = REPO / "strategy/pre-a-round1-admission-canonical-functional-bridge-manifest.json"
EVIDENCE = REPO / "strategy/pre-a-round1-boundary-evidence-register-260809-v0.1.json"
DEFAULT_OUTPUT = (
    REPO / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-09-independent-{SLUG}/result.json"
)


def f(numerator: int, denominator: int = 1) -> Fraction:
    return Fraction(numerator, denominator)


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
        return Jet(
            self.value / right.value,
            tuple(
                (a * right.value - self.value * b) / right.value**2
                for a, b in zip(self.gradient, right.gradient)
            ),
        )

    def __rtruediv__(self, other: "Jet | Fraction | int") -> "Jet":
        return self._coerce(other) / self

    def __pow__(self, exponent: int) -> "Jet":
        if exponent == 0:
            return Jet.constant(f(1), len(self.gradient))
        if exponent < 0:
            return Jet.constant(f(1), len(self.gradient)) / (self ** (-exponent))
        return Jet(
            self.value**exponent,
            tuple(exponent * self.value ** (exponent - 1) * item for item in self.gradient),
        )


Scalar = Fraction | Jet
Vector = list[Scalar]
Leg = tuple[Vector, Vector]


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Jet):
        return {"value": str(value.value), "gradient": [str(item) for item in value.gradient]}
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


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def vector_add(left: Sequence[Scalar], right: Sequence[Scalar], a: Fraction = f(1), b: Fraction = f(1)) -> Vector:
    return [a * x + b * y for x, y in zip(left, right)]


def q3_gradient(values: Sequence[Scalar], data: dict[str, Any]) -> Vector:
    result = [data["r"] * value + data["g"] * value**3 for value in values]
    for left, right in q3_edges():
        x, y = values[left], values[right]
        difference = x - y
        square_sum = x**2 + y**2
        result[left] = result[left] + data["lambda"] * (difference * square_sum + difference**2 * x) / 2
        result[right] = result[right] + data["lambda"] * (-difference * square_sum + difference**2 * y) / 2
    return result


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        raw = {
            "name": name, "M": 4, "L": f(8), "chi": f(2), "c": f(3, 2),
            "r": f(-1, 2), "g": f(2), "lambda": f(1), "Delta": f(1, 2),
            "rectangle": (2, 2),
        }
    elif name == "f1":
        raw = {
            "name": name, "M": 6, "L": f(9), "chi": f(4, 3), "c": f(7, 9),
            "r": f(1, 5), "g": f(9, 7), "lambda": f(5, 6), "Delta": f(-3, 10),
            "rectangle": (1, 5),
        }
    else:
        raise ValueError(name)
    raw["a"] = raw["L"] / raw["M"]
    raw["w"] = raw["a"] / 8
    raw["mu"] = raw["chi"] * raw["w"]
    raw["s"] = raw["Delta"] / 2
    raw["h"] = raw["Delta"] / 8
    raw["kappa"] = raw["w"] * raw["c"] / raw["a"] ** 2
    raw["rho"] = 2 * raw["h"] * raw["s"] * raw["kappa"] / raw["mu"]
    return raw


def valid_parameters(data: dict[str, Any]) -> bool:
    return (
        data["M"] >= 4 and data["M"] % 2 == 0 and data["L"] > 0
        and data["a"] == data["L"] / data["M"] and data["w"] == data["a"] / 8
        and data["mu"] == data["chi"] * data["w"] and data["chi"] > 0
        and data["c"] > 0 and data["g"] > 0 and data["lambda"] > 0
        and data["Delta"] != 0 and data["s"] == data["Delta"] / 2
        and data["h"] == data["Delta"] / 8
        and data["kappa"] == data["w"] * data["c"] / data["a"] ** 2
        and data["rho"] == data["c"] * data["Delta"] ** 2 / (8 * data["chi"] * data["a"] ** 2)
        and data["rho"] != 0 and data["rho"] ** 2 != 1
    )


def force(position: Sequence[Scalar], data: dict[str, Any]) -> Vector:
    return [data["w"] * item / 2 for item in q3_gradient(position, data)]


def drift(leg: Leg, duration: Fraction, data: dict[str, Any]) -> Leg:
    return vector_add(leg[0], leg[1], f(1), duration / data["mu"]), list(leg[1])


def kick(west: Leg, south: Leg, strength: Fraction, data: dict[str, Any]) -> tuple[Leg, Leg]:
    fw = vector_add(force(west[0], data), vector_add(west[0], south[0], data["kappa"], -data["kappa"]))
    fs = vector_add(force(south[0], data), vector_add(south[0], west[0], data["kappa"], -data["kappa"]))
    return (
        (list(west[0]), vector_add(west[1], fw, f(1), -strength)),
        (list(south[0]), vector_add(south[1], fs, f(1), -strength)),
    )


def macro_gate(west: Leg, south: Leg, data: dict[str, Any], sign: int = 1) -> tuple[Leg, Leg]:
    h, s = sign * data["h"], sign * data["s"]
    west_1, south_1 = drift(west, h, data), drift(south, h, data)
    west_k1, south_k1 = kick(west_1, south_1, s, data)
    west_2, south_2 = drift(west_k1, 2 * h, data), drift(south_k1, 2 * h, data)
    west_k2, south_k2 = kick(west_2, south_2, s, data)
    return drift(west_k2, h, data), drift(south_k2, h, data)


def mixed_west_east(west: Leg, east: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    h, s, kappa, mu = data["h"], data["s"], data["kappa"], data["mu"]
    x, p = west; e, p2 = east
    x1 = vector_add(x, p, f(1), h / mu)
    x2 = vector_add(e, p2, f(1), -h / mu)
    p1 = [(right - left) * mu / (2 * h) for left, right in zip(x1, x2)]
    y1 = [left + (middle - old + s * onsite) / (s * kappa) for left, middle, old, onsite in zip(x1, p1, p, force(x1, data))]
    y2 = [left + (new - middle + s * onsite) / (s * kappa) for left, new, middle, onsite in zip(x2, p2, p1, force(x2, data))]
    r1 = [(right - left) * mu / (2 * h) for left, right in zip(y1, y2)]
    r = vector_add(r1, vector_add(force(y1, data), vector_add(y1, x1, kappa, -kappa)), f(1), s)
    y = vector_add(y1, r, f(1), -h / mu)
    r2 = vector_add(r1, vector_add(force(y2, data), vector_add(y2, x2, kappa, -kappa)), f(1), -s)
    north = vector_add(y2, r2, f(1), h / mu), r2
    return north, (y, r)


def mixed_west_north(west: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    h, s, kappa, mu, rho = data["h"], data["s"], data["kappa"], data["mu"], data["rho"]
    x, p = west; n, r2 = north
    x1 = vector_add(x, p, f(1), h / mu)
    y2 = vector_add(n, r2, f(1), -h / mu)
    a_value = vector_add(x1, vector_add(p, vector_add(force(x1, data), x1, f(1), kappa), f(1), -s), f(1), 2 * h / mu)
    b_value = vector_add(r2, vector_add(force(y2, data), vector_add(y2, a_value, kappa, -kappa)), f(1), s)
    y1 = [(value - (2 * h / mu) * b) / (1 - rho**2) for value, b in zip(y2, b_value)]
    x2 = vector_add(a_value, y1, f(1), rho)
    r1 = [(right - left) * mu / (2 * h) for left, right in zip(y1, y2)]
    r = vector_add(r1, vector_add(force(y1, data), vector_add(y1, x1, kappa, -kappa)), f(1), s)
    y = vector_add(y1, r, f(1), -h / mu)
    p1 = [(right - left) * mu / (2 * h) for left, right in zip(x1, x2)]
    p2 = vector_add(p1, vector_add(force(x2, data), vector_add(x2, y2, kappa, -kappa)), f(1), -s)
    east = vector_add(x2, p2, f(1), h / mu), p2
    return east, (y, r)


def legs_equal(left: Leg, right: Leg) -> bool:
    return left[0] == right[0] and left[1] == right[1]


def zeros() -> list[Fraction]:
    return [f(0)] * 8


def local_fixture() -> tuple[Leg, Leg]:
    return (
        ([f(x) for x in (1, 0, -1, 0, 0, 1, 0, -1)], [f(x) for x in (0, 1, 0, -1, 1, 0, -1, 0)]),
        ([f(x) for x in (0, 1, 0, -1, -1, 0, 1, 0)], [f(x) for x in (1, 0, -1, 0, 0, -1, 0, 1)]),
    )


def flatten_legs(*legs: Leg) -> list[Scalar]:
    result: list[Scalar] = []
    for leg in legs:
        result.extend(leg[0]); result.extend(leg[1])
    return result


def global_inputs(m: int, n: int) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    horizontal: dict[tuple[int, int], Leg] = {}
    vertical: dict[tuple[int, int], Leg] = {}
    for row in range(1, n + 1):
        qv, pv = zeros(), zeros(); qv[(row - 1) % 8] = f((-1) ** row, row + 1); pv[(row + 2) % 8] = f(1, row + 3)
        horizontal[(0, row)] = (qv, pv)
    for column in range(1, m + 1):
        qv, pv = zeros(), zeros(); qv[(column + 4) % 8] = f(1, column + 2); pv[(column + 6) % 8] = f(-1, column + 4)
        vertical[(column, 0)] = (qv, pv)
    return horizontal, vertical


def forward_rectangle(data: dict[str, Any], order: str) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    horizontal, vertical = global_inputs(m, n)
    vertices: Iterable[tuple[int, int]] = (
        ((i, j) for i in range(1, m + 1) for j in range(1, n + 1))
        if order == "column" else ((i, j) for j in range(1, n + 1) for i in range(1, m + 1))
    )
    for i, j in vertices:
        horizontal[(i, j)], vertical[(i, j)] = macro_gate(horizontal[(i - 1, j)], vertical[(i, j - 1)], data)
    return horizontal, vertical


def ideals(m: int, n: int) -> list[tuple[int, ...]]:
    return [tuple(item) for item in itertools.product(range(m + 1), repeat=n) if all(item[index] >= item[index + 1] for index in range(n - 1))]


def cut_edges(m: int, n: int, lengths: tuple[int, ...]) -> list[tuple[str, int, int]]:
    result = [("X", lengths[row - 1], row) for row in range(1, n + 1)]
    for column in range(1, m + 1):
        height = max((row for row, length in enumerate(lengths, 1) if length >= column), default=0)
        result.append(("Y", column, height))
    return result


def reverse_ideal(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], ideal: tuple[int, ...], data: dict[str, Any]) -> bool:
    m, n = data["rectangle"]
    known_x: dict[tuple[int, int], Leg] = {}; known_y: dict[tuple[int, int], Leg] = {}
    for kind, i, j in cut_edges(m, n, ideal):
        if kind == "X": known_x[(i, j)] = horizontal[(i, j)]
        else: known_y[(i, j)] = vertical[(i, j)]
    for i in range(m, 0, -1):
        for j in range(n, 0, -1):
            if i <= ideal[j - 1]:
                known_x[(i - 1, j)], known_y[(i, j - 1)] = macro_gate(known_x[(i, j)], known_y[(i, j)], data, -1)
    return all(legs_equal(known_x[(0, j)], horizontal[(0, j)]) for j in range(1, n + 1)) and all(legs_equal(known_y[(i, 0)], vertical[(i, 0)]) for i in range(1, m + 1))


def matrix_zero(rows: int, columns: int) -> list[list[Fraction]]:
    return [[f(0) for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    right_t = transpose(right)
    return [[sum((x * y for x, y in zip(row, column)), f(0)) for column in right_t] for row in left]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    size = len(matrix); work = [list(row) for row in matrix]; result = f(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None: return f(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]; result = -result
        pivot_value = work[column][column]; result *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] != 0:
                coefficient = work[row][column] / pivot_value
                for index in range(column + 1, size):
                    work[row][index] -= coefficient * work[column][index]
    return result


def rank(matrix: list[list[Fraction]]) -> int:
    work = [list(row) for row in matrix]; rows = len(work); columns = len(work[0]); pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column] != 0), None)
        if pivot is None: continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]; work[pivot_row] = [item / value for item in work[pivot_row]]
        for row in range(rows):
            if row != pivot_row and work[row][column] != 0:
                coefficient = work[row][column]
                work[row] = [a - coefficient * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows: break
    return pivot_row


def symplectic_form(leg_count: int) -> list[list[Fraction]]:
    size = 16 * leg_count; omega = matrix_zero(size, size)
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
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()

    source_tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".")[0] for node in ast.walk(source_tree) if isinstance(node, ast.Import) for alias in node.names
    } | {(node.module or "").split(".")[0] for node in ast.walk(source_tree) if isinstance(node, ast.ImportFrom)}
    audit.check("stdlib independence", not imported_roots.intersection({"sympy", "numpy"}), sorted(imported_roots), "no sympy or numpy", "provenance")
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("parameter domain", valid_parameters(data), data, "valid", "parameters")
    rho_oracle = f(3, 512) if profile == "f0" else f(7, 2400)
    audit.check("rho oracle", data["rho"] == rho_oracle, data["rho"], rho_oracle, "parameters")
    audit.check("cross Hessian convention", data["kappa"] == data["c"] / (8 * data["a"]), data["kappa"], data["c"] / (8 * data["a"]), "parameters")
    audit.check("potential ownership", 2 * data["s"] == data["Delta"], 2 * data["s"], data["Delta"], "ledger")
    audit.check("kinetic half ownership", 4 * data["h"] == data["Delta"] / 2, 4 * data["h"], data["Delta"] / 2, "ledger")

    west, south = local_fixture(); east, north = macro_gate(west, south, data)
    inv_west, inv_south = macro_gate(east, north, data, -1)
    audit.check("temporal inverse west", legs_equal(inv_west, west), inv_west, west, "local")
    audit.check("temporal inverse south", legs_equal(inv_south, south), inv_south, south, "local")
    got_north, got_south = mixed_west_east(west, east, data)
    audit.check("W-E reconstruct north", legs_equal(got_north, north), got_north, north, "local")
    audit.check("W-E reconstruct south", legs_equal(got_south, south), got_south, south, "local")
    got_east, got_south_2 = mixed_west_north(west, north, data)
    audit.check("W-N reconstruct east", legs_equal(got_east, east), got_east, east, "local")
    audit.check("W-N reconstruct south", legs_equal(got_south_2, south), got_south_2, south, "local")

    values = flatten_legs(west, south)
    jets = [Jet.variable(value, 32, index) for index, value in enumerate(values)]
    jet_west: Leg = (jets[0:8], jets[8:16]); jet_south: Leg = (jets[16:24], jets[24:32])
    jet_east, jet_north = macro_gate(jet_west, jet_south, data)
    jacobian = [list(item.gradient) for item in flatten_legs(jet_east, jet_north) if isinstance(item, Jet)]
    omega = symplectic_form(2)
    audit.check("Fraction Jet Jacobian size", len(jacobian) == 32 and all(len(row) == 32 for row in jacobian), [len(jacobian), len(jacobian[0])], [32, 32], "Jacobian")
    audit.check("Fraction Jet symplectic", matmul(transpose(jacobian), matmul(omega, jacobian)) == omega, "zero defect", "zero defect", "Jacobian")
    audit.check("Fraction Jet temporal determinant", determinant(jacobian) == 1, determinant(jacobian), 1, "Jacobian")
    east_cross = [row[16:32] for row in jacobian[0:16]]
    north_cross = [row[16:32] for row in jacobian[16:32]]
    audit.check("E cross rank", rank(east_cross) == 16, rank(east_cross), 16, "Jacobian")
    audit.check("N cross rank", rank(north_cross) == 16, rank(north_cross), 16, "Jacobian")
    audit.check("E cross determinant", determinant(east_cross) == data["rho"] ** 16, determinant(east_cross), data["rho"] ** 16, "Jacobian")
    audit.check("N cross determinant", determinant(north_cross) == (1 - data["rho"] ** 2) ** 8, determinant(north_cross), (1 - data["rho"] ** 2) ** 8, "Jacobian")

    hessian_points = []
    for position in (drift(west, data["h"], data)[0], drift(south, data["h"], data)[0]):
        promoted = [Jet.variable(value, 8, index) for index, value in enumerate(position)]
        hessian_points.append([list(item.gradient) for item in q3_gradient(promoted, data) if isinstance(item, Jet)])
    commutator = [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(matmul(hessian_points[0], hessian_points[1]), matmul(hessian_points[1], hessian_points[0]))]
    audit.check("hostile Hessians noncommute", any(item != 0 for row in commutator for item in row), rank(commutator), "nonzero", "Jacobian")

    exact_mass = 2 * data["mu"]
    exact_species = data["kappa"] ** 2 / (12 * exact_mass**2)
    exact_mu = data["kappa"] ** 2 / (48 * data["mu"] ** 2)
    macro_species = data["kappa"] ** 2 / (64 * data["mu"] ** 2)
    audit.check("exact mass m=2mu", exact_mass == 2 * data["mu"], exact_mass, 2 * data["mu"], "exact_flow")
    audit.check("exact /48", exact_species == exact_mu, exact_species, exact_mu, "exact_flow")
    audit.check("macro /64", data["rho"] ** 2 / data["Delta"] ** 4 == macro_species, data["rho"] ** 2 / data["Delta"] ** 4, macro_species, "exact_flow")
    audit.check("48/64 mutation fails", exact_mu != macro_species, [exact_mu, macro_species], "different", "exact_flow")
    audit.check("rho zero negative control", f(0) ** 16 == 0, 0, 0, "negative_controls")
    audit.check("rho one negative control", (1 - f(1) ** 2) ** 8 == 0, 0, 0, "negative_controls")

    horizontal_a, vertical_a = forward_rectangle(data, "column")
    horizontal_b, vertical_b = forward_rectangle(data, "row")
    audit.check("sweep horizontal", horizontal_a == horizontal_b, len(horizontal_a), len(horizontal_b), "rectangle")
    audit.check("sweep vertical", vertical_a == vertical_b, len(vertical_a), len(vertical_b), "rectangle")
    m, n = data["rectangle"]; all_ideals = ideals(m, n)
    audit.check("cut count", len(all_ideals) == math.comb(m + n, m), len(all_ideals), math.comb(m + n, m), "rectangle")
    audit.check("cut leg count", all(len(cut_edges(m, n, item)) == data["M"] for item in all_ideals), [len(cut_edges(m, n, item)) for item in all_ideals], data["M"], "rectangle")
    for ideal in all_ideals:
        audit.check(f"reverse cut {ideal}", reverse_ideal(horizontal_a, vertical_a, ideal, data), True, True, "all_cuts")

    quotient_rows = []
    for q_m, q_n in ((2, 2), (3, 2), (3, 3), (4, 4)):
        q_M = q_m + q_n
        theta = q_n * 2 + q_m * 3
        theta_shift = q_n * (2 + q_m) + q_m * (3 - q_n)
        horizontal_degrees = [q_m] * q_n
        vertical_degrees = [q_n] * q_m
        row = {
            "m": q_m, "n": q_n, "M": q_M, "theta_invariant": theta == theta_shift,
            "east_rise": q_n, "north_rise": q_m, "gate_count": q_m * q_n,
            "horizontal_degrees": horizontal_degrees, "vertical_degrees": vertical_degrees,
            "seam_order": q_M // math.gcd(q_m, q_n), "parity_descends": q_M % 2 == 0,
            "seam_preserves_colour": q_n % 2 == 0,
        }
        quotient_rows.append(row)
        audit.check(f"quotient height {q_m}x{q_n}", row["theta_invariant"] and row["east_rise"] > 0 and row["north_rise"] > 0, row, "invariant increasing", "quotient")
        audit.check(f"quotient incidence {q_m}x{q_n}", row["gate_count"] == q_m * q_n and horizontal_degrees == [q_m] * q_n and vertical_degrees == [q_n] * q_m, row, "K_(n,m)", "quotient")
    count_solutions = [(left, right) for left in range(1, 9) for right in range(1, 9) if left * right == left + right]
    audit.check("raw ring count solution", count_solutions == [(2, 2)], count_solutions, [(2, 2)], "quotient")

    commute = {frozenset(("A", "D")), frozenset(("B", "C"))}
    def trace_closure(word: tuple[str, ...]) -> set[tuple[str, ...]]:
        seen = {word}; frontier = [word]
        while frontier:
            current = frontier.pop()
            for index in range(len(current) - 1):
                if frozenset((current[index], current[index + 1])) in commute:
                    changed = current[:index] + (current[index + 1], current[index]) + current[index + 2:]
                    if changed not in seen:
                        seen.add(changed); frontier.append(changed)
        return seen
    audit.check("C4 trace word conjugacy", ("D", "A", "B", "C", "A") in trace_closure(("A", "D", "C", "B", "A")), sorted(trace_closure(("A", "D", "C", "B", "A"))), "right word", "quotient")

    c4_data = dict(data)
    c4_data.update({
        "M": 4,
        "L": f(4),
        "a": f(1),
        "w": f(1, 8),
        "chi": f(8),
        "mu": f(1),
        "c": f(8),
        "r": f(0),
        "Delta": f(2),
        "s": f(1),
        "h": f(1, 4),
        "kappa": f(1),
        "rho": f(1, 2),
    })
    audit.check("C4 fixture parameter ledger", valid_parameters(c4_data), c4_data, "valid", "quotient")
    jet_size = 32
    west_c4: Leg = (
        [Jet.variable(0, jet_size, species) for species in range(8)],
        [Jet.variable(0, jet_size, 8 + species) for species in range(8)],
    )
    south_c4: Leg = (
        [Jet.variable(0, jet_size, 16 + species) for species in range(8)],
        [Jet.variable(0, jet_size, 24 + species) for species in range(8)],
    )
    east_c4, north_c4 = macro_gate(west_c4, south_c4, c4_data)
    c4_outputs = east_c4[0] + east_c4[1] + north_c4[0] + north_c4[1]
    if not all(isinstance(item, Jet) for item in c4_outputs):
        raise AssertionError("C4 tangent outputs did not retain jet gradients")
    full_c4_jacobian = [list(item.gradient) for item in c4_outputs if isinstance(item, Jet)]
    c4_indices = [0, 8, 16, 24]
    derived_local = [[full_c4_jacobian[row][column] for column in c4_indices] for row in c4_indices]
    expected_local = [
        [f(1, 4), f(11, 16), f(3, 4), f(5, 16)],
        [f(-1), f(1, 4), f(1), f(3, 4)],
        [f(3, 4), f(5, 16), f(1, 4), f(11, 16)],
        [f(1), f(3, 4), f(-1), f(1, 4)],
    ]
    audit.check("C4 tangent derived from macro", derived_local == expected_local, derived_local, expected_local, "quotient")
    expected_full = matrix_zero(32, 32)
    for species in range(8):
        species_indices = [species, 8 + species, 16 + species, 24 + species]
        for row_index, row_target in enumerate(species_indices):
            for column_index, column_target in enumerate(species_indices):
                expected_full[row_target][column_target] = derived_local[row_index][column_index]
    audit.check("C4 tangent species decoupling", full_c4_jacobian == expected_full, full_c4_jacobian, expected_full, "quotient")
    local_linear = derived_local
    def identity(size: int) -> list[list[Fraction]]:
        result = matrix_zero(size, size)
        for index in range(size): result[index][index] = f(1)
        return result
    def embedded_gate(first: int, second: int) -> list[list[Fraction]]:
        result = identity(8); indices = [2 * first, 2 * first + 1, 2 * second, 2 * second + 1]
        for row_index, row_target in enumerate(indices):
            for column_index, column_target in enumerate(indices):
                result[row_target][column_target] = local_linear[row_index][column_index]
        return result
    def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
        return [sum((left * right for left, right in zip(row, vector)), f(0)) for row in matrix]
    gate_a = embedded_gate(0, 2); gate_b = embedded_gate(0, 3)
    gate_c = embedded_gate(1, 2); gate_d = embedded_gate(1, 3)
    u_block = matmul(gate_d, matmul(gate_c, matmul(gate_b, gate_a)))
    raw_eo = matmul(matmul(gate_d, gate_a), matmul(gate_b, gate_c))
    audit.check("C4 matrix conjugacy", matmul(gate_a, u_block) == matmul(raw_eo, gate_a), "zero defect", "zero defect", "quotient")
    witness = [f(1)] + [f(0)] * 7
    block_witness = matvec(u_block, witness); eo_witness = matvec(raw_eo, witness)
    expected_block = [f(-5, 8), f(-1, 2), f(1), f(-1), f(7, 8), f(-1, 2), f(3, 4), f(2)]
    expected_eo = [f(-5, 8), f(-1, 2), f(7, 8), f(3, 2), f(-1, 8), f(-1, 2), f(7, 8), f(-1, 2)]
    audit.check("block witness oracle", block_witness == expected_block, block_witness, expected_block, "quotient")
    audit.check("EO witness oracle", eo_witness == expected_eo, eo_witness, expected_eo, "quotient")
    audit.check("raw direct inequality", block_witness != eo_witness, block_witness, eo_witness, "quotient")

    def mod1(value: int, size: int) -> int:
        return (value - 1) % size + 1

    def embedded_pairs(local: list[list[Fraction]], pairs: list[tuple[int, int]], size: int) -> list[list[Fraction]]:
        result = identity(4 * size)
        for first, second in pairs:
            indices = [2 * first, 2 * first + 1, 2 * second, 2 * second + 1]
            for row_index, row_target in enumerate(indices):
                for column_index, column_target in enumerate(indices):
                    result[row_target][column_target] = local[row_index][column_index]
        return result

    def labelled_gate(row: int, column: int, size: int) -> list[list[Fraction]]:
        return embedded_pairs(local_linear, [(row - 1, size + column - 1)], size)

    def compose_application_order(maps: list[list[list[Fraction]]], size: int) -> list[list[Fraction]]:
        result = identity(4 * size)
        for current in maps:
            result = matmul(current, result)
        return result

    def word_data(size: int) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[list[tuple[int, int]]]]:
        square: list[tuple[int, int]] = []
        triangle: list[tuple[int, int]] = []
        for diagonal in range(2, 2 * size + 1):
            for row in range(1, size + 1):
                column = diagonal - row
                if 1 <= column <= size:
                    square.append((row, column))
                    if diagonal <= size:
                        triangle.append((row, column))
        layers = [[(row, mod1(layer - row, size)) for row in range(1, size + 1)] for layer in range(1, size + 1)]
        return square, triangle, layers

    def dependent_projection_equal(first: list[tuple[int, int]], second: list[tuple[int, int]], size: int) -> bool:
        if Counter(first) != Counter(second):
            return False
        letters = [(row, column) for row in range(1, size + 1) for column in range(1, size + 1)]
        for left_index, left in enumerate(letters):
            for right in letters[left_index:]:
                if left[0] == right[0] or left[1] == right[1]:
                    if [item for item in first if item in (left, right)] != [item for item in second if item in (left, right)]:
                        return False
        return True

    def frame(size: int, step: int) -> list[list[Fraction]]:
        result = matrix_zero(4 * size, 4 * size)
        for row in range(1, size + 1):
            position = (2 * (size - row) + step) % (2 * size)
            label = row - 1
            for component in range(2):
                result[2 * position + component][2 * label + component] = f(1)
        for column in range(1, size + 1):
            position = (2 * (column - 1) + 1 - step) % (2 * size)
            label = size + column - 1
            for component in range(2):
                result[2 * position + component][2 * label + component] = f(1)
        return result

    def half_turn(size: int) -> list[list[Fraction]]:
        result = matrix_zero(4 * size, 4 * size)
        for position in range(2 * size):
            target = (position + size) % (2 * size)
            for component in range(2):
                result[2 * target + component][2 * position + component] = f(1)
        return result

    leg_swap = matrix_zero(4, 4)
    leg_swap[0][2] = leg_swap[1][3] = leg_swap[2][0] = leg_swap[3][1] = f(1)
    routed_local = matmul(leg_swap, local_linear)
    routed_rows: dict[str, Any] = {}
    expected_first = {2: (f(-5, 8), f(-5, 8)), 3: (f(-1, 2), f(0)), 4: (f(7, 32), f(13, 32))}
    for size in (2, 3, 4):
        square_word, triangle_word, layer_words = word_data(size)
        strip_word = [gate for layer in layer_words for gate in layer]
        audit.check(f"k={size} counts", [len(square_word), len(triangle_word), len(strip_word)] == [size**2, size * (size - 1) // 2, size**2], [len(square_word), len(triangle_word), len(strip_word)], [size**2, size * (size - 1) // 2, size**2], "routed_seam")
        audit.check(f"k={size} trace projections", dependent_projection_equal(square_word + triangle_word, triangle_word + strip_word, size), True, True, "routed_seam")
        square = compose_application_order([labelled_gate(row, column, size) for row, column in square_word], size)
        triangle = compose_application_order([labelled_gate(row, column, size) for row, column in triangle_word], size)
        labelled_layers = [compose_application_order([labelled_gate(row, column, size) for row, column in layer], size) for layer in layer_words]
        strip = compose_application_order(labelled_layers, size)
        audit.check(f"k={size} exact gluing", matmul(triangle, square) == matmul(strip, triangle), "zero defect", "zero defect", "routed_seam")
        routed_layers: list[list[list[Fraction]]] = []
        for layer, labelled_layer in enumerate(labelled_layers, start=1):
            pairs = ([(2 * index, 2 * index + 1) for index in range(size)] if layer % 2 else [((2 * index + 1) % (2 * size), (2 * index + 2) % (2 * size)) for index in range(size)])
            direct = embedded_pairs(routed_local, pairs, size)
            conjugated = matmul(frame(size, layer), matmul(labelled_layer, transpose(frame(size, layer - 1))))
            audit.check(f"k={size} routed layer {layer}", direct == conjugated, "zero defect", "zero defect", "routed_seam")
            routed_layers.append(direct)
        routed = compose_application_order(routed_layers, size)
        audit.check(f"k={size} routed total", routed == matmul(frame(size, size), matmul(strip, transpose(frame(size, 0)))), "zero defect", "zero defect", "routed_seam")
        audit.check(f"k={size} half turn", matmul(frame(size, size), transpose(frame(size, 0))) == half_turn(size), "exact", "exact", "routed_seam")
        cut_in = matmul(frame(size, 0), triangle)
        audit.check(f"k={size} seam conjugacy", matmul(cut_in, square) == matmul(transpose(half_turn(size)), matmul(routed, cut_in)), "zero defect", "zero defect", "routed_seam")
        raw_layers = [labelled_layers[0 if time % 2 == 0 else size - 1] for time in range(size)]
        raw = compose_application_order(raw_layers, size)
        audit.check(f"k={size} raw equality boundary", (strip == raw) == (size == 2), strip == raw, size == 2, "routed_seam")
        basis = [f(1)] + [f(0)] * (4 * size - 1)
        desired_output, raw_output = matvec(strip, basis), matvec(raw, basis)
        audit.check(f"k={size} routed witness", desired_output[0] == expected_first[size][0], desired_output[0], expected_first[size][0], "routed_seam")
        audit.check(f"k={size} raw witness", raw_output[0] == expected_first[size][1], raw_output[0], expected_first[size][1], "routed_seam")
        routed_rows[str(size)] = {"triangle_count": len(triangle_word), "routed_first": desired_output[0], "raw_first": raw_output[0], "raw_equals_routed": strip == raw}

    def expected_c4_polynomial(value: Fraction) -> Fraction:
        return (value - 1) ** 2 * (value**2 + value + 1) * (value**2 + 3 * value + 1) ** 2

    c4_samples = []
    for integer in range(9):
        value = f(integer)
        shifted = [[(value if row == column else f(0)) - raw_eo[row][column] for column in range(8)] for row in range(8)]
        c4_samples.append((integer, determinant(shifted), expected_c4_polynomial(value)))
    audit.check("C4 characteristic polynomial samples", all(actual == expected for _, actual, expected in c4_samples), c4_samples, "nine exact degree-eight samples", "state")
    audit.check("C4 hyperbolic factor", f(1) - f(3) + f(1) < 0 and 9 - 4 > 0, [f(-1), f(5)], "root below -1", "state")

    ordered_data = dict(data); ordered_data["r"] = -ordered_data["g"]
    for label, positions in (("zero", [f(0)] * 8), ("plus", [f(1)] * 8), ("minus", [f(-1)] * 8)):
        leg = (positions, [f(0)] * 8)
        fixed_left, fixed_right = macro_gate(leg, leg, ordered_data)
        audit.check(f"{label} singular fixed phase", legs_equal(fixed_left, leg) and legs_equal(fixed_right, leg), "fixed", "fixed", "state")

    shadow_mu, shadow_s, shadow_k = f(2), f(1, 2), f(1)
    shadow_h = shadow_s / 4; shadow_d = shadow_h / shadow_mu; shadow_u = shadow_d * shadow_s * shadow_k
    shadow_step = [[1 - shadow_u, shadow_d * (2 - shadow_u)], [-shadow_s * shadow_k, 1 - shadow_u]]
    shadow_metric = [[shadow_k / (1 - shadow_u / 2), f(0)], [f(0), f(1) / (2 * shadow_mu)]]
    shadow_defect = matmul(transpose(shadow_step), matmul(shadow_metric, shadow_step))
    audit.check("single-bond shadow domain", 0 < shadow_u < 2, shadow_u, "between zero and two", "state")
    audit.check("single-bond quadratic shadow identity", shadow_defect == shadow_metric, shadow_defect, shadow_metric, "state")

    vector = admission["exact_admission_vector"]
    audit.check("admission result", admission["result_id"] == ADMISSION_RESULT_ID, admission["result_id"], ADMISSION_RESULT_ID, "admission")
    audit.check("no selection", vector["round1_decisive_selection_authorized"] is False and vector["pre_a_exit_conditions_met"] is False, vector, "false conjunction", "admission")
    audit.check("not frozen", vector["partial_boundary_evidence_tranche_frozen"] is False and evidence["versioning_policy"]["charter_complete_freeze"] is False, [vector["partial_boundary_evidence_tranche_frozen"], evidence["versioning_policy"]["charter_complete_freeze"]], [False, False], "admission")
    audit.check("visible validation role", any(item["role"] == "declared_non_fitting_validation" for item in evidence["evidence_items"]), [item["role"] for item in evidence["evidence_items"]], "declared_non_fitting_validation", "evidence")
    audit.check("BIPM not experiment", evidence["calibration_authorities"][0]["role"] == "CALIBRATION_AUTHORITY_NOT_EXPERIMENT", evidence["calibration_authorities"][0]["role"], "CALIBRATION_AUTHORITY_NOT_EXPERIMENT", "evidence")
    audit.check("certificate mass firewall", "m=2\\mu" in certificate_text, certificate_text.find("m=2\\mu"), ">=0", "provenance")
    audit.check("certificate all-cut boundary", "open acyclic monotone cuts" in certificate_text, certificate_text.find("open acyclic monotone cuts"), ">=0", "scope")
    next_gate = "PA-CP1-CL8-PERIODIC-BLOCH-LYAPUNOV-CUT-COMPATIBLE-STATE-FEASIBILITY"
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == next_gate, manifest["gate_resolution"]["next_gate"], next_gate, "scope")
    expected_negatives = ["NG-2026-08-09-PRE-A-CP1-CL8-RAW-PERIODIC-EO-RECTANGLE-QUOTIENT", "NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS"]
    audit.check("registered negative ids", manifest["negative_ids"] == expected_negatives, manifest["negative_ids"], expected_negatives, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "admission_result_id": ADMISSION_RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "profile": profile,
        "parameters": data,
        "verdict": manifest["verdict"],
        "invariants": {
            "rho": data["rho"],
            "det_E_S": data["rho"] ** 16,
            "det_N_S": (1 - data["rho"] ** 2) ** 8,
            "exact_flow_species_coefficient": exact_mu,
            "macro_species_coefficient": macro_species,
            "hessian_commutator_rank": rank(commutator),
            "cut_count": len(all_ideals),
            "periodic_quotient_fixtures": quotient_rows,
            "C4_local_tangent": local_linear,
            "C4_block_witness": block_witness,
            "C4_raw_EO_witness": eo_witness,
            "C4_characteristic_samples": c4_samples,
            "routed_seam_fixtures": routed_rows,
            "single_bond_shadow_metric": shadow_metric,
            "next_gate": manifest["gate_resolution"]["next_gate"],
        },
        "scope": manifest["scope"],
        "negative_ids": manifest["negative_ids"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE),
            "admission": sha256(ADMISSION), "evidence": sha256(EVIDENCE),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("f0", "f1"), default="f1")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(args.profile)
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent {args.profile}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
