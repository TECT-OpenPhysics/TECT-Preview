#!/usr/bin/env python3
"""Prepare, QA and seal the author-authorized Q3LOCK submission edition.

Source mathematics and old artifacts are immutable inputs. This script is a
packaging tool, not an analytic theorem prover. Use --prepare --work ABSENT_DIR,
compile the derived manuscript with untrusted TeX, --qa --work SAME_DIR,
visually inspect every rendered page and author render-review.json, then
--seal --work SAME_DIR. --self-test and --check are read-only.
No network, email, submission, Git mutation or scientific promotion.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import runpy
import subprocess
import sys
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
DEST = ROOT / "publish/submission-packages/q3lock/submission-v0138-s1"
OLD = ROOT / "publish/review-packages/q3lock-v0138-r1"
REPLAY = "verification/scripts/q3lock_manuscript_integrated_replay.py"
LEGACY_BUILDER = ROOT / "verification/scripts/build_q3lock_review_distribution.py"
SCOPE = {"result_id": "R-497", "tier": "T0", "claim_bearing": False,
         "mathematics_review": "NOT_PERFORMED", "literature_review": "NOT_PERFORMED",
         "external_review_required_for_packaging": False,
         "actual_submission": "NOT_AUTHORIZED_NOT_PERFORMED"}
SCIENCE_START = r"\section{The exact Q3LOCK model and conventions}"
SCIENCE_END = r"\section{Readiness gates and conclusion}"
SUPPLEMENTS = ("proof-audit.md", "imported-source-ledger.md",
               "theorem-applicability-audit.md", "literature-crosswalk.md",
               "literature-qps-addendum.md", "claims-cited.md",
               "external-review-handoff.md")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_hash(path):
    return digest(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_text(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def require_unsealed():
    if (DEST / "MANIFEST.json").exists():
        raise ValueError("Sealed edition is immutable; use --check or a new edition")


def safe_member(name):
    p = PurePosixPath(name)
    if (not name or "\\" in name or ":" in name or p.is_absolute()
            or any(x in {"..", ".git", ".venv", "__pycache__", "internal", "tmp"}
                   for x in p.parts) or p.as_posix() != name):
        raise ValueError("Unsafe archive member: " + name)
    return p


def same_science(original, candidate):
    for marker in (SCIENCE_START, SCIENCE_END, r"\begin{thebibliography}{99}",
                   r"\end{thebibliography}"):
        if original.count(marker) != 1 or candidate.count(marker) != 1:
            raise ValueError("Missing/duplicated region marker: " + marker)
    body = original.split(SCIENCE_START, 1)[1].split(SCIENCE_END, 1)[0]
    other = candidate.split(SCIENCE_START, 1)[1].split(SCIENCE_END, 1)[0]
    bib = original.split(r"\begin{thebibliography}{99}", 1)[1].split(r"\end{thebibliography}", 1)[0]
    other_bib = candidate.split(r"\begin{thebibliography}{99}", 1)[1].split(r"\end{thebibliography}", 1)[0]
    if body != other or bib != other_bib:
        raise ValueError("Scientific body or bibliography changed")
    return {"scientific_body_unchanged": True, "bibliography_unchanged": True,
            "scientific_body_sha256": digest(body.encode()),
            "bibliography_sha256": digest(bib.encode()),
            "comparison": "Exact Unicode equality after newline normalization; no field filtering"}


def submission_tex(original):
    legacy = runpy.run_path(str(LEGACY_BUILDER), run_name="q3_submission_source")
    text, _ = legacy["review_tex"](original)
    once = legacy["replace_once"]
    text = once(text, "% Derived external-review edition authorized on 2026-09-08.",
                "% Derived submission-preparation edition authorized on 2026-09-09.")
    text = once(text, r"\date{Review edition v0.1.38-r1 -- 2026-09-08}",
                r"\date{Submission-preparation edition v0.1.38-s1 -- 2026-09-09}")
    start = text.index("This is an external-review edition of a conditional")
    end = text.index(r"\end{abstract}", start)
    text = text[:start] + r"""This submission-preparation edition retains the conditional theorem and
its explicit analytic hypotheses. Internal argument review and finite
diagnostic replay are not independent external mathematical or specialist
novelty review; neither external review has been obtained. No claim is made
about a ground-state gap, real-time KMS dynamics, a continuum limit, a
physical vacuum, cosmology, or closure of a broader physical theory.
""" + text[end:]
    text = once(text,
        "as a conditional composition while the model-specific arguments and their\n"
        "source applicability are subjected to line-by-line independent review.",
        "as a conditional composition. The model-specific arguments and source\n"
        "applicability have undergone internal AI-assisted review; independent\n"
        "external mathematical and specialist novelty reviews have not been obtained.\n"
        "The author has requested preparation for submission without making those\n"
        "external reviews prerequisites for producing the package.")
    start = text.index(SCIENCE_END)
    end = text.index(r"\begin{thebibliography}{99}", start)
    text = text[:start] + r"""\section{Readiness gates and conclusion}
\label{sec:readiness}

This edition is a submission-preparation candidate, not a record of submission
or editorial acceptance. On 9 September 2026 the author requested completion
of the package without obtaining external reviewers first. That instruction
changes a packaging prerequisite; it does not establish any analytic
hypothesis, sign an audit row, or promote R-497 from its research status.
The conditional main theorem and all nonclaims remain unchanged.

The delivered package identifies the frozen source and output bytes, includes
an executable bounded research snapshot, and records the actual replay and
all-page PDF inspection. Its \texttt{build-report.json},
\texttt{render-review.json}, and \texttt{MANIFEST.json} distinguish these
mechanical checks from mathematical acceptance. Historical audit documents
retain their earlier signed-review and PDF-deferral language as provenance;
the current packaging contract is the accompanying \texttt{README.md}.

Independent mathematical and specialist novelty reviews have not been
performed. They remain valuable, including during journal refereeing, but are
not represented as completed and are not prerequisites for preparing this
edition. An internally checked conditional manuscript may still require
mathematical correction or be subsumed by prior work.

Before actual transmission the author must choose a journal, check its current
requirements, confirm author metadata and declarations, approve the exact
files, and authorize submission. No journal-specific compliance, originality,
exclusive-submission, funding or competing-interest declaration is inferred.
The cover letter and author-confirmation checklist accompany the package.
AI tools assisted drafting, internal checking, diagnostic orchestration and
typesetting; this assistance is not independent external peer review. Any
journal-specific responsibility and disclosure statement requires author
confirmation.

The mathematical source and finite verification material are included for
evaluation. No experimental dataset is asserted and no new licence is assigned
by this package. Any subsequent mathematical repair must receive a new
research checkpoint, replay, PDF inspection and package identity. The present
work is thus a precisely scoped conditional phase-coexistence manuscript,
prepared for an author-controlled submission decision, not a certification
of a physical theory or a guarantee of publication.

""" + text[end:]
    return text, same_science(original, text)


def old_inventory():
    archive = OLD.with_suffix(".zip")
    expected = (OLD / "archive-sha256.txt").read_text().split()[0]
    if file_hash(archive) != expected:
        raise ValueError("Prior archive SHA mismatch")
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate prior archive member")
        for name in names:
            safe_member(name)
        manifest = json.loads(z.read("MANIFEST.json"))
        if set(names) != set(manifest["files"]) | {"MANIFEST.json"}:
            raise ValueError("Unexpected prior archive inventory")
        for name, expected in manifest["files"].items():
            if digest(z.read(name)) != expected:
                raise ValueError("Prior member mismatch: " + name)
    return archive, manifest


def build_guide():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.pdfgen.canvas import Canvas
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BriefBody", fontName="Helvetica", fontSize=10,
                             leading=14, spaceAfter=9))
    styles["Heading2"].keepWithNext = True
    story = []
    for para in (DEST / "submission-guide.md").read_text(encoding="utf-8").split("\n\n"):
        para = para.strip()
        if not para:
            continue
        style = "BriefBody"
        if para.startswith("# "):
            para, style = para[2:], "Title"
        elif para.startswith("## "):
            para, style = para[3:], "Heading2"
            if para == "What is frozen and what is reproduced":
                story.append(PageBreak())
        story.append(Paragraph(escape(para.replace("\n", " ")), styles[style]))
        if style == "Title":
            story.append(Spacer(1, 10))

    def footer(canvas, doc):
        canvas.setTitle("Q3LOCK submission-preparation guide v0.1.38-s1")
        canvas.setAuthor("Jusang Lee")
        canvas.setFont("Helvetica", 8)
        canvas.drawString(48, 26, "Q3LOCK s1 | External review not performed | Submission not sent")
        canvas.drawRightString(A4[0] - 48, 26, str(doc.page))

    def stable(*a, **kw):
        kw["invariant"] = 1
        return Canvas(*a, **kw)

    SimpleDocTemplate(str(DEST / "submission-guide.pdf"), pagesize=A4,
                      leftMargin=48, rightMargin=48, topMargin=44, bottomMargin=48).build(
                          story, onFirstPage=footer, onLaterPages=footer, canvasmaker=stable)


def replay(snapshot):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    run = subprocess.run([sys.executable, "-X", "utf8", REPLAY, "--check"],
                         cwd=snapshot, env=env, capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        raise ValueError("Snapshot replay failed:\n" + run.stdout + run.stderr)
    return {"status": "PASS", "command": "python -X utf8 " + REPLAY + " --check",
            "stdout": run.stdout.replace(str(snapshot), "research-snapshot").strip(),
            "returncode": run.returncode}


def prepare(work):
    require_unsealed()
    work = work.resolve()
    if work.exists():
        raise ValueError("Use an absent scratch directory; prior snapshots are retained")
    archive, manifest = old_inventory()
    original = (PAPER / "manuscript.tex").read_text(encoding="utf-8")
    old_report = read_json(OLD / "build-report.json")
    if file_hash(PAPER / "manuscript.tex") != old_report["original_manuscript_sha256"]:
        raise ValueError("Research manuscript changed since the reviewed edition")
    candidate, science = submission_tex(original)
    snapshot_files = {n: h for n, h in manifest["files"].items()
                      if n.startswith("research-snapshot/")}
    work.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        for name in sorted(snapshot_files):
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(z.read(name))
    snapshot = work / "research-snapshot"
    checks = replay(snapshot)
    for name, expected in snapshot_files.items():
        if file_hash(work / name) != expected:
            raise ValueError("Replay mutated its snapshot: " + name)
    write_text(DEST / "manuscript.tex", candidate)
    for name in SUPPLEMENTS:
        source = snapshot / PAPER.relative_to(ROOT) / name
        (DEST / "supplement").mkdir(exist_ok=True)
        (DEST / "supplement" / name).write_bytes(source.read_bytes())
    (DEST / "supplement" / "review-response.md").write_bytes((OLD / "review-response.md").read_bytes())
    build_guide()
    import sympy
    report = {"schema": "tect/q3lock-submission-build/1.0", "edition": DEST.name,
              "scope": SCOPE, "package_state": "PREPARED_AWAITING_PDF_QA_AND_SEAL",
              "old_archive_sha256": file_hash(archive),
              "original_manuscript_sha256": file_hash(PAPER / "manuscript.tex"),
              "submission_manuscript_sha256": file_hash(DEST / "manuscript.tex"),
              "science_comparison": science, "snapshot_files": snapshot_files,
              "snapshot_replay": checks, "python": sys.version, "sympy": sympy.__version__,
              "external_source_pdfs_included": False, "git_metadata_included": False}
    write_json(DEST / "build-report.json", report)
    print("PREPARED", DEST, "snapshot files", len(snapshot_files))
    print(checks["stdout"])


def qa(work, poppler):
    require_unsealed()
    import pdfplumber
    from PIL import Image, ImageDraw
    results = {}
    for name in ("manuscript", "submission-guide"):
        folder = work / "render" / name
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(poppler), "-r", "110", "-png", str(DEST / (name + ".pdf")),
                        str(folder / "page")], check=True, capture_output=True)
        images = sorted(folder.glob("page-*.png"))
        pages = []
        with pdfplumber.open(DEST / (name + ".pdf")) as pdf:
            if len(images) != len(pdf.pages):
                raise ValueError("Rendered page count mismatch")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                outside = [c for c in page.chars if c["x0"] < -.5 or c["x1"] > page.width+.5
                           or c["top"] < -.5 or c["bottom"] > page.height+.5]
                if not text.strip() or "??" in text or outside:
                    raise ValueError(f"PDF text/geometry defect: {name} page {i+1}")
                pages.append({"page": i+1, "characters": len(page.chars),
                              "render_sha256": file_hash(images[i]), "off_page_glyphs": 0})
        for offset in range(0, len(images), 2):
            pair = [Image.open(p).convert("RGB") for p in images[offset:offset+2]]
            sheet = Image.new("RGB", (sum(im.width for im in pair), max(im.height for im in pair)+24), "#ddd")
            draw = ImageDraw.Draw(sheet)
            x = 0
            for i, im in enumerate(pair):
                draw.text((x+8, 5), f"{name} page {offset+i+1}", fill="black")
                sheet.paste(im, (x, 24))
                x += im.width
                im.close()
            sheet.save(folder / f"spread-{offset//2+1:02d}.jpg", quality=90)
        results[name + ".pdf"] = {"sha256": file_hash(DEST / (name + ".pdf")),
                                  "pages": len(pages), "page_checks": pages}
    write_json(DEST / "pdf-qa.json", {"status": "PASS", "documents": results,
                                    "scope": "Mechanical layout checks; visual verdict not assigned"})
    print("QA PASS", {n: row["pages"] for n, row in results.items()})


VERIFY = '''"""Integrity and declared scope only, not mathematical acceptance."""
from pathlib import Path, PurePosixPath
import hashlib, json
root = Path(__file__).resolve().parent
m = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
scope = m["scope"]
if scope != EXPECTED_SCOPE:
    raise SystemExit("FAIL: declared scientific/review scope changed")
for name, expected in m["files"].items():
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\\\" in name or ":" in name:
        raise SystemExit("FAIL unsafe member: " + name)
    target = (root / name).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise SystemExit("FAIL missing/unsafe member: " + name)
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise SystemExit("FAIL changed member: " + name)
print("PASS", len(m["files"]), "file hashes; external review NOT PERFORMED")
'''.replace("EXPECTED_SCOPE", repr(SCOPE))


def validate_review(report, review, qa_report):
    if review["compiled_source_sha256"] != report["submission_manuscript_sha256"]:
        raise ValueError("Stale compiled source")
    if review.get("external_review") != "NOT_PERFORMED":
        raise ValueError("False external-review disposition")
    for name, row in qa_report["documents"].items():
        visual = review["documents"][name]
        if (visual["sha256"] != row["sha256"] or visual["disposition"] != "PASS"
                or visual["reviewed_pages"] != list(range(1, row["pages"]+1))):
            raise ValueError("Missing, failed or stale all-page visual review")


def seal(work):
    require_unsealed()
    report = read_json(DEST / "build-report.json")
    review = read_json(DEST / "render-review.json")
    qa_report = read_json(DEST / "pdf-qa.json")
    validate_review(report, review, qa_report)
    if report["scope"] != SCOPE:
        raise ValueError("Scope changed")
    if file_hash(DEST / "manuscript.tex") != report["submission_manuscript_sha256"]:
        raise ValueError("Submission source changed")
    if file_hash(PAPER / "manuscript.tex") != report["original_manuscript_sha256"]:
        raise ValueError("Original source changed")
    same_science((PAPER / "manuscript.tex").read_text(encoding="utf-8"),
                 (DEST / "manuscript.tex").read_text(encoding="utf-8"))
    for name, row in qa_report["documents"].items():
        if file_hash(DEST / name) != row["sha256"]:
            raise ValueError("PDF changed after QA")
    snapshot = work / "research-snapshot"
    report["final_snapshot_replay"] = replay(snapshot)
    for name, expected in report["snapshot_files"].items():
        if file_hash(work / name) != expected:
            raise ValueError("Snapshot changed: " + name)
    report["package_state"] = "SEALED_SUBMISSION_PREPARATION_NO_EXTERNAL_REVIEW"
    write_json(DEST / "build-report.json", report)
    write_text(DEST / "verify-package.py", VERIFY)
    (DEST / "build-package.py").write_bytes(Path(__file__).read_bytes())
    files = {p.relative_to(DEST).as_posix(): file_hash(p)
             for p in sorted(DEST.rglob("*"), key=lambda p: p.as_posix())
             if p.is_file() and p.name not in {"MANIFEST.json", "archive-sha256.txt"}}
    files.update(report["snapshot_files"])
    for name in files:
        safe_member(name)
    manifest = {"schema": "tect/q3lock-submission-package/1.0", "edition": DEST.name,
                "scope": SCOPE, "files": files,
                "status": report["package_state"],
                "excluded_from_self_hash": ["MANIFEST.json", "archive-sha256.txt"]}
    write_json(DEST / "MANIFEST.json", manifest)
    archive = DEST.with_suffix(".zip")
    if archive.exists():
        raise ValueError("Existing archive refused")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            path = work / name if name.startswith("research-snapshot/") else DEST / name
            z.write(path, name)
        z.write(DEST / "MANIFEST.json", "MANIFEST.json")
    write_text(DEST / "archive-sha256.txt", file_hash(archive) + "  " + archive.name + "\n")
    check()
    print("SEALED", archive, "bytes", archive.stat().st_size)


def check():
    manifest = read_json(DEST / "MANIFEST.json")
    if manifest["scope"] != SCOPE:
        raise ValueError("Scope mismatch")
    archive = DEST.with_suffix(".zip")
    if file_hash(archive) != (DEST / "archive-sha256.txt").read_text().split()[0]:
        raise ValueError("Archive hash mismatch")
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("Duplicate member")
        if set(z.namelist()) != set(manifest["files"]) | {"MANIFEST.json"}:
            raise ValueError("Archive member mismatch")
        if z.read("MANIFEST.json") != (DEST / "MANIFEST.json").read_bytes():
            raise ValueError("Archive manifest differs")
        for name, expected in manifest["files"].items():
            safe_member(name)
            if digest(z.read(name)) != expected:
                raise ValueError("Archive member hash mismatch: " + name)
            if not name.startswith("research-snapshot/") and file_hash(DEST / name) != expected:
                raise ValueError("Delivered member changed: " + name)
    print("PACKAGE CHECK PASS", len(manifest["files"]), "file hashes; external review NOT PERFORMED")


def self_test():
    original = (PAPER / "manuscript.tex").read_text(encoding="utf-8")
    candidate, equality = submission_tex(original)
    assert equality["scientific_body_unchanged"] and equality["bibliography_unchanged"]
    assert "PDF deferred" not in candidate and "not been obtained" in candidate
    mutations = [candidate.replace(r"\frac r2S_y", r"\frac r3S_y", 1),
                 candidate.replace(SCIENCE_START, "missing", 1)]
    for mutant in mutations:
        assert mutant != candidate
        try:
            same_science(original, mutant)
        except ValueError:
            pass
        else:
            raise AssertionError("Scientific mutation accepted")
    for name in ("../escape", "C:/escape", "research-snapshot/internal/private", "x\\y"):
        try:
            safe_member(name)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe path accepted")
    # Synthetic fixture; not evidence of an actual rendered PDF or review.
    report = {"submission_manuscript_sha256": "fixture"}
    qa_fixture = {"documents": {"a.pdf": {"sha256": "fixture-pdf", "pages": 2}}}
    valid = {"compiled_source_sha256": "fixture", "external_review": "NOT_PERFORMED",
             "documents": {"a.pdf": {"sha256": "fixture-pdf", "disposition": "PASS", "reviewed_pages": [1, 2]}}}
    validate_review(report, valid, qa_fixture)
    for kind in ("false_external", "missing_page", "stale_hash"):
        mutant = copy.deepcopy(valid)
        if kind == "false_external":
            mutant["external_review"] = "PASS"
        elif kind == "missing_page":
            mutant["documents"]["a.pdf"]["reviewed_pages"] = [1]
        else:
            mutant["documents"]["a.pdf"]["sha256"] = "stale"
        try:
            validate_review(report, mutant, qa_fixture)
        except ValueError:
            pass
        else:
            raise AssertionError("False review accepted: " + kind)
    compile(VERIFY, "verify-package.py", "exec")
    print("SELF-TEST PASS: scientific/bibliographic invariance, hostile coefficient/marker, path escape, false external review, missing page, stale PDF, verifier syntax")


def main():
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    for name in ("self-test", "prepare", "qa", "seal", "check"):
        mode.add_argument("--" + name, action="store_true")
    parser.add_argument("--work", type=Path)
    parser.add_argument("--poppler", type=Path)
    args = parser.parse_args()
    if (args.prepare or args.qa or args.seal) and (args.work is None or not args.work.is_absolute()):
        parser.error("--work requires an absolute bounded scratch path")
    if args.prepare:
        prepare(args.work)
    elif args.qa:
        if args.poppler is None:
            parser.error("--qa requires --poppler PATH_TO_PDFTOPPM")
        qa(args.work, args.poppler)
    elif args.seal:
        seal(args.work)
    elif args.check:
        check()
    else:
        self_test()


if __name__ == "__main__":
    main()
