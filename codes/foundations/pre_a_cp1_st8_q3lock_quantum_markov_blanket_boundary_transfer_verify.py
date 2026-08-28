#!/usr/bin/env python3
"""Integrated verifier for the R-391 quantum-Markov blanket checkpoint."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-blanket-boundary-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-integrated-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "integrated.json"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "hostile.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_FILE = LEAN_ROOT / "Tect/R391.lean"
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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def compare_values(left: Any, right: Any, tolerance: float, path: str = "") -> tuple[bool, str]:
    if isinstance(left, bool) or isinstance(right, bool):
        return (left == right, path)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return (abs(float(left) - float(right)) <= tolerance, path)
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False, path + ".length"
        for index, (a, b) in enumerate(zip(left, right)):
            ok, failed = compare_values(a, b, tolerance, f"{path}[{index}]")
            if not ok:
                return False, failed
        return True, ""
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False, path + ".keys"
        for key in sorted(left):
            ok, failed = compare_values(left[key], right[key], tolerance, f"{path}.{key}")
            if not ok:
                return False, failed
        return True, ""
    return (left == right, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    coverage = manifest["coverage"]
    scope = manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["candidate_id"].endswith("FINITE-v0") and manifest["result_id"] == "R-391" and manifest["exploration_id"] == "EXP-001234" and manifest["claim_bearing"] is False, [manifest["candidate_id"], manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-391 finite false", "identity")
    check("coverage flags", all(coverage.values()), coverage, "all declared rows", "coverage")
    finite_flags = ("finite_qcmI_nonnegativity_closed", "finite_recoverability_scale_closed", "finite_petz_diagnostic_closed", "finite_spectral_complement_profile_closed", "finite_buffer_width_stress_closed")
    promoted_flags = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted_flags.values()), promoted_flags, "all promoted flags false", "scope")

    artifact_paths = [ROOT / manifest["artifacts"][key] for key in ("primary_script", "independent_script", "hostile_script", "integrated_verifier", "lean")]
    check("artifacts present", all(path.is_file() for path in artifact_paths), [str(path) for path in artifact_paths if not path.is_file()], "all R-391 artifacts", "provenance")
    artifact_hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in artifact_paths}
    check("source digests distinct", len(set(artifact_hashes.values())) == len(artifact_hashes), artifact_hashes, "distinct source hashes", "provenance")
    lean_text = LEAN_FILE.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "all declared theorem markers", "Lean")
    check("Lean boundary", "QFT" not in lean_text and "Pre-A" not in lean_text and "Sector-A" not in lean_text, "finite scalar file", "no QFT closure text", "Lean")

    scripts = [
        (ROOT / manifest["artifacts"]["primary_script"], PRIMARY_OUTPUT),
        (ROOT / manifest["artifacts"]["independent_script"], INDEPENDENT_OUTPUT),
        (ROOT / manifest["artifacts"]["hostile_script"], HOSTILE_OUTPUT)
    ]
    command_outputs: dict[str, str] = {}
    for script, expected_output in scripts:
        result = run_command([sys.executable, "-X", "utf8", str(script)], ROOT)
        command_outputs[script.name] = (result.stdout + result.stderr).strip()
        check(f"run {script.name}", result.returncode == 0 and expected_output.is_file(), command_outputs[script.name][-1200:], "exit 0 and output file", "executables")

    lean_result = run_command([str(LAKE), "env", "lean", "Tect/R391.lean"], LEAN_ROOT)
    command_outputs["lean"] = (lean_result.stdout + lean_result.stderr).strip()
    check("Lean compile", lean_result.returncode == 0, command_outputs["lean"][-1200:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS" and primary.get("result_id") == "R-391", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS" and independent.get("result_id") == "R-391", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS" and hostile.get("result_id") == "R-391", hostile.get("verdict"), "PASS", "hostile")
    ok, failed_path = compare_values(primary["derived"], independent["derived"], tolerance)
    check("primary-independent agreement", ok, failed_path or "all derived fields", f"within {tolerance}", "independence")

    pderived = primary["derived"]
    hderived = hostile["derived"]
    check("finite counts", pderived["system_count"] > 0 and pderived["partition_count"] > 0 and pderived["qcmI_record_count"] > 0 and pderived["row_count"] > 0, [pderived[key] for key in ("system_count", "partition_count", "qcmI_record_count", "row_count")], "positive", "coverage")
    check("QCMI nonnegative", pderived["qcmI_negative_count"] == 0 and pderived["qcmI_min"] >= -tolerance, [pderived["qcmI_negative_count"], pderived["qcmI_min"]], "zero negatives", "QCMI")
    check("recoverability finite", pderived["recoverability_scale_max"] >= 0.0 and pderived["recoverability_scale_max"] < float("inf"), pderived["recoverability_scale_max"], ">=0 finite", "recoverability")
    check("Petz range", 0.0 <= pderived["petz_trace_distance_max"] <= 1.0 + tolerance, pderived["petz_trace_distance_max"], "[0,1]", "Petz")
    check("spectral complement range", -tolerance <= pderived["tail_mass_min"] and pderived["tail_mass_max"] <= 1.0 + tolerance, [pderived["tail_mass_min"], pderived["tail_mass_max"]], "[0,1]", "spectral complement")
    q_profiles = pderived["qcmI_buffer_profile"]["profiles"]
    q_by_key = {tuple(row["key"]): row for row in q_profiles}
    check("buffer-width profiles", (1, 1) in q_by_key and (1, 2) in q_by_key and (2, 1) in q_by_key and (2, 2) in q_by_key, [row["key"] for row in q_profiles], "four core/buffer profiles", "buffer stress")
    check("buffer suppression finite", q_by_key[(1, 2)]["maximum"] < q_by_key[(1, 1)]["maximum"] and q_by_key[(2, 2)]["maximum"] < q_by_key[(2, 1)]["maximum"], {"core1": [q_by_key[(1, 1)]["maximum"], q_by_key[(1, 2)]["maximum"]], "core2": [q_by_key[(2, 1)]["maximum"], q_by_key[(2, 2)]["maximum"]]}, "buffer width 2 has smaller sampled maximum", "buffer stress")
    check("hostile catches product collapse", hderived["actual_qcmI_max"] > float(fixture["hostile_threshold"]) and hderived["product_qcmI_abs_max"] <= tolerance and hderived["mismatch"] > float(fixture["hostile_threshold"]), hderived, "nonzero interacting signal versus product zero", "hostile")
    check("hostile width signal", len(hderived["buffer_width_max"]) > 0, hderived["buffer_width_max"], "finite width profile", "hostile")

    payload = {"schema": "tect/pre-a-r391-integrated/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-391", "exploration_id": "EXP-001234", "verdict": "PASS", "checks": checks, "derived": {"primary": pderived, "independent": independent["derived"], "hostile": hderived, "lean": "PASS", "command_outputs": command_outputs}, "scope": scope}
    atomic_json(args.output, payload)
    print(f"INTEGRATED QUANTUM-MARKOV-BLANKET PASS {len(checks)}/{len(checks)} Lean=PASS qcmI_max={pderived['qcmI_max']:.6g} buffer2_suppression=PASS petz_max={pderived['petz_trace_distance_max']:.6g}")


if __name__ == "__main__":
    main()
