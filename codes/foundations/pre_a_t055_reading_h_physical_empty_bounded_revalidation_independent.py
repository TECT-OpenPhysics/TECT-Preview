#!/usr/bin/env python3
"""Non-importing independent audit for the R-427 blocked contract."""

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
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}/independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("manifest identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-427", "EXP-001272", False], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-427", "EXP-001272", False], "provenance")
    check("R-420 identity lock", manifest["revalidation"]["base_result_id"] == "R-420" and manifest["revalidation"]["same_contract_identity"] is True and manifest["revalidation"]["same_required_field_count"] == 15, manifest["revalidation"], "R-420/15/identity-locked", "provenance")

    source_hashes: dict[str, str] = {}
    texts: dict[str, str] = {}
    for item in manifest["authority_inputs"]:
        path = ROOT / item["path"]
        check(f"authority exists {item['id']}", path.is_file(), str(path), True, "authority")
        actual = digest(path)
        source_hashes[item["id"]] = actual
        check(f"authority hash {item['id']}", actual == item["sha256"], actual, item["sha256"], "authority")
        texts[item["id"]] = path.read_text(encoding="utf-8")

    check("R-169 is not full physical owner", "physical empty space" in texts["R169-V1.4-MANIFEST"] and "not the A1 side-16 three-component F_decl" in texts["R169-V1.4-MANIFEST"], True, True, "authority")
    check("R-170 retains open physical-empty gate", "PA-CP1-ST8-Q3LOCK-PHYSICAL-EMPTY-SPACE-REFERENCE" in texts["R170-MANIFEST"], True, True, "authority")
    check("R-170 does not import G-star versus E", "F_total[Q] > F_total[G_*]" in texts["R170-CERTIFICATE"] and "physical-empty" in texts["R170-CERTIFICATE"].lower(), True, True, "authority")
    check("EXP-000790 supplies only a future contract", "physical_empty_reference_contract" in texts["EXP790-MANIFEST"] and '"physical_empty_space_reference": false' in texts["EXP790-MANIFEST"], True, True, "authority")
    check("R-418 still forbids zero alias", "FORBIDDEN" in texts["R418-MANIFEST"] and "BLOCKED_NOT_INSTANTIATED" in texts["R418-MANIFEST"], True, True, "authority")
    check("R-420 base remains blocked", "R-420 v1.0" in texts["R420-MANIFEST"] and "BLOCKED_NOT_INSTANTIATED" in texts["R420-MANIFEST"], True, True, "authority")

    owner = manifest["owner_contract"]
    field_names = owner["required_fixed_fields"]
    check("fifteen-field matrix is complete", len(field_names) == 15 and set(field_names) == set(owner["field_matrix"]), len(field_names), 15, "contract")
    check("orientation is G-star minus E", owner["comparison_orientation"] == "F_total[G_*] - F_total[E]", owner["comparison_orientation"], "F_total[G_*] - F_total[E]", "contract")
    check("current owner remains noncommon", owner["field_status"] == "NOT_FIXED_IN_ONE_COMMON_OWNER", owner["field_status"], "NOT_FIXED_IN_ONE_COMMON_OWNER", "contract")
    check("finite evaluation remains disabled", owner["finite_evaluation_allowed"] is False, owner["finite_evaluation_allowed"], False, "contract")
    check("at least one field value is missing", any(entry["status"] == "MISSING" for entry in owner["field_matrix"].values()), True, True, "contract")
    branch = manifest["physical_empty_branch_E"]
    check("E is a preregistered slot only", branch["preregistered_slot"] is True and branch["admitted"] is False, [branch["preregistered_slot"], branch["admitted"]], [True, False], "E-preregistration")
    check("E admission is blocked", branch["admission_status"] == "BLOCKED_NOT_INSTANTIATED" and not branch["supplied_fields"], [branch["admission_status"], branch["supplied_fields"]], ["BLOCKED_NOT_INSTANTIATED", []], "E-preregistration")
    check("zero/P1 aliases are rejected", [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]] == ["FORBIDDEN", "NOT_ACCEPTED"], [branch["zero_reference_identification"], branch["p1_zero_reference_alias"]], ["FORBIDDEN", "NOT_ACCEPTED"], "E-preregistration")

    verdicts = manifest["verdicts"]
    names = ("sign", "reading_h_stationarity", "symmetry_projected_transverse_stability")
    statuses = [verdicts[name]["status"] for name in names]
    check("all three verdicts are blocked", statuses == ["BLOCKED_NOT_EVALUATED"] * 3, statuses, ["BLOCKED_NOT_EVALUATED"] * 3, "verdict")
    check("top-level status is blocked", manifest["status"] == "BLOCKED", manifest["status"], "BLOCKED", "verdict")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-t055-physical-empty-bounded-revalidation-run/1.0",
        "run_kind": "independent",
        "audit_id": manifest["test_card_id"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["card_id"],
        "verdict": "BLOCKED",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "source_hashes": source_hashes,
        "derived": {
            "contract_identity": manifest["revalidation"]["same_contract_identity"],
            "owner_contract_status": owner["field_status"],
            "physical_empty_slot": branch["admission_status"],
            "required_field_count": len(field_names),
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
    if args.self_test:
        assert payload["verdict"] == "BLOCKED"
        assert payload["derived"]["numeric_evaluation"] is False
        print(f"R-427 INDEPENDENT SELFTEST: PASS ({len(assertions)} reconstructed contract assertions; no numeric evaluation)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    write_json(output, payload)
    print(f"R-427 INDEPENDENT BLOCKED {len(assertions)}/{len(assertions)} assertions; no numeric evaluation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
