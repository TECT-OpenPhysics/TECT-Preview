#!/usr/bin/env python3
"""Independently verify the R-169 v1.0 geometry/sign route split.

Purpose: recompute the polytope incidence, affine invariant, matched scalar
cancellation, uniform sign margin, and two polynomial Hessian fixtures using
only Python standard-library exact rational arithmetic.

Convention: relative means candidate minus preregistered reference; affine
images preserve tiling combinatorics but are not called Euclidean Voronoi
cells; symmetry-zero directions are omitted from the transverse Hessian.

Formula: DeltaF <= Deltahat + sum(errors), and the polynomial fixture has
H_perp=diag(8-8 alpha,2-2 tau) at the candidate point.
"""

from __future__ import annotations

import argparse
import ast
from fractions import Fraction
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-truncated-octahedron-realization-and-empty-reference-sign-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = [
    "PA-T055-TRUNCATED-OCTAHEDRON-BCC-VORONOI-AND-AFFINE-REALIZATION-FAMILY",
    "PA-T055-MATCHED-RENORMALIZATION-EMPTY-REFERENCE-SIGN-AND-TRANSVERSE-STABILITY-REDUCTION",
]
NEW_NEGATIVES = [
    "NG-2026-08-14-PRE-A-T055-TRUNCATED-OCTAHEDRON-COMBINATORICS-AUTOMATIC-FINITE-REALIZATION-ENUMERATION",
    "NG-2026-08-14-PRE-A-T055-COMMON-COUNTERTERM-BASIS-UNFIXED-FINITE-PARTS-AUTOMATIC-EMPTY-REFERENCE-SIGN",
]
REUSED = [
    "R-2026-06-23-b3-bcc-structural-selection",
    "NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-EQUILIBRIUM-PHASE-AS-STRICT-EMPTY-REFERENCE",
]


def normalized_sha256(path: Path) -> str:
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


def q(value: str | int) -> Fraction:
    return Fraction(str(value))


def exact_text(value: Fraction | int) -> str:
    fraction = value if isinstance(value, Fraction) else Fraction(value)
    return str(fraction.numerator) if fraction.denominator == 1 else f"{fraction.numerator}/{fraction.denominator}"


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def determinant3(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def replace_column(
    matrix: tuple[tuple[Fraction, ...], ...], column: int, rhs: tuple[Fraction, ...]
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(rhs[row] if index == column else matrix[row][index] for index in range(3))
        for row in range(3)
    )


def solve3(matrix: tuple[tuple[Fraction, ...], ...], rhs: tuple[Fraction, ...]) -> tuple[Fraction, ...] | None:
    determinant = determinant3(matrix)
    if determinant == 0:
        return None
    return tuple(determinant3(replace_column(matrix, column, rhs)) / determinant for column in range(3))


def dot(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def geometry_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]
    dimension = int(inputs["dimension"])
    if dimension != 3:
        raise AssertionError("independent exact solver is intentionally three-dimensional")
    axis_bound = q(inputs["axis_bound"])
    diagonal_bound = q(inputs["diagonal_bound"])
    planes: list[tuple[str, tuple[Fraction, ...], Fraction]] = []
    for coordinate in range(dimension):
        for sign in (-1, 1):
            normal = [Fraction(0)] * dimension
            normal[coordinate] = Fraction(sign)
            planes.append(("quadrilateral", tuple(normal), axis_bound))
    for signs in itertools.product((-1, 1), repeat=dimension):
        planes.append(("hexagonal", tuple(Fraction(sign) for sign in signs), diagonal_bound))

    vertices: set[tuple[Fraction, ...]] = set()
    for selection in itertools.combinations(range(len(planes)), dimension):
        matrix = tuple(planes[index][1] for index in selection)
        rhs = tuple(planes[index][2] for index in selection)
        solution = solve3(matrix, rhs)
        if solution is not None and all(dot(normal, solution) <= bound for _, normal, bound in planes):
            vertices.add(solution)
    active = {
        vertex: {index for index, (_, normal, bound) in enumerate(planes) if dot(normal, vertex) == bound}
        for vertex in vertices
    }
    middle = diagonal_bound - axis_bound
    expected_vertices = {
        tuple(Fraction(signs[index]) * permutation[index] for index in range(dimension))
        for permutation in set(itertools.permutations((Fraction(0), middle, axis_bound)))
        for signs in itertools.product((-1, 1), repeat=dimension)
    }
    face_counts = [
        (kind, sum(index in active[vertex] for vertex in vertices))
        for index, (kind, _, _) in enumerate(planes)
    ]
    quadrilateral_faces = sum(kind == "quadrilateral" and count == 4 for kind, count in face_counts)
    hexagonal_faces = sum(kind == "hexagonal" and count == 6 for kind, count in face_counts)
    edges = {
        tuple(sorted((left, right), key=str))
        for left, right in itertools.combinations(vertices, 2)
        if len(active[left].intersection(active[right])) == dimension - 1
    }
    lattice_rows = tuple(
        tuple(Fraction(inputs["lattice_basis"][column][row]) for column in range(dimension))
        for row in range(dimension)
    )
    lattice_determinant = abs(determinant3(lattice_rows))
    affine_t = q(inputs["affine_t"])
    affine_determinant = affine_t * Fraction(1) / affine_t
    descendant_lengths = (2 * axis_bound * affine_t, 2 * axis_bound, 2 * axis_bound / affine_t)
    translation_ratio = max(descendant_lengths) / min(descendant_lengths)

    parity_witnesses = []
    coefficient_radius = int(axis_bound + diagonal_bound)
    for coefficients in itertools.product(range(-coefficient_radius, coefficient_radius + 1), repeat=dimension):
        if coefficients == (0,) * dimension:
            continue
        if not all((value - coefficients[0]) % 2 == 0 for value in coefficients):
            continue
        nearest_even = sorted(abs(value) for value in coefficients) == [0, 0, int(axis_bound)]
        nearest_odd = all(abs(value) == int(middle) for value in coefficients)
        if nearest_even or nearest_odd:
            continue
        parity_witnesses.append(2 * sum(abs(value) for value in coefficients) <= sum(value * value for value in coefficients))

    return {
        "plane_count": len(planes),
        "vertex_count": len(vertices),
        "vertices_match_permutation_formula": vertices == expected_vertices,
        "quadrilateral_faces": quadrilateral_faces,
        "hexagonal_faces": hexagonal_faces,
        "edge_count": len(edges),
        "euler_characteristic": len(vertices) - len(edges) + len(planes),
        "lattice_determinant": exact_text(lattice_determinant),
        "affine_determinant": exact_text(affine_determinant),
        "affine_quadrilateral_translation_ratio": exact_text(translation_ratio),
        "finite_parity_redundancy_audit": all(parity_witnesses),
        "finite_parity_witness_count": len(parity_witnesses),
    }


def renormalization_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]["renormalization"]
    candidate = q(inputs["candidate_bare"])
    reference = q(inputs["reference_bare"])
    common_scalar = q(inputs["common_scalar"])
    scale = q(inputs["positive_common_scale"])
    finite_shift = q(inputs["unfixed_finite_shift"])
    bare_difference = candidate - reference
    common_scalar_difference = (candidate - common_scalar) - (reference - common_scalar)
    certificate = manifest["exact_fixture_inputs"]["sign_certificate"]
    estimate = q(certificate["estimate"])
    errors = [q(value) for value in certificate["errors"]]
    eta = q(certificate["eta"])
    error_sum = sum(errors, Fraction(0))
    certified_upper = estimate + error_sum
    finite_sequence = [-Fraction(1, value) for value in (1, 2, 4, 8)]
    return {
        "bare_difference": exact_text(bare_difference),
        "common_scalar_difference": exact_text(common_scalar_difference),
        "scaled_difference": exact_text(scale * common_scalar_difference),
        "candidate_specific_shifted_difference": exact_text(bare_difference + finite_shift),
        "error_sum": exact_text(error_sum),
        "certified_upper": exact_text(certified_upper),
        "uniform_margin_pass": certified_upper <= -eta,
        "finite_sequence_all_negative": all(value < 0 for value in finite_sequence),
        "finite_sequence_limit": "0",
    }


def polynomial_value(x: Fraction, y: Fraction, alpha: Fraction, tau: Fraction) -> Fraction:
    return x**2 * (x**2 - 1) ** 2 + alpha * (2 * x**2 - x**4) + (1 - tau * x**2) * y**2 + y**4


def polynomial_gradient(x: Fraction, y: Fraction, alpha: Fraction, tau: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    dx = 6 * x**5 - 8 * x**3 + 2 * x + 4 * alpha * x - 4 * alpha * x**3 - 2 * tau * x * y**2
    dy = 2 * y - 2 * tau * x**2 * y + 4 * y**3
    return dx, dy, Fraction(0)


def transverse_hessian(x: Fraction, y: Fraction, alpha: Fraction, tau: Fraction) -> tuple[Fraction, Fraction]:
    hxx = 30 * x**4 - 24 * x**2 + 2 + 4 * alpha - 12 * alpha * x**2 - 2 * tau * y**2
    hyy = 2 - 2 * tau * x**2 + 12 * y**2
    return hxx, hyy


def polynomial_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    points = manifest["exact_fixture_inputs"]["points"]
    candidate = tuple(q(value) for value in points["candidate"])
    reference = tuple(q(value) for value in points["reference"])
    competitor = tuple(q(value) for value in points["tested_competitor"])
    cases: dict[str, Any] = {}
    for case in manifest["exact_fixture_inputs"]["polynomial_cases"]:
        alpha = q(case["alpha"])
        tau = q(case["tau"])
        candidate_energy = polynomial_value(candidate[0], candidate[1], alpha, tau)
        reference_energy = polynomial_value(reference[0], reference[1], alpha, tau)
        competitor_energy = polynomial_value(competitor[0], competitor[1], alpha, tau)
        candidate_gradient = polynomial_gradient(candidate[0], candidate[1], alpha, tau)
        reference_gradient = polynomial_gradient(reference[0], reference[1], alpha, tau)
        hessian = transverse_hessian(candidate[0], candidate[1], alpha, tau)
        cases[case["label"]] = {
            "candidate": exact_text(candidate_energy),
            "reference": exact_text(reference_energy),
            "relative_sign": exact_text(candidate_energy - reference_energy),
            "competitor": exact_text(competitor_energy),
            "candidate_stationary": candidate_gradient == (Fraction(0),) * 3,
            "reference_stationary": reference_gradient == (Fraction(0),) * 3,
            "transverse_hessian": [exact_text(value) for value in hessian],
            "candidate_beats_tested_competitor": candidate_energy < competitor_energy,
            "strict_transverse_stability": all(value > 0 for value in hessian),
        }
    return cases


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "geometry": geometry_derivation(manifest),
        "renormalization": renormalization_derivation(manifest),
        "polynomial": polynomial_derivation(manifest),
    }


def build_payload(*, formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    audit = Audit()
    audit.check(
        "identity and topology",
        manifest["version"] == "R-169 v1.0"
        and manifest["exploration_id"] == "EXP-000851"
        and manifest["closed_gate_ids"] == CLOSED
        and manifest["new_negative_ids"] == NEW_NEGATIVES
        and manifest["reused_negative_ids"] == REUSED,
        "exact topology",
        "exact topology",
        "topology",
    )
    audit.check(
        "affine-voronoi semantic firewall",
        "not claimed to be the Euclidean Voronoi cell" in manifest["affine_realization_family"]["boundary"]
        and "different candidate classes" in manifest["geometry_semantics"]["firewall"],
        "affine tile only",
        "affine tile only",
        "theorem",
    )
    audit.check(
        "matched finite parts and limit order",
        "finite parts" in manifest["matched_renormalization"]["matching"]
        and "do not make" in manifest["matched_renormalization"]["state_dependent_terms"]
        and "no exchange" in manifest["signed_limit_reduction"]["order"]
        and "uniform margin" in manifest["signed_limit_reduction"]["finite_regulator_firewall"],
        "matched scheme",
        "matched scheme",
        "theorem",
    )
    audit.check(
        "limiting stationarity before local minimum",
        "limiting candidate is stationary" in manifest["transverse_stability_reduction"]["stationarity"]
        and "certified gradient convergence" in manifest["transverse_stability_reduction"]["stationarity"]
        and "stationary on the symmetry slice" in manifest["transverse_stability_reduction"]["local_minimum"],
        "limit stationarity or gradient passage is explicit",
        "limit stationarity or gradient passage is explicit",
        "theorem",
    )
    geometry = derived["geometry"]
    geometry_oracle = manifest["test_oracles"]["geometry"]
    audit.check(
        "independent exact geometry",
        all(str(geometry[key]) == str(value) for key, value in geometry_oracle.items())
        and geometry["vertices_match_permutation_formula"]
        and geometry["finite_parity_redundancy_audit"],
        geometry,
        geometry_oracle,
        "derivation",
    )
    renormalization = derived["renormalization"]
    renormalization_oracle = manifest["test_oracles"]["renormalization"]
    audit.check(
        "independent exact renormalization",
        all(str(renormalization[key]) == str(value) for key, value in renormalization_oracle.items())
        and renormalization["finite_sequence_all_negative"]
        and renormalization["finite_sequence_limit"] == "0",
        renormalization,
        renormalization_oracle,
        "derivation",
    )
    polynomial = derived["polynomial"]
    polynomial_oracle = manifest["test_oracles"]["polynomial"]
    positive = polynomial["ranking_stable_but_above_reference"]
    negative = polynomial["below_reference_but_transverse_saddle"]
    audit.check(
        "independent exact polynomial split",
        positive["candidate"] == polynomial_oracle["positive_case_candidate"]
        and positive["competitor"] == polynomial_oracle["positive_case_competitor"]
        and positive["transverse_hessian"] == polynomial_oracle["positive_case_hessian"]
        and negative["candidate"] == polynomial_oracle["negative_case_candidate"]
        and negative["competitor"] == polynomial_oracle["negative_case_competitor"]
        and negative["transverse_hessian"] == polynomial_oracle["negative_case_hessian"]
        and positive["candidate_stationary"]
        and positive["reference_stationary"]
        and positive["strict_transverse_stability"]
        and not negative["strict_transverse_stability"],
        polynomial,
        polynomial_oracle,
        "derivation",
    )
    audit.check(
        "certificate scope tokens",
        all(
            token in certificate
            for token in (
                *CLOSED,
                *NEW_NEGATIVES,
                "affine translational tile",
                "state-dependent counterterm does not cancel",
                "full admissible tangent",
                "No R-169",
            )
        ),
        "required certificate tokens",
        "required certificate tokens",
        "certificate",
    )
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden_names = {"float", "complex", "eval", "exec", "compile"}
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    audit.check(
        "stdlib exact-arithmetic AST firewall",
        not ({"sympy", "numpy", "scipy"} & imported)
        and not (forbidden_names & called_names)
        and all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        {"imports": sorted(imported), "forbidden_calls": sorted(forbidden_names & called_names)},
        "stdlib, no float/complex/dynamic execution, ASCII LF",
        "format",
    )
    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check(
            "formal authority links",
            all(token in formal_text for token in ("EXP-000851", "R-169", *CLOSED, *NEW_NEGATIVES, *REUSED)),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )
    return {
        "schema": "tect/pre-a-t055-truncated-octahedron-sign-independent-run/1.0",
        "version": manifest["version"],
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(formal=not args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
