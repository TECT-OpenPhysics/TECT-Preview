#!/usr/bin/env python3
"""Replay TIME-002 pinned certificate and four checks; no physical promotion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean-cache',type=Path,default=ROOT/'verification/lean/.lake/packages')
    p.add_argument('--elan-home',type=Path,default=Path.home()/'.elan')
    a=p.parse_args()
    card=json.loads((ROOT/'strategy/pa-hyp/PAH-TIME-002-result-v1.json').read_text(encoding='utf-8'))
    for group in ('source_hashes','evidence_hashes'):
        for path,digest in card[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    for name in ('primary','independent','hostile','lean'):
        cmd=[sys.executable,'-X','utf8',str(ROOT/f'verification/scripts/pah_time002_{name}.py'),'--check']
        if name=='lean':
            cmd+=['--lean-cache',str(a.lean_cache),'--elan-home',str(a.elan_home)]
        subprocess.run(cmd,cwd=ROOT,check=True)
    review=json.loads((ROOT/'strategy/pa-hyp/PAH-TIME-002-review-v1.json').read_text(encoding='utf-8'))
    assert review['note_sha256']==card['evidence_hashes'][review['note']]
    assert len(review['reviews'])==2
    assert all(v['status']=='ACCEPT_SCOPED' for v in review['reviews'])
    for path,digest in review['reviewed_hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    assert card['verdict']=='PROVED' and card['classification']=='negative_result'
    assert not card['active_gate_change'] and not card['physical_promotion']
    assert card['missing_physical_input']=='PAH-COMMON-OPERATIONAL-CLOCK-W'
    assert card['proof']['clock_horizon']=='S=T/epsilon^nu'
    assert card['proof']['bound']=='E_r(T)<=d_r^2*(Lambda*S+(Lambda*S)^2)'
    assert not card['follow_on']['automatic_successor']
    assert card['follow_on']['scientific_attempt_budget']==0
    print('TIME-002 INTEGRATED: PASS; scoped path freezing PROVED, no mainline/physical promotion')


if __name__=='__main__':
    main()
