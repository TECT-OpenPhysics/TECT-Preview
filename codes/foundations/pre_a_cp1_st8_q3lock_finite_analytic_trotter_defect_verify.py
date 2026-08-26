#!/usr/bin/env python3
"""Integrated verifier for EXP-001162, including Lean R332."""

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
SLUG = "pre_a_cp1_st8_q3lock_finite_analytic_trotter_defect"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-analytic-trotter-defect-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R332.lean"
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
    command = "lake env lean Tect/R332.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R332.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    finite = manifest["finite_fixture"]
    tolerance = float(finite["bound_slack_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001162" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001162/T-054/false")
    check("source files", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN)], "present")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["local_defect_fixture", "history_sum_fixture", "history_bound_fixture", "scope_fixture"]
    check("Lean markers", all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="finite-analytic-trotter-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        check("row count", p.get("row_count") == i.get("row_count") and p.get("row_count", 0) > 0, [p.get("row_count"), i.get("row_count")], ">0 and equal")
        for key in ("commutator_sum_by_volume", "commutator_sum_per_site_by_volume"):
            p_map, i_map = p.get(key, {}), i.get(key, {})
            check(f"{key} agreement", set(p_map) == set(i_map) and all(abs(float(p_map[name]) - float(i_map[name])) <= tolerance for name in p_map), [p_map, i_map], f"within {tolerance}")
        for key in ("max_unitary_bound", "max_history_bound", "minimum_unitary_slack", "minimum_history_slack"):
            check(f"{key} agreement", abs(float(p.get(key)) - float(i.get(key))) <= tolerance, [p.get(key), i.get(key)], f"within {tolerance}")
        p_summaries, i_summaries = p.get("volume_summaries", []), i.get("volume_summaries", [])
        check("volume summary coverage", [item.get("volume") for item in p_summaries] == [item.get("volume") for item in i_summaries] and len(p_summaries) == len(manifest["source_fixture"]["volume_values"]), [p_summaries, i_summaries], "all declared volumes")
        for p_row, i_row in zip(p_summaries, i_summaries):
            check(f"V={p_row.get('volume')} summary agreement", all(abs(float(p_row[key]) - float(i_row[key])) <= tolerance for key in ("commutator_sum", "max_final_unitary_error", "max_unitary_bound", "max_history_error", "max_history_bound", "overlap_pair_count", "term_norm_max", "coarse_volume_commutator_bound")), [p_row, i_row], f"within {tolerance}")
        scope = manifest["scope"]
        finite_flags = ("finite_local_commutator_sum_closed", "finite_fixed_cutoff_volume_linear_envelope_closed", "finite_analytic_unitary_defect_closed", "finite_two_orientation_history_bound_closed", "finite_bound_both_orders_and_signs_closed")
        check("finite flags", all(p.get(key) is True and i.get(key) is True for key in finite_flags), [p, i], "all finite flags true")
        check("QFT firewall", scope["volume_uniform_trotter_bound_closed"] is False and scope["cutoff_uniform_volume_linear_bound_closed"] is False and scope["analytic_infinite_dimensional_trotter_rate_closed"] is False and scope["operator_domain_embedding_closed"] is False and scope["common_alpha_closed"] is False and scope["pre_a_closed"] is False, scope, "uniform/domain/QFT gates remain open")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ANALYTIC-TROTTER-DEFECT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": manifest["scope"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)},
    }


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
    print(f"INTEGRATED ANALYTIC-TROTTER-DEFECT PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
