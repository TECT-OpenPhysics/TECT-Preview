#!/usr/bin/env python3
"""Build a hash-pinned reproduction manifest for the A2/R-157/R-158 paper.

The manifest is a package-integrity aid.  It records the exact manuscript,
PDF, verification scripts, JSON artifacts, source hashes exposed by those
artifacts, and the expected finite replay commands.  It does not prove the
analytic theorem, replace an external review, or promote any claim tier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PAPER_ROOT.parents[2]
DEFAULT_OUTPUT = PAPER_ROOT / "verification" / "runs" / "reproduction-manifest.json"

PACKAGE_FILES = (
    "README.md",
    "STATUS.md",
    "claims-cited.md",
    "external-review-handoff.md",
    "independent-proof-review-form.md",
    "specialist-novelty-review-form.md",
    "source-sign-reconciliation.md",
    "submission-readiness.md",
    "theorem-applicability-audit.md",
    "literature-crosswalk.md",
    "manuscript.tex",
    "manuscript.pdf",
    "proof-audit.md",
    "verification/README.md",
    "verification/exact_coercivity_audit.py",
    "verification/classii_sign_audit.py",
    "verification/ensemble_identity_audit.py",
    "verification/analytic_dependency_audit.py",
    "verification/review_packet_audit.py",
    "verification/reproduction_manifest.py",
    "verification/runs/exact-coercivity.json",
    "verification/runs/classii-sign.json",
    "verification/runs/ensemble-identity.json",
    "verification/runs/analytic-dependency.json",
    "verification/runs/review-packet.json",
)

EXPECTED_AUDITS = {
    "exact-coercivity": {"verdict": "PAPER-EXACT-COERCIVITY-AUDIT-PASS", "passed": 13, "total": 13},
    "classii-sign": {"verdict": "PAPER-CLASSII-SIGN-AUDIT-PASS", "passed": 8, "total": 8},
    "ensemble-identity": {"verdict": "PAPER-ENSEMBLE-IDENTITY-AUDIT-PASS", "passed": 24, "total": 24},
    "analytic-dependency": {"verdict": "PAPER-ANALYTIC-DEPENDENCY-AUDIT-PASS", "passed": 50, "total": 50},
    "review-packet": {"verdict": "PAPER-REVIEW-PACKET-AUDIT-PASS", "passed": 22, "total": 22},
}

EXPECTED_COMMANDS = (
    {
        "command": "python -X utf8 codes/foundations/a2_full_production_verify.py",
        "expected": "A2-FULL-PRODUCTION-VERIFY-PASS (61/61)",
        "scope": "finite A2 full-production wrapper",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py",
        "expected": "26/26 PASS",
        "scope": "finite R-157 primary exact replay",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py",
        "expected": "24/24 PASS",
        "scope": "finite R-157 independent non-importing replay",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py",
        "expected": "integrated 144/144 PASS; legacy A2 61/61 PASS",
        "scope": "finite R-157/A2 integrated replay",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition.py",
        "expected": "35/35 PASS",
        "scope": "finite R-158 primary exact replay",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py",
        "expected": "24/24 PASS",
        "scope": "finite R-158 independent standard-library replay",
    },
    {
        "command": "python -X utf8 codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py",
        "expected": "integrated 155/155 PASS; R-157/A2 regression PASS",
        "scope": "finite R-158 integrated replay",
    },
    {
        "command": "python -X utf8 verification/scripts/a2_r472_lean_crosscheck_verify.py --output tmp/r472-integrated.json",
        "expected": "R-472 INTEGRATED PASS 22/22; Lean=PASS",
        "scope": "non-bearing exact/Lean assurance replay",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/exact_coercivity_audit.py",
        "expected": "PAPER-EXACT-COERCIVITY-AUDIT-PASS: 13/13",
        "scope": "paper-local exact coercivity",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/classii_sign_audit.py",
        "expected": "PAPER-CLASSII-SIGN-AUDIT-PASS: 8/8",
        "scope": "paper-local source/sign check",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/ensemble_identity_audit.py",
        "expected": "PAPER-ENSEMBLE-IDENTITY-AUDIT-PASS: 24/24",
        "scope": "paper-local ensemble identities",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/analytic_dependency_audit.py",
        "expected": "PAPER-ANALYTIC-DEPENDENCY-AUDIT-PASS: 50/50",
        "scope": "paper-local structural analytic audit",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/review_packet_audit.py --self-test",
        "expected": "PAPER-REVIEW-PACKET-AUDIT-PASS: 22/22",
        "scope": "blank external-review packet structure and hash consistency",
    },
    {
        "command": "python -X utf8 publish/papers/a2-r157-r158-ensemble-minimizers/verification/reproduction_manifest.py --self-test",
        "expected": "PAPER-REPRODUCTION-MANIFEST-PASS",
        "scope": "hash-pinned package and replay-input integrity",
    },
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


def command_script(command: str) -> str:
    parts = command.split()
    try:
        index = parts.index("utf8")
    except ValueError as error:
        raise ValueError(f"command lacks '-X utf8': {command}") from error
    if index < 1 or parts[index - 1] != "-X" or index + 1 >= len(parts):
        raise ValueError(f"command has malformed Python prefix: {command}")
    return parts[index + 1]


def documented_command_scripts(text: str) -> tuple[str, ...]:
    scripts: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("& $py "):
            continue
        remainder = stripped[len("& $py "):]
        if not remainder:
            raise ValueError("empty $py command in verification README")
        scripts.append(remainder.split()[0])
    return tuple(scripts)


def self_test() -> None:
    assert command_script("python -X utf8 a.py") == "a.py"
    assert command_script("python -X utf8 a.py --flag value") == "a.py"
    try:
        command_script("python a.py")
    except ValueError:
        pass
    else:
        raise AssertionError("missing UTF-8 prefix was accepted")
    assert documented_command_scripts("& $py a.py\n& $py b.py --flag\n") == (
        "a.py",
        "b.py",
    )


def artifact_summary(path: Path, name: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assertions = data.get("assertions", {})
    if isinstance(assertions, dict) and "passed" in assertions and "total" in assertions:
        passed = int(assertions["passed"])
        total = int(assertions["total"])
    else:
        passed = int(data.get("passed_count", 0))
        total = int(data.get("assertion_count", 0))
    expected = EXPECTED_AUDITS[name]
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(path),
        "verdict": data.get("verdict"),
        "passed": passed,
        "total": total,
        "expected": expected,
        "manuscript_sha256": data.get("manuscript_sha256"),
        "manifest_sha256": data.get("manifest_sha256"),
    }


def build() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for relative in PACKAGE_FILES:
        path = PAPER_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    artifacts = {
        name: artifact_summary(
            PAPER_ROOT / "verification" / "runs" / f"{name}.json", name
        )
        for name in EXPECTED_AUDITS
    }
    manuscript_hash = sha256(PAPER_ROOT / "manuscript.tex")
    artifact_hash_match = all(
        entry["manuscript_sha256"] in (None, manuscript_hash)
        for entry in artifacts.values()
    )
    audit_pass = all(
        entry["verdict"] == entry["expected"]["verdict"]
        and entry["passed"] == entry["expected"]["passed"]
        and entry["total"] == entry["expected"]["total"]
        for entry in artifacts.values()
    )
    replay_inputs: list[dict[str, Any]] = []
    missing_replay_inputs: list[str] = []
    for item in EXPECTED_COMMANDS:
        relative = command_script(item["command"])
        path = REPO_ROOT / relative
        if not path.is_file():
            missing_replay_inputs.append(relative)
            continue
        replay_inputs.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    all_replay_inputs_present = not missing_replay_inputs
    expected_command_scripts = tuple(
        command_script(item["command"]) for item in EXPECTED_COMMANDS
    )
    documented_scripts = documented_command_scripts(
        (PAPER_ROOT / "verification" / "README.md").read_text(encoding="utf-8")
    )
    verification_readme_matches = documented_scripts == expected_command_scripts
    return {
        "schema": "tect/paper-reproduction-manifest/1.1",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generator": "publish/papers/a2-r157-r158-ensemble-minimizers/verification/reproduction_manifest.py",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "package_scope": "finite side-16 classical A2/R-157/R-158 draft only",
        "manuscript_sha256": manuscript_hash,
        "files": files,
        "artifacts": artifacts,
        "expected_commands": list(EXPECTED_COMMANDS),
        "replay_inputs": replay_inputs,
        "missing_replay_inputs": missing_replay_inputs,
        "documented_replay_inputs": list(documented_scripts),
        "integrity": {
            "all_package_files_present": True,
            "all_replay_inputs_present": all_replay_inputs_present,
            "replay_command_count": len(EXPECTED_COMMANDS),
            "replay_input_count": len(replay_inputs),
            "verification_readme_command_paths_match": verification_readme_matches,
            "audit_verdicts_and_counts_match": audit_pass,
            "artifact_manuscript_hashes_match": artifact_hash_match,
        },
        "verdict": "PAPER-REPRODUCTION-MANIFEST-PASS" if audit_pass and artifact_hash_match and all_replay_inputs_present and verification_readme_matches else "FAIL",
        "non_claims": [
            "This manifest proves package integrity only; it is not an analytic proof or external review.",
            "Expected command strings are finite-scope replay oracles and do not promote claim tiers.",
            "No canonical-transfer source-sign, novelty, operator, physical-limit, submission, upload, tag, push, or publication conclusion is asserted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    result = build()
    atomic_write(args.output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['verdict']}")
    print(f"artifact: {args.output}")
    return 0 if result["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
