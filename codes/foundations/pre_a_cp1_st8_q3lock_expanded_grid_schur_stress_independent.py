#!/usr/bin/env python3
"""Non-importing independent audit of the R-425 finite Schur algebra."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-manifest.json"
SLUG = "expanded_grid_schur_stress"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"


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


def block_basis(weights: np.ndarray, blocks: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    pi = np.asarray(weights, dtype=float)
    if pi.ndim != 1 or not np.all(np.isfinite(pi)) or np.any(pi <= 0.0) or abs(float(np.sum(pi)) - 1.0) > 1.0e-10:
        raise AssertionError("weights must be positive and normalized")
    n = len(pi)
    raw = np.zeros((n, len(blocks)), dtype=float)
    seen: set[int] = set()
    for column, block in enumerate(blocks):
        indices = np.asarray(block, dtype=int)
        if indices.size < 2 or np.any(indices < 0) or np.any(indices >= n) or seen.intersection(int(value) for value in indices):
            raise AssertionError("blocks must be disjoint, in range and have size >=2")
        seen.update(int(value) for value in indices)
        mass = float(np.sum(pi[indices]))
        if not math.isfinite(mass) or mass <= 0.0:
            raise AssertionError("invalid block mass")
        raw[indices, column] = np.sqrt(pi[indices] / mass)
    if np.max(np.abs(raw.T @ raw - np.eye(len(blocks)))) > 1.0e-10:
        raise AssertionError("block vectors not orthonormal")
    complete, _ = np.linalg.qr(raw, mode="complete")
    return complete[:, : len(blocks)], complete[:, len(blocks) :]


def direct_residual_basis(weights: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    pi = np.asarray(weights, dtype=float)
    columns: list[np.ndarray] = []
    for block in blocks:
        indices = np.asarray(block, dtype=int)
        if indices.size < 2:
            raise AssertionError("block too small")
        anchor = int(indices[0])
        for index in indices[1:]:
            vector = np.zeros(len(pi), dtype=float)
            vector[anchor] = np.sqrt(pi[int(index)])
            vector[int(index)] = -np.sqrt(pi[anchor])
            columns.append(vector)
    q, _ = np.linalg.qr(np.column_stack(columns), mode="reduced")
    return q


def split_gaps(weights: np.ndarray, conductance: np.ndarray, blocks: list[np.ndarray]) -> dict[str, float]:
    pi = np.asarray(weights, dtype=float)
    c = np.asarray(conductance, dtype=float)
    if c.shape != (len(pi), len(pi)) or not np.all(np.isfinite(c)) or np.any(c < 0.0) or not np.allclose(c, c.T, atol=1.0e-12):
        raise AssertionError("invalid reversible conductance")
    laplacian = np.diag(np.sum(c, axis=1)) - c
    inverse = 1.0 / np.sqrt(pi)
    operator = inverse[:, None] * laplacian * inverse[None, :]
    operator = (operator + operator.T) / 2.0
    u, v = block_basis(pi, blocks)
    residual_operator = (v.T @ operator @ v + (v.T @ operator @ v).T) / 2.0
    residual_values = np.linalg.eigvalsh(residual_operator)
    if residual_values.size == 0 or float(residual_values[0]) <= 0.0:
        raise AssertionError("residual block is not positive")
    coupling = u.T @ operator @ v
    coarse = (u.T @ operator @ u + (u.T @ operator @ u).T) / 2.0
    schur = coarse - coupling @ np.linalg.solve(residual_operator, coupling.T)
    schur = (schur + schur.T) / 2.0
    harmonic = u - v @ np.linalg.solve(residual_operator, coupling.T)
    mass = (harmonic.T @ harmonic + (harmonic.T @ harmonic).T) / 2.0
    mass_values, mass_vectors = np.linalg.eigh(mass)
    if float(np.min(mass_values)) <= 0.0:
        raise AssertionError("harmonic mass is singular")
    mass_inverse = mass_vectors @ np.diag(1.0 / np.sqrt(mass_values)) @ mass_vectors.T
    coarse_weighted = mass_inverse @ schur @ mass_inverse
    coarse_values = np.linalg.eigvalsh((coarse_weighted + coarse_weighted.T) / 2.0)
    if abs(float(coarse_values[0])) > 2.0e-7 or float(coarse_values[1]) <= 0.0:
        raise AssertionError("coarse Schur is not positive")
    residual_direct = direct_residual_basis(pi, blocks)
    direct_values = np.linalg.eigvalsh((residual_direct.T @ operator @ residual_direct + (residual_direct.T @ operator @ residual_direct).T) / 2.0)
    difference = abs(float(np.min(direct_values)) - float(residual_values[0]))
    if difference > 5.0e-7:
        raise AssertionError("independent residual bases disagree")
    coarse_gap = float(coarse_values[1])
    residual_gap = float(residual_values[0])
    combined = 0.5 * min(coarse_gap, residual_gap)
    if combined <= 0.0:
        raise AssertionError("combined envelope is not positive")
    root = np.sqrt(pi)
    max_energy_error = 0.0
    minimum_margin = math.inf
    for phase in (0.11, 0.53, 0.97):
        probe = np.sin((np.arange(len(pi)) + 1.0) * phase) + 0.17 * np.cos(np.arange(len(pi)) + 2.0)
        probe -= float(np.dot(pi, probe))
        y = root * probe
        z = u.T @ y
        residual_coordinate = v.T @ y
        harmonic_coordinate = -np.linalg.solve(residual_operator, coupling.T @ z)
        harmonic_y = u @ z + v @ harmonic_coordinate
        residual_y = v @ (residual_coordinate - harmonic_coordinate)
        energy = float(y @ operator @ y)
        split_energy = float(harmonic_y @ operator @ harmonic_y + residual_y @ operator @ residual_y)
        max_energy_error = max(max_energy_error, abs(energy - split_energy))
        minimum_margin = min(minimum_margin, energy - combined * float(y @ y))
    if max_energy_error > 1.0e-7 or minimum_margin < -1.0e-7:
        raise AssertionError("harmonic energy split failed")
    return {"coarse_gap": coarse_gap, "residual_gap": residual_gap, "combined_gap": combined, "energy_error": max_energy_error, "lower_margin": minimum_margin, "residual_basis_difference": difference}


def fixtures() -> list[tuple[np.ndarray, np.ndarray, list[np.ndarray]]]:
    records: list[tuple[np.ndarray, np.ndarray, list[np.ndarray]]] = []
    for values, scale, blocks in (
        ([0.45, 0.30, 0.17, 0.08], 0.8, ([0, 1], [2, 3])),
        ([0.36, 0.29, 0.21, 0.14], 1.3, ([0, 1], [2, 3])),
        ([0.40, 0.25, 0.20, 0.10, 0.05], 0.7, ([0, 1], [2, 3, 4])),
        ([0.31, 0.24, 0.19, 0.14, 0.07, 0.05], 1.1, ([0, 1, 2], [3, 4, 5])),
    ):
        pi = np.asarray(values, dtype=float)
        conductance = scale * np.outer(pi, pi)
        np.fill_diagonal(conductance, 0.0)
        for index in range(len(pi) - 1):
            conductance[index, index + 1] += 0.02 * min(pi[index], pi[index + 1])
            conductance[index + 1, index] = conductance[index, index + 1]
        records.append((pi, conductance, [np.asarray(block, dtype=int) for block in blocks]))
    return records


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    assertions = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = ["finite_expanded_grid_assembly_closed", "finite_harmonic_coarse_schur_closed", "finite_residual_reuse_closed", "finite_combined_lower_envelope_closed", "finite_coverage_boundary_recorded"]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-425" and manifest["exploration_id"] == "EXP-001270" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-425/EXP-001270/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")
    records: list[dict[str, float]] = []
    for index, (pi, conductance, blocks) in enumerate(fixtures()):
        check(f"fixture={index} weights", np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= 1.0e-10, [float(np.min(pi)), float(np.sum(pi))], "positive normalized weights", "weights")
        check(f"fixture={index} conductance", np.allclose(conductance, conductance.T) and np.all(conductance >= 0.0), "symmetric nonnegative", "reversible graph", "conductance")
        result = split_gaps(pi, conductance, blocks)
        check(f"fixture={index} coarse", result["coarse_gap"] > 0.0, result["coarse_gap"], ">0", "coarse Schur")
        check(f"fixture={index} residual", result["residual_gap"] > 0.0, result["residual_gap"], ">0", "residual")
        check(f"fixture={index} combined", result["combined_gap"] > 0.0 and result["combined_gap"] <= 0.5 * min(result["coarse_gap"], result["residual_gap"]) + 1.0e-12, result["combined_gap"], "positive half-minimum envelope", "combined")
        check(f"fixture={index} split", result["energy_error"] <= 1.0e-7 and result["lower_margin"] >= -1.0e-7, [result["energy_error"], result["lower_margin"]], "finite split residuals", "decomposition")
        records.append(result)
    check("fixture coverage", len(records) == 4 and min(item["combined_gap"] for item in records) > 0.0, len(records), "four positive finite fixtures", "coverage")
    derived = {"fixture_count": len(records), "minimum_coarse_gap": min(item["coarse_gap"] for item in records), "maximum_coarse_gap": max(item["coarse_gap"] for item in records), "minimum_residual_gap": min(item["residual_gap"] for item in records), "maximum_residual_gap": max(item["residual_gap"] for item in records), "minimum_combined_gap": min(item["combined_gap"] for item in records), "maximum_combined_gap": max(item["combined_gap"] for item in records), "maximum_energy_error": max(item["energy_error"] for item in records), "minimum_lower_margin": min(item["lower_margin"] for item in records), "maximum_residual_basis_difference": max(item["residual_basis_difference"] for item in records), "records": records}
    payload: dict[str, Any] = {"schema": "tect/pre-a-r425-independent/1.0", "result_id": manifest["result_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_ids"][0], "manifest": MANIFEST.relative_to(REPO).as_posix(), "run_kind": "independent", "verdict": "PASS", "assertion_count": assertions, "assertions": checks, "derived": derived, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"]}
    atomic_json(output, payload)
    print(f"R-425 INDEPENDENT PASS {assertions}/{assertions} fixtures={len(records)} coarse=[{derived['minimum_coarse_gap']:.6g},{derived['maximum_coarse_gap']:.6g}] residual=[{derived['minimum_residual_gap']:.6g},{derived['maximum_residual_gap']:.6g}] combined=[{derived['minimum_combined_gap']:.6g},{derived['maximum_combined_gap']:.6g}]")
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
