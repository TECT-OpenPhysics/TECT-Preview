#!/usr/bin/env python3
"""Finite Gibbs gentle spectral-complement bridge (R-395)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-gibbs-gentle-projection-bridge-manifest.json"
R394 = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge" / "primary.json"


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location("r394_parent", R394)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-394 finite model")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()


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


def trace_norm(matrix: np.ndarray) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(PARENT.hermitian(matrix)).real)))


def cutoff_profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[dict[str, float]]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append({"disturbance": float(row["trace_disturbance"]), "gentle_bound": float(row["gentle_bound"]), "composed_bound": float(row["gentle_markov_bound"])})
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = []
        for dimension, values in sorted(by_dimension.items()):
            dimensions.append({"dimension": dimension, "count": len(values), "disturbance_maximum": max(v["disturbance"] for v in values), "gentle_bound_maximum": max(v["gentle_bound"] for v in values), "composed_bound_maximum": max(v["composed_bound"] for v in values)})
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denom = float(left["disturbance_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "disturbance_ratio": float(right["disturbance_maximum"]) / denom if denom > tolerance else 0.0})
        values = [value for group in by_dimension.values() for value in group]
        records.append({"key": list(key), "dimensions": dimensions, "disturbance_minimum": min(v["disturbance"] for v in values), "disturbance_maximum": max(v["disturbance"] for v in values), "gentle_bound_maximum": max(v["gentle_bound"] for v in values), "composed_bound_maximum": max(v["composed_bound"] for v in values), "adjacent_ratios": ratios, "maximum_adjacent_disturbance_ratio": max((v["disturbance_ratio"] for v in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_adjacent_disturbance_ratio": max((v["maximum_adjacent_disturbance_ratio"] for v in records), default=0.0)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001238" and manifest["result_id"] == "R-395" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001238/R-395/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all gentle-bridge rows", "coverage")
    finite_flags = ("finite_positive_shift_closed", "finite_spectral_projector_closed", "finite_mass_markov_bound_closed", "finite_gentle_trace_norm_bridge_closed", "finite_gentle_markov_composition_closed", "finite_cutoff_disturbance_profile_closed", "finite_hostile_factor_mutation_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite gentle bridge only", "all promoted flags false", "scope")
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    check("pair grid", len(pairs) == sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"]) and len(set(pairs)) == len(pairs), pairs, "distinct declared systems", "fixture")
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    energies = [float(Fraction(value)) for value in fixture["energy_windows"]]
    rows: list[dict[str, Any]] = []
    tails: list[float] = []
    disturbances: list[float] = []
    gentle_bounds: list[float] = []
    composed_bounds: list[float] = []
    markov_failures = 0
    gentle_failures = 0
    composition_failures = 0
    partition_count = 0
    for volume, dimension in pairs:
        local = {width: PARENT.local_energy_spectrum(dimension, width, fixture) for width in [int(value) for value in fixture["core_widths"]]}
        layouts = [layout for width in [int(value) for value in fixture["core_widths"]] for layout in PARENT.core_layouts(volume, width)]
        partition_count += len(layouts)
        state = {beta: PARENT.gibbs(PARENT.build_hamiltonian(dimension, volume, fixture), beta) for beta in betas}
        for beta in betas:
            for layout in layouts:
                width = int(layout["core_width"])
                data = local[width]
                rho_core = PARENT.partial_trace_sites(state[beta], dimension, volume, layout["core"])
                K = PARENT.hermitian(data["raw"] - data["minimum"] * data["identity"])
                minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(K)).real)
                first_moment = float(np.trace(K @ rho_core).real)
                second_moment = float(np.trace(K @ K @ rho_core).real)
                check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} positive shift", minimum_eigenvalue >= -positivity_tolerance, minimum_eigenvalue, f">=-{positivity_tolerance}", "positive local energy")
                for energy in energies:
                    projector = data["projectors"][energy]
                    complement = PARENT.hermitian(data["identity"] - projector)
                    projection_error = float(np.linalg.norm(projector @ projector - projector, ord="fro"))
                    rank = int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))
                    window_mass = float(np.trace(projector @ rho_core).real)
                    tail_raw = float(np.trace(complement @ rho_core).real)
                    tail = max(0.0, tail_raw)
                    projected = PARENT.hermitian(projector @ rho_core @ projector)
                    projected_trace = float(np.trace(projected).real)
                    disturbance = trace_norm(rho_core - projected)
                    gentle_bound = 2.0 * np.sqrt(tail)
                    mass_bound = first_moment / energy
                    composed_bound = 2.0 * np.sqrt(max(0.0, mass_bound))
                    markov_slack = mass_bound - tail
                    gentle_slack = gentle_bound - disturbance
                    composition_slack = composed_bound - disturbance
                    tails.append(tail)
                    disturbances.append(disturbance)
                    gentle_bounds.append(gentle_bound)
                    composed_bounds.append(composed_bound)
                    markov_failures += int(tail_raw > mass_bound + tolerance)
                    gentle_failures += int(disturbance > gentle_bound + tolerance)
                    composition_failures += int(disturbance > composed_bound + tolerance)
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} projector", np.isfinite(projection_error) and projection_error <= tolerance and rank > 0, [projection_error, rank], f"idempotence <= {tolerance}, positive rank", "spectral projector")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} split", abs(window_mass + tail_raw - 1.0) <= tolerance and abs(projected_trace - window_mass) <= tolerance and -tolerance <= window_mass <= 1.0 + tolerance, [window_mass, tail_raw, projected_trace], "normalized split and projected trace", "spectral tail")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} Markov", np.isfinite(mass_bound) and tail_raw <= mass_bound + tolerance, [tail_raw, mass_bound], "tail <= first_moment/E", "Markov")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} gentle", np.isfinite(disturbance) and disturbance >= -tolerance and disturbance <= gentle_bound + tolerance, [disturbance, gentle_bound], "trace norm <= 2 sqrt(tail)", "gentle bridge")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} composed", np.isfinite(composed_bound) and disturbance <= composed_bound + tolerance, [disturbance, composed_bound], "trace norm <= 2 sqrt(first_moment/E)", "Markov composition")
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": layout["orientation"], "core": layout["core"], "core_width": width, "energy_window": energy, "local_min_energy": data["minimum"], "shifted_min_eigenvalue": minimum_eigenvalue, "projector_rank": rank, "projector_error": projection_error, "window_mass": window_mass, "tail_mass": tail, "tail_mass_raw": tail_raw, "first_moment": first_moment, "second_moment": second_moment, "mass_bound": mass_bound, "trace_disturbance": disturbance, "gentle_bound": gentle_bound, "gentle_markov_bound": composed_bound, "markov_slack": markov_slack, "gentle_slack": gentle_slack, "gentle_markov_slack": composition_slack})
    check("partition aggregate", partition_count > 0 and len(rows) > 0, [partition_count, len(rows)], "positive rows", "coverage")
    check("finite aggregates", min(tails) >= -tolerance and max(tails) <= 1.0 + tolerance and min(disturbances) >= -tolerance and all(np.isfinite(value) for value in tails + disturbances + gentle_bounds + composed_bounds), [min(tails), max(tails), min(disturbances), max(disturbances)], "finite nonnegative tails and disturbances", "aggregate")
    check("bridge aggregates", markov_failures == 0 and gentle_failures == 0 and composition_failures == 0, [markov_failures, gentle_failures, composition_failures], "zero violations", "bridge")
    profiles = cutoff_profiles(rows, tolerance)
    check("cutoff profiles", profiles["count"] > 0 and all(len(record["dimensions"]) >= 2 for record in profiles["profiles"]), profiles["count"], "adjacent cutoff profiles", "cutoff stress")
    derived = {"admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "system_count": len(pairs), "base_partition_count": partition_count, "beta_values": betas, "energy_windows": energies, "row_count": len(rows), "tail_mass_min": min(tails), "tail_mass_max": max(tails), "trace_disturbance_min": min(disturbances), "trace_disturbance_max": max(disturbances), "gentle_bound_max": max(gentle_bounds), "gentle_markov_bound_max": max(composed_bounds), "first_moment_max": max(float(row["first_moment"]) for row in rows), "mass_bound_max": max(float(row["mass_bound"]) for row in rows), "markov_violation_count": markov_failures, "gentle_violation_count": gentle_failures, "composition_violation_count": composition_failures, "projector_error_max": max(float(row["projector_error"]) for row in rows), "cutoff_profiles": profiles}
    payload = {"schema": "tect/pre-a-r395-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-395", "exploration_id": "EXP-001238", "verdict": "PASS", "checks": checks, "derived": derived, "scope": scope, "records": rows}
    atomic_json(output, payload)
    print(f"R-395 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={partition_count} rows={len(rows)} disturbance_max={max(disturbances):.6g} composed_max={max(composed_bounds):.6g} profiles={profiles['count']}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
