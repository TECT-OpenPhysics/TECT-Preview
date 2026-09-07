#!/usr/bin/env python3
"""Exact finite Fourier, kernel and shell checks for the Q3LOCK manuscript.

Use fourth-root Fourier vectors on a diagnostic L=4 torus, rather than the
older polynomial-field implementation. All finite tests are bookkeeping;
they do not certify FSS applicability, loop limits or a phase theorem.
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
NOTE = ROOT / "strategy/q3lock-manuscript-infrared-integration-260906.md"
PRIOR = ROOT / "verification/scripts/q3lock_manuscript_dlr_audit.py"
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
OLD_RUNS = tuple(RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
                 for part in ("content", "loop", "dlr"))
OUT = RUNS / "2026-09-06-q3lock-manuscript-infrared-audit/result.json"
SPACE_DIM = 3  # Model input.
INTERNAL_DIM = 3  # Internal cube Q3 model input.
LENGTH = 4  # Finite diagnostic grid; exact fourth roots, no convergence claim.
SOURCES = (
    "strategy/q3lock-reflection-infrared-content-260905.md",
    "strategy/q3lock-fss-theorem-factor-transcription-audit-260905.md",
    "strategy/q3lock-fss-coupling-rescaling-audit-260905.md",
    "strategy/q3lock-literature-source-freeze-260905.md",
)


def shifted(site, axis, step):
    point = list(site)
    point[axis] = (point[axis]+step) % LENGTH
    return tuple(point)


def build_payload():
    rows = []

    def check(name, condition, actual, lane="independent-exact"):
        assert bool(condition), (name, actual)
        rows.append({"name": name, "pass": True, "lane": lane, "actual": str(actual)})

    vertices = tuple(product(range(LENGTH), repeat=SPACE_DIM))
    volume = len(vertices)
    roots = tuple(s.expand_complex(s.exp(2*s.pi*s.I*k/LENGTH)) for k in range(LENGTH))
    beta, coupling, parameter, g = s.symbols("beta c t g", positive=True)
    components = len(tuple(product((0, 1), repeat=INTERNAL_DIM)))
    for mesh in (4, 6, 8):  # Finite time-scaling fixtures.
        epsilon = beta/mesh
        quartic = (g/(4*epsilon))/(components*mesh)
        check(f"prior-quartic-{mesh}", s.simplify(quartic-g/(32*beta)) == 0,
              quartic)  # Independently reproduced manuscript oracle.
        norm_u_squared = sum(s.Rational(1, components) for _ in range(components))
        source_time_factor = sum(epsilon*norm_u_squared for _ in range(mesh))
        check(f"source-time-factor-{mesh}", source_time_factor == beta, source_time_factor)

    for wave in vertices:
        field = {y: roots[sum(a*b for a, b in zip(wave, y)) % LENGTH] for y in vertices}
        grad = {(y, j): field[shifted(y, j, -1)]-field[y]
                for y in vertices for j in range(SPACE_DIM)}
        lap_field = {y: s.expand(sum(grad[(shifted(y, j, 1), j)]-grad[(y, j)]
                                    for j in range(SPACE_DIM))) for y in vertices}
        eigenvalue = s.simplify(sum(2-2*s.cos(2*s.pi*k/LENGTH) for k in wave))
        check(f"mode{wave}-laplacian", all(lap_field[y] == eigenvalue*field[y] for y in vertices),
              eigenvalue)
        norm_squared = sum(s.conjugate(v)*v for v in field.values())
        check(f"mode{wave}-fourier-norm", norm_squared == volume, norm_squared)
        if eigenvalue == 0:
            check("constant-mode-excluded", wave == (0,)*SPACE_DIM and all(v == 0 for v in grad.values()),
                  "G annihilates the constant mode; inverse is restricted")
            continue
        check(f"mode{wave}-zero-sum", sum(field.values()) == 0, sum(field.values()))
        edge_preimage = {edge: value/eigenvalue for edge, value in grad.items()}
        divergence = {y: s.expand(sum(edge_preimage[(shifted(y, j, 1), j)]-edge_preimage[(y, j)]
                                      for j in range(SPACE_DIM))) for y in vertices}
        check(f"mode{wave}-poisson-source", divergence == field, "B G L^-1 f = f")
        energy = s.simplify(sum(s.conjugate(value)*value for value in edge_preimage.values()))
        check(f"mode{wave}-poisson-energy", energy == volume/eigenvalue, energy)
        check(f"mode{wave}-vertex-norm-rejected", energy != norm_squared,
              (energy, norm_squared), "hostile-fixture")
        real_energy = sum(s.re(value)**2 for value in edge_preimage.values())
        imag_energy = sum(s.im(value)**2 for value in edge_preimage.values())
        check(f"mode{wave}-complex-split", s.simplify(real_energy+imag_energy-energy) == 0,
              (real_energy, imag_energy, energy))
        mgf_coefficient = beta*energy/(2*coupling)
        covariance_bound = s.simplify(2*mgf_coefficient/(beta*beta*norm_squared))
        E_p = sum(1-s.cos(2*s.pi*k/LENGTH) for k in wave)
        check(f"mode{wave}-infrared-factor", s.simplify(covariance_bound-1/(2*beta*coupling*E_p)) == 0,
              covariance_bound)  # Printed Fourier-bound oracle, not an input eigenvalue.

    edges = [(y, shifted(y, j, 1)) for y in vertices for j in range(SPACE_DIM)]
    for axis in range(SPACE_DIM):
        def reflected(y):
            answer = list(y)
            answer[axis] = LENGTH-1-answer[axis]
            return tuple(answer)
        plus = {y for y in vertices if y[axis] < LENGTH//2}
        crossing = [(y, z) for y, z in edges if (y in plus) != (z in plus)]
        check(f"reflection{axis}-involution", all(reflected(reflected(y)) == y for y in vertices), "involution")
        check(f"reflection{axis}-halves", {reflected(y) for y in plus} == set(vertices)-plus, len(plus))
        check(f"reflection{axis}-crossing", all(reflected(y) == z for y, z in crossing), len(crossing))
        check(f"reflection{axis}-two-planes", len(crossing) == 2*LENGTH**(SPACE_DIM-1), len(crossing))

    # Rational Gaussian-kernel fixture: c=2 log(2), integer point coordinates.
    # The values 2^(-||v-w||^2) are exact, not rounded exponentials.
    points = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, -1, 2))
    for rank in range(1, len(points[0])+1):
        kernel = s.Matrix([[s.Rational(1, 2)**sum((v[j]-w[j])**2 for j in range(rank))
                            for w in points] for v in points])
        for size in range(1, len(points)+1):
            for selected in combinations(range(len(points)), size):
                determinant = kernel.extract(selected, selected).det()
                check(f"rank{rank}-gram-minor{selected}", determinant >= 0, determinant)
    delta, h_edge = s.symbols("delta h_edge", real=True)
    original = coupling*delta**2/2-h_edge*delta
    completed = coupling*(delta-h_edge/coupling)**2/2-h_edge**2/(2*coupling)
    check("coupling-rescaled-completion", s.expand(original-completed) == 0, completed)
    wrong = coupling*(delta-h_edge)**2/2-h_edge**2/(2*coupling)
    wrong_residual = (original-wrong).subs({coupling: 2, delta: 3, h_edge: 1})
    check("unscaled-bond-field-rejected", wrong_residual != 0, wrong_residual, "hostile-fixture")

    n = s.symbols("n", positive=True, integer=True)
    shell_polynomial = s.expand((2*n+1)**SPACE_DIM-(2*n-1)**SPACE_DIM)
    check("shell-polynomial", shell_polynomial == 24*n*n+2, shell_polynomial)  # Reproduction oracle.
    for radius in range(1, 7):
        count = sum(max(map(abs, y)) == radius
                    for y in product(range(-radius, radius+1), repeat=SPACE_DIM))
        check(f"shell-enumeration-{radius}", count == shell_polynomial.subs(n, radius), count)
    # Analytic input from sin concavity: E(p)>=2 |p|^2/pi^2.
    sine_coefficient = 2/s.pi**2
    integer_coefficient = s.simplify(sine_coefficient*(2*s.pi)**2)
    shell_sup = shell_polynomial.subs(n, 1)
    discrete_coefficient = s.simplify(shell_sup/(integer_coefficient*2*s.pi))
    check("discrete-tail-coefficient", discrete_coefficient == 13/(8*s.pi), discrete_coefficient)
    sphere_area = 2*s.pi**s.Rational(SPACE_DIM, 2)/s.gamma(s.Rational(SPACE_DIM, 2))
    continuous_coefficient = s.simplify(sphere_area*(1/sine_coefficient)*
                                      s.sqrt(SPACE_DIM)**(SPACE_DIM-2)/
                                      ((2*s.pi)**SPACE_DIM*(SPACE_DIM-2)))
    check("continuous-tail-coefficient", continuous_coefficient == s.sqrt(3)/4, continuous_coefficient)
    for length, delta_over_pi in product((4, 6, 16), (s.Rational(1, 10), s.Rational(1, 5), s.Rational(1, 2))):
        last_shell = int(s.floor(delta_over_pi*length/2))
        majorant = sum(shell_polynomial.subs(n, j)/(integer_coefficient*length*j*j)
                       for j in range(1, last_shell+1))
        bound = discrete_coefficient*s.pi*delta_over_pi
        check(f"discrete-tail-L{length}-ratio{delta_over_pi}", majorant <= bound,
              {"last_shell": last_shell, "majorant": majorant, "bound": bound})
        if last_shell == 0:
            check(f"empty-tail-L{length}-ratio{delta_over_pi}", majorant == 0, majorant)

    old_hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in OLD_RUNS}
    integrated = runpy.run_path(str(PRIOR), run_name="q3lock_prior_dlr")["build_payload"]()
    for path, digest in old_hashes.items():
        check("historical-run-preserved-"+path.parent.name,
              hashlib.sha256(path.read_bytes()).hexdigest() == digest, digest, "integrated")
    tex = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    labels = ("eq:rp-local-measure", "eq:hilbert-kernel-positive", "eq:spatial-reflection-positive",
              "eq:fss-theorem-input", "eq:fss-scaled-action", "eq:fss-prior-coercivity",
              "eq:fss-poisson-energy", "eq:fss-square-shift", "eq:fss-mesh-mgf", "eq:fss-source-ui",
              "eq:duhamel-two-time", "eq:infrared-continuous-tail", "eq:infrared-discrete-tail",
              "eq:infrared-subtraction")
    for label in labels:
        check("manuscript-"+label, "\\label{"+label+"}" in tex, label, "integrated-structure-only")
    sources = [Path(__file__).resolve(), NOTE, PRIOR, *OLD_RUNS]
    sources += [ROOT/p for p in SOURCES]
    sources += [PAPER/"manuscript.tex", PAPER/"STATUS.md", PAPER/"verification/package-manifest.json"]
    return {"schema": "tect/q3lock-manuscript-infrared-audit/1.0", "status": "PASS", "claim_bearing": False,
            "assertions_passed": len(rows), "assertions": rows,
            "integrated_dlr_checks": integrated,
            "source_hashes": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "scope": "Exact finite Fourier, kernel, shell and source checks; no analytic closure or signed external acceptance."}


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
    dlr = payload["integrated_dlr_checks"]
    loop = dlr["integrated_loop_checks"]
    print(f"Q3LOCK manuscript infrared audit: PASS {payload['assertions_passed']} checks; "
          f"integrated DLR {dlr['assertions_passed']}, loop {loop['assertions_passed']}, "
          f"prior {loop['integrated_prior_checks']['assertions_passed']}")
    print(OUT.relative_to(ROOT).as_posix())
