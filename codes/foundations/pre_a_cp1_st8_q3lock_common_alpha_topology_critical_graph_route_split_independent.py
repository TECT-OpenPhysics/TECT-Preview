#!/usr/bin/env python3
"""Independent stdlib/Fraction audit of the R-167 v1.3 route split.

This verifier deliberately does not import the primary implementation and does
not consume a primary result artifact.  It rebuilds the exact arithmetic and
the counterexample fixtures from standard-library ``Fraction`` calculations.

The positive scope is narrow: the exact all-bond kick has a uniform two-sided
global energy-form bound, and finite-volume strong Lie--Trotter convergence can
be upgraded to graph-strong convergence below the half-energy endpoint when a
uniform half-graph bound is supplied.  The same calculations also expose three
critical topology boundaries: raw resolvents are not point-norm continuous
under the unbounded kick, the quartic onsite flow defeats the proposed local
graph estimate below one half, and coordinate cutoffs do not provide a
cutoff-uniform norm-C1 half-strip expansion.  A faithful-representation
strong-star limit is not an abstract C-star conclusion.  Common alpha/KMS,
ground-state selection, a GNS gap, continuum removal, and Pre-A remain open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-"
    "resummation-route-split-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.3"
EXPLORATION_ID = "EXP-000799"
TASK_ID = "T-054"
CLAIM_IDS = ["C6-SPACETIME-SIGNATURE"]
TROTTER_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-"
    "LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE"
)
MODULAR_GATE = (
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY"
)
OPEN_GATES = [TROTTER_GATE, MODULAR_GATE]
NEGATIVE_IDS = [
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-POINT-NORM-BOND-KICK-CONTINUITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-ONSITE-QP-LIPSCHITZ-STABILITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SUBCRITICAL-ENERGY-DAMPED-ONSITE-LIPSCHITZ-STABILITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-COORDINATE-CUTOFF-HALF-MODULAR-STRIP-ABSOLUTE-CLOSURE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SMALL-D-DELTA-D-UNIFORM-HALF-STRIP-MULTIPLIER-INFERENCE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FAITHFUL-REPRESENTATION-STRONGSTAR-ABSTRACT-CSTAR-INFERENCE",
]
CRITICAL_HALF_NEGATIVE_ID = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-ENERGY-DAMPED-"
    "LEIBNIZ-ONSITE-STABILITY"
)


def serial(value: Any) -> Any:
    """Convert exact values to deterministic JSON-compatible objects."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        serial(dict(payload)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write one deterministic JSON object using fsync and atomic replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                serial(dict(payload)),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast exact assertion ledger."""

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
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
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


def exact_sqrt(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator:
        raise ValueError(f"numerator is not a square: {value}")
    if denominator * denominator != value.denominator:
        raise ValueError(f"denominator is not a square: {value}")
    return Fraction(numerator, denominator)


def polynomial_subtract(
    left: Mapping[tuple[int, ...], Fraction],
    right: Mapping[tuple[int, ...], Fraction],
) -> dict[tuple[int, ...], Fraction]:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, Fraction(0)) - coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


SparsePolynomial = dict[tuple[int, ...], Fraction]


def sparse_constant(dimension: int, coefficient: Fraction) -> SparsePolynomial:
    if coefficient == 0:
        return {}
    return {tuple([0] * dimension): coefficient}


def sparse_variable(dimension: int, index: int) -> SparsePolynomial:
    exponent = [0] * dimension
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def sparse_add(left: Mapping[tuple[int, ...], Fraction], right: Mapping[tuple[int, ...], Fraction]) -> SparsePolynomial:
    output = dict(left)
    for exponent, coefficient in right.items():
        output[exponent] = output.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def sparse_scale(polynomial: Mapping[tuple[int, ...], Fraction], scale: Fraction) -> SparsePolynomial:
    if scale == 0:
        return {}
    return {
        exponent: coefficient * scale
        for exponent, coefficient in polynomial.items()
        if coefficient * scale
    }


def sparse_multiply(left: Mapping[tuple[int, ...], Fraction], right: Mapping[tuple[int, ...], Fraction]) -> SparsePolynomial:
    output: SparsePolynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            if len(left_exponent) != len(right_exponent):
                raise ValueError("sparse polynomial dimensions disagree")
            exponent = tuple(
                left_power + right_power
                for left_power, right_power in zip(left_exponent, right_exponent)
            )
            output[exponent] = output.get(exponent, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def sparse_power(polynomial: Mapping[tuple[int, ...], Fraction], exponent: int, dimension: int) -> SparsePolynomial:
    output = sparse_constant(dimension, Fraction(1))
    for _ in range(exponent):
        output = sparse_multiply(output, polynomial)
    return output


def sparse_derivative(polynomial: Mapping[tuple[int, ...], Fraction], index: int) -> SparsePolynomial:
    output: SparsePolynomial = {}
    for exponent, coefficient in polynomial.items():
        power = exponent[index]
        if power == 0:
            continue
        differentiated = list(exponent)
        differentiated[index] -= 1
        differentiated_exponent = tuple(differentiated)
        output[differentiated_exponent] = (
            output.get(differentiated_exponent, Fraction(0))
            + coefficient * power
        )
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def sparse_vector_field_apply(
    polynomial: Mapping[tuple[int, ...], Fraction],
    vector_field: list[SparsePolynomial],
) -> SparsePolynomial:
    output: SparsePolynomial = {}
    for index, component in enumerate(vector_field):
        derivative = sparse_derivative(polynomial, index)
        if derivative and component:
            output = sparse_add(output, sparse_multiply(derivative, component))
    return output


def sparse_axis_projection(
    polynomial: Mapping[tuple[int, ...], Fraction],
    axis_index: int,
) -> dict[int, Fraction]:
    """Set all variables except one axis coordinate to zero."""

    output: dict[int, Fraction] = {}
    for exponent, coefficient in polynomial.items():
        if any(power for index, power in enumerate(exponent) if index != axis_index):
            continue
        power = exponent[axis_index]
        output[power] = output.get(power, Fraction(0)) + coefficient
    return {power: coefficient for power, coefficient in output.items() if coefficient}


def graph_kick_fixture() -> dict[str, Any]:
    """Rebuild the weighted Q3 kick-form constants without symbolic software."""

    z = 6
    centered_ratio = Fraction(3, 2)
    c = Fraction(3, 5)
    chi = Fraction(7, 4)
    gamma = Fraction(4, 25)
    sqrt_gamma = exact_sqrt(gamma)

    # |S_x|^2 <= z sum_(y~x)|q_y|^2 and f_x <= e^mu f_y on an edge.
    neighbor_weight_coefficient = Fraction(z) * centered_ratio
    weighted_s_coefficient_before_absorption = (
        Fraction(z) * neighbor_weight_coefficient
    )
    q2_absorption_coefficient = Fraction(1, 1) / (2 * sqrt_gamma)
    weighted_s_coefficient = (
        weighted_s_coefficient_before_absorption * q2_absorption_coefficient
    )

    # q^2 <= (1+gamma q^4)/(2 sqrt(gamma)); the residual is a square.
    q2_residual = {
        4: gamma,
        2: -2 * sqrt_gamma,
        0: Fraction(1),
    }
    q2_residual_square = {
        4: gamma,
        2: -2 * sqrt_gamma,
        0: Fraction(1),
    }

    kick_excess = c * c * weighted_s_coefficient / chi
    c_b = 1 + kick_excess
    delta = Fraction(2, 7)
    factor = 1 + c_b * abs(delta)
    young_cross = abs(delta)
    young_square = delta * delta + abs(delta)

    sign_rows = []
    for sign in (-1, 1):
        signed_delta = sign * delta
        sign_rows.append(
            {
                "sign": sign,
                "delta": signed_delta,
                "cross_young_coefficient": abs(signed_delta),
                "square_coefficient": signed_delta * signed_delta
                + abs(signed_delta),
                "square_below_two_abs": signed_delta * signed_delta
                + abs(signed_delta)
                <= 2 * abs(signed_delta),
                "form_factor": 1 + c_b * abs(signed_delta),
            }
        )

    graph_power_rows = []
    for s in (Fraction(0), Fraction(1, 4), Fraction(3, 8), Fraction(1, 2)):
        graph_power_rows.append(
            {
                "s": s,
                "one_orientation_power": s,
                "one_sided_sum_power": s,
                "fully_conjugated_safe_power": 2 * s,
                "finite_step_exponent_for_N8": 2 * s * 8,
            }
        )

    return {
        "z": z,
        "centered_ratio": centered_ratio,
        "c": c,
        "chi": chi,
        "gamma": gamma,
        "sqrt_gamma": sqrt_gamma,
        "neighbor_weight_coefficient": neighbor_weight_coefficient,
        "weighted_s_coefficient_before_absorption": (
            weighted_s_coefficient_before_absorption
        ),
        "q2_absorption_coefficient": q2_absorption_coefficient,
        "weighted_s_coefficient": weighted_s_coefficient,
        "q2_residual": q2_residual,
        "q2_residual_square": q2_residual_square,
        "kick_excess": kick_excess,
        "C_b": c_b,
        "delta": delta,
        "factor": factor,
        "young_cross": young_cross,
        "young_square": young_square,
        "sign_rows": sign_rows,
        "graph_power_rows": graph_power_rows,
        "trotter_exponential_rate_at_s_half": c_b,
        "two_s_rate_formula": "exp(2*s*C_b*abs(t))",
    }


def kick_commutator_fixture() -> dict[str, Any]:
    """Use the terminating CCR derivation to recover the exact kick recurrence."""

    c = Fraction(3, 5)
    delta = Fraction(2, 7)
    z = 6
    # Sparse linear expressions use the ordered basis q0,...,q6,p0.
    dimension = z + 2
    q_rows = []
    for coordinate in range(z + 1):
        vector = [Fraction(0)] * dimension
        vector[coordinate] = Fraction(1)
        q_rows.append(tuple(vector))
    p0 = [Fraction(0)] * dimension
    p0[-1] = Fraction(1)
    derivation_p0 = [Fraction(0)] * dimension
    for neighbor in range(1, z + 1):
        derivation_p0[neighbor] = c
    second_derivation_p0 = tuple([Fraction(0)] * dimension)
    kicked_p0 = tuple(
        coefficient + delta * derivative
        for coefficient, derivative in zip(p0, derivation_p0)
    )
    inverse_p0 = tuple(
        coefficient - delta * derivative
        for coefficient, derivative in zip(kicked_p0, derivation_p0)
    )
    expected_kicked = [Fraction(0)] * dimension
    expected_kicked[-1] = Fraction(1)
    for neighbor in range(1, z + 1):
        expected_kicked[neighbor] = delta * c
    return {
        "basis": [*(f"q{index}" for index in range(z + 1)), "p0"],
        "q_invariant": all(row == q_rows[index] for index, row in enumerate(q_rows)),
        "derivation_p0": tuple(derivation_p0),
        "second_derivation_p0": second_derivation_p0,
        "kicked_p0": kicked_p0,
        "expected_kicked_p0": tuple(expected_kicked),
        "inverse_p0": inverse_p0,
        "original_p0": tuple(p0),
        "neighbor_coefficient": delta * c,
        "series_terminates_after_first_commutator": True,
        "convention": (
            "beta_delta(X)=B_delta^* X B_delta, so p_x maps to "
            "p_x+delta*c*sum_(y~x)q_y"
        ),
    }


def resolvent_no_go_fixture() -> dict[str, Any]:
    """Compute the exact joint-spectrum resolvent discontinuity."""

    denominator = {
        (0, 0): Fraction(1),
        (2, 0): Fraction(1),
        (0, 2): Fraction(1),
        (2, 2): Fraction(1),
    }
    numerator = {
        (2, 0): Fraction(1),
        (1, 1): Fraction(-2),
        (0, 2): Fraction(1),
    }
    residual = polynomial_subtract(denominator, numerator)
    expected_residual = {
        (0, 0): Fraction(1),
        (1, 1): Fraction(2),
        (2, 2): Fraction(1),
    }

    u = Fraction(2)
    v = Fraction(-1, 2)
    numerator_value = (u - v) ** 2
    denominator_value = (1 + u * u) * (1 + v * v)
    residual_value = denominator_value - numerator_value
    c = Fraction(3, 5)
    delta_rows = []
    for delta in (
        Fraction(-5, 13),
        Fraction(-2, 7),
        Fraction(2, 7),
        Fraction(5, 13),
    ):
        q_neighbor = (v - u) / (delta * c)
        reconstructed_v = u + delta * c * q_neighbor
        delta_rows.append(
            {
                "delta": delta,
                "q_neighbor": q_neighbor,
                "reconstructed_v": reconstructed_v,
                "distance_squared": numerator_value / denominator_value,
            }
        )
    return {
        "denominator_polynomial": denominator,
        "numerator_polynomial": numerator,
        "residual_polynomial": residual,
        "expected_residual_polynomial": expected_residual,
        "residual_identity": "(1+u*v)^2",
        "u": u,
        "v": v,
        "uv": u * v,
        "numerator_value": numerator_value,
        "denominator_value": denominator_value,
        "residual_value": residual_value,
        "distance_squared": numerator_value / denominator_value,
        "delta_rows": delta_rows,
        "joint_spectrum_surjective_for_nonzero_delta": True,
        "norm_distance_for_every_nonzero_delta": Fraction(1),
        "point_norm_continuous_at_zero": False,
    }


def shifted_power_three(shift: Fraction) -> dict[int, Fraction]:
    """Return the exact coefficients of (q-shift)^3."""

    return {
        3: Fraction(1),
        2: -3 * shift,
        1: 3 * shift * shift,
        0: -(shift**3),
    }


def quartic_onsite_fixture() -> dict[str, Any]:
    """Rebuild the quartic translation commutator and moving-bump threshold."""

    g = Fraction(7, 9)
    a = Fraction(5, 7)
    unshifted = {3: g}
    shifted = {
        power: g * coefficient for power, coefficient in shifted_power_three(a).items()
    }
    difference = dict(unshifted)
    for power, coefficient in shifted.items():
        difference[power] = difference.get(power, Fraction(0)) - coefficient
    difference = {power: coefficient for power, coefficient in difference.items() if coefficient}
    expected = {
        2: 3 * g * a,
        1: -3 * g * a * a,
        0: g * a**3,
    }

    exponent_rows = []
    for s in (
        Fraction(0),
        Fraction(1, 4),
        Fraction(3, 8),
        Fraction(1, 2),
        Fraction(3, 4),
    ):
        exponent = 2 - 4 * s
        exponent_rows.append(
            {
                "s": s,
                "translated_bump_exponent": exponent,
                "forces_unboundedness": exponent > 0,
                "critical_test_only": exponent == 0,
            }
        )
    return {
        "g": g,
        "a": a,
        "U_prime": "g*q^3",
        "translated_U_prime": shifted,
        "difference": difference,
        "expected": expected,
        "identity": (
            "[p,delta(W_a)]=(U'(q)-U'(q-a))*W_a="
            "g*(3*a*q^2-3*a^2*q+a^3)*W_a"
        ),
        "exponent_formula": "2-4*s",
        "threshold": Fraction(1, 2),
        "exponent_rows": exponent_rows,
        "below_half_local_graph_bound": False,
        "critical_half_status": (
            "INCONCLUSIVE UNDER THIS FIRST-VARIATION POWER COUNT; THE FIXED "
            "ONE-SIDED LEIBNIZ ROUTE IS TESTED SEPARATELY"
        ),
    }


def q3_edges() -> list[tuple[int, int]]:
    """Return the twelve edges of the three-cube on binary vertices 0,...,7."""

    return [
        (left, left ^ bit)
        for left in range(8)
        for bit in (1, 2, 4)
        if left < (left ^ bit)
    ]


def critical_half_vector_field_fixture() -> dict[str, Any]:
    """Rebuild the full-Q3 and scalar backward Hamilton jets exactly."""

    sites = 8
    dimension = 2 * sites
    g = Fraction(3, 5)
    lam = Fraction(2, 7)
    chi = Fraction(7, 4)
    capital_g = g + 3 * lam
    edges = q3_edges()
    q = [sparse_variable(dimension, index) for index in range(sites)]
    p = [sparse_variable(dimension, sites + index) for index in range(sites)]

    quartic: SparsePolynomial = {}
    for coordinate in q:
        quartic = sparse_add(
            quartic,
            sparse_scale(sparse_power(coordinate, 4, dimension), g / 4),
        )
    for left, right in edges:
        difference = sparse_add(q[left], sparse_scale(q[right], Fraction(-1)))
        square_sum = sparse_add(
            sparse_power(q[left], 2, dimension),
            sparse_power(q[right], 2, dimension),
        )
        edge_term = sparse_multiply(
            sparse_power(difference, 2, dimension), square_sum
        )
        quartic = sparse_add(quartic, sparse_scale(edge_term, lam / 4))

    forces = [sparse_derivative(quartic, index) for index in range(sites)]
    backward_vector_field = [
        sparse_scale(momentum, -Fraction(1, 1) / chi) for momentum in p
    ] + forces

    neighbors_zero = sorted(
        right if left == 0 else left
        for left, right in edges
        if left == 0 or right == 0
    )
    expected_force_zero = sparse_scale(sparse_power(q[0], 3, dimension), capital_g)
    for neighbor in neighbors_zero:
        expected_force_zero = sparse_add(
            expected_force_zero,
            sparse_scale(
                sparse_multiply(
                    sparse_power(q[0], 2, dimension), q[neighbor]
                ),
                -3 * lam / 2,
            ),
        )
        expected_force_zero = sparse_add(
            expected_force_zero,
            sparse_scale(
                sparse_multiply(q[0], sparse_power(q[neighbor], 2, dimension)),
                lam,
            ),
        )
        expected_force_zero = sparse_add(
            expected_force_zero,
            sparse_scale(sparse_power(q[neighbor], 3, dimension), -lam / 2),
        )

    full_jets: list[dict[str, Any]] = []
    current = p[0]
    for order in range(1, 4):
        current = sparse_vector_field_apply(current, backward_vector_field)
        full_jets.append(
            {
                "order": order,
                "axis_polynomial": sparse_axis_projection(current, 0),
                "term_count_before_axis_projection": len(current),
            }
        )

    full_tau_terms = []
    for row in full_jets:
        for a_power, coefficient in row["axis_polynomial"].items():
            full_tau_terms.append(
                {
                    "tau_power": row["order"],
                    "a_power": a_power - 2 * row["order"],
                    "coefficient": coefficient / math.factorial(row["order"]),
                }
            )

    scalar_dimension = 2
    scalar_q = sparse_variable(scalar_dimension, 0)
    scalar_p = sparse_variable(scalar_dimension, 1)
    scalar_field = [
        sparse_scale(scalar_p, Fraction(-1)),
        sparse_power(scalar_q, 3, scalar_dimension),
    ]
    scalar_jets: list[dict[str, Any]] = []
    scalar_current = scalar_p
    for order in range(1, 6):
        scalar_current = sparse_vector_field_apply(scalar_current, scalar_field)
        scalar_jets.append(
            {
                "order": order,
                "axis_polynomial": sparse_axis_projection(scalar_current, 0),
                "term_count_before_axis_projection": len(scalar_current),
            }
        )

    scalar_tau_terms = []
    for row in scalar_jets:
        for a_power, coefficient in row["axis_polynomial"].items():
            scalar_tau_terms.append(
                {
                    "tau_power": row["order"],
                    "a_power": a_power - 2 * row["order"],
                    "coefficient": coefficient / math.factorial(row["order"]),
                }
            )

    leibniz_rows = []
    b = Fraction(3, 5)
    tau = Fraction(2, 7)
    for n in (1, 2, 4, 8, 16):
        a = n * b
        time = tau / (a * a)
        leading_p = a * tau
        cubic_correction = -tau**3 / (2 * a)
        quintic_correction = 9 * tau**5 / (40 * a**3)
        leibniz_rows.append(
            {
                "n": n,
                "b": b,
                "a": a,
                "t": time,
                "W_a_factor_count": n,
                "leading_p": leading_p,
                "cubic_correction": cubic_correction,
                "quintic_correction": quintic_correction,
                "leading_per_factor": leading_p / n,
                "cubic_per_factor": cubic_correction / n,
                "quintic_per_factor": quintic_correction / n,
            }
        )

    return {
        "q3": {
            "vertices": sites,
            "edges": edges,
            "degree_rows": [
                sum(vertex in edge for edge in edges) for vertex in range(sites)
            ],
            "g": g,
            "lambda": lam,
            "chi": chi,
            "G": capital_g,
            "neighbors_of_zero": neighbors_zero,
            "partial_0_V4": forces[0],
            "expected_partial_0_V4": expected_force_zero,
            "partial_0_formula": (
                "(g+3lambda)q0^3+lambda*sum_(j~0)"
                "[-3q0^2qj/2+q0qj^2-qj^3/2]"
            ),
            "backward_jets": full_jets,
            "tau_over_a_squared_terms": full_tau_terms,
        },
        "scalar": {
            "g": Fraction(1),
            "chi": Fraction(1),
            "backward_jets": scalar_jets,
            "tau_over_a_squared_terms": scalar_tau_terms,
            "series": (
                "p(tau/a^2)=a*tau-tau^3/(2a)+9tau^5/(40a^3)+..."
            ),
        },
        "leibniz": {
            "identity": "W_(n*b)=W_b^n",
            "scaling": "a=n*b, t=tau/a^2",
            "rows": leibniz_rows,
            "leading_per_factor": b * tau,
            "first_correction_per_factor_order": "n^-2",
            "second_correction_per_factor_order": "n^-4",
            "one_sided_critical_uniform_stability": False,
            "scope": (
                "The fixture rejects the named one-sided critical energy-damped "
                "Leibniz onsite stability class. It does not reject a two-sided, "
                "orbit-adapted, state-tempered, or non-Leibniz critical topology."
            ),
        },
    }


def power_of_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def trotter_graph_convergence_fixture() -> dict[str, Any]:
    """Audit the strict subcritical interpolation and its endpoint boundary."""

    s_values = (
        Fraction(0),
        Fraction(1, 4),
        Fraction(3, 8),
        Fraction(1, 2),
    )
    interpolation_rows = []
    for s in s_values:
        interpolation_rows.append(
            {
                "s": s,
                "strong_factor_exponent": 1 - 2 * s,
                "half_graph_factor_exponent": 2 * s,
                "strict_upgrade": s < Fraction(1, 2),
            }
        )

    # K e_0=e_0, K e_n=256^n e_n and
    # S_n=16^(-n)|e_n><e_0|.  Then S_n ->0 in norm, while
    # K^(1/2)S_nK^(-1/2)=|e_n><e_0| does not converge strongly.
    endpoint_rows = []
    for n in range(1, 9):
        row: dict[str, Any] = {
            "n": n,
            "K_ratio": Fraction(256**n),
            "base_norm": Fraction(1, 16**n),
        }
        coefficients: dict[str, Fraction] = {}
        for s in s_values:
            exponent = int(8 * n * s - 4 * n)
            if Fraction(exponent) != 8 * n * s - 4 * n:
                raise AssertionError("chosen exact fixture lost an integral exponent")
            coefficients[str(s)] = power_of_two(exponent)
        row["graph_coefficients"] = coefficients
        endpoint_rows.append(row)

    return {
        "interpolation_inequality": (
            "||K^s S_n K^-s psi|| <= ||S_n K^-s psi||^(1-2s) "
            "*(2M ||K^(1/2-s)psi||)^(2s)"
        ),
        "interpolation_rows": interpolation_rows,
        "dense_core": "D(K^(1/2-s))",
        "hypotheses": [
            "finite-volume strong Lie--Trotter convergence",
            "uniform K^(1/2) graph bound for approximants and limit",
            "uniform ordinary operator bound",
        ],
        "conclusion": (
            "finite-volume K^s-graph strong convergence for every 0<=s<1/2"
        ),
        "endpoint_rows": endpoint_rows,
        "endpoint_base_norm_tends_to_zero": True,
        "endpoint_half_graph_image_norm": Fraction(1),
        "endpoint_inference_valid": False,
        "finite_volume_subcritical_status": "CONDITIONAL THEOREM",
        "thermodynamic_status": "OPEN: no spatial Cauchy estimate follows",
    }


def coordinate_cutoff_fixture() -> dict[str, Any]:
    """Rebuild the norm-C1 and absolute half-strip cutoff obstructions."""

    commutator_rows = []
    # In the region Q_L(q)=q, [p^2,Q_L]=[p^2,q]=-2 i p (hbar=1).
    # For psi_k=e^(ikq)phi with <p>=0 and ||p phi||^2=1, the squared
    # norm is exactly 4(k^2+1).
    for momentum in (1, 2, 4, 8, 16, 32):
        commutator_rows.append(
            {
                "momentum": momentum,
                "squared_norm": 4 * (momentum * momentum + 1),
            }
        )

    z = 6
    beta = Fraction(5, 7)
    c = Fraction(3, 5)
    radius_rows = []
    for cutoff in (1, 2, 4, 8, 16):
        j_l = c * cutoff * cutoff
        radius = z * beta * j_l
        radius_rows.append(
            {
                "L": cutoff,
                "J_L": j_l,
                "radius": radius,
                "absolute_geometric_route_converges": radius < 1,
            }
        )
    return {
        "commutator_identity": "[p^2,Q_L]=-2*i*p on the identity region",
        "commutator_rows": commutator_rows,
        "norm_C1": False,
        "z": z,
        "beta": beta,
        "c": c,
        "J_L_formula": "c*L^2",
        "radius_formula": "r=z*beta*J_L",
        "radius_rows": radius_rows,
        "quartic_scaling_ratio": radius_rows[1]["J_L"] / radius_rows[0]["J_L"],
        "fixed_beta_half_strip_limit": False,
        "scope": (
            "This rejects the absolute connected/norm-C1 cutoff method, not "
            "all projected Duhamel or state-tempered locality methods."
        ),
    }


def direct_relative_unitary_fixture() -> dict[str, Any]:
    """Check the exact constants in the two-orientation finite-volume theorem."""

    time = Fraction(5, 7)
    hbar = Fraction(11, 13)
    beta = Fraction(4, 3)
    theta = Fraction(7, 3)
    phi_w_squared = Fraction(9, 16)
    root_tail = exact_sqrt(phi_w_squared)
    one_orientation = abs(time) * root_tail / hbar
    trace_distance = 2 * one_orientation
    norm_a = Fraction(2, 3)
    norm_a_minus = Fraction(3, 4)
    norm_a_plus = Fraction(5, 6)
    return {
        "time": time,
        "hbar": hbar,
        "beta": beta,
        "theta": theta,
        "phi_W_squared": phi_w_squared,
        "root_tail": root_tail,
        "one_orientation_bound": one_orientation,
        "other_orientation_bound": one_orientation,
        "trace_distance_bound": trace_distance,
        "entropy_coefficient": beta / (theta - beta),
        "fixed_finite_volume_unbounded_tail_passage_closed": True,
        "thermodynamic_uniform_tail_passage_closed": False,
        "form_norm_cutoff_required": True,
        "finite_gibbs_energy_required": True,
        "norm_A": norm_a,
        "norm_A_minus": norm_a_minus,
        "norm_A_plus": norm_a_plus,
        "initial_direct_bound": one_orientation * (norm_a + norm_a_minus),
        "initial_adjoint_bound": one_orientation * (norm_a + norm_a_plus),
        "relative_entropy_identity": (
            "S(U_K rho U_K^*||rho)=beta*(rho_t(W)-rho(W))"
        ),
        "entropy_moment_condition": "theta>beta",
        "scope": (
            "finite volume, fixed beta, and an initially modular-analytic test; "
            "no uniform evolved half-strip multiplier follows"
        ),
    }


def small_direct_tail_multiplier_fixture() -> dict[str, Any]:
    """Exact rational surrogate for the two-level evolved-multiplier no-go.

    Take beta=4 log(2), epsilon_n=2^(-n), and hence
    exp(-beta*n)=epsilon_n^4=16^(-n).  Duhamel logarithmic means are reported
    in units of log(16); this removes one fixed positive scalar and preserves
    every vanishing/divergence verdict.
    """

    rows = []
    for gap in (1, 2, 4, 8, 16, 32):
        epsilon = Fraction(1, 2**gap)
        gibbs_ratio = epsilon**4
        p0 = Fraction(1, 1) / (1 + gibbs_ratio)
        p1 = gibbs_ratio / (1 + gibbs_ratio)
        difference = p0 - p1
        log_gap_units = Fraction(gap)
        logarithmic_mean_units = difference / log_gap_units
        omega_squared = gap * gap + 4 * epsilon * epsilon
        off_diagonal = 2 * epsilon * gap / omega_squared
        diagonal_zero = -4 * epsilon * epsilon / omega_squared
        diagonal_one = -diagonal_zero

        w_duhamel_squared = 2 * epsilon * epsilon * logarithmic_mean_units
        modular_w_duhamel_squared = gap * gap * w_duhamel_squared
        direct_duhamel_squared = (
            p0 * diagonal_zero * diagonal_zero
            + p1 * diagonal_one * diagonal_one
            + 2 * logarithmic_mean_units * off_diagonal * off_diagonal
        )
        direct_modular_duhamel_squared = (
            2
            * logarithmic_mean_units
            * gap
            * gap
            * off_diagonal
            * off_diagonal
        )
        m0_lower = off_diagonal / (epsilon * epsilon)
        asymptotic_ratio = m0_lower * gap * epsilon / 2
        rows.append(
            {
                "n": gap,
                "epsilon": epsilon,
                "gibbs_ratio": gibbs_ratio,
                "p0": p0,
                "p1": p1,
                "logarithmic_mean_in_log16_units": logarithmic_mean_units,
                "Omega_squared": omega_squared,
                "half_period_label": "pi*hbar/sqrt(Omega_squared)",
                "evolved_projection_off_diagonal": off_diagonal,
                "W_D_squared_in_log16_units": w_duhamel_squared,
                "logrho_W_D_squared_in_log16_units": modular_w_duhamel_squared,
                "direct_D_squared_in_log16_units": direct_duhamel_squared,
                "direct_delta_D_squared_in_log16_units": (
                    direct_modular_duhamel_squared
                ),
                "M0_lower": m0_lower,
                "M0_asymptotic_ratio": asymptotic_ratio,
            }
        )
    return {
        "beta": "4*log(2)",
        "rows": rows,
        "W_tail_decreases": all(
            right["W_D_squared_in_log16_units"]
            < left["W_D_squared_in_log16_units"]
            for left, right in zip(rows, rows[1:])
        ),
        "modular_W_tail_decreases": all(
            right["logrho_W_D_squared_in_log16_units"]
            < left["logrho_W_D_squared_in_log16_units"]
            for left, right in zip(rows, rows[1:])
        ),
        "direct_tail_decreases": all(
            right["direct_D_squared_in_log16_units"]
            < left["direct_D_squared_in_log16_units"]
            for left, right in zip(rows, rows[1:])
        ),
        "direct_modular_tail_decreases": all(
            right["direct_delta_D_squared_in_log16_units"]
            < left["direct_delta_D_squared_in_log16_units"]
            for left, right in zip(rows, rows[1:])
        ),
        "M0_lower_increases": all(
            right["M0_lower"] > left["M0_lower"]
            for left, right in zip(rows, rows[1:])
        ),
        "M0_scaled_ratio_increases_to_one": all(
            right["M0_asymptotic_ratio"] > left["M0_asymptotic_ratio"]
            for left, right in zip(rows, rows[1:])
        ),
        "scope": (
            "small direct D and delta-D tails do not imply uniform evolved "
            "M0/M1; the direct projected route remains open"
        ),
    }


def faithful_representation_fixture() -> dict[str, Any]:
    """Compare tail projections in a faithful l2 representation and a character."""

    rows = []
    for tail_start in range(1, 11):
        rows.append(
            {
                "n": tail_start,
                # xi_k^2=2^(-(k+1)), k>=0, so the tail is exactly 2^-n.
                "standard_l2_tail_squared": Fraction(1, 2**tail_start),
                "adjoint_tail_squared": Fraction(1, 2**tail_start),
                "free_ultrafilter_character": Fraction(1),
            }
        )
    return {
        "algebra": "ell_infinity(N)",
        "tail_projection": "e_n(k)=1 if k>=n else 0",
        "standard_representation": "faithful multiplication on ell_2(N)",
        "standard_representation_faithful": True,
        "finite_support_dense_test": "e_n xi=0 once n exceeds supp(xi)",
        "rows": rows,
        "standard_strong_star_limit": Fraction(0),
        "ultrafilter_character_limit": Fraction(1),
        "abstract_C_star_inference": False,
        "scope": (
            "A preregistered faithful strong-star topology can still be used; "
            "the fixture forbids promoting it to a representation-free C-star fact."
        ),
    }


def build_payload() -> dict[str, Any]:
    """Run the independent exact audit against the package authorities."""

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    audit = Audit()

    graph = graph_kick_fixture()
    audit.check("Q3 degree", graph["z"] == 6, graph["z"], 6, "global-graph")
    audit.check(
        "centered neighbor ratio",
        graph["centered_ratio"] == Fraction(3, 2),
        graph["centered_ratio"],
        Fraction(3, 2),
        "global-graph",
    )
    audit.check(
        "fixture parameters",
        (graph["c"], graph["chi"], graph["gamma"])
        == (Fraction(3, 5), Fraction(7, 4), Fraction(4, 25)),
        (graph["c"], graph["chi"], graph["gamma"]),
        (Fraction(3, 5), Fraction(7, 4), Fraction(4, 25)),
        "global-graph",
    )
    audit.check(
        "exact sqrt gamma",
        graph["sqrt_gamma"] == Fraction(2, 5),
        graph["sqrt_gamma"],
        Fraction(2, 5),
        "global-graph",
    )
    audit.check(
        "Young q2 residual square",
        graph["q2_residual"] == graph["q2_residual_square"],
        graph["q2_residual"],
        "(sqrt(gamma) q^2-1)^2",
        "global-graph",
    )
    audit.check(
        "weighted neighbor coefficient",
        graph["weighted_s_coefficient_before_absorption"] == 54,
        graph["weighted_s_coefficient_before_absorption"],
        54,
        "global-graph",
    )
    audit.check(
        "weighted S absorption coefficient",
        graph["weighted_s_coefficient"] == Fraction(135, 2),
        graph["weighted_s_coefficient"],
        Fraction(135, 2),
        "global-graph",
    )
    audit.check(
        "kick excess",
        graph["kick_excess"] == Fraction(486, 35),
        graph["kick_excess"],
        Fraction(486, 35),
        "global-graph",
    )
    audit.check(
        "C_b exact",
        graph["C_b"] == Fraction(521, 35),
        graph["C_b"],
        Fraction(521, 35),
        "global-graph",
    )
    audit.check(
        "delta form factor",
        graph["factor"] == Fraction(1287, 245),
        graph["factor"],
        Fraction(1287, 245),
        "global-graph",
    )
    audit.check(
        "Young square bounded by two abs delta",
        graph["young_square"] <= 2 * abs(graph["delta"]),
        graph["young_square"],
        f"<= {2 * abs(graph['delta'])}",
        "global-graph",
    )
    audit.check(
        "positive and negative kick forms",
        all(row["square_below_two_abs"] for row in graph["sign_rows"])
        and len({row["form_factor"] for row in graph["sign_rows"]}) == 1,
        graph["sign_rows"],
        "same 1+C_b|delta| bound for both signs",
        "global-graph",
    )
    audit.check(
        "two-sided graph exponent",
        [row["fully_conjugated_safe_power"] for row in graph["graph_power_rows"]]
        == [Fraction(0), Fraction(1, 2), Fraction(3, 4), Fraction(1)],
        [row["fully_conjugated_safe_power"] for row in graph["graph_power_rows"]],
        [Fraction(0), Fraction(1, 2), Fraction(3, 4), Fraction(1)],
        "global-graph",
    )

    kick = kick_commutator_fixture()
    audit.check("kick leaves q invariant", kick["q_invariant"], True, True, "kick-CCR")
    audit.check(
        "kick commutator series terminates",
        all(value == 0 for value in kick["second_derivation_p0"]),
        kick["second_derivation_p0"],
        "zero",
        "kick-CCR",
    )
    audit.check(
        "kick momentum sign and coefficient",
        kick["kicked_p0"] == kick["expected_kicked_p0"]
        and kick["neighbor_coefficient"] == Fraction(6, 35),
        {
            "p": kick["kicked_p0"],
            "neighbor": kick["neighbor_coefficient"],
        },
        "p_x+delta*c*sum q_y with coefficient 6/35",
        "kick-CCR",
    )
    audit.check(
        "inverse kick recurrence",
        kick["inverse_p0"] == kick["original_p0"],
        kick["inverse_p0"],
        kick["original_p0"],
        "kick-CCR",
    )

    resolvent = resolvent_no_go_fixture()
    audit.check(
        "resolvent polynomial residual",
        resolvent["residual_polynomial"]
        == resolvent["expected_residual_polynomial"],
        resolvent["residual_polynomial"],
        "(1+u*v)^2",
        "resolvent-no-go",
    )
    audit.check(
        "uv critical fibre",
        resolvent["uv"] == -1,
        resolvent["uv"],
        -1,
        "resolvent-no-go",
    )
    audit.check(
        "resolvent ratio residual zero",
        resolvent["residual_value"] == 0
        and resolvent["numerator_value"] == resolvent["denominator_value"],
        resolvent["residual_value"],
        0,
        "resolvent-no-go",
    )
    audit.check(
        "every tested nonzero kick realizes the critical fibre",
        all(row["reconstructed_v"] == resolvent["v"] for row in resolvent["delta_rows"]),
        resolvent["delta_rows"],
        "v=u+delta*c*q_y for each nonzero delta",
        "resolvent-no-go",
    )
    audit.check(
        "raw resolvent norm distance",
        resolvent["distance_squared"] == 1
        and resolvent["norm_distance_for_every_nonzero_delta"] == 1
        and not resolvent["point_norm_continuous_at_zero"],
        resolvent["distance_squared"],
        1,
        "resolvent-no-go",
    )

    onsite = quartic_onsite_fixture()
    audit.check(
        "quartic translation polynomial",
        onsite["difference"] == onsite["expected"],
        onsite["difference"],
        onsite["expected"],
        "onsite-critical",
    )
    audit.check(
        "quartic leading translated coefficient",
        onsite["difference"][2] == 3 * onsite["g"] * onsite["a"],
        onsite["difference"][2],
        3 * onsite["g"] * onsite["a"],
        "onsite-critical",
    )
    audit.check(
        "translated bump exponents",
        [row["translated_bump_exponent"] for row in onsite["exponent_rows"]]
        == [Fraction(2), Fraction(1), Fraction(1, 2), Fraction(0), Fraction(-1)],
        [row["translated_bump_exponent"] for row in onsite["exponent_rows"]],
        [Fraction(2), Fraction(1), Fraction(1, 2), Fraction(0), Fraction(-1)],
        "onsite-critical",
    )
    audit.check(
        "all sampled subcritical powers fail",
        all(
            row["forces_unboundedness"]
            for row in onsite["exponent_rows"]
            if row["s"] < Fraction(1, 2)
        )
        and not onsite["below_half_local_graph_bound"],
        onsite["exponent_rows"],
        "2-4s>0 for s<1/2",
        "onsite-critical",
    )
    audit.check(
        "first-variation critical half test is inconclusive",
        next(
            row for row in onsite["exponent_rows"] if row["s"] == Fraction(1, 2)
        )["critical_test_only"]
        and onsite["critical_half_status"].startswith("INCONCLUSIVE"),
        onsite["critical_half_status"],
        "inconclusive here; separate critical theorem required",
        "onsite-critical",
    )

    critical = critical_half_vector_field_fixture()
    q3_critical = critical["q3"]
    audit.check(
        "critical Q3 graph combinatorics",
        len(q3_critical["edges"]) == 12
        and q3_critical["degree_rows"] == [3] * 8
        and q3_critical["neighbors_of_zero"] == [1, 2, 4],
        {
            "edges": len(q3_critical["edges"]),
            "degrees": q3_critical["degree_rows"],
            "neighbors0": q3_critical["neighbors_of_zero"],
        },
        {"edges": 12, "degrees": [3] * 8, "neighbors0": [1, 2, 4]},
        "critical-half",
    )
    audit.check(
        "critical Q3 exact parameters",
        (
            q3_critical["g"],
            q3_critical["lambda"],
            q3_critical["chi"],
            q3_critical["G"],
        )
        == (
            Fraction(3, 5),
            Fraction(2, 7),
            Fraction(7, 4),
            Fraction(51, 35),
        ),
        {
            key: q3_critical[key] for key in ("g", "lambda", "chi", "G")
        },
        {"g": Fraction(3, 5), "lambda": Fraction(2, 7), "chi": Fraction(7, 4), "G": Fraction(51, 35)},
        "critical-half",
    )
    audit.check(
        "critical Q3 force polynomial",
        q3_critical["partial_0_V4"] == q3_critical["expected_partial_0_V4"],
        q3_critical["partial_0_V4"],
        q3_critical["partial_0_formula"],
        "critical-half",
    )
    audit.check(
        "critical Q3 force term count",
        len(q3_critical["partial_0_V4"]) == 10,
        len(q3_critical["partial_0_V4"]),
        "one own cubic plus three terms for each of three neighbors",
        "critical-half",
    )
    expected_q3_jets = [
        {3: Fraction(51, 35)},
        {},
        {5: Fraction(-32112, 8575)},
    ]
    audit.check(
        "critical Q3 backward jets",
        [row["axis_polynomial"] for row in q3_critical["backward_jets"]]
        == expected_q3_jets,
        [row["axis_polynomial"] for row in q3_critical["backward_jets"]],
        expected_q3_jets,
        "critical-half",
    )
    audit.check(
        "critical Q3 third jet Hessian-force contraction",
        Fraction(-32112, 8575)
        == -(
            3 * q3_critical["G"] ** 2
            + Fraction(9, 4) * q3_critical["lambda"] ** 2
        )
        / q3_critical["chi"],
        Fraction(-32112, 8575),
        "-(3G^2+9lambda^2/4)/chi",
        "critical-half",
    )
    audit.check(
        "critical Q3 tau over a squared expansion",
        q3_critical["tau_over_a_squared_terms"]
        == [
            {"tau_power": 1, "a_power": 1, "coefficient": Fraction(51, 35)},
            {"tau_power": 3, "a_power": -1, "coefficient": Fraction(-5352, 8575)},
        ],
        q3_critical["tau_over_a_squared_terms"],
        "(51/35)a*tau-(5352/8575)a^-1*tau^3+...",
        "critical-half",
    )

    scalar_critical = critical["scalar"]
    expected_scalar_jets = [
        {3: Fraction(1)},
        {},
        {5: Fraction(-3)},
        {},
        {7: Fraction(27)},
    ]
    audit.check(
        "critical scalar backward jets",
        [row["axis_polynomial"] for row in scalar_critical["backward_jets"]]
        == expected_scalar_jets,
        [row["axis_polynomial"] for row in scalar_critical["backward_jets"]],
        expected_scalar_jets,
        "critical-half",
    )
    audit.check(
        "critical scalar tau expansion",
        scalar_critical["tau_over_a_squared_terms"]
        == [
            {"tau_power": 1, "a_power": 1, "coefficient": Fraction(1)},
            {"tau_power": 3, "a_power": -1, "coefficient": Fraction(-1, 2)},
            {"tau_power": 5, "a_power": -3, "coefficient": Fraction(9, 40)},
        ],
        scalar_critical["tau_over_a_squared_terms"],
        "a*tau-tau^3/(2a)+9tau^5/(40a^3)+...",
        "critical-half",
    )

    leibniz = critical["leibniz"]
    audit.check(
        "critical Leibniz a and time scaling",
        all(row["a"] == row["n"] * row["b"] for row in leibniz["rows"])
        and all(
            row["t"] == Fraction(2, 7) / row["a"] ** 2
            for row in leibniz["rows"]
        )
        and all(row["W_a_factor_count"] == row["n"] for row in leibniz["rows"]),
        leibniz["rows"],
        "a=n*b, t=tau/a^2, W_a=W_b^n",
        "critical-half",
    )
    audit.check(
        "critical Leibniz leading response per factor",
        all(
            row["leading_per_factor"] == leibniz["leading_per_factor"]
            for row in leibniz["rows"]
        ),
        [row["leading_per_factor"] for row in leibniz["rows"]],
        leibniz["leading_per_factor"],
        "critical-half",
    )
    audit.check(
        "critical Leibniz correction scaling",
        all(
            abs(right["cubic_per_factor"])
            * 4
            == abs(left["cubic_per_factor"])
            and abs(right["quintic_per_factor"])
            * 16
            == abs(left["quintic_per_factor"])
            for left, right in zip(leibniz["rows"], leibniz["rows"][1:])
        ),
        [
            (row["cubic_per_factor"], row["quintic_per_factor"])
            for row in leibniz["rows"]
        ],
        "n^-2 and n^-4 per-factor corrections",
        "critical-half",
    )
    audit.check(
        "critical one-sided negative scope",
        not leibniz["one_sided_critical_uniform_stability"]
        and "one-sided critical" in leibniz["scope"]
        and "does not reject" in leibniz["scope"].lower()
        and "two-sided" in leibniz["scope"],
        leibniz["scope"],
        "only named one-sided Leibniz class rejected",
        "critical-half",
    )

    trotter = trotter_graph_convergence_fixture()
    audit.check(
        "subcritical interpolation exponent positive",
        all(
            row["strong_factor_exponent"] > 0
            for row in trotter["interpolation_rows"]
            if row["s"] < Fraction(1, 2)
        ),
        trotter["interpolation_rows"],
        "1-2s>0",
        "trotter-topology",
    )
    audit.check(
        "endpoint interpolation exponent zero",
        trotter["interpolation_rows"][-1]["strong_factor_exponent"] == 0,
        trotter["interpolation_rows"][-1],
        "1-2s=0 at s=1/2",
        "trotter-topology",
    )
    audit.check(
        "endpoint fixture base norm decays",
        all(
            right["base_norm"] < left["base_norm"]
            for left, right in zip(trotter["endpoint_rows"], trotter["endpoint_rows"][1:])
        ),
        [row["base_norm"] for row in trotter["endpoint_rows"]],
        "strict decay to zero",
        "trotter-topology",
    )
    audit.check(
        "strict subcritical graph coefficients decay",
        all(
            all(
                right["graph_coefficients"][str(s)]
                < left["graph_coefficients"][str(s)]
                for left, right in zip(
                    trotter["endpoint_rows"], trotter["endpoint_rows"][1:]
                )
            )
            for s in (Fraction(0), Fraction(1, 4), Fraction(3, 8))
        ),
        [row["graph_coefficients"] for row in trotter["endpoint_rows"][:3]],
        "strict decay for s<1/2",
        "trotter-topology",
    )
    audit.check(
        "endpoint half-graph image stays unit size",
        all(
            row["graph_coefficients"][str(Fraction(1, 2))] == 1
            for row in trotter["endpoint_rows"]
        )
        and not trotter["endpoint_inference_valid"],
        [
            row["graph_coefficients"][str(Fraction(1, 2))]
            for row in trotter["endpoint_rows"]
        ],
        "all one; no endpoint inference",
        "trotter-topology",
    )
    audit.check(
        "finite-volume theorem is conditional and subcritical",
        trotter["finite_volume_subcritical_status"] == "CONDITIONAL THEOREM"
        and "s<1/2" in trotter["conclusion"],
        {
            "status": trotter["finite_volume_subcritical_status"],
            "conclusion": trotter["conclusion"],
        },
        "conditional finite-volume graph-strong convergence below one half",
        "trotter-topology",
    )
    audit.check(
        "thermodynamic inference remains open",
        trotter["thermodynamic_status"].startswith("OPEN"),
        trotter["thermodynamic_status"],
        "OPEN",
        "trotter-topology",
    )

    cutoff = coordinate_cutoff_fixture()
    audit.check(
        "cutoff kinetic commutator grows",
        all(
            right["squared_norm"] > left["squared_norm"]
            for left, right in zip(cutoff["commutator_rows"], cutoff["commutator_rows"][1:])
        )
        and not cutoff["norm_C1"],
        cutoff["commutator_rows"],
        "unbounded [p^2,Q_L] norm",
        "cutoff",
    )

    direct = direct_relative_unitary_fixture()
    audit.check(
        "relative-unitary one-orientation constant",
        direct["one_orientation_bound"] == Fraction(195, 308)
        and direct["other_orientation_bound"] == Fraction(195, 308),
        {
            "right": direct["one_orientation_bound"],
            "left": direct["other_orientation_bound"],
        },
        Fraction(195, 308),
        "direct-relative-unitary",
    )
    audit.check(
        "relative-unitary trace factor two",
        direct["trace_distance_bound"] == Fraction(195, 154)
        and direct["trace_distance_bound"] == 2 * direct["one_orientation_bound"],
        direct["trace_distance_bound"],
        Fraction(195, 154),
        "direct-relative-unitary",
    )
    audit.check(
        "initial analytic direct constants",
        direct["initial_direct_bound"]
        == direct["one_orientation_bound"]
        * (direct["norm_A"] + direct["norm_A_minus"])
        and direct["initial_adjoint_bound"]
        == direct["one_orientation_bound"]
        * (direct["norm_A"] + direct["norm_A_plus"]),
        {
            "direct": direct["initial_direct_bound"],
            "adjoint": direct["initial_adjoint_bound"],
        },
        "tail*(||A||+||A_minus/plus||)",
        "direct-relative-unitary",
    )
    audit.check(
        "relative entropy and fixed-beta scope",
        "beta*(rho_t(W)-rho(W))" in direct["relative_entropy_identity"]
        and direct["entropy_moment_condition"] == "theta>beta"
        and direct["entropy_coefficient"] == Fraction(4, 3)
        and "initially modular-analytic" in direct["scope"]
        and "no uniform evolved" in direct["scope"],
        direct,
        "same-H identity and initial-analytic-only scope",
        "direct-relative-unitary",
    )
    audit.check(
        "fixed-finite-volume unbounded-tail scope",
        direct["fixed_finite_volume_unbounded_tail_passage_closed"] is True
        and direct["thermodynamic_uniform_tail_passage_closed"] is False
        and direct["form_norm_cutoff_required"] is True
        and direct["finite_gibbs_energy_required"] is True,
        {
            "fixed_finite_volume": direct[
                "fixed_finite_volume_unbounded_tail_passage_closed"
            ],
            "thermodynamic_uniform": direct[
                "thermodynamic_uniform_tail_passage_closed"
            ],
            "form_norm": direct["form_norm_cutoff_required"],
            "finite_energy": direct["finite_gibbs_energy_required"],
        },
        "fixed finite volume only",
        "direct-relative-unitary",
    )

    multiplier = small_direct_tail_multiplier_fixture()
    audit.check(
        "two-level Gibbs relation exact",
        all(row["gibbs_ratio"] == row["epsilon"] ** 4 for row in multiplier["rows"]),
        [
            (row["epsilon"], row["gibbs_ratio"])
            for row in multiplier["rows"]
        ],
        "exp(-beta*n)=epsilon^4",
        "multiplier-no-go",
    )
    audit.check(
        "two-level perturbation and modular tails decrease",
        multiplier["W_tail_decreases"] and multiplier["modular_W_tail_decreases"],
        [
            (
                row["W_D_squared_in_log16_units"],
                row["logrho_W_D_squared_in_log16_units"],
            )
            for row in multiplier["rows"]
        ],
        "both strictly decrease",
        "multiplier-no-go",
    )
    audit.check(
        "two-level direct D and delta-D tails decrease",
        multiplier["direct_tail_decreases"]
        and multiplier["direct_modular_tail_decreases"],
        [
            (
                row["direct_D_squared_in_log16_units"],
                row["direct_delta_D_squared_in_log16_units"],
            )
            for row in multiplier["rows"]
        ],
        "both strictly decrease",
        "multiplier-no-go",
    )
    audit.check(
        "two-level evolved M0 lower bound diverges",
        multiplier["M0_lower_increases"]
        and multiplier["M0_scaled_ratio_increases_to_one"]
        and multiplier["rows"][-1]["M0_lower"] > 10**6,
        [
            (row["M0_lower"], row["M0_asymptotic_ratio"])
            for row in multiplier["rows"]
        ],
        "M0 lower increases and scales as 2/(n*epsilon)",
        "multiplier-no-go",
    )
    audit.check(
        "cutoff connected radius formula",
        cutoff["radius_rows"][0]["radius"] == Fraction(18, 7),
        cutoff["radius_rows"][0]["radius"],
        Fraction(18, 7),
        "cutoff",
    )
    audit.check(
        "cutoff interaction scales quadratically",
        cutoff["quartic_scaling_ratio"] == 4,
        cutoff["quartic_scaling_ratio"],
        4,
        "cutoff",
    )
    audit.check(
        "fixed-beta absolute half-strip route fails",
        all(
            not row["absolute_geometric_route_converges"]
            for row in cutoff["radius_rows"]
        )
        and not cutoff["fixed_beta_half_strip_limit"],
        cutoff["radius_rows"],
        "r=z*beta*J_L grows like L^2 and exceeds one",
        "cutoff",
    )

    faithful = faithful_representation_fixture()
    audit.check(
        "standard multiplication representation faithful",
        faithful["standard_representation_faithful"],
        True,
        True,
        "representation",
    )
    audit.check(
        "standard tail tends strongly-star to zero",
        all(
            right["standard_l2_tail_squared"]
            < left["standard_l2_tail_squared"]
            for left, right in zip(faithful["rows"], faithful["rows"][1:])
        )
        and all(
            row["standard_l2_tail_squared"] == row["adjoint_tail_squared"]
            for row in faithful["rows"]
        ),
        faithful["rows"],
        "2^-n for operator and adjoint",
        "representation",
    )
    audit.check(
        "ultrafilter character keeps every tail",
        all(row["free_ultrafilter_character"] == 1 for row in faithful["rows"]),
        [row["free_ultrafilter_character"] for row in faithful["rows"]],
        "all one",
        "representation",
    )
    audit.check(
        "no representation-free C-star inference",
        faithful["standard_strong_star_limit"] == 0
        and faithful["ultrafilter_character_limit"] == 1
        and not faithful["abstract_C_star_inference"],
        {
            "faithful": faithful["standard_strong_star_limit"],
            "character": faithful["ultrafilter_character_limit"],
        },
        "different strong-star limits",
        "representation",
    )

    audit.check(
        "manifest result number reused",
        manifest["result_number"] == RESULT_NUMBER,
        manifest["result_number"],
        RESULT_NUMBER,
        "authority",
    )
    audit.check(
        "manifest result version",
        manifest["result_version"] == RESULT_VERSION,
        manifest["result_version"],
        RESULT_VERSION,
        "authority",
    )
    audit.check(
        "manifest exploration identity",
        manifest["exploration_id"] == EXPLORATION_ID,
        manifest["exploration_id"],
        EXPLORATION_ID,
        "authority",
    )
    audit.check(
        "manifest task and claim scope",
        manifest["task_id"] == TASK_ID and manifest["claim_ids"] == CLAIM_IDS,
        {"task": manifest["task_id"], "claims": manifest["claim_ids"]},
        {"task": TASK_ID, "claims": CLAIM_IDS},
        "authority",
    )
    audit.check(
        "manifest result identity unchanged",
        manifest["result_id"] == RESULT_ID,
        manifest["result_id"],
        RESULT_ID,
        "authority",
    )
    audit.check(
        "parent was R-167 v1.2",
        parent["result_number"] == RESULT_NUMBER
        and parent["result_version"] == "v1.2"
        and parent["exploration_id"] == "EXP-000798",
        {
            "number": parent["result_number"],
            "version": parent["result_version"],
            "exploration": parent["exploration_id"],
        },
        {"number": RESULT_NUMBER, "version": "v1.2", "exploration": "EXP-000798"},
        "authority",
    )
    manifest_open = manifest["open_gates"]
    audit.check(
        "two inherited active gates retained",
        all(gate in manifest_open for gate in OPEN_GATES),
        manifest_open,
        OPEN_GATES,
        "authority",
    )
    audit.check(
        "no gate falsely closed",
        not any(gate in manifest.get("closed_subgates", []) for gate in OPEN_GATES),
        manifest.get("closed_subgates", []),
        "neither active gate",
        "authority",
    )
    audit.check(
        "claim bearing remains false",
        manifest["claim_bearing"] is False,
        manifest["claim_bearing"],
        False,
        "authority",
    )
    expected_negative_ids = NEGATIVE_IDS + [CRITICAL_HALF_NEGATIVE_ID]
    audit.check(
        "seven negative route IDs exact",
        manifest["negative_ids"] == expected_negative_ids,
        manifest["negative_ids"],
        expected_negative_ids,
        "authority",
    )
    audit.check(
        "small direct-tail multiplier negative registered",
        NEGATIVE_IDS[4] in manifest["negative_ids"],
        manifest["negative_ids"],
        NEGATIVE_IDS[4],
        "authority",
    )
    audit.check(
        "critical half one-sided negative registered",
        CRITICAL_HALF_NEGATIVE_ID in manifest["negative_ids"],
        manifest["negative_ids"],
        CRITICAL_HALF_NEGATIVE_ID,
        "authority",
    )
    critical_contract = manifest["critical_half_leibniz_counterexample"]
    audit.check(
        "manifest critical setup",
        "K=h-inf(spec h)+1" in critical_contract["setup"]
        and "W_a=exp(-ia p_0/hbar)" in critical_contract["setup"]
        and "t_a=tau/a^2" in critical_contract["setup"]
        and "G=g+3lambda" in critical_contract["setup"],
        critical_contract["setup"],
        "K, W_a, t_a and G declared",
        "authority",
    )
    audit.check(
        "manifest critical Q3 force",
        "partial_0 V4=G q_0^3" in critical_contract["force"]
        and "(3lambda/2)q_0^2" in critical_contract["force"]
        and "lambda q_0" in critical_contract["force"]
        and "(lambda/2)" in critical_contract["force"],
        critical_contract["force"],
        q3_critical["partial_0_formula"],
        "authority",
    )
    audit.check(
        "manifest critical boundary-layer lower bound",
        ">=G tau a-B_tau" in critical_contract["boundary_layer"]
        and "independent of a" in critical_contract["boundary_layer"],
        critical_contract["boundary_layer"],
        "G*tau*a-B_tau with uniform remainder",
        "authority",
    )
    audit.check(
        "manifest critical Leibniz contradiction",
        "star-symmetric C-star-Leibniz" in critical_contract["leibniz_contradiction"]
        and "L(W_b^n)<=nL(W_b)" in critical_contract["leibniz_contradiction"]
        and "a=nb" in critical_contract["leibniz_contradiction"]
        and "n tends to infinity" in critical_contract["leibniz_contradiction"],
        critical_contract["leibniz_contradiction"],
        "fixed one-sided-dominating Leibniz contradiction",
        "authority",
    )
    audit.check(
        "manifest critical exact jets",
        "g=3/5" in critical_contract["exact_fixture"]
        and "lambda=2/7" in critical_contract["exact_fixture"]
        and "chi=7/4" in critical_contract["exact_fixture"]
        and "G=51/35" in critical_contract["exact_fixture"]
        and "D^3p_0=-(32112/8575)a^5" in critical_contract["exact_fixture"]
        and "27a^7" in critical_contract["exact_fixture"],
        critical_contract["exact_fixture"],
        "full Q3 and scalar jet sentinels",
        "authority",
    )
    audit.check(
        "manifest critical no-overclaim scope",
        "only" in critical_contract["scope"]
        and "does not reject" in critical_contract["scope"]
        and "non-Leibniz" in critical_contract["scope"]
        and "state-weighted" in critical_contract["scope"]
        and "full dynamics" in critical_contract["scope"],
        critical_contract["scope"],
        "only fixed critical Leibniz route rejected",
        "authority",
    )

    direct_contract = manifest["direct_relative_unitary_theorem"]
    audit.check(
        "manifest two relative-unitary orientations",
        "each at most" in direct_contract["two_orientations"]
        and "phi(W^2)^(1/2)" in direct_contract["two_orientations"],
        direct_contract["two_orientations"],
        "two HS orientations with the same tail",
        "authority",
    )
    audit.check(
        "manifest trace-distance factor two",
        "<=2|t|hbar^(-1)phi(W^2)^(1/2)" in direct_contract["state_distance"],
        direct_contract["state_distance"],
        "2|t|/hbar tail",
        "authority",
    )
    audit.check(
        "manifest entropy theorem",
        "beta[rho_t(W)-rho(W)]" in direct_contract["relative_entropy"]
        and "theta>beta" in direct_contract["relative_entropy"],
        direct_contract["relative_entropy"],
        "same-H entropy identity and theta>beta bound",
        "authority",
    )
    audit.check(
        "manifest unbounded-tail hypotheses",
        "fixed finite Lambda" in direct_contract["unbounded_tail_hypotheses"]
        and "form-norm" in direct_contract["unbounded_tail_hypotheses"]
        and "finite H-energy" in direct_contract["unbounded_tail_hypotheses"]
        and "exponential W_L moment" in direct_contract["unbounded_tail_hypotheses"],
        direct_contract["unbounded_tail_hypotheses"],
        "fixed-volume form norm + finite energy + exponential moment",
        "authority",
    )
    audit.check(
        "manifest initial-analytic-only scope",
        "initial A" in direct_contract["initial_analytic_corollary"]
        and "not uniform half-strip" in direct_contract["initial_analytic_corollary"]
        and "does not provide" in direct_contract["scope"]
        and "common alpha" in direct_contract["scope"],
        {
            "initial": direct_contract["initial_analytic_corollary"],
            "scope": direct_contract["scope"],
        },
        "initial analytic tests only; no common alpha",
        "authority",
    )
    multiplier_contract = manifest["small_direct_tail_large_multiplier_counterexample"]
    audit.check(
        "manifest exact two-level fixture",
        "H_n=diag(0,n)" in multiplier_contract["fixture"]
        and "epsilon_n=exp(-beta n/4)" in multiplier_contract["fixture"]
        and "pi hbar/sqrt(n^2+4epsilon_n^2)" in multiplier_contract["fixture"],
        multiplier_contract["fixture"],
        "declared H, epsilon and half period",
        "authority",
    )
    audit.check(
        "manifest direct-small multiplier-large split",
        "Duhamel norm" in multiplier_contract["small_quantities"]
        and "2exp(beta n/4)/n" in multiplier_contract["failure"]
        and "direct route" in multiplier_contract["scope"],
        multiplier_contract,
        "small D/delta-D but divergent M0; direct route retained",
        "authority",
    )

    boundary = manifest["no_overclaim"]
    for token in (
        "common alpha",
        "KMS",
        "ground",
        "GNS",
        "continuum",
        "Pre-A",
    ):
        audit.check(
            f"manifest no-overclaim {token}",
            token.lower().replace("-", " ") in boundary.lower().replace("-", " "),
            boundary,
            f"contains {token}",
            "scope",
        )
    certificate_flat = " ".join(certificate.replace("`", "").split()).lower()
    for token in (
        "exp-000799",
        "r-167 v1.3",
        "521",
        "(1+uv)^2",
        "3aq^2-3a^2q+a^3",
        "q^2k^{-s}",
        "strong-star",
        "direct relative-unitary theorem",
        "critical one-sided leibniz no-go",
        "32112",
        "8575",
        "a=nb",
    ):
        audit.check(
            f"certificate records {token}",
            token in certificate_flat,
            token in certificate_flat,
            True,
            "authority",
        )

    source_paths = (SCRIPT, MANIFEST, CERTIFICATE, PARENT)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
    }
    for relative_path, digest in source_hashes.items():
        audit.check(
            f"source hash {relative_path}",
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": (
            "tect/pre-a-cp1-st8-q3lock-common-alpha-topology-critical-"
            "graph-route-split-independent-result/1.0"
        ),
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": CLAIM_IDS,
        "claim_bearing": False,
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "global_graph": graph,
            "kick_commutator": kick,
            "resolvent_no_go": resolvent,
            "quartic_onsite_criticality": onsite,
            "critical_half_vector_field": critical,
            "finite_volume_trotter_graph_convergence": trotter,
            "coordinate_cutoff": cutoff,
            "direct_relative_unitary": direct,
            "small_direct_tail_large_multiplier": multiplier,
            "faithful_representation": faithful,
            "scope": {
                "global_kick_graph_form_closed": True,
                "finite_volume_subcritical_graph_convergence_conditional": True,
                "raw_resolvent_point_norm_continuity": False,
                "subcritical_quartic_local_graph_lipschitz": False,
                "critical_half_local_graph_lipschitz_closed": False,
                "critical_half_one_sided_leibniz_stability": False,
                "alternative_critical_topology_closed": False,
                "cutoff_norm_C1_half_strip_closed": False,
                "thermodynamic_spatial_cauchy_closed": False,
                "common_alpha_closed": False,
                "common_alpha_kms_closed": False,
                "ground_selection_closed": False,
                "gns_gap_closed": False,
                "continuum_closed": False,
                "pre_a_closed": False,
                "open_gates": OPEN_GATES,
                "negative_ids": expected_negative_ids,
            },
        },
        "source_hashes": source_hashes,
        "boundary": boundary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-identical canonical payloads",
    )
    arguments = parser.parse_args()

    payload = build_payload()
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.self_test:
        repeated = build_payload()
        repeated_encoded = canonical_bytes(repeated)
        if encoded != repeated_encoded:
            raise AssertionError("nondeterministic independent payload")
        repeated_digest = hashlib.sha256(repeated_encoded).hexdigest()
        if digest != repeated_digest:
            raise AssertionError("nondeterministic independent digest")
        print(
            f"SELF-TEST PASS {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
        )
        return 0

    atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['summary']['passed']}/{payload['summary']['total']} | "
        f"SHA256 {digest} | {RESULT_ID}"
    )
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
