#!/usr/bin/env python3
"""Collect a reviewable P1 production-functional evidence run.

The tool executes the hash-pinned multi-grid verifier in a fresh subprocess,
records the environment and all input hashes, and writes a reviewer checklist.
It never changes a claim tier and a preflight run is explicitly non-certifying.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__claims__ = ["A1-PRODUCTION-FUNCTIONAL-REALISATION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = "A1-PRODUCTION-FUNCTIONAL-REALISATION"
CLAIM_ROOT = REPO / "claims" / CLAIM_ID
MANIFEST = CLAIM_ROOT / "production_functional_manifest.json"
DEFAULT_ROOT = CLAIM_ROOT / "runs" / "promotion-evidence"
BACKEND = Path("codes/foundations/n001_variational_backend.py")
VERIFIER = Path("codes/foundations/a1_production_backend_verify.py")
INPUTS = (
    Path("claims/a1f/production_functional_manifest.json"),
    BACKEND,
    VERIFIER,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def resolved_root(path: Path) -> Path:
    return path if path.is_absolute() else REPO / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument(
        "--mode",
        choices=("preflight", "independent"),
        default="preflight",
    )
    parser.add_argument("--grids", nargs="+", type=int, default=[4, 6, 8])
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_ROOT)
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    compact = args.run_id.replace("-", "").replace("_", "")
    if not compact or not compact.isalnum():
        raise SystemExit("run-id must use only letters, digits, hyphen, and underscore")
    if not args.reviewer.strip():
        raise SystemExit("reviewer must not be blank")
    if len(set(args.grids)) != len(args.grids) or any(grid < 4 for grid in args.grids):
        raise SystemExit("grids must be unique integers >=4")


def pinned_hash_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    return {
        "backend_hash_matches_manifest": (
            sha256(REPO / BACKEND)
            == manifest["production_reference_backend"]["sha256"]
        ),
        "verifier_hash_matches_manifest": (
            sha256(REPO / VERIFIER)
            == manifest["independent_verifier"]["sha256"]
        ),
    }


def review_text(args: argparse.Namespace, run_dir: Path, verdict: str) -> str:
    mode_note = (
        "This is a non-certifying local preflight; it cannot count as independent "
        "reproduction evidence."
        if args.mode == "preflight"
        else "This run is intended for independent reproduction review before any T5 decision."
    )
    relative = run_dir.relative_to(REPO).as_posix()
    return f"""# A1 production-functional review

Claim: {CLAIM_ID}
Mode: {args.mode}
Run directory: {relative}
Recorded verdict: {verdict}

{mode_note}

## Required checks

- [ ] The command in `environment.json` was executed without modification.
- [ ] The backend and verifier hashes match the frozen manifest.
- [ ] `verification-result.json` reports `PRODUCTION-BACKEND-MULTIGRID-PASS`.
- [ ] Grids 4, 6, and 8 and all five required field classes were exercised.
- [ ] All four numerical maxima are below their recorded thresholds.
- [ ] The scope is discrete spectral-torus variational consistency only.
- [ ] No continuum theorem, minimizer, BCC selection, or stability claim is inferred.

Reviewer:
Decision:
Date:
Notes:
"""


def main() -> int:
    args = parse_args()
    validate_args(args)
    missing = [str(path) for path in INPUTS if not (REPO / path).is_file()]
    if missing:
        raise SystemExit(f"missing inputs: {missing}")

    run_dir = resolved_root(args.evidence_root) / args.run_id
    if run_dir.exists():
        raise SystemExit(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hash_checks = pinned_hash_checks(manifest)
    timestamp = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    command = [
        sys.executable,
        str(REPO / VERIFIER),
        "--grids",
        *[str(grid) for grid in args.grids],
        "--output",
        str(run_dir / "verification-result.json"),
    ]
    environment = {
        "schema": "tect/a1-production-functional-evidence-environment/1.0",
        "claim_id": CLAIM_ID,
        "tool_version": __version__,
        "timestamp_utc": timestamp,
        "run_id": args.run_id,
        "run_mode": args.mode,
        "reviewer": args.reviewer,
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "cwd": str(REPO),
        "git_head": git_value("rev-parse", "HEAD"),
        "git_describe_dirty": git_value("describe", "--always", "--dirty"),
        "input_sha256": {str(path): sha256(REPO / path) for path in INPUTS},
        "manifest_hash_checks": hash_checks,
        "command": command,
    }
    write_json(run_dir / "environment.json", environment)

    result = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    (run_dir / "verifier.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (run_dir / "verifier.stderr.txt").write_text(result.stderr, encoding="utf-8")
    verification: dict[str, Any] = {}
    verification_path = run_dir / "verification-result.json"
    if verification_path.is_file():
        verification = json.loads(verification_path.read_text(encoding="utf-8"))

    technical_pass = (
        result.returncode == 0
        and all(hash_checks.values())
        and verification.get("verdict") == "PRODUCTION-BACKEND-MULTIGRID-PASS"
        and sorted(verification.get("grids", [])) == sorted(args.grids)
        and all(item.get("pass") for item in verification.get("assertions", []))
    )
    if technical_pass and args.mode == "independent":
        verdict = "REPRODUCTION-PASS"
    elif technical_pass:
        verdict = "TECHNICAL-PASS"
    elif args.mode == "independent":
        verdict = "REPRODUCTION-FAIL"
    else:
        verdict = "TECHNICAL-FAIL"

    evidence = {
        "schema": "tect/a1-production-functional-promotion-evidence/1.0",
        "claim_id": CLAIM_ID,
        "purpose": "review evidence collection only; this tool makes no tier decision",
        "run_id": args.run_id,
        "run_mode": args.mode,
        "reviewer": args.reviewer,
        "timestamp_utc": timestamp,
        "verifier_returncode": result.returncode,
        "manifest_hash_checks": hash_checks,
        "verifier_verdict": verification.get("verdict"),
        "verifier_maxima": verification.get("maxima"),
        "verdict": verdict,
        "tier_status": "unchanged by this evidence package",
    }
    write_json(run_dir / "promotion-evidence.json", evidence)
    (run_dir / "REVIEW.md").write_text(review_text(args, run_dir, verdict), encoding="utf-8")
    file_hashes = {
        path.name: sha256(path)
        for path in sorted(run_dir.iterdir())
        if path.is_file() and path.name != "FILE-SHA256.json"
    }
    write_json(run_dir / "FILE-SHA256.json", file_hashes)

    print(f"Verdict: {verdict}")
    print(f"Evidence directory: {run_dir}")
    return 0 if technical_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
