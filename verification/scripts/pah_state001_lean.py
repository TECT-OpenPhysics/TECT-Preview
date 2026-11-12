#!/usr/bin/env python3
"""Pinned Lean replay of four partial display-state algebra bridges."""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'verification/lean/Tect/PahDisplayClosure.lean'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-pah-state001/lean.json'
HARNESS_HASH='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    p.add_argument('--write',action='store_true')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    assert hashlib.sha256(Path(harness.__file__).read_bytes()).hexdigest()==HARNESS_HASH
    harness.SOURCE=SOURCE
    result=harness.run(a.lean_cache,a.elan_home)
    result.update(schema='tect/pah-state001-lean/1.0',status='PASS_PARTIAL_DISPLAY_BRIDGES',
        script_version='1.0.0',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        compiler_harness_sha256=HARNESS_HASH,
        equivalent_lake_command='cd verification/lean; lake env lean Tect/PahDisplayClosure.lean',
        scope='No fibre factorization from a witness; positive exponential gap; two-value conditional variance; positive-mass contribution.',
        not_encoded='Source F, full roots, gauge/anchor actions, finite detailed balance, Gibbs conditional expectation and analytic semigroup failure are checked separately, not encoded in Lean.',
        non_claims='No full-model formalization, physical carrier, clock law, uniform limit or Pre-A conclusion.')
    if a.write:
        assert not OUT.exists(),'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    elif a.check:
        old=json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in result.items() if k!='environment'}
    print('STATE-001 LEAN: PASS',len(result['declarations']),'partial declarations')

if __name__=='__main__': main()
