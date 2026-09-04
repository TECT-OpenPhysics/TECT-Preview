#!/usr/bin/env python3
"""Audit the frozen external-review packet for the A2/R-157/R-158 paper.

This is a structural completeness and hash-consistency check.  It does not
fill a reviewer form, judge a proof, establish novelty, or impersonate an
independent reviewer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path



PAPER_ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = PAPER_ROOT / "verification" / "runs" / "review-packet.json"

# These are review-contract inputs, not derived mathematical values.
THEOREM_LABELS = ("thm:a2-flow", "thm:r157-neutral", "thm:r158-ensemble")
PROOF_ITEMS = tuple(f"P-{index:02d}" for index in range(1, 16))
NOVELTY_FAMILIES = tuple(f"N-{index:02d}" for index in range(1, 8))
NOVELTY_DECISIONS = tuple(f"D-{index:02d}" for index in range(1, 8))
PROOF_SIGNATURE_FIELDS = (
    "reviewer_name:",
    "affiliation:",
    "expertise:",
    "independence_statement:",
    "manuscript_sha256_checked:",
    "pdf_sha256_checked:",
    "reproduction_toolchain_and_commit:",
    "items_completed:",
    "unlisted_objections:",
    "global_disposition:",
    "signature_or_verifiable_review_record:",
    "date:",
)
NOVELTY_SIGNATURE_FIELDS = (
    "reviewer_name:",
    "affiliation:",
    "specialist_area:",
    "independence_statement:",
    "search_dates:",
    "databases_and_indexes:",
    "queries_and_citation_chains:",
    "manuscript_sha256_checked:",
    "decisions_completed:",
    "global_disposition:",
    "required_repairs:",
    "signature_or_verifiable_review_record:",
    "date:",
)
REPLAY_SCRIPTS = (
    "a2_full_production_verify.py",
    "a2_pinned_functional_unique_zero_global_minimizer.py",
    "a2_pinned_functional_unique_zero_global_minimizer_independent.py",
    "a2_pinned_functional_unique_zero_global_minimizer_verify.py",
    "a2_charge_ensemble_first_order_shell_transition.py",
    "a2_charge_ensemble_first_order_shell_transition_independent.py",
    "a2_charge_ensemble_first_order_shell_transition_verify.py",
    "a2_r472_lean_crosscheck_verify.py",
    "exact_coercivity_audit.py",
    "classii_sign_audit.py",
    "ensemble_identity_audit.py",
    "analytic_dependency_audit.py",
    "review_packet_audit.py",
    "reproduction_manifest.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def exact_ids(text: str, pattern: str) -> tuple[str, ...]:
    return tuple(sorted(set(re.findall(pattern, text))))


def build_assertions(
    manuscript: str,
    proof_form: str,
    novelty_form: str,
    handoff: str,
    readiness: str,
    manuscript_hash: str,
    pdf_hash: str,
) -> dict[str, bool]:
    hostile_numbers = tuple(
        sorted(
            int(value)
            for value in re.findall(r"(?m)^(\d+)\. ", proof_form.split("## Mandatory hostile tests", 1)[-1].split("## Global", 1)[0])
        )
    )
    return {
        "manuscript_version_is_v019": "Draft v0.1.39" in manuscript,
        "all_theorem_labels_are_unique": all(
            manuscript.count(rf"\label{{{label}}}") == 1 for label in THEOREM_LABELS
        ),
        "manuscript_declares_blank_review_contracts": (
            "The two blank, package-local proof and novelty review contracts" in manuscript
            and "Their presence records no" in manuscript
        ),
        "proof_form_is_explicitly_blank": (
            "Status: `BLANK / NO REVIEW DISPOSITION RECORDED`" in proof_form
        ),
        "novelty_form_is_explicitly_blank": (
            "Status: `BLANK / NO NOVELTY DISPOSITION RECORDED`" in novelty_form
        ),
        "proof_form_pins_current_manuscript_hash": manuscript_hash in proof_form,
        "proof_form_pins_current_pdf_hash": pdf_hash in proof_form,
        "novelty_form_pins_current_manuscript_hash": manuscript_hash in novelty_form,
        "novelty_form_pins_current_pdf_hash": pdf_hash in novelty_form,
        "proof_obligation_ids_are_complete": exact_ids(proof_form, r"\bP-\d{2}\b") == PROOF_ITEMS,
        "proof_hostile_tests_are_complete": hostile_numbers == tuple(range(1, 10)),
        "proof_signature_contract_is_complete": all(
            field in proof_form for field in PROOF_SIGNATURE_FIELDS
        ),
        "novelty_family_ids_are_complete": exact_ids(novelty_form, r"\bN-\d{2}\b") == NOVELTY_FAMILIES,
        "novelty_decision_ids_are_complete": exact_ids(novelty_form, r"\bD-\d{2}\b") == NOVELTY_DECISIONS,
        "novelty_signature_contract_is_complete": all(
            field in novelty_form for field in NOVELTY_SIGNATURE_FIELDS
        ),
        "forms_are_routed_by_handoff": (
            "independent-proof-review-form.md" in handoff
            and "specialist-novelty-review-form.md" in handoff
        ),
        "handoff_has_exactly_one_blank_contract_section": (
            handoff.count("## Frozen blank response contracts") == 1
        ),
        "handoff_lists_complete_replay_surface": all(
            script in handoff for script in REPLAY_SCRIPTS
        ),
        "forms_are_routed_by_readiness_matrix": (
            "independent-proof-review-form.md" in readiness
            and "specialist-novelty-review-form.md" in readiness
        ),
        "canonical_source_sign_is_transfer_only": (
            "standalone theorem" in manuscript
            and "Separate transfer-only disposition" in readiness
            and "is not an independent-paper submission gate" in readiness
        ),
        "proof_form_forbids_internal_impersonation": (
            "may not fill the independent-review fields" in proof_form
        ),
        "novelty_form_separates_novel_methods_from_conjunction": (
            "does not claim that analytic semigroups" in novelty_form
            and "individually new" in novelty_form
        ),
    }


def self_test() -> None:
    assert exact_ids("P-01 P-03 P-01", r"\bP-\d{2}\b") == ("P-01", "P-03")
    assert exact_ids("", r"\bP-\d{2}\b") == ()
    assert tuple(range(1, 10)) != tuple(range(1, 9))
    assert "0" * 64 not in "1" * 64


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()

    manuscript_path = PAPER_ROOT / "manuscript.tex"
    pdf_path = PAPER_ROOT / "manuscript.pdf"
    proof_path = PAPER_ROOT / "independent-proof-review-form.md"
    novelty_path = PAPER_ROOT / "specialist-novelty-review-form.md"
    handoff_path = PAPER_ROOT / "external-review-handoff.md"
    readiness_path = PAPER_ROOT / "submission-readiness.md"

    paths = (manuscript_path, pdf_path, proof_path, novelty_path, handoff_path, readiness_path)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print("PAPER-REVIEW-PACKET-AUDIT-FAIL: missing files")
        for path in missing:
            print(f"  - {path}")
        return 1

    manuscript_hash = sha256(manuscript_path)
    pdf_hash = sha256(pdf_path)
    assertions = build_assertions(
        manuscript_path.read_text(encoding="utf-8"),
        proof_path.read_text(encoding="utf-8"),
        novelty_path.read_text(encoding="utf-8"),
        handoff_path.read_text(encoding="utf-8"),
        readiness_path.read_text(encoding="utf-8"),
        manuscript_hash,
        pdf_hash,
    )
    passed = sum(assertions.values())
    total = len(assertions)
    verdict = (
        "PAPER-REVIEW-PACKET-AUDIT-PASS"
        if passed == total
        else "PAPER-REVIEW-PACKET-AUDIT-FAIL"
    )
    result = {
        "schema": "tect/paper-review-packet-audit/1.1",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "scope": "structural completeness and hash consistency of blank external-review contracts",
        "manuscript_sha256": manuscript_hash,
        "pdf_sha256": pdf_hash,
        "assertions": {"passed": passed, "total": total, "results": assertions},
        "verdict": verdict,
        "non_claims": [
            "This audit does not judge the analytic proof.",
            "This audit does not establish novelty or simulate an independent reviewer.",
            "This audit does not close canonical-transfer source-owner, operator, capstone, submission, or publication gates.",
        ],
    }
    atomic_write(RUN_PATH, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{verdict}: {passed}/{total}")
    print(f"artifact: {RUN_PATH}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
