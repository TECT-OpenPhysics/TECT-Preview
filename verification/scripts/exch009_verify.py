"""Check the exact identities and immutable inputs of the EXCH-009 proof."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
EX = "strategy/physical-candidates/"
P1 = "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R158 = ("claims/A2-FULL-PRODUCTION-WELLPOSED/"
        "charge_ensemble_first_order_shell_transition_manifest.json")
NOTE = ("claims/C6-SPACETIME-SIGNATURE/notes/"
        "common-data-reservoir-tails-261121-v1.0.tex.txt")
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-21-exch009.json"
PINS = {
    EX+"TECT-EXCH-001-contract-v1.json": "d07cb738d40d9b97a3a2341ada94ac13167e4410edd4ece39fb6ba02504f073e",
    EX+"TECT-EXCH-001-result-v1.json": "e932c9a837af12538109490358042f113447d4ed1efa838aebab2f6d7ff8c7cf",
    EX+"TECT-EXCH-007-result-v1.json": "ed7a60d99cbfb0689b0daaeebb4c774131247a9d14de2b5a3f1785e04ee0b2d7",
    EX+"TECT-EXCH-008-witness-v1.json": "407888491b6197e6291f6666a89f1835ed9d9ebcd1e7e735c19d7db4e1698e38",
    P1: "88da7764302b20b0dde6e10902e94b1e26ec3c5274759c7fa51ca6302868b565",
    R158: "82ecf0e8e4e4b3d99cb67fad1655e03d85c63921f9e02deb83bd8ad0a74138e5",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def replay():
    for name, pin in PINS.items():
        if digest(ROOT/name) != pin:
            raise ValueError(f"Changed pinned source: {name}")
    coeff = load(ROOT/P1)["parameters"]
    p1 = load(ROOT/R158)["exact_constants"]
    model = load(ROOT/(EX+"TECT-EXCH-001-contract-v1.json"))["model"]["inserted_parameters"]
    rat = lambda x: F(str(x))
    omega, u, eps = (rat(model[x]) for x in ("omega", "u", "epsilon"))
    c = rat(coeff["gamma"])/6
    rho_star = rat(p1["coexistence_density"])
    Y, Z = (rat(coeff[x]) for x in ("Y", "Z"))
    D = eps**2*rho_star + eps**4/(4*c)
    checks = {}

    def check(label, condition):
        if not bool(condition):
            raise AssertionError(label)
        checks[label] = True

    def zero(x):
        return s.expand(x) == 0

    t, a, v = s.symbols("t a v", real=True)
    check("young_signed_coupling", zero(a*a/4 + eps**2*t*t - eps*a*t - (a/2-eps*t)**2))
    check("sextic_dominates_remainder", zero(
        c*t*(t-rho_star)**2 - eps**2*t*t + D*t
        - c*t*(t-rho_star-eps**2/(2*c))**2))
    check("positive_fourth_order_coefficient", Y > 0)
    check("spectral_square", zero(Y*t*t + Z*t - Y*t*t/2 + Z*Z/(2*Y)
          - Y*(t+Z/Y)**2/2))
    check("original_reservoir_coefficients", omega == u == 1 and eps > 0)
    check("positive_mass_remainder_on_source", rat(p1["transition_chemical_potential_interval_decimal"][0])/2 > D)

    x, y, d1, d2, g1, g2, e1, e2 = s.symbols("x y d1 d2 g1 g2 e1 e2", real=True)
    w, d, g, e = map(s.Matrix, ([x,y], [d1,d2], [g1,g2], [e1,e2]))
    z = w+d
    U = lambda z: omega*z.dot(z)/2 + u*z.dot(z)**2/4
    f = lambda z: (omega+u*z.dot(z))*z
    J = s.Matrix([[0,1],[-1,0]])
    diff = f(z)-f(w)
    B = s.expand(U(z)-U(w)-f(w).dot(d))
    check("quartic_bregman_identity", zero(B - omega*d.dot(d)/2
          - u*(2*w.dot(w)*d.dot(d)+(2*w.dot(d)+d.dot(d))**2)/4))
    check("uniform_quartic_bregman_lower_bound", zero(
        B - omega*d.dot(d)/2 - u*d.dot(d)**2/12
        - u*(2*(x*d2-y*d1)**2 + 6*(w.dot(d)+d.dot(d)/3)**2)/4))
    rem = diff-f(w).jacobian(w)*d
    check("cubic_taylor_remainder", all(zero(z) for z in
          rem-u*(2*w.dot(d)*d+d.dot(d)*w+d.dot(d)*d)))
    check("canonical_radial_velocity_is_tangent", zero(w.dot(J*f(w))))
    check("skew_cancels_in_retained_plane", zero(diff.dot(J*diff)))
    bdot = B.diff(x)*g1+B.diff(y)*g2+B.diff(d1)*(J*diff-e)[0]+B.diff(d2)*(J*diff-e)[1]
    check("relative_energy_chain_rule_and_residual_sign", zero(bdot - rem.dot(g)+diff.dot(e)))
    check("fourth_power_conjugate_identity", zero(s.re((a+s.I*v)**4)-(a**4-6*a*a*v*v+v**4)))

    # Fejer uses a positive normalized convolution, not a new evolution projection.
    # The coefficients of |sum_{j=0}^N z^j|^2/(N+1) agree with the average
    # of the first N+1 sharp interval symbols, including the retained edge.
    for N in (0, 1, 2, 7):
        coeffs = {j: F(sum((k-l)==j for k in range(N+1) for l in range(N+1)), N+1)
                  for j in range(-N-1, N+2)}
        check(f"fejer_support_mean_{N}", coeffs[0] == 1 and all(
            n >= 0 and n == F(sum(abs(j) <= m for m in range(N+1)), N+1)
            for j, n in coeffs.items()))
    return {"id": "EXCH-009", "source_sha256": PINS, "note_sha256": digest(ROOT/NOTE),
            "verifier_sha256": digest(Path(__file__)), "exact_absorption_constant": str(D),
            "checks": checks, "scope": "Symbolic identities and pins; analytic compactness is in the proof note.",
            "independence": "Separate read-only derivation by fixed-degree smoothing and projected H2 comparison; hostile rough-data review. No newly formalized Lean theorem."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-run", action="store_true")
    args = parser.parse_args()
    report = replay()
    if args.write_run:
        with RUN.open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(report, indent=2)+"\n")
    elif report != load(RUN):
        raise ValueError("Published run does not reproduce")
    print(f"EXCH009: PASS ({len(report['checks'])} exact checks)")
