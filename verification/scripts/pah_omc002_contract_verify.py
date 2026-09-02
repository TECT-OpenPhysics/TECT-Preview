#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-002 contract-admission packet.

The packet is a structural successor contract, not an intertwining theorem.
This verifier combines the independent structural lanes, pins all source
hashes, and rechecks the inherited R479 Lean theorem without promoting it to a
conditional-kernel result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
REGISTRY = ROOT / "verification/lean/registry.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN_PATH = LEAN_ROOT / "Tect/R479.lean"
DEFAULT_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-contract"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path, normalized: bool = False) -> str:
    data = path.read_bytes()
    if normalized:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def pinned_lake(registry: dict[str, Any]) -> Path | None:
    encoded = registry["toolchain"]["toolchain"].replace("/", "--").replace(":", "---")
    root = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        candidate = root / name
        if candidate.is_file():
            return candidate
    found = shutil.which("lake")
    return Path(found) if found else None


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def run(directory: Path = DEFAULT_DIR) -> dict[str, Any]:
    manifest = load(MANIFEST)
    contract = load(CONTRACT)
    primary = load(directory / "primary.json")
    independent = load(directory / "independent.json")
    hostile = load(directory / "hostile.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected = {
        "PAH-OMC-002": manifest["contract"]["sha256"],
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
    }
    actual = {
        "PAH-OMC-002": digest(CONTRACT),
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
    }
    check("source-hashes", actual == expected, actual)
    check("primary-source-hashes", primary.get("source_hashes") == actual, primary.get("source_hashes"))
    check("independent-source-hashes", independent.get("source_hashes") == actual, independent.get("source_hashes"))
    check("hostile-source-hashes", hostile.get("source_hashes") == actual, hostile.get("source_hashes"))
    check("primary-pass", primary.get("verification") == "PASS" and primary.get("verdict") == "CANDIDATE_NOT_ADMITTED")
    check("independent-pass", independent.get("verification") == "PASS" and independent.get("verdict") == "CANDIDATE_NOT_ADMITTED")
    check(
        "hostile-pass",
        hostile.get("verification") == "PASS"
        and hostile.get("assertions", {}).get("all_mutations_rejected") is True
        and hostile.get("assertions", {}).get("mutations_rejected") == hostile.get("assertions", {}).get("mutations_attempted"),
        hostile.get("assertions"),
    )
    check("stage2-held", all(item.get("stage2_status") == "HOLD_FOR_EVIDENCE" for item in (primary, independent, hostile)))
    check("no-physical-progress", all(item.get("physical_progress") is False for item in (primary, independent, hostile)))
    check("contract-id", contract.get("contract_id") == "PAH-OMC-002")
    check("kernel-target-present", "conditional_projected" in contract.get("compatibility_targets", {}))
    check("inherited-r479-only", "R-480/R-481" in contract.get("known_boundaries", {}).get("natural_pullback", ""))

    registry = load(REGISTRY)
    lake = pinned_lake(registry)
    if lake is None:
        lean_ok = False
        lean_detail = "pinned lake executable missing"
    else:
        process = subprocess.run(
            [str(lake), "env", "lean", str(LEAN_PATH.relative_to(LEAN_ROOT))],
            cwd=LEAN_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=180,
        )
        lean_detail = (process.stdout + process.stderr).strip()
        lean_ok = process.returncode == 0 and "error:" not in lean_detail.lower()
    check("inherited-r479-lean", lean_ok, lean_detail[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc002-contract-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-002-CONTRACT-AUDIT-001",
        "exploration_id": "EXP-001366",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual,
        "contract_status": contract.get("status"),
        "verdict": "CANDIDATE_NOT_ADMITTED",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "lean": {
            "path": "verification/lean/Tect/R479.lean",
            "status": "PASS" if lean_ok else "FAIL",
            "inherited_only": True,
            "output": lean_detail[-2000:],
        },
        "physical_progress": False,
        "non_claims": [
            "This packet does not prove conditional-kernel or strong generator intertwining.",
            "R479 Lean is inherited finite composite evidence only and is not a theorem about PAH-OMC-002.",
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
        ],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(directory / "integrated.json", payload)
    print(
        "PAH-OMC-002-CONTRACT-AUDIT-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"Lean={payload['lean']['status']}; verdict={payload['verdict']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    result = run(args.directory)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
