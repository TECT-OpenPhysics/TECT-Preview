#!/usr/bin/env python3
"""Integrate the OMC-004 root-overlap primary, independent and hostile lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_root_overlap_bound.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_root_overlap_bound_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_root_overlap_bound_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Overlap.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-overlap/integrated.json"
)


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


def execute(script: Path, output: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=240, check=False,
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


def compile_lean(cache: Path) -> str:
    if not cache.is_dir():
        raise FileNotFoundError(f"Lean package cache not found: {cache}")
    libraries = []
    for package in sorted(cache.iterdir()):
        library = package / ".lake" / "build" / "lib" / "lean"
        if library.is_dir():
            libraries.append(str(library))
    env = dict(os.environ)
    env["LEAN_PATH"] = os.pathsep.join(libraries)
    lean = lean_executable()
    process = subprocess.run([str(lean), str(LEAN_SOURCE)], cwd=ROOT, env=env,
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=600, check=False)
    if process.returncode != 0 or process.stdout or process.stderr:
        raise RuntimeError(f"Lean diagnostics:\n{process.stdout}\n{process.stderr}")
    return subprocess.run([str(lean), "--version"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=True).stdout.strip()


def run(output: Path, cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-overlap-integrated-") as directory:
        folder = Path(directory)
        primary = execute(PRIMARY, folder / "primary.json")
        independent = execute(INDEPENDENT, folder / "independent.json")
        hostile = execute(HOSTILE, folder / "hostile.json")
        lanes = {"primary": primary, "independent": independent, "hostile": hostile}
        run_hashes = {name: digest(folder / f"{name}.json") for name in lanes}
    checks = []

    def ck(name: str, ok: bool, actual: object, expected: object) -> None:
        if not ok:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    ck("primary status", primary["status"] == "PASS_ROOT_OVERLAP_BOUND", primary["status"], "PASS_ROOT_OVERLAP_BOUND")
    ck("independent status", independent["status"] == "PASS_INDEPENDENT_ROOT_OVERLAP", independent["status"], "PASS_INDEPENDENT_ROOT_OVERLAP")
    ck("hostile status", hostile["status"] == "PASS_HOSTILE_ROOT_OVERLAP", hostile["status"], "PASS_HOSTILE_ROOT_OVERLAP")
    ck("all lanes auxiliary", all(item["verdict"] == "AUXILIARY_SUPPORT" for item in lanes.values()),
       [item["verdict"] for item in lanes.values()], "AUXILIARY_SUPPORT")
    ck("all lanes claim-nonbearing", all(not item["claim_bearing"] for item in lanes.values()),
       [item["claim_bearing"] for item in lanes.values()], [False, False, False])
    ck("Duhamel attribution open", primary["n2c_status"]["word_to_duhamel_attribution"] == "NOT_PROVED",
       primary["n2c_status"]["word_to_duhamel_attribution"], "NOT_PROVED")
    ck("primary branching bound", primary["derived_constants"]["overlap_branching_bound"] == 144,
       primary["derived_constants"]["overlap_branching_bound"], 144)
    ck("independent branching bound", independent["derived_constants"]["overlap_branching"] == 144,
       independent["derived_constants"]["overlap_branching"], 144)

    tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    ck("independent non-importing", not any("pah_omc020_root_overlap_bound" in item for item in imports),
       imports, "no primary import")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Overlap.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    ck("Lean registry hash", entry["sha256"] == digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE))
    ck("Lean declarations", declarations == entry["declarations"], declarations, entry["declarations"])
    ck("Lean policy", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "clean")
    version = compile_lean(cache)
    ck("Lean compile", "version 4.32.1" in version, version, "Lean 4.32.1")

    payload = {
        "schema": "tect/pah-omc020-overlap-integrated/1.0",
        "status": "PASS_ROOT_OVERLAP_INTEGRATED",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "scripts": {
            "primary": {"path": str(PRIMARY.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(PRIMARY)},
            "independent": {"path": str(INDEPENDENT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(INDEPENDENT)},
            "hostile": {"path": str(HOSTILE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(HOSTILE)},
            "lean": {"path": str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(LEAN_SOURCE), "version": version},
        },
        "run_hashes": run_hashes,
        "lane_counts": {name: len(item["checks"]) for name, item in lanes.items()},
        "derived_constants": {"roots_per_column": 16, "footprint_radius": 2, "overlap_branching": 144},
        "scope": "Exact OMC-004 PH/LK/AP dependency-footprint overlap bound after the R-511 j-limit; connected-word-to-Duhamel attribution remains open.",
        "next_single_question": "Can a source-valid coupling or Duhamel construction bound the exact A_n^(out,m)Q_n(s)g term by the connected-word event with b=144?",
        "non_claims": [
            "No N2c/N4 boundary-escape theorem, anchored-n convergence, common U_n or R-512 minimal-form selection.",
            "No infinite-volume, continuum or physical Pre-A/spacetime/QFT/gravity/Yang-Mills/mass-gap/TOE result.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_root_overlap_bound.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-overlap/primary.json",
            "independent": "python -X utf8 codes/foundations/pah_omc020_root_overlap_bound_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-overlap/independent.json",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_root_overlap_bound_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-overlap/hostile.json",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_root_overlap_bound_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        },
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--lean-cache", type=Path, default=ROOT / "verification/lean/.lake/packages")
    args = parser.parse_args()
    if args.check and not args.output.exists():
        raise SystemExit("integrated output missing")
    with tempfile.TemporaryDirectory(prefix="pah020-overlap-replay-") as directory:
        replay = run(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 overlap integrated replay mismatch")
    else:
        atomic_json(args.output, replay)
    print("PAH-OMC-020 ROOT OVERLAP INTEGRATED: PASS (Duhamel attribution remains open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
