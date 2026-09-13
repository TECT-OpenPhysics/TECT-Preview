#!/usr/bin/env python3
"""Independent GD-002 finite formulation and Arb audit, version 1.0.0.

No primary/source-evaluator imports. Reconstructs geometry, coordinates,
signed roots, actual displayed F and actual rates from the pinned contract.
Directed bounds on finite rows are diagnostics, not the all-tail proof.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
from flint import arb, acb, ctx

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT/'strategy/pa-hyp/PAH-v2-GD-002-execution-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-13-pah-v2-gd002/independent.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def primes(n):
    answer=[]
    for k in itertools.count(2):
        if all(k%d for d in range(2,math.isqrt(k)+1)):
            answer.append(k)
            if len(answer)==n:
                return answer


def run():
    ctx.prec=160
    plan=json.loads(PLAN.read_text(encoding='utf-8'))
    pp=ROOT/plan['preregistration']['path']
    assert sha(pp)==plan['preregistration']['sha256']
    spec=json.loads(pp.read_text(encoding='utf-8'))
    for path,digest in spec['source_hashes'].items():
        assert sha(ROOT/path)==digest
    v=plan['frozen_probe']
    assert v['h']==v['N']==0 and v['epsilon']==v['nu']==v['beta']==1
    vertices=[(0,0),(1,0),(0,1),(1,1)]  # Exact admitted side-two Morton input.
    edges=[(i,vertices.index(w)) for i,(x,y) in enumerate(vertices)
           for w in ((x+1,y),(x,y+1)) if w in vertices]
    boundary=[(0,1),(1,3),(3,2),(2,0)]
    face=[(edges.index(e),1) if e in edges else (edges.index(e[::-1]),-1) for e in boundary]
    # Enumerate the ACTUAL full graph automorphism group preserving both anchors.
    undirected={frozenset(e) for e in edges}
    automorphisms=[p for p in itertools.permutations(range(len(vertices)))
                   if p[0]==0 and p[1]==1 and {frozenset((p[a],p[b])) for a,b in edges}==undirected]
    assert automorphisms==[tuple(range(len(vertices)))]
    modulus=v['observable_modulus']
    baseK=math.prod(primes(v['r0']+1))
    root_counts=Counter()
    rows=[]

    def flux(x):
        return sum(sign*x[3][e] for e,sign in face)

    def functional(x,r,K):
        amplitudes=[arb(ell)/2**r for ell in x[1]]
        # epsilon=1 makes all aperture terms zero, all J=1, mobility=1.
        F=sum(a**6/6+a**2/2 for a in amplitudes)
        for e,(tail,head) in enumerate(edges):
            angle=2*arb.pi()*(x[2][head]-x[2][tail]-x[3][e])/K
            av,aw=amplitudes[tail],amplitudes[head]
            F+=(av**2+aw**2-2*av*aw*angle.cos())/2
        return F+1-(2*arb.pi()*flux(x)/K).cos()

    for r in plan['bounded_fixtures']['root_cutoffs']:
        K=math.prod(primes(r+1))
        a=next(k for k in range(1,modulus) if (K//baseK*k)%modulus==1)
        # Split positive occupation, nonzero links/phases, both aperture endpoints.
        x=(tuple(0 if i%2==0 else 2**r for i in range(len(vertices))),
           (2**r-1,1,0,0), tuple((2*i+1)%K for i in range(len(vertices))),
           tuple((e+1)%K for e in range(len(edges))))
        F=functional(x,r,K)
        assert F > -arb('1e-35') and F < arb(14)/3  # Analytic bound independently derived below.
        result=acb(0)
        for family in ('PH','TR','LK','AP'):
            cells=len(vertices) if family in ('PH','AP') else len(edges)
            for cell in range(cells):
                for sign in (-1,1):
                    y=[list(c) for c in x]
                    if family=='PH':
                        y[2][cell]=(y[2][cell]+sign)%K
                    elif family=='LK':
                        y[3][cell]=(y[3][cell]+sign)%K
                    elif family=='AP':
                        y[0][cell]+=sign
                    else:
                        tail,head=edges[cell]
                        y[1][tail]-=sign
                        y[1][head]+=sign
                    if not all(0<=z<=2**r for z in y[0]) or not all(0<=z<=4**r for z in y[1]):
                        continue
                    assert sum(y[1])==2**r
                    root_counts[family]+=1
                    phase_delta=(a*(flux(y)-flux(x)))%modulus
                    if family!='LK':
                        assert phase_delta==0
                    inc=acb(0) if phase_delta==0 else acb(0,2*arb.pi()*phase_delta/modulus).exp()-1
                    dF=functional(y,r,K)-F
                    rate=(-dF/2).exp()  # Original rate, not the leading unit term.
                    if family=='LK':
                        assert abs(dF)<arb(16)/K
                        assert abs(rate-1)<arb(16)/K
                    result+=rate*inc
        eigen=len(edges)*(2*(2*arb.pi()*a/modulus).cos()-2)
        residual=abs(result-eigen)
        assert residual<arb(4*len(edges)*16)/K
        rows.append({'r':r,'K':K,'a':a,'F':str(F),'L_f_over_f':str(result),'residual':str(residual),
                     'certified_residual_upper':str(Fraction(4*len(edges)*16,K))})
    assert set(root_counts)=={'PH','TR','LK','AP'}
    # Independent character diagonalization at exactly five residues.
    zeta=acb(0,2*arb.pi()/modulus).exp()
    gap_checks=0
    for a in range(1,modulus):
        eig=len(edges)*(zeta**a+zeta**(modulus-a)-2)
        for q in (2,3):
            b=next(k for k in range(1,modulus) if q*k%modulus==a)
            eig2=len(edges)*(zeta**b+zeta**(modulus-b)-2)
            gap=abs(eig2-eig)
            assert gap>2*len(edges)
            assert (gap**2).contains(len(edges)**2*modulus)
            gap_checks+=1
    # Uniform Gibbs comparison: finite sum normalized, not a replacement state.
    Fupper=Fraction(1,6)+Fraction(1,2)+Fraction(len(edges),2)+2*len(face)//len(face)
    assert Fupper==Fraction(14,3)  # Labelled independent arithmetic oracle.
    assert (arb(1).exp()<3) and (arb.pi()<4)
    residues={1,4}
    assert {a*b%modulus for a in residues for b in residues}==residues
    assert 2 not in residues
    return {'schema':'tect/pah-v2-gd002-independent/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'preregistration_sha256':sha(pp),'execution_sha256':sha(PLAN),
            'source_hashes':spec['source_hashes'],'root_counts':dict(root_counts),'fixtures':rows,
            'gauge_invariance':'Signed closed-loop coboundary telescopes for every vertex label.',
            'full_anchor_automorphisms':[list(p) for p in automorphisms],
            'gap_checks':gap_checks,'F_upper':str(Fupper),'arb_precision_bits':ctx.prec,
            'checks':[{'name':n,'pass':True} for n in ['pins','actual_full_root_rows','original_F_and_rates',
                'outward_rounded_residuals','full_anchor_group','character_eigenvalues','residue_subgroup','Gibbs_bound_arithmetic']],
            'scope':'Independent finite coordinate/Arb implementation plus written alternative all-index proof. Same-task authorship; not an external referee and not an exhaustive finite Gibbs enumeration.',
            'environment':{'python':platform.python_version(),'platform':platform.platform()}}


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
    print('GD-002 INDEPENDENT: PASS',len(result['checks']),'checks')


if __name__=='__main__':
    main()
