#!/usr/bin/env python3
"""Non-importing real-canonical verifier of the augmented-state witness.

Independent derivation by next_gate_math: density Hamiltonian in eight real
constant amplitudes, with brackets 1/V and H=V*h. Spatial first variations
are justified in the synthesis, not replaced by an invariant-mode assumption.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-exch006/independent.json'


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cp=ROOT/'strategy/physical-candidates/TECT-EXCH-006-contract-v1.json'
    contract=json.loads(cp.read_text())
    assert sha(cp)=='adbc069cf08df9c17d862c2bbe0f4ff45aafafab1465c1d6bad87e76b3be994e'
    for path,digest in contract['source_hashes'].items():
        assert sha(ROOT/path)==digest,path
    p=json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    old=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    rat=lambda value:s.Rational(str(value))
    eps,omega,u=(rat(old['model']['inserted_parameters'][k]) for k in ('epsilon','omega','u'))
    V=s.prod(rat(p[k]) for k in ('Lx','Ly','Lz'))
    z0=s.Matrix(list(map(rat,p['z0'])))
    L=rat(p['r'])*s.eye(3)+s.diag(*map(rat,p['family_masses']))+rat(p['k_lock'])*(s.eye(3)-z0*z0.T/z0.dot(z0))
    x=s.symbols('x0:3',real=True);y=s.symbols('y0:3',real=True)
    c,d=s.symbols('c d',real=True)
    X,Y=s.Matrix(x),s.Matrix(y)
    rho=X.dot(X)+Y.dot(Y);nchi=c*c+d*d
    reS=X.dot(X)-Y.dot(Y);imS=2*X.dot(Y)
    hp=(X.dot(L*X)+Y.dot(L*Y))/2+rat(p['lambda'])*rho**2/4+rat(p['gamma'])*rho**3/6
    hc=omega*nchi/2+u*nchi**2/4
    hi=-eps*(c*reS+d*imS);h=hp+hc+hi
    pairs=list(zip(x,y))+[(c,d)]
    def D(f):
        return s.expand(sum(s.diff(f,a)*s.diff(h,b)-s.diff(f,b)*s.diff(h,a) for a,b in pairs))
    q=-3*rat(p['lambda'])/(8*rat(p['gamma']))
    r=q;aa=q-r*r;a=s.sqrt(aa)
    A=dict(zip(x+y+(c,d),(a,0,0,0,a,0,r,0)))
    B=dict(zip(x+y+(c,d),(0,a,0,a,0,0,r,0)))
    at=lambda f,state:s.simplify(f.subs(state))
    rz=V*(c*reS+d*imS);iz=V*(c*imS-d*reS);J=2*eps*iz
    obs={'H':V*h,'Fpsi':V*hp,'Hchi':V*hc,'Hint':V*hi,'Q':V*(rho/2+nchi),'Npsi':V*rho,'Nchi':V*nchi,'ReZ':rz,'ImZ':iz}
    checks={}
    def ck(name,condition):
        checks[name]=bool(condition);assert checks[name],name
    for name,f in obs.items():
        ck('same_'+name,at(f,A)==at(f,B))
    ck('positive_amplitudes',q>0 and aa>0)
    ck('full_sector',at(obs['Q'],A)==V*q)
    ck('rho_regularizer',rat(p['rho_regularizer'])>0)
    ck('classii_regularizer',rat(p['classii_mass_regularizer'])>0)
    ck('eta_zero',rat(p['eta_shell'])==0)
    ck('lock_diagonal_equal',z0[0]**2==z0[1]**2)
    ck('pair_zero',at(rz,A)==at(iz,A)==0)
    ck('component_charge_convention',s.expand(D(obs['Npsi'])-4*eps*iz)==0)
    delta=L[0,0]-L[1,1]
    dia,dib=at(D(iz),A),at(D(iz),B)
    ja,jb=at(D(J),A),at(D(J),B)
    ck('mass_split',delta!=0)
    ck('coherence_drift_gap',s.simplify(dia-dib+4*V*r*aa*delta)==0)
    ck('current_drift_gap',s.simplify(ja-jb+8*eps*V*r*aa*delta)==0)
    ck('opposite_acceleration',ja>0 and jb<0)
    ck('same_zero_initial_current',at(J,A)==at(J,B)==0)
    ck('same_real_drift',at(D(rz),A)==at(D(rz),B))
    # Hostile control: with the original equal lock diagonals, removing only
    # mass splitting in this symbolic calculation kills this witness gap.
    # This is a test oracle, NOT an allowed replacement of the source model.
    m1,m2=s.symbols('m1 m2',real=True)
    gap=-4*V*r*aa*(m1-m2)
    ck('mass_degenerate_control',gap.subs(m1,m2)==0 and gap.subs({m1:rat(p['family_masses'][0]),m2:rat(p['family_masses'][1])})==dia-dib)
    out={'status':'PASS_INDEPENDENT_REAL_CANONICAL','contract_sha256':sha(cp),'script_sha256':sha(Path(__file__)),
         'checks':checks,'shared':{k:str(at(f,A)) for k,f in obs.items()},
         'derived':{'Q':str(V*q),'q':str(q),'r':str(r),'a_squared':str(aa),'delta':str(delta),
                    'dImZ':[str(dia),str(dib)],'dReZ':[str(at(D(rz),A)),str(at(D(rz),B))],
                    'dJ':[str(ja),str(jb)],'dJ_gap':str(s.simplify(ja-jb))}}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH006 INDEPENDENT: PASS',len(checks),'exact checks')


if __name__=='__main__':main()
