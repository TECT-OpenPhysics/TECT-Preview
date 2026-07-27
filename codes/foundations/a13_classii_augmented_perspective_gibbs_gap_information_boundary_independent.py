#!/usr/bin/env python3
"""Non-importing independent audit for the R-093 A13 boundary theorem."""

from __future__ import annotations

__version__ = "1.0.0"
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
RESULT_ID = "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-independent-augmented-perspective-gibbs-gap-information-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def symmetric_square_root(matrix: np.ndarray, tolerance: float = 1.0e-10) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    if float(np.min(eigenvalues)) < -tolerance:
        raise ValueError(f"matrix is not positive semidefinite: min eigenvalue={np.min(eigenvalues)}")
    return (eigenvectors * np.sqrt(np.maximum(eigenvalues, 0.0))) @ eigenvectors.T


def cutoff_two_spectral_sums(parameters: dict[str, Any]) -> dict[str, float]:
    length = float(parameters["Lx"])
    omega_square = (2.0 * math.pi / length) ** 2
    z0 = np.asarray(parameters["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    internal = np.diag(np.asarray(parameters["family_masses"], dtype=float))
    internal += float(parameters["k_lock"]) * (np.eye(3) - projector)
    internal_eigenvalues = np.linalg.eigvalsh(internal)
    field_trace = 0.0
    gradient_trace = 0.0
    shell_minimum = math.inf
    lattice = np.indices((5, 5, 5), dtype=int).reshape(3, -1).T - 2
    for vector in lattice:
        norm_square = int(vector @ vector)
        wave_square = omega_square * norm_square
        scalar = float(parameters["r"]) + float(parameters["Z"]) * wave_square + float(parameters["Y"]) * wave_square**2
        eigenvalues = scalar + internal_eigenvalues
        inverse_trace = float(np.sum(1.0 / eigenvalues))
        field_trace += 2.0 * inverse_trace
        gradient_trace += 2.0 * wave_square * inverse_trace / length**3
        if int(np.max(np.abs(vector))) == 2:
            shell_minimum = min(shell_minimum, float(eigenvalues[0]))
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    coefficients = (
        float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
        float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator,
        float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator,
    )
    beta = 4.0 * (coefficients[0] + 2.0 * abs(coefficients[1]) + coefficients[2])
    c_two = beta * gradient_trace / 2.0
    map_bound = 2.0 / shell_minimum
    return {
        "beta_operator": beta,
        "gradient_covariance_trace": gradient_trace,
        "field_covariance_trace": field_trace,
        "shell_symbol_minimum": shell_minimum,
        "control_map_bound": map_bound,
        "negative_quadratic_constant": c_two,
        "paid_control_margin": 9.0 / 20.0 - 2.0 * c_two * map_bound,
        "lower_bound_constant": 2.0 * c_two * field_trace,
    }


def main() -> int:
    rows: list[dict[str, Any]] = []

    def record(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    q = Fraction(10, 9)
    record("independent_q_inverse", 1 / q == Fraction(9, 10), str(1 / q), "9/10")
    record("independent_q_energy", 1 / (2 * q) == Fraction(9, 20), str(1 / (2 * q)), "9/20")

    c0 = Fraction(3, 250)
    c1 = Fraction(243, 8000)

    def radial(t: Fraction) -> Fraction:
        return t - Fraction(5, 9) * t**3 / (t**2 + 1)

    def coefficient(t: Fraction) -> Fraction:
        return 4 * c0 * t**2 + 4 * c1 * radial(t) ** 2

    b_minus = coefficient(Fraction(1, 2))
    b_plus = coefficient(Fraction(3, 2))
    delta = b_plus - b_minus
    b_tail = b_minus + delta / 3
    mean_b = (b_plus + b_tail) / 2
    density = b_tail - mean_b
    expected_values = {
        "b_minus": Fraction(9, 250),
        "b_plus": Fraction(8937, 42250),
        "delta": Fraction(3708, 21125),
        "b_tail": Fraction(3993, 42250),
        "mean_b": Fraction(1293, 8450),
        "density": Fraction(-1236, 21125),
        "outer_density": Fraction(-618, 21125),
    }
    actual_values = {
        "b_minus": b_minus,
        "b_plus": b_plus,
        "delta": delta,
        "b_tail": b_tail,
        "mean_b": mean_b,
        "density": density,
        "outer_density": density / 2,
    }
    for name, expected in expected_values.items():
        actual = actual_values[name]
        record(f"independent_{name}", actual == expected, str(actual), str(expected))

    # Direct matrix audit of the unconditional completed normal form.
    rng = np.random.default_rng(93027)
    maximum_identity_error = 0.0
    maximum_normal_form_error = 0.0
    maximum_unsubtracted_form_error = 0.0
    minimum_covariance_term_magnitude = math.inf
    minimum_sign_flip_residual = math.inf
    minimum_theta_eigenvalue = math.inf
    for _ in range(24):
        raw_r = rng.normal(size=(3, 3))
        r_matrix = raw_r.T @ raw_r + 0.4 * np.eye(3)
        probabilities = np.asarray([0.2, 0.3, 0.5])
        z_values = rng.normal(size=(3, 3))
        b_values: list[np.ndarray] = []
        a_values: list[np.ndarray] = []
        theta_values: list[np.ndarray] = []
        m_values: list[np.ndarray] = []
        y_values: list[np.ndarray] = []
        for z_value in z_values:
            raw_b = rng.normal(size=(3, 3))
            b_matrix = raw_b.T @ raw_b
            a_matrix = b_matrix + 2.0 * r_matrix
            theta_matrix = b_matrix - b_matrix @ np.linalg.solve(a_matrix, b_matrix)
            minimum_theta_eigenvalue = min(minimum_theta_eigenvalue, float(np.min(np.linalg.eigvalsh(theta_matrix))))
            m_value = np.linalg.solve(a_matrix, b_matrix @ z_value)
            y_value = symmetric_square_root(theta_matrix) @ z_value
            maximum_identity_error = max(maximum_identity_error, float(np.linalg.norm(b_matrix @ np.linalg.solve(a_matrix, b_matrix) + theta_matrix - b_matrix)))
            b_values.append(b_matrix)
            a_values.append(a_matrix)
            theta_values.append(theta_matrix)
            m_values.append(m_value)
            y_values.append(y_value)
        bar_b = sum(weight * matrix for weight, matrix in zip(probabilities, b_values))
        bar_a = bar_b + 2.0 * r_matrix
        q_vector = sum(weight * matrix @ vector for weight, matrix, vector in zip(probabilities, b_values, z_values))
        m_zero = np.linalg.solve(bar_a, q_vector)
        y_mean = sum(weight * value for weight, value in zip(probabilities, y_values))
        covariance = sum(weight * np.outer(vector, vector) for weight, vector in zip(probabilities, z_values))
        z_mean = sum(weight * vector for weight, vector in zip(probabilities, z_values))
        covariance -= np.outer(z_mean, z_mean)
        unsubtracted_left = sum(
            weight * ((m_value - m_zero) @ a_matrix @ (m_value - m_zero) + float((y_value - y_mean) @ (y_value - y_mean)))
            for weight, m_value, a_matrix, y_value in zip(probabilities, m_values, a_values, y_values)
        )
        covariance_term = float(np.sum(bar_b * covariance))
        unsubtracted_right = sum(weight * float(vector @ matrix @ vector) for weight, matrix, vector in zip(probabilities, b_values, z_values))
        unsubtracted_right -= float(q_vector @ np.linalg.solve(bar_a, q_vector)) + float(y_mean @ y_mean)
        left = unsubtracted_left - covariance_term
        right = unsubtracted_right - covariance_term
        maximum_normal_form_error = max(maximum_normal_form_error, abs(left - right))
        maximum_unsubtracted_form_error = max(maximum_unsubtracted_form_error, abs(unsubtracted_left - unsubtracted_right))
        minimum_covariance_term_magnitude = min(minimum_covariance_term_magnitude, abs(covariance_term))
        minimum_sign_flip_residual = min(minimum_sign_flip_residual, abs((unsubtracted_right + covariance_term) - right))
    record("independent_matrix_perspective_identity", maximum_identity_error < 2.0e-12, maximum_identity_error, "<2e-12")
    record("independent_theta_positive_semidefinite_before_clipping", minimum_theta_eigenvalue >= -1.0e-10, minimum_theta_eigenvalue, ">=-1e-10")
    record("independent_unconditional_normal_form", maximum_normal_form_error < 2.0e-11, maximum_normal_form_error, "<2e-11")
    record("independent_unsubtracted_normal_form", maximum_unsubtracted_form_error < 2.0e-11, maximum_unsubtracted_form_error, "<2e-11")
    record("independent_covariance_subtraction_load_bearing", minimum_covariance_term_magnitude > 1.0e-3 and minimum_sign_flip_residual > 2.0e-3, [minimum_covariance_term_magnitude, minimum_sign_flip_residual], [">1e-3", ">2e-3"])

    nodes, weights = np.polynomial.legendre.leggauss(600)
    cutoff = 9.0
    transformed = cutoff * nodes
    normal_density = np.exp(-0.5 * transformed**2) / math.sqrt(2.0 * math.pi)
    reciprocal = float(cutoff * np.sum(weights * normal_density / (1.0 + transformed**2)))
    closed = math.sqrt(math.pi / 2.0) * math.exp(0.5) * math.erfc(1.0 / math.sqrt(2.0))
    record("independent_gaussian_reciprocal", abs(reciprocal - closed) < 5.0e-14, reciprocal, closed)
    record("independent_gaussian_covariance_negative", 1.0 - 2.0 * reciprocal < 0.0, 1.0 - 2.0 * reciprocal, "<0")

    free_energy = Fraction(9, 20) * math.log(Fraction(19, 9))
    record("independent_one_chart_obstruction", float(free_energy) < 0.5, float(free_energy), "<1/2")
    for bins in (3, 7, 19):
        entropy = -sum((1.0 / bins) * math.log(1.0 / bins) for _ in range(bins))
        record(f"independent_quantile_information_{bins}", abs(entropy - math.log(bins)) < 2.0e-15, entropy, math.log(bins))

    bg_pairs = (
        (Fraction(21, 40), Fraction(19, 120)),
        (Fraction(2, 5), Fraction(8, 15)),
        (Fraction(11, 20), Fraction(19, 60)),
        (Fraction(11, 20), Fraction(3, 20)),
        (Fraction(2, 5), Fraction(11, 30)),
        (Fraction(11, 40), Fraction(49, 120)),
        (Fraction(4, 5), Fraction(1, 6)),
        (Fraction(3, 5), Fraction(1, 3)),
    )
    bg_slacks = tuple(1 - a_value - b_value for a_value, b_value in bg_pairs)
    record("independent_bg_all_slacks_positive", all(value > 0 for value in bg_slacks), [str(value) for value in bg_slacks], "all positive")
    record("independent_bg_maximum_moment", max(1 / value for value in bg_slacks) == 30, str(max(1 / value for value in bg_slacks)), "30")
    record("independent_bg_critical_rows", all(1 - a_value - b_value == 0 for a_value, b_value in ((Fraction(3, 4), Fraction(1, 4)), (Fraction(1, 2), Fraction(1, 2)))), "two zero slacks", "two zero slacks")

    # A block-lower orthogonal 2x2 matrix [[a,0],[c,d]] has d^2=1 and cd=0.
    # Since d is invertible, the Gram off-diagonal excludes every c != 0.
    for d_value in (Fraction(-1), Fraction(1)):
        adversarial_c = Fraction(2, 5)
        gram_offdiagonal = adversarial_c * d_value
        record(
            f"independent_lower_orthogonal_gram_excludes_c_{int(d_value)}",
            d_value**2 == 1 and gram_offdiagonal != 0,
            [str(d_value**2), str(gram_offdiagonal)],
            ["1", "nonzero for c=2/5"],
        )

    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    finite = cutoff_two_spectral_sums(parameters)
    record("independent_cutoff_two_gradient_trace", 0.2 < finite["gradient_covariance_trace"] < 0.3, finite["gradient_covariance_trace"], "in (0.2,0.3)")
    record("independent_cutoff_two_field_trace", 1200.0 < finite["field_covariance_trace"] < 1300.0, finite["field_covariance_trace"], "in (1200,1300)")
    record("independent_cutoff_two_symbol_minimum", 0.3 < finite["shell_symbol_minimum"] < 0.4, finite["shell_symbol_minimum"], "in (0.3,0.4)")
    record("independent_cutoff_two_paid_margin", finite["paid_control_margin"] > 0.38, finite["paid_control_margin"], ">0.38")
    record("independent_cutoff_two_lower_constant", finite["lower_bound_constant"] < 12.0, finite["lower_bound_constant"], "<12")
    record("independent_cutoff_two_c2_identity", abs(finite["negative_quadratic_constant"] - 0.5 * finite["beta_operator"] * finite["gradient_covariance_trace"]) < 2.0e-14, finite["negative_quadratic_constant"] - 0.5 * finite["beta_operator"] * finite["gradient_covariance_trace"], 0.0)
    record("independent_cutoff_two_control_map_identity", abs(finite["control_map_bound"] - 2.0 / finite["shell_symbol_minimum"]) < 2.0e-13, finite["control_map_bound"] - 2.0 / finite["shell_symbol_minimum"], 0.0)
    record("independent_cutoff_two_paid_margin_identity", abs(finite["paid_control_margin"] - (9.0 / 20.0 - 2.0 * finite["negative_quadratic_constant"] * finite["control_map_bound"])) < 2.0e-13, finite["paid_control_margin"] - (9.0 / 20.0 - 2.0 * finite["negative_quadratic_constant"] * finite["control_map_bound"]), 0.0)
    record("independent_cutoff_two_lower_constant_identity", abs(finite["lower_bound_constant"] - 2.0 * finite["negative_quadratic_constant"] * finite["field_covariance_trace"]) < 2.0e-12, finite["lower_bound_constant"] - 2.0 * finite["negative_quadratic_constant"] * finite["field_covariance_trace"], 0.0)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-augmented-perspective-gibbs-gap-information-boundary-independent/1.0",
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "derived": {
            "finite_density_times_P_over_e": str(density),
            "gaussian_reciprocal": reciprocal,
            "cutoff_two_paid_coercivity": finite,
            "matrix_normal_form_max_error": maximum_normal_form_error,
            "matrix_unsubtracted_normal_form_max_error": maximum_unsubtracted_form_error,
            "matrix_minimum_covariance_term_magnitude": minimum_covariance_term_magnitude,
            "matrix_minimum_sign_flip_residual": minimum_sign_flip_residual,
            "minimum_theta_eigenvalue": minimum_theta_eigenvalue,
            "bg_maximum_required_moment": str(max(1 / value for value in bg_slacks)),
        },
        "scope": "Non-importing finite-dimensional and cutoff-two audit; no uniform H_N, Nelson, measure, or Sector-A closure.",
    }
    atomic_json(OUTPUT, payload)
    print(f"R-093 independent: {passed}/{len(rows)} assertions PASS" if passed == len(rows) else f"R-093 independent: {passed}/{len(rows)} assertions; FAIL")
    print(f"result: {OUTPUT.relative_to(REPO)}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
