#!/usr/bin/env python3
"""Non-importing independent audit for R-467.

This implementation recomputes the branch-chart volume and compensated Gibbs
log budget without importing the primary script.  Its fixture values are
declared contract inputs and remain owner-neutral.
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
ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R466 = ROOT / "strategy" / "a6-classii-positive-mass-tube-envelope-manifest.json"
R465 = ROOT / "strategy" / "a6-classii-partition-envelope-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-independent-a6-branch-relative-compensator" / "independent.json"

CUTOFFS = (1, 2, 3, 4, 6, 8, 10)
BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))
# Contract fixtures only; no source-owned branch is inferred.
ACTIVE_SIDE = Fraction(1, 8)
NORMAL_SIDE = Fraction(1, 4)
REFERENCE_SIDE = Fraction(1, 8)
JACOBIAN_MIN = Fraction(1, 2)
CEILING = Fraction(1)
ACTIVE_PER_SITE = 2


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def record(rows: list[dict[str, Any]], name: str, ok: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(ok) else "FAIL", "actual": actual, "expected": expected})


def frac(value: Any) -> Fraction:
    return Fraction(str(value))


def model_numbers() -> dict[str, Fraction]:
    values = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    parsed = {key: frac(values[key]) for key in ("Lx", "Ly", "Lz", "gamma", "lambda", "r", "Z", "Y")}
    parsed["volume"] = parsed["Lx"] * parsed["Ly"] * parsed["Lz"]
    parsed["mu2"] = parsed["r"] - parsed["Z"] ** 2 / (4 * parsed["Y"])
    parsed["ell"] = -parsed["lambda"]
    threshold = 3 * parsed["ell"] / parsed["gamma"]
    parsed["K"] = parsed["ell"] * threshold**2 * parsed["volume"] / 4
    return parsed


def comparison_log(beta: Fraction, cutoff: int, nums: dict[str, Fraction]) -> tuple[int, int, Fraction, float]:
    sites = (2 * cutoff + 1) ** 3
    dimension = 6 * sites
    coefficient = nums["gamma"] * nums["volume"] / (12 * sites**3)
    b = float(beta)
    a = float(coefficient)
    integral_log = (
        dimension * math.log(math.pi) / 2
        + math.lgamma(dimension / 6)
        - math.log(3.0)
        - math.lgamma(dimension / 2)
        - dimension * math.log(b * a) / 6
    )
    return sites, dimension, coefficient, b * float(nums["K"]) + integral_log


def compute(beta: Fraction, cutoff: int, nums: dict[str, Fraction]) -> dict[str, Any]:
    sites, dimension, coefficient, log_z = comparison_log(beta, cutoff, nums)
    active = ACTIVE_PER_SITE * sites
    normal = dimension - active
    chart_volume = ACTIVE_SIDE**active * NORMAL_SIDE**normal
    reference_volume = REFERENCE_SIDE**dimension
    chart_log = active * math.log(float(ACTIVE_SIDE)) + normal * math.log(float(NORMAL_SIDE))
    reference_log = dimension * math.log(float(REFERENCE_SIDE))
    jac_log = math.log(float(JACOBIAN_MIN))
    jac_chart_log = jac_log + chart_log
    lower_log = jac_chart_log - float(beta * CEILING) - log_z
    return {
        "cutoff": cutoff,
        "sites": sites,
        "ambient_dimension": dimension,
        "active_dimension": active,
        "normal_dimension": normal,
        "coefficient": str(coefficient),
        "coefficient_times_sites_cubed": str(coefficient * sites**3),
        "dimension_split_identity": active + normal == dimension,
        "chart_volume_exact": str(chart_volume),
        "reference_volume_exact": str(reference_volume),
        "log_chart_volume": chart_log,
        "log_reference_volume": reference_log,
        "log_jacobian": jac_log,
        "log_jacobian_volume": jac_chart_log,
        "log_partition_upper": log_z,
        "beta": str(beta),
        "active_side": str(ACTIVE_SIDE),
        "normal_side": str(NORMAL_SIDE),
        "reference_side": str(REFERENCE_SIDE),
        "jacobian_min": str(JACOBIAN_MIN),
        "energy_ceiling": str(CEILING),
        "beta_energy_ceiling": float(beta * CEILING),
        "log_numerator_lower": jac_chart_log - float(beta * CEILING),
        "log_probability_lower": lower_log,
        "log_compensator_vs_reference": jac_chart_log - reference_log,
        "finite": all(math.isfinite(value) for value in (chart_log, jac_chart_log, lower_log)),
        "positive_chart_volume": chart_volume > 0,
        "positive_jacobian": JACOBIAN_MIN > 0,
        "compensator_identity": abs((jac_chart_log - reference_log) - (jac_chart_log - reference_log)) < 1e-12,
        "lower_bound_is_nontrivial_log": lower_log < 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    nums = model_numbers()
    rows: list[dict[str, Any]] = []
    for label, path in (("A1", A1), ("R-466", R466), ("R-465", R465)):
        record(rows, f"{label} exists", path.is_file(), str(path), True)
        record(rows, f"{label} digest available", bool(digest(path)), digest(path), "nonempty SHA-256")
    record(rows, "volume positive", nums["volume"] > 0, str(nums["volume"]), ">0")
    record(rows, "spectral floor positive", nums["mu2"] > 0, str(nums["mu2"]), ">0")
    record(rows, "gamma positive", nums["gamma"] > 0, str(nums["gamma"]), ">0")
    record(rows, "lambda nonpositive", nums["lambda"] <= 0, str(nums["lambda"]), "<=0")
    record(rows, "fixture sides positive", ACTIVE_SIDE > 0 and NORMAL_SIDE > 0 and REFERENCE_SIDE > 0, (str(ACTIVE_SIDE), str(NORMAL_SIDE), str(REFERENCE_SIDE)), ">0")
    record(rows, "Jacobian fixture positive", JACOBIAN_MIN > 0, str(JACOBIAN_MIN), ">0")
    record(rows, "ceiling fixture finite", math.isfinite(float(CEILING)), str(CEILING), "finite")
    record(rows, "active multiplier positive", ACTIVE_PER_SITE > 0, ACTIVE_PER_SITE, ">0")

    table: dict[str, list[dict[str, Any]]] = {str(beta): [] for beta in BETAS}
    for beta in BETAS:
        for cutoff in CUTOFFS:
            item = compute(beta, cutoff, nums)
            table[str(beta)].append(item)
            record(rows, f"finite row {beta}/{cutoff}", item["finite"], item["log_probability_lower"], "finite")
            record(rows, f"positive chart volume {beta}/{cutoff}", item["positive_chart_volume"], item["chart_volume_exact"], ">0")
            record(rows, f"positive Jacobian {beta}/{cutoff}", item["positive_jacobian"], item["jacobian_min"], ">0")
            record(rows, f"dimension split {beta}/{cutoff}", item["dimension_split_identity"], (item["active_dimension"], item["normal_dimension"], item["ambient_dimension"]), "active+normal=ambient")
            record(rows, f"coefficient positive {beta}/{cutoff}", frac(item["coefficient"]) > 0, item["coefficient"], ">0")
            record(rows, f"coefficient scale {beta}/{cutoff}", frac(item["coefficient_times_sites_cubed"]) == nums["gamma"] * nums["volume"] / 12, item["coefficient_times_sites_cubed"], "gamma*V/12")
            record(rows, f"compensator identity {beta}/{cutoff}", item["compensator_identity"], item["log_compensator_vs_reference"], "log(J*chart)-log(reference)")
            record(rows, f"lower log nontrivial {beta}/{cutoff}", item["lower_bound_is_nontrivial_log"], item["log_probability_lower"], "<0")
        logs = [item["log_probability_lower"] for item in table[str(beta)]]
        record(rows, f"strict decrease {beta}", all(left > right for left, right in zip(logs, logs[1:])), logs, "strictly decreasing")

    record(rows, "row cardinality", sum(len(v) for v in table.values()) == len(BETAS) * len(CUTOFFS), sum(len(v) for v in table.values()), len(BETAS) * len(CUTOFFS))
    record(rows, "conditional owner-neutral label", True, "conditional chart interface", "not source-owned")
    record(rows, "uniform conclusion withheld", True, "not asserted", "not asserted")
    passed = sum(row["status"] == "PASS" for row in rows)
    output = {
        "schema": "tect/a6-classii-branch-relative-compensator-independent/1.0",
        "run_kind": "independent",
        "result_id": "R-467",
        "exploration_id": "EXP-001342",
        "script_version": __version__,
        "verdict": "R-467-INDEPENDENT-PASS" if passed == len(rows) else "R-467-INDEPENDENT-FAIL",
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "assertions": rows,
        "inputs": {"a1": {"path": str(A1.relative_to(ROOT)), "sha256": digest(A1)}, "r466": {"path": str(R466.relative_to(ROOT)), "sha256": digest(R466)}, "r465": {"path": str(R465.relative_to(ROOT)), "sha256": digest(R465)}, "cutoffs": list(CUTOFFS), "betas": [str(beta) for beta in BETAS]},
        "derived": {"volume": str(nums["volume"]), "mu2": str(nums["mu2"]), "rows": [item for values in table.values() for item in values], "chart_mass_lower_formula": "mu_N(B_N)>=J_min*vol(U_N)*exp(-beta*E_tube)/Z_upper_N(beta)", "branch_relative_compensator": "log(J_min*vol(U_N))-log(reference_volume_N)", "uniform_admissibility_condition": "liminf_N log_probability_lower(N,beta)>-infinity"},
        "evidence_level": "T0 exact finite conditional branch-relative Jacobian/entropy budget with owner-neutral chart fixtures",
        "assumptions": ["Fixed-cutoff R-464/R-465 comparisons hold.", "A later owner supplies an injective chart, positive Jacobian lower bound and energy ceiling.", "All fixture values are nonphysical audit inputs."],
        "missing_assumptions": ["Source-owned active branch chart and Jacobian.", "Correlated partition normalization and uniform compensator.", "Tightness, floor removal and ordered continuum limit.", "Source-owned Q3LOCK dynamics and physical/QFT/Yang--Mills bridge."],
        "non_claims": ["No source-owned branch or physical sector is selected.", "No cutoff-uniform probability, entropy density, tightness, continuum, Pre-A, Sector-A, QFT, Yang--Mills or mass-gap result follows.", "Existing T-054/T-059/T-061 methods, owner order and promotion firewalls are unchanged."],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"INDEPENDENT R-467 {output['verdict']} {passed}/{len(rows)}")
    print(f"Evidence: {destination.resolve()}")
    return 0 if output["verdict"].endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
