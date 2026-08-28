#!/usr/bin/env python3
"""Finite physical-coordinate conditional-gap stress.

R-400 measured variation per truncation level.  This diagnostic repeats the
same Gibbs conditional laws but uses the ordered one-site oscillator
coordinate eigenvalues as the edge metric.  The comparison is explicit: the
coordinate form is not silently identified with the level-index form.
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
SLUG = "pre_a_cp1_st8_q3lock_coordinate_metric_gap"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coordinate-metric-gap-manifest.json"
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


def coordinate_levels(dimension: int) -> np.ndarray:
    q_single, _ = r399.q3.oscillator(dimension)
    values = np.linalg.eigvalsh((q_single + q_single.conj().T) / 2.0).real
    if not np.all(np.isfinite(values)) or np.any(np.diff(values) <= 0.0):
        raise AssertionError("one-site coordinate levels are not strictly ordered")
    return values


def metric_gap(probabilities: np.ndarray, spacings: np.ndarray, spacing_power: Fraction) -> float:
    pi = np.asarray(probabilities, dtype=float)
    if pi.ndim != 1 or pi.size < 2 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid conditional law")
    pi = pi / float(np.sum(pi))
    if spacings.shape != (pi.size - 1,) or np.any(spacings <= 0.0):
        raise AssertionError("invalid coordinate spacing")
    conductances = np.minimum(pi[:-1], pi[1:]) * np.power(spacings, float(spacing_power))
    laplacian = np.zeros((pi.size, pi.size), dtype=float)
    for index, conductance in enumerate(conductances):
        laplacian[index, index] += conductance
        laplacian[index + 1, index + 1] += conductance
        laplacian[index, index + 1] -= conductance
        laplacian[index + 1, index] -= conductance
    scale = np.diag(1.0 / np.sqrt(pi))
    normalized = scale @ laplacian @ scale
    spectrum = np.linalg.eigvalsh((normalized + normalized.T) / 2.0)
    gap = float(np.sort(spectrum)[1])
    if not math.isfinite(gap) or gap <= 0.0:
        raise AssertionError(f"nonpositive metric gap: {gap}")
    return gap


def conditional_profile(reference: np.ndarray, order: list[int], dimension: int, floor: float, spacings: np.ndarray, spacing_power: Fraction) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    index_gaps: list[float] = []
    coordinate_gaps: list[float] = []
    atoms: list[float] = []
    for radius in range(1, len(order)):
        prefix = r399.marginal(reference, order[: radius + 1], dimension)
        parent = r399.marginal(reference, order[:radius], dimension)
        if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
            raise AssertionError(f"marginal floor at radius {radius}")
        local_index: list[float] = []
        local_coordinate: list[float] = []
        local_atoms: list[float] = []
        for parent_mass, row in zip(parent.reshape(-1), prefix.reshape(-1, dimension)):
            conditional = row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0:
                raise AssertionError("nonpositive conditional atom")
            local_atoms.append(float(np.min(conditional)))
            local_index.append(r399.birth_death_gap(conditional))
            local_coordinate.append(metric_gap(conditional, spacings, spacing_power))
        index_min = min(local_index)
        coordinate_min = min(local_coordinate)
        index_gaps.extend(local_index)
        coordinate_gaps.extend(local_coordinate)
        atoms.extend(local_atoms)
        rows.append({
            "radius": radius,
            "parent_count": len(local_index),
            "minimum_index_gap": index_min,
            "maximum_index_gap": max(local_index),
            "minimum_coordinate_gap": coordinate_min,
            "maximum_coordinate_gap": max(local_coordinate),
            "minimum_conditional_atom": min(local_atoms),
        })
    return {
        "rows": rows,
        "minimum_index_gap": min(index_gaps, default=float("inf")),
        "maximum_index_gap": max(index_gaps, default=0.0),
        "minimum_coordinate_gap": min(coordinate_gaps, default=float("inf")),
        "maximum_coordinate_gap": max(coordinate_gaps, default=0.0),
        "minimum_conditional_atom": min(atoms, default=float("inf")),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    spacing_power = Fraction(str(fixture["edge_spacing_power"]))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
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

    check("identity", manifest["exploration_id"] == "EXP-001246" and manifest["result_id"] == "R-401" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001246/R-401/false", "provenance")
    finite_flags = ("finite_coordinate_metric_gap_closed", "finite_index_metric_comparison_closed", "finite_cutoff_metric_profile_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "coordinate metric stress only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")
    check("spacing exponent", spacing_power == Fraction(-2), spacing_power, "-2", "fixture")

    records: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = {}
    index_mins: list[float] = []
    coordinate_mins: list[float] = []
    atoms: list[float] = []
    reference_mins: list[float] = []
    spacing_mins: list[float] = []
    for volume, dimension in pairs:
        _, hamiltonian, _ = r399.split_system(volume, dimension, fixture)
        basis = r399.coordinate_basis(dimension, volume)
        levels = coordinate_levels(dimension)
        spacings = np.diff(levels)
        spacing_mins.append(float(np.min(spacings)))
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} spacing", float(np.min(spacings)) > 0.0, float(np.min(spacings)), ">0", "coordinate metric")
        for beta in betas:
            reference, raw_minimum = r399.coordinate_distribution(r399.gibbs(hamiltonian, beta), basis, dimension, volume)
            reference_mins.append(float(np.min(reference)))
            check(f"V={volume} d={dimension} beta={beta} raw positivity", raw_minimum >= -tolerance, raw_minimum, f">=-{tolerance}", "coordinates")
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}", "Gibbs")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = conditional_profile(reference, order, dimension, floor, spacings, spacing_power)
                check(f"V={volume} d={dimension} beta={beta} {orientation} index gap", profile["minimum_index_gap"] > 0.0, profile["minimum_index_gap"], ">0", "index gap")
                check(f"V={volume} d={dimension} beta={beta} {orientation} coordinate gap", profile["minimum_coordinate_gap"] > 0.0, profile["minimum_coordinate_gap"], ">0", "coordinate gap")
                row = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, **profile}
                records.append(row)
                by_key.setdefault(f"V={volume}/beta={beta}/{orientation}", []).append(row)
                index_mins.append(profile["minimum_index_gap"])
                coordinate_mins.append(profile["minimum_coordinate_gap"])
                atoms.append(profile["minimum_conditional_atom"])

    index_ratios: list[dict[str, Any]] = []
    coordinate_ratios: list[dict[str, Any]] = []
    for key, values in by_key.items():
        ordered = sorted(values, key=lambda row: row["dimension"])
        for previous, current in zip(ordered, ordered[1:]):
            index_ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": current["minimum_index_gap"] / previous["minimum_index_gap"]})
            coordinate_ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": current["minimum_coordinate_gap"] / previous["minimum_coordinate_gap"]})
    gains = [row["minimum_coordinate_gap"] / row["minimum_index_gap"] for row in records]
    check("profile coverage", len(records) == len(pairs) * len(betas) * len(orientations), len(records), len(pairs) * len(betas) * len(orientations), "coverage")
    check("finite profiles", all(math.isfinite(value) for value in index_mins + coordinate_mins + atoms + reference_mins + spacing_mins + gains), "all finite", "all finite", "numerics")
    check("ratio coverage", all(item["ratio"] > 0.0 and math.isfinite(item["ratio"]) for item in index_ratios + coordinate_ratios), len(index_ratios) + len(coordinate_ratios), "positive finite ratios", "cutoff ratios")
    derived = {
        "system_count": len(pairs),
        "profile_count": len(records),
        "index_ratio_count": len(index_ratios),
        "coordinate_ratio_count": len(coordinate_ratios),
        "minimum_index_gap": min(index_mins, default=0.0),
        "maximum_index_gap": max(index_mins, default=0.0),
        "minimum_coordinate_gap": min(coordinate_mins, default=0.0),
        "maximum_coordinate_gap": max(coordinate_mins, default=0.0),
        "minimum_metric_gain": min(gains, default=0.0),
        "maximum_metric_gain": max(gains, default=0.0),
        "minimum_conditional_atom": min(atoms, default=0.0),
        "minimum_reference_atom": min(reference_mins, default=0.0),
        "minimum_coordinate_spacing": min(spacing_mins, default=0.0),
        "minimum_adjacent_index_ratio": min((item["ratio"] for item in index_ratios), default=0.0),
        "maximum_adjacent_index_ratio": max((item["ratio"] for item in index_ratios), default=0.0),
        "minimum_adjacent_coordinate_ratio": min((item["ratio"] for item in coordinate_ratios), default=0.0),
        "maximum_adjacent_coordinate_ratio": max((item["ratio"] for item in coordinate_ratios), default=0.0),
        "profiles": records,
        "index_ratios": index_ratios,
        "coordinate_ratios": coordinate_ratios,
    }
    payload = {
        "schema": "tect/pre-a-r401-primary/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-401",
        "exploration_id": "EXP-001246",
        "verdict": "PASS",
        "checks": checks,
        "assertion_count": check_count,
        "derived": derived,
        "scope": scope,
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-401 PRIMARY PASS {check_count}/{check_count} profiles={len(records)} index_min={derived['minimum_index_gap']:.6g} coordinate_min={derived['minimum_coordinate_gap']:.6g} gain={derived['minimum_metric_gain']:.6g}")
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
