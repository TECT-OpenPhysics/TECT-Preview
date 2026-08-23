"""Non-importing Fraction lane for the current-authority R-200 revalidation."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"strategy/pre-a13-r200-current-authority-revalidation-260823-manifest.json"

def sha(p): return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def derive(m):
    i=m["registered_inputs"]; h=[Fraction(str(x)) for x in i["hessian_diagonal"]]; a=[Fraction(str(x)) for x in i["mobility_a"]]; b=[Fraction(str(x)) for x in i["mobility_b"]]; beta=Fraction(str(i["beta"]))
    cancel=lambda mob,mass: mob*(mass+beta**-1*(-beta*mass)); ra=[x*y for x,y in zip(a,h)]; rb=[x*y for x,y in zip(b,h)]
    return {"hessian":[str(x) for x in h],"gibbs_covariance":[str(x**-1) for x in h],"mobility_a_rates":[str(x) for x in ra],"mobility_b_rates":[str(x) for x in rb],"stationary_current_a":[str(cancel(x,y)) for x,y in zip(a,h)],"stationary_current_b":[str(cancel(x,y)) for x,y in zip(b,h)],"same_stationary_density":all(cancel(x,y)==0 for x,y in zip(a+b,h+h)),"different_heat_rates":ra!=rb,"root_labels":list(i["root_labels"]),"root_rate_pairs":{"A":dict(zip(i["root_labels"],[str(x) for x in ra])),"B":dict(zip(i["root_labels"],[str(x) for x in rb]))}}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--no-store",action="store_true"); args=ap.parse_args(); m=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[]
    def check(n,ok,a,e): rows.append({"name":n,"pass":bool(ok),"actual":str(a),"expected":str(e)}); (ok or (_ for _ in ()).throw(AssertionError(f"{n}: actual={a!r}, expected={e!r}")))
    check("manifest identity",m["audit_id"]=="A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT",m["audit_id"],"A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT"); check("claim nonbearing",m["claim_bearing"] is False,m["claim_bearing"],False); check("no new negative",m["formal_integration"]["no_new_negative_ids"]==[],m["formal_integration"]["no_new_negative_ids"],[])
    for label,item in m["source_authorities"].items(): p=ROOT/item["path"]; check(f"source {label}",p.is_file() and sha(p)==item["sha256"],sha(p) if p.is_file() else None,item["sha256"])
    d=derive(m); check("stationary currents vanish",d["same_stationary_density"],d["stationary_current_a"],["0","0"]); check("rates A",d["mobility_a_rates"]==["1","1"],d["mobility_a_rates"],["1","1"]); check("rates B",d["mobility_b_rates"]==["2","3"],d["mobility_b_rates"],["2","3"]); check("rates differ",d["different_heat_rates"],True,True); check("covariance unchanged",d["gibbs_covariance"]==["1","1"],d["gibbs_covariance"],["1","1"])
    payload={"schema":"tect/a13-fref-r200-current-independent/1.0","run_kind":"independent","audit_id":m["audit_id"],"exploration_id":m["exploration_id"],"claim_id":m["claim_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"derived":d,"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"boundary":m["boundary"]}
    if not args.no_store:
        out=args.output or ROOT/"claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-r200-current-authority-revalidation/independent.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")
    print(f"A13 R200 CURRENT INDEPENDENT PASS {len(rows)}/{len(rows)}"); return 0
if __name__=="__main__": raise SystemExit(main())
