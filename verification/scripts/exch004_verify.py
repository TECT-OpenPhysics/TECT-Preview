#!/usr/bin/env python3
"""Reproduce EXCH004 source/identifiability audit; never fill missing data."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-13-exch004'
ASSESS=ROOT/'strategy/physical-candidates/TECT-EXCH-004-assessment-v1.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-cache',type=Path);a=p.parse_args()
    extras=['--source-cache',str(a.source_cache)] if a.source_cache else []
    for name,args in [('exch004_primary.py',extras),('exch004_independent.py',[])]:
        subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'verification/scripts'/name),*args],cwd=ROOT,check=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assessment=json.loads(ASSESS.read_text())
    cpath=ROOT/assessment['contract'];contract=json.loads(cpath.read_text())
    assert sha(cpath)==assessment['contract_sha256']
    primary=json.loads((RUN/'primary.json').read_text());ind=json.loads((RUN/'independent.json').read_text())
    assert all(primary['checks'].values()) and all(ind['checks'].values())
    assert assessment['overall_verdict']=='HOLD_FOR_EVIDENCE'
    assert assessment['new_result_id'] is None and assessment['new_negative_id'] is None
    assert not assessment['claim_bearing'] and not assessment['active_gate_change'] and not assessment['physical_promotion']
    assert contract['budget']['physical_fits']==0 and len(contract['sources'])==2
    assert assessment['single_missing_input']['status']=='NOT_SUPPLIED_BY_THE_TWO_ADMITTED_SOURCES'
    note=ROOT/'claims/C6-SPACETIME-SIGNATURE/notes/pair-readout-audit-261113-v1.0.tex.txt'
    pdf=note.with_name(note.name.replace('.tex.txt','.pdf'))
    review=RUN/'hostile-review.json'
    assert pdf.read_bytes().startswith(b'%PDF')
    assert json.loads(review.read_text())['physical_verdict']=='HOLD_FOR_EVIDENCE'
    files=[cpath,ASSESS,note,pdf,review,Path(__file__),ROOT/'verification/scripts/exch004_primary.py',ROOT/'verification/scripts/exch004_independent.py']
    report={'status':'PASS_AUDIT_COMPLETE_PHYSICAL_HOLD','task_id':'T-105','new_result_id':None,
      'primary_checks':len(primary['checks']),'independent_checks':len(ind['checks']),
      'evidence_hashes':{f.relative_to(ROOT).as_posix():sha(f) for f in files},
      'native_target_reconstruction':'NOT_ESTABLISHED_MISSING_CALIBRATION',
      'empirical_unused_response_validation':'NOT_EXECUTED_MISSING_CALIBRATION_AND_ROLE_FROZEN_OUTCOMES',
      'Lean':'NOT_RUN_NEW_THEOREM: standard reference algebra is diagnostic; missing physical data cannot be supplied by Lean. Existing sources unchanged.',
      'scope':'Source/provenance and conditional standard algebra audit only, not empirical PASS or native physical no-go.'}
    (RUN/'integrated.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH004 VERIFY: PASS_AUDIT_COMPLETE_PHYSICAL_HOLD')


if __name__=='__main__':main()
