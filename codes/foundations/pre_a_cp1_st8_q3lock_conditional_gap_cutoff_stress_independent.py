#!/usr/bin/env python3
"""Non-importing independent lane for the R-400 cutoff stress.

The independent lane rebuilds the static Q3 Gibbs coordinate laws and the
oriented-prefix conditional birth-death profiles without importing the R-400
primary module.  It deliberately stores the same finite profile fields so the
integrated verifier can compare the two numerical derivations.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-gap-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-30-independent-pre_a_cp1_st8_q3lock_conditional_gap_cutoff_stress"
) / "independent.json"
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


def make_system(volume: int, dimension: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [kron_site(q_single, site, volume, identity) for site in range(volume)]
    momenta = [kron_site(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(fixture[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(fixture[key]))) for key in ("c", "lambda"))
    terms: list[np.ndarray] = []
    terms.extend(
        p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0
        for q, p in zip(coordinates, momenta)
    )
    for left in range(volume - 1):
        difference = coordinates[left] - coordinates[left + 1]
        difference2 = difference @ difference
        terms.append(
            c * difference2 / 2.0
            + lam * difference2 @ (coordinates[left] @ coordinates[left] + coordinates[left + 1] @ coordinates[left + 1]) / 4.0
        )
    return sym(sum(terms, np.zeros_like(coordinates[0])))


def thermal(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(sym(q_single))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
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


def birth_death_gap(probabilities_row: np.ndarray) -> float:
    pi = np.asarray(probabilities_row, dtype=float)
    if pi.ndim != 1 or pi.size < 2 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0):
        raise AssertionError("invalid conditional law")
    pi = pi / float(np.sum(pi))
    conductances = np.minimum(pi[:-1], pi[1:])
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
        raise AssertionError(f"nonpositive gap: {gap}")
    return gap


def conditional_profile(reference: np.ndarray, order: list[int], dimension: int, floor: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    gaps: list[float] = []
    atoms: list[float] = []
    for radius in range(1, len(order)):
        prefix = marginal(reference, order[: radius + 1], dimension)
        parent = marginal(reference, order[:radius], dimension)
        if float(np.min(prefix)) <= floor or float(np.min(parent)) <= floor:
            raise AssertionError(f"marginal floor at radius {radius}")
        local_gaps: list[float] = []
        local_atoms: list[float] = []
        for parent_mass, row in zip(parent.reshape(-1), prefix.reshape(-1, dimension)):
            conditional = row / float(parent_mass)
            conditional /= float(np.sum(conditional))
            if float(np.min(conditional)) <= 0.0:
                raise AssertionError("nonpositive conditional atom")
            local_atoms.append(float(np.min(conditional)))
            local_gaps.append(birth_death_gap(conditional))
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
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    orientations = list(fixture["orientations"])
    pairs = [
        (int(item["volume"]), int(dimension))
        for item in fixture["admissible_pairs"]
        for dimension in item["cutoff_dimensions"]
    ]
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 160:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001245" and manifest["result_id"] == "R-400" and manifest["claim_bearing"] is False,
        [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]],
        "EXP-001245/R-400/false",
        "provenance",
    )
    finite_flags = ("finite_static_conditional_gap_closed", "finite_cutoff_profile_closed", "finite_adjacent_ratio_audit_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "static cutoff stress only", "all promoted flags false", "scope")
    check("orientation grid", orientations == ["right", "left"], orientations, "right/left", "fixture")

    records: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = {}
    gap_mins: list[float] = []
    atom_mins: list[float] = []
    reference_mins: list[float] = []
    for volume, dimension in pairs:
        hamiltonian = make_system(volume, dimension, fixture)
        basis = coordinate_basis(dimension, volume)
        check(f"V={volume} d={dimension} basis", basis.shape == (dimension**volume, dimension**volume), basis.shape, (dimension**volume, dimension**volume), "coordinates")
        references: dict[float, np.ndarray] = {}
        for beta in betas:
            reference, raw_minimum = probabilities(thermal(hamiltonian, beta), basis, dimension, volume)
            reference_mins.append(float(np.min(reference)))
            check(f"V={volume} d={dimension} beta={beta} raw positivity", raw_minimum >= -tolerance, raw_minimum, f">=-{tolerance}", "coordinates")
            check(f"V={volume} d={dimension} beta={beta} reference", float(np.min(reference)) > floor, float(np.min(reference)), f">{floor}", "Gibbs")
            references[beta] = reference
        for beta in betas:
            reference = references[beta]
            for orientation in orientations:
                order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                profile = conditional_profile(reference, order, dimension, floor)
                check(f"V={volume} d={dimension} beta={beta} {orientation} gap", profile["minimum_conditional_gap"] > 0.0, profile["minimum_conditional_gap"], ">0", "conditional gap")
                check(f"V={volume} d={dimension} beta={beta} {orientation} atoms", profile["minimum_conditional_atom"] > 0.0, profile["minimum_conditional_atom"], ">0", "conditional law")
                row = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": orientation, **profile}
                records.append(row)
                by_key.setdefault(f"V={volume}/beta={beta}/{orientation}", []).append(row)
                gap_mins.append(profile["minimum_conditional_gap"])
                atom_mins.append(profile["minimum_conditional_atom"])

    ratios: list[dict[str, Any]] = []
    for key, values in by_key.items():
        ordered = sorted(values, key=lambda row: row["dimension"])
        for previous, current in zip(ordered, ordered[1:]):
            ratio = current["minimum_conditional_gap"] / previous["minimum_conditional_gap"]
            ratios.append({"key": key, "from_dimension": previous["dimension"], "to_dimension": current["dimension"], "ratio": ratio})
    expected_profiles = len(pairs) * len(betas) * len(orientations)
    check("profile coverage", len(records) == expected_profiles, len(records), expected_profiles, "coverage")
    check("finite profiles", all(math.isfinite(value) for value in gap_mins + atom_mins + reference_mins), "all finite", "all finite", "numerics")
    check("ratio coverage", all(item["ratio"] > 0.0 and math.isfinite(item["ratio"]) for item in ratios), ratios, "positive finite ratios", "cutoff ratios")
    payload = {
        "schema": "tect/pre-a-r400-independent/1.0",
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
            "minimum_reference_atom": min(reference_mins, default=0.0),
            "minimum_adjacent_gap_ratio": min((item["ratio"] for item in ratios), default=0.0),
            "maximum_adjacent_gap_ratio": max((item["ratio"] for item in ratios), default=0.0),
            "profiles": records,
            "adjacent_ratios": ratios,
        },
        "scope": scope,
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-400 INDEPENDENT PASS {check_count}/{check_count} profiles={len(records)} min_gap={payload['derived']['minimum_conditional_gap']:.6g} max_ratio={payload['derived']['maximum_adjacent_gap_ratio']:.6g}")
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
