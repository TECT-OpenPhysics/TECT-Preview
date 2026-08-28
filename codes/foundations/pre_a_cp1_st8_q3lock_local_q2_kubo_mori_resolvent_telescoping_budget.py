#!/usr/bin/env python3
"""Primary finite resolvent telescoping audit for EXP-001219 / R-377."""

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
SLUG = "pre_a_cp1_st8_q3lock_local_q2_kubo_mori_resolvent_telescoping_budget"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-q2-kubo-mori-resolvent-telescoping-budget-manifest.json"
SOURCE_RUN = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-28-primary-pre_a_cp1_st8_q3lock_local_q2_kubo_mori_hs_lipschitz_bridge/primary.json"
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


def matrix_abs(operator: np.ndarray) -> np.ndarray:
    hermitian = prior.hermitian(operator)
    values, vectors = np.linalg.eigh(hermitian)
    return (vectors * np.abs(values)) @ vectors.conj().T


def resolvent(operator: np.ndarray, beta: float, mode: int) -> tuple[np.ndarray, float, float]:
    dimension = operator.shape[0]
    omega = (2.0 * float(mode) + 1.0) * math.pi
    denominator = omega * omega * np.eye(dimension, dtype=complex) + (beta * operator) @ (beta * operator)
    candidate = np.linalg.inv(denominator)
    minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(prior.hermitian(denominator))))
    return candidate, omega, minimum_eigenvalue


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
        if len(checks) < 160:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001219" and manifest["result_id"] == "R-377", [manifest["exploration_id"], manifest["result_id"]], "EXP-001219/R-377", "provenance")
    check("scope", manifest["claim_bearing"] is False and not manifest["scope"]["resolvent_locality_proved"], manifest["scope"], "finite-resolvent-interface-only", "scope")
    check("series length", terms_count >= 1, terms_count, ">=1", "fixture")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("source run", source.get("verdict") == "PASS" and source.get("derived", {}).get("source_context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("source_context_count")], "R-376 PASS and expected contexts", "source linkage")

    _, hamiltonian, terms = prior.base.split_system(int(regime["volume"]), int(regime["cutoff"]), parameters)
    identity_single = np.eye(int(regime["cutoff"]), dtype=complex)
    identity_global = np.eye(hamiltonian.shape[0], dtype=complex)
    selected = int(regime["bond_term_index"])
    perturbation_site = int(regime["perturbation_site"])
    _q_single, p_single = prior.q3.oscillator(int(regime["cutoff"]))
    perturbation = prior.base.embed(p_single, perturbation_site, int(regime["volume"]), identity_single)
    generator = terms[selected]
    perturbation_generator = perturbation
    base_liouvillian = liouvillian(generator)
    commutator_norm = float(np.linalg.norm(generator @ perturbation_generator - perturbation_generator @ generator, ord="fro"))
    check("noncommuting perturbation", commutator_norm > threshold, commutator_norm, f">{threshold}", "fixture")
    check("base Hermitian", float(np.linalg.norm(base_liouvillian - base_liouvillian.conj().T, ord="fro")) <= threshold, float(np.linalg.norm(base_liouvillian - base_liouvillian.conj().T, ord="fro")), f"<={threshold}", "fixture")

    max_identity_residual = 0.0
    max_single_bound_violation = -float("inf")
    max_operator_bound_violation = -float("inf")
    max_sum_identity_residual = 0.0
    max_sum_bound_violation = -float("inf")
    max_sum_budget_ratio = 0.0
    max_kernel_decomposition_residual = 0.0
    max_kernel_difference = 0.0
    max_square_root_debt = 0.0
    max_resolvent_kernel_term = 0.0
    max_square_difference = 0.0
    min_denominator_eigenvalue = float("inf")
    max_resolvent_operator_norm = 0.0
    cases: list[dict[str, Any]] = []

    for beta_fraction in betas:
        beta = float(beta_fraction)
        check(f"beta={beta_fraction} positive", beta > 0.0, beta, ">0", "resolvent positivity")
        abs_base = matrix_abs(base_liouvillian)
        for fraction in perturbations:
            perturbed_liouvillian = liouvillian(generator + fraction * perturbation_generator)
            difference = perturbed_liouvillian - base_liouvillian
            denominator = float(np.linalg.norm(difference, ord="fro"))
            square_difference = base_liouvillian @ base_liouvillian - perturbed_liouvillian @ perturbed_liouvillian
            square_norm = float(np.linalg.norm(square_difference, ord="fro"))
            check(f"beta={beta_fraction} fraction={fraction} nonzero denominator", denominator > threshold, denominator, f">{threshold}", "comparison")
            abs_perturbed = matrix_abs(perturbed_liouvillian)
            summed_difference = np.zeros_like(base_liouvillian)
            summed_bound = 0.0
            summed_identity_residual = 0.0
            summed_kernel_difference = np.zeros_like(base_liouvillian)
            summed_root_term = np.zeros_like(base_liouvillian)
            summed_resolvent_term = np.zeros_like(base_liouvillian)
            maximum_mode_identity_residual = 0.0
            maximum_mode_bound_violation = -float("inf")
            maximum_mode_operator_bound_violation = -float("inf")
            maximum_mode_denominator = float("inf")
            maximum_mode_resolvent_norm = 0.0
            maximum_mode_difference_norm = 0.0
            maximum_mode_bound = 0.0
            for mode in range(terms_count):
                reference, omega, minimum_eigenvalue_a = resolvent(base_liouvillian, beta, mode)
                candidate, _, minimum_eigenvalue_b = resolvent(perturbed_liouvillian, beta, mode)
                delta = candidate - reference
                rhs = candidate @ (beta * beta * square_difference) @ reference
                identity_residual = float(np.linalg.norm(delta - rhs, ord="fro"))
                bound = beta * beta * square_norm / (omega ** 4)
                delta_norm = float(np.linalg.norm(delta, ord="fro"))
                single_bound_violation = delta_norm - bound
                operator_bound = 1.0 / (omega * omega)
                operator_norm = max(1.0 / minimum_eigenvalue_a, 1.0 / minimum_eigenvalue_b)
                operator_bound_violation = operator_norm - operator_bound
                summed_difference += delta
                summed_bound += bound
                summed_identity_residual += identity_residual
                min_denominator_eigenvalue = min(min_denominator_eigenvalue, minimum_eigenvalue_a, minimum_eigenvalue_b)
                max_resolvent_operator_norm = max(max_resolvent_operator_norm, operator_norm)
                max_identity_residual = max(max_identity_residual, identity_residual)
                max_single_bound_violation = max(max_single_bound_violation, single_bound_violation)
                max_operator_bound_violation = max(max_operator_bound_violation, operator_bound_violation)
                maximum_mode_identity_residual = max(maximum_mode_identity_residual, identity_residual)
                maximum_mode_bound_violation = max(maximum_mode_bound_violation, single_bound_violation)
                maximum_mode_operator_bound_violation = max(maximum_mode_operator_bound_violation, operator_bound_violation)
                maximum_mode_denominator = min(maximum_mode_denominator, minimum_eigenvalue_a, minimum_eigenvalue_b)
                maximum_mode_resolvent_norm = max(maximum_mode_resolvent_norm, operator_norm)
                maximum_mode_difference_norm = max(maximum_mode_difference_norm, delta_norm)
                maximum_mode_bound = max(maximum_mode_bound, bound)
                root_term = 8.0 * (abs_perturbed - abs_base) @ candidate
                resolvent_term = 8.0 * abs_base @ delta
                kernel_delta = 8.0 * abs_perturbed @ candidate - 8.0 * abs_base @ reference
                summed_kernel_difference += kernel_delta
                summed_root_term += root_term
                summed_resolvent_term += resolvent_term
                maximum_mode_kernel_residual = float(np.linalg.norm(kernel_delta - root_term - resolvent_term, ord="fro"))
                max_kernel_decomposition_residual = max(max_kernel_decomposition_residual, maximum_mode_kernel_residual)
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} identity", identity_residual <= threshold * (1.0 + float(np.linalg.norm(rhs, ord="fro"))), identity_residual, "identity residual tolerance", "resolvent identity")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} denominator", min(minimum_eigenvalue_a, minimum_eigenvalue_b) >= omega * omega - threshold, min(minimum_eigenvalue_a, minimum_eigenvalue_b), f">={omega * omega - threshold}", "resolvent positivity")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} operator bound", operator_bound_violation <= threshold * (1.0 + operator_bound), operator_bound_violation, "operator norm <= 1/omega^2", "resolvent bound")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} Frobenius bound", single_bound_violation <= threshold * (1.0 + bound), single_bound_violation, "Frobenius resolvent budget", "resolvent bound")
            summed_norm = float(np.linalg.norm(summed_difference, ord="fro"))
            sum_bound_violation = summed_norm - summed_bound
            sum_budget_ratio = summed_norm / summed_bound if summed_bound > threshold else 0.0
            summed_kernel_norm = float(np.linalg.norm(summed_kernel_difference, ord="fro"))
            root_debt = float(np.linalg.norm(summed_root_term, ord="fro"))
            resolvent_kernel_term = float(np.linalg.norm(summed_resolvent_term, ord="fro"))
            summed_kernel_residual = float(np.linalg.norm(summed_kernel_difference - summed_root_term - summed_resolvent_term, ord="fro"))
            max_sum_identity_residual = max(max_sum_identity_residual, summed_identity_residual)
            max_sum_bound_violation = max(max_sum_bound_violation, sum_bound_violation)
            max_sum_budget_ratio = max(max_sum_budget_ratio, sum_budget_ratio)
            max_sum_identity_residual = max(max_sum_identity_residual, summed_identity_residual)
            max_kernel_difference = max(max_kernel_difference, summed_kernel_norm)
            max_square_root_debt = max(max_square_root_debt, root_debt)
            max_resolvent_kernel_term = max(max_resolvent_kernel_term, resolvent_kernel_term)
            max_kernel_decomposition_residual = max(max_kernel_decomposition_residual, summed_kernel_residual)
            max_square_difference = max(max_square_difference, square_norm)
            check(f"beta={beta_fraction} fraction={fraction} summed identity", summed_identity_residual <= threshold * (1.0 + float(np.linalg.norm(summed_difference, ord="fro"))), summed_identity_residual, "summed identity tolerance", "resolvent identity")
            check(f"beta={beta_fraction} fraction={fraction} summed budget", sum_bound_violation <= threshold * (1.0 + summed_bound), sum_bound_violation, "summed resolvent budget", "resolvent bound")
            check(f"beta={beta_fraction} fraction={fraction} kernel decomposition", summed_kernel_residual <= threshold * (1.0 + summed_kernel_norm), summed_kernel_residual, "root plus resolvent decomposition", "kernel decomposition")
            cases.append({"beta": str(beta_fraction), "perturbation_fraction": fraction, "liouvillian_difference_frobenius": denominator, "squared_liouvillian_difference_frobenius": square_norm, "maximum_mode_identity_residual": maximum_mode_identity_residual, "maximum_mode_frobenius_bound_violation": maximum_mode_bound_violation, "maximum_mode_operator_bound_violation": maximum_mode_operator_bound_violation, "minimum_resolvent_denominator_eigenvalue": maximum_mode_denominator, "maximum_resolvent_operator_norm": maximum_mode_resolvent_norm, "maximum_mode_resolvent_difference_frobenius": maximum_mode_difference_norm, "maximum_mode_bound": maximum_mode_bound, "summed_resolvent_difference_frobenius": summed_norm, "summed_resolvent_budget": summed_bound, "summed_budget_ratio": sum_budget_ratio, "summed_budget_violation": sum_bound_violation, "summed_kernel_difference_frobenius": summed_kernel_norm, "summed_square_root_debt_frobenius": root_debt, "summed_resolvent_kernel_term_frobenius": resolvent_kernel_term, "summed_kernel_decomposition_residual": summed_kernel_residual})

    check("identity envelope", max_identity_residual <= threshold * 100.0, max_identity_residual, f"<={threshold * 100.0}", "resolvent identity")
    check("single Frobenius envelope", max_single_bound_violation <= threshold * 100.0, max_single_bound_violation, f"<={threshold * 100.0}", "resolvent bound")
    check("operator envelope", max_operator_bound_violation <= threshold * 100.0, max_operator_bound_violation, f"<={threshold * 100.0}", "resolvent bound")
    check("summed identity envelope", max_sum_identity_residual <= threshold * 200.0, max_sum_identity_residual, f"<={threshold * 200.0}", "resolvent identity")
    check("summed budget envelope", max_sum_bound_violation <= threshold * 200.0, max_sum_bound_violation, f"<={threshold * 200.0}", "resolvent bound")
    check("kernel decomposition envelope", max_kernel_decomposition_residual <= threshold * 200.0, max_kernel_decomposition_residual, f"<={threshold * 200.0}", "kernel decomposition")
    check("denominator positivity", min_denominator_eigenvalue >= math.pi * math.pi - threshold, min_denominator_eigenvalue, f">={math.pi * math.pi - threshold}", "resolvent positivity")
    check("square-root term recorded", max_square_root_debt >= 0.0, max_square_root_debt, ">=0", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-RESOLVENT-TELESCOPING-BUDGET", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": checks,
        "derived": {"series_terms": terms_count, "beta_values": [str(value) for value in betas], "perturbation_fractions": perturbations, "commutator_frobenius_norm": commutator_norm, "maximum_identity_residual": max_identity_residual, "maximum_single_frobenius_bound_violation": max_single_bound_violation, "maximum_operator_bound_violation": max_operator_bound_violation, "maximum_summed_identity_residual": max_sum_identity_residual, "maximum_summed_budget_violation": max_sum_bound_violation, "maximum_summed_budget_ratio": max_sum_budget_ratio, "maximum_kernel_decomposition_residual": max_kernel_decomposition_residual, "minimum_resolvent_denominator_eigenvalue": min_denominator_eigenvalue, "maximum_resolvent_operator_norm": max_resolvent_operator_norm, "maximum_squared_liouvillian_difference_frobenius": max_square_difference, "maximum_kernel_difference_frobenius": max_kernel_difference, "maximum_square_root_debt_frobenius": max_square_root_debt, "maximum_resolvent_kernel_term_frobenius": max_resolvent_kernel_term, "cases": cases, "resolvent_identity_finite_checked": True, "resolvent_operator_bound_finite_checked": True, "summable_resolvent_budget_finite_checked": True, "kernel_decomposition_finite_checked": True, "square_root_debt_isolated": True, "resolvent_locality_proved": False, "operator_norm_locality_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False},
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY RESOLVENT-TELESCOPING-BUDGET PASS {payload['assertion_count']}/{payload['assertion_count']} cases={len(payload['derived']['cases'])} ratio={payload['derived']['maximum_summed_budget_ratio']:.9f} root_debt={payload['derived']['maximum_square_root_debt_frobenius']:.6e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
