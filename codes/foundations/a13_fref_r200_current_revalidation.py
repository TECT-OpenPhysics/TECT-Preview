"""Primary exact lane for the current-authority R-200 revalidation."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-r200-current-authority-revalidation-260823-manifest.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R200.lean"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()

def derive(m: dict) -> dict:
    i = m["registered_inputs"]
    h = [F(str(x)) for x in i["hessian_diagonal"]]
    a = [F(str(x)) for x in i["mobility_a"]]
    b = [F(str(x)) for x in i["mobility_b"]]
    beta = F(str(i["beta"]))
    cancel = lambda mob, mass: mob * (mass + beta**-1 * (-beta * mass))
    ra, rb = [x*y for x,y in zip(a,h)], [x*y for x,y in zip(b,h)]
    return {"hessian": [str(x) for x in h], "gibbs_covariance": [str(x**-1) for x in h],
            "mobility_a_rates": [str(x) for x in ra], "mobility_b_rates": [str(x) for x in rb],
            "stationary_current_a": [str(cancel(x,y)) for x,y in zip(a,h)],
            "stationary_current_b": [str(cancel(x,y)) for x,y in zip(b,h)],
            "same_stationary_density": all(cancel(x,y)==0 for x,y in zip(a+b,h+h)),
            "different_heat_rates": ra != rb, "root_labels": list(i["root_labels"]),
            "root_rate_pairs": {"A": dict(zip(i["root_labels"],[str(x) for x in ra])),
                                "B": dict(zip(i["root_labels"],[str(x) for x in rb]))}}

def find_lake() -> str | None:
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        p = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if p.is_file(): return str(p)
    return None

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path); ap.add_argument("--no-store", action="store_true"); args = ap.parse_args()
    m = json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[]
    def check(name, ok, actual, expected):
        rows.append({"name":name,"pass":bool(ok),"actual":str(actual),"expected":str(expected)})
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("manifest identity", m["audit_id"] == "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT", m["audit_id"], "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY-CURRENT")
    check("claim nonbearing", m["claim_bearing"] is False, m["claim_bearing"], False)
    check("no new negative", m["formal_integration"]["no_new_negative_ids"] == [], m["formal_integration"]["no_new_negative_ids"], [])
    for label,item in m["source_authorities"].items():
        p=ROOT/item["path"]; check(f"source {label}", p.is_file() and sha(p)==item["sha256"], sha(p) if p.is_file() else None, item["sha256"])
    d=derive(m)
    check("stationary currents vanish", d["same_stationary_density"], d["stationary_current_a"], ["0","0"])
    check("rates A", d["mobility_a_rates"] == ["1","1"], d["mobility_a_rates"], ["1","1"])
    check("rates B", d["mobility_b_rates"] == ["2","3"], d["mobility_b_rates"], ["2","3"])
    check("rates differ", d["different_heat_rates"], True, True)
    check("covariance unchanged", d["gibbs_covariance"] == ["1","1"], d["gibbs_covariance"], ["1","1"])
    lake=find_lake(); check("pinned lake", lake is not None, lake, "pinned lake")
    run=subprocess.run([lake,"env","lean",str(LEAN.relative_to(LEAN_ROOT))],cwd=LEAN_ROOT,text=True,encoding="utf-8",capture_output=True,check=False)
    check("Lean compile", run.returncode==0, run.returncode, 0)
    check("Lean clean", run.returncode==0 and "error:" not in (run.stdout+run.stderr).lower(), run.stderr, "no Lean error")
    payload={"schema":"tect/a13-fref-r200-current-primary/1.0","run_kind":"primary","audit_id":m["audit_id"],"exploration_id":m["exploration_id"],"claim_id":m["claim_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"derived":d,"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"boundary":m["boundary"]}
    if not args.no_store:
        out=args.output or ROOT/"claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-r200-current-authority-revalidation/primary.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")
    print(f"A13 R200 CURRENT PRIMARY PASS {len(rows)}/{len(rows)}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
