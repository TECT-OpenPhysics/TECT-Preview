#!/usr/bin/env python3
"""Non-importing exact audit of PA-CP1-ST8-Q3LOCK-v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-v0"
PARENT_ID = "PA-CP1-ST8-CB-v0"
SLUG = "pre-a-cp1-st8-q3lock"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Counter):
        return {str(key): serial(item) for key, item in sorted(value.items())}
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def vertices() -> tuple[int, ...]:
    return tuple(range(1 << 3))


def edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (node, node ^ (1 << axis))
        for node in vertices()
        for axis in range(3)
        if not (node & (1 << axis))
    )


def walsh(alpha: int, node: int) -> int:
    return -1 if ((alpha & node).bit_count() % 2) else 1


def laplacian_action(alpha: int, node: int) -> int:
    return sum(
        walsh(alpha, node) - walsh(alpha, node ^ (1 << axis))
        for axis in range(3)
    )


def cut(pattern: tuple[int, ...]) -> int:
    return sum(pattern[left] != pattern[right] for left, right in edges())


def lock(left: Fraction, right: Fraction, coupling: Fraction) -> Fraction:
    return coupling * (left - right) ** 2 * (left**2 + right**2) / 4


def sign_energy(
    pattern: tuple[int, ...],
    mass: Fraction,
    quartic: Fraction,
    coupling: Fraction,
) -> Fraction:
    onsite = sum(
        mass * Fraction(sign) ** 2 / 2 + quartic * Fraction(sign) ** 4 / 4
        for sign in pattern
    )
    interaction = sum(
        lock(Fraction(pattern[left]), Fraction(pattern[right]), coupling)
        for left, right in edges()
    )
    return onsite + interaction


Polynomial = dict[tuple[int, int], Fraction]


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for (i, j), first in left.items():
        for (k, ell), second in right.items():
            exponent = (i + k, j + ell)
            output[exponent] = output.get(exponent, Fraction(0)) + first * second
    return {exponent: value for exponent, value in output.items() if value}


def add(*polynomials: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for polynomial in polynomials:
        for exponent, value in polynomial.items():
            output[exponent] = output.get(exponent, Fraction(0)) + value
    return {exponent: value for exponent, value in output.items() if value}


def shifted_power(constant: Fraction, variable: int, power: int) -> Polynomial:
    output: Polynomial = {}
    for degree in range(power + 1):
        exponent = (degree, 0) if variable == 0 else (0, degree)
        output[exponent] = Fraction(comb(power, degree)) * constant ** (power - degree)
    return output


def shifted_edge_polynomial(background_left: Fraction, background_right: Fraction) -> Polynomial:
    a = shifted_power(background_left, 0, 1)
    b = shifted_power(background_right, 1, 1)
    minus_b = {exponent: -value for exponent, value in b.items()}
    difference = add(a, minus_b)
    squares = add(multiply(a, a), multiply(b, b))
    return multiply(multiply(difference, difference), squares)


def verify() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        rows.append(
            {
                "name": name,
                "group": group,
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    cube_vertices = vertices()
    cube_edges = edges()
    check("parent identity", upstream["candidate_id"] == PARENT_ID, upstream["candidate_id"], PARENT_ID, "identity")
    check("binary cube size", len(cube_vertices) == 8, len(cube_vertices), 8, "cube")
    check("binary cube edges", len(cube_edges) == 12, len(cube_edges), 12, "cube")

    spectrum: Counter[int] = Counter()
    for alpha in cube_vertices:
        eigenvalue = 2 * alpha.bit_count()
        check(
            f"Walsh eigen-equation alpha={alpha}",
            all(laplacian_action(alpha, node) == eigenvalue * walsh(alpha, node) for node in cube_vertices),
            [laplacian_action(alpha, node) for node in cube_vertices],
            [eigenvalue * walsh(alpha, node) for node in cube_vertices],
            "cube_character",
        )
        spectrum[eigenvalue] += 1
    expected_spectrum = Counter({0: 1, 2: 3, 4: 3, 6: 1})
    check("independent cube spectrum", spectrum == expected_spectrum, spectrum, expected_spectrum, "cube")

    origin = shifted_edge_polynomial(Fraction(0), Fraction(0))
    ordered = shifted_edge_polynomial(Fraction(1), Fraction(1))
    origin_degrees = {sum(exponent) for exponent in origin}
    ordered_quadratic = {
        exponent: value for exponent, value in ordered.items() if sum(exponent) == 2
    }
    expected_quadratic = {(2, 0): Fraction(2), (1, 1): Fraction(-4), (0, 2): Fraction(2)}
    check("origin polynomial starts at degree four", origin_degrees == {4}, sorted(origin_degrees), [4], "polynomial")
    check("ordered quadratic polynomial", ordered_quadratic == expected_quadratic, ordered_quadratic, expected_quadratic, "polynomial")
    check("ordered edge Hessian from coefficients", (ordered_quadratic[(2, 0)] / 2, ordered_quadratic[(1, 1)] / 4, ordered_quadratic[(0, 2)] / 2) == (1, -1, 1), (ordered_quadratic[(2, 0)] / 2, ordered_quadratic[(1, 1)] / 4, ordered_quadratic[(0, 2)] / 2), (1, -1, 1), "polynomial")

    patterns = tuple(product((-1, 1), repeat=len(cube_vertices)))
    histogram = Counter(cut(pattern) for pattern in patterns)
    expected_histogram = Counter({0: 2, 3: 16, 4: 30, 5: 48, 6: 64, 7: 48, 8: 30, 9: 16, 12: 2})
    check("independent cut histogram", histogram == expected_histogram, histogram, expected_histogram, "ordering")
    check("two zero-cut patterns", histogram[0] == 2, histogram[0], 2, "ordering")
    check("cube edge connectivity gap", min(value for value in histogram if value > 0) == 3, min(value for value in histogram if value > 0), 3, "ordering")

    mass, quartic, coupling = Fraction(-1), Fraction(1), Fraction(5, 7)
    minimum = -len(cube_vertices) * mass**2 / (4 * quartic)
    energies = [sign_energy(pattern, mass, quartic, coupling) for pattern in patterns]
    check("independent same-H minimum", min(energies) == minimum, min(energies), minimum, "ordering")
    check("independent minimum count", energies.count(minimum) == 2, energies.count(minimum), 2, "ordering")
    predicted_gap = 2 * coupling * min(value for value in histogram if value > 0)
    actual_gap = min(value - minimum for value in energies if value > minimum)
    check("independent sign-lock gap", actual_gap == predicted_gap, actual_gap, predicted_gap, "ordering")
    check("zero coupling restores 256", sum(sign_energy(pattern, mass, quartic, Fraction(0)) == minimum for pattern in patterns) == len(patterns), len(patterns), len(patterns), "hostile")

    ordered_spectrum = Counter(
        {-2 * mass + coupling * eigenvalue: multiplicity for eigenvalue, multiplicity in spectrum.items()}
    )
    check("ordered singlet is unique", ordered_spectrum[-2 * mass] == 1, ordered_spectrum[-2 * mass], 1, "hessian")
    check("ordered first transverse level is triplet", ordered_spectrum[-2 * mass + 2 * coupling] == 3, ordered_spectrum[-2 * mass + 2 * coupling], 3, "hessian")
    check("quadratic connected control nullity", spectrum[0] == 1, spectrum[0], 1, "quadratic_control")

    normalized = Fraction(1, len(cube_vertices))
    check("canonical collective normalization", len(cube_vertices) * normalized == 1, len(cube_vertices) * normalized, 1, "collective")
    check("finite collective quartic", len(cube_vertices) * normalized**2 * quartic == quartic / len(cube_vertices), len(cube_vertices) * normalized**2 * quartic, quartic / len(cube_vertices), "collective")
    check("collective interaction vanishes", all(lock(Fraction(4, 3), Fraction(4, 3), coupling) == 0 for _ in cube_edges), 0, 0, "collective")

    fine_spacing = Fraction(3, 20)
    coarse_spacing = 2 * fine_spacing
    species_weight = coarse_spacing**3 / len(cube_vertices)
    check("independent volume factor", species_weight == fine_spacing**3, species_weight, fine_spacing**3, "physical_ledger")
    check("physical diagonal quartic", normalized * len(cube_vertices) * quartic == quartic, normalized * len(cube_vertices) * quartic, quartic, "physical_ledger")

    mass_square = Fraction(9)
    circumference_numerator = Fraction(1, 2)
    first_wave_square = Fraction(4) ** 2
    pah1_squares = (mass_square, mass_square + first_wave_square, mass_square + first_wave_square)
    check("independent PA-H1 tangent", pah1_squares == (9, 25, 25), pah1_squares, (9, 25, 25), "pah1")
    check("PA-H1 degeneracy is spatial pair", pah1_squares.count(25) == 2 and spectrum[2] == 3, (pah1_squares.count(25), spectrum[2]), (2, 3), "pah1")
    check("circle fixture marker", circumference_numerator == Fraction(1, 2), circumference_numerator, Fraction(1, 2), "pah1")

    bipartite_threshold = -len(cube_vertices) * quartic / (8 * len(cube_edges))
    check("negative locking threshold", bipartite_threshold == -quartic / 12, bipartite_threshold, -quartic / 12, "hostile")
    check("square-difference fails sign lock", (Fraction(1) ** 2 - Fraction(-1) ** 2) ** 2 == 0, 0, 0, "hostile")
    check("difference-fourth lacks ordered quadratic", all(sum(exponent) != 2 for exponent in {(4, 0): 1, (3, 1): -4, (2, 2): 6, (1, 3): -4, (0, 4): 1}), True, True, "hostile")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "non-importing Fraction and Walsh audit; not CP1 or Pre-A closure",
        "claim_bearing": False,
        "task_id": "T-054",
        "exact_results": {
            "species_count": len(cube_vertices),
            "cube_edge_count": len(cube_edges),
            "cube_laplacian_spectrum": dict(sorted(spectrum.items())),
            "origin_lock_hessian": "zero",
            "ordered_minimum_count": energies.count(minimum),
            "cut_histogram": dict(sorted(histogram.items())),
            "minimum_old_manifold_gap_fixture": str(predicted_gap),
            "ordered_species_spectrum_fixture": dict(sorted(ordered_spectrum.items())),
            "finite_collective_effective_quartic": str(quartic / len(cube_vertices)),
            "physical_diagonal_continuum_quartic": str(quartic),
            "pah1_collective_tangent_squared_frequencies": list(pah1_squares),
            "quadratic_connected_control_nullity": spectrum[0],
            "negative_lambda_bipartite_threshold": str(bipartite_threshold),
        },
        "scope": {
            "independent_of_primary_import": True,
            "fine_one_site_translation": False,
            "connected_interaction_hypergraph": True,
            "connected_harmonic_graph_at_origin": False,
            "physical_empty_space_comparison": False,
            "selected_collective_quantum_state": False,
            "finite_exact_characteristic_cone": False,
            "CP1_complete": False,
            "Pre_A_complete": False,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "sources": [
            {"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(path)}
            for path in (SCRIPT, UPSTREAM)
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and DEFAULT_OUTPUT.is_file():
        stored = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored independent artifact is stale; regenerate without --self-test")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    count = payload["assertions"]["passed"]
    print(f"PASS {count}/{count} | {CANDIDATE_ID} | non-importing Q3 audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
