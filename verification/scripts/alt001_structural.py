#!/usr/bin/env python3
"""Separate reviewer's tensor/density comparison, not overall model ranking.

Exact real Poisson calculations, Frobenius normalization and same-sector
INITIAL second response. No full-P1 U3 symmetry or all-time dominance claim.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-exch002/alternative.json'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cp=ROOT/'strategy/physical-candidates/TECT-ALT-001-contract-v1.json'
    assert sha(cp)=='75e8a1e70a27a9880bdcc17a74f812dbeb95a2be4f6cb4ef9f51c98ff3cfe060'
    checks={}
    def ck(k,v):
        checks[k]=bool(v);assert checks[k],k
    x=s.symbols('x0:3',real=True);y=s.symbols('y0:3',real=True)
    psi=s.Matrix([x[i]+s.I*y[i] for i in range(3)]);basis=[]
    for i in range(3):
        E=s.zeros(3);E[i,i]=1;basis.append(E)
    for i,j in ((0,1),(0,2),(1,2)):
        E=s.zeros(3);E[i,j]=E[j,i]=1/s.sqrt(2);basis.append(E)
    ck('orthonormal_basis',s.Matrix([[s.trace(a.conjugate().T*b) for b in basis] for a in basis])==s.eye(6))
    P=psi*psi.T;pc=[s.expand(s.trace(E.conjugate().T*P)) for E in basis]
    rho=s.expand((psi.conjugate().T*psi)[0])
    ck('pair_norm',s.expand(sum(s.expand_complex(s.conjugate(p)*p) for p in pc)-rho**2)==0)
    r=s.symbols('r0:6',real=True);t=s.symbols('t0:6',real=True);ep=s.symbols('ep',real=True)
    pre=list(map(lambda p:s.expand(s.re(p)),pc));pim=list(map(lambda p:s.expand(s.im(p)),pc))
    h=-ep*sum(r[i]*pre[i]+t[i]*pim[i] for i in range(6));flux=sum(r[i]*pim[i]-t[i]*pre[i] for i in range(6))
    qp=rho/2;qc=sum(r[i]**2+t[i]**2 for i in range(6))/2;pairs=list(zip(x,y))+list(zip(r,t))
    def pb(f,g,pairs):return s.expand(sum(s.diff(f,a)*s.diff(g,b)-s.diff(f,b)*s.diff(g,a) for a,b in pairs))
    dp,dc=pb(qp,h,pairs),pb(qc,h,pairs)
    ck('psi_transfer',s.expand(dp-2*ep*flux)==0);ck('C_transfer',s.expand(dc+ep*flux)==0)
    ck('weighted_charge',s.expand(dp+2*dc)==0);ck('unweighted_rejected',s.expand(dp+dc)!=0)
    zero=dict.fromkeys(r+t,0)
    ck('zero_first_response',dc.subs(zero)==0)
    ddc=s.expand(pb(dc,h,pairs).subs(zero))
    ck('tensor_second_response',s.expand(ddc-ep**2*rho**2)==0)
    u,v=s.symbols('u v',real=True);S=s.expand((psi.T*psi)[0]);sr,si=s.expand(s.re(S)),s.expand(s.im(S))
    ps=list(zip(x,y))+[(u,v)];hs=-ep*(u*sr+v*si);ds=pb((u*u+v*v)/2,hs,ps)
    dds=s.expand(pb(ds,hs,ps).subs({u:0,v:0}))
    ck('scalar_second_response',s.expand(dds-ep**2*(sr*sr+si*si))==0)
    gram=4*sum((x[i]*y[j]-x[j]*y[i])**2 for i in range(3) for j in range(i+1,3))
    ck('response_domination',s.expand(rho**2-sr*sr-si*si-gram)==0)
    a1=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    src=json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())['exact_constants']
    ex=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    V=s.prod(s.Rational(str(a1[k])) for k in ('Lx','Ly','Lz'));Q=s.Rational(src['coexistence_charge']);q=Q/V
    eps=s.Rational(ex['model']['inserted_parameters']['epsilon'])
    state=dict.fromkeys(x+y,0);state.update({x[0]:s.sqrt(q),y[1]:s.sqrt(q)})
    ck('same_sector',s.simplify(qp.subs(state)*V-Q)==0);ck('scalar_cancellation',s.simplify(S.subs(state))==0)
    tensor=s.simplify(ddc.subs(state).subs(ep,eps)*V);scalar=s.simplify(dds.subs(state).subs(ep,eps)*V)
    ck('strict_initial_advantage',tensor>0 and scalar==0)
    eta=s.Rational(1,16)  # Explicit ALT-DENSITY admission input, not a derived output.
    hd=eta*rho*(u*u+v*v)
    ck('density_no_psi_transfer',pb(qp,hd,ps)==0);ck('density_no_reservoir_transfer',pb((u*u+v*v)/2,hd,ps)==0)
    # Exact test-control inputs, not fitted model parameters.
    w=s.Matrix([1,2,3]);house=s.eye(3)-2*w*w.T/(w.T*w)[0]
    U=s.diag(1,s.I,(3+4*s.I)/5)*house
    ck('unitary_control',s.simplify(U.conjugate().T*U)==s.eye(3))
    z=s.Matrix([1+s.I,2-s.I,-1+3*s.I]);P0=z*z.T
    C=s.Matrix([[1+2*s.I,2-s.I,3],[2-s.I,-2+s.I,1+s.I],[3,1+s.I,4-s.I]])
    Cn=s.simplify(U*C*U.T);Pn=s.simplify((U*z)*(U*z).T)
    ck('pair_covariance_control',s.simplify(Pn-U*P0*U.T)==s.zeros(3))
    ck('symmetric_control',s.simplify(Cn-Cn.T)==s.zeros(3))
    ck('norm_covariance_control',s.simplify(s.trace(Cn.conjugate().T*Cn)-s.trace(C.conjugate().T*C))==0)
    ck('interaction_covariance_control',s.simplify(s.trace(Cn.conjugate().T*Pn)-s.trace(C.conjugate().T*P0))==0)
    w=w/s.sqrt(14);a,b,c,d=s.symbols('a b c d',real=True);phi=a+s.I*b;chi=c+s.I*d;z=phi*w;C=chi*w*w.T
    ck('rank_one_norm',s.simplify(s.trace(C.conjugate().T*C)-(c*c+d*d))==0)
    ck('rank_one_coupling',s.simplify(s.trace(C.conjugate().T*z*z.T)-s.conjugate(chi)*phi**2)==0)
    ck('rank_one_interaction_field',s.simplify(C*s.conjugate(z)-chi*s.conjugate(phi)*w)==s.zeros(3,1))
    report={'status':'PASS_ALT_STRUCTURAL_CONTROLS','script_sha256':sha(Path(__file__)),'contract_sha256':sha(cp),'checks':checks,
      'derived':{'Qbar':str(Q),'q':str(q),'tensor_second_response':str(tensor),'scalar_second_response':str(scalar)},
      'scope':'Structural gain only, same-sector initial response. Scalar cancellation need not persist under full P1. No stability superiority or physical adoption.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('ALT001 STRUCTURAL: PASS',len(checks),'checks')


if __name__=='__main__':main()
