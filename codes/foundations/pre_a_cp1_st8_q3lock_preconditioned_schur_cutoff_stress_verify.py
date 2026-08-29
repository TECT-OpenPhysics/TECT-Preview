#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-416.

This verifier treats the log-domain/projected-Schur calculation as a finite,
claim-nonbearing stress test.  Minima are compared tightly because they are
the robust obstruction diagnostics; maxima are compared with a separate
aggregate tolerance because eigensolver conditioning can perturb upper
envelopes without changing the finite pass/fail conclusion.
"""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-preconditioned-schur-cutoff-stress-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R416.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-preconditioned_schur_cutoff_stress/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-preconditioned_schur_cutoff_stress/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-preconditioned_schur_cutoff_stress/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-preconditioned_schur_cutoff_stress/integrated.json"
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
    aggregate_tolerance = float(fixture.get("aggregate_tolerance", "1e-2"))
    numerical_tolerance = float(fixture["numerical_tolerance"])
    gap_floor = float(fixture["gap_floor"])
    raw_zero_threshold = float(fixture["raw_zero_threshold"])
    hostile_zero_threshold = float(fixture["hostile_zero_threshold"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = (
        "finite_log_domain_gibbs_closed",
        "finite_log_conditional_rows_closed",
        "finite_constant_mode_projection_closed",
        "finite_projected_schur_gap_stress_closed",
        "finite_cutoff_stress_closed",
        "finite_scale_invariance_closed",
    )
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check(
        "manifest identity",
        manifest["result_id"] == "R-416" and manifest["exploration_id"] == "EXP-001261" and manifest["claim_bearing"] is False,
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        "R-416/EXP-001261/false",
        "provenance",
    )
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    dimensions = [int(value) for value in fixture["cutoff_dimensions"]]
    betas = [float(Fraction(str(value))) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    check(
        "fixture grid",
        int(fixture["volume"]) == 2 and dimensions == sorted(set(dimensions)) and len(dimensions) >= 10 and orientations == ["right", "left"] and betas == [0.5, 2.0, 8.0],
        [fixture["volume"], dimensions, betas, orientations],
        "volume 2, ordered cutoffs, beta 1/2,2,8, right/left",
        "fixture",
    )
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-416 artifacts", "provenance")
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
    lean = command([str(LAKE), "env", "lean", "Tect/R416.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1400:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p, i, h = primary["derived"], independent["derived"], hostile["derived"]

    exact_fields = ("system_count", "profile_count", "comparison_row_count", "cutoff_dimensions", "beta_values", "direct_underflow_rows")
    for field in exact_fields:
        check(f"primary-independent {field}", close(p[field], i[field], 0.0), [p[field], i[field]], "exact agreement", "independence")
    tight_fields = ("minimum_projected_gap", "minimum_schur_gap", "minimum_coarse_schur_gap", "minimum_residual_gap", "minimum_log_conditional_mass")
    for field in tight_fields:
        check(f"primary-independent {field}", close(p[field], i[field], tolerance), [p[field], i[field]], f"within {tolerance}", "independence")
    aggregate_fields = ("maximum_projected_gap", "maximum_schur_gap", "maximum_coarse_schur_gap", "maximum_residual_gap", "maximum_log_condition_number")
    for field in aggregate_fields:
        check(f"primary-independent {field}", close(p[field], i[field], aggregate_tolerance), [p[field], i[field]], f"within aggregate tolerance {aggregate_tolerance}", "independence")
    check("system grid reached", p["system_count"] == len(dimensions), p["system_count"], len(dimensions), "coverage")
    expected_profiles = len(dimensions) * len(betas) * len(orientations)
    check("profile grid reached", p["profile_count"] == expected_profiles, p["profile_count"], expected_profiles, "coverage")
    expected_rows = len(orientations) * len(betas) * sum(dimension + 1 for dimension in dimensions)
    check("row grid reached", p["comparison_row_count"] == expected_rows and i["comparison_row_count"] == expected_rows, [p["comparison_row_count"], i["comparison_row_count"]], expected_rows, "coverage")
    check("projected and Schur positivity", p["minimum_projected_gap"] > gap_floor and p["minimum_schur_gap"] > gap_floor and i["minimum_projected_gap"] > gap_floor and i["minimum_schur_gap"] > gap_floor, [p["minimum_projected_gap"], i["minimum_projected_gap"], p["minimum_schur_gap"], i["minimum_schur_gap"]], f"> {gap_floor}", "finite stress")
    check("Schur below projected", p["minimum_schur_gap"] <= p["minimum_projected_gap"] + numerical_tolerance and p["maximum_schur_gap"] <= p["maximum_projected_gap"] + numerical_tolerance, [p["minimum_schur_gap"], p["maximum_schur_gap"]], f"within {numerical_tolerance}", "Schur")
    check("log-domain finite", p["direct_underflow_rows"] == 0 and i["direct_underflow_rows"] == 0 and math.isfinite(p["minimum_log_conditional_mass"]) and math.isfinite(i["minimum_log_conditional_mass"]), [p["direct_underflow_rows"], i["direct_underflow_rows"], p["minimum_log_conditional_mass"], i["minimum_log_conditional_mass"]], "finite with no direct underflow rows", "log-domain")
    check("scale invariance", p["maximum_scale_invariance_residual"] <= tolerance and i["maximum_scale_invariance_residual"] <= tolerance, [p["maximum_scale_invariance_residual"], i["maximum_scale_invariance_residual"]], f"<= {tolerance}", "scale")
    check("raw-mode diagnosis", p["maximum_raw_zero_mode_residual"] > raw_zero_threshold and i["maximum_raw_zero_mode_residual"] > raw_zero_threshold, [p["maximum_raw_zero_mode_residual"], i["maximum_raw_zero_mode_residual"]], f"> {raw_zero_threshold}", "conditioning diagnosis")
    check(
        "hostile mutation suite",
        len(hostile.get("checks", [])) >= 9
        and all(row.get("status") == "PASS" for row in hostile.get("checks", []))
        and h["raw_zero_mode_residual"] > hostile_zero_threshold
        and h["projected_gap"] > gap_floor
        and h["wrong_projected_minimum"] < -hostile_zero_threshold
        and h["scale_residual"] <= tolerance
        and h["naive_underflow_count"] >= 1,
        h,
        "raw drift diagnosed, projection survives, wrong projection/underflow fail closed",
        "hostile",
    )

    payload = {
        "schema": "tect/pre-a-r416-integrated/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-416",
        "exploration_id": "EXP-001261",
        "verdict": "PASS",
        "checks": checks,
        "derived": {"primary": p, "independent": i, "hostile": h, "lean": "PASS", "command_outputs": outputs},
        "scope": scope,
        "boundary": manifest["boundary"],
        "comparison_policy": {"tight_tolerance": tolerance, "aggregate_tolerance": aggregate_tolerance, "reason": "minima are robust gap diagnostics; maxima are eigensolver-conditioning-sensitive envelopes"},
    }
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED PRECONDITIONED-SCHUR PASS {len(checks)}/{len(checks)} cutoffs={len(dimensions)} profiles={p['profile_count']} rows={p['comparison_row_count']} projected_gap=[{p['minimum_projected_gap']:.6g},{p['maximum_projected_gap']:.6g}] schur_gap=[{p['minimum_schur_gap']:.6g},{p['maximum_schur_gap']:.6g}] raw_zero_max={p['maximum_raw_zero_mode_residual']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
