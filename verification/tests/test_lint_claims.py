"""Smoke tests: the seeded ledger must validate and render in sync."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "verification" / "scripts" / "lint_claims.py"


def test_ledger_validates():
    r = subprocess.run([sys.executable, str(LINT)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_claims_md_in_sync():
    r = subprocess.run([sys.executable, str(LINT), "--render", "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_catalog_in_sync():
    cat = REPO / "verification" / "scripts" / "build_catalog.py"
    r = subprocess.run([sys.executable, str(cat), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
