#!/usr/bin/env python3
"""verify_claim.py -- one-command claim reproduction entrypoint.

Usage:
    python verification/scripts/verify_claim.py --claim A2-PDE-WELLPOSED
    python verification/scripts/verify_claim.py --claim A2-PDE-WELLPOSED --dry-run

The claim card remains the source of truth. This wrapper reads
`claims/<ID>/status.json`, executes its `reproduction.command`, and returns the
same success/failure status as the underlying verifier.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_claim(claim_id):
    path = REPO / "claims" / claim_id / "status.json"
    if not path.exists():
        raise SystemExit(f"VERIFY-CLAIM: FAIL -- unknown claim {claim_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _command_tokens(command):
    tokens = shlex.split(command, posix=False)
    if not tokens:
        raise SystemExit("VERIFY-CLAIM: FAIL -- empty reproduction.command")
    if tokens[0].lower() in {"python", "python3", "py"}:
        tokens[0] = sys.executable
    return tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", required=True, help="claim ID, e.g. A2-PDE-WELLPOSED")
    parser.add_argument("--dry-run", action="store_true", help="print the command but do not execute it")
    args = parser.parse_args()

    card = _load_claim(args.claim)
    reproduction = card.get("reproduction", {})
    if reproduction.get("status") != "AVAILABLE":
        print(f"VERIFY-CLAIM: FAIL -- {args.claim} reproduction.status is {reproduction.get('status')!r}")
        return 1

    command = reproduction.get("command", "").strip()
    tokens = _command_tokens(command)
    print(f"VERIFY-CLAIM: {args.claim}")
    print(f"  tier: {card.get('tier')}  lifecycle: {card.get('lifecycle')}")
    print(f"  command: {command}")
    print(f"  expected: {reproduction.get('expected', '')}")
    if args.dry_run:
        print("VERIFY-CLAIM: DRY-RUN")
        return 0

    result = subprocess.run(tokens, cwd=REPO)
    if result.returncode == 0:
        print(f"VERIFY-CLAIM: PASS -- {args.claim}")
    else:
        print(f"VERIFY-CLAIM: FAIL -- {args.claim} exited {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
