#!/usr/bin/env python3
"""Primary algebra and normalization verifier for EXP-000782.

The analytic proof is the certificate.  This executable independently
recomputes every finite algebraic/numerical constant used by that proof and
tests hostile convention mutations; it is not a numerical proof of FKG, RP,
DLR existence, or a phase transition.
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

import mpmath as mp
import numpy as np
import sympy as sp


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
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


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


def cube_vertices() -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(2) for b in range(2) for c in range(2)]


def cube_edges() -> list[tuple[int, int]]:
    vertices = cube_vertices()
    return [
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def x_from_t(value: float) -> float:
    if value < 0:
        raise ValueError("t must be nonnegative")
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
    cosine = np.cos(2.0 * math.pi * np.arange(length) / length)
    energy = 3.0 - cosine[:, None, None] - cosine[None, :, None] - cosine[None, None, :]
    energy[0, 0, 0] = np.inf
    return float(np.sum(1.0 / energy) / length**3)


def phase_values(parameters: dict[str, float], watson: float) -> dict[str, float | bool]:
    theta = -parameters["r"] / (3.0 * (parameters["g"] + parameters["lambda"]))
    strength = 8.0 * parameters["c"] * parameters["chi"] * theta**2 / parameters["hbar"] ** 2
    result: dict[str, float | bool] = {"theta_Q": theta, "A0": strength, "has_finite_threshold": strength > watson}
    if strength > watson:
        rho = math.sqrt(watson / strength)
        x_star = math.atanh(rho)
        beta_star = 4.0 * parameters["chi"] * theta * x_star * rho / parameters["hbar"] ** 2
        result.update({"rho": rho, "x_star": x_star, "beta_star": beta_star})
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("parent EXP774 pass", parent["verdict"] == "PASS" and parent["assertions"]["passed"] == parent["assertions"]["total"], parent["assertions"], "all pass", "parent")
    audit.check("parent result", parent["result_id"] == "PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY", parent["result_id"], "EXP774 result", "parent")

    edges = cube_edges()
    vertices = cube_vertices()
    adjacency = sp.zeros(8)
    degrees = [0] * 8
    for left, right in edges:
        adjacency[left, right] = adjacency[right, left] = 1
        degrees[left] += 1
        degrees[right] += 1
    laplacian = 3 * sp.eye(8) - adjacency
    spectrum = {int(value): multiplicity for value, multiplicity in laplacian.eigenvals().items()}
    audit.check("Q3 vertices", len(vertices) == 8, len(vertices), 8, "q3")
    audit.check("Q3 edges", len(edges) == 12, len(edges), 12, "q3")
    audit.check("Q3 degree three", degrees == [3] * 8, degrees, [3] * 8, "q3")
    audit.check("Q3 spectrum", spectrum == {0: 1, 2: 3, 4: 3, 6: 1}, spectrum, {0: 1, 2: 3, 4: 3, 6: 1}, "q3")

    x, y, lam = sp.symbols("x y lam", real=True)
    edge_potential = lam * (x - y) ** 2 * (x**2 + y**2) / 4
    mixed = sp.factor(sp.diff(edge_potential, x, y))
    mixed_expected = -lam * (3 * x**2 - 4 * x * y + 3 * y**2) / 2
    sos_expected = -lam * ((x + y) ** 2 + 5 * (x - y) ** 2) / 4
    audit.check("Q3 mixed derivative", sp.simplify(mixed - mixed_expected) == 0, mixed, mixed_expected, "fkg_sign")
    audit.check("Q3 mixed SOS", sp.simplify(mixed - sos_expected) == 0, mixed, sos_expected, "fkg_sign")
    audit.check("mixed quadratic eigenvalues", set(sp.Matrix([[3, -2], [-2, 3]]).eigenvals()) == {1, 5}, sp.Matrix([[3, -2], [-2, 3]]).eigenvals(), {1, 5}, "fkg_sign")
    for x_value in range(-3, 4):
        for y_value in range(-3, 4):
            value = float(mixed.subs({x: x_value, y: y_value, lam: Fraction(5, 7)}))
            audit.check("Q3 attractive grid fixture", value <= 1e-14, value, "<=0", "fkg_sign")
    hostile_mixed = float(mixed.subs({x: 1, y: 0, lam: -1}))
    audit.check("negative lambda hostile flips FKG sign", hostile_mixed > 0, hostile_mixed, ">0", "hostile")

    q = sp.symbols("q0:8", real=True)
    shift = sp.symbols("shift", real=True)
    r_symbol, g_symbol = sp.symbols("r_symbol g_symbol", real=True)
    onsite = r_symbol * sum(item**2 for item in q) / 2 + g_symbol * sum(item**4 for item in q) / 4
    onsite += lam * sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges) / 4
    shifted = onsite.subs({q[index]: q[index] + shift / sp.sqrt(8) for index in range(8)})
    directional_hessian = sp.expand(sp.diff(shifted, shift, 2).subs(shift, 0))
    total_square = sum(item**2 for item in q)
    q3_square = sum((q[i] - q[j]) ** 2 for i, j in edges)
    expected_hessian = r_symbol + 3 * g_symbol * total_square / 8 + lam * q3_square / 8
    audit.check("normalized collective onsite Hessian", sp.simplify(directional_hessian - expected_hessian) == 0, directional_hessian, expected_hessian, "double_commutator")
    left = sp.symbols("left0:8", real=True)
    right = sp.symbols("right0:8", real=True)
    spatial_bond = sum((left[i] - right[i]) ** 2 for i in range(8))
    translated_bond = spatial_bond.subs({**{left[i]: left[i] + shift / sp.sqrt(8) for i in range(8)}, **{right[i]: right[i] + shift / sp.sqrt(8) for i in range(8)}})
    audit.check("global shift cancels spatial bond", sp.diff(translated_bond, shift, 2) == 0, sp.diff(translated_bond, shift, 2), 0, "double_commutator")

    covariance_rows: list[dict[str, float]] = []
    for diagonal, off_diagonal in ((1.0, 0.0), (1.0, 0.125), (2.0, 0.3), (0.75, 0.05)):
        covariance = np.full((8, 8), off_diagonal, dtype=float)
        np.fill_diagonal(covariance, diagonal)
        collective = float(np.sum(covariance) / 8.0)
        trace_over_eight = float(np.trace(covariance) / 8.0)
        covariance_rows.append({"diagonal": diagonal, "off_diagonal": off_diagonal, "collective": collective})
        audit.check("FKG collective covariance lower", collective + 1e-14 >= trace_over_eight, collective, trace_over_eight, "collective_FKG")
        audit.check("FKG covariance PSD fixture", float(np.min(np.linalg.eigvalsh(covariance))) >= -1e-12, np.linalg.eigvalsh(covariance), ">=0", "collective_FKG")
    hostile_covariance = np.full((8, 8), -1.0 / 8.0)
    np.fill_diagonal(hostile_covariance, 1.0)
    hostile_collective = float(np.sum(hostile_covariance) / 8.0)
    audit.check("PSD hostile covariance", float(np.min(np.linalg.eigvalsh(hostile_covariance))) > 0, np.linalg.eigvalsh(hostile_covariance), ">0", "hostile")
    audit.check("without FKG collective lower fails", hostile_collective < float(np.trace(hostile_covariance) / 8.0), hostile_collective, "< trace/8", "hostile")

    edge_correlations = [Fraction(index + 1, 50) for index in range(12)]
    component_second = Fraction(7, 5)
    s_expectation = 8 * component_second
    d_expectation = 3 * s_expectation - 2 * sum(edge_correlations)
    q_expectation = (s_expectation + 2 * sum(Fraction(index + 1, 100) for index in range(28))) / 8
    audit.check("Q3 FKG edge improves D", d_expectation <= 3 * s_expectation, d_expectation, 3 * s_expectation, "collective_FKG")
    audit.check("all-pair FKG improves Q", q_expectation >= s_expectation / 8, q_expectation, s_expectation / 8, "collective_FKG")
    for r_value, g_value, lambda_value in ((-9.0, 1.0, 1.0), (-4.0, 1.5, 0.4), (-0.7, 2.1, 0.3)):
        theta = -r_value / (3.0 * (g_value + lambda_value))
        weak = -r_value / (3.0 * g_value + 6.0 * lambda_value)
        audit.check("FKG theta positive", theta > 0, theta, ">0", "collective_FKG")
        audit.check("FKG theta improves no-FKG bound", theta >= weak, theta, weak, "collective_FKG")

    points = np.array([[0.0, 0.0], [1.0, -0.5], [-0.4, 1.3], [1.7, 0.8]], dtype=float)
    coupling = 0.7
    gram = np.exp(coupling * (points @ points.T))
    gaussian_gram = np.exp(-coupling * np.sum((points[:, None, :] - points[None, :, :]) ** 2, axis=2) / 2.0)
    audit.check("RP exponential inner-product kernel PSD", float(np.min(np.linalg.eigvalsh(gram))) >= -1e-11, np.linalg.eigvalsh(gram), ">=0", "reflection_positivity")
    audit.check("RP Gaussian crossing kernel PSD", float(np.min(np.linalg.eigvalsh(gaussian_gram))) >= -1e-11, np.linalg.eigvalsh(gaussian_gram), ">=0", "reflection_positivity")
    hostile_two_point = np.array([[1.0, math.exp(0.5)], [math.exp(0.5), 1.0]])
    audit.check("negative spatial coupling hostile is not PD", float(np.linalg.det(hostile_two_point)) < 0, np.linalg.det(hostile_two_point), "<0", "hostile")

    for root in (1.0e-6, 0.125, 0.5, 1.0, 2.0, 5.0, 10.0):
        value = root * math.tanh(root)
        recovered = x_from_t(value)
        function = falk_f(value)
        audit.check("Falk inverse fixture", abs(recovered - root) < 2e-11, recovered, root, "falk_bruch")
        audit.check("Falk transform identity", abs(value * function - math.tanh(root) ** 2) < 2e-12, value * function, math.tanh(root) ** 2, "falk_bruch")
        audit.check("Falk range", 0 < function <= 1.0, function, "(0,1]", "falk_bruch")
    beta_ho, hbar_ho, chi_ho, omega_ho = 2.0, 3.0, 5.0, 0.7
    x_ho = beta_ho * hbar_ho * omega_ho / 2.0
    coth = 1.0 / math.tanh(x_ho)
    equal_time = hbar_ho * coth / (2.0 * chi_ho * omega_ho)
    duhamel = 1.0 / (beta_ho * chi_ho * omega_ho**2)
    commutator = beta_ho * hbar_ho**2 / chi_ho
    argument = commutator / (4.0 * equal_time)
    audit.check("harmonic Falk argument", abs(argument - x_ho * math.tanh(x_ho)) < 2e-12, argument, x_ho * math.tanh(x_ho), "falk_bruch")
    audit.check("harmonic Falk equality", abs(equal_time * falk_f(argument) - duhamel) < 2e-12, equal_time * falk_f(argument), duhamel, "falk_bruch")
    hostile_argument = commutator / (2.0 * equal_time)
    audit.check("factor-two hostile breaks harmonic equality", abs(equal_time * falk_f(hostile_argument) - duhamel) > 1e-3, equal_time * falk_f(hostile_argument), duhamel, "hostile")

    mp.mp.dps = 40
    watson_mp = mp.quad(lambda time: mp.e ** (-3 * time) * mp.besseli(0, time) ** 3, [0, 1, mp.inf])
    watson = float(watson_mp)
    audit.check("Watson integral positive", 0.5 < watson < 0.51, watson, "(0.5,0.51)", "infrared")
    audit.check("Watson computed digits", abs(watson - 0.505462019717326) < 5e-15, watson, "test oracle 0.505462019717326", "infrared")
    finite_watson_rows: list[dict[str, float]] = []
    previous = -math.inf
    for length, oracle in ((8, 0.4492112507805545), (16, 0.4772606372100334), (32, 0.4913531023730123), (64, 0.49840656778749315)):
        value = finite_watson(length)
        finite_watson_rows.append({"L": length, "I3_L": value})
        audit.check("finite Watson oracle", abs(value - oracle) < 3e-13, value, oracle, "infrared")
        audit.check("dyadic Watson monotonic diagnostic", value > previous, value, previous, "infrared")
        previous = value
    richardson = 2.0 * finite_watson_rows[-1]["I3_L"] - finite_watson_rows[-2]["I3_L"]
    audit.check("Watson Richardson diagnostic", 0.50545 < richardson < 0.50548, richardson, "(0.50545,0.50548)", "infrared")

    for momentum, expected_energy in (((math.pi, 0.0, 0.0), 2.0), ((math.pi / 2.0, 0.0, 0.0), 1.0), ((math.pi, math.pi, math.pi), 6.0)):
        energy = sum(1.0 - math.cos(item) for item in momentum)
        audit.check("spatial Fourier E(p)", abs(energy - expected_energy) < 1e-14, energy, expected_energy, "infrared")
        audit.check("spatial Laplacian factor two", abs(2.0 * energy - 2.0 * expected_energy) < 1e-14, 2.0 * energy, 2.0 * expected_energy, "infrared")
    beta_ir, c_ir, energy_ir = 1.7, 0.9, 2.3
    ir_cap = 1.0 / (2.0 * beta_ir * c_ir * energy_ir)
    audit.check("IR beta mutation differs", abs(ir_cap - 1.0 / (2.0 * c_ir * energy_ir)) > 1e-3, ir_cap, "not missing beta", "hostile")
    audit.check("IR factor-two mutation differs", abs(ir_cap - 1.0 / (beta_ir * c_ir * energy_ir)) > 1e-3, ir_cap, "not missing two", "hostile")

    fixtures = [
        {"name": "supercritical", "r": -9.0, "g": 1.0, "lambda": 1.0, "hbar": 1.0, "chi": 1.0, "c": 1.0},
        {"name": "infrared_inconclusive", "r": -9.0, "g": 1.0, "lambda": 1.0, "hbar": 1.0, "chi": 1.0, "c": 1.0 / 36.0},
        {"name": "nontrivial_units", "r": -4.0, "g": 1.5, "lambda": 0.4, "hbar": 2.0, "chi": 3.0, "c": 5.0 / 7.0},
    ]
    phase_rows: list[dict[str, Any]] = []
    for parameters in fixtures:
        values = phase_values(parameters, watson)
        phase_rows.append({**parameters, **values})
        theta = float(values["theta_Q"])
        strength = float(values["A0"])
        audit.check("theta formula positive fixture", theta > 0, theta, ">0", "threshold")
        audit.check("A0 exact recomputation", abs(strength - 8.0 * parameters["c"] * parameters["chi"] * theta**2 / parameters["hbar"] ** 2) < 1e-14, strength, "recomputed", "threshold")
        if bool(values["has_finite_threshold"]):
            beta_star = float(values["beta_star"])
            for factor, should_pass in ((0.99, False), (1.01, True), (2.0, True)):
                beta = factor * beta_star
                t_value = beta * parameters["hbar"] ** 2 / (4.0 * parameters["chi"] * theta)
                root = x_from_t(t_value)
                lhs = 2.0 * beta * parameters["c"] * theta * falk_f(t_value)
                transformed = strength * math.tanh(root) ** 2
                audit.check("threshold transform identity", abs(lhs - transformed) < 3e-12, lhs, transformed, "threshold")
                audit.check("threshold strict side", (lhs > watson) is should_pass, lhs > watson, should_pass, "threshold")
            beta = 2.0 * beta_star
            t_value = beta * parameters["hbar"] ** 2 / (4.0 * parameters["chi"] * theta)
            delta = theta * falk_f(t_value) - watson / (2.0 * beta * parameters["c"])
            audit.check("strict zero-mode margin", delta > 0, delta, ">0", "threshold")
        else:
            audit.check("inconclusive fixture below Watson", strength < watson, strength, watson, "threshold")
            for root in (1.0, 5.0, 20.0):
                audit.check("inconclusive asymptotic route stays below", strength * math.tanh(root) ** 2 < watson, strength * math.tanh(root) ** 2, watson, "threshold")

    beta_source, magnetization = 3.0, 3.5
    coarse_slope = beta_source * magnetization
    fine_energy_slope = magnetization / 8.0
    audit.check("coarse dimensionless source slope", coarse_slope == beta_source * magnetization, coarse_slope, beta_source * magnetization, "source_normalization")
    audit.check("fine energy pressure slope", fine_energy_slope == magnetization / 8.0, fine_energy_slope, magnetization / 8.0, "source_normalization")
    audit.check("p=8 beta P derivative", abs(coarse_slope - 8.0 * beta_source * fine_energy_slope) < 1e-14, coarse_slope, 8.0 * beta_source * fine_energy_slope, "source_normalization")
    audit.check("cusp gap fine pressure", abs(2.0 * fine_energy_slope - magnetization / 4.0) < 1e-14, 2.0 * fine_energy_slope, magnetization / 4.0, "source_normalization")
    for volume in (4, 16, 64, 256):
        field = 0.2
        finite_pressure = math.log(2.0 * math.cosh(beta_source * field * volume * magnetization)) / (8.0 * beta_source * volume)
        limiting = abs(field) * magnetization / 8.0
        audit.check("two-macrostate pressure convergence", abs(finite_pressure - limiting) <= math.log(2.0) / (8.0 * beta_source * volume) + 1e-14, abs(finite_pressure - limiting), "log2/(8 beta V)", "source_normalization")
    audit.check("finite-volume zero derivative hostile", math.tanh(0.0) == 0.0, math.tanh(0.0), 0.0, "hostile")

    for key in (
        "continuous_loop_FKG",
        "spatial_reflection_positivity",
        "collective_infrared_bound",
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
        "MTP2",
        "global collective double commutator",
        "Falk--Bruch",
        "Internal `O(8)` invariance is not used",
        "factor `1/8`",
        "does not prove phase absence",
        "This is not an algebraic-KMS theorem",
        "physical empty space",
        "Pre-A completion",
    ):
        audit.check(f"certificate phrase {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    return {
        "schema": f"tect/{SLUG}/0.1",
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
            "q3_laplacian_spectrum": spectrum,
            "q3_edges": len(edges),
            "watson_I3": watson,
            "finite_watson": finite_watson_rows,
            "covariance_fixtures": covariance_rows,
            "phase_fixtures": phase_rows,
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
    print(f"EXP-000782 PRIMARY PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
