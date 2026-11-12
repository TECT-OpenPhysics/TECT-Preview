#!/usr/bin/env python3
"""Reproduce the finite audit while enforcing the physical HOLD firewall."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch003'
CARD=ROOT/'strategy/physical-candidates/TECT-EXCH-003-result-v1.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--source-cache',type=Path)
    a=p.parse_args();sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    for name,args in [('exch003_primary.py',[]),('exch003_independent.py',[]),('exch003_lean.py',['--lean-cache',str(a.lean_cache),'--check'])]:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts'/name),*args],cwd=ROOT,check=True)
    card=json.loads(CARD.read_text())
    for path,digest in {**card['source_hashes'],**card['evidence_hashes']}.items():
        assert sha(ROOT/path)==digest,path
    src=json.loads((ROOT/card['physical_source_crosswalk']).read_text())
    if a.source_cache:
        for name,item in zip(('syassen-v2.pdf','heinzen-v1.pdf'),src['sources']):
            assert sha(a.source_cache/name)==item['sha256']
    primary=json.loads((RUN/'primary.json').read_text());ind=json.loads((RUN/'independent.json').read_text())
    assert all(primary['checks'].values()) and all(c['pass'] for c in ind['checks'])
    assert primary['derived']['Qbar']==ind['derived']['Q']
    assert primary['derived']['p']==ind['derived']['p']
    assert primary['derived']['abs_current']==str(abs(s.Rational(ind['counterexample'][0]['J'])))
    assert card['overall_verdict']==src['overall']=='HOLD_FOR_EVIDENCE_NOT_A_PHYSICAL_NO_GO'
    assert not card['active_gate_change'] and not card['physical_promotion']
    assert card['new_physical_state_adopted'] is False
    assert card['verdicts']['universal_population_closure']=='DISPROVED_FOR_ALL_FULL_DIRAC_PREPARATIONS'
    assert card['verdicts']['augmented_observable_closure']=='NOT_ESTABLISHED'
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts/lean_toolchain_check.py'),'--metadata'],cwd=ROOT,check=True)
    out={'status':'PASS_SCOPED_AUDIT_PHYSICAL_HOLD','result_id':'R-580','script_sha256':sha(Path(__file__)),
      'card_sha256':sha(CARD),'primary_checks':len(primary['checks']),'independent_checks':len(ind['checks']),
      'lean_declarations':len(json.loads((RUN/'lean.json').read_text())['declarations']),
      'scope':'Exact finite diagnostics and source firewall, not a complete physical state/law/instrument mapping.'}
    (RUN/'integrated.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH003 VERIFY: PASS_SCOPED_AUDIT_PHYSICAL_HOLD')


if __name__=='__main__':main()
