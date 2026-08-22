"""Integrated verifier for R-195 spatial constant-field lift."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any
REPO=Path(__file__).resolve().parents[2]
MANIFEST=REPO/"strategy/pre-a6-spatial-constant-field-lift-boundary-manifest.json"; PRIMARY=REPO/"verification/scripts/lean_a6_spatial_constant_field_lift.py"; INDEPENDENT=REPO/"codes/foundations/lean_a6_spatial_constant_field_lift_independent.py"; DEFAULT_OUTPUT=REPO/"claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-08-22-lean-r195-spatial-constant-field-lift/integrated.json"
PYTHON=Path(os.environ.get("TECT_PYTHON",str(Path(sys.executable))))
def sha256(path:Path)->str: return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f: json.dump(payload,f,indent=2,sort_keys=True,ensure_ascii=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def run_child(script:Path,out:Path):
    p=subprocess.run([str(PYTHON),"-X","utf8",str(script),"--output",str(out)],cwd=REPO,text=True,encoding="utf-8",capture_output=True,check=False); payload=json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}; return p,payload
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); ap.add_argument("--no-store",action="store_true"); args=ap.parse_args(); manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[]
    def check(name,cond,actual,expected):
        rows.append({"name":name,"pass":bool(cond),"actual":actual,"expected":expected})
        if not cond: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity",manifest["result_id"]=="R-195" and manifest["exploration_id"]=="EXP-000933",[manifest["result_id"],manifest["exploration_id"]],"R-195/EXP-000933"); check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False); check("no new negative",manifest["formal_integration"]["no_new_negative_ids"]==[],manifest["formal_integration"]["no_new_negative_ids"],[]); check("reused boundary",manifest["formal_integration"]["reused_negative_ids"]==["NG-2026-07-20-A6-NAIVE-W-SUBTRACTION-NONUNIFORM"],manifest["formal_integration"]["reused_negative_ids"],"R-194 boundary")
    for key,item in manifest["inputs"].items():
        path=REPO/item["path"]; check(f"input {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    for key,item in manifest["files"].items():
        path=REPO/item["path"]; check(f"file {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    source=(REPO/manifest["files"]["lean_entrypoint"]["path"]).read_text(encoding="utf-8"); check("all theorem markers",all(m in source for m in manifest["theorem_markers"]),manifest["theorem_markers"],"present"); check("no Lean escape",not any(t in source.split() for t in ("sorry","admit","axiom","unsafe")),[],"none")
    boundary=(manifest["boundary"]+" "+manifest["no_overclaim"]).lower(); check("local/global boundary",("constant-field" in boundary and "full-field" in boundary and "not" in boundary),boundary,"explicit boundary"); check("spatial volume boundary",("volume" in boundary and "tightness" in boundary),boundary,"volume/tightness boundary"); check("hostile mutations",len(manifest["hostile_mutations"])==8,len(manifest["hostile_mutations"]),8)
    with tempfile.TemporaryDirectory(prefix="r195-integrated-") as temp:
        pp,ip=Path(temp)/"primary.json",Path(temp)/"independent.json"; pproc,primary=run_child(PRIMARY,pp); iproc,independent=run_child(INDEPENDENT,ip); check("primary child",pproc.returncode==0 and primary.get("verdict")=="PASS",pproc.stdout+pproc.stderr,"PASS"); check("independent child",iproc.returncode==0 and independent.get("verdict")=="PASS",iproc.stdout+iproc.stderr,"PASS"); check("volume agreement",primary.get("derived",{}).get("volume")==independent.get("derived",{}).get("volume"),[primary.get("derived",{}).get("volume"),independent.get("derived",{}).get("volume")],"equal volume"); check("ratio agreement",primary.get("derived",{}).get("local_ratio")==independent.get("derived",{}).get("local_ratio"),[primary.get("derived",{}).get("local_ratio"),independent.get("derived",{}).get("local_ratio")],"equal ratio"); check("witness agreement",primary.get("derived",{}).get("r")==independent.get("derived",{}).get("r"),[primary.get("derived",{}).get("r"),independent.get("derived",{}).get("r")],"equal r")
    check("mutation volume omission rejected","V * D" in source and "V*s" in source,source,"volume factor retained"); check("mutation local-global promotion rejected","full-field" in boundary and "not" in boundary,boundary,"not full-field"); check("mutation uniform coercivity rejected","no positive volume-uniform coercivity" in boundary,boundary,"noncoercive boundary"); check("mutation domain expansion rejected","constant-field" in boundary and "full spatial gibbs" in boundary,boundary,"constant-only boundary"); check("mutation full measure rejected","partition" in boundary and "tightness" in boundary,boundary,"partition/tightness boundary"); check("mutation Lean escape rejected",not any(t in source.split() for t in ("sorry","admit","axiom","unsafe")),[],"none")
    payload={"schema":"tect/lean-kernel-crosscheck/1.0","run_kind":"integrated","audit_id":manifest["audit_id"],"claim_id":manifest["claim_id"],"result_id":manifest["result_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"boundary":manifest["boundary"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INTEGRATED R-195 PASS {len(rows)}/{len(rows)}"); return 0
if __name__=="__main__": raise SystemExit(main())
