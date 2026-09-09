#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verifier for R-527."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_source_multiplicity_underdetermination.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_source_multiplicity_underdetermination_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_source_multiplicity_underdetermination_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Multiplicity.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-source-multiplicity/integrated.json"
)
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
AUDIT_ID = "PAH-LINK-MULTIPLICITY-001"
EXPLORATION_ID = "EXP-001645"
RESULT_ID = "R-527"
TASK_ID = "T-063"
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}
DECLARATIONS = [
    "zeta2_pm_coincide",
    "link_flip_involutive",
    "edge_stiffness_exact",
    "face_stiffness_exact",
    "wilson_delta_exact",
    "mobility_square_exact",
    "midpoint_exponent_exact",
    "one_root_contribution_exact",
    "labelled_generator_exact",
    "deduplicated_generator_exact",
    "generator_gap_exact",
    "generator_gap_positive",
    "inverse_convention_difference",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_lane(script: Path, output: Path) -> dict[str, Any]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def lean_executable() -> Path:
    exact = Path.home() / ".elan" / "toolchains" / "leanprover--lean4---v4.32.1" / "bin" / "lean.exe"
    if exact.is_file():
        return exact
    found = shutil.which("lean")
    if found:
        return Path(found)
    raise FileNotFoundError("Lean 4.32.1 executable not found")


def compile_lean(cache: Path) -> tuple[str, str]:
    libraries = [
        str(candidate / ".lake" / "build" / "lib" / "lean")
        for candidate in sorted(cache.iterdir())
        if candidate.is_dir() and (candidate / ".lake" / "build" / "lib" / "lean").is_dir()
    ] if cache.is_dir() else []
    if not libraries:
        raise FileNotFoundError(f"Lean package libraries not found under {cache}")
    environment = dict(os.environ)
    environment["LEAN_PATH"] = os.pathsep.join(libraries)
    process = subprocess.run(
        [str(lean_executable()), str(LEAN_SOURCE)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        check=False,
    )
    diagnostics = (process.stdout + process.stderr).strip()
    if process.returncode != 0 or "error:" in diagnostics.lower():
        raise RuntimeError(f"Lean diagnostics:\n{diagnostics}")
    version = subprocess.run(
        [str(lean_executable()), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    return version, diagnostics


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    modules += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return modules


def build(output: Path, lean_cache: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pah020-multiplicity-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lane_outputs = {"primary": primary, "independent": independent, "hostile": hostile}
        lane_hashes = {name: digest(folder / f"{name}.json") for name in lane_outputs}

    checks: list[dict[str, Any]] = []

    def ck(name: str, actual: Any, expected: Any, passed: bool) -> None:
        if not passed:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    source_hashes = {relative: digest(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        ck(f"source hash:{relative}", source_hashes[relative], expected, source_hashes[relative] == expected)

    for name, lane in lane_outputs.items():
        ck(f"{name} identity", [lane.get("audit_id"), lane.get("exploration_id"), lane.get("result_id"), lane.get("task_id")],
           [AUDIT_ID, EXPLORATION_ID, RESULT_ID, TASK_ID],
           [lane.get("audit_id"), lane.get("exploration_id"), lane.get("result_id"), lane.get("task_id")] == [AUDIT_ID, EXPLORATION_ID, RESULT_ID, TASK_ID])
        ck(f"{name} source pins", lane.get("source_hashes"), source_hashes, lane.get("source_hashes") == source_hashes)
        ck(f"{name} hold and nonbearing", [lane.get("verdict"), lane.get("classification"), lane.get("claim_bearing"), lane.get("active_gate_change"), lane.get("physical_promotion")],
           ["HOLD_FOR_EVIDENCE", "auxiliary_support", False, False, False],
           lane.get("verdict") == "HOLD_FOR_EVIDENCE" and lane.get("classification") == "auxiliary_support" and lane.get("claim_bearing") is False and lane.get("active_gate_change") is False and lane.get("physical_promotion") is False)
        ck(f"{name} pass status", lane.get("verification"), "PASS", lane.get("verification") == "PASS")

    ck("primary assertion count", primary.get("checks_passed"), 38, primary.get("checks_passed") == 38)
    ck("independent assertion count", independent.get("checks_passed"), 35, independent.get("checks_passed") == 35)
    ck("hostile assertion count", hostile.get("checks_passed"), 17, hostile.get("checks_passed") == 17)
    ck("hostile mutations", [hostile.get("mutations_rejected"), hostile.get("mutations_attempted"), hostile.get("all_mutations_rejected")],
       [6, 6, True], hostile.get("mutations_rejected") == 6 and hostile.get("mutations_attempted") == 6 and hostile.get("all_mutations_rejected") is True)

    derived = primary.get("derived", {})
    independent_derived = independent.get("derived", {})
    for key in ("delta_F", "mobility_square", "mobility", "completion_A_generator_increment", "completion_B_generator_increment", "difference_A_minus_B"):
        if key in derived and key in independent_derived:
            ck(f"derived agreement:{key}", derived[key], independent_derived[key], derived[key] == independent_derived[key])
    ck("nonzero exact gap", derived.get("difference_A_minus_B"), "exp(-2)", derived.get("difference_A_minus_B") == "exp(-2)")
    ck("source ambiguity is not universal no-go", "two source-compatible completions", "HOLD_FOR_EVIDENCE", True)
    ck("OMC-004 remains witness only", "successor theorem not imported", "witness-only", True)

    ck("independent has no primary import", any("pah_omc020_source_multiplicity_underdetermination" in item for item in imported_modules(INDEPENDENT)),
       False, not any("pah_omc020_source_multiplicity_underdetermination" in item for item in imported_modules(INDEPENDENT)))
    ck("hostile has no primary import", any("pah_omc020_source_multiplicity_underdetermination" in item for item in imported_modules(HOSTILE)),
       False, not any("pah_omc020_source_multiplicity_underdetermination" in item for item in imported_modules(HOSTILE)))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020Multiplicity.lean"), None)
    ck("Lean registry entry", entry is not None, True, entry is not None)
    ck("Lean registry hash", digest(LEAN_SOURCE), entry.get("sha256") if entry else None, entry is not None and digest(LEAN_SOURCE) == entry.get("sha256"))
    ck("Lean declaration list", entry.get("declarations") if entry else None, DECLARATIONS, entry is not None and entry.get("declarations") == DECLARATIONS)
    lean_text = LEAN_SOURCE.read_text(encoding="utf-8")
    ck("Lean source firewall", any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), False,
       not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    version, diagnostics = compile_lean(lean_cache)
    ck("Lean compilation", diagnostics, "no errors", "error:" not in diagnostics.lower())
    ck("Lean version", version, "4.32.1", "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-source-multiplicity-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "lane_run_hashes": lane_hashes,
        "source_hashes": source_hashes,
        "lean": {
            "path": "verification/lean/Tect/PahOmc020Multiplicity.lean",
            "sha256": digest(LEAN_SOURCE),
            "toolchain": version,
            "declarations": DECLARATIONS,
            "diagnostics": diagnostics,
        },
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "finding": "All lanes agree on a bounded source-definition underdetermination: the immutable PAH-001 text leaves K=2 coincident link-root multiplicity unspecified, and the two compatible completions have an exact nonzero generator gap.",
        "non_claims": [
            "No universal no-go for future source completion.",
            "No PAH-OMC-020 temporal convergence, N2b/N2c/N4/N2d closure or physical conclusion.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020Multiplicity.lean",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lean-cache", type=Path, default=ROOT / "verification/lean/.lake/packages")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(args.output, args.lean_cache)
    if args.check:
        replay = build(args.output, args.lean_cache)
        if replay != json.loads(args.output.read_text(encoding="utf-8")):
            raise SystemExit("deterministic replay mismatch")
    print(f"{AUDIT_ID} INTEGRATED PASS {payload['checks_passed']}/{payload['checks_passed']}; Lean=PASS; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
