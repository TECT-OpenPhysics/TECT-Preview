#!/usr/bin/env python3
"""Crosswalk the conditional A2 gradient flow against the R-192 owner slots."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a2-gradient-flow-r192-owner-crosswalk-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-08-23-a2-gradient-flow-r192-owner-crosswalk" / "primary.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authorities = {key: ROOT / record["path"] for key, record in manifest["source_authorities"].items()}
    expected_hashes = {key: record["sha256"] for key, record in manifest["source_authorities"].items()}
    actual_hashes = {key: digest(path) for key, path in authorities.items() if path.is_file()}
    rows: list[dict[str, Any]] = []
    check(rows, "source_hashes_match", actual_hashes == expected_hashes, actual_hashes, expected_hashes)

    a2_status = json.loads(authorities["a2_status"].read_text(encoding="utf-8"))
    a2_manifest = json.loads(authorities["a2_pinned_manifest"].read_text(encoding="utf-8"))
    r192 = json.loads(authorities["r192_manifest"].read_text(encoding="utf-8"))
    a2_text = (authorities["a2_status"].read_text(encoding="utf-8") + "\n" + authorities["a2_pinned_manifest"].read_text(encoding="utf-8")).lower()
    statement = str(a2_status.get("statement", "")).lower()
    scope = str(a2_status.get("scope", "")).lower()
    no_overclaim = str(a2_status.get("no_overclaim", "")).lower()
    required_absence = tuple(str(value).lower() for value in manifest["registered_crosswalk"]["expected_absence"])
    absence_flags = {token: token not in a2_text for token in required_absence}
    r192_inputs = r192["registered_inputs"]
    slot_audit = {entry["slot"]: entry for entry in r192_inputs["slot_audit"]}
    first_slot = r192_inputs["first_failure_slot"]

    check(rows, "a2_conditional_hypothesis", "a2-h3-canonical-production-functional" in scope, scope, "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL")
    check(rows, "a2_gradient_flow_present", "canonical gradient flow" in statement and "real hilbert space l2" in statement, statement, "conditional real-L2 gradient flow")
    check(rows, "a2_fixed_torus_scope", "fixed three-torus" in statement and "fixed periodic cell" in scope, [statement, scope], "fixed torus")
    check(rows, "a2_stochastic_heat_absent", "stochastic_heat" not in a2_text and "stochastic heat" not in a2_text, a2_text, "no stochastic heat owner")
    check(rows, "required_slots_absent", all(absence_flags.values()), absence_flags, "all required R-192 slots absent")
    check(rows, "r192_first_failure_slot", first_slot == manifest["registered_crosswalk"]["first_failure_slot"], first_slot, manifest["registered_crosswalk"]["first_failure_slot"])
    check(rows, "r192_slot_structural_only", slot_audit[first_slot]["mapped"] is False and slot_audit[first_slot]["status"] == "structural-only", slot_audit[first_slot], "mapped=false, structural-only")
    check(rows, "owner_incompatibility", manifest["registered_crosswalk"]["owner_compatible"] is False, manifest["registered_crosswalk"]["owner_compatible"], False)
    check(rows, "a2_not_physical_empty", "not a physical-vacuum theorem" in no_overclaim and "physical-vacuum" in scope, no_overclaim, "physical-vacuum excluded")
    check(rows, "a2_reference_functional_present", "f_p1" in json.dumps(a2_manifest).lower() and "eta_shell" in json.dumps(a2_manifest).lower(), a2_manifest.get("statement", ""), "F_P1/eta_shell authority")
    check(rows, "boundary_scope_tokens", all(token.lower() in manifest["boundary"].lower() for token in ("t0", "claim-nonbearing", "r-192", "a13", "physical-empty")), manifest["boundary"], "scope boundary")

    derived = {
        "a2_flow_kind": "conditional deterministic real-L2 gradient flow",
        "a2_stochastic_heat": False,
        "required_slot_absence": absence_flags,
        "r192_first_failure_slot": first_slot,
        "r192_first_failure_status": slot_audit[first_slot]["status"],
        "owner_compatible": False,
        "a2_hypothesis": "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    }
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a2-gradient-flow-r192-owner-crosswalk-primary/1.0",
        "claim_ids": manifest["claim_ids"],
        "script_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_authorities": actual_hashes,
        "derived": derived,
        "assertions": rows,
        "assertion_count": len(rows),
        "conclusion": "The conditional A2 deterministic gradient flow is a valid baseline for its fixed P1 functional, but it does not supply the stochastic/root-labelled R-192 owner; the first missing slot remains heat_root_incidence.",
        "honesty_boundary": ["conditional A2 baseline only", "no stochastic heat/root owner", "no R-192 completion", "no A13 closure", "no physical-empty or continuum conclusion"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A2 GRADIENT FLOW R192 CROSSWALK FAIL {len(rows)-len(failures)}/{len(rows)}")
        return 1
    print(f"A2 GRADIENT FLOW R192 CROSSWALK PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
