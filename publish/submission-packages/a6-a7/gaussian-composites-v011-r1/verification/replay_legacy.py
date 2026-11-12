#!/usr/bin/env python3
"""Replay pinned A6/A7 ingredient audits into new paths, preserving issued runs."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    work=args.work.resolve()
    if work.exists(): raise ValueError('Choose an absent directory; previous audits are immutable')
    work.relative_to(ROOT)
    work.mkdir(parents=True)
    protected={p:p.read_bytes() for claim in ('A6-CLASSII-K-COMPOSITE-DEFINITION','A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE')
               for p in (ROOT/'claims'/claim/'runs').glob('2026-07-20*/result.json')}
    module=runpy.run_path(str(ROOT/'codes/foundations/a6_classii_k_composite_verify.py'),run_name='a6_paper_replay')
    fn=module['main']
    fn.__globals__['PRIMARY_RESULT']=work/'a6-primary.json'
    fn.__globals__['INDEPENDENT_RESULT']=work/'a6-independent.json'
    before=sys.argv
    try:
        sys.argv=['a6-replay','--output',str(work/'a6-integrated.json')]
        if fn()!=0: raise ValueError('A6 ingredient replay failed')
    finally: sys.argv=before
    command=[sys.executable,'-X','utf8',str(ROOT/'codes/foundations/a7_classii_renormalised_energy_verify.py'),
             '--primary-output',str(work/'a7-primary.json'),
             '--independent-output',str(work/'a7-independent.json'),
             '--output',str(work/'a7-integrated.json')]
    subprocess.run(command,cwd=ROOT,check=True)
    if not all(p.read_bytes()==value for p,value in protected.items()):
        raise ValueError('Issued historical runs changed')
    results={name:json.loads((work/(name+'-integrated.json')).read_text(encoding='utf-8')) for name in ('a6','a7')}
    report={'schema':'tect/a6-a7-paper-legacy-replay/1.0','status':'PASS',
            'scope':'Finite ingredient/source-hash audits; not analytic limit proofs.',
            'issued_historical_reports_preserved':len(protected),
            'summaries':{key:value['assertion_summary'] for key,value in results.items()},
            'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(work.glob('*.json'))}}
    with (work/'replay-summary.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,indent=2,sort_keys=True); stream.write('\n')
    print('A6/A7 LEGACY REPLAY: PASS; issued reports preserved')


if __name__=='__main__': main()
