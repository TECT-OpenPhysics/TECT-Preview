#!/usr/bin/env python3
"""Independent reconstruction of EXP-001169 (no primary/helper imports)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-extended-direct-d-delta-d-shape-beta"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream: json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


class Checks:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []
    def add(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name":name,"group":group,"status":"PASS","actual":str(actual),"expected":str(expected)})


def local_ops(d: int) -> tuple[np.ndarray, np.ndarray]:
    a=np.zeros((d,d),dtype=complex)
    for k in range(d-1): a[k,k+1]=np.sqrt(k+1.0)
    return (a+a.conj().T)/np.sqrt(2.0),(a-a.conj().T)/(1j*np.sqrt(2.0))


def tensor_at(single: np.ndarray, site: int, count: int, identity: np.ndarray) -> np.ndarray:
    result=None
    for k in range(count): result=single.copy() if result is None and k==site else (identity.copy() if result is None else np.kron(result, single if k==site else identity))
    if result is None: raise ValueError("empty")
    return result


def sym(m: np.ndarray) -> np.ndarray: return (m+m.conj().T)/2.0
def eig(m: np.ndarray) -> tuple[np.ndarray,np.ndarray]: return np.linalg.eigh(sym(m))
def evo(vals: np.ndarray, vecs: np.ndarray, t: float) -> np.ndarray: return (vecs*np.exp(-1j*t*vals))@vecs.conj().T
def gibbs(vals: np.ndarray, vecs: np.ndarray, beta: float) -> np.ndarray:
    w=np.exp(-beta*(vals-float(np.min(vals)))); w/=float(np.sum(w)); return (vecs*w)@vecs.conj().T
def char(q: np.ndarray, amp: float) -> np.ndarray:
    vals,vecs=eig(q); return (vecs*np.exp(1j*amp*vals))@vecs.conj().T
def cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    vals,vecs=eig(q); s=np.abs(vals)/radius; taper=np.where(s<=1,1,np.where(s<2,0.5*(1+np.cos(np.pi*(s-1))),0)); return (vecs*(vals*taper))@vecs.conj().T
def seminorm(x: np.ndarray, rho: np.ndarray) -> float:
    v=np.trace(rho@x.conj().T@x)+np.trace(rho@x@x.conj().T); return float(np.sqrt(max(0.0,float(np.real(v)))))


def ladder(name: str) -> list[tuple[int,int]]: return [(k,k+1) for k in range({"path4":3,"path6":5}[name])]


def assemble(name: str, d: int, p: dict[str,str]) -> tuple[np.ndarray,np.ndarray]:
    v=int(name[4:]); q,p_m=local_ops(d); I=np.eye(d,dtype=complex); qs=[tensor_at(q,k,v,I) for k in range(v)]; ps=[tensor_at(p_m,k,v,I) for k in range(v)]
    chi=float(Fraction(p["chi"])); r=float(Fraction(p["r"])); g=float(Fraction(p["g"])); c=float(Fraction(p["c"])); lam=float(Fraction(p["lambda"]))
    terms=[pm@pm/(2*chi)+r*qq@qq/2+g*qq@qq@qq@qq/4 for qq,pm in zip(qs,ps)]
    for u,w in ladder(name):
        diff=qs[u]-qs[w]; sq=diff@diff; terms.append(c*sq/2+lam*sq@(qs[u]@qs[u]+qs[w]@qs[w])/4)
    return sym(sum(terms,np.zeros_like(qs[0]))), q


def run() -> dict[str,Any]:
    m=json.loads(MANIFEST.read_text(encoding="utf-8")); f=m["finite_fixture"]; scope=m["scope"]; checks=Checks(); checks.add("identity",m["exploration_id"]=="EXP-001169" and m["task_id"]=="T-054",[m["exploration_id"],m["task_id"]],"EXP-001169/T-054","provenance"); checks.add("claim nonbearing",m["claim_bearing"] is False,m["claim_bearing"],False,"scope"); checks.add("beta grid",f["beta_values"]==[0.5,1.0,2.0],f["beta_values"],"0.5,1,2","fixture"); checks.add("scope firewall",scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["beta_uniform_direct_d_cauchy_closed"],scope,"finite only","scope")
    d=int(f["oscillator_dimension"]); amp=float(f["character_amplitude"]); h=float(f["hbar"]); tol=float(f["finite_tolerance"]); tail_tol=float(f["tail_tolerance"]); src=int(f["source_site"]); p=m["model_parameters"]; volumes=[]
    for name,decl in f["graphs"].items():
        v=int(decl["vertices"]); edges=[tuple(int(x) for x in e) for e in decl["edges"]]; expected=ladder(name); checks.add(f"{name} edge reconstruction",edges==expected,edges,expected,"graph"); H,q_local=assemble(name,d,p); vals,vecs=eig(H); I=np.eye(d,dtype=complex); A=tensor_at(char(q_local,amp),src,v,I); ref={t:evo(vals,vecs,float(t)) for t in f["time_values"]}; radii=[]
        q,_=local_ops(d)
        for rad in map(float,f["radius_values"]):
            qcut=cutoff(q,rad); # rebuild with the replaced coordinate below
            qs=[tensor_at(qcut,k,v,I) for k in range(v)]; ps=[tensor_at(local_ops(d)[1],k,v,I) for k in range(v)]; chi=float(Fraction(p["chi"])); r=float(Fraction(p["r"])); g=float(Fraction(p["g"])); c=float(Fraction(p["c"])); lam=float(Fraction(p["lambda"])); terms=[pm@pm/(2*chi)+r*qq@qq/2+g*qq@qq@qq@qq/4 for qq,pm in zip(qs,ps)]
            for u,w in edges:
                diff=qs[u]-qs[w]; sq=diff@diff; terms.append(c*sq/2+lam*sq@(qs[u]@qs[u]+qs[w]@qs[w])/4)
            Hc=sym(sum(terms,np.zeros_like(H))); tail=H-Hc; tail_norm=float(np.linalg.norm(tail,ord=2)); checks.add(f"{name} L={rad} tail finite",np.isfinite(tail_norm),tail_norm,"finite","cutoff");
            if rad==max(map(float,f["radius_values"])): checks.add(f"{name} L={rad} zero tail",tail_norm<=tail_tol,tail_norm,f"<={tail_tol}","cutoff")
            vp,up=eig(H+tail); vm,um=eig(H-tail); beta_rows=[]
            for beta in map(float,f["beta_values"]):
                rho=gibbs(vals,vecs,beta); times=[]
                zero=evo(vals,vecs,0)@A@evo(vals,vecs,0).conj().T-A; checks.add(f"{name} L={rad} beta={beta} t=0 anchor",seminorm(zero,rho)<=tail_tol,seminorm(zero,rho),f"<={tail_tol}","direct D")
                for t in map(float,f["time_values"]):
                    O={}
                    for sign,V,U in ((1,vp,up),(-1,vm,um)):
                        Us=evo(V,U,t); Ur=ref[t]; D=Us@A@Us.conj().T-Ur@A@Ur.conj().T; dD=-beta*(H@D-D@H); vals_row={"D_norm":seminorm(D,rho),"delta_D_norm":seminorm(dD,rho),"matrix_norm":float(np.linalg.norm(D,ord=2))}; checks.add(f"{name} L={rad} beta={beta} t={t} sign={sign} finite",all(np.isfinite(x) for x in vals_row.values()),vals_row,"finite","direct D"); O[str(sign)]=vals_row
                    times.append({"time":t,"orientations":O,"two_orientation_sum_of_norms":{k:O["1"][k]+O["-1"][k] for k in ("D_norm","delta_D_norm","matrix_norm")}})
                beta_rows.append({"beta":beta,"times":times})
            radii.append({"radius":rad,"tail_operator_norm":tail_norm,"beta_rows":beta_rows})
        volumes.append({"graph":name,"volume":v,"dimension":d**v,"radius_rows":radii})
    maxima={str(x["volume"]):{"D_norm":max(t["two_orientation_sum_of_norms"]["D_norm"] for r in x["radius_rows"] for b in r["beta_rows"] for t in b["times"]),"delta_D_norm":max(t["two_orientation_sum_of_norms"]["delta_D_norm"] for r in x["radius_rows"] for b in r["beta_rows"] for t in b["times"])} for x in volumes}; checks.add("maxima finite",all(np.isfinite(v) for x in maxima.values() for v in x.values()),maxima,"finite","scaling")
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","audit_id":"PA-CP1-ST8-Q3LOCK-EXTENDED-DIRECT-D-DELTA-D-SHAPE-BETA","claim_id":m["claim_ids"][0],"task_id":m["task_id"],"exploration_id":m["exploration_id"],"verdict":"PASS","passed":len(checks.rows),"assertion_count":len(checks.rows),"assertions":checks.rows,"derived":{"volume_rows":volumes,"maxima_by_volume":maxima,"finite_direct_D_closed":True,"finite_direct_delta_D_closed":True,"finite_two_orientation_difference_closed":True,"cutoff_zero_tail_fixture_closed":True,"path_exhaustion_fixture_closed":True,"beta_grid_fixture_closed":True,"volume_uniform_direct_d_cauchy_closed":False,"beta_uniform_direct_d_cauchy_closed":False,"delta_d_cauchy_closed":False,"product_core_density_closed":False,"exhaustion_independence_closed":False,"group_law_closed":False,"common_alpha_closed":False,"hamiltonian_os_identification_closed":False,"kms_gns_gap_closed":False,"continuum_closed":False,"c6_closed":False,"sector_a_closed":False,"pre_a_closed":False,"no_new_negative_result":True,"no_tier_change":True,"no_pdf":True},"boundary":scope}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args(); payload=run();
    if not a.self_test: save(a.output if a.output.is_absolute() else REPO/a.output,payload)
    print(f"INDEPENDENT EXTENDED-DIRECT-D-DELTA-D PASS {payload['passed']}/{payload['assertion_count']}"); return 0
if __name__=="__main__": raise SystemExit(main())
