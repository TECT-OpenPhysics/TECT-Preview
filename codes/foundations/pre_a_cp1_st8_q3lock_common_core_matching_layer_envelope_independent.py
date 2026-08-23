#!/usr/bin/env python3
"""Independent Fraction audit for the Q3 matching-layer envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-24-primary-pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope/independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def graph(side: int) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int, int]]]:
    vertices = list(product(range(side), repeat=3))
    index = {vertex: i for i, vertex in enumerate(vertices)}
    edges = []
    for vertex in vertices:
        for axis in range(3):
            if vertex[axis] + 1 >= side:
                continue
            neighbour = list(vertex)
            neighbour[axis] += 1
            edges.append((index[vertex], index[tuple(neighbour)], axis, vertex[axis] % 2))
    return vertices, edges


def energy(weights: list[F], momentum: list[F], position: list[F], chi: F, gamma: F) -> F:
    return sum((weight * (1 + p * p / (2 * chi) + gamma * q**4) for weight, p, q in zip(weights, momentum, position)), F(0))


def shifted(momentum: list[F], position: list[F], edges: list[tuple[int, int, int, int]], delta: F, coupling: F) -> list[F]:
    output = list(momentum)
    for left, right, _axis, _parity in edges:
        output[left] += delta * coupling * position[right]
        output[right] += delta * coupling * position[left]
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        rows.append({"name": name, "group": group, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-common-core-matching-layer-envelope/1.0", manifest["schema"], ".../1.0", "provenance")
    check("exploration", manifest["exploration_id"] == "EXP-001024", manifest["exploration_id"], "EXP-001024", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    source_lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    has_symbolic_import = any(line.strip().startswith(("import sympy", "from sympy")) for line in source_lines)
    check("independent source policy", not has_symbolic_import, has_symbolic_import, False, "scope")

    vertices, edges = graph(3)
    layers: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {}
    for edge in edges:
        layers.setdefault((edge[2], edge[3]), []).append(edge)
    for colour, layer in layers.items():
        counts = {vertex: 0 for vertex in range(len(vertices))}
        for left, right, _axis, _parity in layer:
            counts[left] += 1
            counts[right] += 1
        check(f"matching layer {colour}", max(counts.values()) <= 1, max(counts.values()), 1, "graph")
    check("box vertices", len(vertices) == 27, len(vertices), 27, "graph")
    check("box edges", len(edges) == 54, len(edges), 54, "graph")
    check("layer sizes", sorted(len(layer) for layer in layers.values()) == [9] * 6, sorted(len(layer) for layer in layers.values()), [9] * 6, "graph")
    degrees = [0] * len(vertices)
    for left, right, _axis, _parity in edges:
        degrees[left] += 1
        degrees[right] += 1
    check("full degree six and not matching", max(degrees) == 6 and max(degrees) > 1, max(degrees), 6, "adversarial")

    weights = [F(1, 2 ** sum(abs(component - 1) for component in vertex)) for vertex in vertices]
    ratios = [weights[left] / weights[right] for left, right, _axis, _parity in edges]
    check("weight ratios", min(ratios) >= F(1, 2) and max(ratios) <= 2, [min(ratios), max(ratios)], "[1/2,2]", "weights")

    coupling, chi, square_root_gamma, gamma, kappa = F(3, 5), F(7, 4), F(2, 5), F(4, 25), F(2)
    C_match = 1 + kappa * coupling * coupling / (2 * chi * square_root_gamma)
    check("derived coefficient", C_match == F(53, 35), C_match, F(53, 35), "form")
    for value in (F(-3, 2), F(-1, 3), F(2, 5), F(7, 4)):
        d = F(1, 7)
        lhs = (value + d * coupling * F(2, 3)) ** 2
        rhs = (1 + d) * value**2 + (d*d + d) * (coupling * F(2, 3))**2
        check(f"shift scalar fixture {value}", lhs <= rhs, [lhs, rhs], "lhs<=rhs", "form")
        check(f"quartic scalar fixture {value}", 2 * square_root_gamma * value**2 <= 1 + gamma * value**4, 2 * square_root_gamma * value**2, "<=1+gamma*q^4", "form")

    fixtures = []
    for seed in range(4):
        momentum = [F(1 + seed + 2 * x + 3 * y + 4 * z, 5) for x, y, z in vertices]
        position = [F(1 + seed + x + 2 * y - z, 4) for x, y, z in vertices]
        fixtures.append((momentum, position))
    delta = F(1, 7)
    for index, (momentum, position) in enumerate(fixtures):
        before = energy(weights, momentum, position, chi, gamma)
        for sign in (1, -1):
            for colour, layer in sorted(layers.items()):
                after = energy(weights, shifted(momentum, position, layer, sign * delta, coupling), position, chi, gamma)
                check(f"matching form fixture {index} sign {sign} layer {colour}", after <= (1 + C_match * delta) * before, after, f"<={(1 + C_match * delta) * before}", "form")
            full_after = energy(weights, shifted(momentum, position, edges, sign * delta, coupling), position, chi, gamma)
            check(f"full six-layer fixture {index} sign {sign}", full_after <= (1 + C_match * delta) ** 6 * before, full_after, f"<={(1 + C_match * delta) ** 6 * before}", "product")

    endpoint_exponent = 3 * C_match
    check("endpoint exponent", endpoint_exponent == F(159, 35), endpoint_exponent, F(159, 35), "product")
    for steps in (1, 2, 5, 11):
        t = F(3, 5)
        factor = (1 + C_match * t / steps) ** (3 * steps)
        check(f"exponential product steps={steps}", float(factor) <= math.exp(float(3 * C_match * t)) + 1e-12, factor, "<=exp(3*C*T)", "product")
    check("onsite assumption retained", manifest["onsite_factor"]["operator_theorem_assumption"] == "conditional", manifest["onsite_factor"]["operator_theorem_assumption"], "conditional", "scope")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": len(rows),
        "total": len(rows),
        "failed": 0,
        "assertions": rows,
        "derived": {
            "box_vertices": len(vertices),
            "box_edges": len(edges),
            "layer_count": len(layers),
            "layer_sizes": sorted(len(layer) for layer in layers.values()),
            "C_match": C_match,
            "endpoint_exponent": endpoint_exponent,
            "finite_common_core_induced_norm_closed": True,
            "volume_uniform_split_envelope_closed": True,
            "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False,
            "qft_kms_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"],
        "exploration_id": manifest["exploration_id"],
    }
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT MATCHING-LAYER PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
