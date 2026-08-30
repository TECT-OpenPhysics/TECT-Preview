#!/usr/bin/env python3
"""Independent field-order control for the R-434 blocked owner audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-t055-reading-h-physical-empty-bounded-test-owner-refresh-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-pre-a-t055-reading-h-physical-empty-bounded-test-owner-refresh/independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(fd)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    owner = manifest["owner_contract"]
    branch = manifest["physical_empty_branch_E"]
    verdicts = manifest["verdicts"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest["result_id"], manifest["exploration_id"], manifest["status"], manifest["claim_bearing"]) == ("R-434", "EXP-001279", "BLOCKED", False), [manifest["result_id"], manifest["exploration_id"], manifest["status"], manifest["claim_bearing"]], ["R-434", "EXP-001279", "BLOCKED", False], "provenance")
    fields = list(reversed(owner["required_fixed_fields"]))
    check("reversed field enumeration", len(fields) == 15 and len(set(fields)) == 15 and set(fields) == set(owner["field_matrix"]), len(fields), 15, "contract")
    check("orientation immutable", owner["comparison_orientation"] == "F_total[G_*] - F_total[E]", owner["comparison_orientation"], "F_total[G_*] - F_total[E]", "contract")
    check("owner unavailable", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    check("E slot", branch["preregistered_slot"] is True and branch["admitted"] is False and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["preregistered_slot"], branch["admitted"], branch["admission_status"]], [True, False, "BLOCKED_NOT_INSTANTIATED"], "E")
    check("E is not zero", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E")
    check("all three statuses", all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in verdicts.values()), {key: item["status"] for key, item in verdicts.items()}, "BLOCKED_NOT_EVALUATED", "verdict")
    check("sign reason", "NO_COMMON_FINITE_REGULATOR_OWNER" in verdicts["sign"]["reason_codes"] and "E_NOT_ADMITTED" in verdicts["sign"]["reason_codes"], verdicts["sign"]["reason_codes"], "owner and E blockers", "verdict")
    check("stationarity reason", "NO_FULL_REGULATED_TANGENT" in verdicts["reading_h_stationarity"]["reason_codes"], verdicts["reading_h_stationarity"]["reason_codes"], "missing full tangent", "verdict")
    check("stability reason", "NO_TRANSVERSE_PROJECTOR" in verdicts["symmetry_projected_transverse_stability"]["reason_codes"], verdicts["symmetry_projected_transverse_stability"]["reason_codes"], "missing projector", "verdict")
    check("no numeric path", owner["finite_evaluation_allowed"] is False and branch["supplied_fields"] == [], [owner["finite_evaluation_allowed"], branch["supplied_fields"]], [False, []], "stop")
    expected_hashes = {item["id"]: item["sha256"] for item in manifest["authority_inputs"]}
    actual_hashes = {item["id"]: sha256(ROOT / item["path"]) for item in manifest["authority_inputs"]}
    check("authority hashes", actual_hashes == expected_hashes, actual_hashes, expected_hashes, "authority")
    check("no promotion", manifest["tier"] == "T0" and manifest["claim_bearing"] is False, [manifest["tier"], manifest["claim_bearing"]], ["T0", False], "scope")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r434-independent/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-434",
        "exploration_id": "EXP-001279",
        "claim_id": manifest["card_id"],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_BLOCKED_INPUT_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"reversed_required_fields": fields, "comparison": owner["comparison_orientation"], "sign": verdicts["sign"]["status"], "reading_h_stationarity": verdicts["reading_h_stationarity"]["status"], "symmetry_projected_transverse_stability": verdicts["symmetry_projected_transverse_stability"]["status"], "E_preregistered": True, "E_admitted": False},
        "scope": {"independent_input_audit": True, "numeric_evaluation": False, "claim_bearing": False, "physical_promotion": False},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED INDEPENDENT FIELD-ORDER CONTROL; PHYSICAL QUANTITIES BLOCKED_NOT_EVALUATED",
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-434 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    payload = run(output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_BLOCKED_INPUT_CONTROL"
        print("R-434 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
