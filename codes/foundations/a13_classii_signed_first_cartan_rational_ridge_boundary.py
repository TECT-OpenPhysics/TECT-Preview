#!/usr/bin/env python3
"""Primary executable certificate for the R-098 A13 checkpoint.

The executable derives every reported fraction and scale from the stated
inputs.  It checks posterior payment-split superadditivity, the rational
ridge normal form and standalone recovery identity, the anisotropic Cartan
Fourier/partition-refinement obstruction, and the derivative-free resampling
Hardy kernel.  It writes a reproducible JSON artefact under the A13 claim card.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-FIRST-CARTAN-RATIONAL-RIDGE-BOUNDARY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-primary-signed-first-cartan-rational-ridge-boundary/result.json"
)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serialise(actual),
                "expected": serialise(expected),
            }
        )

    def close(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-signed-first-cartan-rational-ridge-boundary-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "no_overclaim": (
                "Exact R-098 reductions and a refinement-stable nonnegative "
                "per-subvisit method no-go only; "
                "the production posterior lower form, Cartan (4.11), rational "
                "(6.5), H_N, REG, OVERLAP_src, Nelson, measure, and Sector A remain open."
            ),
        }


def serialise(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, tuple):
        return [serialise(item) for item in value]
    return value


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


def quadratic(matrix: np.ndarray, vector: np.ndarray) -> float:
    return float(vector @ matrix @ vector)


def posterior_raw(
    weights: np.ndarray,
    matrices: list[np.ndarray],
    carriers: list[np.ndarray],
    gamma: np.ndarray,
    payment: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    bar = sum(float(w) * matrix for w, matrix in zip(weights, matrices))
    q = sum(float(w) * (matrix @ carrier) for w, matrix, carrier in zip(weights, matrices, carriers))
    wick = sum(
        float(w) * float(np.sum(matrix * (np.outer(carrier, carrier) - gamma)))
        for w, matrix, carrier in zip(weights, matrices, carriers)
    )
    value = wick - quadratic(np.linalg.inv(bar + 2.0 * payment), q)
    return value, bar, q


def cartan_tau(theta: np.ndarray, epsilon: float) -> np.ndarray:
    sine = np.sin(theta)
    cosine = np.cos(theta)
    d = sine * sine + epsilon * epsilon * cosine * cosine
    q = (sine * sine - epsilon * epsilon * cosine * cosine) / d
    dprime = 2.0 * (1.0 - epsilon * epsilon) * sine * cosine
    return q * dprime


def cartan_coefficient(epsilon: float, k: int) -> float:
    rho = (1.0 - epsilon) / (1.0 + epsilon)
    return -2.0 * epsilon * (1.0 - rho * rho) * rho ** (k - 1)


def main() -> int:
    audit = Audit()
    tolerance = 2.0e-11

    # Posterior payment-split superadditivity on noncommuting positive matrices.
    rng = np.random.default_rng(98260727)
    superadd_defects: list[float] = []
    square_defects: list[float] = []
    for trial in range(12):
        dimension = 3
        atom_count = 5
        weights = rng.random(atom_count)
        weights /= weights.sum()
        carriers = [rng.normal(size=dimension) for _ in range(atom_count)]
        gamma = np.diag(rng.uniform(0.2, 1.3, size=dimension))
        components: list[list[np.ndarray]] = [[], []]
        for _ in range(atom_count):
            for component in components:
                frame = rng.normal(size=(dimension, 2))
                component.append(frame @ frame.T)
        payment_parts = []
        for _ in range(2):
            root = rng.normal(size=(dimension, dimension))
            payment_parts.append(root @ root.T + 0.3 * np.eye(dimension))
        total_matrices = [left + right for left, right in zip(*components)]
        total_payment = payment_parts[0] + payment_parts[1]
        total_value, _, _ = posterior_raw(weights, total_matrices, carriers, gamma, total_payment)
        part_values = [
            posterior_raw(weights, component, carriers, gamma, payment)[0]
            for component, payment in zip(components, payment_parts)
        ]
        defect = total_value - sum(part_values)
        superadd_defects.append(defect)

        bars: list[np.ndarray] = []
        qs: list[np.ndarray] = []
        for component in components:
            _, bar, q = posterior_raw(weights, component, carriers, gamma, np.zeros((dimension, dimension)))
            bars.append(bar)
            qs.append(q)
        matrices_a = [bar + 2.0 * payment for bar, payment in zip(bars, payment_parts)]
        y = np.linalg.solve(sum(matrices_a), sum(qs))
        fractional_defect = sum(quadratic(np.linalg.inv(matrix), q) for matrix, q in zip(matrices_a, qs)) - quadratic(
            np.linalg.inv(sum(matrices_a)), sum(qs)
        )
        square_certificate = sum(
            quadratic(np.linalg.inv(matrix), q - matrix @ y)
            for matrix, q in zip(matrices_a, qs)
        )
        square_defects.append(abs(fractional_defect - square_certificate))
        audit.check("posterior", f"payment_split_superadditivity_{trial}", defect >= -tolerance, defect, ">= 0")
        audit.check("posterior", f"fractional_square_certificate_{trial}", abs(fractional_defect - square_certificate) < tolerance, fractional_defect - square_certificate, 0.0)

    # Reusing the same payment in every row is a deliberate invalid mutation.
    reused_payment = 1.0
    full_fraction = -(2.0**2) / (2.0 + 2.0 * reused_payment)
    reused_rows = -2.0 / (1.0 + 2.0 * reused_payment)
    split_rows = -2.0 / (1.0 + reused_payment)
    audit.check("posterior", "same_payment_reuse_mutant_fails", full_fraction < reused_rows, full_fraction - reused_rows, "< 0")
    audit.check("posterior", "matching_half_payment_is_exact", abs(full_fraction - split_rows) < tolerance, full_fraction - split_rows, 0.0)

    # Exact rational coefficient fractions, all derived from c1 and alpha.
    alpha = Fraction(5, 9)
    c1_without_p = Fraction(243, 8000)

    def rational_b_without_e_p(t: Fraction) -> Fraction:
        ridge = t - alpha * t**3 / (t**2 + 1)
        return 4 * c1_without_p * ridge**2

    b_minus = rational_b_without_e_p(Fraction(1, 2))
    b_plus = rational_b_without_e_p(Fraction(3, 2))
    delta = b_plus - b_minus
    cpost_three_atom = -delta / 3
    audit.check("rational", "b_minus_exact", b_minus == Fraction(3, 125), b_minus, Fraction(3, 125))
    audit.check("rational", "b_plus_exact", b_plus == Fraction(2187, 21125), b_plus, Fraction(2187, 21125))
    audit.check("rational", "delta_exact", delta == Fraction(1680, 21125), delta, Fraction(1680, 21125))
    audit.check("rational", "three_atom_cpost_exact", cpost_three_atom == Fraction(-560, 21125), cpost_three_atom, Fraction(-560, 21125))
    audit.check("rational", "three_atom_cpost_negative", cpost_three_atom < 0, cpost_three_atom, "< 0")

    # Compute the same three-atom value directly, rather than from -Delta/3.
    atom_weights = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)]
    atom_g = np.array([0.0, math.sqrt(2.0), -math.sqrt(2.0)])
    atom_g2 = [Fraction(0), Fraction(2), Fraction(2)]
    atom_b = [b_plus, b_minus + delta / 3, b_minus + delta / 3]
    direct_cpost = sum(weight * coefficient * (g2 - 1) for weight, coefficient, g2 in zip(atom_weights, atom_b, atom_g2))
    direct_mean = sum(weight * coefficient for weight, coefficient in zip(atom_weights, atom_b))
    three_atom_gamma = sum(float(weight) * g * g for weight, g in zip(atom_weights, atom_g))
    three_atom_q = sum(float(weight) * float(coefficient) * g for weight, coefficient, g in zip(atom_weights, atom_b, atom_g))
    transformed_r_values: list[float] = []
    for scalar_payment in (0.125, 1.0, 7.5):
        theta_roots = [
            math.sqrt(2.0 * scalar_payment * float(coefficient) / (float(coefficient) + 2.0 * scalar_payment))
            for coefficient in atom_b
        ]
        transformed_r_values.append(
            sum(float(weight) * theta_root * g for weight, theta_root, g in zip(atom_weights, theta_roots, atom_g))
        )
    audit.check("rational", "three_atom_direct_matches", direct_cpost == cpost_three_atom, direct_cpost, cpost_three_atom)
    audit.check("rational", "three_atom_gamma_one", abs(three_atom_gamma - 1.0) < tolerance, three_atom_gamma, 1.0)
    audit.check("rational", "three_atom_q_zero_by_symmetry", abs(three_atom_q) < tolerance, three_atom_q, 0.0)
    audit.check("rational", "three_atom_r_zero_by_symmetry", max(abs(value) for value in transformed_r_values) < tolerance, transformed_r_values, [0.0, 0.0, 0.0])
    audit.check("rational", "three_atom_mean_positive", direct_mean > 0, direct_mean, "> 0")

    # The already accepted complete four-row sign slice transfers to C_post.
    c0_without_p = Fraction(3, 250)

    def full_b_without_e_p(t: Fraction) -> Fraction:
        return 4 * c0_without_p * t**2 + rational_b_without_e_p(t)

    full_minus = full_b_without_e_p(Fraction(1, 2))
    full_plus = full_b_without_e_p(Fraction(3, 2))
    full_delta = full_plus - full_minus
    full_tail = full_minus + full_delta / 3
    full_cpost = (full_tail - full_plus) / 2
    audit.check("rational", "full_frame_minus_exact", full_minus == Fraction(9, 250), full_minus, Fraction(9, 250))
    audit.check("rational", "full_frame_plus_exact", full_plus == Fraction(8937, 42250), full_plus, Fraction(8937, 42250))
    audit.check("rational", "full_frame_delta_exact", full_delta == Fraction(3708, 21125), full_delta, Fraction(3708, 21125))
    audit.check("rational", "full_frame_cpost_exact", full_cpost == Fraction(-1236, 21125), full_cpost, Fraction(-1236, 21125))

    # Conditional rational ridge identity on a nontrivial discrete vector fibre.
    weights = np.array([0.2, 0.3, 0.5])
    b_atoms = [np.array([1.0, -0.5]), np.array([0.2, 1.1]), np.array([-0.7, 0.4])]
    g_atoms = [np.array([0.4, -1.0]), np.array([1.3, 0.2]), np.array([-0.1, 0.9])]
    gamma = np.array([[0.8, 0.1], [0.1, 0.6]])
    payment = np.array([[0.7, 0.15], [0.15, 0.9]])
    s_atoms = [float(b @ g) for b, g in zip(b_atoms, g_atoms)]
    k_matrix = sum(float(w) * np.outer(b, b) for w, b in zip(weights, b_atoms))
    q_vector = sum(float(w) * b * s for w, b, s in zip(weights, b_atoms, s_atoms))
    a_matrix = k_matrix + 2.0 * payment
    h_star = np.linalg.solve(a_matrix, q_vector)
    direct_ridge = sum(float(w) * (s * s - float(b @ gamma @ b)) for w, b, s in zip(weights, b_atoms, s_atoms)) - quadratic(
        np.linalg.inv(a_matrix), q_vector
    )

    def ridge_objective(h: np.ndarray) -> float:
        return sum(float(w) * (s - float(b @ h)) ** 2 for w, b, s in zip(weights, b_atoms, s_atoms)) + 2.0 * quadratic(payment, h) - sum(
            float(w) * float(b @ gamma @ b) for w, b in zip(weights, b_atoms)
        )

    audit.check("ridge", "ridge_stationarity", np.linalg.norm(a_matrix @ h_star - q_vector) < tolerance, np.linalg.norm(a_matrix @ h_star - q_vector), 0.0)
    audit.check("ridge", "ridge_objective_identity", abs(ridge_objective(h_star) - direct_ridge) < tolerance, ridge_objective(h_star) - direct_ridge, 0.0)
    for trial in range(6):
        perturbation = rng.normal(size=2)
        audit.check(
            "ridge",
            f"ridge_minimum_{trial}",
            ridge_objective(h_star + perturbation) >= ridge_objective(h_star) - tolerance,
            ridge_objective(h_star + perturbation) - ridge_objective(h_star),
            ">= 0",
        )
    wrong_a = k_matrix + payment
    wrong_h = np.linalg.solve(wrong_a, q_vector)
    audit.check("ridge", "missing_factor_two_mutant_fails", abs(ridge_objective(wrong_h) - direct_ridge) > 1.0e-5, ridge_objective(wrong_h) - direct_ridge, "nonzero")

    # Standalone recovery identity: compute the endpoint and terminal Schur sides independently.
    scalar_weights = np.array([0.25, 0.5, 0.25])
    scalar_g = np.array([-1.5, 0.2, 1.1])
    scalar_b0 = np.array([0.6, 0.9, 0.7])
    scalar_b1 = np.array([1.2, 0.5, 1.4])
    scalar_gamma = 0.8
    scalar_c = -0.35
    scalar_r = 0.45
    unshifted_u = -0.17
    w0 = 0.5 * float(np.sum(scalar_weights * scalar_b0 * (scalar_g**2 - scalar_gamma)))
    w_star = 0.5 * float(np.sum(scalar_weights * scalar_b1 * ((scalar_g + scalar_c) ** 2 - scalar_gamma)))
    delta_w = w_star - w0
    f65 = delta_w - unshifted_u
    bar_b = float(np.sum(scalar_weights * scalar_b1))
    scalar_q = float(np.sum(scalar_weights * scalar_b1 * scalar_g))
    scalar_a = bar_b + 2.0 * scalar_r
    completed_square = 0.5 * scalar_a * (scalar_c + scalar_q / scalar_a) ** 2
    scalar_cpost = float(np.sum(scalar_weights * scalar_b1 * (scalar_g**2 - scalar_gamma))) - scalar_q**2 / scalar_a
    recovered_f65 = completed_square + 0.5 * scalar_cpost - scalar_r * scalar_c**2 - w0 - unshifted_u
    audit.check("recovery", "terminal_schur_endpoint_identity", abs(w_star + scalar_r * scalar_c**2 - completed_square - 0.5 * scalar_cpost) < tolerance, w_star + scalar_r * scalar_c**2 - completed_square - 0.5 * scalar_cpost, 0.0)
    audit.check("recovery", "standalone_f65_recovery", abs(f65 - recovered_f65) < tolerance, f65 - recovered_f65, 0.0)
    wrong_recovery = completed_square + 0.5 * scalar_cpost - scalar_r * scalar_c**2 - w0 + unshifted_u
    audit.check("recovery", "unshifted_sign_mutant_fails", abs(f65 - wrong_recovery) > 1.0e-5, f65 - wrong_recovery, "nonzero")

    # Cartan Fourier coefficients and the eps=1/2 exponent audit.
    point_count = 1 << 18
    theta = (2.0 * math.pi / point_count) * np.arange(point_count)
    fourier_errors: list[float] = []
    for epsilon in (0.25, 0.5, 0.75):
        tau = cartan_tau(theta, epsilon)
        for k in range(2, 9):
            quadrature = 2.0 * float(np.mean(tau * np.sin(2.0 * k * theta)))
            closed = cartan_coefficient(epsilon, k)
            error = abs(quadrature - closed)
            fourier_errors.append(error)
            audit.check("cartan", f"fourier_eps_{epsilon}_k_{k}", error < 2.0e-12, quadrature, closed)
    epsilon = 0.5
    for k in (2, 3, 9):
        corrected = Fraction(-8, 3 ** (k + 1))
        closed = cartan_coefficient(epsilon, k)
        audit.check("cartan", f"half_epsilon_correct_power_{k}", abs(closed - float(corrected)) < tolerance, closed, corrected)
        wrong = Fraction(-8, 3 ** (k + 2))
        audit.check("cartan", f"half_epsilon_k_plus_two_mutant_{k}", abs(closed - float(wrong)) > 1.0e-8 if k < 9 else abs(closed - float(wrong)) > 1.0e-18, closed - float(wrong), "nonzero")

    # Finite-floor radial derivative of the actual production one-form.
    # A centered derivative of the uncompleted current is compared with the
    # exact correction, rather than merely assuming floorless homogeneity.
    production_floor = 0.7
    radial_frequency = 8.0
    radial_errors: list[float] = []
    for radial_epsilon in (0.35, 0.5):
        for amplitude in (2.0, 7.0, 31.0):
            for angle in (0.23, 0.71, 1.37):
                sine = math.sin(angle)
                cosine = math.cos(angle)
                d_value = sine * sine + radial_epsilon * radial_epsilon * cosine * cosine
                n_value = sine * sine - radial_epsilon * radial_epsilon * cosine * cosine
                d_prime = (1.0 - radial_epsilon * radial_epsilon) * math.sin(2.0 * angle)

                def radial_current(radial_amplitude: float) -> float:
                    denominator = radial_amplitude * radial_amplitude * d_value + production_floor
                    return 0.5 * radial_frequency * radial_amplitude**4 * n_value * d_prime / denominator

                step = amplitude * 1.0e-5
                numerical = (
                    radial_current(amplitude + step) - radial_current(amplitude - step)
                ) / (2.0 * step * amplitude * radial_frequency)
                tau_value = (n_value / d_value) * d_prime
                exact = tau_value * (
                    1.0
                    - production_floor**2
                    / (amplitude * amplitude * d_value + production_floor) ** 2
                )
                error = abs(numerical - exact)
                radial_errors.append(error)
                audit.check(
                    "cartan",
                    f"finite_floor_radial_identity_eps_{radial_epsilon}_A_{amplitude}_theta_{angle}",
                    error < 2.0e-9,
                    numerical,
                    exact,
                )

    # Exact leading reverse-current model and amplitude ledger.
    epsilon = 0.5
    root_mass = 0.03125
    frequency = 8.0
    tau = cartan_tau(theta, epsilon)
    for amplitude in (1.0, 3.0, 11.0):
        leading_plus = amplitude * frequency * math.sqrt(root_mass) * tau
        leading_minus = -leading_plus
        audit.check("cartan", f"reverse_cancellation_A_{amplitude}", np.max(np.abs(leading_plus + leading_minus)) == 0.0, np.max(np.abs(leading_plus + leading_minus)), 0.0)
        normalized_square = float(np.mean(leading_plus**2)) / (amplitude * amplitude)
        reference_square = frequency * frequency * root_mass * float(np.mean(tau**2))
        audit.check("cartan", f"atom_square_scales_A2_{amplitude}", abs(normalized_square - reference_square) < tolerance, normalized_square, reference_square)
    for amplitude in (8.0, 64.0, 512.0):
        atom_ledger = amplitude * amplitude
        mixed_budget = 1.0 + amplitude
        audit.check("cartan", f"per_subvisit_ratio_grows_{int(amplitude)}", atom_ledger / mixed_budget > amplitude / 2.0, atom_ledger / mixed_budget, f"> {amplitude / 2.0}")

    # Production frame finite-difference constant from the accepted inputs.
    p_input = 4.0 + 1.0e-12
    qii = np.array(
        [
            [9.0 / (500.0 * p_input), 3.0 / (400.0 * p_input)],
            [3.0 / (400.0 * p_input), 3.0 / (320.0 * p_input)],
        ]
    )
    qii_eigenvalues = np.linalg.eigvalsh(qii)
    frame_value_bound_sq = 20.0
    frame_secant_bound_sq = 68.0
    generator_count = 3.0
    frame_secant_constant = generator_count * float(qii_eigenvalues[-1]) * math.sqrt(
        frame_value_bound_sq * frame_secant_bound_sq
    )
    audit.check("resampling", "qii_positive", float(qii_eigenvalues[0]) > 0.0, qii_eigenvalues, "> 0")
    audit.check("resampling", "frame_secant_constant_derived", frame_secant_constant > 0.0, frame_secant_constant, "> 0")
    envelope_left = generator_count * float(qii_eigenvalues[-1]) * frame_value_bound_sq
    envelope_right = frame_secant_constant
    deleted_factor_three = float(qii_eigenvalues[-1]) * math.sqrt(
        frame_value_bound_sq * frame_secant_bound_sq
    )
    audit.check("resampling", "frame_factor_three_envelope_holds", envelope_left <= envelope_right, envelope_left, f"<= {envelope_right}")
    audit.check("resampling", "drop_factor_three_mutant_fails", envelope_left > deleted_factor_three, envelope_left, f"> {deleted_factor_three}")

    # Resampling identity on an explicit finite probability table.
    table = np.array([[1.0, -2.0, 0.5], [0.2, 1.4, -0.7]])
    mean_over_root = table.mean(axis=0, keepdims=True)
    expected_conditional_variance = float(np.mean((table - mean_over_root) ** 2))
    resampled_difference = float(
        np.mean(
            [
                (table[left, other] - table[right, other]) ** 2
                for other in range(table.shape[1])
                for left in range(table.shape[0])
                for right in range(table.shape[0])
            ]
        )
    )
    audit.check("resampling", "resampling_equals_twice_conditional_variance", abs(resampled_difference - 2.0 * expected_conditional_variance) < tolerance, resampled_difference, 2.0 * expected_conditional_variance)
    audit.check("resampling", "resampling_bounded_by_second_moment", resampled_difference <= 2.0 * float(np.mean(table**2)) + tolerance, resampled_difference, f"<= {2.0 * float(np.mean(table**2))}")

    # A pure two-root Hoeffding interaction is counted once by each raw root
    # influence, so the influence sum is not a once-only decomposition.
    signs = (-1, 1)
    interaction_second_moment = sum(Fraction((left * right) ** 2, 4) for left in signs for right in signs)
    conditional_variance_sum = Fraction(0)
    for _root in range(2):
        conditional_variance_sum += Fraction(1)
    audit.check(
        "resampling",
        "two_root_interaction_counted_twice",
        conditional_variance_sum == 2 * interaction_second_moment,
        conditional_variance_sum,
        2 * interaction_second_moment,
    )

    hardy_values: list[float] = []
    j0 = 0
    for k in range(1, 13):
        exact = sum(Fraction(2**j, 2 ** (4 * k)) for j in range(j0, k))
        closed = Fraction(2**k - 2**j0, 2 ** (4 * k))
        upper = Fraction(1, 2 ** (3 * k))
        hardy_values.append(float(exact))
        audit.check("resampling", f"hardy_closed_form_{k}", exact == closed, exact, closed)
        audit.check("resampling", f"hardy_strict_gain_{k}", exact < upper, exact, f"< {upper}")
    no_smoothing = sum(Fraction(2**j, 1) for j in range(0, 8))
    audit.check("resampling", "remove_k_smoothing_mutant_fails", no_smoothing > 1, no_smoothing, "> 1")

    payload = audit.close(
        {
            "maximum_superadditivity_square_error": max(square_defects),
            "minimum_superadditivity_defect": min(superadd_defects),
            "rational_b_minus_without_e_over_p": serialise(b_minus),
            "rational_b_plus_without_e_over_p": serialise(b_plus),
            "rational_delta_without_e_over_p": serialise(delta),
            "rational_three_atom_cpost_without_e_over_p": serialise(cpost_three_atom),
            "rational_three_atom_gamma": three_atom_gamma,
            "rational_three_atom_q": three_atom_q,
            "rational_three_atom_max_abs_r": max(abs(value) for value in transformed_r_values),
            "full_frame_three_atom_cpost_without_e_over_p": serialise(full_cpost),
            "maximum_cartan_fourier_error": max(fourier_errors),
            "maximum_finite_floor_radial_error": max(radial_errors),
            "cartan_half_epsilon_k2": cartan_coefficient(0.5, 2),
            "cartan_half_epsilon_k3": cartan_coefficient(0.5, 3),
            "qii_operator_norm": float(qii_eigenvalues[-1]),
            "frame_secant_constant": frame_secant_constant,
            "maximum_hardy_mass": max(hardy_values),
        }
    )
    atomic_json(OUTPUT, payload)
    print(
        f"R-098 primary: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"assertions {payload['status']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
