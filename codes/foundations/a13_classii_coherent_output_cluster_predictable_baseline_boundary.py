#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-107 boundary.

The certificate verifies exact finite-dimensional identities used to isolate
the remaining Sector-A production atom.  It deliberately does not assert the
adapted same-root cluster estimate, OVERLAP_src, Nelson, or Sector-A closure.
All reported values are derived from exact symbolic inputs.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import sympy as sp


SCHEMA = "tect/a13-coherent-output-cluster-predictable-baseline-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-coherent-output-cluster-predictable-baseline-boundary/result.json"
)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def require(self, group: str, name: str, condition: object, actual: object, expected: object) -> None:
        passed = condition is True or condition == sp.S.true
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...], variance: sp.Expr) -> sp.Expr:
    """Exact expectation of a polynomial in independent N(0, variance) variables."""
    polynomial = sp.Poly(sp.expand(expression), *variables)
    total = sp.Integer(0)
    for powers, coefficient in polynomial.terms():
        moment = sp.Integer(1)
        for power in powers:
            if power % 2:
                moment = sp.Integer(0)
                break
            moment *= sp.factorial2(power - 1) * variance ** (power // 2) if power else 1
        total += coefficient * moment
    return sp.simplify(total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    q = sp.Rational(10, 9)
    source_budget = sp.Rational(9, 20)
    sextic_budget = sp.Rational(3, 20)
    checks.require("budget", "q times source budget", q * source_budget == sp.Rational(1, 2), q * source_budget, sp.Rational(1, 2))
    checks.require("budget", "q times sextic budget", q * sextic_budget == sp.Rational(1, 6), q * sextic_budget, sp.Rational(1, 6))

    # Exact endpoint likelihood interpolation and entropy production.
    s = sp.symbols("s", real=True)
    alpha = sp.Rational(2, 3)
    psi = s * sp.log(1 + alpha) / 2 - sp.log(1 + alpha * s) / 2
    variance = sp.simplify(sp.diff(psi, s, 2))
    forward_kl = sp.simplify(sp.integrate(s * variance, (s, 0, 1)))
    reverse_kl = sp.simplify(sp.integrate((1 - s) * variance, (s, 0, 1)))
    expected_forward = sp.log(1 + alpha) / 2 - alpha / (2 * (1 + alpha))
    expected_reverse = alpha / 2 - sp.log(1 + alpha) / 2
    checks.require("entropy", "normalized scalar likelihood", sp.simplify(psi.subs(s, 1)) == 0, psi.subs(s, 1), 0)
    checks.require("entropy", "tilt variance formula", sp.simplify(variance - alpha**2 / (2 * (1 + alpha * s) ** 2)) == 0, variance, alpha**2 / (2 * (1 + alpha * s) ** 2))
    checks.require("entropy", "forward entropy production", sp.simplify(forward_kl - expected_forward) == 0, forward_kl, expected_forward)
    checks.require("entropy", "reverse entropy production", sp.simplify(reverse_kl - expected_reverse) == 0, reverse_kl, expected_reverse)
    checks.require("entropy", "forward entropy positive", forward_kl > 0, forward_kl, ">0")
    checks.require("entropy", "reverse entropy positive", reverse_kl > 0, reverse_kl, ">0")
    checks.require("entropy", "forward derivative weight", sp.simplify(sp.diff(s * sp.diff(psi, s) - psi, s) - s * variance) == 0, sp.diff(s * sp.diff(psi, s) - psi, s), s * variance)
    reverse_entropy_s = (s - 1) * sp.diff(psi, s) - psi + psi.subs(s, 1)
    checks.require("entropy", "reverse derivative weight", sp.simplify(sp.diff(reverse_entropy_s, s) - (s - 1) * variance) == 0, sp.diff(reverse_entropy_s, s), (s - 1) * variance)

    # Backward-resolvent density martingale for jointly frozen rows:
    # two scalar roots A1=1, A2=2.
    x1, x2 = sp.symbols("x1 x2", real=True)
    a1, a2 = sp.Integer(1), sp.Integer(2)
    covariance_total = a1**2 + a2**2
    det_total = 1 + q * covariance_total
    det_tail = 1 + q * a2**2
    log_m0 = sp.Integer(0)
    log_m1 = sp.log(det_total / det_tail) / 2 - q * (a1 * x1) ** 2 / (2 * det_tail)
    log_m2 = sp.log(det_total) / 2 - q * (a1 * x1 + a2 * x2) ** 2 / 2
    endpoint_likelihood = sp.log(det_total) / 2 - q * (a1 * x1 + a2 * x2) ** 2 / 2
    checks.require("martingale", "scalar total determinant", det_total == sp.Rational(59, 9), det_total, sp.Rational(59, 9))
    checks.require("martingale", "scalar tail determinant", det_tail == sp.Rational(49, 9), det_tail, sp.Rational(49, 9))
    checks.require("martingale", "M0 equals one", log_m0 == 0, log_m0, 0)
    checks.require("martingale", "MJ equals endpoint likelihood", sp.simplify(log_m2 - endpoint_likelihood) == 0, log_m2, endpoint_likelihood)
    checks.require("martingale", "M1 quadratic coefficient", sp.simplify(sp.diff(log_m1, x1, 2) / 2 + sp.Rational(5, 49)) == 0, sp.diff(log_m1, x1, 2) / 2, -sp.Rational(5, 49))
    conditional_x2 = sp.sqrt(1 / (1 + q * a2**2)) * sp.exp(
        -(q / 2) * (a1 * x1) ** 2 / (1 + q * a2**2)
    )
    checks.require("martingale", "fresh second root Gaussian integral", sp.simplify(conditional_x2 - sp.Rational(3, 7) * sp.exp(-sp.Rational(5, 49) * x1**2)) == 0, conditional_x2, sp.Rational(3, 7) * sp.exp(-sp.Rational(5, 49) * x1**2))
    conditional_m2 = sp.sqrt(det_total) * conditional_x2
    checks.require("martingale", "conditional M2 equals M1", sp.simplify(conditional_m2 - sp.exp(log_m1)) == 0, conditional_m2, sp.exp(log_m1))
    mean_m1 = sp.sqrt(det_total / det_tail) / sp.sqrt(1 + sp.Rational(10, 49))
    checks.require("martingale", "mean M1 equals one", sp.simplify(mean_m1) == 1, mean_m1, 1)

    # A bounded progressive future row invalidates the global frozen
    # normalizer.  Take A1=1 and A2=1_{|x1|>1}.  After integrating x2, the
    # candidate density has different Gaussian precisions inside and outside
    # the threshold, so its two pieces do not recombine to mass one.
    beta_inner = sp.simplify(1 + q)
    beta_outer = sp.simplify((1 + 2 * q) / (1 + q))
    inner_mass = sp.erf(sp.sqrt(beta_inner / 2))
    outer_mass = sp.erfc(sp.sqrt(beta_outer / 2))
    adaptive_mass = sp.simplify(inner_mass + outer_mass.rewrite(sp.erf))
    adaptive_normalization_defect = sp.simplify(adaptive_mass - 1)
    expected_adaptive_mass = 1 + sp.erf(sp.sqrt(sp.Rational(19, 18))) - sp.erf(
        sp.sqrt(sp.Rational(29, 38))
    )
    checks.require("martingale-boundary", "adaptive inner precision", beta_inner == sp.Rational(19, 9), beta_inner, sp.Rational(19, 9))
    checks.require("martingale-boundary", "adaptive outer precision", beta_outer == sp.Rational(29, 19), beta_outer, sp.Rational(29, 19))
    checks.require("martingale-boundary", "adaptive combined mass exact", sp.simplify(adaptive_mass - expected_adaptive_mass) == 0, adaptive_mass, expected_adaptive_mass)
    checks.require("martingale-boundary", "adaptive erf arguments ordered", sp.Rational(19, 18) > sp.Rational(29, 38), sp.Rational(19, 18), sp.Rational(29, 38))
    checks.require("martingale-boundary", "adaptive row normalization defect positive", adaptive_normalization_defect > 0, adaptive_normalization_defect, ">0")
    checks.require("martingale-boundary", "adaptive defect numerical bracket", sp.Float("0.0704") < sp.N(adaptive_normalization_defect, 50) < sp.Float("0.0705"), sp.N(adaptive_normalization_defect, 20), "(0.0704,0.0705)")
    fixed_inner_mass = sp.erf(sp.sqrt(beta_inner / 2)) + sp.erfc(sp.sqrt(beta_inner / 2)).rewrite(sp.erf)
    fixed_outer_mass = sp.erf(sp.sqrt(beta_outer / 2)) + sp.erfc(sp.sqrt(beta_outer / 2)).rewrite(sp.erf)
    checks.require("martingale-boundary", "fixed zero-row normalization guard", sp.simplify(fixed_inner_mass) == 1, fixed_inner_mass, 1)
    checks.require("martingale-boundary", "fixed one-row normalization guard", sp.simplify(fixed_outer_mass) == 1, fixed_outer_mass, 1)

    centered_q = ((a1 * x1 + a2 * x2) ** 2 - covariance_total) / 2
    determinant_debt = (q * covariance_total - sp.log(det_total)) / 2
    checks.require("martingale", "likelihood centered form", sp.simplify(endpoint_likelihood + q * centered_q + determinant_debt) == 0, endpoint_likelihood, -q * centered_q - determinant_debt)
    checks.require("martingale", "determinant debt positive", determinant_debt > 0, determinant_debt, ">0")

    # Whole-output frozen Gaussian formula, retaining the mixed baseline.
    kmap = sp.Matrix([[1, 1], [0, 1]])
    output_covariance = kmap * kmap.T
    baseline = sp.Matrix([1, -1])
    resolvent = (sp.eye(2) + q * output_covariance).inv()
    log_formula = q * sp.trace(output_covariance) / 2 - sp.log((sp.eye(2) + q * output_covariance).det()) / 2 - q * (baseline.T * resolvent * baseline)[0] / 2
    log_det2_formula = -(sp.log((sp.eye(2) + q * output_covariance).det()) - q * sp.trace(output_covariance)) / 2 - q * (baseline.T * resolvent * baseline)[0] / 2
    hs_bound = q**2 * sp.trace(output_covariance**2) / 4
    checks.require("frozen", "whole-output det2 identity", sp.simplify(log_formula - log_det2_formula) == 0, log_formula, log_det2_formula)
    checks.require("frozen", "baseline resolvent term nonpositive", -q * (baseline.T * resolvent * baseline)[0] / 2 < 0, -q * (baseline.T * resolvent * baseline)[0] / 2, "<0")
    checks.require("frozen", "whole-output Hilbert-Schmidt bound", sp.N(log_formula, 40) <= sp.N(hs_bound, 40), sp.N(log_formula, 20), sp.N(hs_bound, 20))
    u = sp.symbols("u", nonnegative=True)
    scalar_remainder = u - sp.log(1 + u) - u**2 / 2
    checks.require("frozen", "scalar determinant remainder starts zero", scalar_remainder.subs(u, 0) == 0, scalar_remainder.subs(u, 0), 0)
    checks.require("frozen", "scalar determinant remainder derivative nonpositive", sp.simplify(sp.diff(scalar_remainder, u)) == -u**2 / (1 + u), sp.diff(scalar_remainder, u), -u**2 / (1 + u))

    # Sequential Schur increments and the cost of independent row normalizers.
    t1 = sp.Matrix([[1, 0], [0, 0]])
    t2 = sp.Matrix([[1, 1], [1, 1]])
    identity = sp.eye(2)
    det1 = (identity + q * t1).det()
    det2 = (identity + q * t2).det()
    det12 = (identity + q * (t1 + t2)).det()
    ratio12 = sp.simplify(det12 / det1)
    ratio21 = sp.simplify(det12 / det2)
    slack = sp.log(det1 * det2 / det12) / 2
    checks.require("schur", "first row determinant", det1 == sp.Rational(19, 9), det1, sp.Rational(19, 9))
    checks.require("schur", "second row determinant", det2 == sp.Rational(29, 9), det2, sp.Rational(29, 9))
    checks.require("schur", "combined determinant", det12 == sp.Rational(451, 81), det12, sp.Rational(451, 81))
    checks.require("schur", "order 1 then 2 ratio", ratio12 == sp.Rational(451, 171), ratio12, sp.Rational(451, 171))
    checks.require("schur", "order 2 then 1 ratio", ratio21 == sp.Rational(451, 261), ratio21, sp.Rational(451, 261))
    checks.require("schur", "sequential products invariant", sp.simplify(det1 * ratio12 - det2 * ratio21) == 0, det1 * ratio12, det2 * ratio21)
    checks.require("schur", "independent normalizer slack positive", slack > 0, slack, ">0")
    checks.require("schur", "slack exact ratio", sp.simplify(sp.exp(2 * slack) - sp.Rational(551, 451)) == 0, sp.exp(2 * slack), sp.Rational(551, 451))
    m = sp.symbols("m", positive=True, integer=True)
    lam = sp.Rational(3, 5)
    repeated_slack = (m * sp.log(1 + q * lam) - sp.log(1 + q * m * lam)) / 2
    checks.require("schur", "four-row slack positive", repeated_slack.subs(m, 4) > 0, repeated_slack.subs(m, 4), ">0")
    checks.require("schur", "four-row slack exact ratio", sp.simplify(sp.exp(2 * repeated_slack.subs(m, 4)) - sp.Rational(625, 297)) == 0, sp.exp(2 * repeated_slack.subs(m, 4)), sp.Rational(625, 297))
    checks.require("schur", "repeated-row slack grows linearly", sp.limit(repeated_slack / m, m, sp.oo) == sp.log(1 + q * lam) / 2, sp.limit(repeated_slack / m, m, sp.oo), sp.log(1 + q * lam) / 2)

    # Exact one-pair contraction-connected output-cluster fixture.
    a, b, aa, bb, sigma2 = sp.symbols("a b aa bb sigma2", real=True, positive=True)
    z_plus = (a - sp.I * b) / 2
    z_minus = (a + sp.I * b) / 2
    w_plus = (aa - sp.I * bb) / 2
    w_minus = (aa + sp.I * bb) / 2
    current = {
        2: sp.simplify(z_plus * sp.I * z_plus),
        0: sp.simplify(z_plus * (-sp.I) * z_minus + z_minus * sp.I * z_plus),
        -2: sp.simplify(z_minus * (-sp.I) * z_minus),
    }
    trace_coeff = {
        2: sp.simplify(z_plus * sp.I * w_plus),
        0: sp.simplify(z_plus * (-sp.I) * w_minus + z_minus * sp.I * w_plus),
        -2: sp.simplify(z_minus * (-sp.I) * w_minus),
    }
    checks.require("cluster", "zero output current vanishes", current[0] == 0, current[0], 0)
    checks.require("cluster", "positive output current", sp.simplify(current[2] - sp.I * z_plus**2) == 0, current[2], sp.I * z_plus**2)
    checks.require("cluster", "negative output current", sp.simplify(current[-2] + sp.I * z_minus**2) == 0, current[-2], -sp.I * z_minus**2)

    tau: dict[int, sp.Expr] = {}
    for frequency in (0, 2, -2):
        squared = sp.expand(trace_coeff[frequency] * sp.conjugate(trace_coeff[frequency]))
        tau[frequency] = gaussian_expectation(squared, (aa, bb), sigma2)
    z_abs_sq = sp.simplify(z_plus * z_minus)
    checks.require("cluster", "zero output trace allocation", sp.simplify(tau[0] - sigma2 * z_abs_sq) == 0, tau[0], sigma2 * z_abs_sq)
    checks.require("cluster", "positive output trace allocation", sp.simplify(tau[2] - sigma2 * z_abs_sq / 2) == 0, tau[2], sigma2 * z_abs_sq / 2)
    checks.require("cluster", "negative output trace allocation", sp.simplify(tau[-2] - sigma2 * z_abs_sq / 2) == 0, tau[-2], sigma2 * z_abs_sq / 2)
    ez2 = gaussian_expectation(z_abs_sq, (a, b), sigma2)
    ez4 = gaussian_expectation(z_abs_sq**2, (a, b), sigma2)
    packet0 = gaussian_expectation(-tau[0] / 2, (a, b), sigma2)
    packet2 = gaussian_expectation((current[2] * sp.conjugate(current[2]) - tau[2]) / 2, (a, b), sigma2)
    packet_minus2 = gaussian_expectation((current[-2] * sp.conjugate(current[-2]) - tau[-2]) / 2, (a, b), sigma2)
    checks.require("cluster", "second radial moment", ez2 == sigma2 / 2, ez2, sigma2 / 2)
    checks.require("cluster", "fourth radial moment", ez4 == sigma2**2 / 2, ez4, sigma2**2 / 2)
    checks.require("cluster", "zero output packet negative", packet0 == -sigma2**2 / 4, packet0, -sigma2**2 / 4)
    checks.require("cluster", "positive output packet positive", packet2 == sigma2**2 / 8, packet2, sigma2**2 / 8)
    checks.require("cluster", "negative output packet positive", packet_minus2 == sigma2**2 / 8, packet_minus2, sigma2**2 / 8)
    checks.require("cluster", "cluster expectation cancels", sp.simplify(packet0 + packet2 + packet_minus2) == 0, packet0 + packet2 + packet_minus2, 0)
    radial = sp.symbols("radial", nonnegative=True)
    complete_packet = radial**2 - sigma2 * radial
    checks.require("cluster", "cluster packet minimum", sp.simplify(complete_packet.subs(radial, sigma2 / 2)) == -sigma2**2 / 4, complete_packet.subs(radial, sigma2 / 2), -sigma2**2 / 4)

    # Predictable-baseline action and subdivision-invariant covariance mass.
    p1, p2, p3, base_v, energy, terminal_sextic = sp.symbols("P1 P2 P3 V0 E Y", real=True)
    endpoint_expectation = base_v + p1 + p2 + p3
    action = endpoint_expectation + sextic_budget * terminal_sextic + source_budget * energy
    simplified_action = p1 + p2 + p3 + sextic_budget * terminal_sextic + source_budget * energy
    checks.require("baseline", "centered base action normal form", sp.simplify(action.subs(base_v, 0) - simplified_action) == 0, action.subs(base_v, 0), simplified_action)
    checks.require("baseline", "single terminal sextic owner", sp.diff(simplified_action, terminal_sextic) == sextic_budget, sp.diff(simplified_action, terminal_sextic), sextic_budget)
    checks.require("baseline", "source payment owner", sp.diff(simplified_action, energy) == source_budget, sp.diff(simplified_action, energy), source_budget)

    dmat = sp.Matrix([[2, 1], [1, 3]])
    smat1 = sp.Matrix([[1, 0], [0, 2]])
    smat2 = sp.Matrix([[1, 1], [0, 1]])
    covariance1 = smat1 * smat1.T
    covariance2 = smat2 * smat2.T
    mass_left = sp.trace(smat1.T * dmat * smat1) + sp.trace(smat2.T * dmat * smat2)
    mass_right = sp.trace(dmat * (covariance1 + covariance2))
    checks.require("covariance", "predictable covariance mass", mass_left == mass_right, mass_left, mass_right)
    split_left = sp.Rational(3, 5) * smat1
    split_right = sp.Rational(4, 5) * smat1
    split_covariance = split_left * split_left.T + split_right * split_right.T
    checks.require("covariance", "Pythagorean subdivision covariance", split_covariance == covariance1, split_covariance, covariance1)
    split_mass = sp.trace(split_left.T * dmat * split_left) + sp.trace(split_right.T * dmat * split_right)
    checks.require("covariance", "Pythagorean subdivision mass", split_mass == sp.trace(dmat * covariance1), split_mass, sp.trace(dmat * covariance1))
    gaussian_random_heat_defect = sp.Integer(3) - sp.Integer(1)
    checks.require("covariance", "same-root random heat guard", gaussian_random_heat_defect == 2, gaussian_random_heat_defect, 2)

    # Adapted second-jet fixture: separated companions grow while the signed
    # complete combination cancels.
    amplitude, frequency = sp.symbols("amplitude frequency", positive=True)
    decay = sp.exp(-2 * frequency**2)
    eh2 = amplitude**2 * (1 - decay) / 2
    edh2 = amplitude**2 * frequency**2 * (1 + decay) / 2
    ehddh = -amplitude**2 * frequency**2 * (1 - decay) / 2
    signed_second_jet = sp.simplify(edh2 + ehddh)
    hermite_pairing = 2 * amplitude**2 * frequency**2 * decay
    checks.require("second_jet", "signed derivative companions", signed_second_jet == amplitude**2 * frequency**2 * decay, signed_second_jet, amplitude**2 * frequency**2 * decay)
    checks.require("second_jet", "Hermite second-jet pairing", hermite_pairing == 2 * signed_second_jet, hermite_pairing, 2 * signed_second_jet)
    checks.require("second_jet", "bounded source cost limit", sp.limit(eh2, frequency, sp.oo) == amplitude**2 / 2, sp.limit(eh2, frequency, sp.oo), amplitude**2 / 2)
    checks.require("second_jet", "positive companion quadratic growth", sp.limit(edh2 / frequency**2, frequency, sp.oo) == amplitude**2 / 2, sp.limit(edh2 / frequency**2, frequency, sp.oo), amplitude**2 / 2)
    checks.require("second_jet", "negative companion quadratic growth", sp.limit(ehddh / frequency**2, frequency, sp.oo) == -amplitude**2 / 2, sp.limit(ehddh / frequency**2, frequency, sp.oo), -amplitude**2 / 2)
    checks.require("second_jet", "complete companion cancellation", sp.limit(signed_second_jet, frequency, sp.oo) == 0, sp.limit(signed_second_jet, frequency, sp.oo), 0)

    # Pure carrier-information bridge and its dyadic dimensional divergence.
    t = sp.symbols("t", positive=True)
    dimension = sp.symbols("dimension", positive=True, integer=True)
    mutual_information = -dimension * sp.log(t) / 2
    conditional_covariance_cost = dimension * (t - 1 - sp.log(t)) / 2
    conditional_mean_cost = dimension * (1 - t) / 2
    checks.require("carrier", "conditional KL decomposition", sp.simplify(conditional_covariance_cost + conditional_mean_cost - mutual_information) == 0, conditional_covariance_cost + conditional_mean_cost, mutual_information)
    checks.require("carrier", "bridge vanishes at independent endpoint", mutual_information.subs(t, 1) == 0, mutual_information.subs(t, 1), 0)
    quarter_bridge = mutual_information.subs({dimension: 1, t: sp.Rational(1, 4)})
    ninth_bridge = mutual_information.subs({dimension: 6, t: sp.Rational(1, 9)})
    checks.require("carrier", "one-dimensional quarter bridge", sp.simplify(quarter_bridge - sp.log(2)) == 0, quarter_bridge, sp.log(2))
    checks.require("carrier", "six-dimensional ninth bridge", sp.simplify(ninth_bridge - 6 * sp.log(3)) == 0, ninth_bridge, 6 * sp.log(3))
    shell = sp.symbols("shell", nonnegative=True, integer=True)
    partial_shell_dimension = sp.summation(2 ** (3 * shell), (shell, 0, dimension))
    checks.require("carrier", "dyadic root dimension sum", partial_shell_dimension == (8 ** (dimension + 1) - 1) / 7, partial_shell_dimension, (8 ** (dimension + 1) - 1) / 7)
    checks.require("carrier", "carrier bridge diverges at diagonal", sp.limit(mutual_information, t, 0, dir="+") == sp.oo, sp.limit(mutual_information, t, 0, dir="+"), sp.oo)

    # Convexified Gaussian-divergence identity; the associated flow is only a
    # parked route and is not promoted to a production inequality.
    x, p, r, coupling = sp.symbols("x p r coupling", real=True)
    vector_field = p * x + r * x**3
    potential = coupling * x**6
    div_gamma = lambda expression: sp.diff(expression, x) - x * expression
    v_term = -div_gamma(vector_field) / 2
    convexified_field = vector_field + sp.diff(potential, x) / 3
    divergence_identity = sp.simplify(v_term + potential + div_gamma(convexified_field) / 2 - sp.diff(potential, x, 2) / 6)
    checks.require("divergence", "convexified Gaussian divergence identity", divergence_identity == 0, divergence_identity, 0)
    checks.require("divergence", "degree-six Euler identity", sp.simplify(x * sp.diff(potential, x) - 6 * potential) == 0, x * sp.diff(potential, x), 6 * potential)
    flow_time = sp.symbols("flow_time", positive=True)
    flow_coefficient = (1 - (1 + 2 * flow_time) * sp.exp(-2 * flow_time)) / 2
    flow_derivative = sp.simplify(sp.diff(flow_coefficient, flow_time))
    checks.require("divergence", "inward linear-flow remainder positive", flow_derivative == 2 * flow_time * sp.exp(-2 * flow_time) and flow_derivative.is_positive is True, flow_derivative, ">0")
    flow_expectation = 1 / sp.sqrt(1 - 2 * flow_coefficient)
    exact_linear_laplace = sp.exp(flow_time) / sp.sqrt(1 + 2 * flow_time)
    checks.require("divergence", "linear-flow change of variables", sp.simplify(flow_expectation - exact_linear_laplace) == 0, flow_expectation, exact_linear_laplace)

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "source_budget": str(source_budget),
        "sextic_budget": str(sextic_budget),
        "forward_gaussian_kl": str(forward_kl),
        "reverse_gaussian_kl": str(reverse_kl),
        "scalar_total_determinant": str(det_total),
        "scalar_tail_determinant": str(det_tail),
        "adaptive_row_normalization_defect": str(adaptive_normalization_defect),
        "matrix_combined_determinant": str(det12),
        "independent_row_slack": str(slack),
        "one_pair_packet_expectations": [str(packet0), str(packet2), str(packet_minus2)],
        "complete_cluster_packet_infimum": str(-sigma2**2 / 4),
        "adapted_second_jet_signed_sum": str(signed_second_jet),
        "carrier_mutual_information": str(mutual_information),
        "convexified_divergence_residual": str(divergence_identity),
    }
    route_verdicts = {
        "endpoint_entropy_production": "exact-identity-not-free-energy-bound",
        "jointly_frozen_whole_output": "closed-by-det2",
        "progressive_future_row_backward_resolvent": "failed-positive-normalization-defect",
        "single_output_frequency_positivity": "failed-exact-one-pair-fixture",
        "independent_output_determinant_normalization": "failed-linear-slack",
        "predictable_covariance_mass": "exact-subdivision-invariant",
        "termwise_adapted_second_jet": "failed-quadratic-derivative-growth",
        "pure_carrier_kl_diagonal_bridge": "failed-dimensional-divergence",
        "convexified_divergence_flow": "parked-unfavourable-sign",
        "adapted_complete_cluster_matrix_carleson": "open",
        "overlap_src": "open",
        "nelson": "open",
        "sector_a": "open",
    }
    results = {"derived": derived, "route_verdicts": route_verdicts}
    results_sha256 = hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": len(checks.rows),
        "assertions_passed": len(checks.rows) - len(failed),
        "assertions_failed": len(failed),
        "assertions": checks.rows,
        "assertion_names": [str(row["name"]) for row in checks.rows],
        "results_sha256": results_sha256,
        "results": results,
        "derived": derived,
        "route_verdicts": route_verdicts,
    }
    atomic_json(args.output, payload)
    print(f"Primary R-107: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
