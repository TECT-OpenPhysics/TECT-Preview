"""Non-importing PAH-OMC-018 audit by expanded energy and root images.

Reads only immutable contracts. No primary module import. Exact fixtures
check source conventions; inverse-domain counting and square-weight algebra
are distinct formulations of the analytic estimate, not a proof by tables.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as R
import hashlib
import json
from pathlib import Path
import sympy as sy

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
PR='strategy/pa-hyp/PAH-OMC-018-generator-prereg-v1.json'
PIN='92a4fa92cb8c0384812220acd2e9929539a10a114fe348ea3f8aa7676f98aa05'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc018-generator/independent.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(output):
    checks=[]
    def ck(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    ck('preregistration',sha(ROOT/PR)==PIN)
    for p,h in json.loads((ROOT/PR).read_text())['sources'].items(): ck('source:'+p,sha(ROOT/p)==h)
    source=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())
    p={k:R(str(v)) for k,v in source['scope']['fixed_parameters'].items()}
    base=source['scope']['path']['base']
    fixtures=[]
    for n in (2,4):
        edges=[(2*i,2*i+1) for i in range(n+2)]
        edges += [(2*i+k,2*i+k+2) for i in range(n+1) for k in (0,1)]
        edges += [(2*i,2*i+3) for i in range(n)]
        triangles=[face for i in range(n) for face in ((2*i,2*i+2,2*i+3),(2*i,2*i+3,2*i+1))]
        polygons=triangles+[(2*n,2*n+2,2*n+3,2*n+1)]
        def value(rad,ap,phase,links):
            ans=R(0)
            for v,t in enumerate(rad):
                s=ap[v]
                ans+=p['lambda_s']*(s*s-2*s+1)/2+(p['m2']+p['g']*s*s)*t*t/2+p['lambda_4']*t**4/4+p['eta_6']*t**6/6
            for a,b in edges:
                ans+=p['kappa_s']*(ap[a]*ap[a]+ap[b]*ap[b]-2*ap[a]*ap[b])/2
                ans+=p['kappa_D']*(rad[a]*rad[a]+rad[b]*rad[b]-2*phase[a]*links[(a,b)]*phase[b]*rad[a]*rad[b])/(ap[a]+ap[b])
            for poly in polygons:
                boundary=list(zip(poly,poly[1:]+poly[:1])); hol=1; jsum=R(0)
                for a,b in boundary:
                    hol*=links[tuple(sorted((a,b)))]; jsum+=2/(ap[a]+ap[b])
                ans+=p['kappa_g']*jsum*(1-hol)/len(poly)
            return ans
        for j in (0,1):
            cap=base**(2*j); step=R(1,base**j)
            for seed in (0,1):
                r=[step*((3*(v//2)+v%2+seed)%(cap+1)) for v in range(2*(n+2))]
                s=[p['epsilon']+(1-p['epsilon'])*((v//2+v%2+seed)%2) for v in range(len(r))]
                ph=[(-1)**((v//2+seed)%2) for v in range(len(r))]
                links={(a,b):(-1)**(a+b+seed) for a,b in edges}; F=value(r,s,ph,links)
                for kind in ('PH','LK','AP','TR'):
                    for sign in (-1,1):
                        rr,ss,pp,ll=r.copy(),s.copy(),ph.copy(),links.copy()
                        if kind=='PH': pp[0]=-pp[0]; m2=s[0]**(2*p['nu'])
                        elif kind=='LK': ll[(0,1)]=-ll[(0,1)]; m2=(s[0]*s[1])**p['nu']
                        elif kind=='AP':
                            target=s[0]+sign*(1-p['epsilon'])/p['M_s']
                            if target not in (p['epsilon'],R(1)): continue
                            ss[0]=target; m2=(s[0]*target)**p['nu']
                        else:
                            donor,recv=(0,1) if sign>0 else (1,0)
                            if r[donor]/step==0 or r[recv]/step==cap: continue
                            rr[donor]-=step; rr[recv]+=step; m2=(s[0]*s[1])**p['nu']
                        d=value(rr,ss,pp,ll)-F
                        ck(f'positive mobility {n}:{j}:{seed}:{kind}:{sign}',0<m2<=1)
                        fixtures.append({'n':n,'j':j,'seed':seed,'kind':kind,'sign':sign,'F':str(F),'delta':str(d),'mobility_squared':str(m2),'delta_b':str(min(R(1),rr[0])-min(R(1),r[0])),'delta_s':str(ss[0]-s[0])})
    # Independent exact partial-domain enumeration, no Gibbs quadrature.
    for cap in (1,4,16):  # TEST INPUTS on the preregistered dyadic path.
        dom={(a,b) for a in range(cap+1) for b in range(cap+1) if a>=1 and b<cap}
        image={(a-1,b+1) for a,b in dom}
        inverse={(a,b) for a in range(cap+1) for b in range(cap+1) if b>=1 and a<cap}
        ck(f'inverse-domain equality:{cap}',image==inverse and len(image)==len(dom))
        ck(f'partial not total:{cap}',len(image)<(cap+1)**2)
    a,b,m,Z=sy.symbols('a b m Z',positive=True)
    # a,b are square roots of unnormalized Gibbs weights. c=m*b/a.
    ck('square-root weight square transport',sy.cancel((a*a/Z)*(m*b/a)**2-m*m*b*b/Z)==0)
    ck('square-root weight balance',sy.cancel((a*a/Z)*(m*b/a)-(b*b/Z)*(m*a/b))==0)
    u,v,K=sy.symbols('u v K',real=True)
    ck('two summand norm control',sy.expand(2*(u*u+v*v)-(u+v)**2-(u-v)**2)==0)
    ck('tail multiplier identity',sy.expand(u*u-u*K-u*(u-K))==0)
    closure=[]
    degree=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-004-v1.json').read_text())['exact_scope']['strip_family']['degree_bound']
    for m0 in range(5):
        n=max(2,m0+2); vertices=set(range(2*(m0+1)))
        links=[(2*i,2*i+1) for i in range(n+2)]+[(2*i+k,2*i+2+k) for i in range(n+1) for k in (0,1)]+[(2*i,2*i+3) for i in range(n)]
        H=sum(2 for e in links if set(e)&vertices)
        E=sum(set(e)<=vertices for e in links); D=4*len(vertices)+2*E
        ck(f'root bound:{m0}',H<=2*degree*len(vertices))
        closure.append({'m':m0,'N':n,'H':H,'D':D})
    data={'status':'PASS','lane':'independent','checks':checks,'fixtures':fixtures,'closure':closure,
          'code_version':__version__,'code_sha256':sha(Path(__file__)),'prereg_sha256':PIN,
          'scope':'Non-importing expanded-energy and square-root-weight derivation; internal independent implementation, not external signed review.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-018 INDEPENDENT: PASS ({len(checks)} checks)')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,default=OUT)
    run(p.parse_args().output)
