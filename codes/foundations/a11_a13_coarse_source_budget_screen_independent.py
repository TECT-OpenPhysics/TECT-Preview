#!/usr/bin/env python3
"""Independent stdlib-only rederivation of the A11/A13 coarse screen."""

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
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-coarse-source-budget-screen" / "result.json"
FILES = {
    "a1": REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json",
    "a10": REPO / "claims" / "A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION" / "classii_relative_structural_reduction_manifest.json",
    "a12": REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_source_square_reduction_manifest.json",
    "sharp": REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_sharp_cube_budget_obstruction_manifest.json",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def f(value: Any) -> Fraction:
    return Fraction(str(value))


def s(value: Fraction) -> str:
    getcontext().prec = 80
    return format(Decimal(value.numerator) / Decimal(value.denominator), "f")


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def compute() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in FILES.items()}
    composition = data["a10"]["composition_target"]
    theta = f(composition["theta"])
    alpha_f = f(composition["alpha_f"])
    alpha_c = f(composition["alpha_c"])
    alpha_d = f(composition["alpha_d"])
    epsilon_6 = f(composition["epsilon_6"])
    epsilon_d = f(composition["epsilon_d"])
    p = f(composition["p"])
    gamma = f(data["a1"]["parameters"]["gamma"])
    base = f(data["a12"]["derived_oracles"]["source_base_constant"])
    m_r = f(data["sharp"]["budget"]["M_R"])
    h_lower = f(data["sharp"]["budget"]["sharp_lower"])
    alpha = alpha_f + alpha_c + alpha_d
    reserve = gamma / 6 - epsilon_6 - epsilon_d
    envelope = base * m_r**2 * h_lower
    retained = 1 - theta
    k_registered = retained**2 * envelope / (4 * alpha_f)
    k_doubled = retained**2 * envelope / (2 * alpha_f)
    limit_registered = 4 * alpha_f * reserve / envelope
    limit_doubled = 2 * alpha_f * reserve / envelope
    getcontext().prec = 80
    req_registered = Decimal(1) - (Decimal(limit_registered.numerator) / Decimal(limit_registered.denominator)).sqrt()
    req_doubled = Decimal(1) - (Decimal(limit_doubled.numerator) / Decimal(limit_doubled.denominator)).sqrt()
    derived = {
        "theta": s(theta), "alpha_f": s(alpha_f), "alpha_c": s(alpha_c), "alpha_d": s(alpha_d), "alpha": s(alpha),
        "p": s(p), "p_alpha": s(p * alpha), "gamma": s(gamma), "epsilon_6": s(epsilon_6), "epsilon_d": s(epsilon_d),
        "B6": s(reserve), "source_base_constant": s(base), "M_R": s(m_r), "sharp_lower_H6": s(h_lower),
        "C_src_coarse": s(envelope), "s": s(retained), "target_s2": s(retained**2),
        "Kf_registered": s(k_registered), "Kf_conservative": s(k_doubled),
        "required_s2_registered": s(limit_registered), "required_s2_conservative": s(limit_doubled),
        "required_theta_registered": format(req_registered, "f"), "required_theta_conservative": format(req_doubled, "f"),
        "registered_ratio_Kf_over_B6": s(k_registered / reserve), "conservative_ratio_Kf_over_B6": s(k_doubled / reserve),
    }
    rows: list[dict[str, Any]] = []
    check(rows, "reserve_positive", reserve > 0, derived["B6"], ">0")
    check(rows, "p_alpha_below_one", p * alpha < 1, derived["p_alpha"], "<1")
    check(rows, "envelope_positive", envelope > 0, derived["C_src_coarse"], ">0")
    check(rows, "registered_target_exceeds_reserve", k_registered > reserve, derived["Kf_registered"], f">{derived['B6']}")
    check(rows, "doubled_target_exceeds_reserve", k_doubled > reserve, derived["Kf_conservative"], f">{derived['B6']}")
    check(rows, "registered_required_theta_is_higher", req_registered > Decimal(1) - Decimal(theta.numerator) / Decimal(theta.denominator), derived["required_theta_registered"], f">{derived['theta']}")
    check(rows, "doubled_required_theta_is_higher", req_doubled > Decimal(1) - Decimal(theta.numerator) / Decimal(theta.denominator), derived["required_theta_conservative"], f">{derived['theta']}")
    check(rows, "registered_identity", k_registered * 4 * alpha_f == retained**2 * envelope, "exact Fraction identity", "true")
    check(rows, "doubled_is_twice_registered", k_doubled == 2 * k_registered, "exact Fraction identity", "true")
    return derived, rows, {str(path.relative_to(REPO)): digest(path) for path in FILES.values()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    derived, rows, authorities = compute()
    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/a11-a13-coarse-source-budget-screen-independent-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent Fraction-only recomputation of the coefficient-blind coarse screen; exact-B and joint routes remain open.",
        "source_authorities": authorities, "derived": derived, "assertions": rows,
        "assertion_count": len(rows), "conclusion": "The registered theta target fails the coarse envelope only; this is not an exact-B or production closure.",
        "honesty_boundary": ["not exact-B", "not joint source/potential", "not action reconstruction", "not gate closure"], "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A11/A13 INDEPENDENT SCREEN FAIL {len(rows)-len(failures)}/{len(rows)}")
        return 1
    print(f"A11/A13 INDEPENDENT SCREEN PASS {len(rows)}/{len(rows)}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
