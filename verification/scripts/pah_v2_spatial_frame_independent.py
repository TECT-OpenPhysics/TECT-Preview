#!/usr/bin/env python3
"""Non-importing spatial-frame witness audit with structural group discovery.

Named vertices and distance-class permutations replace the primary's full
permutation scan. No map, primary checker or source enumerator is imported.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/"strategy/pa-hyp/PAH-v2-spatial-frame-prereg.json"
PIN="07d67b69ec742dc3c7981d2b73e102a88c5bc376a97009f53e125cde57c72997"  # INPUT.
RUN=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-spatial-frame"


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    assert sha(SPEC)==PIN
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    for path,pin in spec["source_pins"].items():assert sha(ROOT/path)==pin,path
    d=spec["preregistered_tests"]["smoke_depth"]
    names=["O"]+[side+str(i) for i in range(d+1) for side in ("L","R")]
    idx={name:i for i,name in enumerate(names)};nv=len(names)
    edge_names=[("O","L0"),("L0","R0"),("R0","O")]
    edge_names += [(s+str(i-1),s+str(i)) for i in range(1,d+1) for s in ("L","R")]
    edges=[(idx[v],idx[w]) for v,w in edge_names]
    neighbors={v:set() for v in names}
    for v,w in edge_names:neighbors[v].add(w);neighbors[w].add(v)
    dist={"O":0};queue=["O"]
    for v in queue:
        for w in sorted(neighbors[v]):
            if w not in dist:dist[w]=dist[v]+1;queue.append(w)
    # Every automorphism fixes O and preserves distance from O. Each nonzero
    # distance class has two vertices; exhaust their permitted swaps.
    classes=[[v for v in names if dist[v]==k] for k in range(1,d+2)]
    assert all(len(c)==2 for c in classes)
    autos=[]
    for flags in itertools.product((False,True),repeat=len(classes)):
        mapping={"O":"O"}
        for c,swap in zip(classes,flags):
            mapping.update(zip(c,c[::-1] if swap else c))
        if any({mapping[w] for w in neighbors[v]}!=neighbors[mapping[v]] for v in names):continue
        perm=tuple(idx[mapping[v]] for v in names)
        em=[]
        for v,w in edge_names:
            pair=(mapping[v],mapping[w])
            if pair in edge_names:em.append((edge_names.index(pair),1))
            else:em.append((edge_names.index(pair[::-1]),-1))
        # The unique triangle face maps to itself with either orientation.
        assert {em[i][0] for i in range(3)}=={0,1,2}
        autos.append((perm,tuple(em)))
    autos=tuple(sorted(autos))
    assert len(autos)==2
    inp=json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    k,ms,mp,q=(inp[z] for z in ("K","M_s","M_psi","Q"))
    assert k==2 and q==1
    def act(z,h,mod):
        a,l,w=z;p,e=h;aa=[0]*nv;ll=[0]*nv;ww=[0]*len(edges)
        for i,j in enumerate(p):aa[j]=a[i];ll[j]=l[i]
        for i,(j,s) in enumerate(e):ww[j]=s*w[i]%mod
        return tuple(aa),tuple(ll),tuple(ww)
    def normal(x,mod):
        a,l,n,u=x
        return a,l,tuple((u[i]+n[v]-n[w])%mod for i,(v,w) in enumerate(edges))
    def p(x):
        candidates=[(act(normal(x,2*k),h,2*k),h) for h in autos]
        z,h=min(candidates);a,l,w=z
        # Token pairing, not the primary map's prefix differences.
        tokens=[v for v in range(nv) for _ in range(l[v])]
        chosen=Counter(tokens[1::2])
        red=(tuple(v//2 for v in a),tuple(chosen[v] for v in range(nv)),tuple(v//2 for v in w))
        # Both discovered group elements are involutions, including edge signs.
        assert tuple(h[0][h[0][i]] for i in range(nv))==tuple(range(nv))
        aa,ll,ww=act(red,h,k)
        ns=tuple(v//2 for v in x[2])
        us=tuple((ww[i]-ns[v]+ns[w])%k for i,(v,w) in enumerate(edges))
        return aa,ll,ns,us
    def valid(x,fine):
        a,l,n,u=x;mult=2 if fine else 1
        return len(a)==len(l)==len(n)==nv and len(u)==len(edges) and all(0<=v<=mult*ms for v in a) and all(0<=v<=(4 if fine else 1)*mp for v in l) and sum(l)==mult*q and all(0<=v<mult*k for v in n+u)
    xs=[]
    for side in ("L","R"):
        a=[0]*nv;a[idx[side+str(d)]]=1;l=[0]*nv;l[0]=2*q;u=[0]*len(edges);u[1]=1
        xs.append((tuple(a),tuple(l),(0,)*nv,tuple(u)))
    ys=[p(x) for x in xs]
    assert all(valid(x,True) for x in xs) and all(valid(y,False) for y in ys)
    vals=[(-1)**normal(y,k)[2][1] for y in ys]
    assert vals[0]!=vals[1]
    changed=[names[v] for v in range(nv) if xs[0][0][v]!=xs[1][0][v]]
    assert all(dist[v]-1==d for v in changed)
    # Wrong formula controls: suppressing the frame OR its fine edge sign
    # would give the same base-edge quantization to the two input states.
    wrong_values=[(-1)**(x[3][1]//2) for x in xs]
    assert wrong_values[0]==wrong_values[1] and wrong_values!=vals
    # The observable must be invariant: the even coarse character is unchanged
    # by sign reversal; a signed odd fine residue is deliberately NOT used as f.
    assert all((-1)**w==(-1)**((-w)%k) for w in range(k))
    # Two-point bound is arithmetic, not a Gibbs-probability statement.
    gap=abs(vals[0]-vals[1])
    assert gap>0 and gap%2==0
    bound=gap//2
    primary=json.loads((RUN/"primary.json").read_text(encoding="utf-8"))
    flatten=lambda x:list(itertools.chain.from_iterable(x))
    assert primary["values"]==vals and primary["fine_states"]==[flatten(x) for x in xs]
    assert primary["coarse_images"]==[flatten(y) for y in ys]
    assert primary["automorphisms"]==json.loads(json.dumps(autos))
    assert primary["two_point_sup_lower_bound"]==bound
    return {"schema":"tect/pah-v2-spatial-frame-independent/1.0",
            "status":"PASS_EXACT_INSTANCE_AND_HOSTILE_CONTROLS",
            "prereg_sha256":sha(SPEC),"script_sha256":sha(Path(__file__)),
            "source_pins":spec["source_pins"],"primary_sha256":sha(RUN/"primary.json"),
            "depth":d,"automorphism_count":len(autos),"values":vals,
            "changed_vertices":changed,"distance_from_fixed_support":d,
            "two_point_sup_lower_bound":bound,
            "hostile_controls":{"wrong_frame_or_sign":wrong_values,"fixed_invariant_observable":"PASS exact coarse sign reversal","no_table_extrapolation":"General d argument is in the written proof, not inferred from this instance.","limit_order":"Fixed-cutoff support obstruction does not refute cutoff-first dynamics or Gibbs-L2.","no_family_adoption":"This diagnostic family is not an approved production tower."},
            "independence":"No primary/map/enumerator imports; named graph, distance partitions and token pairing. Same-task authorship.",
            "Lean":"NOT_RUN; external-person analytic review NOT_PERFORMED",
            "non_claims":spec["non_claims"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true")
    args=parser.parse_args();data=json.loads(json.dumps(run()));out=RUN/"independent-hostile.json"
    if args.check:assert json.loads(out.read_text(encoding="utf-8"))==data
    else:
        with out.open("w",encoding="utf-8",newline="\n") as f:json.dump(data,f,indent=2,sort_keys=True);f.write("\n")
    print("PAH-V2 SPATIAL-FRAME INDEPENDENT/HOSTILE: PASS (separate implementation; no limit claim)")


if __name__=="__main__":main()
