#!/usr/bin/env python3
"""Independent non-importing finite reconstruction for R-395."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-gibbs-gentle-projection-bridge-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge" / "independent.json"


def dump_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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


def ladder(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        lowering[index - 1, index] = np.sqrt(float(index))
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else eye)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = ladder(n)
    eye = np.eye(n, dtype=complex)
    qs = [embed(q, index, volume, eye) for index in range(volume)]
    ps = [embed(p, index, volume, eye) for index in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * qj @ qj / 2.0 + g * qj @ qj @ qj @ qj / 4.0
    for index in range(volume - 1):
        delta = qs[index] - qs[index + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[index] @ qs[index] + qs[index + 1] @ qs[index + 1]) / 4.0
    return sym(h)


def thermal_state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h)
    weights = np.exp(-beta * (values - values.min())
    )
    weights /= weights.sum()
    return sym((vectors * weights) @ vectors.conj().T)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    rest = [index for index in range(volume) if index not in keep]
    axes = keep + rest + [index + volume for index in keep] + [index + volume for index in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), axes)
    count = len(keep)
    for _ in rest:
        tensor = np.trace(tensor, axis1=count, axis2=tensor.ndim // 2 + count)
    return sym(tensor.reshape(n**count, n**count))


def layouts(volume: int, width: int) -> list[dict[str, Any]]:
    result = []
    for orientation in ("right", "left"):
        for start in range(volume - width + 1):
            result.append({"orientation": orientation, "core": list(range(start, start + width)), "core_width": width})
    return result


def trace_norm(matrix: np.ndarray) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(sym(matrix)).real)))


def profile(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[dict[str, float]]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append({"disturbance": float(row["trace_disturbance"]), "gentle_bound": float(row["gentle_bound"]), "composed_bound": float(row["gentle_markov_bound"])})
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = [{"dimension": dimension, "count": len(values), "disturbance_maximum": max(v["disturbance"] for v in values), "gentle_bound_maximum": max(v["gentle_bound"] for v in values), "composed_bound_maximum": max(v["composed_bound"] for v in values)} for dimension, values in sorted(by_dimension.items())]
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["disturbance_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "disturbance_ratio": float(right["disturbance_maximum"]) / denominator if denominator > tolerance else 0.0})
        values = [item for group in by_dimension.values() for item in group]
        records.append({"key": list(key), "dimensions": dimensions, "disturbance_minimum": min(v["disturbance"] for v in values), "disturbance_maximum": max(v["disturbance"] for v in values), "gentle_bound_maximum": max(v["gentle_bound"] for v in values), "composed_bound_maximum": max(v["composed_bound"] for v in values), "adjacent_ratios": ratios, "maximum_adjacent_disturbance_ratio": max((v["disturbance_ratio"] for v in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_adjacent_disturbance_ratio": max((v["maximum_adjacent_disturbance_ratio"] for v in records), default=0.0)}


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tol = float(cfg["numerical_tolerance"])
    positivity = float(cfg["positivity_tolerance"])
    pairs = [(int(item["volume"]), int(dimension)) for item in cfg["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in cfg["beta_values"]]
    energies = [float(Fraction(value)) for value in cfg["energy_windows"]]
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
        local = {}
        for width in [int(value) for value in cfg["core_widths"]]:
            raw = hamiltonian(dimension, width, cfg)
            values, vectors = np.linalg.eigh(raw)
            minimum = float(values.min())
            projectors = {}
            for window in energies:
                selected = values - minimum <= window + positivity
                projectors[window] = sym(vectors[:, selected] @ vectors[:, selected].conj().T)
            local[width] = (raw, minimum, projectors, np.eye(dimension**width, dtype=complex))
        layouts_for_system = [layout for width in [int(value) for value in cfg["core_widths"]] for layout in layouts(volume, width)]
        partition_count += len(layouts_for_system)
        for beta in betas:
            rho = thermal_state(hamiltonian(dimension, volume, cfg), beta)
            for layout in layouts_for_system:
                width = int(layout["core_width"])
                raw, minimum, projectors, identity = local[width]
                rho_core = reduce_sites(rho, dimension, volume, layout["core"])
                K = sym(raw - minimum * identity)
                min_eigenvalue = float(np.linalg.eigvalsh(K).min().real)
                first_moment = float(np.trace(K @ rho_core).real)
                second_moment = float(np.trace(K @ K @ rho_core).real)
                if min_eigenvalue < -positivity:
                    raise AssertionError("local shift is not positive")
                for energy in energies:
                    P = projectors[energy]
                    Q = sym(identity - P)
                    window_mass = float(np.trace(P @ rho_core).real)
                    tail_raw = float(np.trace(Q @ rho_core).real)
                    tail = max(0.0, tail_raw)
                    projected = sym(P @ rho_core @ P)
                    disturbance = trace_norm(rho_core - projected)
                    gentle_bound = 2.0 * np.sqrt(tail)
                    mass_bound = first_moment / energy
                    composed_bound = 2.0 * np.sqrt(max(0.0, mass_bound))
                    markov_failures += int(tail_raw > mass_bound + tol)
                    gentle_failures += int(disturbance > gentle_bound + tol)
                    composition_failures += int(disturbance > composed_bound + tol)
                    tails.append(tail)
                    disturbances.append(disturbance)
                    gentle_bounds.append(gentle_bound)
                    composed_bounds.append(composed_bound)
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": layout["orientation"], "core": layout["core"], "core_width": width, "energy_window": energy, "window_mass": window_mass, "tail_mass": tail, "tail_mass_raw": tail_raw, "first_moment": first_moment, "second_moment": second_moment, "mass_bound": mass_bound, "trace_disturbance": disturbance, "gentle_bound": gentle_bound, "gentle_markov_bound": composed_bound, "projector_error": float(np.linalg.norm(P @ P - P, ord="fro")), "shifted_min_eigenvalue": min_eigenvalue})
    if not all(np.isfinite(value) for value in tails + disturbances + gentle_bounds + composed_bounds) or markov_failures or gentle_failures or composition_failures:
        raise AssertionError("independent gentle bridge failed")
    derived = {"admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "system_count": len(pairs), "base_partition_count": partition_count, "beta_values": betas, "energy_windows": energies, "row_count": len(rows), "tail_mass_min": min(tails), "tail_mass_max": max(tails), "trace_disturbance_min": min(disturbances), "trace_disturbance_max": max(disturbances), "gentle_bound_max": max(gentle_bounds), "gentle_markov_bound_max": max(composed_bounds), "first_moment_max": max(float(row["first_moment"]) for row in rows), "mass_bound_max": max(float(row["mass_bound"]) for row in rows), "markov_violation_count": markov_failures, "gentle_violation_count": gentle_failures, "composition_violation_count": composition_failures, "projector_error_max": max(float(row["projector_error"]) for row in rows), "cutoff_profiles": profile(rows, tol)}
    payload = {"schema": "tect/pre-a-r395-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-395", "exploration_id": "EXP-001238", "verdict": "PASS", "checks": 6, "derived": derived}
    dump_atomic(path, payload)
    print(f"R-395 INDEPENDENT PASS 6/6 systems={len(pairs)} partitions={partition_count} rows={len(rows)} disturbance_max={max(disturbances):.6g} composed_max={max(composed_bounds):.6g} profiles={derived['cutoff_profiles']['count']}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
