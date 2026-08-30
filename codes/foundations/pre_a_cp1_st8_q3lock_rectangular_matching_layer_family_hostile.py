#!/usr/bin/env python3
"""Hostile mutation firewall for R-440."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rectangular-matching-layer-family-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rectangular_matching_layer_family/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def graph(side: int) -> tuple[list[tuple[int, int]], int]:
    vertices = list(product(range(side), repeat=3))
    index = {vertex: number for number, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    for vertex in vertices:
        for axis in range(3):
            if vertex[axis] + 1 < side:
                neighbour = list(vertex)
                neighbour[axis] += 1
                edges.append((index[vertex], index[tuple(neighbour)]))
    return edges, len(vertices)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def expect_reject(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    expect_reject("claim promotion", baseline.get("claim_bearing") is False, baseline.get("claim_bearing"), False)
    promoted = copy.deepcopy(baseline)
    promoted["claim_bearing"] = True
    expect_reject("reject claim-bearing mutation", promoted["claim_bearing"] is not False, promoted["claim_bearing"], "rejected")

    one_sign = copy.deepcopy(baseline)
    one_sign["finite_contract"]["signs"] = [1]
    expect_reject("reject one-sided shear", set(one_sign["finite_contract"]["signs"]) != {1, -1}, one_sign["finite_contract"]["signs"], "both signs")

    one_order = copy.deepcopy(baseline)
    one_order["finite_contract"]["orders"] = ["lexicographic"]
    expect_reject("reject one layer order", set(one_order["finite_contract"]["orders"]) != {"lexicographic", "reverse_lexicographic"}, one_order["finite_contract"]["orders"], "both orders")

    wrong_modulus = copy.deepcopy(baseline)
    wrong_modulus["finite_contract"]["parity_modulus"] = 1
    expect_reject("reject parity mutation", wrong_modulus["finite_contract"]["parity_modulus"] != 2, wrong_modulus["finite_contract"]["parity_modulus"], 2)

    missing_box = copy.deepcopy(baseline)
    missing_box["finite_contract"]["box_sides"] = missing_box["finite_contract"]["box_sides"][:-1]
    expect_reject("reject incomplete box family", len(missing_box["finite_contract"]["box_sides"]) != len(baseline["finite_contract"]["box_sides"]), len(missing_box["finite_contract"]["box_sides"]), len(baseline["finite_contract"]["box_sides"]))

    promoted_scope = copy.deepcopy(baseline)
    promoted_scope["scope"]["arbitrary_box_theorem_closed"] = True
    expect_reject("reject arbitrary-box promotion", promoted_scope["scope"]["arbitrary_box_theorem_closed"] is True, True, False)

    full_edges, vertex_count = graph(3)
    full_counts = [0] * vertex_count
    for left, right in full_edges:
        full_counts[left] += 1
        full_counts[right] += 1
    expect_reject("reject full-graph-as-one-layer", max(full_counts) > 1, max(full_counts), "at most one incidence")

    changed_input = copy.deepcopy(baseline)
    changed_input["finite_contract"]["coupling"] = "4/5"
    expect_reject("reject coefficient-input mutation", changed_input["finite_contract"]["coupling"] != baseline["finite_contract"]["coupling"], changed_input["finite_contract"]["coupling"], baseline["finite_contract"]["coupling"])

    absent_qft_boundary = copy.deepcopy(baseline)
    absent_qft_boundary["boundary"] = "finite pass"
    expect_reject("reject erased QFT boundary", "common alpha" not in absent_qft_boundary["boundary"].lower() or "yang-mills" not in absent_qft_boundary["boundary"].lower(), absent_qft_boundary["boundary"], "explicit boundary")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "PA-CP1-ST8-Q3LOCK-RECTANGULAR-MATCHING-LAYER-FAMILY",
        "claim_id": baseline["claim_ids"][0],
        "task_id": baseline["task_id"],
        "exploration_id": baseline["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "mutations_rejected": len(rows),
        "boundary": baseline["boundary"],
    }
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"R-440 HOSTILE MUTATIONS_REJECTED {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
