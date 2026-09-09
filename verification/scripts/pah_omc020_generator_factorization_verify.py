#!/usr/bin/env python3
"""Integrated verifier for PAH-OMC-020 R-549."""

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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-generator-factorization-contract-v1.json"
PRIMARY = ROOT / "verification/scripts/pah_omc020_generator_factorization.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc020_generator_factorization_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc020_generator_factorization_hostile.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020Generator.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-generator-factorization"
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
    forbidden = ("pah_omc020_generator_factorization", "verification.scripts", "codes.foundations")
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
    check(rows, "independent count", independent.get("checks_passed"), 12, independent.get("checks_passed") == 12)
    check(rows, "hostile count", hostile.get("checks_passed"), 13, hostile.get("checks_passed") == 13)
    check(rows, "independent non-importing", non_importing(INDEPENDENT), True, non_importing(INDEPENDENT))
    check(rows, "hostile non-importing", non_importing(HOSTILE), True, non_importing(HOSTILE))
    check(rows, "parent hashes agree", primary.get("source_hashes"), independent.get("source_hashes"), primary.get("source_hashes") == independent.get("source_hashes") == hostile.get("source_hashes"))

    contract = load(CONTRACT)
    check(rows, "contract identity", (contract.get("result_id"), contract.get("task_id")), ("R-549", "T-081"), contract.get("result_id") == "R-549" and contract.get("task_id") == "T-081")
    check(rows, "factorization identity declared", "exact_identity" in contract["factorization"], True, "exact_identity" in contract["factorization"])
    check(rows, "two defect fields required", len(contract["required_owner_packet"]) == 5 and "gradient defect" in " ".join(contract["required_owner_packet"]).lower() and "divergence defect" in " ".join(contract["required_owner_packet"]).lower(), True, len(contract["required_owner_packet"]) == 5 and "gradient defect" in " ".join(contract["required_owner_packet"]).lower() and "divergence defect" in " ".join(contract["required_owner_packet"]).lower())
    nonclaims = json.dumps(contract["non_claims"], ensure_ascii=True).lower()
    check(rows, "scope firewall", all(word in nonclaims for word in ("source-authorized", "semigroup convergence", "no change")), True, all(word in nonclaims for word in ("source-authorized", "semigroup convergence", "no change")))
    check(rows, "physical firewall", all(word in nonclaims for word in ("pre-a", "spacetime", "qft", "gravity", "continuum")), True, all(word in nonclaims for word in ("pre-a", "spacetime", "qft", "gravity", "continuum")))

    registry = load(REGISTRY)
    entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/PahOmc020Generator.lean"), None)
    check(rows, "Lean registry entry", entry is not None, True, entry is not None)
    entry = entry or {}
    declarations = ["factorization_identity", "factorization_fixture", "divergence_fixture_is_nonzero", "gradient_fixture_is_nonzero", "omitted_term_can_change_residual", "missing_owner_field_blocks", "owner_packet_requires_all_fields"]
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
        "strategy/pa-hyp/PAH-OMC-020-generator-factorization-contract-v1.json": sha(CONTRACT),
        "verification/scripts/pah_omc020_generator_factorization.py": sha(PRIMARY),
        "codes/foundations/pah_omc020_generator_factorization_independent.py": sha(INDEPENDENT),
        "codes/foundations/pah_omc020_generator_factorization_hostile.py": sha(HOSTILE),
        "verification/scripts/pah_omc020_generator_factorization_verify.py": sha(Path(__file__)),
        "verification/lean/Tect/PahOmc020Generator.lean": sha(LEAN),
        "verification/lean/registry.json": sha(REGISTRY)
    }
    payload = {
        "schema": "tect/pah-omc020-generator-factorization-integrated/1.0",
        "audit_id": "PAH-OMC-020-GENERATOR-FACTORIZATION-INTEGRATED-001",
        "result_id": "R-549",
        "task_id": "T-081",
        "status": "PASS_CONDITIONAL_FACTORISATION",
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
        "finding": "Primary, independent and hostile lanes agree on the exact finite weighted-incidence factorization. The checkpoint isolates two necessary source-owner fields—gradient and adjoint-divergence defect estimates—and leaves them open, so it is HOLD_FOR_EVIDENCE for PAH-OMC-020.",
        "next_single_question": contract["single_next_question"],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_generator_factorization_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        "non_claims": contract["non_claims"]
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("R-549 integrated replay mismatch")
    else:
        atomic(destination, payload)
    print(f"PAH-OMC-020 GENERATOR FACTORIZATION INTEGRATED: PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
