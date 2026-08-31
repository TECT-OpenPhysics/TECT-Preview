#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean audit for R-472."""

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
MANIFEST = REPO / "strategy/a2-r472-lean-crosscheck-manifest.json"
PRIMARY = REPO / "codes/foundations/a2_r472_lean_crosscheck.py"
INDEPENDENT = REPO / "codes/foundations/a2_r472_lean_crosscheck_independent.py"
HOSTILE = REPO / "codes/foundations/a2_r472_lean_crosscheck_hostile.py"
LEAN_ROOT = REPO / "verification/lean"
DEFAULT_OUTPUT = REPO / (
    "claims/A2-FULL-PRODUCTION-WELLPOSED/runs/"
    "2026-08-31-integrated-r472-a2-lean-crosscheck/integrated.json"
)
PYTHON = Path(os.environ.get("TECT_PYTHON", sys.executable))


def digest(path: Path, *, normalise: bool = False) -> str:
    data = path.read_bytes()
    if normalise:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
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


def lean_run() -> dict[str, Any]:
    registry = json.loads((LEAN_ROOT / "registry.json").read_text(encoding="utf-8"))
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidates = [Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe", Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake"]
    lake = next((item for item in candidates if item.is_file()), None) or shutil.which("lake")
    if lake is None:
        return {"status": "FAIL", "returncode": 1, "command": "lake env lean Tect/R472.lean", "output": "pinned lake executable missing"}
    process = subprocess.run([str(lake), "env", "lean", "Tect/R472.lean"], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False, timeout=180)
    output = (process.stdout + "\n" + process.stderr).strip()
    return {"status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": process.returncode, "command": "lake env lean Tect/R472.lean", "output": output[-2000:]}


def child(script: Path, output: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    process = subprocess.run([str(PYTHON), "-X", "utf8", str(script), "--output", str(output)], cwd=REPO, text=True, encoding="utf-8", capture_output=True, check=False, timeout=180)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, payload


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-472", "EXP-001347", False], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-472", "EXP-001347", False])
    check("methods unchanged", manifest["formal_integration"]["methods_unchanged"] is True and all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")
    check("no tier/PDF/negative mutation", manifest["formal_integration"]["no_tier_change"] is True and manifest["formal_integration"]["no_pdf"] is True and manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"], "T0/no PDF/no new negative")
    for name, item in manifest["authorities"].items():
        path = REPO / item["path"]
        check(f"authority {name}", path.is_file() and digest(path) == item["sha256"], digest(path) if path.is_file() else "MISSING", item["sha256"])
    for name, item in manifest["files"].items():
        path = REPO / item["path"]
        if item["sha256"]:
            check(f"file {name}", path.is_file() and digest(path, normalise=name == "lean_entrypoint") == item["sha256"], digest(path, normalise=name == "lean_entrypoint") if path.is_file() else "MISSING", item["sha256"])

    with tempfile.TemporaryDirectory(prefix="tect-r472-integrated-") as temporary:
        primary_process, primary = child(PRIMARY, Path(temporary) / "primary.json")
        independent_process, independent = child(INDEPENDENT, Path(temporary) / "independent.json")
        hostile_process, hostile = child(HOSTILE, Path(temporary) / "hostile.json")
        check("primary child", primary_process.returncode == 0 and primary.get("verdict") == "PASS", primary_process.stdout + primary_process.stderr, "PASS")
        check("independent child", independent_process.returncode == 0 and independent.get("verdict") == "PASS", independent_process.stdout + independent_process.stderr, "PASS")
        check("hostile child", hostile_process.returncode == 0 and hostile.get("verdict") == "PASS", hostile_process.stdout + hostile_process.stderr, "PASS")
        check("primary/independent exact parity", primary.get("derived") == independent.get("derived"), [primary.get("derived"), independent.get("derived")], "equal derived core")
        check("primary and independent T0", primary.get("claim_bearing") is False and independent.get("claim_bearing") is False and primary.get("tier") == independent.get("tier") == "T0", [primary.get("claim_bearing"), independent.get("claim_bearing"), primary.get("tier"), independent.get("tier")], [False, False, "T0", "T0"])
        check("hostile mutations rejected", hostile.get("all_mutations_rejected") is True and hostile.get("mutation_count", 0) >= 9, hostile.get("mutation_count"), ">=9")
        check("positive child assertions", all(item.get("assertion_count", 0) > 0 for item in (primary, independent, hostile)), [item.get("assertion_count") for item in (primary, independent, hostile)], ">0")

    lean = lean_run()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")
    check("no physical promotion", all(not bool(manifest["scope"].get(key)) for key in ("physical_owner", "physical_vacuum", "qft_yang_mills", "continuum_or_thermodynamic_limit", "sector_a_or_pre_a_closure")), manifest["scope"], "all promotion flags false")

    payload = {
        "schema": "tect/a2-r472-lean-crosscheck-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"] + "-INTEGRATED",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "tier": "T0",
        "methods_unchanged": True,
        "assertion_count": len(rows),
        "passed": len(rows),
        "assertions": rows,
        "lean": lean,
        "scope": manifest["scope"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "falsifiers": manifest["falsifiers"],
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"manifest_sha256": digest(MANIFEST), "primary_sha256": digest(PRIMARY), "independent_sha256": digest(INDEPENDENT), "hostile_sha256": digest(HOSTILE), "lean_sha256": digest(REPO / manifest["files"]["lean_entrypoint"]["path"], normalise=True)},
    }
    atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-472 INTEGRATED PASS {len(rows)}/{len(rows)}; Lean={lean['status']}; methods unchanged")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
