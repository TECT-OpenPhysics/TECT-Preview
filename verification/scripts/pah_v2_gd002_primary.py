#!/usr/bin/env python3
"""GD-002 source-root and exact cyclotomic checks, version 1.0.1.

The general proof is the synthesis: these fixtures do not extrapolate a tail.
Original rates are NOT replaced by unit rates: the unit part is an algebraic
decomposition, accompanied by an analytic uniform remainder bound.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys
import sympy as sp
from flint import arb, ctx

__version__ = '1.0.1'
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'codes/foundations'))
import pah_v2_morton_crt as maps
import pah_v2_root_enumerator as en
PLAN = ROOT/'strategy/pa-hyp/PAH-v2-GD-002-execution-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-13-pah-v2-gd002/primary-v101.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    pp = ROOT/plan['preregistration']['path']
    assert sha(pp) == plan['preregistration']['sha256']
    spec = json.loads(pp.read_text(encoding='utf-8'))
    for path, digest in spec['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    inputs = plan['frozen_probe']
    assert all(inputs[k] == 1 for k in ('epsilon','beta','nu','kappa_D','kappa_g','q0','m0','R0'))
    W, edges, faces = maps.geometry(inputs['h'], inputs['N'])
    assert len(faces) == 1  # Explicit frozen probe, not all geometries.
    face = faces[0]
    modulus = inputs['observable_modulus']
    baseK = maps.regulator(maps.Index(inputs['r0'],0,0)).K
    assert baseK % modulus == 0
    X = sp.Symbol('X')
    phi = sp.cyclotomic_poly(modulus,X)

    def character(k):
        return X**(k % modulus)

    def flux(x):
        return sum(sign*x.link[e] for e,sign in face)

    counts = Counter()
    rows = []
    for r in plan['bounded_fixtures']['root_cutoffs']:
        idx = maps.Index(r,0,0)
        reg = maps.regulator(idx)
        a = pow(reg.K//baseK,-1,modulus)
        x = en.State(tuple(v % (reg.M_s+1) for v in range(reg.vertices)),
                     (reg.Q,)+(0,)*(reg.vertices-1),
                     tuple(v % reg.K for v in range(reg.vertices)),
                     tuple((3*e+1) % reg.K for e in range(len(edges))))
        assert en.valid_state(reg,x)
        y = x
        for k in range(r,inputs['r0'],-1):
            y = maps.project(y,maps.Index(k,0,0),0)
        assert (flux(y)-a*flux(x)) % modulus == 0
        leading = 0
        for root,z in en.incidences(reg,x):
            counts[root.family] += 1
            increment = character(a*(flux(z)-flux(x)))-1
            if root.family != 'LK':
                assert increment == 0  # A zero observable increment, not a zero rate.
            leading += increment
        predicted = len(edges)*(character(a)+character(-a)-2)
        assert sp.rem(leading-predicted,phi,X) == 0
        # Full gauge group: each vertex generator telescopes on the closed face.
        for v in range(reg.vertices):
            gauge_flux = sum(sign*((1 if edges[e][1]==v else 0)-(1 if edges[e][0]==v else 0)) for e,sign in face)
            assert gauge_flux == 0
        rows.append({'r':r,'K':reg.K,'a':a,'leading_polynomial':str(sp.rem(leading,phi,X))})
    assert set(counts) == set(en.FAMILIES)
    eigen = {a:sp.simplify(len(edges)*(2*sp.cos(2*sp.pi*a/modulus)-2)) for a in range(1,modulus)}
    flips = []
    for a in range(1,modulus):
        for prime_residue in (2,3):  # Exhaustive nonresidue INPUT classes modulo five.
            b = a*pow(prime_residue,-1,modulus) % modulus
            square = sp.simplify((eigen[b]-eigen[a])**2)
            expected = len(edges)**2*modulus
            assert square == expected
            flips.append({'a':a,'prime_residue':prime_residue,'b':b,'gap_squared':str(square)})
    # DERIVED conservative constants from the original one-face functional.
    pi_upper = sp.Integer(4)  # Analytic inequality pi<4; interval-checked below.
    amplitude_upper = sp.Rational(inputs['R0']*inputs['q0'],inputs['m0'])
    deltaF_coeff = 2*pi_upper*(inputs['kappa_D']*amplitude_upper**2+inputs['kappa_g'])
    signed_links = 2*len(edges)
    residual_coeff = signed_links*2*deltaF_coeff  # |character increment|<=2.
    pair_coeff = 2*residual_coeff
    first_safe = inputs['r0']
    while maps.regulator(maps.Index(first_safe,0,0)).K < max(pair_coeff,deltaF_coeff):
        first_safe += 1
    gap_lower = 2*len(edges)  # sqrt(5)>2, derived from exact gap square.
    eta = gap_lower-1
    assert eta > 0
    ctx.prec = 128
    assert arb.pi() < int(pi_upper)
    assert arb(1).exp() < 3
    # Nontriviality: original nonnegative F is bounded by this constant.
    Fupper = (sp.Rational(1,6)*amplitude_upper**6 + sp.Rational(1,2)*amplitude_upper**2
              + sp.Rational(len(edges),2)*amplitude_upper**2+2*len(faces))
    energy_lower_factor = len(edges)  # min 2(1-cos(2pi*a/5))>1.
    assert sp.simplify(2*(1-sp.cos(2*sp.pi/modulus))-1) > 0
    # One finite Euclid/CRT replay. General construction is proved in the note.
    small = maps.primes(first_safe+1)
    product = sp.prod(p for p in small if p != modulus)
    t = pow(int(product),-1,modulus)
    witness_integer = 1+t*product
    factors = sp.factorint(witness_integer)
    assert witness_integer % modulus == 2
    assert all(witness_integer % p == 1 for p in small if p!=modulus)
    candidates = [int(p) for p in factors if int(p)%modulus in (2,3)]
    assert candidates and all(p>small[-1] for p in candidates)
    return {'schema':'tect/pah-v2-gd002-primary/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'execution_sha256':sha(PLAN),'preregistration_sha256':sha(pp),
            'source_hashes':spec['source_hashes'],'root_counts':dict(counts),
            'geometry':{'W':W,'edges':[list(e) for e in edges],'face':[list(e) for e in face]},'fixtures':rows,
            'cyclotomic_eigenvalues':{str(k):str(v) for k,v in eigen.items()},'all_residue_flips':flips,
            'derived':{k:str(v) for k,v in {'deltaF_coeff':deltaF_coeff,'residual_coeff':residual_coeff,
                'pair_coeff':pair_coeff,'safe_cutoff':first_safe,'gap_lower':gap_lower,'eta':eta,
                'Fupper':Fupper,'energy_lower_factor':energy_lower_factor}.items()},
            'euclid_fixture':{'threshold_prime':small[-1],'product':int(product),'t':t,'integer':int(witness_integer),
                              'factors':{str(k):int(v) for k,v in factors.items()},'new_nonresidue_primes':candidates},
            'checks':[{'name':n,'pass':True} for n in ['source_pins','complete_signed_roots','gauge_telescoping',
                'fixed_character_pullbacks','cyclotomic_gap_all_residues','analytic_constant_arithmetic',
                'directed_pi_and_exp_bounds','constructive_prime_fixture']],
            'evidence_boundary':'Fixtures check implementation only. General rate, tail, Gibbs and nontriviality inequalities require the written all-state proof. No Gibbs replacement or simulation extrapolation.',
            'environment':{'python':platform.python_version(),'sympy':sp.__version__,'platform':platform.platform()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    result = run()
    if args.check:
        old = json.loads(OUT.read_text(encoding='utf-8'))
        assert {k:v for k,v in old.items() if k!='environment'} == {k:v for k,v in result.items() if k!='environment'}
    else:
        assert not OUT.exists(), 'Issued run is immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GD-002 PRIMARY: PASS',len(result['checks']),'checks; derived',result['derived'])


if __name__ == '__main__':
    main()
