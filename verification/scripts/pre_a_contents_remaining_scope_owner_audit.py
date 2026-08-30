#!/usr/bin/env python3
"""Primary residual canonical-Contents owner-applicability audit for R-460.

This is a bounded provenance scan.  It complements R-459 and deliberately does
not infer a universal absence theorem or alter the existing owner contract.
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

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-contents-remaining-scope-owner-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-pre_a_contents_remaining_scope_owner_audit/result.json"
)
INCLUDED_ROOTS = ("Backup", "Codes", "Runs", "Website", "Docs", "Github")
EXCLUDED_SUBTREES = ("Docs/math", "Github/note", "Docs/status", "Github/status")
TEXT_SUFFIXES = {".txt", ".md", ".tex"}
GROUP_PATTERNS = {
    "generator": re.compile(r"generator|transfer\s+operator|markov\s+semigroup", re.I),
    "heat": re.compile(r"heat[-_ ]?(?:root|kernel|semigroup)|heat\s+root", re.I),
    "filtration": re.compile(r"filtration|conditional\s+replica|replica", re.I),
    "current": re.compile(
        r"raw[-_ ]?current|current\s+spatial|spatial\s+intertwiner", re.I
    ),
    "qledger": re.compile(
        r"\bq[-_ ]ledger\b|\bq[_ -]?k\b[^\r\n]{0,80}\bledger\b"
        r"|\bone[- ]use(?:d)?\s+q\b|\bnonnegative\s+q(?:[-_ ]ledger)?\b",
        re.I,
    ),
}
LOOSE_QLEDGER_PATTERN = re.compile(r"one[- ]?use.*q", re.I)
EXACT_TOKENS = (
    "heat_root_incidence",
    "root filtration",
    "conditional replicas",
    "raw-current spatial intertwiner",
    "production_one_use_q_ledger",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def repo_digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def _is_excluded(relative: str) -> bool:
    return any(
        relative == subtree or relative.startswith(subtree + "/")
        for subtree in EXCLUDED_SUBTREES
    )


def iter_paths(contents_root: Path) -> list[Path]:
    paths: set[Path] = set()
    for top in INCLUDED_ROOTS:
        base = contents_root / top
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            relative = path.relative_to(contents_root).as_posix()
            if not _is_excluded(relative):
                paths.add(path)
    return sorted(paths, key=lambda path: path.as_posix().lower())


def scan_contents(contents_root: Path) -> dict[str, Any]:
    paths = iter_paths(contents_root)
    complete_rows: list[dict[str, Any]] = []
    partial_rows: list[dict[str, Any]] = []
    exact_rows: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    unique_hashes: set[str] = set()
    for path in paths:
        raw = path.read_bytes()
        source_sha = hashlib.sha256(raw).hexdigest()
        unique_hashes.add(source_sha)
        text = raw.decode("utf-8", errors="replace")
        groups = {
            key: bool(pattern.search(text))
            for key, pattern in GROUP_PATTERNS.items()
        }
        row = {
            "path": path.relative_to(contents_root).as_posix(),
            "sha256": source_sha,
            "size_bytes": len(raw),
            "groups": groups,
            "group_count": sum(groups.values()),
            "merged_bundle": "merged" in path.name.casefold(),
            "exact_tokens": [
                token for token in EXACT_TOKENS if token.casefold() in text.casefold()
            ],
            "loose_qledger_match": bool(LOOSE_QLEDGER_PATTERN.search(text)),
            "strict_qledger_match": groups["qledger"],
        }
        all_rows.append(row)
        if row["exact_tokens"]:
            exact_rows.append(row)
        if row["group_count"] == len(GROUP_PATTERNS):
            complete_rows.append(row)
        elif row["group_count"] >= 3:
            partial_rows.append(row)
    standalone_rows = [row for row in complete_rows if not row["merged_bundle"]]
    loose_only_rows = [
        row
        for row in all_rows
        if row["loose_qledger_match"] and not row["strict_qledger_match"]
    ]
    loose_only_complete_rows = [
        row
        for row in complete_rows
        if row["loose_qledger_match"] and not row["strict_qledger_match"]
    ]
    return {
        "contents_root": str(contents_root),
        "included_roots": list(INCLUDED_ROOTS),
        "excluded_subtrees": list(EXCLUDED_SUBTREES),
        "text_extensions": sorted(TEXT_SUFFIXES),
        "paths_scanned": len(paths),
        "unique_content_hashes": len(unique_hashes),
        "duplicate_path_count": len(paths) - len(unique_hashes),
        "complete_semantic_rows": complete_rows,
        "complete_semantic_paths": len(complete_rows),
        "complete_semantic_unique_hashes": len(
            {row["sha256"] for row in complete_rows}
        ),
        "merged_complete_paths": sum(
            1 for row in complete_rows if row["merged_bundle"]
        ),
        "standalone_complete_rows": standalone_rows,
        "standalone_complete_paths": len(standalone_rows),
        "partial_rows_at_least_three_groups": partial_rows,
        "partial_paths_at_least_three_groups": len(partial_rows),
        "exact_token_rows": exact_rows,
        "exact_owner_token_paths": len(exact_rows),
        "all_complete_rows_are_merged": all(
            row["merged_bundle"] for row in complete_rows
        ),
        "loose_qledger_only_rows": loose_only_rows,
        "loose_qledger_only_paths": len(loose_only_rows),
        "loose_qledger_only_complete_rows": loose_only_complete_rows,
        "loose_qledger_only_complete_rows_are_merged": all(
            row["merged_bundle"] for row in loose_only_complete_rows
        ),
    }


def run(output: Path = DEFAULT_OUTPUT, contents_root: Path | None = None) -> dict[str, Any]:
    if contents_root is None:
        raise ValueError("--contents-root is required for external canonical source scanning")
    contents_root = contents_root.resolve()
    if not contents_root.is_dir():
        raise FileNotFoundError(contents_root)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected}
        )

    identity = [
        manifest["result_id"],
        manifest["exploration_id"],
        manifest["task_id"],
        manifest["claim_bearing"],
        manifest["tier"],
    ]
    check(
        "manifest identity",
        identity == ["R-460", "EXP-001333", "T-054", False, "T0"],
        identity,
        ["R-460", "EXP-001333", "T-054", False, "T0"],
        "provenance",
    )
    check(
        "method preservation",
        all(manifest["method_preservation"].values()),
        manifest["method_preservation"],
        "all method-preservation flags true",
        "method-firewall",
    )
    scan = scan_contents(contents_root)
    expected = manifest["expected_boundary"]
    for name, key in (
        ("path boundary", "paths_scanned"),
        ("unique hash boundary", "unique_content_hashes"),
        ("duplicate path boundary", "duplicate_path_count"),
        ("complete semantic boundary", "complete_semantic_paths"),
        ("standalone complete boundary", "standalone_complete_paths"),
        ("partial boundary", "partial_paths_at_least_three_groups"),
        ("exact owner-token boundary", "exact_owner_token_paths"),
        ("loose q-ledger boundary", "loose_qledger_only_paths"),
    ):
        check(name, scan[key] == expected[key], scan[key], expected[key], "owner-applicability")
    for name, key in (
        ("merged false-positive boundary", "all_complete_rows_are_merged"),
        ("loose q-ledger merged boundary", "loose_qledger_only_complete_rows_are_merged"),
    ):
        check(name, scan[key] == expected[key], scan[key], expected[key], "owner-applicability")
    check(
        "nonempty scan",
        scan["paths_scanned"] > 0 and scan["unique_content_hashes"] > 0,
        [scan["paths_scanned"], scan["unique_content_hashes"]],
        "positive scan cardinalities",
        "provenance",
    )
    check(
        "mirror deduplication recorded",
        scan["duplicate_path_count"] >= 0
        and scan["unique_content_hashes"] <= scan["paths_scanned"],
        [scan["duplicate_path_count"], scan["unique_content_hashes"]],
        "path count dominates unique content count",
        "provenance",
    )
    check(
        "no physical promotion",
        manifest["claim_bearing"] is False
        and manifest["formal_integration"]["no_tier_change"] is True,
        [manifest["claim_bearing"], manifest["formal_integration"]["no_tier_change"]],
        [False, True],
        "promotion-firewall",
    )
    payload = {
        "schema": "tect/pre-a-contents-remaining-scope-owner-audit-primary/1.0",
        "run_kind": "primary",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "verdict": "PASS_BOUNDED_NO_STANDALONE_OWNER",
        "assertion_count": len(checks),
        "assertions": checks,
        "scan": scan,
        "semantic_groups": manifest["semantic_groups"],
        "exact_owner_tokens": list(EXACT_TOKENS),
        "boundary": manifest["decision_scope"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "source_hashes": {
            "manifest": repo_digest(MANIFEST),
            "script": repo_digest(Path(__file__)),
        },
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        "R-460 PRIMARY "
        f"{payload['verdict']} paths={scan['paths_scanned']} "
        f"standalone={scan['standalone_complete_paths']} exact={scan['exact_owner_token_paths']}",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contents-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output, args.contents_root)
    if args.self_test:
        assert payload["assertion_count"] == len(payload["assertions"])
        assert payload["scan"]["complete_semantic_paths"] == 0
        assert payload["scan"]["standalone_complete_paths"] == 0
        assert payload["scan"]["exact_owner_token_paths"] == 0
        print("R-460 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
