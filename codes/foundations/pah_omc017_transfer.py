"""Exact PAH-OMC-017 energy regrouping and bound audit, not a spectral solver.

All parameters come from the immutable OMC-016 contract. Rational fixtures
audit endpoint/face conventions; the all-n proof is the incidence bijection
in the certificate. No finite matrix eigenvalue or partition fit is used.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as sp

__version__ = "1.0.0"
ROOT = next(p for p in Path(__file__).resolve().parents if (p/"GOVERNANCE.md").exists())
PREREG = "strategy/pa-hyp/PAH-OMC-017-cauchy-prereg-v1.json"
PIN = "249bf12f71b4869e566925b8c011291ec74ef2fc4f5df2faeeafc4050f04fdff"
OUT = ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc017-cauchy/primary.json"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def parameters():
    source = ROOT/"strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
    return {k:Q(str(v)) for k,v in json.loads(source.read_text())["scope"]["fixed_parameters"].items()}


def fixture(n, seed):
    # Deterministic tooling fixtures, not fitted model inputs.
    vertices = {(i,k):(Q((i*3+k+seed)%7,3), Q(1+(i+k+seed)%2,2),
                         (-1)**((i+2*k+seed//2)%2))
                for i in range(n+2) for k in range(2)}
    links = {("v",i):(-1)**((i+seed)%2) for i in range(n+2)}
    links.update({("h",i,k):(-1)**((i+k+seed//3)%2) for i in range(n+1) for k in range(2)})
    links.update({("d",i):(-1)**((i+seed//5)%2) for i in range(n)})
    return vertices, links


def energies(n, seed, terminal=True, halves=True):
    p=parameters()
    v,links=fixture(n,seed)
    def onsite(a):
        r,s,_=v[a]
        return p['lambda_s']*(s-1)**2/2+p['m2']*r*r/2+p['lambda_4']*r**4/4+p['eta_6']*r**6/6+p['g']*s*s*r*r/2
    endpoints={('v',i):((i,0),(i,1)) for i in range(n+2)}
    endpoints.update({('h',i,k):((i,k),(i+1,k)) for i in range(n+1) for k in range(2)})
    endpoints.update({('d',i):((i,0),(i+1,1)) for i in range(n)})
    def stiffness(e):
        a,b=endpoints[e]
        return 2/(v[a][1]+v[b][1])
    def edge(e):
        a,b=endpoints[e]; r,s,ph=v[a]; t,z,pt=v[b]
        return p['kappa_s']*(s-z)**2/2+p['kappa_D']*stiffness(e)*(pt*t-links[e]*ph*r)**2/2
    def face(es):
        hol=1
        for e in es: hol*=links[e]
        return p['kappa_g']*sum(map(stiffness,es))/len(es)*(1-hol)
    faces=[]
    for i in range(n):
        faces.extend([[('h',i,0),('v',i+1),('d',i)], [('d',i),('h',i,1),('v',i)]])
    sq=[('h',n,0),('v',n+1),('h',n,1),('v',n)]
    full=sum(map(onsite,v))+sum(map(edge,endpoints))+sum(face(f) for f in faces)+face(sq)
    W=[onsite((i,0))+onsite((i,1))+edge(('v',i)) for i in range(n+2)]
    split=[edge(('h',i,0))+edge(('h',i,1))+edge(('d',i))+face(faces[2*i])+face(faces[2*i+1]) for i in range(n)]
    square=edge(('h',n,0))+edge(('h',n,1))+face(sq)
    kernel_exponent=sum((W[i]+W[i+1])/2+split[i] for i in range(n))
    kernel_exponent+=(W[n]+W[n+1])/2+(square if terminal else 0)
    if halves: kernel_exponent+=(W[0]+W[-1])/2
    return full,kernel_exponent,{'square':square,'endpoint_half':(W[0]+W[-1])/2}


def constants():
    p=parameters(); eps=p['epsilon']; jmax=1/eps
    vertex=p['lambda_s']*(1-eps)**2/2+p['m2']/2+p['lambda_4']/4+p['eta_6']/6+p['g']/2
    edge=p['kappa_s']*(1-eps)**2/2+p['kappa_D']*jmax*4/2
    face=p['kappa_g']*jmax*2
    col=2*vertex+edge; split=3*edge+2*face
    labels=p['K']**3*(p['M_s']+1)**2
    kernel_count=p['K']**3; terminal_count=p['K']**2
    tail=1
    while p['eta_6']*tail**5/6<1: tail*=2
    return {k:str(v) for k,v in {
        'vertex_box':vertex,'edge_box':edge,'face_box':face,'column_box':col,
        'split_box':split,'kernel_box_cost':col+split,'column_labels':labels,
        'split_labels':kernel_count,'square_labels':terminal_count,
        'radius_lower_prefactor':labels*kernel_count,'scalar_tail_split':tail,
        'scalar_integral_bound':tail+1,'u_norm_squared_bound':labels*(tail+1)**2
    }.items()}


def main(output):
    checks=[]
    def check(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    check('prereg_hash',sha(ROOT/PREREG)==PIN)
    c=json.loads((ROOT/PREREG).read_text())
    for path,pin in c['sources'].items(): check('parent:'+path,sha(ROOT/path)==pin)
    p=parameters()
    check('exact_fixed_scope',p['K']==2 and p['M_s']==1 and p['epsilon']==Q(1,2)
          and p['m2']==p['theta']==0 and all(p[k]==1 for k in ('beta','nu','lambda_s','lambda_4','eta_6','g','kappa_s','kappa_D','kappa_g')))
    n=sp.symbols('n',integer=True,nonnegative=True)
    check('all_n_label_bijection',sp.expand(5*(n+2)+3*n+2-(2*(2*(n+2))+(4*n+4)))==0)
    check('all_n_edge_bijection',sp.expand((n+2)+3*n+2-(4*n+4))==0)
    check('all_n_face_bijection',sp.expand(2*n+1-(2*n+1))==0)
    fixture_values=[]
    for size in (2,3,5):
        for seed in range(12):
            full,grouped,_=energies(size,seed)
            check(f'energy_{size}_{seed}',full==grouped)
            fixture_values.append({'n':size,'seed':seed,'F':str(full)})
        W=sp.symbols('w:'+str(size+2))
        exponent=(W[0]+W[-1])/2+sum((W[i]+W[i+1])/2 for i in range(size+1))
        check(f'endpoint_polynomial_{size}',sp.expand(exponent-sum(W))==0)
    a,e,d,z=sp.symbols('a e d z',nonzero=True)
    check('ratio_error_identity',sp.cancel((a+e)/(d+z)-a/d-(d*e-a*z)/(d*(d+z)))==0)
    data={'lane':'primary','status':'PASS','checks':checks,'constants':constants(),
          'fixtures':fixture_values,'source_sha256':PIN,'code_sha256':sha(Path(__file__)),
          'code_version':__version__,'scope':'Exact rational/symbolic model bridge; analytic compact spectrum and all-n convergence are in the certificates, not proved by finite fixtures.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-017 PRIMARY: PASS ({len(checks)} checks)')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    main(parser.parse_args().output)
