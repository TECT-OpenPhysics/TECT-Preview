#!/usr/bin/env python3
"""Integrated verifier for the A11/A13 coarse source-budget screen."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
PRIMARY = REPO / "codes" / "foundations" / "a11_a13_coarse_source_budget_screen.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a11_a13_coarse_source_budget_screen_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-coarse-source-budget-screen" / "result.json"


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def run_child(script: Path, output: Path) -> tuple[int, str, str, dict[str, Any]]:
    process = subprocess.run([sys.executable, str(script), "--output", str(output)], cwd=REPO, capture_output=True, text=True)
    payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    return process.returncode, process.stdout, process.stderr, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    with tempfile.TemporaryDirectory(prefix="a11_a13_coarse_screen_") as temp:
        temp_dir = Path(temp)
        p_code, p_out, p_err, primary = run_child(PRIMARY, temp_dir / "primary.json")
        i_code, i_out, i_err, independent = run_child(INDEPENDENT, temp_dir / "independent.json")
    rows: list[dict[str, Any]] = []
    add(rows, "primary_exit_zero", p_code == 0, p_code, 0)
    add(rows, "independent_exit_zero", i_code == 0, i_code, 0)
    add(rows, "primary_failures_empty", primary.get("failures") == [], primary.get("failures"), [])
    add(rows, "independent_failures_empty", independent.get("failures") == [], independent.get("failures"), [])
    add(rows, "derived_values_identical", primary.get("derived") == independent.get("derived"), [primary.get("derived"), independent.get("derived")], "identical")
    add(rows, "source_authorities_identical", primary.get("source_authorities") == independent.get("source_authorities"), [primary.get("source_authorities"), independent.get("source_authorities")], "identical")
    conclusion = str(primary.get("conclusion", ""))
    boundary = " ".join(str(x) for x in primary.get("honesty_boundary", []))
    for token in ("coarse", "exact-B", "joint", "not", "closure"):
        add(rows, f"scope_token_{token}", token.lower() in (conclusion + " " + boundary).lower(), conclusion + " " + boundary, f"contains {token}")
    add(rows, "registered_screen_fires", "registered_target_fails_coarse_envelope" in {r["name"] for r in primary.get("assertions", []) if r.get("status") == "PASS"}, primary.get("assertions"), "registered target failure asserted")
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/a11-a13-coarse-source-budget-screen-integrated-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Integrated cross-check of the coefficient-blind coarse source-budget screen; exact-B, joint, and production-valid routes remain open.",
        "primary_result": primary, "independent_result": independent, "child_stdout": {"primary": p_out, "independent": i_out}, "child_stderr": {"primary": p_err, "independent": i_err},
        "cross_assertions": rows, "cross_assertion_count": len(rows), "assertion_count": len(rows) + int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)),
        "conclusion": "The registered theta target fails the coefficient-blind coarse envelope. This is an exploration screen, not a theorem against exact-B, joint, or production-valid routes.",
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A11/A13 COARSE SCREEN INTEGRATED FAIL {len(rows)-len(failures)}/{len(rows)}")
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"A11/A13 COARSE SCREEN INTEGRATED PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
