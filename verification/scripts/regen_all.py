#!/usr/bin/env python3
"""regen_all.py -- regenerate every generated surface from its source, in
dependency order (build_catalog LAST). One command to clear all staleness.

    python verification/scripts/regen_all.py [--check]

--check runs release_check.py afterwards (exit code propagated).
Gate/order source: gates.py (shared with doctor.py + release_check.py).
"""
__version__ = "1.0.0"

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]
from gates import REGEN_ORDER


def main() -> int:
    for args in REGEN_ORDER:
        print(f"  regen: {' '.join(args)}")
        r = subprocess.run([sys.executable, str(SCRIPTS / args[0])] + args[1:], cwd=str(REPO))
        if r.returncode != 0:
            print(f"REGEN-ALL: FAIL at {args[0]} (rc={r.returncode})")
            return 1
    print("REGEN-ALL: all generated surfaces refreshed")
    if "--check" in sys.argv[1:]:
        return subprocess.run([sys.executable, str(SCRIPTS / "release_check.py")], cwd=str(REPO)).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
