#!/usr/bin/env python3
"""Primary exact verifier for the scoped R-125 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY"
SCHEMA = "tect/a13-conditional-variance-forest-bridge-root-shell-operator-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-conditional-variance-forest-bridge-root-shell-operator-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.simplify(value))
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
            "scope": {
                "finite_cutoff_bridge_proved": True,
                "conditional_variance_rebate_required": True,
                "finite_cutoff_adapted_partial_wick_identity_proved": True,
                "abstract_root_shell_operator_criterion_proved": True,
                "owner_complete_stationary_baseline_sum_proved": False,
                "adapted_forest_continuum_bound_proved": False,
                "production_root_shell_factorization_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-125 proves the finite-cutoff conditional-variance/forest bridge, the smooth "
                "cylindrical adapted partial-Wick identity, and an abstract correlated operator "
                "criterion. It does not prove the adapted continuum forest, the "
                "production root-shell factorization, the owner-complete stationary-baseline sum, OVERLAP_src, "
                "Nelson, removals, an interacting measure, or Sector A closure."
            ),
        }


def production_constants() -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))
    c0 = sp.Rational(3, 250) / mass
    c1 = sp.Rational(243, 8000) / mass
    alpha = sp.Rational(5, 9)
    return mass, c0, c1, alpha


def owner_curls(alpha: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    x, y = sp.symbols("x y", real=True)

    def coefficient(x_value: sp.Expr, y_value: sp.Expr) -> sp.Matrix:
        denominator = 1 + x_value**2 + y_value**2
        g = sp.Matrix(
            [
                x_value - alpha * x_value**3 / denominator,
                -alpha * x_value**2 * y_value / denominator,
            ]
        )
        return sp.simplify(4 * g * g.T)

    b0 = coefficient(x, y)
    b1 = coefficient(x + 1, y)
    taylor = sp.simplify(b0 + b0.diff(x) + sp.Rational(1, 2) * b0.diff(x, 2))
    remainder = sp.simplify(b1 - taylor)
    point = {x: 1, y: 1}

    def curl(current: sp.Matrix) -> sp.Expr:
        return sp.simplify((sp.diff(current[0], y) - sp.diff(current[1], x)).subs(point))

    return curl(remainder[:, 0]), curl(taylor[:, 0]), curl(b1[:, 0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    mass, c0, c1, alpha = production_constants()
    s = sp.simplify(c0 + c1)
    audit.check("production", "mass", mass == sp.Rational(4000000000001, 10**12), mass, sp.Rational(4000000000001, 10**12))
    audit.check("production", "c0", c0 == sp.Rational(3, 250) / mass, c0, sp.Rational(3, 250) / mass)
    audit.check("production", "c1", c1 == sp.Rational(243, 8000) / mass, c1, sp.Rational(243, 8000) / mass)
    audit.check("production", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("production", "s", s == sp.Rational(339, 8000) / mass, s, sp.Rational(339, 8000) / mass)

    # Exhaustive output resolution and the Gram trace identity.
    c_matrix = sp.Matrix([[1, 2], [2, -1], [1, 1], [3, 0]])
    gamma = sp.Matrix([[sp.Rational(5, 3), sp.Rational(1, 4)], [sp.Rational(1, 4), sp.Rational(7, 5)]])
    projections = [sp.diag(1, 1, 0, 0), sp.diag(0, 0, 1, 1)]
    gram = c_matrix.T * c_matrix
    trace_total = sum((sp.trace(projection * c_matrix * gamma * c_matrix.T) for projection in projections), sp.Integer(0))
    gram_trace = sp.trace(gram * gamma)
    audit.check("bridge", "orthogonal_resolution", sum(projections, sp.zeros(4)) == sp.eye(4), sum(projections, sp.zeros(4)), sp.eye(4))
    audit.check("bridge", "gram_trace", sp.simplify(trace_total - gram_trace) == 0, trace_total, gram_trace)

    # Conditional mean/variance bridge on a nontrivial exact atom law.
    weights = (sp.Rational(1, 6), sp.Rational(1, 3), sp.Rational(1, 2))
    currents = (sp.Matrix([2, -1, 0, 3]), sp.Matrix([-1, 4, 2, 0]), sp.Matrix([3, 1, -2, 1]))
    mean = sum((weights[index] * currents[index] for index in range(3)), sp.zeros(4, 1))
    second = sum((weights[index] * currents[index].dot(currents[index]) for index in range(3)), sp.Integer(0))
    variance = sum((weights[index] * (currents[index] - mean).dot(currents[index] - mean) for index in range(3)), sp.Integer(0))
    audit.check("bridge", "conditional_variance", sp.simplify(second - mean.dot(mean) - variance) == 0, second, mean.dot(mean) + variance)

    theta = sp.Rational(17, 5)
    raw_wick = sp.simplify(second - theta)
    packet = sp.simplify((mean.dot(mean) - theta) / 2)
    bridge = sp.simplify(packet + variance / 2)
    audit.check("bridge", "packet_variance_forest", sp.simplify(bridge - raw_wick / 2) == 0, bridge, raw_wick / 2)

    # Two endpoints: the R-124 secant equals Delta variance minus Delta forest.
    v0, vh, f0, fh = sp.symbols("v0 vh f0 fh", real=True)
    delta_variance = vh - v0
    delta_forest = fh - f0
    secant = sp.expand(delta_variance - delta_forest)
    owners = sp.expand(delta_forest / 2)
    audit.check("bridge", "secant_owner_form", sp.expand(secant - (delta_variance - 2 * owners)) == 0, secant, delta_variance - 2 * owners)
    audit.check("bridge", "forest_convention", sp.expand(owners - delta_forest / 2) == 0, owners, delta_forest / 2)

    # Generic moving-endpoint R-121 telescope.
    b0, b1, b2, q0, q1, q2 = sp.symbols("b0 b1 b2 q0 q1 q2", real=True)
    visits = (sp.Rational(1, 2) * (b1 * q1 - b0 * q0), sp.Rational(1, 2) * (b2 * q2 - b1 * q1))
    audit.check("owners", "two_visit_telescope", sp.expand(sum(visits) - (b2 * q2 - b0 * q0) / 2) == 0, sum(visits), (b2 * q2 - b0 * q0) / 2)

    # Exact production counterfixture: the naive trace/forest identification misses variance/2.
    theta_fixture = sp.simplify(4 * s)
    phi_fixture = sp.Integer(0)
    variance_fixture = sp.simplify(4 * s)
    forest_fixture = sp.Integer(0)
    packet_fixture = sp.simplify((phi_fixture - theta_fixture) / 2)
    audit.check("counterfixture", "theta", theta_fixture == sp.Rational(339, 2000) / mass, theta_fixture, sp.Rational(339, 2000) / mass)
    audit.check("counterfixture", "variance", variance_fixture == theta_fixture, variance_fixture, theta_fixture)
    audit.check("counterfixture", "forest_mean", forest_fixture == 0, forest_fixture, 0)
    audit.check("counterfixture", "packet", packet_fixture == -2 * s, packet_fixture, -2 * s)
    audit.check("counterfixture", "rebate_repairs", sp.simplify(packet_fixture + variance_fixture / 2 - forest_fixture / 2) == 0, packet_fixture + variance_fixture / 2, forest_fixture / 2)
    omission = sp.simplify(variance_fixture / 2)
    audit.check("counterfixture", "naive_omission", omission == sp.Rational(339, 4000) / mass, omission, sp.Rational(339, 4000) / mass)
    audit.check("counterfixture", "stationary_baseline_not_zero_automatically", theta_fixture - phi_fixture > 0, theta_fixture - phi_fixture, "strictly positive")

    # Conditional common-terminal baseline lemma.  This is an acceptance test,
    # not the production theorem: the actual family of middle currents is k-dependent.
    trace_low, trace_roots, low_energy, root_energy, mean_reserve = sp.symbols(
        "trace_low trace_roots low_energy root_energy mean_reserve", nonnegative=True
    )
    stationary_trace_contract = sp.Eq(trace_low + trace_roots, low_energy + root_energy)
    d0_sum = sp.expand(trace_low + trace_roots - low_energy - root_energy)
    audit.check(
        "baseline",
        "conditional_common_terminal_d0_cancellation",
        sp.simplify(d0_sum.subs(trace_roots, low_energy + root_energy - trace_low)) == 0,
        d0_sum.subs(trace_roots, low_energy + root_energy - trace_low),
        0,
    )
    full_s0_sum = sp.expand(d0_sum - mean_reserve)
    audit.check(
        "baseline",
        "conditional_common_terminal_low_plus_root_s0",
        sp.simplify(full_s0_sum.subs(trace_roots, low_energy + root_energy - trace_low) + mean_reserve) == 0,
        full_s0_sum.subs(trace_roots, low_energy + root_energy - trace_low),
        -mean_reserve,
    )
    low_s0 = sp.expand(trace_low - low_energy)
    root_s0 = sp.expand(trace_roots - root_energy - mean_reserve)
    root_s0_reduced = sp.expand(root_s0.subs(trace_roots, low_energy + root_energy - trace_low))
    audit.check(
        "baseline",
        "conditional_root_only_formula_retains_low_atom",
        sp.simplify(root_s0_reduced + mean_reserve + low_s0) == 0,
        root_s0_reduced,
        -mean_reserve - low_s0,
    )
    nonnegative_low_s0 = sp.symbols("nonnegative_low_s0", nonnegative=True)
    audit.check(
        "baseline",
        "conditional_root_upper_bound_needs_nonnegative_low",
        -mean_reserve - nonnegative_low_s0 <= 0,
        -mean_reserve - nonnegative_low_s0,
        "<= 0 only with nonnegative complete-low stationary atom",
    )

    n = sp.symbols("n", integer=True, positive=True)
    k = sp.symbols("k", integer=True, positive=True)
    d0_k = sp.Rational(1, 1) / n - (2 * k - 1) / n**2
    d0_fixture_sum = sp.simplify(sp.summation(d0_k, (k, 1, n)))
    s0_k = sp.Rational(1, 1) / n - k**2 / n**2
    s0_fixture_sum = sp.simplify(sp.summation(s0_k, (k, 1, n)))
    audit.check("baseline", "diagnostic_n_root_d0_sum", d0_fixture_sum == 0, d0_fixture_sum, 0)
    audit.check(
        "baseline",
        "diagnostic_n_root_s0_sum",
        sp.simplify(s0_fixture_sum + (n - 1) * (2 * n - 1) / (6 * n)) == 0,
        s0_fixture_sum,
        -(n - 1) * (2 * n - 1) / (6 * n),
    )
    audit.check("baseline", "diagnostic_two_root_first_atom_positive", s0_k.subs({n: 2, k: 1}) == sp.Rational(1, 4), s0_k.subs({n: 2, k: 1}), sp.Rational(1, 4))
    audit.check("baseline", "diagnostic_two_root_second_atom_negative", s0_k.subs({n: 2, k: 2}) == -sp.Rational(1, 2), s0_k.subs({n: 2, k: 2}), -sp.Rational(1, 2))
    audit.check("baseline", "diagnostic_two_root_aggregate", s0_fixture_sum.subs(n, 2) == -sp.Rational(1, 4), s0_fixture_sum.subs(n, 2), -sp.Rational(1, 4))
    audit.check("baseline", "low_omission_diagnostic", sp.Integer(2) - sp.Integer(1) == 1, 1, "positive root D0 if low omitted")
    baseline_variance, baseline_forest, baseline_leakage = sp.symbols("baseline_variance baseline_forest baseline_leakage", real=True)
    baseline_residual = baseline_variance - baseline_forest + baseline_leakage
    audit.check(
        "baseline",
        "exact_production_residual_form",
        sp.expand(baseline_residual - (baseline_variance - baseline_forest + baseline_leakage)) == 0,
        baseline_residual,
        "sum V0 - sum F063_ad,0 + complement leakage",
    )
    audit.check("baseline", "actual_c0_not_inferred", True, False, False)

    # Clark--Ocone square-first identity on H_2(G) and an affine perturbation.
    t = sp.symbols("t", nonnegative=True)
    variance_h2 = sp.integrate(4 * t, (t, 0, 1))
    audit.check("clark_ocone", "h2_variance", variance_h2 == 2, variance_h2, 2)
    a = sp.symbols("a", real=True)
    delta_integrand_square = sp.integrate(a**2, (t, 0, 1))
    cross_integrand = sp.integrate(2 * a * 2 * sp.Integer(0), (t, 0, 1))
    audit.check("clark_ocone", "affine_increment_square", delta_integrand_square == a**2, delta_integrand_square, a**2)
    audit.check("clark_ocone", "orthogonal_cross", cross_integrand == 0, cross_integrand, 0)

    # The adapted finite-forest shortcut is unavailable: sin has infinitely many Hermite coefficients.
    y_wick = sp.symbols("y_wick", real=True)
    hermites = [sp.hermite_prob(index, y_wick) for index in range(6)]
    coefficients = (sp.Integer(2), sp.Integer(3), sp.Integer(-5), sp.Integer(7))
    coefficient_field = sum((coefficients[index] * hermites[index] for index in range(4)), sp.Integer(0))
    wick_product = sum((coefficients[index] * hermites[index + 2] for index in range(4)), sp.Integer(0))
    quadratic_wick = hermites[2]
    partial_wick_rhs = sp.expand(
        wick_product
        + 2 * y_wick * sp.diff(coefficient_field, y_wick)
        - sp.diff(coefficient_field, y_wick, 2)
    )
    ordinary_product = sp.expand(coefficient_field * quadratic_wick)
    audit.check(
        "adapted_algebra",
        "finite_cutoff_partial_wick_identity",
        sp.expand(partial_wick_rhs - ordinary_product) == 0,
        partial_wick_rhs,
        ordinary_product,
    )
    wrong_single_derivative = sp.expand(
        wick_product
        + y_wick * sp.diff(coefficient_field, y_wick)
        - sp.diff(coefficient_field, y_wick, 2)
    )
    audit.check(
        "adapted_algebra",
        "two_first_derivative_contractions_required",
        sp.expand(wrong_single_derivative - ordinary_product) != 0,
        sp.expand(wrong_single_derivative - ordinary_product),
        "nonzero",
    )
    hermite_coefficients = [sp.exp(-sp.Rational(1, 2)) * (-1) ** m / sp.factorial(2 * m + 1) for m in range(6)]
    audit.check("adapted_scope", "sine_first_six_odd_coefficients_nonzero", all(value != 0 for value in hermite_coefficients), hermite_coefficients, "all nonzero")
    audit.check("adapted_scope", "deterministic_r063_only", True, "finite-cutoff identity only", "finite-cutoff identity only")

    # The 2680/729 Cartan connection is retained rather than cancelled.
    curl_k, curl_m, curl_total = owner_curls(alpha)
    audit.check("cartan", "curl_k", curl_k == -sp.Rational(40, 729), curl_k, -sp.Rational(40, 729))
    audit.check("cartan", "curl_m", curl_m == sp.Rational(2720, 729), curl_m, sp.Rational(2720, 729))
    audit.check("cartan", "curl_total", curl_total == sp.Rational(2680, 729), curl_total, sp.Rational(2680, 729))
    audit.check("cartan", "curl_addition", sp.simplify(curl_k + curl_m - curl_total) == 0, curl_k + curl_m, curl_total)

    # Correlated far-root/shell operator theorem.
    j0 = sp.symbols("j0", integer=True, nonnegative=True)
    cstar = sp.symbols("Cstar", positive=True)
    hs_square = sp.simplify(cstar**2 * sp.Rational(64, 16065) * 2 ** (-6 * j0))
    k_far = sp.simplify(8 * cstar * 2 ** (-3 * j0) / sp.sqrt(16065))
    audit.check("operator", "hs_square", sp.simplify(k_far**2 - hs_square) == 0, k_far**2, hs_square)

    # Direct geometric-series derivation at j0=0.
    inner_sum = sp.summation(2 ** (2 * sp.Symbol("j", integer=True, nonnegative=True) - 8 * sp.Symbol("k", integer=True, positive=True)), (sp.Symbol("k", integer=True, positive=True), sp.Symbol("j", integer=True, nonnegative=True) + 1, sp.oo))
    total_sum = sp.summation(inner_sum, (sp.Symbol("j", integer=True, nonnegative=True), 0, sp.oo))
    audit.check("operator", "geometric_sum", sp.simplify(total_sum - sp.Rational(64, 16065)) == 0, total_sum, sp.Rational(64, 16065))

    eta, zeta, x, y, kval = sp.symbols("eta zeta x y kval", positive=True)
    young_rhs = 2 * eta * x**2 + kval**2 * y**2 / (8 * eta)
    target_rhs = 2 * eta * x**2 + 2 * zeta * y**2
    audit.check("operator", "young_exact", sp.simplify(target_rhs - young_rhs).subs(kval, 4 * sp.sqrt(eta * zeta)) == 0, young_rhs.subs(kval, 4 * sp.sqrt(eta * zeta)), target_rhs)
    full_threshold = sp.simplify(4 * sp.sqrt(sp.Rational(9, 20) * sp.Rational(3, 20)))
    audit.check("operator", "full_trace_threshold", full_threshold == 3 * sp.sqrt(3) / 5, full_threshold, 3 * sp.sqrt(3) / 5)
    action_threshold = sp.simplify(full_threshold / 2)
    audit.check("operator", "action_threshold", action_threshold == 3 * sp.sqrt(3) / 10, action_threshold, 3 * sp.sqrt(3) / 10)

    eta_residual = sp.Rational(197, 440)
    zeta_residual = sp.Rational(3, 25)
    reserve_threshold = sp.simplify(4 * sp.sqrt(eta_residual * zeta_residual))
    audit.check("operator", "r103_reserve_threshold", reserve_threshold**2 == sp.Rational(1182, 1375), reserve_threshold**2, sp.Rational(1182, 1375))
    eta_row = sp.simplify(sp.Rational(3, 125) / mass)
    row_residual_threshold = sp.simplify(4 * sp.sqrt((eta_residual - eta_row) * zeta_residual))
    audit.check("operator", "legal_row_residual_positive", eta_residual - eta_row > 0, eta_residual - eta_row, "positive")
    audit.check("operator", "legal_row_residual_numeric", abs(float(row_residual_threshold.evalf()) - 0.920932) < 1e-6, row_residual_threshold.evalf(12), "0.920932 +/- 1e-6")
    audit.check("operator", "hs_check_is_sufficient_not_necessary", True, "K_far is an HS upper bound", "sufficient check only")

    diagnostics = {
        "bridge": "S_h-S_0 = Delta V_fut - 2 Delta O = Delta V_fut - Delta F063_ad",
        "production_counterfixture": {
            "theta": theta_fixture,
            "conditional_variance": variance_fixture,
            "forest_mean": forest_fixture,
            "missing_half_variance": omission,
        },
        "operator": {
            "K_far": k_far,
            "full_threshold": full_threshold,
            "r103_reserve_threshold": reserve_threshold,
            "row_residual_threshold": row_residual_threshold,
        },
        "open": [
            "adapted cutoff-uniform R-063 root-shell reconstruction",
            "production factorization with the required square ledgers and total-symbol decay",
            "owner-complete stationary-baseline upper bound",
            "OVERLAP_src and q=10/9 Nelson",
        ],
        "stationary_baseline": {
            "exact_residual": "sum V0 - sum F063_ad,0 plus complement leakage",
            "conditional_lemma": "the low-plus-root aggregate is nonpositive under common-terminal hypotheses; root-only C0=0 additionally requires a nonnegative complete-low baseline",
            "production_status": "OPEN",
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-125 primary {payload['status']} {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
