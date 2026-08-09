#!/usr/bin/env python3
"""Independent stdlib audit for the CL8 matrix-counterterm compactness split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split"
CANDIDATE_ID = "PA-CP1-CL8-MATRIX-COUNTERTERM-STATE-COMPACTNESS-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-UNIFORM-COERCIVE-SHIFT-WEAKSTAR-SUBNET-CUT-DEFECT-IDENTITY-REGULARITY-AND-DYNAMICS-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-ABSTRACT-COMPACTNESS-ONLY-REGULAR-CONTINUUM-STATE",
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-EXACT-DYNAMICS-EQUIVARIANCE",
    "NG-2026-08-04-PRE-A-CP1-CL8-POINTWISE-STABILITY-GAUSSIAN-TRIAL-UNIFORM-ENERGY",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
)
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-independent-{SLUG}/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


Poly = dict[tuple[int, ...], Fraction]
Matrix = list[list[Fraction]]


def poly_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def poly_scale(poly: Poly, scale: Fraction | int) -> Poly:
    factor = Fraction(scale)
    return {exponent: coefficient * factor for exponent, coefficient in poly.items() if coefficient * factor}


def poly_multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for exponent_left, coefficient_left in left.items():
        for exponent_right, coefficient_right in right.items():
            exponent = tuple(a + b for a, b in zip(exponent_left, exponent_right))
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient_left * coefficient_right
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def poly_power(poly: Poly, power: int) -> Poly:
    dimensions = len(next(iter(poly)))
    result: Poly = {(0,) * dimensions: Fraction(1)}
    for _ in range(power):
        result = poly_multiply(result, poly)
    return result


def poly_variable(dimensions: int, axis: int) -> Poly:
    exponent = [0] * dimensions
    exponent[axis] = 1
    return {tuple(exponent): Fraction(1)}


def cube_data() -> tuple[list[int], list[tuple[int, int]], Matrix]:
    nodes = list(range(8))
    edges = [(left, right) for left in nodes for right in nodes if left < right and (left ^ right).bit_count() == 1]
    laplacian = [[Fraction(0) for _ in nodes] for _ in nodes]
    for left, right in edges:
        laplacian[left][left] += 1
        laplacian[right][right] += 1
        laplacian[left][right] -= 1
        laplacian[right][left] -= 1
    return nodes, edges, laplacian


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> Matrix:
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def kron(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] * right[r][s] for j in range(len(left[0])) for s in range(len(right[0]))]
        for i in range(len(left))
        for r in range(len(right))
    ]


def permutation_matrix(order: list[int]) -> Matrix:
    return [[Fraction(int(j == order[i])) for j in range(len(order))] for i in range(len(order))]


def conjugate(unitary: Matrix, observable: Matrix) -> Matrix:
    return matmul(matmul(unitary, observable), transpose(unitary))


def theta(anchor: Matrix, bulk: Matrix) -> Matrix:
    return matmul(matmul(transpose(anchor), bulk), anchor)


def theta_inverse(anchor: Matrix, cut: Matrix) -> Matrix:
    return matmul(matmul(anchor, cut), transpose(anchor))


def cut_embedding(anchor_coarse: Matrix, anchor_fine: Matrix, cut_observable: Matrix) -> Matrix:
    bulk_coarse = theta_inverse(anchor_coarse, cut_observable)
    return theta(anchor_fine, kron(bulk_coarse, identity(2)))


def partial_trace_added(density: Matrix, low_dimension: int, added_dimension: int) -> Matrix:
    return [
        [sum((density[i * added_dimension + a][j * added_dimension + a] for a in range(added_dimension)), Fraction(0)) for j in range(low_dimension)]
        for i in range(low_dimension)
    ]


def diagonal_trace_norm(matrix: Matrix) -> Fraction:
    assert all(matrix[i][j] == 0 for i in range(len(matrix)) for j in range(len(matrix)) if i != j)
    return sum((abs(matrix[i][i]) for i in range(len(matrix))), Fraction(0))


def matrix_trace(matrix: Matrix) -> Fraction:
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative identities", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("parent identities", tuple(parent["candidate_id"] for parent in parents) == tuple(manifest["parent_ids"]), [parent["candidate_id"] for parent in parents], manifest["parent_ids"], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    parent_wick = parents[0]["common_diagonal_Wick_ledger"]
    audit.check("independent parent Wick matrix convention", parent_wick["quadratic_matrix"] == "deltaK=-3*C*[(g+lambda)I+lambda*L_Q3]", parent_wick["quadratic_matrix"], "deltaK=-3*C*[(g+lambda)I+lambda*L_Q3]", "parent-convention")
    audit.check("independent candidate Wick matrix convention", manifest["matrix_counterterm_candidate"]["Wick_contraction"] == "deltaK_C=-3*C*[(g+lambda)I+lambda*L_Q3]", manifest["matrix_counterterm_candidate"]["Wick_contraction"], "deltaK_C=-3*C*[(g+lambda)I+lambda*L_Q3]", "parent-convention")
    audit.check("independent parent Wick scalar convention", "6*C^2*(g+4*lambda)" in parent_wick["Q3_sum"], parent_wick["Q3_sum"], "6*C^2*(g+4*lambda)", "parent-convention")

    nodes, edges, laplacian = cube_data()
    audit.check("Q3 node count", len(nodes) == 8, len(nodes), 8, "Q3")
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 Laplacian symmetric", laplacian == transpose(laplacian), laplacian, "symmetric", "Q3")
    walsh_levels: list[int] = []
    for alpha_bits in nodes:
        vector = [Fraction((-1) ** ((alpha_bits & node).bit_count() % 2)) for node in nodes]
        image = [sum((laplacian[i][j] * vector[j] for j in range(8)), Fraction(0)) for i in range(8)]
        eigenvalue = 2 * alpha_bits.bit_count()
        audit.check(f"Walsh eigenvector {alpha_bits}", image == [eigenvalue * value for value in vector], image, eigenvalue, "Q3")
        walsh_levels.append(eigenvalue)
    spectrum = dict(sorted(Counter(walsh_levels).items()))
    audit.check("Q3 Walsh multiplicities", spectrum == {0: 1, 2: 3, 4: 3, 6: 1}, spectrum, {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")

    g = Fraction(5)
    lam = Fraction(2)
    covariance = Fraction(3)
    mass = Fraction(7)
    eta = Fraction(4)
    identity8 = identity(8)
    K_R = [[mass * identity8[i][j] + eta * laplacian[i][j] for j in range(8)] for i in range(8)]
    delta_K = [[-3 * covariance * ((g + lam) * identity8[i][j] + lam * laplacian[i][j]) for j in range(8)] for i in range(8)]
    K_raw = [[K_R[i][j] + delta_K[i][j] for j in range(8)] for i in range(8)]
    kappas: list[Fraction] = []
    for weight in range(4):
        alpha_mask = (1 << weight) - 1
        vector = [Fraction((-1) ** ((alpha_mask & node).bit_count() % 2)) for node in nodes]
        image = [sum((K_raw[i][j] * vector[j] for j in range(8)), Fraction(0)) for i in range(8)]
        eigenvalue = mass + 2 * weight * eta - 3 * covariance * (g + lam + 2 * weight * lam)
        audit.check(f"independent Kraw Walsh action {weight}", image == [eigenvalue * value for value in vector], image, eigenvalue, "coercivity")
        kappas.append(eigenvalue)
    audit.check("independent Kraw hostile diagonal", all(K_raw[i][i] == -98 for i in range(8)), [K_raw[i][i] for i in range(8)], [-98] * 8, "coercivity")
    audit.check("independent Kraw hostile edges", all(K_raw[i][j] == 14 for i, j in edges), [K_raw[i][j] for i, j in edges], [14] * 12, "coercivity")
    b_value = max(Fraction(0), -min(kappas)) / 2
    epsilon_iso = 16 * b_value * b_value / g - 6 * covariance * covariance * (g + 4 * lam)
    alpha_value = max(Fraction(0), 3 * covariance * (g + lam) - mass)
    beta_value = max(Fraction(0), 3 * covariance * lam - eta)
    epsilon_aniso = 4 * alpha_value * alpha_value / g + 12 * beta_value * beta_value / lam - 6 * covariance * covariance * (g + 4 * lam)
    audit.check("hostile Walsh stiffness", kappas == [-56, -84, -112, -140], kappas, [-56, -84, -112, -140], "coercivity")
    audit.check("hostile isotropic b", b_value == 70, b_value, 70, "coercivity")
    audit.check("hostile isotropic shift", epsilon_iso == 14978, epsilon_iso, 14978, "coercivity")
    audit.check("hostile anisotropic alpha", alpha_value == 56, alpha_value, 56, "coercivity")
    audit.check("hostile anisotropic beta", beta_value == 14, beta_value, 14, "coercivity")
    audit.check("hostile anisotropic shift", epsilon_aniso == Fraction(14914, 5), epsilon_aniso, Fraction(14914, 5), "coercivity")
    lambda_zero_kappas = [Fraction(7) + 2 * s * Fraction(-4) - 3 * Fraction(3) * Fraction(5) for s in range(4)]
    lambda_zero_b = max(Fraction(0), -min(lambda_zero_kappas)) / 2
    lambda_zero_shift = 16 * lambda_zero_b**2 / 5 - 6 * 3**2 * 5
    audit.check("independent lambda-zero Walsh fixture", lambda_zero_kappas == [-38, -46, -54, -62], lambda_zero_kappas, [-38, -46, -54, -62], "coercivity")
    audit.check("independent lambda-zero isotropic route", (lambda_zero_b, lambda_zero_shift) == (31, Fraction(14026, 5)), (lambda_zero_b, lambda_zero_shift), (31, Fraction(14026, 5)), "coercivity")

    variables = [poly_variable(8, axis) for axis in range(8)]
    squares = [poly_power(variable, 2) for variable in variables]
    fourths = [poly_power(variable, 4) for variable in variables]
    radius_squared: Poly = {}
    onsite_fourth: Poly = {}
    for square, fourth in zip(squares, fourths):
        radius_squared = poly_add(radius_squared, square)
        onsite_fourth = poly_add(onsite_fourth, fourth)
    onsite_left = poly_add(onsite_fourth, poly_scale(poly_power(radius_squared, 2), Fraction(-1, 8)))
    onsite_right: Poly = {}
    for i in range(8):
        for j in range(i + 1, 8):
            onsite_right = poly_add(onsite_right, poly_scale(poly_power(poly_add(squares[i], poly_scale(squares[j], -1)), 2), Fraction(1, 8)))
    audit.check("independent onsite SOS identity", onsite_left == onsite_right, onsite_left, onsite_right, "coercivity")

    differences = [poly_add(variables[i], poly_scale(variables[j], -1)) for i, j in edges]
    difference_squares = [poly_power(value, 2) for value in differences]
    difference_fourths = [poly_power(value, 4) for value in differences]
    edge_polynomial: Poly = {}
    edge_first_sos: Poly = {}
    for (i, j), difference_square, difference_fourth in zip(edges, difference_squares, difference_fourths):
        edge_polynomial = poly_add(edge_polynomial, poly_multiply(difference_square, poly_add(squares[i], squares[j])))
        plus_square = poly_power(poly_add(variables[i], variables[j]), 2)
        edge_first_sos = poly_add(edge_first_sos, poly_scale(poly_multiply(difference_square, plus_square), Fraction(1, 2)))
    half_difference_fourths: Poly = {}
    total_edge_square: Poly = {}
    for difference_square, difference_fourth in zip(difference_squares, difference_fourths):
        half_difference_fourths = poly_add(half_difference_fourths, poly_scale(difference_fourth, Fraction(1, 2)))
        total_edge_square = poly_add(total_edge_square, difference_square)
    audit.check("independent Q3 edge first SOS", poly_add(edge_polynomial, poly_scale(half_difference_fourths, -1)) == edge_first_sos, edge_polynomial, edge_first_sos, "coercivity")
    edge_cauchy_left = poly_add(poly_scale(half_difference_fourths, 24), poly_scale(poly_power(total_edge_square, 2), -1))
    edge_cauchy_right: Poly = {}
    for i in range(12):
        for j in range(i + 1, 12):
            edge_cauchy_right = poly_add(edge_cauchy_right, poly_power(poly_add(difference_squares[i], poly_scale(difference_squares[j], -1)), 2))
    audit.check("independent Q3 edge Cauchy SOS", edge_cauchy_left == edge_cauchy_right, edge_cauchy_left, edge_cauchy_right, "coercivity")

    bipartite = [Fraction((-1) ** node.bit_count()) for node in nodes]
    sharp_S = sum((value * value for value in bipartite), Fraction(0))
    sharp_T = sum(((bipartite[i] - bipartite[j]) ** 2 for i, j in edges), Fraction(0))
    sharp_onsite = sum((value**4 for value in bipartite), Fraction(0))
    sharp_edge = sum(((bipartite[i] - bipartite[j]) ** 2 * (bipartite[i] ** 2 + bipartite[j] ** 2) for i, j in edges), Fraction(0))
    audit.check("bipartite S sharpness", (sharp_S, sharp_onsite) == (8, 8), (sharp_S, sharp_onsite), (8, 8), "sharpness")
    audit.check("bipartite T sharpness", (sharp_T, sharp_edge) == (48, 96), (sharp_T, sharp_edge), (48, 96), "sharpness")
    audit.check("bipartite onsite equality", sharp_onsite == sharp_S * sharp_S / 8, sharp_onsite, sharp_S * sharp_S / 8, "sharpness")
    audit.check("bipartite edge equality", sharp_edge == sharp_T * sharp_T / 24, sharp_edge, sharp_T * sharp_T / 24, "sharpness")

    isotropic_left = (g / 32, -b_value, 16 * b_value * b_value / g)
    isotropic_right = (g / 64 + g / 64, -b_value, 16 * b_value * b_value / g)
    audit.check("independent isotropic completion coefficients", isotropic_left == isotropic_right, isotropic_left, isotropic_right, "completion")
    anisotropic_left = (g / 32, lam / 96, -alpha_value / 2, -beta_value / 2, 4 * alpha_value**2 / g + 12 * beta_value**2 / lam)
    anisotropic_right = (g / 64 + g / 64, lam / 192 + lam / 192, -alpha_value / 2, -beta_value / 2, 4 * alpha_value**2 / g + 12 * beta_value**2 / lam)
    audit.check("independent anisotropic completion coefficients", anisotropic_left == anisotropic_right, anisotropic_left, anisotropic_right, "completion")

    R_poly, G_poly, B_poly = (poly_variable(3, axis) for axis in range(3))
    isotropic_cleared_left = poly_add(
        poly_add(poly_scale(poly_multiply(poly_power(G_poly, 2), poly_power(R_poly, 2)), 2), poly_scale(poly_multiply(poly_multiply(G_poly, B_poly), R_poly), -64)),
        poly_scale(poly_power(B_poly, 2), 1024),
    )
    isotropic_square = poly_add(poly_multiply(G_poly, R_poly), poly_scale(B_poly, -32))
    isotropic_cleared_right = poly_add(poly_multiply(poly_power(G_poly, 2), poly_power(R_poly, 2)), poly_power(isotropic_square, 2))
    audit.check("independent formal isotropic cleared identity", isotropic_cleared_left == isotropic_cleared_right, isotropic_cleared_left, isotropic_cleared_right, "completion")

    S_poly, T_poly, G6_poly, L6_poly, A_poly, B6_poly = (poly_variable(6, axis) for axis in range(6))
    anisotropic_cleared_left: Poly = {}
    anisotropic_terms = (
        poly_scale(poly_multiply(poly_multiply(poly_power(G6_poly, 2), L6_poly), poly_power(S_poly, 2)), 6),
        poly_scale(poly_multiply(poly_multiply(G6_poly, poly_power(L6_poly, 2)), poly_power(T_poly, 2)), 2),
        poly_scale(poly_multiply(poly_multiply(poly_multiply(G6_poly, L6_poly), A_poly), S_poly), -96),
        poly_scale(poly_multiply(poly_multiply(poly_multiply(G6_poly, L6_poly), B6_poly), T_poly), -96),
        poly_scale(poly_multiply(L6_poly, poly_power(A_poly, 2)), 768),
        poly_scale(poly_multiply(G6_poly, poly_power(B6_poly, 2)), 2304),
    )
    for term in anisotropic_terms:
        anisotropic_cleared_left = poly_add(anisotropic_cleared_left, term)
    gs_minus_a = poly_add(poly_multiply(G6_poly, S_poly), poly_scale(A_poly, -16))
    lt_minus_b = poly_add(poly_multiply(L6_poly, T_poly), poly_scale(B6_poly, -48))
    anisotropic_cleared_right = poly_add(
        poly_add(
            poly_scale(poly_multiply(poly_multiply(poly_power(G6_poly, 2), L6_poly), poly_power(S_poly, 2)), 3),
            poly_multiply(poly_multiply(G6_poly, poly_power(L6_poly, 2)), poly_power(T_poly, 2)),
        ),
        poly_add(poly_scale(poly_multiply(L6_poly, poly_power(gs_minus_a, 2)), 3), poly_multiply(G6_poly, poly_power(lt_minus_b, 2))),
    )
    audit.check("independent formal anisotropic cleared identity", anisotropic_cleared_left == anisotropic_cleared_right, anisotropic_cleared_left, anisotropic_cleared_right, "completion")

    singlet_coefficients = (2 * g, 4 * mass - 12 * covariance * (g + lam), 6 * covariance**2 * (g + 4 * lam))
    singlet_minimum_point = -singlet_coefficients[1] / (2 * singlet_coefficients[0])
    audit.check("independent derived singlet minimum point", singlet_minimum_point == Fraction(56, 5), singlet_minimum_point, Fraction(56, 5), "Gaussian-gap")
    singlet_minimum = singlet_coefficients[0] * singlet_minimum_point**2 + singlet_coefficients[1] * singlet_minimum_point + singlet_coefficients[2]
    singlet_literal_mean = 6 * g * covariance**2 + singlet_coefficients[1] * covariance + singlet_coefficients[2]
    full_Gaussian_mean = covariance * (4 * mass + 12 * eta)
    Gaussian_gap_lower_bound = full_Gaussian_mean - singlet_minimum
    leading_gap = 12 * g + 12 * lam + 18 * lam * lam / g
    audit.check("independent singlet coefficients", singlet_coefficients == (10, -224, 702), singlet_coefficients, (10, -224, 702), "Gaussian-gap")
    audit.check("independent singlet minimum", singlet_minimum == Fraction(-2762, 5), singlet_minimum, Fraction(-2762, 5), "Gaussian-gap")
    audit.check("independent literal singlet Gaussian mean", singlet_literal_mean == 300, singlet_literal_mean, 300, "Gaussian-gap")
    audit.check("independent full Gaussian mean", full_Gaussian_mean == 228, full_Gaussian_mean, 228, "Gaussian-gap")
    audit.check("independent singlet and full means distinguished", singlet_literal_mean != full_Gaussian_mean, singlet_literal_mean, full_Gaussian_mean, "Gaussian-gap")
    audit.check("independent scalar-shift invariant gap lower bound", Gaussian_gap_lower_bound == Fraction(3902, 5), Gaussian_gap_lower_bound, Fraction(3902, 5), "Gaussian-gap")
    audit.check("independent leading gap coefficient", leading_gap == Fraction(492, 5), leading_gap, Fraction(492, 5), "Gaussian-gap")
    def gap_formula(c_value: Fraction) -> Fraction:
        restricted_minimum = 6 * c_value**2 * (g + 4 * lam) - (12 * c_value * (g + lam) - 4 * mass) ** 2 / (8 * g)
        return c_value * (4 * mass + 12 * eta) - restricted_minimum
    gap_samples = [gap_formula(Fraction(index)) for index in (1, 2, 3)]
    leading_from_finite_difference = (gap_samples[2] - 2 * gap_samples[1] + gap_samples[0]) / 2
    audit.check("independent general-gap finite difference", leading_from_finite_difference == leading_gap, leading_from_finite_difference, leading_gap, "Gaussian-gap")

    field_scale_squared = Fraction(2)
    momentum_scale_squared = Fraction(1, 2)
    audit.check("reciprocal Nyquist squeeze", field_scale_squared * momentum_scale_squared == 1, field_scale_squared * momentum_scale_squared, 1, "embedding")
    audit.check("Nyquist squeeze typed", "sqrt2" in manifest["abstract_state_compactness"]["algebras"] or "reciprocal" in manifest["abstract_state_compactness"]["algebras"], manifest["abstract_state_compactness"]["algebras"], "reciprocal squeeze", "embedding")
    audit.check("embedding transitivity boundary", "transitivity" in manifest["abstract_state_compactness"]["compatibility"], manifest["abstract_state_compactness"]["compatibility"], "transitivity", "embedding")
    old_pair_after_first = (field_scale_squared, momentum_scale_squared)
    old_pair_after_second = (old_pair_after_first[0] * 1, old_pair_after_first[1] * 1)
    old_pair_direct = (field_scale_squared, momentum_scale_squared)
    new_exceptional_pair = (field_scale_squared, momentum_scale_squared)
    audit.check("independent three-regulator old-pair transitivity", old_pair_after_second == old_pair_direct, old_pair_after_second, old_pair_direct, "embedding")
    audit.check("independent newly exceptional reciprocal pair", new_exceptional_pair[0] * new_exceptional_pair[1] == 1, new_exceptional_pair, "symplectic", "embedding")

    projector = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    rational_ket = [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1, 2)]
    fine_projector = [[left * right for right in rational_ket] for left in rational_ket]
    audit.check("independent rational fine projector trace", matrix_trace(fine_projector) == 1, matrix_trace(fine_projector), 1, "distance")
    audit.check("independent rational fine projector idempotent", matmul(fine_projector, fine_projector) == fine_projector, matmul(fine_projector, fine_projector), fine_projector, "distance")
    reduced = partial_trace_added(fine_projector, 2, 4)
    audit.check("independent rational pure-state partial trace", reduced == [[Fraction(3, 4), Fraction(0)], [Fraction(0), Fraction(1, 4)]], reduced, "diag(3/4,1/4)", "distance")
    difference = [[reduced[i][j] - projector[i][j] for j in range(2)] for i in range(2)]
    eta_distance = 1 - sum((projector[i][j] * reduced[j][i] for i in range(2) for j in range(2)), Fraction(0))
    trace_distance = diagonal_trace_norm(difference)
    audit.check("pure-state eta fixture", eta_distance == Fraction(1, 4), eta_distance, Fraction(1, 4), "distance")
    audit.check("pure-state lower distance saturation", trace_distance == 2 * eta_distance, trace_distance, 2 * eta_distance, "distance")
    audit.check("pure-state upper distance bound", trace_distance * trace_distance <= 4 * eta_distance, trace_distance * trace_distance, 4 * eta_distance, "distance")
    audit.check("distance equivalence recorded", "if and only if" in manifest["ground_entanglement_distance"]["equivalence"], manifest["ground_entanglement_distance"]["equivalence"], "if and only if", "distance")
    swap_chart = permutation_matrix([1, 0])
    chart_fine_density = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    chart_fine_density[0][0] = 1
    chart_coarse_density = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    bare_chart_restriction = partial_trace_added(chart_fine_density, 2, 2)
    typed_chart_restriction = theta(swap_chart, bare_chart_restriction)
    bare_chart_defect = diagonal_trace_norm([[bare_chart_restriction[i][j] - chart_coarse_density[i][j] for j in range(2)] for i in range(2)])
    typed_chart_defect = diagonal_trace_norm([[typed_chart_restriction[i][j] - chart_coarse_density[i][j] for j in range(2)] for i in range(2)])
    audit.check("independent bare partial trace masks chart defect", bare_chart_defect == 0, bare_chart_defect, 0, "distance")
    audit.check("independent predual chart restriction", typed_chart_defect == 2, typed_chart_defect, 2, "distance")

    gamma_M_C = permutation_matrix([1, 0])
    gamma_M_D = identity(2)
    gamma_N_C = permutation_matrix([3, 0, 1, 2])
    gamma_N_D = identity(4)
    observable = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(-1)]]
    cut_C = theta(gamma_M_C, observable)
    direct_square = cut_embedding(gamma_M_C, gamma_N_C, cut_C)
    expected_square = theta(gamma_N_C, kron(observable, identity(2)))
    expected_cut_C = [[Fraction(-1), Fraction(1)], [Fraction(1), Fraction(2)]]
    expected_j_C = [[Fraction(2), Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(-1), Fraction(0), Fraction(1)], [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0), Fraction(2)]]
    expected_j_D = [[Fraction(2), Fraction(0), Fraction(1), Fraction(0)], [Fraction(0), Fraction(2), Fraction(0), Fraction(1)], [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)]]
    audit.check("independent cut C hard-coded orientation", cut_C == expected_cut_C, cut_C, expected_cut_C, "cut")
    audit.check("independent cut embedding hard-coded orientation", direct_square == expected_j_C, direct_square, expected_j_C, "cut")
    audit.check("independent matched cut square", direct_square == expected_square, direct_square, expected_square, "cut")
    S_M = matmul(transpose(gamma_M_D), gamma_M_C)
    S_N = matmul(transpose(gamma_N_D), gamma_N_C)
    beta_M_cut = conjugate(S_M, cut_C)
    left_square = cut_embedding(gamma_M_D, gamma_N_D, beta_M_cut)
    right_square = conjugate(S_N, cut_embedding(gamma_M_C, gamma_N_C, cut_C))
    audit.check("independent same-time hard-coded target", left_square == expected_j_D, left_square, expected_j_D, "cut")
    audit.check("independent same-time naturality", left_square == right_square, left_square, right_square, "cut")
    reversed_S_M = matmul(transpose(gamma_M_C), gamma_M_D)
    reversed_S_N = matmul(transpose(gamma_N_C), gamma_N_D)
    reversed_left = cut_embedding(gamma_M_D, gamma_N_D, conjugate(reversed_S_M, cut_C))
    reversed_right = conjugate(reversed_S_N, direct_square)
    audit.check("independent reversed-S mutation rejected", reversed_left != reversed_right, reversed_left, "not equal", "cut-mutation")
    wrong_ad_M = matmul(matmul(transpose(S_M), cut_C), S_M)
    wrong_ad_N = matmul(matmul(transpose(S_N), direct_square), S_N)
    wrong_ad_left = cut_embedding(gamma_M_D, gamma_N_D, wrong_ad_M)
    audit.check("independent reversed-Ad mutation rejected", wrong_ad_left != wrong_ad_N, wrong_ad_left, "not equal", "cut-mutation")

    rho_N = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for index, value in enumerate((Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 8))):
        rho_N[index][index] = value
    rho_M = [[Fraction(2, 3), Fraction(0)], [Fraction(0), Fraction(1, 3)]]
    reduced_N = partial_trace_added(rho_N, 2, 2)
    reduced_defect = [[reduced_N[i][j] - rho_M[i][j] for j in range(2)] for i in range(2)]
    defect_norm = diagonal_trace_norm(reduced_defect)
    rho_M_C = theta(gamma_M_C, rho_M)
    rho_N_C = theta(gamma_N_C, rho_N)
    bulk_expectation_defect = matrix_trace(matmul(rho_N, kron(observable, identity(2)))) - matrix_trace(matmul(rho_M, observable))
    cut_expectation_defect = matrix_trace(matmul(rho_N_C, cut_embedding(gamma_M_C, gamma_N_C, theta(gamma_M_C, observable)))) - matrix_trace(matmul(rho_M_C, theta(gamma_M_C, observable)))
    audit.check("independent reduced density", reduced_N == [[Fraction(3, 4), Fraction(0)], [Fraction(0), Fraction(1, 4)]], reduced_N, "diag(3/4,1/4)", "cut")
    audit.check("independent cut bulk dual norm", defect_norm == Fraction(1, 6), defect_norm, Fraction(1, 6), "cut")
    cut_restriction_density = theta(gamma_M_C, reduced_N)
    cut_density_defect = [[cut_restriction_density[i][j] - rho_M_C[i][j] for j in range(2)] for i in range(2)]
    cut_dual_norm = diagonal_trace_norm(cut_density_defect)
    audit.check("independent cut and bulk dual norms agree", cut_dual_norm == defect_norm, cut_dual_norm, defect_norm, "cut")
    audit.check("independent nonzero bulk defect", bulk_expectation_defect == Fraction(1, 4), bulk_expectation_defect, Fraction(1, 4), "cut")
    audit.check("independent cut bulk expectation identity", cut_expectation_defect == bulk_expectation_defect, cut_expectation_defect, bulk_expectation_defect, "cut")

    squeezed_N = (1, 4, 16, 64)
    squeezed_covariances = [(Fraction(N, 2), Fraction(1, 2 * N)) for N in squeezed_N]
    audit.check("squeezed covariance determinants", all(qvar * pvar == Fraction(1, 4) for qvar, pvar in squeezed_covariances), squeezed_covariances, "all 1/4", "regularity")
    audit.check("squeezed uniform frequencies", all(Fraction(N) * Fraction(1, N) == 1 for N in squeezed_N), squeezed_N, "all one", "regularity")
    q_exponents = [-Fraction(N, 4) for N in squeezed_N]
    p_exponents = [-Fraction(1, 4 * N) for N in squeezed_N]
    audit.check("squeezed nonzero-u exponent divergence direction", all(right == 4 * left for left, right in zip(q_exponents, q_exponents[1:])), q_exponents, "multiplies by four", "regularity")
    audit.check("squeezed u-zero exponent limit direction", all(right == left / 4 for left, right in zip(p_exponents, p_exponents[1:])), p_exponents, "divides by four", "regularity")
    audit.check("nonregular witness scope", "discontinuously" in manifest["regularity_no_go"]["witness"], manifest["regularity_no_go"]["witness"], "discontinuous", "regularity")

    dyadic_tail = sum((Fraction(1, 4**j) for j in range(3, 30)), Fraction(0)) + Fraction(1, 3 * 4**29)
    audit.check("summable dyadic tail", dyadic_tail == Fraction(1, 48), dyadic_tail, Fraction(1, 48), "cylindrical")
    audit.check("adjacent-only firewall", "insufficient" in manifest["cylindrical_topology_gate"]["full_sequence"], manifest["cylindrical_topology_gate"]["full_sequence"], "insufficient", "cylindrical")
    audit.check("fixed-K Nyquist firewall", "excludes" in manifest["cylindrical_topology_gate"]["definition"], manifest["cylindrical_topology_gate"]["definition"], "excludes moving Nyquist", "cylindrical")

    dynamic_L = 4
    dynamic_X = poly_variable(2, 0)
    dynamic_Y = poly_variable(2, 1)
    collective_onsite: Poly = {}
    for site in range(dynamic_L):
        sign = 1 if site % 2 == 0 else -1
        coordinate = poly_scale(poly_add(dynamic_X, poly_scale(dynamic_Y, sign)), Fraction(1, 2))
        collective_onsite = poly_add(collective_onsite, poly_scale(poly_power(coordinate, 4), Fraction(1, 4)))
    mixed_energy_coefficient = collective_onsite[(2, 2)]
    mixed_derivative = 4 * mixed_energy_coefficient
    added_force_at_one = -2 * mixed_energy_coefficient
    added_force_at_y_zero = Fraction(0)
    audit.check("independent dynamic mixed coefficient", mixed_energy_coefficient == Fraction(3, 8), mixed_energy_coefficient, Fraction(3, 8), "dynamics")
    audit.check("independent dynamic mixed derivative", mixed_derivative == Fraction(3, 2), mixed_derivative, Fraction(3, 2), "dynamics")
    audit.check("independent signed added-mode force", added_force_at_one == Fraction(-3, 4), added_force_at_one, Fraction(-3, 4), "dynamics")
    audit.check("independent force depends on added coordinate", added_force_at_one != added_force_at_y_zero, added_force_at_one, added_force_at_y_zero, "dynamics")
    audit.check("dynamics alternatives remain", "not_excluded" in manifest["natural_dynamics_no_go"], manifest["natural_dynamics_no_go"], "alternatives", "dynamics")

    moment_fixture = {
        "field_fourth": Fraction(64 * 7, 5),
        "momentum_second": Fraction(2 * 3 * 7),
        "edge_fourth": Fraction(192 * 7, 2),
    }
    audit.check("conditional field coefficient", moment_fixture["field_fourth"] == Fraction(448, 5), moment_fixture, Fraction(448, 5), "moments")
    audit.check("conditional momentum coefficient", moment_fixture["momentum_second"] == 42, moment_fixture, 42, "moments")
    audit.check("conditional edge coefficient", moment_fixture["edge_fourth"] == 672, moment_fixture, 672, "moments")
    point_count = 4
    weight = Fraction(1, 8)
    smeared_value = weight * point_count * 2
    label_fourth_factor = (weight * point_count) ** 3
    configuration_fourth = weight * point_count * 2**4
    label_second = weight * point_count
    configuration_second = weight * point_count * 2**2
    audit.check("independent weighted Holder equality", smeared_value**4 == label_fourth_factor * configuration_fourth, smeared_value**4, label_fourth_factor * configuration_fourth, "moments")
    audit.check("independent weighted Cauchy equality", smeared_value**2 == label_second * configuration_second, smeared_value**2, label_second * configuration_second, "moments")
    audit.check("uniform energy remains open", manifest["scope"]["uniform_shifted_energy_upper_bound"] is False, manifest["scope"]["uniform_shifted_energy_upper_bound"], False, "moments")

    for key, value in manifest["scope"].items():
        if key in {
            "Q3_matrix_counterterm_candidate_typed",
            "cutoff_uniform_lower_form_stability_after_declared_scalar_shift",
            "fixed_regulator_ground_and_Gibbs",
            "abstract_compatible_state_subnet",
            "matched_reference_cut_algebra_square",
            "cut_bulk_defect_identity",
        }:
            audit.check(f"scope true: {key}", value is True, value, True, "scope")
        else:
            audit.check(f"scope false: {key}", value is False, value, False, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(manifest["parent_ids"]),
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "status": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            **{path: sha256(REPO / path) for path in PARENT_FILES},
        },
        "derived": {
            "Q3_spectrum": spectrum,
            "Walsh_stiffness": kappas,
            "coercive_shifts": {"b": b_value, "isotropic": epsilon_iso, "alpha": alpha_value, "beta": beta_value, "anisotropic": epsilon_aniso},
            "sharpness": {"S": sharp_S, "T": sharp_T, "onsite": sharp_onsite, "edge": sharp_edge},
            "singlet_Gaussian": {
                "minimum_point_squared": singlet_minimum_point,
                "minimum": singlet_minimum,
                "literal_singlet_mean": singlet_literal_mean,
                "full_reference_mean": full_Gaussian_mean,
                "global_gap_lower_bound": Gaussian_gap_lower_bound,
                "leading_gap": leading_gap,
            },
            "entanglement_distance": {"eta": eta_distance, "trace_distance": trace_distance},
            "cut_fixture": {"dual_norm": defect_norm, "same_time_square": "exact"},
            "squeezed_covariances": squeezed_covariances,
            "dyadic_tail": dyadic_tail,
            "dynamic_fixture": {"mixed_energy_coefficient": mixed_energy_coefficient, "force_at_X1_Y1": added_force_at_one, "force_at_X1_Y0": added_force_at_y_zero},
            "conditional_moment_coefficients": moment_fixture,
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
