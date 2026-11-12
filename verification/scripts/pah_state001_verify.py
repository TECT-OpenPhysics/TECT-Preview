#!/usr/bin/env python3
"""Replay the issued exact finite display-state checkpoint and pinned Lean."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args=p.parse_args()
    result=json.loads((ROOT/'strategy/pa-hyp/PAH-STATE-001-result-v1.json').read_text(encoding='utf-8'))
    for group in ('source_hashes','evidence_hashes'):
        for path,expected in result[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    assert result['verdict']=='DISPROVED' and result['classification']=='negative_result'
    assert not result['active_gate_change'] and not result['physical_promotion']
    for name in ('primary','independent','hostile','lean'):
        cmd=[sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_state001_{name}.py'),'--check']
        if name=='lean': cmd+=['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)]
        proc=subprocess.run(cmd,cwd=ROOT,check=True)
        assert proc.returncode==0
    print('STATE-001 VERIFY: PASS exact finite negative; no physical/mainline promotion')

if __name__=='__main__': main()
