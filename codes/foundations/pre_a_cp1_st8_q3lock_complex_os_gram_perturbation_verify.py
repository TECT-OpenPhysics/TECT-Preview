#!/usr/bin/env python3
"""Integrated primary/independent/pinned-Lean verifier for EXP-001179."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-complex-os-gram-perturbation"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / "codes" / "foundations" / f"{SLUG.replace('-', '_')}_independent.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R340.lean"
LEAN_ROOT = REPO / "verification" / "lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-integrated-{SLUG}" / "integrated.json"
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def lake_path() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        if (candidate / name).is_file():
            return candidate / name
    found = shutil.which("lake")
    return Path(found) if found else None


def run_lean() -> dict[str, Any]:
    lake = lake_path()
    command = "lake env lean Tect/R340.lean"
    if lake is None:
        return {"status": "UNAVAILABLE", "command": command, "output": "pinned lake executable not found"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R340.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "command": command, "returncode": process.returncode, "output": output[-2000:]}


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row.get("graph"), row.get("source_site"), row.get("beta"), row.get("i"), row.get("j"))


def compare_rows(one: list[dict[str, Any]], two: list[dict[str, Any]], tolerance: float) -> tuple[bool, str]:
    if len(one) != len(two):
        return False, f"row count {len(one)} != {len(two)}"
    left = {row_key(row): row for row in one}
    right = {row_key(row): row for row in two}
    if len(left) != len(one) or len(right) != len(two):
        return False, "duplicate row key"
    if set(left) != set(right):
        return False, "row key sets differ"
    fields = ("tau_f", "tau_g", "vector_dimension", "partition", "raw_lhs", "raw_left_term", "raw_right_term", "raw_rhs", "normalized_lhs", "normalized_rhs", "normalized_slack", "identity_residual", "normalized_identity_residual", "tolerance")
    for key in sorted(left):
        for field in fields:
            a, b = left[key][field], right[key][field]
            if field == "vector_dimension":
                if a != b:
                    return False, f"{key} {field}: {a} != {b}"
            elif abs(float(a) - float(b)) > tolerance + tolerance * max(1.0, abs(float(a)), abs(float(b))):
                return False, f"{key} {field}: {a} != {b}"
    return True, "all rows agree within tolerance"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-lean", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001179", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001179/T-054/false")
    check("scope firewall", scope["r340_complex_gram_bound_closed"] and scope["finite_q3_os_transfer_word_factorization_closed"] and not scope["thermodynamic_common_os_hilbert_carrier_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["pre_a_closed"], scope, "finite actual bridge only")
    with tempfile.TemporaryDirectory(prefix="complex-os-gram-perturbation-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("child audit identity", primary.get("audit_id") == independent.get("audit_id") == "PA-CP1-ST8-Q3LOCK-COMPLEX-OS-GRAM-PERTURBATION", [primary.get("audit_id"), independent.get("audit_id")], "common audit id")
        check("formal marker agreement", primary.get("formal_checks") == independent.get("formal_checks") == ["finite_complex_gram_entry_perturbation"], [primary.get("formal_checks"), independent.get("formal_checks")], "R340 marker")
        check("scope agreement", primary.get("scope") == independent.get("scope"), primary.get("scope"), "identical scope")
        agreement, message = compare_rows(primary.get("rows", []), independent.get("rows", []), float(manifest["finite_fixture"]["agreement_tolerance"]))
        check("row agreement", agreement, message, "all primary/independent rows")
        check("row coverage", len(primary.get("rows", [])) == len(independent.get("rows", [])) and len(primary.get("rows", [])) > 0, [len(primary.get("rows", [])), len(independent.get("rows", []))], "same nonzero coverage")
    lean = {"status": "SKIPPED", "command": "lake env lean Tect/R340.lean"} if args.skip_lean else run_lean()
    check("Lean compile", args.skip_lean or lean["status"] == "PASS", lean, "PASS")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = next((item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R340.lean"), None)
    check("registry integrity", entry is not None and entry["sha256"] == sha256(LEAN), entry["sha256"] if entry else None, sha256(LEAN))
    payload = {"schema": "tect/foundation-audit/1.0", "run_kind": "integrated", "audit_id": "PA-CP1-ST8-Q3LOCK-COMPLEX-OS-GRAM-PERTURBATION", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "lean": lean, "formal_checks": ["finite_complex_gram_entry_perturbation"], "rows": primary.get("rows"), "scope": scope, "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "provenance": {"primary_sha256": sha256(PRIMARY), "independent_sha256": sha256(INDEPENDENT), "manifest_sha256": sha256(MANIFEST), "lean_sha256": sha256(LEAN), "registry_sha256": sha256(REGISTRY)}}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INTEGRATED COMPLEX-OS-GRAM-PERTURBATION PASS {len(checks)}/{len(checks)}; Lean={lean['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())