#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-458."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-m5-isolated-node-equation-level-audit-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_m5_isolated_node_equation_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_m5_isolated_node_equation_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_m5_isolated_node_equation_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R458.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-integrated-pre_a_m5_isolated_node_equation_level_audit/integrated.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lean_run() -> dict[str, Any]:
    if not LAKE.is_file():
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R458.lean", "output": "pinned direct lake executable not found"}
    process = subprocess.run(
        [str(LAKE), "env", "lean", "Tect/R458.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "command": "lake env lean Tect/R458.lean",
        "returncode": process.returncode,
        "output": output[-3000:],
    }


def run(output: Path = DEFAULT_OUTPUT, skip_lean: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]]
        == ["R-458", "EXP-001331", "T-054", False, "T0", "M5_EQUATION_LEVEL_AUDITED_NOT_ADMITTED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]],
        "R-458/EXP-001331/T-054/false/T0/status",
        "provenance",
    )
    check("method preservation", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    finite_keys = (
        "clifford_relations_closed",
        "symbol_hermiticity_closed",
        "symbol_square_identity_closed",
        "isolated_node_grid_closed",
        "chiral_anticommutation_closed",
        "chiral_even_quadratic_closed",
        "observable_symmetry_closed",
        "local_dispersion_leading_closed",
        "finite_hamiltonian_coercivity_closed",
        "flow_equivariance_conditional",
        "finite_flow_conditional_closed",
    )
    check("finite scope flags", all(manifest["scope"][key] is True for key in finite_keys), manifest["scope"], "finite flags true", "finite-scope")
    promotion_keys = (
        "source_owner_admitted",
        "candidate_admitted",
        "f_reg_measured",
        "f_lim_closed",
        "f_eff_closed",
        "f_obs_closed",
        "continuum_closed",
        "qft_identity_closed",
        "yang_mills_identity_closed",
        "physical_empty_closed",
        "pre_a_closed",
        "sector_a_closed",
        "c6_closed",
    )
    check("promotion firewall", all(manifest["scope"][key] is False for key in promotion_keys), manifest["scope"], "all promotion flags false", "promotion-firewall")
    parent = ROOT / manifest["parent_manifest"]["path"]
    check("parent hash", parent.is_file() and sha(parent) == manifest["parent_manifest"]["sha256"], sha(parent) if parent.is_file() else None, manifest["parent_manifest"]["sha256"], "provenance")
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    declarations = manifest["lean_crosscheck"]["declarations"]
    check("Lean markers", all(re.search(rf"(?m)^\s*theorem\s+{re.escape(marker)}\b", source) for marker in declarations), declarations, "all declarations present", "Lean")
    check("Lean forbidden tokens", not any(re.search(rf"\b{re.escape(token)}\b", source) for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "forbidden absent", "Lean")
    for name, item in manifest["files"].items():
        if name == "parent_manifest":
            continue
        artifact = ROOT / item["path"]
        check(f"artifact {name}", artifact.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(artifact) == item["sha256"], sha(artifact) if artifact.is_file() else None, item["sha256"], "provenance")

    with tempfile.TemporaryDirectory(prefix="r458-integrated-") as directory:
        temporary = Path(directory)
        primary_process, primary = child(PRIMARY, temporary / "primary.json")
        independent_process, independent = child(INDEPENDENT, temporary / "independent.json")
        hostile_process, hostile = child(HOSTILE, temporary / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == manifest["status"], primary_process.stdout + primary_process.stderr, manifest["status"], "children")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == manifest["status"], independent_process.stdout + independent_process.stderr, manifest["status"], "children")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "HOSTILE_MUTATIONS_REJECTED", "children")
        common = (
            "mode_count",
            "nonorigin_mode_count",
            "clifford_matrix_checks",
            "symbol_matrix_checks",
            "taylor_checks",
            "observable_symmetry_checks",
            "coercivity_checks",
            "clifford_relations_closed",
            "symbol_hermiticity_closed",
            "symbol_square_identity_closed",
            "isolated_node_grid_closed",
            "chiral_anticommutation_closed",
            "chiral_even_quadratic_closed",
            "observable_symmetry_closed",
            "local_dispersion_leading_closed",
            "finite_hamiltonian_coercivity_closed",
            "flow_equivariance_conditional",
            "finite_flow_conditional_closed",
            "source_owner_admitted",
            "candidate_admitted",
            "physical_identity",
            "continuum_closed",
            "pre_a_closed",
            "sector_a_closed",
        )
        for key in common:
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "cross-check")
        check("primary minimum assertions", primary.get("assertion_count", 0) >= manifest["test_oracles"]["primary_minimum_assertions"], primary.get("assertion_count"), manifest["test_oracles"]["primary_minimum_assertions"], "coverage")
        check("independent minimum assertions", independent.get("assertion_count", 0) >= manifest["test_oracles"]["independent_minimum_assertions"], independent.get("assertion_count"), manifest["test_oracles"]["independent_minimum_assertions"], "coverage")
        check("hostile mutation count", hostile.get("mutation_count") == manifest["test_oracles"]["hostile_mutation_count"] and len(hostile.get("mutations_rejected", [])) == manifest["test_oracles"]["hostile_mutation_count"], hostile.get("mutation_count"), manifest["test_oracles"]["hostile_mutation_count"], "hostile")
        check("independent does not import primary", "pre_a_m5_isolated_node_equation_audit.py" not in INDEPENDENT.read_text(encoding="utf-8"), True, "no primary import", "independence")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R458.lean"} if skip_lean else lean_run()
    check("Lean run", skip_lean or lean["status"] == "PASS", lean, "PASS", "Lean")
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "lean": lean,
        "source_hashes": {"manifest": sha(MANIFEST), "primary": sha(PRIMARY), "independent": sha(INDEPENDENT), "hostile": sha(HOSTILE), "integrated": sha(Path(__file__)), "lean": sha(LEAN)},
        "derived": {
            "clifford_relations_closed": True,
            "symbol_hermiticity_closed": True,
            "symbol_square_identity_closed": True,
            "isolated_node_grid_closed": True,
            "chiral_anticommutation_closed": True,
            "chiral_even_quadratic_closed": True,
            "observable_symmetry_closed": True,
            "local_dispersion_leading_closed": True,
            "finite_hamiltonian_coercivity_closed": True,
            "flow_equivariance_conditional": True,
            "finite_flow_conditional_closed": True,
            "primary_assertions": primary.get("assertion_count"),
            "independent_assertions": independent.get("assertion_count"),
            "hostile_mutations_rejected": hostile.get("mutation_count"),
            "source_owner_admitted": False,
            "candidate_admitted": False,
            "physical_identity": False,
            "continuum_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    save(output, payload)
    print(f"R-458 INTEGRATED PASS {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output, skip_lean=args.skip_lean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
