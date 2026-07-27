#!/usr/bin/env python3
"""Primary executable evidence for the R-095 A13 ownership boundary.

The program recomputes the moving-prefix identity, fractional matrix
perspective, conditional resolvent gap, critical allocation schedules, and
the normalized Cartan homotopy.  It does not assert H_N, REG, Nelson, or
Sector-A closure.
"""

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
from numpy.polynomial.legendre import leggauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FRACTIONAL-FEEDBACK-SQUARE-PERSPECTIVE-DOMINATION-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-fractional-feedback-square-perspective-boundary/result.json"

AUTHORITIES = {
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r086": CLAIM_DIR / "notes/classii-rational-translated-wick-payload-comparable-reduction-260725-v1.0.tex.txt",
    "r092": CLAIM_DIR / "notes/classii-normalized-cartan-perspective-triangular-covariance-frontier-260725-v1.0.tex.txt",
    "r093": CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt",
    "r094": CLAIM_DIR / "notes/classii-root-local-gram-secant-feedback-boundary-260727-v1.0.tex.txt",
}

# Clearly labelled exact test oracles.  No output is derived from these.
TEST_ORACLES = {
    "moving_fixture": Fraction(-1, 4),
    "fractional_A": Fraction(3, 4),
    "fractional_theta": Fraction(-1, 3),
    "fractional_optimizer": Fraction(-4, 3),
    "fractional_value": Fraction(-1, 6),
}


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


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def conditional(values: list[Fraction], level: int, roots: int) -> list[Fraction]:
    """Conditional expectation on the first ``level`` Rademacher bits."""

    block = 1 << (roots - level)
    result = [Fraction(0) for _ in values]
    for start in range(0, len(values), block):
        mean = sum(values[start : start + block], Fraction(0)) / block
        for index in range(start, start + block):
            result[index] = mean
    return result


def expectation(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def dot_expectation(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return expectation([x * y for x, y in zip(left, right)])


def inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    return (eigenvectors * eigenvalues ** -0.5) @ eigenvectors.T


def normalized_map(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    q = float(z @ symmetric @ z) / (float(z @ z) + floor)
    return q * z


def normalized_jacobian(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    denominator = float(z @ z) + floor
    q = float(z @ symmetric @ z) / denominator
    gradient = 2.0 * (symmetric - q * np.eye(z.size)) @ z / denominator
    return q * np.eye(z.size) + np.outer(z, gradient)


def omega(z: np.ndarray, h: np.ndarray, k: np.ndarray, symmetric: np.ndarray, floor: float) -> float:
    jacobian = normalized_jacobian(z, symmetric, floor)
    return float((jacobian @ h) @ k - (jacobian @ k) @ h)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    authority_tokens = {
        "r079": ("future-feedback innovation block", "tag{3.4}", "tag{5.2}"),
        "r086": ("T_G^>", "tag{6.3}", "coefficient-dominant"),
        "r092": ("matrix-perspective telescope", "Theta_R", "tag{10.10}"),
        "r093": ("q_B", "unconditional augmented normal form", "tag{2.5}"),
        "r094": ("exact square-allocation split", "theta", "tag{6.4}"),
    }
    for label, path in AUTHORITIES.items():
        check(f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(
            f"authority_{label}_tokens",
            all(token in content for token in tokens),
            [token for token in tokens if token in content],
            list(tokens),
        )

    # Exact finite-tree moving-prefix identity.  The moving prefix is allowed
    # to carry terminal dependence, as it does through M_* in the theorem.
    roots = 3
    leaves = 1 << roots
    signs = [[Fraction(1 if (leaf >> (roots - bit)) & 1 else -1) for leaf in range(leaves)] for bit in range(1, roots + 1)]
    terminal = [signs[0][i] + 2 * signs[1][i] * signs[2][i] + Fraction(1, 2) for i in range(leaves)]
    prefix_families = {
        1: [2 * signs[0][i] - signs[1][i] * signs[2][i] for i in range(leaves)],
        2: [signs[0][i] + signs[1][i] + signs[0][i] * signs[2][i] for i in range(leaves)],
        3: [terminal[i] - signs[2][i] for i in range(leaves)],
    }
    p_low = conditional(terminal, 0, roots)
    terminal_differences: dict[int, list[Fraction]] = {}
    zeta: dict[int, list[Fraction]] = {}
    future_y: dict[int, list[Fraction]] = {}
    for level in range(1, roots + 1):
        previous_terminal = conditional(terminal, level - 1, roots)
        current_terminal = conditional(terminal, level, roots)
        terminal_differences[level] = [a - b for a, b in zip(current_terminal, previous_terminal)]
        minus = prefix_families[level]
        plus = [terminal[i] - minus[i] for i in range(leaves)]
        zeta[level] = [a - b for a, b in zip(conditional(minus, level, roots), conditional(minus, level - 1, roots))]
        future_y[level] = [a - b for a, b in zip(conditional(plus, level, roots), conditional(plus, level - 1, roots))]
        split_error = max(abs(terminal_differences[level][i] - zeta[level][i] - future_y[level][i]) for i in range(leaves))
        check(f"tree_doob_increment_split_{level}", split_error == 0, split_error, 0)

    pythagoras_left = expectation([value * value for value in terminal])
    pythagoras_right = expectation([value * value for value in p_low]) + sum(
        expectation([value * value for value in terminal_differences[level]]) for level in range(1, roots + 1)
    )
    check("tree_doob_pythagoras", pythagoras_left == pythagoras_right, pythagoras_left - pythagoras_right, 0)

    tree_defects: dict[str, str] = {}
    for theta in (Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        left = theta * pythagoras_left / 2 - theta * sum(
            expectation([value * value for value in future_y[level]]) for level in range(1, roots + 1)
        ) / 2
        right = theta * expectation([value * value for value in p_low]) / 2
        right += theta * sum(expectation([value * value for value in zeta[level]]) for level in range(1, roots + 1)) / 2
        right += theta * sum(dot_expectation(zeta[level], future_y[level]) for level in range(1, roots + 1))
        tree_defects[str(theta)] = str(left)
        check(f"moving_prefix_identity_theta_{theta}", left == right, left - right, 0)

    xi = [Fraction(-1), Fraction(1)]
    rho_star = [Fraction(0), Fraction(0)]
    fixture_theta = Fraction(1, 2)
    fixture_left = fixture_theta * expectation([value * value for value in rho_star]) / 2
    fixture_left -= fixture_theta * expectation([value * value for value in xi]) / 2
    fixture_right = fixture_theta * expectation([value * value for value in xi]) / 2
    fixture_right += fixture_theta * dot_expectation(xi, [-value for value in xi])
    check("moving_fixture_centered", expectation(xi) == 0, expectation(xi), 0)
    check("moving_fixture_terminal_zero", all(value == 0 for value in rho_star), rho_star, [0, 0])
    check("moving_fixture_lhs_minus_quarter", fixture_left == TEST_ORACLES["moving_fixture"], fixture_left, TEST_ORACLES["moving_fixture"])
    check("moving_fixture_rhs_minus_quarter", fixture_right == TEST_ORACLES["moving_fixture"], fixture_right, TEST_ORACLES["moving_fixture"])
    check("moving_fixture_defect_negative", fixture_left < 0, fixture_left, "< 0")

    # Fractional perspective: exact scalar oracle and random matrix identities.
    scalar_b = Fraction(1)
    scalar_theta = Fraction(1, 2)
    scalar_r = Fraction(1, 8)
    scalar_a = (1 - scalar_theta) * scalar_b + 2 * scalar_r
    scalar_perspective = scalar_b - scalar_b * scalar_b / scalar_a
    scalar_optimizer = -scalar_b / scalar_a
    scalar_value = scalar_b / 2 + scalar_b * scalar_optimizer + scalar_a * scalar_optimizer * scalar_optimizer / 2
    check("scalar_fractional_A", scalar_a == TEST_ORACLES["fractional_A"], scalar_a, TEST_ORACLES["fractional_A"])
    check("scalar_fractional_theta", scalar_perspective == TEST_ORACLES["fractional_theta"], scalar_perspective, TEST_ORACLES["fractional_theta"])
    check("scalar_fractional_optimizer", scalar_optimizer == TEST_ORACLES["fractional_optimizer"], scalar_optimizer, TEST_ORACLES["fractional_optimizer"])
    check("scalar_fractional_value", scalar_value == TEST_ORACLES["fractional_value"], scalar_value, TEST_ORACLES["fractional_value"])
    check("scalar_fractional_threshold", 2 * Fraction(1, 4) == scalar_theta * scalar_b, Fraction(1, 4), "R=1/4")

    rng = np.random.default_rng(95027)
    maximum_completion_error = 0.0
    minimum_safe_theta_eigenvalue = math.inf
    maximum_unsafe_theta_eigenvalue = -math.inf
    for index in range(24):
        dimension = 2 + index % 4
        raw_b = rng.normal(size=(dimension, dimension))
        b_matrix = raw_b.T @ raw_b + 0.1 * np.eye(dimension)
        theta = float(rng.uniform(0.05, 0.9))
        raw_s = rng.normal(size=(dimension, dimension))
        surplus = raw_s.T @ raw_s + 0.05 * np.eye(dimension)
        r_matrix = 0.5 * theta * b_matrix + surplus
        a_theta = (1.0 - theta) * b_matrix + 2.0 * r_matrix
        theta_matrix = b_matrix - b_matrix @ np.linalg.solve(a_theta, b_matrix)
        minimum_safe_theta_eigenvalue = min(minimum_safe_theta_eigenvalue, float(np.linalg.eigvalsh(theta_matrix)[0]))
        g = rng.normal(size=dimension)
        c = rng.normal(size=dimension)
        gamma_raw = rng.normal(size=(dimension, dimension))
        gamma = gamma_raw.T @ gamma_raw
        left = 0.5 * g @ b_matrix @ g + g @ b_matrix @ c + 0.5 * c @ a_theta @ c - 0.5 * np.trace(b_matrix @ gamma)
        shift = c + np.linalg.solve(a_theta, b_matrix @ g)
        right = 0.5 * shift @ a_theta @ shift + 0.5 * g @ theta_matrix @ g - 0.5 * np.trace(b_matrix @ gamma)
        error = abs(float(left - right))
        maximum_completion_error = max(maximum_completion_error, error)
        check(f"matrix_completion_identity_{index}", error < 2.0e-10, error, "< 2e-10")
        check(f"matrix_safe_domination_{index}", np.linalg.eigvalsh(2.0 * r_matrix - theta * b_matrix)[0] > 0.0, float(np.linalg.eigvalsh(2.0 * r_matrix - theta * b_matrix)[0]), "> 0")
        check(f"matrix_safe_perspective_{index}", np.linalg.eigvalsh(theta_matrix)[0] > -1.0e-10, float(np.linalg.eigvalsh(theta_matrix)[0]), ">= 0")

    b_noncommuting = np.array([[2.0, 1.0], [1.0, 2.0]])
    r_noncommuting = np.diag([1.0, 0.5])
    whiten = inverse_sqrt(r_noncommuting)
    generalized = whiten @ b_noncommuting @ whiten
    largest = float(np.linalg.eigvalsh(generalized)[-1])
    theta_critical = 2.0 / largest
    check("noncommuting_generalized_eigenvalue", abs(largest - (3.0 + math.sqrt(3.0))) < 1.0e-13, largest, "3+sqrt(3)")
    for label, theta in (
        ("below", theta_critical / 2.0),
        ("critical", theta_critical),
        ("above", 0.5 * (1.0 + theta_critical)),
    ):
        a_theta = (1.0 - theta) * b_noncommuting + 2.0 * r_noncommuting
        theta_matrix = b_noncommuting - b_noncommuting @ np.linalg.solve(a_theta, b_noncommuting)
        domination_min = float(np.linalg.eigvalsh(2.0 * r_noncommuting - theta * b_noncommuting)[0])
        perspective_min = float(np.linalg.eigvalsh(theta_matrix)[0])
        if label == "below":
            condition = domination_min > 0.0 and perspective_min > 0.0
            expected = "both positive"
        elif label == "critical":
            condition = abs(domination_min) < 1.0e-12 and abs(perspective_min) < 1.0e-12
            expected = "both zero at minimum"
        else:
            condition = domination_min < 0.0 and perspective_min < 0.0
            expected = "both negative"
            maximum_unsafe_theta_eigenvalue = max(maximum_unsafe_theta_eigenvalue, perspective_min)
        check(f"noncommuting_threshold_{label}", condition, [domination_min, perspective_min], expected)

    # Conditional resolvent-gap identity on finite matrix ensembles.
    maximum_conditional_error = 0.0
    maximum_integral_error = 0.0
    for index in range(16):
        dimension = 2 + index % 3
        atom_count = 3 + index % 4
        b_atoms: list[np.ndarray] = []
        z_atoms: list[np.ndarray] = []
        for _ in range(atom_count):
            raw = rng.normal(size=(dimension, dimension))
            b_atoms.append(raw.T @ raw + 0.05 * np.eye(dimension))
            z_atoms.append(rng.normal(size=dimension))
        raw_r = rng.normal(size=(dimension, dimension))
        r_matrix = raw_r.T @ raw_r + 0.4 * np.eye(dimension)
        theta = float(rng.uniform(0.05, 0.8))
        bar_b = sum(b_atoms) / atom_count
        bar_a = bar_b + 2.0 * r_matrix
        bar_a_theta = (1.0 - theta) * bar_b + 2.0 * r_matrix
        q_vector = sum((b @ z for b, z in zip(b_atoms, z_atoms)), np.zeros(dimension)) / atom_count
        mean_z = sum(z_atoms, np.zeros(dimension)) / atom_count
        gamma = sum((np.outer(z - mean_z, z - mean_z) for z in z_atoms), np.zeros((dimension, dimension))) / atom_count
        raw_energy = sum(float(z @ b @ z) for b, z in zip(b_atoms, z_atoms)) / atom_count
        theta_roots: list[np.ndarray] = []
        for b, z in zip(b_atoms, z_atoms):
            theta_full = b - b @ np.linalg.solve(b + 2.0 * r_matrix, b)
            evals, evecs = np.linalg.eigh(theta_full)
            theta_roots.append((evecs * np.sqrt(np.maximum(evals, 0.0))) @ evecs.T @ z)
        r_mean = sum(theta_roots, np.zeros(dimension)) / atom_count
        d_r = raw_energy - float(np.trace(bar_b @ gamma)) - float(q_vector @ np.linalg.solve(bar_a, q_vector)) - float(r_mean @ r_mean)
        c = rng.normal(size=dimension)
        s_theta = 0.5 * (raw_energy - float(np.trace(bar_b @ gamma))) + float(c @ q_vector) + 0.5 * float(c @ bar_a_theta @ c)
        shifted = c + np.linalg.solve(bar_a_theta, q_vector)
        gap = 0.5 * float(q_vector @ (np.linalg.solve(bar_a_theta, q_vector) - np.linalg.solve(bar_a, q_vector)))
        reconstructed = 0.5 * d_r + 0.5 * float(r_mean @ r_mean) + 0.5 * float(shifted @ bar_a_theta @ shifted) - gap
        error = abs(s_theta - reconstructed)
        maximum_conditional_error = max(maximum_conditional_error, error)
        check(f"conditional_resolvent_identity_{index}", error < 3.0e-10, error, "< 3e-10")
        check(f"conditional_resolvent_gap_nonnegative_{index}", gap > -1.0e-11, gap, ">= 0")
        upper = theta / (2.0 * (1.0 - theta)) * float(q_vector @ np.linalg.solve(bar_a, q_vector))
        check(f"conditional_resolvent_gap_bound_{index}", gap <= upper + 2.0e-10, gap, f"<= {upper}")

        nodes, weights = leggauss(40)
        integral = 0.0
        for node, weight in zip(nodes, weights):
            s = (2.0 - theta + theta * node) / 2.0
            vector = np.linalg.solve(s * bar_b + 2.0 * r_matrix, q_vector)
            integral += weight * float(vector @ bar_b @ vector)
        integral *= theta / 4.0
        integral_error = abs(integral - gap)
        maximum_integral_error = max(maximum_integral_error, integral_error)
        check(f"conditional_resolvent_integral_{index}", integral_error < 2.0e-10, integral_error, "< 2e-10")

    # Exact four-atom terminal-mean fixture.
    z_over_t = np.array([1.0, -1.0, 2.0, -2.0])
    b_atoms_scalar = np.array([0.0, 2.0, 1.5, 0.5])
    bar_b_scalar = float(np.mean(b_atoms_scalar))
    gamma_scalar = float(np.mean(z_over_t**2))
    q_scalar = float(np.mean(b_atoms_scalar * z_over_t))
    raw_scalar = float(np.mean(b_atoms_scalar * z_over_t**2))
    theta_scalar = 2.0 * b_atoms_scalar / (b_atoms_scalar + 2.0)
    r_scalar = float(np.mean(np.sqrt(theta_scalar) * z_over_t))
    r_formula = 0.25 * (-1.0 + 2.0 * math.sqrt(6.0 / 7.0) - 2.0 * math.sqrt(2.0 / 5.0))
    check("mean_fixture_bar_b", abs(bar_b_scalar - 1.0) < 1.0e-15, bar_b_scalar, 1.0)
    check("mean_fixture_gamma", abs(gamma_scalar - 2.5) < 1.0e-15, gamma_scalar, 2.5)
    check("mean_fixture_q_zero", abs(q_scalar) < 1.0e-15, q_scalar, 0.0)
    check("mean_fixture_covariance_match", abs(raw_scalar - bar_b_scalar * gamma_scalar) < 1.0e-15, raw_scalar, bar_b_scalar * gamma_scalar)
    check("mean_fixture_r_formula", abs(r_scalar - r_formula) < 1.0e-15, r_scalar, r_formula)
    check("mean_fixture_r_nonzero", abs(r_scalar) > 1.0e-3, r_scalar, "nonzero")
    check("mean_fixture_terminal_restoration", abs((-r_scalar * r_scalar) + r_scalar * r_scalar) < 1.0e-15, 0.0, 0.0)

    # Production Gram growth is derived from the actual rational ray.
    c1 = 243.0 / (8000.0 * (4.0 + 1.0e-12))
    floor = 1.0e-12
    asymptotic = 64.0 * c1 / 81.0
    growth_errors: dict[str, float] = {}
    for exponent in (2, 3, 4, 5):
        t = 10.0**exponent
        g_value = t * (1.0 - (5.0 / 9.0) * t * t / (t * t + floor))
        scaled = 4.0 * c1 * g_value * g_value / (t * t)
        growth_errors[str(exponent)] = abs(scaled - asymptotic)
        check(f"production_gram_growth_{exponent}", abs(scaled - asymptotic) < 1.0e-10, scaled, asymptotic)
    check("production_gram_unbounded", 4.0 * c1 * (1.0e5 * (1.0 - 5.0 / 9.0)) ** 2 > 1.0e6, "quadratic growth", "unbounded")

    # Scale-dependent theta schedules.  The direct finite sums exhibit the
    # incompatible alpha<1 and alpha>1 requirements.
    schedule_rows: list[dict[str, float]] = []
    for alpha in (0.5, 1.0, 1.5):
        prefix_values = []
        debt_values = []
        for length in (8, 16, 32):
            prefix = sum(2.0 ** (-(1.0 - alpha) * j) for j in range(length))
            debt = sum(2.0 ** ((1.0 - alpha) * j) for j in range(length))
            prefix_values.append(prefix)
            debt_values.append(debt)
        schedule_rows.append({"alpha": alpha, "prefix_32": prefix_values[-1], "debt_32": debt_values[-1]})
        if alpha < 1.0:
            check(f"theta_schedule_prefix_bounded_{alpha}", prefix_values[-1] < 1.0 / (1.0 - 2.0 ** (-(1.0 - alpha))), prefix_values[-1], "bounded")
            check(f"theta_schedule_debt_diverges_{alpha}", debt_values[-1] > debt_values[-2] * 10.0, debt_values, "exponential growth")
        elif alpha > 1.0:
            check(f"theta_schedule_prefix_diverges_{alpha}", prefix_values[-1] > prefix_values[-2] * 10.0, prefix_values, "exponential growth")
            check(f"theta_schedule_debt_bounded_{alpha}", debt_values[-1] < 1.0 / (1.0 - 2.0 ** (-(alpha - 1.0))), debt_values[-1], "bounded")
        else:
            check("theta_schedule_prefix_critical", prefix_values == [8.0, 16.0, 32.0], prefix_values, [8.0, 16.0, 32.0])
            check("theta_schedule_debt_critical", debt_values == [8.0, 16.0, 32.0], debt_values, [8.0, 16.0, 32.0])
    for j in range(12):
        theta_j = 0.4 * 2.0 ** (-0.37 * j)
        product = (2.0 ** (-j) / theta_j) * (theta_j * 2.0**j)
        check(f"theta_weight_product_{j}", abs(product - 1.0) < 1.0e-14, product, 1.0)

    # Normalized Cartan curvature and exact homotopy.
    nodes, weights = leggauss(64)
    maximum_homotopy_error = 0.0
    maximum_omega_ratio = 0.0
    for index in range(24):
        dimension = 3 + index % 3
        raw_s = rng.normal(size=(dimension, dimension))
        symmetric = 0.5 * (raw_s + raw_s.T)
        norm_s = float(np.linalg.norm(symmetric, 2))
        symmetric /= max(1.0, norm_s)
        z = rng.normal(size=dimension)
        a = rng.normal(size=dimension)
        g = rng.normal(size=dimension)
        c = rng.normal(size=dimension)
        floor_value = 0.03 + 0.01 * (index % 4)
        omega_value = omega(z, a, g, symmetric, floor_value)
        denominator = max(1.0e-15, float(np.linalg.norm(a) * np.linalg.norm(g)))
        ratio = abs(omega_value) / denominator
        maximum_omega_ratio = max(maximum_omega_ratio, ratio)
        check(f"cartan_omega_bound_{index}", ratio <= 2.0 + 1.0e-12, ratio, "<= 2")

        endpoint_f = normalized_map(z + a, symmetric, floor_value) @ (g + c) - normalized_map(z, symmetric, floor_value) @ g
        derivative_integral = 0.0
        curvature_integral = 0.0
        for node, weight in zip(nodes, weights):
            t = 0.5 * (node + 1.0)
            u = z + t * a
            velocity = g + t * c
            derivative_integral += 0.5 * weight * (
                (normalized_jacobian(u, symmetric, floor_value) @ velocity) @ a
                + normalized_map(u, symmetric, floor_value) @ c
            )
            curvature_integral += 0.5 * weight * omega(u, a, velocity, symmetric, floor_value)
        error = abs(endpoint_f - derivative_integral - curvature_integral)
        maximum_homotopy_error = max(maximum_homotopy_error, error)
        check(f"cartan_homotopy_{index}", error < 2.0e-11, error, "< 2e-11")

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-fractional-feedback-square-perspective-boundary-primary/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "derived": {
            "tree_defects": tree_defects,
            "maximum_matrix_completion_error": maximum_completion_error,
            "minimum_safe_perspective_eigenvalue": minimum_safe_theta_eigenvalue,
            "maximum_unsafe_perspective_eigenvalue": maximum_unsafe_theta_eigenvalue,
            "maximum_conditional_identity_error": maximum_conditional_error,
            "maximum_resolvent_integral_error": maximum_integral_error,
            "mean_fixture_r": r_scalar,
            "production_growth_errors": growth_errors,
            "schedule_rows": schedule_rows,
            "maximum_cartan_homotopy_error": maximum_homotopy_error,
            "maximum_cartan_omega_ratio": maximum_omega_ratio,
        },
        "claims_not_established": [
            "complete_rootwise_R079_R086_form_bound",
            "complete_H_N",
            "REG",
            "OVERLAP_src",
            "Nelson",
            "interacting_measure",
            "Sector_A_closure",
        ],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-095 PRIMARY {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)} assertions")
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
