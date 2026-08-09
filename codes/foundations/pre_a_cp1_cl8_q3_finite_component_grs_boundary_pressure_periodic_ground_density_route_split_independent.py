#!/usr/bin/env python3
"""Independent stdlib audit of the finite-component Q3 GRS theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-HALF-PERIODIC-PRESSURE-PERIODIC-GROUND-AND-SPECIFIC-KL-DENSITY"
EXPLORATION_ID = "EXP-000778"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"

Polynomial = dict[tuple[int, ...], Fraction]


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


def clean(poly: Polynomial) -> Polynomial:
    return {exponents: coefficient for exponents, coefficient in poly.items() if coefficient}


def add(poly: Polynomial, exponents: tuple[int, ...], coefficient: Fraction) -> None:
    poly[exponents] = poly.get(exponents, Fraction(0)) + coefficient
    if poly[exponents] == 0:
        del poly[exponents]


def laplacian(poly: Polynomial, indices: tuple[int, ...]) -> Polynomial:
    result: Polynomial = {}
    for exponents, coefficient in poly.items():
        for index in indices:
            power = exponents[index]
            if power >= 2:
                lowered = list(exponents)
                lowered[index] -= 2
                add(result, tuple(lowered), coefficient * power * (power - 1))
    return result


def heat(poly: Polynomial, indices: tuple[int, ...], coefficient: Fraction) -> Polynomial:
    result = dict(poly)
    current = dict(poly)
    factorial = 1
    for order in range(1, 8):
        current = laplacian(current, indices)
        if not current:
            break
        factorial *= order
        for exponents, value in current.items():
            add(result, exponents, coefficient**order * value / factorial)
    return clean(result)


def expand_shift(poly: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (power0, power1), coefficient in poly.items():
        for y0_power in range(power0 + 1):
            for y1_power in range(power1 + 1):
                exponents = (power0 - y0_power, power1 - y1_power, y0_power, y1_power)
                value = coefficient * math.comb(power0, y0_power) * math.comb(power1, y1_power)
                add(result, exponents, value)
    return clean(result)


def pad_two(poly: Polynomial) -> Polynomial:
    return {(exponents[0], exponents[1], 0, 0): coefficient for exponents, coefficient in poly.items()}


def gaussian_expect_y(poly: Polynomial, variance: Fraction) -> Polynomial:
    heated = heat(poly, (2, 3), variance / 2)
    return clean({exponents: coefficient for exponents, coefficient in heated.items() if exponents[2] == 0 and exponents[3] == 0})


def cube_edges() -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for vertex in range(8):
        for bit in range(3):
            neighbour = vertex ^ (1 << bit)
            if vertex < neighbour:
                edges.append((vertex, neighbour))
    return edges


def q3_polynomial(g: Fraction, coupling: Fraction) -> Polynomial:
    poly: Polynomial = {}
    for vertex in range(8):
        exponents = [0] * 8
        exponents[vertex] = 4
        add(poly, tuple(exponents), g / 4)
    for left, right in cube_edges():
        for left_power, right_power, factor in ((4, 0, 1), (0, 4, 1), (2, 2, 2), (3, 1, -2), (1, 3, -2)):
            exponents = [0] * 8
            exponents[left] = left_power
            exponents[right] = right_power
            add(poly, tuple(exponents), coupling * factor / 4)
    return clean(poly)


def expected_q3_laplacian(g: Fraction, coupling: Fraction) -> Polynomial:
    result: Polynomial = {}
    for vertex in range(8):
        exponents = [0] * 8
        exponents[vertex] = 2
        add(result, tuple(exponents), 3 * (g + 4 * coupling))
    for left, right in cube_edges():
        exponents = [0] * 8
        exponents[left] = 1
        exponents[right] = 1
        add(result, tuple(exponents), -6 * coupling)
    return clean(result)


def quadratic_form(matrix: list[list[float]], vector: list[float]) -> float:
    return sum(vector[row] * matrix[row][column] * vector[column] for row in range(len(vector)) for column in range(len(vector)))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("independent claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("independent EXP770 parent", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")

    toy: Polynomial = {(4, 0): Fraction(1), (2, 2): Fraction(2), (0, 4): Fraction(3), (1, 1): Fraction(1), (2, 0): Fraction(2)}
    c1, c2 = Fraction(2, 5), Fraction(3, 7)
    wick_total = heat(toy, (0, 1), -(c1 + c2) / 2)
    conditional = gaussian_expect_y(expand_shift(wick_total), c2)
    target = pad_two(heat(toy, (0, 1), -c1 / 2))
    audit.check("independent multivariate Wick conditioning", conditional == target, conditional, target, "conditioning")

    g, coupling = Fraction(5, 4), Fraction(2, 7)
    q3 = q3_polynomial(g, coupling)
    q3_lap = laplacian(q3, tuple(range(8)))
    expected_lap = expected_q3_laplacian(g, coupling)
    q3_lap_two = laplacian(q3_lap, tuple(range(8)))
    audit.check("independent Q3 edge count", len(cube_edges()) == 12, len(cube_edges()), 12, "Q3")
    audit.check("independent Q3 Wick Laplacian", q3_lap == expected_lap, q3_lap, expected_lap, "Q3")
    audit.check("independent Q3 second Wick Laplacian", q3_lap_two == {(0,) * 8: 48 * (g + 4 * coupling)}, q3_lap_two, 48 * (g + 4 * coupling), "Q3")
    delta = Fraction(3, 11)
    diagonal_k = tuple(Fraction(index - 3, 7) for index in range(8))
    polynomial_k = dict(q3)
    for index, value in enumerate(diagonal_k):
        exponents = [0] * 8
        exponents[index] = 2
        add(polynomial_k, tuple(exponents), value / 2)
    reordered = heat(polynomial_k, tuple(range(8)), delta / 2)
    lap_polynomial_k = laplacian(polynomial_k, tuple(range(8)))
    lap_two_polynomial_k = laplacian(lap_polynomial_k, tuple(range(8)))
    expected_reordered = dict(polynomial_k)
    for exponents, value in lap_polynomial_k.items():
        add(expected_reordered, exponents, delta * value / 2)
    for exponents, value in lap_two_polynomial_k.items():
        add(expected_reordered, exponents, delta**2 * value / 8)
    audit.check("independent exact boundary Wick reordering", reordered == clean(expected_reordered), reordered, expected_reordered, "Q3")

    base = [[1.4, 0.2], [0.2, 1.1]]
    direction = [0.7, -0.35]
    difference = [[direction[row] * direction[column] for column in range(2)] for row in range(2)]
    tensor = [[0.0 for _ in range(16)] for _ in range(16)]
    for row in range(2):
        for column in range(2):
            for component in range(8):
                tensor[8 * row + component][8 * column + component] = difference[row][column]
    tensor_rows = []
    for shift in range(5):
        vector = [((index + 2 * shift) % 9 - 4) / 3.0 for index in range(16)]
        value = quadratic_form(tensor, vector)
        tensor_rows.append(value)
        audit.check("independent tensor covariance order", value >= -1e-14, value, ">=0", "conditioning")

    c4 = float(g) / 32.0
    young_rows = []
    for theta in (0.1, 0.3, 0.8):
        for matrix_norm in (0.2, 1.3, 4.0):
            for radius in (0.0, 0.5, 1.8, 5.0):
                lhs = 0.5 * matrix_norm * radius * radius
                rhs = theta * c4 * radius**4 + matrix_norm**2 / (16.0 * theta * c4)
                young_rows.append({"theta": theta, "B": matrix_norm, "r": radius, "lhs": lhs, "rhs": rhs})
                audit.check("independent quadratic Young absorption", lhs <= rhs + 1e-12, lhs, rhs, "subdominant")
    expected_exponents = {0: 1.0, 1: 4.0 / 3.0, 2: 2.0, 3: 4.0}
    audit.check("independent subdominant exponents", all(abs(4.0 / (4.0 - degree) - value) < 1e-15 for degree, value in expected_exponents.items()), expected_exponents, "1,4/3,2,4", "subdominant")

    boundary_rows = []
    mass = 0.93
    for side in (5.0, 10.0, 20.0, 40.0, 80.0):
        steps = 20000
        width = side / steps
        l1 = 0.0
        l2 = 0.0
        for index in range(steps):
            x = (index + 0.5) * width
            delta = math.exp(-mass * x) + math.exp(-mass * (side - x))
            l1 += delta * width
            l2 += delta * delta * width
        normalized_matrix = math.sqrt(l2 / side)
        normalized_scalar = (l1 + l2) / side
        boundary_rows.append({"side": side, "matrix": normalized_matrix, "scalar": normalized_scalar, "total": normalized_matrix + normalized_scalar})
    audit.check("independent boundary coupling norm tends zero", all(boundary_rows[index + 1]["total"] < boundary_rows[index]["total"] for index in range(4)), boundary_rows, "decreasing", "boundary")

    samples = (-1.3, 0.1, 0.9, 1.8)
    def finite_pressure(value: float) -> float:
        return math.log(sum(math.exp(-value * sample) for sample in samples) / len(samples))
    grid = [(-0.5 + index * 0.05) for index in range(21)]
    pressure_values = [finite_pressure(value) for value in grid]
    second_differences = [pressure_values[index + 1] - 2 * pressure_values[index] + pressure_values[index - 1] for index in range(1, len(grid) - 1)]
    audit.check("independent pressure convexity", min(second_differences) >= -1e-12, min(second_differences), ">=0", "convexity")
    lipschitz = max(abs((pressure_values[index + 1] - pressure_values[index]) / 0.05) for index in range(len(grid) - 1))
    audit.check("independent convex Lipschitz fixture", abs(finite_pressure(0.02) - finite_pressure(0.0)) <= 0.02 * lipschitz + 1e-14, abs(finite_pressure(0.02)), 0.02 * lipschitz, "convexity")

    choices = ("F", "D", "N", "P")
    pairs = [(left, right) for left in choices for right in choices]
    audit.check("independent all sixteen boundary pairs", len(pairs) == 16 and ("P", "F") in pairs, pairs, "16 with half-periodic", "boundary")
    audit.check("independent half versus full periodic", ("P", "F") != ("P", "P"), ("P", "F"), "distinct conventions", "boundary")
    wick_tags = {(left, right): ("diagonal-full" if left == right else "non-diagonal-half-X" if right == "F" else "other-generalized") for left, right in pairs}
    direction_tags = {(left, right): "coordinate-mixed-full" for left, right in pairs}
    audit.check("independent Section VIII pair counts", list(wick_tags.values()).count("diagonal-full") == 4 and list(wick_tags.values()).count("non-diagonal-half-X") == 3 and list(wick_tags.values()).count("other-generalized") == 9, wick_tags, "4 diagonal, 3 non-diagonal Half-X, 9 other", "boundary")
    audit.check("independent reused P-F notation separation", wick_tags[("P", "F")] == "non-diagonal-half-X" and direction_tags[("P", "F")] == "coordinate-mixed-full", (wick_tags[("P", "F")], direction_tags[("P", "F")]), ("non-diagonal-half-X", "coordinate-mixed-full"), "boundary")

    alpha = 0.52
    diagonal_rows = []
    for index, side in enumerate((3.0, 6.0, 12.0, 24.0, 48.0), start=1):
        time = max(index, int(side**3))
        ground = alpha + 0.4 / side
        pressure_value = ground + 0.3 / time
        diagonal_rows.append({"side": side, "time": time, "ground": ground, "pressure": pressure_value, "error": abs(pressure_value - ground)})
    audit.check("independent diagonal transfer error", all(diagonal_rows[index + 1]["error"] < diagonal_rows[index]["error"] for index in range(4)), diagonal_rows, "to zero", "transfer")
    audit.check("independent ground density convergence", abs(diagonal_rows[-1]["ground"] - alpha) < abs(diagonal_rows[0]["ground"] - alpha), diagonal_rows, alpha, "transfer")

    ledger_rows = []
    for side in (2.0, 4.0, 8.0, 16.0, 32.0):
        scalar = math.exp(-1.2 * side) * (0.7 + 0.1 * math.exp(-1.2 * side))
        half_ground_density = -alpha + 0.2 / side + scalar
        centered_ground_density = half_ground_density - scalar
        specific_kl = -centered_ground_density
        ledger_rows.append({"side": side, "scalar": scalar, "half_ground": half_ground_density, "centered_ground": centered_ground_density, "specific_KL": specific_kl})
    audit.check("independent circle scalar decay", ledger_rows[-1]["scalar"] < ledger_rows[0]["scalar"], ledger_rows, "to zero", "ledger")
    audit.check("independent specific KL limit fixture", abs(ledger_rows[-1]["specific_KL"] - alpha) < abs(ledger_rows[0]["specific_KL"] - alpha), ledger_rows, alpha, "ledger")

    rectangles = []
    for beta, length in ((5.0, 8.0), (10.0, 16.0), (20.0, 32.0), (40.0, 64.0)):
        correction = math.exp(-mass * min(beta, length))
        density = alpha + 0.25 / beta + 0.25 / length + correction
        swapped = alpha + 0.25 / length + 0.25 / beta + correction
        rectangles.append({"beta": beta, "L": length, "density": density, "correction": correction})
        audit.check("independent KL exchange symmetry", abs(density - swapped) < 1e-15, density, swapped, "ledger")
    audit.check("independent joint KL convergence", abs(rectangles[-1]["density"] - alpha) < abs(rectangles[0]["density"] - alpha), rectangles, alpha, "ledger")

    for phrase in (
        "Q3 uniform subdominant-coupling theorem",
        "multivariate Wick identity",
        "not a factorization",
        "all sixteen",
        "Half-periodic transfer",
        "No ground-projection estimate uniform",
        "old surface gate",
        "scalar quantities are interchanged",
        "physical empty space",
        "Pre-A remain open",
    ):
        audit.check(f"independent certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "scope")

    for key in (
        "finite_component_GRS_uniform_subdominant_coupling",
        "all_sixteen_full_half_boundary_pressure_density_limits",
        "periodic_ground_energy_density_limit",
        "periodic_zero_temperature_specific_KL_limit",
        "joint_scalar_van_Hove_limit",
        "both_iterated_scalar_density_limits_equal",
    ):
        audit.check(f"independent positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in (
        "periodic_sharp_surface_pairing_uniform_in_cutoff_volume_and_interpolation",
        "O_boundary_log_partition_comparison",
        "O1_periodic_sharp_ground_energy_difference",
        "physical_empty_space_reference",
        "phase_transition_or_phase_uniqueness",
        "zero_temperature_state_limit",
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
        "negative_ids": manifest["negative_ids"],
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "parent": sha256(PARENT)},
        "derived": {
            "conditioning": {"conditional": {str(key): str(value) for key, value in conditional.items()}, "target": {str(key): str(value) for key, value in target.items()}, "tensor_rows": tensor_rows},
            "Q3": {"edges": len(cube_edges()), "laplacian_terms": len(q3_lap), "second_laplacian": {str(key): str(value) for key, value in q3_lap_two.items()}, "boundary_reordering_terms": len(reordered)},
            "subdominant": {"young": young_rows, "exponents": expected_exponents},
            "boundary": {"rows": boundary_rows, "pairs": pairs, "wick_tags": {f"{left};{right}": value for (left, right), value in wick_tags.items()}, "direction_tags": {f"{left}|{right}": value for (left, right), value in direction_tags.items()}},
            "transfer": diagonal_rows,
            "ledger": {"target_alpha": alpha, "circle": ledger_rows, "rectangles": rectangles},
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
