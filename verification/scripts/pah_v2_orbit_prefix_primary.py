#!/usr/bin/env python3
"""Prototype of an UNAPPROVED full-state v2 comparison at fixed G.

Integer operations only. Uses source roots without changing rates or labels.
Whole-G canonicalization is NOT a proof of volume-uniform spatial locality.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/"strategy/pa-hyp/PAH-v2-orbit-prefix-draft.json"
PIN="0f1aaa35c6729c2c3a8a484e8a60ae3e5de3941736a78e6fdd90c92a328314cd"  # INPUT prereg.
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-orbit-prefix/primary.json"
sys.path.insert(0,str(ROOT/"codes/foundations"))
import pah_v2_root_enumerator as en


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def flat(x): return x.aperture+x.occupation+x.phase+x.link


def cell_group(inp):
    """Complete simple-edge fixture automorphisms, validating signed face words."""
    nv=inp["vertices"]; edges=tuple(map(tuple,inp["edges"]))
    assert len(edges)==len(set(edges)) and all(v!=w for v,w in edges)
    def cycles(w): return {w[i:]+w[:i] for i in range(len(w))}
    faces=[tuple(map(tuple,f)) for f in inp["faces"]]
    targets=[cycles(f)|cycles(tuple((e,-s) for e,s in reversed(f))) for f in faces]
    answer=[]
    for perm in it.permutations(range(nv)):
        if any({perm[v] for v in inp[a]}!=set(inp[a]) for a in ("outer_anchor","core_anchor")): continue
        em=[]
        for v,w in edges:
            pair=(perm[v],perm[w])
            if pair in edges: em.append((edges.index(pair),1))
            elif pair[::-1] in edges: em.append((edges.index(pair[::-1]),-1))
            else: break
        if len(em)!=len(edges): continue
        mapped=[tuple((em[e][0],s*em[e][1]) for e,s in f) for f in faces]
        if not any(all(mapped[i] in targets[p[i]] for i in range(len(faces))) for p in it.permutations(range(len(faces)))): continue
        answer.append((perm,tuple(em)))
    return tuple(sorted(answer))


def act(z,h,k):
    ap,occ,w=z; perm,em=h; aa=[0]*len(ap);ll=aa.copy();ww=[0]*len(w)
    for v,d in enumerate(perm): aa[d]=ap[v];ll[d]=occ[v]
    for e,(d,s) in enumerate(em): ww[d]=s*w[e]%k
    return tuple(aa),tuple(ll),tuple(ww)


def inv(h):
    p,em=h; pp=[0]*len(p);ee=[None]*len(em)
    for i,j in enumerate(p): pp[j]=i
    for i,(j,s) in enumerate(em): ee[j]=(i,s)
    return tuple(pp),tuple(ee)


def normal(x,reg):
    return x.aperture,x.occupation,tuple((u+x.phase[v]-x.phase[w])%reg.K for u,(v,w) in zip(x.link,reg.edges))


def make_map(co,fi,group):
    assert fi.vertices==co.vertices and fi.edges==co.edges and fi.K==2*co.K
    assert fi.M_s==2*co.M_s and fi.M_psi==4*co.M_psi and fi.Q==2*co.Q and 1<=co.Q<=co.M_psi
    @lru_cache(None)
    def reduce_normal(z):
        c,h=min((act(z,h,fi.K),h) for h in group)
        ap,occ,w=c; total=0; prev=0; ll=[]
        for l in occ:
            total+=l; ll.append(total//2-prev);prev=total//2
        red=(tuple(a//2 for a in ap),tuple(ll),tuple(v//2 for v in w))
        return act(red,inv(h),co.K)
    def p(x):
        ap,occ,w=reduce_normal(normal(x,fi))
        ns=tuple(n//2 for n in x.phase)
        us=tuple((z-ns[v]+ns[t])%co.K for z,(v,t) in zip(w,co.edges))
        return en.State(ap,occ,ns,us)
    return p,reduce_normal


def run():
    assert sha(SPEC)==PIN
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    for p,h in spec["source_pins"].items(): assert sha(ROOT/p)==h,p
    inp=json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    co=en.Regulator(inp["vertices"],tuple(map(tuple,inp["edges"])),inp["K"],inp["M_s"],inp["M_psi"],inp["Q"])
    fi=en.Regulator(co.vertices,co.edges,2*co.K,2*co.M_s,4*co.M_psi,2*co.Q)
    group=cell_group(inp);p,red=make_map(co,fi,group)
    canonical=lambda z,k:min(act(z,h,k) for h in group)
    phases=tuple(it.product(range(fi.K),repeat=fi.vertices))
    digest=hashlib.sha256();normal_count=0;state_count=0
    for ap in it.product(range(fi.M_s+1),repeat=fi.vertices):
        for occ in it.product(range(fi.M_psi+1),repeat=fi.vertices):
            if sum(occ)!=fi.Q: continue
            for w in it.product(range(fi.K),repeat=len(fi.edges)):
                z=(ap,occ,w);rz=red(z);normal_count+=1
                digest.update(json.dumps([z,rz],separators=(",",":")).encode("ascii"));digest.update(b"\n")
                for h in group: assert canonical(red(act(z,h,fi.K)),co.K)==canonical(rz,co.K)
                for ns in phases:
                    us=tuple((q-ns[v]+ns[t])%fi.K for q,(v,t) in zip(w,fi.edges))
                    x=en.State(ap,occ,ns,us);y=p(x)
                    assert en.valid_state(fi,x) and en.valid_state(co,y)
                    assert normal(y,co)==rz
                    state_count+=1
    def J(x): return en.State(*(tuple(2*v for v in block) for block in (x.aperture,x.occupation,x.phase,x.link)))
    coarse=tuple(en.states(co))
    assert all(p(J(x))==x for x in coarse)
    @lru_cache(None)
    def targets(x):
        out={}
        for r,y in en.incidences(co,x): out.setdefault(y,r)
        return out
    def key(x,r): return flat(x)+(en.FAMILIES.index(r.family),r.cell,r.sign)
    def paired(x,s,y):
        if key(x,s)<key(y,s.inverse()): return targets(p(x)).get(p(y))
        r=targets(p(y)).get(p(x))
        return None if r is None else r.inverse()
    counts=Counter();root_digest=hashlib.sha256();missing_digest=hashlib.sha256()
    for c in coarse:
        x=J(c);assigned=set()
        for s,y in en.incidences(fi,x):
            r=paired(x,s,y);rr=paired(y,s.inverse(),x)
            assert (r is None)==(rr is None)
            if r is not None:
                assert rr==r.inverse() and en.apply_move(co,p(x),r)==p(y)
                counts["paired"]+=1
                assigned.add(r)
            else: counts["unpaired"]+=1
            row=[flat(x),(s.family,s.cell,s.sign),None if r is None else (r.family,r.cell,r.sign)]
            root_digest.update(json.dumps(row,separators=(",",":")).encode("ascii"));root_digest.update(b"\n")
        for r,_ in en.incidences(co,c):
            counts["coarse_labels_retained"]+=1
            if r not in assigned:
                counts["unmatched_coarse"]+=1
                row=[flat(x),(r.family,r.cell,r.sign)]
                missing_digest.update(json.dumps(row,separators=(",",":")).encode("ascii"));missing_digest.update(b"\n")
    # Preregistered full-support scrutiny: coarse core-edge gauge invariant
    # changes when ONLY an incident outside edge changes on the fine side.
    a=en.State((0,0,0),(0,1,1),(0,0,0),(0,1,0))
    b=en.State(a.aperture,a.occupation,a.phase,(1,1,0))
    assert en.valid_state(fi,a) and en.valid_state(fi,b)
    assert a.aperture[1:]==b.aperture[1:] and a.occupation[1:]==b.occupation[1:]
    assert a.phase[1:]==b.phase[1:] and a.link[1]==b.link[1]
    core_edge=co.edges.index((1,2))
    assert co.K==2, "issued cosine oracle uses exact +/-1"
    fa=(-1)**normal(p(a),co)[2][core_edge];fb=(-1)**normal(p(b),co)[2][core_edge]
    assert fa!=fb
    return {"schema":"tect/pah-v2-orbit-prefix-primary/1.0","status":"PASS_FIXED_G_DRAFT_CHECKS_NOT_FULL_CONTRACT",
            "prereg_sha256":sha(SPEC),"script_sha256":sha(Path(__file__)),"source_pins":spec["source_pins"],
            "normal_coordinates_checked":normal_count,"retained_phase_fibres_each":len(phases),"full_fine_states_checked":state_count,
            "normal_map_digest":digest.hexdigest(),"full_coarse_right_inverse_checks":len(coarse),
            "automorphisms":group,"root_scope":"All valid fine incidences at every injected coarse tuple, plus paired reverse checks; not all fine incidence rows enumerated",
            "root_counts":dict(counts),"root_assignment_digest":root_digest.hexdigest(),"unmatched_coarse_digest":missing_digest.hexdigest(),
            "support_witness":{"fine_a":flat(a),"fine_b":flat(b),"mapped_a":flat(p(a)),"mapped_b":flat(p(b)),"coarse_observable":"cos(2 pi (u_12+n_1-n_2)/K), K=2", "values":[fa,fb],"original_support":"vertices {1,2}, edge (1,2)","changed_fine_coordinate":"u_(0,1)","meaning":"Zero-halo support fails for this candidate. All-G bound only; not a proof of failure of every bounded halo or volume-uniformity."},
            "non_claims":"No approved contract, uniform spatial support, dynamics/Gibbs compatibility, limit or physical conclusion."}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--check",action="store_true");args=ap.parse_args()
    data=json.loads(json.dumps(run()))
    if args.check: assert json.loads(OUT.read_text(encoding="utf-8"))==data
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as f: json.dump(data,f,indent=2,sort_keys=True);f.write("\n")
    print("PAH-V2-ORBIT-PREFIX PRIMARY: PASS (total fixed-G prototype; whole-contract/locality not admitted)")


if __name__=="__main__": main()
