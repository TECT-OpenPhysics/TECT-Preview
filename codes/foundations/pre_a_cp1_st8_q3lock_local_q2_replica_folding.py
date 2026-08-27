#!/usr/bin/env python3
"""Primary finite-Q3 verifier for EXP-001204 / R-362.

The script checks the exact local-PVM two-copy collision witness on every
prefix of a declared finite Q3 split product. It also checks source/pure-bond
coordinate invariance, the terminal diagonal peel, common-weight mixture
convexity, and a nonzero bond/onsite interspersed commutator witness. All
limiting and QFT promotions remain false in the output firewall.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_q2_replica_folding"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-replica-folding-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress as base  # noqa: E402
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


def pvm(q_single: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    values, vectors = np.linalg.eigh(base.hermitian(q_single))
    projectors = [np.outer(vectors[:, index], vectors[:, index].conj()) for index in range(len(values))]
    return values, projectors


def measured(reduced: np.ndarray, projectors: list[np.ndarray], tolerance: float) -> np.ndarray:
    probabilities = np.array([float(np.trace(projector @ reduced).real) for projector in projectors])
    if float(np.min(probabilities)) < -tolerance:
        raise AssertionError(f"negative measured probability {float(np.min(probabilities))}")
    probabilities = np.maximum(probabilities, 0.0)
    probabilities /= float(np.sum(probabilities))
    return probabilities


def collision(reference: np.ndarray, sample: np.ndarray) -> float:
    return float(np.sum(sample * sample / reference))


def collision_witness(reference: np.ndarray, projectors: list[np.ndarray]) -> np.ndarray:
    witness = np.zeros((projectors[0].shape[0] ** 2,) * 2, dtype=complex)
    for probability, projector in zip(reference, projectors):
        witness += np.kron(projector, projector) / probability
    return base.hermitian(witness)


def prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float) -> list[np.ndarray]:
    current = np.eye(terms[0].shape[0], dtype=complex)
    rows = [current.copy()]
    for index in order:
        current = base.unitary(terms[index], sign * delta, hbar) @ current
        rows.append(current.copy())
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    volume = int(fixture["volume"])
    cutoffs = [int(value) for value in fixture["cutoff_values"]]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    supports = [tuple(int(site) for site in row) for row in fixture["source_support_values"]]
    source_signs = [int(value) for value in fixture["source_sign_values"]]
    time_signs = [int(value) for value in fixture["time_sign_values"]]
    adjoints = [int(value) for value in fixture["history_adjoint_values"]]
    parameters = fixture["parameters"]
    amplitude = float(Fraction(fixture["source_amplitude"]))
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    tolerance = float(fixture["finite_tolerance"])
    witness_tolerance = float(fixture["noncommutation_witness_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 72:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001204" and manifest["result_id"] == "R-362", [manifest["exploration_id"], manifest["result_id"]], "EXP-001204/R-362", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite fixture", volume == 2 and fixture["prefix_policy"] == "every prefix", [volume, fixture["prefix_policy"]], "V=2/every prefix", "fixture")

    context_count = 0
    site_row_count = 0
    max_replica_error = 0.0
    max_outcome_replica_error = 0.0
    max_reference_error = 0.0
    max_heisenberg_error = 0.0
    minimum_witness_eigenvalue = float("inf")
    max_source_invariance_error = 0.0
    max_pure_bond_invariance_error = 0.0
    max_coordinate_commutator = 0.0
    interspersed_witnesses: list[float] = []
    mixture_cache: dict[tuple[int, str, int], tuple[np.ndarray, np.ndarray]] = {}

    for size in cutoffs:
        qs, hamiltonian, terms = base.split_system(volume, size, parameters)
        q_single, _ = q3.oscillator(size)
        _, projectors = pvm(q_single)
        identity_single = np.eye(size, dtype=complex)
        identity_full = np.eye(hamiltonian.shape[0], dtype=complex)
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        prefix_bank = {(name, sign): prefixes(terms, order, sign, delta, hbar) for name, order in orders.items() for sign in time_signs}
        embedded_projectors = [[base.embed(projector, site, volume, identity_single) for projector in projectors] for site in range(volume)]
        bond = base.unitary(terms[-1], delta, hbar)

        for site in range(volume):
            for projector in embedded_projectors[site]:
                max_coordinate_commutator = max(max_coordinate_commutator, float(np.linalg.norm(bond @ projector - projector @ bond, ord="fro")))

        for beta_fraction in betas:
            rho = base.gibbs(hamiltonian, float(beta_fraction))
            reference_reduced = [base.reduced_site(rho, size, volume, site) for site in range(volume)]
            references = [measured(reduced, projectors, tolerance) for reduced in reference_reduced]
            witnesses = [collision_witness(reference, projectors) for reference in references]
            for site in range(volume):
                replica_reference = float(np.trace(witnesses[site] @ np.kron(reference_reduced[site], reference_reduced[site])).real)
                max_reference_error = max(max_reference_error, abs(replica_reference - 1.0))
                minimum_witness_eigenvalue = min(minimum_witness_eigenvalue, float(np.min(np.linalg.eigvalsh(witnesses[site]))))
                check(f"d={size} beta={beta_fraction} site={site} reference", abs(replica_reference - 1.0) <= tolerance * 40, replica_reference, "1", "replica reference")

            for support in supports:
                generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                for source_sign in source_signs:
                    source = q3.character(generator, source_sign * amplitude, hbar)
                    seeded = source @ rho @ source.conj().T
                    for site in range(volume):
                        seeded_probabilities = measured(base.reduced_site(seeded, size, volume, site), projectors, tolerance)
                        max_source_invariance_error = max(max_source_invariance_error, float(np.max(np.abs(seeded_probabilities - references[site]))))
                    for bond_adjoint in adjoints:
                        pure_bond = bond @ seeded @ bond.conj().T if not bond_adjoint else bond.conj().T @ seeded @ bond
                        for site in range(volume):
                            pure_probabilities = measured(base.reduced_site(pure_bond, size, volume, site), projectors, tolerance)
                            max_pure_bond_invariance_error = max(max_pure_bond_invariance_error, float(np.max(np.abs(pure_probabilities - references[site]))))

                    for order_name, order in orders.items():
                        for time_sign in time_signs:
                            for prefix_length, prefix in enumerate(prefix_bank[(order_name, time_sign)]):
                                for history_adjoint in adjoints:
                                    effective = prefix @ source if not history_adjoint else prefix.conj().T @ source
                                    state = effective @ rho @ effective.conj().T
                                    context_count += 1
                                    for site in range(volume):
                                        site_row_count += 1
                                        reduced = base.reduced_site(state, size, volume, site)
                                        sample = measured(reduced, projectors, tolerance)
                                        direct = collision(references[site], sample)
                                        replica = float(np.trace(witnesses[site] @ np.kron(reduced, reduced)).real)
                                        replica_error = abs(direct - replica)
                                        max_replica_error = max(max_replica_error, replica_error)
                                        outcome_error = 0.0
                                        for probability, projector in zip(sample, projectors):
                                            folded = float(np.trace(np.kron(projector, projector) @ np.kron(reduced, reduced)).real)
                                            outcome_error = max(outcome_error, abs(folded - probability * probability))
                                        max_outcome_replica_error = max(max_outcome_replica_error, outcome_error)
                                        check(f"d={size} beta={beta_fraction} ctx={context_count} site={site} replica", replica_error <= tolerance * 80, replica_error, f"<={tolerance * 80}", "replica identity")
                                        check(f"d={size} beta={beta_fraction} ctx={context_count} site={site} positive", direct >= 1.0 - tolerance * 20 and np.isfinite(direct), direct, ">=1 finite", "collision")

                                        if size == cutoffs[0] and beta_fraction == betas[0] and support == supports[0] and source_sign == source_signs[-1] and order_name == "forward" and time_sign == time_signs[-1] and prefix_length == len(terms):
                                            global_witness = np.zeros((hamiltonian.shape[0] ** 2,) * 2, dtype=complex)
                                            for probability, projector in zip(references[site], embedded_projectors[site]):
                                                global_witness += np.kron(projector, projector) / probability
                                            effective_two = np.kron(effective, effective)
                                            heisenberg = float(np.trace(np.kron(rho, rho) @ effective_two.conj().T @ global_witness @ effective_two).real)
                                            max_heisenberg_error = max(max_heisenberg_error, abs(heisenberg - direct))

                                        if support == supports[0] and source_sign == source_signs[-1] and order_name == "reverse" and time_sign == time_signs[-1] and prefix_length == len(terms) and history_adjoint == 0:
                                            mixture_cache[(size, str(beta_fraction), site)] = (references[site].copy(), sample.copy())

            site = 0
            global_witness = np.zeros((hamiltonian.shape[0] ** 2,) * 2, dtype=complex)
            for probability, projector in zip(references[site], embedded_projectors[site]):
                global_witness += np.kron(projector, projector) / probability
            onsite = base.unitary(terms[site], delta, hbar)
            onsite_two = np.kron(onsite, onsite)
            bond_two = np.kron(bond, bond)
            moved_witness = onsite_two.conj().T @ global_witness @ onsite_two
            interspersed_witnesses.append(float(np.linalg.norm(bond_two @ moved_witness - moved_witness @ bond_two, ord="fro")))

    mixture_max_identity_error = 0.0
    mixture_min_slack = float("inf")
    mixture_rows = 0
    weight_one = Fraction(1, 2)
    weight_two = Fraction(1, 2)
    for size in cutoffs:
        for site in range(volume):
            p_one, q_one = mixture_cache[(size, str(betas[0]), site)]
            p_two, q_two = mixture_cache[(size, str(betas[1]), site)]
            p_mix = float(weight_one) * p_one + float(weight_two) * p_two
            q_mix = float(weight_one) * q_one + float(weight_two) * q_two
            mixture_collision = collision(p_mix, q_mix)
            component_collision = float(weight_one) * collision(p_one, q_one) + float(weight_two) * collision(p_two, q_two)
            mixture_min_slack = min(mixture_min_slack, component_collision - mixture_collision)
            for p1, p2, q1, q2 in zip(p_one, p_two, q_one, q_two):
                lhs_gap = float(weight_one) * q1 * q1 / p1 + float(weight_two) * q2 * q2 / p2 - (float(weight_one) * q1 + float(weight_two) * q2) ** 2 / (float(weight_one) * p1 + float(weight_two) * p2)
                rhs_gap = float(weight_one * weight_two) * (p2 * q1 - p1 * q2) ** 2 / (p1 * p2 * (float(weight_one) * p1 + float(weight_two) * p2))
                mixture_max_identity_error = max(mixture_max_identity_error, abs(lhs_gap - rhs_gap))
                mixture_rows += 1

    expected_contexts = len(cutoffs) * len(betas) * len(supports) * len(source_signs) * len(orders) * len(time_signs) * (len(terms) + 1) * len(adjoints)
    check("context count", context_count == expected_contexts, context_count, expected_contexts, "coverage")
    check("site row count", site_row_count == context_count * volume, site_row_count, context_count * volume, "coverage")
    check("source invariance", max_source_invariance_error <= tolerance * 50, max_source_invariance_error, f"<={tolerance * 50}", "diagonal peel")
    check("pure bond invariance", max_pure_bond_invariance_error <= tolerance * 80, max_pure_bond_invariance_error, f"<={tolerance * 80}", "diagonal peel")
    check("bond PVM commutator", max_coordinate_commutator <= tolerance * 80, max_coordinate_commutator, f"<={tolerance * 80}", "diagonal peel")
    check("interspersed witness", min(interspersed_witnesses) > witness_tolerance, min(interspersed_witnesses), f">{witness_tolerance}", "open collar")
    check("mixture identity", mixture_max_identity_error <= tolerance * 80, mixture_max_identity_error, f"<={tolerance * 80}", "mixture")
    check("mixture convexity", mixture_min_slack >= -tolerance * 80, mixture_min_slack, f">={-tolerance * 80}", "mixture")
    check("Heisenberg replica", max_heisenberg_error <= tolerance * 200, max_heisenberg_error, f"<={tolerance * 200}", "Heisenberg folding")
    check("positive witness", minimum_witness_eigenvalue >= -tolerance * 80, minimum_witness_eigenvalue, f">={-tolerance * 80}", "positivity")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-REPLICA-FOLDING",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "context_count": context_count,
            "site_row_count": site_row_count,
            "mixture_row_count": mixture_rows,
            "max_replica_error": max_replica_error,
            "max_outcome_replica_error": max_outcome_replica_error,
            "max_reference_error": max_reference_error,
            "max_heisenberg_error": max_heisenberg_error,
            "minimum_witness_eigenvalue": minimum_witness_eigenvalue,
            "max_source_invariance_error": max_source_invariance_error,
            "max_pure_bond_invariance_error": max_pure_bond_invariance_error,
            "max_coordinate_commutator": max_coordinate_commutator,
            "minimum_interspersed_commutator_witness": min(interspersed_witnesses),
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
    print(f"PRIMARY LOCAL-Q2 REPLICA FOLDING PASS {payload['assertion_count']}/{payload['assertion_count']} rows={payload['derived']['site_row_count']} maxerr={payload['derived']['max_replica_error']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
