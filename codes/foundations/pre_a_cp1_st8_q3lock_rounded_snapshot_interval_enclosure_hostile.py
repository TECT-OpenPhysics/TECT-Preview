#!/usr/bin/env python3
"""Hostile contract mutations for the R-431 interval certificate."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rounded-snapshot-interval-enclosure-manifest.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-rounded_snapshot_interval_enclosure/hostile.json"


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(candidate: dict[str, Any], baseline: dict[str, Any]) -> None:
    contract = candidate["interval_contract"]
    base = baseline["interval_contract"]
    scope = candidate["scope"]
    row = contract["fixed_row"]
    if candidate.get("claim_bearing") is not False:
        raise AssertionError("claim-bearing promotion is forbidden")
    if row != base["fixed_row"]:
        raise AssertionError("fixed row mutation is forbidden")
    if contract["comparison_tolerance"] != base["comparison_tolerance"]:
        raise AssertionError("comparison tolerance mutation is forbidden")
    if Decimal(contract["lower_probe"]) >= Decimal(contract["upper_probe"]):
        raise AssertionError("lower/upper probe ordering is invalid")
    if scope.get("original_source_interval_certified") is not False:
        raise AssertionError("original-source interval promotion is forbidden")
    if scope.get("residual_reuse_closed_for_original_source") is not False:
        raise AssertionError("original-source residual closure is forbidden")
    if candidate.get("status") != baseline.get("status"):
        raise AssertionError("status mutation is forbidden")


def run() -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutations: list[tuple[str, dict[str, Any]]] = []

    mutation = copy.deepcopy(baseline)
    mutation["claim_bearing"] = True
    mutations.append(("claim-bearing promotion", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["interval_contract"]["fixed_row"]["conditional_row_index"] = 6
    mutations.append(("conditional-row substitution", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["interval_contract"]["comparison_tolerance"] = "1e-3"
    mutations.append(("comparison-tolerance relaxation", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["interval_contract"]["lower_probe"] = mutation["interval_contract"]["upper_probe"]
    mutations.append(("collapsed interval bracket", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["scope"]["original_source_interval_certified"] = True
    mutations.append(("unrounded-source promotion", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["scope"]["residual_reuse_closed_for_original_source"] = True
    mutations.append(("residual-reuse closure", mutation))

    mutation = copy.deepcopy(baseline)
    mutation["status"] = "SOURCE_INTERVAL_CERTIFIED"
    mutations.append(("status promotion", mutation))

    outcomes: list[dict[str, Any]] = []
    for label, candidate in mutations:
        try:
            validate(candidate, baseline)
        except AssertionError as error:
            outcomes.append({"mutation": label, "rejected": True, "reason": str(error)})
        else:
            outcomes.append({"mutation": label, "rejected": False, "reason": "unexpected acceptance"})

    all_rejected = all(item["rejected"] for item in outcomes)
    if not all_rejected:
        raise AssertionError("hostile mutation accepted")
    payload = {
        "schema": "tect/pre-a-r431-hostile/1.0",
        "result_id": "R-431",
        "exploration_id": "EXP-001276",
        "claim_id": baseline["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "hostile",
        "verdict": "PASS",
        "controls": {
            "mutation_count": len(outcomes),
            "all_mutations_rejected": all_rejected,
            "rounded_snapshot_interval_certified": True,
            "original_source_interval_certified": False,
            "residual_reuse_closed_for_original_source": False,
            "outcomes": outcomes,
        },
        "source_hashes": {"manifest": sha256(MANIFEST)},
        "boundary": baseline["boundary"],
        "non_claims": baseline["non_claims"],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-431 HOSTILE PASS {len(outcomes)}/{len(outcomes)} invalid mutations rejected")
    return payload


if __name__ == "__main__":
    run()
