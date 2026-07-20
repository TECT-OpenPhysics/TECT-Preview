#!/usr/bin/env python3
"""Non-importing audit for A8's decoupled Nelson theorem.

This route reconstructs the coefficient rows directly in complex notation,
uses modewise determinant algebra for a constant spatial background, verifies
the exact finite-dimensional Gaussian-divergence analogue, and includes a
negative control showing that the decoupled and self-coupled weights are not
interchangeable.
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
DEFAULT_OUTPUT = REPO / "claims" / CLAIM_ID / "runs" / "2026-07-20-independent-decoupled-nelson" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def pauli() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    ]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    alpha = float(params["alpha_X"])
    beta = float(params["beta_X"])
    return (
        float(params["cJJ"]) * alpha * alpha / denominator,
        float(params["cJK"]) * alpha * beta / denominator,
        float(params["cKK"]) * beta * beta / denominator,
    )


def coefficient_from_complex_rows(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    a_value, b_value, c_value = coefficients(params)
    rho = float(np.real(np.vdot(field, field)))
    eps = float(params["rho_regularizer"])
    result = np.zeros((6, 6), dtype=np.float64)
    for generator in pauli():
        transformed = generator @ field
        q_value = float(np.real(np.vdot(field, transformed))) / (rho + eps)
        horizontal = transformed - q_value * field
        p_row = 2.0 * np.concatenate((transformed.real, transformed.imag))
        v_row = 2.0 * np.concatenate((horizontal.real, horizontal.imag))
        rows = np.vstack((p_row, v_row))
        q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
        result += rows.T @ q_matrix @ rows
    return result


def mass_matrix(params: dict[str, Any]) -> np.ndarray:
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, z0.conjugate()) / np.real(np.vdot(z0, z0))
    complex_mass = np.diag(np.asarray(params["family_masses"], dtype=np.float64))
    complex_mass = complex_mass + float(params["k_lock"]) * (np.eye(3) - projector)
    return realify(complex_mass)


def root_covariance(k2: float, params: dict[str, Any], mass: np.ndarray) -> np.ndarray:
    scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    eigenvalues, basis = np.linalg.eigh(scalar * np.eye(6) + mass)
    return (basis * (1.0 / np.sqrt(eigenvalues))) @ basis.T


def standard_normal_quadrature(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return math.sqrt(2.0) * nodes, weights / math.sqrt(math.pi)


def toy_weights(p_value: float, coupling: float, gamma: float, order: int) -> dict[str, float]:
    nodes, weights = standard_normal_quadrature(order)
    z = nodes[:, None]
    y = nodes[None, :]
    joint_weights = weights[:, None] * weights[None, :]
    local = gamma * z**6 / 6.0
    decoupled_action = local + 0.5 * coupling * z**2 * (y**2 - 1.0)
    decoupled = float(np.sum(joint_weights * np.exp(-p_value * decoupled_action)))
    self_action = gamma * nodes**6 / 6.0 + 0.5 * coupling * nodes**2 * (nodes**2 - 1.0)
    self_coupled = float(np.sum(weights * np.exp(-p_value * self_action)))
    return {"decoupled": decoupled, "self_coupled": self_coupled, "absolute_difference": abs(decoupled - self_coupled)}


def periodic_derivatives(sites: int) -> tuple[np.ndarray, np.ndarray]:
    """Return an even/central derivative and a parity-breaking control."""
    central = np.zeros((sites, sites), dtype=np.float64)
    one_sided = np.zeros((sites, sites), dtype=np.float64)
    for site in range(sites):
        central[site, (site + 1) % sites] = 0.5
        central[site, (site - 1) % sites] = -0.5
        one_sided[site, site] = -1.0
        one_sided[site, (site + 1) % sites] = 1.0
    return central, one_sided


def block_coefficient(field: np.ndarray, sites: int, params: dict[str, Any]) -> np.ndarray:
    result = np.zeros((6 * sites, 6 * sites), dtype=np.float64)
    for site in range(sites):
        local = field[6 * site : 6 * (site + 1)]
        complex_field = local[:3] + 1j * local[3:]
        result[6 * site : 6 * (site + 1), 6 * site : 6 * (site + 1)] = (
            coefficient_from_complex_rows(complex_field, params)
        )
    return result


def full_divergence_residual(
    xi: np.ndarray,
    covariance_root: np.ndarray,
    derivative: np.ndarray,
    sites: int,
    params: dict[str, Any],
    step: float,
) -> float:
    def vector_field(noise: np.ndarray) -> np.ndarray:
        field = covariance_root @ noise
        gradient = derivative @ field
        coefficient = block_coefficient(field, sites, params)
        return covariance_root.T @ derivative.T @ coefficient @ gradient

    field = covariance_root @ xi
    gradient = derivative @ field
    coefficient = block_coefficient(field, sites, params)
    vector = vector_field(xi)
    divergence = 0.0
    for coordinate in range(xi.size):
        direction = np.zeros_like(xi)
        direction[coordinate] = step
        divergence += (
            vector_field(xi + direction)[coordinate]
            - vector_field(xi - direction)[coordinate]
        ) / (2.0 * step)
    gaussian_divergence = float(xi @ vector - divergence)
    twice_renormalised = float(
        gradient @ coefficient @ gradient
        - np.trace(covariance_root.T @ derivative.T @ coefficient @ derivative @ covariance_root)
    )
    return abs(gaussian_divergence - twice_renormalised)


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
    params = production["parameters"]
    audit = manifest["independent_audit"]
    assertions: list[dict[str, Any]] = []

    add("independent_A1_hash_matches", sha256(a1_path) == authority["production_functional_manifest"]["sha256"], sha256(a1_path), authority["production_functional_manifest"]["sha256"], assertions)
    add("independent_A7_hash_matches", sha256(a7_path) == authority["a7_composite_manifest"]["sha256"], sha256(a7_path), authority["a7_composite_manifest"]["sha256"], assertions)

    a_value, b_value, c_value = coefficients(params)
    q_matrix = np.asarray([[a_value, b_value], [b_value, c_value]], dtype=np.float64)
    q_eigenvalues = np.linalg.eigvalsh(q_matrix)
    add("independent_QII_positive", float(q_eigenvalues[0]) > 0.0, q_eigenvalues.tolist(), ">0", assertions)

    y_value, z_value, r_value = float(params["Y"]), float(params["Z"]), float(params["r"])
    stationary = max(0.0, (2.0 * r_value - z_value) / (2.0 * y_value - z_value))
    analytic_c = (y_value * stationary**2 + z_value * stationary + r_value) / (1.0 + stationary) ** 2
    dense = np.linspace(0.0, float(audit["coercivity_scan_max"]), int(audit["coercivity_scan_points"]))
    dense_values = (y_value * dense**2 + z_value * dense + r_value) / (1.0 + dense) ** 2
    dense_minimum = float(np.min(dense_values))
    add("independent_symbol_coercivity_reconstructs", abs(dense_minimum - analytic_c) < float(audit["coercivity_tolerance"]), {"analytic": analytic_c, "dense": dense_minimum, "stationary": stationary}, audit["coercivity_tolerance"], assertions)

    shell_counts = [((2 * m + 1) ** 3 - (2 * m - 1) ** 3, 24 * m * m + 2) for m in range(1, int(audit["shell_count_limit"]) + 1)]
    add("independent_supnorm_shell_count_is_exact", all(left == right for left, right in shell_counts), shell_counts, "equal", assertions)
    alpha = 2.0 * math.pi / float(params["Lx"])
    lattice_upper = 1.0 + alpha**-4 * (4.0 * math.pi**2 + math.pi**4 / 45.0)
    add("independent_lattice_upper_is_finite", math.isfinite(lattice_upper) and lattice_upper > 1.0, lattice_upper, "finite >1", assertions)

    rng = np.random.default_rng(int(audit["seed"]))
    beta_bound = 12.0 * a_value + 48.0 * abs(b_value) + 48.0 * c_value
    maximum_ratio = 0.0
    minimum_eigenvalue = math.inf
    for _ in range(int(audit["coefficient_samples"])):
        field = rng.normal(size=3) + 1j * rng.normal(size=3)
        rho = float(np.real(np.vdot(field, field)))
        matrix = coefficient_from_complex_rows(field, params)
        maximum_ratio = max(maximum_ratio, float(np.linalg.norm(matrix, ord="fro")) / rho)
        minimum_eigenvalue = min(minimum_eigenvalue, float(np.linalg.eigvalsh(matrix)[0]))
    add("sampled_independent_complex_row_B_is_PSD", minimum_eigenvalue > -float(audit["matrix_tolerance"]), minimum_eigenvalue, ">=-tolerance", assertions)
    add("sampled_independent_beta_rho_bound_holds", maximum_ratio <= beta_bound * (1.0 + float(audit["relative_tolerance"])), {"maximum_ratio": maximum_ratio, "beta": beta_bound}, "ratio<=beta", assertions)

    test_field = np.asarray(audit["test_field_real"], dtype=np.float64) + 1j * np.asarray(audit["test_field_imag"], dtype=np.float64)
    background = coefficient_from_complex_rows(test_field, params)
    mass = mass_matrix(params)
    cutoff = int(audit["determinant_cutoff"])
    p_value = float(audit["determinant_p"])
    trace_value = 0.0
    hs_squared = 0.0
    log_moment_eigen = 0.0
    log_moment_slogdet = 0.0
    for i in range(-cutoff, cutoff + 1):
        for j in range(-cutoff, cutoff + 1):
            for k in range(-cutoff, cutoff + 1):
                k2 = alpha**2 * float(i * i + j * j + k * k)
                if k2 == 0.0:
                    continue
                root = root_covariance(k2, params, mass)
                block = k2 * (root @ background @ root)
                eigenvalues = np.linalg.eigvalsh(block)
                trace_value += float(np.sum(eigenvalues))
                hs_squared += float(np.sum(eigenvalues**2))
                log_moment_eigen += 0.5 * float(np.sum(p_value * eigenvalues - np.log1p(p_value * eigenvalues)))
                sign, logdet = np.linalg.slogdet(np.eye(6) + p_value * block)
                if sign <= 0.0:
                    log_moment_slogdet = math.nan
                else:
                    log_moment_slogdet += 0.5 * (p_value * float(np.trace(block)) - float(logdet))
    determinant = {
        "cutoff": cutoff,
        "trace": trace_value,
        "hs_squared": hs_squared,
        "log_moment_eigen": log_moment_eigen,
        "log_moment_slogdet": log_moment_slogdet,
        "half_hs_bound": 0.25 * p_value**2 * hs_squared,
    }
    add("independent_det2_eigen_and_slogdet_routes_agree", abs(log_moment_eigen - log_moment_slogdet) < float(audit["determinant_tolerance"]), determinant, audit["determinant_tolerance"], assertions)
    add("independent_det2_HS_bound_holds", 0.0 <= log_moment_eigen <= determinant["half_hs_bound"] * (1.0 + float(audit["relative_tolerance"])), determinant, "0<=log<=p^2 HS^2/4", assertions)

    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    regulator_bound = float(manifest["regulator_class"]["multiplier_supremum_bound"])
    trace_constant = regulator_bound**4 * lattice_upper / (volume * analytic_c**2)
    nelson_constant = 0.25 * beta_bound**2 * trace_constant
    lambda_negative = max(-float(params["lambda"]), 0.0)
    gamma = float(params["gamma"])
    p_rows: list[dict[str, float]] = []
    derivative_residuals: list[float] = []
    for raw_p in audit["p_values"]:
        test_p = float(raw_p)
        quartic = test_p**2 * nelson_constant + test_p * lambda_negative / 4.0
        sextic = test_p * gamma / 6.0
        rho_star = 2.0 * quartic / (3.0 * sextic)
        maximum = 4.0 * quartic**3 / (27.0 * sextic**2)
        derivative_residuals.append(abs(2.0 * quartic * rho_star - 3.0 * sextic * rho_star**2))
        p_rows.append({"p": test_p, "quartic": quartic, "sextic": sextic, "rho_star": rho_star, "pointwise_maximum": maximum})
    add("independent_sextic_absorption_stationarity_is_exact", max(derivative_residuals) < float(audit["polynomial_tolerance"]), derivative_residuals, audit["polynomial_tolerance"], assertions)
    add("independent_Nelson_bounds_are_finite", all(math.isfinite(row["pointwise_maximum"]) and row["pointwise_maximum"] > 0.0 for row in p_rows), p_rows, "finite positive", assertions)

    toy_rows = [
        {
            "order": int(order),
            **toy_weights(
                float(audit["toy_p"]),
                float(audit["toy_coupling"]),
                gamma,
                int(order),
            ),
        }
        for order in audit["quadrature_orders"]
    ]
    toy_differences = [row["absolute_difference"] for row in toy_rows]
    toy = {
        "rows": toy_rows,
        "minimum_absolute_difference": min(toy_differences),
        "order_spread": max(toy_differences) - min(toy_differences),
    }
    add(
        "decoupled_and_self_coupled_toy_weights_are_stably_distinct",
        toy["minimum_absolute_difference"] > float(audit["toy_difference_floor"])
        and toy["order_spread"] < float(audit["toy_quadrature_stability_tolerance"]),
        toy,
        f"minimum difference>{audit['toy_difference_floor']} and order spread<{audit['toy_quadrature_stability_tolerance']}",
        assertions,
    )

    sites = int(audit["divergence_sites"])
    central_spatial, one_sided_spatial = periodic_derivatives(sites)
    laplacian = central_spatial.T @ central_spatial
    covariance_spatial = np.linalg.inv(
        float(audit["divergence_mass_oracle"]) * np.eye(sites)
        + laplacian
        + laplacian @ laplacian
    )
    covariance_eigenvalues, covariance_basis = np.linalg.eigh(covariance_spatial)
    covariance_root_spatial = (
        covariance_basis * np.sqrt(covariance_eigenvalues)
    ) @ covariance_basis.T
    covariance_root_full = np.kron(covariance_root_spatial, np.eye(6))
    central_full = np.kron(central_spatial, np.eye(6))
    one_sided_full = np.kron(one_sided_spatial, np.eye(6))
    rng_divergence = np.random.default_rng(int(audit["divergence_seed"]))
    noises = [
        float(audit["divergence_field_scale"])
        * rng_divergence.normal(size=6 * sites)
        for _ in range(int(audit["divergence_trials"]))
    ]
    even_errors = [
        full_divergence_residual(
            noise,
            covariance_root_full,
            central_full,
            sites,
            params,
            float(audit["divergence_fd_step"]),
        )
        for noise in noises
    ]
    asymmetric_gaps = [
        full_divergence_residual(
            noise,
            covariance_root_full,
            one_sided_full,
            sites,
            params,
            float(audit["divergence_fd_step"]),
        )
        for noise in noises
    ]
    even_kernel = float(np.max(np.abs(np.diag(central_spatial @ covariance_spatial))))
    asymmetric_kernel = float(np.max(np.abs(np.diag(one_sided_spatial @ covariance_spatial))))
    divergence = {
        "sites": sites,
        "dimension": 6 * sites,
        "finite_difference_step": audit["divergence_fd_step"],
        "even_errors": even_errors,
        "asymmetric_gaps": asymmetric_gaps,
        "even_same_point_kernel": even_kernel,
        "asymmetric_same_point_kernel": asymmetric_kernel,
    }
    add(
        "full_B_Gaussian_divergence_identity_and_parity_negative_control",
        max(even_errors) < float(audit["divergence_identity_tolerance"])
        and even_kernel < float(audit["even_kernel_tolerance"])
        and min(asymmetric_gaps) > float(audit["asymmetric_gap_floor"])
        and asymmetric_kernel > float(audit["asymmetric_kernel_floor"]),
        divergence,
        "even identity passes and parity-breaking control fires",
        assertions,
    )
    add("self_coupling_interpolation_remains_named", manifest["open_followup"] == "A7-CLASSII-SELF-COUPLING-INTERPOLATION", manifest["open_followup"], "named", assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    verdict = "A8-CLASSII-DECOUPLED-NELSON-INDEPENDENT-PASS" if not failures else "A8-CLASSII-DECOUPLED-NELSON-INDEPENDENT-FAIL"
    config = {
        "seed": audit["seed"],
        "coefficient_samples": audit["coefficient_samples"],
        "determinant_cutoff": audit["determinant_cutoff"],
        "determinant_p": audit["determinant_p"],
        "p_values": audit["p_values"],
        "quadrature_orders": audit["quadrature_orders"],
        "regulator_multiplier_bound": regulator_bound,
    }
    output = {
        "schema": "tect/a8-classii-decoupled-nelson-independent-result/1.0",
        "claim_id": CLAIM_ID,
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "config": config,
        "config_sha256": canonical_digest(config),
        "derived": {
            "coefficients": {"a": a_value, "b": b_value, "c": c_value, "Q_eigenvalues": q_eigenvalues.tolist()},
            "symbol_coercivity": {"stationary_k2": stationary, "c_symbol": analytic_c, "dense_minimum": dense_minimum},
            "beta_B": beta_bound,
            "sample_max_B_over_rho": maximum_ratio,
            "lattice_upper": lattice_upper,
            "trace_ideal_constant": trace_constant,
            "nelson_quartic_constant": nelson_constant,
            "determinant": determinant,
            "p_bounds": p_rows,
            "toy_negative_control": toy,
            "divergence": divergence,
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
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['assertion_summary']['passed']}/{output['assertion_summary']['total']} PASS")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
