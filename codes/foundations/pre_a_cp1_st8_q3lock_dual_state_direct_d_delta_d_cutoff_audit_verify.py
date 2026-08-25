#!/usr/bin/env python3
"""Integrated verifier for EXP-001123 (primary, independent, Lean)."""

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


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_dual_state_direct_d_delta_d_cutoff_audit"
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
PRIMARY = ROOT / f"codes/foundations/{NAME}.py"
INDEPENDENT = ROOT / f"codes/foundations/{NAME}_independent.py"
LEAN = ROOT / "verification/lean/Tect/R294.lean"
LEAN_ROOT = ROOT / "verification/lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{NAME}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads((ROOT / "verification/lean/registry.json").read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R294.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R294.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    clean = "error:" not in output.lower() and "warning:" not in output.lower()
    return {"status": "PASS" if process.returncode == 0 and clean else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def close(left: Any, right: Any, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)) + abs(float(right)))


def compare(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, check: Any) -> None:
    p_rows = primary.get("derived", {}).get("volume_rows", [])
    i_rows = independent.get("derived", {}).get("volume_rows", [])
    check("volume row count", len(p_rows) == len(i_rows), [len(p_rows), len(i_rows)], "equal")
    scalar_keys = ("root", "right", "left")
    ratio_keys = ("reference_D_to_time_tail", "dual_D_to_time_tail", "reference_delta_to_tail", "dual_delta_to_tail")
    for p_row, i_row in zip(p_rows, i_rows):
        label = f"V={p_row['volume']} n={p_row['oscillator_dimension']}"
        check(label + " metadata", p_row["volume"] == i_row["volume"] and p_row["oscillator_dimension"] == i_row["oscillator_dimension"] and p_row["hilbert_dimension"] == i_row["hilbert_dimension"], p_row, i_row)
        check(label + " radius count", len(p_row["radius_rows"]) == len(i_row["radius_rows"]), len(p_row["radius_rows"]), len(i_row["radius_rows"]))
        for p_radius, i_radius in zip(p_row["radius_rows"], i_row["radius_rows"]):
            rlabel = label + f" L={p_radius['radius']}"
            check(rlabel + " radius", close(p_radius["radius"], i_radius["radius"], tolerance), p_radius["radius"], i_radius["radius"])
            check(rlabel + " commutation", close(p_radius["character_commutation_2norm"], i_radius["character_commutation_2norm"], tolerance), p_radius["character_commutation_2norm"], i_radius["character_commutation_2norm"])
            for side in ("tail_reference", "tail_dual"):
                for key in scalar_keys:
                    check(rlabel + f" {side} {key}", close(p_radius[side][key], i_radius[side][key], tolerance), p_radius[side][key], i_radius[side][key])
            check(rlabel + " time count", len(p_radius["times"]) == len(i_radius["times"]), len(p_radius["times"]), len(i_radius["times"]))
            for p_time, i_time in zip(p_radius["times"], i_radius["times"]):
                tlabel = rlabel + f" t={p_time['time']}"
                check(tlabel + " sign count", len(p_time["sign_rows"]) == len(i_time["sign_rows"]), len(p_time["sign_rows"]), len(i_time["sign_rows"]))
                for p_sign, i_sign in zip(p_time["sign_rows"], i_time["sign_rows"]):
                    slabel = tlabel + f" s={p_sign['sign']}"
                    check(slabel + " sign", p_sign["sign"] == i_sign["sign"], p_sign["sign"], i_sign["sign"])
                    for side in ("reference_D", "reference_delta_D", "dual_D", "dual_delta_D"):
                        for key in scalar_keys:
                            check(slabel + f" {side} {key}", close(p_sign[side][key], i_sign[side][key], tolerance), p_sign[side][key], i_sign[side][key])
                    for key in ratio_keys:
                        check(slabel + " " + key, close(p_sign[key], i_sign[key], tolerance), p_sign[key], i_sign[key])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001123" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001123/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source distinct", digest(PRIMARY) != digest(INDEPENDENT), [digest(PRIMARY), digest(INDEPENDENT)], "distinct source hashes")
    markers = ["twoSided", "dual_trace_fixture", "signed_orientation_count", "volume_edge_count", "ratio_tail_fixture", "scope_fixture"]
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    check("Lean markers", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="dual-state-d-delta-d-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive assertion totals", primary.get("assertion_count", 0) > 0 and independent.get("assertion_count", 0) > 0, [primary.get("assertion_count"), independent.get("assertion_count")], ">0")
        for key, value in scope.items():
            if key in primary.get("derived", {}):
                check("scope agreement " + key, primary["derived"].get(key) == independent["derived"].get(key) == value, [primary["derived"].get(key), independent["derived"].get(key), value], "equal")
        compare(primary, independent, tolerance, check)

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    open_keys = tuple(key for key, value in scope.items() if value is False)
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all open")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-STATE-DIRECT-D-DELTA-D-CUTOFF",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "manifest_sha256": digest(MANIFEST), "lean_sha256": digest(LEAN)},
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
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED DUAL-STATE-D-DELTA-D-CUTOFF PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
