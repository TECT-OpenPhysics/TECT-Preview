#!/usr/bin/env python3
"""Current-tree revalidation of the historical A1 Class-II owner mismatch.

The historical R-172 wrapper pins an old aggregate catalog count.  This
reader revalidation runs the unchanged primary and independent mismatch lanes
against a current-tree output directory, derives current counts from their
authorities, and keeps the old wrapper's stale-count failure separate from the
mathematical coefficient result.  It is T0 and claim-nonbearing.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a-a1-classii-owner-mismatch-current-revalidation-manifest.json"
PRIMARY = ROOT / "verification" / "scripts" / "lean_a1_classii_owner_mismatch_crosscheck.py"
INDEPENDENT = ROOT / "codes" / "foundations" / "a1_classii_owner_mismatch_crosscheck_independent.py"
HISTORICAL_MANIFEST = ROOT / "strategy" / "pre-a-a1-classii-owner-mismatch-lean-crosscheck-manifest.json"
DEFAULT_RUN = ROOT / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "runs" / "2026-08-24-current-a1-classii-owner-mismatch"
DEFAULT_OUTPUT = DEFAULT_RUN / "integrated.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        temporary_path = Path(temporary)
        if temporary_path.exists():
            temporary_path.unlink()


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    text = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed ({completed.returncode}): {text}")
    return json.loads(output.read_text(encoding="utf-8")), text


def current_counts() -> dict[str, int]:
    catalog = json.loads((ROOT / "verification" / "catalog-summary.json").read_text(encoding="utf-8"))
    explorations = [json.loads(line) for line in (ROOT / "explorations" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    events = [json.loads(line) for line in (ROOT / "changelog" / "log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    result_text = (ROOT / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    tasks = json.loads((ROOT / "todo" / "todo.json").read_text(encoding="utf-8"))
    return {
        "catalog": int(catalog["total"]),
        "explorations": len(explorations),
        "events": len(events),
        "results": len(re.findall(r"^### R-\d+\b", result_text, re.MULTILINE)),
        "tasks": len(tasks.get("tasks", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A1-CLASSII-OWNER-MISMATCH-CURRENT-REVALIDATION", manifest["audit_id"], "A1-CLASSII-OWNER-MISMATCH-CURRENT-REVALIDATION")
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", manifest["claim_bearing"], False)
    for key, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    check("primary AST", ast.parse(PRIMARY.read_text(encoding="utf-8")) is not None, True, True)
    check("independent AST", ast.parse(INDEPENDENT.read_text(encoding="utf-8")) is not None, True, True)
    check("independent stdlib-only", manifest["independent_stdlib_only"] is True, manifest["independent_stdlib_only"], True)

    primary_path = DEFAULT_RUN / "primary.json"
    independent_path = DEFAULT_RUN / "independent.json"
    primary, primary_output = run_child(PRIMARY, primary_path)
    independent, independent_output = run_child(INDEPENDENT, independent_path)
    check("primary PASS", primary.get("verdict") == "PASS", primary.get("verdict"), "PASS")
    check("independent PASS", independent.get("verdict") == "PASS", independent.get("verdict"), "PASS")
    p_derived = primary.get("derived", {})
    i_derived = independent.get("derived", {})
    shared = ["declared_numerator", "residual_numerator", "numerator_difference", "coefficients_are_not_equal", "mass_denominator_positive"]
    check("derived agreement", all(p_derived.get(key) == i_derived.get(key) for key in shared), {key: p_derived.get(key) for key in shared}, {key: i_derived.get(key) for key in shared})
    check("owner mismatch remains", p_derived.get("coefficients_are_not_equal") is True and p_derived.get("numerator_difference") != "0", p_derived, "nonzero exact mismatch")
    check("A1 obstruction is named", "A1-PFR-VARIATIONAL-MISMATCH" in (ROOT / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json").read_text(encoding="utf-8"), True, True)

    counts = current_counts()
    historical = json.loads(HISTORICAL_MANIFEST.read_text(encoding="utf-8"))
    historical_catalog = int(historical["formal_integration"]["expected_counts"]["catalog"])
    check("current counts are readable", all(value > 0 for value in counts.values()), counts, "positive current authority counts")
    check("historical wrapper stale count is isolated", historical_catalog != counts["catalog"], {"historical": historical_catalog, "current": counts["catalog"]}, "different counts require current reader")
    check("primary Lean lane", "LEAN PASS" in primary_output.upper(), primary_output, "LEAN PASS")
    check("independent Lean lane", "PASS" in independent_output.upper(), independent_output, "PASS")

    payload = {
        "schema": "tect/a1-classii-owner-mismatch-current-revalidation/1.0",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "run_kind": "integrated",
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": p_derived,
        "current_counts": counts,
        "historical_wrapper_catalog": historical_catalog,
        "children": {"primary": primary, "independent": independent},
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"CURRENT A1 CLASS-II OWNER MISMATCH REVALIDATION PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
