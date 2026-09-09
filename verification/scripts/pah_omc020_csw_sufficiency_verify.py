#!/usr/bin/env python3
"""Integrate the primary, independent, hostile and Lean C_sw audits."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_csw_sufficiency_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_csw_sufficiency_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_csw_sufficiency_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Csw.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-csw-sufficiency/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json":
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md":
        "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}

LEAN_DECLARATIONS = [
    "denominator_pos",
    "detailed_balance",
    "first_moment_formula",
    "first_moment_lt_two",
    "energy_formula",
    "energy_lt_four",
    "generator_l2_formula",
    "generator_l2_unbounded",
    "fixed_first_moment_and_unbounded_l2",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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


def run_lane(script: Path, output: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed: {completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def lean_executable() -> Path:
    candidates = list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean.exe"))
    candidates += list((Path.home() / ".elan" / "toolchains").glob("**/bin/lean"))
    exact = [path for path in candidates if "v4.32.1" in str(path)]
    if exact:
        return exact[0]
    found = shutil.which("lean")
    if found:
        return Path(found)
    raise FileNotFoundError("Lean 4.32.1 executable not found")


def compile_lean(cache: Path) -> tuple[str, str]:
    libraries = []
    if cache.exists():
        for package in sorted(cache.iterdir()):
            library = package / ".lake" / "build" / "lib" / "lean"
            if library.is_dir():
                libraries.append(str(library))
    if not libraries:
        raise FileNotFoundError(f"No Lean package libraries under {cache}")
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
    if process.returncode != 0 or re.search(r"(?im)\berror:", diagnostics):
        raise RuntimeError(f"Lean diagnostics:\n{diagnostics}")
    version = subprocess.run(
        [str(lean_executable()), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    return version, diagnostics


def build(output: Path, lean_cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-csw-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lane_outputs = {
            "primary": primary,
            "independent": independent,
            "hostile": hostile,
        }
        run_hashes = {name: digest(folder / f"{name}.json") for name in lane_outputs}

    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        ck(f"source hash:{relative}", actual, expected, actual == expected)

    ck("primary status", primary["status"], "PASS_CSW_FIRST_MOMENT_SUFFICIENCY_OBSTRUCTION",
       primary["status"] == "PASS_CSW_FIRST_MOMENT_SUFFICIENCY_OBSTRUCTION")
    ck("independent status", independent["status"], "PASS_INDEPENDENT_CSW_FIRST_MOMENT_OBSTRUCTION",
       independent["status"] == "PASS_INDEPENDENT_CSW_FIRST_MOMENT_OBSTRUCTION")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_CSW_SCOPE_CONTROLS",
       hostile["status"] == "PASS_HOSTILE_CSW_SCOPE_CONTROLS")
    lanes = (primary, independent, hostile)
    ck("all lanes hold", [lane["verdict"] for lane in lanes],
       ["HOLD_FOR_EVIDENCE"] * len(lanes), all(lane["verdict"] == "HOLD_FOR_EVIDENCE" for lane in lanes))
    ck("primary is auxiliary", primary["classification"], "auxiliary_support",
       primary["classification"] == "auxiliary_support")
    ck("no physical promotion", primary["route"]["physical_promotion"], False,
       primary["route"]["physical_promotion"] is False)
    ck("primary check count", len(primary["checks"]), 46, len(primary["checks"]) == 46)
    ck("independent check count", len(independent["checks"]), 27, len(independent["checks"]) == 27)
    ck("hostile check count", len(hostile["checks"]), 13, len(hostile["checks"]) == 13)
    ck("derived C_sw", primary["source_constants"]["c_sw"], 540,
       primary["source_constants"]["c_sw"] == 540)
    ck("first moment formula", primary["abstract_witness"]["formulae"]["first_moment"],
       "2M/(M+1)<2<=C_sw", primary["abstract_witness"]["formulae"]["first_moment"] == "2M/(M+1)<2<=C_sw")
    ck("L2 formula", primary["abstract_witness"]["formulae"]["generator_l2_sq"], "4M -> infinity",
       primary["abstract_witness"]["formulae"]["generator_l2_sq"] == "4M -> infinity")
    ck("missing second-moment contract", any("second-rate-moment" in item for item in primary["route"]["missing_contract"]),
       True, any("second-rate-moment" in item for item in primary["route"]["missing_contract"]))
    ck("primary-independent shared hashes", all(
        primary["source_hashes"][key] == independent["source_hashes"][key]
        for key in set(primary["source_hashes"]) & set(independent["source_hashes"])), True,
       all(primary["source_hashes"][key] == independent["source_hashes"][key]
           for key in set(primary["source_hashes"]) & set(independent["source_hashes"])))
    ck("primary-hostile shared hashes", all(
        primary["source_hashes"][key] == hostile["source_hashes"][key]
        for key in set(primary["source_hashes"]) & set(hostile["source_hashes"])), True,
       all(primary["source_hashes"][key] == hostile["source_hashes"][key]
           for key in set(primary["source_hashes"]) & set(hostile["source_hashes"])))
    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree)
                           if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree)
                            if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary", any("pah_omc020_csw_sufficiency_audit" in item for item in independent_imports),
       False, not any("pah_omc020_csw_sufficiency_audit" in item for item in independent_imports))
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree)
                       if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree)
                        if isinstance(node, ast.Import) for alias in node.names]
    ck("hostile does not import primary", any("pah_omc020_csw_sufficiency_audit" in item for item in hostile_imports),
       False, not any("pah_omc020_csw_sufficiency_audit" in item for item in hostile_imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"]
                  if item["path"] == "verification/lean/Tect/PahOmc020Csw.lean"), None)
    ck("Lean registry entry exists", entry is not None, True, entry is not None)
    ck("Lean source hash", digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE) == entry["sha256"])
    ck("Lean declaration registry", entry["declarations"], LEAN_DECLARATIONS,
       entry["declarations"] == LEAN_DECLARATIONS)
    version, diagnostics = compile_lean(lean_cache)
    ck("Lean compilation", "error:" in diagnostics.lower(), False, "error:" not in diagnostics.lower())
    ck("Lean toolchain", "4.32.1" in version, True, "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-csw-sufficiency-integrated/1.0",
        "status": "PASS_INTEGRATED_CSW_FIRST_MOMENT_OBSTRUCTION",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(checks),
        "checks": checks,
        "lane_status": {
            "primary": primary["status"],
            "independent": independent["status"],
            "hostile": hostile["status"],
        },
        "lane_run_hashes": run_hashes,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "lean": {
            "path": "verification/lean/Tect/PahOmc020Csw.lean",
            "sha256": digest(LEAN_SOURCE),
            "toolchain": version,
            "declarations": LEAN_DECLARATIONS,
            "diagnostics": diagnostics,
        },
        "finding": primary["route"]["finding"],
        "next_contract": primary["route"]["missing_contract"],
        "non_claims": primary["non_claims"],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_csw_sufficiency_audit.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_csw_sufficiency_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lean-cache", type=Path,
                        default=ROOT / "verification/lean/.lake/packages")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(args.output, args.lean_cache)
    if args.check:
        replay = build(args.output, args.lean_cache)
        if replay != json.loads(args.output.read_text(encoding="utf-8")):
            raise SystemExit("deterministic replay mismatch")
    print(f"PASS {payload['checks_passed']} integrated checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
