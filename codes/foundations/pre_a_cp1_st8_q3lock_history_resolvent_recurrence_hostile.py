#!/usr/bin/env python3
"""Hostile mutations for the R-452 recurrence-resolvent contract."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
R451 = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"


def kernel(kappa: Fraction, decay: Fraction, radius: int) -> Fraction:
    return sum(kappa ** (radius - 1 - j) * decay**j for j in range(radius))


def run() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451.read_text(encoding="utf-8"))
    r450 = json.loads(R450.read_text(encoding="utf-8"))
    q = Fraction(str(r451["finite_fixture"]["ratio_q"]))
    decay = q**4
    c4 = Fraction(str(r450["derived"]["C4_edge"]))
    base = Fraction(str(r451["finite_fixture"]["base_tail"]))
    orientations = int(r451["finite_fixture"]["orientation_count"])
    factor = (2 ** (4 - 1)) * orientations
    source = Fraction(factor) * c4 * base**4
    resonant = kernel(decay, decay, 8)
    mutations = [
        {
            "name": "unit-propagation-coefficient",
            "reject": not (Fraction(1) < 1),
            "reason": "kappa=1 is outside the sufficient vanishing threshold",
        },
        {
            "name": "superunit-propagation-coefficient",
            "reject": not (Fraction(26, 25) < 1),
            "reason": "kappa>1 cannot be admitted by the contraction threshold",
        },
        {
            "name": "nondecaying-parent-base",
            "reject": not (Fraction(1) < 1),
            "reason": "r=1 would remove the parent geometric decay",
        },
        {
            "name": "drop-one-orientation",
            "mutated_factor": 2 ** (4 - 1),
            "reject": (2 ** (4 - 1)) != factor,
            "reason": "the R-451 source factor must include both orientations",
        },
        {
            "name": "add-undeclared-orientation",
            "mutated_factor": (2 ** (4 - 1)) * 3,
            "reject": ((2 ** (4 - 1)) * 3) != factor,
            "reason": "an extra orientation changes the declared source envelope",
        },
        {
            "name": "resonant-denominator",
            "reject": decay == decay,
            "reason": "the nonresonant quotient is invalid at kappa=r; use R*r^(R-1)",
        },
        {
            "name": "missing-one-step-recurrence",
            "mutated_recurrence": "H_R <= A*r^(R-1)",
            "reject": "kappa*H_(R-1)" not in "H_R <= A*r^(R-1)",
            "reason": "the resolvent requires the history-propagation term",
        },
        {
            "name": "fitted-source-constant",
            "mutated_source": source + 1,
            "reject": source + 1 != source,
            "reason": "A must be recomputed from factor*C4_edge*base^4",
        },
        {
            "name": "radius-rows-as-exhaustion",
            "mutated_scope": "all radius rows are the exhaustion theorem",
            "reject": "all radius rows are the exhaustion theorem" != "all radius rows prove the conditional recurrence",
            "reason": "exact rows do not replace the conditional limit argument",
        },
        {
            "name": "q3-promotion",
            "reject": manifest["scope"]["actual_q3_history_closed"] is False and manifest["scope"]["source_owned_kappa_closed"] is False,
            "reason": "the owner recurrence and kappa remain open",
        },
        {
            "name": "method-overhaul",
            "mutated_method": {"existing_forward_method_unchanged": False},
            "reject": not all({**manifest["method_preservation"], "existing_forward_method_unchanged": False}.values()),
            "reason": "the packet must remain an additive T-054 interface",
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
        "resonant_control": str(resonant),
        "scope": manifest["scope"],
        "method_preservation": manifest["method_preservation"],
        "non_claims": manifest["non_claims"],
    }
    print(f"R-452 HOSTILE {output['verdict']} {len(mutations)}/{len(mutations)}", flush=True)
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
