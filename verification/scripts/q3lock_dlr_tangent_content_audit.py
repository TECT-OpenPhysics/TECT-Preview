#!/usr/bin/env python3
"""Finite exact diagnostics for the DLR tangent content, not a limit proof."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / 'strategy/q3lock-dlr-source-tangent-content-260905.md'
OUT = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-dlr-tangent-content-audit/result.json'
COMPONENTS = 2**3  # Model input.
DIMENSION = 3  # Spatial model input.


def build_payload():
    rows = []
    def check(name, actual, expected):
        assert actual == expected, (name, actual, expected)
        rows.append({'name': name, 'actual': str(actual), 'expected': str(expected), 'pass': True})

    # Diagnostic moment inputs; X is reconstructed from time-translation invariance.
    for beta in (F(1,2), F(1), F(3,2), F(2)):
        for length in (4,6):
            volume = length**DIMENSION
            mean_q = F(3,5)
            mean_x = beta * volume * mean_q
            dp = mean_x / volume
            dP = mean_x / (COMPONENTS * beta * volume)
            label = f'beta{beta}-L{length}'
            check(label+'-time-zero', dP, mean_q/COMPONENTS)
            check(label+'-dictionary', dp, COMPONENTS*beta*dP)
            if beta != 1:
                check(label+'-reject-extra-beta', beta*mean_x/volume != dp, True)

    # alpha_k=1/k. The strong input for target alpha_k is alpha_(k+1).
    for k in range(1,7):
        target, source = F(1,k), F(1,k+1)
        check(f'weight{k}-positive-tail-gap', target-source>0, True)
        check(f'weight{k}-reversed-tail-gap', source-target<0, True)

    # Exact exponential weights for alpha=log(4) and log(2), beta=1.
    for n in (1,2,4,8):
        amplitude_squared = F(4)**n
        weak_norm = amplitude_squared * F(1,4)**n
        strong_norm = amplitude_squared * F(1,2)**n
        check(f'escape{n}-weak-norm', weak_norm, F(1))
        check(f'escape{n}-strong-norm', strong_norm, F(2)**n)

    for c in (F(1), F(2,3)):
        for kappa in (F(1), F(3,2)):
            j0=2*DIMENSION*c
            theta=kappa/(2*j0)
            t=theta*j0/kappa
            check(f'c{c}-kappa{kappa}-holder-exponent', t, F(1,2))
            # C1 is a diagnostic input; solve log M <= C1+t log M.
            C1=F(7,3)
            boundary=C1/(1-t)
            check(f'c{c}-kappa{kappa}-closure', boundary, C1+t*boundary)
            check(f'c{c}-kappa{kappa}-hostile', boundary+1>C1+t*(boundary+1), True)

    # Exact summable budgets and radius selection; arbitrary moment bounds are inputs.
    epsilon=F(1,10)
    total=F(0)
    for k in range(1,9):
        budget=epsilon/F(2)**k
        moment=F((k+1)**3)
        radius_squared=moment/budget
        total+=budget
        check(f'budget{k}-markov', moment/radius_squared, budget)
        check(f'budget{k}-partial-sum', total, epsilon*(1-F(1,2)**k))

    return {'schema':'tect/q3lock-dlr-tangent-content-audit/1.0', 'status':'PASS',
            'claim_bearing':False, 'assertions_passed':len(rows), 'assertions':rows,
            'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (Path(__file__).resolve(),NOTE)},
            'scope':'Finite normalization, weight direction and moment-budget diagnostics only; analytic DLR limits require the content proof and imported hypotheses.'}


if __name__ == '__main__':
    payload=build_payload()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=OUT.parent,suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as stream:
            json.dump(payload,stream,indent=2,sort_keys=True)
            stream.write('\n')
        os.replace(tmp,OUT)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    print(f"Q3LOCK DLR TANGENT CONTENT PASS {payload['assertions_passed']}/{len(payload['assertions'])}")
    print(OUT)
