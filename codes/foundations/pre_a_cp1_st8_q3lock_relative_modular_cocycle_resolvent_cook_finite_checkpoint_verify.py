#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-385."""

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
SLUG = "pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-manifest.json"
PRIMARY = REPO / f"codes/foundations/{SLUG}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG}_independent.py"
HOSTILE = REPO / f"codes/foundations/{SLUG}_hostile.py"
LEAN = REPO / "verification/lean/Tect/R385.lean"
REGISTRY = REPO / "verification/lean/registry.json"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    return process, json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}


def lake_path() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file(): return path
    found = shutil.which("lake")
    return Path(found) if found else None


def compile_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R385.lean"
    if lake is None: return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R385.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-3000:]}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    agreement = float(manifest["finite_fixture"]["agreement_tolerance"])
    rows: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(rows) < 240: rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001228" and manifest["result_id"] == "R-385" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001228/R-385/false")
    check("sources", all(path.is_file() for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, REGISTRY)), [str(path) for path in (PRIMARY, INDEPENDENT, HOSTILE, LEAN, REGISTRY)], "all present")
    primary_hash, independent_hash = sha256(PRIMARY), sha256(INDEPENDENT)
    check("independent source", primary_hash != independent_hash, [primary_hash, independent_hash], "distinct")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = ["relative_cocycle_composition", "resolvent_difference_identity", "scope_fixture"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "present")
    check("Lean forbidden", not any(token in lean_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), "none", "none")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = [entry for entry in registry["entrypoints"] if entry["path"] == "verification/lean/Tect/R385.lean"]
    check("Lean registry unique", len(entries) == 1, len(entries), 1)
    check("Lean registry hash", entries[0]["sha256"] == sha256(LEAN), entries[0]["sha256"], sha256(LEAN))
    check("Lean declarations", entries[0]["declarations"] == markers, entries[0]["declarations"], markers)

    with tempfile.TemporaryDirectory(prefix="r385-relative-cocycle-") as temporary:
        primary_process, primary = run_child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, Path(temporary) / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        p, i = primary["derived"], independent["derived"]
        exact_fields = ["context_count", "expected_contexts", "prefix_count", "bond_prefix_count", "alpha_row_count", "composition_row_count", "derivative_row_count", "resolvent_row_count", "finite_relative_cocycle_identity_closed", "finite_cocycle_derivative_identity_closed", "finite_cocycle_composition_closed", "finite_resolvent_identity_closed", "finite_two_orientation_state_weighted_rows_closed", "finite_all_prefix_order_sign_beta_seed_grid_closed", "boundary_shell_l1_closed", "phase_local_bkm_estimate_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"]
        for field in exact_fields: check(f"agreement {field}", p[field] == i[field], [p[field], i[field]], "equal")
        numeric_fields = ["alpha_intertwining_residual", "cocycle_residual", "derivative_residual", "resolvent_residual", "unitarity_residual", "commutator_norm", "weighted_left", "weighted_right", "weighted_commutator", "weighted_adjoint_commutator"]
        for field in numeric_fields:
            scale = 1.0 + max(abs(float(p[field])), abs(float(i[field])))
            check(f"agreement {field}", abs(float(p[field]) - float(i[field])) <= agreement * scale, [p[field], i[field]], f"within {agreement} scaled")
        check("volume summary count", len(p["volume_summaries"]) == len(i["volume_summaries"]), [len(p["volume_summaries"]), len(i["volume_summaries"])], "equal")
        summary_numeric = ["dimension", "term_count", "prefix_count", "bond_prefix_count", "context_count"]
        for index, (ps, ins) in enumerate(zip(p["volume_summaries"], i["volume_summaries"])):
            check(f"summary {index} volume", ps["volume"] == ins["volume"], [ps["volume"], ins["volume"]], "equal")
            for field in summary_numeric:
                check(f"summary {index} {field}", ps[field] == ins[field], [ps[field], ins[field]], "equal")
            for field in numeric_fields:
                scale = 1.0 + max(abs(float(ps["maximums"][field])), abs(float(ins["maximums"][field])))
                check(f"summary {index} {field}", abs(float(ps["maximums"][field]) - float(ins["maximums"][field])) <= agreement * scale, [ps["maximums"][field], ins["maximums"][field]], f"within {agreement} scaled")
        check("hostile mutation", hostile["derived"]["wrong_orientation_rejected"] is True and float(hostile["derived"]["wrong_orientation_residual"]) > float(hostile["derived"]["mutation_threshold"]), hostile.get("derived", {}), "reversed product rejected")

    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    open_fields = [field for field in ("boundary_shell_l1_closed", "phase_local_bkm_estimate_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")]
    check("scope firewall", all(primary["derived"][field] is False for field in open_fields), open_fields, "all open")
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-MODULAR-COCYCLE-RESOLVENT-COOK-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": rows, "lean": lean, "derived": {"primary": primary["derived"], "independent": independent["derived"], "hostile": hostile["derived"], "max_primary_independent_numeric_difference": max(abs(float(primary["derived"][field]) - float(independent["derived"][field])) for field in ("alpha_intertwining_residual", "cocycle_residual", "derivative_residual", "resolvent_residual", "unitarity_residual", "commutator_norm", "weighted_left", "weighted_right", "weighted_commutator", "weighted_adjoint_commutator"))}, "provenance": {"manifest_sha256": sha256(MANIFEST), "primary_sha256": primary_hash, "independent_sha256": independent_hash, "hostile_sha256": sha256(HOSTILE), "lean_sha256": sha256(LEAN), "lean_registry_sha256": sha256(REGISTRY)}, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--no-store", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.no_store: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED RELATIVE-MODULAR-COCYCLE-COOK PASS {payload['assertion_count']}/{payload['assertion_count']}; Lean={payload['lean']['status']} diff={payload['derived']['max_primary_independent_numeric_difference']:.3e}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
