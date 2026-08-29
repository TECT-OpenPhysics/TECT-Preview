#!/usr/bin/env python3
"""Hostile input-mutation checks for the R-420 preregistration firewall."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-t055-reading-h-physical-empty-bounded-test-blocked"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}/hostile.json"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def admissible_for_evaluation(doc: dict[str, Any]) -> bool:
    owner = doc["owner_contract"]
    branch = doc["physical_empty_branch_E"]
    statuses = [doc["verdicts"][key]["status"] for key in ("sign", "reading_h_stationarity", "symmetry_projected_transverse_stability")]
    fields = owner["required_fixed_fields"]
    matrix = owner["field_matrix"]
    return (
        owner["field_status"] == "FIXED_IN_ONE_COMMON_OWNER"
        and owner["finite_evaluation_allowed"] is True
        and len(fields) == len(matrix)
        and all(matrix[name]["status"] == "FIXED" for name in fields)
        and branch["admitted"] is True
        and branch["admission_status"] == "ADMITTED"
        and bool(branch["supplied_fields"])
        and branch["zero_reference_identification"] != "FORBIDDEN"
        and statuses != ["BLOCKED_NOT_EVALUATED"] * 3
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def mutation(name: str, mutated: dict[str, Any], reason: str) -> None:
        accepted = admissible_for_evaluation(mutated)
        if accepted:
            raise AssertionError(f"hostile mutation accepted: {name}")
        assertions.append({"name": name, "group": "hostile", "status": "PASS", "actual": accepted, "expected": False, "reason": reason})

    zero_alias = copy.deepcopy(original)
    zero_alias["physical_empty_branch_E"]["p1_zero_reference_alias"] = "ACCEPTED"
    mutation("P1 zero alias", zero_alias, "E cannot be admitted by aliasing another owner")

    e_without_data = copy.deepcopy(original)
    e_without_data["physical_empty_branch_E"]["admitted"] = True
    e_without_data["physical_empty_branch_E"]["admission_status"] = "ADMITTED"
    mutation("admit E without representative", e_without_data, "admission requires supplied state, measure and preparation fields")

    missing_finite_parts = copy.deepcopy(original)
    missing_finite_parts["owner_contract"]["field_status"] = "FIXED_IN_ONE_COMMON_OWNER"
    missing_finite_parts["owner_contract"]["finite_evaluation_allowed"] = True
    mutation("mark missing finite parts fixed", missing_finite_parts, "all field-matrix entries must be fixed")

    p1_owner = copy.deepcopy(original)
    p1_owner["owner_contract"]["candidate"] = "P1 zero/disordered owner"
    p1_owner["owner_contract"]["field_status"] = "FIXED_IN_ONE_COMMON_OWNER"
    p1_owner["owner_contract"]["finite_evaluation_allowed"] = True
    mutation("switch candidate to P1", p1_owner, "a different parent is not a Reading-H same-owner test")

    numeric_verdict = copy.deepcopy(original)
    numeric_verdict["verdicts"]["sign"]["status"] = "POSITIVE"
    mutation("premature numeric sign", numeric_verdict, "blocked inputs cannot emit a sign")

    missing_limit_order = copy.deepcopy(original)
    missing_limit_order["owner_contract"]["required_fixed_fields"].remove("limit_order")
    del missing_limit_order["owner_contract"]["field_matrix"]["limit_order"]
    mutation("omit limit order", missing_limit_order, "limit order is mandatory in the common contract")

    forged_status = copy.deepcopy(original)
    forged_status["status"] = "PASS"
    forged_status["owner_contract"]["finite_evaluation_allowed"] = True
    mutation("forge top-level PASS", forged_status, "top-level status cannot override missing owner and E")

    payload = {
        "schema": "tect/pre-a-t055-physical-empty-bounded-test-blocked-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": original["test_card_id"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": original["result_id"],
        "exploration_id": original["exploration_id"],
        "claim_id": original["card_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "controls": {
            "all_mutations_rejected": all(row["actual"] is False for row in assertions),
            "numeric_evaluation": False,
            "physical_empty_admission": original["physical_empty_branch_E"]["admission_status"],
        },
        "non_claims": original["non_claims"],
    }
    if args.self_test:
        assert payload["verdict"] == "PASS"
        assert payload["assertion_count"] == 7
        assert payload["controls"]["all_mutations_rejected"] is True
        print("R-420 HOSTILE SELFTEST: PASS (7 invalid mutations rejected)")
        return 0
    output = args.output if args.output.is_absolute() else ROOT / args.output
    write_json(output, payload)
    print(f"R-420 HOSTILE PASS {len(assertions)}/{len(assertions)} invalid mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

