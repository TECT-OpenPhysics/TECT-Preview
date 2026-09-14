#!/usr/bin/env python3
"""SG-001 full fresh replay: inherited source checks plus four current checks.

PASS reproduces a scoped DISPROVED target, not successful convergence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    a=p.parse_args()
    certificate=json.loads((ROOT/'strategy/pa-hyp/PAH-v2-SG-001-result-v1.json').read_text(encoding='utf-8'))
    for group in ('source_hashes','evidence_hashes'):
        for path,digest in certificate[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    lean_args=['--lean-cache',str(a.lean_cache),'--elan-home',str(a.elan_home)]
    parent=[sys.executable,'-X','utf8',str(ROOT/'verification/scripts/pah_v2_gd002_verify.py')]+lean_args
    subprocess.run(parent,cwd=ROOT,check=True)
    for name in ('primary','independent','hostile','lean'):
        cmd=[sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_v2_sg001_{name}.py'),'--check']
        if name=='lean': cmd+=lean_args
        subprocess.run(cmd,cwd=ROOT,check=True)
    d=json.loads((ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-pah-v2-sg001/primary.json').read_text(encoding='utf-8'))['derived']
    assert certificate['counterexample']['time']==d['time']
    assert certificate['counterexample']['norm_lower']==d['delta']
    assert certificate['counterexample']['norm_squared_lower']==d['norm_squared_lower']
    assert certificate['verdict']=='DISPROVED'
    assert not certificate['active_gate_change'] and not certificate['physical_promotion']
    assert certificate['follow_on']['automatic_successor'] is False
    print('SG-001 INTEGRATED: PASS; target DISPROVED; fixed t=1/10, delta=1/5; no automatic successor')


if __name__=='__main__':
    main()
