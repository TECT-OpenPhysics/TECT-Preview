#!/usr/bin/env python3
"""Development-only definition tests for the unapproved full comparison draft."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'codes/foundations'))
import pah_v2_morton_crt as m
en = m.en
SPEC = ROOT / 'strategy/pa-hyp/PAH-v2-morton-crt-draft.json'
PIN = '5020922e7c69569fe040ceac7084a81297570e2b6c982c3c9a466e7b8bbb05a7'  # INPUT preregistration.
OUT = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-morton-crt/primary.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def packed(x):
    return [list(v) for v in (x.aperture, x.occupation, x.phase, x.link)]


def check_geometry(idx):
    W, edges, faces = m.geometry(idx.h, idx.N)
    assert all(m.morton(*m.coordinates(z)) == z for z in range(W*W))
    degree = Counter(v for e in edges for v in e)
    assert max(degree.values()) <= 4
    for word in faces:
        oriented = [edges[e][::s] for e, s in word]
        assert all(oriented[i][1] == oriented[(i+1) % len(word)][0] for i in range(len(word)))
    # Full graph automorphism rigidity certificate: O plus a distinguished
    # bottom-right corner yield injective distance coordinates. C separates
    # that corner from the other adjacent corner, even on the smallest grid.
    Cx = 2**idx.h
    assert W-1-Cx != W-1+Cx
    distances = {(x+y, W-1-x+y) for x, y in map(m.coordinates, range(W*W))}
    assert len(distances) == W*W
    paths = m.child_paths(idx)
    fine_edges = m.regulator(idx.step(1)).edges
    for (a, b), path in zip(edges, paths):
        assert fine_edges[path[0]][0] == 4*a
        assert fine_edges[path[0]][1] == fine_edges[path[1]][0]
        assert fine_edges[path[1]][1] == 4*b
    # Each coarse oriented face boundary is the boundary of four children:
    # cancelling internal edges is a chain computation, not a picture.
    fine_lookup = {e: i for i, e in enumerate(fine_edges)}
    for y in range(W-1):
        for x in range(W-1):
            chain = Counter()
            for dx in (0, 1):
                for dy in (0, 1):
                    xx, yy = 2*x+dx, 2*y+dy
                    a,b,c,d = [m.morton(*v) for v in ((xx,yy),(xx+1,yy),(xx+1,yy+1),(xx,yy+1))]
                    for e, sign in (((a,b),1),((b,c),1),((d,c),-1),((a,d),-1)):
                        chain[fine_lookup[e]] += sign
            co_word = faces[y*(W-1)+x]
            expected = Counter()
            for e, sign in co_word:
                for fe in paths[e]:
                    expected[fe] += sign
            assert {e:s for e,s in chain.items() if s} == {e:s for e,s in expected.items() if s}


def run():
    assert sha(SPEC) == PIN
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for p, h in spec['source_pins'].items():
        assert sha(ROOT/p) == h, p
    inputs = spec['preapproval_checks']
    params = inputs['base_inputs']
    indices = [m.Index(*i, **params) for i in inputs['sample_indices']]
    cases = []
    gauges = []
    squares = []
    injections = []
    geometry_count = 0
    for idx in indices:
        check_geometry(idx)
        geometry_count += 1
        for seed in range(inputs['deterministic_samples_per_index']):
            x = m.sample(idx, seed)
            for axis in range(3):
                y = m.inject(x, idx, axis)
                assert m.project(y, idx.step(axis), axis) == x
                if seed == 0:
                    injections.append({'coarse': [idx.r,idx.h,idx.N], 'axis':axis,
                                       'x':packed(x),'Jx':packed(y)})
                if (idx.r,idx.h,idx.N)[axis] == 0:
                    continue
                px = m.project(x, idx, axis)
                g = tuple((seed+v*v+v) % m.regulator(idx).K for v in range(m.regulator(idx).vertices))
                left = m.project(m.gauge(x,idx,g),idx,axis)
                right = m.gauge(px,idx.step(axis,-1),m.gauge_project(g,idx,axis))
                assert left == right
                cases.append({'fine':[idx.r,idx.h,idx.N], 'axis':axis,'x':packed(x),'px':packed(px)})
                gauges.append({'case':len(cases)-1,'g':g,'pgx':packed(left)})
            for a,b in combinations(range(3),2):
                if min((idx.r,idx.h,idx.N)[i] for i in (a,b)) == 0:
                    continue
                ab = m.project(m.project(x,idx,a),idx.step(a,-1),b)
                ba = m.project(m.project(x,idx,b),idx.step(b,-1),a)
                assert ab == ba
                squares.append({'fine':[idx.r,idx.h,idx.N],'axes':[a,b],'x':packed(x),'px':packed(ab)})
    base = indices[0]
    count = 0
    digest = hashlib.sha256()
    for x in en.states(m.regulator(base)):
        for axis in range(3):
            assert m.project(m.inject(x,base,axis),base.step(axis),axis) == x
        digest.update(bytes(m.flat(x)))
        count += 1
    r = m.regulator(base)
    # Independently count all fixed-Q occupations, not an asserted derived literal.
    coeff = [1] + [0]*r.Q
    for _ in range(r.vertices):
        coeff = [sum(coeff[q-j] for j in range(min(q,r.M_psi)+1)) for q in range(r.Q+1)]
    assert count == coeff[r.Q]*(r.M_s+1)**r.vertices*r.K**(r.vertices+len(r.edges))
    # Every ordering on the preregistered top corner gives the same image.
    top = indices[-1]
    for seed in range(inputs['deterministic_samples_per_index']):
        x = m.sample(top,seed)
        assert len({m.project_to(x,top,base,order) for order in permutations(range(3))}) == 1
    # Vary ALL unretained aperture/phase/link coordinates and redistribute
    # outside occupation, keeping the source-box restriction and total Q.
    retained = m.regulator(m.Index(top.r,top.h,base.N,**params))
    support = []
    for seed in range(inputs['deterministic_samples_per_index']):
        x = m.sample(top,seed)
        reg = m.regulator(top)
        ap,occ,phase,links = map(list,(x.aperture,x.occupation,x.phase,x.link))
        bound = retained.vertices
        outside_total = sum(occ[bound:])
        for v in range(bound,reg.vertices):
            ap[v] = (ap[v]+1) % (reg.M_s+1)
            phase[v] = (phase[v]+1) % reg.K
            occ[v] = 0
        occ[-1] = outside_total
        inside_edges = set(retained.edges)
        for e,edge in enumerate(reg.edges):
            if edge not in inside_edges:
                links[e] = (links[e]+1) % reg.K
        y = en.State(tuple(ap),tuple(occ),tuple(phase),tuple(links))
        assert en.valid_state(reg,y)
        assert m.project_to(x,top,base) == m.project_to(y,top,base)
        support.append({'fine':[top.r,top.h,top.N],'coarse':[base.r,base.h,base.N],
                        'x':packed(x),'y':packed(y),'px':packed(m.project_to(x,top,base))})
    roots = []
    for axis in range(3):
        fine = base.step(axis)
        x = m.sample(fine,0)
        px = m.project(x,fine,axis)
        all_coarse = {s for s,_ in en.incidences(m.regulator(base),px)}
        used = set()
        labels = []
        for s,y in en.incidences(m.regulator(fine),x):
            a = m.assign_root(x,fine,axis,s)
            reverse = m.assign_root(y,fine,axis,s.inverse())
            assert reverse == (a.inverse() if a else None)
            if a is not None:
                assert en.apply_move(m.regulator(base),px,a) == m.project(y,fine,axis)
                used.add(a)
            labels.append({'root':[s.family,s.cell,s.sign],
                           'assignment':[a.family,a.cell,a.sign] if a else None})
        roots.append({'fine':[fine.r,fine.h,fine.N],'axis':axis,'x':packed(x),'labels':labels,
                      'fine_incidence_count':len(labels),'paired':sum(z['assignment'] is not None for z in labels),
                      'unmatched_coarse':[[s.family,s.cell,s.sign] for s in sorted(all_coarse-used,key=lambda s:(s.family,s.cell,s.sign))]})
    # A signed group homomorphism has no orientation-dependent rounding.
    phase = []
    c,f = m.regulator(base),m.regulator(base.step(0))
    A = pow(f.K//c.K,-1,c.K)
    for u in range(f.K):
        assert A*((-u)%f.K)%c.K == (-A*u)%c.K
        phase.append([u,A*u%c.K])
    # Historical failure remains a negative control, not erased by new geometry.
    old = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-spatial-frame/primary.json'
    historical = {'path':old.relative_to(ROOT).as_posix(),'sha256':sha(old)}
    return {'schema':'tect/pah-v2-morton-crt-development-check/1.0','status':'PASS_DEVELOPMENT_ONLY',
            'spec_sha256':PIN,'source_pins':spec['source_pins'],
            'implementation_sha256':sha(ROOT/'codes/foundations/pah_v2_morton_crt.py'),
            'verifier_sha256':sha(Path(__file__)), 'geometry_samples':geometry_count,
            'coarse_right_inverse_states':count,'coarse_state_digest':digest.hexdigest(),
            'cases':cases,'gauges':gauges,'squares':squares,'injections':injections,
            'support':support,'roots':roots,'phase_homomorphism':phase,'historical_negative_control':historical,
            'all_index_proof':'Separate human mathematical review, not inferred from tests.',
            'approved_contract':False,'generator_or_limit_verified':False,'Lean':'NOT_RUN',
            'non_claims':'No physical Pre-A, spacetime, QFT, GR, continuum, gravity or TOE conclusion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path,default=OUT)
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    if args.check:
        assert json.loads(args.output.read_text(encoding='utf-8')) == result
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('MORTON-CRT PRIMARY:',result['status'],'coarse states=',result['coarse_right_inverse_states'],
          'map samples=',len(result['cases']),'squares=',len(result['squares']))


if __name__ == '__main__':
    main()
