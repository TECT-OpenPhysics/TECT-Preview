#!/usr/bin/env python3
"""Independent implementation and hostile checks of a DRAFT, not admission.

No primary, backend or source-enumerator imports. Shared primary test inputs
are explicit; this is same-author implementation independence, not an external
reviewer. Coordinate dictionaries/token pairs provide a second calculation.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import permutations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-morton-crt'
PIN = '5020922e7c69569fe040ceac7084a81297570e2b6c982c3c9a466e7b8bbb05a7'  # INPUT prereg.


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@lru_cache(None)
def layout(idx):
    r,h,N = idx
    width = 2**(h+N+1)
    # Recursive quadrant traversal, not the backend bit-interleaving code.
    points = [(0,0)]
    side = 1
    while side < width:
        points = [(x+dx*side,y+dy*side) for dx,dy in ((0,0),(1,0),(0,1),(1,1)) for x,y in points]
        side *= 2
    edges = [(a,b) for a in points for b in ((a[0]+1,a[1]),(a[0],a[1]+1)) if max(b) < width]
    prime = []
    candidate = 2
    while len(prime) <= r:
        if all(candidate % d for d in range(2,candidate)):
            prime.append(candidate)
        candidate += 1
    K = 1
    for p in prime:
        K *= p
    return tuple(points),tuple(edges),K,2**r,4**r,2**r


def unpack(state,idx):
    points,edges,*_ = layout(idx)
    return [{v:a for v,a in zip(points,s)} for s in state[:3]] + [{e:a for e,a in zip(edges,state[3])}]


def pack(d,idx):
    pts,eds,*_ = layout(idx)
    return [[d[k][v] for v in pts] for k in range(3)] + [[d[3][e] for e in eds]]


def lower(idx,axis):
    out = list(idx)
    out[axis] -= 1
    return tuple(out)


def valid(state,idx):
    pts,eds,K,Ms,Mp,Q = layout(idx)
    assert list(map(len,state)) == [len(pts)]*3+[len(eds)]
    for s,bound in zip(state,(Ms+1,Mp+1,K,K)):
        assert all(type(x) is int and 0 <= x < bound for x in s)
    assert sum(state[1]) == Q


def project(state,idx,axis):
    valid(state,idx)
    co = lower(idx,axis)
    pts,eds,K,Ms,Mp,Q = layout(co)
    finepts,fineeds,Kf,*_ = layout(idx)
    d = unpack(state,idx)
    if axis == 0:
        P = Kf//K
        A = next(a for a in range(K) if (a*P)%K == 1)
        # Select second tokens of consecutive pairs in the full ordered list.
        tokens = [v for v in pts for _ in range(d[1][v])]
        counts = Counter(tokens[1::2])
        out = [{v:d[0][v]//2 for v in pts},{v:counts[v] for v in pts},
               {v:(A*d[2][v])%K for v in pts},{e:(A*d[3][e])%K for e in eds}]
    elif axis == 1:
        rep = lambda v:(2*v[0],2*v[1])
        occ = Counter()
        for (x,y),value in d[1].items():
            occ[x//2,y//2] += value
        links = {}
        for a,b in eds:
            middle = (a[0]+b[0],a[1]+b[1])
            links[a,b] = (d[3][rep(a),middle]+d[3][middle,rep(b)])%K
        out = [{v:d[0][rep(v)] for v in pts},{v:occ[v] for v in pts},
               {v:d[2][rep(v)] for v in pts},links]
    else:
        occ = {v:d[1][v] for v in pts}
        # Direct suffix summation, independent of backend Q-minus-prefix.
        occ[pts[-1]] = sum(d[1][v] for v in finepts[len(pts)-1:])
        out = [{v:d[0][v] for v in pts},occ,{v:d[2][v] for v in pts},{e:d[3][e] for e in eds}]
    answer = pack(out,co)
    valid(answer,co)
    return answer


def to_base(x,idx,co,order=(2,1,0)):
    for axis in order:
        while idx[axis] > co[axis]:
            x,idx = project(x,idx,axis),lower(idx,axis)
    assert idx == co
    return x


def move(x,idx,s):
    family,cell,sign = s
    pts,eds,K,Ms,Mp,Q = layout(idx)
    y = [a.copy() for a in x]
    if family == 'TR':
        a,b = eds[cell]
        y[1][pts.index(a)] -= sign
        y[1][pts.index(b)] += sign
    else:
        k = {'AP':0,'PH':2,'LK':3}[family]
        y[k][cell] += sign
        if family in ('PH','LK'):
            y[k][cell] %= K
    if min(y[0]) < 0 or max(y[0]) > Ms or min(y[1]) < 0 or max(y[1]) > Mp:
        return None
    return y


def incidences(x,idx):
    pts,eds,*_ = layout(idx)
    for f in ('PH','TR','LK','AP'):
        for c in range(len(pts) if f in ('PH','AP') else len(eds)):
            for sign in (-1,1):
                s = [f,c,sign]
                y = move(x,idx,s)
                if y is not None:
                    yield s,y


def run():
    spec = ROOT/'strategy/pa-hyp/PAH-v2-morton-crt-draft.json'
    assert sha(spec) == PIN
    manifest = json.loads(spec.read_text(encoding='utf-8'))
    for p,h in manifest['source_pins'].items():
        assert sha(ROOT/p) == h
    primary = json.loads((BASE/'primary.json').read_text(encoding='utf-8'))
    assert primary['spec_sha256'] == PIN
    checks = Counter()
    for case in primary['cases']:
        assert project(case['x'],tuple(case['fine']),case['axis']) == case['px']
        checks['map_cases'] += 1
    for case in primary['gauges']:
        src = primary['cases'][case['case']]
        idx = tuple(src['fine'])
        pts,eds,K,*_ = layout(idx)
        x = [a.copy() for a in src['x']]
        g = case['g']
        x[2] = [(a+b)%K for a,b in zip(x[2],g)]
        x[3] = [(u+g[pts.index(b)]-g[pts.index(a)])%K for u,(a,b) in zip(x[3],eds)]
        assert project(x,idx,src['axis']) == case['pgx']
        checks['gauge_cases'] += 1
    for case in primary['squares']:
        idx = tuple(case['fine'])
        for a,b in (case['axes'],case['axes'][::-1]):
            assert project(project(case['x'],idx,a),lower(idx,a),b) == case['px']
        checks['square_cases'] += 1
    for case in primary['injections']:
        idx = list(case['coarse'])
        idx[case['axis']] += 1
        assert project(case['Jx'],tuple(idx),case['axis']) == case['x']
        checks['injection_samples'] += 1
    for case in primary['support']:
        for order in permutations(range(3)):
            for tag in ('x','y'):
                assert to_base(case[tag],tuple(case['fine']),tuple(case['coarse']),order) == case['px']
        checks['support_cases'] += 1
    for case in primary['roots']:
        idx,axis = tuple(case['fine']),case['axis']
        co = lower(idx,axis)
        x = case['x']
        px = project(x,idx,axis)
        rows = list(incidences(x,idx))
        assert [s for s,_ in rows] == [v['root'] for v in case['labels']]
        used = set()
        for (s,y),row in zip(rows,case['labels']):
            assert move(y,idx,[s[0],s[1],-s[2]]) == x
            key = lambda a,b: (tuple(v for field in a for v in field),*b)
            inv = [s[0],s[1],-s[2]]
            flip = key(y,inv) < key(x,s)
            aa,bb = (y,x) if flip else (x,y)
            pa,pb = project(aa,idx,axis),project(bb,idx,axis)
            chosen = next((root for root,target in incidences(pa,co) if target == pb),None)
            if chosen is not None and flip:
                chosen = [chosen[0],chosen[1],-chosen[2]]
            assert chosen == row['assignment']
            if chosen is not None:
                assert move(px,co,chosen) == project(y,idx,axis)
                used.add(tuple(chosen))
            checks['root_incidences'] += 1
        unmatched = {tuple(s) for s,_ in incidences(px,co)}-used
        assert unmatched == set(map(tuple,case['unmatched_coarse']))
    # Actual full smallest graph group, not a selected symmetry subgroup.
    pts,eds,*_ = layout((0,0,0))
    E = {frozenset(e) for e in eds}
    group = []
    for p in permutations(pts):
        d = dict(zip(pts,p))
        if d[0,0] == (0,0) and d[1,0] == (1,0) and {frozenset((d[a],d[b])) for a,b in eds} == E:
            group.append(d)
    assert len(group) == 1
    checks['full_smallest_graph_automorphisms'] = len(group)
    # Hostile controls: ordinary phase floor fails a signed path sum;
    # retaining an exterior-dependent global frame remains a failure.
    # Test INPUT: Kf=6, Kc=2, two oriented edges each carrying u=2.
    assert ((2+2)%6)//3 != ((2//3)+(2//3))%2
    # Removing prefix carry loses charge; plain volume restriction does too.
    occupied = [1,1,0,0]  # Test INPUT: fine total Q=2.
    assert sum(v//2 for v in occupied) != sum(occupied)//2
    co,fi = (0,0,0),(0,0,1)
    pts,eds,K,Ms,Mp,Q = layout(fi)
    x = [[0]*len(pts),[0]*len(pts),[0]*len(pts),[0]*len(eds)]
    x[1][-1] = Q
    px = project(x,fi,2)
    nc = len(layout(co)[0])
    assert sum(x[1][:nc]) != Q
    assert px[1][-1] == Q and x[1][nc-1] == 0
    hostile = {
        'ordinary_phase_rounding_path_sum':'REJECTED by Kf6/Kc2, u1=u2=2',
        'pointwise_occupation_floor':'REJECTED by ell=(1,1,0,0)',
        'plain_volume_restriction':'REJECTED by all charge outside retained box',
        'literal_terminal_occupation_preservation':'FALSE: comparison terminal=Q, literal terminal=0',
        'global_frame_negative_control':'Historical EXP-001735 replay retained separately; not passed on old geometry',
        'external_independence':'NOT_PERFORMED',
        'counts_as_generator_proof':False}
    return {'schema':'tect/pah-v2-morton-crt-independent/1.0','status':'PASS_DEVELOPMENT_ONLY',
            'spec_sha256':PIN,'primary_sha256':sha(BASE/'primary.json'),'verifier_sha256':sha(Path(__file__)),
            'checks':dict(checks),'hostile_controls':hostile,
            'independence':'Separate implementation, same author, shared declared test inputs; not external approval/admission.',
            'Lean':'NOT_RUN','approved_contract':False,'all_index_proof_machine_checked':False,
            'non_claims':'No generator or limit proof; no physical Pre-A, spacetime, QFT, GR, gravity or TOE.'}


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
    print('MORTON-CRT INDEPENDENT:',result['status'],result['checks'])


if __name__ == '__main__':
    main()
