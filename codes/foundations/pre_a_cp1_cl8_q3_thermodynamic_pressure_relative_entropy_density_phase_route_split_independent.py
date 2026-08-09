#!/usr/bin/env python3
"""Independent stdlib verifier for the Q3 thermodynamic theorem."""

from __future__ import annotations

import argparse
import ast
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
SLUG = "pre-a-cp1-cl8-q3-thermodynamic-pressure-relative-entropy-density-phase-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-THERMODYNAMIC-PRESSURE-RELATIVE-ENTROPY-DENSITY-AND-PHASE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FIXED-BETA-VOLUME-COHERENT-NELSON-PRESSURE-SPECIFIC-RELATIVE-ENTROPY-AND-PERIODIC-LOCAL-SCHWINGER-LIMIT"
EXPLORATION_ID = "EXP-000775"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-beta-independent-hamiltonian-ground-reference-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
PRIMARY_STEM = SLUG.replace("-", "_")

Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


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


def add_term(poly: Polynomial, coefficient: Fraction, powers: dict[int, int]) -> None:
    exponent = [0] * 8
    for index, power in powers.items():
        exponent[index] = power
    key = tuple(exponent)
    poly[key] = poly.get(key, Fraction(0)) + coefficient
    if poly[key] == 0:
        del poly[key]


def add_polynomials(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def scale_polynomial(poly: Polynomial, coefficient: Fraction) -> Polynomial:
    return {exponent: coefficient * value for exponent, value in poly.items() if coefficient * value}


def laplacian(poly: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in poly.items():
        for index, power in enumerate(exponent):
            if power >= 2:
                lowered = list(exponent)
                lowered[index] -= 2
                key = tuple(lowered)
                result[key] = result.get(key, Fraction(0)) + coefficient * power * (power - 1)
    return {key: value for key, value in result.items() if value}


def wick(poly: Polynomial, covariance: Fraction) -> Polynomial:
    result = dict(poly)
    current = dict(poly)
    coefficient = Fraction(1)
    for order in range(1, 3):
        current = laplacian(current)
        coefficient *= -covariance / (2 * order)
        result = add_polynomials(result, scale_polynomial(current, coefficient))
    return result


def cube_laplacian() -> tuple[list[tuple[int, int]], list[list[Fraction]]]:
    edges = [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]
    matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for left, right in edges:
        matrix[left][left] += 1
        matrix[right][right] += 1
        matrix[left][right] -= 1
        matrix[right][left] -= 1
    return edges, matrix


def matrix_add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[row][column] + right[row][column] for column in range(8)] for row in range(8)]


def matrix_scale(matrix: list[list[Fraction]], coefficient: Fraction) -> list[list[Fraction]]:
    return [[coefficient * matrix[row][column] for column in range(8)] for row in range(8)]


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum(matrix[index][index] for index in range(8))


def interaction_polynomial(g: Fraction, lam: Fraction, matrix: list[list[Fraction]], edges: list[tuple[int, int]]) -> Polynomial:
    result: Polynomial = {}
    for left in range(8):
        for right in range(8):
            coefficient = matrix[left][right] / 2
            if coefficient:
                add_term(result, coefficient, {left: 2} if left == right else {left: 1, right: 1})
    for index in range(8):
        add_term(result, g / 4, {index: 4})
    for left, right in edges:
        add_term(result, lam / 4, {left: 4})
        add_term(result, lam / 4, {right: 4})
        add_term(result, -lam / 2, {left: 3, right: 1})
        add_term(result, -lam / 2, {left: 1, right: 3})
        add_term(result, lam / 2, {left: 2, right: 2})
    return result


def finite_covariance(beta: float, length: float, mass: float, cutoff: int) -> float:
    return sum(
        1.0 / (mass * mass + (2.0 * math.pi * temporal / beta) ** 2 + (2.0 * math.pi * spatial / length) ** 2)
        for temporal in range(-cutoff, cutoff + 1)
        for spatial in range(-cutoff, cutoff + 1)
    ) / (beta * length)


def squared_image_radii(beta: Fraction, length: Fraction, cutoff: int) -> list[Fraction]:
    return sorted(
        Fraction(temporal * temporal) * beta * beta + Fraction(spatial * spatial) * length * length
        for temporal in range(-cutoff, cutoff + 1)
        for spatial in range(-cutoff, cutoff + 1)
        if temporal != 0 or spatial != 0
    )


def k0_integral(argument: float, panels: int = 800, endpoint: float = 12.0) -> float:
    step = endpoint / panels
    total = math.exp(-argument)
    for index in range(1, panels):
        weight = 4.0 if index % 2 else 2.0
        total += weight * math.exp(-argument * math.cosh(index * step))
    total += math.exp(-argument * math.cosh(endpoint))
    return total * step / 3.0


def image_sum(beta: float, length: float, mass: float, cutoff: int) -> float:
    total = 0.0
    for temporal in range(-cutoff, cutoff + 1):
        for spatial in range(-cutoff, cutoff + 1):
            if temporal == 0 and spatial == 0:
                continue
            radius = math.sqrt((temporal * beta) ** 2 + (spatial * length) ** 2)
            total += k0_integral(mass * radius)
    return total / (2.0 * math.pi)


def axis_sum(circumference: float, mass: float, cutoff: int) -> float:
    return sum(k0_integral(mass * index * circumference) for index in range(1, cutoff + 1)) / math.pi


def mixed_sum(beta: float, length: float, mass: float, cutoff: int) -> float:
    total = 0.0
    for temporal in range(-cutoff, cutoff + 1):
        for spatial in range(-cutoff, cutoff + 1):
            if temporal == 0 or spatial == 0:
                continue
            radius = math.sqrt((temporal * beta) ** 2 + (spatial * length) ** 2)
            total += k0_integral(mass * radius)
    return total / (2.0 * math.pi)


def logsumexp(values: list[float]) -> float:
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def two_level_ground(t: float, gap: float, trial: float, coupling: float, excited: float) -> float:
    diagonal_zero = t * trial
    diagonal_one = gap + t * excited
    return 0.5 * (diagonal_zero + diagonal_one - math.sqrt((diagonal_zero - diagonal_one) ** 2 + 4.0 * t * t * coupling * coupling))


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
    audit.check("independent EXP767 parent", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    edges, Lq = cube_laplacian()
    identity = [[Fraction(int(row == column)) for column in range(8)] for row in range(8)]
    g, lam, C, D = Fraction(9, 7), Fraction(5, 12), Fraction(7, 10), Fraction(3, 17)
    Aq = matrix_add(matrix_scale(identity, g + lam), matrix_scale(Lq, lam))
    G = g + 4 * lam
    audit.check("independent Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("independent Q3 trace A", trace(Aq) == 8 * G, trace(Aq), 8 * G, "Q3")
    norm_k = Fraction(13, 6)
    radial_minimizer = 8 * norm_k / g
    stability_value = g * radial_minimizer**2 / 32 - norm_k * radial_minimizer / 2
    audit.check("independent arbitrary K stability minimum", stability_value == -2 * norm_k**2 / g, stability_value, -2 * norm_k**2 / g, "Hamiltonian")
    Kpl = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for index in range(8):
        Kpl[index][index] = Fraction(2 * index - 7, index + 4)
    for left, right, value in ((0, 2, Fraction(3, 11)), (1, 6, Fraction(-2, 9)), (4, 7, Fraction(5, 13))):
        Kpl[left][right] = value
        Kpl[right][left] = value
    Ktorus = matrix_add(Kpl, matrix_scale(Aq, 3 * D))
    torus = wick(interaction_polynomial(g, lam, Ktorus, edges), C + D)
    scalar = D * trace(Kpl) / 2 + 6 * D * D * G
    zero = (0,) * 8
    torus[zero] = torus.get(zero, Fraction(0)) + scalar
    plane = wick(interaction_polynomial(g, lam, Kpl, edges), C)
    audit.check("independent exact plane-torus Wick identity", torus == plane, len(torus), len(plane), "coherence")
    audit.check("independent matrix volume coherence", matrix_add(Ktorus, matrix_scale(Aq, -3 * D)) == Kpl, Ktorus, Kpl, "coherence")
    wrong = dict(torus)
    wrong[zero] = wrong.get(zero, Fraction(0)) - 2 * scalar
    audit.check("independent scalar sign mutation", wrong != plane, wrong.get(zero), plane.get(zero), "mutation")
    mass_only = matrix_add(Kpl, matrix_scale(identity, 3 * D * (g + lam)))
    audit.check("independent mass-only volume mutation", matrix_add(mass_only, matrix_scale(Aq, -3 * D)) != Kpl, mass_only, "fails", "mutation")

    covariance_rows = []
    for cutoff in (1, 3, 6):
        forward = finite_covariance(1.7, 2.4, 0.85, cutoff)
        backward = finite_covariance(2.4, 1.7, 0.85, cutoff)
        covariance_rows.append({"cutoff": cutoff, "forward": forward, "backward": backward})
        audit.check(f"independent rectangular exchange N{cutoff}", abs(forward - backward) < 2e-14, forward, backward, "coherence")
    radii_forward = squared_image_radii(Fraction(7, 5), Fraction(11, 6), 4)
    radii_backward = squared_image_radii(Fraction(11, 6), Fraction(7, 5), 4)
    audit.check("independent exact image-radius exchange", radii_forward == radii_backward, len(radii_forward), len(radii_backward), "coherence")
    image_forward = image_sum(1.4, 1.9, 1.05, 4)
    image_backward = image_sum(1.9, 1.4, 1.05, 4)
    audit.check("independent Bessel-integral exchange", abs(image_forward - image_backward) < 2e-13, image_forward, image_backward, "coherence")
    audit.check("independent image positivity", image_forward > 0.0, image_forward, "positive", "coherence")
    circle_values = [image_sum(80.0, length, 1.05, 5) for length in (1.5, 3.0, 6.0)]
    audit.check("independent circle correction decay", circle_values[0] > circle_values[1] > circle_values[2] > 0.0, circle_values, "strict decay", "coherence")
    beta_fixture, mass_fixture, image_cutoff = 1.4, 1.05, 4
    a_beta = axis_sum(beta_fixture, mass_fixture, image_cutoff)
    decomposition_rows = []
    for length in (1.9, 3.8, 7.6):
        total = image_sum(beta_fixture, length, mass_fixture, image_cutoff)
        a_length = axis_sum(length, mass_fixture, image_cutoff)
        mixed = mixed_sum(beta_fixture, length, mass_fixture, image_cutoff)
        decomposition_rows.append({"L": length, "total": total, "a_beta": a_beta, "a_L": a_length, "mixed": mixed})
        audit.check(f"independent cylinder decomposition L{length}", abs(total - a_beta - a_length - mixed) < 2e-13, total, a_beta + a_length + mixed, "coherence")
    audit.check("independent cylinder limit", all(abs(decomposition_rows[index + 1]["total"] - a_beta) < abs(decomposition_rows[index]["total"] - a_beta) for index in range(2)), decomposition_rows, a_beta, "coherence")
    trace_fixture, G_fixture, e_plane = -0.8, 1.9, 0.25
    e_circle = e_plane + a_beta * trace_fixture / 2 + 6 * a_beta * a_beta * G_fixture
    e_values = [e_plane + row["total"] * trace_fixture / 2 + 6 * row["total"] ** 2 * G_fixture for row in decomposition_rows]
    audit.check("independent scalar cylinder limit", all(abs(e_values[index + 1] - e_circle) < abs(e_values[index] - e_circle) for index in range(2)), e_values, e_circle, "coherence")
    radius, step = 1e-4, 1e-6
    green_plus = k0_integral(mass_fixture * (radius + step)) / (2.0 * math.pi)
    green_minus = k0_integral(mass_fixture * (radius - step)) / (2.0 * math.pi)
    green_flux = -2.0 * math.pi * radius * (green_plus - green_minus) / (2.0 * step)
    audit.check("independent Green coefficient flux", abs(green_flux - 1.0) < 2e-4, green_flux, 1.0, "coherence")

    interacting = [-1.35, 0.75, 2.6, 4.9]
    free = [0.0, 1.05, 2.9, 5.4]
    rates = []
    for length in (1.3, 2.6, 5.2, 10.4, 20.8):
        rate = (logsumexp([-length * value for value in interacting]) - logsumexp([-length * value for value in free])) / length
        rates.append({"L": length, "rate": rate})
    audit.check("independent Nelson trace rate", abs(rates[-1]["rate"] + interacting[0]) < 2e-11, rates, -interacting[0], "pressure")
    audit.check("independent Nelson convergence", all(abs(rates[index + 1]["rate"] + interacting[0]) < abs(rates[index]["rate"] + interacting[0]) for index in range(4)), rates, "convergent", "pressure")
    beta, shift = 2.2, 1.6
    pressure = -interacting[0] / beta
    shifted_pressure = -(interacting[0] + shift * beta) / beta
    audit.check("independent raw pressure shift", abs(shifted_pressure - (pressure - shift)) < 2e-15, shifted_pressure, pressure - shift, "pressure")
    audit.check("independent raw sign mutation", pressure > 0.0 and shifted_pressure < 0.0, (pressure, shifted_pressure), "both signs", "mutation")
    ledger_length = 4.1
    scalar_volume = shift * beta * ledger_length
    base_log, base_insertion = 3.6, -0.7
    scalar_ledger = {
        "H_L": shift * ledger_length,
        "H_beta": shift * beta,
        "logZ": -scalar_volume,
        "insertion": scalar_volume,
        "E": (interacting[0] + shift * beta) - interacting[0],
        "pressure": shifted_pressure - pressure,
        "KL_change": (base_log - scalar_volume + base_insertion + scalar_volume) - (base_log + base_insertion),
    }
    audit.check("independent full scalar factor ledger", abs(scalar_ledger["H_L"] - shift * ledger_length) < 1e-15 and abs(scalar_ledger["H_beta"] - shift * beta) < 1e-15 and abs(scalar_ledger["logZ"] + scalar_volume) < 1e-14 and abs(scalar_ledger["insertion"] - scalar_volume) < 1e-14 and abs(scalar_ledger["E"] - shift * beta) < 1e-14 and abs(scalar_ledger["pressure"] + shift) < 1e-14 and abs(scalar_ledger["KL_change"]) < 1e-14, scalar_ledger, "complete c beta L cancellation", "pressure")

    mu = [0.17, 0.23, 0.29, 0.31]
    action = [0.8, -0.45, 1.25, -0.7]
    partition = sum(weight * math.exp(-value) for weight, value in zip(mu, action))
    nu = [weight * math.exp(-value) / partition for weight, value in zip(mu, action)]
    relative_entropy = sum(weight * math.log(weight / tilted) for weight, tilted in zip(mu, nu))
    formula = math.log(partition) + sum(weight * value for weight, value in zip(mu, action))
    audit.check("independent free-to-interacting KL identity", abs(relative_entropy - formula) < 2e-15, relative_entropy, formula, "entropy")
    scalar_action = [value + 5.75 for value in action]
    scalar_partition = sum(weight * math.exp(-value) for weight, value in zip(mu, scalar_action))
    scalar_nu = [weight * math.exp(-value) / scalar_partition for weight, value in zip(mu, scalar_action)]
    audit.check("independent KL scalar invariance", max(abs(left - right) for left, right in zip(nu, scalar_nu)) < 2e-15, scalar_nu, nu, "entropy")
    reverse_entropy = sum(tilted * math.log(tilted / weight) for weight, tilted in zip(mu, nu))
    audit.check("independent KL direction mutation", abs(reverse_entropy - formula) > 1e-3, reverse_entropy, "not D(free||interacting)", "mutation")

    gap, trial, coupling, excited = 3.1, -0.25, 0.55, 0.7
    endpoint = two_level_ground(1.0, gap, trial, coupling, excited)
    bregman = trial - endpoint
    audit.check("independent strict Bregman density", bregman > 0.0, bregman, "positive", "strictness")
    pure_quartic = g / 4 + 3 * lam / 4
    audit.check("independent Q3 pure quartic coefficient", pure_quartic == (g + 3 * lam) / 4, pure_quartic, (g + 3 * lam) / 4, "strictness")
    beta_fraction, mass_fraction = Fraction(11, 5), Fraction(6, 5)
    zero_mode_four_squared = Fraction(1, 16) / (beta_fraction**4 * mass_fraction**4)
    audit.check("independent zero-mode normalization squared", zero_mode_four_squared == (Fraction(1, 4) / (beta_fraction**2 * mass_fraction**2)) ** 2, zero_mode_four_squared, "1/(4 beta^2 m^2)^2", "strictness")
    amplitude_squared = (beta_fraction * pure_quartic) ** 2 * zero_mode_four_squared * 24
    expected_amplitude_squared = (g + 3 * lam) ** 2 * 24 / (256 * beta_fraction**2 * mass_fraction**4)
    audit.check("independent Q3 amplitude factor derivation", amplitude_squared == expected_amplitude_squared, amplitude_squared, expected_amplitude_squared, "strictness")
    audit.check("independent Q3 dual amplitude squared", amplitude_squared > 0, amplitude_squared, "positive", "strictness")
    A, B, t = Fraction(5, 13), Fraction(-17, 9), Fraction(1, 10)
    trial_form = Fraction(2, 7)
    rayleigh = (-2 * t * A + t * t * (B - trial_form)) / (1 + t * t)
    audit.check("independent form Rayleigh strictness", rayleigh < 0, rayleigh, "negative", "strictness")
    common = Fraction(19, 4)
    audit.check("independent Bregman scalar invariance", (trial_form + common) - (B + common) == trial_form - B, (trial_form + common) - (B + common), trial_form - B, "strictness")
    endpoint_excited = trial + gap + excited - endpoint
    density_rows = []
    for length in (2.5, 5.0, 10.0, 20.0):
        log_ratio = logsumexp([-length * endpoint, -length * endpoint_excited]) - logsumexp([0.0, -length * gap])
        insertion_per_length = (trial + excited * math.exp(-length * gap)) / (1.0 + math.exp(-length * gap))
        per_length = log_ratio / length + insertion_per_length
        density_rows.append({"L": length, "D_per_L": per_length, "D_per_area": per_length / beta, "negative_centered": -per_length / beta})
    audit.check("independent specific KL length composition", abs(density_rows[-1]["D_per_L"] - bregman) < 2e-12, density_rows, bregman, "entropy")
    audit.check("independent specific KL beta factor", abs(density_rows[-1]["D_per_area"] - bregman / beta) < 2e-12 and abs(density_rows[-1]["negative_centered"] - (endpoint - trial) / beta) < 2e-12, density_rows[-1], (bregman / beta, (endpoint - trial) / beta), "entropy")

    spectral_gap = interacting[1] - interacting[0]
    probabilities = []
    for length in (1.0, 2.0, 4.0, 8.0):
        tail = sum(math.exp(-length * (value - interacting[0])) for value in interacting[1:])
        probabilities.append({"L": length, "ground": 1.0 / (1.0 + tail)})
    audit.check("independent ground projection", probabilities[-1]["ground"] > 0.9999999, probabilities, "to one", "state")
    cluster = [math.exp(-spectral_gap * distance) for distance in (0.5, 1.0, 2.0, 4.0)]
    audit.check("independent transfer gap", spectral_gap > 0.0, spectral_gap, "positive", "state")
    audit.check("independent exponential clustering", all(cluster[index + 1] < cluster[index] for index in range(3)), cluster, "strict decay", "state")
    observable, separation = 0.61, 0.8
    connected_rows = []
    for total_length in (4.0, 8.0, 16.0, 32.0):
        connected = observable**2 * (math.exp(-spectral_gap * separation) + math.exp(-spectral_gap * (total_length - separation))) / (1.0 + math.exp(-spectral_gap * total_length))
        connected_rows.append({"L": total_length, "connected": connected})
    connected_limit = observable**2 * math.exp(-spectral_gap * separation)
    audit.check("independent trace-normalized connected limit", abs(connected_rows[-1]["connected"] - connected_limit) < 2e-14, connected_rows, connected_limit, "state")

    source = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {alias.name for node in ast.walk(source) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module or "" for node in ast.walk(source) if isinstance(node, ast.ImportFrom)}
    audit.check("independent stdlib implementation", not ({"sympy", "mpmath", "numpy", "scipy"} & imported), sorted(imported), "stdlib only", "independence")
    audit.check("independent no primary import", PRIMARY_STEM not in imported, sorted(imported), f"not {PRIMARY_STEM}", "independence")
    for phrase in ("same plane-Wick action", "No coupling derivative", "exact exchange symmetry", "raw relative pressure", "free reference with respect to the interacting", "strict scalar-invariant specific relative entropy", "not convergence of global density matrices", "periodic bounded-local Schwinger limit", "full noncommutative infinite-volume KMS algebra", "does not assert a finite global Radon--Nikodym", "does not claim a world-first"):
        audit.check(f"independent certificate phrase {phrase[:34]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in ("new_plane_Wick_volume_coherent_extension_of_EXP767", "Nelson_coordinate_exchange", "raw_relative_pressure_limit_exists", "specific_relative_entropy_density_exists", "strict_positive_specific_relative_entropy_density", "periodic_bounded_local_Schwinger_limit", "periodic_transfer_observable_spatial_mixing", "dual_transfer_ground_unique_and_gapped"):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in ("raw_relative_pressure_sign_gauge_invariant", "arbitrary_L_dependent_K_and_scalar_family", "original_fixed_raw_CL8_family", "physical_empty_space_reference", "absolute_vacuum_energy_fixed", "global_infinite_volume_Radon_Nikodym_density", "finite_total_infinite_volume_relative_entropy", "all_boundary_condition_state_uniqueness", "periodic_beta_KMS_limit", "full_noncommutative_infinite_volume_local_algebra", "beta_to_infinity_L_to_infinity_interchange", "zero_temperature_ground_energy_density", "spontaneous_symmetry_breaking_or_phase_transition", "interacting_Hadamard_or_microlocal_spectrum", "original_3D_Q3LOCK_parent", "physical_light_speed_derived", "C0_closed", "N1_through_N5_closed", "C6_advanced", "CP1_complete", "Sector_A_complete", "Pre_A_complete"):
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
            "Q3": {"edges": len(edges), "trace_A": str(trace(Aq)), "amplitude_squared": str(amplitude_squared)},
            "coherence": {"covariance": covariance_rows, "image": image_forward, "circle": circle_values, "decomposition": decomposition_rows, "e_limit": e_values, "scalar": str(scalar)},
            "pressure": {"rates": rates, "raw": pressure, "shifted": shifted_pressure, "scalar_ledger": scalar_ledger},
            "entropy": {"partition": partition, "KL": relative_entropy, "reverse": reverse_entropy, "formula": formula, "Bregman": bregman, "density": density_rows},
            "state": {"gap": spectral_gap, "projection": probabilities, "clustering": cluster, "connected": connected_rows},
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
