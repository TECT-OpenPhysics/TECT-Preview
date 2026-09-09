#!/usr/bin/env python3
"""Audit objective coverage and publication boundaries for the Q3LOCK paper.

This is a provenance/readiness diagnostic. It checks that the current
manuscript, authority manifest, review packet and replay checkpoints cover the
requested seven-block result chain, while deliberately requiring the package
to remain T0, claim-nonbearing, unfrozen and PDF-deferred. It does not prove a
theorem, sign an A1--A23 row, or replace an external mathematics/literature
review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
MANUSCRIPT = PAPER / "manuscript.tex"
PROOF_AUDIT = PAPER / "proof-audit.md"
READINESS = PAPER / "submission-readiness.md"
HANDOFF = PAPER / "external-review-handoff.md"
PACKAGE = PAPER / "verification/package-manifest.json"
AUTHORITY_MANIFEST = ROOT / "strategy/q3lock-exp782-independent-result-manifest-260905.json"
MATRIX = ROOT / "strategy/q3lock-independent-review-matrix-260907.md"
LOCATOR_RESULT = RUNS / "2026-09-08-q3lock-review-locator-audit-source-review-v1/result.json"
FRESH_RESULT = RUNS / (
    "2026-09-08-q3lock-manuscript-fresh-audit-source-review-v1/result.json"
)
INTEGRATED_RESULT = RUNS / (
    "2026-09-08-q3lock-paper-integrated-replay-source-review-v1/result.json"
)
TEST = ROOT / "verification/tests/test_q3lock_completion_gate_audit.py"
STRATEGY_NOTE = ROOT / "strategy/q3lock-completion-gate-audit-260908.md"
LITERATURE_NOTE = ROOT / "strategy/q3lock-general-asymmetric-primary-boundary-260908.md"
LITERATURE_SUPPLEMENT_NOTE = ROOT / "strategy/q3lock-bounded-literature-supplement-260908.md"
KKK_BOUNDARY_NOTE = ROOT / "strategy/q3lock-kkk-vector-scalar-definition-boundary-260908.md"
LINEAGE_NOTE = ROOT / "strategy/q3lock-r497-claim-lineage-decision-260908.md"
KP_NOTE = ROOT / "strategy/q3lock-kp-envelope-formula-audit-260908.md"
KP_SCRIPT = ROOT / "verification/scripts/q3lock_kp_envelope_audit.py"
KP_TEST = ROOT / "verification/tests/test_q3lock_kp_envelope_audit.py"
KP_RESULT = RUNS / "2026-09-08-q3lock-kp-envelope-audit-v001/result.json"
EXPLORATIONS = ROOT / "explorations/log.jsonl"
DEFAULT_OUTPUT = RUNS / "2026-09-08-q3lock-completion-gate-audit-source-review-v1/result.json"

EXPECTED_ROWS = tuple(f"A{index}" for index in range(1, 24))
REQUIRED_LABELS = (
    "eq:hamiltonian",
    "eq:form-domain",
    "eq:open-pressure",
    "sec:dlr-specification",
    "sec:fkg-loop-passage",
    "eq:spatial-reflection-positive",
    "eq:infrared-bound",
    "eq:double-commutator",
    "eq:threshold-algebra",
    "eq:beta-star",
    "eq:cusp",
    "eq:parity-specification-intertwining",
    "eq:bounded-phase-witness",
    "thm:q3lock-composition",
)
REQUIRED_TOKENS = (
    r"\lambda>0",
    "r<0",
    "A_0>I_3",
    r"\beta>\beta_*",
)
REQUIRED_AUTHORITY = ("EXP-000780", "EXP-000781", "EXP-000782")
ROW_RE = re.compile(
    r"^\|\s*(A(?:[1-9]|1[0-9]|2[0-3]))\s*\|.*\|\s*"
    r"(OPEN|PASS|REPAIR|FAIL)(?:\s*;[^|]*)?\s*\|\s*$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        .encode("utf-8")
    ).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_labels(text: str) -> set[str]:
    return set(re.findall(r"\\label\{([^}]+)\}", text))


def proof_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = ROW_RE.match(line)
        if match:
            rows.append(
                {
                    "id": match.group(1),
                    "disposition": match.group(2),
                    "line": str(line_number),
                }
            )
    return rows


def validate_state(
    manuscript_text: str,
    proof_text: str,
    readiness_text: str,
    handoff_text: str,
    matrix_text: str,
    package: dict[str, Any],
    locator: dict[str, Any],
    fresh: dict[str, Any],
    integrated: dict[str, Any],
    paper_pdf_count: int,
) -> dict[str, Any]:
    claim_status = package.get("claim_status")
    expected_claim_status = {
        "claim_bearing": False,
        "publication_status": "RESEARCH_ONLY",
        "result_id": "R-497",
        "tier": "T0",
    }
    if claim_status != expected_claim_status:
        raise ValueError("claim/result scope is no longer the bounded R-497 T0 scope")
    if package.get("status") != "UNFROZEN_CONTENT_REVIEW":
        raise ValueError("package must remain UNFROZEN_CONTENT_REVIEW until signed review")
    if package.get("pdf_status") != "DEFERRED":
        raise ValueError("PDF must remain DEFERRED")
    chain = tuple(
        entry.get("exploration_id")
        for entry in package.get("authority_chain", [])[:3]
    )
    if chain != REQUIRED_AUTHORITY:
        raise ValueError(f"authority chain mismatch: {chain!r}")

    labels = source_labels(manuscript_text)
    missing_labels = sorted(set(REQUIRED_LABELS) - labels)
    if missing_labels:
        raise ValueError("missing manuscript labels: " + ", ".join(missing_labels))
    missing_tokens = [token for token in REQUIRED_TOKENS if token not in manuscript_text]
    if missing_tokens:
        raise ValueError("missing model/strict-regime token: " + ", ".join(missing_tokens))
    for token in (REQUIRED_AUTHORITY[0], REQUIRED_AUTHORITY[-1]):
        if token not in manuscript_text:
            raise ValueError("authority endpoint is absent from manuscript: " + token)
    if "EXP-000780--EXP-000782" not in manuscript_text:
        raise ValueError("manuscript authority-range text is absent")
    if REQUIRED_AUTHORITY[-1] not in handoff_text:
        raise ValueError("current independent authority token is absent from handoff")
    if "pressure" not in manuscript_text.lower() or "source" not in manuscript_text.lower():
        raise ValueError("finite/source pressure language is absent")
    if "tempered Euclidean DLR" not in manuscript_text:
        raise ValueError("tempered Euclidean DLR language is absent")
    if "continuous-loop FKG" not in manuscript_text:
        raise ValueError("continuous-loop FKG language is absent")
    if "reflection positivity" not in manuscript_text.lower():
        raise ValueError("reflection-positivity language is absent")
    if "Falk" not in manuscript_text or "Griffiths" not in manuscript_text:
        raise ValueError("Falk--Bruch/Griffiths language is absent")
    if "strict" not in manuscript_text.lower() or "cusp" not in manuscript_text.lower():
        raise ValueError("strict-cusp language is absent")
    if "parity" not in manuscript_text.lower() or "DLR" not in manuscript_text:
        raise ValueError("parity/DLR language is absent")

    rows = proof_rows(proof_text)
    row_ids = tuple(row["id"] for row in rows)
    if row_ids != EXPECTED_ROWS:
        raise ValueError(f"A1--A23 proof-audit rows mismatch: {row_ids!r}")
    dispositions: dict[str, int] = {}
    for row in rows:
        dispositions[row["disposition"]] = dispositions.get(row["disposition"], 0) + 1
    if not all(
        token in readiness_text
        for token in (
            "R12 signed mathematics review",
            "R13 signed literature/novelty review",
            "R15 final PDF",
        )
    ):
        raise ValueError("submission-readiness review/PDF gates are not present")
    if "A1--A23" not in handoff_text or "PDF remains deferred" not in handoff_text:
        raise ValueError("handoff does not expose the A1--A23 and PDF boundaries")
    if not all(token in matrix_text for token in REQUIRED_AUTHORITY):
        raise ValueError("review matrix authority chain is incomplete")

    if locator.get("status") != "PASS" or locator.get("claim_bearing") is not False:
        raise ValueError("locator checkpoint scope/status failed")
    coverage = locator.get("coverage", {})
    if coverage.get("row_count") != len(EXPECTED_ROWS):
        raise ValueError("locator row count does not cover A1--A23")
    if not isinstance(coverage.get("manuscript_locators_checked"), int) or (
        coverage["manuscript_locators_checked"] <= 0
    ):
        raise ValueError("locator manuscript coverage is empty")
    if fresh.get("status") != "PASS" or fresh.get("claim_bearing") is not False:
        raise ValueError("fresh checkpoint scope/status failed")
    if fresh.get("audit_count") != 7 or fresh.get("total_assertions", 0) <= 0:
        raise ValueError("fresh checkpoint does not contain all seven audits")
    if integrated.get("status") != "PASS" or integrated.get("claim_bearing") is not False:
        raise ValueError("integrated checkpoint scope/status failed")
    if integrated.get("result_id") != "R-497" or integrated.get("pdf_status") != "DEFERRED":
        raise ValueError("integrated checkpoint result/PDF scope failed")
    if len(integrated.get("manuscript_replay", [])) != 7:
        raise ValueError("integrated manuscript replay does not contain seven groups")
    if len(integrated.get("canonical_replay", [])) != 7:
        raise ValueError("integrated canonical replay does not contain seven groups")
    independent = integrated.get("independent_replay", {})
    child = independent.get("child_assertions", {})
    if child.get("assertions_passed") != child.get("assertions_total") or (
        child.get("assertions_total", 0) <= 0
    ):
        raise ValueError("independent child replay is not complete")
    if independent.get("package_assertions", 0) <= 0:
        raise ValueError("independent package replay is empty")
    if paper_pdf_count != 0:
        raise ValueError("Q3LOCK paper PDF exists before final freeze")

    return {
        "required_labels": len(REQUIRED_LABELS),
        "required_tokens": len(REQUIRED_TOKENS),
        "authority_chain": list(REQUIRED_AUTHORITY),
        "proof_audit_rows": len(rows),
        "proof_audit_dispositions": dispositions,
        "locator_rows": coverage["row_count"],
        "locator_manuscript_locators": coverage["manuscript_locators_checked"],
        "fresh_audits": fresh["audit_count"],
        "fresh_assertions": fresh["total_assertions"],
        "integrated_manuscript_groups": len(integrated["manuscript_replay"]),
        "integrated_canonical_groups": len(integrated["canonical_replay"]),
        "independent_child_assertions": child["assertions_total"],
        "independent_package_assertions": independent["package_assertions"],
        "paper_pdf_count": paper_pdf_count,
        "completion_state": "INCOMPLETE_EXTERNAL_REVIEW_AND_FREEZE",
    }


def hostile_checks(
    manuscript_text: str,
    proof_text: str,
    readiness_text: str,
    handoff_text: str,
    matrix_text: str,
    package: dict[str, Any],
    locator: dict[str, Any],
    fresh: dict[str, Any],
    integrated: dict[str, Any],
    paper_pdf_count: int,
) -> list[dict[str, str]]:
    mutations: list[tuple[str, str, str, str, dict[str, Any]]] = []
    mutations.append(
        (
            "missing-required-label",
            manuscript_text.replace(
                r"\label{eq:hamiltonian}", r"\label{eq:hamiltonian-removed}", 1
            ),
            proof_text,
            handoff_text,
            package,
        )
    )
    package_claim_mutation = json.loads(json.dumps(package))
    package_claim_mutation["claim_status"]["claim_bearing"] = True
    mutations.append(
        (
            "claim-promotion",
            manuscript_text,
            proof_text,
            handoff_text,
            package_claim_mutation,
        )
    )
    package_status_mutation = json.loads(json.dumps(package))
    package_status_mutation["status"] = "FROZEN"
    mutations.append(
        (
            "premature-freeze",
            manuscript_text,
            proof_text,
            handoff_text,
            package_status_mutation,
        )
    )
    mutations.append(
        (
            "missing-authority",
            manuscript_text,
            proof_text,
            handoff_text.replace("EXP-000782", "EXP-999999", 1),
            package,
        )
    )
    checks: list[dict[str, str]] = []
    for name, mutated_manuscript, mutated_proof, mutated_handoff, mutated_package in mutations:
        try:
            validate_state(
                mutated_manuscript,
                mutated_proof,
                readiness_text,
                mutated_handoff,
                matrix_text,
                mutated_package,
                locator,
                fresh,
                integrated,
                paper_pdf_count,
            )
        except ValueError:
            checks.append({"name": name, "status": "PASS", "expected": "rejected"})
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return checks


def build_payload() -> dict[str, Any]:
    manuscript_text = MANUSCRIPT.read_text(encoding="utf-8")
    proof_text = PROOF_AUDIT.read_text(encoding="utf-8")
    readiness_text = READINESS.read_text(encoding="utf-8")
    handoff_text = HANDOFF.read_text(encoding="utf-8")
    matrix_text = MATRIX.read_text(encoding="utf-8")
    package = read_json(PACKAGE)
    authority_manifest = read_json(AUTHORITY_MANIFEST)
    validation_package = json.loads(json.dumps(package))
    validation_package["authority_chain"] = authority_manifest.get("authority_chain", [])
    locator = read_json(LOCATOR_RESULT)
    fresh = read_json(FRESH_RESULT)
    integrated = read_json(INTEGRATED_RESULT)
    paper_pdf_count = len(tuple(PAPER.rglob("*.pdf")))
    coverage = validate_state(
        manuscript_text,
        proof_text,
        readiness_text,
        handoff_text,
        matrix_text,
        validation_package,
        locator,
        fresh,
        integrated,
        paper_pdf_count,
    )
    hostile = hostile_checks(
        manuscript_text,
        proof_text,
        readiness_text,
        handoff_text,
        matrix_text,
        validation_package,
        locator,
        fresh,
        integrated,
        paper_pdf_count,
    )
    sources = (
        MANUSCRIPT,
        PROOF_AUDIT,
        READINESS,
        HANDOFF,
        PACKAGE,
        AUTHORITY_MANIFEST,
        MATRIX,
        LOCATOR_RESULT,
        FRESH_RESULT,
        INTEGRATED_RESULT,
        STRATEGY_NOTE,
        LITERATURE_NOTE,
        LITERATURE_SUPPLEMENT_NOTE,
        KKK_BOUNDARY_NOTE,
        LINEAGE_NOTE,
        KP_NOTE,
        KP_SCRIPT,
        KP_TEST,
        KP_RESULT,
        EXPLORATIONS,
        TEST,
        Path(__file__).resolve(),
    )
    return {
        "schema": "tect/q3lock-completion-gate-audit/1.0",
        "script_version": __version__,
        "status": "PASS",
        "result_id": "R-497",
        "exploration_id": "EXP-001661",
        "tier": "T0",
        "claim_bearing": False,
        "pdf_status": "DEFERRED",
        "coverage": coverage,
        "hostile_checks": hostile,
        "assertions_passed": len(REQUIRED_LABELS)
        + len(REQUIRED_TOKENS)
        + len(REQUIRED_AUTHORITY)
        + coverage["proof_audit_rows"]
        + len(hostile),
        "source_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in sources
        },
        "payload_sha256": payload_digest(coverage),
        "scope": (
            "Objective-coverage and publication-boundary audit for the "
            "EXP-000780 -> EXP-000781 -> EXP-000782/R-497 paper package. "
            "It does not certify any mathematical proof row or external review."
        ),
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode(
        "utf-8"
    )
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-new", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            payload = build_payload()
            if len(payload["hostile_checks"]) != 4:
                raise AssertionError("hostile completion checks are incomplete")
            print("Q3LOCK COMPLETION-GATE SELF-TEST: PASS", len(payload["hostile_checks"]))
            return 0
        if args.write_new and os.path.lexists(args.output):
            raise FileExistsError(f"refusing to overwrite: {args.output}")
        before = None if args.write_new else args.output.read_bytes()
        payload = build_payload()
        if args.write_new:
            write_new(args.output, payload)
        else:
            if json.loads(before.decode("utf-8")) != payload or args.output.read_bytes() != before:
                raise ValueError("saved completion-gate audit differs; investigate without overwrite")
        print(
            "Q3LOCK COMPLETION-GATE AUDIT: PASS",
            payload["coverage"]["proof_audit_rows"],
            "proof rows;",
            payload["coverage"]["locator_manuscript_locators"],
            "locators;",
            "PDF_COUNT=" + str(payload["coverage"]["paper_pdf_count"]),
            "state=" + payload["coverage"]["completion_state"],
        )
        return 0
    except (AssertionError, FileExistsError, OSError, ValueError, KeyError, TypeError) as error:
        print("Q3LOCK COMPLETION-GATE AUDIT: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
