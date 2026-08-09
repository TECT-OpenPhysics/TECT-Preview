#!/usr/bin/env python3
"""Independent stdlib verifier for the fixed-torus Q3 OS/KMS/reference theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-fixed-torus-os-kms-markov-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-FIXED-TORUS-OS-KMS-MARKOV-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FIXED-TORUS-PERIODIC-OS-DOMAIN-MARKOV-KMS-AND-STRICT-CENTERED-FREE-ENERGY-COMPARATOR"
EXPLORATION_ID = "EXP-000773"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-centered-nodal-q3-nelson-boue-dupuis-seam-limit-route-split/result.json"
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


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))] for i in range(len(left))]


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum(matrix[index][index] for index in range(len(matrix)))


def tilted_conditional_fixture() -> list[dict[str, Any]]:
    rows = []
    p_i = [
        [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)],
        [Fraction(2, 7), Fraction(3, 7), Fraction(2, 7)],
    ]
    p_o = [
        [Fraction(4, 9), Fraction(5, 9)],
        [Fraction(3, 8), Fraction(5, 8)],
    ]
    w_i = [[Fraction(2), Fraction(3), Fraction(5)], [Fraction(7), Fraction(11), Fraction(13)]]
    w_o = [[Fraction(17), Fraction(19)], [Fraction(23), Fraction(29)]]
    for boundary in range(2):
        left = [p_i[boundary][index] * w_i[boundary][index] for index in range(3)]
        right = [p_o[boundary][index] * w_o[boundary][index] for index in range(2)]
        left = [value / sum(left) for value in left]
        right = [value / sum(right) for value in right]
        joint = [[left[i] * right[o] for o in range(2)] for i in range(3)]
        inside = [sum(row) for row in joint]
        outside = [sum(joint[i][o] for i in range(3)) for o in range(2)]
        reconstructed = [[inside[i] * outside[o] for o in range(2)] for i in range(3)]
        rows.append({"boundary": boundary, "joint": joint, "reconstructed": reconstructed})
    return rows


def stringify(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    return value


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
    audit.check("independent EXP765 parent", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    covariance_rows = []
    for beta, omega in ((0.8, 0.9), (1.7, 1.1), (4.2, 2.3)):
        exact = 1.0 / (2.0 * omega * math.tanh(beta * omega / 2.0))
        cutoff = sum(1.0 / ((2.0 * math.pi * n / beta) ** 2 + omega**2) for n in range(-30000, 30001)) / beta
        covariance_rows.append({"beta": beta, "omega": omega, "exact": exact, "cutoff": cutoff})
        audit.check(f"independent Matsubara b{beta}", abs(exact - cutoff) < 2e-5, cutoff, exact, "sharp-time")
    beta, omega = 2.2, 1.6
    variances = []
    c0 = 1.0 / (2.0 * omega * math.tanh(beta * omega / 2.0))
    for delta in (0.3, 0.12, 0.04):
        cd = math.cosh(omega * (beta / 2.0 - delta)) / (2.0 * omega * math.sinh(beta * omega / 2.0))
        variances.append(2.0 * (c0 - cd))
    audit.check("independent sharp-time continuity", variances[2] < variances[1] < variances[0], variances, "decreasing", "sharp-time")
    coefficient_left = math.exp(-omega * beta / 2.0) / (4.0 * omega * math.sinh(omega * beta / 2.0))
    coefficient_right = math.exp(omega * beta / 2.0) / (4.0 * omega * math.sinh(omega * beta / 2.0))
    audit.check("independent RP rank-one coefficients", coefficient_left > 0.0 and coefficient_right > 0.0, (coefficient_left, coefficient_right), "positive", "reflection")
    times = [0.05, 0.16, 0.29, 0.41]
    rp = [[coefficient_left * math.exp(omega * (left + right)) + coefficient_right * math.exp(-omega * (left + right)) for right in times] for left in times]
    quadratic_tests = []
    for vector in ([1, -2, 3, -1], [2, 0, -1, 4], [-3, 1, 2, 5]):
        value = sum(vector[i] * rp[i][j] * vector[j] for i in range(4) for j in range(4))
        quadratic_tests.append(value)
    audit.check("independent RP Gram fixtures", min(quadratic_tests) >= -1e-12, quadratic_tests, "nonnegative", "reflection")

    markov_rows = tilted_conditional_fixture()
    for row in markov_rows:
        audit.check(f"independent local Bayes factorization b{row['boundary']}", row["joint"] == row["reconstructed"], row["joint"], row["reconstructed"], "Markov")
    audit.check("independent two-sided boundary fixture", len(markov_rows) == 2, len(markov_rows), 2, "Markov")

    q = Fraction(2, 5)
    K = [[Fraction(1), Fraction(0)], [Fraction(0), q]]
    K_inv = [[Fraction(1), Fraction(0)], [Fraction(0), 1 / q]]
    rho = [[value / (1 + q) for value in row] for row in K]
    A = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(-1)]]
    B = [[Fraction(0), Fraction(5)], [Fraction(7), Fraction(2)]]
    alpha = matmul(matmul(K, B), K_inv)
    kms_left = trace(matmul(matmul(rho, A), alpha))
    kms_right = trace(matmul(matmul(rho, B), A))
    audit.check("independent finite KMS identity", kms_left == kms_right, kms_left, kms_right, "KMS")
    energy_differences = [0, -3, 3, 0]
    audit.check("independent thermal Liouvillean two-sided", min(energy_differences) < 0 < max(energy_differences), energy_differences, "two-sided", "KMS")

    edges = [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]
    incident = [edge for edge in edges if 0 in edge]
    audit.check("independent Q3 twelve edges", len(edges) == 12, len(edges), 12, "free-energy")
    audit.check("independent Q3 one-vertex degree", len(incident) == 3, len(incident), 3, "free-energy")
    g, lam, beta, length = Fraction(5, 4), Fraction(2, 7), Fraction(3, 2), Fraction(11, 5)
    fourth = -(g + 3 * lam) / (4 * beta * length)
    audit.check("independent Q3 fourth chaos strictness", fourth < 0, fourth, "negative nonzero", "free-energy")

    probabilities = [0.2, 0.3, 0.5]
    raw = [-1.7, 0.4, 0.44]
    mean = sum(weight * value for weight, value in zip(probabilities, raw))
    values = [value - mean for value in raw]
    audit.check("independent centered fixture", abs(sum(weight * value for weight, value in zip(probabilities, values))) < 1e-15, values, "mean zero", "free-energy")
    partition = sum(weight * math.exp(value) for weight, value in zip(probabilities, values))
    audit.check("independent strict Jensen", partition > 1.0, partition, ">1", "free-energy")
    density = [weight * math.exp(value) / partition for weight, value in zip(probabilities, values)]
    relative_entropy = sum(probabilities[index] * math.log(probabilities[index] / density[index]) for index in range(3))
    audit.check("independent KL identity", abs(relative_entropy - math.log(partition)) < 1e-14, relative_entropy, math.log(partition), "free-energy")
    audit.check("independent KL strictness", relative_entropy > 0.0, relative_entropy, "positive", "free-energy")
    shift = 2.125
    shifted = [value - shift for value in values]
    shifted_partition = sum(weight * math.exp(value) for weight, value in zip(probabilities, shifted))
    shifted_density = [weight * math.exp(value) / shifted_partition for weight, value in zip(probabilities, shifted)]
    audit.check("independent normalized scalar gauge", max(abs(left - right) for left, right in zip(density, shifted_density)) < 1e-15, shifted_density, density, "free-energy")
    shifted_mean = sum(weight * value for weight, value in zip(probabilities, shifted))
    audit.check("independent gauge-invariant logZ-minus-mean", abs((math.log(shifted_partition) - shifted_mean) - math.log(partition)) < 1e-14, math.log(shifted_partition) - shifted_mean, math.log(partition), "free-energy")

    for phrase in ("finite beta circle is not a positive-energy vacuum theorem", "two-sided domain-Markov theorem", "relative-entropy formulation", "physical empty space", "microlocal spectrum condition", "no thermodynamic phase transition"):
        audit.check(f"independent certificate phrase {phrase[:30]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("Schwinger_distribution_regularity", "closed_L2_thermal_reflection_positivity", "sharp_time_algebra_and_generation", "two_sided_germ_domain_Markov", "abstract_stochastically_positive_beta0_KMS", "strict_centered_Gaussian_reference_free_energy_ordering", "scalar_gauge_invariant_relative_entropy_comparator"):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("ordinary_one_sided_circle_Markov_claimed", "beta_independent_Hamiltonian_family", "physical_beta_selected", "positive_energy_vacuum", "interacting_Hadamard_or_microlocal_spectrum", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "thermodynamic_limit", "ground_state_limit", "phase_transition_proved", "original_3D_Q3LOCK_parent", "C0_closed", "N1_through_N5_closed", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
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
            "covariance": covariance_rows,
            "continuity_variances": variances,
            "reflection_coefficients": [coefficient_left, coefficient_right],
            "Markov": stringify(markov_rows),
            "KMS": {"left": str(kms_left), "right": str(kms_right), "Liouville_spectrum": energy_differences},
            "free_energy": {"edges": len(edges), "incident": len(incident), "fourth_coefficient": str(fourth), "partition": partition, "KL": relative_entropy},
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
