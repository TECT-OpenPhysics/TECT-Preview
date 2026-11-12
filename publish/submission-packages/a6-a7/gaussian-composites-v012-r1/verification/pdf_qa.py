#!/usr/bin/env python3
"""PDF text/geometry audit; visual review is a separate human-readable receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import pdfplumber

PAPER=Path(__file__).resolve().parents[1]


def build():
    path=PAPER/'manuscript.pdf'
    pages=[]
    with pdfplumber.open(path) as pdf:
        if not pdf.pages: raise ValueError('Empty PDF')
        for i,page in enumerate(pdf.pages,1):
            text=page.extract_text() or ''
            if '??' in text: raise ValueError('Unresolved reference')
            if not page.chars or len(text)<100: raise ValueError('Empty or unreadable page')
            bounds=(min(c['x0'] for c in page.chars),max(c['x1'] for c in page.chars),
                    min(c['top'] for c in page.chars),max(c['bottom'] for c in page.chars))
            if bounds[0]<30 or bounds[1]>page.width-30 or bounds[2]<30 or bounds[3]>page.height-20:
                raise ValueError('Content outside page safety margins')
            pages.append({'page':i,'characters':len(text),'width':page.width,'height':page.height,
                          'text_bounds':[round(x,4) for x in bounds]})
    return {'schema':'tect/a6-a7-paper-pdf-qa/1.0','status':'PASS','pages':pages,
            'page_count':len(pages),'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'tex_sha256':hashlib.sha256((PAPER/'manuscript.tex').read_bytes()).hexdigest(),
            'scope':'Text/geometry/reference checks; visual layout reviewed separately.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-new',type=Path); p.add_argument('--check',type=Path)
    a=p.parse_args(); payload=build()
    if a.check and payload!=json.loads(a.check.read_text(encoding='utf-8')):
        raise ValueError('PDF QA snapshot changed')
    if a.write_new:
        a.write_new.parent.mkdir(parents=True,exist_ok=True)
        with a.write_new.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(payload,stream,indent=2,sort_keys=True);stream.write('\n')
    print('A6/A7 PDF QA: PASS',payload['page_count'],'pages; visual receipt required')


if __name__=='__main__': main()
