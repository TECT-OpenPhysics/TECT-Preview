#!/usr/bin/env python3
"""Independent stdlib verifier for the CL8 time-local RP/FK route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split"
CANDIDATE_ID = "PA-CP1-CL8-TIME-LOCAL-RP-FEYNMAN-KAC-BRIDGE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-FIXED-REGULATOR-EXACT-HEAT-TRANSFER-REFLECTION-POSITIVITY-FEYNMAN-KAC-AND-STRANG-LIMIT-WITH-EXACT-SLICE-AND-CONE-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-STRANG-ONE-SLICE-EXACT-HAMILTONIAN-SEMIGROUP",
    "NG-2026-08-04-PRE-A-CP1-CL8-EUCLIDEAN-HEAT-SUPPORT-PHYSICAL-LIGHT-CONE",
)
EXPLORATION_ID = "EXP-000768"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_STEM = SLUG.replace("-", "_")
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"

# Explicit self-test oracles only.
TEST_ORACLE_STRANG_JET_3 = {
    (12, 0, 3): Fraction(-1, 6),
    (6, 1, 2): Fraction(10),
    (0, 2, 1): Fraction(-6),
}
TEST_ORACLE_EXACT_JET_3 = {
    (12, 0, 3): Fraction(-1, 6),
    (6, 1, 2): Fraction(34, 3),
    (0, 2, 1): Fraction(-4),
}
TEST_ORACLE_DEFECT_JET_3 = {
    (6, 1, 2): Fraction(-4, 3),
    (0, 2, 1): Fraction(-2),
}
TEST_ORACLE_RP_Z = 189297938
TEST_ORACLE_SITE_NUMERATOR = 3556553674
TEST_ORACLE_LINK_NUMERATOR = 94067688

Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def clean(polynomial: Polynomial) -> Polynomial:
    return {key: value for key, value in polynomial.items() if value}


def add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return clean(result)


def scale(polynomial: Polynomial, coefficient: Fraction | int) -> Polynomial:
    factor = Fraction(coefficient)
    return clean({exponent: factor * value for exponent, value in polynomial.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(left_exponent, right_exponent))
            result[exponent] = result.get(exponent, Fraction(0)) + left_coefficient * right_coefficient
    return clean(result)


def power(polynomial: Polynomial, degree: int) -> Polynomial:
    dimension = len(next(iter(polynomial)))
    result: Polynomial = {(0,) * dimension: Fraction(1)}
    for _ in range(degree):
        result = multiply(result, polynomial)
    return result


def differentiate(polynomial: Polynomial, variable: int, order: int = 1) -> Polynomial:
    result = polynomial
    for _ in range(order):
        derivative: Polynomial = {}
        for exponent, coefficient in result.items():
            if exponent[variable] == 0:
                continue
            new_exponent = list(exponent)
            derivative_coefficient = coefficient * new_exponent[variable]
            new_exponent[variable] -= 1
            derivative[tuple(new_exponent)] = derivative.get(tuple(new_exponent), Fraction(0)) + derivative_coefficient
        result = clean(derivative)
    return result


def monomial(dimension: int, variable: int, degree: int, coefficient: Fraction | int = 1) -> Polynomial:
    exponent = [0] * dimension
    exponent[variable] = degree
    return {tuple(exponent): Fraction(coefficient)}


def compose_jet(operator: Callable[[Polynomial], Polynomial], incoming: list[Polynomial], order: int) -> list[Polynomial]:
    result: list[Polynomial] = [{} for _ in range(order + 1)]
    factorial = 1
    for source_degree, polynomial in enumerate(incoming):
        current = polynomial
        factorial = 1
        for added_degree in range(order - source_degree + 1):
            if added_degree:
                current = operator(current)
                factorial *= added_degree
            result[source_degree + added_degree] = add(result[source_degree + added_degree], scale(current, Fraction(1, factorial)))
    return result


def matrix_transpose(matrix: list[list[int | Fraction]]) -> list[list[Fraction]]:
    return [[Fraction(matrix[row][column]) for row in range(len(matrix))] for column in range(len(matrix[0]))]


def matrix_multiply(left: list[list[int | Fraction]], right: list[list[int | Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((Fraction(left[row][middle]) * Fraction(right[middle][column]) for middle in range(len(right))), Fraction(0)) for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def matrix_power(matrix: list[list[int | Fraction]], degree: int) -> list[list[Fraction]]:
    size = len(matrix)
    result = [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]
    for _ in range(degree):
        result = matrix_multiply(result, matrix)
    return result


def matrix_trace(matrix: list[list[int | Fraction]]) -> Fraction:
    return sum((Fraction(matrix[index][index]) for index in range(len(matrix))), Fraction(0))


def determinant3(matrix: list[list[int | Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return Fraction(a) * (Fraction(e) * Fraction(i) - Fraction(f) * Fraction(h)) - Fraction(b) * (Fraction(d) * Fraction(i) - Fraction(f) * Fraction(g)) + Fraction(c) * (Fraction(d) * Fraction(h) - Fraction(e) * Fraction(g))


def gram(factor: list[list[int | Fraction]]) -> list[list[Fraction]]:
    return matrix_multiply(matrix_transpose(factor), factor)


def quadratic(matrix: list[list[int | Fraction]], vector: list[int | Fraction]) -> Fraction:
    return sum((Fraction(vector[row]) * Fraction(matrix[row][column]) * Fraction(vector[column]) for row in range(len(vector)) for column in range(len(vector))), Fraction(0))


def serialize_polynomial(polynomial: Polynomial) -> dict[str, str]:
    return {",".join(map(str, exponent)): str(coefficient) for exponent, coefficient in sorted(polynomial.items())}


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    # Sparse-polynomial epsilon jet with variables (x, kappa, gamma).
    variable_count = 3
    one: Polynomial = {(0, 0, 0): Fraction(1)}
    zero: Polynomial = {}
    x = monomial(variable_count, 0, 1)
    kappa = monomial(variable_count, 1, 1)
    gamma = monomial(variable_count, 2, 1)
    potential = multiply(gamma, power(x, 4))

    def a_operator(polynomial: Polynomial) -> Polynomial:
        return scale(multiply(potential, polynomial), Fraction(-1, 2))

    def b_operator(polynomial: Polynomial) -> Polynomial:
        return multiply(kappa, differentiate(polynomial, 0, 2))

    def exact_operator(polynomial: Polynomial) -> Polynomial:
        return add(b_operator(polynomial), scale(multiply(potential, polynomial), -1))

    seed = [one, zero, zero, zero]
    strang = compose_jet(a_operator, compose_jet(b_operator, compose_jet(a_operator, seed, 3), 3), 3)
    exact = compose_jet(exact_operator, seed, 3)
    for degree in range(3):
        audit.check(f"independent jets agree epsilon^{degree}", strang[degree] == exact[degree], serialize_polynomial(strang[degree]), serialize_polynomial(exact[degree]), "jet")
    audit.check("Strang jet oracle", strang[3] == TEST_ORACLE_STRANG_JET_3, serialize_polynomial(strang[3]), serialize_polynomial(TEST_ORACLE_STRANG_JET_3), "jet")
    audit.check("exact jet oracle", exact[3] == TEST_ORACLE_EXACT_JET_3, serialize_polynomial(exact[3]), serialize_polynomial(TEST_ORACLE_EXACT_JET_3), "jet")
    defect = add(strang[3], scale(exact[3], -1))
    audit.check("defect jet oracle", defect == TEST_ORACLE_DEFECT_JET_3, serialize_polynomial(defect), serialize_polynomial(TEST_ORACLE_DEFECT_JET_3), "jet")
    gradient_square = power(differentiate(potential, 0), 2)
    fourth_derivative = differentiate(potential, 0, 4)
    closed_defect = add(scale(multiply(kappa, gradient_square), Fraction(-1, 12)), scale(multiply(power(kappa, 2), fourth_derivative), Fraction(-1, 12)))
    audit.check("closed defect reconstruction", defect == closed_defect, serialize_polynomial(defect), serialize_polynomial(closed_defect), "jet")
    origin_defect = {exponent: coefficient for exponent, coefficient in defect.items() if exponent[0] == 0}
    audit.check("origin defect coefficient", origin_defect == {(0, 2, 1): Fraction(-2)}, serialize_polynomial(origin_defect), "-2 gamma kappa^2", "jet")
    audit.check("plateau germ sentinel", b_operator(one) == {}, serialize_polynomial(b_operator(one)), "0", "jet")
    audit.check("heat sign sentinel", b_operator(power(x, 2)) == {(0, 1, 0): Fraction(2)}, serialize_polynomial(b_operator(power(x, 2))), "2 kappa", "jet")

    # Actual Q3 bi-Laplacian, independently in two variables.
    x2 = monomial(2, 0, 1)
    y2 = monomial(2, 1, 1)
    edge = multiply(power(add(x2, scale(y2, -1)), 2), add(power(x2, 2), power(y2, 2)))

    def laplacian2(polynomial: Polynomial) -> Polynomial:
        return add(differentiate(polynomial, 0, 2), differentiate(polynomial, 1, 2))

    self_bilaplacian = laplacian2(laplacian2(power(x2, 4))).get((0, 0), Fraction(0))
    edge_bilaplacian = laplacian2(laplacian2(edge)).get((0, 0), Fraction(0))
    audit.check("self quartic raw bi-Laplacian", self_bilaplacian == 24, self_bilaplacian, 24, "actual_CL8")
    audit.check("Q3 edge raw bi-Laplacian", edge_bilaplacian == 64, edge_bilaplacian, 64, "actual_CL8")
    self_weighted = self_bilaplacian / 4
    edge_weighted = edge_bilaplacian / 4
    audit.check("self quartic weighted coefficient", self_weighted == 6, self_weighted, 6, "actual_CL8")
    audit.check("Q3 edge weighted coefficient", edge_weighted == 16, edge_weighted, 16, "actual_CL8")
    q3_species, q3_edges = 8, 12
    total_g = q3_species * self_weighted
    total_lambda = q3_edges * edge_weighted
    audit.check("Q3 per-node g coefficient", total_g == 48, total_g, 48, "actual_CL8")
    audit.check("Q3 per-node lambda coefficient", total_lambda == 192, total_lambda, 192, "actual_CL8")
    sample_w, sample_m, sample_g, sample_lambda, sample_kappa = Fraction(3, 7), 5, Fraction(11, 3), Fraction(2, 5), Fraction(7, 4)
    actual_bilaplacian = sample_w * sample_m * (total_g * sample_g + total_lambda * sample_lambda)
    actual_defect = -sample_kappa**2 * actual_bilaplacian / 12
    audit.check("actual CL8 defect negative fixture", actual_defect < 0, actual_defect, "<0", "actual_CL8")
    audit.check("actual CL8 defect factor", actual_defect == -4 * sample_kappa**2 * sample_w * sample_m * (sample_g + 4 * sample_lambda), actual_defect, -4 * sample_kappa**2 * sample_w * sample_m * (sample_g + 4 * sample_lambda), "actual_CL8")

    # A deliberately different exact RP fixture: K=R^T R.
    factor = [[1, 2, 1], [2, 1, 3], [1, 1, 2]]
    transfer = gram(factor)
    audit.check("independent transfer Gram", transfer == [[Fraction(6), Fraction(5), Fraction(9)], [Fraction(5), Fraction(6), Fraction(7)], [Fraction(9), Fraction(7), Fraction(14)]], transfer, "R^T R", "RP")
    audit.check("independent transfer symmetric", transfer == matrix_transpose(transfer), transfer, "symmetric", "RP")
    audit.check("independent transfer entries positive", all(value > 0 for row in transfer for value in row), transfer, ">0", "RP")
    leading_minors = (transfer[0][0], transfer[0][0] * transfer[1][1] - transfer[0][1] * transfer[1][0], determinant3(transfer))
    audit.check("independent transfer leading minors", leading_minors == (6, 11, 4), leading_minors, (6, 11, 4), "RP")
    paths6 = list(itertools.product(range(3), repeat=6))
    partition_path = sum((Fraction(transfer[path[index]][path[(index + 1) % 6]]) for path in paths6 for index in ()), Fraction(0))
    # Recompute without any matrix helper to retain an independent path sum.
    partition_path = sum((
        Fraction(transfer[path[0]][path[1]]) * transfer[path[1]][path[2]] * transfer[path[2]][path[3]]
        * transfer[path[3]][path[4]] * transfer[path[4]][path[5]] * transfer[path[5]][path[0]]
        for path in paths6
    ), Fraction(0))
    partition_trace = matrix_trace(matrix_power(transfer, 6))
    audit.check("six-ring path equals trace", partition_path == partition_trace, partition_path, partition_trace, "RP")
    audit.check("six-ring partition oracle", partition_trace == TEST_ORACLE_RP_Z, partition_trace, TEST_ORACLE_RP_Z, "RP")

    site_paths = list(itertools.product(range(3), repeat=4))

    def site_weight(path: tuple[int, int, int, int]) -> Fraction:
        return Fraction(transfer[path[0]][path[1]]) * transfer[path[1]][path[2]] * transfer[path[2]][path[3]]

    def site_function(path: tuple[int, int, int, int]) -> int:
        return 1 + 2 * path[0] - path[1] + 3 * path[2] - 2 * path[3]

    site_direct = Fraction(0)
    for left in site_paths:
        for right in site_paths:
            if left[0] == right[0] and left[3] == right[3]:
                site_direct += site_function(left) * site_weight(left) * site_weight(right) * site_function(right)
    site_factor = Fraction(0)
    for endpoint0, endpoint3 in itertools.product(range(3), repeat=2):
        amplitude = sum((site_weight(path) * site_function(path) for path in site_paths if path[0] == endpoint0 and path[3] == endpoint3), Fraction(0))
        site_factor += amplitude * amplitude
    audit.check("site direct Gram factor", site_direct == site_factor, site_direct, site_factor, "RP")
    audit.check("site numerator oracle", site_direct == TEST_ORACLE_SITE_NUMERATOR, site_direct, TEST_ORACLE_SITE_NUMERATOR, "RP")
    audit.check("site numerator positive", site_direct > 0, site_direct, ">0", "RP")

    link_paths = list(itertools.product(range(3), repeat=3))

    def link_weight(path: tuple[int, int, int]) -> Fraction:
        return Fraction(transfer[path[0]][path[1]]) * transfer[path[1]][path[2]]

    def link_function(path: tuple[int, int, int]) -> int:
        return 2 - path[0] + 2 * path[1] - 3 * path[2]

    link_direct = Fraction(0)
    for left in link_paths:
        for right in link_paths:
            link_direct += link_function(left) * link_weight(left) * transfer[left[0]][right[0]] * transfer[left[2]][right[2]] * link_weight(right) * link_function(right)
    link_factor = Fraction(0)
    for z0, z2 in itertools.product(range(3), repeat=2):
        amplitude = sum((Fraction(factor[z0][path[0]]) * link_weight(path) * factor[z2][path[2]] * link_function(path) for path in link_paths), Fraction(0))
        link_factor += amplitude * amplitude
    audit.check("link direct Gram factor", link_direct == link_factor, link_direct, link_factor, "RP")
    audit.check("link numerator oracle", link_direct == TEST_ORACLE_LINK_NUMERATOR, link_direct, TEST_ORACLE_LINK_NUMERATOR, "RP")
    audit.check("link numerator positive", link_direct > 0, link_direct, ">0", "RP")

    entrywise_control = [[2, 4, 1], [4, 2, 1], [1, 1, 3]]
    audit.check("entrywise positivity not operator positivity", quadratic(entrywise_control, [1, -1, 0]) == -4, quadratic(entrywise_control, [1, -1, 0]), -4, "RP")

    # Exact rational coefficient and ordering sentinels.
    a_value, chi_value, hbar_value, delta_value = Fraction(10), Fraction(3), Fraction(7), Fraction(11)
    w_value = a_value / 8
    mu_value = chi_value * w_value
    kappa_value = hbar_value**2 / (2 * mu_value)
    epsilon_value = delta_value / hbar_value
    physical_link = 1 / (4 * kappa_value * epsilon_value)
    audit.check("rational kappa coefficient", kappa_value == 4 * hbar_value**2 / (a_value * chi_value), kappa_value, 4 * hbar_value**2 / (a_value * chi_value), "coefficients")
    audit.check("rational physical link coefficient", physical_link == a_value * chi_value / (16 * hbar_value * delta_value), physical_link, a_value * chi_value / (16 * hbar_value * delta_value), "coefficients")
    audit.check("Brownian velocity divergence ledger", "2d kappa_a/epsilon" in manifest["canonical_Feynman_Kac_bridge"]["momentum_boundary"], manifest["canonical_Feynman_Kac_bridge"]["momentum_boundary"], "2d kappa_a/epsilon", "coefficients")

    endpoint = [[Fraction(2, 3), 0], [0, Fraction(3, 5)]]
    heat_half = [[Fraction(1, 2), Fraction(1, 7)], [Fraction(1, 7), Fraction(3, 4)]]
    potential_order = matrix_multiply(matrix_multiply(endpoint, matrix_power(heat_half, 2)), endpoint)
    kinetic_order = matrix_multiply(matrix_multiply(heat_half, matrix_power(endpoint, 2)), heat_half)
    audit.check("independent Strang ordering differs", potential_order != kinetic_order, potential_order, kinetic_order, "ordering")
    for degree in range(1, 5):
        audit.check(f"independent cyclic trace N={degree}", matrix_trace(matrix_power(potential_order, degree)) == matrix_trace(matrix_power(kinetic_order, degree)), matrix_trace(matrix_power(potential_order, degree)), matrix_trace(matrix_power(kinetic_order, degree)), "ordering")
    gram_order = gram(matrix_multiply(heat_half, endpoint))
    audit.check("independent Strang Gram orientation", potential_order == gram_order, potential_order, gram_order, "ordering")
    audit.check("exact and Strang link splits distinct", "T_epsilon=T_(epsilon/2)^*T_(epsilon/2)" in manifest["periodic_path_and_reflection_positivity"]["link_reflection"] and "S_epsilon=B_epsilon^*B_epsilon" in manifest["symmetric_time_slice"]["link_Gram_factor"], "two factorizations", "distinct and present", "ordering")

    gate = manifest["gate_resolution"]
    audit.check("exact closed gate tuple", len(gate["closed_subgates"]) == 5, gate["closed_subgates"], 5, "gate")
    audit.check("exact refuted gate tuple", len(gate["refuted_subgates"]) == 2, gate["refuted_subgates"], 2, "gate")
    audit.check("exact open gate tuple", len(gate["open_subgates"]) == 7, gate["open_subgates"], 7, "gate")
    audit.check("next gate retained", gate["next_gate"] == "PA-CP1-CL8-REGULATOR-COMPATIBLE-RP-FEYNMAN-KAC-STATE-AND-WEYL-LIMIT", gate["next_gate"], "PA-CP1-CL8-REGULATOR-COMPATIBLE-RP-FEYNMAN-KAC-STATE-AND-WEYL-LIMIT", "gate")

    true_scope = {
        "fixed_regulator_exact_heat_transfer",
        "fixed_regulator_Feynman_Kac_kernel",
        "fixed_regulator_site_reflection_positive",
        "fixed_regulator_link_reflection_positive",
        "fixed_regulator_configuration_Gibbs_bridge",
        "fixed_regulator_symmetric_slice_reflection_positive",
        "fixed_regulator_symmetric_product_trace_norm_limit",
        "fixed_regulator_ground_state_Doob_Markov_interface",
    }
    for key, value in manifest["scope"].items():
        expected = key in true_scope
        audit.check(f"scope {key}", value is expected, value, expected, "scope")
    audit.check("all scope booleans", all(isinstance(value, bool) for value in manifest["scope"].values()), manifest["scope"], "booleans", "scope")
    audit.check("C6 tier", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    from_imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    dynamic = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile"}}
    audit.check("stdlib import firewall", not ({"sympy", "numpy", "scipy", PRIMARY_STEM} & (imports | from_imports)), sorted(imports | from_imports), "no project/numeric primary imports", "independence")
    audit.check("dynamic execution firewall", not dynamic and "runpy" not in imports and "importlib" not in imports, {"dynamic": sorted(dynamic), "imports": sorted(imports)}, "none", "independence")
    audit.check("certificate actual CL8 witness", "48wM(g+4\\lambda)>0" in certificate, "actual CL8 witness", "present", "source")
    audit.check("certificate aligned RP", "lattice-preserving dihedral reflection axis" in certificate, "aligned RP", "present", "source")
    audit.check("ASCII package", all(ord(character) < 128 for path in (MANIFEST, CERTIFICATE, SCRIPT) for character in path.read_text(encoding="utf-8")), "ASCII", "clean", "hygiene")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": gate["status"],
        "next_gate": gate["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {
            "quartic_jet": {
                "strang": [serialize_polynomial(polynomial) for polynomial in strang],
                "exact": [serialize_polynomial(polynomial) for polynomial in exact],
                "defect": serialize_polynomial(defect),
            },
            "actual_CL8": {
                "self_raw_bilaplacian": str(self_bilaplacian),
                "edge_raw_bilaplacian": str(edge_bilaplacian),
                "per_node_g_coefficient": str(total_g),
                "per_node_lambda_coefficient": str(total_lambda),
                "sample_defect": str(actual_defect),
            },
            "RP": {
                "factor": factor,
                "transfer": [[str(value) for value in row] for row in transfer],
                "Z": str(partition_trace),
                "site_numerator": str(site_direct),
                "link_numerator": str(link_direct),
            },
            "coefficient_fixture": {"w": str(w_value), "kappa": str(kappa_value), "physical_link": str(physical_link)},
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
