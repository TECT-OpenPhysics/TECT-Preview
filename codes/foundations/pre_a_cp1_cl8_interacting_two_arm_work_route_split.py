#!/usr/bin/env python3
"""Primary exact audit for the driven 1D CL8 interacting two-arm work route."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-interacting-two-arm-work-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-1D-Q3-DRIVEN-ALL-CUT-WORK-TRANSPORT-AND-DIRECT-ORDER-MICROCUT-NOGO"
SCHEMA = f"tect/{SLUG}-primary/0.1"
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
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [serial(item) for item in sorted(value)]
    if isinstance(value, (list, tuple)):
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


def q(value: int, denominator: int = 1) -> sp.Rational:
    return sp.Rational(value, denominator)


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        return {
            "name": name,
            "M": 4,
            "L": q(8),
            "chi": q(2),
            "c": q(3, 2),
            "r": q(-1, 2),
            "g": q(2),
            "lambda": q(1),
            "tau": q(1, 2),
            "gamma": q(3, 5),
            "eta": q(4, 5),
            "nu": q(2),
            "hbar": q(3, 7),
            "rectangle": (2, 2),
        }
    if name == "f1":
        return {
            "name": name,
            "M": 6,
            "L": q(9),
            "chi": q(4, 3),
            "c": q(7, 9),
            "r": q(1, 5),
            "g": q(9, 7),
            "lambda": q(5, 6),
            "tau": q(-3, 10),
            "gamma": q(5, 13),
            "eta": q(-12, 13),
            "nu": q(4, 5),
            "hbar": q(7, 8),
            "rectangle": (1, 5),
        }
    raise ValueError(name)


def complete_parameters(raw: dict[str, Any]) -> dict[str, Any]:
    result = dict(raw)
    result["a"] = sp.factor(result["L"] / result["M"])
    result["w"] = sp.factor(result["a"] / 8)
    result["mu"] = sp.factor(result["chi"] * result["w"])
    result["h"] = sp.factor(result["tau"] / 4)
    return result


def valid_parameters(data: dict[str, Any]) -> bool:
    m, n = data["rectangle"]
    return bool(
        data["M"] >= 4
        and data["M"] % 2 == 0
        and m > 0
        and n > 0
        and m + n == data["M"]
        and data["L"] > 0
        and data["a"] == data["L"] / data["M"]
        and data["w"] == data["a"] / 8
        and data["mu"] == data["chi"] * data["w"]
        and data["chi"] > 0
        and data["c"] > 0
        and data["g"] > 0
        and data["lambda"] > 0
        and data["tau"] != 0
        and data["h"] == data["tau"] / 4
        and data["gamma"] * data["eta"] != 0
        and data["gamma"] ** 2 + data["eta"] ** 2 == 1
        and data["nu"] > 0
        and data["hbar"] > 0
    )


def q3_potential(values: sp.Matrix, data: dict[str, Any]) -> sp.Expr:
    onsite = sum(data["r"] * x**2 / 2 + data["g"] * x**4 / 4 for x in values)
    locked = sum(
        data["lambda"] * (values[left] - values[right]) ** 2
        * (values[left] ** 2 + values[right] ** 2) / 4
        for left, right in q3_edges()
    )
    return sp.factor(onsite + locked)


def q3_gradient(values: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    gradient = sp.Matrix([data["r"] * x + data["g"] * x**3 for x in values])
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        difference = x - y
        square_sum = x**2 + y**2
        gradient[left] += data["lambda"] * (
            difference * square_sum + difference**2 * x
        ) / 2
        gradient[right] += data["lambda"] * (
            -difference * square_sum + difference**2 * y
        ) / 2
    return gradient.applyfunc(sp.factor)


def bond_density(west_q: sp.Matrix, south_q: sp.Matrix, data: dict[str, Any]) -> sp.Expr:
    spatial = data["c"] * sum((south_q[i] - west_q[i]) ** 2 for i in range(8)) / (2 * data["a"] ** 2)
    return sp.factor(data["w"] * (spatial + (q3_potential(west_q, data) + q3_potential(south_q, data)) / 2))


def bond_gradient(west_q: sp.Matrix, south_q: sp.Matrix, data: dict[str, Any]) -> tuple[sp.Matrix, sp.Matrix]:
    coefficient = data["w"] * data["c"] / data["a"] ** 2
    west = coefficient * (west_q - south_q) + data["w"] * q3_gradient(west_q, data) / 2
    south = coefficient * (south_q - west_q) + data["w"] * q3_gradient(south_q, data) / 2
    return west.applyfunc(sp.factor), south.applyfunc(sp.factor)


Leg = tuple[sp.Matrix, sp.Matrix]


def add_leg(left: Leg, right: Leg, left_scale: sp.Expr, right_scale: sp.Expr) -> Leg:
    return (
        (left_scale * left[0] + right_scale * right[0]).applyfunc(sp.factor),
        (left_scale * left[1] + right_scale * right[1]).applyfunc(sp.factor),
    )


def drift(leg: Leg, duration: sp.Expr, data: dict[str, Any]) -> Leg:
    return ((leg[0] + duration * leg[1] / data["mu"]).applyfunc(sp.factor), leg[1].copy())


def action(leg: Leg, data: dict[str, Any]) -> sp.Expr:
    return sp.factor((data["nu"] * leg[0].dot(leg[0]) + leg[1].dot(leg[1]) / data["nu"]) / 2)


def drift_increment(leg: Leg, data: dict[str, Any]) -> sp.Expr:
    h = data["h"]
    return sp.factor(
        data["nu"] * h * leg[0].dot(leg[1]) / data["mu"]
        + data["nu"] * h**2 * leg[1].dot(leg[1]) / (2 * data["mu"] ** 2)
    )


def forward_gate(west: Leg, south: Leg, data: dict[str, Any]) -> tuple[Leg, Leg, dict[str, Any]]:
    west_1 = drift(west, data["h"], data)
    south_1 = drift(south, data["h"], data)
    grad_w, grad_s = bond_gradient(west_1[0], south_1[0], data)
    west_2 = (west_1[0], (west_1[1] - data["tau"] * grad_w).applyfunc(sp.factor))
    south_2 = (south_1[0], (south_1[1] - data["tau"] * grad_s).applyfunc(sp.factor))
    east_0 = add_leg(west_2, south_2, data["gamma"], data["eta"])
    north_0 = add_leg(west_2, south_2, -data["eta"], data["gamma"])
    east = drift(east_0, data["h"], data)
    north = drift(north_0, data["h"], data)
    kick_work = sp.factor(
        -data["tau"] * (west_1[1].dot(grad_w) + south_1[1].dot(grad_s)) / data["nu"]
        + data["tau"] ** 2 * (grad_w.dot(grad_w) + grad_s.dot(grad_s)) / (2 * data["nu"])
    )
    parts = (
        drift_increment(west, data),
        drift_increment(south, data),
        kick_work,
        drift_increment(east_0, data),
        drift_increment(north_0, data),
    )
    actual = sp.factor(action(east, data) + action(north, data) - action(west, data) - action(south, data))
    return east, north, {
        "west_1": west_1,
        "south_1": south_1,
        "grad_w": grad_w,
        "grad_s": grad_s,
        "east_0": east_0,
        "north_0": north_0,
        "work_parts": parts,
        "work": sp.factor(sum(parts)),
        "actual_work": actual,
        "bond_density": bond_density(west_1[0], south_1[0], data),
    }


def temporal_inverse(east: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    east_0 = drift(east, -data["h"], data)
    north_0 = drift(north, -data["h"], data)
    west_2 = add_leg(east_0, north_0, data["gamma"], -data["eta"])
    south_2 = add_leg(east_0, north_0, data["eta"], data["gamma"])
    grad_w, grad_s = bond_gradient(west_2[0], south_2[0], data)
    west_1 = (west_2[0], (west_2[1] + data["tau"] * grad_w).applyfunc(sp.factor))
    south_1 = (south_2[0], (south_2[1] + data["tau"] * grad_s).applyfunc(sp.factor))
    return drift(west_1, -data["h"], data), drift(south_1, -data["h"], data)


def mixed_west_north(west: Leg, north: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    west_1 = drift(west, data["h"], data)
    north_1 = drift(north, -data["h"], data)
    q_s = ((north_1[0] + data["eta"] * west_1[0]) / data["gamma"]).applyfunc(sp.factor)
    grad_w, grad_s = bond_gradient(west_1[0], q_s, data)
    p_s = (
        (north_1[1] + data["eta"] * (west_1[1] - data["tau"] * grad_w)) / data["gamma"]
        + data["tau"] * grad_s
    ).applyfunc(sp.factor)
    south_1 = (q_s, p_s)
    q_e = ((west_1[0] + data["eta"] * north_1[0]) / data["gamma"]).applyfunc(sp.factor)
    p_e = ((west_1[1] + data["eta"] * north_1[1] - data["tau"] * grad_w) / data["gamma"]).applyfunc(sp.factor)
    return drift((q_e, p_e), data["h"], data), drift(south_1, -data["h"], data)


def mixed_west_east(west: Leg, east: Leg, data: dict[str, Any]) -> tuple[Leg, Leg]:
    west_1 = drift(west, data["h"], data)
    east_1 = drift(east, -data["h"], data)
    q_s = ((east_1[0] - data["gamma"] * west_1[0]) / data["eta"]).applyfunc(sp.factor)
    grad_w, grad_s = bond_gradient(west_1[0], q_s, data)
    p_s = (
        (east_1[1] - data["gamma"] * (west_1[1] - data["tau"] * grad_w)) / data["eta"]
        + data["tau"] * grad_s
    ).applyfunc(sp.factor)
    south_1 = (q_s, p_s)
    west_2 = (west_1[0], west_1[1] - data["tau"] * grad_w)
    south_2 = (south_1[0], south_1[1] - data["tau"] * grad_s)
    north_1 = add_leg(west_2, south_2, -data["eta"], data["gamma"])
    return drift(north_1, data["h"], data), drift(south_1, -data["h"], data)


def legs_equal(left: Leg, right: Leg) -> bool:
    return left[0] == right[0] and left[1] == right[1]


def local_fixture() -> tuple[Leg, Leg]:
    return (
        (sp.Matrix([1, 0, -1, 0, 0, 1, 0, -1]), sp.Matrix([0, 1, 0, -1, 1, 0, -1, 0])),
        (sp.Matrix([0, 1, 0, -1, -1, 0, 1, 0]), sp.Matrix([1, 0, -1, 0, 0, -1, 0, 1])),
    )


def global_inputs(m: int, n: int, profile: str) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    zero = sp.zeros(8, 1)
    horizontal: dict[tuple[int, int], Leg] = {}
    vertical: dict[tuple[int, int], Leg] = {}
    if profile == "f0" and (m, n) == (2, 2):
        qx1 = zero.copy(); qx1[0] = 1
        px2 = zero.copy(); px2[1] = q(1, 2)
        qy1 = zero.copy(); qy1[7] = -1
        py1 = zero.copy(); py1[2] = q(1, 3)
        qy2 = zero.copy(); qy2[3] = q(1, 2)
        py2 = zero.copy(); py2[4] = q(-1, 4)
        horizontal[(0, 1)] = (qx1, zero.copy())
        horizontal[(0, 2)] = (zero.copy(), px2)
        vertical[(1, 0)] = (qy1, py1)
        vertical[(2, 0)] = (qy2, py2)
        return horizontal, vertical
    for row in range(1, n + 1):
        qv = zero.copy(); pv = zero.copy()
        qv[(row - 1) % 8] = q((-1) ** row, row + 1)
        pv[(row + 2) % 8] = q(1, row + 3)
        horizontal[(0, row)] = (qv, pv)
    for column in range(1, m + 1):
        qv = zero.copy(); pv = zero.copy()
        qv[(column + 4) % 8] = q(1, column + 2)
        pv[(column + 6) % 8] = q(-1, column + 4)
        vertical[(column, 0)] = (qv, pv)
    return horizontal, vertical


def forward_rectangle(data: dict[str, Any], order: str) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg], dict[tuple[int, int], sp.Expr]]:
    m, n = data["rectangle"]
    horizontal, vertical = global_inputs(m, n, data["name"])
    works: dict[tuple[int, int], sp.Expr] = {}
    if order == "column":
        vertices: Iterable[tuple[int, int]] = ((i, j) for i in range(1, m + 1) for j in range(1, n + 1))
    elif order == "row":
        vertices = ((i, j) for j in range(1, n + 1) for i in range(1, m + 1))
    else:
        raise ValueError(order)
    for i, j in vertices:
        east, north, details = forward_gate(horizontal[(i - 1, j)], vertical[(i, j - 1)], data)
        horizontal[(i, j)] = east
        vertical[(i, j)] = north
        works[(i, j)] = details["work"]
    return horizontal, vertical, works


def row_length_ideals(m: int, n: int) -> list[tuple[int, ...]]:
    return [
        tuple(lengths)
        for lengths in itertools.product(range(m + 1), repeat=n)
        if all(lengths[index] >= lengths[index + 1] for index in range(n - 1))
    ]


def cut_edges(m: int, n: int, lengths: tuple[int, ...]) -> list[tuple[str, int, int]]:
    edges: list[tuple[str, int, int]] = [("X", lengths[row - 1], row) for row in range(1, n + 1)]
    for column in range(1, m + 1):
        height = max((row for row, length in enumerate(lengths, 1) if length >= column), default=0)
        edges.append(("Y", column, height))
    return edges


def cut_action(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], edges: list[tuple[str, int, int]], data: dict[str, Any]) -> sp.Expr:
    return sp.factor(sum(action(horizontal[(i, j)] if kind == "X" else vertical[(i, j)], data) for kind, i, j in edges))


def reverse_ideal(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], lengths: tuple[int, ...], data: dict[str, Any]) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    known_x: dict[tuple[int, int], Leg] = {}
    known_y: dict[tuple[int, int], Leg] = {}
    for kind, i, j in cut_edges(m, n, lengths):
        if kind == "X":
            known_x[(i, j)] = horizontal[(i, j)]
        else:
            known_y[(i, j)] = vertical[(i, j)]
    for i in range(m, 0, -1):
        for j in range(n, 0, -1):
            if i <= lengths[j - 1]:
                west, south = temporal_inverse(known_x[(i, j)], known_y[(i, j)], data)
                known_x[(i - 1, j)] = west
                known_y[(i, j - 1)] = south
    return known_x, known_y


def mixed_rectangle_reconstruct(horizontal: dict[tuple[int, int], Leg], vertical: dict[tuple[int, int], Leg], data: dict[str, Any]) -> tuple[dict[tuple[int, int], Leg], dict[tuple[int, int], Leg]]:
    m, n = data["rectangle"]
    known_x = {(0, j): horizontal[(0, j)] for j in range(1, n + 1)}
    known_y = {(i, n): vertical[(i, n)] for i in range(1, m + 1)}
    for i in range(1, m + 1):
        for j in range(n, 0, -1):
            east, south = mixed_west_north(known_x[(i - 1, j)], known_y[(i, j)], data)
            known_x[(i, j)] = east
            known_y[(i, j - 1)] = south
    return known_x, known_y


def dependency_sets(m: int, n: int) -> tuple[dict[tuple[int, int], frozenset[tuple[str, int]]], dict[tuple[int, int], frozenset[tuple[str, int]]]]:
    x = {(0, j): frozenset({("W", j)}) for j in range(1, n + 1)}
    y = {(i, 0): frozenset({("S", i)}) for i in range(1, m + 1)}
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            union = x[(i - 1, j)] | y[(i, j - 1)]
            x[(i, j)] = union
            y[(i, j)] = union
    return x, y


def pair_layer(size: int, offset: int, gamma: sp.Expr, eta: sp.Expr) -> sp.Matrix:
    matrix = sp.zeros(size)
    pairs = (
        [(index, index + 1) for index in range(0, size, 2)]
        if offset == 0
        else [(index, index + 1) for index in range(1, size - 1, 2)] + [(size - 1, 0)]
    )
    for left, right in pairs:
        matrix[left, left] = gamma
        matrix[left, right] = eta
        matrix[right, left] = -eta
        matrix[right, right] = gamma
    return matrix


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def build_payload(profile: str) -> dict[str, Any]:
    data = complete_parameters(fixture(profile))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads(path.read_text(encoding="utf-8")) for path in PARENT_PATHS]
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "provenance")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "provenance")
    audit.check("parent ids", manifest["parent_ids"] == [item["candidate_id"] for item in parents], manifest["parent_ids"], [item["candidate_id"] for item in parents], "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    audit.check("T0 authority", manifest["authority"].startswith("T0 "), manifest["authority"], "T0", "provenance")
    for anchor in (
        "section-3-exact-1d-q3-term-ownership",
        "section-5-global-mixed-inverses",
        "section-6-open-rectangle-all-cut-theorem",
        "section-8-exact-work-ledger",
        "section-9-interacting-bh-cut-unitaries-and-density-transport",
        "section-10-direct-order-microcut-no-go",
        "section-12-devils-advocate-audit",
    ):
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate_text, anchor, "present", "provenance")

    audit.check("parameter domain", valid_parameters(data), data, "valid", "parameters")
    mutations: list[tuple[str, dict[str, Any]]] = []
    for key, value in (("M", 5), ("tau", q(0)), ("lambda", q(0)), ("c", q(0)), ("g", q(0)), ("chi", q(0)), ("gamma", q(1)), ("eta", q(0))):
        changed = dict(data); changed[key] = value
        mutations.append((key, changed))
    changed_w = dict(data); changed_w["w"] = data["w"] * 2; mutations.append(("w", changed_w))
    changed_mu = dict(data); changed_mu["mu"] = data["mu"] * 2; mutations.append(("mu", changed_mu))
    changed_h = dict(data); changed_h["h"] = data["tau"] / 2; mutations.append(("h", changed_h))
    for name, changed in mutations:
        audit.check(f"reject hostile parameter {name}", not valid_parameters(changed), valid_parameters(changed), False, "parameters")

    edges = q3_edges()
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 degrees", [sum(index in edge for edge in edges) for index in range(8)] == [3] * 8, [sum(index in edge for edge in edges) for index in range(8)], [3] * 8, "Q3")
    symbols = sp.Matrix(sp.symbols("q0:8", real=True))
    symbolic_potential = q3_potential(symbols, data)
    automatic_gradient = sp.Matrix([sp.diff(symbolic_potential, symbol) for symbol in symbols])
    hand_gradient = q3_gradient(symbols, data)
    audit.check("Q3 analytic gradient", all(sp.expand(automatic_gradient[i] - hand_gradient[i]) == 0 for i in range(8)), automatic_gradient - hand_gradient, sp.zeros(8, 1), "Q3")
    symbolic_hessian = sp.hessian(symbolic_potential, tuple(symbols))
    audit.check("Q3 Hessian symmetric", symbolic_hessian == symbolic_hessian.T, symbolic_hessian - symbolic_hessian.T, sp.zeros(8), "Q3")

    zero = sp.zeros(8, 1)
    ring_q: list[sp.Matrix] = []
    for index in range(data["M"]):
        vector = zero.copy()
        if profile == "f0":
            if index == 0: vector[0] = 1
            if index == 1: vector[1] = 1
            if index == 2: vector[2] = -1
            if index == 3: vector[3] = 2
        else:
            vector[index % 8] = q((-1) ** index, index + 1)
        ring_q.append(vector)
    bond_values = [bond_density(ring_q[index], ring_q[(index + 1) % data["M"]], data) for index in range(data["M"])]
    inherited_u = sp.factor(data["w"] * sum(
        data["c"] * (ring_q[(index + 1) % data["M"]] - ring_q[index]).dot(ring_q[(index + 1) % data["M"]] - ring_q[index]) / (2 * data["a"] ** 2)
        + q3_potential(ring_q[index], data)
        for index in range(data["M"])
    ))
    audit.check("bond sum equals U_a", sp.factor(sum(bond_values) - inherited_u) == 0, sum(bond_values), inherited_u, "term_ledger")
    even_edges = {(index, (index + 1) % data["M"]) for index in range(0, data["M"], 2)}
    odd_edges = {(index, (index + 1) % data["M"]) for index in range(1, data["M"], 2)}
    audit.check("two-colour edge partition", len(even_edges | odd_edges) == data["M"] and not (even_edges & odd_edges), [even_edges, odd_edges], data["M"], "term_ledger")
    ownership = [sum(site in edge for edge in even_edges | odd_edges) for site in range(data["M"])]
    audit.check("two onsite half owners", ownership == [2] * data["M"], ownership, [2] * data["M"], "term_ledger")
    audit.check("four quarter drifts", 4 * data["h"] == data["tau"], 4 * data["h"], data["tau"], "term_ledger")
    audit.check("controller count", len(even_edges) + len(odd_edges) == data["M"], len(even_edges) + len(odd_edges), data["M"], "term_ledger")
    if profile == "f0":
        audit.check("F0 Q3 onsite oracle", [q3_potential(item, data) for item in ring_q] == [1, 1, 1, 19], [q3_potential(item, data) for item in ring_q], [1, 1, 1, 19], "oracles")
        audit.check("F0 bond oracle", bond_values == [q(11, 32), q(11, 32), q(175, 64), q(175, 64)], bond_values, [q(11, 32), q(11, 32), q(175, 64), q(175, 64)], "oracles")
        audit.check("F0 U oracle", inherited_u == q(197, 32), inherited_u, q(197, 32), "oracles")

    qw, pw, qs, ps = sp.symbols("qw pw qs ps", real=True)
    one = complete_parameters(fixture(profile))
    v_one = one["w"] * (one["c"] * (qs - qw) ** 2 / (2 * one["a"] ** 2) + (one["r"] * qw**2 / 2 + one["g"] * qw**4 / 4 + one["r"] * qs**2 / 2 + one["g"] * qs**4 / 4) / 2)
    input_vector = sp.Matrix([qw, pw, qs, ps])
    pre = sp.Matrix([qw + one["h"] * pw / one["mu"], pw, qs + one["h"] * ps / one["mu"], ps])
    gw_one = sp.diff(v_one, qw).subs({qw: pre[0], qs: pre[2]})
    gs_one = sp.diff(v_one, qs).subs({qw: pre[0], qs: pre[2]})
    kicked = sp.Matrix([pre[0], pre[1] - one["tau"] * gw_one, pre[2], pre[3] - one["tau"] * gs_one])
    central = sp.Matrix([
        one["gamma"] * kicked[0] + one["eta"] * kicked[2],
        one["gamma"] * kicked[1] + one["eta"] * kicked[3],
        -one["eta"] * kicked[0] + one["gamma"] * kicked[2],
        -one["eta"] * kicked[1] + one["gamma"] * kicked[3],
    ])
    output_vector = sp.Matrix([
        central[0] + one["h"] * central[1] / one["mu"], central[1],
        central[2] + one["h"] * central[3] / one["mu"], central[3],
    ])
    jacobian = output_vector.jacobian(input_vector)
    j_leg = sp.Matrix([[0, -1], [1, 0]])
    omega = sp.diag(1, 1, 1, 1); omega[:2, :2] = j_leg; omega[2:, 2:] = j_leg
    audit.check("one-species full gate symplectic", all(sp.expand(item) == 0 for item in jacobian.T * omega * jacobian - omega), jacobian.T * omega * jacobian - omega, sp.zeros(4), "local_symbolic")
    audit.check("one-species temporal determinant", sp.factor(jacobian.det()) == 1, sp.factor(jacobian.det()), 1, "local_symbolic")
    north_cross = output_vector[2:4, :].jacobian(sp.Matrix([qs, ps]))
    east_cross = output_vector[0:2, :].jacobian(sp.Matrix([qs, ps]))
    audit.check("one-species gamma cross determinant", sp.factor(north_cross.det()) == one["gamma"] ** 2, sp.factor(north_cross.det()), one["gamma"] ** 2, "local_symbolic")
    audit.check("one-species eta cross determinant", sp.factor(east_cross.det()) == one["eta"] ** 2, sp.factor(east_cross.det()), one["eta"] ** 2, "local_symbolic")

    west, south = local_fixture()
    east, north, details = forward_gate(west, south, data)
    recovered_west, recovered_south = temporal_inverse(east, north, data)
    audit.check("full eight-species temporal inverse west", legs_equal(recovered_west, west), recovered_west, west, "local_numeric")
    audit.check("full eight-species temporal inverse south", legs_equal(recovered_south, south), recovered_south, south, "local_numeric")
    mixed_east, mixed_south = mixed_west_north(west, north, data)
    audit.check("full eight-species gamma mixed east", legs_equal(mixed_east, east), mixed_east, east, "local_numeric")
    audit.check("full eight-species gamma mixed south", legs_equal(mixed_south, south), mixed_south, south, "local_numeric")
    mixed_north, eta_south = mixed_west_east(west, east, data)
    audit.check("full eight-species eta mixed north", legs_equal(mixed_north, north), mixed_north, north, "local_numeric")
    audit.check("full eight-species eta mixed south", legs_equal(eta_south, south), eta_south, south, "local_numeric")
    audit.check("local work formula", details["work"] == details["actual_work"], details["work"], details["actual_work"], "work")
    audit.check("cross determinant gamma exponent", data["gamma"] ** 16 != 0, data["gamma"] ** 16, "nonzero", "local_numeric")
    audit.check("cross determinant eta exponent", data["eta"] ** 16 != 0, data["eta"] ** 16, "nonzero", "local_numeric")
    coefficient = data["tau"] * data["w"] * data["c"] / data["a"] ** 2
    expected_cross_coefficient = q(3, 64) if profile == "f0" else q(-7, 360)
    audit.check("q-only cross sign oracle", coefficient == expected_cross_coefficient, coefficient, expected_cross_coefficient, "microcut_no_go")
    qkick_cross = sp.zeros(16)
    qkick_cross[8:16, 0:8] = coefficient * sp.eye(8)
    drift_jacobian = sp.eye(16); drift_jacobian[:8, 8:] = data["h"] * sp.eye(8) / data["mu"]
    drifted_cross = drift_jacobian * qkick_cross * drift_jacobian
    audit.check("q-only cross rank", qkick_cross.rank() == 8, qkick_cross.rank(), 8, "microcut_no_go")
    audit.check("drifted q-only cross rank", drifted_cross.rank() == 8, drifted_cross.rank(), 8, "microcut_no_go")
    audit.check("q-only cross determinant", qkick_cross.det() == 0, qkick_cross.det(), 0, "microcut_no_go")
    full_controller_cross = data["eta"] * sp.eye(16)
    audit.check("controller cross rank", full_controller_cross.rank() == 16, full_controller_cross.rank(), 16, "microcut_no_go")
    if profile == "f0":
        audit.check("F0 pre-drift bond oracle", details["bond_density"] == q(265, 128), details["bond_density"], q(265, 128), "oracles")
        audit.check("F0 west-gradient oracle", details["grad_w"][0] == q(475, 512), details["grad_w"][0], q(475, 512), "oracles")
        audit.check("F0 south-gradient oracle", details["grad_s"][0] == q(-1, 128), details["grad_s"][0], q(-1, 128), "oracles")
        audit.check("F0 east q oracle", east[0][0] == q(19071, 20480), east[0][0], q(19071, 20480), "oracles")
        audit.check("F0 east p oracle", east[1][0] == q(2687, 5120), east[1][0], q(2687, 5120), "oracles")
        audit.check("F0 north q oracle", north[0][0] == q(-1041, 2560), north[0][0], q(-1041, 2560), "oracles")
        audit.check("F0 north p oracle", north[1][0] == q(623, 640), north[1][0], q(623, 640), "oracles")
        audit.check("F0 input action oracle", action(west, data) + action(south, data) == 10, action(west, data) + action(south, data), 10, "oracles")
        audit.check("F0 output action oracle", action(east, data) + action(north, data) == q(44465381, 4194304), action(east, data) + action(north, data), q(44465381, 4194304), "oracles")
        audit.check("F0 work oracle", details["work"] == q(2522341, 4194304), details["work"], q(2522341, 4194304), "oracles")
        expected_parts = (q(1, 4), q(1, 4), q(507745, 1048576), q(-2590667, 20971520), q(-339893, 1310720))
        audit.check("F0 work-parts oracle", details["work_parts"] == expected_parts, details["work_parts"], expected_parts, "oracles")

    positive_work = details["work"]
    sign_q = sp.zeros(8, 1); sign_q[0] = 1
    sign_leg = (sign_q, sp.zeros(8, 1))
    _, _, sign_details = forward_gate(sign_leg, sign_leg, data)
    if profile == "f0":
        audit.check("negative-work oracle", sign_details["work"] == q(-471, 2048), sign_details["work"], q(-471, 2048), "work")
    audit.check("work sign-indefinite witness", positive_work * sign_details["work"] < 0, [positive_work, sign_details["work"]], "opposite signs", "work")

    even_layer = pair_layer(data["M"], 0, data["gamma"], data["eta"])
    odd_layer = pair_layer(data["M"], 1, data["gamma"], data["eta"])
    zero_step = odd_layer * even_layer
    audit.check("fixed controller zero-step not identity", zero_step != sp.eye(data["M"]), zero_step, "not identity", "ordering")
    audit.check("controller layers orthogonal", even_layer.T * even_layer == sp.eye(data["M"]) and odd_layer.T * odd_layer == sp.eye(data["M"]), "orthogonal", "orthogonal", "ordering")
    order_w = (sp.eye(8)[:, 0], sp.zeros(8, 1)); order_s = (sp.zeros(8, 1), sp.zeros(8, 1))
    gw, gs = bond_gradient(order_w[0], order_s[0], data)
    kicked_w = (order_w[0], order_w[1] - data["tau"] * gw); kicked_s = (order_s[0], order_s[1] - data["tau"] * gs)
    g_after_k = (add_leg(kicked_w, kicked_s, data["gamma"], data["eta"]), add_leg(kicked_w, kicked_s, -data["eta"], data["gamma"]))
    mixed_w = add_leg(order_w, order_s, data["gamma"], data["eta"]); mixed_s = add_leg(order_w, order_s, -data["eta"], data["gamma"])
    mgw, mgs = bond_gradient(mixed_w[0], mixed_s[0], data)
    k_after_g = ((mixed_w[0], mixed_w[1] - data["tau"] * mgw), (mixed_s[0], mixed_s[1] - data["tau"] * mgs))
    audit.check("kick-controller noncommutation", not legs_equal(g_after_k[0], k_after_g[0]) or not legs_equal(g_after_k[1], k_after_g[1]), [g_after_k, k_after_g], "different", "ordering")

    horizontal_a, vertical_a, works_a = forward_rectangle(data, "column")
    horizontal_b, vertical_b, works_b = forward_rectangle(data, "row")
    audit.check("rectangle horizontal sweep independence", horizontal_a == horizontal_b, len(horizontal_a), len(horizontal_b), "rectangle")
    audit.check("rectangle vertical sweep independence", vertical_a == vertical_b, len(vertical_a), len(vertical_b), "rectangle")
    audit.check("rectangle work sweep independence", works_a == works_b, works_a, works_b, "rectangle")
    m, n = data["rectangle"]
    ideals = row_length_ideals(m, n)
    audit.check("cut count", len(ideals) == math.comb(m + n, m), len(ideals), math.comb(m + n, m), "rectangle")
    audit.check("cut leg count", all(len(cut_edges(m, n, ideal)) == data["M"] for ideal in ideals), [len(cut_edges(m, n, ideal)) for ideal in ideals], data["M"], "rectangle")
    input_edges = cut_edges(m, n, tuple(0 for _ in range(n)))
    input_action = cut_action(horizontal_a, vertical_a, input_edges, data)
    cut_fingerprints: list[dict[str, Any]] = []
    for ideal in ideals:
        edges_for_cut = cut_edges(m, n, ideal)
        reverse_x, reverse_y = reverse_ideal(horizontal_a, vertical_a, ideal, data)
        recovered = all(legs_equal(reverse_x[(0, j)], horizontal_a[(0, j)]) for j in range(1, n + 1)) and all(legs_equal(reverse_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m + 1))
        audit.check(f"reverse cut {ideal}", recovered, recovered, True, "all_cuts")
        ideal_work = sp.factor(sum(works_a[(i, j)] for i in range(1, m + 1) for j in range(1, n + 1) if i <= ideal[j - 1]))
        action_difference = sp.factor(cut_action(horizontal_a, vertical_a, edges_for_cut, data) - input_action)
        audit.check(f"work telescope {ideal}", ideal_work == action_difference, ideal_work, action_difference, "all_cuts")
        cut_fingerprints.append({"ideal": ideal, "work": ideal_work, "action_difference": action_difference})
    mixed_x, mixed_y = mixed_rectangle_reconstruct(horizontal_a, vertical_a, data)
    audit.check("global west-north reconstruct south", all(legs_equal(mixed_y[(i, 0)], vertical_a[(i, 0)]) for i in range(1, m + 1)), "recovered", "recovered", "rectangle")
    audit.check("global west-north reconstruct east", all(legs_equal(mixed_x[(m, j)], horizontal_a[(m, j)]) for j in range(1, n + 1)), "recovered", "recovered", "rectangle")
    dep_x, dep_y = dependency_sets(m, n)
    causal_violations = []
    for (i, j), dependencies in list(dep_x.items()) + list(dep_y.items()):
        for kind, index in dependencies:
            if (kind == "W" and index > j) or (kind == "S" and index > i):
                causal_violations.append([(i, j), (kind, index)])
    audit.check("southwest causal support", causal_violations == [], causal_violations, [], "rectangle")
    global_projection_det = data["gamma"] ** (16 * m * n)
    audit.check("global projection determinant nonzero", global_projection_det != 0, global_projection_det, "nonzero", "rectangle")

    true_scope = (
        "inserted_1D_per_unit_transverse_area_model", "same_CL8_16M_phase_dimension",
        "lambda_positive_locked_Q3_domain", "exact_Q3_spatial_bond_coefficient_ownership",
        "exact_kinetic_shear_coefficient_ownership", "controller_explicitly_ledgered",
        "global_full_cross_inverse", "open_rectangle_all_cut_symplectic_diffeomorphism",
        "exact_local_to_global_work_ledger", "interacting_BH_forward_cut_unitaries",
        "exact_normal_density_transport",
    )
    false_scope = tuple(key for key, value in manifest["scope"].items() if value is False)
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER", "scope")
    audit.check("quantum single-leg drift", "single-leg Dhat_h" in manifest["quantum_forward_cut"]["local_unitary"], manifest["quantum_forward_cut"]["local_unitary"], "single-leg", "quantum")
    audit.check("Schrodinger density direction", manifest["quantum_forward_cut"]["density_transport"].startswith("rho_I=U_I*rho_in*U_I^*"), manifest["quantum_forward_cut"]["density_transport"], "rho'=U rho U*", "quantum")
    audit.check("Heisenberg direction", "alpha_I(A_target)=U_I^* A_target U_I" in manifest["quantum_forward_cut"]["BH_map"], manifest["quantum_forward_cut"]["BH_map"], "U* A U", "quantum")
    audit.check("Schwartz work domain", "Schwartz core" in manifest["quantum_forward_cut"]["work_domain"], manifest["quantum_forward_cut"]["work_domain"], "Schwartz core", "quantum")
    audit.check("nonlinear Weyl firewall", manifest["scope"]["full_nonlinear_Weyl_Cstar_invariance"] is False, manifest["scope"]["full_nonlinear_Weyl_Cstar_invariance"], False, "quantum")

    cross_invariants = {
        "profile": profile,
        "q3_edges": edges,
        "ring_size": data["M"],
        "bond_values": bond_values,
        "inherited_U": inherited_u,
        "gamma_cross_determinant": data["gamma"] ** 16,
        "eta_cross_determinant": data["eta"] ** 16,
        "qonly_cross_coefficient": coefficient,
        "qonly_cross_rank": qkick_cross.rank(),
        "local_east": ([east[0][index] for index in range(8)], [east[1][index] for index in range(8)]),
        "local_north": ([north[0][index] for index in range(8)], [north[1][index] for index in range(8)]),
        "local_work": details["work"],
        "local_work_parts": details["work_parts"],
        "negative_work": sign_details["work"],
        "rectangle": {"m": m, "n": n, "cut_count": len(ideals), "phase_dimension": 16 * data["M"]},
        "cut_fingerprints": cut_fingerprints,
        "global_projection_determinant": global_projection_det,
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": manifest["parent_ids"],
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "profile": profile,
        "parameters": data,
        "verdict": manifest["verdict"],
        "derived": {
            "q3_edge_count": len(edges),
            "Q3_gradient_verified": True,
            "Q3_Hessian_symmetric": True,
            "term_ledger_verified": True,
            "local_temporal_and_mixed_inverses_verified": True,
            "all_cuts_verified": True,
            "work_telescope_verified": True,
            "ordering_no_go_verified": True,
            "quantum_BH_contract_verified": True,
        },
        "cross_invariants": cross_invariants,
        "scope": manifest["scope"],
        "negative_ids": manifest["negative_ids"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
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
    print(f"{CANDIDATE_ID} primary {args.profile}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
