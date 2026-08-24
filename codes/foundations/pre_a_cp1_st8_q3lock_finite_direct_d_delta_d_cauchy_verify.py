#!/usr/bin/env python3
"""Integrated verifier for EXP-001085."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-direct-d-delta-d-cauchy"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_finite_direct_d_delta_d_cauchy.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_finite_direct_d_delta_d_cauchy_independent.py"
LEAN = REPO / "verification/lean/Tect/R267.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def lake_path() -> Path | None:
    registry = json.loads((REPO / "verification/lean/registry.json").read_text(encoding="utf-8")); encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file(): return candidate / name
    found = shutil.which("lake"); return Path(found) if found else None


def lean_run() -> dict[str, Any]:
    command = "lake env lean Tect/R267.lean"; lake = lake_path()
    if lake is None: return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R267.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False); output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False); payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}; return process, payload


def close(a: Any, b: Any, tolerance: float = 1e-7) -> bool:
    return abs(float(a) - float(b)) <= tolerance * (1.0 + abs(float(a)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); scope = manifest["scope"]; rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    check("identity", manifest["exploration_id"] == "EXP-001085" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001085/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""; markers = ["direct_fixture", "modular_fixture", "zero_tail_fixture", "orientation_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    with tempfile.TemporaryDirectory(prefix="finite-direct-d-") as temporary:
        p_process, primary = child(PRIMARY, Path(temporary) / "primary.json"); i_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", p_process.returncode == 0 and primary.get("verdict") == "PASS", p_process.stdout + p_process.stderr, "PASS")
        check("independent child", i_process.returncode == 0 and independent.get("verdict") == "PASS", i_process.stdout + i_process.stderr, "PASS")
        p_rows = primary.get("derived", {}).get("volume_rows", []); i_rows = independent.get("derived", {}).get("volume_rows", [])
        check("volume sequence", [x.get("volume") for x in p_rows] == [x.get("volume") for x in i_rows] == manifest["finite_fixture"]["volume_values"], [[x.get("volume") for x in p_rows], [x.get("volume") for x in i_rows]], manifest["finite_fixture"]["volume_values"])
        for p_volume, i_volume in zip(p_rows, i_rows):
            check(f"V={p_volume['volume']} dimensions", p_volume["dimension"] == i_volume["dimension"], [p_volume["dimension"], i_volume["dimension"]], "equal")
            for p_radius, i_radius in zip(p_volume["radius_rows"], i_volume["radius_rows"]):
                check(f"V={p_volume['volume']} L={p_radius['radius']} tail agreement", close(p_radius["tail_operator_norm"], i_radius["tail_operator_norm"]), [p_radius["tail_operator_norm"], i_radius["tail_operator_norm"]], "within 1e-7 relative")
                for p_time, i_time in zip(p_radius["times"], i_radius["times"]):
                    check(f"V={p_volume['volume']} L={p_radius['radius']} t={p_time['time']} time", close(p_time["time"], i_time["time"]), [p_time["time"], i_time["time"]], "equal")
                    for sign in ("-1", "1"):
                        p_values, i_values = p_time["orientations"][sign], i_time["orientations"][sign]
                        check(f"V={p_volume['volume']} L={p_radius['radius']} t={p_time['time']} sign={sign}", all(close(p_values[key], i_values[key]) for key in ("D_norm", "delta_D_norm", "matrix_norm")), [p_values, i_values], "within 1e-7 relative")
    open_keys = ("volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    check("finite scope", scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and scope["finite_two_orientation_difference_closed"], scope, "PASS")
    lean = lean_run(); check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-DIRECT-D-DELTA-D-CAUCHY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); parser.add_argument("--skip-lean", action="store_true"); args = parser.parse_args()
    if args.skip_lean: raise SystemExit("skip-lean is not allowed for the integrated proof checkpoint")
    payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-DIRECT-D-DELTA-D PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
