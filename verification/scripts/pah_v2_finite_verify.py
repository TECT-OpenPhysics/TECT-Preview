#!/usr/bin/env python3
"""R-570 exact-source replay integrator, version 0.1.0, issued 2026-09-11.

Replays four independent-scope checks and verifies the result's immutable
evidence pins. This integrity/orchestration check does not itself prove the
written theorem or turn floating/partial Lean checks into universal proofs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

__version__="0.1.0"
ROOT=Path(__file__).resolve().parents[2]
CARD=ROOT/"strategy/pa-hyp/PAH-v2-finite-result-v1.json"
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-finite/integrated.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--lean-cache",type=Path,default=ROOT/"verification/lean/.lake/packages")
    args=parser.parse_args()
    card=json.loads(CARD.read_text(encoding="utf-8"))
    assert card["result_id"]=="R-570" and card["verdict"]=="PROVED"
    assert not card["active_gate_change"] and not card["physical_promotion"]
    assert len(card["requirement_audit"])==5
    for item in card["requirement_audit"]:
        assert item["disposition"]=="DISCHARGED_BY_EXACT_FINITE_PROOF"
    for group in ("source_files","evidence_files"):
        for p,h in card[group].items():
            assert sha(ROOT/p)==h,p
    outputs={}
    for mode in ("primary","independent","hostile","lean"):
        cmd=[sys.executable,"-X","utf8",str(ROOT/f"verification/scripts/pah_v2_finite_{mode}.py"),"--check"]
        if mode=="lean":cmd += ["--lean-cache",str(args.lean_cache)]
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=300)
        assert p.returncode==0,(mode,p.stdout,p.stderr)
        outputs[mode]={"exit_code":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
        print(p.stdout.strip(),flush=True)
    result={"schema":"tect/pah-v2-finite-integrated/1.0","status":"PASS","script_version":__version__,
            "script_sha256":sha(Path(__file__)),"result_sha256":sha(CARD),"replays":outputs,
            "scope":"Exact-byte/result-scope integrity and fresh four-lane replay; written proof is the source of universal quantifiers",
            "non_claims":"No external-person review, full-model Lean formalization, refinement, limit or physical promotion."}
    if args.check:
        assert json.loads(OUT.read_text(encoding="utf-8"))==result
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as f:
            json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("PAH-V2-INTEGRATED: PASS (exact evidence pins and fresh replays)")


if __name__=="__main__":
    main()
