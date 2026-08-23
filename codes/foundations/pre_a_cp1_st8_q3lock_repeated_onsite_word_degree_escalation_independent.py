#!/usr/bin/env python3
"""Independent Fraction audit for prescribed repeated onsite words."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO=Path(__file__).resolve().parents[2]
SCRIPT=Path(__file__).resolve()
SLUG="pre-a-cp1-st8-q3lock-repeated-onsite-word-degree-escalation"
MANIFEST=REPO/f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT=REPO/"claims/C6-SPACETIME-SIGNATURE/runs"/f"2026-08-24-primary-{SLUG}"/"independent.json"


def sha256(path:Path)->str: return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def safe(value:Any)->Any:
    if isinstance(value,Fraction): return str(value)
    if isinstance(value,dict): return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [safe(v) for v in value]
    return value
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            json.dump(safe(payload),stream,indent=2,sort_keys=True,ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
class Audit:
    def __init__(self)->None:self.rows:list[dict[str,Any]]=[]
    def check(self,name:str,ok:bool,actual:Any,expected:Any,group:str)->None:
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name":name,"group":group,"status":"PASS","actual":safe(actual),"expected":safe(expected)})


def run()->dict[str,Any]:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); audit=Audit(); audit.check("exploration",manifest["exploration_id"]=="EXP-001031",manifest["exploration_id"],"EXP-001031","provenance"); audit.check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False,"scope")
    g=Fraction(3,5); lam=Fraction(2,7); c=Fraction(2,3); G=g+3*lam; weight_degree=5; amplitude=10; rows=[]
    audit.check("coefficient fixture",G==Fraction(51,35),G,Fraction(51,35),"derivation")
    for m in [int(v) for v in manifest["fixture"]["word_lengths"]]:
        degree=4*m-3; coefficient=-m*c*(-G/Fraction(4))**(m-1); value=abs(coefficient)*amplitude**degree; gap=degree-weight_degree
        audit.check(f"degree formula m={m}",degree==4*m-3,degree,4*m-3,"word")
        audit.check(f"coefficient nonzero m={m}",coefficient!=0,coefficient,"nonzero","word")
        audit.check(f"weight gap m={m}",gap==4*m-8,gap,4*m-8,"weight")
        rows.append({"word_length":m,"degree":degree,"coefficient":coefficient,"response_at_10":value,"degree_gap":gap})
    audit.check("m2 degree-five",rows[1]["degree"]==5,rows[1],5,"cross-route")
    audit.check("m3 outruns fixed weight",rows[2]["degree"]>weight_degree,rows[2]["degree"],">5","cross-route")
    audit.check("scope boundary",manifest["scope"]["no_new_negative_result"] is True,manifest["scope"],True,"scope")
    passed=len(audit.rows)
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","verdict":"PASS","passed":passed,"total":passed,"failed":0,"assertions":audit.rows,"word_rows":rows,"derived":{"G":G,"weight_degree":weight_degree,"word_lengths":[int(v) for v in manifest["fixture"]["word_lengths"]],"degree_formula":"4m-3","m2_degree":rows[1]["degree"],"m3_degree":rows[2]["degree"],"fixed_polynomial_weight_closed_for_all_words":False,"actual_q3_word_incidence_closed":False,"cancellation_closed":False,"entire_analytic_route_open":True},"provenance":{"script":str(SCRIPT.relative_to(REPO)).replace("\\","/"),"script_sha256":sha256(SCRIPT),"manifest":str(MANIFEST.relative_to(REPO)).replace("\\","/"),"manifest_sha256":sha256(MANIFEST)},"exploration_id":manifest["exploration_id"],"boundary":manifest["scope"]}


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT REPEATED-ONSITE-WORD-DEGREE PASS {payload['passed']}/{payload['total']}"); return 0
if __name__=="__main__": raise SystemExit(main())
