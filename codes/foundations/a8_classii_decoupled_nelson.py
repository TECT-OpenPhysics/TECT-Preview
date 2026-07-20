#!/usr/bin/env python3
"""Primary audit for the decoupled Class-II Nelson bound.

The theorem proved by the accompanying note is deliberately not the original
self-coupled A7 Gibbs theorem.  A value field Z supplies the positive
coefficient B(Z), while an independent Gaussian copy Y supplies the
derivatives.  Conditional Gaussian integration then gives an exact det_2
formula.  A cutoff-independent Schatten-2 estimate and the production sextic
term yield every fixed p-th negative exponential moment.

All numerical values are derived from the hash-pinned A1 and A7 manifests.
The executable checks finite-dimensional identities and constants; the
all-cutoff statement is the analytic theorem in the proof note.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM_ID = "A8-CLASSII-DECOUPLED-NELSON-BOUND"
DEFAULT_MANIFEST = REPO / "claims" / CLAIM_ID / "classii_decoupled_nelson_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-20-primary-decoupled-nelson" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def generators() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    ]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def classii_coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def coefficient_matrix(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    a_value, b_value, c_value = classii_coefficients(params)
    x_value = np.concatenate((field.real, field.imag))
    rho = float(np.real(np.vdot(field, field)))
    eps = float(params["rho_regularizer"])
    result = np.zeros((6, 6), dtype=np.float64)
    for generator in generators():
        s_matrix = realify(generator)
        transformed = generator @ field
        q_value = float(np.real(np.vdot(field, transformed))) / (rho + eps)
        p_value = 2.0 * (s_matrix @ x_value)
        v_value = 2.0 * ((s_matrix - q_value * np.eye(6)) @ x_value)
        result += (
            a_value * np.outer(p_value, p_value)
            + b_value * (np.outer(p_value, v_value) + np.outer(v_value, p_value))
            + c_value * np.outer(v_value, v_value)
        )
    return result


def internal_mass(params: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(params["family_masses"], dtype=np.float64))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, z0.conjugate()) / float(np.real(np.vdot(z0, z0)))
    complex_mass = family + float(params["k_lock"]) * (np.eye(3) - projector)
    return realify(complex_mass)


def symbol_coercivity(params: dict[str, Any]) -> dict[str, float]:
    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    denominator = 2.0 * y_value - z_value
    stationary = max(0.0, (2.0 * r_value - z_value) / denominator)

    def ratio(x_value: float) -> float:
        return (y_value * x_value**2 + z_value * x_value + r_value) / (1.0 + x_value) ** 2

    candidates = {"zero": ratio(0.0), "stationary": ratio(stationary), "infinity": y_value}
    return {
        "stationary_k2": stationary,
        "c_symbol": min(candidates.values()),
        "zero_ratio": candidates["zero"],
        "stationary_ratio": candidates["stationary"],
        "infinity_ratio": candidates["infinity"],
    }


def lattice_sum_upper(length: float) -> float:
    alpha = 2.0 * math.pi / length
    # ||n||_infinity=m contains 24m^2+2 points and |n|>=m.
    return 1.0 + alpha**-4 * (4.0 * math.pi**2 + math.pi**4 / 45.0)


def partial_lattice_sum(length: float, cutoff: int) -> float:
    alpha = 2.0 * math.pi / length
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.float64)
    n1, n2, n3 = np.meshgrid(axis, axis, axis, indexing="ij")
    k2 = alpha**2 * (n1**2 + n2**2 + n3**2)
    return float(np.sum((1.0 + k2) ** -2))


def covariance_root(index: tuple[int, int, int], params: dict[str, Any], mass: np.ndarray) -> np.ndarray:
    alpha = 2.0 * math.pi / float(params["Lx"])
    k2 = alpha**2 * float(sum(component * component for component in index))
    scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    symbol = scalar * np.eye(6) + mass
    eigenvalues, basis = np.linalg.eigh(symbol)
    return (basis * (1.0 / np.sqrt(eigenvalues))) @ basis.T


def finite_operator_audit(
    field: np.ndarray,
    params: dict[str, Any],
    c_symbol: float,
    lattice_upper: float,
    cutoff: int,
    modulation: float,
    p_value: float,
) -> dict[str, Any]:
    b_zero = coefficient_matrix(field, params)
    mass = internal_mass(params)
    modes = [
        (i, j, k)
        for i in range(-cutoff, cutoff + 1)
        for j in range(-cutoff, cutoff + 1)
        for k in range(-cutoff, cutoff + 1)
    ]
    roots = {mode: covariance_root(mode, params, mass) for mode in modes}
    dimension = 6 * len(modes)
    operator = np.zeros((dimension, dimension), dtype=np.float64)
    alpha = 2.0 * math.pi / float(params["Lx"])

    def coefficient_mode(delta: tuple[int, int, int]) -> np.ndarray | None:
        if delta == (0, 0, 0):
            return b_zero
        if delta in ((1, 0, 0), (-1, 0, 0)):
            return 0.5 * modulation * b_zero
        return None

    for row_index, left in enumerate(modes):
        left_k = alpha * np.asarray(left, dtype=np.float64)
        for column_index, right in enumerate(modes):
            delta = tuple(left[axis] - right[axis] for axis in range(3))
            b_hat = coefficient_mode(delta)
            if b_hat is None:
                continue
            right_k = alpha * np.asarray(right, dtype=np.float64)
            block = float(left_k @ right_k) * (roots[left] @ b_hat @ roots[right])
            row = slice(6 * row_index, 6 * (row_index + 1))
            column = slice(6 * column_index, 6 * (column_index + 1))
            operator[row, column] = block

    symmetry_error = float(np.max(np.abs(operator - operator.T)))
    eigenvalues = np.linalg.eigvalsh(0.5 * (operator + operator.T))
    hs_squared = float(np.sum(operator * operator))
    trace_value = float(np.trace(operator))
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    b_l2_squared = volume * (1.0 + 0.5 * modulation**2) * float(np.sum(b_zero * b_zero))
    hs_upper = lattice_upper * b_l2_squared / (volume * c_symbol**2)

    derivative_covariance = np.zeros((6, 6), dtype=np.float64)
    for mode in modes:
        alpha_mode = alpha * np.asarray(mode, dtype=np.float64)
        c_matrix = roots[mode] @ roots[mode]
        derivative_covariance += float(alpha_mode @ alpha_mode) * c_matrix / volume
    direct_counterterm = 0.5 * volume * float(np.trace(b_zero @ derivative_covariance))
    spectral_counterterm = 0.5 * trace_value
    # The analytic operator is PSD. Clip the roundoff-scale negative tail in
    # both terms so the finite-dimensional det_2 diagnostic uses one spectrum.
    clipped_eigenvalues = np.maximum(eigenvalues, 0.0)
    det2_log_moment = 0.5 * float(
        np.sum(p_value * clipped_eigenvalues - np.log1p(p_value * clipped_eigenvalues))
    )
    det2_hs_upper = 0.25 * p_value**2 * hs_squared
    return {
        "cutoff": cutoff,
        "dimension": dimension,
        "modulation": modulation,
        "p": p_value,
        "symmetry_error": symmetry_error,
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "maximum_eigenvalue": float(np.max(eigenvalues)),
        "trace": trace_value,
        "counterterm_direct": direct_counterterm,
        "counterterm_spectral": spectral_counterterm,
        "counterterm_absolute_error": abs(direct_counterterm - spectral_counterterm),
        "hs_squared": hs_squared,
        "b_l2_squared": b_l2_squared,
        "hs_upper": hs_upper,
        "hs_ratio_to_upper": hs_squared / hs_upper,
        "det2_log_moment": det2_log_moment,
        "det2_hs_upper": det2_hs_upper,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    a1_path = REPO / authority["production_functional_manifest"]["path"]
    a7_path = REPO / authority["a7_composite_manifest"]["path"]
    production = json.loads(a1_path.read_text(encoding="utf-8"))
    a7_manifest = json.loads(a7_path.read_text(encoding="utf-8"))
    params = production["parameters"]
    audit = manifest["audit"]
    assertions: list[dict[str, Any]] = []

    add("A1_authority_hash_matches", sha256(a1_path) == authority["production_functional_manifest"]["sha256"], sha256(a1_path), authority["production_functional_manifest"]["sha256"], assertions)
    add("A7_authority_hash_matches", sha256(a7_path) == authority["a7_composite_manifest"]["sha256"], sha256(a7_path), authority["a7_composite_manifest"]["sha256"], assertions)

    a_value, b_value, c_value = classii_coefficients(params)
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    q_eigenvalues = np.linalg.eigvalsh(q_matrix)
    add("production_ClassII_matrix_is_positive_definite", float(q_eigenvalues[0]) > 0.0, q_eigenvalues.tolist(), ">0", assertions)

    mass = internal_mass(params)
    mass_eigenvalues = np.linalg.eigvalsh(mass)
    add("internal_mass_is_positive_semidefinite", float(mass_eigenvalues[0]) > -float(audit["matrix_tolerance"]), mass_eigenvalues.tolist(), ">=-tolerance", assertions)

    coercivity = symbol_coercivity(params)
    add("q4_symbol_has_global_coercivity", coercivity["c_symbol"] > 0.0, coercivity, ">0", assertions)
    stationary = coercivity["stationary_k2"]
    step = float(audit["coercivity_difference_step"])
    left = max(0.0, stationary - step)
    right = stationary + step
    y_value, z_value, r_value = float(params["Y"]), float(params["Z"]), float(params["r"])
    ratio = lambda value: (y_value * value**2 + z_value * value + r_value) / (1.0 + value) ** 2
    add("coercivity_stationary_point_is_a_minimum", ratio(stationary) <= min(ratio(left), ratio(right)), {"left": ratio(left), "center": ratio(stationary), "right": ratio(right)}, "center<=neighbors", assertions)

    beta_bound = 12.0 * a_value + 48.0 * abs(b_value) + 48.0 * c_value
    rng = np.random.default_rng(int(audit["seed"]))
    maximum_ratio = 0.0
    minimum_b_eigenvalue = math.inf
    for _ in range(int(audit["coefficient_samples"])):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        rho = float(np.real(np.vdot(field, field)))
        b_matrix = coefficient_matrix(field, params)
        maximum_ratio = max(maximum_ratio, float(np.linalg.norm(b_matrix, ord="fro")) / rho)
        minimum_b_eigenvalue = min(minimum_b_eigenvalue, float(np.linalg.eigvalsh(b_matrix)[0]))
    add("sampled_ClassII_coefficient_is_positive_semidefinite", minimum_b_eigenvalue > -float(audit["matrix_tolerance"]), minimum_b_eigenvalue, ">=-tolerance", assertions)
    add("sampled_ClassII_coefficient_obeys_derived_beta_rho_bound", maximum_ratio <= beta_bound * (1.0 + float(audit["relative_tolerance"])), {"sample_max": maximum_ratio, "beta": beta_bound}, "sample_max<=beta", assertions)

    length = float(params["Lx"])
    lattice_upper = lattice_sum_upper(length)
    lattice_rows = [
        {"cutoff": cutoff, "partial_sum": partial_lattice_sum(length, cutoff)}
        for cutoff in audit["lattice_cutoffs"]
    ]
    add("lattice_Hminus2_sum_is_monotone", all(lattice_rows[index]["partial_sum"] < lattice_rows[index + 1]["partial_sum"] for index in range(len(lattice_rows) - 1)), lattice_rows, "strictly increasing", assertions)
    add("analytic_lattice_shell_bound_encloses_partial_sums", all(row["partial_sum"] < lattice_upper for row in lattice_rows), {"rows": lattice_rows, "upper": lattice_upper}, "partial<upper", assertions)

    test_field = np.asarray(audit["test_field_real"], dtype=np.float64) + 1j * np.asarray(audit["test_field_imag"], dtype=np.float64)
    operator = finite_operator_audit(
        test_field,
        params,
        coercivity["c_symbol"],
        lattice_upper,
        int(audit["operator_cutoff"]),
        float(audit["coefficient_modulation"]),
        float(audit["determinant_p"]),
    )
    add("variable_background_operator_is_self_adjoint", operator["symmetry_error"] < float(audit["matrix_tolerance"]), operator["symmetry_error"], audit["matrix_tolerance"], assertions)
    add("variable_background_operator_is_positive", operator["minimum_eigenvalue"] > -float(audit["matrix_tolerance"]), operator["minimum_eigenvalue"], ">=-tolerance", assertions)
    add("Schatten2_bound_encloses_variable_background", operator["hs_squared"] <= operator["hs_upper"] * (1.0 + float(audit["relative_tolerance"])), operator, "HS^2<=analytic upper", assertions)
    add("counterterm_equals_one_half_operator_trace", operator["counterterm_absolute_error"] < float(audit["trace_tolerance"]), operator["counterterm_absolute_error"], audit["trace_tolerance"], assertions)
    add("det2_log_moment_is_nonnegative", operator["det2_log_moment"] >= -float(audit["matrix_tolerance"]), operator["det2_log_moment"], ">=0", assertions)
    add("det2_log_moment_obeys_HS_bound", operator["det2_log_moment"] <= operator["det2_hs_upper"] * (1.0 + float(audit["relative_tolerance"])), operator, "log moment<=p^2 HS^2/4", assertions)

    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    regulator_bound = float(manifest["regulator_class"]["multiplier_supremum_bound"])
    trace_constant = regulator_bound**4 * lattice_upper / (
        volume * coercivity["c_symbol"] ** 2
    )
    nelson_constant = 0.25 * beta_bound**2 * trace_constant
    lambda_negative = max(-float(params["lambda"]), 0.0)
    gamma = float(params["gamma"])
    p_rows: list[dict[str, float]] = []
    polynomial_grid_errors: list[float] = []
    for p_value in audit["p_values"]:
        p_float = float(p_value)
        quartic_coefficient = p_float**2 * nelson_constant + p_float * lambda_negative / 4.0
        sextic_coefficient = p_float * gamma / 6.0
        rho_star = 2.0 * quartic_coefficient / (3.0 * sextic_coefficient)
        pointwise_maximum = 4.0 * quartic_coefficient**3 / (27.0 * sextic_coefficient**2)
        grid = np.linspace(0.0, 2.0 * rho_star, int(audit["polynomial_grid_points"]))
        values = quartic_coefficient * grid**2 - sextic_coefficient * grid**3
        grid_maximum = float(np.max(values))
        polynomial_grid_errors.append(abs(grid_maximum - pointwise_maximum) / max(1.0, abs(pointwise_maximum)))
        p_rows.append(
            {
                "p": p_float,
                "quartic_coefficient": quartic_coefficient,
                "sextic_coefficient": sextic_coefficient,
                "rho_star": rho_star,
                "pointwise_log_bound": pointwise_maximum,
                "volume_log_bound": volume * pointwise_maximum,
                "grid_maximum": grid_maximum,
            }
        )
    add("sextic_absorption_maximum_matches_direct_grid", max(polynomial_grid_errors) < float(audit["polynomial_relative_tolerance"]), max(polynomial_grid_errors), audit["polynomial_relative_tolerance"], assertions)
    add("decoupled_Nelson_constants_are_finite_for_all_tested_p", all(math.isfinite(row["volume_log_bound"]) and row["volume_log_bound"] > 0.0 for row in p_rows), p_rows, "finite positive", assertions)

    closed = manifest["honesty_boundary"]["closed"]
    excluded = manifest["honesty_boundary"]["excluded"]
    add("full_sequence_decoupled_density_convergence_is_declared", any("full-sequence" in item for item in closed), closed, "declared", assertions)
    add("self_coupled_A7_measure_remains_excluded", any("self-coupled" in item for item in excluded), excluded, "explicit exclusion", assertions)
    add("adapted_drift_gate_is_named", manifest["open_followup"] == "A7-CLASSII-SELF-COUPLING-INTERPOLATION", manifest["open_followup"], "A7-CLASSII-SELF-COUPLING-INTERPOLATION", assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    verdict = "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-PASS" if not failures else "A8-CLASSII-DECOUPLED-NELSON-PRIMARY-FAIL"
    config = {
        "seed": audit["seed"],
        "coefficient_samples": audit["coefficient_samples"],
        "lattice_cutoffs": audit["lattice_cutoffs"],
        "operator_cutoff": audit["operator_cutoff"],
        "coefficient_modulation": audit["coefficient_modulation"],
        "determinant_p": audit["determinant_p"],
        "p_values": audit["p_values"],
        "regulator_multiplier_bound": regulator_bound,
    }
    output = {
        "schema": "tect/a8-classii-decoupled-nelson-primary-result/1.0",
        "claim_id": CLAIM_ID,
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "config": config,
        "config_sha256": canonical_digest(config),
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value, "Q_eigenvalues": q_eigenvalues.tolist()},
            "internal_mass_eigenvalues": mass_eigenvalues.tolist(),
            "symbol_coercivity": coercivity,
            "beta_B": beta_bound,
            "sample_max_B_over_rho": maximum_ratio,
            "lattice_sum": {"upper": lattice_upper, "partials": lattice_rows},
            "trace_ideal_constant": trace_constant,
            "nelson_quartic_constant": nelson_constant,
            "operator": operator,
            "p_bounds": p_rows,
            "theorem": manifest["theorem"],
        },
        "assertions": assertions,
        "assertion_summary": {"passed": len(assertions) - len(failures), "total": len(assertions)},
        "failures": failures,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
        },
        "not_closed_here": excluded,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['assertion_summary']['passed']}/{output['assertion_summary']['total']} PASS")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
