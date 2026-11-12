#!/usr/bin/env python3
"""Pinned partial real-algebra replay, not a formalization of the analytic theorem."""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch001/lean.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    assert hashlib.sha256(Path(harness.__file__).read_bytes()).hexdigest()=='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
    harness.SOURCE=ROOT/'verification/lean/Tect/ExchangeParent.lean'
    r=harness.run(a.lean_cache,a.elan_home)
    r.update(schema='tect/exch001-lean/1.0',status='PASS_PARTIAL_EXCHANGE_ALGEBRA',
             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             compiler_harness_sha256=hashlib.sha256(Path(harness.__file__).read_bytes()).hexdigest(),
             scope='Six parameterized cancellation, square-completion, lower-bound and negative-trial lemmas.',
             not_encoded='Source P1/R158 identity, global phase invariance, projected flow completeness, coercivity/compactness, minimizer threshold and charge jump remain analytic obligations.',
             equivalent_lake_command='cd verification/lean; lake env lean Tect/ExchangeParent.lean',
             non_claims='No physical reservoir/time, equilibration, limit, Pre-A, QFT or gravity.')
    if a.check:
        old=json.loads(OUT.read_text())
        assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in r.items() if k!='environment'}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH001 LEAN: PASS',len(r['declarations']),'partial declarations')


if __name__=='__main__': main()
