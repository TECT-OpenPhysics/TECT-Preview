"""Integrate the PAH-OMC-020 N2c owner-audit lanes and Lean check."""

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
PRIMARY = ROOT / "verification/scripts/pah_omc020_n2c_owner_audit.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_n2c_owner_audit_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_n2c_owner_audit_hostile.py"
LEAN_SOURCE = ROOT / "verification/lean/Tect/PahOmc020N2c.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-n2c-owner-audit/integrated.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json":
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json":
        "87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379",
    "strategy/pa-hyp/PAH-OMC-020-c2-moment-certificate.md":
        "61284627c3a74df7d30e346365df983bba2781138639877196f4fbf90229887c",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json":
        "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json":
        "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
}

DECLARATIONS = [
    "n4_squared_budget",
    "n4_zero_when_pathwise_budget_zero",
    "static_c2_is_only_a_coefficient",
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


def build(lean_cache: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="pah020-n2c-integrated-") as directory:
        folder = Path(directory)
        primary = run_lane(PRIMARY, folder / "primary.json")
        independent = run_lane(INDEPENDENT, folder / "independent.json")
        hostile = run_lane(HOSTILE, folder / "hostile.json")
        lane_files = {
            "primary": folder / "primary.json",
            "independent": folder / "independent.json",
            "hostile": folder / "hostile.json",
        }
        lane_hashes = {name: digest(path) for name, path in lane_files.items()}

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

    lanes = (primary, independent, hostile)
    ck("primary hold status", primary["status"], "HOLD_FOR_EVIDENCE_N2C_OWNER_PACKET",
       primary["status"] == "HOLD_FOR_EVIDENCE_N2C_OWNER_PACKET")
    ck("independent hold status", independent["status"], "PASS_INDEPENDENT_N2C_OWNER_HOLD",
       independent["status"] == "PASS_INDEPENDENT_N2C_OWNER_HOLD")
    ck("hostile status", hostile["status"], "PASS_HOSTILE_N2C_FAIL_CLOSED",
       hostile["status"] == "PASS_HOSTILE_N2C_FAIL_CLOSED")
    ck("all lanes are auxiliary", [lane["classification"] for lane in lanes],
       ["auxiliary_support"] * len(lanes), all(lane["classification"] == "auxiliary_support" for lane in lanes))
    ck("all lanes claim-nonbearing", [lane["claim_bearing"] for lane in lanes],
       [False] * len(lanes), all(lane["claim_bearing"] is False for lane in lanes))
    ck("no active gate change", primary["active_gate_change"], False, primary["active_gate_change"] is False)
    ck("no physical promotion", primary["physical_promotion"], False, primary["physical_promotion"] is False)
    ck("primary checks executed", primary["checks_passed"] > 0, True, primary["checks_passed"] > 0)
    ck("independent checks executed", independent["checks_passed"] > 0, True, independent["checks_passed"] > 0)
    ck("hostile checks executed", hostile["checks_passed"] > 0, True, hostile["checks_passed"] > 0)
    ck("strict owner candidate set empty", primary["owner_packet_contract"]["candidate_paths_with_strict_admission"], [],
       primary["owner_packet_contract"]["candidate_paths_with_strict_admission"] == [])
    ck("N4 missing contract is explicit", any("N2c/N4" in item for item in primary["missing_assumptions"]), True,
       any("N2c/N4" in item for item in primary["missing_assumptions"]))
    ck("non-explosion missing contract is explicit", any("non-explosion" in item for item in primary["missing_assumptions"]), True,
       any("non-explosion" in item for item in primary["missing_assumptions"]))

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    independent_imports = [node.module or "" for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom)]
    independent_imports += [alias.name for node in ast.walk(independent_tree)
                            if isinstance(node, ast.Import) for alias in node.names]
    hostile_tree = ast.parse(HOSTILE.read_text(encoding="utf-8"))
    hostile_imports = [node.module or "" for node in ast.walk(hostile_tree) if isinstance(node, ast.ImportFrom)]
    hostile_imports += [alias.name for node in ast.walk(hostile_tree)
                        if isinstance(node, ast.Import) for alias in node.names]
    ck("independent does not import primary", any("pah_omc020_n2c_owner_audit" in item for item in independent_imports), False,
       not any("pah_omc020_n2c_owner_audit" in item for item in independent_imports))
    ck("hostile does not import primary", any("pah_omc020_n2c_owner_audit" in item for item in hostile_imports), False,
       not any("pah_omc020_n2c_owner_audit" in item for item in hostile_imports))

    shared = sorted(set(primary["source_hashes"]) & set(independent["source_hashes"]))
    ck("primary-independent hashes", all(primary["source_hashes"][key] == independent["source_hashes"][key] for key in shared), True,
       all(primary["source_hashes"][key] == independent["source_hashes"][key] for key in shared))
    shared_hostile = sorted(set(primary["source_hashes"]) & set(hostile["source_hashes"]))
    ck("primary-hostile hashes", all(primary["source_hashes"][key] == hostile["source_hashes"][key] for key in shared_hostile), True,
       all(primary["source_hashes"][key] == hostile["source_hashes"][key] for key in shared_hostile))

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"]
                  if item["path"] == "verification/lean/Tect/PahOmc020N2c.lean"), None)
    ck("Lean registry entry exists", entry is not None, True, entry is not None)
    ck("Lean registry hash", entry["sha256"], digest(LEAN_SOURCE), entry["sha256"] == digest(LEAN_SOURCE))
    ck("Lean declarations", entry["declarations"], DECLARATIONS, entry["declarations"] == DECLARATIONS)
    lean_source = LEAN_SOURCE.read_text(encoding="utf-8")
    ck("Lean has no forbidden tokens", not any(token in lean_source for token in ("sorry", "admit", "axiom", "unsafe")), True,
       not any(token in lean_source for token in ("sorry", "admit", "axiom", "unsafe")))
    version, diagnostics = compile_lean(lean_cache)
    ck("Lean diagnostics", "error:" in diagnostics.lower(), False, "error:" not in diagnostics.lower())
    ck("Lean toolchain", "4.32.1" in version, True, "4.32.1" in version)

    return {
        "schema": "tect/pah-omc020-n2c-owner-audit-integrated/1.0",
        "status": "PASS_INTEGRATED_N2C_OWNER_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "checks_passed": len(checks),
        "lane_counts": {"primary": primary["checks_passed"], "independent": independent["checks_passed"],
                        "hostile": hostile["checks_passed"]},
        "lane_run_hashes": lane_hashes,
        "source_hashes": source_hashes,
        "lean": {
            "path": "verification/lean/Tect/PahOmc020N2c.lean",
            "sha256": digest(LEAN_SOURCE),
            "toolchain": version,
            "declarations": DECLARATIONS,
            "diagnostics": diagnostics,
        },
        "finding": (
            "Primary, independent and hostile lanes agree that the repository-scoped "
            "source-authorized path-space/Lyapunov owner packet is absent.  Lean proves "
            "only the conditional C2-times-pathwise-budget algebraic bridge; it does not "
            "supply the missing path law, non-explosion or N2c/N4 estimate."
        ),
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_n2c_owner_audit.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_n2c_owner_audit_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_n2c_owner_audit_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020N2c.lean",
        },
        "missing_assumptions": primary["missing_assumptions"],
        "non_claims": primary["non_claims"],
        "next_single_question": primary["next_single_question"],
        "revisit_condition": primary["revisit_condition"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--lean-cache", type=Path, default=ROOT / "verification/lean/.lake/packages")
    args = parser.parse_args()
    payload = build(args.lean_cache)
    atomic_json(args.output, payload)
    if args.check:
        with tempfile.TemporaryDirectory(prefix="pah020-n2c-replay-") as directory:
            replay = build(args.lean_cache)
        if replay != payload:
            raise SystemExit("PAH-OMC-020 N2c integrated replay mismatch")
    print(f"PAH-OMC-020 N2C INTEGRATED: PASS {payload['checks_passed']} checks (HOLD_FOR_EVIDENCE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
