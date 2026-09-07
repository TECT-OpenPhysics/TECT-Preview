"""Hostile sign, domain, multiplicity, topology and tail controls for OMC-018.

Finite fixtures are attacks on the exact bridge, not new finite results.
No claim of externally signed review or full analytic formalization.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as sp
import pah_omc018_generator as primary

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc018-generator/hostile.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(output):
    checks=[]
    def ck(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    F,G=sp.symbols('F G',real=True)
    good=sp.simplify(sp.exp(-F)*sp.exp(-(G-F)/2)**2-sp.exp(-G))
    bad=sp.simplify(sp.exp(-F)*sp.exp(-(G-F))**2-sp.exp(-G))
    ck('correct half exponent passes',good==0)
    ck('doubled exponent rejected',bad.subs({F:0,G:1})!=0)
    ck('reversed Gibbs sign rejected',sp.simplify(sp.exp(F)*sp.exp(-(G-F))-sp.exp(G)).subs({F:0,G:1})!=0)
    a,b,u,v=sp.symbols('a b u v',real=True)
    pair=-a*(b-a)-b*(a-b)
    ck('two directed labels need half',sp.expand(pair-(b-a)**2)==0 and sp.expand(pair-2*(b-a)**2)!=0)
    x=primary.state(2,1,1)
    for family in ('PH','LK'):
        plus=primary.move(x,1,family,1); minus=primary.move(x,1,family,-1)
        ck('K2 coincident distinct labels:'+family,plus==minus)
        d=primary.energy(2,plus[0])-primary.energy(2,x)
        ck('K2 dedup loses nonzero rate:'+family,plus[1]>0 and isinstance(d,Q))
    for donor,recv in ((0,0),(4,4),(1,3),(4,0)):
        y=primary.state(2,1,0); y[0][0]=Q(donor,2); y[0][1]=Q(recv,2)
        ans=primary.move(y,1,'TR',1)
        allowed=donor>=1 and recv<4
        ck(f'exact radial endpoint:{donor}:{recv}',(ans is not None)==allowed)
        if ans:
            ck(f'endpoint inverse:{donor}:{recv}',primary.move(ans[0],1,'TR',-1)==(y,ans[1]))
    for seed in (0,1):
        y=primary.state(2,1,seed)
        ck(f'only one AP admissible:{seed}',sum(primary.move(y,1,'AP',s) is not None for s in (-1,1))==1)
    # Same physical amplitude is represented by doubled occupation at j+1;
    # one retained root label then has half the old amplitude step.
    y=primary.state(2,1,0); y[0][0]=Q(1); y[0][1]=Q(0)
    z1=primary.move(y,1,'TR',1)[0]; z2=primary.move(y,2,'TR',1)[0]
    ck('label retention is not radial intertwining',z1[0]!=z2[0])
    ck('radial Lipschitz distance exactly two steps',sum(abs(a-b) for a,b in zip(y[0],z1[0]))==1)
    # Negative control: TV -> 0 alone cannot pass an unbounded function.
    for k in (2,8,32):
        weight=Q(1,k); observable=Q(k)
        ck(f'weak-only tail failure:{k}',weight*observable==1 and weight*observable**2==k)
        ck(f'second-moment tail control:{k}',weight*observable<=weight*observable**2/k)
    # Root rate support stabilizes; full F does NOT stabilize with volume.
    for family in ('PH','LK','AP','TR'):
        for seed in (0,1):
            x=primary.state(2,1,seed); y=primary.state(4,1,seed)
            for sign in (-1,1):
                a=primary.move(x,1,family,sign); b=primary.move(y,1,family,sign)
                if a is None: continue
                ck(f'local delta stable:{family}:{seed}:{sign}',primary.energy(2,a[0])-primary.energy(2,x)==primary.energy(4,b[0])-primary.energy(4,y))
    ck('global energy not discarded',primary.energy(2,primary.state(2,1,1))!=primary.energy(4,primary.state(4,1,1)))
    independent=(ROOT/'codes/foundations/pah_omc018_generator_independent.py').read_text()
    ck('independent no primary import','import pah_omc018_generator' not in independent and 'import pah_omc017' not in independent)
    data={'status':'PASS','lane':'hostile','checks':checks,'code_version':__version__,
          'code_sha256':sha(Path(__file__)),'scope':'Executed mutation/endpoint/tail controls; closure and temporal process construction explicitly not certified.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-018 HOSTILE: PASS ({len(checks)} checks)')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,default=OUT)
    run(p.parse_args().output)
