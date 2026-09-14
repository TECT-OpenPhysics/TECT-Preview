#!/usr/bin/env python3
"""Hostile definition controls and boundary coverage, version 1.0.0.

No model changes, rates or dynamics. Symbolic all-W fringe identity is
separate from finite geometry checks and documentary admission firewalls.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sympy as sp
import sys

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'codes/foundations'))
import pah_v2_morton_crt as implementation
BASE = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-comparison'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    contract = ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-contract-v1.json'
    assert sha(contract) == '7b58978a2bead7e011196f4712323a3cc7ef17bd0285e3dfbbabb6698221a152'
    spec = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-admission-prereg.json').read_text(encoding='utf-8'))
    bundle = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-bundle.json').read_text(encoding='utf-8'))
    for path,h in {**bundle['source_pins'],**bundle['evidence_hashes']}.items():
        assert sha(ROOT/path) == h,path
    W = sp.Symbol('W',integer=True,positive=True)
    fringe = sp.expand((2*W-1)**2-4*(W-1)**2)
    assert sp.simplify(fringe-(4*W-3)) == 0
    # The all-W positive bound follows from W>=2: 4W-3>=5.
    # W=2 is an explicit endpoint oracle, not a fitted value.
    assert fringe.subs(W,2)>0 and sp.diff(fringe,W)>0
    geometries = sorted(set((c['co'][1],c['co'][2]) for c in spec['fixtures']))
    rows = []
    for h,N in geometries:
        width,edges,faces = implementation.geometry(h,N)
        fine_width,fine_edges,fine_faces = implementation.geometry(h+1,N)
        assert len(faces)==(width-1)**2 and len(fine_faces)==(fine_width-1)**2
        image_faces = 4*len(faces)
        actual = len(fine_faces)-image_faces
        assert actual==int(fringe.subs(W,width)) and actual>0
        for eds,fs in ((edges,faces),(fine_edges,fine_faces)):
            for face in fs:
                net = Counter()
                for e,sign in face:
                    a,b = eds[e]
                    net[a]-=sign
                    net[b]+=sign
                assert all(v==0 for v in net.values())
        rows.append({'h':h,'N':N,'W':width,'coarse_faces':len(faces),
                     'fine_faces':len(fine_faces),'additional_fringe_faces':actual})
    primary = json.loads((BASE/'primary.json').read_text(encoding='utf-8'))
    independent = json.loads((BASE/'independent.json').read_text(encoding='utf-8'))
    assert independent['primary_sha256']==sha(BASE/'primary.json')
    assert primary['counts']['root_incidences']==independent['counts']['root_incidences']
    assert all(c['unpaired']>0 for c in independent['root_counts'])
    lean = json.loads((BASE/'lean.json').read_text(encoding='utf-8'))
    assert lean['status']=='PASS_PARAMETERIZED_ALGEBRA' and lean['exit_code']==0
    # Scope guards are document checks, explicitly not additional math proofs.
    assert 'not_encoded' in lean and 'Concrete grid' in lean['not_encoded']
    assert 'not an external human referee' in independent['independence']
    source = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-draft.json').read_text(encoding='utf-8'))
    assert source['future_defects']['status']=='NOT_EVALUATED_NO_APPROVED_CONTRACT'
    assert source['ordered_limits']['order'][0:3]==['LOCAL_STATE_CUTOFF','LATTICE_REFINEMENT','VOLUME_EXHAUSTION']
    return {'schema':'tect/pah-v2-comparison-hostile/1.0','status':'PASS_SCOPED_HOSTILE_CHECKS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'operative_sha256':sha(contract),'sympy_version':sp.__version__,
            'source_preserved':True,'fringe_identity':str(fringe),'boundary_rows':rows,
            'fresh_evidence_hashes':{f'{name}.json':sha(BASE/f'{name}.json') for name in ('primary','independent','lean')},
            'mathematical_controls':independent['hostile'],
            'documentary_guards':{'Lean_full_model_promotion':False,'external_referee_claim':False,'limit_order_changed':False},
            'explicit_boundaries':['Extra outer fringe is part of the exact fine complex; pure-subdivision claim is rejected.',
                                   'Root assignment is endpoint bookkeeping, not a gauge-equivariant root-Hilbert operator.',
                                   'Owner adoption does not certify a mathematical or physical theorem.'],
            'non_claims':spec['non_claims']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    out = BASE/'hostile.json'
    if args.check:
        assert json.loads(out.read_text(encoding='utf-8'))==result
    else:
        out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PAH-V2-COMPARISON HOSTILE: PASS; full-W fringe identity and',len(result['boundary_rows']),'geometry checks')


if __name__=='__main__':
    main()
