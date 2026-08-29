#!/usr/bin/env python3
"""Hostile mutation lane for the R-422 residual reserve interface."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
SLUG = "residual_core_tail_reserve"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}" / "hostile.json"


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


def validate_inputs(core_gap: float, tail_floor: float, cross_norm: float) -> float:
    values = (core_gap, tail_floor, cross_norm)
    if not all(math.isfinite(value) for value in values):
        raise AssertionError("reserve inputs must be finite")
    if core_gap < 0.0 or tail_floor < 0.0 or cross_norm < 0.0:
        raise AssertionError("reserve inputs must be nonnegative")
    return min(core_gap, tail_floor) - cross_norm


def validate_claim(core_gap: float, tail_floor: float, cross_norm: float, claimed: float) -> None:
    expected = validate_inputs(core_gap, tail_floor, cross_norm)
    if not math.isfinite(claimed) or claimed > expected + 1.0e-12:
        raise AssertionError("claimed reserve exceeds conservative bound")


def validate_tail_floor(direct_tail_gap: float, declared_floor: float) -> None:
    if not math.isfinite(direct_tail_gap) or not math.isfinite(declared_floor) or direct_tail_gap < declared_floor:
        raise AssertionError("tail floor is not certified")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, fn: Callable[[], None], group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        try:
            fn()
        except AssertionError:
            checks.append({"name": name, "group": group, "status": "PASS", "expected": "mutation rejected"})
            return
        raise AssertionError(f"hostile mutation accepted: {name}")

    a, b, eta = 2.5, 0.75, 0.2
    expected = validate_inputs(a, b, eta)
    check("negative core gap", lambda: validate_inputs(-a, b, eta), "positivity")
    check("negative tail floor", lambda: validate_inputs(a, -b, eta), "positivity")
    check("negative cross norm", lambda: validate_inputs(a, b, -eta), "positivity")
    check("nonfinite cross norm", lambda: validate_inputs(a, b, float("nan")), "finiteness")
    check("omitted cross term", lambda: validate_claim(a, b, eta, min(a, b)), "cross block")
    check("forged upward reserve", lambda: validate_claim(a, b, eta, expected + 0.1), "reserve")
    check("forged tail floor", lambda: validate_tail_floor(0.7, b), "tail Hardy")

    if not (manifest["result_id"] == "R-422" and manifest["exploration_id"] == "EXP-001267" and manifest["claim_bearing"] is False):
        raise AssertionError("manifest identity")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r422-hostile/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "controls": {
            "all_mutations_rejected": True,
            "mutation_count": assertion_count,
            "numeric_evaluation": False,
            "physical_promotion": False,
        },
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-422 HOSTILE PASS {assertion_count}/{assertion_count} invalid mutations rejected")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)


if __name__ == "__main__":
    main()
