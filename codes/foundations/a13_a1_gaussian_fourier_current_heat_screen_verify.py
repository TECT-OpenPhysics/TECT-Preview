#!/usr/bin/env python3
"""Integrated cross-check for the A1 Gaussian Fourier heat proxy screen."""

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
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-gaussian-fourier-current-heat-screen-manifest.json"
PRIMARY = ROOT / "codes" / "foundations" / "a13_a1_gaussian_fourier_current_heat_screen.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a13_a1_gaussian_fourier_current_heat_screen_independent.py"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-a1-gaussian-fourier-current-heat-screen" / "result.json"


def add(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def child(script: Path, output: Path) -> tuple[int, dict[str, Any]]:
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
    with tempfile.TemporaryDirectory(prefix="a1_fourier_heat_screen_") as tmp:
        temp = Path(tmp)
        p_code, primary = child(PRIMARY, temp / "primary.json")
        i_code, independent = child(INDEPENDENT, temp / "independent.json")
    rows: list[dict[str, Any]] = []
    add(rows, "primary_exit_zero", p_code == 0, p_code, 0)
    add(rows, "independent_exit_zero", i_code == 0, i_code, 0)
    add(rows, "primary_failures_empty", primary.get("failures") == [], primary.get("failures"), [])
    add(rows, "independent_failures_empty", independent.get("failures") == [], independent.get("failures"), [])
    core_keys = ("dimension", "cutoffs", "heat_exponents", "current_factor", "finite_q_tables")
    primary_core = {key: primary.get("derived", {}).get(key) for key in core_keys}
    independent_core = {key: independent.get("derived", {}).get(key) for key in core_keys}
    add(rows, "derived_core_values_identical", primary_core == independent_core, [primary_core, independent_core], "identical")
    add(rows, "source_authorities_identical", primary.get("source_authorities") == independent.get("source_authorities"), [primary.get("source_authorities"), independent.get("source_authorities")], "identical")
    text = " ".join([str(primary.get("conclusion", "")), *[str(x) for x in primary.get("honesty_boundary", [])]])
    for token in ("proxy", "finite", "production", "q-ledger", "A13"):
        add(rows, f"scope_token_{token}", token.lower() in text.lower(), text, f"contains {token}")
    add(rows, "unweighted_growth_retained", any(row.get("name") == "unweighted_screen_strict_growth" and row.get("status") == "PASS" for row in primary.get("assertions", [])), primary.get("assertions"), "growth assertion")
    add(rows, "heat_order_retained", all(row.get("name", "").startswith("heat_order") and row.get("status") == "PASS" for row in independent.get("assertions", []) if row.get("name", "").startswith("heat_order")), independent.get("assertions"), "all heat-order assertions PASS")
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-gaussian-fourier-current-heat-screen-integrated-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Integrated finite diagonal-Gaussian A1 current proxy screen; not the production heat/root owner.",
        "primary_result": {k: v for k, v in primary.items() if not k.startswith("_")},
        "independent_result": {k: v for k, v in independent.items() if not k.startswith("_")},
        "cross_assertions": rows,
        "cross_assertion_count": len(rows),
        "assertion_count": len(rows) + int(primary.get("assertion_count", 0)) + int(independent.get("assertion_count", 0)),
        "conclusion": "The two exact lanes agree on the finite current convolution and heat-rate ordering. The result is a QFT-compatible UV screen only; the A1 production generator, filtration and cutoff-uniform q-ledger remain unprovided.",
        "honesty_boundary": ["no production heat/root owner", "no full raw-current intertwiner", "no cutoff-uniform q-ledger", "no A13 closure", "no Sector-A or Pre-A closure"],
        "failures": failures,
    }
    if not args.no_store:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 FOURIER HEAT INTEGRATED FAIL {len(rows)-len(failures)}/{len(rows)}")
        for failure in failures:
            print(f"FAIL {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"A1 FOURIER HEAT INTEGRATED PASS {len(rows)}/{len(rows)}")
    if not args.no_store:
        print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
