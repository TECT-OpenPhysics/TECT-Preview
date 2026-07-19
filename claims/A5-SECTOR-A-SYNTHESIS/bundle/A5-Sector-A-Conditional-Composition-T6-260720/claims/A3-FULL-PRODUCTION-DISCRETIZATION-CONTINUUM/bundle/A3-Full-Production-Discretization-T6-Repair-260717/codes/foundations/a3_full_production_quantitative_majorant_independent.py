#!/usr/bin/env python3
"""Independent adversarial audit of the P3 quantitative majorant.

This script does not import the majorant implementation.  It reconstructs the
linear spectrum and Fourier tail inequalities independently, samples the exact
Class-II q=m/(rho+eps) directional derivatives against the published analytic
envelopes, and checks the logarithmic constant representation and scope flags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.1.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
P2_MANIFEST = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "full_pde_manifest.json"
MAJORANT_RESULT = CLAIM / "runs" / "2026-07-17-quantitative-majorant-repair" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-quantitative-majorant-independent-repair" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def generators() -> tuple[np.ndarray, ...]:
    return (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def q_value(real_vector: np.ndarray, generator: np.ndarray, epsilon: float) -> float:
    psi = real_vector[:3] + 1j * real_vector[3:]
    rho = float(np.real(np.vdot(psi, psi)))
    moment = float(np.real(np.vdot(psi, generator @ psi)))
    return moment / (rho + epsilon)


def directional_differences(point: np.ndarray, direction: np.ndarray, generator: np.ndarray, epsilon: float, step: float) -> tuple[float, float, float]:
    f0 = q_value(point, generator, epsilon)
    fp = q_value(point + step * direction, generator, epsilon)
    fm = q_value(point - step * direction, generator, epsilon)
    fpp = q_value(point + 2.0 * step * direction, generator, epsilon)
    fmm = q_value(point - 2.0 * step * direction, generator, epsilon)
    first = (fp - fm) / (2.0 * step)
    second = (fp - 2.0 * f0 + fm) / (step * step)
    third = (fpp - 2.0 * fp + 2.0 * fm - fmm) / (2.0 * step**3)
    return abs(first), abs(second), abs(third)


D = Decimal
getcontext().prec = 100


def dec(value: Any) -> Decimal:
    return D(str(value))


def choose(order: int, index: int) -> Decimal:
    return D(math.comb(order, index))


def derivative_product(left: list[Decimal], right: list[Decimal], order: int) -> Decimal:
    total = D(0)
    for index in range(order + 1):
        total += choose(order, index) * left[index] * right[order - index]
    return total


def independent_coefficient_bounds(
    amplitude: Decimal,
    epsilon: Decimal,
    a_value: Decimal,
    b_value: Decimal,
    c_value: Decimal,
    generator_count: int,
) -> list[Decimal]:
    """Reconstruct D^j B bounds without importing the primary implementation."""
    moment = [amplitude**2, D(2) * amplitude, D(2), D(0)]
    inverse: list[Decimal] = []
    for order in range(4):
        inverse.append(D(math.factorial(order)) * (D(2) * amplitude + D(2)) ** order / epsilon ** (order + 1))
    q = [D(1)]
    for order in range(1, 4):
        total = D(0)
        for index in range(min(order, 2) + 1):
            total += choose(order, index) * moment[index] * inverse[order - index]
        q.append(total)
    p = [D(2) * amplitude, D(2), D(0), D(0)]
    two_u = list(p)
    s = [p[order] + derivative_product(q, two_u, order) for order in range(4)]
    output: list[Decimal] = []
    for order in range(4):
        pp = derivative_product(p, p, order)
        ps = derivative_product(p, s, order) + derivative_product(s, p, order)
        ss = derivative_product(s, s, order)
        output.append(D(generator_count) * (abs(a_value) * pp + abs(b_value) * ps + abs(c_value) * ss))
    return output


def independent_nonlinear_bounds(
    m2: Decimal,
    m4: Decimal | None,
    embedding: Decimal,
    gradient_l4: Decimal,
    algebra: Decimal,
    volume: Decimal,
    lambda_value: Decimal,
    gamma_value: Decimal,
    bmetric: list[Decimal],
    contraction: Decimal,
) -> dict[str, Decimal]:
    pointwise = embedding * m2
    potential0 = abs(lambda_value) * pointwise**2 * m2 + gamma_value * pointwise**4 * m2
    classii0 = contraction * (bmetric[0] * m2 + bmetric[1] * D(3) * gradient_l4**2 * m2**2)
    lip_potential0 = D(3) * abs(lambda_value) * pointwise**2 + D(5) * gamma_value * pointwise**4
    lip_classii0 = contraction * (
        bmetric[0]
        + bmetric[1] * embedding * m2**2
        + bmetric[2] * embedding * D(3) * gradient_l4**2 * m2**2
        + D(2) * bmetric[1] * D(3) * gradient_l4**2 * m2
    )
    values = {"K0": potential0 + classii0, "Lip0": lip_potential0 + lip_classii0}
    if m4 is None:
        return values
    sqrt_volume = volume.sqrt()
    b_h2 = bmetric[0] * sqrt_volume + bmetric[1] * algebra * m2 + bmetric[2] * (algebra * m2) ** 2
    db_h2 = bmetric[1] * sqrt_volume + bmetric[2] * algebra * m2 + bmetric[3] * (algebra * m2) ** 2
    potential2 = abs(lambda_value) * algebra**2 * m2**3 + gamma_value * algebra**4 * m2**5
    k2 = potential2 + contraction * (algebra * b_h2 * m4 + algebra**2 * db_h2 * m4**2)
    b_lip = algebra * (bmetric[1] * sqrt_volume + bmetric[2] * algebra * m2 + bmetric[3] * (algebra * m2) ** 2)
    db_lip = algebra * (bmetric[2] * sqrt_volume + bmetric[3] * (D(1) + algebra * m2) ** 2)
    potential_lip2 = D(3) * abs(lambda_value) * algebra**2 * m2**2 + D(5) * gamma_value * algebra**4 * m2**4
    lip2 = potential_lip2 + contraction * (
        algebra * (b_lip * m4 + b_h2)
        + algebra**2 * (db_lip * m4**2 + D(2) * db_h2 * m4)
    )
    values.update({"K2": k2, "Lip2": lip2})
    return values


def energy_upper(radius: Decimal, linear: Decimal, quartic: Decimal, sextic: Decimal) -> Decimal:
    return D("0.5") * linear * radius**2 + quartic * radius**4 + sextic * radius**6


def logarithmic_relative_error(left: Decimal, right: Decimal) -> Decimal:
    if left <= 0 or right <= 0:
        return D("Infinity")
    return abs(left.ln() - right.ln())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    p2 = json.loads(P2_MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(MAJORANT_RESULT.read_text(encoding="utf-8"))
    params = p1["parameters"]
    stage = manifest["stage8_quantitative_majorant"]
    assertions: list[dict[str, Any]] = []

    source_entry = manifest["authority"]["quantitative_majorant_audit"]
    source_path = REPO / source_entry["path"]
    source_hash = sha256(source_path)
    check("majorant_source_hash_matches_manifest", source_hash == source_entry["sha256"], {"actual": source_hash, "expected": source_entry["sha256"]}, assertions)
    check("majorant_result_passed", result.get("verdict") == "A3-FULL-QUANTITATIVE-MAJORANT-PASS" and result.get("assertion_summary", {}).get("passed") == result.get("assertion_summary", {}).get("total"), result.get("verdict"), assertions)

    # Independent spectral reconstruction of the constant internal matrix.
    z0 = np.asarray(params["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(np.dot(z0, z0))
    internal = np.diag(np.asarray(params["family_masses"], dtype=float))
    internal += float(params["k_lock"]) * (np.eye(3) - projector)
    internal_eigenvalues = np.linalg.eigvalsh(internal)
    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    mode_axis = np.arange(-32, 33, dtype=float)
    k_scale = 2.0 * math.pi / float(params["Lx"])
    k_squared = k_scale**2 * mode_axis**2
    sampled_symbols = []
    for x_value in k_squared:
        sampled_symbols.extend((y_value * x_value**2 + z_value * x_value + r_value + internal_eigenvalues).tolist())
    symbols = np.asarray(sampled_symbols)
    check("independent_linear_spectrum_is_positive", float(np.min(symbols)) > 0.0, {"minimum": float(np.min(symbols)), "internal_eigenvalues": internal_eigenvalues.tolist()}, assertions)

    semigroup_ratios = []
    for time in (0.005, 0.02, 0.2):
        for power in (0.25, 0.5, 0.75, 1.0):
            observed = float(np.max(symbols**power * np.exp(-time * symbols)))
            universal = (power / (math.e * time)) ** power
            semigroup_ratios.append(observed / universal)
    check("sampled_semigroup_respects_universal_fractional_bound", max(semigroup_ratios) <= 1.0 + 2e-12, max(semigroup_ratios), assertions)

    # Direct Fourier-tail test over many omitted modes and all declared N.
    tail_constant = float(result["derived_global_constants"]["projection_tail_N_minus_4"])
    tail_ratios = []
    l_max = max(float(params[name]) for name in ("Lx", "Ly", "Lz"))
    for grid in (8, 12, 16, 32):
        for index in range(grid // 2, 8 * grid + 1):
            k_value = 2.0 * math.pi * index / l_max
            h2_over_h6 = 1.0 / (1.0 + k_value**4)
            tail_ratios.append(h2_over_h6 / (tail_constant * grid**-4))
    check("projection_H6_to_H2_tail_obeys_N_minus_4", max(tail_ratios) <= 1.0 + 2e-12, max(tail_ratios), assertions)

    alias_constant = float(result["derived_global_constants"]["periodic_alias_N_minus_2"])
    exact_alias_shell_sum = 4.0 * math.pi**2 + math.pi**4 / 45.0
    reconstructed_alias = (l_max / math.pi) ** 2 * math.sqrt(exact_alias_shell_sum)
    check("alias_shell_constant_is_conservative", alias_constant >= reconstructed_alias * (1.0 - 2e-14), {"published": alias_constant, "reconstructed": reconstructed_alias}, assertions)

    # Adversarial local checks of the exact q ratio against the analytic
    # derivative envelopes.  Points stay away from zero to avoid finite-
    # difference cancellation; the analytic bound itself covers zero via eps.
    rng = np.random.default_rng(20260717)
    largest = result["rows"][-1]
    amplitude = float(largest["pointwise_amplitude_upper"])
    envelopes = [float(value) for value in largest["classii_q_derivative_envelopes"]]
    maxima = [0.0, 0.0, 0.0]
    for _ in range(64):
        point = rng.normal(size=6)
        point *= rng.uniform(0.1, amplitude) / np.linalg.norm(point)
        direction = rng.normal(size=6)
        direction /= np.linalg.norm(direction)
        for generator in generators():
            values = directional_differences(point, direction, generator, float(params["rho_regularizer"]), 2e-4)
            maxima = [max(old, new) for old, new in zip(maxima, values)]
    check("sampled_q_directional_derivatives_fit_explicit_envelopes", all(maxima[index] <= envelopes[index + 1] for index in range(3)), {"sampled_maxima": maxima, "envelopes": envelopes[1:]}, assertions)

    # Full-chain reconstruction.  This code uses its own coefficient/product
    # routines and does not import the primary majorant module.
    constants = {key: dec(value) for key, value in result["derived_global_constants"].items() if key not in {"fractional_power", "holder_exponent", "tau", "T"}}
    embedding = constants["H2_to_Linf"]
    gradient_l4 = constants["H2_to_grad_L4"]
    algebra = constants["H2_algebra_overcount"]
    c_lower = constants["linear_graph_lower"]
    c_upper = constants["linear_graph_upper"]
    young = constants["energy_young_constant_per_volume"]
    quartic_energy = constants["energy_quartic_upper"]
    sextic_energy = constants["energy_sextic_upper"]
    contraction = constants["classii_contraction_overcount"]
    projection = constants["projection_tail_N_minus_4"]
    alias = constants["periodic_alias_N_minus_2"]
    periods = [dec(params[name]) for name in ("Lx", "Ly", "Lz")]
    volume = periods[0] * periods[1] * periods[2]
    epsilon_d = dec(params["rho_regularizer"])
    denominator = dec(params["M_X"]) ** 2 + dec(params["classii_mass_regularizer"])
    a_value = dec(params["cJJ"]) * dec(params["alpha_X"]) ** 2 / denominator
    b_value = dec(params["cJK"]) * dec(params["alpha_X"]) * dec(params["beta_X"]) / denominator
    c_value = dec(params["cKK"]) * dec(params["beta_X"]) ** 2 / denominator
    lambda_value = dec(params["lambda"])
    gamma_value = dec(params["gamma"])
    tau_d = dec(stage["tau"])
    final_d = dec(stage["T"])
    delta = tau_d / D(4)
    alpha_d = dec(stage["fractional_power"])
    theta_d = alpha_d - D("0.5")
    e_value = D(1).exp()
    c_theta = (theta_d / e_value) ** theta_d
    c_alpha = (alpha_d / e_value) ** alpha_d
    c_half = (D("0.5") / e_value).sqrt()
    c_one = D(1) / e_value

    energy_errors: list[Decimal] = []
    galerkin_ball_errors: list[Decimal] = []
    low_errors: list[Decimal] = []
    endpoint4_errors: list[Decimal] = []
    high_errors: list[Decimal] = []
    endpoint6_errors: list[Decimal] = []
    residual_errors: list[Decimal] = []
    evolution_lip_errors: list[Decimal] = []
    growth_errors: list[Decimal] = []
    gronwall_log_errors: list[Decimal] = []
    no_projection_monotonicity = []
    common_ball_order = []
    for row in result["rows"]:
        radius = dec(row["initial_h2_radius"])
        initial_energy = energy_upper(radius, c_upper, quartic_energy, sextic_energy)
        m2 = (D(2) * (initial_energy + young * volume) / c_lower).sqrt()
        energy_errors.append(logarithmic_relative_error(dec(row["continuum_initial_energy_upper"]), initial_energy))
        energy_errors.append(logarithmic_relative_error(dec(row["M2"]), m2))

        stored_m2 = dec(row["M2"])
        restart_energy = energy_upper(stored_m2, c_upper, quartic_energy, sextic_energy)
        galerkin_m2 = (D(2) * (restart_energy + young * volume) / c_lower).sqrt()
        galerkin_ball_errors.append(logarithmic_relative_error(dec(row["galerkin_restart_energy_upper"]), restart_energy))
        galerkin_ball_errors.append(logarithmic_relative_error(dec(row["galerkin_H2_envelope"]), galerkin_m2))
        no_projection_monotonicity.append(row.get("projection_energy_monotonicity_used") is False)
        common_m2 = dec(row["evolution_common_H2_ball"])
        common_ball_order.append(common_m2 >= dec(row["galerkin_H2_envelope"]) >= stored_m2)

        amplitude = embedding * stored_m2
        bmetric = independent_coefficient_bounds(amplitude, epsilon_d, a_value, b_value, c_value, int(stage["classii_generators"]))
        low = independent_nonlinear_bounds(stored_m2, None, embedding, gradient_l4, algebra, volume, lambda_value, gamma_value, bmetric, contraction)
        low_errors.extend([
            logarithmic_relative_error(dec(row["K0_H2_to_L2_bound"]), low["K0"]),
            logarithmic_relative_error(dec(row["Lip0_H2_to_L2_bound"]), low["Lip0"]),
        ])

        x_half = c_upper.sqrt() * stored_m2
        fractional_h3 = c_theta * delta ** (-theta_d) * x_half + c_alpha * low["K0"] * delta ** (D(1) - alpha_d) / (D(1) - alpha_d)
        holder_xhalf = fractional_h3 + D(2) * c_half * low["K0"]
        holder_n0 = low["Lip0"] * holder_xhalf / c_lower.sqrt()
        x_one = c_half * delta ** D("-0.5") * x_half + D(2) * low["K0"] + c_one * holder_n0 * delta ** theta_d / theta_d
        m4 = x_one / c_lower
        endpoint4_errors.append(logarithmic_relative_error(dec(row["B4_tau_over_2_T"]), m4))

        high = independent_nonlinear_bounds(stored_m2, dec(row["B4_tau_over_2_T"]), embedding, gradient_l4, algebra, volume, lambda_value, gamma_value, bmetric, contraction)
        high_errors.extend([
            logarithmic_relative_error(dec(row["K2_H4_to_H2_bound"]), high["K2"]),
            logarithmic_relative_error(dec(row["Lip2_H4_to_H2_bound"]), high["Lip2"]),
        ])
        k2_xhalf = c_upper.sqrt() * dec(row["K2_H4_to_H2_bound"])
        fractional_h5 = c_theta * delta ** (-theta_d) * x_one + c_alpha * k2_xhalf * delta ** (D(1) - alpha_d) / (D(1) - alpha_d)
        holder_xone = fractional_h5 + D(2) * c_half * k2_xhalf
        holder_n2 = c_upper.sqrt() * dec(row["Lip2_H4_to_H2_bound"]) * holder_xone / c_lower
        x_three_halves = c_half * delta ** D("-0.5") * x_one + D(2) * k2_xhalf + c_one * holder_n2 * delta ** theta_d / theta_d
        b6 = x_three_halves / c_lower ** D("1.5")
        endpoint6_errors.append(logarithmic_relative_error(dec(row["B6_tau_T"]), b6))

        residual = low["Lip0"] * projection * dec(row["B6_tau_T"]) + alias * high["K2"]
        residual_errors.append(logarithmic_relative_error(dec(row["residual_C_for_N_minus_2"]), residual))

        common_amplitude = embedding * common_m2
        common_bmetric = independent_coefficient_bounds(common_amplitude, epsilon_d, a_value, b_value, c_value, int(stage["classii_generators"]))
        common_low = independent_nonlinear_bounds(common_m2, None, embedding, gradient_l4, algebra, volume, lambda_value, gamma_value, common_bmetric, contraction)
        evolution_lip = dec(row["evolution_Lip0_H2_to_L2_bound"])
        evolution_lip_errors.append(logarithmic_relative_error(evolution_lip, common_low["Lip0"]))
        growth = evolution_lip**2 / (D(2) * c_lower)
        growth_errors.append(logarithmic_relative_error(dec(row["dealiased_galerkin_growth_rate"]), growth))
        forcing = low["Lip0"] * projection * dec(row["B6_tau_T"])
        z_value = growth * (final_d - tau_d)
        # Independently reconstruct the deliberately coarse enclosure
        # (exp(a d)-1)/a <= d exp(a d) <= exp(a d), valid for 0 < d <= 1.
        log_e = forcing.log10() + z_value / D(10).ln()
        gronwall_log_errors.append(logarithmic_relative_error(dec(row["log10_dealiased_error_constant"]), log_e))

    chain_tolerance = D("2e-11")
    check("full_chain_continuum_energy_and_M2_reconstructed", max(energy_errors) <= chain_tolerance, [str(value) for value in energy_errors], assertions)
    check("full_chain_galerkin_restart_ball_reconstructed", max(galerkin_ball_errors) <= chain_tolerance, [str(value) for value in galerkin_ball_errors], assertions)
    check("projection_energy_monotonicity_is_not_assumed", all(no_projection_monotonicity), no_projection_monotonicity, assertions)
    check("common_evolution_ball_contains_galerkin_and_continuum_balls", all(common_ball_order), common_ball_order, assertions)
    check("full_chain_K0_and_Lip0_reconstructed", max(low_errors) <= chain_tolerance, [str(value) for value in low_errors], assertions)
    check("full_chain_first_endpoint_B4_reconstructed", max(endpoint4_errors) <= chain_tolerance, [str(value) for value in endpoint4_errors], assertions)
    check("full_chain_K2_and_Lip2_reconstructed", max(high_errors) <= chain_tolerance, [str(value) for value in high_errors], assertions)
    check("full_chain_second_endpoint_B6_reconstructed", max(endpoint6_errors) <= chain_tolerance, [str(value) for value in endpoint6_errors], assertions)
    check("full_chain_residual_C_reconstructed", max(residual_errors) <= chain_tolerance, [str(value) for value in residual_errors], assertions)
    check("full_chain_evolution_Lip0_reconstructed_on_galerkin_ball", max(evolution_lip_errors) <= chain_tolerance, [str(value) for value in evolution_lip_errors], assertions)
    check("full_chain_growth_rate_reconstructed", max(growth_errors) <= chain_tolerance, [str(value) for value in growth_errors], assertions)
    check("full_chain_gronwall_log_constant_reconstructed", max(gronwall_log_errors) <= chain_tolerance, [str(value) for value in gronwall_log_errors], assertions)
    check("gronwall_duration_is_within_coarse_enclosure_scope", D(0) < final_d - tau_d <= D(1), {"T_minus_tau": str(final_d - tau_d)}, assertions)
    check(
        "declared_contraction_dominates_coordinate_free_euler_factor",
        contraction / D("1.5") >= D(72)
        and constants["coordinate_free_euler_tensor_factor"] == D("1.5")
        and constants["classii_contraction_headroom_ratio"] >= D(72),
        {"declared": str(contraction), "required": "1.5", "headroom_ratio": str(constants["classii_contraction_headroom_ratio"])},
        assertions,
    )

    log_errors = []
    for row in result["rows"]:
        b6 = Decimal(row["B6_tau_T"])
        recorded = Decimal(row["log10_B6_tau_T"])
        recomputed = b6.log10()
        log_errors.append(abs(recomputed - recorded))
    check("decimal_B6_logarithms_are_self_consistent", max(log_errors) <= Decimal("2e-12"), [str(value) for value in log_errors], assertions)
    check("declared_rates_and_restart_scope_are_consistent", all(row["dealiased_restarted_error_rate"].startswith("N^-4") for row in result["rows"]) and float(stage["tau"]) > 0.0 and "restarted" in stage["evolution_scope"].lower(), stage["evolution_scope"], assertions)
    check("historical_solver_certificate_is_absent", "historical Sector-B solver continuum certification" in result["honesty_boundary"]["not_closed_here"], result["honesty_boundary"]["not_closed_here"], assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-quantitative-majorant-independent/1.1",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-PASS" if passed == len(assertions) else "A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-FAIL",
        "scope": "independent full-chain reconstruction of energy balls, nonlinear constants, two endpoint gains, residual/alias bound, Galerkin Lipschitz/Gronwall chain, plus spectral, Fourier-tail, q-derivative, logarithm, and honesty-boundary checks",
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "not_closed_here": ["sharpness of the conservative constants", "historical solver certification", "external public reproduction"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Maximum sampled semigroup ratio: {max(semigroup_ratios):.12g}")
    print(f"Maximum projection-tail ratio: {max(tail_ratios):.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
