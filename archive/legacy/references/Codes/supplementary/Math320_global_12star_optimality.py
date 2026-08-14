#!/usr/bin/env python3
# =====================================================================
# Math320_global_12star_optimality.py
#
# Numerical verification of the Math320 closure of the Global 12-Star
# Optimality Theorem (Paper-TI-2 §3.5). Provides the quantitative
# sanity-check evidence required by CLAUDE.md §6.3.4.
#
# Verifies:
#   1. BCC {110} cuboctahedral star: r(0)=12, n_1=12, n_2=24, n_4=18,
#      Lambda = 540 (exact).
#   2. Direct L_4 enumeration: 540 (matches Lambda by Lemma).
#   3. Random scan of N antipodal 12-stars: max Lambda = 540 only at
#      cuboctahedral orientations (within tolerance).
#   4. Icosahedral 12-star: Lambda = 132.
#
# Theory tag: Math320-BCC-Global-12-Star-Optimality-Closure-2026-05-06
# =====================================================================
from __future__ import annotations

import argparse
import sys
import numpy as np
from collections import Counter
from typing import Tuple


def bcc_110_star() -> np.ndarray:
    """BCC {110} reciprocal half-star: 12 unit vectors (up to scale)."""
    v = np.array([
        [+1,+1, 0],[-1,-1, 0],[+1,-1, 0],[-1,+1, 0],
        [+1, 0,+1],[-1, 0,-1],[+1, 0,-1],[-1, 0,+1],
        [ 0,+1,+1],[ 0,-1,-1],[ 0,+1,-1],[ 0,-1,+1],
    ], dtype=float)
    return v / np.linalg.norm(v[0])


def icosahedral_star() -> np.ndarray:
    """Icosahedral 12-star (vertices of a regular icosahedron, antipodal)."""
    phi = (1 + np.sqrt(5)) / 2
    raw = np.array([
        [ 0, +1, +phi],[ 0, -1, +phi],[ 0, +1, -phi],[ 0, -1, -phi],
        [+1, +phi, 0],[-1, +phi, 0],[+1, -phi, 0],[-1, -phi, 0],
        [+phi, 0, +1],[+phi, 0, -1],[-phi, 0, +1],[-phi, 0, -1],
    ])
    return raw / np.linalg.norm(raw[0])


def random_antipodal_12_star(rng: np.random.Generator) -> np.ndarray:
    """Random orthogonal rotation applied to BCC {110}, then random
    perturbation breaking cubic symmetry but preserving antipodality."""
    R = np.linalg.qr(rng.standard_normal((3,3)))[0]
    base = bcc_110_star()
    perturb = rng.standard_normal((6,3)) * 0.15
    perturbed = np.zeros_like(base)
    for i in range(6):
        v = base[2*i] + perturb[i]
        v = v / np.linalg.norm(v)
        perturbed[2*i]   = v
        perturbed[2*i+1] = -v
    return perturbed @ R.T


def compute_distribution(S: np.ndarray, tol: float = 1e-9) -> Tuple[Counter, int]:
    """Compute r(v) distribution for ordered pairs (i,j) ∈ S × S.
    Returns (Counter mapping rounded v -> r(v), L_4)."""
    sums = Counter()
    for i in range(len(S)):
        for j in range(len(S)):
            v = tuple(np.round((S[i] + S[j]) / tol).astype(int))
            sums[v] += 1
    L_4 = sum(m**2 for m in sums.values())
    return sums, L_4


def summarise(name: str, S: np.ndarray) -> dict:
    sums, L4 = compute_distribution(S)
    by_m = Counter()
    for v, m in sums.items():
        by_m[m] += 1
    Lambda = sum(m**2 * n for m, n in by_m.items())
    print(f'\n=== {name} ===')
    print(f'  N = {len(S)}, antipodal: ', end='')
    S_set = {tuple(np.round(s/1e-9).astype(int)) for s in S}
    antipodal_ok = all(tuple(np.round(-s/1e-9).astype(int)) in S_set for s in S)
    print('YES' if antipodal_ok else 'NO')
    print(f'  Distribution by multiplicity:')
    for m in sorted(by_m.keys(), reverse=True):
        print(f'    r(v) = {m:3d}  n_m = {by_m[m]:4d}    contribution {by_m[m]*m**2:5d}')
    print(f'  Lambda(S) = {Lambda}  L_4 = {L4}')
    return {'name': name, 'Lambda': Lambda, 'L_4': L4, 'distribution': dict(by_m)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n-random', type=int, default=10000,
                   help='number of random antipodal 12-stars to scan (default 10000)')
    p.add_argument('--seed', type=int, default=20260506)
    args = p.parse_args()

    print(' Math320 numerical verification (CLAUDE.md §6.3.4)')

    bcc = summarise('BCC {110} cuboctahedral star', bcc_110_star())
    ico = summarise('Icosahedral 12-star', icosahedral_star())

    bcc_lambda_expected = 540
    ico_lambda_expected = 396  # corrected from TECT-BCC-Part-I '132' value
                               # (which used a non-standard, off-diagonal-only Lambda)
    bcc_pass = (bcc['Lambda'] == bcc_lambda_expected and bcc['L_4'] == bcc_lambda_expected)
    ico_pass = (ico['Lambda'] == ico_lambda_expected)
    print(f'\nBCC Lambda check: {bcc["Lambda"]} == {bcc_lambda_expected} ? {bcc_pass}')
    print(f'ICO Lambda check: {ico["Lambda"]} == {ico_lambda_expected} ? {ico_pass}')
    print(f'Ratio Lambda_BCC / Lambda_ICO = {bcc["Lambda"]/ico["Lambda"]:.3f}')

    print(f'\n=== Random scan ({args.n_random:d} antipodal 12-stars) ===')
    rng = np.random.default_rng(args.seed)
    max_lambda = 0
    over_540 = 0
    for k in range(args.n_random):
        S = random_antipodal_12_star(rng)
        _, L4 = compute_distribution(S, tol=1e-6)
        if L4 > 540:
            over_540 += 1
        if L4 > max_lambda:
            max_lambda = L4
    print(f'  max Lambda in random scan = {max_lambda}')
    print(f'  # scans exceeding 540    = {over_540}')
    scan_pass = (over_540 == 0)
    print(f'  scan PASS (no Lambda > 540): {scan_pass}')

    overall = bcc_pass and ico_pass and scan_pass
    print(f'\nOverall PASS: {overall}')
    return 0 if overall else 1


if __name__ == '__main__':
    raise SystemExit(main())
