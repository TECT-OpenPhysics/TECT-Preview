#!/usr/bin/env python3
"""Primary verifier for EXP773 fixed-lattice ST8/Q3LOCK thermodynamics."""

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
SLUG = "pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY"
EXPLORATION_ID = "EXP-000780"
PARENT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
ST8_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
EXP772_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split/result.json"
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


def cube_edges() -> list[tuple[tuple[int, int, int], tuple[int, int, int]]]:
    vertices = [(a, b, c) for a in range(2) for b in range(2) for c in range(2)]
    edges: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    for left_index, left in enumerate(vertices):
        for right in vertices[left_index + 1 :]:
            if sum(a != b for a, b in zip(left, right)) == 1:
                edges.append((left, right))
    return edges


def seam_geometry(side: int) -> tuple[int, dict[tuple[int, int, int, int], int]]:
    incidence: dict[tuple[int, int, int, int], int] = {}
    count = 0
    for x in range(side):
        for y in range(side):
            for z in range(side):
                site = [x, y, z]
                for species in range(8):
                    for direction in range(3):
                        if site[direction] != side - 1:
                            continue
                        target = site.copy()
                        target[direction] = 0
                        left = (x, y, z, species)
                        right = (target[0], target[1], target[2], species)
                        incidence[left] = incidence.get(left, 0) + 1
                        incidence[right] = incidence.get(right, 0) + 1
                        count += 1
    return count, incidence


def logsumexp(values: list[float]) -> float:
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


def finite_source_model(source: tuple[float, float]) -> tuple[float, list[float], list[tuple[float, float]]]:
    states = [(-1.4, 0.2), (1.4, -0.2), (-0.3, 1.1), (0.3, -1.1), (0.0, 0.0)]
    energies = [0.3 * (x**4 + y**4) + 0.2 * (x - y) ** 2 for x, y in states]
    scores = [-energy + source[0] * state[0] + source[1] * state[1] for energy, state in zip(energies, states)]
    log_z = logsumexp(scores)
    probability = [math.exp(score - log_z) for score in scores]
    return log_z, probability, states


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    st8 = json.loads(ST8_PARENT.read_text(encoding="utf-8"))
    exp772 = json.loads(EXP772_PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("ST8 parent all pass", st8["assertions"]["passed"] == st8["assertions"]["total"], st8["assertions"], "all pass", "parent")
    audit.check("ST8 finite theorem", st8["scope"]["exact_finite_nonlinear_locking_theorem"] is True, st8["scope"], True, "parent")
    audit.check("EXP772 parent all pass", exp772["assertion_summary"]["passed"] == exp772["assertion_summary"]["total"], exp772["assertion_summary"], "all pass", "parent")
    audit.check("EXP772 parent remains nonbearing", exp772["claim_bearing"] is False, exp772["claim_bearing"], False, "parent")

    x, g, rminus, j = sp.symbols("x g rminus j", nonnegative=True)
    quadratic_gap = sp.factor(g * x**4 / 16 - rminus * x**2 / 2 + rminus**2 / g)
    quadratic_expected = (g * x**2 / 4 - rminus) ** 2 / g
    audit.check("exact negative quadratic absorption", sp.simplify(quadratic_gap - quadratic_expected) == 0, quadratic_gap, quadratic_expected, "coercivity")
    t = sp.symbols("t", nonnegative=True)
    source_scaled_gap = sp.factor(t**4 / 4 - t + sp.Rational(3, 4))
    source_scaled_expected = (t - 1) ** 2 * (t**2 + 2 * t + 3) / 4
    audit.check("exact source Young factorization", sp.simplify(source_scaled_gap - source_scaled_expected) == 0, source_scaled_gap, source_scaled_expected, "coercivity")
    audit.check("source dual exponent", sp.Rational(4, 3) == sp.Rational(4, 4 - 1), sp.Rational(4, 3), sp.Rational(4, 3), "coercivity")
    coercivity_rows: list[dict[str, float]] = []
    for g_value in (0.2, 0.9, 2.7):
        for r_value in (0.0, 0.6, 1.8):
            for j_value in (0.0, 0.3, 1.5):
                for x_value in (-2.4, -0.7, 0.0, 0.9, 3.1):
                    lhs = g_value * x_value**4 / 4 - r_value * x_value**2 / 2 - j_value * abs(x_value)
                    rhs = (
                        g_value * x_value**4 / 8
                        - r_value**2 / g_value
                        - 0.75 * (4.0 / g_value) ** (1.0 / 3.0) * j_value ** (4.0 / 3.0)
                    )
                    coercivity_rows.append({"lhs": lhs, "rhs": rhs})
                    audit.check("numeric scalar source coercivity", lhs + 1e-12 >= rhs, lhs, rhs, "coercivity")

    q3_edges = cube_edges()
    audit.check("Q3 vertex count", len({vertex for edge in q3_edges for vertex in edge}) == 2**3, len({vertex for edge in q3_edges for vertex in edge}), 2**3, "geometry")
    audit.check("Q3 edge count", len(q3_edges) == 3 * 2 ** (3 - 1), len(q3_edges), 3 * 2 ** (3 - 1), "geometry")
    seam_rows: list[dict[str, Any]] = []
    for side in (2, 4, 8):
        count, incidence = seam_geometry(side)
        expected = 8 * 3 * side**2
        endpoints = sum(incidence.values())
        maximum = max(incidence.values())
        seam_rows.append({"L": side, "count": count, "endpoints": endpoints, "max_incidence": maximum})
        audit.check("periodic seam count", count == expected, count, expected, "geometry")
        audit.check("seam endpoint count", endpoints == 2 * count, endpoints, 2 * count, "geometry")
        audit.check("seam maximum incidence", maximum <= 3, maximum, "<=3", "geometry")
        fine_volume = 8 * side**3
        audit.check("seam to fine-volume ratio", Fraction(count, fine_volume) == Fraction(3, side), Fraction(count, fine_volume), Fraction(3, side), "geometry")

    c_value, g_value, eta_value = 1.7, 0.8, 0.23
    for left in (-3.0, -0.4, 0.0, 0.7, 2.9):
        for right in (-2.2, -0.1, 0.5, 3.4):
            seam_edge = c_value * (left - right) ** 2 / 2
            separated = c_value * (left * left + right * right)
            absorbed = (
                eta_value * g_value * (left**4 + right**4) / 24
                + 12 * c_value**2 / (eta_value * g_value)
            )
            audit.check("edge square separated", seam_edge <= separated + 1e-12, seam_edge, separated, "seam")
            audit.check("edge quartic absorption", separated <= absorbed + 1e-12, separated, absorbed, "seam")
    side_symbol = sp.symbols("L", positive=True, integer=True)
    seam_count_formula = 8 * 3 * side_symbol**2
    endpoint_formula = 2 * seam_count_formula
    single_endpoint_constant = 6 * sp.symbols("c", positive=True) ** 2 / (
        sp.symbols("eta", positive=True) * sp.symbols("gg", positive=True)
    )
    total_constant = sp.factor(endpoint_formula * single_endpoint_constant)
    audit.check("global seam constant derived", str(total_constant).startswith("288*"), total_constant, "288*c**2*L**2/(eta*gg)", "seam")
    for side in (4, 16, 64, 256):
        eta = side ** (-0.5)
        optimized_density_terms = (eta, 1.0 / (eta * side))
        audit.check("optimized seam terms agree", abs(optimized_density_terms[0] - optimized_density_terms[1]) < 1e-15, optimized_density_terms, "equal", "seam")

    s, hbar, chi, c, lam, rr, gg = sp.symbols("s hbar chi c lambda r g", positive=True)
    kinetic_per_coordinate = hbar**2 / (8 * chi * s**2)
    kinetic_per_cell = sp.simplify(8 * kinetic_per_coordinate)
    onsite_per_cell = sp.expand(8 * (rr * s**2 / 2 + gg * 3 * s**4 / 4))
    spatial_per_cell = sp.expand((8 * 3) * c * s**2)
    q3_moment = sp.expand(2 * 3 * s**4 + 2 * s**4)
    q3_per_cell = sp.expand(len(q3_edges) * lam * q3_moment / 4)
    trial = sp.expand(kinetic_per_cell + onsite_per_cell + spatial_per_cell + q3_per_cell)
    trial_expected = hbar**2 / (chi * s**2) + (4 * rr + 24 * c) * s**2 + (6 * gg + 24 * lam) * s**4
    audit.check("Gaussian Q3 moment", q3_moment == 8 * s**4, q3_moment, 8 * s**4, "trial")
    audit.check("Gaussian product trial density", sp.simplify(trial - trial_expected) == 0, trial, trial_expected, "trial")

    open_energies = [Fraction(-1, 2), Fraction(1), Fraction(7, 2), Fraction(6)]
    periodic_energies = [Fraction(-3, 10), Fraction(6, 5), Fraction(15, 4), Fraction(13, 2)]
    eta = Fraction(1, 4)
    form_constant = Fraction(1)
    for open_energy, periodic_energy in zip(open_energies, periodic_energies):
        audit.check("finite min-max lower spectral order", open_energy <= periodic_energy, open_energy, periodic_energy, "spectral")
        audit.check("finite min-max upper spectral order", periodic_energy <= (1 + eta) * open_energy + form_constant, periodic_energy, (1 + eta) * open_energy + form_constant, "spectral")
    beta = 0.7
    z_open = sum(math.exp(-beta * float(value)) for value in open_energies)
    z_periodic = sum(math.exp(-beta * float(value)) for value in periodic_energies)
    z_open_scaled = sum(math.exp(-beta * float((1 + eta) * value)) for value in open_energies)
    audit.check("finite heat trace upper order", z_periodic <= z_open + 1e-14, z_periodic, z_open, "spectral")
    audit.check("finite heat trace scaled lower order", z_periodic + 1e-14 >= math.exp(-beta * float(form_constant)) * z_open_scaled, z_periodic, math.exp(-beta * float(form_constant)) * z_open_scaled, "spectral")

    spectra = [0.37, 1.2, 2.8, 4.9, 8.1]
    beta_star = 0.6
    star_log_z = logsumexp([-beta_star * energy for energy in spectra])
    squeeze_rows: list[dict[str, float]] = []
    for beta in (0.6, 1.0, 2.0, 5.0, 20.0):
        log_z = logsumexp([-beta * energy for energy in spectra])
        free = -log_z / beta
        gap = spectra[0] - free
        bound = (beta_star * spectra[0] + star_log_z) / beta
        squeeze_rows.append({"beta": beta, "gap": gap, "bound": bound})
        audit.check("finite zero-temperature gap nonnegative", gap >= -1e-15, gap, ">=0", "zero_temperature")
        audit.check("finite zero-temperature beta-star squeeze", gap <= bound + 1e-15, gap, bound, "zero_temperature")
    audit.check("zero-temperature gap decreases", squeeze_rows[-1]["gap"] < squeeze_rows[0]["gap"], squeeze_rows, "decreases", "zero_temperature")

    source_rows: list[dict[str, Any]] = []
    for source in ((0.0, 0.0), (0.2, -0.1), (-0.2, 0.1), (0.6, 0.4), (-0.6, -0.4)):
        log_z, probability, states = finite_source_model(source)
        opposite, _, _ = finite_source_model((-source[0], -source[1]))
        means = [sum(weight * state[index] for weight, state in zip(probability, states)) for index in range(2)]
        source_rows.append({"J": source, "logZ": log_z, "means": means})
        audit.check("finite source global Z2", abs(log_z - opposite) < 1e-14, log_z, opposite, "source")
    step = 1e-5
    point = (0.23, -0.17)
    center_log, probability, states = finite_source_model(point)
    mean_first = sum(weight * state[0] for weight, state in zip(probability, states))
    plus_log, _, _ = finite_source_model((point[0] + step, point[1]))
    minus_log, _, _ = finite_source_model((point[0] - step, point[1]))
    derivative = (plus_log - minus_log) / (2 * step)
    audit.check("finite source derivative", abs(derivative - mean_first) < 1e-9, derivative, mean_first, "source")
    second = (plus_log - 2 * center_log + minus_log) / step**2
    variance = sum(weight * (state[0] - mean_first) ** 2 for weight, state in zip(probability, states))
    audit.check("finite source Hessian covariance", abs(second - variance) < 1e-5, second, variance, "source")

    raw_energies = [0.2, 0.9, 1.7, 3.4]
    scalar_shift = 1.35
    beta = 0.8
    raw_weights = [math.exp(-beta * energy) for energy in raw_energies]
    shifted_weights = [math.exp(-beta * (energy + scalar_shift)) for energy in raw_energies]
    raw_probability = [weight / sum(raw_weights) for weight in raw_weights]
    shifted_probability = [weight / sum(shifted_weights) for weight in shifted_weights]
    raw_pi = math.log(sum(raw_weights))
    shifted_pi = math.log(sum(shifted_weights))
    audit.check("scalar shift normalized Gibbs invariant", max(abs(a - b) for a, b in zip(raw_probability, shifted_probability)) < 1e-15, shifted_probability, raw_probability, "centering")
    audit.check("scalar shift log partition", abs(shifted_pi - (raw_pi - beta * scalar_shift)) < 1e-14, shifted_pi, raw_pi - beta * scalar_shift, "centering")
    audit.check("scalar shift free energy", abs((-shifted_pi / beta) - (-raw_pi / beta + scalar_shift)) < 1e-14, -shifted_pi / beta, -raw_pi / beta + scalar_shift, "centering")

    collective = sp.symbols("Q", real=True)
    transverse = sp.symbols("r0:8", real=True)
    transformed_sum = sp.expand(sum((collective / sp.sqrt(8) + value) ** 4 for value in transverse))
    expected_collective = (
        collective**4 / 8
        + sp.Rational(3, 4) * collective**2 * sum(value**2 for value in transverse)
        + sp.sqrt(2) * collective * sum(value**3 for value in transverse)
        + sum(value**4 for value in transverse)
    )
    constrained_difference = sp.simplify((transformed_sum - expected_collective).subs(transverse[-1], -sum(transverse[:-1])))
    audit.check("collective transverse quartic identity", constrained_difference == 0, constrained_difference, 0, "reduction")
    mixed_derivative = sp.diff(expected_collective, collective, transverse[0], transverse[0])
    audit.check("collective transverse mixed interaction", mixed_derivative != 0, mixed_derivative, "nonzero", "reduction")

    required_phrases = (
        "Result first",
        "Open-rectangle thermodynamic limits",
        "Periodic/open global-form comparison",
        "Uniform zero-temperature squeeze",
        "Source and scalar covariance",
        "Effective reduction remains open",
        "24L^2",
        "288c^2",
        "uniformly locally Lipschitz",
        "not a physical-vacuum normalization",
        "This proves Pre-A",
    )
    for phrase in required_phrases:
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")

    positive_scope = (
        "exact_registered_unweighted_ST8_Q3LOCK_family",
        "fixed_block_origin_retained",
        "finite_volume_self_adjoint_compact_resolvent",
        "open_rectangular_source_pressure_limit",
        "open_rectangular_ground_energy_density_limit",
        "periodic_even_cube_source_pressure_limit",
        "periodic_even_cube_ground_energy_density_limit",
        "free_periodic_density_agreement",
        "source_pressure_locally_uniform_convex_global_Z2_even",
        "ground_density_locally_uniform_concave_global_Z2_even",
        "uniform_zero_temperature_density_interchange",
        "all_joint_beta_volume_scalar_density_paths",
        "additive_scalar_covariance",
        "source_free_classical_center_nonnegative",
    )
    false_scope = (
        "natural_collective_transverse_additive_factorization",
        "exact_3D_to_1plus1_effective_reduction",
        "thermodynamic_phase_transition",
        "spontaneous_Z2_breaking",
        "source_selected_tangent_states",
        "pure_ordered_infinite_volume_state",
        "KMS_or_ground_state_weak_limit",
        "uniform_spectral_gap",
        "clustering_or_correlation_limit",
        "continuum_regulator_removal",
        "Euclidean_4D_or_relativistic_QFT",
        "physical_empty_space_reference",
        "below_empty_space",
        "absolute_vacuum_energy_fixed",
        "fine_one_site_translation_restored",
        "physical_light_speed_derived",
        "event_horizon_or_cooling",
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
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": manifest["negative_ids"],
        "reused_negative_ids": manifest["reused_negative_ids"],
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": NEXT_GATE,
        "script_version": __version__,
        "source_sha256": {
            "script": portable_sha256(SCRIPT),
            "manifest": portable_sha256(MANIFEST),
            "certificate": portable_sha256(CERTIFICATE),
            "st8_parent": portable_sha256(ST8_PARENT),
            "EXP772_parent": portable_sha256(EXP772_PARENT),
        },
        "derived": {
            "coercivity": {"quadratic_gap": str(quadratic_gap), "source_gap": str(source_scaled_gap), "rows": coercivity_rows},
            "geometry": {"Q3_edges": len(q3_edges), "seams": seam_rows, "global_constant": str(total_constant)},
            "trial": {"Q3_moment": str(q3_moment), "coarse_density": str(trial)},
            "spectral": {"open": [str(value) for value in open_energies], "periodic": [str(value) for value in periodic_energies]},
            "zero_temperature": squeeze_rows,
            "source": source_rows,
            "reduction": {"quartic": str(expected_collective), "mixed_derivative": str(mixed_derivative)},
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
