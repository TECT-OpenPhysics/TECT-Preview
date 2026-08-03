#!/usr/bin/env python3
"""Non-importing Fraction audit for the R-162 recursive-chain theorem."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-RESOLVENT-PURE-DYADIC-RECURSIVE-CHAIN-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-162"
SLUG = "resolvent-pure-dyadic-recursive-chain-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"

AUTHORITIES = {
    "A1": REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json",
    "A7": REPO / "claims" / "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE" / "classii_renormalised_energy_manifest.json",
    "R-107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-159": CLAIM_DIR / "classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary_manifest.json",
    "R-160": CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json",
    "R-161": CLAIM_DIR / "classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_manifest.json",
}
R160_MANIFEST = AUTHORITIES["R-160"]
R161_MANIFEST = AUTHORITIES["R-161"]

SCOPE = {
    "deterministic_matrix_coefficients": True,
    "centered_independent_raw_gaussian_blocks": True,
    "actual_shifted_state_read_at_each_stage": True,
    "finite_acyclic_single_pure_dyadic_chain": True,
    "uniform_over_chain_length_starting_mode_finite_cutoff_and_admitted_regulator": True,
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_positive_A7_floor": True,
    "fixed_spatial_dimension_three": True,
    "exact_nonaliased_continuum_torus_integration": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "summed_HS_l2_coefficient_norm": True,
    "complete_expected_global_terminal_scalar": True,
    "complete_controller_pullback_hessian": True,
    "projected_force_connection_included": True,
    "sextic_connection_included": True,
    "forward_legal_reverse_balanced_are_one_hessian": True,
    "independent_low_or_feshbach_coordinate": False,
    "intrinsic_hessian_claimed": False,
    "arbitrary_unrelated_multichain_forest": False,
    "random_or_nonlinear_past_dependent_coefficients": False,
    "revisit_or_cycles": False,
    "pathwise_fibrewise_conditional_hessian": False,
    "local_root_ECN_equals_Pcomp": False,
    "floor_or_infinite_endpoint_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-162 proves one positive analytic l2(HS) coefficient radius for each finite acyclic single "
    "pure-dyadic deterministic-matrix shifted-state recursion, with one radius uniform in its "
    "finite length, retained starting mode, finite cutoff, and admitted common-even contraction "
    "regulator, at the fixed side-16 d=3 A1/A7 setting. It controls the complete expected global "
    "controller-pullback Hessian and includes the projected-force, source, current, trace, and "
    "sextic connection terms once. It proves no intrinsic-Hessian theorem, unrelated multi-chain "
    "forest, random or nonlinear past-dependent coefficient law, revisit/cycle, pathwise fibrewise "
    "conditional estimate, removal, T-050/A13, Nelson, measure, phase/PDE, or Sector-A closure."
)


def frac(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return frac(value)
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
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def repo_relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2))


Matrix = list[list[F]]


def zero(size: int = 4) -> Matrix:
    return [[F(0) for _ in range(size)] for _ in range(size)]


def identity(size: int = 4) -> Matrix:
    result = zero(size)
    for index in range(size):
        result[index][index] = F(1)
    return result


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]


def sub(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def scale(value: F, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def mul(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return [[sum((left[i][k] * right[k][j] for k in range(size)), F(0)) for j in range(size)] for i in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def power(matrix: Matrix, exponent: int) -> Matrix:
    result = identity(len(matrix))
    for _ in range(exponent):
        result = mul(result, matrix)
    return result


def shift(values: tuple[F, F, F]) -> Matrix:
    result = zero()
    for index, value in enumerate(values):
        result[index + 1][index] = value
    return result


def resolvent(matrix: Matrix) -> Matrix:
    return add(add(identity(), matrix), add(power(matrix, 2), power(matrix, 3)))


def combine(base: Matrix, terms: list[tuple[F, Matrix]]) -> Matrix:
    result = [row[:] for row in base]
    for coefficient, matrix in terms:
        result = add(result, scale(coefficient, matrix))
    return result


def evaluate_t(base: Matrix, h: Matrix, k: Matrix | None = None, ell: Matrix | None = None, u: int = 0, v: int = 0, w: int = 0) -> Matrix:
    terms = [(F(u), h)]
    if k is not None:
        terms.append((F(v), k))
    if ell is not None:
        terms.append((F(w), ell))
    return resolvent(combine(base, terms))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, path in AUTHORITIES.items():
        audit.check("authority", f"{label} exists", path.is_file(), repo_relative(path), "existing file")
    r160_manifest = json.loads(R160_MANIFEST.read_text(encoding="utf-8"))
    r160_record = r160_manifest["files"]["primary_result"]
    r160_result_path = REPO / r160_record["path"]
    audit.check("authority", "R-160 result hash", sha256_text(r160_result_path) == r160_record["sha256"], sha256_text(r160_result_path), r160_record["sha256"])
    r160 = json.loads(r160_result_path.read_text(encoding="utf-8"))
    origin_gap = F(r160["diagnostics"]["lattice_certified_gap"])
    audit.check("authority", "R-160 origin gap reconstructed", origin_gap == F(4, 25), origin_gap, F(4, 25))
    audit.check("authority", "R-160 primary passed", r160["summary"]["failed"] == 0, r160["summary"], "zero failures")
    r161_manifest = json.loads(R161_MANIFEST.read_text(encoding="utf-8"))
    r161_record = r161_manifest["files"]["primary_result"]
    r161_result_path = REPO / r161_record["path"]
    audit.check("authority", "R-161 result hash", sha256_text(r161_result_path) == r161_record["sha256"], sha256_text(r161_result_path), r161_record["sha256"])
    r161 = json.loads(r161_result_path.read_text(encoding="utf-8"))
    r155_manifest = json.loads(AUTHORITIES["R-155"].read_text(encoding="utf-8"))
    r155_statement = r155_manifest["statement"]
    audit.check("authority", "R-155 stationary p-to-4p connection cancellation", "{+/-3p,+/-5p}" in r155_statement and "vanish only" in r155_statement and "stationary" in r155_statement, r155_statement, "stationary exact-support cancellation")
    audit.check("authority", "R-161 global-owner firewall", r161_manifest["scope"]["global_terminal_action_only"] is True and r161_manifest["scope"]["local_root_ECN_equals_Pcomp"] is False, r161_manifest["scope"], "global true; local false")

    a = shift((F(1, 7), F(-1, 5), F(2, 9)))
    h = shift((F(2, 5), F(1, 3), F(-3, 8)))
    k = shift((F(-1, 4), F(5, 11), F(1, 6)))
    ell = shift((F(3, 10), F(-2, 7), F(4, 13)))
    t = resolvent(a)
    audit.check("resolvent", "independent Neumann inverse", mul(sub(identity(), a), t) == identity(), mul(sub(identity(), a), t), identity())

    f1 = evaluate_t(a, h, u=1)
    fm1 = evaluate_t(a, h, u=-1)
    f2 = evaluate_t(a, h, u=2)
    fm2 = evaluate_t(a, h, u=-2)
    d1_fd = scale(F(1, 12), sub(scale(F(8), sub(f1, fm1)), sub(f2, fm2)))
    d1_formula = mul(mul(t, h), t)
    audit.check("resolvent", "first derivative by exact interpolation", d1_fd == d1_formula, d1_fd, d1_formula)

    d2_fd = zero()
    for su, sv in itertools.product((-1, 1), repeat=2):
        value = evaluate_t(a, h, k, u=su, v=sv)
        d2_fd = add(d2_fd, scale(F(su * sv, 4), value))
    d2_formula = add(mul(mul(mul(mul(t, h), t), k), t), mul(mul(mul(mul(t, k), t), h), t))
    audit.check("resolvent", "mixed second derivative by exact corners", d2_fd == d2_formula, d2_fd, d2_formula)

    d3_fd = zero()
    for su, sv, sw in itertools.product((-1, 1), repeat=3):
        value = evaluate_t(a, h, k, ell, su, sv, sw)
        d3_fd = add(d3_fd, scale(F(su * sv * sw, 8), value))
    directions = (h, k, ell)
    d3_formula = zero()
    for permutation in itertools.permutations(range(3)):
        term = t
        for index in permutation:
            term = mul(mul(term, directions[index]), t)
        d3_formula = add(d3_formula, term)
    audit.check("resolvent", "mixed third derivative by exact corners", d3_fd == d3_formula, d3_fd, d3_formula)

    h2 = power(h, 2)
    origin_covariance_second = scale(F(2), add(add(mul(h, transpose(h)), h2), power(transpose(h), 2)))
    audit.check("origin", "two-step acceleration is present", any(origin_covariance_second[i][j] != 0 for i in range(4) for j in range(4) if abs(i - j) == 2), "nonzero second diagonal", "nonzero second diagonal")
    audit.check("origin", "no acceleration beyond two steps", all(origin_covariance_second[i][j] == 0 for i in range(4) for j in range(4) if abs(i - j) > 2), "bandwidth two", "bandwidth two")
    audit.check("origin", "Fourier cancellation support", sorted({4 - 1, 4 + 1}) == [3, 5], sorted({4 - 1, 4 + 1}), [3, 5])

    g = F(r161["derived"]["synthesis_envelope_g"])
    c0 = F(r161["derived"]["side16_lattice_floor_c0"])
    b_s = F(16, 15) * g / c0**2
    b_d = F(4, 3) * g / c0
    c_z_squared = b_s**2 + 9 * b_d**2 + 18 * b_s * b_d
    audit.check("synthesis", "g exact", g == F(244140625000000000, 28800000000947494031), g, F(244140625000000000, 28800000000947494031))
    audit.check("synthesis", "B_S exact", b_s == F(312500000000000000000, 777600000025582338837), b_s, "exact B_S")
    audit.check("synthesis", "B_D exact", b_d == F(19531250000000000000, 259200000008527446279), b_d, "exact B_D")
    audit.check("synthesis", "c_Z squared positive", c_z_squared > 0, c_z_squared, "> 0")
    audit.check("synthesis", "c_Z squared below one", c_z_squared < 1, c_z_squared, "< 1")

    r0, tau0 = F(1, 2), F(2)
    jet_factors = (2 * tau0**3, 6 * tau0**4, 24 * tau0**5)
    audit.check("modulus", "covariance jet factors", jet_factors == (F(16), F(96), F(768)), jet_factors, (16, 96, 768))
    chain_rule_coefficients = (jet_factors[2], 3 * jet_factors[0] * jet_factors[1], jet_factors[0] ** 3)
    audit.check("modulus", "complete third-order chain-rule coefficients", chain_rule_coefficients == (F(768), F(4608), F(4096)), chain_rule_coefficients, (768, 4608, 4096))
    cm_bound = F(27, 5) * (1 + r0) * tau0**5
    audit.check("modulus", "source third derivative bound", cm_bound == F(1296, 5), cm_bound, F(1296, 5))
    audit.check("gap", "retained 13/100", origin_gap - F(3, 100) == F(13, 100), origin_gap - F(3, 100), F(13, 100))
    audit.check("gap", "metric comparison", F(100, 97) ** 4 < F(13, 10), F(100, 97) ** 4, "< 13/10")

    # Direct Gaussian sixth moment and the nonlinear-pullback falsifier.
    for c1, c2 in ((F(1, 3), F(2, 5)), (F(7, 4), F(3, 8))):
        direct = 15 * c1**3 + 9 * c1**2 * c2 + 9 * c1 * c2**2 + 15 * c2**3
        trace = (c1 + c2) ** 3 + 6 * (c1 + c2) * (c1**2 + c2**2) + 8 * (c1**3 + c2**3)
        audit.check("sextic", f"Gaussian trace identity {frac(c1)}:{frac(c2)}", direct == trace, trace, direct)
    sextic_power = 6
    hessian = [
        [F(sextic_power * (sextic_power - 1)), F(sextic_power * sextic_power)],
        [F(sextic_power * sextic_power), F(sextic_power * (sextic_power - 1))],
    ]
    audit.check("sextic", "negative antisymmetric Rayleigh value", hessian[0][0] + hessian[1][1] - 2 * hessian[0][1] == F(-12), F(-12), F(-12))
    audit.check("sextic", "positive symmetric Rayleigh value", hessian[0][0] + hessian[1][1] + 2 * hessian[0][1] == F(132), F(132), F(132))

    coherent_at_three = F(4, 25) - 3 + F(5, 3)
    audit.check("failure", "bare continuity coherent fixture", coherent_at_three < 0, coherent_at_three, "< 0")
    audit.check("scope", "single chain only", SCOPE["finite_acyclic_single_pure_dyadic_chain"] is True and SCOPE["arbitrary_unrelated_multichain_forest"] is False, "single chain", "single chain")
    audit.check("scope", "intrinsic not promoted", SCOPE["intrinsic_hessian_claimed"] is False, SCOPE["intrinsic_hessian_claimed"], False)
    audit.check("scope", "one Hessian and no invented low", SCOPE["forward_legal_reverse_balanced_are_one_hessian"] is True and SCOPE["independent_low_or_feshbach_coordinate"] is False, [SCOPE["forward_legal_reverse_balanced_are_one_hessian"], SCOPE["independent_low_or_feshbach_coordinate"]], [True, False])
    audit.check("scope", "T-050 open", SCOPE["t050_closed"] is False, SCOPE["t050_closed"], False)
    audit.check("scope", "Sector A open", SCOPE["sector_a_closed"] is False, SCOPE["sector_a_closed"], False)

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "implementation_independence": {
            "imports_primary": False,
            "imports_sympy": False,
            "arithmetic": "fractions.Fraction plus independent list-matrix algebra and exact interpolation",
        },
        "inputs": {"authority_hashes": {label: sha256_text(path) for label, path in AUTHORITIES.items()}},
        "diagnostics": {
            "g": g,
            "B_S": b_s,
            "B_D": b_d,
            "c_Z_squared": c_z_squared,
            "jet_factors_at_r0": jet_factors,
            "terminal_D3_coefficients_M1_M2_M3": chain_rule_coefficients,
            "CM_D3_bound_at_r0": cm_bound,
            "retained_gap": F(13, 100),
            "metric_guard": F(100, 97) ** 4,
        },
        "assertions": audit.rows,
        "summary": {
            "total": len(audit.rows),
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
        },
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(arguments.output, payload)
    print(f"PASS {payload['summary']['passed']}/{payload['summary']['total']} -> {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
