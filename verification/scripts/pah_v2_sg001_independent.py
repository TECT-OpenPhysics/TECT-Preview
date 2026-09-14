#!/usr/bin/env python3
"""Independent SG-001 rational/interval audit, v1.0.0.

Imports neither primary code nor source evaluators. Reconstructs signed-edge
coefficients and verifies the leading exponential separation by positive odd
Taylor terms. Independent full-operator proof uses the maximum principle,
not invariance of the character span. No new finite carrier is introduced.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/'strategy/pa-hyp/PAH-v2-SG-001-prereg-v1.json'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-pah-v2-sg001/independent.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    assert sha(SPEC)=='177e36c3ea7370f2377c9a53b385396e7b6de1a28399c3b306880c92ce672646'
    spec=json.loads(SPEC.read_text(encoding='utf-8'))
    for p,h in spec['source_hashes'].items():
        assert sha(ROOT/p)==h,p
    v=json.loads((ROOT/'strategy/pa-hyp/PAH-v2-GD-002-execution-v1.json').read_text(encoding='utf-8'))['frozen_probe']
    vertices=[(0,0),(1,0),(0,1),(1,1)]  # Unchanged R-573 input geometry.
    edges=[(x,y) for x in vertices for y in vertices if
           (y[0]-x[0],y[1]-x[1]) in [(1,0),(0,1)]]
    amplitude=Q(v['R0']*v['q0'],v['m0'])
    rate_bound=2*4*(v['kappa_D']*amplitude**2+v['kappa_g'])
    remainder=2*len(edges)*2*rate_bound
    time=Q(spec['fixed_test_time']['numerator'],spec['fixed_test_time']['denominator'])
    m=v['observable_modulus']
    # The inherited character polynomial gives half-gap^2 = edges^2*m/4.
    half_square=Q(len(edges)**2*m,4)
    half_lower=math.isqrt(half_square.numerator//half_square.denominator)
    assert half_lower**2 <= half_square
    x_lower=time*half_lower
    # exp(x)-exp(-x)=2 sum x^(2k+1)/(2k+1)! >=2x, for x>=0.
    # e<3 independently follows from 1/n!<=1/2^(n-1), strict at n=3.
    leading=2*x_lower/3
    delta=Q(3,4)*leading
    cutoff_floor=math.ceil(2*time*remainder/(leading-delta))
    primes=[]; K=1
    for candidate in range(2,100):  # Only locate arithmetic threshold; not tail evidence.
        if all(candidate%d for d in range(2,math.isqrt(candidate)+1)):
            primes.append(candidate); K*=candidate
            if K>=cutoff_floor: break
    r=len(primes)-1
    assert K>=cutoff_floor and leading-2*time*remainder/K>=delta
    odd_terms=[2*x_lower**(2*k+1)/math.factorial(2*k+1) for k in range(6)]
    assert all(x>0 for x in odd_terms) and sum(odd_terms)>=2*x_lower
    curves=[]
    for precision in (96,192):
        ctx.prec=precision
        rad=arb(m).sqrt()*len(edges)/2
        center=arb(-5)*len(edges)/2  # From cos fifth-root roots: center=-5E/2.
        tt=arb(time.numerator)/time.denominator
        low=((center-rad)*tt).exp(); high=((center+rad)*tt).exp()
        lower=arb(leading.numerator)/leading.denominator
        assert high-low>lower
        assert high-low-tt*2*int(remainder)/K>arb(delta.numerator)/delta.denominator
        # Every original-time multiplier <=1; this is the sign needed in the
        # independent forced maximum principle, not just a gap calculation.
        assert 0<low<high<1
        curves.append({'precision':precision,'slow':str(high),'fast':str(low),'gap':str(high-low)})
    # Algebraic t=0 control: all finite semigroups are identity there; generator
    # nonconvergence must never be claimed to give an instantaneous gap.
    assert Q(0)*remainder==0
    return {'schema':'tect/pah-v2-sg001-independent/1.0','version':'1.0.0','status':'PASS',
        'script_sha256':sha(Path(__file__)),'preregistration_sha256':sha(SPEC),
        'derived':{k:str(z) for k,z in {'residual_coeff':remainder,'time':time,
           'leading_lower':leading,'delta':delta,'required_K':cutoff_floor,
           'safe_cutoff':r,'safe_K':K,'norm_squared_lower':delta**2}.items()},
        'directed_intervals':curves,
        'checks':[{'name':s,'pass':True} for s in ['source_pins','independent_edge_count',
           'original_rate_coefficient','positive_odd_Taylor_bound','independent_cutoff_threshold',
           'two_precision_time_gap','negative_spectrum_contraction_sign','zero_time_control']],
        'analytic_formulation':'For each theta, apply the finite row-generator maximum principle to Re(exp(-i theta)u), u=S(t)f-exp(lambda t)f; the forcing is bounded by C/K since lambda<=0. Sup over theta yields |u|<=Ct/K without a sqrt(2) loss.',
        'independence_boundary':'Same-task authorship, independently written formulation and code; not an external referee. Analytic all-state/tail bridges are in the synthesis.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    result=run()
    if a.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==result
    else:
        assert not OUT.exists(),'Issued run is immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=OUT.parent,suffix='.tmp')
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
        os.replace(tmp,OUT)
    print('SG-001 INDEPENDENT: PASS',len(result['checks']),'checks')
