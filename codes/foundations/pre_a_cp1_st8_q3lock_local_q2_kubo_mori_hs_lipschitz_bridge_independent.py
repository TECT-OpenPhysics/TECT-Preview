#!/usr/bin/env python3
"""Independent finite Hilbert-Schmidt functional-calculus audit for EXP-001218 / R-376."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_hs_lipschitz_bridge"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-hs-lipschitz-bridge-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-primary-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_matsubara_lipschitz_budget/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-independent-{SLUG}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_independent as reference  # noqa: E402


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


def commutator_liouvillian(operator: np.ndarray) -> np.ndarray:
    unit = np.eye(operator.shape[0], dtype=complex)
    return np.kron(unit, operator) - np.kron(operator.T, unit)


def spectral_map(operator: np.ndarray, beta: float, modes: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    hermitian = reference.hermitian(operator)
    spectrum, basis = np.linalg.eigh(hermitian)
    positive = np.abs(spectrum)
    if modes is None:
        values = 2.0 * np.tanh(beta * positive / 2.0) / beta
    else:
        values = np.zeros_like(positive)
        for mode in range(modes):
            frequency = math.pi * (2.0 * float(mode) + 1.0)
            values += 8.0 * positive / (frequency * frequency + np.square(beta * positive))
    return (basis * values) @ basis.conj().T, values


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    regime = fixture["small_operator_regime"]
    beta_values = [Fraction(item) for item in fixture["beta_values"]]
    perturbation_values = [float(Fraction(item)) for item in fixture["perturbation_fractions"]]
    modes = int(fixture["series_terms"])
    tolerance = float(fixture["finite_tolerance"])
    slack = tolerance * float(fixture["tolerance_multiplier"])
    parameters = {"chi": "1", "r": "-1", "g": "3/5", "c": "3/5", "lambda": "1/10"}
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 128:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001218" and manifest["result_id"] == "R-376", [manifest["exploration_id"], manifest["result_id"]], "EXP-001218/R-376", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["hs_operator_lipschitz_theorem_proved"] is False, manifest["scope"], "finite-Hilbert-Schmidt-interface-only", "scope")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("source run", source.get("verdict") == "PASS" and source.get("derived", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("context_count")], "R-375 PASS and expected contexts", "source linkage")

    _q_single, p_single = reference.graph.oscillator(int(regime["cutoff"]))
    _coordinates, hamiltonian, terms = reference.build_system(int(regime["volume"]), int(regime["cutoff"]), parameters)
    del _coordinates, _q_single
    single_identity = np.eye(int(regime["cutoff"]), dtype=complex)
    global_identity = np.eye(hamiltonian.shape[0], dtype=complex)
    bond_index = int(regime["bond_term_index"])
    site = int(regime["perturbation_site"])
    momentum = reference.embed(p_single, site, int(regime["volume"]), single_identity)
    bond_generator = np.kron(terms[bond_index], global_identity) + np.kron(global_identity, terms[bond_index])
    momentum_generator = np.kron(momentum, global_identity) + np.kron(global_identity, momentum)
    base_liouvillian = commutator_liouvillian(bond_generator)
    commutator_norm = float(np.linalg.norm(bond_generator @ momentum_generator - momentum_generator @ bond_generator, ord="fro"))
    check("noncommuting perturbation", commutator_norm > slack, commutator_norm, f">{slack}", "eigenvector rotation")

    full_ratios: list[float] = []
    partial_ratios: list[float] = []
    cases: list[dict[str, Any]] = []
    maximum_full_violation = -float("inf")
    maximum_partial_violation = -float("inf")
    maximum_hermitian_error = 0.0
    maximum_positivity_violation = -float("inf")
    maximum_difference = 0.0
    minimum_difference = float("inf")
    for beta_fraction in beta_values:
        beta = float(beta_fraction)
        check(f"beta={beta_fraction} positive", beta > 0.0, beta, ">0", "capped kernel")
        full_reference, full_values = spectral_map(base_liouvillian, beta)
        partial_reference, partial_values = spectral_map(base_liouvillian, beta, modes)
        for fraction in perturbation_values:
            perturbed = commutator_liouvillian(bond_generator + fraction * momentum_generator)
            difference = perturbed - base_liouvillian
            denominator = float(np.linalg.norm(difference, ord="fro"))
            check(f"beta={beta_fraction} fraction={fraction} denominator", denominator > slack, denominator, f">{slack}", "Hilbert-Schmidt comparison")
            full_candidate, full_candidate_values = spectral_map(perturbed, beta)
            partial_candidate, partial_candidate_values = spectral_map(perturbed, beta, modes)
            full_ratio = float(np.linalg.norm(full_candidate - full_reference, ord="fro") / denominator)
            budget = sum(8.0 / (math.pi * (2.0 * float(mode) + 1.0)) ** 2 for mode in range(modes))
            partial_ratio = float(np.linalg.norm(partial_candidate - partial_reference, ord="fro") / denominator)
            full_violation = full_ratio - 1.0
            partial_violation = partial_ratio - budget
            full_ratios.append(full_ratio)
            partial_ratios.append(partial_ratio)
            maximum_full_violation = max(maximum_full_violation, full_violation)
            maximum_partial_violation = max(maximum_partial_violation, partial_violation)
            maximum_difference = max(maximum_difference, denominator)
            minimum_difference = min(minimum_difference, denominator)
            hermitian_error = max(float(np.linalg.norm(full_candidate - full_candidate.conj().T, ord="fro")), float(np.linalg.norm(partial_candidate - partial_candidate.conj().T, ord="fro")))
            minimum_value = min(float(np.min(full_values)), float(np.min(full_candidate_values)), float(np.min(partial_values)), float(np.min(partial_candidate_values)))
            maximum_hermitian_error = max(maximum_hermitian_error, hermitian_error)
            maximum_positivity_violation = max(maximum_positivity_violation, -minimum_value)
            check(f"beta={beta_fraction} fraction={fraction} full ratio", full_violation <= slack, full_violation, f"<={slack}", "Hilbert-Schmidt comparison")
            check(f"beta={beta_fraction} fraction={fraction} partial ratio", partial_violation <= slack, partial_violation, f"<={slack}", "Matsubara budget")
            check(f"beta={beta_fraction} fraction={fraction} Hermiticity", hermitian_error <= slack, hermitian_error, f"<={slack}", "functional calculus")
            check(f"beta={beta_fraction} fraction={fraction} positivity", minimum_value >= -slack, minimum_value, f">={-slack}", "functional calculus")
            cases.append({"beta": str(beta_fraction), "perturbation_fraction": fraction, "liouvillian_difference_frobenius": denominator, "full_ratio": full_ratio, "partial_ratio": partial_ratio, "partial_budget": budget, "full_violation": full_violation, "partial_violation": partial_violation})

    check("full envelope", maximum_full_violation <= slack, maximum_full_violation, f"<={slack}", "Hilbert-Schmidt comparison")
    check("partial envelope", maximum_partial_violation <= slack, maximum_partial_violation, f"<={slack}", "Matsubara budget")
    check("Hermiticity", maximum_hermitian_error <= slack, maximum_hermitian_error, f"<={slack}", "functional calculus")
    check("positivity", maximum_positivity_violation <= slack, maximum_positivity_violation, f"<={slack}", "functional calculus")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-HS-LIPSCHITZ-BRIDGE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"source_context_count": int(source["derived"]["context_count"]), "expected_source_contexts": int(fixture["expected_source_contexts"]), "beta_values": [str(value) for value in beta_values], "perturbation_fractions": perturbation_values, "series_terms": modes, "commutator_frobenius_norm": commutator_norm, "maximum_full_hilbert_schmidt_ratio": max(full_ratios), "maximum_partial_hilbert_schmidt_ratio": max(partial_ratios), "maximum_full_hilbert_schmidt_violation": maximum_full_violation, "maximum_partial_budget": max(c["partial_budget"] for c in cases), "maximum_partial_hilbert_schmidt_violation": maximum_partial_violation, "maximum_hermitian_error": maximum_hermitian_error, "maximum_positivity_violation": maximum_positivity_violation, "maximum_liouvillian_difference_frobenius": maximum_difference, "minimum_liouvillian_difference_frobenius": minimum_difference, "cases": cases, "hs_functional_calculus_finite_checked": True, "partial_hs_lipschitz_budget_finite_checked": True, "eigenvector_rotation_stress_finite_checked": True, "source_context_link_finite_checked": True, "hs_operator_lipschitz_theorem_proved": False, "operator_norm_locality_proved": False, "spatial_resolvent_locality_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT HS-LIPSCHITZ-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} cases={len(payload['derived']['cases'])} full={payload['derived']['maximum_full_hilbert_schmidt_ratio']:.9f} partial={payload['derived']['maximum_partial_hilbert_schmidt_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
