#!/usr/bin/env python3
"""Integrated verifier for the R-422 residual core/tail reserve."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_core_tail_reserve.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_core_tail_reserve_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_core_tail_reserve_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R422.lean"
PRIMARY_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-residual_core_tail_reserve/primary.json"
INDEPENDENT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-residual_core_tail_reserve/independent.json"
HOSTILE_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-residual_core_tail_reserve/hostile.json"
INTEGRATED_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-integrated-residual_core_tail_reserve/integrated.json"
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

    finite_flags = [
        "finite_block_mean_zero_split_closed",
        "finite_tail_hardy_reuse_closed",
        "finite_cross_block_norm_closed",
        "finite_two_by_two_reserve_closed",
        "finite_positive_reserve_rows_recorded",
        "finite_negative_reserve_rows_recorded",
    ]
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-422" and manifest["exploration_id"] == "EXP-001267" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-422/EXP-001267/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.as_posix() for path in artifacts if not path.is_file()], "all R-422 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
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
    lean = command([str(LAKE), "env", "lean", "Tect/R422.lean"], ROOT / "verification/lean")
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
    check("primary coverage", p["system_count"] == expected_system_count and p["conditional_row_count"] > 0 and p["tail_row_count"] > 0 and p["eligible_row_count"] > 0, [p["system_count"], p["conditional_row_count"], p["tail_row_count"], p["eligible_row_count"]], [expected_system_count, "positive", "positive", "positive"], "coverage")
    check("primary outcome split", p["positive_reserve_row_count"] > 0 and p["nonpositive_reserve_row_count"] > 0 and p["minimum_safe_reserve"] < 0.0 and p["maximum_safe_reserve"] > 0.0, [p["positive_reserve_row_count"], p["nonpositive_reserve_row_count"], p["minimum_safe_reserve"], p["maximum_safe_reserve"]], "positive and failure rows retained", "boundary")
    check("primary finite bounds", p["minimum_core_gap"] > 0.0 and p["minimum_direct_tail_gap"] > 0.0 and p["minimum_tail_hardy_floor"] > 0.0 and p["minimum_probe_margin"] >= -float(fixture["reserve_tolerance"]), [p["minimum_core_gap"], p["minimum_direct_tail_gap"], p["minimum_tail_hardy_floor"], p["minimum_probe_margin"]], "finite form and reserve checks", "primary")
    check("independent coverage", i["fixture_count"] >= 3 and i["eligible_fixture_count"] == i["fixture_count"] and i["positive_reserve_fixture_count"] > 0, i, "independent fixtures with positive reserves", "coverage")
    check("independent finite bounds", i["minimum_tail_hardy_floor"] > 0.0 and i["minimum_actual_residual_gap"] > 0.0 and i["minimum_probe_margin"] >= -float(fixture["reserve_tolerance"]), i, "finite independent reserve checks", "independent")
    check("hostile controls", h.get("all_mutations_rejected") is True and h.get("numeric_evaluation") is False and h.get("physical_promotion") is False and h.get("mutation_count") == 7, h, "seven invalid mutations rejected", "hostile")
    check("reserve direction", p["minimum_safe_reserve"] <= p["minimum_sharp_diagnostic"] + float(fixture["reserve_tolerance"]), [p["minimum_safe_reserve"], p["minimum_sharp_diagnostic"]], "conservative reserve does not exceed sharp diagnostic", "comparison")
    payload = {
        "schema": "tect/pre-a-r422-integrated/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "checks": checks,
        "derived": {"primary": p, "independent": i, "hostile": h, "lean": "PASS", "command_outputs": outputs},
        "scope": scope,
        "boundary": manifest["boundary"],
        "comparison_policy": {"tolerance": float(fixture["crosscheck_tolerance"]), "reason": "the finite reserve theorem is checked after independent reconstruction; negative sufficient reserves are retained and no uniform or physical field is inferred"},
    }
    atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"R-422 INTEGRATED PASS {len(checks)}/{len(checks)} systems={p['system_count']} rows={p['conditional_row_count']} eligible={p['eligible_row_count']} positive={p['positive_reserve_row_count']} nonpositive={p['nonpositive_reserve_row_count']} min_safe={p['minimum_safe_reserve']:.6g} Lean=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
