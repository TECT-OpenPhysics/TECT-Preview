#!/usr/bin/env python3
"""verify_note_pdfs.py -- enforce that every CURRENT Math note has a fresh PDF.

A note (claims/**/notes/*.tex.txt) is CURRENT iff its first non-empty line is not
'% SUPERSEDED'. Every current note MUST have a sibling .pdf at least as new as its
source. This closes the recurring "forgot to build the PDF" / "PDF build timed out"
defect systemically (parallel to the generated-surface sync gates).

  --check            list current notes with missing/stale PDFs; warn (exit 0).
  --check --strict   exit 1 if any missing/stale AND pdflatex is available.
  --build            build all missing/stale PDFs (build_note_pdf.py per note);
                     exit 1 if any build genuinely fails.

Enforcement: commit_watcher.ps1 runs `--build` before every commit (operator-side,
no sandbox 44s timeout), so no note enters history without a fresh PDF. release_check
and doctor report missing PDFs as a warning. Governance: enforcement-spine.md.

Changelog:
  1.0.0 (2026-06-10) first issue. Note-PDF presence/freshness enforcement.
"""
__version__ = "1.0.0"

import argparse, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "verification" / "scripts"
SUF = ".tex.txt"


def current_notes():
    out = []
    for f in sorted((REPO / "claims").rglob("notes/*.tex.txt")):
        head = f.read_text(encoding="utf-8", errors="replace").lstrip()
        if head.startswith("% SUPERSEDED"):
            continue
        out.append(f)
    return out


def pdf_of(f):
    return f.parent / (f.name[:-len(SUF)] + ".pdf")


def state(f):
    p = pdf_of(f)
    if not p.exists():
        return "missing"
    if p.stat().st_mtime < f.stat().st_mtime:
        return "stale"
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    notes = current_notes()
    bad = [(f, state(f)) for f in notes if state(f) != "ok"]
    have_tex = shutil.which("pdflatex") is not None

    if a.build:
        built = failed = 0
        for f, st in bad:
            r = subprocess.run([sys.executable, str(SCRIPTS / "build_note_pdf.py"), str(f.relative_to(REPO))],
                               cwd=str(REPO), capture_output=True, text=True)
            if r.returncode == 0 and pdf_of(f).exists():
                built += 1; print(f"  built {f.relative_to(REPO)}")
            else:
                failed += 1; print(f"  FAILED {f.relative_to(REPO)} (build_note_pdf rc={r.returncode})")
        print(f"NOTE-PDF build: {built} built, {failed} failed, {len(notes)-len(bad)} already current")
        return 1 if failed else 0

    if not bad:
        print(f"NOTE-PDF: PASS ({len(notes)} current notes, all have fresh PDFs)")
        return 0
    print(f"NOTE-PDF: {len(bad)} current note(s) missing/stale PDF:")
    for f, st in bad:
        print(f"  {st:7s} {f.relative_to(REPO)}")
    if a.strict and have_tex:
        print("  STRICT + pdflatex present -> FAIL. Fix: python verification/scripts/verify_note_pdfs.py --build")
        return 1
    print("  (warning) build with: python verification/scripts/verify_note_pdfs.py --build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
