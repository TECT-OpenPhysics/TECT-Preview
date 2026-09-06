"""Adversarial PAH-OMC-017 controls; fixtures are not a convergence proof.

Mutations remove endpoint halves/frontier terms and invalidate spectral or
ratio hypotheses. Imports the primary only to attack it, never as an
independent lane. No candidate state or source file is modified.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as s
import pah_omc017_transfer as target

__version__='1.0.0'
ROOT=target.ROOT
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc017-cauchy/hostile.json'


def main(output):
    checks=[]
    def check(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    full,exact,parts=target.energies(2,5)
    check('unaltered_factorization_control',full==exact)
    check('missing_frontier_rejected',target.energies(2,5,terminal=False)[1]!=full)
    check('missing_endpoint_halves_rejected',target.energies(2,5,halves=False)[1]!=full)
    check('frontier_mutation_exact_delta',full-target.energies(2,5,terminal=False)[1]==parts['square']>0)
    check('half_mutation_exact_delta',full-target.energies(2,5,halves=False)[1]==parts['endpoint_half']>0)
    r,t,J=s.symbols('r t J')
    check('covariant_half_mutation_rejected',s.expand(J*(r-t)**2-J*(r-t)**2/2)!=0)
    check('Gibbs_sign_mutation_rejected',full>0 and -full!=full)
    check('label_quotient_changes_count',2**(8*2+12)!=2**(8*2+12-2*(2+2)))
    # Positive-but-not-improving periodic matrix: missing strictness is fatal.
    periodic=s.Matrix([[0,1],[1,0]])
    check('positivity_alone_not_peripheral_gap',periodic**2==s.eye(2) and set(periodic.eigenvals())=={-1,1})
    # Non-normal spectral radius zero need not imply norm below one.
    nilpotent=s.Matrix([[0,10],[0,0]])
    check('nonnormal_norm_shortcut_rejected',nilpotent**2==s.zeros(2) and nilpotent.norm()>1)
    P=s.Matrix([[1,0],[0,0]]); A=s.zeros(2)
    check('k_zero_residual_not_A_zero',s.eye(2)-P!=A**0)
    check('k_positive_identity_control',(P+A)**2==P+A**2)
    # A denominator perturbation near -1 defeats an unconditional 4t bound.
    delta=Q(-99,100); err=Q(1,100); a=Q(1); F=Q(1); t0=abs(delta)
    check('half_denominator_hypothesis_necessary',abs((a+err)/(1+delta)-a)>4*F*t0)
    c=json.loads((ROOT/target.PREREG).read_text())
    check('prereg_hash',target.sha(ROOT/target.PREREG)==target.PIN)
    for path,pin in c['sources'].items(): check('source_preserved:'+path,target.sha(ROOT/path)==pin)
    check('no_conditional_comparison_map','coordinate forgetting' in c['common_observable_algebra']['embeddings'])
    check('no_temporal_transfer_import','not a new carrier' in c['exact_spatial_transfer_proposal']['role'])
    check('numeric_gap_not_claimed','not a certified numerical value' in c['proof_plan_and_budget']['quantitative_convention'])
    check('zero_amplitude_labels_retained','Phases at r=0 are retained' in c['scope']['state'])
    data={'lane':'hostile','status':'PASS','checks':checks,
        'code_sha256':target.sha(Path(__file__)),'code_version':__version__,
        'mutant_deltas':{k:str(v) for k,v in parts.items()},
        'scope':'Internal adversarial controls, not a negative result for PAH or an external signed review.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-017 HOSTILE: PASS ({len(checks)} checks)')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    main(parser.parse_args().output)
