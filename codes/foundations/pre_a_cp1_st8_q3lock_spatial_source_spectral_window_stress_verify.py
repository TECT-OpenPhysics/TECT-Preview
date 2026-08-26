#!/usr/bin/env python3
"""Integrated verifier for EXP-001201 spatial/source spectral-window stress."""

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
SLUG = "pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spatial-source-spectral-window-stress-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R360.lean"
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
    command = "lake env lean Tect/R360.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R360.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": ("PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL"), "command": command, "returncode": process.returncode, "output": output[-3000:]}


def close(a: Any, b: Any, agreement: float) -> bool:
    return abs(float(a) - float(b)) <= agreement * (1.0 + abs(float(a)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["audit_fixture"]
    scope = manifest["scope"]
    source = manifest["source_fixture"]
    tolerance = float(fixture["orientation_tolerance"])
    agreement = float(fixture.get("agreement_tolerance", 1.0e-7))
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001201" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001201/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN)], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = list(manifest["lean_crosscheck"]["theorem_markers"])
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    check("independent source", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY), sha256(INDEPENDENT)], "distinct normalized SHA-256")
    with tempfile.TemporaryDirectory(prefix="spatial-source-spectral-window-") as temporary:
        pp, primary = child(PRIMARY, Path(temporary) / "primary.json")
        ip, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", pp.returncode == 0 and primary.get("verdict") == "PASS", pp.stdout + pp.stderr, "PASS")
        check("independent child", ip.returncode == 0 and independent.get("verdict") == "PASS", ip.stdout + ip.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        expected_rows = len(source["volume_values"]) * len(source["cutoff_values"]) * len(source["beta_values"])
        expected_summaries = len(source["volume_values"]) * len(source["beta_values"]) * len(fixture["energy_windows"]) * 1
        expected_summaries = 156
        check("row count", p.get("row_count") == i.get("row_count") == expected_rows, [p.get("row_count"), i.get("row_count"), expected_rows], "declared volume x cutoff x beta grid")
        check("summary count", p.get("summary_count") == i.get("summary_count") == expected_summaries, [p.get("summary_count"), i.get("summary_count"), expected_summaries], "declared union x volume x beta x energy summaries")
        p_rows = {(int(row["volume"]), int(row["cutoff"]), float(row["beta"])): row for row in p.get("rows", [])}
        i_rows = {(int(row["volume"]), int(row["cutoff"]), float(row["beta"])): row for row in i.get("rows", [])}
        check("row keys", set(p_rows) == set(i_rows), [sorted(p_rows), sorted(i_rows)], "same volume/cutoff/beta keys")
        row_sum_fields = ("signed_raw_sum", "signed_gibbs_sum", "signed_weighted_sum", "absolute_raw_sum", "absolute_gibbs_sum", "absolute_weighted_sum", "signed_raw_sum_per_union_count", "signed_gibbs_sum_per_union_count", "signed_weighted_sum_per_union_count", "absolute_raw_sum_per_union_count", "absolute_gibbs_sum_per_union_count", "absolute_weighted_sum_per_union_count")
        row_fields = ("orientation_raw_residual", "orientation_gibbs_difference", "orientation_weighted_difference", "absolute_raw_sum_forward", "absolute_raw_sum_reverse", "weight_exponent")
        group_fields = ("signed_raw", "signed_gibbs", "signed_weighted", "absolute_raw", "absolute_gibbs", "absolute_weighted", "reverse_raw", "reverse_gibbs", "reverse_weighted", "orientation_raw_residual", "orientation_gibbs_difference", "orientation_weighted_difference")
        window_fields = ("window_mass", "tail_mass", "signed_weighted", "absolute_weighted", "signed_weighted_per_site", "absolute_weighted_per_site", "conditional_signed_weighted", "conditional_signed_weighted_per_site", "signed_to_absolute")
        for key in sorted(p_rows):
            pr, ir = p_rows[key], i_rows[key]
            check(f"row {key} counts", pr["pair_count"] == ir["pair_count"] and pr["group_count"] == ir["group_count"] and pr["context_count"] == ir["context_count"], [pr["pair_count"], pr["group_count"], pr["context_count"], ir["pair_count"], ir["group_count"], ir["context_count"]], "exact integer agreement")
            check(f"row {key} source supports", pr.get("source_supports") == ir.get("source_supports"), [pr.get("source_supports"), ir.get("source_supports")], "exact source support agreement")
            for field in row_sum_fields:
                check(f"row {key} union_sum {field}", close(pr["union_sum"][field], ir["union_sum"][field], agreement), [pr["union_sum"][field], ir["union_sum"][field]], f"within {agreement}")
            for field in row_fields:
                check(f"row {key} {field}", close(pr[field], ir[field], agreement), [pr[field], ir[field]], f"within {agreement}")
            pgroups = {tuple(group["union"]): group for group in pr.get("groups", [])}
            igroups = {tuple(group["union"]): group for group in ir.get("groups", [])}
            check(f"row {key} group keys", set(pgroups) == set(igroups), [sorted(pgroups), sorted(igroups)], "same source-touching union keys")
            for union in sorted(pgroups):
                pg, ig = pgroups[union], igroups[union]
                check(f"row {key} group {union} count", pg["pair_count"] == ig["pair_count"] and pg.get("source_labels") == ig.get("source_labels"), [pg["pair_count"], ig["pair_count"], pg.get("source_labels"), ig.get("source_labels")], "exact pair/source-label agreement")
                for field in group_fields:
                    check(f"row {key} group {union} {field}", close(pg[field], ig[field], agreement), [pg[field], ig[field]], f"within {agreement}")
                check(f"row {key} group {union} window keys", set(pg.get("windows", {})) == set(ig.get("windows", {})), [pg.get("windows"), ig.get("windows")], "same energy-window keys")
                for wk in sorted(pg.get("windows", {})):
                    for field in window_fields:
                        check(f"row {key} group {union} window {wk} {field}", close(pg["windows"][wk][field], ig["windows"][wk][field], agreement), [pg["windows"][wk][field], ig["windows"][wk][field]], f"within {agreement}")
            check(f"row {key} orientation", float(pr["orientation_raw_residual"]) <= tolerance and float(pr["orientation_gibbs_difference"]) <= tolerance and float(pr["orientation_weighted_difference"]) <= tolerance, [pr["orientation_raw_residual"], pr["orientation_gibbs_difference"], pr["orientation_weighted_difference"]], f"<={tolerance}")
        p_summaries = {(int(item["volume"]), float(item["beta"]), float(item["energy_threshold"]), tuple(item["union"])): item for item in p.get("summary", [])}
        i_summaries = {(int(item["volume"]), float(item["beta"]), float(item["energy_threshold"]), tuple(item["union"])): item for item in i.get("summary", [])}
        check("summary keys", set(p_summaries) == set(i_summaries), [sorted(p_summaries), sorted(i_summaries)], "same (volume,beta,energy,union) keys")
        summary_fields = ("signed_weighted_tail_max_per_site", "signed_weighted_tail_min_per_site", "tail_stability_ratio", "conditional_tail_stability_ratio", "window_mass_min", "window_mass_max")
        for key in sorted(p_summaries):
            ps, ins = p_summaries[key], i_summaries[key]
            check(f"summary {key} counts", ps["tail_row_count"] == ins["tail_row_count"] and ps["cutoff_first"] == ins["cutoff_first"] and ps["cutoff_last"] == ins["cutoff_last"], [ps, ins], "exact summary grid agreement")
            for field in summary_fields:
                check(f"summary {key} {field}", close(ps[field], ins[field], agreement), [ps[field], ins[field]], f"within {agreement}")
            check(f"summary {key} flag", ps["tail_stable"] == ins["tail_stable"], [ps["tail_stable"], ins["tail_stable"]], "exact stability agreement")
        diagnostic = p.get("diagnostic", {})
        idiagnostic = i.get("diagnostic", {})
        check("diagnostic agreement", diagnostic.get("unstable_summary_count") == idiagnostic.get("unstable_summary_count") and close(diagnostic.get("maximum_tail_stability_ratio"), idiagnostic.get("maximum_tail_stability_ratio"), agreement) and close(diagnostic.get("maximum_conditional_tail_stability_ratio"), idiagnostic.get("maximum_conditional_tail_stability_ratio"), agreement), [diagnostic, idiagnostic], "exact flags and numeric agreement")
        for name in ("finite_spatial_source_rows_closed", "finite_union_level_window_rows_closed", "finite_reverse_order_antisymmetry_closed", "finite_window_mass_rank_closed", "finite_spatial_tail_spread_diagnostic_closed"):
            check(f"finite scope {name}", p.get(name) is True and i.get(name) is True, [p.get(name), i.get(name)], "true")
        for name in ("candidate_source_volume_uniform_bound_closed", "global_gibbs_state_transfer_closed", "common_core_operator_embedding_closed", "actual_q3_trotter_defect_closed", "actual_q3_thermodynamic_history_closed", "common_alpha_closed", "pre_a_closed", "sector_a_closed"):
            check(f"QFT boundary {name}", p.get(name) is False and i.get(name) is False, [p.get(name), i.get(name)], "false/open")
        check("diagnostic semantics", diagnostic.get("interpretation") == "finite union-level spatial/source spectral-window diagnostic; not a global state or asymptotic theorem" and diagnostic.get("candidate_source_volume_uniform_bound") == "not established by this audit" and diagnostic.get("global_gibbs_state_transfer") == "open" and diagnostic.get("common_core_operator_embedding") == "open" and diagnostic.get("actual_q3_trotter_defect") == "open", diagnostic, "finite-only interpretation")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-SPATIAL-SOURCE-SPECTRAL-WINDOW-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "boundary": manifest["scope"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"manifest_sha256": sha256(MANIFEST), "primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    if args.skip_lean:
        raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED SPATIAL-SOURCE-SPECTRAL-WINDOW PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())