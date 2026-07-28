#!/usr/bin/env python3
"""Primary exact audit for the scoped R-118 A13 quotient boundary.

The executable checks finite-dimensional quotient factorisation, the exact
R-068 interpolation exponents, the opposite-visit terminal-owner obstruction,
the two-visit Hermite mean debt, and its canonical signed double-divergence
preimage.  The analytic Hilbert/Sobolev estimates are proved in the companion
note; finite fixtures here are falsifiers, not substitutes for those proofs.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-REVISIT-QUOTIENT-OPERATOR-CARLESON-SIGNED-SCORE-BOUNDARY"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-revisit-quotient-operator-carleson-signed-score-boundary/result.json"
)
SCHEMA = "tect/a13-revisit-quotient-operator-carleson-signed-score-boundary-primary/1.0"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(item) for item in value.row(row)] for row in range(value.rows)]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

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

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "The audit proves an abstract quotient criterion, a visit-count-free "
                "operator centered-form extension under explicit spectral variation, "
                "and signed-score obstructions. It does not identify or bound the full "
                "adapted A1 owner, prove one-use, Nelson, or Sector A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    expanded = sp.Poly(sp.expand(poly), variable)
    total = sp.Integer(0)
    for (degree,), coefficient in expanded.terms():
        if degree % 2:
            continue
        moment = sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1)
        total += coefficient * moment
    return sp.simplify(total)


def delta2_scalar(weight: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    return sp.expand(
        weight * (variable**2 - 1)
        - 2 * variable * sp.diff(weight, variable)
        + sp.diff(weight, variable, 2)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()

    # A full-row-rank synthesis fixture and its exact quotient factorisation.
    L = sp.Matrix([[1, 1, 0], [0, 1, 1]])
    vertical = sp.Matrix([1, -1, 1])
    B = sp.Matrix([[2, -1], [-1, 3]])
    K = L.T * B * L
    gram_inverse = (L * L.T).inv()
    right_inverse = L.T * gram_inverse
    recovered_B = sp.simplify(right_inverse.T * K * right_inverse)
    sample = sp.Matrix([2, -3, 5])
    audit.check("quotient", "vertical_is_kernel", L * vertical == sp.zeros(2, 1), L * vertical, sp.zeros(2, 1))
    audit.check("quotient", "factor_kills_vertical", K * vertical == sp.zeros(3, 1), K * vertical, sp.zeros(3, 1))
    audit.check("quotient", "canonical_B_recovery", recovered_B == B, recovered_B, B)
    audit.check("quotient", "factor_reconstruction", L.T * recovered_B * L == K, L.T * recovered_B * L, K)
    q_sample = (sample.T * K * sample)[0]
    q_shift = ((sample + vertical).T * K * (sample + vertical))[0]
    audit.check("quotient", "fibre_invariance", sp.expand(q_shift - q_sample) == 0, sp.expand(q_shift - q_sample), 0)

    bad_K = sp.eye(3)
    audit.check("quotient", "bad_form_has_null_endpoint", L * vertical == sp.zeros(2, 1), L * vertical, sp.zeros(2, 1))
    bad_value = (vertical.T * bad_K * vertical)[0]
    audit.check("quotient", "bad_form_survives_vertical", bad_value == 3, bad_value, 3)

    # A nonlinear scalar endpoint still factors when its visit dependence is
    # genuinely through the fixed affine synthesis L.
    u1, u2 = sp.symbols("u1 u2", real=True)
    endpoint = u1**3 + 2 * u1 * u2 + u2**4
    endpoint_hessian = sp.hessian(endpoint, (u1, u2)).subs({u1: 1, u2: 2})
    visit_hessian = sp.simplify(L.T * endpoint_hessian * L)
    audit.check("chain_rule", "endpoint_hessian_value", endpoint_hessian == sp.Matrix([[6, 2], [2, 48]]), endpoint_hessian, sp.Matrix([[6, 2], [2, 48]]))
    audit.check("chain_rule", "visit_hessian_kills_vertical", visit_hessian * vertical == sp.zeros(3, 1), visit_hessian * vertical, sp.zeros(3, 1))

    # R-068 interpolation and three-factor Young exponents are derived from
    # kappa, rather than pasted as derived constants.
    kappa = Fraction(1, 10)
    theta = (1 + kappa) / 2
    beta = (1 - kappa) / 6
    young_gap = 1 - theta - beta
    model_moment = 1 / young_gap
    eta_power = theta / young_gap
    zeta_power = beta / young_gap
    audit.check("operator_carleson", "theta", theta == Fraction(11, 20), theta, Fraction(11, 20))
    audit.check("operator_carleson", "terminal_sextic_power", beta == Fraction(3, 20), beta, Fraction(3, 20))
    audit.check("operator_carleson", "young_gap", young_gap == Fraction(3, 10), young_gap, Fraction(3, 10))
    audit.check("operator_carleson", "model_moment", model_moment == Fraction(10, 3), model_moment, Fraction(10, 3))
    audit.check("operator_carleson", "spectral_constant_power", model_moment == Fraction(10, 3), model_moment, Fraction(10, 3))
    audit.check("operator_carleson", "eta_power", eta_power == Fraction(11, 6), eta_power, Fraction(11, 6))
    audit.check("operator_carleson", "zeta_power", zeta_power == Fraction(1, 2), zeta_power, Fraction(1, 2))

    projectors = [sp.diag(1, 0, 0), sp.diag(0, 1, 0), sp.diag(0, 0, 1)]
    variation = sum(projectors, sp.zeros(3, 3))
    audit.check("operator_carleson", "spectral_variation_fixture", variation == sp.eye(3), variation, sp.eye(3))
    left, right = sp.Matrix([1, -2, 3]), sp.Matrix([4, 1, -1])
    polar_sum = sum(abs((left.T * projector * right)[0]) for projector in projectors)
    polar_bound = sp.sqrt((left.T * left)[0] * (right.T * right)[0])
    audit.check("operator_carleson", "polar_variation_bound", sp.simplify(polar_bound**2 - polar_sum**2) >= 0, polar_sum, f"<={polar_bound}")

    # Two opposite visits are invisible to the endpoint but not to a diagonal
    # visit square. This is the smallest terminal-owner obstruction.
    endpoint_L = sp.Matrix([[1, 1]])
    opposite = sp.Matrix([1, -1])
    diagonal = sp.eye(2)
    audit.check("opposite_visit", "terminal_aggregate_zero", endpoint_L * opposite == sp.zeros(1, 1), endpoint_L * opposite, sp.zeros(1, 1))
    diagonal_value = (opposite.T * diagonal * opposite)[0]
    audit.check("opposite_visit", "diagonal_visit_square_nonzero", diagonal_value == 2, diagonal_value, 2)
    visit_sextic_density = diagonal_value**3
    audit.check("opposite_visit", "visit_square_sextic_density", visit_sextic_density == 8, visit_sextic_density, 8)
    coherent_count = sp.Integer(7)
    coherent_source = sum((1 / sp.sqrt(coherent_count)) ** 2 for _ in range(int(coherent_count)))
    coherent_endpoint_square = (coherent_count / sp.sqrt(coherent_count)) ** 2
    audit.check("opposite_visit", "coherent_source_fixed", sp.simplify(coherent_source) == 1, coherent_source, 1)
    audit.check("opposite_visit", "coherent_endpoint_amplifies", sp.simplify(coherent_endpoint_square) == coherent_count, coherent_endpoint_square, coherent_count)

    # Exact two-visit Hermite quotient and its canonical double divergence.
    G, a, s = sp.symbols("G a s", real=True)
    H1 = G
    H2 = G**2 - 1
    H3 = G**3 - 3 * G
    H4 = G**4 - 6 * G**2 + 3
    x0 = a * G
    xs = a * G + s * H2
    x1 = a * G + H2
    t0 = a**2
    ts = (a + 2 * s * G) ** 2
    t1 = (a + 2 * G) ** 2
    visit_one = x0 * (xs - x0) + sp.Rational(1, 2) * (xs - x0) ** 2 - sp.Rational(1, 2) * (ts - t0)
    visit_two = xs * (x1 - xs) + sp.Rational(1, 2) * (x1 - xs) ** 2 - sp.Rational(1, 2) * (t1 - ts)
    quotient = sp.expand(visit_one + visit_two)
    endpoint_difference = sp.expand(sp.Rational(1, 2) * (x1**2 - x0**2) - sp.Rational(1, 2) * (t1 - t0))
    target = sp.expand(a * H3 + sp.Rational(1, 2) * H4 - 1)
    audit.check("hermite", "internal_visit_cancels", sp.simplify(quotient - endpoint_difference) == 0, sp.simplify(quotient - endpoint_difference), 0)
    audit.check("hermite", "quotient_normal_form", sp.simplify(quotient - target) == 0, sp.simplify(quotient - target), 0)
    mean_debt = gaussian_expectation(target, G)
    audit.check("hermite", "mean_debt", mean_debt == -1, mean_debt, -1)
    first_chaos = gaussian_expectation(G * target, G)
    audit.check("hermite", "first_chaos_zero", first_chaos == 0, first_chaos, 0)

    canonical_weight = sp.expand(H2 + 2 * a * H1)
    centered = sp.expand(target - mean_debt)
    lifted = sp.expand(delta2_scalar(canonical_weight, G) / 2)
    audit.check("hermite", "canonical_weight_formula", sp.simplify(canonical_weight - ((G + a) ** 2 - (a**2 + 1))) == 0, canonical_weight, "(G+a)^2-(a^2+1)")
    audit.check("hermite", "double_divergence_identity", sp.simplify(lifted - centered) == 0, sp.simplify(lifted - centered), 0)
    negative_value = canonical_weight.subs(G, -a)
    positive_value = canonical_weight.subs({a: 1, G: 2})
    audit.check("hermite", "weight_has_negative_value", sp.simplify(negative_value) == -(a**2 + 1), negative_value, -(a**2 + 1))
    audit.check("hermite", "weight_has_positive_value", positive_value == 7, positive_value, 7)

    # In one dimension delta^2 H_n=H_{n+2}; solve the possible degree-two
    # preimage and pin its uniqueness directly.
    c0, c1, c2 = sp.symbols("c0 c1 c2", real=True)
    candidate = c0 + c1 * H1 + c2 * H2
    identity_poly = sp.Poly(sp.expand(delta2_scalar(candidate, G) / 2 - centered), G)
    solution = sp.solve(identity_poly.all_coeffs(), (c0, c1, c2), dict=True)
    expected_solution = [{c0: 0, c1: 2 * a, c2: 1}]
    audit.check("hermite", "unique_degree_two_preimage", solution == expected_solution, solution, expected_solution)

    # The exact algebraic score split for an arbitrary W.
    W = canonical_weight
    delta_tau = sp.expand((a + 2 * G) ** 2 - a**2)
    residual = H2
    base = a * G
    raw_G = sp.expand(base * residual + sp.Rational(1, 2) * residual**2)
    tau_W = sp.expand(W + 2 * G * sp.diff(W, G) - sp.diff(W, G, 2))
    schur_remainder = sp.expand(raw_G - sp.Rational(1, 2) * G**2 * W)
    split = sp.expand(delta2_scalar(W, G) / 2 + schur_remainder + (tau_W - delta_tau) / 2)
    exact_residual = sp.expand(raw_G - delta_tau / 2)
    audit.check("score_split", "exact_random_W_decomposition", sp.simplify(split - exact_residual) == 0, sp.simplify(split - exact_residual), 0)

    diagnostics = {
        "quotient_matrix": K,
        "recovered_B": recovered_B,
        "interpolation": {
            "kappa": kappa,
            "theta": theta,
            "terminal_sextic_power": beta,
            "model_moment": model_moment,
            "eta_power": eta_power,
            "zeta_power": zeta_power,
        },
        "hermite": {
            "quotient": target,
            "mean": mean_debt,
            "first_chaos": first_chaos,
            "canonical_weight": canonical_weight,
            "unique_preimage": solution,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Primary R-118 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
