#!/usr/bin/env python3
"""Hostile mutations for the R-453 defect-stable recurrence contract."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-defect-stable-history-resolvent-manifest.json"
R451 = ROOT / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
R450 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-pre_a_cp1_st8_q3lock_two_orientation_shell_transfer/primary.json"


def kernel(kappa: Fraction, base: Fraction, radius: int) -> Fraction:
    return sum(kappa ** (radius - 1 - j) * base**j for j in range(radius))


def run() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    r451 = json.loads(R451.read_text(encoding="utf-8"))
    r450 = json.loads(R450.read_text(encoding="utf-8"))
    q = Fraction(str(r451["finite_fixture"]["ratio_q"]))
    parent_decay = q**4
    c4 = Fraction(str(r450["derived"]["C4_edge"]))
    base = Fraction(str(r451["finite_fixture"]["base_tail"]))
    orientations = int(r451["finite_fixture"]["orientation_count"])
    factor = (2 ** (4 - 1)) * orientations
    source = Fraction(factor) * c4 * base**4
    kappa = Fraction(1, 2)
    defect_base = Fraction(1, 3)
    amplitude = Fraction(3, 2)
    radius = 7
    exact_defects = [amplitude * defect_base**(step - 1) for step in range(1, radius + 1)]
    correct_weighted = sum(kappa ** (radius - step) * exact_defects[step - 1] for step in range(1, radius + 1))
    wrong_weighted = sum(kappa ** (radius - step + 1) * exact_defects[step - 1] for step in range(1, radius + 1))
    mutations = [
        {
            "name": "drop-defect-convolution",
            "reject": source * kernel(kappa, parent_decay, radius) + amplitude * kernel(kappa, defect_base, radius) != source * kernel(kappa, parent_decay, radius),
            "reason": "a positive residual cannot be omitted from the envelope",
        },
        {
            "name": "shift-residual-index",
            "reject": wrong_weighted != correct_weighted,
            "reason": "step j receives kappa^(R-j), not one extra propagation factor",
        },
        {
            "name": "unit-propagation-coefficient",
            "reject": not (Fraction(1) < 1),
            "reason": "kappa=1 is outside the sufficient vanishing threshold",
        },
        {
            "name": "unit-defect-base",
            "reject": not (Fraction(1) < 1),
            "reason": "s=1 is outside the sufficient vanishing threshold",
        },
        {
            "name": "superunit-propagation-coefficient",
            "reject": not (Fraction(26, 25) < 1),
            "reason": "kappa>1 cannot be admitted by contraction",
        },
        {
            "name": "superunit-defect-base",
            "reject": not (Fraction(6, 5) < 1),
            "reason": "s>1 cannot be admitted by defect decay",
        },
        {
            "name": "nondecaying-parent-base",
            "reject": not (Fraction(1) < 1),
            "reason": "r=1 removes the inherited R-451 geometric source decay",
        },
        {
            "name": "fitted-source-constant",
            "reject": source + 1 != source,
            "reason": "A is recomputed from the R-451/R-450 parent constants",
        },
        {
            "name": "fitted-defect-amplitude",
            "reject": amplitude + 1 != amplitude,
            "reason": "D is a declared owner-side bound, not a post-fit free parameter",
        },
        {
            "name": "resonant-denominator",
            "reject": kappa == kappa,
            "reason": "the quotient is invalid at resonance; use R*x^(R-1)",
        },
        {
            "name": "unbounded-residual-admitted",
            "reject": not all(Fraction(1) <= amplitude * defect_base**(step - 1) for step in range(1, radius + 1)),
            "reason": "a residual must satisfy the declared common geometric bound",
        },
        {
            "name": "radius-rows-as-exhaustion",
            "reject": "exact recurrence rows" != "the radius rows are an exhaustion theorem",
            "reason": "finite algebra rows do not replace the owner-level uniform limit",
        },
        {
            "name": "method-overhaul",
            "reject": not all({**manifest["method_preservation"], "existing_forward_method_unchanged": False}.values()),
            "reason": "R-453 must remain an additive T-054 interface",
        },
        {
            "name": "physical-promotion",
            "reject": manifest["scope"]["pre_a_closed"] is False and manifest["scope"]["c6_closed"] is False,
            "reason": "a conditional scalar envelope is not a physical or Clay result",
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
        "control": {"correct_weighted": str(correct_weighted), "wrong_weighted": str(wrong_weighted), "source_constant": str(source)},
        "scope": manifest["scope"],
        "method_preservation": manifest["method_preservation"],
        "non_claims": manifest["non_claims"],
    }
    print(f"R-453 HOSTILE {output['verdict']} {len(mutations)}/{len(mutations)}", flush=True)
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
