#!/usr/bin/env python3
"""Primary finite Hilbert-Schmidt functional-calculus audit for EXP-001218 / R-376."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-28-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering as prior  # noqa: E402


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


def liouvillian(operator: np.ndarray) -> np.ndarray:
    identity = np.eye(operator.shape[0], dtype=complex)
    return np.kron(identity, operator) - np.kron(operator.T, identity)


def functional_calculus(operator: np.ndarray, beta: float, terms: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    hermitian = prior.hermitian(operator)
    values, vectors = np.linalg.eigh(hermitian)
    energies = np.abs(values)
    if terms is None:
        scalar = (2.0 / beta) * np.tanh(beta * energies / 2.0)
    else:
        scalar = np.zeros_like(energies)
        for index in range(terms):
            omega = (2.0 * float(index) + 1.0) * math.pi
            scalar += 8.0 * energies / (omega * omega + (beta * energies) ** 2)
    return (vectors * scalar) @ vectors.conj().T, scalar


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    regime = fixture["small_operator_regime"]
    betas = [Fraction(value) for value in fixture["beta_values"]]
    perturbations = [float(Fraction(value)) for value in fixture["perturbation_fractions"]]
    terms_count = int(fixture["series_terms"])
    tolerance = float(fixture["finite_tolerance"])
    threshold = tolerance * float(fixture["tolerance_multiplier"])
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
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["hs_operator_lipschitz_theorem_proved"], manifest["scope"], "finite-Hilbert-Schmidt-interface-only", "scope")
    check("series length", terms_count >= 1, terms_count, ">=1", "fixture")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("source run", source.get("verdict") == "PASS" and source.get("derived", {}).get("context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("context_count")], "R-375 PASS and expected contexts", "source linkage")

    coordinates, hamiltonian, terms = prior.base.split_system(int(regime["volume"]), int(regime["cutoff"]), parameters)
    del coordinates
    identity_single = np.eye(int(regime["cutoff"]), dtype=complex)
    identity = np.eye(hamiltonian.shape[0], dtype=complex)
    selected = int(regime["bond_term_index"])
    perturbation_site = int(regime["perturbation_site"])
    _q_single, p_single = prior.q3.oscillator(int(regime["cutoff"]))
    perturbation = prior.base.embed(p_single, perturbation_site, int(regime["volume"]), identity_single)
    generator = np.kron(terms[selected], identity) + np.kron(identity, terms[selected])
    perturbation_generator = np.kron(perturbation, identity) + np.kron(identity, perturbation)
    base_liouvillian = liouvillian(generator)
    commutator_norm = float(np.linalg.norm(generator @ perturbation_generator - perturbation_generator @ generator, ord="fro"))
    check("noncommuting perturbation", commutator_norm > threshold, commutator_norm, f">{threshold}", "eigenvector rotation")

    max_full_ratio = 0.0
    max_partial_ratio = 0.0
    max_full_violation = -float("inf")
    max_partial_violation = -float("inf")
    max_hermitian_error = 0.0
    max_min_eigenvalue_violation = -float("inf")
    max_liouvillian_difference = 0.0
    minimum_difference = float("inf")
    cases: list[dict[str, Any]] = []
    for beta_fraction in betas:
        beta = float(beta_fraction)
        check(f"beta={beta_fraction} positive", beta > 0.0, beta, ">0", "capped kernel")
        capped_base, capped_values = functional_calculus(base_liouvillian, beta)
        partial_base, partial_values = functional_calculus(base_liouvillian, beta, terms_count)
        for fraction in perturbations:
            perturbed_generator = generator + fraction * perturbation_generator
            perturbed_liouvillian = liouvillian(perturbed_generator)
            difference = perturbed_liouvillian - base_liouvillian
            denominator = float(np.linalg.norm(difference, ord="fro"))
            check(f"beta={beta_fraction} fraction={fraction} nonzero denominator", denominator > threshold, denominator, f">{threshold}", "Hilbert-Schmidt comparison")
            capped_perturbed, capped_perturbed_values = functional_calculus(perturbed_liouvillian, beta)
            partial_perturbed, partial_perturbed_values = functional_calculus(perturbed_liouvillian, beta, terms_count)
            full_ratio = float(np.linalg.norm(capped_perturbed - capped_base, ord="fro") / denominator)
            budget = sum(8.0 / (((2.0 * float(index) + 1.0) * math.pi) ** 2) for index in range(terms_count))
            partial_ratio = float(np.linalg.norm(partial_perturbed - partial_base, ord="fro") / denominator)
            full_violation = full_ratio - 1.0
            partial_violation = partial_ratio - budget
            max_full_ratio = max(max_full_ratio, full_ratio)
            max_partial_ratio = max(max_partial_ratio, partial_ratio)
            max_full_violation = max(max_full_violation, full_violation)
            max_partial_violation = max(max_partial_violation, partial_violation)
            max_liouvillian_difference = max(max_liouvillian_difference, denominator)
            minimum_difference = min(minimum_difference, denominator)
            hermitian_error = max(float(np.linalg.norm(capped_base - capped_base.conj().T, ord="fro")), float(np.linalg.norm(capped_perturbed - capped_perturbed.conj().T, ord="fro")), float(np.linalg.norm(partial_base - partial_base.conj().T, ord="fro")), float(np.linalg.norm(partial_perturbed - partial_perturbed.conj().T, ord="fro")))
            min_eigenvalue = min(float(np.min(capped_values)), float(np.min(capped_perturbed_values)), float(np.min(partial_values)), float(np.min(partial_perturbed_values)))
            max_hermitian_error = max(max_hermitian_error, hermitian_error)
            max_min_eigenvalue_violation = max(max_min_eigenvalue_violation, -min_eigenvalue)
            check(f"beta={beta_fraction} fraction={fraction} full HS budget", full_violation <= threshold, full_violation, f"<= {threshold}", "Hilbert-Schmidt comparison")
            check(f"beta={beta_fraction} fraction={fraction} partial HS budget", partial_violation <= threshold, partial_violation, f"<= {threshold}", "Matsubara budget")
            check(f"beta={beta_fraction} fraction={fraction} Hermiticity", hermitian_error <= threshold, hermitian_error, f"<= {threshold}", "functional calculus")
            check(f"beta={beta_fraction} fraction={fraction} positivity", min_eigenvalue >= -threshold, min_eigenvalue, f">= {-threshold}", "functional calculus")
            cases.append({"beta": str(beta_fraction), "perturbation_fraction": fraction, "liouvillian_difference_frobenius": denominator, "full_ratio": full_ratio, "partial_ratio": partial_ratio, "partial_budget": budget, "full_violation": full_violation, "partial_violation": partial_violation})

    check("source context count", int(source["derived"]["context_count"]) == int(fixture["expected_source_contexts"]), source["derived"]["context_count"], fixture["expected_source_contexts"], "source linkage")
    check("full HS envelope", max_full_violation <= threshold, max_full_violation, f"<= {threshold}", "Hilbert-Schmidt comparison")
    check("partial HS envelope", max_partial_violation <= threshold, max_partial_violation, f"<= {threshold}", "Matsubara budget")
    check("Hermiticity", max_hermitian_error <= threshold, max_hermitian_error, f"<= {threshold}", "functional calculus")
    check("positivity", max_min_eigenvalue_violation <= threshold, max_min_eigenvalue_violation, f"<= {threshold}", "functional calculus")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-HS-LIPSCHITZ-BRIDGE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"source_context_count": int(source["derived"]["context_count"]), "expected_source_contexts": int(fixture["expected_source_contexts"]), "beta_values": [str(value) for value in betas], "perturbation_fractions": perturbations, "series_terms": terms_count, "commutator_frobenius_norm": commutator_norm, "maximum_full_hilbert_schmidt_ratio": max_full_ratio, "maximum_partial_hilbert_schmidt_ratio": max_partial_ratio, "maximum_full_hilbert_schmidt_violation": max_full_violation, "maximum_partial_budget": max(c["partial_budget"] for c in cases), "maximum_partial_hilbert_schmidt_violation": max_partial_violation, "maximum_hermitian_error": max_hermitian_error, "maximum_positivity_violation": max_min_eigenvalue_violation, "maximum_liouvillian_difference_frobenius": max_liouvillian_difference, "minimum_liouvillian_difference_frobenius": minimum_difference, "cases": cases, "hs_functional_calculus_finite_checked": True, "partial_hs_lipschitz_budget_finite_checked": True, "eigenvector_rotation_stress_finite_checked": True, "source_context_link_finite_checked": True, "hs_operator_lipschitz_theorem_proved": False, "operator_norm_locality_proved": False, "spatial_resolvent_locality_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY HS-LIPSCHITZ-BRIDGE PASS {payload['assertion_count']}/{payload['assertion_count']} cases={len(payload['derived']['cases'])} full={payload['derived']['maximum_full_hilbert_schmidt_ratio']:.9f} partial={payload['derived']['maximum_partial_hilbert_schmidt_ratio']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
