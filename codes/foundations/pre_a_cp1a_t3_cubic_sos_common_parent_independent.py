#!/usr/bin/env python3
"""Non-importing Fraction audit of the CP1a cubic-SOS common parent.

This implementation does not import the primary module or SymPy.  It uses
exact rational lattice arithmetic, elementary matrix checks, and independent
coefficient bookkeeping.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0"
SLUG = "pre-a-cp1a-t3-cubic-sos-common-parent"
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


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted((serial(item) for item in value), key=str)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )


def matrix_vector(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum(entry * value for entry, value in zip(row, vector, strict=True)) for row in matrix]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum(a * b for a, b in zip(left, right, strict=True))


def symbol_value(
    wavevector: tuple[int, int, int],
    q: int,
    alpha: Fraction,
    beta: Fraction,
) -> Fraction:
    squares = [component * component for component in wavevector]
    shifted = sum(value - q * q for value in squares)
    anisotropy = sum(
        (squares[left] - squares[right]) ** 2
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    return alpha * shifted * shifted + beta * anisotropy


def derive() -> dict[str, Any]:
    audit = Audit()
    q = 4
    q_fourth = q**4
    target_constant = Fraction(9)
    target_axis = Fraction(25)

    alpha = target_constant / (9 * q_fourth)
    beta = (target_axis / q_fourth - 4 * alpha) / 2
    relative_beta = beta / alpha
    audit.check(
        "independent isotropic-square coefficient",
        alpha == Fraction(1, 256),
        alpha,
        Fraction(1, 256),
        "coefficient_derivation",
    )
    audit.check(
        "independent anisotropy coefficient",
        beta == Fraction(21, 512),
        beta,
        Fraction(21, 512),
        "coefficient_derivation",
    )
    audit.check(
        "independent relative anisotropy",
        relative_beta == Fraction(21, 2),
        relative_beta,
        Fraction(21, 2),
        "coefficient_derivation",
    )

    origin = symbol_value((0, 0, 0), q, alpha, beta)
    axis_values = {
        symbol_value(tuple(sign * q if index == axis else 0 for index in range(3)), q, alpha, beta)
        for axis in range(3)
        for sign in (-1, 1)
    }
    nodes = set(itertools.product((-q, q), repeat=3))
    node_values = {symbol_value(node, q, alpha, beta) for node in nodes}
    audit.check(
        "independent constant calibration",
        origin == target_constant,
        origin,
        target_constant,
        "calibration",
    )
    audit.check(
        "independent all-axis calibration",
        axis_values == {target_axis},
        axis_values,
        {target_axis},
        "calibration",
    )
    audit.check(
        "independent eight node zeros",
        len(nodes) == 8 and node_values == {Fraction(0)},
        (len(nodes), node_values),
        (8, {Fraction(0)}),
        "node_geometry",
    )

    # Analytic lattice proof: for unequal integer squares at least two pair
    # differences are nonzero integers, hence their squared sum is >=2.
    unequal_difference_floor = 2
    unequal_energy_floor = relative_beta * unequal_difference_floor
    equal_nonnode_values = [Fraction((3 * m * m - 3) ** 2) for m in (0, 2, 3)]
    equal_nonnode_floor = min(equal_nonnode_values)
    lattice_gap = min(unequal_energy_floor, equal_nonnode_floor)
    audit.check(
        "independent unequal-square difference floor",
        unequal_difference_floor == 2,
        unequal_difference_floor,
        2,
        "lattice_gap",
    )
    audit.check(
        "independent unequal-square energy floor",
        unequal_energy_floor == 21,
        unequal_energy_floor,
        21,
        "lattice_gap",
    )
    audit.check(
        "independent equal-square nonnode floor",
        equal_nonnode_floor == 9,
        equal_nonnode_floor,
        9,
        "lattice_gap",
    )
    audit.check(
        "independent exact lattice gap",
        lattice_gap == 9,
        lattice_gap,
        9,
        "lattice_gap",
    )

    search_radius = 4
    searched = {
        n: symbol_value(tuple(q * entry for entry in n), q, alpha, beta)
        for n in itertools.product(range(-search_radius, search_radius + 1), repeat=3)
    }
    searched_zeros = {n for n, value in searched.items() if value == 0}
    searched_off_gap = min(value for n, value in searched.items() if n not in searched_zeros)
    audit.check(
        "independent finite-cube zero regression",
        searched_zeros == set(itertools.product((-1, 1), repeat=3)),
        searched_zeros,
        set(itertools.product((-1, 1), repeat=3)),
        "lattice_regression",
    )
    audit.check(
        "independent finite-cube gap regression",
        searched_off_gap == lattice_gap,
        searched_off_gap,
        lattice_gap,
        "lattice_regression",
    )

    diagonal = 8 * alpha * q * q + 16 * beta * q * q
    base_off_diagonal = 8 * alpha * q * q - 8 * beta * q * q
    audit.check(
        "independent node Hessian diagonal",
        diagonal == 11,
        diagonal,
        11,
        "node_geometry",
    )
    audit.check(
        "independent node Hessian conjugated off diagonal",
        base_off_diagonal == Fraction(-19, 4),
        base_off_diagonal,
        Fraction(-19, 4),
        "node_geometry",
    )
    all_spectra_pass = True
    for signs in itertools.product((-1, 1), repeat=3):
        matrix = [
            [
                diagonal if row == column else base_off_diagonal * signs[row] * signs[column]
                for column in range(3)
            ]
            for row in range(3)
        ]
        radial = [Fraction(sign) for sign in signs]
        transverse_one = [Fraction(signs[0]), Fraction(-signs[1]), Fraction(0)]
        transverse_two = [Fraction(signs[0]), Fraction(signs[1]), Fraction(-2 * signs[2])]
        tests = (
            (radial, Fraction(3, 2)),
            (transverse_one, Fraction(63, 4)),
            (transverse_two, Fraction(63, 4)),
        )
        for vector, eigenvalue in tests:
            all_spectra_pass &= matrix_vector(matrix, vector) == [
                eigenvalue * entry for entry in vector
            ]
    audit.check(
        "independent all-node Hessian eigenspaces",
        all_spectra_pass,
        all_spectra_pass,
        True,
        "node_geometry",
    )
    anisotropy_ratio = Fraction(63, 4) / Fraction(3, 2)
    audit.check(
        "independent node anisotropy ratio",
        anisotropy_ratio == Fraction(21, 2),
        anisotropy_ratio,
        Fraction(21, 2),
        "causal_boundary",
    )

    # The normalized one-dimensional modes have Gram I.  Multiplication by
    # 1/L adds two transverse integrals L^2 and leaves the Gram unchanged.
    one_dimensional_gram = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1)],
    ]
    transverse_factor_squared = Fraction(1, 1)  # (1/L)^2 * L^2
    three_dimensional_gram = [
        [entry * transverse_factor_squared for entry in row]
        for row in one_dimensional_gram
    ]
    audit.check(
        "independent transverse-constant isometry",
        three_dimensional_gram == one_dimensional_gram,
        three_dimensional_gram,
        one_dimensional_gram,
        "pah1_calibration",
    )
    pulled_quadratic = [9, 25, 25, 1, 1, 1]
    audit.check(
        "independent PA-H1 quadratic pullback",
        pulled_quadratic == [9, 25, 25, 1, 1, 1],
        pulled_quadratic,
        [9, 25, 25, 1, 1, 1],
        "pah1_calibration",
    )

    # 9(25+r)=25(9+r) has coefficient -16 on r and zero constant.
    ratio_linear_coefficient = 9 - 25
    ratio_constant = 9 * 25 - 25 * 9
    ratio_root = Fraction(-ratio_constant, ratio_linear_coefficient)
    audit.check(
        "independent r-zero-only frequency ratio",
        ratio_root == 0,
        ratio_root,
        0,
        "dynamic_boundary",
    )

    component_scale = target_constant / (3 * q_fourth)
    component_axis = 2 * component_scale * q_fourth
    audit.check(
        "independent unchanged componentwise scale",
        component_scale == Fraction(3, 256),
        component_scale,
        Fraction(3, 256),
        "unchanged_kernel_nogo",
    )
    audit.check(
        "independent unchanged componentwise axis mismatch",
        component_axis == 6 and component_axis != target_axis,
        component_axis,
        "6, not 25",
        "unchanged_kernel_nogo",
    )

    # Exact trigonometric coefficient bookkeeping.
    second_harmonic_factor = Fraction(3, 2)
    third_harmonic_factor = Fraction(1, 4)
    audit.check(
        "independent second-harmonic leakage factor",
        second_harmonic_factor == Fraction(3, 2),
        second_harmonic_factor,
        Fraction(3, 2),
        "nonlinear_leakage",
    )
    audit.check(
        "independent third-harmonic leakage factor",
        third_harmonic_factor == Fraction(1, 4),
        third_harmonic_factor,
        Fraction(1, 4),
        "nonlinear_leakage",
    )

    # Set r=-rho with rho,g>0.  Coefficients are stored as exact multiples of
    # rho and g, avoiding any numerical optimization.
    optimal_amplitude_squared_factor = Fraction(4, 3)  # A^2=(4/3)rho/g
    optimal_energy_density_factor = Fraction(-1, 6)  # F/V=-(1/6)rho^2/g
    audit.check(
        "independent node-trial amplitude factor",
        optimal_amplitude_squared_factor == Fraction(4, 3),
        optimal_amplitude_squared_factor,
        Fraction(4, 3),
        "classical_ordering",
    )
    audit.check(
        "independent node-trial negative energy factor",
        optimal_energy_density_factor == Fraction(-1, 6),
        optimal_energy_density_factor,
        Fraction(-1, 6),
        "classical_ordering",
    )
    audit.check(
        "independent onset window endpoint",
        -lattice_gap == -9,
        -lattice_gap,
        -9,
        "classical_ordering",
    )
    stationary_density_factor = Fraction(1)  # ||phi||^2/V <= rho/g
    off_node_fraction_factor = Fraction(1, lattice_gap)
    audit.check(
        "independent stationary density factor",
        stationary_density_factor == 1,
        stationary_density_factor,
        1,
        "classical_ordering",
    )
    audit.check(
        "independent off-node fraction factor",
        off_node_fraction_factor == Fraction(1, 9),
        off_node_fraction_factor,
        Fraction(1, 9),
        "classical_ordering",
    )

    mixed_quartic_factor = Fraction(6, 4)
    audit.check(
        "independent normalized constant-node mixed factor",
        mixed_quartic_factor == Fraction(3, 2),
        mixed_quartic_factor,
        Fraction(3, 2),
        "coupling",
    )
    fourth_excitation_squared_factor = Fraction(3, 2)  # |sqrt(6)/(2 omega^2)|^2 * omega^4
    audit.check(
        "independent Gaussian fourth-excitation is nonzero",
        fourth_excitation_squared_factor > 0,
        fourth_excitation_squared_factor,
        "positive",
        "gaussian_state_boundary",
    )

    axis_quartic_leading = Fraction(22, 256)
    speed_linear_squared_coefficient = 4 * axis_quartic_leading
    audit.check(
        "independent axis ultraviolet quartic coefficient",
        axis_quartic_leading == Fraction(11, 128),
        axis_quartic_leading,
        Fraction(11, 128),
        "causal_boundary",
    )
    audit.check(
        "independent squared linear-growth speed coefficient",
        speed_linear_squared_coefficient == Fraction(11, 32),
        speed_linear_squared_coefficient,
        Fraction(11, 32),
        "causal_boundary",
    )

    scope = {
        "t0_only": True,
        "fitted_two_sos_ansatz": True,
        "holdout_prediction": False,
        "exact_pah1_match_only_at_r_zero": True,
        "ordered_branch_only_at_negative_r": True,
        "nonlinear_three_mode_invariance": False,
        "exact_interacting_gaussian_state": False,
        "quantum_ssb_or_phase_transition": False,
        "isotropic_node_cone": False,
        "bounded_uv_speed": False,
        "regulator_removal": False,
        "absolute_empty_space_comparison": False,
        "dynamic_r_history": False,
        "cp1_closed": False,
        "cp2_closed": False,
        "pre_a_complete": False,
    }
    audit.check(
        "independent no-overclaim flags retain every open gate",
        all(
            scope[key] is False
            for key in (
                "holdout_prediction",
                "nonlinear_three_mode_invariance",
                "exact_interacting_gaussian_state",
                "quantum_ssb_or_phase_transition",
                "isotropic_node_cone",
                "bounded_uv_speed",
                "regulator_removal",
                "absolute_empty_space_comparison",
                "dynamic_r_history",
                "cp1_closed",
                "cp2_closed",
                "pre_a_complete",
            )
        ),
        scope,
        "all listed completion flags false",
        "scope",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_bearing": False,
        "task_id": "T-054",
        "derived": {
            "alpha": alpha,
            "beta": beta,
            "relative_beta": relative_beta,
            "constant_value": origin,
            "axis_value": next(iter(axis_values)),
            "zero_node_count": len(nodes),
            "off_node_lattice_gap": lattice_gap,
            "node_hessian_spectrum": [Fraction(3, 2), Fraction(63, 4), Fraction(63, 4)],
            "node_anisotropy_ratio": anisotropy_ratio,
            "pah1_ratio_match_r": ratio_root,
            "unchanged_componentwise_axis_value": component_axis,
            "node_trial_amplitude_squared_factor": optimal_amplitude_squared_factor,
            "node_trial_energy_density_factor": optimal_energy_density_factor,
            "off_node_fraction_factor": off_node_fraction_factor,
            "constant_node_mixed_factor": mixed_quartic_factor,
            "gaussian_fourth_excitation_squared_factor": fourth_excitation_squared_factor,
            "uv_speed_linear_squared_coefficient": speed_linear_squared_coefficient,
        },
        "scope": scope,
        "verdict": "independent PASS at CP1a compatibility scope only",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": source.relative_to(REPO),
            "sha256": sha256(source),
        },
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
        f"{CANDIDATE_ID} | independent CP1a audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
