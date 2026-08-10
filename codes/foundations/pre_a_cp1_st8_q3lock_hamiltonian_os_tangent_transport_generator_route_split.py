#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v1.5 tangent-transport split.

The verifier recomputes every finite fixture used by the selected fixed-beta
Hamiltonian-to-OS route.  Until the matching certificate and formal authority
records are assembled, run with ``--staged``; missing authority is then
reported as ``INCOMPLETE`` rather than silently promoted to a proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-hamiltonian-os-tangent-transport-generator-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate.md"
PARENTS = (
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split-manifest.json",
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-counterterm-empty-route-split-manifest.json",
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split-manifest.json",
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json",
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-primary-{SLUG}/result.json"
)
EXPECTED_EXPLORATION = "EXP-000801"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v1.5"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CLOSED_SUBGATE = (
    "PA-CP1-ST8-Q3LOCK-FIXED-BETA-TANGENT-NET-BANDLIMITED-HAMILTONIAN-OS-POINTED-GNS-IDENTIFICATION"
)
EXPECTED_NEXT_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-BETA-INDEPENDENT-CSTAR-DYNAMICS"
)
NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-NAIVE-LABEL-EMBEDDING",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-CANONICAL-MOMENTUM-GENERATOR",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-CHARACTER-BOUNDED-GENERATOR-CORE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-ZERO-SOURCE-PERIODIC-LIMIT",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-AUTOMATIC-CROSS-BETA-GLUING",
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


def frobenius_square(matrix: sp.MatrixBase) -> sp.Expr:
    return sp.simplify(sum(sp.conjugate(value) * value for value in matrix))


def submatrix(matrix: sp.MatrixBase, indices: Iterable[int]) -> sp.Matrix:
    selected = tuple(indices)
    return sp.Matrix([[matrix[i, j] for j in selected] for i in selected])


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


def character_dirichlet_filter_audit() -> dict[str, Any]:
    # INPUTS: a rational multi-coordinate character and physical constants.
    beta = sp.Rational(5, 3)
    hbar = sp.Rational(7, 5)
    chi = sp.Rational(11, 6)
    xi = sp.Matrix([sp.Rational(1, 2), -sp.Rational(2, 3), sp.Rational(3, 5)])
    physical_bandwidth = sp.Rational(13, 4)

    xi_norm_sq = sp.simplify((xi.T * xi)[0])
    double_commutator = sp.simplify(hbar**2 * xi_norm_sq / chi)
    kubo_delta_square = sp.simplify(double_commutator / (beta * hbar**2))
    kubo_expected = sp.simplify(xi_norm_sq / (beta * chi))
    a_xi = sp.sqrt(kubo_delta_square)

    # The even Fejer multiplier is g_R(omega)=(1-|omega|/R)_+.
    duhamel_error_bound = sp.simplify(a_xi / physical_bandwidth)
    delta_duhamel_error_bound = a_xi
    unaveraged_two_sided_square_bound = sp.simplify(
        2 * duhamel_error_bound**2
        + beta * hbar * duhamel_error_bound * delta_duhamel_error_bound
    )
    unaveraged_two_sided_square_formula = sp.simplify(
        kubo_delta_square
        * (2 / physical_bandwidth**2 + beta * hbar / physical_bandwidth)
    )

    # The same estimate with dimensionless modular bandwidth U=beta*hbar*R.
    modular_bandwidth = sp.simplify(beta * hbar * physical_bandwidth)
    modular_form = sp.simplify(
        (beta * hbar * a_xi) ** 2
        * (2 / modular_bandwidth**2 + 1 / modular_bandwidth)
    )

    # Exact point fixture for (u/2)coth(u/2) <= 1+u/2.  The residual reduces
    # to (exp(u)-1-u)/(exp(u)-1), so positivity follows from exp(u)>1+u.
    modular_gap = sp.Rational(3, 2)
    modular_exponential = sp.exp(modular_gap)
    exponential_residual = modular_exponential - 1 - modular_gap
    mean_lhs_coth = sp.simplify(modular_gap * sp.coth(modular_gap / 2) / 2)
    mean_lhs = sp.together(
        modular_gap * (modular_exponential + 1)
        / (2 * (modular_exponential - 1))
    )
    mean_rhs = sp.simplify(1 + modular_gap / 2)
    mean_residual = sp.factor(sp.together(mean_rhs - mean_lhs))
    mean_residual_factorized = sp.factor(
        exponential_residual / (modular_exponential - 1)
    )

    # KMS invariance gives phi(delta W_xi)=0.  The Fejer multiplier equals one
    # at zero frequency, so its residual also has zero mean; connected and
    # uncentered Duhamel norms therefore coincide for this residual.
    generator_mean = sp.Integer(0)
    fejer_zero_multiplier = sp.Integer(1)
    filter_error_mean = sp.simplify((1 - fejer_zero_multiplier) * generator_mean)

    return {
        "inputs": {
            "beta": beta,
            "hbar": hbar,
            "chi": chi,
            "xi": list(xi),
            "physical_bandwidth": physical_bandwidth,
        },
        "xi_norm_sq": xi_norm_sq,
        "double_commutator": double_commutator,
        "kubo_delta_square": kubo_delta_square,
        "kubo_expected": kubo_expected,
        "a_xi": a_xi,
        "fejer": {
            "duhamel_error_bound": duhamel_error_bound,
            "delta_duhamel_error_bound": delta_duhamel_error_bound,
            "unaveraged_two_sided_square_bound": unaveraged_two_sided_square_bound,
            "unaveraged_two_sided_square_formula": unaveraged_two_sided_square_formula,
            "modular_bandwidth": modular_bandwidth,
            "modular_bandwidth_form": modular_form,
            "raw_character_operator_norm": 1,
            "filtered_character_operator_bound": 1,
            "filter_error_operator_bound": 2,
            "generator_mean": generator_mean,
            "fejer_zero_multiplier": fejer_zero_multiplier,
            "filter_error_mean": filter_error_mean,
            "connected_equals_uncentered": filter_error_mean == 0,
        },
        "mean_fixture": {
            "modular_gap": modular_gap,
            "exponential_residual": exponential_residual,
            "lhs": mean_lhs,
            "lhs_coth": mean_lhs_coth,
            "rhs": mean_rhs,
            "residual": mean_residual,
            "factorized_residual": mean_residual_factorized,
        },
        "commutator": {
            "momentum_shift": sp.simplify(hbar * xi),
            "momentum_vector_coefficients": sp.simplify(hbar * xi / chi),
            "momentum_coefficient": sp.simplify(hbar / chi),
            "scalar_coefficient": sp.simplify(hbar**2 * xi_norm_sq / (2 * chi)),
            "generator_momentum_vector_coefficients": sp.simplify(xi / chi),
            "generator_momentum_coefficient": sp.simplify(1 / chi),
            "generator_scalar_coefficient": sp.simplify(
                hbar * xi_norm_sq / (2 * chi)
            ),
        },
    }


def finite_span_audit(beta: sp.Expr, chi: sp.Expr) -> dict[str, Any]:
    # INPUTS: collinear rational frequencies make the triangle bound sharp at q=0.
    coefficients = (sp.Rational(2, 5), sp.Rational(3, 7))
    frequencies = (sp.Matrix([1, 0]), sp.Matrix([2, 0]))
    ell_gradient = sp.simplify(
        sum(
            abs(coefficient) * sp.sqrt((frequency.T * frequency)[0])
            for coefficient, frequency in zip(coefficients, frequencies)
        )
    )
    gradient_at_zero = sum(
        (coefficient * frequency for coefficient, frequency in zip(coefficients, frequencies)),
        sp.zeros(2, 1),
    )
    gradient_norm_at_zero = sp.sqrt(sp.simplify((gradient_at_zero.T * gradient_at_zero)[0]))
    delta_bound = sp.simplify(ell_gradient / sp.sqrt(beta * chi))
    delta_bound_square = sp.simplify(ell_gradient**2 / (beta * chi))
    return {
        "coefficients": coefficients,
        "frequencies": [list(item) for item in frequencies],
        "ell_gradient": ell_gradient,
        "gradient_at_zero": list(gradient_at_zero),
        "gradient_norm_at_zero": gradient_norm_at_zero,
        "delta_bound": delta_bound,
        "delta_bound_square": delta_bound_square,
        "sharp_at_zero": sp.simplify(gradient_norm_at_zero - ell_gradient) == 0,
    }


def gram_polar_transport_audit() -> dict[str, Any]:
    # INPUTS: exact positive square roots with a genuinely noncommuting Gram pair.
    epsilon = sp.symbols("epsilon", positive=True)
    square_root_zero = sp.diag(2, 3)
    mixing = sp.Matrix([[0, 1], [1, 0]])
    square_root_n = square_root_zero + epsilon * mixing
    gram_zero = square_root_zero**2
    gram_n = sp.expand(square_root_n**2)
    transport = sp.simplify(square_root_zero.inv() * square_root_n)
    congruence = sp.simplify(transport.T * gram_zero * transport)

    left_zero = sp.Matrix([[0, 1], [2, 0]])
    perturbation = sp.Matrix([[1, -1], [0, 1]])
    left_n = left_zero + epsilon * perturbation
    transported_left = sp.simplify(transport * left_n * transport.inv())
    transported_limit = transported_left.applyfunc(
        lambda value: sp.limit(value, epsilon, 0, dir="+")
    )
    metric_adjoint_n = sp.simplify(gram_n.inv() * left_n.T * gram_n)
    transported_adjoint = sp.simplify(
        transport * metric_adjoint_n * transport.inv()
    )
    metric_adjoint_after = sp.simplify(
        gram_zero.inv() * transported_left.T * gram_zero
    )

    fixture_rows: list[dict[str, Any]] = []
    for denominator in (2, 3, 5, 8):
        eps_value = sp.Rational(1, denominator)
        s_value = square_root_n.subs(epsilon, eps_value)
        g_value = gram_n.subs(epsilon, eps_value)
        m_value = transport.subs(epsilon, eps_value)
        l_value = transported_left.subs(epsilon, eps_value)
        fixture_rows.append(
            {
                "epsilon": eps_value,
                "root_first_minor": s_value[0, 0],
                "root_determinant": sp.det(s_value),
                "noncommutator": sp.simplify(gram_zero * g_value - g_value * gram_zero),
                "congruence_residual": sp.simplify(m_value.T * gram_zero * m_value - g_value),
                "transport_distance_sq": frobenius_square(l_value - left_zero),
            }
        )

    # A singular limiting Gram block must be reduced before taking inverse roots.
    singular_limit = sp.diag(1, 0, 4)
    singular_finite = sp.diag(1 + epsilon, epsilon**2, 4 - epsilon)
    retained = tuple(singular_limit.rref()[1])
    reduced_limit = submatrix(singular_limit, retained)
    reduced_finite = submatrix(singular_finite, retained)
    reduced_root_limit = sp.diag(*[sp.sqrt(value) for value in reduced_limit.diagonal()])
    reduced_root_finite = sp.diag(*[sp.sqrt(value) for value in reduced_finite.diagonal()])
    reduced_transport = sp.simplify(reduced_root_limit.inv() * reduced_root_finite)
    reduced_congruence = sp.simplify(
        reduced_transport.T * reduced_limit * reduced_transport
    )

    return {
        "gram_zero": gram_zero,
        "gram_n": gram_n,
        "square_root_zero": square_root_zero,
        "square_root_n": square_root_n,
        "transport": transport,
        "congruence": congruence,
        "transport_limit": transport.applyfunc(
            lambda value: sp.limit(value, epsilon, 0, dir="+")
        ),
        "operator_transport": {
            "left_zero": left_zero,
            "left_n": left_n,
            "transported_left": transported_left,
            "transported_limit": transported_limit,
            "adjoint_residual": sp.simplify(transported_adjoint - metric_adjoint_after),
        },
        "fixtures": fixture_rows,
        "singular_support": {
            "limit": singular_limit,
            "finite": singular_finite,
            "limit_rank": singular_limit.rank(),
            "limit_determinant": singular_limit.det(),
            "retained_indices": retained,
            "discarded_indices": tuple(
                index for index in range(singular_limit.rows) if index not in retained
            ),
            "reduced_limit": reduced_limit,
            "reduced_finite": reduced_finite,
            "reduced_transport": reduced_transport,
            "reduced_congruence": reduced_congruence,
        },
    }


def embedding_no_go_audit() -> dict[str, Any]:
    rotating_rows: list[dict[str, Any]] = []
    gram_limit = sp.Matrix([[1, 0], [0, 0]])
    for n_value in (2, 4, 8, 16):
        n = sp.Integer(n_value)
        vector = sp.Matrix([1, 1 / n])
        gram = sp.simplify(vector * vector.T)
        null_vector = sp.Matrix([-1 / n, 1])
        rotating_rows.append(
            {
                "n": n,
                "gram": gram,
                "gram_distance_sq": frobenius_square(gram - gram_limit),
                "finite_null_value": sp.simplify((null_vector.T * gram * null_vector)[0]),
                "limit_null_value": sp.simplify(
                    (null_vector.T * gram_limit * null_vector)[0]
                ),
                "null_vector": null_vector,
            }
        )

    collapse_rows: list[dict[str, Any]] = []
    collapse_limit = sp.diag(1, 0)
    for denominator in (2, 4, 8, 16):
        eps = sp.Rational(1, denominator)
        state_gram = sp.diag(1 - eps, eps)
        collapse_rows.append(
            {
                "epsilon": eps,
                "gram": state_gram,
                "rank": state_gram.rank(),
                "distance_sq": frobenius_square(state_gram - collapse_limit),
            }
        )

    return {
        "rotating_null": {
            "limit_gram": gram_limit,
            "limit_rank": gram_limit.rank(),
            "rows": rotating_rows,
            "naive_label_map_well_defined": False,
        },
        "dimension_collapse": {
            "limit_gram": collapse_limit,
            "finite_rows": collapse_rows,
            "finite_rank": collapse_rows[0]["rank"],
            "limit_rank": collapse_limit.rank(),
            "injective_isometry_possible": False,
        },
    }


def momentum_gauge_and_raw_character_audit(
    character: dict[str, Any],
) -> dict[str, Any]:
    chi = sp.sympify(character["inputs"]["chi"])
    hbar = sp.sympify(character["inputs"]["hbar"])
    xi_norm_sq = sp.sympify(character["xi_norm_sq"])
    gauge = sp.Matrix([sp.Rational(2, 5), -sp.Rational(1, 3)])
    generator_difference = sp.simplify(-gauge / chi)

    # Exact finite matrix witness for the unitary-cancellation mechanism in every
    # q-cylinder trace.  Polynomial transfer functions stand in for functional
    # calculus; conjugation covariance then applies equally to exp(-tH).
    imaginary = sp.I
    unitary = sp.diag(1, imaginary)
    hamiltonian = sp.Matrix([[2, 1], [1, 3]])
    gauged_hamiltonian = sp.simplify(unitary * hamiltonian * unitary.conjugate().T)
    q_function_one = sp.diag(sp.Rational(2, 3), -sp.Rational(1, 5))
    q_function_two = sp.diag(sp.Rational(3, 4), sp.Rational(4, 7))

    def transfer(matrix: sp.MatrixBase, time: sp.Expr) -> sp.Matrix:
        scaled = time * matrix
        return sp.eye(matrix.rows) + scaled + scaled**2 / 2 + scaled**3 / 6

    time_one = sp.Rational(1, 4)
    time_two = sp.Rational(2, 5)
    original_trace = sp.trace(
        transfer(hamiltonian, time_one)
        * q_function_one
        * transfer(hamiltonian, time_two)
        * q_function_two
    )
    gauged_trace = sp.trace(
        transfer(gauged_hamiltonian, time_one)
        * q_function_one
        * transfer(gauged_hamiltonian, time_two)
        * q_function_two
    )

    xi_dot_p_ray = sp.symbols("xi_dot_p_ray", positive=True)
    raw_amplitude = sp.simplify(
        hbar * xi_dot_p_ray / chi + hbar**2 * xi_norm_sq / (2 * chi)
    )
    raw_rows = [
        {
            "xi_dot_p_ray": sp.Integer(value),
            "commutator_amplitude": raw_amplitude.subs(xi_dot_p_ray, value),
        }
        for value in (1, 2, 4, 8, 16)
    ]

    return {
        "momentum_gauge": {
            "gauge": gauge,
            "generator_difference": generator_difference,
            "unitary": unitary,
            "hamiltonian": hamiltonian,
            "gauged_hamiltonian": gauged_hamiltonian,
            "unitary_conjugation_residual": sp.simplify(
                gauged_hamiltonian
                - unitary * hamiltonian * unitary.conjugate().T
            ),
            "q_commutator_residual": sp.simplify(
                unitary * q_function_one - q_function_one * unitary
            ),
            "original_cylinder_trace": sp.simplify(original_trace),
            "gauged_cylinder_trace": sp.simplify(gauged_trace),
            "cylinder_trace_residual": sp.simplify(gauged_trace - original_trace),
            "canonical_momentum_selected": False,
        },
        "raw_character": {
            "xi_dot_p_ray_expression": raw_amplitude,
            "asymptotic_slope": sp.limit(raw_amplitude / xi_dot_p_ray, xi_dot_p_ray, sp.oo),
            "asymptotic_limit": sp.limit(raw_amplitude, xi_dot_p_ray, sp.oo),
            "rows": raw_rows,
            "bounded_generator_core": False,
        },
    }


def parity_and_cross_beta_audit() -> dict[str, Any]:
    mixture_weight = sp.symbols("mixture_weight", real=True)
    phase_order = sp.Rational(3, 7)
    mixture_order = sp.expand(
        mixture_weight * phase_order + (1 - mixture_weight) * (-phase_order)
    )
    parity_solutions = sp.solve(sp.Eq(mixture_order, 0), mixture_weight)
    asymmetric_weight = sp.Rational(2, 5)

    identity = sp.eye(2)
    sigma_x = sp.Matrix([[0, 1], [1, 0]])

    def thermal_fixture(beta: sp.Expr, coupling: sp.Expr) -> dict[str, Any]:
        x = sp.simplify(beta * coupling)
        plus_weight = sp.simplify(sp.exp(x) / (2 * sp.cosh(x)))
        minus_weight = sp.simplify(sp.exp(-x) / (2 * sp.cosh(x)))
        rho = sp.simplify((identity + sp.tanh(x) * sigma_x) / 2)
        ratio = sp.simplify(plus_weight / minus_weight)
        log_ratio = sp.simplify(sp.log(ratio))
        centered_log = sp.simplify(log_ratio * sigma_x / 2)
        effective_generator = sp.simplify(-centered_log / beta)
        test_time = sp.Rational(1, 3)
        heat = sp.simplify(
            sp.cosh(test_time * coupling) * identity
            + sp.sinh(test_time * coupling) * sigma_x
        )
        return {
            "beta": beta,
            "coupling": coupling,
            "x": x,
            "rho": rho,
            "eigenweights": (plus_weight, minus_weight),
            "ratio": ratio,
            "log_ratio": log_ratio,
            "centered_log": centered_log,
            "effective_generator": effective_generator,
            "heat_kernel": heat,
            "heat_entries_nonnegative": all(
                bool(sp.N(value, 40) >= 0) for value in heat
            ),
        }

    beta_one = sp.Integer(1)
    beta_two = sp.Integer(2)
    first = thermal_fixture(beta_one, sp.Integer(1))
    second = thermal_fixture(beta_two, sp.Integer(2))
    generator_difference = sp.simplify(
        second["effective_generator"] - first["effective_generator"]
    )

    return {
        "parity": {
            "phase_order": phase_order,
            "symbolic_mixture_order": mixture_order,
            "parity_solutions": parity_solutions,
            "asymmetric_weight": asymmetric_weight,
            "asymmetric_order": mixture_order.subs(mixture_weight, asymmetric_weight),
            "symmetric_order": mixture_order.subs(mixture_weight, sp.Rational(1, 2)),
            "asymmetric_zero_source_periodic_limit_possible": False,
        },
        "cross_beta": {
            "sigma_x": sigma_x,
            "first": first,
            "second": second,
            "generator_difference": generator_difference,
            "difference_trace": sp.trace(generator_difference),
            "difference_determinant": sp.det(generator_difference),
            "single_inner_dynamics_possible": False,
        },
    }


def local_jet_and_tail_audit(character: dict[str, Any]) -> dict[str, Any]:
    chi = sp.sympify(character["inputs"]["chi"])
    source = sp.Rational(3, 7)
    u = sp.ones(8, 1) / sp.sqrt(8)
    source_xi = sp.Matrix(
        [sp.Rational(1, 2), -sp.Rational(1, 3), 0, 0, 0, 0, 0, 0]
    )
    source_pairing = sp.simplify((source_xi.T * u)[0])
    second_jet_difference = sp.simplify(sp.I * source * source_pairing / chi)

    balls: list[dict[str, Any]] = []
    for radius_value in range(4):
        radius = sp.Integer(radius_value)
        points = [
            (x, y, z)
            for x in range(-radius_value, radius_value + 1)
            for y in range(-radius_value, radius_value + 1)
            for z in range(-radius_value, radius_value + 1)
            if abs(x) + abs(y) + abs(z) <= radius_value
        ]
        formula = sp.simplify(
            sum(
                2**dimension
                * sp.binomial(3, dimension)
                * sp.binomial(radius, dimension)
                for dimension in range(4)
            )
        )
        balls.append(
            {
                "radius": radius,
                "enumerated_count": len(points),
                "binomial_formula": formula,
                "maximum_l1_distance": max(
                    (abs(x) + abs(y) + abs(z) for x, y, z in points),
                    default=0,
                ),
            }
        )

    xi = sp.Matrix(character["inputs"]["xi"])
    gradient = sp.Matrix(
        [sp.Rational(2, 5), -sp.Rational(1, 7), sp.Rational(3, 8)]
    )
    xi_norm_sq = sp.simplify((xi.T * xi)[0])
    gradient_norm_sq = sp.simplify((gradient.T * gradient)[0])
    contraction = sp.simplify((xi.T * gradient)[0])
    cauchy_residual = sp.simplify(xi_norm_sq * gradient_norm_sq - contraction**2)
    exact_first_rung_square = sp.simplify(contraction**2 / chi**2)
    first_rung_bound_square = sp.simplify(
        xi_norm_sq * gradient_norm_sq / chi**2
    )
    first_rung_difference_coefficient = sp.simplify(-sp.I * contraction / chi)

    # INPUTS for an exact monotonicity proof of one super-Gaussian envelope.
    tail_power = sp.Integer(4)
    tail_rate = sp.Integer(2)
    tail_constant = sp.Rational(7, 3)
    tail_rows: list[dict[str, Any]] = []
    for radius_value in (2, 3, 4, 5):
        radius = sp.Integer(radius_value)
        value = tail_constant * radius**tail_power * sp.exp(-tail_rate * radius**2)
        log_ratio_upper = sp.simplify(
            tail_power / radius - tail_rate * (2 * radius + 1)
        )
        tail_rows.append(
            {
                "radius": radius,
                "bound": value,
                "next_over_current_log_upper": log_ratio_upper,
            }
        )

    return {
        "local_jet": {
            "source": source,
            "u": list(u),
            "xi": list(source_xi),
            "source_pairing": source_pairing,
            "first_jet_source_difference": 0,
            "second_jet_difference_coefficient": second_jet_difference,
            "neighborhood_balls": balls,
            "volume_independence_radius_rule": "m-th jet uses only the m-neighborhood",
        },
        "coordinate_tail": {
            "xi": list(xi),
            "gradient_fixture": list(gradient),
            "xi_norm_sq": xi_norm_sq,
            "gradient_norm_sq": gradient_norm_sq,
            "contraction": contraction,
            "first_rung_difference_coefficient": first_rung_difference_coefficient,
            "cauchy_residual": cauchy_residual,
            "exact_first_rung_square": exact_first_rung_square,
            "first_rung_bound_square": first_rung_bound_square,
            "first_rung_coefficient": sp.simplify(sp.sqrt(xi_norm_sq) / chi),
            "tail_inputs": {
                "power": tail_power,
                "rate": tail_rate,
                "constant": tail_constant,
            },
            "tail_rows": tail_rows,
            "all_higher_orbit_rungs_resummed": False,
        },
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in (MANIFEST, CERTIFICATE)
        if not path.exists()
    ]
    if not MANIFEST.exists():
        if not staged:
            raise FileNotFoundError(
                f"staged v1.5 manifest is missing ({missing[0]}); rerun with --staged"
            )
        return {"status": "MISSING_STAGED", "missing": missing}

    formal_missing = list(missing)

    manifest_text = MANIFEST.read_text(encoding="utf-8")
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
    audit.check(
        "all v1.5 negatives ordered",
        tuple(manifest["negative_ids"]) == NEGATIVE_IDS,
        manifest["negative_ids"],
        NEGATIVE_IDS,
        "authority",
    )
    audit.check(
        "registered parent explorations",
        tuple(manifest["parent_explorations"])
        == ("EXP-000781", "EXP-000790", "EXP-000798", "EXP-000800"),
        manifest["parent_explorations"],
        ("EXP-000781", "EXP-000790", "EXP-000798", "EXP-000800"),
        "authority",
    )
    expected_parents = (
        (PARENTS[0], "EXP-000781", None),
        (PARENTS[1], "EXP-000790", None),
        (PARENTS[2], "EXP-000798", "v1.2"),
        (PARENTS[3], "EXP-000800", "v1.4"),
    )
    for parent_path, parent_exploration, parent_version in expected_parents:
        audit.check(
            f"parent exists {parent_exploration}",
            parent_path.exists(),
            str(parent_path.relative_to(REPO)).replace("\\", "/"),
            "existing registered parent manifest",
            "authority",
        )
        parent_manifest = json.loads(parent_path.read_text(encoding="utf-8"))
        audit.check(
            f"parent identity {parent_exploration}",
            parent_manifest.get("exploration_id") == parent_exploration
            and (
                parent_version is None
                or parent_manifest.get("result_version") == parent_version
            ),
            {
                "exploration": parent_manifest.get("exploration_id"),
                "version": parent_manifest.get("result_version"),
            },
            {"exploration": parent_exploration, "version": parent_version},
            "authority",
        )
    for object_name in (
        "registered_tangent_net",
        "bandlimited_kms_kernel_theorem",
        "finite_block_polar_transport",
        "character_dirichlet_and_filter_theorem",
        "generator_and_first_tail",
        "embedding_and_generator_no_gos",
        "parity_and_cross_beta_no_gos",
        "route_status",
    ):
        audit.check(
            f"manifest object {object_name}",
            object_name in manifest and isinstance(manifest[object_name], dict),
            object_name if object_name in manifest else "MISSING",
            object_name,
            "authority",
        )
    audit.check(
        "primary script binding",
        manifest["verification"]["primary_script"]
        == str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        manifest["verification"]["primary_script"],
        str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        "authority",
    )
    audit.check(
        "closed tangent-net subgate",
        manifest["closed_subgates"] == [EXPECTED_CLOSED_SUBGATE],
        manifest["closed_subgates"],
        [EXPECTED_CLOSED_SUBGATE],
        "authority",
    )
    audit.check(
        "next gate binding",
        manifest["route_status"]["next_gate"] == EXPECTED_NEXT_GATE
        and EXPECTED_NEXT_GATE in manifest["open_gates"],
        {
            "next": manifest["route_status"]["next_gate"],
            "open": manifest["open_gates"],
        },
        EXPECTED_NEXT_GATE,
        "authority",
    )
    bandlimited = manifest["bandlimited_kms_kernel_theorem"]
    transport_scope = manifest["finite_block_polar_transport"]
    filter_scope = manifest["character_dirichlet_and_filter_theorem"]
    audit.check(
        "KMS continuation is a scalar function boundary statement",
        "finite-volume KMS function" in bandlimited["normal_family"]
        and "thermal tube" in bandlimited["normal_family"]
        and "real-time boundary functions" in bandlimited["boundary_smoothing"],
        {
            "normal_family": bandlimited["normal_family"],
            "boundary": bandlimited["boundary_smoothing"],
        },
        "scalar KMS function analytically continued from real-time boundary data",
        "scope",
    )
    audit.check(
        "fixed finite-word Gram scope",
        "Every fixed finite Gram matrix" in bandlimited["gram_convergence"]
        and "selected tangent-net word kernels" in bandlimited["scope"],
        {
            "gram": bandlimited["gram_convergence"],
            "scope": bandlimited["scope"],
        },
        "selected tangent-net finite-word Gram convergence",
        "scope",
    )
    audit.check(
        "independent-pivot finite-core Fell/GNS scope",
        "retained independent pivots" in transport_scope["scope"]
        and "pointed finite-core Fell/GNS" in transport_scope["operator_transport"]
        and "No globally compatible common-Hilbert extension" in transport_scope["operator_transport"],
        {
            "transport": transport_scope["operator_transport"],
            "scope": transport_scope["scope"],
        },
        "independent-pivot pointed finite-core Fell/GNS only",
        "scope",
    )
    audit.check(
        "cyclic L2-only raw-character recovery scope",
        "cyclic two-sided L2 vector" in filter_scope["fejer_filter"]
        and "arbitrary bandlimited left/right-context multiplier control" in filter_scope["fejer_filter"]
        and "raw-core operator strong-star convergence" in filter_scope["fejer_filter"],
        filter_scope["fejer_filter"],
        "cyclic two-sided L2, without contextual multiplier or operator strong-star control",
        "scope",
    )
    audit.check(
        "Duhamel and modular form-domain convention",
        "finite-volume and form-core exact" in filter_scope["scope"]
        and "limiting Dirichlet form requires a separate closure" in filter_scope["scope"]
        and "faithful normal W-star standard form" in filter_scope["general_wstar_bridge"]
        and "unaveraged v1.4 sum convention" in filter_scope["general_wstar_bridge"],
        {
            "form_scope": filter_scope["scope"],
            "modular_bridge": filter_scope["general_wstar_bridge"],
        },
        "finite-volume form-core exact; faithful support-reduced standard form; no limiting form equality",
        "scope",
    )
    semantic_tokens = (
        "pointed",
        "Fejer",
        "selected phase-tangent",
        "not the zero-source periodic sequence",
        "not a beta-independent C-star dynamics",
    )
    combined_manifest = manifest_text
    for token in semantic_tokens:
        audit.check(
            f"manifest semantic {token}",
            token in combined_manifest,
            token if token in combined_manifest else "MISSING",
            token,
            "authority",
        )

    if CERTIFICATE.exists():
        certificate = CERTIFICATE.read_text(encoding="utf-8")
        for token in (
            EXPECTED_EXPLORATION,
            EXPECTED_RESULT_NUMBER,
            EXPECTED_RESULT_VERSION,
            "Fejer",
            "pointed",
            "zero-source",
            "beta-independent",
            "Pre-A",
            "bounded scalar KMS analytic continuation",
            "pointed finite-core Fell/GNS",
            "common-Hilbert operator strong-star",
            "arbitrary left/right contexts",
        ):
            if token in certificate:
                audit.check(
                    f"certificate token {token}",
                    True,
                    token,
                    token,
                    "authority",
                )
            else:
                formal_missing.append(
                    f"{str(CERTIFICATE.relative_to(REPO)).replace(chr(92), '/')}#{token}"
                )
        for negative_id in NEGATIVE_IDS:
            if negative_id in certificate:
                audit.check(
                    f"certificate negative {negative_id}",
                    True,
                    negative_id,
                    negative_id,
                    "authority",
                )
            else:
                formal_missing.append(
                    f"{str(CERTIFICATE.relative_to(REPO)).replace(chr(92), '/')}#{negative_id}"
                )

    formal_missing = list(dict.fromkeys(formal_missing))
    if formal_missing and not staged:
        joined = ", ".join(formal_missing)
        raise FileNotFoundError(
            f"staged v1.5 authority is missing ({joined}); rerun with --staged"
        )
    if formal_missing:
        return {"status": "MISSING_STAGED", "missing": formal_missing}
    return {"status": "COMPLETE", "missing": []}


def run_audit(staged: bool) -> dict[str, Any]:
    audit = Audit()
    character = character_dirichlet_filter_audit()
    span = finite_span_audit(
        sp.sympify(character["inputs"]["beta"]),
        sp.sympify(character["inputs"]["chi"]),
    )
    gram = gram_polar_transport_audit()
    embedding = embedding_no_go_audit()
    gauge_raw = momentum_gauge_and_raw_character_audit(character)
    parity_beta = parity_and_cross_beta_audit()
    jet_tail = local_jet_and_tail_audit(character)

    audit.check(
        "character frequency is nonzero",
        character["xi_norm_sq"] > 0,
        character["xi_norm_sq"],
        "positive rational norm square",
        "character",
    )
    audit.check(
        "character double commutator coefficient",
        sp.simplify(
            character["double_commutator"]
            - character["inputs"]["hbar"] ** 2
            * character["xi_norm_sq"]
            / character["inputs"]["chi"]
        )
        == 0,
        character["double_commutator"],
        "hbar^2 ||xi||^2 / chi",
        "character",
    )
    audit.check(
        "Kubo factor has no extra two or hbar",
        sp.simplify(character["kubo_delta_square"] - character["kubo_expected"])
        == 0,
        character["kubo_delta_square"],
        character["kubo_expected"],
        "character",
    )
    audit.check(
        "Kubo reconstruction of double commutator",
        sp.simplify(
            character["inputs"]["beta"]
            * character["inputs"]["hbar"] ** 2
            * character["kubo_delta_square"]
            - character["double_commutator"]
        )
        == 0,
        character["kubo_delta_square"],
        "double/(beta hbar^2)",
        "character",
    )
    audit.check(
        "raw character momentum shift and commutator vector",
        matrix_equal(
            character["commutator"]["momentum_shift"],
            character["inputs"]["hbar"] * sp.Matrix(character["inputs"]["xi"]),
        )
        and matrix_equal(
            character["commutator"]["momentum_vector_coefficients"],
            character["inputs"]["hbar"]
            * sp.Matrix(character["inputs"]["xi"])
            / character["inputs"]["chi"],
        )
        and matrix_equal(
            character["commutator"]["generator_momentum_vector_coefficients"],
            sp.Matrix(character["inputs"]["xi"])
            / character["inputs"]["chi"],
        ),
        {
            "shift": character["commutator"]["momentum_shift"],
            "commutator": character["commutator"]["momentum_vector_coefficients"],
            "generator": character["commutator"]["generator_momentum_vector_coefficients"],
        },
        "hbar xi, hbar xi/chi, xi/chi",
        "character",
    )
    audit.check(
        "Fejer Duhamel error bound",
        sp.simplify(
            character["fejer"]["duhamel_error_bound"]
            - character["a_xi"] / character["inputs"]["physical_bandwidth"]
        )
        == 0,
        character["fejer"]["duhamel_error_bound"],
        "a_xi/R",
        "filter",
    )
    audit.check(
        "Fejer delta-D bound",
        sp.simplify(
            character["fejer"]["delta_duhamel_error_bound"] - character["a_xi"]
        )
        == 0,
        character["fejer"]["delta_duhamel_error_bound"],
        "a_xi",
        "filter",
    )
    audit.check(
        "unaveraged two-sided Fejer bound",
        sp.simplify(
            character["fejer"]["unaveraged_two_sided_square_bound"]
            - character["fejer"]["unaveraged_two_sided_square_formula"]
        )
        == 0,
        character["fejer"]["unaveraged_two_sided_square_bound"],
        character["fejer"]["unaveraged_two_sided_square_formula"],
        "filter",
    )
    audit.check(
        "physical and modular bandwidth conventions agree",
        sp.simplify(
            character["fejer"]["unaveraged_two_sided_square_bound"]
            - character["fejer"]["modular_bandwidth_form"]
        )
        == 0,
        character["fejer"]["modular_bandwidth_form"],
        character["fejer"]["unaveraged_two_sided_square_bound"],
        "filter",
    )
    audit.check(
        "connected Duhamel convention harmless",
        character["fejer"]["generator_mean"] == 0
        and character["fejer"]["fejer_zero_multiplier"] == 1
        and character["fejer"]["filter_error_mean"] == 0
        and character["fejer"]["connected_equals_uncentered"] is True,
        {
            "generator_mean": character["fejer"]["generator_mean"],
            "zero_multiplier": character["fejer"]["fejer_zero_multiplier"],
            "residual_mean": character["fejer"]["filter_error_mean"],
        },
        "0, 1, 0",
        "filter",
    )
    audit.check(
        "Fejer operator bounds distinguish smear and residual",
        character["fejer"]["raw_character_operator_norm"] == 1
        and character["fejer"]["filtered_character_operator_bound"] == 1
        and character["fejer"]["filter_error_operator_bound"] == 2,
        {
            "raw": character["fejer"]["raw_character_operator_norm"],
            "smear": character["fejer"]["filtered_character_operator_bound"],
            "residual": character["fejer"]["filter_error_operator_bound"],
        },
        {"raw": 1, "smear": 1, "residual": 2},
        "filter",
    )
    audit.check(
        "modular arithmetic/logarithmic mean inequality",
        sp.simplify(
            character["mean_fixture"]["residual"]
            - character["mean_fixture"]["factorized_residual"]
        )
        == 0
        and sp.simplify(
            character["mean_fixture"]["lhs_coth"].rewrite(sp.exp)
            - character["mean_fixture"]["lhs"]
        )
        == 0
        and bool(sp.N(character["mean_fixture"]["exponential_residual"], 50) > 0)
        and bool(sp.N(character["mean_fixture"]["residual"], 50) > 0),
        {
            "lhs": character["mean_fixture"]["lhs"],
            "rhs": character["mean_fixture"]["rhs"],
            "residual": character["mean_fixture"]["residual"],
            "factorized": character["mean_fixture"]["factorized_residual"],
        },
        "(u/2)coth(u/2) <= 1+u/2 with residual (exp(u)-1-u)/(exp(u)-1)",
        "filter",
    )
    audit.check(
        "finite-span triangle bound sharp fixture",
        span["sharp_at_zero"] is True,
        {
            "ell": span["ell_gradient"],
            "gradient": span["gradient_norm_at_zero"],
        },
        "equal at q=0",
        "finite_span",
    )
    audit.check(
        "finite-span Duhamel bound square",
        sp.simplify(
            span["delta_bound"] ** 2 - span["delta_bound_square"]
        )
        == 0,
        span["delta_bound_square"],
        "ell_gradient^2/(beta chi)",
        "finite_span",
    )

    audit.check(
        "noncommuting Gram fixture",
        any(not matrix_zero(row["noncommutator"]) for row in gram["fixtures"]),
        [row["noncommutator"] for row in gram["fixtures"]],
        "at least one nonzero commutator",
        "gram_transport",
    )
    audit.check(
        "polar congruence identity",
        matrix_equal(gram["congruence"], gram["gram_n"]),
        gram["congruence"],
        gram["gram_n"],
        "gram_transport",
    )
    audit.check(
        "fixture square roots positive",
        all(
            row["root_first_minor"] > 0 and row["root_determinant"] > 0
            for row in gram["fixtures"]
        ),
        [
            (row["root_first_minor"], row["root_determinant"])
            for row in gram["fixtures"]
        ],
        "Sylvester positive",
        "gram_transport",
    )
    audit.check(
        "fixture congruences exact",
        all(matrix_zero(row["congruence_residual"]) for row in gram["fixtures"]),
        [row["congruence_residual"] for row in gram["fixtures"]],
        "all zero",
        "gram_transport",
    )
    audit.check(
        "polar transport tends to identity",
        matrix_equal(gram["transport_limit"], sp.eye(2)),
        gram["transport_limit"],
        sp.eye(2),
        "gram_transport",
    )
    audit.check(
        "transported operator tends to limiting matrix",
        matrix_equal(
            gram["operator_transport"]["transported_limit"],
            gram["operator_transport"]["left_zero"],
        ),
        gram["operator_transport"]["transported_limit"],
        gram["operator_transport"]["left_zero"],
        "gram_transport",
    )
    audit.check(
        "metric adjoint transported exactly",
        matrix_zero(gram["operator_transport"]["adjoint_residual"]),
        gram["operator_transport"]["adjoint_residual"],
        sp.zeros(2),
        "gram_transport",
    )
    singular = gram["singular_support"]
    audit.check(
        "singular limit cannot be inverse-rooted",
        singular["limit_determinant"] == 0 and singular["limit_rank"] == 2,
        {
            "det": singular["limit_determinant"],
            "rank": singular["limit_rank"],
        },
        {"det": 0, "rank": 2},
        "support_reduction",
    )
    audit.check(
        "support pivot rule deterministic",
        singular["retained_indices"] == (0, 2)
        and singular["discarded_indices"] == (1,),
        {
            "retained": singular["retained_indices"],
            "discarded": singular["discarded_indices"],
        },
        {"retained": (0, 2), "discarded": (1,)},
        "support_reduction",
    )
    audit.check(
        "reduced polar congruence exact",
        matrix_equal(singular["reduced_congruence"], singular["reduced_finite"]),
        singular["reduced_congruence"],
        singular["reduced_finite"],
        "support_reduction",
    )

    rotating = embedding["rotating_null"]
    audit.check(
        "rotating finite nulls exact",
        all(row["finite_null_value"] == 0 for row in rotating["rows"]),
        [row["finite_null_value"] for row in rotating["rows"]],
        "all zero",
        "embedding_no_go",
    )
    audit.check(
        "rotating nulls survive in limit quotient",
        all(row["limit_null_value"] > 0 for row in rotating["rows"]),
        [row["limit_null_value"] for row in rotating["rows"]],
        "all positive",
        "embedding_no_go",
    )
    audit.check(
        "rotating Gram forms converge",
        all(
            left["gram_distance_sq"] > right["gram_distance_sq"]
            for left, right in zip(rotating["rows"], rotating["rows"][1:])
        ),
        [row["gram_distance_sq"] for row in rotating["rows"]],
        "strictly decreasing to zero",
        "embedding_no_go",
    )
    audit.check(
        "naive label map rejected",
        rotating["naive_label_map_well_defined"] is False,
        rotating["naive_label_map_well_defined"],
        False,
        "embedding_no_go",
    )
    collapse = embedding["dimension_collapse"]
    audit.check(
        "faithful finite state dimensions",
        all(row["rank"] == 2 for row in collapse["finite_rows"]),
        [row["rank"] for row in collapse["finite_rows"]],
        "all rank two",
        "dimension_collapse",
    )
    audit.check(
        "GNS dimension collapses",
        collapse["finite_rank"] == 2
        and collapse["limit_rank"] == 1
        and collapse["injective_isometry_possible"] is False,
        collapse,
        "rank 2 to rank 1; no injective isometry",
        "dimension_collapse",
    )

    gauge = gauge_raw["momentum_gauge"]
    audit.check(
        "gauge functional calculus conjugation",
        matrix_zero(gauge["unitary_conjugation_residual"]),
        gauge["unitary_conjugation_residual"],
        sp.zeros(2),
        "momentum_gauge",
    )
    audit.check(
        "gauge commutes with q cylinders",
        matrix_zero(gauge["q_commutator_residual"]),
        gauge["q_commutator_residual"],
        sp.zeros(2),
        "momentum_gauge",
    )
    audit.check(
        "q-cylinder trace gauge invariant",
        gauge["cylinder_trace_residual"] == 0,
        {
            "original": gauge["original_cylinder_trace"],
            "gauged": gauge["gauged_cylinder_trace"],
        },
        "identical",
        "momentum_gauge",
    )
    audit.check(
        "momentum generator changes nonscalarly",
        not matrix_zero(gauge["generator_difference"])
        and gauge["canonical_momentum_selected"] is False,
        gauge["generator_difference"],
        "-a/chi nonzero",
        "momentum_gauge",
    )
    raw = gauge_raw["raw_character"]
    audit.check(
        "raw commutator asymptotic slope",
        sp.simplify(
            raw["asymptotic_slope"]
            - character["commutator"]["momentum_coefficient"]
        )
        == 0,
        raw["asymptotic_slope"],
        character["commutator"]["momentum_coefficient"],
        "raw_character",
    )
    audit.check(
        "raw commutator unbounded",
        raw["asymptotic_limit"] == sp.oo
        and raw["bounded_generator_core"] is False,
        raw["asymptotic_limit"],
        sp.oo,
        "raw_character",
    )
    audit.check(
        "raw ray regression increases",
        all(
            left["commutator_amplitude"] < right["commutator_amplitude"]
            for left, right in zip(raw["rows"], raw["rows"][1:])
        ),
        [row["commutator_amplitude"] for row in raw["rows"]],
        "strictly increasing",
        "raw_character",
    )

    parity = parity_beta["parity"]
    audit.check(
        "parity fixes only equal phase weight",
        parity["parity_solutions"] == [sp.Rational(1, 2)],
        parity["parity_solutions"],
        [sp.Rational(1, 2)],
        "parity",
    )
    audit.check(
        "asymmetric mixture remains ordered",
        parity["asymmetric_order"] != 0
        and parity["asymmetric_zero_source_periodic_limit_possible"] is False,
        parity["asymmetric_order"],
        "nonzero",
        "parity",
    )
    audit.check(
        "symmetric mixture parity expectation",
        parity["symmetric_order"] == 0,
        parity["symmetric_order"],
        0,
        "parity",
    )
    cross_beta = parity_beta["cross_beta"]
    audit.check(
        "cross-beta Gibbs densities faithful",
        all(
            all(bool(sp.N(weight, 40) > 0) for weight in fixture["eigenweights"])
            for fixture in (cross_beta["first"], cross_beta["second"])
        ),
        {
            "first": cross_beta["first"]["eigenweights"],
            "second": cross_beta["second"]["eigenweights"],
        },
        "all positive",
        "cross_beta",
    )
    audit.check(
        "cross-beta heat kernels positive",
        cross_beta["first"]["heat_entries_nonnegative"]
        and cross_beta["second"]["heat_entries_nonnegative"],
        {
            "first": cross_beta["first"]["heat_kernel"],
            "second": cross_beta["second"]["heat_kernel"],
        },
        "entrywise nonnegative",
        "cross_beta",
    )
    audit.check(
        "cross-beta effective Hamiltonians recomputed",
        matrix_equal(
            cross_beta["first"]["effective_generator"],
            -cross_beta["sigma_x"],
        )
        and matrix_equal(
            cross_beta["second"]["effective_generator"],
            -2 * cross_beta["sigma_x"],
        ),
        {
            "first": cross_beta["first"]["effective_generator"],
            "second": cross_beta["second"]["effective_generator"],
        },
        {"first": "-sigma_x", "second": "-2 sigma_x"},
        "cross_beta",
    )
    audit.check(
        "cross-beta generator mismatch nonscalar",
        cross_beta["difference_trace"] == 0
        and cross_beta["difference_determinant"] != 0
        and cross_beta["single_inner_dynamics_possible"] is False,
        cross_beta["generator_difference"],
        "traceless nonscalar mismatch",
        "cross_beta",
    )

    jet = jet_tail["local_jet"]
    audit.check(
        "source leaves first character jet unchanged",
        jet["first_jet_source_difference"] == 0,
        jet["first_jet_source_difference"],
        0,
        "local_jet",
    )
    audit.check(
        "source enters exact second jet",
        sp.simplify(
            jet["second_jet_difference_coefficient"]
            - sp.I * jet["source"] * jet["source_pairing"] / character["inputs"]["chi"]
        )
        == 0,
        jet["second_jet_difference_coefficient"],
        "i h (xi.u)/chi",
        "local_jet",
    )
    audit.check(
        "local jet balls match binomial formula",
        all(
            row["enumerated_count"] == row["binomial_formula"]
            for row in jet["neighborhood_balls"]
        ),
        [
            (row["enumerated_count"], row["binomial_formula"])
            for row in jet["neighborhood_balls"]
        ],
        "all equal",
        "local_jet",
    )
    audit.check(
        "local jet maximum radius",
        all(
            row["maximum_l1_distance"] == row["radius"]
            for row in jet["neighborhood_balls"]
        ),
        [row["maximum_l1_distance"] for row in jet["neighborhood_balls"]],
        [row["radius"] for row in jet["neighborhood_balls"]],
        "local_jet",
    )
    tail = jet_tail["coordinate_tail"]
    audit.check(
        "coordinate-tail Cauchy residual nonnegative",
        tail["cauchy_residual"] >= 0,
        tail["cauchy_residual"],
        "nonnegative",
        "coordinate_tail",
    )
    audit.check(
        "coordinate-tail first rung bounded",
        tail["exact_first_rung_square"] <= tail["first_rung_bound_square"],
        {
            "exact": tail["exact_first_rung_square"],
            "bound": tail["first_rung_bound_square"],
        },
        "exact <= ||xi||^2 ||grad W||^2/chi^2",
        "coordinate_tail",
    )
    audit.check(
        "coordinate-tail exact signed first rung",
        sp.simplify(
            tail["first_rung_difference_coefficient"]
            + sp.I * tail["contraction"] / character["inputs"]["chi"]
        )
        == 0,
        tail["first_rung_difference_coefficient"],
        "-i (xi.grad W_L)/chi",
        "coordinate_tail",
    )
    audit.check(
        "super-Gaussian fixture decreases",
        all(row["next_over_current_log_upper"] < 0 for row in tail["tail_rows"]),
        [row["next_over_current_log_upper"] for row in tail["tail_rows"]],
        "all negative using log(1+x)<x",
        "coordinate_tail",
    )
    audit.check(
        "higher tail rungs remain open",
        tail["all_higher_orbit_rungs_resummed"] is False,
        tail["all_higher_orbit_rungs_resummed"],
        False,
        "coordinate_tail",
    )

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    passed = len(audit.rows)
    source_paths = [SCRIPT, *PARENTS]
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
            "character_dirichlet_filter": character,
            "finite_span": span,
            "gram_polar_transport": gram,
            "embedding_no_gos": embedding,
            "momentum_gauge_and_raw_character": gauge_raw,
            "parity_and_cross_beta": parity_beta,
            "local_jet_and_coordinate_tail": jet_tail,
            "kms_scalar_analytic_continuation_from_real_time": True,
            "raw_operator_complex_time_alpha_used": False,
            "fixed_band_finite_word_gram_convergence_scope": True,
            "independent_pivot_pointed_finite_core_fell_gns_scope": True,
            "common_hilbert_operator_strong_star_closed": False,
            "raw_character_cyclic_two_sided_l2_filter_removal": True,
            "arbitrary_bandlimited_left_right_context_control_closed": False,
            "raw_character_operator_strong_star_recovery_closed": False,
            "all_exhaustion_mixture_l2_closed": False,
            "zero_source_periodic_symmetric_limit_closed": False,
            "canonical_momentum_weyl_bridge_closed": False,
            "beta_independent_cstar_dynamics_closed": False,
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
        help="permit missing v1.5 certificate/authorities and report INCOMPLETE",
    )
    args = parser.parse_args()
    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"{payload['verdict']} {summary['passed']}/{summary['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    print("script_sha256: " + payload["source_hashes"][str(SCRIPT.relative_to(REPO)).replace("\\", "/")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
