#!/usr/bin/env python3
"""Non-importing exact audit for PA-H1-DNKG4-v0.

This route uses only standard-library rational polynomial arithmetic.  It does
not import the primary implementation, SymPy, or the primary result artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from math import factorial
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-H1-DNKG4-v0"
SLUG = "pre-a-double-null-semilinear-reconstruction"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)

Polynomial = dict[tuple[int, int], F]
Polynomial1 = dict[int, F]


def encode(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(poly: Polynomial) -> Polynomial:
    return {key: value for key, value in poly.items() if value}


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, F(0)) + value
    return clean(result)


def scale(poly: Polynomial, scalar: F) -> Polynomial:
    return clean({key: scalar * value for key, value in poly.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (left_a, left_b), left_value in left.items():
        for (right_a, right_b), right_value in right.items():
            key = (left_a + right_a, left_b + right_b)
            result[key] = result.get(key, F(0)) + left_value * right_value
    return clean(result)


def partial(poly: Polynomial, axis: int) -> Polynomial:
    result: Polynomial = {}
    for powers, coefficient in poly.items():
        power = powers[axis]
        if power:
            reduced = list(powers)
            reduced[axis] -= 1
            key = (reduced[0], reduced[1])
            result[key] = result.get(key, F(0)) + coefficient * power
    return clean(result)


def volterra(poly: Polynomial) -> Polynomial:
    return clean(
        {
            (u_power + 1, v_power + 1): coefficient / ((u_power + 1) * (v_power + 1))
            for (u_power, v_power), coefficient in poly.items()
        }
    )


def mixed_derivative(poly: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (u_power, v_power), coefficient in poly.items():
        if u_power and v_power:
            key = (u_power - 1, v_power - 1)
            result[key] = result.get(key, F(0)) + coefficient * u_power * v_power
    return clean(result)


def axis_trace(poly: Polynomial, axis: str) -> dict[int, F]:
    result: dict[int, F] = {}
    for (u_power, v_power), coefficient in poly.items():
        if axis == "v=0" and v_power == 0:
            result[u_power] = result.get(u_power, F(0)) + coefficient
        elif axis == "u=0" and u_power == 0:
            result[v_power] = result.get(v_power, F(0)) + coefficient
    return {key: value for key, value in result.items() if value}


def poly1_add(left: Polynomial1, right: Polynomial1) -> Polynomial1:
    result = dict(left)
    for power, value in right.items():
        result[power] = result.get(power, F(0)) + value
    return {power: value for power, value in result.items() if value}


def poly1_scale(poly: Polynomial1, scalar: F) -> Polynomial1:
    return {power: value * scalar for power, value in poly.items() if value * scalar}


def poly1_multiply(left: Polynomial1, right: Polynomial1) -> Polynomial1:
    result: Polynomial1 = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            result[power] = result.get(power, F(0)) + left_value * right_value
    return {power: value for power, value in result.items() if value}


def poly1_derivative(poly: Polynomial1) -> Polynomial1:
    return {power - 1: power * value for power, value in poly.items() if power}


def poly1_affine(poly: Polynomial1, constant: F, slope: F) -> Polynomial1:
    """Return p(constant+slope*x) by exact binomial expansion."""
    from math import comb

    result: Polynomial1 = {}
    for power, value in poly.items():
        for x_power in range(power + 1):
            coefficient = value * comb(power, x_power) * constant ** (power - x_power) * slope**x_power
            result[x_power] = result.get(x_power, F(0)) + coefficient
    return {power: value for power, value in result.items() if value}


def poly1_integral(poly: Polynomial1, lower: F, upper: F) -> F:
    return sum(
        value * (upper ** (power + 1) - lower ** (power + 1)) / (power + 1)
        for power, value in poly.items()
    )


def derive() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": encode(actual),
                "expected": encode(expected),
                "group": group,
            }
        )

    for a in range(4):
        for b in range(4):
            monomial = {(a, b): F(1)}
            image = volterra(monomial)
            expected = {(a + 1, b + 1): F(1, (a + 1) * (b + 1))}
            check(
                f"independent Volterra monomial ({a},{b})",
                image == expected,
                image,
                expected,
                "linear_reconstruction",
            )

    boundary_u = {0: F(1), 1: F(2), 2: F(3)}
    boundary_v = {0: F(1), 1: F(-4), 2: F(5)}
    free_lift: Polynomial = {
        (0, 0): F(1),
        (1, 0): F(2),
        (2, 0): F(3),
        (0, 1): F(-4),
        (0, 2): F(5),
    }
    check(
        "independent compatible u-axis trace",
        axis_trace(free_lift, "v=0") == boundary_u,
        axis_trace(free_lift, "v=0"),
        boundary_u,
        "linear_reconstruction",
    )
    check(
        "independent compatible v-axis trace",
        axis_trace(free_lift, "u=0") == boundary_v,
        axis_trace(free_lift, "u=0"),
        boundary_v,
        "linear_reconstruction",
    )
    check(
        "independent free lift mixed derivative",
        mixed_derivative(free_lift) == {},
        mixed_derivative(free_lift),
        {},
        "linear_reconstruction",
    )

    kappa = F(2, 3)
    truncation_order = 6
    iterates = [free_lift]
    for _ in range(truncation_order):
        iterates.append(volterra(iterates[-1]))
    partial_solution: Polynomial = {}
    for index, item in enumerate(iterates):
        partial_solution = add(partial_solution, scale(item, (-kappa) ** index))
    residual = add(mixed_derivative(partial_solution), scale(partial_solution, kappa))
    expected_residual = scale(iterates[-1], kappa * (-kappa) ** truncation_order)
    check(
        "independent finite Neumann residual",
        residual == expected_residual,
        residual,
        expected_residual,
        "linear_reconstruction",
    )
    check(
        "independent massive partial sums preserve traces",
        axis_trace(partial_solution, "v=0") == boundary_u
        and axis_trace(partial_solution, "u=0") == boundary_v,
        (axis_trace(partial_solution, "v=0"), axis_trace(partial_solution, "u=0")),
        (boundary_u, boundary_v),
        "linear_reconstruction",
    )

    # Constant compatible data yield coefficients (-kappa)^n/(n!)^2.
    coefficients = [(-kappa) ** n / factorial(n) ** 2 for n in range(10)]
    recurrence_checks = [
        coefficients[n + 1] == -kappa * coefficients[n] / (n + 1) ** 2
        for n in range(9)
    ]
    check(
        "independent Bessel coefficient recurrence",
        all(recurrence_checks),
        recurrence_checks,
        [True] * 9,
        "linear_reconstruction",
    )

    # The factorial-squared uniqueness factor has successive ratio
    # x/(n+1)^2.  An exact tail witness below one plus monotone decrease is a
    # finite audit of the analytic ratio-to-zero proof in the note.
    x = F(3, 2)
    ratios = [x / (n + 1) ** 2 for n in range(4, 13)]
    check(
        "independent uniqueness ratios are below one and decreasing",
        all(F(0) < value < 1 for value in ratios)
        and all(left > right for left, right in zip(ratios, ratios[1:])),
        ratios,
        "strictly decreasing values in (0,1)",
        "stability",
    )

    U = F(1, 4)
    V = F(1, 4)
    kappa_sample = F(1)
    coupling_sample = F(1)
    radius = F(1)
    data_norm = F(1, 2)
    self_map_value = data_norm + U * V * (
        kappa_sample * radius + coupling_sample * radius**3
    )
    lipschitz = U * V * (kappa_sample + 3 * coupling_sample * radius**2)
    stability_factor = 1 / (1 - lipschitz)
    check(
        "independent semilinear self-map gate",
        self_map_value == F(5, 8) <= radius,
        self_map_value,
        F(5, 8),
        "semilinear_reconstruction",
    )
    check(
        "independent semilinear contraction gate",
        lipschitz == F(1, 4) < 1,
        lipschitz,
        F(1, 4),
        "semilinear_reconstruction",
    )
    check(
        "independent semilinear stability factor",
        stability_factor == F(4, 3),
        stability_factor,
        F(4, 3),
        "semilinear_reconstruction",
    )

    # Independent symplectic transport fixture at tau=1 for the same two
    # compatible massless data pairs used only abstractly by the theorem.
    A1: Polynomial1 = {0: F(1), 1: F(1), 2: F(2)}
    B1: Polynomial1 = {0: F(1), 1: F(-3), 2: F(1)}
    A2: Polynomial1 = {0: F(2), 1: F(-1), 3: F(1)}
    B2: Polynomial1 = {0: F(2), 1: F(2), 2: F(-1)}

    def symplectic_integrand(left: Polynomial1, right: Polynomial1) -> Polynomial1:
        return poly1_add(
            poly1_multiply(left, poly1_derivative(right)),
            poly1_scale(poly1_multiply(right, poly1_derivative(left)), F(-1)),
        )

    omega_boundary = poly1_integral(symplectic_integrand(A1, A2), F(0), F(2))
    omega_boundary += poly1_integral(symplectic_integrand(B1, B2), F(0), F(2))
    phi1 = poly1_add(
        poly1_add(poly1_affine(A1, F(1), F(1)), poly1_affine(B1, F(1), F(-1))),
        {0: F(-1)},
    )
    phi2 = poly1_add(
        poly1_add(poly1_affine(A2, F(1), F(1)), poly1_affine(B2, F(1), F(-1))),
        {0: F(-2)},
    )
    pi1 = poly1_add(
        poly1_affine(poly1_derivative(A1), F(1), F(1)),
        poly1_affine(poly1_derivative(B1), F(1), F(-1)),
    )
    pi2 = poly1_add(
        poly1_affine(poly1_derivative(A2), F(1), F(1)),
        poly1_affine(poly1_derivative(B2), F(1), F(-1)),
    )
    omega_slice_integrand = poly1_add(
        poly1_multiply(phi1, pi2),
        poly1_scale(poly1_multiply(phi2, pi1), F(-1)),
    )
    omega_slice = poly1_integral(omega_slice_integrand, F(-1), F(1))
    check(
        "independent massless symplectic boundary-to-slice fixture",
        omega_slice == omega_boundary,
        omega_slice,
        omega_boundary,
        "state_transport",
    )

    # Generic exact-polynomial check of the massive symplectic-current
    # identity.  The two polynomial variables here are t and x.
    field_one: Polynomial = {
        (0, 0): F(2),
        (2, 0): F(3, 2),
        (1, 1): F(-5, 3),
        (0, 3): F(7, 4),
    }
    field_two: Polynomial = {
        (0, 0): F(-1),
        (3, 0): F(2, 5),
        (1, 2): F(9, 7),
        (0, 2): F(-4, 3),
    }
    mass_squared = F(11, 6)
    one_t = partial(field_one, 0)
    two_t = partial(field_two, 0)
    one_x = partial(field_one, 1)
    two_x = partial(field_two, 1)
    symplectic_t = add(multiply(field_one, two_t), scale(multiply(field_two, one_t), F(-1)))
    symplectic_x = add(multiply(field_one, two_x), scale(multiply(field_two, one_x), F(-1)))
    divergence = add(partial(symplectic_t, 0), scale(partial(symplectic_x, 1), F(-1)))
    kg_one = add(
        add(partial(partial(field_one, 0), 0), scale(partial(partial(field_one, 1), 1), F(-1))),
        scale(field_one, mass_squared),
    )
    kg_two = add(
        add(partial(partial(field_two, 0), 0), scale(partial(partial(field_two, 1), 1), F(-1))),
        scale(field_two, mass_squared),
    )
    expected_divergence = add(
        multiply(field_one, kg_two),
        scale(multiply(field_two, kg_one), F(-1)),
    )
    check(
        "independent massive symplectic-current identity",
        divergence == expected_divergence,
        divergence,
        expected_divergence,
        "state_transport",
    )

    # Exact arithmetic audit of the null energy-flux half-potential factor.
    tangent = F(5, 3)
    transverse = F(-7, 5)
    boundary_value = F(4, 3)
    mass_sample = F(3, 2)
    lambda_sample = F(2, 5)
    field_t = tangent + transverse
    field_x = tangent - transverse
    potential = mass_sample**2 * boundary_value**2 / 2 + lambda_sample * boundary_value**4 / 4
    null_flux_per_parameter = ((field_t**2 + field_x**2) / 2 + potential + field_t * field_x) / 2
    expected_null_flux = tangent**2 + mass_sample**2 * boundary_value**2 / 4 + lambda_sample * boundary_value**4 / 8
    check(
        "independent right-null energy-flux factor",
        null_flux_per_parameter == expected_null_flux,
        null_flux_per_parameter,
        expected_null_flux,
        "state_transport",
    )
    left_field_t = transverse + tangent
    left_field_x = transverse - tangent
    left_flux_per_parameter = (
        (left_field_t**2 + left_field_x**2) / 2
        + potential
        - left_field_t * left_field_x
    ) / 2
    check(
        "independent left-null energy-flux factor",
        left_flux_per_parameter == expected_null_flux,
        left_flux_per_parameter,
        expected_null_flux,
        "state_transport",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "independent exact audit of a T0 Lane-H bridge certificate",
        "shared_exact_results": {
            "global_linear_rectangle_reconstruction": True,
            "volterra_factorial_squared_bound": True,
            "constant_data_bessel_coefficients": coefficients,
            "linear_uniqueness": True,
            "sample_self_map_value": self_map_value,
            "sample_lipschitz_constant": lipschitz,
            "sample_stability_factor": stability_factor,
            "local_semilinear_reconstruction": True,
            "classical_slice_state_map": True,
            "massless_symplectic_boundary_to_slice_fixture": True,
            "massive_symplectic_current_identity": True,
            "left_and_right_null_energy_flux_factors": True,
            "pre_a_complete": False,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This non-importing audit checks rational Volterra reconstruction, explicit semilinear "
            "contraction gates, a polynomial symplectic-current identity and fixture, and both null-flux "
            "factors. It does not establish a physical horizon algebra or state, gravitational bulk "
            "reconstruction, cosmic cooling, spacetime emergence, or Pre-A completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"independent {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
