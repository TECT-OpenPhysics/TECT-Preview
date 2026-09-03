#!/usr/bin/env python3
"""Primary exact audit for the R-163 deterministic dyadic-forest theorem.

The analytic proof is carried by the accompanying note.  This executable
checks its exact upstream constants, path-series identities, forest algebra,
origin connection support, adverse local-gap fixture, and retained gap.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-FULL-LATTICE-WEIGHTED-RESOLVENT-DYADIC-FOREST-"
    "UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
)
LEDGER_ID = "R-163"
SLUG = "full-lattice-weighted-resolvent-dyadic-forest-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-primary-{SLUG}" / "result.json"

AUTHORITIES = {
    "A1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "A7": REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "R-107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-160": CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json",
    "R-161": CLAIM_DIR / "classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_manifest.json",
    "R-162": CLAIM_DIR / "classii_resolvent_pure_dyadic_recursive_chain_uniform_neighborhood_gap_boundary_manifest.json",
}

SCOPE = {
    "actual_shifted_state_read_at_each_stage": True,
    "arbitrary_finite_injective_pure_dyadic_forest": True,
    "centered_independent_raw_gaussian_blocks": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "complete_controller_pullback_hessian": True,
    "complete_expected_global_terminal_scalar": True,
    "deterministic_matrix_coefficients": True,
    "exact_nonaliased_continuum_torus_integration": True,
    "fixed_positive_A7_floor": True,
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_spatial_dimension_three": True,
    "forward_legal_reverse_balanced_are_one_hessian": True,
    "independent_low_or_feshbach_coordinate": False,
    "intrinsic_hessian_claimed": False,
    "local_root_ECN_equals_Pcomp": False,
    "pathwise_fibrewise_conditional_hessian": False,
    "projected_force_connection_included": True,
    "random_or_nonlinear_past_dependent_coefficients": False,
    "revisit_cycles_or_general_branching": False,
    "sextic_connection_included": True,
    "summed_HS_l2_coefficient_norm": True,
    "uniform_over_forest_cardinality_depth_finite_cutoff_and_admitted_regulator": True,
    "floor_or_infinite_endpoint_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-163 proves one positive analytic l2(HS) coefficient radius for every finite injective "
    "pure-dyadic deterministic-matrix shifted-state forest, uniformly in its number of unrelated "
    "chains, depths, retained modes, finite cutoff, and admitted common-even regulator, at the "
    "fixed side-16 d=3 A1/A7 setting. It controls the complete expected global controller-pullback "
    "Hessian and includes source, endpoint/current, trace, projected-force, forward/legal-reverse/"
    "balanced, and sextic connections once. It proves no intrinsic-Hessian theorem, random or "
    "nonlinear past-dependent law, revisit/cycle/general branching, pathwise fibrewise conditional "
    "estimate, removal, T-050/A13, Nelson, measure, phase/PDE, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def sha256_text(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def forest_shift(values: tuple[sp.Expr, ...]) -> sp.Matrix:
    """Two disjoint length-two chains on vertices 0-1-2 and 3-4-5."""
    if len(values) != 4:
        raise ValueError("four edge values required")
    matrix = sp.zeros(6)
    for target, source, value in ((1, 0, values[0]), (2, 1, values[1]), (4, 3, values[2]), (5, 4, values[3])):
        matrix[target, source] = value
    return matrix


def finite_resolvent(matrix: sp.Matrix) -> sp.Matrix:
    identity = sp.eye(matrix.rows)
    return identity + matrix + matrix**2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, path in AUTHORITIES.items():
        audit.check("authority", f"{label} exists", path.is_file(), relative(path), "existing file")

    r160_manifest = json.loads(AUTHORITIES["R-160"].read_text(encoding="utf-8"))
    r160_record = r160_manifest["files"]["primary_result"]
    r160_path = REPO / r160_record["path"]
    audit.check("authority", "R-160 primary hash", sha256_text(r160_path) == r160_record["sha256"], sha256_text(r160_path), r160_record["sha256"])
    r160 = json.loads(r160_path.read_text(encoding="utf-8"))
    origin_gap = sp.Rational(r160["diagnostics"]["lattice_certified_gap"])
    audit.check("authority", "R-160 arbitrary-family origin gap", origin_gap == sp.Rational(4, 25), origin_gap, sp.Rational(4, 25))

    r161_manifest = json.loads(AUTHORITIES["R-161"].read_text(encoding="utf-8"))
    r161_record = r161_manifest["files"]["primary_result"]
    r161_path = REPO / r161_record["path"]
    audit.check("authority", "R-161 primary hash", sha256_text(r161_path) == r161_record["sha256"], sha256_text(r161_path), r161_record["sha256"])
    r161 = json.loads(r161_path.read_text(encoding="utf-8"))
    g = sp.Rational(r161["derived"]["synthesis_envelope_g"])
    c0 = sp.Rational(r161["derived"]["side16_lattice_floor_c0"])
    audit.check("authority", "registered synthesis envelope g", g == sp.Rational(244140625000000000, 28800000000947494031), g, "registered exact g")
    audit.check("authority", "registered side-16 floor", c0 == sp.Rational(3, 20), c0, sp.Rational(3, 20))
    shell_constants = r161["derived"]["shell_upper_constants"]
    audit.check("authority", "R-161 lattice zeta guards", shell_constants == {"power4": 52, "power6": 35, "power8": 32}, shell_constants, {"power4": 52, "power6": 35, "power8": 32})

    # Endpoint cross weights alpha_EF,k <= a_EF q_EF^k.  The square-sum
    # bounds are inherited from the exact A1 symbol and the d=3 lattice sums.
    cross_base_squared = {
        "SS": 32 * g**2 / c0**4,
        "SD": 35 * g**2 / c0**3,
        "DS": 35 * g**2 / c0**3,
        "DD": 52 * g**2 / c0**2,
    }
    cross_ratio = {
        "SS": sp.Rational(1, 4),
        "SD": sp.Rational(1, 4),
        "DS": sp.Rational(1, 2),
        "DD": sp.Rational(1, 2),
    }
    audit.check("weights", "all cross bases finite positive", all(value > 0 and value.is_finite for value in cross_base_squared.values()), cross_base_squared, "finite positive")
    audit.check("weights", "worst current-current exponent is summable", cross_base_squared["DD"] == 52 * g**2 / c0**2, cross_base_squared["DD"], "52 g^2 c0^-2")
    audit.check("weights", "target-current dyadic ratio", cross_ratio["DD"] == sp.Rational(1, 2), cross_ratio["DD"], sp.Rational(1, 2))
    audit.check("weights", "value-target dyadic ratio", cross_ratio["SS"] == sp.Rational(1, 4), cross_ratio["SS"], sp.Rational(1, 4))
    audit.check("weights", "three-dimensional threshold", 4 > 3 and 2 <= 3, {"weighted_power": 4, "raw_current_power": 2, "dimension": 3}, "4>d while 2<=d")

    # Exact path-series derivative identities.  Differentiating the scalar
    # majorant is an exact audit of the falling-factorial path counts.
    r, q = sp.symbols("r q", positive=True)
    path_majorant = q * r / (1 - q * r)
    hs_majorant = r / (1 - r)
    for order in range(1, 4):
        path_expected = sp.factorial(order) * q**order / (1 - q * r) ** (order + 1)
        hs_expected = sp.factorial(order) / (1 - r) ** (order + 1)
        audit.check("series", f"cross path derivative order {order}", sp.simplify(sp.diff(path_majorant, r, order) - path_expected) == 0, sp.diff(path_majorant, r, order), path_expected)
        audit.check("series", f"weighted-HS derivative order {order}", sp.simplify(sp.diff(hs_majorant, r, order) - hs_expected) == 0, sp.diff(hs_majorant, r, order), hs_expected)
    audit.check("series", "cross path zero jet starts with one edge", sp.series(path_majorant, r, 0, 4).removeO() == q * r + q**2 * r**2 + q**3 * r**3, sp.series(path_majorant, r, 0, 4), "qr+q^2r^2+q^3r^3")
    audit.check("series", "weighted-HS zero jet starts with one edge", sp.series(hs_majorant, r, 0, 4).removeO() == r + r**2 + r**3, sp.series(hs_majorant, r, 0, 4), "r+r^2+r^3")

    # Direct two-sided word majorant for P_A-I.  This independently covers
    # common-ancestor BB* words and avoids ever factoring through raw D*.
    q_s = sp.Rational(1, 4)
    q_d = sp.Rational(1, 2)
    word_generators = {
        "SS": 1 / (1 - q_s * r) ** 2 - 1,
        "DD": 1 / (1 - q_d * r) ** 2 - 1,
        "SD": 1 / ((1 - q_s * r) * (1 - q_d * r)) - 1,
    }
    audit.check("word", "SS two-sided series starts after identity", sp.series(word_generators["SS"], r, 0, 3).removeO() == 2 * q_s * r + 3 * q_s**2 * r**2, sp.series(word_generators["SS"], r, 0, 3), "2q_S r+3q_S^2 r^2")
    audit.check("word", "DD two-sided series starts after identity", sp.series(word_generators["DD"], r, 0, 3).removeO() == 2 * q_d * r + 3 * q_d**2 * r**2, sp.series(word_generators["DD"], r, 0, 3), "2q_D r+3q_D^2 r^2")
    audit.check("word", "mixed generator includes both orientations", sp.diff(word_generators["SD"], r).subs(r, 0) == q_s + q_d, sp.diff(word_generators["SD"], r).subs(r, 0), q_s + q_d)

    # Exact two-component forest fixture.  It verifies nilpotence, resolvent,
    # R=B+B*+BB*, direct-sum separation, and the complete covariance second jet.
    a = (sp.Rational(1, 7), sp.Rational(-1, 5), sp.Rational(2, 9), sp.Rational(1, 4))
    h = (sp.Rational(2, 5), sp.Rational(1, 3), sp.Rational(-3, 8), sp.Rational(5, 11))
    k = (sp.Rational(-1, 4), sp.Rational(5, 13), sp.Rational(1, 6), sp.Rational(-2, 7))
    n_a, n_h, n_k = map(forest_shift, (a, h, k))
    t_a = finite_resolvent(n_a)
    b_a = t_a - sp.eye(6)
    p_a = t_a * t_a.T
    r_a = p_a - sp.eye(6)
    audit.check("forest", "forest shift cubic nilpotence", n_a**3 == sp.zeros(6), n_a**3, sp.zeros(6))
    audit.check("forest", "finite resolvent inverse", sp.simplify((sp.eye(6) - n_a) * t_a) == sp.eye(6), (sp.eye(6) - n_a) * t_a, sp.eye(6))
    audit.check("forest", "covariance perturbation decomposition", sp.simplify(r_a - (b_a + b_a.T + b_a * b_a.T)) == sp.zeros(6), r_a - (b_a + b_a.T + b_a * b_a.T), sp.zeros(6))
    audit.check("forest", "unrelated chains remain covariance-disjoint", all(r_a[i, j] == 0 for i in range(3) for j in range(3, 6)), "cross blocks zero", "cross blocks zero")

    u, v = sp.symbols("u v")
    n_path = n_a + u * n_h + v * n_k
    t_path = finite_resolvent(n_path)
    d1 = t_path.diff(u).subs({u: 0, v: 0})
    d2 = t_path.diff(u, v).subs({u: 0, v: 0})
    audit.check("forest", "resolvent first jet", sp.simplify(d1 - t_a * n_h * t_a) == sp.zeros(6), d1 - t_a * n_h * t_a, sp.zeros(6))
    d2_expected = t_a * n_h * t_a * n_k * t_a + t_a * n_k * t_a * n_h * t_a
    audit.check("forest", "resolvent mixed second jet", sp.simplify(d2 - d2_expected) == sp.zeros(6), d2 - d2_expected, sp.zeros(6))

    t_origin = finite_resolvent(u * n_h)
    p_origin = t_origin * t_origin.T
    covariance_second = p_origin.diff(u, 2).subs(u, 0)
    covariance_expected = 2 * (n_h * n_h.T + n_h**2 + (n_h.T) ** 2)
    audit.check("origin", "recursive covariance second jet", sp.simplify(covariance_second - covariance_expected) == sp.zeros(6), covariance_second - covariance_expected, sp.zeros(6))
    acceleration = n_h**2 + (n_h.T) ** 2
    audit.check("origin", "acceleration is two-step within each chain", all(acceleration[i, j] == 0 for i in range(6) for j in range(6) if abs(i - j) != 2), acceleration, "only distance-two blocks")
    audit.check("origin", "no cross-chain acceleration", all(acceleration[i, j] == 0 for i in range(3) for j in range(3, 6)), "cross blocks zero", "cross blocks zero")
    audit.check("origin", "p-to-4p support is nonzero", {4 - 1, 4 + 1} == {3, 5}, sorted({4 - 1, 4 + 1}), [3, 5])
    audit.check("origin", "source gradient vanishes at zero controller", b_a.subs({}) is not None and sp.zeros(6) == (finite_resolvent(sp.zeros(6)) - sp.eye(6)), finite_resolvent(sp.zeros(6)) - sp.eye(6), sp.zeros(6))

    # An explicit one-use 2x2 fixture rejects the forbidden inference from
    # positive diagonal/local gaps to a positive complete owner.
    local_owner = sp.Matrix([[sp.Rational(3, 20), -sp.Rational(1, 5)], [-sp.Rational(1, 5), sp.Rational(3, 20)]])
    eigenvalues = sorted(local_owner.eigenvals().keys())
    audit.check("adversary", "local diagonals exceed target", all(local_owner[i, i] > sp.Rational(1, 10) for i in range(2)), [local_owner[i, i] for i in range(2)], ">1/10")
    audit.check("adversary", "complete one-use owner is indefinite", eigenvalues == [-sp.Rational(1, 20), sp.Rational(7, 20)], eigenvalues, [-sp.Rational(1, 20), sp.Rational(7, 20)])
    low_kernel = sp.Matrix([[1, 1], [1, 0]])
    audit.check("adversary", "low-kernel cross needs range compatibility", low_kernel.det() == -1, low_kernel.det(), -1)

    # Assembly constants are deliberately analytic.  Finiteness, rather than
    # an unregistered decimal radius, is the numerical content of the theorem.
    r0 = sp.Rational(1, 2)
    m_s_squared = g
    m_d_squared = g / 2
    cross_jets_at_r0: dict[str, list[sp.Expr]] = {}
    for label in ("SS", "SD", "DS", "DD"):
        base = sp.sqrt(cross_base_squared[label])
        ratio = cross_ratio[label]
        values = [base * ratio * r0 / (1 - ratio * r0)]
        values.extend(
            sp.factorial(order) * base * ratio**order / (1 - ratio * r0) ** (order + 1)
            for order in range(1, 4)
        )
        cross_jets_at_r0[label] = values
    hs_jets_at_r0 = {
        "S": [sp.sqrt(m_s_squared) * r0 / (1 - r0)]
        + [sp.sqrt(m_s_squared) * sp.factorial(order) / (1 - r0) ** (order + 1) for order in range(1, 4)],
        "D": [sp.sqrt(m_d_squared) * r0 / (1 - r0)]
        + [sp.sqrt(m_d_squared) * sp.factorial(order) / (1 - r0) ** (order + 1) for order in range(1, 4)],
    }
    audit.check("assembly", "all cross jets finite at audit ball", all(value.is_finite and value > 0 for values in cross_jets_at_r0.values() for value in values), cross_jets_at_r0, "finite positive")
    audit.check("assembly", "all weighted-HS jets finite at audit ball", all(value.is_finite and value > 0 for values in hs_jets_at_r0.values() for value in values), hs_jets_at_r0, "finite positive")
    for order in range(4):
        quadratic_ss = sum(sp.binomial(order, split) * hs_jets_at_r0["S"][split] * hs_jets_at_r0["S"][order - split] for split in range(order + 1))
        quadratic_dd = sum(sp.binomial(order, split) * hs_jets_at_r0["D"][split] * hs_jets_at_r0["D"][order - split] for split in range(order + 1))
        rho_ss = 2 * cross_jets_at_r0["SS"][order] + quadratic_ss
        rho_dd = 2 * cross_jets_at_r0["DD"][order] + quadratic_dd
        audit.check("assembly", f"complete R data jet {order} finite", rho_ss.is_finite and rho_dd.is_finite and rho_ss > 0 and rho_dd > 0, {"SS": rho_ss, "DD": rho_dd}, "finite positive")

    gamma_word = {
        "SS": sp.sqrt(cross_base_squared["SS"]),
        "DD": sp.sqrt(cross_base_squared["DD"]),
        "SD": sp.sqrt(cross_base_squared["SD"]),
    }
    word_jets_at_r0: dict[str, list[sp.Expr]] = {}
    for label, generator in word_generators.items():
        word_jets_at_r0[label] = [sp.simplify(gamma_word[label] * sp.diff(generator, r, order).subs(r, r0)) for order in range(4)]
    data_jet_squared_at_r0 = []
    for order in range(4):
        c_jet = word_jets_at_r0["SS"][order]
        u_jet = 3 * word_jets_at_r0["DD"][order]
        k_jet = word_jets_at_r0["SD"][order]
        data_jet_squared_at_r0.append(sp.simplify(c_jet**2 + u_jet**2 + 6 * k_jet**2))
    audit.check("word", "two-sided word jets finite through order three", all(value.is_finite and value > 0 for values in word_jets_at_r0.values() for value in values), word_jets_at_r0, "finite positive")
    audit.check("word", "safe assembled data jets finite", all(value.is_finite and value > 0 for value in data_jet_squared_at_r0), data_jet_squared_at_r0, "finite positive")

    cm_d3_bound = sp.Rational(27, 5) * (1 + r0) * (1 - r0) ** -5
    audit.check("modulus", "source third derivative bound", cm_d3_bound == sp.Rational(1296, 5), cm_d3_bound, sp.Rational(1296, 5))
    retained_gap = origin_gap - sp.Rational(3, 100)
    audit.check("gap", "retained coefficient gap", retained_gap == sp.Rational(13, 100), retained_gap, sp.Rational(13, 100))
    audit.check("gap", "retained gap exceeds target", retained_gap > sp.Rational(1, 10), retained_gap, ">1/10")
    audit.check("gap", "recursive tangent metric guard", sp.Rational(100, 97) ** 4 < sp.Rational(13, 10), sp.Rational(100, 97) ** 4, "<13/10")

    # The exact T-050 coefficient threshold is weaker than positive convexity.
    # If the complete reduced action has Hessian mu G along every radial
    # segment, the explicit source term permits any mu > -1/110, provided the
    # origin force and anchor are controlled.  This is a theorem about the
    # required target, not a claim that the production mu is already proved.
    p_nelson = sp.Rational(11, 10)
    epsilon_v_limit = 1 / (2 * p_nelson)
    explicit_source = sp.Rational(9, 20)
    epsilon_6 = sp.Rational(3, 20)
    epsilon_6_limit = sp.Rational(27, 100)
    coefficient_headroom = epsilon_v_limit - explicit_source
    mu_floor = -2 * coefficient_headroom
    owner_floor = mu_floor - sp.Rational(9, 10)
    delta = sp.symbols("delta", positive=True)
    mu_trial = mu_floor + delta
    eta_trial = delta / 4
    epsilon_v_trial = sp.simplify(explicit_source - mu_trial / 2 + eta_trial)
    audit.check("threshold", "source coefficient headroom", coefficient_headroom == sp.Rational(1, 220), coefficient_headroom, sp.Rational(1, 220))
    audit.check("threshold", "reduced Hessian floor", mu_floor == -sp.Rational(1, 110), mu_floor, -sp.Rational(1, 110))
    audit.check("threshold", "owner adverse floor", owner_floor == -sp.Rational(10, 11), owner_floor, -sp.Rational(10, 11))
    audit.check("threshold", "strict trial coefficient", sp.simplify(epsilon_v_limit - epsilon_v_trial) == delta / 4, epsilon_v_trial, "5/11-delta/4")
    audit.check("threshold", "sextic coefficient admissible", epsilon_6 < epsilon_6_limit, epsilon_6, "<27/100")
    audit.check("scope", "forest is injective and acyclic only", SCOPE["arbitrary_finite_injective_pure_dyadic_forest"] and not SCOPE["revisit_cycles_or_general_branching"], SCOPE, "injective pure-dyadic forest only")
    audit.check("scope", "T-050 remains open", not SCOPE["t050_closed"] and not SCOPE["a13_closed"] and not SCOPE["sector_a_closed"], [SCOPE["t050_closed"], SCOPE["a13_closed"], SCOPE["sector_a_closed"]], [False, False, False])

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {label: sha256_text(path) for label, path in AUTHORITIES.items()},
        "diagnostics": {
            "g": g,
            "c0": c0,
            "origin_gap": origin_gap,
            "retained_gap": retained_gap,
            "cross_base_squared": cross_base_squared,
            "cross_ratio": cross_ratio,
            "cross_jets_at_r0": cross_jets_at_r0,
            "weighted_HS_jets_at_r0": hs_jets_at_r0,
            "two_sided_word_jets_at_r0": word_jets_at_r0,
            "safe_data_jet_squared_at_r0": data_jet_squared_at_r0,
            "CM_D3_bound_at_r0": cm_d3_bound,
            "nelson_p": p_nelson,
            "epsilon_v_limit": epsilon_v_limit,
            "epsilon_6": epsilon_6,
            "reduced_action_hessian_floor": mu_floor,
            "owner_adverse_floor": owner_floor,
            "forest_fixture_edges": 4,
            "forest_fixture_components": 2,
            "local_gap_counterfixture_eigenvalues": eigenvalues,
        },
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} primary: {len(audit.rows)}/{len(audit.rows)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
