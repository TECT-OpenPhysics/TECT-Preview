#!/usr/bin/env python3
"""One-command verifier for the branch-aware Sector-A synthesis review package.

The wrapper re-executes the primary audit and the non-importing independent
audit in a temporary directory, checks all three source hashes, and writes one
integrated JSON.  It deliberately does not publish or promote the package.
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

__version__ = "1.1.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "sector_a_synthesis_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-19-t5-integrated-preflight" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO, text=True, capture_output=True, check=False)


def load_result(path: Path, expected: str) -> tuple[bool, dict[str, Any], str]:
    if not path.is_file():
        return False, {}, "result JSON was not created"
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return False, {}, f"invalid result JSON: {error}"
    summary = result.get("assertion_summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", -1))
    ok = result.get("verdict") == expected and total > 0 and passed == total
    return ok, result, "" if ok else f"verdict={result.get('verdict')}; assertions={summary}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    source_reports = []
    for key in ("primary_audit", "independent_audit", "one_command_verifier"):
        source = REPO / authority[key]["path"]
        actual = sha256(source)
        source_reports.append(
            {
                "authority": key,
                "path": authority[key]["path"],
                "actual_sha256": actual,
                "expected_sha256": authority[key]["sha256"],
                "passed": actual == authority[key]["sha256"],
            }
        )

    failures: list[str] = []
    reports: list[dict[str, Any]] = []
    assertion_total = 0
    assertion_passed = 0
    primary_result: dict[str, Any] = {}
    independent_result: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="a5-sector-a-synthesis-") as temporary:
        root = Path(temporary)
        primary_output = root / "primary.json"
        primary_source = REPO / authority["primary_audit"]["path"]
        primary_run = run([sys.executable, str(primary_source), "--output", str(primary_output)])
        primary_ok, primary_result, primary_detail = load_result(primary_output, "A5-SECTOR-A-SYNTHESIS-PRIMARY-PASS")
        primary_ok = primary_ok and primary_run.returncode == 0
        primary_summary = primary_result.get("assertion_summary", {})
        assertion_total += int(primary_summary.get("total", 0))
        assertion_passed += int(primary_summary.get("passed", 0))
        reports.append(
            {
                "audit": "primary_audit",
                "mode": "fresh temporary re-execution",
                "returncode": primary_run.returncode,
                "expected_verdict": "A5-SECTOR-A-SYNTHESIS-PRIMARY-PASS",
                "actual_verdict": primary_result.get("verdict"),
                "assertions": primary_summary,
                "passed": primary_ok,
            }
        )
        print(f"{'PASS' if primary_ok else 'FAIL'}: primary ({primary_summary.get('passed', 0)}/{primary_summary.get('total', 0)})")
        if not primary_ok:
            failures.append(f"primary: {primary_detail}; exit={primary_run.returncode}; stderr={primary_run.stderr[-600:]!r}")

        independent_output = root / "independent.json"
        independent_source = REPO / authority["independent_audit"]["path"]
        independent_run = run(
            [
                sys.executable,
                str(independent_source),
                "--primary-result",
                str(primary_output),
                "--output",
                str(independent_output),
            ]
        )
        independent_ok, independent_result, independent_detail = load_result(
            independent_output, "A5-SECTOR-A-SYNTHESIS-INDEPENDENT-PASS"
        )
        independent_ok = independent_ok and independent_run.returncode == 0 and primary_ok
        independent_summary = independent_result.get("assertion_summary", {})
        assertion_total += int(independent_summary.get("total", 0))
        assertion_passed += int(independent_summary.get("passed", 0))
        reports.append(
            {
                "audit": "independent_audit",
                "mode": "fresh non-importing temporary re-execution",
                "returncode": independent_run.returncode,
                "expected_verdict": "A5-SECTOR-A-SYNTHESIS-INDEPENDENT-PASS",
                "actual_verdict": independent_result.get("verdict"),
                "assertions": independent_summary,
                "passed": independent_ok,
            }
        )
        print(f"{'PASS' if independent_ok else 'FAIL'}: independent ({independent_summary.get('passed', 0)}/{independent_summary.get('total', 0)})")
        if not independent_ok:
            failures.append(f"independent: {independent_detail}; exit={independent_run.returncode}; stderr={independent_run.stderr[-600:]!r}")

    if not all(row["passed"] for row in source_reports):
        failures.append("one or more source hashes do not match the frozen synthesis manifest")
    branch_agreement = (
        primary_result.get("termination_verdict", {}).get("result") == manifest["termination_verdict"]["result"]
        and independent_result.get("branch_map", {}).get("full_production") == manifest["branch_map"]["full_production"]
        and independent_result.get("branch_map", {}).get("scalar_continuum") == manifest["branch_map"]["scalar_continuum"]
    )
    if not branch_agreement:
        failures.append("primary/independent branch or termination records disagree with the manifest")
    mass_agreement = False
    try:
        primary_bridge = primary_result["parameter_bridge"]
        independent_fork = independent_result["mass_fork"]
        mass_agreement = (
            abs(float(primary_bridge["scalar_mass_squared"]) - float(independent_fork["scalar_mass_squared"])) < 1.0e-15
            and abs(float(primary_bridge["full_mass_squared"]) - float(independent_fork["full_mass_squared"])) < 1.0e-12
            and abs(float(primary_bridge["full_mass_squared"]) - float(primary_bridge["scalar_mass_squared"])) > 0.2
        )
    except (KeyError, TypeError, ValueError):
        mass_agreement = False
    if not mass_agreement:
        failures.append("primary and independent mass-fork reconstructions disagree")

    passed = not failures and all(row["passed"] for row in reports)
    verdict = "A5-SECTOR-A-SYNTHESIS-INTEGRATED-PASS" if passed else "A5-SECTOR-A-SYNTHESIS-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a5-sector-a-synthesis-integrated-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "scope": "fresh primary and non-importing independent audit of the branch-aware P1-P4 synthesis",
        "termination_verdict": manifest["termination_verdict"],
        "source_reports": source_reports,
        "audit_reports": reports,
        "cross_audit": {"branch_agreement": branch_agreement, "mass_fork_agreement": mass_agreement},
        "assertion_summary": {"passed": assertion_passed, "total": assertion_total},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "failures": failures,
        "promotion_boundary": "T5 CLOSED@BRANCH-AWARE-SECTOR-A-SYNTHESIS after operator confirmation; capstone PUBLISHED packaging remains deferred until the A4 support bundle is PUBLISHED",
        "not_closed_here": manifest["honesty_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"ASSERTS: {assertion_passed}/{assertion_total}")
    print(verdict)
    print("Termination:", manifest["termination_verdict"]["result"])
    print("Evidence:", args.output.resolve())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
