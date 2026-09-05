#!/usr/bin/env python3
"""Exact finite bookkeeping for the Q3LOCK reflection/infrared content.

Graph fixtures are actual cubic tori; polynomial fields are test inputs.
No finite test is represented as a proof of FSS or an infinite-volume limit.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from math import factorial
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / 'strategy/q3lock-reflection-infrared-content-260905.md'
OUT = ROOT / 'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-q3lock-reflection-infrared-content-audit/result.json'
DIM = 3  # Physical lattice dimension.
COMPONENTS = 2**3  # Q3 vertex count.
SIZES = (4, 6)  # Finite graph diagnostics, not a convergence certificate.
BETAS = (F(1, 3), F(5, 2))  # Independent rational test inputs.
MESHES = (3, 7)  # Time-slice counts used only to check exact scaling.
COUPLING = F(7, 5)  # Diagnostic positive spatial coupling.


def build_payload():
    rows = []
    def check(name, actual, expected):
        assert actual == expected, (name, actual, expected)
        rows.append({'name': name, 'actual': str(actual), 'expected': str(expected), 'pass': True})

    for L in SIZES:
        vertices = list(product(range(L), repeat=DIM))
        V = len(vertices)
        edges = []
        for y in vertices:
            for j in range(DIM):
                z = list(y)
                z[j] = (z[j] + 1) % L
                edges.append((y, tuple(z)))
        check(f'edge-count-{L}', len(edges), DIM*V)
        degrees = {y: 0 for y in vertices}
        for y, z in edges:
            degrees[y] += 1
            degrees[z] += 1
        check(f'degrees-{L}', set(degrees.values()), {2*DIM})
        fixtures = (
            {y: F((-1)**y[0]) for y in vertices},
            {y: F(y[0]*y[1]+y[2]**2, L+1) for y in vertices},
        )
        for index, raw in enumerate(fixtures):
            avg = sum(raw.values()) / V
            v = {y: raw[y]-avg for y in vertices}
            gradient = [v[z]-v[y] for y, z in edges]
            f = {y: F(0) for y in vertices}
            for (y, z), value in zip(edges, gradient):
                f[y] -= value
                f[z] += value
            energy = sum(value**2 for value in gradient)
            vertex_pair = sum(v[y]*f[y] for y in vertices)
            tag = f'{L}-{index}'
            check(f'zero-sum-source-{tag}', sum(f.values()), 0)
            check(f'zero-sum-solution-{tag}', sum(v.values()), 0)
            check(f'adjoint-poisson-energy-{tag}', energy, vertex_pair)
            check(f'reject-vertex-norm-{tag}', sum(value**2 for value in f.values()) != energy, True)
            # v solves L_sp v=f; Gv is its exact minimum-norm edge preimage.
            for beta in BETAS:
                for N in MESHES:
                    epsilon = beta/N
                    # u_i^2=1/COMPONENTS avoids approximation to sqrt(8).
                    norm_u_sq = sum(F(1, COMPONENTS) for _ in range(COMPONENTS))
                    edge_source_norm = sum(epsilon*norm_u_sq*energy for _ in range(N))
                    check(f'source-beta-{tag}-{beta}-{N}', edge_source_norm, beta*energy)
                    mgf_coefficient = edge_source_norm/(2*COUPLING)
                    duhamel_pair_bound = 2*mgf_coefficient/beta**2
                    check(f'duhamel-beta-{tag}-{beta}-{N}', duhamel_pair_bound, energy/(beta*COUPLING))
            if index == 0:
                # Nyquist mode in one coordinate: independent eigenvalue oracle.
                check(f'nyquist-eigenvalue-{L}', {f[y]/v[y] for y in vertices}, {F(4)})

        theta = lambda y: (L-1-y[0],) + y[1:]
        plus = {y for y in vertices if y[0] < L//2}
        crossing = [(y, z) for y, z in edges if (y in plus) != (z in plus)]
        check(f'reflection-involution-{L}', all(theta(theta(y)) == y for y in vertices), True)
        check(f'crossing-reflection-pairs-{L}', all(theta(y) == z for y, z in crossing), True)
        check(f'crossing-count-{L}', len(crossing), 2*L**(DIM-1))

    # Shell polynomial is a labelled independent analytic oracle.
    for n in range(1, 9):
        count = sum(max(map(abs, k)) == n for k in product(range(-n, n+1), repeat=DIM))
        check(f'shell-{n}', count, 24*n*n+2)
        check(f'shell-tail-bound-{n}', F(count, n*n) <= 26, True)

    # Independent finite feature sign control for exp(c<v,w>): its degree-k
    # term is a Gram matrix of tensor powers. No transcendental rounding.
    points = ((F(1), F(-2)), (F(0), F(3)), (F(-1), F(1)))
    coefficients = (F(2), F(-3), F(1))
    dot = lambda v, w: sum(a*b for a, b in zip(v, w))
    for k in range(7):
        direct = sum(a*b*dot(v, w)**k for a, v in zip(coefficients, points)
                     for b, w in zip(coefficients, points))
        feature_sum = F(0)
        for word in product(range(len(points[0])), repeat=k):
            feature = F(0)
            for coefficient, point in zip(coefficients, points):
                monomial = F(1)
                for j in word:
                    monomial *= point[j]
                feature += coefficient*monomial
            feature_sum += feature**2
        check(f'tensor-Gram-{k}', direct, feature_sum)
        check(f'tensor-positivity-{k}', COUPLING**k*direct/F(factorial(k)) >= 0, True)
    return {'schema': 'tect/q3lock-reflection-infrared-content-audit/1.0',
            'status': 'PASS', 'claim_bearing': False, 'assertions_passed': len(rows),
            'assertions': rows,
            'source_hashes': {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__).resolve(), NOTE)},
            'scope': 'Exact finite graph, scaling, shell and kernel-feature diagnostics only; analytic limits require the note and source review.'}


def main():
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write('\n')
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"PASS {payload['assertions_passed']}/{len(payload['assertions'])}: {OUT}")


if __name__ == '__main__':
    main()
