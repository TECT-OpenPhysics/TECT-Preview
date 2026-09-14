#!/usr/bin/env python3
"""One-command replay of the completed definition admission, version 1.0.0.

Integrity and executable/Lean replay supplement the cited written all-index
proof. This script does not mechanically decide arbitrary mathematical prose.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'strategy/pa-hyp/PAH-v2-comparison-admission-v1.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args=parser.parse_args()
    result=json.loads(RESULT.read_text(encoding='utf-8'))
    assert result['id']=='PAH-V2-COMPARISON-ADMISSION-v1'
    assert result['verdict']=='PASS_DEFINITION_ADMISSION'
    assert result['counts_as_mainline'] is False and result['physical_promotion'] is False
    for path,h in {**result['source_hashes'],**result['evidence_hashes']}.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    for name in ('primary','independent','lean','hostile'):
        cmd=[sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_v2_comparison_{name}.py'),'--check']
        if name=='lean':
            cmd.extend(['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)])
        run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=300)
        assert run.returncode==0,run.stdout+run.stderr
        print(run.stdout.strip(),flush=True)
    assert all(r['status']=='DISCHARGED_AT_STATED_DEFINITION_SCOPE' for r in result['requirements'])
    print('PAH-V2-COMPARISON ADMISSION: PASS (internal definition scope; no dynamics/physical promotion)')


if __name__=='__main__':
    main()
