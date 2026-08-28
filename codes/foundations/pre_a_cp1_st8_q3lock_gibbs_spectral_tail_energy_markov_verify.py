#!/usr/bin/env python3
"""Integrated verifier for the R-394 positive-energy Gibbs-tail audit."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-gibbs-spectral-tail-energy-markov-manifest.json"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "hostile.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_FILE = LEAN_ROOT / "Tect/R394.lean"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


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
    parser.add_argument("--output", type=Path, default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov/integrated.json")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    coverage = manifest["coverage"]
    scope = manifest["scope"]
    tolerance = float(cfg["numerical_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["candidate_id"].endswith("FINITE-v0") and manifest["result_id"] == "R-394" and manifest["exploration_id"] == "EXP-001237" and manifest["claim_bearing"] is False, [manifest["candidate_id"], manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-394 finite false", "identity")
    check("coverage", all(coverage.values()), coverage, "all declared energy-tail rows", "coverage")
    finite_flags = ("finite_positive_shift_closed", "finite_spectral_projector_closed", "finite_mass_markov_bound_closed", "finite_weighted_markov_bound_closed", "finite_spectral_tail_profile_closed", "finite_cutoff_profile_closed", "finite_hostile_moment_mutation_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")

    paths = [ROOT / manifest["artifacts"][key] for key in ("primary_script", "independent_script", "hostile_script", "integrated_verifier", "lean")]
    check("artifacts present", all(path.is_file() for path in paths), [str(path) for path in paths if not path.is_file()], "all R-394 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in paths}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN_FILE.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean finite boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "finite scalar file", "no promotion text", "Lean")

    outputs: dict[str, str] = {}
    scripts = ((ROOT / manifest["artifacts"]["primary_script"], PRIMARY_OUTPUT), (ROOT / manifest["artifacts"]["independent_script"], INDEPENDENT_OUTPUT), (ROOT / manifest["artifacts"]["hostile_script"], HOSTILE_OUTPUT))
    for script, expected in scripts:
        result = run([sys.executable, "-X", "utf8", str(script)], ROOT)
        outputs[script.name] = (result.stdout + result.stderr).strip()
        check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = run([str(LAKE), "env", "lean", "Tect/R394.lean"], LEAN_ROOT)
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    agreed, failed = compare(primary["derived"], independent["derived"], tolerance)
    check("primary-independent agreement", agreed, failed or "all derived fields", f"within {tolerance}", "independence")
    derived = primary["derived"]
    cutoff = derived["cutoff_profiles"]
    declared_max_dimension = max(int(dimension) for item in cfg["admissible_pairs"] for dimension in item["cutoff_dimensions"])
    observed_max_dimension = max(int(row["dimension"]) for row in primary["records"])
    check("finite counts", derived["system_count"] > 0 and derived["base_partition_count"] > 0 and derived["row_count"] > 0, [derived["system_count"], derived["base_partition_count"], derived["row_count"]], "positive rows", "coverage")
    check("high cutoff reached", observed_max_dimension == declared_max_dimension, [observed_max_dimension, declared_max_dimension], "declared maximum cutoff", "cutoff stress")
    check("spectral tails", derived["tail_mass_min"] >= -tolerance and derived["tail_mass_max"] <= 1.0 + tolerance and derived["weighted_tail_min"] >= -tolerance, [derived["tail_mass_min"], derived["tail_mass_max"], derived["weighted_tail_min"]], "finite nonnegative tails", "spectral tail")
    check("Markov bounds", derived["mass_markov_violation_count"] == 0 and derived["weighted_markov_violation_count"] == 0 and derived["first_moment_max"] >= -tolerance and derived["second_moment_max"] >= -tolerance, [derived["mass_markov_violation_count"], derived["weighted_markov_violation_count"], derived["first_moment_max"], derived["second_moment_max"]], "zero violations and nonnegative moments", "Markov")
    check("cutoff profiles", cutoff["count"] > 0 and all(len(row["dimensions"]) >= 2 for row in cutoff["profiles"]), cutoff["count"], "profiles with adjacent cutoffs", "cutoff stress")
    ratios = [float(value) for row in cutoff["profiles"] for ratio in row["adjacent_ratios"] for value in (ratio["tail_mass_ratio"], ratio["tail_weighted_ratio"])]
    check("cutoff ratios finite", all(np.isfinite(value) and value >= -tolerance for value in ratios), [min(ratios, default=0.0), max(ratios, default=0.0)], "finite nonnegative ratios", "cutoff stress")
    hderived = hostile["derived"]
    check("hostile zero-moment mutation", hderived["selected"]["tail"] > float(cfg["hostile_threshold"]) and hderived["selected"]["tail"] <= hderived["selected"]["mass_bound"] + tolerance and hderived["selected"]["weighted_tail"] <= hderived["selected"]["weighted_bound"] + tolerance and hderived["mismatch"] > float(cfg["hostile_threshold"]), hderived, "positive moment bounds versus zero mutation", "hostile")

    payload = {"schema": "tect/pre-a-r394-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-394", "exploration_id": "EXP-001237", "verdict": "PASS", "checks": checks, "derived": {"primary": derived, "independent": independent["derived"], "hostile": hderived, "lean": "PASS", "command_outputs": outputs}, "scope": scope}
    atomic_json(args.output, payload)
    print(f"INTEGRATED GIBBS-TAIL-MARKOV PASS {len(checks)}/{len(checks)} Lean=PASS tail_max={derived['tail_mass_max']:.6g} weighted_max={derived['weighted_tail_max']:.6g} profiles={cutoff['count']}")


if __name__ == "__main__":
    main()
