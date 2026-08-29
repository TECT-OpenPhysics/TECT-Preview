#!/usr/bin/env python3
"""Integrated verifier for the R-417 Lyapunov core-tail corridor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-lyapunov-core-tail-corridor-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_lyapunov_core_tail_corridor.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_lyapunov_core_tail_corridor_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_lyapunov_core_tail_corridor_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R417.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-lyapunov_core_tail_corridor/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-lyapunov_core_tail_corridor/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-lyapunov_core_tail_corridor/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-lyapunov_core_tail_corridor/integrated.json"
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


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def close(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isfinite(float(left)) and math.isfinite(float(right)) and abs(float(left) - float(right)) <= tolerance
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(close(a, b, tolerance) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(close(left[key], right[key], tolerance) for key in left)
    return left == right


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["crosscheck_tolerance"])
    aggregate_tolerance = float(fixture["aggregate_tolerance"])
    gap_floor = float(fixture["gap_floor"])
    drift_floor = float(fixture["drift_floor"])
    tail_mass_cap = float(fixture["tail_mass_cap"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = ("finite_log_domain_rows_closed", "finite_lyapunov_drift_closed", "finite_core_gap_closed", "finite_tail_mass_accounting_closed", "finite_boundary_rate_closed", "finite_alpha_theta_cutoff_stress_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-417" and manifest["exploration_id"] == "EXP-001262" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-417/EXP-001262/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    alphas = [float(Fraction(value)) for value in fixture["alpha_values"]]
    thetas = [float(value) for value in fixture["tail_thresholds"]]
    check("fixture grid", int(fixture["volume"]) == 2 and dimensions == sorted(set(dimensions)) and len(dimensions) >= 10 and betas == [0.5, 2.0, 8.0] and list(fixture["orientations"]) == ["right", "left"] and alphas == [0.025, 0.05, 0.1] and thetas == [4.0, 8.0, 12.0], [fixture["volume"], dimensions, betas, fixture["orientations"], alphas, thetas], "volume two, ordered cutoff/beta/orientation/alpha/theta grid", "fixture")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.as_posix() for path in artifacts if not path.is_file()], "all R-417 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "finite scalar file", "no promotion text", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1400:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R417.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1400:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p, i, h = primary["derived"], independent["derived"], hostile["derived"]
    for field in ("system_count", "profile_count", "comparison_row_count", "cutoff_dimensions", "beta_values", "alpha_values", "tail_thresholds", "tail_row_count_by_theta", "drift_row_count_by_alpha_theta"):
        check(f"primary-independent {field}", close(p[field], i[field], 0.0), [p[field], i[field]], "exact agreement", "independence")
    for field in ("minimum_full_projected_gap", "minimum_core_gap", "minimum_core_mass", "maximum_tail_mass"):
        check(f"primary-independent {field}", close(p[field], i[field], tolerance), [p[field], i[field]], f"within {tolerance}", "independence")
    for field in ("maximum_full_projected_gap", "maximum_core_gap", "maximum_boundary_rate"):
        check(f"primary-independent {field}", close(p[field], i[field], aggregate_tolerance), [p[field], i[field]], f"within {aggregate_tolerance}", "independence")
    for field in p["minimum_tail_drift_by_alpha_theta"]:
        check(f"primary-independent drift {field}", close(p["minimum_tail_drift_by_alpha_theta"][field], i["minimum_tail_drift_by_alpha_theta"][field], aggregate_tolerance), [p["minimum_tail_drift_by_alpha_theta"][field], i["minimum_tail_drift_by_alpha_theta"][field]], f"within {aggregate_tolerance}", "independence")
    check("grid coverage", p["system_count"] == len(dimensions) and p["profile_count"] == len(dimensions) * len(betas) * 2 and p["comparison_row_count"] == 2 * len(betas) * sum(dimension + 1 for dimension in dimensions), [p["system_count"], p["profile_count"], p["comparison_row_count"]], "complete finite grid", "coverage")
    check("core-tail envelope", p["minimum_core_gap"] > gap_floor and p["minimum_core_mass"] > float(fixture["core_mass_floor"]) and p["maximum_tail_mass"] < tail_mass_cap, [p["minimum_core_gap"], p["minimum_core_mass"], p["maximum_tail_mass"]], f"gap>{gap_floor}, core mass>{fixture['core_mass_floor']}, tail mass<{tail_mass_cap}", "core-tail")
    check("positive drift envelope", min(p["minimum_tail_drift_by_alpha_theta"].values()) > drift_floor and min(i["minimum_tail_drift_by_alpha_theta"].values()) > drift_floor, [min(p["minimum_tail_drift_by_alpha_theta"].values()), min(i["minimum_tail_drift_by_alpha_theta"].values())], f">{drift_floor}", "Lyapunov")
    check("tail thresholds covered", all(value > 0 for value in p["tail_row_count_by_theta"].values()), p["tail_row_count_by_theta"], "positive tail rows", "coverage")
    check("hostile suite", len(hostile.get("checks", [])) >= 8 and all(row.get("status") == "PASS" for row in hostile.get("checks", [])) and h["reversed_minimum_tail_rate"] < -drift_floor and h["inverse_minimum_tail_rate"] < -drift_floor, h, "sign/inverse/connection/positivity mutations rejected", "hostile")
    # Keep the integrated artefact compact; full per-row profiles remain in the two
    # independent run artefacts referenced by this verifier.
    p_compact = {key: value for key, value in p.items() if key != "profiles"}
    i_compact = {key: value for key, value in i.items() if key != "profiles"}
    payload = {"schema": "tect/pre-a-r417-integrated/1.0", "manifest": MANIFEST.relative_to(ROOT).as_posix(), "result_id": "R-417", "exploration_id": "EXP-001262", "verdict": "PASS", "checks": checks, "derived": {"primary": p_compact, "independent": i_compact, "hostile": h, "lean": "PASS", "command_outputs": outputs}, "scope": scope, "boundary": manifest["boundary"], "comparison_policy": {"tight_tolerance": tolerance, "aggregate_tolerance": aggregate_tolerance, "reason": "minimum drift/gap/mass values are compared tightly; maxima use an aggregate eigensolver tolerance"}}
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED LYAPUNOV-CORE-TAIL PASS {len(checks)}/{len(checks)} cutoffs={len(dimensions)} profiles={p['profile_count']} rows={p['comparison_row_count']} core_gap=[{p['minimum_core_gap']:.6g},{p['maximum_core_gap']:.6g}] tail_drift_min={min(p['minimum_tail_drift_by_alpha_theta'].values()):.6g} tail_mass_max={p['maximum_tail_mass']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
