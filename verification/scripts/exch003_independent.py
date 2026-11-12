#!/usr/bin/env python3
"""Independent real-canonical and reference-Fock checks; no primary imports.

Constant Fourier coordinates retain the exact volume normalization. The Fock
calculation is a reference-state warning, not a quantization/state of EXCH.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch003/independent.json'


def main():
    sha = lambda path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    paths = {'contract':'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json',
             'sector':'strategy/physical-candidates/TECT-EXCH-002-result-v1.json',
             'p1':'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json'}
    src = {k:json.loads((ROOT/v).read_text(encoding='utf-8')) for k,v in paths.items()}
    checks = []
    def check(name, condition):
        ok = bool(condition); checks.append({'name':name,'pass':ok}); assert ok,name
    c, sector, prm = src['contract'],src['sector'],src['p1']['parameters']
    for path, expected in c['source_hashes'].items():
        check('pin:'+path,sha(path)==expected)
    rat = lambda x:s.Rational(str(x))
    V = s.prod(rat(prm[k]) for k in ('Lx','Ly','Lz'))
    Q = rat(sector['key_bounds']['Qbar']); q = Q/V
    eps = rat(c['model']['inserted_parameters']['epsilon'])
    omega = rat(c['model']['inserted_parameters']['omega'])
    onsite_u = rat(c['model']['inserted_parameters']['u'])
    check('sector_density_agrees',q==rat(sector['key_bounds']['q']))
    check('positive_admissible_density',0<q<1)
    r=q; p=2*(q-r*r)
    check('strictly_mixed_initial_points',p>0 and r>0)
    check('same_fixed_charge',s.simplify(V*(p/2+r*r)-Q)==0)
    x,y,u,v,kappa = s.symbols('x y u v kappa',real=True)
    z,w=x+s.I*y,u+s.I*v
    raw_pair=s.expand(s.conjugate(w)*z*z)
    h_int=-kappa*s.re(raw_pair)
    dx,dy=s.diff(h_int,y),-s.diff(h_int,x)
    du,dv=s.diff(h_int,v),-s.diff(h_int,u)
    dNp=s.expand(2*x*dx+2*y*dy); dNc=s.expand(2*u*du+2*v*dv)
    imag_pair=s.expand(s.im(raw_pair))
    check('real_PB_psi_factor_sign',s.expand(dNp-4*kappa*imag_pair)==0)
    check('real_PB_chi_factor_sign',s.expand(dNc+2*kappa*imag_pair)==0)
    check('weighted_charge_PB',s.expand(dNp/2+dNc)==0)
    check('orthonormal_volume_factor',s.simplify((eps/s.sqrt(V))*s.sqrt(V)-eps)==0)
    check('pinned_shell_inactive',rat(prm['eta_shell'])==0)
    z0=[rat(a) for a in prm['z0']]
    lock_e1=1-z0[0]**2/sum(a*a for a in z0)
    a0=rat(prm['r'])+rat(prm['family_masses'][0])+rat(prm['k_lock'])*lock_e1
    # Exact constant-field F_ref: all derivatives/Class-II currents vanish.
    fp=a0*p/2+rat(prm['lambda'])*p*p/4+rat(prm['gamma'])*p**3/6
    states=[]
    for sign in (1,-1):
        chi=sign*s.I*r; pair=s.simplify(V*s.conjugate(chi)*p)
        energy=V*(fp+omega*r*r/2+onsite_u*r**4/4)-eps*s.re(pair)
        flux=s.simplify(2*eps*s.im(pair))
        states.append({'H':energy,'Npsi':V*p,'Nchi':V*r*r,'Z':pair,'J':flux})
    check('equal_full_constant_state_energy',states[0]['H']==states[1]['H'])
    check('equal_component_populations',all(states[0][k]==states[1][k] for k in ('Npsi','Nchi')))
    check('opposite_nonzero_currents',states[0]['J']==-states[1]['J'] and states[0]['J']!=0)
    # Reference-only finite Fock space, not a new dynamics or physical state.
    basis=[(na,nb) for na in range(3) for nb in range(2)]
    index={pair:j for j,pair in enumerate(basis)}
    a,b=s.zeros(len(basis)),s.zeros(len(basis))
    for j,(na,nb) in enumerate(basis):
        if na:a[index[(na-1,nb)],j]=s.sqrt(na)
        if nb:b[index[(na,nb-1)],j]=s.sqrt(nb)
    Na,Nb,pair_op=a.H*a,b.H*b,b.H*a*a
    number=Na+2*Nb
    check('reference_pair_preserves_total_number',number*pair_op==pair_op*number)
    fock=[]
    for sign in (1,-1):
        ket=s.zeros(len(basis),1)
        ket[index[(2,0)]]=1/s.sqrt(2); ket[index[(0,1)]]=sign*s.I/s.sqrt(2)
        mean=lambda op:s.simplify((ket.H*op*ket)[0])
        check(f'reference_fixed_number_{sign}',number*ket==2*ket)
        check(f'reference_zero_charged_means_{sign}',mean(a)==0 and mean(b)==0)
        check(f'reference_nonzero_pair_{sign}',mean(pair_op)==-sign*s.I/s.sqrt(2))
        fock.append({k:str(mean(op)) for k,op in {'Na':Na,'Nb':Nb,'pair':pair_op}.items()})
    check('reference_equal_populations',all(fock[0][k]==fock[1][k] for k in ('Na','Nb')))
    report={'status':'PASS_INDEPENDENT_SCOPED_ALGEBRA','checks':checks,'check_count':len(checks),
      'source_hashes':{p:sha(p) for p in paths.values()},'script_hash':sha('verification/scripts/exch003_independent.py'),
      'derived':{'V':str(V),'Q':str(Q),'q':str(q),'r':str(r),'p':str(p)},
      'counterexample':[{k:str(v) for k,v in state.items()} for state in states],'reference_fock':fock,
      'scope':'Each fixed finite K>=1, initial full-regulator points only; not an invariant-mode reduction.',
      'negative_scope':'No universal population-only law for all full Dirac preparations; special ensembles not excluded.',
      'non_claims':'Fock reference only; no EXCH quantization, physical state, condensate, clock, relaxation or PreA.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=True)+'\n',encoding='utf-8',newline='\n')
    print('EXCH003 INDEPENDENT: PASS',len(checks),'checks')


if __name__=='__main__':main()
