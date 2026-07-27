#!/usr/bin/env python3
"""Primary executable evidence for the R-096 A13 reduction.

This program checks the low-Hermite Wick compression, rootwise tensorized
decomposition, conditional mean ownership, full-square restoration, and the
predictable-baseline support reduction.  It deliberately does not assert a
complete H_N estimate, REG, Nelson, or Sector-A closure.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOW-HERMITE-WICK-PREDICTABLE-BASELINE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-low-hermite-wick-predictable-baseline-reduction/result.json"

AUTHORITIES = {
    "r063": CLAIM_DIR / "notes/classii-coefficient-jet-forest-classification-260722-v1.0.tex.txt",
    "r077": CLAIM_DIR / "notes/classii-causal-packet-payload-resonance-reduction-260725-v1.0.tex.txt",
    "r079": CLAIM_DIR / "notes/classii-full-safe-packet-frame-current-doob-decomposition-260725-v1.0.tex.txt",
    "r085": CLAIM_DIR / "notes/classii-nonorthogonal-cartan-schur-rational-shifted-hessian-boundary-260725-v1.0.tex.txt",
    "r086": CLAIM_DIR / "notes/classii-rational-translated-wick-payload-comparable-reduction-260725-v1.0.tex.txt",
    "r095": CLAIM_DIR / "notes/classii-fractional-feedback-square-perspective-domination-boundary-260727-v1.0.tex.txt",
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


def hermite(index: int, value: np.ndarray, variance: float = 1.0) -> np.ndarray:
    """Probabilists' Hermite polynomial for N(0, variance)."""

    if index == 0:
        return np.ones_like(value)
    if index == 1:
        return value.copy()
    previous = np.ones_like(value)
    current = value.copy()
    for degree in range(1, index):
        following = value * current - degree * variance * previous
        previous, current = current, following
    return current


def normal_rule(order: int, variance: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = hermgauss(order)
    return math.sqrt(2.0 * variance) * nodes, weights / math.sqrt(math.pi)


def bounded_normal_expectation(function: Callable[[np.ndarray], np.ndarray], order: int = 720) -> float:
    """High-order independent spatial quadrature on [-12,12]."""

    nodes, weights = leggauss(order)
    points = 12.0 * nodes
    density = np.exp(-0.5 * points * points) / math.sqrt(2.0 * math.pi)
    return float(12.0 * np.dot(weights, function(points) * density))


def sech_squared(value: np.ndarray) -> np.ndarray:
    """Overflow-free sech(value)^2."""

    tail = np.exp(-2.0 * np.abs(value))
    return 4.0 * tail / (1.0 + tail) ** 2


def multi_hermite(index: tuple[int, ...], roots: list[np.ndarray]) -> np.ndarray:
    result = np.ones_like(roots[0])
    for degree, root in zip(index, roots):
        result = result * hermite(degree, root)
    return result


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
        "r063": ("coefficient-jet", "forest", "Wick"),
        "r077": ("predictable", "payload", "resonance"),
        "r079": ("future-feedback innovation block", "tag{3.4}", "safe packet"),
        "r085": ("tag{4.10}", "tag{4.11}", "shifted-Hessian"),
        "r086": ("tag{3.7}", "T_Q^>", "T_G^>"),
        "r095": ("moving-prefix", "terminal mean energy", "T_G^>"),
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

    # One-root low-Hermite compression in a non-unit scalar covariance.
    variance = 1.7
    mu = 0.7
    gamma_past = 0.3
    coefficients = np.array([1.2, -0.8, 0.45, 1.1, -0.6, 0.3, -0.2])
    roots, weights = normal_rule(80, variance)
    basis = np.stack([hermite(index, roots, variance) for index in range(len(coefficients))])
    coefficient_field = coefficients @ basis
    q_wick = (mu + roots) ** 2 - (gamma_past + variance)
    raw_pairing = float(np.dot(weights, coefficient_field * q_wick))
    rank0 = coefficients[0] * (mu * mu - gamma_past)
    rank1 = coefficients[1] * 2.0 * mu * variance
    rank2 = coefficients[2] * 2.0 * variance * variance
    compressed_pairing = rank0 + rank1 + rank2
    check("one_root_low_hermite_identity", abs(raw_pairing - compressed_pairing) < 2.0e-11, raw_pairing - compressed_pairing, 0.0)

    derivative = sum(index * coefficients[index] * basis[index - 1] for index in range(1, len(coefficients)))
    second_derivative = sum(
        index * (index - 1) * coefficients[index] * basis[index - 2]
        for index in range(2, len(coefficients))
    )
    stein_pairing = (
        coefficients[0] * (mu * mu - gamma_past)
        + 2.0 * mu * variance * float(np.dot(weights, derivative))
        + variance * variance * float(np.dot(weights, second_derivative))
    )
    check("one_root_stein_second_order_identity", abs(raw_pairing - stein_pairing) < 2.0e-11, raw_pairing - stein_pairing, 0.0)

    q_mean = float(np.dot(weights, coefficient_field * (mu + roots)))
    q_low = coefficients[0] * mu + coefficients[1] * variance
    q_stein = coefficients[0] * mu + variance * float(np.dot(weights, derivative))
    check("one_root_q_rank_zero_one", abs(q_mean - q_low) < 2.0e-11, q_mean - q_low, 0.0)
    check("one_root_q_stein", abs(q_mean - q_stein) < 2.0e-11, q_mean - q_stein, 0.0)

    low_field = coefficients[:3] @ basis[:3]
    high_field = coefficient_field - low_field
    check("rank_ge_three_wick_orthogonal", abs(float(np.dot(weights, high_field * q_wick))) < 2.0e-11, float(np.dot(weights, high_field * q_wick)), 0.0)
    check("rank_ge_two_q_orthogonal", abs(float(np.dot(weights, (coefficient_field - coefficients[:2] @ basis[:2]) * (mu + roots)))) < 2.0e-11, float(np.dot(weights, (coefficient_field - coefficients[:2] @ basis[:2]) * (mu + roots))), 0.0)

    beta = [abs(coefficients[index]) * math.sqrt(math.factorial(index) * variance**index) for index in range(3)]
    kappa = [abs(mu * mu - gamma_past), 2.0 * abs(mu) * math.sqrt(variance), math.sqrt(2.0) * variance]
    block_bound = sum(left * right for left, right in zip(beta, kappa))
    euclidean_bound = math.sqrt(sum(value * value for value in beta)) * math.sqrt(sum(value * value for value in kappa))
    check("low_rank_block_cauchy", abs(raw_pairing) <= block_bound + 1.0e-12, abs(raw_pairing), block_bound)
    check("low_rank_euclidean_cauchy", abs(raw_pairing) <= euclidean_bound + 1.0e-12, abs(raw_pairing), euclidean_bound)

    rank1_norm_sq = coefficients[1] ** 2 * variance
    rank2_norm_sq = coefficients[2] ** 2 * 2.0 * variance**2
    derivative_energy = float(np.dot(weights, derivative * derivative))
    second_derivative_energy = float(np.dot(weights, second_derivative * second_derivative))
    check("malliavin_rank_one_sufficient", rank1_norm_sq <= variance * derivative_energy + 1.0e-11, rank1_norm_sq, variance * derivative_energy)
    check("malliavin_rank_two_sufficient", rank2_norm_sq <= 0.5 * variance**2 * second_derivative_energy + 1.0e-11, rank2_norm_sq, 0.5 * variance**2 * second_derivative_energy)

    # Three-root tensorized Wick identity with mixed high coordinate ranks.
    one_nodes, one_weights = normal_rule(12)
    mesh = np.meshgrid(one_nodes, one_nodes, one_nodes, indexing="ij")
    mesh_weights = np.meshgrid(one_weights, one_weights, one_weights, indexing="ij")
    root_arrays = [item.reshape(-1) for item in mesh]
    product_weights = np.prod(np.stack([item.reshape(-1) for item in mesh_weights]), axis=0)
    coefficient_map: dict[tuple[int, int, int], float] = {
        (0, 0, 0): 0.8,
        (1, 0, 0): -0.4,
        (0, 1, 0): 0.7,
        (0, 0, 2): 0.3,
        (1, 1, 0): -0.6,
        (0, 1, 1): 0.5,
        (2, 0, 1): 0.9,
        (3, 1, 0): -0.25,
        (4, 0, 3): 0.11,
        (2, 2, 2): -0.08,
        (6, 0, 0): 0.04,
    }
    fields = {index: multi_hermite(index, root_arrays) for index in coefficient_map}
    coefficient_tensor = sum(coefficient_map[index] * fields[index] for index in coefficient_map)
    g_low = 0.4
    gamma_low = 0.2
    terminal_g = g_low + sum(root_arrays)
    terminal_q = terminal_g * terminal_g - (gamma_low + len(root_arrays))
    direct_tensor_pairing = float(np.dot(product_weights, coefficient_tensor * terminal_q))
    q_low_field = np.full_like(terminal_q, g_low * g_low - gamma_low)
    reconstructed_q = q_low_field.copy()
    root_terms: list[np.ndarray] = []
    for root_index, root in enumerate(root_arrays):
        prefix = g_low + sum(root_arrays[:root_index], np.zeros_like(root))
        term = 2.0 * prefix * root + root * root - 1.0
        root_terms.append(term)
        reconstructed_q += term
        check(f"tensor_root_term_rank_{root_index + 1}", abs(float(np.dot(product_weights, coefficient_tensor * term)) - float(np.dot(product_weights, sum((coefficient_map[index] * fields[index] for index in coefficient_map if index[root_index] in (1, 2)), np.zeros_like(term)) * term))) < 3.0e-11, float(np.dot(product_weights, coefficient_tensor * term)), "Pi1+Pi2 pairing")
    check("tensorized_q_pathwise", float(np.max(np.abs(terminal_q - reconstructed_q))) < 2.0e-12, float(np.max(np.abs(terminal_q - reconstructed_q))), 0.0)

    projected_pairing = float(np.dot(product_weights, coefficient_tensor * q_low_field))
    for root_index, term in enumerate(root_terms):
        projected = sum(
            (coefficient_map[index] * fields[index] for index in coefficient_map if index[root_index] in (1, 2)),
            np.zeros_like(term),
        )
        projected_pairing += float(np.dot(product_weights, projected * term))
    check("tensorized_low_hermite_pairing", abs(direct_tensor_pairing - projected_pairing) < 4.0e-11, direct_tensor_pairing - projected_pairing, 0.0)

    direct_tensor_mean = float(np.dot(product_weights, coefficient_tensor * terminal_g))
    projected_tensor_mean = float(np.dot(product_weights, coefficient_tensor * g_low))
    for root_index, root in enumerate(root_arrays):
        rank_one = sum(
            (coefficient_map[index] * fields[index] for index in coefficient_map if index[root_index] == 1),
            np.zeros_like(root),
        )
        projected_tensor_mean += float(np.dot(product_weights, rank_one * root))
    check("tensorized_mean_rank_one", abs(direct_tensor_mean - projected_tensor_mean) < 4.0e-11, direct_tensor_mean - projected_tensor_mean, 0.0)

    # Smooth PSD tanh fixture: raw Wick vanishes while q and transformed r survive.
    b_value = 2.0
    epsilon = 0.5
    reserve = 1.0
    raw_tanh = bounded_normal_expectation(lambda z: (b_value + epsilon * np.tanh(z)) * (z * z - 1.0))
    q_tanh = bounded_normal_expectation(lambda z: (b_value + epsilon * np.tanh(z)) * z)
    stein_q = epsilon * bounded_normal_expectation(lambda z: sech_squared(z))

    def transformed(z: np.ndarray) -> np.ndarray:
        coefficient = b_value + epsilon * np.tanh(z)
        return np.sqrt(2.0 * reserve * coefficient / (coefficient + 2.0 * reserve))

    r_tanh = bounded_normal_expectation(lambda z: z * transformed(z))
    theta_prime_factor = reserve * reserve / (b_value + epsilon * np.tanh(np.array([0.0]))[0] + 2.0 * reserve) ** 2
    check("tanh_positive_coefficient", b_value > abs(epsilon), b_value - abs(epsilon), "> 0")
    check("tanh_raw_wick_zero", abs(raw_tanh) < 2.0e-11, raw_tanh, 0.0)
    check("tanh_q_stein", abs(q_tanh - stein_q) < 3.0e-10, q_tanh - stein_q, 0.0)
    check("tanh_q_positive", q_tanh > 0.0, q_tanh, "> 0")
    check("tanh_r_positive", r_tanh > 0.0, r_tanh, "> 0")
    check("tanh_transform_derivative_sign", theta_prime_factor > 0.0, theta_prime_factor, "> 0")

    mean_a = b_value + 2.0 * reserve
    d_remainder = raw_tanh - q_tanh * q_tanh / mean_a - r_tanh * r_tanh
    optimizer = -q_tanh / mean_a
    full_minimum = 0.5 * raw_tanh + optimizer * q_tanh + 0.5 * mean_a * optimizer * optimizer
    restored_minimum = 0.5 * d_remainder + 0.5 * r_tanh * r_tanh
    check("full_square_completion", abs(full_minimum - restored_minimum) < 3.0e-10, full_minimum - restored_minimum, 0.0)
    check("terminal_mean_restores_r_debt", abs((d_remainder + r_tanh * r_tanh) - (raw_tanh - q_tanh * q_tanh / mean_a)) < 3.0e-12, (d_remainder + r_tanh * r_tanh) - (raw_tanh - q_tanh * q_tanh / mean_a), 0.0)
    check("raw_forest_cannot_cancel_q", abs(raw_tanh) < 2.0e-11 and q_tanh > 0.25, [raw_tanh, q_tanh], "raw=0 and q>0")

    # Bounded adapted selector fixture: coefficient moments remain bounded,
    # first Hermite ownership is O(1), but same-root derivative energy grows.
    selector_rows: list[dict[str, float]] = []
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        mu_scale = bounded_normal_expectation(lambda z, scale=scale: z * np.tanh(scale * z))
        derivative_energy_scale = bounded_normal_expectation(
            lambda z, scale=scale: scale * scale * sech_squared(scale * z) ** 2
        )
        selector_norm = bounded_normal_expectation(lambda z, scale=scale: np.tanh(scale * z) ** 2)
        bracket_minimum = -0.5 * mu_scale * mu_scale / selector_norm
        selector_rows.append(
            {
                "scale": scale,
                "mu": mu_scale,
                "derivative_energy": derivative_energy_scale,
                "selector_norm": selector_norm,
                "bracket_minimum": bracket_minimum,
            }
        )
        check(f"selector_bounded_{int(scale)}", selector_norm <= 1.0 + 1.0e-12, selector_norm, "<= 1")
        check(f"selector_first_hermite_positive_{int(scale)}", mu_scale > 0.0, mu_scale, "> 0")
    limiting_mu = math.sqrt(2.0 / math.pi)
    limiting_bracket = -1.0 / math.pi
    check("selector_mu_limit", abs(selector_rows[-1]["mu"] - limiting_mu) < 0.035, selector_rows[-1]["mu"], limiting_mu)
    check("selector_bracket_limit", abs(selector_rows[-1]["bracket_minimum"] - limiting_bracket) < 0.03, selector_rows[-1]["bracket_minimum"], limiting_bracket)
    check("selector_derivative_growth", selector_rows[-1]["derivative_energy"] > 6.0 * selector_rows[0]["derivative_energy"], selector_rows[-1]["derivative_energy"] / selector_rows[0]["derivative_energy"], "> 6")

    # Coordinate Hermite projection supplies no deterministic spatial gain.
    spatial_points = np.linspace(0.0, 2.0 * math.pi, 8192, endpoint=False)
    spatial_rows: list[dict[str, float]] = []
    h2_norm = 2.0
    for frequency in (1, 4, 16, 64):
        carrier = math.sqrt(2.0) * np.cos(frequency * spatial_points)
        carrier_norm = float(np.mean(carrier * carrier))
        pairing = carrier_norm * h2_norm
        spatial_rows.append({"frequency": frequency, "carrier_norm": carrier_norm, "pairing": pairing})
        check(f"spatial_carrier_norm_{frequency}", abs(carrier_norm - 1.0) < 2.0e-12, carrier_norm, 1.0)
        check(f"spatial_pairing_no_gain_{frequency}", abs(pairing - 2.0) < 4.0e-12, pairing, 2.0)

    # Complete-packet ordering and predictable-baseline support arithmetic.
    support_collar = 3
    resonance_width = 4
    large_gap = support_collar + resonance_width + 1
    for cutoff in (-2, 0, 3, 7):
        violating_pairs = [
            (m, n)
            for n in range(cutoff - 12, cutoff + support_collar + 1)
            for m in range(cutoff - 12, cutoff + large_gap + resonance_width + 3)
            if abs(m - n) <= resonance_width and m > cutoff + large_gap
        ]
        check(f"predictable_large_gap_empty_{cutoff}", not violating_pairs, violating_pairs, [])
        boundary_gap = support_collar + resonance_width
        boundary_pairs = [
            (m, n)
            for n in range(cutoff - 12, cutoff + support_collar + 1)
            for m in range(cutoff - 12, cutoff + boundary_gap + resonance_width + 3)
            if abs(m - n) <= resonance_width and m > cutoff + boundary_gap - 1
        ]
        check(f"fixed_collar_boundary_present_{cutoff}", bool(boundary_pairs), boundary_pairs[:3], "nonempty fixed boundary")

    # Doob commutes with deterministic LP projections, not with products.
    rademacher = np.array([-1.0, 1.0])
    p0_x = float(np.mean(rademacher))
    p0_xy = float(np.mean(rademacher * rademacher))
    p1_xy = rademacher * rademacher
    d_product = p1_xy - p0_xy
    factorwise = (rademacher - p0_x) * (rademacher - p0_x)
    covariance_level_one = p1_xy - rademacher * rademacher
    covariance_level_zero = p0_xy - p0_x * p0_x
    reconstructed_product = factorwise + covariance_level_one - covariance_level_zero
    check("doob_product_increment_zero", float(np.max(np.abs(d_product))) == 0.0, d_product, [0.0, 0.0])
    check("factorwise_leibniz_false", float(np.mean(factorwise)) == 1.0, float(np.mean(factorwise)), 1.0)
    check("conditional_covariance_repairs_product", float(np.max(np.abs(d_product - reconstructed_product))) == 0.0, d_product - reconstructed_product, [0.0, 0.0])

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-low-hermite-wick-predictable-baseline-reduction-primary/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "derived": {
            "raw_tanh": raw_tanh,
            "q_tanh": q_tanh,
            "r_tanh": r_tanh,
            "d_remainder": d_remainder,
            "full_minimum": full_minimum,
            "selector_rows": selector_rows,
            "spatial_rows": spatial_rows,
            "support_margin": large_gap - support_collar - resonance_width,
        },
        "boundary": {
            "coordinate_hermite_rank_at_most_two": True,
            "predictable_baseline_genuine_large_gap_empty": True,
            "full_packet_order_required": True,
            "adapted_prefix_global_payment": False,
            "complete_h_n": False,
            "reg": False,
            "sector_a_closure": False,
        },
        "failures": [row["name"] for row in failures],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-096 PRIMARY {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)}")
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
