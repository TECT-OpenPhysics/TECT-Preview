#!/usr/bin/env python3
"""Capture and audit the versioned Simon Feynman--Kac source bytes.

This is a provenance diagnostic only.  It records the raw byte length and
SHA-256 of a locally downloaded, version-pinned PDF, exercises a hostile byte
mutation, and writes a non-claim-bearing JSON result.  The PDF itself is never
copied into the repository, and the historical R-497 source manifest is not
modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://arxiv.org/pdf/math-ph/9907022v1"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-q3lock-simon-source-capture/result.json"
)


def sha256_bytes(data: bytes) -> str:
    """Return the raw-byte SHA-256 digest without newline normalisation."""

    return hashlib.sha256(data).hexdigest()


def atomic_no_replace(path: Path, payload: dict[str, Any]) -> None:
    """Write one UTF-8 JSON result without overwriting an existing result."""

    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fetch_url(url: str) -> bytes:
    """Fetch a pinned source URL into memory for a transient audit only."""

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TECT-Q3LOCK-source-audit/0.1"},
    )
    # The URL is version-pinned.  The caller still records the resulting raw
    # digest, so transport certificate policy cannot silently change identity.
    # A local --source path is preferred when a trust-managed download exists.
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, context=context, timeout=60) as response:
        return response.read()


def load_bytes(source: Path | None, url: str | None) -> tuple[bytes, str]:
    if (source is None) == (url is None):
        raise ValueError("provide exactly one of --source or --url")
    if source is not None:
        if not source.is_file():
            raise FileNotFoundError(source)
        return source.read_bytes(), "local-path"
    assert url is not None
    return fetch_url(url), "versioned-url"


def assertion(name: str, condition: bool, actual: Any, expected: Any) -> dict[str, Any]:
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    return {
        "name": name,
        "status": "PASS",
        "actual": actual,
        "expected": expected,
    }


def build_payload(
    data: bytes,
    *,
    url: str,
    expected_sha256: str,
    expected_bytes: int,
    retrieval_date: str,
    retrieval_mode: str,
) -> dict[str, Any]:
    actual_sha256 = sha256_bytes(data)
    actual_bytes = len(data)
    rows = [
        assertion("nonempty source bytes", actual_bytes > 0, actual_bytes, ">0"),
        assertion("PDF magic", data[:5] == b"%PDF-", data[:5].decode("ascii", "replace"), "%PDF-"),
        assertion("raw SHA-256 matches supplied source oracle", actual_sha256 == expected_sha256, actual_sha256, expected_sha256),
        assertion("raw byte length matches supplied source oracle", actual_bytes == expected_bytes, actual_bytes, expected_bytes),
    ]

    hostile = bytearray(data)
    hostile[len(hostile) // 2] ^= 1
    hostile_sha256 = sha256_bytes(bytes(hostile))
    rows.append(
        assertion(
            "one-byte hostile mutation is rejected",
            hostile_sha256 != expected_sha256,
            hostile_sha256,
            "different from expected SHA-256",
        )
    )

    return {
        "schema": "q3lock-simon-source-capture-v1",
        "tool_version": __version__,
        "status": "PROVISIONAL_CAPTURE",
        "claim_bearing": False,
        "source": {
            "author": "B. Simon",
            "title": "A Feynman-Kac Formula for Unbounded Semigroups",
            "url": url,
            "version": "v1",
            "locator": "Theorem 1.1 and equations (1.1)--(1.3), printed page 2",
            "retrieval_date_utc": retrieval_date,
            "retrieval_mode": retrieval_mode,
        },
        "raw_bytes": {
            "byte_length": actual_bytes,
            "sha256": actual_sha256,
            "expected_byte_length_oracle": expected_bytes,
            "expected_sha256_oracle": expected_sha256,
        },
        "assertions": {
            "passed": len(rows),
            "total": len(rows),
            "rows": rows,
        },
        "boundary": [
            "The PDF bytes are not stored in the repository.",
            "This provisional capture does not alter the historical R-497 manifest.",
            "A final source freeze must re-capture all cited sources together.",
            "The source audit does not establish form convergence, thermodynamic limits, DLR multiplicity, or phase coexistence.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path, help="local raw PDF bytes to audit")
    group.add_argument("--url", default=None, help="version-pinned URL to fetch transiently")
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--expected-bytes", required=True, type=int)
    parser.add_argument("--retrieval-date", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true", help="run the hostile mutation check and print PASS")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data, retrieval_mode = load_bytes(args.source, args.url)
    payload = build_payload(
        data,
        url=args.url or DEFAULT_URL,
        expected_sha256=args.expected_sha256,
        expected_bytes=args.expected_bytes,
        retrieval_date=args.retrieval_date,
        retrieval_mode=retrieval_mode,
    )
    if args.self_test:
        print(
            "Q3LOCK Simon source capture SELF-TEST PASS: "
            f"{payload['assertions']['passed']}/{payload['assertions']['total']} assertions"
        )
    if args.output is not None:
        atomic_no_replace(args.output, payload)
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
