#!/usr/bin/env python3
"""Integrated verifier for the R-425 expanded finite Schur stress."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_expanded_grid_schur_stress.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_expanded_grid_schur_stress_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_expanded_grid_schur_stress_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R425.lean"
SLUG = "expanded_grid_schur_stress"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-integrated-{SLUG}" / "integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--4.32.1/bin/lake.exe"))


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-425" and manifest["exploration_id"] == "EXP-001270" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-425/EXP-001270/false", "provenance")
    check("scope firewall", all(value is False for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in {"finite_expanded_grid_assembly_closed", "finite_harmonic_coarse_schur_closed", "finite_residual_reuse_closed", "finite_combined_lower_envelope_closed", "finite_coverage_boundary_recorded"}), "all promoted flags false", "no uniform or physical flag", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-425 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean source policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = run_command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lake = LAKE if LAKE.is_file() else Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lake.exe"
    lean = run_command([str(lake), "env", "lean", "Tect/R425.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1800:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    derived = primary["derived"]
    expected_systems = sum(len(item["cutoff_dimensions"]) for item in manifest["finite_fixture"]["q3_pairs"])
    check("primary result identity", primary["result_id"] == "R-425" and primary["verdict"] == "PASS", [primary["result_id"], primary["verdict"]], "R-425/PASS", "outputs")
    check("primary expanded coverage", derived["system_count"] == expected_systems and derived["conditional_row_count"] > 0 and derived["eligible_row_count"] == derived["combined_row_count"] and derived["eligible_row_count"] > 0, [derived["system_count"], derived["conditional_row_count"], derived["eligible_row_count"], derived["combined_row_count"]], "declared systems and eligible rows", "outputs")
    check("primary positive envelope", derived["minimum_coarse_schur_gap"] > manifest["finite_fixture"]["gap_floor"] and derived["minimum_residual_gap"] > manifest["finite_fixture"]["gap_floor"] and derived["minimum_combined_lower_envelope"] > manifest["finite_fixture"]["gap_floor"], [derived["minimum_coarse_schur_gap"], derived["minimum_residual_gap"], derived["minimum_combined_lower_envelope"]], "all finite minima above gap floor", "outputs")
    check("independent result", independent["result_id"] == "R-425" and independent["verdict"] == "PASS" and independent["derived"]["fixture_count"] > 0 and independent["derived"]["minimum_combined_gap"] > 0.0, independent["derived"], "positive finite fixtures", "independent")
    check("hostile result", hostile["result_id"] == "R-425" and hostile["verdict"] == "PASS" and hostile["controls"]["all_mutations_rejected"] is True, hostile["controls"], "all hostile mutations rejected", "hostile")
    payload: dict[str, Any] = {"schema": "tect/pre-a-r425-integrated/1.0", "result_id": "R-425", "exploration_id": "EXP-001270", "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(ROOT).as_posix(), "run_kind": "integrated", "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "derived": {"system_count": derived["system_count"], "conditional_row_count": derived["conditional_row_count"], "eligible_row_count": derived["eligible_row_count"], "minimum_coarse_schur_gap": derived["minimum_coarse_schur_gap"], "minimum_residual_gap": derived["minimum_residual_gap"], "minimum_combined_lower_envelope": derived["minimum_combined_lower_envelope"], "independent_fixture_count": independent["derived"]["fixture_count"], "hostile_mutation_count": hostile["controls"]["mutation_count"], "lean": "PASS", "outputs": outputs}, "source_hashes": hashes, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(output, payload)
    print(f"R-425 INTEGRATED PASS {len(checks)}/{len(checks)} systems={derived['system_count']} rows={derived['conditional_row_count']} eligible={derived['eligible_row_count']} combined_min={derived['minimum_combined_lower_envelope']:.6g} Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
