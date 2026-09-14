#!/usr/bin/env python3
"""GD-001 exact adversarial tests and evidence comparison, version 1.0.0.

Mutation oracles are tests, not substitutes for the written all-index proof.
No dynamics-model implementation is imported. Scope controls prohibit
claiming Gibbs-L2 or physical failure from the present sup-norm witness.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import subprocess

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-gd001'
OUT = RUNS/'hostile.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scalar_action(M,j):
    f = lambda k: int(k<M)
    return sum(f(j+sigma)-f(j) for sigma in (-1,1) if 0<=j+sigma<=M)


def run():
    primary = json.loads((RUNS/'primary.json').read_text(encoding='utf-8'))
    independent = json.loads((RUNS/'independent.json').read_text(encoding='utf-8'))
    assert primary['fixtures'] == independent['fixtures']
    assert primary['root_counts'] == independent['root_counts']
    assert primary['source_hashes'] == independent['source_hashes']
    for p,h in primary['source_hashes'].items():
        assert sha(ROOT/p) == h
    tests = []
    def check(name,actual,expected):
        assert actual == expected,name
        tests.append({'name':name,'actual':actual,'expected':expected,'pass':True})
    # INPUT witness M=1 (base boundary); independent direct action, not a
    # preassigned defect. Other fixtures below test nonadjacent interval ends.
    M = 1
    j = 2*M-2
    fine,coarse = scalar_action(2*M,j),scalar_action(M,j//2)
    defect = fine-coarse
    check('base_endpoint_fine',fine,0)
    check('base_endpoint_coarse',coarse,-1)
    check('actual_defect',defect,1)
    check('reject_reversed_sign',coarse-fine != defect,True)
    check('reject_extra_half',Fraction(defect,2) != defect,True)
    check('reject_coarse_root_omission',fine != defect,True)
    check('reject_hidden_label_quotient',0 != defect,True)
    for row in primary['fixtures']:
        r,s,D = row['r'],row['s'],row['D']
        Ms = 2**s
        values = {v['j']:v['defect'] for v in row['values']}
        check(f'{r}_{s}_positive_endpoint_cancels',values[Ms],0)
        check(f'{r}_{s}_fine_negative_endpoint_cancels',values[Ms-1],0)
        check(f'{r}_{s}_band_left_included',values[Ms-D],1)
        check(f'{r}_{s}_band_count',sum(values.values()),D-1)
        # Adjacent-only evidence is not the all-pair proof; this explicit
        # nonadjacent fixture tests a genuinely wider interval.
        if D>2:
            check('reject_single_point_band',sum(values.values())!=1,True)
            check('full_state_odd_j_included',any(j%2 and val for j,val in values.items()),True)
    lean = json.loads((RUNS/'lean.json').read_text(encoding='utf-8'))
    check('fresh_kernel_exit',lean['exit_code'],0)
    check('parameterized_tail_marker','unbounded_tail_witness' in lean['declarations'],True)
    source = (ROOT/'verification/scripts/pah_v2_gd001_independent.py').read_text(encoding='utf-8')
    check('nonimporting_independent','import pah_v2_' not in source,True)
    spec = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-GD-001-prereg-v1.json').read_text(encoding='utf-8'))
    check('full_norm',spec['norm']['kind'],'FULL_STATE_SUP')
    check('fixed_f0',spec['observables']['fixed_base'],True)
    check('all_pairs',spec['quantifiers']['pair_scope'],'ALL_TAIL_PAIRS')
    return {'schema':'tect/pah-v2-gd001-hostile/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'evidence_hashes':{name:sha(RUNS/name) for name in ('primary.json','independent.json','lean.json')},
            'checks':tests,'check_count':len(tests),
            'analytic_audit':'Synthesis sections 2-5 check every family, both endpoints, one fixed f0, all-state floor interval and arbitrary tail. Same-task authorship; external referee NOT_PERFORMED.',
            'upheld_boundaries':['No Gibbs-L2 inference','No all-parameter no-go','No changed source, norm, state or time','No physical promotion'],
            'environment':{'python':platform.python_version(),'platform':platform.platform(),
                           'producer_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()},
            'seeds':None,'non_claims':'No physical Pre-A, spacetime, QFT, gravity, continuum or TOE.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args = ap.parse_args()
    result = run()
    if args.check:
        old = json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'} == {k:v for k,v in result.items() if k!='environment'}
    else:
        assert not OUT.exists(), 'Issued run is immutable; use --check'
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GD-001 HOSTILE: PASS',result['check_count'],'exact/sign/endpoint/scope checks')


if __name__ == '__main__':
    main()
