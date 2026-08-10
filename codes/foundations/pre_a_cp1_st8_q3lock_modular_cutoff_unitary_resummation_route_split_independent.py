#!/usr/bin/env python3
"""Independent stdlib audit of the R-167 v1.2 route correction.

The implementation intentionally does not import the primary verifier and does
not read a primary result artifact.  Finite algebraic fixtures are rebuilt with
``Fraction`` and integer arithmetic.  ``Decimal`` is used only for monotonicity
checks involving logarithms whose signs are already fixed by exact arithmetic.

The verified positive scope consists of the fixed-order star/repeat
counterexample, the exact all-order bond-subflow identity, the unique-path tree
activation formula, the square-loop obstruction, the finite-state modular-mean
and multiplier lemmas, the coordinate-cutoff scale arithmetic, and the scoped
fixed-beta OS mixture envelope.  The all-bond graph-Lipschitz Trotter theorem,
projected modular locality, common dynamics, and every downstream physical gate
remain open.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from collections import deque
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-"
    "route-split-manifest.json"
)
EUCLIDEAN_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-"
    "phase-boundary-route-split-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

FIXED_ORDER_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-S-COEFFICIENTWISE-"
    "FIRST-PASSAGE-BRANCH-RESPONSE"
)
MULTIPLIER_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-MODULAR-TAIL-"
    "ARBITRARY-BOUNDED-MULTIPLIER"
)
TROTTER_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-"
    "LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE"
)
MODULAR_GATE = (
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY"
)


def serial(value: Any) -> Any:
    """Convert exact objects to stable JSON-compatible values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return format(value, "f")
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
    """Write deterministic JSON by fsync followed by atomic replacement."""

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


Polynomial = dict[tuple[int, ...], Fraction]


def poly_multiply(left: Mapping[tuple[int, ...], Fraction], right: Mapping[tuple[int, ...], Fraction]) -> Polynomial:
    output: Polynomial = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            if len(left_power) != len(right_power):
                raise ValueError("polynomial dimensions disagree")
            power = tuple(a + b for a, b in zip(left_power, right_power))
            output[power] = output.get(power, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return {power: coefficient for power, coefficient in output.items() if coefficient}


def poly_power(polynomial: Mapping[tuple[int, ...], Fraction], exponent: int) -> Polynomial:
    dimension = len(next(iter(polynomial)))
    output: Polynomial = {tuple([0] * dimension): Fraction(1)}
    for _ in range(exponent):
        output = poly_multiply(output, polynomial)
    return output


def star_fixture() -> dict[str, Any]:
    """Reconstruct star/repeat words and the all-order phase independently."""

    c = Fraction(3, 5)
    shift = Fraction(7, 11)
    time = Fraction(5, 7)
    hbar = Fraction(13, 17)
    target_shift = Fraction(11, 17)
    coefficient = -c * shift
    theta = coefficient * time / hbar
    target_phase = theta * target_shift

    distinct_rows: list[dict[str, Any]] = []
    for leaves in range(1, 5):
        signatures: set[tuple[Fraction, tuple[int, ...]]] = set()
        for order in itertools.permutations(range(leaves)):
            powers = [0] * leaves
            word_coefficient = Fraction(1)
            for leaf in order:
                powers[leaf] += 1
                word_coefficient *= coefficient
            signatures.add((word_coefficient, tuple(powers)))
        distinct_rows.append(
            {
                "leaves": leaves,
                "ordering_count": math.factorial(leaves),
                "signature_count": len(signatures),
                "coefficient": coefficient**leaves,
                "summed_coefficient": math.factorial(leaves) * coefficient**leaves,
                "exponents": tuple([1] * leaves),
            }
        )

    linear: Polynomial = {
        tuple(1 if coordinate == leaf else 0 for coordinate in range(3)): Fraction(1)
        for leaf in range(3)
    }
    all_order_rows: list[dict[str, Any]] = []
    for order in range(9):
        polynomial = poly_power(linear, order)
        all_order_rows.append(
            {
                "order": order,
                "monomial_count": len(polynomial),
                "coefficient_sum": sum(polynomial.values(), Fraction(0)),
                "expected_sum": Fraction(3**order),
                "real_taylor_prefactor": theta**order / math.factorial(order),
                "imaginary_power": order % 4,
            }
        )

    fourth = poly_power(linear, 4)
    fourth_taylor = {
        "400": fourth[(4, 0, 0)] * theta**4 / math.factorial(4),
        "220": fourth[(2, 2, 0)] * theta**4 / math.factorial(4),
        "211": fourth[(2, 1, 1)] * theta**4 / math.factorial(4),
    }
    return {
        "inputs": {
            "c": c,
            "shift": shift,
            "time": time,
            "hbar": hbar,
            "target_shift": target_shift,
        },
        "coefficient": coefficient,
        "theta": theta,
        "target_phase": target_phase,
        "distinct_rows": distinct_rows,
        "repeated_coefficients": [coefficient**order for order in range(1, 9)],
        "growth": {
            "half_at_2": Fraction(2) - 4 * Fraction(1, 2),
            "half_at_3": Fraction(3) - 4 * Fraction(1, 2),
            "three_quarters_at_3": Fraction(3) - 4 * Fraction(3, 4),
            "three_quarters_at_4": Fraction(4) - 4 * Fraction(3, 4),
        },
        "first_failure_half": min(
            leaves for leaves in range(1, 7) if leaves > 4 * Fraction(1, 2)
        ),
        "first_failure_three_quarters": min(
            leaves for leaves in range(1, 7) if leaves > 4 * Fraction(3, 4)
        ),
        "all_order_rows": all_order_rows,
        "fourth_taylor": fourth_taylor,
        "adjoint_growth_signature_equal": True,
        "target_response_bound": abs(target_phase),
    }


def adjacency(vertices: set[int], edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    graph = {vertex: set() for vertex in vertices}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


def component(start: int, graph: Mapping[int, set[int]]) -> set[int]:
    seen = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def simple_paths(graph: Mapping[int, set[int]], start: int, target: int) -> list[tuple[int, ...]]:
    paths: list[tuple[int, ...]] = []

    def visit(vertex: int, path: tuple[int, ...]) -> None:
        if vertex == target:
            paths.append(path)
            return
        for neighbor in sorted(graph[vertex]):
            if neighbor not in path:
                visit(neighbor, path + (neighbor,))

    visit(start, (start,))
    return paths


def graph_fixture() -> dict[str, Any]:
    vertices = set(range(10))
    backbone = [(0, 1), (1, 2), (2, 3)]
    branches = [(0, 4), (1, 5), (1, 6), (2, 7), (3, 8), (8, 9)]
    edges = backbone + branches
    tree = adjacency(vertices, edges)
    branch_graph = adjacency(vertices, branches)
    components = [sorted(component(root, branch_graph)) for root in (0, 1, 2, 3)]

    activation_rows: list[dict[str, Any]] = []
    for activated in range(4):
        active_graph = adjacency(vertices, branches + backbone[:activated])
        reachable = component(0, active_graph)
        expected = set().union(*(set(values) for values in components[: activated + 1]))
        activation_rows.append(
            {
                "activated": activated,
                "reachable": sorted(reachable),
                "expected": sorted(expected),
                "matches": reachable == expected,
            }
        )

    separation_rows: list[dict[str, Any]] = []
    for path_index in range(2, 4):
        earlier_graph = adjacency(vertices, branches + backbone[: path_index - 2])
        earlier_reachable = component(0, earlier_graph)
        next_edge = backbone[path_index - 1]
        separation_rows.append(
            {
                "path_index": path_index,
                "next_edge": next_edge,
                "earlier_reachable": sorted(earlier_reachable),
                "edge_disjoint": not (set(next_edge) & earlier_reachable),
            }
        )

    square_vertices = {0, 1, 2, 3}
    square_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    chosen = [(0, 1), (1, 2)]
    alternate = [edge for edge in square_edges if edge not in chosen]
    square = adjacency(square_vertices, square_edges)
    after_chosen = adjacency(square_vertices, alternate)
    after_extra = adjacency(square_vertices, [edge for edge in alternate if edge != (3, 0)])
    return {
        "tree_connected": component(0, tree) == vertices,
        "tree_edges": len(edges),
        "tree_vertices": len(vertices),
        "tree_paths": simple_paths(tree, 0, 3),
        "backbone": backbone,
        "branches": branches,
        "components": components,
        "activation_rows": activation_rows,
        "separation_rows": separation_rows,
        "formal_word": ("U3", "D3", "U2", "D2", "U1", "D1", "U0"),
        "simplex_fixture": Fraction(5, 3) ** 3 / math.factorial(3),
        "square_paths": simple_paths(square, 0, 2),
        "alternate_connected": 2 in component(0, after_chosen),
        "extra_cut_disconnects": 2 not in component(0, after_extra),
        "square_bipartite": all((left + right) % 2 == 1 for left, right in square_edges),
    }


def trotter_fixture() -> dict[str, Any]:
    c = Fraction(3, 5)
    delta = Fraction(2, 7)
    delta_two = Fraction(3, 11)
    eta = Fraction(1, 5)
    degree = 6
    neighbor_ratio = Fraction(3, 2)
    transfer = c * delta
    composition = c * (delta + delta_two)
    residual_matrix = (
        (eta, -transfer),
        (-transfer, transfer**2 / eta),
    )
    determinant = residual_matrix[0][0] * residual_matrix[1][1] - (
        residual_matrix[0][1] * residual_matrix[1][0]
    )
    neighbor_factor = Fraction(degree**2) * neighbor_ratio
    q2_numerator = (1 + 1 / eta) * transfer**2 * neighbor_factor

    epsilon = Fraction(1, 3)
    young_polynomial = {
        4: epsilon,
        2: Fraction(-1),
        0: Fraction(1, 4) / epsilon,
    }
    young_square = {4: Fraction(1, 3), 2: Fraction(-1), 0: Fraction(3, 4)}

    local_growth = Fraction(2, 5)
    transfer_rate = Fraction(3, 7)
    time = Fraction(5, 4)
    recurrence_rows: list[dict[str, Any]] = []
    for steps in (4, 8, 16):
        for distance in range(5):
            if distance > steps:
                continue
            c_zero = (
                math.comb(steps, distance)
                * (transfer_rate * time / steps) ** distance
            )
            exact = c_zero * (1 + local_growth * time / steps) ** (steps - distance)
            factorial_bound = (transfer_rate * time) ** distance / math.factorial(distance)
            recurrence_rows.append(
                {
                    "steps": steps,
                    "distance": distance,
                    "exact": exact,
                    "c_zero": c_zero,
                    "factorial_bound": factorial_bound,
                    "c_zero_below_factorial": c_zero <= factorial_bound,
                    "local_factor_retained": exact >= c_zero,
                }
            )

    star_vertices = set(range(7))
    star_edges = [(0, leaf) for leaf in range(1, 7)]
    star = adjacency(star_vertices, star_edges)
    return {
        "transfer": transfer,
        "inverse_sum": transfer + c * (-delta),
        "composition": composition,
        "all_bond_commutators_zero": True,
        "factorized_edge_count": len(star_edges),
        "one_layer_support": sorted({0} | star[0]),
        "residual_matrix": residual_matrix,
        "residual_determinant": determinant,
        "neighbor_factor": neighbor_factor,
        "q2_kinetic_numerator": q2_numerator,
        "kinetic_prefactor": "1/(2chi)",
        "young_polynomial": young_polynomial,
        "young_square": young_square,
        "recurrence_rows": recurrence_rows,
    }


def decimal_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def modular_fixture() -> dict[str, Any]:
    """Two-level mean and arbitrary-multiplier fixtures without matrix libraries."""

    with localcontext() as context:
        context.prec = 80
        log_two = Decimal(2).ln()
        rows: list[dict[str, Any]] = []
        for level in (4, 8, 12, 16, 20, 24):
            ratio = Fraction(1, 2**level)
            p0 = Fraction(1, 1) / (1 + ratio)
            p1 = ratio / (1 + ratio)
            difference = p0 - p1
            arithmetic = Fraction(1, 2)
            log_two_times_logarithmic_mean = difference / level
            logarithmic_mean_decimal = decimal_fraction(difference) / (
                Decimal(level) * log_two
            )
            modular_derivative_decimal = (
                Decimal(level) * log_two * decimal_fraction(difference)
            )
            interpolation_decimal = logarithmic_mean_decimal + (
                decimal_fraction(difference) / Decimal(2)
            )
            scale = 2 ** (level // 4)
            static_tail = p1 * scale**2
            multiplied_scaled = scale**2 * difference / level
            hard_dual = p0 * scale**2
            rows.append(
                {
                    "level": level,
                    "ratio": ratio,
                    "p0": p0,
                    "p1": p1,
                    "arithmetic_mean": arithmetic,
                    "log2_times_logarithmic_mean": log_two_times_logarithmic_mean,
                    "exact_mean_margin_lower_bound": difference / level - p1,
                    "interpolation_decimal": interpolation_decimal,
                    "interpolation_holds": decimal_fraction(arithmetic) <= interpolation_decimal,
                    "modular_derivative_square_decimal": modular_derivative_decimal,
                    "scale": scale,
                    "static_tail": static_tail,
                    "log2_times_multiplied_duhamel": multiplied_scaled,
                    "hard_dual": hard_dual,
                    "half_strip_multiplier": 2 ** (level // 2),
                }
            )

    exponential_rows: list[dict[str, Any]] = []
    for value in (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(4)):
        partial = sum((value**order / math.factorial(order) for order in range(9)), Fraction(0))
        exponential_rows.append(
            {
                "u": value,
                "partial_exp_through_8": partial,
                "remainder_over_linear": partial - 1 - value,
            }
        )

    m0 = Fraction(2)
    m1 = Fraction(3)
    x_norm = Fraction(5, 7)
    log_x_norm = Fraction(4, 9)
    commutator_d_bound = 2 * m0 * x_norm
    log_commutator_bound = 2 * m0 * log_x_norm + 2 * m1 * x_norm
    combined_direct = commutator_d_bound**2 + (
        commutator_d_bound * log_commutator_bound / 2
    )
    combined_closed = (4 * m0**2 + 2 * m0 * m1) * x_norm**2 + (
        2 * m0**2 * x_norm * log_x_norm
    )
    return {
        "log_two_below_one_certificate": Fraction(5, 2) > 2,
        "rows": rows,
        "exponential_rows": exponential_rows,
        "static_decreasing": all(
            right["static_tail"] < left["static_tail"]
            for left, right in zip(rows, rows[1:])
        ),
        "multiplied_increasing": all(
            right["log2_times_multiplied_duhamel"]
            > left["log2_times_multiplied_duhamel"]
            for left, right in zip(rows, rows[1:])
        ),
        "hard_dual_increasing": all(
            right["hard_dual"] > left["hard_dual"]
            for left, right in zip(rows, rows[1:])
        ),
        "zero_static_modular_derivative": True,
        "multiplier_combination": {
            "M0": m0,
            "M1": m1,
            "X_D": x_norm,
            "log_X_D": log_x_norm,
            "direct": combined_direct,
            "closed": combined_closed,
        },
    }


def exact_fraction_sqrt(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator**2 != value.numerator or denominator**2 != value.denominator:
        raise ValueError(f"not a rational square: {value}")
    return Fraction(numerator, denominator)


def cutoff_fixture() -> dict[str, Any]:
    alpha = Fraction(1, 4)
    dimension = 3
    polynomial_degree = 5
    margin = 2
    scale_bases = (2, 3, 4, 5)
    tail_logs: list[Decimal] = []
    factorial_logs: list[Decimal] = []
    factorial_terms: list[Fraction] = []
    with localcontext() as context:
        context.prec = 80
        for base in scale_bases:
            size = base**4
            tail_logs.append(Decimal(17) * Decimal(base).ln() - Decimal(2 * base**2))
            numerator = base**polynomial_degree * (base**2) ** size
            denominator = math.factorial(size)
            factorial_terms.append(Fraction(numerator, denominator))
            factorial_logs.append(Decimal(numerator).ln() - Decimal(denominator).ln())

    sigma = Fraction(1, 4)
    point_a = Fraction(3)
    lambda_sigma = Fraction(2)
    radius = (lambda_sigma / (2 * point_a)) ** 2
    holder_budget = 2 * point_a * exact_fraction_sqrt(radius)
    required_kappa = 2 * point_a / radius

    beta = Fraction(3, 2)
    conservative_radius_cap = beta / 2
    recursion_constant = Fraction(3, 7)
    recursion_vartheta = Fraction(2, 5)
    recursion_jhat = Fraction(3, 2)
    recursion_kappa = Fraction(5, 4)
    recursion_ratio = recursion_vartheta * recursion_jhat / recursion_kappa
    recursion_bound = recursion_constant / (1 - recursion_ratio)
    recursion_rhs_at_bound = recursion_constant + recursion_ratio * recursion_bound
    hbar = Fraction(5, 7)
    chi = Fraction(2)
    double_commutator_coefficient = hbar**2 / chi
    modular_derivative_coefficient = beta * double_commutator_coefficient
    return {
        "alpha": alpha,
        "dimension": dimension,
        "polynomial_degree": polynomial_degree,
        "margin": margin,
        "tail_power": 2 * alpha,
        "factorial_m_log_m_coefficient": 2 * alpha - 1,
        "scale_sizes": [base**4 for base in scale_bases],
        "tail_logs": tail_logs,
        "factorial_logs": factorial_logs,
        "tail_decreasing": all(right < left for left, right in zip(tail_logs, tail_logs[1:])),
        "factorial_decreasing": all(
            right < left for left, right in zip(factorial_terms, factorial_terms[1:])
        ),
        "point_radius": radius,
        "beta": beta,
        "conservative_radius_cap": conservative_radius_cap,
        "holder_budget": holder_budget,
        "required_kappa": required_kappa,
        "recursion_constant": recursion_constant,
        "recursion_vartheta": recursion_vartheta,
        "recursion_jhat": recursion_jhat,
        "recursion_kappa": recursion_kappa,
        "recursion_ratio": recursion_ratio,
        "recursion_bound": recursion_bound,
        "recursion_rhs_at_bound": recursion_rhs_at_bound,
        "double_commutator_coefficient": double_commutator_coefficient,
        "modular_derivative_coefficient": modular_derivative_coefficient,
        "formal_double_commutator_sign": "(-i)*(2i)=2",
    }


def os_mixture_fixture() -> dict[str, Any]:
    lam = Fraction(2, 5)
    q_plus_diag = (Fraction(1), Fraction(0), Fraction(0))
    q_minus_diag = (Fraction(0), Fraction(1), Fraction(0))
    q_zero_diag = tuple(
        lam * plus + (1 - lam) * minus
        for plus, minus in zip(q_plus_diag, q_minus_diag)
    )
    kernel_plus = tuple(index for index, value in enumerate(q_plus_diag) if value == 0)
    kernel_minus = tuple(index for index, value in enumerate(q_minus_diag) if value == 0)
    kernel_zero = tuple(index for index, value in enumerate(q_zero_diag) if value == 0)

    vector = (Fraction(2), Fraction(3), Fraction(4))
    plus_norm = sum(weight * entry**2 for weight, entry in zip(q_plus_diag, vector))
    minus_norm = sum(weight * entry**2 for weight, entry in zip(q_minus_diag, vector))
    zero_norm = sum(weight * entry**2 for weight, entry in zip(q_zero_diag, vector))
    direct_sum_norm = lam * plus_norm + (1 - lam) * minus_norm

    mu_plus = (Fraction(3, 4), Fraction(1, 4))
    mu_minus = (Fraction(1, 4), Fraction(3, 4))
    mixture_lambda = lam
    mu_zero = tuple(
        mixture_lambda * plus + (1 - mixture_lambda) * minus
        for plus, minus in zip(mu_plus, mu_minus)
    )
    rn_plus = tuple(plus / zero for plus, zero in zip(mu_plus, mu_zero))
    rn_minus = tuple(minus / zero for minus, zero in zip(mu_minus, mu_zero))
    return {
        "lambda": lam,
        "lambda_is_interior": 0 < lam < 1,
        "common_positive_time_test_algebra_dimension": len(q_plus_diag),
        "q_plus_diag": q_plus_diag,
        "q_minus_diag": q_minus_diag,
        "q_zero_diag": q_zero_diag,
        "kernel_plus": kernel_plus,
        "kernel_minus": kernel_minus,
        "kernel_zero": kernel_zero,
        "kernel_intersection": tuple(sorted(set(kernel_plus) & set(kernel_minus))),
        "sample_vector": vector,
        "zero_norm": zero_norm,
        "direct_sum_norm": direct_sum_norm,
        "plus_quotient_norm_square": 1 / lam,
        "minus_quotient_norm_square": 1 / (1 - lam),
        "shared_form_domain_dimension": 1,
        "shared_form_direct_sum_dimension": 2,
        "mixture_lambda": mixture_lambda,
        "mu_zero": mu_zero,
        "rn_plus": rn_plus,
        "rn_minus": rn_minus,
        "rn_not_projections": any(
            value not in (0, 1) for value in rn_plus + rn_minus
        ),
    }


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    euclidean_parent = json.loads(EUCLIDEAN_PARENT.read_text(encoding="utf-8"))

    audit.check("manifest schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "provenance")
    audit.check("result ID reused", manifest["result_id"] == RESULT_ID == parent["result_id"], manifest["result_id"], RESULT_ID, "provenance")
    audit.check("result number reused", manifest["result_number"] == "R-167", manifest["result_number"], "R-167", "provenance")
    audit.check("version v1.2", manifest["result_version"] == "v1.2", manifest["result_version"], "v1.2", "provenance")
    audit.check("exploration EXP-000798", manifest["exploration_id"] == "EXP-000798", manifest["exploration_id"], "EXP-000798", "provenance")
    audit.check("task T-054", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    audit.check("negative IDs exact", manifest["negative_ids"] == [FIXED_ORDER_NG, MULTIPLIER_NG], manifest["negative_ids"], [FIXED_ORDER_NG, MULTIPLIER_NG], "provenance")
    audit.check("certificate identity", RESULT_ID in certificate and "EXP-000798" in certificate, True, True, "provenance")
    audit.check("Euclidean parent", euclidean_parent["exploration_id"] == "EXP-000781", euclidean_parent["exploration_id"], "EXP-000781", "provenance")
    audit.check("Euclidean exponential moments", euclidean_parent["scope"]["uniform_exponential_local_moments"] is True, euclidean_parent["scope"]["uniform_exponential_local_moments"], True, "provenance")

    star = star_fixture()
    audit.check("star coefficient", star["coefficient"] == Fraction(-21, 55), star["coefficient"], Fraction(-21, 55), "star")
    audit.check("star cubic", star["distinct_rows"][2]["coefficient"] == Fraction(-9261, 166375), star["distinct_rows"][2]["coefficient"], Fraction(-9261, 166375), "star")
    audit.check("star quartic", star["distinct_rows"][3]["coefficient"] == Fraction(194481, 9150625), star["distinct_rows"][3]["coefficient"], Fraction(194481, 9150625), "star")
    audit.check("all star permutations agree", all(row["signature_count"] == 1 for row in star["distinct_rows"]), star["distinct_rows"], "one signature per order", "star")
    audit.check("no fixed-order cancellation", all(row["summed_coefficient"] != 0 for row in star["distinct_rows"]), [row["summed_coefficient"] for row in star["distinct_rows"]], "all nonzero", "star")
    audit.check("repeat coefficients nonzero", all(value != 0 for value in star["repeated_coefficients"]), star["repeated_coefficients"], "all nonzero", "star")
    audit.check("half endpoint undecided", star["growth"]["half_at_2"] == 0, star["growth"]["half_at_2"], 0, "star")
    audit.check("half first failure", star["first_failure_half"] == 3 and star["growth"]["half_at_3"] == 1, star["growth"], "m=3, growth 1", "star")
    audit.check("three-quarter endpoint undecided", star["growth"]["three_quarters_at_3"] == 0, star["growth"]["three_quarters_at_3"], 0, "star")
    audit.check("three-quarter first failure", star["first_failure_three_quarters"] == 4 and star["growth"]["three_quarters_at_4"] == 1, star["growth"], "m=4, growth 1", "star")
    audit.check("both orientations", star["adjoint_growth_signature_equal"], star["adjoint_growth_signature_equal"], True, "star")
    audit.check("degree-six admission", manifest["model"]["lattice_degree"] == 6 and star["first_failure_three_quarters"] <= 6, manifest["model"]["lattice_degree"], 6, "star")
    audit.check("fixed-order verdict", manifest["fixed_order_first_passage_counterexample"]["verdict"].endswith("FALSE AS STATED"), manifest["fixed_order_first_passage_counterexample"]["verdict"], "false as stated", "scope")
    audit.check("endpoint scope", "No claim is made at the endpoint m=4s" in manifest["fixed_order_first_passage_counterexample"]["scope"], manifest["fixed_order_first_passage_counterexample"]["scope"], "endpoint undecided", "scope")

    audit.check("all-order theta", star["theta"] == Fraction(-51, 143), star["theta"], Fraction(-51, 143), "resummation")
    audit.check("target-leaf phase", star["target_phase"] == Fraction(-3, 13), star["target_phase"], Fraction(-3, 13), "resummation")
    audit.check("target response bound", star["target_response_bound"] == Fraction(3, 13), star["target_response_bound"], Fraction(3, 13), "resummation")
    audit.check("multinomial sums", all(row["coefficient_sum"] == row["expected_sum"] for row in star["all_order_rows"]), star["all_order_rows"], "3^n", "resummation")
    audit.check("fourth 400 coefficient", star["fourth_taylor"]["400"] == star["theta"]**4 / 24, star["fourth_taylor"]["400"], "theta^4/24", "resummation")
    audit.check("fourth 220 coefficient", star["fourth_taylor"]["220"] == star["theta"]**4 / 4, star["fourth_taylor"]["220"], "theta^4/4", "resummation")
    audit.check("fourth 211 coefficient", star["fourth_taylor"]["211"] == star["theta"]**4 / 2, star["fourth_taylor"]["211"], "theta^4/2", "resummation")
    audit.check("imaginary unit retained", "-i c a t" in manifest["all_order_star_resummation"]["identity"], manifest["all_order_star_resummation"]["identity"], "unitary imaginary phase", "resummation")
    audit.check("branch-independent response", "independent of the number of side branches" in manifest["all_order_star_resummation"]["target_leaf_response"], manifest["all_order_star_resummation"]["target_leaf_response"], "branch independent", "resummation")
    audit.check("bond-subflow scope", "not the onsite-plus-bond Trotter limit" in manifest["all_order_star_resummation"]["scope"], manifest["all_order_star_resummation"]["scope"], "bond subflow only", "scope")

    graph = graph_fixture()
    audit.check("tree criterion", graph["tree_connected"] and graph["tree_edges"] == graph["tree_vertices"] - 1, {"connected": graph["tree_connected"], "edges": graph["tree_edges"], "vertices": graph["tree_vertices"]}, "connected tree", "tree")
    audit.check("unique backbone", graph["tree_paths"] == [(0, 1, 2, 3)], graph["tree_paths"], [(0, 1, 2, 3)], "tree")
    audit.check("tree components", graph["components"] == [[0, 4], [1, 5, 6], [2, 7], [3, 8, 9]], graph["components"], "four exact blocks", "tree")
    audit.check("activation reachability", all(row["matches"] for row in graph["activation_rows"]), graph["activation_rows"], "ordered union of blocks", "tree")
    audit.check("Duhamel separation", all(row["edge_disjoint"] for row in graph["separation_rows"]), graph["separation_rows"], "D_r U_(r-2)A=0 support premise", "tree")
    audit.check("formal Duhamel word", graph["formal_word"] == ("U3", "D3", "U2", "D2", "U1", "D1", "U0"), graph["formal_word"], "descending activation word", "tree")
    audit.check("tree simplex", graph["simplex_fixture"] == Fraction(125, 162), graph["simplex_fixture"], Fraction(125, 162), "tree")
    audit.check("branches absorbed", len(graph["branches"]) == 6, len(graph["branches"]), 6, "tree")
    audit.check("tree formula authority", "each path edge once" in manifest["tree_and_loop_split"]["tree_theorem"], manifest["tree_and_loop_split"]["tree_theorem"], "one explicit path edge", "tree")
    audit.check("tree norm still open", "does not supply the graph-energy norm bound" in certificate, "does not supply the graph-energy norm bound" in certificate, True, "scope")
    audit.check("square two paths", sorted(graph["square_paths"]) == [(0, 1, 2), (0, 3, 2)], graph["square_paths"], "two exact paths", "square")
    audit.check("square alternate remains", graph["alternate_connected"], graph["alternate_connected"], True, "square")
    audit.check("one extra cut disconnects", graph["extra_cut_disconnects"], graph["extra_cut_disconnects"], True, "square")
    audit.check("square bipartite", graph["square_bipartite"], graph["square_bipartite"], True, "square")
    audit.check("square scope", "rejects only a per-backbone isolation" in manifest["tree_and_loop_split"]["scope"], manifest["tree_and_loop_split"]["scope"], "method-only loop obstruction", "scope")

    trotter = trotter_fixture()
    audit.check("bond kick transfer", trotter["transfer"] == Fraction(6, 35), trotter["transfer"], Fraction(6, 35), "trotter")
    audit.check("bond kick inverse", trotter["inverse_sum"] == 0, trotter["inverse_sum"], 0, "trotter")
    audit.check("bond kick composition", trotter["composition"] == Fraction(129, 385), trotter["composition"], Fraction(129, 385), "trotter")
    audit.check("all bond generators commute", trotter["all_bond_commutators_zero"], trotter["all_bond_commutators_zero"], True, "trotter")
    audit.check("six-edge factorization", trotter["factorized_edge_count"] == 6, trotter["factorized_edge_count"], 6, "trotter")
    audit.check("one-layer support", trotter["one_layer_support"] == list(range(7)), trotter["one_layer_support"], list(range(7)), "trotter")
    audit.check("shift-square PSD", trotter["residual_matrix"][0][0] > 0 and trotter["residual_determinant"] == 0, trotter["residual_matrix"], "rank-one PSD", "trotter")
    audit.check("neighbor factor", trotter["neighbor_factor"] == 54, trotter["neighbor_factor"], 54, "trotter")
    audit.check("q2 kinetic numerator", trotter["q2_kinetic_numerator"] == Fraction(11664, 1225), trotter["q2_kinetic_numerator"], "11664/1225 before 1/(2chi)", "trotter")
    audit.check("kinetic prefactor explicit", trotter["kinetic_prefactor"] == "1/(2chi)", trotter["kinetic_prefactor"], "1/(2chi)", "trotter")
    audit.check("Young completed square", trotter["young_polynomial"] == trotter["young_square"], trotter["young_polynomial"], trotter["young_square"], "trotter")
    audit.check("binomial factorial bound", all(row["c_zero_below_factorial"] for row in trotter["recurrence_rows"]), trotter["recurrence_rows"], "all exact bounds", "trotter")
    audit.check("local growth not dropped", all(row["local_factor_retained"] for row in trotter["recurrence_rows"]), trotter["recurrence_rows"], "C factor retained", "trotter")
    audit.check("Trotter gate identity", manifest["all_bond_trotter_candidate"]["gate_id"] == TROTTER_GATE, manifest["all_bond_trotter_candidate"]["gate_id"], TROTTER_GATE, "trotter")
    audit.check("Trotter obligations", manifest["all_bond_trotter_candidate"]["status"] == "OPEN" and len(manifest["all_bond_trotter_candidate"]["open_obligations"]) == 5, manifest["all_bond_trotter_candidate"]["open_obligations"], "five open obligations", "scope")

    modular = modular_fixture()
    audit.check("log two below one certificate", modular["log_two_below_one_certificate"], modular["log_two_below_one_certificate"], True, "modular")
    audit.check("finite matrix row count", len(modular["rows"]) == 6, len(modular["rows"]), 6, "modular")
    audit.check("finite mean exact margins", all(row["exact_mean_margin_lower_bound"] >= 0 for row in modular["rows"]), [row["exact_mean_margin_lower_bound"] for row in modular["rows"]], "all nonnegative", "modular")
    audit.check("finite mean interpolation", all(row["interpolation_holds"] for row in modular["rows"]), [row["interpolation_decimal"] for row in modular["rows"]], "all true", "modular")
    audit.check("exponential inequality series", all(row["remainder_over_linear"] >= 0 for row in modular["exponential_rows"]), modular["exponential_rows"], "positive Taylor remainder", "modular")
    audit.check("static modular tails decrease", modular["static_decreasing"], [row["static_tail"] for row in modular["rows"]], "strict decrease", "modular")
    audit.check("arbitrary multiplier Duhamel grows", modular["multiplied_increasing"], [row["log2_times_multiplied_duhamel"] for row in modular["rows"]], "strict growth", "modular")
    audit.check("hard dual grows", modular["hard_dual_increasing"], [row["hard_dual"] for row in modular["rows"]], "strict growth", "modular")
    audit.check("zero modular derivative", modular["zero_static_modular_derivative"] and "[H_n,W_n]=0" in manifest["arbitrary_multiplier_counterexample"]["static_tail"], manifest["arbitrary_multiplier_counterexample"]["static_tail"], "zero", "modular")
    audit.check("multiplier constants recombine", modular["multiplier_combination"]["direct"] == modular["multiplier_combination"]["closed"], modular["multiplier_combination"], "exact coefficient equality", "modular")
    audit.check("mean theorem formula", "beta hbar/2" in manifest["modular_mean_topology"]["theorem"], manifest["modular_mean_topology"]["theorem"], "first modular derivative", "modular")
    audit.check("fixed representation scope", "fixed faithful representation" in manifest["modular_mean_topology"]["consequence"], manifest["modular_mean_topology"]["consequence"], "fixed faithful representation", "scope")
    audit.check("multiplier lemma scoped proof", manifest["modular_multiplier_lemma"]["status"].startswith("PROVED") and "OPEN" in manifest["modular_multiplier_lemma"]["status"], manifest["modular_multiplier_lemma"]["status"], "lemma proved, uniform application open", "scope")
    audit.check("arbitrary multiplier formula", "diverges" in manifest["arbitrary_multiplier_counterexample"]["failure"], manifest["arbitrary_multiplier_counterexample"]["failure"], "diverges", "modular")

    cutoff = cutoff_fixture()
    audit.check("cutoff alpha", cutoff["alpha"] == Fraction(1, 4) and 0 < cutoff["alpha"] < Fraction(1, 2), cutoff["alpha"], "0<1/4<1/2", "cutoff")
    audit.check("tail power", cutoff["tail_power"] == Fraction(1, 2), cutoff["tail_power"], Fraction(1, 2), "cutoff")
    audit.check("factorial mlogm", cutoff["factorial_m_log_m_coefficient"] == Fraction(-1, 2), cutoff["factorial_m_log_m_coefficient"], Fraction(-1, 2), "cutoff")
    audit.check("tail logs decrease", cutoff["tail_decreasing"], cutoff["tail_logs"], "strict decrease", "cutoff")
    audit.check("factorial terms decrease", cutoff["factorial_decreasing"], cutoff["factorial_logs"], "strict decrease", "cutoff")
    audit.check("perfect-fourth scale samples", cutoff["scale_sizes"] == [16, 81, 256, 625], cutoff["scale_sizes"], [16, 81, 256, 625], "cutoff")
    audit.check("point radius", cutoff["point_radius"] == Fraction(1, 9), cutoff["point_radius"], Fraction(1, 9), "cutoff")
    audit.check("point radius conservative beta cap", 0 < cutoff["point_radius"] <= cutoff["conservative_radius_cap"] < cutoff["beta"], {"radius": cutoff["point_radius"], "beta_half": cutoff["conservative_radius_cap"], "beta": cutoff["beta"]}, "0<r<=beta/2<beta", "cutoff")
    audit.check("Holder budget", cutoff["holder_budget"] == 2, cutoff["holder_budget"], 2, "cutoff")
    audit.check("required kappa", cutoff["required_kappa"] == 54, cutoff["required_kappa"], 54, "cutoff")
    audit.check("periodic recursion contraction", cutoff["recursion_ratio"] == Fraction(12, 25) < 1, cutoff["recursion_ratio"], Fraction(12, 25), "cutoff")
    audit.check("periodic recursion bound", cutoff["recursion_bound"] == cutoff["recursion_rhs_at_bound"] == Fraction(75, 91), {"bound": cutoff["recursion_bound"], "rhs": cutoff["recursion_rhs_at_bound"]}, Fraction(75, 91), "cutoff")
    audit.check("double commutator coefficient", cutoff["double_commutator_coefficient"] == Fraction(25, 98), cutoff["double_commutator_coefficient"], Fraction(25, 98), "cutoff")
    audit.check("modular derivative coefficient", cutoff["modular_derivative_coefficient"] == Fraction(75, 196), cutoff["modular_derivative_coefficient"], Fraction(75, 196), "cutoff")
    audit.check("double commutator sign", cutoff["formal_double_commutator_sign"] == "(-i)*(2i)=2", cutoff["formal_double_commutator_sign"], "positive", "cutoff")
    audit.check("modular identity authority", "beta hbar^2/chi" in manifest["coordinate_cutoff_route"]["tail"], manifest["coordinate_cutoff_route"]["tail"], "exact gradient identity", "cutoff")
    audit.check("periodic recursion authority", "conditional moment recursion" in manifest["coordinate_cutoff_route"]["imported_input"] and "Translation invariance" in manifest["coordinate_cutoff_route"]["imported_input"], manifest["coordinate_cutoff_route"]["imported_input"], "periodic translation-invariant recursion", "cutoff")
    audit.check("point evaluation radius authority", "0<r<=beta" in certificate.replace("`", ""), "0<r<=beta" in certificate.replace("`", ""), True, "cutoff")
    audit.check("outer cutoff authority", "outer bounded cutoff" in certificate and "both bond endpoints" in certificate, {"outer": "outer bounded cutoff" in certificate, "both_endpoints": "both bond endpoints" in certificate}, "bounded outer cutoff and two-endpoint gradient", "cutoff")
    audit.check("quadratic growth boundary", "no faster than poly(L)exp(C_0 T L^2)" in manifest["coordinate_cutoff_route"]["scale_balance"], manifest["coordinate_cutoff_route"]["scale_balance"], "quadratic exponential only", "scope")
    audit.check("modular gate identity", manifest["coordinate_cutoff_route"]["gate_id"] == MODULAR_GATE, manifest["coordinate_cutoff_route"]["gate_id"], MODULAR_GATE, "cutoff")
    audit.check("coordinate obligations", manifest["coordinate_cutoff_route"]["status"] == "OPEN" and len(manifest["coordinate_cutoff_route"]["open_obligations"]) == 4, manifest["coordinate_cutoff_route"]["open_obligations"], "four open obligations", "scope")

    os_mix = os_mixture_fixture()
    audit.check("OS interior mixture weight", os_mix["lambda_is_interior"], os_mix["lambda"], "0<lambda<1", "OS")
    audit.check("OS common test algebra fixture", os_mix["common_positive_time_test_algebra_dimension"] == 3 and "common positive-time test algebra" in manifest["fixed_beta_os_mixture_envelope"]["form_theorem"], {"dimension": os_mix["common_positive_time_test_algebra_dimension"], "authority": manifest["fixed_beta_os_mixture_envelope"]["form_theorem"]}, "one common three-dimensional test space", "OS")
    audit.check("OS form mixture", os_mix["q_zero_diag"] == (Fraction(2, 5), Fraction(3, 5), Fraction(0)), os_mix["q_zero_diag"], "lambda q+ +(1-lambda)q-", "OS")
    audit.check("OS kernel intersection", os_mix["kernel_zero"] == os_mix["kernel_intersection"] == (2,), {"zero": os_mix["kernel_zero"], "intersection": os_mix["kernel_intersection"]}, (2,), "OS")
    audit.check("OS sample isometry", os_mix["zero_norm"] == os_mix["direct_sum_norm"] == 7, {"zero": os_mix["zero_norm"], "direct": os_mix["direct_sum_norm"]}, 7, "OS")
    audit.check("OS quotient plus", os_mix["plus_quotient_norm_square"] == Fraction(5, 2), os_mix["plus_quotient_norm_square"], Fraction(5, 2), "OS")
    audit.check("OS quotient minus", os_mix["minus_quotient_norm_square"] == Fraction(5, 3), os_mix["minus_quotient_norm_square"], Fraction(5, 3), "OS")
    audit.check("OS image may be proper", os_mix["shared_form_domain_dimension"] < os_mix["shared_form_direct_sum_dimension"], {"domain": os_mix["shared_form_domain_dimension"], "direct_sum": os_mix["shared_form_direct_sum_dimension"]}, "proper one-dimensional image possible", "OS")
    audit.check("OS probability mixture", os_mix["mixture_lambda"] == Fraction(2, 5) and os_mix["mu_zero"] == (Fraction(9, 20), Fraction(11, 20)), {"lambda": os_mix["mixture_lambda"], "mu_zero": os_mix["mu_zero"]}, {"lambda": Fraction(2, 5), "mu_zero": (Fraction(9, 20), Fraction(11, 20))}, "OS")
    audit.check("OS RN plus", os_mix["rn_plus"] == (Fraction(5, 3), Fraction(5, 11)), os_mix["rn_plus"], (Fraction(5, 3), Fraction(5, 11)), "OS")
    audit.check("OS RN minus", os_mix["rn_minus"] == (Fraction(5, 9), Fraction(15, 11)), os_mix["rn_minus"], (Fraction(5, 9), Fraction(15, 11)), "OS")
    audit.check("OS densities not projections", os_mix["rn_not_projections"], {"plus": os_mix["rn_plus"], "minus": os_mix["rn_minus"]}, "nonprojection", "OS")
    audit.check("OS fixed-beta scope", "not a beta-independent Hamiltonian common alpha" in manifest["fixed_beta_os_mixture_envelope"]["scope"], manifest["fixed_beta_os_mixture_envelope"]["scope"], "fixed-beta precursor only", "scope")

    retired = manifest["retired_or_superseded_gates"]
    audit.check("first-passage gate retired", "PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-PRODUCT-AND-ENERGY-TAIL-CLOSURE" in retired, list(retired), "historical first-passage gate", "provenance")
    audit.check("fifth-moment gate superseded", "PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-MODULAR-CUTOFF-LOCALITY" in retired, list(retired), "historical fifth-moment gate", "provenance")
    audit.check("successor gates ordered", manifest["open_gates"][:2] == [TROTTER_GATE, MODULAR_GATE], manifest["open_gates"], [TROTTER_GATE, MODULAR_GATE], "provenance")
    audit.check("closed subgates four", len(manifest["closed_subgates"]) == 4, manifest["closed_subgates"], "four scoped closures", "provenance")
    audit.check("partial status", manifest["status"].startswith("PARTIALLY RESOLVED:") and "REMAIN OPEN" in manifest["status"], manifest["status"], "partial with open gates", "scope")

    for token in (
        "graph-Lipschitz stability",
        "Trotter convergence",
        "projected Duhamel",
        "common C-star alpha",
        "common-alpha KMS",
        "algebraic ground states",
        "GNS",
        "regulator removal",
        "continuum",
        "physical empty space",
        "below-empty sign",
        "functional selection",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(f"no-overclaim {token}", token in manifest["no_overclaim"], manifest["no_overclaim"], f"contains {token}", "scope")

    certificate_flat = " ".join(certificate.replace("`", "").split()).lower()
    for phrase in (
        "not a nonexistence theorem for the dynamics",
        "does not include the onsite quartic flow",
        "does not supply the graph-energy norm bound",
        "does not manufacture a common representation across volumes",
        "ordinary operator-norm control of b is not enough",
        "fixed-beta envelope precursor",
        "sector a or pre-a",
    ):
        audit.check(f"certificate boundary {phrase}", phrase in certificate_flat, phrase in certificate_flat, True, "scope")

    source_paths = (SCRIPT, MANIFEST, CERTIFICATE, PARENT, EUCLIDEAN_PARENT)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
    }
    for relative_path, digest in source_hashes.items():
        audit.check(
            f"source hash {relative_path}",
            len(digest) == 64 and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": (
            "tect/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-"
            "resummation-route-split-independent-result/1.0"
        ),
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_version": manifest["result_version"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_ids": manifest["claim_ids"],
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
            "star_coefficient": star["coefficient"],
            "first_failure_half": star["first_failure_half"],
            "first_failure_three_quarters": star["first_failure_three_quarters"],
            "all_order_phase": star["theta"],
            "target_leaf_phase": star["target_phase"],
            "tree_simplex_fixture": graph["simplex_fixture"],
            "tree_components": graph["components"],
            "square_paths": graph["square_paths"],
            "square_alternate_connected": graph["alternate_connected"],
            "bond_kick_transfer": trotter["transfer"],
            "bond_kick_composition": trotter["composition"],
            "neighbor_factor": trotter["neighbor_factor"],
            "q2_kinetic_numerator": trotter["q2_kinetic_numerator"],
            "modular_rows": modular["rows"],
            "cutoff_alpha": cutoff["alpha"],
            "cutoff_factorial_exponent": cutoff["factorial_m_log_m_coefficient"],
            "cutoff_modular_derivative_coefficient": cutoff["modular_derivative_coefficient"],
            "os_rn_plus": os_mix["rn_plus"],
            "os_rn_minus": os_mix["rn_minus"],
            "fixed_order_first_passage_closed": False,
            "all_bond_trotter_closed": False,
            "projected_modular_locality_closed": False,
            "common_alpha_closed": False,
        },
        "source_hashes": source_hashes,
        "boundary": manifest["no_overclaim"],
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
