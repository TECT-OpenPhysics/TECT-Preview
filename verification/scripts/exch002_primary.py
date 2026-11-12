#!/usr/bin/env python3
"""Exact fixed-Q comparisons and rotating-flow instability certificate.

No phase/time sweep. Analytic minimizer-set stability and nonlinear instability
are proved in the synthesis, not inferred from finite numerical integration.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch002'
PIN='5dad4605d24d338d0ff4a8c169607595d7c59f247c15a4388185fceee31d75cc'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cp=ROOT/'strategy/physical-candidates/TECT-EXCH-002-contract-v1.json'
    assert sha(cp)==PIN
    c=json.loads(cp.read_text())
    for p,h in c['source_hashes'].items(): assert sha(ROOT/p)==h,p
    old=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for p,h in old['source_hashes'].items(): assert sha(ROOT/p)==h,p
    a1=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    src=json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())
    rat=lambda v:s.Rational(str(v))
    lam,gamma=(rat(a1[k]) for k in ('lambda','gamma'))
    eps=rat(old['model']['inserted_parameters']['epsilon'])
    vol=s.prod(rat(a1[k]) for k in ('Lx','Ly','Lz'))
    rho=-3*lam/(4*gamma); q=rho/2; total=vol*q
    muR=(1+q)/2; c2=4*eps**2*q
    lo,hi=map(rat,src['exact_constants']['transition_chemical_potential_interval_decimal'])
    g=3*lam**2/(16*gamma); l0_hi=hi+g
    checks={}
    def ck(k,b):
        checks[k]=bool(b)
        assert checks[k],k
    ck('fixed_old_charge',total==rat(src['exact_constants']['coexistence_charge']))
    ck('declared_charge_density',q==s.Rational(43,432))  # reproduction oracle
    ck('source_mu_bounds',s.Rational(1,4)<lo<hi<s.Rational(1,3))
    ck('reservoir_tangent_negative',l0_hi<muR)
    # Exact same-charge trial, no new input amplitude.
    r=eps*rho; p=rho-2*r*r
    ck('same_sector_identity',p/2+r*r==q and p>0)
    t=s.symbols('t',real=True)
    difference=(s.Rational(1,2)-t)*r*r+r**4/4+2*gamma*p*r**4/3-eps*r*p
    upper=s.factor(difference.subs(t,s.Rational(1,4)))
    ck('mixed_beats_best_pure_order',s.diff(difference,t)<0 and upper<0)
    reservoir=q/2+q*q/4
    order_upper=rho/6
    ck('pure_order_beats_all_reservoir',reservoir>order_upper)
    # A positive reservoir-only tangent direction at the same charge.
    z=s.symbols('z',real=True)
    modulation=q*q*(1+3*z*z+3*z**4/8)/(1+z*z/2)**2
    ck('reservoir_positive_tangent',s.diff(modulation,z,2).subs(z,0)>0)
    # Exact projected co-rotating Psi block: i zdot=d z-c conj(z).
    d,cc=s.symbols('d cc',real=True)
    block=s.Matrix([[0,d+cc],[-d+cc,0]])
    ck('actual_growth_polynomial',block**2==(cc*cc-d*d)*s.eye(2))
    ck('negative_energy_not_enough',c2-(muR-l0_hi)**2<0)  # lowest-shell block elliptic
    # Matrix derived from original parameters, not pasted eigenvalues.
    masses=list(map(rat,a1['family_masses']))
    z0=s.Matrix(list(map(rat,a1['z0'])))
    M=s.diag(*masses)+rat(a1['k_lock'])*(s.eye(len(masses))-z0*z0.T/(z0.dot(z0)))
    w=s.symbols('w')
    poly=s.Poly(M.charpoly(w).as_expr(),w)
    nlo,nhi=s.Rational(1,5),s.Rational(21,100)  # rational certificate thresholds
    ck('largest_internal_root_isolated',poly.count_roots(nlo,nhi)==1 and poly.count_roots(nhi,s.oo)==0 and poly.count_roots(-s.oo,nlo)==2)
    # Machin formula with alternating series; identity also used in R158 source.
    def atan_bounds(x,n):
        a=sum((-1)**j*x**(2*j+1)/(2*j+1) for j in range(n))
        err=x**(2*n+1)/(2*n+1)
        return (a,a+err) if n%2==0 else (a-err,a)
    al,ah=atan_bounds(s.Rational(1,5),6);bl,bh=atan_bounds(s.Rational(1,239),3)
    pil,pih=16*al-4*bh,16*ah-4*bl
    ck('pi_outer_bounds',3<pil<pih<s.Rational(22,7))
    xl,xh=s.Rational(9,64),s.Rational(121,784)
    Y,Z,R=(rat(a1[k]) for k in ('Y','Z','r'))
    f=lambda x:Y*x*x+Z*x+R
    ck('spatial_decreasing',2*Y*xh+Z<0)
    ck('spatial_rational_enclosure',s.Rational(35,100)<f(xh)<f(xl)<s.Rational(37,100))
    eiglo,eighi=s.Rational(11,20),s.Rational(29,50)
    dlo,dhi=eiglo-muR,eighi-muR
    growth_lower=s.factor(c2-dhi*dhi)
    ck('real_positive_transverse_growth',0<dlo<dhi and growth_lower>0)
    ck('wrong_zero_coupling_control',-dhi*dhi<0)
    report={'status':'PASS_FIXED_SECTOR_ALGEBRA','contract_sha256':PIN,'script_sha256':sha(Path(__file__)),
      'checks':checks,'derived':{k:str(v) for k,v in {'Qbar':total,'q':q,'rho_star':rho,'muR':muR,'coupling_squared':c2,'mixed_r':r,'mixed_density':p,'mixed_energy_upper_per_volume':upper,'reservoir_min_per_volume':reservoir,'pure_order_upper_per_volume':order_upper,'growth_squared_lower':growth_lower}.items()},
      'growth_bound_decimal_for_reading':str(s.N(growth_lower,15)),
      'scope':'Each fixed finite K>=1, n=(1,0,0) high internal branch for instability. No trajectory simulation, thermal/continuum limit or physical time.',
      'analytic_obligations':'Compact constrained mixed minimizers; set Lyapunov stability; relative-orbit nonlinear instability from local unstable manifold; energy no-attraction are proved in note.'}
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'primary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH002 PRIMARY: PASS',len(checks),'checks; growth² lower=',s.N(growth_lower,10))


if __name__=='__main__': main()
