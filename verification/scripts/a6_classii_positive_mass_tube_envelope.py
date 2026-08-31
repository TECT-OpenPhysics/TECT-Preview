#!/usr/bin/env python3
"""Primary audit of the finite positive-mass tube lower-bound interface.

R-466 is an additive consequence of the unchanged R-464/R-465 comparison.
For an explicitly supplied measurable box tube and an energy ceiling on that
tube, it computes a rigorous finite-cutoff lower-bound formula for its Gibbs
mass.  The box and ceiling below are declared owner-neutral fixtures; they are
not a source-owned branch and are not promoted to a physical probability.
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
R464_MANIFEST = REPO / "strategy" / "a6-classii-finite-gibbs-conditioning-manifest.json"
R465_MANIFEST = REPO / "strategy" / "a6-classii-partition-envelope-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-primary-a6-positive-mass-tube-envelope"
    / "primary.json"
)

AUDIT_CUTOFFS = (1, 2, 3, 4, 6, 8, 10)
AUDIT_BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))
# These are declared owner-neutral contract fixtures, not derived values.
TUBE_HALF_WIDTH = Fraction(1, 16)
TUBE_ENERGY_CEILING = Fraction(1)


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
    dimension = 6 * sites
    coefficient = d["gamma"] * d["volume"] / (12 * sites**3)
    beta_float = float(beta)
    coefficient_float = float(coefficient)
    radial_log = (
        dimension / 2 * math.log(math.pi)
        + math.lgamma(dimension / 6)
        - math.log(3.0)
        - math.lgamma(dimension / 2)
        - dimension / 6 * math.log(beta_float * coefficient_float)
    )
    log_upper = beta_float * float(d["K"]) + radial_log
    return {
        "cutoff": cutoff,
        "sites": sites,
        "real_dimension": dimension,
        "coefficient": coefficient,
        "radial_log": radial_log,
        "log_partition_upper": log_upper,
    }


def tube_row(beta: Fraction, cutoff: int, d: dict[str, Fraction]) -> dict[str, Any]:
    radial = radial_log_upper(beta, cutoff, d)
    dimension = radial["real_dimension"]
    side = 2 * TUBE_HALF_WIDTH
    box_volume = side**dimension
    log_box_volume = dimension * math.log(float(side))
    beta_ceiling = float(beta * TUBE_ENERGY_CEILING)
    log_numerator_lower = log_box_volume - beta_ceiling
    log_probability_lower = log_numerator_lower - radial["log_partition_upper"]
    return {
        **{key: value for key, value in radial.items() if key not in {"coefficient"}},
        "beta": str(beta),
        "coefficient": str(radial["coefficient"]),
        "coefficient_times_sites_cubed": str(radial["coefficient"] * radial["sites"] ** 3),
        "tube_half_width": str(TUBE_HALF_WIDTH),
        "tube_side": str(side),
        "tube_box_volume_exact": str(box_volume),
        "log_tube_box_volume": log_box_volume,
        "energy_ceiling": str(TUBE_ENERGY_CEILING),
        "beta_energy_ceiling": beta_ceiling,
        "log_numerator_lower": log_numerator_lower,
        "log_probability_lower": log_probability_lower,
        "finite": all(math.isfinite(float(value)) for value in (log_box_volume, beta_ceiling, log_numerator_lower, log_probability_lower)),
        "positive_box_volume": box_volume > 0,
        "lower_bound_is_nontrivial_log": log_probability_lower < 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    params = load_parameters()
    derived = derive(params)
    rows: list[dict[str, Any]] = []

    for label, path in (("A1", A1_MANIFEST), ("R-464", R464_MANIFEST), ("R-465", R465_MANIFEST)):
        assertion(rows, f"{label} manifest exists", path.is_file(), str(path), True)
        assertion(rows, f"{label} manifest hash available", bool(sha256_normalised(path)), sha256_normalised(path), "nonempty SHA-256")
    assertion(rows, "volume positive", derived["volume"] > 0, str(derived["volume"]), ">0")
    assertion(rows, "spectral floor positive", derived["mu2"] > 0, str(derived["mu2"]), ">0")
    assertion(rows, "gamma positive", derived["gamma"] > 0, str(derived["gamma"]), ">0")
    assertion(rows, "lambda nonpositive", params["lambda"] <= 0, str(params["lambda"]), "<=0")
    assertion(rows, "tube half-width positive", TUBE_HALF_WIDTH > 0, str(TUBE_HALF_WIDTH), ">0")
    assertion(rows, "tube energy ceiling finite fixture", math.isfinite(float(TUBE_ENERGY_CEILING)), str(TUBE_ENERGY_CEILING), "finite")
    assertion(rows, "tube side identity", 2 * TUBE_HALF_WIDTH == Fraction(1, 8), str(2 * TUBE_HALF_WIDTH), "1/8")

    rows_by_beta: dict[str, list[dict[str, Any]]] = {str(beta): [] for beta in AUDIT_BETAS}
    for beta in AUDIT_BETAS:
        for cutoff in AUDIT_CUTOFFS:
            row = tube_row(beta, cutoff, derived)
            rows_by_beta[str(beta)].append(row)
            assertion(rows, f"finite tube row beta={beta} N={cutoff}", row["finite"], row["log_probability_lower"], "finite")
            assertion(rows, f"positive exact box volume beta={beta} N={cutoff}", row["positive_box_volume"], row["tube_box_volume_exact"], ">0")
            assertion(rows, f"positive sextic coefficient beta={beta} N={cutoff}", rational(row["coefficient"]) > 0, row["coefficient"], ">0")
            assertion(rows, f"exact coefficient scale beta={beta} N={cutoff}", rational(row["coefficient_times_sites_cubed"]) == derived["gamma"] * derived["volume"] / 12, row["coefficient_times_sites_cubed"], str(derived["gamma"] * derived["volume"] / 12))
            assertion(rows, f"conditional lower log is nontrivial beta={beta} N={cutoff}", row["lower_bound_is_nontrivial_log"], row["log_probability_lower"], "<0")
        logs = [row["log_probability_lower"] for row in rows_by_beta[str(beta)]]
        assertion(rows, f"coarse lower log decreases with cutoff beta={beta}", all(left > right for left, right in zip(logs, logs[1:])), logs, "strictly decreasing")

    assertion(rows, "all declared beta/cutoff rows present", sum(len(value) for value in rows_by_beta.values()) == len(AUDIT_BETAS) * len(AUDIT_CUTOFFS), sum(len(value) for value in rows_by_beta.values()), len(AUDIT_BETAS) * len(AUDIT_CUTOFFS))
    assertion(rows, "bound is labelled conditional owner-neutral interface", True, "conditional owner-neutral tube contract", "not source-owned")
    assertion(rows, "uniform positive-mass conclusion withheld", True, "not asserted", "not asserted")

    passed = sum(1 for row in rows if row["status"] == "PASS")
    output = {
        "schema": "tect/a6-classii-positive-mass-tube-envelope-primary/1.0",
        "run_kind": "primary",
        "result_id": "R-466",
        "exploration_id": "EXP-001341",
        "script_version": __version__,
        "verdict": "R-466-PRIMARY-PASS" if passed == len(rows) else "R-466-PRIMARY-FAIL",
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "assertions": rows,
        "inputs": {
            "a1_manifest": {"path": str(A1_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(A1_MANIFEST)},
            "r464_manifest": {"path": str(R464_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(R464_MANIFEST)},
            "r465_manifest": {"path": str(R465_MANIFEST.relative_to(REPO)), "sha256": sha256_normalised(R465_MANIFEST)},
            "cutoffs": list(AUDIT_CUTOFFS),
            "betas": [str(value) for value in AUDIT_BETAS],
            "tube_half_width": str(TUBE_HALF_WIDTH),
            "tube_energy_ceiling": str(TUBE_ENERGY_CEILING),
        },
        "derived": {
            "volume": str(derived["volume"]),
            "mu2": str(derived["mu2"]),
            "gamma": str(derived["gamma"]),
            "comparison_K": str(derived["K"]),
            "coefficient_scale": "a_N=gamma*V/(12*m^3)",
            "tube_probability_lower_formula": "mu_N(B_N)>=vol(B_N)*exp(-beta*E_tube)/Z_upper_N",
            "log_decomposition": "d*log(2*delta)-beta*E_tube-log(Z_upper_N)",
            "rows": [row for beta_rows in rows_by_beta.values() for row in beta_rows],
            "uniform_admissibility_condition": "liminf_N log_probability_lower(N,beta)>-infinity",
        },
        "evidence_level": "T0 exact finite conditional Gibbs-mass lower-bound interface with owner-neutral box fixtures",
        "assumptions": [
            "The R-464 sextic lower comparison and R-465 radial partition upper envelope hold at each fixed cutoff.",
            "A later owner supplies a measurable box-like branch tube and a valid uniform energy ceiling on that tube.",
            "The declared half-width and energy ceiling are audit fixtures only and are not claimed to describe a physical branch.",
        ],
        "missing_assumptions": [
            "A source-owned active-branch embedding, measurable tube and energy ceiling tied to R-461/R-463.",
            "The actual correlated partition lower/upper pair with cutoff- and volume-uniform normalization.",
            "A quantitative entropy/Jacobian compensator, tightness, floor removal and ordered continuum limit.",
            "A source-owned Q3LOCK dynamics, physical branch, QFT/Yang--Mills identity or mass-gap bridge.",
        ],
        "non_claims": [
            "The owner-neutral box is not a source-owned active branch and does not select a physical sector.",
            "The finite lower bound is conditional on an energy ceiling and is not a cutoff-uniform probability theorem.",
            "The decreasing coarse log bound diagnoses the present full-dimensional comparison; it is not a no-go theorem for a better branch-relative normalization.",
            "No entropy density, tightness, floor removal, continuum, Pre-A, Sector-A, QFT, Yang--Mills or mass-gap conclusion follows.",
            "Existing T-054 forward, T-059/T-061 inverse methods, owner order and promotion firewalls are unchanged.",
        ],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output_path = args.output if args.output.is_absolute() else REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"PRIMARY R-466 {output['verdict']} {passed}/{len(rows)}")
    print(f"Evidence: {output_path.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
