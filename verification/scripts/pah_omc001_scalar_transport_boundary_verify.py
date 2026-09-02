#!/usr/bin/env python3
"""Integrated verifier for the PAH positive-scalar transport boundary."""

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
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
LEAN_ROOT = ROOT / "verification/lean"
LEAN = LEAN_ROOT / "Tect/R481.lean"
REGISTRY = LEAN_ROOT / "registry.json"
DEFAULT_DIR = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r481-pah-positive-scalar-transport-boundary"
)


def sha256(path: Path, normalized: bool = False) -> str:
    data = path.read_bytes()
    if normalized:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


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
        mode="w",
        encoding="utf-8",
        newline="\n",
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def run(directory: Path = DEFAULT_DIR) -> dict[str, Any]:
    primary = load(directory / "primary.json")
    independent = load(directory / "independent.json")
    hostile = load(directory / "hostile.json")
    expected_parent = (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    expected_contract = (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    check("parent-hash", sha256(PARENT) == expected_parent, sha256(PARENT))
    check("contract-hash", sha256(CONTRACT) == expected_contract, sha256(CONTRACT))
    check(
        "primary-sources",
        primary.get("source_authorities", [{}])[0].get("sha256") == expected_parent
        and primary.get("source_authorities", [{}, {}])[1].get("sha256")
        == expected_contract,
    )
    check(
        "independent-sources",
        independent.get("source_hashes")
        == {"PAH-001": expected_parent, "PAH-OMC-001": expected_contract},
        independent.get("source_hashes"),
    )
    check(
        "primary-pass",
        primary.get("assertions", {}).get("all_pass") is True
        and primary.get("verdict") == "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
    )
    check(
        "independent-pass",
        independent.get("assertions", {}).get("all_pass") is True
        and independent.get("verdict") == "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
    )
    check(
        "case-count-agreement",
        primary.get("assertions", {}).get("cases")
        == independent.get("assertions", {}).get("cases")
        == primary.get("assertions", {}).get("nonzero_defects")
        == independent.get("assertions", {}).get("nonzero_defects"),
        [
            primary.get("assertions", {}).get("cases"),
            independent.get("assertions", {}).get("cases"),
        ],
    )
    check(
        "hostile-pass",
        hostile.get("assertions", {}).get("all_mutations_rejected") is True
        and hostile.get("assertions", {}).get("route_local_boundary_preserved") is True,
        hostile.get("assertions"),
    )
    check(
        "stage2-held",
        primary.get("stage2_status") == independent.get("stage2_status")
        == hostile.get("stage2_status")
        == "HOLD_FOR_EVIDENCE",
    )
    check(
        "no-model-mutation",
        "No PAH-001" in " ".join(primary.get("non_claims", []))
        and "No PAH-001" in " ".join(independent.get("non_claims", [])),
    )

    registry = load(REGISTRY)
    entry = next(
        (
            item
            for item in registry.get("entrypoints", [])
            if item.get("path") == "verification/lean/Tect/R481.lean"
        ),
        None,
    )
    check("lean-registry-entry", entry is not None, entry)
    lean_hash = sha256(LEAN, normalized=True)
    check("lean-hash", entry is not None and entry.get("sha256") == lean_hash, lean_hash)
    lake = pinned_lake(registry)
    if lake is None:
        lean_pass = False
        lean_output = "pinned lake executable missing"
        lean_returncode = 1
    else:
        process = subprocess.run(
            [str(lake), "env", "lean", "Tect/R481.lean"],
            cwd=LEAN_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=180,
        )
        lean_returncode = process.returncode
        lean_output = (process.stdout + process.stderr).strip()
        lean_pass = process.returncode == 0 and "error:" not in lean_output.lower()
    check("lean-compile", lean_pass, lean_output[-2000:])

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc-positive-scalar-transport-boundary-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": "PAH-OMC-SCALAR-TRANSPORT-001",
        "exploration_id": "EXP-001364",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "verdict": "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "lean": {
            "status": "PASS" if lean_pass else "FAIL",
            "command": "lake env lean Tect/R481.lean",
            "returncode": lean_returncode,
            "output": lean_output[-2000:],
        },
        "source_hashes": {"PAH-001": expected_parent, "PAH-OMC-001": expected_contract},
        "non_claims": [
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No global refinement no-go is claimed.",
            "No nontrivial refinement, uniform limit, continuum or observable law is admitted.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    atomic_json(directory / "integrated.json", payload)
    print(
        "PAH-OMC-SCALAR-TRANSPORT-001 INTEGRATED "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"Lean={payload['lean']['status']}; verdict={payload['verdict']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    payload = run(args.directory)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
