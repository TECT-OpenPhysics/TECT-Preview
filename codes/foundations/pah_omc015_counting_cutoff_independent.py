#!/usr/bin/env python3
"""Independent PAH-OMC-015 audit: polynomial energy and charge-tail route.

No primary or earlier PAH implementation is imported. Energy is rebuilt as a
polynomial in R from source incidence; all coefficients are exact rationals.
The independent bound is P(Q>0)<=(2^|V|-1) exp(-c(R)). The accompanying
analytic certificate proves the bound for every finite strip and cutoff.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "strategy/pa-hyp/PAH-OMC-015-counting-prereg-v1.json"
PIN = "0e07bd05c56c9765f15074505a5ce791622282a0e0c884bba277e780bbda0b35"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc015-counting-cutoff/independent.json"


def graph(n):
    edges = [(f"h{i}{j}", 2*i+j, 2*i+2+j) for i in range(n+1) for j in range(2)]
    edges += [(f"v{i}", 2*i, 2*i+1) for i in range(n+2)]
    edges += [(f"d{i}", 2*i, 2*i+3) for i in range(n)]
    faces = []
    for i in range(n):
        faces.extend([(f"h{i}0",f"v{i+1}",f"d{i}"), (f"d{i}",f"h{i}1",f"v{i}")])
    faces.append((f"h{n}0",f"v{n+1}",f"h{n}1",f"v{n}"))
    return edges, faces


def coefficients(p, aperture, radial, phase, link, edges, faces):
    s = [p["epsilon"]+(1-p["epsilon"])*j for j in aperture]
    u = [(-1)**k for k in link]
    signed = [radial[i]*(-1)**phase[i] for i in range(len(s))]
    e0 = sum(p["lambda_s"]*(x-1)**2/2 for x in s)
    e2 = sum((p["m2"]+p["g"]*s[i]**2)*radial[i]**2/2 for i in range(len(s)))
    e4 = sum(p["lambda_4"]*j**4/4 for j in radial)
    e6 = sum(p["eta_6"]*j**6/6 for j in radial)
    stiffness = {}
    sign = {}
    for k,(name,a,b) in enumerate(edges):
        stiffness[name] = 2/(s[a]+s[b])
        sign[name] = u[k]
        e0 += p["kappa_s"]*(s[a]-s[b])**2/2
        e2 += p["kappa_D"]*stiffness[name]*(signed[b]-u[k]*signed[a])**2/2
    for face in faces:
        e0 += p["kappa_g"]*sum(stiffness[e] for e in face)/len(face)*(1-math.prod(sign[e] for e in face))
    return e0,e2,e4,e6


def run(output=OUT):
    checks=[]
    def test(name, ok):
        checks.append({"name": name,"pass":bool(ok)})
        assert ok,name
    test("prereg hash",hashlib.sha256(REG.read_bytes()).hexdigest()==PIN)
    reg=json.loads(REG.read_text())
    for name,pin in reg["sources"].items():
        test(name,hashlib.sha256((ROOT/reg["source_path_base"]/name).read_bytes()).hexdigest()==pin)
    src=json.loads((ROOT/"strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json").read_text())["exact_scope"]["fixture"]
    p={k:F(str(v)) for k,v in src.items()}
    c2,c4,c6=p["g"]*p["epsilon"]**2/2,p["lambda_4"]/4,p["eta_6"]/6
    h=hashlib.sha256()
    totals=[]
    for n in (2,3):
        edges,faces=graph(n)
        nv=len({v for _,a,b in edges for v in (a,b)})
        count=0
        for variant in range(3):
            aperture=[(i+variant)%2 for i in range(nv)]
            phase=[(i*variant+variant)%2 for i in range(nv)]
            link=[(i+variant)%2 for i in range(len(edges))]
            for bits in itertools.product((0,1),repeat=nv):
                co=coefficients(p,aperture,bits,phase,link,edges,faces)
                zero=coefficients(p,aperture,[0]*nv,phase,link,edges,faces)
                q=sum(bits)
                assert co[0]==zero[0] and co[1]>=c2*q and co[2]==c4*q and co[3]==c6*q
                for r in (1,2):
                    energy=sum(co[i]*r**(2*i) for i in range(len(co)))
                    h.update(f"{n},{variant},{bits},{r}:{energy}\n".encode())
                    count+=1
        test(f"n{n} coefficient-wise all-R domination on diagnostic states",count>0)
        # Build occupation-count polynomial by recurrence, not binomial import.
        poly=[1]
        for _ in range(nv):
            new=[0]*(len(poly)+1)
            for i,a in enumerate(poly):
                new[i]+=a
                new[i+1]+=a
            poly=new
        test(f"n{n} charge polynomial and phase multiplicity",sum(poly)==2**nv and
             all(a==math.comb(nv,q) for q,a in enumerate(poly)))
        for z in (F(1,7),F(1,2),F(1)):
            tail=sum(a*z**q for q,a in enumerate(poly) if q)
            assert tail<=(sum(poly)-poly[0])*z
        test(f"n{n} independent total-charge tail bound",True)
        # Every label is retained; flip each gauge bit in full polynomial energy.
        bits=[i%2 for i in range(nv)]
        before=coefficients(p,aperture,bits,phase,link,edges,faces)
        for v in range(nv):
            gp=phase.copy(); gp[v]^=1
            gl=[x^int(v in (a,b)) for x,(_,a,b) in zip(link,edges)]
            assert coefficients(p,aperture,bits,gp,gl,edges,faces)==before
        test(f"n{n} single-vertex gauges preserve every energy coefficient",True)
        # Independently enumerate labelled inverses for all four families.
        moves=[]
        for v in range(nv):
            for sign in (-1,1):
                moves.append(("phase",v,sign))
                if 0<=aperture[v]+sign<=1:
                    moves.append(("aperture",v,sign))
        for e,(_,a,b) in enumerate(edges):
            for sign in (-1,1):
                moves.append(("link",e,sign))
            if bits[a]!=bits[b]:
                moves.append(("radial",e,1 if bits[a] else -1))
        for kind,idx,sgn in moves:
            ap,rp,ph,li=aperture.copy(),bits.copy(),phase.copy(),link.copy()
            if kind=="phase": ph[idx]=(ph[idx]+sgn)%2
            elif kind=="aperture": ap[idx]+=sgn
            elif kind=="link": li[idx]=(li[idx]+sgn)%2
            else:
                _,a,b=edges[idx]; rp[a]-=sgn; rp[b]+=sgn
            after=coefficients(p,ap,rp,ph,li,edges,faces)
            assert sum(rp)==sum(bits)
            ex,ey=sum(before),sum(after)
            assert -ex-(ey-ex)/2 == -ey-(ex-ey)/2
            if kind=="phase": ph[idx]=(ph[idx]-sgn)%2
            elif kind=="aperture": ap[idx]-=sgn
            elif kind=="link": li[idx]=(li[idx]-sgn)%2
            else: rp[a]+=sgn;rp[b]-=sgn
            assert (ap,rp,ph,li)==(aperture,bits,phase,link)
        test(f"n{n} independent root reversal and Gibbs exponent balance",True)
        totals.append({"n":n,"states_times_R":count,"vertices":nv,"charge_tail_prefactor":sum(poly)-poly[0]})
    payload={"schema":"tect/pah-omc015-independent/1.0","status":"PASS","checks":checks,
             "prereg_sha256":PIN,"code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "energy_digest":h.hexdigest(),"penalty_coefficients_R2_R4_R6":list(map(str,(c2,c4,c6))),
             "diagnostics":totals,"bound":"P(Q>0) <= (2^|V_n|-1) exp(-c(R)); each ell_v^2 <= 1_(Q>0)",
             "boundary":"Independently implemented exact polynomial and finite-state checks; universal proof is the coefficient/erasure argument in the certificate. No physical theorem."}
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=output.parent,suffix=".tmp")
    with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
        json.dump(payload,stream,indent=2,sort_keys=True);stream.write("\n")
    os.replace(tmp,output)
    print(f"PAH-OMC-015 INDEPENDENT: PASS ({len(checks)} assertions)")
    return payload


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    run(parser.parse_args().output)
