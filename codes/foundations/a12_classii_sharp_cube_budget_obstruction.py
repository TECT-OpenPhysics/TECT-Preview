#!/usr/bin/env python3
"""Primary audit for the A12 sharp-cube scalar-budget obstruction.

This executable derives an exact lower bound for the separated sharp-cube
constant H_6=M_6^4 Q_6^2 and for the coefficient-blind six-linear envelope.
It also verifies the exact Class-II gauge-null identity B(X) JX=0, which is
the structural reason the lower-bound witness does not refute the true source.

Version: 1.0.0 (first issued 2026-07-21; this version 2026-07-21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_sharp_cube_budget_obstruction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "runs" / "2026-07-21-primary-sharp-cube-obstruction" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def gaussian_multiply(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gaussian_convolve(
    left: list[tuple[int, int]], right: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    output = [(0, 0) for _ in range(len(left) + len(right) - 1)]
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            product = gaussian_multiply(left_value, right_value)
            old = output[left_index + right_index]
            output[left_index + right_index] = (old[0] + product[0], old[1] + product[1])
    return output


def exact_l6_sixth(coefficients: list[tuple[int, int]]) -> int:
    """Return the common-scale numerator of ||sum c_n z^n||_6^6."""

    cubic = gaussian_convolve(gaussian_convolve(coefficients, coefficients), coefficients)
    return sum(real * real + imag * imag for real, imag in cubic)


def pauli() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
        np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    ]


def generators() -> list[np.ndarray]:
    return [np.pad(matrix, ((0, 1), (0, 1))) for matrix in pauli()]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def real_vector(field: np.ndarray) -> np.ndarray:
    return np.concatenate((field.real, field.imag), axis=-1)


def complex_structure() -> np.ndarray:
    identity = np.eye(3)
    zero = np.zeros((3, 3))
    return np.block([[zero, -identity], [identity, zero]])


def coefficients(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    return (
        float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator,
        float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator,
        float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator,
    )


def coefficient_matrix(field: np.ndarray, parameters: dict[str, Any]) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    field = np.asarray(field, dtype=np.complex128)
    a_value, b_value, c_value = coefficients(parameters)
    floor = float(parameters["rho_regularizer"])
    x_value = real_vector(field)
    rho = float(np.real(np.vdot(field, field)))
    eye = np.eye(6)
    matrix = np.zeros((6, 6), dtype=np.float64)
    p_vectors: list[np.ndarray] = []
    v_vectors: list[np.ndarray] = []
    for generator in generators():
        symmetric = realify(generator)
        moment = float(np.real(np.vdot(field, generator @ field)))
        q_value = moment / (rho + floor)
        p_value = 2.0 * symmetric @ x_value
        v_value = 2.0 * (symmetric - q_value * eye) @ x_value
        matrix += a_value * np.outer(p_value, p_value)
        matrix += b_value * (np.outer(p_value, v_value) + np.outer(v_value, p_value))
        matrix += c_value * np.outer(v_value, v_value)
        p_vectors.append(p_value)
        v_vectors.append(v_value)
    return matrix, p_vectors, v_vectors


def symbol_coercivity(parameters: dict[str, Any]) -> float:
    y_value = float(parameters["Y"])
    z_value = float(parameters["Z"])
    r_value = float(parameters["r"])
    stationary = max(0.0, (2.0 * r_value - z_value) / (2.0 * y_value - z_value))

    def ratio(x_value: float) -> float:
        return (y_value * x_value**2 + z_value * x_value + r_value) / (1.0 + x_value) ** 2

    return min(ratio(0.0), ratio(stationary), y_value)


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    for key in ("a1_manifest", "a12_manifest", "a12_note"):
        authority = manifest["authority"][key]
        actual = sha256(REPO / authority["path"])
        add(assertions, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    for key in ("primary", "independent", "verifier"):
        source = manifest["sources"][key]
        actual = sha256(REPO / source["path"])
        add(assertions, f"source_{key}_hash", actual == source["sha256"], actual, source["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    dimension = int(manifest["geometry"]["spatial_dimension"])
    exponent = int(manifest["geometry"]["lebsegue_exponent"])
    riesz_norm = Fraction(1, 1) / Fraction(1, 2)
    tensor_projection_lower = riesz_norm**dimension
    q_squared_lower = Fraction(dimension, 1) * tensor_projection_lower**2
    h_lower = tensor_projection_lower**4 * q_squared_lower
    scalar_envelope_lower = Fraction(dimension, 1) * tensor_projection_lower**6

    add(assertions, "riesz_exponent_is_six", exponent == 6, exponent, 6)
    add(assertions, "riesz_norm_is_exactly_two", riesz_norm == 2, str(riesz_norm), "2")
    add(assertions, "sharp_cube_dimension_is_three", dimension == 3, dimension, 3)
    add(assertions, "tensor_projection_lower_is_eight", tensor_projection_lower == 8, str(tensor_projection_lower), "8")
    add(assertions, "q_squared_lower_is_192", q_squared_lower == 192, str(q_squared_lower), "192")
    add(assertions, "h6_lower_is_786432", h_lower == 786432, str(h_lower), "786432")
    add(assertions, "scalar_envelope_lower_matches_h6_lower", scalar_envelope_lower == h_lower, str(scalar_envelope_lower), str(h_lower))

    getcontext().prec = 80
    a_value, b_value, c_value = coefficients(parameters)
    coefficient_determinant = a_value * c_value - b_value * b_value
    add(assertions, "classii_a_is_nonnegative", a_value >= 0.0, a_value, ">=0")
    add(assertions, "classii_c_is_nonnegative", c_value >= 0.0, c_value, ">=0")
    add(assertions, "classii_coefficient_matrix_is_positive_definite", coefficient_determinant > 0.0, coefficient_determinant, ">0")
    beta_operator = Decimal(str(4.0 * (a_value + 2.0 * abs(b_value) + c_value)))
    c_symbol = Decimal(str(symbol_coercivity(parameters)))
    source_base = beta_operator * beta_operator / c_symbol
    target_p = Decimal(str(manifest["budget"]["p"]))
    regulator_supremum = Decimal(str(manifest["budget"]["M_R"]))
    gamma = Decimal(str(parameters["gamma"]))
    source_allowance = gamma / (Decimal(3) * target_p)
    h_target = source_allowance / (source_base * regulator_supremum * regulator_supremum)
    h_lower_decimal = Decimal(h_lower.numerator) / Decimal(h_lower.denominator)
    obstruction_ratio = h_lower_decimal / h_target
    source_lower = source_base * regulator_supremum * regulator_supremum * h_lower_decimal

    add(assertions, "h6_exact_lower_exceeds_source_target", h_lower_decimal > h_target, decimal_string(h_lower_decimal), decimal_string(h_target))
    add(assertions, "h6_obstruction_ratio_exceeds_26000", obstruction_ratio > Decimal(26000), decimal_string(obstruction_ratio), ">26000")
    add(assertions, "source_constant_lower_exceeds_allowance", source_lower > source_allowance, decimal_string(source_lower), decimal_string(source_allowance))

    witness = manifest["finite_rational_witness"]
    frequencies = list(range(int(witness["frequency_min"]), int(witness["frequency_max"]) + 1))
    coefficients_integer = [(int(row[0]), int(row[1])) for row in witness["gaussian_integer_coefficients"]]
    projected = [value for frequency, value in zip(frequencies, coefficients_integer) if frequency <= 0]
    full_sixth = exact_l6_sixth(coefficients_integer)
    projected_sixth = exact_l6_sixth(projected)
    ratio_sixth = Fraction(projected_sixth, full_sixth)
    finite_h_lower = Fraction(dimension, 1) * ratio_sixth**dimension
    finite_h_decimal = Decimal(finite_h_lower.numerator) / Decimal(finite_h_lower.denominator)

    add(assertions, "finite_witness_frequency_range", len(frequencies) == len(coefficients_integer) == 21, [frequencies[0], frequencies[-1], len(frequencies)], [-10, 10, 21])
    add(assertions, "finite_witness_projection_has_eleven_modes", len(projected) == 11, len(projected), 11)
    add(assertions, "finite_witness_exact_lower_exceeds_target", finite_h_decimal > h_target, decimal_string(finite_h_decimal), decimal_string(h_target))
    add(assertions, "finite_witness_exact_lower_exceeds_180", finite_h_decimal > Decimal(180), decimal_string(finite_h_decimal), ">180")
    add(assertions, "finite_witness_below_sharp_asymptotic_lower", finite_h_decimal < h_lower_decimal, decimal_string(finite_h_decimal), decimal_string(h_lower_decimal))

    carrier = int(manifest["finite_rational_witness"]["dyadic_carrier"])
    shift_rows = [
        {
            "relative_frequency": frequency,
            "shifted_frequency": carrier + frequency,
            "kept_by_centered_cube": -carrier <= carrier + frequency <= carrier,
            "kept_by_half_line": frequency <= 0,
        }
        for frequency in frequencies
    ]
    add(assertions, "dyadic_carrier_exceeds_witness_degree", carrier > max(abs(value) for value in frequencies), carrier, f">{max(abs(value) for value in frequencies)}")
    add(assertions, "modulation_shift_identity_all_modes", all(row["kept_by_centered_cube"] == row["kept_by_half_line"] for row in shift_rows), shift_rows, "cube after shift equals half-line projection")

    structure = complex_structure()
    commutator_errors = [float(np.linalg.norm(realify(generator) @ structure - structure @ realify(generator))) for generator in generators()]
    add(assertions, "generators_commute_with_complex_structure", max(commutator_errors) < 1e-14, max(commutator_errors), "<1e-14")

    rng = np.random.default_rng(int(manifest["audit"]["seed"]))
    p_null_error = 0.0
    v_null_error = 0.0
    b_null_error = 0.0
    matrix_norm_max = 0.0
    matrix_minimum_eigenvalue = math.inf
    for _ in range(int(manifest["audit"]["gauge_samples"])):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        x_value = real_vector(field)
        gauge_tangent = structure @ x_value
        matrix, p_vectors, v_vectors = coefficient_matrix(field, parameters)
        normalization = max(1.0, float(np.linalg.norm(x_value)) ** 2)
        p_null_error = max(p_null_error, max(abs(float(vector @ gauge_tangent)) for vector in p_vectors) / normalization)
        v_null_error = max(v_null_error, max(abs(float(vector @ gauge_tangent)) for vector in v_vectors) / normalization)
        b_null_error = max(b_null_error, float(np.linalg.norm(matrix @ gauge_tangent)) / max(1.0, float(np.linalg.norm(matrix)) * float(np.linalg.norm(gauge_tangent))))
        matrix_norm_max = max(matrix_norm_max, float(np.linalg.norm(matrix)))
        matrix_minimum_eigenvalue = min(matrix_minimum_eigenvalue, float(np.linalg.eigvalsh(matrix)[0]))

    gauge_tolerance = float(manifest["audit"]["gauge_tolerance"])
    add(assertions, "pauli_frame_vectors_annihilate_gauge_tangent", p_null_error < gauge_tolerance, p_null_error, f"<{gauge_tolerance}")
    add(assertions, "rational_frame_vectors_annihilate_gauge_tangent", v_null_error < gauge_tolerance, v_null_error, f"<{gauge_tolerance}")
    add(assertions, "classii_matrix_annihilates_gauge_tangent", b_null_error < gauge_tolerance, b_null_error, f"<{gauge_tolerance}")
    add(assertions, "sampled_classii_matrix_is_positive_semidefinite", matrix_minimum_eigenvalue >= -gauge_tolerance, matrix_minimum_eigenvalue, f">=-{gauge_tolerance}")

    plane_field = np.asarray([1.0 + 0.0j, 0.0j, 0.0j])
    plane_matrix, _, _ = coefficient_matrix(plane_field, parameters)
    plane_tangent = structure @ real_vector(plane_field)
    plane_source = float(np.linalg.norm(plane_matrix @ plane_tangent))
    plane_envelope = float(np.linalg.norm(plane_matrix)) * float(np.linalg.norm(plane_tangent))
    add(assertions, "global_phase_plane_wave_actual_source_is_zero", plane_source < gauge_tolerance, plane_source, f"<{gauge_tolerance}")
    add(assertions, "coefficient_blind_plane_wave_envelope_is_positive", plane_envelope > 0.0 and matrix_norm_max > 0.0, [plane_envelope, matrix_norm_max], ">0")

    next_gate = manifest["consequence"]["next_gate"]
    add(assertions, "next_gate_is_coefficient_aware", "COEFFICIENT-AWARE" in next_gate, next_gate, "contains COEFFICIENT-AWARE")
    add(assertions, "next_gate_preserves_shell_localisation", "SHELL-LOCALISED" in next_gate, next_gate, "contains SHELL-LOCALISED")
    add(assertions, "package_does_not_promote_tier", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")

    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/a12-classii-sharp-cube-budget-obstruction-primary-result/1.0",
        "claim_id": "A12-CLASSII-SOURCE-SQUARE-REDUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "exact_theorem": {
            "riesz_projection_norm_L6": "2",
            "sharp_cube_maximal_lower": "8",
            "derivative_prefix_q_squared_lower": "192",
            "H6_lower": "786432",
            "coefficient_blind_scalar_envelope_lower": "786432",
            "proof": "Dyadic boundary modulation turns the centered three-cube projection into P_+ tensor P_+ tensor P_+; the exact L6 Riesz norm is 2. The same carrier gives the sqrt(3) derivative factor.",
        },
        "budget": {
            "p": str(target_p),
            "M_R": str(regulator_supremum),
            "beta_operator": str(beta_operator),
            "c_symbol": str(c_symbol),
            "source_base": decimal_string(source_base),
            "source_allowance": decimal_string(source_allowance),
            "H6_target": decimal_string(h_target),
            "H6_lower": decimal_string(h_lower_decimal),
            "obstruction_ratio": decimal_string(obstruction_ratio),
            "source_constant_lower": decimal_string(source_lower),
        },
        "finite_rational_witness": {
            "full_l6_sixth_integer": str(full_sixth),
            "projected_l6_sixth_integer": str(projected_sixth),
            "projection_ratio_sixth_numerator": str(ratio_sixth.numerator),
            "projection_ratio_sixth_denominator": str(ratio_sixth.denominator),
            "elementary_H6_lower_numerator": str(finite_h_lower.numerator),
            "elementary_H6_lower_denominator": str(finite_h_lower.denominator),
            "elementary_H6_lower_decimal": decimal_string(finite_h_decimal),
            "shift_rows": shift_rows,
        },
        "gauge_null": {
            "identity": "B(X) J X = 0",
            "p_null_error": p_null_error,
            "v_null_error": v_null_error,
            "B_null_error": b_null_error,
            "minimum_sampled_B_eigenvalue": matrix_minimum_eigenvalue,
            "plane_wave_actual_source": plane_source,
            "plane_wave_scalar_envelope": plane_envelope,
            "interpretation": "The sharp-cube carrier obstruction fires only after discarding the exact Class-II gauge-null structure.",
        },
        "negative_result": manifest["consequence"]["negative_result"],
        "next_gate": next_gate,
        "assertion_count": len(assertions),
        "assertions": assertions,
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print(f"FAIL: primary ({len(assertions) - len(failures)}/{len(assertions)})")
        for failure in failures:
            print(f"  {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"PASS: primary ({len(assertions)}/{len(assertions)})")
    print(f"H6 >= {h_lower}; target {h_target}; ratio {obstruction_ratio}")
    print(f"Finite rational witness: H6 >= {finite_h_decimal}")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    manifest = arguments.manifest if arguments.manifest.is_absolute() else REPO / arguments.manifest
    output = arguments.output if arguments.output.is_absolute() else REPO / arguments.output
    return run(manifest, output)


if __name__ == "__main__":
    raise SystemExit(main())
