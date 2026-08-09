#!/usr/bin/env python3
"""Non-importing standard-library audit for EXP-000789.

This implementation does not import the primary verifier.  It uses explicit
finite-torus sums and a small exact polynomial engine over Fraction instead
of mpmath, numpy, or sympy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION"
EXPLORATION_ID = "EXP-000789"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-SPECTRAL-GAP",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-G-LAMBDA-ONLY-4D-ONE-LOOP-CLOSURE",
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260809.md"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-09-independent-{SLUG}/result.json"

# Labelled regression oracles only.
TEST_ORACLE_I3 = 0.505462019717326006
TEST_ORACLE_J3 = 0.643953733381468096

Exponent = tuple[int, ...]
LinearGL = tuple[Fraction, Fraction]
QuadraticGL = tuple[Fraction, Fraction, Fraction]


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def vertices() -> list[tuple[int, int, int]]:
    return [(index >> 2 & 1, index >> 1 & 1, index & 1) for index in range(8)]


def edges() -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for left in range(8):
        for bit in (1, 2, 4):
            right = left ^ bit
            if left < right:
                result.append((left, right))
    return result


def hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def finite_constants(length: int) -> tuple[float, float]:
    cosines = [math.cos(2.0 * math.pi * index / length) for index in range(length)]
    watson = 0.0
    half_watson = 0.0
    for first in range(length):
        for second in range(length):
            for third in range(length):
                if first == second == third == 0:
                    continue
                energy = 3.0 - cosines[first] - cosines[second] - cosines[third]
                watson += 1.0 / energy
                half_watson += 1.0 / math.sqrt(energy)
    volume = float(length**3)
    return watson / volume, half_watson / volume


def falk_upper(duhamel: float, commutator: float) -> float:
    root = math.sqrt(commutator / (4.0 * duhamel))
    return math.sqrt(duhamel * commutator) / (2.0 * math.tanh(root))


def zero_exponent() -> Exponent:
    return (0,) * 8


def exponent_with(pairs: dict[int, int]) -> Exponent:
    values = [0] * 8
    for index, power in pairs.items():
        values[index] = power
    return tuple(values)


def add_linear(left: LinearGL, right: LinearGL) -> LinearGL:
    return left[0] + right[0], left[1] + right[1]


def scale_linear(value: LinearGL, scalar: Fraction) -> LinearGL:
    return value[0] * scalar, value[1] * scalar


def add_term(poly: dict[Exponent, LinearGL], exponent: Exponent, value: LinearGL) -> None:
    poly[exponent] = add_linear(poly.get(exponent, (Fraction(0), Fraction(0))), value)
    if poly[exponent] == (0, 0):
        del poly[exponent]


def derivative(poly: dict[Exponent, LinearGL], variable: int) -> dict[Exponent, LinearGL]:
    result: dict[Exponent, LinearGL] = {}
    for exponent, coefficient in poly.items():
        power = exponent[variable]
        if power == 0:
            continue
        lowered = list(exponent)
        lowered[variable] -= 1
        add_term(result, tuple(lowered), scale_linear(coefficient, Fraction(power)))
    return result


def hessian_entry(poly: dict[Exponent, LinearGL], left: int, right: int) -> dict[Exponent, LinearGL]:
    return derivative(derivative(poly, left), right)


def add_quadratic(left: QuadraticGL, right: QuadraticGL) -> QuadraticGL:
    return left[0] + right[0], left[1] + right[1], left[2] + right[2]


def multiply_linear(left: LinearGL, right: LinearGL) -> QuadraticGL:
    return left[0] * right[0], left[0] * right[1] + left[1] * right[0], left[1] * right[1]


def square_accumulate(target: dict[Exponent, QuadraticGL], poly: dict[Exponent, LinearGL]) -> None:
    for left_exp, left_value in poly.items():
        for right_exp, right_value in poly.items():
            exponent = tuple(a + b for a, b in zip(left_exp, right_exp))
            target[exponent] = add_quadratic(
                target.get(exponent, (Fraction(0), Fraction(0), Fraction(0))),
                multiply_linear(left_value, right_value),
            )


def build_quartic() -> dict[Exponent, LinearGL]:
    poly: dict[Exponent, LinearGL] = {}
    for index in range(8):
        add_term(poly, exponent_with({index: 4}), (Fraction(1, 4), Fraction(0)))
    for left, right in edges():
        add_term(poly, exponent_with({left: 4}), (Fraction(0), Fraction(1, 4)))
        add_term(poly, exponent_with({right: 4}), (Fraction(0), Fraction(1, 4)))
        add_term(poly, exponent_with({left: 3, right: 1}), (Fraction(0), Fraction(-1, 2)))
        add_term(poly, exponent_with({left: 1, right: 3}), (Fraction(0), Fraction(-1, 2)))
        add_term(poly, exponent_with({left: 2, right: 2}), (Fraction(0), Fraction(1, 2)))
    return poly


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent pass", parent["verdict"] == "PASS", parent["verdict"], "PASS", "parent")

    graph_vertices = vertices()
    graph_edges = edges()
    audit.check("binary vertices", len(set(graph_vertices)) == 8, graph_vertices, "8 unique", "q3")
    audit.check("xor edges", len(graph_edges) == 12, graph_edges, "12", "q3")
    degrees = [sum(index in edge for edge in graph_edges) for index in range(8)]
    audit.check("degree three", degrees == [3] * 8, degrees, [3] * 8, "q3")
    common_03 = [index for index in range(8) if hamming(index, 0) == hamming(index, 3) == 1]
    common_07 = [index for index in range(8) if hamming(index, 0) == hamming(index, 7) == 1]
    audit.check("distance two", hamming(0, 3) == 2, hamming(0, 3), 2, "q3")
    audit.check("two common neighbours", len(common_03) == 2, common_03, "two", "q3")
    audit.check("distance three no common neighbour", len(common_07) == 0, common_07, [], "q3")

    constant_rows: list[dict[str, float]] = []
    for length in (8, 16, 32, 64):
        i_value, j_value = finite_constants(length)
        constant_rows.append({"L": length, "I3_L": i_value, "J3_L": j_value})
        audit.check("finite Cauchy", j_value**2 <= i_value + 2e-14, j_value**2, i_value, "watson")
    i64, j64 = constant_rows[-1]["I3_L"], constant_rows[-1]["J3_L"]
    audit.check("finite J3 approaches oracle", abs(j64 - TEST_ORACLE_J3) < 2e-4, j64, TEST_ORACLE_J3, "watson")
    audit.check("finite I3 approaches oracle", abs(i64 - TEST_ORACLE_I3) < 8e-3, i64, TEST_ORACLE_I3, "watson")
    audit.check("oracle Cauchy", TEST_ORACLE_J3**2 < TEST_ORACLE_I3, TEST_ORACLE_J3**2, TEST_ORACLE_I3, "watson")

    harmonic_rows: list[dict[str, float]] = []
    for beta, hbar, chi, omega in ((1.0, 1.0, 1.0, 1.0), (2.3, 0.7, 1.4, 1.8), (8.0, 2.0, 3.0, 0.2)):
        duhamel = 1.0 / (beta * chi * omega**2)
        commutator = beta * hbar**2 / chi
        upper = falk_upper(duhamel, commutator)
        equal = hbar / (2 * chi * omega * math.tanh(beta * hbar * omega / 2))
        harmonic_rows.append({"upper": upper, "equal_time": equal})
        audit.check("harmonic exact coth", abs(upper - equal) < 2e-14, upper, equal, "falk_bruch")
    for commutator in (0.7, 4.0):
        chain = [falk_upper(value, commutator) for value in (0.03, 0.2, 1.0, 5.0)]
        audit.check("coth expression monotone", all(left < right for left, right in zip(chain, chain[1:])), chain, "increasing", "falk_bruch")

    beta, hbar, chi, coupling, energy = 3.7, 1.1, 2.2, 0.6, 1.9
    cap = falk_upper(1.0 / (2 * beta * coupling * energy), beta * hbar**2 / chi)
    formula = hbar / (2 * math.sqrt(2 * chi * coupling * energy) * math.tanh(beta * hbar * math.sqrt(coupling * energy / (2 * chi))))
    audit.check("independent IR substitution", abs(cap - formula) < 2e-14, cap, formula, "ground_order")

    ground_fixture_rows: list[dict[str, float | bool]] = []
    for strength in (0.43, 0.51, 3.0):
        theta = math.sqrt(strength / 8.0)
        rho = theta * (1.0 - TEST_ORACLE_J3 / math.sqrt(strength))
        intrinsic = strength > TEST_ORACLE_J3**2
        finite_temperature = strength > TEST_ORACLE_I3
        ground_fixture_rows.append({"A0": strength, "rho_star": rho, "intrinsic": intrinsic, "finite_temperature": finite_temperature})
        audit.check("rho threshold", (rho > 0) is intrinsic, rho > 0, intrinsic, "ground_order")
    audit.check("strictly weaker threshold fixture", bool(ground_fixture_rows[0]["intrinsic"]) and not bool(ground_fixture_rows[0]["finite_temperature"]), ground_fixture_rows[0], "ground only", "ground_order")

    for volume in (8, 125, 1000):
        hbar_value, chi_value, order = 1.4, 0.8, 0.55
        s_squared = Fraction(volume * volume) * Fraction(11, 20)
        commutator = Fraction(volume) * Fraction(49, 25) / Fraction(4, 5)
        gap = commutator / (2 * s_squared)
        formula_gap = Fraction(49, 25) / (2 * Fraction(4, 5) * volume * Fraction(11, 20))
        audit.check("exact parity quotient", gap == formula_gap, gap, formula_gap, "gap")
        audit.check("exact doublet half", gap / 2 == Fraction(49, 25) / (4 * Fraction(4, 5) * volume * Fraction(11, 20)), gap / 2, "half", "gap")

    quartic = build_quartic()
    audit.check("bare distance-two absent", exponent_with({0: 2, 3: 2}) not in quartic, quartic.get(exponent_with({0: 2, 3: 2})), None, "one_loop")
    audit.check("bare edge mixed present", quartic[exponent_with({0: 2, 1: 2})] == (0, Fraction(1, 2)), quartic[exponent_with({0: 2, 1: 2})], (0, Fraction(1, 2)), "one_loop")

    laplacian: dict[Exponent, LinearGL] = {}
    for variable in range(8):
        for exponent, value in derivative(derivative(quartic, variable), variable).items():
            add_term(laplacian, exponent, value)
    for index in range(8):
        expected = (Fraction(3), Fraction(12))
        audit.check("Wick diagonal coefficient", laplacian[exponent_with({index: 2})] == expected, laplacian[exponent_with({index: 2})], expected, "wick")
    for left, right in graph_edges:
        expected = (Fraction(0), Fraction(-6))
        audit.check("Wick edge coefficient", laplacian[exponent_with({left: 1, right: 1})] == expected, laplacian[exponent_with({left: 1, right: 1})], expected, "wick")
    laplacian_twice = (Fraction(0), Fraction(0))
    for variable in range(8):
        second = derivative(derivative(laplacian, variable), variable)
        laplacian_twice = add_linear(laplacian_twice, second.get(zero_exponent(), (0, 0)))
    audit.check("Wick second Laplacian", laplacian_twice == (Fraction(48), Fraction(192)), laplacian_twice, (48, 192), "wick")

    one_loop: dict[Exponent, QuadraticGL] = {}
    for left in range(8):
        for right in range(8):
            square_accumulate(one_loop, hessian_entry(quartic, left, right))
    coefficient_d2 = one_loop.get(exponent_with({0: 2, 3: 2}), (0, 0, 0))
    coefficient_d1 = one_loop.get(exponent_with({0: 2, 1: 2}), (0, 0, 0))
    coefficient_d3 = one_loop.get(exponent_with({0: 2, 7: 2}), (0, 0, 0))
    coefficient_d0 = one_loop.get(exponent_with({0: 4}), (0, 0, 0))
    audit.check("distance-two exact engine", coefficient_d2 == (0, 0, 4), coefficient_d2, (0, 0, 4), "one_loop")
    audit.check("distance-one exact engine", coefficient_d1 == (0, 12, 71), coefficient_d1, (0, 12, 71), "one_loop")
    audit.check("distance-three exact engine", coefficient_d3 == (0, 0, 0), coefficient_d3, (0, 0, 0), "one_loop")
    audit.check("onsite exact engine", coefficient_d0 == (9, 54, Fraction(195, 2)), coefficient_d0, (9, 54, Fraction(195, 2)), "one_loop")
    audit.check("common-neighbour derivation", 2 * len(common_03) == 4, 2 * len(common_03), 4, "one_loop")
    audit.check("lambda-zero witness gone", coefficient_d2[0] == coefficient_d2[1] == 0, coefficient_d2, "only lambda^2", "one_loop")

    for phrase in (
        "`beta -> infinity` at each fixed `L`",
        "not a mass-gap result",
        "phasewise periodic OS reconstruction",
        "one pre-existing real-time dynamics",
        "distance-two `q_e^2q_f^2`",
        "physical empty space",
    ):
        audit.check(f"certificate boundary {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    for key, expected in (
        ("beta_first_symmetric_ground_equal_time_LRO", True),
        ("uniform_positive_full_finite_volume_gap_refuted", True),
        ("standard_4D_one_loop_g_lambda_basis_closure_refuted", True),
        ("distinct_infinite_volume_algebraic_ground_states", False),
        ("algebraic_KMS_for_preexisting_common_dynamics", False),
        ("ground_GNS_sector_gap", False),
        ("continuum_regulator_removal", False),
        ("physical_empty_space_reference", False),
        ("C6_advanced", False),
        ("Pre_A_complete", False),
    ):
        audit.check(f"scope {key}", manifest["scope"][key] is expected, manifest["scope"][key], expected, "scope")

    return {
        "schema": f"tect/{SLUG}-independent/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": PARENT_GATE,
        "negative_ids": list(NEGATIVE_IDS),
        "claim_bearing": False,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "finite_torus": constant_rows,
            "harmonic_rows": harmonic_rows,
            "ground_threshold_fixtures": ground_fixture_rows,
            "one_loop_coefficients_gl_basis": {
                "distance_2": [str(value) for value in coefficient_d2],
                "distance_1": [str(value) for value in coefficient_d1],
                "distance_3": [str(value) for value in coefficient_d3],
                "onsite_fourth": [str(value) for value in coefficient_d0],
            },
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000789 INDEPENDENT PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
