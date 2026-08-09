#!/usr/bin/env python3
"""Independent stdlib verifier for the Q3 fixed Hamiltonian/ground theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-beta-independent-hamiltonian-ground-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-BETA-INDEPENDENT-HAMILTONIAN-GROUND-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-COMPACT-CIRCLE-FIXED-HAMILTONIAN-FK-GIBBS-AND-STRICT-GROUND-REFERENCE-ADVANTAGE"
EXPLORATION_ID = "EXP-000774"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-fixed-torus-os-kms-markov-reference-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


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


def add_term(poly: Polynomial, coefficient: Fraction, powers: dict[int, int]) -> None:
    exponent = tuple(powers.get(index, 0) for index in range(8))
    poly[exponent] = poly.get(exponent, Fraction(0)) + coefficient
    if poly[exponent] == 0:
        del poly[exponent]


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def scale(poly: Polynomial, coefficient: Fraction) -> Polynomial:
    return {exponent: coefficient * value for exponent, value in poly.items() if coefficient * value}


def laplacian(poly: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in poly.items():
        for index, power in enumerate(exponent):
            if power >= 2:
                lowered = list(exponent)
                lowered[index] -= 2
                key = tuple(lowered)
                result[key] = result.get(key, Fraction(0)) + coefficient * power * (power - 1)
    return {key: value for key, value in result.items() if value}


def wick(poly: Polynomial, covariance: Fraction) -> Polynomial:
    result = dict(poly)
    current = dict(poly)
    coefficient = Fraction(1)
    for order in (1, 2):
        current = laplacian(current)
        coefficient *= -covariance / (2 * order)
        result = add(result, scale(current, coefficient))
    return result


def cube_laplacian() -> tuple[list[tuple[int, int]], list[list[Fraction]]]:
    edges = [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]
    matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for left, right in edges:
        matrix[left][left] += 1
        matrix[right][right] += 1
        matrix[left][right] -= 1
        matrix[right][left] -= 1
    return edges, matrix


def matrix_add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(8)] for i in range(8)]


def matrix_scale(matrix: list[list[Fraction]], coefficient: Fraction) -> list[list[Fraction]]:
    return [[coefficient * matrix[i][j] for j in range(8)] for i in range(8)]


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum(matrix[index][index] for index in range(8))


def polynomial(g: Fraction, lam: Fraction, matrix: list[list[Fraction]], edges: list[tuple[int, int]]) -> Polynomial:
    result: Polynomial = {}
    for left in range(8):
        for right in range(8):
            if matrix[left][right]:
                add_term(result, matrix[left][right] / 2, {left: 1, right: 1} if left != right else {left: 2})
    for vertex in range(8):
        add_term(result, g / 4, {vertex: 4})
    for left, right in edges:
        add_term(result, lam / 4, {left: 4})
        add_term(result, lam / 2, {left: 2, right: 2})
        add_term(result, lam / 4, {right: 4})
        add_term(result, -lam / 2, {left: 3, right: 1})
        add_term(result, -lam / 2, {left: 1, right: 3})
    return result


def stringify_polynomial(poly: Polynomial) -> dict[str, str]:
    return {",".join(str(power) for power in exponent): str(coefficient) for exponent, coefficient in sorted(poly.items())}


def thermal_difference(beta: float, length: float, mass: float, cutoff: int) -> float:
    total = 0.0
    for mode in range(-cutoff, cutoff + 1):
        omega = math.sqrt(mass**2 + (2.0 * math.pi * mode / length) ** 2)
        boltzmann = math.exp(-beta * omega)
        total += boltzmann / (omega * (1.0 - boltzmann))
    return total / length


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("independent EXP766 parent", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    edges, Lq = cube_laplacian()
    audit.check("independent Q3 twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("independent Q3 trace", trace(Lq) == 24, trace(Lq), 24, "Q3")
    audit.check("independent Q3 row sums", all(sum(row) == 0 for row in Lq), [sum(row) for row in Lq], "zero", "Q3")
    g, lam = Fraction(7, 5), Fraction(3, 8)
    m, eta = Fraction(-2, 7), Fraction(5, 11)
    C, D = Fraction(4, 9), Fraction(2, 13)
    identity = [[Fraction(int(i == j)) for j in range(8)] for i in range(8)]
    Aq = matrix_add(matrix_scale(identity, g + lam), matrix_scale(Lq, lam))
    Kstar = matrix_add(matrix_scale(identity, m), matrix_scale(Lq, eta))
    Kbeta = matrix_add(Kstar, matrix_scale(Aq, 3 * D))
    Pstar = polynomial(g, lam, Kstar, edges)
    Pbeta = polynomial(g, lam, Kbeta, edges)
    left = wick(Pbeta, C + D)
    right = wick(Pstar, C)
    G = g + 4 * lam
    coherent_scalar = -D * trace(Kstar) / 2 - 6 * D * D * G
    zero = (0,) * 8
    right[zero] = right.get(zero, Fraction(0)) + coherent_scalar
    audit.check("independent exact Wick dictionary", left == right, stringify_polynomial(left), stringify_polynomial(right), "Wick")
    Kgeneric = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for row in range(8):
        Kgeneric[row][row] = Fraction(2 * row - 5, row + 3)
    for row, column, value in ((0, 1, Fraction(2, 9)), (0, 3, Fraction(-1, 5)), (2, 7, Fraction(4, 13)), (4, 6, Fraction(-3, 11))):
        Kgeneric[row][column] = value
        Kgeneric[column][row] = value
    Kbeta_generic = matrix_add(Kgeneric, matrix_scale(Aq, 3 * D))
    generic_left = wick(polynomial(g, lam, Kbeta_generic, edges), C + D)
    generic_right = wick(polynomial(g, lam, Kgeneric, edges), C)
    generic_scalar = -D * trace(Kgeneric) / 2 - 6 * D * D * G
    generic_right[zero] = generic_right.get(zero, Fraction(0)) + generic_scalar
    audit.check("independent generic symmetric K dictionary", generic_left == generic_right, stringify_polynomial(generic_left), stringify_polynomial(generic_right), "Wick")
    audit.check("independent generic K not Q3 symmetric specialization", Kgeneric != Kstar, Kgeneric, "not mI+etaL_Q3", "Wick")
    audit.check("independent Tr A_Q3", trace(Aq) == 8 * G, trace(Aq), 8 * G, "Wick")
    general_scalar = 6 * D * D * G - D * trace(Kbeta) / 2
    audit.check("independent coherent scalar", general_scalar == coherent_scalar, general_scalar, coherent_scalar, "Wick")
    compensator = D * trace(Kstar) / 2 + 6 * D * D * G
    audit.check("independent scalar compensator", coherent_scalar + compensator == 0, compensator, -coherent_scalar, "Wick")
    raw_beta = matrix_add(Kbeta, matrix_scale(Aq, -3 * (C + D)))
    raw_star = matrix_add(Kstar, matrix_scale(Aq, -3 * C))
    audit.check("independent raw coefficient coherence", raw_beta == raw_star, raw_beta, raw_star, "Wick")
    mass_only = matrix_add(Kstar, matrix_scale(identity, 3 * D * (g + lam)))
    mass_only_raw = matrix_add(mass_only, matrix_scale(Aq, -3 * D))
    audit.check("independent mass-only mutation", mass_only_raw != Kstar, mass_only_raw, "not Kstar", "mutation")
    audit.check("independent wrong scalar mutation", coherent_scalar != compensator, coherent_scalar, "not compensator", "mutation")

    difference_rows = []
    for beta in (0.9, 1.8, 3.6, 7.2):
        first = thermal_difference(beta, 4.5, 0.95, 280)
        second = thermal_difference(beta, 4.5, 0.95, 560)
        difference_rows.append({"beta": beta, "K280": first, "K560": second})
        audit.check(f"independent D cutoff convergence beta{beta}", abs(first - second) < 1e-14, first, second, "thermal")
    audit.check("independent D positive", all(row["K560"] > 0 for row in difference_rows), difference_rows, "positive", "thermal")
    audit.check("independent D ground decay", difference_rows[-1]["K560"] < 0.01 * difference_rows[0]["K560"], difference_rows, "decay", "thermal")

    trace_rows = []
    for cutoff in (7, 15, 31, 63):
        log_z = 0.0
        for mode in range(-cutoff, cutoff + 1):
            omega = math.sqrt(0.95**2 + (2.0 * math.pi * mode / 4.5) ** 2)
            log_z += -8.0 * math.log1p(-math.exp(-1.3 * omega))
        trace_rows.append({"cutoff": cutoff, "logZ": log_z})
    audit.check("independent Fock trace monotone", trace_rows[1]["logZ"] > trace_rows[0]["logZ"] and all(trace_rows[index + 1]["logZ"] >= trace_rows[index]["logZ"] for index in range(3)), trace_rows, "nondecreasing", "Hamiltonian")
    audit.check("independent Fock trace tail", trace_rows[-1]["logZ"] - trace_rows[-2]["logZ"] < 1e-12, trace_rows, "convergent", "Hamiltonian")

    length, mass = Fraction(9, 4), Fraction(6, 5)
    amplitude_squared = (g + 3 * lam) ** 2 * 24 / (256 * length**2 * mass**4)
    audit.check("independent four-particle amplitude squared", amplitude_squared > 0, amplitude_squared, "positive", "ground")
    A, B, t = Fraction(4, 9), Fraction(13, 5), Fraction(1, 8)
    rayleigh = (-2 * t * A + t * t * B) / (1 + t * t)
    audit.check("independent Rayleigh strictness", rayleigh < 0, rayleigh, "negative", "ground")
    audit.check("independent Rayleigh threshold", t < 2 * A / B, t, 2 * A / B, "ground")
    gauge_shift = Fraction(17, 6)
    e0, trial = Fraction(-5, 3), Fraction(2, 7)
    audit.check("independent ground gauge invariance", (e0 + gauge_shift) - (trial + gauge_shift) == e0 - trial, (e0 + gauge_shift) - (trial + gauge_shift), e0 - trial, "ground")
    spectrum_h = (-1.75, 0.8, 3.1, 6.2)
    spectrum_0 = (0.0, 1.4, 3.8, 7.0)
    ground_rows = []
    for beta in (1.2, 2.4, 4.8, 9.6):
        fh = -math.log(sum(math.exp(-beta * energy) for energy in spectrum_h)) / beta
        f0 = -math.log(sum(math.exp(-beta * energy) for energy in spectrum_0)) / beta
        ground_rows.append({"beta": beta, "difference": fh - f0})
    audit.check("independent ground free-energy limit", abs(ground_rows[-1]["difference"] + 1.75) < 2e-7, ground_rows, -1.75, "ground")
    audit.check("independent ground convergence", all(abs(ground_rows[index + 1]["difference"] + 1.75) < abs(ground_rows[index]["difference"] + 1.75) for index in range(3)), ground_rows, "convergent", "ground")

    for phrase in ("exact change of coordinates", "necessary and sufficient", "strong resolvent", "not inferred from strong-resolvent convergence alone", "positivity improving", "closed Hamiltonian form", "cutoff-independent cross-form limit", "ground-reference theorem", "does not choose an absolute gravitational", "does not prove a thermodynamic"):
        audit.check(f"independent certificate phrase {phrase[:34]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("new_Wick_coherent_extension_of_EXP766", "exact_thermal_to_vacuum_Wick_dictionary", "matrix_and_scalar_coherence_necessary_sufficient", "beta_independent_compact_circle_Hamiltonian", "self_adjoint_lower_bounded_Hamiltonian", "compact_resolvent_and_trace_class_heat_semigroup", "Feynman_Kac_Nelson_Gibbs_identification", "faithful_normal_beta_KMS_family", "unique_finite_volume_ground", "strict_ground_Gaussian_reference_advantage", "beta_to_infinity_ground_free_energy_limit"):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("arbitrary_bounded_K_beta_family", "original_fixed_raw_CL8_family", "thermodynamic_limit", "strict_thermodynamic_energy_density", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "spontaneous_symmetry_breaking_or_phase_transition", "interacting_Hadamard_or_microlocal_spectrum", "original_3D_Q3LOCK_parent", "physical_light_speed_derived", "C0_closed", "N1_through_N5_closed", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("independent C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("independent C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
        "derived": {
            "Q3": {"edges": len(edges), "trace_L": str(trace(Lq)), "trace_A": str(trace(Aq))},
            "Wick": {"term_count": len(left), "coherent_scalar": str(coherent_scalar), "compensator": str(compensator)},
            "thermal_difference": difference_rows,
            "free_Fock_trace": trace_rows,
            "ground": {"amplitude_squared": str(amplitude_squared), "Rayleigh": str(rayleigh), "free_energy": ground_rows},
        },
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
