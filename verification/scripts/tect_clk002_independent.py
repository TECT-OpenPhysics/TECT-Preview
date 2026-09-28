#!/usr/bin/env python3
"""CLK-002 v1.0.0 independent exact-rational and inverse-image audit.

No import of the primary implementation. TEST_ONLY fixtures are deliberately
not atomic constants or observed data. The general proof is in the certificate.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRE=ROOT/'strategy/clock/TECT-CLK-002-prereg-v1.json'
PIN='eed93e6aa01b4bacc780bba0a24f53ccf7c6b7f6daab394ae20e54afa270c92f'
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-28-tect-clk002/independent.json'


def audit():
    assert hashlib.sha256(PRE.read_bytes()).hexdigest()==PIN
    pre=json.loads(PRE.read_text(encoding='utf-8'))
    for path,digest in pre['protected_sources'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    # Rational input fixtures, never measured or fitted physical coefficients.
    cases=[(F(1,3),F(1,7),F(2,9),F(1,5),F(-3,8)),
           (F(-1,3),F(1,7),F(2,9),F(1,5),F(-3,8)),
           (F(0),F(1,7),F(2,9),F(1,5),F(-3,8)),
           (F(2,5),F(0),F(1,11),F(2,7),F(1,9))]
    results=[]
    for coupling,a,b,source,k in cases:
        # Independent force construction: tensor plus scalar-exchange parts.
        force_a=1+(coupling*a)*(coupling*source)
        force_b=1+(coupling*b)*(coupling*source)
        mean=(force_a+force_b)/2
        eta=(force_a-force_b)/mean
        scalar_clock_gradient=(coupling*k)*(coupling*source)
        z=-scalar_clock_gradient/mean
        assert (a-b)*z+k*eta==0
        C=-z/k
        recovered=C/(source*(1-(a+b)*C/2))
        assert recovered==coupling**2
        assert C>=0 and 1-(a+b)*C/2>0
        results.append({'coupling':str(coupling),'z':str(z),'eta':str(eta),'recovered_square':str(recovered)})
    assert results[0]['z']==results[1]['z'] and results[0]['eta']==results[1]['eta']
    # Necessary null is not sufficient: negative inferred squared coupling.
    q,k=F(1,5),F(2,3)
    z,eta=k,-q
    assert q*z+k*eta==0 and -z/k<0
    return {'schema':'tect/clk002-independent/1.0','status':'PASS_CONDITIONAL_AUDIT',
            'prereg_sha256':PIN,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'test_only_cases':results,'case_count':len(results),
            'checks':{'opposite_coupling_signs_indistinguishable':True,
                      'null_without_image_condition_insufficient':True,
                      'primary_import_absent':True},
            'general_proof':'Monotone map u -> S*u/(1+Q*S*u) has derivative S/(1+Q*S*u)^2>0 for S>0,Q>=0,u>=0; range C>=0 and Q*C<1, inverse as displayed. Scalar sign is not identifiable.',
            'boundary':'Exact rational fixtures audit an independent implementation; they do not establish the parameterized physical reduction or an experimental prediction.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); value=audit()
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8'))==value
    else:
        assert not OUT.exists(),'Issued run is immutable'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('CLK-002 INDEPENDENT: PASS',value['case_count'],'TEST_ONLY exact rational cases plus inverse-image checks')
