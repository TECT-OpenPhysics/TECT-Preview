#!/usr/bin/env python3
"""Exact scalar Gaussian and manuscript checks for the Q3LOCK loop passage.

Compute precision inverses with rational arithmetic independently of the
older Fourier implementation. Reuse the old draft checker only in a labelled
integrated lane and preserve its old result bytes. Finite fixtures and source
labels do not prove weak convergence or replace an external proof review.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import os
import runpy
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-loop-integration-260906.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_content_audit.py"
OLD_RUN = ROOT / ("claims/C6-SPACETIME-SIGNATURE/runs/"
                  "2026-09-06-q3lock-manuscript-content-audit/result.json")
OUT = ROOT / ("claims/C6-SPACETIME-SIGNATURE/runs/"
             "2026-09-06-q3lock-manuscript-loop-audit/result.json")
Q = s.Rational
MESHES = (4, 6, 8)  # Finite diagnostic mesh inputs.
PARAMETERS = ((Q(1), Q(1), Q(1)), (Q(3, 2), Q(5, 3), Q(2, 5)))  # beta,m,a.
SOURCES = (
    "strategy/q3lock-p06-gaussian-weak-limit-quantitative-audit-260905.md",
    "strategy/q3lock-harmonic-residual-reconciliation-260905.md",
    "strategy/q3lock-finite-volume-pressure-content-260905.md",
    "strategy/q3lock-continuous-loop-fkg-content-260905.md",
)


def cycle_laplacian(n):
    matrix = s.zeros(n)
    for j in range(n):
        edge = s.zeros(n, 1)
        edge[j], edge[(j+1) % n] = 1, -1
        matrix += edge * edge.T
    return matrix


def interpolation_weights(phase, n):
    """Periodic linear evaluation vector; phase is time divided by beta."""
    scaled = (phase % 1) * n
    cell = int(s.floor(scaled))
    fraction = scaled-cell
    weights = s.zeros(n, 1)
    weights[cell] = 1-fraction
    weights[(cell+1) % n] += fraction
    return weights


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-rational"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    for n in MESHES:
        lap = cycle_laplacian(n)
        constant_projection = s.ones(n) / n
        pseudoinverse = (lap+constant_projection).inv()-constant_projection
        check(f"N{n}-constant-mode-singular", lap.det() == 0, lap.det())
        check(f"N{n}-pseudoinverse", lap*pseudoinverse == s.eye(n)-constant_projection,
              "L Lplus = I-Pconstant")
        # Formula is an independent reproduction oracle, not a covariance input.
        check(f"N{n}-massless-diagonal", pseudoinverse[0, 0] == Q(n*n-1, 12*n),
              pseudoinverse[0, 0])
        node_variables = s.Matrix(s.symbols(f"x0:{n}"))
        trapezoid = sum((node_variables[j]+node_variables[(j+1) % n])/2 for j in range(n))
        check(f"N{n}-cyclic-source-integration", s.expand(trapezoid-sum(node_variables)) == 0,
              "integrated polygon equals cyclic vertex sum after multiplying by epsilon")
        phases = (Q(0), Q(1, 3*n), Q(4, 3*n), Q(1, 2), 1-Q(1, 3*n), Q(1))
        for i, phase in enumerate(phases):
            weights = interpolation_weights(phase, n)
            check(f"N{n}-interpolation-{i}", sum(weights) == 1 and all(w >= 0 for w in weights),
                  list(weights))
        check(f"N{n}-periodic-endpoint", interpolation_weights(Q(0), n) == interpolation_weights(Q(1), n),
              "time zero and beta evaluation vectors agree")

        for parameter_id, (beta, mass, rigidity) in enumerate(PARAMETERS):
            epsilon = beta/n
            precision = (mass/epsilon)*lap+rigidity*epsilon*s.eye(n)
            covariance = precision.inv()
            key = f"N{n}-P{parameter_id}"
            check(key+"-inverse", precision*covariance == s.eye(n), "exact inverse")
            bound = 1/(beta*rigidity)+beta/(12*mass)  # Independently checked formula oracle.
            check(key+"-diagonal", covariance[0, 0] <= bound, (covariance[0, 0], bound))
            zero_mode = s.ones(n, 1)/n
            check(key+"-retained-zero-mode", (zero_mode.T*covariance*zero_mode)[0] == 1/(beta*rigidity),
                  (zero_mode.T*covariance*zero_mode)[0])
            for j in range(1, n//2+1):
                increment = s.zeros(n, 1)
                increment[0], increment[j] = 1, -1
                variance = (increment.T*covariance*increment)[0]
                resistance = (increment.T*pseudoinverse*increment)[0]
                check(key+f"-resistance-{j}", resistance == Q(j*(n-j), n), resistance)
                check(key+f"-vertex-increment-{j}", variance <= epsilon*resistance/mass <= epsilon*j/mass,
                      (variance, epsilon*resistance/mass, epsilon*j/mass))
            for pair_id, (left, right) in enumerate(combinations(phases, 2)):
                delta = abs(left-right)
                distance = beta*min(delta, 1-delta)
                increment = interpolation_weights(left, n)-interpolation_weights(right, n)
                variance = (increment.T*covariance*increment)[0]
                # 14 is a labelled manuscript oracle, derived analytically from (2+sqrt(3))^2.
                bound = (distance/mass if distance <= epsilon else 14*distance/mass)
                check(key+f"-polygon-increment-{pair_id}", 0 <= variance <= bound,
                      {"distance": distance, "variance": variance, "bound": bound})

    check("interpolation-constant", (2+s.sqrt(3))**2 < 14, s.expand((2+s.sqrt(3))**2))
    height = s.symbols("height", positive=True)
    width = height**-8
    t = s.symbols("t", nonnegative=True)
    integrated_fourth = 2*s.integrate((height*(1-t/width))**4, (t, 0, width))
    check("spike-integrated-fourth", s.simplify(integrated_fourth-2/(5*height**4)) == 0,
          integrated_fourth, "hostile-analytic-identity")
    for h in (2, 4, 8):  # Hostile spike-height inputs, not Q3LOCK measure samples.
        check(f"spike-no-point-bound-{h}", integrated_fourth.subs(height, h) < 1 and h > 1,
              {"integrated_fourth": integrated_fourth.subs(height, h), "point_value": h},
              "hostile-fixture")

    old_hash = hashlib.sha256(OLD_RUN.read_bytes()).hexdigest()
    old_checker = runpy.run_path(str(PRIOR), run_name="q3lock_prior_checker")
    integrated = old_checker["build_payload"]()  # Does not invoke its result writer.
    check("previous-audit-result-preserved", hashlib.sha256(OLD_RUN.read_bytes()).hexdigest() == old_hash,
          old_hash, "integrated")
    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    required = ("eq:residual-lower", "eq:gaussian-covariances", "eq:gaussian-diagonal-bound",
                "eq:gaussian-grid-error", "eq:gaussian-interpolated-error", "eq:gaussian-tightness",
                "eq:gaussian-weak-limit", "eq:mesh-normalizer-lower", "eq:compact-riemann-residual",
                "eq:weighted-loop-limit", "sec:fk-identification", "eq:mesh-source-ui",
                "eq:fixed-volume-evaluation-moment", "sec:fkg-loop-passage", "eq:fkg-product-clipping")
    for label in required:
        check("proof-content-"+label, "\\label{"+label+"}" in tex, label, "integrated-structure-only")
    scope_fragments = ("This is weak convergence", "not total-variation convergence",
                       "It is not a spatially uniform", "parity-invariant periodic",
                       "Their $Z_\\Lambda$ in (2.32) is")
    for index, fragment in enumerate(scope_fragments):
        check(f"scope-boundary-{index}", fragment in tex, fragment, "integrated-structure-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, OLD_RUN]
    sources += [ROOT/path for path in SOURCES]
    sources += [PAPER/"manuscript.tex", PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-loop-audit/1.0", "status": "PASS", "claim_bearing": False,
            "assertions_passed": len(rows), "assertions": rows,
            "integrated_prior_checks": integrated,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Finite rational covariance and manuscript consistency only; analytic limit and external review are not certified."}


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
    print(f"Q3LOCK manuscript loop audit: PASS {payload['assertions_passed']} checks; "
          f"integrated prior checks {payload['integrated_prior_checks']['assertions_passed']}")
    print(OUT.relative_to(ROOT).as_posix())
