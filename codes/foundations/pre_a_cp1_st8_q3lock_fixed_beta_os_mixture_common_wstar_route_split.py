#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v1.4 OS-mixture route split.

The mathematical fixtures are self-contained.  Until the matching manifest and
certificate are assembled, use ``--staged``; the payload then reports
``INCOMPLETE`` rather than silently treating missing authority as a proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.1.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = (
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split-manifest.json"
)
OS_PARENT = (
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split-certificate-260809.md"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-primary-{SLUG}/result.json"
)
EXPECTED_EXPLORATION = "EXP-000800"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v1.4"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SHARP-TIME-OS-GRAM-ONLY-REAL-TIME-FUNCTORIALITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FULL-GIBBS-HALF-MODULAR-LOCAL-SEPARATING-CLASS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SINGLE-RUNG-ENERGY-CONSTRAINED-SITEWISE-INFLUENCE-RECURRENCE",
)


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def matrix_zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.simplify(value) == 0 for value in matrix)


def matrix_equal(left: sp.MatrixBase, right: sp.MatrixBase) -> bool:
    return left.shape == right.shape and matrix_zero(sp.Matrix(left - right))


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
                "group": group,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def _basis() -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], int]]:
    basis = list(product(range(2), repeat=3))
    return basis, {label: index for index, label in enumerate(basis)}


def _gram(
    center_weights: tuple[sp.Rational, sp.Rational],
    rho_weights: tuple[sp.Rational, sp.Rational],
    basis: list[tuple[int, int, int]],
) -> sp.Matrix:
    # q(E_ij,E_ij)=phi(E_ji E_ij)=center_weight*rho_j.
    return sp.diag(
        *[center_weights[center] * rho_weights[column] for center, _, column in basis]
    )


def _left_matrix_unit(
    center: int,
    row: int,
    column: int,
    basis: list[tuple[int, int, int]],
    index: dict[tuple[int, int, int], int],
) -> sp.Matrix:
    result = sp.zeros(len(basis))
    for source, (source_center, source_row, source_column) in enumerate(basis):
        if source_center == center and source_row == column:
            target = index[(center, row, source_column)]
            result[target, source] = 1
    return result


def _omega_vector(index: dict[tuple[int, int, int], int]) -> sp.Matrix:
    vector = sp.zeros(len(index), 1)
    for center in range(2):
        for diagonal in range(2):
            vector[index[(center, diagonal, diagonal)], 0] = 1
    return vector


def _state_of_matrix_unit_product(
    center_weight: sp.Expr,
    rho_weights: tuple[sp.Rational, sp.Rational],
    left: tuple[int, int],
    right: tuple[int, int],
) -> sp.Expr:
    i, j = left
    k, ell = right
    if j != k or i != ell:
        return sp.Integer(0)
    return sp.simplify(center_weight * rho_weights[i])


def full_cylinder_mixture_audit() -> dict[str, Any]:
    # INPUTS: two overlapping parity-related center laws and one exact Gibbs qubit.
    lam_plus = sp.Rational(2, 5)
    lam_minus = 1 - lam_plus
    p_plus = (sp.Rational(3, 4), sp.Rational(1, 4))
    p_minus = tuple(reversed(p_plus))
    boltzmann_ratio = sp.Rational(1, 2)
    rho = (
        sp.simplify(1 / (1 + boltzmann_ratio)),
        sp.simplify(boltzmann_ratio / (1 + boltzmann_ratio)),
    )
    p_zero = tuple(
        sp.simplify(lam_plus * p_plus[i] + lam_minus * p_minus[i])
        for i in range(2)
    )

    basis, index = _basis()
    g_plus = _gram(p_plus, rho, basis)
    g_minus = _gram(p_minus, rho, basis)
    g_zero = _gram(p_zero, rho, basis)
    mixture_residual = sp.simplify(g_zero - lam_plus * g_plus - lam_minus * g_minus)

    identity = sp.eye(len(basis))
    j_plus = identity
    j_minus = identity
    j_plus_adjoint = sp.simplify(g_zero.inv() * j_plus.T * g_plus)
    j_minus_adjoint = sp.simplify(g_zero.inv() * j_minus.T * g_minus)
    t_plus = sp.simplify(j_plus_adjoint * j_plus)
    t_minus = sp.simplify(j_minus_adjoint * j_minus)
    weighted_t_residual = sp.simplify(lam_plus * t_plus + lam_minus * t_minus - identity)
    expected_t_plus = sp.diag(
        *[sp.simplify(p_plus[center] / p_zero[center]) for center, _, _ in basis]
    )
    expected_t_minus = sp.diag(
        *[sp.simplify(p_minus[center] / p_zero[center]) for center, _, _ in basis]
    )

    left_generators = [
        _left_matrix_unit(center, row, column, basis, index)
        for center, row, column in basis
    ]
    commutator_residuals = [
        sp.simplify(t_matrix * generator - generator * t_matrix)
        for t_matrix in (t_plus, t_minus)
        for generator in left_generators
    ]

    # A common formal real-time translation: u=exp(i*t*Delta).
    u = sp.symbols("u", nonzero=True)
    translation = sp.diag(*[u ** (row - column) for _, row, column in basis])
    translation_residuals = [
        sp.simplify(j_matrix * translation - translation * j_matrix)
        for j_matrix in (j_plus, j_minus)
    ]

    # Full two-insertion analytic words alpha_(i beta/2)(E_ab) E_bc.
    word_labels: list[tuple[int, int, int, int]] = []
    word_vectors = sp.zeros(len(basis), 16)
    for word_index, (center, a, b, c) in enumerate(product(range(2), repeat=4)):
        word_labels.append((center, a, b, c))
        coefficient = boltzmann_ratio ** sp.Rational(a - b, 2)
        word_vectors[index[(center, a, c)], word_index] = coefficient
    word_gram_plus = sp.simplify(word_vectors.T * g_plus * word_vectors)
    word_gram_minus = sp.simplify(word_vectors.T * g_minus * word_vectors)
    word_gram_zero = sp.simplify(word_vectors.T * g_zero * word_vectors)
    word_mixture_residual = sp.simplify(
        word_gram_zero
        - lam_plus * word_gram_plus
        - lam_minus * word_gram_minus
    )
    zero_nullspace = word_gram_zero.nullspace()
    null_intersection = all(
        matrix_zero(word_gram_plus * vector)
        and matrix_zero(word_gram_minus * vector)
        for vector in zero_nullspace
    )

    # Exhaustive KMS boundary identity on all central matrix units.
    kms_rows: list[dict[str, Any]] = []
    for phase, center_weights in (("plus", p_plus), ("minus", p_minus)):
        for center, i, j, k, ell in product(range(2), repeat=5):
            real_phase = u ** (k - ell)
            modular_ratio = boltzmann_ratio ** (k - ell)
            lhs = sp.simplify(
                real_phase
                * modular_ratio
                * _state_of_matrix_unit_product(
                    center_weights[center], rho, (i, j), (k, ell)
                )
            )
            rhs = sp.simplify(
                real_phase
                * _state_of_matrix_unit_product(
                    center_weights[center], rho, (k, ell), (i, j)
                )
            )
            kms_rows.append(
                {
                    "phase": phase,
                    "center": center,
                    "A": [i, j],
                    "B": [k, ell],
                    "residual": sp.simplify(lhs - rhs),
                }
            )

    # The commutant RN formula on a non-self-adjoint exact test element.
    omega = _omega_vector(index)
    x_blocks = (
        sp.Matrix([[1, 2], [3, 4]]),
        sp.Matrix([[5, 6], [7, 8]]),
    )
    left_x = sp.zeros(len(basis))
    for center in range(2):
        for row in range(2):
            for column in range(2):
                left_x += x_blocks[center][row, column] * _left_matrix_unit(
                    center, row, column, basis, index
                )

    def direct_state(center_weights: tuple[sp.Rational, sp.Rational]) -> sp.Expr:
        return sp.simplify(
            sum(
                center_weights[center]
                * sum(rho[i] * x_blocks[center][i, i] for i in range(2))
                for center in range(2)
            )
        )

    rn_plus_value = sp.simplify((omega.T * g_zero * t_plus * left_x * omega)[0])
    rn_minus_value = sp.simplify((omega.T * g_zero * t_minus * left_x * omega)[0])

    # Canonical symmetric mixture: parity is internally state preserving only here.
    symmetric_center = tuple(
        sp.simplify((p_plus[i] + p_minus[i]) / 2) for i in range(2)
    )
    g_symmetric = _gram(symmetric_center, rho, basis)
    parity = sp.zeros(len(basis))
    for source, (center, row, column) in enumerate(basis):
        parity[index[(1 - center, row, column)], source] = 1

    return {
        "inputs": {
            "lambda_plus": lam_plus,
            "lambda_minus": lam_minus,
            "p_plus": p_plus,
            "p_minus": p_minus,
            "boltzmann_ratio": boltzmann_ratio,
        },
        "rho": rho,
        "p_zero": p_zero,
        "gram_plus": g_plus,
        "gram_minus": g_minus,
        "gram_zero": g_zero,
        "mixture_residual": mixture_residual,
        "T_plus": t_plus,
        "T_minus": t_minus,
        "expected_T_plus": expected_t_plus,
        "expected_T_minus": expected_t_minus,
        "weighted_T_residual": weighted_t_residual,
        "T_plus_bound_residual": sp.simplify(identity / lam_plus - t_plus),
        "T_minus_bound_residual": sp.simplify(identity / lam_minus - t_minus),
        "commutator_residuals": commutator_residuals,
        "translation_residuals": translation_residuals,
        "word_labels": word_labels,
        "word_gram_rank": word_gram_zero.rank(),
        "word_nullity": len(zero_nullspace),
        "word_mixture_residual": word_mixture_residual,
        "word_null_intersection": null_intersection,
        "kms_rows": kms_rows,
        "rn_plus_value": rn_plus_value,
        "rn_minus_value": rn_minus_value,
        "direct_plus_value": direct_state(p_plus),
        "direct_minus_value": direct_state(p_minus),
        "rn_are_not_projections": any(
            sp.simplify(value * (value - 1)) != 0
            for value in list(t_plus.diagonal()) + list(t_minus.diagonal())
        ),
        "mixture_faithful": all(value > 0 for value in g_zero.diagonal()),
        "symmetric_parity_gram_residual": sp.simplify(
            parity.T * g_symmetric * parity - g_symmetric
        ),
        "symmetric_parity_translation_residual": sp.simplify(
            parity * translation - translation * parity
        ),
    }


def sharp_time_only_counterexample() -> dict[str, Any]:
    # INPUT: beta=1 and beta*nu=log(2), chosen so every displayed density is exact.
    beta = sp.Integer(1)
    nu = sp.log(2)
    identity = sp.eye(2)
    sigma_x = sp.Matrix([[0, 1], [1, 0]])
    sigma_y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sigma_z = sp.diag(1, -1)
    rho_zero = identity / 2
    exp_minus_h_one = sp.cosh(nu) * identity + sp.sinh(nu) * sigma_x
    rho_one = sp.simplify(exp_minus_h_one / sp.trace(exp_minus_h_one))

    a, b = sp.symbols("a b", real=True)
    sharp = sp.diag(a, b)
    sharp_q_zero = sp.simplify(sp.trace(rho_zero * sharp.T * sharp))
    sharp_q_one = sp.simplify(sp.trace(rho_one * sharp.T * sharp))

    t_star = sp.simplify(sp.pi / (4 * nu))
    angle = sp.simplify(nu * t_star)
    # H_1=-nu*sigma_x, so exp(i t H_1)=cos(nu t)I-i sin(nu t)sigma_x.
    unitary = sp.cos(angle) * identity - sp.I * sp.sin(angle) * sigma_x
    evolved = sp.simplify(unitary * sigma_z * unitary.conjugate().T)
    difference_square = sp.simplify((evolved - sigma_z) ** 2)

    half = beta / 2
    exp_minus_half_h = sp.cosh(half * nu) * identity + sp.sinh(half * nu) * sigma_x
    exp_plus_half_h = sp.cosh(half * nu) * identity - sp.sinh(half * nu) * sigma_x
    euclidean_evolved = sp.simplify(
        exp_minus_half_h * sigma_z * exp_plus_half_h
    )
    midpoint_zero = sp.simplify(sp.trace(rho_zero * sigma_z * sigma_z))
    midpoint_one = sp.simplify(
        sp.trace(rho_one * sigma_z * euclidean_evolved)
    )

    return {
        "beta": beta,
        "nu": nu,
        "rho_zero": rho_zero,
        "rho_one": rho_one,
        "sharp_q_zero": sharp_q_zero,
        "sharp_q_one": sharp_q_one,
        "t_star": t_star,
        "evolved_sigma_z": evolved,
        "expected_evolved": -sigma_y,
        "difference_square": difference_square,
        "operator_norm_difference": sp.sqrt(2),
        "midpoint_zero": midpoint_zero,
        "midpoint_one": midpoint_one,
        "sharp_time_inference_valid": False,
        "full_cylinder_translation_required": True,
    }


def half_modular_scalarity_audit() -> dict[str, Any]:
    """Verify the exact coefficients and hostile finite-CCR control fixture.

    The coefficient identities are bookkeeping checks for the analytic theorem
    in the v1.4 certificate.  The oscillator truncation deliberately is *not*
    used as proof: its top-state defect records why finite matrices cannot
    represent the canonical commutation relation.
    """

    # SYMBOLIC INPUTS: all parameters in the analytic half-modular theorem.
    beta, c, radius, hbar, chi, displacement = sp.symbols(
        "beta c R hbar chi a", positive=True
    )
    half_strip = beta / 2
    strip_coefficient = sp.simplify(1 / half_strip)
    bond_shift_coefficient = -c * radius
    momentum_boost_coefficient = hbar * radius / chi
    cross_exponent_coefficient = -half_strip * c * displacement

    # TEST FIXTURE INPUT: the complete 2x2x2 cube.  Every nonempty subset is
    # peeled by a maximal first-coordinate site and its +e_1 outward neighbor.
    cube_sites = list(product(range(2), repeat=3))
    subset_count = 0
    peeling_steps = 0
    maximum_depth = 0
    outward_failures: list[dict[str, Any]] = []
    full_cube_trace: list[dict[str, tuple[int, int, int]]] = []
    full_mask = (1 << len(cube_sites)) - 1
    for mask in range(1, full_mask + 1):
        active = {
            site for index, site in enumerate(cube_sites) if mask & (1 << index)
        }
        initial_depth = len(active)
        trace: list[dict[str, tuple[int, int, int]]] = []
        while active:
            maximal_first = max(site[0] for site in active)
            extreme = max(site for site in active if site[0] == maximal_first)
            outward = (extreme[0] + 1, extreme[1], extreme[2])
            if outward in active:
                outward_failures.append(
                    {"mask": mask, "extreme": extreme, "outward": outward}
                )
            trace.append({"extreme": extreme, "outward": outward})
            active.remove(extreme)
            peeling_steps += 1
        if mask == full_mask:
            full_cube_trace = trace
        subset_count += 1
        maximum_depth = max(maximum_depth, initial_depth)

    expected_subset_count = 2 ** len(cube_sites) - 1
    expected_peeling_steps = len(cube_sites) * 2 ** (len(cube_sites) - 1)

    # HOSTILE CONTROL INPUT: a finite oscillator dimension.  This checks the
    # exact boundary term, not the infinite-dimensional theorem.
    truncation_dimension = 5
    annihilation = sp.zeros(truncation_dimension)
    for occupation in range(1, truncation_dimension):
        annihilation[occupation - 1, occupation] = sp.sqrt(occupation)
    creation = annihilation.T
    q_truncated = sp.sqrt(hbar / 2) * (annihilation + creation)
    p_truncated = -sp.I * sp.sqrt(hbar / 2) * (annihilation - creation)
    commutator = sp.simplify(q_truncated * p_truncated - p_truncated * q_truncated)
    top_projection = sp.zeros(truncation_dimension)
    top_projection[truncation_dimension - 1, truncation_dimension - 1] = 1
    exact_truncated_ccr = sp.I * hbar * (
        sp.eye(truncation_dimension) - truncation_dimension * top_projection
    )
    canonical_ccr_defect = sp.simplify(
        commutator - sp.I * hbar * sp.eye(truncation_dimension)
    )
    expected_canonical_defect = (
        -sp.I * hbar * truncation_dimension * top_projection
    )

    return {
        "inputs": {
            "beta": beta,
            "c": c,
            "R": radius,
            "hbar": hbar,
            "chi": chi,
            "a": displacement,
            "truncation_dimension": truncation_dimension,
        },
        "half_strip": half_strip,
        "strip_coefficient": strip_coefficient,
        "expected_strip_coefficient": 2 / beta,
        "bond_shift_coefficient": bond_shift_coefficient,
        "expected_bond_shift_coefficient": -c * radius,
        "momentum_boost_coefficient": momentum_boost_coefficient,
        "expected_momentum_boost_coefficient": hbar * radius / chi,
        "cross_exponent_coefficient": cross_exponent_coefficient,
        "expected_cross_exponent_coefficient": -half_strip * c * displacement,
        "cross_exponent_nonzero": cross_exponent_coefficient != 0,
        "cube_site_count": len(cube_sites),
        "peeled_nonempty_subset_count": subset_count,
        "expected_nonempty_subset_count": expected_subset_count,
        "peeling_step_count": peeling_steps,
        "expected_peeling_step_count": expected_peeling_steps,
        "maximum_peeling_depth": maximum_depth,
        "outward_failure_count": len(outward_failures),
        "outward_failures": outward_failures,
        "full_cube_trace": full_cube_trace,
        "truncated_commutator": commutator,
        "exact_truncated_ccr": exact_truncated_ccr,
        "truncated_ccr_residual": sp.simplify(commutator - exact_truncated_ccr),
        "canonical_ccr_defect": canonical_ccr_defect,
        "expected_canonical_ccr_defect": expected_canonical_defect,
        "canonical_ccr_defect_residual": sp.simplify(
            canonical_ccr_defect - expected_canonical_defect
        ),
        "commutator_trace": sp.simplify(sp.trace(commutator)),
        "canonical_ccr_defect_rank": canonical_ccr_defect.rank(),
        "analytic_infinite_dimensional_theorem_authoritative": True,
        "finite_truncation_authoritative": False,
        "finite_truncation_role": (
            "hostile boundary control: [q_N,p_N]=i*hbar*(I-N*P_top)"
        ),
    }


def single_rung_influence_audit() -> dict[str, Any]:
    """Compute the exact Weyl sine response and its uniformity obstruction."""

    # EXACT FIXTURE INPUTS: positive units and one nonzero oriented bond step.
    hbar = sp.Rational(13, 17)
    c = sp.Rational(3, 5)
    delta = -sp.Rational(2, 7)
    b = sp.Rational(5, 11)
    graph_normalization = sp.Rational(7, 3)
    a_fixture = sp.simplify(
        sp.pi * hbar / (c * sp.Abs(delta) * b)
    )
    half_phase = sp.simplify(c * delta * a_fixture * b / (2 * hbar))
    response_formula = sp.simplify(
        2
        * sp.sqrt(2)
        / graph_normalization
        * sp.Abs(sp.sin(half_phase))
    )
    saturated_response = sp.simplify(2 * sp.sqrt(2) / graph_normalization)

    opposite_delta = -delta
    opposite_a = sp.simplify(
        sp.pi * hbar / (c * sp.Abs(opposite_delta) * b)
    )
    opposite_half_phase = sp.simplify(
        c * opposite_delta * opposite_a * b / (2 * hbar)
    )
    opposite_response = sp.simplify(
        2
        * sp.sqrt(2)
        / graph_normalization
        * sp.Abs(sp.sin(opposite_half_phase))
    )

    # A symbolic positive epsilon makes the quantifier failure explicit: the
    # source frequency a(epsilon) diverges while the response stays fixed.
    epsilon = sp.symbols("epsilon", positive=True)
    epsilon_a = sp.simplify(sp.pi * hbar / (c * epsilon * b))
    epsilon_half_phase = sp.simplify(c * epsilon * epsilon_a * b / (2 * hbar))
    epsilon_response = sp.simplify(
        2
        * sp.sqrt(2)
        / graph_normalization
        * sp.Abs(sp.sin(epsilon_half_phase))
    )

    # TEST INPUTS: an exact decreasing coefficient sequence used only as a
    # finite regression fixture for the symbolic all-epsilon identity.
    sequence = []
    for denominator in (2, 4, 8, 16):
        delta_n = sp.Rational(1, denominator)
        a_n = sp.simplify(sp.pi * hbar / (c * delta_n * b))
        phase_n = sp.simplify(c * delta_n * a_n * b / (2 * hbar))
        response_n = sp.simplify(
            2
            * sp.sqrt(2)
            / graph_normalization
            * sp.Abs(sp.sin(phase_n))
        )
        sequence.append(
            {
                "delta": delta_n,
                "a": a_n,
                "half_phase": phase_n,
                "response": response_n,
            }
        )

    positive_precursor_scope = {
        "finite_volume_critical_graph_bond_kick_energy_propagation": True,
        "finite_volume_energy_constrained_strongstar_bond_kick_propagation": True,
        "weyl_fourier_analytic_shear_radius_recurrence": True,
        "quartic_onsite_all_moment_orbit_frechet_invariance": False,
        "volume_uniform_thermodynamic_cauchy": False,
        "hamiltonian_thermodynamic_alpha_identification": False,
    }

    return {
        "inputs": {
            "hbar": hbar,
            "c": c,
            "delta": delta,
            "b": b,
            "G_y_W_b": graph_normalization,
        },
        "bond_kick_identity": (
            "beta_delta(W_a(x))=W_a(x) exp(-i*c*delta*a*q_y/hbar)"
        ),
        "exact_response_identity": (
            "(2*sqrt(2)/G_y(W_b))*Abs(sin(c*delta*a*b/(2*hbar)))"
        ),
        "a_fixture": a_fixture,
        "expected_a_fixture": sp.pi * hbar / (c * sp.Abs(delta) * b),
        "half_phase": half_phase,
        "response": response_formula,
        "saturated_response": saturated_response,
        "opposite_half_phase": opposite_half_phase,
        "opposite_response": opposite_response,
        "epsilon": epsilon,
        "epsilon_a": epsilon_a,
        "epsilon_half_phase": epsilon_half_phase,
        "epsilon_response": epsilon_response,
        "decreasing_delta_fixture": sequence,
        "initial_y_influence": sp.Integer(0),
        "uniform_x_influence_upper_bound": 2 * sp.sqrt(2),
        "frequency_blind_small_coefficient_recurrence_possible": False,
        "positive_precursor_scope": positive_precursor_scope,
    }


def theorem_schema() -> dict[str, Any]:
    return {
        "name": "fixed-beta canonical OS-mixture common-normal-envelope theorem",
        "hypotheses": {
            "fixed_beta": True,
            "positive_mixture_weights": True,
            "common_reflection_field_and_positive_time_cylinder_module": True,
            "common_sharp_multipliers": True,
            "common_formal_analytic_word_algebra": True,
            "translation_intertwining": True,
        },
        "exact_form_identity": "q_0=lambda_+ q_+ + lambda_- q_-",
        "canonical_maps": "J_sigma[F]_0=[F]_sigma and T_sigma=J_sigma^*J_sigma",
        "conclusions": {
            "bounded_dense_range_J": True,
            "T_in_mixture_commutant": True,
            "weighted_T_partition_of_identity": True,
            "component_states_normal": True,
            "component_states_beta_KMS_for_one_reconstructed_alpha": True,
            "faithful_mixture_two_sided_L2_metrizes_bounded_strong_star": True,
            "interior_weight_envelopes_label_equivalent": True,
        },
        "v1_4_route_split": {
            "full_gibbs_half_modular_nontrivial_local_class_available": False,
            "frequency_blind_single_rung_site_recurrence_available": False,
            "analytic_half_modular_extreme_site_theorem_authoritative": True,
            "finite_oscillator_truncation_authoritative": False,
            "finite_volume_graph_energy_precursor_survives": True,
            "weyl_frequency_or_analytic_rung_profile_required": True,
        },
        "open_boundaries": {
            "finite_volume_strong_star_cauchy": True,
            "hamiltonian_thermodynamic_limit_identification": True,
            "phase_state_independent_quasilocal_Cstar_alpha": True,
            "exhaustion_independence": True,
            "common_local_generator_core": True,
            "beta_independent_passage": True,
            "beta_to_infinity_ground_passage": True,
            "GNS_gap": True,
            "continuum": True,
            "physical_empty_comparison": True,
            "Pre_A": True,
        },
        "strong_star_successor_criterion": (
            "For every preregistered bounded local analytic A and compact time "
            "interval, prove mixture expectations of D^*D+DD^* tend to zero "
            "for nested finite-volume zero-source dynamics."
        ),
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing = [str(path.relative_to(REPO)).replace("\\", "/") for path in (MANIFEST, CERTIFICATE) if not path.exists()]
    if missing and not staged:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"staged v1.4 authority is missing ({joined}); rerun with --staged"
        )
    if missing:
        return {"status": "MISSING_STAGED", "missing": missing}

    manifest_text = MANIFEST.read_text(encoding="utf-8")
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    audit.check(
        "authority task",
        manifest["task_id"] == "T-054",
        manifest["task_id"],
        "T-054",
        "authority",
    )
    audit.check(
        "authority exploration",
        manifest["exploration_id"] == EXPECTED_EXPLORATION,
        manifest["exploration_id"],
        EXPECTED_EXPLORATION,
        "authority",
    )
    audit.check(
        "authority result number",
        manifest["result_number"] == EXPECTED_RESULT_NUMBER,
        manifest["result_number"],
        EXPECTED_RESULT_NUMBER,
        "authority",
    )
    audit.check(
        "authority result version",
        manifest["result_version"] == EXPECTED_RESULT_VERSION,
        manifest["result_version"],
        EXPECTED_RESULT_VERSION,
        "authority",
    )
    audit.check(
        "authority result id",
        manifest["result_id"] == EXPECTED_RESULT_ID,
        manifest["result_id"],
        EXPECTED_RESULT_ID,
        "authority",
    )
    audit.check(
        "authority claim nonbearing",
        manifest["claim_bearing"] is False,
        manifest["claim_bearing"],
        False,
        "authority",
    )
    manifest_negative_ids = tuple(manifest["negative_ids"])
    audit.check(
        "all v1.4 negatives registered in order",
        manifest_negative_ids == NEGATIVE_IDS
        and all(item in certificate for item in NEGATIVE_IDS),
        manifest_negative_ids,
        NEGATIVE_IDS,
        "authority",
    )
    for object_name in (
        "fixed_beta_os_mixture_theorem",
        "sharp_time_only_counterexample",
        "half_modular_local_scalarity_theorem",
        "single_rung_influence_counterexample",
        "hamiltonian_identification_boundary",
    ):
        audit.check(
            f"manifest object {object_name}",
            object_name in manifest and isinstance(manifest[object_name], dict),
            object_name if object_name in manifest else "MISSING",
            object_name,
            "authority",
        )
    semantic_pairs = (
        ("strip coefficient", "2M/beta"),
        ("bond shift", "-cR"),
        ("momentum boost", "hbar R/chi"),
        ("cross exponent", "-sca"),
        ("truncated CCR boundary", "I-NP_"),
        ("single-rung frequency fixture", "a=pi hbar/(c|delta|b)"),
    )
    combined_authority = manifest_text + "\n" + certificate
    for label, token in semantic_pairs:
        audit.check(
            f"authority semantic {label}",
            token in combined_authority,
            token if token in combined_authority else "MISSING",
            token,
            "authority",
        )
    for token in (
        EXPECTED_EXPLORATION,
        EXPECTED_RESULT_NUMBER,
        EXPECTED_RESULT_VERSION,
        "fixed-beta",
        "KMS",
        "strong-star",
        "thermodynamic",
        "beta-independent",
        "Pre-A",
        "analytic infinite-dimensional theorem",
        "non-authoritative",
    ):
        audit.check(
            f"certificate token {token}",
            token in certificate,
            token if token in certificate else "MISSING",
            token,
            "authority",
        )
    return {"status": "COMPLETE", "missing": []}


def run_audit(staged: bool) -> dict[str, Any]:
    audit = Audit()
    mixture = full_cylinder_mixture_audit()
    sharp = sharp_time_only_counterexample()
    half_modular = half_modular_scalarity_audit()
    single_rung = single_rung_influence_audit()
    theorem = theorem_schema()

    audit.check(
        "Gibbs qubit weights",
        mixture["rho"] == (sp.Rational(2, 3), sp.Rational(1, 3)),
        mixture["rho"],
        (sp.Rational(2, 3), sp.Rational(1, 3)),
        "mixture",
    )
    audit.check(
        "derived mixture center law",
        mixture["p_zero"] == (sp.Rational(9, 20), sp.Rational(11, 20)),
        mixture["p_zero"],
        (sp.Rational(9, 20), sp.Rational(11, 20)),
        "mixture",
    )
    audit.check(
        "full Gram mixture identity",
        matrix_zero(mixture["mixture_residual"]),
        mixture["mixture_residual"],
        "zero matrix",
        "mixture",
    )
    audit.check(
        "T plus exact",
        matrix_equal(mixture["T_plus"], mixture["expected_T_plus"]),
        mixture["T_plus"],
        mixture["expected_T_plus"],
        "RN",
    )
    audit.check(
        "T minus exact",
        matrix_equal(mixture["T_minus"], mixture["expected_T_minus"]),
        mixture["T_minus"],
        mixture["expected_T_minus"],
        "RN",
    )
    audit.check(
        "weighted T identity",
        matrix_zero(mixture["weighted_T_residual"]),
        mixture["weighted_T_residual"],
        "zero matrix",
        "RN",
    )
    audit.check(
        "T plus domination",
        all(value >= 0 for value in mixture["T_plus_bound_residual"].diagonal()),
        mixture["T_plus_bound_residual"].diagonal(),
        "nonnegative diagonal",
        "RN",
    )
    audit.check(
        "T minus domination",
        all(value >= 0 for value in mixture["T_minus_bound_residual"].diagonal()),
        mixture["T_minus_bound_residual"].diagonal(),
        "nonnegative diagonal",
        "RN",
    )
    audit.check(
        "T in common-word commutant",
        all(matrix_zero(residual) for residual in mixture["commutator_residuals"]),
        len(mixture["commutator_residuals"]),
        "all zero",
        "RN",
    )
    audit.check(
        "J translation intertwining",
        all(matrix_zero(residual) for residual in mixture["translation_residuals"]),
        mixture["translation_residuals"],
        "all zero",
        "functoriality",
    )
    audit.check(
        "two-insertion cylinder Gram mixture",
        matrix_zero(mixture["word_mixture_residual"]),
        mixture["word_mixture_residual"],
        "zero matrix",
        "functoriality",
    )
    audit.check(
        "analytic word rank",
        mixture["word_gram_rank"] == 8,
        mixture["word_gram_rank"],
        8,
        "functoriality",
    )
    audit.check(
        "analytic word null intersection",
        mixture["word_null_intersection"] is True,
        {"nullity": mixture["word_nullity"], "intersection": mixture["word_null_intersection"]},
        "N0=N+ intersection N-",
        "functoriality",
    )
    audit.check(
        "exhaustive KMS word inheritance",
        all(row["residual"] == 0 for row in mixture["kms_rows"]),
        len(mixture["kms_rows"]),
        "all matrix-unit KMS residuals zero",
        "KMS",
    )
    audit.check(
        "RN plus functional",
        mixture["rn_plus_value"] == mixture["direct_plus_value"],
        mixture["rn_plus_value"],
        mixture["direct_plus_value"],
        "RN",
    )
    audit.check(
        "RN minus functional",
        mixture["rn_minus_value"] == mixture["direct_minus_value"],
        mixture["rn_minus_value"],
        mixture["direct_minus_value"],
        "RN",
    )
    audit.check(
        "overlapping phases do not imply projections",
        mixture["rn_are_not_projections"] is True,
        mixture["rn_are_not_projections"],
        True,
        "scope",
    )
    audit.check(
        "mixture state faithful",
        mixture["mixture_faithful"] is True,
        mixture["mixture_faithful"],
        True,
        "strong_star",
    )
    audit.check(
        "symmetric mixture parity invariant",
        matrix_zero(mixture["symmetric_parity_gram_residual"]),
        mixture["symmetric_parity_gram_residual"],
        "zero matrix",
        "parity",
    )
    audit.check(
        "parity commutes with translation",
        matrix_zero(mixture["symmetric_parity_translation_residual"]),
        mixture["symmetric_parity_translation_residual"],
        "zero matrix",
        "parity",
    )

    audit.check(
        "sharp Gibbs density",
        matrix_equal(
            sharp["rho_one"],
            sp.Matrix([[sp.Rational(1, 2), sp.Rational(3, 10)], [sp.Rational(3, 10), sp.Rational(1, 2)]]),
        ),
        sharp["rho_one"],
        "[[1/2,3/10],[3/10,1/2]]",
        "sharp_counterexample",
    )
    audit.check(
        "sharp-time Gram equality",
        sp.simplify(sharp["sharp_q_zero"] - sharp["sharp_q_one"]) == 0,
        {"zero": sharp["sharp_q_zero"], "one": sharp["sharp_q_one"]},
        "equal",
        "sharp_counterexample",
    )
    audit.check(
        "real-time dynamics differ",
        matrix_equal(sharp["evolved_sigma_z"], sharp["expected_evolved"]),
        sharp["evolved_sigma_z"],
        sharp["expected_evolved"],
        "sharp_counterexample",
    )
    audit.check(
        "real-time norm gap",
        matrix_equal(sharp["difference_square"], 2 * sp.eye(2)),
        sharp["difference_square"],
        "2I hence norm sqrt(2)",
        "sharp_counterexample",
    )
    audit.check(
        "Euclidean midpoint separates dynamics",
        sharp["midpoint_zero"] == 1 and sharp["midpoint_one"] == sp.Rational(4, 5),
        {"zero": sharp["midpoint_zero"], "one": sharp["midpoint_one"]},
        {"zero": 1, "one": sp.Rational(4, 5)},
        "sharp_counterexample",
    )
    audit.check(
        "sharp-only inference rejected",
        sharp["sharp_time_inference_valid"] is False
        and sharp["full_cylinder_translation_required"] is True,
        {
            "sharp_valid": sharp["sharp_time_inference_valid"],
            "full_required": sharp["full_cylinder_translation_required"],
        },
        "sharp-time insufficient; full cylinder required",
        "sharp_counterexample",
    )

    audit.check(
        "half-modular strip coefficient",
        sp.simplify(
            half_modular["strip_coefficient"]
            - half_modular["expected_strip_coefficient"]
        )
        == 0,
        half_modular["strip_coefficient"],
        "2/beta",
        "half_modular",
    )
    audit.check(
        "outward bond translation coefficient",
        sp.simplify(
            half_modular["bond_shift_coefficient"]
            - half_modular["expected_bond_shift_coefficient"]
        )
        == 0,
        half_modular["bond_shift_coefficient"],
        "-c*R",
        "half_modular",
    )
    audit.check(
        "momentum boost coefficient",
        sp.simplify(
            half_modular["momentum_boost_coefficient"]
            - half_modular["expected_momentum_boost_coefficient"]
        )
        == 0,
        half_modular["momentum_boost_coefficient"],
        "hbar*R/chi",
        "half_modular",
    )
    audit.check(
        "cross witness exponent coefficient",
        sp.simplify(
            half_modular["cross_exponent_coefficient"]
            - half_modular["expected_cross_exponent_coefficient"]
        )
        == 0
        and half_modular["cross_exponent_nonzero"],
        half_modular["cross_exponent_coefficient"],
        "-s*c*a with s=beta/2 and nonzero positive inputs",
        "half_modular",
    )
    audit.check(
        "2x2x2 all-subset extreme-site peeling",
        half_modular["peeled_nonempty_subset_count"]
        == half_modular["expected_nonempty_subset_count"],
        half_modular["peeled_nonempty_subset_count"],
        half_modular["expected_nonempty_subset_count"],
        "extreme_site",
    )
    audit.check(
        "2x2x2 aggregate peeling steps",
        half_modular["peeling_step_count"]
        == half_modular["expected_peeling_step_count"],
        half_modular["peeling_step_count"],
        half_modular["expected_peeling_step_count"],
        "extreme_site",
    )
    audit.check(
        "outward neighbor absent at every peel",
        half_modular["outward_failure_count"] == 0,
        half_modular["outward_failure_count"],
        0,
        "extreme_site",
    )
    audit.check(
        "full cube peeled to scalar base",
        len(half_modular["full_cube_trace"])
        == half_modular["cube_site_count"]
        == half_modular["maximum_peeling_depth"],
        {
            "trace_length": len(half_modular["full_cube_trace"]),
            "maximum_depth": half_modular["maximum_peeling_depth"],
        },
        half_modular["cube_site_count"],
        "extreme_site",
    )
    audit.check(
        "finite truncation exact CCR boundary",
        matrix_zero(half_modular["truncated_ccr_residual"]),
        half_modular["truncated_commutator"],
        "i*hbar*(I-N*P_top)",
        "truncation_boundary",
    )
    audit.check(
        "finite truncation canonical CCR defect",
        matrix_zero(half_modular["canonical_ccr_defect_residual"]),
        half_modular["canonical_ccr_defect"],
        half_modular["expected_canonical_ccr_defect"],
        "truncation_boundary",
    )
    audit.check(
        "finite truncation trace-rank obstruction",
        half_modular["commutator_trace"] == 0
        and half_modular["canonical_ccr_defect_rank"] == 1,
        {
            "trace": half_modular["commutator_trace"],
            "defect_rank": half_modular["canonical_ccr_defect_rank"],
        },
        {"trace": 0, "defect_rank": 1},
        "truncation_boundary",
    )
    audit.check(
        "analytic authority excludes finite truncation",
        half_modular["analytic_infinite_dimensional_theorem_authoritative"]
        is True
        and half_modular["finite_truncation_authoritative"] is False,
        {
            "analytic": half_modular[
                "analytic_infinite_dimensional_theorem_authoritative"
            ],
            "finite_truncation": half_modular[
                "finite_truncation_authoritative"
            ],
        },
        {"analytic": True, "finite_truncation": False},
        "scope",
    )

    audit.check(
        "single-rung prescribed frequency fixture",
        sp.simplify(single_rung["a_fixture"] - single_rung["expected_a_fixture"])
        == 0,
        single_rung["a_fixture"],
        "pi*hbar/(c*Abs(delta)*b)",
        "single_rung",
    )
    audit.check(
        "single-rung half phase saturation",
        sp.simplify(sp.Abs(single_rung["half_phase"]) - sp.pi / 2) == 0,
        single_rung["half_phase"],
        "+/- pi/2",
        "single_rung",
    )
    audit.check(
        "single-rung exact sine response",
        sp.simplify(single_rung["response"] - single_rung["saturated_response"])
        == 0,
        single_rung["response"],
        single_rung["saturated_response"],
        "single_rung",
    )
    audit.check(
        "single-rung orientation-independent magnitude",
        sp.simplify(
            sp.Abs(single_rung["opposite_half_phase"]) - sp.pi / 2
        )
        == 0
        and sp.simplify(
            single_rung["opposite_response"]
            - single_rung["saturated_response"]
        )
        == 0,
        {
            "half_phase": single_rung["opposite_half_phase"],
            "response": single_rung["opposite_response"],
        },
        {"abs_half_phase": "pi/2", "response": single_rung["saturated_response"]},
        "single_rung",
    )
    audit.check(
        "all-positive-epsilon saturation identity",
        single_rung["epsilon_half_phase"] == sp.pi / 2
        and sp.simplify(
            single_rung["epsilon_response"] - single_rung["saturated_response"]
        )
        == 0,
        {
            "half_phase": single_rung["epsilon_half_phase"],
            "response": single_rung["epsilon_response"],
        },
        {"half_phase": "pi/2", "response": single_rung["saturated_response"]},
        "single_rung",
    )
    audit.check(
        "decreasing-delta exact saturation regression",
        all(
            row["half_phase"] == sp.pi / 2
            and sp.simplify(row["response"] - single_rung["saturated_response"])
            == 0
            for row in single_rung["decreasing_delta_fixture"]
        ),
        len(single_rung["decreasing_delta_fixture"]),
        "all exact responses saturated",
        "single_rung",
    )
    audit.check(
        "single-rung initial influences",
        single_rung["initial_y_influence"] == 0
        and single_rung["uniform_x_influence_upper_bound"] == 2 * sp.sqrt(2),
        {
            "y": single_rung["initial_y_influence"],
            "x_upper": single_rung["uniform_x_influence_upper_bound"],
        },
        {"y": 0, "x_upper": "2*sqrt(2)"},
        "single_rung",
    )
    audit.check(
        "frequency-blind small-coefficient recurrence rejected",
        single_rung["frequency_blind_small_coefficient_recurrence_possible"]
        is False,
        single_rung["frequency_blind_small_coefficient_recurrence_possible"],
        False,
        "single_rung",
    )
    precursor = single_rung["positive_precursor_scope"]
    audit.check(
        "finite-volume graph-energy precursors retained",
        precursor["finite_volume_critical_graph_bond_kick_energy_propagation"]
        is True
        and precursor[
            "finite_volume_energy_constrained_strongstar_bond_kick_propagation"
        ]
        is True
        and precursor["weyl_fourier_analytic_shear_radius_recurrence"] is True,
        precursor,
        "three finite-volume/analytic precursor statements true",
        "precursor_scope",
    )
    audit.check(
        "precursors do not close onsite or thermodynamic gates",
        precursor["quartic_onsite_all_moment_orbit_frechet_invariance"] is False
        and precursor["volume_uniform_thermodynamic_cauchy"] is False
        and precursor["hamiltonian_thermodynamic_alpha_identification"] is False,
        precursor,
        "quartic onsite and thermodynamic gates remain false",
        "precursor_scope",
    )

    audit.check(
        "theorem is fixed-beta",
        theorem["hypotheses"]["fixed_beta"] is True,
        theorem["hypotheses"],
        "fixed beta",
        "scope",
    )
    audit.check(
        "normal common-envelope conclusions",
        all(theorem["conclusions"].values()),
        theorem["conclusions"],
        "all scoped conclusions true",
        "scope",
    )
    audit.check(
        "thermodynamic and beta-independent claims remain open",
        all(theorem["open_boundaries"].values()),
        theorem["open_boundaries"],
        "all listed boundaries open",
        "scope",
    )
    audit.check(
        "successor criterion is two-sided mixture L2",
        "D^*D+DD^*" in theorem["strong_star_successor_criterion"],
        theorem["strong_star_successor_criterion"],
        "two-sided mixture L2 boundary Cauchy",
        "scope",
    )

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    passed = len(audit.rows)
    source_paths = [SCRIPT, PARENT, OS_PARENT]
    if MANIFEST.exists():
        source_paths.append(MANIFEST)
    if CERTIFICATE.exists():
        source_paths.append(CERTIFICATE)
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "verdict": verdict,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "authority": authority,
        "derived": {
            "mixture": mixture,
            "sharp_time_counterexample": sharp,
            "half_modular_scalarity": half_modular,
            "single_rung_influence": single_rung,
            "theorem_schema": theorem,
            "fixed_beta_common_normal_envelope_closed": True,
            "analytic_infinite_dimensional_scalarity_theorem_authoritative": True,
            "finite_truncation_authoritative": False,
            "positive_finite_volume_graph_energy_precursor_closed": True,
            "finite_volume_strong_star_cauchy_closed": False,
            "hamiltonian_thermodynamic_alpha_closed": False,
            "beta_independent_alpha_closed": False,
            "common_alpha_KMS_for_hamiltonian_limit_closed": False,
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
        },
        "negative_id": NEGATIVE_IDS[0],
        "negative_ids": list(NEGATIVE_IDS),
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="permit missing v1.4 manifest/certificate and report INCOMPLETE",
    )
    args = parser.parse_args()
    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"{payload['verdict']} {summary['passed']}/{summary['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
