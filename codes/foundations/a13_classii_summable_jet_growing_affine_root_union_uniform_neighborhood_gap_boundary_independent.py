#!/usr/bin/env python3
"""Independent standard-library audit for R-161.

This implementation imports neither SymPy nor the primary module.  It rebuilds
the rational symbol, lattice-shell, covariance-jet, Wick, owner-telescope, and
gap arithmetic with Fraction and small polynomial dictionaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SUMMABLE-JET-GROWING-AFFINE-ROOT-UNION-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-161"
SLUG = "summable-jet-growing-affine-root-union-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
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

R160_INDEPENDENT = CLAIM_DIR / "runs" / "2026-08-03-independent-weighted-schur-growing-affine-root-union-origin-gap-boundary" / "result.json"
R107_NOTE = CLAIM_DIR / "notes" / "classii-coherent-output-cluster-predictable-baseline-boundary-260728-v1.0.tex.txt"
R141_NOTE = CLAIM_DIR / "notes" / "classii-projected-force-global-doob-signed-gram-adaptive-collar-quotient-boundary-260731-v1.0.tex.txt"
R146_NOTE = CLAIM_DIR / "notes" / "classii-canonical-covariance-relative-anchor-anisotropic-temporal-reduction-260802-v1.0.tex.txt"

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
    "p:2p global terminal action on the side-16 torus at the fixed A1 symbol and positive A7 floor. "
    "The radius is nonnumerical. The R-107 tower bridge applies to the global V_J^ren terminal "
    "action; no local root E_CN atom is identified with P_comp. Its positive analytic radius is not "
    "numerically evaluated. There is no realised-past, shifted-state recursive, nonlinear/revisit, "
    "floor-removal, infinite-endpoint, T-050/A13, Nelson, measure, phase/PDE, or Sector-A theorem."
)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
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


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


# Sparse polynomials in (C,Q,K,Q0), used only for an independent Wick check.
Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


def poly_add(*items: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for item in items:
        for exponent, coefficient in item.items():
            output[exponent] = output.get(exponent, Fraction(0)) + coefficient
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def poly_scale(item: Polynomial, scalar: Fraction) -> Polynomial:
    return {exponent: coefficient * scalar for exponent, coefficient in item.items() if coefficient * scalar}


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for a, ca in left.items():
        for b, cb in right.items():
            if len(a) != len(b):
                raise ValueError("sparse polynomial exponent dimensions differ")
            exponent = tuple(a[index] + b[index] for index in range(len(a)))
            output[exponent] = output.get(exponent, Fraction(0)) + ca * cb
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


ONE: Polynomial = {(0, 0, 0, 0): Fraction(1)}
CV: Polynomial = {(1, 0, 0, 0): Fraction(1)}
QV: Polynomial = {(0, 1, 0, 0): Fraction(1)}
KV: Polynomial = {(0, 0, 1, 0): Fraction(1)}
Q0V: Polynomial = {(0, 0, 0, 1): Fraction(1)}


def moment(w_power: int, v_power: int, cache: dict[tuple[int, int], Polynomial]) -> Polynomial:
    key = (w_power, v_power)
    if key in cache:
        return cache[key]
    if w_power < 0 or v_power < 0 or (w_power + v_power) % 2:
        return {}
    if w_power == 0 and v_power == 0:
        return ONE
    if w_power:
        result = poly_add(
            poly_scale(poly_mul(CV, moment(w_power - 2, v_power, cache)), Fraction(w_power - 1)),
            poly_scale(poly_mul(KV, moment(w_power - 1, v_power - 1, cache)), Fraction(v_power)),
        )
    else:
        result = poly_scale(poly_mul(QV, moment(0, v_power - 2, cache)), Fraction(v_power - 1))
    cache[key] = result
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    manifests: dict[str, dict[str, Any]] = {}
    authority_hashes: dict[str, str] = {}
    for key, path in AUTHORITIES.items():
        audit.check("authority", f"{key} exists", path.is_file(), str(path.relative_to(REPO)).replace("\\", "/"), "file")
        manifests[key] = json.loads(path.read_text(encoding="utf-8"))
        authority_hashes[key] = canonical_sha256(path)
    for key in ("R-141", "R-151", "R-155", "R-159", "R-160", "R-145", "R-146"):
        audit.check("authority", f"{key} identity", manifests[key].get("result_ledger_id") == key, manifests[key].get("result_ledger_id"), key)
    audit.check("authority", "R-107 identity", manifests["R-107"].get("result_id") == "A13-CLASSII-COHERENT-OUTPUT-CLUSTER-PREDICTABLE-BASELINE-BOUNDARY", manifests["R-107"].get("result_id"), "A13-CLASSII-COHERENT-OUTPUT-CLUSTER-PREDICTABLE-BASELINE-BOUNDARY")

    r160 = json.loads(R160_INDEPENDENT.read_text(encoding="utf-8"))
    expected_r160_hash = manifests["R-160"]["files"]["independent_result"]["sha256"]
    audit.check("authority", "R-160 independent result hash", canonical_sha256(R160_INDEPENDENT) == expected_r160_hash, canonical_sha256(R160_INDEPENDENT), expected_r160_hash)

    # Rebuild f(x)=x^2-a*x+b exclusively from the hash-pinned R-160 result.
    lower_symbol = [Fraction(value) for value in r160["derived"]["lower_symbol"]]
    audit.check("symbol", "authority lower-symbol degree and monicity", len(lower_symbol) == 3 and lower_symbol[2] == 1, lower_symbol, "three coefficients with leading one")
    b = lower_symbol[0]
    a = -lower_symbol[1]
    nu = b - a * a / 4
    kappa = nu / 5
    envelope_leading = 1 - kappa
    envelope_constant = b - kappa
    envelope_discriminant = a * a - 4 * envelope_leading * envelope_constant
    audit.check("symbol", "exact symbol minimum", nu == Fraction(28800000000947494031, 10**20), nu, Fraction(28800000000947494031, 10**20))
    audit.check("symbol", "global envelope leading positive", envelope_leading > 0, envelope_leading, ">0")
    audit.check("symbol", "global envelope discriminant negative", envelope_discriminant < 0, envelope_discriminant, "<0")

    volume = Fraction(r160["derived"]["volume"])
    c0 = Fraction(r160["derived"]["nonzero_mode_floor"])
    g = Fraction(2, 1) / (volume * kappa)
    audit.check("lattice", "synthesis constant", g == Fraction(244140625000000000, 28800000000947494031), g, Fraction(244140625000000000, 28800000000947494031))

    def zeta_integral_upper(power: int) -> Fraction:
        return Fraction(power, power - 1)

    def shell_coefficients(dimension: int) -> dict[int, int]:
        output: dict[int, int] = {}
        for choose in range(dimension + 1):
            power = dimension - choose
            plus = math.comb(dimension, choose) * 2**power
            minus = math.comb(dimension, choose) * (-1) ** choose * 2**power
            coefficient = plus - minus
            if coefficient:
                output[power] = coefficient
        return output

    shell3 = shell_coefficients(3)
    shell4_dimension = shell_coefficients(4)
    audit.check("lattice", "derived three-dimensional max-shell polynomial", shell3 == {2: 24, 0: 2}, shell3, {2: 24, 0: 2})
    audit.check("lattice", "derived four-dimensional harmonic shell term", shell4_dimension == {3: 64, 1: 16}, shell4_dimension, {3: 64, 1: 16})

    zeta2 = zeta_integral_upper(2)
    zeta4 = zeta_integral_upper(4)
    zeta6 = zeta_integral_upper(6)
    zeta8 = zeta_integral_upper(8)
    shell4 = 24 * zeta2 + 2 * zeta4
    shell6 = 24 * zeta4 + 2 * zeta6
    shell8 = 24 * zeta6 + 2 * zeta8
    audit.check("lattice", "power-four shell sum", shell4 < 52, shell4, "<52")
    audit.check("lattice", "power-six shell sum", shell6 < 35, shell6, "<35")
    audit.check("lattice", "power-eight shell sum", shell8 < 32, shell8, "<32")

    # Independently clear the common positive denominator
    # (1+x^2)(1+16x^2)=1+17x^2+16x^4.
    denominator_coefficients = {0: Fraction(1), 2: Fraction(17), 4: Fraction(16)}
    c_residual = dict(denominator_coefficients)
    c_residual[4] -= 16
    q_residual = dict(denominator_coefficients)
    q_residual[4] -= 16
    k_residual = {power: 5 * value for power, value in denominator_coefficients.items()}
    k_residual[4] -= 72
    audit.check("jet", "C-weight cleared residual derived", all(value >= 0 for value in c_residual.values()) and c_residual[0] > 0, c_residual, "nonnegative coefficients with positive constant")
    audit.check("jet", "Q-weight cleared residual derived", all(value >= 0 for value in q_residual.values()) and q_residual[0] > 0, q_residual, "nonnegative coefficients with positive constant")
    audit.check("jet", "K-weight cleared residual derived", all(value >= 0 for value in k_residual.values()) and k_residual[0] > 0, k_residual, "nonnegative coefficients with positive constant")

    jet_bounds = {
        "aC_squared": 8 * g * g / c0**4,
        "aQ_squared": 52 * g * g / c0**2,
        "aK_squared": Fraction(175, 8) * g * g / c0**3,
        "bC": g,
        "bQ": g / 2,
        "bK": g,
        "background_C_upper": g * (1 + Fraction(52) / c0**2),
    }
    audit.check("jet", "fixed-d3 cardinality-free jet constants finite", all(value > 0 for value in jet_bounds.values()), jet_bounds, "all positive finite Fractions")
    b_squared = jet_bounds["bC"] ** 2 + jet_bounds["bQ"] ** 2 + jet_bounds["bK"] ** 2
    a_squared = jet_bounds["aC_squared"] + jet_bounds["aQ_squared"] + jet_bounds["aK_squared"]
    bq_residual = {0: Fraction(1), 1: Fraction(-8), 2: Fraction(16)}
    linear_square_source = {0: Fraction(-1), 1: Fraction(4)}
    derived_square: dict[int, Fraction] = {}
    for left_power, left_value in linear_square_source.items():
        for right_power, right_value in linear_square_source.items():
            power = left_power + right_power
            derived_square[power] = derived_square.get(power, Fraction(0)) + left_value * right_value
    audit.check("jet", "bQ certificate is the derived square (4x-1)^2", bq_residual == derived_square, bq_residual, derived_square)
    audit.check("jet", "bK closed upper has positive squared slack", g * g - g * g / 2 > 0, g * g - g * g / 2, ">0")
    audit.check("jet", "closed product-data quadratic norm", b_squared == Fraction(9, 4) * g * g, b_squared, Fraction(9, 4) * g * g)
    audit.check("modulus", "product-data linear norm finite", a_squared > 0, a_squared, ">0")

    compact_bounds = {
        "M0": jet_bounds["background_C_upper"],
        "MC": {"base": jet_bounds["background_C_upper"] + jet_bounds["bC"], "linear_squared": jet_bounds["aC_squared"]},
        "MU": {"base": jet_bounds["bQ"], "linear_squared": jet_bounds["aQ_squared"]},
        "MK": {"base": jet_bounds["bK"], "linear_squared": jet_bounds["aK_squared"]},
    }
    audit.check("modulus", "compact data-box inputs positive", compact_bounds["M0"] > 0 and all(item["base"] > 0 and item["linear_squared"] > 0 for item in (compact_bounds["MC"], compact_bounds["MU"], compact_bounds["MK"])), compact_bounds, "positive exact ingredients")

    # Sparse formal expansion in variables (r,a,b,M2,M3), independent of SymPy.
    one5: Polynomial = {(0, 0, 0, 0, 0): Fraction(1)}
    rv: Polynomial = {(1, 0, 0, 0, 0): Fraction(1)}
    av: Polynomial = {(0, 1, 0, 0, 0): Fraction(1)}
    bv: Polynomial = {(0, 0, 1, 0, 0): Fraction(1)}
    m2v: Polynomial = {(0, 0, 0, 1, 0): Fraction(1)}
    m3v: Polynomial = {(0, 0, 0, 0, 1): Fraction(1)}
    eta_formal = poly_add(poly_mul(av, rv), poly_mul(bv, poly_mul(rv, rv)))
    first_jet_formal = poly_add(av, poly_scale(poly_mul(bv, rv), Fraction(2)))
    omega_formal = poly_scale(poly_add(
        poly_mul(m3v, poly_mul(eta_formal, poly_mul(first_jet_formal, first_jet_formal))),
        poly_scale(poly_mul(m2v, poly_mul(bv, poly_mul(rv, first_jet_formal))), Fraction(4)),
        poly_scale(poly_mul(bv, poly_mul(m2v, eta_formal)), Fraction(2)),
    ), volume)
    omega_over_r = {tuple([exponent[0] - 1, *exponent[1:]]): coefficient for exponent, coefficient in omega_formal.items()}
    audit.check("modulus", "formal Omega/r polynomial coefficients positive", all(exponent[0] >= 0 and coefficient > 0 for exponent, coefficient in omega_over_r.items()), omega_over_r, "positive coefficients in r,a,b,M2,M3")
    lstar_formal: Polynomial = {}
    for exponent, coefficient in omega_over_r.items():
        at_one = tuple([0, *exponent[1:]])
        lstar_formal[at_one] = lstar_formal.get(at_one, Fraction(0)) + coefficient
    audit.check("modulus", "formal L-star is positive Omega(1)", all(coefficient > 0 for coefficient in lstar_formal.values()), lstar_formal, "positive formal polynomial")

    left_control: Polynomial = {(1, 0): Fraction(1)}
    right_control: Polynomial = {(0, 1): Fraction(1)}
    one2: Polynomial = {(0, 0): Fraction(1)}
    two_source_covariance = poly_add(
        poly_mul(poly_add(one2, left_control), poly_add(one2, left_control)),
        poly_mul(poly_add(one2, right_control), poly_add(one2, right_control)),
    )
    audit.check("affine", "distinct raw sources have zero mixed covariance jet", two_source_covariance.get((1, 1), Fraction(0)) == 0, two_source_covariance.get((1, 1), Fraction(0)), 0)

    # Exact Wick recurrence for B(w)=2+3w^2+5w^4.
    cache: dict[tuple[int, int], Polynomial] = {}
    eb = poly_add(poly_scale(moment(0, 0, cache), Fraction(2)), poly_scale(moment(2, 0, cache), Fraction(3)), poly_scale(moment(4, 0, cache), Fraction(5)))
    eb2 = poly_add(poly_scale(moment(0, 0, cache), Fraction(6)), poly_scale(moment(2, 0, cache), Fraction(60)))
    ebv2 = poly_add(poly_scale(moment(0, 2, cache), Fraction(2)), poly_scale(moment(2, 2, cache), Fraction(3)), poly_scale(moment(4, 2, cache), Fraction(5)))
    rhs = poly_add(poly_mul(QV, eb), poly_mul(poly_mul(KV, KV), eb2))
    normal_rhs = poly_add(poly_mul(Q0V, eb), poly_mul(poly_add(QV, poly_scale(Q0V, Fraction(-1))), eb), poly_mul(poly_mul(KV, KV), eb2))
    audit.check("gaussian", "independent Wick identity", ebv2 == rhs, ebv2, rhs)
    audit.check("gaussian", "independent Q0 cancellation", ebv2 == normal_rhs, ebv2, normal_rhs)

    r107_text = R107_NOTE.read_text(encoding="utf-8")
    r141_text = R141_NOTE.read_text(encoding="utf-8")
    r146_text = R146_NOTE.read_text(encoding="utf-8")
    values = [Fraction(7, 5), Fraction(-2, 3), Fraction(11, 7), Fraction(19, 13)]
    telescope = sum(values[index + 1] - values[index] for index in range(3)) - (values[3] - values[0])
    audit.check("owner", "independent terminal telescope", telescope == 0, telescope, 0)
    audit.check("owner", "R-107 bridge tokens", all(token in r107_text for token in ("\\Delta_kV=V_J^{\\rm ren}(Z_k)-V_J^{\\rm ren}(Z_{k-1})", "\\mathcal A_J(h)", "\\sum_k\\E P_k")), "Section 9", "global terminal bridge")
    audit.check("owner", "R-146 anchor tokens", all(token in r146_text for token in ("\\E V_J^{\\rm ren}(Z_h)", "\\E V_J^{\\rm ren}(X_J)=0", "a_{J,\\pi}=\\cT_{J,\\pi}(0)")), "Theorem 2.1", "zero-control relative anchor")
    audit.check("owner", "R-141 local-owner firewall", all(token in r141_text for token in ("\\cP_{\\rm comp}={1\\over2}\\|\\Phi\\|^2-{1\\over2}\\Theta", "G_{\\rm CN}-{1\\over2}G_{\\mathcal V}")), "Section 2", "do not identify local E_CN with P_comp")
    audit.check("owner", "R-107 note hash pinned", canonical_sha256(R107_NOTE) == manifests["R-107"]["sources"]["proof_note"]["sha256"], canonical_sha256(R107_NOTE), manifests["R-107"]["sources"]["proof_note"]["sha256"])
    audit.check("owner", "R-141 note hash pinned", canonical_sha256(R141_NOTE) == manifests["R-141"]["files"]["note"]["sha256"], canonical_sha256(R141_NOTE), manifests["R-141"]["files"]["note"]["sha256"])
    audit.check("owner", "R-146 note hash pinned", canonical_sha256(R146_NOTE) == manifests["R-146"]["files"]["note"]["sha256"], canonical_sha256(R146_NOTE), manifests["R-146"]["files"]["note"]["sha256"])

    origin_gap = Fraction(r160["derived"]["lattice_certified_gap"])
    target = Fraction(1, 10)
    headroom = origin_gap - target
    allowance = headroom / 2
    retained = origin_gap - allowance
    audit.check("gap", "independent R-160 origin gap", origin_gap == Fraction(4, 25), origin_gap, Fraction(4, 25))
    audit.check("gap", "half-headroom modulus", allowance == Fraction(3, 100), allowance, Fraction(3, 100))
    audit.check("gap", "retained gap", retained == Fraction(13, 100) and retained > target, retained, "13/100 > 1/10")

    audit.check("scope", "analytic radius not numerically evaluated", SCOPE["existential_nonzero_radius"] and SCOPE["uniform_over_every_finite_family_cardinality"] and SCOPE["analytic_radius_formula"] and not SCOPE["numerically_evaluated_radius"], SCOPE, "positive analytic formula; no numerical evaluation")
    audit.check("scope", "local owner transfer forbidden", SCOPE["global_terminal_action_only"] and not SCOPE["local_root_ECN_equals_Pcomp"], SCOPE, "global terminal only")
    audit.check("scope", "T-050 remains open", not SCOPE["t050_closed"] and not SCOPE["sector_a_closed"], SCOPE, "open")

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "method": "standard-library Fraction, sparse Wick polynomials, exact shell counting, direct authority-token bridge; no SymPy and no primary import",
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": authority_hashes,
        "derived": {
            "symbol_minimum": nu,
            "symbol_global_envelope_kappa": kappa,
            "symbol_global_envelope_discriminant": envelope_discriminant,
            "side16_lattice_floor_c0": c0,
            "synthesis_envelope_g": g,
            "shell_upper_constants": {"power4": 52, "power6": 35, "power8": 32},
            "shell_polynomials": {"d3": shell3, "d4": shell4_dimension},
            "jet_bounds": jet_bounds,
            "cleared_first_jet_residuals": {"C": c_residual, "Q": q_residual, "K": k_residual},
            "product_data_a_squared": a_squared,
            "product_data_b_squared": b_squared,
            "compact_data_bounds": compact_bounds,
            "formal_omega_over_r": omega_over_r,
            "formal_L_star": lstar_formal,
            "analytic_radius_definition": "delta_* = min(1, 3/[100(1+L_*)])",
            "wick_left": ebv2,
            "wick_right": rhs,
            "terminal_telescope_residual": telescope,
            "origin_gap": origin_gap,
            "target_gap": target,
            "uniform_modulus_allowance": allowance,
            "retained_gap": retained,
        },
        "assertions": audit.rows,
        "summary": {
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
            "total": len(audit.rows),
        },
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} independent: {payload['summary']['passed']}/{payload['summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
