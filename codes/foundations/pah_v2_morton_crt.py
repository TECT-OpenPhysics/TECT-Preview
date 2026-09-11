#!/usr/bin/env python3
"""Prototype implementation of the UNAPPROVED Morton/CRT comparison draft.

Only integer definitions; no functional, rates, Gibbs weights or dynamics.
The original source enumerator owns states and all labelled root incidences.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import accumulate
import random

import pah_v2_root_enumerator as en


def primes(count):
    out = []
    candidate = 2
    while len(out) < count:
        if all(candidate % p for p in out if p * p <= candidate):
            out.append(candidate)
        candidate += 1
    return out


def morton(x, y):
    z = 0
    for b in range(max(x.bit_length(), y.bit_length())):
        z += (((x >> b) & 1) + 2 * ((y >> b) & 1)) << (2 * b)
    return z


def coordinates(z):
    x = y = 0
    for b in range((z.bit_length() + 1) // 2):
        x += ((z >> (2 * b)) & 1) << b
        y += ((z >> (2 * b + 1)) & 1) << b
    return x, y


@dataclass(frozen=True)
class Index:
    r: int
    h: int
    N: int
    q0: int = 1
    m0: int = 1

    def __post_init__(self):
        assert all(type(i) is int and i >= 0 for i in (self.r, self.h, self.N))
        assert type(self.q0) is int and type(self.m0) is int
        assert 1 <= self.q0 <= self.m0

    def step(self, axis, direction=1):
        vals = [self.r, self.h, self.N]
        vals[axis] += direction
        return Index(*vals, self.q0, self.m0)


@lru_cache(None)
def geometry(h, N):
    W = 2 ** (h + N + 1)
    edges = []
    for z in range(W * W):
        x, y = coordinates(z)
        if x + 1 < W:
            edges.append((z, morton(x + 1, y)))
        if y + 1 < W:
            edges.append((z, morton(x, y + 1)))
    lookup = {e: i for i, e in enumerate(edges)}
    faces = []
    for y in range(W - 1):
        for x in range(W - 1):
            a, b, c, d = [morton(*v) for v in
                           ((x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1))]
            faces.append(((lookup[a, b], 1), (lookup[b, c], 1),
                          (lookup[d, c], -1), (lookup[a, d], -1)))
    return W, tuple(edges), tuple(faces)


@lru_cache(None)
def regulator(idx):
    W, edges, _ = geometry(idx.h, idx.N)
    K = 1
    for p in primes(idx.r + 1):
        K *= p
    return en.Regulator(W * W, edges, K, 2 ** idx.r,
                        idx.m0 * 4 ** idx.r, idx.q0 * 2 ** idx.r)


@lru_cache(None)
def child_paths(coarse):
    co, fi = regulator(coarse), regulator(coarse.step(1))
    lookup = {e: i for i, e in enumerate(fi.edges)}
    paths = []
    for a, b in co.edges:
        x, y = coordinates(a)
        xx, yy = coordinates(b)
        mid = morton(x + xx, y + yy)
        paths.append((lookup[4 * a, mid], lookup[mid, 4 * b]))
    assert len(set(e for path in paths for e in path)) == 2 * len(paths)
    return tuple(paths)


@lru_cache(None)
def retained_edges(coarse):
    fine = coarse.step(2)
    lookup = {e: i for i, e in enumerate(regulator(fine).edges)}
    return tuple(lookup[e] for e in regulator(coarse).edges)


def project(x, fine, axis):
    """Adjacent fine-to-coarse state map; defined on every source tuple."""
    co = fine.step(axis, -1)
    rc, rf = regulator(co), regulator(fine)
    assert en.valid_state(rf, x)
    if axis == 0:
        P = rf.K // rc.K
        A = pow(P, -1, rc.K)
        cumulative = [0] + [s // 2 for s in accumulate(x.occupation)]
        result = en.State(tuple(j // 2 for j in x.aperture),
                          tuple(b - a for a, b in zip(cumulative, cumulative[1:])),
                          tuple(A * n % rc.K for n in x.phase),
                          tuple(A * u % rc.K for u in x.link))
    elif axis == 1:
        result = en.State(x.aperture[::4],
                          tuple(sum(x.occupation[4*z:4*z+4]) for z in range(rc.vertices)),
                          x.phase[::4],
                          tuple(sum(x.link[e] for e in p) % rc.K for p in child_paths(co)))
    elif axis == 2:
        t = rc.vertices - 1
        result = en.State(x.aperture[:rc.vertices],
                          x.occupation[:t] + (rc.Q - sum(x.occupation[:t]),),
                          x.phase[:rc.vertices],
                          tuple(x.link[e] for e in retained_edges(co)))
    else:
        raise ValueError("Unknown comparison direction")
    assert en.valid_state(rc, result)
    return result


def inject(x, coarse, axis):
    co, fi = regulator(coarse), regulator(coarse.step(axis))
    assert en.valid_state(co, x)
    if axis == 0:
        P = fi.K // co.K
        y = en.State(tuple(2*j for j in x.aperture), tuple(2*l for l in x.occupation),
                     tuple(P*n for n in x.phase), tuple(P*u for u in x.link))
    else:
        ap = [0] * fi.vertices
        occ = ap.copy()
        phase = ap.copy()
        links = [0] * len(fi.edges)
        for v in range(co.vertices):
            rep = 4*v if axis == 1 else v
            ap[rep], occ[rep], phase[rep] = x.aperture[v], x.occupation[v], x.phase[v]
        targets = tuple(p[0] for p in child_paths(coarse)) if axis == 1 else retained_edges(coarse)
        for e, target in enumerate(targets):
            links[target] = x.link[e]
        y = en.State(tuple(ap), tuple(occ), tuple(phase), tuple(links))
    assert en.valid_state(fi, y)
    return y


def project_to(x, fine, coarse, order=(2, 1, 0)):
    assert (fine.q0, fine.m0) == (coarse.q0, coarse.m0)
    assert all(a >= b for a, b in zip((fine.r, fine.h, fine.N), (coarse.r, coarse.h, coarse.N)))
    cur = fine
    for axis in order:
        while (cur.r, cur.h, cur.N)[axis] > (coarse.r, coarse.h, coarse.N)[axis]:
            x = project(x, cur, axis)
            cur = cur.step(axis, -1)
    assert cur == coarse
    return x


def gauge(x, idx, g):
    reg = regulator(idx)
    assert len(g) == reg.vertices
    return en.State(x.aperture, x.occupation,
                    tuple((n+a) % reg.K for n, a in zip(x.phase, g)),
                    tuple((u+g[w]-g[v]) % reg.K for u, (v, w) in zip(x.link, reg.edges)))


def gauge_project(g, fine, axis):
    co = fine.step(axis, -1)
    rc, rf = regulator(co), regulator(fine)
    if axis == 0:
        return tuple(pow(rf.K // rc.K, -1, rc.K) * v % rc.K for v in g)
    return g[::4] if axis == 1 else g[:rc.vertices]


def sample(idx, seed):
    """Declared deterministic test input, not an ensemble or fitted state."""
    reg = regulator(idx)
    rng = random.Random(seed)
    occ = [0] * reg.vertices
    for _ in range(reg.Q):
        occ[rng.randrange(reg.vertices)] += 1
    x = en.State(tuple(rng.randrange(reg.M_s+1) for _ in occ), tuple(occ),
                 tuple(rng.randrange(reg.K) for _ in occ),
                 tuple(rng.randrange(reg.K) for _ in reg.edges))
    assert en.valid_state(reg, x)
    return x


def flat(x):
    return x.aperture + x.occupation + x.phase + x.link


def assign_root(x, fine, axis, root):
    rf = regulator(fine)
    y = en.apply_move(rf, x, root)
    assert y is not None
    reverse = root.inverse()
    key = lambda z, s: (flat(z), s.family, s.cell, s.sign)
    flipped = key(y, reverse) < key(x, root)
    a, b = (y, x) if flipped else (x, y)
    aa, bb = project(a, fine, axis), project(b, fine, axis)
    rc = regulator(fine.step(axis, -1))
    chosen = next((s for s, dest in en.incidences(rc, aa) if dest == bb), None)
    return chosen.inverse() if chosen is not None and flipped else chosen
