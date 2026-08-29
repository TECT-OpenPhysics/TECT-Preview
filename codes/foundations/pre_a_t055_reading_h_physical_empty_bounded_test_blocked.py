#!/usr/bin/env python3
"""Run the R-420 Reading-H physical-empty bounded preregistration test.

The lane intentionally evaluates no energy, stationarity residual, or
Hessian.  It verifies that one common finite-regulator owner and an admitted
physical-empty branch are prerequisites for those quantities, then emits a
typed BLOCKED result when the current authorities do not provide them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-t055-reading-h-physical-empty-bounded-test-blocked"
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

    r169 = texts["R169-V1.4-MANIFEST"]
    r170 = texts["R170-MANIFEST"]
    r170_certificate = texts["R170-CERTIFICATE"]
    exp790 = texts["EXP790-MANIFEST"]
    r418 = texts["R418-MANIFEST"]
    audit.check("R-169 latest owner boundary", "not the A1 side-16 three-component F_decl" in r169 and "physical empty space" in r169, True, True, "authority")
    audit.check("R-169 no physical-empty comparison", "or an energy relative to G_* or physical empty space" in r169, True, True, "authority")
    audit.check("R-170 physical-empty gate remains open", "PA-CP1-ST8-Q3LOCK-PHYSICAL-EMPTY-SPACE-REFERENCE" in r170, True, True, "authority")
    audit.check("R-170 B1 scope is Q versus G-star", "F_total[Q] > F_total[G_*]" in r170_certificate, True, True, "authority")
    audit.check("EXP-000790 future branch contract", "physical_empty_reference_contract" in exp790 and "minimum_contract" in exp790, True, True, "authority")
    audit.check("EXP-000790 does not identify physical empty", '"physical_empty_space_reference": false' in exp790, True, True, "authority")
    audit.check("prior R-418 did not alias E to zero", "zero_reference_identification" in r418 and "FORBIDDEN" in r418, True, True, "authority")
    return hashes


def contract_check(audit: Audit, manifest: dict[str, Any]) -> None:
    audit.check(
        "manifest identity",
        manifest["result_id"] == "R-420" and manifest["exploration_id"] == "EXP-001265" and manifest["claim_bearing"] is False,
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        ["R-420", "EXP-001265", False],
        "provenance",
    )
    owner = manifest["owner_contract"]
    fields = owner["required_fixed_fields"]
    matrix = owner["field_matrix"]
    audit.check("all requested contract fields are enumerated", len(fields) == 15 and set(fields) == set(matrix), len(fields), 15, "contract")
    audit.check("owner is not common/fixed", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    audit.check("at least one required owner field is missing", any(item["status"] == "MISSING" for item in matrix.values()), True, True, "contract")
    branch = manifest["physical_empty_branch_E"]
    audit.check("E slot is preregistered", branch["preregistered_slot"] is True, branch["preregistered_slot"], True, "E-preregistration")
    audit.check("E is not admitted", branch["admitted"] is False and branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED", [branch["admitted"], branch["admission_status"]], [False, "BLOCKED_NOT_INSTANTIATED"], "E-preregistration")
    audit.check("zero alias is forbidden", branch["zero_reference_identification"] == "FORBIDDEN" and branch["p1_zero_reference_alias"] == "NOT_ACCEPTED", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E-preregistration")
    verdicts = manifest["verdicts"]
    keys = ("sign", "reading_h_stationarity", "symmetry_projected_transverse_stability")
    statuses = [verdicts[key]["status"] for key in keys]
    audit.check("three requested tests are blocked", statuses == ["BLOCKED_NOT_EVALUATED"] * len(keys), statuses, ["BLOCKED_NOT_EVALUATED"] * len(keys), "verdict")
    audit.check("no numerical evaluation is authorized", owner["finite_evaluation_allowed"] is False, owner["finite_evaluation_allowed"], False, "verdict")
    audit.check("manifest status is BLOCKED", manifest["status"] == "BLOCKED", manifest["status"], "BLOCKED", "verdict")


def run_audit() -> tuple[dict[str, Any], Audit]:
    manifest = load_manifest()
    audit = Audit()
    hashes = authority_check(audit, manifest)
    contract_check(audit, manifest)
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-bounded-test-blocked-run/1.0",
        "run_kind": "primary",
        "audit_id": manifest["test_card_id"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["card_id"],
        "verdict": "BLOCKED",
        "assertion_count": len(audit.rows),
        "assertions": audit.rows,
        "source_hashes": hashes,
        "derived": {
            "owner_contract_status": manifest["owner_contract"]["field_status"],
            "physical_empty_slot": manifest["physical_empty_branch_E"]["admission_status"],
            "required_field_count": len(manifest["owner_contract"]["required_fixed_fields"]),
            "sign_status": manifest["verdicts"]["sign"]["status"],
            "stationarity_status": manifest["verdicts"]["reading_h_stationarity"]["status"],
            "transverse_stability_status": manifest["verdicts"]["symmetry_projected_transverse_stability"]["status"],
            "numeric_evaluation": False,
            "blocker_count": len(manifest["blockers"]),
        },
        "evidence_level": manifest["evidence_level"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "blockers": manifest["blockers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    return payload, audit


def self_test() -> int:
    manifest = load_manifest()
    assert manifest["result_id"] == "R-420"
    assert manifest["test_card_id"] == "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST"
    assert manifest["physical_empty_branch_E"]["admission_status"] == "BLOCKED_NOT_INSTANTIATED"
    assert all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in manifest["verdicts"].values())
    print("R-420 PRIMARY SELFTEST: PASS (common-owner contract, E preregistration, and three blocked verdicts)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    payload, audit = run_audit()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-420 PRIMARY BLOCKED {len(audit.rows)}/{len(audit.rows)} assertions; sign=BLOCKED_NOT_EVALUATED stationarity=BLOCKED_NOT_EVALUATED transverse=BLOCKED_NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
