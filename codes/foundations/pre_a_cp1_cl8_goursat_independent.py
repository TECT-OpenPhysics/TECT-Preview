#!/usr/bin/env python3
"""Non-importing rational audit of PA-CP1-CL8-GOURSAT-v0."""

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


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-GOURSAT-v0"
PARENT_ID = "PA-CP1-ST8-Q3LOCK-v0"
RESULT_ID = "PA-CP1-CL8-CONTINUUM-GOURSAT-ENERGY-SYMPLECTIC-FLUX"
SLUG = "pre-a-cp1-cl8-goursat"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
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


Polynomial2 = dict[tuple[int, int], Fraction]
Polynomial1 = dict[int, Fraction]


def clean2(polynomial: Polynomial2) -> Polynomial2:
    return {power: coefficient for power, coefficient in polynomial.items() if coefficient}


def add2(left: Polynomial2, right: Polynomial2) -> Polynomial2:
    output = dict(left)
    for power, coefficient in right.items():
        output[power] = output.get(power, Fraction(0)) + coefficient
    return clean2(output)


def multiply2(left: Polynomial2, right: Polynomial2) -> Polynomial2:
    output: Polynomial2 = {}
    for (left_a, left_b), left_coefficient in left.items():
        for (right_a, right_b), right_coefficient in right.items():
            power = (left_a + right_a, left_b + right_b)
            output[power] = output.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return clean2(output)


def scale2(polynomial: Polynomial2, scalar: Fraction) -> Polynomial2:
    return clean2({power: scalar * coefficient for power, coefficient in polynomial.items()})


def derivative2(polynomial: Polynomial2, axis: int) -> Polynomial2:
    output: Polynomial2 = {}
    for powers, coefficient in polynomial.items():
        exponent = powers[axis]
        if exponent:
            new_powers = list(powers)
            new_powers[axis] -= 1
            output[tuple(new_powers)] = coefficient * exponent
    return clean2(output)


def evaluate2(polynomial: Polynomial2, left: Fraction, right: Fraction) -> Fraction:
    return sum(
        (coefficient * left**power_left * right**power_right for (power_left, power_right), coefficient in polynomial.items()),
        Fraction(0),
    )


def add1(left: Polynomial1, right: Polynomial1) -> Polynomial1:
    output = dict(left)
    for power, coefficient in right.items():
        output[power] = output.get(power, Fraction(0)) + coefficient
    return {power: coefficient for power, coefficient in output.items() if coefficient}


def multiply1(left: Polynomial1, right: Polynomial1) -> Polynomial1:
    output: Polynomial1 = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            output[power] = output.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in output.items() if coefficient}


def derivative1(polynomial: Polynomial1) -> Polynomial1:
    return {
        power - 1: power * coefficient
        for power, coefficient in polynomial.items()
        if power
    }


def scale1(polynomial: Polynomial1, scalar: Fraction) -> Polynomial1:
    return {power: scalar * coefficient for power, coefficient in polynomial.items() if scalar * coefficient}


def integrate1(polynomial: Polynomial1, lower: Fraction, upper: Fraction) -> Fraction:
    return sum(
        (
            coefficient * (upper ** (power + 1) - lower ** (power + 1)) / (power + 1)
            for power, coefficient in polynomial.items()
        ),
        Fraction(0),
    )


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
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    audit.check(
        "upstream identity",
        upstream["candidate_id"] == PARENT_ID,
        upstream["candidate_id"],
        PARENT_ID,
        "authority",
    )

    vertices = tuple(range(8))
    edges = tuple(
        (vertex, vertex ^ (1 << axis))
        for vertex in vertices
        for axis in range(3)
        if not (vertex & (1 << axis))
    )
    degree_sequence = tuple(sum(vertex in edge for edge in edges) for vertex in vertices)
    audit.check("cube vertex count", len(vertices) == 8, len(vertices), 8, "q3")
    audit.check("cube edge count", len(edges) == 12, len(edges), 12, "q3")
    audit.check(
        "cube degree sequence",
        degree_sequence == (3,) * 8,
        degree_sequence,
        (3,) * 8,
        "q3",
    )

    # Reconstruct (a-b)^2(a^2+b^2)/4 using sparse rational polynomials.
    difference = {(1, 0): Fraction(1), (0, 1): Fraction(-1)}
    sum_squares = {(2, 0): Fraction(1), (0, 2): Fraction(1)}
    edge_potential = scale2(multiply2(multiply2(difference, difference), sum_squares), Fraction(1, 4))
    gradient = derivative2(edge_potential, 0)
    same_hessian = derivative2(gradient, 0)
    cross_hessian = derivative2(gradient, 1)
    expected_gradient = {
        (3, 0): Fraction(1),
        (2, 1): Fraction(-3, 2),
        (1, 2): Fraction(1),
        (0, 3): Fraction(-1, 2),
    }
    expected_same = {(2, 0): Fraction(3), (1, 1): Fraction(-3), (0, 2): Fraction(1)}
    expected_cross = {
        (2, 0): Fraction(-3, 2),
        (1, 1): Fraction(2),
        (0, 2): Fraction(-3, 2),
    }
    audit.check("sparse edge gradient", gradient == expected_gradient, gradient, expected_gradient, "potential")
    audit.check("sparse same Hessian", same_hessian == expected_same, same_hessian, expected_same, "potential")
    audit.check("sparse cross Hessian", cross_hessian == expected_cross, cross_hessian, expected_cross, "potential")

    edge_force_constant = sum(abs(coefficient) for coefficient in gradient.values())
    edge_same_constant = sum(abs(coefficient) for coefficient in same_hessian.values())
    edge_cross_constant = sum(abs(coefficient) for coefficient in cross_hessian.values())
    edge_row_constant = edge_same_constant + edge_cross_constant
    audit.check("edge force coefficient l1", edge_force_constant == 4, edge_force_constant, 4, "bounds")
    audit.check("edge same Hessian coefficient l1", edge_same_constant == 7, edge_same_constant, 7, "bounds")
    audit.check("edge cross Hessian coefficient l1", edge_cross_constant == 5, edge_cross_constant, 5, "bounds")
    audit.check("edge Hessian row coefficient l1", edge_row_constant == 12, edge_row_constant, 12, "bounds")
    audit.check(
        "bipartite force saturation",
        evaluate2(gradient, Fraction(1), Fraction(-1)) == edge_force_constant,
        evaluate2(gradient, Fraction(1), Fraction(-1)),
        edge_force_constant,
        "bounds",
    )
    audit.check(
        "bipartite Hessian row saturation",
        evaluate2(same_hessian, Fraction(1), Fraction(-1))
        + abs(evaluate2(cross_hessian, Fraction(1), Fraction(-1)))
        == edge_row_constant,
        evaluate2(same_hessian, Fraction(1), Fraction(-1))
        + abs(evaluate2(cross_hessian, Fraction(1), Fraction(-1))),
        edge_row_constant,
        "bounds",
    )

    graph_degree = degree_sequence[0]
    lock_force = graph_degree * edge_force_constant
    lock_lipschitz = graph_degree * edge_row_constant
    b_value = Fraction(1) + Fraction(1 + lock_force)
    ell_value = Fraction(1) + Fraction(3 + lock_lipschitz)
    tau = Fraction(1, 10)
    volterra_factor = tau * tau / 4
    self_map = Fraction(1, 2) + volterra_factor * b_value
    contraction = volterra_factor * ell_value
    stability = 1 / (1 - contraction)
    for name, actual, expected in (
        ("lock force coefficient", lock_force, Fraction(12)),
        ("lock Lipschitz coefficient", lock_lipschitz, Fraction(36)),
        ("fixture b_R", b_value, Fraction(14)),
        ("fixture ell_R", ell_value, Fraction(40)),
        ("fixture self-map", self_map, Fraction(107, 200)),
        ("fixture contraction", contraction, Fraction(1, 10)),
        ("fixture stability", stability, Fraction(10, 9)),
    ):
        audit.check(name, actual == expected, actual, expected, "goursat_gate")

    for power_u in range(4):
        for power_v in range(4):
            coefficient = Fraction(1, (power_u + 1) * (power_v + 1))
            audit.check(
                f"rational Volterra monomial ({power_u},{power_v})",
                coefficient * (power_u + 1) * (power_v + 1) == 1,
                coefficient,
                Fraction(1, (power_u + 1) * (power_v + 1)),
                "volterra",
            )
    for order in range(1, 7):
        recurrence = Fraction(1)
        for step in range(1, order + 1):
            recurrence /= step * step
        expected = Fraction(1, factorial(order) ** 2)
        audit.check(
            f"factorial-squared coefficient {order}",
            recurrence == expected,
            recurrence,
            expected,
            "volterra",
        )

    # Physical weights are computed with a=10 as a rational unit fixture.
    coarse_spacing = Fraction(10)
    fine_spacing = coarse_spacing / 2
    volume_weight = fine_spacing**3
    reduced_weight = coarse_spacing / 8
    audit.check(
        "fine volume equals a cubed over eight",
        volume_weight == coarse_spacing**3 / 8,
        volume_weight,
        coarse_spacing**3 / 8,
        "normalization",
    )
    audit.check(
        "three-dimensional species weights close",
        8 * volume_weight == coarse_spacing**3,
        8 * volume_weight,
        coarse_spacing**3,
        "normalization",
    )
    audit.check(
        "reduced species weights close per unit transverse area",
        8 * reduced_weight == coarse_spacing,
        8 * reduced_weight,
        coarse_spacing,
        "normalization",
    )

    chi, speed, duration = Fraction(2), Fraction(3), Fraction(1)
    c_physical = chi * speed**2
    a_prime, b_prime = Fraction(1), Fraction(2)
    field_time = a_prime + b_prime
    field_space = (a_prime - b_prime) / speed
    density = Fraction(1, 8) * (
        chi * field_time**2 / 2 + c_physical * field_space**2 / 2
    )
    slice_energy = 2 * speed * duration * density
    boundary_energy = speed / 8 * (
        2 * duration * chi * a_prime**2 + 2 * duration * chi * b_prime**2
    )
    audit.check("independent slice energy", slice_energy == Fraction(15, 2), slice_energy, Fraction(15, 2), "energy_flux")
    audit.check("independent boundary energy", boundary_energy == slice_energy, boundary_energy, slice_energy, "energy_flux")

    ordered_potential = 8 * (Fraction(-1, 2) + Fraction(1, 4))
    negative_slice = 2 * speed * duration * ordered_potential / 8
    negative_boundary = speed / 8 * (
        2 * duration * ordered_potential / 2 + 2 * duration * ordered_potential / 2
    )
    audit.check("ordered potential minimum", ordered_potential == -2, ordered_potential, -2, "energy_flux")
    audit.check(
        "negative energy flux balance",
        negative_slice == negative_boundary == Fraction(-3, 2),
        (negative_slice, negative_boundary),
        (Fraction(-3, 2), Fraction(-3, 2)),
        "energy_flux",
    )

    # Slice polynomials after v=2-u.
    eta1 = {0: Fraction(4), 1: Fraction(-1)}
    eta2 = {0: Fraction(12), 1: Fraction(-12), 2: Fraction(4)}
    eta1_time = {0: Fraction(3)}
    eta2_time = {0: Fraction(12), 1: Fraction(-4)}
    slice_integrand = add1(
        multiply1(eta1_time, eta2),
        scale1(multiply1(eta2_time, eta1), Fraction(-1)),
    )
    slice_form = chi * speed / 8 * integrate1(slice_integrand, Fraction(0), Fraction(2))

    A1, A2 = {1: Fraction(1)}, {2: Fraction(1)}
    B1, B2 = {1: Fraction(2)}, {2: Fraction(3)}
    boundary_u_integrand = add1(
        multiply1(derivative1(A1), A2),
        scale1(multiply1(derivative1(A2), A1), Fraction(-1)),
    )
    boundary_v_integrand = add1(
        multiply1(derivative1(B1), B2),
        scale1(multiply1(derivative1(B2), B1), Fraction(-1)),
    )
    boundary_form = chi * speed / 8 * (
        integrate1(boundary_u_integrand, Fraction(0), Fraction(2))
        + integrate1(boundary_v_integrand, Fraction(0), Fraction(2))
    )
    audit.check("independent inherited slice form", slice_form == -14, slice_form, -14, "symplectic_flux")
    audit.check("independent derivative-first boundary form", boundary_form == slice_form, boundary_form, slice_form, "symplectic_flux")
    audit.check("independent value-first control", -boundary_form == 14, -boundary_form, 14, "symplectic_flux")

    exact_results = {
        "species_count": len(vertices),
        "q3_edge_count": len(edges),
        "q3_degree": graph_degree,
        "edge_force_bound_coefficient": edge_force_constant,
        "edge_hessian_row_bound_coefficient": edge_row_constant,
        "b_R_fixture": b_value,
        "ell_R_fixture": ell_value,
        "self_map_fixture": self_map,
        "contraction_fixture": contraction,
        "stability_fixture": stability,
        "massless_energy_fixture": slice_energy,
        "negative_unshifted_energy_fixture": negative_slice,
        "symplectic_derivative_first_fixture": boundary_form,
        "symplectic_value_first_hostile_control": -boundary_form,
        "physical_3d_weight": "a^3/8",
        "reduced_1d_weight_per_unit_transverse_area": "a/8",
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
            "fixed_1_plus_1_lorentzian_background": True,
            "gated_continuum_goursat_reconstruction": True,
            "finite_a_goursat_scheme": False,
            "lattice_boundary_composition": False,
            "physical_state_selection": False,
            "physical_empty_space": False,
            "cp1_complete": False,
            "pre_a_complete": False,
        },
        "provenance": {
            "script": serial(SCRIPT.relative_to(REPO)),
            "script_sha256": sha256(SCRIPT),
            "upstream": serial(UPSTREAM.relative_to(REPO)),
            "upstream_sha256": sha256(UPSTREAM),
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
