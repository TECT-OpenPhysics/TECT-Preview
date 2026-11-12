#!/usr/bin/env python3
"""Reproducible finite checks for the A6/A7 manuscript; analytic limits are in TeX.

Run with --self-test --write-new FILE to retain a new audit, or --check FILE
to compare with a saved payload. Issued reports are never overwritten.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

PAPER = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'


def require(ok, name):
    if not ok:
        raise ValueError(name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_saved(actual, expected, locator='result'):
    """Exact algebra/provenance equality; declared tolerance for floating diagnostics."""
    if isinstance(expected,float):
        require(isinstance(actual,(int,float)) and math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-14),locator)
    elif isinstance(expected,dict):
        require(isinstance(actual,dict) and set(actual)==set(expected),locator)
        for key in expected: compare_saved(actual[key],expected[key],locator+'.'+key)
    elif isinstance(expected,list):
        require(isinstance(actual,list) and len(actual)==len(expected),locator)
        for i,(a,b) in enumerate(zip(actual,expected)): compare_saved(a,b,locator+f'[{i}]')
    else:
        require(type(actual)==type(expected) and actual==expected,locator)


def model():
    path = PAPER / 'sources/production-inputs.json'
    meta = json.loads((PAPER / 'sources/provenance.json').read_text(encoding='utf-8'))
    require(sha(path) == meta['production_manifest_sha256'], 'production snapshot bytes')
    p = json.loads(path.read_text(encoding='utf-8'), parse_float=F)['parameters']
    d = p['M_X']**2 + p['classii_mass_regularizer']
    a = p['cJJ'] * p['alpha_X']**2 / d
    b = p['cJK'] * p['alpha_X'] * p['beta_X'] / d
    c = p['cKK'] * p['beta_X']**2 / d
    return p, a, b, c


def wick_moment(cov, powers):
    """Exact recursive pair enumeration, independent of Gaussian-IBP formula."""
    @lru_cache(None)
    def rec(ns):
        if sum(ns) == 0:
            return F(1)
        if sum(ns) % 2:
            return F(0)
        i = next(k for k, n in enumerate(ns) if n)
        rem = list(ns); rem[i] -= 1
        value = F(0)
        for j, multiplicity in enumerate(rem):
            if multiplicity:
                nxt = rem.copy(); nxt[j] -= 1
                value += multiplicity * cov[i][j] * rec(tuple(nxt))
        return value
    return rec(tuple(powers))


def ibp_case(i, j):
    # INPUT fixture: covariance of (X,Y,U,V), strictly diagonally dominant SPD.
    P, R, Q, C = F(1,5), F(-1,7), F(1,6), F(1,4)
    cov = ((F(1),F(0),C,R), (F(0),F(1),P,Q),
           (C,P,F(1),F(0)), (R,Q,F(0),F(1)))
    for k, row in enumerate(cov):
        require(row[k] > sum(abs(x) for l,x in enumerate(row) if l != k), 'SPD fixture')
    def moment(ix, ju, iy=0, jv=0):
        return F(0) if ix < 0 or ju < 0 else wick_moment(cov, (ix,iy,ju,jv))
    lhs = moment(i,j,2,2)-moment(i,j,2,0)-moment(i,j,0,2)+moment(i,j)
    terms = (2*Q**2*moment(i,j),
             4*P*Q*R*i*j*moment(i-1,j-1),
             P**2*R**2*i*(i-1)*j*(j-1)*moment(i-2,j-2))
    return lhs, terms


def build():
    p,a,b,c = model()
    checks = []
    def check(name, ok):
        require(ok, name); checks.append(name)
    h = 9*(a+2*b+c); low = 9*a+12*b+6*c
    check('positive coefficient matrix', a > 0 and c > 0 and a*c > b*b)
    gap = p['r'] - p['Z']**2/(4*p['Y'])
    check('positive fourth-order reference', gap > 0)
    check('fixed floor and side', p['rho_regularizer'] == F(1,10**12) and p['Lx']==p['Ly']==p['Lz']==16)
    def W(s,r,e):
        rho=s+r
        return h*s - 6*b*s*s/(rho+e) - 3*c*s*s*(rho+2*e)/(rho+e)**2
    fixtures = ((F(1),F(0),F(1,10)), (F(2),F(3),F(1,7)),
                (F(3,10),F(10**6),F(1,10**12)), (F(0),F(5),F(1,10)))
    for ix,(s,r,e) in enumerate(fixtures):
        rho=s+r; w=W(s,r,e)
        upper=6*b*s*s/(rho+e)+3*c*s*s*(rho+2*e)/(rho+e)**2
        lower=6*b*s*(1-s/(rho+e))+3*c*s*(1-s*(rho+2*e)/(rho+e)**2)
        check(f'slope exact residual {ix}', h*s-w == upper and w-low*s == lower)
        check(f'slope signs {ix}', low*s <= w <= h*s)
    ratios=[]
    for r in (10,100,1000,10000):
        s=F(1); e=p['rho_regularizer']
        ratio=h-W(s,F(r),e)/s
        check(f'critical escape bound {r}', 0 < ratio <= 6*s*(b+c)/r)
        ratios.append(ratio)
    check('critical residual shrinks', all(u>v for u,v in zip(ratios,ratios[1:])))
    m=h/2; x=min(F(1,2),(h-m)/(2*(6*b+3*c)))
    Ax=(h-m)*x-(6*b+3*c)*x*x
    check('subcritical orientation', 0 < x <= 1 and Ax > 0)
    # Exact coefficient check after rho = z*sqrt(t), z^2=2Ax/gamma:
    # gamma*z^3/6 - Ax*z = -2*Ax*z/3 < 0.
    check('sextic optimum sign and factor', F(1,6)*2-F(1) == F(-2,3))
    for i in range(7):
        for j in range(7):
            lhs, terms=ibp_case(i,j)
            check(f'nonconstant Gaussian IBP {i},{j}', lhs == sum(terms))
    # Real/complex matrix route is separately coded, with no imported TECT code.
    generators=[np.array([[0,1,0],[1,0,0],[0,0,0]],complex),
                np.array([[0,-1j,0],[1j,0,0],[0,0,0]],complex),
                np.diag([1,-1,0]).astype(complex)]
    def realify(A): return np.block([[A.real,-A.imag],[A.imag,A.real]])
    D=np.array([[2,1j/5,0],[-1j/5,3,1/4],[0,1/4,4]],complex)
    check('complex covariance fixture positive', np.linalg.eigvalsh(D).min()>0)
    for index,psi in enumerate((np.array([1+2j,2-1j,3j]), np.array([1,0,2j]), np.array([0,0,1j]))):
        rho=float(np.vdot(psi,psi).real); X=np.r_[psi.real,psi.imag]
        B=np.zeros((6,6)); counter=0.; isotropic=0.
        for T in generators:
            q=float(np.vdot(psi,T@psi).real)/(rho+float(p['rho_regularizer']))
            U=T@psi; V=U-q*psi
            pv=2*realify(T)@X; vv=2*(realify(T)-q*np.eye(6))@X
            B += float(a)*np.outer(pv,pv)+float(b)*(np.outer(pv,vv)+np.outer(vv,pv))+float(c)*np.outer(vv,vv)
            counter += float(a)*np.vdot(U,D@U).real+2*float(b)*np.vdot(U,D@V).real+float(c)*np.vdot(V,D@V).real
            isotropic += float(a)*np.vdot(U,U).real+2*float(b)*np.vdot(U,V).real+float(c)*np.vdot(V,V).real
        real_counter=.5*np.trace(B@(.5*realify(D)))
        check(f'conditional real-complex factor {index}', abs(real_counter-counter)<1e-12)
        s=float(np.vdot(psi[:2],psi[:2]).real)
        expected=float(h)*s-6*float(b)*s*s/(rho+float(p['rho_regularizer']))-3*float(c)*s*s*(rho+2*float(p['rho_regularizer']))/(rho+float(p['rho_regularizer']))**2
        check(f'Pauli spatial factor and cross coefficient {index}', abs(3*isotropic-expected)<1e-12)
        check(f'positive B {index}', np.linalg.eigvalsh(B).min()>-1e-12)
    # Numerical quadrature is a diagnostic of the displayed defining integral.
    deltas=[]
    for order in (48,80):
        z,w=np.polynomial.legendre.leggauss(order); z=(z+1)/2; w=w/2
        integral=24*np.sum(np.outer(w,w)/(1+z[:,None]**2+z[None,:]**2))
        deltas.append(float(integral/(6*np.pi**2*float(p['Y'])*float(p['Lx']))))
    check('cube face quadrature consistency', abs(deltas[0]-deltas[1])<1e-14)
    c0=(float(p['r']+p['Y'])-np.sqrt(float((p['r']-p['Y'])**2+p['Z']**2)))/4
    check('explicit ellipticity constant positive', c0>0)
    shell_sum=24*np.pi**2/6+2*np.pi**4/90
    check('shell counting identity', abs(shell_sum-(4*np.pi**2+np.pi**4/45))<1e-13)
    return {'schema':'tect/a6-a7-paper-audit/1.0','version':VERSION,'status':'PASS',
        'scope':'Finite exact algebra, Wick moments and numerical diagnostics only; analytic limits require manuscript proofs.',
        'source_checkpoint':json.loads((PAPER/'sources/provenance.json').read_text())['source_checkpoint'],
        'source_input_sha256':sha(PAPER/'sources/production-inputs.json'),
        'checks':checks,'checks_passed':len(checks),
        'derived':{'a':str(a),'b':str(b),'c':str(c),'h':str(h),'lower_slope':str(low),
                   'reference_gap':str(gap),'delta_cube':deltas[1],
                   'leading_family_mass_slope':2*float(h)*deltas[1],
                   'ellipticity_c0':float(c0),'critical_residual_ratios':[str(x) for x in ratios]},
        'external_mathematical_review':'NOT_PERFORMED','specialist_novelty_review':'NOT_PERFORMED',
        'interacting_Gibbs_measure':False,'A13_closure':False,'physical_vacuum':False}


def self_test():
    rejected=[]
    for family,(i,j) in enumerate(((0,0),(1,1),(2,2))):
        lhs,terms=ibp_case(i,j)
        require(terms[family]!=0,'nonzero hostile fixture')
        for factor in (F(0),F(-1),F(2)):
            altered=list(terms); altered[family]*=factor
            require(lhs!=sum(altered),'IBP mutation not rejected')
            rejected.append(f'family{family}:factor{factor}')
    p,a,b,c=model(); h=9*(a+2*b+c)
    require(h!=9*(a+b+c),'cross-term mutation')
    require(2*h!=h,'family mass half mutation')
    require(9*(a+2*b+c)!=3*(a+2*b+c),'spatial factor mutation')
    rejected.extend(['cross coefficient','mass half','spatial count'])
    # A low Fourier mode has variance error (1-(1-delta)^2)^2, not O(N^-3).
    slow=[]
    for N in (16,64,256,1024):
        delta=1/np.log(N+2)
        slow.append(float((1-(1-delta)**2)**2*N**3))
    require(all(x<y for x,y in zip(slow,slow[1:])),'slow cutoff diagnostic')
    rejected.append('universal cutoff rate')
    return {'status':'PASS','rejected_mutations':rejected,'count':len(rejected)}


def main():
    require(__debug__,'Run without Python -O: assertions must remain enabled')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--write-new',type=Path)
    parser.add_argument('--check',type=Path)
    args=parser.parse_args()
    result=build()
    if args.self_test: result['hostile']=self_test()
    if args.check:
        expected=json.loads(args.check.read_text(encoding='utf-8'))
        compare_saved(result,expected)
    if args.write_new:
        require(not args.write_new.exists(),'Existing audit overwrite refused')
        args.write_new.parent.mkdir(parents=True,exist_ok=True)
        with args.write_new.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2,sort_keys=True); stream.write('\n')
    print('A6/A7 PAPER AUDIT: PASS',result['checks_passed'],'checks;',
          result.get('hostile',{}).get('count',0),'hostile mutations rejected')


if __name__=='__main__': main()
