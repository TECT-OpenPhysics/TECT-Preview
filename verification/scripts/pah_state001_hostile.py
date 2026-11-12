#!/usr/bin/env python3
"""Executable semantic corruptions of the fixed witness; no source writes.

These tests check verifier sensitivity, not the analytic compression theorem.
Every mutation is restored before continuing. -O must fail closed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import sympy as S
import pah_state001_independent as I

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-11-12-pah-state001/hostile.json'

def audit():
    reference=I.audit()
    assert reference['status']=='PASS_EXACT_FINITE_WITNESS'
    original={name:getattr(I,name) for name in ('energy','mobile','step','ROOTS')}
    def reset_phase(x,r):
        y=original['step'](x,r)
        if y is not None and r[0]=='TR':
            return (y[0],y[1],(0,)*len(y[2]),y[3])
        return y
    mutations=[
        ('energy_sign','energy',lambda x:-original['energy'](x)),
        ('energy_half_factor','energy',lambda x:original['energy'](x)/2),
        ('rate_double','mobile',lambda x,y,r:2*original['mobile'](x,y,r)),
        ('rate_zero','mobile',lambda x,y,r:S.Integer(0)),
        ('TR_phase_reset','step',reset_phase),
        ('drop_K2_negative_PH','ROOTS',tuple(r for r in I.ROOTS if not(r[0]=='PH' and r[2]<0))),
        ('drop_K2_negative_LK','ROOTS',tuple(r for r in I.ROOTS if not(r[0]=='LK' and r[2]<0))),
        ('omit_one_TR','ROOTS',tuple(r for r in I.ROOTS if r!=('TR',0,-1))),
    ]
    rejected=[]
    for name,attribute,value in mutations:
        setattr(I,attribute,value)
        I.action.cache_clear()
        try:
            I.audit()
        except AssertionError:
            rejected.append(name)
        finally:
            for key,old in original.items(): setattr(I,key,old)
            I.action.cache_clear()
        assert name in rejected,'Undetected semantic mutation: '+name
    optimized=[]
    for name in ('primary','independent','hostile','lean'):
        script=ROOT/f'verification/scripts/pah_state001_{name}.py'
        proc=subprocess.run([sys.executable,'-X','utf8','-O',str(script)],
                            capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert proc.returncode!=0 and 'Assertions must be enabled' in proc.stderr
        optimized.append(name)
    # A Gibbs instantaneous rate average loses the within-fibre variance.
    a,b=S.exp(S.Rational(1,2)),S.exp(-S.Rational(1,2))
    assert a>b and S.expand(((2*a-a-b)**2+(2*b-a-b)**2)/2-(a-b)**2)==0
    assert S.expand((a-b)**2)!=0
    return {'schema':'tect/pah-state001-hostile/1.0','status':'PASS_SCOPED_CONTROLS',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'independent_sha256':hashlib.sha256(Path(I.__file__).read_bytes()).hexdigest(),
        'rejected_mutations':rejected,'optimized_rejections':optimized,
        'reference_fibre_size':reference['fibre_size'],
        'scope':'Code sensitivity only. Analytic stationary compression and source applicability reviewed separately.'}

def main():
    if not __debug__: raise RuntimeError('Assertions must be enabled')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    result=audit()
    if a.write:
        assert not OUT.exists(),'Issued run immutable'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    elif a.check: assert json.loads(OUT.read_text(encoding='utf-8'))==result
    print('STATE-001 HOSTILE: PASS',len(result['rejected_mutations']),'semantic mutations;',len(result['optimized_rejections']),'optimization rejections')

if __name__=='__main__': main()
