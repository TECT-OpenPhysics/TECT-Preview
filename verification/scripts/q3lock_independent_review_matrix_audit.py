#!/usr/bin/env python3
"""Validate that the Q3LOCK external-review matrix covers A1--A23 exactly.

This is a handoff-package diagnostic.  It checks coverage, evidence locators,
and hostile missing/duplicate-row mutations; it does not review mathematics,
sign a theorem, or generate a paper PDF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
NOTE = REPO / "strategy/q3lock-independent-review-matrix-260907.md"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-q3lock-independent-review-matrix-audit/result.json"
)
ROW_RE = re.compile(r"^\|\s*(A(?:[1-9]|1[0-9]|2[0-3]))\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
EXPECTED_IDS = tuple(f"A{index}" for index in range(1, 24))


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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

    def check(self, name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def parse_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = ROW_RE.match(line)
        if match:
            rows.append(
                {
                    "id": match.group(1),
                    "question": match.group(2),
                    "evidence": match.group(3),
                    "decision": match.group(4),
                    "line": str(line_number),
                }
            )
    return rows


def validate_matrix(text: str) -> tuple[Audit, list[dict[str, str]]]:
    audit = Audit()
    rows = parse_rows(text)
    identifiers = [row["id"] for row in rows]
    audit.check("row count", len(rows) == len(EXPECTED_IDS), len(rows), len(EXPECTED_IDS))
    audit.check("row order", identifiers == list(EXPECTED_IDS), identifiers, list(EXPECTED_IDS))
    authority_present = all(
        token in text for token in ("EXP-000780", "EXP-000781", "EXP-000782")
    )
    audit.check("authority chain", authority_present, authority_present, True)
    pdf_deferred = "paper PDF gate remains" in text
    audit.check("pdf deferral", pdf_deferred, pdf_deferred, True)
    for row in rows:
        audit.check(
            f"{row['id']} question",
            bool(row["question"].strip()),
            row["question"].strip(),
            "nonempty",
        )
        audit.check(
            f"{row['id']} manuscript locator",
            "manuscript.tex#" in row["evidence"],
            row["evidence"],
            "manuscript.tex#...",
        )
        audit.check(
            f"{row['id']} review decision",
            bool(row["decision"].strip()),
            row["decision"].strip(),
            "nonempty",
        )
    return audit, rows


def build_payload() -> dict[str, Any]:
    text = NOTE.read_text(encoding="utf-8")
    audit, rows = validate_matrix(text)

    # Hostile validator fixtures: the checker must refuse a missing row, a
    # duplicate row, and a row whose evidence locator is erased.
    missing_text = text.replace(
        next(line for line in text.splitlines() if line.startswith("| A23 |")), ""
    )
    try:
        validate_matrix(missing_text)
    except AssertionError:
        audit.check("hostile missing row rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile missing row rejected", False, "accepted", "rejected")

    a1_line = next(line for line in text.splitlines() if line.startswith("| A1 |"))
    duplicate_text = text + "\n" + a1_line + "\n"
    try:
        validate_matrix(duplicate_text)
    except AssertionError:
        audit.check("hostile duplicate row rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile duplicate row rejected", False, "accepted", "rejected")

    erased_text = text.replace("manuscript.tex#", "source#")
    try:
        validate_matrix(erased_text)
    except AssertionError:
        audit.check("hostile missing locator rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile missing locator rejected", False, "accepted", "rejected")

    script = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-independent-review-matrix-audit/1.0",
        "script_version": __version__,
        "result_id": "R-497",
        "exploration_id": "EXP-001634",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "matrix": {
            "path": str(NOTE.relative_to(REPO)).replace("\\", "/"),
            "row_ids": [row["id"] for row in rows],
            "rows": rows,
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "files": {
            "script": str(script.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(script),
            "matrix_sha256": normalized_sha256(NOTE),
        },
        "verdict": "PASS",
        "boundary": (
            "Coverage and hostile-mutation diagnostics for the A1-A23 external-review "
            "handoff only. This result does not sign any proof row, promote R-497, "
            "certify literature applicability, or generate a paper PDF."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"Q3LOCK REVIEW MATRIX PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
