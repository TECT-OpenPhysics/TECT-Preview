#!/usr/bin/env python3
"""Primary verifier for the Q3 source-pressure and route-split theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import mpmath as mp
import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SOURCE-PRESSURE-PHASE-DIAGNOSTIC-PHYSICAL-REFERENCE-AND-3D-PARENT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-ALL-SOURCE-BOUNDARY-INDEPENDENT-CONVEX-EVEN-PRESSURE-WITH-PHASE-REFERENCE-AND-PARENT-OBSTRUCTIONS"
NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-PRESSURE-VALUE-ONLY-PHASE-CLASSIFICATION",
    "NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL",
]
EXPLORATION_ID = "EXP-000779"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split/result.json"
ST8_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


def sha256(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


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


def logsumexp(values: list[float]) -> float:
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


def normalized(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [weight / total for weight in weights]


def stable_log_cosh(value: float) -> float:
    magnitude = abs(value)
    return magnitude + math.log1p(math.exp(-2.0 * magnitude)) - math.log(2.0)


def kl(probability: list[float], reference: list[float]) -> float:
    return sum(left * math.log(left / right) for left, right in zip(probability, reference))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    st8_parent = json.loads(ST8_PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("EXP771 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP771 all-source base", parent["scope"]["finite_component_GRS_uniform_subdominant_coupling"] is True and parent["scope"]["all_sixteen_full_half_boundary_pressure_density_limits"] is True, parent["scope"], "GRS base", "parent")
    audit.check("ST8 parent all pass", st8_parent["assertions"]["passed"] == st8_parent["assertions"]["total"], st8_parent["assertions"], "all pass", "parent")

    c4, radius, kappa, source = sp.symbols("c4 r k J", positive=True)
    quadratic_gap = sp.factor(c4 * radius**4 / 4 - kappa * radius**2 / 2 + kappa**2 / (4 * c4))
    audit.check("quadratic negative-part absorption", quadratic_gap == (c4 * radius**2 - kappa) ** 2 / (4 * c4), quadratic_gap, "square", "source")
    x = sp.symbols("x", nonnegative=True)
    linear_scaled = sp.factor(x**4 / 4 - x + sp.Rational(3, 4))
    audit.check("linear source Young factorization", linear_scaled == (x - 1) ** 2 * (x**2 + 2 * x + 3) / 4, linear_scaled, "nonnegative factorization", "source")
    audit.check("linear source exponent", sp.Rational(4, 4 - 1) == sp.Rational(4, 3), sp.Rational(4, 3), sp.Rational(4, 3), "source")
    for c4_value in (0.04, 0.2, 1.1):
        for kappa_value in (0.0, 0.7, 2.3):
            for source_value in (0.0, 0.4, 1.9):
                for radius_value in (0.0, 0.3, 1.2, 3.7):
                    lhs = c4_value * radius_value**4 - kappa_value * radius_value**2 / 2 - source_value * radius_value
                    rhs = c4_value * radius_value**4 / 2 - kappa_value**2 / (4 * c4_value) - 0.75 * c4_value ** (-1.0 / 3.0) * source_value ** (4.0 / 3.0)
                    audit.check("combined source coercive bound fixture", lhs + 1e-12 >= rhs, lhs, rhs, "source")

    points = [(-1.4, 0.2), (1.4, -0.2), (-0.3, 1.1), (0.3, -1.1), (0.0, 0.0)]
    base_energy = [0.3 * (first**4 + second**4) + 0.2 * (first - second) ** 2 for first, second in points]
    def finite_distribution(first_source: float, second_source: float) -> list[float]:
        exponents = [-energy + first_source * point[0] + second_source * point[1] for energy, point in zip(base_energy, points)]
        peak = max(exponents)
        return normalized([math.exp(exponent - peak) for exponent in exponents])

    def finite_pressure(first_source: float, second_source: float) -> float:
        exponents = [-energy + first_source * point[0] + second_source * point[1] for energy, point in zip(base_energy, points)]
        return logsumexp(exponents) - math.log(len(points))
    source_rows = []
    for first_source, second_source in ((0.0, 0.0), (0.2, -0.1), (-0.2, 0.1), (0.5, 0.3), (-0.5, -0.3)):
        value = finite_pressure(first_source, second_source)
        opposite = finite_pressure(-first_source, -second_source)
        source_rows.append({"J": [first_source, second_source], "p": value, "p_minus": opposite})
        audit.check("finite source pressure even", abs(value - opposite) < 1e-14, value, opposite, "convexity")
    zero_probability = finite_distribution(0.0, 0.0)
    gradient_zero = [
        sum(probability * point[index] for probability, point in zip(zero_probability, points))
        for index in range(2)
    ]
    audit.check("finite-volume zero source response", max(abs(value) for value in gradient_zero) < 1e-10, gradient_zero, [0.0, 0.0], "convexity")
    directions = [(1.0, 0.0), (0.0, 1.0), (0.7, -0.4), (1.1, 0.8)]
    hessian_rows = []
    tilted_probability = finite_distribution(0.13, -0.07)
    for direction in directions:
        projections = [direction[0] * point[0] + direction[1] * point[1] for point in points]
        mean = sum(probability * value for probability, value in zip(tilted_probability, projections))
        variance = sum(probability * (value - mean) ** 2 for probability, value in zip(tilted_probability, projections))
        hessian_rows.append({"direction": list(direction), "variance": variance})
        audit.check("finite log-MGF Hessian PSD", variance >= 0.0, variance, ">=0", "convexity")

    smooth_cusp_rows = []
    for order in (2, 4, 8, 16, 32, 64):
        values = []
        for h in (-0.7, -0.2, 0.0, 0.2, 0.7):
            value = stable_log_cosh(order * h) / order
            gap = abs(h) - value
            values.append({"h": h, "f": value, "gap": gap})
            audit.check("smooth cusp signed gap nonnegative", gap >= -1e-15, gap, ">=0", "phase")
            audit.check("smooth cusp uniform log2 over n bound", gap <= math.log(2.0) / order + 1e-15, gap, math.log(2.0) / order, "phase")
        smooth_cusp_rows.append({"n": order, "values": values})
    audit.check("smooth even sequence tends cusp", smooth_cusp_rows[-1]["values"][-1]["gap"] < smooth_cusp_rows[0]["values"][-1]["gap"], smooth_cusp_rows, "gap decreases", "phase")
    audit.check("smooth sequence derivative stays zero", all(abs((math.tanh(order * 0.0))) < 1e-15 for order in (2, 4, 8, 16, 32, 64)), 0.0, 0.0, "phase")
    alpha, cusp = 0.43, 0.37
    h_grid = [-1.0 + index * 0.01 for index in range(201)]
    smooth_values = [alpha + cusp * stable_log_cosh(h) for h in h_grid]
    cusp_values = [alpha + cusp * abs(h) for h in h_grid]
    smooth_second = [smooth_values[index + 1] - 2 * smooth_values[index] + smooth_values[index - 1] for index in range(1, len(h_grid) - 1)]
    cusp_second = [cusp_values[index + 1] - 2 * cusp_values[index] + cusp_values[index - 1] for index in range(1, len(h_grid) - 1)]
    audit.check("same pressure value different cusp", smooth_values[100] == cusp_values[100] == alpha, (smooth_values[100], cusp_values[100]), alpha, "phase")
    audit.check("smooth and cusp fixtures convex", min(smooth_second) >= -1e-12 and min(cusp_second) >= -1e-12, (min(smooth_second), min(cusp_second)), ">=0", "phase")
    step = 1e-6
    smooth_right = (alpha + cusp * stable_log_cosh(step) - alpha) / step
    cusp_right = (alpha + cusp * step - alpha) / step
    audit.check("smooth control zero derivative", abs(smooth_right) < 1e-6, smooth_right, 0.0, "phase")
    audit.check("cusp right derivative positive", abs(cusp_right - cusp) < 1e-10, cusp_right, cusp, "phase")

    energies = [0.2, 0.9, 1.7, 2.8]
    reference = normalized([math.exp(-0.1 * index) for index in range(len(energies))])
    boltzmann = [reference[index] * math.exp(-energy) for index, energy in enumerate(energies)]
    partition = sum(boltzmann)
    interacting = [weight / partition for weight in boltzmann]
    shift = 2.4
    shifted_boltzmann = [reference[index] * math.exp(-(energy + shift)) for index, energy in enumerate(energies)]
    shifted_partition = sum(shifted_boltzmann)
    shifted = [weight / shifted_partition for weight in shifted_boltzmann]
    pressure = math.log(partition)
    shifted_pressure = math.log(shifted_partition)
    relative_entropy = kl(interacting, reference)
    shifted_relative_entropy = kl(shifted, reference)
    expected_relative_entropy = -sum(probability * energy for probability, energy in zip(interacting, energies)) - pressure
    shifted_expected_relative_entropy = -sum(probability * (energy + shift) for probability, energy in zip(shifted, energies)) - shifted_pressure
    audit.check("scalar shift normalized law invariant", max(abs(left - right) for left, right in zip(interacting, shifted)) < 1e-15, shifted, interacting, "reference")
    audit.check("Gibbs KL identity", abs(relative_entropy - expected_relative_entropy) < 1e-14, relative_entropy, expected_relative_entropy, "reference")
    audit.check("shifted Gibbs KL identity", abs(shifted_relative_entropy - shifted_expected_relative_entropy) < 1e-14, shifted_relative_entropy, shifted_expected_relative_entropy, "reference")
    audit.check("scalar shift KL invariant", abs(relative_entropy - shifted_relative_entropy) < 1e-15, shifted_relative_entropy, relative_entropy, "reference")
    audit.check("scalar shift pressure covariance", abs(shifted_pressure - (pressure - shift)) < 1e-14, shifted_pressure, pressure - shift, "reference")

    q, r = sp.symbols("q r", real=True)
    phi_one = (q + r) / sp.sqrt(2)
    phi_two = (q - r) / sp.sqrt(2)
    transverse = sp.expand(phi_one**4 + phi_two**4)
    transverse_expected = q**4 / 2 + 3 * q**2 * r**2 + r**4 / 2
    audit.check("exact transverse two-cell quartic identity", sp.simplify(transverse - transverse_expected) == 0, transverse, transverse_expected, "parent")
    mp.mp.dps = 40
    marginal_rows = []
    a_value, b_value = mp.mpf("1.3"), mp.mpf("0.27")
    for q_value in (mp.mpf("0"), mp.mpf("0.4"), mp.mpf("0.9"), mp.mpf("1.5")):
        denominator = mp.quad(lambda rr: mp.e ** (-(a_value / 2 + 3 * b_value * q_value**2) * rr**2 - b_value * rr**4 / 2), [-mp.inf, mp.inf])
        second_moment_numerator = mp.quad(lambda rr: rr**2 * mp.e ** (-(a_value / 2 + 3 * b_value * q_value**2) * rr**2 - b_value * rr**4 / 2), [-mp.inf, mp.inf])
        fourth_moment_numerator = mp.quad(lambda rr: rr**4 * mp.e ** (-(a_value / 2 + 3 * b_value * q_value**2) * rr**2 - b_value * rr**4 / 2), [-mp.inf, mp.inf])
        effective = -mp.log(denominator)
        second_moment = second_moment_numerator / denominator
        fourth_moment = fourth_moment_numerator / denominator
        derivative = 3 * b_value * second_moment
        second_derivative = -9 * b_value**2 * (fourth_moment - second_moment**2)
        marginal_rows.append({"q": str(q_value), "F": str(effective), "dF_dq2": str(derivative), "d2F_dq2_2": str(second_derivative)})
        audit.check("discarded-mode effective derivative positive", derivative > 0, derivative, ">0", "parent")
        audit.check("discarded-mode effective curvature negative", second_derivative < 0, second_derivative, "<0", "parent")
    baseline_effective = mp.mpf(marginal_rows[0]["F"])
    for row in marginal_rows:
        row["F_minus_F0"] = str(mp.mpf(row["F"]) - baseline_effective)
    audit.check("discarded-mode effective term nonconstant", all(mp.mpf(marginal_rows[index + 1]["F"]) > mp.mpf(marginal_rows[index]["F"]) for index in range(len(marginal_rows) - 1)), marginal_rows, "strictly increasing in q squared", "parent")

    for phrase in (
        "All-source pressure theorem",
        "Directional derivative and order of limits",
        "Exact phase-information boundary",
        "Physical-reference obstruction",
        "Exact restriction-versus-marginal obstruction",
        "both side lengths tending independently to infinity",
        "difference quotient",
        "full registered ST8/Q3LOCK marginal",
        "not a claim that either function is the Q3 pressure",
        "No result here identifies the named Gaussian comparator with physical empty space",
        "This proves Pre-A. UPHELD AS FALSE",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    positive_scope = (
        "constant_vector_source_Q3_interaction",
        "linear_source_subdominant_exponent_4_over_3",
        "all_source_pressure_exists_and_finite",
        "all_source_boundary_Wick_independence",
        "source_pressure_locally_uniform",
        "source_pressure_convex",
        "source_pressure_global_Z2_even",
        "source_pressure_origin_equals_alpha_infinity",
        "directional_one_sided_derivatives_exist",
        "pressure_cusp_diagnostic_defined",
        "finite_volume_zero_source_response",
        "thermodynamic_then_zero_source_order_required",
        "pressure_value_only_phase_classification_refuted",
        "additive_scalar_absolute_reference_no_go_reused",
        "bare_transverse_restriction_suffices_for_interacting_marginal_inference_refuted",
    )
    false_scope = (
        "any_Q3_cusp_sign_determined",
        "Q3_phase_transition_or_phase_uniqueness",
        "source_selected_infinite_volume_states",
        "plus_minus_state_purity_or_clustering",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
        "common_renormalized_stress_tensor_anchor",
        "original_fixed_raw_CL8_family",
        "fixed_lattice_3D_Q3LOCK_thermodynamic_limit",
        "original_3D_Q3LOCK_parent_derived",
        "exact_effective_dimensional_reduction",
        "zero_temperature_state_limit",
        "ground_vector_limit",
        "uniform_spectral_gap",
        "correlation_function_limit_interchange",
        "interacting_Hadamard_or_microlocal_spectrum",
        "physical_light_speed_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    )
    for key in positive_scope:
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("exact scope keyset", set(manifest["scope"]) == set(positive_scope) | set(false_scope), sorted(manifest["scope"]), sorted(set(positive_scope) | set(false_scope)), "scope")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": NEGATIVE_IDS,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": NEXT_GATE,
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "parent": sha256(PARENT), "st8_parent": sha256(ST8_PARENT)},
        "derived": {
            "source": {"quadratic_gap": str(quadratic_gap), "linear_scaled": str(linear_scaled), "rows": source_rows, "hessian_rows": hessian_rows},
            "phase": {"smooth_cusp": smooth_cusp_rows, "alpha": alpha, "cusp": cusp},
            "reference": {"reference": reference, "probability": interacting, "shifted_probability": shifted, "KL": relative_entropy, "expected_KL": expected_relative_entropy, "pressure": pressure, "shifted_pressure": shifted_pressure},
            "parent": {"quartic_identity": str(transverse), "marginal": marginal_rows},
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
