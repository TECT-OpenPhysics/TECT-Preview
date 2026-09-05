#!/usr/bin/env python3
"""Exact Q3LOCK residual/physical-potential reconciliation diagnostics.

Derive bond counts and quadratic coefficient maps from spatial multigraphs.
Compare the difference and pair residuals and detect the doubled diagonal.
Finite exact diagnostics supplement, but do not prove, the loop-limit audit.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / 'strategy/q3lock-harmonic-residual-reconciliation-260905.md'
OUTPUT = ROOT / ('claims/C6-SPACETIME-SIGNATURE/runs/'
                 '2026-09-05-q3lock-harmonic-residual-reconciliation/result.json')

# Model inputs for exact diagnostic fixtures; no fitted/derived constants.
INTERNAL_DIM = 3
SPATIAL_DIM = 3
R, C, G, LAM = F(-3, 2), F(2, 3), F(5, 4), F(3, 5)
SOURCE_COEFFICIENT = F(2, 7)  # h/sqrt(number of components), exactly.
SHAPES = ((2, True), (4, True), (3, False))  # Tooling fixture sizes.


def build_payload():
    internal = list(itertools.product((0, 1), repeat=INTERNAL_DIM))
    d = len(internal)
    internal_edges = [(i, j) for i in range(d) for j in range(i + 1, d)
                      if sum(x != y for x, y in zip(internal[i], internal[j])) == 1]
    rows = []

    def check(name, lhs, rhs):
        assert lhs == rhs, (name, lhs, rhs)
        rows.append({'name': name, 'pass': True, 'actual': str(lhs), 'expected': str(rhs)})

    def quadratic_map(edges, degrees, pair_form):
        coeff = {}
        def add(i, j, val):
            key = tuple(sorted((i, j)))
            coeff[key] = coeff.get(key, F(0)) + val
        if pair_form:
            for i, degree in enumerate(degrees):
                add(i, i, C * degree / 2)
            for i, j in edges:
                add(i, j, -C)
        else:
            for i, j in edges:
                add(i, i, C / 2)
                add(j, j, C / 2)
                add(i, j, -C)
        return coeff

    for length, periodic in SHAPES:
        vertices = list(itertools.product(range(length), repeat=SPATIAL_DIM))
        lookup = {v: i for i, v in enumerate(vertices)}
        edges = []
        for i, vertex in enumerate(vertices):
            for axis in range(SPATIAL_DIM):
                other = list(vertex)
                other[axis] += 1
                if other[axis] == length:
                    if not periodic:
                        continue
                    other[axis] = 0
                edges.append((i, lookup[tuple(other)]))
        degrees = [0] * len(vertices)
        for i, j in edges:
            degrees[i] += 1
            degrees[j] += 1
        tag = f'L{length}-' + ('periodic' if periodic else 'open')
        check(tag + '-quadratic-polynomial', quadratic_map(edges, degrees, False),
              quadratic_map(edges, degrees, True))
        check(tag + '-handshake', sum(degrees), 2 * len(edges))
        if periodic:
            check(tag + '-bond-count', len(edges), SPATIAL_DIM * len(vertices))
        if periodic and length == 2:
            check(tag + '-parallel-bonds', len(edges),
                  2 * len({tuple(sorted(edge)) for edge in edges}))
        if not periodic:
            check(tag + '-boundary-degrees-vary', min(degrees) < max(degrees), True)

        for fixture in range(3):  # Constant, staggered, inhomogeneous fixtures.
            fields = []
            for y, vertex in enumerate(vertices):
                if fixture == 0:
                    q = [F(1)] * d
                elif fixture == 1:
                    q = [F((-1) ** (sum(vertex) + i), i + 1) for i in range(d)]
                else:
                    q = [F((y + 2) * (i + 1) % 11 - 5, i + 2) for i in range(d)]
                fields.append(q)
            norm = [sum(x * x for x in q) for q in fields]
            norm_total = sum(norm)
            onsite = sum(R * norm[y] / 2 + G / 4 * sum(x**4 for x in q)
                         + LAM / 4 * sum((q[i] - q[j])**2 * (q[i]**2 + q[j]**2)
                                         for i, j in internal_edges)
                         - SOURCE_COEFFICIENT * sum(q) for y, q in enumerate(fields))
            difference = C / 2 * sum(sum((x - z)**2 for x, z in zip(fields[i], fields[j]))
                                     for i, j in edges)
            pair = -C * sum(sum(x * z for x, z in zip(fields[i], fields[j]))
                           for i, j in edges)
            allocation = C / 2 * sum(degree * s for degree, s in zip(degrees, norm))
            physical = onsite + difference
            for a in (F(1, 2), 2 * SPATIAL_DIM * C):
                prefix = f'{tag}-fixture{fixture}-a{a}'
                harmonic = a / 2 * norm_total
                residual_diff = onsite - harmonic + difference
                residual_pair = onsite - harmonic + allocation + pair
                old_u = onsite - harmonic + allocation + difference
                check(prefix + '-equivalent-residuals', residual_diff, residual_pair)
                check(prefix + '-physical-reconstruction', residual_pair + harmonic, physical)
                check(prefix + '-old-U-defect', old_u - physical, allocation - harmonic)
                check(prefix + '-old-residual-defect', old_u + harmonic - physical, allocation)
                check(prefix + '-hostile-defect-nonzero', allocation > 0, True)
                # Finite time action: harmonic cancellation holds at each slice.
                for mesh in (4, 8):  # Tooling meshes, not convergence evidence.
                    beta, m = F(5, 2), F(7, 3)  # Gaussian fixture inputs.
                    eps = beta / mesh
                    scales = [F(k + 1, mesh) for k in range(mesh)]
                    kinetic = m / (2 * eps) * norm_total * sum(
                        (scales[(k + 1) % mesh] - scales[k])**2 for k in range(mesh))
                    harmonic_action = eps * harmonic * sum(s**2 for s in scales)
                    # All nonquadratic/source terms cancel from this identity.
                    physical_quadratic = R / 2 * norm_total + difference
                    residual_quadratic = physical_quadratic - harmonic
                    check(prefix + f'-mesh{mesh}-quadratic-action',
                          kinetic + harmonic_action + eps * residual_quadratic * sum(s**2 for s in scales),
                          kinetic + eps * physical_quadratic * sum(s**2 for s in scales))
        # Derive equal-time Wick expectation coefficients from graph counts.
        s = F(3, 7)  # Test covariance input.
        quadratic_mean = (R - F(1, 2)) * d * len(vertices) * s / 2
        spatial_mean = C * d * len(edges) * s
        quartic_mean = G / 4 * d * len(vertices) * 3 * s**2
        edge_wick = 3 * s**2 + 3 * s**2 + 2 * s**2
        locking_mean = LAM / 4 * len(internal_edges) * len(vertices) * edge_wick
        if periodic:
            # Independent oracle: the displayed eight-component periodic formula.
            expected = 4 * (R - F(1, 2) + 6 * C) * s + (6 * G + 24 * LAM) * s**2
            check(tag + '-periodic-Wick-formula',
                  (quadratic_mean + spatial_mean + quartic_mean + locking_mean) / len(vertices), expected)

    return {'schema': 'tect/q3lock-harmonic-residual-audit/1.0', 'status': 'PASS',
            'claim_bearing': False, 'assertions_passed': len(rows), 'assertions': rows,
            'source_hashes': {str(p.relative_to(ROOT)).replace('\\', '/'):
                              hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__).resolve(), NOTE)},
            'scope': 'Exact finite residual identities; analytic weak passage is in the note; no phase or DLR closure.'}


if __name__ == '__main__':
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(f"Q3LOCK RESIDUAL PASS {payload['assertions_passed']}/{len(payload['assertions'])}")
    print(OUTPUT)
