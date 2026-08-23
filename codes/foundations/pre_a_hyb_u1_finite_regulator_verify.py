#!/usr/bin/env python3
"""Integrated fresh audit for HYB-TECT-U1-FINITE-0001."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-finite-regulator-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / "pre_a_hyb_u1_finite_regulator.py"
INDEPENDENT = REPO / "codes" / "foundations" / "pre_a_hyb_u1_finite_regulator_independent.py"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-hyb-u1-finite-regulator" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def load_result(path: Path, expected: str) -> tuple[bool, dict[str, Any], str]:
    if not path.is_file():
        return False, {}, "missing result"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, {}, f"invalid JSON: {exc}"
    summary = data.get("assertion_summary", {})
    ok = data.get("verdict") == expected and summary.get("total", 0) > 0 and summary.get("passed") == summary.get("total")
    return ok, data, "" if ok else f"verdict={data.get('verdict')}; summary={summary}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_reports = []
    for key, path in (("primary", PRIMARY), ("independent", INDEPENDENT), ("verifier", Path(__file__).resolve())):
        actual = sha256(path)
        expected = manifest["files"][key]["sha256"]
        source_reports.append({"authority": key, "path": str(path.relative_to(REPO)), "actual_sha256": actual, "expected_sha256": expected, "passed": actual == expected})

    failures: list[str] = []
    reports: list[dict[str, Any]] = []
    total = 0
    passed = 0
    with tempfile.TemporaryDirectory(prefix="hyb-u1-") as temp:
        root = Path(temp)
        primary_out = root / "primary.json"
        independent_out = root / "independent.json"
        p_run = subprocess.run([sys.executable, str(PRIMARY), "--output", str(primary_out)], cwd=REPO, text=True, capture_output=True, check=False)
        p_ok, p_data, p_detail = load_result(primary_out, "HYB-TECT-U1-FINITE-PRIMARY-PASS")
        p_ok = p_ok and p_run.returncode == 0
        p_summary = p_data.get("assertion_summary", {})
        total += int(p_summary.get("total", 0))
        passed += int(p_summary.get("passed", 0))
        reports.append({"lane": "primary", "returncode": p_run.returncode, "summary": p_summary, "passed": p_ok})
        if not p_ok:
            failures.append(f"primary: {p_detail}; stderr={p_run.stderr[-500:]!r}")
        i_run = subprocess.run([sys.executable, str(INDEPENDENT), "--primary-result", str(primary_out), "--output", str(independent_out)], cwd=REPO, text=True, capture_output=True, check=False)
        i_ok, i_data, i_detail = load_result(independent_out, "HYB-TECT-U1-FINITE-INDEPENDENT-PASS")
        i_ok = i_ok and i_run.returncode == 0
        i_summary = i_data.get("assertion_summary", {})
        total += int(i_summary.get("total", 0))
        passed += int(i_summary.get("passed", 0))
        reports.append({"lane": "independent", "returncode": i_run.returncode, "summary": i_summary, "passed": i_ok})
        if not i_ok:
            failures.append(f"independent: {i_detail}; stderr={i_run.stderr[-500:]!r}")

    if not all(row["passed"] for row in source_reports):
        failures.append("authority source hash mismatch")
    p_cross = p_data.get("r192_crosswalk", {})
    i_cross = i_data.get("r192_crosswalk", {})
    cross_agreement = p_cross == i_cross and p_cross.get("first_missing_slot") == "heat_root_incidence" and p_cross.get("production_owner") is False
    if not cross_agreement:
        failures.append("primary and independent R-192 crosswalks disagree")
    required_absent = ("heat_root_incidence", "root_filtration", "conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")
    if not all(p_cross.get(field) is False for field in required_absent):
        failures.append("R-192 missing owner slots were promoted")
    all_passed = not failures and all(row["passed"] for row in reports)
    verdict = "HYB-TECT-U1-FINITE-INTEGRATED-PASS" if all_passed else "HYB-TECT-U1-FINITE-INTEGRATED-FAIL"
    payload = {
        "schema": "tect/pre-a-hyb-u1-finite-regulator-integrated/1.0",
        "script_version": __version__,
        "audit_id": manifest["audit_id"],
        "candidate_id": manifest["candidate_id"],
        "verdict": verdict,
        "source_reports": source_reports,
        "lane_reports": reports,
        "cross_audit": {"r192_agreement": cross_agreement, "all_missing_slots_absent": all(p_cross.get(field) is False for field in required_absent)},
        "assertion_summary": {"passed": passed, "total": total},
        "failures": failures,
        "gate_results": manifest["selection"],
        "boundary": manifest["boundary"],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY: {reports[0]['summary'].get('passed', 0)}/{reports[0]['summary'].get('total', 0)}")
    print(f"INDEPENDENT: {reports[1]['summary'].get('passed', 0)}/{reports[1]['summary'].get('total', 0)}")
    print(f"ASSERTS: {passed}/{total}")
    print(verdict)
    print("R-192 first missing:", p_cross.get("first_missing_slot"))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
