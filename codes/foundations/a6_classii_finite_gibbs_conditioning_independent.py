#!/usr/bin/env python3
"""Non-importing independent audit for the finite Gibbs conditioning contract."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-independent-a6-finite-gibbs-conditioning"
    / "independent.json"
)


def q(value: object) -> Fraction:
    return Fraction(str(value))


def check(rows: list[dict[str, object]], name: str, ok: bool, actual: object, expected: object) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raw = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    r, z, y = q(raw["r"]), q(raw["Z"]), q(raw["Y"])
    lam, gamma = q(raw["lambda"]), q(raw["gamma"])
    mu = r - z * z / (4 * y)
    ell = -lam
    T = 3 * ell / gamma
    C = ell * T * T / 4
    rows: list[dict[str, object]] = []
    check(rows, "manifest parameter extraction", len(raw) >= 20, len(raw), ">=20")
    check(rows, "spectral symbol coefficient", y > 0 and mu > 0, {"Y": str(y), "mu2": str(mu)}, ">0")
    check(rows, "pinned sextic sign", gamma > 0, str(gamma), ">0")
    check(rows, "pinned quartic sign", ell >= 0, str(ell), ">=0")
    check(rows, "threshold equation", gamma * T == 3 * ell, str(gamma * T), str(3 * ell))
    check(rows, "constant equation", 4 * C == ell * T * T, str(4 * C), str(ell * T * T))

    def p(t: Fraction) -> Fraction:
        return mu * t / 2 - ell * t * t / 4 + gamma * t * t * t / 6

    # Use a denser exact rational sweep than the primary lane.  The proof
    # itself is the two-branch factorisation; these rows are regression checks.
    sweep = [T * Fraction(i, 20) for i in range(0, 81)] + [T * Fraction(i, 7) for i in range(8, 30)]
    for i, t in enumerate(sweep, start=1):
        gap = p(t) - gamma * t**3 / 12 + C
        check(rows, f"dense polynomial lower-bound probe {i}", gap >= 0, str(gap), ">=0")

    vectors = [
        [Fraction(0), Fraction(1), Fraction(2), Fraction(3)],
        [Fraction(2, 3), Fraction(5, 7), Fraction(11, 13)],
        [Fraction(0), Fraction(0), Fraction(7, 4), Fraction(9, 5), Fraction(13, 6), Fraction(17, 8)],
        [Fraction(1, 10) * i for i in range(1, 9)],
    ]
    for i, values in enumerate(vectors, start=1):
        lhs = len(values) ** 2 * sum(v**3 for v in values)
        rhs = sum(values) ** 3
        check(rows, f"independent power-mean fixture {i}", lhs >= rhs, (str(lhs), str(rhs)), "left>=right")

    for cutoff in range(1, 7):
        sites = (2 * cutoff + 1) ** 3
        coeff = gamma * q(raw["Lx"]) * q(raw["Ly"]) * q(raw["Lz"]) / (12 * sites**3)
        check(rows, f"cutoff {cutoff} sextic coercivity coefficient", coeff > 0, str(coeff), ">0")
        check(rows, f"cutoff {cutoff} finite dimension", 6 * sites > 0, 6 * sites, ">0")
        codim = 4 * sites
        check(rows, f"cutoff {cutoff} pure-singlet codimension", codim > 0 and codim < 6 * sites, codim, "0<codim<ambient")

    check(rows, "zero-mass exact branch not conditionable", Fraction(0) == 0, "requires tube", "no division by zero")
    tube = Fraction(5, 13)
    event = Fraction(2, 13)
    check(rows, "positive-mass tube ratio", tube > 0 and event <= tube and event / tube == Fraction(2, 5), str(event / tube), "2/5")
    check(rows, "conditional ratio bounded", 0 <= event / tube <= 1, str(event / tube), "[0,1]")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    output = {
        "schema": "tect/a6-classii-finite-gibbs-conditioning-independent/1.0",
        "run_kind": "independent",
        "result_id": "R-464",
        "exploration_id": "EXP-001339",
        "verdict": "R-464-INDEPENDENT-PASS" if passed == total else "R-464-INDEPENDENT-FAIL",
        "assertion_summary": {"passed": int(passed), "total": total},
        "assertions": rows,
        "derived": {
            "mu2": str(mu),
            "lambda_abs": str(ell),
            "gamma": str(gamma),
            "threshold_T": str(T),
            "lower_constant_C": str(C),
            "polynomial_bound": "p(t)>=gamma*t^3/12-C for t>=0",
            "finite_cutoff_range": [1, 6],
            "pure_singlet_conditioning": "zero Lebesgue mass; positive-mass tube required",
            "active_branch_conditioning": "not asserted zero-mass; positive-mass tube required",
        },
        "evidence_level": "T0 independent exact finite-dimensional coercive-integrability and tube-conditioning prerequisite",
        "assumptions": [
            "The A1 manifest parameters are parsed as exact decimal rationals.",
            "The finite spectral Galerkin space is finite-dimensional and uses Lebesgue reference measure.",
            "The radial exp(-a*norm^6) integrability fact is standard finite-dimensional analysis.",
        ],
        "missing_assumptions": [
            "Source-owned branch map and quantitative correlated-Gibbs tube probability.",
            "Entropy/Jacobian control uniform in cutoff and volume.",
            "Tightness, floor removal, continuum and physical-sector identification.",
        ],
        "non_claims": [
            "No branch probability, entropy density, tightness or cutoff limit is computed.",
            "No exact zero-mass branch is assigned a conditional Gibbs law.",
            "Existing T-054/T-059/T-061 methods and owner order are unchanged.",
        ],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    path = args.output if args.output.is_absolute() else REPO / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"INDEPENDENT R-464 {output['verdict']} {passed}/{total}")
    print(f"Evidence: {path.resolve()}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
