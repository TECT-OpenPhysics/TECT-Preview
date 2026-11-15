#!/usr/bin/env python3
"""Exact all-lattice spectral certificate and pointwise reservoir shear.

Original finite Fourier blocks only. Rational interval certificates are
tooling inputs, not model parameters. No collocation or time simulation.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-alt002'
PIN='9ded4fd4a2e29c759bc4ea4925edb58b197546c91871c0344e2b69209d3d98ca'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cp=ROOT/'strategy/physical-candidates/TECT-ALT-002-contract-v1.json'
    assert sha(cp)==PIN
    contract=json.loads(cp.read_text())
    for p,h in contract['source_hashes'].items():assert sha(ROOT/p)==h,p
    old=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for p,h in old['source_hashes'].items():assert sha(ROOT/p)==h,p
    p=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    src=json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())
    rat=lambda v:s.Rational(str(v))
    V=s.prod(rat(p[k]) for k in ('Lx','Ly','Lz'));Q=rat(src['exact_constants']['coexistence_charge']);q=Q/V
    eps,omega,u=(rat(old['model']['inserted_parameters'][k]) for k in ('epsilon','omega','u'))
    mu=(omega+u*q)/2;c2=4*eps**2*q
    checks={}
    def ck(k,b):checks[k]=bool(b);assert checks[k],k
    ck('original_reservoir_coefficients',omega==u==1)
    ck('isotropic_side16',p['Lx']==p['Ly']==p['Lz']==16)
    ck('zero_shell_positive_floors',rat(p['eta_shell'])==0 and rat(p['rho_regularizer'])>0 and rat(p['classii_mass_regularizer'])>0)
    z0=s.Matrix(list(map(rat,p['z0'])))
    M=s.diag(*map(rat,p['family_masses']))+rat(p['k_lock'])*(s.eye(3)-z0*z0.T/z0.dot(z0))
    w=s.symbols('w');poly=s.Poly(M.charpoly(w).as_expr(),w)
    # Rational isolation windows and margins are certificate thresholds only.
    roots=[(s.Rational(28,1000),s.Rational(29,1000)),(s.Rational(165,1000),s.Rational(166,1000)),(s.Rational(206,1000),s.Rational(207,1000))]
    for i,(a,b) in enumerate(roots):ck('root_'+str(i),poly.count_roots(a,b)==1)
    ck('all_three_roots',poly.degree()==3)
    def atan_bounds(x,n):
        a=sum((-1)**j*x**(2*j+1)/(2*j+1) for j in range(n));err=x**(2*n+1)/(2*n+1)
        return (a,a+err) if n%2==0 else (a-err,a)
    al,ah=atan_bounds(s.Rational(1,5),6);bl,bh=atan_bounds(s.Rational(1,239),3)
    plo,phi=s.Rational(314159,100000),s.Rational(3927,1250)
    ck('pi_machin_enclosure',plo<16*al-4*bh<16*ah-4*bl<phi)
    R,Z,Y=(rat(p[k]) for k in ('r','Z','Y'))
    scale=(2/rat(p['Lx']))**2
    ck('interval_signs',Y>0 and Z<0)
    def interval(m):
        xl,xh=m*scale*plo**2,m*scale*phi**2
        return R+Z*xh+Y*xl**2,R+Z*xl+Y*xh**2
    ds=[];margins=[];deltas=[]
    for m in range(7):
        fl,fh=interval(m);dl,dh=fl+roots[0][0]-mu,fh+roots[0][1]-mu
        ck('low_negative_'+str(m),dl<=dh<0)
        margin=dh**2-c2;ck('low_gap_'+str(m),margin>s.Rational(1,2000))
        ds.append([str(dl),str(dh)]);margins.append(margin);deltas.append(-dh)
    fl,fh=interval(7);tail=fl+roots[0][0]-mu
    x7=7*scale*plo**2
    ck('tail_monotone',2*Y*x7+Z>0)
    ck('tail_positive_gap',tail>0 and tail**2-c2>s.Rational(1,2000))
    deltas.append(tail);margins.append(tail**2-c2)
    grows=[]
    for i in (1,2):
        fl,fh=interval(1);dl,dh=fl+roots[i][0]-mu,fh+roots[i][1]-mu
        margin=c2-max(dl**2,dh**2)
        ck('growing_orientation_'+str(i),margin>s.Rational(1,2000))
        grows.append(margin)
    delta=min(deltas);cupper=s.Rational(1,25)
    ck('coupling_upper',c2<cupper**2)
    ck('order_flow_bound_four',15*delta>17*cupper)
    # Full real two-coordinate Hamiltonian block, not a sign of energy alone.
    d,c=s.symbols('d c',real=True);A=s.Matrix([[0,d+c],[-d+c,0]])
    ck('order_generator_square',s.simplify(A*A-(c*c-d*d)*s.eye(2))==s.zeros(2))
    W=s.diag(d-c,d+c)
    ck('order_weighted_energy',s.simplify(A.T*W+W*A)==s.zeros(2))
    # Pointwise reservoir radial pair; nonzero Fourier cosines survive fixed Q.
    qq,t=s.symbols('q t',positive=True);N=s.Matrix([[0,0],[-2*u*qq,0]])
    ck('reservoir_nilpotent',N*N==s.zeros(2) and N!=s.zeros(2))
    E=s.eye(2)+t*N
    ck('exact_shear_solution',E.diff(t)==N*E)
    ck('shear_norm',s.expand((E*s.Matrix([1,0])).dot(E*s.Matrix([1,0]))-(1+4*u*u*qq*qq*t*t))==0)
    delta0=s.symbols('delta',real=True)
    theta=s.symbols('theta',real=True)
    curve_density=(1+delta0*s.cos(theta))**2/(1+delta0**2/2)
    ck('exact_fixed_charge_curve',s.simplify(s.integrate(curve_density,(theta,0,2*s.pi))/(2*s.pi))==1)
    # Equality of energy/charge for unit Frobenius rank-one projector vs scalar.
    P=s.Matrix([1,2,3]);P=P/s.sqrt(P.dot(P));C=P*P.T
    ck('rank_one_frobenius',s.simplify(s.trace(C.T*C))==1)
    ck('wrong_identity_matching_rejected',s.trace(s.eye(3).T*s.eye(3))!=1)
    out={'status':'PASS_EXACT_MATCHED_LINEAR_CLASSIFICATION','script_sha256':sha(Path(__file__)),'contract_sha256':PIN,
         'checks':checks,'derived':{'Qbar':str(Q),'V':str(V),'q':str(q),'muR':str(mu),'coupling_squared':str(c2),
            'root_windows':[[str(a),str(b)] for a,b in roots],'low_d_intervals_m0_to6':ds,
            'min_low_squared_gap':str(min(margins)),'min_absolute_detuning':str(delta),
            'middle_growth_squared_lower':str(grows[0]),'high_growth_squared_lower':str(grows[1]),
            'order_flow_norm_bound':4,'full_low_flow_bound':'4+2q*abs(tau)','reservoir_growth_ratio_squared':'1+4q²*tau²'},
         'scope':'All lattice modes by finite low-shell certificate plus monotone high tail. Every constant reservoir has full linear shear; no nonlinear or physical result.'}
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'primary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('ALT002 PRIMARY: PASS',len(checks),'exact checks')


if __name__=='__main__':main()
