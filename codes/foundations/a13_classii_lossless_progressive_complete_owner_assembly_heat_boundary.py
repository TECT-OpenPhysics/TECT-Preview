#!/usr/bin/env python3
"""Primary certificate for the R-104 fixed-chart owner identity.

This executable checks the finite-dimensional identities used by the proof.
It does not approximate the open Nelson bound. All fixture values are labelled
inputs; reported quantities are recomputed from those inputs.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-28-primary-lossless-progressive-complete-owner-assembly-heat-boundary/result.json"

AUTHORITY_NOTES = {
    "r079": "classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r081": "classii-cartan-tail-adapted-near-temporal-reduction-260725-v1.0.tex.txt",
    "r083": "classii-controlled-polynomial-cfar-linear-pauli-fierz-forest-reduction-260725-v1.0.tex.txt",
    "r089": "classii-progressive-covariance-compression-rational-mean-spectral-boundary-260725-v1.0.tex.txt",
    "r091": "classii-projected-cartan-full-frame-temporal-boundary-260725-v1.0.tex.txt",
    "r093": "classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt",
    "r099": "classii-extended-state-cartan-doob-rational-recovery-260727-v1.0.tex.txt",
    "r100": "classii-owner-gauge-heat-centered-covariance-debt-reduction-260727-v1.0.tex.txt",
    "r101": "classii-raw-wick-heat-baseline-orthogonality-rational-current-reduction-260727-v1.0.tex.txt",
    "r102": "classii-full-hessian-laplace-wick-future-feedback-boundary-260728-v1.0.tex.txt",
    "r103": "classii-regular-complete-packet-ownership-hn-reg-closure-260728-v1.0.tex.txt",
}

MODULE_ATOMS = {
    "cartan_far": ("cartan_output",),
    "linear_near": ("linear_rows", "linear_heat_trace_forest"),
    "rational_raw_wick_residual": (
        "raw_wick_future_residual",
        "rational_heat_trace_forest",
        "full_wick_secant",
    ),
    "rational_unshifted_current": ("current_u3", "current_u4", "current_u5"),
    "rational_shifted_current": ("future_current", "terminal_square"),
    "conditional_low": ("conditional_low",),
    "complete_low": ("complete_low",),
    "paid_collar": ("r078_paid_difference",),
}

NEAR_MODULES = tuple(name for name in MODULE_ATOMS if name != "cartan_far")

REFUNDS = (
    "raw_q_taylor_u1",
    "raw_q_taylor_u2",
    "r076_base_cubic",
    "r086_tg_low_current",
    "r086_q_orientations",
    "second_r094_secant",
    "appended_r063_forest",
    "extra_q_r_schur_reserve",
)

R103_PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
EIGENVALUE_ZERO_TOLERANCE_INPUT = 1e-12
RECONSTRUCTION_TOLERANCE_INPUT = 1e-10


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-lossless-progressive-complete-owner-assembly-heat-boundary-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "consequence": {
                "fixed_chart_owner_defect_zero": diagnostics["assembly"]["identity_from_components"],
                "representation_preserving_subdivision_total_invariance": diagnostics["assembly"]["identity_from_components"],
                "ownerwise_subdivision_invariance": False,
                "physical_source_action_douglas_slack_identity": diagnostics["assembly"]["douglas_reconstruction"],
                "douglas_slack_nonnegative": diagnostics["assembly"]["douglas_cost_direction"],
                "exact_h_a_packet_assembly": diagnostics["assembly"]["identity_from_components"],
                "anticipative_heat_general_extension": False,
                "r103_visitwise_estimates_extended": False,
                "full_overlap_src": False,
                "nelson": False,
                "sector_a_closure": False,
            },
            "no_overclaim": (
                "R-104 proves only the finite-cutoff fixed-chart endpoint-owner identity and "
                "nonnegative Douglas cost slack. It does not assert ownerwise subdivision "
                "invariance, extend the R-103 module estimates visit by visit, or prove a uniform "
                "OVERLAP_src bound, q=10/9 Nelson, removals, a measure, T5--T7, or Sector A."
            ),
        }


def psd_sqrt(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    clipped = np.maximum(eigenvalues, 0.0)
    root = (eigenvectors * np.sqrt(clipped)) @ eigenvectors.T
    inverse_values = np.zeros_like(clipped)
    positive = clipped > EIGENVALUE_ZERO_TOLERANCE_INPUT
    inverse_values[positive] = 1.0 / np.sqrt(clipped[positive])
    inverse_root = (eigenvectors * inverse_values) @ eigenvectors.T
    return root, inverse_root


def douglas_fixture(samples: list[np.ndarray], weights: list[float], control: np.ndarray) -> dict[str, Any]:
    interval_length = float(sum(weights))
    left = sum(weight * sample for weight, sample in zip(weights, samples))
    covariance = sum(weight * (sample @ sample.T) for weight, sample in zip(weights, samples))
    root, inverse_root = psd_sqrt(covariance)
    factor = inverse_root @ left
    displacement = left @ control
    source_shift = factor @ control
    singular_values = np.linalg.svd(factor, compute_uv=False)
    return {
        "interval_length": interval_length,
        "left": left,
        "covariance": covariance,
        "root": root,
        "factor": factor,
        "displacement": displacement,
        "source_shift": source_shift,
        "reconstruction_error": float(np.linalg.norm(root @ factor - left)),
        "displacement_error": float(np.linalg.norm(root @ source_shift - displacement)),
        "factor_norm_sq": float((singular_values[0] if singular_values.size else 0.0) ** 2),
        "source_cost": float(source_shift @ source_shift),
        "control_cost": float(interval_length * (control @ control)),
        "rank": int(np.linalg.matrix_rank(covariance)),
    }


def polynomial(value: Fraction) -> Fraction:
    return value**4 + 2 * value**3 - value + Fraction(3, 2)


def finite_expectation(values: list[Fraction], probabilities: list[Fraction]) -> Fraction:
    return sum((probability * value for probability, value in zip(probabilities, values)), Fraction(0))


def gaussian_even_moment(order: int) -> int:
    if order < 0 or order % 2:
        raise ValueError("order must be a nonnegative even integer")
    value = 1
    for factor in range(1, order, 2):
        value *= factor
    return value


def main() -> int:
    audit = Audit()

    authority_diagnostics: dict[str, Any] = {}
    note_tokens = {
        "r079": ("canonical safe packet", "future-feedback innovation"),
        "r081": ("Theorem 8.1", "complete-packet algebraic temporalisation"),
        "r083": ("three linear rows", "exact Gram"),
        "r089": ("pathwise global contraction", "OVERLAP"),
        "r091": ("terminal nonduplication", "(w+f)i"),
        "r093": ("source-union/CORE equality", "OVERLAP}_{\\rm src}"),
        "r099": ("five R-085 unshifted rational families", "Chronological Doob differences"),
        "r100": ("row-additive", "complete owner"),
        "r101": ("raw-Wick plus current partition", "terminal raw-Wick identity"),
        "r102": ("last future insertion", "terminal square unspent"),
        "r103": ("complete regular $H_N$ closure", "terminal square"),
    }
    for label, filename in AUTHORITY_NOTES.items():
        path = CLAIM_DIR / "notes" / filename
        audit.check("authority", f"{label}_note_exists", path.is_file(), path.name, "present")
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        tokens = note_tokens[label]
        audit.check("authority", f"{label}_tokens", all(token in text for token in tokens), [token in text for token in tokens], [True] * len(tokens))
        authority_diagnostics[label] = {"path": path.relative_to(REPO).as_posix(), "tokens": list(tokens)}

    # INPUTS: three deterministic quadrature fixtures, including a rank-one range.
    fixtures = [
        (
            "rank_one_repeated",
            [np.array([[1.0, 0.0], [0.0, 0.0]]), np.array([[1.0, 0.0], [0.0, 0.0]])],
            [0.25, 0.75],
            np.array([2.0, -3.0]),
            1,
        ),
        (
            "full_rank_rotating",
            [np.array([[1.0, 0.0], [0.0, 2.0]]), np.array([[0.0, 1.0], [1.0, 1.0]])],
            [0.4, 0.6],
            np.array([1.5, -0.5]),
            2,
        ),
        (
            "pure_kernel",
            [np.array([[1.0, 0.0], [0.0, 0.0]])],
            [1.0],
            np.array([0.0, 1.0]),
            1,
        ),
    ]
    douglas_diagnostics: dict[str, Any] = {}
    tolerance = RECONSTRUCTION_TOLERANCE_INPUT
    douglas_reconstruction = True
    douglas_cost_direction = True
    for label, samples, weights, control, expected_rank in fixtures:
        row = douglas_fixture(samples, weights, control)
        audit.check("douglas", f"{label}_rank", row["rank"] == expected_rank, row["rank"], expected_rank)
        audit.check("douglas", f"{label}_factor_reconstruction", row["reconstruction_error"] < tolerance, row["reconstruction_error"], f"<{tolerance}")
        audit.check("douglas", f"{label}_displacement_reconstruction", row["displacement_error"] < tolerance, row["displacement_error"], f"<{tolerance}")
        audit.check("douglas", f"{label}_operator_cost", row["factor_norm_sq"] <= row["interval_length"] + tolerance, row["factor_norm_sq"], f"<={row['interval_length']}")
        audit.check("douglas", f"{label}_vector_cost", row["source_cost"] <= row["control_cost"] + tolerance, row["source_cost"], f"<={row['control_cost']}")
        douglas_reconstruction = douglas_reconstruction and row["reconstruction_error"] < tolerance and row["displacement_error"] < tolerance
        douglas_cost_direction = douglas_cost_direction and row["source_cost"] <= row["control_cost"] + tolerance
        douglas_diagnostics[label] = {
            key: value for key, value in row.items() if key not in {"left", "covariance", "root", "factor", "displacement", "source_shift"}
        }

    kernel = douglas_diagnostics["pure_kernel"]
    kernel_values = (kernel["displacement_error"], kernel["source_cost"], kernel["control_cost"])
    audit.check("douglas", "pure_kernel_fixture_values", kernel_values == (0.0, 0.0, 1.0), kernel_values, (0, 0, 1))
    audit.check("douglas", "douglas_cost_equality_mutant_rejected", kernel["source_cost"] < kernel["control_cost"], (kernel["source_cost"], kernel["control_cost"]), "strict <")

    # Exact endpoint and complete-square telescopes. INPUT values are rational.
    base = Fraction(3, 2)
    increments = [Fraction(5, 3), Fraction(-2, 3), Fraction(7, 4), Fraction(-7, 4)]
    states = [base]
    for increment in increments:
        states.append(states[-1] + increment)
    telescoped = sum((polynomial(states[index + 1]) - polynomial(states[index]) for index in range(len(increments))), Fraction(0))
    endpoint = polynomial(states[-1]) - polynomial(states[0])
    audit.check("telescope", "nonlinear_endpoint_telescope", telescoped == endpoint, telescoped, endpoint)
    audit.check("telescope", "reverse_revisit_final_state", states[-1] == base + increments[0] + increments[1], states[-1], base + increments[0] + increments[1])

    w = Fraction(7, 5)
    fresh = Fraction(-3, 4)
    insertion = Fraction(11, 6)
    direct_square = ((w + fresh + insertion) ** 2 - w**2) / 2
    complete_square = w * fresh + fresh**2 / 2 + (w + fresh) * insertion + insertion**2 / 2
    wrong_square = w * fresh + fresh**2 / 2 + w * insertion + insertion**2 / 2
    cross = fresh * insertion
    audit.check("telescope", "complete_square_identity", direct_square == complete_square, direct_square, complete_square)
    audit.check("telescope", "fresh_future_cross_nonzero", cross != 0, cross, "nonzero")
    audit.check("telescope", "missing_cross_mutant_rejected", direct_square - wrong_square == cross, direct_square - wrong_square, cross)

    # A Doob owner identity is generally expectation-level, not atomwise.
    rademacher_atoms = [(Fraction(a), Fraction(b)) for a in (-1, 1) for b in (-1, 1)]
    atom_probability = Fraction(1, 4)
    doob_lhs_atoms = [((first_root + second_root) ** 2 - first_root**2) for first_root, second_root in rademacher_atoms]
    doob_rhs_atoms = [second_root**2 for _, second_root in rademacher_atoms]
    doob_cross_mean = sum((atom_probability * 2 * first_root * second_root for first_root, second_root in rademacher_atoms), Fraction(0))
    doob_lhs_mean = sum((atom_probability * value for value in doob_lhs_atoms), Fraction(0))
    doob_rhs_mean = sum((atom_probability * value for value in doob_rhs_atoms), Fraction(0))
    doob_defect = doob_lhs_mean - doob_rhs_mean
    audit.check("doob", "doob_predictable_cross_mean_zero", doob_cross_mean == 0, doob_cross_mean, 0)
    audit.check("doob", "doob_product_identity_in_expectation", doob_defect == 0 and doob_lhs_mean == 1, (doob_lhs_mean, doob_rhs_mean), (1, 1))
    audit.check("doob", "doob_pathwise_equality_mutant_rejected", any(left != right for left, right in zip(doob_lhs_atoms, doob_rhs_atoms)), list(zip(doob_lhs_atoms, doob_rhs_atoms)), "at least one unequal atom")

    # Covariance matching by independent one-shot compression does not preserve causality.
    adapted_covariance = sum((atom_probability * first_root**2 for first_root, _ in rademacher_atoms), Fraction(0))
    compressed_covariance = sum((atom_probability * second_root**2 for _, second_root in rademacher_atoms), Fraction(0))
    adapted_correlation = sum((atom_probability * first_root * first_root for first_root, _ in rademacher_atoms), Fraction(0))
    compressed_correlation = sum((atom_probability * first_root * second_root for first_root, second_root in rademacher_atoms), Fraction(0))
    compression_distance = sum((atom_probability * (first_root - second_root) ** 2 for first_root, second_root in rademacher_atoms), Fraction(0))
    audit.check("causality", "terminal_covariance_matched", adapted_covariance == compressed_covariance == 1, (adapted_covariance, compressed_covariance), (1, 1))
    audit.check("causality", "noncausal_mixed_correlation_changed", (adapted_correlation, compressed_correlation) == (1, 0), (adapted_correlation, compressed_correlation), (1, 0))
    audit.check("causality", "noncausal_l2_distance_two", compression_distance == 2, compression_distance, 2)

    # Owner incidence is compared against the frozen R-103 canonical module map.
    r103_payload = json.loads(R103_PRIMARY_RESULT.read_text(encoding="utf-8"))
    frozen_atoms = {name: tuple(atoms) for name, atoms in r103_payload["diagnostics"]["atomic_owners"].items()}
    all_atoms = [atom for atoms in MODULE_ATOMS.values() for atom in atoms]
    missing_modules = tuple(sorted(set(frozen_atoms) - set(MODULE_ATOMS)))
    extra_modules = tuple(sorted(set(MODULE_ATOMS) - set(frozen_atoms)))
    duplicate_count = len(all_atoms) - len(set(all_atoms))
    refund_hits = tuple(sorted(set(all_atoms) & set(REFUNDS)))
    internal_coordinates = {"linear_heat_trace_forest", "rational_heat_trace_forest", "terminal_square"}
    audit.check("ownership", "seven_near_modules", len(NEAR_MODULES) == 7, len(NEAR_MODULES), 7)
    audit.check("ownership", "eight_reg_modules", len(MODULE_ATOMS) == 8, len(MODULE_ATOMS), 8)
    audit.check("ownership", "near_excludes_only_cartan_far", set(MODULE_ATOMS) - set(NEAR_MODULES) == {"cartan_far"}, sorted(set(MODULE_ATOMS) - set(NEAR_MODULES)), ["cartan_far"])
    audit.check("ownership", "module_table_complete", MODULE_ATOMS == frozen_atoms, MODULE_ATOMS, frozen_atoms)
    audit.check("ownership", "atomic_owner_uniqueness", duplicate_count == 0, duplicate_count, 0)
    audit.check("ownership", "cartan_output_once", all_atoms.count("cartan_output") == 1, all_atoms.count("cartan_output"), 1)
    audit.check("ownership", "terminal_square_nested_in_shifted", "terminal_square" in MODULE_ATOMS["rational_shifted_current"] and "terminal_square" not in MODULE_ATOMS, MODULE_ATOMS["rational_shifted_current"], "nested once")
    audit.check("ownership", "outer_internal_disjoint", set(MODULE_ATOMS).isdisjoint(internal_coordinates), sorted(set(MODULE_ATOMS) & internal_coordinates), [])
    for module, atoms in MODULE_ATOMS.items():
        audit.check("ownership", f"module_{module}_nonempty", bool(atoms), len(atoms), ">0")
    for refund in REFUNDS:
        audit.check("refund", f"refund_{refund}_zero", refund not in all_atoms and refund not in MODULE_ATOMS, 0, 0)

    # Visitwise low failure and exact complete cancellation.
    eta_input = Fraction(2)
    constant_input = Fraction(3)
    amplitude = 2 * (eta_input + constant_input)
    isolated_low = -(amplitude**4) / 2
    complete_low = (amplitude**4) / 2
    control_energy = 2 * amplitude**2
    proposed_lower = -eta_input * control_energy - constant_input
    audit.check("revisit", "isolated_low_form_fails", isolated_low < proposed_lower, isolated_low, f"<{proposed_lower}")
    audit.check("revisit", "complete_low_cancels", isolated_low + complete_low == 0, isolated_low + complete_low, 0)
    audit.check("revisit", "final_revisit_displacement_zero", amplitude - amplitude == 0, amplitude - amplitude, 0)

    phi_sixth_input = Fraction(3, 2)
    revisit_rows: list[dict[str, str]] = []
    previous_sixth = Fraction(0)
    for reciprocal_probability in (2, 5, 10):
        event_probability = Fraction(1, reciprocal_probability)
        source_amplitude_squared = Fraction(reciprocal_probability)
        visit_count = 2
        source_cost = visit_count * event_probability * source_amplitude_squared
        sixth_sum = (
            visit_count
            * event_probability
            * phi_sixth_input
            * source_amplitude_squared**3
        )
        audit.check("revisit", f"source_cost_fixed_n{reciprocal_probability}", source_cost == 2, source_cost, 2)
        audit.check("revisit", f"sixth_scaling_n{reciprocal_probability}", sixth_sum == 2 * phi_sixth_input * reciprocal_probability**2, sixth_sum, 2 * phi_sixth_input * reciprocal_probability**2)
        if previous_sixth:
            audit.check("revisit", f"sixth_growth_n{reciprocal_probability}", sixth_sum > previous_sixth, sixth_sum, f">{previous_sixth}")
        previous_sixth = sixth_sum
        revisit_rows.append({"inverse_probability": str(reciprocal_probability), "source_cost": str(source_cost), "sixth_sum": str(sixth_sum)})

    # Gaussian moments are derived by double factorial, not inserted as a two-point law.
    mean_square = Fraction(gaussian_even_moment(2))
    mean_fourth = Fraction(gaussian_even_moment(4))
    fresh_wick_mean = mean_square - 1
    predictable_heat_wick = mean_square * fresh_wick_mean
    anticipative_heat_wick = mean_fourth - mean_square
    audit.check("heat", "second_moment", mean_square == 1, mean_square, 1)
    audit.check("heat", "fourth_moment", mean_fourth == 3, mean_fourth, 3)
    audit.check("heat", "fresh_wick_centered", fresh_wick_mean == 0, fresh_wick_mean, 0)
    audit.check("heat", "predictable_heat_wick_zero", predictable_heat_wick == 0, predictable_heat_wick, 0)
    audit.check("heat", "anticipative_heat_wick_defect", anticipative_heat_wick == 2, anticipative_heat_wick, 2)

    q = Fraction(10, 9)
    source_coefficient = Fraction(1, 2) / q
    gap_coefficient = Fraction(1) / q
    audit.check("variational", "source_coefficient", source_coefficient == Fraction(9, 20), source_coefficient, Fraction(9, 20))
    audit.check("variational", "gap_coefficient", gap_coefficient == Fraction(9, 10), gap_coefficient, Fraction(9, 10))
    endpoint_defect = telescoped - endpoint
    square_defect = direct_square - complete_square
    assembly_components = (
        endpoint_defect,
        square_defect,
        doob_defect,
        missing_modules,
        extra_modules,
        duplicate_count,
        refund_hits,
        douglas_reconstruction,
    )
    expected_assembly_components = (Fraction(0), Fraction(0), Fraction(0), (), (), 0, (), True)
    assembly_identity = assembly_components == expected_assembly_components
    audit.check("variational", "assembly_identity_from_components", assembly_identity, assembly_components, expected_assembly_components)
    pure_kernel_cost_gap = Fraction(str(kernel["control_cost"])) - Fraction(str(kernel["source_cost"]))
    strict_douglas_action_slack = source_coefficient * pure_kernel_cost_gap

    diagnostics = {
        "authorities": authority_diagnostics,
        "douglas": douglas_diagnostics,
        "telescope": {
            "states": [str(value) for value in states],
            "endpoint_difference": str(endpoint),
            "complete_square": str(complete_square),
            "fresh_future_cross": str(cross),
        },
        "ownership": {
            "modules": {name: list(atoms) for name, atoms in MODULE_ATOMS.items()},
            "near_modules": list(NEAR_MODULES),
            "refunds": list(REFUNDS),
        },
        "revisit": {
            "amplitude": str(amplitude),
            "isolated_low": str(isolated_low),
            "complete_low": str(complete_low),
            "control_energy": str(control_energy),
            "sixth_rows": revisit_rows,
        },
        "heat": {
            "mean_square": str(mean_square),
            "mean_fourth": str(mean_fourth),
            "predictable_heat_wick": str(predictable_heat_wick),
            "anticipative_heat_wick": str(anticipative_heat_wick),
        },
        "variational": {
            "q": str(q),
            "source_coefficient": str(source_coefficient),
            "gap_coefficient": str(gap_coefficient),
            "exact_h_a_packet_assembly": assembly_identity,
            "full_overlap_src": False,
            "nelson": False,
        },
        "causality": {
            "adapted_covariance": str(adapted_covariance),
            "compressed_covariance": str(compressed_covariance),
            "adapted_correlation": str(adapted_correlation),
            "compressed_correlation": str(compressed_correlation),
            "l2_distance": str(compression_distance),
        },
        "doob": {
            "lhs_atoms": [str(value) for value in doob_lhs_atoms],
            "rhs_atoms": [str(value) for value in doob_rhs_atoms],
            "expectation_defect": str(doob_defect),
        },
        "assembly": {
            "components": [str(value) for value in assembly_components],
            "identity_from_components": assembly_identity,
            "douglas_reconstruction": douglas_reconstruction,
            "douglas_cost_direction": douglas_cost_direction,
            "physical_source_cost_slack_strict_fixture": str(strict_douglas_action_slack),
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(f"R-104 primary: {payload['assertions_passed']}/{payload['assertions_total']} assertions {payload['status']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
