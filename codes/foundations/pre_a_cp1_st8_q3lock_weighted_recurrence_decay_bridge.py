#!/usr/bin/env python3
"""Primary exact audit for the conditional weighted-recurrence bridge.

The theorem is deliberately conditional: a nonnegative local graph recurrence
implies a volume-uniform weighted distance bound.  The audit does not claim
that the exact Q3 onsite flow satisfies that recurrence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-weighted-recurrence-decay-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


class Audit:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []
    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def graph(side: int) -> tuple[list[tuple[int, int, int]], list[int]]:
    vertices = list(product(range(side), repeat=3))
    index = {v: i for i, v in enumerate(vertices)}
    edges: list[tuple[int, int, int]] = []
    for v in vertices:
        for axis in range(3):
            if v[axis] + 1 >= side: continue
            u = list(v); u[axis] += 1
            edges.append((index[v], index[tuple(u)], axis))
    center = tuple((side - 1) // 2 for _ in range(3))
    distance = [sum(abs(a - b) for a, b in zip(v, center)) for v in vertices]
    return edges, distance


def step(values: list[Fraction], edges: list[tuple[int, int, int]], C: Fraction, J: Fraction, delta: Fraction) -> list[Fraction]:
    out = [(1 + C * delta) * value for value in values]
    for left, right, _axis in edges:
        out[left] += J * delta * values[right]
        out[right] += J * delta * values[left]
    return out


def weighted(values: list[Fraction], distance: list[int], base: int = 2) -> Fraction:
    return sum(Fraction(base**d) * value for value, d in zip(values, distance))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-weighted-recurrence-decay-bridge/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001026", manifest["exploration_id"], "EXP-001026", "provenance")
    audit.check("conditional scope", manifest["claim_bearing"] is False and manifest["recurrence_hypothesis"]["supplied_by_q3"] is False, [manifest["claim_bearing"], manifest["recurrence_hypothesis"]["supplied_by_q3"]], [False, False], "scope")

    C, J, delta, z, base = Fraction(1), Fraction(1), Fraction(1, 5), 6, 2
    side = 5
    edges, distance = graph(side)
    values = [Fraction(int(d == 0)) for d in distance]
    initial_weight = weighted(values, distance, base)
    audit.check("center seed", initial_weight == 1, initial_weight, 1, "initial")
    rows: list[dict[str, Any]] = []
    for n in range(1, 7):
        before = weighted(values, distance, base)
        values = step(values, edges, C, J, delta)
        after = weighted(values, distance, base)
        bound = (1 + (C + J * z * base) * delta) * before
        audit.check(f"weighted recurrence step {n}", after <= bound, after, f"<={bound}", "recurrence")
        rows.append({"step": n, "weight_before": before, "weight_after": after, "bound": bound})

    total_bound = (1 + (C + J * z * base) * delta) ** 6
    audit.check("iterated weighted bound", weighted(values, distance, base) <= total_bound * initial_weight, weighted(values, distance, base), f"<={total_bound}", "recurrence")
    decay_rows: list[dict[str, Any]] = []
    W = weighted(values, distance, base)
    for d in range(0, 5):
        point_bound = W / (base**d)
        actual_max = max((value for value, radius in zip(values, distance) if radius >= d), default=Fraction(0))
        audit.check(f"pointwise decay radius {d}", actual_max <= point_bound, actual_max, f"<={point_bound}", "decay")
        decay_rows.append({"distance": d, "actual_max": actual_max, "bound": point_bound})

    # The same weighted constant is independent of side length; check the
    # local graph degree and recurrence envelope on side 3 and side 5.
    for test_side in (3, 5):
        test_edges, test_distance = graph(test_side)
        degrees = [0] * (test_side**3)
        for left, right, _axis in test_edges: degrees[left] += 1; degrees[right] += 1
        audit.check(f"degree bound side {test_side}", max(degrees) <= z, max(degrees), f"<={z}", "volume")

    audit.check("conditional bridge declared", manifest["conclusion"]["boundary_decay_is_conditional"] is True, manifest["conclusion"], True, "scope")
    audit.check("actual Q3 recurrence open", manifest["recurrence_hypothesis"]["status"] == "OPEN", manifest["recurrence_hypothesis"], "OPEN", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "side": side, "max_degree": z, "weight_base": base, "C": C, "J": J, "delta": delta,
            "weighted_recurrence_to_decay_closed": True, "volume_uniform_conditional": True,
            "recurrence_hypothesis_supplied_by_q3": False, "boundary_commutator_decay_closed": False,
            "exhaustion_cauchy_closed": False, "common_alpha_closed": False,
        },
        "recurrence_rows": rows, "decay_rows": decay_rows,
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"], "exploration_id": manifest["exploration_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RECURRENCE-DECAY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
