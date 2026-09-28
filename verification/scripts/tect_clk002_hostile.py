#!/usr/bin/env python3
"""CLK-002 v1.0.0 adversarial algebra, scope and admission fixtures."""
import argparse
from fractions import Fraction as F
from pathlib import Path
import tect_clk002_primary as io


def audit():
    pre=io.inputs()
    # TEST_ONLY input values; no precision or empirical evidence is attributed.
    d,a,b,S,K=F(1,3),F(1,7),F(2,9),F(1,5),F(-3,8)
    Q=(a+b)/2; delta=a-b; D=1+Q*S*d*d; C=S*d*d/D
    z=-K*C; eta=delta*C
    checks={}
    def check(name,truth):
        assert truth,name
        checks[name]=True
    check('baseline_null',delta*z+K*eta==0)
    check('gradient_sign_flip_rejected',delta*(-z)+K*eta!=0)
    check('denominator_dropped_only_for_freefall_rejected',delta*z+K*(delta*S*d*d)!=0)
    other_mean=1+F(5,11)*S*d*d
    check('different_gravimeter_rejected',delta*(-K*S*d*d/other_mean)+K*eta!=0)
    other_source=F(3,5)
    other_C=other_source*d*d/(1+Q*other_source*d*d)
    check('different_source_rejected',delta*(-K*other_C)+K*eta!=0)
    check('clock_swap_consistent',delta*(-z)+(-K)*eta==0)
    check('mass_swap_consistent',(-delta)*z+K*(-eta)==0)
    check('zero_coupling_blind',S*F(0)/(1+Q*S*F(0))==0)
    check('zero_source_blind',F(0)*d*d/(1+Q*F(0)*d*d)==0)
    check('zero_clock_contrast_not_full_blindness',(-F(0)*C)==0 and eta!=0)
    check('zero_mass_contrast_not_full_blindness',F(0)*C==0 and z!=0)
    check('negative_C_outside_image',F(-1)<0)
    check('saturation_inverse_undefined',1-Q*(1/Q)==0)
    check('above_saturation_wrong_square',(2/Q)/(S*(1-Q*2/Q))<0)
    check('sign_not_identified',(-d)**2==d**2)
    # An arbitrary neglected finite-field clock term preserves the zero-field
    # derivative but need not preserve finite-field closure. Not a new candidate.
    response_amplitude=F(1,100)
    check('finite_response_not_certified',delta*(z+response_amplitude**2)+K*eta!=0)
    check('full_vs_primed_source_not_interchangeable',S*d*d/(1+Q*S*d*d)!=(S-F(27,100000))*d*d/(1+Q*(S-F(27,100000))*d*d))
    check('clock_sensitivity_not_mass_sensitivity',K!=delta)
    check('atomic_rounded_coefficient_not_exact_input','approximately' in pre['candidate']['atomic_choice'])
    check('empirical_data_not_fitted',pre['data_roles']['calibration'].startswith('EMPTY'))
    check('prospective_success_forbidden',pre['data_roles']['prospective_holdout'].startswith('EMPTY'))
    check('tect_candidate_not_admitted',pre['candidate']['tect_microscopic_admission']=='NOT_ADMITTED')
    check('pah_sources_protected',len(pre['protected_sources'])>=3)
    check('same_source_explicit','same source' in pre['candidate']['geometry_choice'])
    check('denominator_positive',D>0)
    return {'schema':'tect/clk002-hostile/1.0','status':'PASS_CONDITIONAL_SCOPE_CHECKS',
            'prereg_sha256':io.PIN,'script_sha256':io.sha(Path(__file__)),
            'checks':checks,'check_count':len(checks),
            'non_claims':'Passing rejection fixtures is not an all-orders EFT theorem or empirical test. Nuclear, atomic, observer, finite-response and source-composition errors remain external inputs.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); value=audit()
    io.issue_or_check(value,io.RUNS/'hostile.json',args.check)
    print('CLK-002 HOSTILE: PASS',value['check_count'],'scope/mutation fixtures')
