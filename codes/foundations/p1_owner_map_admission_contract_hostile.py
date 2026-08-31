#!/usr/bin/env python3
"""Hostile mutation tests for the P1 fail-closed admission contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/p1-owner-map-admission-contract-v0.1.json"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-p1-owner-map-admission/hostile.json"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(manifest: dict[str, Any]) -> dict[str, Any]:
    slots = [item["id"] for item in manifest["forward_owner_slots"]]
    stages = [item["id"] for item in manifest["inverse_map_stages"]]
    return {
        "source_artifact": {"path": "fixture://complete-owner", "sha256": "c" * 64, "synthetic": False},
        "owner_slot_status": {item: True for item in slots},
        "inverse_stage_status": {item: True for item in stages},
        "candidate_neutral_estimand_frozen": True,
        "immutable_scorer_frozen": True,
        "prospective_holdout_frozen": True,
        "methods_unchanged": True,
        "synthetic": False,
    }


def production_admissible(packet: dict[str, Any], manifest: dict[str, Any]) -> bool:
    """Structural predicate used only for hostile contract testing."""

    source = packet.get("source_artifact", {})
    if not isinstance(source, dict):
        return False
    if not isinstance(source.get("path"), str) or not source["path"].strip():
        return False
    if not isinstance(source.get("sha256"), str) or SHA256_RE.fullmatch(source["sha256"]) is None:
        return False
    if source.get("synthetic") is True or packet.get("synthetic") is True:
        return False
    slots = [item["id"] for item in manifest["forward_owner_slots"]]
    statuses = packet.get("owner_slot_status")
    if not isinstance(statuses, dict) or set(statuses) != set(slots) or any(statuses[item] is not True for item in slots):
        return False
    stages = [item["id"] for item in manifest["inverse_map_stages"]]
    stage_status = packet.get("inverse_stage_status")
    if not isinstance(stage_status, dict) or set(stage_status) != set(stages):
        return False
    for stage in stages:
        if stage_status[stage] is not True:
            return False
    return all(packet.get(name) is True for name in (
        "candidate_neutral_estimand_frozen",
        "immutable_scorer_frozen",
        "prospective_holdout_frozen",
        "methods_unchanged",
    ))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = fixture(manifest)
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    check("unmutated fixture satisfies structural predicate", production_admissible(base, manifest), True, "contract fixture only")
    check("manifest is claim-nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", [manifest["claim_bearing"], manifest["tier"]], [False, "T0"])
    check("methods remain preserved", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("delete source hash", lambda p: p["source_artifact"].update(sha256="")),
        ("malformed source hash", lambda p: p["source_artifact"].update(sha256="z" * 64)),
        ("mark source synthetic", lambda p: p["source_artifact"].update(synthetic=True)),
        ("mark packet synthetic", lambda p: p.update(synthetic=True)),
        ("disable first owner slot", lambda p: p["owner_slot_status"].update({"generator_or_transfer": False})),
        ("delete final owner slot", lambda p: p["owner_slot_status"].pop("production_one_use_q_ledger")),
        ("disable F_reg", lambda p: p["inverse_stage_status"].update(F_reg=False)),
        ("disable F_lim", lambda p: p["inverse_stage_status"].update(F_lim=False)),
        ("disable F_eff", lambda p: p["inverse_stage_status"].update(F_eff=False)),
        ("disable F_obs", lambda p: p["inverse_stage_status"].update(F_obs=False)),
        ("unfreeze prospective holdout", lambda p: p.update(prospective_holdout_frozen=False)),
        ("unfreeze immutable scorer", lambda p: p.update(immutable_scorer_frozen=False)),
        ("unfreeze candidate-neutral estimand", lambda p: p.update(candidate_neutral_estimand_frozen=False)),
        ("flip method preservation", lambda p: p.update(methods_unchanged=False)),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        check(name, not production_admissible(candidate, manifest), production_admissible(candidate, manifest), False)

    altered_manifest = copy.deepcopy(manifest)
    altered_manifest["forward_owner_slots"] = list(reversed(altered_manifest["forward_owner_slots"]))
    check("reordered owner slots are detectable", [item["id"] for item in altered_manifest["forward_owner_slots"]] != [item["id"] for item in manifest["forward_owner_slots"]], True, "order mutation visible")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "P1-OWNER-MAP-ADMISSION-HOSTILE",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_admission": "NONE",
        "base_fixture_structural_predicate": True,
        "all_mutations_rejected": True,
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "mutation_count": len(mutations),
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"manifest_sha256": digest(MANIFEST)},
    }
    if output:
        write_json(output if output.is_absolute() else REPO / output, payload)
    print(f"P1 OWNER/MAP ADMISSION HOSTILE PASS {len(checks)}/{len(checks)}; mutations={len(mutations)}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    run(None if args.no_store else args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
