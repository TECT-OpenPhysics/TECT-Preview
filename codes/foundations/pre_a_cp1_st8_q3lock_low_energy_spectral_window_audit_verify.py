#!/usr/bin/env python3
"""Integrated verifier for EXP-001200 low-energy spectral-window audit."""

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
SLUG = "pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-low-energy-spectral-window-audit-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R359.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R359.lean"; lake = lake_path()
    if lake is None: return {"status":"UNAVAILABLE","command":command,"output":"pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R359.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status":"PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command":command, "returncode":process.returncode, "output":output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["audit_fixture"]; scope = manifest["scope"]
    tolerance = float(fixture["orientation_tolerance"]); agreement = float(fixture.get("agreement_tolerance", 1.0e-7))
    checks: list[dict[str, Any]] = []
    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name":name,"pass":bool(ok),"actual":str(actual),"expected":str(expected)})
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity", manifest["exploration_id"] == "EXP-001200" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"],manifest["task_id"],manifest["claim_bearing"]], "EXP-001200/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY),str(INDEPENDENT),str(LEAN)], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["dimension_count_fixture","beta_count_fixture","window_count_fixture","tail_cutoff_fixture","source_edge_count_fixture","scope_fixture"]
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry","admit","axiom","unsafe")), [], "none")
    check("independent source", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY),sha256(INDEPENDENT)], "distinct normalized SHA-256")
    with tempfile.TemporaryDirectory(prefix="low-energy-spectral-window-") as temporary:
        pp, primary = child(PRIMARY, Path(temporary)/"primary.json"); ip, independent = child(INDEPENDENT, Path(temporary)/"independent.json")
        check("primary child", pp.returncode == 0 and primary.get("verdict") == "PASS", pp.stdout+pp.stderr, "PASS")
        check("independent child", ip.returncode == 0 and independent.get("verdict") == "PASS", ip.stdout+ip.stderr, "PASS")
        p, i = primary.get("derived",{}), independent.get("derived",{}); source = manifest["source_fixture"]
        expected_rows = len(source["volume_values"]) * len(source["cutoff_values"]) * len(source["beta_values"]); expected_windows = expected_rows * len(fixture["energy_windows"])
        check("row count", p.get("row_count") == i.get("row_count") == expected_rows, [p.get("row_count"),i.get("row_count"),expected_rows], "declared volume x cutoff x beta grid")
        check("window row count", p.get("window_row_count") == i.get("window_row_count") == expected_windows, [p.get("window_row_count"),i.get("window_row_count"),expected_windows], "rows x declared energy windows")
        p_rows={(int(row["volume"]),int(row["cutoff"]),float(row["beta"])):row for row in p.get("rows",[])}; i_rows={(int(row["volume"]),int(row["cutoff"]),float(row["beta"])):row for row in i.get("rows",[])}
        check("row keys", set(p_rows)==set(i_rows), [sorted(p_rows),sorted(i_rows)], "same volume/cutoff/beta keys")
        all_fields=("signed_raw_sum","signed_gibbs_sum","signed_weighted_sum","absolute_raw_sum","absolute_gibbs_sum","absolute_weighted_sum","signed_raw_sum_per_site","signed_gibbs_sum_per_site","signed_weighted_sum_per_site","absolute_raw_sum_per_site","absolute_gibbs_sum_per_site","absolute_weighted_sum_per_site","max_signed_weighted")
        group_fields=("signed_raw","signed_gibbs","signed_weighted","absolute_raw","absolute_gibbs","absolute_weighted","reverse_raw","reverse_gibbs","reverse_weighted","orientation_raw_residual","orientation_gibbs_difference","orientation_weighted_difference")
        window_fields=("window_mass","tail_mass","signed_weighted","absolute_weighted","signed_weighted_per_site","absolute_weighted_per_site","conditional_signed_weighted","conditional_signed_weighted_per_site","signed_to_absolute")
        for key in sorted(p_rows):
            pr, ir = p_rows[key], i_rows[key]
            check(f"row {key} counts", pr["pair_count"]==ir["pair_count"] and pr["group_count"]==ir["group_count"] and pr["context_count"]==ir["context_count"], [pr["pair_count"],pr["group_count"],pr["context_count"],ir["pair_count"],ir["group_count"],ir["context_count"]], "exact integer agreement")
            for field in all_fields: check(f"row {key} all {field}", abs(float(pr["all_group"][field])-float(ir["all_group"][field])) <= agreement*(1.0+abs(float(pr["all_group"][field]))), [pr["all_group"][field],ir["all_group"][field]], f"within {agreement}")
            check(f"row {key} group keys", set(tuple(g["union"]) for g in pr.get("groups",[]))==set(tuple(g["union"]) for g in ir.get("groups",[])), [pr.get("groups"),ir.get("groups")], "same union keys")
            for pg, ig in zip(pr.get("groups",[]), ir.get("groups",[])):
                for field in group_fields: check(f"row {key} group {pg['union']} {field}", abs(float(pg[field])-float(ig[field])) <= agreement*(1.0+abs(float(pg[field]))), [pg[field],ig[field]], f"within {agreement}")
                check(f"row {key} group {pg['union']} window keys", set(pg.get("windows",{}))==set(ig.get("windows",{})), [pg.get("windows"),ig.get("windows")], "same energy windows")
                for wk in sorted(pg.get("windows",{})):
                    for field in window_fields: check(f"row {key} group {pg['union']} window {wk} {field}", abs(float(pg["windows"][wk][field])-float(ig["windows"][wk][field])) <= agreement*(1.0+abs(float(pg["windows"][wk][field]))), [pg["windows"][wk][field],ig["windows"][wk][field]], f"within {agreement}")
            check(f"row {key} window keys", set(pr.get("windows",{}))==set(ir.get("windows",{})), [pr.get("windows"),ir.get("windows")], "same energy windows")
            for wk in sorted(pr.get("windows",{})):
                for field in window_fields:
                    check(f"row {key} window {wk} {field}", abs(float(pr["windows"][wk][field])-float(ir["windows"][wk][field])) <= agreement*(1.0+abs(float(pr["windows"][wk][field]))), [pr["windows"][wk][field],ir["windows"][wk][field]], f"within {agreement}")
            check(f"row {key} source keys", set(pr.get("source_touching",{}))==set(ir.get("source_touching",{})), [pr.get("source_touching"),ir.get("source_touching")], "same source keys")
            check(f"row {key} orientation", float(pr["orientation_raw_residual"]) <= tolerance and float(pr["orientation_gibbs_difference"]) <= tolerance and float(pr["orientation_weighted_difference"]) <= tolerance, [pr["orientation_raw_residual"],pr["orientation_gibbs_difference"],pr["orientation_weighted_difference"]], f"<={tolerance}")
        check("summary coverage", len(p.get("summary",[]))==len(i.get("summary",[]))==len(source["beta_values"])*len(fixture["energy_windows"]), [len(p.get("summary",[])),len(i.get("summary",[]))], "declared beta x window summaries")
        summary_fields=("signed_weighted_tail_max_per_site","signed_weighted_tail_min_per_site","tail_stability_ratio","conditional_tail_stability_ratio","full_endpoint_ratio","window_mass_min","window_mass_max")
        for ps, ins in zip(p.get("summary",[]),i.get("summary",[])):
            check(f"summary {ps.get('beta')}/{ps.get('energy_threshold')} identity", ps.get("beta")==ins.get("beta") and ps.get("energy_threshold")==ins.get("energy_threshold"), [ps,ins], "same summary key")
            for field in summary_fields: check(f"summary {ps.get('beta')}/{ps.get('energy_threshold')} {field}", abs(float(ps[field])-float(ins[field])) <= agreement*(1.0+abs(float(ps[field]))), [ps[field],ins[field]], f"within {agreement}")
            check(f"summary {ps.get('beta')}/{ps.get('energy_threshold')} flags", ps.get("tail_stable")==ins.get("tail_stable"), [ps,ins], "exact stability agreement")
        check("finite scope", all(p.get(name) is True and i.get(name) is True for name in ("finite_spectral_window_rows_closed","finite_reverse_order_antisymmetry_closed","finite_window_mass_rank_closed","finite_high_cutoff_window_stability_closed")), [p,i], "finite window flags true")
        check("QFT boundary", all(p.get(name) is False and i.get(name) is False for name in ("candidate_global_state_uniform_bound_closed","global_gibbs_state_transfer_closed","common_core_operator_embedding_closed","actual_q3_trotter_defect_closed")), [p,i], "global/common-core/QFT gates open")
        diagnostic=p.get("diagnostic",{}); check("diagnostic semantics", diagnostic.get("interpretation")=="finite fixed-energy spectral-window state-weighted diagnostic; not a global KMS or asymptotic theorem" and diagnostic.get("candidate_global_state_uniform_bound")=="not established by this audit" and diagnostic.get("actual_q3_trotter_defect")=="open", diagnostic, "finite-only interpretation")
    lean=lean_run(); check("Lean compile", lean["status"]=="PASS", lean, "PASS")
    return {"schema":"tect/foundation-audit/1.0","run_kind":"integrated","audit_id":"PA-CP1-ST8-Q3LOCK-LOW-ENERGY-SPECTRAL-WINDOW-AUDIT","claim_id":manifest["claim_ids"][0],"task_id":manifest["task_id"],"exploration_id":manifest["exploration_id"],"verdict":"PASS","assertion_count":len(checks),"assertions":checks,"lean":lean,"boundary":manifest["scope"],"recorded_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"provenance":{"manifest_sha256":sha256(MANIFEST),"primary_sha256":sha256(PRIMARY),"independent_sha256":sha256(INDEPENDENT),"lean_sha256":sha256(LEAN)}}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--no-store",action="store_true"); parser.add_argument("--skip-lean",action="store_true"); args=parser.parse_args()
    if args.skip_lean: raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload=run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INTEGRATED LOW-ENERGY-SPECTRAL-WINDOW PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}"); return 0

if __name__ == "__main__": raise SystemExit(main())
