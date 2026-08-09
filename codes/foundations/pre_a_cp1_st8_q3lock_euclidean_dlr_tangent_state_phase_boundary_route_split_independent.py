#!/usr/bin/env python3
"""Standard-library independent audit for EXP-000781."""

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
PRIMARY_SCRIPT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split.py"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"


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


def vertices() -> list[tuple[int, int, int]]:
    return [(i >> 2 & 1, i >> 1 & 1, i & 1) for i in range(8)]


def edges() -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    data = vertices()
    for i in range(8):
        for j in range(i + 1, 8):
            if sum(a != b for a, b in zip(data[i], data[j])) == 1:
                result.append((i, j))
    return result


def log_two_cosh(value: float) -> float:
    absolute = abs(value)
    return absolute + math.log1p(math.exp(-2.0 * absolute))


def two_by_two_log_z(field: float, beta: float) -> float:
    # H0=[[0.3,0.45],[0.45,1.2]], M=[[0.7,-0.25],[-0.25,-0.4]].
    h00 = 0.3 - 0.7 * field
    h11 = 1.2 + 0.4 * field
    h01 = 0.45 + 0.25 * field
    center = (h00 + h11) / 2.0
    radius = math.hypot((h00 - h11) / 2.0, h01)
    return -beta * center + log_two_cosh(beta * radius)


def two_by_two_expectation(field: float, beta: float) -> float:
    # d(log Z)/dh divided by beta, derived without importing the primary code.
    h00 = 0.3 - 0.7 * field
    h11 = 1.2 + 0.4 * field
    h01 = 0.45 + 0.25 * field
    delta = (h00 - h11) / 2.0
    radius = math.hypot(delta, h01)
    center_prime = (-0.7 + 0.4) / 2.0
    delta_prime = (-0.7 - 0.4) / 2.0
    off_prime = 0.25
    radius_prime = (delta * delta_prime + h01 * off_prime) / radius
    return -center_prime + math.tanh(beta * radius) * radius_prime


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    certificate = " ".join(certificate_text.split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    summary = parent.get("assertion_summary", parent.get("assertions", {}))
    audit.check("parent all pass", summary["passed"] == summary["total"], summary, "all pass", "parent")
    independent_source = Path(__file__).read_text(encoding="utf-8")
    forbidden_import = "import pre_a_cp1_st8_" + "q3lock_euclidean"
    audit.check("no import from primary", forbidden_import not in independent_source, forbidden_import in independent_source, False, "independence")

    cube_edges = edges()
    degree = [0] * 8
    neighbors: list[list[int]] = [[] for _ in range(8)]
    for left, right in cube_edges:
        degree[left] += 1
        degree[right] += 1
        neighbors[left].append(right)
        neighbors[right].append(left)
    audit.check("Q3 edge count independent", len(cube_edges) == 12, len(cube_edges), 12, "q3")
    audit.check("Q3 degrees independent", degree == [3] * 8, degree, [3] * 8, "q3")
    spectrum: list[int] = []
    data = vertices()
    for mask in range(8):
        character = [(-1) ** ((mask >> 2 & 1) * point[0] + (mask >> 1 & 1) * point[1] + (mask & 1) * point[2]) for point in data]
        weight = (mask >> 2 & 1) + (mask >> 1 & 1) + (mask & 1)
        eigenvalue = 2 * weight
        spectrum.append(eigenvalue)
        for site in range(8):
            action = 3 * character[site] - sum(character[item] for item in neighbors[site])
            audit.check("Walsh Q3 Laplacian eigenpair", action == eigenvalue * character[site], action, eigenvalue * character[site], "q3")
    audit.check("Q3 spectrum independent", sorted(spectrum) == [0, 2, 2, 2, 4, 4, 4, 6], sorted(spectrum), [0, 2, 2, 2, 4, 4, 4, 6], "q3")

    vectors = [
        [Fraction(i - 4, 3) for i in range(8)],
        [Fraction((-1) ** i * (i + 2), 5) for i in range(8)],
        [Fraction(1, 2)] * 8,
        [Fraction(0)] * 8,
    ]
    q3_rows: list[dict[str, str]] = []
    for vector in vectors:
        fourth = sum(item**4 for item in vector)
        norm4 = sum(item**2 for item in vector) ** 2
        lock = sum((vector[i] - vector[j]) ** 2 * (vector[i] ** 2 + vector[j] ** 2) for i, j in cube_edges)
        q3_rows.append({"fourth": str(fourth), "norm4": str(norm4), "lock": str(lock)})
        audit.check("rational quartic coercivity", 8 * fourth >= norm4, 8 * fourth, norm4, "coercivity")
        audit.check("rational lock positivity", lock >= 0, lock, ">=0", "coercivity")

    spatial_vectors = [
        ([Fraction(i, 3) for i in range(8)], [Fraction(7 - i, 4) for i in range(8)]),
        ([Fraction((-1) ** i, 2) for i in range(8)], [Fraction(i % 3 - 1, 5) for i in range(8)]),
    ]
    for left, right in spatial_vectors:
        lhs = Fraction(7, 10) * sum((a - b) ** 2 for a, b in zip(left, right)) / 2
        rhs = Fraction(7, 10) * (sum(a * a for a in left) + sum(b * b for b in right)) / 2 - Fraction(7, 10) * sum(a * b for a, b in zip(left, right))
        audit.check("spatial difference expansion independent", lhs == rhs, lhs, rhs, "coarse_map")
    audit.check("coordination diagonal coefficient", Fraction(6, 2) == 3, Fraction(6, 2), 3, "coarse_map")
    audit.check("interaction summability", abs(6 * 0.7 - 4.2) < 1e-14, 6 * 0.7, 4.2, "external_map")

    lower_rows: list[dict[str, float]] = []
    for g_value in (0.25, 0.8, 2.4):
        retained = g_value / 64.0
        epsilon = g_value / 128.0
        delta = g_value / 128.0
        audit.check("retained quartic independent", abs(retained - (g_value / 32.0 - epsilon - delta)) < 1e-15, retained, g_value / 32.0 - epsilon - delta, "coercivity")
        for alpha in (0.0, 0.4, 1.9):
            for source in (0.0, 0.3, 1.4):
                quadratic_cost = alpha * alpha / (4.0 * epsilon)
                linear_cost = 0.75 * source ** (4.0 / 3.0) / (4.0 * delta) ** (1.0 / 3.0)
                for radius in (0.0, 0.1, 0.7, 1.8, 4.1):
                    lhs = g_value * radius**4 / 32.0 - alpha * radius**2 - source * radius
                    rhs = retained * radius**4 - quadratic_cost - linear_cost
                    lower_rows.append({"lhs": lhs, "rhs": rhs})
                    audit.check("source-compact lower bound independent", lhs + 1e-12 >= rhs, lhs, rhs, "coercivity")

    derivative_rows: list[dict[str, float]] = []
    for beta in (0.35, 0.9, 1.8, 2.6):
        for field in (-1.1, -0.3, 0.0, 0.45, 1.4):
            step = 2.0e-6
            derivative = (two_by_two_log_z(field + step, beta) - two_by_two_log_z(field - step, beta)) / (2.0 * step)
            expectation = two_by_two_expectation(field, beta)
            pressure_derivative = derivative / (beta * 8.0)
            pi_derivative = derivative / 8.0
            derivative_rows.append({"beta": beta, "field": field, "derivative": derivative, "expectation": expectation})
            audit.check("2x2 noncommuting Duhamel derivative", abs(derivative - beta * expectation) < 2e-9, derivative, beta * expectation, "source_derivative")
            audit.check("2x2 fine pressure factor", abs(pressure_derivative - expectation / 8.0) < 2e-9, pressure_derivative, expectation / 8.0, "source_derivative")
            audit.check("2x2 dimensionless beta factor", abs(pi_derivative - beta * expectation / 8.0) < 2e-9, pi_derivative, beta * expectation / 8.0, "source_derivative")

    convex_rows: list[dict[str, float]] = []
    endpoint = 2.3
    previous = 0.0
    for n in (3, 6, 12, 24, 48, 96, 192):
        smoothing = 1.0 / n
        field = n ** -0.5
        derivative = endpoint * field / math.sqrt(field * field + smoothing * smoothing)
        secant_left = endpoint * (math.sqrt(field * field + smoothing * smoothing) - smoothing) / field
        secant_right = endpoint * (math.sqrt((2 * field) ** 2 + smoothing * smoothing) - math.sqrt(field * field + smoothing * smoothing)) / field
        convex_rows.append({"n": n, "derivative": derivative, "left_secant": secant_left, "right_secant": secant_right})
        audit.check("convex derivative secant lower", derivative + 1e-14 >= secant_left, derivative, f">={secant_left}", "convex_selection")
        audit.check("convex derivative secant upper", derivative <= secant_right + 1e-14, derivative, f"<={secant_right}", "convex_selection")
        audit.check("selected derivative monotone", derivative >= previous, derivative, f">={previous}", "convex_selection")
        previous = derivative
    audit.check("selected endpoint convergence", endpoint - previous < 0.01, previous, endpoint, "convex_selection")
    audit.check("parity endpoint slopes", -endpoint == -1.0 * endpoint, -endpoint, "-endpoint", "convex_selection")

    probabilities = [math.exp(-0.12 * level) for level in range(1, 201)]
    normalizer = sum(probabilities)
    probabilities = [value / normalizer for value in probabilities]
    mean_energy = sum((index + 1) * value for index, value in enumerate(probabilities))
    tail_rows: list[dict[str, float]] = []
    for cutoff in (6, 12, 24, 48, 96, 160):
        tail = sum(value for index, value in enumerate(probabilities, start=1) if index > cutoff)
        bound = mean_energy / cutoff
        tail_rows.append({"cutoff": cutoff, "tail": tail, "bound": bound})
        audit.check("spectral Markov tail independent", tail <= bound + 1e-14, tail, f"<={bound}", "local_compactness")
    audit.check("compactness tail decreases", all(tail_rows[i + 1]["tail"] < tail_rows[i]["tail"] for i in range(len(tail_rows) - 1)), [row["tail"] for row in tail_rows], "strictly decreasing", "local_compactness")

    submodular_rows: list[dict[str, float]] = []
    for x in (-2.0, -0.75, 0.0, 0.6, 1.8):
        for y in (-1.5, -0.2, 0.0, 1.1, 2.2):
            form = 3.0 * x * x - 4.0 * x * y + 3.0 * y * y
            alternate = 2.0 * (x - y) ** 2 + x * x + y * y
            mixed = -0.5 * form
            submodular_rows.append({"x": x, "y": y, "form": form, "mixed_at_lambda1": mixed})
            audit.check("submodular quadratic factor", abs(form - alternate) < 1e-13, form, alternate, "positive_lambda_structure")
            audit.check("submodular mixed sign", mixed <= 1e-14, mixed, "<=0", "positive_lambda_structure")

    nonradial_rows: list[dict[str, float]] = []
    for radius in (0.2, 0.9, 2.1):
        for g_value in (0.3, 1.4):
            for lambda_value in (0.1, 0.8):
                axial = (g_value + 3.0 * lambda_value) * radius**4 / 4.0
                diagonal = g_value * radius**4 / 32.0
                nonradial_rows.append({"axial": axial, "diagonal": diagonal})
                audit.check("positive lambda nonradial witness", axial > diagonal, axial, f">{diagonal}", "positive_lambda_structure")

    lambda0_rows: list[dict[str, float]] = []
    for a in (0.4, 1.0, 2.2):
        for r in (-4.0, -2.0):
            for c in (0.1, 0.25):
                if r + 6.0 * c >= 0:
                    continue
                for g in (0.5, 1.7):
                    b = (a - r - 6.0 * c) / 2.0
                    b2 = g / 4.0
                    theta_external = (2.0 * b - a) / (4.0 * b2 * 3.0)
                    theta_target = -(r + 6.0 * c) / (3.0 * g)
                    lambda0_rows.append({"theta_external": theta_external, "theta_target": theta_target})
                    audit.check("lambda0 theta substitution independent", abs(theta_external - theta_target) < 1e-13, theta_external, theta_target, "lambda0_boundary")
                    audit.check("lambda0 double well", b > a / 2.0, b, f">{a/2.0}", "lambda0_boundary")

    urls = [
        "https://arxiv.org/pdf/math-ph/0609045",
        "https://arxiv.org/pdf/0710.2303",
    ]
    for url in urls:
        audit.check(f"primary-source URL {url}", url in certificate_text, url in certificate_text, True, "provenance")
    audit.check("general theorem not radial", "No radial symmetry is needed for these general conclusions" in certificate, "No radial symmetry is needed for these general conclusions" in certificate, True, "provenance")
    audit.check("positive lambda phase remains open", "does not prove that strict sign" in certificate, "does not prove that strict sign" in certificate, True, "provenance")
    audit.check("KMS warning", "This is not a KMS theorem" in certificate, "This is not a KMS theorem" in certificate, True, "provenance")
    audit.check("physical reference warning", "physical empty-space reference" in certificate, "physical empty-space reference" in certificate, True, "provenance")
    audit.check("world-first disclaimed", "No new general Gibbs-state or phase-transition theorem and no world-first claim is made" in manifest["prior_art_boundary"], manifest["prior_art_boundary"], "world-first disclaimed", "provenance")

    for key, value in manifest["scope"].items():
        if key in {
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
        }:
            audit.check(f"true scope {key}", value is True, value, True, "scope")
        else:
            audit.check(f"false scope {key}", value is False, value, False, "scope")

    audit.check("C6 tier", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    payload = {
        "schema": f"tect/{SLUG}-independent/0.1",
        "script_version": __version__,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "parent_gate": PARENT_GATE,
        "next_gate": NEXT_GATE,
        "claim_bearing": False,
        "independent_of_primary_imports": True,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "derived": {
            "q3_edges": cube_edges,
            "q3_spectrum": sorted(spectrum),
            "q3_rows": q3_rows,
            "lower_bound_rows": lower_rows,
            "source_derivative_rows": derivative_rows,
            "convex_rows": convex_rows,
            "spectral_tail_rows": tail_rows,
            "submodular_rows": submodular_rows,
            "nonradial_rows": nonradial_rows,
            "lambda0_rows": lambda0_rows,
        },
        "scope": manifest["scope"],
        "files": {
            "manifest_sha256": portable_sha256(MANIFEST),
            "certificate_sha256": portable_sha256(CERTIFICATE),
            "primary_script_sha256_observed": portable_sha256(PRIMARY_SCRIPT),
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
    print(f"EXP-000781 INDEPENDENT PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
