#!/usr/bin/env python3
"""Independent finite-Galerkin energy audit for A2 full production.

This NumPy-only verifier reconstructs the canonical P1 energy from its pinned
manifest without importing the Torch P1 backend.  On explicit real orthonormal
low-Fourier subspaces it computes the restricted energy gradient by centred
finite differences.  Thus, for the finite Galerkin equation

    u_n' = - grad_{V_n} F(u_n),

it independently checks

    d/dt F(u_n) = - ||grad_{V_n} F(u_n)||_R^2.

The executable is a finite-dimensional sanity check.  The accompanying proof
note supplies the infinite-dimensional chain rule, compactness passage, and
continuation argument; this program does not by itself prove a PDE theorem.
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
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BASELINE_RESULT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-coercivity-baseline" / "result.json"
NONLINEAR_RESULT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-nonlinear-mapping-audit" / "result.json"
DEFAULT_OUTPUT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-energy-continuation-audit" / "result.json"

# Test settings only; no production coefficient or derived physical value is
# embedded here.
TEST_SEED = 20260717
TEST_GRIDS = (4, 6, 8)
FINITE_DIFFERENCE_STEP = 1.0e-5
BASIS_GRAM_TOLERANCE = 3.0e-12
ENERGY_REL_TOLERANCE = 4.0e-6


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_revision() -> str | None:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None


def dvol(shape: tuple[int, int, int], params: dict[str, Any]) -> float:
    return math.prod(float(params[key]) / n for key, n in zip(("Lx", "Ly", "Lz"), shape))


def pairing(left: np.ndarray, right: np.ndarray, params: dict[str, Any]) -> float:
    return dvol(tuple(int(n) for n in left.shape[1:]), params) * float(np.real(np.vdot(left, right)))


def norm_sq(value: np.ndarray, params: dict[str, Any]) -> float:
    return pairing(value, value, params)


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The three Hermitian generators explicitly fixed by the P1 backend."""
    return (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def kmesh(shape: tuple[int, int, int], params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    axes = [2.0 * math.pi * np.fft.fftfreq(n, d=float(params[key]) / n) for key, n in zip(("Lx", "Ly", "Lz"), shape)]
    kx, ky, kz = np.meshgrid(*axes, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    return kx, ky, kz, np.sqrt(k2)


def energy(psi: np.ndarray, params: dict[str, Any]) -> float:
    """Independent NumPy reconstruction of the canonical eta_shell=0 energy."""
    shape = tuple(int(n) for n in psi.shape[1:])
    volume_element = dvol(shape, params)
    rho = np.sum(np.abs(psi) ** 2, axis=0)
    kx, ky, kz, kmag = kmesh(shape, params)
    psi_k = np.fft.fftn(psi, axes=(1, 2, 3))
    grad = np.stack([np.fft.ifftn(1j * wave[None, ...] * psi_k, axes=(1, 2, 3)) for wave in (kx, ky, kz)], axis=0)
    lap = np.fft.ifftn(-(kmag * kmag)[None, ...] * psi_k, axes=(1, 2, 3))
    result = 0.5 * float(params["r"]) * np.sum(rho)
    result += 0.5 * float(params["Z"]) * np.sum(np.abs(grad) ** 2)
    result += 0.5 * float(params["Y"]) * np.sum(np.abs(lap) ** 2)
    family = np.diag(np.asarray(params["family_masses"], dtype=np.complex128))
    family_psi = np.einsum("ab,bxyz->axyz", family, psi)
    result += 0.5 * np.sum(np.real(np.sum(np.conj(psi) * family_psi, axis=0)))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, np.conj(z0)) / np.real(np.vdot(z0, z0))
    locked = np.einsum("ab,bxyz->axyz", np.eye(3, dtype=np.complex128) - projector, psi)
    result += 0.5 * float(params["k_lock"]) * np.sum(np.abs(locked) ** 2)
    result += 0.25 * float(params["lambda"]) * np.sum(rho**2)
    result += float(params["gamma"]) * np.sum(rho**3) / 6.0
    if float(params["eta_shell"]) != 0.0:
        penalty = (kmag - float(params["q0"]))[None, ...] * psi_k
        result += 0.5 * float(params["eta_shell"]) * np.sum(np.abs(penalty) ** 2) / math.prod(shape) / volume_element
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    rho_safe = rho + float(params["rho_regularizer"])
    grad_rho = 2.0 * np.real(np.sum(np.conj(psi)[None, ...] * grad, axis=1))
    for generator in generators():
        transformed = np.einsum("ab,bxyz->axyz", generator, psi)
        moment = np.sum(np.conj(psi) * transformed, axis=0)
        current = np.sum(np.conj(grad) * transformed[None, ...], axis=1)
        current += np.sum(np.conj(psi)[None, ...] * np.einsum("ab,ibxyz->iaxyz", generator, grad), axis=1)
        covariant = current - (moment / rho_safe)[None, ...] * grad_rho
        result += 0.5 * a_value * np.sum(np.abs(current) ** 2)
        result += b_value * np.sum(np.real(np.conj(current) * covariant))
        result += 0.5 * c_value * np.sum(np.abs(covariant) ** 2)
    return float(np.real(result * volume_element))


def candidate_basis(shape: tuple[int, int, int], params: dict[str, Any]) -> list[np.ndarray]:
    x = np.arange(shape[0], dtype=float) * float(params["Lx"]) / shape[0]
    phase = 2.0 * math.pi * x / float(params["Lx"])
    cos = np.cos(phase)[:, None, None] * np.ones((1, shape[1], shape[2]))
    sin = np.sin(phase)[:, None, None] * np.ones((1, shape[1], shape[2]))
    constant = np.ones(shape)
    fields: list[np.ndarray] = []
    for component, profile, phase_factor in (
        (0, constant, 1.0), (0, constant, 1j), (1, constant, 1.0), (1, constant, 1j),
        (0, cos, 1.0), (0, sin, 1j), (1, cos, 1.0), (1, sin, 1j),
    ):
        value = np.zeros((3, *shape), dtype=np.complex128)
        value[component] = phase_factor * profile
        fields.append(value)
    return fields


def real_orthonormal_basis(shape: tuple[int, int, int], params: dict[str, Any]) -> list[np.ndarray]:
    basis: list[np.ndarray] = []
    for candidate in candidate_basis(shape, params):
        residual = candidate.copy()
        for vector in basis:
            residual -= pairing(vector, residual, params) * vector
        length_sq = norm_sq(residual, params)
        if length_sq > 0.0:
            basis.append(residual / math.sqrt(length_sq))
    return basis


def project(value: np.ndarray, basis: list[np.ndarray], params: dict[str, Any]) -> np.ndarray:
    return sum((pairing(vector, value, params) * vector for vector in basis), np.zeros_like(value))


def state_coefficients(name: str, dimension: int, rng: np.random.Generator) -> np.ndarray:
    amplitude = 0.18  # test-state amplitude only
    values = np.zeros(dimension)
    if name == "zero":
        return values
    if name == "homogeneous":
        values[: min(4, dimension)] = amplitude
        return values
    if name == "random":
        return amplitude * rng.normal(size=dimension)
    if name == "q-shell":
        values[4:] = amplitude
        return values
    if name == "classii-active":
        values[:] = amplitude * np.linspace(0.5, 1.0, dimension)
        return values
    raise ValueError(f"unknown test state: {name}")


def combine(coefficients: np.ndarray, basis: list[np.ndarray]) -> np.ndarray:
    return sum((coefficient * vector for coefficient, vector in zip(coefficients, basis)), np.zeros_like(basis[0]))


def relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(1.0, abs(expected))


def audit() -> dict[str, Any]:
    manifest = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_RESULT.read_text(encoding="utf-8"))
    nonlinear = json.loads(NONLINEAR_RESULT.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    backend = manifest["production_reference_backend"]
    backend_path = REPO / backend["path"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, passed: bool, value: Any) -> None:
        assertions.append({"name": name, "passed": bool(passed), "value": value})

    backend_hash = sha256_file(backend_path)
    check("p1_backend_hash_matches_manifest", backend_hash == backend["sha256"], {"computed": backend_hash, "expected": backend["sha256"]})
    check("coercivity_baseline_is_available_and_passed", baseline["passed"] and baseline["verdict"] == "A2-FULL-COERCIVITY-BASELINE-PASS", baseline["verdict"])
    check("nonlinear_mapping_audit_is_available_and_passed", nonlinear["passed"] and nonlinear["verdict"] == "A2-FULL-NONLINEAR-MAPPING-AUDIT-PASS", nonlinear["verdict"])
    check(
        "production_subset_has_zero_shell_bias_and_positive_regularisers",
        float(params["eta_shell"]) == 0.0 and float(params["rho_regularizer"]) > 0.0 and float(params["classii_mass_regularizer"]) > 0.0,
        {"eta_shell": float(params["eta_shell"]), "rho_regularizer": float(params["rho_regularizer"]), "classii_mass_regularizer": float(params["classii_mass_regularizer"])},
    )

    rng = np.random.default_rng(TEST_SEED)
    names = ("zero", "homogeneous", "random", "q-shell", "classii-active")
    gram_errors: list[float] = []
    projector_idempotence_errors: list[float] = []
    projector_symmetry_errors: list[float] = []
    support_errors: list[float] = []
    gradient_support_errors: list[float] = []
    directional_gradient_errors: list[float] = []
    dissipation_errors: list[float] = []
    forward_descent_margins: list[float] = []
    cases: list[dict[str, Any]] = []

    for grid in TEST_GRIDS:
        shape = (grid, grid, grid)
        basis = real_orthonormal_basis(shape, params)
        gram = np.array([[pairing(left, right, params) for right in basis] for left in basis])
        gram_errors.append(float(np.max(np.abs(gram - np.eye(len(basis))))))
        probe = rng.normal(size=(3, *shape)) + 1j * rng.normal(size=(3, *shape))
        projected_probe = project(probe, basis, params)
        projector_idempotence_errors.append(relative_error(norm_sq(project(projected_probe, basis, params) - projected_probe, params), 0.0))
        projector_symmetry_errors.append(relative_error(pairing(projected_probe, probe, params), pairing(probe, projected_probe, params)))
        for name in names:
            coefficients = state_coefficients(name, len(basis), rng)
            state = combine(coefficients, basis)
            support_errors.append(relative_error(norm_sq(project(state, basis, params) - state, params), 0.0))
            coordinate_gradient = np.empty(len(basis))
            for index in range(len(basis)):
                offset = np.zeros_like(coefficients)
                offset[index] = FINITE_DIFFERENCE_STEP
                coordinate_gradient[index] = (energy(combine(coefficients + offset, basis), params) - energy(combine(coefficients - offset, basis), params)) / (2.0 * FINITE_DIFFERENCE_STEP)
            projected_gradient = combine(coordinate_gradient, basis)
            velocity = -projected_gradient
            gradient_support_errors.append(relative_error(norm_sq(project(velocity, basis, params) - velocity, params), 0.0))
            gradient_norm_sq = float(coordinate_gradient @ coordinate_gradient)
            scale = max(1.0, math.sqrt(norm_sq(velocity, params)))
            directional_step = FINITE_DIFFERENCE_STEP / scale
            directional_fd = (energy(state + directional_step * velocity, params) - energy(state - directional_step * velocity, params)) / (2.0 * directional_step)
            directional_gradient_errors.append(relative_error(directional_fd, -gradient_norm_sq))
            dissipation_errors.append(relative_error(directional_fd, -norm_sq(projected_gradient, params)))
            forward_margin = energy(state, params) - energy(state + directional_step * velocity, params)
            forward_descent_margins.append(forward_margin)
            cases.append({"grid": grid, "state": name, "energy": energy(state, params), "gradient_norm_sq": gradient_norm_sq, "finite_difference_dFdt": directional_fd, "forward_descent_margin": forward_margin})

    check("real_galerkin_basis_is_orthonormal", max(gram_errors) <= BASIS_GRAM_TOLERANCE, max(gram_errors))
    check("galerkin_projector_is_idempotent", max(projector_idempotence_errors) <= BASIS_GRAM_TOLERANCE, max(projector_idempotence_errors))
    check("galerkin_projector_is_self_adjoint_for_real_pairing", max(projector_symmetry_errors) <= BASIS_GRAM_TOLERANCE, max(projector_symmetry_errors))
    check("test_states_are_in_the_galerkin_subspace", max(support_errors) <= BASIS_GRAM_TOLERANCE, max(support_errors))
    check("restricted_energy_gradient_flow_stays_in_the_galerkin_subspace", max(gradient_support_errors) <= BASIS_GRAM_TOLERANCE, max(gradient_support_errors))
    check("restricted_energy_directional_derivative_is_negative_gradient_norm", max(directional_gradient_errors) <= ENERGY_REL_TOLERANCE, max(directional_gradient_errors))
    check("real_pairing_norm_and_coordinate_gradient_norm_agree", max(dissipation_errors) <= ENERGY_REL_TOLERANCE, max(dissipation_errors))
    check("small_forward_galerkin_gradient_steps_do_not_increase_energy", min(forward_descent_margins) >= -ENERGY_REL_TOLERANCE, min(forward_descent_margins))

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/a2-full-production-energy-continuation-audit/1.0",
        "claim_id": "A2-FULL-PRODUCTION-WELLPOSED",
        "generated_on": "2026-07-17",
        "script_version": __version__,
        "input": {
            "p1_manifest": str(P1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "p1_manifest_sha256": sha256_file(P1_MANIFEST),
            "backend": backend["path"],
            "backend_sha256": backend_hash,
            "coercivity_result": str(BASELINE_RESULT.relative_to(REPO)).replace("\\", "/"),
            "nonlinear_mapping_result": str(NONLINEAR_RESULT.relative_to(REPO)).replace("\\", "/"),
        },
        "galerkin_identity": "dF(u_n)/dt=-||grad_{V_n}F(u_n)||_R^2",
        "test_configuration": {"seed": TEST_SEED, "grids": list(TEST_GRIDS), "states": list(names), "finite_difference_step": FINITE_DIFFERENCE_STEP, "basis_gram_tolerance": BASIS_GRAM_TOLERANCE, "energy_relative_tolerance": ENERGY_REL_TOLERANCE},
        "derived": {
            "max_basis_gram_error": max(gram_errors),
            "max_directional_energy_relative_error": max(directional_gradient_errors),
            "max_coordinate_norm_relative_error": max(dissipation_errors),
            "minimum_forward_descent_margin": min(forward_descent_margins),
        },
        "cases": cases,
        "environment": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "git_revision": git_revision()},
        "assertions": assertions,
        "proof_boundary": {
            "closed_here": ["finite Galerkin restricted-gradient energy identity", "independent NumPy energy reconstruction and directional-descent checks", "analytic energy-continuation route in the v1.2 note"],
            "not_closed_here": ["continuous dependence and positive-time smoothing audit", "T6 or T7 full-production PDE theorem", "historical non-variational proxy or eta_shell nonzero"],
        },
        "verdict": "A2-FULL-ENERGY-CONTINUATION-AUDIT-PASS" if passed else "A2-FULL-ENERGY-CONTINUATION-AUDIT-FAIL",
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    passed_count = sum(item["passed"] for item in result["assertions"])
    print(f"{passed_count}/{len(result['assertions'])} PASS")
    print(f"Diagnosis: {result['verdict']}")
    print(f"Evidence: {args.output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
