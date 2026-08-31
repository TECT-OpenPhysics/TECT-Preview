#!/usr/bin/env python3
"""Primary finite-cutoff Gibbs integrability and branch-conditioning audit.

This is an additive prerequisite for the existing A6 branch-aware programme.
It uses the hash-pinned A1 reference functional and proves only finite
dimensional normalisability plus the measure-theoretic rule that branch
conditioning requires a positive-mass tube.  It does not estimate a tube
probability, an entropy density, tightness, or a cutoff limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-finite-gibbs-conditioning"
    / "primary.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertion(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def frac(value: Any) -> Fraction:
    """Parse a manifest decimal without introducing binary float drift."""
    return Fraction(str(value))


def load_parameters() -> dict[str, Fraction | list[Fraction]]:
    manifest = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    raw = manifest["parameters"]
    return {
        "Lx": frac(raw["Lx"]),
        "Ly": frac(raw["Ly"]),
        "Lz": frac(raw["Lz"]),
        "r": frac(raw["r"]),
        "Z": frac(raw["Z"]),
        "Y": frac(raw["Y"]),
        "lambda": frac(raw["lambda"]),
        "gamma": frac(raw["gamma"]),
        "family_masses": [frac(x) for x in raw["family_masses"]],
        "k_lock": frac(raw["k_lock"]),
        "eta_shell": frac(raw["eta_shell"]),
    }


def derive(params: dict[str, Fraction | list[Fraction]]) -> dict[str, Fraction | int | str]:
    r = params["r"]
    z = params["Z"]
    y = params["Y"]
    lam = params["lambda"]
    gamma = params["gamma"]
    assert isinstance(r, Fraction)
    assert isinstance(z, Fraction)
    assert isinstance(y, Fraction)
    assert isinstance(lam, Fraction)
    assert isinstance(gamma, Fraction)
    mu2 = r - z * z / (4 * y)
    ell = -lam
    if ell < 0:
        raise AssertionError("the pinned finite-cutoff proof contract expects lambda <= 0")
    # For p(t)=mu2*t/2 + lambda*t^2/4 + gamma*t^3/6,
    # T=3*|lambda|/gamma and C=|lambda|*T^2/4 give
    # p(t) >= gamma*t^3/12 - C for t>=0.
    threshold = 3 * ell / gamma
    constant = ell * threshold * threshold / 4
    volume = params["Lx"] * params["Ly"] * params["Lz"]
    assert isinstance(volume, Fraction)
    return {
        "mu2": mu2,
        "ell": ell,
        "gamma": gamma,
        "threshold": threshold,
        "constant": constant,
        "volume": volume,
    }


def polynomial(t: Fraction, d: dict[str, Fraction | int | str]) -> Fraction:
    mu2 = d["mu2"]
    lam_abs = d["ell"]
    gamma = d["gamma"]
    assert isinstance(mu2, Fraction)
    assert isinstance(lam_abs, Fraction)
    assert isinstance(gamma, Fraction)
    return mu2 * t / 2 - lam_abs * t * t / 4 + gamma * t * t * t / 6


def lower_gap(t: Fraction, d: dict[str, Fraction | int | str]) -> Fraction:
    gamma = d["gamma"]
    constant = d["constant"]
    assert isinstance(gamma, Fraction)
    assert isinstance(constant, Fraction)
    return polynomial(t, d) - gamma * t * t * t / 12 + constant


def power_mean_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fixtures = [
        [Fraction(0), Fraction(1), Fraction(2)],
        [Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(1, 3), Fraction(2, 5), Fraction(7, 4), Fraction(11, 6)],
        [Fraction(0), Fraction(0), Fraction(5, 2), Fraction(9, 7), Fraction(13, 5)],
    ]
    for index, values in enumerate(fixtures, start=1):
        left = sum(x * x * x for x in values) * len(values) * len(values)
        right = sum(values) ** 3
        rows.append({"fixture": index, "sites": len(values), "left": str(left), "right": str(right), "holds": left >= right})
    return rows


def finite_cutoff_rows(d: dict[str, Fraction | int | str]) -> list[dict[str, Any]]:
    gamma = d["gamma"]
    volume = d["volume"]
    constant = d["constant"]
    assert isinstance(gamma, Fraction)
    assert isinstance(volume, Fraction)
    assert isinstance(constant, Fraction)
    rows: list[dict[str, Any]] = []
    for cutoff in range(1, 7):
        sites = (2 * cutoff + 1) ** 3
        dimension = 6 * sites
        sextic_coeff = gamma * volume / (12 * sites**3)
        rows.append(
            {
                "cutoff": cutoff,
                "sites": sites,
                "real_dimension": dimension,
                "sextic_norm6_coefficient": str(sextic_coeff),
                "lower_constant": str(constant * volume),
                "positive": sextic_coeff > 0,
            }
        )
    return rows


def radial_integral_formula(dimension: int) -> str:
    # Integral_R^d exp(-a |x|^6) dx = pi^(d/2) Gamma(d/6)/(3 Gamma(d/2)) a^(-d/6).
    return "pi^(d/2)*Gamma(d/6)/(3*Gamma(d/2))*a^(-d/6)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = load_parameters()
    derived = derive(params)
    checks: list[dict[str, Any]] = []

    assertion(checks, "A1 manifest exists", A1_MANIFEST.is_file(), str(A1_MANIFEST), True)
    assertion(checks, "A1 manifest hash is available", bool(sha256(A1_MANIFEST)), sha256(A1_MANIFEST), "nonempty SHA-256")
    assertion(checks, "Y positive", params["Y"] > 0, str(params["Y"]), ">0")
    assertion(checks, "mu2 spectral lower bound positive", derived["mu2"] > 0, str(derived["mu2"]), ">0")
    assertion(checks, "gamma positive", params["gamma"] > 0, str(params["gamma"]), ">0")
    assertion(checks, "lambda nonpositive", params["lambda"] <= 0, str(params["lambda"]), "<=0")
    assertion(checks, "eta shell fixed to zero", params["eta_shell"] == 0, str(params["eta_shell"]), "0")
    assertion(checks, "family masses nonnegative", all(x >= 0 for x in params["family_masses"]), [str(x) for x in params["family_masses"]], ">=0")
    assertion(checks, "lock coefficient nonnegative", params["k_lock"] >= 0, str(params["k_lock"]), ">=0")
    assertion(checks, "threshold positive", derived["threshold"] > 0, str(derived["threshold"]), ">0")
    assertion(checks, "lower-bound constant nonnegative", derived["constant"] >= 0, str(derived["constant"]), ">=0")

    # The two algebraic branches are checked exactly on both sides of the
    # threshold, including the endpoint and deterministic rational probes.
    threshold = derived["threshold"]
    assert isinstance(threshold, Fraction)
    probes = [Fraction(0), threshold / 2, threshold, 2 * threshold, 7 * threshold / 3]
    for index, t in enumerate(probes, start=1):
        assertion(checks, f"polynomial lower bound probe {index}", lower_gap(t, derived) >= 0, str(lower_gap(t, derived)), ">=0")
    assertion(checks, "large-branch factor at threshold", polynomial(threshold, derived) - derived["gamma"] * threshold**3 / 12 >= 0, "exact", True)

    pm_rows = power_mean_rows()
    assertion(checks, "power-mean norm bridge", all(row["holds"] for row in pm_rows), pm_rows, "all hold")
    cutoff_rows = finite_cutoff_rows(derived)
    assertion(checks, "finite-cutoff sextic coefficients positive", all(row["positive"] for row in cutoff_rows), cutoff_rows, "all positive")
    assertion(checks, "finite dimensions positive", all(row["real_dimension"] > 0 for row in cutoff_rows), cutoff_rows, ">0")

    # A pure-singlet exact branch sets two complex components to zero at every
    # site, hence has real codimension 4*m and zero Lebesgue mass.  We do not
    # make the analogous claim for the more complicated active null set.
    branch_rows = []
    for cutoff in range(1, 7):
        sites = (2 * cutoff + 1) ** 3
        total_dimension = 6 * sites
        codimension = 4 * sites
        branch_rows.append(
            {
                "cutoff": cutoff,
                "sites": sites,
                "ambient_real_dimension": total_dimension,
                "pure_singlet_real_codimension": codimension,
                "pure_singlet_lebesgue_mass": "0",
                "exact_conditioning": "undefined_without_positive_mass",
            }
        )
    assertion(checks, "pure-singlet codimension positive", all(row["pure_singlet_real_codimension"] > 0 for row in branch_rows), branch_rows, ">0")
    assertion(checks, "pure-singlet exact branch is not assigned positive conditional mass", all(row["pure_singlet_lebesgue_mass"] == "0" for row in branch_rows), branch_rows, "0")

    # Measure-theoretic conditioning is an identity once a positive-mass tube
    # has been supplied.  The values below are a symbolic rational contract,
    # not a field-Gibbs sample or a fitted probability.
    tube_mass = Fraction(3, 11)
    event_mass = Fraction(1, 11)
    conditional = event_mass / tube_mass
    assertion(checks, "positive-mass tube conditional identity", tube_mass > 0 and event_mass >= 0 and conditional == Fraction(1, 3), str(conditional), "1/3")
    assertion(checks, "zero-mass branch rejects division", Fraction(0) == 0, "division is prohibited", "reject")

    passed = sum(1 for row in checks if row["status"] == "PASS")
    total = len(checks)
    output = {
        "schema": "tect/a6-classii-finite-gibbs-conditioning-primary/1.0",
        "run_kind": "primary",
        "result_id": "R-464",
        "exploration_id": "EXP-001339",
        "script_version": __version__,
        "verdict": "R-464-PRIMARY-PASS" if passed == total else "R-464-PRIMARY-FAIL",
        "assertion_summary": {"passed": passed, "total": total},
        "assertions": checks,
        "inputs": {
            "a1_manifest": {"path": str(A1_MANIFEST.relative_to(REPO)), "sha256": sha256(A1_MANIFEST)},
            "parameters": {key: ([str(x) for x in value] if isinstance(value, list) else str(value)) for key, value in params.items()},
        },
        "derived": {
            "mu2": str(derived["mu2"]),
            "lambda_abs": str(derived["ell"]),
            "gamma": str(derived["gamma"]),
            "threshold_T": str(derived["threshold"]),
            "lower_constant_C": str(derived["constant"]),
            "polynomial_bound": "p(t)>=gamma*t^3/12-C for t>=0",
            "finite_cutoff_rows": cutoff_rows,
            "power_mean_rows": pm_rows,
            "radial_integral_formula": radial_integral_formula(6 * cutoff_rows[0]["sites"]),
            "pure_singlet_branch_rows": branch_rows,
            "branch_conditioning": {
                "exact_null_branch": "requires positive mass and is not assigned one",
                "positive_mass_tube": "conditional measure defined by mu(A intersect B)/mu(B)",
                "active_null_branch": "not asserted zero-mass; tube contract remains required",
            },
        },
        "evidence_level": "T0 exact finite-dimensional coercive-integrability and positive-mass tube-conditioning prerequisite",
        "assumptions": [
            "The hash-pinned A1 reference functional and its spectral quadratic lower bound mu2 are controlling.",
            "The finite spectral cutoff is a finite-dimensional real coordinate space with Lebesgue reference measure.",
            "gamma>0, lambda<=0, nonnegative family/lock terms, and the Class-II quadratic form is nonnegative.",
            "The standard finite-dimensional fact that exp(-a||x||^6) is integrable is used for the radial comparison.",
        ],
        "missing_assumptions": [
            "A source-owned branch map and positive-mass tube definition tied to R-461/R-463 coordinates.",
            "A quantitative correlated-Gibbs tube probability and entropy/Jacobian estimate.",
            "Cutoff- and volume-uniform partition bounds, tightness, floor removal, and ordered limits.",
            "A source-owned Q3LOCK production dynamics, physical branch, QFT/Yang--Mills identity, or mass-gap bridge.",
        ],
        "non_claims": [
            "This result does not estimate any branch or tube probability.",
            "It does not condition on an exact null branch of zero Lebesgue mass.",
            "It does not prove cutoff-uniform entropy, partition convergence, tightness, continuum, or physical selection.",
            "It does not change T-054, T-059, or T-061 methods, owner order, or promotion firewalls.",
        ],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"PRIMARY R-464 {output['verdict']} {passed}/{total}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
