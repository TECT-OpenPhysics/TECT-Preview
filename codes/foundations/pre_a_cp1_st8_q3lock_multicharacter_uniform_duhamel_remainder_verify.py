#!/usr/bin/env python3
"""Integrated verifier for EXP-001072."""

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
SLUG = "pre-a-cp1-st8-q3lock-multicharacter-uniform-duhamel-remainder"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_uniform_duhamel_remainder.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_uniform_duhamel_remainder_independent.py"
LEAN = REPO / "verification/lean/Tect/R254.lean"
LEAN_ROOT = REPO / "verification/lean"
STATIC = REPO / "strategy/pre-a-cp1-st8-q3lock-multicharacter-static-double-commutator-bound-manifest.json"
FINITE = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-gibbs-isometric-duhamel-remainder-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "integrated.json"
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
    lake = lake_path()
    command = "lake env lean Tect/R254.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R254.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    static = json.loads(STATIC.read_text(encoding="utf-8"))
    finite = json.loads(FINITE.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001072" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001072/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("finite authority", finite["exploration_id"] == "EXP-001066" and "t^2 N_beta(delta_H^2(X))/2" in finite["finite_time_theorem"]["bound"], finite["exploration_id"], "EXP-001066 finite bound")
    check("static authority", static["exploration_id"] == "EXP-001071" and static["scope"]["finite_support_static_multi_character_closed"] is True, static["exploration_id"], "EXP-001071 static multi-character bound")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["remainder_factor_fixture", "remainder_upper_fixture", "remainder_upper_unreduced_fixture", "remainder_upper_small", "time_positive_fixture", "scope_fixture"]
    check("Lean source", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="multicharacter-duhamel-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive totals", primary.get("passed", 0) > 0 and independent.get("passed", 0) > 0, [primary.get("passed"), independent.get("passed")], ">0")
        pderived = primary.get("derived", {})
        iderived = independent.get("derived", {})
        keys = ("support_size", "amplitudes", "time", "static_full_squared_norm_upper", "remainder_factor", "remainder_squared_upper", "finite_support_remainder_uniform_closed", "product_core_density_closed", "actual_q3_factorial_history_proved")
        for key in keys:
            check(f"lane agreement {key}", str(pderived.get(key)) == str(iderived.get(key)), [pderived.get(key), iderived.get(key)], "equal")
        expected = manifest["finite_fixture"]
        for key, derived_key in (("time", "time"), ("static_full_squared_norm_upper", "static_full_squared_norm_upper"), ("derived_remainder_factor", "remainder_factor"), ("derived_remainder_squared_upper", "remainder_squared_upper")):
            check(f"fixture {key}", str(pderived.get(derived_key)) == str(expected[key]), pderived.get(derived_key), expected[key])

    open_keys = ("force_history_uniform_closed", "full_actual_q3_double_commutator_uniform_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_os_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R254.lean"} if args.skip_lean else lean_run()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-MULTICHARACTER-UNIFORM-DUHAMEL-REMAINDER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "lean": lean, "boundary": scope, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "static_manifest_sha256": sha256(STATIC), "finite_manifest_sha256": sha256(FINITE)}}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED MULTICHARACTER-DUHAMEL PASS {len(rows)}/{len(rows)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
