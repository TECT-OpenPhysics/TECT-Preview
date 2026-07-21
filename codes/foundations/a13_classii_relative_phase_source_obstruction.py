#!/usr/bin/env python3
"""Primary audit for the A13 exact-B relative-phase source obstruction.

The audit has two roles.  First it verifies the exact Pauli/Fierz reduction,
the two independent phase-null directions, the sharp-shell commutator, and
the determinant resolvent identity.  Second it evaluates one explicit finite
Fourier polynomial by zero-padded coefficient convolution.  That polynomial
produces an opposite-corner SU(2) carrier whose asymptotic exact-B source
constant exceeds the complete production sextic allowance for every p >= 1.

This script does not claim a floating-point interval proof or an interacting
measure.  A non-importing grid/quadrature route independently reproduces the
finite certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "classii_relative_phase_source_obstruction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-07-21-primary-relative-phase-obstruction" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def pauli_generators() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
        np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    ]


def embedded_generators() -> list[np.ndarray]:
    return [np.pad(generator, ((0, 1), (0, 1))) for generator in pauli_generators()]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def real_vector(field: np.ndarray) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    return np.concatenate((field.real, field.imag))


def complex_vector(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float64)
    return vector[:3] + 1j * vector[3:]


def coefficients(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    return (
        float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
        float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator,
        float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator,
    )


def direct_matrix(field: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    x_value = real_vector(field)
    rho = float(np.real(np.vdot(field, field)))
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    eye = np.eye(6)
    result = np.zeros((6, 6), dtype=np.float64)
    for generator in embedded_generators():
        symmetric = realify(generator)
        moment = float(np.real(np.vdot(field, generator @ field)))
        q_value = moment / (rho + floor)
        p_value = 2.0 * symmetric @ x_value
        v_value = 2.0 * (symmetric - q_value * eye) @ x_value
        result += a_value * np.outer(p_value, p_value)
        result += b_value * (np.outer(p_value, v_value) + np.outer(v_value, p_value))
        result += c_value * np.outer(v_value, v_value)
    return result


def compact_matrix(field: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    x_value = real_vector(field)
    z_value = x_value.copy()
    z_value[[2, 5]] = 0.0
    jz_value = np.asarray([-z_value[3], -z_value[4], 0.0, z_value[0], z_value[1], 0.0])
    s_value = float(np.real(np.vdot(field[:2], field[:2])))
    rho = float(np.real(np.vdot(field, field)))
    floor = float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficients(parameters)
    d_value = a_value + 2.0 * b_value + c_value
    e_value = b_value + c_value
    projector = np.diag([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    p_frame = 4.0 * (s_value * projector - np.outer(jz_value, jz_value))
    ratio = s_value / (rho + floor)
    return (
        d_value * p_frame
        - 4.0 * e_value * ratio * (np.outer(z_value, x_value) + np.outer(x_value, z_value))
        + 4.0 * c_value * ratio * ratio * np.outer(x_value, x_value)
    )


def phase_tangents(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z_phase = np.asarray([1j * field[0], 1j * field[1], 0.0j])
    w_phase = np.asarray([0.0j, 0.0j, 1j * field[2]])
    return real_vector(z_phase), real_vector(w_phase)


def rotate(field: np.ndarray, theta_z: float, theta_w: float) -> np.ndarray:
    result = np.asarray(field, dtype=np.complex128).copy()
    result[:2] *= np.exp(1j * theta_z)
    result[2] *= np.exp(1j * theta_w)
    return result


def linear_convolution(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    size = len(left) + len(right) - 1
    fft_size = 1 << (size - 1).bit_length()
    transformed = np.fft.rfft(left, fft_size) * np.fft.rfft(right, fft_size)
    return np.fft.irfft(transformed, fft_size)[:size]


def l6_sixth(coefficients_value: np.ndarray) -> float:
    cubic = linear_convolution(linear_convolution(coefficients_value, coefficients_value), coefficients_value)
    return float(np.dot(cubic, cubic))


def polynomial_certificate(degree: int, exponent: float, beta_operator: float) -> dict[str, float]:
    indices = np.arange(1, degree + 1, dtype=np.float64)
    amplitudes = indices ** (-exponent)
    full = np.concatenate((amplitudes[::-1], np.asarray([0.0]), -amplitudes))
    past = np.concatenate((amplitudes[::-1], np.asarray([0.0])))

    full_l6 = l6_sixth(full)
    past_l6 = l6_sixth(past)
    cubic_current = linear_convolution(linear_convolution(past, past), past[::-1])
    nonpositive_energy = float(np.dot(cubic_current[: 2 * degree + 1], cubic_current[: 2 * degree + 1]))

    past_ratio = past_l6 / full_l6
    nonpositive_ratio = nonpositive_energy / full_l6
    spin_functional = past_ratio**3 - nonpositive_ratio**3
    source_ratio = beta_operator**2 * spin_functional
    return {
        "degree": degree,
        "coefficient_exponent": exponent,
        "full_l6_sixth": full_l6,
        "past_l6_sixth": past_l6,
        "nonpositive_cubic_energy": nonpositive_energy,
        "past_over_full": past_ratio,
        "nonpositive_over_full": nonpositive_ratio,
        "spin_functional": spin_functional,
        "source_ratio": source_ratio,
    }


def shell_commutator(parameters: dict[str, Any], seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    grid = 256
    cutoff = 8
    modes = np.arange(-cutoff, cutoff + 1)
    coefficients_value = rng.normal(size=(3, len(modes))) + 1j * rng.normal(size=(3, len(modes)))
    coordinate = np.arange(grid)
    phase = np.exp(2j * np.pi * np.outer(modes, coordinate) / grid)
    field = coefficients_value @ phase
    frequencies = np.rint(np.fft.fftfreq(grid) * grid).astype(int)
    field_hat = np.fft.fft(field, axis=1) / grid
    physical = 2.0 * math.pi * frequencies / float(parameters["Lx"])
    derivative = np.fft.ifft((1j * physical)[None, :] * (field_hat * grid), axis=1)
    current = np.zeros_like(field)
    for index in range(grid):
        current[:, index] = complex_vector(compact_matrix(field[:, index], parameters) @ real_vector(derivative[:, index]))

    shell_mask = (np.abs(frequencies) > cutoff) & (np.abs(frequencies) <= 2 * cutoff)
    current_hat = np.fft.fft(current, axis=1) / grid
    shell_current = np.fft.ifft((current_hat * shell_mask[None, :]) * grid, axis=1)
    derivative_hat = np.fft.fft(derivative, axis=1) / grid
    shell_derivative = np.fft.ifft((derivative_hat * shell_mask[None, :]) * grid, axis=1)
    commutator = np.zeros_like(field)
    for index in range(grid):
        local = compact_matrix(field[:, index], parameters) @ real_vector(shell_derivative[:, index])
        commutator[:, index] = shell_current[:, index] - complex_vector(local)
    return {
        "past_derivative_shell_norm": float(np.linalg.norm(shell_derivative)),
        "commutator_identity_error": float(np.linalg.norm(shell_current - commutator)),
        "shell_source_norm": float(np.linalg.norm(shell_current)),
    }


def internal_mass(parameters: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(parameters["family_masses"], dtype=np.float64))
    z0_value = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(z0_value, z0_value) / float(z0_value @ z0_value)
    return family + float(parameters["k_lock"]) * (np.eye(3) - projector)


def spectral_rows(parameters: dict[str, Any], scales: list[int]) -> list[dict[str, float]]:
    alpha_l = 2.0 * math.pi / float(parameters["Lx"])
    mass = internal_mass(parameters)
    direction = np.asarray([1.0, 1.0, 1.0]) / math.sqrt(3.0)
    rows: list[dict[str, float]] = []
    for scale in scales:
        k_norm = alpha_l * math.sqrt(3.0) * scale
        scalar = float(parameters["r"]) + float(parameters["Z"]) * k_norm**2 + float(parameters["Y"]) * k_norm**4
        symbol = scalar * np.eye(3) + mass
        inverse = np.linalg.inv(symbol)
        asymptotic = k_norm**4 * float(np.real(direction @ inverse @ direction))
        shell_norm = k_norm**2 / float(np.min(np.linalg.eigvalsh(symbol)))
        rows.append({"scale": scale, "k_norm": k_norm, "q4_inverse": asymptotic, "derivative_covariance_norm": shell_norm})
    return rows


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key, authority in manifest["authority"].items():
        actual = sha256(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])
    for key, source in manifest["sources"].items():
        actual = sha256(REPO / source["path"])
        add(rows, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    a_value, b_value, c_value = coefficients(parameters)
    d_value = a_value + 2.0 * b_value + c_value
    beta_operator = 4.0 * d_value
    coefficient_determinant = a_value * c_value - b_value * b_value

    add(rows, "production_coefficient_matrix_positive", a_value > 0.0 and c_value > 0.0 and coefficient_determinant > 0.0, [a_value, b_value, c_value, coefficient_determinant], "a>0,c>0,ac-b^2>0")
    add(rows, "beta_operator_derived_from_a1", abs(beta_operator - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, beta_operator, manifest["derived_oracles"]["beta_operator"])

    rng = np.random.default_rng(int(manifest["audit"]["seed"]))
    matrix_error = 0.0
    z_null_error = 0.0
    w_null_error = 0.0
    gauge_error = 0.0
    carrier_error = 0.0
    spectral_upper_error = 0.0
    for _ in range(int(manifest["audit"]["algebra_samples"])):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        direct = direct_matrix(field, parameters)
        compact = compact_matrix(field, parameters)
        matrix_error = max(matrix_error, float(np.linalg.norm(direct - compact)))
        z_phase, w_phase = phase_tangents(field)
        scale = max(1.0, float(np.linalg.norm(compact)) * float(np.linalg.norm(real_vector(field))))
        z_null_error = max(z_null_error, float(np.linalg.norm(compact @ z_phase)) / scale)
        w_null_error = max(w_null_error, float(np.linalg.norm(compact @ w_phase)) / scale)

        tangent = rng.normal(size=3) + 1j * rng.normal(size=3)
        theta_z, theta_w, tau_z, tau_w = rng.normal(size=4)
        rotated_field = rotate(field, theta_z, theta_w)
        rotated_tangent = rotate(tangent + complex_vector(tau_z * z_phase + tau_w * w_phase), theta_z, theta_w)
        left = compact_matrix(rotated_field, parameters) @ real_vector(rotated_tangent)
        right = real_vector(rotate(complex_vector(compact @ real_vector(tangent)), theta_z, theta_w))
        gauge_error = max(gauge_error, float(np.linalg.norm(left - right)) / max(1.0, float(np.linalg.norm(right))))

        doublet = rng.normal(size=2) + 1j * rng.normal(size=2)
        carrier_field = np.asarray([doublet[0], doublet[1], 0.0j])
        carrier_tangent = np.asarray([1j * doublet[0], -1j * doublet[1], 0.0j])
        actual = complex_vector(compact_matrix(carrier_field, parameters) @ real_vector(carrier_tangent))
        expected = 2j * beta_operator * np.asarray([doublet[0] * abs(doublet[1]) ** 2, -abs(doublet[0]) ** 2 * doublet[1], 0.0j])
        carrier_error = max(carrier_error, float(np.linalg.norm(actual - expected)) / max(1.0, float(np.linalg.norm(expected))))

        eigenvalues = np.linalg.eigvalsh(compact)
        s_value = float(np.real(np.vdot(field[:2], field[:2])))
        spectral_upper_error = max(spectral_upper_error, float(max(0.0, eigenvalues[-1] - beta_operator * s_value)))

    tolerance = float(manifest["audit"]["algebra_tolerance"])
    add(rows, "exact_fierz_matrix_identity", matrix_error < tolerance, matrix_error, f"<{tolerance}")
    add(rows, "doublet_phase_null", z_null_error < tolerance, z_null_error, f"<{tolerance}")
    add(rows, "singlet_phase_null", w_null_error < tolerance, w_null_error, f"<{tolerance}")
    add(rows, "local_two_phase_covariance", gauge_error < tolerance, gauge_error, f"<{tolerance}")
    add(rows, "active_su2_carrier_identity", carrier_error < tolerance, carrier_error, f"<{tolerance}")
    add(rows, "sharp_B_upper_uses_doublet_density", spectral_upper_error < tolerance, spectral_upper_error, f"<{tolerance}")

    shell = shell_commutator(parameters, int(manifest["audit"]["shell_seed"]))
    add(rows, "past_derivative_has_no_next_shell", shell["past_derivative_shell_norm"] < tolerance, shell["past_derivative_shell_norm"], f"<{tolerance}")
    add(rows, "exact_output_shell_commutator", shell["commutator_identity_error"] < tolerance, shell["commutator_identity_error"], f"<{tolerance}")
    add(rows, "nontrivial_shell_source_fixture", shell["shell_source_norm"] > 0.0, shell["shell_source_norm"], ">0")

    max_resolvent_error = 0.0
    for _ in range(int(manifest["audit"]["resolvent_samples"])):
        operator = rng.normal(size=(7, 5))
        source = rng.normal(size=7)
        p_value = float(manifest["budget"]["reference_p"])
        t_matrix = operator.T @ operator
        k_matrix = operator @ operator.T
        ell = operator.T @ source
        left = float(ell @ np.linalg.solve(np.eye(5) + p_value * t_matrix, ell))
        right = float((source @ source - source @ np.linalg.solve(np.eye(7) + p_value * k_matrix, source)) / p_value)
        max_resolvent_error = max(max_resolvent_error, abs(left - right))
    add(rows, "exact_resolvent_rebate_identity", max_resolvent_error < float(manifest["audit"]["resolvent_tolerance"]), max_resolvent_error, f"<{manifest['audit']['resolvent_tolerance']}")

    certificate = polynomial_certificate(
        int(manifest["certificate"]["degree"]),
        float(manifest["certificate"]["coefficient_exponent"]),
        beta_operator,
    )
    allowance_all_p = float(parameters["gamma"]) / 3.0
    allowance_reference = allowance_all_p / float(manifest["budget"]["reference_p"])
    add(rows, "finite_spin_functional_positive", certificate["spin_functional"] > 0.0, certificate["spin_functional"], ">0")
    add(rows, "source_ratio_exceeds_all_p_allowance", certificate["source_ratio"] > allowance_all_p, certificate["source_ratio"], allowance_all_p)
    add(rows, "source_ratio_exceeds_reference_allowance", certificate["source_ratio"] > allowance_reference, certificate["source_ratio"], allowance_reference)
    add(rows, "all_p_margin_is_robust", certificate["source_ratio"] - allowance_all_p > float(manifest["certificate"]["required_margin_over_gamma_third"]), certificate["source_ratio"] - allowance_all_p, f">{manifest['certificate']['required_margin_over_gamma_third']}")
    add(rows, "certificate_matches_recorded_oracle", abs(certificate["source_ratio"] - float(manifest["derived_oracles"]["primary_source_ratio"])) < float(manifest["audit"]["certificate_cross_tolerance"]), certificate["source_ratio"], manifest["derived_oracles"]["primary_source_ratio"])

    spectrum = spectral_rows(parameters, [int(value) for value in manifest["audit"]["carrier_scales"]])
    add(rows, "q4_covariance_limit_uses_Y", abs(spectrum[-1]["q4_inverse"] - 1.0 / float(parameters["Y"])) < float(manifest["audit"]["asymptotic_tolerance"]), spectrum[-1]["q4_inverse"], 1.0 / float(parameters["Y"]))
    add(rows, "derivative_covariance_decays", all(right["derivative_covariance_norm"] < left["derivative_covariance_norm"] for left, right in zip(spectrum, spectrum[1:])), [row["derivative_covariance_norm"] for row in spectrum], "strictly decreasing")
    decay_ratios = [right["derivative_covariance_norm"] / left["derivative_covariance_norm"] for left, right in zip(spectrum, spectrum[1:])]
    add(rows, "resolvent_operator_is_order_minus_two", max(abs(value - 0.25) for value in decay_ratios[-2:]) < float(manifest["audit"]["decay_ratio_tolerance"]), decay_ratios, "dyadic ratio -> 1/4")

    add(rows, "t049_disposition_is_negative", manifest["consequence"]["t049"] == "CLOSED-NEGATIVELY", manifest["consequence"]["t049"], "CLOSED-NEGATIVELY")
    add(rows, "tier_remains_t4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")
    add(rows, "next_gate_is_joint_not_source_only", "JOINT-SOURCE-POTENTIAL" in manifest["consequence"]["next_gate"], manifest["consequence"]["next_gate"], "contains JOINT-SOURCE-POTENTIAL")

    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/a13-classii-relative-phase-source-obstruction-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failures), "total": len(rows), "failed": len(failures)},
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value, "d": d_value, "beta_operator": beta_operator, "ac_minus_b2": coefficient_determinant},
            "algebra": {"matrix_error": matrix_error, "doublet_phase_null_error": z_null_error, "singlet_phase_null_error": w_null_error, "local_phase_covariance_error": gauge_error, "su2_carrier_error": carrier_error},
            "shell_commutator": shell,
            "resolvent_identity_error": max_resolvent_error,
            "certificate": certificate,
            "budget": {"gamma_over_three": allowance_all_p, "gamma_over_3p_reference": allowance_reference, "margin_over_all_p": certificate["source_ratio"] - allowance_all_p},
            "spectral_asymptotic": spectrum,
        },
        "honesty_boundary": manifest["honesty_boundary"],
        "next_gate": manifest["consequence"]["next_gate"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: primary ({len(rows) - len(failures)}/{len(rows)})" if not failures else f"FAIL: primary ({len(failures)} failures)")
    print(f"Relative-phase source ratio: {certificate['source_ratio']:.15g}")
    print(f"All-p sextic allowance: {allowance_all_p:.15g}")
    print(f"Evidence: {output_path}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
