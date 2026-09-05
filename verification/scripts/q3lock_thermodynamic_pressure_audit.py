#!/usr/bin/env python3
"""Exact finite diagnostics for the Q3LOCK thermodynamic pressure proof.

Derive seam constants from bond multiplicities; reject the historical 48
coefficient, check even tilings and exact positive crossing-bond identities.
Infinite-volume conclusions depend on the analytic proof, not these fixtures.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from math import prod
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / 'strategy/q3lock-thermodynamic-pressure-content-260905.md'
OUT = ROOT / ('claims/C6-SPACETIME-SIGNATURE/runs/'
              '2026-09-05-q3lock-thermodynamic-pressure-audit/result.json')
DIM, COMPONENTS = 3, 2**3  # Model inputs.
LENGTHS = (2, 4, 6)  # Finite diagnostic sizes.
PARAMS = ((F(1), F(1), F(1)), (F(2, 3), F(5, 4), F(1, 2)))  # c,g,eta


def geometry(sides):
    vertices = list(product(*(range(n) for n in sides)))
    opened, seam = [], []
    for v in vertices:
        for axis, length in enumerate(sides):
            w = list(v)
            w[axis] = (w[axis] + 1) % length
            (seam if v[axis] == length - 1 else opened).append((v, tuple(w)))
    return vertices, opened, seam


def build_payload():
    rows = []
    def check(name, condition, actual, expected):
        assert condition, (name, actual, expected)
        rows.append({'name': name, 'pass': True, 'actual': str(actual), 'expected': str(expected)})
    for length in LENGTHS:
        vertices, opened, seam = geometry((length,) * DIM)
        degree = {v: 0 for v in vertices}
        for v, w in seam:
            degree[v] += 1
            degree[w] += 1
        endpoints = COMPONENTS * sum(degree.values())
        max_degree = max(degree.values())
        check(f'L{length}-seam-count', len(seam) == DIM * length**(DIM-1), len(seam), DIM * length**(DIM-1))
        check(f'L{length}-maximum-degree', max_degree == DIM, max_degree, DIM)
        for c, g, eta in PARAMS:
            allocated = eta * (g / 8) / max_degree
            young_constant = c**2 / (4 * allocated)
            derived = endpoints * young_constant
            # Independent reproduction oracle for the displayed analytic formula.
            oracle = 288 * c**2 * length**2 / (eta * g)
            check(f'L{length}-constant-{c}', derived == oracle, derived, oracle)
            for fixture in range(3):
                values = {v: F(2) * (-1)**sum(v) if fixture == 0 else
                          F(sum(v) + 1, 3) if fixture == 1 else F(0) for v in vertices}
                b = COMPONENTS * c / 2 * sum((values[v] - values[w])**2 for v, w in seam)
                q = COMPONENTS * g / 8 * sum(x**4 for x in values.values())
                check(f'L{length}-bound-{c}-{fixture}', b <= eta * q + derived, b, eta*q+derived)
                if length == 2 and c == g == eta == 1 and fixture == 0:
                    bad = eta*q + 48*c**2*length**2/(eta*g)  # Historical hostile oracle.
                    check('historical-48-counterexample', b > bad, b, bad)
                    check('counterexample-B-oracle', b == 768, b, 768)
                    check('counterexample-Q-oracle', q == 128, q, 128)
        # On an open cube cut along an even coordinate plane; test actual bonds.
        if length >= 4:
            values = {v: F(sum((i+1)*x for i, x in enumerate(v)), 3) for v in vertices}
            cut = 2
            within = [(v,w) for v,w in opened if (v[0]<cut) == (w[0]<cut)]
            crossing = [(v,w) for v,w in opened if (v[0]<cut) != (w[0]<cut)]
            energy = lambda es: COMPONENTS * F(1,2) * sum((values[v]-values[w])**2 for v,w in es)
            check(f'L{length}-cut-identity', energy(opened) == energy(within)+energy(crossing), energy(opened), energy(within)+energy(crossing))
            check(f'L{length}-crossing-positive', energy(crossing)>0, energy(crossing), '>0')
    for sides in ((10,14,18), (16,20,24), (4,6,8)):
        for block in ((2,2,2), (4,6,8)):
            if any(x<y for x,y in zip(sides,block)):
                continue
            intervals = []
            remainders = []
            for x,y in zip(sides,block):
                count, rem = divmod(x,y)
                intervals.append([y]*count+([rem] if rem else []))
                remainders.append(rem)
            pieces = list(product(*intervals))
            vol = prod(sides)
            tiled = prod((x//y)*y for x,y in zip(sides,block))
            remain_fraction = F(vol-tiled,vol)
            upper = sum(F(rem,x) for rem,x in zip(remainders,sides))
            tag=f'{sides}-{block}'
            check(tag+'-volume', sum(prod(piece) for piece in pieces)==vol, sum(prod(piece) for piece in pieces), vol)
            check(tag+'-parity', all(n%2==0 for piece in pieces for n in piece), True, True)
            check(tag+'-remainder', 0<=remain_fraction<=upper, remain_fraction, upper)
    return {'schema':'tect/q3lock-thermodynamic-pressure-audit/1.0','status':'PASS',
            'claim_bearing':False,'assertions_passed':len(rows),'assertions':rows,
            'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (Path(__file__).resolve(),NOTE)},
            'scope':'Finite exact seam and tiling diagnostics; analytic spatial limit is in the content note.'}


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
    print(f"Q3LOCK THERMODYNAMIC PRESSURE PASS {payload['assertions_passed']}/{len(payload['assertions'])}")
    print(OUT)
