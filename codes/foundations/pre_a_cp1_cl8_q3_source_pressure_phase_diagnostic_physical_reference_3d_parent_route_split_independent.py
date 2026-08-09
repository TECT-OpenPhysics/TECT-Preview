#!/usr/bin/env python3
"""Independent stdlib audit of the EXP772 Q3 source-pressure route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SOURCE-PRESSURE-PHASE-DIAGNOSTIC-PHYSICAL-REFERENCE-AND-3D-PARENT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-ALL-SOURCE-BOUNDARY-INDEPENDENT-CONVEX-EVEN-PRESSURE-WITH-PHASE-REFERENCE-AND-PARENT-OBSTRUCTIONS"
NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-PRESSURE-VALUE-ONLY-PHASE-CLASSIFICATION",
    "NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL",
]
PARENT_IDS = [
    "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0",
    "PA-CP1-ST8-Q3LOCK-v0",
]
EXPLORATION_ID = "EXP-000779"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
EXP771_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split/result.json"
ST8_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"


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
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def polynomial_multiply(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for left_power, left_value in enumerate(left):
        for right_power, right_value in enumerate(right):
            result[left_power + right_power] += left_value * right_value
    return result


def polynomial_value(coefficients: list[Fraction], value: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def logsumexp(values: list[float]) -> float:
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


def stable_log_cosh(value: float) -> float:
    absolute = abs(value)
    if absolute < 20.0:
        return math.log(math.cosh(value))
    return absolute + math.log1p(math.exp(-2.0 * absolute)) - math.log(2.0)


def discrete_gibbs(
    reference: list[float], energies: list[float], observables: list[float], source: float, shift: float = 0.0
) -> tuple[float, list[float], list[float]]:
    actions = [energy - source * observable + shift for energy, observable in zip(energies, observables)]
    scores = [math.log(weight) - action for weight, action in zip(reference, actions)]
    log_partition = logsumexp(scores)
    probability = [math.exp(score - log_partition) for score in scores]
    return log_partition, probability, actions


def relative_entropy(probability: list[float], reference: list[float]) -> float:
    return sum(left * math.log(left / right) for left, right in zip(probability, reference))


def simpson_even(function: Callable[[float], float], upper: float, panels: int) -> float:
    if panels <= 0 or panels % 2:
        raise ValueError("composite Simpson requires a positive even panel count")
    step = upper / panels
    total = function(0.0) + function(upper)
    for index in range(1, panels):
        total += (4.0 if index % 2 else 2.0) * function(index * step)
    return 2.0 * step * total / 3.0


def transverse_moments(squared_q: float, quadratic: float, quartic: float) -> tuple[float, float, float]:
    upper = 8.0
    panels = 12000
    coefficient = quadratic / 2.0 + 3.0 * quartic * squared_q

    def density(radius: float) -> float:
        square = radius * radius
        return math.exp(-coefficient * square - quartic * square * square / 2.0)

    integral0 = simpson_even(density, upper, panels)
    integral2 = simpson_even(lambda radius: radius * radius * density(radius), upper, panels)
    integral4 = simpson_even(lambda radius: radius**4 * density(radius), upper, panels)
    return integral0, integral2, integral4


def transverse_effective(squared_q: float, quadratic: float, quartic: float) -> tuple[float, float, float]:
    integral0, integral2, integral4 = transverse_moments(squared_q, quadratic, quartic)
    mean2 = integral2 / integral0
    mean4 = integral4 / integral0
    first = 3.0 * quartic * mean2
    second = -9.0 * quartic * quartic * (mean4 - mean2 * mean2)
    return -math.log(integral0), first, second


def transformed_two_cell_action(q: float, r: float, quadratic: float, quartic: float) -> float:
    return (
        quadratic * (q * q + r * r) / 2.0
        + quartic * (q**4 / 2.0 + 3.0 * q * q * r * r + r**4 / 2.0)
    )


def original_two_cell_action(q: float, r: float, quadratic: float, quartic: float) -> float:
    root_two = math.sqrt(2.0)
    phi_one = (q + r) / root_two
    phi_two = (q - r) / root_two
    return quadratic * (phi_one * phi_one + phi_two * phi_two) / 2.0 + quartic * (
        phi_one**4 + phi_two**4
    )


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    exp771 = json.loads(EXP771_PARENT.read_text(encoding="utf-8"))
    st8 = json.loads(ST8_PARENT.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("independent parent ids", manifest["parent_ids"] == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check(
        "independent EXP771 parent all pass",
        exp771["assertion_summary"]["passed"] == exp771["assertion_summary"]["total"],
        exp771["assertion_summary"],
        "all pass",
        "parent",
    )
    audit.check(
        "independent EXP771 source base",
        exp771["scope"]["finite_component_GRS_uniform_subdominant_coupling"] is True
        and exp771["scope"]["all_sixteen_full_half_boundary_pressure_density_limits"] is True,
        exp771["scope"],
        "finite-component all-boundary GRS base",
        "parent",
    )
    audit.check(
        "independent ST8 parent all pass",
        st8["assertions"]["passed"] == st8["assertions"]["total"],
        st8["assertions"],
        "all pass",
        "parent",
    )
    audit.check(
        "independent ST8 exact finite candidate retained",
        st8["scope"]["exact_finite_nonlinear_locking_theorem"] is True
        and st8["scope"]["one_connected_interaction_graph_candidate"] is True,
        st8["scope"],
        "finite candidate only",
        "parent",
    )
    audit.check(
        "independent ST8 thermodynamic and physical gates remain open",
        st8["scope"]["thermodynamic_phase_transition"] is False
        and st8["scope"]["interacting_quantum_continuum_limit"] is False
        and st8["scope"]["physical_vacuum"] is False
        and st8["scope"]["Pre_A_complete"] is False,
        st8["scope"],
        "all false",
        "parent",
    )

    linear_left = [Fraction(3, 4), Fraction(-1), Fraction(0), Fraction(0), Fraction(1, 4)]
    linear_right = polynomial_multiply(
        [Fraction(1), Fraction(-2), Fraction(1)],
        [Fraction(3, 4), Fraction(1, 2), Fraction(1, 4)],
    )
    audit.check("independent exact linear Young identity", linear_left == linear_right, linear_left, linear_right, "source")
    for value in (Fraction(0), Fraction(1, 7), Fraction(1), Fraction(9, 5), Fraction(13, 3)):
        gap = polynomial_value(linear_left, value)
        audit.check("independent linear Young nonnegative fixture", gap >= 0, gap, ">=0", "source")

    c4 = Fraction(7, 5)
    negative_norm = Fraction(11, 6)
    quadratic_left = [negative_norm**2 / (4 * c4), -negative_norm / 2, c4 / 4]
    quadratic_right = [coefficient / (4 * c4) for coefficient in polynomial_multiply([-negative_norm, c4], [-negative_norm, c4])]
    audit.check("independent exact quadratic absorption identity", quadratic_left == quadratic_right, quadratic_left, quadratic_right, "source")
    for squared_radius in (Fraction(0), Fraction(2, 9), negative_norm / c4, Fraction(17, 4)):
        gap = polynomial_value(quadratic_left, squared_radius)
        audit.check("independent quadratic absorption nonnegative fixture", gap >= 0, gap, ">=0", "source")
    audit.check("independent linear source exponent", Fraction(4, 4 - 1) == Fraction(4, 3), Fraction(4, 3), Fraction(4, 3), "source")

    coercive_rows: list[dict[str, str]] = []
    for cube_root_c4 in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 2)):
        local_c4 = cube_root_c4**3
        for source_root in (Fraction(0), Fraction(1, 3), Fraction(5, 4)):
            source = source_root**3
            for local_k in (Fraction(0), Fraction(2, 5), Fraction(7, 3)):
                for radius in (Fraction(0), Fraction(1, 4), Fraction(7, 5), Fraction(3)):
                    left = local_c4 * radius**4 - local_k * radius**2 / 2 - source * radius
                    right = (
                        local_c4 * radius**4 / 2
                        - local_k**2 / (4 * local_c4)
                        - Fraction(3, 4) * source_root**4 / cube_root_c4
                    )
                    coercive_rows.append({"lhs": str(left), "rhs": str(right)})
                    audit.check("independent exact combined source coercivity", left >= right, left, right, "source")

    reference = [float(value) for value in (Fraction(1, 9), Fraction(2, 9), Fraction(3, 9), Fraction(2, 9), Fraction(1, 9))]
    observables = [-2.0, -1.0, 0.0, 1.0, 2.0]
    energies = [0.7, 0.2, 0.0, 0.2, 0.7]
    pressure_rows: list[dict[str, float]] = []
    for source in (-0.83, -0.31, 0.0, 0.31, 0.83):
        pressure, probability, _ = discrete_gibbs(reference, energies, observables, source)
        opposite, _, _ = discrete_gibbs(reference, energies, observables, -source)
        mean = sum(weight * observable for weight, observable in zip(probability, observables))
        variance = sum(weight * (observable - mean) ** 2 for weight, observable in zip(probability, observables))
        pressure_rows.append({"J": source, "pressure": pressure, "mean": mean, "variance": variance})
        audit.check("independent finite pressure global Z2", abs(pressure - opposite) < 2e-15, pressure, opposite, "convexity")
        audit.check("independent finite pressure Hessian variance positive", variance > 0.0, variance, ">0", "convexity")
    zero_pressure, zero_probability, _ = discrete_gibbs(reference, energies, observables, 0.0)
    zero_mean = sum(weight * observable for weight, observable in zip(zero_probability, observables))
    audit.check("independent finite-volume zero-source derivative", abs(zero_mean) < 1e-15, zero_mean, 0.0, "convexity")
    finite_step = 1e-5
    test_source = 0.37
    center, test_probability, _ = discrete_gibbs(reference, energies, observables, test_source)
    plus, _, _ = discrete_gibbs(reference, energies, observables, test_source + finite_step)
    minus, _, _ = discrete_gibbs(reference, energies, observables, test_source - finite_step)
    mean = sum(weight * observable for weight, observable in zip(test_probability, observables))
    variance = sum(weight * (observable - mean) ** 2 for weight, observable in zip(test_probability, observables))
    finite_gradient = (plus - minus) / (2.0 * finite_step)
    finite_hessian = (plus - 2.0 * center + minus) / finite_step**2
    audit.check("independent finite log-MGF gradient", abs(finite_gradient - mean) < 2e-9, finite_gradient, mean, "convexity")
    audit.check("independent finite log-MGF Hessian", abs(finite_hessian - variance) < 3e-6, finite_hessian, variance, "convexity")

    cusp_rows: list[dict[str, float | int]] = []
    for order in (1, 2, 5, 20, 100, 1000):
        for field in (-3.0, -0.7, -0.05, 0.0, 0.05, 0.7, 3.0):
            approximation = stable_log_cosh(order * field) / order
            gap = abs(field) - approximation
            bound = math.log(2.0) / order
            cusp_rows.append({"n": order, "h": field, "value": approximation, "gap": gap, "bound": bound})
            audit.check("independent stable log-cosh even", abs(approximation - stable_log_cosh(-order * field) / order) < 2e-15, approximation, "even", "phase")
            audit.check("independent local-uniform cusp gap", gap >= -2e-15 and gap <= bound + 2e-15, gap, f"[0,{bound}]", "phase")
    fixed_field = 0.2
    thermodynamic_quotients = [stable_log_cosh(order * fixed_field) / (order * fixed_field) for order in (5, 20, 100, 1000)]
    fixed_order = 7
    zero_source_quotients = [stable_log_cosh(fixed_order * field) / (fixed_order * field) for field in (0.1, 0.01, 0.001, 0.0001)]
    audit.check("independent thermodynamic-first quotient tends cusp slope", thermodynamic_quotients[-1] > 0.996, thermodynamic_quotients, 1.0, "phase")
    audit.check("independent zero-source-first quotient tends zero", abs(zero_source_quotients[-1]) < 4e-4, zero_source_quotients, 0.0, "phase")
    audit.check("independent every finite approximation derivative zero", all(math.tanh(order * 0.0) == 0.0 for order in (1, 2, 5, 20, 100, 1000)), 0.0, 0.0, "phase")

    source = 0.43
    shift = 1.7
    unshifted_pressure, unshifted_probability, unshifted_actions = discrete_gibbs(
        reference, energies, observables, source
    )
    shifted_pressure, shifted_probability, shifted_actions = discrete_gibbs(
        reference, energies, observables, source, shift
    )
    unshifted_kl = relative_entropy(unshifted_probability, reference)
    shifted_kl = relative_entropy(shifted_probability, reference)
    unshifted_identity = -sum(weight * action for weight, action in zip(unshifted_probability, unshifted_actions)) - unshifted_pressure
    shifted_identity = -sum(weight * action for weight, action in zip(shifted_probability, shifted_actions)) - shifted_pressure
    zero_source_unshifted, _, _ = discrete_gibbs(reference, energies, observables, 0.0)
    zero_source_shifted, _, _ = discrete_gibbs(reference, energies, observables, 0.0, shift)
    audit.check("independent reference-weighted Gibbs normalization", abs(sum(unshifted_probability) - 1.0) < 2e-15, sum(unshifted_probability), 1.0, "reference")
    audit.check("independent scalar shift normalized Gibbs invariant", max(abs(left - right) for left, right in zip(unshifted_probability, shifted_probability)) < 2e-15, shifted_probability, unshifted_probability, "reference")
    audit.check("independent scalar shift pressure", abs(shifted_pressure - (unshifted_pressure - shift)) < 2e-15, shifted_pressure, unshifted_pressure - shift, "reference")
    audit.check("independent reference-weighted KL identity", abs(unshifted_kl - unshifted_identity) < 2e-15, unshifted_kl, unshifted_identity, "reference")
    audit.check("independent shifted reference-weighted KL identity", abs(shifted_kl - shifted_identity) < 2e-15, shifted_kl, shifted_identity, "reference")
    audit.check("independent scalar shift KL invariant", abs(shifted_kl - unshifted_kl) < 2e-15, shifted_kl, unshifted_kl, "reference")
    audit.check(
        "independent source-pressure difference invariant",
        abs((shifted_pressure - zero_source_shifted) - (unshifted_pressure - zero_source_unshifted)) < 2e-15,
        shifted_pressure - zero_source_shifted,
        unshifted_pressure - zero_source_unshifted,
        "reference",
    )

    for q_value, r_value in (
        (Fraction(0), Fraction(0)),
        (Fraction(2, 5), Fraction(-3, 7)),
        (Fraction(7, 4), Fraction(5, 6)),
        (Fraction(-9, 8), Fraction(11, 10)),
    ):
        quartic_original = ((q_value + r_value) ** 4 + (q_value - r_value) ** 4) / 4
        quartic_transformed = q_value**4 / 2 + 3 * q_value**2 * r_value**2 + r_value**4 / 2
        audit.check("independent exact two-cell quartic identity", quartic_original == quartic_transformed, quartic_original, quartic_transformed, "parent")

    quadratic = 1.3
    quartic = 0.27
    action_rows: list[dict[str, float]] = []
    for q_value, r_value in ((0.0, 0.0), (0.4, -0.7), (1.1, 0.3), (-1.5, 1.2)):
        original = original_two_cell_action(q_value, r_value, quadratic, quartic)
        transformed = transformed_two_cell_action(q_value, r_value, quadratic, quartic)
        action_rows.append({"q": q_value, "r": r_value, "original": original, "transformed": transformed})
        audit.check("independent full two-cell action transform", abs(original - transformed) < 3e-15, original, transformed, "parent")

    effective_rows: list[dict[str, float]] = []
    previous_effective: float | None = None
    for squared_q in (0.0, 0.16, 0.81, 2.25):
        effective, first, second = transverse_effective(squared_q, quadratic, quartic)
        effective_rows.append({"q_squared": squared_q, "F": effective, "F_prime": first, "F_second": second})
        audit.check("independent transverse F prime positive", first > 0.0, first, ">0", "parent")
        audit.check("independent transverse F second negative", second < 0.0, second, "<0", "parent")
        if previous_effective is not None:
            audit.check("independent transverse effective term nonconstant", effective > previous_effective, effective, f">{previous_effective}", "parent")
        previous_effective = effective

    differentiation_point = 0.64
    differentiation_step = 0.001
    center_effective, analytic_first, analytic_second = transverse_effective(
        differentiation_point, quadratic, quartic
    )
    plus_effective, _, _ = transverse_effective(differentiation_point + differentiation_step, quadratic, quartic)
    minus_effective, _, _ = transverse_effective(differentiation_point - differentiation_step, quadratic, quartic)
    numerical_first = (plus_effective - minus_effective) / (2.0 * differentiation_step)
    numerical_second = (plus_effective - 2.0 * center_effective + minus_effective) / differentiation_step**2
    audit.check("independent Simpson F prime formula", abs(numerical_first - analytic_first) < 2e-7, numerical_first, analytic_first, "parent")
    audit.check("independent Simpson F second formula", abs(numerical_second - analytic_second) < 2e-6, numerical_second, analytic_second, "parent")

    marginal_rows: list[dict[str, float]] = []
    for q_value in (0.0, 0.4, 0.9, 1.5):
        restricted = quadratic * q_value * q_value / 2.0 + quartic * q_value**4 / 2.0
        effective, _, _ = transverse_effective(q_value * q_value, quadratic, quartic)
        direct_integral = simpson_even(
            lambda r_value: math.exp(-original_two_cell_action(q_value, r_value, quadratic, quartic)),
            8.0,
            12000,
        )
        direct_action = -math.log(direct_integral)
        reconstructed_action = restricted + effective
        marginal_rows.append(
            {
                "q": q_value,
                "restricted": restricted,
                "effective": effective,
                "direct_action": direct_action,
                "reconstructed_action": reconstructed_action,
            }
        )
        audit.check("independent full marginal action reconstruction", abs(direct_action - reconstructed_action) < 3e-12, direct_action, reconstructed_action, "parent")

    for phrase in (
        "All-source pressure theorem",
        "formally stated its uniform perturbation theorem only",
        "difference quotient",
        "fully differentiable at `J=0` exactly when",
        "restricts the **source variable**",
        "not a field restriction",
        "Physical-reference obstruction",
        "does not calculate the full registered ST8/Q3LOCK marginal",
        "four-dimensional Euclidean construction",
        "This proves Pre-A. UPHELD AS FALSE",
    ):
        audit.check(f"independent certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")

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
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check(
        "independent exact scope keyset",
        set(manifest["scope"]) == set(positive_scope) | set(false_scope),
        sorted(manifest["scope"]),
        sorted(set(positive_scope) | set(false_scope)),
        "scope",
    )
    audit.check("independent next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "EXP771_parent": sha256(EXP771_PARENT),
            "ST8_parent": sha256(ST8_PARENT),
        },
        "derived": {
            "source": {
                "linear_identity": [str(value) for value in linear_left],
                "quadratic_identity": [str(value) for value in quadratic_left],
                "coercive_rows": coercive_rows,
            },
            "convexity": {
                "pressure_rows": pressure_rows,
                "gradient": finite_gradient,
                "mean": mean,
                "hessian": finite_hessian,
                "variance": variance,
            },
            "phase": {
                "log_cosh_rows": cusp_rows,
                "thermodynamic_first": thermodynamic_quotients,
                "zero_source_first": zero_source_quotients,
            },
            "reference": {
                "probability": unshifted_probability,
                "shifted_probability": shifted_probability,
                "KL": unshifted_kl,
                "shifted_KL": shifted_kl,
                "pressure": unshifted_pressure,
                "shifted_pressure": shifted_pressure,
            },
            "parent": {
                "action_rows": action_rows,
                "effective_rows": effective_rows,
                "differentiation": {
                    "analytic_first": analytic_first,
                    "numerical_first": numerical_first,
                    "analytic_second": analytic_second,
                    "numerical_second": numerical_second,
                },
                "marginal_rows": marginal_rows,
            },
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
