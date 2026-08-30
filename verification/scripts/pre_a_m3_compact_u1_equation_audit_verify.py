#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-457."""

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
MANIFEST = ROOT / "strategy/pre-a-m3-compact-u1-equation-level-audit-manifest.json"
PRIMARY = ROOT / "verification/scripts/pre_a_m3_compact_u1_equation_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_m3_compact_u1_equation_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_m3_compact_u1_equation_audit_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R457.lean"
LEAN_ROOT = ROOT / "verification/lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))
DEFAULT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-integrated-pre_a_m3_compact_u1_equation_level_audit/integrated.json"
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
        return {"status": "UNAVAILABLE", "command": "lake env lean Tect/R457.lean", "output": "pinned direct lake executable not found"}
    process = subprocess.run(
        [str(LAKE), "env", "lean", "Tect/R457.lean"],
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
        "command": "lake env lean Tect/R457.lean",
        "returncode": process.returncode,
        "output": output[-3000:],
    }


def run(output: Path = DEFAULT, skip_lean: bool = False) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]]
        == ["R-457", "EXP-001330", "T-054", False, "T0", "M3_EQUATION_LEVEL_AUDITED_NOT_ADMITTED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"], manifest["status"]],
        "R-457/EXP-001330/T-054/false/T0/status",
        "provenance",
    )
    check("method preservation", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    check(
        "finite scope firewall",
        all(manifest["scope"][key] is True for key in ("equation_charge_audit_closed", "gauge_invariant_hamiltonian_terms_closed", "observable_map_neutrality_closed", "gauss_neutrality_identity_closed", "poisson_energy_identity_closed", "coercivity_completion_identity_closed", "finite_flow_conditional_closed"))
        and all(manifest["scope"][key] is False for key in ("source_owner_admitted", "candidate_admitted", "f_lim_closed", "f_eff_closed", "f_obs_closed", "continuum_closed", "qft_identity_closed", "yang_mills_identity_closed", "physical_empty_closed", "pre_a_closed", "sector_a_closed", "c6_closed")),
        manifest["scope"],
        "finite equations closed; all admission and physical flags false",
        "scope",
    )
    check("parent manifest exists", (ROOT / manifest["parent_manifest"]["path"]).is_file(), manifest["parent_manifest"]["path"], True, "provenance")
    check(
        "parent manifest hash",
        manifest["files"]["parent_manifest"]["sha256"] != "TO_BE_FILLED"
        and sha(ROOT / manifest["parent_manifest"]["path"])
        == manifest["files"]["parent_manifest"]["sha256"],
        sha(ROOT / manifest["parent_manifest"]["path"]),
        manifest["files"]["parent_manifest"]["sha256"],
        "provenance",
    )
    check("Lean source", LEAN.is_file(), str(LEAN), True, "Lean")
    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    declarations = manifest["lean_crosscheck"]["declarations"]
    check("Lean markers", all(re.search(rf"(?m)^\s*theorem\s+{re.escape(marker)}\b", lean_source) for marker in declarations), declarations, "all theorem declarations present", "Lean")
    check("Lean forbidden tokens", not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "forbidden absent", "Lean")

    for name, item in manifest["files"].items():
        if name == "parent_manifest":
            continue
        artifact = ROOT / item["path"]
        check(f"artifact {name}", artifact.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(artifact) == item["sha256"], sha(artifact) if artifact.is_file() else None, item["sha256"], "provenance")

    with tempfile.TemporaryDirectory(prefix="r457-integrated-") as directory:
        temp = Path(directory)
        primary_process, primary = child(PRIMARY, temp / "primary.json")
        independent_process, independent = child(INDEPENDENT, temp / "independent.json")
        hostile_process, hostile = child(HOSTILE, temp / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == manifest["status"], primary_process.stdout + primary_process.stderr, manifest["status"], "children")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == manifest["status"], independent_process.stdout + independent_process.stderr, manifest["status"], "children")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", hostile_process.stdout + hostile_process.stderr, "HOSTILE_MUTATIONS_REJECTED", "children")
        keys = (
            "lattice_sizes",
            "sites_checked",
            "plaquette_checks",
            "covariant_checks",
            "observable_checks",
            "gauss_checks",
            "coercivity_rows",
            "poisson_self_bracket_rows",
            "equation_charge_audit_closed",
            "gauge_invariant_hamiltonian_terms_closed",
            "observable_map_neutrality_closed",
            "gauss_neutrality_identity_closed",
            "poisson_energy_identity_closed",
            "coercivity_completion_identity_closed",
            "finite_flow_conditional_closed",
            "source_owner_admitted",
            "candidate_admitted",
            "physical_identity",
            "continuum_closed",
            "pre_a_closed",
            "sector_a_closed",
        )
        for key in keys:
            check(f"lane agreement {key}", primary.get("derived", {}).get(key) == independent.get("derived", {}).get(key), [primary.get("derived", {}).get(key), independent.get("derived", {}).get(key)], "equal", "cross-check")
        check("primary minimum assertions", primary.get("assertion_count", 0) >= manifest["test_oracles"]["primary_minimum_assertions"], primary.get("assertion_count"), manifest["test_oracles"]["primary_minimum_assertions"], "coverage")
        check("independent minimum assertions", independent.get("assertion_count", 0) >= manifest["test_oracles"]["independent_minimum_assertions"], independent.get("assertion_count"), manifest["test_oracles"]["independent_minimum_assertions"], "coverage")
        check("hostile mutation count", hostile.get("mutation_count") == manifest["test_oracles"]["hostile_mutation_count"] and len(hostile.get("mutations_rejected", [])) == manifest["test_oracles"]["hostile_mutation_count"], hostile.get("mutation_count"), manifest["test_oracles"]["hostile_mutation_count"], "hostile")
        check("independent does not import primary", "pre_a_m3_compact_u1_equation_audit.py" not in INDEPENDENT.read_text(encoding="utf-8"), True, "no primary import", "independence")

    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R457.lean"} if skip_lean else lean_run()
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
            "equation_charge_audit_closed": True,
            "gauge_invariant_hamiltonian_terms_closed": True,
            "observable_map_neutrality_closed": True,
            "gauss_neutrality_identity_closed": True,
            "gauss_surface_preservation": "CONDITIONAL_ON_DECLARED_CANONICAL_GENERATOR",
            "poisson_energy_identity_closed": True,
            "coercivity_completion_identity_closed": True,
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
    print(f"R-457 INTEGRATED PASS {len(checks)}/{len(checks)} Lean={lean['status']}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--skip-lean", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output, skip_lean=args.skip_lean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
