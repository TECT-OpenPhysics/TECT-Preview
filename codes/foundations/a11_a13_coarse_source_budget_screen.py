#!/usr/bin/env python3
"""Exact coarse coefficient-blind source-budget screening for A11/A13.

This is an exploration-level screen.  It tests the registered A10 theta
target against the coefficient-blind A12 source-square envelope.  It does
not estimate the exact-B shell-localised source, the joint source/potential
allocation, or any production-valid action reconstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-coarse-source-budget-screen" / "result.json"
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
A10 = REPO / "claims" / "A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION" / "classii_relative_structural_reduction_manifest.json"
A12 = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_source_square_reduction_manifest.json"
SHARP = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_sharp_cube_budget_obstruction_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def decimal(value: Fraction) -> str:
    getcontext().prec = 80
    return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def derive() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    a1 = json.loads(A1.read_text(encoding="utf-8"))
    a10 = json.loads(A10.read_text(encoding="utf-8"))
    a12 = json.loads(A12.read_text(encoding="utf-8"))
    sharp = json.loads(SHARP.read_text(encoding="utf-8"))
    target = a10["composition_target"]
    gamma = fraction(a1["parameters"]["gamma"])
    theta = fraction(target["theta"])
    alpha_f = fraction(target["alpha_f"])
    alpha_c = fraction(target["alpha_c"])
    alpha_d = fraction(target["alpha_d"])
    epsilon_6 = fraction(target["epsilon_6"])
    epsilon_d = fraction(target["epsilon_d"])
    p = fraction(target["p"])
    source_base = fraction(a12["derived_oracles"]["source_base_constant"])
    m_r = fraction(sharp["budget"]["M_R"])
    sharp_lower = fraction(sharp["budget"]["sharp_lower"])
    alpha = alpha_f + alpha_c + alpha_d
    b6 = gamma / 6 - epsilon_6 - epsilon_d
    c_src = source_base * m_r * m_r * sharp_lower
    s = 1 - theta
    target_s2 = s * s
    kf_registered = target_s2 * c_src / (4 * alpha_f)
    kf_conservative = target_s2 * c_src / (2 * alpha_f)
    required_s2_registered = 4 * alpha_f * b6 / c_src
    required_s2_conservative = 2 * alpha_f * b6 / c_src
    getcontext().prec = 80
    required_theta_registered = Decimal(1) - (Decimal(required_s2_registered.numerator) / Decimal(required_s2_registered.denominator)).sqrt()
    required_theta_conservative = Decimal(1) - (Decimal(required_s2_conservative.numerator) / Decimal(required_s2_conservative.denominator)).sqrt()
    derived = {
        "theta": decimal(theta),
        "alpha_f": decimal(alpha_f),
        "alpha_c": decimal(alpha_c),
        "alpha_d": decimal(alpha_d),
        "alpha": decimal(alpha),
        "p": decimal(p),
        "p_alpha": decimal(p * alpha),
        "gamma": decimal(gamma),
        "epsilon_6": decimal(epsilon_6),
        "epsilon_d": decimal(epsilon_d),
        "B6": decimal(b6),
        "source_base_constant": decimal(source_base),
        "M_R": decimal(m_r),
        "sharp_lower_H6": decimal(sharp_lower),
        "C_src_coarse": decimal(c_src),
        "s": decimal(s),
        "target_s2": decimal(target_s2),
        "Kf_registered": decimal(kf_registered),
        "Kf_conservative": decimal(kf_conservative),
        "required_s2_registered": decimal(required_s2_registered),
        "required_s2_conservative": decimal(required_s2_conservative),
        "required_theta_registered": format(required_theta_registered, "f"),
        "required_theta_conservative": format(required_theta_conservative, "f"),
        "registered_ratio_Kf_over_B6": decimal(kf_registered / b6),
        "conservative_ratio_Kf_over_B6": decimal(kf_conservative / b6),
    }
    assertions: list[dict[str, Any]] = []
    add(assertions, "B6_positive", b6 > 0, derived["B6"], ">0")
    add(assertions, "p_alpha_below_one", p * alpha < 1, derived["p_alpha"], "<1")
    add(assertions, "source_envelope_positive", c_src > 0, derived["C_src_coarse"], ">0")
    add(assertions, "registered_target_fails_coarse_envelope", kf_registered > b6, derived["Kf_registered"], f">{derived['B6']}")
    add(assertions, "conservative_target_fails_coarse_envelope", kf_conservative > b6, derived["Kf_conservative"], f">{derived['B6']}")
    add(assertions, "registered_theta_required_exceeds_target", required_theta_registered > Decimal(1) - (Decimal(theta.numerator) / Decimal(theta.denominator)), derived["required_theta_registered"], f">{derived['theta']}")
    add(assertions, "conservative_theta_required_exceeds_target", required_theta_conservative > Decimal(1) - (Decimal(theta.numerator) / Decimal(theta.denominator)), derived["required_theta_conservative"], f">{derived['theta']}")
    add(assertions, "source_allocation_formula_identity", kf_registered * 4 * alpha_f == target_s2 * c_src, "exact Fraction identity", "true")
    add(assertions, "conservative_formula_is_double_registered", kf_conservative == 2 * kf_registered, "exact Fraction identity", "true")
    authorities = {str(path.relative_to(REPO)): sha256(path) for path in (A1, A10, A12, SHARP)}
    return derived, assertions, authorities


def run(output: Path) -> int:
    derived, assertions, authorities = derive()
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/a11-a13-coarse-source-budget-screen-primary-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Coefficient-blind A12 source-square envelope applied to the registered A10 composition target; exploration screen only.",
        "source_authorities": authorities,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "The registered theta target fails the coefficient-blind coarse envelope; this does not refute exact-B shell-localised, joint source/potential, or production-valid action routes.",
        "honesty_boundary": ["not an exact-B theorem", "not a joint allocation theorem", "not a production action reconstruction", "not a gate closure"],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A11/A13 COARSE SCREEN FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A11/A13 COARSE SCREEN PASS {len(assertions)}/{len(assertions)}")
    print(f"Evidence: {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    return run(output)


if __name__ == "__main__":
    raise SystemExit(main())
