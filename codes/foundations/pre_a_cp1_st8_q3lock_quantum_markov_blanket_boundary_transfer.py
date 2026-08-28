#!/usr/bin/env python3
"""Finite quantum-Markov blanket and spectral-complement stress for R-391.

The finite Gibbs state is reduced to contiguous core--buffer--environment
tripartitions.  Conditional mutual information (QCMI), a natural-log
recoverability scale, a finite Petz reconstruction diagnostic, and the local
spectral complement are recorded together.  This is a finite diagnostic only:
no buffer tail, cutoff-uniform estimate, or QFT promotion is asserted.
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


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-blanket-boundary-transfer-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "primary.json"


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
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    for site in range(volume):
        q = coordinates[site]
        p = momenta[site]
        hamiltonian += p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0
    for site in range(volume - 1):
        difference = coordinates[site] - coordinates[site + 1]
        difference2 = difference @ difference
        hamiltonian += c * difference2 / 2.0 + lam * difference2 @ (coordinates[site] @ coordinates[site] + coordinates[site + 1] @ coordinates[site + 1]) / 4.0
    return hermitian(hamiltonian)


def gibbs_from_spectrum(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def partial_trace_sites(state: np.ndarray, dimension: int, volume: int, keep: Iterable[int]) -> np.ndarray:
    """Partial trace for equal-dimensional tensor sites, preserving keep order."""
    kept = list(keep)
    if len(set(kept)) != len(kept) or any(site < 0 or site >= volume for site in kept):
        raise ValueError("invalid site list")
    rest = [site for site in range(volume) if site not in kept]
    axes = kept + rest + [site + volume for site in kept] + [site + volume for site in rest]
    tensor = np.transpose(state.reshape([dimension] * (2 * volume)), axes)
    kept_count = len(kept)
    for _ in rest:
        half = tensor.ndim // 2
        tensor = np.trace(tensor, axis1=kept_count, axis2=half + kept_count)
    size = dimension**kept_count
    return hermitian(tensor.reshape(size, size))


def partial_trace_groups(state: np.ndarray, dimensions: list[int], keep: Iterable[int]) -> np.ndarray:
    """Partial trace for a tensor product with possibly unequal group sizes."""
    kept = list(keep)
    count = len(dimensions)
    rest = [index for index in range(count) if index not in kept]
    axes = kept + rest + [index + count for index in kept] + [index + count for index in rest]
    tensor = np.transpose(state.reshape(dimensions + dimensions), axes)
    kept_count = len(kept)
    for _ in rest:
        half = tensor.ndim // 2
        tensor = np.trace(tensor, axis1=kept_count, axis2=half + kept_count)
    size = int(np.prod([dimensions[index] for index in kept], dtype=int))
    return hermitian(tensor.reshape(size, size))


def entropy(state: np.ndarray, tolerance: float) -> float:
    values = np.linalg.eigvalsh(hermitian(state)).real
    values = np.maximum(values, 0.0)
    total = float(np.sum(values))
    if total <= tolerance:
        raise AssertionError("entropy called on numerically zero state")
    probabilities = values / total
    positive = probabilities[probabilities > tolerance]
    return float(-np.sum(positive * np.log(positive)))


def spectral_power(matrix: np.ndarray, exponent: float, tolerance: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    clipped = np.maximum(values.real, 0.0)
    if exponent < 0.0:
        powered = np.where(clipped > tolerance, clipped**exponent, 0.0)
    else:
        powered = clipped**exponent
    return hermitian((vectors * powered) @ vectors.conj().T)


def petz_recovery(rho_ab: np.ndarray, rho_bc: np.ndarray, rho_b: np.ndarray, dimensions: tuple[int, int, int], tolerance: float) -> np.ndarray:
    """Apply the finite Petz map to the B block of rho_AB."""
    d_a, d_b, d_c = dimensions
    sqrt_bc = spectral_power(rho_bc, 0.5, tolerance)
    inverse_sqrt_b = spectral_power(rho_b, -0.5, tolerance)
    identity_c = np.eye(d_c, dtype=complex)
    blocks = rho_ab.reshape(d_a, d_b, d_a, d_b)
    recovered = np.zeros((d_a, d_b, d_c, d_a, d_b, d_c), dtype=complex)
    for left in range(d_a):
        for right in range(d_a):
            block = blocks[left, :, right, :]
            lifted = np.kron(inverse_sqrt_b @ block @ inverse_sqrt_b, identity_c)
            image = sqrt_bc @ lifted @ sqrt_bc
            recovered[left, :, :, right, :, :] = image.reshape(d_b, d_c, d_b, d_c)
    return hermitian(recovered.reshape(d_a * d_b * d_c, d_a * d_b * d_c))


def trace_distance(left: np.ndarray, right: np.ndarray) -> float:
    values = np.linalg.eigvalsh(hermitian(left - right)).real
    return float(0.5 * np.sum(np.abs(values)))


def tripartitions(volume: int, core_widths: list[int], buffer_widths: list[int]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for core_width in core_widths:
        for buffer_width in buffer_widths:
            # The environment is on the right; an omitted left exterior is traced out.
            for start in range(max(0, volume - core_width - buffer_width)):
                a = list(range(start, start + core_width))
                b = list(range(start + core_width, start + core_width + buffer_width))
                c = list(range(start + core_width + buffer_width, volume))
                if c:
                    records.append({"core": a, "buffer": b, "environment": c, "orientation": "right", "core_width": core_width, "buffer_width": buffer_width})
            # Mirror orientation: environment is on the left; an omitted right exterior is traced out.
            for end in range(core_width + buffer_width, volume + 1):
                a = list(range(end - core_width, end))
                b = list(range(end - core_width - buffer_width, end - core_width))
                c = list(range(0, end - core_width - buffer_width))
                if c:
                    records.append({"core": a, "buffer": b, "environment": c, "orientation": "left", "core_width": core_width, "buffer_width": buffer_width})
    return records


def local_projectors(dimension: int, fixture: dict[str, Any], tolerance: float) -> dict[int, dict[float, np.ndarray]]:
    result: dict[int, dict[float, np.ndarray]] = {}
    for width in [int(value) for value in fixture["core_widths"]]:
        values, vectors = np.linalg.eigh(build_system(dimension, width, fixture))
        shifted = values - float(np.min(values))
        result[width] = {}
        for raw in fixture["energy_windows"]:
            threshold = float(Fraction(raw))
            mask = shifted <= threshold + tolerance
            result[width][threshold] = hermitian((vectors[:, mask] @ vectors[:, mask].conj().T))
    return result


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    coverage = manifest["coverage"]
    scope = manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    positivity_tolerance = float(fixture["positivity_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001234" and manifest["result_id"] == "R-391" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001234/R-391/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all declared Markov and window rows", "coverage")
    finite_flags = ("finite_qcmI_nonnegativity_closed", "finite_recoverability_scale_closed", "finite_petz_diagnostic_closed", "finite_spectral_complement_profile_closed", "finite_buffer_width_stress_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite quantum-Markov blanket only", "all promoted flags false", "scope")

    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct volume/cutoff systems", "fixture")
    betas = [float(Fraction(raw)) for raw in fixture["beta_values"]]
    energies = [float(Fraction(raw)) for raw in fixture["energy_windows"]]

    row_records: list[dict[str, Any]] = []
    qcmI_values: list[float] = []
    recoverability_values: list[float] = []
    petz_values: list[float] = []
    tail_values: list[float] = []
    qcmI_negative = 0
    row_count = 0
    partition_count = 0
    system_cache: dict[tuple[int, int], tuple[np.ndarray, dict[int, dict[float, np.ndarray]]]] = {}
    entropy_cache: dict[tuple[int, int, float, tuple[int, ...]], float] = {}

    for volume, dimension in pairs:
        values, vectors = np.linalg.eigh(build_system(dimension, volume, fixture))
        projectors = local_projectors(dimension, fixture, positivity_tolerance)
        partition_rows = tripartitions(volume, [int(value) for value in fixture["core_widths"]], [int(value) for value in fixture["buffer_widths"]])
        partition_count += len(partition_rows)
        states = {beta: gibbs_from_spectrum(values, vectors, beta) for beta in betas}
        system_cache[(volume, dimension)] = (states[betas[0]], projectors)
        for beta in betas:
            state = states[beta]
            for partition in partition_rows:
                core = partition["core"]
                buffer = partition["buffer"]
                environment = partition["environment"]
                abc_sites = tuple(core + buffer + environment)
                a_sites = tuple(core)
                ab_sites = tuple(core + buffer)
                bc_sites = tuple(buffer + environment)
                b_sites = tuple(buffer)

                def cached_entropy(sites: tuple[int, ...]) -> float:
                    key = (volume, dimension, beta, tuple(sites))
                    if key not in entropy_cache:
                        entropy_cache[key] = entropy(partial_trace_sites(state, dimension, volume, sites), tolerance)
                    return entropy_cache[key]

                qcmI = cached_entropy(ab_sites) + cached_entropy(bc_sites) - cached_entropy(b_sites) - cached_entropy(abc_sites)
                qcmI_values.append(qcmI)
                if qcmI < -tolerance:
                    qcmI_negative += 1
                qcmI_for_scale = max(qcmI, 0.0)
                recoverability_scale = float(np.sqrt(2.0 * qcmI_for_scale))
                recoverability_values.append(recoverability_scale)

                dimensions = (dimension ** len(core), dimension ** len(buffer), dimension ** len(environment))
                rho_abc = partial_trace_sites(state, dimension, volume, abc_sites)
                rho_ab = partial_trace_groups(rho_abc, list(dimensions), [0, 1])
                rho_bc = partial_trace_groups(rho_abc, list(dimensions), [1, 2])
                rho_b = partial_trace_groups(rho_abc, list(dimensions), [1])
                recovered = petz_recovery(rho_ab, rho_bc, rho_b, dimensions, positivity_tolerance)
                petz_distance = trace_distance(rho_abc, recovered)
                petz_values.append(petz_distance)
                check(f"V={volume} d={dimension} beta={beta} {partition['orientation']} core={core} buffer={buffer} QCMI", np.isfinite(qcmI) and qcmI >= -tolerance, qcmI, ">=-numerical tolerance", "QCMI")
                check(f"V={volume} d={dimension} beta={beta} {partition['orientation']} recoverability", np.isfinite(recoverability_scale) and recoverability_scale >= 0.0, recoverability_scale, ">=0", "recoverability")
                check(f"V={volume} d={dimension} beta={beta} {partition['orientation']} Petz distance", np.isfinite(petz_distance) and -tolerance <= petz_distance <= 1.0 + tolerance, petz_distance, "[0,1]", "Petz")

                rho_core = partial_trace_groups(rho_abc, list(dimensions), [0])
                core_width = int(partition["core_width"])
                for energy in energies if core_width == 2 else [None]:
                    if energy is None:
                        continue
                    projector = projectors[core_width][energy]
                    window = hermitian(projector @ rho_core @ projector)
                    mass = float(np.trace(window).real)
                    tail = 1.0 - mass
                    rank = int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))
                    tail_values.append(tail)
                    check(f"V={volume} d={dimension} beta={beta} {partition['orientation']} core={core} E={energy} spectral complement", np.isfinite(mass) and np.isfinite(tail) and -tolerance <= mass <= 1.0 + tolerance and abs(mass + tail - 1.0) <= tolerance and rank > 0, [mass, tail, rank], "finite split and positive rank", "spectral complement")
                    check(f"V={volume} d={dimension} beta={beta} {partition['orientation']} core={core} E={energy} complement PSD", float(np.min(np.linalg.eigvalsh(window))) >= -positivity_tolerance, float(np.min(np.linalg.eigvalsh(window))), f">=-{positivity_tolerance}", "spectral complement")
                    row_count += 1
                    row_records.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": partition["orientation"], "core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": int(partition["buffer_width"]), "qcmI": qcmI, "recoverability_scale": recoverability_scale, "petz_trace_distance": petz_distance, "window_mass": mass, "tail_mass": tail, "window_rank": rank})

                if core_width == 1:
                    row_count += 1
                    row_records.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": partition["orientation"], "core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": int(partition["buffer_width"]), "qcmI": qcmI, "recoverability_scale": recoverability_scale, "petz_trace_distance": petz_distance})

    check("QCMI aggregate", len(qcmI_values) == partition_count * len(betas) and qcmI_negative == 0, [len(qcmI_values), qcmI_negative], [partition_count * len(betas), 0], "QCMI")
    check("recoverability aggregate", len(recoverability_values) == len(qcmI_values) and all(np.isfinite(value) for value in recoverability_values), len(recoverability_values), "one scale per QCMI row", "recoverability")
    check("Petz aggregate", len(petz_values) == len(qcmI_values) and all(-tolerance <= value <= 1.0 + tolerance for value in petz_values), len(petz_values), "one finite distance per QCMI row", "Petz")
    check("row aggregate", len(row_records) == row_count and row_count > 0, [len(row_records), row_count], "positive row count", "coverage")
    check("tail aggregate", len(tail_values) > 0 and min(tail_values) >= -tolerance and max(tail_values) <= 1.0 + tolerance, [len(tail_values), min(tail_values), max(tail_values)], "finite complement profile", "spectral complement")

    def profile(records: list[dict[str, Any]], field: str, key_fields: tuple[str, ...]) -> dict[str, Any]:
        groups: dict[tuple[Any, ...], list[float]] = {}
        for record in records:
            key = tuple(record[field_name] if not isinstance(record[field_name], list) else tuple(record[field_name]) for field_name in key_fields)
            if field in record:
                groups.setdefault(key, []).append(float(record[field]))
        rows: list[dict[str, Any]] = []
        for key, values_for_key in sorted(groups.items(), key=lambda item: str(item[0])):
            rows.append({"key": list(key), "count": len(values_for_key), "minimum": min(values_for_key), "maximum": max(values_for_key), "range": max(values_for_key) - min(values_for_key)})
        return {"profiles": rows, "maximum_range": max((row["range"] for row in rows), default=0.0)}

    qcmI_buffer_profile = profile(row_records, "qcmI", ("core_width", "buffer_width"))
    recoverability_buffer_profile = profile(row_records, "recoverability_scale", ("core_width", "buffer_width"))
    petz_buffer_profile = profile(row_records, "petz_trace_distance", ("core_width", "buffer_width"))
    qcmI_cutoff_profile = profile(row_records, "qcmI", ("dimension", "core_width", "buffer_width"))
    tail_buffer_profile = profile([record for record in row_records if "tail_mass" in record], "tail_mass", ("core_width", "buffer_width"))
    check("buffer stress finite", all(np.isfinite(value) for value in [qcmI_buffer_profile["maximum_range"], recoverability_buffer_profile["maximum_range"], petz_buffer_profile["maximum_range"]]), [qcmI_buffer_profile["maximum_range"], recoverability_buffer_profile["maximum_range"], petz_buffer_profile["maximum_range"]], "finite diagnostic", "buffer stress")

    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "system_count": len(pairs),
        "partition_count": partition_count,
        "beta_values": betas,
        "qcmI_record_count": len(qcmI_values),
        "row_count": len(row_records),
        "qcmI_min": min(qcmI_values),
        "qcmI_max": max(qcmI_values),
        "recoverability_scale_max": max(recoverability_values),
        "petz_trace_distance_max": max(petz_values),
        "qcmI_negative_count": qcmI_negative,
        "spectral_complement_row_count": len(tail_values),
        "tail_mass_min": min(tail_values),
        "tail_mass_max": max(tail_values),
        "qcmI_buffer_profile": qcmI_buffer_profile,
        "recoverability_buffer_profile": recoverability_buffer_profile,
        "petz_buffer_profile": petz_buffer_profile,
        "qcmI_cutoff_profile": qcmI_cutoff_profile,
        "tail_buffer_profile": tail_buffer_profile
    }
    payload = {"schema": "tect/pre-a-r391-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-391", "exploration_id": "EXP-001234", "verdict": "PASS", "checks": checks, "derived": derived, "scope": scope, "records": row_records}
    atomic_json(output, payload)
    print(f"R-391 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={partition_count} qcmI={len(qcmI_values)} rows={len(row_records)} qcmI_max={max(qcmI_values):.6g} petz_max={max(petz_values):.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
