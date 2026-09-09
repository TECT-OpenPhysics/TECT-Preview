#!/usr/bin/env python3
"""Integrated successor replay for the current-byte PAH-OMC-020 N2b audit.

The v1.1 authority remains immutable.  This successor points the same
primary/independent/hostile checks at a fresh run directory so that additions
to the bounded strategy inventory are represented in the independent digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-09-pah-omc020-n2b-common-space-audit-v1.2"
)
OUTPUT = RUN_DIR / "integrated.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_n2b_common_space_audit_v11.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json": "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json": "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json": "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md": "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md": "2eeaa12411cba9525bfb6672fdae73d47a113349236639e0c3aa2e9ed8fbd9ab",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-inventory-stable/result.json": "e4ed74bed72b1b30a13ea059e51fab87af540ce85bc45515da6384b0e2a2ecf2",
    "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n-mosco-contract/n-mosco.json": "5864d7e10312a3a220d4fd7766f7bbd1d260287eb3441bc844e172a26026c96a",
    "verification/lean/Tect/PahOmc020.lean": "f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def lean_path(cache: Path | None) -> str:
    paths: list[str] = []
    for root in (cache, ROOT / "verification/lean/.lake/packages"):
        if root is None or not root.is_dir():
            continue
        for package in sorted(root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir() and str(candidate) not in paths:
                paths.append(str(candidate))
    return os.pathsep.join(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    parser.add_argument("--lean-cache", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    output_paths = {
        "primary": RUN_DIR / "result.json",
        "independent": RUN_DIR / "independent.json",
        "hostile": RUN_DIR / "hostile.json",
    }
    commands = {
        "primary": [sys.executable, "-X", "utf8", str(PRIMARY), "--output", str(output_paths["primary"]), "--check"],
        "independent": [sys.executable, "-X", "utf8", str(INDEPENDENT), "--output", str(output_paths["independent"]), "--check"],
        "hostile": [sys.executable, "-X", "utf8", str(HOSTILE), "--output", str(output_paths["hostile"]), "--check"],
    }
    replay: dict[str, dict[str, Any]] = {}
    for name, command in commands.items():
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        replay[name] = {"returncode": process.returncode, "command": " ".join(command), "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
        check(f"{name} replay", process.returncode, 0, process.returncode == 0)

    primary = load(output_paths["primary"])
    independent = load(output_paths["independent"])
    hostile = load(output_paths["hostile"])
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(f"{name} verdict", run.get("verdict"), "HOLD_FOR_EVIDENCE", run.get("verdict") == "HOLD_FOR_EVIDENCE")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(value is False for value in flags.values()))
    check("primary checks", primary.get("passed"), 22, primary.get("passed") == 22 and primary.get("failed") == 0)
    check("independent checks", independent.get("checks_passed"), 16, independent.get("checks_passed") == 16)
    check("independent current inventory", len(independent.get("inventory", [])), 203, len(independent.get("inventory", [])) == 203)
    check("independent strict candidates", independent.get("strict_owner_candidates"), [], independent.get("strict_owner_candidates") == [])
    check("hostile checks", hostile.get("checks_passed"), 12, hostile.get("checks_passed") == 12)
    actual_pins = {relative: sha(ROOT / relative) for relative in PINS}
    check("source pins", actual_pins, PINS, actual_pins == PINS)

    check("Lean LF", b"\r" not in LEAN.read_bytes(), True, b"\r" not in LEAN.read_bytes())
    lean_text = LEAN.read_text(encoding="utf-8")
    forbidden = {token: bool(re.search(rf"\b{re.escape(token)}\b", lean_text)) for token in ("sorry", "admit", "axiom", "unsafe")}
    check("Lean forbidden tokens", forbidden, {token: False for token in forbidden}, not any(forbidden.values()))
    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020.lean"), None)
    check("Lean registry entry", entry is not None, True, entry is not None)
    if entry is None:
        entry = {}
    declarations = {"inverse_pair_form", "finite_sum_square_bound", "finite_sum_abs_bound", "radial_form_coefficient", "split_boundary_gap", "split_fibre_ratio_strict_decay"}
    check("Lean registry hash", entry.get("sha256"), sha(LEAN), entry.get("sha256") == sha(LEAN))
    check("Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == declarations)
    environment = os.environ.copy()
    paths = lean_path(args.lean_cache)
    if paths:
        environment["LEAN_PATH"] = paths
    lean_process = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check("Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_returncode = lean_process.returncode if lean_process is not None else None
    lean_output = ((lean_process.stdout + lean_process.stderr).strip() if lean_process is not None else "")
    check("Lean compile", lean_returncode, 0, lean_returncode == 0)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-n2b-common-space-audit-integrated/1.2",
        "audit_id": "PAH-OMC-020-N2B-COMMON-SPACE-AUDIT-001-V1.2-INTEGRATED",
        "task_id": "T-064",
        "status": "PASS_INTEGRATED_N2B_CURRENT_BYTE_SUCCESSOR_HOLD",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(rows),
        "passed": len(rows),
        "failed": 0,
        "checks": rows,
        "replay": replay,
        "lean": {"command": [str(args.lean), str(LEAN)], "returncode": lean_returncode, "output": lean_output},
        "source_hashes": {
            **actual_pins,
            "verification/scripts/pah_omc020_n2b_common_space_audit_v11.py": sha(PRIMARY),
            "codes/foundations/pah_omc020_n2b_common_space_audit_v11_independent.py": sha(INDEPENDENT),
            "codes/foundations/pah_omc020_n2b_common_space_audit_v11_hostile.py": sha(HOSTILE),
            "verification/scripts/pah_omc020_n2b_common_space_audit_v12_verify.py": sha(Path(__file__)),
            "verification/lean/registry.json": sha(REGISTRY),
        },
        "run_files": {str(path.relative_to(ROOT)): sha(path) for path in output_paths.values()},
        "finding": "The v1.2 successor replays the unchanged PAH-OMC-020 N2b audit against the current 203-path inventory. Primary, non-importing independent, hostile and Lean checks pass, while the source-authorized common-space packet remains absent and the verdict stays HOLD_FOR_EVIDENCE.",
        "next_single_question": "Can one source-authorized owner provide the complete common-space, arbitrary-sequence liminf, recovery, N2c/N4 boundary escape and R-512 minimal-identification packet without changing PAH-001?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit_v12_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence, Mosco theorem or universal impossibility theorem.",
            "No PAH functional, rate, state, carrier, regulator, normalization, time or limit-order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
    }
    encoded = atomic_json(destination, payload) if not args.check else (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and (not destination.is_file() or destination.read_bytes() != encoded):
        raise SystemExit("PAH-OMC-020 N2b integrated v1.2 replay mismatch")
    print(f"PAH-OMC-020 N2B INTEGRATED V1.2: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
