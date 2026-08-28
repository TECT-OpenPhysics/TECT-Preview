#!/usr/bin/env python3
"""Integrated verifier for the R-392 QCMI shell-budget checkpoint."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-shell-telescope-manifest.json"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_quantum_markov_shell_telescope" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_quantum_markov_shell_telescope" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_quantum_markov_shell_telescope" / "hostile.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_FILE = LEAN_ROOT / "Tect/R392.lean"
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
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-pre_a_cp1_st8_q3lock_quantum_markov_shell_telescope/integrated.json"); args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); cfg = manifest["finite_fixture"]; coverage = manifest["coverage"]; scope = manifest["scope"]
    tolerance = float(cfg["numerical_tolerance"]); checks: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["candidate_id"].endswith("FINITE-v0") and manifest["result_id"] == "R-392" and manifest["exploration_id"] == "EXP-001235" and manifest["claim_bearing"] is False, [manifest["candidate_id"], manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-392 finite false", "identity")
    check("coverage", all(coverage.values()), coverage, "all declared shell rows", "coverage")
    finite_flags = ("finite_qcmI_shell_nonnegativity_closed", "finite_qcmI_chain_rule_closed", "finite_l1_boundary_budget_closed", "finite_buffer_shell_stress_closed", "finite_product_hostile_closed")
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")

    paths = [ROOT / manifest["artifacts"][key] for key in ("primary_script", "independent_script", "hostile_script", "integrated_verifier", "lean")]
    check("artifacts present", all(path.is_file() for path in paths), [str(path) for path in paths if not path.is_file()], "all R-392 artifacts", "provenance")
    hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in paths}
    check("source hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct", "provenance")
    lean_text = LEAN_FILE.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean finite boundary", all(token not in lean_text for token in ("QFT", "Pre-A", "Sector-A")), "finite scalar file", "no promotion text", "Lean")

    outputs = {}
    for script, expected in ((ROOT / manifest["artifacts"]["primary_script"], PRIMARY_OUTPUT), (ROOT / manifest["artifacts"]["independent_script"], INDEPENDENT_OUTPUT), (ROOT / manifest["artifacts"]["hostile_script"], HOSTILE_OUTPUT)):
        result = run([sys.executable, "-X", "utf8", str(script)], ROOT); outputs[script.name] = (result.stdout + result.stderr).strip()
        check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1200:], "exit 0 and output", "executables")
    lean = run([str(LAKE), "env", "lean", "Tect/R392.lean"], LEAN_ROOT); outputs["lean"] = (lean.stdout + lean.stderr).strip(); check("Lean compile", lean.returncode == 0, outputs["lean"][-1200:], "exit 0", "Lean")
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8")); independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8")); hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables"); check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables"); check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    agreed, failed = compare(primary["derived"], independent["derived"], tolerance); check("primary-independent agreement", agreed, failed or "all derived fields", f"within {tolerance}", "independence")
    derived = primary["derived"]; qprofiles = {tuple(row["key"]): row for row in derived["qcmI_shell_profile"]["profiles"]}
    check("finite counts", derived["system_count"] > 0 and derived["base_partition_count"] > 0 and derived["qcmI_record_count"] == derived["row_count"] > 0, [derived["system_count"], derived["base_partition_count"], derived["qcmI_record_count"], derived["row_count"]], "positive and aligned", "coverage")
    check("chain residual", derived["max_chain_rule_residual"] <= tolerance and derived["negative_increment_count"] == 0 and derived["negative_cumulative_count"] == 0, [derived["max_chain_rule_residual"], derived["negative_increment_count"], derived["negative_cumulative_count"]], f"residual <= {tolerance}, no negatives", "chain rule")
    check("l1 budget", derived["l1_budget_min"] >= -tolerance and derived["l1_budget_max"] >= derived["qcmI_max"] - tolerance, [derived["l1_budget_min"], derived["l1_budget_max"], derived["qcmI_max"]], "finite nonnegative budget", "l1 budget")
    check("shell profiles", all(key in qprofiles for key in ((1, 1), (1, 2), (2, 1), (2, 2))), [row["key"] for row in derived["qcmI_shell_profile"]["profiles"]], "four first/second-shell profiles", "buffer stress")
    check("successive-shell suppression", qprofiles[(1, 2)]["maximum"] < qprofiles[(1, 1)]["maximum"] and qprofiles[(2, 2)]["maximum"] < qprofiles[(2, 1)]["maximum"], {"core1": [qprofiles[(1, 1)]["maximum"], qprofiles[(1, 2)]["maximum"]], "core2": [qprofiles[(2, 1)]["maximum"], qprofiles[(2, 2)]["maximum"]]}, "second shell maximum smaller", "buffer stress")
    hderived = hostile["derived"]; check("hostile product collapse", hderived["actual_increment_max"] > float(cfg["hostile_threshold"]) and hderived["product_increment_abs_max"] <= tolerance and hderived["mismatch"] > float(cfg["hostile_threshold"]), hderived, "interacting signal versus product zero", "hostile")

    payload = {"schema": "tect/pre-a-r392-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-392", "exploration_id": "EXP-001235", "verdict": "PASS", "checks": checks, "derived": {"primary": derived, "independent": independent["derived"], "hostile": hderived, "lean": "PASS", "command_outputs": outputs}, "scope": scope}
    atomic_json(args.output, payload)
    print(f"INTEGRATED QCMI-SHELL-TELESCOPE PASS {len(checks)}/{len(checks)} Lean=PASS qcmI_max={derived['qcmI_max']:.6g} chain_residual={derived['max_chain_rule_residual']:.3g} suppression=PASS")


if __name__ == "__main__": main()
