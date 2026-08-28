#!/usr/bin/env python3
"""Non-importing independent finite lane for R-397.

The oscillator Hamiltonian, reductions, spectral collar and Petz map are
rebuilt here rather than imported from the primary R-397 implementation.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-semigroup-dressed-petz-collar-finite-discriminator-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_semigroup_dressed_petz_collar" / "independent.json"


def dump_atomic(path: Path, payload: dict[str, Any]) -> None:
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
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def build_system(dimension: int, volume: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [lift(q_single, site, volume, identity) for site in range(volume)]
    momenta = [lift(p_single, site, volume, identity) for site in range(volume)]
    hamiltonian = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    chi, r, g, c, lam = (float(fixture[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for q, p in zip(coordinates, momenta):
        hamiltonian += p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
    for index in range(volume - 1):
        difference = coordinates[index] - coordinates[index + 1]
        difference2 = difference @ difference
        hamiltonian += c * difference2 / 2.0 + lam * difference2 @ (coordinates[index] @ coordinates[index] + coordinates[index + 1] @ coordinates[index + 1]) / 4.0
    return hermitian(hamiltonian)


def thermal_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hamiltonian)
    weights = np.exp(-beta * (values - float(values.min())))
    weights /= float(weights.sum())
    return hermitian((vectors * weights) @ vectors.conj().T)


def reduce_sites(state: np.ndarray, dimension: int, volume: int, keep: Iterable[int]) -> np.ndarray:
    kept = list(keep)
    rest = [site for site in range(volume) if site not in kept]
    axes = kept + rest + [site + volume for site in kept] + [site + volume for site in rest]
    tensor = np.transpose(state.reshape([dimension] * (2 * volume)), axes)
    kept_count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    return hermitian(tensor.reshape(dimension**kept_count, dimension**kept_count))


def reduce_groups(state: np.ndarray, dimensions: list[int], keep: Iterable[int]) -> np.ndarray:
    kept = list(keep)
    count = len(dimensions)
    rest = [index for index in range(count) if index not in kept]
    axes = kept + rest + [index + count for index in kept] + [index + count for index in rest]
    tensor = np.transpose(state.reshape(dimensions + dimensions), axes)
    kept_count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    size = int(np.prod([dimensions[index] for index in kept], dtype=int))
    return hermitian(tensor.reshape(size, size))


def spectral_power(matrix: np.ndarray, exponent: float, tolerance: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    clipped = np.maximum(values.real, 0.0)
    if exponent < 0.0:
        powered = np.where(clipped > tolerance, clipped**exponent, 0.0)
    else:
        powered = clipped**exponent
    return hermitian((vectors * powered) @ vectors.conj().T)


def petz(input_ab: np.ndarray, reference_bc: np.ndarray, reference_b: np.ndarray, dimensions: tuple[int, int, int], tolerance: float) -> np.ndarray:
    d_a, d_b, d_c = dimensions
    root = spectral_power(reference_bc, 0.5, tolerance)
    inverse = spectral_power(reference_b, -0.5, tolerance)
    dressed = np.kron(np.eye(d_a, dtype=complex), inverse) @ input_ab @ np.kron(np.eye(d_a, dtype=complex), inverse)
    source = dressed.reshape(d_a, d_b, d_a, d_b)
    kernel = root.reshape(d_b, d_c, d_b, d_c)
    recovered = np.einsum("bcuv,auAx,xvBC->abcABC", kernel, source, kernel, optimize=True)
    return hermitian(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(hermitian(left - right)).real)))


def tripartitions(volume: int, core_widths: list[int], buffer_widths: list[int]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for core_width in core_widths:
        for buffer_width in buffer_widths:
            for start in range(max(0, volume - core_width - buffer_width)):
                core = list(range(start, start + core_width))
                buffer = list(range(start + core_width, start + core_width + buffer_width))
                environment = list(range(start + core_width + buffer_width, volume))
                if environment:
                    records.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "right", "core_width": core_width, "buffer_width": buffer_width})
            for end in range(core_width + buffer_width, volume + 1):
                core = list(range(end - core_width, end))
                buffer = list(range(end - core_width - buffer_width, end - core_width))
                environment = list(range(0, end - core_width - buffer_width))
                if environment:
                    records.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "left", "core_width": core_width, "buffer_width": buffer_width})
    return records


def shifted_local(dimension: int, width: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(build_system(dimension, width, fixture))
    shifted = values - float(values.min())
    local_k = hermitian((vectors * shifted) @ vectors.conj().T)
    return shifted, vectors, local_k


def collar_filter(shifted: np.ndarray, vectors: np.ndarray, scale: float) -> np.ndarray:
    return hermitian((vectors * np.exp(-scale * shifted / 2.0)) @ vectors.conj().T)


def profile(rows: list[dict[str, Any]], field: str, tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["buffer_width"], row["orientation"], row["beta"], row["scale"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row[field]))
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = [{"dimension": dimension, "count": len(values), "maximum": max(values)} for dimension, values in sorted(by_dimension.items())]
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["maximum"])
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "ratio": float(right["maximum"]) / denominator if denominator > tolerance else 0.0})
        values = [value for group in by_dimension.values() for value in group]
        records.append({"key": list(key), "dimensions": dimensions, "minimum": min(values), "maximum": max(values), "adjacent_ratios": ratios, "maximum_adjacent_ratio": max((item["ratio"] for item in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "profiles_with_adjacent_cutoff": sum(len(item["dimensions"]) >= 2 for item in records), "maximum_adjacent_ratio": max((item["maximum_adjacent_ratio"] for item in records), default=0.0)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    semigroup_tolerance = float(fixture["semigroup_tolerance"])
    scales = [float(Fraction(value)) for value in fixture["filter_scales"]]
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    widths = [int(value) for value in fixture["core_widths"]]
    buffers = [int(value) for value in fixture["buffer_widths"]]
    local_data: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    semigroup_residuals: list[float] = []
    for _, dimension in pairs:
        for width in widths:
            if (dimension, width) in local_data:
                continue
            shifted, vectors, local_k = shifted_local(dimension, width, fixture)
            local_data[(dimension, width)] = (shifted, vectors, local_k)
            if float(np.min(shifted)) < -positivity_tolerance:
                raise AssertionError("negative shifted energy")
            for scale_s in scales:
                for scale_t in scales:
                    first = collar_filter(shifted, vectors, scale_s) @ collar_filter(shifted, vectors, scale_t)
                    second = collar_filter(shifted, vectors, scale_s + scale_t)
                    residual = float(np.linalg.norm(first - second, ord="fro") / max(1.0, np.linalg.norm(second, ord="fro")))
                    semigroup_residuals.append(residual)
                    if residual > semigroup_tolerance:
                        raise AssertionError("semigroup composition failed")
    rows: list[dict[str, Any]] = []
    mass_defects: list[float] = []
    moments: list[float] = []
    mass_slacks: list[float] = []
    disturbances: list[float] = []
    envelopes: list[float] = []
    projected_errors: list[float] = []
    transported_errors: list[float] = []
    budgets: list[float] = []
    for volume, dimension in pairs:
        state_values, state_vectors = np.linalg.eigh(build_system(dimension, volume, fixture))
        states = {beta: thermal_state((state_vectors * state_values) @ state_vectors.conj().T, beta) for beta in betas}
        for beta in betas:
            for partition in tripartitions(volume, widths, buffers):
                core, buffer, environment = partition["core"], partition["buffer"], partition["environment"]
                core_width, buffer_width = int(partition["core_width"]), int(partition["buffer_width"])
                dimensions = (dimension**len(core), dimension**len(buffer), dimension**len(environment))
                rho_abc = reduce_sites(states[beta], dimension, volume, core + buffer + environment)
                rho_ab = reduce_groups(rho_abc, list(dimensions), [0, 1])
                shifted, local_vectors, local_k = local_data[(dimension, core_width)]
                identity_bc = np.eye(dimensions[1] * dimensions[2], dtype=complex)
                moment = max(float(np.trace(rho_abc @ np.kron(local_k, identity_bc)).real), 0.0)
                for scale in scales:
                    filt = collar_filter(shifted, local_vectors, scale)
                    raw = hermitian(np.kron(filt, identity_bc) @ rho_abc @ np.kron(filt, identity_bc))
                    mass = float(np.trace(raw).real)
                    if not (mass > tolerance and mass <= 1.0 + tolerance):
                        raise AssertionError("invalid filter mass")
                    mass_defect = 1.0 - mass
                    mass_bound = scale * moment
                    if mass_defect > mass_bound + tolerance:
                        raise AssertionError("mass moment inequality failed")
                    sigma = hermitian(raw / mass)
                    if abs(float(np.trace(sigma).real) - 1.0) > tolerance or float(np.min(np.linalg.eigvalsh(sigma)).real) < -positivity_tolerance:
                        raise AssertionError("invalid normalized filter")
                    sigma_ab = reduce_groups(sigma, list(dimensions), [0, 1])
                    sigma_b = reduce_groups(sigma, list(dimensions), [1])
                    sigma_bc = reduce_groups(sigma, list(dimensions), [1, 2])
                    recovered_sigma = petz(sigma_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    recovered_rho = petz(rho_ab, sigma_bc, sigma_b, dimensions, positivity_tolerance)
                    delta_abc = distance(rho_abc, sigma)
                    delta_ab = distance(rho_ab, sigma_ab)
                    projected = distance(sigma, recovered_sigma)
                    transported = distance(rho_abc, recovered_rho)
                    recovered_input = distance(recovered_rho, recovered_sigma)
                    budget = projected + delta_abc + delta_ab
                    two_delta = projected + 2.0 * delta_abc
                    envelope = float(np.sqrt(max(0.0, mass_defect)) + mass_defect / 2.0)
                    if delta_abc > envelope + tolerance or recovered_input > delta_ab + tolerance or delta_ab > delta_abc + tolerance or transported > budget + tolerance or transported > two_delta + tolerance:
                        raise AssertionError("independent finite inequality failed")
                    row = {"volume": volume, "dimension": dimension, "beta": beta, "orientation": partition["orientation"], "core_width": core_width, "buffer_width": buffer_width, "scale": scale, "moment": moment, "projection_mass": mass, "mass_defect": mass_defect, "mass_bound": mass_bound, "mass_slack": mass_bound - mass_defect, "delta_abc": delta_abc, "delta_ab": delta_ab, "candidate_envelope": envelope, "candidate_envelope_slack": envelope - delta_abc, "projected_error": projected, "transported_error": transported, "recovered_input_distance": recovered_input, "triangle_budget": budget, "two_delta_budget": two_delta}
                    rows.append(row)
                    mass_defects.append(mass_defect); moments.append(moment); mass_slacks.append(mass_bound - mass_defect); disturbances.append(delta_abc); envelopes.append(envelope); projected_errors.append(projected); transported_errors.append(transported); budgets.append(budget)
    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "system_count": len(pairs),
        "partition_count": sum(len(tripartitions(volume, widths, buffers)) for volume, _ in pairs),
        "row_count": len(rows),
        "beta_values": betas,
        "filter_scales": scales,
        "shifted_local_minimum": min(float(np.min(data[0])) for data in local_data.values()),
        "shifted_local_maximum": max(float(np.max(data[0])) for data in local_data.values()),
        "semigroup_residual_max": max(semigroup_residuals, default=0.0),
        "mass_min": min(1.0 - value for value in mass_defects),
        "mass_max": max(1.0 - value for value in mass_defects),
        "mass_defect_max": max(mass_defects),
        "moment_max": max(moments),
        "mass_bound_slack_min": min(mass_slacks),
        "disturbance_max": max(disturbances),
        "candidate_envelope_max": max(envelopes),
        "candidate_envelope_slack_min": min(float(row["candidate_envelope_slack"]) for row in rows),
        "projected_error_max": max(projected_errors),
        "transported_error_max": max(transported_errors),
        "triangle_budget_max": max(budgets),
        "normalization_violation_count": 0,
        "mass_violation_count": 0,
        "candidate_envelope_violation_count": 0,
        "contractivity_violation_count": 0,
        "triangle_violation_count": 0,
        "two_delta_violation_count": 0,
        "transport_profiles": profile(rows, "transported_error", tolerance),
        "disturbance_profiles": profile(rows, "delta_abc", tolerance)
    }
    payload = {"schema": "tect/pre-a-r397-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-397", "exploration_id": "EXP-001241", "verdict": "PASS", "checks": 6, "derived": derived}
    dump_atomic(output, payload)
    print(f"R-397 INDEPENDENT PASS 6/6 systems={len(pairs)} partitions={derived['partition_count']} rows={len(rows)} mass_defect_max={derived['mass_defect_max']:.6g} disturbance_max={derived['disturbance_max']:.6g} transport_max={derived['transported_error_max']:.6g} ratio_max={derived['transport_profiles']['maximum_adjacent_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
