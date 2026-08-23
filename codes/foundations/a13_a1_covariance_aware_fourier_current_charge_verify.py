#!/usr/bin/env python3
"""Integrated verifier for the finite covariance-aware current charge screen."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-covariance-aware-fourier-current-charge-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a13_a1_covariance_aware_fourier_current_charge.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a13_a1_covariance_aware_fourier_current_charge_independent.py"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-covariance-aware-fourier-current-charge" / "result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_child(script: Path, output: Path) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    payload["_stdout"] = proc.stdout
    payload["_stderr"] = proc.stderr
    return proc.returncode, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def mark(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    with tempfile.TemporaryDirectory(prefix="covariance_fourier_charge_") as temp_name:
        temp = Path(temp_name)
        p_code, primary = run_child(PRIMARY, temp / "primary.json")
        i_code, independent = run_child(INDEPENDENT, temp / "independent.json")
    mark("primary_exit_zero", p_code == 0, p_code, 0)
    mark("independent_exit_zero", i_code == 0, i_code, 0)
    mark("primary_failures_empty", primary.get("failures") == [], primary.get("failures"), [])
    mark("independent_failures_empty", independent.get("failures") == [], independent.get("failures"), [])
    mark("derived_core_agreement", primary.get("derived") == independent.get("derived"), [primary.get("derived"), independent.get("derived")], "identical")
    mark("source_hash_agreement", primary.get("source_authorities") == independent.get("source_authorities"), [primary.get("source_authorities"), independent.get("source_authorities")], "identical")
    mark("hostile_mutation_contract", len(manifest.get("hostile_mutations", [])) == int(manifest["contract"]["hostile_mutation_count"]), len(manifest.get("hostile_mutations", [])), manifest["contract"]["hostile_mutation_count"])
    mark("boundary_not_production", "no a1 production" in " ".join(str(v) for v in primary.get("honesty_boundary", [])).lower(), primary.get("honesty_boundary"), "no A1 production owner")
    mark("r201_source_hash", sha(ROOT / manifest["source_authorities"]["lean_r201"]["path"]) == manifest["source_authorities"]["lean_r201"]["sha256"], manifest["source_authorities"]["lean_r201"]["sha256"], "registered Lean hash")
    try:
        ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
        static_ok = "a13_a1_covariance_aware_fourier_current_charge" not in INDEPENDENT.read_text(encoding="utf-8")
    except SyntaxError:
        static_ok = False
    mark("independent_is_standalone", static_ok, str(INDEPENDENT), "no primary import")
    required_tokens = ("finite", "proxy", "no A1 production", "no A13")
    text = " ".join([str(primary.get("scope", "")), str(primary.get("conclusion", "")), *[str(v) for v in primary.get("honesty_boundary", [])]])
    mark("scope_tokens", all(token.lower() in text.lower() for token in required_tokens), text, required_tokens)
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-covariance-aware-fourier-current-charge-integrated-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Integrated exact finite covariance-aware QFT current proxy; no production heat/root owner.",
        "primary_result": {key: value for key, value in primary.items() if not key.startswith("_")},
        "independent_result": {key: value for key, value in independent.items() if not key.startswith("_")},
        "cross_assertions": rows,
        "cross_assertion_count": len(rows),
        "assertion_count": len(rows) + int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)),
        "conclusion": "The exact finite covariance-aware Fierz/heat formula is independently reproduced and Lean-pinned at fixture level. The missing A1 production mobility, root filtration, raw-current intertwiner and cutoff-uniform q-ledger remain open.",
        "honesty_boundary": ["finite QFT proxy", "Lean fixture cross-check only", "no A1 production heat/root owner", "no A13/T-050 closure", "no Sector-A/Pre-A/continuum/thermodynamic result"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 COVARIANCE FOURIER CHARGE INTEGRATED FAIL {len(rows)-len(failures)}/{len(rows)}")
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"A1 COVARIANCE FOURIER CHARGE INTEGRATED PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
