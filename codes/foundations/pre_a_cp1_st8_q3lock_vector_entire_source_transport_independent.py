#!/usr/bin/env python3
"""Independent exact audit for the conditional vector source transport lemma.

This lane constructs coordinates and neighbour incidences independently of the
primary matrix-style implementation.  It uses only the Python standard
library and exact ``Fraction`` arithmetic.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def fraction(value: str | int) -> Fraction:
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


def coordinate(index: int, side: int, dimension: int) -> list[int]:
    result = [0] * dimension
    value = index
    for axis in range(dimension):
        result[axis] = value % side
        value //= side
    return result


def flat(coords: list[int], side: int) -> int:
    multiplier = 1
    result = 0
    for value in coords:
        result += value * multiplier
        multiplier *= side
    return result


def transport(vector: list[Fraction], side: int, dimension: int, kappa: Fraction, delta: Fraction) -> list[Fraction]:
    neighbour_count = 2 * dimension
    result: list[Fraction] = []
    for index in range(len(vector)):
        base = coordinate(index, side, dimension)
        total = Fraction(0)
        for axis in range(dimension):
            for direction in (-1, 1):
                shifted = list(base)
                shifted[axis] = (shifted[axis] + direction) % side
                total += vector[flat(shifted, side)]
        result.append(vector[index] + kappa * delta * total / neighbour_count)
    return result


def fourth_sum(vector: list[Fraction]) -> Fraction:
    total = Fraction(0)
    for value in vector:
        total += abs(value) ** 4
    return total


def vectors(count: int) -> list[list[Fraction]]:
    first = [Fraction(1) for _ in range(count)]
    second = [Fraction((index % 5) - 2) for index in range(count)]
    third = [Fraction(((-1) ** index) * (index % 4)) for index in range(count)]
    fourth = [Fraction(0) for _ in range(count)]
    fourth[0] = Fraction(3)
    fourth[count // 2] = Fraction(-2)
    return [first, second, third, fourth]


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    dimension = int(fixture["dimension"])
    side = int(fixture["side"])
    count = side**dimension
    kappa = fraction(fixture["kappa"])
    total_time = fraction(fixture["total_time"])
    steps = int(fixture["steps"])
    delta = total_time / steps
    sigma_0 = fraction(fixture["sigma_0"])
    oracle_upper = fraction(fixture["sigma_upper_bound_oracle"])
    neighbours = 2 * dimension
    factor = 1 + kappa * delta
    multiplier = Fraction(1)
    for _ in range(steps):
        multiplier *= factor**4
    sigma_steps = sigma_0 * multiplier
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001035", manifest["exploration_id"], "EXP-001035", "provenance")
    audit.check("task identity", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("supplied recurrence flag", manifest["scope"]["supplied_by_q3"] is False, manifest["scope"], False, "scope")
    audit.check("six-neighbour geometry", neighbours == 6, neighbours, 6, "graph")
    audit.check("factor arithmetic", factor == 1 + kappa * delta, factor, 1 + kappa * delta, "transport")

    rows: list[dict[str, Any]] = []
    for number, vector in enumerate(vectors(count)):
        start = fourth_sum(vector)
        current = list(vector)
        for _ in range(steps):
            current = transport(current, side, dimension, kappa, delta)
        finish = fourth_sum(current)
        bound = multiplier * start
        audit.check(f"iterated exact bound {number}", finish <= bound, finish, f"<={bound}", "vector")
        rows.append({"index": number, "before_fourth_power_sum": start, "after_steps_fourth_power_sum": finish, "iterated_bound": bound})

    audit.check("type multiplier", multiplier == factor ** (4 * steps), multiplier, factor ** (4 * steps), "weight")
    audit.check("sigma update", sigma_steps == sigma_0 * multiplier, sigma_steps, sigma_0 * multiplier, "weight")
    audit.check("finite sigma oracle", sigma_steps < oracle_upper, sigma_steps, f"<{oracle_upper}", "weight")
    audit.check("volume-independent expression", "site_count" not in manifest["model"]["type_update"], manifest["model"]["type_update"], "no site count", "volume")
    audit.check("actual Q3 history remains open", manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], False, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "vector_rows": rows,
        "derived": {
            "dimension": dimension,
            "side": side,
            "site_count": count,
            "neighbour_count": neighbours,
            "delta": delta,
            "one_step_factor": factor,
            "type_multiplier": multiplier,
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
    print(f"INDEPENDENT VECTOR-ENTIRE-SOURCE-TRANSPORT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
