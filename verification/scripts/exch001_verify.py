#!/usr/bin/env python3
"""Reproduce EXCH001 algebra, pinned partial Lean and package integrity.

Does not machine-formalize the analytic finite-K coexistence proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
RUNS=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch001'
CARD=ROOT/'strategy/physical-candidates/TECT-EXCH-001-result-v1.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    a=p.parse_args()
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    for script,extra in [('exch001_primary.py',[]),('exch001_independent.py',[]),('exch001_lean.py',['--lean-cache',str(a.lean_cache),'--check'])]:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts'/script),*extra],cwd=ROOT,check=True)
    card=json.loads(CARD.read_text())
    for path,h in card['evidence_hashes'].items(): assert sha(ROOT/path)==h,path
    for path,h in card['source_hashes'].items(): assert sha(ROOT/path)==h,path
    assert card['active_gate_change'] is False and card['physical_promotion'] is False
    primary=json.loads((RUNS/'primary.json').read_text())
    independent=json.loads((RUNS/'independent.json').read_text())
    assert primary['derived']['D']==independent['derived']['D']
    assert all(primary['checks'].values()) and all(independent['checks'].values())
    assert card['verdicts']['exact_R158_inheritance']=='DISPROVED'
    assert card['verdicts']['controlled_shifted_variational_coexistence']=='PROVED_CONDITIONAL_FINITE_K'
    assert card['verdicts']['physical_realization']=='NOT_ESTABLISHED'
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verification/scripts/lean_toolchain_check.py'),'--metadata'],cwd=ROOT,check=True)
    out={'status':'PASS_SCOPED_PACKAGE','result_id':'R-578','script_sha256':sha(Path(__file__)),
         'primary_checks':len(primary['checks']),'independent_checks':len(independent['checks']),
         'lean_declarations':len(json.loads((RUNS/'lean.json').read_text())['declarations']),
         'card_sha256':sha(CARD),'scope':'Exact algebra, dependency pins and partial Lean; analytic proof/review remains in synthesis. Legacy full PDF replay failure remains explicit.'}
    (RUNS/'integrated.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH001 VERIFY: PASS_SCOPED_PACKAGE')


if __name__=='__main__': main()
