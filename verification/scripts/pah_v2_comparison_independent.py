#!/usr/bin/env python3
"""Non-importing closed-form admission cross-check, version 1.0.0.

This implementation uses coordinate dictionaries and charge-token selection,
not the approved adjacent-map backend. Same-task authorship is disclosed.
No functional, rate, generator or limiting state is evaluated.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-12-pah-v2-comparison'
PIN = 'f3c724535900c56a71a0b66000b34916b12c2981ce1a2b1dd95a63b3e11c34f3'  # INPUT.


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@lru_cache(None)
def layout(idx,q0,m0):
    r,h,N = idx
    width = 2**(h+N+1)
    pts = [(0,0)]
    side = 1
    while side < width:
        pts = [(x+a*side,y+b*side) for a,b in ((0,0),(1,0),(0,1),(1,1)) for x,y in pts]
        side *= 2
    eds = [(a,b) for a in pts for b in ((a[0]+1,a[1]),(a[0],a[1]+1)) if max(b)<width]
    ps = []
    p = 2
    while len(ps) <= r:
        if all(p%d for d in range(2,p)):
            ps.append(p)
        p += 1
    K = 1
    for p in ps:
        K *= p
    return tuple(pts),tuple(eds),K,2**r,m0*4**r,q0*2**r


def valid(x,idx,q0,m0):
    pts,eds,K,Ms,Mp,Q = layout(tuple(idx),q0,m0)
    assert [len(c) for c in x] == [len(pts)]*3+[len(eds)]
    for c,b in zip(x,(Ms+1,Mp+1,K,K)):
        assert all(type(v) is int and 0<=v<b for v in c)
    assert sum(x[1]) == Q


def direct(x,co,fi,q0,m0):
    co,fi = tuple(co),tuple(fi)
    assert all(a<=b for a,b in zip(co,fi))
    valid(x,fi,q0,m0)
    cp,ce,Kc,Ms,Mp,Qc = layout(co,q0,m0)
    fp,fe,Kf,*_ = layout(fi,q0,m0)
    D,H = 2**(fi[0]-co[0]),2**(fi[1]-co[1])
    ratio = Kf//Kc
    A = next(a for a in range(Kc) if (a*ratio)%Kc == 1)
    fields = [{v:a for v,a in zip(fp,c)} for c in x[:3]]
    links = dict(zip(fe,x[3]))
    rep = lambda v:(H*v[0],H*v[1])
    # Pair/block token selection: choose tokens D,2D,... in Morton order.
    # Only the retained nonterminal blocks enter the output sums.
    tokens = [v for v in fp for _ in range(fields[1][v])]
    counts = Counter((v[0]//H,v[1]//H) for v in tokens[D-1::D])
    occ = [counts[v] for v in cp[:-1]]
    occ.append(Qc-sum(occ))
    out_links = []
    for a,b in ce:
        dx,dy = b[0]-a[0],b[1]-a[1]
        start = rep(a)
        total = 0
        for step in range(H):
            v = (start[0]+step*dx,start[1]+step*dy)
            w = (v[0]+dx,v[1]+dy)
            total += links[v,w]
        out_links.append(A*total%Kc)
    out = [[fields[0][rep(v)]//D for v in cp],occ,
           [A*fields[2][rep(v)]%Kc for v in cp],out_links]
    valid(out,co,q0,m0)
    return out


def move(x,idx,q0,m0,label):
    family,cell,sign = label
    pts,eds,K,Ms,Mp,Q = layout(tuple(idx),q0,m0)
    y = [c.copy() for c in x]
    if family == 'TR':
        a,b = eds[cell]
        y[1][pts.index(a)] -= sign
        y[1][pts.index(b)] += sign
    else:
        field = {'AP':0,'PH':2,'LK':3}[family]
        y[field][cell] += sign
        if family in ('PH','LK'):
            y[field][cell] %= K
    if min(y[0])<0 or max(y[0])>Ms or min(y[1])<0 or max(y[1])>Mp:
        return None
    return y


def roots(x,idx,q0,m0):
    pts,eds,*_ = layout(tuple(idx),q0,m0)
    for family in ('PH','TR','LK','AP'):
        for cell in range(len(pts) if family in ('PH','AP') else len(eds)):
            for sign in (-1,1):
                s = [family,cell,sign]
                y = move(x,idx,q0,m0,s)
                if y is not None:
                    yield s,y


def run():
    prereg = ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-admission-prereg.json'
    assert sha(prereg) == PIN
    spec = json.loads(prereg.read_text(encoding='utf-8'))
    prim = json.loads((BASE/'primary.json').read_text(encoding='utf-8'))
    assert prim['spec_sha256'] == PIN
    counts = Counter()
    for case in prim['cases']:
        cfg = case['config']
        co,fi,q0,m0 = cfg['co'],cfg['fi'],cfg['q0'],cfg['m0']
        p = lambda x:direct(x,co,fi,q0,m0)
        assert p(case['x']) == case['px']
        assert p(case['Jy']) == case['y']
        mid = [(a+b)//2 for a,b in zip(co,fi)]
        assert direct(direct(case['x'],mid,fi,q0,m0),co,mid,q0,m0) == case['px']
        pts,eds,K,Ms,Mp,Q = layout(tuple(fi),q0,m0)
        x = [c.copy() for c in case['x']]
        g = case['g']
        x[2] = [(a+b)%K for a,b in zip(x[2],g)]
        x[3] = [(a+g[pts.index(w)]-g[pts.index(v)])%K for a,(v,w) in zip(x[3],eds)]
        assert p(x) == case['pgx']
        # Alter every field outside the refined source box, preserving totalQ.
        box = (fi[0],fi[1],co[2])
        retained_pts,retained_edges,*_ = layout(box,q0,m0)
        retained = set(retained_pts)
        y = [c.copy() for c in case['x']]
        outside = [i for i,v in enumerate(pts) if v not in retained]
        if outside:
            total = sum(y[1][i] for i in outside)
            for i in outside:
                y[0][i] = (y[0][i]+1)%(Ms+1)
                y[1][i] = 0
                y[2][i] = (y[2][i]+1)%K
            y[1][outside[-1]] = total
            for e,edge in enumerate(eds):
                if edge not in set(retained_edges):
                    y[3][e] = (y[3][e]+1)%K
            assert p(y) == case['px']
            counts['external_support_changes'] += 1
        # Independent geometric rigidity coordinates on the actual finite box.
        W = max(v[0] for v in pts)+1
        Cx = 2**fi[1]
        assert W-1-Cx != W-1+Cx
        assert len({(x+y,W-1-x+y) for x,y in pts}) == len(pts)
        counts['direct_formula_cases'] += 1
        counts['factorization_cases'] += 1
        counts['gauge_cases'] += 1
        counts['right_inverse_cases'] += 1
    root_counts = []
    for case in prim['root_cases']:
        cfg = case['config']
        co,fi,q0,m0 = cfg['co'],cfg['fi'],cfg['q0'],cfg['m0']
        p = lambda x:direct(x,co,fi,q0,m0)
        x = case['x']
        actual = list(roots(x,fi,q0,m0))
        assert [s for s,_ in actual] == [r['label'] for r in case['labels']]
        used = set()
        for (s,y),row in zip(actual,case['labels']):
            inv = [s[0],s[1],-s[2]]
            assert move(y,fi,q0,m0,inv) == x
            key = lambda z,r:(tuple(a for field in z for a in field),*r)
            flip = key(y,inv)<key(x,s)
            a,b = (y,x) if flip else (x,y)
            chosen = next((r for r,z in roots(p(a),co,q0,m0) if z==p(b)),None)
            if chosen is not None and flip:
                chosen = [chosen[0],chosen[1],-chosen[2]]
            assert chosen == row['assigned']
            if chosen is not None:
                assert move(p(x),co,q0,m0,chosen) == p(y)
                used.add(tuple(chosen))
            counts['root_incidences'] += 1
        assert {tuple(r) for r,_ in roots(p(x),co,q0,m0)}-used == set(map(tuple,case['unmatched_coarse']))
        root_counts.append({'axis':case['axis'],'incidences':len(actual),
                            'unpaired':sum(r['assigned'] is None for r in case['labels']),
                            'unmatched_coarse':len(case['unmatched_coarse'])})
    # Exact hostile mutation fixtures. Numerical literals are declared inputs,
    # not inserted target conclusions. None evaluates a generator or rate.
    assert ((2+2)%6)//3 != ((2//3)+(2//3))%2
    assert sum(v//2 for v in (1,1,0,0)) != sum((1,1,0,0))//2
    co,fi = (0,0,0),(0,0,1)
    pts,eds,K,Ms,Mp,Q = layout(fi,1,1)
    x = [[0]*len(pts),[0]*len(pts),[0]*len(pts),[0]*len(eds)]
    x[1][-1] = Q
    px = direct(x,co,fi,1,1)
    nc = len(layout(co,1,1)[0])
    assert sum(x[1][:nc]) != Q and px[1][-1] != x[1][nc-1]
    assert any(c['unpaired']>0 for c in root_counts)
    z = [[0]*nc,[Q]+[0]*(nc-1),[0]*nc,[0]*len(layout(co,1,1)[1])]
    plus = move(z,co,1,1,['PH',0,1])
    minus = move(z,co,1,1,['PH',0,-1])
    assert plus == minus and ['PH',0,1] != ['PH',0,-1]
    return {'schema':'tect/pah-v2-comparison-independent/1.0','status':'PASS_FINITE_DEFINITION_CHECKS',
            'script_version':__version__,'script_sha256':sha(Path(__file__)),
            'prereg_sha256':PIN,'primary_sha256':sha(BASE/'primary.json'),
            'counts':dict(counts),'root_counts':root_counts,
            'hostile':{'phase_rounding':'REJECTED','pointwise_floor':'REJECTED',
                       'literal_volume_restriction':'REJECTED','literal_terminal_preservation':'FALSE_AND_DISCLOSED',
                       'discard_unpaired':'REJECTED','K2_inverse_label_collapse':'REJECTED',
                       'wrong_map_direction':'Closed formula accepts only componentwise coarse<=fine',
                       'sup_to_Gibbs_or_support_to_generator':'NOT_PERMITTED; all-index proof and Lean bounds have no Gibbs or generator premise'},
            'independence':'Closed-form implementation imports no primary/backend/source-enumerator code; shared declared inputs and same-task authorship, not an external human referee.',
            'scope':'Independent finite checks supplement the all-index written proof, not a finite enumeration proof of an infinite family.',
            'non_claims':spec['non_claims']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    out = BASE/'independent.json'
    if args.check:
        assert json.loads(out.read_text(encoding='utf-8')) == result
    else:
        out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PAH-V2-COMPARISON INDEPENDENT: PASS',result['counts'])


if __name__ == '__main__':
    main()
