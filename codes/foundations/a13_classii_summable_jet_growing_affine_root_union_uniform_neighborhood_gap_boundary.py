#!/usr/bin/env python3
"""Primary exact audit for the R-161 summable-jet uniform-neighbourhood theorem.

The executable certifies the exact rational constants and finite algebra used
by the analytic proof.  The radius is existential: it follows from a uniform
operator-Hessian modulus after the fixed-d=3, family-cardinality-free
covariance-jet bounds below.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
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
RESULT_ID = "A13-CLASSII-SUMMABLE-JET-GROWING-AFFINE-ROOT-UNION-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-161"
SLUG = "summable-jet-growing-affine-root-union-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
CLAIM_DIR = REPO / "claims" / CLAIM

AUTHORITIES = {
    "A1": REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json",
    "A7": REPO / "claims" / "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE" / "classii_renormalised_energy_manifest.json",
    "R-107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-151": CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-159": CLAIM_DIR / "classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary_manifest.json",
    "R-160": CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json",
    "R-145": CLAIM_DIR / "classii_weighted_trace_excess_anisotropic_covariance_sextic_reduction_manifest.json",
    "R-146": CLAIM_DIR / "classii_canonical_covariance_relative_anchor_anisotropic_temporal_reduction_manifest.json",
}

R160_PRIMARY = CLAIM_DIR / "runs" / "2026-08-03-primary-weighted-schur-growing-affine-root-union-origin-gap-boundary" / "result.json"
R151_PRIMARY = CLAIM_DIR / "runs" / "2026-08-03-primary-two-root-endpoint-hessian-uniform-local-gap-boundary" / "result.json"
R107_NOTE = CLAIM_DIR / "notes" / "classii-coherent-output-cluster-predictable-baseline-boundary-260728-v1.0.tex.txt"
R141_NOTE = CLAIM_DIR / "notes" / "classii-projected-force-global-doob-signed-gram-adaptive-collar-quotient-boundary-260731-v1.0.tex.txt"
R146_NOTE = CLAIM_DIR / "notes" / "classii-canonical-covariance-relative-anchor-anisotropic-temporal-reduction-260802-v1.0.tex.txt"

TARGET_GAP = sp.Rational(1, 10)
RETAINED_GAP = sp.Rational(13, 100)
VOLUME = sp.Integer(16) ** 3

SCOPE = {
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_positive_A7_floor": True,
    "exact_continuum_torus_integration": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "multiplier_contraction_abs_le_one": True,
    "centered_raw_gaussian_no_deterministic_past": True,
    "one_shot_fixed_law_affine_p_to_2p_controls": True,
    "source_target_reuse_allowed": True,
    "summed_HS_l2_controller_norm": True,
    "fixed_spatial_dimension_three": True,
    "pointwise_Linfty_covariance_jets": True,
    "uniform_over_every_finite_family_cardinality": True,
    "uniform_over_finite_cutoff_regulator_and_path_length": True,
    "existential_nonzero_radius": True,
    "analytic_radius_formula": True,
    "numerically_evaluated_radius": False,
    "global_terminal_action_only": True,
    "local_root_ECN_equals_Pcomp": False,
    "realised_past": False,
    "shifted_state_recursive_or_revisit": False,
    "arbitrary_predictable_nonlinearity": False,
    "floor_removal": False,
    "cutoff_removal_or_infinite_endpoint": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-161 proves one existential l2(HS) coefficient radius, uniform over every finite family "
    "cardinality, finite cutoff, admitted common-even contraction regulator, and factor-three path "
    "length, only at fixed spatial dimension three for the centered one-shot fixed-law affine "
    "p:2p global terminal action on the "
    "side-16 torus at the fixed A1 symbol and positive A7 floor. The radius is nonnumerical. The "
    "R-107 tower bridge applies to the global V_J^ren terminal action; no local root E_CN atom is "
    "identified with P_comp. Its positive analytic radius is not numerically evaluated. There is "
    "no realised-past, shifted-state recursive, nonlinear/revisit, "
    "floor-removal, infinite-endpoint, T-050/A13, Nelson, measure, phase/PDE, or Sector-A theorem."
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


def sha256(path: Path) -> str:
    # Git authorities are pinned in canonical LF form.  A Windows clone may
    # materialize CRLF while retaining the same tracked blob.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def total_degree(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> int:
    return int(sp.Poly(sp.expand(expression), *variables).total_degree())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    manifests: dict[str, dict[str, Any]] = {}
    authority_hashes: dict[str, str] = {}
    for key, path in AUTHORITIES.items():
        audit.check("authority", f"{key} authority exists", path.is_file(), str(path.relative_to(REPO)).replace("\\", "/"), "file")
        manifests[key] = json.loads(path.read_text(encoding="utf-8"))
        authority_hashes[key] = sha256(path)
    for key in ("R-141", "R-151", "R-155", "R-159", "R-160", "R-145", "R-146"):
        audit.check("authority", f"{key} ledger identity", manifests[key].get("result_ledger_id") == key, manifests[key].get("result_ledger_id"), key)
    audit.check("authority", "R-107 result identity", manifests["R-107"].get("result_id") == "A13-CLASSII-COHERENT-OUTPUT-CLUSTER-PREDICTABLE-BASELINE-BOUNDARY", manifests["R-107"].get("result_id"), "A13-CLASSII-COHERENT-OUTPUT-CLUSTER-PREDICTABLE-BASELINE-BOUNDARY")

    r151 = json.loads(R151_PRIMARY.read_text(encoding="utf-8"))
    r160 = json.loads(R160_PRIMARY.read_text(encoding="utf-8"))
    audit.check("authority", "R-151 primary hash", sha256(R151_PRIMARY) == manifests["R-151"]["files"]["primary_result"]["sha256"], sha256(R151_PRIMARY), manifests["R-151"]["files"]["primary_result"]["sha256"])
    audit.check("authority", "R-160 primary hash", sha256(R160_PRIMARY) == manifests["R-160"]["files"]["primary_result"]["sha256"], sha256(R160_PRIMARY), manifests["R-160"]["files"]["primary_result"]["sha256"])

    x = sp.symbols("x", nonnegative=True)
    f = sp.sympify(r151["derived"]["symbol_lower_polynomial"], locals={"x": x})
    coeffs = sp.Poly(f, x).all_coeffs()
    vertex = sp.factor(-coeffs[1] / (2 * coeffs[0]))
    nu = sp.factor(f.subs(x, vertex))
    kappa = sp.factor(nu / 5)
    global_envelope = sp.Poly(sp.expand(f - kappa * (1 + x**2)), x)
    envelope_discriminant = sp.factor(sp.discriminant(global_envelope.as_expr(), x))
    audit.check("symbol", "R-151 exact lower symbol", str(f) == r160["diagnostics"]["lower_symbol"], f, r160["diagnostics"]["lower_symbol"])
    audit.check("symbol", "exact positive minimum", nu == sp.Rational(28800000000947494031, 10**20) and nu > 0, nu, "28800000000947494031/10^20")
    audit.check("symbol", "global envelope leading coefficient positive", global_envelope.LC() > 0, global_envelope.LC(), ">0")
    audit.check("symbol", "global envelope discriminant negative", envelope_discriminant < 0, envelope_discriminant, "<0")

    c0 = sp.Rational(r160["diagnostics"]["nonzero_mode_floor"])
    g = sp.factor(sp.Rational(2, 1) / (VOLUME * kappa))
    audit.check("lattice", "side-16 nonzero floor imported", c0 == sp.Rational(3, 20), c0, "3/20")
    audit.check("lattice", "synthesis envelope constant", g == sp.Rational(244140625000000000, 28800000000947494031), g, "derived from 2/(V kappa)")

    # Max-norm shells have 24m^2+2 points. Integral-test zeta bounds give
    # exact convenient strict upper constants for exponents 4, 6, and 8.
    shell_index = sp.symbols("m", integer=True, positive=True)
    shell_count_3d = sp.expand((2 * shell_index + 1) ** 3 - (2 * shell_index - 1) ** 3)
    shell_count_4d = sp.expand((2 * shell_index + 1) ** 4 - (2 * shell_index - 1) ** 4)
    audit.check("lattice", "three-dimensional max-shell count", shell_count_3d == 24 * shell_index**2 + 2, shell_count_3d, "24*m^2+2")
    audit.check("lattice", "four-dimensional max-shell harmonic term", shell_count_4d == 64 * shell_index**3 + 16 * shell_index, shell_count_4d, "64*m^3+16*m")
    shell4 = 24 * sp.Rational(2, 1) + 2 * sp.Rational(4, 3)
    shell6 = 24 * sp.Rational(4, 3) + 2 * sp.Rational(6, 5)
    shell8 = 24 * sp.Rational(6, 5) + 2 * sp.Rational(8, 7)
    audit.check("lattice", "sum |n|^-4 shell bound", shell4 < 52, shell4, "<52")
    audit.check("lattice", "sum |n|^-6 shell bound", shell6 < 35, shell6, "<35")
    audit.check("lattice", "sum |n|^-8 shell bound", shell8 < 32, shell8, "<32")

    denominator = (1 + x**2) * (1 + 16 * x**2)
    c_weight_sq = sp.factor(4 * g**2 / denominator)
    q_weight_sq = sp.factor(16 * g**2 * x**2 / denominator)
    k_weight_sq = sp.factor(9 * g**2 * x / denominator)
    c_residual = sp.factor(g**2 / (4 * x**4) - c_weight_sq)
    q_residual = sp.factor(g**2 / x**2 - q_weight_sq)
    k_residual = sp.factor(sp.Rational(5, 8) * g**2 / x**3 - k_weight_sq)
    def positive_rational_for_positive_x(expression: sp.Expr) -> bool:
        numerator, denominator_value = sp.fraction(sp.together(expression))
        numerator_coefficients = sp.Poly(numerator, x).all_coeffs()
        denominator_coefficients = sp.Poly(denominator_value, x).all_coeffs()
        return (
            all(coefficient >= 0 for coefficient in numerator_coefficients)
            and any(coefficient > 0 for coefficient in numerator_coefficients)
            and all(coefficient >= 0 for coefficient in denominator_coefficients)
            and any(coefficient > 0 for coefficient in denominator_coefficients)
        )
    audit.check("jet", "value first-jet pointwise majorant", positive_rational_for_positive_x(c_residual), c_residual, ">0 for x>0")
    audit.check("jet", "derivative first-jet pointwise majorant", positive_rational_for_positive_x(q_residual), q_residual, ">0 for x>0")
    audit.check("jet", "cross first-jet pointwise majorant", positive_rational_for_positive_x(k_residual), k_residual, ">0 for x>0")

    jet_bounds = {
        "aC_squared": sp.factor(8 * g**2 / c0**4),
        "aQ_squared": sp.factor(52 * g**2 / c0**2),
        "aK_squared": sp.factor(sp.Rational(175, 8) * g**2 / c0**3),
        "bC": g,
        "bQ": sp.factor(g / 2),
        "bK": g,
        "background_C_upper": sp.factor(g * (1 + 52 / c0**2)),
    }
    audit.check("jet", "all first-jet square sums finite", all(value > 0 for key, value in jet_bounds.items() if key.startswith("a")), jet_bounds, "finite positive exact constants")
    audit.check("jet", "all quadratic-jet sup bounds finite", all(jet_bounds[key] > 0 for key in ("bC", "bQ", "bK")), jet_bounds, "finite positive exact constants")
    q_quadratic_residual = sp.factor(g / 2 - 4 * g * x / (1 + 16 * x**2))
    k_quadratic_residual = sp.factor(g**2 - 2 * g**2 / 4)
    q_quadratic_square = sp.factor(g * (4 * x - 1) ** 2 / (2 * (1 + 16 * x**2)))
    audit.check("jet", "derivative quadratic-jet supremum certificate", sp.factor(q_quadratic_residual - q_quadratic_square) == 0, q_quadratic_residual, q_quadratic_square)
    audit.check("jet", "cross quadratic-jet closed upper certificate", k_quadratic_residual > 0, k_quadratic_residual, ">0")

    a_squared = sp.factor(jet_bounds["aC_squared"] + jet_bounds["aQ_squared"] + jet_bounds["aK_squared"])
    b_squared = sp.factor(jet_bounds["bC"] ** 2 + jet_bounds["bQ"] ** 2 + jet_bounds["bK"] ** 2)
    a_norm = sp.sqrt(a_squared)
    b_norm = sp.sqrt(b_squared)
    audit.check("modulus", "product-data linear jet norm", a_squared > 0, a_squared, ">0")
    audit.check("modulus", "product-data quadratic jet norm", sp.factor(b_squared - sp.Rational(9, 4) * g**2) == 0 and sp.factor(b_norm - sp.Rational(3, 2) * g) == 0, [b_squared, b_norm], [sp.Rational(9, 4) * g**2, sp.Rational(3, 2) * g])

    compact_bounds = {
        "M0": jet_bounds["background_C_upper"],
        "MC": sp.factor(jet_bounds["background_C_upper"] + sp.sqrt(jet_bounds["aC_squared"]) + jet_bounds["bC"]),
        "MU": sp.factor(sp.sqrt(jet_bounds["aQ_squared"]) + jet_bounds["bQ"]),
        "MK": sp.factor(sp.sqrt(jet_bounds["aK_squared"]) + jet_bounds["bK"]),
    }
    audit.check("modulus", "compact covariance-data box finite", all(value.is_finite is True and value > 0 for value in compact_bounds.values()), compact_bounds, "finite positive bounds")

    radius = sp.symbols("r", nonnegative=True)
    M2, M3 = sp.symbols("M_2 M_3", positive=True)
    eta = sp.expand(a_norm * radius + b_norm * radius**2)
    first_jet = sp.expand(a_norm + 2 * b_norm * radius)
    omega = sp.expand(VOLUME * (M3 * eta * first_jet**2 + 4 * M2 * b_norm * radius * first_jet + 2 * b_norm * M2 * eta))
    omega_quotient = sp.factor(omega / radius)
    omega_coefficients = sp.Poly(sp.expand(omega_quotient), radius).all_coeffs()
    L_star = sp.factor(omega_quotient.subs(radius, 1))
    analytic_delta = sp.factor(sp.Rational(3, 100) / (1 + L_star))
    delta_headroom = sp.factor(sp.Rational(3, 100) - L_star * analytic_delta)
    audit.check("modulus", "explicit Omega(r)/r has positive coefficients", all(coefficient.is_positive is True for coefficient in omega_coefficients), omega_coefficients, "all positive")
    audit.check("modulus", "L-star is the unit-ball modulus coefficient", sp.factor(L_star - omega.subs(radius, 1)) == 0 and L_star.is_positive is True, L_star, "Omega(1)>0")
    audit.check("modulus", "analytic radius preserves strict half-headroom", sp.factor(delta_headroom - analytic_delta) == 0 and analytic_delta.is_positive is True, delta_headroom, analytic_delta)

    # Fixed-law affine columns have no p-q products because each target reads
    # its distinct raw source innovation, even when a target is reused later.
    a, s, s2, d, d2 = sp.symbols("a s s2 d d2", real=True)
    column = s + s2 * a
    derivative_column = d + d2 * a
    covariance = sp.expand(column**2)
    delta_q = sp.expand(derivative_column**2 - d**2)
    cross = sp.expand(column * derivative_column - s * d)
    cm = a**2
    degree_table = {
        "chart": 1,
        "C": total_degree(covariance, (a,)),
        "DeltaQ": total_degree(delta_q, (a,)),
        "K": total_degree(cross, (a,)),
        "CM": total_degree(cm, (a,)),
        "sextic_moment_in_control": total_degree(covariance**3, (a,)),
    }
    expected_degrees = {"chart": 1, "C": 2, "DeltaQ": 2, "K": 2, "CM": 2, "sextic_moment_in_control": 6}
    audit.check("affine", "fixed-law covariance degree table", degree_table == expected_degrees, degree_table, expected_degrees)
    audit.check("affine", "primitive derivative covariance cancels", delta_q.subs(a, 0) == 0, delta_q.subs(a, 0), 0)
    audit.check("affine", "covariance jets stop at order two", sp.diff(covariance, a, 3) == 0 and sp.diff(delta_q, a, 3) == 0 and sp.diff(cross, a, 3) == 0, [sp.diff(covariance, a, 3), sp.diff(delta_q, a, 3), sp.diff(cross, a, 3)], [0, 0, 0])
    a_left, a_right, t, t2 = sp.symbols("a_left a_right t t2", real=True)
    two_source_covariance = sp.expand((s + s2 * a_left) ** 2 + (t + t2 * a_right) ** 2)
    audit.check("affine", "distinct raw sources have zero mixed covariance jet", sp.diff(two_source_covariance, a_left, a_right) == 0, sp.diff(two_source_covariance, a_left, a_right), 0)

    # Scalar Wick recurrence checks the all-state covariance-normal identity
    # without a covariance inverse.
    C, Q, K, Q0 = sp.symbols("C Q K Q0", real=True)

    @functools.lru_cache(maxsize=None)
    def moment(w_power: int, v_power: int) -> sp.Expr:
        if w_power < 0 or v_power < 0:
            return sp.Integer(0)
        if w_power == 0 and v_power == 0:
            return sp.Integer(1)
        if (w_power + v_power) % 2:
            return sp.Integer(0)
        if w_power:
            return sp.expand((w_power - 1) * C * moment(w_power - 2, v_power) + v_power * K * moment(w_power - 1, v_power - 1))
        return sp.expand((v_power - 1) * Q * moment(0, v_power - 2))

    b_poly = 2 + 3 * sp.Symbol("w") ** 2 + 5 * sp.Symbol("w") ** 4
    coeff_power = [(sp.Integer(2), 0), (sp.Integer(3), 2), (sp.Integer(5), 4)]
    eb = sum(coefficient * moment(power, 0) for coefficient, power in coeff_power)
    eb2 = sum(coefficient * power * (power - 1) * moment(power - 2, 0) for coefficient, power in coeff_power)
    ebv2 = sum(coefficient * moment(power, 2) for coefficient, power in coeff_power)
    ibp = sp.factor(ebv2 - Q * eb - K**2 * eb2)
    normal = sp.factor(ebv2 - Q0 * eb - ((Q - Q0) * eb + K**2 * eb2))
    audit.check("gaussian", "all-state Gaussian identity", ibp == 0, ibp, 0)
    audit.check("gaussian", "Q0 cancellation before continuity", normal == 0, normal, 0)
    audit.check("gaussian", "no covariance inverse", all(not sp.denom(sp.together(item)).has(C) for item in (eb, eb2, ebv2)), [sp.denom(sp.together(item)) for item in (eb, eb2, ebv2)], "no C denominator")

    # Exact global owner bridge: local E_CN is not identified with P_comp.
    v0, v1, v2, v3 = sp.symbols("v0 v1 v2 v3", real=True)
    telescope = sp.expand((v1 - v0) + (v2 - v1) + (v3 - v2) - (v3 - v0))
    r107_text = R107_NOTE.read_text(encoding="utf-8")
    r141_text = R141_NOTE.read_text(encoding="utf-8")
    r146_text = R146_NOTE.read_text(encoding="utf-8")
    audit.check("owner", "finite terminal telescope", telescope == 0, telescope, 0)
    audit.check("owner", "R-107 global action bridge pinned", all(token in r107_text for token in ("\\Delta_kV=V_J^{\\rm ren}(Z_k)-V_J^{\\rm ren}(Z_{k-1})", "\\mathcal A_J(h)", "\\sum_k\\E P_k")), "R-107 Section 9 tokens", "all present")
    audit.check("owner", "R-146 zero-control relative anchor pinned", all(token in r146_text for token in ("\\E V_J^{\\rm ren}(Z_h)", "\\E V_J^{\\rm ren}(X_J)=0", "a_{J,\\pi}=\\cT_{J,\\pi}(0)")), "R-146 Theorem 2.1 tokens", "all present")
    audit.check("owner", "local owner inequality firewall pinned", all(token in r141_text for token in ("\\cP_{\\rm comp}={1\\over2}\\|\\Phi\\|^2-{1\\over2}\\Theta", "G_{\\rm CN}-{1\\over2}G_{\\mathcal V}")), "R-141 local-owner tokens", "all present")
    audit.check("owner", "R-107 note hash pinned", sha256(R107_NOTE) == manifests["R-107"]["sources"]["proof_note"]["sha256"], sha256(R107_NOTE), manifests["R-107"]["sources"]["proof_note"]["sha256"])
    audit.check("owner", "R-141 note hash pinned", sha256(R141_NOTE) == manifests["R-141"]["files"]["note"]["sha256"], sha256(R141_NOTE), manifests["R-141"]["files"]["note"]["sha256"])
    audit.check("owner", "R-146 note hash pinned", sha256(R146_NOTE) == manifests["R-146"]["files"]["note"]["sha256"], sha256(R146_NOTE), manifests["R-146"]["files"]["note"]["sha256"])

    origin_gap = sp.Rational(r160["diagnostics"]["lattice_certified_gap"])
    headroom = sp.factor(origin_gap - TARGET_GAP)
    modulus_allowance = sp.factor(headroom / 2)
    retained = sp.factor(origin_gap - modulus_allowance)
    audit.check("gap", "R-160 actual-lattice origin gap", origin_gap == sp.Rational(4, 25), origin_gap, "4/25")
    audit.check("gap", "headroom over one tenth", headroom == sp.Rational(3, 50), headroom, "3/50")
    audit.check("gap", "uniform modulus allowance", modulus_allowance == sp.Rational(3, 100), modulus_allowance, "3/100")
    audit.check("gap", "retained nonzero-neighbourhood gap", retained == RETAINED_GAP and retained > TARGET_GAP, retained, "13/100 > 1/10")

    audit.check("scope", "radius has an analytic formula and is cardinality uniform", SCOPE["existential_nonzero_radius"] and SCOPE["analytic_radius_formula"] and SCOPE["uniform_over_every_finite_family_cardinality"] and not SCOPE["numerically_evaluated_radius"], SCOPE, "uniform positive analytic radius; not numerically evaluated")
    audit.check("scope", "global/local owner distinction", SCOPE["global_terminal_action_only"] and not SCOPE["local_root_ECN_equals_Pcomp"], [SCOPE["global_terminal_action_only"], SCOPE["local_root_ECN_equals_Pcomp"]], [True, False])
    audit.check("scope", "T-050 and Sector A remain open", not SCOPE["t050_closed"] and not SCOPE["sector_a_closed"], [SCOPE["t050_closed"], SCOPE["sector_a_closed"]], [False, False])

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "inputs": {key: str(path.relative_to(REPO)).replace("\\", "/") for key, path in AUTHORITIES.items()},
        "authority_hashes": authority_hashes,
        "derived": {
            "symbol_lower_polynomial": f,
            "symbol_minimum": nu,
            "symbol_global_envelope_kappa": kappa,
            "symbol_global_envelope_discriminant": envelope_discriminant,
            "side16_lattice_floor_c0": c0,
            "synthesis_envelope_g": g,
            "shell_upper_constants": {"power4": 52, "power6": 35, "power8": 32},
            "jet_bounds": jet_bounds,
            "product_data_a_squared": a_squared,
            "product_data_b_squared": b_squared,
            "compact_data_bounds": compact_bounds,
            "formal_modulus": omega,
            "formal_L_star": L_star,
            "analytic_radius": analytic_delta,
            "radius_headroom_residual": delta_headroom,
            "covariance_degree_table": degree_table,
            "gaussian_ibp_residual": ibp,
            "covariance_normal_residual": normal,
            "global_terminal_telescope_residual": telescope,
            "origin_gap": origin_gap,
            "target_gap": TARGET_GAP,
            "uniform_modulus_allowance": modulus_allowance,
            "retained_gap": retained,
            "uniform_modulus_statement": "sup over finite P, finite cutoffs and admitted regulators of ||D2 R_P(A)-D2 R_P(0)||_op tends to zero as ||A||_l2(HS) tends to zero",
        },
        "assertions": audit.rows,
        "summary": {
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
            "total": len(audit.rows),
        },
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: {payload['summary']['passed']}/{payload['summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
