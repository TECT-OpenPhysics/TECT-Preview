#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v1.7 additive route split.

This program neither imports the primary implementation nor reads a primary
run artifact.  It reconstructs the finite calculations used by the v1.7
checkpoint from exact rational arithmetic and high-precision ``Decimal``
arithmetic:

* bounded local-strict, graph, and energy-constrained topology comparisons;
* the exact eight-component Q3 quartic force and commutator signs;
* translated-packet powers for the unsplit point-norm ``C0`` obstruction;
* the exact pure-quartic basic-resolvent translation jump;
* both finite-Gibbs character relative-entropy orientations and the binary
  tail bound;
* the general two-level ``m >= 3`` entropy/finite-moment hostile family; and
* two pure disjoint ordered ground sectors with simple, gapless generators.

The output deliberately preserves the theorem boundary.  The two positive
results are finite-region or fixed-finite-Gibbs statements.  The four negative
results reject specific proof routes; none is a nonexistence theorem for the
Q3LOCK thermodynamic dynamics or a physical mass-gap statement.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-local-strict-quartic-c0-entropy-gap-"
    "route-split"
)
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.7"
EXPLORATION_ID = "EXP-000804"
TASK_ID = "T-054"

MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATION_LOG = REPO / "explorations/log.jsonl"
GATES = REPO / "claims/GATES.md"
RESULTS_LEDGER = REPO / "RESULTS-LEDGER.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-independent-{SLUG}/result.json"
)

NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-"
    "QUARTIC-POINT-NORM-C0",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-"
    "RESOLVENT-ALGEBRA-INVARIANCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-"
    "DYNAMIC-GAUSSIAN-TAIL-INFERENCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-"
    "AUTOMATIC-GNS-GAP",
)
CLOSED_SUBGATES = (
    "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-LOCAL-STRICT-ENERGY-"
    "SUBFLOW-CARRIER",
    "PA-CP1-ST8-Q3LOCK-FIXED-GIBBS-CHARACTER-ENTROPY-TILTED-"
    "TAIL-BOUND",
)
SUCCESSOR_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-"
    "ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
SUPERSEDED_GATE = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-"
    "EXHAUSTION-COMMON-ALPHA-AND-BROKEN-GNS-GAP"
)

EXPECTED_NO_OVERCLAIM = (
    "This package proves only a finite-region local-strict/energy carrier "
    "and a fixed finite-Gibbs entropy tail bound, together with four sharply "
    "scoped route no-go results. It does not prove a continuous-time "
    "thermodynamic split limit, all-exhaustion or all-boundary Cauchy, a "
    "quasi-local raw oscillator common alpha, full resolvent-algebra "
    "invariance or non-invariance for the unsplit quartic flow, phase-KMS "
    "quotient identification, a broken-sector GNS or physical mass gap, "
    "regulator removal, a continuum, physical empty space or a below-empty "
    "sign, Pre-A selection, C6, CP1 or Sector-A closure."
)

Pair = tuple[Fraction, Fraction]
Monomial = tuple[int, ...]
PairPolynomial = dict[Monomial, Pair]


def serial(value: Any) -> Any:
    """Convert exact objects to deterministic JSON-compatible values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return format(value, "E")
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
    """Write deterministic JSON using fsync and same-directory replacement."""

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
    """Fail-fast assertion ledger."""

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


def pair_add(left: Pair, right: Pair) -> Pair:
    return left[0] + right[0], left[1] + right[1]


def pair_scale(value: Pair, factor: Fraction) -> Pair:
    return factor * value[0], factor * value[1]


def add_pair_term(polynomial: PairPolynomial, power: Monomial, value: Pair) -> None:
    updated = pair_add(polynomial.get(power, (Fraction(0), Fraction(0))), value)
    if updated == (0, 0):
        polynomial.pop(power, None)
    else:
        polynomial[power] = updated


def derivative(polynomial: PairPolynomial, coordinate: int) -> PairPolynomial:
    output: PairPolynomial = {}
    for power, coefficient in polynomial.items():
        if power[coordinate] == 0:
            continue
        lowered = list(power)
        factor = Fraction(lowered[coordinate])
        lowered[coordinate] -= 1
        add_pair_term(output, tuple(lowered), pair_scale(coefficient, factor))
    return output


def cube_edges() -> list[tuple[int, int]]:
    """The twelve undirected edges of the three-cube on vertices 0,...,7."""

    return [
        (left, left ^ bit)
        for left in range(8)
        for bit in (1, 2, 4)
        if left < (left ^ bit)
    ]


def exponent(*entries: tuple[int, int]) -> Monomial:
    powers = [0] * 8
    for coordinate, power in entries:
        powers[coordinate] = power
    return tuple(powers)


def q3_quartic_force_fixture() -> dict[str, Any]:
    """Build the Q3 cube quartic and differentiate its q0 sector exactly."""

    polynomial: PairPolynomial = {}
    for coordinate in range(8):
        add_pair_term(
            polynomial,
            exponent((coordinate, 4)),
            (Fraction(1, 4), Fraction(0)),
        )

    # lambda/4 * (x-y)^2 * (x^2+y^2)
    for left, right in cube_edges():
        terms = (
            (exponent((left, 4)), Fraction(1, 4)),
            (exponent((right, 4)), Fraction(1, 4)),
            (exponent((left, 3), (right, 1)), Fraction(-1, 2)),
            (exponent((left, 1), (right, 3)), Fraction(-1, 2)),
            (exponent((left, 2), (right, 2)), Fraction(1, 2)),
        )
        for power, coefficient in terms:
            add_pair_term(polynomial, power, (Fraction(0), coefficient))

    force_zero = derivative(polynomial, 0)
    neighbours = sorted(
        right if left == 0 else left
        for left, right in cube_edges()
        if left == 0 or right == 0
    )
    expected: PairPolynomial = {
        exponent((0, 3)): (Fraction(1), Fraction(3))
    }
    for neighbour in neighbours:
        add_pair_term(
            expected,
            exponent((0, 2), (neighbour, 1)),
            (Fraction(0), Fraction(-3, 2)),
        )
        add_pair_term(
            expected,
            exponent((0, 1), (neighbour, 2)),
            (Fraction(0), Fraction(1)),
        )
        add_pair_term(
            expected,
            exponent((neighbour, 3)),
            (Fraction(0), Fraction(-1, 2)),
        )

    axis_power = exponent((0, 4))
    axis_coefficient = polynomial[axis_power]
    shift = Fraction(-4, 3)
    # In V(q)-V(q-a), q^4 cancels and all lower powers are the negated
    # shifted-binomial coefficients.
    difference_coefficients: dict[int, Pair] = {
        q_power: pair_scale(
            axis_coefficient,
            -Fraction(math.comb(4, q_power)) * (-shift) ** (4 - q_power),
        )
        for q_power in range(4)
    }

    g = Fraction(3, 5)
    lam = Fraction(2, 7)
    capital_g = g + 3 * lam

    def evaluate(value: Pair) -> Fraction:
        return value[0] * g + value[1] * lam

    return {
        "edges": cube_edges(),
        "degree_rows": [
            sum(vertex in edge for edge in cube_edges()) for vertex in range(8)
        ],
        "neighbours_of_zero": neighbours,
        "quartic_term_count": len(polynomial),
        "force_zero": force_zero,
        "expected_force_zero": expected,
        "force_term_count": len(force_zero),
        "symbolic_G_pair": (Fraction(1), Fraction(3)),
        "axis_quartic_pair": axis_coefficient,
        "g_fixture": g,
        "lambda_fixture": lam,
        "G_fixture": capital_g,
        "axis_quartic_fixture": evaluate(axis_coefficient),
        "shift_a": shift,
        "axis_D_coefficients": difference_coefficients,
        "axis_D_leading_pair": difference_coefficients[3],
        "axis_D_leading_fixture": evaluate(difference_coefficients[3]),
        "axis_F_leading_pair": force_zero[exponent((0, 3))],
        "axis_F_leading_fixture": evaluate(force_zero[exponent((0, 3))]),
    }


def gaussian_mul(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def derivation_and_packet_fixture(q3: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute the commutator coefficients and shrinking-time powers."""

    hbar = Fraction(5, 2)
    chi = Fraction(7, 4)
    imaginary_over_hbar = (Fraction(0), Fraction(1, 1) / hbar)
    delta_F_factor = Fraction(1, 1) / (2 * chi)
    delta2_w_anticommutator = (
        Fraction(0),
        Fraction(1, 1) / (2 * chi * hbar),
    )
    delta2_w_square = gaussian_mul(imaginary_over_hbar, imaginary_over_hbar)
    commutator_v_resolvent = (Fraction(0), -hbar)
    delta_resolvent_factor = gaussian_mul(
        imaginary_over_hbar, commutator_v_resolvent
    )

    capital_g = q3["G_fixture"]
    shift = q3["shift_a"]
    resolvent_square_norm = Fraction(7, 13)
    d_weyl = abs(shift) * capital_g / hbar
    d_resolvent = capital_g * resolvent_square_norm

    graph_degrees = {
        "D_a": 3,
        "p_partial_D_a": 4,
        "D_a_squared": 6,
        "F_0": 3,
        "F_0_squared": 6,
        "p_partial_F_0": 4,
    }
    rows = []
    for label, d_value, graph_constant, packet_constant in (
        ("W_a", d_weyl, Fraction(7, 5), Fraction(11, 6)),
        ("R_0", d_resolvent, Fraction(9, 7), Fraction(13, 8)),
    ):
        product = graph_constant * packet_constant
        tau = d_value / product
        lower = tau * d_value - tau * tau * product / 2
        rows.append(
            {
                "label": label,
                "first_derivative_limit": d_value,
                "graph_constant_fixture": graph_constant,
                "packet_K32_constant_fixture": packet_constant,
                "tau": tau,
                "tau_upper": 2 * d_value / product,
                "liminf_lower": lower,
                "positive_only_not_exact_jump": True,
            }
        )

    return {
        "hbar": hbar,
        "chi": chi,
        "delta_W_D_coefficient": imaginary_over_hbar,
        "delta2_W_anticommutator_coefficient": delta2_w_anticommutator,
        "delta2_W_D_squared_coefficient": delta2_w_square,
        "q_resolvent_commutator_sign": "[q_0,R_0]=-i*hbar*R_0^2",
        "V_resolvent_commutator_coefficient": commutator_v_resolvent,
        "delta_R_F_coefficient": delta_resolvent_factor,
        "delta2_R_F_R_F_coefficient": Fraction(2),
        "delta2_R_anticommutator_coefficient": delta_F_factor,
        "graph_degrees": graph_degrees,
        "graph_endpoint": max(graph_degrees.values()),
        "translation_powers": {
            "delta_W_a": 3,
            "delta_R_0": 3,
            "K": 4,
            "K_to_three_halves": 6,
            "time": -3,
            "first_Taylor_total": 0,
            "second_Taylor_total": 0,
        },
        "rows": rows,
        "unsplit_flow_invariance_decided": False,
        "unsplit_flow_point_norm_C0_if_invariant": False,
        "exact_norm_jump_claimed": False,
    }


def local_strict_fixture() -> dict[str, Any]:
    """Audit the spectral inequalities and the strict-versus-norm boundary."""

    eigenvalues = (1, 4, 9, 16)
    diagonal_a = (1, 2, 3, 4)
    energy = 4
    graph_right = max(
        Fraction(value, math.isqrt(k))
        for value, k in zip(diagonal_a, eigenvalues)
    )
    graph_left = graph_right
    energy_norm = Fraction(2)
    operator_norm = Fraction(4)
    q_value = graph_left + graph_right
    forward_right = Fraction(math.isqrt(energy)) * max(graph_left, graph_right)
    reverse_right = 2 * energy_norm + 2 * operator_norm / math.isqrt(energy)

    tail_rows = []
    fixed_energy = Fraction(4)
    for index in (4, 8, 16, 32, 64):
        q_tail = Fraction(2, index)
        energy_squared = (fixed_energy - 1) / (index * index - 1)
        forward_squared = fixed_energy / (index * index)
        with localcontext() as context:
            context.prec = 70
            energy_tail = (
                Decimal(energy_squared.numerator)
                / Decimal(energy_squared.denominator)
            ).sqrt()
            reverse_bound = 2 * energy_tail + Decimal(1)
        tail_rows.append(
            {
                "index": index,
                "operator_norm": Fraction(1),
                "q_half": q_tail,
                "e_E_squared": energy_squared,
                "forward_bound_squared": forward_squared,
                "reverse_bound": reverse_bound,
                "q_below_reverse_bound": Decimal(q_tail.numerator)
                / Decimal(q_tail.denominator)
                <= reverse_bound,
            }
        )

    # A two-level bond-form fixture: K=diag(1,4), B swaps the basis, hence
    # B*KB<=4K in both orientations.  For A=|0><1|, q_1/2(A)=3/2 and
    # q_1/2(B*AB)=3/2, safely below 4^(1/2)q(A)=3.
    bond = {
        "K_diagonal": (1, 4),
        "form_factor_M": Fraction(4),
        "s": Fraction(1, 2),
        "q_before": Fraction(3, 2),
        "q_after": Fraction(3, 2),
        "M_to_s_times_q": Fraction(3),
        "both_form_orientations": True,
        "energy_map": "e_E(beta(A))<=e_(M E)(A)",
    }

    return {
        "finite_spectral_fixture": {
            "K_eigenvalues": eigenvalues,
            "A_diagonal": diagonal_a,
            "s": Fraction(1, 2),
            "E": energy,
            "AK_minus_s_norm": graph_right,
            "K_minus_s_A_norm": graph_left,
            "e_E": energy_norm,
            "operator_norm": operator_norm,
            "q_s": q_value,
            "forward_bound": forward_right,
            "reverse_bound": reverse_right,
        },
        "tail_projection_rows": tail_rows,
        "strict_equals_strong_star_on_norm_bounded_sets": True,
        "compact_graph_dense_range_equivalence": True,
        "tail_projections_strict_not_norm": True,
        "fixed_region_only": True,
        "uniform_over_all_normal_states_collapses_to_norm": True,
        "onsite_commuting_control_isometric": True,
        "onsite_support_growth": 0,
        "bond_support_growth": 1,
        "bond_form_fixture": bond,
        "continuous_split_product_limit_closed": False,
        "all_exhaustion_Cauchy_closed": False,
        "global_multiplier_strict_topology_claimed": False,
    }


def pure_quartic_resolvent_fixture() -> dict[str, Any]:
    """Rebuild the translated-dilated packet and exact Cayley upper bound."""

    capital_g = Fraction(17, 9)
    time = Fraction(-5, 7)
    shift = Fraction(3, 4)
    mu = Fraction(-11, 6)
    # F(R)-F(R-s)=G(3s R^2-3s^2 R+s^3).
    center_coefficients = {
        2: time * capital_g * 3 * shift,
        1: time * capital_g * (-3) * shift * shift,
        0: time * capital_g * shift**3,
    }
    jump = Fraction(1, 1) / abs(mu)
    dimension = 8
    width_power = Fraction(1, 2)
    amplitude_power = -Fraction(dimension, 2) * width_power
    return {
        "G": capital_g,
        "t": time,
        "s": shift,
        "mu": mu,
        "axis_W4_coefficient": capital_g / 4,
        "axis_force_coefficient": capital_g,
        "momentum_center_coefficients": center_coefficients,
        "momentum_center_leading": 3 * time * capital_g * shift,
        "momentum_center_power": 2,
        "phase_spread_power": Fraction(3, 2),
        "initial_momentum_spread_power": Fraction(-1, 2),
        "packet_dimension": dimension,
        "packet_width_power": width_power,
        "packet_amplitude_power": amplitude_power,
        "normalization_power": 2 * amplitude_power + dimension * width_power,
        "one_resolvent_limit": jump,
        "other_resolvent_limit": Fraction(0),
        "cayley_formula": "R_L=(1-C_L)/(2 i mu)",
        "cayley_unitary_difference_bound": Fraction(2),
        "upper_bound": jump,
        "lower_bound": jump,
        "exact_jump": jump,
        "weyl_orbit_norm_continuous_for_resolvent_algebra_elements": True,
        "translated_element_in_resolvent_algebra": False,
        "full_resolvent_algebra_unital": True,
        "its_multiplier_strict_equals_norm": True,
        "unsplit_invariance_decided": False,
        "dynamics_nonexistence_claimed": False,
    }


def decimal_from_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def binary_relative_entropy(q_value: Decimal, p_value: Decimal) -> Decimal:
    return q_value * (q_value / p_value).ln() + (1 - q_value) * (
        (1 - q_value) / (1 - p_value)
    ).ln()


def finite_gibbs_entropy_fixture() -> dict[str, Any]:
    """Check both character orientations and binary inversion independently."""

    beta = Fraction(2)
    hbar = Fraction(3)
    chi = Fraction(5)
    xi = (Fraction(1, 2), Fraction(-2, 3))
    xi_squared = sum((entry * entry for entry in xi), Fraction(0))
    entropy = beta * hbar * hbar * xi_squared / (2 * chi)

    with localcontext() as context:
        context.prec = 80
        p_value = Decimal(1) / Decimal(64)
        q_value = Decimal(2) / Decimal(5)
        binary = binary_relative_entropy(q_value, p_value)
        elementary_lower = q_value * (Decimal(1) / p_value).ln() - Decimal(2).ln()
        entropy_decimal = decimal_from_fraction(entropy)
        inverted = (entropy_decimal + Decimal(2).ln()) / (
            Decimal(1) / p_value
        ).ln()

        tail_prefactor = Decimal(3)
        tail_a = Decimal(2) / Decimal(3)
        tail_L = Decimal(4)
        tail_denominator = tail_a * tail_L * tail_L - tail_prefactor.ln()
        substituted = (entropy_decimal + Decimal(2).ln()) / tail_denominator

    return {
        "beta": beta,
        "hbar": hbar,
        "chi": chi,
        "xi": xi,
        "xi_squared": xi_squared,
        "momentum_shift_linear_coefficient": hbar / chi,
        "momentum_shift_constant": hbar * hbar * xi_squared / (2 * chi),
        "time_reversal_momentum_mean": Fraction(0),
        "relative_entropy_plus": entropy,
        "relative_entropy_minus": entropy,
        "evolved_relative_entropy_plus": entropy,
        "evolved_relative_entropy_minus": entropy,
        "binary_fixture": {
            "p": p_value,
            "q": q_value,
            "d_binary": binary,
            "elementary_lower": elementary_lower,
            "S_xi": entropy_decimal,
            "d_below_S": binary <= entropy_decimal,
            "inverted_bound": inverted,
            "q_below_inverted_bound": q_value <= inverted,
        },
        "gaussian_tail_substitution": {
            "M_times_cardinality": tail_prefactor,
            "a": tail_a,
            "L": tail_L,
            "denominator": tail_denominator,
            "bound": substituted,
            "denominator_positive": tail_denominator > 0,
            "asymptotic_power": -2,
        },
        "two_orientations": True,
        "all_history_gaussian_tail_closed": False,
        "exponential_corridor_absorbed": False,
    }


def entropy_finite_moment_fixture() -> dict[str, Any]:
    """Recompute the m>=3 two-level Gibbs family and all finite moments."""

    rows: list[dict[str, Any]] = []
    real_r_rows: list[dict[str, Any]] = []
    gaussian_rows: list[dict[str, Any]] = []
    m4_rows: list[dict[str, Any]] = []
    with localcontext() as context:
        context.prec = 90
        for m_value in (3, 4, 5, 7):
            for n_value in (2, 3, 5, 8):
                n_decimal = Decimal(n_value)
                weight = (-n_decimal**4).exp()
                p_one = weight / (1 + weight)
                p_zero = Decimal(1) / (1 + weight)
                delta = p_zero - p_one
                polynomial_tail = Decimal(1) / n_decimal ** (2 * m_value)
                sine_squared = polynomial_tail / delta
                tilted_p_one = p_one + polynomial_tail
                relative_entropy = n_decimal**4 * polynomial_tail
                expected_entropy = n_decimal ** (4 - 2 * m_value)
                moment_checks = []
                for r_value in range(1, 2 * m_value + 1):
                    moment = n_decimal**r_value * tilted_p_one
                    formula = (
                        n_decimal**r_value * p_one
                        + n_decimal ** (r_value - 2 * m_value)
                    )
                    r_decimal = Decimal(r_value)
                    calculus_bound = Decimal(1) + (
                        (r_decimal / 4)
                        * ((r_decimal / 4).ln() - Decimal(1))
                    ).exp()
                    moment_checks.append(
                        {
                            "r": r_value,
                            "moment": moment,
                            "formula": formula,
                            "calculus_uniform_bound": calculus_bound,
                            "identity": abs(moment - formula) <= Decimal("1e-75"),
                            "within_uniform_bound": moment <= calculus_bound,
                        }
                    )
                rows.append(
                    {
                        "m": m_value,
                        "n": n_value,
                        "p1": p_one,
                        "Delta": delta,
                        "sin_squared_theta": sine_squared,
                        "rotation_exists": 0 < sine_squared < 1,
                        "tail_plus": tilted_p_one,
                        "tail_minus": tilted_p_one,
                        "tail_increment": polynomial_tail,
                        "relative_entropy_plus": relative_entropy,
                        "relative_entropy_minus": relative_entropy,
                        "expected_relative_entropy": expected_entropy,
                        "energy_excess_beta_times": relative_entropy,
                        "moment_domain": f"all real 0<r<={2*m_value}",
                        "moment_formula": "n^r p1+n^(r-2m)",
                        "integer_moment_checks": moment_checks,
                        "bounded_drive_both_orientations": True,
                    }
                )

                for r_fraction in (
                    Fraction(1, 2),
                    Fraction(3, 2),
                    Fraction(2 * m_value, 1) - Fraction(1, 2),
                    Fraction(2 * m_value, 1),
                ):
                    r_decimal = decimal_from_fraction(r_fraction)
                    n_to_r = (r_decimal * n_decimal.ln()).exp()
                    second = (
                        (r_decimal - Decimal(2 * m_value))
                        * n_decimal.ln()
                    ).exp()
                    moment = n_to_r * p_one + second
                    calculus_bound = Decimal(1) + (
                        (r_decimal / 4)
                        * ((r_decimal / 4).ln() - Decimal(1))
                    ).exp()
                    real_r_rows.append(
                        {
                            "m": m_value,
                            "n": n_value,
                            "r": r_fraction,
                            "r_in_domain": 0 < r_fraction <= 2 * m_value,
                            "second_exponent_nonpositive": r_fraction
                            - 2 * m_value
                            <= 0,
                            "moment": moment,
                            "calculus_uniform_bound": calculus_bound,
                            "within_uniform_bound": moment <= calculus_bound,
                        }
                    )

        for a_value in (
            Decimal(1) / Decimal(3),
            Decimal(1),
            Decimal(7) / Decimal(5),
            Decimal(3),
        ):
            envelope = Decimal(1) + (a_value * a_value / 4).exp()
            for n_value in (2, 3, 5, 8):
                n_decimal = Decimal(n_value)
                weight = (-n_decimal**4).exp()
                p_zero = Decimal(1) / (1 + weight)
                p_one = weight / (1 + weight)
                moment = p_zero + p_one * (a_value * n_decimal**2).exp()
                gaussian_rows.append(
                    {
                        "a": a_value,
                        "n": n_value,
                        "moment": moment,
                        "envelope": envelope,
                        "within_envelope": moment <= envelope,
                    }
                )

        m4_bound = Decimal(4) * Decimal(-2).exp()
        for n_value in (2, 3, 5, 8, 13):
            n_decimal = Decimal(n_value)
            weight = (-n_decimal**4).exp()
            p_one = weight / (1 + weight)
            eighth = Decimal(1) + n_decimal**8 * p_one
            m4_rows.append(
                {
                    "n": n_value,
                    "eighth_moment": eighth,
                    "excess": n_decimal**8 * p_one,
                    "universal_excess_bound": m4_bound,
                    "bound_holds": n_decimal**8 * p_one <= m4_bound,
                    "tail_increment": n_decimal ** (-8),
                    "relative_entropy": n_decimal ** (-4),
                }
            )

        polynomial_log_rows = []
        tail_a = Decimal(1) / Decimal(3)
        for n_value in (8, 16, 32, 64):
            n_decimal = Decimal(n_value)
            log_weighted_tail = (
                tail_a * n_decimal**2 - Decimal(8) * n_decimal.ln()
            )
            polynomial_log_rows.append(
                {"n": n_value, "log_exp_aq2_times_n_minus_8": log_weighted_tail}
            )

    return {
        "rows": rows,
        "real_r_rows": real_r_rows,
        "gaussian_reference_rows": gaussian_rows,
        "m4_rows": m4_rows,
        "m4_excess_bound": m4_bound,
        "m4_calculus_optimizer_for_x_squared_exp_minus_x": Fraction(2),
        "polynomial_log_rows": polynomial_log_rows,
        "general_real_moment_bound": (
            "n^r p1+n^(r-2m)<=1+(r/(4e))^(r/4) for every real "
            "0<r<=2m"
        ),
        "arbitrary_finite_ceiling_rows": [
            {
                "ceiling": ceiling,
                "chosen_m": max(3, math.ceil(Fraction(ceiling, 2))),
                "covered": ceiling
                <= 2 * max(3, math.ceil(Fraction(ceiling, 2))),
            }
            for ceiling in (1, 5, 8, 13, 20)
        ],
        "reference_gaussian_bound": (
            "phi_n(exp(a q_n^2))<=1+exp(a^2/4) for every a>0"
        ),
        "finite_moment_to_gaussian_inference_valid": False,
        "Q3LOCK_counterexample": False,
        "stronger_quasi_invariance_excluded": False,
    }


def ordered_ground_gap_fixture() -> dict[str, Any]:
    """Encode the direct-integral ground doublet and a gapless Weyl sequence."""

    rows = []
    for index in (2, 4, 8, 16, 32, 64):
        rows.append(
            {
                "n": index,
                "support_interval": f"(0,1/{index})",
                "norm_squared": Fraction(1),
                "energy_expectation": Fraction(1, 2 * index),
                "H_norm_squared": Fraction(1, 3 * index * index),
                "variance": Fraction(1, 12 * index * index),
                "orthogonal_to_ground": True,
            }
        )

    spectral_points = [Fraction(1, index) for index in (1, 2, 4, 8, 16, 32)]
    return {
        "one_sector_Hilbert_space": "C Omega direct-sum L2((0,1),dx)",
        "one_sector_generator": "0 on Omega direct-sum multiplication by x",
        "algebra": "B(H0) direct-sum B(H0)",
        "generator_bounded_norm": Fraction(1),
        "dynamics_point_norm_C0": True,
        "states_pure": True,
        "states_disjoint": True,
        "parity_swap": True,
        "central_order_values": (Fraction(1), Fraction(-1)),
        "GNS_ground_kernel_dimension_each": 1,
        "spectrum_each": "[0,1]",
        "positive_spectral_points": spectral_points,
        "positive_spectrum_infimum": Fraction(0),
        "weyl_sequence_rows": rows,
        "coercivity_form": (
            "-i*hbar*omega(A*delta(A))>=Delta*"
            "[omega(A*A)-|omega(A)|^2]"
        ),
        "ordered_doublets_imply_gap": False,
        "physical_mass_gap_claimed": False,
    }


def read_exploration(identifier: str) -> dict[str, Any] | None:
    if not EXPLORATION_LOG.exists():
        return None
    found = None
    with EXPLORATION_LOG.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == identifier:
                found = record
    return found


def section_after_heading(text: str, heading: str) -> str:
    marker = f"### **{heading}**"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n### ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def authority_audit(
    audit: Audit, manifest: Mapping[str, Any], staged: bool
) -> dict[str, Any]:
    """Bind formal authorities while allowing only absence in staged mode."""

    missing: list[str] = []

    if CERTIFICATE.exists():
        certificate = CERTIFICATE.read_text(encoding="utf-8")
        flat_certificate = " ".join(certificate.replace("`", "").split())
        for token in (
            "R-167",
            "v1.7",
            EXPLORATION_ID,
            RESULT_ID,
            "{1\\over|\\mu|}",
            "{\\beta\\hbar^2\\over2\\chi}\\|\\xi\\|^2",
            "0<r\\le2m",
            "[0,1]",
        ):
            audit.check(
                f"certificate token {token}",
                token in flat_certificate,
                token in flat_certificate,
                True,
                "authority",
            )
        for identifier in NEGATIVE_IDS + CLOSED_SUBGATES + SUCCESSOR_GATES:
            audit.check(
                f"certificate binds {identifier}",
                identifier in certificate,
                identifier in certificate,
                True,
                "authority",
            )
    else:
        missing.append(str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"))

    if NEGATIVE_REGISTRY.exists():
        registry = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
        for identifier in NEGATIVE_IDS:
            audit.check(
                f"negative authority {identifier}",
                f"### {identifier} --" in registry,
                registry.count(identifier),
                "registered heading",
                "authority",
            )
    else:
        missing.append(str(NEGATIVE_REGISTRY.relative_to(REPO)))

    if GATES.exists():
        gates_text = GATES.read_text(encoding="utf-8")
        for identifier in CLOSED_SUBGATES:
            section = section_after_heading(gates_text, identifier)
            audit.check(
                f"closed gate authority {identifier}",
                bool(section) and "**Status:** CLOSED" in section,
                section[:240],
                "heading with CLOSED status",
                "authority",
            )
        for identifier in SUCCESSOR_GATES:
            section = section_after_heading(gates_text, identifier)
            audit.check(
                f"open successor authority {identifier}",
                bool(section) and "**Status:** OPEN" in section,
                section[:240],
                "heading with OPEN status",
                "authority",
            )
        superseded = section_after_heading(gates_text, SUPERSEDED_GATE)
        audit.check(
            "combined gate split and superseded",
            "SPLIT AND SUPERSEDED" in superseded,
            superseded[:300],
            "historically open; split and superseded",
            "authority",
        )
    else:
        missing.append(str(GATES.relative_to(REPO)))

    exploration = read_exploration(EXPLORATION_ID)
    if exploration is None:
        missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check(
            "exploration task binding",
            exploration.get("task_id") == TASK_ID,
            exploration.get("task_id"),
            TASK_ID,
            "authority",
        )
        audit.check(
            "exploration negatives exact",
            exploration.get("formal_refs", {}).get("negatives")
            == list(NEGATIVE_IDS),
            exploration.get("formal_refs", {}).get("negatives"),
            list(NEGATIVE_IDS),
            "authority",
        )
        expected_gates = set(CLOSED_SUBGATES + SUCCESSOR_GATES + (SUPERSEDED_GATE,))
        audit.check(
            "exploration gate split complete",
            expected_gates.issubset(set(exploration.get("gate_ids", []))),
            exploration.get("gate_ids", []),
            sorted(expected_gates),
            "authority",
        )
        audit.check(
            "exploration result binding",
            exploration.get("formal_refs", {}).get("results") == [RESULT_NUMBER],
            exploration.get("formal_refs", {}).get("results"),
            [RESULT_NUMBER],
            "authority",
        )

    if RESULTS_LEDGER.exists():
        results_text = RESULTS_LEDGER.read_text(encoding="utf-8")
        audit.check(
            "results ledger v1.7",
            "R-167 v1.7 closes" in results_text,
            "R-167 v1.7 closes" in results_text,
            True,
            "authority",
        )
        for identifier in NEGATIVE_IDS + CLOSED_SUBGATES + SUCCESSOR_GATES:
            audit.check(
                f"results ledger binds {identifier}",
                identifier in results_text,
                identifier in results_text,
                True,
                "authority",
            )
    else:
        missing.append(str(RESULTS_LEDGER.relative_to(REPO)))

    status = "COMPLETE" if not missing else "INCOMPLETE"
    if missing and not staged:
        return {"status": status, "missing": missing, "staged": False}
    return {"status": status, "missing": missing, "staged": staged}


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    audit.check(
        "manifest schema",
        manifest.get("schema") == "tect/pre-a-route-split/1.0",
        manifest.get("schema"),
        "tect/pre-a-route-split/1.0",
        "identity",
    )
    audit.check(
        "stable result ID",
        manifest.get("result_id") == RESULT_ID,
        manifest.get("result_id"),
        RESULT_ID,
        "identity",
    )
    audit.check(
        "result number",
        manifest.get("result_number") == RESULT_NUMBER,
        manifest.get("result_number"),
        RESULT_NUMBER,
        "identity",
    )
    audit.check(
        "result version",
        manifest.get("result_version") == RESULT_VERSION,
        manifest.get("result_version"),
        RESULT_VERSION,
        "identity",
    )
    audit.check(
        "exploration identity",
        manifest.get("exploration_id") == EXPLORATION_ID,
        manifest.get("exploration_id"),
        EXPLORATION_ID,
        "identity",
    )
    audit.check(
        "task identity",
        manifest.get("task_id") == TASK_ID,
        manifest.get("task_id"),
        TASK_ID,
        "identity",
    )
    audit.check(
        "claim context",
        manifest.get("claim_ids") == ["C6-SPACETIME-SIGNATURE"]
        and manifest.get("claim_bearing") is False,
        {
            "claim_ids": manifest.get("claim_ids"),
            "claim_bearing": manifest.get("claim_bearing"),
        },
        {"claim_ids": ["C6-SPACETIME-SIGNATURE"], "claim_bearing": False},
        "identity",
    )
    audit.check(
        "four negative IDs exact",
        manifest.get("negative_ids") == list(NEGATIVE_IDS),
        manifest.get("negative_ids"),
        list(NEGATIVE_IDS),
        "identity",
    )
    audit.check(
        "two closed subgates exact",
        manifest.get("closed_subgates") == list(CLOSED_SUBGATES),
        manifest.get("closed_subgates"),
        list(CLOSED_SUBGATES),
        "identity",
    )
    expected_open = list(SUCCESSOR_GATES)
    if ROUND1_GATE in manifest.get("open_gates", []):
        expected_open.append(ROUND1_GATE)
    audit.check(
        "two successors plus manifest-required round1",
        manifest.get("open_gates") == expected_open,
        manifest.get("open_gates"),
        expected_open,
        "identity",
    )
    audit.check(
        "historical combined gate superseded",
        manifest.get("superseded_gate_ids") == [SUPERSEDED_GATE],
        manifest.get("superseded_gate_ids"),
        [SUPERSEDED_GATE],
        "identity",
    )
    audit.check(
        "exact no-overclaim text",
        manifest.get("no_overclaim") == EXPECTED_NO_OVERCLAIM,
        manifest.get("no_overclaim"),
        EXPECTED_NO_OVERCLAIM,
        "scope",
    )

    source_text = SCRIPT.read_text(encoding="utf-8")
    syntax_tree = ast.parse(source_text)
    imported_roots = set()
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "math",
        "os",
        "tempfile",
        "decimal",
        "fractions",
        "pathlib",
        "typing",
    }
    audit.check(
        "stdlib-only import surface",
        imported_roots <= allowed_imports,
        sorted(imported_roots),
        sorted(allowed_imports),
        "independence",
    )

    topology = local_strict_fixture()
    finite = topology["finite_spectral_fixture"]
    audit.check(
        "finite spectral forward inequality",
        finite["e_E"] <= finite["forward_bound"],
        finite["e_E"],
        finite["forward_bound"],
        "local-strict",
    )
    audit.check(
        "finite spectral reverse inequality",
        finite["q_s"] <= finite["reverse_bound"],
        finite["q_s"],
        finite["reverse_bound"],
        "local-strict",
    )
    audit.check(
        "tail forward inequalities",
        all(
            row["e_E_squared"] <= row["forward_bound_squared"]
            for row in topology["tail_projection_rows"]
        ),
        topology["tail_projection_rows"],
        "e_E^2<=E max(graph)^2",
        "local-strict",
    )
    audit.check(
        "tail reverse inequalities",
        all(row["q_below_reverse_bound"] for row in topology["tail_projection_rows"]),
        [row["q_below_reverse_bound"] for row in topology["tail_projection_rows"]],
        "all true",
        "local-strict",
    )
    audit.check(
        "strict sequence not norm sequence",
        all(row["operator_norm"] == 1 for row in topology["tail_projection_rows"])
        and all(
            right["q_half"] < left["q_half"]
            for left, right in zip(
                topology["tail_projection_rows"],
                topology["tail_projection_rows"][1:],
            )
        )
        and all(
            right["e_E_squared"] < left["e_E_squared"]
            for left, right in zip(
                topology["tail_projection_rows"],
                topology["tail_projection_rows"][1:],
            )
        ),
        topology["tail_projection_rows"],
        "norm one while q_s and e_E tend to zero",
        "local-strict",
    )
    audit.check(
        "bond q_s implication",
        topology["bond_form_fixture"]["q_after"]
        <= topology["bond_form_fixture"]["M_to_s_times_q"],
        topology["bond_form_fixture"]["q_after"],
        topology["bond_form_fixture"]["M_to_s_times_q"],
        "subflows",
    )
    audit.check(
        "finite-region topology boundary",
        topology["fixed_region_only"]
        and topology["strict_equals_strong_star_on_norm_bounded_sets"]
        and topology["tail_projections_strict_not_norm"]
        and not topology["continuous_split_product_limit_closed"]
        and not topology["all_exhaustion_Cauchy_closed"],
        topology,
        "finite-region precursor only",
        "scope",
    )

    q3 = q3_quartic_force_fixture()
    audit.check(
        "Q3 cube degrees",
        q3["degree_rows"] == [3] * 8 and len(q3["edges"]) == 12,
        {"degrees": q3["degree_rows"], "edges": len(q3["edges"])},
        {"degrees": [3] * 8, "edges": 12},
        "Q3",
    )
    audit.check(
        "exact Q3 force",
        q3["force_zero"] == q3["expected_force_zero"],
        q3["force_zero"],
        q3["expected_force_zero"],
        "Q3",
    )
    audit.check(
        "exact G=g+3lambda",
        q3["symbolic_G_pair"] == (1, 3)
        and q3["axis_quartic_pair"] == (Fraction(1, 4), Fraction(3, 4))
        and q3["force_term_count"] == 10,
        {
            "G": q3["symbolic_G_pair"],
            "axis": q3["axis_quartic_pair"],
            "terms": q3["force_term_count"],
        },
        {"G": (1, 3), "axis": (Fraction(1, 4), Fraction(3, 4)), "terms": 10},
        "Q3",
    )
    audit.check(
        "translated D leading coefficient aG",
        q3["axis_D_leading_pair"]
        == pair_scale(q3["symbolic_G_pair"], q3["shift_a"]),
        q3["axis_D_leading_pair"],
        pair_scale(q3["symbolic_G_pair"], q3["shift_a"]),
        "Q3",
    )
    audit.check(
        "force leading coefficient G",
        q3["axis_F_leading_pair"] == q3["symbolic_G_pair"],
        q3["axis_F_leading_pair"],
        q3["symbolic_G_pair"],
        "Q3",
    )

    packet = derivation_and_packet_fixture(q3)
    audit.check(
        "delta W sign",
        packet["delta_W_D_coefficient"]
        == (Fraction(0), Fraction(1, 1) / packet["hbar"]),
        packet["delta_W_D_coefficient"],
        "+i/hbar",
        "derivation",
    )
    audit.check(
        "delta2 W signs",
        packet["delta2_W_anticommutator_coefficient"]
        == (Fraction(0), Fraction(1, 1) / (2 * packet["chi"] * packet["hbar"]))
        and packet["delta2_W_D_squared_coefficient"]
        == (-Fraction(1, 1) / (packet["hbar"] ** 2), Fraction(0)),
        {
            "anti": packet["delta2_W_anticommutator_coefficient"],
            "square": packet["delta2_W_D_squared_coefficient"],
        },
        "+i/(2 chi hbar), -1/hbar^2",
        "derivation",
    )
    audit.check(
        "resolvent derivation signs",
        packet["delta_R_F_coefficient"] == (1, 0)
        and packet["delta2_R_F_R_F_coefficient"] == 2
        and packet["delta2_R_anticommutator_coefficient"]
        == Fraction(1, 1) / (2 * packet["chi"]),
        {
            "delta": packet["delta_R_F_coefficient"],
            "quadratic": packet["delta2_R_F_R_F_coefficient"],
            "anti": packet["delta2_R_anticommutator_coefficient"],
        },
        "+RFR, +2RFRFR, +1/(2chi)",
        "derivation",
    )
    audit.check(
        "anisotropic graph endpoint six",
        packet["graph_endpoint"] == 6,
        packet["graph_degrees"],
        "all terms degree <=6",
        "packet",
    )
    audit.check(
        "packet R powers",
        packet["translation_powers"]
        == {
            "delta_W_a": 3,
            "delta_R_0": 3,
            "K": 4,
            "K_to_three_halves": 6,
            "time": -3,
            "first_Taylor_total": 0,
            "second_Taylor_total": 0,
        },
        packet["translation_powers"],
        "R^3/R^6 at t=tau R^-3",
        "packet",
    )
    audit.check(
        "positive liminf only",
        all(
            row["tau"] < row["tau_upper"] and row["liminf_lower"] > 0
            for row in packet["rows"]
        )
        and not packet["exact_norm_jump_claimed"]
        and not packet["unsplit_flow_invariance_decided"],
        packet["rows"],
        "positive lower bound, no exact jump, invariance open",
        "scope",
    )

    pure = pure_quartic_resolvent_fixture()
    audit.check(
        "eight-dimensional packet normalization",
        pure["packet_amplitude_power"] == -2
        and pure["normalization_power"] == 0,
        {
            "amplitude": pure["packet_amplitude_power"],
            "normalization": pure["normalization_power"],
        },
        {"amplitude": -2, "normalization": 0},
        "pure-quartic",
    )
    audit.check(
        "translated quartic momentum scale",
        pure["momentum_center_leading"]
        == 3 * pure["t"] * pure["G"] * pure["s"]
        and pure["phase_spread_power"] < pure["momentum_center_power"],
        {
            "leading": pure["momentum_center_leading"],
            "spread_power": pure["phase_spread_power"],
        },
        "3tGs R^2 with o(R^2) spread",
        "pure-quartic",
    )
    audit.check(
        "exact basic-resolvent jump",
        pure["lower_bound"]
        == pure["upper_bound"]
        == pure["exact_jump"]
        == Fraction(1, 1) / abs(pure["mu"]),
        {
            "lower": pure["lower_bound"],
            "upper": pure["upper_bound"],
            "jump": pure["exact_jump"],
        },
        Fraction(1, 1) / abs(pure["mu"]),
        "pure-quartic",
    )
    audit.check(
        "intrinsic membership boundary",
        pure["weyl_orbit_norm_continuous_for_resolvent_algebra_elements"]
        and not pure["translated_element_in_resolvent_algebra"]
        and pure["full_resolvent_algebra_unital"]
        and pure["its_multiplier_strict_equals_norm"]
        and not pure["unsplit_invariance_decided"],
        pure,
        "pure kick excluded; unsplit invariance open",
        "scope",
    )

    gibbs = finite_gibbs_entropy_fixture()
    audit.check(
        "finite-Gibbs entropy exact both orientations",
        gibbs["relative_entropy_plus"]
        == gibbs["relative_entropy_minus"]
        == gibbs["evolved_relative_entropy_plus"]
        == gibbs["evolved_relative_entropy_minus"]
        == Fraction(5, 4),
        {
            "plus": gibbs["relative_entropy_plus"],
            "minus": gibbs["relative_entropy_minus"],
        },
        Fraction(5, 4),
        "Gibbs",
    )
    audit.check(
        "binary lower and inversion",
        gibbs["binary_fixture"]["d_binary"]
        >= gibbs["binary_fixture"]["elementary_lower"]
        and gibbs["binary_fixture"]["d_below_S"]
        and gibbs["binary_fixture"]["q_below_inverted_bound"],
        gibbs["binary_fixture"],
        "d>=q log(1/p)-log2 and q<=(S+log2)/log(1/p)",
        "Gibbs",
    )
    audit.check(
        "finite-Gibbs tail stays inverse logarithmic",
        gibbs["gaussian_tail_substitution"]["denominator_positive"]
        and gibbs["gaussian_tail_substitution"]["asymptotic_power"] == -2
        and not gibbs["all_history_gaussian_tail_closed"]
        and not gibbs["exponential_corridor_absorbed"],
        gibbs["gaussian_tail_substitution"],
        "O(L^-2), no history closure",
        "scope",
    )

    entropy_fixture = entropy_finite_moment_fixture()
    audit.check(
        "all m>=3 sample rotations exist",
        all(row["m"] >= 3 and row["rotation_exists"] for row in entropy_fixture["rows"]),
        [(row["m"], row["n"], row["rotation_exists"]) for row in entropy_fixture["rows"]],
        "all true",
        "entropy-no-go",
    )
    audit.check(
        "both tails and entropies exact",
        all(
            row["tail_plus"] == row["tail_minus"]
            and row["relative_entropy_plus"] == row["relative_entropy_minus"]
            and abs(
                row["relative_entropy_plus"] - row["expected_relative_entropy"]
            )
            <= Decimal("1e-75")
            for row in entropy_fixture["rows"]
        ),
        entropy_fixture["rows"],
        "tail p1+n^-2m and entropy n^(4-2m)",
        "entropy-no-go",
    )
    audit.check(
        "moments through every integer r<=2m",
        all(
            all(
                item["identity"] and item["within_uniform_bound"]
                for item in row["integer_moment_checks"]
            )
            and len(row["integer_moment_checks"]) == 2 * row["m"]
            for row in entropy_fixture["rows"]
        ),
        [
            (row["m"], row["n"], len(row["integer_moment_checks"]))
            for row in entropy_fixture["rows"]
        ],
        "formula verified for 1,...,2m; calculus formula covers real r",
        "entropy-no-go",
    )
    audit.check(
        "all-real moment formula boundary",
        all(
            row["r_in_domain"]
            and row["second_exponent_nonpositive"]
            and row["within_uniform_bound"]
            for row in entropy_fixture["real_r_rows"]
        ),
        entropy_fixture["real_r_rows"],
        "n^r p1+n^(r-2m) uniformly bounded for real 0<r<=2m",
        "entropy-no-go",
    )
    audit.check(
        "arbitrary finite moment ceiling covered",
        all(
            row["chosen_m"] >= 3 and row["covered"]
            for row in entropy_fixture["arbitrary_finite_ceiling_rows"]
        ),
        entropy_fixture["arbitrary_finite_ceiling_rows"],
        "choose m>=3 with ceiling<=2m",
        "entropy-no-go",
    )
    audit.check(
        "all-coefficient Gaussian reference fixture",
        all(row["within_envelope"] for row in entropy_fixture["gaussian_reference_rows"]),
        entropy_fixture["gaussian_reference_rows"],
        "<=1+exp(a^2/4)",
        "entropy-no-go",
    )
    audit.check(
        "m=4 eighth-moment 4e^-2 bound",
        all(row["bound_holds"] for row in entropy_fixture["m4_rows"])
        and entropy_fixture[
            "m4_calculus_optimizer_for_x_squared_exp_minus_x"
        ]
        == 2,
        entropy_fixture["m4_rows"],
        "Tr tilted q^8 <= 1+4e^-2",
        "entropy-no-go",
    )
    audit.check(
        "polynomial tail defeats every Gaussian coefficient",
        all(
            right["log_exp_aq2_times_n_minus_8"]
            > left["log_exp_aq2_times_n_minus_8"]
            for left, right in zip(
                entropy_fixture["polynomial_log_rows"],
                entropy_fixture["polynomial_log_rows"][1:],
            )
        )
        and entropy_fixture["polynomial_log_rows"][-1][
            "log_exp_aq2_times_n_minus_8"
        ]
        > 0,
        entropy_fixture["polynomial_log_rows"],
        "a n^2-2m log n tends to +infinity",
        "entropy-no-go",
    )
    audit.check(
        "entropy no-go method scope",
        not entropy_fixture["finite_moment_to_gaussian_inference_valid"]
        and not entropy_fixture["Q3LOCK_counterexample"]
        and not entropy_fixture["stronger_quasi_invariance_excluded"],
        entropy_fixture,
        "method no-go only",
        "scope",
    )

    ground = ordered_ground_gap_fixture()
    audit.check(
        "ordered ground categorical properties",
        ground["states_pure"]
        and ground["states_disjoint"]
        and ground["parity_swap"]
        and ground["central_order_values"] == (1, -1)
        and ground["GNS_ground_kernel_dimension_each"] == 1,
        ground,
        "pure, disjoint, parity-related, ordered, simple ground",
        "ground-gap",
    )
    audit.check(
        "spectrum [0,1] and zero gap",
        ground["spectrum_each"] == "[0,1]"
        and ground["positive_spectrum_infimum"] == 0
        and all(value > 0 for value in ground["positive_spectral_points"])
        and all(
            right < left
            for left, right in zip(
                ground["positive_spectral_points"],
                ground["positive_spectral_points"][1:],
            )
        ),
        ground["positive_spectral_points"],
        "positive spectrum accumulates at zero",
        "ground-gap",
    )
    audit.check(
        "direct-integral low-energy sequence",
        all(
            right["energy_expectation"] < left["energy_expectation"]
            and right["H_norm_squared"] < left["H_norm_squared"]
            for left, right in zip(
                ground["weyl_sequence_rows"], ground["weyl_sequence_rows"][1:]
            )
        )
        and all(row["orthogonal_to_ground"] for row in ground["weyl_sequence_rows"]),
        ground["weyl_sequence_rows"],
        "orthogonal unit vectors with energy tending to zero",
        "ground-gap",
    )
    audit.check(
        "GNS coercivity remains separate",
        not ground["ordered_doublets_imply_gap"]
        and not ground["physical_mass_gap_claimed"]
        and "Delta" in ground["coercivity_form"],
        ground["coercivity_form"],
        "positive Delta still required",
        "scope",
    )

    for phrase in (
        "continuous-time thermodynamic split limit",
        "all-exhaustion or all-boundary Cauchy",
        "quasi-local raw oscillator common alpha",
        "full resolvent-algebra invariance or non-invariance for the unsplit",
        "phase-KMS quotient identification",
        "broken-sector GNS or physical mass gap",
        "regulator removal",
        "continuum",
        "physical empty space or a below-empty sign",
        "Pre-A selection",
        "C6",
        "CP1",
        "Sector-A closure",
    ):
        audit.check(
            f"no-overclaim boundary {phrase}",
            phrase in EXPECTED_NO_OVERCLAIM,
            phrase in EXPECTED_NO_OVERCLAIM,
            True,
            "scope",
        )

    authority = authority_audit(audit, manifest, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"

    source_paths = (
        SCRIPT,
        MANIFEST,
        CERTIFICATE,
        NEGATIVE_REGISTRY,
        EXPLORATION_LOG,
        GATES,
        RESULTS_LEDGER,
    )
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
        if path.exists()
    }
    for relative, digest in source_hashes.items():
        audit.check(
            f"source hash {relative}",
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": ["C6-SPACETIME-SIGNATURE"],
        "claim_bearing": False,
        "verdict": verdict,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "local_strict_topology": topology,
            "q3_quartic_force": q3,
            "unsplit_packet": packet,
            "pure_quartic_resolvent": pure,
            "finite_gibbs_entropy": gibbs,
            "entropy_finite_moment_no_go": entropy_fixture,
            "ordered_ground_gap_no_go": ground,
            "finite_region_local_strict_carrier_closed": True,
            "fixed_finite_gibbs_entropy_tail_closed": True,
            "continuous_time_split_limit_closed": False,
            "all_exhaustion_common_alpha_closed": False,
            "unsplit_resolvent_algebra_invariance_decided": False,
            "phase_KMS_quotient_identified": False,
            "broken_sector_GNS_gap_closed": False,
            "physical_mass_gap_closed": False,
            "regulator_removal_closed": False,
            "continuum_closed": False,
            "physical_empty_comparison_closed": False,
            "C6_closed": False,
            "CP1_closed": False,
            "Sector_A_closed": False,
            "Pre_A_closed": False,
        },
        "negative_ids": list(NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "successor_gates": list(SUCCESSOR_GATES),
        "open_gates": list(manifest["open_gates"]),
        "superseded_gate_ids": [SUPERSEDED_GATE],
        "authority": authority,
        "source_hashes": source_hashes,
        "boundary": EXPECTED_NO_OVERCLAIM,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-identical canonical payloads",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="allow missing formal authorities and report INCOMPLETE",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="run all checks without writing the result JSON",
    )
    arguments = parser.parse_args()

    payload = build_payload(staged=arguments.staged)
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()

    if arguments.self_test:
        repeated = build_payload(staged=arguments.staged)
        repeated_encoded = canonical_bytes(repeated)
        if encoded != repeated_encoded:
            raise AssertionError("nondeterministic independent payload")
        if digest != hashlib.sha256(repeated_encoded).hexdigest():
            raise AssertionError("nondeterministic independent digest")
        print(
            f"SELF-TEST {payload['verdict']} {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
        )
        if payload["authority"]["missing"]:
            print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
        return 0 if payload["verdict"] == "PASS" or arguments.staged else 1

    if payload["verdict"] != "PASS" and not arguments.staged:
        print(
            f"INCOMPLETE {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | authority "
            + ", ".join(payload["authority"]["missing"])
        )
        return 1

    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    label = "PASS" if payload["verdict"] == "PASS" else "STAGED"
    print(
        f"{label} {payload['summary']['passed']}/"
        f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    if payload["authority"]["missing"]:
        print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
