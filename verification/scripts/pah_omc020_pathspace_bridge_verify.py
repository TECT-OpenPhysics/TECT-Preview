"""Integrate the PAH-OMC-020 U_n-free path-space bridge lanes.

The integrated check replays independent finite arithmetic and hostile
controls, verifies their pinned source inputs and the Lean registry entry,
and compiles the finite rational Lean declarations.  It deliberately does
not construct a path-space process or promote the conditional bridge to a
semigroup theorem.
"""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_pathspace_bridge.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_pathspace_bridge_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_pathspace_bridge_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020Pathspace.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-pathspace-bridge/integrated.json"
)

EXPECTED_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json":
        "8d005bea7ee33111712f58a32046cdb254f77bc8c17d8eb1a470abcc2adbbbc7",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json":
        "9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11",
    "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json":
        "67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d",
    "strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json":
        "2bfc217bfa7785726d7342ce5ec80d1adab5be030c561d4e6681d49f64cf3248",
}

LEAN_DECLARATIONS = [
    "bridge_triangle",
    "bridge_budget_nonnegative",
    "source_overlap_formula",
    "source_two_copy_formula",
    "source_first_root_width_two",
    "independent_first_root_width_three",
    "tail_ratio_fixture",
    "tail_ratio_primary_fixture",
    "state_fixture_pair_decreases",
    "independent_state_fixture_pair_decreases",
    "explicit_target_defect_fixture",
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


def compile_lean(cache: Path) -> tuple[str, str]:
    libraries: list[str] = []
    if cache.exists():
        for package in sorted(cache.iterdir()):
            library = package / ".lake" / "build" / "lib" / "lean"
            if library.is_dir():
                libraries.append(str(library))
    if not libraries:
        raise FileNotFoundError(f"No Lean package libraries found under {cache}")
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


def build(output: Path, cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-pathspace-integrated-") as directory:
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

    for relative, expected in EXPECTED_PINS.items():
        actual = digest(ROOT / relative)
        ck(f"source hash {relative}", actual, expected, actual == expected)

    ck(
        "primary status",
        primary["status"],
        "PASS_PATHSPACE_BRIDGE_CONTRACT",
        primary["status"] == "PASS_PATHSPACE_BRIDGE_CONTRACT",
    )
    ck(
        "independent status",
        independent["status"],
        "PASS_INDEPENDENT_PATHSPACE_BRIDGE_CONTRACT",
        independent["status"] == "PASS_INDEPENDENT_PATHSPACE_BRIDGE_CONTRACT",
    )
    ck(
        "hostile status",
        hostile["status"],
        "PASS_HOSTILE_PATHSPACE_BRIDGE_CONTROLS",
        hostile["status"] == "PASS_HOSTILE_PATHSPACE_BRIDGE_CONTROLS",
    )
    ck(
        "all lanes HOLD",
        [lane["verdict"] for lane in lanes.values()],
        ["HOLD_FOR_EVIDENCE"] * 3,
        all(lane["verdict"] == "HOLD_FOR_EVIDENCE" for lane in lanes.values()),
    )
    ck(
        "all lanes auxiliary",
        [lane["classification"] for lane in lanes.values()],
        ["auxiliary_support"] * 3,
        all(lane["classification"] == "auxiliary_support" for lane in lanes.values()),
    )
    ck(
        "all lanes conditional",
        [lane["conditional"] for lane in lanes.values()],
        [True] * 3,
        all(lane["conditional"] for lane in lanes.values()),
    )
    ck(
        "all lanes non-bearing",
        [lane["claim_bearing"] for lane in lanes.values()],
        [False] * 3,
        all(not lane["claim_bearing"] for lane in lanes.values()),
    )
    ck(
        "physical promotion blocked",
        [lane["physical_promotion"] for lane in lanes.values()],
        [False] * 3,
        all(not lane["physical_promotion"] for lane in lanes.values()),
    )
    ck("primary check count", len(primary["checks"]), 41, len(primary["checks"]) == 41)
    ck("independent check count", len(independent["checks"]), 33, len(independent["checks"]) == 33)
    ck("hostile check count", len(hostile["checks"]), 20, len(hostile["checks"]) == 20)

    shared = sorted(set(primary["source_hashes"]) & set(independent["source_hashes"]))
    agreement = all(primary["source_hashes"][key] == independent["source_hashes"][key] for key in shared)
    ck("primary-independent shared hashes", agreement, True, agreement)
    shared_hostile = sorted(set(primary["source_hashes"]) & set(hostile["source_hashes"]))
    hostile_agreement = all(primary["source_hashes"][key] == hostile["source_hashes"][key] for key in shared_hostile)
    ck("primary-hostile shared hashes", hostile_agreement, True, hostile_agreement)
    ck("primary effective branching", primary["derived_inputs"]["effective_branching"], 288,
       primary["derived_inputs"]["effective_branching"] == 288)
    ck("primary first-root bound", primary["derived_inputs"]["first_root_bound"], 112,
       primary["derived_inputs"]["first_root_bound"] == 112)
    ck("independent first-root bound", independent["fixture"]["first_root_bound"], 128,
       independent["fixture"]["first_root_bound"] == 128)
    ck("primary tail distances", primary["derived_inputs"]["tail_distances"], [128, 192, 256],
       primary["derived_inputs"]["tail_distances"] == [128, 192, 256])
    ck("target process defect remains explicit", len(primary["missing_assumptions"]), 4,
       len(primary["missing_assumptions"]) == 4)
    ck("common U is not synthesized", any("common U_n" in item for item in primary["non_claims"]), True,
       any("common U_n" in item for item in primary["non_claims"]))
    ck("minimal selection remains open", any("minimal" in item.lower() for item in primary["missing_assumptions"]), True,
       any("minimal" in item.lower() for item in primary["missing_assumptions"]))
    ck("physical firewall", all(any("physical Pre-A" in item for item in lane["non_claims"])
                                 for lane in lanes.values()), True,
       all(any("physical Pre-A" in item for item in lane["non_claims"]) for lane in lanes.values()))

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree)
                            if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary", not any("pah_omc020_pathspace_bridge" in item
                                                        for item in independent_imports), True,
       not any("pah_omc020_pathspace_bridge" in item for item in independent_imports))
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree)
                        if isinstance(node, ast.Import) for alias in node.names]
    ck("hostile does not import primary", not any("pah_omc020_pathspace_bridge" in item
                                                    for item in hostile_imports), True,
       not any("pah_omc020_pathspace_bridge" in item for item in hostile_imports))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next(item for item in registry["entrypoints"] if item["path"] ==
                 "verification/lean/Tect/PahOmc020Pathspace.lean")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    declarations = re.findall(r"(?m)^theorem\s+([A-Za-z0-9_]+)", source)
    source_digest = digest(LEAN_SOURCE)
    ck("Lean registry hash", entry["sha256"], source_digest, entry["sha256"] == source_digest)
    ck("Lean declaration list", declarations, LEAN_DECLARATIONS, declarations == LEAN_DECLARATIONS)
    forbidden = ("sorry", "admit", "axiom", "unsafe")
    policy_ok = not any(token in source for token in forbidden)
    ck("Lean forbidden-token policy", policy_ok, True, policy_ok)
    version, diagnostics = compile_lean(cache)
    ck("Lean 4.32.1 version", "version 4.32.1" in version, version, "version 4.32.1" in version)
    ck("Lean diagnostics contain no errors", "error:" not in diagnostics.lower(), True,
       "error:" not in diagnostics.lower())

    payload = {
        "schema": "tect/pah-omc020-pathspace-bridge-integrated/1.0",
        "status": "PASS_INTEGRATED_PATHSPACE_BRIDGE_CONTRACT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
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
                     "sha256": source_digest, "version": version, "diagnostics": diagnostics},
        },
        "run_hashes": run_hashes,
        "lane_counts": {name: len(lane["checks"]) for name, lane in lanes.items()},
        "scope": "Conditional finite scalar path-space bridge contract for the registered PAH-OMC-020 local cylinder target; process construction, uniqueness and R-512 minimal-form identification remain open.",
        "bridge_decomposition": [
            "projective local-state error from R-510",
            "finite local-generator stabilization from R-493",
            "explicit conditional boundary tail from R-517",
            "uninstantiated target-process and minimal-form defect",
        ],
        "missing_assumptions": primary["missing_assumptions"],
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence theorem or negative result.",
            "No common U_n or Hilbert isometry, N2b liminf, N2c/N4 unconditional escape or N2d selection.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_pathspace_bridge.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_pathspace_bridge_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "lean verification/lean/Tect/PahOmc020Pathspace.lean (Lean 4.32.1 with the registered package path)",
        },
        "next_single_question": primary["next_single_question"],
        "revisit_condition": primary["revisit_condition"],
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
    with tempfile.TemporaryDirectory(prefix="pah020-pathspace-replay-") as directory:
        replay = build(Path(directory) / "integrated.json", args.lean_cache)
    encoded = (json.dumps(replay, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 path-space integrated replay mismatch")
    else:
        atomic_json(args.output, replay)
    print("PAH-OMC-020 PATHSPACE INTEGRATED: PASS (conditional contract; process/minimal selection open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
