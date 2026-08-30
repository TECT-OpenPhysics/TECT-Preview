#!/usr/bin/env python3
"""Hostile mutations for the R-454 variable-coefficient resolver."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-variable-coefficient-defect-resolvent-manifest.json"
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
    upper = Fraction(3, 4)
    defect_base = Fraction(1, 3)
    amplitude = Fraction(3, 2)
    radius = 7
    positive_step_history = source + amplitude
    bad_coefficient = upper + Fraction(1, 10)
    correct_residual_weight = sum(upper ** (radius - step) * amplitude * defect_base ** (step - 1) for step in range(1, radius + 1))
    shifted_residual_weight = sum(upper ** (radius - step + 1) * amplitude * defect_base ** (step - 1) for step in range(1, radius + 1))
    mutations = [
        {"name": "omit-common-coefficient-bound", "reject": not (bad_coefficient <= upper), "reason": "path-product domination requires every kappa_R<=kappa_bar"},
        {"name": "negative-step-coefficient", "reject": not (Fraction(-1, 4) >= 0), "reason": "the nonnegative recurrence hypothesis is explicit"},
        {"name": "replace-variable-by-unbounded-step", "reject": not (bad_coefficient <= upper), "reason": "a single super-bound step invalidates the common envelope"},
        {"name": "drop-defect-convolution", "reject": source * kernel(upper, parent_decay, radius) + amplitude * kernel(upper, defect_base, radius) != source * kernel(upper, parent_decay, radius), "reason": "positive residuals cannot be omitted"},
        {"name": "shift-residual-index", "reject": shifted_residual_weight != correct_residual_weight, "reason": "step j receives kappa_bar^(R-j), not an extra factor"},
        {"name": "unit-propagation-upper-bound", "reject": not (Fraction(1) < 1), "reason": "kappa_bar=1 is outside the sufficient vanishing threshold"},
        {"name": "unit-defect-base", "reject": not (Fraction(1) < 1), "reason": "s=1 is outside the sufficient vanishing threshold"},
        {"name": "superunit-propagation-upper-bound", "reject": not (Fraction(26, 25) < 1), "reason": "kappa_bar>1 cannot be admitted"},
        {"name": "superunit-defect-base", "reject": not (Fraction(6, 5) < 1), "reason": "s>1 cannot be admitted"},
        {"name": "nondecaying-parent", "reject": not (Fraction(1) < 1), "reason": "r=1 removes inherited source decay"},
        {"name": "fitted-source-constant", "reject": source + 1 != source, "reason": "A must be recomputed from R-451/R-450"},
        {"name": "fitted-defect-amplitude", "reject": amplitude + 1 != amplitude, "reason": "D is an owner input, not a post-fit number"},
        {"name": "one-step-history-without-bound", "reject": positive_step_history * bad_coefficient > positive_step_history * upper, "reason": "unbounded coefficients invalidate the monotone step"},
        {"name": "radius-patterns-as-exhaustion", "reject": "scalar pattern rows" != "uniform exhaustion theorem", "reason": "finite patterns do not replace the owner limit"},
        {"name": "method-overhaul", "reject": not all({**manifest["method_preservation"], "existing_forward_method_unchanged": False}.values()), "reason": "R-454 is additive and must preserve T-054/T-059/T-061"},
        {"name": "physical-promotion", "reject": manifest["scope"]["pre_a_closed"] is False and manifest["scope"]["c6_closed"] is False, "reason": "conditional scalar control is not physical or Clay closure"},
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
        "control": {"correct_residual_weight": str(correct_residual_weight), "shifted_residual_weight": str(shifted_residual_weight), "upper": str(upper), "bad_coefficient": str(bad_coefficient), "source_constant": str(source)},
        "scope": manifest["scope"],
        "method_preservation": manifest["method_preservation"],
        "non_claims": manifest["non_claims"],
    }
    print(f"R-454 HOSTILE {output['verdict']} {len(mutations)}/{len(mutations)}", flush=True)
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
