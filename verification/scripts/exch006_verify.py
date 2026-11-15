#!/usr/bin/env python3
"""Replay two exact formulations and the pinned existing Lean obstruction.

The Lean reuse checks function-factorization algebra, NOT the full P1 model.
The exact witness is analytic plus two independent symbolic formulations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-exch006'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args=parser.parse_args()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ('exch006_primary.py','exch006_independent.py'):
        subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'verification/scripts'/name)],cwd=ROOT,check=True)
    a=json.loads((RUN/'primary.json').read_text());b=json.loads((RUN/'independent.json').read_text())
    assert all(a['checks'].values()) and all(b['checks'].values())
    assert a['shared']==b['shared']
    for key in ('q','r','a_squared','delta','dImZ','dReZ','dJ','dJ_gap'):
        assert a['derived'][key]==b['derived'][key],key
    assert sha(Path(harness.__file__))=='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
    harness.SOURCE=ROOT/'verification/lean/Tect/ExchangeReadout.lean'
    lean=harness.run(args.lean_cache,args.elan_home)
    lean.update(schema='tect/exch006-reused-lean/1.0',status='PASS_REUSED_FACTORIZATION_LEMMA',
                scope='Fresh compilation of existing no_value_only_drift plus four companion algebra lemmas; no new Lean theorem.',
                not_encoded='Concrete state pair, original P1 first variations and regulated projection crosswalk remain analytic and independently symbolic.',
                equivalent_lake_command='cd verification/lean; lake env lean Tect/ExchangeReadout.lean')
    (RUN/'lean.json').write_text(json.dumps(lean,indent=2)+'\n',encoding='utf-8',newline='\n')
    card=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-006-result-v1.json').read_text())
    assert card['overall_verdict']=='DISPROVED' and not card['active_gate_change'] and not card['physical_promotion']
    assert card['contract_sha256']==a['contract_sha256']==b['contract_sha256']
    reviews=json.loads((RUN/'reviews.json').read_text())
    assert reviews['independent']['status']==reviews['hostile']['status']=='SCOPED_PASS'
    required={'strategy/physical-candidates/TECT-EXCH-006-contract-v1.json',
              'strategy/physical-candidates/TECT-EXCH-006-result-v1.json',
              'verification/scripts/exch006_primary.py','verification/scripts/exch006_independent.py',
              'verification/scripts/exch006_verify.py',
              'claims/C6-SPACETIME-SIGNATURE/notes/augmented-exchange-closure-261115-v1.0.tex.txt'}
    assert set(reviews['reviewed_hashes'])==required
    for p,digest in reviews['reviewed_hashes'].items():assert sha(ROOT/p)==digest,p
    out={'status':'PASS_EXACT_AUGMENTED_NONCLOSURE','result_id':'R-581',
         'script_sha256':sha(Path(__file__)),'contract_sha256':a['contract_sha256'],
         'primary_checks':len(a['checks']),'independent_checks':len(b['checks']),
         'lean_declarations':len(lean['declarations']),'lean_scope':'Existing parameterized factorization reused; no full P1 formalization.',
         'reviewed_hashes':reviews['reviewed_hashes'],
         'scope':'Exact named-observable negative at original finite model; C6/T054 and native instrument HOLD unchanged.'}
    (RUN/'integrated.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH006 VERIFY: PASS_EXACT_AUGMENTED_NONCLOSURE')


if __name__=='__main__':main()
