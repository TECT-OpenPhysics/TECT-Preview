#!/usr/bin/env python3
"""One-command verifier for the A5 T6 conditional-composition candidate.

Both audits are freshly executed in a temporary directory.  Promotion is not
automatic: a PASS establishes referee-package readiness, while exact-package
operator confirmation remains the publication gate.
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
__first_issued__ = "2026-07-19"
__version_issued__ = "2026-07-20"
__claims__ = ["A5-SECTOR-A-SYNTHESIS"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "conditional_composition_manifest.json"


# Path-hygiene compatibility: compact legacy aliases resolve to canonical roots.
PATH_ALIASES = (
    ("claims/a5/bundle/a5t5", "claims/A5-SECTOR-A-SYNTHESIS/bundle/a5t5"),
    ("claims/a5/bundle/a5t6", "claims/A5-SECTOR-A-SYNTHESIS/bundle/a5t6"),
    ("claims/a1k/bundle/b-a1n", "claims/A1-PRODUCTION-KERNEL-MANIFEST/bundle/A1-N001-Manifest-T5-260716"),
    ("claims/a1f/bundle/b-a1f", "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/bundle/A1-Production-Functional-T5-260717"),
    ("claims/a2/bundle/b-a2", "claims/A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717"),
    ("claims/a3f/bundle/b-a3f", "claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM/bundle/A3-Full-Production-Discretization-T6-Repair-260717"),
    ("claims/a3p/bundle/b-a3p", "claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/bundle/A3-Perturbative-Continuum-T6-260719"),
    ("claims/a4/bundle/b-a4", "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/bundle/A4-Scalar-Constructive-T6-260719"),
    ("claims/a1k", "claims/A1-PRODUCTION-KERNEL-MANIFEST"),
    ("claims/a1f", "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION"),
    ("claims/a2", "claims/A2-FULL-PRODUCTION-WELLPOSED"),
    ("claims/a3f", "claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"),
    ("claims/a3p", "claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS"),
    ("claims/a4", "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"),
    ("claims/a5", "claims/A5-SECTOR-A-SYNTHESIS"),
)

def resolve_repo_path(value: str) -> Path:
    for alias, canonical in sorted(PATH_ALIASES, key=lambda row: -len(row[0])):
        if value == alias or value.startswith(alias + "/"):
            return REPO / (canonical + value[len(alias):])
    return REPO / value
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-20-t6-conditional-published-integrated" / "result.json"


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
        source = resolve_repo_path(authority[key]["path"])
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
    with tempfile.TemporaryDirectory(prefix="a5-t6-conditional-") as temporary:
        root = Path(temporary)
        primary_output = root / "primary.json"
        primary_source = resolve_repo_path(authority["primary_audit"]["path"])
        primary_run = run([sys.executable, str(primary_source), "--output", str(primary_output)])
        primary_ok, primary_result, primary_detail = load_result(primary_output, "A5-T6-CONDITIONAL-PRIMARY-PASS")
        primary_ok = primary_ok and primary_run.returncode == 0
        primary_summary = primary_result.get("assertion_summary", {})
        assertion_total += int(primary_summary.get("total", 0))
        assertion_passed += int(primary_summary.get("passed", 0))
        reports.append(
            {
                "audit": "primary_audit",
                "mode": "fresh temporary re-execution",
                "returncode": primary_run.returncode,
                "expected_verdict": "A5-T6-CONDITIONAL-PRIMARY-PASS",
                "actual_verdict": primary_result.get("verdict"),
                "assertions": primary_summary,
                "passed": primary_ok,
            }
        )
        print(f"{'PASS' if primary_ok else 'FAIL'}: primary ({primary_summary.get('passed', 0)}/{primary_summary.get('total', 0)})")
        if not primary_ok:
            failures.append(f"primary: {primary_detail}; exit={primary_run.returncode}; stderr={primary_run.stderr[-800:]!r}")

        independent_output = root / "independent.json"
        independent_source = resolve_repo_path(authority["independent_audit"]["path"])
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
            independent_output, "A5-T6-CONDITIONAL-INDEPENDENT-PASS"
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
                "expected_verdict": "A5-T6-CONDITIONAL-INDEPENDENT-PASS",
                "actual_verdict": independent_result.get("verdict"),
                "assertions": independent_summary,
                "passed": independent_ok,
            }
        )
        print(f"{'PASS' if independent_ok else 'FAIL'}: independent ({independent_summary.get('passed', 0)}/{independent_summary.get('total', 0)})")
        if not independent_ok:
            failures.append(
                f"independent: {independent_detail}; exit={independent_run.returncode}; stderr={independent_run.stderr[-800:]!r}"
            )

    if not all(row["passed"] for row in source_reports):
        failures.append("one or more source hashes disagree with the conditional-composition manifest")
    agreement_fields = [
        "theorem_contract_sha256",
        "hypotheses",
        "branches",
        "mass_fork",
        "immutable_t5_bundle_digest",
    ]
    agreement = {field: primary_result.get(field) == independent_result.get(field) for field in agreement_fields}
    if not all(agreement.values()):
        failures.append("primary and independent audits disagree on one or more theorem-contract fields")

    passed = not failures and all(row["passed"] for row in reports)
    verdict = "A5-T6-CONDITIONAL-COMPOSITION-INTEGRATED-PASS" if passed else "A5-T6-CONDITIONAL-COMPOSITION-INTEGRATED-FAIL"
    output = {
        "schema": "tect/a5-t6-conditional-integrated-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "candidate_result": manifest["candidate_result"],
        "publication_state": manifest["publication_state"],
        "source_reports": source_reports,
        "audit_reports": reports,
        "cross_audit_agreement": agreement,
        "theorem_contract_sha256": primary_result.get("theorem_contract_sha256"),
        "hypotheses": primary_result.get("hypotheses"),
        "branches": primary_result.get("branches"),
        "mass_fork": primary_result.get("mass_fork"),
        "immutable_t5_bundle_digest": primary_result.get("immutable_t5_bundle_digest"),
        "assertion_summary": {"passed": assertion_passed, "total": assertion_total},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "failures": failures,
        "promotion_boundary": "Exact v1.0 is operator-confirmed. PASS verifies the enacted T6 contract; publication completeness additionally requires the bundle-last PUBLISHED package and final integrity gate.",
        "next_required_action": "Build or verify the PUBLISHED T6 bundle last, then synchronize the public ledgers and release gate.",
        "not_closed_here": manifest["theorem_contract"]["exclusions"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"ASSERTS: {assertion_passed}/{assertion_total}")
    print(verdict)
    print("Publication:", manifest["publication_state"])
    print("Evidence:", args.output.resolve())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
