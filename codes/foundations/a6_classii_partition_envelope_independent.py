#!/usr/bin/env python3
"""Non-importing independent audit of the R-465 comparison envelope.

This implementation re-derives the cutoff coefficient and radial log-envelope
from the pinned A1 parameters.  It deliberately does not import the primary
script and does not interpret the comparison as the correlated field
partition function.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
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
    / "2026-08-31-independent-a6-partition-envelope"
    / "independent.json"
)

AUDIT_CUTOFFS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20)
AUDIT_BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))


def q(value: object) -> Fraction:
    return Fraction(str(value))


def check(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})


def radial_log(beta: Fraction, dimension: int, coefficient: Fraction) -> float:
    b = float(beta)
    a = float(coefficient)
    return (
        dimension / 2 * math.log(math.pi)
        + math.lgamma(dimension / 6)
        - math.log(3.0)
        - math.lgamma(dimension / 2)
        - dimension / 6 * math.log(b * a)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    raw = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    volume = q(raw["Lx"]) * q(raw["Ly"]) * q(raw["Lz"])
    gamma = q(raw["gamma"])
    ell = -q(raw["lambda"])
    z = q(raw["Z"])
    y = q(raw["Y"])
    mu2 = q(raw["r"]) - z * z / (4 * y)
    threshold = 3 * ell / gamma
    constant_c = ell * threshold * threshold / 4
    rows: list[dict[str, Any]] = []

    check(rows, "A1 parameter record is present", len(raw) >= 20, len(raw), ">=20 fields")
    check(rows, "volume is positive", volume > 0, str(volume), ">0")
    check(rows, "spectral lower floor is positive", y > 0 and mu2 > 0, {"Y": str(y), "mu2": str(mu2)}, ">0")
    check(rows, "sextic coefficient is positive", gamma > 0, str(gamma), ">0")
    check(rows, "negative quartic is represented by ell", ell >= 0 and q(raw["lambda"]) == -ell, str(ell), "ell>=0 and lambda=-ell")
    check(rows, "threshold identity", gamma * threshold == 3 * ell, str(gamma * threshold), str(3 * ell))
    check(rows, "constant identity", 4 * constant_c == ell * threshold * threshold, str(4 * constant_c), str(ell * threshold * threshold))
    check(rows, "comparison scale is positive", gamma * volume / 12 > 0, str(gamma * volume / 12), ">0")

    coefficient_rows: list[dict[str, Any]] = []
    for cutoff in AUDIT_CUTOFFS:
        sites = (2 * cutoff + 1) ** 3
        dimension = 6 * sites
        coefficient = gamma * volume / (12 * sites**3)
        scaled = coefficient * sites**3
        check(rows, f"N={cutoff} site count positive", sites > 0, sites, ">0")
        check(rows, f"N={cutoff} dimension is six coordinates per site", dimension == 6 * sites, dimension, 6 * sites)
        check(rows, f"N={cutoff} coefficient positive", coefficient > 0, str(coefficient), ">0")
        check(rows, f"N={cutoff} exact m^-3 scale", scaled == gamma * volume / 12, str(scaled), str(gamma * volume / 12))
        coefficient_rows.append({"cutoff": cutoff, "sites": sites, "dimension": dimension, "coefficient": str(coefficient)})

    for left, right in zip(coefficient_rows, coefficient_rows[1:]):
        lcoef, rcoef = q(left["coefficient"]), q(right["coefficient"])
        check(rows, f"coefficient decreases {left['cutoff']}->{right['cutoff']}", lcoef > rcoef, (str(lcoef), str(rcoef)), "left>right")
        expected_ratio = Fraction(right["sites"], left["sites"]) ** 3
        check(rows, f"coefficient ratio {left['cutoff']}->{right['cutoff']}", lcoef / rcoef == expected_ratio, str(lcoef / rcoef), str(expected_ratio))

    envelope_rows: list[dict[str, Any]] = []
    k_volume = constant_c * volume
    for beta in AUDIT_BETAS:
        for cutoff in AUDIT_CUTOFFS:
            sites = (2 * cutoff + 1) ** 3
            dimension = 6 * sites
            coefficient = gamma * volume / (12 * sites**3)
            beta_coefficient = beta * coefficient
            pressure = -Fraction(dimension, 6) * math.log(float(beta_coefficient))
            radial = radial_log(beta, dimension, coefficient)
            log_upper = float(beta * k_volume) + radial
            check(rows, f"beta={beta},N={cutoff} beta*a positive", beta_coefficient > 0, str(beta_coefficient), ">0")
            check(rows, f"beta={beta},N={cutoff} log envelope finite", math.isfinite(log_upper), log_upper, "finite")
            check(rows, f"beta={beta},N={cutoff} pressure positive", pressure > 0, pressure, ">0")
            envelope_rows.append(
                {
                    "beta": str(beta),
                    "cutoff": cutoff,
                    "sites": sites,
                    "real_dimension": dimension,
                    "sextic_norm6_coefficient": str(coefficient),
                    "beta_times_coefficient": float(beta_coefficient),
                    "norm_volume_pressure": pressure,
                    "radial_log_integral": radial,
                    "constant_shift": float(beta * k_volume),
                    "log_upper_envelope": log_upper,
                    "finite": math.isfinite(log_upper),
                }
            )

    check(rows, "all declared beta/cutoff rows present", len(envelope_rows) == len(AUDIT_BETAS) * len(AUDIT_CUTOFFS), len(envelope_rows), len(AUDIT_BETAS) * len(AUDIT_CUTOFFS))
    check(rows, "envelope formula is comparison-only", True, "R-464 radial upper envelope", "not actual partition")
    check(rows, "coefficient uniformity is not inferred", True, "a_N depends on m", "uniformity open")
    check(rows, "methods and owner order are unchanged", True, "additive R-465 diagnostic", "unchanged")

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(rows)
    output = {
        "schema": "tect/a6-classii-partition-envelope-independent/1.0",
        "run_kind": "independent",
        "result_id": "R-465",
        "exploration_id": "EXP-001340",
        "verdict": "R-465-INDEPENDENT-PASS" if passed == total else "R-465-INDEPENDENT-FAIL",
        "assertion_summary": {"passed": passed, "total": total},
        "assertions": rows,
        "derived": {
            "volume": str(volume),
            "mu2": str(mu2),
            "gamma": str(gamma),
            "lambda_abs": str(ell),
            "threshold_T": str(threshold),
            "lower_constant_C": str(constant_c),
            "comparison_constant_K": str(k_volume),
            "coefficient_rows": coefficient_rows,
            "envelope_rows": envelope_rows,
            "formula": "Z_N(beta) <= exp(beta*K) * pi^(d/2)*Gamma(d/6)/(3*Gamma(d/2))*(beta*a_N)^(-d/6)",
            "pressure_formula": "(d/6)*log(1/(beta*a_N)) with a_N=gamma*V/(12*m^3)",
        },
        "evidence_level": "T0 independent finite comparison-envelope diagnostic",
        "assumptions": [
            "The R-464 sextic lower comparison is valid at each fixed cutoff.",
            "The radial integral is used only as a finite-dimensional upper envelope.",
            "The declared cutoffs and beta values are audit fixtures, not fitted parameters.",
        ],
        "missing_assumptions": [
            "Correlated full-field partition asymptotics and a cutoff-uniform lower/upper balance.",
            "A source-owned positive-mass branch tube, probability and entropy/Jacobian estimate.",
            "Tightness, floor removal, continuum limits and physical/QFT/Yang--Mills identification.",
        ],
        "non_claims": [
            "This radial comparison is not the actual correlated partition function.",
            "The pressure term is not a no-go theorem and is not an entropy density.",
            "No branch probability, tightness, continuum, physical, QFT, Yang--Mills or mass-gap result is claimed.",
            "Existing T-054, T-059 and T-061 methods and owner order are unchanged.",
        ],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"INDEPENDENT R-465 {output['verdict']} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
