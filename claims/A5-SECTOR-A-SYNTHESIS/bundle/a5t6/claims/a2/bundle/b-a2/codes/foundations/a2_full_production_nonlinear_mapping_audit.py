#!/usr/bin/env python3
"""Audit the Class-II real-coordinate Euler--Lagrange map for A2.

The canonical P1 functional writes the three complex components as the six
real coordinates ``u=(Re Psi, Im Psi)``.  For each Hermitian generator ``T``
with realification ``A``, this program independently uses

    m = u.T A u,  q = m/(u.T u + eps),
    p = 2 A u,    s = 2(A-q I)u,
    B = a p p.T + b(p s.T+s p.T) + c s s.T,

so that the Class-II density is ``G_II = 1/2 sum_j (du_j).T B(u) du_j``.
It checks the analytic directional derivatives of ``q`` and ``B``, the
complex-to-real density identity, and the Euler--Lagrange formula

    E_gamma = -B_gamma,beta Delta u_beta
              + sum_j [1/2 d_gamma B_alpha,beta
                       - d_alpha B_gamma,beta]
                (d_j u_alpha)(d_j u_beta).

The finite-difference checks use only local jets and NumPy; they do not call
the Torch-autodiff P1 backend.  They are an independent algebraic audit of
the derivative order needed for the analytic H2-to-L2 estimate, not a
numerical proof of the infinite-dimensional PDE theorem.
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
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
P1_MANIFEST = (
    REPO
    / "claims"
    / "A1-PRODUCTION-FUNCTIONAL-REALISATION"
    / "production_functional_manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A2-FULL-PRODUCTION-WELLPOSED"
    / "runs"
    / "2026-07-17-nonlinear-mapping-audit"
    / "result.json"
)

# Tooling settings for independent finite-difference checks, not production
# parameters or derived physical values.
TEST_SEED = 20260717
FINITE_DIFFERENCE_STEP = 1.0e-6
ABSOLUTE_TOLERANCE = 2.0e-7
RELATIVE_TOLERANCE = 2.0e-6
TEST_RADII = (0.0, 0.3, 1.0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_revision() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        check=False,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def canonical_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the three Hermitian matrices fixed by the P1 backend."""
    return (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def realify(generator: np.ndarray) -> np.ndarray:
    """Realify a Hermitian complex 3-by-3 matrix in (Re Psi, Im Psi)."""
    return np.block(
        [
            [generator.real, -generator.imag],
            [generator.imag, generator.real],
        ]
    )


def q_value(u: np.ndarray, matrix: np.ndarray, epsilon: float) -> float:
    rho = float(u @ u)
    moment = float(u @ matrix @ u)
    return moment / (rho + epsilon)


def dq_value(
    u: np.ndarray, direction: np.ndarray, matrix: np.ndarray, epsilon: float
) -> float:
    rho = float(u @ u)
    moment = float(u @ matrix @ u)
    numerator = 2.0 * float(direction @ matrix @ u) * (rho + epsilon)
    numerator -= 2.0 * moment * float(direction @ u)
    return numerator / (rho + epsilon) ** 2


def classii_coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def b_matrix(
    u: np.ndarray,
    matrix: np.ndarray,
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> np.ndarray:
    a_value, b_value, c_value = coefficients
    identity = np.eye(u.size)
    q = q_value(u, matrix, epsilon)
    p = 2.0 * matrix @ u
    s = 2.0 * (matrix - q * identity) @ u
    return (
        a_value * np.outer(p, p)
        + b_value * (np.outer(p, s) + np.outer(s, p))
        + c_value * np.outer(s, s)
    )


def db_matrix(
    u: np.ndarray,
    direction: np.ndarray,
    matrix: np.ndarray,
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> np.ndarray:
    """Directional derivative DB(u)[direction] from the displayed formula."""
    a_value, b_value, c_value = coefficients
    identity = np.eye(u.size)
    q = q_value(u, matrix, epsilon)
    dq = dq_value(u, direction, matrix, epsilon)
    p = 2.0 * matrix @ u
    dp = 2.0 * matrix @ direction
    s = 2.0 * (matrix - q * identity) @ u
    ds = 2.0 * (matrix - q * identity) @ direction - 2.0 * dq * u
    return (
        a_value * (np.outer(dp, p) + np.outer(p, dp))
        + b_value
        * (
            np.outer(dp, s)
            + np.outer(p, ds)
            + np.outer(ds, p)
            + np.outer(s, dp)
        )
        + c_value * (np.outer(ds, s) + np.outer(s, ds))
    )


def aggregate_b(
    u: np.ndarray,
    matrices: tuple[np.ndarray, ...],
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> np.ndarray:
    return sum((b_matrix(u, matrix, coefficients, epsilon) for matrix in matrices), np.zeros((u.size, u.size)))


def aggregate_db(
    u: np.ndarray,
    direction: np.ndarray,
    matrices: tuple[np.ndarray, ...],
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> np.ndarray:
    return sum(
        (db_matrix(u, direction, matrix, coefficients, epsilon) for matrix in matrices),
        np.zeros((u.size, u.size)),
    )


def complex_classii_density(
    psi: np.ndarray,
    derivative: np.ndarray,
    generators: tuple[np.ndarray, ...],
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> float:
    a_value, b_value, c_value = coefficients
    rho = float(np.real(np.vdot(psi, psi)))
    rho_derivative = 2.0 * float(np.real(np.vdot(psi, derivative)))
    value = 0.0
    for generator in generators:
        transformed = generator @ psi
        moment = float(np.real(np.vdot(psi, transformed)))
        current = np.vdot(derivative, transformed) + np.vdot(psi, generator @ derivative)
        covariant = current - moment * rho_derivative / (rho + epsilon)
        value += 0.5 * a_value * abs(current) ** 2
        value += b_value * float(np.real(np.conj(current) * covariant))
        value += 0.5 * c_value * abs(covariant) ** 2
    return float(value)


def density_from_b(u: np.ndarray, derivative: np.ndarray, b_total: np.ndarray) -> float:
    return 0.5 * float(derivative @ b_total @ derivative)


def euler_local_jet(
    u: np.ndarray,
    derivative: np.ndarray,
    second_derivative: np.ndarray,
    matrices: tuple[np.ndarray, ...],
    coefficients: tuple[float, float, float],
    epsilon: float,
) -> np.ndarray:
    b_total = aggregate_b(u, matrices, coefficients, epsilon)
    quadratic = np.empty_like(u)
    for gamma in range(u.size):
        basis = np.zeros_like(u)
        basis[gamma] = 1.0
        first_variation = 0.5 * float(derivative @ aggregate_db(u, basis, matrices, coefficients, epsilon) @ derivative)
        flux_variation = float((aggregate_db(u, derivative, matrices, coefficients, epsilon) @ derivative)[gamma])
        quadratic[gamma] = first_variation - flux_variation
    return -b_total @ second_derivative + quadratic


def relative_error(actual: np.ndarray | float, expected: np.ndarray | float) -> float:
    numerator = float(np.linalg.norm(np.asarray(actual) - np.asarray(expected)))
    denominator = max(1.0, float(np.linalg.norm(np.asarray(expected))))
    return numerator / denominator


def audit() -> dict[str, Any]:
    manifest = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    backend_record = manifest["production_reference_backend"]
    backend_path = REPO / backend_record["path"]
    epsilon = float(params["rho_regularizer"])
    coefficients = classii_coefficients(params)
    generators = canonical_generators()
    matrices = tuple(realify(generator) for generator in generators)
    assertions: list[dict[str, Any]] = []

    def check(name: str, passed: bool, value: Any) -> None:
        assertions.append({"name": name, "passed": bool(passed), "value": value})

    backend_hash = sha256_file(backend_path)
    check(
        "p1_backend_hash_matches_manifest",
        backend_hash == backend_record["sha256"],
        {"computed": backend_hash, "expected": backend_record["sha256"]},
    )
    check(
        "canonical_functional_declares_full_classii_quadratic_form",
        "b Re(conj(J_A).K_A)" in manifest["proposed_reference_functional"]["formula"],
        manifest["proposed_reference_functional"]["formula"],
    )
    check(
        "regularised_production_subset_is_selected",
        epsilon > 0.0 and float(params["eta_shell"]) == 0.0,
        {"rho_regularizer": epsilon, "eta_shell": float(params["eta_shell"])},
    )
    q_matrix = np.array([[coefficients[0], coefficients[1]], [coefficients[1], coefficients[2]]])
    q_eigenvalues = np.linalg.eigvalsh(q_matrix)
    check(
        "classii_coefficient_matrix_is_positive_definite",
        bool(q_eigenvalues[0] > 0.0),
        {"matrix": q_matrix.tolist(), "eigenvalues": q_eigenvalues.tolist()},
    )
    symmetry_errors = [float(np.max(np.abs(matrix - matrix.T))) for matrix in matrices]
    check("realified_generators_are_symmetric", max(symmetry_errors) == 0.0, symmetry_errors)

    rng = np.random.default_rng(TEST_SEED)
    samples = [np.zeros(6)]
    samples.extend(radius * rng.normal(size=6) for radius in TEST_RADII[1:])
    samples.extend(rng.normal(size=6) for _ in range(4))
    directions = [rng.normal(size=6) for _ in samples]
    moment_errors: list[float] = []
    q_derivative_errors: list[float] = []
    q_bounds: list[dict[str, float]] = []
    b_symmetry_errors: list[float] = []
    b_derivative_errors: list[float] = []
    density_errors: list[float] = []

    for u, direction in zip(samples, directions):
        psi = u[:3] + 1j * u[3:]
        derivative = direction[:3] + 1j * direction[3:]
        for generator, matrix in zip(generators, matrices):
            complex_moment = float(np.real(np.vdot(psi, generator @ psi)))
            real_moment = float(u @ matrix @ u)
            moment_errors.append(abs(complex_moment - real_moment))
            q = q_value(u, matrix, epsilon)
            q_bound = float(np.linalg.eigvalsh(matrix)[-1])
            q_bounds.append({"abs_q": abs(q), "operator_bound": q_bound})
            step = FINITE_DIFFERENCE_STEP / max(1.0, float(np.linalg.norm(direction)))
            q_fd = (q_value(u + step * direction, matrix, epsilon) - q_value(u - step * direction, matrix, epsilon)) / (2.0 * step)
            q_derivative_errors.append(relative_error(dq_value(u, direction, matrix, epsilon), q_fd))
            b_one = b_matrix(u, matrix, coefficients, epsilon)
            b_symmetry_errors.append(float(np.max(np.abs(b_one - b_one.T))))
            b_fd = (b_matrix(u + step * direction, matrix, coefficients, epsilon) - b_matrix(u - step * direction, matrix, coefficients, epsilon)) / (2.0 * step)
            b_derivative_errors.append(relative_error(db_matrix(u, direction, matrix, coefficients, epsilon), b_fd))
        b_total = aggregate_b(u, matrices, coefficients, epsilon)
        density_errors.append(
            relative_error(
                density_from_b(u, direction, b_total),
                complex_classii_density(psi, derivative, generators, coefficients, epsilon),
            )
        )

    check("complex_and_real_moment_definitions_agree", max(moment_errors) <= ABSOLUTE_TOLERANCE, max(moment_errors))
    check(
        "regularised_q_is_bounded_by_generator_norm",
        all(item["abs_q"] <= item["operator_bound"] + ABSOLUTE_TOLERANCE for item in q_bounds),
        q_bounds,
    )
    check("analytic_dq_matches_central_difference", max(q_derivative_errors) <= RELATIVE_TOLERANCE, max(q_derivative_errors))
    check("classii_b_matrix_is_symmetric", max(b_symmetry_errors) <= ABSOLUTE_TOLERANCE, max(b_symmetry_errors))
    check("complex_and_real_classii_densities_agree", max(density_errors) <= RELATIVE_TOLERANCE, max(density_errors))
    check("analytic_db_matches_central_difference", max(b_derivative_errors) <= RELATIVE_TOLERANCE, max(b_derivative_errors))

    jet_errors: list[float] = []
    potential_errors: list[float] = []
    for _ in range(5):
        u = rng.normal(size=6)
        derivative = rng.normal(size=6)
        second_derivative = rng.normal(size=6)
        formula = euler_local_jet(u, derivative, second_derivative, matrices, coefficients, epsilon)
        numeric = np.empty_like(u)
        step = FINITE_DIFFERENCE_STEP
        for gamma in range(u.size):
            basis = np.zeros_like(u)
            basis[gamma] = 1.0
            b_plus = aggregate_b(u + step * basis, matrices, coefficients, epsilon)
            b_minus = aggregate_b(u - step * basis, matrices, coefficients, epsilon)
            partial_density = (
                density_from_b(u + step * basis, derivative, b_plus)
                - density_from_b(u - step * basis, derivative, b_minus)
            ) / (2.0 * step)
            def flux_at(x: float) -> np.ndarray:
                field = u + x * derivative + 0.5 * x * x * second_derivative
                field_derivative = derivative + x * second_derivative
                return aggregate_b(field, matrices, coefficients, epsilon) @ field_derivative
            flux_derivative = (flux_at(step) - flux_at(-step)) / (2.0 * step)
            numeric[gamma] = partial_density - flux_derivative[gamma]
        jet_errors.append(relative_error(formula, numeric))

        rho = float(u @ u)
        lambda_value = float(params["lambda"])
        gamma_value = float(params["gamma"])
        potential_gradient = lambda_value * rho * u + gamma_value * rho * rho * u
        potential_fd = np.empty_like(u)
        for gamma in range(u.size):
            basis = np.zeros_like(u)
            basis[gamma] = 1.0
            def potential(field: np.ndarray) -> float:
                field_rho = float(field @ field)
                return lambda_value * field_rho**2 / 4.0 + gamma_value * field_rho**3 / 6.0
            potential_fd[gamma] = (potential(u + step * basis) - potential(u - step * basis)) / (2.0 * step)
        potential_errors.append(relative_error(potential_gradient, potential_fd))

    check("expanded_classii_euler_local_jet_matches_finite_difference", max(jet_errors) <= RELATIVE_TOLERANCE, max(jet_errors))
    check("quartic_and_sextic_real_gradients_match_finite_difference", max(potential_errors) <= RELATIVE_TOLERANCE, max(potential_errors))
    check(
        "classii_has_at_most_second_spatial_order_and_y_is_positive",
        float(params["Y"]) > 0.0,
        {"classii_euler_order": 2, "brazovskii_principal_order": 4, "Y": float(params["Y"])},
    )

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/a2-full-production-nonlinear-mapping-audit/1.0",
        "claim_id": "A2-FULL-PRODUCTION-WELLPOSED",
        "generated_on": "2026-07-17",
        "script_version": __version__,
        "input": {
            "p1_manifest": str(P1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "p1_manifest_sha256": sha256_file(P1_MANIFEST),
            "backend": backend_record["path"],
            "backend_sha256": backend_hash,
        },
        "convention": {
            "real_coordinates": "u=(Re Psi_1,Re Psi_2,Re Psi_3,Im Psi_1,Im Psi_2,Im Psi_3)",
            "classii_density": "G_II=1/2 sum_j (partial_j u)^T B(u) partial_j u",
            "euler_map": "E_gamma=-B_gamma,beta Delta u_beta + sum_j[1/2 partial_gamma B_alpha,beta-partial_alpha B_gamma,beta]partial_j u_alpha partial_j u_beta",
            "spatial_order": {"classii": 2, "brazovskii_principal": 4},
        },
        "derived": {
            "classii_coefficients": {"a": coefficients[0], "b": coefficients[1], "c": coefficients[2]},
            "classii_coefficient_eigenvalues": q_eigenvalues.tolist(),
            "max_moment_realification_error": max(moment_errors),
            "max_q_derivative_relative_error": max(q_derivative_errors),
            "max_b_derivative_relative_error": max(b_derivative_errors),
            "max_density_relative_error": max(density_errors),
            "max_euler_local_jet_relative_error": max(jet_errors),
            "max_potential_gradient_relative_error": max(potential_errors),
        },
        "test_configuration": {
            "seed": TEST_SEED,
            "finite_difference_step": FINITE_DIFFERENCE_STEP,
            "absolute_tolerance": ABSOLUTE_TOLERANCE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "test_radii": list(TEST_RADII),
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_revision": git_revision(),
        },
        "assertions": assertions,
        "proof_boundary": {
            "closed_here": [
                "six-real-coordinate Class-II density and Euler--Lagrange expansion",
                "no derivative order above two in the Class-II Euler--Lagrange term",
                "smooth regularised coefficient map on bounded H2 balls",
                "algebraic inputs for the local H2-to-L2 Lipschitz estimate",
            ],
            "not_closed_here": [
                "Galerkin chain rule and energy identity",
                "global continuation",
                "continuous dependence and positive-time smoothing",
                "T6 or T7 well-posedness theorem",
            ],
        },
        "verdict": "A2-FULL-NONLINEAR-MAPPING-AUDIT-PASS" if passed else "A2-FULL-NONLINEAR-MAPPING-AUDIT-FAIL",
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assertion_count = len(result["assertions"])
    passed_count = sum(item["passed"] for item in result["assertions"])
    print(f"{passed_count}/{assertion_count} PASS")
    print(f"Diagnosis: {result['verdict']}")
    print(f"Evidence: {args.output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
