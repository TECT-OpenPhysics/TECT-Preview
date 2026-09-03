#!/usr/bin/env python3
"""Reject new direct consumers of frozen generated aggregate volumes.

The cutover keeps CHANGELOG.md and CATALOG.md at their historical paths because
issued verifier packages search those files directly.  New code must instead
use changelog/log.jsonl, changelog/index.json, verification/catalog/index.json,
or verification/catalog-summary.json. The allowlist is derived from the immutable
cutover commit, so deleting/migrating a legacy consumer needs no hand-maintained
list while adding a new one fails closed.
"""
__version__ = "1.0.1"
__first_issued__ = "2026-08-10"
__version_issued__ = "2026-09-03"

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CUTOVER_COMMIT = "4db22f4ea94bb1a936d1a2e4b416aa2d6d1960d4"
TARGETS = ("CHANGELOG.md", "CATALOG.md", "verification/catalog.json")
CODE_SUFFIXES = {".py", ".js", ".ts", ".mjs", ".cjs"}
SELF = "verification/scripts/check_aggregate_consumers.py"
# These are integrity guards, not data consumers: frozen compatibility bytes,
# the canonical root-file allowlist, and exact-byte checkout fixture coverage.
# The checkout test writes a synthetic catalog in a temporary Git repository;
# it never consumes the real frozen catalog as research data.
EXEMPT = {
    SELF,
    "verification/scripts/check_protocol_single_source.py",
    "verification/tests/test_aggregate_indexes.py",
    "verification/tests/test_checkout_bytes.py",
}
SKIP_PARTS = {".git", ".venv", "venv", "internal", "tmp", "build", ".cache"}


def _git(*args):
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=60,
    )


def baseline(target):
    run = _git("grep", "-l", "-F", target, CUTOVER_COMMIT, "--", "*.py", "*.js", "*.ts")
    if run.returncode not in (0, 1):
        raise RuntimeError(run.stderr.strip() or f"git grep exited {run.returncode}")
    prefix = CUTOVER_COMMIT + ":"
    return {
        line[len(prefix):] if line.startswith(prefix) else line
        for line in run.stdout.splitlines() if line.strip()
    }


def current(target):
    found = set()
    for path in REPO.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        rel_path = path.relative_to(REPO)
        if any(part in SKIP_PARTS for part in rel_path.parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if target in source:
            found.add(rel_path.as_posix())
    return found


def main():
    failed = False
    for target in TARGETS:
        try:
            old = baseline(target)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"AGGREGATE-CONSUMERS: FAIL -- cannot audit {target}: {exc}")
            return 1
        now = current(target)
        new = sorted(now - old - EXEMPT)
        migrated = sorted(old - now)
        if new:
            failed = True
            print(f"AGGREGATE-CONSUMERS: FAIL -- {len(new)} new {target} consumer(s)")
            for path in new:
                print(f"  - {path}")
        else:
            print(
                f"AGGREGATE-CONSUMERS: PASS -- {target}: {len(now - EXEMPT)} current, "
                f"{len(migrated)} legacy consumer(s) migrated"
            )
    if failed:
        print("  use canonical JSONL/JSON or a compact index instead of a frozen root volume")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
