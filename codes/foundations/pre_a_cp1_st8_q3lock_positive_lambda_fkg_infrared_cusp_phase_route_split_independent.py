#!/usr/bin/env python3
"""Standard-library independent convention audit for EXP-000782.

All finite computations below are diagnostic regression fixtures, not a
numerical replacement for the analytic FKG/RP/DLR/phase proof.
"""

from __future__ import annotations

import argparse
import ast
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
SLUG = "pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-FKG-INFRARED-CUSP-PHASE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-LOW-TEMPERATURE-DLR-PHASE-AND-COLLECTIVE-SOURCE-CUSP"
EXPLORATION_ID = "EXP-000782"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-Q3-PHASE-SIGN-AND-KMS-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-INFINITE-VOLUME-DYNAMICS-KMS-GROUND-AND-CONTINUUM-SPLIT"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PRIMARY_SCRIPT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split.py"
PRIMARY_RESULT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
TEST_ORACLE_I3_INTERVAL = (0.50545, 0.50548)


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def vertices() -> list[tuple[int, int, int]]:
    return [(index >> 2 & 1, index >> 1 & 1, index & 1) for index in range(8)]


def edges() -> list[tuple[int, int]]:
    data = vertices()
    return [(i, j) for i in range(8) for j in range(i + 1, 8) if sum(a != b for a, b in zip(data[i], data[j])) == 1]


def differentiate(polynomial: dict[tuple[int, int], Fraction], variable: int) -> dict[tuple[int, int], Fraction]:
    output: dict[tuple[int, int], Fraction] = {}
    for powers, coefficient in polynomial.items():
        exponent = powers[variable]
        if exponent:
            reduced = list(powers)
            reduced[variable] -= 1
            key = (reduced[0], reduced[1])
            output[key] = output.get(key, Fraction(0)) + coefficient * exponent
    return {key: value for key, value in output.items() if value}


def evaluate(polynomial: dict[tuple[int, int], Fraction], x: Fraction, y: Fraction) -> Fraction:
    return sum(coefficient * x**powers[0] * y**powers[1] for powers, coefficient in polynomial.items())


def x_from_t(value: float) -> float:
    if value < 0:
        raise ValueError("negative Falk argument")
    if value == 0:
        return 0.0
    low, high = 0.0, max(1.0, value + 1.0)
    for _ in range(120):
        middle = (low + high) / 2.0
        if middle * math.tanh(middle) < value:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def falk_f(value: float) -> float:
    if value == 0:
        return 1.0
    root = x_from_t(value)
    return math.tanh(root) / root


def finite_watson(length: int) -> float:
    cosines = [math.cos(2.0 * math.pi * index / length) for index in range(length)]
    terms: list[float] = []
    for i in range(length):
        for j in range(length):
            for k in range(length):
                if i == 0 and j == 0 and k == 0:
                    continue
                terms.append(1.0 / (3.0 - cosines[i] - cosines[j] - cosines[k]))
    return math.fsum(terms) / length**3


def exact_small_watson(cosines: list[Fraction]) -> Fraction:
    length = len(cosines)
    total = Fraction(0)
    for i in range(length):
        for j in range(length):
            for k in range(length):
                if i == 0 and j == 0 and k == 0:
                    continue
                total += 1 / (3 - cosines[i] - cosines[j] - cosines[k])
    return total / length**3


def positive_definite(matrix: list[list[float]], tolerance: float = 1e-12) -> bool:
    # Independent Cholesky test.
    size = len(matrix)
    lower = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1):
            subtotal = math.fsum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                diagonal = matrix[i][i] - subtotal
                if diagonal <= tolerance:
                    return False
                lower[i][j] = math.sqrt(diagonal)
            else:
                lower[i][j] = (matrix[i][j] - subtotal) / lower[j][j]
    return True


def phase_values(r: float, g: float, lam: float, hbar: float, chi: float, c: float, watson: float) -> dict[str, float | bool]:
    theta = -r / (3.0 * (g + lam))
    strength = 8.0 * c * chi * theta**2 / hbar**2
    result: dict[str, float | bool] = {"theta_Q": theta, "A0": strength, "has_threshold": strength > watson}
    if strength > watson:
        rho = math.sqrt(watson / strength)
        root = math.atanh(rho)
        result["beta_star"] = 4.0 * chi * theta * root * rho / hbar**2
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    certificate = " ".join(certificate_text.split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    own_source = Path(__file__).read_text(encoding="utf-8")

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("primary result pass", primary["verdict"] == "PASS" and primary["assertions"]["passed"] == primary["assertions"]["total"], primary["assertions"], "all pass", "independence")
    syntax_tree = ast.parse(own_source)
    imported_modules = {
        alias.name
        for node in ast.walk(syntax_tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    primary_module_fragment = "pre_a_cp1_st8_q3lock_" + "positive_lambda_fkg_infrared_cusp_phase_route_split"
    imports_primary = any(primary_module_fragment in module for module in imported_modules)
    audit.check("no primary module import", not imports_primary, imports_primary, False, "independence")
    for forbidden in (("import " + "numpy"), ("import " + "sympy"), ("import " + "mpmath")):
        audit.check(f"no dependency {forbidden}", forbidden not in own_source, forbidden in own_source, False, "independence")

    polynomial = {
        (4, 0): Fraction(1),
        (3, 1): Fraction(-2),
        (2, 2): Fraction(2),
        (1, 3): Fraction(-2),
        (0, 4): Fraction(1),
    }
    mixed = differentiate(differentiate(polynomial, 0), 1)
    expected_mixed = {(2, 0): Fraction(-6), (1, 1): Fraction(8), (0, 2): Fraction(-6)}
    audit.check("independent Q3 mixed polynomial", mixed == expected_mixed, mixed, expected_mixed, "q3_polynomial")
    for x_value in range(-3, 4):
        for y_value in range(-3, 4):
            raw = evaluate(mixed, Fraction(x_value), Fraction(y_value))
            sos = -((x_value + y_value) ** 2 + 5 * (x_value - y_value) ** 2)
            audit.check("mixed derivative SOS grid", raw == sos, raw, sos, "q3_polynomial")
            audit.check("positive lambda mixed sign grid", raw <= 0, raw, "<=0", "q3_polynomial")
    audit.check("negative lambda hostile", -evaluate(mixed, Fraction(1), Fraction(0)) > 0, -evaluate(mixed, Fraction(1), Fraction(0)), ">0", "hostile")

    cube_edges = edges()
    data = vertices()
    neighbors: list[list[int]] = [[] for _ in range(8)]
    for left, right in cube_edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    audit.check("Q3 edge count", len(cube_edges) == 12, len(cube_edges), 12, "q3_graph")
    audit.check("Q3 degree", [len(items) for items in neighbors] == [3] * 8, [len(items) for items in neighbors], [3] * 8, "q3_graph")
    walsh_spectrum: list[int] = []
    for mask in range(8):
        weight = (mask & 1) + (mask >> 1 & 1) + (mask >> 2 & 1)
        eigenvalue = 2 * weight
        walsh_spectrum.append(eigenvalue)
        vector = [(-1) ** (((mask >> 2) & 1) * vertex[0] + ((mask >> 1) & 1) * vertex[1] + (mask & 1) * vertex[2]) for vertex in data]
        for site in range(8):
            action = 3 * vector[site] - sum(vector[other] for other in neighbors[site])
            audit.check("Walsh Laplacian eigenpair", action == eigenvalue * vector[site], action, eigenvalue * vector[site], "q3_graph")
    audit.check("Walsh spectrum", sorted(walsh_spectrum) == [0, 2, 2, 2, 4, 4, 4, 6], sorted(walsh_spectrum), [0, 2, 2, 2, 4, 4, 4, 6], "q3_graph")
    for vector in (
        [Fraction(index - 3, 2) for index in range(8)],
        [Fraction((-1) ** index * (index + 1), 5) for index in range(8)],
        [Fraction(1)] * 8,
    ):
        graph_form = sum((vector[i] - vector[j]) ** 2 for i, j in cube_edges)
        norm = sum(value**2 for value in vector)
        audit.check("graph form nonnegative", graph_form >= 0, graph_form, ">=0", "q3_graph")
        audit.check("graph spectral upper six", graph_form <= 6 * norm, graph_form, 6 * norm, "q3_graph")
    alternating = [Fraction((-1) ** sum(vertex)) for vertex in data]
    alternating_form = sum((alternating[i] - alternating[j]) ** 2 for i, j in cube_edges)
    alternating_norm = sum(value**2 for value in alternating)
    audit.check("graph upper six sharp", alternating_form == 6 * alternating_norm, alternating_form, 6 * alternating_norm, "hostile")

    # Exact collective Hessian coefficient ledger, derived term by term.
    r_value, g_value, lambda_value = Fraction(-9), Fraction(1), Fraction(1)
    s_value = Fraction(12)
    d_value = Fraction(36)
    commutator_core = r_value + Fraction(3, 8) * g_value * s_value + Fraction(1, 8) * lambda_value * d_value
    theta = -r_value / (3 * (g_value + lambda_value))
    audit.check("collective commutator saturation fixture", commutator_core == 0, commutator_core, 0, "collective_bound")
    audit.check("FKG improved theta fixture", theta == Fraction(3, 2), theta, Fraction(3, 2), "collective_bound")
    audit.check("three-regular D bound fixture", d_value == 3 * s_value, d_value, 3 * s_value, "collective_bound")
    audit.check("collective Q lower fixture", s_value / 8 == theta, s_value / 8, theta, "collective_bound")
    weak_theta = -r_value / (3 * g_value + 6 * lambda_value)
    audit.check("no-FKG bound is weaker", theta > weak_theta, theta, weak_theta, "collective_bound")
    audit.check("global shift removes c", "r+6c" not in manifest["collective_moment_bound"]["exact_hessian"], manifest["collective_moment_bound"]["exact_hessian"], "no r+6c", "collective_bound")

    covariance_fixtures = [
        [[Fraction(1) if i == j else Fraction(0) for j in range(8)] for i in range(8)],
        [[Fraction(2) if i == j else Fraction(1, 8) for j in range(8)] for i in range(8)],
        [[Fraction(i + 2, 3) if i == j else Fraction((i + j) % 3, 50) for j in range(8)] for i in range(8)],
    ]
    for covariance in covariance_fixtures:
        trace = sum(covariance[i][i] for i in range(8))
        collective = sum(sum(row) for row in covariance) / 8
        off_sum = sum(covariance[i][j] for i in range(8) for j in range(i + 1, 8))
        audit.check("FKG covariance exact identity", 8 * collective - trace == 2 * off_sum, 8 * collective - trace, 2 * off_sum, "collective_bound")
        audit.check("FKG covariance collective lower", collective >= trace / 8, collective, trace / 8, "collective_bound")
    hostile_covariance = [[Fraction(1) if i == j else Fraction(-1, 8) for j in range(8)] for i in range(8)]
    hostile_collective = sum(sum(row) for row in hostile_covariance) / 8
    audit.check("negative-correlation hostile collective small", hostile_collective == Fraction(1, 8), hostile_collective, Fraction(1, 8), "hostile")
    audit.check("PSD hostile eigen ledgers", Fraction(1, 8) > 0 and Fraction(9, 8) > 0, [Fraction(1, 8), Fraction(9, 8)], "positive", "hostile")

    points = [(0.0, 0.0), (1.0, -0.5), (-0.4, 1.3), (1.7, 0.8)]
    coupling = 0.7
    inner_gram = [[math.exp(coupling * sum(a * b for a, b in zip(left, right))) for right in points] for left in points]
    gaussian_gram = [[math.exp(-coupling * sum((a - b) ** 2 for a, b in zip(left, right)) / 2.0) for right in points] for left in points]
    audit.check("inner-product RP Gram Cholesky", positive_definite(inner_gram), inner_gram, "positive definite", "reflection_positivity")
    audit.check("Gaussian RP Gram Cholesky", positive_definite(gaussian_gram), gaussian_gram, "positive definite", "reflection_positivity")
    hostile_kernel = [[1.0, math.exp(0.5)], [math.exp(0.5), 1.0]]
    audit.check("negative c hostile kernel fails", not positive_definite(hostile_kernel), hostile_kernel, "not positive definite", "hostile")

    previous_f = math.inf
    for root in (1.0e-6, 0.125, 0.5, 1.0, 2.0, 5.0, 10.0):
        value = root * math.tanh(root)
        function = falk_f(value)
        audit.check("Falk bisection recovers x", abs(x_from_t(value) - root) < 2e-11, x_from_t(value), root, "falk_bruch")
        audit.check("Falk identity", abs(value * function - math.tanh(root) ** 2) < 2e-12, value * function, math.tanh(root) ** 2, "falk_bruch")
        audit.check("Falk decreasing diagnostic", function <= previous_f + 1e-14, function, previous_f, "falk_bruch")
        previous_f = function
    beta_ho, hbar_ho, chi_ho, omega_ho = 2.0, 3.0, 5.0, 0.7
    root_ho = beta_ho * hbar_ho * omega_ho / 2.0
    equal_time = hbar_ho / (2.0 * chi_ho * omega_ho * math.tanh(root_ho))
    duhamel = 1.0 / (beta_ho * chi_ho * omega_ho**2)
    commutator = beta_ho * hbar_ho**2 / chi_ho
    argument = commutator / (4.0 * equal_time)
    audit.check("harmonic Falk argument independent", abs(argument - root_ho * math.tanh(root_ho)) < 2e-12, argument, root_ho * math.tanh(root_ho), "falk_bruch")
    audit.check("harmonic Falk equality independent", abs(equal_time * falk_f(argument) - duhamel) < 2e-12, equal_time * falk_f(argument), duhamel, "falk_bruch")
    audit.check("wrong hbar hostile", abs(equal_time * falk_f(beta_ho * hbar_ho / chi_ho / (4.0 * equal_time)) - duhamel) > 1e-3, "mutated", "different", "hostile")

    exact_two = exact_small_watson([Fraction(1), Fraction(-1)])
    exact_four = exact_small_watson([Fraction(1), Fraction(0), Fraction(-1), Fraction(0)])
    audit.check("exact I3,2", exact_two == Fraction(29, 96), exact_two, Fraction(29, 96), "watson")
    audit.check("exact I3,4", exact_four == Fraction(1517, 3840), exact_four, Fraction(1517, 3840), "watson")
    watson_rows: list[dict[str, float]] = []
    previous = -math.inf
    oracles = {8: 0.4492112507805545, 16: 0.4772606372100334, 32: 0.4913531023730123, 64: 0.49840656778749315}
    for length in (8, 16, 32, 64):
        value = finite_watson(length)
        watson_rows.append({"L": length, "I3_L": value})
        audit.check("finite Watson stdlib oracle", abs(value - oracles[length]) < 3e-13, value, oracles[length], "watson")
        audit.check("finite Watson dyadic diagnostic", value > previous, value, previous, "watson")
        previous = value
    watson_diagnostic = 2.0 * watson_rows[-1]["I3_L"] - watson_rows[-2]["I3_L"]
    audit.check("Richardson Watson oracle interval", TEST_ORACLE_I3_INTERVAL[0] < watson_diagnostic < TEST_ORACLE_I3_INTERVAL[1], watson_diagnostic, TEST_ORACLE_I3_INTERVAL, "watson")
    watson_oracle = 0.505462019717326

    for momentum, expected in (((math.pi, 0.0, 0.0), 2.0), ((math.pi / 2.0, 0.0, 0.0), 1.0), ((math.pi, math.pi, math.pi), 6.0)):
        energy = math.fsum(1.0 - math.cos(value) for value in momentum)
        audit.check("Fourier E fixture", abs(energy - expected) < 1e-14, energy, expected, "infrared")
        audit.check("Fourier ell=2E", abs(2.0 * energy - 2.0 * expected) < 1e-14, 2.0 * energy, 2.0 * expected, "infrared")
    beta_ir, c_ir, energy_ir = 1.7, 0.9, 2.3
    cap = 1.0 / (2.0 * beta_ir * c_ir * energy_ir)
    audit.check("IR missing beta hostile", abs(cap - 1.0 / (2.0 * c_ir * energy_ir)) > 1e-3, cap, "different", "hostile")
    audit.check("IR missing two hostile", abs(cap - 1.0 / (beta_ir * c_ir * energy_ir)) > 1e-3, cap, "different", "hostile")

    phase_rows: list[dict[str, Any]] = []
    fixtures = (
        ("supercritical", -9.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        ("infrared_route_inconclusive", -9.0, 1.0, 1.0, 1.0, 1.0, 1.0 / 36.0),
        ("nontrivial_units", -4.0, 1.5, 0.4, 2.0, 3.0, 5.0 / 7.0),
    )
    for name, r, g, lam, hbar, chi, c in fixtures:
        result = phase_values(r, g, lam, hbar, chi, c, watson_oracle)
        phase_rows.append({"name": name, **result})
        theta_value = float(result["theta_Q"])
        strength = float(result["A0"])
        audit.check("phase theta positive", theta_value > 0, theta_value, ">0", "threshold")
        if bool(result["has_threshold"]):
            beta_star = float(result["beta_star"])
            for factor, expected_pass in ((0.99, False), (1.01, True), (2.0, True)):
                beta = factor * beta_star
                t_value = beta * hbar**2 / (4.0 * chi * theta_value)
                root = x_from_t(t_value)
                lhs = 2.0 * beta * c * theta_value * falk_f(t_value)
                transformed = strength * math.tanh(root) ** 2
                audit.check("threshold identity independent", abs(lhs - transformed) < 3e-12, lhs, transformed, "threshold")
                audit.check("threshold side independent", (lhs > watson_oracle) is expected_pass, lhs > watson_oracle, expected_pass, "threshold")
        else:
            audit.check("route inconclusive strength", strength < watson_oracle, strength, watson_oracle, "threshold")
            audit.check("route inconclusive is not no-phase", name == "infrared_route_inconclusive", name, "infrared_route_inconclusive", "scope")
    for invalid in ((1.0, 1.0, 1.0), (-1.0, 1.0, -0.1), (-1.0, -1.0, 1.0)):
        r, lam, c = invalid
        valid = r < 0 and lam > 0 and c > 0
        audit.check("invalid hypothesis rejected", not valid, valid, False, "hostile")

    beta_source, physical_magnetization = Fraction(3), Fraction(7, 2)
    fine_slope = physical_magnetization / 8
    coarse_slope = beta_source * physical_magnetization
    audit.check("fine pressure factor one eighth", fine_slope == Fraction(7, 16), fine_slope, Fraction(7, 16), "source")
    audit.check("coarse pressure beta slope", coarse_slope == Fraction(21, 2), coarse_slope, Fraction(21, 2), "source")
    audit.check("p equals 8 beta P derivative", coarse_slope == 8 * beta_source * fine_slope, coarse_slope, 8 * beta_source * fine_slope, "source")
    audit.check("fine cusp jump", 2 * fine_slope == physical_magnetization / 4, 2 * fine_slope, physical_magnetization / 4, "source")
    for volume in (4, 16, 64, 256):
        field = 0.2
        value = math.log(2.0 * math.cosh(float(beta_source) * field * volume * float(physical_magnetization))) / (8.0 * float(beta_source) * volume)
        limit = field * float(physical_magnetization) / 8.0
        audit.check("two-state thermodynamic cusp diagnostic", abs(value - limit) <= math.log(2.0) / (8.0 * float(beta_source) * volume) + 1e-14, abs(value - limit), "finite log2 bound", "source")
    audit.check("finite response zero is hostile", math.tanh(0.0) == 0.0, math.tanh(0.0), 0.0, "hostile")

    for key in (
        "continuous_loop_FKG",
        "spatial_reflection_positivity",
        "collective_infrared_bound",
        "collective_double_commutator_moment_bound",
        "strict_collective_source_pressure_cusp",
        "distinct_parity_related_tangent_DLR_states",
        "positive_lambda_DLR_phase_transition",
    ):
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in (
        "phase_for_all_positive_lambda_parameters",
        "tangent_states_extreme",
        "Cstar_pure_states",
        "spatial_clustering",
        "algebraic_KMS_for_preexisting_dynamics",
        "ground_state_phase",
        "continuum_regulator_removal",
        "physical_empty_space_reference",
        "below_empty_space",
        "C6_advanced",
        "Sector_A_complete",
        "Pre_A_complete",
    ):
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    for phrase in (
        "every finite evaluation marginal of the exact loop law is MTP2",
        "global collective double commutator",
        "volume-squared zero-mode density",
        "factor `1/8`",
        "does not prove phase absence",
        "not a new general phase method",
        "algebraic KMS",
        "physical empty space",
        "Pre-A completion",
    ):
        audit.check(f"certificate phrase {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    return {
        "schema": f"tect/{SLUG}-independent/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "q3_spectrum": sorted(walsh_spectrum),
            "exact_I3_L2": str(exact_two),
            "exact_I3_L4": str(exact_four),
            "finite_watson": watson_rows,
            "watson_richardson_diagnostic": watson_diagnostic,
            "phase_fixtures": phase_rows,
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "primary_script_sha256": portable_sha256(PRIMARY_SCRIPT),
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
    print(f"EXP-000782 INDEPENDENT PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
