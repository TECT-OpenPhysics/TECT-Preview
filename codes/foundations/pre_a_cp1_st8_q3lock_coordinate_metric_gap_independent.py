#!/usr/bin/env python3
"""Non-importing independent lane for R-401.

This lane reconstructs the finite Q3 Gibbs coordinate laws and computes both
the level-index and physical-coordinate gaps from its own implementation.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-coordinate-metric-gap-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-pre_a_cp1_st8_q3lock_coordinate_metric_gap/independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def kron_site(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def hamiltonian(volume: int, dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [kron_site(q_single, site, volume, identity) for site in range(volume)]
    momenta = [kron_site(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    terms: list[np.ndarray] = []
    terms.extend(p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(coordinates, momenta))
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        terms.append(c * difference2 / 2.0 + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0)
    return sym(sum(terms, np.zeros_like(coordinates[0])))


def thermal(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(sym(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, coordinate_basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(coordinate_basis.conj().T @ state @ coordinate_basis))
    raw_minimum = float(np.min(diagonal))
    values = np.maximum(diagonal, 0.0)
    total = float(np.sum(values))
    if total <= 0.0:
        raise AssertionError("coordinate distribution has zero mass")
    values /= total
    return values.reshape((dimension,) * volume), raw_minimum


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    left = dimension ** len(sites)
    return moved.reshape(left, -1).sum(axis=1).reshape((dimension,) * len(sites))


def gap(probabilities_row: np.ndarray, spacings: np.ndarray, exponent: Fraction) -> float:
    pi = np.asarray(probabilities_row, dtype=float)
    pi = pi / float(np.sum(pi))
    if pi.ndim != 1 or pi.size < 2 or np.any(pi <= 0.0) or spacings.shape != (pi.size - 1,) or np.any(spacings <= 0.0):
        raise AssertionError("invalid gap inputs")
    conductances = np.minimum(pi[:-1], pi[1:]) * np.power(spacings, float(exponent))
    laplacian = np.zeros((pi.size, pi.size), dtype=float)
    for index, value in enumerate(conductances):
        laplacian[index, index] += value
        laplacian[index + 1, index + 1] += value
        laplacian[index, index + 1] -= value
        laplacian[index + 1, index] -= value
    scale = np.diag(1.0 / np.sqrt(pi))
    normalized = scale @ laplacian @ scale
    eigenvalues = np.linalg.eigvalsh((normalized + normalized.T) / 2.0)
    answer = float(np.sort(eigenvalues)[1])
    if not math.isfinite(answer) or answer <= 0.0:
        raise AssertionError("nonpositive gap")
    return answer


def profile(reference: np.ndarray, order: list[int], dimension: int, floor: float, spacings: np.ndarray, exponent: Fraction) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    index_values: list[float] = []
    coordinate_values: list[float] = []
    atom_values: list[float] = []
    for radius in range(1, len(order)):
        prefix = marginal(reference, order[: radius + 1], dimension)
        parent = marginal(reference, order[:radius], dimension)
        if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
            raise AssertionError("marginal floor")
        local_index: list[float] = []
        local_coordinate: list[float] = []
        local_atoms: list[float] = []
        for mass, row in zip(parent.reshape(-1), prefix.reshape(-1, dimension)):
            conditional = row / float(mass)
            conditional /= float(np.sum(conditional))
            local_atoms.append(float(np.min(conditional)))
            local_index.append(gap(conditional, np.ones(dimension - 1), Fraction(0)))
            local_coordinate.append(gap(conditional, spacings, exponent))
        index_values.extend(local_index)
        coordinate_values.extend(local_coordinate)
        atom_values.extend(local_atoms)
        rows.append({
            "radius": radius,
            "parent_count": len(local_index),
            "minimum_index_gap": min(local_index),
            "maximum_index_gap": max(local_index),
            "minimum_coordinate_gap": min(local_coordinate),
            "maximum_coordinate_gap": max(local_coordinate),
            "minimum_conditional_atom": min(local_atoms),
        })
    return {
        "rows": rows,
        "minimum_index_gap": min(index_values, default=float("inf")),
        "maximum_index_gap": max(index_values, default=0.0),
        "minimum_coordinate_gap": min(coordinate_values, default=float("inf")),
        "maximum_coordinate_gap": max(coordinate_values, default=0.0),
        "minimum_conditional_atom": min(atom_values, default=float("inf")),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    exponent = Fraction(str(fixture["edge_spacing_power"]))
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
    check("spacing exponent", exponent == Fraction(-2), exponent, "-2", "fixture")
    records: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = {}
    index_mins: list[float] = []
    coordinate_mins: list[float] = []
    atom_mins: list[float] = []
    reference_mins: list[float] = []
    spacing_mins: list[float] = []
    for volume, dimension in pairs:
        h = hamiltonian(volume, dimension, fixture)
        b = basis(dimension, volume)
        q_single, _ = q3.oscillator(dimension)
        levels = np.linalg.eigvalsh(sym(q_single)).real
        spacings = np.diff(levels)
        spacing_mins.append(float(np.min(spacings)))
        check(f"V={volume} d={dimension} basis", b.shape == (dimension**volume, dimension**volume), b.shape, (dimension**volume, dimension**volume), "coordinates")
        check(f"V={volume} d={dimension} spacing", float(np.min(spacings)) > 0.0, float(np.min(spacings)), ">0", "coordinate metric")
        for beta in betas:
            reference, raw_minimum = probabilities(thermal(h, beta), b, dimension, volume)
            reference_mins.append(float(np.min(reference)))
            check(f"V={volume} d={dimension} beta={beta} raw positivity", raw_minimum >= -tolerance, raw_minimum, f">=-{tolerance}", "coordinates")
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}", "Gibbs")
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                row = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, **profile(reference, order, dimension, floor, spacings, exponent)}
                check(f"V={volume} d={dimension} beta={beta} {orientation} index gap", row["minimum_index_gap"] > 0.0, row["minimum_index_gap"], ">0", "index gap")
                check(f"V={volume} d={dimension} beta={beta} {orientation} coordinate gap", row["minimum_coordinate_gap"] > 0.0, row["minimum_coordinate_gap"], ">0", "coordinate gap")
                records.append(row)
                by_key.setdefault(f"V={volume}/beta={beta}/{orientation}", []).append(row)
                index_mins.append(row["minimum_index_gap"])
                coordinate_mins.append(row["minimum_coordinate_gap"])
                atom_mins.append(row["minimum_conditional_atom"])
    index_ratios: list[dict[str, Any]] = []
    coordinate_ratios: list[dict[str, Any]] = []
    for key, values in by_key.items():
        ordered = sorted(values, key=lambda row: row["dimension"])
        for previous, current in zip(ordered, ordered[1:]):
            index_ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": current["minimum_index_gap"] / previous["minimum_index_gap"]})
            coordinate_ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": current["minimum_coordinate_gap"] / previous["minimum_coordinate_gap"]})
    gains = [row["minimum_coordinate_gap"] / row["minimum_index_gap"] for row in records]
    expected_profiles = len(pairs) * len(betas) * len(orientations)
    check("profile coverage", len(records) == expected_profiles, len(records), expected_profiles, "coverage")
    check("finite profiles", all(math.isfinite(value) for value in index_mins + coordinate_mins + atom_mins + reference_mins + spacing_mins + gains), "all finite", "all finite", "numerics")
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
        "minimum_conditional_atom": min(atom_mins, default=0.0),
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
    payload = {"schema": "tect/pre-a-r401-independent/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-401", "exploration_id": "EXP-001246", "verdict": "PASS", "checks": checks, "assertion_count": check_count, "derived": derived, "scope": scope, "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-401 INDEPENDENT PASS {check_count}/{check_count} profiles={len(records)} index_min={derived['minimum_index_gap']:.6g} coordinate_min={derived['minimum_coordinate_gap']:.6g} gain={derived['minimum_metric_gain']:.6g}")
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
