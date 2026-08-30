#!/usr/bin/env python3
"""Integrated primary/independent/hostile verifier for R-459."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-contents-alt-terminology-owner-audit-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_contents_alt_terminology_owner_audit.py"
INDEPENDENT = ROOT / (
    "codes/foundations/pre_a_contents_alt_terminology_owner_audit_independent.py"
)
HOSTILE = ROOT / (
    "codes/foundations/pre_a_contents_alt_terminology_owner_audit_hostile.py"
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-integrated-pre_a_contents_alt_terminology_owner_audit/integrated.json"
)
PRIMARY_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-pre_a_contents_alt_terminology_owner_audit/result.json"
)
INDEPENDENT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-independent-pre_a_contents_alt_terminology_owner_audit/result.json"
)
HOSTILE_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-pre_a_contents_alt_terminology_owner_audit/result.json"
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


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


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
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": actual,
                "expected": expected,
            }
        )

    commands = [
        (
            "primary",
            PRIMARY,
            PRIMARY_OUTPUT,
        ),
        (
            "independent",
            INDEPENDENT,
            INDEPENDENT_OUTPUT,
        ),
        (
            "hostile",
            HOSTILE,
            HOSTILE_OUTPUT,
        ),
    ]
    command_reports = {}
    for label, script, result_path in commands:
        command = [
            sys.executable,
            "-X",
            "utf8",
            str(script),
            "--output",
            str(result_path),
        ]
        if label != "hostile":
            command.extend(["--contents-root", str(root)])
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        check(
            f"{label} command",
            completed.returncode == 0 and result_path.is_file(),
            {"returncode": completed.returncode, "output": completed.stdout[-500:]},
            "returncode 0 and result file",
            "execution",
        )
        command_reports[label] = {
            "command": command,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-500:],
            "stderr_tail": completed.stderr[-500:],
            "result_path": result_path.relative_to(ROOT).as_posix(),
        }

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    pscan = primary["scan"]
    iscan = independent["scan"]
    keys = (
        "paths_scanned",
        "unique_content_hashes",
        "duplicate_path_count",
        "complete_semantic_paths",
        "standalone_complete_paths",
        "partial_paths_at_least_three_groups",
        "exact_owner_token_paths",
        "loose_qledger_only_paths",
    )
    check(
        "primary-independent scan agreement",
        all(pscan[key] == iscan[key] for key in keys),
        {key: [pscan[key], iscan[key]] for key in keys},
        "matching scan summaries",
        "independence",
    )
    expected = manifest["expected_boundary"]
    check(
        "strict complete boundary",
        pscan["complete_semantic_paths"] == expected["complete_semantic_paths"],
        pscan["complete_semantic_paths"],
        expected["complete_semantic_paths"],
        "owner-applicability",
    )
    check(
        "standalone owner boundary",
        pscan["standalone_complete_paths"]
        == expected["standalone_complete_paths"],
        pscan["standalone_complete_paths"],
        expected["standalone_complete_paths"],
        "owner-applicability",
    )
    check(
        "exact token boundary",
        pscan["exact_owner_token_paths"] == expected["exact_owner_token_paths"],
        pscan["exact_owner_token_paths"],
        expected["exact_owner_token_paths"],
        "owner-applicability",
    )
    check(
        "merged row boundary",
        pscan["all_complete_rows_are_merged"]
        == expected["all_complete_rows_are_merged"],
        pscan["all_complete_rows_are_merged"],
        expected["all_complete_rows_are_merged"],
        "owner-applicability",
    )
    check(
        "loose phrase boundary",
        pscan["loose_qledger_only_complete_rows_are_merged"]
        == expected["loose_qledger_only_complete_rows_are_merged"],
        pscan["loose_qledger_only_complete_rows_are_merged"],
        expected["loose_qledger_only_complete_rows_are_merged"],
        "owner-applicability",
    )
    check(
        "hostile firewall",
        hostile["mutations_rejected"] == len(hostile["mutations"]) == 8,
        [hostile["mutations_rejected"], len(hostile["mutations"])],
        8,
        "adversarial-review",
    )
    check(
        "methods preserved",
        all(manifest["method_preservation"].values()),
        manifest["method_preservation"],
        "all method-preservation flags true",
        "method-firewall",
    )
    check(
        "claim and tier firewall",
        manifest["claim_bearing"] is False
        and manifest["tier"] == "T0"
        and manifest["formal_integration"]["no_tier_change"] is True,
        [
            manifest["claim_bearing"],
            manifest["tier"],
            manifest["formal_integration"]["no_tier_change"],
        ],
        [False, "T0", True],
        "promotion-firewall",
    )
    payload = {
        "schema": "tect/pre-a-contents-owner-audit-integrated/1.0",
        "run_kind": "integrated",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "verdict": "PASS_BOUNDED_NO_STANDALONE_OWNER",
        "assertion_count": len(checks),
        "assertions": checks,
        "command_reports": command_reports,
        "primary_summary": {
            key: pscan[key]
            for key in keys
        },
        "hostile_summary": {
            "mutations_rejected": hostile["mutations_rejected"],
            "assertion_count": hostile["assertion_count"],
        },
        "source_hashes": {
            "manifest": digest(MANIFEST),
            "primary": digest(PRIMARY),
            "independent": digest(INDEPENDENT),
            "hostile": digest(HOSTILE),
            "integrated": digest(Path(__file__)),
        },
        "boundary": manifest["decision_scope"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(
        f"R-459 INTEGRATED {payload['verdict']} "
        f"{len(checks)}/{len(checks)}",
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
        assert payload["verdict"] == "PASS_BOUNDED_NO_STANDALONE_OWNER"
        print("R-459 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
