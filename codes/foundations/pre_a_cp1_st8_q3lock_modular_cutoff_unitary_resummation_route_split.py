#!/usr/bin/env python3
"""Primary exact verifier for the R-167 v1.2 route correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import deque
from itertools import permutations
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split-manifest.json"
EUCLIDEAN_PARENT = REPO / "strategy/pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-10-primary-{SLUG}/result.json"


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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def star_audit() -> dict[str, Any]:
    # Declared rational fixture inputs, not derived or fitted numbers.
    c = sp.Rational(3, 5)
    shift = sp.Rational(7, 11)
    time = sp.Rational(5, 7)
    hbar = sp.Rational(13, 17)
    target_shift = sp.Rational(11, 17)
    k = -c * shift
    theta = sp.simplify(k * time / hbar)
    target_phase = sp.simplify(theta * target_shift)

    distinct_rows: list[dict[str, Any]] = []
    for m in (1, 2, 3, 4):
        signatures = {(tuple(order), k**m, tuple([1] * m)) for order in permutations(range(m))}
        distinct_rows.append(
            {
                "m": m,
                "ordering_count": math.factorial(m),
                "signature_count": len({(coefficient, exponents) for _, coefficient, exponents in signatures}),
                "coefficient": k**m,
                "summed_coefficient": sp.factorial(m) * k**m,
            }
        )

    q = sp.symbols("q0:3")
    all_order_rows: list[dict[str, Any]] = []
    for n in range(9):
        polynomial = sp.Poly(sp.expand(sum(q) ** n), *q)
        coefficient_sum = sum(polynomial.coeff_monomial(monomial) for monomial in polynomial.monoms())
        all_order_rows.append(
            {
                "n": n,
                "monomial_count": len(polynomial.terms()),
                "coefficient_sum": coefficient_sum,
                "expected_sum": 3**n,
                "real_taylor_prefactor": sp.simplify(theta**n / sp.factorial(n)),
                "complex_phase": f"i^{n}",
            }
        )

    growth = {
        "s_half_m2": sp.Rational(2) - 4 * sp.Rational(1, 2),
        "s_half_m3": sp.Rational(3) - 4 * sp.Rational(1, 2),
        "s_three_quarters_m3": sp.Rational(3) - 4 * sp.Rational(3, 4),
        "s_three_quarters_m4": sp.Rational(4) - 4 * sp.Rational(3, 4),
    }
    return {
        "inputs": {"c": c, "shift": shift, "time": time, "hbar": hbar, "target_shift": target_shift},
        "k": k,
        "theta": theta,
        "target_phase": target_phase,
        "distinct_rows": distinct_rows,
        "repeated_coefficients": [k**n for n in range(1, 9)],
        "all_order_rows": all_order_rows,
        "growth": growth,
        "first_failure_half": min(m for m in range(1, 7) if sp.Rational(m) > 4 * sp.Rational(1, 2)),
        "first_failure_three_quarters": min(m for m in range(1, 7) if sp.Rational(m) > 4 * sp.Rational(3, 4)),
    }


def adjacency(vertices: set[int], edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    graph = {vertex: set() for vertex in vertices}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


def connected_component(start: int, graph: dict[int, set[int]]) -> set[int]:
    seen = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def simple_paths(graph: dict[int, set[int]], start: int, target: int) -> list[tuple[int, ...]]:
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


def graph_audit() -> dict[str, Any]:
    vertices = set(range(10))
    backbone = [(0, 1), (1, 2), (2, 3)]
    branches = [(0, 4), (1, 5), (1, 6), (2, 7), (3, 8), (8, 9)]
    edges = backbone + branches
    graph = adjacency(vertices, edges)
    remaining = adjacency(vertices, branches)
    components = [sorted(connected_component(root, remaining)) for root in (0, 1, 2, 3)]

    square_vertices = {0, 1, 2, 3}
    square_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    square_graph = adjacency(square_vertices, square_edges)
    square_paths = simple_paths(square_graph, 0, 2)
    square_remaining = adjacency(square_vertices, [(2, 3), (3, 0)])
    return {
        "tree_connected": connected_component(0, graph) == vertices,
        "tree_edge_count": len(edges),
        "tree_vertex_count": len(vertices),
        "tree_paths": simple_paths(graph, 0, 3),
        "components": components,
        "backbone": backbone,
        "branch_count": len(branches),
        "simplex_fixture": sp.Rational(5, 3) ** 3 / sp.factorial(3),
        "square_paths": square_paths,
        "square_alternate_connected": 2 in connected_component(0, square_remaining),
        "square_bipartite": all((left + right) % 2 == 1 for left, right in square_edges),
    }


def trotter_audit() -> dict[str, Any]:
    c = sp.Rational(3, 5)
    delta = sp.Rational(2, 7)
    delta_two = sp.Rational(3, 11)
    eta = sp.Rational(1, 5)
    degree = sp.Integer(6)
    neighbor_ratio = sp.Rational(3, 2)
    transfer = sp.simplify(c * delta)
    composed_transfer = sp.simplify(c * (delta + delta_two))
    residual_matrix = sp.Matrix([[eta, -transfer], [-transfer, transfer**2 / eta]])
    neighbor_factor = degree**2 * neighbor_ratio
    q2_coefficient = sp.simplify((1 + 1 / eta) * transfer**2 * neighbor_factor)
    q = sp.symbols("q", real=True)
    epsilon = sp.Rational(1, 3)
    young_residual = sp.factor(epsilon * q**4 + 1 / (4 * epsilon) - q**2)

    local_growth = sp.Rational(2, 5)
    transfer_rate = sp.Rational(3, 7)
    time = sp.Rational(5, 4)
    recurrence_rows: list[dict[str, Any]] = []
    for steps in (4, 8, 16):
        for distance in range(0, 5):
            if distance > steps:
                continue
            exact = sp.binomial(steps, distance) * (transfer_rate * time / steps) ** distance * (
                1 + local_growth * time / steps
            ) ** (steps - distance)
            c_zero = sp.binomial(steps, distance) * (transfer_rate * time / steps) ** distance
            factorial_bound = (transfer_rate * time) ** distance / sp.factorial(distance)
            recurrence_rows.append(
                {
                    "steps": steps,
                    "distance": distance,
                    "exact": exact,
                    "c_zero": c_zero,
                    "c_zero_below_factorial": c_zero <= factorial_bound,
                }
            )
    return {
        "transfer": transfer,
        "composed_transfer": composed_transfer,
        "residual_matrix": residual_matrix,
        "residual_determinant": sp.simplify(residual_matrix.det()),
        "residual_principal": residual_matrix[0, 0],
        "neighbor_factor": neighbor_factor,
        "q2_coefficient": q2_coefficient,
        "young_residual": young_residual,
        "recurrence_rows": recurrence_rows,
    }


def modular_mean_audit() -> dict[str, Any]:
    u = sp.symbols("u", positive=True)
    ratio = u * (sp.exp(u) + 1) / (2 * (sp.exp(u) - 1))
    exponential_residual = sp.factor(sp.together(2 * (sp.exp(u) - 1) * (1 + u / 2 - ratio)))

    rows: list[dict[str, Any]] = []
    for n in (4, 8, 12, 16, 20, 24):
        r = sp.Rational(1, 2) ** n
        gap = n * sp.log(2)
        p0 = 1 / (1 + r)
        p1 = r / (1 + r)
        logarithmic_mean = sp.simplify((p0 - p1) / gap)
        arithmetic_mean = sp.simplify((p0 + p1) / 2)
        modular_derivative_square = sp.simplify(gap**2 * logarithmic_mean)
        interpolation_rhs = sp.simplify(logarithmic_mean + sp.sqrt(logarithmic_mean * modular_derivative_square) / 2)
        scale = sp.Integer(2) ** (n // 4)
        static_tail = sp.simplify(p1 * scale**2)
        multiplied_duhamel = sp.simplify(scale**2 * logarithmic_mean)
        hard_dual = sp.simplify(p0 * scale**2)
        rows.append(
            {
                "n": n,
                "r": r,
                "logarithmic_mean": logarithmic_mean,
                "arithmetic_mean": arithmetic_mean,
                "modular_derivative_square": modular_derivative_square,
                "interpolation_rhs": interpolation_rhs,
                "interpolation_holds": arithmetic_mean <= interpolation_rhs,
                "static_tail": static_tail,
                "multiplied_duhamel": multiplied_duhamel,
                "hard_dual": hard_dual,
                "half_strip_multiplier": sp.Integer(2) ** (n // 2),
            }
        )
    return {
        "ratio": ratio,
        "exponential_residual": exponential_residual,
        "rows": rows,
        "static_decreasing": all(rows[i + 1]["static_tail"] < rows[i]["static_tail"] for i in range(len(rows) - 1)),
        "multiplied_increasing": all(
            rows[i + 1]["multiplied_duhamel"] > rows[i]["multiplied_duhamel"] for i in range(len(rows) - 1)
        ),
        "dual_increasing": all(rows[i + 1]["hard_dual"] > rows[i]["hard_dual"] for i in range(len(rows) - 1)),
        "half_strip_increasing": all(
            rows[i + 1]["half_strip_multiplier"] > rows[i]["half_strip_multiplier"]
            for i in range(len(rows) - 1)
        ),
    }


def cutoff_audit() -> dict[str, Any]:
    alpha = sp.Rational(1, 4)
    dimension = sp.Integer(3)
    polynomial_degree = sp.Integer(5)
    margin = sp.Integer(2)  # Declared fixture a-C0*T.
    sample_m = (16, 32, 64, 128)
    tail_logs = [
        float((dimension + alpha * polynomial_degree) * sp.log(m) - margin * m ** (2 * alpha))
        for m in sample_m
    ]
    factorial_logs = [
        float(polynomial_degree * alpha * sp.log(m) + m * sp.log(m ** (2 * alpha)) - sp.loggamma(m + 1))
        for m in sample_m
    ]

    # Periodic conditional-recursion and point-evaluation fixtures.
    degree = sp.Integer(6)
    coupling = sp.Rational(3, 5)
    j_hat = degree * coupling
    recursion_theta = sp.Rational(1, 4)
    moment_kappa = sp.Integer(2)
    recursion_constant = sp.Rational(7, 5)
    recursion_denominator = sp.simplify(1 - recursion_theta * j_hat / moment_kappa)
    recursion_bound = sp.simplify(recursion_constant / recursion_denominator)

    # Point-evaluation coefficient selection, with sigma=1/4 and declared a=3.
    sigma = sp.Rational(1, 4)
    a = sp.Integer(3)
    lambda_sigma = sp.Integer(2)
    beta = sp.Integer(2)
    radius = (lambda_sigma / (2 * a)) ** (1 / (2 * sigma))
    required_kappa = sp.simplify(2 * a / radius)
    beta_symbol, hbar_symbol, chi_symbol, w1_symbol = sp.symbols("beta hbar chi w1", positive=True)
    # Independently reduce [w,[p^2/(2chi),w]] from [w,p]=i hbar w'.
    commutator_w_p = sp.I * hbar_symbol * w1_symbol
    double_commutator = sp.simplify(
        (-2 * sp.I * hbar_symbol * w1_symbol * commutator_w_p) / (2 * chi_symbol)
    )
    dirichlet_coefficient = sp.simplify(beta_symbol * double_commutator / w1_symbol**2)
    return {
        "alpha": alpha,
        "dimension": dimension,
        "polynomial_degree": polynomial_degree,
        "margin": margin,
        "tail_power": 2 * alpha,
        "factorial_m_log_m_coefficient": 2 * alpha - 1,
        "tail_logs": tail_logs,
        "factorial_logs": factorial_logs,
        "tail_eventually_decreasing": tail_logs[-1] < tail_logs[-2],
        "factorial_decreasing": all(right < left for left, right in zip(factorial_logs, factorial_logs[1:])),
        "j_hat": j_hat,
        "recursion_theta": recursion_theta,
        "moment_kappa": moment_kappa,
        "recursion_denominator": recursion_denominator,
        "recursion_bound": recursion_bound,
        "point_radius": radius,
        "beta": beta,
        "holder_budget": sp.simplify(2 * a * radius ** (2 * sigma)),
        "required_kappa": required_kappa,
        "double_commutator": double_commutator,
        "dirichlet_coefficient": dirichlet_coefficient,
        "dirichlet_expected": beta_symbol * hbar_symbol**2 / chi_symbol,
    }


def os_mixture_audit() -> dict[str, Any]:
    lam = sp.Rational(2, 5)
    q_plus_matrix = sp.diag(1, 0)
    q_minus_matrix = sp.diag(0, 1)
    q_zero_matrix = sp.simplify(lam * q_plus_matrix + (1 - lam) * q_minus_matrix)
    plus_vector = sp.Matrix([1, 0])
    minus_vector = sp.Matrix([0, 1])
    plus_ratio = sp.simplify((plus_vector.dot(plus_vector)) / (plus_vector.dot(q_zero_matrix * plus_vector)))
    minus_ratio = sp.simplify((minus_vector.dot(minus_vector)) / (minus_vector.dot(q_zero_matrix * minus_vector)))

    common_test = sp.Matrix(sp.symbols("f0:2"))
    embedded = sp.Matrix(
        [
            sp.sqrt(lam) * common_test[0],
            sp.sqrt(1 - lam) * common_test[1],
        ]
    )
    mixture_norm = sp.simplify((common_test.T * q_zero_matrix * common_test)[0])
    embedded_norm = sp.simplify(embedded.dot(embedded))

    mu_plus = [sp.Rational(3, 4), sp.Rational(1, 4)]
    mu_minus = [sp.Rational(1, 4), sp.Rational(3, 4)]
    mu_zero = [sp.simplify(lam * a + (1 - lam) * b) for a, b in zip(mu_plus, mu_minus)]
    rn_plus = [sp.simplify(a / z) for a, z in zip(mu_plus, mu_zero)]
    rn_minus = [sp.simplify(a / z) for a, z in zip(mu_minus, mu_zero)]
    return {
        "lambda": lam,
        "plus_norm_square": plus_ratio,
        "minus_norm_square": minus_ratio,
        "q_zero_matrix": q_zero_matrix,
        "q_zero_determinant": sp.simplify(q_zero_matrix.det()),
        "mixture_norm": mixture_norm,
        "embedded_norm": embedded_norm,
        "mu_zero": mu_zero,
        "rn_plus": rn_plus,
        "rn_minus": rn_minus,
        "rn_are_not_projections": any(value not in (0, 1) for value in rn_plus + rn_minus),
    }


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    euclidean_parent = json.loads(EUCLIDEAN_PARENT.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("schema", manifest["schema"] == "tect/pre-a-route-split/1.0", manifest["schema"], "tect/pre-a-route-split/1.0", "provenance")
    audit.check("result number reused", manifest["result_number"] == "R-167", manifest["result_number"], "R-167", "provenance")
    audit.check("result id reused", manifest["result_id"] == parent["result_id"], manifest["result_id"], parent["result_id"], "provenance")
    audit.check("version", manifest["result_version"] == "v1.2", manifest["result_version"], "v1.2", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-000798", manifest["exploration_id"], "EXP-000798", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "provenance")
    audit.check("two negatives", len(manifest["negative_ids"]) == 2, manifest["negative_ids"], "two exact IDs", "provenance")
    audit.check("certificate identity", manifest["result_id"] in certificate and "EXP-000798" in certificate, True, True, "provenance")
    audit.check("Euclidean parent imported", euclidean_parent["exploration_id"] == "EXP-000781", euclidean_parent["exploration_id"], "EXP-000781", "provenance")
    audit.check("Euclidean moment authority", euclidean_parent["scope"]["uniform_exponential_local_moments"] is True, euclidean_parent["scope"]["uniform_exponential_local_moments"], True, "provenance")

    star = star_audit()
    audit.check("star k", star["k"] == -sp.Rational(21, 55), star["k"], "-21/55", "star")
    audit.check("star cubic coefficient", star["distinct_rows"][2]["coefficient"] == -sp.Rational(9261, 166375), star["distinct_rows"][2]["coefficient"], "-9261/166375", "star")
    audit.check("star quartic coefficient", star["distinct_rows"][3]["coefficient"] == sp.Rational(194481, 9150625), star["distinct_rows"][3]["coefficient"], "194481/9150625", "star")
    audit.check("all permutations agree", all(row["signature_count"] == 1 for row in star["distinct_rows"]), star["distinct_rows"], "one signature per m", "star")
    audit.check("no permutation cancellation", all(row["summed_coefficient"] != 0 for row in star["distinct_rows"]), [row["summed_coefficient"] for row in star["distinct_rows"]], "all nonzero", "star")
    audit.check("repeat powers nonzero", all(value != 0 for value in star["repeated_coefficients"]), star["repeated_coefficients"], "all nonzero", "star")
    audit.check("half threshold", star["first_failure_half"] == 3 and star["growth"]["s_half_m3"] == 1, star["growth"], "m=3 growth 1", "star")
    audit.check("three-quarter threshold", star["first_failure_three_quarters"] == 4 and star["growth"]["s_three_quarters_m4"] == 1, star["growth"], "m=4 growth 1", "star")
    audit.check("manifest fixed-order rejected", manifest["fixed_order_first_passage_counterexample"]["verdict"].startswith("THE V1.1 FIXED-s"), manifest["fixed_order_first_passage_counterexample"]["verdict"], "route false as stated", "scope")

    audit.check("all-order theta", star["theta"] == -sp.Rational(51, 143), star["theta"], "-51/143", "resummation")
    audit.check("target phase", star["target_phase"] == -sp.Rational(3, 13), star["target_phase"], "-3/13", "resummation")
    audit.check("multinomial coefficient sums", all(row["coefficient_sum"] == row["expected_sum"] for row in star["all_order_rows"]), star["all_order_rows"], "3^n", "resummation")
    audit.check("unitary i retained", "-i c a t" in manifest["all_order_star_resummation"]["identity"], manifest["all_order_star_resummation"]["identity"], "imaginary phase", "resummation")
    audit.check("subflow scope", "not the onsite-plus-bond Trotter limit" in manifest["all_order_star_resummation"]["scope"], manifest["all_order_star_resummation"]["scope"], "subflow only", "scope")

    graph = graph_audit()
    audit.check("tree criterion", graph["tree_connected"] and graph["tree_edge_count"] == graph["tree_vertex_count"] - 1, graph, "connected tree", "tree")
    audit.check("tree unique backbone", graph["tree_paths"] == [(0, 1, 2, 3)], graph["tree_paths"], [(0, 1, 2, 3)], "tree")
    audit.check("tree components", graph["components"] == [[0, 4], [1, 5, 6], [2, 7], [3, 8, 9]], graph["components"], "four exact components", "tree")
    audit.check("tree simplex", graph["simplex_fixture"] == sp.Rational(125, 162), graph["simplex_fixture"], "125/162", "tree")
    audit.check("square two paths", sorted(graph["square_paths"]) == [(0, 1, 2), (0, 3, 2)], graph["square_paths"], "two paths", "square")
    audit.check("square alternate remains", graph["square_alternate_connected"], graph["square_alternate_connected"], True, "square")
    audit.check("square bipartite", graph["square_bipartite"], graph["square_bipartite"], True, "square")
    audit.check("square scope", "rejects only a per-backbone isolation" in manifest["tree_and_loop_split"]["scope"], manifest["tree_and_loop_split"]["scope"], "method-only obstruction", "scope")

    trotter = trotter_audit()
    audit.check("kick transfer", trotter["transfer"] == sp.Rational(6, 35), trotter["transfer"], "6/35", "trotter")
    audit.check("kick composition", trotter["composed_transfer"] == sp.Rational(129, 385), trotter["composed_transfer"], "129/385", "trotter")
    audit.check("shift square PSD", trotter["residual_principal"] > 0 and trotter["residual_determinant"] == 0, trotter["residual_matrix"], "PSD rank one", "trotter")
    audit.check("neighbor factor", trotter["neighbor_factor"] == 54, trotter["neighbor_factor"], 54, "trotter")
    audit.check("q2 kinetic numerator", trotter["q2_coefficient"] == sp.Rational(11664, 1225), trotter["q2_coefficient"], "11664/1225 before 1/(2chi)", "trotter")
    audit.check("Young square", trotter["young_residual"] == (2 * sp.symbols("q", real=True) ** 2 - 3) ** 2 / 12, trotter["young_residual"], "(2q^2-3)^2/12", "trotter")
    audit.check("binomial factorial bound", all(row["c_zero_below_factorial"] for row in trotter["recurrence_rows"]), trotter["recurrence_rows"], "all true", "trotter")
    audit.check("local growth retained", all("exact" in row and "c_zero" in row for row in trotter["recurrence_rows"]), True, True, "trotter")
    audit.check("Trotter remains open", manifest["all_bond_trotter_candidate"]["status"] == "OPEN" and len(manifest["all_bond_trotter_candidate"]["open_obligations"]) == 5, manifest["all_bond_trotter_candidate"], "five open obligations", "scope")

    modular = modular_mean_audit()
    u = sp.symbols("u", positive=True)
    audit.check("mean inequality reduction", sp.simplify(modular["exponential_residual"] - 2 * (sp.exp(u) - 1 - u)) == 0, modular["exponential_residual"], "2(exp(u)-1-u)", "modular")
    audit.check("finite mean fixtures", all(row["interpolation_holds"] for row in modular["rows"]), modular["rows"], "all true", "modular")
    audit.check("static tails decrease", modular["static_decreasing"], [row["static_tail"] for row in modular["rows"]], "decrease", "modular")
    audit.check("arbitrary multiplier Duhamel diverges", modular["multiplied_increasing"], [row["multiplied_duhamel"] for row in modular["rows"]], "increase", "modular")
    audit.check("arbitrary multiplier dual diverges", modular["dual_increasing"], [row["hard_dual"] for row in modular["rows"]], "increase", "modular")
    audit.check("half-strip multiplier grows", modular["half_strip_increasing"], [row["half_strip_multiplier"] for row in modular["rows"]], "increase", "modular")
    audit.check("zero modular tail derivative", "[H_n,W_n]=0" in manifest["arbitrary_multiplier_counterexample"]["static_tail"], manifest["arbitrary_multiplier_counterexample"]["static_tail"], "zero derivative", "modular")
    audit.check("faithful representation scope", "finite type-I Gibbs representation" in manifest["modular_mean_topology"]["consequence"] and "general W-star extension" in manifest["modular_mean_topology"]["scope"], manifest["modular_mean_topology"], "finite type-I proof and general W-star boundary", "scope")
    audit.check("multiplier lemma proved", manifest["modular_multiplier_lemma"]["status"].startswith("PROVED"), manifest["modular_multiplier_lemma"]["status"], "proved scoped lemma", "modular")
    audit.check("structured multiplier open", "ARE OPEN" in manifest["modular_multiplier_lemma"]["status"], manifest["modular_multiplier_lemma"]["status"], "uniform structured bound open", "scope")

    cutoff = cutoff_audit()
    audit.check("cutoff alpha window", 0 < cutoff["alpha"] < sp.Rational(1, 2), cutoff["alpha"], "0<alpha<1/2", "cutoff")
    audit.check("tail exponent positive", cutoff["tail_power"] > 0, cutoff["tail_power"], ">0", "cutoff")
    audit.check("factorial exponent negative", cutoff["factorial_m_log_m_coefficient"] == -sp.Rational(1, 2), cutoff["factorial_m_log_m_coefficient"], "-1/2", "cutoff")
    audit.check("cutoff logs decay", cutoff["tail_eventually_decreasing"] and cutoff["factorial_decreasing"], cutoff, "decay", "cutoff")
    audit.check("periodic recursion admissible", cutoff["recursion_theta"] * cutoff["j_hat"] < cutoff["moment_kappa"] and cutoff["recursion_denominator"] == sp.Rational(11, 20), cutoff, "theta Jhat<kappa and denominator 11/20", "cutoff")
    audit.check("periodic recursion bound", cutoff["recursion_bound"] == sp.Rational(28, 11), cutoff["recursion_bound"], "28/11", "cutoff")
    audit.check("periodic recursion derivation", all(token in manifest["coordinate_cutoff_route"]["imported_input"] for token in ("Lemma 4.1", "generalized Holder", "Jhat_Lambda<=6c", "Finite-volume integrability")), manifest["coordinate_cutoff_route"]["imported_input"], "conditional lemma, Holder and finite-volume bridge", "cutoff")
    audit.check("point Holder budget", cutoff["holder_budget"] == 2, cutoff["holder_budget"], 2, "cutoff")
    audit.check("point radius beta cap", 0 < cutoff["point_radius"] <= cutoff["beta"] / 2, {"radius": cutoff["point_radius"], "beta": cutoff["beta"]}, "0<r<=beta/2", "cutoff")
    audit.check("point L2 coefficient", cutoff["required_kappa"] == 54 and cutoff["required_kappa"] > cutoff["recursion_theta"] * cutoff["j_hat"], cutoff["required_kappa"], "54 and above recursion threshold", "cutoff")
    audit.check("double commutator reduction", sp.simplify(cutoff["double_commutator"] - sp.symbols("hbar", positive=True) ** 2 * sp.symbols("w1", positive=True) ** 2 / sp.symbols("chi", positive=True)) == 0, cutoff["double_commutator"], "hbar^2*w1^2/chi", "cutoff")
    audit.check("Dirichlet coefficient", sp.simplify(cutoff["dirichlet_coefficient"] - cutoff["dirichlet_expected"]) == 0, cutoff["dirichlet_coefficient"], "beta*hbar^2/chi", "cutoff")
    audit.check("outer cutoff scope", "bounded outer truncation" in manifest["coordinate_cutoff_route"]["tail"] and "both endpoints" in manifest["coordinate_cutoff_route"]["tail"], manifest["coordinate_cutoff_route"]["tail"], "bounded outer truncation and both endpoints", "scope")
    audit.check("coordinate route open", manifest["coordinate_cutoff_route"]["status"] == "OPEN" and len(manifest["coordinate_cutoff_route"]["open_obligations"]) == 4, manifest["coordinate_cutoff_route"], "four open obligations", "scope")
    audit.check("growth boundary", "no faster than poly(L)exp(C_0 T L^2)" in manifest["coordinate_cutoff_route"]["scale_balance"], manifest["coordinate_cutoff_route"]["scale_balance"], "quadratic exponential only", "scope")

    os_mix = os_mixture_audit()
    audit.check("OS quotient plus norm", os_mix["plus_norm_square"] == 1 / os_mix["lambda"], os_mix["plus_norm_square"], "lambda^-1", "OS")
    audit.check("OS quotient minus norm", os_mix["minus_norm_square"] == 1 / (1 - os_mix["lambda"]), os_mix["minus_norm_square"], "(1-lambda)^-1", "OS")
    audit.check("OS lambda interior", 0 < os_mix["lambda"] < 1, os_mix["lambda"], "0<lambda<1", "OS")
    audit.check("OS null intersection", os_mix["q_zero_determinant"] > 0, os_mix["q_zero_matrix"], "positive definite mixture for transverse null forms", "OS")
    audit.check("OS isometry", sp.simplify(os_mix["mixture_norm"] - os_mix["embedded_norm"]) == 0, {"mixture": os_mix["mixture_norm"], "embedded": os_mix["embedded_norm"]}, "equal norms", "OS")
    audit.check("OS weighted mixture", os_mix["mu_zero"] == [sp.Rational(9, 20), sp.Rational(11, 20)], os_mix["mu_zero"], "lambda-weighted mixture", "OS")
    audit.check("distinct not central", os_mix["rn_are_not_projections"], {"plus": os_mix["rn_plus"], "minus": os_mix["rn_minus"]}, "nonprojection densities", "OS")
    audit.check("OS common test hypotheses", "0<lambda<1" in manifest["fixed_beta_os_mixture_envelope"]["form_theorem"] and "same reflection" in manifest["fixed_beta_os_mixture_envelope"]["form_theorem"], manifest["fixed_beta_os_mixture_envelope"]["form_theorem"], "interior lambda and common reflection/test algebra", "OS")
    audit.check("OS scope", "not a beta-independent Hamiltonian common alpha" in manifest["fixed_beta_os_mixture_envelope"]["scope"], manifest["fixed_beta_os_mixture_envelope"]["scope"], "fixed-beta only", "scope")

    retired = manifest["retired_or_superseded_gates"]
    audit.check("old first passage retained", "PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-PRODUCT-AND-ENERGY-TAIL-CLOSURE" in retired, list(retired), "historical gate retained", "provenance")
    audit.check("old fifth moment retained", "PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-MODULAR-CUTOFF-LOCALITY" in retired, list(retired), "historical gate retained", "provenance")
    audit.check("two new active gates", manifest["open_gates"][:2] == [manifest["all_bond_trotter_candidate"]["gate_id"], manifest["coordinate_cutoff_route"]["gate_id"]], manifest["open_gates"], "two exact successors", "provenance")

    for token in (
        "graph-Lipschitz stability",
        "Trotter convergence",
        "projected Duhamel",
        "common C-star alpha",
        "common-alpha KMS",
        "algebraic ground states",
        "GNS",
        "continuum",
        "physical empty space",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(f"no-overclaim {token}", token in manifest["no_overclaim"], manifest["no_overclaim"], f"contains {token}", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split-primary-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "result_version": manifest["result_version"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "star_coefficient": str(star["k"]),
            "first_failure_half": star["first_failure_half"],
            "first_failure_three_quarters": star["first_failure_three_quarters"],
            "all_order_phase": str(star["theta"]),
            "target_leaf_phase": str(star["target_phase"]),
            "tree_simplex_fixture": str(graph["simplex_fixture"]),
            "square_paths": graph["square_paths"],
            "bond_kick_transfer": str(trotter["transfer"]),
            "bond_kick_composition": str(trotter["composed_transfer"]),
            "neighbor_factor": str(trotter["neighbor_factor"]),
            "q2_kinetic_numerator": str(trotter["q2_coefficient"]),
            "mean_inequality_residual": str(modular["exponential_residual"]),
            "modular_rows": json_safe(modular["rows"]),
            "cutoff_alpha": str(cutoff["alpha"]),
            "cutoff_factorial_exponent": str(cutoff["factorial_m_log_m_coefficient"]),
            "os_rn_plus": [str(value) for value in os_mix["rn_plus"]],
            "os_rn_minus": [str(value) for value in os_mix["rn_minus"]],
            "fixed_order_first_passage_closed": False,
            "all_bond_trotter_closed": False,
            "projected_modular_locality_closed": False,
            "common_alpha_closed": False,
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE, PARENT, EUCLIDEAN_PARENT)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
