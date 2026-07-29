#!/usr/bin/env python3
"""Primary exact audit for the scoped R-119 A13 proof frontier.

The executable checks the minimal legal two-block adapted chart, endpoint
telescoping, the exact zero/first-chaos score--trace criterion, counterfixtures
to automatic cancellation, the bare-Jacobian-heat no-go, the positive
canonical coefficient for the one-pair diagnostic, the two exact boundary
faces of the stationary scalar model, and finite-dimensional terminal-Hessian
quotient identities.  The companion note proves the general statements.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LEGAL-ADAPTED-CLUSTER-SCORE-TRACE-TERMINAL-HESSIAN-FRONTIER"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-29-primary-legal-adapted-cluster-score-trace-terminal-hessian-frontier/result.json"
)
R102_RESULT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-full-hessian-laplace-wick-future-feedback-boundary/result.json"
)
SCHEMA = "tect/a13-legal-adapted-cluster-score-trace-terminal-hessian-frontier-primary/1.0"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
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
                "The audit proves structural and exact finite-dimensional R-119 statements. "
                "It does not compute the coefficient-level low-chaos cancellation of the "
                "full production A1 cluster, prove the mixed-interior PSD conjecture, the "
                "spatial multiplier estimate, one-use aggregation, Nelson, or Sector A closure."
            ),
        }


def gaussian_expectation(poly: sp.Expr, variables: Iterable[sp.Symbol]) -> sp.Expr:
    value = sp.expand(poly)
    for variable in variables:
        expanded = sp.Poly(sp.expand(value), variable)
        total = sp.Integer(0)
        for (degree,), coefficient in expanded.terms():
            if degree % 2:
                continue
            moment = sp.Integer(1) if degree == 0 else sp.factorial2(degree - 1)
            total += coefficient * moment
        value = sp.expand(total)
    return sp.simplify(value)


def delta2_matrix(weight: sp.Matrix, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    total = sp.Integer(0)
    for i, xi in enumerate(variables):
        for j, xj in enumerate(variables):
            wij = weight[i, j]
            total += (xi * xj - (1 if i == j else 0)) * wij
            total -= xi * sp.diff(wij, xj)
            total -= xj * sp.diff(wij, xi)
            total += sp.diff(wij, xi, xj)
    return sp.expand(total)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    # Round 1: the smallest genuinely adapted strict-triangular chart uses two
    # independent source blocks and two visits.  The second visit may depend on
    # the first root but not on the unrevealed second root.
    xi1, xi2, h1 = sp.symbols("xi1 xi2 h1", real=True)
    h2 = xi1**2 - 1
    z0 = xi1 + 2 * xi2
    z1 = z0 + h1
    zstar = z1 + h2
    audit.check("legal_chart", "future_visit_is_strict_past", sp.diff(h2, xi2) == 0, sp.diff(h2, xi2), 0)
    audit.check("legal_chart", "future_visit_is_nontrivial", sp.diff(h2, xi1) != 0, sp.diff(h2, xi1), "nonzero")
    audit.check("legal_chart", "two_source_endpoint", sp.expand(zstar - z0) == h1 + h2, sp.expand(zstar - z0), h1 + h2)

    x0, x1, xs, t0, t1, ts = sp.symbols("x0 x1 xs t0 t1 ts", real=True)
    visit_one = x0 * (x1 - x0) + sp.Rational(1, 2) * (x1 - x0) ** 2 - sp.Rational(1, 2) * (t1 - t0)
    visit_two = x1 * (xs - x1) + sp.Rational(1, 2) * (xs - x1) ** 2 - sp.Rational(1, 2) * (ts - t1)
    two_visit = sp.expand(visit_one + visit_two)
    endpoint = sp.expand(sp.Rational(1, 2) * (xs**2 - x0**2) - sp.Rational(1, 2) * (ts - t0))
    audit.check("legal_chart", "two_visit_endpoint_telescope", sp.expand(two_visit - endpoint) == 0, sp.expand(two_visit - endpoint), 0)
    audit.check("legal_chart", "intermediate_output_cancels", sp.diff(two_visit, x1) == 0, sp.diff(two_visit, x1), 0)
    audit.check("legal_chart", "intermediate_trace_cancels", sp.diff(two_visit, t1) == 0, sp.diff(two_visit, t1), 0)

    # Round 2: exact score--trace formula for R=alpha H2+beta H3.  All
    # constants are derived from Gaussian moments rather than pasted.
    G, b, a, alpha, beta, q0, q1 = sp.symbols("G b a alpha beta q0 q1", real=True)
    H2 = G**2 - 1
    H3 = G**3 - 3 * G
    R = alpha * H2 + beta * H3
    Y = b + a * G + R
    delta_tau = q0 + q1 * G
    residual = sp.expand((b + a * G) * R + sp.Rational(1, 2) * R**2 - sp.Rational(1, 2) * delta_tau)
    mean_direct = gaussian_expectation(residual, (G,))
    first_direct = gaussian_expectation(G * residual, (G,))
    mean_formula = sp.expand((2 * alpha**2 + 6 * beta**2 - q0) / 2)
    first_formula = sp.expand(2 * a * alpha + 6 * alpha * beta - q1 / 2)
    audit.check("score_trace", "remainder_is_centered", gaussian_expectation(R, (G,)) == 0, gaussian_expectation(R, (G,)), 0)
    audit.check("score_trace", "remainder_has_no_first_chaos", gaussian_expectation(G * R, (G,)) == 0, gaussian_expectation(G * R, (G,)), 0)
    audit.check("score_trace", "mean_projection_formula", sp.simplify(mean_direct - mean_formula) == 0, mean_direct, mean_formula)
    audit.check("score_trace", "first_projection_formula", sp.simplify(first_direct - first_formula) == 0, first_direct, first_formula)

    required_q0 = sp.expand(2 * alpha**2 + 6 * beta**2)
    required_q1 = sp.expand(4 * a * alpha + 12 * alpha * beta)
    cancelled = sp.expand(residual.subs({q0: required_q0, q1: required_q1}))
    audit.check("score_trace", "necessary_mean_trace", gaussian_expectation(cancelled, (G,)) == 0, gaussian_expectation(cancelled, (G,)), 0)
    audit.check("score_trace", "necessary_first_trace", gaussian_expectation(G * cancelled, (G,)) == 0, gaussian_expectation(G * cancelled, (G,)), 0)

    DR = sp.diff(R, G)
    divergence_u = sp.expand(G * a * R - sp.diff(a * R, G))
    score = sp.expand(delta_tau - 2 * b * R - R**2 - 2 * a * DR)
    audit.check("score_trace", "score_divergence_identity", sp.expand(residual - (divergence_u - score / 2)) == 0, sp.expand(residual - (divergence_u - score / 2)), 0)
    audit.check("score_trace", "physical_mean_condition", sp.simplify(gaussian_expectation(delta_tau, (G,)) - gaussian_expectation(R**2, (G,))).subs(q0, required_q0) == 0, required_q0, gaussian_expectation(R**2, (G,)))
    physical_first_rhs = sp.expand(2 * a * gaussian_expectation(sp.diff(R, G, 2), (G,)) + 2 * gaussian_expectation(DR * R, (G,)))
    audit.check("score_trace", "physical_first_condition", sp.simplify(physical_first_rhs - required_q1) == 0, physical_first_rhs, required_q1)

    # Exact counterfixtures: centering alone does not remove first chaos, and
    # adjacent nonlinear chaoses create an independent first-chaos debt.
    eps = sp.symbols("eps", positive=True)
    first_fixture = sp.expand((G) * (eps * H2) + sp.Rational(1, 2) * (eps * H2) ** 2 - eps**2)
    audit.check("counterfixtures", "centered_fixture_mean", gaussian_expectation(first_fixture, (G,)) == 0, gaussian_expectation(first_fixture, (G,)), 0)
    audit.check("counterfixtures", "centered_fixture_first_debt", gaussian_expectation(G * first_fixture, (G,)) == 2 * eps, gaussian_expectation(G * first_fixture, (G,)), 2 * eps)
    adjacent_fixture = sp.expand(sp.Rational(1, 2) * R**2 - sp.Rational(1, 2) * required_q0)
    audit.check("counterfixtures", "adjacent_fixture_mean", gaussian_expectation(adjacent_fixture, (G,)) == 0, gaussian_expectation(adjacent_fixture, (G,)), 0)
    audit.check("counterfixtures", "adjacent_fixture_first_debt", gaussian_expectation(G * adjacent_fixture, (G,)) == 6 * alpha * beta, gaussian_expectation(G * adjacent_fixture, (G,)), 6 * alpha * beta)

    # Round 3: bare Jacobian heat cannot cancel a nonlinear residual.
    bare_heat = sp.expand(2 * a * DR + DR**2)
    bare_residual = sp.expand((b + a * G) * R + sp.Rational(1, 2) * R**2 - sp.Rational(1, 2) * bare_heat)
    bare_mean = gaussian_expectation(bare_residual, (G,))
    bare_formula = -alpha**2 - 6 * beta**2
    audit.check("bare_heat", "bare_heat_mean_formula", sp.simplify(bare_mean - bare_formula) == 0, bare_mean, bare_formula)
    audit.check("bare_heat", "bare_heat_strict_fixture", bare_mean.subs({alpha: 1, beta: 1}) < 0, bare_mean.subs({alpha: 1, beta: 1}), "<0")
    audit.check("bare_heat", "nonlinearity_weight_h2", -sp.Rational(1, 2) * (2 - 1) * sp.factorial(2) == -1, -sp.Rational(1, 2) * (2 - 1) * sp.factorial(2), -1)
    audit.check("bare_heat", "nonlinearity_weight_h3", -sp.Rational(1, 2) * (3 - 1) * sp.factorial(3) == -6, -sp.Rational(1, 2) * (3 - 1) * sp.factorial(3), -6)

    # The one-pair diagnostic has a strictly PSD canonical coefficient.  This
    # is viability evidence, not the complete production A1 cluster.
    X, Y = sp.symbols("X Y", real=True)
    sigma = sp.symbols("sigma", real=True, positive=True)
    radius = X**2 + Y**2
    pair_packet = sp.expand(sigma**4 * (radius**2 - 4 * radius) / 16)
    H2X, H2Y = X**2 - 1, Y**2 - 1
    H4X, H4Y = X**4 - 6 * X**2 + 3, Y**4 - 6 * Y**2 + 3
    pair_chaos2 = sp.expand(sigma**4 * (H2X + H2Y) / 4)
    pair_chaos4 = sp.expand(sigma**4 * (H4X + H4Y + 2 * H2X * H2Y) / 16)
    vector = sp.Matrix([X, Y])
    canonical_w = sp.simplify(
        sp.hessian(pair_chaos2, (X, Y))
        + sp.hessian(pair_chaos4, (X, Y)) / 6
    )
    pair_delta2 = delta2_matrix(canonical_w, (X, Y))
    pair_decomposition_error = sp.expand(pair_packet - pair_chaos2 - pair_chaos4)
    audit.check(
        "one_pair_w",
        "packet_chaos_reconstruction",
        gaussian_expectation(pair_packet, (X, Y)) == 0
        and pair_decomposition_error == 0,
        [gaussian_expectation(pair_packet, (X, Y)), pair_decomposition_error],
        [0, 0],
    )
    audit.check("one_pair_w", "double_divergence_identity", sp.expand(pair_delta2 - 2 * pair_packet) == 0, sp.expand(pair_delta2 - 2 * pair_packet), 0)
    tangent = sp.Matrix([-Y, X])
    tangential_eigenvalue = sp.simplify((tangent.T * canonical_w * tangent)[0] / radius)
    radial_eigenvalue = sp.simplify((vector.T * canonical_w * vector)[0] / radius)
    expected_tangential = sigma**4 * (radius + 8) / 24
    expected_radial = sigma**4 * (3 * radius + 8) / 24
    audit.check("one_pair_w", "tangential_eigenvalue", sp.simplify(tangential_eigenvalue - expected_tangential) == 0, tangential_eigenvalue, expected_tangential)
    audit.check("one_pair_w", "radial_eigenvalue", sp.simplify(radial_eigenvalue - expected_radial) == 0, radial_eigenvalue, expected_radial)
    pair_cost = gaussian_expectation(pair_delta2**2, (X, Y))
    audit.check("one_pair_w", "exact_double_divergence_cost", sp.simplify(pair_cost - 2 * sigma**8) == 0, pair_cost, 2 * sigma**8)
    audit.check("one_pair_w", "strict_origin_eigenvalue", expected_tangential.subs({X: 0, Y: 0}) == sigma**4 / 3, expected_tangential.subs({X: 0, Y: 0}), sigma**4 / 3)

    # Only the two boundary faces of the R-115 scalar W are certified here.
    scalar_b = sp.symbols("scalar_b", nonnegative=True)
    C4y = radius**2 - 8 * radius + 8
    face0_f2 = (4 * scalar_b + 1) * (radius - 2) / 16
    face0_f4 = C4y / 64
    face0_w = sp.simplify(sp.hessian(face0_f2, (X, Y)) + sp.hessian(face0_f4, (X, Y)) / 6)
    face0_tang = sp.simplify((tangent.T * face0_w * tangent)[0] / radius)
    face0_rad = sp.simplify((vector.T * face0_w * vector)[0] / radius)
    audit.check("scalar_faces", "c0_tangential", sp.simplify(face0_tang - (48 * scalar_b + radius + 8) / 96) == 0, face0_tang, (48 * scalar_b + radius + 8) / 96)
    audit.check("scalar_faces", "c0_radial", sp.simplify(face0_rad - (48 * scalar_b + 3 * radius + 8) / 96) == 0, face0_rad, (48 * scalar_b + 3 * radius + 8) / 96)

    C4x = radius**2 - 8 * radius + 8
    face1_f2 = (scalar_b + 1) * (radius - 2) / 4
    face1_f4 = C4x / 16
    face1_w = sp.simplify(sp.hessian(face1_f2, (X, Y)) + sp.hessian(face1_f4, (X, Y)) / 6)
    face1_tang = sp.simplify((tangent.T * face1_w * tangent)[0] / radius)
    face1_rad = sp.simplify((vector.T * face1_w * vector)[0] / radius)
    audit.check("scalar_faces", "c1_tangential", sp.simplify(face1_tang - (12 * scalar_b + radius + 8) / 24) == 0, face1_tang, (12 * scalar_b + radius + 8) / 24)
    audit.check("scalar_faces", "c1_radial", sp.simplify(face1_rad - (12 * scalar_b + 3 * radius + 8) / 24) == 0, face1_rad, (12 * scalar_b + 3 * radius + 8) / 24)
    audit.check("scalar_faces", "c0_origin_positive", face0_tang.subs({X: 0, Y: 0, scalar_b: 0}) == sp.Rational(1, 12), face0_tang.subs({X: 0, Y: 0, scalar_b: 0}), sp.Rational(1, 12))
    audit.check("scalar_faces", "c1_origin_positive", face1_tang.subs({X: 0, Y: 0, scalar_b: 0}) == sp.Rational(1, 3), face1_tang.subs({X: 0, Y: 0, scalar_b: 0}), sp.Rational(1, 3))

    # Round 4: the full terminal action has an automatic quotient Hessian.
    L = sp.Matrix([[1, 1, 0], [0, 1, 1]])
    vertical = sp.Matrix([1, -1, 1])
    u1, u2 = sp.symbols("u1 u2", real=True)
    c0, c1, c2 = sp.symbols("c0 c1 c2", real=True)
    potential = u1**3 + 2 * u1 * u2 + u2**4
    endpoint_hessian = sp.hessian(potential, (u1, u2)).subs({u1: 1, u2: 2})
    controls = sp.Matrix([c0, c1, c2])
    endpoint_controls = L * controls
    composed_potential = sp.expand(
        potential.subs({u1: endpoint_controls[0], u2: endpoint_controls[1]})
    )
    visit_hessian = sp.hessian(composed_potential, (c0, c1, c2)).subs(
        {c0: 1, c1: 0, c2: 2}
    )
    chain_hessian = sp.simplify(L.T * endpoint_hessian * L)
    audit.check(
        "terminal_hessian",
        "endpoint_chain_rule",
        sp.simplify(visit_hessian - chain_hessian) == sp.zeros(3),
        visit_hessian,
        chain_hessian,
    )
    audit.check("terminal_hessian", "vertical_cycle_is_kernel", L * vertical == sp.zeros(2, 1), L * vertical, sp.zeros(2, 1))
    audit.check("terminal_hessian", "global_hessian_kills_cycle", visit_hessian * vertical == sp.zeros(3, 1), visit_hessian * vertical, sp.zeros(3, 1))

    sample = sp.Matrix([2, -3, 5])
    endpoint_sample = L * sample
    minimal = sp.simplify(L.T * (L * L.T).inv() * endpoint_sample)
    quotient_norm_sq = sp.simplify((endpoint_sample.T * (L * L.T).inv() * endpoint_sample)[0])
    minimal_norm_sq = sp.simplify((minimal.T * minimal)[0])
    audit.check("terminal_hessian", "minimal_representative_has_endpoint", L * minimal == endpoint_sample, L * minimal, endpoint_sample)
    audit.check("terminal_hessian", "quotient_norm_is_minimal_norm", quotient_norm_sq == minimal_norm_sq, quotient_norm_sq, minimal_norm_sq)
    audit.check("terminal_hessian", "discarded_part_is_vertical", L * (sample - minimal) == sp.zeros(2, 1), L * (sample - minimal), sp.zeros(2, 1))

    # The inherited R-102 curl fixes a checksum for omitted companions; it is
    # not re-labelled as an independently reconstructed companion theorem.
    r102 = json.loads(R102_RESULT.read_text(encoding="utf-8"))
    inherited_curl = Fraction(r102["diagnostics"]["cartan_boundary"]["full_remainder_one_form_curl"])
    required_companion_curl = -inherited_curl
    audit.check("cartan_checksum", "r102_authority_pass", r102.get("status") == "PASS", r102.get("status"), "PASS")
    audit.check("cartan_checksum", "isolated_current_curl", inherited_curl == Fraction(-40, 729), inherited_curl, Fraction(-40, 729))
    audit.check("cartan_checksum", "required_companion_curl", required_companion_curl == Fraction(40, 729), required_companion_curl, Fraction(40, 729))
    audit.check("cartan_checksum", "global_exactness_checksum", inherited_curl + required_companion_curl == 0, inherited_curl + required_companion_curl, 0)

    diagnostics = {
        "legal_adapted_minimum": {
            "independent_source_blocks": 2,
            "visits": 2,
            "diagnostic_output_cluster": ["0", "+2k", "-2k"],
            "diagnostic_is_full_production_cluster": False,
        },
        "score_trace": {
            "mean_trace_requirement": required_q0,
            "first_trace_requirement": required_q1,
            "bare_heat_mean": bare_formula,
        },
        "one_pair": {
            "tangential_eigenvalue": expected_tangential,
            "radial_eigenvalue": expected_radial,
            "double_divergence_cost": pair_cost,
            "unit_sigma_double_divergence_cost": pair_cost.subs(sigma, 1),
        },
        "scalar_model": {
            "c0_psd_proved": True,
            "c1_psd_proved": True,
            "mixed_interior_psd_proved": False,
        },
        "terminal_hessian": {
            "global_vertical_basicness": True,
            "termwise_owner_basicness_proved": False,
            "quotient_norm_requires_inverse_loss": False,
            "spatial_h2_l6_compatibility_proved": False,
        },
        "cartan_checksum": {
            "isolated_current": inherited_curl,
            "required_complete_companions": required_companion_curl,
            "required_not_observed": True,
        },
        "consequence": {
            "full_a1_low_chaos_cancellation": False,
            "one_use_source_sextic_aggregation": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"{payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
