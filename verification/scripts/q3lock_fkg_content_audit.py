#!/usr/bin/env python3
"""Exact finite alternative checks for the continuous-loop FKG content.

The rational spin law is an induction diagnostic, not the Q3LOCK loop law.
Exhaustive upper-event covariance checks do not prove infinite-volume limits.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT=Path(__file__).resolve().parents[2]
NOTE=ROOT/'strategy/q3lock-continuous-loop-fkg-content-260905.md'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-fkg-content-audit/result.json'
BINARY_DIM=3  # Finite diagnostic dimension, not a replacement field dimension.
FIELDS=(-1,1,0)  # Diagnostic unary coefficients.
PAIRS=((0,1),(1,2))  # Diagnostic attractive pair coefficients are one.
Q3_BITS=3  # Actual internal graph input.


def build_payload():
    rows=[]
    def check(name, ok, actual, expected):
        assert ok, (name,actual,expected)
        rows.append({'name':name,'actual':str(actual),'expected':str(expected),'pass':True})
    states=list(product((0,1),repeat=BINARY_DIM))
    le=lambda x,y: all(a<=b for a,b in zip(x,y))
    weights={x:F(2)**(sum(a*b for a,b in zip(FIELDS,x))+sum(x[i]*x[j] for i,j in PAIRS)) for x in states}
    Z=sum(weights.values())
    mass=lambda event: sum(weights[x] for x in event)/Z
    uppers=[]
    for mask in range(1<<len(states)):
        event={x for i,x in enumerate(states) if mask&(1<<i)}
        if all(y in event for x in event for y in states if le(x,y)):
            uppers.append(event)
    check('three-cube-upper-events',len(uppers)==20,len(uppers),20)  # Independent combinatorial oracle.
    for x in states:
        for y in states:
            meet=tuple(min(a,b) for a,b in zip(x,y))
            join=tuple(max(a,b) for a,b in zip(x,y))
            lhs=weights[meet]*weights[join]
            rhs=weights[x]*weights[y]
            check(f'lattice-{x}-{y}',lhs>=rhs,lhs,rhs)
    for i,A in enumerate(uppers):
        for j,B in enumerate(uppers):
            covariance=mass(A&B)-mass(A)*mass(B)
            check(f'upper-covariance-{i}-{j}',covariance>=0,covariance,'>=0')
    sub=list(product((0,1),repeat=BINARY_DIM-1))
    ratios={x:weights[x+(1,)]/weights[x+(0,)] for x in sub}
    for x in sub:
        for y in sub:
            if le(x,y):
                check(f'conditional-ratio-{x}-{y}',ratios[x]<=ratios[y],ratios[x],ratios[y])
    for i,event in enumerate(uppers):
        means=[]
        for t in (0,1):
            denom=sum(weights[x+(t,)] for x in sub)
            means.append(sum(weights[x+(t,)] for x in sub if x+(t,) in event)/denom)
        check(f'conditional-mean-{i}',means[0]<=means[1],means[0],means[1])
    # A mixture of two associated point masses need not be associated.
    atoms=((F(0),F(1)),(F(1),F(0)))
    avg=lambda f: sum(f(x) for x in atoms)/len(atoms)
    mix_cov=avg(lambda x:x[0]*x[1])-avg(lambda x:x[0])*avg(lambda x:x[1])
    check('reject-arbitrary-mixtures',mix_cov==F(-1,4),mix_cov,F(-1,4))  # Hostile oracle.
    vertices=list(product((0,1),repeat=Q3_BITS))
    edges=[(i,j) for i,x in enumerate(vertices) for j,y in enumerate(vertices) if i<j and sum(a!=b for a,b in zip(x,y))==1]
    degrees=[sum(i in e for e in edges) for i in range(len(vertices))]
    check('Q3-degree',all(d==Q3_BITS for d in degrees),degrees,Q3_BITS)
    check('Q3-edge-count',2*len(edges)==len(vertices)*Q3_BITS,2*len(edges),len(vertices)*Q3_BITS)
    # Parity-symmetric rank-one positive covariance fixtures, not loop laws.
    for fixture in (tuple(F(i+1,3) for i in range(len(vertices))), (F(1),)*len(vertices)):
        S=sum(x*x for x in fixture)
        D=sum((fixture[i]-fixture[j])**2 for i,j in edges)
        edge_sum=sum(fixture[i]*fixture[j] for i,j in edges)
        Qsquare=sum(fixture)**2/len(vertices)
        check(f'graph-identity-{fixture[0]}',D==Q3_BITS*S-2*edge_sum,D,Q3_BITS*S-2*edge_sum)
        check(f'positive-covariance-D-{fixture[0]}',D<=Q3_BITS*S,D,Q3_BITS*S)
        check(f'positive-covariance-Q-{fixture[0]}',Qsquare>=S/len(vertices),Qsquare,S/len(vertices))
    alternating=tuple(F((-1)**sum(v)) for v in vertices)
    S=sum(x*x for x in alternating)
    Qsquare=sum(alternating)**2/len(vertices)
    check('reject-pointwise-collective-bound',Qsquare<S/len(vertices),Qsquare,S/len(vertices))
    return {'schema':'tect/q3lock-fkg-content-audit/1.0','status':'PASS','claim_bearing':False,
            'assertions_passed':len(rows),'assertions':rows,
            'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__).resolve(),NOTE)},
            'scope':'Finite rational association, induction and graph diagnostics only; no path-space or phase conclusion from sampling.'}


if __name__=='__main__':
    payload=build_payload()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=OUT.parent,suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:
            json.dump(payload,stream,indent=2,sort_keys=True)
            stream.write('\n')
        os.replace(tmp,OUT)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    print(f"Q3LOCK FKG CONTENT PASS {payload['assertions_passed']}/{len(payload['assertions'])}")
    print(OUT)
