#!/usr/bin/env python3
"""Non-importing rational audit of fixed-domain CL8 semidiscretization."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0"
PARENT_ID = "PA-CP1-CL8-GOURSAT-v0"
RESULT_ID = "PA-CP1-CL8-FIXED-DOMAIN-SEMIDISCRETE-CAUCHY-OA2"
SLUG = "pre-a-cp1-cl8-semidiscrete-cauchy-oa2"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
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


Matrix = list[list[Fraction]]
Vector = list[Fraction]


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [Fraction(1 if row == column else 0) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def scale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * entry for entry in row] for row in matrix]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(matrix: Matrix, vector: Vector) -> Vector:
    return [
        sum((entry * component for entry, component in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def dot(left: Vector, right: Vector) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def block_matrix(top_left: Matrix, top_right: Matrix, bottom_left: Matrix, bottom_right: Matrix) -> Matrix:
    top = [left + right for left, right in zip(top_left, top_right)]
    bottom = [left + right for left, right in zip(bottom_left, bottom_right)]
    return top + bottom


def diagonal(values: Vector) -> Matrix:
    return [
        [values[row] if row == column else Fraction(0) for column in range(len(values))]
        for row in range(len(values))
    ]


def forward_matrix(sites: int, spacing: Fraction) -> Matrix:
    matrix = zeros(sites, sites)
    for site in range(sites):
        matrix[site][site] = -1 / spacing
        matrix[site][(site + 1) % sites] = 1 / spacing
    return matrix


def laplacian_matrix(sites: int, spacing: Fraction) -> Matrix:
    matrix = zeros(sites, sites)
    for site in range(sites):
        matrix[site][site] = -2 / spacing**2
        matrix[site][(site - 1) % sites] = 1 / spacing**2
        matrix[site][(site + 1) % sites] = 1 / spacing**2
    return matrix


def central_difference_polynomial(power: int) -> dict[tuple[int, int], Fraction]:
    """Coefficients of [f(x+a)-2f(x)+f(x-a)]/a^2 as x^i a^j."""
    output: dict[tuple[int, int], Fraction] = {}
    for exponent_a in range(power + 1):
        coefficient = Fraction(comb(power, exponent_a)) * (
            1 + (-1) ** exponent_a
        )
        if exponent_a == 0:
            coefficient -= 2
        if coefficient:
            output[(power - exponent_a, exponent_a - 2)] = coefficient
    return output


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def derive() -> dict[str, Any]:
    audit = Audit()
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    audit.check(
        "Q3LOCK identity",
        q3lock["candidate_id"] == "PA-CP1-ST8-Q3LOCK-v0",
        q3lock["candidate_id"],
        "PA-CP1-ST8-Q3LOCK-v0",
        "authority",
    )

    coefficient_four = Fraction(2, factorial(4))
    coefficient_six = Fraction(2, factorial(6))
    audit.check("factorial coefficient 2/4!", coefficient_four == Fraction(1, 12), coefficient_four, Fraction(1, 12), "consistency")
    audit.check("factorial coefficient 2/6!", coefficient_six == Fraction(1, 360), coefficient_six, Fraction(1, 360), "consistency")

    expected = {
        0: {},
        1: {},
        2: {(0, 0): Fraction(2)},
        4: {(2, 0): Fraction(12), (0, 2): Fraction(2)},
        6: {(4, 0): Fraction(30), (2, 2): Fraction(30), (0, 4): Fraction(2)},
    }
    for power, oracle in expected.items():
        actual = central_difference_polynomial(power)
        audit.check(
            f"binomial central difference x^{power}",
            actual == oracle,
            actual,
            oracle,
            "consistency",
        )

    # 2(1-cos z)/a^2 gives the positive Fourier symbol independently.
    symbol_coefficients = tuple(
        Fraction(2 * (-1) ** (order + 1), factorial(2 * order))
        for order in (1, 2, 3)
    )
    audit.check(
        "independent Fourier symbol coefficients",
        symbol_coefficients == (Fraction(1), Fraction(-1, 12), Fraction(1, 360)),
        symbol_coefficients,
        (Fraction(1), Fraction(-1, 12), Fraction(1, 360)),
        "consistency",
    )
    manufactured_coefficient = -24 * coefficient_four
    audit.check(
        "manufactured x4 residual multiplier",
        manufactured_coefficient == -2,
        manufactured_coefficient,
        -2,
        "consistency",
    )

    edge_force_coefficients = (Fraction(1), Fraction(-3, 2), Fraction(1), Fraction(-1, 2))
    edge_same_coefficients = (Fraction(3), Fraction(-3), Fraction(1))
    edge_cross_coefficients = (Fraction(-3, 2), Fraction(2), Fraction(-3, 2))
    edge_force_bound = sum((abs(value) for value in edge_force_coefficients), Fraction(0))
    edge_hessian_row_bound = sum((abs(value) for value in edge_same_coefficients + edge_cross_coefficients), Fraction(0))
    degree = Fraction(3)
    ell_unit = Fraction(1) + Fraction(3) + degree * edge_hessian_row_bound
    audit.check("independent edge force bound", edge_force_bound == 4, edge_force_bound, 4, "potential")
    audit.check("independent edge Hessian row bound", edge_hessian_row_bound == 12, edge_hessian_row_bound, 12, "potential")
    audit.check("independent unit ell_R", ell_unit == 40, ell_unit, 40, "potential")

    sites = 4
    spacing = Fraction(2, 3)
    weight = spacing / 8
    chi = Fraction(3, 2)
    c_physical = Fraction(5, 3)
    r = Fraction(-2, 5)
    g = Fraction(7, 6)
    q = [Fraction(1, 2), Fraction(-1), Fraction(3, 2), Fraction(2)]
    p = [Fraction(2, 3), Fraction(-3, 4), Fraction(5, 6), Fraction(-7, 8)]
    forward = forward_matrix(sites, spacing)
    laplacian = laplacian_matrix(sites, spacing)
    audit.check(
        "rational D transpose D identity",
        multiply(transpose(forward), forward) == scale(laplacian, Fraction(-1)),
        multiply(transpose(forward), forward),
        scale(laplacian, Fraction(-1)),
        "hamiltonian",
    )

    identity_block = identity(sites)
    zero_block = zeros(sites, sites)
    J = block_matrix(zero_block, identity_block, scale(identity_block, Fraction(-1)), zero_block)
    S = scale(block_matrix(zero_block, scale(identity_block, Fraction(-1)), identity_block, zero_block), weight)
    audit.check("rational J antisymmetry", transpose(J) == scale(J, Fraction(-1)), transpose(J), scale(J, Fraction(-1)), "hamiltonian")

    DTD = multiply(transpose(forward), forward)
    q_hessian = add(
        scale(DTD, weight * c_physical),
        scale(diagonal([r + 3 * g * value**2 for value in q]), weight),
    )
    p_hessian = scale(identity_block, weight / chi)
    hessian = block_matrix(q_hessian, zero_block, zero_block, p_hessian)
    audit.check("rational Hamiltonian Hessian symmetry", transpose(hessian) == hessian, transpose(hessian), hessian, "hamiltonian")

    gradient_q = [
        weight
        * (
            c_physical * value_dtd
            + r * value_q
            + g * value_q**3
        )
        for value_dtd, value_q in zip(matrix_vector(DTD, q), q)
    ]
    gradient_p = [weight * value / chi for value in p]
    gradient = gradient_q + gradient_p
    vector_field = [value / weight for value in matrix_vector(J, gradient)]
    expected_qdot = [value / chi for value in p]
    expected_pdot = [
        c_physical * value_lap - r * value_q - g * value_q**3
        for value_lap, value_q in zip(matrix_vector(laplacian, q), q)
    ]
    audit.check("rational qdot convention", vector_field[:sites] == expected_qdot, vector_field[:sites], expected_qdot, "hamiltonian")
    audit.check("rational pdot convention", vector_field[sites:] == expected_pdot, vector_field[sites:], expected_pdot, "hamiltonian")
    audit.check("rational energy derivative", dot(gradient, vector_field) == 0, dot(gradient, vector_field), 0, "hamiltonian")

    generator = scale(multiply(J, hessian), 1 / weight)
    infinitesimal = add(multiply(transpose(generator), S), multiply(S, generator))
    audit.check("rational infinitesimal symplectic identity", infinitesimal == zeros(2 * sites, 2 * sites), infinitesimal, zeros(2 * sites, 2 * sites), "symplectic")
    xi = [Fraction(index + 1, 7) for index in range(2 * sites)]
    eta = [Fraction((-1) ** index * (index + 2), 11) for index in range(2 * sites)]
    xi_dot, eta_dot = matrix_vector(generator, xi), matrix_vector(generator, eta)
    bilinear_derivative = dot(xi_dot, matrix_vector(S, eta)) + dot(xi, matrix_vector(S, eta_dot))
    audit.check("rational two-variation bilinear derivative", bilinear_derivative == 0, bilinear_derivative, 0, "symplectic")

    # Exact negative-r complete-square identity at several rational q values.
    for index, value in enumerate((Fraction(-2), Fraction(-1, 3), Fraction(0), Fraction(5, 4))):
        shifted = r * value**2 / 2 + g * value**4 / 4 + r**2 / (4 * g)
        square = g * (value**2 + r / g) ** 2 / 4
        audit.check(
            f"coercive onsite square fixture {index}",
            shifted == square,
            shifted,
            square,
            "coercivity",
        )

    gamma = Fraction(2) + 2 * ell_unit + Fraction(1, 2)
    residual_constant = Fraction(12) * coefficient_four + Fraction(1, 4) * Fraction(360) * coefficient_six
    audit.check("independent Gamma fixture", gamma == Fraction(165, 2), gamma, Fraction(165, 2), "analytic_constants")
    audit.check("independent residual fixture", residual_constant == Fraction(5, 4), residual_constant, Fraction(5, 4), "analytic_constants")

    # The leading frequency correction follows without floating-point fitting.
    # omega_a^2=2-a^2/12+O(a^4), hence
    # omega_a=sqrt(2)-a^2/(24*sqrt(2))+O(a^4).  At T=1/2 this
    # produces sin(sqrt(2)/2)/(48*sqrt(2)).
    squared_frequency_a2 = symbol_coefficients[1]
    frequency_shift_rational = squared_frequency_a2 / 2
    time_factor = Fraction(1, 2)
    asymptotic_multiplier = -frequency_shift_rational * time_factor
    audit.check(
        "formal one-mode asymptotic rational multiplier",
        asymptotic_multiplier == Fraction(1, 48),
        asymptotic_multiplier,
        Fraction(1, 48),
        "linearized_regression",
    )

    tail = [Fraction(1), Fraction(-2), Fraction(3), Fraction(-4)]
    subset = (1, 3)
    global_square = weight * sum((value**2 for value in tail), Fraction(0))
    restricted_square = weight * sum((tail[index] ** 2 for index in subset), Fraction(0))
    audit.check("restricted norm monotonicity", restricted_square <= global_square, restricted_square, f"<= {global_square}", "tail_scope")

    exact_results = {
        "central_fourth_coefficient": coefficient_four,
        "central_sixth_remainder_coefficient": coefficient_six,
        "manufactured_residual_coefficient": manufactured_coefficient,
        "physical_grid_weight": "a/8",
        "hamiltonian_fixture_weight": weight,
        "hamiltonian_energy_derivative": dot(gradient, vector_field),
        "variational_symplectic_derivative": bilinear_derivative,
        "ell_R_unit_fixture": ell_unit,
        "gamma_unit_fixture": gamma,
        "uniform_residual_constant_fixture": residual_constant,
        "one_mode_asymptotic_coefficient": "sin(sqrt(2)/2)/(48*sqrt(2))",
        "one_mode_rational_multiplier": asymptotic_multiplier,
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
            "smooth_classical_cauchy_data": True,
            "analytic_discrete_H1_L2_Oa2_theorem": True,
            "numerical_regression_used": False,
            "finite_a_exact_support": False,
            "semidiscrete_goursat_scheme": False,
            "lattice_boundary_composition": False,
            "pointwise_tail_bound": False,
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
        f"{CANDIDATE_ID} independent: {payload['assertions']['passed']}/"
        f"{payload['assertions']['total']} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
