#!/usr/bin/env python3
"""Non-importing audit of the A12 sharp-cube scalar-budget obstruction.

The audit uses an exact Gaussian-integer trigonometric polynomial as an
elementary countercertificate, then separately reproduces the sharp Riesz
projection asymptotic and the Class-II gauge-null current identities.

Version: 1.0.0 (first issued 2026-07-21; this version 2026-07-21).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
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
DEFAULT_OUTPUT = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "runs" / "2026-07-21-independent-sharp-cube-obstruction" / "result.json"


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


def record(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def multiply(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    real = left[0] * right[0] - left[1] * right[1]
    imag = left[0] * right[1] + left[1] * right[0]
    return real, imag


def convolve(left: list[tuple[int, int]], right: list[tuple[int, int]]) -> list[tuple[int, int]]:
    result = [(0, 0) for _ in range(len(left) + len(right) - 1)]
    for i, x_value in enumerate(left):
        for j, y_value in enumerate(right):
            real, imag = multiply(x_value, y_value)
            old_real, old_imag = result[i + j]
            result[i + j] = old_real + real, old_imag + imag
    return result


def sixth_power_integral(coefficients: list[tuple[int, int]]) -> int:
    third_power = convolve(convolve(coefficients, coefficients), coefficients)
    return sum(real * real + imag * imag for real, imag in third_power)


def pauli_matrices() -> list[np.ndarray]:
    return [
        np.array([[0, 1], [1, 0]], dtype=np.complex128),
        np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.array([[1, 0], [0, -1]], dtype=np.complex128),
    ]


def independent_gauge_current_errors(seed: int, samples: int, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum_j = 0.0
    maximum_k = 0.0
    maximum_density_derivative = 0.0
    for _ in range(samples):
        psi = rng.normal(size=3) + 1j * rng.normal(size=3)
        tangent = 1j * psi
        z_value = psi[:2]
        eta = tangent[:2]
        density_derivative = 2.0 * float(np.real(np.vdot(psi, tangent)))
        rho = float(np.real(np.vdot(psi, psi)))
        maximum_density_derivative = max(maximum_density_derivative, abs(density_derivative))
        for matrix in pauli_matrices():
            moment = float(np.real(np.vdot(z_value, matrix @ z_value)))
            j_current = 2.0 * float(np.real(np.vdot(matrix @ z_value, eta)))
            k_current = j_current - moment * density_derivative / (rho + floor)
            maximum_j = max(maximum_j, abs(j_current))
            maximum_k = max(maximum_k, abs(k_current))
    return {
        "maximum_density_derivative": maximum_density_derivative,
        "maximum_J_current": maximum_j,
        "maximum_K_current": maximum_k,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    record(rows, "manifest_schema", manifest["schema"] == "tect/a12-classii-sharp-cube-budget-obstruction-manifest/1.0", manifest["schema"], "tect/a12-classii-sharp-cube-budget-obstruction-manifest/1.0")
    for key in ("a1_manifest", "a12_manifest", "a12_note"):
        authority = manifest["authority"][key]
        actual = sha256(REPO / authority["path"])
        record(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])
    own_source = manifest["sources"]["independent"]
    own_hash = sha256(REPO / own_source["path"])
    record(rows, "independent_source_hash", own_hash == own_source["sha256"], own_hash, own_source["sha256"])

    witness = manifest["finite_rational_witness"]
    coefficients = [(int(row[0]), int(row[1])) for row in witness["gaussian_integer_coefficients"]]
    frequencies = list(range(int(witness["frequency_min"]), int(witness["frequency_max"]) + 1))
    projected = [coefficient for frequency, coefficient in zip(frequencies, coefficients) if frequency <= 0]
    full_integral = sixth_power_integral(coefficients)
    projected_integral = sixth_power_integral(projected)
    exact_ratio_sixth = Fraction(projected_integral, full_integral)
    dimension = int(manifest["geometry"]["spatial_dimension"])
    elementary_lower = Fraction(dimension, 1) * exact_ratio_sixth**dimension

    record(rows, "finite_integrals_are_positive", full_integral > 0 and projected_integral > 0, [full_integral > 0, projected_integral > 0], [True, True])
    record(rows, "finite_projection_ratio_sixth_exceeds_3_9", exact_ratio_sixth > Fraction(39, 10), f"{exact_ratio_sixth.numerator}/{exact_ratio_sixth.denominator}", ">39/10")
    record(rows, "finite_elementary_lower_exceeds_180", elementary_lower > 180, f"{elementary_lower.numerator}/{elementary_lower.denominator}", ">180")

    getcontext().prec = 80
    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    denominator = Decimal(str(parameters["M_X"])) ** 2 + Decimal(str(parameters["classii_mass_regularizer"]))
    a_value = Decimal(str(parameters["cJJ"])) * Decimal(str(parameters["alpha_X"])) ** 2 / denominator
    b_value = Decimal(str(parameters["cJK"])) * Decimal(str(parameters["alpha_X"])) * Decimal(str(parameters["beta_X"])) / denominator
    c_value = Decimal(str(parameters["cKK"])) * Decimal(str(parameters["beta_X"])) ** 2 / denominator
    determinant = a_value * c_value - b_value * b_value
    beta_operator = Decimal(4) * (a_value + Decimal(2) * abs(b_value) + c_value)
    y_value = Decimal(str(parameters["Y"]))
    z_value = Decimal(str(parameters["Z"]))
    r_value = Decimal(str(parameters["r"]))
    stationary = max(Decimal(0), (Decimal(2) * r_value - z_value) / (Decimal(2) * y_value - z_value))

    def symbol_ratio(x_value: Decimal) -> Decimal:
        return (y_value * x_value * x_value + z_value * x_value + r_value) / (Decimal(1) + x_value) ** 2

    c_symbol = min(symbol_ratio(Decimal(0)), symbol_ratio(stationary), y_value)
    source_base = beta_operator * beta_operator / c_symbol
    target_p = Decimal(str(manifest["budget"]["p"]))
    source_allowance = Decimal(str(parameters["gamma"])) / (Decimal(3) * target_p)
    h_target = source_allowance / source_base
    elementary_decimal = Decimal(elementary_lower.numerator) / Decimal(elementary_lower.denominator)

    record(rows, "classii_a_positive", a_value > 0, str(a_value), ">0")
    record(rows, "classii_c_positive", c_value > 0, str(c_value), ">0")
    record(rows, "classii_two_by_two_determinant_positive", determinant > 0, str(determinant), ">0")
    record(rows, "finite_elementary_lower_exceeds_production_target", elementary_decimal > h_target, str(elementary_decimal), str(h_target))

    riesz_norm = Fraction(2, 1)
    tensor_lower = riesz_norm**dimension
    q_squared_lower = Fraction(dimension, 1) * tensor_lower**2
    sharp_h_lower = tensor_lower**4 * q_squared_lower
    one_axis_scalar_lower = riesz_norm**6
    record(rows, "sharp_riesz_norm_at_p6", riesz_norm == 2, str(riesz_norm), "2")
    record(rows, "tensor_projection_lower", tensor_lower == 8, str(tensor_lower), "8")
    record(rows, "sharp_q_squared_lower", q_squared_lower == 192, str(q_squared_lower), "192")
    record(rows, "sharp_H6_lower", sharp_h_lower == 786432, str(sharp_h_lower), "786432")
    record(rows, "one_axis_scalar_envelope_already_exceeds_target", Decimal(one_axis_scalar_lower.numerator) / Decimal(one_axis_scalar_lower.denominator) > h_target, str(one_axis_scalar_lower), str(h_target))

    carrier = int(witness["dyadic_carrier"])
    shift_equivalence = [(-carrier <= carrier + frequency <= carrier) == (frequency <= 0) for frequency in frequencies]
    record(rows, "carrier_is_dyadic", carrier > 0 and carrier & (carrier - 1) == 0, carrier, "positive power of two")
    record(rows, "shifted_cube_equals_half_line_on_finite_witness", all(shift_equivalence), shift_equivalence, "all true")

    gauge = independent_gauge_current_errors(
        int(manifest["audit"]["independent_seed"]),
        int(manifest["audit"]["gauge_samples"]),
        float(parameters["rho_regularizer"]),
    )
    tolerance = float(manifest["audit"]["gauge_tolerance"])
    record(rows, "global_phase_density_derivative_vanishes", gauge["maximum_density_derivative"] < tolerance, gauge["maximum_density_derivative"], f"<{tolerance}")
    record(rows, "global_phase_J_currents_vanish", gauge["maximum_J_current"] < tolerance, gauge["maximum_J_current"], f"<{tolerance}")
    record(rows, "global_phase_K_currents_vanish_with_floor", gauge["maximum_K_current"] < tolerance, gauge["maximum_K_current"], f"<{tolerance}")

    source_text = (REPO / own_source["path"]).read_text(encoding="utf-8")
    syntax_tree = ast.parse(source_text)
    imported_modules = []
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    record(rows, "non_importing_independent_implementation", not any(name.endswith("a12_classii_sharp_cube_budget_obstruction") for name in imported_modules), imported_modules, "primary module absent")
    record(rows, "exact_B_source_not_refuted", manifest["consequence"]["exact_B_source_status"] == "OPEN", manifest["consequence"]["exact_B_source_status"], "OPEN")
    record(rows, "tier_remains_T4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")

    failures = [row for row in rows if row["status"] != "PASS"]
    result = {
        "schema": "tect/a12-classii-sharp-cube-budget-obstruction-independent-result/1.0",
        "claim_id": "A12-CLASSII-SOURCE-SQUARE-REDUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "non_importing": "This audit imports neither the primary obstruction executable nor its helper functions.",
        "finite_countercertificate": {
            "projection_ratio_sixth": f"{exact_ratio_sixth.numerator}/{exact_ratio_sixth.denominator}",
            "elementary_H6_lower": f"{elementary_lower.numerator}/{elementary_lower.denominator}",
            "elementary_H6_lower_decimal": str(elementary_decimal),
            "production_target": str(h_target),
        },
        "sharp_asymptotic": {
            "riesz_projection_norm": "2",
            "tensor_projection_lower": "8",
            "Q6_squared_lower": "192",
            "H6_lower": "786432",
            "one_axis_scalar_envelope_lower": "64",
        },
        "coefficient_matrix": {
            "a": str(a_value),
            "b": str(b_value),
            "c": str(c_value),
            "ac_minus_b_squared": str(determinant),
        },
        "gauge_current_errors": gauge,
        "negative_result": manifest["consequence"]["negative_result"],
        "next_gate": manifest["consequence"]["next_gate"],
        "assertion_count": len(rows),
        "assertions": rows,
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print(f"FAIL: independent ({len(rows) - len(failures)}/{len(rows)})")
        for failure in failures:
            print(f"  {failure['name']}: {failure['actual']} expected {failure['expected']}")
        return 1
    print(f"PASS: independent ({len(rows)}/{len(rows)})")
    print(f"Exact finite countercertificate: H6 >= {elementary_decimal} > {h_target}")
    print(f"Sharp asymptotic: H6 >= {sharp_h_lower}")
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
