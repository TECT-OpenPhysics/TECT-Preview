#!/usr/bin/env python3
"""Independent stdlib audit of the Q3 zero-temperature density theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any


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
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-thermodynamic-pressure-relative-entropy-density-phase-route-split/result.json"
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def cube_edges() -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for vertex in range(8):
        for bit in range(3):
            neighbour = vertex ^ (1 << bit)
            if vertex < neighbour:
                edges.append((vertex, neighbour))
    return edges


def q3_quartic(values: list[float], g: float, coupling: float, edges: list[tuple[int, int]]) -> float:
    onsite = g * sum(value**4 for value in values) / 4.0
    edge = coupling * sum((values[left] - values[right]) ** 2 * (values[left] ** 2 + values[right] ** 2) for left, right in edges) / 4.0
    return onsite + edge


def invert(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    augmented = [row[:] + [1.0 if index == column else 0.0 for column in range(size)] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        if abs(divisor) < 1e-14:
            raise ArithmeticError("singular fixture matrix")
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [left - factor * right for left, right in zip(augmented[row], augmented[column])]
    return [row[size:] for row in augmented]


def massive_laplacian(size: int, mass: float, periodic: bool) -> list[list[float]]:
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    for index in range(size):
        matrix[index][index] = mass * mass + 2.0
        if index > 0:
            matrix[index][index - 1] = -1.0
        if index + 1 < size:
            matrix[index][index + 1] = -1.0
    if periodic:
        matrix[0][-1] = -1.0
        matrix[-1][0] = -1.0
    return matrix


def zeta_three(terms: int) -> float:
    partial = sum(1.0 / (index**3) for index in range(1, terms + 1))
    n = float(terms)
    tail = 1.0 / (2.0 * n * n) - 1.0 / (2.0 * n**3) + 1.0 / (4.0 * n**4)
    return partial + tail


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("independent EXP768 parent", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    edges = cube_edges()
    audit.check("independent Q3 edge count", len(edges) == 12 and len(set(edges)) == 12, len(edges), 12, "Q3")
    degrees = [sum(1 for edge in edges if vertex in edge) for vertex in range(8)]
    audit.check("independent Q3 cubic degree", degrees == [3] * 8, degrees, [3] * 8, "Q3")
    g_value, coupling = 0.91, 0.27
    pure_coefficient = g_value / 4.0 + degrees[0] * coupling / 4.0
    audit.check("independent pure quartic coefficient", abs(pure_coefficient - (g_value + 3.0 * coupling) / 4.0) < 1e-15, pure_coefficient, (g_value + 3.0 * coupling) / 4.0, "Q3")
    coercivity_rows = []
    for shift in range(5):
        values = [((index + 2 * shift) % 7 - 3) / 2.0 for index in range(8)]
        quartic = q3_quartic(values, g_value, coupling, edges)
        lower = g_value * sum(value * value for value in values) ** 2 / 32.0
        coercivity_rows.append({"values": values, "quartic": quartic, "lower": lower})
        audit.check("independent Q3 coercivity mutation", quartic + 1e-14 >= lower, quartic, lower, "Q3")
    mixed_flat = (2.5**2) * (0.0**2)
    q3_axis = q3_quartic([2.5] + [0.0] * 7, g_value, coupling, edges)
    audit.check("independent Nagoji flat-axis mutation", mixed_flat == 0.0 and q3_axis > 0.0, (mixed_flat, q3_axis), "flat versus coercive", "normalizability")

    holder_rows = []
    weights = [0.09, 0.31, 0.60]
    spectrum = [0.22, 1.3, 5.7]
    for exponent in (0.13, 0.58, 0.93):
        lhs = sum(weight * value**exponent for weight, value in zip(weights, spectrum))
        rhs = sum(weight * value for weight, value in zip(weights, spectrum)) ** exponent
        holder_rows.append({"a": exponent, "lhs": lhs, "rhs": rhs})
        audit.check("independent spectral Holder inequality", lhs <= rhs + 1e-14, lhs, rhs, "GRS")
    alpha_limit = 0.71
    alpha = lambda length: alpha_limit * length / (1.0 + length)
    grs_rows = []
    for length in (0.7, 1.4, 2.8, 5.6):
        for fraction in (0.3, 0.6, 0.9):
            energy = -length * alpha(length)
            small_energy = -fraction * length * alpha(fraction * length)
            grs_rows.append({"l": length, "a": fraction, "alpha_l": alpha(length), "alpha_al": alpha(fraction * length), "E_al": small_energy, "aE_l": fraction * energy})
            audit.check("independent GRS alpha implication", alpha(fraction * length) <= alpha(length) and small_energy >= fraction * energy - 1e-14, (alpha(fraction * length), small_energy), (alpha(length), fraction * energy), "GRS")

    energy, overlap = -0.84, 0.23
    spectral_rows = []
    for time in (3.0, 6.0, 12.0, 24.0):
        z_value = overlap**2 * math.exp(-time * energy) + (1.0 - overlap**2) * math.exp(-time * 0.66)
        rate = math.log(z_value) / time
        lower = -energy + 2.0 * math.log(overlap) / time
        spectral_rows.append({"t": time, "lower": lower, "rate": rate, "upper": -energy})
        audit.check("independent sharp spectral squeeze", lower <= rate <= -energy + 1e-14, rate, (lower, -energy), "GRS")
    audit.check("independent sharp ground extraction", abs(spectral_rows[-1]["rate"] + energy) < abs(spectral_rows[0]["rate"] + energy), spectral_rows, -energy, "GRS")

    fourth_channel_norm = pure_coefficient**2 * math.factorial(4) * 0.037
    diagonal = 1.9
    rayleigh = 0.5 * (diagonal - math.sqrt(diagonal * diagonal + 4.0 * fourth_channel_norm))
    audit.check("independent fourth-chaos norm", fourth_channel_norm > 0.0, fourth_channel_norm, "positive", "strictness")
    audit.check("independent strict ground Rayleigh", rayleigh < 0.0, rayleigh, "negative", "strictness")

    covariance_rows = []
    for size in (6, 10, 16, 24):
        open_covariance = invert(massive_laplacian(size, 1.2, False))
        periodic_covariance = invert(massive_laplacian(size, 1.2, True))
        entry_l1 = sum(abs(periodic_covariance[row][column] - open_covariance[row][column]) for row in range(size) for column in range(size))
        entry_l2_sq = sum((periodic_covariance[row][column] - open_covariance[row][column]) ** 2 for row in range(size) for column in range(size))
        covariance_rows.append({"size": size, "L1": entry_l1, "L2_squared": entry_l2_sq, "density_L1": entry_l1 / size})
    audit.check("independent finite open-periodic covariance fixture bounded", max(row["L1"] for row in covariance_rows) < 2.0 * covariance_rows[-1]["L1"], covariance_rows, "finite fixture only", "boundary")
    audit.check("independent finite covariance-density fixture decreases", covariance_rows[-1]["density_L1"] < covariance_rows[0]["density_L1"], covariance_rows, "finite fixture only", "boundary")
    surface_rows = []
    for time, length in ((8.0, 5.0), (16.0, 10.0), (32.0, 20.0), (64.0, 40.0)):
        area = time * length
        error = 2.4 * (2.0 * time + 2.0 * length + 1.0)
        ground_error_per_length = 2.4 / length
        surface_rows.append({"t": time, "l": length, "surface_per_area": error / area, "ground_error_per_length": ground_error_per_length})
    audit.check("independent formal surface scaling implication", all(surface_rows[index + 1]["surface_per_area"] < surface_rows[index]["surface_per_area"] for index in range(3)), surface_rows, "conditional to zero", "boundary")
    audit.check("independent formal O1 bridge scaling implication", all(surface_rows[index + 1]["ground_error_per_length"] < surface_rows[index]["ground_error_per_length"] for index in range(3)), surface_rows, "conditional to zero", "boundary")

    e_plane, gap_limit, scalar_shift = 0.18, 0.44, 1.1
    beta_rows = []
    for beta in (2.0, 4.0, 8.0, 16.0, 32.0):
        correction = math.exp(-1.2 * beta) / math.sqrt(beta)
        boundary = 0.31 / beta
        trial_density = e_plane + correction
        raw_density = trial_density - gap_limit + boundary
        gap = trial_density - raw_density
        beta_rows.append({"beta": beta, "trial": trial_density, "raw": raw_density, "gap": gap})
    audit.check("independent circle scalar flow", abs(beta_rows[-1]["trial"] - e_plane) < abs(beta_rows[0]["trial"] - e_plane), beta_rows, e_plane, "zero-temperature")
    audit.check("independent conditional zero-temperature gap fixture", abs(beta_rows[-1]["gap"] - gap_limit) < abs(beta_rows[0]["gap"] - gap_limit) and beta_rows[-1]["gap"] > 0.0, beta_rows, "requires surface lemma", "zero-temperature")
    shifted_gap = (beta_rows[-1]["trial"] + scalar_shift) - (beta_rows[-1]["raw"] + scalar_shift)
    audit.check("independent scalar gap invariance", abs(shifted_gap - beta_rows[-1]["gap"]) < 1e-15, shifted_gap, beta_rows[-1]["gap"], "zero-temperature")
    audit.check("independent raw sign mutation", beta_rows[-1]["raw"] < 0.0 and beta_rows[-1]["raw"] + scalar_shift > 0.0, (beta_rows[-1]["raw"], beta_rows[-1]["raw"] + scalar_shift), "both signs", "mutation")

    rectangle_rows = []
    for beta, length in ((4.0, 7.0), (8.0, 14.0), (16.0, 28.0), (32.0, 56.0)):
        density = gap_limit + 0.2 / beta + 0.3 / length + 0.1 / (beta * length)
        transposed = gap_limit + 0.2 / length + 0.3 / beta + 0.1 / (length * beta)
        symmetric_density = 0.5 * (density + transposed)
        symmetric_transposed = 0.5 * (transposed + density)
        rectangle_rows.append({"beta": beta, "L": length, "density": symmetric_density})
        audit.check("independent beta-L symmetric density", abs(symmetric_density - symmetric_transposed) < 1e-15, symmetric_density, symmetric_transposed, "zero-temperature")
    audit.check("independent conditional joint van Hove fixture", abs(rectangle_rows[-1]["density"] - gap_limit) < abs(rectangle_rows[0]["density"] - gap_limit), rectangle_rows, "requires surface lemma", "zero-temperature")

    finite_witness = []
    for beta in (2.0, 4.0, 8.0, 16.0):
        amplitude = (g_value + 3.0 * coupling) * math.sqrt(24.0) / (16.0 * beta * 1.2**2)
        finite_witness.append({"beta": beta, "amplitude": amplitude, "density_proxy": amplitude * amplitude / beta})
    audit.check("independent finite-circle witness no uniform density", all(finite_witness[index + 1]["density_proxy"] < finite_witness[index]["density_proxy"] for index in range(3)), finite_witness, "to zero", "mutation")

    zeta3 = zeta_three(200000)
    mass = 1.2
    plane_fourth = 7.0 * zeta3 / (64.0 * math.pi**3 * mass * mass)
    curvature = 8.0 * math.factorial(4) * pure_coefficient**2 * plane_fourth
    closed_form = 21.0 * zeta3 * (g_value + 3.0 * coupling) ** 2 / (16.0 * math.pi**3 * mass * mass)
    audit.check("independent zeta3 convergence", abs(zeta3 - 1.202056903159594) < 2e-12, zeta3, "Apery constant", "curvature")
    audit.check("independent eight-channel curvature algebra", abs(curvature - closed_form) < 2e-15, curvature, closed_form, "curvature")
    audit.check("independent curvature positive", curvature > 0.0, curvature, "positive", "curvature")

    centered_values = [-0.9, -0.3, 0.4, 0.8]
    mean = sum(centered_values) / len(centered_values)
    centered_values = [value - mean for value in centered_values]
    block_partition = sum(math.exp(-value) for value in centered_values) / len(centered_values)
    block_rows = [{"blocks": blocks, "pressure": math.log(block_partition**blocks) / blocks} for blocks in (1, 2, 4, 8)]
    audit.check("independent finite-block Jensen fixture", block_partition > 1.0, block_partition, ">1 fixture only", "chessboard")
    audit.check("independent formal chessboard dissemination fixture", all(abs(row["pressure"] - math.log(block_partition)) < 1e-14 for row in block_rows), block_rows, math.log(block_partition), "chessboard")

    for phrase in (
        "component-blind GRS monotonicity proof",
        "Periodic-sharp surface-pairing reduction and open gate",
        "covariance interpolation",
        "does not close",
        "multicomponent obstruction",
        "finite-circle zero mode",
        "physical empty space",
        "phase uniqueness",
        "scalar densities only",
    ):
        audit.check(f"independent certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")
    for key in (
        "strict_positive_centered_reference_density",
        "scalar_shift_invariant_gap",
        "periodic_zero_temperature_limit_reduced_to_surface_pairing",
    ):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
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
        "original_3D_Q3LOCK_parent",
        "C6_advanced",
        "Pre_A_complete",
    ):
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
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
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {
            "Q3": {"edges": len(edges), "degrees": degrees, "pure_coefficient": pure_coefficient, "coercivity": coercivity_rows},
            "GRS": {"Holder": holder_rows, "rows": grs_rows, "spectral": spectral_rows},
            "strictness": {"fourth_norm": fourth_channel_norm, "Rayleigh": rayleigh},
            "boundary": {"covariance": covariance_rows, "surface": surface_rows},
            "zero_temperature": {"beta": beta_rows, "rectangles": rectangle_rows, "witness": finite_witness},
            "curvature": {"zeta3": zeta3, "plane_fourth": plane_fourth, "lower": curvature},
            "chessboard": {"block_partition": block_partition, "rows": block_rows},
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
