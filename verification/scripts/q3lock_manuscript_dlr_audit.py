#!/usr/bin/env python3
"""Exact finite DLR manuscript diagnostics; not an analytic proof certificate.

Compute model coefficients from graph inputs. Printed numerical formulas used
in equalities are labelled reproduction oracles, never upstream parameters.
Historical draft runs are preserved; earlier checks run only in memory.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import runpy
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-dlr-integration-260906.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_loop_audit.py"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUNS = tuple(RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
                 for part in ("content", "loop"))
OUT = RUNS / "2026-09-06-q3lock-manuscript-dlr-audit/result.json"
INTERNAL_DIM = 3  # Model input: Q3 internal cube.
SPACE_DIM = 3  # Model input: spatial nearest-neighbor lattice.
SOURCES = (
    "strategy/q3lock-dlr-source-tangent-content-260905.md",
    "strategy/q3lock-source-zero-dlr-kernel-determining-class-audit-260905.md",
    "strategy/q3lock-kp-vector-hypothesis-crosswalk-independent-audit-260905.md",
)


def neighbors(site):
    for axis in range(SPACE_DIM):
        for sign in (-1, 1):
            point = list(site)
            point[axis] += sign
            yield tuple(point)


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-symbolic"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    g, b, h, c, kappa, beta = s.symbols("g b h c kappa beta", positive=True)
    x, y = s.symbols("x y", real=True)
    t = s.symbols("t", nonnegative=True)
    vertices = tuple(product((0, 1), repeat=INTERNAL_DIM))
    dimension = len(vertices)
    row_sum = len(tuple(neighbors((0,) * SPACE_DIM))) * c
    quartic = g / (4 * dimension)
    quadratic_budget, source_budget = quartic / 2, quartic / 4
    retained = quartic - quadratic_budget - source_budget
    check("retained-quartic", retained == g/128, retained)  # Printed formula oracle.
    quadratic_max = b*b/(4*quadratic_budget)
    check("quadratic-envelope-completion",
          s.expand(quadratic_max-(b*t*t-quadratic_budget*t**4)
                   -quadratic_budget*(t*t-b/(2*quadratic_budget))**2) == 0,
          quadratic_max)
    check("quadratic-envelope-constant", quadratic_max == 16*b*b/g,
          quadratic_max)  # Independent reproduction oracle.
    maximizer = (h/(4*source_budget))**s.Rational(1, 3)
    source_max = s.simplify(h*maximizer-source_budget*maximizer**4)
    check("source-envelope-stationary", s.simplify(h-4*source_budget*maximizer**3) == 0,
          maximizer)
    check("source-envelope-constant",
          s.simplify(source_max-s.Rational(3, 4)*h**s.Rational(4, 3)*(32/g)**s.Rational(1, 3)) == 0,
          source_max)  # Printed formula oracle; derivative changes from positive to negative.
    edge = (x-y)**2*(x*x+y*y)
    slack_sos = 2*(x*x-y*y)**2+(x+y)**2*(x*x+y*y)
    check("locking-upper-sum-of-squares", s.expand(4*(x**4+y**4)-edge-slack_sos) == 0,
          slack_sos)
    degrees = [sum(sum(a != b_ for a, b_ in zip(v, w)) == 1 for w in vertices)
               for v in vertices]
    check("locking-upper-degree", set(degrees) == {INTERNAL_DIM}, degrees)
    j_half = row_sum/2
    half_a = retained/2
    boundary_max = j_half*j_half/(4*half_a)
    check("boundary-absorption-square",
          s.expand(boundary_max-(j_half*t*t-half_a*t**4)
                   -half_a*(t*t-j_half/(2*half_a))**2) == 0, boundary_max)
    check("boundary-absorption-constant", boundary_max == row_sum**2/(8*retained),
          boundary_max)  # Printed formula oracle.
    theta = kappa/(2*row_sum)
    holder_exponent = s.simplify(theta*row_sum/kappa)
    check("periodic-holder-exponent", holder_exponent == s.Rational(1, 2), holder_exponent)
    C1 = s.symbols("C1", nonnegative=True)
    log_bound = C1/(1-holder_exponent)
    check("finite-moment-log-bound", log_bound == 2*C1, log_bound)

    origin = (0,) * SPACE_DIM
    regions = (
        {origin},
        {origin, (1, 0, 0)},
        set(product((0, 1), repeat=SPACE_DIM)),
        {origin, (1, 0, 0), (0, 1, 0), (-1, 0, 1)},
    )  # Finite geometry fixtures, including nonconvex and disconnected sites.
    for region_id, inside in enumerate(regions):
        total_inside_degree = total_boundary_degree = 0
        for site in sorted(inside):
            adjacent = tuple(neighbors(site))
            internal_degree = sum(z in inside for z in adjacent)
            boundary_degree = len(adjacent)-internal_degree
            total_inside_degree += internal_degree
            total_boundary_degree += boundary_degree
            allocated = c*s.Rational(internal_degree+boundary_degree, 2)
            check(f"region{region_id}-site{site}-allocation", allocated == row_sum/2,
                  {"internal_degree": internal_degree, "boundary_degree": boundary_degree,
                   "coefficient": allocated}, "independent-rational")
        check(f"region{region_id}-ordered-edge-parity", total_inside_degree % 2 == 0,
              total_inside_degree, "independent-rational")
        check(f"region{region_id}-degree-budget",
              c*(total_inside_degree+total_boundary_degree) == len(inside)*row_sum,
              (total_inside_degree, total_boundary_degree), "independent-rational")

    # Source moment maximum: differentiate log(Q^(1/4) exp(-A Q/2)).
    Q = s.symbols("Q", positive=True)
    log_weight = s.log(Q)/4-retained*Q/2
    stationary = s.solve(s.diff(log_weight, Q), Q)[0]
    check("kernel-source-maximizer", stationary == 1/(2*retained), stationary)
    check("kernel-source-log-concavity", s.diff(log_weight, Q, 2).is_negative,
          s.diff(log_weight, Q, 2))
    maximum = s.simplify(stationary**s.Rational(1, 4)*s.exp(-retained*stationary/2))
    check("kernel-source-maximum", s.simplify(maximum-(2*retained*s.E)**(-s.Rational(1, 4))) == 0,
          maximum)
    F, ell = s.symbols("F ell", positive=True)
    radius_squared = s.log(2*F)/ell
    markov_tail = s.simplify(F*s.exp(-ell*radius_squared))
    check("gaussian-sup-ball-markov", markov_tail == s.Rational(1, 2), markov_tail)
    for n in (1, 2, 5):  # Region-size diagnostic inputs.
        reference_event_lower = (1-markov_tail)**n
        check(f"product-ball-{n}", reference_event_lower == s.Rational(1, 2)**n,
              reference_event_lower, "independent-rational")

    nh, nz = s.symbols("N_h N_zero", real=True)
    zh, zz = s.symbols("Z_h Z_zero", positive=True)
    quotient_decomposition = (nh-nz)/zh+nz*(zz-zh)/(zh*zz)
    check("normalized-source-quotient",
          s.simplify(nh/zh-nz/zz-quotient_decomposition) == 0, quotient_decomposition)
    numerator_bound, weight_bound, lower = s.symbols("f_bound M z_lower", positive=True)
    quotient_bound = numerator_bound*weight_bound/lower+numerator_bound*weight_bound/lower
    check("normalized-source-factor", quotient_bound == 2*numerator_bound*weight_bound/lower,
          quotient_bound)
    local_mean, volume = s.symbols("local_mean volume", real=True)
    expected_source = beta*volume*local_mean
    pressure_derivative = s.cancel(expected_source/volume)
    normalized_derivative = s.cancel(pressure_derivative/(dimension*beta))
    check("source-tangent-dictionary", normalized_derivative == local_mean/dimension,
          normalized_derivative)
    for beta_value in (s.Rational(1, 2), s.Rational(3, 2)):
        extra_beta = (beta*normalized_derivative).subs({beta: beta_value, local_mean: 1})
        check(f"extra-beta-rejected-{beta_value}", extra_beta != s.Rational(1, dimension),
              extra_beta, "hostile-fixture")

    # Finite hostile fixtures demonstrate failures, not infinite-volume sufficiency.
    for n in (1, 2, 4, 8):
        amplitude_squared = 4**n
        fast_norm_squared = s.Rational(amplitude_squared, 4**n)
        slow_norm_squared = s.Rational(amplitude_squared, 2**n)
        check(f"reversed-weight-rejected-{n}", fast_norm_squared == 1 and slow_norm_squared == 2**n,
              (fast_norm_squared, slow_norm_squared), "hostile-fixture")
        radius = n-1
        stronger_tail = s.Rational(1, 2)**radius*slow_norm_squared
        check(f"correct-weight-tail-{n}", fast_norm_squared <= stronger_tail,
              (fast_norm_squared, stronger_tail), "independent-rational")
        # mu_n=(1-1/n)delta_0+(1/n)delta_n, mean one, second moment n.
        probability = s.Rational(1, n)
        check(f"unbounded-expectation-without-ui-{n}", probability*n == 1 and probability*n*n == n,
              {"mass_at_n": probability, "mean": probability*n, "second": probability*n*n},
              "hostile-fixture")
    for value, cutoff in product((s.Rational(-3), s.Rational(-1, 2), s.Rational(0), s.Rational(4)),
                                 (s.Rational(1, 2), s.Rational(2))):
        clipped = max(-cutoff, min(value, cutoff))
        check(f"clipping-{value}-{cutoff}", abs(value-clipped) <= value*value/cutoff,
              (abs(value-clipped), value*value/cutoff), "independent-rational")

    old_hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in OLD_RUNS}
    integrated = runpy.run_path(str(PRIOR), run_name="q3lock_previous_loop")["build_payload"]()
    for path, digest in old_hashes.items():
        check("historical-run-preserved-"+path.parent.name,
              hashlib.sha256(path.read_bytes()).hexdigest() == digest, digest, "integrated")
    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    labels = ("eq:tempered-metric", "eq:dlr-potential-envelope", "eq:one-site-exponential",
              "eq:periodic-holder-closure", "eq:dlr-compact-set", "eq:weighted-tail-direction",
              "eq:boundary-coercivity", "eq:dlr-normalizer-lower", "eq:kernel-source-lipschitz",
              "eq:dlr-local-clipping", "sec:dlr-source-tangents")
    for label in labels:
        check("manuscript-"+label, "\\label{"+label+"}" in tex, label, "integrated-structure-only")
    check("finite-M-before-holder", tex.index("First $M<\\infty$") <
          tex.index("\\label{eq:periodic-holder-closure}"), "proof text order", "integrated-structure-only")
    check("normalizer-before-source-quotient", tex.index("\\label{eq:dlr-normalizer-lower}") <
          tex.index("\\label{eq:kernel-source-lipschitz}"), "proof text order", "integrated-structure-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, *OLD_RUNS]
    sources += [ROOT/p for p in SOURCES]
    sources += [PAPER/"manuscript.tex", PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-dlr-audit/1.0", "status": "PASS", "claim_bearing": False,
            "assertions_passed": len(rows), "assertions": rows,
            "integrated_loop_checks": integrated,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Exact finite identities, hostile fixtures and source structure; no analytic closure or signed review."}


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
    loop = payload["integrated_loop_checks"]
    print(f"Q3LOCK manuscript DLR audit: PASS {payload['assertions_passed']} checks; "
          f"integrated loop {loop['assertions_passed']}, prior {loop['integrated_prior_checks']['assertions_passed']}")
    print(OUT.relative_to(ROOT).as_posix())
