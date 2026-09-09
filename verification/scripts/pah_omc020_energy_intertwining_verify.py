#!/usr/bin/env python3
"""Integrate the PAH-OMC-020 energy-intertwining audit lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_energy_intertwining_contract.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_energy_intertwining_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_energy_intertwining_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Energy.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-energy-intertwining/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json":
        "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json":
        "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json":
        "86246c253273f5dc1fc630c37c70e7b7b2e3aefcf1fc3d81ae5ad2b0f56cdc35",
}

DECLARATIONS = [
    "weighted_conductance_transfer",
    "weighted_transfer_fixture",
    "static_l2_identity_contraction",
    "static_energy_witness_source",
    "static_energy_witness_target",
    "static_energy_witness_strict",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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
    return version


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    values += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return values


def build(output: Path, lean_cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-energy-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lanes = {"primary": primary, "independent": independent, "hostile": hostile}
        lane_hashes = {name: digest(folder / f"{name}.json") for name in lanes}

    checks: list[dict] = []

    def check(name: str, actual: object, expected: object, condition: bool) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    hashes = {relative: digest(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        check(f"source hash:{relative}", hashes[relative], expected, hashes[relative] == expected)
    check("contract hash is recorded", digest(CONTRACT), primary["contract_sha256"],
          digest(CONTRACT) == primary["contract_sha256"])
    check("primary status", primary["status"], "HOLD_FOR_EVIDENCE_ENERGY_INTERTWINING",
          primary["status"] == "HOLD_FOR_EVIDENCE_ENERGY_INTERTWINING")
    check("independent status", independent["status"], "PASS_INDEPENDENT_ENERGY_SCOPE",
          independent["status"] == "PASS_INDEPENDENT_ENERGY_SCOPE")
    check("hostile status", hostile["status"], "PASS_HOSTILE_ENERGY_SCOPE_CONTROLS",
          hostile["status"] == "PASS_HOSTILE_ENERGY_SCOPE_CONTROLS")
    check("all lanes held", [lane["verdict"] for lane in lanes.values()],
          ["HOLD_FOR_EVIDENCE"] * 3,
          all(lane["verdict"] == "HOLD_FOR_EVIDENCE" for lane in lanes.values()))
    check("all lanes auxiliary", [lane["classification"] for lane in lanes.values()],
          ["auxiliary_support"] * 3,
          all(lane["classification"] == "auxiliary_support" for lane in lanes.values()))
    check("all lanes claim-nonbearing", [lane["claim_bearing"] for lane in lanes.values()],
          [False] * 3,
          all(lane["claim_bearing"] is False for lane in lanes.values()))
    check("no gate change", primary["active_gate_change"], False, primary["active_gate_change"] is False)
    check("no physical promotion", primary["physical_promotion"], False, primary["physical_promotion"] is False)
    check("primary checks present", primary["checks_passed"], ">0", primary["checks_passed"] > 0)
    check("independent checks present", independent["checks_passed"], ">0", independent["checks_passed"] > 0)
    check("hostile checks present", hostile["checks_passed"], ">0", hostile["checks_passed"] > 0)
    check("abstract witness source energy", primary["abstract_witness"]["source_energy"], "1/2",
          primary["abstract_witness"]["source_energy"] == "1/2")
    check("abstract witness target energy", primary["abstract_witness"]["target_energy"], "1",
          primary["abstract_witness"]["target_energy"] == "1")
    check("abstract witness explicitly non-PAH", primary["abstract_witness"]["scope"], "Abstract",
          primary["abstract_witness"]["scope"].startswith("Abstract insufficiency"))
    check("next question is one owner datum", primary["next_single_question"], "root-wise",
          "root-wise" in primary["next_single_question"])

    independent_imports = imports(INDEPENDENT)
    hostile_imports = imports(HOSTILE)
    check("independent does not import primary", independent_imports, "no primary import",
          not any("pah_omc020_energy_intertwining_contract" in item for item in independent_imports))
    check("hostile does not import primary", hostile_imports, "no primary import",
          not any("pah_omc020_energy_intertwining_contract" in item for item in hostile_imports))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item["path"] == str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/")), None)
    check("Lean registry entry exists", entry is not None, True, entry is not None)
    check("Lean registry hash", digest(LEAN_SOURCE), entry["sha256"], digest(LEAN_SOURCE) == entry["sha256"])
    check("Lean declaration registry", entry["declarations"], DECLARATIONS, entry["declarations"] == DECLARATIONS)
    version = compile_lean(lean_cache)
    check("Lean toolchain", version, "4.32.1", "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-energy-intertwining-integrated/1.0",
        "status": "PASS_INTEGRATED_ENERGY_SCOPE",
        "verdict": "HOLD_FOR_EVIDENCE",
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
        "contract_sha256": digest(CONTRACT),
        "lean": {
            "path": str(LEAN_SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": digest(LEAN_SOURCE),
            "toolchain": version,
            "declarations": DECLARATIONS,
        },
        "finding": "The conditional weighted-edge implication is verified, while the exact PAH dynamic root-wise coupling/form defect remains absent; the static two-state witness is not a PAH negative result.",
        "next_single_question": primary["next_single_question"],
        "non_claims": primary["non_claims"],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_energy_intertwining_contract.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_energy_intertwining_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_energy_intertwining_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_energy_intertwining_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020Energy.lean",
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
    print(f"PAH-OMC-020 ENERGY INTEGRATED: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
