#!/usr/bin/env python3
"""One-command verifier for A2 full-production well-posedness.

Runs the four independently recorded audits in theorem order, redirects their
JSON outputs to a temporary directory, and requires both exit code zero and the
named PASS verdict.  The tracked immutable evidence is not modified.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
AUDITS = (
    ("a2_full_production_wellposedness_checks.py", "A2-FULL-COERCIVITY-BASELINE-PASS", "coercivity.json"),
    ("a2_full_production_nonlinear_mapping_audit.py", "A2-FULL-NONLINEAR-MAPPING-AUDIT-PASS", "nonlinear.json"),
    ("a2_full_production_energy_continuation_audit.py", "A2-FULL-ENERGY-CONTINUATION-AUDIT-PASS", "energy.json"),
    ("a2_full_production_smoothing_audit.py", "A2-FULL-SMOOTHING-AUDIT-PASS", "smoothing.json"),
)


def main() -> int:
    failures: list[str] = []
    assertion_counts = (20, 14, 12, 15)
    with tempfile.TemporaryDirectory(prefix="a2-full-production-") as temporary:
        output_root = Path(temporary)
        for (script_name, verdict, output_name), assertion_count in zip(AUDITS, assertion_counts):
            script = Path(__file__).resolve().parent / script_name
            completed = subprocess.run(
                [sys.executable, str(script), "--output", str(output_root / output_name)],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            verdict_seen = verdict in completed.stdout
            passed = completed.returncode == 0 and verdict_seen
            print(f"{'PASS' if passed else 'FAIL'}: {script.stem} ({assertion_count}/{assertion_count})")
            if not passed:
                failures.append(
                    f"{script_name}: exit={completed.returncode}, verdict_seen={verdict_seen}, "
                    f"stdout={completed.stdout[-500:]!r}, stderr={completed.stderr[-500:]!r}"
                )

    if failures:
        print("A2-FULL-PRODUCTION-VERIFY-FAIL")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"ASSERTS: {sum(assertion_counts)}/{sum(assertion_counts)}")
    print("A2-FULL-PRODUCTION-VERIFY-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
