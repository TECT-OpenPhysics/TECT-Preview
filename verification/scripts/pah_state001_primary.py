#!/usr/bin/env python3
"""Exact fixed-regulator PAH display-fibre diagnostic; no simulated limit.

All model inputs come from the preregistration. Full source signed roots,
including duplicate K=2 labels, are retained. Output is exact SymPy algebra.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import sympy as S

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/'strategy/pa-hyp/PAH-STATE-001-prereg-v1.json'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-pah-state001/primary.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for p, h in spec['source_hashes'].items():
        assert sha(ROOT/p) == h, p
    raw = spec['inputs']
    p = {k:S.Rational(v) for k,v in raw.items() if not isinstance(v,list)}
    source = ROOT/'codes/foundations/pah_v2_root_enumerator.py'
    modspec = importlib.util.spec_from_file_location('state001_roots', source)
    E = importlib.util.module_from_spec(modspec)
    sys.modules[modspec.name] = E
    modspec.loader.exec_module(E)
    W = 2**int(p['h']+p['N']+1)
    # This certificate is deliberately restricted to the pinned minimal box.
    assert W == 2 and p['r'] == 0
    coords = sorted(product(range(W),repeat=2), key=lambda z:z[0]+2*z[1])
    edges = tuple((i,coords.index(z)) for i,(x,y) in enumerate(coords)
                  for z in ((x+1,y),(x,y+1)) if z in coords)
    K = int(S.prod(S.prime(i+1) for i in range(int(p['r'])+1)))
    Ms, Mp = 2**int(p['r']), int(p['m0']*4**p['r'])
    Q, R = int(p['q0']*2**p['r']), p['R0']*2**p['r']
    reg = E.Regulator(len(coords), edges, K, Ms, Mp, Q)
    assert K == 2
    def display(x):
        s = tuple(p['epsilon']+j*(1-p['epsilon'])/Ms for j in x.aperture)
        psi = tuple(R*ell/Mp*(-1)**n for ell,n in zip(x.occupation,x.phase))
        U = tuple((-1)**u for u in x.link)
        return s,psi,U
    def energy(x):
        s,psi,U = display(x)
        val = sum(p['lambda_s']*(a-1)**2/2+p['m2']*b**2/2+
                  p['lambda_4']*b**4/4+p['eta_6']*b**6/6+p['g']*a**2*b**2/2
                  for a,b in zip(s,psi))
        J = [2/(s[v]+s[w]) for v,w in edges]
        val += sum(p['kappa_s']*(s[v]-s[w])**2/2+
                   p['kappa_D']*J[i]*(psi[w]-U[i]*psi[v])**2/2
                   for i,(v,w) in enumerate(edges))
        # K=2 inverse equals itself; one source square face, all four edges.
        val += p['kappa_g']*sum(J)/len(J)*(1-S.prod(U))
        return S.simplify(val)
    def mobility(x,y,r):
        sx,sy = display(x)[0],display(y)[0]
        if r.family == 'PH': return sx[r.cell]**p['nu']
        if r.family == 'AP': return (sx[r.cell]*sy[r.cell])**(p['nu']/2)
        v,w = edges[r.cell]
        return (sx[v]*sx[w])**(p['nu']/2)
    def f(x): return display(x)[1][0]**2
    def row(x):
        rows = []
        for r,y in E.incidences(reg,x):
            assert E.apply_move(reg,y,r.inverse()) == x
            m = mobility(x,y,r)
            assert m == mobility(y,x,r.inverse())
            delta = energy(y)-energy(x)
            c = m*S.exp(-p['beta']*delta/2)
            # Exact unnormalised detailed balance, with every root retained.
            assert S.simplify(S.exp(-p['beta']*energy(x))*c-
                S.exp(-p['beta']*energy(y))*m*S.exp(p['beta']*delta/2)) == 0
            rows.append((r,y,delta,S.simplify(c*(f(y)-f(x)))))
        return rows
    pair = [E.State(tuple(raw['j']),tuple(raw['ell']),tuple(n),tuple(raw['u']))
            for n in raw['phase_pair']]
    assert pair[0] != pair[1] and display(pair[0]) == display(pair[1])
    assert all(E.valid_state(reg,x) for x in pair)
    rows = [row(x) for x in pair]
    actions = [S.simplify(sum(t[3] for t in r)) for r in rows]
    # Independent paper-derived test oracles, never used to compute the rows.
    assert [energy(x) for x in pair] == [S.Rational(10,3)]*2
    assert actions == [2*S.exp(S.Rational(1,2)),2*S.exp(-S.Rational(1,2))]
    assert [Counter(t[0].family for t in r) for r in rows] == [Counter(PH=8,TR=4,LK=8,AP=4)]*2
    assert all(t[0].family == 'TR' for r in rows for t in r if t[3] != 0)
    # Independent full-functional regression oracles on cancelled AP roots.
    for cell,expected in ((0,S.Rational(17,24)),(1,S.Rational(1,3))):
        ap=next(t for t in rows[0] if t[0]==E.Move('AP',cell,-1))
        assert ap[2]==expected and ap[3]==0
        assert mobility(pair[0],ap[1],ap[0])==S.sqrt(2)/2
    fibre=[]
    for a,b in product(range(K),repeat=2):
        x=E.State(pair[0].aperture,pair[0].occupation,(a,0,0,b),pair[0].link)
        assert display(x)==display(pair[0]) and energy(x)==energy(pair[0])
        fibre.append(S.simplify(sum(t[3] for t in row(x))))
    mean=S.simplify(sum(fibre)/len(fibre))
    var=S.simplify(sum((v-mean)**2 for v in fibre)/len(fibre))
    oracle=(S.exp(S.Rational(1,2))-S.exp(-S.Rational(1,2)))**2
    assert S.simplify(S.expand((var-oracle).rewrite(S.exp)))==0
    assert S.exp(S.Rational(1,2)) > S.exp(-S.Rational(1,2))
    gauge_checks=0
    for g in product(range(K),repeat=reg.vertices):
        for x in pair:
            gx=E.State(x.aperture,x.occupation,tuple((n+a)%K for n,a in zip(x.phase,g)),
                tuple((u+g[w]-g[v])%K for u,(v,w) in zip(x.link,edges)))
            assert f(gx)==f(x) and energy(gx)==energy(x)
            assert S.simplify(sum(t[3] for t in row(gx))-sum(t[3] for t in row(x)))==0
            gauge_checks+=1
    return {'schema':'tect/pah-state001-primary/1.0','status':'PASS_EXACT_FINITE_WITNESS',
        'source_hashes':spec['source_hashes'],'prereg_sha256':sha(SPEC),'script_sha256':sha(Path(__file__)),
        'geometry':{'W':W,'vertices':coords,'edges':edges,'O':[0],'C':[1]},
        'regulator':{'K':K,'Ms':Ms,'Mpsi':Mp,'Q':Q,'Rmax':str(R)},
        'energies':[str(energy(x)) for x in pair],'generator_values':list(map(str,actions)),
        'nonzero_rows':[[{'family':t[0].family,'edge':t[0].cell,'sign':t[0].sign,
            'delta_energy':str(t[2]),'contribution':str(t[3])} for t in r if t[3]!=0] for r in rows],
        'valid_root_counts':[dict(Counter(t[0].family for t in r)) for r in rows],
        'fibre_size':len(fibre),'conditional_variance':str(var),'gauge_checks':gauge_checks,
        'boundary':'One admitted finite regulator only. No physical identity or uniform-limit bound.'}

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=run()
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        assert not OUT.exists(),'Issued run immutable'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(encoded,encoding='utf-8',newline='\n')
    elif args.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==json.loads(encoded)
    print('STATE-001 PRIMARY: PASS exact root/energy/gauge/fibre checks')

if __name__=='__main__': main()
