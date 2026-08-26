#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001185."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-modular-multiplier-bound"
AUDIT = "PA-CP1-ST8-Q3LOCK-FINITE-MODULAR-MULTIPLIER-BOUND"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R344.lean"
LEAN_ROOT = REPO / "verification" / "lean"
REGISTRY = LEAN_ROOT / "registry.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
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
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def run_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R344.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R344.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def compare_rows(primary: list[dict[str, Any]], independent: list[dict[str, Any]], tolerance: float) -> tuple[bool, str]:
    key_fields = ("volume", "beta", "radius", "kind", "orientation", "interpolation", "time")
    numeric_fields = ("base_four_leg_norm", "commutator_four_leg_norm", "envelope_four_leg_norm", "envelope_ratio", "gamma", "tail_operator_norm", "source_commutator_norm")
    left = {tuple(row[field] for field in key_fields): row for row in primary}
    right = {tuple(row[field] for field in key_fields): row for row in independent}
    if len(left) != len(primary) or len(right) != len(independent):
        return False, "duplicate row key"
    if set(left) != set(right):
        return False, f"row keys differ: {sorted(set(left) ^ set(right))}"
    for key in sorted(left):
        for field in numeric_fields:
            first, second = float(left[key]["values"][field]), float(right[key]["values"][field])
            if abs(first - second) > tolerance + tolerance * max(1.0, abs(first), abs(second)):
                return False, f"{key} {field}: {first} != {second}"
    return True, "all finite rows agree within tolerance"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001185", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001185/T-054/false")
    check("scope firewall", scope["finite_modular_multiplier_envelope_closed"] and scope["finite_component_envelopes_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["modular_domain_transfer_closed"] and not scope["pre_a_closed"], scope, "finite multiplier envelope only")
    expected_rows = len(fixture["volume_values"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]) * 2 * len(fixture["orientation_values"]) * len(fixture["interpolation_values"]) * len(fixture["time_values"])
    check("fixture", fixture["volume_values"] == [2, 4, 6] and fixture["oscillator_dimension"] == 3 and expected_rows > 0, fixture, "declared finite Q3 grid")
    with tempfile.TemporaryDirectory(prefix="finite-modular-multiplier-bound-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("audit identity", primary.get("audit_id") == independent.get("audit_id") == AUDIT, [primary.get("audit_id"), independent.get("audit_id")], AUDIT)
        check("scope agreement", primary.get("scope") == independent.get("scope"), primary.get("scope"), "identical scope")
        row_ok, row_message = compare_rows(primary.get("rows", []), independent.get("rows", []), float(fixture["finite_tolerance"]))
        check("row agreement", row_ok, row_message, "all rows")
        check("coverage", len(primary.get("rows", [])) == expected_rows and len(independent.get("rows", [])) == expected_rows, [len(primary.get("rows", [])), len(independent.get("rows", []))], expected_rows)
        for field in ("row_count", "max_envelope_ratio", "min_envelope_ratio", "local_gamma_min", "local_gamma_max", "full_gamma_min", "full_gamma_max"):
            first, second = float(primary.get("derived", {}).get(field)), float(independent.get("derived", {}).get(field))
            check(f"derived {field}", abs(first - second) <= float(fixture["finite_tolerance"]) * max(1.0, abs(first), abs(second)) + float(fixture["finite_tolerance"]), [first, second], "agree within tolerance")
        check("finite witness", primary.get("derived", {}).get("max_envelope_ratio", -1.0) >= 0.0, primary.get("derived", {}).get("max_envelope_ratio"), ">=0")
    lean = run_lean()
    check("Lean R344", lean["status"] == "PASS", lean, "PASS")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R344.lean"), None)
    check("registry R344", entry is not None and entry.get("sha256") == sha256(LEAN) and entry.get("declarations") == ["four_component_envelope", "max_pair_sum_bound"], entry, "registered LF hash and declarations")
    downstream = ("source_volume_cutoff_beta_uniform_closed", "modular_domain_transfer_closed", "unbounded_common_core_closed", "direct_d_delta_d_cauchy_closed", "common_os_hilbert_carrier_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("downstream QFT firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": AUDIT, "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "derived": primary.get("derived"), "summary_rows": primary.get("summary_rows"), "rows": primary.get("rows"), "scope": scope, "boundary": manifest["boundary"], "lean": lean, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "registry_sha256": sha256(REGISTRY)}}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED FINITE-MODULAR-MULTIPLIER-BOUND PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
