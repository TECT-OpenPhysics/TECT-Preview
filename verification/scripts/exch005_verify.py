#!/usr/bin/env python3
"""EXCH005 provenance and admission guards, not an experimental verifier."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = ROOT / "strategy/physical-candidates"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-exch005"
REQUIRED = ("full_text_assessed", "actual_conversion",
            "same_pre_readout_state_analyzer", "independent_relative_phase",
            "complete_instrument", "joint_error_control", "unused_outcome_packet")


def eligible(row):
    """Unknown is not false evidence, but neither is it admissible truth."""
    return all(row.get(key) is True for key in REQUIRED)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_eligible():
    """Pure-tooling self-test; these flags are synthetic, never observations."""
    assert eligible({key: True for key in REQUIRED})
    assert not eligible({})
    assert not eligible({key: None for key in REQUIRED})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    test_eligible()
    cp = PREFIX / "TECT-EXCH-005-contract-v1.json"
    ap = PREFIX / "TECT-EXCH-005-assessment-v1.json"
    contract = json.loads(cp.read_text(encoding="utf-8"))
    assessment = json.loads(ap.read_text(encoding="utf-8"))
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        if not checks[name]:
            raise AssertionError(name)

    check("contract_pin", digest(cp) == assessment["contract_sha256"])
    for path, expected in contract["preserved_hashes"].items():
        check("preserved:" + path, digest(ROOT / path) == expected)
    rows = assessment["protocols"]
    check("protocol_budget", len(rows) <= contract["budget"]["protocols_max"])
    check("source_budget", len(contract["sources"]) <= contract["budget"]["primary_documents_max"])
    check("slots_preserved", [r["id"] for r in rows] == [r["id"] for r in contract["protocol_slots"]])
    check("no_complete_packet_admitted", not any(eligible(r) for r in rows))
    check("source_vs_access_distinct", rows[0]["full_text_assessed"] is True
          and rows[1]["full_text_assessed"] is False
          and rows[1]["disposition"] == "NOT_ASSESSED_ACCESS_LIMITATION")
    check("no_global_no_go", not any(r["physical_impossibility_claim"] for r in rows))
    check("no_new_claim", not assessment["claim_bearing"]
          and assessment["new_result_id"] is None and assessment["new_negative_id"] is None)
    check("no_promotion", not assessment["active_gate_change"]
          and not assessment["physical_promotion"] and not assessment["new_state_or_model_adopted"])
    check("no_fitting_or_successor", contract["budget"]["physical_fits"] == 0
          and contract["budget"]["automatic_successor"] is False)
    check("scientific_hold", assessment["overall_verdict"] == "HOLD_FOR_EVIDENCE")
    check("no_unexecuted_success", assessment["measurement_reconstruction"].startswith("NOT_EXECUTED")
          and assessment["unused_response_validation"].startswith("NOT_EXECUTED"))
    # Labelled synthetic tooling oracles, never a physical state or instrument.
    oracle = {key: True for key in REQUIRED}
    check("fixture_complete_only", eligible(oracle))
    for key in REQUIRED:
        for replacement in (False, None, "TRUE"):
            invalid = copy.deepcopy(oracle)
            invalid[key] = replacement
            check("fixture_reject_" + key + "_" + str(replacement), not eligible(invalid))
    cache_status = "NOT_CHECKED_NO_CACHE_ARGUMENT"
    if args.source_cache:
        for source in contract["sources"]:
            if source["access"] == "FULL_PRIMARY_PDF":
                path = args.source_cache / source["cache_file"]
                check("source_bytes:" + source["id"], path.stat().st_size == source["bytes"])
                check("source_hash:" + source["id"], digest(path) == source["sha256"])
                check("source_pdf:" + source["id"], path.read_bytes().startswith(b"%PDF"))
        cache_status = "EXACT_FULL_PRIMARY_PDF_VERIFIED"
    review_path = RUN / "reviews.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    check("separate_source_and_hostile_review", review["independent"]["status"] == "SCOPED_PASS"
          and review["hostile"]["status"] == "SCOPED_PASS")
    note = ROOT / "claims/C6-SPACETIME-SIGNATURE/notes/pair-protocol-intake-261115-v1.0.tex.txt"
    expected_review_files = {p.relative_to(ROOT).as_posix() for p in (cp, ap, note, Path(__file__))}
    check("complete_review_file_set", set(review["reviewed_hashes"]) == expected_review_files)
    check("review_binds_actual_files", all(digest(ROOT / p) == h for p, h in review["reviewed_hashes"].items()))
    pdf = note.with_name(note.name.replace(".tex.txt", ".pdf"))
    check("synthesis_pdf", pdf.read_bytes().startswith(b"%PDF"))
    report = {"status": "PASS_AUDIT_COMPLETE_PHYSICAL_HOLD", "task_id": contract["task_id"],
              "checks": checks, "check_count": len(checks),
              "source_cache": cache_status, "physical_verdict": assessment["overall_verdict"],
              "eligible_packets": sum(eligible(r) for r in rows),
              "new_result_id": None, "Lean": assessment["lean"],
              "scope": "Provenance and fail-closed eligibility software. Does not prove experimental absence or a new theorem.",
              "evidence_hashes": {p.relative_to(ROOT).as_posix(): digest(p)
                                  for p in (cp, ap, note, pdf, review_path, Path(__file__))}}
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "integrated.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("EXCH005 VERIFY:", report["status"], len(checks), "tooling checks; physical HOLD")


if __name__ == "__main__":
    main()
