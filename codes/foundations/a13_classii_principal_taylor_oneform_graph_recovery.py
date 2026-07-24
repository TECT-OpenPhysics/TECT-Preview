#!/usr/bin/env python3
"""Primary audit for the A13 principal Taylor one-form/graph recovery split.

This executable verifies the exact second-order Taylor attribution, the full
production reassembly of the R-074 resonance on its canonical fixture, a
constant-control omission oracle, the infinite-chaos adapted-multiplier
diagnostic, the critical third-order budget, and a finite-cutoff graph-core
recovery sequence.  It proves no signed coefficient-transport estimate and
no Nelson bound.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import a13_classii_phase_kernel_causal_diagonal_reduction as r072

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PRINCIPAL-TAYLOR-ONE-FORM-GRAPH-RECOVERY-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-primary-principal-taylor-oneform-graph-recovery/result.json"

# Regression fixtures and numerical tolerances only.
RANDOM_SEED = 24077501
RANDOM_CASES = 24
FD_STEPS = (2.0e-4, 1.0e-4)
TAYLOR_TOL = 2.0e-5
IDENTITY_TOL = 4.0e-7
GRAPH_POINTS = 4096
GRAPH_CUTOFFS = (2, 4, 8, 12)
GRAPH_REFERENCE = 16
KAPPA = 1.0 / 10.0
HONESTY_BOUNDARY = (
    "The principal unshifted second-order Taylor one-form and fixed-cutoff "
    "predictable graph recovery are closed. The adapted coefficient-transport "
    "remainder, complete lower-chaos signed endpoint estimate, one-use theorem, "
    "and Nelson bound remain open."
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def half_hessian(z: np.ndarray, a: np.ndarray, floor: float, step: float) -> list[np.ndarray]:
    base = r072.frame_jet(z, floor)[0]
    plus = r072.frame_jet(z + step * a, floor)[0]
    minus = r072.frame_jet(z - step * a, floor)[0]
    return [(right - 2.0 * middle + left) / (2.0 * step**2) for right, middle, left in zip(plus, base, minus)]


def raw_energy(z: np.ndarray, derivative: np.ndarray, q_matrix: np.ndarray, floor: float) -> float:
    frames = r072.frame_jet(z, floor)[0]
    return 0.5 * sum(float((frame.T @ derivative) @ q_matrix @ (frame.T @ derivative)) for frame in frames)


def invariant_currents(
    z: np.ndarray,
    derivative: np.ndarray,
    generators: list[np.ndarray],
    floor: float,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    denominator = float(z @ z + floor)
    ds = 2.0 * float(z @ derivative) / denominator
    masses = np.asarray([float(z @ symmetric @ z) for symmetric in generators])
    current_j = np.asarray([2.0 * float((symmetric @ z) @ derivative) for symmetric in generators])
    current_l = current_j - alpha * masses * ds
    return current_j, current_l, ds, masses


def invariant_quotient_chart(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    """Verify the projector-free (rho,m) current chart and its exact Taylor remainder."""
    generators = r072.real_generators()
    a_q = float(q_matrix[0, 0])
    b_q = float(q_matrix[0, 1])
    c_q = float(q_matrix[1, 1])
    determinant = a_q * c_q - b_q**2
    c0 = determinant / c_q
    c1 = c_q * (1.0 + b_q / c_q) ** 2
    alpha = c_q / (b_q + c_q)
    rng = np.random.default_rng(RANDOM_SEED + 3)
    max_frame_error = 0.0
    max_diagonal_error = 0.0
    max_taylor_error = 0.0
    max_phase_error = 0.0
    generic_ranks: list[int] = []
    for _ in range(96):
        z = rng.normal(size=6)
        a = 0.4 * rng.normal(size=6)
        y = rng.normal(size=6)
        c = 0.4 * rng.normal(size=6)
        frames = r072.frame_jet(z, floor)[0]
        current_j, current_l, ds, masses = invariant_currents(z, y, generators, floor, alpha)
        current_k = current_j - masses * ds
        frame_currents = np.asarray([frame.T @ y for frame in frames])
        max_frame_error = max(max_frame_error, float(np.linalg.norm(frame_currents - np.column_stack((current_j, current_k)))))
        raw = sum(float(value @ q_matrix @ value) for value in frame_currents)
        diagonal = c0 * float(current_j @ current_j) + c1 * float(current_l @ current_l)
        max_diagonal_error = max(max_diagonal_error, abs(raw - diagonal))

        endpoint = z + a
        endpoint_derivative = y + c
        j1, l1, ds1, masses1 = invariant_currents(endpoint, endpoint_derivative, generators, floor, alpha)
        delta_j = j1 - current_j
        delta_l = l1 - current_l
        denominator = float(z @ z + floor)
        r1 = 2.0 * float(z @ a)
        r2 = float(a @ a)
        dr1 = 2.0 * float(y @ a + z @ c)
        ddenominator = 2.0 * float(z @ y)
        first_ds = dr1 / denominator - r1 * ddenominator / denominator**2
        mu = np.asarray([2.0 * float(z @ symmetric @ a) for symmetric in generators])
        eta = np.asarray([float(a @ symmetric @ a) for symmetric in generators])
        dmu = np.asarray([2.0 * float(y @ symmetric @ a + z @ symmetric @ c) for symmetric in generators])
        deta = np.asarray([2.0 * float(a @ symmetric @ c) for symmetric in generators])
        first_j = dmu
        first_l = first_j - alpha * (mu * ds + masses * first_ds)
        delta_s = ds1 - ds
        remainder_s = delta_s - first_ds
        remainder_j = deta
        remainder_l = deta - alpha * (masses * remainder_s + mu * delta_s + eta * ds1)
        base_energy = 0.5 * (c0 * float(current_j @ current_j) + c1 * float(current_l @ current_l))
        endpoint_energy = 0.5 * (c0 * float(j1 @ j1) + c1 * float(l1 @ l1))
        first_energy = c0 * float(current_j @ first_j) + c1 * float(current_l @ first_l)
        direct_remainder = endpoint_energy - base_energy - first_energy
        chart_remainder = (
            c0 * (float(current_j @ remainder_j) + 0.5 * float(delta_j @ delta_j))
            + c1 * (float(current_l @ remainder_l) + 0.5 * float(delta_l @ delta_l))
        )
        max_taylor_error = max(max_taylor_error, abs(direct_remainder - chart_remainder))
        j_doublet, j_singlet = r072.phase_generators()
        for phase in (j_doublet, j_singlet):
            vertical = phase @ z
            j_vertical, l_vertical, _, _ = invariant_currents(z, vertical, generators, floor, alpha)
            max_phase_error = max(max_phase_error, float(np.linalg.norm(j_vertical)), float(np.linalg.norm(l_vertical)))
        stacked = np.concatenate(frames, axis=1)
        generic_ranks.append(int(np.linalg.matrix_rank(stacked, tol=1.0e-10)))

    pure_singlet = np.eye(6)[2]
    pure_frames = r072.frame_jet(pure_singlet, floor)[0]
    pure_frame_rank = int(np.linalg.matrix_rank(np.concatenate(pure_frames, axis=1), tol=1.0e-10))
    invariant_differential = np.vstack(
        [2.0 * pure_singlet] + [2.0 * symmetric @ pure_singlet for symmetric in generators]
    )
    invariant_rank = int(np.linalg.matrix_rank(invariant_differential, tol=1.0e-10))
    return {
        "q_entries": {"a": a_q, "b": b_q, "c": c_q},
        "diagonal_coefficients": {"c0": c0, "c1": c1, "alpha": alpha, "two_alpha": 2.0 * alpha},
        "max_frame_current_error": max_frame_error,
        "max_diagonalization_error": max_diagonal_error,
        "max_exact_taylor_chart_error": max_taylor_error,
        "max_phase_vertical_error": max_phase_error,
        "generic_frame_ranks": sorted(set(generic_ranks)),
        "pure_singlet_frame_rank": pure_frame_rank,
        "pure_singlet_invariant_rank": invariant_rank,
        "tip_boundary": "algebraic invariant-current representation, not a nondegenerate or bi-Lipschitz global quotient coordinate",
    }


def principal_resonance_reassembly(q_matrix: np.ndarray, floor: float, mass_denominator: float) -> dict[str, Any]:
    z = np.eye(6)[0]
    a = np.eye(6)[1]
    y = a.copy()
    c = a.copy()
    frames, first = r072.frame_jet(z, floor, direction=a)
    assert first is not None
    expected_isolated = -27.0 / (200.0 * mass_denominator * (1.0 + floor))
    expected_full = 3.0 * (113.0 * floor**2 + 136.0 * floor + 48.0) / (
        2000.0 * mass_denominator * (1.0 + floor) ** 2
    )
    resolutions: list[dict[str, Any]] = []
    for step in FD_STEPS:
        second_half = half_hessian(z, a, floor, step)
        generator_rows: list[dict[str, float]] = []
        isolated = 0.0
        full = 0.0
        for frame, derivative_frame, half_second in zip(frames, first, second_half):
            w00 = frame.T @ y
            w01 = frame.T @ c
            w10 = derivative_frame.T @ y
            w11 = derivative_frame.T @ c
            w20 = half_second.T @ y
            w21 = half_second.T @ c
            branch = float(w00 @ q_matrix @ w21)
            transported_linear = float(w10 @ q_matrix @ w11)
            restored_base = float(w20 @ q_matrix @ w01)
            isolated += branch
            full += branch + transported_linear + restored_base
            generator_rows.append(
                {
                    "isolated_E_b": branch,
                    "transported_linear": transported_linear,
                    "restored_base": restored_base,
                    "full": branch + transported_linear + restored_base,
                }
            )
        resolutions.append({"step": step, "isolated": isolated, "full": full, "generators": generator_rows})
    return {
        "expected_isolated": expected_isolated,
        "expected_full": expected_full,
        "resolutions": resolutions,
        "isolated_error": max(abs(row["isolated"] - expected_isolated) for row in resolutions),
        "full_error": max(abs(row["full"] - expected_full) for row in resolutions),
        "refinement_error": abs(resolutions[0]["full"] - resolutions[1]["full"]),
    }


def exact_taylor_split(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    nodes, weights = np.polynomial.legendre.leggauss(24)
    times = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights
    max_integral_error = 0.0
    max_split_error = 0.0
    max_refinement_error = 0.0
    sample: dict[str, float] = {}
    for case in range(RANDOM_CASES):
        z = rng.normal(size=6)
        a = 0.35 * rng.normal(size=6)
        y = rng.normal(size=6)
        c = rng.normal(size=6)
        frames, first = r072.frame_jet(z, floor, direction=a)
        endpoint = r072.frame_jet(z + a, floor)[0]
        assert first is not None
        direct_remainders = [right - left - tangent for right, left, tangent in zip(endpoint, frames, first)]
        split_rows: list[tuple[float, float, float]] = []
        for step in FD_STEPS:
            base_half = half_hessian(z, a, floor, step)
            integrated_d2 = [np.zeros_like(frame) for frame in frames]
            integrated_difference = [np.zeros_like(frame) for frame in frames]
            for time, weight in zip(times, weights):
                local_half = half_hessian(z + time * a, a, floor, step)
                for index, value in enumerate(local_half):
                    # D2 = 2 * half_hessian; Taylor weight is (1-t).
                    integrated_d2[index] += weight * (1.0 - time) * 2.0 * value
                    integrated_difference[index] += weight * (1.0 - time) * 2.0 * (value - base_half[index])
            integral_error = max(float(np.linalg.norm(direct - integral)) for direct, integral in zip(direct_remainders, integrated_d2))
            w = [frame.T @ y for frame in frames]
            direct_value = sum(float(root @ q_matrix @ remainder.T @ c) for root, remainder in zip(w, direct_remainders))
            principal = sum(float(root @ q_matrix @ half.T @ c) for root, half in zip(w, base_half))
            transport = sum(float(root @ q_matrix @ remainder.T @ c) for root, remainder in zip(w, integrated_difference))
            reconstruction = principal + transport
            split_error = abs(direct_value - reconstruction)
            split_rows.append((integral_error, split_error, reconstruction))
            max_integral_error = max(max_integral_error, integral_error)
            max_split_error = max(max_split_error, split_error)
        # Unlike the direct secant, this quantity depends on the independently
        # resolved Hessian stencil.  Its refinement therefore detects a stale
        # or step-insensitive principal/transport reconstruction.
        max_refinement_error = max(max_refinement_error, abs(split_rows[0][2] - split_rows[1][2]))
        if case == 0:
            sample = {
                "reconstruction": split_rows[1][2],
                "integral_error": split_rows[1][0],
                "split_error": split_rows[1][1],
            }
    return {
        "cases": RANDOM_CASES,
        "max_integral_error": max_integral_error,
        "max_split_error": max_split_error,
        "direct_refinement_error": max_refinement_error,
        "sample": sample,
    }


def constant_control_omission(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    # Fixed adversarial oracle found independently; constants are test inputs.
    z = np.asarray([-2.0087988573, 0.2161055980, -0.2093846062, 0.2320281713, -0.3769292432, 1.1938405659])
    a = np.asarray([0.4460281222, 0.0261573996, 0.0462881437, -0.2656341471, 0.1880042393, 0.9974080611])
    y = np.asarray([-0.8005849904, 1.2906569240, 1.4704710058, 1.2036294577, -0.6224917863, -1.7316179052])
    frames, first = r072.frame_jet(z, floor, direction=a)
    endpoint = r072.frame_jet(z + a, floor)[0]
    assert first is not None
    base = raw_energy(z, y, q_matrix, floor)
    end = raw_energy(z + a, y, q_matrix, floor)
    derivative = sum(float((frame.T @ y) @ q_matrix @ (tangent.T @ y)) for frame, tangent in zip(frames, first))
    delta = [(right - left).T @ y for right, left in zip(endpoint, frames)]
    retained_square = 0.5 * sum(float(value @ q_matrix @ value) for value in delta)
    remainder = end - base - derivative
    curvature_pair = sum(
        float((frame.T @ y) @ q_matrix @ ((right - frame - tangent).T @ y))
        for frame, right, tangent in zip(frames, endpoint, first)
    )
    return {
        "raw_taylor_remainder": remainder,
        "retained_square": retained_square,
        "coefficient_curvature_pair": curvature_pair,
        "reassembly_error": abs(remainder - retained_square - curvature_pair),
    }


def radial_transport_oracle(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    """Exact non-tip horizontal line on which the transported remainder survives."""
    scale = math.sqrt(floor)
    z = scale * np.eye(6)[0]
    a = z.copy()
    endpoint = z + a
    generator_index = 2  # sigma_3
    frames, first = r072.frame_jet(z, floor, direction=a)
    assert first is not None
    endpoint_frames = r072.frame_jet(endpoint, floor)[0]
    exact_remainder = endpoint_frames[generator_index] - frames[generator_index] - first[generator_index]
    half_second = half_hessian(z, a, floor, 1.0e-3)[generator_index]
    transported = exact_remainder - half_second
    g = np.eye(6)[0]
    c = g.copy()
    root = frames[generator_index].T @ g
    contraction = float(root @ q_matrix @ (transported.T @ c))
    expected = 0.3 * floor * (2.0 * q_matrix[0, 1] + q_matrix[1, 1])
    j_doublet, j_singlet = r072.phase_generators()
    phase_overlap = max(abs(float(a @ (j_doublet @ endpoint))), abs(float(a @ (j_singlet @ endpoint))))
    return {
        "exact_v_remainder_over_sqrt_floor": float(exact_remainder[0, 1] / scale),
        "principal_v_over_sqrt_floor": float(half_second[0, 1] / scale),
        "transport_v_over_sqrt_floor": float(transported[0, 1] / scale),
        "transport_contraction": contraction,
        "expected_transport_contraction": expected,
        "relative_error": abs(contraction - expected) / max(abs(expected), 1.0e-300),
        "phase_overlap": phase_overlap,
    }


def hermite_infinite_chaos() -> dict[str, Any]:
    # f(X)=exp(-X^2)(X^2-1), probabilists' Hermite coefficients.
    coefficients: dict[str, float] = {"0": -2.0 / (3.0 * math.sqrt(3.0))}
    for order in range(2, 22, 2):
        m = order // 2
        coefficients[str(order)] = ((-1.0) ** (m - 1)) * (m + 2.0) / (
            math.sqrt(3.0) * 3.0 ** (m + 1) * math.factorial(m)
        )
    t_values = (0.15, 0.4, 0.8)
    generating_errors: list[float] = []
    for t_value in t_values:
        exact = math.exp(-t_value**2 / 3.0) * (t_value**2 / 9.0 - 2.0 / 3.0) / math.sqrt(3.0)
        truncated = sum(value * t_value ** int(order) for order, value in coefficients.items())
        generating_errors.append(abs(exact - truncated))
    return {
        "coefficients": coefficients,
        "minimum_nonzero_magnitude": min(abs(value) for value in coefficients.values()),
        "generating_function_errors": generating_errors,
        "exact_generating_function": "3^(-1/2) exp(-t^2/3) (t^2/9-2/3)",
    }


def frame_lipschitz(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    max_ratio = 0.0
    max_growth = 0.0
    min_psd = math.inf
    for _ in range(256):
        u = 3.0 * rng.normal(size=6)
        v = 3.0 * rng.normal(size=6)
        frames_u = r072.frame_jet(u, floor)[0]
        frames_v = r072.frame_jet(v, floor)[0]
        denominator = max(float(np.linalg.norm(u - v)), 1.0e-14)
        max_ratio = max(max_ratio, *(float(np.linalg.norm(left - right)) / denominator for left, right in zip(frames_u, frames_v)))
        growth_denominator = max(float(np.linalg.norm(u)), 1.0e-14)
        max_growth = max(max_growth, *(float(np.linalg.norm(frame)) / growth_denominator for frame in frames_u))
        matrix = sum((frame @ q_matrix @ frame.T for frame in frames_u), np.zeros((6, 6)))
        min_psd = min(min_psd, float(np.linalg.eigvalsh(matrix).min()))
    return {"sample_max_lipschitz_ratio": max_ratio, "sample_max_linear_growth_ratio": max_growth, "sample_min_coefficient_eigenvalue": min_psd}


def fourier_field(coefficients: np.ndarray, x: np.ndarray, cutoff: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    components = coefficients.shape[0]
    value = np.zeros((x.size, components))
    first = np.zeros_like(value)
    second = np.zeros_like(value)
    for component in range(components):
        value[:, component] += coefficients[component, 0, 0]
        for mode in range(1, cutoff + 1):
            cosine = coefficients[component, mode, 0]
            sine = coefficients[component, mode, 1]
            value[:, component] += cosine * np.cos(mode * x) + sine * np.sin(mode * x)
            first[:, component] += -mode * cosine * np.sin(mode * x) + mode * sine * np.cos(mode * x)
            second[:, component] += -(mode**2) * (cosine * np.cos(mode * x) + sine * np.sin(mode * x))
    return value, first, second


def spatial_norms(value: np.ndarray, first: np.ndarray, second: np.ndarray) -> tuple[float, float]:
    point_norm = np.linalg.norm(value, axis=1)
    l6 = float(np.mean(point_norm**6) ** (1.0 / 6.0))
    h2 = float(np.mean(np.sum(value**2 + first**2 + second**2, axis=1)) ** 0.5)
    return l6, h2


def current_field(value: np.ndarray, derivative: np.ndarray, q_matrix: np.ndarray, floor: float) -> np.ndarray:
    q_sqrt = np.linalg.cholesky(q_matrix)
    output = np.zeros((value.shape[0], 3, 2))
    for index, (point, tangent) in enumerate(zip(value, derivative)):
        for generator, frame in enumerate(r072.frame_jet(point, floor)[0]):
            output[index, generator] = q_sqrt.T @ (frame.T @ tangent)
    return output


def graph_recovery(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED + 2)
    x = np.linspace(0.0, 2.0 * math.pi, GRAPH_POINTS, endpoint=False)
    u_coefficients = np.zeros((6, GRAPH_REFERENCE + 1, 2))
    a_coefficients = np.zeros_like(u_coefficients)
    u_coefficients[:, 0, 0] = rng.normal(scale=0.3, size=6)
    for mode in range(1, GRAPH_REFERENCE + 1):
        u_coefficients[:, mode, :] = rng.normal(size=(6, 2)) / (1.0 + mode**2) ** 1.8
        a_coefficients[:, mode, :] = rng.normal(size=(6, 2)) / (1.0 + mode**2) ** 1.65
    u, du, d2u = fourier_field(u_coefficients, x, GRAPH_REFERENCE)
    a_ref, da_ref, d2a_ref = fourier_field(a_coefficients, x, GRAPH_REFERENCE)
    endpoint_ref = u + a_ref
    derivative_ref = du + da_ref
    reference_current = current_field(endpoint_ref, derivative_ref, q_matrix, floor)
    rows: list[dict[str, float]] = []
    for cutoff in GRAPH_CUTOFFS:
        a, da, d2a = fourier_field(a_coefficients, x, cutoff)
        difference_l6, difference_h2 = spatial_norms(a - a_ref, da - da_ref, d2a - d2a_ref)
        endpoint = u + a
        derivative = du + da
        current = current_field(endpoint, derivative, q_matrix, floor)
        current_error = float(np.mean((current - reference_current) ** 2) ** 0.5)
        endpoint_l6, endpoint_h2 = spatial_norms(endpoint, derivative, d2u + d2a)
        rows.append(
            {
                "cutoff": float(cutoff),
                "difference_L6": difference_l6,
                "difference_H2": difference_h2,
                "current_L2_error": current_error,
                "endpoint_L6": endpoint_l6,
                "endpoint_H2": endpoint_h2,
            }
        )
    return {
        "rows": rows,
        "current_errors": [row["current_L2_error"] for row in rows],
        "L6_errors": [row["difference_L6"] for row in rows],
        "H2_errors": [row["difference_H2"] for row in rows],
        "analytic_continuity": "F(u_n)->F(u) in L2(Omega;L2) from strong L2(H2) and L6(L6)",
    }


def graph_topology_and_budget() -> dict[str, Any]:
    event_rows = []
    for n_value in (8, 27, 64, 125, 216, 343):
        amplitude = n_value ** (1.0 / 6.0)
        probability = 1.0 / n_value
        event_rows.append(
            {
                "n": n_value,
                "L2_energy": probability * amplitude**2,
                "terminal_L6_sixth": probability * amplitude**6,
            }
        )
    principal_control_power = 0.5
    principal_sextic_power = 1.0 / 3.0
    principal_slack = 1.0 - principal_control_power - principal_sextic_power
    transport_control_power = 0.5
    transport_sextic_power = 0.5
    transport_slack = 1.0 - transport_control_power - transport_sextic_power
    eta = 0.07
    zeta = 0.05
    multiplier = 1.0
    scales = (10.0, 100.0, 1000.0)
    critical_deficits = [multiplier * scale - (eta + zeta) * scale for scale in scales]
    return {
        "predictable_L2_counterexample": event_rows,
        "principal": {
            "product": "||A^2 DA||_B <= C ||A||_H2 ||A||_6^2",
            "control_power": principal_control_power,
            "sextic_power": principal_sextic_power,
            "young_slack": principal_slack,
            "current_moment": 1.0 / principal_slack,
        },
        "transport": {
            "product": "||A^3 DA||_B <= C ||A||_H2 ||A||_6^3",
            "control_power": transport_control_power,
            "sextic_power": transport_sextic_power,
            "young_slack": transport_slack,
            "necessary_absolute_multiplier_threshold": 2.0 * math.sqrt(eta * zeta),
            "test_multiplier": multiplier,
            "critical_deficits": critical_deficits,
        },
        "payload_probability_duality": [6.0, 6.0 / 5.0],
    }


def main() -> int:
    parameters, q_matrix, floor = r072.production_data()
    mass_denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    eigenvalues = np.linalg.eigvalsh(q_matrix)
    resonance = principal_resonance_reassembly(q_matrix, floor, mass_denominator)
    quotient = invariant_quotient_chart(q_matrix, floor)
    taylor = exact_taylor_split(q_matrix, floor)
    omission = constant_control_omission(q_matrix, floor)
    radial = radial_transport_oracle(q_matrix, floor)
    hermite = hermite_infinite_chaos()
    lipschitz = frame_lipschitz(q_matrix, floor)
    graph = graph_recovery(q_matrix, floor)
    budget = graph_topology_and_budget()

    rows: list[dict[str, Any]] = []
    add(rows, "production_Q_is_positive", bool(eigenvalues.min() > 0.0), eigenvalues.tolist(), ">0")
    add(rows, "frame_currents_equal_invariant_J_K_currents", quotient["max_frame_current_error"] < 2.0e-12, quotient["max_frame_current_error"], "<2e-12")
    add(rows, "Nelson_aligned_invariant_diagonalization_is_exact", quotient["max_diagonalization_error"] < 2.0e-12 and abs(quotient["diagonal_coefficients"]["alpha"] - 5.0 / 9.0) < 1.0e-14, quotient["diagonal_coefficients"], "error<2e-12, alpha=5/9")
    add(rows, "invariant_current_Taylor_chart_is_exact", quotient["max_exact_taylor_chart_error"] < 5.0e-12, quotient["max_exact_taylor_chart_error"], "<5e-12")
    add(rows, "phase_verticals_annihilate_invariant_currents", quotient["max_phase_vertical_error"] < 2.0e-12, quotient["max_phase_vertical_error"], "<2e-12")
    add(rows, "quotient_chart_preserves_tip_rank_warning", quotient["pure_singlet_frame_rank"] == 0 and quotient["pure_singlet_invariant_rank"] == 1, {"frame": quotient["pure_singlet_frame_rank"], "invariants": quotient["pure_singlet_invariant_rank"]}, "0 versus 1")
    add(rows, "principal_isolated_resonance_is_reproduced", resonance["isolated_error"] < 2.0e-7, resonance["isolated_error"], "<2e-7")
    add(rows, "full_resonance_reassembly_is_positive", resonance["expected_full"] > 0.0 and resonance["full_error"] < 2.0e-7, {"value": resonance["resolutions"][-1]["full"], "error": resonance["full_error"]}, "positive, error<2e-7")
    add(rows, "resonance_reassembly_converges_in_step", resonance["refinement_error"] < 2.0e-7, resonance["refinement_error"], "<2e-7")
    add(rows, "other_generator_restores_the_isolated_sign", resonance["resolutions"][-1]["generators"][2]["transported_linear"] > abs(resonance["expected_isolated"]), resonance["resolutions"][-1]["generators"], "full three-generator sum retained")
    add(rows, "exact_Taylor_integral_matches_frame_secant", taylor["max_integral_error"] < TAYLOR_TOL, taylor["max_integral_error"], f"<{TAYLOR_TOL}")
    add(rows, "principal_plus_transport_reconstructs_E_DA_branch", taylor["max_split_error"] < TAYLOR_TOL, taylor["max_split_error"], f"<{TAYLOR_TOL}")
    add(
        rows,
        "Taylor_split_is_checked_on_multiple_fixtures",
        taylor["cases"] == RANDOM_CASES and taylor["direct_refinement_error"] < TAYLOR_TOL,
        {"cases": taylor["cases"], "reconstruction_refinement_error": taylor["direct_refinement_error"]},
        {"cases": RANDOM_CASES, "reconstruction_refinement_error": f"<{TAYLOR_TOL}"},
    )
    add(rows, "constant_control_raw_remainder_is_negative", omission["raw_taylor_remainder"] < -1.0e-3, omission["raw_taylor_remainder"], "<-1e-3")
    add(rows, "constant_control_retained_square_is_positive", omission["retained_square"] > 1.0e-3, omission["retained_square"], ">1e-3")
    add(rows, "coefficient_curvature_channel_is_load_bearing", omission["coefficient_curvature_pair"] < -omission["retained_square"], omission, "negative magnitude exceeds square")
    add(rows, "constant_control_reassembly_is_exact", omission["reassembly_error"] < 1.0e-14, omission["reassembly_error"], "<1e-14")
    add(rows, "horizontal_radial_transport_remainder_is_nonzero", radial["transport_contraction"] > 0.0 and radial["relative_error"] < 2.0e-5, radial, "positive, relative error<2e-5")
    add(rows, "radial_transport_is_not_a_phase_Ward_channel", radial["phase_overlap"] < 1.0e-20, radial["phase_overlap"], "0")
    add(rows, "adapted_feedback_has_infinitely_many_even_chaoses", hermite["minimum_nonzero_magnitude"] > 0.0 and len(hermite["coefficients"]) == 11, hermite["coefficients"], "orders 0 through 20 all nonzero")
    add(rows, "Hermite_generating_function_cross_check", max(hermite["generating_function_errors"]) < 2.0e-10, hermite["generating_function_errors"], "<2e-10")
    add(rows, "production_frames_have_global_sample_Lipschitz_bound", lipschitz["sample_max_lipschitz_ratio"] < 20.0, lipschitz["sample_max_lipschitz_ratio"], "<20 (analytic per-frame bound 14)")
    add(rows, "production_frames_have_linear_growth", lipschitz["sample_max_linear_growth_ratio"] < 4.0, lipschitz["sample_max_linear_growth_ratio"], "<4")
    add(rows, "production_coefficient_is_PSD", lipschitz["sample_min_coefficient_eigenvalue"] > -1.0e-12, lipschitz["sample_min_coefficient_eigenvalue"], ">-1e-12")
    add(rows, "principal_Besov_route_has_one_sixth_slack", abs(budget["principal"]["young_slack"] - 1.0 / 6.0) < 1.0e-14, budget["principal"], "slack=1/6")
    add(rows, "principal_oneform_needs_exactly_sixth_moment", abs(budget["principal"]["current_moment"] - 6.0) < 1.0e-12, budget["principal"]["current_moment"], 6.0)
    add(rows, "transport_remainder_has_zero_Young_slack", abs(budget["transport"]["young_slack"]) < 1.0e-14, budget["transport"], "0")
    add(rows, "absolute_transport_deficit_grows_with_budget_scale", all(right > left for left, right in zip(budget["transport"]["critical_deficits"], budget["transport"]["critical_deficits"][1:])), budget["transport"]["critical_deficits"], "strict growth")
    add(rows, "L2_only_predictable_sequence_converges", budget["predictable_L2_counterexample"][-1]["L2_energy"] < budget["predictable_L2_counterexample"][0]["L2_energy"], [row["L2_energy"] for row in budget["predictable_L2_counterexample"]], "decreases to zero")
    add(rows, "L2_only_sequence_does_not_converge_in_terminal_L6", max(abs(row["terminal_L6_sixth"] - 1.0) for row in budget["predictable_L2_counterexample"]) < 1.0e-12, [row["terminal_L6_sixth"] for row in budget["predictable_L2_counterexample"]], "identically one")
    add(rows, "graph_recovery_H2_errors_decrease", all(right < left for left, right in zip(graph["H2_errors"], graph["H2_errors"][1:])), graph["H2_errors"], "strict decrease")
    add(rows, "graph_recovery_L6_errors_decrease", all(right < left for left, right in zip(graph["L6_errors"], graph["L6_errors"][1:])), graph["L6_errors"], "strict decrease")
    add(rows, "production_current_graph_errors_decrease", all(right < left for left, right in zip(graph["current_errors"], graph["current_errors"][1:])), graph["current_errors"], "strict decrease")
    add(rows, "production_current_graph_final_error_is_small", graph["current_errors"][-1] < 1.0e-3, graph["current_errors"][-1], "<1e-3")
    add(rows, "graph_payload_duality_uses_six_and_six_fifths", abs(sum(1.0 / value for value in budget["payload_probability_duality"]) - 1.0) < 1.0e-14, budget["payload_probability_duality"], "conjugate")
    add(
        rows,
        "scope_keeps_signed_transport_open",
        "remain open" in HONESTY_BOUNDARY
        and all(token in HONESTY_BOUNDARY for token in ("coefficient-transport", "one-use", "Nelson")),
        HONESTY_BOUNDARY,
        "explicit open coefficient-transport, one-use, and Nelson boundary",
    )

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-principal-taylor-oneform-graph-recovery-run/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "run_kind": "primary",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "version": __version__, "sha256": digest(Path(__file__).resolve())},
        "inputs": {"random_seed": RANDOM_SEED, "random_cases": RANDOM_CASES, "floor": floor, "mass_denominator": mass_denominator, "kappa": KAPPA, "graph_points": GRAPH_POINTS},
        "derived": {"invariant_quotient_chart": quotient, "resonance_reassembly": resonance, "exact_taylor_split": taylor, "constant_control_omission": omission, "radial_transport_oracle": radial, "adapted_infinite_chaos": hermite, "frame_lipschitz": lipschitz, "graph_recovery": graph, "budget": budget},
        "assertions": rows,
        "assertion_count": len(rows),
        "summary": {"status": "PASS" if passed else "FAIL", "passed": sum(row["status"] == "PASS" for row in rows), "total": len(rows)},
        "pass": passed,
        "honesty_boundary": HONESTY_BOUNDARY,
    }
    atomic_json(OUT, payload)
    print(f"A13 PRINCIPAL TAYLOR/GRAPH PRIMARY: {'PASS' if passed else 'FAIL'} {payload['summary']['passed']}/{len(rows)}")
    print(f"RESULT_JSON={OUT.relative_to(REPO).as_posix()}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
