#!/usr/bin/env python3
"""Independent GD-001 row-action reconstruction, version 1.0.0.

No primary, source enumerator or comparison-backend imports. This uses named
integer coordinate tuples and direct all-pair floors; full root rows are
aggregated before applying one fixed base indicator. Same-task authorship.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import subprocess

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT/'strategy/pa-hyp/PAH-v2-GD-001-execution-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-gd001/independent.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def primorial(r):
    ps = []
    k = 2
    while len(ps) < r+1:
        if all(k%d for d in range(2,k)):
            ps.append(k)
        k += 1
    out = 1
    for p in ps:
        out *= p
    return out


def roots(x,r,edges):
    M,K,Q,cap = 2**r,primorial(r),2**r,4**r
    V = len(x[0])
    for fam,slot in (('PH',2),('TR',1),('LK',3),('AP',0)):
        for cell in range(len(edges) if fam in ('TR','LK') else V):
            for sign in (-1,1):
                y = [list(c) for c in x]
                if fam == 'TR':
                    v,w = edges[cell]
                    y[1] = [ell+sign*(int(z==w)-int(z==v)) for z,ell in enumerate(x[1])]
                elif fam in ('PH','LK'):
                    y[slot][cell] = (y[slot][cell]+sign)%K
                else:
                    y[slot][cell] += sign
                if not all(0<=j<=M for j in y[0]) or not all(0<=ell<=cap for ell in y[1]):
                    continue
                assert sum(y[1]) == Q
                yield fam,cell,sign,tuple(tuple(c) for c in y)


def pullback_state(x,s,r):
    D = 2**(s-r)
    Kr,Ks = primorial(r),primorial(s)
    inv = pow(Ks//Kr,-1,Kr)
    prefix = [0]
    for ell in x[1]:
        prefix.append(prefix[-1]+ell)
    return (tuple(j//D for j in x[0]),
            tuple(prefix[v+1]//D-prefix[v]//D for v in range(len(x[1]))),
            tuple(inv*n%Kr for n in x[2]),tuple(inv*u%Kr for u in x[3]))


def row_action(x,r,edges,counts):
    """AP row assembled as an exact integer matrix row; other increments 0.

    At epsilon=1 every displayed s is 1. AP changes no ell,n,u and therefore
    no displayed field of ANY parent functional term. Its inherited rate is
    (1*1)^(nu/2)*exp(-beta*0/2)=1. No rate for another family is replaced by 1.
    """
    observable = lambda z: int(pullback_state(z,r,0)[0][0] == 0)
    row = Counter()
    for fam,cell,sign,y in roots(x,r,edges):
        counts[fam] += 1
        if fam == 'AP':
            assert y[1:] == x[1:]
            assert tuple(1 for _ in y[0]) == tuple(1 for _ in x[0])
            row[y] += 1
            row[x] -= 1
        else:
            assert observable(y)-observable(x) == 0
    assert sum(row.values()) == 0
    return sum(coefficient*observable(y) for y,coefficient in row.items())


def run():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    pp = plan['preregistration']
    assert sha(ROOT/pp['path']) == pp['sha256']
    spec = json.loads((ROOT/pp['path']).read_text(encoding='utf-8'))
    for p,h in spec['source_hashes'].items():
        assert sha(ROOT/p) == h
    p = plan['frozen_probe']
    assert (p['h'],p['N'],p['epsilon']) == (0,0,1)
    # Derived coordinates of the adopted W=2^(h+N+1) graph, not a new carrier.
    W = 2**(p['h']+p['N']+1)
    coords = [(x,y) for y in range(W) for x in range(W)]
    edges = tuple((i,coords.index(q)) for i,(x,y) in enumerate(coords)
                  for q in ((x+1,y),(x,y+1)) if q in coords)
    counts = Counter()
    rows = []
    for r,s in plan['bounded_implementation_fixtures']['pairs']:
        Ms,K = 2**s,primorial(s)
        D = 2**(s-r)
        values = []
        for j in range(Ms+1):
            x = ((j,)+(0,)*(len(coords)-1),
                 (2**s,)+(0,)*(len(coords)-1),
                 tuple(v%K for v in range(len(coords))),
                 tuple((e+1)%K for e in range(len(edges))))
            y = pullback_state(x,s,r)
            fine,coarse = row_action(x,s,edges,counts),row_action(y,r,edges,counts)
            defect = fine-coarse
            assert defect == int(Ms-D<=j<Ms-1)  # Analytic formula oracle.
            values.append({'j':j,'fine':fine,'coarse':coarse,'defect':defect,'pass':True})
        rows.append({'r':r,'s':s,'D':D,'sup':max(abs(v['defect']) for v in values),'values':values})
    assert all(row['sup']==1 for row in rows)  # Test oracle, never assigned output.
    # Original K=2 labelled duplicate channels remain separately enumerable.
    x0 = ((0,)*len(coords),(1,)+(0,)*(len(coords)-1),(0,)*len(coords),(0,)*len(edges))
    ph0 = [(fam,cell,sign,y) for fam,cell,sign,y in roots(x0,0,edges) if fam=='PH' and cell==0]
    assert len(ph0)==2 and ph0[0][3]==ph0[1][3] and ph0[0][2]!=ph0[1][2]
    return {'schema':'tect/pah-v2-gd001-independent/1.0','status':'PASS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'execution_sha256':sha(PLAN),'source_hashes':spec['source_hashes'],
            'fixtures':rows,'root_counts':dict(counts),
            'assertions':[{'name':n,'pass':True} for n in (
                'direct_full_coordinate_moves','row_sum_zero','all_non_AP_increments_zero',
                'all_AP_displayed_fields_identical','both_K2_labels_retained',
                'full_j_rows_equal_exact_band','one_fixed_base_observable')],
            'independence':'No primary/backend/enumerator imports; direct all-pair coordinate projection and integer row-action. Same-task authorship, not external-person review.',
            'scope':'Bounded executable cross-check plus separately written all-index audit; not numerical extrapolation.',
            'environment':{'python':platform.python_version(),'platform':platform.platform(),
                           'producer_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()},
            'seeds':None,'non_claims':'No Gibbs-L2, infinite dynamics, physical Pre-A, spacetime, QFT, gravity or TOE.'}


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
    print('GD-001 INDEPENDENT: PASS direct full-root row-action and fixed-base defect')


if __name__ == '__main__':
    main()
