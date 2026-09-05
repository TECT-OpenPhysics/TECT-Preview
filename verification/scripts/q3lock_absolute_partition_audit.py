#!/usr/bin/env python3
"""Q3LOCK cyclic Gaussian determinant and absolute partition diagnostics.

Exact rational elimination is compared with a separate Chebyshev recurrence.
Floating-point probes test the derived mesh error, not convergence by sampling.
The harmonic target is a normalization control, not a replacement phase model.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / 'strategy/q3lock-finite-volume-pressure-content-260905.md'
OUT = ROOT / ('claims/C6-SPACETIME-SIGNATURE/runs/'
              '2026-09-05-q3lock-absolute-partition-audit/result.json')
PARAMETERS = ((F(5, 2), F(3, 2), F(7, 4)),
              (F(5, 4), F(4, 5), F(11, 5)),
              (F(4), F(5, 2), F(9, 10)))  # beta,m,a fixture inputs
MESHES = (4, 8, 12, 16)  # Tooling exact determinant sizes.
TOL = 2e-11  # Floating-point diagnostic tolerance, not an analytic bound.
COMPONENTS, VOLUME = 2**3, 2**3  # Q3 components and an L=2 fixture.


def matrix(n, t, periodic=True):
    mat = [[F(0) for _ in range(n)] for _ in range(n)]
    for k in range(n):
        mat[k][k] += t
    edges = [(k, (k + 1) % n) for k in range(n if periodic else n - 1)]
    for k, j in edges:
        mat[k][k] += 1
        mat[j][j] += 1
        mat[k][j] -= 1
        mat[j][k] -= 1
    return mat


def determinant(mat):
    a = [row[:] for row in mat]
    det = F(1)
    for i in range(len(a)):
        pivot = next((k for k in range(i, len(a)) if a[k][i]), None)
        if pivot is None:
            return F(0)
        if pivot != i:
            a[pivot], a[i] = a[i], a[pivot]
            det = -det
        val = a[i][i]
        det *= val
        for k in range(i + 1, len(a)):
            ratio = a[k][i] / val
            for j in range(i + 1, len(a)):
                a[k][j] -= ratio * a[i][j]
            a[k][i] = 0
    return det


def recurrence(n, t):
    prev, curr = F(2), F(2) + t
    for _ in range(2, n + 1):
        prev, curr = curr, (2 + t) * curr - prev
    return curr - 2


def build_payload():
    rows = []
    def check(name, ok, actual, expected):
        assert ok, (name, actual, expected)
        rows.append({'name': name, 'pass': True, 'actual': str(actual), 'expected': str(expected)})
    d = COMPONENTS * VOLUME
    for case, (beta, mass, rigidity) in enumerate(PARAMETERS):
        x = float(beta) * math.sqrt(float(rigidity / mass)) / 2
        log_z = -d * math.log(2 * math.sinh(x))
        previous_error = None
        for n in MESHES:
            eps = beta / n
            t = eps**2 * rigidity / mass
            direct, recur = determinant(matrix(n, t)), recurrence(n, t)
            label = f'case{case}-N{n}'
            check(label + '-exact-det', direct == recur, direct, recur)
            precision = [[mass / eps * xij for xij in row] for row in matrix(n, t)]
            det_p = determinant(precision)
            cancelled = (mass / eps)**(n * d // 2) / det_p**(d // 2)
            expected = direct**(-d // 2)
            check(label + '-free-kernel-prefactor', cancelled == expected, cancelled, expected)
            check(label + '-zero-mode-hostile', determinant(matrix(n, F(0))) == 0, 0, 0)
            opened = determinant(matrix(n, t, False))
            check(label + '-missing-periodic-bond-hostile', opened != direct, opened, direct)
            y = n * math.asinh(x / n)
            closed = 4 * math.sinh(y)**2
            relative = abs(float(direct) / closed - 1)
            check(label + '-hyperbolic-det', relative < TOL, relative, TOL)
            mesh_log_z = -d * math.log(2 * math.sinh(y))
            error = mesh_log_z - log_z
            bound = d / math.tanh(y) * x**3 / (6 * n**2)
            check(label + '-analytic-log-bound', -TOL <= error <= bound + TOL, error, bound)
            if previous_error is not None:
                check(label + '-refinement-probe', error < previous_error, error, previous_error)
            previous_error = error
            # Exact independent harmonic-target normalization control.
            target = rigidity + F(2, 3)  # Fixture target; not Q3LOCK potential.
            target_det = determinant(matrix(n, eps**2 * target / mass))
            target_z = target_det**(-d // 2)
            residual = (direct / target_det)**(d // 2)
            check(label + '-harmonic-target-ratio', expected * residual == target_z,
                  expected * residual, target_z)
            reference2 = rigidity * F(3, 2)
            det2 = recurrence(n, eps**2 * reference2 / mass)
            residual2 = (det2 / target_det)**(d // 2)
            check(label + '-split-independent-absolute', det2**(-d // 2) * residual2 == target_z,
                  det2**(-d // 2) * residual2, target_z)
            check(label + '-residual-alone-depends-on-split', residual != residual2,
                  residual, residual2)
        # Dropping the reference shifts per-oscillator pressure by this amount.
        shift = log_z / (d * float(beta))
        check(f'case{case}-reference-pressure-nonzero', abs(shift) > TOL, shift, 'nonzero')
    return {'schema': 'tect/q3lock-absolute-partition-audit/1.0', 'status': 'PASS',
            'claim_bearing': False, 'assertions_passed': len(rows), 'assertions': rows,
            'source_hashes': {str(path.relative_to(ROOT)).replace('\\', '/'):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (Path(__file__).resolve(), NOTE)},
            'scope': 'Finite determinant and normalization controls; analytic proof and external source crosswalk are in the note.'}


if __name__ == '__main__':
    result = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=OUT.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
        os.replace(tmp, OUT)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print(f"Q3LOCK ABSOLUTE PARTITION PASS {result['assertions_passed']}/{len(result['assertions'])}")
    print(OUT)
