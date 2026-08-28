#!/usr/bin/env python3
"""Independent non-importing finite reconstruction for R-396."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-recoverability-first-projected-petz-transport-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_recoverability_first_projected_petz_transport" / "independent.json"


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
    weights = np.exp(-beta * (values - values.min()))
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


def reduce_groups(state: np.ndarray, dimensions: list[int], keep: list[int]) -> np.ndarray:
    count = len(dimensions)
    rest = [index for index in range(count) if index not in keep]
    axes = keep + rest + [index + count for index in keep] + [index + count for index in rest]
    tensor = np.transpose(state.reshape(dimensions + dimensions), axes)
    kept_count = len(keep)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    size = int(np.prod([dimensions[index] for index in keep], dtype=int))
    return sym(tensor.reshape(size, size))


def tripartitions(volume: int, widths: list[int], buffers: list[int]) -> list[dict[str, Any]]:
    result = []
    for core_width in widths:
        for buffer_width in buffers:
            for start in range(max(0, volume - core_width - buffer_width)):
                core = list(range(start, start + core_width))
                buffer = list(range(start + core_width, start + core_width + buffer_width))
                environment = list(range(start + core_width + buffer_width, volume))
                if environment:
                    result.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "right", "core_width": core_width, "buffer_width": buffer_width})
            for end in range(core_width + buffer_width, volume + 1):
                core = list(range(end - core_width, end))
                buffer = list(range(end - core_width - buffer_width, end - core_width))
                environment = list(range(0, end - core_width - buffer_width))
                if environment:
                    result.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "left", "core_width": core_width, "buffer_width": buffer_width})
    return result


def spectral_power(matrix: np.ndarray, exponent: float, tolerance: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    clipped = np.maximum(values.real, 0.0)
    powered = np.where(clipped > tolerance, clipped**exponent, 0.0) if exponent < 0.0 else clipped**exponent
    return sym((vectors * powered) @ vectors.conj().T)


def petz(input_ab: np.ndarray, reference_bc: np.ndarray, reference_b: np.ndarray, dimensions: tuple[int, int, int], tolerance: float) -> np.ndarray:
    d_a, d_b, d_c = dimensions
    sqrt_bc = spectral_power(reference_bc, 0.5, tolerance)
    inverse_sqrt_b = spectral_power(reference_b, -0.5, tolerance)
    blocks = input_ab.reshape(d_a, d_b, d_a, d_b)
    recovered = np.zeros((d_a, d_b, d_c, d_a, d_b, d_c), dtype=complex)
    eye_c = np.eye(d_c, dtype=complex)
    for left in range(d_a):
        for right in range(d_a):
            block = blocks[left, :, right, :]
            lifted = np.kron(inverse_sqrt_b @ block @ inverse_sqrt_b, eye_c)
            image = sqrt_bc @ lifted @ sqrt_bc
            recovered[left, :, :, right, :, :] = image.reshape(d_b, d_c, d_b, d_c)
    return sym(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(sym(left - right)).real)))


def petz_fast(input_ab: np.ndarray, reference_bc: np.ndarray, reference_b: np.ndarray, dimensions: tuple[int, int, int], tolerance: float) -> np.ndarray:
    d_a, d_b, d_c = dimensions
    sqrt_bc = spectral_power(reference_bc, 0.5, tolerance)
    inverse_sqrt_b = spectral_power(reference_b, -0.5, tolerance)
    dressing = np.kron(np.eye(d_a, dtype=complex), inverse_sqrt_b)
    source = (dressing @ input_ab @ dressing).reshape(d_a, d_b, d_a, d_b)
    kernel = sqrt_bc.reshape(d_b, d_c, d_b, d_c)
    recovered = np.einsum("bcuv,auAx,xvBC->abcABC", kernel, source, kernel, optimize=True)
    return sym(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["buffer_width"], row["orientation"], row["beta"], row["energy_window"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row["transported_error"]))
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dims = [{"dimension": dimension, "count": len(values), "transported_error_maximum": max(values)} for dimension, values in sorted(by_dimension.items())]
        ratios = []
        for left, right in zip(dims, dims[1:]):
            denom = float(left["transported_error_maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "transported_error_ratio": float(right["transported_error_maximum"]) / denom if denom > tolerance else 0.0})
        vals = [value for group in by_dimension.values() for value in group]
        records.append({"key": list(key), "dimensions": dims, "transported_error_minimum": min(vals), "transported_error_maximum": max(vals), "adjacent_ratios": ratios, "maximum_adjacent_transport_ratio": max((item["transported_error_ratio"] for item in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_adjacent_transport_ratio": max((item["maximum_adjacent_transport_ratio"] for item in records), default=0.0)}


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tol = float(cfg["numerical_tolerance"])
    positivity = float(cfg["positivity_tolerance"])
    pairs = [(int(item["volume"]), int(dimension)) for item in cfg["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in cfg["beta_values"]]
    energies = [float(Fraction(value)) for value in cfg["energy_windows"]]
    widths = [int(value) for value in cfg["core_widths"]]
    buffers = [int(value) for value in cfg["buffer_widths"]]
    rows: list[dict[str, Any]] = []
    dabc_values: list[float] = []
    dab_values: list[float] = []
    projected_values: list[float] = []
    transported_values: list[float] = []
    budget_values: list[float] = []
    norm_fail = contract_fail = triangle_fail = two_delta_fail = 0
    partition_count = 0
    for volume, dimension in pairs:
        global_state = {beta: thermal_state(hamiltonian(dimension, volume, cfg), beta) for beta in betas}
        projectors = {}
        for width in widths:
            local_values, local_vectors = np.linalg.eigh(hamiltonian(dimension, width, cfg))
            shifted = local_values - local_values.min()
            projectors[width] = {}
            for energy in energies:
                mask = shifted <= energy + positivity
                projectors[width][energy] = sym(local_vectors[:, mask] @ local_vectors[:, mask].conj().T)
        parts = tripartitions(volume, widths, buffers)
        partition_count += len(parts)
        for beta in betas:
            for part in parts:
                core, buffer, env = part["core"], part["buffer"], part["environment"]
                dims = (dimension**len(core), dimension**len(buffer), dimension**len(env))
                abc = core + buffer + env
                rho_abc = reduce_sites(global_state[beta], dimension, volume, abc)
                rho_ab = reduce_groups(rho_abc, list(dims), [0, 1])
                for energy in energies:
                    P = projectors[int(part["core_width"])][energy]
                    lifted = np.kron(P, np.eye(dims[1] * dims[2], dtype=complex))
                    raw_sigma = sym(lifted @ rho_abc @ lifted)
                    mass = float(np.trace(raw_sigma).real)
                    norm_fail += int(not (mass > tol and mass <= 1.0 + tol))
                    sigma = sym(raw_sigma / mass)
                    sigma_ab = reduce_groups(sigma, list(dims), [0, 1])
                    sigma_b = reduce_groups(sigma, list(dims), [1])
                    sigma_bc = reduce_groups(sigma, list(dims), [1, 2])
                    rec_sigma = petz_fast(sigma_ab, sigma_bc, sigma_b, dims, positivity)
                    rec_rho = petz_fast(rho_ab, sigma_bc, sigma_b, dims, positivity)
                    dabc = distance(rho_abc, sigma)
                    dab = distance(rho_ab, sigma_ab)
                    projected = distance(sigma, rec_sigma)
                    transported = distance(rho_abc, rec_rho)
                    rec_input = distance(rec_rho, rec_sigma)
                    budget = projected + dabc + dab
                    two_delta = projected + 2.0 * dabc
                    contract_fail += int(rec_input > dab + tol or dab > dabc + tol)
                    triangle_fail += int(transported > budget + tol)
                    two_delta_fail += int(transported > two_delta + tol)
                    dabc_values.append(dabc); dab_values.append(dab); projected_values.append(projected); transported_values.append(transported); budget_values.append(budget)
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": part["orientation"], "core": core, "buffer": buffer, "environment": env, "core_width": int(part["core_width"]), "buffer_width": int(part["buffer_width"]), "energy_window": energy, "projection_mass": mass, "delta_abc": dabc, "delta_ab": dab, "projected_error": projected, "transported_error": transported, "recovered_input_distance": rec_input, "triangle_budget": budget, "two_delta_budget": two_delta})
    if not all(np.isfinite(value) for value in dabc_values + dab_values + projected_values + transported_values + budget_values) or norm_fail or contract_fail or triangle_fail or two_delta_fail:
        raise AssertionError("independent Petz transport failed")
    derived = {"admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs], "system_count": len(pairs), "partition_count": partition_count, "row_count": len(rows), "beta_values": betas, "energy_windows": energies, "delta_abc_min": min(dabc_values), "delta_abc_max": max(dabc_values), "delta_ab_min": min(dab_values), "delta_ab_max": max(dab_values), "projected_error_max": max(projected_values), "transported_error_max": max(transported_values), "triangle_budget_max": max(budget_values), "contractivity_gap_max": max(float(row["recovered_input_distance"] - row["delta_ab"]) for row in rows), "normalization_violation_count": norm_fail, "contractivity_violation_count": contract_fail, "triangle_violation_count": triangle_fail, "two_delta_violation_count": two_delta_fail, "cutoff_profiles": profiles(rows, tol)}
    payload = {"schema": "tect/pre-a-r396-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-396", "exploration_id": "EXP-001239", "verdict": "PASS", "checks": 6, "derived": derived}
    dump_atomic(path, payload)
    print(f"R-396 INDEPENDENT PASS 6/6 systems={len(pairs)} partitions={partition_count} rows={len(rows)} transported_max={max(transported_values):.6g} ratio_max={derived['cutoff_profiles']['maximum_adjacent_transport_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
