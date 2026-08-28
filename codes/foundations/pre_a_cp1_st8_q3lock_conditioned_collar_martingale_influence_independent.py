#!/usr/bin/env python3
"""Non-importing reconstruction of the R-398 conditioned-collar audit.

The primary implementation is not imported.  Only the registered oscillator
and bond primitives are reused; likelihood conditioning, collar marginals and
the Doob square-function bookkeeping are rebuilt independently.
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


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_conditioned_collar_martingale_influence"
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-conditioned-collar-martingale-influence-finite-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
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


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def build(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = q3.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    qs = [lift(q_single, site, volume, identity) for site in range(volume)]
    ps = [lift(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(str(fixture["chi"])))
    r = float(Fraction(str(fixture["r"])))
    g = float(Fraction(str(fixture["g"])))
    c = float(Fraction(str(fixture["c"])))
    lam = float(Fraction(str(fixture["lambda"])))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    bonds = []
    for site in range(volume - 1):
        difference = qs[site] - qs[site + 1]
        square = difference @ difference
        bonds.append(c * square / 2.0 + lam * square @ (qs[site] @ qs[site] + qs[site + 1] @ qs[site + 1]) / 4.0)
    zero = np.zeros_like(qs[0])
    return qs, sym(sum(onsite + bonds, zero)), onsite + bonds


def thermal(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def evolution(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(matrix))
    return sym((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


def product_coordinate_basis(dimension: int, volume: int) -> np.ndarray:
    q_single, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(sym(q_single))
    basis = vectors
    for _ in range(volume - 1):
        basis = np.kron(basis, vectors)
    return basis


def probabilities(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> np.ndarray:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    values = np.maximum(diagonal, 0.0)
    total = float(np.sum(values))
    if total <= 0.0:
        raise AssertionError("zero coordinate mass")
    return (values / total).reshape((dimension,) * volume)


def marginal(array: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(array.ndim) if site not in sites]
    rearranged = np.transpose(array, sites + rest)
    return rearranged.reshape(dimension ** len(sites), -1).sum(axis=1).reshape((dimension,) * len(sites))


def prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[tuple[int, np.ndarray]]:
    current = np.eye(terms[0].shape[0], dtype=complex)
    result = [(0, current.copy())]
    for position, term_index in enumerate(order, start=1):
        current = evolution(terms[term_index], sign * delta, hbar) @ current
        result.append((position, current.copy()))
    return result


def metrics(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, mu: float, floor: float) -> tuple[float, float, float, float, float]:
    local_p = marginal(reference, [order[0]], dimension)
    local_q = marginal(sample, [order[0]], dimension)
    if float(np.min(local_p)) <= floor:
        raise AssertionError("reference local mass below floor")
    local_ratio = local_q / local_p
    local_chi = float(np.sum(local_p * (local_ratio - 1.0) ** 2))
    local_q2 = float(np.sum(local_p * local_ratio**2))
    parent: np.ndarray | None = None
    shell = 0.0
    weighted = 0.0
    for radius in range(len(order)):
        sites = order[: radius + 1]
        p = marginal(reference, sites, dimension)
        q = marginal(sample, sites, dimension)
        if float(np.min(p)) <= floor:
            raise AssertionError("reference collar mass below floor")
        ratio = q / p
        baseline = np.ones_like(ratio) if radius == 0 else np.expand_dims(parent, axis=-1)  # type: ignore[arg-type]
        increment = ratio - baseline
        energy = float(np.sum(p * increment**2))
        if radius > 0:
            shell += energy
            weighted += math.exp(2.0 * mu * radius) * energy
        parent = ratio
    full_ratio = sample / reference
    global_chi = float(np.sum(reference * (full_ratio - 1.0) ** 2))
    residual = abs(global_chi - local_chi - shell)
    return local_q2, global_chi, shell, weighted, residual


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    mu = float(Fraction(str(fixture["shell_weight_mu"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    history_signs = [int(value) for value in fixture["history_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    orientations = list(fixture["orientations"])
    supports = [tuple(int(site) for site in support) for support in fixture["source_support_values"]]
    pairs = [(int(item["volume"]), int(dim)) for item in fixture["admissible_pairs"] for dim in item["cutoff_dimensions"]]
    context_count = 0
    max_identity = 0.0
    max_local_q2 = 0.0
    max_global_chi = 0.0
    max_shell = 0.0
    max_weighted = 0.0
    min_shell = float("inf")
    profile_by_system: dict[str, dict[str, float]] = {}
    for volume, dimension in pairs:
        qs, hamiltonian, terms = build(volume, dimension, fixture)
        basis = product_coordinate_basis(dimension, volume)
        states = {beta: thermal(hamiltonian, beta) for beta in betas}
        references = {beta: probabilities(states[beta], basis, dimension, volume) for beta in betas}
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        for beta in betas:
            for support in supports:
                generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = sym(source @ states[beta] @ source.conj().T)
                    for order_name, term_order in orders.items():
                        for history_sign in history_signs:
                            for prefix_length, prefix in prefixes(terms, term_order, history_sign, delta, hbar):
                                for history_adjoint in adjoints:
                                    state = sym(prefix @ seeded @ prefix.conj().T) if not history_adjoint else sym(prefix.conj().T @ seeded @ prefix)
                                    sample = probabilities(state, basis, dimension, volume)
                                    for orientation in orientations:
                                        collar_order = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                        local_q2, global_chi, shell, weighted, residual = metrics(references[beta], sample, collar_order, dimension, mu, floor)
                                        if residual > tolerance or local_q2 < 1.0 - tolerance or shell < -tolerance or weighted < -tolerance:
                                            raise AssertionError("finite independent decomposition check failed")
                                        context_count += 1
                                        max_identity = max(max_identity, residual)
                                        max_local_q2 = max(max_local_q2, local_q2)
                                        max_global_chi = max(max_global_chi, global_chi)
                                        max_shell = max(max_shell, shell)
                                        max_weighted = max(max_weighted, weighted)
                                        min_shell = min(min_shell, shell)
                                        key = f"V={volume}/d={dimension}/{orientation}"
                                        profile = profile_by_system.setdefault(key, {"max_local_q2": 0.0, "max_global_chi2": 0.0, "max_shell_energy": 0.0, "max_weighted_shell_energy": 0.0})
                                        profile["max_local_q2"] = max(profile["max_local_q2"], local_q2)
                                        profile["max_global_chi2"] = max(profile["max_global_chi2"], global_chi)
                                        profile["max_shell_energy"] = max(profile["max_shell_energy"], shell)
                                        profile["max_weighted_shell_energy"] = max(profile["max_weighted_shell_energy"], weighted)
    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "system_count": len(pairs),
        "context_count": context_count,
        "beta_values": betas,
        "source_support_values": [list(item) for item in supports],
        "prefix_policy": fixture["prefix_policy"],
        "orientation_values": orientations,
        "max_identity_residual": max_identity,
        "max_local_q2": max_local_q2,
        "max_global_chi2": max_global_chi,
        "max_shell_energy": max_shell,
        "max_weighted_shell_energy": max_weighted,
        "min_shell_energy": min_shell,
        "profile_by_system": profile_by_system,
        "finite_coordinate_likelihood_closed": True,
        "finite_local_q2_identity_closed": True,
        "finite_doob_shell_decomposition_closed": True,
        "finite_shell_influence_profile_closed": True,
        "phase_conditioned_influence_closed": False,
        "folded_positive_replica_domination_closed": False,
        "cutoff_independent_shell_bound_closed": False,
        "volume_independent_shell_bound_closed": False,
        "source_independent_shell_bound_closed": False,
        "common_core_closed": False,
        "common_alpha_closed": False,
        "actual_split_limit_closed": False,
        "hamiltonian_os_identification_closed": False,
        "kms_gns_gap_closed": False,
        "continuum_closed": False,
        "c6_closed": False,
        "sector_a_closed": False,
        "pre_a_closed": False,
    }
    payload = {"schema": "tect/pre-a-r398-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-398", "exploration_id": "EXP-001242", "verdict": "PASS", "derived": derived}
    atomic_json(output, payload)
    print(f"R-398 INDEPENDENT PASS contexts={context_count} max_identity={max_identity:.6g} max_local_q2={max_local_q2:.6g} max_weighted_shell={max_weighted:.6g}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
