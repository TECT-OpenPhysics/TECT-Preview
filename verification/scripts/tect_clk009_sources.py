#!/usr/bin/env python3
"""CLK009 source-byte and repository provenance audit, not a physics verifier.

Default/--check compares current repository bytes and declared source pins with
the stored receipt. --cache additionally requires original PDF bytes. --write
generates a receipt and requires --cache. No downloads, model evaluation,
injection/recovery, parameter fitting or empirical response certification occur.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STRATEGY = ROOT / "strategy/clock"
RECEIPT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-10-07-tect-clk009/sources.json"
DOCUMENTS = (
    "TECT-CLK-009-admission-v1.json",
    "TECT-CLK-009-sources-v1.json",
    "TECT-CLK-009-assessment-v1.json",
    "TECT-CLK-009-owner-request-v1.md",
    "TECT-CLK-009-checkpoint-v1.md",
)
RECEIPT_HEADERS = {
    "schema": "tect/source-provenance-run/1.0",
    "id": "TECT-CLK-009",
    "evidence_level": "BYTE_PROVENANCE_ONLY",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_pdf(data: bytes, expected: str) -> dict:
    if not data.startswith(b"%PDF-"):
        raise ValueError("Source is not a PDF byte stream")
    actual = digest(data)
    if actual != expected:
        raise ValueError("Source SHA-256 mismatch")
    return {"sha256": actual, "bytes": len(data)}


def local_path(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Path escapes the declared base")
    return path


def check_headers(stored: dict) -> None:
    for key, expected in RECEIPT_HEADERS.items():
        if stored.get(key) != expected:
            raise ValueError("Invalid provenance receipt header: " + key)


def selftest() -> list[str]:
    # TEST_ONLY bytes, not a PDF parser or a mission-data fixture.
    fixture = b"%PDF-1.0\nTEST_ONLY\n"
    expected = digest(fixture)
    assert checked_pdf(fixture, expected)["bytes"] == len(fixture)
    checks = ["exact_bytes_accepted"]
    for name, payload, pin in (
        ("changed_bytes_rejected", fixture + b"X", expected),
        ("html_instead_of_pdf_rejected", b"<html>not a source</html>", expected),
        ("wrong_pin_rejected", fixture, "0" * 64),
    ):
        try:
            checked_pdf(payload, pin)
        except ValueError:
            checks.append(name)
        else:
            raise AssertionError(name)
    try:
        local_path(ROOT, "../outside")
    except ValueError:
        checks.append("path_escape_rejected")
    else:
        raise AssertionError("path escape")
    check_headers(dict(RECEIPT_HEADERS))
    for key in RECEIPT_HEADERS:
        changed = {**RECEIPT_HEADERS, key: "WRONG_TEST_ONLY"}
        try:
            check_headers(changed)
        except ValueError:
            checks.append(key + "_mutation_rejected")
        else:
            raise AssertionError("header mutation: " + key)
    return checks


def repository_report() -> dict:
    admission = json.loads((STRATEGY / DOCUMENTS[0]).read_text(encoding="utf-8"))
    protected = {}
    for relative, expected in admission["protected_sources"].items():
        actual = digest(local_path(ROOT, relative).read_bytes())
        if actual != expected:
            raise ValueError("Protected source changed: " + relative)
        protected[relative] = actual
    document_hashes = {
        "strategy/clock/" + name: digest((STRATEGY / name).read_bytes())
        for name in DOCUMENTS
    }
    document_hashes[Path(__file__).resolve().relative_to(ROOT).as_posix()] = digest(
        Path(__file__).read_bytes()
    )
    manifest = json.loads((STRATEGY / DOCUMENTS[1]).read_text(encoding="utf-8"))
    return {
        "protected_sources": protected,
        "documents": document_hashes,
        "source_pins": {key: item["sha256"] for key, item in manifest["sources"].items()},
        "selftests": selftest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write and args.cache is None:
        parser.error("--write requires --cache with the original PDFs")
    repository = repository_report()
    source_bytes = None
    if args.cache is not None:
        manifest = json.loads((STRATEGY / DOCUMENTS[1]).read_text(encoding="utf-8"))
        source_bytes = {
            key: checked_pdf(local_path(args.cache, item["cache_path"]).read_bytes(), item["sha256"])
            for key, item in manifest["sources"].items()
        }
    if args.write:
        report = {
            **RECEIPT_HEADERS,
            "actual_response_verified": False,
            "repository": repository,
            "source_bytes": source_bytes,
        }
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    check_headers(stored)
    if stored["repository"] != repository:
        raise ValueError("Stored repository receipt differs from current bytes")
    if source_bytes is not None and stored["source_bytes"] != source_bytes:
        raise ValueError("Stored source receipt differs from original source bytes")
    if stored["actual_response_verified"] is not False:
        raise ValueError("Provenance receipt cannot certify actual response")
    print(json.dumps({
        "status": "PASS_PROVENANCE_ONLY",
        "source_pins": len(repository["source_pins"]),
        "original_pdfs_rehashed": source_bytes is not None,
        "tooling_selftests": len(repository["selftests"]),
        "actual_response_verified": False,
        "goal_completed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
