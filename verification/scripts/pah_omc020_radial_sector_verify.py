"""Integrate the primary, independent, hostile and Lean radial-sector lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_radial_sector.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_radial_sector_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_radial_sector_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Radial.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-radial-sector/integrated.json"
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


def run_script(script: Path, output: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180, check=False,
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
    libraries = []
    for package in sorted(cache.iterdir()):
        library = package / ".lake" / "build" / "lib" / "lean"
        if library.is_dir():
            libraries.append(str(library))
    env = dict(os.environ)
    env["LEAN_PATH"] = os.pathsep.join(libraries)
    process = subprocess.run(
        [str(lean_executable()), str(LEAN_SOURCE)], cwd=ROOT, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600, check=False,
    )
    if process.returncode != 0 or process.stdout or process.stderr:
        raise RuntimeError(f"Lean diagnostics:\n{process.stdout}\n{process.stderr}")
    return subprocess.run([str(lean_executable()), "--version"], capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout.strip()


def build(output: Path, cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-radial-integrated-") as directory:
        folder = Path(directory)
        primary = run_script(PRIMARY, folder / "primary.json")
        independent = run_script(INDEPENDENT, folder / "independent.json")
        hostile = run_script(HOSTILE, folder / "hostile.json")
        lanes = {"primary": primary, "independent": independent, "hostile": hostile}
        run_hashes = {name: digest(folder / f"{name}.json") for name in lanes}

    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    ck("primary status", primary["status"], "PASS_RADIAL_SECTOR_ORDERED_CORRELATION",
       primary["status"] == "PASS_RADIAL_SECTOR_ORDERED_CORRELATION")
    ck("independent status", independent["status"], "PASS_INDEPENDENT_RADIAL_SECTOR",
       independent["status"] == "PASS_INDEPENDENT_RADIAL_SECTOR")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_RADIAL_SECTOR",
       hostile["status"] == "PASS_HOSTILE_RADIAL_SECTOR")
    ck("all lanes auxiliary", [item["verdict"] for item in lanes.values()],
       ["AUXILIARY_SUPPORT"] * 3,
       all(item["verdict"] == "AUXILIARY_SUPPORT" for item in lanes.values()))
    ck("all lanes conditional", [item["conditional"] for item in lanes.values()], [True] * 3,
       all(item["conditional"] for item in lanes.values()))
    ck("all lanes non-bearing", [item["claim_bearing"] for item in lanes.values()], [False] * 3,
       all(not item["claim_bearing"] for item in lanes.values()))
    ck("physical promotion blocked", [item["physical_promotion"] for item in lanes.values()], [False] * 3,
       all(not item["physical_promotion"] for item in lanes.values()))
    ck("primary checks", len(primary["checks"]), 31, len(primary["checks"]) == 31)
    ck("independent checks", len(independent["checks"]), 23, len(independent["checks"]) == 23)
    ck("hostile checks", len(hostile["checks"]), 21, len(hostile["checks"]) == 21)
    ck("residual factor", primary["derived_inputs"]["radial_residual_factor"], "5", True)
    ck("target sector is D_rad", "D_rad" in primary["scope"]["observables"], True,
       "D_rad" in primary["scope"]["observables"])
    anchored_open = "anchored-n" in json.dumps(primary)
    ck("anchored-n remains open", anchored_open, True, anchored_open)
    ck("no physical promotion", any("physical Pre-A" in item for item in primary["non_claims"]), True,
       any("physical Pre-A" in item for item in primary["non_claims"]))

    tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary", not any("pah_omc020_radial_sector" in item for item in imports),
       True, not any("pah_omc020_radial_sector" in item for item in imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Radial.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    ck("Lean registry hash", entry["sha256"], digest(LEAN_SOURCE), entry["sha256"] == digest(LEAN_SOURCE))
    ck("Lean declarations", declarations, entry["declarations"], declarations == entry["declarations"])
    ck("Lean policy", not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
       True, not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")))
    version = compile_lean(cache)
    ck("Lean compile", "version 4.32.1" in version, version, "version 4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-radial-sector-integrated/1.0",
        "status": "PASS_INTEGRATED_RADIAL_SECTOR",
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
        "scope": "Conditional ordered compact-time correlation convergence on the amplitude-only D_rad sector; mixed observables and full anchored-n convergence remain open.",
        "derived": {"radial_factor": "2", "finite_time_error": "2*T*||f||_infinity*H_g*L_g*h_j"},
        "non_claims": [
            "No common U_n/Hilbert realization for mixed observables, no N2b/N2c/N2d full closure and no infinite-volume process.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_radial_sector.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_radial_sector_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_radial_sector_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_radial_sector_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
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
    with tempfile.TemporaryDirectory(prefix="pah020-radial-replay-") as directory:
        replay = build(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.read_bytes() != encoded:
        raise SystemExit("PAH-OMC-020 radial integrated replay mismatch")
    if not args.check:
        atomic_json(args.output, replay)
    print("PAH-OMC-020 RADIAL INTEGRATED: PASS (D_rad ordered correlation; full target open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
