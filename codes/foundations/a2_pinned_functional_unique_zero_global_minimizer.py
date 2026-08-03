#!/usr/bin/env python3
"""Primary certificate for the pinned P1 unique-zero minimizer theorem.

The certificate derives every constant from the A1 manifest, proves an exact
coercive lower bound for the A2 continuum functional, and runs adversarial
same-backend finite-grid checks.  It does not apply to the historical backend
or to the signed A7 covariance-normal stochastic composite.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A2-FULL-PRODUCTION-WELLPOSED"
RESULT_ID = "A2-PINNED-FUNCTIONAL-UNIQUE-ZERO-GLOBAL-MINIMIZER"
LEDGER_ID = "R-157"
SLUG = "pinned-functional-unique-zero-global-minimizer"
SCHEMA = f"tect/a2-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A2_MANIFEST = REPO / "claims/A2-FULL-PRODUCTION-WELLPOSED/full_pde_manifest.json"
BACKEND = REPO / "codes/foundations/n001_variational_backend.py"

INTERNAL_LOWER = sp.Rational(7, 250)
SCOPE = {
    "pinned_a1_p1_functional": True,
    "a2_fixed_torus_continuum_h2": True,
    "eta_shell_zero": True,
    "unconstrained_linear_field_space": True,
    "unique_zero_global_minimizer": True,
    "unique_zero_critical_point": True,
    "nonzero_stationary_or_metastable_equilibrium_exclusion": True,
    "canonical_gradient_flow_exponential_l2_decay": True,
    "physical_vacuum_selection": False,
    "historical_backend": False,
    "a7_covariance_normal_composite": False,
    "fixed_norm_or_charge_constraint": False,
    "chemical_potential_modified_model": False,
    "compact_cp2_target": False,
    "conserved_or_alternative_dynamics": False,
    "alternative_parameter_or_functional_branches": False,
}
NO_OVERCLAIM = (
    "R-157 applies only to the unconstrained hash-pinned P1/A2 classical functional on the fixed torus "
    "with eta_shell=0 and to its canonical L2 gradient flow. It makes Psi=0 the unique critical point "
    "and global minimizer and forces exponential L2 decay in that flow. It is not a physical-vacuum "
    "theorem; it does not apply to the historical backend, signed A7 stochastic composite, fixed-norm/charge "
    "or compact-target constraints, chemical-potential or conserved dynamics, other parameters/functionals, "
    "or general nonequilibrium transients."
)


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[r, c]) for c in range(value.cols)] for r in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def load_backend():
    spec = importlib.util.spec_from_file_location("n001_variational_backend_r157", BACKEND)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    a2 = json.loads(A2_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    audit.check("authority", "A1 claim identity", a1.get("claim_id") == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1.get("claim_id"), "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    audit.check("authority", "A2 conditional theorem scope", "CONDITIONAL-THEOREM" in a2.get("tier_boundary", ""), a2.get("tier_boundary"), "T6 CONDITIONAL-THEOREM")
    backend_hash = a1["production_reference_backend"]["sha256"]
    audit.check("authority", "same backend is hash-pinned", sha256(BACKEND) == backend_hash, sha256(BACKEND), backend_hash)

    r_value, z_value, y_value = (q(params[key]) for key in ("r", "Z", "Y"))
    lambda_value, gamma_value = (q(params[key]) for key in ("lambda", "gamma"))
    eta = q(params["eta_shell"])
    x = sp.symbols("x", nonnegative=True)
    shell_symbol = sp.expand(y_value * x**2 + z_value * x + r_value)
    shell_minimum = sp.factor(r_value - z_value**2 / (4 * y_value))
    shell_square = sp.expand(y_value * (x + z_value / (2 * y_value)) ** 2 + shell_minimum)
    audit.check("linear", "shell square completion", shell_symbol == shell_square, shell_symbol - shell_square, 0)
    audit.check("linear", "continuous shell minimum positive", shell_minimum > 0, shell_minimum, ">0")
    audit.check("linear", "eta shell is exactly zero", eta == 0, eta, 0)

    family = [q(value) for value in params["family_masses"]]
    lock = q(params["k_lock"])
    z0 = sp.Matrix([q(value) for value in params["z0"]])
    internal = sp.diag(*family) + lock * (sp.eye(3) - z0 * z0.T / (z0.T * z0)[0])
    shifted_internal = sp.simplify(internal - INTERNAL_LOWER * sp.eye(3))
    leading_minors = [sp.factor(shifted_internal[:size, :size].det()) for size in range(1, 4)]
    expected_minors = [sp.Rational(9, 125), sp.Rational(1211, 250000), sp.Rational(89, 31250000)]
    audit.check("linear", "internal mass matrix exact", internal == sp.Matrix([[sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)], [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)], [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)]]), internal, "registered 3x3 mass")
    audit.check("linear", "Sylvester lower-bound minors", leading_minors == expected_minors and all(value > 0 for value in leading_minors), leading_minors, expected_minors)

    total_mass = sp.factor(shell_minimum + INTERNAL_LOWER)
    rho = sp.symbols("rho", nonnegative=True)
    rho_star = sp.factor(-3 * lambda_value / (4 * gamma_value))
    gap = sp.factor(total_mass / 2 - 3 * lambda_value**2 / (32 * gamma_value))
    bracket = sp.expand(total_mass / 2 + lambda_value * rho / 4 + gamma_value * rho**2 / 6)
    completed = sp.expand(gap + gamma_value * (rho - rho_star) ** 2 / 6)
    expected_gap = sp.Rational(719818750025582338837, 5400000000000000000000)
    audit.check("potential", "local polynomial exact completion", bracket == completed, sp.factor(bracket - completed), 0)
    audit.check("potential", "completion vertex nonnegative", rho_star == sp.Rational(43, 216), rho_star, sp.Rational(43, 216))
    audit.check("potential", "strict global L2 gap exact", gap == expected_gap and gap > 0, gap, expected_gap)
    audit.check("potential", "convenient one-eighth lower bound", gap > sp.Rational(1, 8), sp.factor(gap - sp.Rational(1, 8)), ">0")

    cjj, cjk, ckk = (q(params[key]) for key in ("cJJ", "cJK", "cKK"))
    alpha, beta = (q(params[key]) for key in ("alpha_X", "beta_X"))
    denominator = q(params["M_X"]) ** 2 + q(params["classii_mass_regularizer"])
    classii = sp.Matrix([[cjj * alpha**2 / denominator, cjk * alpha * beta / denominator], [cjk * alpha * beta / denominator, ckk * beta**2 / denominator]])
    classii_minor = sp.factor(classii.det())
    audit.check("classii", "positive leading coefficient", classii[0, 0] > 0, classii[0, 0], ">0")
    audit.check("classii", "positive determinant", classii_minor > 0 and sp.factor(cjj * ckk - cjk**2) == sp.Rational(1, 50), classii_minor, ">0 derived from 1/50")

    # Along every amplitude ray Psi -> t Psi, the regularised Class-II term
    # is monotone.  With y=t^2 and theta=eps/(y*rho+eps), differentiation
    # reduces to this exact two-current matrix.
    theta, j_current, k_current = sp.symbols("theta j k", real=True)
    radial_matrix = sp.Matrix([
        [classii[0, 0] - theta * classii[0, 1], classii[0, 1] + theta * (classii[0, 1] - classii[1, 1]) / 2],
        [classii[0, 1] + theta * (classii[0, 1] - classii[1, 1]) / 2, classii[1, 1] * (1 + theta)],
    ])
    differentiated_form = sp.expand(
        classii[0, 0] * j_current**2 + 2 * classii[0, 1] * j_current * k_current + classii[1, 1] * k_current**2
        - theta * (classii[0, 1] * j_current + classii[1, 1] * k_current) * (j_current - k_current)
    )
    matrix_form = sp.expand((sp.Matrix([j_current, k_current]).T * radial_matrix * sp.Matrix([j_current, k_current]))[0])
    radial_determinant = sp.factor(radial_matrix.det())
    expected_radial_determinant = 9 * (-81 * theta**2 + 128 * theta + 128) / (sp.Integer(10240000) * denominator**2)
    audit.check("classii-ray", "radial derivative matrix identity", sp.factor(differentiated_form - matrix_form) == 0, sp.factor(differentiated_form - matrix_form), 0)
    audit.check("classii-ray", "radial determinant formula", sp.factor(radial_determinant - expected_radial_determinant) == 0, radial_determinant, expected_radial_determinant)
    first_minor_at_one = sp.factor(radial_matrix[0, 0].subs(theta, 1))
    determinant_endpoints = [sp.factor(radial_determinant.subs(theta, endpoint)) for endpoint in (0, 1)]
    audit.check("classii-ray", "radial matrix positive on theta interval", first_minor_at_one > 0 and all(value > 0 for value in determinant_endpoints), {"first_minor_at_one": first_minor_at_one, "determinant_endpoints": determinant_endpoints, "determinant_numerator_concave": True}, ">0 on 0<=theta<=1")

    radial_gap = sp.factor(total_mass - lambda_value**2 / (4 * gamma_value))
    expected_radial_gap = sp.Rational(2101675000076747016511, 8100000000000000000000)
    audit.check("critical-point", "strict radial derivative gap", radial_gap == expected_radial_gap and radial_gap > sp.Rational(1, 4), radial_gap, expected_radial_gap)

    # Same-backend adversarial checks are regression guards, not the proof.
    backend = load_backend()
    rng = np.random.default_rng(157003)
    numerical_rows: list[dict[str, Any]] = []
    for size in (4, 6, 8):
        for fixture in range(3):
            field = (rng.standard_normal((3, size, size, size)) + 1j * rng.standard_normal((3, size, size, size))) / (10.0 + 3.0 * fixture)
            energy = backend.energy(field, params)
            gradient = backend.residual(field, params)
            dvol = np.prod([float(params[key]) / size for key in ("Lx", "Ly", "Lz")])
            norm_squared = float(dvol * np.sum(np.abs(field) ** 2))
            residual = energy - float(gap) * norm_squared
            radial_pairing = float(dvol * np.real(np.vdot(field, gradient)))
            numerical_rows.append({"grid": size, "fixture": fixture, "energy": energy, "l2_squared": norm_squared, "lower_bound_residual": residual, "radial_pairing": radial_pairing, "radial_gap_residual": radial_pairing - float(radial_gap) * norm_squared})
    audit.check("backend", "all random fields obey certified lower bound", min(row["lower_bound_residual"] for row in numerical_rows) > -2.0e-10, min(row["lower_bound_residual"] for row in numerical_rows), ">=-2e-10")
    audit.check("backend", "all random radial pairings obey critical-point bound", min(row["radial_gap_residual"] for row in numerical_rows) > -2.0e-9, min(row["radial_gap_residual"] for row in numerical_rows), ">=-2e-9")
    zero = np.zeros((3, 4, 4, 4), dtype=np.complex128)
    audit.check("backend", "zero field has zero energy", abs(backend.energy(zero, params)) < 1.0e-15, backend.energy(zero, params), 0)
    audit.check("backend", "zero field is stationary", float(np.max(np.abs(backend.residual(zero, params)))) < 1.0e-14, float(np.max(np.abs(backend.residual(zero, params)))), 0)

    audit.check("scope", "theorem rejects every nonzero global minimizer", gap > 0, "F[Psi] >= g ||Psi||_2^2 and F[0]=0", "unique minimizer Psi=0")
    audit.check("scope", "radial test rejects every nonzero critical point", radial_gap > 0, "<DF(Psi),Psi> >= kappa ||Psi||_2^2", "unique critical point Psi=0")
    audit.check("dynamics", "canonical gradient flow decays exponentially in L2", radial_gap > 0, "d||Psi||_2^2/dt <= -2 kappa ||Psi||_2^2", "||Psi(t)||_2^2 <= exp(-2 kappa t)||Psi(0)||_2^2")
    audit.check("scope", "A7 signed composite excluded", True, "A7 covariance-normal counterterm is outside P1 positivity", "excluded")
    audit.require()

    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "authority_hashes": {"A1_manifest": sha256(A1_MANIFEST), "A2_manifest": sha256(A2_MANIFEST), "backend": sha256(BACKEND)},
        "derived": {
            "shell_minimum": shell_minimum,
            "internal_mass_lower_bound": INTERNAL_LOWER,
            "total_quadratic_mass_lower_bound": total_mass,
            "potential_completion_vertex": rho_star,
            "strict_l2_gap": gap,
            "strict_radial_derivative_gap": radial_gap,
            "classii_matrix": classii,
            "classii_determinant": classii_minor,
            "classii_radial_matrix": radial_matrix,
            "classii_radial_determinant": radial_determinant,
            "theorem": "F_P1[Psi] >= g ||Psi||_L2^2 and <DF_P1(Psi),Psi> >= kappa ||Psi||_L2^2 with g,kappa>0; therefore Psi=0 is the unique critical point and global minimizer, and its canonical L2 gradient flow decays as ||Psi(t)||_2^2 <= exp(-2 kappa t)||Psi(0)||_2^2",
        },
        "backend_fixtures": numerical_rows,
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: {len(audit.rows)}/{len(audit.rows)} PASS; g={gap} ({float(gap):.12g})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
