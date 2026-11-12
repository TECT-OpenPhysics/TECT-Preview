#!/usr/bin/env python3
"""Independent local/reduced diagnostic supplied by a separate read-only reviewer.

No primary checker import. Parent added only output/provenance serialization.
python -X utf8 verification/scripts/phy002_link_independent.py --out claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-phy002/independent.json
"""
import argparse
import hashlib
import json
from pathlib import Path

import sympy as s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    x, y, dx, dy = s.symbols("x y dx dy", real=True)
    a, b, m, phi = s.symbols("a b m phi", positive=True, real=True)
    z = x + s.I*y
    dz = dx + s.I*dy
    q_real = s.expand(-s.I*(s.conjugate(z)*dz-z*s.conjugate(dz))/2)
    # Analytic test oracles, not numerical inputs or fitted output.
    assert s.simplify(q_real-(x*dy-y*dx)) == 0
    q1 = q_real.subs({x: a, y: 0, dx: 0, dy: b})
    q2 = q_real.subs({x: a, y: 0, dx: 0, dy: 2*b})
    assert q1 == a*b
    assert q2 == 2*a*b
    sigma = a*(s.cosh(m*phi)+s.I*s.sinh(m*phi))
    derivative = s.diff(sigma, phi)
    residual = s.simplify(s.diff(sigma, phi, 2)-m**2*sigma)
    number = s.simplify(s.expand_complex(sigma*s.conjugate(sigma)))
    charge = s.simplify(-s.I*(s.conjugate(sigma)*derivative-sigma*s.conjugate(derivative))/2)
    halfnorm_derivative = s.simplify(s.diff(number/2, phi))
    assert residual == 0
    assert s.simplify(number-a**2*s.cosh(2*m*phi)) == 0
    assert charge == a**2*m
    assert s.simplify(halfnorm_derivative-a**2*m*s.sinh(2*m*phi)) == 0
    report = {
        "checker": "TECT-PHY-002-independent-real-component-diagnostic",
        "status": "PASS",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "engine": {"name": "sympy", "version": s.__version__},
        "expressions": {
            "Q_real": str(q_real), "initial_N_both": str(a**2),
            "initial_Q": [str(q1), str(q2)], "reduced_residual": str(residual),
            "N": str(number), "Q": str(charge), "d_half_N": str(halfnorm_derivative),
        },
        "scope": "Local effective Cauchy data and the diagnostic equality sigma''-m^2*sigma=0 only; source Eq.66 is approximate.",
        "interpretation": "Identical positive amplitude norms with charges ab and 2ab exclude a fixed nonzero state-independent N/2=cQ assignment on the declared local phase space.",
        "non_claims": [
            "No exact interacting or microscopic solution.",
            "No globally normalizable Fock-state assertion.",
            "No exclusion of derivative-dependent maps or justified restrictions.",
            "No source error bound or physical-time identification.",
            "No adopted TECT model, physical Pre-A, spacetime, QFT or gravity.",
            "No automatic follow-up research authorization.",
        ],
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
