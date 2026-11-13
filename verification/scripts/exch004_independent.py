#!/usr/bin/env python3
"""Independent conditional readout controls; no primary imports/native PASS.

Exact reference matrices are test oracles, not experimental calibrations.
The current-generating coupling is fixed while analyzer orientation is unknown.
"""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-13-exch004/independent.json'


def main():
    ident=s.eye(2)
    sx=s.Matrix([[0,1],[1,0]]);sy=s.Matrix([[0,-s.I],[s.I,0]]);sz=s.diag(1,-1)
    pair=s.Matrix([[0,0],[s.sqrt(2),0]])
    na,nb=s.diag(2,0),s.diag(0,1)
    rho=[(ident+sign*sy)/2 for sign in (1,-1)]
    mean=lambda state,op:s.simplify(s.trace(state*op))
    checks={}
    def check(name,condition):
        checks[name]=bool(condition);assert checks[name],name
    check('positive_normalized_reference_states',all(st==st.H and st.det()==0 and s.trace(st)==1 for st in rho))
    check('same_populations',all(mean(st,na)==1 and mean(st,nb)==s.Rational(1,2) for st in rho))
    check('same_xz_calibration',all(mean(st,(ident+sx)/2)==s.Rational(1,2) and mean(st,(ident+sz)/2)==s.Rational(1,2) for st in rho))
    check('opposite_pair_quadrature',mean(rho[0],pair)==-s.I/s.sqrt(2) and mean(rho[1],pair)==s.I/s.sqrt(2))
    check('same_real_pair_energy',all(mean(st,pair+pair.T)==0 for st in rho))
    check('different_known_y_holdout',mean(rho[0],(ident+sy)/2)==1 and mean(rho[1],(ident+sy)/2)==0)
    target=s.Matrix([[0,-1/s.sqrt(2),0]])
    axz=s.Matrix([[s.Rational(1,2),0,0],[0,0,s.Rational(1,2)]])
    ay=s.Matrix([[0,s.Rational(1,2),0]])
    check('xz_target_not_identified',axz.rank()==2 and axz.col_join(target).rank()==3)
    check('one_calibrated_y_axis_suffices',ay.col_join(target).rank()==1)
    g,hbar=s.symbols('g hbar',real=True,nonzero=True)
    hpair=g*(pair+pair.T)
    dop=s.simplify(s.I*(hpair*na-na*hpair)/hbar)
    imag_op=(pair-pair.T)/(2*s.I)
    check('reference_current_factor',s.simplify(dop+4*g*imag_op/hbar)==s.zeros(2))
    for j,phi in enumerate((0,s.pi/2,s.pi,3*s.pi/2)):
        effect0=(ident+s.cos(phi)*sx+s.sin(phi)*sy)/2
        effect_pi=(ident+s.cos(phi+s.pi)*sx+s.sin(phi+s.pi)*sy)/2
        check(f'unknown_analyzer_orientation_{j}',mean(rho[0],effect0)==mean(rho[1],effect_pi))
    beta=s.Matrix([-1/s.sqrt(2),1/s.sqrt(2)])
    v1,v2,cov=s.symbols('v1 v2 cov',real=True)
    covariance=s.Matrix([[v1,cov],[cov,v2]])
    variance=s.simplify((beta.T*covariance*beta)[0])
    check('correlated_difference_variance',s.simplify(variance-(v1+v2-2*cov)/2)==0)
    report={'status':'PASS_CONDITIONAL_REFERENCE_READOUT_ALGEBRA','checks':checks,'check_count':len(checks),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'witness':{'same_readouts':'population, real pair energy, x/z effects',
      'different_target':'ImC = minus/plus 1/sqrt(2), fixed native g',
      'different_known_holdout':'reference calibrated y-effect probability1 versus0, NOT experimental data'},
      'scope':'Calibrated two-channel reference effects only, not native continuum dynamics.',
      'physical_verdict':'NOT_ESTABLISHED_BY_THIS_ALGEBRA',
      'missing':'Native instrument effects and their joint errors/covariance.',
      'non_claims':'No EXCH quantization, source-native no-go, calibrated instrument, empirical holdout, P1 identity or physical time.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXCH004 INDEPENDENT: PASS',len(checks),'conditional checks')


if __name__=='__main__':main()
