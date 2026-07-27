#!/usr/bin/env python3
"""Independent executable audit for the R-095 A13 boundary result.

This implementation deliberately does not import the primary verifier.  It
rebuilds conditional expectations by leaf enumeration, uses direct matrix
algebra for the fractional perspective, and checks the Cartan identity by an
independent high-order quadrature path.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-27"
__version_issued__ = "2026-07-27"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.legendre import leggauss


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-FRACTIONAL-FEEDBACK-SQUARE-PERSPECTIVE-DOMINATION-BOUNDARY"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-27-independent-fractional-feedback-square-perspective-boundary/result.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def branch_average(values: list[Fraction], revealed: int, roots: int) -> list[Fraction]:
    """Explicit conditional expectation on lexicographically ordered leaves."""

    width = 2 ** (roots - revealed)
    answer: list[Fraction] = []
    for offset in range(0, len(values), width):
        average = sum(values[offset : offset + width], Fraction(0)) / width
        answer.extend([average] * width)
    return answer


def mean(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def inner(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return mean([a * b for a, b in zip(left, right)])


def normalized_map(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    return (float(z @ symmetric @ z) / (float(z @ z) + floor)) * z


def normalized_jacobian(z: np.ndarray, symmetric: np.ndarray, floor: float) -> np.ndarray:
    rho = float(z @ z) + floor
    q = float(z @ symmetric @ z) / rho
    gradient = 2.0 * (symmetric - q * np.eye(z.size)) @ z / rho
    return q * np.eye(z.size) + np.outer(z, gradient)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append(
            {
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    # Independent finite-tree reconstruction.  No conditional-expectation
    # helper or fixture is shared with the primary program.
    roots = 3
    leaves = 2**roots
    bits = [
        [Fraction(1 if ((leaf >> (roots - 1 - root)) & 1) else -1) for leaf in range(leaves)]
        for root in range(roots)
    ]
    terminal = [bits[0][i] - 2 * bits[1][i] + bits[0][i] * bits[2][i] for i in range(leaves)]
    moving_prefix = {
        1: [2 * bits[0][i] + bits[1][i] * bits[2][i] for i in range(leaves)],
        2: [bits[0][i] - bits[1][i] + bits[0][i] * bits[2][i] for i in range(leaves)],
        3: [terminal[i] + bits[2][i] for i in range(leaves)],
    }
    terminal_deltas: dict[int, list[Fraction]] = {}
    zeta: dict[int, list[Fraction]] = {}
    future: dict[int, list[Fraction]] = {}
    for root in range(1, roots + 1):
        before = branch_average(terminal, root - 1, roots)
        after = branch_average(terminal, root, roots)
        terminal_deltas[root] = [b - a for a, b in zip(before, after)]
        prefix = moving_prefix[root]
        remainder = [terminal[i] - prefix[i] for i in range(leaves)]
        zeta[root] = [
            b - a
            for a, b in zip(
                branch_average(prefix, root - 1, roots),
                branch_average(prefix, root, roots),
            )
        ]
        future[root] = [
            b - a
            for a, b in zip(
                branch_average(remainder, root - 1, roots),
                branch_average(remainder, root, roots),
            )
        ]
        split = max(abs(terminal_deltas[root][i] - zeta[root][i] - future[root][i]) for i in range(leaves))
        check(f"tree_split_{root}", split == 0, split, 0)

    terminal_energy = mean([value * value for value in terminal])
    low = branch_average(terminal, 0, roots)
    martingale_energy = mean([value * value for value in low]) + sum(
        mean([value * value for value in terminal_deltas[root]]) for root in range(1, roots + 1)
    )
    check("tree_pythagoras", terminal_energy == martingale_energy, terminal_energy - martingale_energy, 0)
    tree_defects: dict[str, str] = {}
    for theta in (Fraction(1, 8), Fraction(1, 2), Fraction(3, 4)):
        lhs = theta * terminal_energy / 2 - theta * sum(
            mean([value * value for value in future[root]]) for root in range(1, roots + 1)
        ) / 2
        rhs = theta * mean([value * value for value in low]) / 2
        rhs += theta * sum(mean([value * value for value in zeta[root]]) for root in range(1, roots + 1)) / 2
        rhs += theta * sum(inner(zeta[root], future[root]) for root in range(1, roots + 1))
        tree_defects[str(theta)] = str(lhs)
        check(f"tree_defect_identity_{theta}", lhs == rhs, lhs - rhs, 0)

    xi = [Fraction(-1), Fraction(1)]
    fixture = Fraction(1, 4) * (Fraction(0) - mean([x * x for x in xi]))
    fixture_rhs = Fraction(1, 4) * mean([x * x for x in xi]) + Fraction(1, 2) * inner(xi, [-x for x in xi])
    check("moving_fixture_lhs", fixture == Fraction(-1, 4), fixture, Fraction(-1, 4))
    check("moving_fixture_rhs", fixture_rhs == Fraction(-1, 4), fixture_rhs, Fraction(-1, 4))

    # Exact scalar perspective counterfixture.
    b = Fraction(1)
    allocation = Fraction(1, 2)
    regularizer = Fraction(1, 8)
    a_theta = (1 - allocation) * b + 2 * regularizer
    perspective = b - b * b / a_theta
    optimizer = -b / a_theta
    minimized = b / 2 + b * optimizer + a_theta * optimizer * optimizer / 2
    check("scalar_A_theta", a_theta == Fraction(3, 4), a_theta, Fraction(3, 4))
    check("scalar_perspective", perspective == Fraction(-1, 3), perspective, Fraction(-1, 3))
    check("scalar_optimizer", optimizer == Fraction(-4, 3), optimizer, Fraction(-4, 3))
    check("scalar_minimum", minimized == Fraction(-1, 6), minimized, Fraction(-1, 6))

    # Noncommuting exact threshold and direct Schur-complement sign tests.
    b_matrix = np.array([[2.0, 1.0], [1.0, 2.0]])
    r_matrix = np.diag([1.0, 0.5])
    r_inverse_sqrt = np.diag([1.0, math.sqrt(2.0)])
    spectral = np.linalg.eigvalsh(r_inverse_sqrt @ b_matrix @ r_inverse_sqrt)
    critical = 2.0 / float(spectral[-1])
    exact_critical = 2.0 / (3.0 + math.sqrt(3.0))
    check("noncommuting_threshold", abs(critical - exact_critical) < 2.0e-15, critical, exact_critical)
    perspective_eigenvalues: dict[str, list[float]] = {}
    for label, theta in (
        ("below", critical / 2.0),
        ("critical", critical),
        ("above", (1.0 + critical) / 2.0),
    ):
        a_matrix = (1.0 - theta) * b_matrix + 2.0 * r_matrix
        schur = b_matrix - b_matrix @ np.linalg.solve(a_matrix, b_matrix)
        eigenvalues = np.linalg.eigvalsh((schur + schur.T) / 2.0)
        perspective_eigenvalues[label] = eigenvalues.tolist()
        if label == "below":
            check("noncommuting_below_positive", eigenvalues[0] > 1.0e-12, eigenvalues[0], "> 0")
        elif label == "critical":
            check("noncommuting_critical_zero", abs(eigenvalues[0]) < 2.0e-14, eigenvalues[0], "0")
        else:
            check("noncommuting_above_negative", eigenvalues[0] < -1.0e-3, eigenvalues[0], "< 0")

    rng = np.random.default_rng(95137)
    maximum_completion_error = 0.0
    minimum_safe_eigenvalue = math.inf
    for index in range(12):
        dimension = 2 + index % 3
        raw = rng.normal(size=(dimension, dimension))
        matrix_b = raw.T @ raw + 0.2 * np.eye(dimension)
        theta = float(rng.uniform(0.03, 0.9))
        reserve_raw = rng.normal(size=(dimension, dimension))
        matrix_r = 0.5 * theta * matrix_b + reserve_raw.T @ reserve_raw + 0.1 * np.eye(dimension)
        matrix_a = (1.0 - theta) * matrix_b + 2.0 * matrix_r
        theta_matrix = matrix_b - matrix_b @ np.linalg.solve(matrix_a, matrix_b)
        minimum_safe_eigenvalue = min(minimum_safe_eigenvalue, float(np.linalg.eigvalsh(theta_matrix)[0]))
        g = rng.normal(size=dimension)
        c = rng.normal(size=dimension)
        left = 0.5 * g @ matrix_b @ g + g @ matrix_b @ c + 0.5 * c @ matrix_a @ c
        shifted = c + np.linalg.solve(matrix_a, matrix_b @ g)
        right = 0.5 * shifted @ matrix_a @ shifted + 0.5 * g @ theta_matrix @ g
        error = abs(float(left - right))
        maximum_completion_error = max(maximum_completion_error, error)
        check(f"random_completion_{index}", error < 2.0e-10, error, "< 2e-10")
    check("random_safe_perspectives", minimum_safe_eigenvalue > -2.0e-12, minimum_safe_eigenvalue, ">= 0")

    # Conditional mean-debt fixture, evaluated directly over four atoms.
    atoms_z = np.array([1.0, -1.0, 2.0, -2.0])
    atoms_b = np.array([0.0, 2.0, 1.5, 0.5])
    mean_b = float(np.mean(atoms_b))
    gamma = float(np.mean(atoms_z**2))
    q = float(np.mean(atoms_b * atoms_z))
    atom_theta = atoms_b - atoms_b**2 / (atoms_b + 2.0)
    r = float(np.mean(np.sqrt(atom_theta) * atoms_z))
    raw_gap = float(np.mean(atoms_b * atoms_z**2) - mean_b * gamma - q * q / (mean_b + 2.0) - r * r)
    check("mean_fixture_b", abs(mean_b - 1.0) < 1.0e-15, mean_b, 1.0)
    check("mean_fixture_q", abs(q) < 1.0e-15, q, 0.0)
    check("mean_fixture_covariance_zero", abs(float(np.mean(atoms_b * atoms_z**2) - mean_b * gamma)) < 1.0e-15, float(np.mean(atoms_b * atoms_z**2) - mean_b * gamma), 0.0)
    check("mean_fixture_r_nonzero", abs(r) > 1.0e-3, r, "nonzero")
    check("mean_fixture_terminal_r_required", abs(raw_gap + r * r) < 2.0e-15, raw_gap + r * r, 0.0)

    # Critical scale conflict from the actually proved prefix envelope.
    j0 = 5
    theta_star = 0.4
    scale_rows: dict[str, dict[str, float]] = {}
    for alpha in (0.75, 1.0, 1.25):
        prefix_terms = [2.0 ** (-(1.0 - alpha) * (j - j0)) for j in range(j0, j0 + 80)]
        mean_terms = [2.0 ** ((1.0 - alpha) * (j - j0)) for j in range(j0, j0 + 80)]
        scale_rows[str(alpha)] = {
            "prefix_tail_ratio": prefix_terms[-1] / prefix_terms[-2],
            "mean_tail_ratio": mean_terms[-1] / mean_terms[-2],
            "theta_star": theta_star,
        }
    check("scale_prefix_requires_alpha_lt_one", scale_rows["0.75"]["prefix_tail_ratio"] < 1.0 and scale_rows["1.25"]["prefix_tail_ratio"] > 1.0, scale_rows, "alpha < 1")
    check("scale_mean_requires_alpha_gt_one", scale_rows["1.25"]["mean_tail_ratio"] < 1.0 and scale_rows["0.75"]["mean_tail_ratio"] > 1.0, scale_rows, "alpha > 1")
    check("scale_critical_product_one", abs(scale_rows["1.0"]["prefix_tail_ratio"] * scale_rows["1.0"]["mean_tail_ratio"] - 1.0) < 1.0e-15, scale_rows["1.0"], "product 1")

    # Independent Cartan homotopy check.  The derivative of the scalar
    # line integral is evaluated by centered differences, rather than by the
    # primary script's direct endpoint formula.
    nodes, weights = leggauss(96)
    symmetric = np.diag([1.0, -0.4, 0.25])
    projector = np.diag([1.0, 1.0, 0.0])
    floor = 0.37
    alpha = 5.0 / 9.0

    def line_integral(z: np.ndarray, a: np.ndarray) -> float:
        total = 0.0
        for node, weight in zip(nodes, weights):
            t = 0.5 * (float(node) + 1.0)
            total += float(weight) * float(normalized_map(z + t * a, symmetric, floor) @ a)
        return 0.5 * total

    maximum_homotopy_error = 0.0
    maximum_omega_ratio = 0.0
    for index in range(10):
        z = rng.normal(size=3)
        a = rng.normal(size=3)
        g = rng.normal(size=3)
        c = rng.normal(size=3)

        def psi_at(point: np.ndarray, displacement: np.ndarray) -> float:
            return 0.5 * (
                (point + displacement) @ projector @ (point + displacement)
                - point @ projector @ point
            ) - alpha * line_integral(point, displacement)

        step = 2.0e-6
        directional = (
            psi_at(z + step * g, a + step * c)
            - psi_at(z - step * g, a - step * c)
        ) / (2.0 * step)
        curvature = 0.0
        for node, weight in zip(nodes, weights):
            t = 0.5 * (float(node) + 1.0)
            point = z + t * a
            k = g + t * c
            jacobian = normalized_jacobian(point, symmetric, floor)
            exterior = float((jacobian @ a) @ k - (jacobian @ k) @ a)
            curvature += 0.5 * float(weight) * exterior
            maximum_omega_ratio = max(maximum_omega_ratio, abs(exterior) / max(float(np.linalg.norm(a) * np.linalg.norm(k)), 1.0e-14))
        map_z = projector @ z - alpha * normalized_map(z, symmetric, floor)
        map_za = projector @ (z + a) - alpha * normalized_map(z + a, symmetric, floor)
        endpoint = float(map_za @ (g + c) - map_z @ g)
        error = abs(endpoint - directional + alpha * curvature)
        maximum_homotopy_error = max(maximum_homotopy_error, error)
        check(f"cartan_homotopy_{index}", error < 4.0e-8, error, "< 4e-8")
    check("cartan_curvature_bound", maximum_omega_ratio <= 2.0 + 2.0e-12, maximum_omega_ratio, "<= 2")

    no_overclaim = {
        "complete_rootwise_R079_R086_form_bound": False,
        "complete_H_N": False,
        "REG": False,
        "OVERLAP_src": False,
        "Nelson": False,
        "interacting_measure": False,
        "Sector_A_closure": False,
    }
    for key, value in no_overclaim.items():
        check(f"no_overclaim_{key}", value is False, value, False)

    failures = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-fractional-feedback-square-perspective-boundary-independent/1.0",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "verifier": "independent",
        "script_version": __version__,
        "date": "2026-07-27",
        "status": "PASS" if not failures else "FAIL",
        "assertions_total": len(rows),
        "assertions_passed": len(rows) - len(failures),
        "assertions_failed": len(failures),
        "assertions": rows,
        "derived": {
            "tree_defects": tree_defects,
            "critical_fraction": critical,
            "perspective_eigenvalues": perspective_eigenvalues,
            "maximum_completion_error": maximum_completion_error,
            "minimum_safe_eigenvalue": minimum_safe_eigenvalue,
            "mean_fixture_r": r,
            "scale_rows": scale_rows,
            "maximum_cartan_homotopy_error": maximum_homotopy_error,
            "maximum_cartan_omega_ratio": maximum_omega_ratio,
        },
        "claims_not_established": list(no_overclaim),
        "independence": {
            "imports_primary": False,
            "reads_primary_result": False,
            "method": "explicit leaf enumeration, direct Schur algebra, and finite-difference homotopy",
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"R-095 INDEPENDENT {'PASS' if not failures else 'FAIL'}: {len(rows) - len(failures)}/{len(rows)} assertions")
    print(f"output={OUTPUT.relative_to(REPO).as_posix()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
