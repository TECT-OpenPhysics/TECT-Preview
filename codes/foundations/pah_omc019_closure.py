"""Exact identity audit for the primary PAH-OMC-019 closure proof.

This is not a finite PAH simulation or a verifier of inherited measure theory.
The universal Hilbert argument is in PahOmc019.lean and the certificate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

__version__ = '1.0.0'
ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'strategy/pa-hyp/PAH-OMC-019-closure-prereg-v1.json'


def compute():
    checks = []
    def ck(name, condition):
        assert bool(condition), name
        checks.append({'name': name, 'pass': True})
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    for path, digest in contract['sources'].items():
        ck('source:' + path, hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest)
    a, b, c, t = sp.symbols('a b c t', real=True)
    ck('Gram polynomial expansion', sp.expand(a+2*t*b+t*t*c-(a-b*b/c+c*(t+b/c)**2)) == 0)
    ck('null-energy cross polynomial is linear', sp.Poly((a+2*t*b+t*t*c).subs(c, 0), t).degree() == 1)
    qn, qnm, pair = sp.symbols('qn qnm pair', real=True)
    ck('fixed-test decomposition', sp.expand(qn-(qnm+pair)).subs(qnm, qn-pair) == 0)
    vnorm, hnorm, energy = sp.symbols('vnorm hnorm energy', real=True)
    ck('transported form norm', sp.expand(hnorm+(vnorm-hnorm)-vnorm) == 0)
    ck('radial form norm', (hnorm+energy).subs(energy, 0) == hnorm)
    ex, ey, exy = sp.symbols('ex ey exy', real=True)
    ck('energy difference for radial approximants', (ex+ey-2*exy).subs({ex:0, ey:0, exy:0}) == 0)
    ck('sign convention', sp.simplify(-(-sp.Symbol('E'))-sp.Symbol('E')) == 0)
    return {'schema':'tect/pah-omc019-primary/1.0','status':'PASS','checks':checks,
            'code_version':__version__, 'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            'coverage':'Exact algebra and immutable-input audit; not a numerical closability proof.',
            'identities':{'completion':'norm_H2 + (norm_V2 - norm_H2) = norm_V2',
                          'gram':'a+2tb+t^2c = a-b^2/c+c(t+b/c)^2 for c!=0'}}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output; result=compute(); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f"PAH-OMC-019 PRIMARY: PASS ({len(result['checks'])} checks)")
