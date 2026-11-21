"""Recheck the exact Class-II identities used in the R-585 uniqueness audit."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
P1 = "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
EX = "strategy/physical-candidates/"
RUN = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-11-21-exch011.json"
PINS = {
    P1: "88da7764302b20b0dde6e10902e94b1e26ec3c5274759c7fa51ca6302868b565",
    "codes/foundations/n001_variational_backend.py": "e2b55702d48198b933968f002e3d7e3781075927fe9b2684047d585ed56f70fc",
    EX+"TECT-EXCH-001-contract-v1.json": "d07cb738d40d9b97a3a2341ada94ac13167e4410edd4ece39fb6ba02504f073e",
    EX+"TECT-EXCH-010-result-v1.json": "eba4f9878431cb427062f57fd5a53510f616b93469b46faba608141348945934",
    "claims/C6-SPACETIME-SIGNATURE/notes/classii-weak-limit-261121-v1.0.tex.txt":
        "3c6919102f666d1d1f436f9500c6728166685a5afff0c81dc06ee2b463e3bdc1",
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def replay():
    for name, expected in PINS.items():
        if digest(ROOT/name) != expected:
            raise ValueError(f"Changed pinned source: {name}")
    pp = load(ROOT/P1)["parameters"]
    rat = lambda v: s.Rational(str(v))
    dr, dm, m, al, be, jj, jk, kk, Y = [
        rat(pp[k]) for k in ("rho_regularizer", "classii_mass_regularizer",
                             "M_X", "alpha_X", "beta_X", "cJJ", "cJK", "cKK", "Y")]
    dM = m*m+dm
    a, b, c = jj*al*al/dM, jk*al*be/dM, kk*be*be/dM
    checks = {}

    def check(label, value):
        if not bool(value):
            raise AssertionError(label)
        checks[label] = True

    def zero(value):
        return s.cancel(value) == 0

    check("positive_floors_dispersion_and_zero_shell", min(dr, dm, Y) > 0 and rat(pp["eta_shell"]) == 0)
    check("signed_original_mixed_coefficient_and_positive_form", b != 0 and a > 0 and a*c-b*b > 0)
    A, g, gx, t = s.symbols("A g gx t", real=True)
    C = lambda rho: a+2*b*dr/(rho+dr)+c*(dr/(rho+dr))**2
    beta = 4*A*A*C(A*A)
    rho_bar = s.Symbol("rho", real=True)
    diff_parts = []
    J = s.Matrix([[0,1],[-1,0]])
    for sign in (1,-1):
        u = A+sign*(1-s.I)*g
        ux = sign*(1-s.I)*gx
        h, hx = 2*(1+s.I)*g, 2*(1+s.I)*gx
        X, Xx = u+t*h, ux+t*hx
        rho = s.expand(s.conjugate(X)*X)
        grad = s.expand(2*s.re(s.conjugate(X)*Xx))
        rho0 = rho.subs(t,0)
        grad0 = grad.subs(t,0)
        check(f"test_density_and_gradient_variation_{sign}",
              zero(rho.diff(t).subs(t,0)-4*A*g) and zero(grad.diff(t).subs(t,0)-4*A*gx))
        # First-component source: m1=m2=0, m3=rho, J3=grad and K3=theta*grad.
        theta = dr/(rho+dr)
        source = (a*grad**2+2*b*grad*(theta*grad)+c*(theta*grad)**2)/2
        part = 4*A*C(rho0)*(sign*2*A+4*g)+2*A*g*(sign*2*A+4*g)**2*s.diff(C(rho_bar),rho_bar).subs(rho_bar,rho0)
        check(f"full_pinned_quotient_derivative_{sign}",
              zero(s.diff(source,t).subs(t,0)-part*gx*gx))
        check(f"original_density_gradient_{sign}", zero(grad0-(sign*2*A+4*g)*gx))
        diff_parts.append(part)
    check("positive_two_state_slope_factor", zero((diff_parts[0]-diff_parts[1]).subs(g,0)-4*beta))
    q, A0 = s.symbols("q A0", real=True)
    center, amp = A0*(1-q*q)/(1+q*q), 2*A0*q/(1+q*q)
    check("exact_common_charge_parameterization", zero(center*center+amp*amp-A0*A0))
    check("half_period_swaps_preparations",
          A+(1-s.I)*g == (A-(1-s.I)*g).subs(g,-g))
    real_w = s.Matrix([2*g,-2*g])
    check("difference_norm_and_hamiltonian_test_sign",
          real_w.dot(real_w) == 8*g*g and -J*real_w == s.Matrix([2*g,2*g]))

    B = s.diag(beta,0)
    Bminus = (B+J*B*J)/2
    check("positive_rank_one_not_complex_linear", B*J != J*B)
    check("anti_part_and_phase_derivative", Bminus*J == -J*Bminus and
          J*Bminus-Bminus*J == s.Matrix([[0,-beta],[-beta,0]]))
    k = s.Symbol("wave_number", positive=True)
    block = Y*k**4*s.eye(2)+k**2*B
    metric = block/(Y*k**4)
    L = J*block
    check("frozen_corrected_energy_exact_cancellation",
          all(zero(item) for item in L.T*metric+metric*L))
    # Scaling of the isolated time-of-coefficient form in three dimensions:
    # amplitude N^-1/2, four derivatives; two tests N^1/2; dx scales N^-3.
    half = s.Rational(1,2)
    power = 4-half+2*half-3
    check("standalone_coefficient_time_term_scaling", power > 0 and 2-half+2*half-3 < power)
    check("exact_positive_radial_sample", beta.subs(A,half) > 0)
    return {"id":"EXCH-011", "source_sha256": PINS,
            "verifier_sha256":digest(Path(__file__)), "checks":checks,
            "coefficient_time_form_exponent":str(power),
            "boundary":"Uniform bare Gronwall and isolated correction-term routes only. The proofs and scoped HOLD are in the assessment, not in these algebra checks. No same-datum nonuniqueness."}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-run", action="store_true")
    args=parser.parse_args()
    report=replay()
    if args.write_run:
        with RUN.open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(report, indent=2)+"\n")
    elif report != load(RUN):
        raise ValueError("Published audit does not reproduce")
    print(f"EXCH011: PASS ({len(report['checks'])} exact checks; uniqueness is not adjudicated)")
