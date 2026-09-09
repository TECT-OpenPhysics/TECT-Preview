#!/usr/bin/env python3
"""Check that every A1--A23 review locator resolves to current sources.

This is a provenance and handoff diagnostic.  It verifies actual manuscript
labels, strategy-file references, exploration IDs, authority-chain text and
PDF deferral in the independent-review matrix.  It does not review any
mathematical argument, sign a proof row, promote R-497 or generate a PDF.
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
MATRIX = ROOT / "strategy/q3lock-independent-review-matrix-260907.md"
MANUSCRIPT = ROOT / "publish/papers/q3lock-phase-coexistence/manuscript.tex"
PACKAGE = ROOT / "publish/papers/q3lock-phase-coexistence/verification/package-manifest.json"
EXPLORATIONS = ROOT / "explorations/log.jsonl"
TEST = ROOT / "verification/tests/test_q3lock_review_locator_audit.py"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
     "2026-09-08-q3lock-review-locator-audit-source-review-v1/result.json"
)
EXPECTED_IDS = tuple(f"A{index}" for index in range(1, 24))
ROW_RE = re.compile(
    r"^\|\s*(A(?:[1-9]|1[0-9]|2[0-3]))\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$"
)
LOCATOR_RE = re.compile(r"manuscript\.tex#([A-Za-z0-9:_-]+)")
STRATEGY_RE = re.compile(r"(?<![A-Za-z0-9_./-])(strategy/[A-Za-z0-9._/-]+)")
EXP_RE = re.compile(r"EXP-\d{6}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def parse_rows(text: str) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = ROW_RE.match(line)
        if match:
            rows.append({
                "id": match.group(1),
                "question": match.group(2),
                "evidence": match.group(3),
                "decision": match.group(4),
                "line": line_number,
            })
    return rows


def source_labels(text: str) -> set[str]:
    return set(re.findall(r"\\label\{([^}]+)\}", text))


def validate_matrix(matrix_text: str, manuscript_text: str, exploration_text: str,
                    package: dict[str, Any]) -> dict[str, Any]:
    rows = parse_rows(matrix_text)
    identifiers = [row["id"] for row in rows]
    if identifiers != list(EXPECTED_IDS):
        raise ValueError(f"matrix row order/count mismatch: {identifiers!r}")
    labels = source_labels(manuscript_text)
    strategy_refs: set[str] = set()
    exploration_refs: set[str] = set()
    row_details = []
    for row in rows:
        if not row["question"].strip() or not row["decision"].strip():
            raise ValueError(f"empty review field in {row['id']}")
        locators = LOCATOR_RE.findall(row["evidence"])
        if not locators:
            raise ValueError(f"missing manuscript locator in {row['id']}")
        missing = sorted(set(locators) - labels)
        if missing:
            raise ValueError(f"missing manuscript labels for {row['id']}: {missing}")
        refs = sorted(set(STRATEGY_RE.findall(row["evidence"])))
        for ref in refs:
            target = (ROOT / ref).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                raise ValueError(f"missing or escaping strategy reference: {ref}")
        exps = sorted(set(EXP_RE.findall(row["evidence"])))
        for exp in exps:
            if exp not in exploration_text:
                raise ValueError(f"matrix references absent exploration record: {exp}")
        strategy_refs.update(refs)
        exploration_refs.update(exps)
        row_details.append({
            "id": row["id"],
            "line": row["line"],
            "manuscript_locators": sorted(set(locators)),
            "strategy_refs": refs,
            "exploration_refs": exps,
        })
    if not all(token in matrix_text for token in ("EXP-000780", "EXP-000781", "EXP-000782")):
        raise ValueError("authority chain missing from review matrix")
    if "paper PDF gate remains" not in matrix_text:
        raise ValueError("PDF deferral statement missing from review matrix")
    expected_scope = {
        "result_id": "R-497",
        "tier": "T0",
        "claim_bearing": False,
        "publication_status": "RESEARCH_ONLY",
    }
    if (package.get("claim_status") != expected_scope
            or package.get("status") != "UNFROZEN_CONTENT_REVIEW"
            or package.get("pdf_status") != "DEFERRED"):
        raise ValueError("package scope or PDF boundary changed")
    return {
        "row_ids": identifiers,
        "row_count": len(rows),
        "manuscript_labels_available": len(labels),
        "manuscript_locators_checked": sum(len(row["manuscript_locators"]) for row in row_details),
        "strategy_files_checked": sorted(strategy_refs),
        "exploration_ids_checked": sorted(exploration_refs),
        "rows": row_details,
    }


def hostile_checks(matrix_text: str, manuscript_text: str, exploration_text: str,
                   package: dict[str, Any]) -> list[dict[str, Any]]:
    checks = []
    mutations = []
    a23 = next(line for line in matrix_text.splitlines() if line.startswith("| A23 |"))
    mutations.append(("missing-row", matrix_text.replace(a23, "", 1), manuscript_text))
    mutations.append(("duplicate-row", matrix_text + "\n" + a23 + "\n", manuscript_text))
    bad_label = manuscript_text.replace("\\label{eq:bounded-phase-witness}", "\\label{eq:bounded-phase-witness-removed}", 1)
    mutations.append(("missing-manuscript-label", matrix_text, bad_label))
    for name, mutated_matrix, mutated_manuscript in mutations:
        try:
            validate_matrix(mutated_matrix, mutated_manuscript, exploration_text, package)
        except ValueError:
            checks.append({"name": name, "status": "PASS", "expected": "rejected"})
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return checks


def build_payload() -> dict[str, Any]:
    if not __debug__:
        raise ValueError("assertions must be enabled; do not use python -O")
    matrix_text = MATRIX.read_text(encoding="utf-8")
    manuscript_text = MANUSCRIPT.read_text(encoding="utf-8")
    exploration_text = EXPLORATIONS.read_text(encoding="utf-8")
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    coverage = validate_matrix(matrix_text, manuscript_text, exploration_text, package)
    hostile = hostile_checks(matrix_text, manuscript_text, exploration_text, package)
    script = Path(__file__).resolve()
    sources = (MATRIX, MANUSCRIPT, PACKAGE, EXPLORATIONS, TEST, script)
    return {
        "schema": "tect/q3lock-review-locator-audit/1.0",
        "script_version": __version__,
        "status": "PASS",
        "result_id": "R-497",
        "exploration_id": "EXP-001660",
        "tier": "T0",
        "claim_bearing": False,
        "pdf_status": "DEFERRED",
        "coverage": coverage,
        "hostile_checks": hostile,
        "assertions_passed": coverage["row_count"] + len(hostile),
        "source_hashes": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in sources},
        "payload_sha256": payload_digest(coverage),
        "scope": (
            "Exact locator and provenance coverage for the A1-A23 external-review handoff. "
            "This result does not review mathematics, sign a proof row, promote R-497, "
            "certify theorem applicability or generate a paper PDF."
        ),
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
        if not __debug__:
            raise ValueError("assertions must be enabled; do not use python -O")
        if args.self_test:
            payload = hostile_checks(
                MATRIX.read_text(encoding="utf-8"), MANUSCRIPT.read_text(encoding="utf-8"),
                EXPLORATIONS.read_text(encoding="utf-8"),
                json.loads(PACKAGE.read_text(encoding="utf-8")),
            )
            print("Q3LOCK REVIEW LOCATOR SELF-TEST: PASS", len(payload))
            return 0
        if args.write_new and os.path.lexists(args.output):
            raise FileExistsError(f"refusing to overwrite: {args.output}")
        before = None if args.write_new else args.output.read_bytes()
        payload = build_payload()
        if args.write_new:
            write_new(args.output, payload)
        else:
            if json.loads(before.decode("utf-8")) != payload or args.output.read_bytes() != before:
                raise ValueError("saved locator audit differs; investigate without rewriting history")
        print("Q3LOCK REVIEW LOCATOR AUDIT: PASS", payload["coverage"]["row_count"],
              "rows;", payload["coverage"]["manuscript_locators_checked"], "manuscript locators;",
              len(payload["coverage"]["strategy_files_checked"]), "strategy files;",
              len(payload["coverage"]["exploration_ids_checked"]), "explorations")
        return 0
    except (AssertionError, FileExistsError, OSError, ValueError, KeyError, TypeError) as error:
        print("Q3LOCK REVIEW LOCATOR AUDIT: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
