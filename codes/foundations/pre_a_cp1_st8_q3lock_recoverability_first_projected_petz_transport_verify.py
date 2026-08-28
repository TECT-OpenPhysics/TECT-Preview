#!/usr/bin/env python3
"""Integrated verifier for the R-396 recoverability-first transport."""

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

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-recoverability-first-projected-petz-transport-manifest.json"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "hostile.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_FILE = LEAN_ROOT / "Tect/R396.lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def compare(left: Any, right: Any, tolerance: float, path: str = "") -> tuple[bool, str]:
    if isinstance(left, bool) or isinstance(right, bool): return left == right, path
    if isinstance(left, (int, float)) and isinstance(right, (int, float)): return abs(float(left) - float(right)) <= tolerance, path
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right): return False, path + ".length"
        for index, (a, b) in enumerate(zip(left, right)):
            ok, bad = compare(a, b, tolerance, f"{path}[{index}]")
            if not ok: return False, bad
        return True, ""
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right): return False, path + ".keys"
        for key in sorted(left):
            ok, bad = compare(left[key], right[key], tolerance, f"{path}.{key}")
            if not ok: return False, bad
        return True, ""
    return left == right, path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-integrated-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "integrated.json")
    parser.add_argument("--reuse-existing", action="store_true", help="reuse already executed primary, independent and hostile outputs")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["finite_fixture"]; coverage = manifest["coverage"]; scope = manifest["scope"]; tolerance = float(fixture["numerical_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["candidate_id"].endswith("FINITE-v0") and manifest["result_id"] == "R-396" and manifest["exploration_id"] == "EXP-001239" and manifest["claim_bearing"] is False, [manifest["candidate_id"], manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-396 finite false", "identity")
    check("coverage", all(coverage.values()), coverage, "all projected Petz transport rows", "coverage")
    finite_flags = ("finite_projected_state_normalization_closed", "finite_petz_recovery_closed", "finite_recovery_contractivity_closed", "finite_triangle_transport_closed", "finite_cutoff_transport_profile_closed", "finite_hostile_budget_mutation_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [ROOT / manifest["artifacts"][key] for key in ("primary_script", "independent_script", "hostile_script", "integrated_verifier", "lean")]
    check("artifacts present", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-396 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in artifacts}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN_FILE.read_text(encoding="utf-8"); markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean finite boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "finite scalar file", "no promotion text", "Lean")
    outputs: dict[str, str] = {}
    for script, expected in ((ROOT / manifest["artifacts"]["primary_script"], PRIMARY_OUTPUT), (ROOT / manifest["artifacts"]["independent_script"], INDEPENDENT_OUTPUT), (ROOT / manifest["artifacts"]["hostile_script"], HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused existing output: {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", expected.is_file(), outputs[script.name], "existing output", "executables")
        else:
            result = run([sys.executable, "-X", "utf8", str(script)], ROOT); outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = run([str(LAKE), "env", "lean", "Tect/R396.lean"], LEAN_ROOT); outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8")); independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8")); hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    agreed, failed = compare(primary["derived"], independent["derived"], tolerance)
    check("primary-independent agreement", agreed, failed or "all derived fields", f"within {tolerance}", "independence")
    derived = primary["derived"]; profiles = derived["cutoff_profiles"]
    declared_systems = {(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]}
    observed_systems = {(int(item["volume"]), int(item["dimension"])) for item in derived["admissible_pairs"]}
    declared_max_dimension = max(dimension for _, dimension in declared_systems); observed_max_dimension = max(dimension for _, dimension in observed_systems)
    check("finite counts", derived["system_count"] > 0 and derived["partition_count"] > 0 and derived["row_count"] > 0, [derived["system_count"], derived["partition_count"], derived["row_count"]], "positive rows", "coverage")
    check("system grid reached", observed_systems == declared_systems, [len(observed_systems), len(declared_systems)], "declared volume-cutoff grid", "cutoff stress")
    check("high cutoff reached", observed_max_dimension == declared_max_dimension, [observed_max_dimension, declared_max_dimension], "declared maximum cutoff", "cutoff stress")
    check("distance ranges", derived["delta_abc_min"] >= -tolerance and derived["delta_ab_min"] >= -tolerance and derived["projected_error_max"] >= -tolerance and derived["transported_error_max"] >= -tolerance, [derived["delta_abc_min"], derived["delta_ab_min"], derived["projected_error_max"], derived["transported_error_max"]], "finite nonnegative distances", "bridge")
    check("transport inequalities", derived["normalization_violation_count"] == 0 and derived["contractivity_violation_count"] == 0 and derived["triangle_violation_count"] == 0 and derived["two_delta_violation_count"] == 0 and derived["contractivity_gap_max"] <= tolerance, [derived["normalization_violation_count"], derived["contractivity_violation_count"], derived["triangle_violation_count"], derived["two_delta_violation_count"], derived["contractivity_gap_max"]], "zero violations", "transport")
    check("cutoff profiles", profiles["count"] > 0 and all(len(row["dimensions"]) >= 2 for row in profiles["profiles"]), profiles["count"], "profiles with adjacent cutoffs", "cutoff stress")
    ratios = [float(item["transported_error_ratio"]) for row in profiles["profiles"] for item in row["adjacent_ratios"]]
    check("cutoff ratios finite", all(np.isfinite(value) and value >= -tolerance for value in ratios), [min(ratios, default=0.0), max(ratios, default=0.0)], "finite nonnegative ratios", "cutoff stress")
    hd = hostile["derived"]
    check("hostile omitted displacement budget", hd["transported_error"] > float(fixture["hostile_threshold"]) and hd["transported_error"] <= hd["genuine_budget"] + tolerance and hd["transported_error"] > hd["mutated_budget_without_displacements"] + float(fixture["hostile_threshold"]), hd, "genuine triangle survives and omission is caught", "hostile")
    payload = {"schema": "tect/pre-a-r396-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-396", "exploration_id": "EXP-001239", "verdict": "PASS", "checks": checks, "derived": {"primary": derived, "independent": independent["derived"], "hostile": hd, "lean": "PASS", "command_outputs": outputs}, "scope": scope}
    atomic_json(args.output, payload)
    print(f"INTEGRATED RECOVERABILITY-FIRST PETZ TRANSPORT PASS {len(checks)}/{len(checks)} Lean=PASS transported_max={derived['transported_error_max']:.6g} ratio_max={profiles['maximum_adjacent_transport_ratio']:.6g}")


if __name__ == "__main__": main()
