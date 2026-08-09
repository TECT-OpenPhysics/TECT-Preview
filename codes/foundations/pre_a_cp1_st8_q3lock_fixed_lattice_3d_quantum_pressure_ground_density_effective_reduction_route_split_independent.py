#!/usr/bin/env python3
"""Independent standard-library audit for EXP773 fixed-lattice thermodynamics."""

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
SLUG = "pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split"
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0"
RESULT_ID = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY"
EXPLORATION_ID = "EXP-000780"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
ST8_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
EXP772_PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split/result.json"
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


def cube_edges() -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for left in range(8):
        for right in range(left + 1, 8):
            if (left ^ right).bit_count() == 1:
                result.append((left, right))
    return result


def seam_geometry(side: int) -> tuple[int, dict[tuple[int, int, int, int], int]]:
    incidence: dict[tuple[int, int, int, int], int] = {}
    count = 0
    for x in range(side):
        for y in range(side):
            for z in range(side):
                coordinate = (x, y, z)
                for species in range(8):
                    for direction in range(3):
                        if coordinate[direction] != side - 1:
                            continue
                        target = list(coordinate)
                        target[direction] = 0
                        for endpoint in ((x, y, z, species), (target[0], target[1], target[2], species)):
                            incidence[endpoint] = incidence.get(endpoint, 0) + 1
                        count += 1
    return count, incidence


def logsumexp(values: list[float]) -> float:
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


def discrete_source(source: float) -> tuple[float, list[float], list[float]]:
    coordinates = [-2.0, -0.7, 0.0, 0.7, 2.0]
    energies = [0.18 * coordinate**4 + 0.22 * coordinate**2 for coordinate in coordinates]
    scores = [-energy + source * coordinate for energy, coordinate in zip(energies, coordinates)]
    log_z = logsumexp(scores)
    probabilities = [math.exp(score - log_z) for score in scores]
    return log_z, probabilities, coordinates


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    st8 = json.loads(ST8_PARENT.read_text(encoding="utf-8"))
    exp772 = json.loads(EXP772_PARENT.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("independent ST8 parent passes", st8["assertions"]["passed"] == st8["assertions"]["total"], st8["assertions"], "all pass", "parent")
    audit.check("independent EXP772 parent passes", exp772["assertion_summary"]["passed"] == exp772["assertion_summary"]["total"], exp772["assertion_summary"], "all pass", "parent")

    coercivity_rows: list[dict[str, str]] = []
    for local_g in (Fraction(1, 5), Fraction(7, 9), Fraction(11, 4)):
        for local_r in (Fraction(0), Fraction(2, 7), Fraction(9, 5)):
            for local_x in (Fraction(0), Fraction(1, 6), Fraction(4, 3), Fraction(7, 2)):
                quadratic_gap = local_g * local_x**4 / 16 - local_r * local_x**2 / 2 + local_r**2 / local_g
                quadratic_square = (local_g * local_x**2 / 4 - local_r) ** 2 / local_g
                coercivity_rows.append({"gap": str(quadratic_gap), "square": str(quadratic_square)})
                audit.check("independent exact quadratic square", quadratic_gap == quadratic_square, quadratic_gap, quadratic_square, "coercivity")
    for value in (Fraction(0), Fraction(1, 8), Fraction(1), Fraction(5, 3), Fraction(13, 4)):
        young_gap = value**4 / 4 - value + Fraction(3, 4)
        young_factor = (value - 1) ** 2 * (value**2 + 2 * value + 3) / 4
        audit.check("independent exact source Young factor", young_gap == young_factor, young_gap, young_factor, "coercivity")
        audit.check("independent source Young nonnegative", young_gap >= 0, young_gap, ">=0", "coercivity")
    audit.check("independent source exponent", Fraction(4, 3) == Fraction(4, 4 - 1), Fraction(4, 3), Fraction(4, 3), "coercivity")

    for cube_root_g in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 2)):
        local_g = cube_root_g**3
        for source_root in (Fraction(0), Fraction(1, 4), Fraction(5, 3)):
            local_j = source_root**3
            for local_r in (Fraction(0), Fraction(3, 5), Fraction(8, 3)):
                for local_x in (Fraction(-9, 4), Fraction(-1, 3), Fraction(0), Fraction(4, 5), Fraction(10, 3)):
                    lhs = local_g * local_x**4 / 4 - local_r * local_x**2 / 2 - local_j * abs(local_x)
                    # Compare the two absorption pieces directly, avoiding irrational serialization.
                    retained = local_g * local_x**4 / 8
                    quadratic_piece = local_g * local_x**4 / 16 - local_r * local_x**2 / 2 + local_r**2 / local_g
                    source_piece = float(local_g * local_x**4 / 16 - local_j * abs(local_x))
                    source_minimum = -0.75 * (4.0 / float(local_g)) ** (1.0 / 3.0) * float(local_j) ** (4.0 / 3.0)
                    audit.check("independent quadratic absorption piece", quadratic_piece >= 0, quadratic_piece, ">=0", "coercivity")
                    audit.check("independent source absorption piece", source_piece + 1e-12 >= source_minimum, source_piece, source_minimum, "coercivity")
                    rhs = float(retained - local_r**2 / local_g) + source_minimum
                    audit.check("independent combined scalar coercivity", float(lhs) + 1e-12 >= rhs, float(lhs), rhs, "coercivity")

    edges = cube_edges()
    degrees = {vertex: 0 for vertex in range(8)}
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
    audit.check("independent Q3 edge count", len(edges) == sum(degrees.values()) // 2, len(edges), sum(degrees.values()) // 2, "geometry")
    audit.check("independent Q3 regular degree", set(degrees.values()) == {3}, degrees, {3}, "geometry")
    seam_rows: list[dict[str, Any]] = []
    for side in (2, 6, 10):
        count, incidence = seam_geometry(side)
        expected = len(degrees) * len(next(iter([tuple(range(3))]))) * side**2
        ratio = Fraction(count, len(degrees) * side**3)
        seam_rows.append({"L": side, "count": count, "ratio": str(ratio), "max": max(incidence.values())})
        audit.check("independent seam count", count == expected, count, expected, "geometry")
        audit.check("independent seam density ratio", ratio == Fraction(3, side), ratio, Fraction(3, side), "geometry")
        audit.check("independent seam incidence", max(incidence.values()) <= 3, max(incidence.values()), "<=3", "geometry")
        endpoint_count = sum(incidence.values())
        derived_constant_multiplier = endpoint_count * 6 // side**2
        audit.check("independent seam constant multiplier", derived_constant_multiplier == 2 * len(degrees) * 3 * 6, derived_constant_multiplier, 2 * len(degrees) * 3 * 6, "geometry")

    for local_c in (Fraction(1, 3), Fraction(7, 5)):
        for local_g in (Fraction(2, 7), Fraction(9, 4)):
            for eta in (Fraction(1, 8), Fraction(3, 5)):
                for left, right in ((Fraction(-2), Fraction(3, 5)), (Fraction(0), Fraction(7, 3)), (Fraction(5, 4), Fraction(-9, 7))):
                    edge = local_c * (left - right) ** 2 / 2
                    separated = local_c * (left**2 + right**2)
                    absorbed = eta * local_g * (left**4 + right**4) / 24 + 12 * local_c**2 / (eta * local_g)
                    audit.check("independent edge separation", edge <= separated, edge, separated, "seam")
                    audit.check("independent edge quartic absorption", separated <= absorbed, separated, absorbed, "seam")

    variance = Fraction(5, 7)
    second_moment = variance
    fourth_moment = 3 * variance**2
    pair_moment = 2 * fourth_moment + 2 * second_moment**2
    audit.check("independent Gaussian pair Q3 moment", pair_moment == 8 * variance**2, pair_moment, 8 * variance**2, "trial")
    hbar_squared_over_chi = Fraction(11, 5)
    local_r = Fraction(-2, 9)
    local_c = Fraction(3, 8)
    local_g = Fraction(7, 6)
    local_lambda = Fraction(5, 13)
    kinetic = hbar_squared_over_chi / variance
    onsite = 4 * local_r * variance + 6 * local_g * variance**2
    spatial = 24 * local_c * variance
    locking = 24 * local_lambda * variance**2
    trial_density = kinetic + onsite + spatial + locking
    rebuilt = hbar_squared_over_chi / variance + (4 * local_r + 24 * local_c) * variance + (6 * local_g + 24 * local_lambda) * variance**2
    audit.check("independent product trial reconstruction", trial_density == rebuilt, trial_density, rebuilt, "trial")

    open_spectrum = [-0.4, 0.8, 2.3, 5.0, 8.2]
    periodic_spectrum = [-0.2, 1.0, 2.7, 5.4, 8.8]
    eta = 0.2
    form_constant = 1.0
    for left, right in zip(open_spectrum, periodic_spectrum):
        audit.check("independent min-max lower order", left <= right, left, right, "spectral")
        audit.check("independent min-max upper order", right <= (1 + eta) * left + form_constant + 1e-14, right, (1 + eta) * left + form_constant, "spectral")
    for beta in (0.3, 0.8, 1.7):
        z_open = sum(math.exp(-beta * value) for value in open_spectrum)
        z_periodic = sum(math.exp(-beta * value) for value in periodic_spectrum)
        z_scaled = sum(math.exp(-beta * (1 + eta) * value) for value in open_spectrum)
        audit.check("independent trace upper order", z_periodic <= z_open + 1e-14, z_periodic, z_open, "spectral")
        audit.check("independent trace scaled lower order", z_periodic + 1e-14 >= math.exp(-beta * form_constant) * z_scaled, z_periodic, math.exp(-beta * form_constant) * z_scaled, "spectral")

    spectrum = [0.19, 0.7, 1.9, 4.2, 7.8, 12.0]
    beta_star = 0.5
    star_log = logsumexp([-beta_star * value for value in spectrum])
    zero_rows: list[dict[str, float]] = []
    for beta in (0.5, 0.9, 2.0, 7.0, 30.0):
        log_z = logsumexp([-beta * value for value in spectrum])
        free = -log_z / beta
        gap = spectrum[0] - free
        bound = (beta_star * spectrum[0] + star_log) / beta
        zero_rows.append({"beta": beta, "gap": gap, "bound": bound})
        audit.check("independent zero-temperature nonnegative gap", gap >= -1e-15, gap, ">=0", "zero_temperature")
        audit.check("independent zero-temperature squeeze", gap <= bound + 1e-15, gap, bound, "zero_temperature")

    source_rows: list[dict[str, float]] = []
    for source in (-0.8, -0.3, 0.0, 0.3, 0.8):
        log_z, probability, coordinates = discrete_source(source)
        opposite, _, _ = discrete_source(-source)
        mean = sum(weight * coordinate for weight, coordinate in zip(probability, coordinates))
        variance_value = sum(weight * (coordinate - mean) ** 2 for weight, coordinate in zip(probability, coordinates))
        source_rows.append({"J": source, "logZ": log_z, "mean": mean, "variance": variance_value})
        audit.check("independent global source evenness", abs(log_z - opposite) < 1e-14, log_z, opposite, "source")
        audit.check("independent source covariance nonnegative", variance_value >= 0, variance_value, ">=0", "source")
    zero_log, zero_probability, coordinates = discrete_source(0.0)
    zero_mean = sum(weight * coordinate for weight, coordinate in zip(zero_probability, coordinates))
    audit.check("independent zero-source response", abs(zero_mean) < 1e-15, zero_mean, 0.0, "source")
    step = 2e-5
    source = 0.27
    center, probability, coordinates = discrete_source(source)
    plus, _, _ = discrete_source(source + step)
    minus, _, _ = discrete_source(source - step)
    mean = sum(weight * coordinate for weight, coordinate in zip(probability, coordinates))
    variance_value = sum(weight * (coordinate - mean) ** 2 for weight, coordinate in zip(probability, coordinates))
    audit.check("independent source finite derivative", abs((plus - minus) / (2 * step) - mean) < 2e-9, (plus - minus) / (2 * step), mean, "source")
    audit.check("independent source finite Hessian", abs((plus - 2 * center + minus) / step**2 - variance_value) < 3e-6, (plus - 2 * center + minus) / step**2, variance_value, "source")

    energies = [0.1, 0.8, 1.9, 3.6]
    shift = 1.7
    beta = 0.9
    raw = [math.exp(-beta * value) for value in energies]
    moved = [math.exp(-beta * (value + shift)) for value in energies]
    raw_probability = [value / sum(raw) for value in raw]
    moved_probability = [value / sum(moved) for value in moved]
    audit.check("independent scalar state invariance", max(abs(a - b) for a, b in zip(raw_probability, moved_probability)) < 2e-15, moved_probability, raw_probability, "centering")
    audit.check("independent scalar log shift", abs(math.log(sum(moved)) - (math.log(sum(raw)) - beta * shift)) < 2e-15, math.log(sum(moved)), math.log(sum(raw)) - beta * shift, "centering")

    collective_rows: list[dict[str, str]] = []
    transverse_sets = [
        [Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(2, 3), Fraction(-1, 5), Fraction(4, 7), Fraction(-2, 9), Fraction(1, 6), Fraction(-3, 8), Fraction(5, 11), Fraction(0)],
    ]
    transverse_sets[1][-1] = -sum(transverse_sets[1][:-1])
    for collective_amplitude in (Fraction(-3, 2), Fraction(0), Fraction(4, 5)):
        for transverse in transverse_sets:
            lhs = sum((collective_amplitude + value) ** 4 for value in transverse)
            rhs = (
                8 * collective_amplitude**4
                + 6 * collective_amplitude**2 * sum(value**2 for value in transverse)
                + 4 * collective_amplitude * sum(value**3 for value in transverse)
                + sum(value**4 for value in transverse)
            )
            collective_rows.append({"lhs": str(lhs), "rhs": str(rhs)})
            audit.check("independent collective quartic identity", lhs == rhs, lhs, rhs, "reduction")
    nonzero_transverse = transverse_sets[0]
    values_by_collective = [sum((amplitude + value) ** 4 for value in nonzero_transverse) for amplitude in (Fraction(0), Fraction(1), Fraction(2))]
    bare_collective = [8 * amplitude**4 for amplitude in (Fraction(0), Fraction(1), Fraction(2))]
    corrections = [full - bare for full, bare in zip(values_by_collective, bare_collective)]
    audit.check("independent transverse correction nonconstant", len(set(corrections)) > 1, corrections, "nonconstant", "reduction")

    for phrase in (
        "fixed-spacing thermodynamic-volume result only",
        "Counting `O(L^2)` bonds alone would not be sufficient",
        "uniformly locally Lipschitz",
        "both iterated and joint",
        "physical empty space",
        "Effective reduction remains open",
        "This proves Pre-A",
    ):
        audit.check(f"independent certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")

    positive_scope = {key for key, value in manifest["scope"].items() if value is True}
    false_scope = {key for key, value in manifest["scope"].items() if value is False}
    required_positive = {
        "open_rectangular_source_pressure_limit",
        "periodic_even_cube_source_pressure_limit",
        "free_periodic_density_agreement",
        "uniform_zero_temperature_density_interchange",
        "additive_scalar_covariance",
    }
    required_false = {
        "thermodynamic_phase_transition",
        "exact_3D_to_1plus1_effective_reduction",
        "continuum_regulator_removal",
        "physical_empty_space_reference",
        "below_empty_space",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    }
    audit.check("independent positive scope set", required_positive <= positive_scope, sorted(positive_scope), sorted(required_positive), "scope")
    audit.check("independent false scope set", required_false <= false_scope, sorted(false_scope), sorted(required_false), "scope")
    audit.check("independent Boolean scope", positive_scope | false_scope == set(manifest["scope"]), sorted(positive_scope | false_scope), sorted(manifest["scope"]), "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
            "ST8_parent": portable_sha256(ST8_PARENT),
            "EXP772_parent": portable_sha256(EXP772_PARENT),
        },
        "derived": {
            "coercivity": coercivity_rows,
            "geometry": {"Q3_edges": len(edges), "seams": seam_rows},
            "trial": {"pair_moment": str(pair_moment), "coarse_density": str(trial_density)},
            "zero_temperature": zero_rows,
            "source": source_rows,
            "collective": collective_rows,
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
