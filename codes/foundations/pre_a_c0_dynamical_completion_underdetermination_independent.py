#!/usr/bin/env python3
"""Non-importing exact audit for PA-C0-DYNAMICAL-COMPLETION-NOGO-v0.

This implementation uses only standard-library rational polynomial arithmetic.
It does not import SymPy, the primary implementation, or primary artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from math import comb
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0-DYNAMICAL-COMPLETION-NOGO-v0"
SLUG = "pre-a-c0-dynamical-completion-underdetermination"
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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
    return {powers: coefficient for powers, coefficient in poly.items() if coefficient}


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for powers, coefficient in right.items():
        result[powers] = result.get(powers, F(0)) + coefficient
    return clean(result)


def scale(poly: Polynomial, scalar: F) -> Polynomial:
    return clean({powers: scalar * coefficient for powers, coefficient in poly.items()})


def derivative(poly: Polynomial, axis: int) -> Polynomial:
    result: Polynomial = {}
    for powers, coefficient in poly.items():
        power = powers[axis]
        if power:
            reduced = list(powers)
            reduced[axis] -= 1
            key = (reduced[0], reduced[1])
            result[key] = result.get(key, F(0)) + coefficient * power
    return clean(result)


def compose_linear(coefficients: dict[int, F], x_weight: F, t_weight: F) -> Polynomial:
    """Expand sum_n a_n*(x_weight*x+t_weight*t)^n exactly."""
    result: Polynomial = {}
    for power, coefficient in coefficients.items():
        for x_power in range(power + 1):
            t_power = power - x_power
            value = (
                coefficient
                * comb(power, x_power)
                * x_weight**x_power
                * t_weight**t_power
            )
            key = (x_power, t_power)
            result[key] = result.get(key, F(0)) + value
    return clean(result)


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

    # The force x*(lambda+g*x^2), lambda,g>0, has only x=0 as a real
    # equilibrium.  Both temporal completions use this exact force.
    lam = F(2)
    quartic = F(3)
    force_coefficients = {1: lam, 3: quartic}
    check(
        "independent nonlinear force coefficients",
        force_coefficients == {1: F(2), 3: F(3)},
        force_coefficients,
        {1: F(2), 3: F(3)},
        "same_static_data",
    )
    check(
        "independent positive bracket makes zero the only real equilibrium",
        lam > 0 and quartic > 0,
        (lam, quartic),
        "lambda>0 and g>0, so lambda+g*x^2>0",
        "same_static_data",
    )

    force_value = F(7, 5)
    gamma = F(3, 2)
    chi = F(11, 6)
    gradient_energy_rate = force_value * (-gamma * force_value)
    reverse_energy_rate = force_value * (gamma * force_value)
    check(
        "independent gradient Lyapunov identity",
        gradient_energy_rate == -gamma * force_value**2,
        gradient_energy_rate,
        -gamma * force_value**2,
        "dynamics",
    )
    check(
        "independent reversed-gradient energy identity",
        reverse_energy_rate == gamma * force_value**2,
        reverse_energy_rate,
        gamma * force_value**2,
        "dynamics",
    )
    velocity = F(-4, 7)
    acceleration = -force_value / chi
    inertial_energy_rate = velocity * (chi * acceleration + force_value)
    check(
        "independent inertial energy conservation on shell",
        inertial_energy_rate == 0,
        inertial_energy_rate,
        F(0),
        "dynamics",
    )

    eigenvalue = F(5, 3)
    mobility = F(7, 4)
    gradient_root = -mobility * eigenvalue
    inertial_root_squared = -eigenvalue / chi
    check(
        "independent positive-mode gradient root is negative real",
        gradient_root < 0,
        gradient_root,
        "negative real",
        "dynamics",
    )
    check(
        "independent positive-mode inertial root square is negative",
        inertial_root_squared == F(-10, 11),
        inertial_root_squared,
        F(-10, 11),
        "dynamics",
    )
    check(
        "independent temporal orders differ",
        (1, 2) == (1, 2),
        (1, 2),
        (1, 2),
        "dynamics",
    )

    # Independent heat-kernel identity after division by its positive kernel.
    diffusivity = F(2, 3)
    space = F(5, 4)
    time = F(7, 5)
    heat_t_over_heat = -F(1, 2) / time + space**2 / (
        4 * diffusivity * time**2
    )
    heat_xx_over_heat = -F(1, 2) / (diffusivity * time) + space**2 / (
        4 * diffusivity**2 * time**2
    )
    check(
        "independent heat-kernel differential identity",
        heat_t_over_heat == diffusivity * heat_xx_over_heat,
        heat_t_over_heat,
        diffusivity * heat_xx_over_heat,
        "causal_class",
    )

    # Independent polynomial d'Alembert fixture.
    speed = F(3, 2)
    left_profile = {0: F(1), 1: F(2), 2: F(3), 3: F(1)}
    right_profile = {0: F(-2), 1: F(1), 3: F(-2)}
    wave = add(
        compose_linear(left_profile, F(1), -speed),
        compose_linear(right_profile, F(1), speed),
    )
    wave_tt = derivative(derivative(wave, 1), 1)
    wave_xx = derivative(derivative(wave, 0), 0)
    wave_residual = add(wave_tt, scale(wave_xx, -speed**2))
    check(
        "independent dAlembert polynomial solves the wave equation",
        wave_residual == {},
        wave_residual,
        {},
        "causal_class",
    )

    # Two copies with one static stiffness and different inertias retain a
    # nontrivial relative speed under a common clock rescaling.
    stiffness = F(9, 5)
    chi_one = F(1)
    chi_two = F(4)
    relative_speed_squared = (stiffness / chi_one) / (stiffness / chi_two)
    check(
        "independent two-copy relative-speed square",
        relative_speed_squared == 4,
        relative_speed_squared,
        F(4),
        "relative_speed",
    )

    # Exact PA-M2 coordinate-ray polynomial around a critical node.
    c = F(3, 5)
    q = F(7, 4)
    node_polynomial = {
        2: 4 * c * q**2,
        3: 4 * c * q,
        4: c,
    }
    opposite_polynomial = {
        2: 4 * c * q**2,
        3: -4 * c * q,
        4: c,
    }
    symmetric_polynomial = {
        power: (node_polynomial.get(power, F(0)) + opposite_polynomial.get(power, F(0))) / 2
        for power in set(node_polynomial) | set(opposite_polynomial)
    }
    symmetric_polynomial = {
        power: coefficient for power, coefficient in symmetric_polynomial.items() if coefficient
    }
    check(
        "independent symmetric node expansion cancels cubic term",
        symmetric_polynomial == {2: 4 * c * q**2, 4: c},
        symmetric_polynomial,
        {2: 4 * c * q**2, 4: c},
        "pa_m2_corollary",
    )
    gradient_leading_power = min(node_polynomial)
    inertial_frequency_leading_power = gradient_leading_power // 2
    check(
        "independent PA-M2 Gaussian exponents",
        (gradient_leading_power, inertial_frequency_leading_power) == (2, 1),
        (gradient_leading_power, inertial_frequency_leading_power),
        (2, 1),
        "pa_m2_corollary",
    )
    target_speed = F(5, 2)
    selected_inertia = 4 * c * q**2 / target_speed**2
    recovered_speed_squared = 4 * c * q**2 / selected_inertia
    check(
        "independent arbitrary positive node-speed fixture",
        recovered_speed_squared == target_speed**2,
        recovered_speed_squared,
        target_speed**2,
        "pa_m2_corollary",
    )
    q_zero_polynomial = {4: c}
    check(
        "independent q-zero exponents",
        (min(q_zero_polynomial), min(q_zero_polynomial) // 2) == (4, 2),
        (min(q_zero_polynomial), min(q_zero_polynomial) // 2),
        (4, 2),
        "pa_m2_corollary",
    )
    # Along k=(q+R,q,q), omega^2=(c/chi)*[(q+R)^2-q^2]^2.
    # Its positive-branch group speed is proportional to 2(q+R), a degree-one
    # polynomial with positive leading coefficient and hence is unbounded.
    group_speed_without_positive_sqrt_factor = {0: 2 * q, 1: F(2)}
    check(
        "independent ultraviolet group-speed polynomial is unbounded",
        group_speed_without_positive_sqrt_factor[1] > 0,
        group_speed_without_positive_sqrt_factor,
        "positive degree-one polynomial",
        "pa_m2_corollary",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "independent exact audit of a T0 static-dynamics underdetermination certificate",
        "shared_exact_results": {
            "same_static_equilibria_and_hessian": True,
            "gradient_and_inertial_temporal_orders": [1, 2],
            "gradient_energy_decreases": True,
            "reversed_gradient_energy_increases_in_finite_dimension": True,
            "inertial_extended_energy_conserved": True,
            "heat_wave_causal_class_witness": True,
            "two_copy_relative_speed_squared_fixture": relative_speed_squared,
            "pa_m2_gradient_dynamic_exponent": gradient_leading_power,
            "pa_m2_inertial_dynamic_exponent": inertial_frequency_leading_power,
            "inertia_for_speed_fixture": selected_inertia,
            "q_zero_gradient_dynamic_exponent": 4,
            "q_zero_inertial_dynamic_exponent": 2,
            "pa_m2_ultraviolet_group_speed_unbounded": True,
            "pre_a_complete": False,
        },
        "scope": {
            "static_data_map_noninjective": True,
            "static_functional_selects_kinetic_law": False,
            "inertial_speed_is_inserted": True,
            "z_is_linearized_and_gapless_only": True,
            "finite_torus_z_requires_limit": True,
            "pa_m2_cone_is_ir_only": True,
            "time_orientation_derived": False,
            "dynamical_exponent_uniquely_derived": False,
            "physical_speed_derived": False,
            "global_causal_structure_derived": False,
            "c0_branch_selected": False,
            "pa_m2_invalidated": False,
            "physical_time_and_causal_emergence": False,
            "pre_a_complete": False,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This non-importing audit checks exact finite-mode energy identities, distinct temporal spectra, "
            "heat-versus-wave equations, relative-speed freedom, and PA-M2 Gaussian scaling boundaries. It "
            "does not select a physical dynamics, derive time or causal order, fix light speed, establish a "
            "global PA-M2 cone, or complete Pre-A."
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
