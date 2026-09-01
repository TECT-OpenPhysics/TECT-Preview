#!/usr/bin/env python3
"""Integrated primary, independent, hostile, and Lean audit for R-476.

The verifier certifies only the structural intake and promotion firewalls of
the PAH-001 researcher hypothesis.  It does not prove the proposed finite
dynamics, either collapse predicate, a common-core limit, or physical identity.
"""

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
MANIFEST = REPO / "strategy/pa-hyp/intake-v1.json"
SOURCE = REPO / "strategy/pa-hyp/PAH-001-v1.json"
PRIMARY = REPO / "codes/foundations/pah001_intake.py"
INDEPENDENT = REPO / "codes/foundations/pah001_intake_independent.py"
HOSTILE = REPO / "codes/foundations/pah001_intake_hostile.py"
LEAN = REPO / "verification/lean/Tect/R476.lean"
LEAN_ROOT = REPO / "verification/lean"
REGISTRY = LEAN_ROOT / "registry.json"


def sha256(path: Path, *, normalize_lf: bool = False) -> str:
    data = path.read_bytes()
    if normalize_lf:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def pinned_lake() -> Path | None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def run_lean() -> dict[str, Any]:
    command = "lake env lean Tect/R476.lean"
    lake = pinned_lake()
    if lake is None:
        return {"status": "FAIL", "returncode": 1, "command": command, "output": "pinned lake executable missing"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R476.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    combined = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in combined.lower() else "FAIL",
        "returncode": process.returncode,
        "command": command,
        "output": combined[-2000:],
        "lake": str(lake),
    }


def run_child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def run(output: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        row = {"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected}
        checks.append(row)
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id")] == ["R-476", "EXP-001357", "T-062"], [manifest.get("result_id"), manifest.get("exploration_id"), manifest.get("task_id")], ["R-476", "EXP-001357", "T-062"])
    check("T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, [manifest.get("tier"), manifest.get("claim_bearing")], ["T0", False])
    check("source hash", sha256(SOURCE) == manifest["source_artifact"]["sha256"], sha256(SOURCE), manifest["source_artifact"]["sha256"])

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    lean_entry = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R476.lean"), None)
    check("Lean registry entry", lean_entry is not None, lean_entry, "registered R476.lean")
    if lean_entry is None:
        raise AssertionError("Lean registry entry missing")
    check("Lean registry hash", sha256(LEAN, normalize_lf=True) == lean_entry.get("sha256"), sha256(LEAN, normalize_lf=True), lean_entry.get("sha256"))
    check("Lean declarations", lean_entry.get("declarations") == manifest["lean"]["declarations"], lean_entry.get("declarations"), manifest["lean"]["declarations"])

    with tempfile.TemporaryDirectory(prefix="tect-r476-") as temporary:
        root = Path(temporary)
        primary_process, primary = run_child(PRIMARY, root / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, root / "hostile.json")

    for name, process, payload in (
        ("primary", primary_process, primary),
        ("independent", independent_process, independent),
        ("hostile", hostile_process, hostile),
    ):
        check(f"{name} child exit", process.returncode == 0, {"returncode": process.returncode, "stdout": process.stdout[-1000:], "stderr": process.stderr[-1000:]}, 0)
        check(f"{name} verdict", str(payload.get("verdict", "")).endswith("PASS") or payload.get("verdict") == "PASS", payload.get("verdict"), "PASS")

    check("primary-independent state agreement", primary.get("current_state") == independent.get("current_state") == "OWNER_PACKET_HASHED", [primary.get("current_state"), independent.get("current_state")], "OWNER_PACKET_HASHED")
    check("primary-independent core digest", primary.get("core_digest") == independent.get("core_digest") and bool(primary.get("core_digest")), [primary.get("core_digest"), independent.get("core_digest")], "one nonempty digest")
    check("production admission empty", all(item.get("production_admission") == "NONE" for item in (primary, independent, hostile)), [item.get("production_admission") for item in (primary, independent, hostile)], "NONE")
    check("physical owner remains false", primary.get("physical_owner_admitted") is False and independent.get("physical_owner_admitted") is False and hostile.get("physical_owner_admitted") is False, [primary.get("physical_owner_admitted"), independent.get("physical_owner_admitted"), hostile.get("physical_owner_admitted")], [False, False, False])
    check("hostile mutation floor", hostile.get("all_mutations_rejected") is True and int(hostile.get("mutation_count", 0)) >= int(manifest["test_oracles"]["hostile_minimum_mutations"]), hostile.get("mutation_count"), f">={manifest['test_oracles']['hostile_minimum_mutations']}")
    check("child assertion floors", int(primary.get("assertion_count", 0)) >= int(manifest["test_oracles"]["primary_minimum_assertions"]) and int(independent.get("assertion_count", 0)) >= int(manifest["test_oracles"]["independent_minimum_assertions"]), [primary.get("assertion_count"), independent.get("assertion_count")], [manifest["test_oracles"]["primary_minimum_assertions"], manifest["test_oracles"]["independent_minimum_assertions"]])
    check("methods unchanged", all(item.get("methods_unchanged") is True for item in (primary, independent, hostile)), [item.get("methods_unchanged") for item in (primary, independent, hostile)], [True, True, True])

    lean = run_lean()
    check("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    payload = {
        "schema": "tect/pah001-structural-intake-run/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "packet_id": "PAH-001",
        "candidate_id": "PA-M6-RELATIONAL-APERTURE-TRANSFER-v0",
        "verdict": "PAH001-STRUCTURAL-INTAKE-INTEGRATED-PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "classification": "mainline_advance",
        "hypothesis_packet_state": "OWNER_PACKET_HASHED",
        "r471_canonical_current_snapshot": "EMPTY_OWNER_ARTIFACT",
        "production_admission": "NONE",
        "physical_owner_admitted": False,
        "physical_projection_admitted": False,
        "F_reg_admitted": False,
        "F_lim_admitted": False,
        "F_eff_admitted": False,
        "F_obs_admitted": False,
        "gate_changed": False,
        "scientific_transition": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "assertions": checks,
        "child_summary": {
            "primary": {"assertions": primary.get("assertion_count"), "core_digest": primary.get("core_digest")},
            "independent": {"assertions": independent.get("assertion_count"), "core_digest": independent.get("core_digest")},
            "hostile": {"assertions": hostile.get("assertion_summary", {}).get("total"), "mutations": hostile.get("mutation_count")},
        },
        "lean": lean,
        "evidence_level": "T0 / HASH-PINNED RESEARCHER-HYPOTHESIS STRUCTURAL INTAKE WITH INDEPENDENT, HOSTILE, INTEGRATED AND LEAN FIREWALLS",
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "next_action": manifest["next_action"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "source_sha256": sha256(SOURCE),
            "manifest_sha256": sha256(MANIFEST),
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "hostile_sha256": sha256(HOSTILE),
            "lean_sha256": sha256(LEAN, normalize_lf=True),
            "registry_sha256": sha256(REGISTRY),
        },
    }
    target = output if output.is_absolute() else REPO / output
    atomic_json(target, payload)
    print(
        f"PAH-001 INTEGRATED PASS {len(checks)}/{len(checks)}; "
        f"primary={primary.get('assertion_count')}; independent={independent.get('assertion_count')}; "
        f"hostile={hostile.get('mutation_count')} mutations; Lean={lean.get('status')}"
    )
    return payload


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    default_output = REPO / manifest["runs"]["integrated"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
