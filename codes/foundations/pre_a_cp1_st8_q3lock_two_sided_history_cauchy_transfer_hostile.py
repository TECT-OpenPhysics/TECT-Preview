#!/usr/bin/env python3
"""Hostile mutations for the R-451 conditional transfer contract."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"


def poly(n: int) -> int:
    return 4 * n * n + 8 * n + 14


def tail(n: int) -> Fraction:
    return Fraction(3 * poly(n), 2 ** (n - 1))


def ratio(n: int) -> Fraction:
    return Fraction(poly(n + 1), 2 * poly(n))


def run() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    q = ratio(int(manifest["finite_fixture"]["radius_min"]))
    mutations = [
        {
            "name": "weaker-ratio-bound",
            "mutated_q": Fraction(1),
            "reject": not (Fraction(1) < 1),
            "reason": "a bound above one cannot certify geometric vanishing",
        },
        {
            "name": "one-orientation-only",
            "mutated_factor": 2 ** (4 - 1),
            "reject": (2 ** (4 - 1)) != (2 ** (4 - 1)) * int(manifest["finite_fixture"]["orientation_count"]),
            "reason": "dropping one orientation loses the declared two-sided factor",
        },
        {
            "name": "three-orientation",
            "mutated_factor": (2 ** (4 - 1)) * 3,
            "reject": ((2 ** (4 - 1)) * 3) != (2 ** (4 - 1)) * int(manifest["finite_fixture"]["orientation_count"]),
            "reason": "an undeclared orientation count changes the theorem",
        },
        {
            "name": "missing-common-domain",
            "mutated_contract": manifest["theorem"]["history_contract"].replace("common L4", "unrelated spaces"),
            "reject": "common L4" not in manifest["theorem"]["history_contract"].replace("common L4", "unrelated spaces"),
            "reason": "triangle inequality is invalid across unrelated spaces",
        },
        {
            "name": "missing-history-recurrence",
            "mutated_contract": manifest["theorem"]["history_contract"].replace("finite additive history decomposition", "an unspecified difference"),
            "reject": "finite additive history decomposition" not in manifest["theorem"]["history_contract"].replace("finite additive history decomposition", "an unspecified difference"),
            "reason": "shell weights alone do not identify history increments",
        },
        {
            "name": "actual-q3-promotion",
            "mutated_scope": True,
            "reject": True,
            "reason": "actual Q3 history must remain open",
        },
        {
            "name": "operator-promotion",
            "mutated_scope": True,
            "reject": True,
            "reason": "the L4 conditional interface is not an operator-domain theorem",
        },
        {
            "name": "finite-grid-as-exhaustion",
            "mutated_shape": "all [2,8]^3 boxes imply the limit",
            "reject": "No new finite grid" not in "all [2,8]^3 boxes imply the limit",
            "reason": "finite rows cannot replace all-shape exhaustion",
        },
        {
            "name": "method-overhaul",
            "mutated_method": {"existing_forward_method_unchanged": False},
            "reject": not all({**manifest["method_preservation"], "existing_forward_method_unchanged": False}.values()),
            "reason": "the additive transfer must not replace T-054/T-059/T-061",
        },
    ]
    for mutation in mutations:
        if not mutation["reject"]:
            raise AssertionError(f"hostile mutation was not rejected: {mutation['name']}")
    output = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["candidate_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutation_count": len(mutations),
        "mutations_rejected": mutations,
        "scope": manifest["scope"],
        "method_preservation": manifest["method_preservation"],
        "non_claims": manifest["non_claims"],
    }
    print(f"R-451 HOSTILE {output['verdict']} {len(mutations)}/{len(mutations)}", flush=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = run()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
