#!/usr/bin/env python3
"""Exact Q3LOCK draft checks; not an infinite-volume proof certificate.

Conventions: rho=exp(-S)/Z, eight coordinates indexed by Q3, energy source h.
Differentiate actual pair polynomials and integrate onsite polynomials by
Gaussian moments. Test transcription mutations and bind the inspected draft.
All displayed numeric formula constants below are independent test oracles;
the measured coefficients are computed from the graph and polynomial.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import os
import re
import tempfile

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
NOTE = ROOT / "strategy/q3lock-manuscript-content-repair-260906.md"
OUT = ROOT / ("claims/C6-SPACETIME-SIGNATURE/runs/"
              "2026-09-06-q3lock-manuscript-content-audit/result.json")
INTERNAL_DIM = 3  # Model input: the internal cube Q3.
SPACE_DIM = 3  # Model input: spatial nearest-neighbor lattice.


def gaussian_mean(poly, variables, variance):
    """Integrate an explicit polynomial against independent centered Gaussians."""
    total = s.S.Zero
    for powers, coefficient in s.Poly(s.expand(poly), *variables).terms():
        moment = s.S.One
        for degree in powers:
            if degree % 2:
                moment = s.S.Zero
                break
            if degree:
                moment *= s.factorial2(degree - 1) * variance ** (degree // 2)
        total += coefficient * moment
    return s.expand(total)


def document_errors(tex):
    errors = []
    correct_sign = (r"\partial_i\partial_j\log\rho_N"
                    "\n =-\\partial_i\\partial_j S_N\\geq0")
    if correct_sign not in tex or r"-\partial_i\partial_j\log\rho_N" in tex:
        errors.append("log-density-sign")
    if r"$p_{\beta,L}$ is real analytic" not in tex or re.search(
            r"p_\{\\beta,L\}.{0,40}is entire", tex):
        errors.append("pressure-analyticity")
    entries = re.split(r"\\bibitem\{([^}]+)\}", tex)[1:]
    bib = dict(zip(entries[::2], entries[1::2]))
    expected = {  # Verified primary-source metadata, not mathematical inputs.
        "KP": ("Y.~Kozitsky and T.~Pasurek",
               "Euclidean Gibbs Measures of Interacting Quantum Anharmonic Oscillators"),
        "KKK": ("A.~Kargol, Y.~Kondratiev, and Y.~Kozitsky",
                "Phase Transitions and Quantum Stabilization in Quantum Anharmonic Crystals"),
        "KK-asym": ("A.~Kargol and Y.~Kozitsky",
                    "A phase transition in a quantum crystal with asymmetric potentials"),
    }
    for key, pieces in expected.items():
        if any(piece not in bib.get(key, "") for piece in pieces):
            errors.append("bibliography-" + key)
    return errors


def build_payload():
    rows = []

    def check(name, condition, evidence):
        assert bool(condition), (name, evidence)
        rows.append({"name": name, "pass": True, "evidence": str(evidence)})

    x, y = s.symbols("x y", real=True)
    lam, c, eps, m, k, g = s.symbols("lambda c epsilon m k g", positive=True)
    r, a = s.symbols("r a", real=True)
    w = lam * (x-y)**2 * (x*x+y*y) / 4
    mixed = -s.diff(w, x, y)
    oracle = lam * ((x+y)**2 + 5*(x-y)**2) / 4
    check("q3-mixed-hessian", s.expand(mixed-oracle) == 0, s.expand(mixed))
    for name, coefficient in (("spatial", eps*c), ("temporal", m/eps)):
        log_bond = -coefficient * (x-y)**2 / 2
        actual = s.diff(log_bond, x, y)
        check(name + "-log-density-sign", s.simplify(actual-coefficient) == 0, actual)
        check(name + "-old-sign-rejected", (-actual).is_negative, -actual)
    check("q3-old-sign-rejected", (-mixed).subs({x: 1, y: 1}).is_negative,
          (-mixed).subs({x: 1, y: 1}))  # Hostile fixture coordinates.
    check("scalar-fourth-moment", gaussian_mean(x**4, (x,), k) == 3*k*k,
          gaussian_mean(x**4, (x,), k))  # Independent Wick oracle.
    check("internal-edge-moment", gaussian_mean(4*w/lam, (x, y), k) == 8*k*k,
          gaussian_mean(4*w/lam, (x, y), k))
    vertices = tuple(product((0, 1), repeat=INTERNAL_DIM))
    edges = [(i, j) for i, j in combinations(range(len(vertices)), 2)
             if sum(u != v for u, v in zip(vertices[i], vertices[j])) == 1]
    q = s.symbols(f"q0:{len(vertices)}", real=True)
    polynomial = (r-a)*sum(t*t for t in q)/2 + g*sum(t**4 for t in q)/4
    polynomial += lam*sum((q[i]-q[j])**2*(q[i]**2+q[j]**2)
                          for i, j in edges)/4
    onsite_mean = gaussian_mean(polynomial, q, k)
    spatial_mean = SPACE_DIM * len(vertices) * gaussian_mean(c*(x-y)**2/2, (x, y), k)
    check("internal-graph-edge-count", len(edges) == len(vertices)*INTERNAL_DIM//2, len(edges))
    check("gaussian-quadratic-coefficient", onsite_mean.coeff(r) == 4*k, onsite_mean.coeff(r))
    check("gaussian-scalar-quartic-coefficient", onsite_mean.coeff(g) == 6*k*k, onsite_mean.coeff(g))
    check("gaussian-locking-coefficient", onsite_mean.coeff(lam) == 24*k*k, onsite_mean.coeff(lam))
    check("gaussian-spatial-coefficient", spatial_mean == 24*c*k, spatial_mean)
    check("source-component-budget", s.simplify(len(vertices)/s.sqrt(len(vertices))**s.Rational(4, 3)) == 2,
          s.simplify(len(vertices)/s.sqrt(len(vertices))**s.Rational(4, 3)))
    check("entire-mgf-need-not-be-zero-free", s.cosh(s.I*s.pi/2) == 0, "cosh(i*pi/2)=0; generic MGF only")

    tex = (PAPER / "manuscript.tex").read_text(encoding="utf-8")
    check("corrected-document", not document_errors(tex), document_errors(tex))
    sign_mutant = tex.replace(r"\partial_i\partial_j\log\rho_N", r"-\partial_i\partial_j\log\rho_N")
    check("document-sign-mutation", "log-density-sign" in document_errors(sign_mutant), document_errors(sign_mutant))
    analytic_mutant = tex.replace(r"$p_{\beta,L}$ is real analytic", r"$p_{\beta,L}$ is entire")
    check("document-entire-mutation", "pressure-analyticity" in document_errors(analytic_mutant), document_errors(analytic_mutant))
    bib_mutant = tex.replace("A.~Kargol, Y.~Kondratiev, and Y.~Kozitsky", "J.~Kargol, Y.~Kondratiev, and T.~Kozitsky")
    check("document-author-mutation", "bibliography-KKK" in document_errors(bib_mutant), document_errors(bib_mutant))
    check("gaussian-bound-transcription", r"C_J&=4|r-a|K+24cK+(6g+24\lambda)K^2" in tex, "derived coefficients match display")
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    refs = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", tex)
    check("unique-labels", len(labels) == len(set(labels)), len(labels))
    check("resolving-tex-references", not set(refs)-set(labels), sorted(set(refs)-set(labels)))
    cites = {key for group in re.findall(r"\\cite\{([^}]+)\}", tex) for key in group.split(",")}
    bibkeys = set(re.findall(r"\\bibitem\{([^}]+)\}", tex))
    check("resolving-citations", not cites-bibkeys, sorted(cites))
    check("environment-counts", Counter(re.findall(r"\\begin\{([^}]+)\}", tex)) ==
          Counter(re.findall(r"\\end\{([^}]+)\}", tex)), "begin/end environment multisets")
    for doc in ("proof-audit.md", "theorem-applicability-audit.md"):
        md = (PAPER/doc).read_text(encoding="utf-8")
        anchored = set(re.findall(r"`((?:eq|sec|tab):[^`]+)`", md))
        check("audit-labels-" + doc, not anchored-set(labels), sorted(anchored-set(labels)))
    for label in ("eq:two-sided-pressure", "eq:retained-quartic", "eq:seam-trace-sandwich", "eq:pressure-seam-rate"):
        check("pressure-proof-step-" + label, label in labels, label)
    manifest = json.loads((PAPER/"verification/package-manifest.json").read_text(encoding="utf-8"))
    check("draft-scope", manifest["claim_status"]["tier"] == "T0" and
          not manifest["claim_status"]["claim_bearing"], manifest["claim_status"])
    check("pdf-deferred", manifest["pdf_status"] == "DEFERRED" and not list(PAPER.rglob("*.pdf")), "no paper PDF")
    sources = [Path(__file__).resolve(), NOTE] + sorted(PAPER.rglob("*.md")) + [PAPER/"manuscript.tex", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-content-audit/1.0", "status": "PASS",
            "claim_bearing": False, "assertions_passed": len(rows), "assertions": rows,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Exact local polynomial and manuscript regression checks; no analytic closure or signed review."}


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
    print(f"Q3LOCK manuscript content audit: PASS {len(payload['assertions'])}/{len(payload['assertions'])}")
    print(OUT.relative_to(ROOT).as_posix())
