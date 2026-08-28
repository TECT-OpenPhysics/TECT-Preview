#!/usr/bin/env python3
"""Integrated verifier for the finite R-399 conditional Poincare package."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-conditional-poincare-shell-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_conditional_poincare_shell.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_conditional_poincare_shell_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_conditional_poincare_shell_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R399.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_conditional_poincare_shell/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-pre_a_cp1_st8_q3lock_conditional_poincare_shell/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-pre_a_cp1_st8_q3lock_conditional_poincare_shell/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-pre_a_cp1_st8_q3lock_conditional_poincare_shell/integrated.json"
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
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-399" and manifest["exploration_id"] == "EXP-001244" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-399/EXP-001244/false", "identity")
    finite_flags = ("finite_conditional_variance_identity_closed", "finite_birth_death_poincare_transfer_closed", "finite_oriented_shell_gradient_profile_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [str(path) for path in artifacts if not path.is_file()], "all R-399 artifacts", "provenance")
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
            result = command([sys.executable, "-X", "utf8", str(script)], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R399.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p = primary["derived"]
    i = independent["derived"]
    fields = ("context_count", "system_count", "max_shell_energy", "max_weighted_shell_energy", "max_poincare_bound", "max_weighted_poincare_bound", "max_poincare_residual", "max_weighted_poincare_residual", "min_conditional_gap", "max_conditional_slack", "max_gradient_energy", "min_coordinate_probability_roundoff", "profile_by_system")
    for field in fields:
        check(f"primary-independent {field}", close(p[field], i[field], tolerance * 20.0), [p[field], i[field]], f"within {tolerance * 20.0}", "independence")
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("system grid reached", p["system_count"] == expected_system_count, p["system_count"], expected_system_count, "coverage")
    check("context rows positive", p["context_count"] > 0, p["context_count"], ">0", "coverage")
    check("finite gap positive", p["min_conditional_gap"] > 0.0, p["min_conditional_gap"], ">0", "conditional gap")
    check("Poincare residual", p["max_poincare_residual"] >= -tolerance and p["max_weighted_poincare_residual"] >= -tolerance, [p["max_poincare_residual"], p["max_weighted_poincare_residual"]], f">=-{tolerance}", "conditional Poincare")
    hostile_derived = hostile["derived"]
    check("hostile mutations caught", hostile_derived["genuine_deficit"] >= -tolerance and hostile_derived["weighted_deficit"] >= -tolerance and hostile_derived["naive_deficit"] > float(fixture["hostile_threshold"]) and hostile_derived["wrong_parent_gap"] > float(fixture["hostile_threshold"]), hostile_derived, "genuine transfer plus mutation gaps", "hostile")
    payload = {"schema": "tect/pre-a-r399-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-399", "exploration_id": "EXP-001244", "verdict": "PASS", "checks": checks, "derived": {"primary": p, "independent": i, "hostile": hostile_derived, "lean": "PASS", "command_outputs": outputs}, "scope": scope}
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INTEGRATED CONDITIONAL-POINCARE PASS {len(checks)}/{len(checks)} contexts={p['context_count']} min_gap={p['min_conditional_gap']:.6g} max_poincare={p['max_poincare_bound']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
