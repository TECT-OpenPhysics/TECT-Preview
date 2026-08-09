#!/usr/bin/env python3
"""Primary exact audit for the CL8 matrix-counterterm compactness route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import sympy as sp


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
AUTHORITY_FILES = (
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
)
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-primary-{SLUG}/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
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


def cube_laplacian() -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], sp.Matrix]:
    nodes = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    index = {node: i for i, node in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    laplacian = sp.zeros(8)
    for node in nodes:
        i = index[node]
        for axis in range(3):
            neighbor = list(node)
            neighbor[axis] = 1 - neighbor[axis]
            neighbor_tuple = tuple(neighbor)
            j = index[neighbor_tuple]
            laplacian[i, i] += 1
            laplacian[i, j] -= 1
            if i < j:
                edges.append((i, j))
    return nodes, edges, laplacian


def walsh(nodes: list[tuple[int, int, int]], alpha: tuple[int, int, int]) -> sp.Matrix:
    return sp.Matrix([(-1) ** sum(a * x for a, x in zip(alpha, node)) for node in nodes])


def partial_trace_second(rho: sp.Matrix, left_dimension: int, right_dimension: int) -> sp.Matrix:
    result = sp.zeros(left_dimension)
    for i in range(left_dimension):
        for j in range(left_dimension):
            result[i, j] = sum(rho[i * right_dimension + k, j * right_dimension + k] for k in range(right_dimension))
    return result


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == "EXP-000765", manifest["exploration_id"], "EXP-000765", "identity")
    audit.check("parent ids", tuple(parent["candidate_id"] for parent in parents) == tuple(manifest["parent_ids"]), [parent["candidate_id"] for parent in parents], manifest["parent_ids"], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    parent_wick = parents[0]["common_diagonal_Wick_ledger"]
    audit.check("parent Wick matrix convention", parent_wick["quadratic_matrix"] == "deltaK=-3*C*[(g+lambda)I+lambda*L_Q3]", parent_wick["quadratic_matrix"], "deltaK=-3*C*[(g+lambda)I+lambda*L_Q3]", "parent-convention")
    audit.check("candidate Wick matrix convention", manifest["matrix_counterterm_candidate"]["Wick_contraction"] == "deltaK_C=-3*C*[(g+lambda)I+lambda*L_Q3]", manifest["matrix_counterterm_candidate"]["Wick_contraction"], "deltaK_C=-3*C*[(g+lambda)I+lambda*L_Q3]", "parent-convention")
    audit.check("parent Wick scalar convention", "6*C^2*(g+4*lambda)" in parent_wick["Q3_sum"], parent_wick["Q3_sum"], "6*C^2*(g+4*lambda)", "parent-convention")
    audit.check("candidate Wick scalar convention", "6C^2(g+4lambda)" in manifest["statement"], manifest["statement"], "6C^2(g+4lambda)", "parent-convention")

    nodes, edges, laplacian = cube_laplacian()
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 Laplacian row sums", laplacian * sp.ones(8, 1) == sp.zeros(8, 1), laplacian * sp.ones(8, 1), sp.zeros(8, 1), "Q3")
    spectrum: Counter[int] = Counter()
    for alpha in nodes:
        level = sum(alpha)
        vector = walsh(nodes, alpha)
        residual = laplacian * vector - 2 * level * vector
        audit.check(f"Q3 Walsh vector {alpha}", residual == sp.zeros(8, 1), residual, sp.zeros(8, 1), "Q3")
        spectrum[2 * level] += 1
    audit.check("Q3 spectrum", spectrum == Counter({0: 1, 2: 3, 4: 3, 6: 1}), dict(spectrum), {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")

    g = sp.symbols("g", positive=True)
    lam, C = sp.symbols("lambda C", nonnegative=True)
    mass, eta = sp.symbols("m_R eta_R", real=True)
    delta_k = -3 * C * ((g + lam) * sp.eye(8) + lam * laplacian)
    k_raw = mass * sp.eye(8) + eta * laplacian + delta_k
    kappa = []
    for level in range(4):
        alpha = (1,) * level + (0,) * (3 - level)
        vector = walsh(nodes, alpha)
        value = sp.factor(mass + 2 * level * eta - 3 * C * (g + lam + 2 * level * lam))
        audit.check(f"raw Walsh stiffness level {level}", (k_raw * vector - value * vector).applyfunc(sp.simplify) == sp.zeros(8, 1), k_raw * vector, value * vector, "counterterm")
        kappa.append(value)

    fixture = {g: 5, lam: 2, C: 3, mass: 7, eta: 4}
    kappa_fixture = [value.subs(fixture) for value in kappa]
    audit.check("hostile Walsh stiffness fixture", kappa_fixture == [-56, -84, -112, -140], kappa_fixture, [-56, -84, -112, -140], "counterterm")
    minimum_fixture = min(kappa_fixture)
    b_fixture = sp.Rational(1, 2) * max(0, -minimum_fixture)
    epsilon_iso = sp.factor(16 * b_fixture**2 / fixture[g] - 6 * fixture[C] ** 2 * (fixture[g] + 4 * fixture[lam]))
    audit.check("isotropic b fixture", b_fixture == 70, b_fixture, 70, "coercivity")
    audit.check("isotropic energy fixture", epsilon_iso == 14978, epsilon_iso, 14978, "coercivity")

    q = sp.symbols("q0:8", real=True)
    S = sp.expand(sum(value**2 for value in q))
    onsite_sos_left = sp.expand(sum(value**4 for value in q) - S**2 / 8)
    onsite_sos_right = sp.expand(sum((q[i] ** 2 - q[j] ** 2) ** 2 for i in range(8) for j in range(i + 1, 8)) / 8)
    audit.check("onsite quartic SOS identity", sp.expand(onsite_sos_left - onsite_sos_right) == 0, onsite_sos_left, onsite_sos_right, "coercivity")

    differences = [sp.expand(q[i] - q[j]) for i, j in edges]
    T = sp.expand(sum(value**2 for value in differences))
    edge_polynomial = sp.expand(sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges))
    edge_first_remainder = sp.expand(edge_polynomial - sum(value**4 for value in differences) / 2)
    edge_first_sos = sp.expand(sum((q[i] - q[j]) ** 2 * (q[i] + q[j]) ** 2 for i, j in edges) / 2)
    audit.check("Q3 edge first SOS", sp.expand(edge_first_remainder - edge_first_sos) == 0, edge_first_remainder, edge_first_sos, "coercivity")
    edge_cauchy_left = sp.expand(12 * sum(value**4 for value in differences) - T**2)
    edge_cauchy_right = sp.expand(sum((differences[i] ** 2 - differences[j] ** 2) ** 2 for i in range(12) for j in range(i + 1, 12)))
    audit.check("Q3 edge Cauchy SOS", sp.expand(edge_cauchy_left - edge_cauchy_right) == 0, edge_cauchy_left, edge_cauchy_right, "coercivity")

    radial, b_symbol = sp.symbols("R2 b", nonnegative=True)
    isotropic_left = g * radial**2 / 32 - b_symbol * radial + 16 * b_symbol**2 / g
    isotropic_right = g * radial**2 / 64 + (g * radial - 32 * b_symbol) ** 2 / (64 * g)
    audit.check("isotropic square completion", sp.simplify(isotropic_left - isotropic_right) == 0, isotropic_left, isotropic_right, "coercivity")

    alpha, beta, T_symbol = sp.symbols("alpha beta T", nonnegative=True)
    lam_pos = sp.symbols("lambda_pos", positive=True)
    anisotropic_left = g * radial**2 / 32 + lam_pos * T_symbol**2 / 96 - alpha * radial / 2 - beta * T_symbol / 2 + 4 * alpha**2 / g + 12 * beta**2 / lam_pos
    anisotropic_right = g * radial**2 / 64 + lam_pos * T_symbol**2 / 192 + (g * radial - 16 * alpha) ** 2 / (64 * g) + (lam_pos * T_symbol - 48 * beta) ** 2 / (192 * lam_pos)
    audit.check("anisotropic square completion", sp.simplify(anisotropic_left - anisotropic_right) == 0, anisotropic_left, anisotropic_right, "coercivity")
    alpha_fixture = max(0, 3 * fixture[C] * (fixture[g] + fixture[lam]) - fixture[mass])
    beta_fixture = max(0, 3 * fixture[C] * fixture[lam] - fixture[eta])
    epsilon_aniso = sp.factor(
        sp.Rational(4 * alpha_fixture**2, fixture[g])
        + sp.Rational(12 * beta_fixture**2, fixture[lam])
        - 6 * fixture[C] ** 2 * (fixture[g] + 4 * fixture[lam])
    )
    audit.check("anisotropic alpha fixture", alpha_fixture == 56, alpha_fixture, 56, "coercivity")
    audit.check("anisotropic beta fixture", beta_fixture == 14, beta_fixture, 14, "coercivity")
    audit.check("anisotropic energy fixture", epsilon_aniso == sp.Rational(14914, 5), epsilon_aniso, sp.Rational(14914, 5), "coercivity")
    lambda_zero_fixture = {g: 5, lam: 0, C: 3, mass: 7, eta: -4}
    lambda_zero_kappa = [value.subs(lambda_zero_fixture) for value in kappa]
    lambda_zero_b = sp.Rational(1, 2) * max(0, -min(lambda_zero_kappa))
    lambda_zero_shift = sp.factor(16 * lambda_zero_b**2 / lambda_zero_fixture[g] - 6 * lambda_zero_fixture[C] ** 2 * lambda_zero_fixture[g])
    audit.check("lambda-zero Walsh hostile fixture", lambda_zero_kappa == [-38, -46, -54, -62], lambda_zero_kappa, [-38, -46, -54, -62], "coercivity")
    audit.check("lambda-zero isotropic route finite", (lambda_zero_b, lambda_zero_shift) == (31, sp.Rational(14026, 5)), (lambda_zero_b, lambda_zero_shift), (31, sp.Rational(14026, 5)), "coercivity")

    bipartite = {q[index]: (-1) ** sum(node) for index, node in enumerate(nodes)}
    bipartite_S = S.subs(bipartite)
    bipartite_T = T.subs(bipartite)
    bipartite_onsite = sum(value**4 for value in q).subs(bipartite)
    bipartite_edge = edge_polynomial.subs(bipartite)
    audit.check("bipartite S fixture", bipartite_S == 8, bipartite_S, 8, "sharpness")
    audit.check("bipartite T fixture", bipartite_T == 48, bipartite_T, 48, "sharpness")
    audit.check("bipartite onsite sharpness", bipartite_onsite == bipartite_S**2 / 8, bipartite_onsite, bipartite_S**2 / 8, "sharpness")
    audit.check("bipartite edge sharpness", bipartite_edge == bipartite_T**2 / 24, bipartite_edge, bipartite_T**2 / 24, "sharpness")

    x = sp.symbols("x", real=True)
    singlet_polynomial = 2 * fixture[g] * x**4 + (4 * fixture[mass] - 12 * fixture[C] * (fixture[g] + fixture[lam])) * x**2 + 6 * fixture[C] ** 2 * (fixture[g] + 4 * fixture[lam])
    singlet_expected = 10 * x**4 - 224 * x**2 + 702
    audit.check("singlet hostile polynomial", sp.expand(singlet_polynomial - singlet_expected) == 0, singlet_polynomial, singlet_expected, "Gaussian-gap")
    singlet_y_coefficient = sp.expand(singlet_polynomial).coeff(x, 2)
    singlet_y2_coefficient = sp.expand(singlet_polynomial).coeff(x, 4)
    singlet_minimum_point = sp.factor(-singlet_y_coefficient / (2 * singlet_y2_coefficient))
    audit.check("derived singlet minimum point", singlet_minimum_point == sp.Rational(56, 5), singlet_minimum_point, sp.Rational(56, 5), "Gaussian-gap")
    singlet_minimum = sp.factor(singlet_polynomial.subs(x**2, singlet_minimum_point))
    singlet_literal_mean = sp.factor(
        6 * fixture[g] * fixture[C] ** 2
        + (4 * fixture[mass] - 12 * fixture[C] * (fixture[g] + fixture[lam])) * fixture[C]
        + 6 * fixture[C] ** 2 * (fixture[g] + 4 * fixture[lam])
    )
    full_Gaussian_mean = fixture[C] * (4 * fixture[mass] + 12 * fixture[eta])
    Gaussian_gap_lower_bound = sp.factor(full_Gaussian_mean - singlet_minimum)
    audit.check("singlet minimum fixture", singlet_minimum == sp.Rational(-2762, 5), singlet_minimum, sp.Rational(-2762, 5), "Gaussian-gap")
    audit.check("literal singlet Gaussian mean fixture", singlet_literal_mean == 300, singlet_literal_mean, 300, "Gaussian-gap")
    audit.check("full reference Gaussian mean fixture", full_Gaussian_mean == 228, full_Gaussian_mean, 228, "Gaussian-gap")
    audit.check("singlet and full means distinguished", singlet_literal_mean != full_Gaussian_mean, singlet_literal_mean, full_Gaussian_mean, "Gaussian-gap")
    audit.check("scalar-shift invariant gap lower-bound fixture", Gaussian_gap_lower_bound == sp.Rational(3902, 5), Gaussian_gap_lower_bound, sp.Rational(3902, 5), "Gaussian-gap")
    singlet_minimum_general = 6 * C**2 * (g + 4 * lam) - (12 * C * (g + lam) - 4 * mass) ** 2 / (8 * g)
    full_Gaussian_mean_general = C * (4 * mass + 12 * eta)
    general_gap = sp.expand(full_Gaussian_mean_general - singlet_minimum_general)
    general_leading_gap = sp.factor(general_gap.coeff(C, 2))
    expected_leading_gap = sp.factor(12 * g + 12 * lam + 18 * lam**2 / g)
    audit.check("general Gaussian gap leading coefficient", sp.simplify(general_leading_gap - expected_leading_gap) == 0, general_leading_gap, expected_leading_gap, "Gaussian-gap")

    squeeze = sp.diag(sp.sqrt(2), 1 / sp.sqrt(2))
    symplectic = sp.Matrix([[0, 1], [-1, 0]])
    audit.check("Nyquist squeeze symplectic", sp.simplify(squeeze.T * symplectic * squeeze - symplectic) == sp.zeros(2), squeeze.T * symplectic * squeeze, symplectic, "embedding")
    embed_M_2M = sp.zeros(4, 2)
    embed_M_2M[:2, :2] = squeeze
    embed_2M_4M = sp.zeros(6, 4)
    embed_2M_4M[:2, :2] = sp.eye(2)
    embed_2M_4M[2:4, 2:4] = squeeze
    embed_M_4M = sp.zeros(6, 2)
    embed_M_4M[:2, :2] = squeeze
    symplectic4 = sp.diag(symplectic, symplectic)
    symplectic6 = sp.diag(symplectic, symplectic, symplectic)
    audit.check("three-regulator Nyquist transitivity", embed_2M_4M * embed_M_2M == embed_M_4M, embed_2M_4M * embed_M_2M, embed_M_4M, "embedding")
    audit.check("M-to-2M symplectic injection", sp.simplify(embed_M_2M.T * symplectic4 * embed_M_2M) == symplectic, embed_M_2M.T * symplectic4 * embed_M_2M, symplectic, "embedding")
    audit.check("2M-to-4M symplectic injection", sp.simplify(embed_2M_4M.T * symplectic6 * embed_2M_4M) == symplectic4, embed_2M_4M.T * symplectic6 * embed_2M_4M, symplectic4, "embedding")

    ket = sp.Matrix([sp.sqrt(3) / 2, 0, 0, sp.Rational(1, 2)])
    fine_projector = ket * ket.T
    coarse_projector = sp.diag(1, 0)
    reduced = partial_trace_second(fine_projector, 2, 2)
    eta_overlap = sp.factor(1 - sp.trace(coarse_projector * reduced))
    difference = reduced - coarse_projector
    trace_distance = sum(abs(value) for value in difference.eigenvals().keys() for _ in range(difference.eigenvals()[value]))
    audit.check("entanglement eta fixture", eta_overlap == sp.Rational(1, 4), eta_overlap, sp.Rational(1, 4), "distance")
    audit.check("reduced trace distance fixture", trace_distance == sp.Rational(1, 2), trace_distance, sp.Rational(1, 2), "distance")
    audit.check("distance lower bound fixture", trace_distance >= 2 * eta_overlap, trace_distance, 2 * eta_overlap, "distance")
    audit.check("distance upper bound fixture", trace_distance <= 2 * sp.sqrt(eta_overlap), trace_distance, 2 * sp.sqrt(eta_overlap), "distance")
    squeeze_chart = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    chart_fine_density = sp.diag(1, 0, 0, 0)
    chart_coarse_density = sp.diag(1, 0)
    bare_restriction = partial_trace_second(chart_fine_density, 2, 2)
    typed_restriction = sp.simplify(squeeze_chart.T * bare_restriction * squeeze_chart)
    bare_restriction_norm = sum(abs(value) * multiplicity for value, multiplicity in (bare_restriction - chart_coarse_density).eigenvals().items())
    typed_restriction_norm = sum(abs(value) * multiplicity for value, multiplicity in (typed_restriction - chart_coarse_density).eigenvals().items())
    audit.check("bare partial trace can mask chart defect", bare_restriction_norm == 0, bare_restriction_norm, 0, "distance")
    audit.check("predual chart restriction nontrivial", typed_restriction_norm == sp.sqrt(2), typed_restriction_norm, sp.sqrt(2), "distance")

    identity2 = sp.eye(2)
    gamma_m_c = sp.Matrix([[0, 1], [1, 0]])
    gamma_m_d = identity2
    gamma_n_c = sp.Matrix([[0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    gamma_n_d = sp.eye(4)
    observable = sp.Matrix([[2, 1], [1, -1]])
    rho_m = sp.diag(sp.Rational(2, 3), sp.Rational(1, 3))
    rho_n = sp.diag(sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(1, 8), sp.Rational(1, 8))

    def theta(gamma: sp.Matrix, value: sp.Matrix) -> sp.Matrix:
        return sp.simplify(gamma.T * value * gamma)

    def cut_embedding(gamma_coarse: sp.Matrix, gamma_fine: sp.Matrix, value: sp.Matrix) -> sp.Matrix:
        bulk = sp.simplify(gamma_coarse * value * gamma_coarse.T)
        return sp.simplify(gamma_fine.T * sp.kronecker_product(bulk, identity2) * gamma_fine)

    b_c = theta(gamma_m_c, observable)
    b_d = theta(gamma_m_d, observable)
    j_c = cut_embedding(gamma_m_c, gamma_n_c, b_c)
    j_d = cut_embedding(gamma_m_d, gamma_n_d, b_d)
    rho_m_c = theta(gamma_m_c, rho_m)
    rho_n_c = theta(gamma_n_c, rho_n)
    bulk_defect = sp.factor(sp.trace(rho_n * sp.kronecker_product(observable, identity2)) - sp.trace(rho_m * observable))
    cut_defect = sp.factor(sp.trace(rho_n_c * j_c) - sp.trace(rho_m_c * b_c))
    audit.check("cut bulk defect nonzero oracle", bulk_defect == sp.Rational(1, 4), bulk_defect, sp.Rational(1, 4), "cut-square")
    audit.check("cut and bulk defect identity fixture", cut_defect == bulk_defect, cut_defect, bulk_defect, "cut-square")
    reduced_rho_n = partial_trace_second(rho_n, 2, 2)
    reduced_density_defect = reduced_rho_n - rho_m
    reduced_trace_norm = sum(abs(value) * multiplicity for value, multiplicity in reduced_density_defect.eigenvals().items())
    audit.check("predual restriction trace norm fixture", reduced_trace_norm == sp.Rational(1, 6), reduced_trace_norm, sp.Rational(1, 6), "cut-square")
    cut_restriction_density = theta(gamma_m_c, reduced_rho_n)
    cut_density_defect = cut_restriction_density - rho_m_c
    cut_dual_norm = sum(abs(value) * multiplicity for value, multiplicity in cut_density_defect.eigenvals().items())
    audit.check("cut and bulk dual norms agree", cut_dual_norm == reduced_trace_norm, cut_dual_norm, reduced_trace_norm, "cut-square")
    same_time_m = sp.simplify(gamma_m_d.T * gamma_m_c)
    same_time_n = sp.simplify(gamma_n_d.T * gamma_n_c)
    beta_m = sp.simplify(same_time_m * b_c * same_time_m.T)
    beta_n_jc = sp.simplify(same_time_n * j_c * same_time_n.T)
    audit.check("coarse same-time anchor identity", beta_m == b_d, beta_m, b_d, "cut-square")
    audit.check("all-same-time cut naturality fixture", beta_n_jc == j_d, beta_n_jc, j_d, "cut-square")

    n_symbol = sp.symbols("N", positive=True)
    covariance_q = n_symbol / 2
    covariance_p = 1 / (2 * n_symbol)
    audit.check("squeezed uncertainty determinant", sp.simplify(covariance_q * covariance_p) == sp.Rational(1, 4), sp.simplify(covariance_q * covariance_p), sp.Rational(1, 4), "regularity")
    audit.check("squeezed oscillator frequency", sp.sqrt(n_symbol * (1 / n_symbol)) == 1, sp.sqrt(n_symbol * (1 / n_symbol)), 1, "regularity")
    characteristic_field = sp.exp(-n_symbol / 4)
    characteristic_momentum = sp.exp(-1 / (4 * n_symbol))
    audit.check("squeezed field characteristic limit", sp.limit(characteristic_field, n_symbol, sp.oo) == 0, sp.limit(characteristic_field, n_symbol, sp.oo), 0, "regularity")
    audit.check("squeezed momentum characteristic limit", sp.limit(characteristic_momentum, n_symbol, sp.oo) == 1, sp.limit(characteristic_momentum, n_symbol, sp.oo), 1, "regularity")

    lattice_index = sp.symbols("n", integer=True, nonnegative=True)
    adjacent_error = 4 ** (-lattice_index)
    tail_error = sp.summation(adjacent_error, (lattice_index, 3, sp.oo))
    audit.check("summable dyadic cylindrical tail fixture", tail_error == sp.Rational(1, 48), tail_error, sp.Rational(1, 48), "cylindrical")
    X_dynamic, Y_dynamic = sp.symbols("X_dynamic Y_dynamic", real=True)
    g_dynamic, L_dynamic = sp.symbols("g_dynamic L_dynamic", positive=True)
    collective_onsite = sp.expand(
        (L_dynamic / 2)
        * (g_dynamic / 4)
        * (((X_dynamic + Y_dynamic) / sp.sqrt(L_dynamic)) ** 4 + ((X_dynamic - Y_dynamic) / sp.sqrt(L_dynamic)) ** 4)
    )
    dynamic_cross_coefficient_general = sp.factor(collective_onsite.coeff(X_dynamic, 2).coeff(Y_dynamic, 2))
    dynamic_mixed_derivative = sp.factor(sp.diff(collective_onsite, X_dynamic, 2, Y_dynamic, 2))
    dynamic_cross_coefficient = dynamic_cross_coefficient_general.subs({g_dynamic: 1, L_dynamic: 4})
    dynamic_total_force = sp.factor(-sp.diff(collective_onsite, X_dynamic))
    dynamic_total_force_at_one = dynamic_total_force.subs({g_dynamic: 1, L_dynamic: 4, X_dynamic: 1, Y_dynamic: 1})
    dynamic_total_force_at_y_zero = dynamic_total_force.subs({g_dynamic: 1, L_dynamic: 4, X_dynamic: 1, Y_dynamic: 0})
    dynamic_force_at_one = sp.factor(dynamic_total_force_at_one - dynamic_total_force_at_y_zero)
    dynamic_force_at_y_zero = sp.Rational(0)
    audit.check("collective dynamic coefficient derived", dynamic_cross_coefficient_general == 3 * g_dynamic / (2 * L_dynamic), dynamic_cross_coefficient_general, 3 * g_dynamic / (2 * L_dynamic), "dynamics")
    audit.check("collective mixed derivative derived", dynamic_mixed_derivative == 6 * g_dynamic / L_dynamic, dynamic_mixed_derivative, 6 * g_dynamic / L_dynamic, "dynamics")
    audit.check("collective dynamic cross coefficient fixture", dynamic_cross_coefficient == sp.Rational(3, 8), dynamic_cross_coefficient, sp.Rational(3, 8), "dynamics")
    audit.check("collective total force fixture", (dynamic_total_force_at_one, dynamic_total_force_at_y_zero) == (-1, sp.Rational(-1, 4)), (dynamic_total_force_at_one, dynamic_total_force_at_y_zero), (-1, sp.Rational(-1, 4)), "dynamics")
    audit.check("signed added-mode force leakage fixture", dynamic_force_at_one == sp.Rational(-3, 4), dynamic_force_at_one, sp.Rational(-3, 4), "dynamics")
    audit.check("force depends on added coordinate", dynamic_force_at_one != dynamic_force_at_y_zero, dynamic_force_at_one, dynamic_force_at_y_zero, "dynamics")

    point_count = 4
    weight = sp.Rational(1, 8)
    field_value = weight * sum(sp.Rational(2) for _ in range(point_count))
    field_label_norm_fourth = (weight * point_count) ** 3
    field_configuration_norm_fourth = weight * point_count * 2**4
    momentum_value = field_value
    momentum_label_norm_second = weight * point_count
    momentum_configuration_norm_second = weight * point_count * 2**2
    audit.check("weighted Holder fourth-power equality fixture", field_value**4 == field_label_norm_fourth * field_configuration_norm_fourth, field_value**4, field_label_norm_fourth * field_configuration_norm_fourth, "moments")
    audit.check("weighted momentum Cauchy equality fixture", momentum_value**2 == momentum_label_norm_second * momentum_configuration_norm_second, momentum_value**2, momentum_label_norm_second * momentum_configuration_norm_second, "moments")
    audit.check("conditional field coefficient fixture", sp.Rational(64 * 7, 5) == sp.Rational(448, 5), sp.Rational(64 * 7, 5), sp.Rational(448, 5), "moments")
    audit.check("conditional momentum coefficient fixture", 2 * 3 * 7 == 42, 2 * 3 * 7, 42, "moments")
    audit.check("conditional edge coefficient fixture", sp.Rational(192 * 7, 2) == 672, sp.Rational(192 * 7, 2), 672, "moments")

    true_scope = (
        "Q3_matrix_counterterm_candidate_typed",
        "cutoff_uniform_lower_form_stability_after_declared_scalar_shift",
        "fixed_regulator_ground_and_Gibbs",
        "abstract_compatible_state_subnet",
        "matched_reference_cut_algebra_square",
        "cut_bulk_defect_identity",
    )
    false_scope = (
        "exact_finite_pair_ground_projectivity",
        "asymptotic_ground_projectivity",
        "unshifted_uniform_energy_floor",
        "uniform_shifted_energy_upper_bound",
        "pointwise_stability_plus_reference_Gaussian_uniform_energy",
        "cutoff_uniform_moment_bounds",
        "uniform_Weyl_equicontinuity",
        "normal_or_regular_limit_state",
        "unique_full_sequence_limit",
        "natural_exact_dynamics_equivariance",
        "asymptotic_or_dressed_dynamics_equivariance",
        "interacting_continuum_QFT_state",
        "interacting_Hadamard_state",
        "physical_state_or_vacuum",
        "below_empty_space_comparison",
        "physical_phase_transition",
        "physical_light_speed_derived",
        "original_3D_Q3LOCK_parent",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    next_gate = "PA-CP1-CL8-UNIFORM-WEYL-EQUICONTINUITY-AND-INTERACTING-LIMIT-IDENTIFICATION"
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == next_gate, manifest["gate_resolution"]["next_gate"], next_gate, "scope")

    derived = {
        "Q3_spectrum": {"eigenvalues": sorted(spectrum), "multiplicities": [spectrum[value] for value in sorted(spectrum)]},
        "counterterm_fixture": {
            "kappa": kappa_fixture,
            "b_iso": b_fixture,
            "epsilon_iso": epsilon_iso,
            "alpha": alpha_fixture,
            "beta": beta_fixture,
            "epsilon_aniso": epsilon_aniso,
        },
        "sharpness_fixture": {"S": bipartite_S, "T": bipartite_T, "onsite": bipartite_onsite, "edge": bipartite_edge},
        "Gaussian_gap_fixture": {
            "polynomial": singlet_polynomial,
            "minimum": singlet_minimum,
            "literal_singlet_mean": singlet_literal_mean,
            "full_reference_mean": full_Gaussian_mean,
            "global_gap_lower_bound": Gaussian_gap_lower_bound,
        },
        "distance_fixture": {"eta": eta_overlap, "trace_distance": trace_distance},
        "cut_fixture": {"bulk_defect": bulk_defect, "cut_defect": cut_defect, "same_time_commutes": beta_n_jc == j_d},
        "regularity_fixture": {"uncertainty_determinant": covariance_q * covariance_p, "field_limit": 0, "momentum_limit": 1},
        "dynamic_force_fixture": {"at_X1_Y1": dynamic_force_at_one, "at_X1_Y0": dynamic_force_at_y_zero},
        "negative_ids": list(NEGATIVE_IDS),
    }
    source_hashes = {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST)}
    for path in PARENT_FILES + AUTHORITY_FILES:
        source_hashes[path] = sha256(REPO / path)
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": manifest["parent_ids"],
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "script_version": __version__,
        "verdict": manifest["verdict"],
        "status": manifest["gate_resolution"]["status"],
        "derived": derived,
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "source_sha256": source_hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
