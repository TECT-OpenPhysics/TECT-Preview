"""Exact source and algebra audit for the EXCH-010 weak-limit argument."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
EX = "strategy/physical-candidates/"
P1 = "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R158 = "claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json"
A2 = "claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-full-production-wellposedness-260717-v2.0.tex.txt"
NOTE = "claims/C6-SPACETIME-SIGNATURE/notes/classii-weak-limit-261121-v1.0.tex.txt"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-21-exch010.json"
PINS = {
    P1: "88da7764302b20b0dde6e10902e94b1e26ec3c5274759c7fa51ca6302868b565",
    R158: "82ecf0e8e4e4b3d99cb67fad1655e03d85c63921f9e02deb83bd8ad0a74138e5",
    A2: "e60b1b7640329bae4b5e2a9ac753705e8714921acff22f483d7cc59d0eeb8c34",
    "codes/foundations/n001_variational_backend.py": "e2b55702d48198b933968f002e3d7e3781075927fe9b2684047d585ed56f70fc",
    EX+"TECT-EXCH-001-contract-v1.json": "d07cb738d40d9b97a3a2341ada94ac13167e4410edd4ece39fb6ba02504f073e",
    EX+"TECT-EXCH-001-result-v1.json": "e932c9a837af12538109490358042f113447d4ed1efa838aebab2f6d7ff8c7cf",
    EX+"TECT-EXCH-009-result-v1.json": "e7b20049c075232460a57cace72a981d91e0fbc19787509b286dd23e3f9cdc34",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def realify(z):
    return s.Matrix.vstack(s.re(z), s.im(z))


def scalar(x):
    return x[0, 0]


def replay():
    for name, expected in PINS.items():
        if digest(ROOT/name) != expected:
            raise ValueError(f"Changed pinned source: {name}")
    pp = load(ROOT/P1)["parameters"]
    ex = load(ROOT/(EX+"TECT-EXCH-001-contract-v1.json"))["model"]["inserted_parameters"]
    rat = lambda v: s.Rational(str(v))
    dr, dm, m, al, be, jj, jk, kk = [
        rat(pp[k]) for k in ("rho_regularizer", "classii_mass_regularizer",
                             "M_X", "alpha_X", "beta_X", "cJJ", "cJK", "cKK")]
    cost = m*m+dm
    a, b, c = jj*al*al/cost, jk*al*be/cost, kk*be*be/cost
    eps, omega, u = (rat(ex[k]) for k in ("epsilon", "omega", "u"))
    checks = {}

    def check(label, condition):
        if not bool(condition):
            raise AssertionError(label)
        checks[label] = True

    check("pinned_positive_floors_zero_shell_bias", dr > 0 and dm > 0 and rat(pp["eta_shell"]) == 0)
    check("pinned_signed_mixed_coefficient_and_positivity", b != 0 and a > 0 and a*c-b*b > 0)
    check("positive_leading_linear_symbol", rat(pp["Y"]) > 0)

    # Input test vectors for the local first variation, not a simulation.
    I = s.I
    psi = s.Matrix([2+I, 1-2*I, -1+3*I])
    h = s.Matrix([-1+2*I, 3+I, 2-I])
    grad = s.Matrix([3-I, -2+I, 1+2*I])
    grad_h = s.Matrix([1+I, 2-3*I, 2*I])
    z, v, g, gh = map(realify, (psi, h, grad, grad_h))
    T = (s.Matrix([[0,1,0],[1,0,0],[0,0,0]]),
         s.Matrix([[0,-I,0],[I,0,0],[0,0,0]]),
         s.diag(1,-1,0))  # Source backend generators, without a Pauli half.
    t = s.Symbol("t", real=True)
    X, dX = psi+t*h, grad+t*grad_h
    rho = scalar(X.H*X)
    grad_rho = 2*s.re(scalar(X.H*dX))
    cross_test, omitted_floor_variation = s.S.Zero, s.S.Zero
    for j, generator in enumerate(T, 1):
        R, C = s.re(generator), s.im(generator)
        A = R.row_join(-C).col_join(C.row_join(R))
        moment = scalar(X.H*generator*X)
        q_t = moment/(rho+dr)
        J_t = 2*s.re(scalar(dX.H*generator*X))
        K_t = J_t-q_t*grad_rho
        density = a*J_t**2/2+b*J_t*K_t+c*K_t**2/2
        eta = z.dot(z)+dr
        q = z.dot(A*z)/eta
        dq = (2*v.dot(A*z)-2*q*z.dot(v))/eta
        p, r = 2*A*z, 2*(A-q*s.eye(6))*z
        dp, ds = 2*A*v, 2*(A-q*s.eye(6))*v-2*dq*z
        A0 = a*p*p.T+b*(p*r.T+r*p.T)+c*r*r.T
        D = a*(dp*p.T+p*dp.T)+b*(dp*r.T+p*ds.T+ds*p.T+r*dp.T)+c*(ds*r.T+r*ds.T)
        check(f"realification_generator_{j}", A == A.T and A*z == realify(generator*psi))
        check(f"original_energy_{j}", s.simplify(density.subs(t,0)-g.dot(A0*g)/2) == 0)
        check(f"exact_original_variation_{j}", s.simplify(
            s.diff(density,t).subs(t,0)-gh.dot(A0*g)-g.dot(D*g)/2) == 0)
        cross_test += (J_t*K_t).subs(t,0)
        omitted_floor_variation += ((b*J_t+c*K_t)*s.diff(q_t,t)*grad_rho).subs(t,0)
    check("mixed_term_omission_detectable", s.simplify(cross_test) != 0)
    check("coefficient_quotient_variation_omission_detectable", s.simplify(omitted_floor_variation) != 0)

    chi, k = 2-3*I, 1+2*I
    C_t = chi+t*k
    source_t = scalar(X.T*X)
    exchange_t = -eps*s.re(s.conjugate(C_t)*source_t)
    reservoir_t = omega*C_t*s.conjugate(C_t)/2+u*(C_t*s.conjugate(C_t))**2/4+exchange_t
    exchange_grad = -2*eps*chi*s.conjugate(psi)
    res_grad = (omega+u*chi*s.conjugate(chi))*chi-eps*scalar(psi.T*psi)
    check("real_canonical_exchange_and_reservoir_factors", s.simplify(
        s.diff(reservoir_t,t).subs(t,0)-s.re(scalar(h.H*exchange_grad)+s.conjugate(k)*res_grad)) == 0)
    check("canonical_skew_sign", realify(-I*psi) == s.Matrix.vstack(s.im(psi), -s.re(psi)))
    dim, sigma = 3, F(15,8)  # Fixed proof choices.
    theta = (2-sigma)/4
    check("interpolation_weights", 0 < theta < 1 and (-2)*theta+2*(1-theta) == sigma)
    check("strict_sobolev_thresholds", sigma > max(F(dim,2),1+F(dim,4)) and sigma < 2)
    check("fourth_order_term_is_only_required_in_dual", 2-4 == -2 and sigma-4 < -2)
    return {
        "id": "EXCH-010", "source_sha256": PINS, "note_sha256": digest(ROOT/NOTE),
        "verifier_sha256": digest(Path(__file__)), "checks": checks,
        "interpolation": {"s": str(sigma), "time_increment_power": str(theta)},
        "analytic_boundary": "Same-subsequence compactness and weak equations use the analytic note, not these algebra checks; no uniqueness or energy equality."
    }


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
    print(f"EXCH010: PASS ({len(report['checks'])} exact checks)")
