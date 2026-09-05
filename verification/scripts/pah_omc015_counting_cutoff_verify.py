#!/usr/bin/env python3
"""Reproduce R-508: all three PAH-OMC-015 lanes and pinned Lean compilation.

The all-volume restricted-path theorem is the certificate's exact counting
argument. Implementation agreement checks the energy translation, not the
proof of the universal quantifier. This verifier fails on source/registry
drift, a failing lane, mismatched independent arithmetic, or Lean diagnostics.
"""
from __future__ import annotations
import argparse
import concurrent.futures
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"strategy/pa-hyp/PAH-OMC-015-result-v1.json"
RUN=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc015-counting-cutoff"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    manifest=json.loads(MANIFEST.read_text())
    rows=[]
    def check(name,ok):
        rows.append({"name":name,"pass":bool(ok)})
        assert ok,name
    for file,pin in manifest["source_files"].items():
        check("source pin "+file,sha(ROOT/file)==pin)
    prereg=json.loads((ROOT/manifest["preregistration"]).read_text())
    for name,pin in prereg["sources"].items():
        check("parent "+name,sha(ROOT/prereg["source_path_base"]/name)==pin)
    def child(lane):
        suffix="" if lane=="primary" else "_"+lane
        script=ROOT/f"codes/foundations/pah_omc015_counting_cutoff{suffix}.py"
        dest=RUN/f"{lane}.json"
        proc=subprocess.run([sys.executable,"-X","utf8",str(script),"--output",str(dest)],
                            cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=180)
        if proc.returncode:
            raise RuntimeError(proc.stdout+proc.stderr)
        data=json.loads(dest.read_text())
        return lane,data
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        lanes=dict(executor.map(child,("primary","independent","hostile")))
    for lane,data in lanes.items():
        check(lane+" checks",data["status"]=="PASS" and bool(data["checks"]) and all(x["pass"] for x in data["checks"]))
    primary,ind=lanes["primary"],lanes["independent"]
    check("independent full-energy digest",primary["energy_digest"]==ind["energy_digest"])
    check("independent polynomial coefficients",primary["penalty_coefficients_R2_R4_R6"]==ind["penalty_coefficients_R2_R4_R6"])
    check("strict charge penalty",all(Fraction(x)>0 for x in ind["penalty_coefficients_R2_R4_R6"]))
    # Source names are enumerated for coverage; numerical finite samples alone
    # never pass the universal theorem. Each source proof anchor is explicit.
    check("four-observable proof mapping",set(manifest["conclusion"]["ordered_squared_limits"])=={"ell_a","ell_d","H_0","H_1"})
    check("single-candidate scope",manifest["verdict"]=="CANDIDATE_REJECTED" and not manifest["active_gate_change"] and not manifest["physical_promotion"])
    leanpath=ROOT/manifest["lean"]["path"]
    source=leanpath.read_text()
    registry=json.loads((ROOT/"verification/lean/registry.json").read_text())
    entry=next(x for x in registry["entrypoints"] if x["path"]==manifest["lean"]["path"])
    check("Lean registry source",entry["sha256"]==sha(leanpath))
    names=re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)",source)
    check("Lean declarations",names==entry["declarations"]==manifest["lean"]["declarations"])
    check("Lean source policy",not any(t in source for t in ("sorry","admit","axiom","unsafe")) and b"\r" not in leanpath.read_bytes())
    toolchain=registry["toolchain"]
    for key in ("toolchain_file","lakefile","lockfile"):
        hashkey="toolchain_sha256" if key=="toolchain_file" else key+"_sha256"
        check("toolchain "+key,sha(ROOT/toolchain[key])==toolchain[hashkey])
    encoded=toolchain["toolchain"].replace("/","--").replace(":","---")
    lake=Path.home()/".elan/toolchains"/encoded/"bin/lake.exe"
    proc=subprocess.run([str(lake),"env","lean","Tect/PahOmc015.lean"],cwd=ROOT/"verification/lean",
                        text=True,encoding="utf-8",capture_output=True,timeout=180)
    lean_output=(proc.stdout+proc.stderr).strip()
    check("Lean compilation diagnostics-free",proc.returncode==0 and not lean_output)
    coverage={
        "finite_normalization_conditional_recovery":"certificate#finite-ensemble-and-generator; conditional_weight_cancellation",
        "finite_stationarity":"certificate#finite-ensemble-and-generator; inverse root replays; gibbs_root_flux",
        "uniform_in_R_at_each_fixed_n":"certificate#primary-energy-and-counting-proof; independent coefficient/charge-tail proof",
        "radial_ordered_limits":"certificate#independent-proof-and-explicit-modulus; cutoff_squeeze and charge_penalty_diverges",
        "holonomy_ordered_limits":"pointwise binary_character_square",
        "source_translation_boundary":"all-n incidence/counting proof is written in certificate; finite diagnostics audit implementation only"}
    payload={"schema":"tect/pah-omc015-integrated/1.0","result_id":manifest["result_id"],"status":"PASS",
             "verdict":manifest["verdict"],"checks":rows,"coverage":coverage,
             "manifest_sha256":sha(MANIFEST),"code_sha256":sha(Path(__file__)),
             "lane_counts":{name:len(data["checks"]) for name,data in lanes.items()},
             "run_hashes":{name:sha(RUN/f"{name}.json") for name in lanes},
             "lean":{"command":"lake env lean Tect/PahOmc015.lean","status":"PASS","output":lean_output,
                     "source_sha256":sha(leanpath),"toolchain":toolchain},
             "conclusion":manifest["conclusion"],"non_claims":manifest["non_claims"]}
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=output.parent,suffix=".tmp")
    with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
        json.dump(payload,stream,indent=2,sort_keys=True);stream.write("\n")
    os.replace(tmp,output)
    print(f"PAH-OMC-015 INTEGRATED: PASS ({len(rows)} checks; {manifest['verdict']}; Lean PASS)")
    return payload


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=RUN/"integrated.json")
    run(parser.parse_args().output)
