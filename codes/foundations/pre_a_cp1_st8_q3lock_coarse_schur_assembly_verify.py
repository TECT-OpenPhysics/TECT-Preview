#!/usr/bin/env python3
"""Integrated verifier for the R-424 finite two-block coarse-Schur lane."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_coarse_schur_assembly.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_coarse_schur_assembly_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_coarse_schur_assembly_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R424.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-coarse_schur_assembly/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-coarse_schur_assembly/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-coarse_schur_assembly/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-coarse_schur_assembly/integrated.json"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = ["finite_harmonic_coarse_schur_closed", "finite_residual_reuse_closed", "finite_combined_lower_envelope_closed", "finite_coarse_rows_recorded"]
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-424" and manifest["exploration_id"] == "EXP-001269" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-424/EXP-001269/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-424 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    check("parent hashes", sha256(ROOT / manifest["upstream_authority"]["r422_manifest"]) == manifest["upstream_authority"]["r422_sha256"] and sha256(ROOT / manifest["upstream_authority"]["r419_manifest"]) == manifest["upstream_authority"]["r419_sha256"], "R-422/R-419 parent bytes", "declared SHA-256 values", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared markers", "Lean")
    check("Lean boundary", all(token not in lean_text for token in ("Yang", "mass gap", "Sector-A", "Pre-A")), "finite scalar file", "no physical promotion text", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            result = command([sys.executable, "-X", "utf8", str(script), "--self-test"], ROOT)
            outputs[script.name] = (result.stdout + result.stderr).strip()
            check(f"run {script.name}", result.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")
    lean = command([str(LAKE), "env", "lean", "Tect/R424.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0, outputs["lean"][-1800:], "exit 0", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    check("primary verdict", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS", "executables")
    check("independent verdict", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS", "executables")
    check("hostile verdict", hostile.get("verdict") == "PASS", hostile.get("verdict"), "PASS", "hostile")
    p, i, h = primary["derived"], independent["derived"], hostile["controls"]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["q3_pairs"])
    check("primary coverage", p["system_count"] == expected_system_count and p["conditional_row_count"] > 0 and p["tail_row_count"] > 0 and p["eligible_row_count"] == p["combined_row_count"] and p["eligible_row_count"] > 0, [p["system_count"], p["conditional_row_count"], p["tail_row_count"], p["eligible_row_count"], p["combined_row_count"]], [expected_system_count, "positive", "positive", "equal positive", "equal"], "coverage")
    check("primary coarse positivity", p["minimum_coarse_schur_gap"] > float(fixture["gap_floor"]), p["minimum_coarse_schur_gap"], f">{fixture['gap_floor']}", "coarse Schur")
    check("primary residual positivity", p["minimum_residual_gap"] > float(fixture["gap_floor"]), p["minimum_residual_gap"], f">{fixture['gap_floor']}", "residual")
    check("primary combined positivity", p["minimum_combined_lower_envelope"] > float(fixture["gap_floor"]) and p["maximum_combined_lower_envelope"] <= 0.5 * min(p["maximum_coarse_schur_gap"], p["maximum_residual_gap"]) + float(fixture["comparison_tolerance"]), [p["minimum_combined_lower_envelope"], p["maximum_combined_lower_envelope"]], "positive finite half-minimum envelope", "combined")
    check("primary residual reuse", p["maximum_residual_reuse_difference"] <= float(fixture["comparison_tolerance"]), p["maximum_residual_reuse_difference"], f"<={fixture['comparison_tolerance']}", "R-422 reuse")
    check("primary harmonic split", p["minimum_harmonic_lower_margin"] >= -float(fixture["numerical_tolerance"]), p["minimum_harmonic_lower_margin"], f">=-{fixture['numerical_tolerance']}", "harmonic split")
    check("independent coverage", i["fixture_count"] == 4 and i["minimum_combined_gap"] > 0.0 and i["maximum_energy_error"] <= 1.0e-7 and i["minimum_lower_margin"] >= -1.0e-7, i, "four positive independent fixtures", "coverage")
    check("hostile controls", h.get("all_mutations_rejected") is True and h.get("numeric_evaluation") is False and h.get("physical_promotion") is False and h.get("mutation_count") == 7, h, "seven invalid mutations rejected", "hostile")
    payload = {
        "schema": "tect/pre-a-r424-integrated/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "checks": checks,
        "derived": {"primary": p, "independent": i, "hostile": h, "lean": "PASS", "command_outputs": outputs},
        "scope": scope,
        "boundary": manifest["boundary"],
        "comparison_policy": {"tolerance": float(fixture["comparison_tolerance"]), "reason": "the finite harmonic decomposition is checked row-by-row; no finite constant is promoted to a uniform or physical claim"},
    }
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"R-424 INTEGRATED PASS {len(checks)}/{len(checks)} systems={p['system_count']} rows={p['conditional_row_count']} eligible={p['eligible_row_count']} coarse_min={p['minimum_coarse_schur_gap']:.6g} residual_min={p['minimum_residual_gap']:.6g} combined_min={p['minimum_combined_lower_envelope']:.6g} Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
