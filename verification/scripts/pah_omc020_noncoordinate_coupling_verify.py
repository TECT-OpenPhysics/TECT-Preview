#!/usr/bin/env python3
"""Integrate the non-coordinate PAH-OMC-020 coupling candidate lanes."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_noncoordinate_coupling_candidate.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_noncoordinate_coupling_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_noncoordinate_coupling_hostile.py"
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Coupling.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-noncoordinate-coupling/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md": "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json": "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json": "034f5fc35a88a4431ee1594c8a25e0d7bcf6c75b055ec2b21bbf30daf636dc7f",
    "strategy/pa-hyp/PAH-OMC-020-boundary-kernel-obstruction-result-v1.json": "3497fb5b0e6ea99add8fd4b0f6cbef124eaadf1d33ec7cadc9b5c798a316748b",
}

LEAN_DECLARATIONS = [
    "overlap_mass",
    "mismatch_mass",
    "coupling_rows",
    "coupling_columns",
    "conditional_expectation_contraction",
    "local_recovery_bound",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    exact = [item for item in candidates if "v4.32.1" in str(item)]
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
    return subprocess.run(
        [str(lean_executable()), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--lean-cache", type=Path, default=Path(
        r"E:\Dev\TECT\verification\lean\.lake\packages"
    ))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="pah020-coupling-integrated-") as directory:
        folder = Path(directory)
        primary = run_script(PRIMARY, folder / "primary.json")
        independent = run_script(INDEPENDENT, folder / "independent.json")
        hostile = run_script(HOSTILE, folder / "hostile.json")
    lanes = {"primary": primary, "independent": independent, "hostile": hostile}
    rows: list[dict] = []

    def check(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(f"source hash {relative}", actual, expected, actual == expected)
    candidate_hash = digest(CANDIDATE)
    check("candidate hash agrees across lanes", primary["candidate_sha256"], candidate_hash,
          primary["candidate_sha256"] == candidate_hash)
    check("independent candidate hash agrees", independent["candidate_sha256"], candidate_hash,
          independent["candidate_sha256"] == candidate_hash)
    check("hostile candidate hash agrees", hostile["candidate_sha256"], candidate_hash,
          hostile["candidate_sha256"] == candidate_hash)

    check("primary status", primary["status"], "PASS_SCOPED_NONCOORDINATE_LOCAL_COUPLING",
          primary["status"] == "PASS_SCOPED_NONCOORDINATE_LOCAL_COUPLING")
    check("independent status", independent["status"], "PASS_INDEPENDENT_NONCOORDINATE_LOCAL_COUPLING",
          independent["status"] == "PASS_INDEPENDENT_NONCOORDINATE_LOCAL_COUPLING")
    check("hostile status", hostile["status"], "PASS_HOSTILE_NONCOORDINATE_COUPLING_CONTROLS",
          hostile["status"] == "PASS_HOSTILE_NONCOORDINATE_COUPLING_CONTROLS")
    check("all lanes hold", [lane["verdict"] for lane in lanes.values()], ["HOLD_FOR_EVIDENCE"] * 3,
          all(lane["verdict"] == "HOLD_FOR_EVIDENCE" for lane in lanes.values()))
    check("all lanes auxiliary", [lane["classification"] for lane in lanes.values()], ["auxiliary_support"] * 3,
          all(lane["classification"] == "auxiliary_support" for lane in lanes.values()))
    check("all lanes conditional", [lane["conditional"] for lane in lanes.values()], [True] * 3,
          all(lane["conditional"] for lane in lanes.values()))
    check("all lanes non-bearing", [lane["claim_bearing"] for lane in lanes.values()], [False] * 3,
          all(not lane["claim_bearing"] for lane in lanes.values()))
    check("no physical promotion", [lane["physical_promotion"] for lane in lanes.values()], [False] * 3,
          all(not lane["physical_promotion"] for lane in lanes.values()))
    check("primary check count", len(primary["checks"]), 42, len(primary["checks"]) == 42)
    check("independent check count", len(independent["checks"]), 25, len(independent["checks"]) == 25)
    check("hostile check count", len(hostile["checks"]), 16, len(hostile["checks"]) == 16)

    p = primary["fixture"]
    check("exact overlap", p["mismatch"], "1/10", p["mismatch"] == "1/10")
    check("diagonal index grows", p["diagonal_indices_n8_to_n40"][-1] > p["diagonal_indices_n8_to_n40"][0], True,
          p["diagonal_indices_n8_to_n40"][-1] > p["diagonal_indices_n8_to_n40"][0])
    check("hard obligations remain open", len(primary["open_obligations"]), 6,
          len(primary["open_obligations"]) == 6)
    check("R-512 minimal target remains separate", "minimal" in " ".join(primary["open_obligations"]).lower(), True,
          "minimal" in " ".join(primary["open_obligations"]).lower())

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    imported += [alias.name for node in ast.walk(independent_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("independent does not import primary", not any("noncoordinate_coupling_candidate" in item for item in imported), True,
          not any("noncoordinate_coupling_candidate" in item for item in imported))
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree) if isinstance(node, ast.Import) for alias in node.names]
    check("hostile does not import primary", not any("noncoordinate_coupling_candidate" in item for item in hostile_imports), True,
          not any("noncoordinate_coupling_candidate" in item for item in hostile_imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/PahOmc020Coupling.lean"), None)
    check("Lean registry entry exists", entry is not None, True, entry is not None)
    if entry is not None:
        check("Lean registry hash", entry["sha256"], digest(LEAN_SOURCE), entry["sha256"] == digest(LEAN_SOURCE))
        check("Lean declarations registered", entry["declarations"], LEAN_DECLARATIONS, entry["declarations"] == LEAN_DECLARATIONS)
    version = compile_lean(args.lean_cache)
    check("Lean compilation", "4.32.1" in version, True, "4.32.1" in version)

    payload = {
        "schema": "tect/pah-omc020-noncoordinate-coupling-integrated/1.0",
        "status": "PASS_INTEGRATED_NONCOORDINATE_LOCAL_COUPLING",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "candidate_sha256": candidate_hash,
        "lean_version": version,
        "checks": rows,
        "lane_counts": {
            "primary": len(primary["checks"]),
            "independent": len(independent["checks"]),
            "hostile": len(hostile["checks"]),
        },
        "finding": "All lanes confirm a non-coordinate local coupling contraction and recovery candidate, while source authorization, energy intertwining, N2b, N2c/N4, N2d and the PAH-OMC-020 temporal theorem remain open.",
        "non_claims": primary["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("integrated coupling replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(f"PAH-OMC-020 NONCOORDINATE INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
