#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001169."""

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
SLUG="pre-a-cp1-st8-q3lock-extended-direct-d-delta-d-shape-beta"
MANIFEST=REPO/f"strategy/{SLUG}-manifest.json"
PRIMARY=REPO/f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT=REPO/f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
LEAN=REPO/"verification/lean/Tect/R267.lean"; LEAN_ROOT=REPO/"verification/lean"
DEFAULT_OUTPUT=REPO/"claims/C6-SPACETIME-SIGNATURE/runs"/f"2026-08-26-integrated-{SLUG}"/"integrated.json"
PYTHON=Path(os.environ.get("TECT_PYTHON",sys.executable))

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def store(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f: json.dump(payload,f,indent=2,sort_keys=True,ensure_ascii=True,default=float); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def lake()->Path|None:
    reg=json.loads((REPO/"verification/lean/registry.json").read_text(encoding="utf-8")); enc=reg["toolchain"]["toolchain"].replace("/","--").replace(":","---"); base=Path.home()/".elan"/"toolchains"/enc/"bin"
    for n in ("lake.exe","lake"):
        if (base/n).is_file():return base/n
    found=shutil.which("lake");return Path(found) if found else None
def child(script:Path,out:Path)->tuple[subprocess.CompletedProcess[str],dict[str,Any]]:
    proc=subprocess.run([str(PYTHON),"-X","utf8",str(script),"--output",str(out)],cwd=REPO,text=True,encoding="utf-8",capture_output=True,check=False); return proc,json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
def lean_run()->dict[str,Any]:
    executable=lake(); command="lake env lean Tect/R267.lean"
    if executable is None:return {"status":"UNAVAILABLE","command":command,"output":"pinned lake executable not found"}
    p=subprocess.run([str(executable),"env","lean","Tect/R267.lean"],cwd=LEAN_ROOT,text=True,encoding="utf-8",capture_output=True,check=False); out=(p.stdout+"\n"+p.stderr).strip(); return {"status":"PASS" if p.returncode==0 and "error:" not in out.lower() else "FAIL","command":command,"returncode":p.returncode,"output":out[-2000:]}
def flatten(payload:dict[str,Any])->dict[tuple[Any,...],dict[str,float]]:
    rows={}
    for volume in payload.get("derived",{}).get("volume_rows",[]):
        for radius in volume.get("radius_rows",[]):
            for beta in radius.get("beta_rows",[]):
                for time in beta.get("times",[]):
                    for sign,values in time["orientations"].items(): rows[(volume["volume"],radius["radius"],beta["beta"],time["time"],sign)] = values
    return rows
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT);ap.add_argument("--no-store",action="store_true");args=ap.parse_args();m=json.loads(MANIFEST.read_text(encoding="utf-8"));scope=m["scope"];checks=[]
    def check(name:str,ok:bool,actual:Any,expected:Any)->None:
        checks.append({"name":name,"pass":bool(ok),"actual":actual,"expected":expected});
        if not ok:raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity",m["exploration_id"]=="EXP-001169" and m["task_id"]=="T-054",[m["exploration_id"],m["task_id"]],"EXP-001169/T-054");check("claim nonbearing",m["claim_bearing"] is False,m["claim_bearing"],False);check("scope firewall",scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["beta_uniform_direct_d_cauchy_closed"],scope,"finite diagnostic only")
    source=LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""; markers=["direct_fixture","modular_fixture","zero_tail_fixture","orientation_fixture","scope_fixture"];check("Lean source",LEAN.is_file() and all(x in source for x in markers),markers,"present");check("Lean forbidden",not any(x in source.split() for x in ("sorry","admit","axiom","unsafe")),[],"none")
    with tempfile.TemporaryDirectory(prefix="extended-direct-d-delta-d-") as tmp:
        pp,primary=child(PRIMARY,Path(tmp)/"primary.json");ip,independent=child(INDEPENDENT,Path(tmp)/"independent.json");check("primary child",pp.returncode==0 and primary.get("verdict")=="PASS",pp.stdout+pp.stderr,"PASS");check("independent child",ip.returncode==0 and independent.get("verdict")=="PASS",ip.stdout+ip.stderr,"PASS")
        pr,ir=flatten(primary),flatten(independent);check("row count",len(pr)==len(ir)>0,[len(pr),len(ir)],">0 and equal"); tol=float(m["finite_fixture"]["agreement_tolerance"])
        for key in pr:
            check(f"row {key} context",key in ir,key,"independent context");
            for field in ("D_norm","delta_D_norm","matrix_norm"): check(f"row {key} {field}",abs(float(pr[key][field])-float(ir[key][field]))<=tol*(1+abs(float(pr[key][field]))),[pr[key][field],ir[key][field]],"within relative tolerance")
        for flag in ("finite_direct_D_closed","finite_direct_delta_D_closed","finite_two_orientation_difference_closed","cutoff_zero_tail_fixture_closed","path_exhaustion_fixture_closed","beta_grid_fixture_closed","volume_uniform_direct_d_cauchy_closed","beta_uniform_direct_d_cauchy_closed","delta_d_cauchy_closed","product_core_density_closed","exhaustion_independence_closed","group_law_closed","common_alpha_closed","hamiltonian_os_identification_closed","kms_gns_gap_closed","continuum_closed","c6_closed","sector_a_closed","pre_a_closed","no_new_negative_result","no_tier_change","no_pdf"):check(f"lane agreement {flag}",primary.get("derived",{}).get(flag)==independent.get("derived",{}).get(flag),[primary.get("derived",{}).get(flag),independent.get("derived",{}).get(flag)],"equal")
    lean=lean_run();check("Lean compile",lean["status"]=="PASS",lean,"PASS");payload={"schema":"tect/foundation-audit/1.0","run_kind":"integrated","audit_id":"PA-CP1-ST8-Q3LOCK-EXTENDED-DIRECT-D-DELTA-D-SHAPE-BETA","claim_id":m["claim_ids"][0],"task_id":m["task_id"],"exploration_id":m["exploration_id"],"verdict":"PASS","assertion_count":len(checks),"assertions":checks,"lean":lean,"boundary":scope,"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"provenance":{"primary_sha256":sha(PRIMARY),"independent_sha256":sha(INDEPENDENT),"manifest_sha256":sha(MANIFEST),"lean_sha256":sha(LEAN)}}
    if not args.no_store:store(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INTEGRATED EXTENDED-DIRECT-D-DELTA-D PASS {len(checks)}/{len(checks)}; Lean={lean['status']}");return 0
if __name__=="__main__":raise SystemExit(main())
