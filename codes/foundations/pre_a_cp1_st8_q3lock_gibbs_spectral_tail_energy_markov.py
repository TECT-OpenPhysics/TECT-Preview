#!/usr/bin/env python3
"""Finite positive-energy Markov audit for Gibbs spectral complements (R-394)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-gibbs-spectral-tail-energy-markov-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "primary.json"


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(index + 1.0)
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def build_hamiltonian(dimension: int, volume: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [lift(q_single, site, volume, identity) for site in range(volume)]
    momenta = [lift(p_single, site, volume, identity) for site in range(volume)]
    hamiltonian = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    chi, r, g, c, lam = (float(fixture[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for q, p in zip(coordinates, momenta):
        hamiltonian += p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0
    for site in range(volume - 1):
        difference = coordinates[site] - coordinates[site + 1]
        difference2 = difference @ difference
        hamiltonian += c * difference2 / 2.0 + lam * difference2 @ (coordinates[site] @ coordinates[site] + coordinates[site + 1] @ coordinates[site + 1]) / 4.0
    return hermitian(hamiltonian)


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hamiltonian)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def partial_trace_sites(state: np.ndarray, dimension: int, volume: int, keep: Iterable[int]) -> np.ndarray:
    kept = list(keep)
    rest = [site for site in range(volume) if site not in kept]
    axes = kept + rest + [site + volume for site in kept] + [site + volume for site in rest]
    tensor = np.transpose(state.reshape([dimension] * (2 * volume)), axes)
    kept_count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    size = dimension**kept_count
    return hermitian(tensor.reshape(size, size))


def core_layouts(volume: int, width: int) -> list[dict[str, Any]]:
    answer: list[dict[str, Any]] = []
    for orientation in ("right", "left"):
        for start in range(volume - width + 1):
            answer.append({"orientation": orientation, "core": list(range(start, start + width)), "core_width": width})
    return answer


def local_energy_spectrum(dimension: int, width: int, fixture: dict[str, Any]) -> dict[str, Any]:
    raw = build_hamiltonian(dimension, width, fixture)
    values, vectors = np.linalg.eigh(raw)
    minimum = float(np.min(values))
    shifted = values - minimum
    identity = np.eye(dimension**width, dtype=complex)
    projectors: dict[float, np.ndarray] = {}
    for raw_window in fixture["energy_windows"]:
        threshold = float(Fraction(raw_window))
        selected = shifted <= threshold + float(fixture["positivity_tolerance"])
        projectors[threshold] = hermitian(vectors[:, selected] @ vectors[:, selected].conj().T)
    return {"raw": raw, "minimum": minimum, "shifted_values": shifted, "vectors": vectors, "identity": identity, "projectors": projectors}


def profile(rows: list[dict[str, Any]], field: str, keys: tuple[str, ...]) -> dict[str, Any]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = tuple(row[name] for name in keys)
        groups.setdefault(key, []).append(float(row[field]))
    output = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        output.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
    return {"profiles": output, "maximum_range": max((item["range"] for item in output), default=0.0)}


def cutoff_profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[dict[str, float]]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append({"tail_mass": float(row["tail_mass"]), "tail_mass_bound": float(row["tail_mass_bound"]), "tail_weighted": float(row["tail_weighted"]), "tail_weighted_bound": float(row["tail_weighted_bound"])})
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = []
        for dimension, values in sorted(by_dimension.items()):
            dimensions.append({"dimension": dimension, "count": len(values), "tail_mass_minimum": min(v["tail_mass"] for v in values), "tail_mass_maximum": max(v["tail_mass"] for v in values), "tail_mass_bound_maximum": max(v["tail_mass_bound"] for v in values), "tail_weighted_maximum": max(v["tail_weighted"] for v in values), "tail_weighted_bound_maximum": max(v["tail_weighted_bound"] for v in values)})
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["tail_mass_maximum"])
            weighted_denominator = float(left["tail_weighted_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "tail_mass_ratio": float(right["tail_mass_maximum"]) / denominator if denominator > tolerance else 0.0, "tail_weighted_ratio": float(right["tail_weighted_maximum"]) / weighted_denominator if weighted_denominator > tolerance else 0.0})
        all_values = [value for values in by_dimension.values() for value in values]
        records.append({"key": list(key), "dimensions": dimensions, "tail_mass_minimum": min(v["tail_mass"] for v in all_values), "tail_mass_maximum": max(v["tail_mass"] for v in all_values), "tail_mass_bound_maximum": max(v["tail_mass_bound"] for v in all_values), "tail_weighted_maximum": max(v["tail_weighted"] for v in all_values), "tail_weighted_bound_maximum": max(v["tail_weighted_bound"] for v in all_values), "adjacent_ratios": ratios, "maximum_adjacent_tail_ratio": max((v["tail_mass_ratio"] for v in ratios), default=0.0), "maximum_adjacent_weighted_ratio": max((v["tail_weighted_ratio"] for v in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_adjacent_tail_ratio": max((row["maximum_adjacent_tail_ratio"] for row in records), default=0.0), "maximum_adjacent_weighted_ratio": max((row["maximum_adjacent_weighted_ratio"] for row in records), default=0.0)}


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

    check("identity", manifest["exploration_id"] == "EXP-001237" and manifest["result_id"] == "R-394" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001237/R-394/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all energy-tail rows", "coverage")
    finite_flags = ("finite_positive_shift_closed", "finite_spectral_projector_closed", "finite_mass_markov_bound_closed", "finite_weighted_markov_bound_closed", "finite_spectral_tail_profile_closed", "finite_cutoff_profile_closed", "finite_hostile_moment_mutation_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite Gibbs tail only", "all promoted flags false", "scope")

    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct systems", "fixture")
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    energies = [float(Fraction(value)) for value in fixture["energy_windows"]]
    rows: list[dict[str, Any]] = []
    tails: list[float] = []
    weighted_tails: list[float] = []
    mass_bound_violations = 0
    weighted_bound_violations = 0
    base_partition_count = 0

    for volume, dimension in pairs:
        local_data = {width: local_energy_spectrum(dimension, width, fixture) for width in [int(value) for value in fixture["core_widths"]]}
        layouts = [layout for width in [int(value) for value in fixture["core_widths"]] for layout in core_layouts(volume, width)]
        base_partition_count += len(layouts)
        for beta in betas:
            state = gibbs(build_hamiltonian(dimension, volume, fixture), beta)
            for layout in layouts:
                width = int(layout["core_width"])
                data = local_data[width]
                rho_core = partial_trace_sites(state, dimension, volume, layout["core"])
                K = hermitian(data["raw"] - data["minimum"] * data["identity"])
                minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(K)).real)
                first_moment = float(np.trace(K @ rho_core).real)
                second_moment = float(np.trace(K @ K @ rho_core).real)
                check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} positive shift", minimum_eigenvalue >= -positivity_tolerance, minimum_eigenvalue, f">=-{positivity_tolerance}", "positive local energy")
                for energy in energies:
                    projector = data["projectors"][energy]
                    complement = hermitian(data["identity"] - projector)
                    projector_error = float(np.linalg.norm(projector @ projector - projector, ord="fro"))
                    rank = int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))
                    mass = float(np.trace(projector @ rho_core).real)
                    tail = float(np.trace(complement @ rho_core).real)
                    tail_weighted = float(np.trace(K @ complement @ rho_core).real)
                    mass_bound = first_moment / energy
                    weighted_bound = second_moment / energy
                    mass_slack = mass_bound - tail
                    weighted_slack = weighted_bound - tail_weighted
                    tails.append(tail)
                    weighted_tails.append(tail_weighted)
                    mass_bound_violations += int(tail > mass_bound + tolerance)
                    weighted_bound_violations += int(tail_weighted > weighted_bound + tolerance)
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} projector", np.isfinite(projector_error) and projector_error <= tolerance and rank > 0, [projector_error, rank], f"idempotence <= {tolerance}, positive rank", "spectral projector")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} split", np.isfinite(mass) and np.isfinite(tail) and abs(mass + tail - 1.0) <= tolerance and -tolerance <= mass <= 1.0 + tolerance, [mass, tail], "mass plus tail = 1", "spectral tail")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} mass Markov", np.isfinite(mass_bound) and tail <= mass_bound + tolerance, [tail, mass_bound], "tail <= first_moment/E", "mass Markov")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} core={layout['core']} E={energy} weighted Markov", np.isfinite(weighted_bound) and tail_weighted <= weighted_bound + tolerance, [tail_weighted, weighted_bound], "weighted tail <= second_moment/E", "weighted Markov")
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": layout["orientation"], "core": layout["core"], "core_width": width, "energy_window": energy, "local_min_energy": data["minimum"], "shifted_min_eigenvalue": minimum_eigenvalue, "projector_rank": rank, "projector_error": projector_error, "window_mass": mass, "tail_mass": tail, "first_moment": first_moment, "second_moment": second_moment, "tail_weighted": tail_weighted, "tail_mass_bound": mass_bound, "tail_weighted_bound": weighted_bound, "markov_mass_slack": mass_slack, "markov_weighted_slack": weighted_slack})

    check("partition aggregate", base_partition_count > 0 and len(rows) > 0, [base_partition_count, len(rows)], "positive rows", "coverage")
    check("tail aggregate", min(tails) >= -tolerance and max(tails) <= 1.0 + tolerance and all(np.isfinite(value) for value in tails), [min(tails), max(tails)], "finite tails in [0,1]", "spectral tail")
    check("weighted tail aggregate", min(weighted_tails) >= -tolerance and all(np.isfinite(value) for value in weighted_tails), [min(weighted_tails), max(weighted_tails)], "finite nonnegative weighted tails", "weighted tail")
    check("Markov aggregate", mass_bound_violations == 0 and weighted_bound_violations == 0, [mass_bound_violations, weighted_bound_violations], "zero bound violations", "Markov")
    cutoff = cutoff_profiles(rows, tolerance)
    check("cutoff profiles", cutoff["count"] > 0 and all(np.isfinite(row["maximum_adjacent_tail_ratio"]) and np.isfinite(row["maximum_adjacent_weighted_ratio"]) for row in cutoff["profiles"]), cutoff["count"], "finite adjacent-cutoff profiles", "cutoff stress")

    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "system_count": len(pairs), "base_partition_count": base_partition_count, "beta_values": betas, "energy_windows": energies,
        "row_count": len(rows), "tail_mass_min": min(tails), "tail_mass_max": max(tails), "weighted_tail_min": min(weighted_tails), "weighted_tail_max": max(weighted_tails), "mass_markov_violation_count": mass_bound_violations, "weighted_markov_violation_count": weighted_bound_violations,
        "first_moment_max": max(float(row["first_moment"]) for row in rows), "second_moment_max": max(float(row["second_moment"]) for row in rows), "tail_mass_bound_max": max(float(row["tail_mass_bound"]) for row in rows), "tail_weighted_bound_max": max(float(row["tail_weighted_bound"]) for row in rows), "projector_error_max": max(float(row["projector_error"]) for row in rows),
        "tail_profile": profile(rows, "tail_mass", ("core_width", "energy_window")), "weighted_tail_profile": profile(rows, "tail_weighted", ("core_width", "energy_window")), "cutoff_profiles": cutoff,
    }
    payload = {"schema": "tect/pre-a-r394-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-394", "exploration_id": "EXP-001237", "verdict": "PASS", "checks": checks, "derived": derived, "scope": scope, "records": rows}
    atomic_json(output, payload)
    print(f"R-394 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={base_partition_count} rows={len(rows)} tail_max={max(tails):.6g} weighted_max={max(weighted_tails):.6g} Markov=PASS cutoff_profiles={cutoff['count']}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
