"""Integrate primary, independent, hostile and Lean projective-envelope lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_projective_correlation.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_projective_correlation_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_projective_correlation_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Projective.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-projective-correlation/integrated.json"
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
    exact = [candidate for candidate in candidates if "v4.32.1" in str(candidate)]
    if exact:
        return exact[0]
    found = shutil.which("lean")
    if found:
        return Path(found)
    raise FileNotFoundError("Lean 4.32.1 executable not found")


def compile_lean(cache: Path) -> str:
    libraries: list[str] = []
    if cache.exists():
        for package in sorted(cache.iterdir()):
            library = package / ".lake" / "build" / "lib" / "lean"
            if library.is_dir():
                libraries.append(str(library))
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
    if process.returncode != 0 or process.stdout or process.stderr:
        raise RuntimeError(f"Lean diagnostics:\n{process.stdout}\n{process.stderr}")
    return subprocess.run(
        [str(lean_executable()), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def build(output: Path, cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-projective-integrated-") as directory:
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

    ck("primary status", primary["status"], "PASS_PROJECTIVE_LOCAL_CORRELATION_ENVELOPE",
       primary["status"] == "PASS_PROJECTIVE_LOCAL_CORRELATION_ENVELOPE")
    ck("independent status", independent["status"], "PASS_INDEPENDENT_PROJECTIVE_ENVELOPE",
       independent["status"] == "PASS_INDEPENDENT_PROJECTIVE_ENVELOPE")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_PROJECTIVE_ENVELOPE",
       hostile["status"] == "PASS_HOSTILE_PROJECTIVE_ENVELOPE")
    ck("all lanes auxiliary", [lane["verdict"] for lane in lanes.values()],
       ["AUXILIARY_SUPPORT"] * 3,
       all(lane["verdict"] == "AUXILIARY_SUPPORT" for lane in lanes.values()))
    ck("all lanes conditional", [lane["conditional"] for lane in lanes.values()],
       [True] * 3, all(lane["conditional"] for lane in lanes.values()))
    ck("all lanes non-bearing", [lane["claim_bearing"] for lane in lanes.values()],
       [False] * 3, all(not lane["claim_bearing"] for lane in lanes.values()))
    ck("all lanes block physical promotion", [lane["physical_promotion"] for lane in lanes.values()],
       [False] * 3, all(not lane["physical_promotion"] for lane in lanes.values()))
    ck("primary checks", len(primary["checks"]), 50, len(primary["checks"]) == 50)
    ck("independent checks", len(independent["checks"]), 35, len(independent["checks"]) == 35)
    ck("hostile checks", len(hostile["checks"]), 31, len(hostile["checks"]) == 31)
    shared_hashes = sorted(set(primary["source_hashes"]) & set(independent["source_hashes"]))
    hashes_agree = all(
        primary["source_hashes"][key] == independent["source_hashes"][key]
        for key in shared_hashes
    )
    ck("shared source hashes agree", hashes_agree, True, hashes_agree)
    ck("effective branching", primary["derived_inputs"]["effective_branching"], 288,
       primary["derived_inputs"]["effective_branching"] == 288)
    ck("finite word cutoff", primary["derived_inputs"]["word_cutoff"], 6,
       primary["derived_inputs"]["word_cutoff"] == 6)
    ck("support first-root bound", primary["derived_inputs"]["first_root_bound"], 112,
       primary["derived_inputs"]["first_root_bound"] == 112)
    ck("n envelope is not a semigroup assertion",
       "common U_n" in " ".join(primary["missing_assumptions"]), True,
       "common U_n" in " ".join(primary["missing_assumptions"]))
    ck("physical firewall in primary",
       any("physical Pre-A" in item for item in primary["non_claims"]), True,
       any("physical Pre-A" in item for item in primary["non_claims"]))
    ck("physical firewall in hostile",
       any("physical Pre-A" in item for item in hostile["non_claims"]), True,
       any("physical Pre-A" in item for item in hostile["non_claims"]))

    tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary",
       not any("pah_omc020_projective_correlation" in item for item in imports),
       True, not any("pah_omc020_projective_correlation" in item for item in imports))
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree)
                        if isinstance(node, ast.Import) for alias in node.names]
    ck("hostile does not import primary",
       not any("pah_omc020_projective_correlation" in item for item in hostile_imports),
       True, not any("pah_omc020_projective_correlation" in item for item in hostile_imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Projective.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    ck("Lean registry hash", entry["sha256"], digest(LEAN_SOURCE),
       entry["sha256"] == digest(LEAN_SOURCE))
    ck("Lean declaration list", declarations, entry["declarations"],
       declarations == entry["declarations"])
    forbidden = ("sorry", "admit", "axiom", "unsafe")
    ck("Lean source policy", not any(token in source for token in forbidden), True,
       not any(token in source for token in forbidden))
    version = compile_lean(cache)
    ck("Lean 4.32.1 compile", "version 4.32.1" in version, version, "version 4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-projective-correlation-integrated/1.0",
        "status": "PASS_INTEGRATED_PROJECTIVE_ENVELOPE",
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
            "lean": {"path": str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                     "sha256": digest(LEAN_SOURCE), "version": version},
        },
        "run_hashes": run_hashes,
        "lane_counts": {name: len(lane["checks"]) for name, lane in lanes.items()},
        "scope": "Conditional finite-word scalar n-Cauchy envelope for one non-radial grade-blind local cylinder; common U_n and full anchored semigroup remain open.",
        "derived": {
            "overlap_branching": primary["derived_inputs"]["overlap_branching"],
            "effective_branching": primary["derived_inputs"]["effective_branching"],
            "word_cutoff": primary["derived_inputs"]["word_cutoff"],
            "tail_distances": primary["derived_inputs"]["tail_distances"],
        },
        "non_claims": [
            "No common U_n, weak Gibbs-L2 convergence, R-512 minimal-form selection or anchored-n semigroup theorem.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_projective_correlation.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_projective_correlation_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_projective_correlation_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_projective_correlation_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "lean verification/lean/Tect/PahOmc020Projective.lean (Lean 4.32.1 with the registered package path)",
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
    with tempfile.TemporaryDirectory(prefix="pah020-projective-replay-") as directory:
        replay = build(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.read_bytes() != encoded:
        raise SystemExit("PAH-OMC-020 projective integrated replay mismatch")
    if not args.check:
        atomic_json(args.output, replay)
    print("PAH-OMC-020 PROJECTIVE INTEGRATED: PASS (auxiliary finite envelope; common U_n open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
