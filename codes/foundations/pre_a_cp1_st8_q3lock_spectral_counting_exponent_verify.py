#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-411."""

from __future__ import annotations

import argparse
import hashlib
import math
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-spectral-counting-exponent-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_spectral_counting_exponent.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_spectral_counting_exponent_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_spectral_counting_exponent_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R411.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_spectral_counting_exponent/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-pre_a_cp1_st8_q3lock_spectral_counting_exponent/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-pre_a_cp1_st8_q3lock_spectral_counting_exponent/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-pre_a_cp1_st8_q3lock_spectral_counting_exponent/integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


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
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-411" and manifest["exploration_id"] == "EXP-001256" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-411/EXP-001256/false", "identity")
    finite_flags = ("finite_mode_ordering_closed", "finite_sublinear_counting_closed", "finite_zeta_tail_bound_closed", "finite_likelihood_row_coverage_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-411 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in artifacts}
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
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1000:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R411.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1000:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p, i = primary["derived"], independent["derived"]
    fields = ("system_count", "context_count", "comparison_row_count", "minimum_resistance_average", "maximum_resistance_average", "minimum_trace_inverse", "maximum_trace_inverse", "minimum_projector_trace", "maximum_projector_trace", "maximum_identity_abs_residual", "maximum_transformed_identity_abs_residual", "maximum_projector_identity_abs_residual", "minimum_positive_normalized_eigenvalue", "maximum_effective_resistance", "minimum_mode_constant", "maximum_mode_constant", "minimum_zeta_bound", "maximum_zeta_bound", "minimum_zeta_infinite_bound", "maximum_zeta_infinite_bound", "maximum_mode_envelope_abs_residual", "alpha_profiles", "pair_count", "cutoff_dimensions", "system_profiles")
    for field in fields:
        check(f"primary-independent {field}", close(p[field], i[field], tolerance), [p[field], i[field]], f"within {tolerance}", "independence")
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("system grid reached", p["system_count"] == expected_system_count, p["system_count"], expected_system_count, "coverage")
    check("context grid reached", p["context_count"] > 0 and p["comparison_row_count"] > p["context_count"], [p["context_count"], p["comparison_row_count"]], "positive rows beyond contexts", "coverage")
    check("trace identity residual bounded", p["maximum_identity_abs_residual"] <= float(fixture["numerical_tolerance"]) and p["maximum_transformed_identity_abs_residual"] <= float(fixture["numerical_tolerance"]) and p["maximum_projector_identity_abs_residual"] <= float(fixture["numerical_tolerance"]), [p["maximum_identity_abs_residual"], p["maximum_transformed_identity_abs_residual"], p["maximum_projector_identity_abs_residual"]], f"<= {fixture['numerical_tolerance']}", "trace identity")
    check("trace positive", p["minimum_trace_inverse"] > 0.0 and p["minimum_resistance_average"] > 0.0, [p["minimum_trace_inverse"], p["minimum_resistance_average"]], ">0 on finite grid", "trace identity")
    check("normalized spectrum positive", p["minimum_positive_normalized_eigenvalue"] > float(fixture["resistance_eigen_floor"]), p["minimum_positive_normalized_eigenvalue"], f"> {fixture['resistance_eigen_floor']}", "connectivity")
    check("quadratic mode envelope", p["minimum_mode_constant"] > 0.0 and p["maximum_mode_envelope_abs_residual"] <= float(fixture["numerical_tolerance"]), [p["minimum_mode_constant"], p["maximum_mode_envelope_abs_residual"]], f"c2>0 and residual <= {fixture['numerical_tolerance']}", "mode counting")
    check("zeta trace envelope", p["minimum_zeta_bound"] > 0.0 and p["maximum_trace_inverse"] <= p["maximum_zeta_bound"] + tolerance and p["maximum_zeta_bound"] <= p["maximum_zeta_infinite_bound"] + tolerance, [p["maximum_trace_inverse"], p["maximum_zeta_bound"], p["maximum_zeta_infinite_bound"]], "trace <= finite <= infinite zeta envelope", "zeta envelope")
    alpha_labels = {str(float(Fraction(value))).rstrip("0").rstrip(".") for value in fixture["counting_exponents"]}
    check("sublinear alpha profiles", set(p["alpha_profiles"]) == alpha_labels and all(profile["minimum_counting_constant"] > 0.0 and profile["minimum_finite_trace_bound"] > 0.0 and profile["minimum_finite_trace_bound"] <= profile["maximum_infinite_zeta_bound"] + tolerance for profile in p["alpha_profiles"].values()), p["alpha_profiles"], "all declared 0<alpha<1 profiles finite", "sublinear zeta")
    h = hostile["derived"]
    hostile_spectral_condition = (
        all(
            item["mode_constant"] > 0.0
            and item["trace_inverse"] <= profile["infinite_zeta_bound"] + tolerance
            and item["one_mode_inverse"] < item["trace_inverse"] - tolerance
            for item in h["selected"]
            for profile in item["alpha_profiles"].values()
        )
        and abs(h["toy_spectrum"]["sorted_c2"] - h["toy_spectrum"]["unsorted_c2"]) > tolerance
        and abs(h["toy_spectrum"]["sorted_alpha_constant"] - h["toy_spectrum"]["unsorted_alpha_constant"]) > tolerance
        and h["toy_spectrum"]["wrong_quadratic_residual"] < -tolerance
        and abs(h["toy_spectrum"]["wrong_power_constant"] - h["toy_spectrum"]["correct_power_constant"]) > tolerance
    )
    check("hostile spectral shortcuts caught", hostile_spectral_condition, h, "sorting, scaling, exponent and Fiedler shortcuts rejected", "hostile")
    check("hostile q mutation caught", h["q_mutation"]["mutated_edge_count"] == 0 and h["q_mutation"]["positive_eigenvalue_count"] == 0 and h["q_mutation"]["maximum_edge"] <= float(fixture["hostile_zero_threshold"]), h["q_mutation"], "zero q conductance edges and spectrum", "hostile")
    payload = {"schema": "tect/pre-a-r411-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-411", "exploration_id": "EXP-001256", "verdict": "PASS", "checks": checks, "derived": {"primary": p, "independent": i, "hostile": h, "lean": "PASS", "command_outputs": outputs}, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED SPECTRAL-COUNTING-EXPONENT PASS {len(checks)}/{len(checks)} contexts={p['context_count']} rows={p['comparison_row_count']} alpha={len(p['alpha_profiles'])} c2=[{p['minimum_mode_constant']:.6g},{p['maximum_mode_constant']:.6g}] trace=[{p['minimum_trace_inverse']:.6g},{p['maximum_trace_inverse']:.6g}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
