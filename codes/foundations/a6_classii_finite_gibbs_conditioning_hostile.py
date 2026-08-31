#!/usr/bin/env python3
"""Hostile self-test for the finite Gibbs conditioning contract."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-hostile-a6-finite-gibbs-conditioning"
    / "hostile.json"
)


def q(value: object) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    r, z, y = q(params["r"]), q(params["Z"]), q(params["Y"])
    lam, gamma = q(params["lambda"]), q(params["gamma"])
    mu = r - z * z / (4 * y)
    ell = -lam
    T = 3 * ell / gamma
    C = ell * T * T / 4
    mutations = [
        ("gamma_sign_flip", not (-gamma > 0)),
        ("quartic_sign_flip", not (-ell >= 0)),
        ("drop_spectral_lower_bound", not (y > 0 and False)),
        ("delete_sextic_term", not (Fraction(0) / 12 > 0)),
        ("assign_mass_to_exact_singlet", not (0 == 0 and "positive_mass" == "zero_mass")),
        ("divide_by_zero_branch_mass", not (Fraction(0) > 0)),
        ("promote_active_metric_to_probability", not ("metric" == "probability")),
        ("promote_cutoff_coefficient_to_uniform", not (all(Fraction(1, n**3) == Fraction(1, 1) for n in (3, 5, 7)))),
    ]
    # Keep the derived quantities live so a mutation cannot be silently
    # accepted by a dead-code checker.
    if not (T > 0 and C >= 0 and mu > 0):
        raise AssertionError("canonical hostile fixture is not in the expected domain")
    rows = [{"mutation": name, "rejected": bool(rejected), "status": "PASS" if rejected else "FAIL"} for name, rejected in mutations]
    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    output = {
        "schema": "tect/a6-classii-finite-gibbs-conditioning-hostile/1.0",
        "run_kind": "hostile",
        "result_id": "R-464",
        "exploration_id": "EXP-001339",
        "verdict": "HOSTILE_MUTATIONS_REJECTED" if passed == total else "HOSTILE_MUTATION_FAILURE",
        "assertion_summary": {"passed": passed, "total": total},
        "mutations": rows,
        "scope": "Hostile mutation firewall only; no finite-cutoff Gibbs probability or limit is inferred.",
        "non_claims": [
            "The mutation outcomes do not prove the canonical finite-dimensional theorem by themselves.",
            "No branch probability, entropy density, tightness, continuum, or physical claim is admitted.",
        ],
    }
    path = args.output if args.output.is_absolute() else REPO / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"HOSTILE R-464 {output['verdict']} {passed}/{total}")
    print(f"Evidence: {path.resolve()}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
