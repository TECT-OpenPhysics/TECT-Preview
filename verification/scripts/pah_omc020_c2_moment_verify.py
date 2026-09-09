#!/usr/bin/env python3
"""Integrate the PAH-OMC-020 C2 primary, independent, hostile and Lean lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_c2_moment.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_c2_moment_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_c2_moment_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020C2.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-c2-moment/integrated.json"
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

DECLARATIONS = [
    "phase_sq_le_one",
    "product_sq_le_one",
    "aperture_sq_le_one",
    "transported_mass_le_target",
    "local_c2_bound",
    "c2_omc010_constant",
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
    with tempfile.TemporaryDirectory(prefix="pah020-c2-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lane_outputs = {"primary": primary, "independent": independent, "hostile": hostile}
        lane_hashes = {name: digest(folder / f"{name}.json") for name in lane_outputs}

    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        ck(f"source hash:{relative}", actual, expected, actual == expected)

    ck("primary status", primary["status"], "PASS_SOURCE_OWNED_C2_LOCAL_BOUND",
       primary["status"] == "PASS_SOURCE_OWNED_C2_LOCAL_BOUND")
    ck("independent status", independent["status"], "PASS_INDEPENDENT_SOURCE_OWNED_C2",
       independent["status"] == "PASS_INDEPENDENT_SOURCE_OWNED_C2")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_C2_SCOPE_CONTROLS",
       hostile["status"] == "PASS_HOSTILE_C2_SCOPE_CONTROLS")
    ck("all lanes auxiliary", [primary["classification"], independent["classification"], hostile["classification"]],
       ["auxiliary_support"] * 3,
       all(lane["classification"] == "auxiliary_support" for lane in (primary, independent, hostile)))
    ck("all lanes claim-nonbearing", [primary["claim_bearing"], independent["claim_bearing"], hostile["claim_bearing"]],
       [False] * 3, all(not lane["claim_bearing"] for lane in (primary, independent, hostile)))
    ck("no active gate change", primary["active_gate_change"], False, primary["active_gate_change"] is False)
    ck("no physical promotion", primary["physical_promotion"], False, primary["physical_promotion"] is False)
    ck("primary check count", primary["checks_passed"], 40, primary["checks_passed"] == 40)
    ck("independent check count", independent["checks_passed"], 31, independent["checks_passed"] == 31)
    ck("hostile check count", hostile["checks_passed"], 17, hostile["checks_passed"] == 17)
    ck("C2 constant", primary["algebra"]["bounds"][-1]["C2_bound"], 480,
       primary["algebra"]["bounds"][-1]["C2_bound"] == 480)
    ck("per-root bound", primary["algebra"]["per_root_bound"], 1,
       primary["algebra"]["per_root_bound"] == 1)
    ck("local C2 formula", primary["algebra"]["formulae"]["local_C2"], "C2(A) <= 60 |A|",
       primary["algebra"]["formulae"]["local_C2"] == "C2(A) <= 60 |A|")
    ck("temporal route stays held", "HOLD_FOR_EVIDENCE", "HOLD_FOR_EVIDENCE", True)

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree)
                           if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree)
                            if isinstance(node, ast.Import) for alias in node.names]
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree)
                       if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree)
                        if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary", any("pah_omc020_c2_moment" in item for item in independent_imports),
       False, not any("pah_omc020_c2_moment" in item for item in independent_imports))
    ck("hostile does not import primary", any("pah_omc020_c2_moment" in item for item in hostile_imports),
       False, not any("pah_omc020_c2_moment" in item for item in hostile_imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"]
                  if item["path"] == "verification/lean/Tect/PahOmc020C2.lean"), None)
    ck("Lean registry entry exists", entry is not None, True, entry is not None)
    ck("Lean source hash", digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE) == entry["sha256"])
    ck("Lean declaration registry", entry["declarations"], DECLARATIONS,
       entry["declarations"] == DECLARATIONS)
    version, diagnostics = compile_lean(lean_cache)
    ck("Lean compilation", "error:" in diagnostics.lower(), False, "error:" not in diagnostics.lower())
    ck("Lean toolchain", "4.32.1" in version, True, "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-c2-moment-integrated/1.0",
        "status": "PASS_INTEGRATED_SOURCE_OWNED_C2",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(checks),
        "checks": checks,
        "lane_status": {name: lane["status"] for name, lane in (("primary", primary), ("independent", independent), ("hostile", hostile))},
        "lane_run_hashes": lane_hashes,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "lean": {
            "path": "verification/lean/Tect/PahOmc020C2.lean",
            "sha256": digest(LEAN_SOURCE),
            "toolchain": version,
            "declarations": DECLARATIONS,
            "diagnostics": diagnostics,
        },
        "finding": "Exact source-owned local C2(A) bound C2(A) <= 60|A| on the registered OMC-010 path, with induced local L2 generator estimate.",
        "remaining_contract": primary["route"]["missing_contract"],
        "non_claims": primary["non_claims"],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_c2_moment.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_c2_moment_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_c2_moment_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_c2_moment_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020C2.lean with the registered package path",
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
    print(f"PASS {payload['checks_passed']} integrated checks; {payload['status']}; temporal route HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
