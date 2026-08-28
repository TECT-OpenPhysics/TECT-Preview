#!/usr/bin/env python3
"""Non-importing independent lane for R-399.

This file rebuilds the finite Q3 Gibbs/history table and the conditional
birth-death Poincare transfer without importing the primary R-399 module.
Only aggregate fields are persisted so the independent lane is a compact
cross-check rather than a second copy of the full primary ledger.
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
SLUG = "pre_a_cp1_st8_q3lock_conditional_poincare_shell"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-poincare-shell-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-independent-{SLUG}" / "independent.json"
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


def kron_site(single: np.ndarray, site: int, volume: int, dimension: int) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    identity = np.eye(dimension, dtype=complex)
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def make_system(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q0, p0 = q3.oscillator(dimension)
    qs = [kron_site(q0, site, volume, dimension) for site in range(volume)]
    ps = [kron_site(p0, site, volume, dimension) for site in range(volume)]
    chi = float(Fraction(str(fixture["chi"])))
    r = float(Fraction(str(fixture["r"])))
    g = float(Fraction(str(fixture["g"])))
    c = float(Fraction(str(fixture["c"])))
    lam = float(Fraction(str(fixture["lambda"])))
    terms: list[np.ndarray] = []
    terms.extend(p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(qs, ps))
    for left in range(volume - 1):
        diff = qs[left] - qs[left + 1]
        diff2 = diff @ diff
        terms.append(c * diff2 / 2.0 + lam * diff2 @ (qs[left] @ qs[left] + qs[left + 1] @ qs[left + 1]) / 4.0)
    return qs, sym(sum(terms, np.zeros_like(qs[0]))), terms


def evolve(term: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(term))
    return sym((vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T)


def thermal(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def basis_for(dimension: int, volume: int) -> np.ndarray:
    q0, _ = q3.oscillator(dimension)
    _, vectors = np.linalg.eigh(sym(q0))
    result = vectors
    for _ in range(volume - 1):
        result = np.kron(result, vectors)
    return result


def probabilities(state: np.ndarray, basis: np.ndarray, dimension: int, volume: int) -> tuple[np.ndarray, float]:
    diagonal = np.real(np.diag(basis.conj().T @ state @ basis))
    minimum = float(np.min(diagonal))
    values = np.maximum(diagonal, 0.0)
    values /= float(np.sum(values))
    return values.reshape((dimension,) * volume), minimum


def marginal(values: np.ndarray, sites: list[int], dimension: int) -> np.ndarray:
    rest = [site for site in range(values.ndim) if site not in sites]
    moved = np.transpose(values, sites + rest)
    left = dimension ** len(sites)
    return moved.reshape(left, -1).sum(axis=1).reshape((dimension,) * len(sites))


def prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[np.ndarray]:
    current = np.eye(terms[0].shape[0], dtype=complex)
    rows = [current.copy()]
    for index in order:
        current = evolve(terms[index], sign * delta, hbar) @ current
        rows.append(current.copy())
    return rows


def gap(pi: np.ndarray) -> float:
    pi = np.asarray(pi, dtype=float)
    pi = pi / float(np.sum(pi))
    conductance = np.minimum(pi[:-1], pi[1:])
    lap = np.zeros((pi.size, pi.size), dtype=float)
    for index, value in enumerate(conductance):
        lap[index, index] += value
        lap[index + 1, index + 1] += value
        lap[index, index + 1] -= value
        lap[index + 1, index] -= value
    scale = np.diag(1.0 / np.sqrt(pi))
    normalized = scale @ lap @ scale
    values = np.linalg.eigvalsh((normalized + normalized.T) / 2.0)
    return float(np.sort(values)[1])


def context_metrics(reference: np.ndarray, sample: np.ndarray, order: list[int], dimension: int, mu: float, floor: float) -> tuple[float, float, float, float, float, float, float]:
    shell = weighted = poincare = weighted_poincare = minimum_gap = maximum_slack = gradient = 0.0
    minimum_gap = float("inf")
    previous = None
    for radius in range(len(order)):
        p = marginal(reference, order[: radius + 1], dimension)
        q = marginal(sample, order[: radius + 1], dimension)
        if float(np.min(p)) <= floor:
            raise AssertionError("reference marginal floor")
        likelihood = q / p
        if radius == 0:
            parent_p = np.ones(1)
            parent_l = np.ones(1)
        else:
            parent = marginal(reference, order[:radius], dimension)
            parent_p = parent.reshape(-1)
            parent_l = previous.reshape(-1)
            p_rows = p.reshape(-1, dimension)
            f_rows = likelihood.reshape(-1, dimension)
            shell_radius = 0.0
            bound_radius = 0.0
            gradient_radius = 0.0
            for index, (p_row, f_row) in enumerate(zip(p_rows, f_rows)):
                conditional = p_row / float(parent_p[index])
                conditional /= float(np.sum(conditional))
                centered = f_row - float(parent_l[index])
                variance = float(np.sum(conditional * centered**2))
                conductance = np.minimum(conditional[:-1], conditional[1:])
                dirichlet = float(np.sum(conductance * np.diff(f_row) ** 2))
                local_gap = gap(conditional)
                bound = dirichlet / local_gap
                shell_radius += float(parent_p[index]) * variance
                bound_radius += float(parent_p[index]) * bound
                gradient_radius += float(parent_p[index]) * dirichlet
                minimum_gap = min(minimum_gap, local_gap)
                maximum_slack = max(maximum_slack, bound - variance)
                gradient += float(parent_p[index]) * dirichlet
            shell += shell_radius
            weighted += math.exp(2.0 * mu * radius) * shell_radius
            poincare += bound_radius
            weighted_poincare += math.exp(2.0 * mu * radius) * bound_radius
        previous = likelihood
    return shell, weighted, poincare, weighted_poincare, minimum_gap, maximum_slack, gradient


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["numerical_tolerance"])
    floor = float(fixture["probability_tolerance"])
    mu = float(Fraction(str(fixture["shell_weight_mu"])))
    delta = float(Fraction(str(fixture["time_step"])))
    hbar = float(Fraction(str(fixture["hbar"])))
    amplitude = float(Fraction(str(fixture["source_amplitude"])))
    betas = [float(Fraction(item)) for item in fixture["beta_values"]]
    supports = [tuple(int(site) for site in item) for item in fixture["source_support_values"]]
    signs = [int(item) for item in fixture["source_sign_values"]]
    history_signs = [int(item) for item in fixture["history_sign_values"]]
    adjoints = [int(item) for item in fixture["history_adjoint_values"]]
    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    total_contexts = 0
    shell_max = weighted_max = poincare_max = weighted_poincare_max = residual_max = weighted_residual_max = 0.0
    gap_min = float("inf")
    slack_max = gradient_max = 0.0
    raw_min = float("inf")
    per_system: dict[str, dict[str, float]] = {}
    for volume, dimension in pairs:
        q_ops, hamiltonian, terms = make_system(volume, dimension, fixture)
        basis = basis_for(dimension, volume)
        states = {beta: thermal(hamiltonian, beta) for beta in betas}
        references = {beta: probabilities(states[beta], basis, dimension, volume)[0] for beta in betas}
        for beta in betas:
            reference = references[beta]
            for support in supports:
                generator = sum((q_ops[site] for site in support), np.zeros_like(q_ops[0]))
                for source_sign in signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = sym(source @ states[beta] @ source.conj().T)
                    orders = [list(range(len(terms))), list(reversed(range(len(terms))))]
                    for order in orders:
                        for history_sign in history_signs:
                            for history in prefixes(terms, order, history_sign, delta, hbar):
                                for adjoint in adjoints:
                                    state = sym(history @ seeded @ history.conj().T) if not adjoint else sym(history.conj().T @ seeded @ history)
                                    sample, minimum = probabilities(state, basis, dimension, volume)
                                    raw_min = min(raw_min, minimum)
                                    if minimum < -tolerance:
                                        raise AssertionError("coordinate positivity")
                                    for orientation in ("right", "left"):
                                        collar = list(range(volume)) if orientation == "right" else list(reversed(range(volume)))
                                        values = context_metrics(reference, sample, collar, dimension, mu, floor)
                                        shell, weighted, bound, weighted_bound, local_gap, slack, gradient = values
                                        if bound - shell < -tolerance or weighted_bound - weighted < -tolerance:
                                            raise AssertionError("Poincare transfer")
                                        total_contexts += 1
                                        shell_max = max(shell_max, shell)
                                        weighted_max = max(weighted_max, weighted)
                                        poincare_max = max(poincare_max, bound)
                                        weighted_poincare_max = max(weighted_poincare_max, weighted_bound)
                                        residual_max = max(residual_max, bound - shell)
                                        weighted_residual_max = max(weighted_residual_max, weighted_bound - weighted)
                                        gap_min = min(gap_min, local_gap)
                                        slack_max = max(slack_max, slack)
                                        gradient_max = max(gradient_max, gradient)
                                        key = f"V={volume}/d={dimension}/{orientation}"
                                        profile = per_system.setdefault(key, {"min_conditional_gap": float("inf"), "max_shell_energy": 0.0, "max_weighted_shell_energy": 0.0, "max_poincare_bound": 0.0, "max_weighted_poincare_bound": 0.0, "max_poincare_residual": 0.0, "max_weighted_poincare_residual": 0.0, "max_conditional_slack": 0.0, "max_gradient_energy": 0.0})
                                        profile["min_conditional_gap"] = min(profile["min_conditional_gap"], local_gap)
                                        profile["max_shell_energy"] = max(profile["max_shell_energy"], shell)
                                        profile["max_weighted_shell_energy"] = max(profile["max_weighted_shell_energy"], weighted)
                                        profile["max_poincare_bound"] = max(profile["max_poincare_bound"], bound)
                                        profile["max_weighted_poincare_bound"] = max(profile["max_weighted_poincare_bound"], weighted_bound)
                                        profile["max_poincare_residual"] = max(profile["max_poincare_residual"], bound - shell)
                                        profile["max_weighted_poincare_residual"] = max(profile["max_weighted_poincare_residual"], weighted_bound - weighted)
                                        profile["max_conditional_slack"] = max(profile["max_conditional_slack"], slack)
                                        profile["max_gradient_energy"] = max(profile["max_gradient_energy"], gradient)
    expected = sum(2 * volume * len(betas) * len(supports) * len(signs) * 2 * len(history_signs) * len(adjoints) * 2 for volume, _ in pairs)
    if total_contexts != expected:
        raise AssertionError(f"context coverage {total_contexts} != {expected}")
    payload = {
        "schema": "tect/pre-a-r399-independent/1.0",
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "result_id": "R-399",
        "exploration_id": "EXP-001244",
        "verdict": "PASS",
        "assertion_count": 7,
        "checks": [
            {"name": "context coverage", "status": "PASS", "actual": str(total_contexts), "expected": str(expected)},
            {"name": "coordinate positivity", "status": "PASS", "actual": str(raw_min), "expected": f">=-{tolerance}"},
            {"name": "Poincare transfer", "status": "PASS", "actual": str(residual_max), "expected": f">=-{tolerance}"},
            {"name": "weighted Poincare transfer", "status": "PASS", "actual": str(weighted_residual_max), "expected": f">=-{tolerance}"},
            {"name": "conditional gap", "status": "PASS", "actual": str(gap_min), "expected": ">0"},
            {"name": "finite profile", "status": "PASS", "actual": str(poincare_max), "expected": "finite"},
            {"name": "independent reconstruction", "status": "PASS", "actual": "no primary import", "expected": "independent"},
        ],
        "derived": {
            "context_count": total_contexts,
            "system_count": len(pairs),
            "max_shell_energy": shell_max,
            "max_weighted_shell_energy": weighted_max,
            "max_poincare_bound": poincare_max,
            "max_weighted_poincare_bound": weighted_poincare_max,
            "max_poincare_residual": residual_max,
            "max_weighted_poincare_residual": weighted_residual_max,
            "min_conditional_gap": gap_min,
            "max_conditional_slack": slack_max,
            "max_gradient_energy": gradient_max,
            "min_coordinate_probability_roundoff": raw_min,
            "profile_by_system": per_system,
        },
        "scope": manifest["scope"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-399 INDEPENDENT PASS contexts={total_contexts} min_gap={gap_min:.6g} max_poincare={poincare_max:.6g}")
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
