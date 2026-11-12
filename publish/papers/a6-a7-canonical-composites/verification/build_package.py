#!/usr/bin/env python3
"""Create a new review distribution, extract it and execute its portable checks."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import zipfile
from package_gates import validate_pdf_qa, validate_visual, validate_output_paths

PAPER=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--extracted',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    dest=args.destination.resolve();archive=dest.with_suffix('.zip')
    extracted=args.extracted.resolve()
    validate_output_paths(PAPER,dest,extracted,args.report)
    if any(p.exists() for p in (dest,archive,extracted,args.report)):
        raise ValueError('New output paths required; issued distributions are immutable')
    qa=json.loads((PAPER/'verification/runs/pdf-qa-v012.json').read_text(encoding='utf-8'))
    validate_pdf_qa(qa)
    live_qa=runpy.run_path(str(PAPER/'verification/pdf_qa.py'))['build']()
    if qa!=live_qa: raise ValueError('PDF QA differs from fresh text/geometry audit')
    review=json.loads((PAPER/'verification/runs/render-review-v012.json').read_text(encoding='utf-8'))
    validate_visual(review,qa,PAPER)
    pdf_sha=hashlib.sha256((PAPER/'manuscript.pdf').read_bytes()).hexdigest()
    tex_sha=hashlib.sha256((PAPER/'manuscript.tex').read_bytes()).hexdigest()
    if qa['pdf_sha256']!=pdf_sha or qa['tex_sha256']!=tex_sha:
        raise ValueError('Stale PDF QA')
    if review['pdf_sha256']!=pdf_sha or review['tex_sha256']!=tex_sha or review['status']!='PASS':
        raise ValueError('Stale or absent visual review')
    if review['pages_reviewed']!=list(range(1,qa['page_count']+1)):
        raise ValueError('Incomplete all-page review')
    dest.mkdir(parents=True)
    for path in sorted(PAPER.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc': continue
        target=dest/path.relative_to(PAPER);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    shutil.copyfile(PAPER/'verification/verify_package.py',dest/'verify-package.py')
    for name,expected in (('manuscript.pdf',pdf_sha),('manuscript.tex',tex_sha)):
        if hashlib.sha256((dest/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Source changed during package copy: '+name)
    validate_visual(review,qa,dest)
    verify=runpy.run_path(str(PAPER/'verification/verify_package.py'))
    files={p.relative_to(dest).as_posix():{'bytes':p.stat().st_size,
           'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(dest.rglob('*')) if p.is_file()}
    manifest={'schema':'tect/a6-a7-review-package/1.0','version':'0.1.2-r1',
        'source_checkpoint':json.loads((PAPER/'sources/provenance.json').read_text())['source_checkpoint'],
        'scope':verify['SCOPE'],'files':files}
    with (dest/'MANIFEST.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(manifest,stream,sort_keys=True,indent=2);stream.write('\n')
    verify['contract'](manifest)
    if verify['check'](dest)!=len(files): raise ValueError('Inventory count')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(dest.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(dest).as_posix())
    extracted.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist(): verify['safe_name'](name)
        z.extractall(extracted)
    commands=([sys.executable,'verify-package.py','--self-test'],
              [sys.executable,'verification/verify.py','--self-test','--check','verification/runs/algebra.json'],
              [sys.executable,'verification/strengthened_audit.py','--check','verification/runs/strengthened-v012.json'],
              [sys.executable,'verification/package_gates.py','--self-test'])
    runs=[]
    for command in commands:
        run=subprocess.run(command,cwd=extracted,capture_output=True,text=True,encoding='utf-8')
        runs.append({'command':command[1:],'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        if run.returncode: raise ValueError(run.stdout+run.stderr)
    if verify['check'](dest)!=len(files) or verify['check'](extracted)!=len(files):
        raise ValueError('Final package changed')
    result={'schema':'tect/a6-a7-package-build/1.0','status':'PASS','version':'0.1.2-r1',
        'files_verified':len(files),'pdf_pages':qa['page_count'],'archive_bytes':archive.stat().st_size,
        'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'manifest_sha256':hashlib.sha256((dest/'MANIFEST.json').read_bytes()).hexdigest(),
        'extracted_checks':runs,'external_mathematical_review':'NOT_PERFORMED',
        'specialist_novelty_review':'NOT_PERFORMED','actual_transmission':'NOT_PERFORMED'}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.report.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print('A6/A7 REVIEW PACKAGE: PASS',len(files),'files; extracted checks PASS')


if __name__=='__main__': main()
