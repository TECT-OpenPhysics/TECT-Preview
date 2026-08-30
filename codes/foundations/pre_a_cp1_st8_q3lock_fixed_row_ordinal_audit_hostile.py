#!/usr/bin/env python3
"""Hostile mutation controls for the R-432 ordinal contract."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-fixed-row-ordinal-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-fixed_row_ordinal_audit/hostile.json"


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


def check_contract(manifest: dict[str, Any]) -> None:
    if manifest["result_id"] != "R-432" or manifest["exploration_id"] != "EXP-001277" or manifest["claim_bearing"] is not False:
        raise ValueError("identity mutation accepted")
    contract = manifest["row_contract"]
    if int(contract["target_emission_ordinal"]) != 7 or int(contract["target_parent_coordinate"]) != 6:
        raise ValueError("target ordinal or parent mapping changed")
    if int(contract["historical_subtract_one_ordinal"]) == int(contract["target_emission_ordinal"]):
        raise ValueError("historical subtract-one row aliases target")
    if contract["comparison_tolerance"] != "5e-7":
        raise ValueError("comparison tolerance changed")
    if contract["r426_direct_reference"] != "5.36318835004781" or contract["r422_reference"] != "5.363184967163699":
        raise ValueError("fixed references changed")
    order = manifest["row_contract"]["order"]
    if len(order) != 3 or not order[0].startswith("emission ordinal 0") or not order[1].startswith("emission ordinal 1"):
        raise ValueError("emission order contract changed")
    scope = manifest["scope"]
    if scope["original_source_interval_certified"] is not False or scope["residual_reuse_closed"] is not False or scope["no_tier_change"] is not True:
        raise ValueError("source or tier scope promoted")


def mutate(base: dict[str, Any], label: str, operation: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    candidate = copy.deepcopy(base)
    operation(candidate)
    try:
        check_contract(candidate)
    except ValueError as error:
        return {"name": label, "status": "REJECTED", "reason": str(error)}
    return {"name": label, "status": "ACCEPTED-INVALID"}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    controls = [
        mutate(manifest, "select ordinal 6 as target", lambda m: m["row_contract"].update({"target_emission_ordinal": 6})),
        mutate(manifest, "map target to parent 5", lambda m: m["row_contract"].update({"target_parent_coordinate": 5})),
        mutate(manifest, "alias historical subtract-one with target", lambda m: m["row_contract"].update({"historical_subtract_one_ordinal": 7})),
        mutate(manifest, "relax comparison tolerance", lambda m: m["row_contract"].update({"comparison_tolerance": "5e-4"})),
        mutate(manifest, "promote claim-bearing status", lambda m: m.update({"claim_bearing": True})),
        mutate(manifest, "promote original-source interval", lambda m: m["scope"].update({"original_source_interval_certified": True})),
        mutate(manifest, "drop unconditional ordinal from order", lambda m: m["row_contract"].update({"order": m["row_contract"]["order"][1:]})),
    ]
    if any(control["status"] != "REJECTED" for control in controls):
        raise AssertionError(controls)
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r432-hostile/1.0",
        "result_id": "R-432",
        "exploration_id": "EXP-001277",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": len(controls),
        "controls": {"all_mutations_rejected": True, "mutations": controls, "original_source_interval_certified": False, "residual_reuse_closed": False, "no_tier_change": True},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-432 HOSTILE PASS {len(controls)}/{len(controls)} invalid row/status mutations rejected")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
