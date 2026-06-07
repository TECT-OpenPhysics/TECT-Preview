#!/usr/bin/env python3
"""doctor.py -- workspace readiness check for resuming TECT on any machine.

Run this immediately after copying the TECT folder to a new computer and
connecting cowork. It answers one question: "is this copy ready to resume
research?" -- by verifying the interpreter, the single external dependency,
the legacy-constants module the numerical codes import, and that every
generated ledger is in sync with its source.

    python verification/scripts/doctor.py

Exit 0 iff READY. Each failed check prints an actionable fix. No physics
constants are hardcoded; the only literal is the minimum supported Python
version (a tooling requirement, not a result).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-06-07"

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MIN_PY = (3, 10)                      # tooling requirement (f-strings w/ unions etc.)
SCRIPTS = REPO / "verification" / "scripts"

results = []  # (ok, name, detail/fix)


def record(ok, name, detail):
    results.append((bool(ok), name, detail))
    print(f"  [{'OK ' if ok else 'XX '}] {name} -- {detail}")


def run_check(label, rel_args):
    """Run a repo script in --check mode; OK iff exit 0."""
    r = subprocess.run([sys.executable, str(SCRIPTS / rel_args[0])] + rel_args[1:],
                       capture_output=True, text=True, cwd=str(REPO))
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    record(r.returncode == 0, label, tail if r.returncode == 0
           else f"FAILED -- run: python verification/scripts/{' '.join(rel_args)}")


def main() -> int:
    print(f"TECT doctor -- workspace readiness ({REPO})")

    # 1. interpreter
    record(sys.version_info >= MIN_PY, "python-version",
           f"{sys.version_info.major}.{sys.version_info.minor} "
           f"(need >= {MIN_PY[0]}.{MIN_PY[1]})")

    # 2. single external dependency
    record(importlib.util.find_spec("numpy") is not None, "numpy",
           "import numpy OK" if importlib.util.find_spec("numpy")
           else "MISSING -- run: pip install -r requirements.txt")

    # 3. canonical files present (resume needs these readable)
    needed = ["CLAUDE.md", "GOVERNANCE.md", "CLAIMS.md", "ROADMAP.md",
              "CHANGELOG.md", "TODO.md", "todo/todo.json",
              "negative-results/registry.md", "SESSION.md"]
    missing = [f for f in needed if not (REPO / f).exists()]
    record(not missing, "canonical-files",
           "all present" if not missing else f"MISSING: {missing}")

    # 4. legacy-constants module the numerical codes import (codes/vacuum/*)
    legacy = REPO / "archive" / "legacy" / "scripts" / "Math424_AddA_reading_uniqueness.py"
    record(legacy.exists(), "legacy-constants-module",
           "archive/legacy/scripts present (codes/ imports resolve)" if legacy.exists()
           else "MISSING archive/legacy/scripts -- copy the WHOLE folder, not just claims/")

    # 5. generated ledgers in sync with their sources
    run_check("ledger-sync", ["lint_claims.py", "--render", "--check"])
    run_check("catalog-sync", ["build_catalog.py", "--check"])
    run_check("lineage-sync", ["build_lineage.py", "--check"])
    run_check("todo-sync", ["todo.py", "--check"])

    # 6. optional: pdflatex (only needed to rebuild note PDFs / FORM-CHECK)
    import shutil
    has_tex = shutil.which("pdflatex") is not None
    record(True, "pdflatex (optional)",
           "present (FORM-CHECK available)" if has_tex
           else "absent -- only needed for note-PDF FORM-CHECK; research can resume without it")

    hard_fail = [n for ok, n, _ in results if not ok and n != "pdflatex (optional)"]
    print()
    if hard_fail:
        print(f"DOCTOR: NOT READY ({len(hard_fail)} issue(s): {', '.join(hard_fail)})")
        return 1
    print("DOCTOR: READY -- session-entry prelude (CLAUDE.md §1) can proceed; "
          "see SESSION.md to continue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
