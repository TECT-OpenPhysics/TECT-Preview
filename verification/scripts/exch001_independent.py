#!/usr/bin/env python3
"""Separate reviewer's real-coordinate certificate; no primary imports.

Root added file serialization only. Analytic ODE/compactness are in the note.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch001/independent.json'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cp=ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json'
    assert sha(cp)=='d07cb738d40d9b97a3a2341ada94ac13167e4410edd4ece39fb6ba02504f073e'
    c=json.loads(cp.read_text())
    for p,h in c['source_hashes'].items(): assert sha(ROOT/p)==h,p
    src=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())
    q=lambda v:s.Rational(str(v))
    gamma,lam=(q(src['parameters'][k]) for k in ('gamma','lambda'))
    eps=q(c['model']['inserted_parameters']['epsilon'])
    rho0=-3*lam/(4*gamma)
    beta=eps**2/(4*s.Rational(1,6))
    D=2*beta*rho0+3*beta**2/gamma
    checks={}
    def ck(k,v):
        checks[k]=bool(v)
        assert checks[k],k
    # Explicit reproduction oracles, not inputs used to compute D.
    ck('D_reproduction',D==s.Rational(2827,1179648))
    ck('positive_window',0<2*D<s.Rational(1,4))
    ep=s.symbols('ep',real=True)
    xs=s.symbols('x0:3',real=True); ys=s.symbols('y0:3',real=True)
    u,v=s.symbols('u v',real=True)
    rho=sum(x*x+y*y for x,y in zip(xs,ys))
    sr=sum(x*x-y*y for x,y in zip(xs,ys)); si=sum(2*x*y for x,y in zip(xs,ys))
    pairs=list(zip(xs,ys))+[(u,v)]
    def pb(f,g): return s.expand(sum(s.diff(f,x)*s.diff(g,y)-s.diff(f,y)*s.diff(g,x) for x,y in pairs))
    ht=-ep*(u*sr+v*si)
    p=pb(rho/2,ht); r=pb((u*u+v*v)/2,ht)
    ck('psi_transfer',s.expand(p-2*ep*(u*si-v*sr))==0)
    ck('chi_transfer',s.expand(r+ep*(u*si-v*sr))==0)
    ck('total_charge',s.expand(p+2*r)==0)
    initial=dict.fromkeys(xs+ys,0);initial.update({xs[0]:1,u:0,v:-1})
    ck('nonzero_initial_transfer',p.subs(initial)==2*ep and r.subs(initial)==-ep)
    ck('wrong_unweighted_charge',s.expand(p+r)!=0)
    density_only=rho*(u*u+v*v)
    ck('density_only_has_no_transfer',pb(rho/2,density_only)==0 and pb((u*u+v*v)/2,density_only)==0)
    t,delta,aa,ee,rr,z=s.symbols('t delta aa ee rr z',real=True)
    ck('reservoir_square',s.expand(aa*z*z-ee*rr*z+ee**2*rr**2/(4*aa)-aa*(z-ee*rr/(2*aa))**2)==0)
    lower=delta/2+gamma*(t-rho0)**2/6-beta*t
    complete=(delta-D)/2+gamma*(t-rho0-3*beta/gamma)**2/6
    ck('phase_square',s.expand(lower-complete)==0)
    ck('wrong_half_shift_rejected',s.expand(lower-((delta-D/2)/2+gamma*(t-rho0-3*beta/gamma)**2/6))!=0)
    g,A,dens=s.symbols('g A dens',positive=True)
    ck('cubic_coercivity',s.expand(g*dens**3/12-A*dens**2+64*A**3/(3*g*g)-g*(dens-8*A/g)**2*(dens+4*A/g)/12)==0)
    trial_r=eps*rho0
    trial_upper=-s.Rational(3,4)*eps**2*rho0**2+trial_r**4/4
    ck('strict_negative_trial',trial_upper<0)
    cr=s.symbols('cr',real=True)
    ck('pair_hessian_split',s.hessian(-ep*cr*sr,list(xs)+list(ys))==s.diag(*([-2*ep*cr]*3+[2*ep*cr]*3)))
    report={'status':'PASS_INDEPENDENT_ALGEBRA','script_sha256':sha(Path(__file__)),'contract_sha256':sha(cp),'checks':checks,
            'derived':{k:str(vv) for k,vv in {'rho_star':rho0,'D':D,'two_D':2*D,'trial_r':trial_r,'trial_upper':trial_upper}.items()},
            'scope':'Non-importing reviewer implementation. ODE and finite-K coexistence proof are separately analytic; not a finite phase sweep.',
            'non_claims':'No physical state/time, relaxation, uniform jump, limit, Pre-A, QFT, gravity or TOE.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH001 INDEPENDENT: PASS',len(checks),'checks')


if __name__=='__main__': main()
