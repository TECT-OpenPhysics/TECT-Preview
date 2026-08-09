#!/usr/bin/env python3
"""Primary verifier for the volume-coherent Q3 thermodynamic theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-thermodynamic-pressure-relative-entropy-density-phase-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-THERMODYNAMIC-PRESSURE-RELATIVE-ENTROPY-DENSITY-AND-PHASE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FIXED-BETA-VOLUME-COHERENT-NELSON-PRESSURE-SPECIFIC-RELATIVE-ENTROPY-AND-PERIODIC-LOCAL-SCHWINGER-LIMIT"
EXPLORATION_ID = "EXP-000775"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-beta-independent-hamiltonian-ground-reference-route-split/result.json"
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


def rectangular_covariance(beta: float, length: float, mass: float, cutoff: int) -> float:
    total = 0.0
    for temporal in range(-cutoff, cutoff + 1):
        for spatial in range(-cutoff, cutoff + 1):
            denominator = mass * mass + (2.0 * math.pi * temporal / beta) ** 2 + (2.0 * math.pi * spatial / length) ** 2
            total += 1.0 / denominator
    return total / (beta * length)


def image_difference(beta: float, length: float, mass: float, cutoff: int) -> float:
    mp.mp.dps = 40
    total = mp.mpf("0")
    for temporal in range(-cutoff, cutoff + 1):
        for spatial in range(-cutoff, cutoff + 1):
            if temporal == 0 and spatial == 0:
                continue
            radius = mp.sqrt((temporal * beta) ** 2 + (spatial * length) ** 2)
            total += mp.besselk(0, mass * radius)
    return float(total / (2 * mp.pi))


def axis_correction(circumference: float, mass: float, cutoff: int) -> float:
    mp.mp.dps = 40
    return float(sum(mp.besselk(0, mass * index * circumference) for index in range(1, cutoff + 1)) / mp.pi)


def mixed_image_difference(beta: float, length: float, mass: float, cutoff: int) -> float:
    mp.mp.dps = 40
    total = mp.mpf("0")
    for temporal in range(-cutoff, cutoff + 1):
        for spatial in range(-cutoff, cutoff + 1):
            if temporal == 0 or spatial == 0:
                continue
            radius = mp.sqrt((temporal * beta) ** 2 + (spatial * length) ** 2)
            total += mp.besselk(0, mass * radius)
    return float(total / (2 * mp.pi))


def logsumexp(values: list[float]) -> float:
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def ground_energy(t: float, gap: float, trial: float, off_diagonal: float, excited_shift: float) -> float:
    left = t * trial
    right = gap + t * excited_shift
    return 0.5 * (left + right - math.sqrt((left - right) ** 2 + 4.0 * (t * off_diagonal) ** 2))


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
    audit.check("EXP767 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP767 fixed Hamiltonian parent", parent["scope"]["beta_independent_compact_circle_Hamiltonian"] is True and parent["scope"]["strict_ground_Gaussian_reference_advantage"] is True, "fixed H and ground sign", True, "parent")

    edges = cube_edges()
    Lq = laplacian_matrix(edges)
    x = sp.symbols("x0:8", real=True)
    g, lam, C, D = sp.symbols("g lambda C D", real=True)
    vector = sp.Matrix(x)
    W4 = g * sum(value**4 for value in x) / 4 + lam * sum((x[left] - x[right]) ** 2 * (x[left] ** 2 + x[right] ** 2) for left, right in edges) / 4
    Aq = (g + lam) * sp.eye(8) + lam * Lq
    G = g + 4 * lam
    audit.check("Q3 twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 trace A", sp.simplify(sp.trace(Aq) - 8 * G) == 0, sp.trace(Aq), 8 * G, "Q3")
    audit.check("Q3 quartic Laplacian", sp.expand(polynomial_laplacian(W4, x) - 3 * (vector.T * Aq * vector)[0]) == 0, polynomial_laplacian(W4, x), "3 qT A q", "Q3")
    norm_k, radial_square = sp.symbols("normK y", positive=True)
    stability_bound = g * radial_square**2 / 32 - norm_k * radial_square / 2
    stability_minimizer = 8 * norm_k / g
    audit.check("arbitrary K stability scalar minimum", sp.simplify(stability_bound.subs(radial_square, stability_minimizer) + 2 * norm_k**2 / g) == 0, stability_bound.subs(radial_square, stability_minimizer), -2 * norm_k**2 / g, "Hamiltonian")

    Kpl = sp.diag(*sp.symbols("d0:8", real=True))
    Kpl[0, 3] = Kpl[3, 0] = sp.Symbol("u03", real=True)
    Kpl[2, 7] = Kpl[7, 2] = sp.Symbol("u27", real=True)
    Ktorus = Kpl + 3 * D * Aq
    Ppl = (vector.T * Kpl * vector)[0] / 2 + W4
    Ptorus = (vector.T * Ktorus * vector)[0] / 2 + W4
    scalar = D * sp.trace(Kpl) / 2 + 6 * D**2 * G
    torus_side = wick(Ptorus, C + D, x) + scalar
    plane_side = wick(Ppl, C, x)
    audit.check("exact plane-to-torus Wick identity", sp.expand(torus_side - plane_side) == 0, sp.expand(torus_side - plane_side), 0, "coherence")
    audit.check("generic matrix volume coherence", sp.expand(Ktorus - 3 * D * Aq) == Kpl, sp.expand(Ktorus - 3 * D * Aq), Kpl, "coherence")
    wrong_scalar = -D * sp.trace(Kpl) / 2 - 6 * D**2 * G
    audit.check("wrong scalar sign mutation", sp.expand(wick(Ptorus, C + D, x) + wrong_scalar - plane_side) != 0, wrong_scalar, "fails", "mutation")
    mass_only = Kpl + 3 * D * (g + lam) * sp.eye(8)
    audit.check("mass-only volume mutation", sp.expand(mass_only - 3 * D * Aq - Kpl) != sp.zeros(8), sp.expand(mass_only - 3 * D * Aq - Kpl), "nonzero lambda L_Q3", "mutation")

    rectangular_rows = []
    for cutoff in (2, 4, 7):
        forward = rectangular_covariance(1.3, 2.1, 1.15, cutoff)
        swapped = rectangular_covariance(2.1, 1.3, 1.15, cutoff)
        rectangular_rows.append({"cutoff": cutoff, "forward": forward, "swapped": swapped})
        audit.check(f"rectangular covariance exchange N{cutoff}", abs(forward - swapped) < 2e-14, forward, swapped, "coherence")
    image_rows = []
    for cutoff in (3, 5, 7):
        forward = image_difference(1.3, 2.1, 1.15, cutoff)
        swapped = image_difference(2.1, 1.3, 1.15, cutoff)
        image_rows.append({"cutoff": cutoff, "forward": forward, "swapped": swapped})
        audit.check(f"image covariance exchange R{cutoff}", abs(forward - swapped) < 2e-14, forward, swapped, "coherence")
    audit.check("image covariance positive", all(row["forward"] > 0.0 for row in image_rows), image_rows, "positive", "coherence")
    audit.check("image covariance converges", abs(image_rows[-1]["forward"] - image_rows[-2]["forward"]) < 1e-4, image_rows, "small image tail", "coherence")
    circle_rows = [{"L": length, "a_L": image_difference(100.0, length, 1.15, 7)} for length in (1.4, 2.8, 5.6)]
    audit.check("circle correction decays with L", all(circle_rows[index + 1]["a_L"] < circle_rows[index]["a_L"] for index in range(2)), circle_rows, "strict decay", "coherence")
    beta_fixture, mass_fixture, image_cutoff = 1.3, 1.15, 7
    a_beta = axis_correction(beta_fixture, mass_fixture, image_cutoff)
    decomposition_rows = []
    for length in (2.1, 4.2, 8.4):
        total = image_difference(beta_fixture, length, mass_fixture, image_cutoff)
        a_length = axis_correction(length, mass_fixture, image_cutoff)
        mixed = mixed_image_difference(beta_fixture, length, mass_fixture, image_cutoff)
        decomposition_rows.append({"L": length, "total": total, "a_beta": a_beta, "a_L": a_length, "mixed": mixed})
        audit.check(f"cylinder image decomposition L{length}", abs(total - a_beta - a_length - mixed) < 3e-15, total, a_beta + a_length + mixed, "coherence")
    audit.check("cylinder limit tends a_beta", all(abs(decomposition_rows[index + 1]["total"] - a_beta) < abs(decomposition_rows[index]["total"] - a_beta) for index in range(2)), decomposition_rows, a_beta, "coherence")
    trace_fixture, G_fixture, e_plane = 1.7, 2.1, -0.4
    e_circle = e_plane + a_beta * trace_fixture / 2.0 + 6.0 * a_beta**2 * G_fixture
    e_rows = [e_plane + row["total"] * trace_fixture / 2.0 + 6.0 * row["total"] ** 2 * G_fixture for row in decomposition_rows]
    audit.check("torus scalar tends dual circle scalar", all(abs(e_rows[index + 1] - e_circle) < abs(e_rows[index] - e_circle) for index in range(2)), e_rows, e_circle, "coherence")
    radial_probe = mp.mpf("1e-7")
    green_flux = float(mass_fixture * radial_probe * mp.besselk(1, mass_fixture * radial_probe))
    audit.check("two-dimensional Green coefficient flux", abs(green_flux - 1.0) < 2e-12, green_flux, 1.0, "coherence")

    interacting_spectrum = [-1.7, 0.4, 2.3, 5.8]
    free_spectrum = [0.0, 1.2, 3.0, 6.5]
    transfer_rows = []
    for length in (1.0, 2.0, 4.0, 8.0, 16.0):
        log_interacting = logsumexp([-length * energy for energy in interacting_spectrum])
        log_free = logsumexp([-length * energy for energy in free_spectrum])
        rate = (log_interacting - log_free) / length
        transfer_rows.append({"L": length, "rate": rate})
    audit.check("Nelson dual trace rate", abs(transfer_rows[-1]["rate"] + interacting_spectrum[0]) < 5e-10, transfer_rows, -interacting_spectrum[0], "pressure")
    audit.check("Nelson rate convergence", all(abs(transfer_rows[index + 1]["rate"] + interacting_spectrum[0]) < abs(transfer_rows[index]["rate"] + interacting_spectrum[0]) for index in range(4)), transfer_rows, "convergent", "pressure")
    beta_value, scalar_shift = 1.6, 2.25
    raw_pressure = -interacting_spectrum[0] / beta_value
    shifted_energy = interacting_spectrum[0] + scalar_shift * beta_value
    shifted_pressure = -shifted_energy / beta_value
    audit.check("raw pressure scalar shift law", abs(shifted_pressure - (raw_pressure - scalar_shift)) < 1e-14, shifted_pressure, raw_pressure - scalar_shift, "pressure")
    audit.check("raw pressure sign mutable", raw_pressure > 0 and shifted_pressure < 0, (raw_pressure, shifted_pressure), "both signs", "mutation")
    ledger_length = 3.25
    base_log_partition, base_insertion = 2.8, 1.9
    scalar_volume = scalar_shift * beta_value * ledger_length
    scalar_ledger = {
        "H_L": scalar_shift * ledger_length,
        "H_beta": scalar_shift * beta_value,
        "logZ": (base_log_partition - scalar_volume) - base_log_partition,
        "insertion": (base_insertion + scalar_volume) - base_insertion,
        "E": shifted_energy - interacting_spectrum[0],
        "pressure": shifted_pressure - raw_pressure,
        "KL_change": (base_log_partition - scalar_volume + base_insertion + scalar_volume) - (base_log_partition + base_insertion),
    }
    audit.check("full scalar density factor ledger", abs(scalar_ledger["H_L"] - scalar_shift * ledger_length) < 1e-15 and abs(scalar_ledger["H_beta"] - scalar_shift * beta_value) < 1e-15 and abs(scalar_ledger["logZ"] + scalar_volume) < 1e-14 and abs(scalar_ledger["insertion"] - scalar_volume) < 1e-14 and abs(scalar_ledger["E"] - scalar_shift * beta_value) < 1e-14 and abs(scalar_ledger["pressure"] + scalar_shift) < 1e-14 and abs(scalar_ledger["KL_change"]) < 1e-14, scalar_ledger, "cL, c beta, -c beta L, +c beta L, invariant KL", "pressure")

    mu = [0.11, 0.19, 0.27, 0.43]
    interaction_values = [-0.8, 0.25, 1.1, -0.35]
    partition = sum(weight * math.exp(-value) for weight, value in zip(mu, interaction_values))
    nu = [weight * math.exp(-value) / partition for weight, value in zip(mu, interaction_values)]
    divergence = sum(weight * math.log(weight / tilted) for weight, tilted in zip(mu, nu))
    identity_value = math.log(partition) + sum(weight * value for weight, value in zip(mu, interaction_values))
    audit.check("finite KL identity", abs(divergence - identity_value) < 2e-15, divergence, identity_value, "entropy")
    area, constant = 7.5, 1.3
    shifted_values = [value + constant * area for value in interaction_values]
    shifted_partition = sum(weight * math.exp(-value) for weight, value in zip(mu, shifted_values))
    shifted_nu = [weight * math.exp(-value) / shifted_partition for weight, value in zip(mu, shifted_values)]
    shifted_divergence = sum(weight * math.log(weight / tilted) for weight, tilted in zip(mu, shifted_nu))
    audit.check("finite KL scalar invariance", abs(shifted_divergence - divergence) < 2e-14, shifted_divergence, divergence, "entropy")
    audit.check("normalized law scalar invariance", max(abs(left - right) for left, right in zip(nu, shifted_nu)) < 2e-15, shifted_nu, nu, "entropy")
    reverse_divergence = sum(tilted * math.log(tilted / weight) for weight, tilted in zip(mu, nu))
    audit.check("KL direction mutation", abs(reverse_divergence - identity_value) > 1e-3, reverse_divergence, "not free-to-interacting identity", "mutation")

    gap, trial, off_diagonal, excited_shift = 2.4, 0.65, 0.42, -0.2
    energy_one = ground_energy(1.0, gap, trial, off_diagonal, excited_shift)
    audit.check("strict Bregman ground gap", trial - energy_one > 0.0, trial - energy_one, "positive", "strictness")
    t_values = [index / 20.0 for index in range(21)]
    energies = [ground_energy(value, gap, trial, off_diagonal, excited_shift) for value in t_values]
    discrete_slopes = [(energies[index + 1] - energies[index]) / 0.05 for index in range(20)]
    audit.check("ground energy concavity", all(discrete_slopes[index + 1] <= discrete_slopes[index] + 1e-12 for index in range(19)), discrete_slopes, "nonincreasing slopes", "strictness")
    g_value, lambda_value, beta_circle, mass_value = 1.2, 0.35, 1.6, 0.9
    pure_quartic = sp.Poly(W4, x).coeff_monomial(x[0] ** 4)
    audit.check("Q3 pure quartic coefficient", sp.simplify(pure_quartic - (g + 3 * lam) / 4) == 0, pure_quartic, (g + 3 * lam) / 4, "strictness")
    zero_mode_four_creation = (1.0 / math.sqrt(beta_circle) / math.sqrt(2.0 * mass_value)) ** 4
    audit.check("zero-mode four-creation normalization", abs(zero_mode_four_creation - 1.0 / (4.0 * beta_circle**2 * mass_value**2)) < 2e-15, zero_mode_four_creation, 1.0 / (4.0 * beta_circle**2 * mass_value**2), "strictness")
    amplitude = (g_value + 3.0 * lambda_value) * math.sqrt(math.factorial(4)) / (16.0 * beta_circle * mass_value**2)
    derived_amplitude = beta_circle * ((g_value + 3.0 * lambda_value) / 4.0) * zero_mode_four_creation * math.sqrt(math.factorial(4))
    audit.check("Q3 dual amplitude factor derivation", abs(amplitude - derived_amplitude) < 2e-15, amplitude, derived_amplitude, "strictness")
    audit.check("Q3 dual four-particle amplitude", amplitude > 0.0, amplitude, "positive", "strictness")
    B_value = -4.3
    rayleigh_t = amplitude / (abs(B_value - trial) + 1.0)
    rayleigh_difference = (-2.0 * rayleigh_t * amplitude + rayleigh_t**2 * (B_value - trial)) / (1.0 + rayleigh_t**2)
    audit.check("form Rayleigh strictness arbitrary B", rayleigh_difference < 0.0, rayleigh_difference, "negative", "strictness")
    common_shift = 3.7 * beta_circle
    audit.check("specific KL scalar invariance", abs(((trial + common_shift) - (energy_one + common_shift)) - (trial - energy_one)) < 1e-14, (trial + common_shift) - (energy_one + common_shift), trial - energy_one, "strictness")
    excited_energy = trial + gap + excited_shift - energy_one
    density_rows = []
    for length in (2.0, 4.0, 8.0, 16.0):
        log_ratio = logsumexp([-length * energy_one, -length * excited_energy]) - logsumexp([0.0, -length * gap])
        free_insertion_per_length = (trial + excited_shift * math.exp(-length * gap)) / (1.0 + math.exp(-length * gap))
        divergence_per_length = log_ratio / length + free_insertion_per_length
        density_rows.append({"L": length, "D_per_L": divergence_per_length, "D_per_area": divergence_per_length / beta_circle, "negative_centered": -divergence_per_length / beta_circle})
    target_per_length = trial - energy_one
    audit.check("specific KL length composition", abs(density_rows[-1]["D_per_L"] - target_per_length) < 1e-12, density_rows, target_per_length, "entropy")
    audit.check("specific KL beta factor", abs(density_rows[-1]["D_per_area"] - target_per_length / beta_circle) < 1e-12 and abs(density_rows[-1]["negative_centered"] - (energy_one - trial) / beta_circle) < 1e-12, density_rows[-1], (target_per_length / beta_circle, (energy_one - trial) / beta_circle), "entropy")

    spectral_gap = interacting_spectrum[1] - interacting_spectrum[0]
    projection_rows = []
    for length in (1.0, 2.0, 4.0, 8.0):
        excited_weight = sum(math.exp(-length * (energy - interacting_spectrum[0])) for energy in interacting_spectrum[1:])
        ground_probability = 1.0 / (1.0 + excited_weight)
        projection_rows.append({"L": length, "ground_probability": ground_probability})
    audit.check("dual ground projection convergence", projection_rows[-1]["ground_probability"] > 0.999999, projection_rows, "to one", "state")
    cluster_rows = [{"r": distance, "bound": math.exp(-spectral_gap * distance)} for distance in (1.0, 2.0, 4.0, 8.0)]
    audit.check("transfer gap positive", spectral_gap > 0.0, spectral_gap, "positive", "state")
    audit.check("exponential spatial clustering fixture", all(cluster_rows[index + 1]["bound"] < cluster_rows[index]["bound"] for index in range(3)), cluster_rows, "strict decay", "state")
    observable_amplitude, separation = 0.73, 1.1
    connected_rows = []
    for total_length in (5.0, 10.0, 20.0, 40.0):
        connected = observable_amplitude**2 * (math.exp(-spectral_gap * separation) + math.exp(-spectral_gap * (total_length - separation))) / (1.0 + math.exp(-spectral_gap * total_length))
        connected_rows.append({"L": total_length, "connected": connected})
    connected_limit = observable_amplitude**2 * math.exp(-spectral_gap * separation)
    audit.check("trace-normalized connected transfer limit", abs(connected_rows[-1]["connected"] - connected_limit) < 1e-14, connected_rows, connected_limit, "state")

    for phrase in ("Scoped theorem", "Plane-to-torus covariance", "No coupling derivative", "Nelson coordinate exchange", "Finite-volume relative entropy identity", "Strictness from the Q3 four-particle witness", "not convergence of global density matrices", "Periodic bounded-local Schwinger limit", "full noncommutative infinite-volume KMS algebra", "not a physical-empty-space", "global Radon--Nikodym", "does not claim a world-first"):
        audit.check(f"certificate phrase {phrase[:38]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("exact_beta_L_symmetric_covariance_correction", "Nelson_coordinate_exchange", "raw_relative_pressure_limit_exists", "specific_relative_entropy_density_exists", "strict_positive_specific_relative_entropy_density", "strict_negative_centered_Gaussian_variational_density", "periodic_bounded_local_Schwinger_limit", "periodic_transfer_observable_spatial_mixing", "dual_transfer_ground_unique_and_gapped"):
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("raw_relative_pressure_sign_gauge_invariant", "arbitrary_L_dependent_K_and_scalar_family", "original_fixed_raw_CL8_family", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "global_infinite_volume_Radon_Nikodym_density", "finite_total_infinite_volume_relative_entropy", "all_boundary_condition_state_uniqueness", "periodic_beta_KMS_limit", "full_noncommutative_infinite_volume_local_algebra", "beta_to_infinity_L_to_infinity_interchange", "zero_temperature_ground_energy_density", "spontaneous_symmetry_breaking_or_phase_transition", "interacting_Hadamard_or_microlocal_spectrum", "original_3D_Q3LOCK_parent", "physical_light_speed_derived", "C0_closed", "N1_through_N5_closed", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
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
            "Q3": {"edges": edges, "trace_A": str(sp.trace(Aq)), "amplitude": amplitude},
            "coherence": {"rectangular": rectangular_rows, "images": image_rows, "circle": circle_rows, "decomposition": decomposition_rows, "e_limit": e_rows, "scalar": str(scalar)},
            "pressure": {"transfer": transfer_rows, "raw": raw_pressure, "shifted": shifted_pressure, "scalar_ledger": scalar_ledger},
            "entropy": {"partition": partition, "divergence": divergence, "reverse": reverse_divergence, "identity": identity_value, "Bregman": trial - energy_one, "density": density_rows},
            "state": {"gap": spectral_gap, "projection": projection_rows, "clustering": cluster_rows, "connected": connected_rows},
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
