#!/usr/bin/env python3
"""Hostile contract tests for the PAH-OMC-020 ordered-epsilon bridge."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-ordered-epsilon-bridge-contract-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-ordered-epsilon-bridge/hostile.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def accepts(model: dict) -> bool:
    fixed = model.get("fixed_source", {})
    order = fixed.get("order", "").lower()
    symbols = model.get("symbols", {})
    bound = symbols.get("bound", "")
    conclusion = symbols.get("conclusion", "")
    non_claims = json.dumps(model.get("non_claims", [])).lower()
    return (
        model.get("schema") == "tect/pah-omc020-ordered-epsilon-bridge-contract/1.0"
        and fixed.get("functional") == "Exactly PAH-001-v1.json."
        and "j" in order and "first" in order and "anchored n" in order
        and "J_(n,j)" in bound and "D_n" in bound
        and "some N" in conclusion and "each such n" in conclusion
        and all(token in non_claims for token in ("physical pre-a", "qft", "gravity", "toe"))
        and "source-authorized owner packet" in model.get("next_single_question", "")
        and not model.get("physical_promotion", False)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mutations = {}
    mutation = copy.deepcopy(baseline)
    mutation["fixed_source"]["order"] = "n is selected first, then j tends to infinity"
    mutations["reversed_order"] = mutation
    mutation = copy.deepcopy(baseline)
    mutation["symbols"]["bound"] = "err_(n,j) <= J_(n,j)"
    mutations["removed_D_term"] = mutation
    mutation = copy.deepcopy(baseline)
    mutation["physical_promotion"] = True
    mutations["physical_promotion"] = mutation
    mutation = copy.deepcopy(baseline)
    mutation["fixed_source"]["functional"] = "A newly fitted functional"
    mutations["changed_functional"] = mutation

    rows = []
    for name, mutated in mutations.items():
        accepted = accepts(mutated)
        rows.append({"mutation": name, "status": "PASS" if not accepted else "FAIL", "accepted_by_guard": accepted})
        if accepted:
            raise AssertionError(f"hostile mutation was not rejected: {name}")
    baseline_acceptance = accepts(baseline)
    rows.append({"mutation": "baseline", "status": "PASS" if baseline_acceptance else "FAIL", "accepted_by_guard": baseline_acceptance})
    if not baseline_acceptance:
        raise AssertionError("baseline contract rejected by hostile guard")
    payload = {
        "schema": "tect/pah-omc020-ordered-epsilon-bridge-hostile/1.0",
        "audit_id": "PAH-OMC-020-ORDERED-EPSILON-BRIDGE-HOSTILE-001",
        "result_id": "R-555",
        "task_id": "T-064",
        "status": "PASS_HOSTILE_FIREWALLS",
        "verdict": "PASS_CONDITIONAL",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "contract_sha256": digest(CONTRACT),
        "checks": rows,
        "checks_passed": len(rows),
        "finding": "Hostile mutations removing the j-before-n order, D term, unchanged functional, or non-claim firewall are rejected while the baseline is accepted.",
        "non_claims": baseline["non_claims"],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_ordered_epsilon_bridge_hostile.py --check",
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    if not args.check:
        write_json(destination, payload)
    elif not destination.is_file() or json.loads(destination.read_text(encoding="utf-8")) != payload:
        raise SystemExit("PAH-OMC-020 hostile replay mismatch")
    print(f"PAH-OMC-020 ORDERED-EPSILON HOSTILE: PASS {len(rows)}/{len(rows)}; verdict=PASS_CONDITIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
