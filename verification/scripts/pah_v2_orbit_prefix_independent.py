#!/usr/bin/env python3
"""Non-importing token-pair implementation of the unapproved orbit-prefix map.

Flat tuples; direct source reflection; token pairing rather than prefix-floor
differences. Exact arithmetic. Same author, not external-person verification.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import itertools as it
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=ROOT/"strategy/pa-hyp/PAH-v2-orbit-prefix-draft.json"
PIN="0f1aaa35c6729c2c3a8a484e8a60ae3e5de3941736a78e6fdd90c92a328314cd"  # INPUT.
RUN=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-orbit-prefix"
FAMILIES=("PH","TR","LK","AP")


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    assert sha(SPEC)==PIN
    spec=json.loads(SPEC.read_text(encoding="utf-8"))
    for p,h in spec["source_pins"].items(): assert sha(ROOT/p)==h,p
    inp=json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))["primary_fixture_inputs"]
    assert inp["vertices"]==3 and inp["edges"]==[[0,1],[1,2],[2,0]]
    assert inp["outer_anchor"]==[0] and inp["core_anchor"]==[1,2]
    assert inp["faces"]==[[[0,1],[1,1],[2,1]]]
    k,ms,mp,q=(inp[s] for s in ("K","M_s","M_psi","Q"));fk=2*k
    edges=inp["edges"]
    def reflect(z,mod): return (z[0],z[2],z[1],z[3],z[5],z[4],-z[8]%mod,-z[7]%mod,-z[6]%mod)
    def norm(x,mod): return x[:6]+tuple((x[9+e]+x[6+v]-x[6+w])%mod for e,(v,w) in enumerate(edges))
    def split(z): return [z[:3],z[3:6],z[6:]]
    def quant(z):
        tokens=[v for v in range(3) for _ in range(z[3+v])]
        assert len(tokens)%2==0
        chosen=Counter(tokens[1::2])
        return tuple(a//2 for a in z[:3])+tuple(chosen[v] for v in range(3))+tuple(w//2 for w in z[6:])
    @lru_cache(None)
    def reduce(z):
        rz=reflect(z,fk)
        if z<=rz: return quant(z)
        return reflect(quant(rz),k)
    def p(x):
        z=reduce(norm(x,fk));ns=tuple(n//2 for n in x[6:9])
        us=tuple((z[6+e]-ns[v]+ns[w])%k for e,(v,w) in enumerate(edges))
        return z[:6]+ns+us
    def valid(x,fine):
        mod=fk if fine else k;am=2*ms if fine else ms;om=4*mp if fine else mp;charge=2*q if fine else q
        return len(x)==12 and all(0<=a<=am for a in x[:3]) and all(0<=l<=om for l in x[3:6]) and sum(x[3:6])==charge and all(0<=n<mod for n in x[6:])
    hd=hashlib.sha256();nc=0;full=0;phases=tuple(it.product(range(fk),repeat=3))
    for ap in it.product(range(2*ms+1),repeat=3):
        for occ in it.product(range(4*mp+1),repeat=3):
            if sum(occ)!=2*q: continue
            for w in it.product(range(fk),repeat=3):
                z=ap+occ+w;rr=reduce(z);nc+=1
                hd.update(json.dumps([split(z),split(rr)],separators=(",",":")).encode("ascii"));hd.update(b"\n")
                rz=reduce(reflect(z,fk));assert min(rz,reflect(rz,k))==min(rr,reflect(rr,k))
                for ns in phases:
                    x=ap+occ+ns+tuple((w[e]-ns[v]+ns[t])%fk for e,(v,t) in enumerate(edges))
                    y=p(x);assert valid(x,True) and valid(y,False) and norm(y,k)==rr;full+=1
    coarse=[ap+occ+ns+u for occ in it.product(range(mp+1),repeat=3) if sum(occ)==q
            for ap in it.product(range(ms+1),repeat=3) for ns in it.product(range(k),repeat=3) for u in it.product(range(k),repeat=3)]
    assert all(p(tuple(2*v for v in x))==x for x in coarse)
    labels=[(fam,c,s) for fam in FAMILIES for c in range(3) for s in (-1,1)]
    def move(x,r,fine):
        fam,c,s=r;y=list(x);mod=fk if fine else k
        if fam=="PH": y[6+c]=(y[6+c]+s)%mod
        elif fam=="LK": y[9+c]=(y[9+c]+s)%mod
        elif fam=="AP": y[c]+=s
        else: v,w=edges[c];y[3+v]-=s;y[3+w]+=s
        return tuple(y) if valid(tuple(y),fine) else None
    inverse=lambda r:(r[0],r[1],-r[2])
    key=lambda x,r:x+(FAMILIES.index(r[0]),r[1],r[2])
    @lru_cache(None)
    def first_match(x,y): return next((r for r in labels if move(x,r,False)==y),None)
    def pair(x,r,y):
        if key(x,r)<key(y,inverse(r)): return first_match(p(x),p(y))
        ans=first_match(p(y),p(x));return None if ans is None else inverse(ans)
    counts=Counter();rd=hashlib.sha256();md=hashlib.sha256()
    for c in coarse:
        x=tuple(2*v for v in c);assigned=set()
        for s in labels:
            y=move(x,s,True)
            if y is None: continue
            r=pair(x,s,y);rr=pair(y,inverse(s),x)
            if r is None: assert rr is None;counts["unpaired"]+=1
            else:
                assert rr==inverse(r) and move(p(x),r,False)==p(y)
                counts["paired"]+=1;assigned.add(r)
            rd.update(json.dumps([x,s,r],separators=(",",":")).encode("ascii"));rd.update(b"\n")
        for r in labels:
            if move(c,r,False) is None: continue
            counts["coarse_labels_retained"]+=1
            if r not in assigned:
                counts["unmatched_coarse"]+=1
                md.update(json.dumps([x,r],separators=(",",":")).encode("ascii"));md.update(b"\n")
    a=(0,0,0,0,1,1,0,0,0,0,1,0);b=a[:9]+(1,1,0)
    assert valid(a,True) and valid(b,True)
    vals=[(-1)**norm(p(x),k)[7] for x in (a,b)]
    assert vals[0]!=vals[1]
    # Concrete malicious shortcuts, not modified production definitions.
    undo_witness=next(x for x in coarse if tuple(2*v for v in norm(x,k))>reflect(tuple(2*v for v in norm(x,k)),fk))
    jx=tuple(2*v for v in undo_witness)
    bad_normal=quant(min(norm(jx,fk),reflect(norm(jx,fk),fk)))
    assert bad_normal!=norm(undo_witness,k)
    missing_phase=next(x for x in coarse if any(l==0 and n!=0 for l,n in zip(x[3:6],x[6:9])))
    assert p(tuple(2*v for v in missing_phase))[6:9]==missing_phase[6:9]
    # If the cell frame is chosen from a subset of H, invariant-output tests
    # need not pass. Find a fixture counterexample to raw quantization.
    bad_symmetry=None
    for ap in it.product(range(2*ms+1),repeat=3):
        if bad_symmetry is not None: break
        for occ in it.product(range(4*mp+1),repeat=3):
            if sum(occ)!=2*q: continue
            z=ap+occ+(0,0,0);a0=quant(z);b0=quant(reflect(z,fk))
            if min(a0,reflect(a0,k))!=min(b0,reflect(b0,k)):
                bad_symmetry=z;break
    assert bad_symmetry is not None
    primary=json.loads((RUN/"primary.json").read_text(encoding="utf-8"))
    assert primary["normal_map_digest"]==hd.hexdigest() and primary["full_fine_states_checked"]==full
    assert primary["root_counts"]==dict(counts) and primary["root_assignment_digest"]==rd.hexdigest()
    assert primary["unmatched_coarse_digest"]==md.hexdigest() and primary["support_witness"]["values"]==vals
    return {"schema":"tect/pah-v2-orbit-prefix-independent/1.0","status":"PASS_FIXED_G_DRAFT_AUDIT",
            "prereg_sha256":sha(SPEC),"script_sha256":sha(Path(__file__)),"primary_sha256":sha(RUN/"primary.json"),
            "source_pins":spec["source_pins"],"normal_coordinates_checked":nc,"full_fine_states_checked":full,
            "normal_map_digest":hd.hexdigest(),"coarse_right_inverse_checks":len(coarse),"root_counts":dict(counts),
            "root_assignment_digest":rd.hexdigest(),"unmatched_coarse_digest":md.hexdigest(),
            "support_witness_values":vals,"hostile_controls":{"missing_frame_inverse":undo_witness,"raw_quantizer_fails_invariant_output":bad_symmetry,"zero_radius_phase_must_survive_right_inverse":missing_phase,
                "locality_overclaim":"Exact support enlargement witness; all-G support is not a volume-uniform locality result.","root_deduplication":"Every source coarse label retained and unmatched labels reported separately.","scope":"No Gibbs/projectivity/rate/time or full-contract admission follows from pullback algebra."},
            "independence":"No primary/source-enumerator imports. Token pairing and flat direct reflection; same-task authorship.","Lean":"NOT_RUN; no new kernel proof or external reviewer claim."}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--check",action="store_true");args=ap.parse_args()
    data=json.loads(json.dumps(run()));out=RUN/"independent-hostile.json"
    if args.check: assert json.loads(out.read_text(encoding="utf-8"))==data
    else:
        with out.open("w",encoding="utf-8",newline="\n") as f:json.dump(data,f,indent=2,sort_keys=True);f.write("\n")
    print("PAH-V2-ORBIT-PREFIX INDEPENDENT/HOSTILE: PASS (full finite tuple coverage; no full-tower admission)")


if __name__=="__main__":main()
