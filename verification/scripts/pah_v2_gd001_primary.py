#!/usr/bin/env python3
"""GD-001 exact full-labelled-generator diagnostic, version 1.0.0.

The analytic all-index proof is separate. This script checks its reduction
against the unchanged full source enumerator/maps on preregistered fixtures.
All non-AP observable increments vanish individually; their finite positive
rates are not set to zero. AP rates are exactly unity at epsilon=1.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import sympy as sp

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'codes/foundations'))
import pah_v2_morton_crt as maps
import pah_v2_root_enumerator as en

PLAN = ROOT/'strategy/pa-hyp/PAH-v2-GD-001-execution-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-gd001/primary.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pins():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    prereg = ROOT/plan['preregistration']['path']
    assert sha(prereg) == plan['preregistration']['sha256']
    spec = json.loads(prereg.read_text(encoding='utf-8'))
    for p,h in spec['source_hashes'].items():
        assert sha(ROOT/p) == h,p
    return plan,spec


def symbolic_ap_reduction(edges, faces):
    """Displayed parent polynomial, with generic real phase-cosine symbols.

    |psi_w-U psi_v|^2=a_w^2+a_v^2-2*a_w*a_v*cos(theta).
    The identity is structural for every phase/occupation tuple, not fitted
    to the zero-label witness. Exact source-to-expression audit is in the note.
    """
    V = 1 + max(v for e in edges for v in e)
    eps, M = sp.symbols('epsilon M',positive=True)
    js = sp.symbols('j:'+str(V))
    amplitudes = sp.symbols('a:'+str(V),real=True)
    ce = sp.symbols('ce:'+str(len(edges)),real=True)
    cp = sp.symbols('cp:'+str(len(faces)),real=True)
    ls,m2,l4,e6,g,ks,kD,kg = sp.symbols('lambda_s m2 lambda_4 eta_6 g kappa_s kappa_D kappa_g')
    s = [eps+j*(1-eps)/M for j in js]
    J = [2/(s[v]+s[w]) for v,w in edges]
    F = sum(ls*(sv-1)**2/2+m2*a**2/2+l4*a**4/4+e6*a**6/6+g*sv**2*a**2/2
            for sv,a in zip(s,amplitudes))
    F += ks*sum((s[v]-s[w])**2 for v,w in edges)/2
    F += kD*sum(J[i]*(amplitudes[w]**2+amplitudes[v]**2-2*amplitudes[w]*amplitudes[v]*ce[i])
                for i,(v,w) in enumerate(edges))/2
    F += kg*sum(sum(J[e] for e,_ in face)/len(face)*(1-cp[i]) for i,face in enumerate(faces))
    unit = sp.expand(F.subs(eps,1))
    assert not (set(js) & unit.free_symbols)
    for j in js:
        for sign in (-1,1):
            assert sp.expand(unit.subs(j,j+sign)-unit) == 0
    return {'functional_at_epsilon_one':str(unit),
            'all_j_absent':True,'generic_phase_and_amplitude_symbols':True,
            'AP_delta_F':'0','AP_mobility':'1','AP_rate':'1',
            'assertions':[{'name':'all_aperture_coordinates_drop_out','pass':True},
                          {'name':'every_AP_sign_preserves_full_displayed_F','pass':True}]}


def project_to(x, cutoff, target):
    while cutoff > target:
        x = maps.project(x,maps.Index(cutoff,0,0),0)
        cutoff -= 1
    return x


def observable(x,cutoff):
    return int(project_to(x,cutoff,0).aperture[0] == 0)


def generator(x,cutoff,counts):
    reg = maps.regulator(maps.Index(cutoff,0,0))
    fx = observable(x,cutoff)
    terms = []
    for root,y in en.incidences(reg,x):
        counts[root.family] += 1
        increment = observable(y,cutoff)-fx
        if root.family != 'AP':
            assert increment == 0
            assert y.aperture == x.aperture
            terms.append(0)  # Exact zero times a finite rate, NOT a deleted root.
        else:
            sb = Fraction(1) + Fraction(x.aperture[root.cell],reg.M_s)*(1-Fraction(1))
            sa = Fraction(1) + Fraction(y.aperture[root.cell],reg.M_s)*(1-Fraction(1))
            assert sa == sb == 1
            mobility_squared = sb*sa  # nu=1 in the fixed parameter tuple.
            assert mobility_squared == 1
            rate = sp.sqrt(sp.Rational(mobility_squared))*sp.exp(0)
            terms.append(int(rate)*increment)
    return sum(terms)


def run():
    plan,spec = pins()
    p = plan['frozen_probe']
    assert (p['r0'],p['h'],p['N'],p['epsilon'],p['q0'],p['m0']) == (0,0,0,1,1,1)
    W,edges,faces = maps.geometry(p['h'],p['N'])
    reduction = symbolic_ap_reduction(edges,faces)
    counts = Counter()
    rows = []
    for r,s in plan['bounded_implementation_fixtures']['pairs']:
        fine = maps.regulator(maps.Index(s,0,0))
        D = 2**(s-r)
        values = []
        for j in range(fine.M_s+1):
            x = en.State((j,)+(0,)*(fine.vertices-1),
                         (fine.Q,)+(0,)*(fine.vertices-1),
                         tuple(v%fine.K for v in range(fine.vertices)),
                         tuple((e+1)%fine.K for e in range(len(fine.edges))))
            assert en.valid_state(fine,x)
            y = project_to(x,s,r)
            fval = generator(x,s,counts)
            cval = generator(y,r,counts)
            defect = fval-cval
            expected = int(fine.M_s-D <= j < fine.M_s-1)
            assert defect == expected  # Closed-form analytic test oracle.
            values.append({'j':j,'fine':fval,'coarse':cval,'defect':defect,'pass':True})
        sup = max(abs(v['defect']) for v in values)
        assert sup == 1  # Independently calculated full-j fixture norm oracle.
        rows.append({'r':r,'s':s,'D':D,'sup':sup,'values':values})
    assert set(counts) == set(en.FAMILIES)
    # Endpoint K=2 inverse labels must remain distinct, not merged.
    reg0 = maps.regulator(maps.Index(0,0,0))
    labels = list(en.roots(reg0))
    assert len(labels) == len(set(labels))
    return {'schema':'tect/pah-v2-gd001-primary/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'execution_sha256':sha(PLAN),'source_hashes':spec['source_hashes'],
            'symbolic_reduction':reduction,'fixtures':rows,'root_counts':dict(counts),
            'geometry':{'W':W,'vertices':W*W,'edges':len(edges),'faces':len(faces)},
            'assertions':[{'name':'all_full_signed_families_retained','pass':True},
                          {'name':'exact_fine_minus_coarse_no_half','pass':True},
                          {'name':'one_base_indicator_all_fixture_pairs','pass':True},
                          {'name':'all_fixture_j_full_generator_matches_band','pass':True}],
            'scope':'Symbolic AP-rate reduction plus bounded source-complete diagnostics; arbitrary-tail proof is the synthesis and parameterized Lean bridge, not extrapolation from rows.',
            'environment':{'python':platform.python_version(),'sympy':sp.__version__,
                           'platform':platform.platform(),
                           'producer_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()},
            'seeds':None,'non_claims':'No Gibbs-L2, h/N limit, physical Pre-A, spacetime, QFT, gravity or TOE.'}


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
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GD-001 PRIMARY: PASS exact AP reduction and full-labelled-root diagnostics')


if __name__ == '__main__':
    main()
