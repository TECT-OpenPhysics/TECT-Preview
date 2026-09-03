#!/usr/bin/env python3
"""Independent stdlib audit for the interacting regulator state route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-interacting-regulator-compatible-state-route-split"
CANDIDATE_ID = "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-STATE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-LOW-MODE-GROUND-ENTANGLEMENT-ALL-BETA-PROJECTIVITY-AND-Q3-WICK-COUNTERTERM-OBSTRUCTIONS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split-manifest.json",
)
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-independent-{SLUG}/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


Poly = dict[tuple[int, ...], Fraction]


def poly_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        if result[exponent] == 0:
            del result[exponent]
    return result


def poly_scale(poly: Poly, scale: Fraction) -> Poly:
    return {exponent: coefficient * scale for exponent, coefficient in poly.items() if coefficient * scale}


def poly_multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for exp_left, coefficient_left in left.items():
        for exp_right, coefficient_right in right.items():
            exponent = tuple(a + b for a, b in zip(exp_left, exp_right))
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient_left * coefficient_right
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def poly_power(poly: Poly, power: int) -> Poly:
    variables = len(next(iter(poly)))
    result: Poly = {(0,) * variables: Fraction(1)}
    for _ in range(power):
        result = poly_multiply(result, poly)
    return result


def laplacian(poly: Poly) -> Poly:
    result: Poly = {}
    for exponent, coefficient in poly.items():
        for axis, degree in enumerate(exponent):
            if degree >= 2:
                reduced = list(exponent)
                reduced[axis] -= 2
                key = tuple(reduced)
                result[key] = result.get(key, Fraction(0)) + coefficient * degree * (degree - 1)
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def wick(poly: Poly, covariance: Fraction) -> Poly:
    result = dict(poly)
    current = dict(poly)
    factorial = 1
    for order in range(1, 3):
        current = laplacian(current)
        factorial *= order
        result = poly_add(result, poly_scale(current, (-covariance / 2) ** order / factorial))
    return result


def cube_data() -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[list[int]]]:
    nodes = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    index = {node: i for i, node in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    matrix = [[0 for _ in nodes] for _ in nodes]
    for node in nodes:
        i = index[node]
        for axis in range(3):
            neighbor = list(node)
            neighbor[axis] ^= 1
            j = index[tuple(neighbor)]
            if i < j:
                edges.append((i, j))
            matrix[i][i] += 1
            matrix[i][j] -= 1
    return nodes, edges, matrix


def matvec(matrix: list[list[Fraction | int]], vector: list[int]) -> list[Fraction]:
    return [sum(Fraction(matrix[i][j]) * vector[j] for j in range(len(vector))) for i in range(len(matrix))]


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("parent ids", tuple(parent["candidate_id"] for parent in parents) == tuple(manifest["parent_ids"]), [parent["candidate_id"] for parent in parents], manifest["parent_ids"], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    field_scale_squared = Fraction(2)
    momentum_scale_squared = Fraction(1, 2)
    audit.check("independent Nyquist reciprocal squeeze", field_scale_squared * momentum_scale_squared == 1, field_scale_squared * momentum_scale_squared, 1, "typing")
    audit.check("independent Nyquist squeeze recorded", "sqrt(2)*Phi" in manifest["natural_low_mode_split"]["coarse_identification"] and "Pi_N,M/2/sqrt(2)" in manifest["natural_low_mode_split"]["coarse_identification"], manifest["natural_low_mode_split"]["coarse_identification"], "reciprocal squeeze", "typing")

    # Direct exact Fraction reconstruction of the admitted M=4 -> N=8 collective plane.
    variables = 2
    X = {(1, 0): Fraction(1)}
    Y = {(0, 1): Fraction(1)}
    total: Poly = {}
    N = 8
    L = Fraction(4)
    b = Fraction(1, 2)
    r = Fraction(-1)
    c = Fraction(1)
    g = Fraction(1)
    sqrt_L = Fraction(2)
    q_rows: list[Poly] = []
    for j in range(N):
        sign = 1 if j % 2 == 0 else -1
        q_rows.append(poly_scale(poly_add(X, poly_scale(Y, Fraction(sign))), 1 / sqrt_L))
    for j in range(N):
        qj = q_rows[j]
        qnext = q_rows[(j + 1) % N]
        onsite = poly_add(poly_scale(poly_power(qj, 2), r / 2), poly_scale(poly_power(qj, 4), g / 4))
        difference = poly_add(qnext, poly_scale(qj, -1))
        gradient = poly_scale(poly_power(difference, 2), c / (2 * b * b))
        for _species in range(8):
            total = poly_add(total, poly_scale(poly_add(onsite, gradient), b / 8))
    expected_fixture: Poly = {
        (2, 0): Fraction(-1, 2),
        (0, 2): Fraction(15, 2),
        (4, 0): Fraction(1, 16),
        (0, 4): Fraction(1, 16),
        (2, 2): Fraction(3, 8),
    }
    audit.check("independent collective plane fixture", total == expected_fixture, total, expected_fixture, "entanglement")
    mixed_fixture = total[(2, 2)] * 4
    audit.check("independent mixed derivative", mixed_fixture == Fraction(3, 2), mixed_fixture, Fraction(3, 2), "entanglement")
    dot_uniform_nyquist = sum(Fraction(1, 2) * Fraction(1 if j % 2 == 0 else -1, 2) for j in range(N))
    audit.check("uniform and Nyquist orthogonal", dot_uniform_nyquist == 0, dot_uniform_nyquist, 0, "entanglement")
    species_rows = [[dict(q_rows[j]) for _species in range(8)] for j in range(N)]
    _, q3_edges_for_lock, _ = cube_data()
    lock_differences = [poly_add(species_rows[j][left], poly_scale(species_rows[j][right], -1)) for j in range(N) for left, right in q3_edges_for_lock]
    audit.check("collective Q3 lock zero", all(not difference for difference in lock_differences), lock_differences, "all zero", "entanglement")

    # Independent purity fixture.
    reduced_entangled = [[Fraction(1, 2), Fraction(0)], [Fraction(0), Fraction(1, 2)]]
    purity_entangled = sum(reduced_entangled[i][j] * reduced_entangled[j][i] for i in range(2) for j in range(2))
    reduced_product = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    purity_product = sum(reduced_product[i][j] * reduced_product[j][i] for i in range(2) for j in range(2))
    audit.check("independent entangled marginal mixed", purity_entangled == Fraction(1, 2), purity_entangled, Fraction(1, 2), "purity")
    audit.check("independent product marginal pure", purity_product == 1, purity_product, 1, "purity")
    audit.check("independent ground no-go conclusion", "restriction is mixed" in manifest["ground_projectivity_no_go"]["conclusion"], manifest["ground_projectivity_no_go"]["conclusion"], "contains mixed", "purity")
    audit.check("independent Gibbs tail scope", "every beta>0" in manifest["all_beta_Gibbs_consequence"]["target"], manifest["all_beta_Gibbs_consequence"]["target"], "contains every beta", "Gibbs")
    audit.check("independent explicit Gibbs tail", "epsilon_s<=eta/4" in manifest["all_beta_Gibbs_consequence"]["explicit_tail"], manifest["all_beta_Gibbs_consequence"]["explicit_tail"], "explicit epsilon tail", "Gibbs")
    audit.check("independent mean-force state", "exactly Gibbs" in manifest["normal_pullback_and_mean_force"]["mean_force"], manifest["normal_pullback_and_mean_force"]["mean_force"], "contains exactly Gibbs", "Gibbs")
    audit.check("independent mean-force faithfulness", "faithful" in manifest["normal_pullback_and_mean_force"]["fine_Gibbs"], manifest["normal_pullback_and_mean_force"]["fine_Gibbs"], "faithfulness", "Gibbs")
    audit.check("independent cut-square condition", "if an inter-regulator" in manifest["history_cut_consequence"]["conditional_square"], manifest["history_cut_consequence"]["conditional_square"], "conditional square", "history")

    # Derive the edge Wick polynomial by monomial algebra.
    a_poly = {(1, 0): Fraction(1)}
    b_poly = {(0, 1): Fraction(1)}
    difference = poly_add(a_poly, poly_scale(b_poly, -1))
    square_sum = poly_add(poly_power(a_poly, 2), poly_power(b_poly, 2))
    edge = poly_multiply(poly_power(difference, 2), square_sum)
    wick_edge = wick(edge, Fraction(1))
    edge_contraction = poly_add(wick_edge, poly_scale(edge, -1))
    expected_edge_contraction = {
        (2, 0): Fraction(-8),
        (1, 1): Fraction(12),
        (0, 2): Fraction(-8),
        (0, 0): Fraction(8),
    }
    audit.check("independent edge Wick contraction", edge_contraction == expected_edge_contraction, edge_contraction, expected_edge_contraction, "Wick")
    onsite = poly_power(a_poly, 4)
    onsite_contraction = poly_add(wick(onsite, Fraction(1)), poly_scale(onsite, -1))
    audit.check("independent onsite Wick contraction", onsite_contraction == {(2, 0): Fraction(-6), (0, 0): Fraction(3)}, onsite_contraction, {(2, 0): Fraction(-6), (0, 0): Fraction(3)}, "Wick")
    edge_a2_factor = edge_contraction.get((2, 0), Fraction(0))
    edge_ab_factor = edge_contraction.get((1, 1), Fraction(0))
    edge_b2_factor = edge_contraction.get((0, 2), Fraction(0))
    edge_constant_factor = edge_contraction.get((0, 0), Fraction(0))
    onsite_q2_factor = onsite_contraction.get((2, 0), Fraction(0))
    onsite_constant_factor = onsite_contraction.get((0, 0), Fraction(0))

    nodes, edges, laplacian = cube_data()
    spectrum: Counter[int] = Counter()
    for alpha in nodes:
        level = sum(alpha)
        vector = [(-1) ** sum(a * e for a, e in zip(alpha, node)) for node in nodes]
        actual = matvec(laplacian, vector)
        expected = [Fraction(2 * level * value) for value in vector]
        audit.check(f"independent Q3 Walsh vector {alpha}", actual == expected, actual, expected, "Q3")
        spectrum[2 * level] += 1
    audit.check("independent Q3 spectrum", spectrum == Counter({0: 1, 2: 3, 4: 3, 6: 1}), dict(spectrum), {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")

    # Assemble deltaK for the g=5, lambda=2, C=3 fixture from the independently
    # derived edge and onsite contractions.
    g_fixture = Fraction(5)
    lambda_fixture = Fraction(2)
    covariance_fixture = Fraction(3)
    delta_matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for vertex in range(8):
        delta_matrix[vertex][vertex] += g_fixture * onsite_q2_factor * covariance_fixture / 2
    for left, right in edges:
        # Quadratic energy coefficients are lambda/4 times the edge contraction;
        # the Hessian doubles diagonal coefficients and leaves the mixed
        # derivative coefficient unchanged.
        diagonal_hessian = 2 * (lambda_fixture / 4) * edge_a2_factor * covariance_fixture
        cross_hessian = (lambda_fixture / 4) * edge_ab_factor * covariance_fixture
        delta_matrix[left][left] += diagonal_hessian
        delta_matrix[right][right] += diagonal_hessian
        delta_matrix[left][right] += cross_hessian
        delta_matrix[right][left] += cross_hessian
    shift_fixture: list[Fraction] = []
    for level in range(4):
        alpha = (1,) * level + (0,) * (3 - level)
        vector = [(-1) ** sum(a * e for a, e in zip(alpha, node)) for node in nodes]
        action = matvec(delta_matrix, vector)
        nonzero_index = next(i for i, value in enumerate(vector) if value)
        shift = action[nonzero_index] / vector[nonzero_index]
        audit.check(f"independent Wick shift level {level}", action == [shift * value for value in vector], action, "eigenvector", "Wick")
        shift_fixture.append(shift)
    audit.check("independent Wick shift fixture", shift_fixture == [-63, -99, -135, -171], shift_fixture, [-63, -99, -135, -171], "Wick")
    onsite_constant = 8 * (g_fixture / 4) * onsite_constant_factor * covariance_fixture**2
    edge_constant = len(edges) * (lambda_fixture / 4) * edge_constant_factor * covariance_fixture**2
    total_constant = onsite_constant + edge_constant
    audit.check("independent Wick scalar fixture", total_constant == 702, total_constant, 702, "Wick")
    audit.check("independent scalar-only obstruction", shift_fixture[1] != shift_fixture[0], shift_fixture[:2], "distinct Walsh shifts", "Wick")

    covariance_values: list[float] = []
    covariance_over_log: list[float] = []
    for size in (16, 32, 64, 128, 256, 512):
        length = 2.0 * math.pi
        spacing = length / size
        symbols = []
        total_covariance = 0.0
        for mode in range(-size // 2, size // 2):
            wave = float(mode)
            symbol = 2.0 * math.sin(wave * spacing / 2.0) / spacing
            if mode:
                symbols.append((abs(symbol), abs(wave)))
            total_covariance += 1.0 / math.sqrt(1.0 + symbol * symbol)
        audit.check(f"independent symbol upper N{size}", all(symbol <= wave + 1e-12 for symbol, wave in symbols), max(symbol - wave for symbol, wave in symbols), "<=0", "covariance")
        audit.check(f"independent symbol lower N{size}", all(symbol + 1e-12 >= 2.0 * wave / math.pi for symbol, wave in symbols), min(symbol - 2.0 * wave / math.pi for symbol, wave in symbols), ">=0", "covariance")
        covariance = total_covariance / (2.0 * length)
        covariance_values.append(covariance)
        covariance_over_log.append(covariance / math.log(size))
    audit.check("independent covariance growth", all(covariance_values[i + 1] > covariance_values[i] for i in range(5)), covariance_values, "strict growth", "covariance")
    audit.check("independent logarithmic window", all(0.12 < value < 0.23 for value in covariance_over_log), covariance_over_log, "bounded positive ratio", "covariance")

    true_scope = (
        "natural_low_mode_tensor_split",
        "fine_interacting_ground_low_high_entangled",
        "common_diagonal_Q3_Wick_counterterm_ledger",
        "reference_covariance_logarithmic_growth",
    )
    false_scope = (
        "natural_exact_ground_projectivity",
        "natural_same_beta_all_temperature_Gibbs_projectivity",
        "natural_ground_anchored_history_cut_projectivity",
        "scalar_mass_only_Q3_Wick_renormalization",
        "Q3_matrix_counterterm_sufficiency",
        "cutoff_uniform_moment_bounds",
        "cutoff_uniform_local_energy_bounds",
        "interacting_state_compactness",
        "typed_inter_regulator_cut_square",
        "interacting_continuum_state",
        "interacting_Hadamard_state",
        "physical_state_or_vacuum",
        "below_empty_space_comparison",
        "physical_phase_transition",
        "physical_light_speed_derived",
        "original_3D_Q3LOCK_parent",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    audit.check("independent next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-Q3-MATRIX-COUNTERTERM-INTERACTING-STATE-COMPACTNESS-AND-CUT-SQUARE", manifest["gate_resolution"]["next_gate"], "matrix-counterterm next gate", "scope")

    derived = {
        "collective_fixture": {"potential_coefficients": total, "mixed_derivative": mixed_fixture},
        "Q3_spectrum": {"eigenvalues": sorted(spectrum), "multiplicities": [spectrum[value] for value in sorted(spectrum)]},
        "Wick_fixture": {
            "edge_quadratic_coefficients": [edge_a2_factor, edge_ab_factor, edge_b2_factor],
            "edge_constant": edge_constant_factor,
            "onsite_quadratic_coefficient": onsite_q2_factor,
            "onsite_constant": onsite_constant_factor,
            "Walsh_shifts": shift_fixture,
            "Q3_constant": total_constant,
        },
        "covariance_values": covariance_values,
        "covariance_over_log": covariance_over_log,
        "negative_ids": list(NEGATIVE_IDS),
    }
    source_hashes = {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST)}
    for path in PARENT_FILES:
        source_hashes[path] = sha256(REPO / path)
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": manifest["parent_ids"],
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "source_sha256": source_hashes,
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
