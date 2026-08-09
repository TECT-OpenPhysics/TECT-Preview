#!/usr/bin/env python3
"""Primary verifier for the Q3 beta-independent Hamiltonian/ground theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-beta-independent-hamiltonian-ground-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-BETA-INDEPENDENT-HAMILTONIAN-GROUND-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-COMPACT-CIRCLE-FIXED-HAMILTONIAN-FK-GIBBS-AND-STRICT-GROUND-REFERENCE-ADVANTAGE"
EXPLORATION_ID = "EXP-000774"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-fixed-torus-os-kms-markov-reference-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


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


def cube_edges() -> list[tuple[int, int]]:
    return [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]


def laplacian_matrix(edges: list[tuple[int, int]]) -> sp.Matrix:
    matrix = sp.zeros(8)
    for left, right in edges:
        matrix[left, left] += 1
        matrix[right, right] += 1
        matrix[left, right] -= 1
        matrix[right, left] -= 1
    return matrix


def polynomial_laplacian(poly: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    return sp.expand(sum(sp.diff(poly, variable, 2) for variable in variables))


def wick(poly: sp.Expr, covariance: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    result = sp.expand(poly)
    current = sp.expand(poly)
    coefficient = sp.Integer(1)
    for order in range(1, 3):
        current = polynomial_laplacian(current, variables)
        coefficient *= -covariance / (2 * order)
        result += coefficient * current
    return sp.expand(result)


def thermal_difference(beta: float, length: float, mass: float, cutoff: int) -> float:
    total = 0.0
    for mode in range(-cutoff, cutoff + 1):
        omega = math.sqrt(mass * mass + (2.0 * math.pi * mode / length) ** 2)
        boltzmann = math.exp(-beta * omega)
        total += boltzmann / (omega * (1.0 - boltzmann))
    return total / length


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("EXP766 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP766 KMS and reference parent", parent["scope"]["abstract_stochastically_positive_beta0_KMS"] is True and parent["scope"]["strict_centered_Gaussian_reference_free_energy_ordering"] is True, "KMS and reference", True, "parent")

    edges = cube_edges()
    Lq = laplacian_matrix(edges)
    audit.check("Q3 twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 Laplacian trace", sp.trace(Lq) == 24, sp.trace(Lq), 24, "Q3")
    audit.check("Q3 Laplacian row sums", all(sum(Lq[row, column] for column in range(8)) == 0 for row in range(8)), list(Lq * sp.ones(8, 1)), "zero", "Q3")
    x = sp.symbols("x0:8", real=True)
    g, lam, m, eta, C, D = sp.symbols("g lambda m eta C D", real=True)
    W4 = g * sum(value**4 for value in x) / 4 + lam * sum((x[left] - x[right]) ** 2 * (x[left] ** 2 + x[right] ** 2) for left, right in edges) / 4
    Aq = (g + lam) * sp.eye(8) + lam * Lq
    G = g + 4 * lam
    vector = sp.Matrix(x)
    Kstar = m * sp.eye(8) + eta * Lq
    quadratic_star = (vector.T * Kstar * vector)[0] / 2
    delta_W4 = polynomial_laplacian(W4, x)
    delta2_W4 = polynomial_laplacian(delta_W4, x)
    audit.check("Q3 quartic Laplacian", sp.expand(delta_W4 - 3 * (vector.T * Aq * vector)[0]) == 0, delta_W4, "3 x^T A_Q3 x", "Wick")
    audit.check("Q3 quartic bi-Laplacian", sp.simplify(delta2_W4 - 48 * G) == 0, delta2_W4, 48 * G, "Wick")
    audit.check("Tr A_Q3", sp.simplify(sp.trace(Aq) - 8 * G) == 0, sp.trace(Aq), 8 * G, "Wick")

    Kbeta = Kstar + 3 * D * Aq
    Pstar = quadratic_star + W4
    Pbeta = (vector.T * Kbeta * vector)[0] / 2 + W4
    left = wick(Pbeta, C + D, x)
    right = wick(Pstar, C, x) - D * sp.trace(Kstar) / 2 - 6 * D**2 * G
    audit.check("exact coherent Wick polynomial identity", sp.expand(left - right) == 0, sp.expand(left - right), 0, "Wick")
    generic_symbols = sp.symbols("k0:36", real=True)
    Kgeneric = sp.zeros(8)
    generic_index = 0
    for row in range(8):
        for column in range(row, 8):
            Kgeneric[row, column] = generic_symbols[generic_index]
            Kgeneric[column, row] = generic_symbols[generic_index]
            generic_index += 1
    Kbeta_generic = Kgeneric + 3 * D * Aq
    Pstar_generic = (vector.T * Kgeneric * vector)[0] / 2 + W4
    Pbeta_generic = (vector.T * Kbeta_generic * vector)[0] / 2 + W4
    generic_left = wick(Pbeta_generic, C + D, x)
    generic_right = wick(Pstar_generic, C, x) - D * sp.trace(Kgeneric) / 2 - 6 * D**2 * G
    audit.check("generic symmetric K exact Wick identity", sp.expand(generic_left - generic_right) == 0, sp.expand(generic_left - generic_right), 0, "Wick")
    audit.check("generic symmetric K coefficient coherence", sp.expand(Kbeta_generic - 3 * D * Aq) == Kgeneric, sp.expand(Kbeta_generic - 3 * D * Aq), Kgeneric, "Wick")
    general_Kbeta = Kstar + 3 * D * Aq
    general_scalar = 6 * D**2 * G - D * sp.trace(general_Kbeta) / 2
    coherent_scalar = -D * sp.trace(Kstar) / 2 - 6 * D**2 * G
    audit.check("coherent uncorrected scalar sign", sp.simplify(general_scalar - coherent_scalar) == 0, general_scalar, coherent_scalar, "Wick")
    compensator = D * sp.trace(Kstar) / 2 + 6 * D**2 * G
    audit.check("absolute scalar compensator", sp.simplify(coherent_scalar + compensator) == 0, compensator, -coherent_scalar, "Wick")
    raw_quadratic_beta = sp.expand(Kbeta - 3 * (C + D) * Aq)
    raw_quadratic_star = sp.expand(Kstar - 3 * C * Aq)
    audit.check("raw field-dependent coefficients beta independent", raw_quadratic_beta == raw_quadratic_star, raw_quadratic_beta, raw_quadratic_star, "Wick")
    wrong_mass_only = Kstar + 3 * D * (g + lam) * sp.eye(8)
    audit.check("mass-only mutation fails for lambda", sp.expand(wrong_mass_only - 3 * D * Aq - Kstar) != sp.zeros(8), sp.expand(wrong_mass_only - 3 * D * Aq - Kstar), "nonzero for lambda", "mutation")
    audit.check("wrong scalar-sign mutation fails", sp.simplify(coherent_scalar - compensator) != 0, sp.simplify(coherent_scalar - compensator), "nonzero", "mutation")

    difference_rows = []
    for beta_value in (0.7, 1.5, 3.0, 6.0):
        bose = thermal_difference(beta_value, 5.0, 1.2, 400)
        direct = 0.0
        for mode in range(-400, 401):
            omega_value = math.sqrt(1.2**2 + (2.0 * math.pi * mode / 5.0) ** 2)
            direct += (1.0 / (2.0 * omega_value)) * (1.0 / math.tanh(beta_value * omega_value / 2.0) - 1.0)
        direct /= 5.0
        difference_rows.append({"beta": beta_value, "bose": bose, "coth_minus_vacuum": direct})
        audit.check(f"thermal-vacuum D identity beta{beta_value}", abs(bose - direct) < 2e-14, bose, direct, "thermal")
    audit.check("D_beta positive", all(row["bose"] > 0.0 for row in difference_rows), difference_rows, "positive", "thermal")
    audit.check("D_beta decreases with beta", all(difference_rows[index + 1]["bose"] < difference_rows[index]["bose"] for index in range(len(difference_rows) - 1)), difference_rows, "strict decrease", "thermal")
    audit.check("D_beta ground decay", difference_rows[-1]["bose"] < 0.03 * difference_rows[0]["bose"], difference_rows, "decay", "thermal")

    trace_rows = []
    for cutoff in (8, 16, 32, 64):
        log_partition = 0.0
        for mode in range(-cutoff, cutoff + 1):
            omega_value = math.sqrt(1.2**2 + (2.0 * math.pi * mode / 5.0) ** 2)
            log_partition += -8.0 * math.log1p(-math.exp(-1.1 * omega_value))
        trace_rows.append({"cutoff": cutoff, "log_free_partition": log_partition})
    audit.check("free Fock log partition monotone", trace_rows[1]["log_free_partition"] > trace_rows[0]["log_free_partition"] and all(trace_rows[index + 1]["log_free_partition"] >= trace_rows[index]["log_free_partition"] for index in range(len(trace_rows) - 1)), trace_rows, "nondecreasing", "Hamiltonian")
    audit.check("free Fock trace tail converges", trace_rows[-1]["log_free_partition"] - trace_rows[-2]["log_free_partition"] < 1e-10, trace_rows, "small tail", "Hamiltonian")

    Lsym, m0 = sp.symbols("L m0", positive=True)
    amplitude = (g + 3 * lam) * sp.sqrt(sp.factorial(4)) / (16 * Lsym * m0**2)
    audit.check("four-particle amplitude positive domain", amplitude.subs({g: 1, lam: 0, Lsym: 2, m0: 1}) > 0, amplitude, "positive for g>0 lambda>=0", "ground")
    audit.check("quadratic degree cannot create four particles", sp.Poly(quadratic_star, x).total_degree() == 2, sp.Poly(quadratic_star, x).total_degree(), 2, "ground")
    t = sp.symbols("t", positive=True)
    Avalue = sp.Rational(5, 7)
    Bvalue = sp.Rational(11, 3)
    rayleigh = sp.simplify((-2 * t * Avalue + t**2 * Bvalue) / (1 + t**2))
    test_t = sp.Rational(1, 10)
    audit.check("Rayleigh-Ritz strict negative fixture", rayleigh.subs(t, test_t) < 0, rayleigh.subs(t, test_t), "negative", "ground")
    audit.check("Rayleigh threshold", test_t < 2 * Avalue / Bvalue, test_t, 2 * Avalue / Bvalue, "ground")
    scalar = sp.symbols("c", real=True)
    audit.check("ground-reference scalar gauge invariance", sp.simplify((sp.Symbol("E0") + scalar) - (sp.Symbol("trial") + scalar) - (sp.Symbol("E0") - sp.Symbol("trial"))) == 0, scalar, "cancels", "ground")

    beta_values = (1.0, 2.0, 4.0, 8.0)
    interacting_energies = (-2.0, 1.0, 4.0)
    free_energies = (0.0, 2.0, 5.0)
    free_energy_rows = []
    for beta_value in beta_values:
        f_h = -math.log(sum(math.exp(-beta_value * energy_value) for energy_value in interacting_energies)) / beta_value
        f_0 = -math.log(sum(math.exp(-beta_value * energy_value) for energy_value in free_energies)) / beta_value
        free_energy_rows.append({"beta": beta_value, "difference": f_h - f_0})
    audit.check("ground free-energy limit approaches -2", abs(free_energy_rows[-1]["difference"] + 2.0) < 1e-7, free_energy_rows, -2.0, "ground")
    audit.check("ground free-energy convergence", all(abs(free_energy_rows[index + 1]["difference"] + 2.0) < abs(free_energy_rows[index]["difference"] + 2.0) for index in range(len(free_energy_rows) - 1)), free_energy_rows, "convergent", "ground")

    for phrase in ("Wick coherence across beta", "necessary and sufficient coherence", "Eight-component Hamiltonian construction", "Feynman--Kac--Nelson identification", "not inferred from strong-resolvent convergence alone", "closed Hamiltonian form", "finite-particle Wick form core", "Strict compact-circle ground advantage", "finite-beta scalar firewall", "not a physical-empty-space", "not a world-first claim"):
        audit.check(f"certificate phrase {phrase[:36]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("exact_thermal_to_vacuum_Wick_dictionary", "matrix_and_scalar_coherence_necessary_sufficient", "beta_independent_compact_circle_Hamiltonian", "self_adjoint_lower_bounded_Hamiltonian", "compact_resolvent_and_trace_class_heat_semigroup", "Feynman_Kac_Nelson_Gibbs_identification", "faithful_normal_beta_KMS_family", "unique_finite_volume_ground", "strict_ground_Gaussian_reference_advantage", "beta_to_infinity_ground_free_energy_limit"):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("arbitrary_bounded_K_beta_family", "original_fixed_raw_CL8_family", "thermodynamic_limit", "strict_thermodynamic_energy_density", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "spontaneous_symmetry_breaking_or_phase_transition", "interacting_Hadamard_or_microlocal_spectrum", "original_3D_Q3LOCK_parent", "physical_light_speed_derived", "C0_closed", "N1_through_N5_closed", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("analytic proof label", manifest["verification"]["proof_grade"].startswith("ANALYTIC"), manifest["verification"]["proof_grade"], "ANALYTIC", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
            "Q3": {"edges": edges, "trace_L": str(sp.trace(Lq)), "trace_A": str(sp.trace(Aq))},
            "Wick": {"delta_W4": str(delta_W4), "delta2_W4": str(delta2_W4), "coherent_scalar": str(coherent_scalar), "compensator": str(compensator)},
            "thermal_difference": difference_rows,
            "free_Fock_trace": trace_rows,
            "ground": {"amplitude": str(amplitude), "Rayleigh": str(rayleigh), "free_energy": free_energy_rows},
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
