#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-020 radial semigroup checkpoint."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_radial_semigroup_consistency.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_radial_semigroup_consistency_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_radial_semigroup_consistency_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020RadialSemigroup.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-radial-semigroup-consistency"
OUTPUT = RUN_DIR / "integrated.json"
DEFAULT_LEAN = Path(r"C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lean.exe")
DEFAULT_CACHE = Path(r"E:\Dev\TECT\verification\lean\.lake\packages")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return encoded


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, ok: bool) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")


def non_importing(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    forbidden = ("pah_omc020_radial_semigroup_consistency", "verification.scripts", "codes.foundations")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        if any(any(token in name for token in forbidden) for name in names):
            return False
    return True


def lean_path(cache: Path | None) -> str:
    roots = [cache, ROOT / "verification/lean/.lake/packages"]
    values: list[str] = []
    for root in roots:
        if root is None or not root.is_dir():
            continue
        for package in sorted(root.iterdir()):
            candidate = package / ".lake" / "build" / "lib" / "lean"
            if candidate.is_dir() and str(candidate) not in values:
                values.append(str(candidate))
    return os.pathsep.join(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--lean", type=Path, default=DEFAULT_LEAN)
    parser.add_argument("--lean-cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    subprocesses: dict[str, dict[str, Any]] = {}
    for name, script in (("primary", PRIMARY), ("independent", INDEPENDENT), ("hostile", HOSTILE)):
        run = subprocess.run([sys.executable, "-X", "utf8", str(script), "--check"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocesses[name] = {"returncode": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr.strip()}
        check(rows, f"{name} replay", run.returncode, 0, run.returncode == 0)

    primary = load(RUN_DIR / "primary.json")
    independent = load(RUN_DIR / "independent.json")
    hostile = load(RUN_DIR / "hostile.json")
    for name, run in (("primary", primary), ("independent", independent), ("hostile", hostile)):
        check(rows, f"{name} verdict", run.get("verdict"), "PASS", run.get("verdict") == "PASS")
        flags = {key: run.get(key) for key in ("claim_bearing", "active_gate_change", "physical_promotion")}
        check(rows, f"{name} firewalls", flags, {"claim_bearing": False, "active_gate_change": False, "physical_promotion": False}, all(value is False for value in flags.values()))
        check(rows, f"{name} nonzero checks", run.get("checks_passed", 0) > 0, True, run.get("checks_passed", 0) > 0)
    check(rows, "primary count", primary.get("checks_passed"), 21, primary.get("checks_passed") == 21)
    check(rows, "independent count", independent.get("checks_passed"), 14, independent.get("checks_passed") == 14)
    check(rows, "hostile count", hostile.get("checks_passed"), 11, hostile.get("checks_passed") == 11)
    check(rows, "independent non-importing", non_importing(INDEPENDENT), True, non_importing(INDEPENDENT))
    check(rows, "hostile non-importing", non_importing(HOSTILE), True, non_importing(HOSTILE))
    check(rows, "parent hashes agree", primary.get("source_hashes"), independent.get("source_hashes"), primary.get("source_hashes") == independent.get("source_hashes") == hostile.get("source_hashes"))

    contract = load(CONTRACT)
    check(rows, "contract identity", (contract.get("result_id"), contract.get("task_id")), ("R-548", "T-065"), contract.get("result_id") == "R-548" and contract.get("task_id") == "T-065")
    check(rows, "restricted status", contract.get("acceptance", {}).get("PASS_RESTRICTED", "").startswith("The finite radial residual"), True, contract.get("acceptance", {}).get("PASS_RESTRICTED", "").startswith("The finite radial residual"))
    check(rows, "target identity status", contract["target_semigroup"]["radial_identity"]["status"], "SPECTRAL_CONSEQUENCE_OF_R512_ZERO_ENERGY", contract["target_semigroup"]["radial_identity"]["status"] == "SPECTRAL_CONSEQUENCE_OF_R512_ZERO_ENERGY")
    nonclaims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "scope firewall", all(word in nonclaims for word in ("non-radial", "anchored-n", "source-authorized")), True, all(word in nonclaims for word in ("non-radial", "anchored-n", "source-authorized")))
    check(rows, "physical firewall", all(word in nonclaims for word in ("pre-a", "qft", "gravity", "continuum")), True, all(word in nonclaims for word in ("pre-a", "qft", "gravity", "continuum")))

    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020RadialSemigroup.lean"), None)
    check(rows, "Lean registry entry", entry is not None, True, entry is not None)
    entry = entry or {}
    declarations = ["radial_jump_bound", "residual_bound", "compact_time_bound", "correlation_bound", "refinement_strict_decay", "primary_fixture", "independent_fixture"]
    check(rows, "Lean registry hash", entry.get("sha256"), sha(LEAN), entry.get("sha256") == sha(LEAN))
    check(rows, "Lean declarations", sorted(entry.get("declarations", [])), sorted(declarations), set(entry.get("declarations", [])) == set(declarations))
    lean_text = LEAN.read_text(encoding="utf-8")
    check(rows, "Lean source policy", b"\r" not in LEAN.read_bytes() and not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")), True, b"\r" not in LEAN.read_bytes() and not any(token in lean_text for token in ("sorry", "admit", "axiom", "unsafe")))
    env = os.environ.copy()
    paths = lean_path(args.lean_cache)
    if paths:
        env["LEAN_PATH"] = paths
    lean_run = subprocess.run([str(args.lean), str(LEAN)], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace") if args.lean.is_file() else None
    check(rows, "Lean compiler available", args.lean.is_file(), True, args.lean.is_file())
    lean_rc = lean_run.returncode if lean_run is not None else None
    lean_output = ((lean_run.stdout + lean_run.stderr).strip() if lean_run is not None else "")
    check(rows, "Lean compile", lean_rc, 0, lean_rc == 0)

    source_hashes = {
        **primary.get("source_hashes", {}),
        "strategy/pa-hyp/PAH-OMC-020-radial-semigroup-consistency-contract-v1.json": sha(CONTRACT),
        "verification/scripts/pah_omc020_radial_semigroup_consistency.py": sha(PRIMARY),
        "codes/foundations/pah_omc020_radial_semigroup_consistency_independent.py": sha(INDEPENDENT),
        "codes/foundations/pah_omc020_radial_semigroup_consistency_hostile.py": sha(HOSTILE),
        "verification/scripts/pah_omc020_radial_semigroup_consistency_verify.py": sha(Path(__file__)),
        "verification/lean/Tect/PahOmc020RadialSemigroup.lean": sha(LEAN),
        "verification/lean/registry.json": sha(REGISTRY),
    }
    payload = {
        "schema": "tect/pah-omc020-radial-semigroup-consistency-integrated/1.0",
        "audit_id": "PAH-OMC-020-RADIAL-SEMIGROUP-CONSISTENCY-INTEGRATED-001",
        "result_id": "R-548",
        "task_id": "T-065",
        "status": "PASS_RESTRICTED_RADIAL_SUBSPACE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(rows),
        "passed": len(rows),
        "failed": 0,
        "checks": rows,
        "subprocesses": subprocesses,
        "lean": {"command": [str(args.lean), str(LEAN)], "returncode": lean_rc, "output": lean_output},
        "source_hashes": source_hashes,
        "finding": "All lanes verify the restricted amplitude-only temporal consistency: the original finite semigroup differs from identity by at most 2 T H_f L_f h_j in L2, while the exact R-512 minimal target acts identically on its zero-energy radial subspace. This proves only the amplitude-only correlation sector; non-radial and source-owned anchored-n transfer remain open.",
        "next_single_question": contract["next_single_question"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_radial_semigroup_consistency_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": contract["non_claims"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial semigroup integrated replay mismatch")
    else:
        atomic(destination, payload)
    print(f"PAH-OMC-020 RADIAL SEMIGROUP INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=PASS_RESTRICTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
