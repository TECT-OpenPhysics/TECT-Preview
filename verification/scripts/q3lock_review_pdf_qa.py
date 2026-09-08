"""Render the review PDFs and report bounded geometry/text checks, not proof."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

from PIL import Image, ImageDraw
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "publish/review-packages/q3lock-v0138-r1"
WORK = ROOT / "tmp/pdfs/q3lock-v0138-r1"
DPI = 110  # Review rendering resolution, not a scientific parameter.


def main():
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    report = {"scope": "Bounded PDF geometry/text and render checks only", "documents": {}}
    for name in ("manuscript", "reviewer-guide"):
        pdf = DIST / (name + ".pdf")
        images = WORK / "render" / name
        images.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(pdf), str(images / "page")], check=True)
        records = []
        with pdfplumber.open(pdf) as document:
            for number, page in enumerate(document.pages, 1):
                text = page.extract_text() or ""
                # This only checks MediaBox bounds. Internal overlap needs visual inspection.
                outside = [c for c in page.chars if c["x0"] < -0.5 or c["x1"] > page.width + 0.5
                           or c["top"] < -0.5 or c["bottom"] > page.height + 0.5]
                assert text.strip(), (name, number, "blank page")
                assert "??" not in text, (name, number, "unresolved reference")
                assert not outside, (name, number, "off-page glyph")
                records.append({"page": number, "characters": len(page.chars),
                                "off_page_glyphs": len(outside), "unresolved_reference_marker": False})
        pngs = sorted(images.glob("page-*.png"))
        assert len(pngs) == len(records)
        for offset in range(0, len(pngs), 2):
            selected = [Image.open(path).convert("RGB") for path in pngs[offset:offset+2]]
            width = sum(img.width for img in selected)
            height = max(img.height for img in selected)
            sheet = Image.new("RGB", (width, height + 28), "#d8dee5")
            cursor = 0
            draw = ImageDraw.Draw(sheet)
            for j, img in enumerate(selected):
                sheet.paste(img, (cursor, 28))
                draw.text((cursor + 12, 7), f"{name}: page {offset+j+1}", fill="black")
                cursor += img.width
            sheet.save(images / f"spread-{offset//2+1:02}.png")
            sheet.save(images / f"spread-{offset//2+1:02}.jpg", quality=75)
        report["documents"][name + ".pdf"] = {
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "pages": len(records), "page_checks": records, "dpi": DPI,
            "rendered_pages": [{"page": n, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                               for n, p in enumerate(pngs, 1)],
            "visual_disposition": "NOT_AUTOMATICALLY_ASSIGNED"}
    out = WORK / "pdf-qa.json"
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print("PASS bounded text/MediaBox checks; all pages rendered; visual review still required")
    print({name: item["pages"] for name, item in report["documents"].items()})


if __name__ == "__main__":
    main()
