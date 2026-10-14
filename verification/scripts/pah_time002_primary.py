#!/usr/bin/env python3
"""TIME-002 exact source, labelled-uniformization and Poisson algebra controls.

Analytic proof is in the synthesis; these checks do not encode path measures.
No finite dynamics simulation, fitted constant, or physical interpretation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / 'strategy/pa-hyp/PAH-TIME-002-prereg-v1.json'
PREREG_SHA = 'a4d3700b323f4b52664cc01680749f4e359c0854bc96f9bf77527a50a827ba10'
OUT = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-time002/primary.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    assert sha(PREREG) == PREREG_SHA
    prereg = json.loads(PREREG.read_text(encoding='utf-8'))
    for path, digest in prereg['source_pins'].items():
        assert sha(ROOT / path) == digest, path
    parent = json.loads((ROOT/'strategy/pa-hyp/PAH-001-v1.json').read_text(encoding='utf-8'))
    child = json.loads((ROOT/'strategy/pa-hyp/PAH-001-v2-r2.json').read_text(encoding='utf-8'))
    assert 'local clock accumulation is d tau_v=s_v^nu dt' in parent['dynamics']['time']
    assert 'all j,n,u fixed' in child['root_partial_maps']['TR']
    assert 'all other coordinates fixed' in child['root_partial_maps']['PH']
    assert 'all other coordinates fixed' in child['root_partial_maps']['AP']
    assert 'u_e -> u_e+sigma mod K' in child['root_partial_maps']['LK']
    # Symbols represent inputs, never pasted derived numerical constants.
    c, C, f, g, m, t, lam, z = s.symbols('c C f g m t lam z', positive=True)
    label_transition = (c/C)*g + (1-c/C)*f
    assert s.simplify(C*(label_transition-f)-c*(g-f)) == 0
    assert s.simplify(m*C*((label_transition-f)/m)-c*(g-f)) == 0
    # Poisson generating function; E[N(N-1)]+E[N] is E[N^2].
    pgf = s.exp(lam*t*(z-1))
    mean = s.diff(pgf,z).subs(z,1)
    factorial_second = s.diff(pgf,z,2).subs(z,1)
    second = s.expand(mean+factorial_second)
    assert s.simplify(mean-lam*t) == 0
    assert s.simplify(second-(lam*t+(lam*t)**2)) == 0
    assert s.simplify(pgf.subs(t,0)-1) == 0
    e, p, K, T, a = s.symbols('e p K T a', positive=True)
    delta = (s.Integer(2)/p)*(2*s.pi/K)
    Lambda = 2*e*C
    horizon = T/a
    bound = s.expand(delta**2*(Lambda*horizon+(Lambda*horizon)**2))
    assert s.limit(bound,K,s.oo) == 0
    assert s.simplify(bound.subs(T,0)) == 0
    assert s.simplify(bound.subs(a,1)-delta**2*(Lambda*T+(Lambda*T)**2)) == 0
    assert s.simplify(bound*K**2).has(K) is False
    # Direction of inverse horizon: a*sigma=u implies sigma=u/a.
    u = s.symbols('u', nonnegative=True)
    assert s.solve(a*t-u,t) == [u/a]
    return {'schema':'tect/pah-time002-primary/1.0',
            'status':'PASS_SOURCE_AND_SYMBOLIC_CONTROLS',
            'script_sha256':sha(Path(__file__)), 'prereg_sha256':PREREG_SHA,
            'source_hashes':prereg['source_pins'],
            'symbolic_controls':['label_generator','uniform_label_choice','poisson_mean',
                'poisson_factorial_to_second','zero_time','inverse_clock_direction',
                'bound_limit','epsilon_one','K_independent_numerator'],
            'derived_bound':str(bound),
            'boundary':'Source and exact symbolic corroboration only; labelled path law, stopping-time sampling and all-r proof are analytic.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true')
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    data=run()
    if args.write:
        assert not OUT.exists(),'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        assert json.loads(OUT.read_text(encoding='utf-8')) == data
    print('TIME-002 PRIMARY: PASS (source pins and exact symbolic controls only)')


if __name__=='__main__':
    main()
