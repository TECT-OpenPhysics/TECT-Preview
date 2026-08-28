#!/usr/bin/env python3
"""Integrated verifier for R-406."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_harmonic_schur_capacity"
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-harmonic-schur-capacity-manifest.json"
PRIMARY = ROOT / f"codes/foundations/{SLUG}.py"
INDEPENDENT = ROOT / f"codes/foundations/{SLUG}_independent.py"
HOSTILE = ROOT / f"codes/foundations/{SLUG}_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R406.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-hostile-{SLUG}" / "hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


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
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isfinite(float(left)) and math.isfinite(float(right)) and abs(float(left) - float(right)) <= tolerance * (1.0 + abs(float(left)) + abs(float(right)))
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(close(a, b, tolerance) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(close(left[key], right[key], tolerance) for key in left)
    return left == right


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["crosscheck_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-406" and manifest["exploration_id"] == "EXP-001251" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-406/EXP-001251/false", "identity")
    finite_flags = ("finite_harmonic_extension_closed", "finite_schur_capacity_closed", "finite_residual_gap_closed", "finite_energy_variance_split_closed", "finite_naive_block_gap_obstruction_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-406 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in artifacts}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "scalar finite file", "no promotion text", "Lean")

    expected = ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT))
    outputs: dict[str, str] = {}
    for script, output in expected:
        if args.reuse_existing and output.is_file():
            outputs[script.name] = f"reused {output.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([str(PYTHON), "-X", "utf8", str(script)], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and output.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R406.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p, i = primary["derived"], independent["derived"]
    scalar_fields = ("system_count", "profile_count", "row_count", "minimum_full_gap", "maximum_full_gap", "minimum_coarse_schur_gap", "maximum_coarse_schur_gap", "minimum_residual_gap", "maximum_residual_gap", "minimum_decomposition_gap", "maximum_decomposition_gap", "minimum_naive_block_gap", "maximum_naive_block_gap", "naive_obstruction_rows")
    for field in scalar_fields:
        check(f"primary-independent {field}", close(p[field], i[field], tolerance), [p[field], i[field]], f"within {tolerance}", "independence")
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("system grid reached", p["system_count"] == expected_system_count, p["system_count"], expected_system_count, "coverage")
    check("profile rows positive", p["profile_count"] > 0 and p["row_count"] > p["profile_count"], [p["profile_count"], p["row_count"]], "positive", "coverage")
    check("full gap positive", p["minimum_full_gap"] > float(fixture["gap_floor"]), p["minimum_full_gap"], f">{fixture['gap_floor']}", "full graph")
    check("Schur coarse gap positive", p["minimum_coarse_schur_gap"] > float(fixture["gap_floor"]), p["minimum_coarse_schur_gap"], f">{fixture['gap_floor']}", "Schur coarse")
    check("residual gap positive", p["minimum_residual_gap"] > float(fixture["gap_floor"]), p["minimum_residual_gap"], f">{fixture['gap_floor']}", "residual")
    check("corrected decomposition positive", p["minimum_decomposition_gap"] > float(fixture["gap_floor"]), p["minimum_decomposition_gap"], f">{fixture['gap_floor']}", "finite lower bound")
    check("naive shortcut obstructed", p["naive_obstruction_rows"] > 0 and p["maximum_naive_block_gap"] > p["maximum_full_gap"], [p["naive_obstruction_rows"], p["maximum_naive_block_gap"], p["maximum_full_gap"]], "strict Ritz-over-full row", "shortcut audit")
    hostile_derived = hostile["derived"]
    check("hostile corrected bound", hostile_derived["decomposition_gap"] > 0.0 and hostile_derived["decomposition_gap"] <= hostile_derived["full_gap"] + 2.0e-8, [hostile_derived["decomposition_gap"], hostile_derived["full_gap"]], "0<corrected<=full", "hostile")
    check("hostile naive failure", hostile_derived["naive_false_lower_bound_margin"] > 1.0e-9, hostile_derived["naive_false_lower_bound_margin"], ">1e-9", "hostile")
    check("hostile disconnected blocks", hostile_derived["cross_deleted_zero_count"] >= hostile_derived["block_count"], [hostile_derived["cross_deleted_zero_count"], hostile_derived["block_count"]], "one zero per block", "hostile")
    check("hostile q mutation", hostile_derived["q_mutation_edge_count"] == 0, hostile_derived["q_mutation_edge_count"], 0, "hostile")
    payload = {"schema": "tect/pre-a-r406-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-406", "exploration_id": "EXP-001251", "verdict": "PASS", "checks": checks, "derived": {"primary": p, "independent": i, "hostile": hostile_derived, "lean": "PASS", "command_outputs": outputs}, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED HARMONIC-SCHUR PASS {len(checks)}/{len(checks)} profiles={p['profile_count']} rows={p['row_count']} full_min={p['minimum_full_gap']:.6g} coarse_min={p['minimum_coarse_schur_gap']:.6g} residual_min={p['minimum_residual_gap']:.6g} corrected_min={p['minimum_decomposition_gap']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
