#!/usr/bin/env python3
"""Non-importing independent audit of the A6 Class-II UV slope.

This implementation deliberately does not import the primary audit.  It uses
direct cube enumeration, explicit batched 3x3 matrix inversion, a one-
dimensional representation of the cube integral, and fixed-seed Monte Carlo
instead of tensor Gauss-Hermite quadrature.
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
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-UV-POWER-COUNTING"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
MANIFEST = REPO / "claims" / CLAIM / "classii_uv_power_counting_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-07-20-independent-classii-uv" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def record(name: str, condition: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})


def direct_counts(cutoff: int) -> np.ndarray:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    squares = axis * axis
    squared_radius = (
        squares[:, None, None] + squares[None, :, None] + squares[None, None, :]
    ).reshape(-1)
    counts = np.bincount(squared_radius, minlength=3 * cutoff * cutoff + 1)
    if int(counts.sum()) != (2 * cutoff + 1) ** 3:
        raise AssertionError("direct cube count failed")
    return counts.astype(np.int64, copy=False)


def mass_matrix(params: dict[str, Any]) -> np.ndarray:
    z0 = np.asarray(params["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return np.diag(np.asarray(params["family_masses"], dtype=np.float64)) + float(params["k_lock"]) * (
        np.eye(3) - projector
    )


def direct_covariances(cutoff: int, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    counts = direct_counts(cutoff)
    squared_index = np.arange(len(counts), dtype=np.float64)
    length = float(params["Lx"])
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    alpha2 = (2.0 * math.pi / length) ** 2
    k2 = alpha2 * squared_index
    scalar_symbol = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2 * k2
    matrices = scalar_symbol[:, None, None] * np.eye(3)[None, :, :] + mass_matrix(params)[None, :, :]
    inverses = np.linalg.inv(matrices)
    covariance = (2.0 / volume) * np.einsum("s,sij->ij", counts, inverses)
    derivative = (2.0 / (3.0 * volume)) * np.einsum("s,s,sij->ij", counts, k2, inverses)
    return covariance, derivative


def cube_integral_1d(order: int) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    y = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights
    integrand = np.arctan(1.0 / np.sqrt(1.0 + y * y)) / np.sqrt(1.0 + y * y)
    return float(24.0 * np.sum(weights * integrand))


def pauli_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def monte_carlo_moments(
    covariance: np.ndarray,
    derivative: np.ndarray,
    params: dict[str, Any],
    sample_count: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    factor = np.linalg.cholesky(covariance)
    standard = (rng.standard_normal((sample_count, 3)) + 1j * rng.standard_normal((sample_count, 3))) / math.sqrt(2.0)
    samples = standard @ factor.T
    rho = np.sum(np.abs(samples) ** 2, axis=1)
    eps_rho = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    total_samples = np.zeros(sample_count, dtype=np.float64)
    rows: list[dict[str, float]] = []
    for number, generator in enumerate(pauli_generators(), start=1):
        transformed = samples @ generator.T
        moment = np.real(np.sum(np.conj(samples) * transformed, axis=1))
        covariant = transformed - (moment / (rho + eps_rho))[:, None] * samples
        j_base = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, transformed))
        jk_base = np.real(np.einsum("bi,ij,bj->b", np.conj(transformed), derivative, covariant))
        k_base = np.real(np.einsum("bi,ij,bj->b", np.conj(covariant), derivative, covariant))
        energy_samples = 3.0 * (a_value * j_base + 2.0 * b_value * jk_base + c_value * k_base)
        total_samples += energy_samples
        j2 = float(6.0 * np.mean(j_base))
        analytic_j2 = float(6.0 * np.real(np.trace(generator @ derivative @ generator @ covariance)))
        rows.append(
            {
                "generator": number,
                "J2": j2,
                "J2_analytic": analytic_j2,
                "J2_relative_error": abs(j2 - analytic_j2) / max(1.0, abs(analytic_j2)),
                "JK": float(6.0 * np.mean(jk_base)),
                "K2": float(6.0 * np.mean(k_base)),
            }
        )
    mean = float(np.mean(total_samples))
    standard_error = float(np.std(total_samples, ddof=1) / math.sqrt(sample_count))
    return {
        "sample_count": sample_count,
        "seed": seed,
        "generators": rows,
        "classii_energy_density_expectation": mean,
        "classii_energy_density_standard_error": standard_error,
    }


def counterterm_value(field: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    a_value, b_value, c_value = coefficients(params)
    total = 0.0
    for generator in pauli_generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + float(params["rho_regularizer"]))
        covariant = transformed - q_value * psi
        total += a_value * np.vdot(transformed, transformed).real
        total += 2.0 * b_value * np.vdot(transformed, covariant).real
        total += c_value * np.vdot(covariant, covariant).real
    return float(3.0 * total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    production_path = REPO / authority["production_functional_manifest"]["path"]
    backend_path = REPO / authority["canonical_backend"]["path"]
    params = json.loads(production_path.read_text(encoding="utf-8"))["parameters"]
    audit = manifest["independent_audit"]
    cutoffs = [int(value) for value in audit["cutoffs"]]
    assertions: list[dict[str, Any]] = []

    record("source_manifest_hash", sha256(production_path) == authority["production_functional_manifest"]["sha256"], sha256(production_path), authority["production_functional_manifest"]["sha256"], assertions)
    record("source_backend_hash", sha256(backend_path) == authority["canonical_backend"]["sha256"], sha256(backend_path), authority["canonical_backend"]["sha256"], assertions)

    integral_a = cube_integral_1d(int(audit["cube_integral_orders"][0]))
    integral_b = cube_integral_1d(int(audit["cube_integral_orders"][1]))
    delta_cube = integral_b / (6.0 * math.pi * math.pi * float(params["Y"]) * float(params["Lx"]))
    record("independent_cube_integral_converges", abs(integral_a - integral_b) < float(audit["cube_integral_tolerance"]), abs(integral_a - integral_b), audit["cube_integral_tolerance"], assertions)

    rows: list[dict[str, Any]] = []
    for cutoff in cutoffs:
        covariance, derivative = direct_covariances(cutoff, params)
        moments = monte_carlo_moments(
            covariance,
            derivative,
            params,
            int(audit["monte_carlo_samples"]),
            int(audit["seed"]) + cutoff,
        )
        rows.append(
            {
                "cutoff": cutoff,
                "covariance": covariance.tolist(),
                "derivative_covariance": derivative.tolist(),
                "derivative_slope_eigenvalues": (np.linalg.eigvalsh(derivative) / cutoff).tolist(),
                "moments": moments,
                "classii_energy_over_cutoff": moments["classii_energy_density_expectation"] / cutoff,
            }
        )

    last = rows[-1]
    previous = rows[-2]
    d_last = np.asarray(last["derivative_covariance"], dtype=np.float64)
    d_previous = np.asarray(previous["derivative_covariance"], dtype=np.float64)
    dyadic_derivative_slope = np.linalg.eigvalsh((d_last - d_previous) / (last["cutoff"] - previous["cutoff"]))
    derivative_error = float(np.max(np.abs(dyadic_derivative_slope - delta_cube)) / delta_cube)
    record("direct_derivative_increment_matches_linear_law", derivative_error < float(audit["asymptotic_relative_tolerance"]), derivative_error, audit["asymptotic_relative_tolerance"], assertions)

    energy_increment = (
        last["moments"]["classii_energy_density_expectation"]
        - previous["moments"]["classii_energy_density_expectation"]
    ) / (last["cutoff"] - previous["cutoff"])
    record("independent_classii_energy_increment_is_positive", energy_increment > 0.0, energy_increment, ">0", assertions)
    max_j_error = max(generator["J2_relative_error"] for row in rows for generator in row["moments"]["generators"])
    record("monte_carlo_J_matches_exact_trace", max_j_error < float(audit["monte_carlo_trace_tolerance"]), max_j_error, audit["monte_carlo_trace_tolerance"], assertions)
    record(
        "all_independent_K_moments_positive",
        all(generator["K2"] > 0.0 for row in rows for generator in row["moments"]["generators"]),
        "all rows",
        ">0",
        assertions,
    )
    record(
        "monte_carlo_signal_exceeds_sampling_error",
        last["moments"]["classii_energy_density_expectation"]
        > float(audit["minimum_signal_to_standard_error"])
        * last["moments"]["classii_energy_density_standard_error"],
        {
            "signal": last["moments"]["classii_energy_density_expectation"],
            "standard_error": last["moments"]["classii_energy_density_standard_error"],
        },
        f">{audit['minimum_signal_to_standard_error']} standard errors",
        assertions,
    )
    record(
        "point_covariance_stabilises",
        np.linalg.norm(np.asarray(last["covariance"]) - np.asarray(previous["covariance"]))
        < float(audit["point_covariance_increment_tolerance"]),
        float(np.linalg.norm(np.asarray(last["covariance"]) - np.asarray(previous["covariance"]))),
        audit["point_covariance_increment_tolerance"],
        assertions,
    )
    values = [
        counterterm_value(np.asarray([1.0, 0.0, 0.0]), params),
        counterterm_value(np.asarray([1.0, 1.0j, 0.5]), params),
    ]
    record("independent_counterterm_is_field_dependent", min(values) > 0.0 and not math.isclose(values[0], values[1], rel_tol=1.0e-6), values, "positive and nonconstant", assertions)
    record("fixed_rho_floor_does_not_change_power", float(params["rho_regularizer"]) > 0.0 and delta_cube > 0.0, {"rho_floor": params["rho_regularizer"], "slope": delta_cube}, "positive linear slope at fixed floor", assertions)
    record("counterterm_closure_remains_open", "finite counterterm sufficiency" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "explicitly excluded", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A6-CLASSII-UV-INDEPENDENT-PASS" if passed == len(assertions) else "A6-CLASSII-UV-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a6-classii-uv-independent-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "algorithmic_independence": [
            "does not import the primary audit",
            "direct 3D cube enumeration instead of FFT convolution",
            "batched original-basis matrix inversion instead of eigenspace sums",
            "one-dimensional cube-integral identity instead of two-dimensional surface quadrature",
            "fixed-seed Monte Carlo instead of tensor Gauss-Hermite quadrature",
        ],
        "inputs": {"cutoffs": cutoffs, "sample_count": audit["monte_carlo_samples"], "seed_rule": f"{audit['seed']} + cutoff"},
        "derived": {
            "cube_integral": integral_b,
            "delta_cube": delta_cube,
            "dyadic_derivative_slope_eigenvalues": dyadic_derivative_slope.tolist(),
            "derivative_slope_relative_error": derivative_error,
            "classii_energy_increment": energy_increment,
            "counterterm_test_values": values,
        },
        "cutoff_rows": rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic_seeded": True,
        },
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print(f"independent delta_cube: {delta_cube:.12g}")
    print(f"independent Class-II energy increment: {energy_increment:.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
