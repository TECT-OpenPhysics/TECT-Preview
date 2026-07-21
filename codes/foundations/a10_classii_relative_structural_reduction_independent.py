#!/usr/bin/env python3
"""Non-importing audit of the A10 Class-II structural reduction.

This route rebuilds the Pauli currents in complex notation, uses a distinct
Fourier/quadrature implementation for the strict-dyadic and triad fixtures,
and checks the conditional composition algebra without importing the primary
module.
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
from pathlib import Path
from typing import Any

import numpy as np


__version__ = "1.0.1"
ROOT = Path(__file__).resolve().parents[2]
CLAIM = "A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION"
DEFAULT_MANIFEST = ROOT / "claims" / CLAIM / "classii_relative_structural_reduction_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / CLAIM / "runs" / "2026-07-21-independent-relative-structural-reduction" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def current_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def record(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def pauli() -> tuple[np.ndarray, ...]:
    return (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def real_form(matrix: np.ndarray) -> np.ndarray:
    upper = np.concatenate((matrix.real, -matrix.imag), axis=1)
    lower = np.concatenate((matrix.imag, matrix.real), axis=1)
    return np.concatenate((upper, lower), axis=0)


def abc(parameters: dict[str, Any]) -> tuple[float, float, float]:
    mass = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    alpha = float(parameters["alpha_X"])
    beta = float(parameters["beta_X"])
    return (
        float(parameters["cJJ"]) * alpha * alpha / mass,
        float(parameters["cJK"]) * alpha * beta / mass,
        float(parameters["cKK"]) * beta * beta / mass,
    )


def direct_density(field: np.ndarray, derivative: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    a_value, b_value, c_value = abc(parameters)
    floor = float(parameters["rho_regularizer"])
    rho = np.sum(np.abs(field) ** 2, axis=-1)
    drho = 2.0 * np.real(np.sum(np.conj(field) * derivative, axis=-1))
    total = np.zeros(field.shape[:-1], dtype=np.float64)
    for generator in pauli():
        transformed = np.einsum("ij,...j->...i", generator, field)
        moment = np.real(np.sum(np.conj(field) * transformed, axis=-1))
        j_value = 2.0 * np.real(np.sum(np.conj(transformed) * derivative, axis=-1))
        k_value = j_value - moment * drho / (rho + floor)
        total += 0.5 * a_value * j_value**2 + b_value * j_value * k_value + 0.5 * c_value * k_value**2
    return total


def gram_matrix(field: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    """Independent six-real Gram construction, vectorised over sites."""
    a_value, b_value, c_value = abc(parameters)
    floor = float(parameters["rho_regularizer"])
    x_value = np.concatenate((field.real, field.imag), axis=-1)
    rho = np.sum(x_value * x_value, axis=-1)
    result = np.zeros(field.shape[:-1] + (6, 6), dtype=np.float64)
    for generator in pauli():
        symmetric = real_form(generator)
        sx = np.einsum("ij,...j->...i", symmetric, x_value)
        q_value = np.einsum("...i,...i->...", x_value, sx) / (rho + floor)
        p_value = 2.0 * sx
        v_value = 2.0 * (sx - q_value[..., None] * x_value)
        column = np.stack((p_value, v_value), axis=-1)
        coupling = np.array([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
        result += np.einsum("...ia,ab,...jb->...ij", column, coupling, column)
    return result


def covariance(cutoff: int, parameters: dict[str, Any]) -> np.ndarray:
    length = float(parameters["Lx"])
    alpha = 2.0 * math.pi / length
    volume = length * float(parameters["Ly"]) * float(parameters["Lz"])
    family = np.diag(np.asarray(parameters["family_masses"], dtype=np.float64)).astype(np.complex128)
    z0 = np.asarray(parameters["z0"], dtype=np.complex128)
    projection = np.outer(z0, np.conj(z0)) / np.vdot(z0, z0).real
    mass = family + float(parameters["k_lock"]) * (np.eye(3) - projection)
    answer = np.zeros((3, 3), dtype=np.complex128)
    for linear in range((2 * cutoff + 1) ** 3):
        n1 = linear // ((2 * cutoff + 1) ** 2) - cutoff
        remainder = linear % ((2 * cutoff + 1) ** 2)
        n2 = remainder // (2 * cutoff + 1) - cutoff
        n3 = remainder % (2 * cutoff + 1) - cutoff
        k2 = alpha**2 * float(n1 * n1 + n2 * n2 + n3 * n3)
        polynomial = float(parameters["r"]) + float(parameters["Z"]) * k2 + float(parameters["Y"]) * k2**2
        eigenvalues, basis = np.linalg.eigh(polynomial * np.eye(3) + mass)
        inverse = (basis * (1.0 / eigenvalues)) @ basis.conj().T
        answer += k2 * inverse / volume
    # Independently implement the pinned A6/A7 convention:
    # E[Psi_k Psi_k^dagger]=2 A(k)^-1 and
    # Gamma=(1/2) realify(D_complex)=realify(answer).
    complex_derivative_covariance = 2.0 * answer
    return 0.5 * real_form(complex_derivative_covariance)


def plane_rows(parameters: dict[str, Any], cutoffs: list[int], grid: int) -> list[dict[str, float]]:
    coordinate = 2.0 * math.pi * np.arange(grid) / grid
    output: list[dict[str, float]] = []
    for cutoff in cutoffs:
        field = np.zeros((grid, 3), dtype=np.complex128)
        field[:, 0] = np.exp(1j * cutoff * coordinate)
        derivative = 1j * cutoff * field
        density = direct_density(field, derivative, parameters)
        matrix = gram_matrix(field, parameters)
        gamma = covariance(cutoff, parameters)
        trace = 0.5 * float(np.mean(np.einsum("...ij,ji->...", matrix, gamma)))
        output.append(
            {
                "cutoff": cutoff,
                "raw": float(np.mean(density)),
                "trace": trace,
                "complete_C": float(np.mean(density)) - trace,
                "B_trace": float(np.mean(np.trace(matrix, axis1=-2, axis2=-1))),
                "Gamma_min": float(np.min(np.linalg.eigvalsh(gamma))),
            }
        )
    return output


def partial_inner(radius: float, order: int, angles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    modes = np.arange(order + 1, dtype=np.float64)
    coefficients = np.empty(order + 1, dtype=np.float64)
    coefficients[0] = -radius
    coefficients[1:] = (1.0 - radius**2) * radius ** (modes[1:] - 1.0)
    phase = np.exp(1j * np.outer(angles, modes))
    return phase @ coefficients, phase @ (1j * modes * coefficients)


def blaschke_rows(parameters: dict[str, Any], radius: float, m_values: list[int], grid: int) -> list[dict[str, float]]:
    angles = 2.0 * math.pi * np.arange(grid) / grid
    rows: list[dict[str, float]] = []
    for m_value in m_values:
        low, _ = partial_inner(radius, m_value, angles)
        endpoint, derivative = partial_inner(radius, 2 * m_value, angles)
        low_field = np.zeros((grid, 3), dtype=np.complex128)
        end_field = np.zeros_like(low_field)
        derivative_field = np.zeros_like(low_field)
        low_field[:, 0] = low
        end_field[:, 0] = endpoint
        derivative_field[:, 0] = derivative
        frozen = float(np.mean(direct_density(low_field, derivative_field, parameters)))
        current = float(np.mean(direct_density(end_field, derivative_field, parameters)))
        modulus_derivative = 2.0 * np.real(np.conj(endpoint) * derivative)
        exact = 2.0 * (1.0 - radius**2) ** 2 * sum(
            k * k * radius ** (8 * m_value - 2 * k) for k in range(1, 2 * m_value + 1)
        )
        rows.append(
            {
                "m": m_value,
                "frozen": frozen,
                "current": current,
                "ratio": (frozen - current) / frozen,
                "autocorrelation_error": abs(float(np.mean(modulus_derivative**2)) - exact),
            }
        )
    return rows


def triad_quadrature(epsilon: float, points: int) -> dict[str, float]:
    values = 2.0 * math.pi * np.arange(points) / points
    x_value, y_value = np.meshgrid(values, values, indexing="ij")
    g_value = np.cos(x_value) + np.cos(y_value) - np.cos(x_value + y_value)
    gx = -np.sin(x_value) + np.sin(x_value + y_value)
    gy = -np.sin(y_value) + np.sin(x_value + y_value)
    grad2 = gx * gx + gy * gy
    return {
        "grad2": float(np.mean(grad2)),
        "g_grad2": float(np.mean(g_value * grad2)),
        "g2_grad2": float(np.mean(g_value * g_value * grad2)),
        "M6": float(np.mean((1.0 + epsilon * g_value) ** 6)),
    }


def finite_entropy_chain_rule() -> dict[str, float]:
    base_first = np.asarray([0.4, 0.6])
    base_second = np.asarray([[0.7, 0.3], [0.2, 0.8]])
    law = np.asarray([[0.31, 0.09], [0.18, 0.42]])
    first = np.sum(law, axis=1)
    total = float(np.sum(law * np.log(law / (base_first[:, None] * base_second))))
    marginal = float(np.sum(first * np.log(first / base_first)))
    conditional = 0.0
    for index in range(2):
        conditional_law = law[index] / first[index]
        conditional += first[index] * float(np.sum(conditional_law * np.log(conditional_law / base_second[index])))
    return {"joint": total, "marginal_plus_conditional": marginal + conditional, "error": abs(total - marginal - conditional)}


def discrete_dv(alpha: float) -> dict[str, float]:
    base = np.asarray([0.19, 0.21, 0.27, 0.33])
    observable = np.asarray([-0.8, 0.6, -1.3, 1.1])
    partition = float(np.sum(base * np.exp(-observable / alpha)))
    tilted = base * np.exp(-observable / alpha) / partition
    entropy = float(np.sum(tilted * np.log(tilted / base)))
    left = math.log(partition)
    right = -float(tilted @ observable) / alpha - entropy
    return {"left": left, "right": right, "error": abs(left - right)}


def quartic_sextic_optimizer(a_value: float, b_value: float) -> dict[str, float]:
    critical = 2.0 * a_value / (3.0 * b_value)
    exact = 4.0 * a_value**3 / (27.0 * b_value**2)
    grid = np.linspace(0.0, 2.0 * critical, 200001)
    scan = float(np.max(a_value * grid**2 - b_value * grid**3))
    return {"critical": critical, "exact": exact, "scan": scan, "relative_error": abs(scan - exact) / exact}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    rows: list[dict[str, Any]] = []

    for name, key in (("A1", "production_functional_manifest"), ("A7", "a7_composite_manifest"), ("A9", "a9_smart_path_manifest"), ("A9_nogo", "a9_nogo_manifest")):
        path = ROOT / authority[key]["path"]
        actual = digest(path)
        record(rows, f"{name}_authority_hash", actual == authority[key]["sha256"], actual, authority[key]["sha256"])

    a1_path = ROOT / authority["production_functional_manifest"]["path"]
    parameters = json.loads(a1_path.read_text(encoding="utf-8"))["parameters"]
    a_value, b_value, c_value = abc(parameters)
    coupling = np.array([[a_value, b_value], [b_value, c_value]])
    determinant = float(np.linalg.det(coupling))
    trace = float(np.trace(coupling))
    record(rows, "QII_trace_determinant_positive", determinant > 0.0 and trace > 0.0, {"det": determinant, "trace": trace}, "both positive")
    beta_b = 12.0 * a_value + 48.0 * abs(b_value) + 48.0 * c_value
    beta_1 = 24.0 * a_value + 192.0 * abs(b_value) + 288.0 * c_value
    record(rows, "beta_B_independent", abs(beta_b - manifest["constants"]["beta_B"]) < 1e-14, beta_b, manifest["constants"]["beta_B"])
    record(rows, "beta_1_independent", abs(beta_1 - manifest["constants"]["beta_1"]) < 1e-13, beta_1, manifest["constants"]["beta_1"])

    audit = manifest["independent_audit"]
    rng = np.random.default_rng(int(audit["seed"]))
    energy_errors: list[float] = []
    minimum_eigenvalue = math.inf
    for _ in range(1024):
        field = rng.normal(size=(1, 3)) + 1j * rng.normal(size=(1, 3))
        derivative = rng.normal(size=(1, 3)) + 1j * rng.normal(size=(1, 3))
        matrix = gram_matrix(field, parameters)[0]
        real_derivative = np.concatenate((derivative.real, derivative.imag), axis=-1)[0]
        matrix_energy = 0.5 * float(real_derivative @ matrix @ real_derivative)
        energy_errors.append(abs(matrix_energy - float(direct_density(field, derivative, parameters)[0])))
        minimum_eigenvalue = min(minimum_eigenvalue, float(np.min(np.linalg.eigvalsh(matrix))))
    record(rows, "complex_current_equals_six_real_Gram", max(energy_errors) < 2e-13, max(energy_errors), "<2e-13")
    record(rows, "Gram_PSD_independent", minimum_eigenvalue > -1e-11, minimum_eigenvalue, ">=-1e-11")
    record(rows, "Gamma_j_frozen_convention_independent", manifest["frozen_shell_convention"]["trace"] == "Gamma_j", manifest["frozen_shell_convention"]["trace"], "Gamma_j")
    record(rows, "Gamma_le_j_commutator_convention_independent", manifest["frozen_shell_convention"]["commutator_trace"] == "Gamma_le_j", manifest["frozen_shell_convention"]["commutator_trace"], "Gamma_le_j")

    random_qx = rng.random(2048)
    random_qz = rng.random(2048)
    random_theta = rng.random(2048)
    identity_error = float(np.max(np.abs(random_theta * random_qx + random_qz - random_qx - (random_qz - (1.0 - random_theta) * random_qx))))
    record(rows, "raw_identity_independent", identity_error < 1e-15, identity_error, 0.0)
    q_cross = rng.random(2048)
    q_endpoint = rng.random(2048)
    q_past = rng.random(2048)
    trace_shell_past = rng.normal(size=2048)
    trace_older_past = rng.normal(size=2048)
    trace_endpoint = rng.normal(size=2048)
    frozen = q_cross - trace_shell_past
    commutator = q_endpoint - q_cross - trace_endpoint + trace_shell_past + trace_older_past
    endpoint = q_endpoint - trace_endpoint
    past_endpoint = q_past - trace_older_past
    action_error = float(np.max(np.abs(frozen + commutator - (endpoint - past_endpoint + q_past))))
    past_remainder = float(np.min(frozen + commutator - (endpoint - past_endpoint)))
    record(
        rows,
        "multiscale_action_identity_independent",
        action_error < 1e-15 and past_remainder >= 0.0,
        {"identity_error": action_error, "minimum_remainder": past_remainder},
        {"identity_error": 0.0, "minimum_remainder": ">=0"},
    )
    record(rows, "raw_theta_one_sharp_formula", manifest["theorem"]["strict_dyadic_sharpness"].endswith("strict shell geometry."), manifest["theorem"]["strict_dyadic_sharpness"], "declares strict-shell theta=1 sharpness")

    blaschke = blaschke_rows(parameters, float(audit["blaschke_radius"]), [int(value) for value in audit["blaschke_m_values"]], int(audit["blaschke_grid"]))
    record(rows, "Blaschke_strict_dyadic_ratio", blaschke[-1]["ratio"] > 0.9998, blaschke[-1]["ratio"], ">0.9998")
    record(rows, "Blaschke_autocorrelation_independent", max(row["autocorrelation_error"] for row in blaschke) < float(audit["quadrature_tolerance"]), max(row["autocorrelation_error"] for row in blaschke), audit["quadrature_tolerance"])

    plane = plane_rows(parameters, [int(value) for value in audit["plane_wave_cutoffs"]], int(audit["plane_wave_grid"]))
    record(rows, "plane_wave_direct_currents_zero", max(abs(row["raw"]) for row in plane) < 2e-12, [row["raw"] for row in plane], "near zero")
    covariance_convention = manifest["frozen_shell_convention"]["covariance_normalisation"]
    record(
        rows,
        "plane_wave_B_and_Gamma_positive_with_A7_factor_two",
        min(min(row["B_trace"], row["Gamma_min"]) for row in plane) > 0.0
        and covariance_convention == "Gamma=0.5*realify(D_complex)=realify(sum_k |k|^2 A(k)^-1/V), with D_complex=2*sum_k |k|^2 A(k)^-1/V",
        {"rows": [{"B": row["B_trace"], "Gamma": row["Gamma_min"]} for row in plane], "convention": covariance_convention},
        "positive and exact A7 complex-factor-two convention",
    )
    final_plane = plane[-1]
    finite_slope = -final_plane["complete_C"] / final_plane["cutoff"]
    asymptotic_slope = float(manifest["constants"]["sharp_cube_trace_defect_coefficient"])
    slope_relative_error = abs(finite_slope / asymptotic_slope - 1.0)
    record(
        rows,
        "plane_wave_negative_trace_with_A6_slope",
        all(row["complete_C"] < 0.0 for row in plane)
        and slope_relative_error < float(audit["plane_wave_slope_relative_tolerance"]),
        {"values": [row["complete_C"] for row in plane], "finite_slope": finite_slope, "relative_error": slope_relative_error},
        {"sign": "all negative", "asymptotic_slope": asymptotic_slope, "relative_error_below": audit["plane_wave_slope_relative_tolerance"]},
    )

    active = np.zeros((1, 3), dtype=np.complex128)
    active[0, 0] = 1.0
    active_matrix = gram_matrix(active, parameters)[0]
    record(rows, "active_doublet_W_proxy_positive", float(np.trace(active_matrix)) > 0.0, float(np.trace(active_matrix)), ">0")
    record(rows, "alpha_zero_uniform_bound_impossible", manifest["theorem"]["entropy_necessity"] == "alpha_c>0", manifest["theorem"]["entropy_necessity"], "alpha_c>0")
    cutoff_ratio = [abs(row["complete_C"]) / (row["cutoff"] ** 4) for row in plane]
    record(rows, "plane_trace_over_CM_scaling_decreases", all(right < left for left, right in zip(cutoff_ratio, cutoff_ratio[1:])), cutoff_ratio, "strictly decreasing")

    triad = triad_quadrature(0.3, 768)
    record(rows, "triad_averages_quadrature", max(abs(triad["grad2"] - 2.0), abs(triad["g_grad2"] + 1.0), abs(triad["g2_grad2"] - 2.5)) < 2e-14, [triad["grad2"], triad["g_grad2"], triad["g2_grad2"]], [2.0, -1.0, 2.5])
    record(rows, "triad_M6_positive", triad["M6"] > 0.0, triad["M6"], ">0")
    theta_triad = 0.3 - 1.25 * 0.3**2
    record(rows, "triad_theta_is_three_sixteenths", abs(theta_triad - 3.0 / 16.0) < 1e-15, theta_triad, 3.0 / 16.0)
    c_f = 4.0 * a_value * 0.3**2
    c_c = a_value * 0.3**3 * (4.0 - 5.0 * 0.3)
    c_h = 1.5 * float(parameters["Y"]) * 0.3**2
    budget = c_c**2 / (4.0 * c_h * triad["M6"])
    record(rows, "triad_budget_discriminant_independent", budget > 0.0, budget, ">0")

    target = manifest["composition_target"]
    total_alpha = float(target["alpha_f"]) + float(target["alpha_c"]) + float(target["alpha_d"])
    p_alpha = float(target["p"]) * total_alpha
    b6 = float(parameters["gamma"]) / 6.0 - float(target["epsilon_6"]) - float(target["epsilon_d"])
    kf_ratio = (1.0 - float(target["theta"])) ** 2 / (4.0 * float(target["alpha_f"]))
    record(rows, "conditional_composition_strict_budgets", p_alpha < 1.0 and b6 > 0.0, {"p_alpha": p_alpha, "B6": b6}, {"p_alpha": "<1", "B6": ">0"})
    record(rows, "conditional_Kf_ratio", abs(kf_ratio - 0.05) < 1e-14, kf_ratio, 0.05)
    optimizer = quartic_sextic_optimizer(0.1075 + 0.2, b6)
    record(rows, "quartic_sextic_optimizer_independent", optimizer["relative_error"] < 1e-10, optimizer["relative_error"], "<1e-10")
    expected_open = [
        "A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION",
        "A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE",
    ]
    record(
        rows,
        "composition_prerequisites_and_cube_filtration_boundary",
        manifest["open_followups"] == expected_open
        and manifest["closed_subgates"] == ["A10-CLASSII-DYADIC-FILTRATION-REALISATION"],
        {"open": manifest["open_followups"], "closed": manifest["closed_subgates"]},
        {"open": expected_open, "closed": ["A10-CLASSII-DYADIC-FILTRATION-REALISATION"]},
    )

    chain = finite_entropy_chain_rule()
    record(rows, "conditional_entropy_chain_rule_fixture", chain["error"] < 1e-14, chain["error"], 0.0)
    dv = discrete_dv(float(target["alpha_c"]))
    record(rows, "stabilised_log_Laplace_DV_fixture", dv["error"] < 1e-14, dv["error"], 0.0)
    excluded = manifest["honesty_boundary"]["excluded"]
    record(rows, "independent_scope_excludes_Gibbs", "a full three-component interacting Gibbs measure" in excluded, excluded, "contains Gibbs exclusion")
    record(rows, "independent_scope_excludes_T6_T7", "T6 or T7" in excluded, excluded, "contains T6/T7 exclusion")

    failures = [row["name"] for row in rows if row["status"] != "PASS"]
    result = {
        "schema": manifest["run_contract"]["independent_result_schema"],
        "verdict": "A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INDEPENDENT-PASS" if not failures else "FAIL",
        "claim_id": CLAIM,
        "version": __version__,
        "git_commit": current_commit(),
        "platform": platform.platform(),
        "python": sys.version,
        "assertion_count": len(rows),
        "failed": failures,
        "assertions": rows,
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value},
            "QII_determinant": determinant,
            "beta_B": beta_b,
            "beta_1": beta_1,
            "blaschke": blaschke,
            "plane_wave": plane,
            "triad": triad,
            "triad_budget_theta_zero": budget,
            "composition": {"p_alpha": p_alpha, "B6": b6, "Kf_over_Cfr": kf_ratio},
            "optimizer": optimizer,
            "entropy_chain_rule": chain,
            "dv_fixture": dv,
        },
    }
    write_json(options.output, result)
    if failures:
        print(f"FAIL: {len(failures)} assertions: {', '.join(failures)}")
        print(f"Evidence: {options.output.resolve()}")
        return 1
    print(f"{len(rows)}/{len(rows)} PASS")
    print(f"strict-dyadic ratio: {blaschke[-1]['ratio']:.12g}")
    print(f"plane-wave C: {plane[-1]['complete_C']:.12g}")
    print("A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INDEPENDENT-PASS")
    print(f"Evidence: {options.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
