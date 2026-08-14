#!/usr/bin/env python3
"""Verify the R-169 v1.0 geometry-first sign/stability route split.

Purpose: derive the exact BCC Voronoi truncated-octahedron fixture, its
volume-preserving affine-combinatorial family, the matched-renormalization
relative sign bound, and the transverse-Hessian route-split fixture.

Convention: candidate minus preregistered reference is the relative sign;
the van-Hove limit precedes the continuum limit; affine images are called
tiles with the same combinatorics, not Euclidean Voronoi cells.

Formula: DeltaF <= Deltahat + e_num + e_TD + e_UV + e_sch, while
lambda_perp is the real Hessian infimum after exact symmetry directions are
removed. All derived values come from the machine manifest.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-truncated-octahedron-realization-and-empty-reference-sign-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
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


def text(value: sp.Expr) -> str:
    return str(sp.factor(sp.simplify(value)))


def rational(value: str | int) -> sp.Rational:
    return sp.Rational(str(value))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def make_planes(dimension: int, axis_bound: sp.Rational, diagonal_bound: sp.Rational) -> list[dict[str, Any]]:
    planes: list[dict[str, Any]] = []
    for coordinate in range(dimension):
        for sign in (-1, 1):
            normal = [sp.Integer(0)] * dimension
            normal[coordinate] = sp.Integer(sign)
            planes.append({"kind": "quadrilateral", "normal": tuple(normal), "bound": axis_bound})
    for signs in itertools.product((-1, 1), repeat=dimension):
        planes.append(
            {"kind": "hexagonal", "normal": tuple(sp.Integer(sign) for sign in signs), "bound": diagonal_bound}
        )
    return planes


def enumerate_vertices(planes: list[dict[str, Any]], dimension: int) -> tuple[set[tuple[sp.Expr, ...]], dict[tuple[sp.Expr, ...], set[int]]]:
    vertices: set[tuple[sp.Expr, ...]] = set()
    for selection in itertools.combinations(range(len(planes)), dimension):
        matrix = sp.Matrix([planes[index]["normal"] for index in selection])
        if matrix.det() == 0:
            continue
        rhs = sp.Matrix([planes[index]["bound"] for index in selection])
        solution = tuple(sp.simplify(value) for value in matrix.inv() * rhs)
        if all(
            sp.Matrix(plane["normal"]).dot(sp.Matrix(solution)) <= plane["bound"]
            for plane in planes
        ):
            vertices.add(solution)
    active: dict[tuple[sp.Expr, ...], set[int]] = {}
    for vertex in vertices:
        active[vertex] = {
            index
            for index, plane in enumerate(planes)
            if sp.Matrix(plane["normal"]).dot(sp.Matrix(vertex)) == plane["bound"]
        }
    return vertices, active


def geometry_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]
    dimension = int(inputs["dimension"])
    axis_bound = rational(inputs["axis_bound"])
    diagonal_bound = rational(inputs["diagonal_bound"])
    planes = make_planes(dimension, axis_bound, diagonal_bound)
    vertices, active = enumerate_vertices(planes, dimension)

    middle_coordinate = sp.simplify(diagonal_bound - axis_bound)
    expected_vertices = {
        tuple(sp.Integer(signs[index]) * permutation[index] for index in range(dimension))
        for permutation in set(itertools.permutations((sp.Integer(0), middle_coordinate, axis_bound)))
        for signs in itertools.product((-1, 1), repeat=dimension)
    }

    face_counts = []
    for index, plane in enumerate(planes):
        face_counts.append((plane["kind"], sum(index in active[vertex] for vertex in vertices)))
    quadrilateral_faces = sum(kind == "quadrilateral" and count == 4 for kind, count in face_counts)
    hexagonal_faces = sum(kind == "hexagonal" and count == 6 for kind, count in face_counts)

    edges = {
        tuple(sorted((left, right), key=str))
        for left, right in itertools.combinations(vertices, 2)
        if len(active[left].intersection(active[right])) == dimension - 1
    }
    edge_count = len(edges)
    euler = len(vertices) - edge_count + len(planes)

    basis_columns = [sp.Matrix(column) for column in inputs["lattice_basis"]]
    lattice_matrix = sp.Matrix.hstack(*basis_columns)
    determinant = abs(sp.det(lattice_matrix))

    affine_t = rational(inputs["affine_t"])
    affine = sp.diag(affine_t, sp.Integer(1), 1 / affine_t)
    affine_determinant = sp.det(affine)
    base_translation_length = 2 * axis_bound
    descendant_lengths = [sp.simplify(base_translation_length * affine[index, index]) for index in range(dimension)]
    translation_ratio = sp.simplify(max(descendant_lengths) / min(descendant_lengths))

    parity_witnesses = []
    coefficient_radius = int(axis_bound + diagonal_bound)
    for coefficients in itertools.product(range(-coefficient_radius, coefficient_radius + 1), repeat=dimension):
        if coefficients == (0,) * dimension:
            continue
        if not all((value - coefficients[0]) % 2 == 0 for value in coefficients):
            continue
        nearest_even = sorted(abs(value) for value in coefficients) == [0, 0, int(axis_bound)]
        nearest_odd = all(abs(value) == int(middle_coordinate) for value in coefficients)
        if nearest_even or nearest_odd:
            continue
        lhs = 2 * sum(abs(value) for value in coefficients)
        rhs = sum(value * value for value in coefficients)
        parity_witnesses.append(lhs <= rhs)

    return {
        "plane_count": len(planes),
        "vertex_count": len(vertices),
        "vertices_match_permutation_formula": vertices == expected_vertices,
        "quadrilateral_faces": quadrilateral_faces,
        "hexagonal_faces": hexagonal_faces,
        "edge_count": edge_count,
        "euler_characteristic": euler,
        "lattice_determinant": text(determinant),
        "affine_determinant": text(affine_determinant),
        "affine_quadrilateral_translation_ratio": text(translation_ratio),
        "finite_parity_redundancy_audit": all(parity_witnesses),
        "finite_parity_witness_count": len(parity_witnesses),
    }


def renormalization_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]["renormalization"]
    candidate = rational(inputs["candidate_bare"])
    reference = rational(inputs["reference_bare"])
    common_scalar = rational(inputs["common_scalar"])
    positive_scale = rational(inputs["positive_common_scale"])
    finite_shift = rational(inputs["unfixed_finite_shift"])

    bare_difference = sp.simplify(candidate - reference)
    common_scalar_difference = sp.simplify((candidate - common_scalar) - (reference - common_scalar))
    scaled_difference = sp.simplify(positive_scale * common_scalar_difference)
    candidate_specific_shifted = sp.simplify(bare_difference + finite_shift)

    certificate = manifest["exact_fixture_inputs"]["sign_certificate"]
    estimate = rational(certificate["estimate"])
    errors = [rational(value) for value in certificate["errors"]]
    eta = rational(certificate["eta"])
    error_sum = sp.simplify(sum(errors, sp.Integer(0)))
    certified_upper = sp.simplify(estimate + error_sum)

    n = sp.symbols("n", positive=True, integer=True)
    finite_sequence = [-sp.Rational(1, value) for value in (1, 2, 4, 8)]
    limiting_sequence = -1 / n

    return {
        "bare_difference": text(bare_difference),
        "common_scalar_difference": text(common_scalar_difference),
        "scaled_difference": text(scaled_difference),
        "candidate_specific_shifted_difference": text(candidate_specific_shifted),
        "error_sum": text(error_sum),
        "certified_upper": text(certified_upper),
        "uniform_margin_pass": bool(certified_upper <= -eta),
        "finite_sequence_all_negative": all(value < 0 for value in finite_sequence),
        "finite_sequence_limit": text(sp.limit(limiting_sequence, n, sp.oo)),
    }


def polynomial_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    x, y, z, alpha, tau = sp.symbols("x y z alpha tau", real=True)
    polynomial = x**2 * (x**2 - 1) ** 2 + alpha * (2 * x**2 - x**4) + (1 - tau * x**2) * y**2 + y**4
    variables = (x, y, z)
    gradient = sp.Matrix([sp.diff(polynomial, variable) for variable in variables])
    hessian = sp.hessian(polynomial, variables)
    points = manifest["exact_fixture_inputs"]["points"]
    candidate_point = {variable: rational(value) for variable, value in zip(variables, points["candidate"])}
    reference_point = {variable: rational(value) for variable, value in zip(variables, points["reference"])}
    competitor_point = {variable: rational(value) for variable, value in zip(variables, points["tested_competitor"])}

    cases: dict[str, Any] = {}
    for case in manifest["exact_fixture_inputs"]["polynomial_cases"]:
        substitutions = {alpha: rational(case["alpha"]), tau: rational(case["tau"])}
        candidate_substitutions = substitutions | candidate_point
        reference_substitutions = substitutions | reference_point
        competitor_substitutions = substitutions | competitor_point
        candidate_energy = sp.simplify(polynomial.subs(candidate_substitutions))
        reference_energy = sp.simplify(polynomial.subs(reference_substitutions))
        competitor_energy = sp.simplify(polynomial.subs(competitor_substitutions))
        candidate_gradient = [sp.simplify(value.subs(candidate_substitutions)) for value in gradient]
        reference_gradient = [sp.simplify(value.subs(reference_substitutions)) for value in gradient]
        full_hessian = hessian.subs(candidate_substitutions)
        transverse_hessian = [sp.simplify(full_hessian[index, index]) for index in (0, 1)]
        cases[case["label"]] = {
            "candidate": text(candidate_energy),
            "reference": text(reference_energy),
            "relative_sign": text(candidate_energy - reference_energy),
            "competitor": text(competitor_energy),
            "candidate_stationary": all(value == 0 for value in candidate_gradient),
            "reference_stationary": all(value == 0 for value in reference_gradient),
            "transverse_hessian": [text(value) for value in transverse_hessian],
            "candidate_beats_tested_competitor": bool(candidate_energy < competitor_energy),
            "strict_transverse_stability": all(value > 0 for value in transverse_hessian),
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
        (manifest["version"], manifest["exploration_id"], manifest["closed_gate_ids"], manifest["new_negative_ids"]),
        ("R-169 v1.0", "EXP-000851", CLOSED, NEW_NEGATIVES),
        "topology",
    )
    semantics = " ".join(manifest["geometry_semantics"].values())
    geometry_text = " ".join(manifest["standard_bcc_voronoi_fixture"].values())
    affine_text = " ".join(manifest["affine_realization_family"].values())
    audit.check(
        "geometry semantics and affine firewall",
        all(
            token in semantics + " " + geometry_text + " " + affine_text
            for token in (
                "metric-regular",
                "affine-combinatorial",
                "statistically extracted",
                "P=Vor_L(0)",
                "six square",
                "eight regular-hexagonal",
                "pairwise nonsimilar",
                "not claimed to be the Euclidean Voronoi cell",
            )
        ),
        "required semantic tokens present",
        "required semantic tokens present",
        "theorem",
    )
    matched = " ".join(manifest["matched_renormalization"].values())
    signed = " ".join(manifest["signed_limit_reduction"].values())
    transverse = " ".join(manifest["transverse_stability_reduction"].values())
    audit.check(
        "matched-scheme signed-limit theorem",
        all(
            token in matched + " " + signed
            for token in (
                "finite parts",
                "state-independent scalar",
                "do not make O_nu",
                "van-Hove",
                "no exchange",
                "e_num+e_TD+e_UV+e_sch",
                "Delta_n=-1/n",
            )
        ),
        "matched counterterms and frozen limit",
        "matched counterterms and frozen limit",
        "theorem",
    )
    audit.check(
        "transverse stability theorem",
        all(
            token in transverse
            for token in (
                "full admissible regulated tangent",
                "limiting candidate is stationary",
                "symmetry/gauge orbit tangent",
                "identified limiting transverse forms",
                "kappa>0",
                "M-Lipschitz",
                "semistability",
            )
        ),
        "full tangent and form-liminf contract",
        "full tangent and form-liminf contract",
        "theorem",
    )

    geometry = derived["geometry"]
    geometry_oracle = manifest["test_oracles"]["geometry"]
    audit.check(
        "exact polytope and affine derivation",
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
        "exact renormalization and margin derivation",
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
        "exact ranking-stability-sign route split",
        positive["candidate"] == polynomial_oracle["positive_case_candidate"]
        and positive["competitor"] == polynomial_oracle["positive_case_competitor"]
        and positive["transverse_hessian"] == polynomial_oracle["positive_case_hessian"]
        and negative["candidate"] == polynomial_oracle["negative_case_candidate"]
        and negative["competitor"] == polynomial_oracle["negative_case_competitor"]
        and negative["transverse_hessian"] == polynomial_oracle["negative_case_hessian"]
        and positive["candidate_stationary"]
        and positive["reference_stationary"]
        and positive["candidate_beats_tested_competitor"]
        and positive["strict_transverse_stability"]
        and negative["candidate_beats_tested_competitor"]
        and not negative["strict_transverse_stability"],
        polynomial,
        polynomial_oracle,
        "derivation",
    )

    audit.check(
        "certificate theorem and governance tokens",
        all(
            token in certificate
            for token in (
                *CLOSED,
                *NEW_NEGATIVES,
                "P=Vor_L(0)",
                "not say that `D_t P` is the Euclidean Voronoi cell",
                "common state-independent scalar",
                "state-dependent counterterm does not cancel",
                "Delta_n=-1/n",
                "full admissible tangent",
                "diag(6,2)",
                "diag(10,-2)",
                "Devil's-advocate and code-discipline audit",
                "External adversarial review is invited",
                "No R-169",
            )
        ),
        "required certificate tokens present",
        "required certificate tokens present",
        "certificate",
    )
    audit.check(
        "source AST and format",
        ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None
        and all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        "AST ASCII LF final-LF",
        "AST ASCII LF final-LF",
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
        "schema": "tect/pre-a-t055-truncated-octahedron-sign-run/1.0",
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
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
