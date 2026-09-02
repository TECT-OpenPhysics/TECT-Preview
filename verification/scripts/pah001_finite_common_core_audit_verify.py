#!/usr/bin/env python3
"""Integrated verification for the PAH-FCC-001 HOLD verdict."""

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
MANIFEST = REPO / "strategy/pa-hyp/finite-common-core-audit-v1.json"
SOURCE = REPO / "strategy/pa-hyp/PAH-001-v1.json"
PRIMARY = REPO / "codes/foundations/pah001_finite_common_core_audit.py"
INDEPENDENT = REPO / "codes/foundations/pah001_finite_common_core_audit_independent.py"
HOSTILE = REPO / "codes/foundations/pah001_finite_common_core_audit_hostile.py"
LEAN_ROOT = REPO / "verification/lean"
REGISTRY = LEAN_ROOT / "registry.json"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r478-pah001-common-core/integrated.json"
)


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path, normalised: bool = False) -> str:
    data = normalised_bytes(path) if normalised else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


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
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )
    return process, load(output)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("source-hash", sha256(SOURCE) == manifest["source"]["sha256"], sha256(SOURCE))
    check("manifest-hold", manifest.get("verdict") == "HOLD_FOR_EVIDENCE")
    check("manifest-no-model-mutation", not any(manifest.get("model_mutation", {}).values()))
    check("manifest-no-gate-change", manifest.get("gate_changed") is False)
    check("manifest-no-negative", manifest.get("negative_result_registered") is False)

    lean_path = REPO / manifest["lean"]["path"]
    lean_entry = next(
        (item for item in registry.get("entrypoints", []) if item.get("path") == manifest["lean"]["path"]),
        None,
    )
    check("lean-registry-entry", lean_entry is not None, lean_entry)
    if lean_entry is None:
        raise AssertionError("R478 Lean registry entry missing")
    check("lean-source-hash", sha256(lean_path, normalised=True) == lean_entry["sha256"], sha256(lean_path, normalised=True))
    check("lean-declarations", lean_entry.get("declarations") == manifest["lean"]["declarations"], lean_entry.get("declarations"))

    with tempfile.TemporaryDirectory(prefix="pah-fcc-001-") as directory:
        root = Path(directory)
        primary_process, primary = run_child(PRIMARY, root / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, root / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, root / "hostile.json")

    for name, process, result in (
        ("primary", primary_process, primary),
        ("independent", independent_process, independent),
        ("hostile", hostile_process, hostile),
    ):
        check(name + "-exit-zero", process.returncode == 0, process.stdout + process.stderr)
        check(name + "-pass", result.get("verification") == "PASS", result.get("verification"))
        check(name + "-hold", result.get("verdict") == "HOLD_FOR_EVIDENCE", result.get("verdict"))
        check(name + "-nonclaim", result.get("claim_bearing") is False)
        check(name + "-no-gate-change", result.get("gate_changed") is False)

    check("primary-count", (primary.get("passed"), primary.get("assertion_count")) == (170, 170), [primary.get("passed"), primary.get("assertion_count")])
    check("independent-count", (independent.get("passed"), independent.get("assertion_count")) == (134, 134), [independent.get("passed"), independent.get("assertion_count")])
    check("hostile-count", (hostile.get("passed"), hostile.get("assertion_count")) == (31, 31), [hostile.get("passed"), hostile.get("assertion_count")])
    check("hostile-mutations", (hostile.get("mutations_rejected"), hostile.get("mutations_attempted")) == (30, 30), [hostile.get("mutations_rejected"), hostile.get("mutations_attempted")])
    check("core-identical", primary.get("core") == independent.get("core"))
    check("core-digest-identical", primary.get("core_digest") == independent.get("core_digest"))
    check("primary-core-integrity", primary.get("core_digest") == canonical_hash(primary.get("core")))
    check("independent-core-integrity", independent.get("core_digest") == canonical_hash(independent.get("core")))

    lake = pinned_lake(registry)
    check("pinned-lake", lake is not None, str(lake) if lake else "missing")
    if lake is None:
        lean_process = None
        lean_pass = False
        lean_output = "pinned lake executable missing"
    else:
        lean_process = subprocess.run(
            [str(lake), "env", "lean", "Tect/R478.lean"],
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
        "schema": "tect/pah001-finite-common-core-integrated-run/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "child_summary": {
            "primary": {"assertions": primary["assertion_count"], "core_digest": primary["core_digest"]},
            "independent": {"assertions": independent["assertion_count"], "core_digest": independent["core_digest"]},
            "hostile": {"assertions": hostile["assertion_count"], "mutations": hostile["mutations_attempted"]},
        },
        "core_digest": primary["core_digest"],
        "lean": {
            "status": "PASS" if lean_pass else "FAIL",
            "command": "lake env lean Tect/R478.lean",
            "returncode": lean_process.returncode if lean_process else 1,
            "output": lean_output,
            "scope": manifest["lean"]["scope"],
        },
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(
        "PAH-FCC-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"primary={primary['assertion_count']}; independent={independent['assertion_count']}; "
        f"hostile={hostile['mutations_rejected']}/{hostile['mutations_attempted']}; "
        f"Lean={payload['lean']['status']}; verdict={payload['verdict']}; "
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
