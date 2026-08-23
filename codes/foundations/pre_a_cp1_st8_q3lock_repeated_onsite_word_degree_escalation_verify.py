#!/usr/bin/env python3
"""Integrated primary, independent and Lean verifier for EXP-001031."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO=Path(__file__).resolve().parents[2]
SLUG="pre-a-cp1-st8-q3lock-repeated-onsite-word-degree-escalation"
MANIFEST=REPO/f"strategy/{SLUG}-manifest.json"
PRIMARY=REPO/"codes/foundations/pre_a_cp1_st8_q3lock_repeated_onsite_word_degree_escalation.py"
INDEPENDENT=REPO/"codes/foundations/pre_a_cp1_st8_q3lock_repeated_onsite_word_degree_escalation_independent.py"
LEAN=REPO/"verification/lean/Tect/R215.lean"
LEAN_ROOT=REPO/"verification/lean"
DEFAULT_OUTPUT=REPO/"claims/C6-SPACETIME-SIGNATURE/runs"/f"2026-08-24-primary-{SLUG}"/"integrated.json"
PYTHON=Path(os.environ.get("TECT_PYTHON",sys.executable))
def sha256(path:Path)->str:return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            json.dump(payload,stream,indent=2,sort_keys=True,ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def child(script:Path,output:Path)->tuple[subprocess.CompletedProcess[str],dict[str,Any]]:
    proc=subprocess.run([str(PYTHON),"-X","utf8",str(script),"--output",str(output)],cwd=REPO,text=True,encoding="utf-8",capture_output=True,check=False); return proc,json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
def lake_path()->Path|None:
    registry=json.loads((REPO/"verification/lean/registry.json").read_text(encoding="utf-8")); encoded=registry["toolchain"]["toolchain"].replace("/","--").replace(":","---"); candidate=Path.home()/".elan"/"toolchains"/encoded/"bin"
    for name in ("lake.exe","lake"):
        if (candidate/name).is_file():return candidate/name
    found=shutil.which("lake"); return Path(found) if found else None
def lean_run()->dict[str,Any]:
    lake=lake_path()
    if lake is None:return {"status":"UNAVAILABLE","command":"lake env lean Tect/R215.lean","output":"pinned lake executable not found"}
    proc=subprocess.run([str(lake),"env","lean","Tect/R215.lean"],cwd=LEAN_ROOT,text=True,encoding="utf-8",capture_output=True,check=False); output=(proc.stdout+"\n"+proc.stderr).strip(); return {"status":"PASS" if proc.returncode==0 and "error:" not in output.lower() else "FAIL","command":"lake env lean Tect/R215.lean","returncode":proc.returncode,"output":output[-2000:]}
def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--no-store",action="store_true"); parser.add_argument("--skip-lean",action="store_true"); args=parser.parse_args(); manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[]
    def check(name:str,ok:bool,actual:Any,expected:Any)->None:
        rows.append({"name":name,"pass":bool(ok),"actual":actual,"expected":expected})
        if not ok:raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    check("identity",manifest["exploration_id"]=="EXP-001031" and manifest["task_id"]=="T-054",[manifest["exploration_id"],manifest["task_id"]],"EXP-001031/T-054")
    check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False)
    check("degree formula",manifest["model"]["exact_degree"]=="deg_a R_m=4m-3 for m>=1",manifest["model"]["exact_degree"],"4m-3")
    check("word scope",manifest["model"]["interpretation"].startswith("coefficient-level prescribed-word"),manifest["model"]["interpretation"],"explicit prescribed-word scope")
    source=LEAN.read_text(encoding="utf-8"); markers=["q3_coefficient_fixture","repeated_word_degree_m2","repeated_word_degree_m3","repeated_word_coefficient_m3","fixed_weight_gap_m3"]; check("Lean source",LEAN.is_file() and all(m in source for m in markers),markers,"present"); check("Lean forbidden",not any(t in source.split() for t in ("sorry","admit","axiom","unsafe")),[],"none")
    with tempfile.TemporaryDirectory(prefix="repeated-onsite-word-") as temp:
        pp,primary=child(PRIMARY,Path(temp)/"primary.json"); ip,independent=child(INDEPENDENT,Path(temp)/"independent.json"); check("primary child",pp.returncode==0 and primary.get("verdict")=="PASS",pp.stdout+pp.stderr,"PASS"); check("independent child",ip.returncode==0 and independent.get("verdict")=="PASS",ip.stdout+ip.stderr,"PASS"); check("positive totals",primary.get("total",0)>0 and independent.get("total",0)>0,[primary.get("total"),independent.get("total")],">0")
        for key in ("G","weight_degree","word_lengths","degree_formula","m2_degree","m3_degree","fixed_polynomial_weight_closed_for_all_words","actual_q3_word_incidence_closed","cancellation_closed","entire_analytic_route_open"):
            check(f"lane agreement {key}",primary.get("derived",{}).get(key)==independent.get("derived",{}).get(key),[primary.get("derived",{}).get(key),independent.get("derived",{}).get(key)],"equal")
        check("m3 degree gap",primary.get("derived",{}).get("m3_degree")==9,primary.get("derived",{}),9); check("fixed polynomial route rejected",primary.get("derived",{}).get("fixed_polynomial_weight_closed_for_all_words") is False,primary.get("derived",{}),False)
    lean={"status":"SKIPPED","command":"lake env lean Tect/R215.lean"} if args.skip_lean else lean_run(); check("Lean compile",args.skip_lean or lean["status"]=="PASS",lean,"PASS")
    payload={"schema":"tect/foundation-audit/1.0","run_kind":"integrated","audit_id":"PA-CP1-ST8-Q3LOCK-REPEATED-ONSITE-WORD-DEGREE-ESCALATION","claim_id":manifest["claim_ids"][0],"task_id":manifest["task_id"],"exploration_id":manifest["exploration_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"lean":lean,"boundary":manifest["scope"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"provenance":{"primary_sha256":sha256(PRIMARY),"independent_sha256":sha256(INDEPENDENT),"manifest_sha256":sha256(MANIFEST),"lean_sha256":sha256(LEAN)}}
    if not args.no_store:atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INTEGRATED REPEATED-ONSITE-WORD-DEGREE PASS {len(rows)}/{len(rows)}; Lean={lean['status']}"); return 0
if __name__=="__main__":raise SystemExit(main())
