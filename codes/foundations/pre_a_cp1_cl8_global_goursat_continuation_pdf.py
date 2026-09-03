#!/usr/bin/env python3
"""Build the deterministic canonical CL8 global-Goursat certificate PDF.

Changelog: 0.1.0 (2026-08-04) first issue with A4 render output.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import tempfile
import textwrap
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer


__version__ = "0.1.0"
__first_issued__ = "2026-08-04"
__version_issued__ = "2026-08-04"
__claims__ = ["C6-SPACETIME-SIGNATURE"]
REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-certificate-260803.md"
DEFAULT_OUTPUT = (
    REPO
    / "output/pdf"
    / "pre-a-cp1-cl8-global-goursat-continuation-certificate-260803-260804-v0.1.1.pdf"
)


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CL8CanonicalTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#183c56"),
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "CL8CanonicalH1",
            parent=sample["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13.2,
            leading=16.5,
            textColor=colors.HexColor("#183c56"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=False,
        ),
        "h2": ParagraphStyle(
            "CL8CanonicalH2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.2,
            leading=14,
            textColor=colors.HexColor("#2e647d"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=False,
        ),
        "body": ParagraphStyle(
            "CL8CanonicalBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.55,
            leading=11.2,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#202a31"),
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "CL8CanonicalBullet",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.35,
            leading=10.85,
            leftIndent=14,
            firstLineIndent=-7,
            bulletIndent=4,
            spaceAfter=3,
        ),
        "meta": ParagraphStyle(
            "CL8CanonicalMeta",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=10.5,
            textColor=colors.HexColor("#48616f"),
            leftIndent=8,
            spaceAfter=2,
        ),
        "code": ParagraphStyle(
            "CL8CanonicalCode",
            fontName="Courier",
            fontSize=6.9,
            leading=8.45,
            leftIndent=7,
            rightIndent=7,
            borderColor=colors.HexColor("#ccd7dd"),
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#f5f8fa"),
            textColor=colors.HexColor("#263238"),
            spaceBefore=2,
            spaceAfter=8,
        ),
    }


def parse_markdown(source: str) -> list[object]:
    styles = make_styles()
    story: list[object] = []
    paragraph: list[str] = []
    paragraph_style = "body"
    bullet: str | None = None
    code: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        nonlocal paragraph_style, bullet
        if paragraph:
            joined = " ".join(piece.strip() for piece in paragraph).strip()
            if joined:
                story.append(
                    Paragraph(
                        inline_markup(joined),
                        styles[paragraph_style],
                        bulletText=bullet,
                    )
                )
            paragraph.clear()
        paragraph_style = "body"
        bullet = None

    def flush_code() -> None:
        if not code:
            return
        wrapped: list[str] = []
        for raw in code:
            if len(raw) <= 92:
                wrapped.append(raw)
            else:
                indentation = raw[: len(raw) - len(raw.lstrip())]
                wrapped.extend(
                    textwrap.wrap(
                        raw,
                        width=92,
                        subsequent_indent=indentation + "  ",
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                )
        story.append(Preformatted("\n".join(wrapped), styles["code"]))
        story.append(Spacer(1, 1.2 * mm))
        code.clear()

    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_paragraph()
                in_code = True
            continue
        if in_code:
            code.append(line)
            continue
        if not line:
            flush_paragraph()
            continue
        if re.fullmatch(r'<a id="[^"]+"></a>', line):
            flush_paragraph()
            continue
        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:]), styles["title"]))
            story.append(
                Paragraph(
                    "Verification-first research certificate - T0 classical fixed-background scope",
                    styles["meta"],
                )
            )
            story.append(Spacer(1, 4 * mm))
            continue
        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[3:]), styles["h1"]))
            continue
        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), styles["h2"]))
            continue
        ordered = re.match(r"^(\d+)\.\s+(.*)$", line)
        if ordered:
            flush_paragraph()
            paragraph_style = "bullet"
            bullet = ordered.group(1) + "."
            paragraph.append(ordered.group(2))
            continue
        if line.startswith("- "):
            flush_paragraph()
            paragraph_style = "meta" if len(story) < 12 else "bullet"
            bullet = "-"
            paragraph.append(line[2:])
            continue
        paragraph.append(line)

    flush_paragraph()
    flush_code()
    return story


def footer(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#c8d3da"))
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(colors.HexColor("#5a6d78"))
    canvas.drawString(18 * mm, 9.5 * mm, "TECT - canonical global CL8 Goursat certificate - 2026-08-04")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def build(source: Path, output: Path) -> None:
    rl_config.invariant = 1
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=output.stem + ".", suffix=".pdf", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        document = SimpleDocTemplate(
            str(temporary),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=17 * mm,
            bottomMargin=19 * mm,
            title="Pre-A canonical CL8 global Goursat-continuation certificate",
            author="TECT verification-first repository",
            subject="T0 global classical characteristic reconstruction with two proof architectures",
            creator=f"ReportLab deterministic builder {__version__}",
            invariant=1,
            pageCompression=1,
        )
        document.build(
            parse_markdown(source.read_text(encoding="utf-8")),
            onFirstPage=footer,
            onLaterPages=footer,
        )
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    source = arguments.source if arguments.source.is_absolute() else REPO / arguments.source
    output = arguments.output if arguments.output.is_absolute() else REPO / arguments.output
    build(source, output)
    try:
        display = output.relative_to(REPO)
    except ValueError:
        display = output
    print(f"PASS | deterministic PDF | {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
