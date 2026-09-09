#!/usr/bin/env python3
"""Integrate the PAH-OMC-020 coordinate-boundary obstruction lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_boundary_kernel_obstruction.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_boundary_kernel_obstruction_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_boundary_kernel_obstruction_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-boundary-kernel-obstruction/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md":
        "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
}

LEAN_DECLARATIONS = [
    "inverse_pair_form",
    "finite_sum_square_bound",
    "finite_sum_abs_bound",
    "radial_form_coefficient",
    "split_boundary_gap",
    "split_fibre_ratio_strict_decay",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_lane(script: Path, output: Path) -> dict:
    command = [sys.executable, "-X", "utf8", str(script), "--output", str(output)]
    # The historical primary checker uses --check as a replay-only mode and
    # therefore needs one stored output before its first invocation.  The two
    # independent lanes write-and-replay in one call, so they remain checked
    # on first use.
    if output.exists() or script != PRIMARY:
        command.append("--check")
    process = subprocess.run(
        command,
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
    output.parent.mkdir(parents=True, exist_ok=True)
    primary_path = output.parent / "primary.json"
    independent_path = output.parent / "independent.json"
    hostile_path = output.parent / "hostile.json"
    primary = run_lane(PRIMARY, primary_path)
    independent = run_lane(INDEPENDENT, independent_path)
    hostile = run_lane(HOSTILE, hostile_path)
    lane_paths = {"primary": primary_path, "independent": independent_path, "hostile": hostile_path}
    lane_hashes = {name: digest(path) for name, path in lane_paths.items()}

    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    source_hashes = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        ck(f"source hash:{relative}", actual, expected, actual == expected)

    ck("primary status", primary["status"], "PASS_COORDINATE_BOUNDARY_OBSTRUCTION",
       primary["status"] == "PASS_COORDINATE_BOUNDARY_OBSTRUCTION")
    ck("independent status", independent["status"], "PASS_INDEPENDENT_COORDINATE_BOUNDARY_OBSTRUCTION",
       independent["status"] == "PASS_INDEPENDENT_COORDINATE_BOUNDARY_OBSTRUCTION")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_COORDINATE_BOUNDARY_CONTROLS",
       hostile["status"] == "PASS_HOSTILE_COORDINATE_BOUNDARY_CONTROLS")
    lanes = (primary, independent, hostile)
    classifications = [lane.get("classification", "auxiliary_support") for lane in lanes]
    claim_bearing = [lane.get("claim_bearing", False) for lane in lanes]
    ck("all lanes auxiliary", classifications,
       ["auxiliary_support"] * 3,
       all(value == "auxiliary_support" for value in classifications))
    ck("all lanes non-bearing", claim_bearing,
       [False] * 3, all(value is False for value in claim_bearing))
    ck("no active gate change", primary.get("active_gate_change", False), False,
       primary.get("active_gate_change", False) is False)
    ck("no physical promotion", primary.get("physical_promotion", False), False,
       primary.get("physical_promotion", False) is False)
    ck("exact ratio formula", primary["arithmetic"]["ratio_formula"],
       "(1+exp(-4))*exp(-A^2/2)",
       primary["arithmetic"]["ratio_formula"] == "(1+exp(-4))*exp(-A^2/2)")
    ck("inverse witnesses are unbounded", len(primary["arithmetic"]["inverse_ratio_witnesses"]), 3,
       len(primary["arithmetic"]["inverse_ratio_witnesses"]) == 3)
    ck("independent formula agrees", independent["arithmetic"]["ratio_formula"],
       primary["arithmetic"]["ratio_formula"],
       independent["arithmetic"]["ratio_formula"] == primary["arithmetic"]["ratio_formula"])
    ck("hostile controls are nonempty", len(hostile["controls"]["mutations_rejected"]), 5,
       len(hostile["controls"]["mutations_rejected"]) == 5)

    for script, marker in ((INDEPENDENT, "pah_omc020_boundary_kernel_obstruction"),
                           (HOSTILE, "pah_omc020_boundary_kernel_obstruction")):
        tree = ast.parse(script.read_text(encoding="utf-8"))
        imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        ck(f"{script.name} does not import primary", any(marker in item for item in imports), False,
           not any(marker in item for item in imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item["path"] == "verification/lean/Tect/PahOmc020.lean"), None)
    ck("Lean registry entry exists", entry is not None, True, entry is not None)
    ck("Lean registry hash", entry["sha256"], digest(LEAN_SOURCE), entry["sha256"] == digest(LEAN_SOURCE))
    ck("Lean declaration registry", entry["declarations"], LEAN_DECLARATIONS,
       entry["declarations"] == LEAN_DECLARATIONS)
    lean_text = LEAN_SOURCE.read_text(encoding="utf-8")
    ck("Lean has no placeholders", any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), False,
       not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    version, diagnostics = compile_lean(lean_cache)
    ck("Lean diagnostics", "error:" in diagnostics.lower(), False, "error:" not in diagnostics.lower())
    ck("Lean version", "4.32.1" in version, True, "4.32.1" in version)

    return {
        "schema": "tect/pah-omc020-boundary-kernel-obstruction-integrated/1.0",
        "status": "PASS_INTEGRATED_COORDINATE_BOUNDARY_OBSTRUCTION",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(checks),
        "checks": checks,
        "lane_status": {"primary": primary["status"], "independent": independent["status"], "hostile": hostile["status"]},
        "lane_counts": {"primary": primary.get("checks_passed", len(primary["checks"])),
                        "independent": independent["checks_passed"], "hostile": hostile["checks_passed"]},
        "lane_run_hashes": lane_hashes,
        "source_hashes": source_hashes,
        "lean": {"path": "verification/lean/Tect/PahOmc020.lean", "sha256": digest(LEAN_SOURCE),
                 "toolchain": version, "declarations": LEAN_DECLARATIONS, "diagnostics": diagnostics},
        "finding": "The exact source terminal square-to-split coordinate-preserving density-ratio lift has split/square ratio (1+exp(-4))*exp(-A^2/2), so its inverse is unbounded along an allowed amplitude ray. This is a route-local N2a obstruction only.",
        "scope": "Original PAH-001 and PAH-OMC-020 source definitions; fixed old labels h0=h1=vx=vy=+1; coordinate-preserving terminal fibre; no new dynamics or limit.",
        "remaining_contract": "A source-authorized non-coordinate bounded-energy realization, or an exact comparison-map counterexample at the parent scope, is still required for N2a/N2b/N2c/N4/N2d.",
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_boundary_kernel_obstruction.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_boundary_kernel_obstruction_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_boundary_kernel_obstruction_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_boundary_kernel_obstruction_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020.lean",
        },
        "non_claims": [
            "No full PAH-OMC-020 semigroup negative result, no Mosco liminf failure and no universal U_n impossibility.",
            "No change to the PAH-001 functional, rates, state, carrier, regulator order or external Markov time.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang-Mills or TOE conclusion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--lean-cache", type=Path, default=ROOT / "verification/lean/.lake/packages")
    args = parser.parse_args()
    payload = build(args.output, args.lean_cache)
    atomic_json(args.output, payload)
    if args.check:
        replay = build(args.output, args.lean_cache)
        if replay != payload:
            raise SystemExit("PAH-OMC-020 boundary integrated replay mismatch")
    print(f"PAH-OMC-020 BOUNDARY INTEGRATED: PASS {payload['checks_passed']} checks (route-local obstruction)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
