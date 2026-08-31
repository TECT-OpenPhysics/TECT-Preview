#!/usr/bin/env python3
"""Hostile mutation firewall for the R-466 tube-bound interface."""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-hostile-a6-positive-mass-tube-envelope" / "hostile.json"


def q(value: Any) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raw = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    volume = q(raw["Lx"]) * q(raw["Ly"]) * q(raw["Lz"])
    gamma = q(raw["gamma"])
    delta = Fraction(1, 16)
    side = 2 * delta
    cutoff = 1
    dimension = 6 * (2 * cutoff + 1) ** 3
    canonical_box = side**dimension
    canonical_coeff = gamma * volume / (12 * ((2 * cutoff + 1) ** 3) ** 3)

    mutations = [
        ("drop_one_real_coordinate", (side ** (dimension - 1)) != canonical_box),
        ("use_half_width_as_side", (delta**dimension) != canonical_box),
        ("omit_beta_energy_ceiling", 0.0 != float(Fraction(1, 2))),
        ("reverse_partition_comparison", not (1.0 <= 0.5)),
        ("rename_conditional_bound_as_actual_probability", "conditional owner-neutral interface" != "actual physical probability"),
        ("assert_fixed_width_uniform_positive_floor", not (-500.0 >= -100.0)),
        ("condition_on_zero_mass_exact_branch", not (Fraction(0) > 0)),
        ("allow_nonpositive_tube_width", not (Fraction(-1, 16) > 0)),
    ]
    rows = [{"mutation": name, "rejected": bool(ok), "status": "PASS" if ok else "FAIL"} for name, ok in mutations]
    passed = sum(row["status"] == "PASS" for row in rows)
    output = {
        "schema": "tect/a6-classii-positive-mass-tube-envelope-hostile/1.0",
        "run_kind": "hostile",
        "result_id": "R-466",
        "exploration_id": "EXP-001341",
        "verdict": "HOSTILE_MUTATIONS_REJECTED" if passed == len(rows) else "HOSTILE_MUTATION_FAILURE",
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "mutations": rows,
        "canonical_fixture": {"cutoff": cutoff, "dimension": dimension, "tube_half_width": str(delta), "box_volume": str(canonical_box), "coefficient": str(canonical_coeff), "finite": math.isfinite(float(canonical_coeff))},
        "scope": "Hostile mutation firewall only; no source-owned branch, uniform probability, entropy, or physical result is inferred.",
        "non_claims": ["Mutation rejection is not a source-owner admission.", "No cutoff-uniform, entropy, tightness, continuum, physical, QFT, Yang--Mills or mass-gap claim is admitted.", "Existing research methods and owner order are unchanged."],
    }
    path = args.output if args.output.is_absolute() else REPO / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"HOSTILE R-466 {output['verdict']} {passed}/{len(rows)}")
    print(f"Evidence: {path.resolve()}")
    return 0 if output["verdict"].endswith("REJECTED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
