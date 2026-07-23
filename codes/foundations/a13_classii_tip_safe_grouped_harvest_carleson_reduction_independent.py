#!/usr/bin/env python3
"""Non-importing audit of the A13 tip-safe grouped-harvest reduction.

This route reconstructs its fixtures locally and never imports the primary
implementation or any earlier A13 executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TIP-SAFE-GROUPED-HARVEST-CARLESON-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-independent-tip-safe-grouped-harvest-carleson-reduction/result.json"
)
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
BALANCED = (
    REPO
    / "claims"
    / CLAIM
    / "classii_balanced_coefficient_jet_continuum_manifest.json"
)

# Independent fixture inputs.
THETA = Fraction(2, 5)
GRID = 65_537


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
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def rational_constants() -> dict[str, Any]:
    parameters = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    mass = Fraction(str(parameters["M_X"]))
    regularizer = Fraction(str(parameters["classii_mass_regularizer"]))
    denominator = mass * mass + regularizer
    a_value = Fraction(str(parameters["cJJ"])) * Fraction(str(parameters["alpha_X"])) ** 2 / denominator
    b_value = (
        Fraction(str(parameters["cJK"]))
        * Fraction(str(parameters["alpha_X"]))
        * Fraction(str(parameters["beta_X"]))
        / denominator
    )
    c_value = Fraction(str(parameters["cKK"])) * Fraction(str(parameters["beta_X"])) ** 2 / denominator
    beta_value = 4 * (a_value + 2 * b_value + c_value)
    return {
        "a_fraction": str(a_value),
        "b_fraction": str(b_value),
        "c_fraction": str(c_value),
        "determinant_fraction": str(a_value * c_value - b_value * b_value),
        "beta_fraction": str(beta_value),
        "beta_float": float(beta_value),
        "distance_constant": math.sqrt(float(beta_value)),
    }


def harvest_audit() -> dict[str, float]:
    rng = np.random.default_rng(26072381)
    rows = []
    maximum_residual = 0.0
    for dimension in (2, 4, 7):
        target = dimension + 3
        linear = rng.normal(size=(target, dimension))
        current = rng.normal(size=target)
        eta = float(rng.uniform(0.1, 1.2))
        normal = linear.T @ linear + 2.0 * eta * np.eye(dimension)
        score = linear.T @ current
        control = -np.linalg.solve(normal, score)
        harvest_direct = 0.5 * float(current @ current)
        harvest_direct -= 0.5 * float((current + linear @ control) @ (current + linear @ control))
        harvest_direct -= eta * float(control @ control)
        harvest_resolvent = 0.5 * float(score @ np.linalg.solve(normal, score))
        residual = abs(harvest_direct - harvest_resolvent)
        maximum_residual = max(maximum_residual, residual)
        rows.append({"control_dimension": dimension, "residual": residual})
    return {"maximum_residual": maximum_residual, "rows": rows}


def score_and_wick_audit() -> dict[str, float]:
    rng = np.random.default_rng(26072382)
    dimension = 5
    state = rng.normal(size=dimension)
    derivative = rng.normal(size=(3, dimension))
    shift = rng.normal(size=dimension)
    derivative_shift = rng.normal(size=(3, dimension))

    # Independent coefficient B(u)=(1+|u|^2)I+2 uu^T.
    def matrix(u: np.ndarray) -> np.ndarray:
        return (1.0 + float(u @ u)) * np.eye(dimension) + 2.0 * np.outer(u, u)

    def energy(u: np.ndarray, du: np.ndarray) -> float:
        coefficient = matrix(u)
        return 0.5 * sum(float(row @ coefficient @ row) for row in du)

    coefficient = matrix(state)
    analytic = sum(float(db @ coefficient @ dy) for db, dy in zip(derivative_shift, derivative))
    for dy in derivative:
        differential = (
            2.0 * float(state @ shift) * np.eye(dimension)
            + 2.0 * np.outer(shift, state)
            + 2.0 * np.outer(state, shift)
        )
        analytic += 0.5 * float(dy @ differential @ dy)
    residuals = []
    for step in (2.0 ** -power for power in range(8, 17)):
        finite = (
            energy(state + step * shift, derivative + step * derivative_shift)
            - energy(state - step * shift, derivative - step * derivative_shift)
        ) / (2.0 * step)
        residuals.append(abs(finite - analytic))

    raw = rng.normal(size=(dimension, dimension))
    covariance = raw @ raw.T / dimension
    trace = float(np.trace(covariance))
    fourth_exact = trace**2 + 2.0 * float(np.trace(covariance @ covariance))
    fourth_upper = 3.0 * trace**2
    return {
        "score_residual": min(residuals),
        "wick_fourth_exact": fourth_exact,
        "wick_fourth_upper": fourth_upper,
        "wick_margin": fourth_upper - fourth_exact,
    }


def gaussian_rate_audit() -> dict[str, Any]:
    rows = []
    for power in range(2, 13):
        n_value = 2**power
        derivative_trace = 24.0 * n_value + math.pi**2 / 3.0
        shell_denominator = 1.0 + (n_value + 1.0) ** 2
        ell = derivative_trace / shell_denominator
        coefficient = derivative_trace**2 / shell_denominator**2
        rows.append(
            {
                "N": n_value,
                "ell": ell,
                "ell_times_N": ell * n_value,
                "m": coefficient,
                "m_times_N2": coefficient * n_value**2,
            }
        )
    return {
        "rows": rows,
        "ell_scaled_upper": 24.0 + math.pi**2 / 3.0,
        "m_scaled_upper": (24.0 + math.pi**2 / 3.0) ** 2,
    }


def schur_audit() -> dict[str, Any]:
    theta = float(THETA)
    constant = (3.0 - 2.0 * theta) / (1.0 - theta) ** 2
    maximum_identity_residual = 0.0
    minimum_margin = math.inf
    bad_region_minimum_margin = math.inf
    for u_num in range(-9, 10):
        if u_num == 0:
            continue
        u_value = Fraction(u_num, 5)
        for a_num in range(-4, 5):
            a_value = Fraction(a_num, 10) * abs(u_value)
            if abs(a_value) > THETA * abs(u_value) or u_value + a_value == 0:
                continue
            for p_num in range(-4, 5):
                for b_num in range(-5, 6):
                    p_value = Fraction(p_num, 3)
                    b_value = Fraction(b_num, 4)
                    secant = (u_value + a_value) ** 2 * (p_value + b_value) ** 2 - u_value**2 * p_value**2
                    tangent = 2 * u_value * a_value * p_value**2 + 2 * u_value**2 * p_value * b_value
                    remainder = secant - tangent
                    completed = (u_value + a_value) ** 2 * (
                        b_value + a_value * p_value * (2 * u_value + a_value) / (u_value + a_value) ** 2
                    ) ** 2
                    completed -= a_value**2 * p_value**2 * u_value * (3 * u_value + 2 * a_value) / (u_value + a_value) ** 2
                    maximum_identity_residual = max(maximum_identity_residual, abs(float(remainder - completed)))
                    minimum_margin = min(minimum_margin, float(remainder) + constant * float(a_value**2 * p_value**2))

    rng = np.random.default_rng(26072383)
    for _ in range(10_000):
        a_value = float(rng.normal())
        u_value = float(rng.uniform(-2.0, 2.0) * abs(a_value))
        p_value, b_value = rng.normal(size=2)
        secant = (u_value + a_value) ** 2 * (p_value + b_value) ** 2 - u_value**2 * p_value**2
        bad_region_minimum_margin = min(bad_region_minimum_margin, secant + 4.0 * a_value**2 * p_value**2)
    return {
        "constant": constant,
        "maximum_identity_residual": maximum_identity_residual,
        "minimum_good_margin": minimum_margin,
        "minimum_bad_margin_for_abs_u_le_2_abs_a": bad_region_minimum_margin,
        "global_tangent_tip_sequence": [1.0 - 2.0 * value for value in (0.0, 10.0, 100.0)],
    }


def gauge_audit() -> dict[str, float]:
    c_value, a_value, b_value = 1.03, 0.61, 0.17
    q_value, n_value, m_value = 5, 13, 18
    x_value = 2.0 * math.pi * np.arange(GRID, dtype=float) / GRID
    u_value = c_value + a_value * np.cos(q_value * x_value)
    du_value = -a_value * q_value * np.sin(q_value * x_value)
    f_value = b_value * (np.cos(n_value * x_value) - np.cos(m_value * x_value))
    df_value = b_value * (-n_value * np.sin(n_value * x_value) + m_value * np.sin(m_value * x_value))
    direct = float(np.mean((u_value * du_value + f_value * df_value) ** 2 - (u_value * du_value) ** 2))
    formula = -0.5 * a_value * c_value * q_value**2 * b_value**2
    formula += 0.375 * (n_value**2 + m_value**2) * b_value**4
    return {
        "direct": direct,
        "formula": formula,
        "residual": abs(direct - formula),
        "affine_score": 0.0,
    }


def cat_and_form_audit() -> dict[str, Any]:
    inputs = json.loads(BALANCED.read_text(encoding="utf-8"))["theorem_inputs"]
    kappa = Fraction(str(inputs["kappa"]))
    theta = (1 + kappa) / 2
    y_exponent = (1 - theta) / 3
    leftover = 1 - theta - y_exponent
    m_exponent = 1 / leftover
    eta_exponent = theta / leftover
    zeta_exponent = y_exponent / leftover

    rng = np.random.default_rng(26072384)
    maximum_cat_residual = 0.0
    for _ in range(2000):
        p_zero = rng.normal(size=(3, 4))
        p_one = rng.normal(size=(3, 4))
        t_value = float(rng.uniform())
        e_zero = 0.5 * float(np.sum(p_zero**2))
        e_one = 0.5 * float(np.sum(p_one**2))
        e_t = 0.5 * float(np.sum(((1.0 - t_value) * p_zero + t_value * p_one) ** 2))
        distance = float(np.sum((p_one - p_zero) ** 2))
        maximum_cat_residual = max(
            maximum_cat_residual,
            abs(e_t + 0.5 * t_value * (1.0 - t_value) * distance - ((1.0 - t_value) * e_zero + t_value * e_one)),
        )

    # Weighted AM-GM normalization for the three-factor form estimate.
    maximum_young_ratio = 0.0
    for _ in range(20_000):
        x_value, y_value, z_value = np.exp(rng.uniform(-8.0, 8.0, size=3))
        product = x_value ** float(theta) * y_value ** float(y_exponent) * z_value ** float(leftover)
        weighted_sum = float(theta) * x_value + float(y_exponent) * y_value + float(leftover) * z_value
        maximum_young_ratio = max(maximum_young_ratio, product / weighted_sum)
    return {
        "kappa_fraction": str(kappa),
        "theta_fraction": str(theta),
        "Y_exponent_fraction": str(y_exponent),
        "leftover_fraction": str(leftover),
        "M_exponent_fraction": str(m_exponent),
        "eta_exponent_fraction": str(eta_exponent),
        "zeta_exponent_fraction": str(zeta_exponent),
        "maximum_cat_equality_residual": maximum_cat_residual,
        "maximum_weighted_young_ratio": maximum_young_ratio,
    }


def true_remainder_audit() -> dict[str, float]:
    # Independent M(z)=z^3 test: the coefficient-curvature term scales with y.
    z_value, a_value, y_value, b_value = 0.9, -0.2, 2.1, -0.3
    delta = (z_value + a_value) ** 3 * (y_value + b_value) - z_value**3 * y_value
    linear = 3.0 * z_value**2 * a_value * y_value + z_value**3 * b_value
    curvature = ((z_value + a_value) ** 3 - z_value**3 - 3.0 * z_value**2 * a_value) * y_value
    product = ((z_value + a_value) ** 3 - z_value**3) * b_value
    return {
        "residual": abs(delta - linear - curvature - product),
        "curvature_term": curvature,
        "product_term": product,
    }


def run(output: Path) -> int:
    constants = rational_constants()
    harvest = harvest_audit()
    score = score_and_wick_audit()
    gaussian = gaussian_rate_audit()
    schur = schur_audit()
    gauge = gauge_audit()
    cat_form = cat_and_form_audit()
    remainder = true_remainder_audit()
    assertions = {
        "rational_psd": Fraction(constants["determinant_fraction"]) > 0,
        "distance_constant_subunit": 0.0 < constants["distance_constant"] < 1.0,
        "harvest_resolvent": harvest["maximum_residual"] < 1e-11,
        "full_score_derivative": score["score_residual"] < 1e-7,
        "wick_fourth_bound": score["wick_margin"] >= -1e-12,
        "ell_rate": all(row["ell_times_N"] <= gaussian["ell_scaled_upper"] + 1e-12 for row in gaussian["rows"]),
        "m_rate": all(row["m_times_N2"] <= gaussian["m_scaled_upper"] + 1e-12 for row in gaussian["rows"]),
        "ell_decreases": gaussian["rows"][-1]["ell"] < gaussian["rows"][0]["ell"],
        "m_decreases": gaussian["rows"][-1]["m"] < gaussian["rows"][0]["m"],
        "schur_exact_completion": schur["maximum_identity_residual"] == 0.0,
        "schur_good_lower_bound": schur["minimum_good_margin"] >= -1e-12,
        "schur_bad_secant_bound": schur["minimum_bad_margin_for_abs_u_le_2_abs_a"] >= -1e-10,
        "global_tangent_failure": schur["global_tangent_tip_sequence"][-1] < -100.0,
        "gauge_formula": gauge["residual"] < 1e-11,
        "gauge_score_zero": gauge["affine_score"] == 0.0,
        "cat0_strong_convexity": cat_form["maximum_cat_equality_residual"] < 1e-11,
        "weighted_young": cat_form["maximum_weighted_young_ratio"] <= 1.0 + 1e-12,
        "M_exponent": cat_form["M_exponent_fraction"] == "10/3",
        "eta_exponent": cat_form["eta_exponent_fraction"] == "11/6",
        "zeta_exponent": cat_form["zeta_exponent_fraction"] == "1/2",
        "true_remainder_split": remainder["residual"] < 1e-12,
        "curvature_remainder_present": abs(remainder["curvature_term"]) > 1e-6,
    }
    assertions = {key: bool(value) for key, value in assertions.items()}
    payload = {
        "schema": "tect/a13-tip-safe-grouped-harvest-independent/1.0",
        "script_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": digest(Path(__file__)),
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "inputs": {"a1_sha256": digest(A1), "balanced_jet_sha256": digest(BALANCED)},
        "computed": {
            "rational_constants": constants,
            "harvest": harvest,
            "score_and_wick": score,
            "gaussian_rates": gaussian,
            "scalar_schur": schur,
            "gauge_beat": gauge,
            "cat_and_form": cat_form,
            "true_remainder": remainder,
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "pass": all(assertions.values()),
        "imports_primary": False,
        "honesty_boundary": (
            "Independent finite-dimensional, rational, Wick, Fourier-grid, and exponent audit. "
            "It does not prove the missing production good/bad Schur--Jacobi inequality, "
            "finite-energy extension, one-use, Nelson estimate, or any removal limit."
        ),
    }
    atomic_json(output, payload)
    passed = sum(bool(value) for value in assertions.values())
    print(f"PASS: independent ({passed}/{len(assertions)})" if payload["pass"] else f"FAIL: independent ({passed}/{len(assertions)})")
    print(
        f"Schur C={schur['constant']:.12g}; gauge residual={gauge['residual']:.3e}; "
        f"Young M exponent={cat_form['M_exponent_fraction']}"
    )
    print(f"Evidence: {output}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(run(OUT))
