"""Reproduce PAH-OMC-016 analytic-bound audits and the pinned Lean bridge.

The universal measure and boundary arguments are in the analytic certificate.
This executable audits their source polynomial, constants and formal algebra,
not a numerical surrogate for all-volume quantifiers. --check replays into a
temporary directory and compares every stored JSON without modifying it.
"""
from __future__ import annotations
import argparse
import concurrent.futures
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

__version__="1.0.0"
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
RUN=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc016-uniform"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def compute(run_dir):
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks=[]
    def check(name,ok):
        assert bool(ok),name
        checks.append({"name":name,"pass":True,"actual":bool(ok),"expected":True})
    for file,pin in m["source_files"].items():
        check("pin:"+file,sha(ROOT/file)==pin)
    prereg=json.loads((ROOT/m["preregistration"]).read_text(encoding="utf-8"))
    for file,pin in prereg["sources"].items():
        check("parent:"+file,sha(ROOT/file)==pin)
    def child(lane):
        suffix="" if lane=="primary" else "_"+lane
        code=ROOT/f"codes/foundations/pah_omc016_uniform{suffix}.py"
        dest=run_dir/f"{lane}.json"
        p=subprocess.run([sys.executable,"-X","utf8",str(code),"--output",str(dest)],
                         cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=120)
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        return lane,json.loads(dest.read_text(encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        lanes=dict(executor.map(child,("primary","independent","hostile")))
    for name,data in lanes.items():
        check(name+" executed",data["status"]=="PASS" and bool(data["checks"]) and all(x["pass"] for x in data["checks"]))
    p,i=lanes["primary"],lanes["independent"]
    check("independent derived constants",p["constants"]==i["constants"])
    # Explicit TEST ORACLES are the constants encoded in the Lean statements;
    # runtime estimates are derived in both executable lanes, never from here.
    lean_oracles={"second_moment_bound":"4","neighbor_radius":"8",
                  "good_event_lower":"11/16","H_cap":"80","A_cap":"11",
                  "tail_split":"4","numerator_cost":"590/3",
                  "denominator_cost":"320","lower_prefactor":"11/80",
                  "lower_exponent":"1550/3"}
    check("derived-to-Lean input bridge",all(p["constants"][k]==v for k,v in lean_oracles.items()))
    check("derived positive lower bound",Fraction(p["constants"]["lower_prefactor"])>0)
    check("result constants",m["proof_constants"]==p["constants"])
    check("fixed-n and uniform scopes separate",m["verdict"]=="PASS" and not m["active_gate_change"] and not m["physical_promotion"])
    leanpath=ROOT/m["lean"]["path"]
    source=leanpath.read_text(encoding="utf-8")
    reg=json.loads((ROOT/"verification/lean/registry.json").read_text(encoding="utf-8"))
    entry=next(x for x in reg["entrypoints"] if x["path"]==m["lean"]["path"])
    check("Lean registry pin",entry["sha256"]==sha(leanpath))
    names=re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)",source)
    check("Lean declaration coverage",names==entry["declarations"]==m["lean"]["declarations"])
    check("Lean source policy",not any(x in source for x in ("sorry","admit","axiom","unsafe")) and b"\r" not in leanpath.read_bytes())
    tc=reg["toolchain"]
    for key in ("toolchain_file","lakefile","lockfile"):
        hk="toolchain_sha256" if key=="toolchain_file" else key+"_sha256"
        check("toolchain:"+key,sha(ROOT/tc[key])==tc[hk])
    encoded=tc["toolchain"].replace("/","--").replace(":","---")
    lake=Path.home()/".elan/toolchains"/encoded/"bin/lake.exe"
    proc=subprocess.run([str(lake),"env","lean","Tect/PahOmc016.lean"],cwd=ROOT/"verification/lean",
                        text=True,encoding="utf-8",capture_output=True,timeout=600)
    lean_output=(proc.stdout+proc.stderr).strip()
    check("Lean diagnostics-free",proc.returncode==0 and not lean_output)
    return {"schema":"tect/pah-omc016-integrated/1.0","result_id":m["result_id"],
            "status":"PASS","verdict":m["verdict"],"checks":checks,
            "code_version":__version__,"code_sha256":sha(Path(__file__)),
            "manifest_sha256":sha(MANIFEST),"base_commit":m["base_commit"],
            "environment":{"python":platform.python_version(),"sympy":__import__("sympy").__version__},
            "proof_constants":p["constants"],"coverage":m["proof_coverage"],
            "lane_counts":{k:len(v["checks"]) for k,v in lanes.items()},
            "run_hashes":{k:sha(run_dir/f"{k}.json") for k in lanes},
            "lean":{"status":"PASS","output":lean_output,"command":"lake env lean Tect/PahOmc016.lean",
                    "source_sha256":sha(leanpath),"toolchain":tc},
            "conclusion":m["conclusion"],"non_claims":m["non_claims"]}


def main(check_only=False):
    if check_only:
        with tempfile.TemporaryDirectory(prefix="pah016-replay-") as tmp:
            directory=Path(tmp)
            result=compute(directory)
            assert json.loads((RUN/"integrated.json").read_text())==result,"stored integrated mismatch"
            for lane in ("primary","independent","hostile"):
                assert (RUN/f"{lane}.json").read_bytes()==(directory/f"{lane}.json").read_bytes(),lane+" replay mismatch"
    else:
        result=compute(RUN)
        RUN.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=RUN,suffix=".tmp")
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            json.dump(result,stream,indent=2,sort_keys=True);stream.write("\n")
        os.replace(tmp,RUN/"integrated.json")
    print(f"PAH-OMC-016 INTEGRATED: PASS ({len(result['checks'])} checks; Lean PASS; replay={check_only})")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--check",action="store_true")
    main(p.parse_args().check)
