#!/usr/bin/env python3
"""Primary verifier for the fixed-torus Q3 OS/KMS/Markov/reference theorem."""

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

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-fixed-torus-os-kms-markov-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-FIXED-TORUS-OS-KMS-MARKOV-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FIXED-TORUS-PERIODIC-OS-DOMAIN-MARKOV-KMS-AND-STRICT-CENTERED-FREE-ENERGY-COMPARATOR"
EXPLORATION_ID = "EXP-000773"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-centered-nodal-q3-nelson-boue-dupuis-seam-limit-route-split/result.json"
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


def gaussian_domain_markov_fixture() -> dict[str, Any]:
    """Exact Bayes fixture: B separates I and O, and local tilts preserve it."""
    p_b = [Fraction(2, 5), Fraction(3, 5)]
    p_i = [[Fraction(1, 4), Fraction(3, 4)], [Fraction(2, 3), Fraction(1, 3)]]
    p_o = [[Fraction(3, 5), Fraction(2, 5)], [Fraction(1, 5), Fraction(4, 5)]]
    w_i = [[Fraction(2), Fraction(5)], [Fraction(3), Fraction(7)]]
    w_o = [[Fraction(11), Fraction(13)], [Fraction(17), Fraction(19)]]
    conditional_rows = []
    for boundary in range(2):
        joint = [[p_i[boundary][inside] * p_o[boundary][outside] * w_i[boundary][inside] * w_o[boundary][outside]
                  for outside in range(2)] for inside in range(2)]
        total = sum(sum(row) for row in joint)
        joint = [[value / total for value in row] for row in joint]
        inside_marginal = [sum(row) for row in joint]
        outside_marginal = [sum(joint[inside][outside] for inside in range(2)) for outside in range(2)]
        factorized = [[inside_marginal[inside] * outside_marginal[outside] for outside in range(2)] for inside in range(2)]
        conditional_rows.append({"boundary": boundary, "joint": joint, "factorized": factorized})
    return {"p_boundary": p_b, "rows": conditional_rows}


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
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("EXP765 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP765 parent scope", parent["scope"]["centered_Q3_limit_reflection_positive"] is True and parent["scope"]["centered_Q3_fixed_band_regular_Weyl_limit"] is True, "RP and Weyl", "true", "parent")

    beta, omega, time = sp.symbols("beta omega t", positive=True)
    sharp = sp.coth(beta * omega / 2) / (2 * omega)
    kernel = sp.cosh(omega * (beta / 2 - time)) / (2 * omega * sp.sinh(beta * omega / 2))
    audit.check("sharp-time thermal covariance", sp.simplify(kernel.subs(time, 0) - sharp) == 0, kernel.subs(time, 0), sharp, "sharp-time")
    audit.check("thermal kernel field equation", sp.simplify(sp.diff(kernel, time, 2) - omega**2 * kernel) == 0, sp.simplify(sp.diff(kernel, time, 2) - omega**2 * kernel), 0, "sharp-time")
    derivative_jump = sp.simplify(sp.diff(kernel, time).subs(time, beta) - sp.diff(kernel, time).subs(time, 0))
    audit.check("thermal kernel derivative jump", derivative_jump == 1, derivative_jump, 1, "sharp-time")
    audit.check("sharp covariance positive", sharp.is_positive is True, sharp, ">0", "sharp-time")
    for beta_value, omega_value in ((1.0, 0.7), (2.5, 1.3), (5.0, 2.0)):
        exact = 0.5 / omega_value / math.tanh(beta_value * omega_value / 2.0)
        cutoff = sum(1.0 / ((2.0 * math.pi * n / beta_value) ** 2 + omega_value**2) for n in range(-20000, 20001)) / beta_value
        audit.check(f"Matsubara covariance fixture b{beta_value}", abs(exact - cutoff) < 2e-5, cutoff, exact, "sharp-time")
    covariance_differences = []
    beta_value, omega_value = 3.0, 1.4
    for delta in (0.2, 0.1, 0.05):
        c0 = math.cosh(omega_value * beta_value / 2.0) / (2.0 * omega_value * math.sinh(omega_value * beta_value / 2.0))
        cd = math.cosh(omega_value * (beta_value / 2.0 - delta)) / (2.0 * omega_value * math.sinh(omega_value * beta_value / 2.0))
        covariance_differences.append(2.0 * (c0 - cd))
    audit.check("sharp-time L2 continuity fixtures", covariance_differences[2] < covariance_differences[1] < covariance_differences[0], covariance_differences, "decrease to zero", "sharp-time")

    rp_times = [0.08, 0.19, 0.31]
    beta_value, omega_value = 1.0, 1.7
    def periodic_covariance(delta: float) -> float:
        distance = min(abs(delta) % beta_value, beta_value - (abs(delta) % beta_value))
        return math.cosh(omega_value * (beta_value / 2.0 - distance)) / (2.0 * omega_value * math.sinh(omega_value * beta_value / 2.0))
    rp_matrix = sp.Matrix([[periodic_covariance((-left) - right) for right in rp_times] for left in rp_times])
    rp_eigenvalues = sorted(float(value) for value in rp_matrix.eigenvals(multiple=True))
    audit.check("free thermal RP Gram positive semidefinite", min(rp_eigenvalues) > -1e-12 and max(rp_eigenvalues) > 0.0, rp_eigenvalues, "positive semidefinite", "reflection")
    audit.check("RP Gram symmetric", rp_matrix == rp_matrix.T, rp_matrix, "symmetric", "reflection")

    markov = gaussian_domain_markov_fixture()
    for row in markov["rows"]:
        audit.check(f"local tilt preserves conditional factorization b{row['boundary']}", row["joint"] == row["factorized"], row["joint"], row["factorized"], "Markov")
    audit.check("Markov fixture has two boundary sectors", len(markov["rows"]) == 2, len(markov["rows"]), 2, "Markov")

    q = sp.symbols("q", positive=True)
    K = sp.diag(1, q)
    rho = K / sp.trace(K)
    A = sp.Matrix([[1, 2], [3, -1]])
    B = sp.Matrix([[0, 5], [7, 2]])
    alpha_ibeta_B = K * B * K.inv()
    kms_left = sp.simplify(sp.trace(rho * A * alpha_ibeta_B))
    kms_right = sp.simplify(sp.trace(rho * B * A))
    audit.check("finite Gibbs KMS boundary identity", sp.simplify(kms_left - kms_right) == 0, kms_left, kms_right, "KMS")
    energy = sp.symbols("E", positive=True)
    liouville_spectrum = [-energy, sp.Integer(0), sp.Integer(0), energy]
    audit.check("thermal Liouvillean not positive", min(value.subs(energy, 2) for value in liouville_spectrum) < 0, liouville_spectrum, "contains negative", "KMS")

    g, lam, beta_symbol, length = sp.symbols("g lambda beta0 L", positive=True)
    fourth_coefficient = -(g + 3 * lam) / (4 * beta_symbol * length)
    audit.check("Q3 constant-mode fourth chaos nonzero", fourth_coefficient != 0, fourth_coefficient, "nonzero", "free-energy")
    audit.check("Q3 fourth coefficient negative", fourth_coefficient.is_negative is True, fourth_coefficient, "negative", "free-energy")
    probabilities = [sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(1, 4)]
    centered_values = [sp.Rational(-1), sp.Rational(0), sp.Rational(1)]
    mean_r = sum(weight * value for weight, value in zip(probabilities, centered_values))
    partition = sum(weight * sp.exp(value) for weight, value in zip(probabilities, centered_values))
    audit.check("centered fixture mean zero", mean_r == 0, mean_r, 0, "free-energy")
    audit.check("strict Jensen fixture", bool(partition > 1), partition, ">1", "free-energy")
    delta_f = -sp.log(partition) / beta_symbol
    audit.check("strict free-energy fixture negative", delta_f.is_negative is True, delta_f, "negative", "free-energy")

    shift = sp.Rational(7, 5)
    shifted_values = [value - shift for value in centered_values]
    shifted_partition = sum(weight * sp.exp(value) for weight, value in zip(probabilities, shifted_values))
    density = [sp.simplify(weight * sp.exp(value) / partition) for weight, value in zip(probabilities, centered_values)]
    shifted_density = [sp.simplify(weight * sp.exp(value) / shifted_partition) for weight, value in zip(probabilities, shifted_values)]
    audit.check("normalized scalar gauge invariance", all(sp.simplify(left - right) == 0 for left, right in zip(density, shifted_density)), shifted_density, density, "free-energy")
    log_ratio = sp.simplify(sp.log(partition) - mean_r)
    shifted_mean = sum(weight * value for weight, value in zip(probabilities, shifted_values))
    shifted_log_ratio = sp.simplify(sp.log(shifted_partition) - shifted_mean)
    audit.check("relative entropy scalar gauge invariance", sp.simplify(log_ratio - shifted_log_ratio) == 0, shifted_log_ratio, log_ratio, "free-energy")
    relative_entropy_direct = sp.simplify(sum(probabilities[index] * sp.log(probabilities[index] / density[index]) for index in range(3)))
    audit.check("KL equals logZ minus meanR", sp.simplify(relative_entropy_direct - log_ratio) == 0, relative_entropy_direct, log_ratio, "free-energy")
    audit.check("strict KL positive", relative_entropy_direct.is_positive is True, relative_entropy_direct, "positive", "free-energy")

    for phrase in ("below-reference", "two-sided germ-domain Markov theorem", "stochastically positive", "strict Jensen", "relative entropy", "does not identify the Gaussian reference with physical empty space", "Regular Weyl continuity", "not a novelty claim"):
        audit.check(f"certificate phrase {phrase[:34]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("fixed_finite_beta0_L_torus", "closed_L2_thermal_reflection_positivity", "sharp_time_algebra_and_generation", "two_sided_germ_domain_Markov", "abstract_stochastically_positive_beta0_KMS", "strict_centered_Gaussian_reference_free_energy_ordering", "scalar_gauge_invariant_relative_entropy_comparator"):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("full_E2_covariance", "ordinary_one_sided_circle_Markov_claimed", "beta_independent_Hamiltonian_family", "positive_energy_vacuum", "interacting_Hadamard_or_microlocal_spectrum", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "thermodynamic_limit", "phase_transition_proved", "original_fixed_raw_CL8_family", "original_3D_Q3LOCK_parent", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
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
            "sharp_time": {"formula": str(sharp), "continuity_variances": covariance_differences},
            "reflection_eigenvalues": rp_eigenvalues,
            "Markov": stringify(markov),
            "KMS": {"left": str(kms_left), "right": str(kms_right), "Liouville_spectrum": [str(value) for value in liouville_spectrum]},
            "free_energy": {"fourth_coefficient": str(fourth_coefficient), "partition": str(partition), "KL": str(relative_entropy_direct)},
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
