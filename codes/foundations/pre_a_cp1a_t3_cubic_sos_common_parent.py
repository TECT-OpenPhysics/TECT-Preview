#!/usr/bin/env python3
"""Exact primary audit for the CP1a cubic-SOS common-parent benchmark.

This is a T0 finite-regulator compatibility certificate.  It constructs one
real-scalar T^3 Hamiltonian family whose r=0 quadratic three-mode restriction
matches the PA-H1 frequency fixture and whose r<0 classical branch has an
eight-node finite-wavevector instability.  It does not select a physical
theory, close CP1, or provide a causal ultraviolet completion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1A-T3-CUBIC-SOS-COMMON-PARENT-v0"
SLUG = "pre-a-cp1a-t3-cubic-sos-common-parent"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [
            [serial(value[row, column]) for column in range(value.cols)]
            for row in range(value.rows)
        ]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
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
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical_symplectic(dimension: int) -> sp.Matrix:
    identity = sp.eye(dimension)
    zero = sp.zeros(dimension)
    return zero.row_join(identity).col_join((-identity).row_join(zero))


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


def derive() -> dict[str, Any]:
    audit = Audit()

    # Inserted calibration data, not predictions.
    q = sp.Integer(4)
    target_constant_squared = sp.Integer(9)
    target_axis_squared = sp.Integer(25)
    side_length = 2 * sp.pi / q
    alpha, beta = sp.symbols("alpha beta", real=True)
    calibration_solution = sp.solve(
        (
            sp.Eq(9 * alpha * q**4, target_constant_squared),
            sp.Eq(4 * alpha * q**4 + 2 * beta * q**4, target_axis_squared),
        ),
        (alpha, beta),
        dict=True,
    )
    audit.check(
        "two-SOS calibration has one solution",
        len(calibration_solution) == 1,
        len(calibration_solution),
        1,
        "coefficient_derivation",
    )
    alpha_value = sp.factor(calibration_solution[0][alpha])
    beta_value = sp.factor(calibration_solution[0][beta])
    relative_beta = sp.factor(beta_value / alpha_value)
    audit.check(
        "derived isotropic-square coefficient",
        alpha_value == sp.Rational(1, 256),
        alpha_value,
        sp.Rational(1, 256),
        "coefficient_derivation",
    )
    audit.check(
        "derived cubic-anisotropy coefficient",
        beta_value == sp.Rational(21, 512),
        beta_value,
        sp.Rational(21, 512),
        "coefficient_derivation",
    )
    audit.check(
        "derived relative anisotropy coefficient",
        relative_beta == sp.Rational(21, 2),
        relative_beta,
        sp.Rational(21, 2),
        "coefficient_derivation",
    )
    audit.check(
        "common torus side",
        side_length == sp.pi / 2,
        side_length,
        sp.pi / 2,
        "normalization",
    )

    k1, k2, k3 = sp.symbols("k1 k2 k3", real=True)
    wavevector = (k1, k2, k3)
    shifted_sum = sum(component**2 - q**2 for component in wavevector)
    anisotropy_sum = sum(
        (wavevector[left] ** 2 - wavevector[right] ** 2) ** 2
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    symbol = sp.factor(alpha_value * shifted_sum**2 + beta_value * anisotropy_sum)
    expanded_symbol = sp.expand(symbol)
    expected_expansion = sp.Rational(1, 256) * (
        22 * sum(component**4 for component in wavevector)
        - 19
        * sum(
            wavevector[left] ** 2 * wavevector[right] ** 2
            for left, right in ((0, 1), (0, 2), (1, 2))
        )
        - 96 * sum(component**2 for component in wavevector)
        + 2304
    )
    audit.check(
        "expanded local fourth-order symbol",
        sp.expand(expanded_symbol - expected_expansion) == 0,
        expanded_symbol,
        expected_expansion,
        "kernel",
    )
    audit.check(
        "symbol is a positive sum of squares",
        alpha_value > 0 and beta_value > 0,
        (alpha_value, beta_value),
        "both positive",
        "kernel",
    )

    origin_value = sp.simplify(symbol.subs({k1: 0, k2: 0, k3: 0}))
    axis_value = sp.simplify(symbol.subs({k1: q, k2: 0, k3: 0}))
    node_value = sp.simplify(symbol.subs({k1: q, k2: q, k3: q}))
    audit.check(
        "constant-mode squared frequency",
        origin_value == target_constant_squared,
        origin_value,
        target_constant_squared,
        "calibration",
    )
    audit.check(
        "first-axis squared frequency",
        axis_value == target_axis_squared,
        axis_value,
        target_axis_squared,
        "calibration",
    )
    audit.check(
        "CI8 node is soft at r zero",
        node_value == 0,
        node_value,
        0,
        "node_geometry",
    )

    n1, n2, n3 = sp.symbols("n1 n2 n3", integer=True)
    lattice_formula = sp.factor(
        symbol.subs({k1: q * n1, k2: q * n2, k3: q * n3})
    )
    expected_lattice_formula = (
        n1**2 + n2**2 + n3**2 - 3
    ) ** 2 + sp.Rational(21, 2) * (
        (n1**2 - n2**2) ** 2
        + (n1**2 - n3**2) ** 2
        + (n2**2 - n3**2) ** 2
    )
    audit.check(
        "exact integer-lattice normal form",
        sp.expand(lattice_formula - expected_lattice_formula) == 0,
        lattice_formula,
        expected_lattice_formula,
        "lattice_gap",
    )
    unequal_square_penalty = 2 * sp.Rational(21, 2)
    equal_nonnode_minimum = (3 * 0**2 - 3) ** 2
    lattice_gap = min(unequal_square_penalty, equal_nonnode_minimum)
    audit.check(
        "unequal integer-square triples cost at least twenty one",
        unequal_square_penalty == 21,
        unequal_square_penalty,
        21,
        "lattice_gap",
    )
    audit.check(
        "equal-square nonnode branch is minimized at the origin",
        equal_nonnode_minimum == 9,
        equal_nonnode_minimum,
        9,
        "lattice_gap",
    )
    audit.check(
        "exact off-node lattice gap",
        lattice_gap == 9,
        lattice_gap,
        9,
        "lattice_gap",
    )

    hessian = sp.hessian(symbol, wavevector)
    node_hessian = sp.simplify(hessian.subs({k1: q, k2: q, k3: q}))
    expected_node_hessian = sp.Matrix(
        [
            [11, sp.Rational(-19, 4), sp.Rational(-19, 4)],
            [sp.Rational(-19, 4), 11, sp.Rational(-19, 4)],
            [sp.Rational(-19, 4), sp.Rational(-19, 4), 11],
        ]
    )
    audit.check(
        "node Hessian matrix",
        node_hessian == expected_node_hessian,
        node_hessian,
        expected_node_hessian,
        "node_geometry",
    )
    hessian_eigenvalues = sorted(
        [value for value, multiplicity in node_hessian.eigenvals().items() for _ in range(multiplicity)],
        key=lambda value: float(value),
    )
    audit.check(
        "node Hessian spectrum",
        hessian_eigenvalues
        == [sp.Rational(3, 2), sp.Rational(63, 4), sp.Rational(63, 4)],
        hessian_eigenvalues,
        [sp.Rational(3, 2), sp.Rational(63, 4), sp.Rational(63, 4)],
        "node_geometry",
    )
    node_anisotropy_ratio = sp.factor(hessian_eigenvalues[-1] / hessian_eigenvalues[0])
    audit.check(
        "node cone squared-speed anisotropy ratio",
        node_anisotropy_ratio == sp.Rational(21, 2),
        node_anisotropy_ratio,
        sp.Rational(21, 2),
        "causal_boundary",
    )

    # Exact normalized embedding of the 1D PA-H1 spatial fixture into T^3.
    x, y, z = sp.symbols("x y z", real=True)
    basis_3d = (
        side_length ** sp.Rational(-3, 2),
        sp.sqrt(2) * side_length ** sp.Rational(-3, 2) * sp.cos(q * x),
        sp.sqrt(2) * side_length ** sp.Rational(-3, 2) * sp.sin(q * x),
    )
    gram = sp.Matrix(
        [
            [
                sp.simplify(
                    sp.integrate(
                        left * right,
                        (x, 0, side_length),
                        (y, 0, side_length),
                        (z, 0, side_length),
                    )
                )
                for right in basis_3d
            ]
            for left in basis_3d
        ]
    )
    audit.check(
        "transverse-constant T1-to-T3 inclusion is isometric",
        gram == sp.eye(3),
        gram,
        sp.eye(3),
        "pah1_calibration",
    )
    pah1_squared = sp.diag(origin_value, axis_value, axis_value)
    parent_quadratic_pullback = sp.diag(pah1_squared, sp.eye(3))
    expected_pah1_quadratic = sp.diag(9, 25, 25, 1, 1, 1)
    audit.check(
        "r-zero quadratic Hamiltonian pullback",
        parent_quadratic_pullback == expected_pah1_quadratic,
        parent_quadratic_pullback,
        expected_pah1_quadratic,
        "pah1_calibration",
    )
    sigma_three = canonical_symplectic(3)
    phase_inclusion = sp.eye(6)
    audit.check(
        "quadratic calibration phase inclusion is symplectic",
        phase_inclusion.T * sigma_three * phase_inclusion == sigma_three,
        phase_inclusion.T * sigma_three * phase_inclusion,
        sigma_three,
        "pah1_calibration",
    )

    r = sp.symbols("r", real=True)
    ratio_equation = sp.factor(
        9 * (target_axis_squared + r) - 25 * (target_constant_squared + r)
    )
    ratio_solutions = sp.solve(sp.Eq(ratio_equation, 0), r)
    audit.check(
        "PA-H1 frequency ratio is restored only at r zero",
        ratio_solutions == [0],
        ratio_solutions,
        [0],
        "dynamic_boundary",
    )

    # The unchanged componentwise PA-M2 kernel cannot meet both calibrations.
    component_scale = sp.solve(
        sp.Eq(3 * sp.Symbol("c") * q**4, target_constant_squared),
        sp.Symbol("c"),
    )[0]
    component_axis_value = sp.factor(2 * component_scale * q**4)
    audit.check(
        "unchanged componentwise kernel normalization",
        component_scale == sp.Rational(3, 256),
        component_scale,
        sp.Rational(3, 256),
        "unchanged_kernel_nogo",
    )
    audit.check(
        "unchanged componentwise kernel misses PA-H1 axis value",
        component_axis_value == 6 and component_axis_value != target_axis_squared,
        component_axis_value,
        "6, not 25",
        "unchanged_kernel_nogo",
    )

    amplitude_constant, amplitude_wave = sp.symbols("a b", real=True)
    field_cube = sp.expand_trig(
        (amplitude_constant + amplitude_wave * sp.cos(q * x)) ** 3
    ).expand()
    cos_two_coefficient = sp.Rational(3, 2) * amplitude_constant * amplitude_wave**2
    cos_three_coefficient = sp.Rational(1, 4) * amplitude_wave**3
    reconstructed_cube = (
        amplitude_constant**3
        + sp.Rational(3, 2) * amplitude_constant * amplitude_wave**2
        + (3 * amplitude_constant**2 * amplitude_wave + sp.Rational(3, 4) * amplitude_wave**3)
        * sp.cos(q * x)
        + cos_two_coefficient * sp.cos(2 * q * x)
        + cos_three_coefficient * sp.cos(3 * q * x)
    )
    audit.check(
        "local cubic harmonic decomposition",
        sp.expand_trig(field_cube - reconstructed_cube).expand().rewrite(sp.exp).simplify() == 0,
        reconstructed_cube,
        field_cube,
        "nonlinear_leakage",
    )
    audit.check(
        "constant-wave mixing leaks to the second harmonic",
        cos_two_coefficient != 0,
        cos_two_coefficient,
        "nonzero for a*b != 0",
        "nonlinear_leakage",
    )
    audit.check(
        "a pure first harmonic leaks to the third harmonic",
        cos_three_coefficient != 0,
        cos_three_coefficient,
        "nonzero for b != 0",
        "nonlinear_leakage",
    )

    # Exact classical finite-regulator ordering inequalities.
    g, amplitude, volume = sp.symbols("g A V", positive=True)
    trial_density = r * amplitude**2 / 4 + 3 * g * amplitude**4 / 32
    optimal_amplitude_squared = -4 * r / (3 * g)
    optimal_trial_density = sp.factor(
        trial_density.subs(amplitude**2, optimal_amplitude_squared)
    )
    audit.check(
        "node-stripe optimal amplitude squared",
        sp.solve(sp.Eq(sp.diff(trial_density, amplitude) / amplitude, 0), amplitude**2)
        == [optimal_amplitude_squared],
        optimal_amplitude_squared,
        -4 * r / (3 * g),
        "classical_ordering",
    )
    audit.check(
        "node-stripe energy density",
        optimal_trial_density == -r**2 / (6 * g),
        optimal_trial_density,
        -r**2 / (6 * g),
        "classical_ordering",
    )
    constant_quadratic_coefficient = sp.factor((origin_value + r) / 2)
    audit.check(
        "homogeneous quadratic coefficient is nonnegative in the onset window",
        constant_quadratic_coefficient.subs(r, -lattice_gap) == 0,
        constant_quadratic_coefficient,
        "nonnegative for -9 <= r < 0",
        "classical_ordering",
    )
    stationary_norm_cap = -r / g
    off_node_fraction_cap = -r / lattice_gap
    audit.check(
        "stationary mean-square density cap",
        stationary_norm_cap == -r / g,
        stationary_norm_cap,
        "|r|/g for r<0",
        "classical_ordering",
    )
    audit.check(
        "stationary off-node fraction cap",
        off_node_fraction_cap == -r / 9,
        off_node_fraction_cap,
        "|r|/9 for r<0",
        "classical_ordering",
    )

    normalized_overlap = sp.simplify(1 / volume)
    mixed_quartic_coefficient = sp.factor(sp.Rational(6, 4) * g * normalized_overlap)
    audit.check(
        "normalized constant-node quartic overlap",
        normalized_overlap == 1 / volume,
        normalized_overlap,
        1 / volume,
        "coupling",
    )
    audit.check(
        "nonzero constant-node quartic coupling",
        mixed_quartic_coefficient == 3 * g / (2 * volume),
        mixed_quartic_coefficient,
        3 * g / (2 * volume),
        "coupling",
    )

    omega = sp.symbols("omega", positive=True)
    fourth_hermite_coefficient = sp.sqrt(6) / (2 * omega**2)
    quartic_fourth_excitation = sp.factor(
        g * sp.Symbol("I4", positive=True) * fourth_hermite_coefficient / 4
    )
    audit.check(
        "x-four vacuum fourth-excitation coefficient",
        fourth_hermite_coefficient == 2 * sp.sqrt(6) / (4 * omega**2),
        fourth_hermite_coefficient,
        2 * sp.sqrt(6) / (4 * omega**2),
        "gaussian_state_boundary",
    )
    audit.check(
        "positive local quartic obstructs an exact free Gaussian eigenstate",
        quartic_fourth_excitation != 0,
        quartic_fourth_excitation,
        "nonzero for g,I4,omega > 0",
        "gaussian_state_boundary",
    )

    radial_expectation = sp.symbols("R2", positive=True)
    variational_shift = sp.factor(r * radial_expectation / 2)
    audit.check(
        "common-reference ground-energy variational shift",
        variational_shift.subs(r, -1) < 0,
        variational_shift,
        "negative for r<0",
        "energy_ledger",
    )

    ultraviolet_wave_number = sp.symbols("K", positive=True)
    axis_symbol = sp.factor(
        symbol.subs({k1: ultraviolet_wave_number, k2: 0, k3: 0})
    )
    ultraviolet_frequency = sp.sqrt(axis_symbol)
    frequency_quadratic_coefficient = sp.limit(
        ultraviolet_frequency / ultraviolet_wave_number**2,
        ultraviolet_wave_number,
        sp.oo,
    )
    speed_linear_coefficient = sp.limit(
        sp.diff(ultraviolet_frequency, ultraviolet_wave_number)
        / ultraviolet_wave_number,
        ultraviolet_wave_number,
        sp.oo,
    )
    audit.check(
        "axis ultraviolet frequency is quadratic",
        frequency_quadratic_coefficient == sp.sqrt(22) / 16,
        frequency_quadratic_coefficient,
        sp.sqrt(22) / 16,
        "causal_boundary",
    )
    audit.check(
        "axis ultraviolet group speed is unbounded",
        speed_linear_coefficient == sp.sqrt(22) / 8,
        speed_linear_coefficient,
        sp.sqrt(22) / 8,
        "causal_boundary",
    )

    source = Path(__file__).resolve()
    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 CP1a kinematic/static common-parent compatibility certificate; not full CP1, a TECT action, claim-tier change, or physical selection",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "inputs": {
            "field": "one real scalar field on the periodic T3 torus",
            "side_length": side_length,
            "fourier_lattice": "k=4n, n in Z^3",
            "hbar": 1,
            "inertia": 1,
            "target_squared_frequencies": [target_constant_squared, target_axis_squared],
            "positive_quartic_coupling": True,
        },
        "kernel": {
            "form": "alpha*(sum_i(k_i^2-16))^2 + beta*sum_(i<j)(k_i^2-k_j^2)^2",
            "alpha": alpha_value,
            "beta": beta_value,
            "relative_beta": relative_beta,
            "expanded": expanded_symbol,
            "lattice_normal_form": lattice_formula,
            "zero_nodes": "exactly k=(+/-4,+/-4,+/-4)",
            "off_node_lattice_gap": lattice_gap,
            "node_hessian": node_hessian,
            "node_hessian_eigenvalues": hessian_eigenvalues,
            "node_anisotropy_ratio": node_anisotropy_ratio,
        },
        "exact_results": {
            "pah1_quadratic_calibration": "at r=0 only, span{1,cos(4x1),sin(4x1)} has frequencies 3,5,5",
            "pah1_frequency_ratio_match_values": ratio_solutions,
            "unchanged_componentwise_kernel_axis_value_after_constant_calibration": component_axis_value,
            "classical_ordering_window": "-9 <= r < 0",
            "node_trial_amplitude_squared": optimal_amplitude_squared,
            "node_trial_energy_density": optimal_trial_density,
            "stationary_mean_square_density_cap": stationary_norm_cap,
            "stationary_off_node_fraction_cap": off_node_fraction_cap,
            "constant_node_quartic_mixed_coefficient": mixed_quartic_coefficient,
            "gaussian_fourth_excitation_coefficient": quartic_fourth_excitation,
            "common_reference_rule": "C_N=E_N(0); compare E_N(r)-E_N(0) within the same cutoff, volume, boundary, hbar, and Hamiltonian family",
            "negative_r_ground_energy_comparison": "E_N(r)<E_N(0) for r<0 by the r=0 ground-state variational trial",
            "ultraviolet_speed": "unbounded; d omega(K,0,0)/dK ~ sqrt(22) K/8",
        },
        "standard_theorem_dependencies": {
            "finite_regulator_ground_state": "a real confining finite-dimensional Schrodinger operator has compact resolvent and a unique strictly positive ground state",
            "coercivity": "the positive quartic L4 term is coercive on every finite Fourier space by finite-dimensional norm equivalence",
            "state_restriction": "the selected interacting ground state restricts to the PA-H1 calibration Weyl subalgebra, but the restriction is not the old pure Gaussian fixture",
        },
        "hostile_controls": {
            "coefficients_are_fitted_to_two_calibrations": True,
            "uniqueness_only_inside_two_sos_family": True,
            "no_holdout_prediction": True,
            "full_transverse_constant_kg_dispersion": False,
            "exact_pah1_match_away_from_r_zero": False,
            "pah1_three_mode_nonlinear_invariance_under_removal": False,
            "full_gaussian_mehler_vacuum_at_criticality": False,
            "exact_pure_pah1_gaussian_marginal_of_interacting_ground_state": False,
            "finite_volume_quantum_symmetry_breaking": False,
            "isotropic_node_cone": False,
            "bounded_uv_group_speed": False,
            "absolute_empty_space_comparison": False,
            "counterterm_removal": False,
            "dynamic_r_history": False,
            "total_work_ledger_across_r": False,
            "full_cp1_closed": False,
            "cp2_closed": False,
            "pre_a_complete": False,
        },
        "verdict": "ADVANCE only as a CP1a structural compatibility benchmark; require CP2 dynamics and treat the anisotropic unbounded-speed symbol as an early T-053 physical-selection liability",
        "next_gate": "CP1b/CP2: derive a nonstationary r(tau) crossing with total work accounting, then test or replace the anisotropic fourth-order ultraviolet symbol under preregistered T-053 criteria",
        "no_overclaim": (
            "This certificate constructs one fitted finite-regulator T3 Hamiltonian family and proves its exact r=0 quadratic PA-H1 calibration, r<0 classical finite-wavevector ordering window, shared relative-energy convention, and stated obstructions. It does not derive the old pure Gaussian PA-H1 state from the interacting parent, provide one fixed-r ordered calibration state, prove nonlinear subspace invariance, quantum symmetry breaking, a thermodynamic phase transition, regulator or counterterm removal, an isotropic or causal cone, bounded ultraviolet propagation, a physical vacuum, energy below empty space, cosmic cooling, spacetime, gravity, CP1, CP2, Pre-A, or Sector A."
        ),
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
    return payload


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
        f"{CANDIDATE_ID} | CP1a compatibility only"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
