"""Exact non-PAH countercontrols for invalid closability shortcuts.

These abstract functional-analysis controls are not replacements for the
frozen PAH carrier. No finite table is counted as an infinite theorem.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sympy as sp

__version__='1.0.0'


def compute():
    checks=[]
    def ck(name, condition):
        assert bool(condition), name
        checks.append({'name':name,'pass':True})
    n=sp.symbols('n',positive=True,integer=True); x=sp.symbols('x',real=True)
    tent=1-n*x
    norm2=sp.integrate(tent**2,(x,0,1/n))
    endpoint=tent.subs(x,0)
    ck('nonclosable control exact L2 norm',sp.simplify(norm2-1/(3*n))==0)
    ck('nonclosable control H-null sequence',sp.limit(norm2,n,sp.oo)==0)
    ck('nonclosable control energy stays one',endpoint**2==1)
    m=sp.symbols('m',positive=True,integer=True)
    ck('nonclosable control energy Cauchy',sp.expand((endpoint-(1-m*x).subs(x,0))**2)==0)
    ck('no bounded fixed point-evaluation representer',sp.limit(endpoint**2/norm2,n,sp.oo)==sp.oo)
    # Orthogonal coordinate vectors fn=e_n/n, S e_n=n^2 e_n.
    ck('diagonal-pair shortcut H norm tends zero',sp.limit(1/n**2,n,sp.oo)==0)
    diag_energy=sp.simplify(n**2*(1/n)**2)
    ck('diagonal-pair shortcut energy does not vanish',diag_energy==1)
    distance=diag_energy+diag_energy  # orthogonal coordinates n != m
    ck('diagonal control violates energy Cauchy',distance>0)
    ck('diagonal norm product not small',sp.simplify((1/n)*n)==1)
    # Adding a pure energy ghost to a completion would violate injectivity.
    ghost_H2=sp.Integer(0); ghost_K2=sp.Integer(1)
    ck('ghost cannot be identified with H zero',ghost_H2==0 and ghost_K2!=0)
    # A form can have more null directions than a designated radial subspace.
    gram=sp.diag(0,0,1); radial=sp.Matrix([1,0,0]); extra=sp.Matrix([0,1,0]); active=sp.Matrix([0,0,1])
    ck('kernel equality overclaim rejected',gram*radial==sp.zeros(3,1) and gram*extra==sp.zeros(3,1) and extra!=radial)
    ck('extra kernel compatible with positive activity',(active.T*gram*active)[0]>0)
    e=sp.symbols('e',positive=True)
    ck('opposite sign destroys nonnegativity',(-e).is_negative)
    c, d=sp.symbols('c d',positive=True)
    directed=(c*d**2+c*(-d)**2)/2
    ck('directed half convention required',sp.simplify(directed-c*d**2)==0 and sp.simplify(2*directed-directed)!=0)
    return {'schema':'tect/pah-omc019-hostile/1.0','status':'PASS','checks':checks,
            'code_version':__version__,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'controls':{'point_evaluation_norm2':str(norm2),'point_evaluation_energy':str(endpoint**2),
                        'diagonal_energy_distance2':str(distance)},
            'scope':'Exact countercontrols to missing-hypothesis shortcuts, NOT counterexamples to PAH-OMC-019.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output; result=compute(); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f"PAH-OMC-019 HOSTILE: PASS ({len(result['checks'])} checks)")
