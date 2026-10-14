#!/usr/bin/env python3
"""RD-001 source-pinned symbolic bounds and exact finite implementation checks.

The written proof, not these fixtures, carries every-r/h/N/F quantifiers.
No physical time, new state, fitted rate, or CRT-domain substitution is used.
Version 1.0.0; first issued 2026-10-14.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'strategy/pa-hyp/PAH-v2-RD-001-prereg-v1.json'
SPEC_HASH = '86021a47783189e6e29f86cd24d14e0e1eaf8cfa2d943f6372099912a5571528'
ENUM = ROOT / 'codes/foundations/pah_v2_root_enumerator.py'
ENUM_HASH = '37044e1e7bc274985823d095a21cd6759dbe9e4c5be303b69464d02846291cc2'
OUT = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-v2-rd001/primary.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_checks():
    assert sha(SPEC) == SPEC_HASH
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for path, expected in spec['source_pins'].items():
        assert sha(ROOT/path) == expected, path
    assert sha(ENUM) == ENUM_HASH
    parent = json.loads((ROOT/'strategy/pa-hyp/PAH-001-v1.json').read_text(encoding='utf-8'))
    assert parent['dynamics']['generator'] == '(L_rho f)(x)=sum_r m_r(x) exp[-beta(F_rho(r x)-F_rho(x))/2] [f(r x)-f(x)]'
    return spec


def geometry(width):
    vertices = [(x,y) for y in range(width) for x in range(width)]
    lookup = {v:i for i,v in enumerate(vertices)}
    edges = []
    for x,y in vertices:
        for w in ((x+1,y),(x,y+1)):
            if w in lookup:
                edges.append((lookup[x,y],lookup[w]))
    ei = {edge:i for i,edge in enumerate(edges)}
    faces = []
    for y in range(width-1):
        for x in range(width-1):
            a,b,c,d = [lookup[v] for v in ((x,y),(x+1,y),(x+1,y+1),(x,y+1))]
            face = [0]*len(edges)
            for edge,sign in (((a,b),1),((b,c),1),((d,c),-1),((a,d),-1)):
                face[ei[edge]] = sign
            faces.append(face)
    return vertices,edges,faces


def symbolic_bounds():
    r = s.symbols('r', integer=True, nonnegative=True)
    V,E,P,R0,q0,m0,K = s.symbols('V E P R0 q0 m0 K', positive=True)
    eps,beta,ls,eta,ks,kD,kg,g = s.symbols('epsilon beta lambda_s eta6 kappa_s kappa_D kappa_g g', positive=True)
    m2,l4 = s.symbols('m2 lambda4', real=True)
    A = s.cancel((R0*2**r)/(m0*4**r)*(q0*2**r))
    assert s.simplify(A-R0*q0/m0) == 0
    A = s.simplify(A)
    z = s.symbols('z', positive=True)  # exact symbolic alias z=2^(-r)
    tau = R0/m0*z
    aperture_step = (1-eps)*z
    counts = {'PH':2*V,'TR':2*E,'LK':2*E,'AP':2*V}
    steps = {'PH':2*s.pi*A/K,'TR':2*tau,'LK':2*s.pi/K,'AP':aperture_step}
    jump_sum = s.expand(sum(counts[k]*steps[k] for k in counts))
    target = (2*V*(1-eps)+4*E*R0/m0)*z+4*s.pi*(V*A+E)/K
    assert s.simplify(jump_sum-target) == 0
    # Every term here comes from the pinned F formula and triangle bounds.
    onsite = ls*(1-eps)**2/2+s.Abs(m2)*A**2/2+s.Abs(l4)*A**4/4+eta*A**6/6+g*A**2/2
    B = V*onsite+ks*E*(1-eps)**2/2+2*kD*E*A**2/eps+2*kg*P/eps
    assert s.diff(B,m2) != 0  # negative mass must not be silently dropped
    assert s.diff(B,l4) != 0
    # |F|<=B implies -beta*DeltaF/2<=beta*B, not beta*B/2.
    assert s.simplify(-beta*((-B)-B)/2-beta*B) == 0
    return {'amplitude':str(A),'step_alias':'z=2^(-r)','energy_absolute_bound':str(B),
            'all_root_jump_sum':str(s.factor(target)),
            'rate_cap':'exp(beta*B)',
            'generator_bound':'Lip(F)*exp(beta*B)*all_root_jump_sum',
            'uniform_time_bound':'T*Lip(F)*exp(beta*B)*all_root_jump_sum',
            'variance_lower':'exp(-2*beta*B)/(2*P) for r>=1'}


def finite_root_checks():
    spec = importlib.util.spec_from_file_location('rd001_source_enumerator', ENUM)
    enum = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = enum
    spec.loader.exec_module(enum)
    vertices,edges,_ = geometry(2)  # original admitted h=N=0 graph; test input
    counts = Counter()
    invalid = 0
    for r in (0,1):  # implementation fixtures only, never limit evidence
        K = int(s.prod(list(s.primerange(1,10))[:r+1]))
        ms,mp,Q = 2**r,4**r,2**r
        reg = enum.Regulator(len(vertices),tuple(edges),K,ms,mp,Q)
        tau = s.Rational(2**r,mp)
        for eps in (s.Rational(1,2),s.Integer(1)):
            def display(x):
                aperture = [eps+(1-eps)*s.Rational(j,ms) for j in x.aperture]
                matter = [tau*l*s.exp(2*s.pi*s.I*n/K).expand(complex=True) for l,n in zip(x.occupation,x.phase)]
                link = [s.exp(2*s.pi*s.I*u/K).expand(complex=True) for u in x.link]
                return aperture+matter+link
            for occupied in (0,len(vertices)-1):
                occupation = tuple(Q if i==occupied else 0 for i in range(len(vertices)))
                x = enum.State(tuple(ms if i%2 else 0 for i in range(len(vertices))),occupation,
                               (K-1,)*len(vertices),(K-1,)*len(edges))
                assert enum.valid_state(reg,x)
                for move in enum.roots(reg):
                    y = enum.apply_move(reg,x,move)
                    if y is None:
                        invalid += 1
                        continue
                    assert enum.apply_move(reg,y,move.inverse()) == x
                    assert sum(y.occupation) == Q
                    distance = s.simplify(sum(s.Abs(a-b) for a,b in zip(display(x),display(y))))
                    chord = 2*s.sin(s.pi/K)
                    cap = {'PH':chord,'TR':2*tau,'LK':chord,'AP':(1-eps)/ms}[move.family]
                    assert s.simplify(cap-distance).is_nonnegative, (move,distance,cap)
                    counts[move.family] += 1
    assert set(counts) == {'PH','TR','LK','AP'} and invalid > 0
    return {'valid_root_checks':dict(counts),'omitted_invalid_checks':invalid,
            'fixture_scope':'r=0,1; h=N=0; epsilon=1/2,1; endpoints and phase wrap; not exhaustive source-state coverage'}


def fourier_checks():
    # E_gamma exp(2*pi*i a.u/K)=1 iff every coefficient is 0 mod K.
    rows = []
    for width in (2,4):  # source G_(h,N), with h+N=0,1; tooling inputs
        _,edges,faces = geometry(width)
        for K in (2,6,30):  # first approved primorial cutoffs, not a proof by table
            for face in faces:
                assert any(a%K for a in face)
            second = s.Integer(0)
            cross = 0
            for i,face in enumerate(faces):
                for j,other in enumerate(faces):
                    expectation = sum(s.Rational(1,4) for sign in (-1,1) for sign2 in (-1,1)
                                      if all((sign*a+sign2*b)%K==0 for a,b in zip(face,other)))
                    oracle = (s.Integer(1) if K==2 else s.Rational(1,2)) if i==j else 0
                    assert expectation == oracle  # independent Fourier test oracle
                    if i!=j:
                        cross += 1
                    second += expectation
            variance = s.factor(second/len(faces)**2)
            assert variance >= s.Rational(1,2*len(faces))
            rows.append({'width':width,'K':K,'faces':len(faces),'edges':len(edges),
                         'off_diagonal_zero_checks':cross,'uniform_variance':str(variance)})
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    spec=source_checks()
    data={'schema':'tect/pah-v2-rd001-primary/1.0','status':'PASS',
          'script_sha256':sha(Path(__file__)),'prereg_sha256':sha(SPEC),
          'source_pins':spec['source_pins'],'enumerator_sha256':sha(ENUM),
          'symbolic':symbolic_bounds(),'root_fixtures':finite_root_checks(),
          'fourier_fixtures':fourier_checks(),
          'scope':'Exact symbolic and finite implementation checks supporting the written all-cutoff proof; no finite table proves the universal limit.'}
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==data
    else:
        assert not OUT.exists(),'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('RD-001 PRIMARY: PASS (source pins, symbolic bounds, all-family root fixtures, exact Fourier covariance)')


if __name__=='__main__':
    main()
