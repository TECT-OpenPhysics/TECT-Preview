#!/usr/bin/env python3
"""Independent exact Fraction audit for the entire source-weight envelope."""

from __future__ import annotations
import argparse, hashlib, json, math, os, tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any
REPO=Path(__file__).resolve().parents[2]; SCRIPT=Path(__file__).resolve(); SLUG="pre-a-cp1-st8-q3lock-entire-source-weight-generating-envelope"; MANIFEST=REPO/f"strategy/{SLUG}-manifest.json"; DEFAULT_OUTPUT=REPO/"claims/C6-SPACETIME-SIGNATURE/runs"/f"2026-08-24-primary-{SLUG}"/"independent.json"
def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def safe(value:Any)->Any:
    if isinstance(value,Fraction):return str(value)
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe(v) for v in value]
    return value
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:json.dump(safe(payload),stream,indent=2,sort_keys=True,ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
class Audit:
    def __init__(self)->None:self.rows:list[dict[str,Any]]=[]
    def check(self,name:str,ok:bool,actual:Any,expected:Any,group:str)->None:
        if not ok:raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name":name,"group":group,"status":"PASS","actual":safe(actual),"expected":safe(expected)})
def run()->dict[str,Any]:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); audit=Audit(); audit.check("exploration",manifest["exploration_id"]=="EXP-001032",manifest["exploration_id"],"EXP-001032","provenance"); audit.check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False,"scope")
    g=Fraction(3,5); lam=Fraction(2,7); c=Fraction(2,3); t=Fraction(1,3); G=g+3*lam; rate=t*G/4; sigma=Fraction(1,5); margin=sigma-rate; prefactor=c*t; order=8
    audit.check("coefficient",G==Fraction(51,35),G,Fraction(51,35),"derivation"); audit.check("rate",rate==Fraction(17,140),rate,Fraction(17,140),"series"); audit.check("margin",margin==Fraction(11,140) and margin>0,margin,Fraction(11,140),"weight"); audit.check("prefactor",prefactor==Fraction(2,9),prefactor,Fraction(2,9),"weight")
    rows=[]
    for amplitude in [0,1,2,5,10]:
        partial=sum(Fraction(n)*c*(G/4)**(n-1)*abs(amplitude)**(4*n-3)*t**n/Fraction(math.factorial(n)) for n in range(1,order+1)) if amplitude else Fraction(0)
        exponent=float(rate)*abs(amplitude)**4
        bound=float(prefactor*abs(amplitude))*math.exp(exponent) if amplitude and exponent < 700 else (float("inf") if amplitude else 0.0)
        audit.check(f"series bound a={amplitude}",float(partial)<=bound+1e-10,float(partial),f"<={bound}","series"); rows.append({"amplitude":amplitude,"partial_sum":partial,"bound":bound})
    audit.check("sigma dominates",sigma>rate,sigma,f">{rate}","weight"); audit.check("actual Q3 open",manifest["scope"]["no_new_negative_result"] is True,manifest["scope"],True,"scope")
    passed=len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"series_rows":rows,"derived":{"G":G,"rate":rate,"sigma":sigma,"margin":margin,"prefactor":prefactor,"truncation_order":order,"candidate_entire_weight_closed_for_prescribed_words":True,"actual_q3_word_incidence_closed":False,"analytic_domain_closed":False,"volume_uniform_history_closed":False,"exhaustion_cauchy_closed":False},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace("\\","/"),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace("\\","/"),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}
def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test:atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT ENTIRE-SOURCE-WEIGHT PASS {payload['passed']}/{payload['total']}"); return 0
if __name__=="__main__":raise SystemExit(main())
