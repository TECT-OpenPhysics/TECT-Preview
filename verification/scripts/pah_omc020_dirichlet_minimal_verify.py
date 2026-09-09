#!/usr/bin/env python3
"""Integrate primary, independent, hostile and Lean Dirichlet checks."""

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
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "verification/scripts/pah_omc020_dirichlet_minimal.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_dirichlet_minimal_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_dirichlet_minimal_hostile.py"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-contract-v1.json"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Dirichlet.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-dirichlet-minimal/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-closure-prereg-v1.json":
        "4337e21a140206956ea52ee10e20d04358af868969e3edb9f055e5ea64b055b7",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md":
        "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
}

DECLARATIONS = [
    "sq_le_sq_of_abs_le",
    "normal_trunc_zero",
    "normal_trunc_one",
    "normal_trunc_lipschitz",
    "weighted_form_contraction",
    "weighted_form_contraction_canonical",
    "constant_one_weighted_energy_zero",
    "normal_trunc_l2_contraction",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
    if process.returncode:
        raise RuntimeError(f"{script.name} failed:\n{process.stdout}\n{process.stderr}")
    return json.loads(output.read_text(encoding="utf-8"))


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    values += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return values


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
    if process.returncode or re.search(r"(?im)\berror:", diagnostics):
        raise RuntimeError(f"Lean diagnostics:\n{diagnostics}")
    return subprocess.run(
        [str(lean_executable()), "--version"], capture_output=True, text=True,
        encoding="utf-8", check=True
    ).stdout.strip()


def build(output: Path, lean_cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-dirichlet-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lanes = {"primary": primary, "independent": independent, "hostile": hostile}
        lane_hashes = {name: sha(folder / f"{name}.json") for name in lanes}

    checks: list[dict] = []

    def check(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    hashes = {path: sha(ROOT / path) for path in PINS}
    for path, expected in PINS.items():
        check(f"source hash:{path}", hashes[path], expected, hashes[path] == expected)
    check("contract hash", sha(CONTRACT), primary["contract_sha256"], sha(CONTRACT) == primary["contract_sha256"])
    check("primary status", primary["status"], "PASS_SCOPED_DIRICHLET_MINIMAL", primary["status"] == "PASS_SCOPED_DIRICHLET_MINIMAL")
    check("independent status", independent["status"], "PASS_INDEPENDENT_DIRICHLET_SCOPE", independent["status"] == "PASS_INDEPENDENT_DIRICHLET_SCOPE")
    check("hostile status", hostile["status"], "PASS_HOSTILE_DIRICHLET_CONTROLS", hostile["status"] == "PASS_HOSTILE_DIRICHLET_CONTROLS")
    check("all lane verdicts", [lane["verdict"] for lane in lanes.values()], ["PASS"] * 3,
          all(lane["verdict"] == "PASS" for lane in lanes.values()))
    check("all lanes auxiliary", [lane["classification"] for lane in lanes.values()], ["auxiliary_support"] * 3,
          all(lane["classification"] == "auxiliary_support" for lane in lanes.values()))
    check("all lanes non-bearing", [lane["claim_bearing"] for lane in lanes.values()], [False] * 3,
          all(lane["claim_bearing"] is False for lane in lanes.values()))
    check("no gate change", primary["active_gate_change"], False, primary["active_gate_change"] is False)
    check("no physical promotion", primary["physical_promotion"], False, primary["physical_promotion"] is False)
    check("primary checks present", primary["checks_passed"], ">0", primary["checks_passed"] > 0)
    check("independent checks present", independent["checks_passed"], ">0", independent["checks_passed"] > 0)
    check("hostile checks present", hostile["checks_passed"], ">0", hostile["checks_passed"] > 0)
    truncated_energy = Fraction(primary["fixture"]["truncated_energy"])
    raw_energy = Fraction(primary["fixture"]["raw_energy"])
    check("normal energy does not exceed raw", str(truncated_energy), f"<= {raw_energy}",
          truncated_energy <= raw_energy)
    check("fixture energies recorded", sorted(primary["fixture"].keys()),
          ["grid_pair_count", "pairs", "raw_energy", "truncated_energy", "weights"],
          sorted(primary["fixture"].keys()) == ["grid_pair_count", "pairs", "raw_energy", "truncated_energy", "weights"])
    check("next question retains N2b", "N2b" in primary["next_single_question"], True,
          "N2b" in primary["next_single_question"])
    check("next question retains N2c/N4", "N2c/N4" in primary["next_single_question"], True,
          "N2c/N4" in primary["next_single_question"])
    check("next question retains N2d", "N2d" in primary["next_single_question"], True,
          "N2d" in primary["next_single_question"])
    check("primary and independent do not import each other",
          imports(INDEPENDENT), "no primary module",
          not any("pah_omc020_dirichlet_minimal" in item for item in imports(INDEPENDENT)))
    check("hostile does not import primary", imports(HOSTILE), "no primary module",
          not any("pah_omc020_dirichlet_minimal" in item for item in imports(HOSTILE)))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    relative_lean = str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/")
    entry = next((item for item in registry["entrypoints"] if item.get("path") == relative_lean), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    check("Lean registry hash", sha(LEAN_SOURCE), entry["sha256"], sha(LEAN_SOURCE) == entry["sha256"])
    check("Lean declarations", entry["declarations"], DECLARATIONS, entry["declarations"] == DECLARATIONS)
    version = compile_lean(lean_cache)
    check("Lean toolchain", version, "4.32.1", "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-dirichlet-minimal-integrated/1.0",
        "status": "PASS_INTEGRATED_DIRICHLET_MINIMAL",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(checks),
        "checks": checks,
        "lane_status": {name: lane["status"] for name, lane in lanes.items()},
        "lane_run_hashes": lane_hashes,
        "source_hashes": hashes,
        "contract_sha256": sha(CONTRACT),
        "lean": {"path": relative_lean, "sha256": sha(LEAN_SOURCE), "toolchain": version, "declarations": DECLARATIONS},
        "finding": "The exact R-512 minimal form is conditionally Dirichlet/Markov and conservative under the inherited R-511 form and domain premises; N2a-N2d and finite-to-anchored-n semigroup identification remain open.",
        "next_single_question": primary["next_single_question"],
        "non_claims": primary["non_claims"],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_dirichlet_minimal.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_dirichlet_minimal_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_dirichlet_minimal_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_dirichlet_minimal_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020Dirichlet.lean",
        },
    }
    atomic(output, payload)
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
            raise SystemExit("integrated Dirichlet replay mismatch")
    print(f"PAH-OMC-020 DIRICHLET INTEGRATED: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
