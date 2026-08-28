#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-389."""

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
SLUG = "pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-window-kinetic-corridor-finite-checkpoint-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
HOSTILE = REPO / f"codes/foundations/{SLUG}_hostile.py"
LEAN = REPO / "verification/lean/Tect/R389.lean"
REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
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


def lake_path() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def compile_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R389.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R389.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001232" and manifest["result_id"] == "R-389" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001232/R-389/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, REGISTRY)), "all present", "all present")
    check("independent source", digest(PRIMARY) != digest(INDEPENDENT), [digest(PRIMARY), digest(INDEPENDENT)], "distinct")
    markers = ["projected_seminorm_nonnegative", "window_mass_split", "scope_fixture"]
    lean_text = LEAN.read_text(encoding="utf-8")
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R389.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == digest(LEAN), entries[0]["sha256"], digest(LEAN))
    check("Lean declarations", entries[0]["declarations"] == markers, entries[0]["declarations"], markers)

    with tempfile.TemporaryDirectory(prefix="r389-") as temporary:
        root = Path(temporary)
        primary_process, primary = run_child(PRIMARY, root / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, root / "hostile.json")
    check("primary child", primary_process.returncode == 0 and "PASS" in primary_process.stdout, primary_process.stdout[-3000:], "PASS")
    check("independent child", independent_process.returncode == 0 and "PASS" in independent_process.stdout, independent_process.stdout[-3000:], "PASS")
    check("hostile child", hostile_process.returncode == 0 and "CAUGHT" in hostile_process.stdout, hostile_process.stdout[-3000:], "CAUGHT")
    pd, ind = primary["derived"], independent["derived"]
    tolerance = float(fixture["agreement_tolerance"])
    for field in ("operator_norm", "projected_weighted_norm", "conditional_projected_norm"):
        check(f"agreement maximum {field}", abs(float(pd["maximums"][field]) - float(ind["maximums"][field])) <= tolerance, [pd["maximums"][field], ind["maximums"][field]], f"within {tolerance}")
    check("agreement growth", abs(float(pd["operator_growth_ratio"]) - float(ind["operator_growth_ratio"])) <= tolerance, [pd["operator_growth_ratio"], ind["operator_growth_ratio"]], f"within {tolerance}")
    check("agreement counts", pd["seed_rows"] == ind["seed_rows"] and pd["weighted_rows"] == ind["weighted_rows"], [pd["seed_rows"], pd["weighted_rows"], ind["seed_rows"], ind["weighted_rows"]], "equal")
    check("agreement keys", pd["corridor_keys"] == ind["corridor_keys"] and pd["outside_keys"] == ind["outside_keys"] and set(pd["summaries"]) == set(ind["summaries"]), "keys equal", "equal")
    summary_fields = ("projected_tail_ratio", "conditional_tail_ratio", "projected_late_ratio", "conditional_late_ratio", "window_mass_min", "window_mass_max")
    max_difference = 0.0
    max_location = "none"
    for key in pd["summaries"]:
        for field in summary_fields:
            difference = abs(float(pd["summaries"][key][field]) - float(ind["summaries"][key][field]))
            if difference > max_difference:
                max_difference, max_location = difference, f"{key}/{field}"
    check("agreement summaries", max_difference <= tolerance, max_difference, f"<={tolerance}")
    finite_flags = ("finite_spectral_window_weighted_corridor_closed", "finite_eta_split_closed", "finite_window_mass_rank_closed", "finite_operator_growth_stress_closed")
    open_flags = tuple(key for key in scope if key.endswith("_closed") and key not in finite_flags)
    for field in finite_flags:
        check(f"scope {field}", pd[field] is True and ind[field] is True, [pd[field], ind[field]], "true")
    for field in open_flags:
        check(f"scope {field}", pd[field] is False and ind[field] is False, [pd[field], ind[field]], "false")
    corridor = [pd["summaries"][key] for key in pd["corridor_keys"]]
    outside = [pd["summaries"][key] for key in pd["outside_keys"]]
    threshold = float(fixture["tail_stability_ratio_threshold"])
    check("corridor stability", all(item["stable"] for item in corridor), "all corridor summaries stable", "true")
    check("outside stress", max(item["projected_tail_ratio"] for item in outside) > threshold, max(item["projected_tail_ratio"] for item in outside), f">{threshold}")
    check("operator growth", float(pd["operator_growth_ratio"]) > float(fixture["operator_growth_threshold"]), pd["operator_growth_ratio"], f">{fixture['operator_growth_threshold']}")
    check("hostile separation", float(hostile["derived"]["wrong_momentum_commutator_min"]) > float(fixture["hostile_threshold"]), hostile["derived"]["wrong_momentum_commutator_min"], f">{fixture['hostile_threshold']}")
    check("hostile coordinate anchor", float(hostile["derived"]["correct_coordinate_commutator_max"]) <= float(fixture["hostile_threshold"]), hostile["derived"]["correct_coordinate_commutator_max"], f"<={fixture['hostile_threshold']}")
    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    firewall = [field for field in open_flags if pd[field]]
    check("scope firewall", firewall == [], firewall, "all open")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-SPECTRAL-WINDOW-KINETIC-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "derived": {"primary": pd, "independent": ind, "hostile": hostile["derived"], "max_summary_numeric_difference": max_difference, "max_summary_difference_location": max_location}, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED SPECTRAL-WINDOW KINETIC CORRIDOR PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} diff={payload['derived']['max_summary_numeric_difference']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
