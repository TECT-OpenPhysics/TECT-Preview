#!/usr/bin/env python3
"""Non-importing audit of the A13 NPC-cone/injection reduction.

This route reconstructs the Pauli currents and production coefficients from
JSON, uses exact rational Fourier convolution for the harmonic witness, and
checks the martingale-injection identity with a separate three-shell cubature.
It deliberately imports none of the primary or local Class-II helpers.
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
RESULT_ID = "A13-CLASSII-NPC-CONE-MARTINGALE-INJECTION-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-independent-npc-cone-martingale-injection-reduction/result.json"
)
TRANSLATION_MANIFEST = (
    REPO / "claims" / CLAIM / "classii_translation_model_reduction_manifest.json"
)
STRICT_PAST_MANIFEST = (
    REPO / "claims" / CLAIM / "classii_strict_past_signed_causal_reduction_manifest.json"
)

WITNESS_C = Fraction(101, 100)
WITNESS_A = Fraction(1, 1)
WITNESS_B = Fraction(-3, 400)


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


def authorities() -> tuple[dict[str, Any], dict[str, Any]]:
    translation = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / translation["authority"]["a1_manifest"]["path"]
    strict = json.loads(STRICT_PAST_MANIFEST.read_text(encoding="utf-8"))
    return json.loads(a1_path.read_text(encoding="utf-8"))["parameters"], strict


def fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def exact_model_arithmetic(
    parameters: dict[str, Any], strict: dict[str, Any]
) -> dict[str, Any]:
    denominator = fraction(parameters["M_X"]) ** 2 + fraction(
        parameters["classii_mass_regularizer"]
    )
    a_value = (
        fraction(parameters["cJJ"]) * fraction(parameters["alpha_X"]) ** 2 / denominator
    )
    b_value = (
        fraction(parameters["cJK"])
        * fraction(parameters["alpha_X"])
        * fraction(parameters["beta_X"])
        / denominator
    )
    c_value = (
        fraction(parameters["cKK"]) * fraction(parameters["beta_X"]) ** 2 / denominator
    )
    determinant = a_value * c_value - b_value * b_value
    epsilon = fraction(strict["audit"]["epsilon_control"])
    q_value = 1 / (2 * epsilon)
    alpha = c_value / (b_value + c_value)
    return {
        "denominator": str(denominator),
        "a": float(a_value),
        "b": float(b_value),
        "c": float(c_value),
        "determinant": float(determinant),
        "alpha_fraction": str(alpha),
        "q_fraction": str(q_value),
        "two_alpha_fraction": str(2 * alpha),
        "residual_coefficient_fraction": str(determinant / c_value),
        "transformed_coefficient_fraction": str(c_value * (1 + b_value / c_value) ** 2),
        "logarithmic_slope_fraction": str((b_value + c_value) / c_value),
        "sphere_ratio_fraction": str((a_value + 2 * b_value + c_value) * c_value / determinant),
        "line_ratio_fraction": str(c_value * c_value / determinant),
        "radial_scale_squared": float(determinant / c_value),
    }


def pauli_and_cone_audit(parameters: dict[str, Any], arithmetic: dict[str, Any]) -> dict[str, float]:
    pauli = (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )
    a_value = float(arithmetic["a"])
    b_value = float(arithmetic["b"])
    c_value = float(arithmetic["c"])
    determinant = float(arithmetic["determinant"])
    alpha = float(Fraction(arithmetic["alpha_fraction"]))
    q_value = float(Fraction(arithmetic["q_fraction"]))
    floor = float(parameters["rho_regularizer"])
    residual_coefficient = determinant / c_value
    transformed_coefficient = c_value * (1.0 + b_value / c_value) ** 2

    rng = np.random.default_rng(26072361)
    maximum_fierz_residual = 0.0
    maximum_factorisation_residual = 0.0
    maximum_cone_residual = 0.0
    maximum_radial_finite_difference_residual = 0.0
    for _ in range(800):
        state = rng.normal(size=3) + 1j * rng.normal(size=3)
        tangent = rng.normal(size=3) + 1j * rng.normal(size=3)
        rho = float(np.real(np.vdot(state, state)))
        density = rho + floor
        doublet_density = float(abs(state[0]) ** 2 + abs(state[1]) ** 2)
        moments = np.asarray(
            [float(np.real(np.vdot(state, generator @ state))) for generator in pauli]
        )
        derivatives = np.asarray(
            [2.0 * float(np.real(np.vdot(tangent, generator @ state))) for generator in pauli]
        )
        maximum_fierz_residual = max(
            maximum_fierz_residual, abs(float(moments @ moments) - doublet_density**2)
        )
        d_log_density = 2.0 * float(np.real(np.vdot(state, tangent))) / density
        k_current = derivatives - moments * d_log_density
        normalized = derivatives - alpha * moments * d_log_density
        direct = (
            a_value * float(derivatives @ derivatives)
            + 2.0 * b_value * float(derivatives @ k_current)
            + c_value * float(k_current @ k_current)
        )
        factored = residual_coefficient * float(derivatives @ derivatives)
        factored += transformed_coefficient * density**q_value * float(
            (density ** (-alpha) * normalized) @ (density ** (-alpha) * normalized)
        )
        maximum_factorisation_residual = max(
            maximum_factorisation_residual,
            abs(direct - factored) / max(1.0, abs(direct), abs(factored)),
        )

        radius = max(float(np.linalg.norm(moments)), 1.0e-10)
        radial_derivative = float(moments @ derivatives) / radius
        angular_squared = max(
            0.0, float(derivatives @ derivatives) - radial_derivative**2
        ) / radius**2
        angular_prefactor = a_value + 2.0 * b_value + c_value
        mixed_prefactor = b_value + c_value
        original = angular_prefactor * (radial_derivative**2 + radius**2 * angular_squared)
        original -= 2.0 * mixed_prefactor * radius * radial_derivative * d_log_density
        original += c_value * radius**2 * d_log_density**2
        cone_radius = math.sqrt(residual_coefficient) * radius
        cone_derivative = math.sqrt(residual_coefficient) * radial_derivative
        z_derivative = d_log_density - (mixed_prefactor / c_value) * radial_derivative / radius
        transformed_metric = cone_derivative**2 + cone_radius**2 * (
            float(Fraction(arithmetic["sphere_ratio_fraction"])) * angular_squared
            + float(Fraction(arithmetic["line_ratio_fraction"])) * z_derivative**2
        )
        maximum_cone_residual = max(
            maximum_cone_residual,
            abs(original - transformed_metric) / max(1.0, abs(original), abs(transformed_metric)),
        )

        step = 2.0e-6 / max(1.0, float(np.linalg.norm(tangent)))

        def radial_transform(value: np.ndarray) -> np.ndarray:
            local_density = float(np.real(np.vdot(value, value))) + floor
            return value * local_density ** (-alpha / 2.0)

        finite_difference = (
            radial_transform(state + step * tangent)
            - radial_transform(state - step * tangent)
        ) / (2.0 * step)
        analytic = density ** (-alpha / 2.0) * (
            tangent - alpha * state * float(np.real(np.vdot(state, tangent))) / density
        )
        maximum_radial_finite_difference_residual = max(
            maximum_radial_finite_difference_residual,
            float(np.linalg.norm(finite_difference - analytic))
            / max(1.0, float(np.linalg.norm(analytic))),
        )

    sphere_ratio = float(Fraction(arithmetic["sphere_ratio_fraction"]))
    return {
        "maximum_fierz_residual": maximum_fierz_residual,
        "maximum_factorisation_residual": maximum_factorisation_residual,
        "maximum_cone_residual": maximum_cone_residual,
        "maximum_radial_finite_difference_residual": maximum_radial_finite_difference_residual,
        "sphere_plane_curvature_coefficient": 1.0 / sphere_ratio - 1.0,
        "sphere_line_curvature_coefficient": -1.0,
        "base_sphere_radius": math.sqrt(sphere_ratio),
        "base_shortest_closed_geodesic": 2.0 * math.pi * math.sqrt(sphere_ratio),
    }


def derivative_product(field: dict[int, Fraction]) -> dict[int, Fraction]:
    """Fourier coefficients without the common imaginary unit for u*u_x."""
    result: dict[int, Fraction] = {}
    for first_mode, first_value in field.items():
        for second_mode, second_value in field.items():
            output_mode = first_mode + second_mode
            result[output_mode] = result.get(output_mode, Fraction()) + (
                first_value * second_mode * second_value
            )
    return {mode: value for mode, value in result.items() if value}


def exact_fourier_witness(parameters: dict[str, Any], arithmetic: dict[str, Any]) -> dict[str, Any]:
    base_field = {
        0: WITNESS_C,
        1: WITNESS_A / 2,
        -1: WITNESS_A / 2,
    }
    endpoint_field = dict(base_field)
    endpoint_field[3] = WITNESS_B / 2
    endpoint_field[-3] = WITNESS_B / 2
    base_product = derivative_product(base_field)
    endpoint_product = derivative_product(endpoint_field)
    modes = set(base_product) | set(endpoint_product)
    displacement = {
        mode: endpoint_product.get(mode, Fraction()) - base_product.get(mode, Fraction())
        for mode in modes
    }
    base = sum((value * value for value in base_product.values()), Fraction())
    cross = 2 * sum(
        (base_product.get(mode, Fraction()) * displacement.get(mode, Fraction()) for mode in modes),
        Fraction(),
    )
    square = sum((value * value for value in displacement.values()), Fraction())
    increment = cross + square
    endpoint = base + increment

    model_a = float(arithmetic["a"])
    model_b = float(arithmetic["b"])
    model_c = float(arithmetic["c"])
    floor = float(parameters["rho_regularizer"])
    lower_endpoint = WITNESS_C - abs(WITNESS_A) - abs(WITNESS_B)
    lower_base = WITNESS_C - abs(WITNESS_A)
    theta_endpoint = floor / (float(lower_endpoint) ** 2 + floor)
    theta_base = floor / (float(lower_base) ** 2 + floor)
    correction_bound = (
        4.0 * model_b * (theta_endpoint * float(endpoint) + theta_base * float(base))
        + 2.0
        * model_c
        * (theta_endpoint**2 * float(endpoint) + theta_base**2 * float(base))
    )
    j_increment = 2.0 * model_a * float(increment)

    nodes, weights = np.polynomial.legendre.leggauss(640)
    grid = math.pi * (nodes + 1.0)
    normalized_weights = weights / 2.0

    def energy(include_third: bool) -> float:
        field = float(WITNESS_C) + float(WITNESS_A) * np.cos(grid)
        derivative = -float(WITNESS_A) * np.sin(grid)
        if include_third:
            field += float(WITNESS_B) * np.cos(3.0 * grid)
            derivative -= 3.0 * float(WITNESS_B) * np.sin(3.0 * grid)
        current_j = 2.0 * field * derivative
        current_k = floor * current_j / (field * field + floor)
        density = (
            0.5 * model_a * current_j**2
            + model_b * current_j * current_k
            + 0.5 * model_c * current_k**2
        )
        return float(normalized_weights @ density)

    quadrature_increment = energy(True) - energy(False)
    return {
        "base_fraction": str(base),
        "cross_fraction": str(cross),
        "square_fraction": str(square),
        "increment_fraction": str(increment),
        "endpoint_fraction": str(endpoint),
        "base": float(base),
        "cross": float(cross),
        "square": float(square),
        "increment": float(increment),
        "endpoint": float(endpoint),
        "interpolation_lower_bound": float(lower_endpoint),
        "exact_endpoint_minimum": float(WITNESS_C - WITNESS_A - WITNESS_B),
        "j_energy_increment": j_increment,
        "positive_floor_correction_bound": correction_bound,
        "certified_full_energy_increment_upper_bound": j_increment + correction_bound,
        "legendre_full_energy_increment": quadrature_increment,
        "legendre_vs_j_only_residual": abs(quadrature_increment - j_increment),
    }


def hermite(dimension: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * dimension, dtype=np.int16).reshape(dimension, -1).T
    return (
        math.sqrt(2.0) * nodes[indices],
        np.prod(weights[indices], axis=1) / math.pi ** (dimension / 2.0),
    )


def independent_injection_telescope() -> dict[str, Any]:
    value_variances = np.asarray([0.09, 0.06, 0.025])
    derivative_variances = np.asarray([0.21, 0.14, 0.08])
    points, weights = hermite(6, 5)

    def backward_coefficient(stage: int, value: np.ndarray) -> np.ndarray:
        return 0.7 + 1.3 * value * value + 1.3 * float(np.sum(value_variances[stage:]))

    def energy(stage: int, value: np.ndarray, derivative: np.ndarray) -> np.ndarray:
        return 0.5 * backward_coefficient(stage, value) * derivative * derivative

    value = np.zeros(len(points))
    derivative = np.zeros(len(points))
    secants = np.zeros(len(points))
    injections = np.zeros(len(points))
    level_means: list[float] = []
    for stage in range(3):
        if stage == 0:
            value_control = np.full(len(points), -0.09)
            derivative_control = np.full(len(points), 0.055)
        elif stage == 1:
            value_control = 0.025 - 0.04 * value + 0.015 * derivative
            derivative_control = -0.018 + 0.03 * value - 0.02 * derivative
        else:
            value_control = -0.012 + 0.02 * value + 0.01 * derivative
            derivative_control = 0.009 - 0.015 * value + 0.025 * derivative
        secants += energy(
            stage, value + value_control, derivative + derivative_control
        ) - energy(stage, value, derivative)
        level = (
            0.5
            * backward_coefficient(stage, value + value_control)
            * float(derivative_variances[stage])
        )
        injections += level
        level_means.append(float(weights @ level))
        value += value_control + math.sqrt(float(value_variances[stage])) * points[:, 2 * stage]
        derivative += derivative_control + math.sqrt(
            float(derivative_variances[stage])
        ) * points[:, 2 * stage + 1]
    terminal = energy(3, value, derivative)
    secant_mean = float(weights @ secants)
    terminal_mean = float(weights @ terminal)
    injection_mean = float(weights @ injections)
    return {
        "secant_expectation": secant_mean,
        "terminal_raw_energy": terminal_mean,
        "injection_sum": injection_mean,
        "injection_levels": level_means,
        "telescope_residual": abs(secant_mean - (terminal_mean - injection_mean)),
    }


def independent_resonance_audit(arithmetic: dict[str, Any]) -> dict[str, Any]:
    """Separate quadrature check of the isolated 1:2/1:3 completion bounds."""
    model_a = float(arithmetic["a"])
    eta_test = 0.29
    kappa_test = 1.07
    carrier_constant = 0.85
    nodes, weights = np.polynomial.legendre.leggauss(384)
    angle = math.pi * (nodes + 1.0)
    normalized_weights = weights / 2.0
    rng = np.random.default_rng(26072362)
    maximum_formula_residual = 0.0
    minimum_completion_slack = math.inf
    for _ in range(96):
        frequency = float(2 ** int(rng.integers(1, 7)))
        carrier = float(rng.normal())
        displacement = float(rng.normal())
        base = carrier_constant + carrier * np.cos(angle)
        base_derivative = -frequency * carrier * np.sin(angle)
        base_energy = 2.0 * model_a * float(
            normalized_weights @ (base**2 * base_derivative**2)
        )
        for harmonic in (2, 3):
            endpoint = base + displacement * np.cos(harmonic * angle)
            endpoint_derivative = base_derivative - (
                harmonic * frequency * displacement * np.sin(harmonic * angle)
            )
            direct = 2.0 * model_a * float(
                normalized_weights @ (endpoint**2 * endpoint_derivative**2)
            ) - base_energy
            if harmonic == 2:
                formula = model_a * frequency**2 * (
                    3.0 * carrier_constant * carrier**2 * displacement
                    + (2.5 * carrier**2 + 4.0 * carrier_constant**2)
                    * displacement**2
                    + displacement**4
                )
                lower = (
                    -9.0
                    * model_a**2
                    * carrier_constant**2
                    * carrier**4
                    / (64.0 * eta_test * kappa_test)
                )
            else:
                formula = model_a * frequency**2 * (
                    carrier**3 * displacement
                    + (5.0 * carrier**2 + 9.0 * carrier_constant**2)
                    * displacement**2
                    + 2.25 * displacement**4
                )
                lower = (
                    -model_a**2
                    * carrier**6
                    / (324.0 * eta_test * kappa_test)
                )
            cost = (
                eta_test
                * kappa_test
                * (harmonic * frequency) ** 4
                * displacement**2
            )
            maximum_formula_residual = max(
                maximum_formula_residual,
                abs(direct - formula) / max(1.0, abs(direct), abs(formula)),
            )
            minimum_completion_slack = min(
                minimum_completion_slack, formula + cost - lower
            )
    per_carrier_powers = {"mode_two": -2 * 4, "mode_three": -3 * 4}
    shell_powers = {
        key: value + 3 for key, value in per_carrier_powers.items()
    }
    return {
        "scope": "zero-floor active-real isolated resonance diagnostic only",
        "maximum_gauss_legendre_formula_residual": maximum_formula_residual,
        "minimum_completion_slack": minimum_completion_slack,
        "per_carrier_loss_powers": per_carrier_powers,
        "shell_loss_powers": shell_powers,
        "dyadic_shell_ratios": {
            key: 2.0**value for key, value in shell_powers.items()
        },
    }


def independent_flat_cone_countermodel() -> dict[str, Any]:
    shell_count = 57
    eta_test = 0.12
    zeta_test = 0.001
    nodes, weights = np.polynomial.hermite.hermgauss(8)
    gaussian = math.sqrt(2.0) * nodes
    normalized_weights = weights / math.sqrt(math.pi)
    second_moment = float(normalized_weights @ gaussian**2)
    sixth_moment = float(normalized_weights @ gaussian**6)
    raw_sum = -0.5 * second_moment * (shell_count - 1)
    control_cost = second_moment * (shell_count - 1)
    additive_coordinate_sixth_moment = sixth_moment + 8.0 * sixth_moment * (
        shell_count - 1
    )
    objective = (
        raw_sum
        + eta_test * control_cost
        + zeta_test * additive_coordinate_sixth_moment
    )

    rng = np.random.default_rng(26072363)
    maximum_completion_residual = 0.0
    for _ in range(700):
        source = float(rng.normal())
        coupling = float(np.exp(rng.uniform(-5.0, 2.0)))
        eta = float(np.exp(rng.uniform(-4.0, 1.0)))
        optimizer = -source * coupling / (coupling**2 + 2.0 * eta)
        evaluated = (
            source * coupling * optimizer
            + (0.5 * coupling**2 + eta) * optimizer**2
        )
        oracle = -0.5 * source**2 * coupling**2 / (
            coupling**2 + 2.0 * eta
        )
        maximum_completion_residual = max(
            maximum_completion_residual, abs(evaluated - oracle)
        )
    equal_sum = shell_count / (1.0 + 2.0 * eta_test)
    decaying_sum = sum(
        3.0 ** (-2 * stage)
        / (3.0 ** (-2 * stage) + 2.0 * eta_test)
        for stage in range(1, shell_count + 1)
    )
    geometric_upper_bound = sum(
        3.0 ** (-2 * stage) / (2.0 * eta_test)
        for stage in range(1, 1000)
    )
    return {
        "scope": "independent generic flat-cone analogue only",
        "shell_count": shell_count,
        "second_moment": second_moment,
        "sixth_moment": sixth_moment,
        "additive_coordinate_sixth_moment": additive_coordinate_sixth_moment,
        "raw_sum": raw_sum,
        "control_cost": control_cost,
        "allocated_objective": objective,
        "asymptotic_slope": (
            -0.5 * second_moment
            + eta_test * second_moment
            + 8.0 * zeta_test * sixth_moment
        ),
        "maximum_weighted_completion_residual": maximum_completion_residual,
        "equal_coupling_sum": equal_sum,
        "decaying_coupling_sum": decaying_sum,
        "geometric_upper_bound": geometric_upper_bound,
    }


def main() -> int:
    parameters, strict = authorities()
    arithmetic = exact_model_arithmetic(parameters, strict)
    geometry = pauli_and_cone_audit(parameters, arithmetic)
    witness = exact_fourier_witness(parameters, arithmetic)
    telescope = independent_injection_telescope()
    resonance = independent_resonance_audit(arithmetic)
    flat_cone = independent_flat_cone_countermodel()

    checks = {
        "exact_alpha": arithmetic["alpha_fraction"] == "5/9",
        "nelson_weight_matches": arithmetic["q_fraction"]
        == arithmetic["two_alpha_fraction"]
        == "10/9",
        "exact_cone_ratios": arithmetic["logarithmic_slope_fraction"] == "9/5"
        and arithmetic["sphere_ratio_fraction"] == "113/32"
        and arithmetic["line_ratio_fraction"] == "25/32",
        "production_q_spd": arithmetic["a"] > 0.0
        and arithmetic["c"] > 0.0
        and arithmetic["determinant"] > 0.0,
        "complex_pauli_fierz": geometry["maximum_fierz_residual"] < 2.0e-12,
        "complex_current_factorisation": geometry["maximum_factorisation_residual"]
        < 3.0e-14,
        "independent_cone_metric": geometry["maximum_cone_residual"] < 3.0e-14,
        "radial_transform_finite_difference": geometry[
            "maximum_radial_finite_difference_residual"
        ]
        < 2.0e-9,
        "cone_curvatures_nonpositive": geometry["sphere_plane_curvature_coefficient"]
        < 0.0
        and geometry["sphere_line_curvature_coefficient"] < 0.0,
        "cat1_closed_geodesic_diagnostic": geometry["base_shortest_closed_geodesic"]
        > 2.0 * math.pi,
        "exact_fourier_witness_values": witness["base_fraction"] == "12701/20000"
        and witness["cross_fraction"] == "-3/800"
        and witness["square_fraction"] == "81682713/204800000000"
        and witness["increment_fraction"] == "-686317287/204800000000",
        "witness_avoids_cone_tip": witness["interpolation_lower_bound"] > 0.0,
        "retained_square_positive_but_secant_negative": witness["square"] > 0.0
        and witness["increment"] < 0.0,
        "production_floor_preserves_negative_witness": witness[
            "certified_full_energy_increment_upper_bound"
        ]
        < 0.0
        and witness["legendre_full_energy_increment"] < 0.0
        and witness["legendre_vs_j_only_residual"]
        <= witness["positive_floor_correction_bound"],
        "independent_three_shell_injection_telescope": telescope["telescope_residual"]
        < 3.0e-13,
        "injection_levels_positive": min(telescope["injection_levels"]) > 0.0,
        "independent_isolated_resonance_formulas": resonance[
            "maximum_gauss_legendre_formula_residual"
        ]
        < 3.0e-12,
        "independent_resonance_completion": resonance["minimum_completion_slack"]
        >= -3.0e-12,
        "independent_resonance_shell_powers_summable": max(
            resonance["dyadic_shell_ratios"].values()
        )
        < 1.0,
        "independent_flat_cone_moments": abs(flat_cone["second_moment"] - 1.0)
        < 2.0e-14
        and abs(flat_cone["sixth_moment"] - 15.0) < 2.0e-13,
        "independent_bare_one_shot_failure": flat_cone["asymptotic_slope"] < 0.0
        and flat_cone["allocated_objective"] < -1.0,
        "independent_weighted_completion": flat_cone[
            "maximum_weighted_completion_residual"
        ]
        < 2.0e-12,
        "independent_carleson_decay": flat_cone["equal_coupling_sum"] > 10.0
        and flat_cone["decaying_coupling_sum"]
        <= flat_cone["geometric_upper_bound"],
    }
    checks = {name: bool(value) for name, value in checks.items()}
    assert all(checks.values()), {name: value for name, value in checks.items() if not value}

    payload = {
        "schema": "tect/a13-npc-cone-martingale-injection-independent/1.0",
        "claim": CLAIM,
        "result_id": RESULT_ID,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {
            "rho_regularizer": float(parameters["rho_regularizer"]),
            "translation_authority_sha256": digest(TRANSLATION_MANIFEST),
            "strict_past_authority_sha256": digest(STRICT_PAST_MANIFEST),
            "independence": "No primary or local Class-II helper is imported.",
        },
        "computed": {
            "exact_model_arithmetic": arithmetic,
            "geometry": geometry,
            "positive_offset_witness": witness,
            "raw_energy_telescope": telescope,
            "isolated_resonance_diagnostic": resonance,
            "flat_cone_one_shot_countermodel": flat_cone,
        },
        "assertions": checks,
        "assertion_count": len(checks),
        "pass": True,
        "honesty_boundary": (
            "Independent finite-dimensional and exact-rational audit of the current "
            "factorisation, cone ratios, retained-square no-go, and injection telescope. "
            "It does not establish the global martingale-injection lower bound."
        ),
    }
    atomic_json(OUT, payload)
    print(f"INDEPENDENT {len(checks)}/{len(checks)} PASS")
    print(
        f"ratios={arithmetic['sphere_ratio_fraction']},{arithmetic['line_ratio_fraction']}; "
        f"witness={witness['legendre_full_energy_increment']:.12e}"
    )
    print(f"injection_telescope_residual={telescope['telescope_residual']:.3e}")
    print(RESULT_ID + "-INDEPENDENT-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
