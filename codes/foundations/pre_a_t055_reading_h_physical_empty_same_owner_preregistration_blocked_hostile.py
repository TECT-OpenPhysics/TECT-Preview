#!/usr/bin/env python3
"""Hostile mutation suite for the R-418 preregistration blocker."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-t055-reading-h-physical-empty-same-owner-preregistration-blocked"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}/hostile.json"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def source_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in manifest["authority_inputs"]:
        raw = (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        value = hashlib.sha256(raw).hexdigest()
        if value != item["sha256"]:
            raise AssertionError(f"authority hash changed: {item['id']}")
        values[item["id"]] = value
    return values


def valid_contract(manifest: dict[str, Any]) -> bool:
    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    return (
        owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER"
        and owner["finite_evaluation_allowed"] is False
        and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED"
        and branch["zero_reference_identification"] == "FORBIDDEN"
        and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED"
        and all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in manifest["verdicts"].values())
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hashes = source_hashes(manifest)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("baseline contract valid", valid_contract(manifest), True, True, "baseline")
    zero_alias = copy.deepcopy(manifest)
    zero_alias["physical_empty_branch_E"]["p1_zero_reference_alias"] = "ACCEPTED"
    check("zero-reference alias mutation rejected", not valid_contract(zero_alias), False, True, "hostile")
    fixed_parts = copy.deepcopy(manifest)
    fixed_parts["owner_contract"]["field_status"] = "FIXED"
    check("finite-part/owner mutation rejected", not valid_contract(fixed_parts), False, True, "hostile")
    p1_owner = copy.deepcopy(manifest)
    p1_owner["owner_contract"]["requested_owner"] = "pinned P1 owner"
    p1_owner["owner_contract"]["finite_evaluation_allowed"] = True
    check("cross-owner mutation rejected", not valid_contract(p1_owner), False, True, "hostile")
    evaluated = copy.deepcopy(manifest)
    evaluated["verdicts"]["sign"]["status"] = "PASS"
    check("premature sign mutation rejected", not valid_contract(evaluated), False, True, "hostile")
    check("blocker list remains nonempty", len(manifest["blockers"]) > 0, len(manifest["blockers"]), "positive", "hostile")
    check("numeric comparison remains absent", manifest["owner_contract"]["finite_evaluation_allowed"] is False, False, False, "hostile")
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-blocked-run/1.0",
        "run_kind": "hostile",
        "audit_id": "T055-PHYSICAL-EMPTY-SAME-OWNER-PREREGISTRATION-BLOCKED",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-418",
        "exploration_id": "EXP-001263",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "source_hashes": hashes,
        "derived": {
            "baseline_verdict": "BLOCKED",
            "mutations_rejected": len(checks) - 2,
            "numeric_evaluation": False,
            "sign_status": manifest["verdicts"]["sign"]["status"],
            "stationarity_status": manifest["verdicts"]["reading_h_stationarity"]["status"],
            "transverse_stability_status": manifest["verdicts"]["symmetry_projected_transverse_stability"]["status"]
        },
        "boundary": "Hostile mutations validate the preregistration firewall only; they do not evaluate a physical energy or stability form."
    }
    if args.self_test:
        assert payload["verdict"] == "PASS"
        assert payload["derived"]["numeric_evaluation"] is False
        print("R-418 HOSTILE SELFTEST: PASS (zero alias, owner, evaluation, and verdict mutations rejected)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    write_json(output, payload)
    print(f"R-418 HOSTILE PASS {len(checks)}/{len(checks)} mutation assertions; baseline remains BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
