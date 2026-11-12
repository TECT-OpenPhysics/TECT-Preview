#!/usr/bin/env python3
"""Pinned six partial algebra lemmas, not full dynamical stability formalization."""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_gd001_lean as harness

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch002/lean.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    p.add_argument('--check',action='store_true');a=p.parse_args()
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    assert sha(Path(harness.__file__))=='76035cd98d8bba5907776c509b7b0c9afc72e68c5c84bc588611832c6dfecf32'
    harness.SOURCE=ROOT/'verification/lean/Tect/FixedSector.lean'
    r=harness.run(a.lean_cache,a.elan_home)
    r.update(schema='tect/exch002-lean/1.0',status='PASS_PARTIAL_FIXED_SECTOR_ALGEBRA',script_sha256=sha(Path(__file__)),
      compiler_harness_sha256=sha(Path(harness.__file__)),
      equivalent_lake_command='cd verification/lean; lake env lean Tect/FixedSector.lean',
      scope='Six parameterized real-algebra charge, spectral-sign, energy-order and tensor-density lemmas.',
      not_encoded='P1, source root intervals, compact minimum set, unstable manifold, nonlinear stability and asymptotic nonconvergence remain analytic; no full complex tensor model formalization.',
      non_claims='No physical time, state preparation, continuum, PreA, QFT or gravity.')
    if a.check:
        old=json.loads(OUT.read_text());assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in r.items() if k!='environment'}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH002 LEAN: PASS',len(r['declarations']),'partial lemmas')


if __name__=='__main__':main()
