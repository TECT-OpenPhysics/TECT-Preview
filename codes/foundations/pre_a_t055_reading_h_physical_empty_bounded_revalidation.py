#!/usr/bin/env python3
"""Execute the R-427 physical-empty same-owner revalidation.

This package deliberately evaluates no energy, stationarity residual, or
Hessian.  It revalidates the frozen R-420 contract and emits a typed blocker
when the current owner still has no common finite parent or admitted E.
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
SLUG = "pre-a-t055-reading-h-physical-empty-bounded-revalidation"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}/primary.json"


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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

    audit.check("R-169 owner boundary", "not the A1 side-16 three-component F_decl" in texts["R169-V1.4-MANIFEST"], True, True, "authority")
    audit.check("R-169 no physical-empty comparison", "physical empty space" in texts["R169-V1.4-MANIFEST"], True, True, "authority")
    audit.check("R-170 physical-empty gate open", "PA-CP1-ST8-Q3LOCK-PHYSICAL-EMPTY-SPACE-REFERENCE" in texts["R170-MANIFEST"], True, True, "authority")
    audit.check("R-170 remains Q versus G-star", "F_total[Q] > F_total[G_*]" in texts["R170-CERTIFICATE"], True, True, "authority")
    audit.check("EXP-000790 future contract only", "physical_empty_reference_contract" in texts["EXP790-MANIFEST"] and "minimum_contract" in texts["EXP790-MANIFEST"], True, True, "authority")
    audit.check("EXP-000790 does not admit E", '"physical_empty_space_reference": false' in texts["EXP790-MANIFEST"], True, True, "authority")
    audit.check("R-418 forbids zero alias", "zero_reference_identification" in texts["R418-MANIFEST"] and "FORBIDDEN" in texts["R418-MANIFEST"], True, True, "authority")
    audit.check("R-420 base is unchanged", "R-420 v1.0" in texts["R420-MANIFEST"] and "BLOCKED_NOT_INSTANTIATED" in texts["R420-MANIFEST"], True, True, "authority")
    return hashes


def contract_check(audit: Audit, manifest: dict[str, Any]) -> None:
    audit.check(
        "manifest identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-427", "EXP-001272", False],
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        ["R-427", "EXP-001272", False],
        "provenance",
    )
    revalidation = manifest["revalidation"]
    audit.check("R-420 contract identity lock", revalidation["base_result_id"] == "R-420" and revalidation["same_contract_identity"] is True and revalidation["value_status"] == "UNSUPPLIED_BY_CURRENT_OWNER", [revalidation["base_result_id"], revalidation["same_contract_identity"], revalidation["value_status"]], ["R-420", True, "UNSUPPLIED_BY_CURRENT_OWNER"], "provenance")
    owner = manifest["owner_contract"]
    fields = owner["required_fixed_fields"]
    matrix = owner["field_matrix"]
    audit.check("fifteen requested fields are enumerated", len(fields) == 15 and set(fields) == set(matrix), len(fields), 15, "contract")
    audit.check("comparison orientation is fixed", owner["comparison_orientation"] == "F_total[G_*] - F_total[E]", owner["comparison_orientation"], "F_total[G_*] - F_total[E]", "contract")
    audit.check("owner is not common/fixed", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER" and owner["finite_evaluation_allowed"] is False, [owner["field_status"], owner["finite_evaluation_allowed"]], ["NOT_FIXED_IN_ONE_COMMON_OWNER", False], "contract")
    audit.check("at least one owner value is missing", any(item["status"] == "MISSING" for item in matrix.values()), True, True, "contract")
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
    verdicts = manifest["verdicts"]
    payload = {
        "schema": "tect/pre-a-t055-physical-empty-bounded-revalidation-run/1.0",
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
            "contract_identity": manifest["revalidation"]["same_contract_identity"],
            "owner_contract_status": manifest["owner_contract"]["field_status"],
            "physical_empty_slot": manifest["physical_empty_branch_E"]["admission_status"],
            "required_field_count": len(manifest["owner_contract"]["required_fixed_fields"]),
            "sign_status": verdicts["sign"]["status"],
            "stationarity_status": verdicts["reading_h_stationarity"]["status"],
            "transverse_stability_status": verdicts["symmetry_projected_transverse_stability"]["status"],
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
    assert manifest["result_id"] == "R-427"
    assert manifest["test_card_id"] == "PA-T055-READING-H-PHYSICAL-EMPTY-BOUNDED-TEST-REVALIDATION"
    assert manifest["revalidation"]["same_contract_identity"] is True
    assert manifest["physical_empty_branch_E"]["admission_status"] == "BLOCKED_NOT_INSTANTIATED"
    assert all(item["status"] == "BLOCKED_NOT_EVALUATED" for item in manifest["verdicts"].values())
    print("R-427 PRIMARY SELFTEST: PASS (R-420 contract revalidation, E preregistration, and three blocked verdicts)")
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
    print(f"R-427 PRIMARY BLOCKED {len(audit.rows)}/{len(audit.rows)} assertions; sign=BLOCKED_NOT_EVALUATED stationarity=BLOCKED_NOT_EVALUATED transverse=BLOCKED_NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
