#!/usr/bin/env python3
"""Offline canonical-environment Lean replay for PAH-OMC-013.

The ordinary OMC-013 integrated verifier already checks the primary,
independent, and hostile finite algebraic lanes.  This wrapper isolates the
environmental part of its Lean cross-check: it verifies the pinned manifest
and R493 source, builds ``LEAN_PATH`` only from an explicitly selected existing
package cache, and compiles R493 without a lake update or network access.

This is an auxiliary reproducibility check.  It does not add a theorem,
change PAH-001, or promote finite intertwining to a semigroup, limit, or
physical conclusion.
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


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-manifest.json"
LEAN = REPO / "verification/lean/Tect/R493.lean"
REGISTRY = REPO / "verification/lean/registry.json"
TOOLCHAIN = REPO / "verification/lean/lean-toolchain"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc013-lean-canonical-env/result.json"
)

# This is a source pin, not a derived numerical constant.  It prevents a
# mutable manifest from silently changing which Lean source is replayed.
MANIFEST_SHA256 = "e3594b8100bd0a34d426e3e1a4dadfe8d7b0c21fccb5d5f5bc7b7d28aae591a1"
PINNED_LEAN_VERSION = "4.32.1"
FORBIDDEN = ("sorry", "admit", "axiom", "unsafe")


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path, *, normalise: bool = True) -> str:
    data = normalised_bytes(path) if normalise else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def pinned_lean_executable() -> Path | None:
    if not TOOLCHAIN.is_file():
        return None
    encoded = TOOLCHAIN.read_text(encoding="utf-8").strip().replace("/", "--").replace(":", "---")
    suffix = "lean.exe" if os.name == "nt" else "lean"
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / suffix
    return candidate if candidate.is_file() else None


def package_library_paths(package_root: Path) -> list[Path]:
    if not package_root.is_dir():
        return []
    paths: list[Path] = []
    for package in sorted(package_root.iterdir(), key=lambda item: item.name):
        candidate = package / ".lake" / "build" / "lib" / "lean"
        if candidate.is_dir():
            paths.append(candidate.resolve())
    return paths


def compile_r493(package_root: Path) -> dict[str, Any]:
    executable = pinned_lean_executable()
    libraries = package_library_paths(package_root)
    if executable is None:
        return {
            "status": "BLOCKED",
            "reason": "pinned Lean executable missing",
            "returncode": None,
            "executable": None,
            "lean_path_entries": len(libraries),
            "output": "",
        }
    if not libraries:
        return {
            "status": "BLOCKED",
            "reason": "selected package cache has no compiled Lean libraries",
            "returncode": None,
            "executable": str(executable.resolve()),
            "lean_path_entries": 0,
            "output": "",
        }
    try:
        version_run = subprocess.run(
            [str(executable), "--version"],
            cwd=LEAN_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "reason": "Lean version query timeout",
            "returncode": None,
            "executable": str(executable.resolve()),
            "lean_path_entries": len(libraries),
            "version": "",
            "output": "",
        }
    version = f"{version_run.stdout}\n{version_run.stderr}".strip()
    if version_run.returncode != 0 or PINNED_LEAN_VERSION not in version:
        return {
            "status": "FAIL",
            "reason": "Lean compiler version does not match the pinned toolchain",
            "returncode": version_run.returncode,
            "executable": str(executable.resolve()),
            "lean_path_entries": len(libraries),
            "version": version,
            "output": "",
        }
    environment = os.environ.copy()
    environment["LEAN_PATH"] = os.pathsep.join(str(path) for path in libraries)
    try:
        completed = subprocess.run(
            [str(executable), "Tect/R493.lean"],
            cwd=LEAN_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired as error:
        output = f"{error.stdout or ''}\n{error.stderr or ''}"
        return {
            "status": "FAIL",
            "reason": "Lean compile timeout",
            "returncode": None,
            "executable": str(executable.resolve()),
            "lean_path_entries": len(libraries),
            "version": version,
            "output": output[-4000:],
        }
    output = f"{completed.stdout}\n{completed.stderr}"
    clean = completed.returncode == 0 and "error:" not in output.lower()
    return {
        "status": "PASS" if clean else "FAIL",
        "reason": "compiled without diagnostics" if clean else "Lean emitted an error",
        "returncode": completed.returncode,
        "executable": str(executable.resolve()),
        "lean_path_entries": len(libraries),
        "version": version,
        "output": output[-4000:],
    }


def run(package_root: Path, output: Path) -> dict[str, Any]:
    contract = load_json(CONTRACT)
    manifest = load_json(MANIFEST)
    registry = load_json(REGISTRY)
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    manifest_hash = sha256(MANIFEST)
    contract_hash = sha256(CONTRACT)
    lean_hash = sha256(LEAN)
    check("manifest source pin", manifest_hash == MANIFEST_SHA256, manifest_hash, MANIFEST_SHA256)
    check("contract hash", contract_hash == manifest["contract"]["sha256"], contract_hash, manifest["contract"]["sha256"])
    check("R493 source hash", lean_hash == manifest["lean"]["sha256"], lean_hash, manifest["lean"]["sha256"])

    registry_entry = next(
        (item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R493.lean"),
        None,
    )
    check("registry hash", registry_entry is not None and registry_entry.get("sha256") == lean_hash, registry_entry, lean_hash)
    lean_source = LEAN.read_text(encoding="utf-8")
    forbidden_hits = {
        token: bool(re.search(rf"\b{re.escape(token)}\b", lean_source)) for token in FORBIDDEN
    }
    check("Lean source policy", not any(forbidden_hits.values()), forbidden_hits, "all forbidden tokens absent")
    declarations = manifest["lean"]["declarations"]
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", lean_source)
    check("Lean declaration markers", all(marker in declared for marker in declarations), declared, declarations)

    package_root = package_root.resolve()
    libraries = package_library_paths(package_root)
    check("package cache selected", package_root.is_dir(), str(package_root), "existing package directory")
    check("compiled package libraries", bool(libraries), [str(path) for path in libraries], "at least one library")
    lean = compile_r493(package_root)
    check("pinned Lean replay", lean["status"] == "PASS", lean, "PASS")

    toolchain_pin = TOOLCHAIN.read_text(encoding="utf-8").strip() if TOOLCHAIN.is_file() else None
    check("toolchain identity", toolchain_pin == registry.get("toolchain", {}).get("toolchain"), toolchain_pin, registry.get("toolchain", {}).get("toolchain"))

    failed = [row for row in rows if not row["pass"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc013-lean-canonical-environment/1.0",
        "run_kind": "environment_cross_check",
        "audit_id": "PAH-OMC-013-LEAN-CANONICAL-ENVIRONMENT-001",
        "result_id": manifest.get("result_id", "R-493"),
        "exploration_id": manifest.get("exploration_id", "EXP-001474"),
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "AUXILIARY_SUPPORT" if not failed else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {
            "PAH-OMC-013-contract": contract_hash,
            "PAH-OMC-013-manifest": manifest_hash,
            "R493-Lean": lean_hash,
            "lean-toolchain": sha256(TOOLCHAIN) if TOOLCHAIN.is_file() else None,
            "verification/scripts/pah_omc013_lean_canonical_env_check.py": sha256(Path(__file__)),
        },
        "lean": {
            "status": lean["status"],
            "compiler": lean.get("executable"),
            "expected_version": PINNED_LEAN_VERSION,
            "version": lean.get("version", ""),
            "package_root": str(package_root),
            "library_count": len(libraries),
            "command": "lean Tect/R493.lean with LEAN_PATH from selected package cache",
            "output": lean.get("output", ""),
        },
        "contract_scope": manifest.get("scope"),
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "boundary": "Environment-only replay of the finite OMC-013 Lean declarations. It does not prove closability, a common semigroup, weak Gibbs-L2 convergence, an infinite-volume or continuum limit, or any physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap, cosmic-origin, or TOE statement.",
        "non_claims": [
            "No change to PAH-001, the OMC-013 finite functional, rates, state, carrier, regulator, or limit order.",
            "No closability, common infinite-volume semigroup, weak Gibbs-L2 convergence, continuum limit, or ordered-limit theorem.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap, cosmic-origin, or TOE conclusion.",
        ],
        "reproduction": {
            "command": f"python -X utf8 verification/scripts/pah_omc013_lean_canonical_env_check.py --package-root {package_root.as_posix()}",
            "check": f"python -X utf8 verification/scripts/pah_omc013_lean_canonical_env_check.py --package-root {package_root.as_posix()} --check",
        },
    }
    atomic_json(output, payload)
    print(
        f"PAH-OMC-013 LEAN CANONICAL ENV: {payload['verification']} "
        f"{payload['passed']}/{payload['assertion_count']}; Lean={lean['status']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package-root",
        type=Path,
        default=REPO / "verification/lean/.lake/packages",
        help="existing read-only .lake/packages directory; no package is downloaded",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="replay and compare bytes with the existing output")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    if args.check:
        with tempfile.TemporaryDirectory(prefix="pah-omc013-lean-env-") as temporary:
            candidate = Path(temporary) / destination.name
            payload = run(args.package_root, candidate)
            if not destination.is_file() or candidate.read_bytes() != destination.read_bytes():
                print(f"PAH-OMC-013 LEAN CANONICAL ENV: replay mismatch at {destination}")
                return 1
            return 0 if payload["verification"] == "PASS" else 1
    payload = run(args.package_root, destination)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
