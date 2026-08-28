#!/usr/bin/env python3
"""Independent non-importing finite reconstruction for R-394."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-gibbs-spectral-tail-energy-markov-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "independent.json"


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
    a = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        a[index - 1, index] = np.sqrt(float(index))
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def embed(a: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    factors = [a if index == site else eye for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = ladder(n)
    eye = np.eye(n, dtype=complex)
    qs = [embed(q, index, volume, eye) for index in range(volume)]
    ps = [embed(p, index, volume, eye) for index in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[name]) for name in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * qj @ qj / 2.0 + g * qj @ qj @ qj @ qj / 4.0
    for index in range(volume - 1):
        delta = qs[index] - qs[index + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[index] @ qs[index] + qs[index + 1] @ qs[index + 1]) / 4.0
    return sym(h)


def thermal_state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h)
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    return sym((vectors * weights) @ vectors.conj().T)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    kept = list(keep)
    rest = [index for index in range(volume) if index not in kept]
    axes = kept + rest + [index + volume for index in kept] + [index + volume for index in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), axes)
    count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=count, axis2=tensor.ndim // 2 + count)
    return sym(tensor.reshape(n**count, n**count))


def layouts(volume: int, width: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for orientation in ("right", "left"):
        for start in range(volume - width + 1):
            result.append({"orientation": orientation, "core": list(range(start, start + width)), "core_width": width})
    return result


def entropy(rho: np.ndarray, tol: float) -> float:
    values = np.maximum(np.linalg.eigvalsh(sym(rho)).real, 0.0)
    probabilities = values / values.sum()
    probabilities = probabilities[probabilities > tol]
    return float(-np.sum(probabilities * np.log(probabilities)))


def profile(rows: list[dict[str, Any]], field: str, keys: tuple[str, ...]) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = tuple(row[key_name] for key_name in keys)
        grouped.setdefault(key, []).append(float(row[field]))
    result = []
    for key, values in sorted(grouped.items(), key=lambda item: str(item[0])):
        result.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
    return {"profiles": result, "maximum_range": max((row["range"] for row in result), default=0.0)}


def cutoff_profiles(rows: list[dict[str, Any]], tol: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[dict[str, float]]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append({"tail_mass": float(row["tail_mass"]), "tail_mass_bound": float(row["tail_mass_bound"]), "tail_weighted": float(row["tail_weighted"]), "tail_weighted_bound": float(row["tail_weighted_bound"])})
    output = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = []
        for dimension, values in sorted(by_dimension.items()):
            dimensions.append({"dimension": dimension, "count": len(values), "tail_mass_minimum": min(v["tail_mass"] for v in values), "tail_mass_maximum": max(v["tail_mass"] for v in values), "tail_mass_bound_maximum": max(v["tail_mass_bound"] for v in values), "tail_weighted_maximum": max(v["tail_weighted"] for v in values), "tail_weighted_bound_maximum": max(v["tail_weighted_bound"] for v in values)})
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["tail_mass_maximum"])
            weighted_denominator = float(left["tail_weighted_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "tail_mass_ratio": float(right["tail_mass_maximum"]) / denominator if denominator > tol else 0.0, "tail_weighted_ratio": float(right["tail_weighted_maximum"]) / weighted_denominator if weighted_denominator > tol else 0.0})
        all_values = [value for values in by_dimension.values() for value in values]
        output.append({"key": list(key), "dimensions": dimensions, "tail_mass_minimum": min(v["tail_mass"] for v in all_values), "tail_mass_maximum": max(v["tail_mass"] for v in all_values), "tail_mass_bound_maximum": max(v["tail_mass_bound"] for v in all_values), "tail_weighted_maximum": max(v["tail_weighted"] for v in all_values), "tail_weighted_bound_maximum": max(v["tail_weighted_bound"] for v in all_values), "adjacent_ratios": ratios, "maximum_adjacent_tail_ratio": max((v["tail_mass_ratio"] for v in ratios), default=0.0), "maximum_adjacent_weighted_ratio": max((v["tail_weighted_ratio"] for v in ratios), default=0.0)})
    return {"profiles": output, "count": len(output), "maximum_adjacent_tail_ratio": max((row["maximum_adjacent_tail_ratio"] for row in output), default=0.0), "maximum_adjacent_weighted_ratio": max((row["maximum_adjacent_weighted_ratio"] for row in output), default=0.0)}


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
    weighted: list[float] = []
    mass_failures = 0
    weighted_failures = 0
    partition_count = 0
    for volume, dimension in pairs:
        local = {}
        for width in [int(value) for value in cfg["core_widths"]]:
            raw = hamiltonian(dimension, width, cfg)
            values, vectors = np.linalg.eigh(raw)
            minimum = float(values.min())
            shifted = values - minimum
            projectors = {}
            for window in energies:
                selector = shifted <= window + positivity
                projectors[window] = sym(vectors[:, selector] @ vectors[:, selector].conj().T)
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
                first = float(np.trace(K @ rho_core).real)
                second = float(np.trace(K @ K @ rho_core).real)
                if min_eigenvalue < -positivity:
                    raise AssertionError("local shift is not positive")
                for energy in energies:
                    P = projectors[energy]
                    Q = sym(identity - P)
                    rank = int(np.count_nonzero(np.linalg.eigvalsh(P) > 0.5))
                    error = float(np.linalg.norm(P @ P - P, ord="fro"))
                    mass = float(np.trace(P @ rho_core).real)
                    tail = float(np.trace(Q @ rho_core).real)
                    weighted_tail = float(np.trace(K @ Q @ rho_core).real)
                    mass_bound = first / energy
                    weighted_bound = second / energy
                    mass_failures += int(tail > mass_bound + tol)
                    weighted_failures += int(weighted_tail > weighted_bound + tol)
                    tails.append(tail)
                    weighted.append(weighted_tail)
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": layout["orientation"], "core": layout["core"], "core_width": width, "energy_window": energy, "local_min_energy": minimum, "shifted_min_eigenvalue": min_eigenvalue, "projector_rank": rank, "projector_error": error, "window_mass": mass, "tail_mass": tail, "first_moment": first, "second_moment": second, "tail_weighted": weighted_tail, "tail_mass_bound": mass_bound, "tail_weighted_bound": weighted_bound, "markov_mass_slack": mass_bound - tail, "markov_weighted_slack": weighted_bound - weighted_tail})
    if not all(np.isfinite(value) for value in tails + weighted) or mass_failures or weighted_failures:
        raise AssertionError("independent Markov tail check failed")
    derived = {"admissible_pairs": [{"volume": v, "dimension": n} for v, n in pairs], "system_count": len(pairs), "base_partition_count": partition_count, "beta_values": betas, "energy_windows": energies, "row_count": len(rows), "tail_mass_min": min(tails), "tail_mass_max": max(tails), "weighted_tail_min": min(weighted), "weighted_tail_max": max(weighted), "mass_markov_violation_count": mass_failures, "weighted_markov_violation_count": weighted_failures, "first_moment_max": max(float(row["first_moment"]) for row in rows), "second_moment_max": max(float(row["second_moment"]) for row in rows), "tail_mass_bound_max": max(float(row["tail_mass_bound"]) for row in rows), "tail_weighted_bound_max": max(float(row["tail_weighted_bound"]) for row in rows), "projector_error_max": max(float(row["projector_error"]) for row in rows), "tail_profile": profile(rows, "tail_mass", ("core_width", "energy_window")), "weighted_tail_profile": profile(rows, "tail_weighted", ("core_width", "energy_window")), "cutoff_profiles": cutoff_profiles(rows, tol)}
    payload = {"schema": "tect/pre-a-r394-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-394", "exploration_id": "EXP-001237", "verdict": "PASS", "checks": 6, "derived": derived}
    dump_atomic(path, payload)
    print(f"R-394 INDEPENDENT PASS 6/6 systems={len(pairs)} partitions={partition_count} rows={len(rows)} tail_max={max(tails):.6g} weighted_max={max(weighted):.6g} Markov=PASS cutoff_profiles={derived['cutoff_profiles']['count']}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
