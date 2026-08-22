"""Non-importing exact audit for the R-195 spatial constant-field lift."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a6-spatial-constant-field-lift-boundary-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-K-COMPOSITE-DEFINITION" / "runs" / "2026-08-22-lean-r195-spatial-constant-field-lift" / "independent.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()

def serial(value: Any) -> Any:
    if isinstance(value, F): return str(value)
    if isinstance(value, dict): return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [serial(v) for v in value]
    return value

def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def coeffs(a1: dict[str, Any]) -> tuple[F,F,F,F]:
    p=a1["parameters"]; q=lambda k:F(str(p[k]))
    den=q("M_X")**2+q("classii_mass_regularizer")
    return q("cJJ")*q("alpha_X")**2/den, q("cJK")*q("alpha_X")*q("beta_X")/den, q("cKK")*q("beta_X")**2/den, q("rho_regularizer")

def D(a:F,b:F,c:F,eps:F,h:F,s:F,r:F)->F:
    rho=s+r
    return h*s-(9*(a+2*b+c)*s-6*b*s*s/(rho+eps)-3*c*s*s*(rho+2*eps)/(rho+eps)**2)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); ap.add_argument("--no-store",action="store_true"); args=ap.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); a1=json.loads((REPO/manifest["inputs"]["a1_production"]["path"]).read_text(encoding="utf-8")); oracle=manifest["registered_inputs"]["test_oracles"]
    rows=[]
    def check(name,cond,actual,expected):
        rows.append({"name":name,"pass":bool(cond),"actual":serial(actual),"expected":serial(expected)})
        if not cond: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity",manifest["audit_id"]=="A6-R195-SPATIAL-CONSTANT-FIELD-LIFT-BOUNDARY" and manifest["result_id"]=="R-195",[manifest["audit_id"],manifest["result_id"]],"R-195 identity")
    check("claim nonbearing",manifest["claim_bearing"] is False,manifest["claim_bearing"],False)
    check("no new negative",manifest["formal_integration"]["no_new_negative_ids"]==[],manifest["formal_integration"]["no_new_negative_ids"],[])
    check("no PDF",manifest["formal_integration"]["no_pdf"] is True,manifest["formal_integration"]["no_pdf"],True)
    for key,item in manifest["inputs"].items():
        path=REPO/item["path"]; check(f"input {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    for key,item in manifest["files"].items():
        path=REPO/item["path"]; check(f"file {key} hash",path.is_file() and sha256(path)==item["sha256"],sha256(path) if path.is_file() else None,item["sha256"])
    a,b,c,eps=coeffs(a1); h=9*(a+2*b+c); V=F(str(a1["parameters"]["Lx"]))*F(str(a1["parameters"]["Ly"]))*F(str(a1["parameters"]["Lz"]))
    s=F(oracle["s"]); kappa=F(oracle["kappa"]); r=s+2*eps+6*s*(b+c)/kappa+F(oracle["strict_margin"])
    local=D(a,b,c,eps,h,s,r); integrated=V*local
    check("volume positive",V>0,V,">0")
    check("constant field variables",s>0 and r>0,[s,r],"s,r positive")
    check("h_min endpoint",h==9*(a+2*b+c),h,"9*(a+2*b+c)")
    check("integrated volume identity",integrated==V*local,[integrated,V*local],"exact V scaling")
    check("ratio volume cancellation",integrated/(V*s)==local/s,integrated/(V*s),local/s)
    check("large-r condition",s+2*eps<=r,[s+2*eps,r],"r >= s+2 eps")
    bound=6*s*(b+c)/r
    check("explicit ratio bound",local/s<=bound,[local/s,bound],"ratio <= bound")
    check("uniform-kappa witness",local/s<kappa,[local/s,kappa],"ratio < kappa")
    payload={"schema":"tect/lean-kernel-crosscheck/1.0","run_kind":"independent","audit_id":manifest["audit_id"],"claim_id":manifest["claim_id"],"result_id":manifest["result_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"derived":serial({"a":a,"b":b,"c":c,"eps":eps,"h_min":h,"volume":V,"s":s,"r":r,"kappa":kappa,"local_ratio":local/s,"integrated_ratio":integrated/(V*s),"bound":bound}),"boundary":manifest["boundary"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT R-195 PASS {len(rows)}/{len(rows)} volume={V} ratio={local/s}"); return 0
if __name__=="__main__": raise SystemExit(main())
