#!/usr/bin/env python3
"""Integrated verifier for EXP-001163, including Lean R333."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_trotter_cutoff_scaling"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-trotter-cutoff-scaling-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R333.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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
    command = "lake env lean Tect/R333.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R333.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tolerance = float(manifest["audit_fixture"]["localization_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001163" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001163/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN)], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["raw_bound_fixture", "cutoff_ratio_fixture", "history_coefficient_fixture", "scope_fixture"]
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-trotter-cutoff-scaling-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        check("row count", p.get("row_count") == i.get("row_count") and p.get("row_count", 0) == len(manifest["source_fixture"]["volume_values"]) * len(manifest["source_fixture"]["cutoff_values"]), [p.get("row_count"), i.get("row_count")], "declared volume x cutoff grid")
        p_rows = {(int(row["volume"]), int(row["cutoff"])): row for row in p.get("rows", [])}
        i_rows = {(int(row["volume"]), int(row["cutoff"])): row for row in i.get("rows", [])}
        check("row keys", set(p_rows) == set(i_rows), [sorted(p_rows), sorted(i_rows)], "same volume/cutoff keys")
        row_keys = ("q_norm", "p_norm", "onsite_norm_max", "bond_norm_max", "term_norm_max", "commutator_sum", "commutator_sum_per_site", "max_overlap_commutator", "coarse_fixed_cutoff_envelope", "unitary_bound_at_step_count", "history_unit_multiplier_coefficient")
        maximum_difference = 0.0
        for key in sorted(p_rows):
            for field in row_keys:
                difference = abs(float(p_rows[key][field]) - float(i_rows[key][field]))
                maximum_difference = max(maximum_difference, difference)
                check(f"row {key} {field}", difference <= tolerance, difference, f"<={tolerance}")
            check(f"row {key} overlap count", p_rows[key]["overlap_pair_count"] == i_rows[key]["overlap_pair_count"] and p_rows[key]["local_max_dimension"] == i_rows[key]["local_max_dimension"], [p_rows[key]["overlap_pair_count"], p_rows[key]["local_max_dimension"], i_rows[key]["overlap_pair_count"], i_rows[key]["local_max_dimension"]], "exact integer agreement")
        p_summaries, i_summaries = p.get("volume_summaries", []), i.get("volume_summaries", [])
        check("summary coverage", [item.get("volume") for item in p_summaries] == [item.get("volume") for item in i_summaries], [p_summaries, i_summaries], "same volume order")
        summary_fields = ("commutator_sum_first", "commutator_sum_last", "commutator_growth_ratio_from_first_positive", "term_norm_growth_ratio", "q_norm_growth_ratio", "unitary_bound_last", "history_coefficient_last")
        for p_summary, i_summary in zip(p_summaries, i_summaries):
            for field in summary_fields:
                if p_summary[field] is None or i_summary[field] is None:
                    check(f"V={p_summary.get('volume')} summary {field}", p_summary[field] is None and i_summary[field] is None, [p_summary[field], i_summary[field]], "both None")
                else:
                    difference = abs(float(p_summary[field]) - float(i_summary[field]))
                    check(f"V={p_summary.get('volume')} summary {field}", difference <= tolerance, difference, f"<={tolerance}")
            check(f"V={p_summary.get('volume')} grid diagnostic", p_summary["commutator_nondecreasing_on_grid"] == i_summary["commutator_nondecreasing_on_grid"] and p_summary["growth_threshold_crossed"] == i_summary["growth_threshold_crossed"], [p_summary, i_summary], "exact diagnostic agreement")
        check("reference localization", abs(float(p.get("reference_localization_residual")) - float(i.get("reference_localization_residual"))) <= tolerance, [p.get("reference_localization_residual"), i.get("reference_localization_residual")], f"within {tolerance}")
        check("finite scope", p.get("finite_cutoff_scaling_rows_closed") is True and i.get("finite_cutoff_scaling_rows_closed") is True and p.get("fixed_volume_growth_diagnostic_closed") is True and i.get("fixed_volume_growth_diagnostic_closed") is True, [p, i], "finite flags true")
        check("raw route boundary", p.get("raw_operator_norm_cutoff_uniformity_closed") is False and i.get("raw_operator_norm_cutoff_uniformity_closed") is False and p.get("raw_operator_norm_route_boundary_recorded") is True and i.get("raw_operator_norm_route_boundary_recorded") is True, [p, i], "uniformity open and boundary recorded")
        check("QFT firewall", manifest["scope"]["energy_state_weighted_cutoff_uniform_route_open"] is True and manifest["scope"]["operator_domain_embedding_closed"] is False and manifest["scope"]["actual_q3_thermodynamic_history_closed"] is False and manifest["scope"]["common_alpha_closed"] is False and manifest["scope"]["pre_a_closed"] is False, manifest["scope"], "weighted/domain/QFT gates remain open")
        diagnostic = p.get("diagnostic", {})
        check("diagnostic semantics", diagnostic.get("interpretation") == "finite-grid raw coefficient growth diagnostic; not an asymptotic divergence theorem" and diagnostic.get("raw_operator_norm_cutoff_uniformity") == "not established by this audit" and diagnostic.get("energy_state_weighted_route") == "open", diagnostic, "finite-only interpretation")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-TROTTER-CUTOFF-SCALING",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": manifest["scope"],
        "provenance": {"manifest_sha256": sha256(MANIFEST), "primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "lean_sha256": sha256(LEAN)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED TROTTER-CUTOFF-SCALING PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
