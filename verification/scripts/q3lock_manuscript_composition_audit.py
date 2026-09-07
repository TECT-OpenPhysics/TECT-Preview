#!/usr/bin/env python3
"""Finite source/threshold/tail and branch-order checks for the Q3LOCK paper.

These symbolic and rational diagnostics do not certify an infinite-volume
phase theorem. The two-point example is an adversarial toy, not Q3LOCK.
Preserve five historical manuscript runs and the frozen R-497 source hashes.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-composition-audit-260906.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_collective_audit.py"
CANONICAL = ROOT / "strategy/q3lock-exp782-independent-result-manifest-260905.json"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUNS = tuple(RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
                 for part in ("content", "loop", "dlr", "infrared", "collective"))
OUT = RUNS / "2026-09-06-q3lock-manuscript-composition-audit/result.json"
INTERNAL_DIM = 3  # Model input: Q3 has 2^3 components.


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-exact"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    beta, m, c, theta, integral, volume = s.symbols("beta m c theta I V", positive=True)
    mean, source = s.symbols("mean h", real=True)
    components = 2**INTERNAL_DIM
    integrated_source = beta*volume*mean
    p_derivative = integrated_source/volume
    P_derivative = s.simplify(p_derivative/(components*beta))
    check("normalized-source-tangent", P_derivative == mean/8, P_derivative)  # Printed oracle.
    check("source-time-square", s.simplify((integrated_source/volume)**2-beta**2*mean**2) == 0,
          (integrated_source/volume)**2)
    check("extra-beta-in-tangent-rejected", (P_derivative-beta*mean/8).subs({beta: 3, mean: 2}) != 0,
          "energy source h, not beta h", "hostile-fixture")

    x = s.symbols("x", positive=True)
    beta_of_x = 4*m*theta*x*s.tanh(x)
    d_beta = theta*s.tanh(x)/x
    delta = d_beta-integral/(2*beta*c)
    A0 = components*c*m*theta**2
    threshold_identity = s.simplify((2*beta*c*delta).subs(beta, beta_of_x))
    check("strict-threshold-identity", s.simplify(threshold_identity-(A0*s.tanh(x)**2-integral)) == 0,
          threshold_identity)
    check("beta-root-monotonicity", s.simplify(s.diff(x*s.tanh(x), x)
                                               -(s.tanh(x)+x/s.cosh(x)**2)) == 0,
          "both terms positive for x>0")
    check("threshold-monotonicity", s.simplify(s.diff(s.tanh(x)**2, x)
                                              -2*s.tanh(x)/s.cosh(x)**2) == 0,
          "positive for x>0")
    for ratio in (s.Rational(1, 4), s.Rational(1, 2), s.Rational(3, 4)):
        # Synthetic I/A0 fixtures, not a numerical value of the lattice integral.
        I_fixture = A0*ratio**2
        beta_star = 4*m*theta*s.atanh(ratio)*ratio
        check(f"ratio{ratio}-threshold-equality", s.simplify(
            threshold_identity.subs({x: s.atanh(ratio), integral: I_fixture})) == 0, beta_star)
        for t_value, sign in ((ratio/2, -1), (ratio, 0), ((1+ratio)/2, 1)):
            residual = s.simplify((A0*t_value**2-I_fixture)/A0)
            check(f"ratio{ratio}-tanh{t_value}-strict-sign", s.sign(residual) == sign, residual)
    rho = s.symbols("rho", positive=True)
    check("A0-equality-cannot-be-strict", s.simplify((A0*rho**2-A0)/A0-(rho**2-1)) == 0,
          "negative for 0<rho<1; no phase-absence inference")
    delta_symbol = s.symbols("delta", positive=True)
    slope_lower = s.simplify(s.sqrt(beta**2*delta_symbol)/(components*beta))
    check("cusp-factor-eight", slope_lower == s.sqrt(delta_symbol)/8, slope_lower)

    z, R, a, offset = s.symbols("z R a offset", positive=True)
    tail_integral = s.integrate(2*z*2*s.exp(-a*(z-offset)), (z, R, s.oo))
    boundary_term = 2*R**2*s.exp(-a*(R-offset))
    tail = s.simplify(tail_integral+boundary_term)
    tail_oracle = 2*s.exp(-a*(R-offset))*(R**2+2*R/a+2/a**2)
    check("exact-squared-tail-integral", s.simplify(tail-tail_oracle) == 0, tail)
    ell = s.symbols("ell", nonnegative=True)
    epsilon = s.symbols("epsilon", positive=True)
    substituted_tail = tail.subs({R: ell+epsilon, offset: ell+epsilon/2})
    check("squared-tail-vanishes", s.limit(substituted_tail, a, s.oo) == 0, "fixed epsilon and test source")
    check("zero-slope-squared-tail", s.limit(substituted_tail.subs(ell, 0), a, s.oo) == 0,
          "ell=0 still has the fixed positive epsilon tail estimate")

    # Exact symmetric two-point law: X=+-beta V b with equal probabilities.
    amplitude = s.symbols("b", positive=True)
    toy_pressure = s.log(s.cosh(beta*volume*amplitude*source))/volume
    toy_slope = s.diff(toy_pressure, source)/(components*beta)
    check("toy-finite-zero-slope", toy_slope.subs(source, 0) == 0, 0)
    positive_source = s.symbols("h_positive", positive=True)
    limit_slope = s.limit(toy_slope.subs(source, positive_source), volume, s.oo)
    check("toy-fixed-positive-source-slope", limit_slope == amplitude/components, limit_slope)
    simultaneous = s.simplify(toy_slope.subs(source, s.log(2)/(beta*amplitude*volume)).rewrite(s.exp))
    check("toy-simultaneous-path-rejected", simultaneous != limit_slope, simultaneous, "hostile-fixture")
    check("toy-simultaneous-ratio", s.simplify(simultaneous/limit_slope) == s.Rational(3, 5),
          simultaneous/limit_slope)  # Exact exp(log 2) reproduction oracle.

    # Rational biased laws; their reflected laws have the opposite mean.
    laws = (((s.Rational(3, 4), 2), (s.Rational(1, 4), -1)),
            ((s.Rational(999, 1000), 1), (s.Rational(1, 1000), 100)))
    for number, law in enumerate(laws):
        check(f"law{number}-normalization", sum(p for p, _ in law) == 1, law)
        mean_value = sum(p*q for p, q in law)
        second = sum(p*q*q for p, q in law)
        lower = mean_value/2  # Chosen weaker positive bound, not a fitted phase mean.
        for excess in (s.Rational(3, 2), s.Rational(2), s.Rational(5)):
            radius = excess*2*second/lower
            clipped = sum(p*min(radius, max(-radius, q)) for p, q in law)
            tail_error = sum(p*abs(q-min(radius, max(-radius, q))) for p, q in law)
            check(f"law{number}-radius{excess}-clip-error", tail_error <= second/radius, tail_error)
            witness_lower = 2*lower-2*second/radius
            check(f"law{number}-radius{excess}-bounded-witness", 2*clipped >= witness_lower > lower,
                  (2*clipped, witness_lower, lower))
        check(f"law{number}-parity-moment", sum(p*(-q) for p, q in law) == -mean_value,
              -mean_value)
    second, lower, excess = s.symbols("C2 lower excess", positive=True)
    witness_at_radius = s.simplify((2*lower-2*second/R-lower).subs(R, 2*second*excess/lower))
    check("bounded-witness-radius-algebra", s.simplify(witness_at_radius-lower*(1-1/excess)) == 0,
          "strictly positive for excess>1")

    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    source_integrity = []
    for item in canonical["source_files"]:
        actual = hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()
        source_integrity.append({"path": item["path"], "expected": item["sha256"], "actual": actual,
                                 "match": actual == item["sha256"]})
    check("frozen-authority-hashes", all(item["match"] for item in source_integrity),
          len(source_integrity), "provenance-only")
    old_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in OLD_RUNS}
    integrated = runpy.run_path(str(PRIOR), run_name="q3lock_prior_collective")["build_payload"]()
    for path, digest in old_hashes.items():
        check("historical-run-preserved-"+path.parent.name,
              hashlib.sha256(path.read_bytes()).hexdigest() == digest, digest, "integrated")
    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    labels = ("eq:composition-source-dictionary", "lem:griffiths-endpoint", "eq:griffiths-squared-tail",
              "eq:composition-liminf-limsup", "eq:parity-specification-intertwining",
              "eq:bounded-phase-witness", "thm:q3lock-composition")
    for label in labels:
        check("manuscript-"+label, "\\label{"+label+"}" in tex, label, "integrated-structure-only")
    for stale in ("operator passages still require full manuscript expansion",
                  "Completing the detailed spatial DLR, infrared and operator passages"):
        check("stale-state-rejected-"+stale, stale not in tex, stale, "integrated-structure-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, CANONICAL, *OLD_RUNS,
               ROOT/"strategy/q3lock-strict-cusp-tangent-content-260905.md",
               PAPER/"manuscript.tex", PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-composition-audit/1.0", "status": "PASS", "claim_bearing": False,
            "assertions_passed": len(rows), "assertions": rows, "integrated_collective_checks": integrated,
            "frozen_source_integrity": source_integrity,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Exact finite and symbolic interface diagnostics; no signed acceptance, Q3LOCK phase computation or release freeze."}


if __name__ == "__main__":
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    collective = payload["integrated_collective_checks"]
    infrared = collective["integrated_infrared_checks"]
    dlr = infrared["integrated_dlr_checks"]
    loop = dlr["integrated_loop_checks"]
    print(f"Q3LOCK manuscript composition audit: PASS {payload['assertions_passed']} checks; "
          f"integrated collective {collective['assertions_passed']}, infrared {infrared['assertions_passed']}, "
          f"DLR {dlr['assertions_passed']}, loop {loop['assertions_passed']}, "
          f"prior {loop['integrated_prior_checks']['assertions_passed']}; "
          f"frozen source hashes {len(payload['frozen_source_integrity'])} verified")
    print(OUT.relative_to(ROOT).as_posix())
