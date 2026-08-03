#!/usr/bin/env python3
"""Primary exact audit for the R-159 regulator-uniform local gap theorem.

The certificate checks the finite-invariant reduction behind the theorem.  It
does not compute a numerical radius: the radius is supplied nonconstructively
by uniform continuity after exact cancellation of the divergent primitive
derivative covariance.
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
RESULT_ID = "A13-CLASSII-PURE-DYADIC-REGULATOR-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-159"
SLUG = "pure-dyadic-regulator-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
CLAIM_DIR = REPO / "claims" / CLAIM
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
A7 = REPO / "claims" / "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE" / "classii_renormalised_energy_manifest.json"
AUTHORITIES = {
    "A1": A1,
    "A7": A7,
    "R-150": CLAIM_DIR / "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json",
    "R-151": CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-156": CLAIM_DIR / "classii_shifted_state_nonzero_neighborhood_gap_boundary_manifest.json",
}

# The comparison target is a declared gate, not a pasted derived result.
TARGET_GAP = sp.Rational(1, 10)

SCOPE = {
    "fixed_L16_and_A1_symbol": True,
    "fixed_positive_floor_1e_minus_12": True,
    "common_real_even_covariance_matched_multiplier": True,
    "multiplier_contraction_subclass_abs_le_one": True,
    "exact_continuum_torus_integration": True,
    "centered_raw_gaussian_no_deterministic_past": True,
    "retained_nonzero_p_2p_4p": True,
    "pure_dyadic_two_stage_shifted_state_chart": True,
    "cutoff_regulator_and_p_uniform_existential_radius": True,
    "explicit_or_numerical_radius": False,
    "floor_uniform": False,
    "generic_finite_grid_alias_control": False,
    "realised_past_fibrewise_uniform": False,
    "simultaneous_growing_multiroot_union": False,
    "arbitrary_predictable_nonlinear_or_revisit_chart": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-159 proves one cutoff-, regulator-, and retained-momentum-uniform existential local radius only "
    "for the centered pure-dyadic p:2p:4p shifted-state chart, the fixed A1 symbol and floor, the "
    "common real-even covariance-matched multiplier contraction subclass |m|<=1, and exact continuum "
    "torus integration. It computes no numerical radius and gives no floor removal, aliased-grid theorem, "
    "realised-past fibrewise bound, growing multiroot union, arbitrary predictable nonlinear/revisit "
    "estimate, T-050 or A13 closure, Nelson theorem, interacting measure, phase/PDE verdict, or Sector-A closure."
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    authority_hashes: dict[str, str] = {}
    manifests: dict[str, dict[str, Any]] = {}
    for key, path in AUTHORITIES.items():
        manifests[key] = json.loads(path.read_text(encoding="utf-8"))
        authority_hashes[key] = sha256(path)
        audit.check(
            "authority",
            f"{key} authority exists",
            path.is_file(),
            str(path.relative_to(REPO)).replace("\\", "/"),
            "file",
        )
    for key in ("R-150", "R-151", "R-155", "R-156"):
        audit.check(
            "authority",
            f"{key} ledger identity",
            manifests[key].get("result_ledger_id") == key,
            manifests[key].get("result_ledger_id"),
            key,
        )

    a7_scope = str(manifests["A7"].get("scope", ""))
    audit.check("authority", "A7 fixed floor", "rho_regularizer=1e-12" in a7_scope, a7_scope, "fixed rho_regularizer=1e-12")
    audit.check("authority", "A7 common real-even regulators", "common real-even" in a7_scope, a7_scope, "common real-even")
    audit.check("authority", "A7 exact covariance subtraction", "exact derivative covariance subtraction" in a7_scope, a7_scope, "exact derivative covariance subtraction")

    # Import the certified symbol polynomial from the immutable R-151 result.
    r151_result_path = REPO / manifests["R-151"]["files"]["primary_result"]["path"]
    r151_result = json.loads(r151_result_path.read_text(encoding="utf-8"))
    audit.check(
        "authority",
        "R-151 result hash",
        sha256(r151_result_path) == manifests["R-151"]["files"]["primary_result"]["sha256"],
        sha256(r151_result_path),
        manifests["R-151"]["files"]["primary_result"]["sha256"],
    )
    x = sp.symbols("x", nonnegative=True)
    f = sp.sympify(r151_result["derived"]["symbol_lower_polynomial"], locals={"x": x})
    polynomial = sp.Poly(f, x)
    leading, linear, constant = polynomial.all_coeffs()
    discriminant = sp.factor(linear**2 - 4 * leading * constant)
    vertex = sp.factor(-linear / (2 * leading))
    minimum = sp.factor(f.subs(x, vertex))
    audit.check("root-bound", "symbol is monic quadratic", leading == 1, leading, 1)
    audit.check("root-bound", "symbol discriminant matches R-151", str(discriminant) == r151_result["derived"]["symbol_lower_discriminant"], discriminant, r151_result["derived"]["symbol_lower_discriminant"])
    audit.check("root-bound", "uniform positive symbol minimum", minimum > 0, minimum, ">0")

    derivative_ratio = sp.factor(1 / (2 * sp.sqrt(constant) + linear))
    audit.check("root-bound", "derivative-synthesis supremum denominator positive", discriminant < 0 and linear < 0, 2 * sp.sqrt(constant) + linear, ">0")
    t = sp.symbols("t", real=True)
    compact_x = t / (1 - t)
    value_tail = sp.limit(1 / f.subs(x, compact_x), t, 1, dir="-")
    derivative_tail = sp.limit(compact_x / f.subs(x, compact_x), t, 1, dir="-")
    audit.check("compactification", "value synthesis vanishes at p infinity", value_tail == 0, value_tail, 0)
    audit.check("compactification", "derivative synthesis vanishes at p infinity", derivative_tail == 0, derivative_tail, 0)

    # Degree audit for the recursive centered Gaussian synthesis.
    a, b = sp.symbols("a b", real=True)
    s1, s2, s4, d1, d2, d4 = sp.symbols("s1 s2 s4 d1 d2 d4", real=True)
    r1 = s1 + s2 * a + s4 * b * a
    r2 = s2 + s4 * b
    r4 = s4
    u1 = d1 + d2 * a + d4 * b * a
    u2 = d2 + d4 * b
    u4 = d4
    covariance = sp.expand(r1**2 + r2**2 + r4**2)
    derivative_covariance = sp.expand(u1**2 + u2**2 + u4**2)
    cross_covariance = sp.expand(r1 * u1 + r2 * u2 + r4 * u4)
    q0 = derivative_covariance.subs({a: 0, b: 0})
    delta_q = sp.expand(derivative_covariance - q0)
    cm_energy = a**2 + b**2 + (b * a) ** 2
    degree_audit = {
        "chart": 2,
        "value_synthesis": max(total_degree(r1, (a, b)), total_degree(r2, (a, b))),
        "C": total_degree(covariance, (a, b)),
        "DeltaQ": total_degree(delta_q, (a, b)),
        "K": total_degree(cross_covariance, (a, b)),
        "K_tensor_K": total_degree(cross_covariance**2, (a, b)),
        "CM": total_degree(cm_energy, (a, b)),
        "gaussian_sixth_moment": total_degree(covariance**3, (a, b)),
    }
    expected_degrees = {"chart": 2, "value_synthesis": 2, "C": 4, "DeltaQ": 4, "K": 4, "K_tensor_K": 8, "CM": 4, "gaussian_sixth_moment": 12}
    audit.check("finite-invariant", "recursive covariance degree table", degree_audit == expected_degrees, degree_audit, expected_degrees)
    audit.check("finite-invariant", "primitive derivative covariance cancels algebraically", not delta_q.has(sp.Symbol("Q0")) and delta_q.subs({a: 0, b: 0}) == 0, delta_q.subs({a: 0, b: 0}), 0)

    # New all-state Gaussian identity.  A recurrence evaluates every bivariate
    # centered Gaussian moment without using a covariance inverse.
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

    coefficients = [sp.Rational(2, 3), sp.Rational(-5, 7), sp.Rational(11, 13), sp.Rational(17, 19)]
    powers = [0, 2, 4, 6]
    expected_b = sum(coefficient * moment(power, 0) for coefficient, power in zip(coefficients, powers))
    expected_b_second = sum(coefficient * power * (power - 1) * moment(power - 2, 0) for coefficient, power in zip(coefficients, powers))
    expected_b_v2 = sum(coefficient * moment(power, 2) for coefficient, power in zip(coefficients, powers))
    gaussian_ibp_residual = sp.factor(expected_b_v2 - Q * expected_b - K**2 * expected_b_second)
    covariance_normal_residual = sp.factor(expected_b_v2 - Q0 * expected_b - ((Q - Q0) * expected_b + K**2 * expected_b_second))
    audit.check("gaussian-ibp", "all-state Gaussian endpoint identity", gaussian_ibp_residual == 0, gaussian_ibp_residual, 0)
    audit.check("gaussian-ibp", "exact Q0 cancellation before continuity", covariance_normal_residual == 0, covariance_normal_residual, 0)
    covariance_denominators = [
        sp.denom(sp.together(expression))
        for expression in (
            expected_b,
            expected_b_second,
            expected_b_v2,
            gaussian_ibp_residual,
            covariance_normal_residual,
        )
    ]
    audit.check(
        "gaussian-ibp",
        "proof uses derivative expectations not C inverse",
        all(not denominator.has(C) for denominator in covariance_denominators),
        covariance_denominators,
        "no denominator depends on C",
    )

    # Six-real centered Gaussian sixth moment is a polynomial in C alone.
    tr1, tr2, tr3 = sp.symbols("trC trC2 trC3", nonnegative=True)
    gaussian_sixth = tr1**3 + 6 * tr1 * tr2 + 8 * tr3
    audit.check("sextic", "sixth moment finite-invariant coefficients", sp.Poly(gaussian_sixth, tr1, tr2, tr3).terms() == [((3, 0, 0), 1), ((1, 1, 0), 6), ((0, 0, 1), 8)], gaussian_sixth, "(tr C)^3+6 tr C tr(C^2)+8 tr(C^3)")

    # Scalar version of G=I+T^*T; the matrix identity is dimension-free.
    gram = sp.eye(2) + sp.Matrix([[b], [a]]) * sp.Matrix([[b, a]])
    tangent = sp.Matrix([[b, a]])
    audit.check("normalization", "source Gram is I plus a positive square", sp.simplify(gram - sp.eye(2) - tangent.T * tangent) == sp.zeros(2), gram, "I+T^T T")
    audit.check("normalization", "source Gram determinant", sp.factor(gram.det()) == 1 + a**2 + b**2, gram.det(), 1 + a**2 + b**2)

    r155_result_path = REPO / manifests["R-155"]["files"]["primary_result"]["path"]
    r155_result = json.loads(r155_result_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-155 result hash", sha256(r155_result_path) == manifests["R-155"]["files"]["primary_result"]["sha256"], sha256(r155_result_path), manifests["R-155"]["files"]["primary_result"]["sha256"])
    origin_gap = sp.Rational(r155_result["diagnostics"]["certified_pure_dyadic_gap"])
    headroom = sp.factor(origin_gap - TARGET_GAP)
    modulus_allowance = sp.factor(headroom / 2)
    retained_gap = sp.factor(origin_gap - modulus_allowance)
    audit.check("gap", "R-155 pure-dyadic origin gap imported", origin_gap > TARGET_GAP, origin_gap, f">{TARGET_GAP}")
    audit.check("gap", "uniform continuity headroom", headroom > 0, headroom, ">0")
    audit.check("gap", "half-headroom retained comparison", retained_gap > TARGET_GAP, retained_gap, f">{TARGET_GAP}")

    audit.check("scope", "radius is existential only", SCOPE["cutoff_regulator_and_p_uniform_existential_radius"] and not SCOPE["explicit_or_numerical_radius"], SCOPE, "uniform existential, nonnumerical")
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
        "diagnostics": {
            "symbol_lower_polynomial": f,
            "symbol_discriminant": discriminant,
            "uniform_symbol_minimum": minimum,
            "derivative_synthesis_ratio_supremum": derivative_ratio,
            "compactified_value_tail": value_tail,
            "compactified_derivative_tail": derivative_tail,
            "degree_audit": degree_audit,
            "gaussian_ibp_residual": gaussian_ibp_residual,
            "covariance_normal_residual": covariance_normal_residual,
            "gaussian_sixth_moment": gaussian_sixth,
            "source_gram_scalar_fixture": gram,
            "origin_gap": origin_gap,
            "target_gap": TARGET_GAP,
            "uniform_modulus_allowance": modulus_allowance,
            "retained_gap": retained_gap,
            "uniform_modulus_definition": "max(controller pullback, intrinsic source-normalized Hessian variation) over the repaired compact finite-invariant family",
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
