#!/usr/bin/env python3
"""Exact finite/symbolic checks of the Q3LOCK collective manuscript section.

Recompute the common-shift Hessian, logarithmic-mean spectral identities and
the local bounded-coordinate normalization. The finite scalar inequality is
proved analytically in the manuscript, not inferred from these tests. Prior
manuscript payloads are evaluated in memory without rewriting their runs.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import os
import runpy
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-collective-integration-260906.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_infrared_audit.py"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUNS = tuple(RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
                 for part in ("content", "loop", "dlr", "infrared"))
OUT = RUNS / "2026-09-06-q3lock-manuscript-collective-audit/result.json"
INTERNAL_DIM = 3  # Q3 model input.
ENERGY_FIXTURES = ((0, 1), (0, 0, 2), (0, 1, 3, 3))  # Diagnostic inputs.
BETA_FIXTURE = s.log(2)  # Exact rational Gibbs weights for integer energies.


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-exact"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    vertices = tuple(product((0, 1), repeat=INTERNAL_DIM))
    edges = [(i, j) for i, j in combinations(range(len(vertices)), 2)
             if sum(a != b for a, b in zip(vertices[i], vertices[j])) == 1]
    count = len(vertices)
    q = s.symbols(f"q0:{count}", real=True)
    shift, r = s.symbols("t r", real=True)
    coupling, locking, mass, beta, hbar, chi, radius = s.symbols(
        "g lam m beta hbar chi R", positive=True)
    potential = r*sum(v*v for v in q)/2 + coupling*sum(v**4 for v in q)/4
    potential += locking*sum((q[i]-q[j])**2*(q[i]**2+q[j]**2) for i, j in edges)/4
    shifted = potential.subs({v: v+shift for v in q}, simultaneous=True)
    hessian = s.expand(s.diff(shifted, shift, 2).subs(shift, 0)/count)
    internal = sum((q[i]-q[j])**2 for i, j in edges)
    oracle = r+3*coupling*sum(v*v for v in q)/8+locking*internal/8
    check("physical-collective-hessian", s.expand(hessian-oracle) == 0, hessian)
    check("internal-degree", all(sum(i in edge for edge in edges) == INTERNAL_DIM
                                 for i in range(count)), len(edges))
    graph_identity = INTERNAL_DIM*sum(v*v for v in q)-2*sum(q[i]*q[j] for i, j in edges)
    check("internal-quadratic-expansion", s.expand(internal-graph_identity) == 0, graph_identity)
    wrong_hessian = s.expand((hbar*hbar-1)*hessian).subs(
        {hbar: 2, r: -1, coupling: 2, locking: 3, **{v: i+1 for i, v in enumerate(q)}})
    check("extra-hbar-in-hessian-rejected", wrong_hessian != 0, wrong_hessian, "hostile-fixture")

    x = s.symbols("x", positive=True)
    phi = x*s.coth(x)
    derivative_u = s.diff(phi, x)/(2*x)
    derivative_uu = s.diff(derivative_u, x)/(2*x)
    first_oracle = (s.sinh(x)*s.cosh(x)-x)/(2*x*s.sinh(x)**2)
    bracket = 2*x*x-x*s.tanh(x)-s.sinh(x)**2
    second_oracle = s.cosh(x)*bracket/(4*x**3*s.sinh(x)**3)
    check("phi-first-derivative", s.simplify((derivative_u-first_oracle).rewrite(s.exp)) == 0,
          first_oracle)
    check("phi-second-derivative", s.simplify((derivative_uu-second_oracle).rewrite(s.exp)) == 0,
          second_oracle)
    check("phi-zero-value", s.limit(phi, x, 0, dir="+") == 1, s.limit(phi, x, 0, dir="+"))
    check("tanh-lower-derivative", s.simplify(s.diff(s.tanh(x)-x+x**3/3, x)
                                             -(x*x-s.tanh(x)**2)) == 0, "x^2-tanh(x)^2")
    lower_polynomial = s.expand((x+x**3/6)**2+x*(x-x**3/3)-2*x*x)
    check("concavity-bracket-majorant", lower_polynomial == x**6/36, lower_polynomial)
    check("positive-first-numerator", s.simplify(s.diff(s.sinh(x)*s.cosh(x)-x, x)
                                                -2*s.sinh(x)**2) == 0, "2 sinh(x)^2")
    # This verifies the analytic identities, not global concavity by sampling.

    coordinate = s.symbols("Q", real=True)
    clip = radius*s.tanh(coordinate/radius)
    grad_squared = s.diff(clip, coordinate)**2
    check("bounded-coordinate-gradient", s.simplify((grad_squared-s.sech(coordinate/radius)**4)
                                                     .rewrite(s.exp)) == 0, grad_squared)
    c_multiplier = s.simplify(2*beta*grad_squared/(2*mass))
    check("local-beta-m-coefficient", s.simplify(c_multiplier-beta*grad_squared/mass) == 0,
          c_multiplier)
    check("physical-mass-convention", s.simplify((beta/mass).subs(mass, chi/hbar**2)
                                                 -beta*hbar**2/chi) == 0, beta*hbar**2/chi)
    check("missing-beta-rejected", (beta/mass-1/mass).subs({beta: 3, mass: 2}) != 0,
          "beta=3, m=2", "hostile-fixture")
    # Direct differential commutator, independent of the form-identity formula.
    psi = s.Function("psi")(coordinate)
    f = s.Function("f")(coordinate)
    def kinetic(value):
        return -s.diff(value, coordinate, 2)/(2*mass)
    differential = s.expand(2*f*beta*kinetic(f*psi)-f*f*beta*kinetic(psi)
                            -beta*kinetic(f*f*psi))
    check("differential-double-commutator", s.simplify(differential-beta*s.diff(f, coordinate)**2
                                                       *psi/mass) == 0, differential)

    for energies in ENERGY_FIXTURES:
        dimension = len(energies)
        raw = [s.Rational(1, 2)**energy for energy in energies]
        partition = sum(raw)
        probabilities = [value/partition for value in raw]
        H = s.diag(*energies)
        # Real symmetric nontrivial fixture; formula is a labelled test input.
        A = s.Matrix(dimension, dimension, lambda i, j: (i+1)*(j+1)-int(i == j))
        g_value = sum(probabilities[i]*A[i, j]**2 for i in range(dimension) for j in range(dimension))
        b_value = s.S.Zero
        c_value = s.S.Zero
        g_weighted = s.S.Zero
        c_weighted = s.S.Zero
        for i, j in product(range(dimension), repeat=2):
            gap = energies[j]-energies[i]
            mean = probabilities[i] if gap == 0 else (probabilities[i]-probabilities[j])/(BETA_FIXTURE*gap)
            b_value += mean*A[i, j]**2
            c_value += BETA_FIXTURE*gap*(probabilities[i]-probabilities[j])*A[i, j]**2
            x_pair = BETA_FIXTURE*abs(gap)/2
            phi_pair = s.S.One if gap == 0 else x_pair*(2**abs(gap)+1)/(2**abs(gap)-1)
            g_weighted += mean*A[i, j]**2*phi_pair
            c_weighted += mean*A[i, j]**2*x_pair*x_pair
            check(f"spectrum{energies}-pair{i},{j}-mean", mean > 0, mean)
        double = A*(BETA_FIXTURE*H*A-A*BETA_FIXTURE*H)-(BETA_FIXTURE*H*A-A*BETA_FIXTURE*H)*A
        direct = sum(probabilities[i]*double[i, i] for i in range(dimension))
        check(f"spectrum{energies}-matrix-c", s.simplify(c_value-direct) == 0, c_value)
        check(f"spectrum{energies}-g-weights", s.simplify(g_weighted-g_value) == 0, g_value)
        check(f"spectrum{energies}-c-weights", s.simplify(c_weighted-c_value/4) == 0, c_value/4)
        check(f"spectrum{energies}-b-upper", bool(s.simplify(b_value-g_value) <= 0), b_value)
        for cutoff in range(1, dimension+1):
            q_M = sum(probabilities[:cutoff])
            finite_g = sum((probabilities[i]/q_M)*A[i, j]**2
                           for i, j in product(range(cutoff), repeat=2))
            restricted = sum(probabilities[i]*A[i, j]**2 for i, j in product(range(cutoff), repeat=2))
            check(f"spectrum{energies}-cutoff{cutoff}-normalization",
                  s.simplify(q_M*finite_g-restricted) == 0, q_M)
            H_M = H[:cutoff, :cutoff]
            A_M = A[:cutoff, :cutoff]
            commutator_M = BETA_FIXTURE*H_M*A_M-A_M*BETA_FIXTURE*H_M
            double_M = A_M*commutator_M-commutator_M*A_M
            finite_c = sum(probabilities[i]*double_M[i, i]/q_M for i in range(cutoff))
            restricted_c = sum(BETA_FIXTURE*(energies[j]-energies[i])*
                               (probabilities[i]-probabilities[j])*A[i, j]**2
                               for i, j in product(range(cutoff), repeat=2))
            check(f"spectrum{energies}-cutoff{cutoff}-direct-c-normalization",
                  s.simplify(q_M*finite_c-restricted_c) == 0, finite_c)
            for i, j in product(range(cutoff), repeat=2):
                gap = energies[j]-energies[i]
                mean_full = probabilities[i] if gap == 0 else (probabilities[i]-probabilities[j])/(BETA_FIXTURE*gap)
                mean_finite = probabilities[i]/q_M if gap == 0 else ((probabilities[i]-probabilities[j])/q_M)/(BETA_FIXTURE*gap)
                check(f"spectrum{energies}-cutoff{cutoff}-mean{i},{j}",
                      s.simplify(q_M*mean_finite-mean_full) == 0, mean_finite)

    for gap in (1, 2, 4):  # Exact two-level saturation test inputs.
        p0 = 1/(1+s.Rational(1, 2)**gap)
        p1 = 1-p0
        mean = (p0-p1)/(BETA_FIXTURE*gap)
        g_value = p0+p1
        b_value = 2*mean
        c_value = 2*BETA_FIXTURE*gap*(p0-p1)
        x_pair = BETA_FIXTURE*gap/2
        tanh_pair = s.Rational(2**gap-1, 2**gap+1)
        check(f"two-level-{gap}-implicit-argument", s.simplify(c_value/(4*g_value)-x_pair*tanh_pair) == 0,
              c_value/(4*g_value))
        check(f"two-level-{gap}-saturation", s.simplify(b_value-g_value*tanh_pair/x_pair) == 0, b_value)

    raw = [s.Rational(1, 2)**i for i in range(3)]
    diagonal = (1, 0, 2)  # Fixture demonstrating nonmonotone normalized g_M.
    g_cutoffs = [sum(raw[i]*diagonal[i]**2 for i in range(M))/sum(raw[:M]) for M in range(1, 4)]
    check("normalized-monotonicity-rejected", g_cutoffs[0] > g_cutoffs[1] < g_cutoffs[2],
          g_cutoffs, "hostile-fixture")
    H_one, A_one = s.diag(3), s.diag(2)  # One-dimensional test inputs.
    commutator_one = beta*H_one*A_one-A_one*beta*H_one
    double_one = A_one*commutator_one-commutator_one*A_one
    check("finite-CCR-substitution-rejected", s.trace(double_one) != (beta/mass).subs({beta: 3, mass: 2}),
          "a one-dimensional matrix commutator is zero, not beta/m", "hostile-fixture")

    old_hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in OLD_RUNS}
    integrated = runpy.run_path(str(PRIOR), run_name="q3lock_prior_infrared")["build_payload"]()
    for path, digest in old_hashes.items():
        check("historical-run-preserved-"+path.parent.name,
              hashlib.sha256(path.read_bytes()).hexdigest() == digest, digest, "integrated")
    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    labels = ("eq:collective-thermal-energy", "eq:collective-jensen-chain", "eq:collective-graph-expectation",
              "eq:collective-log-mean", "eq:collective-duhamel-spectral", "eq:finite-spectral-c",
              "eq:falk-phi-concavity", "eq:falk-spectral-weights", "eq:finite-falk-bruch",
              "eq:collective-absolute-energy-sums", "eq:collective-local-c", "eq:collective-spectral-cutoff",
              "eq:collective-bounded-falk", "eq:collective-coordinate-cutoff", "eq:collective-loop-clipping")
    for label in labels:
        check("manuscript-"+label, "\\label{"+label+"}" in tex, label, "integrated-structure-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, *OLD_RUNS,
               ROOT/"strategy/q3lock-collective-falk-bruch-content-260905.md",
               PAPER/"manuscript.tex", PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-collective-audit/1.0", "status": "PASS", "claim_bearing": False,
            "assertions_passed": len(rows), "assertions": rows, "integrated_infrared_checks": integrated,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Exact finite and symbolic diagnostics; no infinite-dimensional proof certification or signed acceptance."}


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
    infrared = payload["integrated_infrared_checks"]
    dlr = infrared["integrated_dlr_checks"]
    loop = dlr["integrated_loop_checks"]
    print(f"Q3LOCK manuscript collective audit: PASS {payload['assertions_passed']} checks; "
          f"integrated infrared {infrared['assertions_passed']}, DLR {dlr['assertions_passed']}, "
          f"loop {loop['assertions_passed']}, prior {loop['integrated_prior_checks']['assertions_passed']}")
    print(OUT.relative_to(ROOT).as_posix())
