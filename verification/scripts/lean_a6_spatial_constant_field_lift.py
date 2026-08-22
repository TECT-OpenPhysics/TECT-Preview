"""Primary Lean/Fraction audit for the R-195 spatial constant-field lift."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any
REPO=Path(__file__).resolve().parents[2]
MANIFEST=REPO/"strategy/pre-a6-spatial-constant-field-lift-boundary-manifest.json"
LEAN_ROOT=REPO/"verification/lean"; LEAN_ENTRYPOINT=LEAN_ROOT/"Tect/R195.lean"; TOOLCHAIN=LEAN_ROOT/"lean-toolchain"
DEFAULT_OUTPUT=REPO/"claims/A6-CLASSII-K-COMPOSITE-DEFINITION/runs/2026-08-22-lean-r195-spatial-constant-field-lift/primary.json"
def sha256(path:Path)->str: return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def serial(value:Any)->Any:
    if isinstance(value,F): return str(value)
    if isinstance(value,dict): return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value
def atomic_json(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f: json.dump(serial(payload),f,indent=2,sort_keys=True,ensure_ascii=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def pinned_lean()->Path|None:
    encoded=TOOLCHAIN.read_text(encoding="utf-8").strip().replace("/","--").replace(":","---")
    p=Path.home()/".elan"/"toolchains"/encoded/"bin"/("lean.exe" if os.name=="nt" else "lean")
    return p if p.is_file() else None
def compile_lean()->subprocess.CompletedProcess[str]:
    lean=pinned_lean()
    if lean is None: return subprocess.CompletedProcess([],1,"","pinned lean executable missing")
    search=[LEAN_ROOT/".lake/build/lib/lean"]; packages=LEAN_ROOT/".lake/packages"
    if packages.is_dir(): search.extend(p/".lake/build/lib/lean" for p in packages.iterdir() if (p/".lake/build/lib/lean").is_dir())
    env=os.environ.copy(); env["LEAN_PATH"]=os.pathsep.join(str(p) for p in search if p.is_dir())
    return subprocess.run([str(lean),str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))],cwd=LEAN_ROOT,text=True,encoding="utf-8",capture_output=True,check=False,env=env)
def coeffs(a1):
    p=a1["parameters"]; q=lambda k:F(str(p[k])); den=q("M_X")**2+q("classii_mass_regularizer")
    return q("cJJ")*q("alpha_X")**2/den,q("cJK")*q("alpha_X")*q("beta_X")/den,q("cKK")*q("beta_X")**2/den,q("rho_regularizer")
def D(a,b,c,eps,h,s,r):
    rho=s+r; return h*s-(9*(a+2*b+c)*s-6*b*s*s/(rho+eps)-3*c*s*s*(rho+2*eps)/(rho+eps)**2)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); ap.add_argument("--no-store",action="store_true"); args=ap.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); a1=json.loads((REPO/manifest["inputs"]["a1_production"]["path"]).read_text(encoding="utf-8")); oracle=manifest["registered_inputs"]["test_oracles"]; rows=[]
    def check(name,cond,actual,expected):
        rows.append({"name":name,"pass":bool(cond),"actual":serial(actual),"expected":serial(expected)})
        if not cond: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity",manifest["audit_id"]=="A6-R195-SPATIAL-CONSTANT-FIELD-LIFT-BOUNDARY" and manifest["result_id"]=="R-195",[manifest["audit_id"],manifest["result_id"]],"R-195 identity")
    check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False); check("no new negative",manifest["formal_integration"]["no_new_negative_ids"]==[],manifest["formal_integration"]["no_new_negative_ids"],[]); check("no PDF",manifest["formal_integration"]["no_pdf"] is True,manifest["formal_integration"]["no_pdf"],True)
    for key,item in manifest["inputs"].items():
        path=REPO/item["path"]; check(f"input {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    for key,item in manifest["files"].items():
        path=REPO/item["path"]; check(f"file {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    source=LEAN_ENTRYPOINT.read_text(encoding="utf-8"); check("Lean markers",all(m in source for m in manifest["theorem_markers"]),manifest["theorem_markers"],"all present"); check("Lean escape absence",not any(t in source.split() for t in ("sorry","admit","axiom","unsafe")),[],"none")
    cp=compile_lean(); check("Lean compile",cp.returncode==0,cp.returncode,0); check("Lean clean",cp.returncode==0 and "error:" not in (cp.stdout+cp.stderr).lower(),cp.stderr,"no Lean error")
    a,b,c,eps=coeffs(a1); h=9*(a+2*b+c); V=F(str(a1["parameters"]["Lx"]))*F(str(a1["parameters"]["Ly"]))*F(str(a1["parameters"]["Lz"])); s=F(oracle["s"]); kappa=F(oracle["kappa"]); r=s+2*eps+6*s*(b+c)/kappa+F(oracle["strict_margin"]); local=D(a,b,c,eps,h,s,r); integrated=V*local
    check("volume positive",V>0,V,">0"); check("constant field variables",s>0 and r>0,[s,r],"s,r positive"); check("h_min endpoint",h==9*(a+2*b+c),h,"9*(a+2*b+c)"); check("integrated volume identity",integrated==V*local,[integrated,V*local],"exact V scaling"); check("ratio volume cancellation",integrated/(V*s)==local/s,integrated/(V*s),local/s); check("large-r condition",s+2*eps<=r,[s+2*eps,r],"r >= s+2 eps"); bound=6*s*(b+c)/r; check("explicit ratio bound",local/s<=bound,[local/s,bound],"ratio <= bound"); check("uniform-kappa witness",local/s<kappa,[local/s,kappa],"ratio < kappa")
    payload={"schema":"tect/lean-kernel-crosscheck/1.0","run_kind":"primary","audit_id":manifest["audit_id"],"claim_id":manifest["claim_id"],"result_id":manifest["result_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"derived":serial({"a":a,"b":b,"c":c,"eps":eps,"h_min":h,"volume":V,"s":s,"r":r,"kappa":kappa,"local_ratio":local/s,"integrated_ratio":integrated/(V*s),"bound":bound}),"toolchain":TOOLCHAIN.read_text(encoding="utf-8").strip(),"lean_stdout":cp.stdout,"lean_stderr":cp.stderr,"boundary":manifest["boundary"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"PRIMARY R-195 LEAN PASS {len(rows)}/{len(rows)} volume={V} ratio={local/s}"); return 0
if __name__=="__main__": raise SystemExit(main())
