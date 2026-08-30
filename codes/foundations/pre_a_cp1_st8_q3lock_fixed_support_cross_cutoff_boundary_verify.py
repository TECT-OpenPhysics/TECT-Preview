#!/usr/bin/env python3
"""Integrated verifier for the R-437 finite fixed-support boundary package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-fixed-support-cross-cutoff-boundary-manifest.json"
PRIMARY = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_support_cross_cutoff_boundary.py"
INDEPENDENT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_support_cross_cutoff_boundary_independent.py"
HOSTILE = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_fixed_support_cross_cutoff_boundary_hostile.py"
LEAN = ROOT / "verification/lean/Tect/R437.lean"
SLUG = "fixed_support_cross_cutoff_boundary"
RUN_ROOT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
PRIMARY_OUTPUT = RUN_ROOT / f"2026-08-30-primary-{SLUG}/primary.json"
INDEPENDENT_OUTPUT = RUN_ROOT / f"2026-08-30-independent-{SLUG}/independent.json"
HOSTILE_OUTPUT = RUN_ROOT / f"2026-08-30-hostile-{SLUG}/hostile.json"
INTEGRATED_OUTPUT = RUN_ROOT / f"2026-08-30-integrated-{SLUG}/integrated.json"
LAKE = Path(os.environ.get("TECT_LAKE", "C:/Users/NaEun/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--output", type=Path, default=INTEGRATED_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-437" and manifest["exploration_id"] == "EXP-001282" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-437/EXP-001282/false", "provenance")
    artifacts = [PRIMARY, INDEPENDENT, HOSTILE, LEAN]
    check("artifacts present", all(path.is_file() for path in artifacts), [path.relative_to(ROOT).as_posix() for path in artifacts if not path.is_file()], "all R-437 artifacts", "provenance")
    hashes = {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts}
    check("artifact hashes distinct", len(set(hashes.values())) == len(hashes), hashes, "distinct source hashes", "provenance")
    lean_text = LEAN.read_text(encoding="utf-8")
    markers = manifest["lean_crosscheck"]["theorem_markers"]
    check("Lean markers", all(marker in lean_text for marker in markers), markers, "declared theorem markers", "Lean")
    check("Lean policy", not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), "forbidden tokens absent", "clean finite scalar file", "Lean")

    outputs: dict[str, str] = {}
    for script, expected in ((PRIMARY, PRIMARY_OUTPUT), (INDEPENDENT, INDEPENDENT_OUTPUT), (HOSTILE, HOSTILE_OUTPUT)):
        if args.reuse_existing and expected.is_file():
            outputs[script.name] = f"reused {expected.relative_to(ROOT).as_posix()}"
            check(f"reuse {script.name}", True, outputs[script.name], "existing output", "executables")
        else:
            completed = command([os.fspath(Path(sys.executable)), "-X", "utf8", os.fspath(script), "--self-test"], ROOT)
            outputs[script.name] = (completed.stdout + completed.stderr).strip()
            check(f"run {script.name}", completed.returncode == 0 and expected.is_file(), outputs[script.name][-1800:], "exit 0 and output", "executables")

    lean = command([os.fspath(LAKE), "env", "lean", "Tect/R437.lean"], ROOT / "verification/lean")
    outputs["lean"] = (lean.stdout + lean.stderr).strip()
    check("Lean compile", lean.returncode == 0 and "error:" not in outputs["lean"].lower(), outputs["lean"][-1200:], "exit 0 without errors", "Lean")

    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT_OUTPUT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE_OUTPUT.read_text(encoding="utf-8"))
    p = primary["derived"]
    i = independent["derived"]
    scope = manifest["scope"]
    threshold = Decimal(manifest["comparison_contract"]["tail_threshold"])
    check("primary certificate", primary["verdict"] == "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY" and primary["assertion_count"] == 14, [primary["verdict"], primary["assertion_count"]], "14/14 finite boundary checks", "primary")
    check("strict d17/d18 crossing", Decimal(p["d17_index_interval"][1]) < threshold < Decimal(p["d18_index_interval"][0]), [p["d17_index_interval"], p["d18_index_interval"]], "d17 upper < 4 < d18 lower", "interval")
    crossing_index = p["comparison"]["crossing_index"]
    check("primary support statuses", p["d17_status"] == "core" and p["d18_status"] == "tail" and crossing_index == manifest["comparison_contract"]["crossing_index"], [p["d17_status"], p["d18_status"], crossing_index], "core/tail at crossing index", "support")
    check("independent control", independent["verdict"] == "INDEPENDENT_FIXED_SUPPORT_BOUNDARY_CONTROL" and independent["assertion_count"] == 9 and i["d17_split"]["core"] != i["d18_split"]["core"], independent["derived"], "9/9 independent support control", "independent")
    check("hostile controls", hostile["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and hostile["assertion_count"] == 8 and hostile["scope"]["hostile_mutations_rejected"], hostile["scope"], "8/8 hostile mutations rejected", "hostile")
    closed = {key: value for key, value in scope.items() if key.endswith("_closed")}
    check("scope firewall", all(value is False for value in closed.values()) and scope["finite_cross_cutoff_threshold_crossing_certified"] and scope["same_row_rule_identity_checked"], scope, "finite boundary true; all promotion flags false", "scope")

    payload = {
        "schema": "tect/pre-a-r437-integrated/1.0",
        "result_id": "R-437",
        "exploration_id": "EXP-001282",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "integrated",
        "verdict": "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"crossing_index": crossing_index, "d17_index_interval": p["d17_index_interval"], "d18_index_interval": p["d18_index_interval"], "d17_status": p["d17_status"], "d18_status": p["d18_status"], "fixed_support_uniformity_closed": False, "increasing_core_tail_modulus_closed": False, "lean": "PASS", "outputs": outputs},
        "source_hashes": hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-437 INTEGRATED FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY {len(checks)}/{len(checks)} d17={p['d17_status']} d18={p['d18_status']} Lean=PASS", flush=True)
    if args.self_test:
        assert payload["verdict"] == "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY"
        print("R-437 INTEGRATED SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
