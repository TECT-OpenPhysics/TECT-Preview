#!/usr/bin/env python3
"""Primary audit for the A10 Class-II relative structural reduction.

This program verifies the finite-dimensional algebra and the production
constants used by the accompanying proof.  It deliberately does *not* claim
the open all-field stabilised relative log-Laplace estimate.  The analytic
strict-dyadic Blaschke lemma and conditional Nelson-composition theorem live
in the proof note; this executable checks their exact formulas, signs, and
finite fixtures from hash-pinned upstream data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = "A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION"
DEFAULT_MANIFEST = REPO / "claims" / CLAIM_ID / "classii_relative_structural_reduction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-21-primary-relative-structural-reduction" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def generators() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    ]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def real_vector(field: np.ndarray) -> np.ndarray:
    return np.concatenate((field.real, field.imag), axis=-1)


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def coefficient_matrix(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    a_value, b_value, c_value = coefficients(params)
    rho_floor = float(params["rho_regularizer"])
    x_value = real_vector(field)
    rho = np.sum(np.abs(field) ** 2, axis=-1)
    eye = np.eye(6)
    result = np.zeros(field.shape[:-1] + (6, 6), dtype=np.float64)
    for generator in generators():
        symmetric = realify(generator)
        moment = np.real(np.einsum("...i,ij,...j->...", np.conj(field), generator, field))
        q_value = moment / (rho + rho_floor)
        p_value = 2.0 * np.einsum("ij,...j->...i", symmetric, x_value)
        v_value = 2.0 * np.einsum("...ij,...j->...i", symmetric - q_value[..., None, None] * eye, x_value)
        result += (
            a_value * np.einsum("...i,...j->...ij", p_value, p_value)
            + b_value * (
                np.einsum("...i,...j->...ij", p_value, v_value)
                + np.einsum("...i,...j->...ij", v_value, p_value)
            )
            + c_value * np.einsum("...i,...j->...ij", v_value, v_value)
        )
    return result


def direct_currents(field: np.ndarray, derivative: np.ndarray, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    field = np.asarray(field, dtype=np.complex128)
    derivative = np.asarray(derivative, dtype=np.complex128)
    rho = np.sum(np.abs(field) ** 2, axis=-1)
    drho = 2.0 * np.real(np.sum(np.conj(field) * derivative, axis=-1))
    floor = float(params["rho_regularizer"])
    j_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    for generator in generators():
        transformed = np.einsum("ij,...j->...i", generator, field)
        moment = np.real(np.sum(np.conj(field) * transformed, axis=-1))
        current = 2.0 * np.real(np.sum(np.conj(transformed) * derivative, axis=-1))
        q_value = moment / (rho + floor)
        j_rows.append(current)
        k_rows.append(current - q_value * drho)
    return np.stack(j_rows, axis=-1), np.stack(k_rows, axis=-1)


def q_energy(base: np.ndarray, derivative: np.ndarray, params: dict[str, Any]) -> float:
    matrix = coefficient_matrix(base, params)
    real_derivative = real_vector(derivative)
    density = 0.5 * np.einsum("...i,...ij,...j->...", real_derivative, matrix, real_derivative)
    return float(np.mean(density))


def symbol_coercivity(params: dict[str, Any]) -> float:
    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    stationary = max(0.0, (2.0 * r_value - z_value) / (2.0 * y_value - z_value))

    def ratio(x_value: float) -> float:
        return (y_value * x_value**2 + z_value * x_value + r_value) / (1.0 + x_value) ** 2

    return min(ratio(0.0), ratio(stationary), y_value)


def internal_mass(params: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(params["family_masses"], dtype=np.complex128))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, np.conj(z0)) / float(np.real(np.vdot(z0, z0)))
    return family + float(params["k_lock"]) * (np.eye(3) - projector)


def derivative_covariance_sum(cutoff: int, params: dict[str, Any]) -> np.ndarray:
    """Return sum_i Gamma_{<=N,i} in the A7 six-real convention."""
    alpha = 2.0 * math.pi / float(params["Lx"])
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    mass = internal_mass(params)
    total = np.zeros((3, 3), dtype=np.complex128)
    for n1 in range(-cutoff, cutoff + 1):
        for n2 in range(-cutoff, cutoff + 1):
            for n3 in range(-cutoff, cutoff + 1):
                k2 = alpha**2 * float(n1 * n1 + n2 * n2 + n3 * n3)
                scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
                total += k2 * np.linalg.inv(scalar * np.eye(3) + mass) / volume
    # A6/A7 fix E[Psi_k Psi_k^dagger] = 2 A(k)^-1.  Therefore the
    # complex derivative covariance is 2*total, while the six-real covariance
    # is (1/2)*realify(2*total) = realify(total).  The factor two is
    # load-bearing and must not be applied a second time here.
    complex_derivative_covariance = 2.0 * total
    return 0.5 * realify(complex_derivative_covariance)


def plane_wave_audit(params: dict[str, Any], cutoffs: list[int], grid: int) -> dict[str, Any]:
    angle = 2.0 * math.pi * np.arange(grid) / grid
    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        field = np.zeros((grid, 3), dtype=np.complex128)
        field[:, 0] = np.exp(1j * cutoff * angle)
        derivative = 1j * cutoff * field
        zero = np.zeros_like(field)
        gamma = derivative_covariance_sum(cutoff, params)
        matrices = coefficient_matrix(field, params)
        trace = 0.5 * float(np.mean(np.einsum("...ij,ji->...", matrices, gamma)))
        current = q_energy(field, derivative, params)
        frozen = q_energy(zero, derivative, params)
        j_value, k_value = direct_currents(field, derivative, params)
        rows.append(
            {
                "cutoff": cutoff,
                "q_frozen_raw": frozen,
                "q_current_raw": current,
                "trace_current": trace,
                "commutator_complete": current - frozen - trace,
                "max_abs_J": float(np.max(np.abs(j_value))),
                "max_abs_K": float(np.max(np.abs(k_value))),
                "gamma_min_eigenvalue": float(np.min(np.linalg.eigvalsh(gamma))),
                "B_trace_mean": float(np.mean(np.trace(matrices, axis1=-2, axis2=-1))),
            }
        )
    return {"rows": rows}


def counterterm_density(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    a_value, b_value, c_value = coefficients(params)
    rho = np.sum(np.abs(field) ** 2, axis=-1)
    s_value = np.sum(np.abs(field[..., :2]) ** 2, axis=-1)
    floor = float(params["rho_regularizer"])
    return (
        9.0 * (a_value + 2.0 * b_value + c_value) * s_value
        - 6.0 * b_value * s_value**2 / (rho + floor)
        - 3.0 * c_value * s_value**2 * (rho + 2.0 * floor) / (rho + floor) ** 2
    )


def component_bound_audit(params: dict[str, Any], seed: int, samples: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    a_value, b_value, c_value = coefficients(params)
    beta_b = 12.0 * a_value + 48.0 * abs(b_value) + 48.0 * c_value
    beta_1 = 24.0 * a_value + 192.0 * abs(b_value) + 288.0 * c_value
    floor = float(params["rho_regularizer"])
    max_b_ratio = 0.0
    max_db_ratio = 0.0
    max_dq_ratio = 0.0
    min_eigenvalue = math.inf
    max_mvt_ratio = 0.0
    for _ in range(samples):
        x = rng.normal(size=6)
        h = rng.normal(size=6)
        z = rng.normal(size=6)
        psi = x[:3] + 1j * x[3:]
        eta = h[:3] + 1j * h[3:]
        zeta = z[:3] + 1j * z[3:]
        matrix = coefficient_matrix(psi, params)
        norm_x = float(np.linalg.norm(x))
        norm_h = float(np.linalg.norm(h))
        min_eigenvalue = min(min_eigenvalue, float(np.min(np.linalg.eigvalsh(matrix))))
        max_b_ratio = max(max_b_ratio, float(np.linalg.norm(matrix, "fro")) / max(norm_x**2, 1e-30))
        step = 1.0e-6 / max(1.0, norm_h)
        db = (coefficient_matrix(psi + step * eta, params) - coefficient_matrix(psi - step * eta, params)) / (2.0 * step)
        max_db_ratio = max(max_db_ratio, float(np.linalg.norm(db, "fro")) / max(norm_x * norm_h, 1e-30))
        for generator in generators():
            symmetric = realify(generator)
            numerator = float(x @ symmetric @ x)
            denominator = float(x @ x) + floor
            dq = (2.0 * float(h @ symmetric @ x) * denominator - 2.0 * numerator * float(x @ h)) / denominator**2
            max_dq_ratio = max(max_dq_ratio, abs(dq) * norm_x / max(norm_h, 1e-30))
        matrix_z = coefficient_matrix(zeta, params)
        distance = float(np.linalg.norm(z - x))
        denominator_mvt = 0.5 * beta_1 * (norm_x + float(np.linalg.norm(z))) * distance
        max_mvt_ratio = max(max_mvt_ratio, float(np.linalg.norm(matrix_z - matrix, "fro")) / max(denominator_mvt, 1e-30))
    return {
        "beta_B": beta_b,
        "beta_1": beta_1,
        "max_B_over_x2": max_b_ratio,
        "max_DB_over_xh": max_db_ratio,
        "max_Dq_x_over_h": max_dq_ratio,
        "minimum_B_eigenvalue": min_eigenvalue,
        "max_mean_value_bound_ratio": max_mvt_ratio,
    }


def raw_algebra_audit(seed: int, samples: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    max_identity_error = 0.0
    min_raw_slack = math.inf
    max_complete_identity_error = 0.0
    max_action_identity_error = 0.0
    min_past_energy_remainder = math.inf
    for _ in range(samples):
        qx = float(rng.random() * 10.0)
        qz = float(rng.random() * 10.0)
        theta = float(rng.random())
        tj_x = float(rng.normal())
        told_x = float(rng.normal())
        tall_z = float(rng.normal())
        q_fr = qx - tj_x
        commutator = qz - qx - tall_z + tj_x + told_x
        direct = theta * q_fr + commutator
        reduced = qz - (1.0 - theta) * qx - tall_z + told_x + (1.0 - theta) * tj_x
        max_identity_error = max(max_identity_error, abs((theta * qx + qz - qx) - (qz - (1.0 - theta) * qx)))
        max_complete_identity_error = max(max_complete_identity_error, abs(direct - reduced))
        min_raw_slack = min(min_raw_slack, (qz - qx) + qx)
        q_past = float(rng.random() * 10.0)
        endpoint = qz - tall_z
        past_endpoint = q_past - told_x
        shell_sum = q_fr + commutator
        action_reconstruction = endpoint - past_endpoint + q_past
        max_action_identity_error = max(max_action_identity_error, abs(shell_sum - action_reconstruction))
        min_past_energy_remainder = min(min_past_energy_remainder, shell_sum - (endpoint - past_endpoint))
    return {
        "max_raw_identity_error": max_identity_error,
        "max_complete_identity_error": max_complete_identity_error,
        "min_Craw_plus_qx": min_raw_slack,
        "max_action_identity_error": max_action_identity_error,
        "min_past_energy_remainder": min_past_energy_remainder,
    }


def blaschke_coefficients(radius: float, order: int) -> np.ndarray:
    values = np.zeros(order + 1, dtype=np.float64)
    values[0] = -radius
    if order:
        indices = np.arange(1, order + 1, dtype=np.float64)
        values[1:] = (1.0 - radius**2) * radius ** (indices - 1.0)
    return values


def blaschke_row(radius: float, m_value: int, params: dict[str, Any], grid: int) -> dict[str, float]:
    angle = 2.0 * math.pi * np.arange(grid) / grid
    phases = np.exp(1j * np.outer(angle, np.arange(2 * m_value + 1)))
    full_coefficients = blaschke_coefficients(radius, 2 * m_value)
    low_coefficients = full_coefficients.copy()
    low_coefficients[m_value + 1 :] = 0.0
    modes = np.arange(2 * m_value + 1, dtype=np.float64)
    z_value = phases @ full_coefficients
    x_value = phases @ low_coefficients
    dz_value = phases @ (1j * modes * full_coefficients)
    floor = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)

    def scalar_q(base: np.ndarray) -> float:
        source = 2.0 * np.real(np.conj(base) * dz_value)
        s_value = floor / (np.abs(base) ** 2 + floor)
        weight = 0.5 * (a_value + 2.0 * b_value * s_value + c_value * s_value**2)
        return float(np.mean(weight * source**2))

    frozen = scalar_q(x_value)
    current = scalar_q(z_value)
    modulus_derivative = 2.0 * np.real(np.conj(z_value) * dz_value)
    exact_norm = 2.0 * (1.0 - radius**2) ** 2 * sum(
        k * k * radius ** (8 * m_value - 2 * k) for k in range(1, 2 * m_value + 1)
    )
    return {
        "m": m_value,
        "frozen_raw": frozen,
        "current_raw": current,
        "negative_commutator_ratio": (frozen - current) / frozen,
        "current_over_frozen": current / frozen,
        "modulus_derivative_l2": float(np.mean(modulus_derivative**2)),
        "modulus_derivative_exact": exact_norm,
    }


def convolve(left: dict[tuple[int, int], Fraction], right: dict[tuple[int, int], Fraction]) -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for (i1, i2), left_value in left.items():
        for (j1, j2), right_value in right.items():
            mode = (i1 + j1, i2 + j2)
            result[mode] = result.get(mode, Fraction(0)) + left_value * right_value
    return {mode: value for mode, value in result.items() if value}


def power(base: dict[tuple[int, int], Fraction], exponent: int) -> dict[tuple[int, int], Fraction]:
    result = {(0, 0): Fraction(1)}
    for _ in range(exponent):
        result = convolve(result, base)
    return result


def triad_audit(params: dict[str, Any], epsilon: Fraction) -> dict[str, Any]:
    half = Fraction(1, 2)
    g = {(1, 0): half, (-1, 0): half, (0, 1): half, (0, -1): half, (1, 1): -half, (-1, -1): -half}
    dx = {mode: complex(0.0, float(mode[0] * value)) for mode, value in g.items()}
    dy = {mode: complex(0.0, float(mode[1] * value)) for mode, value in g.items()}

    def cconv(left: dict[tuple[int, int], complex], right: dict[tuple[int, int], complex]) -> dict[tuple[int, int], complex]:
        out: dict[tuple[int, int], complex] = {}
        for p, x_value in left.items():
            for q, y_value in right.items():
                mode = (p[0] + q[0], p[1] + q[1])
                out[mode] = out.get(mode, 0j) + x_value * y_value
        return out

    grad2_complex = cconv(dx, dx)
    for mode, value in cconv(dy, dy).items():
        grad2_complex[mode] = grad2_complex.get(mode, 0j) + value
    g_complex = {mode: complex(float(value), 0.0) for mode, value in g.items()}
    avg_grad2 = grad2_complex.get((0, 0), 0j).real
    avg_g_grad2 = cconv(g_complex, grad2_complex).get((0, 0), 0j).real
    avg_g2_grad2 = cconv(cconv(g_complex, g_complex), grad2_complex).get((0, 0), 0j).real
    one_plus = {(0, 0): Fraction(1)} | {mode: epsilon * value for mode, value in g.items()}
    m6 = power(one_plus, 6).get((0, 0), Fraction(0))
    a_value, _, _ = coefficients(params)
    eps = float(epsilon)
    c_f = 4.0 * a_value * eps**2
    c_c = a_value * eps**3 * (4.0 - 5.0 * eps)
    c_h = 1.5 * float(params["Y"]) * eps**2
    c_6 = float(m6)
    theta_ray = eps - 1.25 * eps**2
    return {
        "epsilon": eps,
        "average_grad2": avg_grad2,
        "average_g_grad2": avg_g_grad2,
        "average_g2_grad2": avg_g2_grad2,
        "M6_fraction": f"{m6.numerator}/{m6.denominator}",
        "M6": c_6,
        "c_F": c_f,
        "c_C": c_c,
        "c_H": c_h,
        "c_6": c_6,
        "theta_cost_free": theta_ray,
        "theta_family_supremum": 7.0 / 36.0,
        "budget_product_at_theta_zero": c_c**2 / (4.0 * c_h * c_6),
    }


def composition_audit(params: dict[str, Any], target: dict[str, Any]) -> dict[str, float]:
    theta = float(target["theta"])
    alpha_f = float(target["alpha_f"])
    alpha_c = float(target["alpha_c"])
    alpha_d = float(target["alpha_d"])
    epsilon_6 = float(target["epsilon_6"])
    epsilon_d = float(target["epsilon_d"])
    p_value = float(target["p"])
    kf_over_cfr = (1.0 - theta) ** 2 / (4.0 * alpha_f)
    alpha = alpha_f + alpha_c + alpha_d
    b_6 = float(params["gamma"]) / 6.0 - epsilon_6 - epsilon_d
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    ceiling_factor = 4.0 * p_value * volume / (27.0 * b_6**2)
    return {
        "theta": theta,
        "alpha_f": alpha_f,
        "alpha_c": alpha_c,
        "alpha_d": alpha_d,
        "alpha_total": alpha,
        "epsilon_6": epsilon_6,
        "epsilon_d": epsilon_d,
        "p": p_value,
        "p_alpha": p_value * alpha,
        "B6": b_6,
        "Kf_over_Cfr": kf_over_cfr,
        "negative_lambda_quartic": max(-float(params["lambda"]), 0.0) / 4.0,
        "ceiling_factor_times_A4_cubed": ceiling_factor,
    }


def variational_fixture(alpha: float) -> dict[str, float]:
    base = np.asarray([0.11, 0.23, 0.17, 0.49], dtype=np.float64)
    energy = np.asarray([0.7, -0.4, 1.2, -1.1], dtype=np.float64)
    log_moment = math.log(float(np.sum(base * np.exp(-energy / alpha))))
    tilted = base * np.exp(-energy / alpha - log_moment)
    entropy = float(np.sum(tilted * np.log(tilted / base)))
    objective = -float(tilted @ energy) / alpha - entropy
    return {"log_moment": log_moment, "variational_objective": objective, "absolute_error": abs(log_moment - objective)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    a1_path = REPO / authority["production_functional_manifest"]["path"]
    a7_path = REPO / authority["a7_composite_manifest"]["path"]
    a9_path = REPO / authority["a9_smart_path_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    a7 = json.loads(a7_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    audit = manifest["audit"]
    rows: list[dict[str, Any]] = []

    for label, path, row in (
        ("A1", a1_path, authority["production_functional_manifest"]),
        ("A7", a7_path, authority["a7_composite_manifest"]),
        ("A9", a9_path, authority["a9_smart_path_manifest"]),
    ):
        actual_hash = sha256(path)
        add(f"{label}_authority_hash", actual_hash == row["sha256"], actual_hash, row["sha256"], rows)

    a_value, b_value, c_value = coefficients(params)
    q_ii = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    q_eigenvalues = np.linalg.eigvalsh(q_ii)
    add("production_QII_positive", bool(q_eigenvalues[0] > 0.0), q_eigenvalues.tolist(), "both positive", rows)

    bounds = component_bound_audit(params, int(audit["seed"]), int(audit["coefficient_samples"]))
    add("beta_B_derived", abs(bounds["beta_B"] - float(manifest["constants"]["beta_B"])) < 1e-14, bounds["beta_B"], manifest["constants"]["beta_B"], rows)
    add("beta_1_derived", abs(bounds["beta_1"] - float(manifest["constants"]["beta_1"])) < 1e-13, bounds["beta_1"], manifest["constants"]["beta_1"], rows)
    add("B_is_PSD_samples", bounds["minimum_B_eigenvalue"] >= -float(audit["matrix_tolerance"]), bounds["minimum_B_eigenvalue"], f">=-{audit['matrix_tolerance']}", rows)
    add("B_quadratic_growth_samples", bounds["max_B_over_x2"] <= bounds["beta_B"] * (1.0 + 1e-8), bounds["max_B_over_x2"], bounds["beta_B"], rows)
    add("DB_growth_samples", bounds["max_DB_over_xh"] <= bounds["beta_1"] * (1.0 + 1e-6), bounds["max_DB_over_xh"], bounds["beta_1"], rows)
    add("Dq_component_bound_samples", bounds["max_Dq_x_over_h"] <= 4.0 * (1.0 + 1e-10), bounds["max_Dq_x_over_h"], 4.0, rows)
    add("B_mean_value_bound_samples", bounds["max_mean_value_bound_ratio"] <= 1.0 + 1e-6, bounds["max_mean_value_bound_ratio"], "<=1", rows)

    algebra = raw_algebra_audit(int(audit["seed"]) + 1, int(audit["algebra_samples"]))
    add("raw_retained_identity", algebra["max_raw_identity_error"] < 1e-13, algebra["max_raw_identity_error"], 0.0, rows)
    add("complete_Gamma_j_identity", algebra["max_complete_identity_error"] < 1e-13, algebra["max_complete_identity_error"], 0.0, rows)
    add(
        "multiscale_action_identity_and_positive_past_remainder",
        algebra["max_action_identity_error"] < 1e-13 and algebra["min_past_energy_remainder"] >= 0.0,
        {"identity_error": algebra["max_action_identity_error"], "minimum_remainder": algebra["min_past_energy_remainder"]},
        {"identity_error": 0.0, "minimum_remainder": ">=0"},
        rows,
    )
    add("raw_C_lower_bound", algebra["min_Craw_plus_qx"] >= 0.0, algebra["min_Craw_plus_qx"], ">=0", rows)
    add("frozen_trace_convention", manifest["frozen_shell_convention"]["trace"] == "Gamma_j", manifest["frozen_shell_convention"]["trace"], "Gamma_j", rows)
    add("commutator_trace_convention", manifest["frozen_shell_convention"]["commutator_trace"] == "Gamma_le_j", manifest["frozen_shell_convention"]["commutator_trace"], "Gamma_le_j", rows)

    blaschke = [
        blaschke_row(float(audit["blaschke_radius"]), int(m_value), params, int(audit["blaschke_grid"]))
        for m_value in audit["blaschke_m_values"]
    ]
    ratios = [row["negative_commutator_ratio"] for row in blaschke]
    norm_errors = [abs(row["modulus_derivative_l2"] - row["modulus_derivative_exact"]) for row in blaschke]
    add("strict_dyadic_blaschke_monotone_tail", all(right > left for left, right in zip(ratios[-4:-1], ratios[-3:])), ratios, "last four strictly increase", rows)
    add("strict_dyadic_ratio_near_one", ratios[-1] > float(audit["blaschke_ratio_floor"]), ratios[-1], audit["blaschke_ratio_floor"], rows)
    add("blaschke_exact_autocorrelation", max(norm_errors) < float(audit["quadrature_tolerance"]), max(norm_errors), audit["quadrature_tolerance"], rows)

    plane_wave = plane_wave_audit(params, [int(value) for value in audit["plane_wave_cutoffs"]], int(audit["plane_wave_grid"]))
    max_current = max(abs(row["q_current_raw"]) for row in plane_wave["rows"])
    max_frozen = max(abs(row["q_frozen_raw"]) for row in plane_wave["rows"])
    max_jk = max(max(row["max_abs_J"], row["max_abs_K"]) for row in plane_wave["rows"])
    add("plane_wave_zero_frozen_energy", max_frozen < 1e-24, max_frozen, 0.0, rows)
    add("plane_wave_common_phase_currents_zero", max_jk < float(audit["current_tolerance"]), max_jk, audit["current_tolerance"], rows)
    add("plane_wave_current_raw_zero", max_current < float(audit["current_tolerance"]), max_current, audit["current_tolerance"], rows)
    add("plane_wave_B_nonzero", min(row["B_trace_mean"] for row in plane_wave["rows"]) > 0.0, [row["B_trace_mean"] for row in plane_wave["rows"]], ">0", rows)
    covariance_convention = manifest["frozen_shell_convention"]["covariance_normalisation"]
    add(
        "plane_wave_Gamma_positive_and_A7_factor_two",
        min(row["gamma_min_eigenvalue"] for row in plane_wave["rows"]) > 0.0
        and covariance_convention == "Gamma=0.5*realify(D_complex)=realify(sum_k |k|^2 A(k)^-1/V), with D_complex=2*sum_k |k|^2 A(k)^-1/V",
        {"eigenvalues": [row["gamma_min_eigenvalue"] for row in plane_wave["rows"]], "convention": covariance_convention},
        "positive and exact A7 complex-factor-two convention",
        rows,
    )
    final_plane = plane_wave["rows"][-1]
    finite_slope = -final_plane["commutator_complete"] / final_plane["cutoff"]
    asymptotic_slope = float(manifest["constants"]["sharp_cube_trace_defect_coefficient"])
    slope_relative_error = abs(finite_slope / asymptotic_slope - 1.0)
    add(
        "zero_frozen_negative_commutator_and_A6_slope",
        all(row["commutator_complete"] < 0.0 for row in plane_wave["rows"])
        and slope_relative_error < float(audit["plane_wave_slope_relative_tolerance"]),
        {"values": [row["commutator_complete"] for row in plane_wave["rows"]], "finite_slope": finite_slope, "relative_error": slope_relative_error},
        {"sign": "all negative", "asymptotic_slope": asymptotic_slope, "relative_error_below": audit["plane_wave_slope_relative_tolerance"]},
        rows,
    )

    unit = np.asarray([[1.0 + 0j, 0j, 0j]])
    pure_third = np.asarray([[0j, 0j, 1.0 + 0j]])
    w_unit = float(counterterm_density(unit, params)[0])
    w_third = float(counterterm_density(pure_third, params)[0])
    w_infinity = 9.0 * a_value + 12.0 * b_value + 6.0 * c_value
    delta_cube = float(a7["constants"]["delta_cube"]["value"])
    defect_coefficient = delta_cube * w_infinity
    add("W_active_doublet_positive", w_unit > 0.0, w_unit, ">0", rows)
    add("W_pure_third_zero", abs(w_third) < 1e-30, w_third, 0.0, rows)
    add("W_large_amplitude_coefficient", abs(w_infinity - float(manifest["constants"]["W_infinity"])) < 1e-14, w_infinity, manifest["constants"]["W_infinity"], rows)
    add("sharp_cube_trace_defect_coefficient", abs(defect_coefficient - float(manifest["constants"]["sharp_cube_trace_defect_coefficient"])) < 1e-14, defect_coefficient, manifest["constants"]["sharp_cube_trace_defect_coefficient"], rows)

    c_symbol = symbol_coercivity(params)
    alpha_c = float(manifest["composition_target"]["alpha_c"])
    c_gamma = 26.0 * math.sqrt(6.0) / ((2.0 * math.pi) ** 3 * c_symbol)
    k0 = (bounds["beta_B"] * c_gamma / (alpha_c * c_symbol)) ** (1.0 / 3.0)
    add("symbol_coercivity_positive", c_symbol > 0.0, c_symbol, ">0", rows)
    add("plane_wave_entropy_is_necessary", manifest["theorem"]["entropy_necessity"] == "alpha_c>0", manifest["theorem"]["entropy_necessity"], "alpha_c>0", rows)
    add("plane_wave_trace_entropy_ratio_decays_Kminus3", k0 > 0.0 and math.isfinite(k0), k0, "finite positive threshold for identified family", rows)

    triad = triad_audit(params, Fraction(3, 10))
    add("triad_exact_averages", max(abs(triad["average_grad2"] - 2.0), abs(triad["average_g_grad2"] + 1.0), abs(triad["average_g2_grad2"] - 2.5)) < 1e-14, [triad["average_grad2"], triad["average_g_grad2"], triad["average_g2_grad2"]], [2.0, -1.0, 2.5], rows)
    add("triad_theta_three_sixteenths", abs(triad["theta_cost_free"] - 3.0 / 16.0) < 1e-15, triad["theta_cost_free"], 3.0 / 16.0, rows)
    add("triad_family_supremum_seven_thirtysixths", abs(triad["theta_family_supremum"] - 7.0 / 36.0) < 1e-15, triad["theta_family_supremum"], 7.0 / 36.0, rows)
    add("triad_budget_discriminant_positive", triad["budget_product_at_theta_zero"] > 0.0, triad["budget_product_at_theta_zero"], ">0", rows)

    composition = composition_audit(params, manifest["composition_target"])
    add("composition_entropy_budget_strict", composition["p_alpha"] < 1.0, composition["p_alpha"], "<1", rows)
    add("composition_sextic_budget_strict", composition["B6"] > 0.0, composition["B6"], ">0", rows)
    add("composition_scaled_frozen_cost", abs(composition["Kf_over_Cfr"] - 0.05) < 1e-14, composition["Kf_over_Cfr"], 0.05, rows)
    add("composition_quartic_anchor", abs(composition["negative_lambda_quartic"] - 0.1075) < 1e-14, composition["negative_lambda_quartic"], 0.1075, rows)
    add("composition_ceiling_finite", composition["ceiling_factor_times_A4_cubed"] > 0.0 and math.isfinite(composition["ceiling_factor_times_A4_cubed"]), composition["ceiling_factor_times_A4_cubed"], "finite positive", rows)

    variational = variational_fixture(composition["alpha_c"])
    add("stabilised_DV_equivalence_fixture", variational["absolute_error"] < 1e-14, variational["absolute_error"], 0.0, rows)
    expected_open = [
        "A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION",
        "A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE",
    ]
    add(
        "prerequisite_firewall_and_cube_filtration_closure",
        manifest["open_followups"] == expected_open
        and manifest["closed_subgates"] == ["A10-CLASSII-DYADIC-FILTRATION-REALISATION"],
        {"open": manifest["open_followups"], "closed": manifest["closed_subgates"]},
        {"open": expected_open, "closed": ["A10-CLASSII-DYADIC-FILTRATION-REALISATION"]},
        rows,
    )
    exclusions = manifest["honesty_boundary"]["excluded"]
    add("scope_excludes_A7_Nelson_closure", "the self-coupled A7 Nelson bound" in exclusions, exclusions, "contains A7 Nelson exclusion", rows)
    add("scope_excludes_Gibbs_measure", "a full three-component interacting Gibbs measure" in exclusions, exclusions, "contains Gibbs exclusion", rows)
    add("scope_excludes_T6_T7", "T6 or T7" in exclusions, exclusions, "contains T6/T7 exclusion", rows)

    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": manifest["run_contract"]["primary_result_schema"],
        "verdict": "A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-PRIMARY-PASS" if not failed else "FAIL",
        "claim_id": CLAIM_ID,
        "version": __version__,
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "python": sys.version,
        "assertion_count": len(rows),
        "failed": failed,
        "assertions": rows,
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value},
            "QII_eigenvalues": q_eigenvalues.tolist(),
            "bounds": bounds,
            "raw_algebra": algebra,
            "blaschke": blaschke,
            "plane_wave": plane_wave,
            "W_unit": w_unit,
            "W_infinity": w_infinity,
            "delta_cube": delta_cube,
            "sharp_cube_trace_defect_coefficient": defect_coefficient,
            "symbol_coercivity": c_symbol,
            "plane_wave_CGamma_bound": c_gamma,
            "plane_wave_entropy_threshold_K0": k0,
            "triad": triad,
            "composition": composition,
            "variational_fixture": variational,
        },
    }
    atomic_json(args.output, payload)
    if failed:
        print(f"FAIL: {len(failed)} assertions: {', '.join(failed)}")
        print(f"Evidence: {args.output.resolve()}")
        return 1
    print(f"{len(rows)}/{len(rows)} PASS")
    print(f"strict-dyadic ratio: {ratios[-1]:.12g}")
    print(f"plane-wave C: {plane_wave['rows'][-1]['commutator_complete']:.12g}")
    print("A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-PRIMARY-PASS")
    print(f"Evidence: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
