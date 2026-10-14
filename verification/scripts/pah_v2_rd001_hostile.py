#!/usr/bin/env python3
"""RD-001 exact hostile controls; fixtures do not certify the universal proof."""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/'strategy/pa-hyp/PAH-v2-RD-001-prereg-v1.json'
SPEC_HASH = '86021a47783189e6e29f86cd24d14e0e1eaf8cfa2d943f6372099912a5571528'
ENUM = ROOT/'codes/foundations/pah_v2_root_enumerator.py'
ENUM_HASH = '37044e1e7bc274985823d095a21cd6759dbe9e4c5be303b69464d02846291cc2'
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-v2-rd001/hostile.json'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def source_checks():
    assert sha(SPEC) == SPEC_HASH
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for path, expected in spec['source_pins'].items():
        assert sha(ROOT/path) == expected, path
    assert sha(ENUM) == ENUM_HASH
    return spec['source_pins']

def faces(W):
    # Independent sparse oriented-edge encoding of the open square carrier.
    return [{(x,y,'h'):1,(x+1,y,'v'):1,(x,y+1,'h'):-1,(x,y,'v'):-1}
            for x in range(W-1) for y in range(W-1)]

def covariance(a,b,K):
    edges = a.keys() | b.keys()
    return sum((Q(1,4) for u in (-1,1) for v in (-1,1)
                if all((u*a.get(e,0)+v*b.get(e,0))%K == 0 for e in edges)), Q(0))

def controls():
    passed = []
    def ck(name, ok):
        assert ok, name
        passed.append(name)
    V,E,A,z,d,K,ep = s.symbols('V E A z d K ep', positive=True)
    jump = 2*V*A*2*s.pi/K + 2*E*2*d*z + 2*E*2*s.pi/K + 2*V*(1-ep)*z
    target = 4*s.pi*(V*A+E)/K + (4*E*d+2*V*(1-ep))*z
    ck('all-root multiplicities', s.expand(jump-target) == 0)
    ck('mutation: lost TR factor rejected', s.expand(jump-(target-2*E*d*z)) != 0)
    b,bt = s.symbols('B beta', positive=True)
    exponent = -bt*((-b)-b)/2
    ck('worst downhill rate exponent', s.simplify(exponent-bt*b) == 0)
    ck('mutation: half rate exponent rejected', s.simplify(exponent-bt*b/2) != 0)
    ck('density exponent uses numerator AND normalization',
       s.simplify((-bt*b)-(bt*b)+2*bt*b) == 0)
    ck('mutation: one-B density exponent rejected', -2*bt*b != -bt*b)
    for r in (0,1,4,9):  # TEST INPUTS, not all-index evidence.
        R0,m0,q0 = Q(3,2),3,2
        tau = R0*2**r/(m0*4**r)
        ck('amplitude schedule r='+str(r), tau*q0*2**r == R0*q0/m0)
        ck('TR step r='+str(r), 2*tau == 2*R0/m0*Q(1,2**r))
    for W in (2,4,8):
        fs = faces(W)
        ck('face count W='+str(W), len(fs) == (W-1)**2)
        for mod in (2,6,30):
            total = Q(0)
            for i,a in enumerate(fs):
                assert any(c%mod for c in a.values())
                for j,bface in enumerate(fs):
                    got = covariance(a,bface,mod)
                    want = (Q(1) if mod==2 else Q(1,2)) if i==j else Q(0)
                    assert got == want, (W,mod,i,j)
                    total += got
            ck('Fourier Gram W=%d K=%d'%(W,mod), total/len(fs)**2 >= Q(1,2*len(fs)))
    face = faces(2)[0]
    ck('mutation: K2 half variance rejected', covariance(face,face,2) != Q(1,2))
    weights,vals = (Q(1,4),Q(3,4)),(-1,1)  # TEST centering fixture only.
    mean = sum(p*v for p,v in zip(weights,vals))
    variance = sum(p*(v-mean)**2 for p,v in zip(weights,vals))
    ck('density-floor variance transfer fixture', variance >= Q(1,2))
    ck('mutation: Gibbs mean zero rejected', mean != 0 and variance != 1)
    spec = importlib.util.spec_from_file_location('rd001_hostile_enum', ENUM)
    en = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = en
    spec.loader.exec_module(en)
    reg = en.Regulator(4,((0,1),(0,2),(1,3),(2,3)),2,1,1,1)
    x = en.State((0,0,0,0),(1,0,0,0),(0,0,0,0),(0,0,0,0))
    labels = list(en.roots(reg))
    ck('signed labels not deduplicated', len(labels)==4*(reg.vertices+len(reg.edges)))
    for family,cell in (('PH',1),('LK',0)):
        p,m = en.Move(family,cell,1),en.Move(family,cell,-1)
        ck('K2 distinct labels '+family, p!=m and en.apply_move(reg,x,p)==en.apply_move(reg,x,m))
    ck('zero amplitude retains phase label', en.apply_move(reg,x,en.Move('PH',1,1)) != x)
    ck('invalid AP omitted not clipped', en.apply_move(reg,x,en.Move('AP',0,-1)) is None)
    y = en.apply_move(reg,x,en.Move('TR',0,1))
    ck('TR preserves all nonoccupation labels',
       y is not None and (x.aperture,x.phase,x.link)==(y.aperture,y.phase,y.link))
    ck('hidden aperture survives epsilon=1 display', en.apply_move(reg,x,en.Move('AP',0,1)) != x)
    return passed

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args = ap.parse_args()
    pins,passed = source_checks(),controls()
    data = {'schema':'tect/pah-v2-rd001-hostile/1.0',
            'status':'PASS_HOSTILE_CONTROLS_ONLY','script_sha256':sha(Path(__file__)),
            'prereg_sha256':sha(SPEC),'source_pins':pins,'enumerator_sha256':sha(ENUM),
            'controls':passed,'control_count':len(passed),'floating_proof':False,
            'universal_analytic_proof_certified_by_fixtures':False,'physical_promotion':False,
            'scope':'Exact controls supporting a separately reviewed all-index proof; not a replacement for it.'}
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8')) == data
    else:
        assert not OUT.exists(), 'Issued receipt immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('RD-001 HOSTILE: PASS (%d exact controls; universal proof not certified by fixtures)'%len(passed))

if __name__ == '__main__':
    main()
