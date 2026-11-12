#!/usr/bin/env python3
"""Exact algebra for the separate finite-regulator exchange hypothesis.

Analytic compactness and finite-dimensional ODE arguments are in the synthesis,
not inferred from these checks. No grids, fitting or physical time conversion.
python -X utf8 verification/scripts/exch001_primary.py
"""
import hashlib
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json'
PIN = 'd07cb738d40d9b97a3a2341ada94ac13167e4410edd4ece39fb6ba02504f073e'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch001/primary.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert __debug__, 'Assertions required'
    c = json.loads(CONTRACT.read_text(encoding='utf-8'))
    assert sha(CONTRACT) == PIN
    for p, h in c['source_hashes'].items():
        assert sha(ROOT/p) == h, p
    a1 = json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())
    r158 = json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())
    inp = c['model']['inserted_parameters']
    eps, omega, u = (s.Rational(inp[k]) for k in ('epsilon', 'omega', 'u'))
    lam, gamma = (s.Rational(str(a1['parameters'][k])) for k in ('lambda', 'gamma'))
    rho0 = -3*lam/(4*gamma)
    gap = 3*lam**2/(16*gamma)
    a0 = s.Rational(1, 2)*omega-s.Rational(1, 3)  # mu_t<1/3 certified by R158.
    A = gamma/6
    b = eps**2/(4*a0)
    D = 2*b*rho0+b**2/(2*A)
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        assert checks[name], name

    check('rho_from_upstream', rho0 == s.Rational(r158['exact_constants']['coexistence_density']))
    check('gap_from_upstream', gap == s.Rational(r158['exact_constants']['coexistence_drop_and_metastability_width']))
    mu_lo, mu_hi = map(s.Rational, r158['exact_constants']['transition_chemical_potential_interval_decimal'])
    check('source_mu_bracket', s.Rational(1,4) < mu_lo < mu_hi < s.Rational(1,3))
    check('positive_parameters', eps > 0 and u > 0 and a0 > eps/2 and gamma > 0)
    check('shift_interval_positive', 0 < 2*D < s.Rational(1,4))

    x = s.symbols('x0:3', real=True)
    y = s.symbols('y0:3', real=True)
    r, t, e = s.symbols('r t e', real=True)
    S_re = sum(xx**2-yy**2 for xx, yy in zip(x,y))
    S_im = 2*sum(xx*yy for xx, yy in zip(x,y))
    V = -e*(r*S_re+t*S_im)
    qdot = s.expand(sum(xx*s.diff(V,yy)-yy*s.diff(V,xx) for xx,yy in zip(x,y)))
    rdot = s.expand(r*s.diff(V,t)-t*s.diff(V,r))
    I = r*S_im-t*S_re
    check('transfer_sign_factor', s.expand(qdot-2*e*I) == 0)
    check('reservoir_transfer', s.expand(rdot+e*I) == 0)
    check('weighted_total_conservation', s.expand(qdot+2*rdot) == 0)
    state = {**dict.fromkeys(x,0), **dict.fromkeys(y,0), x[0]:1, r:0, t:-1, e:eps}
    witness = s.simplify(qdot.subs(state))
    check('nonzero_transfer_witness', witness == 2*eps and witness > 0)
    check('wrong_unweighted_charge_rejected', s.expand(qdot+rdot) != 0)

    aa, rr, ss, ee = s.symbols('aa rr ss ee', positive=True)
    check('reservoir_square_identity', s.factor(aa*rr**2-ee*ss*rr+ee**2*ss**2/(4*aa)-aa*(rr-ee*ss/(2*aa))**2) == 0)
    z, delta = s.symbols('z delta', real=True)
    poly = delta/2+A*(z-rho0)**2-b*z
    square = A*(z-rho0-b/(2*A))**2+(delta-D)/2
    check('phase_square_identity', s.expand(poly-square) == 0)
    check('low_mu_positive_remainder', s.simplify(((delta-D)/2).subs(delta,2*D)) == D/2 and D > 0)
    # Dimensionless witness c=eps*rho0 is derived, not a fitted field.
    amplitude = eps*rho0
    mu = s.symbols('mu', positive=True)
    trial = (omega/2-mu)*amplitude**2+u*amplitude**4/4-eps*rho0*amplitude
    check('old_coexistence_trial_identity', s.expand(trial-(-(omega/2+mu)*amplitude**2+u*amplitude**4/4)) == 0)
    check('old_coexistence_strictly_lower', 0 < amplitude < 1 and -omega/2+u*amplitude**2/4 < 0)
    check('old_chi_derivative_nonzero', -eps*rho0 < 0)

    # Pointwise |sum Psi_a^2|^2 <= rho^2: explicit sums of squares.
    density = sum(xx**2+yy**2 for xx, yy in zip(x,y))
    defect = s.expand(density**2-S_re**2-S_im**2)
    gram = 4*sum((x[i]*y[j]-x[j]*y[i])**2 for i in range(3) for j in range(i+1,3))
    check('pairing_domination', s.expand(defect-gram) == 0)
    # Independent test oracle: coherent pair Hessian is not scalar chemical potential.
    hess = s.hessian(V, list(x)+list(y)).subs({r:1,t:0})
    check('quadrature_split', hess == s.diag(*([-2*e]*3+[2*e]*3)))
    check('zero_seed_invariant_transfer', all(s.diff(V,v).subs(dict.fromkeys(list(x)+list(y),0)) == 0 for v in list(x)+list(y)))
    report = {
        'schema':'tect/exch001-primary/1.0', 'status':'PASS_EXACT_ALGEBRA',
        'contract_sha256': PIN, 'script_sha256':sha(Path(__file__)), 'checks':checks,
        'derived': {k:str(v) for k,v in {'rho_star':rho0,'gamma':gamma,'gap':gap,'a0':a0,'b':b,'D':D,'max_transition_shift':2*D,'transfer_witness_per_volume':witness,'trial_reservoir_amplitude':amplitude,'mu_c_lower_bound':mu_lo-2*D,'mu_c_upper_bound':mu_hi}.items()},
        'analytic_obligations':'Finite-K smooth complete flow, equicoercivity, compact minimizers and local exclusion/jump are proved in the note, not by symbolic PASS.',
        'verdicts':{'total_charge':'CONSERVED','component_exchange':'NONZERO_POSSIBLE','exact_R158_inheritance':'DISPROVED','controlled_shifted_coexistence':'SEE_ANALYTIC_PROOF'},
        'scope':'Fixed volume, every separately fixed finite Fourier K>=1, new Hamiltonian parameter. No Gibbs relaxation, physical state/time or regulator limit.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH001 PRIMARY: PASS',len(checks),'checks; shift <',s.N(2*D,12))


if __name__ == '__main__': main()
