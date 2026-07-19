#!/usr/bin/env python3
"""Explicit positive-time smoothing and dealiased Galerkin majorants for P3.

The calculation turns the qualitative P2 smoothing route into a completely
specified (deliberately very conservative) constant chain.  It uses two
quantitative endpoint-cancellation steps, H2 -> H4 and H4 -> H6, explicit
Fourier embedding/product bounds, and explicit derivative envelopes for the
Class-II rational coefficients at the pinned positive density floor.

For merely H2 initial data, the finite-time exact-Galerkin statement is
restarted at positive time tau with initial value P_N u(tau).  No algebraic
rate from t=0 and no historical collocation-solver certificate is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, getcontext
from pathlib import Path
from typing import Any

__version__ = "1.1.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]

getcontext().prec = 90
D = Decimal

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
P2_MANIFEST = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "full_pde_manifest.json"
ENERGY_RESULT = CLAIM / "runs" / "2026-07-17-energy-ball-envelope" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-quantitative-majorant-repair" / "result.json"

# Directed decimal enclosures used in upper bounds.  PI_LO and E_LO are below
# the mathematical constants, so divisions by them remain conservative.
PI_LO = D("3.14159265358979323846264338327950288")
PI_UP = D("3.14159265358979323846264338327950289")
E_LO = D("2.71828182845904523536028747135266249")
LN10_LO = D("2.30258509299404568401799145468436420")
NUMERIC_PAD = D("1e-60")


def dec(value: Any) -> Decimal:
    return D(str(value))


def padded(value: Decimal) -> Decimal:
    """Add a relative safety margin far above the 90-digit arithmetic ulp."""
    if value < 0:
        raise ValueError("majorant arithmetic must be nonnegative")
    return value * (D(1) + NUMERIC_PAD) + NUMERIC_PAD


def powd(value: Decimal, exponent: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("positive base required")
    return padded((exponent * value.ln()).exp())


def sqrt(value: Decimal) -> Decimal:
    return padded(value.sqrt())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sci(value: Decimal) -> str:
    if value == 0:
        return "0.00000000000000E+0"
    exponent = value.adjusted()
    quantum = D(1).scaleb(exponent - 14)
    rounded = value.quantize(quantum, rounding=ROUND_CEILING)
    return format(rounded, ".14E")


def sci_lower(value: Decimal) -> str:
    if value == 0:
        return "0.00000000000000E+0"
    exponent = value.adjusted()
    quantum = D(1).scaleb(exponent - 14)
    rounded = value.quantize(quantum, rounding=ROUND_FLOOR)
    return format(rounded, ".14E")


def log10(value: Decimal) -> Decimal:
    return padded(value.ln() / LN10_LO)


def binom(n: int, k: int) -> Decimal:
    return D(math.comb(n, k))


def convolution_derivative(left: list[Decimal], right: list[Decimal], order: int) -> Decimal:
    return sum((binom(order, index) * left[index] * right[order - index] for index in range(order + 1)), D(0))


def lattice_embedding_upper(periods: list[Decimal], cutoff: int) -> tuple[Decimal, Decimal]:
    l_max = max(periods)
    scale4 = powd(D(2) * PI_LO / l_max, D(4))
    finite = D(1)
    for shell in range(1, cutoff + 1):
        m = D(shell)
        finite += (D(24) * m * m + D(2)) / (D(1) + scale4 * powd(m, D(4)))
    tail = D(24) / (scale4 * D(cutoff)) + D(2) / (D(3) * scale4 * powd(D(cutoff), D(3)))
    return padded(finite + tail), padded(tail)


def gradient_l4_series_upper(periods: list[Decimal], cutoff: int) -> tuple[Decimal, Decimal]:
    """Upper bound for sum k_i^4/(1+|k|^4)^2, uniformly in i."""
    l_max = max(periods)
    scale4 = powd(D(2) * PI_LO / l_max, D(4))
    finite = D(0)
    for shell in range(1, cutoff + 1):
        m = D(shell)
        numerator = scale4 * powd(m, D(4))
        finite += (D(24) * m * m + D(2)) * numerator / powd(D(1) + scale4 * powd(m, D(4)), D(2))
    tail = D(24) / (scale4 * D(cutoff)) + D(2) / (D(3) * scale4 * powd(D(cutoff), D(3)))
    return padded(finite + tail), padded(tail)


def coefficient_derivatives(amplitude: Decimal, epsilon: Decimal, a_value: Decimal, b_value: Decimal, c_value: Decimal, generators: int) -> dict[str, list[Decimal]]:
    """Return explicit 0..3 derivative envelopes for q, A_J, A_K and B."""
    max_order = 3
    moment = [amplitude * amplitude, D(2) * amplitude, D(2), D(0)]
    inverse = [D(0)] * (max_order + 1)
    for order in range(max_order + 1):
        inverse[order] = padded(D(math.factorial(order)) * powd(D(2) * amplitude + D(2), D(order)) / powd(epsilon, D(order + 1)))
    q = [D(1)]
    for order in range(1, max_order + 1):
        raw = sum((binom(order, index) * moment[index] * inverse[order - index] for index in range(min(order, 2) + 1)), D(0))
        q.append(padded(raw))
    aj = [D(2) * amplitude, D(2), D(0), D(0)]
    arho = list(aj)
    ak: list[Decimal] = []
    for order in range(max_order + 1):
        ak.append(padded(aj[order] + convolution_derivative(q, arho, order)))
    bmetric: list[Decimal] = []
    for order in range(max_order + 1):
        jj = convolution_derivative(aj, aj, order)
        jk = convolution_derivative(aj, ak, order) + convolution_derivative(ak, aj, order)
        kk = convolution_derivative(ak, ak, order)
        bmetric.append(padded(D(generators) * (abs(a_value) * jj + abs(b_value) * jk + abs(c_value) * kk)))
    return {"q": q, "aj": aj, "ak": ak, "bmetric": bmetric}


def nonlinear_majorants(
    m2: Decimal,
    m4: Decimal | None,
    embedding: Decimal,
    gradient_l4: Decimal,
    algebra_h2: Decimal,
    volume: Decimal,
    lambda_value: Decimal,
    gamma_value: Decimal,
    bmetric: list[Decimal],
    contraction_factor: Decimal,
) -> dict[str, Decimal]:
    pointwise = embedding * m2
    potential_l2 = abs(lambda_value) * pointwise * pointwise * m2 + gamma_value * powd(pointwise, D(4)) * m2
    k0_classii = contraction_factor * (bmetric[0] * m2 + bmetric[1] * D(3) * gradient_l4 * gradient_l4 * m2 * m2)
    k0 = padded(potential_l2 + k0_classii)
    potential_lip0 = D(3) * abs(lambda_value) * pointwise * pointwise + D(5) * gamma_value * powd(pointwise, D(4))
    lip0_classii = contraction_factor * (
        bmetric[0]
        + bmetric[1] * embedding * m2 * m2
        + bmetric[2] * embedding * D(3) * gradient_l4 * gradient_l4 * m2 * m2
        + D(2) * bmetric[1] * D(3) * gradient_l4 * gradient_l4 * m2
    )
    lip0 = padded(potential_lip0 + lip0_classii)
    result = {"K0": k0, "Lip0": lip0}
    if m4 is None:
        return result

    sqrt_volume = sqrt(volume)
    b_h2 = bmetric[0] * sqrt_volume + bmetric[1] * algebra_h2 * m2 + bmetric[2] * powd(algebra_h2 * m2, D(2))
    db_h2 = bmetric[1] * sqrt_volume + bmetric[2] * algebra_h2 * m2 + bmetric[3] * powd(algebra_h2 * m2, D(2))
    potential_h2 = abs(lambda_value) * powd(algebra_h2, D(2)) * powd(m2, D(3)) + gamma_value * powd(algebra_h2, D(4)) * powd(m2, D(5))
    k2_classii = contraction_factor * (algebra_h2 * b_h2 * m4 + powd(algebra_h2, D(2)) * db_h2 * m4 * m4)
    k2 = padded(potential_h2 + k2_classii)

    b_lip_h2 = algebra_h2 * (bmetric[1] * sqrt_volume + bmetric[2] * algebra_h2 * m2 + bmetric[3] * powd(algebra_h2 * m2, D(2)))
    db_lip_h2 = algebra_h2 * (
        bmetric[2] * sqrt_volume
        + bmetric[3] * powd(D(1) + algebra_h2 * m2, D(2))
    )
    potential_lip2 = D(3) * abs(lambda_value) * powd(algebra_h2, D(2)) * powd(m2, D(2)) + D(5) * gamma_value * powd(algebra_h2, D(4)) * powd(m2, D(4))
    lip2_classii = contraction_factor * (
        algebra_h2 * (b_lip_h2 * m4 + b_h2)
        + powd(algebra_h2, D(2)) * (db_lip_h2 * m4 * m4 + D(2) * db_h2 * m4)
    )
    result.update({"B_H2": padded(b_h2), "DB_H2": padded(db_h2), "K2": k2, "Lip2": padded(potential_lip2 + lip2_classii)})
    return result


def energy_upper_on_h2_ball(
    radius: Decimal,
    linear_upper: Decimal,
    quartic_upper: Decimal,
    sextic_upper: Decimal,
) -> Decimal:
    return padded(
        D("0.5") * linear_upper * radius * radius
        + quartic_upper * powd(radius, D(4))
        + sextic_upper * powd(radius, D(6))
    )


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    p2 = json.loads(P2_MANIFEST.read_text(encoding="utf-8"))
    energy = json.loads(ENERGY_RESULT.read_text(encoding="utf-8"))
    params = p1["parameters"]
    stage = manifest["stage8_quantitative_majorant"]
    assertions: list[dict[str, Any]] = []

    for key, path in (("p1_manifest", P1_MANIFEST), ("p2_manifest", P2_MANIFEST)):
        actual = sha256(path)
        expected = manifest["authority"][key]["sha256"]
        check(f"{key}_hash", actual == expected, {"actual": actual, "expected": expected}, assertions)
    check("energy_ball_result_passed", energy.get("verdict") == "A3-FULL-ENERGY-BALL-ENVELOPE-PASS", energy.get("verdict"), assertions)

    periods = [dec(params[name]) for name in ("Lx", "Ly", "Lz")]
    volume = periods[0] * periods[1] * periods[2]
    cutoff = int(stage["embedding_shell_cutoff"])
    series, series_tail = lattice_embedding_upper(periods, cutoff)
    grad_series, grad_tail = gradient_l4_series_upper(periods, cutoff)
    embedding = sqrt(series / volume)
    gradient_l4 = powd(grad_series / volume, D("0.25"))
    algebra_h2 = D(8) * embedding

    epsilon = dec(params["rho_regularizer"])
    denominator = dec(params["M_X"]) ** 2 + dec(params["classii_mass_regularizer"])
    a_value = dec(params["cJJ"]) * dec(params["alpha_X"]) ** 2 / denominator
    b_value = dec(params["cJK"]) * dec(params["alpha_X"]) * dec(params["beta_X"]) / denominator
    c_value = dec(params["cKK"]) * dec(params["beta_X"]) ** 2 / denominator
    lambda_value = dec(params["lambda"])
    gamma_value = dec(params["gamma"])
    c_linear = dec(p2["production_conditions"]["linear"]["h2_coercivity_constant"])
    internal_upper = max(dec(value) for value in params["family_masses"]) + dec(params["k_lock"])
    c_linear_upper = padded(dec(params["Y"]) + abs(dec(params["Z"])) / D(2) + dec(params["r"]) + internal_upper)
    young_constant = padded(abs(lambda_value) ** 3 / (D(3) * gamma_value ** 2)) if lambda_value < 0 else D(0)
    classii_quartic_coefficient = padded(D(2) * abs(a_value) + D(8) * abs(b_value) + D(8) * abs(c_value))
    quartic_energy_upper = padded((abs(lambda_value) / D(4) + classii_quartic_coefficient / D(2)) * embedding * embedding)
    sextic_energy_upper = padded(gamma_value * powd(embedding, D(4)) / D(6))

    alpha = dec(stage["fractional_power"])
    theta = alpha - D("0.5")
    tau = dec(stage["tau"])
    final_time = dec(stage["T"])
    delta = tau / D(4)
    c_theta = powd(theta / E_LO, theta)
    c_alpha = powd(alpha / E_LO, alpha)
    c_half = sqrt(D("0.5") / E_LO)
    c_one = D(1) / E_LO
    contraction_factor = dec(stage["classii_contraction_overcount"])

    check("positive_declared_times", D(0) < tau < final_time, {"tau": str(tau), "T": str(final_time)}, assertions)
    check("fractional_power_supports_two_endpoint_steps", D("0.5") < alpha < D(1) and theta > 0, {"alpha": str(alpha), "theta": str(theta)}, assertions)
    check("positive_explicit_density_floor", epsilon > 0, str(epsilon), assertions)
    check("embedding_tail_is_explicit", series_tail > 0 and grad_tail > 0, {"linf_tail": sci(series_tail), "grad_l4_tail": sci(grad_tail)}, assertions)
    check("linear_graph_constants_are_positive", c_linear > 0 and c_linear_upper >= c_linear, {"lower": str(c_linear), "upper": str(c_linear_upper)}, assertions)

    l_max = max(periods)
    projection_tail4 = padded(powd(l_max / PI_LO, D(4)))
    alias_shell_sum = padded(D(4) * powd(PI_UP, D(2)) + powd(PI_UP, D(4)) / D(45))
    alias_constant = padded(powd(l_max / PI_LO, D(2)) * sqrt(alias_shell_sum))
    rows: list[dict[str, Any]] = []
    legacy_dominance: list[bool] = []
    discrete_ball_checks: list[bool] = []
    evolution_ball_checks: list[bool] = []
    outward_storage_checks: list[bool] = []
    for energy_row in energy["rows"]:
        radius = dec(energy_row["initial_h2_radius"])
        initial_energy_upper = energy_upper_on_h2_ball(radius, c_linear_upper, quartic_energy_upper, sextic_energy_upper)
        m2 = sqrt(D(2) * (initial_energy_upper + young_constant * volume) / c_linear)
        legacy_dominance.append(m2 >= dec(energy_row["h2_envelope"]))
        amplitude = padded(embedding * m2)
        coeff = coefficient_derivatives(amplitude, epsilon, a_value, b_value, c_value, int(stage["classii_generators"]))
        low = nonlinear_majorants(m2, None, embedding, gradient_l4, algebra_h2, volume, lambda_value, gamma_value, coeff["bmetric"], contraction_factor)

        x_half = padded(sqrt(c_linear_upper) * m2)
        fractional_h3 = padded(c_theta * powd(delta, -theta) * x_half + c_alpha * low["K0"] * powd(delta, D(1) - alpha) / (D(1) - alpha))
        holder_xhalf = padded(fractional_h3 + D(2) * c_half * low["K0"])
        holder_n0 = padded(low["Lip0"] * holder_xhalf / sqrt(c_linear))
        x_one = padded(c_half * powd(delta, D("-0.5")) * x_half + D(2) * low["K0"] + c_one * holder_n0 * powd(delta, theta) / theta)
        m4 = padded(x_one / c_linear)

        high = nonlinear_majorants(m2, m4, embedding, gradient_l4, algebra_h2, volume, lambda_value, gamma_value, coeff["bmetric"], contraction_factor)
        k2_xhalf = padded(sqrt(c_linear_upper) * high["K2"])
        fractional_h5 = padded(c_theta * powd(delta, -theta) * x_one + c_alpha * k2_xhalf * powd(delta, D(1) - alpha) / (D(1) - alpha))
        holder_xone = padded(fractional_h5 + D(2) * c_half * k2_xhalf)
        holder_n2 = padded(sqrt(c_linear_upper) * high["Lip2"] * holder_xone / c_linear)
        x_three_halves = padded(c_half * powd(delta, D("-0.5")) * x_one + D(2) * k2_xhalf + c_one * holder_n2 * powd(delta, theta) / theta)
        b6 = padded(x_three_halves / powd(c_linear, D("1.5")))

        residual_constant = padded(low["Lip0"] * projection_tail4 * b6 + alias_constant * high["K2"])
        galerkin_forcing_constant = padded(low["Lip0"] * projection_tail4 * b6)

        # The restart P_N u(tau) is known only to lie in the continuum M2 ball.
        # Apply the energy upper/coercivity chain once more to obtain the
        # uniform exact-Galerkin ball; no unproved F(P_N u)<=F(u) monotonicity
        # is used.
        galerkin_initial_energy_upper = energy_upper_on_h2_ball(m2, c_linear_upper, quartic_energy_upper, sextic_energy_upper)
        galerkin_m2 = sqrt(D(2) * (galerkin_initial_energy_upper + young_constant * volume) / c_linear)
        evolution_m2 = max(m2, galerkin_m2)
        evolution_amplitude = padded(embedding * evolution_m2)
        evolution_coeff = coefficient_derivatives(evolution_amplitude, epsilon, a_value, b_value, c_value, int(stage["classii_generators"]))
        evolution_low = nonlinear_majorants(evolution_m2, None, embedding, gradient_l4, algebra_h2, volume, lambda_value, gamma_value, evolution_coeff["bmetric"], contraction_factor)
        growth_rate = padded(evolution_low["Lip0"] * evolution_low["Lip0"] / (D(2) * c_linear))
        duration = final_time - tau
        if not (D(0) < duration <= D(1)):
            raise AssertionError("the coarse Gronwall enclosure requires 0 < T-tau <= 1")
        z_value = padded(growth_rate * duration)
        # For a = growth_rate and d = T-tau <= 1,
        # (exp(a d)-1)/a <= d exp(a d) <= exp(a d).  This deliberately
        # coarse enclosure has only positive summands, so every Decimal pad
        # is in the conservative direction even when a d is enormous.
        log10_evolution = padded(log10(galerkin_forcing_constant) + z_value / LN10_LO)

        discrete_ball_checks.append(galerkin_m2 >= m2 and galerkin_initial_energy_upper >= initial_energy_upper)
        evolution_ball_checks.append(evolution_m2 >= galerkin_m2 and evolution_low["Lip0"] >= low["Lip0"])
        outward_values = (m2, galerkin_m2, evolution_low["Lip0"], b6, residual_constant, growth_rate, log10_evolution)
        outward_storage_checks.append(all(dec(sci(value)) >= value for value in outward_values))

        row = {
            "initial_h2_radius": str(radius),
            "continuum_initial_energy_upper": sci(initial_energy_upper),
            "M2": sci(m2),
            "pointwise_amplitude_upper": sci(amplitude),
            "classii_q_derivative_envelopes": [sci(value) for value in coeff["q"]],
            "classii_metric_derivative_envelopes": [sci(value) for value in coeff["bmetric"]],
            "K0_H2_to_L2_bound": sci(low["K0"]),
            "Lip0_H2_to_L2_bound": sci(low["Lip0"]),
            "B4_tau_over_2_T": sci(m4),
            "K2_H4_to_H2_bound": sci(high["K2"]),
            "Lip2_H4_to_H2_bound": sci(high["Lip2"]),
            "B6_tau_T": sci(b6),
            "log10_B6_tau_T": sci(log10(b6)),
            "residual_C_for_N_minus_2": sci(residual_constant),
            "log10_residual_C": sci(log10(residual_constant)),
            "galerkin_restart_energy_upper": sci(galerkin_initial_energy_upper),
            "galerkin_H2_envelope": sci(galerkin_m2),
            "galerkin_to_continuum_H2_envelope_ratio": sci(galerkin_m2 / m2),
            "evolution_common_H2_ball": sci(evolution_m2),
            "evolution_Lip0_H2_to_L2_bound": sci(evolution_low["Lip0"]),
            "dealiased_galerkin_growth_rate": sci(growth_rate),
            "dealiased_restarted_error_rate": "N^-4 on [tau,T] with u_N(tau)=P_N u(tau)",
            "log10_dealiased_error_constant": sci(log10_evolution),
            "projection_energy_monotonicity_used": False,
        }
        rows.append(row)

    b6_logs = [dec(row["log10_B6_tau_T"]) for row in rows]
    residual_logs = [dec(row["log10_residual_C"]) for row in rows]
    evolution_logs = [dec(row["log10_dealiased_error_constant"]) for row in rows]
    check("all_majorants_are_finite_positive_decimals", all(value.is_finite() for value in b6_logs + residual_logs + evolution_logs), {"B6_log10": [str(value) for value in b6_logs]}, assertions)
    check("B6_is_monotone_in_declared_radius", all(b6_logs[index + 1] >= b6_logs[index] for index in range(len(rows) - 1)), [str(value) for value in b6_logs], assertions)
    check("residual_constant_is_monotone_in_declared_radius", all(residual_logs[index + 1] >= residual_logs[index] for index in range(len(rows) - 1)), [str(value) for value in residual_logs], assertions)
    check("evolution_constant_is_monotone_in_declared_radius", all(evolution_logs[index + 1] >= evolution_logs[index] for index in range(len(rows) - 1)), [str(value) for value in evolution_logs], assertions)
    check("residual_aliasing_rate_is_explicit", alias_constant > 0 and projection_tail4 > 0, {"alias_N^-2": sci(alias_constant), "projection_N^-4": sci(projection_tail4)}, assertions)
    check("continuum_energy_envelope_is_recomputed_outward", all(legacy_dominance), legacy_dominance, assertions)
    check("galerkin_restart_has_separate_energy_envelope", all(discrete_ball_checks), [row["galerkin_H2_envelope"] for row in rows], assertions)
    check("evolution_lipschitz_uses_galerkin_common_ball", all(evolution_ball_checks), [row["evolution_Lip0_H2_to_L2_bound"] for row in rows], assertions)
    check("reported_majorants_are_outward_rounded", all(outward_storage_checks), outward_storage_checks, assertions)
    contraction_breakdown = stage["classii_contraction_breakdown"]
    contraction_headroom = contraction_factor / D("1.5")
    check(
        "classii_contraction_overcount_dominates_coordinate_free_euler_factor",
        contraction_headroom >= D(72)
        and dec(contraction_breakdown["remaining_coordinate_free_euler_factor"]) == D("1.5")
        and dec(contraction_breakdown["declared_headroom_ratio"]) == D(72),
        {
            "declared": str(contraction_factor),
            "minimal_euler_tensor_factor": "1.5",
            "headroom_ratio": str(contraction_headroom),
            "generator_sum": contraction_breakdown["generator_sum"],
            "spatial_frobenius_sum": contraction_breakdown["spatial_frobenius_sum"],
            "field_components": contraction_breakdown["field_components"],
        },
        assertions,
    )
    check("gronwall_duration_is_within_coarse_enclosure_scope", D(0) < final_time - tau <= D(1), {"T_minus_tau": str(final_time - tau)}, assertions)
    check("positive_time_restart_is_declared", "restarted" in stage["evolution_scope"].lower() and tau > 0, stage["evolution_scope"], assertions)
    check("historical_solver_scope_is_excluded", bool(stage["acceptance"]["require_no_historical_solver_claim"]), "No historical collocation trajectory is certified", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-quantitative-majorant-result/1.1",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-QUANTITATIVE-MAJORANT-PASS" if passed == len(assertions) else "A3-FULL-QUANTITATIVE-MAJORANT-FAIL",
        "scope": "canonical P1/P2 H2 solution balls; explicit positive-time H6 and residual bounds; exact Galerkin flow restarted at tau",
        "constant_labels": "All reported upper constants are DERIVED outward-rounded conservative enclosures; the graph lower constant is rounded downward.",
        "numeric_enclosure": {
            "decimal_precision": getcontext().prec,
            "relative_pad_per_nonlinear_stage": str(NUMERIC_PAD),
            "upper_serialisation": "ROUND_CEILING to 15 significant digits",
            "lower_serialisation": "ROUND_FLOOR to 15 significant digits",
        },
        "norms": {
            "H2": "volume sum (1+|k|^4)|u_hat|^2",
            "H4": "volume sum (1+|k|^4)^2|u_hat|^2",
            "H6": "volume sum (1+|k|^4)^3|u_hat|^2",
        },
        "derived_global_constants": {
            "H2_to_Linf": sci(embedding),
            "H2_to_grad_L4": sci(gradient_l4),
            "H2_algebra_overcount": sci(algebra_h2),
            "linear_graph_lower": sci_lower(c_linear),
            "linear_graph_upper": sci(c_linear_upper),
            "energy_young_constant_per_volume": sci(young_constant),
            "energy_quartic_upper": sci(quartic_energy_upper),
            "energy_sextic_upper": sci(sextic_energy_upper),
            "classii_contraction_overcount": sci(contraction_factor),
            "coordinate_free_euler_tensor_factor": "1.50000000000000E+0",
            "classii_contraction_headroom_ratio": sci(contraction_headroom),
            "projection_tail_N_minus_4": sci(projection_tail4),
            "periodic_alias_N_minus_2": sci(alias_constant),
            "rho_floor": sci(epsilon),
            "fractional_power": str(alpha),
            "holder_exponent": str(theta),
            "tau": str(tau),
            "T": str(final_time),
        },
        "rows": rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "honesty_boundary": {
            "closed_here": [
                "explicit conservative B4 and B6 positive-time solution-ball majorants",
                "explicit residual aliasing constant C(R,tau,T) multiplying N^-2",
                "explicit N^-4 finite-time bound for exact Galerkin flow restarted at tau",
            ],
            "not_closed_here": [
                "useful or sharp numerical error bars at practical N",
                "algebraic convergence from t=0 for merely H2 initial data",
                "finite-oversampling exactness for the rational Class-II collocation residual",
                "historical Sector-B solver continuum certification",
                "T5/T6/T7 promotion or PUBLISHED reproduction bundle",
            ],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"log10 B6 bounds: {[row['log10_B6_tau_T'] for row in rows]}")
    print(f"log10 residual C bounds: {[row['log10_residual_C'] for row in rows]}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
