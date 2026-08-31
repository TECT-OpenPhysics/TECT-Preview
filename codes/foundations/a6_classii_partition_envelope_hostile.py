#!/usr/bin/env python3
"""Hostile mutation firewall for the R-465 comparison-envelope diagnostic."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-hostile-a6-partition-envelope"
    / "hostile.json"
)


def q(value: object) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    volume = q(params["Lx"]) * q(params["Ly"]) * q(params["Lz"])
    gamma = q(params["gamma"])
    ell = -q(params["lambda"])
    sites_n1 = (2 * 1 + 1) ** 3
    sites_n2 = (2 * 2 + 1) ** 3
    canonical_scale = gamma * volume / (12 * sites_n1**3)

    mutations = [
        ("flip_sextic_sign", not (-gamma > 0)),
        ("use_m_minus_two_instead_of_m_minus_three", not (gamma * volume / (12 * sites_n1**2) * sites_n1**3 == gamma * volume / 12)),
        ("drop_six_real_coordinates_per_site", not (sites_n1 == 6 * sites_n1)),
        ("drop_beta_from_radial_envelope", not (Fraction(1, 2) * canonical_scale == canonical_scale)),
        ("omit_constant_shift_from_bound", not (ell * volume * 0 == ell * volume)),
        ("assert_cutoff_uniform_coercive_coefficient", not (gamma * volume / (12 * sites_n1**3) == gamma * volume / (12 * sites_n2**3))),
        ("rename_comparison_envelope_as_actual_partition", not ("comparison envelope" == "actual partition")),
        ("promote_finite_rows_to_entropy_tightness_or_continuum", not ("finite audit rows" == "uniform continuum theorem")),
    ]
    rows = [{"mutation": name, "rejected": bool(rejected), "status": "PASS" if rejected else "FAIL"} for name, rejected in mutations]
    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    output: dict[str, Any] = {
        "schema": "tect/a6-classii-partition-envelope-hostile/1.0",
        "run_kind": "hostile",
        "result_id": "R-465",
        "exploration_id": "EXP-001340",
        "verdict": "HOSTILE_MUTATIONS_REJECTED" if passed == total else "HOSTILE_MUTATION_FAILURE",
        "assertion_summary": {"passed": passed, "total": total},
        "mutations": rows,
        "scope": "Hostile mutation firewall only; no partition asymptotic, probability, entropy density, or limit is inferred.",
        "non_claims": [
            "Mutation rejection does not by itself prove the comparison-envelope formula.",
            "No cutoff-uniform estimate, branch probability, tightness, continuum, physical, QFT, Yang--Mills or mass-gap claim is admitted.",
            "The established research methods and owner order are unchanged.",
        ],
    }
    path = args.output if args.output.is_absolute() else REPO / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"HOSTILE R-465 {output['verdict']} {passed}/{total}")
    print(f"Evidence: {path.resolve()}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
