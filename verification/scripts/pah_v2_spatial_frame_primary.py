#!/usr/bin/env python3
"""Reproduce one preregistered member of an arbitrary-distance support witness.

The universal geometry statement is proved in the companion review, not by a
size sweep. Apply the already pinned orbit-prefix map without any repair.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pah_v2_orbit_prefix_primary as old

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/"strategy/pa-hyp/PAH-v2-spatial-frame-prereg.json"
PIN="07d67b69ec742dc3c7981d2b73e102a88c5bc376a97009f53e125cde57c72997"  # INPUT: preregistered test contract.
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-spatial-frame/primary.json"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    assert sha(SPEC)==PIN
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    for path,pin in spec["source_pins"].items(): assert sha(ROOT/path)==pin,path
    d=spec["preregistered_tests"]["smoke_depth"]
    assert type(d) is int and d>=1
    edges=[(0,1),(1,2),(2,0)]
    for k in range(1,d+1):
        edges.extend([(2*k-1,2*k+1),(2*k,2*k+2)])
    nv=2*d+3
    inp={"vertices":nv,"edges":edges,"faces":[[(0,1),(1,1),(2,1)]],
         "outer_anchor":[0],"core_anchor":[1,2]}
    adjacency=[set() for _ in range(nv)]
    for v,w in edges: adjacency[v].add(w);adjacency[w].add(v)
    dist={1:0,2:0};front={1,2}
    while front:
        nxt=set()
        for v in front:
            for w in adjacency[v]:
                if w not in dist:dist[w]=dist[v]+1;nxt.add(w)
        front=nxt
    assert len(dist)==nv
    group=old.cell_group(inp)
    # Test oracle from the written complete-group argument.
    assert len(group)==2 and max(map(len,adjacency))==3
    fixture=json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    co=old.en.Regulator(nv,tuple(edges),*(fixture[z] for z in ("K","M_s","M_psi","Q")))
    assert co.K==2 and co.Q==1  # Issued witness uses the exact +/-1 character.
    fi=old.en.Regulator(nv,tuple(edges),2*co.K,2*co.M_s,4*co.M_psi,2*co.Q)
    p,_=old.make_map(co,fi,group)
    states=[]
    for terminal in (2*d+1,2*d+2):
        ap=[0]*nv;ap[terminal]=1
        occ=[0]*nv;occ[0]=fi.Q
        link=[0]*len(edges);link[1]=1
        states.append(old.en.State(tuple(ap),tuple(occ),(0,)*nv,tuple(link)))
    a,b=states
    assert all(old.en.valid_state(fi,x) for x in states)
    images=[p(x) for x in states]
    assert all(old.en.valid_state(co,x) for x in images)
    f=lambda x:(-1)**old.normal(x,co)[2][1]
    vals=[f(x) for x in images]
    assert vals[0]!=vals[1]
    changed=[v for v in range(nv) if a.aperture[v]!=b.aperture[v]]
    assert all(dist[v]==d for v in changed)
    radius=d-1
    assert all(a.aperture[v]==b.aperture[v] for v in range(nv) if dist[v]<=radius)
    assert a.occupation==b.occupation and a.phase==b.phase and a.link==b.link
    # All full source cell symmetries on the two tested inputs; phases are zero.
    for x,value in zip(states,vals):
        for h in group:
            z=old.act(old.normal(x,fi),h,fi.K)
            hx=old.en.State(z[0],z[1],(0,)*nv,z[2])
            assert old.en.valid_state(fi,hx) and f(p(hx))==value
    # The proof's two canonical scalar reductions, independent of d.
    reflected_w=(-1)%fi.K
    reduced_reflected=(-int(reflected_w//2))%co.K
    reduced_identity=1//2
    assert vals==[(-1)**reduced_reflected,(-1)**reduced_identity]
    return {"schema":"tect/pah-v2-spatial-frame-primary/1.0",
            "status":"PASS_SCOPED_WITNESS_UNIVERSAL_PROOF_IS_SEPARATE",
            "prereg_sha256":sha(SPEC),"script_sha256":sha(Path(__file__)),
            "source_pins":spec["source_pins"],"depth":d,"vertices":nv,"edges":len(edges),
            "maximum_degree":max(map(len,adjacency)),"automorphisms":group,
            "fixed_observable":"(-1)^(u_12+n_1-n_2 modulo 2)",
            "fine_states":[old.flat(x) for x in states],
            "coarse_images":[old.flat(x) for x in images],"values":vals,
            "changed_apertures":changed,"changed_distances":[dist[v] for v in changed],
            "equal_on_radius":radius,"two_point_sup_lower_bound":abs(vals[0]-vals[1])//2,
            "coverage":"Two fine states on one preregistered depth; complete fixture cell group. No full-state enumeration, generator/rate, Gibbs or limit calculation.",
            "non_claims":spec["non_claims"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args();data=json.loads(json.dumps(run()))
    if args.check: assert json.loads(OUT.read_text(encoding="utf-8"))==data
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as f:json.dump(data,f,indent=2,sort_keys=True);f.write("\n")
    print("PAH-V2 SPATIAL-FRAME PRIMARY: PASS (one exact witness; see arbitrary-distance proof)")


if __name__=="__main__":main()
