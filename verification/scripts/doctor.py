#!/usr/bin/env python3
"""doctor.py -- workspace readiness check for resuming TECT on any machine.

Run this immediately after copying the TECT folder to a new computer and
connecting the workspace. It answers one question: "is this copy ready to resume
research?" -- by verifying the interpreter, the single external dependency,
the legacy-constants module the numerical codes import, and that every
generated ledger is in sync with its source.

    python verification/scripts/doctor.py

Exit 0 iff READY. Each failed check prints an actionable fix. Readiness now
includes the Python test/PDF-inspection packages and a working TeX engine
because executable tests and proof-note PDF creation are part of the
verification-first workflow. No physics constants are hardcoded; the only
literal is the minimum supported Python version (a tooling requirement, not a
result).
"""
__version__ = "1.3.0"
__first_issued__ = "2026-06-07"
__version_issued__ = "2026-07-24"

import importlib.util
import shutil
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
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / rel_args[0])] + rel_args[1:],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
    )
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    record(r.returncode == 0, label, tail if r.returncode == 0
           else f"FAILED -- run: python verification/scripts/{' '.join(rel_args)}")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="regenerate all generated surfaces (regen_all.py) before checking")
    a = ap.parse_args()
    if a.fix:
        subprocess.run([sys.executable, str(SCRIPTS / "regen_all.py")], cwd=str(REPO))
    print(f"TECT doctor -- workspace readiness ({REPO})")

    # 1. interpreter
    record(sys.version_info >= MIN_PY, "python-version",
           f"{sys.version_info.major}.{sys.version_info.minor} "
           f"(need >= {MIN_PY[0]}.{MIN_PY[1]})")

    # 2. Python dependencies for numerical, test, and PDF verification
    record(importlib.util.find_spec("numpy") is not None, "numpy",
           "import numpy OK" if importlib.util.find_spec("numpy")
           else "MISSING -- run: pip install -r requirements.txt")
    record(importlib.util.find_spec("pytest") is not None, "test-runtime",
           "import pytest OK" if importlib.util.find_spec("pytest")
           else "MISSING -- run: pip install -r requirements.txt")
    pdf_packages = ("pypdf", "pdfplumber", "reportlab")
    missing_pdf = [name for name in pdf_packages if importlib.util.find_spec(name) is None]
    record(not missing_pdf, "pdf-python-runtime",
           "pypdf, pdfplumber, and reportlab import OK" if not missing_pdf
           else f"MISSING {missing_pdf} -- run: pip install -r requirements.txt")

    # 3. canonical files present (resume needs these readable)
    needed = ["CLAUDE.md", "GOVERNANCE.md", "CLAIMS.md", "ROADMAP.md",
              "CHANGELOG.md", "TODO.md", "todo/todo.json",
              "negative-results/registry.md", "explorations/log.jsonl",
              "SESSION.md"]
    missing = [f for f in needed if not (REPO / f).exists()]
    record(not missing, "canonical-files",
           "all present" if not missing else f"MISSING: {missing}")

    # 4. legacy-constants module the numerical codes import (codes/vacuum/*)
    legacy = REPO / "archive" / "legacy" / "scripts" / "Math424_AddA_reading_uniqueness.py"
    record(legacy.exists(), "legacy-constants-module",
           "archive/legacy/scripts present (codes/ imports resolve)" if legacy.exists()
           else "MISSING archive/legacy/scripts -- copy the WHOLE folder, not just claims/")

    # 5. generated surfaces in sync with their sources (single source: gates.py)
    from gates import SYNC_GATES
    for label, args in SYNC_GATES:
        run_check(label + "-sync", args)

    # advisory: every current note should have a fresh PDF (enforced at commit by the watcher)
    rp = subprocess.run([sys.executable, str(SCRIPTS / "verify_note_pdfs.py"), "--check"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(REPO))
    record(True, "note-pdf (advisory)",
           "all current notes have fresh PDFs" if "NOTE-PDF: PASS" in rp.stdout
           else "missing/stale note PDFs -- run verify_note_pdfs.py --build")

    # 6. TeX engine required by the proof-note PDF verification workflow
    pdflatex = shutil.which("pdflatex")
    tectonic = shutil.which("tectonic")
    if not tectonic:
        sibling = Path(sys.executable).resolve().parent / "tectonic.exe"
        if sibling.exists():
            tectonic = str(sibling)
    engine = pdflatex or tectonic
    engine_name = "pdflatex" if pdflatex else "tectonic" if tectonic else None
    record(engine is not None, "tex-engine",
           f"{engine_name} present ({engine})" if engine
           else "MISSING -- install venv-local Tectonic or a pdflatex distribution")

    hard_fail = [n for ok, n, _ in results if not ok]
    print()
    if hard_fail:
        print(f"DOCTOR: NOT READY ({len(hard_fail)} issue(s): {', '.join(hard_fail)})")
        return 1
    print("DOCTOR: READY -- session-entry prelude (AGENTS.md section 1) can proceed; "
          "see SESSION.md to continue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
