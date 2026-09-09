#!/usr/bin/env python3
"""Render the current paper and check geometry; never assign a visual verdict.

Requires pdfplumber, Pillow and Poppler on PATH. These are bounded tooling
checks, not mathematical tests. --self-test verifies the glyph-boundary guard.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import pdfplumber
from PIL import Image, ImageDraw

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[2]
DPI = 120  # Presentation QA resolution only.


def inside(char, width, height):
    tolerance = 0.5  # PDF glyph-box numerical tolerance in points.
    return (char["x0"] >= -tolerance and char["x1"] <= width+tolerance
            and char["top"] >= -tolerance and char["bottom"] <= height+tolerance)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=PAPER/"manuscript.pdf")
    parser.add_argument("--work", type=Path, default=ROOT/"tmp/pdfs/a2-rereview/render")
    parser.add_argument("--output", type=Path, default=PAPER/"verification/runs/pdf-qa.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    assert inside(dict(x0=1,x1=20,top=1,bottom=20),100,100)
    assert not inside(dict(x0=-1,x1=20,top=1,bottom=20),100,100)
    assert not inside(dict(x0=1,x1=101,top=1,bottom=20),100,100)
    args.work.mkdir(parents=True,exist_ok=True)
    subprocess.run(["pdftoppm","-r",str(DPI),"-png",str(args.pdf),str(args.work/"page")],check=True)
    pages = []
    with pdfplumber.open(args.pdf) as doc:
        page_digits = len(str(len(doc.pages)))
        for number, page in enumerate(doc.pages,1):
            text = page.extract_text() or ""
            outside = [c for c in page.chars if not inside(c,page.width,page.height)]
            assert text.strip(), (number,"blank page")
            assert "??" not in text, (number,"unresolved reference")
            assert not outside, (number,"off-page glyphs")
            png = args.work/f"page-{number:0{page_digits}d}.png"
            assert png.is_file(), png
            pages.append({"page":number,"characters":len(page.chars),"off_page_glyphs":0,
                          "render_sha256":hashlib.sha256(png.read_bytes()).hexdigest()})
    for offset in range(0,len(pages),2):
        paths = [args.work/f"page-{i:0{page_digits}d}.png" for i in range(offset+1,min(offset+3,len(pages)+1))]
        images = [Image.open(path).convert("RGB") for path in paths]
        sheet = Image.new("RGB",(sum(im.width for im in images),max(im.height for im in images)+25),"#dddddd")
        draw = ImageDraw.Draw(sheet)
        x = 0
        for j, im in enumerate(images):
            draw.text((x+12,6),f"Page {offset+j+1}",fill="black")
            sheet.paste(im,(x,25))
            x += im.width
            im.close()
        sheet.save(args.work/f"spread-{offset//2+1:02d}.jpg",quality=88)
    report = {"scope":"Bounded PDF text/geometry checks only", "verdict":"PASS",
              "pages":len(pages),"dpi":DPI,"page_checks":pages,
              "pdf_sha256":hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
              "visual_review":"NOT_AUTOMATICALLY_ASSIGNED"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="\n") as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
        stream.write("\n")
    print(f"A2-PDF-QA-PASS: {len(pages)} pages rendered; visual inspection required")


if __name__=="__main__":
    main()
