#!/usr/bin/env python3
"""Independent integer-loop control for the R-444 scalar shell tail."""

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

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-exponential_shell_tail/independent.json"


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
    if radius == 0: return 1
    count = 0
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                count += int(abs(x) + abs(y) + abs(z) == radius)
    return count


def tail_formula(radius: int) -> Fraction:
    return Fraction(3 * (4 * radius * radius + 8 * radius + 14), 2 ** (radius - 1))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["finite_contract"]
    side_min, side_max, r_max = int(fixture["box_side_min"]), int(fixture["box_side_max"]), 12
    checks: list[dict[str, Any]] = []; check_count = 0; samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        check_count += 1
        if len(samples) < 24: samples.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]] == ["R-444", "EXP-001289", False, "EXPONENTIAL_SHELL_TAIL_AUDITED"], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-444/EXP-001289/false/audited", "provenance")
    check("contract", [manifest["finite_contract"]["dimension"], side_min, side_max] == [3, 2, 8], [manifest["finite_contract"]["dimension"], side_min, side_max], "3D boxes 2..8", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for key in ("shell_count_formula_checked", "finite_box_tail_dominated", "closed_form_tail_recurrence_checked", "lean_arithmetic_crosscheck", "geometric_shell_tail_closed"):
        check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("boundary_commutator_decay_closed", "history_tail_closed", "weighted_operator_form_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    for radius in range(0, r_max + 1):
        expected = 1 if radius == 0 else 4 * radius * radius + 2
        check(f"independent shell count {radius}", shell_count(radius) == expected, shell_count(radius), expected, "shell")
    for radius in range(1, r_max + 1):
        difference = tail_formula(radius) - tail_formula(radius + 1)
        expected = Fraction(3 * shell_count(radius), 2 ** radius)
        check(f"independent tail recurrence {radius}", difference == expected, difference, expected, "tail")
    boxes = list(product(range(side_min, side_max + 1), repeat=3)); total_edges = total_tail_rows = 0; maximum_ratio = Fraction(0); summaries: list[dict[str, Any]] = []
    for box_index, sides in enumerate(boxes):
        edges: list[tuple[tuple[int, int, int], Fraction]] = []
        for x in range(sides[0]):
            for y in range(sides[1]):
                for z in range(sides[2]):
                    lower = (x, y, z)
                    for axis, side in enumerate(sides):
                        if lower[axis] + 1 < side:
                            weight = Fraction(1, 2 ** (abs(x) + abs(y) + abs(z)))
                            edges.append((lower, weight))
        expected_edges = sum((sides[axis] - 1) * math.prod(sides[:axis] + sides[axis + 1:]) for axis in range(3))
        check(f"box {box_index} edges", len(edges) == expected_edges, len(edges), expected_edges, "finite-box")
        box_ratio = Fraction(0)
        for radius in range(1, r_max + 1):
            finite_tail = sum((weight for lower, weight in edges if sum(abs(value) for value in lower) >= radius), Fraction(0))
            bound = tail_formula(radius); check(f"box {box_index} tail {radius}", finite_tail <= bound, finite_tail, bound, "finite-box")
            total_tail_rows += 1
            if bound and finite_tail / bound > box_ratio: box_ratio = finite_tail / bound
        maximum_ratio = max(maximum_ratio, box_ratio); summaries.append({"sides": list(sides), "edges": len(edges), "max_tail_ratio": str(box_ratio)}); total_edges += len(edges)
    check("all finite tails dominated", True, total_tail_rows, total_tail_rows, "finite-box")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r444-independent/1.0", "manifest": MANIFEST.relative_to(ROOT).as_posix(), "result_id": "R-444", "exploration_id": "EXP-001289", "claim_id": manifest["claim_ids"][0], "run_kind": "independent", "verdict": "INDEPENDENT_EXPONENTIAL_SHELL_TAIL_CONTROL", "passed": check_count, "assertion_count": check_count, "assertions": samples, "assertion_samples_truncated": check_count > len(samples), "derived": {"box_count": len(boxes), "tail_radius_range": [1, r_max], "shell_count_formula_checked": True, "closed_form_tail_recurrence_checked": True, "finite_box_tail_dominated": True, "total_edges": total_edges, "total_tail_rows": total_tail_rows, "maximum_finite_to_bound_ratio": str(maximum_ratio), "tail_at_1": str(tail_formula(1)), "tail_at_12": str(tail_formula(12)), "boxes": summaries, "geometric_shell_tail_closed": True, "boundary_commutator_decay_closed": False, "history_tail_closed": False, "weighted_operator_form_closed": False, "common_core_closed": False, "common_alpha_closed": False, "pre_a_closed": False, "sector_a_closed": False}, "scope": {"independent_integer_loop": True, "claim_bearing": False, "operator_or_physical_promotion": False}, "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    destination = output if output.is_absolute() else ROOT / output; atomic_json(destination, payload)
    print(f"R-444 INDEPENDENT {payload['verdict']} {check_count}/{check_count} boxes={len(boxes)} edges={total_edges} tail_rows={total_tail_rows}", flush=True); return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run(args.output)
    if args.self_test: assert payload["verdict"] == "INDEPENDENT_EXPONENTIAL_SHELL_TAIL_CONTROL" and payload["derived"]["finite_box_tail_dominated"]; print("R-444 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__": raise SystemExit(main())
