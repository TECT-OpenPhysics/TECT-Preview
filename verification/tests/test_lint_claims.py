"""Smoke tests: the seeded ledger must validate and render in sync."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "verification" / "scripts" / "lint_claims.py"


def run_check(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO,
    )


def test_ledger_validates():
    r = run_check(str(LINT))
    assert r.returncode == 0, r.stdout + r.stderr


def test_claims_md_in_sync():
    r = run_check(str(LINT), "--render", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_catalog_in_sync():
    cat = REPO / "verification" / "scripts" / "build_catalog.py"
    r = run_check(str(cat), "--check")
    assert r.returncode == 0, r.stdout + r.stderr
