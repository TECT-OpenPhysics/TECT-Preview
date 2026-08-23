#!/usr/bin/env python3
"""Primary symbolic audit for the conditional entire source-weight envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp

REPO=Path(__file__).resolve().parents[2]
SCRIPT=Path(__file__).resolve()
SLUG="pre-a-cp1-st8-q3lock-entire-source-weight-generating-envelope"
MANIFEST=REPO/f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT=REPO/"claims/C6-SPACETIME-SIGNATURE/runs"/f"2026-08-24-primary-{SLUG}"/"primary.json"
def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def safe(value:Any)->Any:
    if isinstance(value,sp.Basic):return str(value)
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe(v) for v in value]
    return value
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            json.dump(safe(payload),stream,indent=2,sort_keys=True,ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
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
    g=sp.Rational(3,5); lam=sp.Rational(2,7); c=sp.Rational(2,3); t=sp.Rational(1,3); G=sp.expand(g+3*lam); rate=t*G/4; sigma=sp.Rational(1,5); margin=sigma-rate; prefactor=c*t; a=sp.symbols("a", nonnegative=True); m=sp.symbols("m", integer=True, positive=True)
    summand=m*c*(G/4)**(m-1)*a**(4*m-3)*t**m/sp.factorial(m); rewritten=c*t*a*(t*G*a**4/4)**(m-1)/sp.factorial(m-1)
    audit.check("Q3 coefficient",G==sp.Rational(51,35),G,sp.Rational(51,35),"derivation"); audit.check("summand rewrite",sp.simplify(summand-rewritten)==0,summand,rewritten,"series"); audit.check("rate fixture",rate==sp.Rational(17,140),rate,sp.Rational(17,140),"series"); audit.check("sigma margin",margin==sp.Rational(11,140) and margin>0,margin,sp.Rational(11,140),"weight"); audit.check("prefactor",prefactor==sp.Rational(2,9),prefactor,sp.Rational(2,9),"weight")
    rows=[]; amplitude_list=[int(v) for v in manifest["fixture"]["amplitudes"]]; order=int(manifest["fixture"]["truncation_order"])
    for amplitude in amplitude_list:
        partial=sum(float((n*c*(G/4)**(n-1)*abs(amplitude)**(4*n-3)*t**n/sp.factorial(n))) for n in range(1,order+1)) if amplitude else 0.0
        bound=float(prefactor*abs(amplitude)*sp.exp(rate*abs(amplitude)**4)) if amplitude else 0.0
        audit.check(f"finite positive series a={amplitude}",partial<=bound+1e-10,partial,f"<={bound}","series")
        rows.append({"amplitude":amplitude,"partial_order":order,"partial_sum":partial,"closed_bound":bound})
    audit.check("candidate weight dominates rate", sigma>rate,sigma,f">{rate}","weight"); audit.check("conditional boundary",manifest["scope"]["not_closed"].startswith("Actual Q3"),manifest["scope"]["not_closed"],"explicit open","scope")
    passed=len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"primary","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"series_rows":rows,"derived":{"G":G,"rate":rate,"sigma":sigma,"margin":margin,"prefactor":prefactor,"truncation_order":order,"candidate_entire_weight_closed_for_prescribed_words":True,"actual_q3_word_incidence_closed":False,"analytic_domain_closed":False,"volume_uniform_history_closed":False,"exhaustion_cauchy_closed":False},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace("\\","/"),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace("\\","/"),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}
def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test:atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"PRIMARY ENTIRE-SOURCE-WEIGHT PASS {payload['passed']}/{payload['total']}"); return 0
if __name__=="__main__":raise SystemExit(main())
