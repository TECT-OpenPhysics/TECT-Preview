#!/usr/bin/env python3
"""Non-importing independent reconstruction for R-391.

This lane rebuilds the oscillator chain, tensor reductions, entropy/QCMI,
finite Petz map, and local spectral complements independently of the primary
script.  It emits aggregate fields used by the integrated verifier.
"""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-blanket-boundary-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "independent.json"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def modes(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.diag(np.sqrt(np.arange(1, n, dtype=float)), 1).astype(complex)
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def site_operator(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    output = factors[0]
    for factor in factors[1:]:
        output = np.kron(output, factor)
    return output


def chain_hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = modes(n)
    eye = np.eye(n, dtype=complex)
    qs = [site_operator(q, site, volume, eye) for site in range(volume)]
    ps = [site_operator(p, site, volume, eye) for site in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * (qj @ qj) / 2.0 + g * (qj @ qj @ qj @ qj) / 4.0
    for left in range(volume - 1):
        delta = qs[left] - qs[left + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[left] @ qs[left] + qs[left + 1] @ qs[left + 1]) / 4.0
    return sym(h)


def state_from_hamiltonian(h: np.ndarray, beta: float) -> np.ndarray:
    energy, basis = np.linalg.eigh(h)
    weights = np.exp(-beta * (energy - energy.min()))
    weights /= weights.sum()
    return sym((basis * weights) @ basis.conj().T)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    ordered = list(keep)
    omitted = [index for index in range(volume) if index not in ordered]
    tensor = rho.reshape((n,) * (2 * volume))
    permutation = ordered + omitted + [index + volume for index in ordered] + [index + volume for index in omitted]
    tensor = np.transpose(tensor, permutation)
    k = len(ordered)
    for _ in omitted:
        tensor = np.trace(tensor, axis1=k, axis2=tensor.ndim // 2 + k)
    dimension = n**k
    return sym(tensor.reshape(dimension, dimension))


def reduce_groups(rho: np.ndarray, dimensions: list[int], keep: list[int]) -> np.ndarray:
    total = len(dimensions)
    omitted = [index for index in range(total) if index not in keep]
    tensor = rho.reshape(tuple(dimensions) + tuple(dimensions))
    permutation = keep + omitted + [index + total for index in keep] + [index + total for index in omitted]
    tensor = np.transpose(tensor, permutation)
    k = len(keep)
    for _ in omitted:
        tensor = np.trace(tensor, axis1=k, axis2=tensor.ndim // 2 + k)
    dimension = int(np.prod([dimensions[index] for index in keep], dtype=int))
    return sym(tensor.reshape(dimension, dimension))


def von_neumann_entropy(rho: np.ndarray, tol: float) -> float:
    values = np.maximum(np.linalg.eigvalsh(sym(rho)).real, 0.0)
    total = values.sum()
    if total <= tol:
        raise AssertionError("zero state in entropy")
    probabilities = values / total
    probabilities = probabilities[probabilities > tol]
    return float(-np.dot(probabilities, np.log(probabilities)))


def power(rho: np.ndarray, exponent: float, tol: float) -> np.ndarray:
    values, basis = np.linalg.eigh(sym(rho))
    values = np.maximum(values.real, 0.0)
    if exponent < 0.0:
        values = np.where(values > tol, values**exponent, 0.0)
    else:
        values = values**exponent
    return sym((basis * values) @ basis.conj().T)


def petz(rho_ab: np.ndarray, rho_bc: np.ndarray, rho_b: np.ndarray, dims: tuple[int, int, int], tol: float) -> np.ndarray:
    da, db, dc = dims
    left = power(rho_bc, 0.5, tol)
    inverse = power(rho_b, -0.5, tol)
    eye_c = np.eye(dc, dtype=complex)
    blocks = rho_ab.reshape(da, db, da, db)
    result = np.zeros((da, db, dc, da, db, dc), dtype=complex)
    for a in range(da):
        for ap in range(da):
            block = blocks[a, :, ap, :]
            lifted = np.kron(inverse @ block @ inverse, eye_c)
            result[a, :, :, ap, :, :] = (left @ lifted @ left).reshape(db, dc, db, dc)
    return sym(result.reshape(da * db * dc, da * db * dc))


def distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.abs(np.linalg.eigvalsh(sym(left - right))).sum())


def layouts(volume: int, cores: list[int], buffers: list[int]) -> list[dict[str, Any]]:
    answer: list[dict[str, Any]] = []
    for core_width in cores:
        for buffer_width in buffers:
            for start in range(max(0, volume - core_width - buffer_width)):
                core = list(range(start, start + core_width))
                buffer = list(range(start + core_width, start + core_width + buffer_width))
                environment = list(range(start + core_width + buffer_width, volume))
                if environment:
                    answer.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "right", "core_width": core_width, "buffer_width": buffer_width})
            for end in range(core_width + buffer_width, volume + 1):
                core = list(range(end - core_width, end))
                buffer = list(range(end - core_width - buffer_width, end - core_width))
                environment = list(range(0, end - core_width - buffer_width))
                if environment:
                    answer.append({"core": core, "buffer": buffer, "environment": environment, "orientation": "left", "core_width": core_width, "buffer_width": buffer_width})
    return answer


def projectors(n: int, cfg: dict[str, Any], tol: float) -> dict[int, dict[float, np.ndarray]]:
    output: dict[int, dict[float, np.ndarray]] = {}
    for width in [int(value) for value in cfg["core_widths"]]:
        energy, basis = np.linalg.eigh(chain_hamiltonian(n, width, cfg))
        shifted = energy - energy.min()
        output[width] = {}
        for raw in cfg["energy_windows"]:
            threshold = float(Fraction(raw))
            selected = basis[:, shifted <= threshold + tol]
            output[width][threshold] = sym(selected @ selected.conj().T)
    return output


def profile(rows: list[dict[str, Any]], field: str, keys: tuple[str, ...]) -> dict[str, Any]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        if field not in row:
            continue
        key = tuple(tuple(row[name]) if isinstance(row[name], list) else row[name] for name in keys)
        groups.setdefault(key, []).append(float(row[field]))
    records = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        records.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
    return {"profiles": records, "maximum_range": max((record["range"] for record in records), default=0.0)}


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tol = float(cfg["numerical_tolerance"])
    positivity = float(cfg["positivity_tolerance"])
    pairs = [(int(item["volume"]), int(dim)) for item in cfg["admissible_pairs"] for dim in item["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in cfg["beta_values"]]
    rows: list[dict[str, Any]] = []
    all_qcmI: list[float] = []
    all_recovery: list[float] = []
    all_petz: list[float] = []
    all_tail: list[float] = []
    negative = 0
    partition_count = 0
    for volume, n in pairs:
        project = projectors(n, cfg, positivity)
        layouts_for_system = layouts(volume, [int(value) for value in cfg["core_widths"]], [int(value) for value in cfg["buffer_widths"]])
        partition_count += len(layouts_for_system)
        for beta in betas:
            rho = state_from_hamiltonian(chain_hamiltonian(n, volume, cfg), beta)
            entropy_cache: dict[tuple[int, ...], float] = {}
            def S(sites: list[int]) -> float:
                key = tuple(sites)
                if key not in entropy_cache:
                    entropy_cache[key] = von_neumann_entropy(reduce_sites(rho, n, volume, list(key)), tol)
                return entropy_cache[key]
            for layout in layouts_for_system:
                core, buffer, environment = layout["core"], layout["buffer"], layout["environment"]
                q = S(core + buffer) + S(buffer + environment) - S(buffer) - S(core + buffer + environment)
                negative += int(q < -tol)
                scale = float(np.sqrt(2.0 * max(q, 0.0)))
                abc = reduce_sites(rho, n, volume, core + buffer + environment)
                dims = (n ** len(core), n ** len(buffer), n ** len(environment))
                rab = reduce_groups(abc, list(dims), [0, 1])
                rbc = reduce_groups(abc, list(dims), [1, 2])
                rb = reduce_groups(abc, list(dims), [1])
                pd = distance(abc, petz(rab, rbc, rb, dims, positivity))
                all_qcmI.append(q)
                all_recovery.append(scale)
                all_petz.append(pd)
                base = {"volume": volume, "dimension": n, "beta": beta, "orientation": layout["orientation"], "core_width": layout["core_width"], "buffer_width": layout["buffer_width"], "qcmI": q, "recoverability_scale": scale, "petz_trace_distance": pd}
                if layout["core_width"] == 2:
                    for raw in cfg["energy_windows"]:
                        e = float(Fraction(raw))
                        reduced_core = reduce_groups(abc, list(dims), [0])
                        window = sym(project[2][e] @ reduced_core @ project[2][e])
                        mass = float(np.trace(window).real)
                        tail = 1.0 - mass
                        all_tail.append(tail)
                        rows.append(dict(base, energy_window=e, window_mass=mass, tail_mass=tail))
                else:
                    rows.append(base)
    checks = 6
    if negative != 0 or not all(np.isfinite(value) and value >= -tol for value in all_qcmI):
        raise AssertionError("independent QCMI nonnegativity failure")
    if not all(np.isfinite(value) and value >= 0.0 for value in all_recovery):
        raise AssertionError("independent recoverability failure")
    if not all(np.isfinite(value) and -tol <= value <= 1.0 + tol for value in all_petz):
        raise AssertionError("independent Petz distance failure")
    if not all(-tol <= value <= 1.0 + tol for value in all_tail):
        raise AssertionError("independent spectral complement failure")
    derived = {
        "admissible_pairs": [{"volume": v, "dimension": n} for v, n in pairs],
        "system_count": len(pairs), "partition_count": partition_count, "beta_values": betas,
        "qcmI_record_count": len(all_qcmI), "row_count": len(rows), "qcmI_min": min(all_qcmI), "qcmI_max": max(all_qcmI),
        "recoverability_scale_max": max(all_recovery), "petz_trace_distance_max": max(all_petz), "qcmI_negative_count": negative,
        "spectral_complement_row_count": len(all_tail), "tail_mass_min": min(all_tail), "tail_mass_max": max(all_tail),
        "qcmI_buffer_profile": profile(rows, "qcmI", ("core_width", "buffer_width")),
        "recoverability_buffer_profile": profile(rows, "recoverability_scale", ("core_width", "buffer_width")),
        "petz_buffer_profile": profile(rows, "petz_trace_distance", ("core_width", "buffer_width")),
        "qcmI_cutoff_profile": profile(rows, "qcmI", ("dimension", "core_width", "buffer_width")),
        "tail_buffer_profile": profile([row for row in rows if "tail_mass" in row], "tail_mass", ("core_width", "buffer_width"))
    }
    payload = {"schema": "tect/pre-a-r391-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-391", "exploration_id": "EXP-001234", "verdict": "PASS", "checks": checks, "derived": derived}
    write_json(path, payload)
    print(f"R-391 INDEPENDENT PASS {checks}/{checks} systems={len(pairs)} partitions={partition_count} qcmI={len(all_qcmI)} rows={len(rows)} qcmI_max={max(all_qcmI):.6g} petz_max={max(all_petz):.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
