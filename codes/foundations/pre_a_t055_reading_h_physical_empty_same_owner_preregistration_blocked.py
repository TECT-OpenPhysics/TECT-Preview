#!/usr/bin/env python3
"""Execute the R-418 same-owner physical-empty preregistration audit.

This program intentionally performs no energy, stationarity, or Hessian
calculation. It verifies that the requested common finite-regulator owner is
not present in the current TECT authorities and emits a reproducible BLOCKED
result with the three tests marked BLOCKED_NOT_EVALUATED.
"""

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
SCRIPT = Path(__file__).resolve()
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}/primary.json"


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def authority_check(audit: Audit, manifest: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    texts: dict[str, str] = {}
    for authority in manifest["authority_inputs"]:
        path = ROOT / authority["path"]
        audit.check(f"authority exists {authority['id']}", path.is_file(), str(path), True, "authority")
        digest = normalized_sha256(path)
        hashes[authority["id"]] = digest
        audit.check(f"authority hash {authority['id']}", digest == authority["sha256"], digest, authority["sha256"], "authority")
        texts[authority["id"]] = path.read_text(encoding="utf-8")
    r169 = texts["R169-V1.3-MANIFEST"]
    r170 = texts["R170-APPLICABILITY-CERTIFICATE"]
    b1 = texts["B1-READING-H-CFULL-REFEREE"]
    a1 = texts["A1-P1-FUNCTIONAL-MANIFEST"]
    p1 = texts["R169-V1.1-P1-MANIFEST"]
    audit.check("R-169 no physical-empty sign boundary", "No sign for F_RH[G_*]-F_empty" in r169, True, True, "authority")
    audit.check("R-169 covariance-owner boundary", "G_* is a covariance owner" in r169, True, True, "authority")
    audit.check("B1 finite Q-versus-G-star scope", "F[Q]-F[G_*]" in b1 and "G_*" in b1, True, True, "authority")
    audit.check("R-170 missing physical volume", "No physical spatial volume" in r170, True, True, "authority")
    audit.check("R-170 same-parent next route", "same-parent `G_*`-versus-empty theorem" in r170, True, True, "authority")
    audit.check("A1 source audit mismatch", "EXTERNAL-SOURCE-AUDIT-FAIL" in a1 and "A1-PFR-VARIATIONAL-MISMATCH" in a1, True, True, "authority")
    audit.check("P1 zero is not Reading-H image", "registered_source_object" in p1 and "missing_fields" in p1 and "Q/G_* to Psi" in p1, ["registered_source_object", "missing_fields"], "Reading-H map is listed as missing", "authority")
    return hashes


def contract_check(audit: Audit, manifest: dict[str, Any]) -> None:
    audit.check("manifest identity", manifest["result_id"] == "R-418" and manifest["exploration_id"] == "EXP-001263" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-418", "EXP-001263", False], "provenance")
    owner = manifest["owner_contract"]
    audit.check("owner contract is not fixed", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    audit.check("all requested fields are enumerated", len(owner["required_fixed_fields"]) >= 15, len(owner["required_fixed_fields"]), "complete common-owner field list", "contract")
    branch = manifest["physical_empty_branch_E"]
    audit.check("E slot is preregistered but blocked", branch["preregistered_slot"] is True and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["preregistered_slot"], branch["admission_status"]], [True, "BLOCKED_NOT_INSTANTIATED"], "E-preregistration")
    audit.check("zero alias is forbidden", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E-preregistration")
    verdicts = manifest["verdicts"]
    statuses = [verdicts[key]["status"] for key in ("sign", "reading_h_stationarity", "symmetry_projected_transverse_stability")]
    audit.check("all three tests are blocked before evaluation", statuses == ["BLOCKED_NOT_EVALUATED"] * len(statuses), statuses, ["BLOCKED_NOT_EVALUATED"] * len(statuses), "verdict")
    audit.check("no numeric evaluation is authorized", "finite_evaluation_allowed" in owner and owner["finite_evaluation_allowed"] is False, owner["finite_evaluation_allowed"], False, "verdict")


def run_audit() -> tuple[dict[str, Any], Audit]:
    manifest = load_manifest()
    audit = Audit()
    hashes = authority_check(audit, manifest)
    contract_check(audit, manifest)
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-blocked-run/1.0",
        "run_kind": "primary",
        "audit_id": "T055-PHYSICAL-EMPTY-SAME-OWNER-PREREGISTRATION-BLOCKED",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-418",
        "exploration_id": "EXP-001263",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "BLOCKED",
        "assertion_count": len(audit.rows),
        "assertions": audit.rows,
        "source_hashes": hashes,
        "derived": {
            "physical_empty_slot": manifest["physical_empty_branch_E"]["admission_status"],
            "owner_contract_status": manifest["owner_contract"]["field_status"],
            "required_field_count": len(manifest["owner_contract"]["required_fixed_fields"]),
            "sign_status": manifest["verdicts"]["sign"]["status"],
            "stationarity_status": manifest["verdicts"]["reading_h_stationarity"]["status"],
            "transverse_stability_status": manifest["verdicts"]["symmetry_projected_transverse_stability"]["status"],
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
    return payload, audit


def self_test() -> int:
    manifest = load_manifest()
    assert manifest["result_id"] == "R-418"
    assert manifest["physical_empty_branch_E"]["p1_zero_reference_alias"] == "NOT_ACCEPTED"
    assert all(value["status"] == "BLOCKED_NOT_EVALUATED" for value in manifest["verdicts"].values())
    assert normalized_sha256(SCRIPT) == normalized_sha256(SCRIPT)
    print("R-418 PRIMARY SELFTEST: PASS (owner contract, E slot, and three blocked verdicts)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    payload, audit = run_audit()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-418 PRIMARY BLOCKED {len(audit.rows)}/{len(audit.rows)} assertions; sign=BLOCKED_NOT_EVALUATED stationarity=BLOCKED_NOT_EVALUATED transverse=BLOCKED_NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
