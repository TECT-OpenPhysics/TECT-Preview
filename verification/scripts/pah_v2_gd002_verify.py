#!/usr/bin/env python3
"""Fresh four-lane replay of the exact scoped GD-002 counterexample, v1.0.1.

PASS means reproduction, while the registered mathematical target is DISPROVED.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

__version__='1.0.1'
ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    parser.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    args=parser.parse_args()
    certificate=json.loads((ROOT/'strategy/pa-hyp/PAH-v2-GD-002-result-v1.1.json').read_text(encoding='utf-8'))
    for group in ('source_hashes','evidence_hashes'):
        for path,digest in certificate[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    for name in ('primary','independent','hostile','lean'):
        command=[sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_v2_gd002_{name}.py'),'--check']
        if name=='lean':
            command+=['--lean-cache',str(args.lean_cache),'--elan-home',str(args.elan_home)]
        proc=subprocess.run(command,cwd=ROOT,check=False)
        assert proc.returncode==0,name
    assert certificate['verdict']=='DISPROVED'
    assert not certificate['active_gate_change'] and not certificate['physical_promotion']
    assert certificate['separate_diagnostics']['state_consistency']=='NOT_ESTABLISHED_OR_REFUTED'
    print('GD-002 INTEGRATED: PASS; target DISPROVED; original fine-Gibbs all-tail norm obstruction only')


if __name__=='__main__':
    main()
