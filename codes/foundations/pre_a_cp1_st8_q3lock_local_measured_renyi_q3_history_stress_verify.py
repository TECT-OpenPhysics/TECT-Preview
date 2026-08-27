#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001202."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-q3-history-stress-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R361.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    if os.environ.get("TECT_REUSE_CANONICAL") == "1":
        suffix = "primary" if script == PRIMARY else "independent"
        canonical = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-{suffix}-{SLUG}" / f"{suffix}.json"
        payload = json.loads(canonical.read_text(encoding="utf-8"))
        return subprocess.CompletedProcess([str(script), "--reuse-canonical"], 0, stdout=f"REUSED {canonical.as_posix()}\n", stderr=""), payload
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8")); encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---"); candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake"); return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    lake = lake_path(); command = "lake env lean Tect/R361.lean"
    if lake is None: return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R361.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False); output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["finite_fixture"]; agreement = float(fixture["agreement_tolerance"]); checks: list[dict[str, Any]] = []; check_count = 0
    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        nonlocal check_count
        check_count += 1
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 64: checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001202" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001202/T-054/false")
    check("sources present", PRIMARY.is_file() and INDEPENDENT.is_file() and LEAN.is_file(), [str(PRIMARY), str(INDEPENDENT), str(LEAN)], "present")
    lean_text = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", all(marker in lean_text for marker in ("context_count_fixture", "alpha_fixture", "tail_count_fixture", "scope_fixture")), "R361 markers", "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    check("independent source distinct", sha256(PRIMARY) != sha256(INDEPENDENT), [sha256(PRIMARY), sha256(INDEPENDENT)], "distinct normalized hashes")
    with tempfile.TemporaryDirectory(prefix="local-renyi-q3-history-") as temporary:
        process_primary, primary = child(PRIMARY, Path(temporary) / "primary.json"); process_independent, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", process_primary.returncode == 0 and primary.get("verdict") == "PASS", process_primary.stdout + process_primary.stderr, "PASS")
        check("independent child", process_independent.returncode == 0 and independent.get("verdict") == "PASS", process_independent.stdout + process_independent.stderr, "PASS")
        p, i = primary.get("derived", {}), independent.get("derived", {})
        check("context counts", p.get("context_count") == i.get("context_count") == manifest["derived_oracles"]["context_count"], [p.get("context_count"), i.get("context_count")], manifest["derived_oracles"]["context_count"])
        check("route outcome agreement", p.get("route_outcome") == i.get("route_outcome"), [p.get("route_outcome"), i.get("route_outcome")], "equal")
        check("threshold agreement", abs(float(p.get("diagnostic_Q_threshold")) - float(i.get("diagnostic_Q_threshold"))) <= agreement, [p.get("diagnostic_Q_threshold"), i.get("diagnostic_Q_threshold")], "within tolerance")
        p_rows = {tuple([row["volume"], row["cutoff"], row["beta"], tuple(row["support"]), row["source_sign"], row["order"], row["sign"], row["prefix"], row["prefix_length"], row["history_adjoint"]]): row for row in p.get("contexts", [])}
        i_rows = {tuple([row["volume"], row["cutoff"], row["beta"], tuple(row["support"]), row["source_sign"], row["order"], row["sign"], row["prefix"], row["prefix_length"], row["history_adjoint"]]): row for row in i.get("contexts", [])}
        check("context keys", set(p_rows) == set(i_rows), [len(p_rows), len(i_rows)], "same keys")
        fields = ("max_q_alpha",)
        for key in sorted(p_rows, key=str):
            primary_row, independent_row = p_rows[key], i_rows[key]
            for field in fields:
                check(f"context {key} {field}", abs(float(primary_row[field]) - float(independent_row[field])) <= agreement * (1.0 + abs(float(primary_row[field]))), [primary_row[field], independent_row[field]], f"within {agreement}")
            check(f"context {key} sites", len(primary_row["sites"]) == len(independent_row["sites"]), [len(primary_row["sites"]), len(independent_row["sites"])], "same site count")
            for ps, ins in zip(primary_row["sites"], independent_row["sites"]):
                check(f"context {key} site {ps['site']}", abs(float(ps["q_alpha"]) - float(ins["q_alpha"])) <= agreement * (1.0 + abs(float(ps["q_alpha"]))), [ps["q_alpha"], ins["q_alpha"]], f"within {agreement}")
        check("finite flags", all(p.get(name) is True and i.get(name) is True for name in ("finite_local_coordinate_rows_closed", "finite_two_orientation_prefix_coverage_closed", "finite_tail_inequality_checked")), [p, i], "finite flags true")
        check("QFT firewall", all(p.get(name) is False and i.get(name) is False for name in ("actual_Q3_local_Renyi_uniform_bound_closed", "cutoff_uniformity_proved", "volume_uniformity_proved", "common_alpha_closed", "actual_split_limit_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")), [p, i], "QFT gates open")
    lean = lean_run(); check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-Q3-HISTORY-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": check_count, "assertions": checks, "lean": lean, "boundary": manifest["boundary"], "provenance": {"manifest_sha256": sha256(MANIFEST), "primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "lean_sha256": sha256(LEAN), "child_mode": "canonical-reuse" if os.environ.get("TECT_REUSE_CANONICAL") == "1" else "fresh-subprocess"}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    if args.skip_lean: raise SystemExit("skip-lean is not allowed for the integrated checkpoint")
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED LOCAL-MEASURED-RENYI-Q3-HISTORY PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
