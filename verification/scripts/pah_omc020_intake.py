"""Validate frozen PAH-OMC-020 intake, NOT its temporal convergence theorem.

No simulation, numerical carrier or Lean result is produced by this tool.
The source pins and comparison contract are the only checked propositions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/'strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json'
WORK=ROOT/'strategy/pa-hyp/PAH-OMC-020-temporal-work.md'
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-intake/intake.json'
# Immutable input pin, not a derived mathematical constant.
CONTRACT_SHA256='906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute():
    checks=[]
    def ck(name, value):
        assert bool(value),name
        checks.append({'name':name,'pass':True})
    ck('immutable preregistration',digest(CONTRACT)==CONTRACT_SHA256)
    data=json.loads(CONTRACT.read_text(encoding='utf-8'))
    ck('contract identity',data['contract_id']=='PAH-OMC-020')
    for rel,pin in data['sources'].items():
        ck('source:'+rel,digest(ROOT/rel)==pin)
    for path in (CONTRACT,WORK,Path(__file__)):
        raw=path.read_bytes()
        ck('LF:'+path.name,b'\r' not in raw and raw.endswith(b'\n'))
        ck('UTF8:'+path.name,raw.decode('utf-8').encode('utf-8')==raw)
    parents={rel:json.loads((ROOT/rel).read_text(encoding='utf-8'))
             for rel in data['sources'] if rel.endswith('-result-v1.json')}
    ck('registered inherited result IDs',sorted(x['result_id'] for x in parents.values())==['R-510','R-511','R-512'])
    ck('parent gate firewall',all(not x['active_gate_change'] and not x['physical_promotion'] for x in parents.values()))
    ck('finite target and comparison present',all(data['objects_and_comparison'][k]
       for k in ('S_nj','finite_semigroup','target_semigroup','target_quantifiers','topology_boundary')))
    # Hostile tooling control: changing one source byte must change its pin.
    with tempfile.TemporaryDirectory(prefix='pah020-pin-control-') as temp:
        altered=Path(temp)/'altered-input.json'
        altered.write_bytes(CONTRACT.read_bytes()+b' ')
        ck('reject source mutation',digest(altered)!=CONTRACT_SHA256)
    return {'schema':'tect/pah-omc020-intake/1.0','status':'INTAKE_PASS_NOT_TEMPORAL_PROOF',
            'checks':checks,'code_version':__version__,'code_sha256':digest(Path(__file__)),
            'contract_sha256':digest(CONTRACT),'work_sha256':digest(WORK),
            'temporal_verdict':'IN_PROGRESS','claim_or_gate_promotion':False,
            'lean_status':'NOT_RUN_FOR_OMC020','independent_temporal_verifier':'NOT_YET_EXECUTED',
            'next_action':'Prove and independently verify the fixed-n sampling/closed-form bridge and weak-liminf property; retain anchored n minimal-selection obligation.',
            'non_claims':data['non_claims']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true')
    args=p.parse_args();result=compute()
    encoded=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode('utf-8')
    if args.check:
        assert RUN.read_bytes()==encoded,'intake replay mismatch'
    else:
        RUN.parent.mkdir(parents=True,exist_ok=True);RUN.write_bytes(encoded)
    print(f"PAH-OMC-020 INTAKE: PASS ({len(result['checks'])} input checks; temporal proof IN_PROGRESS)")


if __name__=='__main__':
    main()
