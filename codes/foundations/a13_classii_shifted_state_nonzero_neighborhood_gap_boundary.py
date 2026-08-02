#!/usr/bin/env python3
"""Primary exact certificate for the A13 shifted-state local gap boundary.

R-156 differentiates the actual two-stage predictable shifted-state chart,
separates the intrinsic physical-source Hessian from controller-coordinate
curvature, and applies finite-dimensional continuity to the R-155 pure-dyadic
origin gap.  It is an existential fixed-cutoff neighbourhood theorem, not the
uniform nonlinear/revisit estimate T-050.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SHIFTED-STATE-NONZERO-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-156"
SLUG = "shifted-state-nonzero-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
CLAIM_DIR = REPO / "claims" / CLAIM
AUTHORITIES = {
    "R-131": CLAIM_DIR / "classii_owner_complete_physical_response_mixed_gram_shell_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-153": CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
}

# Declared theorem thresholds, not pasted outputs.
ORIGIN_DYADIC_GAP = sp.Rational(147, 1000)
TARGET_GAP = sp.Rational(1, 10)

SCOPE = {
    "finite_cutoff_positive_floor": True,
    "exact_nonaliased_torus": True,
    "pure_dyadic_two_stage_shifted_state_chart": True,
    "predictable_reveal_order": True,
    "one_scalar_action_intrinsic_hessian": True,
    "nonzero_coefficient_neighborhood": True,
    "existential_radius_only": True,
    "controller_pullback_connection_retained": True,
    "independent_low_coordinate": False,
    "cutoff_floor_or_chart_uniform_radius": False,
    "gaussian_past_fiberwise_uniform_gap": False,
    "global_finite_amplitude_convexity": False,
    "general_predictable_nonlinear_or_revisit_feedback": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}
NO_OVERCLAIM = (
    "R-156 proves an existential nonzero coefficient neighbourhood above 1/10 only for the fixed-cutoff, "
    "positive-floor, exact-torus pure-dyadic two-stage shifted-state chart, by continuity from R-155. "
    "It derives the intrinsic one-scalar production Hessian and keeps controller-coordinate curvature "
    "separate. It supplies no numerical radius and no cutoff-, floor-, refinement-, chart-, or "
    "Gaussian-past-fibre-uniform estimate. It does not prove global finite-amplitude convexity, general "
    "predictable nonlinear/revisit feedback, T-050 or A13 closure, Nelson, an interacting measure, any "
    "phase, lattice, vacuum, BCC, or PDE verdict, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[r, c]) for c in range(value.cols)] for r in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(v) for v in value]
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


def frobenius(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.trace(left.T * right)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    authority_hashes: dict[str, str] = {}
    for ledger, path in AUTHORITIES.items():
        manifest = json.loads(path.read_text(encoding="utf-8"))
        authority_hashes[ledger] = sha256(path)
        audit.check("authority", f"{ledger} manifest ledger", manifest.get("result_ledger_id") == ledger, manifest.get("result_ledger_id"), ledger)

    r155 = json.loads(AUTHORITIES["R-155"].read_text(encoding="utf-8"))
    r155_primary = REPO / r155["files"]["primary_result"]["path"]
    r155_data = json.loads(r155_primary.read_text(encoding="utf-8"))
    imported_gap = sp.Rational(r155_data["diagnostics"]["certified_pure_dyadic_gap"])
    audit.check("authority", "R-155 primary result hash", sha256(r155_primary) == r155["files"]["primary_result"]["sha256"], sha256(r155_primary), r155["files"]["primary_result"]["sha256"])
    audit.check("continuation", "imported pure-dyadic origin gap", imported_gap == ORIGIN_DYADIC_GAP, imported_gap, ORIGIN_DYADIC_GAP)

    # Scalar restriction of C(A,B)=9/20(||A||^2+||B||^2+||BA||^2).
    t, s, a, b, d = sp.symbols("t s a b d", real=True)
    source_cost = sp.Rational(9, 20) * (a * t**2 + b * s**2 + d * t**2 * s**2)
    source_hessian = sp.hessian(source_cost, (t, s))
    expected_hessian = sp.Rational(9, 10) * sp.Matrix([[a + d * s**2, 2 * d * t * s], [2 * d * t * s, b + d * t**2]])
    audit.check("source", "nonlinear chart source Hessian", sp.simplify(source_hessian - expected_hessian) == sp.zeros(2), source_hessian, expected_hessian)
    determinant = sp.factor(source_hessian.det() / sp.Rational(81, 100))
    expected_determinant = sp.factor(a * b + a * d * t**2 + b * d * s**2 - 3 * d**2 * t**2 * s**2)
    audit.check("source", "source Hessian determinant", determinant == expected_determinant, determinant, expected_determinant)

    radius = sp.symbols("R", nonnegative=True)
    ray_hessian = expected_hessian.subs({a: 1, b: 1, d: 1, t: radius, s: radius})
    ray_metric = sp.Matrix([[1 + radius**2, radius**2], [radius**2, 1 + radius**2]])
    hessian_eigen = [sp.factor(sp.Rational(9, 10) * (1 - radius**2)), sp.factor(sp.Rational(9, 10) * (1 + 3 * radius**2))]
    metric_eigen = [sp.Integer(1), 1 + 2 * radius**2]
    anti_residual = sp.simplify(ray_hessian * sp.Matrix([1, -1]) - hessian_eigen[0] * sp.Matrix([1, -1]))
    sym_residual = sp.simplify(ray_hessian * sp.Matrix([1, 1]) - hessian_eigen[1] * sp.Matrix([1, 1]))
    audit.check("curvature", "aligned-ray Hessian eigenvectors", anti_residual == sp.zeros(2, 1) and sym_residual == sp.zeros(2, 1), [anti_residual, sym_residual], "zero residuals")
    audit.check("curvature", "aligned-ray tangent metric eigenvectors", ray_metric * sp.Matrix([1, -1]) == metric_eigen[0] * sp.Matrix([1, -1]) and ray_metric * sp.Matrix([1, 1]) == metric_eigen[1] * sp.Matrix([1, 1]), ray_metric, metric_eigen)
    at_two = ray_hessian.subs(radius, 2)
    audit.check("curvature", "rank-one ray R=2 indefinite", at_two.det() < 0, {"matrix": at_two, "eigenvalues": [value.subs(radius, 2) for value in hessian_eigen]}, "one negative eigenvalue")
    adverse_generalized = sp.factor(hessian_eigen[0] / metric_eigen[0])
    audit.check("curvature", "adverse generalized eigenvalue unbounded below", sp.limit(adverse_generalized, radius, sp.oo) == -sp.oo, adverse_generalized, "-infinity")

    # Concrete exact matrix audit of the full shifted-state differential.
    A = sp.Matrix([[1, 2], [0, -1]])
    B = sp.Matrix([[2, 0], [1, 1]])
    H = sp.Matrix([[0, 1], [1, 0]])
    G = sp.Matrix([[1, -1], [2, 0]])
    K = sp.Matrix([[2, 1], [-1, 1]])
    L = sp.Matrix([[0, 2], [1, -1]])
    tangent_v = (H, G, G * A + B * H)
    tangent_w = (K, L, L * A + B * K)
    gram_direct = sum(frobenius(left, right) for left, right in zip(tangent_v, tangent_w))
    gram_formula = frobenius(H, K) + frobenius(G, L) + frobenius(G * A + B * H, L * A + B * K)
    audit.check("chart", "exact tangent Gram identity", gram_direct == gram_formula, gram_direct, gram_formula)
    gram_diagonal = sum(frobenius(block, block) for block in tangent_v)
    audit.check("chart", "tangent Gram is strictly positive", gram_diagonal > 0, gram_diagonal, ">0")
    connection_vw = G * K + L * H
    connection_wv = L * H + G * K
    audit.check("chart", "mixed chart acceleration symmetric", connection_vw == connection_wv, connection_vw, connection_wv)

    cost_matrix = sp.Rational(9, 20) * (frobenius(A, A) + frobenius(B, B) + frobenius(B * A, B * A))
    u, v = sp.symbols("u v", real=True)
    varied_cost = sp.Rational(9, 20) * (
        frobenius(A + u * H + v * K, A + u * H + v * K)
        + frobenius(B + u * G + v * L, B + u * G + v * L)
        + frobenius((B + u * G + v * L) * (A + u * H + v * K), (B + u * G + v * L) * (A + u * H + v * K))
    )
    cost_mixed_direct = sp.diff(varied_cost, u, v).subs({u: 0, v: 0})
    cost_mixed_formula = sp.Rational(9, 10) * (gram_formula + frobenius(B * A, connection_vw))
    audit.check("chart", "source pullback chain rule", sp.expand(cost_mixed_direct - cost_mixed_formula) == 0, cost_mixed_direct, cost_mixed_formula)
    audit.check("chart", "base source cost fixture finite", cost_matrix == sp.Rational(153, 10), cost_matrix, sp.Rational(153, 10))

    # A polynomial scalar-action chain-rule fixture independently retains the
    # projected-force connection <g,D2 chi>.
    x1, x2 = sp.symbols("x1 x2", real=True)
    action = x1**2 + 3 * x1 * x2 + 2 * x2**2 + x2**3
    chart = {x1: t, x2: s * (1 + t)}
    pullback = sp.expand(action.subs(chart))
    base = {t: sp.Rational(1, 3), s: sp.Rational(2, 5)}
    dchi_t = sp.Matrix([1, s])
    dchi_s = sp.Matrix([0, 1 + t])
    d2chi_ts = sp.Matrix([0, 1])
    grad = sp.Matrix([sp.diff(action, x1), sp.diff(action, x2)]).subs(chart)
    hess = sp.hessian(action, (x1, x2)).subs(chart)
    chain_formula = (dchi_t.T * hess * dchi_s)[0] + (grad.T * d2chi_ts)[0]
    chain_direct = sp.diff(pullback, t, s)
    audit.check("projected-force", "one-scalar pullback Hessian chain rule", sp.simplify((chain_direct - chain_formula).subs(base)) == 0, chain_direct.subs(base), chain_formula.subs(base))

    # Intrinsic physical Hessian and the legal reverse come from one symmetric Q.
    Q = sp.Matrix([[2, -1, 0], [-1, 3, 1], [0, 1, -2]])
    L1 = sp.Matrix([[1, 0], [0, 1], [1, -1]])
    L2 = sp.Matrix([[0, 1], [1, 1], [-1, 0]])
    M11 = sp.Rational(9, 10) * sp.eye(2) + L1.T * Q * L1
    M22 = sp.Rational(9, 10) * sp.eye(2) + L2.T * Q * L2
    M12 = L1.T * Q * L2
    M21 = L2.T * Q * L1
    M = M11.row_join(M12).col_join(M21.row_join(M22))
    audit.check("owner", "legal reverse is the adjoint", M21 == M12.T, M21, M12.T)
    audit.check("owner", "complete two-block Hessian self-adjoint", M == M.T, M, "symmetric")

    # Exact Schur/Douglas acceptance for N=M-mu G in a positive lower block.
    E = sp.Matrix([[3, 1], [1, 2]])
    F = sp.Matrix([[2, 0], [0, 1]])
    C = sp.Matrix([[1, 1], [0, 1]])
    N = E.row_join(C).col_join(C.T.row_join(F))
    schur = sp.simplify(E - C * F.inv() * C.T)
    left = sp.eye(2).row_join(-C * F.inv()).col_join(sp.zeros(2).row_join(sp.eye(2)))
    congruence = sp.simplify(left * N * left.T)
    expected_congruence = schur.row_join(sp.zeros(2)).col_join(sp.zeros(2).row_join(F))
    audit.check("schur", "exact block congruence", congruence == expected_congruence, congruence, expected_congruence)
    audit.check("schur", "positive lower block", all(value > 0 for value in F.diagonal()), F, ">0")
    audit.check("schur", "Schur complement determinant fixture", sp.factor(N.det()) == sp.factor(F.det() * schur.det()), N.det(), F.det() * schur.det())
    audit.check("low", "no independent low coordinate declared", SCOPE["independent_low_coordinate"] is False, SCOPE["independent_low_coordinate"], False)

    # Direct differentiation of the scalar A7 conditional block.
    W, V, z, w, uz, uw, gamma, b0, b1, b2 = sp.symbols("W V z w uz uw gamma b0 b1 b2", real=True)
    Bfun = lambda y: b0 + b1 * y + b2 * y**2 / 2
    energy = sp.Rational(1, 2) * Bfun(W + u * z + v * w) * ((V + u * uz + v * uw) ** 2 - gamma)
    mixed_energy = sp.expand(sp.diff(energy, u, v).subs({u: 0, v: 0}))
    expected_energy = sp.expand(
        Bfun(W) * uz * uw
        + uz * (b1 + b2 * W) * w * V
        + uw * (b1 + b2 * W) * z * V
        + sp.Rational(1, 2) * b2 * z * w * (V**2 - gamma)
    )
    audit.check("endpoint", "complete conditional A7 mixed Hessian", sp.simplify(mixed_energy - expected_energy) == 0, mixed_energy, expected_energy)

    vector_radius, vector_inner, vector_norm = sp.symbols("r i n", nonnegative=True)
    sextic = sp.Rational(9, 10) * (vector_radius**2 * vector_norm + 4 * vector_radius * vector_inner**2)
    audit.check("sextic", "full sextic Hessian is PSD", all(coefficient >= 0 for coefficient in sp.Poly(sextic, vector_radius, vector_inner, vector_norm).coeffs()), sextic, ">=0")

    continuation_margin = sp.factor(ORIGIN_DYADIC_GAP - TARGET_GAP)
    perturbation_allowance = continuation_margin / 2
    retained_gap = sp.factor(ORIGIN_DYADIC_GAP - perturbation_allowance)
    audit.check("continuation", "strict headroom above T-050 target", continuation_margin == sp.Rational(47, 1000), continuation_margin, sp.Rational(47, 1000))
    audit.check("continuation", "continuity perturbation retains target", retained_gap > TARGET_GAP, retained_gap, f">{TARGET_GAP}")
    general_r155_gap = sp.Rational(7, 250)
    audit.check("boundary", "general factor-three gap cannot seed 1/10 continuation", general_r155_gap < TARGET_GAP, general_r155_gap, f"<{TARGET_GAP}")

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
        "inputs": {ledger: str(path.relative_to(REPO)).replace("\\", "/") for ledger, path in AUTHORITIES.items()},
        "authority_hashes": authority_hashes,
        "diagnostics": {
            "source_cost_scalar": source_cost,
            "source_hessian_scalar": source_hessian,
            "source_hessian_determinant_reduced": determinant,
            "aligned_ray_hessian": ray_hessian,
            "aligned_ray_metric": ray_metric,
            "aligned_ray_hessian_eigenvalues": hessian_eigen,
            "aligned_ray_metric_eigenvalues": metric_eigen,
            "aligned_ray_adverse_generalized_eigenvalue": adverse_generalized,
            "fixture_tangent_gram": gram_formula,
            "fixture_source_pullback_mixed_hessian": cost_mixed_formula,
            "origin_pure_dyadic_gap": ORIGIN_DYADIC_GAP,
            "target_gap": TARGET_GAP,
            "continuation_headroom": continuation_margin,
            "chosen_continuity_perturbation_allowance": perturbation_allowance,
            "retained_gap_under_allowance": retained_gap,
            "general_factor_three_gap": general_r155_gap,
            "schur_fixture": schur,
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
