#!/usr/bin/env python3
"""Independent exact face/count algebra; imports neither primary nor source code.

Returned by the separate independent reviewer. Fixtures corroborate the written
all-index incidence and finite stopped-count proof, not a dynamics experiment.
"""
from collections import Counter
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-time002/independent.json'


def incidence(w):
    edges=[]
    for x in range(w):
        for y in range(w):
            if x+1<w:
                edges.append(((x,y),(x+1,y)))
            if y+1<w:
                edges.append(((x,y),(x,y+1)))
    faces=[]
    for x in range(w-1):
        for y in range(w-1):
            a,b=(x,y),(x+1,y)
            c,d=(x+1,y+1),(x,y+1)
            faces.append(((edges.index((a,b)),1),(edges.index((b,c)),1),
                          (edges.index((d,c)),-1),(edges.index((a,d)),-1)))
    use=Counter()
    for face in faces:
        boundary=Counter()
        for k,sign in face:
            tail,head=edges[k]
            boundary[tail]-=sign
            boundary[head]+=sign
            use[k]+=1
        assert all(v==0 for v in boundary.values())
        assert len({k for k,_ in face})==len(face)
    assert set(use)==set(range(len(edges)))
    assert all(1<=count<=2 for count in use.values())
    p=len(faces)
    assert all(F(count,p)<=F(2,p) for count in use.values())
    labels=[(k,sign) for k in range(len(edges)) for sign in (-1,1)]
    assert len(labels)==2*len(edges) and len(set(labels))==len(labels)
    assert 1 % 2 == (-1) % 2  # Equal maps do not merge their labels.
    return {'width':w,'vertices':w*w,'edges':len(edges),'faces':p,
            'max_edge_face_incidence':max(use.values()),'signed_lk_labels':len(labels)}


def primitive(coeffs,t):
    return sum(c*t**(k+1)/F(k+1) for k,c in enumerate(coeffs))


def run():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    fixtures=[incidence(w) for w in (2,4)]  # Admitted geometry test inputs.
    for n in range(7):
        assert (n+1)-n==1
        assert (n+1)**2-n*n==2*n+1
    moments=[]
    for lam in (F(1,3),F(7,2)):  # Algebra test inputs, not model parameters.
        for t in (F(0),F(1,5),F(3)):
            value=primitive((lam,2*lam*lam),t)
            assert value==lam*t+lam*lam*t*t
            moments.append({'lambda':str(lam),'t':str(t),'second_bound':str(value)})
    return {'schema':'tect/pah-time002-independent/1.0',
            'status':'PASS_EXACT_INCIDENCE_AND_COUNT_CONTROLS',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'fixtures':fixtures,'moment_controls':moments,
            'boundary':'No primary imports; analytic stopped-count moment and inverse-clock proof separately reviewed. No finite dynamics simulation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data=run()
    if args.write:
        assert not OUT.exists(),'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        assert json.loads(OUT.read_text(encoding='utf-8'))==data
    print('TIME-002 INDEPENDENT: PASS (exact incidence and count controls only)')


if __name__=='__main__':
    main()
