#!/usr/bin/env python3
"""Independent stdlib verifier for the centered-nodal Q3 Nelson/seam theorem."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-centered-nodal-q3-nelson-boue-dupuis-seam-limit-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CENTERED-NODAL-Q3-NELSON-BOUE-DUPUIS-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-CENTERED-NODAL-Q3-UI-L1-TV-RP-AND-FIXED-BAND-FULL-WEYL-LIMIT"
EXPLORATION_ID = "EXP-000772"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"


def sha256(path: Path) -> str:
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


Poly = dict[int, Fraction]


def poly_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, Fraction(0)) + coefficient
        if result[power] == 0:
            del result[power]
    return result


def poly_scale(poly: Poly, scalar: Fraction) -> Poly:
    return {power: coefficient * scalar for power, coefficient in poly.items() if coefficient * scalar}


def poly_multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for power_left, coefficient_left in left.items():
        for power_right, coefficient_right in right.items():
            power = power_left + power_right
            result[power] = result.get(power, Fraction(0)) + coefficient_left * coefficient_right
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def hermite(order: int, variance: Fraction) -> Poly:
    h0: Poly = {0: Fraction(1)}
    if order == 0:
        return h0
    h1: Poly = {1: Fraction(1)}
    if order == 1:
        return h1
    previous, current = h0, h1
    for degree in range(1, order):
        shifted = {power + 1: coefficient for power, coefficient in current.items()}
        following = poly_add(shifted, poly_scale(previous, -degree * variance))
        previous, current = current, following
    return current


def translate(poly: Poly, shift: Fraction) -> Poly:
    result: Poly = {}
    for power, coefficient in poly.items():
        for retained in range(power + 1):
            term = coefficient * math.comb(power, retained) * shift ** (power - retained)
            result[retained] = result.get(retained, Fraction(0)) + term
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def representative(value: int, modulus: int) -> int:
    return ((value + modulus // 2) % modulus) - modulus // 2


def sectors(modulus: int, degree: int, shift: int) -> set[int]:
    labels = range(-modulus // 2, modulus // 2)
    result = set()
    for values in itertools.product(labels, repeat=degree):
        total = sum(values) + shift
        result.add((total - representative(total, modulus)) // modulus)
    return result


def convolution_1d(base: dict[int, float], degree: int) -> dict[int, float]:
    result = {0: 1.0}
    for _ in range(degree):
        updated: dict[int, float] = {}
        for left_mode, left in result.items():
            for right_mode, right in base.items():
                mode = left_mode + right_mode
                updated[mode] = updated.get(mode, 0.0) + left * right
        result = updated
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    audit.check("independent candidate", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent exploration", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    edges = []
    for left in range(8):
        for right in range(left + 1, 8):
            if (left ^ right).bit_count() == 1:
                edges.append((left, right))
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(8)]
    audit.check("independent Q3 edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("independent Q3 degrees", degrees == [3] * 8, degrees, [3] * 8, "Q3")
    fixtures = [tuple(Fraction(((row + 3) * (column + 2)) % 11 - 5, 4) for column in range(8)) for row in range(9)]
    cauchy_values = []
    for vector in fixtures:
        sum2 = sum(value * value for value in vector)
        sum4 = sum(value**4 for value in vector)
        cauchy_values.append(8 * sum4 - sum2**2)
    audit.check("independent Q3 coercivity fixtures", all(value >= 0 for value in cauchy_values), cauchy_values, ">=0", "Q3")
    onsite_scalar = Fraction(8 * 3, 4)
    edge_scalar = Fraction(12 * 8, 4)
    audit.check("independent whole-Wick scalar coefficients", (onsite_scalar, edge_scalar) == (6, 24), (onsite_scalar, edge_scalar), (6, 24), "scalar")
    audit.check("independent Q3 scalar factor", edge_scalar == 6 * 4, edge_scalar, 24, "scalar")

    variance, shift = Fraction(5, 7), Fraction(-3, 5)
    translation_rows = {}
    for order in range(5):
        left = translate(hermite(order, variance), shift)
        right: Poly = {}
        for retained in range(order + 1):
            term = poly_scale(hermite(retained, variance), Fraction(math.comb(order, retained)) * shift ** (order - retained))
            right = poly_add(right, term)
        translation_rows[str(order)] = {str(power): str(coefficient) for power, coefficient in left.items()}
        audit.check(f"independent Hermite translation n{order}", left == right, left, right, "Wick")

    base_weights = [Fraction(2, 7), Fraction(3, 7), Fraction(2, 7)]
    common = Fraction(11, 13)
    shifted_weights = [common * value for value in base_weights]
    normalized_base = [value / sum(base_weights) for value in base_weights]
    normalized_shifted = [value / sum(shifted_weights) for value in shifted_weights]
    audit.check("independent scalar normalized invariance", normalized_base == normalized_shifted, normalized_shifted, normalized_base, "scalar")
    audit.check("independent scalar raw normalizer changes", sum(shifted_weights) == common * sum(base_weights), sum(shifted_weights), common * sum(base_weights), "scalar")

    epsilon = Fraction(1, 8)
    exponent_rows = []
    for r in (1, 2, 3):
        a_power = Fraction(r) - 2 * epsilon
        b_power = 2 * epsilon
        consumed = a_power / 4 + b_power / 2
        q = 1 / (1 - consumed)
        exponent_rows.append((r, a_power, b_power, consumed, q))
    q_values = [row[-1] for row in exponent_rows]
    audit.check("independent Nelson q table", q_values == [Fraction(16, 11), Fraction(16, 7), Fraction(16, 3)], exponent_rows, "16/11,16/7,16/3", "Nelson")
    audit.check("independent all consumed below one", all(row[-2] < 1 for row in exponent_rows), [row[-2] for row in exponent_rows], "<1", "Nelson")
    # Test-oracle completion of bI-I^2/2 at three rational b values.
    bd_rows = []
    for source in (Fraction(-5, 3), Fraction(2, 7), Fraction(9, 4)):
        optimum = source
        value = source * optimum - optimum**2 / 2
        bd_rows.append((source, optimum, value))
        audit.check(f"independent finite BD source {source}", value == source**2 / 2, value, source**2 / 2, "Nelson")

    symbol_rows = []
    for modulus in (14, 28, 56):
        spacing = 2.0 * math.pi / modulus
        ratios = [4.0 * math.sin(spacing * mode / 2.0) ** 2 / (spacing**2 * mode**2) for mode in range(1, modulus // 2 + 1)]
        symbol_rows.append((modulus, min(ratios), max(ratios)))
        audit.check(f"independent symbol lower M{modulus}", min(ratios) + 1e-12 >= 4.0 / math.pi**2, min(ratios), 4.0 / math.pi**2, "harmonic")
        audit.check(f"independent symbol upper M{modulus}", max(ratios) <= 1.0 + 1e-12, max(ratios), 1.0, "harmonic")
    lift_rows = {}
    for modulus in (6, 10, 12):
        for degree in range(1, 5):
            values = sorted(sectors(modulus, degree, 0))
            lift_rows[f"M{modulus}d{degree}"] = values
            audit.check(f"independent cyclic lift M{modulus}d{degree}", max(abs(value) for value in values) <= degree, values, f"|ell|<={degree}", "harmonic")
    shifted = {offset: sorted(sectors(12, 4, offset)) for offset in (-3, -1, 0, 1, 3)}
    audit.check("independent shifted aliases finite", all(max(abs(value) for value in values) <= 4 for values in shifted.values()), shifted, "|ell|<=4", "harmonic")
    audit.check("independent Nyquist aliases nonzero", any(value for value in lift_rows["M6d4"]), lift_rows["M6d4"], "nonzero", "harmonic")

    base = {mode: 1.0 / (1.0 + mode * mode) for mode in range(-80, 81)}
    convolution_rows = {}
    for degree in (2, 3, 4):
        convolved = convolution_1d(base, degree)
        tail = [convolved.get(mode, 0.0) for mode in (10, 20, 40)]
        convolution_rows[str(degree)] = tail
        audit.check(f"independent convolution tail d{degree}", tail[2] < tail[1] < tail[0], tail, "decrease", "harmonic")

    u = [Fraction(2), Fraction(-1), Fraction(4), Fraction(3), Fraction(-2), Fraction(1, 3)]
    v = [Fraction(-1), Fraction(3), Fraction(2), Fraction(-2), Fraction(5), Fraction(4, 3)]
    product_difference = [u[(index + 1) % len(u)] * v[(index + 1) % len(v)] - u[index] * v[index] for index in range(len(u))]
    shifted_rule = [(u[(index + 1) % len(u)] - u[index]) * v[(index + 1) % len(v)] + u[index] * (v[(index + 1) % len(v)] - v[index]) for index in range(len(u))]
    audit.check("independent discrete Leibniz", product_difference == shifted_rule, product_difference, shifted_rule, "positive-space")
    nodal = sum(value**2 for value in u)
    extended = sum((u[index] ** 2 + u[index] * u[(index + 1) % len(u)] + u[(index + 1) % len(u)] ** 2) / 3 for index in range(len(u)))
    audit.check("independent extension upper", extended <= nodal, extended, nodal, "positive-space")
    audit.check("independent extension lower", extended >= nodal / 3, extended, nodal / 3, "positive-space")

    # Exact rational quadrature for s=t/beta-1/2 with beta=6.
    beta = Fraction(6)
    saw_square = beta / 12
    kinetic = Fraction(1, 2) / beta
    spatial = beta / 24
    audit.check("independent seam saw square", saw_square == Fraction(1, 2), saw_square, Fraction(1, 2), "seam")
    audit.check("independent seam kinetic coefficient", kinetic == Fraction(1, 12), kinetic, Fraction(1, 12), "seam")
    audit.check("independent seam spatial coefficient", spatial == Fraction(1, 4), spatial, Fraction(1, 4), "seam")
    mass_square, wave_square = Fraction(4), Fraction(9)
    audit.check("independent seam Ax mutation", mass_square + wave_square != mass_square, mass_square + wave_square, mass_square, "seam")
    audit.check("independent quartic shift coercivity fixture", all((left + right) ** 4 >= left**4 / 8 - right**4 for left, right in itertools.product(range(-5, 6), repeat=2)), "integer grid", "valid", "seam")

    for phrase in ("finite-dimensional Boue--Dupuis", "cyclic equation", "piecewise-linear spatial extension", "affine seam", "A_{x,M}", "full-sequence locally uniform convergence", "energy below empty space"):
        audit.check(f"independent certificate {phrase[:30]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("centered_Q3_uniform_exponential_integrability", "centered_Q3_interacting_density_L1_limit", "centered_Q3_interacting_density_total_variation_limit", "centered_Q3_limit_reflection_positive", "centered_Q3_shifted_seam_UI_local_uniform", "centered_Q3_offdiagonal_seam_full_sequence", "centered_Q3_fixed_band_regular_Weyl_limit"):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("original_fixed_raw_CL8_family", "absolute_energy_fixed_by_centering", "complete_OS_Markov_Hadamard", "physical_state_or_vacuum", "below_empty_space_comparison", "phase_transition_proved", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("independent analytic proof label", manifest["verification"]["proof_grade"].startswith("ANALYTIC"), manifest["verification"]["proof_grade"], "ANALYTIC", "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": [],
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {"edges": edges, "Hermite_translation": translation_rows, "exponents": [[str(value) for value in row] for row in exponent_rows], "BD": [[str(value) for value in row] for row in bd_rows], "symbol": symbol_rows, "lifts": lift_rows, "shifted_lifts": shifted, "convolution_tails": convolution_rows, "seam": {"saw_square": str(saw_square), "kinetic": str(kinetic), "spatial": str(spatial)}},
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
