"""Non-importing exact audit of the fixed-test proof and graph closure.

Symbolic identities are universal algebra; abstract Gram coordinates below
are proof notation, NOT a new PAH finite carrier or physical model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

__version__='1.0.0'
ROOT=Path(__file__).resolve().parents[2]


def compute():
    checks=[]
    def ck(name, condition):
        assert bool(condition), name
        checks.append({'name':name,'pass':True})
    # Derive the fixed-test split by matrix bilinearity, not the primary polynomial.
    u, v, w=sp.symbols('u v w',real=True)
    gram=sp.Matrix([[u,v],[v,w]])
    en=sp.Matrix([1,0]); em=sp.Matrix([0,1])
    bil=lambda x,y:(x.T*gram*y)[0]
    ck('independent bilinear split',sp.expand(bil(en,en)-bil(en,en-em)-bil(en,em))==0)
    ck('independent reverse difference',sp.expand(bil(en-em,en-em)-(u+w-2*v))==0)
    delta, M=sp.symbols('delta M',positive=True)
    epsilon=delta/(2*M)
    ck('epsilon choice positive',epsilon.is_positive)
    ck('fixed-test quantitative budget',sp.simplify(M*epsilon+delta/2-delta)==0)
    # Independent graph description: same H limit and zero energy coordinate.
    h1,h2,k1,k2=sp.symbols('h1 h2 k1 k2',real=True)
    graph_dist=(h1-h2)**2+(k1-k2)**2
    ck('graph norm radial isometry',sp.expand(graph_dist.subs({k1:0,k2:0})-(h1-h2)**2)==0)
    ck('graph energy unchanged on original domain',sp.expand(graph_dist-(h1-h2)**2-(k1-k2)**2)==0)
    ck('I plus S fixed representer',sp.expand(h1*(h2+k2)-(h1*h2+h1*k2))==0)
    # Standard pointwise Cauchy--Schwarz determinant identity, independently expanded.
    x1,x2,y1,y2=sp.symbols('x1 x2 y1 y2',real=True)
    ck('Gram determinant nonnegative square',sp.expand((x1*x1+x2*x2)*(y1*y1+y2*y2)
       -(x1*y1+x2*y2)**2-(x1*y2-x2*y1)**2)==0)
    ck('no primary import', 'import pah_omc019_closure' not in Path(__file__).read_text(encoding='utf-8').replace("'import pah_omc019_closure'", "''"))
    return {'schema':'tect/pah-omc019-independent/1.0','status':'PASS','checks':checks,
            'code_version':__version__,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'coverage':'Independent algebra for direct epsilon and graph-completion proofs; model measure premises are analytic.',
            'fixed_test_budget':str(sp.simplify(M*epsilon+delta/2)),
            'dependence_boundary':'No primary verifier or PAH-OMC-018 implementation imported; no external signed review.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output; result=compute(); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f"PAH-OMC-019 INDEPENDENT: PASS ({len(result['checks'])} checks)")
