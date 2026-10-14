#!/usr/bin/env python3
"""RD-001 independent replay: no primary, earlier PAH or enumerator imports.
Finite floating controls corroborate, not replace, the universal analytic proof.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/'strategy/pa-hyp/PAH-v2-RD-001-prereg-v1.json'
SPEC_SHA = '86021a47783189e6e29f86cd24d14e0e1eaf8cfa2d943f6372099912a5571528'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-v2-rd001/independent.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_checks():
    assert sha(SPEC) == SPEC_SHA
    pins = json.loads(SPEC.read_text(encoding='utf-8'))['source_pins']
    for name, expected in pins.items():
        assert sha(ROOT/name) == expected, name
    return pins

def symbolic_checks():
    # INPUT Gibbs/rate conventions; exact beta*F_x,beta*F_y coefficients.
    half = Q(1,2)
    assert (-1+half,-half) == (-half,-1+half) == (-half,-half)
    assert (-1-half,half) != (-half,-half)
    # TEST geometry and family coefficients; universal formula is in note.
    V,E = 4,4
    roots = ((2*V,(1,1,0,0),Q(1)),(2*E,(0,0,1,0),Q(2)),
             (2*E,(0,1,0,0),Q(1)),(2*V,(0,0,0,1),Q(1)))
    poly = {}
    for count,power,factor in roots:
        squared = tuple(2*x for x in power)
        poly[squared] = poly.get(squared,0)+half*count*factor**2
    expected = {(2,2,0,0):Q(V),(0,0,2,0):Q(4*E),
                (0,2,0,0):Q(E),(0,0,0,2):Q(V)}
    assert poly == expected
    assert {k:2*v for k,v in poly.items()} != expected
    return {'flux_exponents':[str(-half)]*2,
            'dirichlet_coefficients':{str(k):str(v) for k,v in sorted(poly.items())},
            'wrong_sign_and_missing_half_controls':'REJECTED'}

def character_checks():
    reports=[]
    for W in (2,4,8):  # TEST INPUTS only.
        edges=[]
        for y in range(W):
            for x in range(W):
                if x+1<W: edges.append(((x,y),(x+1,y)))
                if y+1<W: edges.append(((x,y),(x,y+1)))
        lookup={edge:i for i,edge in enumerate(edges)}
        faces=[]
        for y in range(W-1):
            for x in range(W-1):
                vector=[0]*len(edges)
                word=((((x,y),(x+1,y)),1),(((x+1,y),(x+1,y+1)),1),
                      (((x,y+1),(x+1,y+1)),-1),(((x,y),(x,y+1)),-1))
                for edge,sign in word: vector[lookup[edge]]=sign
                faces.append(vector)
        for K in (2,6,30):
            zeros=sum(all((s*x+t*y)%K==0 for x,y in zip(a,b))
                      for a in faces for b in faces for s in (-1,1) for t in (-1,1))
            variance=Q(zeros,4*len(faces)**2)
            assert variance == Q(1,len(faces)*(1 if K==2 else 2))
            reports.append({'W':W,'K':K,'faces':len(faces),'variance':str(variance)})
    return reports

def finite_generator_check():
    # TEST INPUTS: exact admitted W=2,r=0 FULL tuple counting space.
    # Negative polynomial coefficients test that no F>=0 premise is used.
    eps,beta,nu=.5,.125,1.
    ls,m2,l4,eta,g=.125,-1.,-1.,1.,.25
    ks,kd,kg=.125,.125,.125
    edges=((0,1),(0,2),(1,3),(2,3))
    V,E,P,A,Ms=4,len(edges),1,1.,1
    degrees=[sum(v in edge for edge in edges) for v in range(V)]
    states=list(itertools.product(range(2**V),range(V),range(2**V),range(2**E)))
    lookup={state:i for i,state in enumerate(states)}
    assert len(states)==V*2**(2*V+E)
    def energy(x):
        j,o,n,u=x
        s=[eps+(1-eps)*((j>>v)&1) for v in range(V)]
        z=[(-1.)**((n>>v)&1) if v==o else 0. for v in range(V)]
        links=[(-1.)**((u>>e)&1) for e in range(E)]
        val=sum(ls*(s[v]-1)**2/2+m2*z[v]**2/2+l4*z[v]**4/4+
                eta*z[v]**6/6+g*s[v]**2*z[v]**2/2 for v in range(V))
        J=[2/(s[v]+s[w]) for v,w in edges]
        val+=sum(ks*(s[v]-s[w])**2/2+
                 kd*J[e]*(z[w]-links[e]*z[v])**2/2 for e,(v,w) in enumerate(edges))
        return val+kg*sum(J)/E*(1-math.prod(links))
    def moves(x):
        j,o,n,u=x
        s=[eps+(1-eps)*((j>>v)&1) for v in range(V)]
        for v in range(V):
            for sign in (-1,1):
                yield ('PH',v,sign),(j,o,n^(1<<v),u),s[v]**nu
        for e,(v,w) in enumerate(edges):
            for sign in (-1,1):
                tail,head=(v,w) if sign==1 else (w,v)
                if o==tail:
                    yield ('TR',e,sign),(j,head,n,u),(s[v]*s[w])**(nu/2)
        for e,(v,w) in enumerate(edges):
            for sign in (-1,1):
                yield ('LK',e,sign),(j,o,n,u^(1<<e)),(s[v]*s[w])**(nu/2)
        for v in range(V):
            for sign in (-1,1):
                nextj=((j>>v)&1)+sign
                if 0<=nextj<=Ms:
                    sn=eps+(1-eps)*nextj
                    yield ('AP',v,sign),(j^(1<<v),o,n,u),(s[v]*sn)**(nu/2)
    energies=list(map(energy,states))
    Z=sum(math.exp(-beta*val) for val in energies)
    pi=[math.exp(-beta*val)/Z for val in energies]
    f=[(-1.)**x[3].bit_count() for x in states]
    label_mass,rows={},[]
    count,D,flux_error=0,0.,0.
    for i,x in enumerate(states):
        row=[]
        for label,y,mobility in moves(x):
            k=lookup[y]
            c=mobility*math.exp(-beta*(energies[k]-energies[i])/2)
            inverse=(label[0],label[1],-label[2])
            reverse={lab:(target,mob) for lab,target,mob in moves(y)}
            assert reverse[inverse][0]==x
            assert abs(reverse[inverse][1]-mobility)<1e-15
            flux=pi[i]*c
            error=abs(flux-mobility*math.sqrt(pi[i]*pi[k]))
            flux_error=max(flux_error,error)
            assert error<1e-15
            label_mass[label]=label_mass.get(label,0.)+flux
            D+=.5*flux*(f[k]-f[i])**2
            row.append((k,c))
            count+=1
        rows.append(row)
    expected=len(states)*(2*V+2*E+V)+(len(states)//V)*sum(degrees)
    assert count==expected
    assert max(label_mass.values())<=1+1e-12
    assert D<=E*4+1e-12
    # Independent OSCILLATION cap for this fixture, not note's absolute B.
    Bosc=(V*ls*(1-eps)**2/2+abs(m2)*A**2/2+abs(l4)*A**4/4+
          eta*A**6/6+g*A**2/2+ks*E*(1-eps)**2/2+
          kd*max(degrees)*A**2/eps+2*kg*P/eps)
    assert max(energies)-min(energies)<=Bosc+1e-12
    density_floor=math.exp(-beta*Bosc)
    assert min(pi)*len(pi)>=density_floor-1e-12
    mean=sum(w*value for w,value in zip(pi,f))
    variance=sum(w*(value-mean)**2 for w,value in zip(pi,f))
    assert variance>=density_floor/(2*P)-1e-12
    # Floating uniformization corroboration, not interval certification.
    t=.05
    exits=[sum(c for _,c in row) for row in rows]
    rate=max(exits)
    lam=rate*t
    term=list(f)
    weight=math.exp(-lam)
    out=[weight*value for value in term]
    terms=0
    while weight>1e-17 or terms<5:
        terms+=1
        term=[(1-exits[i]/rate)*term[i]+sum(c*term[k]/rate for k,c in rows[i])
              for i in range(len(states))]
        weight*=lam/terms
        for i,value in enumerate(term): out[i]+=weight*value
        assert terms<100
    error_sq=sum(w*(value-initial)**2 for w,value,initial in zip(pi,out,f))
    assert error_sq<=t*D+1e-12
    show=lambda value:format(value,'.12g')
    return {'status':'PASS_FLOATING_FINITE_CORROBORATION_ONLY',
            'states':len(states),'valid_signed_incidences':count,
            'max_flux_error':show(flux_error),
            'maximum_signed_label_expected_rate':show(max(label_mass.values())),
            'dirichlet':show(D),'plaquette_variance':show(variance),
            'uniform_variance_floor':show(density_floor/(2*P)),
            'fixture_oscillation_bound':show(Bosc),
            'semigroup_L2_error_squared':show(error_sq),'time_times_dirichlet':show(t*D),
            'uniformization_terms':terms,'scope':'One full r=0 fixture; not an all-r numerical proof.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    data={'schema':'tect/pah-v2-rd001-independent/1.0','status':'PASS',
          'source_pins':source_checks(),'prereg_sha256':sha(SPEC),
          'script_sha256':sha(Path(__file__)),
          'exact_algebra_controls':symbolic_checks(),'exact_character_controls':character_checks(),
          'full_generator_fixture':finite_generator_check(),
          'analytic_route':'Per-label Gibbs midpoint flux <=1; jump-square Dirichlet bound; finite spectral inequality.',
          'independence':'No primary, previous PAH implementation or enumerator imports; in-session, not external-person review.',
          'proof_boundary':'Written all-index analytic proof carries quantifiers; finite controls corroborate only.',
          'non_claims':['No R-573/R-574 reversal','No model/state/rate/time change',
                        'No infinite volume, continuum, physical Pre-A, spacetime, QFT, gravity or TOE']}
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==data
    else:
        assert not OUT.exists(),'Issued receipt immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('RD-001 INDEPENDENT: PASS (finite controls corroborate analytic proof only)')

if __name__=='__main__':
    main()
