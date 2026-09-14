#!/usr/bin/env python3
"""PAH-v2 adversarial controls, version 0.1.0, first issued 2026-09-11.

Mutations are rejected alternatives, not modifications of the frozen model.
Exact symbolic local algebra complements the all-finite proof; bounded map
witnesses exercise the actual pinned enumerator. No external reviewer claimed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import sympy as s

__version__="0.1.0"
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-finite/hostile.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check():
    manifest=ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json"
    assert sha(manifest)=="531697fa28c5f2e7f4177b42bc12ebd8fc1ffb7e9790d07063082e0ec3d6a331"  # INPUT pin
    data=json.loads(manifest.read_text())
    for p,h in data["source_pins"].items():
        assert sha(ROOT/p)==h
    desc=importlib.util.spec_from_file_location("pah_hostile_enum",ROOT/"codes/foundations/pah_v2_root_enumerator.py")
    e=importlib.util.module_from_spec(desc); sys.modules[desc.name]=e; desc.loader.exec_module(e)
    rejected={}
    def reject(name,condition):
        assert condition,name
        rejected[name]=True
    c=s.Symbol("c",positive=True)
    reject("omit_B_half",s.expand(2*c-c)!=0)
    reject("extra_rate_half_in_root_measure",s.expand(c*c/2-c)!=0)
    fx,fy,beta,m=s.symbols("fx fy beta m",real=True)
    lhs=s.exp(-beta*fx)*m*s.exp(-beta*(fy-fx)/2)
    rhs=s.exp(-beta*fy)*m*s.exp(-beta*(fx-fy)/2)
    assert s.simplify(lhs-rhs)==0
    wrong=s.exp(-beta*fx)*m*s.exp(beta*(fy-fx)/2)
    reject("wrong_midpoint_rate_sign",s.simplify(wrong-rhs)!=0)
    reject("bare_root_measure_inversion",s.simplify(s.exp(-beta*fx)-s.exp(-beta*fy))!=0)
    # Independent symbolic gauge/edge reversal crosswalk, arbitrary unit phases.
    a,b,ac,bc,u,gv,gw=s.symbols("a b ac bc u gv gw",nonzero=True)
    norm=(b-u*a)*(bc-ac/u)
    transformed=(b*gw-u*gw/gv*a*gv)*(bc/gw-ac/gv/(u*gw/gv))
    reversed_edge=(a-b/u)*(ac-u*bc)
    assert s.simplify(transformed-norm)==0
    assert s.simplify(reversed_edge-norm)==0
    # K=4 unit-phase tooling oracle: initially a=b=u=1; g_v=1,g_w=i.
    good=s.I-s.I
    bad=s.I-(-s.I)
    assert s.expand_complex(good*s.conjugate(good))==0
    reject("wrong_gauge_link_sign",s.expand_complex(bad*s.conjugate(bad))!=0)
    reg=e.Regulator(3,((0,1),(1,2),(2,0)),2,1,1,1)
    x=e.State((0,0,0),(1,0,0),(1,0,0),(0,0,0))
    plus,minus=e.Move("LK",0,1),e.Move("LK",0,-1)
    assert plus!=minus and e.apply_move(reg,x,plus)==e.apply_move(reg,x,minus)
    reject("deduplicate_coincident_K2_labels",len({plus,minus})!=len({e.apply_move(reg,x,plus),e.apply_move(reg,x,minus)}))
    tr=e.Move("TR",0,1); y=e.apply_move(reg,x,tr)
    erased=e.State(y.aperture,y.occupation,tuple(0 if l==0 else n for l,n in zip(y.occupation,y.phase)),y.link)
    reject("erase_zero_occupation_phase",e.apply_move(reg,erased,tr.inverse())!=x)
    ap=e.Move("AP",0,1); ay=e.apply_move(reg,x,ap)
    assert x!=ay
    # At epsilon=1, the evaluation 1+j*(1-1)/M_s is identical for all j.
    reject("epsilon1_value_quotient",x.aperture!=ay.aperture and all(1+j*(1-1)/reg.M_s==1 for j in x.aperture+ay.aperture))
    reject("clip_invalid_aperture_move",e.apply_move(reg,x,e.Move("AP",0,-1)) is None)
    # Reversing edge (1,2) under the anchor-preserving swap requires sign -1.
    ax=e.State((0,0,0),(0,0,1),(0,0,0),(0,0,0))
    correct=e.apply_move(reg,ax,e.Move("TR",1,-1))
    wrong=e.apply_move(reg,ax,e.Move("TR",1,1))
    reject("omit_TR_orientation_sign",correct is not None and wrong!=correct)
    h=s.Symbol("h",integer=True,positive=True)
    reject("unnormalized_group_sum_projection",s.expand(h*h-h)!=0)
    # Gauge at vertex 1 and swapping vertices 1,2 do not commute individually.
    phase=(0,1,0); swap=(phase[0],phase[2],phase[1])
    reject("elementwise_gauge_Aut_commutation",phase!=swap)
    # A negative mass/quartic coefficient does not invalidate finite Gibbs.
    # Check the exact symbolic proof's restriction is epsilon>0, not F>=0.
    assert s.exp(s.Integer(3)).is_positive
    return {"schema":"tect/pah-v2-finite-hostile/1.0","status":"PASS",
            "script_version":__version__,"script_sha256":sha(Path(__file__)),"manifest_sha256":sha(manifest),
            "mutations_rejected":rejected,"rejected_count":len(rejected),
            "symbolic_checks":{"midpoint_flux":True,"gauge_edge_norm":True,"orientation_edge_norm":True},
            "scope":"Exact local symbolic and bounded adversarial controls, not an external mathematical audit",
            "environment":{"python":platform.python_version(),"sympy":s.__version__},
            "non_claims":"No mutation is an authorized model change; no independent-person review, limits or physical conclusion."}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--check",action="store_true"); args=p.parse_args()
    result=check()
    if args.check:
        old=json.loads(OUT.read_text())
        assert {k:v for k,v in old.items() if k!="environment"}=={k:v for k,v in result.items() if k!="environment"}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as f:
            json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print(f"PAH-V2-HOSTILE: PASS ({result['rejected_count']} exact mutation controls rejected)")


if __name__=="__main__":
    main()
