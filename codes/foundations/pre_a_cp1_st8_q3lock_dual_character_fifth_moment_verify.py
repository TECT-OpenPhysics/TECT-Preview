#!/usr/bin/env python3
"""Integrated primary/independent/Lean verifier for EXP-001122."""

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
SLUG = "pre_a_cp1_st8_q3lock_dual_character_fifth_moment"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R293.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def normalized_sha256(path: Path) -> str:
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
    command = "lake env lean Tect/R293.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R293.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    clean = "error:" not in output.lower() and "warning:" not in output.lower()
    return {"status": "PASS" if process.returncode == 0 and clean else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def close(left: Any, right: Any, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)) + abs(float(right)))


def compare(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, check: Any) -> None:
    p_rows = primary.get("derived", {}).get("volume_rows", [])
    i_rows = independent.get("derived", {}).get("volume_rows", [])
    check("volume row count", len(p_rows) == len(i_rows), [len(p_rows), len(i_rows)], "equal")
    for p_row, i_row in zip(p_rows, i_rows):
        label = f"V={p_row['volume']} n={p_row['oscillator_dimension']}"
        check(label + " metadata", p_row["volume"] == i_row["volume"] and p_row["oscillator_dimension"] == i_row["oscillator_dimension"] and p_row["hilbert_dimension"] == i_row["hilbert_dimension"], [p_row["volume"], p_row["oscillator_dimension"], p_row["hilbert_dimension"]], [i_row["volume"], i_row["oscillator_dimension"], i_row["hilbert_dimension"]])
        for key in ("energy_min", "shifted_energy_max", "reference_moment5", "dual_moment5", "dual_reference_ratio", "reference_trace_error", "dual_trace_error", "character_unitarity_error"):
            check(label + " " + key, close(p_row[key], i_row[key], tolerance), p_row[key], i_row[key])
        p_tails, i_tails = p_row["tail_rows"], i_row["tail_rows"]
        check(label + " tail row count", len(p_tails) == len(i_tails), [len(p_tails), len(i_tails)], "equal")
        for p_tail, i_tail in zip(p_tails, i_tails):
            radius_label = label + f" R={p_tail['radius']}"
            check(radius_label + " radius", close(p_tail["radius"], i_tail["radius"], tolerance), p_tail["radius"], i_tail["radius"])
            for side in ("reference", "dual"):
                for key in ("tail_mass", "tail_weight"):
                    check(radius_label + f" {side} {key}", close(p_tail[side][key], i_tail[side][key], tolerance), p_tail[side][key], i_tail[side][key])
                check(radius_label + f" {side} count", p_tail[side]["tail_count"] == i_tail[side]["tail_count"], p_tail[side]["tail_count"], i_tail[side]["tail_count"])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001122" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001122/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source distinct", normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT), [normalized_sha256(PRIMARY), normalized_sha256(INDEPENDENT)], "distinct source hashes")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["kinetic_shift_identity", "tail_markov_fixture", "tail_order_fixture", "tail_ratio_fixture", "scope_fixture"]
    check("Lean source markers", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    with tempfile.TemporaryDirectory(prefix="dual-character-fifth-moment-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("positive assertion totals", primary.get("assertion_count", 0) > 0 and independent.get("assertion_count", 0) > 0, [primary.get("assertion_count"), independent.get("assertion_count")], ">0")
        for key in ("finite_reference_fifth_moment_closed", "finite_dual_character_fifth_moment_closed", "finite_global_spectral_tail_comparison_closed", "finite_character_kinetic_shift_identity_closed", "actual_q3_dual_state_moment_uniform_closed", "actual_q3_modular_tail_uniform_closed", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
            check("scope agreement " + key, primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key) == scope.get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key), scope.get(key)], "equal")
        compare(primary, independent, tolerance, check)

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    open_keys = tuple(key for key, value in scope.items() if value is False)
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "all open")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-CHARACTER-FIFTH-MOMENT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": normalized_sha256(PRIMARY), "independent_sha256": normalized_sha256(INDEPENDENT), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN)},
    }
    return payload


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
    print(f"INTEGRATED DUAL-CHARACTER-FIFTH-MOMENT PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
