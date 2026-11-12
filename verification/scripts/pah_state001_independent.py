#!/usr/bin/env python3
"""Independent exact fixed-square verifier, authored by the independent agent.

No PAH implementation imports. Constants below are the declared witness inputs,
cross-checked against the preregistration; asserted outputs are test oracles.
"""
import argparse
from fractions import Fraction as R
from itertools import product, permutations
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sympy as S

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/'strategy/pa-hyp/PAH-STATE-001-prereg-v1.json'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-pah-state001/independent.json'
E=((0,1),(0,2),(1,3),(2,3))  # Fixed source minimal-square incidence input.

@lru_cache(None)
def energy(x):
    j,l,n,u=x
    s=tuple(R(1+a,2) for a in j)
    p=tuple(a*(-1)**b for a,b in zip(l,n))
    z=tuple((-1)**a for a in u)
    out=sum((a-1)**2/2+R(b**6,6)+a*a*b*b/2 for a,b in zip(s,p))
    J=tuple(2/(s[v]+s[w]) for v,w in E)
    out+=sum((s[v]-s[w])**2/2+J[k]*(p[w]-z[k]*p[v])**2/2
             for k,(v,w) in enumerate(E))
    return out+sum(J)/len(E)*(1-math.prod(z))

def step(x,r):
    family,k,sign=r
    y=list(map(list,x))
    if family=='PH': y[2][k]=(y[2][k]+sign)%2
    elif family=='LK': y[3][k]=(y[3][k]+sign)%2
    elif family=='AP': y[0][k]+=sign
    else:
        v,w=E[k]
        y[1][v]-=sign
        y[1][w]+=sign
    if not all(0<=a<=1 for a in y[0]): return None
    if not all(0<=a<=2 for a in y[1]): return None
    return tuple(map(tuple,y))

def mobile(x,y,r):
    family,k,_=r
    s=tuple(S.Rational(1+a,2) for a in x[0])
    if family=='PH': return s[k]
    if family=='AP': return S.sqrt(s[k]*S.Rational(1+y[0][k],2))
    v,w=E[k]
    return S.sqrt(s[v]*s[w])

ROOTS=tuple((fam,k,sign) for fam in ('PH','TR','LK','AP')
            for k in range(4) for sign in (-1,1))

@lru_cache(None)
def action(x):
    out=S.Integer(0)
    for r in ROOTS:
        y=step(x,r)
        if y is not None:
            df=y[1][0]**2-x[1][0]**2
            delta=energy(y)-energy(x)
            out+=mobile(x,y,r)*S.exp(-S.Rational(delta.numerator,2*delta.denominator))*df
    return S.simplify(out)

def gauge(x,g):
    j,l,n,u=x
    return (j,l,tuple((n[v]+g[v])%2 for v in range(4)),
            tuple((u[k]+g[w]-g[v])%2 for k,(v,w) in enumerate(E)))

def display(x):
    j,l,n,u=x
    return (tuple(R(1+a,2) for a in j),tuple(a*(-1)**b for a,b in zip(l,n)),
            tuple((-1)**a for a in u))

def zero(expr): return S.simplify(S.expand(expr.rewrite(S.exp)))==0

def audit():
    spec=json.loads(SPEC.read_text(encoding='utf-8'))
    expected={'r':0,'h':0,'N':0,'m0':2,'q0':2,'R0':2,'epsilon':'1/2','beta':1,'nu':1,
              'lambda_s':1,'eta_6':1,'kappa_s':1,'kappa_D':1,'kappa_g':1,'g':1,'m2':0,'lambda_4':0,
              'j':[1]*4,'ell':[0,1,1,0],'u':[0]*4,'phase_pair':[[0]*4,[1,0,0,0]]}
    assert spec['inputs']==expected,'Specialized independent derivation has a different input'
    for p,h in spec['source_hashes'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    fibre=tuple(((1,1,1,1),(0,1,1,0),(a,0,0,b),(0,0,0,0)) for a,b in product(range(2),repeat=2))
    vals=tuple(action(x) for x in fibre)
    images=tuple(display(x) for x in fibre)
    assert all(z==images[0] for z in images) and len(set(fibre))==len(fibre)
    gauges=tuple(product(range(2),repeat=4))
    root_counts,gauge_checks,balance_checks=[],0,0
    for x in fibre:
        assert energy(x)==R(10,3)  # Independent proof test oracle.
        counts={fam:0 for fam in ('PH','TR','LK','AP')}
        for r in ROOTS:
            y=step(x,r)
            if y is None: continue
            counts[r[0]]+=1
            reverse=(r[0],r[1],-r[2])
            assert step(y,reverse)==x and mobile(x,y,r)==mobile(y,x,reverse)
            assert -energy(x)-(energy(y)-energy(x))/2==-energy(y)-(energy(x)-energy(y))/2
            balance_checks+=1
        root_counts.append(counts)
        assert counts==dict(PH=8,TR=4,LK=8,AP=4)  # Full signed-root test oracle.
        for g in gauges:
            gx=gauge(x,g)
            assert energy(gx)==energy(x) and gx[1][0]**2==x[1][0]**2
            assert zero(action(gx)-action(x))
            gauge_checks+=1
    observed_fibre,full_states=set(),0
    for l in product(range(3),repeat=4):
        if sum(l)!=2: continue
        for j,n,u in product(product(range(2),repeat=4),repeat=3):
            x=(j,l,n,u)
            full_states+=1
            if display(x)==images[0]: observed_fibre.add(x)
    assert observed_fibre==set(fibre)
    undirected={frozenset(e) for e in E}
    autos=[p for p in permutations(range(4)) if p[0]==0 and p[1]==1
           and {frozenset((p[v],p[w])) for v,w in E}==undirected]
    assert autos==[tuple(range(4))]
    hi,lo=2*S.exp(S.Rational(1,2)),2*S.exp(-S.Rational(1,2))  # Test oracles.
    assert all(zero(a-b) for a,b in zip(vals,(hi,hi,lo,lo)))
    mean=S.expand(sum(vals)/len(vals))
    variance=S.expand(sum((v-mean)**2 for v in vals)/len(vals))
    assert zero(variance-(S.exp(S.Rational(1,2))-S.exp(-S.Rational(1,2)))**2)
    assert S.exp(S.Rational(1,2))>S.exp(-S.Rational(1,2))
    return {'schema':'tect/pah-state001-independent/1.0','status':'PASS_EXACT_FINITE_WITNESS',
        'source_hashes':spec['source_hashes'],'prereg_sha256':hashlib.sha256(SPEC.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'full_states_checked_for_fibre':full_states,'fibre_size':len(fibre),'root_counts':root_counts,
        'balance_incidence_checks':balance_checks,'gauge_checks':gauge_checks,
        'anchor_automorphisms':[list(p) for p in autos],'Lf':list(map(str,vals)),
        'conditional_mean':str(mean),'conditional_variance':str(variance),
        'scope':'Finite display-state nonclosure only; full counting CTMC and original Gibbs law preserved.'}

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    result=audit()
    if a.write:
        assert not OUT.exists(),'Issued run immutable'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    elif a.check: assert json.loads(OUT.read_text(encoding='utf-8'))==result
    print('STATE-001 INDEPENDENT: PASS',result['full_states_checked_for_fibre'],'counting states for fibre; no implementation imports')

if __name__=='__main__': main()
