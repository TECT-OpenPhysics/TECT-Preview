"""Non-importing PAH-OMC-017 reconstruction from vertex-face dictionaries.

Uses expanded signed quadratic edges, not primary squared-edge functions.
Rational fixtures are independent implementation checks, not a limit proof.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as R
import hashlib
import json
from pathlib import Path

__version__='1.0.0'
ROOT=next(x for x in Path(__file__).resolve().parents if (x/'GOVERNANCE.md').exists())
PREREG='strategy/pa-hyp/PAH-OMC-017-cauchy-prereg-v1.json'
PIN='249bf12f71b4869e566925b8c011291ec74ef2fc4f5df2faeeafc4050f04fdff'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc017-cauchy/independent.json'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def run(output):
    checks=[]
    def check(name,ok):
        assert bool(ok),name
        checks.append({'name':name,'pass':True})
    c=json.loads((ROOT/PREREG).read_text())
    check('source_hash',sha(ROOT/PREREG)==PIN)
    for file,pin in c['sources'].items(): check('parent:'+file,sha(ROOT/file)==pin)
    base=json.loads((ROOT/'strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json').read_text())
    p={k:R(str(v)) for k,v in base['scope']['fixed_parameters'].items()}
    fixtures=[]
    for n in (2,3,5):
        count=2*(n+2)
        faces=[]
        for i in range(n):
            a,b,c0,d=2*i,2*i+1,2*i+2,2*i+3
            faces.extend([[a,c0,d],[a,d,b]])
        faces.append([2*n,2*n+2,2*n+3,2*n+1])
        for seed in range(12):
            amp=[R((3*(v//2)+v%2+seed)%7,3) for v in range(count)]
            ap=[R(1+(v//2+v%2+seed)%2,2) for v in range(count)]
            phase=[(-1)**((v//2+2*(v%2)+seed//2)%2) for v in range(count)]
            links={}
            for col in range(n+2): links[(2*col,2*col+1)]=(-1)**((col+seed)%2)
            for col in range(n+1):
                for row in range(2): links[(2*col+row,2*col+row+2)]=(-1)**((col+row+seed//3)%2)
            for col in range(n): links[(2*col,2*col+3)]=(-1)**((col+seed//5)%2)
            def edgepair(a,b): return tuple(sorted((a,b)))
            def stiff(a,b): return 2/(ap[a]+ap[b])
            value=R(0)
            for v in range(count):
                t,s=amp[v],ap[v]
                value+=p['lambda_s']*(s*s-2*s+1)/2+(p['m2']+p['g']*s*s)*t*t/2+p['lambda_4']*t**4/4+p['eta_6']*t**6/6
            for (a,b),link in links.items():
                signed=phase[a]*link*phase[b]
                value+=p['kappa_s']*(ap[a]**2+ap[b]**2-2*ap[a]*ap[b])/2
                value+=p['kappa_D']*stiff(a,b)*(amp[a]**2+amp[b]**2-2*signed*amp[a]*amp[b])/2
            for face in faces:
                es=list(zip(face,face[1:]+face[:1])); hol=1; coeff=R(0)
                for a,b in es: hol*=links[edgepair(a,b)]; coeff+=stiff(a,b)
                value+=p['kappa_g']*coeff*(1-hol)/len(face)
            check(f'finite_energy_positive_{n}_{seed}',value>=0)
            fixtures.append({'n':n,'seed':seed,'F':str(value)})
        check(f'face_edge_incidence_{n}',len(links)==4*n+4 and len(faces)==2*n+1 and all(len(f)==3 for f in faces[:-1]) and len(faces[-1])==4)
    # Derive conservative ranges component-by-component, not from primary.
    grid=[p['epsilon'],R(1)]
    jmax=max(2/(s+t) for s in grid for t in grid)
    vertex=max(p['lambda_s']*(s-1)**2/2 for s in grid)+p['m2']/2+p['lambda_4']/4+p['eta_6']/6+max(p['g']*s*s/2 for s in grid)
    edge=max(p['kappa_s']*(s-t)**2/2 for s in grid for t in grid)+p['kappa_D']*jmax*max((a-b)**2 for a in (-1,1) for b in (-1,1))/2
    face=p['kappa_g']*jmax*max(1-u for u in (-1,1))
    labels=len(grid)**2*int(p['K'])**3
    tail=next(2**k for k in range(10) if p['eta_6']*(2**k)**5>=6)
    col=vertex+vertex+edge; split=edge+edge+edge+face+face
    constants={k:str(v) for k,v in {'vertex_box':vertex,'edge_box':edge,'face_box':face,
        'column_box':col,'split_box':split,'kernel_box_cost':col+split,'column_labels':labels,
        'split_labels':int(p['K'])**3,'square_labels':int(p['K'])**2,
        'radius_lower_prefactor':labels*int(p['K'])**3,'scalar_tail_split':tail,
        'scalar_integral_bound':tail+1,'u_norm_squared_bound':labels*(tail+1)**2}.items()}
    # Exact rational corner controls for the universal ratio inequality.
    for t in (R(0),R(1,8),R(1,2)):
        for a in (-2,2):
            for sg in (-1,1):
                for se in (-1,1):
                    delta=sg*t; err=se*2*t
                    check(f'ratio_corner_{t}_{a}_{sg}_{se}',abs((a+err)/(1+delta)-a)<=4*2*t)
    check('source_values_positive',all(R(constants[k])>0 for k in constants))
    data={'lane':'independent','status':'PASS','checks':checks,'constants':constants,
        'fixtures':fixtures,'source_sha256':PIN,'code_sha256':sha(Path(__file__)),
        'code_version':__version__,'scope':'Independent face-vertex and expanded-edge reconstruction; no primary imports, numerical spectral approximation or external referee claim.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'PAH-OMC-017 INDEPENDENT: PASS ({len(checks)} checks)')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    run(parser.parse_args().output)
