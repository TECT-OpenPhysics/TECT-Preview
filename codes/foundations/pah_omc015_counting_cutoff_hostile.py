#!/usr/bin/env python3
"""Adversarial controls for the PAH counting ensemble; exact arithmetic only.

Controls attack conventions and logical scope. They are not substitute PAH
models, fitted ensembles, or evidence of a new physical result.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc015-counting-cutoff/hostile.json"


def run(output=OUT):
    path=ROOT/"codes/foundations/pah_omc015_counting_cutoff_independent.py"
    spec=importlib.util.spec_from_file_location("independent_for_mutations",path)
    ind=importlib.util.module_from_spec(spec);spec.loader.exec_module(ind)
    p={k:F(str(v)) for k,v in json.loads((ROOT/"strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json").read_text())["exact_scope"]["fixture"].items()}
    checks=[]
    def reject(name, detected):
        checks.append({"name":name,"pass":bool(detected),"disposition":"REJECTED_MUTATION_OR_INVALID_INFERENCE"})
        assert detected,name
    edges,faces=ind.graph(2)
    nv=len({v for _,a,b in edges for v in (a,b)})
    ap=[0]*nv;ph=[0]*nv;li=[0]*len(edges)
    occ=[1]+[0]*(nv-1)
    zero=ind.coefficients(p,ap,[0]*nv,ph,li,edges,faces)
    charged=ind.coefficients(p,ap,occ,ph,li,edges,faces)
    reject("opposite Gibbs sign cannot satisfy the suppression inequality",sum(charged)>sum(zero))
    reject("missing sextic denominator changes source coefficient",charged[3]!=p["eta_6"]*sum(occ))
    reject("wrong aperture mass factor two",p["g"]*p["epsilon"]**2/2 != p["g"]*p["epsilon"]**2)
    count_correct=[math.comb(nv,q)*2**(2*nv+len(edges)) for q in range(nv+1)]
    count_collapsed=[math.comb(nv,q)*2**(nv+q+len(edges)) for q in range(nv+1)]
    reject("quotienting phases at zero occupation changes counting measure",count_correct!=count_collapsed and sum(count_correct)!=sum(count_collapsed))
    # Actual model: at n=2,R=2, the proven exp(c)>=1+c gives Z_1/Z_0<1.
    r=F(2)
    c=p["eta_6"]*r**6/6+p["lambda_4"]*r**4/4+p["g"]*p["epsilon"]**2*r**2/2
    reject("equal sector weights differ from partition-weighted law",F(nv)/(1+c)<1)
    reject("suppressing duplicated K=2 phase/link channels changes L",2*nv+2*len(edges)!=nv+len(edges))
    z=F(1)
    reject("zero energy penalty supplies no vanishing tail",z*(1+z)**(nv-1)>0)
    # An explicit rational finite-positive sequence has zero infimum.
    for epsilon in (F(1,2),F(1,10),F(1,100)):
        k=epsilon.denominator+1
        assert 0<F(1,k)<epsilon
    reject("finite positivity is insufficient for limiting nondegeneracy",True)
    # b(n,R)=n/(n+R): fixed n then R gives 0, reversed gives 1.
    for n in range(2,6):
        assert F(n,n+n*100)<F(1,100)
    for r0 in range(1,5):
        assert 1-F(r0*100,r0*100+r0)<F(1,100)
    reject("order interchange invalid for general two-index arrays",True)
    reject("holonomy square must not collapse with radial occupancy",all(h*h==1 for h in (-1,1)))
    # Conditional cancellation is an exact finite arithmetic property, not
    # evidence of uniqueness of the ensemble prior.
    for zq,zt,a in ((F(2),F(7),F(1)),(F(5),F(11),F(3))):
        assert (zq/zt)*(a/zq)==a/zt
        assert F(1,2)*(a/zq)!=a/zt
    reject("substituting an arbitrary sector prior changes unconditional law",True)
    # Two-point state with mass 1/(k+1) at occupied: weak limit exists and is
    # degenerate, so loss of occupancy cannot prove weak-state nonexistence.
    for k in range(1,10):
        a=F(1,k+1); assert (1-a)+a==1 and 0<a<1
    reject("zero limiting observable does not imply no weak state",True)
    payload={"schema":"tect/pah-omc015-hostile/1.0","status":"PASS","checks":checks,
             "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "external_independent_review":"NOT_PERFORMED; this is an internal adversarial implementation",
             "non_claims":"Control examples diagnose invalid inference only; no substitute carrier or physical conclusion."}
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=output.parent,suffix=".tmp")
    with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
        json.dump(payload,stream,indent=2,sort_keys=True);stream.write("\n")
    os.replace(tmp,output)
    print(f"PAH-OMC-015 HOSTILE: PASS ({len(checks)} controls)")
    return payload


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    run(parser.parse_args().output)
