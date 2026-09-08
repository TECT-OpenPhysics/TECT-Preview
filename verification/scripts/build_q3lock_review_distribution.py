#!/usr/bin/env python3
"""Build a derived Q3LOCK review distribution, without promoting mathematics.

The original v0.1.38 sources and all historical results remain untouched.
--prepare captures the dependencies actually read by the integrated replay,
derives a presentation edition and creates a reviewer-guide PDF. Compile the
derived TeX separately, render both PDFs, then use --seal after visual review.
--self-test checks transformations, path safety and the exact A1-A23 inventory.
No network access, external transmission, Git mutation or proof certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
DEST = ROOT / "publish/review-packages/q3lock-v0138-r1"
INPUTS = DEST / "materials"
WORK = ROOT / "tmp/pdfs/q3lock-v0138-r1"
MATRIX = ROOT / "strategy/q3lock-independent-review-matrix-260907.md"
ORIGINAL = PAPER / "manuscript.tex"
REPLAY = "verification/scripts/q3lock_manuscript_integrated_replay.py"
SCOPE = {"result_id": "R-497", "tier": "T0", "claim_bearing": False,
         "mathematics_review": "OPEN", "literature_review": "OPEN",
         "submission": "NOT_AUTHORIZED"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def write_json(path, payload):
    write_text(path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def safe_relative(path):
    path = Path(path).resolve()
    relative = path.relative_to(ROOT.resolve())
    if any(part in {"internal", ".git", ".venv", "tmp", "__pycache__"}
           for part in relative.parts):
        raise ValueError("Private or transient source refused: " + str(relative))
    return relative.as_posix()


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError("Presentation replacement must match exactly once: " + before[:70])
    return text.replace(before, after, 1)


def review_tex(original):
    text = original
    changes = [
        ("% PDF generation is intentionally deferred until content review, final\n"
         "% organization, hash capture, and signed external review are complete.",
         "% Derived external-review edition authorized on 2026-09-08.\n"
         "% Original scientific source and pre-distribution audit bytes are preserved."),
        (r"\date{Draft v0.1.38 -- internal content review -- 2026-09-08}",
         r"\date{Review edition v0.1.38-r1 -- 2026-09-08}"),
        ("The result is currently an internal\nmanuscript-content draft at tier T0 (R-497).",
         "This is an external-review edition of a conditional\nmanuscript at research tier T0 (R-497)."),
        ("PDF generation and submission are\ndeliberately deferred until those gates are complete.",
         "This PDF is supplied for critical external review;\n"
         "its production does not discharge those gates or authorize submission."),
        (r"\item no submission, upload, release tag, or PDF before the gates in" + "\n"
         r"      Section~\ref{sec:readiness} are discharged.",
         r"\item no submission, upload, or release tag is authorized by this" + "\n"
         r"      review PDF; see Section~\ref{sec:readiness}."),
        (r"\item only then, compilation and visual inspection of the final PDF.",
         r"\item after any resulting revision, rebuild and visually inspect the" + "\n"
         r"      final submission PDF. This earlier review PDF is not that approval."),
        ("Until\nthey are discharged, the scientifically correct description is\n"
         r"\textit{conditional internal manuscript content, independently reviewable," + "\n"
         "PDF deferred}.",
         "The operator authorized this review edition on 2026-09-08 to enable\n"
         "external assessment before those gates close. The correct description is\n"
         r"\textit{conditional manuscript supplied for independent review;" + "\n"
         "external acceptance and final submission remain open}."),
    ]
    for old, new in changes:
        text = replace_once(text, old, new)
    text = replace_once(text, r"\usepackage[a4paper,margin=1in]{geometry}",
                        r"\usepackage[a4paper,margin=0.8in]{geometry}")
    # Presentation-only layout controls; formulas and proof paragraphs unchanged.
    text = replace_once(text, r"\usepackage{hyperref}",
                        r"\usepackage{microtype}" + "\n" +
                        r"\usepackage{hyperref}" + "\n" +
                        r"\emergencystretch=2em" + "\n" +
                        r"\allowdisplaybreaks[2]")
    # The model through the entire proof/crosswalk body is byte-identical after
    # newline normalization. Status and layout changes live outside this region.
    start = r"\section{Model, notation, and normalization}"
    if start not in original:
        start = original[original.index(r"\section", original.index(r"\section") + 1):].splitlines()[0]
    end = r"\section{Readiness gates and conclusion}"
    before_body = original[original.index(start):original.index(end)]
    after_body = text[text.index(start):text.index(end)]
    if before_body != after_body:
        raise ValueError("Scientific body changed during presentation transformation")
    return text, {"replacements": len(changes), "science_start": start,
                  "science_end": end,
                  "scientific_body_sha256": hashlib.sha256(before_body.encode()).hexdigest(),
                  "scientific_body_unchanged": True}


def rows():
    result = []
    for line in MATRIX.read_text(encoding="utf-8").splitlines():
        if re.match(r"\| A\d+ \|", line):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 4:
                raise ValueError("Unexpected review row shape")
            result.append(cells)
    if [row[0] for row in result] != [f"A{i}" for i in range(1, 24)]:
        raise ValueError("Incomplete or duplicated A1-A23 matrix")
    return result


def ascii_text(value):
    for a, b in {"--": "-", "\u2014": " - ", "\u2013": "-",
                 "\u2019": "'", "\u2018": "'", "\u201c": '"',
                 "\u201d": '"', "\u03b2": "beta", "\u03bd": "nu",
                 "\u2192": " -> "}.items():
        value = value.replace(a, b)
    return value.replace("`", "")


def build_guide():
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="GuideBody", fontName="Helvetica", fontSize=10,
                             leading=14.5, spaceAfter=8, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="GuideSmall", parent=styles["GuideBody"],
                             fontSize=8.5, leading=12, textColor=colors.HexColor("#39495a")))
    styles["Title"].fontSize = 23
    styles["Title"].leading = 28
    styles["Title"].textColor = colors.HexColor("#173653")
    story = []
    paragraphs = (INPUTS / "reviewer-guide.md").read_text(encoding="utf-8").split("\n\n")
    for paragraph in paragraphs:
        if paragraph.startswith("# "):
            story.append(Paragraph(escape(paragraph[2:]), styles["Title"]))
            story.append(Paragraph("Review distribution q3lock-v0138-r1 | 8 September 2026", styles["GuideSmall"]))
            story.append(Spacer(1, 15))
        elif paragraph.startswith("## "):
            if paragraph[3:].strip() == "Efficient reading route":
                story.append(PageBreak())
            story.append(Paragraph(escape(paragraph[3:]), styles["Heading2"]))
        else:
            story.append(Paragraph(escape(ascii_text(paragraph.replace("\n", " "))), styles["GuideBody"]))
    story.append(PageBreak())
    story.append(Paragraph("A1-A23: load-bearing review cards", styles["Title"]))
    for ident, question, locator, decision in rows():
        # Full exact paths stay in the editable matrix; display labels are
        # shortened only for print legibility, never changed in the sources.
        labels = re.findall(r"manuscript\.tex#([^`, ]+)", locator)
        cards = [Paragraph(ident + " | OPEN", styles["Heading2"]),
                 Paragraph(escape(ascii_text(question)), styles["GuideBody"]),
                 Paragraph("Review: " + escape(ascii_text(decision)), styles["GuideBody"])]
        if labels:
            cards.append(Paragraph("Manuscript labels: " + escape(", ".join(labels)), styles["GuideSmall"]))
        cards.append(Spacer(1, 12))
        story.append(KeepTogether(cards))
    story.append(PageBreak())
    story.append(Paragraph("Decision sheet and next steps", styles["Title"]))
    for heading, body in [
        ("Identify the snapshot", "Give distribution ID, manuscript PDF hash, original source hash, date and reviewer attribution. The editable review-response.md contains all fields."),
        ("Keep dispositions separate", "Report mathematics and literature separately. Record PASS, PASS WITH REPAIR, FAIL or NOT REVIEWED for every reviewed row, with equation numbers and downstream consequences."),
        ("No default acceptance", "Every blank or unreviewed row stays open. A compilation, manifest check or successful finite replay is not an analytic or literature review."),
        ("Return actionable criticism", "Provide an explicit replacement statement, missing estimate or exact subsuming theorem. State uncertainty and coverage limits. Negative or partial findings are welcome."),
        ("Submission remains author-controlled", "The cover letter is an unsent template. Author declarations, target journal, current journal requirements and final approval remain unresolved. No transmission occurs as part of this package."),
    ]:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(body, styles["GuideBody"]))

    def footer(canvas, doc):
        canvas.setTitle("Q3LOCK independent-review guide")
        canvas.setAuthor("Jusang Lee")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#536475"))
        canvas.drawString(48, 26, "Q3LOCK v0.1.38-r1 | External review requested; acceptance open")
        canvas.drawRightString(A4[0] - 48, 26, str(doc.page))
    def stable_canvas(*args, **kwargs):
        kwargs["invariant"] = 1
        return Canvas(*args, **kwargs)

    SimpleDocTemplate(str(DEST / "reviewer-guide.pdf"), pagesize=A4,
                      leftMargin=48, rightMargin=48, topMargin=45, bottomMargin=48).build(
                          story, onFirstPage=footer, onLaterPages=footer, canvasmaker=stable_canvas)


def prepare():
    if (DEST / "MANIFEST.json").exists():
        raise ValueError("Sealed distribution is immutable; select a new release ID")
    DEST.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    original_hash = digest(ORIGINAL)
    original = ORIGINAL.read_text(encoding="utf-8")
    derived, transformation = review_tex(original)
    write_text(DEST / "manuscript.tex", derived)
    source_files = set()
    collecting = [True]

    def audit(event, args):
        if collecting[0] and event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                path = Path(os.fsdecode(args[0])).resolve()
                relative = safe_relative(path)
                if path.is_file() and path.suffix not in {".pyc", ".pdf"}:
                    source_files.add(relative)
            except (ValueError, OSError):
                pass
    sys.addaudithook(audit)
    module = runpy.run_path(str(ROOT / REPLAY), run_name="review_distribution_replay")
    payload = module["build_payload"]()
    module["read_json"](module["DEFAULT_OUTPUT"])
    child = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py"
    runpy.run_path(str(child), run_name="review_child_dependency_capture")["build_payload"]()
    collecting[0] = False
    if payload.get("status") != "PASS":
        raise ValueError("Original integrated replay failed")
    for path in PAPER.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".tex", ".json", ".txt", ".py"}:
            source_files.add(safe_relative(path))
    for path in (ROOT / "strategy").glob("q3lock-*"):
        if path.is_file() and path.suffix in {".md", ".json"}:
            source_files.add(safe_relative(path))
    # Include every current replay entrypoint and its exact expected artifacts.
    for path in (ROOT / "verification/scripts").glob("q3lock*.py"):
        if path.name != Path(__file__).name:
            source_files.add(safe_relative(path))
    source_files.add(safe_relative(Path(__file__)))
    source_files.add("claims/C6-SPACETIME-SIGNATURE/status.json")
    for path in (ROOT / "verification/tests").glob("test_q3lock*.py"):
        source_files.add(safe_relative(path))
    snapshot = WORK / "research-snapshot"
    for relative in sorted(source_files):
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    for name in ("review-request-email.txt", "submission-cover-letter.txt",
                 "submission-checklist.md", "review-response.md"):
        shutil.copyfile(INPUTS / name, DEST / name)
    build_guide()
    if digest(ORIGINAL) != original_hash:
        raise ValueError("Original manuscript changed during build")
    import sympy
    report = {"distribution": DEST.name, "scope": SCOPE,
              "original_manuscript_sha256": original_hash,
              "derived_manuscript_sha256": digest(DEST / "manuscript.tex"),
              "transformation": transformation,
              "snapshot_files": {p: digest(ROOT / p) for p in sorted(source_files)},
              "preparation_python": sys.version, "sympy": sympy.__version__,
              "original_integrated_replay": "PASS",
              "snapshot_replay": "NOT_RUN", "visual_review": "NOT_RUN"}
    write_json(DEST / "build-report.json", report)
    print("PREPARED", DEST, "snapshot files", len(source_files))


VERIFY_CODE = '''"""Verify file bytes, not the mathematical theorem. Python standard library only."""
from pathlib import Path
import hashlib, json, sys
root = Path(__file__).resolve().parent
m = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
for name, expected in m["files"].items():
    p = (root / name).resolve()
    if not p.is_relative_to(root) or not p.is_file():
        raise SystemExit("FAIL missing/unsafe member: " + name)
    if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
        raise SystemExit("FAIL changed member: " + name)
print("PASS", len(m["files"]), "file hashes; mathematics and literature review remain OPEN")
'''


def seal():
    from pypdf import PdfReader
    if (DEST / "MANIFEST.json").exists():
        raise ValueError("Distribution already sealed; use --check")
    report = json.loads((DEST / "build-report.json").read_text(encoding="utf-8"))
    if report["original_manuscript_sha256"] != digest(ORIGINAL):
        raise ValueError("Original source changed")
    if report["derived_manuscript_sha256"] != digest(DEST / "manuscript.tex"):
        raise ValueError("Derived typesetting source changed")
    for relative, expected in report["snapshot_files"].items():
        if digest(WORK / "research-snapshot" / relative) != expected:
            raise ValueError("Snapshot member changed: " + relative)
    review = json.loads((DEST / "render-review.json").read_text(encoding="utf-8"))
    if review["compiled_source_sha256"] != report["derived_manuscript_sha256"]:
        raise ValueError("Visual review is bound to a different TeX source")
    for filename in ("manuscript.pdf", "reviewer-guide.pdf"):
        n = len(PdfReader(DEST / filename).pages)
        row = review["documents"][filename]
        if row["sha256"] != digest(DEST / filename) or row["reviewed_pages"] != list(range(1, n + 1)):
            raise ValueError("Missing or stale all-page visual review: " + filename)
        if row["disposition"] != "PASS":
            raise ValueError("Visual defects not resolved")
    snapshot_run = subprocess.run([sys.executable, "-X", "utf8", REPLAY, "--check"],
                                  cwd=WORK / "research-snapshot", capture_output=True, text=True)
    if snapshot_run.returncode:
        print(snapshot_run.stdout, snapshot_run.stderr)
        raise ValueError("Extracted research snapshot replay failed")
    portable_output = snapshot_run.stdout.strip().replace(str(WORK / "research-snapshot"), "research-snapshot")
    report["snapshot_replay"] = {"status": "PASS", "output": portable_output,
                                  "python": sys.version, "git_metadata_included": False}
    report["visual_review"] = "PASS; see render-review.json"
    write_json(DEST / "build-report.json", report)
    write_text(DEST / "verify-package.py", VERIFY_CODE)
    write_text(DEST / "README.txt", "Q3LOCK v0.1.38-r1 - external review distribution\n\n"
               "START: manuscript.pdf and reviewer-guide.pdf. Return review-response.md.\n"
               "Email and submission cover letter are UNSENT drafts. No journal selected.\n"
               "R-497 remains T0/non-claim-bearing; math and literature acceptance OPEN.\n\n"
               "VERIFY (Python standard library): python verify-package.py\n"
               "REPLAY: cd research-snapshot\n"
               "python -X utf8 verification/scripts/q3lock_manuscript_integrated_replay.py --check\n"
               "Use Python 3.12 with SymPy as recorded in build-report.json.\n"
               "No Git/TeX/network is needed for this finite diagnostic replay.\n"
               "Historical PDF-DEFERRED notices belong to the original research snapshot;\n"
               "the 2026-09-08 operator authorization permits this derived review PDF only.\n"
               "BUILD manuscript: pdflatex -no-shell-escape -interaction=nonstopmode\n"
               "-halt-on-error manuscript.tex (repeat until references stabilize).\n"
               "The compiler and visual checks are recorded in render-review.json.\n"
               "Fonts/engine may change PDF bytes; the delivered hashes identify this edition.\n"
               "No external source PDFs, local secrets or Git metadata are redistributed.\n")
    files = {p.relative_to(DEST).as_posix(): digest(p) for p in sorted(DEST.rglob("*"))
             if p.is_file() and p.name not in {"MANIFEST.json", "archive-sha256.txt"}}
    for relative, expected in report["snapshot_files"].items():
        files["research-snapshot/" + relative] = expected
    manifest = {"schema": "tect/q3lock-review-distribution/1.0", "distribution": DEST.name,
                "scope": SCOPE, "files": files,
                "manifest_self_hash": "Excluded to avoid circular self-hashing; archive hash is separate."}
    write_json(DEST / "MANIFEST.json", manifest)
    archive = DEST.parent / (DEST.name + ".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            source = WORK / name if name.startswith("research-snapshot/") else DEST / name
            z.write(source, name)
        z.write(DEST / "MANIFEST.json", "MANIFEST.json")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or len(z.namelist()) != len(files) + 1:
            raise ValueError("Archive inventory mismatch")
        for name, expected in files.items():
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise ValueError("Archive byte mismatch: " + name)
    write_text(DEST / "archive-sha256.txt", digest(archive) + "  " + archive.name + "\n")
    print("SEALED", archive, "members", len(files) + 1, "bytes", archive.stat().st_size)


def self_test():
    original = ORIGINAL.read_text(encoding="utf-8")
    derived, proof = review_tex(original)
    assert proof["scientific_body_unchanged"]
    assert derived != original and "PDF deferred" not in derived
    assert len(rows()) == 23
    try:
        replace_once("twice twice", "twice", "once")
    except ValueError:
        pass
    else:
        raise AssertionError("Ambiguous replacement accepted")
    # Synthetic component-wise fixtures, not citations to any private file.
    private_component, temporary_component = "internal", "tmp"
    for path in (ROOT / private_component / "private.txt",
                 ROOT / temporary_component / "private.txt", ROOT.parent / "escape.txt"):
        try:
            safe_relative(path)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe snapshot path accepted")
    assert SCOPE["claim_bearing"] is False and SCOPE["tier"] == "T0"
    compile(VERIFY_CODE, "verify-package.py", "exec")
    print("PASS presentation/body invariance, A1-A23 inventory, ambiguous replacement, private/path escape, scope, verifier syntax")


def main():
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--guide", action="store_true")
    group.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.guide:
        build_guide()
    elif args.seal:
        seal()
    else:
        self_test()


if __name__ == "__main__":
    main()
