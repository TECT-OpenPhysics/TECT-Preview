#!/usr/bin/env python3
"""Integrate the PAH-OMC-020 Duhamel/coupling attribution lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_duhamel_attribution.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_duhamel_attribution_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_duhamel_attribution_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Duhamel.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-duhamel-attribution/integrated.json"
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
    with tempfile.TemporaryDirectory(prefix="pah020-duhamel-integrated-") as directory:
        folder = Path(directory)
        primary = execute(PRIMARY, folder / "primary.json")
        independent = execute(INDEPENDENT, folder / "independent.json")
        hostile = execute(HOSTILE, folder / "hostile.json")
        lanes = {"primary": primary, "independent": independent, "hostile": hostile}
        run_hashes = {name: digest(folder / f"{name}.json") for name in lanes}

    checks: list[dict] = []

    def ck(name: str, ok: bool, actual: object, expected: object) -> None:
        if not ok:
            raise AssertionError(name)
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    ck("primary status", primary["status"] == "PASS_DUHAMEL_ATTRIBUTION_BOUND",
       primary["status"], "PASS_DUHAMEL_ATTRIBUTION_BOUND")
    ck("independent status", independent["status"] == "PASS_INDEPENDENT_DUHAMEL_ATTRIBUTION",
       independent["status"], "PASS_INDEPENDENT_DUHAMEL_ATTRIBUTION")
    ck("hostile status", hostile["status"] == "PASS_HOSTILE_DUHAMEL_ATTRIBUTION",
       hostile["status"], "PASS_HOSTILE_DUHAMEL_ATTRIBUTION")
    ck("all lanes auxiliary", all(item["verdict"] == "AUXILIARY_SUPPORT" for item in lanes.values()),
       [item["verdict"] for item in lanes.values()], "AUXILIARY_SUPPORT")
    ck("all lanes claim-nonbearing", all(not item["claim_bearing"] for item in lanes.values()),
       [item["claim_bearing"] for item in lanes.values()], [False, False, False])
    ck("conditional status retained", all(item["conditional"] for item in lanes.values()),
       [item["conditional"] for item in lanes.values()], [True, True, True])
    ck("physical promotion blocked", all(not item["physical_promotion"] for item in lanes.values()),
       [item["physical_promotion"] for item in lanes.values()], [False, False, False])
    ck("primary N4 conditional", primary["n2c_status"]["boundary_escape_N4"].startswith("PASS_CONDITIONAL"),
       primary["n2c_status"]["boundary_escape_N4"], "PASS_CONDITIONAL")
    ck("primary anchored-n open", primary["n2c_status"]["anchored_n"] == "NOT_DISCHARGED",
       primary["n2c_status"]["anchored_n"], "NOT_DISCHARGED")
    ck("connectivity input", primary["derived_constants"]["overlap_branching"] == 144,
       primary["derived_constants"]["overlap_branching"], 144)
    ck("two-copy input", primary["derived_constants"]["two_copy_rate_factor"] == 2,
       primary["derived_constants"]["two_copy_rate_factor"], 2)
    ck("effective coupling input", primary["derived_constants"]["effective_coupling_branching"] == 288,
       primary["derived_constants"]["effective_coupling_branching"], 288)
    ck("independent effective input", independent["derived_constants"]["effective_coupling_branching"] == 288,
       independent["derived_constants"]["effective_coupling_branching"], 288)
    tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    ck("independent non-importing", not any("pah_omc020_duhamel_attribution" in item for item in imports),
       imports, "no primary import")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Duhamel.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    ck("Lean registry hash", entry["sha256"] == digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE))
    ck("Lean declarations", declarations == entry["declarations"], declarations, entry["declarations"])
    ck("Lean policy", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), "clean", "clean")
    version = compile_lean(cache)
    ck("Lean compile", "version 4.32.1" in version, version, "Lean 4.32.1")

    payload = {
        "schema": "tect/pah-omc020-duhamel-attribution-integrated/1.0",
        "status": "PASS_DUHAMEL_ATTRIBUTION_INTEGRATED",
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
        "derived_constants": {
            "overlap_branching": 144,
            "two_copy_rate_factor": 2,
            "effective_coupling_branching": 288,
        },
        "scope": "Conditional source-local finite-fibre Duhamel/coupling attribution for the exact PAH-OMC-004 PH/LK/AP generator after the R-511 j-limit; anchored-n passage remains open.",
        "next_single_question": "Can this finite-fibre attribution be lifted through a source-authorized common U_n/Hilbert realization and terminal-square-compatible comparison map?",
        "non_claims": [
            "No N2a common U_n, N2b liminf/recovery or N2d minimal-form identification.",
            "No anchored-n, infinite-volume, continuum or physical Pre-A/spacetime/QFT/gravity/Yang-Mills/mass-gap/TOE conclusion.",
            "External stochastic Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_duhamel_attribution.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-duhamel-attribution/primary.json",
            "independent": "python -X utf8 codes/foundations/pah_omc020_duhamel_attribution_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-duhamel-attribution/independent.json",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_duhamel_attribution_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-duhamel-attribution/hostile.json",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_duhamel_attribution_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
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
    with tempfile.TemporaryDirectory(prefix="pah020-duhamel-replay-") as directory:
        replay = run(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 Duhamel integrated replay mismatch")
    else:
        atomic_json(args.output, replay)
    print("PAH-OMC-020 DUHAMEL ATTRIBUTION INTEGRATED: PASS (N4 conditional; anchored-n open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
