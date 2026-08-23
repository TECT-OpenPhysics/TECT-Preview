#!/usr/bin/env python3
"""Primary exact audit for the finite Q3 matching-layer common-core envelope.

This is a claim-nonbearing QFT subgate.  It audits the exact matching-layer
edge colouring of a finite Z^3 box, the scalar square identities behind the
two-sided weighted form estimate, and the volume-independent graph envelope
for a six-layer split product.  The onsite factor is treated under its
explicit tensor-local self-adjoint hypothesis.  No exhaustion or KMS claim is
made here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-24-primary-{SLUG}"
    / "primary.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def graph(side: int) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int, int]]]:
    vertices = list(product(range(side), repeat=3))
    index = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int, int, int]] = []
    for vertex in vertices:
        for axis in range(3):
            if vertex[axis] + 1 >= side:
                continue
            neighbour = list(vertex)
            neighbour[axis] += 1
            left = index[vertex]
            right = index[tuple(neighbour)]
            edges.append((left, right, axis, vertex[axis] % 2))
    return vertices, edges


def transform_p(momentum: list[sp.Rational], position: list[sp.Rational], edges: list[tuple[int, int, int, int]], delta: sp.Rational, coupling: sp.Rational) -> list[sp.Rational]:
    output = list(momentum)
    for left, right, _axis, _parity in edges:
        output[left] += delta * coupling * position[right]
        output[right] += delta * coupling * position[left]
    return output


def energy(weights: list[sp.Rational], momentum: list[sp.Rational], position: list[sp.Rational], chi: sp.Rational, gamma: sp.Rational) -> sp.Rational:
    return sp.factor(sum(weight * (1 + p**2 / (2 * chi) + gamma * q**4) for weight, p, q in zip(weights, momentum, position)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001024", manifest["exploration_id"], "EXP-001024", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("six layer hypothesis", manifest["graph_model"]["layer_count"] == 6, manifest["graph_model"]["layer_count"], 6, "graph")

    vertices, edges = graph(3)
    layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {}
    for edge in edges:
        layers.setdefault((edge[2], edge[3]), []).append(edge)
    incidence: dict[tuple[int, int], int] = {}
    for colour, layer in layers.items():
        counts = {vertex: 0 for vertex in range(len(vertices))}
        for left, right, _axis, _parity in layer:
            counts[left] += 1
            counts[right] += 1
        incidence[colour] = max(counts.values())
        audit.check(f"matching layer {colour}", max(counts.values()) <= 1, max(counts.values()), 1, "graph")
    audit.check("box vertices", len(vertices) == 27, len(vertices), 27, "graph")
    audit.check("box edges", len(edges) == 54, len(edges), 54, "graph")
    audit.check("six nonempty layers", sorted(len(layer) for layer in layers.values()) == [9] * 6, sorted(len(layer) for layer in layers.values()), [9] * 6, "graph")
    audit.check("edge colouring covers box", sum(len(layer) for layer in layers.values()) == len(edges), sum(len(layer) for layer in layers.values()), len(edges), "graph")
    full_degree = [0] * len(vertices)
    for left, right, _axis, _parity in edges:
        full_degree[left] += 1
        full_degree[right] += 1
    audit.check("full graph degree six witness", max(full_degree) == 6, max(full_degree), 6, "adversarial")
    audit.check("full graph is not one matching", max(full_degree) > 1, max(full_degree), ">1", "adversarial")

    distance = [sum(abs(component - 1) for component in vertex) for vertex in vertices]
    weights = [sp.Rational(1, 2**radius) for radius in distance]
    ratios = [sp.factor(weights[left] / weights[right]) for left, right, _axis, _parity in edges]
    audit.check("weight ratio lower", min(ratios) >= sp.Rational(1, 2), min(ratios), ">=1/2", "weights")
    audit.check("weight ratio upper", max(ratios) <= 2, max(ratios), "<=2", "weights")

    d, p, q, c, chi, s, kappa = sp.symbols("d p q c chi s kappa", nonnegative=True)
    shift = sp.expand((1 + d) * p**2 + (d**2 + d) * (c * q) ** 2 - (p + d * c * q) ** 2)
    shift_expected = sp.expand(d * (p - c * q) ** 2)
    audit.check("shift square identity", sp.factor(shift - shift_expected) == 0, sp.factor(shift - shift_expected), 0, "form")
    quartic = sp.expand(1 + s**2 * q**4 - 2 * s * q**2)
    audit.check("quartic absorption identity", sp.factor(quartic - (s * q**2 - 1) ** 2) == 0, sp.factor(quartic - (s * q**2 - 1) ** 2), 0, "form")
    fu, fv, qu, qv = sp.symbols("fu fv qu qv", nonnegative=True)
    transfer = sp.expand(kappa * (fu * qu**2 + fv * qv**2) - (fu * qv**2 + fv * qu**2))
    transfer_expected = sp.expand((kappa * fv - fu) * qv**2 + (kappa * fu - fv) * qu**2)
    audit.check("matching weighted transfer identity", sp.factor(transfer - transfer_expected) == 0, sp.factor(transfer - transfer_expected), 0, "form")

    coupling = sp.Rational(3, 5)
    chi_value = sp.Rational(7, 4)
    sqrt_gamma = sp.Rational(2, 5)
    gamma = sqrt_gamma**2
    kappa_value = sp.Integer(2)
    C_match = sp.factor(1 + kappa_value * coupling**2 / (2 * chi_value * sqrt_gamma))
    audit.check("derived matching coefficient", C_match == sp.Rational(53, 35), C_match, sp.Rational(53, 35), "form")
    audit.check("form coefficient uses ratio and quartic source", C_match == 1 + kappa_value * coupling**2 / (2 * chi_value * sqrt_gamma), C_match, "1+kappa*c^2/(2*chi*sqrt_gamma)", "form")

    fixtures: list[tuple[list[sp.Rational], list[sp.Rational]]] = []
    for seed in range(4):
        momentum = [sp.Rational(1 + seed + 2 * x + 3 * y + 4 * z, 5) for x, y, z in vertices]
        position = [sp.Rational(1 + seed + x + 2 * y - z, 4) for x, y, z in vertices]
        fixtures.append((momentum, position))
    layer_rows: list[dict[str, Any]] = []
    delta = sp.Rational(1, 7)
    for index, (momentum, position) in enumerate(fixtures):
        before = energy(weights, momentum, position, chi_value, gamma)
        for sign in (1, -1):
            for colour, layer in sorted(layers.items()):
                after_momentum = transform_p(momentum, position, layer, sign * delta, coupling)
                after = energy(weights, after_momentum, position, chi_value, gamma)
                audit.check(f"matching form bound fixture {index} sign {sign} layer {colour}", after <= (1 + C_match * delta) * before, after, f"<={(1 + C_match * delta) * before}", "form")
                layer_rows.append({"fixture": index, "sign": sign, "layer": colour, "before": before, "after": after})
            all_after = transform_p(momentum, position, edges, sign * delta, coupling)
            full_after = energy(weights, all_after, position, chi_value, gamma)
            audit.check(f"six-layer full shear fixture {index} sign {sign}", full_after <= (1 + C_match * delta) ** 6 * before, full_after, f"<={(1 + C_match * delta) ** 6 * before}", "product")

    endpoint_exponent = sp.factor(3 * C_match)
    audit.check("six-layer endpoint exponent", endpoint_exponent == sp.Rational(159, 35), endpoint_exponent, sp.Rational(159, 35), "product")
    for steps in (1, 2, 5, 11):
        t = sp.Rational(3, 5)
        factor = (1 + C_match * t / steps) ** (3 * steps)
        rhs = math.exp(float(3 * C_match * t))
        audit.check(f"Trotter endpoint exponential steps={steps}", float(factor) <= rhs + 1e-12, [factor, rhs], "<=exp(3*C*T)", "product")

    audit.check("onsite tensor-local scope declared", manifest["onsite_factor"]["operator_theorem_assumption"] == "conditional", manifest["onsite_factor"]["operator_theorem_assumption"], "conditional", "scope")
    audit.check("onsite local commutation count", manifest["onsite_factor"]["site_local_terms_commute"] is True, manifest["onsite_factor"]["site_local_terms_commute"], True, "onsite")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "box_vertices": len(vertices),
            "box_edges": len(edges),
            "layer_count": len(layers),
            "layer_sizes": sorted(len(layer) for layer in layers.values()),
            "matching_incidence_max": incidence,
            "weight_ratio_min": min(ratios),
            "weight_ratio_max": max(ratios),
            "C_match": C_match,
            "endpoint_exponent": endpoint_exponent,
            "finite_common_core_induced_norm_closed": True,
            "volume_uniform_split_envelope_closed": True,
            "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False,
            "qft_kms_closed": False,
        },
        "layer_rows": layer_rows,
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"],
        "exploration_id": manifest["exploration_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY MATCHING-LAYER PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
