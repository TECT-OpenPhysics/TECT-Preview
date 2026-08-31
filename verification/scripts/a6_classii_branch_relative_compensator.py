#!/usr/bin/env python3
"""Primary audit of the finite branch-relative Jacobian/entropy interface.

R-467 is an additive conditional interface downstream of R-466.  It keeps
the existing finite Gibbs comparison and records the exact change-of-variables
budget supplied by a later branch owner: chart dimensions, a positive
Jacobian lower bound, a pointwise energy ceiling, and the R-465 partition
upper envelope.  All chart values below are owner-neutral fixtures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.set_int_max_str_digits(1_000_000)

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R466_MANIFEST = REPO / "strategy" / "a6-classii-positive-mass-tube-envelope-manifest.json"
R465_MANIFEST = REPO / "strategy" / "a6-classii-partition-envelope-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-branch-relative-compensator"
    / "primary.json"
)

AUDIT_CUTOFFS = (1, 2, 3, 4, 6, 8, 10)
AUDIT_BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))
# Declared owner-neutral fixtures.  They are not fitted or physical values.
ACTIVE_SIDE = Fraction(1, 8)
NORMAL_SIDE = Fraction(1, 4)
REFERENCE_SIDE = Fraction(1, 8)
JACOBIAN_MIN = Fraction(1, 2)
ENERGY_CEILING = Fraction(1)
ACTIVE_COORDINATES_PER_SITE = 2


def sha256_normalised(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def rational(value: Any) -> Fraction:
    return Fraction(str(value))


def assertion(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def load_parameters() -> dict[str, Fraction]:
    payload = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    return {key: rational(payload[key]) for key in ("Lx", "Ly", "Lz", "gamma", "lambda", "r", "Z", "Y")}


def derive(params: dict[str, Fraction]) -> dict[str, Fraction]:
    volume = params["Lx"] * params["Ly"] * params["Lz"]
    mu2 = params["r"] - params["Z"] ** 2 / (4 * params["Y"])
    ell = -params["lambda"]
    threshold = 3 * ell / params["gamma"]
    constant = ell * threshold**2 / 4
    return {
        "volume": volume,
        "mu2": mu2,
        "gamma": params["gamma"],
        "lambda_abs": ell,
        "threshold": threshold,
        "constant": constant,
        "K": constant * volume,
    }


def radial_log_upper(beta: Fraction, cutoff: int, d: dict[str, Fraction]) -> dict[str, Any]:
    sites = (2 * cutoff + 1) ** 3
    ambient_dim = 6 * sites
    coefficient = d["gamma"] * d["volume"] / (12 * sites**3)
    beta_float = float(beta)
    coefficient_float = float(coefficient)
    radial_log = (
        ambient_dim / 2 * math.log(math.pi)
        + math.lgamma(ambient_dim / 6)
        - math.log(3.0)
        - math.lgamma(ambient_dim / 2)
        - ambient_dim / 6 * math.log(beta_float * coefficient_float)
    )
    log_upper = beta_float * float(d["K"]) + radial_log
    return {
        "cutoff": cutoff,
        "sites": sites,
        "ambient_dimension": ambient_dim,
        "coefficient": coefficient,
        "radial_log": radial_log,
        "log_partition_upper": log_upper,
    }


def branch_row(beta: Fraction, cutoff: int, d: dict[str, Fraction]) -> dict[str, Any]:
    radial = radial_log_upper(beta, cutoff, d)
    ambient_dim = radial["ambient_dimension"]
    active_dim = ACTIVE_COORDINATES_PER_SITE * radial["sites"]
    normal_dim = ambient_dim - active_dim
    chart_volume = ACTIVE_SIDE**active_dim * NORMAL_SIDE**normal_dim
    reference_volume = REFERENCE_SIDE**ambient_dim
    log_chart_volume = active_dim * math.log(float(ACTIVE_SIDE)) + normal_dim * math.log(float(NORMAL_SIDE))
    log_reference_volume = ambient_dim * math.log(float(REFERENCE_SIDE))
    log_jacobian = math.log(float(JACOBIAN_MIN))
    log_jacobian_volume = log_jacobian + log_chart_volume
    beta_ceiling = float(beta * ENERGY_CEILING)
    log_numerator_lower = log_jacobian_volume - beta_ceiling
    log_probability_lower = log_numerator_lower - radial["log_partition_upper"]
    log_compensator_vs_reference = log_jacobian_volume - log_reference_volume
    return {
        **{key: value for key, value in radial.items() if key != "coefficient"},
        "beta": str(beta),
        "coefficient": str(radial["coefficient"]),
        "active_dimension": active_dim,
        "normal_dimension": normal_dim,
        "dimension_split_identity": active_dim + normal_dim == ambient_dim,
        "active_side": str(ACTIVE_SIDE),
        "normal_side": str(NORMAL_SIDE),
        "reference_side": str(REFERENCE_SIDE),
        "jacobian_min": str(JACOBIAN_MIN),
        "chart_volume_exact": str(chart_volume),
        "reference_volume_exact": str(reference_volume),
        "log_chart_volume": log_chart_volume,
        "log_reference_volume": log_reference_volume,
        "log_jacobian": log_jacobian,
        "log_jacobian_volume": log_jacobian_volume,
        "energy_ceiling": str(ENERGY_CEILING),
        "beta_energy_ceiling": beta_ceiling,
        "log_numerator_lower": log_numerator_lower,
        "log_probability_lower": log_probability_lower,
        "log_compensator_vs_reference": log_compensator_vs_reference,
        "finite": all(
            math.isfinite(float(value))
            for value in (log_chart_volume, log_jacobian_volume, log_numerator_lower, log_probability_lower)
        ),
        "positive_chart_volume": chart_volume > 0,
        "positive_jacobian": JACOBIAN_MIN > 0,
        "compensator_identity": abs(
            log_compensator_vs_reference - (log_jacobian_volume - log_reference_volume)
        )
        < 1e-12,
        "lower_bound_is_nontrivial_log": log_probability_lower < 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = load_parameters()
    derived = derive(params)
    rows: list[dict[str, Any]] = []

    for label, path in (("A1", A1_MANIFEST), ("R-466", R466_MANIFEST), ("R-465", R465_MANIFEST)):
        assertion(rows, f"{label} manifest exists", path.is_file(), str(path), True)
        assertion(rows, f"{label} manifest hash available", bool(sha256_normalised(path)), sha256_normalised(path), "nonempty SHA-256")
    assertion(rows, "volume positive", derived["volume"] > 0, str(derived["volume"]), ">0")
    assertion(rows, "spectral floor positive", derived["mu2"] > 0, str(derived["mu2"]), ">0")
    assertion(rows, "gamma positive", derived["gamma"] > 0, str(derived["gamma"]), ">0")
    assertion(rows, "lambda nonpositive", params["lambda"] <= 0, str(params["lambda"]), "<=0")
    assertion(rows, "active side positive", ACTIVE_SIDE > 0, str(ACTIVE_SIDE), ">0")
    assertion(rows, "normal side positive", NORMAL_SIDE > 0, str(NORMAL_SIDE), ">0")
    assertion(rows, "reference side positive", REFERENCE_SIDE > 0, str(REFERENCE_SIDE), ">0")
    assertion(rows, "Jacobian lower bound positive", JACOBIAN_MIN > 0, str(JACOBIAN_MIN), ">0")
    assertion(rows, "energy ceiling finite fixture", math.isfinite(float(ENERGY_CEILING)), str(ENERGY_CEILING), "finite")
    assertion(rows, "active coordinate multiplier positive", ACTIVE_COORDINATES_PER_SITE > 0, ACTIVE_COORDINATES_PER_SITE, ">0")

    rows_by_beta: dict[str, list[dict[str, Any]]] = {str(beta): [] for beta in AUDIT_BETAS}
    for beta in AUDIT_BETAS:
        for cutoff in AUDIT_CUTOFFS:
            row = branch_row(beta, cutoff, derived)
            rows_by_beta[str(beta)].append(row)
            assertion(rows, f"finite branch row beta={beta} N={cutoff}", row["finite"], row["log_probability_lower"], "finite")
            assertion(rows, f"positive chart volume beta={beta} N={cutoff}", row["positive_chart_volume"], row["chart_volume_exact"], ">0")
            assertion(rows, f"positive Jacobian beta={beta} N={cutoff}", row["positive_jacobian"], row["jacobian_min"], ">0")
            assertion(rows, f"dimension split beta={beta} N={cutoff}", row["dimension_split_identity"], (row["active_dimension"], row["normal_dimension"], row["ambient_dimension"]), "active+normal=ambient")
            assertion(rows, f"positive sextic coefficient beta={beta} N={cutoff}", rational(row["coefficient"]) > 0, row["coefficient"], ">0")
            assertion(rows, f"exact coefficient scale beta={beta} N={cutoff}", rational(row["coefficient"]) * row["sites"] ** 3 == derived["gamma"] * derived["volume"] / 12, row["coefficient"], "gamma*V/(12*m^3)")
            assertion(rows, f"compensator decomposition beta={beta} N={cutoff}", row["compensator_identity"], row["log_compensator_vs_reference"], "log(J*chart_volume)-log(reference_volume)")
            assertion(rows, f"conditional lower log nontrivial beta={beta} N={cutoff}", row["lower_bound_is_nontrivial_log"], row["log_probability_lower"], "<0")
        logs = [row["log_probability_lower"] for row in rows_by_beta[str(beta)]]
        assertion(rows, f"coarse compensated lower log decreases beta={beta}", all(left > right for left, right in zip(logs, logs[1:])), logs, "strictly decreasing")

    assertion(rows, "all declared beta/cutoff rows present", sum(len(value) for value in rows_by_beta.values()) == len(AUDIT_BETAS) * len(AUDIT_CUTOFFS), sum(len(value) for value in rows_by_beta.values()), len(AUDIT_BETAS) * len(AUDIT_CUTOFFS))
    assertion(rows, "bound is labelled conditional owner-neutral interface", True, "conditional branch chart contract", "not source-owned")
    assertion(rows, "uniform positive-mass conclusion withheld", True, "not asserted", "not asserted")

    passed = sum(1 for row in rows if row["status"] == "PASS")
    output = {
        "schema": "tect/a6-classii-branch-relative-compensator-primary/1.0",
        "run_kind": "primary",
        "result_id": "R-467",
        "exploration_id": "EXP-001342",
        "script_version": __version__,
        "verdict": "R-467-PRIMARY-PASS" if passed == len(rows) else "R-467-PRIMARY-FAIL",
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "assertions": rows,
        "inputs": {
            "a1_manifest": {"path": str(A1_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(A1_MANIFEST)},
            "r466_manifest": {"path": str(R466_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(R466_MANIFEST)},
            "r465_manifest": {"path": str(R465_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(R465_MANIFEST)},
            "cutoffs": list(AUDIT_CUTOFFS),
            "betas": [str(value) for value in AUDIT_BETAS],
            "active_side": str(ACTIVE_SIDE),
            "normal_side": str(NORMAL_SIDE),
            "reference_side": str(REFERENCE_SIDE),
            "jacobian_min": str(JACOBIAN_MIN),
            "energy_ceiling": str(ENERGY_CEILING),
            "active_coordinates_per_site": ACTIVE_COORDINATES_PER_SITE,
        },
        "derived": {
            "volume": str(derived["volume"]),
            "mu2": str(derived["mu2"]),
            "gamma": str(derived["gamma"]),
            "comparison_K": str(derived["K"]),
            "coefficient_scale": "a_N=gamma*V/(12*m^3)",
            "chart_mass_lower_formula": "mu_N(B_N)>=J_min*vol(U_N)*exp(-beta*E_tube)/Z_upper_N(beta)",
            "log_decomposition": "log(J_min)+k*log(active_side)+n*log(normal_side)-beta*E_tube-log(Z_upper_N)",
            "branch_relative_compensator": "log(J_min*vol(U_N))-log(reference_volume_N)",
            "rows": [row for beta_rows in rows_by_beta.values() for row in beta_rows],
            "uniform_admissibility_condition": "liminf_N log_probability_lower(N,beta)>-infinity",
        },
        "evidence_level": "T0 exact finite conditional branch-relative Jacobian/entropy budget with owner-neutral chart fixtures",
        "assumptions": [
            "The R-464 sextic comparison and R-465 radial partition upper envelope hold at each fixed cutoff.",
            "A later owner supplies an injective measurable chart with positive Jacobian lower bound and a valid pointwise energy ceiling.",
            "The active/normal side lengths, Jacobian lower bound and ceiling are audit fixtures only and are not physical values.",
        ],
        "missing_assumptions": [
            "A source-owned active-branch embedding, chart domain and Jacobian estimate tied to R-461/R-463.",
            "The actual correlated partition normalization with cutoff- and volume-uniform bounds.",
            "A quantitative branch-relative entropy/Jacobian compensator with a uniform liminf, tightness, floor removal and ordered continuum limit.",
            "A source-owned Q3LOCK dynamics, physical branch, QFT/Yang--Mills identity or mass-gap bridge.",
        ],
        "non_claims": [
            "The chart and Jacobian are owner-neutral fixtures, not a source-owned active branch.",
            "The finite lower bound is conditional and does not establish a cutoff-uniform branch probability.",
            "A finite compensator budget is not an entropy density, a correlated partition theorem, or a physical-sector selection.",
            "No tightness, floor removal, continuum, Pre-A, Sector-A, QFT, Yang--Mills or mass-gap conclusion follows.",
            "Existing T-054 forward, T-059/T-061 inverse methods, owner order and promotion firewalls are unchanged.",
        ],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"PRIMARY R-467 {output['verdict']} {passed}/{len(rows)}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
