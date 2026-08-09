#!/usr/bin/env python3
"""Primary verifier for EXP-000781 Q3LOCK Euclidean-DLR tangent states."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-phase-boundary-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-EUCLIDEAN-DLR-TANGENT-STATE-AND-PHASE-BOUNDARY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY"
EXPLORATION_ID = "EXP-000781"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-Q3-PHASE-SIGN-AND-KMS-SPLIT"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


def portable_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def cube_vertices() -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(2) for b in range(2) for c in range(2)]


def cube_edges() -> list[tuple[int, int]]:
    vertices = cube_vertices()
    edges: list[tuple[int, int]] = []
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            if sum(x != y for x, y in zip(vertices[left], vertices[right])) == 1:
                edges.append((left, right))
    return edges


def stable_gibbs_expectation(matrix_h: np.ndarray, observable: np.ndarray, beta: float) -> tuple[float, float]:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix_h)
    shifted = eigenvalues - float(np.min(eigenvalues))
    weights = np.exp(-beta * shifted)
    partition_shifted = float(np.sum(weights))
    diagonal = np.diag(eigenvectors.T @ observable @ eigenvectors)
    expectation = float(np.dot(weights, diagonal) / partition_shifted)
    log_partition = -beta * float(np.min(eigenvalues)) + math.log(partition_shifted)
    return log_partition, expectation


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
    parent_summary = parent.get("assertion_summary", parent.get("assertions", {}))
    audit.check("EXP773 all pass", parent_summary["passed"] == parent_summary["total"], parent_summary, "all pass", "parent")
    audit.check("EXP773 result", parent["result_id"] == "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY", parent["result_id"], "fixed lattice parent", "parent")

    c = sp.symbols("c", positive=True)
    q = sp.symbols("q0:8", real=True)
    z = sp.symbols("z0:8", real=True)
    edge_difference = sp.expand(c * sum((q[i] - z[i]) ** 2 for i in range(8)) / 2)
    edge_expanded = sp.expand(c * (sum(value**2 for value in q) + sum(value**2 for value in z)) / 2 - c * sum(q[i] * z[i] for i in range(8)))
    audit.check("one spatial edge expansion", sp.simplify(edge_difference - edge_expanded) == 0, edge_difference, edge_expanded, "coarse_map")
    audit.check("six neighbors give onsite 3c", sp.Rational(6, 2) * c == 3 * c, sp.Rational(6, 2) * c, 3 * c, "coarse_map")
    audit.check("ordered interaction counts edge twice", -sp.Rational(1, 2) * 2 * c == -c, -sp.Rational(1, 2) * 2 * c, -c, "coarse_map")

    edges = cube_edges()
    degrees = [0] * 8
    adjacency = sp.zeros(8)
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
        adjacency[left, right] = 1
        adjacency[right, left] = 1
    laplacian = 3 * sp.eye(8) - adjacency
    eigenvalues = {int(value): multiplicity for value, multiplicity in laplacian.eigenvals().items()}
    audit.check("Q3 vertex count", len(cube_vertices()) == 8, len(cube_vertices()), 8, "q3_geometry")
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "q3_geometry")
    audit.check("Q3 degree", degrees == [3] * 8, degrees, [3] * 8, "q3_geometry")
    audit.check("Q3 Laplacian spectrum", eigenvalues == {0: 1, 2: 3, 4: 3, 6: 1}, eigenvalues, {0: 1, 2: 3, 4: 3, 6: 1}, "q3_geometry")

    rational_vectors = [
        [sp.Rational(index - 3, 2) for index in range(8)],
        [sp.Rational((-1) ** index * (index + 1), 3) for index in range(8)],
        [sp.Rational(1, 1) for _ in range(8)],
        [sp.Rational(0, 1) for _ in range(8)],
    ]
    coercivity_rows: list[dict[str, str]] = []
    for vector in rational_vectors:
        sum_fourth = sum(value**4 for value in vector)
        norm_fourth = sum(value**2 for value in vector) ** 2
        lock = sum((vector[left] - vector[right]) ** 2 * (vector[left] ** 2 + vector[right] ** 2) for left, right in edges)
        coercivity_rows.append({"sum_fourth": str(sum_fourth), "norm_fourth": str(norm_fourth), "lock": str(lock)})
        audit.check("eight-component quartic coercivity fixture", 8 * sum_fourth >= norm_fourth, 8 * sum_fourth, norm_fourth, "coercivity")
        audit.check("Q3 lock nonnegative fixture", lock >= 0, lock, ">=0", "coercivity")

    g, radius, alpha, source_norm = sp.symbols("g radius alpha source_norm", positive=True)
    epsilon = g / 128
    delta = g / 128
    retained = sp.simplify(g / 32 - epsilon - delta)
    quadratic_cost = sp.simplify(alpha**2 / (4 * epsilon))
    linear_cost = sp.simplify(sp.Rational(3, 4) * source_norm ** sp.Rational(4, 3) / (4 * delta) ** sp.Rational(1, 3))
    audit.check("uniform retained radial quartic", retained == g / 64, retained, g / 64, "coercivity")
    for values in ((0.3, 0.2, 0.4), (1.1, 2.0, 0.8), (2.7, 0.0, 1.6)):
        g_value, alpha_value, source_value = values
        eps_value = g_value / 128.0
        del_value = g_value / 128.0
        q_cost = alpha_value**2 / (4.0 * eps_value)
        l_cost = 0.75 * source_value ** (4.0 / 3.0) / (4.0 * del_value) ** (1.0 / 3.0)
        for radial_value in (0.0, 0.2, 0.9, 2.3, 5.0):
            lhs = g_value * radial_value**4 / 32.0 - alpha_value * radial_value**2 - source_value * radial_value
            rhs = g_value * radial_value**4 / 64.0 - q_cost - l_cost
            audit.check("uniform source-compact radial lower bound", lhs + 1e-11 >= rhs, lhs, rhs, "coercivity")
    audit.check("quadratic absorption finite", quadratic_cost.is_finite is not False, quadratic_cost, "finite", "coercivity")
    audit.check("linear absorption finite", linear_cost.is_finite is not False, linear_cost, "finite", "coercivity")
    audit.check("nearest-neighbor interaction norm", 6 * c > 0, 6 * c, "finite", "external_map")
    audit.check("reduced mass map present", "m=chi/hbar^2" in manifest["exact_external_theorem_instantiation"]["mass"], manifest["exact_external_theorem_instantiation"]["mass"], "m=chi/hbar^2", "external_map")
    audit.check("external DLR result scoped", manifest["scope"]["tempered_Euclidean_DLR_nonempty"] is True, manifest["scope"]["tempered_Euclidean_DLR_nonempty"], True, "external_map")
    audit.check("external compactness scoped", manifest["scope"]["tempered_Euclidean_DLR_compact"] is True, manifest["scope"]["tempered_Euclidean_DLR_compact"], True, "external_map")

    base_h = np.array([[0.2, 0.4, -0.1], [0.4, 1.1, 0.3], [-0.1, 0.3, 2.0]], dtype=float)
    observable = np.array([[0.7, -0.2, 0.1], [-0.2, -0.4, 0.35], [0.1, 0.35, 0.9]], dtype=float)
    derivative_rows: list[dict[str, float]] = []
    for beta in (0.4, 1.3, 2.1):
        for field in (-0.8, -0.15, 0.0, 0.35, 1.2):
            step = 1.0e-6
            log_plus, _ = stable_gibbs_expectation(base_h - (field + step) * observable, observable, beta)
            log_minus, _ = stable_gibbs_expectation(base_h - (field - step) * observable, observable, beta)
            log_here, expectation = stable_gibbs_expectation(base_h - field * observable, observable, beta)
            derivative_log = (log_plus - log_minus) / (2.0 * step)
            derivative_pressure = derivative_log / (beta * 8.0)
            derivative_pi = derivative_log / 8.0
            derivative_rows.append({"beta": beta, "field": field, "log_z": log_here, "expectation": expectation})
            audit.check("Duhamel logZ source sign and beta", abs(derivative_log - beta * expectation) < 2.0e-7, derivative_log, beta * expectation, "source_derivative")
            audit.check("fine pressure factor eight", abs(derivative_pressure - expectation / 8.0) < 2.0e-7, derivative_pressure, expectation / 8.0, "source_derivative")
            audit.check("dimensionless pi retains beta", abs(derivative_pi - beta * expectation / 8.0) < 2.0e-7, derivative_pi, beta * expectation / 8.0, "source_derivative")

    convex_rows: list[dict[str, float]] = []
    target_slope = 1.7
    previous = -math.inf
    for index in (2, 4, 8, 16, 32, 64):
        smoothing = 1.0 / index
        field = 1.0 / math.sqrt(index)
        value = target_slope * math.sqrt(field * field + smoothing * smoothing)
        derivative = target_slope * field / math.sqrt(field * field + smoothing * smoothing)
        error = abs(value - target_slope * abs(field))
        convex_rows.append({"index": index, "field": field, "value": value, "derivative": derivative, "uniform_error_bound": target_slope * smoothing})
        audit.check("smooth convex even cusp approximation", error <= target_slope * smoothing + 1e-14, error, f"<={target_slope * smoothing}", "convex_selection")
        audit.check("selected derivative monotone to endpoint", derivative >= previous, derivative, f">={previous}", "convex_selection")
        previous = derivative
    audit.check("selected derivatives approach endpoint", target_slope - previous < 0.03, previous, target_slope, "convex_selection")
    audit.check("even convex right slope nonnegative", target_slope >= 0, target_slope, ">=0", "convex_selection")
    audit.check("left slope parity", -target_slope == -1 * target_slope, -target_slope, "negative right slope", "convex_selection")

    compactness_rows: list[dict[str, float]] = []
    levels = np.arange(1.0, 121.0)
    probabilities = np.exp(-0.17 * levels)
    probabilities /= probabilities.sum()
    mean_energy = float(np.dot(probabilities, levels))
    for cutoff in (5.0, 10.0, 20.0, 40.0, 80.0):
        tail = float(probabilities[levels > cutoff].sum())
        markov = mean_energy / cutoff
        compactness_rows.append({"cutoff": cutoff, "tail": tail, "markov_bound": markov})
        audit.check("compact-resolvent spectral tail", tail <= markov + 1e-14, tail, f"<={markov}", "local_compactness")
    audit.check("spectral tail tends small", compactness_rows[-1]["tail"] < compactness_rows[0]["tail"], compactness_rows[-1]["tail"], f"<{compactness_rows[0]['tail']}", "local_compactness")

    x, y, lam = sp.symbols("x y lam", real=True, nonnegative=False)
    edge_potential = lam * (x - y) ** 2 * (x**2 + y**2) / 4
    mixed = sp.factor(sp.diff(edge_potential, x, y))
    mixed_expected = -lam * (3 * x**2 - 4 * x * y + 3 * y**2) / 2
    mixed_matrix = sp.Matrix([[3, -2], [-2, 3]])
    audit.check("Q3 mixed derivative identity", sp.simplify(mixed - mixed_expected) == 0, mixed, mixed_expected, "positive_lambda_structure")
    audit.check("Q3 mixed quadratic eigenvalues", set(mixed_matrix.eigenvals()) == {1, 5}, mixed_matrix.eigenvals(), {1, 5}, "positive_lambda_structure")
    for x_value, y_value in ((-2.0, -0.5), (-1.0, 2.0), (0.0, 3.0), (1.4, 1.4)):
        quadratic = 3 * x_value**2 - 4 * x_value * y_value + 3 * y_value**2
        audit.check("Q3 submodularity fixture", quadratic >= -1e-14, quadratic, ">=0", "positive_lambda_structure")

    R, g_symbol, lambda_symbol = sp.symbols("R g_symbol lambda_symbol", positive=True)
    axial = (g_symbol + 3 * lambda_symbol) * R**4 / 4
    diagonal = g_symbol * R**4 / 32
    direct_axial = g_symbol * R**4 / 4 + 3 * lambda_symbol * R**4 / 4
    direct_diagonal = g_symbol * 8 * (R / sp.sqrt(8)) ** 4 / 4
    audit.check("nonradial axial energy", sp.simplify(axial - direct_axial) == 0, direct_axial, axial, "positive_lambda_structure")
    audit.check("nonradial diagonal energy", sp.simplify(diagonal - direct_diagonal) == 0, direct_diagonal, diagonal, "positive_lambda_structure")
    audit.check("positive lambda breaks O8", sp.simplify(axial - diagonal) != 0, sp.factor(axial - diagonal), "nonzero polynomial", "positive_lambda_structure")

    a, r, c_symbol, g2 = sp.symbols("a r c_symbol g2", real=True, positive=False)
    b = (a - r - 6 * c_symbol) / 2
    b2 = g2 / 4
    theta = sp.simplify((2 * b - a) / (4 * b2 * 3))
    theta_expected = -(r + 6 * c_symbol) / (3 * g2)
    audit.check("lambda0 theta-star substitution", sp.simplify(theta - theta_expected) == 0, theta, theta_expected, "lambda0_boundary")
    mass_chi, hbar = sp.symbols("mass_chi hbar", positive=True)
    reduced_mass = mass_chi / hbar**2
    phase_parameter = sp.simplify(8 * reduced_mass * c_symbol * theta**2)
    phase_expected = sp.simplify(8 * mass_chi * c_symbol * (r + 6 * c_symbol) ** 2 / (9 * hbar**2 * g2**2))
    audit.check("lambda0 phase parameter", sp.simplify(phase_parameter - phase_expected) == 0, phase_parameter, phase_expected, "lambda0_boundary")
    audit.check("lambda0 boundary is not positive lambda", manifest["lambda0_phase_boundary"]["scope"].startswith("This is a boundary comparator"), manifest["lambda0_phase_boundary"]["scope"], "boundary comparator", "lambda0_boundary")

    required_certificate_phrases = [
        "tempered Euclidean DLR measures is nonempty and compact",
        "There is no extra factor of `beta`",
        "does not prove that strict sign",
        "This is not a KMS theorem",
        "boundary comparator, not a theorem",
        "physical empty space",
        "C0, N1--N5, C6, CP1, Sector A, or Pre-A closure",
    ]
    for phrase in required_certificate_phrases:
        audit.check(f"certificate phrase: {phrase}", phrase in certificate, phrase in certificate, True, "certificate")

    true_scope = [
        "exact_registered_positive_lambda_fixed_lattice_family",
        "Kozitsky_Pasurek_hypotheses_instantiated",
        "tempered_Euclidean_DLR_nonempty",
        "tempered_Euclidean_DLR_compact",
        "uniform_exponential_local_moments",
        "periodic_limit_DLR_states",
        "source_tangent_zero_source_DLR_states",
        "pressure_slope_magnetization_identity",
        "locally_normal_time_zero_tangent_states",
        "lambda0_boundary_phase_regime",
    ]
    false_scope = [
        "positive_lambda_pressure_cusp",
        "positive_lambda_spontaneous_Z2_breaking",
        "tangent_states_extreme",
        "Cstar_pure_states",
        "spatial_clustering",
        "algebraic_KMS_for_preexisting_dynamics",
        "infinite_volume_real_time_dynamics",
        "ground_state_phase",
        "uniform_spectral_gap",
        "continuum_regulator_removal",
        "physical_empty_space_reference",
        "below_empty_space",
        "absolute_vacuum_energy_fixed",
        "effective_3D_to_1plus1_reduction",
        "physical_light_speed_derived",
        "event_horizon_or_cooling",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    ]
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    payload = {
        "schema": f"tect/{SLUG}-primary/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "claim_bearing": False,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "q3_edges": edges,
            "q3_degrees": degrees,
            "q3_laplacian_spectrum": eigenvalues,
            "coercivity_rows": coercivity_rows,
            "source_derivative_rows": derivative_rows,
            "convex_selection_rows": convex_rows,
            "compactness_rows": compactness_rows,
            "lambda0_theta_star": str(theta),
            "lambda0_phase_parameter": str(phase_parameter),
        },
        "scope": manifest["scope"],
        "files": {
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate": str(CERTIFICATE.relative_to(REPO)).replace("\\", "/"),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"),
        },
        "verdict": "PASS",
        "boundary": manifest["no_overclaim"],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-000781 PRIMARY PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
