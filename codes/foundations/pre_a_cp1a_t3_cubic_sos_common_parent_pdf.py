#!/usr/bin/env python3
"""Build the deterministic CP1a certificate PDF with ReportLab."""

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
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "strategy" / "pre-a-cp1a-t3-cubic-sos-common-parent-certificate-260803.md"
DEFAULT_OUTPUT = (
    REPO
    / "output"
    / "pdf"
    / "pre-a-cp1a-t3-cubic-sos-common-parent-certificate-260803-v0.1.pdf"
)


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CP1aTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#15344a"),
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "CP1aH1",
            parent=sample["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13.5,
            leading=17,
            textColor=colors.HexColor("#15344a"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "CP1aH2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#285a73"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "CP1aBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.2,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#202830"),
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "CP1aBullet",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.0,
            leading=12,
            leftIndent=13,
            firstLineIndent=-7,
            bulletIndent=4,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "CP1aQuote",
            parent=sample["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.0,
            leading=12,
            leftIndent=12,
            rightIndent=10,
            borderColor=colors.HexColor("#8aa7b8"),
            borderWidth=1,
            borderPadding=(4, 6, 4, 8),
            textColor=colors.HexColor("#334852"),
            backColor=colors.HexColor("#f3f7f9"),
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "CP1aCode",
            fontName="Courier",
            fontSize=7.6,
            leading=9.5,
            leftIndent=7,
            rightIndent=7,
            borderColor=colors.HexColor("#d5dde2"),
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#f6f8fa"),
            textColor=colors.HexColor("#263238"),
            spaceBefore=2,
            spaceAfter=7,
        ),
        "meta": ParagraphStyle(
            "CP1aMeta",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#445b68"),
            leftIndent=8,
            spaceAfter=2,
        ),
    }


def parse_markdown(source: str) -> list[object]:
    style = styles()
    story: list[object] = []
    paragraph: list[str] = []
    paragraph_kind = "body"
    paragraph_bullet: str | None = None
    code: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        nonlocal paragraph_kind, paragraph_bullet
        if paragraph:
            text = " ".join(part.strip() for part in paragraph).strip()
            if text:
                chosen_style = style[paragraph_kind]
                story.append(
                    Paragraph(
                        inline_markup(text),
                        chosen_style,
                        bulletText=paragraph_bullet,
                    )
                )
            paragraph.clear()
        paragraph_kind = "body"
        paragraph_bullet = None

    def flush_code() -> None:
        if code:
            wrapped_lines: list[str] = []
            for raw_line in code:
                if len(raw_line) <= 88:
                    wrapped_lines.append(raw_line)
                    continue
                indentation = raw_line[: len(raw_line) - len(raw_line.lstrip())]
                wrapped_lines.extend(
                    textwrap.wrap(
                        raw_line,
                        width=88,
                        subsequent_indent=indentation + "  ",
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                )
            story.append(Preformatted("\n".join(wrapped_lines), style["code"]))
            code.clear()

    lines = source.splitlines()
    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_paragraph()
                in_code = True
            continue
        if in_code:
            code.append(stripped)
            continue
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), style["title"]))
            story.append(
                Paragraph(
                    "Verification-first research certificate - T0 scope",
                    style["meta"],
                )
            )
            story.append(Spacer(1, 4 * mm))
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), style["h1"]))
            continue
        if stripped.startswith("#### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[5:]), style["h2"]))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), style["h2"]))
            continue
        if stripped.startswith("> "):
            if paragraph_kind != "quote":
                flush_paragraph()
                paragraph_kind = "quote"
            paragraph.append(stripped[2:])
            continue
        ordered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if ordered:
            flush_paragraph()
            paragraph_kind = "bullet"
            paragraph_bullet = ordered.group(1) + "."
            paragraph.append(ordered.group(2))
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            paragraph_kind = "meta" if not story or len(story) < 12 else "bullet"
            paragraph_bullet = "-"
            paragraph.append(stripped[2:])
            continue
        paragraph.append(stripped)

    flush_paragraph()
    flush_code()
    return story


def footer(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#c9d4da"))
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#5c6f78"))
    canvas.drawString(18 * mm, 9.5 * mm, "TECT - CP1a compatibility certificate - 2026-08-03")
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
            title="CP1a cubic-SOS common-parent compatibility certificate",
            author="TECT verification-first repository",
            subject="T0 common-parent compatibility benchmark",
            creator=f"ReportLab deterministic builder {__version__}",
            invariant=1,
            pageCompression=1,
        )
        story = parse_markdown(source.read_text(encoding="utf-8"))
        document.build(story, onFirstPage=footer, onLaterPages=footer)
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
