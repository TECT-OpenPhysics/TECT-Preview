"""Exact source-energy and inverse-root tests for PAH-OMC-018.

Rational fixtures only audit the analytic all-cutoff proof. No partition
sweep, modified carrier or fitted rates. The Gibbs square identity, not a
pointwise rate bound, supplies the uniform estimate in the certificate.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as sp

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
PR='strategy/pa-hyp/PAH-OMC-018-generator-prereg-v1.json'
PIN='92a4fa92cb8c0384812220acd2e9929539a10a114fe348ea3f8aa7676f98aa05'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc018-generator/primary.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def params():
    c=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())
    return {k:Q(str(v)) for k,v in c['scope']['fixed_parameters'].items()}

def mesh_base():
    return json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())['scope']['path']['base']

def graph(n):
    edges={('v',i):(2*i,2*i+1) for i in range(n+2)}
    edges.update({('h',i,k):(2*i+k,2*i+2+k) for i in range(n+1) for k in (0,1)})
    edges.update({('d',i):(2*i,2*i+3) for i in range(n)})
    faces=[]
    for i in range(n):
        faces += [[('h',i,0),('v',i+1),('d',i)], [('d',i),('h',i,1),('v',i)]]
    faces += [[('h',n,0),('v',n+1),('h',n,1),('v',n)]]
    return edges,faces

def state(n,j,seed):
    p=params(); base=mesh_base(); M=base**(2*j); h=Q(1,base**j)
    es,_=graph(n)
    r=[h*((3*(v//2)+v%2+seed)%(M+1)) for v in range(2*(n+2))]
    s=[p['epsilon']+(1-p['epsilon'])*((v//2+v%2+seed)%2) for v in range(len(r))]
    ph=[(-1)**((v//2+seed)%2) for v in range(len(r))]
    lk={e:(-1)**(a+b+seed) for e,(a,b) in es.items()}
    return r,s,ph,lk

def energy(n,x):
    p=params(); r,s,ph,lk=x; es,fs=graph(n)
    J={e:2/(s[a]+s[b]) for e,(a,b) in es.items()}
    value=sum(p['lambda_s']*(t-1)**2/2+p['m2']*a*a/2+p['lambda_4']*a**4/4+p['eta_6']*a**6/6+p['g']*t*t*a*a/2 for a,t in zip(r,s))
    value+=sum(p['kappa_s']*(s[a]-s[b])**2/2+p['kappa_D']*J[e]*(ph[b]*r[b]-lk[e]*ph[a]*r[a])**2/2 for e,(a,b) in es.items())
    for face in fs:
        hol=1
        for e in face: hol*=lk[e]
        value+=p['kappa_g']*sum(J[e] for e in face)/len(face)*(1-hol)
    return value

def move(x,j,kind,sign):
    r,s,ph,lk=x; y=(r.copy(),s.copy(),ph.copy(),lk.copy())
    p=params(); base=mesh_base(); h=Q(1,base**j); R=Q(base**j); msq=Q(0)
    if kind=='PH': y[2][0]*=-1; msq=s[0]**(2*p['nu'])
    if kind=='LK': y[3][('v',0)]*=-1; msq=(s[0]*s[1])**p['nu']
    if kind=='AP':
        target=s[0]+sign*(1-p['epsilon'])/p['M_s']
        if not p['epsilon']<=target<=1: return None
        y[1][0]=target; msq=(s[0]*target)**p['nu']
    if kind=='TR':
        a,b=(0,1) if sign==1 else (1,0)
        if r[a]<h or r[b]>R-h: return None
        y[0][a]-=h; y[0][b]+=h; msq=(s[a]*s[b])**p['nu']
    return y,msq

def run(output):
    checks=[]
    def ck(k,b):
        assert bool(b),k
        checks.append({'name':k,'pass':True})
    ck('preregistration',sha(ROOT/PR)==PIN)
    for p,h in json.loads((ROOT/PR).read_text())['sources'].items(): ck('source:'+p,sha(ROOT/p)==h)
    x,y,m,Z=sp.symbols('F_x F_y m Z',positive=True)
    rate=m*sp.exp(-(y-x)/2); pi=sp.exp(-x)/Z
    ck('Gibbs square transport',sp.simplify(pi*rate**2-m*m*sp.exp(-y)/Z)==0)
    ck('directed conductance balance',sp.simplify(pi*rate-sp.exp(-y)/Z*m*sp.exp(-(x-y)/2))==0)
    z=sp.symbols('F_z',real=True)
    ck('two-root envelope exponent',sp.expand(-x-(y-x)/2-(z-x)/2+(y+z)/2)==0)
    f,g,ft,gt,c=sp.symbols('f g ft gt c',real=True)
    ck('inverse pair form half',sp.expand(-c*(f*(gt-g)+ft*(g-gt))-c*(ft-f)*(gt-g))==0)
    fixtures=[]
    for n in (2,4):
        es,fs=graph(n)
        ck(f'incidence:{n}',len(es)==4*n+4 and len(fs)==2*n+1)
        for j in (0,1):
            for seed in (0,1):
                a=state(n,j,seed); F=energy(n,a)
                for kind in ('PH','LK','AP','TR'):
                    for sign in (-1,1):
                        ans=move(a,j,kind,sign); key=f'{n}:{j}:{seed}:{kind}:{sign}'
                        if ans is None: continue
                        b,msq=ans; inv=move(b,j,kind,-sign)
                        ck('inverse:'+key,inv==(a,msq))
                        d=energy(n,b)-F
                        db=min(Q(1),b[0][0])-min(Q(1),a[0][0]); ds=b[1][0]-a[1][0]
                        ck('mobility:'+key,0<msq<=1)
                        ck('radial or label discriminator:'+key,abs(db)<=Q(1,mesh_base()**j) if kind=='TR' else db==0)
                        fixtures.append({'n':n,'j':j,'seed':seed,'kind':kind,'sign':sign,'F':str(F),'delta':str(d),'mobility_squared':str(msq),'delta_b':str(db),'delta_s':str(ds)})
    closure=[]
    degree=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-004-v1.json').read_text())['exact_scope']['strip_family']['degree_bound']
    for m0 in range(5):
        n=max(2,m0+2); es,fs=graph(n); vs=set(range(2*(m0+1)))
        retained={e for e,ends in es.items() if max(ends)//2<=m0}
        H=2*sum(bool(vs.intersection(ends)) for ends in es.values())
        D=4*len(vs)+2*len(retained)
        ck(f'support bound:{m0}',H<=2*degree*len(vs))
        touched=[e for e,ends in es.items() if vs.intersection(ends)]
        face_support={v for face in fs if set(face).intersection(touched) for e in face for v in es[e]}
        ck(f'nonradial closure:{m0}',max(face_support)//2<=m0+1)
        ck(f'terminal disjoint:{m0}',not set(fs[-1]).intersection(touched))
        closure.append({'m':m0,'N':n,'H':H,'D':D})
    data={'status':'PASS','lane':'primary','checks':checks,'fixtures':fixtures,'closure':closure,
          'code_version':__version__,'code_sha256':sha(Path(__file__)),'prereg_sha256':PIN,
          'scope':'Exact finite source and symbolic identity audits; all-j,n proof is analytic, no numerical extrapolation.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-018 PRIMARY: PASS ({len(checks)} checks)')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,default=OUT)
    run(p.parse_args().output)
