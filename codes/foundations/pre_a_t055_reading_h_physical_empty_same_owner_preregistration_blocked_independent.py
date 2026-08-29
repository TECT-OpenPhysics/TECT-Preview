#!/usr/bin/env python3
"""Non-importing independent R-418 owner-contract audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-t055-reading-h-physical-empty-same-owner-preregistration-blocked"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
SCRIPT = Path(__file__).resolve()
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}/independent.json"


def digest(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "identity", manifest.get("result_id") == "R-418" and manifest.get("exploration_id") == "EXP-001263", [manifest.get("result_id"), manifest.get("exploration_id")], ["R-418", "EXP-001263"], "provenance")
    check(rows, "claim-bearing firewall", manifest.get("claim_bearing") is False and manifest.get("status") == "BLOCKED", [manifest.get("claim_bearing"), manifest.get("status")], [False, "BLOCKED"], "provenance")
    expected_hashes: dict[str, str] = {}
    text_by_id: dict[str, str] = {}
    for item in manifest["authority_inputs"]:
        path = ROOT / item["path"]
        value = digest(path)
        expected_hashes[item["id"]] = value
        text_by_id[item["id"]] = path.read_text(encoding="utf-8")
        check(rows, f"hash {item['id']}", value == item["sha256"], value, item["sha256"], "authority")
    checks = [
        ("R169 sign boundary", "No sign for F_RH[G_*]-F_empty" in text_by_id["R169-V1.3-MANIFEST"]),
        ("R169 owner meaning", "covariance owner" in text_by_id["R169-V1.3-MANIFEST"]),
        ("B1 finite theorem", "F[Q]-F[G_*]" in text_by_id["B1-READING-H-CFULL-REFEREE"]),
        ("R170 no physical volume", "No physical spatial volume" in text_by_id["R170-APPLICABILITY-CERTIFICATE"]),
        ("R170 same-parent route", "same-parent `G_*`-versus-empty theorem" in text_by_id["R170-APPLICABILITY-CERTIFICATE"]),
        ("A1 mismatch", "EXTERNAL-SOURCE-AUDIT-FAIL" in text_by_id["A1-P1-FUNCTIONAL-MANIFEST"] and "A1-PFR-VARIATIONAL-MISMATCH" in text_by_id["A1-P1-FUNCTIONAL-MANIFEST"]),
        ("P1 map absent", "registered_source_object" in text_by_id["R169-V1.1-P1-MANIFEST"] and "missing_fields" in text_by_id["R169-V1.1-P1-MANIFEST"] and "Q/G_* to Psi" in text_by_id["R169-V1.1-P1-MANIFEST"])
    ]
    for name, condition in checks:
        check(rows, name, condition, True, True, "authority")
    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    check(rows, "owner not fixed", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    check(rows, "E preregistration blocked", branch["preregistered_slot"] is True and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["preregistered_slot"], branch["admission_status"]], [True, "BLOCKED_NOT_INSTANTIATED"], "contract")
    check(rows, "zero alias refused", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "contract")
    verdict_statuses = {name: item["status"] for name, item in manifest["verdicts"].items()}
    check(rows, "three blocked statuses", set(verdict_statuses.values()) == {"BLOCKED_NOT_EVALUATED"} and len(verdict_statuses) == 3, verdict_statuses, "three blocked tests", "verdict")
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-blocked-run/1.0",
        "run_kind": "independent",
        "audit_id": "T055-PHYSICAL-EMPTY-SAME-OWNER-PREREGISTRATION-BLOCKED",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-418",
        "exploration_id": "EXP-001263",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "BLOCKED",
        "assertion_count": len(rows),
        "assertions": rows,
        "source_hashes": expected_hashes,
        "derived": {
            "physical_empty_slot": branch["admission_status"],
            "owner_contract_status": owner["field_status"],
            "required_field_count": len(owner["required_fixed_fields"]),
            "verdict_statuses": verdict_statuses,
            "numeric_evaluation": False,
            "blocker_count": len(manifest["blockers"])
        },
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "blockers": manifest["blockers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"]
    }
    if args.self_test:
        assert payload["verdict"] == "BLOCKED"
        assert payload["derived"]["numeric_evaluation"] is False
        print("R-418 INDEPENDENT SELFTEST: PASS (non-importing authority and blocker reconstruction)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    write_json(output, payload)
    print(f"R-418 INDEPENDENT BLOCKED {len(rows)}/{len(rows)} assertions; no numeric comparison evaluated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
