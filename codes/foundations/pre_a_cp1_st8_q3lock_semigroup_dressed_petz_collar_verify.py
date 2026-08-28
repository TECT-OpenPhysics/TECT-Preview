#!/usr/bin/env python3
"""Integrated verifier for the finite R-397 semigroup collar package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-semigroup-dressed-petz-collar-finite-discriminator-manifest.json"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "hostile.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_FILE = LEAN_ROOT / "Tect/R397.lean"
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def compare(left: Any, right: Any, tolerance: float, path: str = "") -> tuple[bool, str]:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right, path
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance, path
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False, path + ".length"
        for index, (a, b) in enumerate(zip(left, right)):
            ok, bad = compare(a, b, tolerance, f"{path}[{index}]")
            if not ok:
                return False, bad
        return True, ""
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False, path + ".keys"
        for key in sorted(left):
            ok, bad = compare(left[key], right[key], tolerance, f"{path}.{key}")
            if not ok:
                return False, bad
        return True, ""
    return left == right, path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-integrated-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "integrated.json")
    parser.add_argument("--reuse-existing", action="store_true", help="reuse already executed primary, independent and hostile outputs")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    semigroup_tolerance = float(fixture["semigroup_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["candidate_id"].endswith("FINITE-v0") and manifest["result_id"] == "R-397" and manifest["exploration_id"] == "EXP-001241" and manifest["claim_bearing"] is False, [manifest["candidate_id"], manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-397 finite false", "identity")
    check("coverage", all(coverage.values()), coverage, "all semigroup collar rows", "coverage")
    finite_flags = ("finite_shifted_filter_positivity_closed", "finite_mass_moment_bound_closed", "finite_semigroup_composition_closed", "finite_normalized_filter_candidate_envelope_closed", "finite_petz_transport_closed", "finite_cutoff_profile_record_closed", "finite_hostile_mutation_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifact_paths = [ROOT / manifest["artifacts"][key] for key in ("primary_script", "independent_script", "hostile_script", "integrated_verifier", "lean")]
    check("artifacts present", all(path.is_file() for path in artifact_paths), [str(path) for path in artifact_paths if not path.is_file()], "all R-397 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in artifact_paths}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN_FILE.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean finite boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "finite scalar file", "no promotion text", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((ROOT / manifest["artifacts"]["primary_script"], PRIMARY_OUTPUT), (ROOT / manifest["artifacts"]["independent_script"], INDEPENDENT_OUTPUT), (ROOT / manifest["artifacts"]["hostile_script"], HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused existing output: {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", expected.is_file(), outputs[script.name], "existing output", "executables")
        else:
            result = run([sys.executable, "-X", "utf8", str(script)], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = run([str(LAKE), "env", "lean", "Tect/R397.lean"], LEAN_ROOT)
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    agreed, failed = compare(primary["derived"], independent["derived"], tolerance * 10.0)
    check("primary-independent agreement", agreed, failed or "all derived fields", f"within {tolerance * 10.0}", "independence")
    derived = primary["derived"]
    declared_systems = {(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]}
    observed_systems = {(int(item["volume"]), int(item["dimension"])) for item in derived["admissible_pairs"]}
    check("finite counts", derived["system_count"] > 0 and derived["partition_count"] > 0 and derived["row_count"] > 0, [derived["system_count"], derived["partition_count"], derived["row_count"]], "positive rows", "coverage")
    check("system grid reached", observed_systems == declared_systems, [len(observed_systems), len(declared_systems)], "declared volume-cutoff grid", "cutoff stress")
    check("scale grid reached", len(derived["filter_scales"]) == len(fixture["filter_scales"]) and all(float(value) > 0.0 for value in derived["filter_scales"]), derived["filter_scales"], "declared positive scales", "fixture")
    check("semigroup residual", derived["semigroup_residual_max"] <= semigroup_tolerance, derived["semigroup_residual_max"], f"<={semigroup_tolerance}", "semigroup")
    check("mass and candidate envelopes", derived["mass_min"] > tolerance and derived["mass_bound_slack_min"] >= -tolerance and derived["candidate_envelope_slack_min"] >= -tolerance, [derived["mass_min"], derived["mass_bound_slack_min"], derived["candidate_envelope_slack_min"]], "finite envelopes", "filter")
    check("transport inequalities", derived["normalization_violation_count"] == 0 and derived["mass_violation_count"] == 0 and derived["candidate_envelope_violation_count"] == 0 and derived["contractivity_violation_count"] == 0 and derived["triangle_violation_count"] == 0 and derived["two_delta_violation_count"] == 0, [derived["normalization_violation_count"], derived["mass_violation_count"], derived["candidate_envelope_violation_count"], derived["contractivity_violation_count"], derived["triangle_violation_count"], derived["two_delta_violation_count"]], "zero finite violations", "transport")
    check("profile coverage", derived["transport_profiles"]["count"] > 0 and derived["transport_profiles"]["profiles_with_adjacent_cutoff"] > 0 and np.isfinite(derived["transport_profiles"]["maximum_adjacent_ratio"]), [derived["transport_profiles"]["count"], derived["transport_profiles"]["profiles_with_adjacent_cutoff"], derived["transport_profiles"]["maximum_adjacent_ratio"]], "finite profiles with adjacent cutoffs", "cutoff stress")
    hostile_derived = hostile["derived"]
    check("hostile mutation sentinels", hostile_derived["normalization_trace_gap"] > float(fixture["hostile_threshold"]) and hostile_derived["one_leg_residual"] > float(fixture["hostile_threshold"]) and hostile_derived["hard_projector_residual"] > float(fixture["hostile_threshold"]) and hostile_derived["transported_error"] <= hostile_derived["genuine_budget"] + tolerance and hostile_derived["mutation_gap"] > float(fixture["hostile_threshold"]) and hostile_derived["reverse_order_residual"] <= semigroup_tolerance, hostile_derived, "declared hostile mutations caught", "hostile")
    payload = {"schema": "tect/pre-a-r397-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-397", "exploration_id": "EXP-001241", "verdict": "PASS", "checks": checks, "derived": {"primary": derived, "independent": independent["derived"], "hostile": hostile_derived, "lean": "PASS", "command_outputs": outputs}, "scope": scope}
    atomic_json(args.output, payload)
    print(f"INTEGRATED SEMIGROUP-DRESSED PETZ COLLAR PASS {len(checks)}/{len(checks)} Lean=PASS mass_defect_max={derived['mass_defect_max']:.6g} disturbance_max={derived['disturbance_max']:.6g} transport_max={derived['transported_error_max']:.6g} ratio_max={derived['transport_profiles']['maximum_adjacent_ratio']:.6g}")


if __name__ == "__main__":
    main()
