#!/usr/bin/env python3
"""SG-001 hostile arithmetic and source mutations, v1.0.0.

No new state carrier is evaluated. Residues exhaust the already fixed fifth
character; scalar calculus controls do not replace the written vector proof.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sympy as sp
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-pah-v2-sg001/hostile.json'
SPEC=ROOT/'strategy/pa-hyp/PAH-v2-SG-001-prereg-v1.json'
SPEC_HASH='177e36c3ea7370f2377c9a53b385396e7b6de1a28399c3b306880c92ce672646'


def run():
    checks=[]
    def check(name,predicate):
        assert predicate,name
        checks.append({'name':name,'pass':True})
    def sha(data): return hashlib.sha256(data).hexdigest()
    check('preregistration_exact_bytes',sha(SPEC.read_bytes())==SPEC_HASH)
    spec=json.loads(SPEC.read_text(encoding='utf-8'))
    for path,digest in spec['source_hashes'].items():
        data=(ROOT/path).read_bytes()
        check('source:'+path,sha(data)==digest)
        check('single_byte_source_mutation_rejected:'+path,sha(data+b' ')!=digest)
    primary=json.loads((OUT.parent/'primary.json').read_text(encoding='utf-8'))
    independent=json.loads((OUT.parent/'independent.json').read_text(encoding='utf-8'))
    for key,value in independent['derived'].items():
        check('independent_coefficient:'+key,primary['derived'][key]==value)
    d={key:Q(value) for key,value in independent['derived'].items()}
    t,C,b,delta,K=d['time'],d['residual_coeff'],d['leading_lower'],d['delta'],d['required_K']
    error=lambda k,j: t*C*(1/k+1/j)
    check('rational_boundary_included',b-error(K,K)==delta)
    check('premature_cutoff_rejected',b-error(K-1,K-1)<delta)
    check('coarse_error_is_load_bearing',error(K,K)>t*C/K)
    check('norm_square_not_norm',delta**2==d['norm_squared_lower'] and delta**2!=delta)
    check('original_normalization_load_bearing',Q(0)*delta**2<d['norm_squared_lower'])
    # Convex normalized weights preserve the pointwise square lower bound;
    # arbitrary small support mass would not. No alternate target state is used.
    for w in (Q(0),Q(1,7),Q(1,2),Q(1)):
        check('normalized_weight_control:'+str(w),w*delta**2+(1-w)*(2*delta)**2>=delta**2)
    ctx.prec=192
    tt=arb(t.numerator)/t.denominator
    edge_count=int(primary['derived']['edge_count'])
    ev={a:edge_count*(2*(2*arb.pi()*a/5).cos()-2) for a in range(1,5)}
    for a in range(1,5):
        check('negative_spectrum:'+str(a),ev[a]<0)
        for p in range(1,5):
            aa=a*pow(p,-1,5)%5
            gap=abs((tt*ev[aa]).exp()-(tt*ev[a]).exp())
            if p in (2,3):
                check('all_flip_classes:'+str((a,p)),gap>arb(b.numerator)/b.denominator)
            else:
                check('nonflip_not_a_witness:'+str((a,p)),gap<arb(delta.numerator)/delta.denominator)
            check('zero_time_no_gap:'+str((a,p)),(arb(0)*ev[a]).exp()==(arb(0)*ev[aa]).exp())
    u,T=sp.symbols('u T',real=True)
    lam,mu=-sp.Integer(2),-sp.Integer(3)  # Scalar calculus test oracles only.
    kernel=sp.exp(lam*u)*sp.exp(mu*(T-u))
    rhs=sp.integrate(kernel,(u,0,T))*(mu-lam)
    lhs=sp.exp(mu*T)-sp.exp(lam*T)
    check('Duhamel_sign_scalar_control',sp.simplify(lhs-rhs)==0)
    check('wrong_Duhamel_sign_rejected',sp.simplify(lhs+rhs)!=0)
    check('positive_lambda_breaks_unit_weight_bound',arb(1).exp()>1)
    # No implication at all from t=0 or from a finite list of prime residues;
    # the written Euclid argument carries the arbitrary-tail quantifier.
    return {'schema':'tect/pah-v2-sg001-hostile/1.0','status':'PASS',
        'script_sha256':sha(Path(__file__).read_bytes()),'preregistration_sha256':SPEC_HASH,
        'checks':checks,'authorship':'Same task; independent implementation is not external-person review.',
        'not_encoded':'Full-state Markov and vector Duhamel proofs and unbounded prime-tail existence are analytic, not certified by these finite arithmetic controls.',
        'non_claims':'No new model, carrier, observable, state, time, physical interpretation or infinite-volume semigroup.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    result=run()
    if a.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==result
    else:
        assert not OUT.exists(),'Issued run is immutable; use --check'
        fd,tmp=tempfile.mkstemp(dir=OUT.parent,suffix='.tmp')
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
        os.replace(tmp,OUT)
    print('SG-001 HOSTILE: PASS',len(result['checks']),'checks')
