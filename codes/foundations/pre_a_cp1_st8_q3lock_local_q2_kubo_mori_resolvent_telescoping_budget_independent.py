#!/usr/bin/env python3
"""Independent finite resolvent telescoping audit for EXP-001219 / R-377."""

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


def commutator_map(operator: np.ndarray) -> np.ndarray:
    unit = np.eye(operator.shape[0], dtype=complex)
    return np.kron(unit, operator) - np.kron(operator.T, unit)


def absolute_matrix(operator: np.ndarray) -> np.ndarray:
    values, basis = np.linalg.eigh(reference.hermitian(operator))
    return (basis * np.abs(values)) @ basis.conj().T


def solve_resolvent(operator: np.ndarray, beta: float, mode: int) -> tuple[np.ndarray, float, float]:
    frequency = math.pi * (2.0 * float(mode) + 1.0)
    identity = np.eye(operator.shape[0], dtype=complex)
    denominator = frequency * frequency * identity + (beta * operator) @ (beta * operator)
    value = np.linalg.solve(denominator, identity)
    floor = float(np.min(np.linalg.eigvalsh(reference.hermitian(denominator))))
    return value, frequency, floor


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
    assertions: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(assertions) < 160:
            assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("authority", manifest["exploration_id"] == "EXP-001219" and manifest["result_id"] == "R-377", [manifest["exploration_id"], manifest["result_id"]], "EXP-001219/R-377", "provenance")
    check("scope", manifest["claim_bearing"] is False and manifest["scope"]["square_root_debt_isolated"] is True and not manifest["scope"]["resolvent_locality_proved"], manifest["scope"], "finite-resolvent-interface-only", "scope")
    check("series length", modes >= 1, modes, ">=1", "fixture")
    source = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    check("source linkage", source.get("verdict") == "PASS" and source.get("derived", {}).get("source_context_count") == int(fixture["expected_source_contexts"]), [source.get("verdict"), source.get("derived", {}).get("source_context_count")], "R-376 PASS and expected contexts", "source linkage")

    _q_single, hamiltonian, terms = reference.build_system(int(regime["volume"]), int(regime["cutoff"]), parameters)
    del _q_single
    _q, momentum_single = reference.graph.oscillator(int(regime["cutoff"]))
    del _q
    single_identity = np.eye(int(regime["cutoff"]), dtype=complex)
    global_identity = np.eye(hamiltonian.shape[0], dtype=complex)
    bond = int(regime["bond_term_index"])
    site = int(regime["perturbation_site"])
    momentum = reference.embed(momentum_single, site, int(regime["volume"]), single_identity)
    base_generator = terms[bond]
    perturb_generator = momentum
    base = commutator_map(base_generator)
    commutator_norm = float(np.linalg.norm(base_generator @ perturb_generator - perturb_generator @ base_generator, ord="fro"))
    check("noncommuting perturbation", commutator_norm > slack, commutator_norm, f">{slack}", "fixture")
    check("base Hermitian", float(np.linalg.norm(base - base.conj().T, ord="fro")) <= slack, float(np.linalg.norm(base - base.conj().T, ord="fro")), f"<={slack}", "fixture")

    maximum_identity_residual = 0.0
    maximum_single_bound_violation = -float("inf")
    maximum_operator_bound_violation = -float("inf")
    maximum_summed_identity_residual = 0.0
    maximum_summed_budget_violation = -float("inf")
    maximum_summed_budget_ratio = 0.0
    maximum_kernel_decomposition_residual = 0.0
    minimum_denominator_eigenvalue = float("inf")
    maximum_resolvent_operator_norm = 0.0
    maximum_squared_difference = 0.0
    maximum_square_root_debt = 0.0
    maximum_resolvent_kernel_term = 0.0
    maximum_kernel_difference = 0.0
    rows: list[dict[str, Any]] = []

    for beta_fraction in beta_values:
        beta = float(beta_fraction)
        check(f"beta={beta_fraction} positive", beta > 0.0, beta, ">0", "resolvent positivity")
        abs_base = absolute_matrix(base)
        for fraction in perturbation_values:
            candidate_generator = base_generator + fraction * perturb_generator
            candidate = commutator_map(candidate_generator)
            diff_square = base @ base - candidate @ candidate
            square_norm = float(np.linalg.norm(diff_square, ord="fro"))
            difference = candidate - base
            difference_norm = float(np.linalg.norm(difference, ord="fro"))
            check(f"beta={beta_fraction} fraction={fraction} denominator", difference_norm > slack, difference_norm, f">{slack}", "comparison")
            abs_candidate = absolute_matrix(candidate)
            total_difference = np.zeros_like(base)
            total_bound = 0.0
            total_identity_residual = 0.0
            total_kernel = np.zeros_like(base)
            total_root = np.zeros_like(base)
            total_resolvent = np.zeros_like(base)
            mode_max_identity = 0.0
            mode_max_frobenius_violation = -float("inf")
            mode_max_operator_violation = -float("inf")
            mode_min_floor = float("inf")
            mode_max_operator_norm = 0.0
            mode_max_difference = 0.0
            mode_max_bound = 0.0
            for mode in range(modes):
                reference_resolvent, frequency, floor_a = solve_resolvent(base, beta, mode)
                candidate_resolvent, _frequency, floor_b = solve_resolvent(candidate, beta, mode)
                resolvent_delta = candidate_resolvent - reference_resolvent
                rhs = candidate_resolvent @ (beta * beta * diff_square) @ reference_resolvent
                identity_error = float(np.linalg.norm(resolvent_delta - rhs, ord="fro"))
                squared_bound = beta * beta * square_norm / (frequency ** 4)
                delta_norm = float(np.linalg.norm(resolvent_delta, ord="fro"))
                frobenius_violation = delta_norm - squared_bound
                operator_ceiling = 1.0 / (frequency * frequency)
                operator_norm = max(1.0 / floor_a, 1.0 / floor_b)
                operator_violation = operator_norm - operator_ceiling
                total_difference += resolvent_delta
                total_bound += squared_bound
                total_identity_residual += identity_error
                floor = min(floor_a, floor_b)
                minimum_denominator_eigenvalue = min(minimum_denominator_eigenvalue, floor)
                maximum_resolvent_operator_norm = max(maximum_resolvent_operator_norm, operator_norm)
                maximum_identity_residual = max(maximum_identity_residual, identity_error)
                maximum_single_bound_violation = max(maximum_single_bound_violation, frobenius_violation)
                maximum_operator_bound_violation = max(maximum_operator_bound_violation, operator_violation)
                mode_max_identity = max(mode_max_identity, identity_error)
                mode_max_frobenius_violation = max(mode_max_frobenius_violation, frobenius_violation)
                mode_max_operator_violation = max(mode_max_operator_violation, operator_violation)
                mode_min_floor = min(mode_min_floor, floor)
                mode_max_operator_norm = max(mode_max_operator_norm, operator_norm)
                mode_max_difference = max(mode_max_difference, delta_norm)
                mode_max_bound = max(mode_max_bound, squared_bound)
                root_component = 8.0 * (abs_candidate - abs_base) @ candidate_resolvent
                resolvent_component = 8.0 * abs_base @ resolvent_delta
                kernel_difference = 8.0 * abs_candidate @ candidate_resolvent - 8.0 * abs_base @ reference_resolvent
                total_kernel += kernel_difference
                total_root += root_component
                total_resolvent += resolvent_component
                decomposition_error = float(np.linalg.norm(kernel_difference - root_component - resolvent_component, ord="fro"))
                maximum_kernel_decomposition_residual = max(maximum_kernel_decomposition_residual, decomposition_error)
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} identity", identity_error <= slack * (1.0 + float(np.linalg.norm(rhs, ord="fro"))), identity_error, "identity residual tolerance", "resolvent identity")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} denominator", floor >= frequency * frequency - slack, floor, f">={frequency * frequency - slack}", "resolvent positivity")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} operator bound", operator_violation <= slack * (1.0 + operator_ceiling), operator_violation, "operator norm <= 1/omega^2", "resolvent bound")
                check(f"beta={beta_fraction} fraction={fraction} mode={mode} Frobenius bound", frobenius_violation <= slack * (1.0 + squared_bound), frobenius_violation, "Frobenius resolvent budget", "resolvent bound")
            total_norm = float(np.linalg.norm(total_difference, ord="fro"))
            budget_violation = total_norm - total_bound
            budget_ratio = total_norm / total_bound if total_bound > slack else 0.0
            kernel_norm = float(np.linalg.norm(total_kernel, ord="fro"))
            root_norm = float(np.linalg.norm(total_root, ord="fro"))
            resolvent_norm = float(np.linalg.norm(total_resolvent, ord="fro"))
            decomposition_residual = float(np.linalg.norm(total_kernel - total_root - total_resolvent, ord="fro"))
            maximum_summed_identity_residual = max(maximum_summed_identity_residual, total_identity_residual)
            maximum_summed_budget_violation = max(maximum_summed_budget_violation, budget_violation)
            maximum_summed_budget_ratio = max(maximum_summed_budget_ratio, budget_ratio)
            maximum_kernel_difference = max(maximum_kernel_difference, kernel_norm)
            maximum_square_root_debt = max(maximum_square_root_debt, root_norm)
            maximum_resolvent_kernel_term = max(maximum_resolvent_kernel_term, resolvent_norm)
            maximum_kernel_decomposition_residual = max(maximum_kernel_decomposition_residual, decomposition_residual)
            maximum_squared_difference = max(maximum_squared_difference, square_norm)
            check(f"beta={beta_fraction} fraction={fraction} summed identity", total_identity_residual <= slack * (1.0 + float(np.linalg.norm(total_difference, ord="fro"))), total_identity_residual, "summed identity tolerance", "resolvent identity")
            check(f"beta={beta_fraction} fraction={fraction} summed budget", budget_violation <= slack * (1.0 + total_bound), budget_violation, "summed resolvent budget", "resolvent bound")
            check(f"beta={beta_fraction} fraction={fraction} decomposition", decomposition_residual <= slack * (1.0 + kernel_norm), decomposition_residual, "root plus resolvent decomposition", "kernel decomposition")
            rows.append({"beta": str(beta_fraction), "perturbation_fraction": fraction, "liouvillian_difference_frobenius": difference_norm, "squared_liouvillian_difference_frobenius": square_norm, "maximum_mode_identity_residual": mode_max_identity, "maximum_mode_frobenius_bound_violation": mode_max_frobenius_violation, "maximum_mode_operator_bound_violation": mode_max_operator_violation, "minimum_resolvent_denominator_eigenvalue": mode_min_floor, "maximum_resolvent_operator_norm": mode_max_operator_norm, "maximum_mode_resolvent_difference_frobenius": mode_max_difference, "maximum_mode_bound": mode_max_bound, "summed_resolvent_difference_frobenius": total_norm, "summed_resolvent_budget": total_bound, "summed_budget_ratio": budget_ratio, "summed_budget_violation": budget_violation, "summed_kernel_difference_frobenius": kernel_norm, "summed_square_root_debt_frobenius": root_norm, "summed_resolvent_kernel_term_frobenius": resolvent_norm, "summed_kernel_decomposition_residual": decomposition_residual})

    check("identity envelope", maximum_identity_residual <= slack * 100.0, maximum_identity_residual, f"<={slack * 100.0}", "resolvent identity")
    check("single bound envelope", maximum_single_bound_violation <= slack * 100.0, maximum_single_bound_violation, f"<={slack * 100.0}", "resolvent bound")
    check("operator envelope", maximum_operator_bound_violation <= slack * 100.0, maximum_operator_bound_violation, f"<={slack * 100.0}", "resolvent bound")
    check("summed identity envelope", maximum_summed_identity_residual <= slack * 200.0, maximum_summed_identity_residual, f"<={slack * 200.0}", "resolvent identity")
    check("summed budget envelope", maximum_summed_budget_violation <= slack * 200.0, maximum_summed_budget_violation, f"<={slack * 200.0}", "resolvent bound")
    check("decomposition envelope", maximum_kernel_decomposition_residual <= slack * 200.0, maximum_kernel_decomposition_residual, f"<={slack * 200.0}", "kernel decomposition")
    check("denominator floor", minimum_denominator_eigenvalue >= math.pi * math.pi - slack, minimum_denominator_eigenvalue, f">={math.pi * math.pi - slack}", "resolvent positivity")
    check("square-root debt recorded", maximum_square_root_debt >= 0.0, maximum_square_root_debt, ">=0", "boundary")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-Q2-KUBO-MORI-RESOLVENT-TELESCOPING-BUDGET", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": assertion_count, "assertions": assertions,
        "derived": {"series_terms": modes, "beta_values": [str(value) for value in beta_values], "perturbation_fractions": perturbation_values, "commutator_frobenius_norm": commutator_norm, "maximum_identity_residual": maximum_identity_residual, "maximum_single_frobenius_bound_violation": maximum_single_bound_violation, "maximum_operator_bound_violation": maximum_operator_bound_violation, "maximum_summed_identity_residual": maximum_summed_identity_residual, "maximum_summed_budget_violation": maximum_summed_budget_violation, "maximum_summed_budget_ratio": maximum_summed_budget_ratio, "maximum_kernel_decomposition_residual": maximum_kernel_decomposition_residual, "minimum_resolvent_denominator_eigenvalue": minimum_denominator_eigenvalue, "maximum_resolvent_operator_norm": maximum_resolvent_operator_norm, "maximum_squared_liouvillian_difference_frobenius": maximum_squared_difference, "maximum_kernel_difference_frobenius": maximum_kernel_difference, "maximum_square_root_debt_frobenius": maximum_square_root_debt, "maximum_resolvent_kernel_term_frobenius": maximum_resolvent_kernel_term, "cases": rows, "resolvent_identity_finite_checked": True, "resolvent_operator_bound_finite_checked": True, "summable_resolvent_budget_finite_checked": True, "kernel_decomposition_finite_checked": True, "square_root_debt_isolated": True, "resolvent_locality_proved": False, "operator_norm_locality_proved": False, "weighted_cutoff_uniformity_proved": False, "weighted_volume_uniformity_proved": False, "source_uniformity_proved": False, "shape_uniformity_proved": False, "common_core_closed": False, "common_alpha_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False},
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
    print(f"INDEPENDENT RESOLVENT-TELESCOPING-BUDGET PASS {payload['assertion_count']}/{payload['assertion_count']} cases={len(payload['derived']['cases'])} ratio={payload['derived']['maximum_summed_budget_ratio']:.9f} root_debt={payload['derived']['maximum_square_root_debt_frobenius']:.6e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
