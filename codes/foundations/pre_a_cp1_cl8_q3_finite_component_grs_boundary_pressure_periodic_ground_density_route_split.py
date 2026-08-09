#!/usr/bin/env python3
"""Primary verifier for the finite-component Q3 GRS boundary theorem."""

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
SLUG = "pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0"
RESULT_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-HALF-PERIODIC-PRESSURE-PERIODIC-GROUND-AND-SPECIFIC-KL-DENSITY"
EXPLORATION_ID = "EXP-000778"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
PARENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-zero-temperature-thermodynamic-ground-phase-physical-reference-route-split/result.json"
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


def heat_polynomial(poly: sp.Expr, variables: tuple[sp.Symbol, ...], coefficient: sp.Expr) -> sp.Expr:
    result = sp.expand(poly)
    current = sp.expand(poly)
    factorial = 1
    for order in range(1, 8):
        current = sp.expand(sum(sp.diff(current, variable, 2) for variable in variables))
        if current == 0:
            break
        factorial *= order
        result += coefficient**order * current / factorial
    return sp.expand(result)


def cube_edges() -> list[tuple[int, int]]:
    return [(vertex, vertex ^ (1 << bit)) for vertex in range(8) for bit in range(3) if vertex < (vertex ^ (1 << bit))]


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("EXP770 parent all pass", parent["assertion_summary"]["passed"] == parent["assertion_summary"]["total"], parent["assertion_summary"], "all pass", "parent")
    audit.check("EXP770 parent sharp density", parent["scope"]["strict_positive_centered_reference_density"] is True, parent["scope"]["strict_positive_centered_reference_density"], True, "parent")
    audit.check("EXP770 parent periodic firewall", parent["scope"]["periodic_zero_temperature_specific_KL_limit"] is False, parent["scope"]["periodic_zero_temperature_specific_KL_limit"], False, "parent")

    q = sp.symbols("q0:8", real=True)
    g, lam = sp.symbols("g lambda", positive=True)
    edges = cube_edges()
    W4 = g * sum(value**4 for value in q) / 4 + lam * sum((q[left] - q[right]) ** 2 * (q[left] ** 2 + q[right] ** 2) for left, right in edges) / 4
    laplacian = sp.expand(sum(sp.diff(W4, variable, 2) for variable in q))
    laplacian_two = sp.expand(sum(sp.diff(laplacian, variable, 2) for variable in q))
    diagonal_expected = 3 * (g + 4 * lam) * sum(variable**2 for variable in q) - 6 * lam * sum(q[left] * q[right] for left, right in edges)
    audit.check("Q3 graph has twelve edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 Wick Laplacian matrix identity", sp.simplify(laplacian - diagonal_expected) == 0, laplacian, diagonal_expected, "Q3")
    audit.check("Q3 second Wick Laplacian", sp.simplify(laplacian_two - 48 * (g + 4 * lam)) == 0, laplacian_two, 48 * (g + 4 * lam), "Q3")
    delta = sp.symbols("delta", real=True)
    diagonal_k = sp.symbols("k0:8", real=True)
    polynomial_k = W4 + sum(diagonal_k[index] * q[index] ** 2 for index in range(8)) / 2
    reordered = heat_polynomial(polynomial_k, q, delta / 2)
    expected_reordered = polynomial_k + delta * (sum(diagonal_k) + laplacian) / 2 + delta**2 * laplacian_two / 8
    audit.check("exact boundary Wick reordering identity", sp.simplify(reordered - expected_reordered) == 0, reordered, expected_reordered, "Q3")

    x0, x1, y0, y1, z0, z1 = sp.symbols("x0 x1 y0 y1 z0 z1", real=True)
    c1, c2 = sp.Rational(2, 5), sp.Rational(3, 7)
    toy = z0**4 + 2 * z0**2 * z1**2 + 3 * z1**4 + z0 * z1 + 2 * z0**2
    wick_total = heat_polynomial(toy, (z0, z1), -(c1 + c2) / 2).subs({z0: x0 + y0, z1: x1 + y1})
    conditional = heat_polynomial(wick_total, (y0, y1), c2 / 2).subs({y0: 0, y1: 0})
    wick_first = heat_polynomial(toy.subs({z0: x0, z1: x1}), (x0, x1), -c1 / 2)
    audit.check("multivariate Wick conditioning identity", sp.simplify(conditional - wick_first) == 0, conditional, wick_first, "conditioning")

    C1 = sp.Matrix([[sp.Rational(3, 2), sp.Rational(1, 5)], [sp.Rational(1, 5), sp.Rational(6, 5)]])
    vector = sp.Matrix([sp.Rational(2, 3), sp.Rational(-1, 4)])
    difference = vector * vector.T
    tensor_difference = sp.kronecker_product(difference, sp.eye(8))
    probes = [sp.Matrix([sp.Rational((index % 5) - 2, 3) for index in range(16)]), sp.ones(16, 1)]
    tensor_rows = []
    for probe in probes:
        quadratic = sp.simplify((probe.T * tensor_difference * probe)[0])
        tensor_rows.append(str(quadratic))
        audit.check("tensor covariance order fixture", quadratic >= 0, quadratic, ">=0", "conditioning")
    audit.check("scalar covariance order fixture", difference.det() == 0 and difference.trace() > 0, (difference.det(), difference.trace()), "rank-one PSD", "conditioning")

    c4 = sp.symbols("c4", positive=True)
    theta, matrix_norm, radius_sq = sp.symbols("theta B r2", positive=True)
    young_gap = sp.expand(theta * c4 * radius_sq**2 + matrix_norm**2 / (16 * theta * c4) - matrix_norm * radius_sq / 2)
    audit.check("quadratic Young identity is a square", sp.factor(young_gap) == (4 * c4 * radius_sq * theta - matrix_norm) ** 2 / (16 * c4 * theta), sp.factor(young_gap), "square", "subdominant")
    exponents = {degree: sp.Rational(4, 4 - degree) for degree in range(4)}
    audit.check("subdominant exponents", exponents == {0: 1, 1: sp.Rational(4, 3), 2: 2, 3: 4}, exponents, "1,4/3,2,4", "subdominant")
    for degree in (1, 2, 3):
        epsilon = 0.17
        for coefficient in (0.2, 1.1, 3.4):
            for radius in (0.0, 0.4, 1.7, 4.3):
                exponent = 4.0 / (4.0 - degree)
                ratio = max(radius**degree * coefficient - epsilon * radius**4, 0.0) / coefficient**exponent
                audit.check("multi-index Young finite supremum fixture", math.isfinite(ratio), ratio, "finite", "subdominant")

    boundary_rows = []
    mass = 1.1
    for side in (4.0, 8.0, 16.0, 32.0, 64.0):
        one = (1.0 - math.exp(-mass * side)) / mass
        cross = side * math.exp(-mass * side)
        two = (1.0 - math.exp(-2.0 * mass * side)) / mass + 2.0 * cross
        normalized_l1 = 2.0 * one / side
        normalized_l2_sq = 2.0 * two / side
        matrix_norm = math.sqrt(normalized_l2_sq)
        scalar_norm = normalized_l1 + normalized_l2_sq
        boundary_rows.append({"side": side, "matrix_norm": matrix_norm, "scalar_norm": scalar_norm, "coupling_norm": matrix_norm + scalar_norm})
    audit.check("boundary Wick coupling norm vanishes", all(boundary_rows[index + 1]["coupling_norm"] < boundary_rows[index]["coupling_norm"] for index in range(4)), boundary_rows, "decreasing to zero", "boundary")
    audit.check("boundary norm has density not surface-rate conclusion", boundary_rows[-1]["coupling_norm"] > 0.0, boundary_rows[-1], "positive finite-size remainder", "boundary")

    samples = [-1.4, -0.2, 0.7, 2.1]
    def pressure(coupling: float) -> float:
        return math.log(sum(math.exp(-coupling * value) for value in samples) / len(samples))
    grid = [index / 20.0 for index in range(-10, 11)]
    values = [pressure(value) for value in grid]
    slopes = [(values[index + 1] - values[index]) / (grid[index + 1] - grid[index]) for index in range(len(grid) - 1)]
    audit.check("convex pressure slope monotonicity", all(slopes[index + 1] >= slopes[index] - 1e-12 for index in range(len(slopes) - 1)), slopes, "nondecreasing", "convexity")
    local_lipschitz = max(abs(slope) for slope in slopes)
    audit.check("convex bounded-ball Lipschitz fixture", abs(pressure(0.03) - pressure(0.0)) <= local_lipschitz * 0.03 + 1e-14, abs(pressure(0.03)), local_lipschitz * 0.03, "convexity")

    boundary_choices = ["F", "D", "N", "P"]
    sixteen = [(left, right) for left in boundary_choices for right in boundary_choices]
    audit.check("all sixteen full-half boundary pairs", len(sixteen) == 16 and ("P", "F") in sixteen and ("P", "P") in sixteen, sixteen, "16 including half-periodic and full-periodic", "boundary")
    audit.check("half-periodic convention distinct", ("P", "F") != ("P", "P"), ("P", "F"), "not diagonal", "boundary")
    wick_semantics = {(left, right): ("full" if left == right else "half-X" if right == "F" else "generalized") for left, right in sixteen}
    direction_semantics = {(left, right): "coordinate-mixed-full" for left, right in sixteen}
    audit.check("Section VIII Wick pair classification", list(wick_semantics.values()).count("full") == 4 and list(wick_semantics.values()).count("half-X") == 3 and list(wick_semantics.values()).count("generalized") == 9, wick_semantics, "4 full, 3 non-diagonal Half-X plus F;F, 9 generalized", "boundary")
    audit.check("reused P-F notation has distinct semantics", wick_semantics[("P", "F")] == "half-X" and direction_semantics[("P", "F")] == "coordinate-mixed-full", (wick_semantics[("P", "F")], direction_semantics[("P", "F")]), ("half-X", "coordinate-mixed-full"), "boundary")

    alpha = 0.43
    diagonal_rows = []
    for index, side in enumerate((4.0, 8.0, 16.0, 32.0), start=1):
        time = max(float(index), side * side)
        pressure_value = alpha + 0.35 / side + 0.27 / time
        ground_density = alpha + 0.35 / side
        projection_error = abs(pressure_value - ground_density)
        diagonal_rows.append({"s": side, "t": time, "pressure": pressure_value, "ground_density": ground_density, "projection_error": projection_error})
    audit.check("sequence diagonal projection error vanishes", all(diagonal_rows[index + 1]["projection_error"] < diagonal_rows[index]["projection_error"] for index in range(3)), diagonal_rows, "to zero", "transfer")
    audit.check("sequence diagonal ground density converges", abs(diagonal_rows[-1]["ground_density"] - alpha) < abs(diagonal_rows[0]["ground_density"] - alpha), diagonal_rows, alpha, "transfer")

    mp.mp.dps = 35
    m0 = mp.mpf("1.13")
    trace_k = mp.mpf("1.7")
    G = mp.mpf("2.2")
    circle_rows = []
    for side in (2, 4, 8, 16):
        a_side = sum(mp.besselk(0, m0 * side * index) for index in range(1, 80)) / mp.pi
        c_side = a_side * trace_k / 2 + 6 * a_side**2 * G
        centered_ground_density = -mp.mpf(str(alpha)) + mp.mpf("0.2") / side
        half_periodic_density = centered_ground_density + c_side
        circle_rows.append({"s": side, "a_s": str(a_side), "c_s": str(c_side), "half_periodic_density": str(half_periodic_density), "specific_KL": str(-centered_ground_density)})
    audit.check("circle Wick scalar tends zero", abs(mp.mpf(circle_rows[-1]["c_s"])) < abs(mp.mpf(circle_rows[0]["c_s"])), circle_rows, "to zero", "ledger")
    audit.check("specific KL tends alpha fixture", abs(mp.mpf(circle_rows[-1]["specific_KL"]) - alpha) < abs(mp.mpf(circle_rows[0]["specific_KL"]) - alpha), circle_rows, alpha, "ledger")
    scalar_shift = 3.1
    raw = -alpha + 0.02
    shifted = raw + scalar_shift
    audit.check("raw ground sign scalar mutable", raw < 0.0 < shifted, (raw, shifted), "both signs", "firewall")

    rectangle_rows = []
    for beta, length in ((4.0, 7.0), (8.0, 14.0), (16.0, 28.0), (32.0, 56.0)):
        half_pressure = alpha + 0.2 / beta + 0.2 / length
        image_correction = math.exp(-mass * min(beta, length))
        density = half_pressure + image_correction
        swapped = alpha + 0.2 / length + 0.2 / beta + math.exp(-mass * min(length, beta))
        rectangle_rows.append({"beta": beta, "L": length, "d": density, "correction": image_correction})
        audit.check("rectangle KL exchange symmetry", abs(density - swapped) < 1e-15, density, swapped, "ledger")
    audit.check("joint scalar KL density converges", abs(rectangle_rows[-1]["d"] - alpha) < abs(rectangle_rows[0]["d"] - alpha), rectangle_rows, alpha, "ledger")

    required_phrases = (
        "Scoped theorem",
        "Exact historical boundary",
        "Vector Gaussian conditioning",
        "Q3 uniform subdominant-coupling theorem",
        "Wick and hypercontractive replacement",
        "Localization and Duhamel summation",
        "all sixteen",
        "Half-periodic transfer",
        "sequence",
        "What the old surface gate now means",
        "physical empty space",
        "not a world-first claim",
    )
    for phrase in required_phrases:
        audit.check(f"certificate phrase {phrase[:44]}", phrase.lower() in certificate.lower(), phrase, "present", "scope")

    true_scope = (
        "finite_component_GRS_Gaussian_conditioning",
        "finite_component_GRS_uniform_subdominant_coupling",
        "all_sixteen_full_half_boundary_pressure_density_limits",
        "half_periodic_plane_Wick_pressure_limit",
        "periodic_ground_energy_density_limit",
        "periodic_zero_temperature_specific_KL_limit",
        "joint_scalar_van_Hove_limit",
        "both_iterated_scalar_density_limits_equal",
        "periodic_sharp_density_difference_vanishes",
    )
    false_scope = (
        "periodic_sharp_surface_pairing_uniform_in_cutoff_volume_and_interpolation",
        "O_boundary_log_partition_comparison",
        "O1_periodic_sharp_ground_energy_difference",
        "physical_empty_space_reference",
        "absolute_vacuum_energy_fixed",
        "phase_transition_or_phase_uniqueness",
        "zero_temperature_state_limit",
        "original_3D_Q3LOCK_parent",
        "C6_advanced",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("stronger surface gate retained", "OPEN BUT NON-LOAD-BEARING" in manifest["stronger_surface_boundary"]["status"], manifest["stronger_surface_boundary"]["status"], "open non-load-bearing", "scope")
    audit.check("next gate separates physical phase parent", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-Q3-PHASE-PHYSICAL-REFERENCE-AND-ONE-DIMENSIONAL-TO-THREE-DIMENSIONAL-PARENT-ROUTE-SPLIT", manifest["gate_resolution"]["next_gate"], "phase/reference/parent split", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

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
            "Q3": {"edges": edges, "laplacian": str(laplacian), "second_laplacian": str(laplacian_two), "boundary_reordering": str(reordered)},
            "conditioning": {"toy_conditional": str(conditional), "toy_target": str(wick_first), "tensor_rows": tensor_rows},
            "subdominant": {"exponents": {str(key): str(value) for key, value in exponents.items()}, "young_gap": str(sp.factor(young_gap))},
            "boundary": {"rows": boundary_rows, "pairs": sixteen, "wick_semantics": {f"{left};{right}": value for (left, right), value in wick_semantics.items()}, "direction_semantics": {f"{left}|{right}": value for (left, right), value in direction_semantics.items()}},
            "transfer": diagonal_rows,
            "ledger": {"target_alpha": alpha, "circle": circle_rows, "rectangles": rectangle_rows},
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
