#!/usr/bin/env python3
"""Pinned PAH-v2 Lean algebra replay, version 0.1.0, issued 2026-09-11.

Compiles fresh using exact pinned Lean and locked package checkouts. A shared
read-only build cache is allowed; its Git revisions must match the local lock.
The result states parameterized algebra scope, not a full PAH formalization.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess

__version__="0.1.0"
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-finite/lean.json"
SOURCE=ROOT/"verification/lean/Tect/PahV2Finite.lean"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cache):
    registry=json.loads((ROOT/"verification/lean/registry.json").read_text())
    tc=registry["toolchain"]
    for p,h in (("toolchain_file","toolchain_sha256"),("lakefile","lakefile_sha256"),("lockfile","lockfile_sha256")):
        assert sha(ROOT/tc[p])==tc[h]
    entry=next(x for x in registry["entrypoints"] if x["path"]==SOURCE.relative_to(ROOT).as_posix())
    assert sha(SOURCE)==entry["sha256"]
    content=SOURCE.read_text(encoding="utf-8")
    for forbidden in registry["source_policy"]["forbidden_tokens"]:
        assert not re.search(r"\b"+forbidden+r"\b",content)
    for name in entry["declarations"]:
        assert re.search(r"theorem\s+"+name+r"\b",content)
    lock=json.loads((ROOT/tc["lockfile"]).read_text())
    dependencies={}
    libraries=[]
    for pkg in lock["packages"]:
        folder=cache/pkg["name"]
        proc=subprocess.run(["git","-c",f"safe.directory={folder.as_posix()}","-C",str(folder),"rev-parse","HEAD"],capture_output=True,text=True,encoding="utf-8")
        assert proc.returncode==0,proc.stderr
        actual=proc.stdout.strip(); assert actual==pkg["rev"],pkg["name"]
        dependencies[pkg["name"]]=actual
        lib=folder/".lake/build/lib/lean"
        if lib.is_dir(): libraries.append(str(lib))
    encoded=tc["toolchain"].replace("/","--").replace(":","---")
    exe=Path.home()/".elan/toolchains"/encoded/"bin/lean.exe"
    assert exe.is_file()
    version=subprocess.run([str(exe),"--version"],capture_output=True,text=True,encoding="utf-8",check=True).stdout.strip()
    assert "4.32.1" in version
    env=os.environ.copy(); env["LEAN_PATH"]=os.pathsep.join(libraries)
    proc=subprocess.run([str(exe),str(SOURCE)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",env=env,timeout=240)
    assert proc.returncode==0,proc.stdout+proc.stderr
    return {"schema":"tect/pah-v2-lean-cross-check/1.0","status":"PASS","script_version":__version__,
            "script_sha256":sha(Path(__file__)),"source_sha256":sha(SOURCE),"declarations":entry["declarations"],
            "toolchain":tc,"dependency_revisions_checked":dependencies,"compiler_version":version,
            "exit_code":proc.returncode,"stdout":proc.stdout,"stderr":proc.stderr,
            "compiler_command":"pinned lean executable with LEAN_PATH from revision-checked cached package builds",
            "equivalent_lake_command":"cd verification/lean; lake env lean Tect/PahV2Finite.lean",
            "scope":"Parameterized integer/modular inverse arithmetic, constant-generator sum, Gibbs flux, root square/half and complex pairing identities, commuting-idempotent algebra",
            "not_encoded":"Full PAH state type, cell-complex admissibility, all-functional gauge/Aut invariance, group-average construction and full finite root summation are proved in the written proof, not claimed encoded here.",
            "environment":{"python":platform.python_version(),"platform":platform.platform()},
            "non_claims":"No all-model Lean formalization, physical identification, refinement or limit theorem."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lean-cache",type=Path,default=ROOT/"verification/lean/.lake/packages")
    p.add_argument("--check",action="store_true"); args=p.parse_args()
    result=run(args.lean_cache)
    if args.check:
        old=json.loads(OUT.read_text())
        assert {k:v for k,v in old.items() if k!="environment"}=={k:v for k,v in result.items() if k!="environment"}
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as f:
            json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
    print(f"PAH-V2-LEAN: PASS ({len(result['declarations'])} parameterized declarations, full model not encoded)")


if __name__=="__main__":
    main()
