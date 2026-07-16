#!/usr/bin/env python3
"""Collect a reviewable A1 manifest-promotion evidence run.

The tool records a reproduction of ``a1_kernel_checks.py`` without changing a
claim tier.  A later T5 decision still has to be made through the normal claim
card, devil's-advocate, changelog, and release process.
"""

__version__ = "1.0.0"
__claims__ = ["A1-PRODUCTION-KERNEL-MANIFEST"]

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = "A1-PRODUCTION-KERNEL-MANIFEST"
CLAIM_ROOT = REPO / "claims" / CLAIM_ID
DEFAULT_ROOT = CLAIM_ROOT / "runs" / "promotion-evidence"
INPUTS = (
    Path("claims/A1-PRODUCTION-KERNEL-MANIFEST/canonical_n001_kernel.json"),
    Path("codes/foundations/a1_kernel_checks.py"),
    Path("codes/foundations/n001_solver/continuation_mu2_v25.py"),
    Path("codes/foundations/n001_solver/bloch_linearization.py"),
    Path("codes/foundations/n001_solver/math56_constants.py"),
    Path("codes/foundations/n001_solver/PROVENANCE.json"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect an A1 N-001 manifest promotion evidence package."
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Stable run identifier; use letters, digits, hyphen, and underscore only.",
    )
    parser.add_argument(
        "--reviewer",
        required=True,
        help="Execution actor or reviewer name recorded in the evidence package.",
    )
    parser.add_argument(
        "--mode",
        choices=("independent", "preflight"),
        default="independent",
        help="Use preflight for non-certifying local checks before independent review.",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Directory under which the run-id directory is created.",
    )
    parser.add_argument(
        "--expected-checker-version",
        default="1.6.0",
        help="Expected a1_kernel_checks.py JSON version.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    run_id_chars = args.run_id.replace("-", "").replace("_", "")
    if not run_id_chars or not run_id_chars.isalnum():
        raise SystemExit("run-id must use only letters, digits, hyphen, and underscore")
    if not args.reviewer.strip():
        raise SystemExit("reviewer must not be blank")


def resolved_root(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO / path


def load_checker_result(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def review_text(args: argparse.Namespace, run_dir: Path, verdict: str) -> str:
    if args.mode == "preflight":
        mode_note = (
            "This is a non-certifying technical preflight and cannot count as "
            "independent reproduction evidence."
        )
    else:
        mode_note = (
            "This run is intended for independent reproduction review before any "
            "T5 claim-card proposal."
        )
    return f"""# A1 Promotion Evidence Review

Claim: {CLAIM_ID}
Run mode: {args.mode}
Run directory: {run_dir.relative_to(REPO)}
Recorded verdict: {verdict}

{mode_note}

## Required reviewer checks

- [ ] The run was executed from the recorded command in `environment.json`.
- [ ] `a1_kernel_checks.json` reports `all_pass: true` and version `1.6.0`.
- [ ] The input hashes in `environment.json` match the source tree under review.
- [ ] The scope is only the canonical N-001 pure-Brazovskii scalar slice.
- [ ] No statement here is treated as a full PDE, BCC, or operator theorem.
- [ ] A main-proof-line decision is recorded before any T5 claim update.

Reviewer:
Decision:
Date:
Notes:
"""


def main() -> int:
    args = parse_args()
    validate_args(args)

    evidence_root = resolved_root(args.evidence_root)
    run_dir = evidence_root / args.run_id
    if run_dir.exists():
        raise SystemExit(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    missing = [str(path) for path in INPUTS if not (REPO / path).exists()]
    if missing:
        raise SystemExit(f"missing required input files: {missing}")

    timestamp = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    input_hashes = {str(path): sha256(REPO / path) for path in INPUTS}
    command = [
        sys.executable,
        str(REPO / "codes" / "foundations" / "a1_kernel_checks.py"),
        "--output",
        str(run_dir / "a1_kernel_checks.json"),
    ]
    environment = {
        "schema": "a1-promotion-evidence-environment-v1",
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
        "expected_checker_version": args.expected_checker_version,
        "input_sha256": input_hashes,
        "command": command,
    }
    write_json(run_dir / "environment.json", environment)

    result = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    (run_dir / "a1_kernel_checks.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (run_dir / "a1_kernel_checks.stderr.txt").write_text(result.stderr, encoding="utf-8")

    checker = load_checker_result(run_dir / "a1_kernel_checks.json")
    version_ok = checker.get("version") == args.expected_checker_version
    gates_ok = bool(checker.get("all_pass"))
    technical_pass = result.returncode == 0 and version_ok and gates_ok
    if technical_pass and args.mode == "independent":
        verdict = "REPRODUCTION-PASS"
    elif technical_pass:
        verdict = "TECHNICAL-PASS"
    elif args.mode == "independent":
        verdict = "REPRODUCTION-FAIL"
    else:
        verdict = "TECHNICAL-FAIL"

    evidence = {
        "schema": "a1-promotion-evidence-v1",
        "claim_id": CLAIM_ID,
        "purpose": "promotion evidence collection only; no tier decision is made by this tool",
        "run_id": args.run_id,
        "run_mode": args.mode,
        "reviewer": args.reviewer,
        "timestamp_utc": timestamp,
        "checker_returncode": result.returncode,
        "checker_version": checker.get("version"),
        "expected_checker_version": args.expected_checker_version,
        "checker_version_ok": version_ok,
        "checker_all_pass": gates_ok,
        "verdict": verdict,
        "tier_status": "unchanged by this evidence package",
        "input_sha256": input_hashes,
        "files": [
            "environment.json",
            "a1_kernel_checks.json",
            "a1_kernel_checks.stdout.txt",
            "a1_kernel_checks.stderr.txt",
            "promotion_evidence.json",
            "REVIEW.md",
            "FILE-SHA256.json",
        ],
    }
    write_json(run_dir / "promotion_evidence.json", evidence)
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
