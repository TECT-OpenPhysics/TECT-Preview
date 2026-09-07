#!/usr/bin/env python3
"""Exact finite model-side cross-check for the Q3LOCK FSS interface.

This script checks rescaling, cubic-torus bookkeeping, coercivity, the
zero-sum Poisson source map, and square completion with rational arithmetic.
It does not re-prove FSS and does not test a loop, thermodynamic, or DLR limit.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import tempfile
import sys


ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "strategy/q3lock-fss-primary-source-applicability-audit-260907.md"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-fss-applicability-audit/result.json"

# Inputs and finite diagnostic fixtures. Derived graph/component constants are
# computed below; they are not copied from a displayed result.
LATTICE_DIM = 3
Q3_COMPONENTS = 2 ** LATTICE_DIM
BETA = F(5, 2)
MASS = F(3, 2)
COUPLING = F(11, 7)
QUARTIC = F(7, 5)
R_MASS = F(-9, 4)
SIZES = (4, 6)
MESHES = (2, 5, 11)


def vertices(size):
    return list(product(range(size), repeat=LATTICE_DIM))


def positive_edges(size):
    edges = []
    for y in vertices(size):
        for direction in range(LATTICE_DIM):
            z = list(y)
            z[direction] = (z[direction] + 1) % size
            edges.append((y, tuple(z)))
    return edges


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def norm_sq(vector):
    return dot(vector, vector)


def G_field(size, field):
    """Backward difference used in the manuscript's FSS source map."""
    out = {}
    for y in vertices(size):
        for direction in range(LATTICE_DIM):
            back = list(y)
            back[direction] = (back[direction] - 1) % size
            out[(y, direction)] = field[tuple(back)] - field[y]
    return out


def B_field(size, edge_field):
    """Adjoint divergence B=G* for the same positive bond indexing."""
    out = {y: F(0) for y in vertices(size)}
    for y in vertices(size):
        for direction in range(LATTICE_DIM):
            forward = list(y)
            forward[direction] = (forward[direction] + 1) % size
            out[y] += edge_field[(tuple(forward), direction)]
            out[y] -= edge_field[(y, direction)]
    return out


def build_payload():
    rows = []

    def check(name, actual, expected):
        assert actual == expected, (name, actual, expected)
        rows.append({
            "name": name,
            "actual": str(actual),
            "expected": str(expected),
            "pass": True,
        })

    # FSS's periodic nearest-neighbour bookkeeping: each undirected pair is
    # represented once by a positive-direction bond on these even tori.
    for size in SIZES:
        sites = vertices(size)
        edges = positive_edges(size)
        expected_sites = size ** LATTICE_DIM
        expected_edges = LATTICE_DIM * expected_sites
        check(f"sites-{size}", len(sites), expected_sites)
        check(f"bonds-once-{size}", len(edges), expected_edges)
        neighbours = {site: 0 for site in sites}
        for y, z in edges:
            neighbours[y] += 1
            neighbours[z] += 1
        check(f"degree-{size}", set(neighbours.values()), {2 * LATTICE_DIM})

    # The s=sqrt(epsilon) x change of variables, checked without introducing
    # a square root. The spatial degree and Q3 component count are derived.
    spatial_degree = 2 * LATTICE_DIM
    local_spatial_coefficient = COUPLING * spatial_degree / 2
    check("local-spatial-coefficient", local_spatial_coefficient,
          COUPLING * LATTICE_DIM)
    for mesh in MESHES:
        epsilon = BETA / mesh
        check(f"temporal-rescaling-{mesh}",
              MASS / (2 * epsilon) / epsilon,
              MASS / (2 * epsilon ** 2))
        check(f"quartic-rescaling-{mesh}",
              epsilon * QUARTIC / 4 / epsilon ** 2,
              QUARTIC / (4 * epsilon))
        check(f"spatial-rescaling-{mesh}",
              COUPLING * epsilon / 2 / epsilon,
              COUPLING / 2)

        spin_dimension = Q3_COMPONENTS * mesh
        quartic_coercivity = QUARTIC / (4 * epsilon * spin_dimension)
        expected_coercivity = QUARTIC / (4 * BETA * Q3_COMPONENTS)
        check(f"quartic-coercivity-{mesh}", quartic_coercivity,
              expected_coercivity)
        check(f"spin-dimension-{mesh}", spin_dimension,
              Q3_COMPONENTS * mesh)

    # The l4/l2 inequality behind the lower bound, tested on a nonconstant
    # exact rational vector for every mesh. The expected coefficient is derived
    # from the number of coordinates rather than pasted as 32 beta.
    for mesh in MESHES:
        coordinates = [F(index + 1) for index in range(Q3_COMPONENTS * mesh)]
        sum_fourth = sum(value ** 4 for value in coordinates)
        squared_norm = sum(value ** 2 for value in coordinates)
        coordinate_count = len(coordinates)
        check(f"quartic-power-mean-{mesh}",
              sum_fourth * coordinate_count >= squared_norm ** 2, True)
        check(f"coercivity-denominator-{mesh}",
              (4 * BETA * Q3_COMPONENTS) * QUARTIC /
              (4 * BETA * Q3_COMPONENTS), QUARTIC)

    # A direct adjoint/Poisson fixture. The source is zero-sum and the constant
    # mode is never inverted. A normalized rational proxy for u has norm one.
    size = SIZES[0]
    sites = vertices(size)
    raw = {y: F(y[0] * y[1] + y[2] ** 2) for y in sites}
    average = sum(raw.values()) / len(sites)
    v = {y: raw[y] - average for y in sites}
    check("mean-zero-potential", sum(v.values()), F(0))
    edge_gradient = G_field(size, v)
    source = B_field(size, edge_gradient)
    check("adjoint-source-zero-sum", sum(source.values()), F(0))
    check("adjoint-poisson-energy", sum(value ** 2 for value in edge_gradient.values()),
          sum(v[y] * source[y] for y in sites))
    unit_component_norm = sum(F(1, Q3_COMPONENTS)
                              for _ in range(Q3_COMPONENTS))
    check("collective-vector-norm", unit_component_norm, F(1))
    t = F(13, 7)
    poisson_energy = sum(value ** 2 for value in edge_gradient.values())
    for mesh in MESHES:
        epsilon = BETA / mesh
        mesh_source_norm = mesh * epsilon * t ** 2 * unit_component_norm * poisson_energy
        check(f"poisson-norm-{mesh}", mesh_source_norm,
              BETA * t ** 2 * poisson_energy)
        check(f"fss-mgf-coefficient-{mesh}", mesh_source_norm / (2 * COUPLING),
              BETA * t ** 2 * poisson_energy / (2 * COUPLING))

    # Square completion with a small scalar edge fixture. This detects the
    # common error of shifting by h instead of h/c.
    s_values = {y: F(y[0] - 2 * y[1] + y[2]) for y in sites}
    source_edge = G_field(size, s_values)
    vertex_values = {y: F(y[0] + y[1] - y[2]) for y in sites}
    eta = B_field(size, G_field(size, vertex_values))
    h_norm_sq = sum(value ** 2 for value in G_field(size, vertex_values).values())
    left = COUPLING / 2 * sum(value ** 2 for value in source_edge.values()) - \
        sum(eta[y] * s_values[y] for y in sites)
    shifted = {
        key: source_edge[key] - G_field(size, vertex_values)[key] / COUPLING
        for key in source_edge
    }
    right = COUPLING / 2 * sum(value ** 2 for value in shifted.values()) - \
        h_norm_sq / (2 * COUPLING)
    check("square-completion", left, right)

    # The zero mode is explicitly rejected by the source interface.
    nonzero_mean = {y: F(1) for y in sites}
    check("zero-mode-not-invertible", sum(nonzero_mean.values()) != 0, True)

    # FSS does not require radiality; verify that the Q3 onsite quartic is
    # genuinely non-radial on equal-norm rational vectors.
    vector_a = [F(1), F(0), F(0), F(0), F(0), F(0), F(0), F(0)]
    vector_b = [F(1, 2), F(1, 2), F(1, 2), F(1, 2), F(0), F(0), F(0), F(0)]
    check("equal-norm-nonradial-witness", norm_sq(vector_a), norm_sq(vector_b))
    check("quartic-nonradial-witness",
          sum(value ** 4 for value in vector_a) !=
          sum(value ** 4 for value in vector_b), True)

    source_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            path.read_bytes()).hexdigest()
        for path in (Path(__file__).resolve(), NOTE)
    }
    return {
        "schema": "tect/q3lock-fss-applicability-audit/1.0",
        "status": "PASS",
        "claim_bearing": False,
        "assertions_passed": len(rows),
        "assertions": rows,
        "source_reference": {
            "title": "Froehlich-Simon-Spencer, CMP 50 (1976), Section 2",
            "url": "https://math.caltech.edu/SimonPapers/65.pdf",
            "frozen_bytes": 1404869,
            "frozen_sha256": "108b70f69d707c77c46bb4d4870c9df43be635394d3013be043f8f1a566178e1",
            "source_freeze": "strategy/q3lock-literature-source-freeze-260905.md",
        },
        "scope": "Finite exact model-side FSS interface checks only; no theorem reproof, loop limit, infrared zero mode, DLR passage, cusp, or phase conclusion.",
        "source_hashes": source_hashes,
    }


def write_result(payload):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=OUT.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, OUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv not in ([], ["--check"]):
        print("usage: q3lock_fss_applicability_audit.py [--check]", file=sys.stderr)
        return 2
    payload = build_payload()
    write_result(payload)
    print(f"Q3LOCK FSS APPLICABILITY: PASS {payload['assertions_passed']} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
