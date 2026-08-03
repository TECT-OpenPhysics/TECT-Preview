#!/usr/bin/env python3
"""Primary audit for fixed-domain CL8 semidiscrete Cauchy convergence.

The exact checks cover the physical one-eighth Hamiltonian ledger, central
difference consistency, Hamiltonian and variational symplectic identities,
and a rigorous Arb enclosure of one linearized Fourier-mode regression.  The
general nonlinear O(a^2) theorem is proved analytically in the certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from math import factorial
from pathlib import Path
from typing import Any

import sympy as sp
from flint import arb, ctx


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0"
PARENT_ID = "PA-CP1-CL8-GOURSAT-v0"
RESULT_ID = "PA-CP1-CL8-FIXED-DOMAIN-SEMIDISCRETE-CAUCHY-OA2"
SLUG = "pre-a-cp1-cl8-semidiscrete-cauchy-oa2"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def periodic_forward_difference(sites: int, spacing: sp.Expr) -> sp.Matrix:
    matrix = sp.zeros(sites, sites)
    for site in range(sites):
        matrix[site, site] = -1 / spacing
        matrix[site, (site + 1) % sites] = 1 / spacing
    return matrix


def periodic_laplacian(sites: int, spacing: sp.Expr) -> sp.Matrix:
    matrix = sp.zeros(sites, sites)
    for site in range(sites):
        matrix[site, site] = -2 / spacing**2
        matrix[site, (site - 1) % sites] = 1 / spacing**2
        matrix[site, (site + 1) % sites] = 1 / spacing**2
    return matrix


def arb_regression(audit: Audit) -> dict[str, Any]:
    old_precision = ctx.prec
    ctx.prec = 160
    try:
        pi = arb.pi()
        final_time = arb(1) / 2
        continuum_frequency = arb(2).sqrt()
        continuum_value = (continuum_frequency * final_time).cos()
        sizes = (16, 32, 64, 128, 256)
        errors: list[arb] = []
        spacings: list[arb] = []
        for size in sizes:
            spacing = 2 * pi / size
            wave_number = 2 * (spacing / 2).sin() / spacing
            frequency = (1 + wave_number**2).sqrt()
            error = (frequency * final_time).cos() - continuum_value
            spacings.append(spacing)
            errors.append(error)
            audit.check(
                f"Arb M={size} error is strictly positive",
                error > arb(0),
                error.str(30),
                "positive interval",
                "arb_regression",
            )
        for index, (left, right) in enumerate(zip(errors, errors[1:])):
            ratio = left / right
            audit.check(
                f"Arb error decreases at refinement {sizes[index]}->{sizes[index + 1]}",
                left > right,
                (left.str(25), right.str(25)),
                "strict decrease",
                "arb_regression",
            )
            audit.check(
                f"Arb second-order ratio {sizes[index]}->{sizes[index + 1]}",
                ratio > arb(397) / 100 and ratio < arb(401) / 100,
                ratio.str(30),
                "(3.97,4.01)",
                "arb_regression",
            )
        asymptotic_constant = (
            (continuum_frequency / 2).sin() / (48 * continuum_frequency)
        )
        normalized_error = errors[-1] / spacings[-1] ** 2
        asymptotic_difference = normalized_error - asymptotic_constant
        audit.check(
            "Arb normalized M=256 error approaches derived coefficient",
            abs(asymptotic_difference) < arb(1) / 100000,
            asymptotic_difference.str(30),
            "absolute value below 1e-5",
            "arb_regression",
        )
        return {
            "precision_bits": ctx.prec,
            "sizes": list(sizes),
            "errors": [value.str(40) for value in errors],
            "ratios": [
                (errors[index] / errors[index + 1]).str(40)
                for index in range(len(errors) - 1)
            ],
            "normalized_M256": normalized_error.str(40),
            "asymptotic_constant": asymptotic_constant.str(40),
            "normalized_difference": asymptotic_difference.str(40),
        }
    finally:
        ctx.prec = old_precision


def derive() -> dict[str, Any]:
    audit = Audit()
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    audit.check(
        "Q3LOCK authority identity",
        q3lock["candidate_id"] == "PA-CP1-ST8-Q3LOCK-v0",
        q3lock["candidate_id"],
        "PA-CP1-ST8-Q3LOCK-v0",
        "authority",
    )
    audit.check(
        "Q3LOCK finite exact cone remains false",
        q3lock["causal_boundary"]["finite_continuous_time_exact_cone"] is False,
        q3lock["causal_boundary"]["finite_continuous_time_exact_cone"],
        False,
        "authority",
    )

    coefficient_four = Fraction(2, factorial(4))
    coefficient_six = Fraction(2, factorial(6))
    audit.check(
        "central-difference fourth-derivative coefficient",
        coefficient_four == Fraction(1, 12),
        coefficient_four,
        Fraction(1, 12),
        "consistency",
    )
    audit.check(
        "central-difference sixth-derivative remainder coefficient",
        coefficient_six == Fraction(1, 360),
        coefficient_six,
        Fraction(1, 360),
        "consistency",
    )

    x, spacing = sp.symbols("x a", real=True)
    expected_polynomials = {
        0: sp.Integer(0),
        1: sp.Integer(0),
        2: sp.Integer(2),
        4: 12 * x**2 + 2 * spacing**2,
        6: 30 * x**4 + 30 * spacing**2 * x**2 + 2 * spacing**4,
    }
    for power, expected in expected_polynomials.items():
        polynomial = x**power
        difference = sp.expand(
            (polynomial.subs(x, x + spacing) - 2 * polynomial + polynomial.subs(x, x - spacing))
            / spacing**2
        )
        audit.check(
            f"central difference on x^{power}",
            sp.expand(difference - expected) == 0,
            difference,
            expected,
            "consistency",
        )

    wave_number = sp.symbols("k", real=True)
    positive_symbol = 4 * sp.sin(wave_number * spacing / 2) ** 2 / spacing**2
    symbol_series = sp.series(positive_symbol, spacing, 0, 6).removeO().expand()
    expected_series = (
        wave_number**2
        - coefficient_four * wave_number**4 * spacing**2
        + coefficient_six * wave_number**6 * spacing**4
    )
    audit.check(
        "Fourier symbol consistency series",
        sp.expand(symbol_series - expected_series) == 0,
        symbol_series,
        expected_series,
        "consistency",
    )

    alpha_component, time, c_physical = sp.symbols("alpha t c", real=True)
    manufactured = alpha_component * (1 + time) * x**4
    discrete_minus_continuum = sp.expand(
        (
            manufactured.subs(x, x + spacing)
            - 2 * manufactured
            + manufactured.subs(x, x - spacing)
        )
        / spacing**2
        - sp.diff(manufactured, x, 2)
    )
    residual_difference = sp.expand(-c_physical * discrete_minus_continuum)
    audit.check(
        "manufactured central residual",
        sp.expand(
            residual_difference
            + 2 * c_physical * alpha_component * (1 + time) * spacing**2
        )
        == 0,
        residual_difference,
        -2 * c_physical * alpha_component * (1 + time) * spacing**2,
        "consistency",
    )

    # Exact Hamiltonian fixture for one component.  The common proof extends
    # blockwise to all eight species and every symmetric Q3 potential Hessian.
    sites = 4
    spacing_value = sp.Rational(2, 3)
    weight = spacing_value / 8
    chi_value = sp.Rational(3, 2)
    c_value = sp.Rational(5, 3)
    r_value = sp.Rational(-2, 5)
    g_value = sp.Rational(7, 6)
    q_symbols = sp.symbols(f"q0:{sites}", real=True)
    p_symbols = sp.symbols(f"p0:{sites}", real=True)
    q_vector = sp.Matrix(q_symbols)
    p_vector = sp.Matrix(p_symbols)
    z_vector = sp.Matrix((*q_symbols, *p_symbols))
    forward = periodic_forward_difference(sites, spacing_value)
    laplacian = periodic_laplacian(sites, spacing_value)
    audit.check(
        "periodic D transpose D equals negative Laplacian",
        forward.T * forward == -laplacian,
        forward.T * forward,
        -laplacian,
        "hamiltonian",
    )
    hamiltonian = sp.expand(
        weight
        * (
            (p_vector.dot(p_vector)) / (2 * chi_value)
            + c_value * (forward * q_vector).dot(forward * q_vector) / 2
            + sum(
                (r_value * q**2 / 2 + g_value * q**4 / 4 for q in q_symbols),
                sp.Integer(0),
            )
        )
    )
    gradient = sp.Matrix([sp.diff(hamiltonian, coordinate) for coordinate in z_vector])
    hessian = sp.hessian(hamiltonian, z_vector)
    identity = sp.eye(sites)
    zero = sp.zeros(sites)
    symplectic_inverse = sp.BlockMatrix([[zero, identity], [-identity, zero]]).as_explicit()
    symplectic_matrix = weight * sp.BlockMatrix([[zero, -identity], [identity, zero]]).as_explicit()
    vector_field = sp.simplify(symplectic_inverse * gradient / weight)
    audit.check(
        "Hamiltonian Hessian is symmetric",
        hessian == hessian.T,
        hessian - hessian.T,
        sp.zeros(2 * sites),
        "hamiltonian",
    )
    audit.check(
        "J is antisymmetric",
        symplectic_inverse.T == -symplectic_inverse,
        symplectic_inverse.T,
        -symplectic_inverse,
        "hamiltonian",
    )
    audit.check(
        "Hamiltonian derivative vanishes exactly",
        sp.simplify((gradient.T * vector_field)[0]) == 0,
        sp.simplify((gradient.T * vector_field)[0]),
        0,
        "hamiltonian",
    )
    audit.check(
        "Hamilton qdot convention",
        all(sp.simplify(vector_field[index] - p_symbols[index] / chi_value) == 0 for index in range(sites)),
        vector_field[:sites, 0],
        p_vector / chi_value,
        "hamiltonian",
    )
    expected_pdot = c_value * laplacian * q_vector - sp.Matrix(
        [r_value * q + g_value * q**3 for q in q_symbols]
    )
    audit.check(
        "Hamilton pdot convention",
        all(sp.simplify(vector_field[sites + index] - expected_pdot[index]) == 0 for index in range(sites)),
        vector_field[sites:, 0],
        expected_pdot,
        "hamiltonian",
    )
    variational_generator = sp.simplify(symplectic_inverse * hessian / weight)
    infinitesimal_symplectic = sp.simplify(
        variational_generator.T * symplectic_matrix
        + symplectic_matrix * variational_generator
    )
    audit.check(
        "variational generator is infinitesimally symplectic",
        infinitesimal_symplectic == sp.zeros(2 * sites),
        infinitesimal_symplectic,
        sp.zeros(2 * sites),
        "symplectic",
    )
    xi = sp.Matrix([sp.Rational(index + 1, 7) for index in range(2 * sites)])
    eta = sp.Matrix([sp.Rational((-1) ** index * (index + 2), 11) for index in range(2 * sites)])
    bilinear_derivative = sp.simplify(
        (variational_generator * xi).T * symplectic_matrix * eta
        + xi.T * symplectic_matrix * (variational_generator * eta)
    )[0]
    audit.check(
        "two-variation symplectic bilinear derivative",
        bilinear_derivative == 0,
        bilinear_derivative,
        0,
        "symplectic",
    )

    # The negative quadratic onsite part has an exact shifted-square lower
    # bound.  Positive spatial and Q3-lock terms only improve coercivity.
    q = sp.symbols("q", real=True)
    onsite_shift = sp.expand(
        r_value * q**2 / 2 + g_value * q**4 / 4 + r_value**2 / (4 * g_value)
    )
    onsite_square = sp.expand(g_value * (q**2 + r_value / g_value) ** 2 / 4)
    audit.check(
        "onsite coercive shifted square",
        sp.expand(onsite_shift - onsite_square) == 0,
        onsite_shift,
        onsite_square,
        "hamiltonian",
    )

    # Derived analytic constants for a rational theorem fixture.  The values
    # are test oracles for formula drift, not evidence replacing the proof.
    alpha_value = Fraction(1)
    chi_bound_value = Fraction(1)
    ell_fixture = Fraction(1 + 3 + 36)
    gamma_fixture = (
        2 * Fraction(1) + 2 * ell_fixture + Fraction(1, 2)
    )
    length_fixture = Fraction(8)
    fourth_bound = Fraction(12)
    sixth_bound = Fraction(360)
    a_bar = Fraction(1, 2)
    residual_fixture = (
        fourth_bound * coefficient_four + a_bar**2 * sixth_bound * coefficient_six
    )
    audit.check(
        "modified-energy Gamma fixture",
        gamma_fixture == Fraction(165, 2),
        gamma_fixture,
        Fraction(165, 2),
        "analytic_constants",
    )
    audit.check(
        "uniform residual constant fixture",
        length_fixture == 8 and residual_fixture == Fraction(5, 4),
        residual_fixture,
        Fraction(5, 4),
        "analytic_constants",
    )
    audit.check(
        "unused alpha and chi fixture remain positive",
        alpha_value > 0 and chi_bound_value > 0,
        (alpha_value, chi_bound_value),
        "positive",
        "analytic_constants",
    )

    # A restricted weighted norm cannot exceed the global grid norm.  This is
    # the only algebra needed for the conditional aggregate-tail corollary.
    tail_fixture = [Fraction(1), Fraction(-2), Fraction(3), Fraction(-4)]
    subset = (1, 3)
    global_square = weight * sum((entry**2 for entry in tail_fixture), Fraction(0))
    subset_square = weight * sum((tail_fixture[index] ** 2 for index in subset), Fraction(0))
    audit.check(
        "restricted aggregate tail norm is bounded by global error norm",
        subset_square <= global_square,
        subset_square,
        f"<= {global_square}",
        "tail_scope",
    )

    arb_results = arb_regression(audit)
    exact_results = {
        "central_fourth_coefficient": coefficient_four,
        "central_sixth_remainder_coefficient": coefficient_six,
        "manufactured_residual_coefficient": sp.Integer(-2),
        "physical_grid_weight": "a/8",
        "hamiltonian_fixture_weight": weight,
        "hamiltonian_energy_derivative": sp.Integer(0),
        "variational_symplectic_derivative": bilinear_derivative,
        "ell_R_unit_fixture": ell_fixture,
        "gamma_unit_fixture": gamma_fixture,
        "uniform_residual_constant_fixture": residual_fixture,
        "arb_regression": arb_results,
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "result_id": RESULT_ID,
        "package_version": __version__,
        "verdict": "PASS",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "exact_results": exact_results,
        "scope": {
            "fixed_periodic_domain": True,
            "fixed_finite_time": True,
            "smooth_classical_cauchy_data": True,
            "analytic_discrete_H1_L2_Oa2_theorem": True,
            "arb_regression_is_theorem": False,
            "finite_a_exact_support": False,
            "aggregate_tail_corollary_requires_continuum_zero_region": True,
            "pointwise_tail_bound": False,
            "semidiscrete_goursat_scheme": False,
            "lattice_boundary_composition": False,
            "continuous_P1_H1_Oa2": False,
            "quantum_continuum": False,
            "physical_empty_space": False,
            "cp1_complete": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "script": serial(SCRIPT.relative_to(REPO)),
            "script_sha256": sha256(SCRIPT),
            "q3lock": serial(Q3LOCK.relative_to(REPO)),
            "q3lock_sha256": sha256(Q3LOCK),
            "python_flint_precision_bits": arb_results["precision_bits"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--selftest", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.selftest:
        atomic_json(arguments.output, payload)
    print(
        f"{CANDIDATE_ID}: {payload['assertions']['passed']}/"
        f"{payload['assertions']['total']} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
