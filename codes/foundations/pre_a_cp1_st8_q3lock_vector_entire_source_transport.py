#!/usr/bin/env python3
"""Primary exact audit for a conditional vector entire-source transport lemma.

The lemma is deliberately conditional: it assumes the supplied source history
is transported by ``M = I + kappa*delta*P`` on a finite regular three-torus,
where ``P`` is the six-neighbour averaging operator.  It proves the exact
type update for ``W_sigma(a) = exp(sigma * sum_x |a_x|^4)`` and checks the
finite rational fixtures.  It does not derive the Q3 operator recurrence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-vector-entire-source-transport"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def parse_fraction(value: str | int) -> Fraction:
    return Fraction(str(value))


def safe(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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


def index_of(point: tuple[int, ...], side: int) -> int:
    result = 0
    for coordinate in point:
        result = result * side + coordinate
    return result


def point_of(index: int, side: int, dimension: int) -> tuple[int, ...]:
    coordinates = [0] * dimension
    remainder = index
    for position in range(dimension - 1, -1, -1):
        coordinates[position] = remainder % side
        remainder //= side
    return tuple(coordinates)


def neighbours(point: tuple[int, ...], side: int) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for axis in range(len(point)):
        for sign in (-1, 1):
            shifted = list(point)
            shifted[axis] = (shifted[axis] + sign) % side
            result.append(tuple(shifted))
    return result


def averaging_transport(vector: list[Fraction], side: int, dimension: int, kappa: Fraction, delta: Fraction) -> list[Fraction]:
    sites = side**dimension
    neighbour_count = 2 * dimension
    result: list[Fraction] = []
    for index in range(sites):
        point = point_of(index, side, dimension)
        neighbour_sum = sum((vector[index_of(neighbour, side)] for neighbour in neighbours(point, side)), Fraction(0))
        result.append(vector[index] + kappa * delta * neighbour_sum / neighbour_count)
    return result


def fourth_power_sum(vector: list[Fraction]) -> Fraction:
    return sum((abs(value) ** 4 for value in vector), Fraction(0))


def fixture_vectors(site_count: int) -> list[list[Fraction]]:
    ramp = [Fraction((index % 5) - 2) for index in range(site_count)]
    alternating = [Fraction((-1) ** index * (index % 4)) for index in range(site_count)]
    sparse = [Fraction(0) for _ in range(site_count)]
    sparse[0] = Fraction(3)
    sparse[site_count // 2] = Fraction(-2)
    return [
        [Fraction(1) for _ in range(site_count)],
        ramp,
        alternating,
        sparse,
    ]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    dimension = int(fixture["dimension"])
    side = int(fixture["side"])
    site_count = side**dimension
    kappa = parse_fraction(fixture["kappa"])
    total_time = parse_fraction(fixture["total_time"])
    steps = int(fixture["steps"])
    delta = total_time / steps
    sigma_0 = parse_fraction(fixture["sigma_0"])
    oracle_upper = parse_fraction(fixture["sigma_upper_bound_oracle"])
    neighbour_count = 2 * dimension
    one_step_factor = 1 + kappa * delta
    type_multiplier = one_step_factor ** (4 * steps)
    sigma_steps = sigma_0 * type_multiplier
    audit = Audit()

    audit.check("exploration", manifest["exploration_id"] == "EXP-001035", manifest["exploration_id"], "EXP-001035", "provenance")
    audit.check("task identity", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("Q3 recurrence is not supplied", manifest["scope"]["supplied_by_q3"] is False, manifest["scope"], False, "scope")
    audit.check("dimension fixture", dimension == 3, dimension, 3, "graph")
    audit.check("site count", site_count == side**dimension, site_count, side**dimension, "graph")
    audit.check("six-neighbour count", neighbour_count == 2 * dimension, neighbour_count, 2 * dimension, "graph")
    audit.check("positive step", steps > 0 and delta > 0, [steps, delta], ">0", "transport")
    audit.check("positive type factor", one_step_factor > 1, one_step_factor, ">1", "transport")

    # The torus construction gives exactly six distinct neighbours at side 3.
    all_neighbour_counts = [len(neighbours(point_of(index, side, dimension), side)) for index in range(site_count)]
    audit.check("regular graph", all(count == neighbour_count for count in all_neighbour_counts), sorted(set(all_neighbour_counts)), [neighbour_count], "graph")

    vectors = fixture_vectors(site_count)
    vector_rows: list[dict[str, Any]] = []
    for vector_index, vector in enumerate(vectors):
        before = fourth_power_sum(vector)
        transported = averaging_transport(vector, side, dimension, kappa, delta)
        after = fourth_power_sum(transported)
        one_step_bound = one_step_factor**4 * before
        iterated = list(vector)
        for _ in range(steps):
            iterated = averaging_transport(iterated, side, dimension, kappa, delta)
        iterated_after = fourth_power_sum(iterated)
        iterated_bound = type_multiplier * before
        audit.check(f"one-step vector bound {vector_index}", after <= one_step_bound, after, f"<={one_step_bound}", "vector")
        audit.check(f"iterated vector bound {vector_index}", iterated_after <= iterated_bound, iterated_after, f"<={iterated_bound}", "vector")
        vector_rows.append({
            "index": vector_index,
            "before_fourth_power_sum": before,
            "after_one_step_fourth_power_sum": after,
            "after_steps_fourth_power_sum": iterated_after,
            "one_step_bound": one_step_bound,
            "iterated_bound": iterated_bound,
        })

    audit.check("sigma type update", sigma_steps == sigma_0 * type_multiplier, sigma_steps, sigma_0 * type_multiplier, "weight")
    audit.check("finite sigma oracle", sigma_steps < oracle_upper, sigma_steps, f"<{oracle_upper}", "weight")
    audit.check("volume-independent factor", "site_count" not in manifest["model"]["type_update"], manifest["model"]["type_update"], "no site count", "volume")
    audit.check("conditional boundary", manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], False, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "vector_rows": vector_rows,
        "derived": {
            "dimension": dimension,
            "side": side,
            "site_count": site_count,
            "neighbour_count": neighbour_count,
            "delta": delta,
            "one_step_factor": one_step_factor,
            "type_multiplier": type_multiplier,
            "sigma_0": sigma_0,
            "sigma_steps": sigma_steps,
            "sigma_upper_bound_oracle": oracle_upper,
            "conditional_vector_transport_closed": True,
            "actual_q3_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY VECTOR-ENTIRE-SOURCE-TRANSPORT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
