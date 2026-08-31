#!/usr/bin/env python3
"""Integrated primary/independent/hostile/Lean audit for R-475.

R-475 is a claim-nonbearing T0 sidecar for the already operator-confirmed
A5 T6 conditional-composition package.  The integrated run checks provenance,
re-executes the two exact Python lanes and the fail-closed hostile harness in
isolated outputs, then compiles the pinned Lean entrypoint.  It deliberately
does not alter the A5 claim tier or infer any physical/continuum conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a5-r475-lean-crosscheck-manifest.json"
PRIMARY = REPO / "verification" / "scripts" / "a5_r475_lean_crosscheck.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a5_r475_lean_crosscheck_independent.py"
HOSTILE = REPO / "codes" / "foundations" / "a5_r475_lean_crosscheck_hostile.py"
LEAN = REPO / "verification" / "lean" / "Tect" / "R475.lean"
DEFAULT_OUTPUT = REPO / (
    "claims/A5-SECTOR-A-SYNTHESIS/runs/"
    "2026-09-01-a5-r475-lean-crosscheck/integrated.json"
)


def sha256(path: Path, *, normalise: bool = False) -> str | None:
    if not path.is_file():
        return None
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


def pinned_lake() -> Path | None:
    registry = json.loads((REPO / "verification" / "lean" / "registry.json").read_text(encoding="utf-8"))
    pin = registry["toolchain"]["toolchain"]
    encoded = pin.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file():
            return path
    found = shutil.which("lake")
    return Path(found) if found else None


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
    report = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    return process, report


def run_lean() -> dict[str, Any]:
    lake = pinned_lake()
    command = "lake env lean Tect/R475.lean"
    if lake is None:
        return {"status": "FAIL", "returncode": 1, "command": command, "output": "pinned lake executable missing"}
    process = subprocess.run(
        [str(lake), "env", "lean", "Tect/R475.lean"],
        cwd=REPO / "verification" / "lean",
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": process.returncode,
        "command": command,
        "output": output[-2000:],
        "lake": str(lake),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def add(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    add(
        "manifest identity",
        manifest.get("audit_id") == "A5-R475-LEAN-CROSSCHECK"
        and manifest.get("result_id") == "R-475"
        and manifest.get("exploration_id") == "EXP-001354"
        and manifest.get("claim_id") == "A5-SECTOR-A-SYNTHESIS",
        {key: manifest.get(key) for key in ("audit_id", "result_id", "exploration_id", "claim_id")},
        "A5-R475-LEAN-CROSSCHECK / R-475 / EXP-001354",
    )
    add(
        "T0 claim firewall",
        manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False,
        {"tier": manifest.get("tier"), "claim_bearing": manifest.get("claim_bearing")},
        {"tier": "T0", "claim_bearing": False},
    )
    preservation = manifest.get("method_preservation", {})
    add(
        "methods and owner order unchanged",
        isinstance(preservation, dict) and all(value is True for value in preservation.values()),
        preservation,
        "all method-preservation flags true",
    )
    scope = manifest.get("scope", {})
    forbidden_promotions = (
        "source_owned_dynamics",
        "common_core",
        "uniform_cutoff_volume_estimate",
        "ordered_limit",
        "physical_sector",
        "pre_a",
        "qft_yang_mills",
    )
    add(
        "no analytic or physical promotion",
        all(scope.get(key) is False for key in forbidden_promotions),
        {key: scope.get(key) for key in forbidden_promotions},
        "all downstream promotion flags false",
    )

    for name, item in manifest.get("authorities", {}).items():
        path = REPO / item["path"]
        actual = sha256(path)
        add(f"authority {name}", actual == item.get("sha256"), actual, item.get("sha256"))

    file_specs = manifest.get("files", {})
    for name, item in file_specs.items():
        path = REPO / item["path"]
        expected = item.get("sha256")
        actual = sha256(path, normalise=name == "lean")
        # The integrated file has no self-referential hash in the manifest.
        add(f"file {name} exists", path.is_file(), actual, expected or "present")
        if expected:
            add(f"file {name} hash", actual == expected, actual, expected)

    lean_source = LEAN.read_text(encoding="utf-8") if LEAN.is_file() else ""
    add(
        "Lean source has no escape tokens",
        not any(re.search(rf"\b{re.escape(token)}\b", lean_source) for token in ("sorry", "admit", "axiom", "unsafe")),
        "escape tokens absent" if lean_source else "missing",
        "none",
    )
    declarations = manifest.get("lean", {}).get("declarations", [])
    add(
        "Lean declaration markers",
        all(re.search(rf"\b(?:theorem|lemma|example)\s+{re.escape(marker)}\b", lean_source) for marker in declarations),
        declarations,
        "all declared R475 theorems",
    )

    with tempfile.TemporaryDirectory(prefix="tect-r475-integrated-") as temporary:
        temp = Path(temporary)
        primary_process, primary = run_child(PRIMARY, temp / "primary.json")
        independent_process, independent = run_child(INDEPENDENT, temp / "independent.json")
        hostile_process, hostile = run_child(HOSTILE, temp / "hostile.json")

    primary_verdict = "R475-A5-CONTRACT-PRIMARY-PASS"
    independent_verdict = "R475-A5-CONTRACT-INDEPENDENT-PASS"
    hostile_verdict = "R475-A5-CONTRACT-HOSTILE-PASS"
    add("primary subprocess", primary_process.returncode == 0, primary_process.returncode, 0)
    add("independent subprocess", independent_process.returncode == 0, independent_process.returncode, 0)
    add("hostile subprocess", hostile_process.returncode == 0, hostile_process.returncode, 0)
    add("primary verdict", primary.get("verdict") == primary_verdict, primary.get("verdict"), primary_verdict)
    add("independent verdict", independent.get("verdict") == independent_verdict, independent.get("verdict"), independent_verdict)
    add("hostile verdict", hostile.get("verdict") == hostile_verdict, hostile.get("verdict"), hostile_verdict)

    primary_total = int(primary.get("assertion_summary", {}).get("total", 0))
    independent_total = int(independent.get("assertion_summary", {}).get("total", 0))
    hostile_total = int(hostile.get("assertion_summary", {}).get("total", 0))
    oracles = manifest.get("test_oracles", {})
    add("primary assertion minimum", primary_total >= int(oracles.get("primary_minimum_assertions", 0)), primary_total, oracles.get("primary_minimum_assertions"))
    add("independent assertion minimum", independent_total >= int(oracles.get("independent_minimum_assertions", 0)), independent_total, oracles.get("independent_minimum_assertions"))
    add("hostile assertion total", hostile_total == int(oracles.get("hostile_check_count", 0)), hostile_total, oracles.get("hostile_check_count"))
    add(
        "all hostile mutations rejected",
        hostile.get("assertion_summary", {}).get("mutations_rejected") == int(oracles.get("hostile_mutation_count", 0))
        and all(row.get("status") == "PASS" for row in hostile.get("checks", [])[1:]),
        hostile.get("assertion_summary"),
        {"mutations_rejected": oracles.get("hostile_mutation_count"), "all": True},
    )
    contract_digests = [primary.get("theorem_contract_sha256"), independent.get("theorem_contract_sha256"), manifest.get("contract", {}).get("theorem_contract_sha256")]
    add("primary independent contract parity", contract_digests[0] == contract_digests[1] == contract_digests[2], contract_digests, "one source-derived theorem contract digest")
    add(
        "primary and independent method boundary",
        all(any(token in str(item).lower() for token in ("analytic", "physical", "continuum")) for item in (primary.get("non_claims", [])))
        and primary.get("evidence_level", "").startswith("T0")
        and independent.get("evidence_level", "").startswith("T0"),
        {"primary_level": primary.get("evidence_level"), "independent_level": independent.get("evidence_level")},
        "T0 non-claim boundary",
    )

    lean = run_lean()
    add("Lean compile", lean.get("status") == "PASS", lean, "PASS")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    verdict = "R475-A5-CONTRACT-INTEGRATED-PASS" if passed == total else "R475-A5-CONTRACT-INTEGRATED-FAIL"
    payload = {
        "schema": "tect/a5-r475-lean-crosscheck-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest.get("audit_id"),
        "claim_id": manifest.get("claim_id"),
        "result_id": manifest.get("result_id"),
        "exploration_id": manifest.get("exploration_id"),
        "script_version": __version__,
        "verdict": verdict,
        "tier": manifest.get("tier"),
        "claim_bearing": manifest.get("claim_bearing"),
        "assertion_summary": {"passed": passed, "total": total, "primary": primary_total, "independent": independent_total, "hostile": hostile_total},
        "assertions": rows,
        "children": {
            "primary": {"returncode": primary_process.returncode, "stdout": primary_process.stdout, "stderr": primary_process.stderr, "verdict": primary.get("verdict"), "assertions": primary.get("assertion_summary")},
            "independent": {"returncode": independent_process.returncode, "stdout": independent_process.stdout, "stderr": independent_process.stderr, "verdict": independent.get("verdict"), "assertions": independent.get("assertion_summary")},
            "hostile": {"returncode": hostile_process.returncode, "stdout": hostile_process.stdout, "stderr": hostile_process.stderr, "verdict": hostile.get("verdict"), "assertions": hostile.get("assertion_summary")},
        },
        "lean": lean,
        "scope": manifest.get("scope"),
        "assumptions": manifest.get("assumptions"),
        "missing_assumptions": manifest.get("missing_assumptions"),
        "non_claims": manifest.get("non_claims"),
        "falsifiers": manifest.get("falsifiers"),
        "evidence_level": manifest.get("evidence_level"),
        "boundary": manifest.get("boundary"),
        "methods_unchanged": all(value is True for value in preservation.values()),
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "manifest_sha256": sha256(MANIFEST),
            "a5_manifest_sha256": sha256(REPO / "claims" / "A5-SECTOR-A-SYNTHESIS" / "conditional_composition_manifest.json"),
            "primary_sha256": sha256(PRIMARY),
            "independent_sha256": sha256(INDEPENDENT),
            "hostile_sha256": sha256(HOSTILE),
            "lean_sha256": sha256(LEAN, normalise=True),
            "registry_sha256": sha256(REPO / "verification" / "lean" / "registry.json"),
        },
        "failures": [row["name"] for row in rows if row["status"] != "PASS"],
    }
    output = args.output if args.output.is_absolute() else REPO / args.output
    atomic_json(output, payload)
    print(f"R-475 INTEGRATED: {verdict} ({passed}/{total}; primary={primary_total}, independent={independent_total}, hostile={hostile_total}, Lean={lean.get('status')})")
    print("Evidence:", output.resolve())
    return 0 if verdict.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
