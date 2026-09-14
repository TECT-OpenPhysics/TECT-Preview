#!/usr/bin/env python3
"""SG-001 exact coefficient and finite-time error audit, v1.0.0.

This is not a finite-state simulation. The all-state and all-tail proof is
the synthesis. R-573's original source decomposition is reproduced separately.
Derived constants are recomputed from the pinned geometry and original inputs.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import sympy as sp
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/'strategy/pa-hyp/PAH-v2-SG-001-prereg-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-pah-v2-sg001/primary.json'
SPEC_HASH = '177e36c3ea7370f2377c9a53b385396e7b6de1a28399c3b306880c92ce672646'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    assert sha(SPEC) == SPEC_HASH
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for path, digest in spec['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    parent = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-GD-002-result-v1.1.json').read_text(encoding='utf-8'))
    for path, digest in parent['evidence_hashes'].items():
        assert sha(ROOT/path) == digest, path
    old = json.loads((ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-13-pah-v2-gd002/primary-v101.json').read_text(encoding='utf-8'))
    probe = json.loads((ROOT/'strategy/pa-hyp/PAH-v2-GD-002-execution-v1.json').read_text(encoding='utf-8'))['frozen_probe']
    count = len(old['geometry']['edges'])
    signed_count = 2*count
    modulus = probe['observable_modulus']
    amp = sp.Rational(probe['R0']*probe['q0'], probe['m0'])
    pi_upper = 4  # Analytic bound pi<4, not a fitted model constant.
    rate_coeff = 2*pi_upper*(probe['kappa_D']*amp**2+probe['kappa_g'])
    residual = signed_count*2*rate_coeff
    assert str(residual) == old['derived']['residual_coeff']
    time = sp.Rational(spec['fixed_test_time']['numerator'], spec['fixed_test_time']['denominator'])
    eigen = sorted(set(sp.simplify(count*(2*sp.cos(2*sp.pi*a/modulus)-2)) for a in range(1,modulus)), key=float)
    assert len(eigen) == 2 and all(x < 0 for x in eigen)
    center = sp.simplify(-(eigen[0]+eigen[1])/2)
    radius = sp.simplify((eigen[1]-eigen[0])/2)
    radius_square = sp.simplify(radius**2)
    radius_lower = math.isqrt(int(radius_square))
    assert radius_lower**2 <= radius_square and center*time == 1
    exp_denominator = 3  # Analytic e<3 bound, independently interval-checked.
    leading_lower = 2*radius_lower*time/exp_denominator
    allocation = sp.Rational(3,4)  # Proof slack allocation, not model input.
    delta = allocation*leading_lower
    pair_numerator = 2*time*residual
    required_K = int(sp.ceiling(pair_numerator/(leading_lower-delta)))
    primes, K, r = [], 1, -1
    candidate = 2
    while K < required_K:
        if all(candidate % p for p in primes if p*p <= candidate):
            primes.append(candidate)
            K *= candidate
            r += 1
        candidate += 1
    assert r >= probe['r0']
    margin = leading_lower-pair_numerator/K
    assert margin >= delta > 0
    # Explicit variation-of-constants integrand sign and endpoint checks.
    t,u,lam = sp.symbols('t u lam', real=True)
    weight = sp.exp(lam*u)
    integral = (sp.exp(lam*t)-1)/lam
    assert sp.simplify(sp.diff(integral,t)-sp.exp(lam*t)) == 0
    assert sp.limit(integral,lam,0) == t
    assert sp.diff(weight,u) == lam*weight
    intervals = []
    for precision in (96,192):  # Tooling precisions, not cutoff samples.
        ctx.prec = precision
        assert arb.pi() < pi_upper and arb(1).exp() < exp_denominator
        ev = {a: count*(2*(2*arb.pi()*a/modulus).cos()-2) for a in range(1,modulus)}
        tt = arb(int(time.p))/int(time.q)
        for a in range(1,modulus):
            for residue in (2,3):  # Exhaustive inherited flip classes mod five.
                b = a*pow(residue,-1,modulus) % modulus
                gap = abs((tt*ev[b]).exp()-(tt*ev[a]).exp())
                assert gap > arb(int(leading_lower.p))/int(leading_lower.q)
                assert gap-tt*2*int(residual)/K > arb(int(delta.p))/int(delta.q)
        intervals.append({'precision':precision,'gap_enclosure':str(gap)})
    # Test oracles cross-check independently derived, exact rational outputs.
    assert (time, delta, required_K, r) == (sp.Rational(1,10),sp.Rational(1,5),768,4)
    return {'schema':'tect/pah-v2-sg001-primary/1.0','version':'1.0.0','status':'PASS',
        'script_sha256':sha(Path(__file__)),'preregistration_sha256':sha(SPEC),
        'source_hashes':spec['source_hashes'],
        'derived':{k:str(v) for k,v in {'edge_count':count,'rate_coeff':rate_coeff,
            'residual_coeff':residual,'time':time,'center':center,'radius':radius,
            'leading_lower':leading_lower,'pair_numerator':pair_numerator,'delta':delta,
            'norm_squared_lower':delta**2,'required_K':required_K,'safe_cutoff':r,
            'safe_K':K,'safe_margin':margin}.items()},
        'eigenvalues':[str(x) for x in eigen],'directed_intervals':intervals,
        'checks':[{'name':x,'pass':True} for x in ['source_and_evidence_pins',
            'original_residual_recomputed','exact_two_eigenvalues','fixed_original_time',
            'variation_of_constants_scalar_identity','rational_uniform_slack',
            'all_residue_time_gaps_two_precisions','positive_squared_Gibbs_lower']],
        'scope':'Analytic coefficient checks; no new state simulation, new carrier or limiting semigroup construction.'}


def save_or_check(result, path, check):
    if check:
        assert json.loads(path.read_text(encoding='utf-8')) == result
    else:
        assert not path.exists(), 'Issued run is immutable; use --check'
        path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp = tempfile.mkstemp(dir=path.parent,suffix='.tmp')
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,sort_keys=True,indent=2); f.write('\n')
        os.replace(tmp,path)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=run(); save_or_check(result,OUT,args.check)
    print('SG-001 PRIMARY: PASS',len(result['checks']),'checks;',result['derived'])
