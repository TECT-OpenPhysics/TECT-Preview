#!/usr/bin/env python3
"""Integrated verifier for EXP-001105."""

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
SLUG = "pre_a_cp1_st8_q3lock_harmonic_compression_boundary_leakage"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
LEAN = REPO / "verification/lean/Tect/R279.lean"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-integrated-{SLUG}" / "integrated.json"
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
    command = "lake env lean Tect/R279.lean"
    lake = lake_path()
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R279.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def close(left: Any, right: Any, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)) + abs(float(right)))


def compare(primary: dict[str, Any], independent: dict[str, Any], tolerance: float, check: Any) -> None:
    p_rows = primary.get("derived", {}).get("n_rows", [])
    i_rows = independent.get("derived", {}).get("n_rows", [])
    check("n row count", len(p_rows) == len(i_rows), [len(p_rows), len(i_rows)], "equal")
    for p_row, i_row in zip(p_rows, i_rows):
        label = f"n={p_row['n']}"
        check(label + " metadata", p_row["n"] == i_row["n"] and p_row["ambient_dimension"] == i_row["ambient_dimension"], [p_row["n"], p_row["ambient_dimension"]], [i_row["n"], i_row["ambient_dimension"]])
        check(label + " degree count", len(p_row["degrees"]) == len(i_row["degrees"]), len(p_row["degrees"]), len(i_row["degrees"]))
        for p_degree, i_degree in zip(p_row["degrees"], i_row["degrees"]):
            dlabel = label + f" d={p_degree['degree']}"
            check(dlabel + " degree", p_degree["degree"] == i_degree["degree"], p_degree["degree"], i_degree["degree"])
            check(dlabel + " conditional bound", close(p_degree["conditional_state_weighted_bound"], i_degree["conditional_state_weighted_bound"], tolerance), p_degree["conditional_state_weighted_bound"], i_degree["conditional_state_weighted_bound"])
            for operator in ("q", "p"):
                p_defect = p_degree["defects"][operator]
                i_defect = i_degree["defects"][operator]
                check(dlabel + f" {operator} support", close(p_defect["support_residual"], i_defect["support_residual"], tolerance), p_defect["support_residual"], i_defect["support_residual"])
                check(dlabel + f" {operator} norm", close(p_defect["norm"], i_defect["norm"], tolerance), p_defect["norm"], i_defect["norm"])
                check(dlabel + f" {operator} envelope", close(p_defect["derived_envelope"], i_defect["derived_envelope"], tolerance), p_defect["derived_envelope"], i_defect["derived_envelope"])
        for key in ("support_residual", "norm", "derived_envelope", "conditional_state_weighted_bound"):
            check(label + " onsite " + key, close(p_row["onsite"][key], i_row["onsite"][key], tolerance), p_row["onsite"][key], i_row["onsite"][key])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["exploration_id"] == "EXP-001105" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001105/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("source distinct", normalized_sha256(PRIMARY) != normalized_sha256(INDEPENDENT), [normalized_sha256(PRIMARY), normalized_sha256(INDEPENDENT)], "different source hashes")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    markers = ["fifth_moment_to_weighted_top_tail", "fifth_moment_fixture"]
    check("Lean source markers", LEAN.is_file() and all(marker in lean_source for marker in markers), markers, "present")
    check("Lean forbidden tokens", not any(token in lean_source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    with tempfile.TemporaryDirectory(prefix="harmonic-compression-boundary-") as temporary:
        p_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        i_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", p_process.returncode == 0 and primary.get("verdict") == "PASS", p_process.stdout + p_process.stderr, "PASS")
        check("independent child", i_process.returncode == 0 and independent.get("verdict") == "PASS", i_process.stdout + i_process.stderr, "PASS")
        compare(primary, independent, tolerance, check)
    open_keys = ("operator_norm_convergence_closed", "q3_energy_to_number_form_domination_closed", "q3_gibbs_weighted_boundary_uniformity_closed", "q3_evolved_history_weighted_boundary_uniformity_closed", "source_volume_orientation_history_uniform_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")
    check("finite conditional scope", scope["finite_path_support_closed"] and scope["finite_norm_envelope_closed"] and scope["conditional_state_weighted_boundary_bound_closed"], scope, "finite PASS")
    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": "PA-CP1-ST8-Q3LOCK-HARMONIC-COMPRESSION-BOUNDARY-LEAKAGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "lean": lean,
        "boundary": scope,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"primary_sha256": normalized_sha256(PRIMARY), "independent_sha256": normalized_sha256(INDEPENDENT), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN)}
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
    print(f"INTEGRATED HARMONIC-COMPRESSION-BOUNDARY-LEAKAGE PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
