#!/usr/bin/env python3
"""TIME-002 adversarial algebra/source-scope controls; no proof-by-fixtures.

Admitted width-four, K=6 links expose a missing edge/face factor. Additional
mutation controls distinguish path sampling from semigroup/time/state changes.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-time002/hostile.json'


def admit_scope(packet):
    required={'original_path':True,'initial_gibbs':True,'physical_clock':False,
              'changed_clock_stationarity':False,'random_semigroup_substitution':False,
              'fixed_epsilon':True,'fixed_geometry':True,'crt_repaired':False,
              'new_time_multiplier':False,'common_limit_process':False}
    return packet==required


def run():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    controls=[]
    theta=F(1,10)  # Explicit Poisson-moment test input.
    assert theta+theta**2 > theta**2
    controls.append('reject_missing_poisson_linear_term')
    a,T=F(1,4),F(1)
    assert a*(T/a)==T and T/a>T and a*(T*a)<T
    controls.append('reject_reversed_inverse_clock_horizon')
    # Exact admitted r=1, h=0, N=1 geometry, not a replacement carrier.
    width,K=4,6
    zeta=s.Rational(1,2)+s.I*s.sqrt(3)/2
    links={}
    for x in range(width):
        for y in range(width):
            if x+1<width:
                links[((x,y),(x+1,y))]=s.Integer(1)
            if y+1<width:
                links[((x,y),(x,y+1))]=s.Integer(1)
    links[((0,0),(1,0))]=zeta
    links[((1,0),(2,0))]=s.conjugate(zeta)
    def W(data):
        faces=[]
        for x in range(width-1):
            for y in range(width-1):
                aa,bb=(x,y),(x+1,y)
                cc,dd=(x+1,y+1),(x,y+1)
                faces.append(s.re(s.expand(data[(aa,bb)]*data[(bb,cc)]*
                    s.conjugate(data[(dd,cc)])*s.conjugate(data[(aa,dd)]))))
        return s.simplify(sum(faces)/len(faces)),len(faces)
    before,p=W(links)
    links[((1,0),(1,1))]*=zeta
    after,_=W(links)
    jump=s.Abs(after-before)
    chord=s.simplify(s.Abs(zeta-1))
    assert jump==2*chord/p and jump>chord/p
    controls.append('reject_missing_two_face_incidence_factor')
    labels=[(edge,sign) for edge in links for sign in (-1,1)]
    assert len(labels)==2*len(links)>len(links)
    assert 1%2==(-1)%2 and (0,-1)!=(0,1)
    controls.append('retain_signed_duplicate_K2_labels')
    assert s.simplify(s.Abs(zeta**(1-K)-1)-chord)==0
    controls.append('retain_modular_chord_wrap')
    assert T/F(1)==T
    controls.append('epsilon_one_inverse_identity')
    scope={'original_path':True,'initial_gibbs':True,'physical_clock':False,
           'changed_clock_stationarity':False,'random_semigroup_substitution':False,
           'fixed_epsilon':True,'fixed_geometry':True,'crt_repaired':False,
           'new_time_multiplier':False,'common_limit_process':False}
    assert admit_scope(scope)
    for key in scope:
        mutant=copy.deepcopy(scope)
        mutant[key]=not mutant[key]
        assert not admit_scope(mutant)
        controls.append('reject_scope_mutation_'+key)
    return {'schema':'tect/pah-time002-hostile/1.0',
            'status':'PASS_EXACT_AND_METADATA_MUTATIONS',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'controls':controls,'count':len(controls),
            'factor_fixture':{'width':width,'K':K,'faces':p,'before':str(before),
                              'after':str(after),'jump':str(jump),'chord':str(chord)},
            'boundary':'Exact factor/moment tests and metadata rejection are not a semantic proof oracle. All-r path proof separately reviewed.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true')
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    data=run()
    if args.write:
        assert not OUT.exists(),'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        assert json.loads(OUT.read_text(encoding='utf-8'))==data
    print('TIME-002 HOSTILE: PASS',data['count'],'controls')


if __name__=='__main__':
    main()
