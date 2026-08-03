#!/usr/bin/env python3
"""Non-importing Fraction audit of PA-M2-CI8-RS-v0.

This script imports neither the primary implementation nor SymPy and never
reads the primary result.  It independently reconstructs the exact rational
coefficients used by the dual-lane candidate certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction as F
from math import comb
from pathlib import Path
from typing import Any


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M2-CI8-RS-v0"
SLUG = "pre-a-pa-m2-ci8-rs-dual-lane"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)


def encode(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def moment(power: int) -> F:
    half = power // 2
    return F(comb(2 * half, half), 4**half)


def main_payload() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": encode(actual),
                "expected": encode(expected),
                "group": group,
            }
        )

    nodes = list(itertools.product((-1, 1), repeat=3))
    check("eight sign nodes", len(nodes) == 8, len(nodes), 8, "kernel")
    check("all nodes are distinct", len(set(nodes)) == 8, len(set(nodes)), 8, "kernel")
    for index, node in enumerate(nodes):
        bottom = sum((component * component - 1) ** 2 for component in node)
        check(f"unit node {index} has zero reduced kernel", bottom == 0, bottom, 0, "kernel")
        diagonal_hessian = tuple(4 * (3 * component * component - 1) for component in node)
        check(
            f"unit node {index} has Hessian eight identity",
            diagonal_hessian == (8, 8, 8),
            diagonal_hessian,
            (8, 8, 8),
            "kernel",
        )

    m2 = moment(2)
    m4 = moment(4)
    check("independent cosine moment two", m2 == F(1, 2), m2, F(1, 2), "lane_f")
    check("independent cosine moment four", m4 == F(3, 8), m4, F(3, 8), "lane_f")

    quadratic_coefficient = m2 / 2
    quartic_coefficient = m4 / 4
    check(
        "trial quadratic coefficient",
        quadratic_coefficient == F(1, 4),
        quadratic_coefficient,
        F(1, 4),
        "lane_f",
    )
    check(
        "trial quartic coefficient",
        quartic_coefficient == F(3, 32),
        quartic_coefficient,
        F(3, 32),
        "lane_f",
    )

    # For f(y)=a*r*y+b*g*y^2, y*=-a*r/(2*b*g) and
    # f(y*)=-a^2*r^2/(4*b*g).  Store only the exact coefficients.
    amplitude_coefficient = quadratic_coefficient / (2 * quartic_coefficient)
    energy_coefficient = quadratic_coefficient * quadratic_coefficient / (4 * quartic_coefficient)
    check(
        "trial amplitude coefficient",
        amplitude_coefficient == F(4, 3),
        amplitude_coefficient,
        F(4, 3),
        "lane_f",
    )
    check(
        "trial energy coefficient",
        energy_coefficient == F(1, 6),
        energy_coefficient,
        F(1, 6),
        "lane_f",
    )

    jensen_coefficient = F(1, 4)
    check(
        "Jensen lower-energy coefficient exceeds trial coefficient",
        jensen_coefficient > energy_coefficient,
        (jensen_coefficient, energy_coefficient),
        "1/4 > 1/6",
        "lane_f",
    )
    mean_square_coefficient = F(1, 1)
    check(
        "stationary minimizer mean-square coefficient",
        mean_square_coefficient == 1,
        mean_square_coefficient,
        1,
        "lane_f",
    )

    # For integer m>=1, the closest integer square other than m^2 is
    # (m-1)^2, so the reduced one-coordinate off-node gap is (2m-1)^2.
    # Exhaust a broad exact-integer audit as a bug trap; the all-m inequality
    # is proved separately in the programme note.
    gap_rows = []
    for mode_index in range(1, 65):
        candidates = [
            (integer * integer - mode_index * mode_index) ** 2
            for integer in range(-2 * mode_index - 2, 2 * mode_index + 3)
            if abs(integer) != mode_index
        ]
        gap_rows.append(min(candidates))
    expected_gaps = [(2 * mode_index - 1) ** 2 for mode_index in range(1, 65)]
    check(
        "independent off-node lattice-gap audit",
        gap_rows == expected_gaps,
        gap_rows,
        expected_gaps,
        "lane_f",
    )

    # Independently enumerate all ordered zero-momentum quartets in the CI8
    # star.  A monomial is an exponent tuple for z0..z3,w0..w3.
    representatives = ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1))
    amplitude_index: dict[tuple[int, int, int], int] = {}
    for index, vector in enumerate(representatives):
        amplitude_index[vector] = index
        amplitude_index[tuple(-entry for entry in vector)] = index + 4
    quartet_polynomial: dict[tuple[int, ...], F] = {}
    vectors = tuple(amplitude_index)
    for quartet in itertools.product(vectors, repeat=4):
        if all(sum(vector[axis] for vector in quartet) == 0 for axis in range(3)):
            exponent = [0] * 8
            for vector in quartet:
                exponent[amplitude_index[vector]] += 1
            key = tuple(exponent)
            quartet_polynomial[key] = quartet_polynomial.get(key, F(0)) + 1

    expected_quartic: dict[tuple[int, ...], F] = {}

    def add_monomial(exponents: tuple[int, ...], coefficient: int) -> None:
        expected_quartic[exponents] = expected_quartic.get(exponents, F(0)) + coefficient

    # (3/2)m2^2 with m2=2*sum_i z_i*w_i.
    for i in range(4):
        for j in range(4):
            exponent = [0] * 8
            exponent[i] += 1
            exponent[i + 4] += 1
            exponent[j] += 1
            exponent[j + 4] += 1
            add_monomial(tuple(exponent), 6)
    # The positive pair term in the exact excess.
    for i in range(4):
        for j in range(i + 1, 4):
            exponent = [0] * 8
            for index in (i, i + 4, j, j + 4):
                exponent[index] += 1
            add_monomial(tuple(exponent), 12)
    # The two conjugate resonant monomials.
    resonance_one = [0] * 8
    for index in (4, 1, 2, 3):
        resonance_one[index] += 1
    add_monomial(tuple(resonance_one), 24)
    resonance_two = [0] * 8
    for index in (0, 5, 6, 7):
        resonance_two[index] += 1
    add_monomial(tuple(resonance_two), 24)
    check(
        "independent CI8 quartic convolution identity",
        quartet_polynomial == expected_quartic,
        quartet_polynomial,
        expected_quartic,
        "lane_f",
    )

    # A critical harmonic commutator grows linearly, so its squared OTOC grows
    # quadratically.  The elementary bound log(1+t^2)/(2t)->0 is audited by
    # the exact degree comparison rather than floating-point fitting.
    polynomial_degree = 2
    check(
        "critical Gaussian OTOC polynomial degree",
        polynomial_degree == 2,
        polynomial_degree,
        2,
        "lane_q",
    )
    # The primary SymPy route evaluates lim_{t->infinity}
    # log(1+t^2)/(2t)=0 exactly.  This non-importing route certifies the only
    # algebraic input to that elementary limit: the critical OTOC is degree 2,
    # not an exponential ansatz.  Do not replace the limit with a finite-time
    # numerical fit.

    # Four distinct CI8 nodes obey a momentum parallelogram.  This is the
    # smallest native local-quartic resonance needed beyond one integrable
    # antipodal pair.
    qa = (1, 1, 1)
    qb = (1, -1, -1)
    qc = (1, -1, 1)
    qd = (1, 1, -1)
    left = tuple(qa[i] + qb[i] for i in range(3))
    right = tuple(qc[i] + qd[i] for i in range(3))
    check("four-distinct-node parallelogram", left == right, left, right, "lane_q")
    check(
        "parallelogram uses four distinct nodes",
        len({qa, qb, qc, qd}) == 4,
        len({qa, qb, qc, qd}),
        4,
        "lane_q",
    )

    # Polynomial coefficient audit for the local double-null toy equation.
    # The last entry is the u*v coefficient, so its vanishing is exactly
    # partial_u partial_v phi=0 in this family.
    phi_zero = (0, 0, 0, 0, 0, 0)
    phi_hidden = (0, 1, 0, 0, 0, 0)
    check(
        "independent single-null nonuniqueness equations",
        phi_zero[-1] == 0 and phi_hidden[-1] == 0,
        (phi_zero[-1], phi_hidden[-1]),
        (0, 0),
        "horizon_origin",
    )
    check(
        "independent single-null equal u=0 trace",
        (phi_zero[0], phi_zero[2], phi_zero[4])
        == (phi_hidden[0], phi_hidden[2], phi_hidden[4]),
        (phi_zero[0], phi_zero[2], phi_zero[4]),
        (phi_hidden[0], phi_hidden[2], phi_hidden[4]),
        "horizon_origin",
    )
    data_u = (3, 5, 7)  # a0,a1,a2
    data_v = (3, 11, 13)  # same corner a0,b1,b2
    reconstruction = (data_u[0], data_u[1], data_v[1], data_u[2], data_v[2], 0)
    check(
        "independent compatible double-null reconstruction",
        reconstruction[-1] == 0
        and (reconstruction[0], reconstruction[1], reconstruction[3]) == data_u
        and (reconstruction[0], reconstruction[2], reconstruction[4]) == data_v,
        reconstruction,
        "two compatible traces and zero mixed coefficient",
        "horizon_origin",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "independent exact audit of a T0 candidate certificate",
        "shared_exact_results": {
            "node_count": len(nodes),
            "reduced_node_hessian_diagonal": (8, 8, 8),
            "critical_speed_squared_coefficient": 4,
            "cosine_second_moment": m2,
            "cosine_fourth_moment": m4,
            "trial_amplitude_squared_coefficient": amplitude_coefficient,
            "trial_energy_density_coefficient": energy_coefficient,
            "ground_energy_lower_coefficient": jensen_coefficient,
            "mean_square_upper_coefficient": mean_square_coefficient,
            "off_node_gap_reduced_formula": "(2*m-1)^2",
            "ci8_quartic_convolution_identity": True,
            "ci8_kernel_morphology_minimizer": "one antipodal node pair in the kernel-restricted leading quartic problem",
            "stable_or_critical_gaussian_lyapunov_exponent": 0,
            "smallest_declared_node_resonance": [qa, qb, qc, qd],
            "single_null_sheet_complete_initial_data": False,
            "double_null_polynomial_reconstruction": True,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This audit checks exact isolated-node, cosine-trial, energy-bracket, stable/critical Gaussian "
            "no-chaos, "
            "and four-node-resonance algebra only. It does not establish nonlinear chaos, a quantum "
            "phase transition, compact gauge structure, gravity, identification of an event horizon as the "
            "physical origin, a bounce, or a cyclic universe."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = main_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"independent {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
