#!/usr/bin/env python3
"""Verify idea-bank metadata and PHY-001 provenance, not physical hypotheses.

python -X utf8 verification/scripts/research_idea_bank_verify.py
python -X utf8 verification/scripts/research_idea_bank_verify.py --source-cache internal/source-cache/tect-phy-001
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANK = ROOT / "strategy/research-idea-bank-v1.json"
ADMISSION = ROOT / "strategy/physical-candidates/TECT-PHY-001-admission-v1.json"
ASSESSMENT = ROOT / "strategy/physical-candidates/TECT-PHY-001-assessment-v1.json"
STATUSES = {"HYPOTHESIS_NOT_ADOPTED", "SPECULATIVE_NOT_EVIDENCE", "PRIORITY_INPUT_QUESTION", "REFERENCE_ONLY"}
FIELDS = {"id", "title", "origin", "status", "hypothesis", "support", "unproved", "test", "failure_boundary", "revisit_when", "references"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(bank: dict) -> list[str]:
    out = []
    required = {"schema", "id", "updated", "authority_level", "replaces_existing_methods", "policy", "ideas", "reviews"}
    if set(bank) != required:
        out.append("top-level fields incomplete")
    if bank.get("schema") != "tect/research-idea-bank/1.0" or bank.get("id") != "TECT-RESEARCH-IDEA-BANK-v1":
        out.append("bank identity invalid")
    if not isinstance(bank.get("updated"), str) or not bank.get("updated"):
        out.append("missing update date")
    if bank.get("authority_level") != "DISCUSSION_AND_HYPOTHESIS_ONLY":
        out.append("ideas promoted to authority")
    if bank.get("replaces_existing_methods") is not False:
        out.append("existing methods replaced")
    policy = bank.get("policy", {})
    policy_keys = {"purpose", "capture", "retrieval_triggers", "retrieval_budget", "retrieval_record", "promotion", "continuation", "proof_economy"}
    if not isinstance(policy, dict):
        return out + ["policy must be an object"]
    if set(policy) != policy_keys:
        out.append("policy fields incomplete")
    for key in policy_keys - {"retrieval_triggers", "retrieval_budget"}:
        if not isinstance(policy.get(key), str) or not policy[key].strip():
            out.append("empty policy field: " + key)
    triggers = policy.get("retrieval_triggers")
    if not isinstance(triggers, list) or not triggers or any(not isinstance(t, str) or not t.strip() for t in triggers):
        out.append("invalid retrieval triggers")
    budget = policy.get("retrieval_budget")
    # A governance tooling threshold, not a derived research number.
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 3:
        out.append("unbounded retrieval")
    seen = set()
    if not isinstance(bank.get("ideas"), list) or not isinstance(bank.get("reviews"), list):
        return out + ["ideas/reviews must be lists"]
    for idea in bank["ideas"]:
        if not isinstance(idea, dict):
            out.append("idea must be an object")
            continue
        if set(idea) != FIELDS:
            out.append("idea fields incomplete")
        if idea.get("id") in seen:
            out.append("duplicate idea id")
        seen.add(idea.get("id"))
        if idea.get("status") not in STATUSES:
            out.append("unsupported idea status")
        for key in FIELDS - {"references"}:
            if not isinstance(idea.get(key), str) or not idea[key].strip():
                out.append("empty idea field: " + key)
        if not isinstance(idea.get("references"), list) or not idea["references"] or any(not isinstance(r, str) or not r.strip() for r in idea["references"]):
            out.append("missing references")
    if not seen:
        out.append("empty idea bank")
    for review in bank["reviews"]:
        if not isinstance(review, dict):
            out.append("review must be an object")
            continue
        review_keys = {"date", "trigger", "selected", "disposition", "next_question", "reentry"}
        if set(review) != review_keys:
            out.append("review fields incomplete")
        for key in review_keys - {"selected"}:
            if not isinstance(review.get(key), str) or not review[key].strip():
                out.append("empty review field: " + key)
        selected = review.get("selected", [])
        if not isinstance(selected, list) or any(not isinstance(s, str) for s in selected) or len(selected) > 3 or len(selected) != len(set(selected)):
            out.append("invalid review selection")
        elif not set(selected) <= seen:
            out.append("unknown reviewed idea")
        if not review.get("disposition") or not review.get("reentry"):
            out.append("review lacks disposition or reentry")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    assessment = json.loads(ASSESSMENT.read_text(encoding="utf-8"))
    assert not errors(bank), errors(bank)
    assert sha(ADMISSION) == assessment["admission_sha256"]
    for path, expected in admission["preserved_hashes"].items():
        assert sha(ROOT / path) == expected, path
    assert len(assessment["sources"]) <= admission["budget"]["primary_papers_max"]
    assert sum(s["role"] == "SELECTED_REFERENCE_ONLY" for s in assessment["sources"]) <= admission["budget"]["deep_candidate_reviews_max"]
    assert assessment["claim_bearing"] is False and assessment["physical_promotion"] is False
    assert assessment["active_gate_change"] is False and assessment["new_result_id"] is None
    assert assessment["remaining_input"]["status"] == "NOT_SUPPLIED"
    mutations = [
        ("authority promotion", lambda b: b.update(authority_level="THEOREM")),
        ("method replacement", lambda b: b.update(replaces_existing_methods=True)),
        ("unlimited retrieval", lambda b: b["policy"].update(retrieval_budget=100)),
        ("duplicate identity", lambda b: b["ideas"].append(copy.deepcopy(b["ideas"][0]))),
        ("lost uncertainty", lambda b: b["ideas"][0].pop("unproved")),
        ("false proof status", lambda b: b["ideas"][0].update(status="PROVED")),
        ("unknown retrieval", lambda b: b["reviews"][0].update(selected=["UNKNOWN"])),
        ("lost trigger policy", lambda b: b["policy"].pop("retrieval_triggers")),
        ("lost retrieval record policy", lambda b: b["policy"].pop("retrieval_record")),
        ("lost review date", lambda b: b["reviews"][0].pop("date")),
        ("lost review trigger", lambda b: b["reviews"][0].pop("trigger")),
        ("null reference", lambda b: b["ideas"][0].update(references=[None])),
        ("lost bank identity", lambda b: b.pop("id")),
    ]
    rejected = []
    for name, mutate in mutations:
        broken = copy.deepcopy(bank)
        mutate(broken)
        assert errors(broken), name
        rejected.append(name)
    source_checks = []
    if args.source_cache:
        for source in assessment["sources"]:
            path = args.source_cache / source["cache_file"]
            assert path.read_bytes().startswith(b"%PDF"), path
            assert sha(path) == source["sha256"], path
            source_checks.append(source["id"])
    result = {
        "schema": "tect/idea-bank-verification/1.0", "status": "PASS",
        "scope": "Metadata, inherited-file hashes and optional downloaded-source hashes only; no physics or proof certification.",
        "inputs": {p.relative_to(ROOT).as_posix(): sha(p) for p in (BANK, ADMISSION, ASSESSMENT)},
        "ideas": len(bank["ideas"]), "hostile_mutations_rejected": rejected,
        "source_hashes_checked": source_checks, "source_retrieval": "RUN" if args.source_cache else "NOT_RUN",
        "Lean": "NOT_RUN: metadata/source applicability, not a new mathematical proof"
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
