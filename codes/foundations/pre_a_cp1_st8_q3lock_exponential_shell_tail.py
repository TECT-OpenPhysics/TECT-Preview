#!/usr/bin/env python3
"""Exact scalar shell-tail audit for the R-444 geometric majorant."""

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

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-exponential_shell_tail/primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def shell_count(radius: int) -> int:
    return 1 if radius == 0 else 4 * radius * radius + 2


def tail_formula(radius: int) -> Fraction:
    if radius < 1: raise ValueError("tail formula is declared for radius >= 1")
    return Fraction(3 * (4 * radius * radius + 8 * radius + 14), 2 ** (radius - 1))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_contract"]
    dimension = int(fixture["dimension"]); side_min = int(fixture["box_side_min"]); side_max = int(fixture["box_side_max"]); r_max = 12
    checks: list[dict[str, Any]] = []; check_count = 0; samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        check_count += 1
        if len(samples) < 24: samples.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]] == ["R-444", "EXP-001289", "T-054", False, "EXPONENTIAL_SHELL_TAIL_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]], "R-444/EXP-001289/T-054/false/audited", "provenance")
    check("contract", [dimension, side_min, side_max] == [3, 2, 8], [dimension, side_min, side_max], "3D boxes 2..8", "contract")
    check("shell formula", fixture["shell_count"] == "N_3(n)=4*n^2+2 for n>=1 and N_3(0)=1", fixture["shell_count"], "N_3", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for key in ("shell_count_formula_checked", "finite_box_tail_dominated", "closed_form_tail_recurrence_checked", "lean_arithmetic_crosscheck", "geometric_shell_tail_closed"):
        check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("boundary_commutator_decay_closed", "history_tail_closed", "weighted_operator_form_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    check("shell count n=0", shell_count(0) == 1, shell_count(0), 1, "shell")
    for radius in range(1, r_max + 1):
        points = list(product(range(-radius, radius + 1), repeat=dimension))
        count = sum(1 for point in points if sum(abs(value) for value in point) == radius)
        check(f"ambient shell count {radius}", count == shell_count(radius), count, shell_count(radius), "shell")
    check("tail base", tail_formula(1) == Fraction(78), tail_formula(1), "78", "tail")
    for radius in range(1, r_max + 1):
        difference = tail_formula(radius) - tail_formula(radius + 1)
        expected = Fraction(3 * shell_count(radius), 2 ** radius)
        check(f"tail recurrence {radius}", difference == expected, difference, expected, "tail")
        check(f"tail monotone {radius}", tail_formula(radius + 1) < tail_formula(radius), [tail_formula(radius), tail_formula(radius + 1)], "strictly decreasing", "tail")
    boxes = list(product(range(side_min, side_max + 1), repeat=dimension))
    total_edges = 0; total_tail_rows = 0; maximum_ratio = Fraction(0); summaries: list[dict[str, Any]] = []
    for box_index, sides in enumerate(boxes):
        vertices = list(product(*[range(side) for side in sides])); index = {vertex: i for i, vertex in enumerate(vertices)}
        edges: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for lower in vertices:
            for axis, side in enumerate(sides):
                if lower[axis] + 1 < side:
                    upper = list(lower); upper[axis] += 1; edges.append((lower, tuple(upper)))
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1:]) for axis in range(dimension))
        check(f"box {box_index} edge count", len(edges) == expected_edges, len(edges), expected_edges, "finite-box")
        edge_weights = [Fraction(1, 2 ** sum(abs(value) for value in lower)) for lower, _upper in edges]
        for radius in range(1, r_max + 1):
            finite_tail = sum((weight for (lower, _upper), weight in zip(edges, edge_weights) if sum(abs(value) for value in lower) >= radius), Fraction(0))
            bound = tail_formula(radius)
            check(f"box {box_index} tail {radius}", finite_tail <= bound, finite_tail, bound, "finite-box")
            total_tail_rows += 1
            if bound and finite_tail / bound > maximum_ratio: maximum_ratio = finite_tail / bound
        summaries.append({"sides": list(sides), "vertices": len(vertices), "edges": len(edges), "max_tail_ratio": str(maximum_ratio)})
        total_edges += len(edges)
    check("all finite tails dominated", True, total_tail_rows, total_tail_rows, "finite-box")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r444-primary/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-444", "exploration_id": "EXP-001289", "claim_id": manifest["claim_ids"][0], "run_kind": "primary", "verdict": "EXPONENTIAL_SHELL_TAIL_AUDITED", "passed": check_count, "assertion_count": check_count, "assertions": samples, "assertion_samples_truncated": check_count > len(samples), "derived": {"dimension": dimension, "box_count": len(boxes), "tail_radius_range": [1, r_max], "shell_count_formula_checked": True, "closed_form_tail_recurrence_checked": True, "finite_box_tail_dominated": True, "total_edges": total_edges, "total_tail_rows": total_tail_rows, "maximum_finite_to_bound_ratio": str(maximum_ratio), "tail_at_1": str(tail_formula(1)), "tail_at_12": str(tail_formula(12)), "boxes": summaries, "geometric_shell_tail_closed": True, "boundary_commutator_decay_closed": False, "history_tail_closed": False, "weighted_operator_form_closed": False, "common_core_closed": False, "common_alpha_closed": False, "pre_a_closed": False, "sector_a_closed": False}, "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    destination = output if output.is_absolute() else REPO / output; atomic_json(destination, payload)
    print(f"R-444 PRIMARY {payload['verdict']} {check_count}/{check_count} boxes={len(boxes)} edges={total_edges} tail_rows={total_tail_rows}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run(args.output)
    if args.self_test: assert payload["verdict"] == "EXPONENTIAL_SHELL_TAIL_AUDITED" and payload["derived"]["finite_box_tail_dominated"]; print("R-444 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__": raise SystemExit(main())
