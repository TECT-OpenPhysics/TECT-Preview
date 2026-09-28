#!/usr/bin/env python3
"""CLK-002 v1.0.0: symbolic first-response map, not a physical-field solver.

The inputs are one global EM coupling, full mass sensitivities and a distinct
clock sensitivity contrast. All identities are conditional on the frozen
Newtonian/linear-response definitions; no atomic constants are fitted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PREREG = 'strategy/clock/TECT-CLK-002-prereg-v1.json'
PIN = 'eed93e6aa01b4bacc780bba0a24f53ccf7c6b7f6daab394ae20e54afa270c92f'
RUNS = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-28-tect-clk002'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(cache=None):
    assert sha(ROOT/PREREG) == PIN, 'Frozen preregistration changed'
    data = json.loads((ROOT/PREREG).read_text(encoding='utf-8'))
    for path, digest in data['protected_sources'].items():
        assert sha(ROOT/path) == digest, path
    if cache is not None:
        for value in data['sources'].values():
            assert sha(cache/value['filename']) == value['sha256'], value['filename']
    return data


def issue_or_check(value, path, check):
    if check:
        assert json.loads(path.read_text(encoding='utf-8')) == value, str(path)
    else:
        assert not path.exists(), 'Issued evidence is immutable; use --check'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n', encoding='utf-8', newline='\n')


def derive():
    d, qa, qb, qs, k = s.symbols('d qA qB qS K', real=True)
    gm, r, c = s.symbols('GM r c', positive=True)
    phi = -d*qs*gm/(r*c**2)
    gradient = s.diff(k*d*phi, r)
    aa = gm/r**2*(1+qa*qs*d**2)
    ab = gm/r**2*(1+qb*qs*d**2)
    mean = (aa+ab)/2
    z = s.factor(-c**2*gradient/mean)
    eta = s.factor((aa-ab)/mean)
    qbar = (qa+qb)/2
    denom = 1+qbar*qs*d**2
    amplitude = qs*d**2/denom
    checks = {}

    def identity(name, expression):
        residual = s.factor(expression)
        assert residual == 0, (name, residual)
        checks[name] = True

    identity('outward_clock_gradient', gradient-k*qs*d**2*gm/(r**2*c**2))
    identity('same_mean_acceleration', mean-gm/r**2*denom)
    identity('clock_readout', z+k*amplitude)
    identity('eotvos_with_denominator', eta-(qa-qb)*amplitude)
    identity('same_source_null', (qa-qb)*z+k*eta)
    identity('sign_ambiguity_clock', z.subs(d, -d)-z)
    identity('sign_ambiguity_freefall', eta.subs(d, -d)-eta)
    u, Q, S, C, C1, C2 = s.symbols('u Q S C C1 C2', real=True)
    forward = S*u/(1+Q*S*u)
    inverse = C/(S*(1-Q*C))
    identity('inverse_recovers_square', inverse.subs(C, forward)-u)
    identity('forward_recovers_response', forward.subs(u, inverse)-C)
    identity('forward_derivative', s.diff(forward, u)-S/(1+Q*S*u)**2)
    identity('inverse_derivative', s.diff(inverse, C)-1/(S*(1-Q*C)**2))
    identity('inverse_difference', inverse.subs(C,C2)-inverse.subs(C,C1)
             -(C2-C1)/(S*(1-Q*C1)*(1-Q*C2)))
    dz, de, dq, dk, z0, e0, q0, k0 = s.symbols('dz de dq dk z0 e0 q0 k0')
    residual_change = (q0+dq)*(z0+dz)+(k0+dk)*(e0+de)-(q0*z0+k0*e0)
    identity('uncertainty_expansion', residual_change-(q0*dz+z0*dq+dq*dz+k0*de+e0*dk+dk*de))
    identity('test_body_swap', eta.xreplace({qa:qb,qb:qa})+eta)
    identity('clock_pair_swap', z.subs(k,-k)+z)
    return {'checks':checks, 'check_count':len(checks),
        'derived':{'z':str(z), 'eta':str(eta), 'C':str(s.factor(amplitude)),
                   'inverse_square':str(inverse), 'inverse_derivative':str(s.diff(inverse,C))},
        'domains':{'r_c_GM':'strictly positive', 'normalization':'D > 0; same measured mean acceleration',
                   'inverse':'S > 0, Q >= 0, C >= 0, 1-Q*C > 0; u=d^2',
                   'finite_response':'NOT_CERTIFIED; no post-Newtonian or atomic remainder bound'},
        'conditioning':'For S>=s0>0 and 1-Q*C_i>=epsilon>0, |Delta u|<=|Delta C|/(s0*epsilon^2), for fixed charges only.',
        'uncertainty':'|Q0|ez+|z0|eQ+eQ*ez+|K0|eeta+|eta0|eK+eK*eeta+emodel. Missing errors cannot be zeroed.',
        'non_claims':'No empirical fit, detection, finite-field exclusion, microscopic TECT, A/B, geometry, QFT or gravity derivation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--source-cache',type=Path)
    args=parser.parse_args()
    data=inputs(args.source_cache)
    value=derive()
    value.update(schema='tect/clk002-primary/1.0', status='PASS_CONDITIONAL_FIRST_RESPONSE',
                 prereg_sha256=PIN, script_sha256=sha(Path(__file__)),
                 source_hashes={key:row['sha256'] for key,row in data['sources'].items()},
                 source_bytes_rule='--source-cache verifies exact PDFs; public replay verifies pinned manifest and protected local sources')
    issue_or_check(value,RUNS/'primary.json',args.check)
    print('CLK-002 PRIMARY: PASS',value['check_count'],'symbolic identities; first-response only')


if __name__ == '__main__':
    main()
