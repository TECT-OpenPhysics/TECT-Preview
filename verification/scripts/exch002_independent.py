#!/usr/bin/env python3
"""Independent reviewer's exact fixed-sector certificate; no primary imports."""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch002/independent.json'


def main():
    rat=lambda x:s.Rational(str(x));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    checks={}
    def ck(k,v):
        checks[k]=bool(v)
        assert checks[k],k
    cp=ROOT/'strategy/physical-candidates/TECT-EXCH-002-contract-v1.json'
    ck('contract',sha(cp)=='5dad4605d24d338d0ff4a8c169607595d7c59f247c15a4388185fceee31d75cc')
    for p,h in json.loads(cp.read_text())['source_hashes'].items():ck('source:'+p,sha(ROOT/p)==h)
    old=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for p,h in old['source_hashes'].items():ck('parent:'+p,sha(ROOT/p)==h)
    a=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    src=json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())['exact_constants']
    eps=rat(old['model']['inserted_parameters']['epsilon'])
    lam,gamma=(rat(a[k]) for k in ('lambda','gamma'))
    vol=s.prod(rat(a[k]) for k in ('Lx','Ly','Lz'))
    rho=-3*lam/(4*gamma);total=rat(src['coexistence_charge']);q=total/vol;muR=(1+q)/2
    ck('fixed_sector',q==rho/2)
    ck('mu_bounds',s.Rational(1,4)<rat(src['transition_chemical_potential_interval_decimal'][0])<rat(src['transition_chemical_potential_interval_decimal'][1])<s.Rational(1,3))
    er=q/2+q*q/4
    ck('order_beats_reservoir',q/3<er)
    r=eps*rho;p=rho-2*r*r
    ck('same_Q_trial',p/2+r*r==q)
    ck('mixed_positive',p>0 and r>0)
    upper=r*r/4+(s.Rational(1,4)+2*gamma*p/3)*r**4-eps*r*p
    ck('mixed_beats_pure',upper<0)
    t,ell=s.symbols('t ell',real=True)
    curve=ell*t*t/2+lam*t**4/4+gamma*t**6/6+(q-t*t/2)/2+(q-t*t/2)**2/4-er
    ck('constrained_hessian',s.diff(curve,t,2).subs(t,0)==ell-muR)
    ck('negative_direction',rat(src['quadratic_ground_eigenvalue_interval_decimal'][1])<muR)
    z=s.Matrix(list(map(rat,a['z0'])))
    mass=s.diag(*map(rat,a['family_masses']))+rat(a['k_lock'])*(s.eye(3)-z*z.T/(z.T*z)[0])
    x=s.symbols('x');poly=s.Poly(mass.charpoly(x).as_expr(),x)
    ck('largest_root',poly.count_roots(s.Rational(1,5),s.Rational(21,100))==1 and poly.count_roots(s.Rational(21,100),s.oo)==0)
    def atan(x,n):
        p=sum((-1)**j*x**(2*j+1)/s.Integer(2*j+1) for j in range(n));nxt=(-1)**n*x**(2*n+1)/s.Integer(2*n+1)
        return min(p,p+nxt),max(p,p+nxt)
    ab=atan(s.Rational(1,5),25);bb=atan(s.Rational(1,239),8)
    ck('Machin',3<16*ab[0]-4*bb[1]<16*ab[1]-4*bb[0]<s.Rational(22,7))
    xl,xh=s.Rational(9,64),s.Rational(121,784)
    Y,Z,R=(rat(a[k]) for k in ('Y','Z','r'))
    f=lambda x:Y*x*x+Z*x+R
    ck('symbol_monotone',2*Y*xh+Z<0)
    ck('mode_enclosure',s.Rational(11,20)<f(xh)+s.Rational(1,5)<f(xl)+s.Rational(21,100)<s.Rational(29,50))
    ck('positive_detuning',muR<s.Rational(11,20))
    growth=4*eps**2*q-(s.Rational(29,50)-muR)**2
    ck('positive_growth',growth>0)
    d,c=s.symbols('d c',real=True);B=s.Matrix([[d,-c],[c,-d]])
    ck('actual_BdG_square',s.simplify((-s.I*B)**2-(c*c-d*d)*s.eye(2))==s.zeros(2))
    report={'status':'PASS_INDEPENDENT_FIXED_SECTOR','script_sha256':sha(Path(__file__)),'checks':checks,
      'derived':{k:str(v) for k,v in {'rho_star':rho,'Qbar':total,'q':q,'muR':muR,'ER_per_volume':er,'mixed_r':r,'mixed_density':p,'mixed_upper':upper,'growth_squared_lower':growth}.items()},
      'scope':'Independent algebra/intervals; compactness, set stability and nonrelaxation reviewed analytically. No physical/limit claim.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH002 INDEPENDENT: PASS',len(checks),'checks')


if __name__=='__main__':main()
