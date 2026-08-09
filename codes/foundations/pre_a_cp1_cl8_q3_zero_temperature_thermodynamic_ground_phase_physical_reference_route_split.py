#!/usr/bin/env python3
"""Primary verifier for the Q3 zero-temperature density theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-ZERO-TEMPERATURE-THERMODYNAMIC-GROUND-PHASE-AND-PHYSICAL-REFERENCE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-SHARP-CUTOFF-GRS-MONOTONE-STRICT-VACUUM-DENSITY-AND-PERIODIC-BRIDGE-REDUCTION"
NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-FINITE-CIRCLE-WITNESS-ZERO-TEMPERATURE-DENSITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-VOLUME-UI-PERIODIC-SHARP-SURFACE-PAIRING",
]
EXPLORATION_ID = "EXP-000777"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-thermodynamic-pressure-relative-entropy-density-phase-route-split/result.json"
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


def cube_edges() -> list[tuple[int, int]]:
    return [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]


def holder_moment(weights: list[float], values: list[float], exponent: float) -> tuple[float, float]:
    left = sum(weight * value**exponent for weight, value in zip(weights, values))
    right = sum(weight * value for weight, value in zip(weights, values)) ** exponent
    return left, right


def two_level_ground(diagonal: float, off_diagonal: float) -> float:
    return 0.5 * (diagonal - math.sqrt(diagonal * diagonal + 4.0 * off_diagonal * off_diagonal))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("EXP768 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP768 strict fixed-beta parent", parent["scope"]["strict_positive_specific_relative_entropy_density"] is True, parent["scope"]["strict_positive_specific_relative_entropy_density"], True, "parent")

    edges = cube_edges()
    q = sp.symbols("q0:8", real=True)
    g, lam = sp.symbols("g lambda", positive=True)
    W4 = g * sum(value**4 for value in q) / 4 + lam * sum((q[left] - q[right]) ** 2 * (q[left] ** 2 + q[right] ** 2) for left, right in edges) / 4
    pure = sp.Poly(W4, q).coeff_monomial(q[0] ** 4)
    audit.check("Q3 twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 pure quartic coefficient", sp.simplify(pure - (g + 3 * lam) / 4) == 0, pure, (g + 3 * lam) / 4, "Q3")
    probes = [tuple(float((index + 1) * ((-1) ** (index + shift))) for index in range(8)) for shift in (0, 1)]
    g_value, lambda_value = 1.3, 0.42
    coercivity_rows = []
    for probe in probes:
        substitution = {q[index]: probe[index] for index in range(8)} | {g: g_value, lam: lambda_value}
        w_value = float(W4.subs(substitution))
        norm_four = sum(value * value for value in probe) ** 2
        lower = g_value * norm_four / 32.0
        coercivity_rows.append({"W4": w_value, "lower": lower})
        audit.check("Q3 radial coercivity probe", w_value + 1e-12 >= lower, w_value, lower, "Q3")
    mixed_axis = lambda x, y: x * x * y * y
    audit.check("mixed-axis counterexample has flat ray", mixed_axis(2.0, 0.0) == 0.0, mixed_axis(2.0, 0.0), 0.0, "normalizability")
    onsite_ray = g_value * 2.0**4 / 4.0
    audit.check("Q3 onsite removes flat ray", onsite_ray > 0.0, onsite_ray, "positive", "normalizability")
    radial, norm_k = sp.symbols("r normK", positive=True)
    scalar_bound = g * radial**2 / 32 - norm_k * radial / 2
    minimizer = 8 * norm_k / g
    audit.check("Q3 arbitrary quadratic stability", sp.simplify(scalar_bound.subs(radial, minimizer) + 2 * norm_k**2 / g) == 0, scalar_bound.subs(radial, minimizer), -2 * norm_k**2 / g, "normalizability")

    weights = [0.17, 0.28, 0.55]
    positive_values = [0.31, 1.7, 4.2]
    holder_rows = []
    for exponent in (0.2, 0.47, 0.81):
        left, right = holder_moment(weights, positive_values, exponent)
        holder_rows.append({"a": exponent, "left": left, "right": right})
        audit.check(f"spectral Holder probability inequality a={exponent}", left <= right + 1e-14, left, right, "GRS")

    alpha_infinity = 0.83
    lengths = [0.5, 1.0, 2.0, 4.0, 8.0]
    alphas = [alpha_infinity * (1.0 - math.exp(-length)) for length in lengths]
    energies = [-length * alpha for length, alpha in zip(lengths, alphas)]
    audit.check("GRS alpha monotone fixture", all(alphas[index + 1] > alphas[index] for index in range(len(alphas) - 1)), alphas, "strictly increasing", "GRS")
    audit.check("GRS alpha bounded fixture", all(0.0 < alpha < alpha_infinity for alpha in alphas), alphas, alpha_infinity, "GRS")
    scaling_rows = []
    for length in (1.2, 2.7, 5.3):
        for fraction in (0.25, 0.5, 0.8):
            alpha_l = alpha_infinity * (1.0 - math.exp(-length))
            alpha_al = alpha_infinity * (1.0 - math.exp(-fraction * length))
            energy_l = -length * alpha_l
            energy_al = -fraction * length * alpha_al
            scaling_rows.append({"l": length, "a": fraction, "E_al": energy_al, "aE_l": fraction * energy_l})
            audit.check("GRS energy scaling implication", energy_al >= fraction * energy_l - 1e-14, energy_al, fraction * energy_l, "GRS")

    ground_energy, overlap = -1.37, 0.16
    spectral_rows = []
    for time in (2.0, 4.0, 8.0, 16.0):
        excited_energy = 0.45
        z_value = overlap**2 * math.exp(-time * ground_energy) + (1.0 - overlap**2) * math.exp(-time * excited_energy)
        rate = math.log(z_value) / time
        spectral_rows.append({"t": time, "rate": rate})
        audit.check("ground spectral squeeze", ground_energy * -1.0 + 2.0 * math.log(overlap) / time <= rate <= -ground_energy + 1e-14, rate, -ground_energy, "GRS")
    audit.check("ground spectral rate converges", abs(spectral_rows[-1]["rate"] + ground_energy) < abs(spectral_rows[0]["rate"] + ground_energy), spectral_rows, -ground_energy, "GRS")

    mp.mp.dps = 35
    mass = mp.mpf("1.17")
    interval_length = mp.mpf("1.4")
    c4 = mp.mpf(str((g_value + 3.0 * lambda_value) / 4.0))
    covariance = lambda radius: mp.besselk(0, mass * radius) / (2 * mp.pi)
    interval_integral = 2 * mp.quad(lambda radius: (interval_length - radius) * covariance(radius) ** 4, [0, interval_length])
    witness_norm_sq = c4**2 * math.factorial(4) * interval_integral
    audit.check("sharp Q3 four-particle norm positive", witness_norm_sq > 0, witness_norm_sq, "positive", "strictness")
    off_diagonal = float(mp.sqrt(witness_norm_sq))
    rayleigh_ground = two_level_ground(2.6, off_diagonal)
    audit.check("sharp two-vector ground strictness", rayleigh_ground < 0.0, rayleigh_ground, "negative", "strictness")
    audit.check("strict alpha seed", -rayleigh_ground / float(interval_length) > 0.0, -rayleigh_ground / float(interval_length), "positive", "strictness")

    boundary_rows = []
    boundary_constant = 3.1
    for side in (4.0, 8.0, 16.0, 32.0):
        area = side * side
        perimeter = 4.0 * side
        density_error = boundary_constant * (perimeter + 1.0) / area
        energy_error = boundary_constant / side
        boundary_rows.append({"side": side, "surface_over_area": density_error, "energy_over_length": energy_error})
    audit.check("formal surface bound would vanish per area", all(boundary_rows[index + 1]["surface_over_area"] < boundary_rows[index]["surface_over_area"] for index in range(3)), boundary_rows, "conditional scaling to zero", "boundary")
    audit.check("formal O1 energy bridge would vanish per length", all(boundary_rows[index + 1]["energy_over_length"] < boundary_rows[index]["energy_over_length"] for index in range(3)), boundary_rows, "conditional scaling to zero", "boundary")
    cutoff_rows = []
    for cutoff in (8, 16, 32, 64):
        ultraviolet_pairing = 1.0 + 0.7 / cutoff
        covariance_surface_norm = 2.3 - 0.4 / cutoff
        cutoff_rows.append({"cutoff": cutoff, "pairing": ultraviolet_pairing, "surface_norm": covariance_surface_norm, "product": ultraviolet_pairing * covariance_surface_norm})
    audit.check("finite fixture cannot certify uniform surface pairing", max(row["product"] for row in cutoff_rows) < 3.0, cutoff_rows, "finite fixture only", "boundary")

    alpha_limit, e_plane, trace_k, G_value = 0.37, -0.22, 1.6, 2.1
    beta_rows = []
    for beta in (1.5, 3.0, 6.0, 12.0):
        a_beta = float(sum(mp.besselk(0, mass * index * beta) for index in range(1, 40)) / mp.pi)
        trial_density = e_plane + 0.5 * a_beta * trace_k + 6.0 * a_beta * a_beta * G_value
        centered_boundary_error = 0.23 / beta
        centered_energy_density = -alpha_limit + centered_boundary_error
        raw_energy_density = trial_density + centered_energy_density
        specific_kl = trial_density - raw_energy_density
        beta_rows.append({"beta": beta, "a_beta": a_beta, "trial_density": trial_density, "raw_energy_density": raw_energy_density, "specific_KL": specific_kl})
    audit.check("circle scalar tends plane scalar", abs(beta_rows[-1]["trial_density"] - e_plane) < abs(beta_rows[0]["trial_density"] - e_plane), beta_rows, e_plane, "zero-temperature")
    audit.check("conditional periodic centered energy fixture", abs(beta_rows[-1]["raw_energy_density"] - beta_rows[-1]["trial_density"] + alpha_limit) < abs(beta_rows[0]["raw_energy_density"] - beta_rows[0]["trial_density"] + alpha_limit), beta_rows, "requires surface lemma", "zero-temperature")
    audit.check("conditional zero-temperature specific KL fixture", abs(beta_rows[-1]["specific_KL"] - alpha_limit) < abs(beta_rows[0]["specific_KL"] - alpha_limit), beta_rows, "requires surface lemma", "zero-temperature")
    scalar_shift = 2.75
    shifted_trial = beta_rows[-1]["trial_density"] + scalar_shift
    shifted_energy = beta_rows[-1]["raw_energy_density"] + scalar_shift
    audit.check("zero-temperature gap scalar invariant", abs((shifted_trial - shifted_energy) - beta_rows[-1]["specific_KL"]) < 1e-14, shifted_trial - shifted_energy, beta_rows[-1]["specific_KL"], "zero-temperature")
    audit.check("raw zero-temperature sign mutable", beta_rows[-1]["raw_energy_density"] < 0.0 and shifted_energy > 0.0, (beta_rows[-1]["raw_energy_density"], shifted_energy), "both signs", "mutation")

    density_rows = []
    for beta in (2.0, 4.0, 8.0, 16.0):
        for length in (3.0, 6.0, 12.0):
            density = alpha_limit + 0.4 / beta + 0.4 / length + 0.2 / (beta * length)
            swapped = alpha_limit + 0.4 / length + 0.4 / beta + 0.2 / (length * beta)
            density_rows.append({"beta": beta, "L": length, "density": density})
            audit.check("beta-L scalar density symmetry", abs(density - swapped) < 1e-15, density, swapped, "zero-temperature")
    audit.check("conditional joint scalar van Hove fixture", abs(density_rows[-1]["density"] - alpha_limit) < abs(density_rows[0]["density"] - alpha_limit), density_rows, "requires surface lemma", "zero-temperature")

    witness_rows = []
    for beta in (2.0, 4.0, 8.0, 16.0):
        amplitude = (g_value + 3.0 * lambda_value) * math.sqrt(math.factorial(4)) / (16.0 * beta * float(mass) ** 2)
        witness_rows.append({"beta": beta, "amplitude": amplitude, "amplitude_per_beta": amplitude / beta})
    audit.check("finite-circle witness subextensive", all(witness_rows[index + 1]["amplitude"] < witness_rows[index]["amplitude"] for index in range(3)) and witness_rows[-1]["amplitude_per_beta"] < witness_rows[0]["amplitude_per_beta"], witness_rows, "vanishes", "mutation")

    bessel_integral = mp.quad(lambda radius: radius * mp.besselk(0, radius) ** 4, [0, 1, mp.inf])
    bessel_exact = 7 * mp.zeta(3) / 8
    plane_fourth = 7 * mp.zeta(3) / (64 * mp.pi**3 * mass**2)
    curvature_lower = 21 * mp.zeta(3) * (g_value + 3 * lambda_value) ** 2 / (16 * mp.pi**3 * mass**2)
    reconstructed = 8 * math.factorial(4) * c4**2 * plane_fourth
    audit.check("K0 fourth-power integral", abs(bessel_integral - bessel_exact) < mp.mpf("1e-30"), bessel_integral, bessel_exact, "curvature")
    audit.check("eight-channel curvature factor", abs(reconstructed - curvature_lower) < mp.mpf("2e-16"), reconstructed, curvature_lower, "curvature")
    audit.check("free pressure curvature positive", curvature_lower > 0, curvature_lower, "positive", "curvature")

    sample = [-1.2, -0.1, 0.8, 1.7]
    sample_weights = [0.25] * 4
    mean = sum(weight * value for weight, value in zip(sample_weights, sample))
    centered = [value - mean for value in sample]
    local_partition = sum(weight * math.exp(-value) for weight, value in zip(sample_weights, centered))
    audit.check("finite-block strict Jensen fixture", local_partition > 1.0, local_partition, ">1 fixture only", "chessboard")
    chessboard_rows = []
    for blocks in (1, 2, 4, 8, 16):
        lower_partition = local_partition**blocks
        pressure_lower = math.log(lower_partition) / blocks
        chessboard_rows.append({"blocks": blocks, "partition_lower": lower_partition, "pressure_lower": pressure_lower})
    audit.check("formal chessboard dissemination fixture", all(abs(row["pressure_lower"] - math.log(local_partition)) < 1e-14 for row in chessboard_rows), chessboard_rows, math.log(local_partition), "chessboard")

    required_phrases = (
        "Scoped theorem",
        "multicomponent obstruction",
        "Sharp-cutoff line Hamiltonians",
        "Open-rectangle Feynman--Kac",
        "component-blind GRS monotonicity proof",
        "Periodic-sharp surface-pairing reduction and open gate",
        "What is exact at common finite cutoff",
        "Why EXP-000772 does not close",
        "specific-KL",
        "states, vectors, gaps or correlators",
        "Physical empty space",
        "phase uniqueness",
        "makes no world-first claim",
    )
    for phrase in required_phrases:
        audit.check(f"certificate phrase {phrase[:42]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in (
        "new_plane_Wick_volume_coherent_Q3_extension",
        "strong_radial_Q3_coercivity_used",
        "sharp_cutoff_line_Q3_Hamiltonians",
        "open_rectangle_Feynman_Kac_Nelson_identity",
        "component_blind_GRS_spectral_Holder_monotonicity",
        "finite_centered_vacuum_energy_density_limit",
        "strict_positive_centered_reference_density",
        "scalar_shift_invariant_gap",
        "explicit_positive_free_pressure_curvature_cross_check",
        "periodic_zero_temperature_limit_reduced_to_surface_pairing",
    ):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in (
        "finite_circle_zero_mode_witness_sufficient_by_itself",
        "ordinary_multivariate_pointwise_stability_sufficient",
        "periodic_zero_temperature_specific_KL_limit",
        "joint_scalar_van_Hove_limit",
        "both_iterated_scalar_density_limits_equal",
        "periodic_sharp_surface_pairing_uniform_in_cutoff_volume_and_interpolation",
        "periodic_dyadic_positive_pressure_liminf",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
        "phase_transition_or_phase_uniqueness",
        "zero_temperature_state_limit",
        "ground_vector_limit",
        "uniform_spectral_gap",
        "correlation_function_limit_interchange",
        "beta_is_cosmological_cooling_time",
        "full_noncommutative_infinite_volume_local_algebra",
        "interacting_Hadamard_or_microlocal_spectrum",
        "original_fixed_raw_CL8_family",
        "original_3D_Q3LOCK_parent",
        "physical_light_speed_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Sector_A_complete",
        "Pre_A_complete",
    ):
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
        "negative_ids": NEGATIVE_IDS,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {
            "Q3": {"edges": edges, "pure_coefficient": str(pure), "coercivity": coercivity_rows},
            "GRS": {"Holder": holder_rows, "alpha": alphas, "energies": energies, "scaling": scaling_rows, "spectral": spectral_rows},
            "strictness": {"interval_integral": str(interval_integral), "witness_norm_squared": str(witness_norm_sq), "rayleigh_ground": rayleigh_ground},
            "boundary": {"rows": boundary_rows, "cutoff": cutoff_rows},
            "zero_temperature": {"beta": beta_rows, "rectangles": density_rows, "finite_circle_witness": witness_rows},
            "curvature": {"Bessel_integral": str(bessel_integral), "Bessel_exact": str(bessel_exact), "plane_fourth": str(plane_fourth), "lower": str(curvature_lower)},
            "chessboard": {"local_partition": local_partition, "rows": chessboard_rows},
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
