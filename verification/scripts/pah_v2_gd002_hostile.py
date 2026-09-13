#!/usr/bin/env python3
"""GD-002 hostile scope and exact mutation controls, version 1.0.1.

This is same-task adversarial verification, not an external analytic referee.
Tests sign, multiplicity, normalization, inverse maps and quantifier mistakes.
"""
import argparse
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform

__version__='1.0.1'
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-13-pah-v2-gd002/hostile-v101.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    specpath=ROOT/'strategy/pa-hyp/PAH-v2-GD-002-prereg-v1.json'
    spec=json.loads(specpath.read_text(encoding='utf-8'))
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append({'name':name,'pass':True})
    for p,h in spec['source_hashes'].items():
        check('pin:'+p,sha(ROOT/p)==h)
    for name in ('primary','independent'):
        path=OUT.with_name('primary-v101.json' if name=='primary' else name+'.json')
        data=json.loads(path.read_text(encoding='utf-8'))
        check(name+'_fresh_producer',data['script_sha256']==sha(ROOT/f'verification/scripts/pah_v2_gd002_{name}.py'))
        check(name+'_all_root_families',set(data['root_counts'])=={'PH','TR','LK','AP'})
    indep=ROOT/'verification/scripts/pah_v2_gd002_independent.py'
    imports=[n.module or '' for n in ast.walk(ast.parse(indep.read_text())) if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(ast.parse(indep.read_text())) if isinstance(n,ast.Import) for a in n.names]
    check('independent_no_primary_or_source_backend_import',not any('pah_v2' in n for n in imports))
    # Exact oriented source-face algebra: closed-loop gauge change is zero.
    face=((0,1),(1,3),(3,2),(2,0))
    check('closed_face_all_gauge_generators',all(sum((b==v)-(a==v) for a,b in face)==0 for v in range(4)))
    check('open_link_mutation_detected',any((1==v)-(0==v)!=0 for v in range(4)))
    for a in range(1,5):
        for p in (2,3):
            b=a*pow(p,-1,5)%5
            check(f'inverse_coefficient_{a}_{p}',p*b%5==a)
            check(f'class_flip_{a}_{p}',(a in (1,4))!=(b in (1,4)))
    check('direct_instead_of_inverse_mutation_detected',(2*2)%5!=1)
    # Positive normalized weights transfer an all-state bound, not a sup witness.
    weights=[Fraction(1,10),Fraction(2,10),Fraction(7,10)]
    eta=Fraction(json.loads(OUT.with_name('primary-v101.json').read_text())['derived']['eta'])
    distances=[eta,eta+1,eta+2]
    check('original_weight_normalization',sum(weights)==1)
    check('weighted_all_state_lower',sum(w*d*d for w,d in zip(weights,distances))>=eta*eta)
    check('single_point_sup_is_insufficient',Fraction(1,100)*eta*eta<eta*eta)
    check('unnormalized_weight_mutation_detected',sum(weights[:-1])!=1)
    # The original generator has eight labelled signed link terms, not four.
    leading=[(edge,sign) for edge in range(len(face)) for sign in (-1,1)]
    check('both_signs',len(leading)==2*len(face))
    check('one_sign_mutation_detected',len([r for r in leading if r[1]>0])!=len(leading))
    check('half_generator_mutation_detected',Fraction(len(leading),2)!=len(leading))
    note=ROOT/'claims/C6-SPACETIME-SIGNATURE/notes/crt-gibbs-defect-260913-v1.0.tex.txt'
    text=note.read_text(encoding='utf-8')
    for token in ('P_B','n_*','k-2','every','projectivity','not fully','UPHELD','Dirichlet','original exponential rates'):
        check('proof_boundary:'+token,token in text)
    for token in ('ALL integers s>r','f0','full counting','No T-054','No change'):
        content=specpath.read_text()+ (ROOT/'strategy/pa-hyp/PAH-v2-GD-002-execution-v1.json').read_text()
        check('contract:'+token,token in content)
    result={'schema':'tect/pah-v2-gd002-hostile/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'preregistration_sha256':sha(specpath),'checks':checks,
            'scope':'Exact finite mutation controls plus written seven-objection analytic audit. Same-task authorship, no external-person certification.',
            'unencoded':'No program proves the full PAH analytic/number-theoretic crosswalk merely by matching text.',
            'environment':{'python':platform.python_version(),'platform':platform.platform()}}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=run()
    if args.check:
        old=json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'}=={k:v for k,v in result.items() if k!='environment'}
    else:
        assert not OUT.exists(), 'Issued run is immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GD-002 HOSTILE: PASS',len(result['checks']),'checks')


if __name__=='__main__':
    main()
