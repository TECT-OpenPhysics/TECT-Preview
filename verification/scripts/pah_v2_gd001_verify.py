#!/usr/bin/env python3
"""Replay the R-572 GD-001 exact negative-result package, version 1.0.0.

Fresh executables and the pinned kernel supplement the written all-index
proof; this integrity checker does not mechanically certify mathematical prose.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT/'strategy/pa-hyp/PAH-v2-GD-001-result-v1.json'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    ap.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args = ap.parse_args()
    result = json.loads(RESULT.read_text(encoding='utf-8'))
    assert result['result_id']=='R-572' and result['verdict']=='DISPROVED'
    assert not result['counts_as_mainline'] and not result['physical_promotion']
    assert result['Gibbs_L2']=='NOT_EVALUATED'
    assert result['exact_scope']['norm']=='FULL_STATE_SUP'
    for p,h in {**result['source_hashes'],**result['evidence_hashes']}.items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    cmd = [sys.executable,'-X','utf8',str(ROOT/'verification/scripts/pah_v2_gd001_prereg_check.py'),'--check']
    subprocess.run(cmd,cwd=ROOT,check=True)
    for lane in ('primary','independent','lean','hostile'):
        cmd = [sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_v2_gd001_{lane}.py'),'--check']
        if lane=='lean':
            cmd += ['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)]
        fresh = subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=300)
        assert fresh.returncode==0,fresh.stdout+fresh.stderr
        print(fresh.stdout.strip(),flush=True)
    assert all(item['status']=='PASS_AT_STATED_SCOPE' for item in result['completion_audit'])
    print('GD-001 PACKAGE: PASS; mathematical verdict DISPROVED at epsilon=1 (full-cylinder sup route only)')


if __name__=='__main__':
    main()
