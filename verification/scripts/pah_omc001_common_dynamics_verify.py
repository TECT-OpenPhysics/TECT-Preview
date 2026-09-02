#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean verification for R-479."""

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


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json"
PRIMARY = ROOT / "codes/foundations/pah_omc001_common_dynamics.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc001_common_dynamics_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc001_common_dynamics_hostile.py"
LEAN_ROOT = ROOT / "verification/lean"
REGISTRY_PATH = LEAN_ROOT / "registry.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r479-pah-omc001/integrated.json"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


def pinned_lake(registry: dict[str, Any]) -> Path | None:
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    directory = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = directory / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )
    return process, load(output)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    audit = load(AUDIT_PATH)
    registry = load(REGISTRY_PATH)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("audit-id", audit.get("audit_id") == "PAH-OMC-AUDIT-001")
    check("result-id", audit.get("result_id") == "R-479")
    check("stage1-advance", audit.get("finite_common_dynamics_verdict") == "MAINLINE_ADVANCE")
    check("stage2-hold", audit.get("uniform_refinement_verdict") == "HOLD_FOR_EVIDENCE")
    check("overall-hold-stage2", audit.get("overall_programme_state") == "HOLD_FOR_EVIDENCE_AT_STAGE_2")
    check("claim-nonbearing", audit.get("claim_bearing") is False)
    check("active-gate-unchanged", audit.get("active_gate_changed") is False)

    lean_path = ROOT / audit["lean"]["path"]
    lean_entry = next(
        (
            item
            for item in registry.get("entrypoints", [])
            if item.get("path") == audit["lean"]["path"]
        ),
        None,
    )
    check("lean-registry-entry", lean_entry is not None, lean_entry)
    if lean_entry is None:
        raise AssertionError("R479 Lean registry entry missing")
    actual_lean_hash = normalized_sha256(lean_path)
    check("lean-audit-hash", actual_lean_hash == audit["lean"]["sha256_normalized"], actual_lean_hash)
    check("lean-registry-hash", actual_lean_hash == lean_entry.get("sha256"), actual_lean_hash)
    check("lean-declarations", lean_entry.get("declarations") == audit["lean"]["declarations"], lean_entry.get("declarations"))
    lean_text = lean_path.read_text(encoding="utf-8")
    for escape in ("sorry", "admit", "axiom", "unsafe"):
        check("lean-no-" + escape, escape not in lean_text)

    with tempfile.TemporaryDirectory(prefix="pah-omc001-") as directory:
        temporary = Path(directory)
        primary_process, primary = run_child(PRIMARY, temporary / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, temporary / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, temporary / "hostile.json")

    for name, process, result in (
        ("primary", primary_process, primary),
        ("independent", independent_process, independent),
        ("hostile", hostile_process, hostile),
    ):
        check(name + "-exit-zero", process.returncode == 0, process.stdout + process.stderr)
        check(name + "-pass", result.get("verification") == "PASS", result.get("verification"))
        check(name + "-stage1", result.get("finite_common_dynamics_verdict") == "MAINLINE_ADVANCE")
        check(name + "-stage2", result.get("uniform_refinement_verdict") == "HOLD_FOR_EVIDENCE")
        check(name + "-nonclaim", result.get("claim_bearing") is False)
        check(name + "-gate", result.get("active_gate_changed") is False)
        check(name + "-physical", result.get("physical_progress") is False)

    expected = audit["expected_verification"]
    check("primary-minimum", primary.get("assertion_count", 0) >= expected["primary_minimum_assertions"], primary.get("assertion_count"))
    check("independent-minimum", independent.get("assertion_count", 0) >= expected["independent_minimum_assertions"], independent.get("assertion_count"))
    check("hostile-minimum", hostile.get("mutations_rejected", 0) >= expected["hostile_minimum_mutations"], hostile.get("mutations_rejected"))
    check("hostile-all-rejected", hostile.get("mutations_rejected") == hostile.get("mutations_attempted"))
    check("primary-independent-core", primary.get("core") == independent.get("core"))
    check("primary-independent-digest", primary.get("core_digest") == independent.get("core_digest"))
    check("primary-core-integrity", primary.get("core_digest") == canonical_hash(primary.get("core")))
    check("independent-core-integrity", independent.get("core_digest") == canonical_hash(independent.get("core")))

    lake = pinned_lake(registry)
    check("pinned-lake", lake is not None, str(lake) if lake else "missing")
    if lake is None:
        lean_process = None
        lean_output = "pinned lake executable missing"
        lean_pass = False
    else:
        lean_process = subprocess.run(
            [str(lake), "env", "lean", "Tect/R479.lean"],
            cwd=LEAN_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        lean_output = (lean_process.stdout + lean_process.stderr)[-4000:]
        lean_pass = lean_process.returncode == 0 and "error:" not in lean_output.lower()
    check("lean-compile", lean_pass, lean_output)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc001-integrated-run/1.0",
        "run_kind": "integrated",
        "audit_id": audit["audit_id"],
        "result_id": audit["result_id"],
        "exploration_id": audit["exploration_id"],
        "task_id": audit["task_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "finite_common_dynamics_verdict": audit["finite_common_dynamics_verdict"],
        "uniform_refinement_verdict": audit["uniform_refinement_verdict"],
        "overall_programme_state": audit["overall_programme_state"],
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "children": {
            "primary": {"assertions": primary["assertion_count"], "core_digest": primary["core_digest"]},
            "independent": {"assertions": independent["assertion_count"], "core_digest": independent["core_digest"]},
            "hostile": {"assertions": hostile["assertion_count"], "mutations": hostile["mutations_attempted"]},
        },
        "core_digest": primary["core_digest"],
        "lean": {
            "status": "PASS" if lean_pass else "FAIL",
            "command": "lake env lean Tect/R479.lean",
            "returncode": lean_process.returncode if lean_process else 1,
            "output": lean_output,
            "scope": audit["lean"]["scope"],
        },
        "claim_bearing": False,
        "active_gate_changed": False,
        "physical_progress": False,
        "non_claims": audit["non_claims"],
    }
    atomic_json(output, payload)
    print(
        "PAH-OMC-AUDIT-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"primary={primary['assertion_count']}; independent={independent['assertion_count']}; "
        f"hostile={hostile['mutations_rejected']}/{hostile['mutations_attempted']}; "
        f"Lean={payload['lean']['status']}; "
        f"finite={payload['finite_common_dynamics_verdict']}; "
        f"refinement={payload['uniform_refinement_verdict']}; "
        f"core={payload['core_digest']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
