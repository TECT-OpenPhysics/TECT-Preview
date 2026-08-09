#!/usr/bin/env python3
"""Verify that AGENTS.md is the sole binding collaborator protocol."""

__version__ = "1.0.0"
__first_issued__ = "2026-08-10"
__version_issued__ = "2026-08-10"

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT_ALLOWLIST = {
    ".gitattributes", ".gitignore", "AGENTS.md", "CATALOG.md", "CHANGELOG.md", "CLAIMS.md",
    "CLAUDE.md", "GOVERNANCE.md", "README.md", "requirements.txt",
    "RESULTS-LEDGER.md", "REVIEWING.md", "ROADMAP.md", "SESSION.md", "TODO.md",
}
BINDING_READERS = (
    "GOVERNANCE.md", "SESSION.md", "governance/CODE-DISCIPLINE.md",
    "governance/naming-and-versioning.md", "verification/scripts/todo.py",
)


def main():
    errors = []
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    shim = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    if "single binding AI-collaborator protocol" not in shim or "AGENTS.md" not in shim:
        errors.append("CLAUDE.md is not an explicit AGENTS.md compatibility pointer")
    if len(shim.splitlines()) > 12 or re.search(r"^##\s+\d", shim, re.M):
        errors.append("CLAUDE.md duplicates protocol content instead of remaining a short shim")
    if "## 1. Session-entry sequence" not in agents or "DEFAULT" not in agents:
        errors.append("AGENTS.md lacks the canonical session or commit protocol")

    forbidden = re.compile(r"CLAUDE\.md\s*(?:§|section\s+\d)", re.I)
    for relative in BINDING_READERS:
        text = (REPO / relative).read_text(encoding="utf-8")
        if forbidden.search(text):
            errors.append(f"{relative} treats CLAUDE.md as a sectioned authority")

    run = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=30,
    )
    if run.returncode != 0:
        errors.append("cannot enumerate tracked root files")
    else:
        tracked_roots = {line for line in run.stdout.splitlines() if line and "/" not in line}
        actual_roots = {
            path.name for path in REPO.iterdir()
            if path.is_file() and path.name != ".git"
        }
        unexpected = sorted((tracked_roots | actual_roots) - ROOT_ALLOWLIST)
        missing = sorted(ROOT_ALLOWLIST - actual_roots)
        if unexpected:
            errors.append(f"tracked root files outside allowlist: {unexpected}")
        if missing:
            errors.append(f"canonical tracked root files missing: {missing}")

    if errors:
        print("PROTOCOL-SINGLE-SOURCE: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PROTOCOL-SINGLE-SOURCE: PASS -- AGENTS.md canonical; CLAUDE.md shim; root allowlist exact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
