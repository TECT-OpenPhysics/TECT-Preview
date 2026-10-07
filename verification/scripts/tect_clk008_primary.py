"""CLK008 symbolic phase/orbit response checks, not an empirical fit.

INPUTS are symbolic full mass charges and absolute proper-frequency response.
Positive U=mu/r; x=d^2. The orbit-calibration shortcut is conditional and is
not the identified Galileo estimator. General scope is in the certificate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT/'strategy/clock/TECT-CLK-008-prereg-v1.json'
PIN = 'a53797b3b5b3390d3942926530f07427972f9cd1728c0f2182442c283633a57d'
RUNS = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-07-tect-clk008'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    assert sha(PREREG) == PIN
    p = json.loads(PREREG.read_text(encoding='utf-8'))
    for path, digest in p['protected_sources'].items():
        assert sha(ROOT/path) == digest, path
    return p


def issue_or_check(value, path, check):
    if check:
        assert json.loads(path.read_text(encoding='utf-8')) == value, path
    else:
        assert not path.exists(), 'Issued run is immutable; use --check'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n', encoding='utf-8', newline='\n')


def derive():
    d, qE, qO, qa, qb, k, kg = s.symbols('d qE qO qA qB K_H K_G', real=True)
    U, V, eps = s.symbols('U V eps', real=True)
    # eps counts weak-field orders; U=mu/(r*c^2), V=v^2/c^2.
    phi = -d*qE*eps*U
    phase_rate = (1+k*d*phi)*(1-eps*(U+V/2))
    first = s.diff(phase_rate, eps).subs(eps, 0)
    t = qE*d**2
    b, q = (qa+qb)/2, qa-qb
    D_O, D_F = 1+qO*t, 1+b*t
    alpha = s.factor((1+k*t)/D_O-1)
    eta = s.factor(q*t/D_F)
    checks = {}

    def identity(name, expression):
        assert s.factor(expression) == 0, (name, expression)
        checks[name] = True

    identity('phase_first_order', first+U*(1+k*t)+V/2)
    identity('orbit_normalized_alpha', alpha-(k-qO)*t/D_O)
    identity('joint_relation', (q+(qO-b)*eta)*alpha-(k-qO)*eta)
    identity('coupling_sign', alpha.subs(d,-d)-alpha)
    identity('zero_coupling', alpha.subs(d,0))
    identity('orbit_clock_blind_direction', alpha.subs(k,qO))
    identity('equal_test_charges', eta.subs(qa,qb))
    identity('test_body_swap', eta.xreplace({qa:qb,qb:qa})+eta)
    ug, us = s.symbols('u_ground u_satellite', real=True)
    y = (1+kg*t)*ug-(1+k*t)*us
    identity('ground_sensitivity_remainder', y-(1+k*t)*(ug-us)-t*(kg-k)*ug)
    identity('identical_clock_gravity', y.subs(kg,k)-(1+k*t)*(ug-us))
    # A constant fractional ground term integrates to a linear phase nuisance.
    time, ground_const = s.symbols('time ground_const', real=True)
    identity('constant_ground_phase_is_linear', s.diff(ground_const*time,time,2))
    # A time-dependent ground term is not generally a daily linear nuisance.
    assert s.diff(time**2, time, 2) != 0
    checks['variable_ground_not_automatically_removed'] = True
    Q,B,K,O,A,E,da,de = s.symbols('Q B K O A E da de', real=True)
    residual = lambda av,ev: (Q+(O-B)*ev)*av-(K-O)*ev
    identity('residual_error_expansion', residual(A+da,E+de)-residual(A,E)
             -((Q+(O-B)*E)*da+((O-B)*A-(K-O))*de+(O-B)*da*de))
    return {
        'schema':'tect/clk008-symbolic/1.0', 'status':'PASS_CONDITIONAL_ALGEBRA',
        'prereg_sha256':PIN, 'script_sha256':sha(Path(__file__)),
        'checks':checks, 'check_count':len(checks),
        'derived':{'phase_first_order':str(s.expand(first)), 'alpha_orbit':str(alpha), 'eta':str(eta)},
        'domain':'Nonzero D_O and D_F for algebra; positive individual force factors, photon kinetic coefficient and weak-field validity for physical use.',
        'not_encoded':'Actual Galileo processing response, link/orbit covariance, absolute H sensitivity, composition and total finite-field errors.',
        'empirical_fit':False, 'physical_promotion':False
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    inputs()
    result = derive()
    issue_or_check(result, RUNS/'primary.json', args.check)
    print('CLK008 PRIMARY:', result['status'], result['check_count'])
