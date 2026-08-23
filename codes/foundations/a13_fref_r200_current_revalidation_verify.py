"""Integrated verifier for the append-only current R-200 revalidation."""
from __future__ import annotations
import argparse, ast, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"strategy/pre-a13-r200-current-authority-revalidation-260823-manifest.json"
PRIMARY=ROOT/"codes/foundations/a13_fref_r200_current_revalidation.py"; INDEPENDENT=ROOT/"codes/foundations/a13_fref_r200_current_revalidation_independent.py"
def sha(p): return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--no-store",action="store_true"); args=ap.parse_args(); m=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[]
    def check(n,ok,a,e): rows.append({"name":n,"pass":bool(ok),"actual":str(a),"expected":str(e)}); (ok or (_ for _ in ()).throw(AssertionError(f"{n}: actual={a!r}, expected={e!r}")))
    check("manifest identity",m["audit_id"]=="A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT",m["audit_id"],"A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT"); check("claim nonbearing",m["claim_bearing"] is False,m["claim_bearing"],False); check("no PDF",m["formal_integration"]["no_pdf"] is True,m["formal_integration"]["no_pdf"],True); check("no new negative",m["formal_integration"]["no_new_negative_ids"]==[],m["formal_integration"]["no_new_negative_ids"],[])
    for label,item in m["source_authorities"].items(): p=ROOT/item["path"]; check(f"source {label}",p.is_file() and sha(p)==item["sha256"],sha(p) if p.is_file() else None,item["sha256"])
    for label,item in m["files"].items():
        p=ROOT/item["path"]
        check(f"file {label}",p.is_file() and sha(p)==item["sha256"],sha(p) if p.is_file() else None,item["sha256"])
    cert=ROOT/m["files"]["certificate"]["path"]; check("certificate boundary",all(x in cert.read_text(encoding="utf-8") for x in ("same stationary density","different heat rates","R-192","A13/T-050","No PDF")),True,True)
    for path in (PRIMARY,INDEPENDENT):
        tree=ast.parse(path.read_text(encoding="utf-8")); names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): names += [a.name.split(".")[0] for a in node.names]
            elif isinstance(node,ast.ImportFrom): names.append((node.module or "__future__").split(".")[0])
        check(f"stdlib {path.name}",all(x in sys.stdlib_module_names for x in names),names,"stdlib only"); check(f"no lane import {path.name}",not any(x.startswith("a13_fref_r200_current_revalidation") for x in names),names,"no lane imports")
    with tempfile.TemporaryDirectory(prefix="r200-current-") as td:
        po=Path(td)/"primary.json"; io=Path(td)/"independent.json"; p=subprocess.run([sys.executable,"-B",str(PRIMARY),"--output",str(po)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",check=False); i=subprocess.run([sys.executable,"-B",str(INDEPENDENT),"--output",str(io)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",check=False); check("primary exit",p.returncode==0,p.returncode,0); check("independent exit",i.returncode==0,i.returncode,0); pp=json.loads(po.read_text(encoding="utf-8")); ip=json.loads(io.read_text(encoding="utf-8")); check("derived agreement",pp["derived"]==ip["derived"],pp["derived"],ip["derived"]); check("child PASS",pp["verdict"]=="PASS" and ip["verdict"]=="PASS",[pp["verdict"],ip["verdict"]],["PASS","PASS"]); d=pp["derived"]
    check("same stationary density",d["same_stationary_density"] is True,d["same_stationary_density"],True); check("different heat rates",d["different_heat_rates"] is True,d["different_heat_rates"],True); check("current pin",m["source_authorities"]["r193_current_manifest"]["sha256"]=="ae48ade9d11e3f47955ef4837e26d6cf106d2427570fe886c2eb33b0607d6b43",m["source_authorities"]["r193_current_manifest"]["sha256"],"ae48ade9d11e3f47955ef4837e26d6cf106d2427570fe886c2eb33b0607d6b43")
    payload={"schema":"tect/a13-fref-r200-current-integrated/1.0","run_kind":"integrated","audit_id":m["audit_id"],"exploration_id":m["exploration_id"],"claim_id":m["claim_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"derived":d,"primary_stdout":p.stdout[-500:],"independent_stdout":i.stdout[-500:],"boundary":m["boundary"]}
    if not args.no_store:
        out=args.output or ROOT/"claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-r200-current-authority-revalidation/integrated.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")
    print(f"A13 R200 CURRENT INTEGRATED PASS {len(rows)}/{len(rows)}"); return 0
if __name__=="__main__": raise SystemExit(main())
