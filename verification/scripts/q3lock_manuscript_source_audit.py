#!/usr/bin/env python3
"""Exact Q3 model-comparison and source-normalization diagnostics.

Enumerate the input Q3 graph; do not paste its derived quartic energies.
Source roles and labels are structural checks, not theorem certification.
Run prior checkers in memory and preserve all historical output bytes.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import os
import re
import runpy
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-source-audit-260907.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_composition_audit.py"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUNS = tuple(RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
                 for part in ("content", "loop", "dlr", "infrared", "collective", "composition"))
OUT = RUNS / "2026-09-07-q3lock-manuscript-source-audit/result.json"
INTERNAL_DIM = 3  # Model input: vertices of Q3 index the internal coordinates.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-symbolic"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    vertices = tuple(product((0, 1), repeat=INTERNAL_DIM))
    edges = tuple((i, j) for i, j in combinations(range(len(vertices)), 2)
                  if sum(a != b for a, b in zip(vertices[i], vertices[j])) == 1)
    n = len(vertices)
    g, lam = s.symbols("g lambda", positive=True)

    def quartic(q):
        return s.expand(g*sum(x**4 for x in q)/4 + lam*sum(
            (q[i]-q[j])**2*(q[i]**2+q[j]**2) for i, j in edges)/4)

    basis = tuple(s.Integer(i == 0) for i in range(n))
    unit = (1/s.sqrt(n),)*n
    wb, wu = quartic(basis), quartic(unit)
    check("equal-norm-witnesses", sum(x*x for x in basis) == sum(x*x for x in unit) == 1, n)
    # These right sides are printed-formula test oracles, not input energies.
    check("basis-energy", s.simplify(wb-(g+3*lam)/4) == 0, wb)
    check("collective-unit-energy", s.simplify(wu-g/32) == 0, wu)
    gap = s.simplify(wb-wu)
    check("nonradial-gap", s.simplify(gap-(7*g/32+3*lam/4)) == 0 and gap.is_positive, gap)
    check("zero-locking-is-not-radial", gap.subs(lam, 0).is_positive, gap.subs(lam, 0), "limit-fixture")
    q = s.symbols(f"q0:{n}", real=True)
    check("global-parity", s.expand(quartic(q)-quartic(tuple(-x for x in q))) == 0, "global parity")
    check("lambda-zero-decouples", s.expand(quartic(q).subs(lam, 0)-g*sum(x**4 for x in q)/4) == 0,
          "different zero-locking model", "limit-fixture")
    x, y = s.symbols("x y", real=True)
    edge = lam*(x-y)**2*(x*x+y*y)/4
    expansion = lam*(x**4+y**4-2*x**3*y+2*x*x*y*y-2*x*y**3)/4
    check("edge-expansion", s.expand(edge-expansion) == 0, s.expand(edge))
    mixed = s.diff(edge, x, y)
    check("edge-mixed-derivative", s.simplify(
        mixed-lam*(-3*x*x/2+2*x*y-3*y*y/2)) == 0, s.expand(mixed))
    check("mixed-derivative-not-constant", s.diff(mixed, x, 2) != 0, s.diff(mixed, x, 2),
          "hostile-bilinear-reduction")
    check("bilinear-mutant-rejected", s.simplify(mixed.subs({x: 1, y: 0})
                                               -mixed.subs({x: 0, y: 0})) != 0,
          "a constant pair Hessian cannot match both points", "hostile-bilinear-reduction")

    beta, m, theta, c, root = s.symbols("beta m theta c root", positive=True)
    beta_at_root = 4*m*theta*root*s.tanh(root)
    lower = theta*s.tanh(root)/root
    lhs = s.simplify(2*beta_at_root*c*lower)
    check("standard-threshold-shape", s.simplify(lhs-8*m*c*theta**2*s.tanh(root)**2) == 0, lhs)
    check("threshold-eight-not-spin-count", not lhs.has(g, lam) and
          s.simplify(lhs/(m*c*theta**2*s.tanh(root)**2)) == 8, "2 times 4; no component-count input")
    D = s.symbols("D", positive=True, integer=True)
    check("unitary-mass-jacobian", s.simplify(m**(-D/2)*m**(D/2)) == 1, "z=sqrt(m) q")
    check("kinetic-mass-scaling", s.simplify(m/(2*m)) == s.Rational(1, 2), "chain rule factor m")
    check("free-kernel-prefactor", s.simplify(
        m**(D/2)*(2*s.pi*beta)**(-D/2)/(m/(2*s.pi*beta))**(D/2)) == 1,
        "coordinate kernel Jacobian m^(D/2)")
    check("wrong-mass-prefactor-rejected", (m**(D/2)).subs({m: 4, D: 2}) != 1,
          "mass-one prefactor rejected", "hostile-mass-fixture")

    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", tex))
    cites = {key.strip() for group in re.findall(
        r"\\cite(?:\[[^\]]*\])*\{([^}]+)\}", tex) for key in group.split(",")}
    bib = set(re.findall(r"\\bibitem\{([^}]+)\}", tex))
    check("all-reference-labels-resolve", not refs-labels, sorted(refs-labels), "structure-only")
    check("optional-locator-citations-resolve", not cites-bib, sorted(cites), "structure-only")
    for label in ("eq:fk-harmonic-bridge-density", "eq:standard-threshold-comparison",
                  "eq:nonradial-witness", "eq:nonbilinear-scalar-obstruction"):
        check("new-label-"+label, label in labels, label, "structure-only")
    ledger = (PAPER/"imported-source-ledger.md").read_text(encoding="utf-8")
    for role in ("S-FK", "KP-G", "KP-DLR", "FSS-GD"):
        check("current-source-role-"+role, "### "+role+":" in ledger, role, "structure-only")
    check("review-not-certified", "independent analytic acceptance is OPEN" in ledger, "OPEN",
          "structure-only")

    old = {path: digest(path) for path in OLD_RUNS}
    integrated = runpy.run_path(str(PRIOR), run_name="q3lock_composition_readonly")["build_payload"]()
    for path, before in old.items():
        check("historical-output-"+path.parent.name, digest(path) == before, before, "provenance-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, *OLD_RUNS,
               PAPER/"manuscript.tex", PAPER/"imported-source-ledger.md",
               PAPER/"theorem-applicability-audit.md", PAPER/"literature-crosswalk.md",
               PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-source-audit/1.0", "status": "PASS",
            "claim_bearing": False, "assertions_passed": len(rows), "assertions": rows,
            "integrated_composition_checks": integrated,
            "source_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
            "scope": "Exact finite model/scaling and structural diagnostics only; no analytic acceptance or novelty certificate."}


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
    print(f"Q3LOCK manuscript source audit: PASS {payload['assertions_passed']} checks; "
          f"integrated composition {payload['integrated_composition_checks']['assertions_passed']}; "
          f"historical outputs preserved {len(OLD_RUNS)}")
    print(OUT.relative_to(ROOT).as_posix())
