#!/usr/bin/env python3
"""One-command verifier for the A4 scalar constructive-measure package.

The verifier re-executes the primary analytic audit and then gives its fresh
temporary artifact to a non-importing independent audit.  It also validates
all three source hashes against the frozen manifest.  Only the final integrated
JSON is written to the repository; intermediate evidence remains temporary.
"""

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

__version__ = "1.2.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "constructive_measure_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-19-referee-preflight-v2.1" / "result.json"

AUDITS = (
    {
        "authority": "primary_audit",
        "expected_verdict": "A4-SCALAR-CONSTRUCTIVE-PRIMARY-PASS",
        "output_name": "primary.json",
    },
    {
        "authority": "independent_audit",
        "expected_verdict": "A4-SCALAR-CONSTRUCTIVE-INDEPENDENT-PASS",
        "output_name": "independent.json",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_audit(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO, text=True, capture_output=True, check=False)


def validate_result(path: Path, expected_verdict: str) -> tuple[bool, dict[str, Any], str]:
    if not path.exists():
        return False, {}, "result JSON was not created"
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, {}, f"invalid result JSON: {error}"
    summary = result.get("assertion_summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", -1))
    ok = result.get("verdict") == expected_verdict and total > 0 and passed == total
    return ok, result, "" if ok else f"verdict={result.get('verdict')}; assertions={summary}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    verifier_expected = authority["one_command_verifier"]["sha256"]
    source_reports = []
    for key in ("primary_audit", "independent_audit", "one_command_verifier"):
        path = REPO / authority[key]["path"]
        actual = sha256(path)
        source_reports.append(
            {
                "authority": key,
                "path": authority[key]["path"],
                "actual_sha256": actual,
                "expected_sha256": authority[key]["sha256"],
                "passed": actual == authority[key]["sha256"],
            }
        )

    reports: list[dict[str, Any]] = []
    failures: list[str] = []
    assertion_total = 0
    assertion_passed = 0
    with tempfile.TemporaryDirectory(prefix="a4-constructive-") as temporary:
        output_root = Path(temporary)
        primary_spec = AUDITS[0]
        primary_path = output_root / primary_spec["output_name"]
        primary_source = REPO / authority[primary_spec["authority"]]["path"]
        primary_run = run_audit([sys.executable, str(primary_source), "--output", str(primary_path)])
        primary_ok, primary_result, primary_detail = validate_result(primary_path, primary_spec["expected_verdict"])
        primary_ok = primary_ok and primary_run.returncode == 0
        primary_summary = primary_result.get("assertion_summary", {})
        assertion_total += int(primary_summary.get("total", 0))
        assertion_passed += int(primary_summary.get("passed", 0))
        reports.append(
            {
                "audit": primary_spec["authority"],
                "mode": "fresh temporary re-execution",
                "returncode": primary_run.returncode,
                "expected_verdict": primary_spec["expected_verdict"],
                "actual_verdict": primary_result.get("verdict"),
                "assertions": primary_summary,
                "passed": primary_ok,
            }
        )
        print(f"{'PASS' if primary_ok else 'FAIL'}: primary ({primary_summary.get('passed', 0)}/{primary_summary.get('total', 0)})")
        if not primary_ok:
            failures.append(f"primary: {primary_detail}; exit={primary_run.returncode}; stderr={primary_run.stderr[-500:]!r}")

        independent_spec = AUDITS[1]
        independent_path = output_root / independent_spec["output_name"]
        independent_source = REPO / authority[independent_spec["authority"]]["path"]
        independent_run = run_audit(
            [
                sys.executable,
                str(independent_source),
                "--primary-result",
                str(primary_path),
                "--output",
                str(independent_path),
            ]
        )
        independent_ok, independent_result, independent_detail = validate_result(independent_path, independent_spec["expected_verdict"])
        independent_ok = independent_ok and independent_run.returncode == 0 and primary_ok
        independent_summary = independent_result.get("assertion_summary", {})
        assertion_total += int(independent_summary.get("total", 0))
        assertion_passed += int(independent_summary.get("passed", 0))
        reports.append(
            {
                "audit": independent_spec["authority"],
                "mode": "fresh non-importing temporary re-execution",
                "returncode": independent_run.returncode,
                "expected_verdict": independent_spec["expected_verdict"],
                "actual_verdict": independent_result.get("verdict"),
                "assertions": independent_summary,
                "passed": independent_ok,
            }
        )
        print(f"{'PASS' if independent_ok else 'FAIL'}: independent ({independent_summary.get('passed', 0)}/{independent_summary.get('total', 0)})")
        if not independent_ok:
            failures.append(f"independent: {independent_detail}; exit={independent_run.returncode}; stderr={independent_run.stderr[-500:]!r}")

    source_hashes_ok = all(row["passed"] for row in source_reports)
    if not source_hashes_ok:
        failures.append("one or more source hashes do not match the manifest")
    if sha256(Path(__file__)) != verifier_expected:
        failures.append("verifier self-hash does not match the manifest")
    passed = not failures and all(report["passed"] for report in reports)
    verdict = "A4-SCALAR-CONSTRUCTIVE-INTEGRATED-PASS" if passed else "A4-SCALAR-CONSTRUCTIVE-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a4-scalar-constructive-integrated-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "scope": "fresh primary and non-importing independent reconstruction of the finite-volume real-scalar spectral constructive measure",
        "source_reports": source_reports,
        "audit_reports": reports,
        "assertion_summary": {"passed": assertion_passed, "total": assertion_total},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "failures": failures,
        "promotion_boundary": "T6 conditional theorem enacted after independent operator reproduction on 2026-07-18; this verifier does not authorize T7 or any excluded scope",
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"ASSERTS: {assertion_passed}/{assertion_total}")
    print(verdict)
    print("Evidence:", args.output.resolve())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
