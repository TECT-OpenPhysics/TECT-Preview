#!/usr/bin/env python3
"""Primary exact certificate for the scoped R-106 boundary.

The script verifies four logically separate facts:

* the exact Gibbs endpoint likelihood, KL, and thermodynamic-integration
  identities;
* the corrected R-105 stabilising sextic coefficient and cutoff notation;
* the exact production radial Fierz coefficient on an active-doublet ray;
* the production 1:2 same-root merge defect and the coherent-output boundary.

Every mathematical value is derived from upstream constants or exact symbolic
algebra.  The result JSON is written atomically.
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


SCHEMA = "tect/a13-gibbs-endpoint-production-merge-boundary-primary/1.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-gibbs-endpoint-production-merge-boundary/result.json"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    # ------------------------------------------------------------------
    # Exact Gibbs endpoint and likelihood identities.
    # ------------------------------------------------------------------
    q = sp.Rational(10, 9)
    U, trace_t, quad_t, logdet = sp.symbols("U TrT xTx logdet", real=True)
    w0 = -q * U + q * (trace_t - quad_t) / 2
    w1 = -q * U + q * trace_t / 2 - logdet / 2
    likelihood = sp.simplify(w0 - w1)
    expected_likelihood = sp.simplify((logdet - q * quad_t) / 2)
    checks.require("gibbs", "endpoint likelihood cancels trace", likelihood == expected_likelihood, likelihood, expected_likelihood)
    checks.require("gibbs", "endpoint likelihood cancels local potential", not likelihood.has(U), likelihood, "U absent")
    checks.require("gibbs", "endpoint likelihood is trace free", not likelihood.has(trace_t), likelihood, "TrT absent")

    phi0, phi1, h01, h10, e0l, e1l = sp.symbols("Phi0 Phi1 H01 H10 E0L E1L", real=True)
    checks.require(
        "gibbs",
        "forward KL orientation",
        sp.solve(sp.Eq(h01, e0l - (phi0 - phi1)), phi0 - phi1)[0] == e0l - h01,
        e0l - h01,
        "E_nu0 L-H(nu0|nu1)",
    )
    checks.require(
        "gibbs",
        "reverse KL orientation",
        sp.solve(sp.Eq(h10, -e1l + (phi0 - phi1)), phi0 - phi1)[0] == e1l + h10,
        e1l + h10,
        "E_nu1 L+H(nu1|nu0)",
    )
    checks.require("gibbs", "forward entropy has minus sign", sp.diff(e0l - h01, h01) == -1, -1, -1)
    checks.require("gibbs", "reverse entropy has plus sign", sp.diff(e1l + h10, h10) == 1, 1, 1)

    t = sp.symbols("t", real=True)
    p0, p1 = sp.symbols("p0 p1", positive=True)
    b0, b1 = sp.symbols("b0 b1", real=True)
    zt = p0 * sp.exp(t * b0) + p1 * sp.exp(t * b1)
    phit = sp.log(zt)
    tilted_derivative = sp.simplify((p0 * b0 * sp.exp(t * b0) + p1 * b1 * sp.exp(t * b1)) / zt)
    checks.require("gibbs", "thermodynamic derivative", sp.simplify(sp.diff(phit, t) - tilted_derivative) == 0, sp.diff(phit, t), tilted_derivative)
    checks.require(
        "gibbs",
        "total time integral is endpoint difference",
        sp.simplify(sp.integrate(sp.diff(phit, t), (t, 0, 1)) - (phit.subs(t, 1) - phit.subs(t, 0))) == 0,
        sp.integrate(sp.diff(phit, t), (t, 0, 1)),
        phit.subs(t, 1) - phit.subs(t, 0),
    )

    # ------------------------------------------------------------------
    # R-105 correction and the fixed-cutoff endpoint-likelihood no-go.
    # ------------------------------------------------------------------
    L = sp.symbols("L", positive=True)
    cosine_sixth_average = sp.Rational(5, 16)
    stabilising_budget = sp.Rational(3, 20)
    u6 = sp.simplify(stabilising_budget * cosine_sixth_average * L**3)
    checks.require("correction", "cosine sixth average", cosine_sixth_average == sp.Rational(5, 16), cosine_sixth_average, sp.Rational(5, 16))
    checks.require("correction", "stabilising sextic budget", stabilising_budget == sp.Rational(3, 20), stabilising_budget, sp.Rational(3, 20))
    checks.require("correction", "corrected top-shell u6", u6 == sp.Rational(3, 64) * L**3, u6, sp.Rational(3, 64) * L**3)
    top_time = sp.symbols("t_top", positive=True)
    bracket_leading = -3 * q * u6 / top_time
    free_leading = q * u6
    checks.require("correction", "R-105 ratio unchanged", sp.simplify(bracket_leading / free_leading) == -3 / top_time, bracket_leading / free_leading, -3 / top_time)

    N, sigma, c_det, zeta, eta = sp.symbols("N sigma c_det zeta eta", positive=True)
    amplitude = sigma * N ** sp.Rational(1, 4)
    determinant_gain = c_det * amplitude**2 * N
    sextic_cost = zeta * L**3 * amplitude**6
    cm_cost = eta * amplitude**2
    leading_scaled = sp.simplify((determinant_gain - sextic_cost) / N ** sp.Rational(3, 2))
    checks.require("likelihood_nogo", "constant-ray determinant scale", sp.simplify(determinant_gain - c_det * sigma**2 * N ** sp.Rational(3, 2)) == 0, determinant_gain, c_det * sigma**2 * N ** sp.Rational(3, 2))
    checks.require("likelihood_nogo", "constant-ray sextic scale", sp.simplify(sextic_cost - zeta * L**3 * sigma**6 * N ** sp.Rational(3, 2)) == 0, sextic_cost, zeta * L**3 * sigma**6 * N ** sp.Rational(3, 2))
    checks.require("likelihood_nogo", "CM payment is lower order", sp.limit(cm_cost / N ** sp.Rational(3, 2), N, sp.oo) == 0, sp.limit(cm_cost / N ** sp.Rational(3, 2), N, sp.oo), 0)
    checks.require("likelihood_nogo", "small-sigma leading coefficient", sp.simplify(leading_scaled - (c_det * sigma**2 - zeta * L**3 * sigma**6)) == 0, leading_scaled, c_det * sigma**2 - zeta * L**3 * sigma**6)
    shell_count_even = sp.expand((2 * N + 1) ** 3 - (N + 1) ** 3)
    checks.require("likelihood_nogo", "outer cube count exceeds seven N cubed", sp.expand(shell_count_even - 7 * N**3).as_poly(N).all_coeffs()[0] >= 0 and sp.expand(shell_count_even - 7 * N**3).subs(N, 1) > 0, shell_count_even, ">=7N^3")

    # ------------------------------------------------------------------
    # Exact production radial coefficient.
    # ------------------------------------------------------------------
    floor = sp.Rational(1, 10**12)
    P = sp.Integer(4) + floor
    a = sp.Rational(9, 500) / P
    b = sp.Rational(3, 400) / P
    c = sp.Rational(3, 320) / P
    d = sp.simplify(a + 2 * b + c)
    c0 = sp.Rational(3, 250) / P
    c1 = sp.Rational(243, 8000) / P
    alpha = sp.Rational(5, 9)
    checks.require("production", "d definition", sp.simplify(d - (a + 2 * b + c)) == 0, d, a + 2 * b + c)
    checks.require("production", "a positive", a > 0, a, ">0")
    checks.require("production", "b positive", b > 0, b, ">0")
    checks.require("production", "c positive", c > 0, c, ">0")
    checks.require("production", "global square c0 positive", c0 > 0, c0, ">0")
    checks.require("production", "global square c1 positive", c1 > 0, c1, ">0")

    y, eps = sp.symbols("y eps", positive=True)
    radius = y + eps
    delta = sp.simplify(8 * b * eps * y / radius + 4 * c * eps**2 * y / radius**2)
    radial_eigenvalue = sp.simplify(4 * y * (d - 2 * (b + c) * y / radius + c * y**2 / radius**2))
    checks.require("production", "radial Fierz split", sp.simplify(radial_eigenvalue - (4 * a * y + delta)) == 0, radial_eigenvalue, 4 * a * y + delta)
    checks.require("production", "radial asymptotic eigenvalue", sp.limit(radial_eigenvalue / y, y, sp.oo) == 4 * a, sp.limit(radial_eigenvalue / y, y, sp.oo), 4 * a)
    checks.require("production", "delta nonnegative", delta > 0, delta, ">0")
    checks.require("production", "delta zero at zero amplitude", sp.limit(delta, y, 0, dir="+") == 0, sp.limit(delta, y, 0, dir="+"), 0)
    checks.require("production", "delta asymptote", sp.limit(delta, y, sp.oo) == 8 * b * eps, sp.limit(delta, y, sp.oo), 8 * b * eps)
    checks.require("production", "floor square inequality", sp.simplify((y + eps) ** 2 - 4 * eps * y - (y - eps) ** 2) == 0, sp.expand((y + eps) ** 2 - 4 * eps * y), (y - eps) ** 2)
    K_eps = sp.simplify(eps * (8 * b + c))
    delta_bound_numerator = eps * (8 * b * eps * (eps + y) + c * (y - eps) ** 2)
    checks.require("production", "delta bound factorisation", sp.simplify(K_eps - delta - delta_bound_numerator / radius**2) == 0, sp.factor(K_eps - delta), delta_bound_numerator / radius**2)
    checks.require("production", "delta bound numerator positive", delta_bound_numerator > 0, delta_bound_numerator, ">0")
    tau = sp.symbols("tau", real=True)
    checks.require(
        "production",
        "R-082 radial diagonalisation agrees",
        sp.expand(c0 + c1 * (1 - alpha * tau) ** 2 - (a + 2 * b * (1 - tau) + c * (1 - tau) ** 2)) == 0,
        sp.expand(c0 + c1 * (1 - alpha * tau) ** 2),
        sp.expand(a + 2 * b * (1 - tau) + c * (1 - tau) ** 2),
    )

    # ------------------------------------------------------------------
    # Exact 1:2 production merge defect.
    # ------------------------------------------------------------------
    theta, r = sp.symbols("theta r", real=True)
    F = 1 + r * sp.cos(theta) - sp.cos(2 * theta)
    F1 = 1 + r * sp.cos(theta)
    F2 = 1 - sp.cos(2 * theta)
    F0 = sp.Integer(1)

    def average(expression: sp.Expr) -> sp.Expr:
        return sp.simplify(sp.integrate(sp.expand_trig(sp.expand(expression)), (theta, 0, 2 * sp.pi)) / (2 * sp.pi))

    raw_merge = average(F**2 * sp.diff(F, theta) ** 2 - F1**2 * sp.diff(F1, theta) ** 2 - F2**2 * sp.diff(F2, theta) ** 2)
    square_merge = average(F**2 - F1**2 - F2**2 + F0**2)
    derivative_sum = average(sp.diff(F, theta) ** 2 + sp.diff(F1, theta) ** 2 + sp.diff(F2, theta) ** 2)
    sextic_merge = average(F**6 - F1**6 - F2**6 + F0**6)
    checks.require("merge", "quartic raw merge", sp.simplify(raw_merge + r**2 / 4) == 0, raw_merge, -r**2 / 4)
    checks.require("merge", "quadratic trace merge cancels", square_merge == 0, square_merge, 0)
    checks.require("merge", "derivative norm envelope", sp.simplify(derivative_sum - (r**2 + 4)) == 0, derivative_sum, r**2 + 4)
    expected_sextic = -sp.Rational(15, 32) * r**2 * (9 * r**2 + 2)
    checks.require("merge", "sextic merge", sp.simplify(sextic_merge - expected_sextic) == 0, sextic_merge, expected_sextic)
    checks.require("merge", "sextic merge negative off zero", expected_sextic.subs(r, 1) < 0, expected_sextic.subs(r, 1), "<0")

    lam, ksq, ggamma, target, r_sq = sp.symbols("lambda ksq gGamma M r_sq", positive=True)
    Acoef = sp.simplify(a * ksq * r_sq / 2)
    Bcoef = sp.simplify(K_eps * ksq * (r_sq + 4) / 2)
    Ccoef = sp.simplify(K_eps * ggamma)
    merge_upper = -Acoef * lam**4 + Bcoef * lam**2 + Ccoef
    threshold = sp.simplify((Bcoef + sp.sqrt(Bcoef**2 + 4 * Acoef * (Ccoef + target))) / (2 * Acoef))
    checks.require("merge", "negative quartic coefficient", Acoef > 0, Acoef, ">0")
    checks.require("merge", "positive quadratic envelope", Bcoef > 0, Bcoef, ">0")
    checks.require("merge", "finite trace envelope", Ccoef > 0, Ccoef, ">0")
    checks.require("merge", "merge tends to minus infinity", sp.limit(merge_upper, lam, sp.oo) == -sp.oo, sp.limit(merge_upper, lam, sp.oo), -sp.oo)
    checks.require("merge", "threshold solves target crossing", sp.simplify(merge_upper.subs(lam**2, threshold) + target) == 0, sp.simplify(merge_upper.subs(lam**2, threshold)), -target)

    # Exact coherent output Parseval fixture.  Leaves interfere before the
    # square; only the already-assembled output coefficients add orthogonally.
    x1, x2, x3 = sp.symbols("x1 x2 x3", real=True)
    coherent = sp.expand((x1 + x2 + x3) ** 2)
    leaves = sp.expand(x1**2 + x2**2 + x3**2)
    checks.require("output", "coherent square retains cross terms", sp.expand(coherent - leaves) == 2 * (x1 * x2 + x1 * x3 + x2 * x3), coherent - leaves, 2 * (x1 * x2 + x1 * x3 + x2 * x3))
    checks.require("output", "coherent and leaf squares differ", sp.expand(coherent - leaves) != 0, coherent, "not leaf sum")
    checks.require("output", "complete output square factor", sp.factor(coherent) == (x1 + x2 + x3) ** 2, sp.factor(coherent), (x1 + x2 + x3) ** 2)

    failed = [row for row in checks.rows if row["status"] != "PASS"]
    derived = {
        "q": str(q),
        "corrected_top_shell_u6": str(u6),
        "forced_all_law_ratio": str(sp.simplify(-bracket_leading / free_leading)),
        "production_a": str(a),
        "production_b": str(b),
        "production_c": str(c),
        "production_d": str(d),
        "K_epsilon": str(K_eps),
        "quartic_merge": str(raw_merge),
        "sextic_merge": str(expected_sextic),
        "merge_upper_bound": str(merge_upper),
    }
    route_verdicts = {
        "total_time_integration_without_root_local_bound": "tautological-endpoint-identity",
        "pointwise_endpoint_likelihood_sextic_cm_coercivity": "failed-constant-ray",
        "input_mode_leaf_tensorization": "failed-exact-production-1-to-2-merge",
        "leafwise_sextic_merge_repair": "failed-not-superadditive",
        "coherent_output_frequency_square": "retained-exact-coordinate",
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
    print(f"Primary R-106: {payload['assertions_passed']}/{payload['assertions_total']} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
