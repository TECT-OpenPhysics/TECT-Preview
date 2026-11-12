#!/usr/bin/env python3
"""Reproduce the scoped EXCH002 and ALT001 packages, not full formal stability."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch002'
CARD=ROOT/'strategy/physical-candidates/TECT-EXCH-002-result-v1.json'
ALT=ROOT/'strategy/physical-candidates/TECT-ALT-001-assessment-v1.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--source-cache',type=Path)
    a=p.parse_args();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    for name,args in [('exch002_primary.py',[]),('exch002_independent.py',[]),('alt001_structural.py',[]),('exch002_lean.py',['--lean-cache',str(a.lean_cache),'--check'])]:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts'/name),*args],cwd=ROOT,check=True)
    card=json.loads(CARD.read_text());alt=json.loads(ALT.read_text())
    for pth,h in {**card['source_hashes'],**card['evidence_hashes']}.items():assert sha(ROOT/pth)==h,pth
    for pth,h in alt['source_hashes'].items():assert sha(ROOT/pth)==h,pth
    if a.source_cache:assert sha(a.source_cache/'teschl-ode.pdf')==card['external_source']['sha256']
    pr=json.loads((RUN/'primary.json').read_text());ind=json.loads((RUN/'independent.json').read_text());ar=json.loads((RUN/'alternative.json').read_text())
    assert all(pr['checks'].values()) and all(ind['checks'].values()) and all(ar['checks'].values())
    assert pr['derived']['Qbar']==ind['derived']['Qbar']==ar['derived']['Qbar']
    assert pr['derived']['growth_squared_lower']==ind['derived']['growth_squared_lower']
    assert card['active_gate_change'] is False and card['physical_promotion'] is False
    assert alt['overall_superiority']=='NOT_ESTABLISHED'
    assert alt['density_candidate']=='REJECTED_NO_COMPONENT_TRANSFER'
    assert card['verdicts']['full_state_ground_attraction']=='DISPROVED_OUTSIDE_MINIMUM_SET'
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts/lean_toolchain_check.py'),'--metadata'],cwd=ROOT,check=True)
    out={'status':'PASS_SCOPED_PACKAGE','result_id':'R-579','script_sha256':sha(Path(__file__)),
      'card_sha256':sha(CARD),'alternative_card_sha256':sha(ALT),
      'primary_checks':len(pr['checks']),'independent_checks':len(ind['checks']),'alternative_checks':len(ar['checks']),
      'lean_declarations':len(json.loads((RUN/'lean.json').read_text())['declarations']),
      'external_source_bytes_checked':bool(a.source_cache),
      'scope':'Algebra, exact spectral signs, frozen inputs and partial Lean; finite-dimensional analytic/source theorem crosswalk reviewed in synthesis, not fully formalized.'}
    (RUN/'integrated.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH002 VERIFY: PASS_SCOPED_PACKAGE')


if __name__=='__main__':main()
