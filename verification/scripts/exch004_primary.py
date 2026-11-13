#!/usr/bin/env python3
"""Conditional calibrated-readout algebra and frozen-source audit, not physics PASS.

Reference matrices are explicitly labelled test oracles, not fitted experimental
effects. Missing native effects/covariance stay missing; no data are digitized.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-13-exch004'
CONTRACT=ROOT/'strategy/physical-candidates/TECT-EXCH-004-contract-v1.json'
PIN='4117b174f9b8abafbee4947053a4c6f5579f994851a27d1bf0e316050cb59daf'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path);args=parser.parse_args()
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha(CONTRACT)==PIN
    c=json.loads(CONTRACT.read_text())
    for path,digest in c['preserved_hashes'].items():assert sha(ROOT/path)==digest,path
    old=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-001-contract-v1.json').read_text())
    for path,digest in old['source_hashes'].items():assert sha(ROOT/path)==digest,path
    if args.source_cache:
        for item in c['sources']:
            path=args.source_cache/item['cache_file']
            assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
    checks={}
    def ck(name,b):
        checks[name]=bool(b);assert checks[name],name
    x,y,z,e0,ex,ey,ez=s.symbols('x y z e0 ex ey ez',real=True)
    rho=s.Matrix([[1+z,x-s.I*y],[x+s.I*y,1-z]])/2
    effect=s.Matrix([[e0+ez,ex-s.I*ey],[ex+s.I*ey,e0-ez]])
    signal=s.simplify(s.trace(rho*effect))
    ck('calibrated_effect_linear_signal',signal==e0+ex*x+ey*y+ez*z)
    pair=s.Matrix([[0,0],[s.sqrt(2),0]])
    coherence=s.simplify(s.trace(rho*pair))
    ck('pair_quadrature_convention',coherence==(x-s.I*y)/s.sqrt(2))
    # Centered/rescaled Pauli expectations (2m-1), not raw probability-effect
    # vectors: missing-y and sufficient-y maps are reference test oracles only.
    A=s.Matrix([[1,0,0],[0,0,1]])
    target=s.Matrix([[0,1,0]])
    ck('xz_cannot_identify_y',A.rank()<A.col_join(target).rank())
    ck('nullspace_certificate',any((target*v)[0]!=0 for v in A.nullspace()))
    B=s.Matrix([[0,1,0]])
    ck('one_axis_can_identify_target',B.rank()==B.col_join(target).rank())
    ck('full_tomography_not_required',B.rank()<3)
    alpha,delta,phi=s.symbols('alpha delta phi',real=True)
    rotated=s.Matrix([[s.cos(alpha),-s.sin(alpha)],[s.sin(alpha),s.cos(alpha)]])*s.Matrix([x,y])
    m=x*s.cos(phi+delta)+y*s.sin(phi+delta)
    other=rotated[0]*s.cos(phi+delta+alpha)+rotated[1]*s.sin(phi+delta+alpha)
    ck('unknown_analyzer_phase_ambiguity_fixed_g',s.trigsimp(s.expand_trig(other-m))==0)
    ck('fixed_g_target_generally_changes',s.simplify(rotated[1].subs({x:0,y:1,alpha:s.pi})+1)==0)
    b1,b2,v1,v2,c12=s.symbols('b1 b2 v1 v2 c12',real=True)
    beta=s.Matrix([b1,b2]);Sigma=s.Matrix([[v1,c12],[c12,v2]])
    variance=(beta.T*Sigma*beta)[0]
    ck('full_covariance_retained',s.expand(variance-b1*b1*v1-b2*b2*v2-2*b1*b2*c12)==0)
    vh,c1h,c2h=s.symbols('vh c1h c2h',real=True)
    residual_vector=s.Matrix([-b1,-b2,1])
    joint=s.Matrix([[v1,c12,c1h],[c12,v2,c2h],[c1h,c2h,vh]])
    residual_var=(residual_vector.T*joint*residual_vector)[0]
    ck('holdout_cross_covariance_retained',s.expand(residual_var-vh-variance+2*(b1*c1h+b2*c2h))==0)
    # Conditional probability after selection is nonlinear; no loss deletion.
    def survivor_probability(t):return (s.Rational(1,2)*t)/(s.Rational(1,2)*t+1-t)
    ck('survivor_postselection_not_linear',survivor_probability(s.Rational(1,2))!=(survivor_probability(0)+survivor_probability(1))/2)
    a=json.loads((ROOT/'strategy/physical-candidates/TECT-EXCH-004-assessment-v1.json').read_text())
    ck('physical_hold_enforced',a['overall_verdict']=='HOLD_FOR_EVIDENCE' and a['claim_bearing'] is False)
    ck('no_new_result_or_no_go',a['new_result_id'] is None and a['new_negative_id'] is None)
    ck('holdout_not_invented',any(r['status']=='NOT_EXECUTED_MISSING_INPUT' for r in a['measurement_crosswalk']))
    ck('one_protocol_two_sources',len(c['sources'])==2 and c['budget']['protocols']==1)
    out={'status':'PASS_CONDITIONAL_DIAGNOSTICS_PHYSICAL_HOLD','checks':checks,
      'script_sha256':sha(Path(__file__)),'contract_sha256':sha(CONTRACT),
      'assessment_sha256':sha(ROOT/'strategy/physical-candidates/TECT-EXCH-004-assessment-v1.json'),
      'source_pins':{a['id']:a['sha256'] for a in c['sources']},
      'scope':'Reference algebra/provenance only; no calibrated native effect, experimental covariance or numerical holdout residual.'}
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'primary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH004 PRIMARY: PASS',len(checks),'conditional/source checks; physical HOLD')


if __name__=='__main__':main()
