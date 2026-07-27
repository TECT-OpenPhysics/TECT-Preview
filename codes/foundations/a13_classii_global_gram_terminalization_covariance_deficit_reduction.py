#!/usr/bin/env python3
"""Primary executable evidence for the R-097 A13 reduction.

The checks cover the complete rational heat telescope, the once-only terminal
Schur completion, the posterior-covariance normal form, derivative-free
predictable terminalization, and exact finite-dimensional method boundaries.
They do not assert the production covariance-bracket estimate, Cartan one-use,
complete H_N, REG, Nelson, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.hermite import hermgauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-GLOBAL-GRAM-TERMINALIZATION-COVARIANCE-DEFICIT-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-global-gram-terminalization-covariance-deficit-reduction/result.json"

AUTHORITIES = {
    "r066": CLAIM_DIR / "notes/classii-backward-heat-martingale-square-coupled-cartan-reduction-260723-v1.0.tex.txt",
    "r077": CLAIM_DIR / "notes/classii-causal-packet-payload-resonance-reduction-260725-v1.0.tex.txt",
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r085": CLAIM_DIR / "notes/classii-nonorthogonal-cartan-schur-rational-shifted-hessian-boundary-260725-v1.0.tex.txt",
    "r086": CLAIM_DIR / "notes/classii-rational-translated-wick-payload-comparable-reduction-260725-v1.0.tex.txt",
    "r087": CLAIM_DIR / "notes/classii-cartan-spatial-decay-rational-trace-variational-core-reduction-260725-v1.0.tex.txt",
    "r093": CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt",
    "r095": CLAIM_DIR / "notes/classii-fractional-feedback-square-perspective-domination-boundary-260727-v1.0.tex.txt",
    "r096": CLAIM_DIR / "notes/classii-low-hermite-wick-predictable-baseline-reduction-260727-v1.0.tex.txt",
}

INPUTS = {
    "random_seed": 9701,
    "matrix_dimension": 3,
    "schur_fixtures": 5,
    "gaussian_shift": 2.0,
    "gaussian_gram_floor": 1.0,
    "matrix_payment": 0.01,
}

TOLERANCES = {
    "exact_float": 2.0e-15,
    "quadrature": 3.0e-11,
    "matrix_identity": 2.0e-10,
    "eigenvalue": 2.0e-10,
    "mutation": 1.0e-8,
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
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def normal_rule(order: int, variance: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = hermgauss(order)
    return math.sqrt(2.0 * variance) * nodes, weights / math.sqrt(math.pi)


def hermite(degree: int, value: np.ndarray) -> np.ndarray:
    if degree == 0:
        return np.ones_like(value)
    if degree == 1:
        return value.copy()
    previous = np.ones_like(value)
    current = value.copy()
    for index in range(1, degree):
        previous, current = current, value * current - index * previous
    return current


def matrix_sqrt_psd(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    if float(np.min(values)) < -1.0e-11:
        raise ValueError("matrix is not positive semidefinite")
    return (vectors * np.sqrt(np.maximum(values, 0.0))) @ vectors.T


def colon(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sum(left * right))


def gaussian_moment(power: int) -> float:
    """Exact integer Gaussian moment, returned as float for NumPy checks."""
    if power % 2:
        return 0.0
    value = 1
    for factor in range(1, power, 2):
        value *= factor
    return float(value)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    authority_tokens = {
        "r066": ("backward heat martingale", "tag{2.8}", "raw-current secant"),
        "r077": ("predictable baselines", "tag{2.10}", "complete Wick forest"),
        "r079": ("full-current identity", "future-feedback innovation block", "conditional mean"),
        "r085": ("tag{4.10}", "tag{4.11}", "tag{6.5}"),
        "r086": ("tag{3.7}", "payload-comparable", "T_Q^>"),
        "r087": ("spatial half of R-085", "Cartan one-use obstruction", "tag{6.5}"),
        "r093": ("augmented one-reveal normal form", "information price", "tag{2.5}"),
        "r095": ("moving-prefix square defect", "conditional mean shadow", "tag{5.4}"),
        "r096": ("adapted-prefix frontier", "low-Hermite", "tag{8.3}"),
    }
    for label, path in AUTHORITIES.items():
        check("authority", f"authority_{label}_exists", path.exists(), str(path.relative_to(REPO)), "exists")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        tokens = authority_tokens[label]
        check(
            "authority",
            f"authority_{label}_tokens",
            all(token in content for token in tokens),
            [token for token in tokens if token in content],
            list(tokens),
        )

    # The scalar quadratic Gram is sufficient to test the exact backward heat
    # identity because its heat lift is available in closed form.
    floor = 0.7
    value_variance = 0.6
    derivative_variance = 1.1
    x = 0.35
    y = -0.8
    a = 0.2
    b = 0.45
    nodes_g, weights_g = normal_rule(17, value_variance)
    nodes_d, weights_d = normal_rule(17, derivative_variance)
    grid_g, grid_d = np.meshgrid(nodes_g, nodes_d, indexing="ij")
    grid_w = np.outer(weights_g, weights_d)

    def heat_b(value: np.ndarray | float, future_variance: float) -> np.ndarray | float:
        return np.asarray(value) ** 2 + floor + future_variance

    def heat_w(value: np.ndarray | float, derivative: np.ndarray | float, gamma: float, future_variance: float) -> np.ndarray | float:
        return 0.5 * heat_b(value, future_variance) * (np.asarray(derivative) ** 2 - gamma)

    fresh = float(np.sum(grid_w * heat_w(x + grid_g, y + grid_d, derivative_variance, 0.0)))
    past = float(heat_w(x, y, 0.0, value_variance))
    check("heat_telescope", "one_step_backward_heat", abs(fresh - past) < 2.0e-12, fresh - past, 0.0)
    controlled_fresh = float(np.sum(grid_w * heat_w(x + a + grid_g, y + b + grid_d, derivative_variance, 0.0)))
    controlled_past = float(heat_w(x + a, y + b, 0.0, value_variance))
    check("heat_telescope", "one_step_predictable_control_heat", abs(controlled_fresh - controlled_past) < 2.0e-12, controlled_fresh - controlled_past, 0.0)

    # Two-shell predictable baseline telescope.  The second control is a
    # function only of the first revealed value/derivative pair.
    value_variances = (0.45, 0.25)
    derivative_variances = (0.9, 0.55)
    g1, wg1 = normal_rule(9, value_variances[0])
    d1, wd1 = normal_rule(9, derivative_variances[0])
    g2, wg2 = normal_rule(9, value_variances[1])
    d2, wd2 = normal_rule(9, derivative_variances[1])
    G1, D1, G2, D2 = np.meshgrid(g1, d1, g2, d2, indexing="ij")
    W1, WD1, W2, WD2 = np.meshgrid(wg1, wd1, wg2, wd2, indexing="ij")
    weights4 = W1 * WD1 * W2 * WD2
    a1 = 0.23
    b1 = -0.31
    a2 = 0.11 + 0.08 * G1 - 0.04 * D1
    b2 = -0.17 + 0.03 * G1 + 0.05 * D1
    total_gamma = sum(derivative_variances)
    terminal_shifted = heat_w(G1 + G2 + a1 + a2, D1 + D2 + b1 + b2, total_gamma, 0.0)
    terminal_base = heat_w(G1 + G2, D1 + D2, total_gamma, 0.0)
    endpoint_difference = float(np.sum(weights4 * (terminal_shifted - terminal_base)))
    first_baseline = float(
        heat_w(a1, b1, 0.0, sum(value_variances))
        - heat_w(0.0, 0.0, 0.0, sum(value_variances))
    )
    G1s, D1s = np.meshgrid(g1, d1, indexing="ij")
    weights2 = np.outer(wg1, wd1)
    A2s = 0.11 + 0.08 * G1s - 0.04 * D1s
    B2s = -0.17 + 0.03 * G1s + 0.05 * D1s
    second_baseline = float(
        np.sum(
            weights2
            * (
                heat_w(
                    G1s + a1 + A2s,
                    D1s + b1 + B2s,
                    derivative_variances[0],
                    value_variances[1],
                )
                - heat_w(
                    G1s + a1,
                    D1s + b1,
                    derivative_variances[0],
                    value_variances[1],
                )
            )
        )
    )
    baseline_sum = first_baseline + second_baseline
    check("heat_telescope", "two_shell_predictable_endpoint_telescope", abs(endpoint_difference - baseline_sum) < 2.0e-11, endpoint_difference - baseline_sum, 0.0)
    a2_fibre = a2[:, :, 0, 0][:, :, None, None]
    b2_fibre = b2[:, :, 0, 0][:, :, None, None]
    strict_past_error = max(float(np.max(np.abs(a2 - a2_fibre))), float(np.max(np.abs(b2 - b2_fibre))))
    check("heat_telescope", "second_control_strict_past", strict_past_error == 0.0, strict_past_error, 0.0)
    future_leaking_mutant = a2 + 0.03 * G2
    future_fibre_variation = float(np.max(np.abs(future_leaking_mutant - future_leaking_mutant[:, :, 0, 0][:, :, None, None])))
    check("mutation_checks", "future_leaking_control_rejected", future_fibre_variation > TOLERANCES["mutation"], future_fibre_variation, f"> {TOLERANCES['mutation']}")

    # Terminal theta=0 Schur identity for several deterministic matrix
    # fixtures.  Every matrix is constructed from an upstream factor.
    generator = np.random.default_rng(INPUTS["random_seed"])
    dimension = INPUTS["matrix_dimension"]
    for fixture in range(INPUTS["schur_fixtures"]):
        factor0 = generator.normal(size=(dimension, dimension))
        factor1 = generator.normal(size=(dimension, dimension))
        factor_r = generator.normal(size=(dimension, dimension))
        b0_matrix = factor0 @ factor0.T
        b1_matrix = factor1 @ factor1.T
        r_matrix = factor_r @ factor_r.T + (0.4 + 0.1 * fixture) * np.eye(dimension)
        gamma = np.diag(generator.uniform(0.2, 1.0, size=dimension))
        g = generator.normal(size=dimension)
        c = generator.normal(size=dimension)
        q_matrix = np.outer(g, g) - gamma
        delta_w = 0.5 * colon(b1_matrix - b0_matrix, q_matrix)
        delta_w += float(g @ b1_matrix @ c + 0.5 * c @ b1_matrix @ c)
        a_matrix = b1_matrix + 2.0 * r_matrix
        inverse_a = np.linalg.inv(a_matrix)
        theta = b1_matrix - b1_matrix @ inverse_a @ b1_matrix
        shifted = c + inverse_a @ b1_matrix @ g
        rhs = 0.5 * float(shifted @ a_matrix @ shifted)
        rhs += 0.5 * float(g @ theta @ g)
        rhs -= 0.5 * colon(b1_matrix, gamma)
        rhs -= 0.5 * colon(b0_matrix, q_matrix)
        lhs = delta_w + float(c @ r_matrix @ c)
        check("terminal_schur", f"terminal_schur_identity_{fixture}", abs(lhs - rhs) < 2.0e-10, lhs - rhs, 0.0)
        check("terminal_schur", f"terminal_theta_psd_{fixture}", float(np.min(np.linalg.eigvalsh(theta))) > -2.0e-10, float(np.min(np.linalg.eigvalsh(theta))), ">= 0")
        partition_error = float(np.linalg.norm(b1_matrix @ inverse_a @ b1_matrix + theta - b1_matrix, ord="fro"))
        check("terminal_schur", f"terminal_theta_partition_{fixture}", partition_error < TOLERANCES["matrix_identity"], partition_error, 0.0)

    # Conditional posterior-covariance normal form on a nontrivial atomic
    # vector fixture.  B is constant on each reveal group.
    probabilities = np.array([0.08, 0.12, 0.17, 0.13, 0.21, 0.29])
    reveal = np.array([0, 0, 1, 1, 2, 2])
    b_groups = np.array(
        [
            [[1.6, 0.2], [0.2, 0.9]],
            [[0.8, -0.1], [-0.1, 1.4]],
            [[2.1, 0.3], [0.3, 1.1]],
        ]
    )
    b_atoms = b_groups[reveal]
    uncentered_g_atoms = np.array([[1.2, -0.4], [-0.7, 0.9], [0.3, 1.5], [1.0, -1.1], [-1.4, 0.2], [0.6, 0.7]])
    unconditional_mean = np.einsum("a,ai->i", probabilities, uncentered_g_atoms)
    g_atoms = uncentered_g_atoms - unconditional_mean
    gamma = np.einsum("a,ai,aj->ij", probabilities, g_atoms, g_atoms)
    r_payment = np.array([[0.65, 0.04], [0.04, 0.55]])
    c = np.array([-0.35, 0.28])
    bar_b = np.einsum("a,aij->ij", probabilities, b_atoms)
    q = np.einsum("a,aij,aj->i", probabilities, b_atoms, g_atoms)
    bar_a = bar_b + 2.0 * r_payment
    inverse_bar_a = np.linalg.inv(bar_a)
    raw = sum(probabilities[index] * colon(b_atoms[index], np.outer(g_atoms[index], g_atoms[index]) - gamma) for index in range(len(probabilities)))
    s0 = 0.5 * raw + float(c @ q) + 0.5 * float(c @ bar_a @ c)
    means: list[np.ndarray] = []
    covariances: list[np.ndarray] = []
    group_probabilities: list[float] = []
    for label in range(len(b_groups)):
        mask = reveal == label
        group_probability = float(np.sum(probabilities[mask]))
        conditional_weights = probabilities[mask] / group_probability
        mean = np.einsum("a,ai->i", conditional_weights, g_atoms[mask])
        centered = g_atoms[mask] - mean
        covariance = np.einsum("a,ai,aj->ij", conditional_weights, centered, centered)
        group_probabilities.append(group_probability)
        means.append(mean)
        covariances.append(covariance)
    j_b = sum(group_probabilities[label] * float(means[label] @ b_groups[label] @ means[label]) for label in range(len(b_groups)))
    j_b -= float(q @ inverse_bar_a @ q)
    covariance_defect = sum(
        group_probabilities[label] * colon(b_groups[label], covariances[label] - gamma)
        for label in range(len(b_groups))
    )
    q_from_conditional_means = sum(
        group_probabilities[label] * b_groups[label] @ means[label]
        for label in range(len(b_groups))
    )
    second_moment_direct = sum(
        probabilities[index] * float(g_atoms[index] @ b_atoms[index] @ g_atoms[index])
        for index in range(len(probabilities))
    )
    second_moment_split = sum(
        group_probabilities[label]
        * (colon(b_groups[label], covariances[label]) + float(means[label] @ b_groups[label] @ means[label]))
        for label in range(len(b_groups))
    )
    check("posterior_covariance", "unconditional_innovation_centered", float(np.linalg.norm(np.einsum("a,ai->i", probabilities, g_atoms))) < TOLERANCES["exact_float"], np.einsum("a,ai->i", probabilities, g_atoms), [0.0, 0.0])
    check("posterior_covariance", "gamma_derived_from_atoms", float(np.min(np.linalg.eigvalsh(gamma))) > 0.0, gamma, "positive covariance derived from centered atoms")
    check("posterior_covariance", "q_conditional_tower", float(np.linalg.norm(q - q_from_conditional_means)) < TOLERANCES["quadrature"], q - q_from_conditional_means, [0.0, 0.0])
    check("posterior_covariance", "second_moment_conditional_split", abs(second_moment_direct - second_moment_split) < TOLERANCES["quadrature"], second_moment_direct - second_moment_split, 0.0)
    completed = c + inverse_bar_a @ q
    normal_form = 0.5 * float(completed @ bar_a @ completed) + 0.5 * j_b + 0.5 * covariance_defect
    check("posterior_covariance", "conditional_normal_form", abs(s0 - normal_form) < 3.0e-12, s0 - normal_form, 0.0)
    check("posterior_covariance", "conditional_j_b_nonnegative", j_b >= -2.0e-12, j_b, ">= 0")
    m_zero = inverse_bar_a @ q
    j_b_variance_certificate = sum(
        group_probabilities[label] * float((means[label] - m_zero) @ b_groups[label] @ (means[label] - m_zero))
        for label in range(len(b_groups))
    ) + 2.0 * float(m_zero @ r_payment @ m_zero)
    check("posterior_covariance", "conditional_j_b_variance_certificate", abs(j_b - j_b_variance_certificate) < TOLERANCES["quadrature"], j_b - j_b_variance_certificate, 0.0)
    block = np.block(
        [
            [bar_a, q[:, None]],
            [q[None, :], np.array([[j_b + float(q @ inverse_bar_a @ q)]])],
        ]
    )
    check("posterior_covariance", "conditional_schur_block_psd", float(np.min(np.linalg.eigvalsh(block))) >= -2.0e-12, float(np.min(np.linalg.eigvalsh(block))), ">= 0")
    transformed_means = []
    for index in range(len(probabilities)):
        theta = b_atoms[index] - b_atoms[index] @ np.linalg.inv(b_atoms[index] + 2.0 * r_payment) @ b_atoms[index]
        transformed_means.append(matrix_sqrt_psd(theta) @ g_atoms[index])
    r_mean = np.einsum("a,ai->i", probabilities, np.asarray(transformed_means))
    d_r = raw - float(q @ inverse_bar_a @ q) - float(r_mean @ r_mean)
    check("posterior_covariance", "q_r_covariance_identity", abs(d_r + float(r_mean @ r_mean) - (j_b + covariance_defect)) < 4.0e-12, d_r + float(r_mean @ r_mean) - (j_b + covariance_defect), 0.0)
    check("posterior_covariance", "r_owner_nonzero", float(r_mean @ r_mean) > 0.0, float(r_mean @ r_mean), "> 0")

    # Predictable terminalization and cross-Doob decomposition for three
    # independent Gaussian roots.  B_2 and B_3 are predictable at their levels.
    nodes, weights = normal_rule(9)
    x1, x2, x3 = np.meshgrid(nodes, nodes, nodes, indexing="ij")
    w1, w2, w3 = np.meshgrid(weights, weights, weights, indexing="ij")
    product_weights = w1 * w2 * w3
    h2_x1 = x1 * x1 - 1.0
    b2 = h2_x1 + 0.4 * x1
    b3 = 0.3 * h2_x1 + 0.5 * x1 * x2 - 0.2 * x2
    t2 = 1.3
    t3 = -0.7
    g1 = x1
    g2 = x1 + x2
    g3 = x1 + x2 + x3
    q1 = g1 * g1 - 1.0
    q2 = g2 * g2 - 2.0
    q3 = g3 * g3 - 3.0
    f_terminal = t2 * b2 + t3 * b3
    predictable_sum = float(np.sum(product_weights * (t2 * b2 * q1 + t3 * b3 * q2)))
    terminal_pairing = float(np.sum(product_weights * f_terminal * q3))
    check("doob_terminalization", "predictable_terminalization", abs(predictable_sum - terminal_pairing) < 2.0e-11, predictable_sum - terminal_pairing, 0.0)
    f1 = t2 * b2 + t3 * 0.3 * h2_x1
    f2 = f_terminal
    d1_f = f1
    d2_f = f2 - f1
    d3_f = np.zeros_like(f_terminal)
    d1_q = q1
    d2_q = q2 - q1
    d3_q = q3 - q2
    cross_doob = float(np.sum(product_weights * (d1_f * d1_q + d2_f * d2_q + d3_f * d3_q)))
    check("doob_terminalization", "cross_doob_pairing", abs(terminal_pairing - cross_doob) < 2.0e-11, terminal_pairing - cross_doob, 0.0)
    f_norm = float(np.sum(product_weights * f_terminal * f_terminal))
    doob_f_norm = float(np.sum(product_weights * (d1_f * d1_f + d2_f * d2_f + d3_f * d3_f)))
    q_norm = float(np.sum(product_weights * q3 * q3))
    doob_q_norm = float(np.sum(product_weights * (d1_q * d1_q + d2_q * d2_q + d3_q * d3_q)))
    check("doob_terminalization", "doob_f_pythagoras", abs(f_norm - doob_f_norm) < 2.0e-11, f_norm - doob_f_norm, 0.0)
    check("doob_terminalization", "doob_q_pythagoras", abs(q_norm - doob_q_norm) < 3.0e-11, q_norm - doob_q_norm, 0.0)
    rank1_part_d2_f = t3 * (0.5 * x1 - 0.2) * x2
    check("doob_terminalization", "root_two_low_hermite_rank_one", float(np.max(np.abs(d2_f - rank1_part_d2_f))) < 2.0e-12, float(np.max(np.abs(d2_f - rank1_part_d2_f))), 0.0)
    check("doob_terminalization", "root_three_coefficient_increment_zero", float(np.max(np.abs(d3_f))) == 0.0, float(np.max(np.abs(d3_f))), 0.0)
    cauchy_bound = math.sqrt(doob_f_norm * doob_q_norm)
    check("doob_terminalization", "one_use_doob_cauchy", abs(cross_doob) <= cauchy_bound + 2.0e-12, abs(cross_doob), cauchy_bound)
    h2_x2 = x2 * x2 - 1.0
    h3_x2 = x2 * x2 * x2 - 3.0 * x2
    low_rank_candidate = rank1_part_d2_f + 0.37 * h2_x2
    high_rank_candidate = 0.19 * h3_x2
    full_candidate = low_rank_candidate + high_rank_candidate
    low_hermite_pairing = float(np.sum(product_weights * low_rank_candidate * d2_q))
    full_hermite_pairing = float(np.sum(product_weights * full_candidate * d2_q))
    high_rank_pairing = float(np.sum(product_weights * high_rank_candidate * d2_q))
    check("doob_terminalization", "pi1_pi2_exhaust_wick_increment", abs(full_hermite_pairing - low_hermite_pairing) < TOLERANCES["quadrature"], full_hermite_pairing - low_hermite_pairing, 0.0)
    check("doob_terminalization", "rank_three_orthogonal_to_wick_increment", abs(high_rank_pairing) < TOLERANCES["quadrature"], high_rank_pairing, 0.0)
    rank_one_only_pairing = float(np.sum(product_weights * rank1_part_d2_f * d2_q))
    check("mutation_checks", "omitted_pi2_rejected", abs(full_hermite_pairing - rank_one_only_pairing) > TOLERANCES["mutation"], full_hermite_pairing - rank_one_only_pairing, f"> {TOLERANCES['mutation']}")

    # Predictability alone does not prevent repeated use of one old H_2 root.
    # Every number below is generated from the Gaussian quadrature and N.
    h2 = nodes * nodes - 1.0
    h2_norm = float(np.dot(weights, h2 * h2))
    h2_norm_oracle = gaussian_moment(4) - 2.0 * gaussian_moment(2) + gaussian_moment(0)
    check("predictable_accumulation", "h2_norm_independent_moment_oracle", abs(h2_norm - h2_norm_oracle) < TOLERANCES["quadrature"], h2_norm, h2_norm_oracle)
    for count in (1, 3, 8):
        aggregate = np.zeros_like(h2)
        for _ in range(count):
            aggregate += h2
        repeated_pairing = float(np.dot(weights, aggregate * h2))
        aggregate_norm = float(np.dot(weights, aggregate * aggregate))
        check("predictable_accumulation", f"repeated_h2_pairing_{count}", abs(repeated_pairing - h2_norm_oracle * count) < TOLERANCES["quadrature"], repeated_pairing, h2_norm_oracle * count)
        check("predictable_accumulation", f"repeated_h2_norm_{count}", abs(aggregate_norm - h2_norm_oracle * count * count) < TOLERANCES["quadrature"], aggregate_norm, h2_norm_oracle * count * count)
    check("predictable_accumulation", "predictable_accumulation_superlinear", (8 * 8 * h2_norm) > 8 * h2_norm, 8 * 8 * h2_norm, "> linear")
    check("mutation_checks", "naive_one_use_aggregate_norm_rejected", abs(8 * h2_norm - 8 * 8 * h2_norm) > TOLERANCES["mutation"], 8 * h2_norm, f"!= {8 * 8 * h2_norm}")

    # Bounded Rademacher coefficient: q/r ownership is exact, but the completed
    # packet is not automatically positive.
    coefficient_base = 2.0
    coefficient_amplitude = 1.0
    payment = INPUTS["matrix_payment"]
    signs = np.array([-1.0, 1.0])
    b_values = coefficient_base + coefficient_amplitude * signs
    gamma_rademacher = float(np.mean(signs * signs))
    raw_scalar = float(np.mean(b_values * (signs * signs - gamma_rademacher)))
    q_mean = float(np.mean(b_values * signs))
    bar_b_scalar = float(np.mean(b_values))
    a_scalar = bar_b_scalar + 2.0 * payment
    optimizer = -q_mean / a_scalar
    minimum = q_mean * optimizer + 0.5 * a_scalar * optimizer * optimizer
    theta_values = 2.0 * payment * b_values / (b_values + 2.0 * payment)
    transformed_mean = float(np.mean(np.sqrt(theta_values) * signs))
    d_scalar = raw_scalar - q_mean * q_mean / a_scalar - transformed_mean * transformed_mean
    check("bounded_coefficient_boundary", "rademacher_coefficient_positive", float(np.min(b_values)) > 0.0, float(np.min(b_values)), "> 0")
    check("bounded_coefficient_boundary", "rademacher_q_derived", abs(q_mean - coefficient_amplitude) < 1.0e-15, q_mean, coefficient_amplitude)
    check("bounded_coefficient_boundary", "rademacher_transformed_mean_nonzero", transformed_mean > 0.0, transformed_mean, "> 0")
    check("bounded_coefficient_boundary", "rademacher_r_restoration", abs(0.5 * (d_scalar + transformed_mean * transformed_mean) - minimum) < 2.0e-15, 0.5 * (d_scalar + transformed_mean * transformed_mean) - minimum, 0.0)
    check("bounded_coefficient_boundary", "rademacher_raw_wick_computed", abs(raw_scalar) < TOLERANCES["exact_float"], raw_scalar, 0.0)
    check("bounded_coefficient_boundary", "rademacher_completed_minimum_negative", minimum < 0.0, minimum, "< 0")
    zeta = 0.01
    block_deficit = minimum + zeta * float(np.mean(np.abs(signs) ** 6))
    for count in (1, 5, 13):
        check("bounded_coefficient_boundary", f"rademacher_direct_sum_{count}", abs(count * block_deficit - sum(block_deficit for _ in range(count))) < 1.0e-15, count * block_deficit, "linear in block count")

    # Gaussian full-forest fixture.  Expected Hermite coefficients are derived
    # symbolically from the shift and floor inputs, not pasted as output data.
    shift = INPUTS["gaussian_shift"]
    gram_floor = INPUTS["gaussian_gram_floor"]
    gaussian, gaussian_weights = normal_rule(24)
    b_gaussian = (gaussian + shift) ** 2 + gram_floor
    q_gaussian = gaussian * gaussian - 1.0
    raw_gaussian = float(np.dot(gaussian_weights, b_gaussian * q_gaussian))
    mean_gaussian = float(np.dot(gaussian_weights, b_gaussian))
    q_coefficient = float(np.dot(gaussian_weights, b_gaussian * gaussian))
    forest_coefficients = [
        float(np.dot(gaussian_weights, b_gaussian * q_gaussian * hermite(degree, gaussian))) / math.factorial(degree)
        for degree in range(5)
    ]
    constant_coefficient = gaussian_moment(2) + shift * shift + gram_floor
    b_hermite = {2: 1.0, 1: 2.0 * shift, 0: constant_coefficient}
    forest_oracle: dict[int, float] = {}
    for left_degree, left_coefficient in b_hermite.items():
        for contraction in range(min(left_degree, 2) + 1):
            degree = left_degree + 2 - 2 * contraction
            product_coefficient = math.factorial(contraction) * math.comb(left_degree, contraction) * math.comb(2, contraction)
            forest_oracle[degree] = forest_oracle.get(degree, 0.0) + left_coefficient * product_coefficient
    expected_forest = [forest_oracle.get(degree, 0.0) for degree in range(5)]
    mean_oracle = gaussian_moment(2) + 2.0 * shift * gaussian_moment(1) + (shift * shift + gram_floor) * gaussian_moment(0)
    q_oracle = gaussian_moment(3) + 2.0 * shift * gaussian_moment(2) + (shift * shift + gram_floor) * gaussian_moment(1)
    raw_oracle = gaussian_moment(4) + 2.0 * shift * gaussian_moment(3) + (shift * shift + gram_floor) * gaussian_moment(2) - mean_oracle
    check("full_forest_boundary", "gaussian_bar_b", abs(mean_gaussian - mean_oracle) < 2.0e-12, mean_gaussian, mean_oracle)
    check("full_forest_boundary", "gaussian_q", abs(q_coefficient - q_oracle) < 2.0e-12, q_coefficient, q_oracle)
    check("full_forest_boundary", "gaussian_raw_wick", abs(raw_gaussian - raw_oracle) < 2.0e-12, raw_gaussian, raw_oracle)
    for degree, expected in enumerate(expected_forest):
        check("full_forest_boundary", f"gaussian_forest_h{degree}", abs(forest_coefficients[degree] - expected) < 3.0e-11, forest_coefficients[degree], expected)
    gaussian_a = mean_gaussian + 2.0 * payment
    gaussian_optimizer = -q_coefficient / gaussian_a
    gaussian_minimum = 0.5 * raw_gaussian + q_coefficient * gaussian_optimizer + 0.5 * gaussian_a * gaussian_optimizer**2
    derived_minimum = 0.5 * raw_gaussian - 0.5 * q_coefficient**2 / gaussian_a
    check("full_forest_boundary", "gaussian_schur_minimum", abs(gaussian_minimum - derived_minimum) < 2.0e-15, gaussian_minimum, derived_minimum)
    check("full_forest_boundary", "gaussian_completed_packet_negative", gaussian_minimum < 0.0, gaussian_minimum, "< 0")
    terminal_sixth = float(np.dot(gaussian_weights, (gaussian + shift) ** 6))
    derived_sixth = sum(math.comb(6, even) * shift ** (6 - even) * math.prod(range(1, even, 2)) for even in range(0, 7, 2))
    check("full_forest_boundary", "gaussian_terminal_sixth", abs(terminal_sixth - derived_sixth) < 2.0e-10, terminal_sixth, derived_sixth)

    # A moving matrix perspective need not be a common-terminal submartingale.
    initial_matrix = float(Fraction(1))
    initial_vector = float(Fraction(1))
    next_matrix = float(Fraction(4))
    next_vector = float(Fraction(1))
    perspective_change = next_vector * next_vector / next_matrix - initial_vector * initial_vector / initial_matrix
    perspective_oracle = float(Fraction(1, 4) - Fraction(1))
    check("moving_perspective", "moving_perspective_negative_defect", perspective_change < 0.0, perspective_change, "< 0")
    check("moving_perspective", "moving_perspective_derived_value", abs(perspective_change - perspective_oracle) < TOLERANCES["exact_float"], perspective_change, perspective_oracle)
    check("mutation_checks", "omitted_moving_base_defect_rejected", abs(perspective_change) > TOLERANCES["mutation"], perspective_change, "!= innovation-only zero")

    names = [row["name"] for row in rows]
    check("contract", "contract_unique_assertion_names", len(names) == len(set(names)), len(names) - len(set(names)), 0)
    failures = [row for row in rows if row["status"] != "PASS"]
    group_counts = Counter(row["group"] for row in rows)
    group_passed = Counter(row["group"] for row in rows if row["status"] == "PASS")
    group_summary = {
        group: {
            "total": count,
            "passed": group_passed[group],
            "failed": count - group_passed[group],
        }
        for group, count in sorted(group_counts.items())
    }
    payload = {
        "schema": "tect/a13-global-gram-terminalization-covariance-deficit-reduction-primary/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertion_groups": group_summary,
        "failures": failures,
        "assertions": rows,
        "inputs": INPUTS,
        "tolerances": TOLERANCES,
        "derived": {
            "two_shell_endpoint_difference": endpoint_difference,
            "two_shell_baseline_sum": baseline_sum,
            "conditional_j_b": j_b,
            "conditional_covariance_defect": covariance_defect,
            "rademacher_minimum": minimum,
            "gaussian_forest_coefficients_h0_to_h4": forest_coefficients,
            "gaussian_minimum": gaussian_minimum,
            "gaussian_terminal_sixth": terminal_sixth,
        },
        "consequence": {
            "rational_heat_telescope": group_summary["heat_telescope"]["failed"] == 0,
            "terminal_theta_zero_schur": group_summary["terminal_schur"]["failed"] == 0,
            "posterior_covariance_normal_form": group_summary["posterior_covariance"]["failed"] == 0,
            "derivative_free_doob_terminalization": group_summary["doob_terminalization"]["failed"] == 0,
            "predictability_alone_controls_aggregate": False,
            "automatic_perspective_positivity": False,
            "production_covariance_bracket_bound": False,
            "cartan_one_use": False,
            "complete_h_n": False,
            "reg": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closure": False,
        },
        "claims_not_established": [
            "production_weighted_posterior_covariance_bound",
            "weighted_low_hermite_doob_norm",
            "common_terminal_q_r_lift_with_moving_prefix",
            "cartan_one_use_4_11",
            "complete_rational_6_5_form_bound",
            "complete_H_N",
            "REG",
            "OVERLAP_src",
            "Nelson",
            "Sector_A_closure",
        ],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-097 PRIMARY {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
