#!/usr/bin/env python3
"""Run the PAH-OMC-030 primary, independent and hostile audits together."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc030-bridge"
COMMANDS = [
    ("primary", ROOT / "verification/scripts/pah_omc030_verify.py", RUN_DIR / "primary.json"),
    ("independent", ROOT / "codes/foundations/pah_omc030_independent.py", RUN_DIR / "independent.json"),
    ("hostile", ROOT / "codes/foundations/pah_omc030_hostile.py", RUN_DIR / "hostile.json")
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=RUN_DIR / "integrated.json")
    args = parser.parse_args()
    runs = {}
    failures = []
    for name, script, output in COMMANDS:
        proc = subprocess.run([sys.executable, "-X", "utf8", str(script), "--check", "--output", str(output)], cwd=ROOT, text=True, capture_output=True)
        runs[name] = {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
        if proc.returncode != 0:
            failures.append(name)
    payload = {
        "schema": "tect/pah-omc030-integrated/1.0",
        "status": "PASS" if not failures else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "commands": {name: f"python -X utf8 {script.relative_to(ROOT)} --check" for name, script, _ in COMMANDS},
        "runs": runs,
        "failures": failures,
        "non_claims": ["No finite-to-target convergence", "No physical Pre-A/QFT/gravity/continuum/Yang-Mills/mass-gap/TOE conclusion"]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PAH-OMC-030 INTEGRATED: {payload['status']}; verdict=HOLD_FOR_EVIDENCE")
    return 0 if args.check and payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
