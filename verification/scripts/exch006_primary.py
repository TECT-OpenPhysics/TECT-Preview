#!/usr/bin/env python3
"""Complex-canonical full-initial-field witness for augmented nonclosure.

The written first-variation crosswalk eliminates spatial/ClassII terms at
constant initial fields; this is not an assumed invariant reduced dynamics.
All parameters are read exactly from preserved upstream sources.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-15-exch006'


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    cp = ROOT/'strategy/physical-candidates/TECT-EXCH-006-contract-v1.json'
    assert sha(cp) == 'adbc069cf08df9c17d862c2bbe0f4ff45aafafab1465c1d6bad87e76b3be994e'
    contract = json.loads(cp.read_text(encoding='utf-8'))
    for path, digest in contract['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    old = json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for path, digest in old['source_hashes'].items():
        assert sha(ROOT/path) == digest, path
    p = json.loads((ROOT/'claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json').read_text())['parameters']
    src = json.loads((ROOT/'claims/A2-FULL-PRODUCTION-WELLPOSED/charge_ensemble_first_order_shell_transition_manifest.json').read_text())
    rat = lambda value: s.Rational(str(value))
    V = s.prod(rat(p[k]) for k in ('Lx','Ly','Lz'))
    Q = rat(src['exact_constants']['coexistence_charge'])
    q = Q/V
    r, aa = q, q-q*q
    eps, omega, u = (rat(old['model']['inserted_parameters'][k]) for k in ('epsilon','omega','u'))
    z0 = s.Matrix(list(map(rat,p['z0'])))
    L = rat(p['r'])*s.eye(3)+s.diag(*map(rat,p['family_masses']))+rat(p['k_lock'])*(s.eye(3)-z0*z0.T/(z0.T*z0)[0])
    z = s.Matrix(s.symbols('z0:3')); zb = s.Matrix(s.symbols('b0:3'))
    w, wb = s.symbols('w wb')
    pairs = list(zip(z,zb))+[(w,wb)]
    rho = (zb.T*z)[0]; nchi = w*wb
    S, Sb = (z.T*z)[0], (zb.T*zb)[0]
    Z, Zb = V*wb*S, V*w*Sb
    reZ, imZ = (Z+Zb)/2, (Z-Zb)/(2*s.I)
    hp = (zb.T*L*z)[0]/2+rat(p['lambda'])*rho**2/4+rat(p['gamma'])*rho**3/6
    hc = omega*nchi/2+u*nchi**2/4
    hi = -eps*(wb*S+w*Sb)/2
    h = hp+hc+hi
    # Constant amplitudes have Poisson bracket -2i/V; H=V*h cancels V.
    D = lambda f: s.expand(-2*s.I*sum(s.diff(f,a)*s.diff(h,b)-s.diff(f,b)*s.diff(h,a) for a,b in pairs))
    av = s.sqrt(aa)
    vectors = [s.Matrix([av,s.I*av,0]),s.Matrix([s.I*av,av,0])]
    states = [{**dict(zip(z,v)),**dict(zip(zb,s.conjugate(v))),w:r,wb:r} for v in vectors]
    at = lambda f,st: s.simplify(f.subs(st,simultaneous=True))
    checks = {}
    def ck(name,condition):
        checks[name] = bool(condition)
        assert checks[name],name
    ck('positive_amplitudes',r>0 and aa>0)
    ck('original_zero_shell_coefficient',rat(p['eta_shell'])==0)
    ck('floors_preserved_positive',rat(p['rho_regularizer'])>0 and rat(p['classii_mass_regularizer'])>0)
    ck('pinned_equal_lock_entries',z0[0]**2==z0[1]**2)
    obs = {'H':V*h,'Fpsi':V*hp,'Hchi':V*hc,'Hint':V*hi,'Q':V*(rho/2+nchi),'Npsi':V*rho,'Nchi':V*nchi,'ReZ':reZ,'ImZ':imZ}
    vals = [{name:at(f,st) for name,f in obs.items()} for st in states]
    ck('all_augmented_observables_equal',vals[0]==vals[1])
    ck('same_original_sector',vals[0]['Q']==Q)
    ck('both_pair_coherences_zero',vals[0]['ReZ']==vals[0]['ImZ']==0)
    ck('individual_populations_equal',all(at(z[i]*zb[i],states[0])==at(z[i]*zb[i],states[1]) for i in range(3)))
    ck('not_same_global_phase_orbit',vectors[0]!=vectors[1] and vectors[0]!=-vectors[1])
    for i in range(3):
        expected=-s.I*(L*z+rat(p['lambda'])*rho*z+rat(p['gamma'])*rho**2*z)[i]+2*s.I*eps*w*zb[i]
        ck('full_constant_gradient_'+str(i),s.expand(D(z[i])-expected)==0)
    ck('chi_field',s.expand(D(w)+s.I*(omega+u*nchi)*w-s.I*eps*S)==0)
    ck('charge_conservation',s.expand(D(obs['Q']))==0)
    ck('energy_conservation',s.expand(D(obs['H']))==0)
    ck('population_current_factor',s.expand(D(obs['Npsi'])-4*eps*imZ)==0)
    dz = [at(D(imZ),st) for st in states]
    dr = [at(D(reZ),st) for st in states]
    dj = [s.simplify(2*eps*v) for v in dz]
    delta = L[0,0]-L[1,1]
    ck('mass_split',delta!=0 and delta==rat(p['family_masses'][0])-rat(p['family_masses'][1]))
    ck('exact_drift_difference',s.simplify(dz[0]-dz[1]+4*V*r*aa*delta)==0)
    ck('nonzero_augmented_drift_defect',dz[0]!=dz[1])
    ck('opposite_current_acceleration',dj[0]>0 and dj[1]<0)
    ck('same_initial_population_drift',all(at(D(obs['Npsi']),st)==0 and at(D(obs['Nchi']),st)==0 for st in states))
    ck('same_real_coherence_drift',dr[0]==dr[1])
    # Labelled oracles independently supplied by the real-canonical verifier.
    ck('independent_gap_oracle',s.simplify(dj[0]-dj[1])==s.Rational(719261,1312200))
    out={'status':'PASS_EXACT_AUGMENTED_NONCLOSURE','contract_sha256':sha(cp),'script_sha256':sha(Path(__file__)),
         'checks':checks,'shared':{k:str(v) for k,v in vals[0].items()},
         'derived':{'V':str(V),'q':str(q),'r':str(r),'a_squared':str(aa),'delta':str(delta),
                    'dImZ':[str(v) for v in dz],'dReZ':[str(v) for v in dr],'dJ':[str(v) for v in dj],
                    'dJ_gap':str(s.simplify(dj[0]-dj[1]))},
         'scope':'Full original initial-vector-field witness at every fixed finite K>=1; no invariant truncation or physical claim.'}
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'primary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH006 PRIMARY: PASS',len(checks),'exact checks')


if __name__=='__main__':
    main()
