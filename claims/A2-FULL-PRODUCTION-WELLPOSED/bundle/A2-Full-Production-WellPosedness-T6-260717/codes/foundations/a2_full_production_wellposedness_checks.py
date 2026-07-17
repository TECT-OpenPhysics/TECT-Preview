#!/usr/bin/env python3
"""Audit the coercivity baseline for A2-FULL-PRODUCTION-WELLPOSED.

This program reads every production coefficient from the P1 functional
manifest.  It checks the source pin, the self-adjoint/coercive linear-symbol
conditions, the Class-II coefficient matrix, the regularisers, and the
sextic Young bound used by the global-continuation route.  It deliberately
does not report local or global PDE well-posedness: those are analytic gates,
not numerical assertions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

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
    / "2026-07-17-coercivity-baseline"
    / "result.json"
)

# Tooling tolerances, not physical or derived parameters.
ANCHOR_ABS_TOL = 1.0e-9
ALGEBRA_ABS_TOL = 1.0e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _minimum_symbol_ratio(r_value: float, z_value: float, y_value: float) -> float:
    """Return min_{x>=0} (r+Z x+Y x^2)/(1+x^2)."""
    candidates = [0.0]
    # Stationary equation: -Z*x^2 + 2*(Y-r)*x + Z = 0.
    a_value = -z_value
    b_value = 2.0 * (y_value - r_value)
    c_value = z_value
    if abs(a_value) <= ALGEBRA_ABS_TOL:
        if abs(b_value) > ALGEBRA_ABS_TOL:
            root = -c_value / b_value
            if root >= 0.0:
                candidates.append(root)
    else:
        discriminant = b_value * b_value - 4.0 * a_value * c_value
        if discriminant >= 0.0:
            root_disc = math.sqrt(discriminant)
            for root in (
                (-b_value - root_disc) / (2.0 * a_value),
                (-b_value + root_disc) / (2.0 * a_value),
            ):
                if root >= 0.0:
                    candidates.append(root)
    values = [
        (r_value + z_value * x_value + y_value * x_value * x_value)
        / (1.0 + x_value * x_value)
        for x_value in candidates
    ]
    values.append(y_value)  # x -> infinity
    return min(values)


def _projector_diagnostics(z0_raw: list[float]) -> dict[str, float]:
    z0 = [complex(value) for value in z0_raw]
    norm_sq = sum(abs(value) ** 2 for value in z0)
    if norm_sq <= 0.0:
        return {
            "norm_sq": norm_sq,
            "hermitian_error": math.inf,
            "idempotence_error": math.inf,
        }
    projector = [
        [z0[i] * z0[j].conjugate() / norm_sq for j in range(len(z0))]
        for i in range(len(z0))
    ]
    square = [
        [
            sum(projector[i][k] * projector[k][j] for k in range(len(z0)))
            for j in range(len(z0))
        ]
        for i in range(len(z0))
    ]
    hermitian_error = max(
        abs(projector[i][j] - projector[j][i].conjugate())
        for i in range(len(z0))
        for j in range(len(z0))
    )
    idempotence_error = max(
        abs(square[i][j] - projector[i][j])
        for i in range(len(z0))
        for j in range(len(z0))
    )
    return {
        "norm_sq": norm_sq,
        "hermitian_error": hermitian_error,
        "idempotence_error": idempotence_error,
    }


def audit() -> dict[str, Any]:
    manifest = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    params = manifest["parameters"]
    backend_record = manifest["production_reference_backend"]
    backend_path = REPO / backend_record["path"]
    proposed = manifest["proposed_reference_functional"]

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
        "canonical_reference_functional_is_implemented",
        "implemented" in proposed["status"].lower(),
        proposed["status"],
    )
    check(
        "historical_backend_remains_separate_proxy",
        manifest["known_obstruction"]["id"] == "A1-PFR-VARIATIONAL-MISMATCH",
        manifest["known_obstruction"]["id"],
    )

    r_value = float(params["r"])
    z_value = float(params["Z"])
    y_value = float(params["Y"])
    q0_value = float(params["q0"])
    mu2_value = float(params["mu2"])
    check("fourth_order_principal_coefficient_positive", y_value > 0.0, y_value)

    if y_value > 0.0 and z_value < 0.0:
        q_shell = math.sqrt(-z_value / (2.0 * y_value))
        shell_mass = r_value - z_value * z_value / (4.0 * y_value)
    else:
        q_shell = 0.0
        shell_mass = r_value
    check(
        "q0_matches_linear_symbol_shell",
        abs(q_shell - q0_value) <= ANCHOR_ABS_TOL,
        {"from_symbol": q_shell, "manifest": q0_value, "abs_error": abs(q_shell - q0_value)},
    )
    check(
        "mu2_matches_linear_symbol_minimum",
        abs(shell_mass - mu2_value) <= ANCHOR_ABS_TOL,
        {"from_symbol": shell_mass, "manifest": mu2_value, "abs_error": abs(shell_mass - mu2_value)},
    )
    check("linear_symbol_has_positive_lower_bound", shell_mass > 0.0, shell_mass)

    h2_coercivity = _minimum_symbol_ratio(r_value, z_value, y_value)
    check("linear_symbol_controls_h2_norm", h2_coercivity > 0.0, h2_coercivity)

    family_masses = [float(value) for value in params["family_masses"]]
    check(
        "family_mass_matrix_is_positive_semidefinite",
        min(family_masses) >= 0.0,
        {"eigenvalues": family_masses, "minimum": min(family_masses)},
    )
    k_lock = float(params["k_lock"])
    projector = _projector_diagnostics(params["z0"])
    check("lock_coefficient_is_nonnegative", k_lock >= 0.0, k_lock)
    check(
        "lock_projector_is_hermitian",
        projector["hermitian_error"] <= ALGEBRA_ABS_TOL,
        projector["hermitian_error"],
    )
    check(
        "lock_projector_is_idempotent",
        projector["idempotence_error"] <= ALGEBRA_ABS_TOL,
        projector["idempotence_error"],
    )
    check(
        "production_shell_bias_is_zero_for_continuum_pde",
        float(params["eta_shell"]) == 0.0,
        float(params["eta_shell"]),
    )

    rho_regularizer = float(params["rho_regularizer"])
    mass_regularizer = float(params["classii_mass_regularizer"])
    check("rho_regularizer_is_positive", rho_regularizer > 0.0, rho_regularizer)
    check("classii_mass_regularizer_is_positive", mass_regularizer > 0.0, mass_regularizer)

    alpha = float(params["alpha_X"])
    beta = float(params["beta_X"])
    denominator = float(params["M_X"]) ** 2 + mass_regularizer
    a_jj = float(params["cJJ"]) * alpha * alpha / denominator
    b_jk = float(params["cJK"]) * alpha * beta / denominator
    c_kk = float(params["cKK"]) * beta * beta / denominator
    determinant = a_jj * c_kk - b_jk * b_jk
    trace = a_jj + c_kk
    discriminant = math.sqrt((a_jj - c_kk) ** 2 + 4.0 * b_jk * b_jk)
    eigenvalues = [(trace - discriminant) / 2.0, (trace + discriminant) / 2.0]
    classii = {
        "a": a_jj,
        "b": b_jk,
        "c": c_kk,
        "determinant": determinant,
        "eigenvalues": eigenvalues,
    }
    check("classii_diagonal_coefficients_positive", a_jj > 0.0 and c_kk > 0.0, classii)
    check("classii_coefficient_matrix_positive_definite", determinant > 0.0, classii)
    check("classii_coercivity_constant_positive", eigenvalues[0] > 0.0, eigenvalues[0])

    lambda_value = float(params["lambda"])
    gamma_value = float(params["gamma"])
    check("sextic_coefficient_positive", gamma_value > 0.0, gamma_value)
    if gamma_value > 0.0 and lambda_value < 0.0:
        young_constant = abs(lambda_value) ** 3 / (3.0 * gamma_value**2)
        potential_floor = -(abs(lambda_value) ** 3) / (12.0 * gamma_value**2)
        split_sextic_coefficient = gamma_value / 12.0
    else:
        young_constant = 0.0
        potential_floor = 0.0
        split_sextic_coefficient = gamma_value / 6.0
    check(
        "quartic_is_absorbed_by_half_of_sextic",
        young_constant >= 0.0 and split_sextic_coefficient > 0.0,
        {
            "young_constant_per_unit_volume": young_constant,
            "remaining_rho_cubed_coefficient": split_sextic_coefficient,
            "exact_local_potential_floor": potential_floor,
        },
    )

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/a2-full-production-wellposedness-check/1.0",
        "claim_id": "A2-FULL-PRODUCTION-WELLPOSED",
        "generated_on": "2026-07-17",
        "script_version": __version__,
        "input": {
            "p1_manifest": str(P1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "p1_manifest_sha256": sha256_file(P1_MANIFEST),
            "backend": str(backend_path.relative_to(REPO)).replace("\\", "/"),
            "backend_sha256": backend_hash,
        },
        "canonical_subset": {
            "field": "Psi in C^3 on a fixed three-torus",
            "flow": "real-L2 gradient flow of the P1 reference functional",
            "eta_shell": float(params["eta_shell"]),
            "historical_backend": "non-variational proxy; excluded",
        },
        "derived": {
            "continuous_shell_wave_number": q_shell,
            "continuous_shell_mass": shell_mass,
            "h2_coercivity_constant": h2_coercivity,
            "family_mass_eigenvalues": family_masses,
            "lock_projector": projector,
            "classii_coefficient_matrix": classii,
            "young_constant_per_unit_volume": young_constant,
            "exact_local_potential_floor": potential_floor,
        },
        "assertions": assertions,
        "proof_boundary": {
            "closed_here": [
                "full linear self-adjointness and lower-bound inputs",
                "family/lock sign conditions",
                "Class-II coefficient-matrix coercivity",
                "sextic energy-coercivity inequality",
            ],
            "not_closed_by_this_program": [
                "local existence and uniqueness",
                "Galerkin/chain-rule energy identity and global continuation",
                "continuous dependence and positive-time smoothing",
            ],
        },
        "verdict": "A2-FULL-COERCIVITY-BASELINE-PASS" if passed else "A2-FULL-COERCIVITY-BASELINE-FAIL",
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    output = args.output if args.output.is_absolute() else REPO / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    for assertion in result["assertions"]:
        label = "PASS" if assertion["passed"] else "FAIL"
        print(f"{label}: {assertion['name']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Evidence: {output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
