#!/usr/bin/env python3
"""Increasing-cutoff stress for the R-399 conditional birth-death gap.

This static diagnostic uses only the finite Q3 Gibbs reference law.  It
measures every oriented-prefix conditional law on a larger cutoff ladder and
records the smallest ordered-level birth-death gap and adjacent-cutoff ratios.
No finite minimum is promoted to a uniform theorem.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_conditional_gap_cutoff_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-gap-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_conditional_poincare_shell as r399  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def conditional_profile(reference: np.ndarray, order: list[int], dimension: int, floor: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    gaps: list[float] = []
    atoms: list[float] = []
    for radius in range(1, len(order)):
        p_prefix = r399.marginal(reference, order[: radius + 1], dimension)
        p_parent = r399.marginal(reference, order[:radius], dimension)
        if float(np.min(p_prefix)) <= floor or float(np.min(p_parent)) <= floor:
            raise AssertionError(f"marginal probability floor at radius {radius}")
        parent_masses = p_parent.reshape(-1)
        rows_prefix = p_prefix.reshape(-1, dimension)
        local_gaps: list[float] = []
        local_atoms: list[float] = []
        for parent_mass, row in zip(parent_masses, rows_prefix):
            conditional = row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0:
                raise AssertionError("nonpositive conditional atom")
            local_atoms.append(float(np.min(conditional)))
            local_gaps.append(r399.birth_death_gap(conditional))
        gap_min = min(local_gaps)
        gap_max = max(local_gaps)
        atom_min = min(local_atoms)
        gaps.extend(local_gaps)
        atoms.extend(local_atoms)
        rows.append({
            "radius": radius,
            "parent_count": len(local_gaps),
            "minimum_conditional_gap": gap_min,
            "maximum_conditional_gap": gap_max,
            "minimum_conditional_atom": atom_min,
        })
    return {
        "rows": rows,
        "minimum_conditional_gap": min(gaps, default=float("inf")),
        "maximum_conditional_gap": max(gaps, default=0.0),
        "minimum_conditional_atom": min(atoms, default=float("inf")),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    betas = [float(Fraction(item)) for item in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 160:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001245" and manifest["result_id"] == "R-400" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001245/R-400/false", "provenance")
    finite_flags = ("finite_static_conditional_gap_closed", "finite_cutoff_profile_closed", "finite_adjacent_ratio_audit_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "static cutoff stress only", "all promoted flags false", "scope")
    check("system grid", len(pairs) == sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"]) and len(set(pairs)) == len(pairs), pairs, "distinct declared systems", "fixture")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")

    records: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = {}
    raw_mins: list[float] = []
    gap_mins: list[float] = []
    atom_mins: list[float] = []
    for volume, dimension in pairs:
        _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        states = {beta: r399.gibbs(hamiltonian, beta) for beta in betas}
        references = {beta: r399.coordinate_distribution(states[beta], basis, dimension, volume)[0] for beta in betas}
        for beta in betas:
            reference = references[beta]
            raw_mins.append(float(np.min(reference)))
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}", "Gibbs")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = conditional_profile(reference, order, dimension, floor)
                check(f"V={volume} d={dimension} beta={beta} {orientation} gap", profile["minimum_conditional_gap"] > 0.0, profile["minimum_conditional_gap"], ">0", "conditional gap")
                check(f"V={volume} d={dimension} beta={beta} {orientation} atoms", profile["minimum_conditional_atom"] > 0.0, profile["minimum_conditional_atom"], ">0", "conditional law")
                row = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, **profile}
                records.append(row)
                key = f"V={volume}/beta={beta}/{orientation}"
                by_key.setdefault(key, []).append(row)
                gap_mins.append(profile["minimum_conditional_gap"])
                atom_mins.append(profile["minimum_conditional_atom"])

    ratios: list[dict[str, Any]] = []
    for key, values in by_key.items():
        ordered = sorted(values, key=lambda row: row["dimension"])
        for previous, current in zip(ordered, ordered[1:]):
            ratio = current["minimum_conditional_gap"] / previous["minimum_conditional_gap"]
            ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": ratio})
    check("profile coverage", len(records) == len(pairs) * len(betas) * len(orientations), len(records), len(pairs) * len(betas) * len(orientations), "coverage")
    check("finite profiles", all(math.isfinite(value) for value in gap_mins + atom_mins + raw_mins), "all finite", "all finite", "numerics")
    check("ratio coverage", all(item["ratio"] > 0.0 and math.isfinite(item["ratio"]) for item in ratios), ratios, "positive finite ratios", "cutoff ratios")

    payload = {
        "schema": "tect/pre-a-r400-primary/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-400",
        "exploration_id": "EXP-001245",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": check_count,
        "derived": {
            "system_count": len(pairs),
            "profile_count": len(records),
            "ratio_count": len(ratios),
            "minimum_conditional_gap": min(gap_mins, default=0.0),
            "maximum_conditional_gap": max(gap_mins, default=0.0),
            "minimum_conditional_atom": min(atom_mins, default=0.0),
            "minimum_reference_atom": min(raw_mins, default=0.0),
            "minimum_adjacent_gap_ratio": min((item["ratio"] for item in ratios), default=0.0),
            "maximum_adjacent_gap_ratio": max((item["ratio"] for item in ratios), default=0.0),
            "profiles": records,
            "adjacent_ratios": ratios,
            "finite_static_conditional_gap_closed": True,
            "finite_cutoff_profile_closed": True,
            "finite_adjacent_ratio_audit_closed": True,
            "cutoff_independent_conditional_gap_closed": False,
            "volume_independent_conditional_gap_closed": False,
            "source_independent_conditional_gap_closed": False,
            "phase_uniform_conditional_gap_closed": False,
            "uniform_gradient_decay_closed": False,
            "phase_conditioned_influence_closed": False,
            "folded_positive_replica_domination_closed": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "actual_split_limit_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
        },
        "records": records,
        "scope": scope,
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-400 PRIMARY PASS {check_count}/{check_count} profiles={len(records)} min_gap={payload['derived']['minimum_conditional_gap']:.6g} max_ratio={payload['derived']['maximum_adjacent_gap_ratio']:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
