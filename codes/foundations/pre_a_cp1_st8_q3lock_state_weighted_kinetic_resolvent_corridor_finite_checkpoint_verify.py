#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-388."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-kinetic-resolvent-corridor-finite-checkpoint-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
HOSTILE = REPO / f"codes/foundations/{SLUG}_hostile.py"
LEAN = REPO / "verification/lean/Tect/R388.lean"
REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", shutil.which("python") or "python"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def pinned_lake() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def compile_lean() -> dict[str, Any]:
    lake = pinned_lake()
    command = "lake env lean Tect/R388.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R388.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001231" and manifest["result_id"] == "R-388" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001231/R-388/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, REGISTRY)), "all present", "all present")
    check("independent source", digest(PRIMARY) != digest(INDEPENDENT), [digest(PRIMARY), digest(INDEPENDENT)], "distinct")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = ["jacobi_reduction", "kinetic_coordinate_isolation", "scope_fixture"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R388.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == digest(LEAN), entries[0]["sha256"], digest(LEAN))
    check("Lean declarations", entries[0]["declarations"] == markers, entries[0]["declarations"], markers)

    with tempfile.TemporaryDirectory(prefix="r388-") as temporary:
        temp = Path(temporary)
        primary_process, primary = child(PRIMARY, temp / "primary.json")
        independent_process, independent = child(INDEPENDENT, temp / "independent.json")
        hostile_process, hostile = child(HOSTILE, temp / "hostile.json")
    check("primary child", primary_process.returncode == 0 and "PASS" in primary_process.stdout, primary_process.stdout[-3000:], "PASS")
    check("independent child", independent_process.returncode == 0 and "PASS" in independent_process.stdout, independent_process.stdout[-3000:], "PASS")
    check("hostile child", hostile_process.returncode == 0 and "CAUGHT" in hostile_process.stdout, hostile_process.stdout[-3000:], "CAUGHT")
    pd, indep = primary["derived"], independent["derived"]
    agreement_tolerance = float(manifest["finite_fixture"]["agreement_tolerance"])
    for field in ("operator_norm", "weighted_norm"):
        check(f"agreement maximum {field}", abs(float(pd["maximums"][field]) - float(indep["maximums"][field])) <= agreement_tolerance, [pd["maximums"][field], indep["maximums"][field]], f"within {agreement_tolerance}")
    check("agreement growth", abs(float(pd["operator_growth_ratio"]) - float(indep["operator_growth_ratio"])) <= agreement_tolerance, [pd["operator_growth_ratio"], indep["operator_growth_ratio"]], f"within {agreement_tolerance}")
    check("agreement late ratios", all(abs(float(pd["late_ratios"][key]) - float(indep["late_ratios"][key])) <= agreement_tolerance for key in pd["late_ratios"]), [pd["late_ratios"], indep["late_ratios"]], f"within {agreement_tolerance}")
    for field in ("seed_rows", "weighted_rows", "cutoff_dimensions"):
        check(f"agreement {field}", pd[field] == indep[field], [pd[field], indep[field]], "equal")
    for field in ("finite_operator_growth_stress_closed", "finite_gibbs_weighted_corridor_closed", "finite_beta_eta_corridor_split_closed"):
        check(f"scope {field}", pd[field] is True and indep[field] is True, [pd[field], indep[field]], "true")
    for field in ("operator_norm_uniformity_closed", "beta_uniformity_closed", "eta_uniformity_closed", "phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope {field}", pd[field] is False and indep[field] is False, [pd[field], indep[field]], "false")
    check("hostile rejected", hostile["derived"]["wrong_orientation_rejected"] is True, hostile["derived"], "momentum resolvent rejected")
    check("hostile separation", float(hostile["derived"]["wrong_momentum_commutator_min"]) > float(manifest["finite_fixture"]["hostile_threshold"]), hostile["derived"]["wrong_momentum_commutator_min"], f">{manifest['finite_fixture']['hostile_threshold']}")
    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    firewall = [field for field in ("operator_norm_uniformity_closed", "beta_uniformity_closed", "eta_uniformity_closed", "phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed") if pd[field]]
    check("scope firewall", firewall == [], firewall, "all open")
    numeric_difference = max(abs(float(pd["maximums"][field]) - float(indep["maximums"][field])) for field in ("operator_norm", "weighted_norm"))
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-KINETIC-RESOLVENT-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": rows, "lean": lean, "derived": {"primary": pd, "independent": indep, "hostile": hostile["derived"], "max_primary_independent_numeric_difference": numeric_difference}, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED STATE-WEIGHTED KINETIC-RESOLVENT CORRIDOR PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} diff={payload['derived']['max_primary_independent_numeric_difference']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
