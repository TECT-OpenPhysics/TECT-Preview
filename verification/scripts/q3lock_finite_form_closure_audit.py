#!/usr/bin/env python3
"""Finite algebraic audit for the Q3LOCK form/trace interface.

The script derives graph degrees and envelope coefficients from the declared
Q3 and spatial graphs, checks the two scalar Young maxima, evaluates generated
finite fields, and exercises the residual truncation direction.  It is a
claim-non-bearing diagnostic: it cannot prove closed-form convergence,
semigroup convergence, or any infinite-volume statement.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-finite-form-closure-audit-260907.md"
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence/manuscript.tex"
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-q3lock-finite-form-closure-audit/result.json"
)
INTERNAL_DIM = 3
COMPONENTS = 2**INTERNAL_DIM
PARAMETERS = {
    "g": F(2, 3),
    "lambda": F(5, 4),
    "c": F(5, 2),
    "r": F(-3, 2),
    "a": F(7, 4),
    "h0": F(3, 2),
}
VOLUMES = (2, 4)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_no_replace(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def q3_vertices() -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product((0, 1), repeat=INTERNAL_DIM))


def q3_edges() -> tuple[tuple[int, int], ...]:
    vertices = q3_vertices()
    return tuple(
        (i, j)
        for i, x in enumerate(vertices)
        for j, y in enumerate(vertices)
        if i < j and sum(a != b for a, b in zip(x, y)) == 1
    )


def spatial_edges(length: int, periodic: bool = True) -> tuple[tuple[int, int], ...]:
    sites = tuple(itertools.product(range(length), repeat=INTERNAL_DIM))
    lookup = {site: i for i, site in enumerate(sites)}
    edges: list[tuple[int, int]] = []
    for i, site in enumerate(sites):
        for axis in range(INTERNAL_DIM):
            target = list(site)
            target[axis] += 1
            if target[axis] == length:
                if not periodic:
                    continue
                target[axis] = 0
            edges.append((i, lookup[tuple(target)]))
    return tuple(edges)


def norm2(q: tuple[float, ...]) -> float:
    return sum(x * x for x in q)


def norm4(q: tuple[float, ...]) -> float:
    return sum(x**4 for x in q)


def locking(q: tuple[float, ...], lam: float) -> float:
    vertices = q3_edges()
    return lam / 4.0 * sum(
        (q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in vertices
    )


def potential(
    fields: tuple[tuple[float, ...], ...],
    *,
    length: int,
    r: float,
    g: float,
    lam: float,
    c: float,
    h: float,
) -> float:
    q3 = q3_edges()
    value = 0.0
    root = math.sqrt(COMPONENTS)
    for q in fields:
        value += r * norm2(q) / 2.0
        value += g * norm4(q) / 4.0
        value += locking(q, lam)
        value -= h * sum(q) / root
    for i, j in spatial_edges(length):
        value += c * norm2(tuple(a - b for a, b in zip(fields[i], fields[j]))) / 2.0
    return value


def fields_for(length: int, *, alternating_internal: bool = False, alternating_space: bool = False) -> tuple[tuple[float, ...], ...]:
    sites = tuple(itertools.product(range(length), repeat=INTERNAL_DIM))
    fields: list[tuple[float, ...]] = []
    for site in sites:
        site_sign = -1.0 if alternating_space and sum(site) % 2 else 1.0
        q: list[float] = []
        for index, vertex in enumerate(q3_vertices()):
            sign = -1.0 if alternating_internal and sum(vertex) % 2 else 1.0
            q.append(site_sign * sign * (1.0 if index < 2 else 0.0))
        fields.append(tuple(q))
    return tuple(fields)


def envelope_constants(*, volume: int, g: float, lam: float, c: float, r: float, h0: float) -> tuple[float, float]:
    constant = volume * (abs(r) / 2.0 + h0 + 6.0 * c)
    coefficient = g / 4.0 + 3.0 * lam + abs(r) / 8.0 + h0 / 4.0 + 3.0 * c / 2.0
    return constant, coefficient


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def build_payload() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    g = float(PARAMETERS["g"])
    lam = float(PARAMETERS["lambda"])
    c = float(PARAMETERS["c"])
    r = float(PARAMETERS["r"])
    a = float(PARAMETERS["a"])
    h0 = float(PARAMETERS["h0"])
    edges = q3_edges()
    add(rows, "Q3 component count", len(q3_vertices()) == COMPONENTS, len(q3_vertices()), COMPONENTS)
    degrees = [sum(i in edge for edge in edges) for i in range(COMPONENTS)]
    add(rows, "Q3 edge count", len(edges) == 12, len(edges), 12)
    add(rows, "Q3 vertex degree", set(degrees) == {3}, degrees, "all 3")

    b_res = abs(r - a) / 2.0
    b_phys = abs(r) / 2.0
    A = g / 128.0
    source_constant = 0.75 * h0 ** (4.0 / 3.0) * (32.0 / g) ** (1.0 / 3.0)
    residual_constant = 16.0 * b_res * b_res / g + source_constant
    physical_constant = 16.0 * b_phys * b_phys / g + source_constant
    add(rows, "residual quartic coefficient", g / 32.0 - g / 64.0 - g / 128.0 == A, A, "g/128")

    quadratic_optimizer = math.sqrt(32.0 * b_res / g) if b_res else 0.0
    quadratic_gap = 16.0 * b_res * b_res / g - (
        b_res * quadratic_optimizer**2 - g * quadratic_optimizer**4 / 64.0
    )
    add(rows, "quadratic Young maximum", abs(quadratic_gap) <= 1e-12, quadratic_gap, 0.0)
    source_optimizer = (32.0 * h0 / g) ** (1.0 / 3.0)
    source_gap = source_constant - (
        h0 * source_optimizer - g * source_optimizer**4 / 128.0
    )
    add(rows, "source Young maximum", abs(source_gap) <= 1e-12, source_gap, 0.0)

    for length in VOLUMES:
        volume = length**INTERNAL_DIM
        edges_spatial = spatial_edges(length)
        endpoint_degrees = [sum(i in edge for edge in edges_spatial) for i in range(volume)]
        add(rows, f"L={length} spatial bond count", len(edges_spatial) == 3 * volume, len(edges_spatial), 3 * volume)
        add(rows, f"L={length} spatial endpoint degree", set(endpoint_degrees) == {6}, endpoint_degrees, "all 6")
        for alternating_internal, alternating_space in (
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ):
            fields = fields_for(
                length,
                alternating_internal=alternating_internal,
                alternating_space=alternating_space,
            )
            w = sum(norm2(q) ** 2 for q in fields)
            U = potential(fields, length=length, r=r, g=g, lam=lam, c=c, h=0.0)
            constant, coefficient = envelope_constants(volume=volume, g=g, lam=lam, c=c, r=r, h0=h0)
            label = f"L={length}-internal={alternating_internal}-space={alternating_space}"
            add(rows, label + " physical upper envelope", abs(U) <= constant + coefficient * w + 1e-10, U, constant + coefficient * w)
            residual = U - a * sum(norm2(q) for q in fields) / 2.0
            residual_lower = A * w - volume * residual_constant
            add(rows, label + " residual lower envelope", residual + 1e-10 >= residual_lower, residual, residual_lower)
            physical_lower = A * w - volume * physical_constant
            add(rows, label + " physical lower envelope", U + 1e-10 >= physical_lower, U, physical_lower)

    # The two declared upper-budget coefficients are not optional: hostile
    # fixtures saturate the corresponding elementary inequalities.
    q3_vector = tuple(-1.0 if sum(vertex) % 2 else 1.0 for vertex in q3_vertices())
    locking_value = locking(q3_vector, lam)
    w_q3 = norm4(q3_vector)
    add(rows, "hostile omitted Q3 degree rejected", locking_value > 0.0, locking_value, ">0")
    add(rows, "Q3 degree coefficient is saturated", abs(locking_value - 3.0 * lam * w_q3) <= 1e-12, locking_value, 3.0 * lam * w_q3)

    spatial_hostile = fields_for(2, alternating_internal=False, alternating_space=True)
    w_spatial = sum(norm2(q) ** 2 for q in spatial_hostile)
    spatial_value = c / 2.0 * sum(
        norm2(tuple(a - b for a, b in zip(spatial_hostile[i], spatial_hostile[j])))
        for i, j in spatial_edges(2)
    )
    volume = 2**INTERNAL_DIM
    add(rows, "hostile omitted spatial endpoint budget rejected", spatial_value > 6.0 * c * volume, spatial_value, ">6*c*V")
    add(rows, "spatial endpoint coefficient is saturated", abs(spatial_value - (6.0 * c * volume + 1.5 * c * w_spatial)) <= 1e-12, spatial_value, 6.0 * c * volume + 1.5 * c * w_spatial)

    residual_values = (-2.5, -0.25, 0.0, 1.5, 9.0)
    cutoffs = (-1.0, 0.0, 1.0, 4.0, 12.0)
    for value in residual_values:
        sequence = [min(value, cutoff) for cutoff in cutoffs]
        add(rows, f"truncation monotonicity {value}", all(x <= y for x, y in zip(sequence, sequence[1:])), sequence, "nondecreasing")
        add(rows, f"truncation convergence {value}", sequence[-1] == value, sequence[-1], value)

    text = PAPER.read_text(encoding="utf-8")
    for label in ("eq:form-domain", "eq:residual-lower", "eq:trace-bound", "sec:fk-identification"):
        add(rows, "manuscript locator " + label, label in text, label, "present")

    return {
        "schema": "tect/q3lock-finite-form-closure-audit/1.0",
        "tool_version": __version__,
        "status": "PASS",
        "claim_bearing": False,
        "assertions_passed": len(rows),
        "assertions": rows,
        "declared_inputs": {key: str(value) for key, value in PARAMETERS.items()},
        "derived": {
            "A": A,
            "residual_constant": residual_constant,
            "physical_constant": physical_constant,
            "upper_constant_formula": "V*(abs(r)/2+h0+6*c)",
            "upper_coefficient_formula": "g/4+3*lambda+abs(r)/8+h0/4+3*c/2",
        },
        "source_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (Path(__file__).resolve(), NOTE, PAPER)
        },
        "scope": "Finite graph/envelope and provenance diagnostics only; closed-form, monotone-form and semigroup acceptance remain open.",
    }


if __name__ == "__main__":
    payload = build_payload()
    atomic_no_replace(OUTPUT, payload)
    print(
        "Q3LOCK FINITE FORM CLOSURE AUDIT PASS "
        f"{payload['assertions_passed']}/{len(payload['assertions'])}"
    )
    print(OUTPUT.relative_to(ROOT).as_posix())
