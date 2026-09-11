#!/usr/bin/env python3
"""Reproduce the PAH-v2 definition-admission HOLD, not a finite proof.

Version: 0.1.0; first issued/version issued: 2026-09-11.
Inputs are the new v2 draft, its explicit approval and hash-pinned authorities.
No state/move enumeration, finite numerical experiment, owner search, or
semigroup calculation is performed. Mutation tests reject premature admission.
The JSON output is an executed provenance/scope audit only.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "strategy/pa-hyp/PAH-001-v2.json"
APPROVAL = ROOT / "strategy/owner-decisions/PAH-root-measure-v0.1-approval-20260911.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-definition-admission/result.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def checks_for(spec, approval):
    enum = spec["exact_move_enumerator"]
    missing = spec["missing_item"]
    return {
        "approved_A_preparation_recorded": approval["approval_received"]
        and approval["approved_document"]["option"] == "A",
        "approval_is_not_complete_model_or_proof": not approval["complete_model_approved"]
        and not approval["proof_approved"],
        "no_full_source_authority_claim": spec["source_authorized"] is False,
        "honest_partial_draft_status": spec["status"] == "DRAFT_PARTIAL_AWAITING_OWNER_STATE_CHOICE",
        "HOLD_not_PROVED": spec["verdict"] == "HOLD_FOR_EVIDENCE",
        "no_fabricated_exact_enumerator": enum["status"] == "NOT_INSTANTIATED"
        and enum["implementation_path"] is None and enum["implementation_sha256"] is None,
        "one_unselected_owner_contract": missing["id"] == "COUNTING_STATE_AND_TRANSFER_COORDINATE_CONTRACT"
        and missing["default_selected"] is False,
        "all_five_mathematical_tests_unrun": all(
            spec["verification_disposition"][key] == "NOT_RUN_UNFIXED_STATE_AND_ENUMERATOR"
            for key in ("inverse_validity", "L1_equals_zero", "Gibbs_detailed_balance",
                        "projection_commutation", "B_adjoint_B_equals_minus_L")
        ),
    }


def mutation_tests(spec, approval):
    # Tooling test inputs, not mathematical state fixtures or derived constants.
    tests = {}
    mutations = (
        ("invent_authority", "source_authorized", True),
        ("invent_theorem", "verdict", "PROVED"),
        ("hide_partial_status", "status", "COMPLETE_MODEL"),
    )
    for name, key, value in mutations:
        bad = copy.deepcopy(spec)
        bad[key] = value
        tests[name] = not all(checks_for(bad, approval).values())
    bad = copy.deepcopy(spec)
    bad["exact_move_enumerator"]["implementation_path"] = "unapproved-enumerator.py"
    tests["invent_enumerator"] = not all(checks_for(bad, approval).values())
    bad = copy.deepcopy(spec)
    bad["missing_item"]["default_selected"] = True
    tests["silently_select_state_labels"] = not all(checks_for(bad, approval).values())
    bad = copy.deepcopy(approval)
    bad["complete_model_approved"] = True
    tests["expand_owner_authorization"] = not all(checks_for(spec, bad).values())
    assert tests and all(tests.values()), "A premature-admission mutation survived"
    return tests


def audit():
    spec, approval = read(SPEC), read(APPROVAL)
    checks = checks_for(spec, approval)
    for path, expected in spec["source_pins"].items():
        checks["source_hash:" + path] = sha(ROOT / path) == expected
    ref = spec["missing_item"]["reference_only_example"]
    checks["reference_only_successor_hash"] = sha(ROOT / ref["path"]) == ref["sha256"]
    parent = read(ROOT / spec["immutable_parent"]["path"])
    checks["parent_field_locators_resolve"] = all(
        key in parent for key in ("microscopic_degrees_of_freedom", "functional_or_action",
                                  "dynamics", "finite_regulator", "ordered_limits")
    )
    checks["approved_document_hash"] = sha(ROOT / approval["approved_document"]["path"]) == approval["approved_document"]["sha256"]
    assert all(checks.values()), "Definition-admission check failed"
    mutants = mutation_tests(spec, approval)
    return {
        "schema": "tect/pah-v2-definition-admission-run/1.0",
        "verdict": spec["verdict"],
        "evidence_level": "EXECUTED_DOCUMENT_AND_PROVENANCE_AUDIT_ONLY",
        "spec_sha256": sha(SPEC),
        "approval_sha256": sha(APPROVAL),
        "script_sha256": sha(Path(__file__)),
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "hostile_scope": "Document-admission flag mutations, not a hostile mathematical verifier.",
        "mutations_rejected": mutants,
        "mathematical_verification": spec["verification_disposition"],
        "missing_item": spec["missing_item"]["id"],
        "non_claims": spec["non_claims"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the existing JSON without writing")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    if args.check:
        assert read(args.output) == result, "Stored audit is stale"
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, ensure_ascii=True, sort_keys=True, indent=2)
            stream.write("\n")
    print(f"PAH-V2-DEFINITION-ADMISSION: HOLD_FOR_EVIDENCE; audit checks {result['checks_passed']}/{result['checks_total']}; mathematical tests NOT_RUN")


if __name__ == "__main__":
    main()
