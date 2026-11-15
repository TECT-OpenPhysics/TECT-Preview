#!/usr/bin/env python3
"""Independent real-canonical ALT002 certificates; no primary imports.

Uses tighter root/pi windows, vertex-aware convex symbol bounds and a
six-complex-coordinate reservoir Hessian. Full P1/projection crosswalk is
analytic in the note, not an assumed invariant-mode reduction.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-alt002/independent.json'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
    rat=lambda v:s.Rational(str(v))
    cp=ROOT/'strategy/physical-candidates/TECT-ALT-002-contract-v1.json'
    assert sha(cp)=='9ded4fd4a2e29c759bc4ea4925edb58b197546c91871c0344e2b69209d3d98ca'
    for p,h in read(cp.relative_to(ROOT))['source_hashes'].items():assert sha(ROOT/p)==h,p
    checks={}
    def ck(k,b):checks[k]=bool(b);assert checks[k],k
    old=read('strategy/physical-candidates/TECT-EXCH-001-contract-v1.json')
    for p,h in old['source_hashes'].items():ck('source_'+p,sha(ROOT/p)==h)
    p=read('claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json')['parameters']
    tr=read('claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json')['exact_constants']
    eps,omega,u=(rat(old['model']['inserted_parameters'][k]) for k in ('epsilon','omega','u'))
    V=s.prod(rat(p[k]) for k in ('Lx','Ly','Lz'));Q=rat(tr['coexistence_charge']);q=Q/V;mu=(omega+u*q)/2;c2=4*eps**2*q
    ck('positive_inputs',q>0 and eps>0 and u>0)
    ck('preserved_floors',rat(p['rho_regularizer'])>0 and rat(p['classii_mass_regularizer'])>0)
    ck('original_zero_shell',rat(p['eta_shell'])==0)
    ck('original_cubic_box',rat(p['Lx'])==rat(p['Ly'])==rat(p['Lz'])==16)
    z0=s.Matrix(list(map(rat,p['z0'])))
    M=s.diag(*map(rat,p['family_masses']))+rat(p['k_lock'])*(s.eye(3)-z0*z0.T/z0.dot(z0))
    ck('real_symmetric',M==M.T)
    z=s.symbols('eigenvalue');poly=s.Poly(M.charpoly(z).as_expr(),z)
    windows=[(s.Rational(281,10000),s.Rational(282,10000)),(s.Rational(1651,10000),s.Rational(1653,10000)),(s.Rational(2066,10000),s.Rational(2068,10000))]
    for j,(lo,hi) in enumerate(windows):ck('isolated_root_'+str(j),poly.count_roots(lo,hi)==1)
    ck('exhausted_roots',poly.degree()==3 and poly.count_roots(-s.oo,windows[0][0])==0 and poly.count_roots(windows[-1][1],s.oo)==0)
    def atan_bounds(x,n):
        a=sum((-1)**j*x**(2*j+1)/(2*j+1) for j in range(n));e=x**(2*n+1)/(2*n+1)
        return (a,a+e) if n%2==0 else (a-e,a)
    al,ah=atan_bounds(s.Rational(1,5),8);bl,bh=atan_bounds(s.Rational(1,239),4)
    plo,phi=s.Rational(3141592653,10**9),s.Rational(1570796327,5*10**8)
    ck('tight_pi_enclosure',plo<16*al-4*bh<16*ah-4*bl<phi)
    Y,Z,R=(rat(p[k]) for k in ('Y','Z','r'));f=lambda x:Y*x*x+Z*x+R;vertex=-Z/(2*Y)
    ck('convex_spatial_symbol',Y>0 and Z<0)
    scale=(2/rat(p['Lx']))**2
    def bounds(m):
        xl,xh=m*scale*plo**2,m*scale*phi**2;v=[f(xl),f(xh)];mins=list(v)
        if xl<=vertex<=xh:mins.append(f(vertex))
        return min(mins),max(v)
    distances=[];gaps=[]
    for m in range(7):
        fl,fh=bounds(m);dl,dh=fl+windows[0][0]-mu,fh+windows[0][1]-mu
        ck('low_negative_'+str(m),dh<0)
        ck('low_elliptic_'+str(m),dh**2-c2>s.Rational(1,2000))
        distances.append(-dh);gaps.append(dh**2-c2)
    fl,fh=bounds(7);tail=fl+windows[0][0]-mu
    ck('tail_monotone',2*Y*(7*scale*plo**2)+Z>0)
    ck('tail_elliptic',tail>0 and tail**2-c2>s.Rational(1,2000))
    distances.append(tail);delta=min(distances);cup=s.Rational(1,25)
    ck('coupling_upper',c2<cup**2)
    ck('actual_order_norm_bound',15*delta>17*cup)
    grow={}
    for j,label,threshold in [(1,'middle',s.Rational(1,2000)),(2,'high',s.Rational(1,1000))]:
        fl,fh=bounds(1);dl,dh=fl+windows[j][0]-mu,fh+windows[j][1]-mu
        grow[label]=c2-max(dl**2,dh**2);ck(label+'_growth',grow[label]>threshold)
    x,y,d,c=s.symbols('x y d c',real=True)
    h=((d-c)*x*x+(d+c)*y*y)/2
    A=s.Matrix([s.diff(h,y),-s.diff(h,x)]).jacobian([x,y])
    ck('canonical_order_block',A==s.Matrix([[0,d+c],[-d+c,0]]))
    ck('growth_polynomial',s.simplify(A*A-(c*c-d*d)*s.eye(2))==s.zeros(2))
    W=s.diag(d-c,d+c);ck('conserved_order_metric',s.simplify(A.T*W+W*A)==s.zeros(2))
    xs=s.symbols('rx0:6',real=True);ys=s.symbols('ry0:6',real=True);v=s.Matrix(xs+ys)
    radius=sum(a*a for a in v);hres=(omega/2-mu)*radius+u*radius**2/4
    J=s.zeros(12)
    for j in range(6):J[j,j+6]=1;J[j+6,j]=-1
    base=dict.fromkeys(v,0);base[xs[0]]=s.sqrt(q)
    grad=s.Matrix([s.diff(hres,a) for a in v]);N=s.simplify(J*grad.jacobian(v).subs(base))
    expected=s.zeros(12);expected[6,0]=-2*u*q
    ck('relative_equilibrium',grad.subs(base)==s.zeros(12,1))
    ck('full_six_complex_reservoir_hessian',N==expected)
    ck('nonzero_nilpotent',N*N==s.zeros(12) and N!=s.zeros(12))
    generic=s.Matrix(s.symbols('v0:12',real=True))
    # N=2u Jvv^T, N²=(2u)² Jv(v^TJv)v^T for every orientation.
    ck('universal_orientation_nilpotence',s.expand((generic.T*J*generic)[0])==0)
    delta0,cs=s.symbols('delta cosine',real=True)
    density=s.Poly(s.expand((1+delta0*cs)**2),cs)
    average=density.nth(0)+density.nth(2)/2
    ck('exact_Q_curve',s.simplify(q*average/(1+delta0**2/2)-q)==0)
    t=s.symbols('time',real=True);B=s.Matrix([[0,0],[-2*u*q,0]]);E=s.eye(2)+t*B
    ck('exact_Jordan_evolution',s.diff(E,t)==B*E)
    outv=E*s.Matrix([1,0]);ck('transverse_growth_squared',s.expand(outv.dot(outv))==1+4*u*u*q*q*t*t)
    out={'status':'PASS_INDEPENDENT_MATCHED_LINEAR','script_sha256':sha(Path(__file__)),'contract_sha256':sha(cp),'checks':checks,
         'derived':{'Qbar':str(Q),'V':str(V),'q':str(q),'muR':str(mu),'coupling_squared':str(c2),
                    'root_windows':[[str(a),str(b)] for a,b in windows],'pi_interval':[str(plo),str(phi)],
                    'min_low_squared_gap':str(min(gaps+[tail**2-c2])),'min_absolute_detuning':str(delta),
                    'middle_growth_squared_lower':str(grow['middle']),'high_growth_squared_lower':str(grow['high']),
                    'order_flow_norm_bound':4,'reservoir_Jordan_coefficient':str(2*u*q)},
         'scope':'Independent tighter certificate and full real reservoir Hessian; no nonlinear or physical inference.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('ALT002 INDEPENDENT: PASS',len(checks),'exact checks')


if __name__=='__main__':main()
