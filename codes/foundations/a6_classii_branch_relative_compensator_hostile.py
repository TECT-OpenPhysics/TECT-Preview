#!/usr/bin/env python3
"""Hostile mutation firewall for the R-467 compensator interface."""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs" / "2026-08-31-hostile-a6-branch-relative-compensator" / "hostile.json"
CUTOFFS = (1, 2, 3, 4, 6, 8, 10)
BETAS = (Fraction(1, 2), Fraction(1), Fraction(2))
ACTIVE_SIDE = Fraction(1, 8)
NORMAL_SIDE = Fraction(1, 4)
REFERENCE_SIDE = Fraction(1, 8)
JACOBIAN_MIN = Fraction(1, 2)
ENERGY = Fraction(1)
ACTIVE_PER_SITE = 2


def row(beta: Fraction, cutoff: int) -> dict[str, Any]:
    sites = (2 * cutoff + 1) ** 3
    ambient = 6 * sites
    active = ACTIVE_PER_SITE * sites
    normal = ambient - active
    chart = ACTIVE_SIDE**active * NORMAL_SIDE**normal
    reference = REFERENCE_SIDE**ambient
    chart_log = active * math.log(float(ACTIVE_SIDE)) + normal * math.log(float(NORMAL_SIDE))
    ref_log = ambient * math.log(float(REFERENCE_SIDE))
    jac_log = math.log(float(JACOBIAN_MIN))
    log_z = float(ambient)  # mutation harness denominator placeholder; direction is checked separately
    return {
        "cutoff": cutoff,
        "beta": str(beta),
        "sites": sites,
        "ambient_dimension": ambient,
        "active_dimension": active,
        "normal_dimension": normal,
        "active_side": str(ACTIVE_SIDE),
        "normal_side": str(NORMAL_SIDE),
        "reference_side": str(REFERENCE_SIDE),
        "jacobian_min": str(JACOBIAN_MIN),
        "energy_ceiling": str(ENERGY),
        "chart_volume_exact": str(chart),
        "reference_volume_exact": str(reference),
        "log_chart_volume": chart_log,
        "log_reference_volume": ref_log,
        "log_jacobian": jac_log,
        "log_jacobian_volume": jac_log + chart_log,
        "log_partition_upper": log_z,
        "log_numerator_lower": jac_log + chart_log - float(beta * ENERGY),
        "log_probability_lower": jac_log + chart_log - float(beta * ENERGY) - log_z,
        "source_owned": False,
        "uniform_closed": False,
        "partition_direction": "upper_denominator",
    }


def valid(item: dict[str, Any]) -> bool:
    active = int(item["active_dimension"])
    normal = int(item["normal_dimension"])
    ambient = int(item["ambient_dimension"])
    if active <= 0 or normal <= 0 or active + normal != ambient:
        return False
    if Fraction(item["active_side"]) <= 0 or Fraction(item["normal_side"]) <= 0 or Fraction(item["reference_side"]) <= 0:
        return False
    if Fraction(item["jacobian_min"]) <= 0 or not math.isfinite(float(Fraction(item["energy_ceiling"]))):
        return False
    expected_chart = Fraction(item["active_side"]) ** active * Fraction(item["normal_side"]) ** normal
    if Fraction(item["chart_volume_exact"]) != expected_chart:
        return False
    expected_reference = Fraction(item["reference_side"]) ** ambient
    if Fraction(item["reference_volume_exact"]) != expected_reference:
        return False
    beta = Fraction(item["beta"])
    expected_jacobian_volume_log = math.log(float(Fraction(item["jacobian_min"])))
    expected_jacobian_volume_log += active * math.log(float(Fraction(item["active_side"])))
    expected_jacobian_volume_log += normal * math.log(float(Fraction(item["normal_side"])))
    expected_numerator_log = expected_jacobian_volume_log - float(beta * Fraction(item["energy_ceiling"]))
    expected_probability_log = expected_numerator_log - float(item["log_partition_upper"])
    if not math.isclose(float(item["log_jacobian_volume"]), expected_jacobian_volume_log, rel_tol=0.0, abs_tol=1e-12):
        return False
    if not math.isclose(float(item["log_numerator_lower"]), expected_numerator_log, rel_tol=0.0, abs_tol=1e-12):
        return False
    if not math.isclose(float(item["log_probability_lower"]), expected_probability_log, rel_tol=0.0, abs_tol=1e-12):
        return False
    if item["partition_direction"] != "upper_denominator":
        return False
    if item["source_owned"] or item["uniform_closed"]:
        return False
    if not math.isfinite(float(item["log_probability_lower"])):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    base = row(Fraction(1), 2)
    mutations: list[tuple[str, dict[str, Any]]] = []

    bad = dict(base)
    bad["normal_dimension"] = 0
    mutations.append(("drop normal coordinates", bad))
    bad = dict(base)
    bad["chart_volume_exact"] = "1"
    mutations.append(("corrupt chart volume", bad))
    bad = dict(base)
    bad["log_jacobian_volume"] = bad["log_chart_volume"]
    mutations.append(("omit Jacobian factor", bad))
    bad = dict(base)
    bad["log_numerator_lower"] = float(base["log_jacobian_volume"]) + float(Fraction(1))
    mutations.append(("reverse Boltzmann ceiling sign", bad))
    bad = dict(base)
    bad["partition_direction"] = "lower_denominator"
    mutations.append(("reverse partition comparison", bad))
    bad = dict(base)
    bad["jacobian_min"] = "0"
    mutations.append(("allow zero Jacobian", bad))
    bad = dict(base)
    bad["source_owned"] = True
    mutations.append(("relabel fixture as source-owned", bad))
    bad = dict(base)
    bad["uniform_closed"] = True
    mutations.append(("promote finite rows to uniform", bad))

    rows: list[dict[str, Any]] = []
    rejected = 0
    for name, mutated in mutations:
        accepted = valid(mutated)
        rows.append({"mutation": name, "status": "REJECTED" if not accepted else "ACCEPTED", "expected": "REJECTED"})
        if not accepted:
            rejected += 1
    verdict = "HOSTILE_MUTATIONS_REJECTED" if rejected == len(mutations) else "HOSTILE_MUTATION_FAILURE"
    output = {"schema": "tect/a6-classii-branch-relative-compensator-hostile/1.0", "run_kind": "hostile", "result_id": "R-467", "exploration_id": "EXP-001342", "verdict": verdict, "assertion_summary": {"passed": rejected, "total": len(mutations)}, "mutations": rows, "boundary": "Hostile firewall only; no source-owned branch or uniform probability is inferred."}
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"HOSTILE R-467 {verdict} {rejected}/{len(mutations)}")
    print(f"Evidence: {destination.resolve()}")
    return 0 if verdict == "HOSTILE_MUTATIONS_REJECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
