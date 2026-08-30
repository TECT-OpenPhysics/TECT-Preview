#!/usr/bin/env python3
"""Fresh TECT-owner input audit for the Reading-H physical-empty test."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-t055-reading-h-physical-empty-bounded-test-owner-refresh-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre-a-t055-reading-h-physical-empty-bounded-test-owner-refresh/primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    verdicts = manifest["verdicts"]
    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]] == ["R-434", "EXP-001279", False, "BLOCKED"], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], ["R-434", "EXP-001279", False, "BLOCKED"], "provenance")
    check("test card identity", manifest["test_card_id"] == "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST-OWNER-REFRESH", manifest["test_card_id"], "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST-OWNER-REFRESH", "provenance")
    check("orientation fixed", owner["comparison_orientation"] == "F_total[G_*] - F_total[E]", owner["comparison_orientation"], "F_total[G_*] - F_total[E]", "contract")
    check("fifteen fields fixed", len(owner["required_fixed_fields"]) == 15 and set(owner["required_fixed_fields"]) == set(owner["field_matrix"]), len(owner["required_fixed_fields"]), 15, "contract")
    check("same-owner status", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["contract_identity_status"] == "LOCKED_TO_R427_AND_R420_VALUES_UNSUPPLIED" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["contract_identity_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", "LOCKED_TO_R427_AND_R420_VALUES_UNSUPPLIED", False], "contract")
    missing = [key for key, value in owner["field_matrix"].items() if value["status"] == "MISSING"]
    check("owner values remain missing", len(missing) >= 10, len(missing), ">=10 missing fields", "contract")
    check("E preregistration", branch["symbol"] == "E" and branch["preregistered_slot"] is True and branch["admitted"] is False and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["symbol"], branch["preregistered_slot"], branch["admitted"], branch["admission_status"]], ["E", True, False, "BLOCKED_NOT_INSTANTIATED"], "E")
    check("E fields absent", branch["supplied_fields"] == [] and len(branch["required_fields"]) == 6, [branch["supplied_fields"], len(branch["required_fields"])], [[], 6], "E")
    check("zero alias forbidden", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E")
    check("three verdicts blocked", all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in verdicts.values()), {key: item["status"] for key, item in verdicts.items()}, "all BLOCKED_NOT_EVALUATED", "verdict")
    check("no numeric evaluation", owner["finite_evaluation_allowed"] is False and branch["admitted"] is False, [owner["finite_evaluation_allowed"], branch["admitted"]], [False, False], "stop")
    hash_results: dict[str, str] = {}
    hash_ok = True
    for authority in manifest["authority_inputs"]:
        path = REPO / authority["path"]
        hash_results[authority["id"]] = sha256(path)
        hash_ok = hash_ok and hash_results[authority["id"]] == authority["sha256"]
    check("authority hashes", hash_ok, hash_results, "all pinned authority hashes", "authority")
    check("scope firewall", manifest["claim_bearing"] is False and all(not value for key, value in {"yang_mills": False, "mass_gap": False, "physical": False}.items()), "claim-nonbearing and no promotion", "no promotion", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r434-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-434",
        "exploration_id": "EXP-001279",
        "claim_id": manifest["card_id"],
        "run_kind": "primary",
        "verdict": "BLOCKED_NOT_EVALUATED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "comparison": "F_total[G_*] - F_total[E]",
            "sign": "BLOCKED_NOT_EVALUATED",
            "reading_h_stationarity": "BLOCKED_NOT_EVALUATED",
            "symmetry_projected_transverse_stability": "BLOCKED_NOT_EVALUATED",
            "E_preregistered": True,
            "E_admitted": False,
            "required_field_count": 15,
            "missing_owner_field_count": len(missing),
            "authority_hashes": hash_results,
        },
        "scope": {"owner_input_audit_executed": True, "E_preregistered": True, "E_admitted": False, "numeric_sign_evaluated": False, "stationarity_evaluated": False, "transverse_stability_evaluated": False, "claim_bearing": False, "yang_mills_promoted": False, "mass_gap_promoted": False},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-434 PRIMARY BLOCKED_NOT_EVALUATED {len(checks)}/{len(checks)}; E preregistered, not admitted", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(output)
    if args.self_test:
        assert payload["verdict"] == "BLOCKED_NOT_EVALUATED"
        assert payload["scope"]["E_admitted"] is False
        print("R-434 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
