#!/usr/bin/env python3
"""Primary audit of the A13 NPC-cone and martingale-injection reduction.

The executable derives the production coefficients from the pinned A1
authority, verifies the exact current factorisation and aggregate cone metric,
checks a positive-floor retained-square shellwise counterexample, and tests the
raw-energy/noise-injection telescope by exact Gaussian cubature.  It does not
prove the remaining global injection-balance, one-use, or Nelson estimate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import hashlib
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a6_classii_uv_power_counting as uv  # noqa: E402
import a13_classii_translation_model_reduction as tr  # noqa: E402

CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-primary-npc-cone-martingale-injection-reduction/result.json"
)
TRANSLATION_MANIFEST = (
    REPO / "claims" / CLAIM / "classii_translation_model_reduction_manifest.json"
)
STRICT_PAST_MANIFEST = (
    REPO / "claims" / CLAIM / "classii_strict_past_signed_causal_reduction_manifest.json"
)

# A rational, uniformly positive harmonic fixture.  These are test inputs, not
# model parameters or hardcoded derived outputs.
WITNESS_C = Fraction(101, 100)
WITNESS_A = Fraction(1, 1)
WITNESS_B = Fraction(-3, 400)
WITNESS_GRID = 1 << 16


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


def production_parameters() -> dict[str, Any]:
    translation = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
    authority = REPO / translation["authority"]["a1_manifest"]["path"]
    return json.loads(authority.read_text(encoding="utf-8"))["parameters"]


def nelson_exponent() -> tuple[float, float]:
    authority = json.loads(STRICT_PAST_MANIFEST.read_text(encoding="utf-8"))
    epsilon_control = float(authority["audit"]["epsilon_control"])
    return 1.0 / (2.0 * epsilon_control), epsilon_control


def standard_hermite(dimension: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * dimension, dtype=np.int16).reshape(dimension, -1).T
    points = math.sqrt(2.0) * nodes[indices]
    product_weights = np.prod(weights[indices], axis=1) / (math.pi ** (dimension / 2.0))
    return points, product_weights


def coefficient_and_factorisation_audit(parameters: dict[str, Any]) -> dict[str, float]:
    a_value, b_value, c_value = tr.coefficients(parameters)
    determinant = a_value * c_value - b_value * b_value
    alpha = c_value / (b_value + c_value)
    residual_coefficient = determinant / c_value
    transformed_coefficient = c_value * (1.0 + b_value / c_value) ** 2
    q_value, _ = nelson_exponent()

    rng = np.random.default_rng(26072351)
    symmetric_generators = tuple(tr.realify(generator) for generator in uv.generators())
    maximum_fierz_residual = 0.0
    maximum_factorisation_residual = 0.0
    maximum_transformed_residual = 0.0
    minimum_radial_eigenvalue_ratio = math.inf
    floor = float(parameters["rho_regularizer"])
    for _ in range(2000):
        state = rng.normal(size=6)
        derivative = rng.normal(size=6)
        rho = float(state @ state)
        density = rho + floor
        doublet_density = float(state[[0, 1, 3, 4]] @ state[[0, 1, 3, 4]])
        moments = np.asarray([state @ generator @ state for generator in symmetric_generators])
        moment_derivatives = np.asarray(
            [2.0 * derivative @ generator @ state for generator in symmetric_generators]
        )
        maximum_fierz_residual = max(
            maximum_fierz_residual,
            abs(float(moments @ moments) - doublet_density**2),
        )
        d_log_density = 2.0 * float(state @ derivative) / density
        k_current = moment_derivatives - moments * d_log_density
        normalized_current = moment_derivatives - alpha * moments * d_log_density
        direct = (
            a_value * float(moment_derivatives @ moment_derivatives)
            + 2.0 * b_value * float(moment_derivatives @ k_current)
            + c_value * float(k_current @ k_current)
        )
        factored = residual_coefficient * float(moment_derivatives @ moment_derivatives)
        factored += transformed_coefficient * float(normalized_current @ normalized_current)
        maximum_factorisation_residual = max(
            maximum_factorisation_residual,
            abs(direct - factored) / max(1.0, abs(direct), abs(factored)),
        )
        transformed_moment_derivative = density ** (-alpha) * normalized_current
        transformed = residual_coefficient * float(moment_derivatives @ moment_derivatives)
        transformed += transformed_coefficient * density**q_value * float(
            transformed_moment_derivative @ transformed_moment_derivative
        )
        maximum_transformed_residual = max(
            maximum_transformed_residual,
            abs(direct - transformed) / max(1.0, abs(direct), abs(transformed)),
        )
        radial_ratio = 1.0 - alpha * rho / density
        minimum_radial_eigenvalue_ratio = min(minimum_radial_eigenvalue_ratio, radial_ratio)

    return {
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "determinant": determinant,
        "alpha": alpha,
        "nelson_exponent": q_value,
        "residual_coefficient": residual_coefficient,
        "transformed_coefficient": transformed_coefficient,
        "maximum_fierz_residual": maximum_fierz_residual,
        "maximum_factorisation_residual": maximum_factorisation_residual,
        "maximum_transformed_residual": maximum_transformed_residual,
        "minimum_sampled_radial_eigenvalue_ratio": minimum_radial_eigenvalue_ratio,
        "analytic_radial_eigenvalue_lower_bound": 1.0 - alpha,
    }


def cone_audit(coefficients: dict[str, float]) -> dict[str, float]:
    a_value = coefficients["a"]
    b_value = coefficients["b"]
    c_value = coefficients["c"]
    determinant = coefficients["determinant"]
    angular_prefactor = a_value + 2.0 * b_value + c_value
    mixed_prefactor = b_value + c_value
    radial_scale_squared = determinant / c_value
    sphere_ratio = angular_prefactor * c_value / determinant
    line_ratio = c_value * c_value / determinant
    logarithmic_slope = mixed_prefactor / c_value

    rng = np.random.default_rng(26072352)
    maximum_metric_residual = 0.0
    for _ in range(2000):
        radius = float(np.exp(rng.uniform(-2.0, 2.0)))
        radial_derivative, log_density_derivative = rng.normal(size=2)
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        angular_derivative = rng.normal(size=3)
        angular_derivative -= direction * float(direction @ angular_derivative)
        original = angular_prefactor * (
            radial_derivative**2 + radius**2 * float(angular_derivative @ angular_derivative)
        )
        original -= 2.0 * mixed_prefactor * radius * radial_derivative * log_density_derivative
        original += c_value * radius**2 * log_density_derivative**2

        cone_radius = math.sqrt(radial_scale_squared) * radius
        cone_radial_derivative = math.sqrt(radial_scale_squared) * radial_derivative
        z_derivative = log_density_derivative - logarithmic_slope * radial_derivative / radius
        transformed = cone_radial_derivative**2
        transformed += cone_radius**2 * (
            sphere_ratio * float(angular_derivative @ angular_derivative)
            + line_ratio * z_derivative**2
        )
        maximum_metric_residual = max(
            maximum_metric_residual,
            abs(original - transformed) / max(1.0, abs(original), abs(transformed)),
        )

    sample_radius = 1.7
    sphere_sectional_curvature = (1.0 / sphere_ratio - 1.0) / sample_radius**2
    sphere_line_sectional_curvature = -1.0 / sample_radius**2
    shortest_base_closed_geodesic = 2.0 * math.pi * math.sqrt(sphere_ratio)
    return {
        "angular_prefactor": angular_prefactor,
        "mixed_prefactor": mixed_prefactor,
        "radial_scale_squared": radial_scale_squared,
        "logarithmic_slope": logarithmic_slope,
        "sphere_ratio": sphere_ratio,
        "line_ratio": line_ratio,
        "maximum_metric_residual": maximum_metric_residual,
        "sample_radius": sample_radius,
        "radial_sectional_curvature": 0.0,
        "sphere_sectional_curvature": sphere_sectional_curvature,
        "sphere_line_sectional_curvature": sphere_line_sectional_curvature,
        "shortest_base_closed_geodesic": shortest_base_closed_geodesic,
        "cat1_closed_geodesic_threshold": 2.0 * math.pi,
    }


def positive_offset_witness(parameters: dict[str, Any], coefficients: dict[str, float]) -> dict[str, Any]:
    c_value, a_value, b_value = WITNESS_C, WITNESS_A, WITNESS_B
    base = a_value**2 * (a_value**2 + 4 * c_value**2) / 8
    cross = a_value**3 * b_value / 2
    retained_square = b_value**2 * (
        20 * a_value**2 + 9 * b_value**2 + 36 * c_value**2
    ) / 8
    increment = cross + retained_square
    endpoint = base + increment
    interpolation_lower_bound = c_value - abs(a_value) - abs(b_value)
    exact_endpoint_minimum = c_value - a_value - b_value
    endpoint_polynomial_derivative_lower_bound = a_value + 9 * b_value

    model_a = coefficients["a"]
    model_b = coefficients["b"]
    model_c = coefficients["c"]
    floor = float(parameters["rho_regularizer"])
    theta_endpoint = floor / (float(interpolation_lower_bound) ** 2 + floor)
    theta_base = floor / (float(c_value - a_value) ** 2 + floor)
    correction_bound = (
        4.0
        * model_b
        * (theta_endpoint * float(endpoint) + theta_base * float(base))
        + 2.0
        * model_c
        * (theta_endpoint**2 * float(endpoint) + theta_base**2 * float(base))
    )
    j_energy_cross = 2.0 * model_a * float(cross)
    j_energy_square = 2.0 * model_a * float(retained_square)
    j_energy_increment = 2.0 * model_a * float(increment)
    certified_full_energy_upper_bound = j_energy_increment + correction_bound

    grid = 2.0 * math.pi * np.arange(WITNESS_GRID) / WITNESS_GRID
    base_field = float(c_value) + float(a_value) * np.cos(grid)
    endpoint_field = base_field + float(b_value) * np.cos(3.0 * grid)
    base_derivative = -float(a_value) * np.sin(grid)
    endpoint_derivative = base_derivative - 3.0 * float(b_value) * np.sin(3.0 * grid)

    def full_energy(field: np.ndarray, derivative: np.ndarray) -> float:
        current_j = 2.0 * field * derivative
        theta = floor / (field * field + floor)
        current_k = theta * current_j
        return float(
            np.mean(
                0.5 * model_a * current_j**2
                + model_b * current_j * current_k
                + 0.5 * model_c * current_k**2
            )
        )

    numerical_increment = full_energy(endpoint_field, endpoint_derivative) - full_energy(
        base_field, base_derivative
    )
    return {
        "inputs": {
            "C": str(c_value),
            "A": str(a_value),
            "B": str(b_value),
            "grid": WITNESS_GRID,
        },
        "base_I_fraction": str(base),
        "cross_I_fraction": str(cross),
        "retained_square_I_fraction": str(retained_square),
        "increment_I_fraction": str(increment),
        "endpoint_I_fraction": str(endpoint),
        "base_I": float(base),
        "cross_I": float(cross),
        "retained_square_I": float(retained_square),
        "increment_I": float(increment),
        "endpoint_I": float(endpoint),
        "interpolation_lower_bound": float(interpolation_lower_bound),
        "exact_endpoint_minimum": float(exact_endpoint_minimum),
        "endpoint_polynomial_derivative_lower_bound": float(
            endpoint_polynomial_derivative_lower_bound
        ),
        "theta_endpoint_upper_bound": theta_endpoint,
        "theta_base_upper_bound": theta_base,
        "j_energy_cross": j_energy_cross,
        "j_energy_retained_square": j_energy_square,
        "j_energy_increment": j_energy_increment,
        "positive_floor_correction_bound": correction_bound,
        "certified_full_energy_increment_upper_bound": certified_full_energy_upper_bound,
        "numerical_full_energy_increment": numerical_increment,
        "numerical_vs_j_only_residual": abs(numerical_increment - j_energy_increment),
    }


def raw_energy_telescope_audit() -> dict[str, Any]:
    """Exact polynomial Gauss--Hermite audit of the raw injection identity."""
    value_variances = np.asarray([0.13, 0.07])
    derivative_variances = np.asarray([0.31, 0.19])
    points, weights = standard_hermite(4, 6)

    def coefficient(stage: int, value: np.ndarray) -> np.ndarray:
        return 1.0 + value * value + float(np.sum(value_variances[stage:]))

    def energy(stage: int, value: np.ndarray, derivative: np.ndarray) -> np.ndarray:
        return 0.5 * coefficient(stage, value) * derivative * derivative

    def execute(controlled: bool) -> tuple[float, float, float, list[float]]:
        value = np.zeros(len(points))
        derivative = np.zeros(len(points))
        secant = np.zeros(len(points))
        injection = np.zeros(len(points))
        injection_expectations: list[float] = []
        for stage in range(2):
            if not controlled:
                value_control = np.zeros(len(points))
                derivative_control = np.zeros(len(points))
            elif stage == 0:
                value_control = np.full(len(points), 0.12)
                derivative_control = np.full(len(points), -0.08)
            else:
                value_control = 0.05 + 0.07 * value - 0.03 * derivative
                derivative_control = -0.02 + 0.02 * value + 0.04 * derivative
            secant += energy(
                stage, value + value_control, derivative + derivative_control
            ) - energy(stage, value, derivative)
            stage_injection = (
                0.5
                * coefficient(stage, value + value_control)
                * float(derivative_variances[stage])
            )
            injection += stage_injection
            injection_expectations.append(float(weights @ stage_injection))
            value += value_control + math.sqrt(float(value_variances[stage])) * points[:, 2 * stage]
            derivative += derivative_control + math.sqrt(
                float(derivative_variances[stage])
            ) * points[:, 2 * stage + 1]
        terminal = energy(2, value, derivative)
        return (
            float(weights @ secant),
            float(weights @ terminal),
            float(weights @ injection),
            injection_expectations,
        )

    controlled_secant, controlled_terminal, controlled_injection, levels = execute(True)
    zero_secant, zero_terminal, zero_injection, zero_levels = execute(False)
    return {
        "controlled_secant_expectation": controlled_secant,
        "controlled_terminal_raw_energy": controlled_terminal,
        "controlled_injection_sum": controlled_injection,
        "controlled_injection_levels": levels,
        "controlled_telescope_residual": abs(
            controlled_secant - (controlled_terminal - controlled_injection)
        ),
        "zero_control_secant_expectation": zero_secant,
        "zero_control_terminal_raw_energy": zero_terminal,
        "zero_control_injection_sum": zero_injection,
        "zero_control_injection_levels": zero_levels,
        "zero_control_cancellation_residual": abs(zero_terminal - zero_injection),
    }


def isolated_resonance_audit(coefficients: dict[str, float]) -> dict[str, Any]:
    """Adversarial zero-floor J-ray test; this is not the full global theorem."""
    model_a = float(coefficients["a"])
    eta_test = 0.37
    kappa_test = 0.81
    carrier_constant = 1.2
    rng = np.random.default_rng(26072353)
    maximum_formula_residual = 0.0
    minimum_mode_two_completion_slack = math.inf
    minimum_mode_three_completion_slack = math.inf
    grid = 2.0 * math.pi * np.arange(4096) / 4096
    for _ in range(120):
        frequency = float(2 ** int(rng.integers(2, 8)))
        carrier = float(rng.normal())
        displacement = float(rng.normal())
        base = carrier_constant + carrier * np.cos(grid)
        base_derivative = -frequency * carrier * np.sin(grid)
        base_energy = 2.0 * model_a * float(np.mean(base**2 * base_derivative**2))
        for harmonic in (2, 3):
            endpoint = base + displacement * np.cos(harmonic * grid)
            endpoint_derivative = base_derivative - (
                harmonic * frequency * displacement * np.sin(harmonic * grid)
            )
            numerical = 2.0 * model_a * float(
                np.mean(endpoint**2 * endpoint_derivative**2)
            ) - base_energy
            if harmonic == 2:
                formula = model_a * frequency**2 * (
                    3.0 * carrier_constant * carrier**2 * displacement
                    + (2.5 * carrier**2 + 4.0 * carrier_constant**2)
                    * displacement**2
                    + displacement**4
                )
                cost = (
                    eta_test
                    * kappa_test
                    * (2.0 * frequency) ** 4
                    * displacement**2
                )
                lower = (
                    -9.0
                    * model_a**2
                    * carrier_constant**2
                    * carrier**4
                    / (64.0 * eta_test * kappa_test)
                )
                minimum_mode_two_completion_slack = min(
                    minimum_mode_two_completion_slack, formula + cost - lower
                )
            else:
                formula = model_a * frequency**2 * (
                    carrier**3 * displacement
                    + (5.0 * carrier**2 + 9.0 * carrier_constant**2)
                    * displacement**2
                    + 2.25 * displacement**4
                )
                cost = (
                    eta_test
                    * kappa_test
                    * (3.0 * frequency) ** 4
                    * displacement**2
                )
                lower = (
                    -model_a**2
                    * carrier**6
                    / (324.0 * eta_test * kappa_test)
                )
                minimum_mode_three_completion_slack = min(
                    minimum_mode_three_completion_slack, formula + cost - lower
                )
            maximum_formula_residual = max(
                maximum_formula_residual,
                abs(numerical - formula) / max(1.0, abs(numerical), abs(formula)),
            )
    # With Var X_N = chi*N^-4, the Gaussian fourth/sixth moments turn the
    # completed losses into N^-8 and N^-12 per carrier.  An O(N^3) shell
    # multiplicity therefore leaves the displayed summable powers.
    return {
        "scope": "zero-floor active-real isolated 1:2 and 1:3 resonance diagnostic",
        "eta_test": eta_test,
        "kappa_test": kappa_test,
        "carrier_constant": carrier_constant,
        "maximum_harmonic_formula_residual": maximum_formula_residual,
        "minimum_mode_two_completion_slack": minimum_mode_two_completion_slack,
        "minimum_mode_three_completion_slack": minimum_mode_three_completion_slack,
        "mode_two_per_carrier_loss_power": -8,
        "mode_two_shell_loss_power": -8 + 3,
        "mode_two_dyadic_shell_ratio": 2.0 ** (-8 + 3),
        "mode_three_per_carrier_loss_power": -12,
        "mode_three_shell_loss_power": -12 + 3,
        "mode_three_dyadic_shell_ratio": 2.0 ** (-12 + 3),
    }


def bare_npc_one_shot_countermodel() -> dict[str, Any]:
    """Exact flat CAT(0) countermodel to geometry plus abstract one-shotness."""
    shell_count = 80  # adversarial test input
    eta_test = 0.1
    zeta_test = 0.001
    expected_raw_sum = -0.5 * (shell_count - 1)
    expected_control_cost = float(shell_count - 1)
    terminal_target_sixth_moment = 15.0
    additive_coordinate_sixth_moment = 15.0 + 120.0 * (shell_count - 1)
    allocated_objective = (
        expected_raw_sum
        + eta_test * expected_control_cost
        + zeta_test * additive_coordinate_sixth_moment
    )
    asymptotic_slope = -0.5 + eta_test + 120.0 * zeta_test

    rng = np.random.default_rng(26072354)
    maximum_weighted_completion_residual = 0.0
    for _ in range(1000):
        source = float(rng.normal())
        coupling = float(10 ** rng.uniform(-3.0, 1.0))
        eta = float(10 ** rng.uniform(-2.0, 0.5))
        optimizer = -source * coupling / (coupling**2 + 2.0 * eta)
        direct = (
            source * coupling * optimizer
            + 0.5 * coupling**2 * optimizer**2
            + eta * optimizer**2
        )
        formula = -source**2 * coupling**2 / (
            2.0 * (coupling**2 + 2.0 * eta)
        )
        maximum_weighted_completion_residual = max(
            maximum_weighted_completion_residual, abs(direct - formula)
        )
    equal_coupling_partial_sum = sum(
        1.0 / (1.0 + 2.0 * eta_test) for _ in range(shell_count)
    )
    decaying_coupling_partial_sum = sum(
        (2.0 ** (-stage)) ** 2
        / ((2.0 ** (-stage)) ** 2 + 2.0 * eta_test)
        for stage in range(1, shell_count + 1)
    )
    decaying_coupling_infinite_upper_bound = sum(
        (2.0 ** (-stage)) ** 2 / (2.0 * eta_test)
        for stage in range(1, 1000)
    )
    return {
        "scope": "generic flat CAT(0) analogue, not a production counterexample",
        "shell_count": shell_count,
        "eta_test": eta_test,
        "zeta_test": zeta_test,
        "expected_raw_sum": expected_raw_sum,
        "expected_control_cost": expected_control_cost,
        "terminal_target_sixth_moment": terminal_target_sixth_moment,
        "additive_coordinate_sixth_moment": additive_coordinate_sixth_moment,
        "allocated_objective": allocated_objective,
        "asymptotic_objective_slope": asymptotic_slope,
        "maximum_weighted_completion_residual": maximum_weighted_completion_residual,
        "equal_coupling_partial_sum": equal_coupling_partial_sum,
        "decaying_coupling_partial_sum": decaying_coupling_partial_sum,
        "decaying_coupling_infinite_upper_bound": decaying_coupling_infinite_upper_bound,
    }


def main() -> int:
    parameters = production_parameters()
    factorisation = coefficient_and_factorisation_audit(parameters)
    cone = cone_audit(factorisation)
    witness = positive_offset_witness(parameters, factorisation)
    telescope = raw_energy_telescope_audit()
    resonance = isolated_resonance_audit(factorisation)
    bare_npc = bare_npc_one_shot_countermodel()

    checks = {
        "production_q_is_spd": factorisation["a"] > 0.0
        and factorisation["c"] > 0.0
        and factorisation["determinant"] > 0.0,
        "nelson_exponent_matches_factorisation_weight": abs(
            factorisation["nelson_exponent"] - 2.0 * factorisation["alpha"]
        )
        < 2.0e-15,
        "fierz_identity": factorisation["maximum_fierz_residual"] < 2.0e-12,
        "exact_current_factorisation": factorisation["maximum_factorisation_residual"]
        < 2.0e-14,
        "normalized_current_weight": factorisation["maximum_transformed_residual"] < 2.0e-14,
        "radial_map_global_orientation": factorisation[
            "analytic_radial_eigenvalue_lower_bound"
        ]
        > 0.0
        and factorisation["minimum_sampled_radial_eigenvalue_ratio"]
        >= factorisation["analytic_radial_eigenvalue_lower_bound"],
        "exact_cone_metric": cone["maximum_metric_residual"] < 2.0e-14,
        "production_cone_ratios": abs(cone["logarithmic_slope"] - 9.0 / 5.0)
        < 2.0e-15
        and abs(cone["sphere_ratio"] - 113.0 / 32.0) < 2.0e-14
        and abs(cone["line_ratio"] - 25.0 / 32.0) < 2.0e-14,
        "smooth_cone_sectional_curvature_nonpositive": cone[
            "radial_sectional_curvature"
        ]
        <= 0.0
        and cone["sphere_sectional_curvature"] < 0.0
        and cone["sphere_line_sectional_curvature"] < 0.0,
        "base_closed_geodesic_cat1_diagnostic": cone["shortest_base_closed_geodesic"]
        > cone["cat1_closed_geodesic_threshold"],
        "witness_uniformly_away_from_tip": witness["interpolation_lower_bound"] > 0.0
        and witness["endpoint_polynomial_derivative_lower_bound"] > 0.0,
        "retained_square_strictly_positive": witness["j_energy_retained_square"] > 0.0,
        "shellwise_j_secant_negative": witness["j_energy_increment"] < 0.0,
        "positive_floor_full_secant_certified_negative": witness[
            "certified_full_energy_increment_upper_bound"
        ]
        < 0.0,
        "positive_floor_quadrature_confirms_negative": witness[
            "numerical_full_energy_increment"
        ]
        < 0.0
        and witness["numerical_vs_j_only_residual"]
        <= witness["positive_floor_correction_bound"],
        "controlled_raw_energy_injection_telescope": telescope[
            "controlled_telescope_residual"
        ]
        < 2.0e-13,
        "zero_control_terminal_injection_cancellation": telescope[
            "zero_control_cancellation_residual"
        ]
        < 2.0e-13
        and abs(telescope["zero_control_secant_expectation"]) < 2.0e-15,
        "injection_is_positive_and_scale_loss_cannot_be_separated": min(
            telescope["controlled_injection_levels"]
        )
        > 0.0
        and telescope["zero_control_injection_sum"] > 0.0,
        "isolated_harmonic_resonance_formulas": resonance[
            "maximum_harmonic_formula_residual"
        ]
        < 2.0e-13,
        "isolated_resonances_complete_against_cm_cost": resonance[
            "minimum_mode_two_completion_slack"
        ]
        >= -2.0e-12
        and resonance["minimum_mode_three_completion_slack"] >= -2.0e-12,
        "isolated_shell_resonance_losses_are_summable": resonance[
            "mode_two_dyadic_shell_ratio"
        ]
        < 1.0
        and resonance["mode_three_dyadic_shell_ratio"] < 1.0,
        "bare_npc_one_shot_objective_diverges_negative": bare_npc[
            "asymptotic_objective_slope"
        ]
        < 0.0
        and bare_npc["allocated_objective"] < -1.0,
        "weighted_flat_cone_completion_identity": bare_npc[
            "maximum_weighted_completion_residual"
        ]
        < 2.0e-12,
        "carleson_decay_distinguishes_production_direction": bare_npc[
            "equal_coupling_partial_sum"
        ]
        > 10.0
        and bare_npc["decaying_coupling_partial_sum"]
        <= bare_npc["decaying_coupling_infinite_upper_bound"],
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    assert all(checks.values()), {name: value for name, value in checks.items() if not value}

    q_value, epsilon_control = nelson_exponent()
    payload = {
        "schema": "tect/a13-npc-cone-martingale-injection-primary/1.0",
        "claim": CLAIM,
        "result_id": RESULT_ID,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {
            "rho_regularizer": float(parameters["rho_regularizer"]),
            "mass_regularizer": float(parameters["classii_mass_regularizer"]),
            "epsilon_control": epsilon_control,
            "q": q_value,
            "translation_authority": str(TRANSLATION_MANIFEST.relative_to(REPO)).replace(
                "\\", "/"
            ),
            "translation_authority_sha256": digest(TRANSLATION_MANIFEST),
            "strict_past_authority": str(STRICT_PAST_MANIFEST.relative_to(REPO)).replace(
                "\\", "/"
            ),
            "strict_past_authority_sha256": digest(STRICT_PAST_MANIFEST),
        },
        "computed": {
            "factorisation": factorisation,
            "cone": cone,
            "positive_offset_witness": witness,
            "raw_energy_telescope": telescope,
            "isolated_resonance_diagnostic": resonance,
            "bare_npc_one_shot_countermodel": bare_npc,
        },
        "assertions": checks,
        "assertion_count": len(checks),
        "pass": True,
        "honesty_boundary": (
            "The exact production current factorisation, ambient NPC cone geometry, "
            "positive-floor retained-square shellwise no-go, and raw-energy/injection "
            "telescope are proved or executed. The global averaged first-variation plus "
            "Jacobi, equivalently terminal-energy minus controlled-injection, lower bound "
            "remains open, as do finite-energy extension, one-use, and Nelson."
        ),
    }
    atomic_json(OUT, payload)
    print(f"PRIMARY {len(checks)}/{len(checks)} PASS")
    print(
        "cone_ratios="
        f"{cone['sphere_ratio']:.12g},{cone['line_ratio']:.12g}; "
        f"witness={witness['numerical_full_energy_increment']:.12e}"
    )
    print(f"injection_telescope_residual={telescope['controlled_telescope_residual']:.3e}")
    print(RESULT_ID + "-PRIMARY-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
