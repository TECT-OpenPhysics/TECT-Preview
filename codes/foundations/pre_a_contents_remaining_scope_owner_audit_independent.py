#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-460 residual scan."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-contents-remaining-scope-owner-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-independent-pre_a_contents_remaining_scope_owner_audit/result.json"
)
ROOTS = ("Backup", "Codes", "Runs", "Website", "Docs", "Github")
EXCLUDED = ("Docs/math", "Github/note", "Docs/status", "Github/status")
EXTENSIONS = {".txt", ".md", ".tex"}
PATTERNS = {
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
LOOSE_QLEDGER = re.compile(r"one[- ]?use.*q", re.I)
TOKENS = (
    "heat_root_incidence",
    "root filtration",
    "conditional replicas",
    "raw-current spatial intertwiner",
    "production_one_use_q_ledger",
)


def atomic_json(path: Path, payload: dict) -> None:
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


def raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def residual(relative: str) -> bool:
    return not any(relative == item or relative.startswith(item + "/") for item in EXCLUDED)


def scan(root: Path) -> dict:
    paths = sorted(
        {
            path
            for top in ROOTS
            for path in (root / top).rglob("*")
            if path.is_file()
            and path.suffix.lower() in EXTENSIONS
            and residual(path.relative_to(root).as_posix())
        },
        key=lambda path: path.as_posix().lower(),
    )
    rows = []
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        groups = {name: bool(pattern.search(text)) for name, pattern in PATTERNS.items()}
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
                "groups": groups,
                "group_count": sum(groups.values()),
                "merged_bundle": "merged" in path.name.casefold(),
                "exact_tokens": [
                    token for token in TOKENS if token.casefold() in text.casefold()
                ],
                "loose_qledger_match": bool(LOOSE_QLEDGER.search(text)),
                "strict_qledger_match": groups["qledger"],
            }
        )
    complete = [row for row in rows if row["group_count"] == len(PATTERNS)]
    partial = [row for row in rows if 3 <= row["group_count"] < len(PATTERNS)]
    exact = [row for row in rows if row["exact_tokens"]]
    loose_only = [
        row for row in rows if row["loose_qledger_match"] and not row["strict_qledger_match"]
    ]
    loose_only_complete = [
        row
        for row in complete
        if row["loose_qledger_match"] and not row["strict_qledger_match"]
    ]
    hashes = {row["sha256"] for row in rows}
    return {
        "contents_root": str(root),
        "included_roots": list(ROOTS),
        "excluded_subtrees": list(EXCLUDED),
        "text_extensions": sorted(EXTENSIONS),
        "paths_scanned": len(paths),
        "unique_content_hashes": len(hashes),
        "duplicate_path_count": len(paths) - len(hashes),
        "complete_semantic_rows": complete,
        "complete_semantic_paths": len(complete),
        "complete_semantic_unique_hashes": len({row["sha256"] for row in complete}),
        "merged_complete_paths": sum(row["merged_bundle"] for row in complete),
        "standalone_complete_rows": [row for row in complete if not row["merged_bundle"]],
        "standalone_complete_paths": sum(not row["merged_bundle"] for row in complete),
        "partial_rows_at_least_three_groups": partial,
        "partial_paths_at_least_three_groups": len(partial),
        "exact_token_rows": exact,
        "exact_owner_token_paths": len(exact),
        "all_complete_rows_are_merged": all(row["merged_bundle"] for row in complete),
        "loose_qledger_only_rows": loose_only,
        "loose_qledger_only_paths": len(loose_only),
        "loose_qledger_only_complete_rows": loose_only_complete,
        "loose_qledger_only_complete_rows_are_merged": all(
            row["merged_bundle"] for row in loose_only_complete
        ),
    }


def run(output: Path = DEFAULT_OUTPUT, contents_root: Path | None = None) -> dict:
    if contents_root is None:
        raise ValueError("--contents-root is required")
    root = contents_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []

    def check(name, condition, actual, expected, group):
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    identity = [manifest["result_id"], manifest["exploration_id"], manifest["task_id"]]
    check("identity", identity == ["R-460", "EXP-001333", "T-054"], identity, ["R-460", "EXP-001333", "T-054"], "provenance")
    check("methods unchanged", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all method-preservation flags true", "method-firewall")
    result = scan(root)
    expected = manifest["expected_boundary"]
    for name, key in (
        ("path boundary", "paths_scanned"),
        ("unique hash boundary", "unique_content_hashes"),
        ("duplicate boundary", "duplicate_path_count"),
        ("complete boundary", "complete_semantic_paths"),
        ("standalone boundary", "standalone_complete_paths"),
        ("partial boundary", "partial_paths_at_least_three_groups"),
        ("exact-token boundary", "exact_owner_token_paths"),
        ("loose q-ledger boundary", "loose_qledger_only_paths"),
    ):
        check(name, result[key] == expected[key], result[key], expected[key], "owner-applicability")
    for name, key in (
        ("merged boundary", "all_complete_rows_are_merged"),
        ("loose merged boundary", "loose_qledger_only_complete_rows_are_merged"),
    ):
        check(name, result[key] == expected[key], result[key], expected[key], "owner-applicability")
    check("scan cardinality", result["paths_scanned"] > 0 and result["unique_content_hashes"] > 0 and result["unique_content_hashes"] <= result["paths_scanned"], [result["paths_scanned"], result["unique_content_hashes"], result["duplicate_path_count"]], "positive scan and deduplication cardinalities", "provenance")
    check("no promotion", manifest["claim_bearing"] is False and manifest["formal_integration"]["no_tier_change"] is True, [manifest["claim_bearing"], manifest["formal_integration"]["no_tier_change"]], [False, True], "promotion-firewall")
    payload = {
        "schema": "tect/pre-a-contents-remaining-scope-owner-audit-independent/1.0",
        "run_kind": "independent",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "verdict": "PASS_BOUNDED_NO_STANDALONE_OWNER",
        "assertion_count": len(checks),
        "assertions": checks,
        "scan": result,
        "boundary": manifest["decision_scope"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "source_hashes": {"manifest": raw_sha(MANIFEST), "script": raw_sha(Path(__file__))},
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-460 INDEPENDENT {payload['verdict']} paths={result['paths_scanned']} standalone={result['standalone_complete_paths']} exact={result['exact_owner_token_paths']}", flush=True)
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
        print("R-460 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
