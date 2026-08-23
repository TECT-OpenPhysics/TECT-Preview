#!/usr/bin/env python3
"""Integrated verifier for EXP-001026."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-weighted-recurrence-decay-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_recurrence_decay_bridge.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_weighted_recurrence_decay_bridge_independent.py"
LEAN = REPO / "verification/lean/Tect/R210.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return proc, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8")); encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake"); return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path()
    if lake is None: return {"status":"UNAVAILABLE","command":"lake env lean Tect/R210.lean","output":"pinned lake executable not found"}
    proc = subprocess.run([str(lake), "env", "lean", "Tect/R210.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False); output=(proc.stdout+"\n"+proc.stderr).strip()
    return {"status":"PASS" if proc.returncode==0 and "error:" not in output.lower() else "FAIL","command":"lake env lean Tect/R210.lean","returncode":proc.returncode,"output":output[-2000:]}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--no-store",action="store_true"); parser.add_argument("--skip-lean",action="store_true"); args=parser.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); rows: list[dict[str,Any]]=[]
    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name":name,"pass":bool(ok),"actual":actual,"expected":expected})
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    check("identity", manifest["exploration_id"]=="EXP-001026" and manifest["task_id"]=="T-054", [manifest["exploration_id"],manifest["task_id"]], "EXP-001026/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("conditional declaration", manifest["recurrence_hypothesis"]["supplied_by_q3"] is False and manifest["conclusion"]["boundary_decay_is_conditional"] is True, manifest["recurrence_hypothesis"], "explicit conditional bridge")
    check("formal integration", manifest["formal_integration"]=={"events":[],"results":[],"negatives":[],"no_new_result":True,"no_new_negative":True,"no_pdf":True}, manifest["formal_integration"], "no event/result/negative/PDF")
    check("Lean source", LEAN.is_file(), str(LEAN), True); source=LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in source for marker in manifest["lean_crosscheck"]["theorem_markers"]), manifest["lean_crosscheck"]["theorem_markers"], "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry","admit","axiom","unsafe")), [], "none")
    boundary=(manifest["boundary"]+" "+manifest["qft_interface"]["open"]+" "+manifest["qft_interface"]["tect_boundary"]).lower()
    check("Q3 recurrence open", "supplied_by_q3" in str(manifest["recurrence_hypothesis"]).lower() and manifest["recurrence_hypothesis"]["status"]=="OPEN", manifest["recurrence_hypothesis"], "OPEN")
    check("QFT firewall", "heat_root_incidence" in boundary and "no" in boundary, boundary, "no production owner")
    with tempfile.TemporaryDirectory(prefix="recurrence-decay-integrated-") as temp:
        pp, primary=child(PRIMARY,Path(temp)/"primary.json"); ip, independent=child(INDEPENDENT,Path(temp)/"independent.json")
        check("primary child",pp.returncode==0 and primary.get("verdict")=="PASS",pp.stdout+pp.stderr,"PASS"); check("independent child",ip.returncode==0 and independent.get("verdict")=="PASS",ip.stdout+ip.stderr,"PASS")
        check("positive totals",primary.get("total",0)>0 and independent.get("total",0)>0,[primary.get("total"),independent.get("total")],">0")
        for key in ("side","max_degree","weight_base","C","J","delta","weighted_recurrence_to_decay_closed","volume_uniform_conditional","recurrence_hypothesis_supplied_by_q3","boundary_commutator_decay_closed","exhaustion_cauchy_closed","common_alpha_closed"):
            check(f"lane agreement {key}",primary.get("derived",{}).get(key)==independent.get("derived",{}).get(key),[primary.get("derived",{}).get(key),independent.get("derived",{}).get(key)],"equal")
    lean={"status":"SKIPPED","command":"lake env lean Tect/R210.lean"} if args.skip_lean else lean_run(); check("Lean compile",args.skip_lean or lean["status"]=="PASS",lean,"PASS")
    payload={"schema":"tect/foundation-audit/1.0","run_kind":"integrated","audit_id":"PA-CP1-ST8-Q3LOCK-WEIGHTED-RECURRENCE-DECAY-BRIDGE","claim_id":manifest["claim_id"],"task_id":manifest["task_id"],"exploration_id":manifest["exploration_id"],"verdict":"PASS","assertion_count":len(rows),"assertions":rows,"lean":lean,"boundary":manifest["boundary"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"provenance":{"primary_sha256":sha256(PRIMARY),"independent_sha256":sha256(INDEPENDENT),"manifest_sha256":sha256(MANIFEST),"lean_sha256":sha256(LEAN)}}
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INTEGRATED RECURRENCE-DECAY PASS {len(rows)}/{len(rows)}; Lean={lean['status']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
