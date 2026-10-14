#!/usr/bin/env python3
"""RD-001 pinned Lean replay; six parameterized bridges, not the full model."""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'verification/lean/Tect/PahV2ReadoutFreezing.lean'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-v2-rd001/lean.json'
HARNESS_HASH='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    assert hashlib.sha256(Path(harness.__file__).read_bytes()).hexdigest()==HARNESS_HASH
    harness.SOURCE=SOURCE
    result=harness.run(a.lean_cache,a.elan_home)
    result.update(schema='tect/pah-v2-rd001-lean/1.0',status='PASS_PARAMETERIZED_READOUT_BRIDGES',
        script_version='1.0.0',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        compiler_harness_sha256=HARNESS_HASH,
        equivalent_lake_command='cd verification/lean; lake env lean Tect/PahV2ReadoutFreezing.lean',
        scope='Six parameterized finite-sum, supplied integral, centering and positive-variance bridges.',
        not_encoded='Source bounds, finite contraction and Duhamel, Gibbs density sandwich, Fourier orthogonality and cutoff decay remain analytic, not fully formalized.',
        non_claims='No full-model Lean encoding, physical time, infinite-volume dynamics, QFT, gravity or external-referee certification.')
    if a.check:
        old=json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in result.items() if k!='environment'}
    else:
        assert not OUT.exists(),'Issued run is immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('RD-001 LEAN: PASS',len(result['declarations']),'parameterized declarations')

if __name__=='__main__':
    main()
