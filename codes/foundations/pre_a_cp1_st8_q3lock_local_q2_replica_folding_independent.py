#!/usr/bin/env python3
"""Non-importing finite-Q3 reconstruction for EXP-001204 / R-362."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_replica_folding"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-replica-folding-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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


def clean(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for level in range(1, size):
        lowering[level - 1, level] = np.sqrt(float(level))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def tensor_site(operator: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for position in range(volume):
        result = np.kron(result, operator if position == site else identity)
    return result


def spectral_unitary(generator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(clean(generator))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def coordinate_character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(clean(generator))
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def build_system(size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray], np.ndarray]:
    volume = 2
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_site(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_site(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    c = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    difference = q_ops[0] - q_ops[1]
    bond = c * difference @ difference / 2.0 + lam * (difference @ difference) @ (q_ops[0] @ q_ops[0] + q_ops[1] @ q_ops[1]) / 4.0
    terms = onsite + [clean(bond)]
    hamiltonian = clean(sum(terms, np.zeros_like(terms[0])))
    return q_ops, hamiltonian, terms, q_single


def thermal_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(clean(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return clean((vectors * weights) @ vectors.conj().T)


def site_reduce(state: np.ndarray, size: int, site: int) -> np.ndarray:
    tensor = state.reshape(size, size, size, size)
    reduced = np.zeros((size, size), dtype=complex)
    if site == 0:
        for outside in range(size):
            reduced += tensor[:, outside, :, outside]
    else:
        for outside in range(size):
            reduced += tensor[outside, :, outside, :]
    return clean(reduced)


def local_pvm(q_single: np.ndarray) -> list[np.ndarray]:
    _, vectors = np.linalg.eigh(clean(q_single))
    return [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(vectors.shape[1])]


def probabilities(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    values = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(values)) < -tolerance:
        raise AssertionError("independent negative local probability")
    values = np.maximum(values, 0.0)
    return values / float(np.sum(values))


def q2(reference: np.ndarray, sample: np.ndarray) -> float:
    return float(np.dot(sample * sample, 1.0 / reference))


def witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    result = np.zeros((len(reference) ** 2, len(reference) ** 2), dtype=complex)
    for index in range(len(reference)):
        result += np.kron(projectors[index], projectors[index]) / reference[index]
    return clean(result)


def all_prefixes(terms: list[np.ndarray], ordering: list[int], time_sign: int, delta: float, hbar: float) -> list[np.ndarray]:
    product = np.eye(terms[0].shape[0], dtype=complex)
    result = [product.copy()]
    for term_index in ordering:
        product = spectral_unitary(terms[term_index], time_sign * delta, hbar) @ product
        result.append(product.copy())
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    cutoffs = [int(value) for value in fixture["cutoff_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    supports = [tuple(row) for row in fixture["source_support_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    time_signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    amplitude = float(Fraction(fixture["source_amplitude"]))
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    witness_tolerance = float(fixture["noncommutation_witness_tolerance"])
    assertion_count = 0
    assertions: list[dict[str, Any]] = []

    def verify(name: str, condition: bool, actual: Any, expected: Any) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(assertions) < 72:
            assertions.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    verify("authority", manifest["exploration_id"] == "EXP-001204" and manifest["result_id"] == "R-362" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001204/R-362/false")
    context_count = 0
    site_row_count = 0
    max_replica_error = 0.0
    max_outcome_error = 0.0
    max_reference_error = 0.0
    max_heisenberg_error = 0.0
    minimum_witness_eigenvalue = float("inf")
    max_source_invariance_error = 0.0
    max_pure_bond_invariance_error = 0.0
    max_coordinate_commutator = 0.0
    interspersed: list[float] = []
    mixture_cache: dict[tuple[int, str, int], tuple[np.ndarray, np.ndarray]] = {}

    for size in cutoffs:
        q_ops, hamiltonian, terms, q_single = build_system(size, fixture["parameters"])
        projectors = local_pvm(q_single)
        identity_single = np.eye(size, dtype=complex)
        orders = {"forward": list(range(len(terms))), "reverse": list(range(len(terms) - 1, -1, -1))}
        banks = {(name, sign): all_prefixes(terms, order, sign, delta, hbar) for name, order in orders.items() for sign in time_signs}
        embedded = [[tensor_site(projector, site, 2, identity_single) for projector in projectors] for site in range(2)]
        bond = spectral_unitary(terms[-1], delta, hbar)
        for site in range(2):
            for projector in embedded[site]:
                max_coordinate_commutator = max(max_coordinate_commutator, float(np.linalg.norm(bond @ projector - projector @ bond, ord="fro")))

        for beta_fraction in betas:
            rho = thermal_state(hamiltonian, float(beta_fraction))
            ref_reduced = [site_reduce(rho, size, site) for site in range(2)]
            refs = [probabilities(reduced, projectors, tolerance) for reduced in ref_reduced]
            folds = [witness(refs[site], projectors) for site in range(2)]
            for site in range(2):
                reference_value = float(np.trace(folds[site] @ np.kron(ref_reduced[site], ref_reduced[site])).real)
                max_reference_error = max(max_reference_error, abs(reference_value - 1.0))
                minimum_witness_eigenvalue = min(minimum_witness_eigenvalue, float(np.min(np.linalg.eigvalsh(folds[site]))))
                verify(f"d={size} beta={beta_fraction} site={site} reference", abs(reference_value - 1.0) <= tolerance * 40, reference_value, "1")

            for support in supports:
                generator = sum((q_ops[int(site)] for site in support), np.zeros_like(q_ops[0]))
                for source_sign in source_signs:
                    source = coordinate_character(generator, source_sign * amplitude, hbar)
                    seeded = source @ rho @ source.conj().T
                    for site in range(2):
                        source_probs = probabilities(site_reduce(seeded, size, site), projectors, tolerance)
                        max_source_invariance_error = max(max_source_invariance_error, float(np.max(np.abs(source_probs - refs[site]))))
                    for adjoint in adjoints:
                        bond_state = bond @ seeded @ bond.conj().T if not adjoint else bond.conj().T @ seeded @ bond
                        for site in range(2):
                            bond_probs = probabilities(site_reduce(bond_state, size, site), projectors, tolerance)
                            max_pure_bond_invariance_error = max(max_pure_bond_invariance_error, float(np.max(np.abs(bond_probs - refs[site]))))

                    for order_name, order in orders.items():
                        for time_sign in time_signs:
                            for prefix_length, product in enumerate(banks[(order_name, time_sign)]):
                                for adjoint in adjoints:
                                    effective = product @ source if not adjoint else product.conj().T @ source
                                    output = effective @ rho @ effective.conj().T
                                    context_count += 1
                                    for site in range(2):
                                        site_row_count += 1
                                        reduced = site_reduce(output, size, site)
                                        sample = probabilities(reduced, projectors, tolerance)
                                        direct = q2(refs[site], sample)
                                        folded = float(np.trace(folds[site] @ np.kron(reduced, reduced)).real)
                                        error = abs(direct - folded)
                                        max_replica_error = max(max_replica_error, error)
                                        local_outcome_error = 0.0
                                        doubled = np.kron(reduced, reduced)
                                        for value, projector in zip(sample, projectors):
                                            local_outcome_error = max(local_outcome_error, abs(float(np.trace(np.kron(projector, projector) @ doubled).real) - value * value))
                                        max_outcome_error = max(max_outcome_error, local_outcome_error)
                                        verify(f"d={size} beta={beta_fraction} ctx={context_count} site={site} fold", error <= tolerance * 80, error, f"<={tolerance * 80}")
                                        verify(f"d={size} beta={beta_fraction} ctx={context_count} site={site} collision", direct >= 1.0 - tolerance * 20 and np.isfinite(direct), direct, ">=1 finite")
                                        if size == cutoffs[0] and beta_fraction == betas[0] and support == supports[0] and source_sign == source_signs[-1] and order_name == "forward" and time_sign == time_signs[-1] and prefix_length == len(terms):
                                            global_fold = np.zeros((hamiltonian.shape[0] ** 2,) * 2, dtype=complex)
                                            for probability, projector in zip(refs[site], embedded[site]):
                                                global_fold += np.kron(projector, projector) / probability
                                            effective_two = np.kron(effective, effective)
                                            heisenberg = float(np.trace(np.kron(rho, rho) @ effective_two.conj().T @ global_fold @ effective_two).real)
                                            max_heisenberg_error = max(max_heisenberg_error, abs(heisenberg - direct))
                                        if support == supports[0] and source_sign == source_signs[-1] and order_name == "reverse" and time_sign == time_signs[-1] and prefix_length == len(terms) and adjoint == 0:
                                            mixture_cache[(size, str(beta_fraction), site)] = (refs[site].copy(), sample.copy())

            global_fold = np.zeros((hamiltonian.shape[0] ** 2,) * 2, dtype=complex)
            for probability, projector in zip(refs[0], embedded[0]):
                global_fold += np.kron(projector, projector) / probability
            onsite = spectral_unitary(terms[0], delta, hbar)
            onsite_two = np.kron(onsite, onsite)
            bond_two = np.kron(bond, bond)
            moved = onsite_two.conj().T @ global_fold @ onsite_two
            interspersed.append(float(np.linalg.norm(bond_two @ moved - moved @ bond_two, ord="fro")))

    mixture_max_identity_error = 0.0
    mixture_min_slack = float("inf")
    mixture_rows = 0
    for size in cutoffs:
        for site in range(2):
            p1, q1 = mixture_cache[(size, str(betas[0]), site)]
            p2, q2_values = mixture_cache[(size, str(betas[1]), site)]
            p_mix = (p1 + p2) / 2.0
            q_mix = (q1 + q2_values) / 2.0
            mixture_value = q2(p_mix, q_mix)
            component_value = (q2(p1, q1) + q2(p2, q2_values)) / 2.0
            mixture_min_slack = min(mixture_min_slack, component_value - mixture_value)
            for a, b, c, d in zip(p1, p2, q1, q2_values):
                left_gap = c * c / (2.0 * a) + d * d / (2.0 * b) - ((c + d) / 2.0) ** 2 / ((a + b) / 2.0)
                right_gap = 0.25 * (b * c - a * d) ** 2 / (a * b * ((a + b) / 2.0))
                mixture_max_identity_error = max(mixture_max_identity_error, abs(left_gap - right_gap))
                mixture_rows += 1

    expected_contexts = len(cutoffs) * len(betas) * len(supports) * len(source_signs) * len(orders) * len(time_signs) * (len(terms) + 1) * len(adjoints)
    verify("contexts", context_count == expected_contexts, context_count, expected_contexts)
    verify("site rows", site_row_count == 2 * context_count, site_row_count, 2 * context_count)
    verify("source invariance", max_source_invariance_error <= tolerance * 50, max_source_invariance_error, f"<={tolerance * 50}")
    verify("bond invariance", max_pure_bond_invariance_error <= tolerance * 80, max_pure_bond_invariance_error, f"<={tolerance * 80}")
    verify("coordinate commutator", max_coordinate_commutator <= tolerance * 80, max_coordinate_commutator, f"<={tolerance * 80}")
    verify("interspersed witness", min(interspersed) > witness_tolerance, min(interspersed), f">{witness_tolerance}")
    verify("mixture identity", mixture_max_identity_error <= tolerance * 80, mixture_max_identity_error, f"<={tolerance * 80}")
    verify("mixture convexity", mixture_min_slack >= -tolerance * 80, mixture_min_slack, f">={-tolerance * 80}")
    verify("Heisenberg", max_heisenberg_error <= tolerance * 200, max_heisenberg_error, f"<={tolerance * 200}")
    verify("positive witness", minimum_witness_eigenvalue >= -tolerance * 80, minimum_witness_eigenvalue, f">={-tolerance * 80}")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-REPLICA-FOLDING",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": assertions,
        "derived": {
            "context_count": context_count,
            "site_row_count": site_row_count,
            "mixture_row_count": mixture_rows,
            "max_replica_error": max_replica_error,
            "max_outcome_replica_error": max_outcome_error,
            "max_reference_error": max_reference_error,
            "max_heisenberg_error": max_heisenberg_error,
            "minimum_witness_eigenvalue": minimum_witness_eigenvalue,
            "max_source_invariance_error": max_source_invariance_error,
            "max_pure_bond_invariance_error": max_pure_bond_invariance_error,
            "max_coordinate_commutator": max_coordinate_commutator,
            "minimum_interspersed_commutator_witness": min(interspersed),
            "mixture_max_identity_error": mixture_max_identity_error,
            "mixture_min_slack": mixture_min_slack,
            "folding_equality_constant": 1,
            "finite_replica_identity_closed": True,
            "finite_positive_folding_closed": True,
            "finite_common_weight_mixture_convexity_closed": True,
            "finite_diagonal_outer_peel_closed": True,
            "positive_Euclidean_path_measure_constructed": False,
            "local_collar_bound_proved": False,
            "phase_weight_preservation_proved": False,
            "phase_conditioned_influence_contraction_proved": False,
            "cutoff_uniformity_proved": False,
            "volume_uniformity_proved": False,
            "history_uniformity_proved": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-Q2 REPLICA FOLDING PASS {payload['assertion_count']}/{payload['assertion_count']} rows={payload['derived']['site_row_count']} maxerr={payload['derived']['max_replica_error']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
