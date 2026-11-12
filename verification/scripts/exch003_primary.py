#!/usr/bin/env python3
"""Exact EXCH charge-current diagnostics and phase-blind closure obstruction.

Formal complex coordinates derive the interaction factors with {z,zbar}=-2i.
The full P1 contribution cancels by its global phase symmetry (analytic proof
in the synthesis); no substitute one-mode dynamics or physical state is used.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch003'
CONTRACT = ROOT/'strategy/physical-candidates/TECT-EXCH-003-contract-v1.json'
PIN = '1e61385a312f0973343b898e474a1c53e2f49cc3af26127d7f9e293444c363e5'


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(CONTRACT) == PIN
    contract = json.loads(CONTRACT.read_text())
    for path, digest in contract['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    old = json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for path, digest in old['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    params = json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    rat = lambda value: s.Rational(str(value))
    eps = rat(old['model']['inserted_parameters']['epsilon'])
    volume = s.prod(rat(params[k]) for k in ('Lx', 'Ly', 'Lz'))
    rho = -3*rat(params['lambda'])/(4*rat(params['gamma']))
    q = rho/2
    total = volume*q
    r = q
    p = 2*(q-r*r)  # Declared exact witness, not a new model parameter.
    e = s.symbols('e', real=True)
    z = s.symbols('z:3'); zb = s.symbols('zb:3')
    w, wb, a = s.symbols('w wb a', nonzero=True)
    coords = list(zip(z, zb)) + [(w, wb)]
    def pb(f, g):
        return s.expand(-2*s.I*sum(s.diff(f, x)*s.diff(g, y)-s.diff(f, y)*s.diff(g, x) for x, y in coords))
    S = sum(x*x for x in z); Sb = sum(x*x for x in zb)
    Z = wb*S; Zb = w*Sb; imagZ = (Z-Zb)/(2*s.I)
    hint = -e*(Z+Zb)/2
    npsi = sum(x*y for x, y in zip(z, zb)); nchi = w*wb
    checks = {}
    def ck(name, condition):
        checks[name] = bool(condition)
        assert checks[name], name
    ck('psi_interaction_field', all(s.expand(pb(x, hint)-2*s.I*e*w*y) == 0 for x, y in zip(z, zb)))
    ck('chi_interaction_field', s.expand(pb(w, hint)-s.I*e*S) == 0)
    ck('norm_psi_rate', s.expand(pb(npsi, hint)-4*e*imagZ) == 0)
    ck('norm_chi_rate', s.expand(pb(nchi, hint)+2*e*imagZ) == 0)
    ck('weighted_charge_conserved', pb(npsi/2+nchi, hint) == 0)
    ck('interaction_quadrature_invariant', s.expand(Z.subs({**{x:a*x for x in z}, wb:wb/a**2}, simultaneous=True)-Z) == 0)
    # Formal antisymmetry verifies the complete three-term energy ledger;
    # this does not assign physical energy units to the norm-charge current.
    f = npsi**2  # Labelled generic invariant test oracle, NOT substituted P1.
    hchi = nchi/2+nchi**2/4
    H = f+hchi+hint
    ck('energy_three_term_balance', s.expand(pb(f,H)+pb(hchi,H)+pb(hint,H)) == 0)
    ck('interaction_energy_cannot_be_omitted', pb(hint,H) != 0)
    ck('same_original_sector', p>0 and r>0 and p/2+r*r == q)
    ck('fixed_sector_reproduction', total == s.Rational(11008,27))  # Test oracle.
    zplus = -s.I*volume*r*p; zminus = s.conjugate(zplus)
    jplus = 2*eps*s.im(zplus); jminus = 2*eps*s.im(zminus)
    ck('opposite_nonzero_flux', jplus == -jminus and jplus != 0)
    ck('same_full_interaction_energy', s.re(zplus) == s.re(zminus) == 0)
    ck('same_modulus_not_same_quadrature', abs(zplus) == abs(zminus) and s.im(zplus) != s.im(zminus))
    # Reference-only number-conserving quantum pair sector, not EXCH quantization.
    C = s.Matrix([[0,0],[s.sqrt(2),0]])
    Na = s.diag(2,0); Nm = s.diag(0,1)
    states = [s.Matrix([1, sign*s.I])/s.sqrt(2) for sign in (1,-1)]
    expect = lambda v, op: s.simplify((s.conjugate(v.T)*op*v)[0])
    ck('reference_same_populations', all(expect(v,Na)==1 and expect(v,Nm)==s.Rational(1,2) for v in states))
    ck('reference_invariant_pair_operator', (Na+2*Nm)*C-C*(Na+2*Nm) == s.zeros(2))
    ck('reference_opposite_pair_coherence', expect(states[0],C) == -expect(states[1],C) and s.im(expect(states[0],C)) != 0)
    ck('reference_same_pair_energy', all(expect(v,C+C.T)==0 for v in states))
    out = {'status':'PASS_EXACT_DIAGNOSTICS_NOT_PHYSICAL_BRIDGE', 'script_sha256':sha(Path(__file__)),
           'contract_sha256':sha(CONTRACT), 'checks':checks,
           'derived':{k:str(v) for k,v in {'volume':volume,'Qbar':total,'q':q,'r':r,'p':p,'abs_current':abs(jplus)}.items()},
           'scope':'Full-regulator initial derivative counterexample; no invariant-mode reduction, closed augmented hierarchy, physical counting/clock map or relaxation.'}
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'primary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH003 PRIMARY: PASS',len(checks),'exact checks; physical bridge unproved')


if __name__ == '__main__':
    main()
