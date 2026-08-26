#!/usr/bin/env python3
"""Integrated verifier for EXP-001199, including Lean R358."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-signed-cancellation-audit-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R358.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R358.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R358.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tolerance = float(manifest["audit_fixture"]["orientation_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001199" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001199/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN)], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["dimension_count_fixture", "cutoff_count_fixture", "beta_count_fixture", "source_edge_count_fixture", "scope_fixture"]
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    with tempfile.TemporaryDirectory(prefix="high-cutoff-signed-cancellation-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        source_manifest = manifest["source_fixture"]
        expected_count = len(source_manifest["volume_values"]) * len(source_manifest["cutoff_values"]) * len(source_manifest["beta_values"])
        check("row count", p.get("row_count") == i.get("row_count") == expected_count, [p.get("row_count"), i.get("row_count"), expected_count], "declared volume x cutoff x beta grid")
        p_rows = {(int(row["volume"]), int(row["cutoff"]), float(row["beta"])): row for row in p.get("rows", [])}
        i_rows = {(int(row["volume"]), int(row["cutoff"]), float(row["beta"])): row for row in i.get("rows", [])}
        check("row keys", set(p_rows) == set(i_rows), [sorted(p_rows), sorted(i_rows)], "same volume/cutoff/beta keys")
        fields = ("signed_raw_sum", "signed_gibbs_sum", "signed_weighted_sum", "absolute_raw_sum", "absolute_gibbs_sum", "absolute_weighted_sum", "signed_raw_sum_per_site", "signed_gibbs_sum_per_site", "signed_weighted_sum_per_site", "absolute_raw_sum_per_site", "absolute_gibbs_sum_per_site", "absolute_weighted_sum_per_site", "max_signed_raw", "max_signed_gibbs", "max_signed_weighted")
        group_fields = ("signed_raw", "signed_gibbs", "signed_weighted", "absolute_raw", "absolute_gibbs", "absolute_weighted", "reverse_raw", "reverse_gibbs", "reverse_weighted", "orientation_raw_residual", "orientation_gibbs_difference", "orientation_weighted_difference")
        source_fields = ("signed_raw_sum", "signed_gibbs_sum", "signed_weighted_sum", "absolute_raw_sum", "absolute_gibbs_sum", "absolute_weighted_sum", "signed_weighted_sum_per_source_site", "signed_gibbs_sum_per_source_site", "signed_raw_sum_per_source_site", "max_signed_raw", "max_signed_gibbs", "max_signed_weighted")
        for key in sorted(p_rows):
            p_row, i_row = p_rows[key], i_rows[key]
            check(f"row {key} counts", p_row["pair_count"] == i_row["pair_count"] and p_row["group_count"] == i_row["group_count"] and p_row["context_count"] == i_row["context_count"], [p_row["pair_count"], p_row["group_count"], p_row["context_count"], i_row["pair_count"], i_row["group_count"], i_row["context_count"]], "exact integer agreement")
            for field in fields:
                check(f"row {key} all {field}", abs(float(p_row["all_group"][field]) - float(i_row["all_group"][field])) <= tolerance, [p_row["all_group"][field], i_row["all_group"][field]], f"within {tolerance}")
            p_groups = {tuple(group["union"]): group for group in p_row["groups"]}
            i_groups = {tuple(group["union"]): group for group in i_row["groups"]}
            check(f"row {key} group keys", set(p_groups) == set(i_groups), [sorted(p_groups), sorted(i_groups)], "same union keys")
            for union in sorted(p_groups):
                pg, ig = p_groups[union], i_groups[union]
                check(f"row {key} group {union} count", pg["pair_count"] == ig["pair_count"], [pg["pair_count"], ig["pair_count"]], "exact integer agreement")
                for field in group_fields:
                    check(f"row {key} group {union} {field}", abs(float(pg[field]) - float(ig[field])) <= tolerance, [pg[field], ig[field]], f"within {tolerance}")
            check(f"row {key} source keys", set(p_row["source_touching"]) == set(i_row["source_touching"]), [p_row["source_touching"], i_row["source_touching"]], "same source keys")
            for source_key in sorted(p_row["source_touching"]):
                ps, ins = p_row["source_touching"][source_key], i_row["source_touching"][source_key]
                check(f"row {key} source {source_key} count", ps["group_count"] == ins["group_count"], [ps["group_count"], ins["group_count"]], "exact integer agreement")
                for field in source_fields:
                    check(f"row {key} source {source_key} {field}", abs(float(ps[field]) - float(ins[field])) <= tolerance, [ps[field], ins[field]], f"within {tolerance}")
            check(f"row {key} orientation", float(p_row["orientation_raw_residual"]) <= tolerance and float(p_row["orientation_gibbs_difference"]) <= tolerance and float(p_row["orientation_weighted_difference"]) <= tolerance, [p_row["orientation_raw_residual"], p_row["orientation_gibbs_difference"], p_row["orientation_weighted_difference"]], f"<={tolerance}")
        check("summary coverage", len(p.get("summary", [])) == len(i.get("summary", [])) == len(source_manifest["volume_values"]) * len(source_manifest["beta_values"]), [len(p.get("summary", [])), len(i.get("summary", []))], "declared volume x beta summaries")
        summary_fields = ("signed_weighted_per_site_max", "absolute_weighted_per_site_max", "signed_cutoff_growth_ratio", "signed_to_absolute_endpoint_ratio")
        for ps, ins in zip(p.get("summary", []), i.get("summary", [])):
            check(f"summary {ps.get('volume')}/{ps.get('beta')} identity", ps.get("volume") == ins.get("volume") and ps.get("beta") == ins.get("beta"), [ps, ins], "same summary key")
            for field in summary_fields:
                check(f"summary {ps.get('volume')}/{ps.get('beta')} {field}", abs(float(ps[field]) - float(ins[field])) <= tolerance, [ps[field], ins[field]], f"within {tolerance}")
            check(f"summary {ps.get('volume')}/{ps.get('beta')} flags", ps.get("signed_cutoff_nondecreasing") == ins.get("signed_cutoff_nondecreasing") and ps.get("growth_threshold_crossed") == ins.get("growth_threshold_crossed"), [ps, ins], "exact diagnostic agreement")
        check("finite scope", p.get("finite_signed_union_rows_closed") is True and i.get("finite_signed_union_rows_closed") is True and p.get("finite_reverse_order_antisymmetry_closed") is True and i.get("finite_reverse_order_antisymmetry_closed") is True and p.get("cancellation_diagnostic_closed") is True and i.get("cancellation_diagnostic_closed") is True, [p, i], "finite flags true")
        check("QFT boundary", p.get("candidate_cutoff_volume_beta_uniform_bound_closed") is False and i.get("candidate_cutoff_volume_beta_uniform_bound_closed") is False and p.get("global_gibbs_state_transfer_closed") is False and i.get("global_gibbs_state_transfer_closed") is False and p.get("common_core_operator_embedding_closed") is False and i.get("common_core_operator_embedding_closed") is False, [p, i], "uniform/global/domain gates open")
        diagnostic = p.get("diagnostic", {})
        check("diagnostic semantics", diagnostic.get("interpretation") == "finite high-cutoff signed-union cancellation diagnostic; not a global-state or asymptotic bound" and diagnostic.get("candidate_cutoff_volume_beta_uniform_bound") == "not established by this audit" and diagnostic.get("actual_q3_trotter_defect") == "open", diagnostic, "finite-only interpretation")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-HIGH-CUTOFF-SIGNED-CANCELLATION-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "boundary": manifest["scope"], "provenance": {"manifest_sha256": sha256(MANIFEST), "primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED HIGH-CUTOFF-SIGNED-CANCELLATION PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
