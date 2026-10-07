"""Independent exact Fraction hostile tests for CLK008, no primary import.

All numerical inputs below are TEST_ONLY rational values, not atomic data.
This verifier tests normalization and degeneracies, not the general EFT proof.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-10-07-tect-clk008/independent.json'


def run():
    # TEST_ONLY inputs, deliberately not physical estimates.
    qE,d,a,b,o,k = F(1,2),F(2,3),F(1,5),F(1,7),F(1,11),F(7,3)
    t, mean, contrast = qE*d*d,(a+b)/2,a-b
    phase_coefficient, orbit_coefficient = 1+k*t,1+o*t
    alpha = phase_coefficient/orbit_coefficient-1
    aa,ab = 1+a*t,1+b*t
    eta = (aa-ab)/((aa+ab)/2)
    residual = lambda A,E: (contrast+(o-mean)*E)*A-(k-o)*E
    assert all(v>0 for v in (aa,ab,orbit_coefficient))
    assert residual(alpha,eta) == 0
    # Independent reproduction oracles from a separate reviewer; TEST_ONLY.
    assert alpha == F(148,303) and eta == F(4,327)
    mutations = {'bare_GM':k*t, 'sign_reversal':-alpha,
                 'wrong_mean_denominator':(k-o)*t/(1+mean*t)}
    values = {name:residual(value,eta) for name,value in mutations.items()}
    assert all(value != 0 for value in values.values())
    # Null is necessary, not sufficient: it also holds for forbidden d^2<0.
    neg_t = F(-1,10)
    neg_a = (1+k*neg_t)/(1+o*neg_t)-1
    neg_e = contrast*neg_t/(1+mean*neg_t)
    assert residual(neg_a,neg_e) == 0 and neg_t/qE < 0
    assert 1+o*neg_t > 0 and 1+mean*neg_t > 0
    assert (1+o*t)/(1+o*t)-1 == 0  # clock/orbit blind direction
    assert (aa-aa)/aa == 0  # no free-fall contrast
    assert qE*(-d)**2 == t  # coupling sign unidentifiable
    # Ground contribution is affine in phase only for constant frequency.
    times = [F(0),F(1),F(2)]
    linear = [F(3)*v+F(7) for v in times]
    quadratic = [v*v for v in times]
    assert linear[2]-2*linear[1]+linear[0] == 0
    assert quadratic[2]-2*quadratic[1]+quadratic[0] != 0
    return {'schema':'tect/clk008-independent/1.0','status':'PASS_TEST_ONLY',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'fixture':{'alpha':str(alpha),'eta':str(eta),'null':str(residual(alpha,eta))},
            'mutation_residuals':{key:str(v) for key,v in values.items()},
            'null_is_not_sufficient':True,'fixed_model_negative_square_rejected':True,
            'constant_ground_only':True,'sign_blind':True,
            'not_encoded':'No empirical Galileo response, calibration, material inputs or coverage.',
            'physical_promotion':False}


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args(); result=run()
    if args.check:
        assert json.loads(RUN.read_text(encoding='utf-8')) == result
    else:
        assert not RUN.exists(), 'Use --check for issued evidence'
        RUN.parent.mkdir(parents=True,exist_ok=True)
        RUN.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('CLK008 INDEPENDENT:',result['status'])
