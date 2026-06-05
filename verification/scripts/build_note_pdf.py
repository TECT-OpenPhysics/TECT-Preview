#!/usr/bin/env python3
"""build_note_pdf.py — validate a proof-note fragment, build its PDF beside it.

Usage:
    python verification/scripts/build_note_pdf.py claims/<ID>/notes/<note>.tex.txt
    python verification/scripts/build_note_pdf.py <note> --no-compile   # validate+wrap only

Pipeline (naming-and-versioning.md section 3, binding):
  1. VALIDATE the note's standard form — banner fields (% Title:, % Claim:,
     % Version: "vN.M -- first issued YYYY-MM-DD; this version issued
     YYYY-MM-DD", % Status:), mandatory sections ("Purpose and scope",
     "Devil's-advocate", "Result footer"), a verbatim footer block — and
     CROSS-CHECK the banner version/dates against the two-date filename.
     Any mismatch refuses the build (verification-first: metadata cannot
     drift from the filename).
  2. WRAP with verification/templates/note-preamble.tex; the title is the
     banner Title (never the filename); the date field shows
     "first issued D1 · this version issued D2 · vN.M"; the author line
     carries the primary claim ID.
  3. COMPILE in a TEMPORARY directory (two pdflatex passes); LaTeX
     intermediates never touch the repository.
  4. GATE on zero Overfull-hbox, then place the PDF NEXT TO ITS SOURCE
     (claims/<ID>/notes/<stem>.pdf). Only the current version's PDF is kept;
     superseded PDFs are removed on re-issue (sources remain, so any PDF is
     reproducible).

Changelog:
  1.0.0 (2026-06-05) first issue.
  1.0.1 (2026-06-05) decode pdflatex log with errors='replace'.
  1.0.2 (2026-06-05) Overfull-hbox count printed; nonzero fails.
  1.1.0 (2026-06-05) banner-driven title/date/claim; standard-form validation
        with filename cross-check; temp-dir compile; PDF placed beside source;
        build/ area retired.
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-06-05"

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PREAMBLE = REPO / "verification" / "templates" / "note-preamble.tex"

BANNER_VER = re.compile(
    r"%\s*Version:\s*v(\d+)\.(\d+)\s*--\s*first issued\s*(\d{4}-\d{2}-\d{2});\s*"
    r"this version issued\s*(\d{4}-\d{2}-\d{2})")
FILE_VER = re.compile(r"-(\d{6})(?:-(\d{6}))?-v(\d+)\.(\d+)\.tex\.txt$")
REQUIRED_SECTIONS = ["Purpose and scope", "Devil's-advocate", "Result footer"]


def banner_field(frag, key):
    m = re.search(rf"%\s*{key}:\s*(.+)", frag)
    return m.group(1).strip() if m else None


def iso(yymmdd):
    return f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"


def validate(src, frag):
    errs = []
    title = banner_field(frag, "Title")
    claim = banner_field(frag, "Claim")
    status = banner_field(frag, "Status")
    if not title:
        errs.append("banner field '% Title:' missing")
    if not claim:
        errs.append("banner field '% Claim:' missing")
    if not status:
        errs.append("banner field '% Status:' missing")
    mb = BANNER_VER.search(frag)
    if not mb:
        errs.append("banner '% Version: vN.M -- first issued ...; this version issued ...' missing/malformed")
    mf = FILE_VER.search(src.name)
    if not mf:
        errs.append("filename does not match <slug>-<YYMMDD>[-<YYMMDD>]-vN.M.tex.txt")
    if mb and mf:
        f_first, f_cur = iso(mf.group(1)), iso(mf.group(2) or mf.group(1))
        f_ver = f"{mf.group(3)}.{mf.group(4)}"
        b_ver = f"{mb.group(1)}.{mb.group(2)}"
        if b_ver != f_ver:
            errs.append(f"version mismatch: banner v{b_ver} vs filename v{f_ver}")
        if mb.group(3) != f_first:
            errs.append(f"first-issue date mismatch: banner {mb.group(3)} vs filename {f_first}")
        if mb.group(4) != f_cur:
            errs.append(f"version-issue date mismatch: banner {mb.group(4)} vs filename {f_cur}")
    for s in REQUIRED_SECTIONS:
        if s not in frag:
            errs.append(f"mandatory section missing: '{s}'")
    if "\\begin{verbatim}" not in frag:
        errs.append("result footer must sit in a verbatim block")
    return errs, title, claim, (mb.groups() if mb else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("note")
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()
    src = (REPO / args.note) if not Path(args.note).is_absolute() else Path(args.note)
    if not src.name.endswith(".tex.txt"):
        print(f"ERROR: expected a .tex.txt fragment, got {src.name}")
        return 1
    frag = src.read_text(encoding="utf-8")
    errs, title, claim, ver = validate(src, frag)
    if errs:
        print(f"FORM-CHECK: FAIL ({len(errs)})")
        for e in errs:
            print(f"  ERR {e}")
        return 1
    print("FORM-CHECK: PASS (banner fields, sections, footer, filename consistency)")

    vmaj, vmin, d_first, d_cur = ver
    date_line = f"first issued {d_first} \\,\\textperiodcentered\\, this version issued {d_cur} \\,\\textperiodcentered\\, v{vmaj}.{vmin}"
    claim_id = claim.split()[0].rstrip(";,")
    pre = PREAMBLE.read_text(encoding="utf-8")
    pre = pre.replace("%%TITLE%%", title).replace("%%DATE%%", date_line)
    pre = pre.replace("%%AUTHOR%%",
                      f"TECT verification-first repository \\,\\textperiodcentered\\, claim {claim_id}")
    doc = pre + "\n" + frag + "\n\\end{document}\n"
    stem = src.name[:-len(".tex.txt")]
    if args.no_compile:
        print("WRAP-ONLY: validated; no PDF requested")
        return 0
    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        print("pdflatex not found - install TeX (e.g. MiKTeX) and re-run")
        return 1
    with tempfile.TemporaryDirectory(prefix="tect-note-") as td:
        tex = Path(td) / f"{stem}.tex"
        tex.write_text(doc, encoding="utf-8")
        for _ in range(2):
            r = subprocess.run([pdflatex, "-interaction=nonstopmode", tex.name],
                               cwd=td, capture_output=True, text=True, errors="replace")
        pdf = Path(td) / f"{stem}.pdf"
        log = (Path(td) / f"{stem}.log").read_text(encoding="utf-8", errors="replace")
        n_over = log.count("Overfull \\hbox")
        if not pdf.exists() or r.returncode != 0:
            print("PDF build FAILED - tail of log:")
            print("\n".join(r.stdout.splitlines()[-15:]))
            return 1
        print(f"OVERFULL-HBOX: {n_over}" +
              ("" if n_over == 0 else "  <- fix per naming-and-versioning.md section 3"))
        if n_over:
            return 1
        dest = src.parent / f"{stem}.pdf"
        shutil.copyfile(pdf, dest)
        print(f"PDF: {dest.relative_to(REPO)} ({dest.stat().st_size//1024} KB) — intermediates discarded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
