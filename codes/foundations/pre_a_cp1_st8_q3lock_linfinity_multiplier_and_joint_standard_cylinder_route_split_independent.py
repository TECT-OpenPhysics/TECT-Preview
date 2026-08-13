#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.1 route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-linfinity-multiplier-and-joint-standard-cylinder-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split.py"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Independently declared fixture inputs. Outputs are computed, not copied.
REAL_VALUES = (Fraction(-2), Fraction(3))
COMPLEX_POINTS = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(1)), (Fraction(-1), Fraction(0)))
CHI = Fraction(7, 3)
X_POINT = (Fraction(1), Fraction(-2))
Y_POINT = (Fraction(4), Fraction(6))
TIMES = (Fraction(2, 5), Fraction(-2, 5))
POLY_COEFFICIENTS = (Fraction(1, 2), Fraction(-1), Fraction(2), Fraction(-3, 2), Fraction(5, 2))
SEGMENT_RADIUS = 3
MODULATION_PHASE = Fraction(-1)
SCALAR_VALUE = Fraction(7)


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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


Matrix2 = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]


def matrix_multiply(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(
        tuple(sum(left[row][inner] * right[inner][column] for inner in range(2)) for column in range(2))
        for row in range(2)
    )  # type: ignore[return-value]


def matrix_transpose(matrix: Matrix2) -> Matrix2:
    return tuple(tuple(matrix[column][row] for column in range(2)) for row in range(2))  # type: ignore[return-value]


def matrix_subtract(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(2)) for row in range(2)
    )  # type: ignore[return-value]


def fraction_sqrt(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise AssertionError(f"fixture square root is not rational: {value}")
    return Fraction(numerator, denominator)


def operator_norm(matrix: Matrix2) -> Fraction:
    gram = matrix_multiply(matrix_transpose(matrix), matrix)
    trace = gram[0][0] + gram[1][1]
    determinant = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    discriminant = trace * trace - 4 * determinant
    maximum_eigenvalue = (trace + fraction_sqrt(discriminant)) / 2
    return fraction_sqrt(maximum_eigenvalue)


def real_step_fixture() -> dict[str, Any]:
    lower = min(REAL_VALUES)
    upper = max(REAL_VALUES)
    midpoint = (upper + lower) / 2
    diameter = upper - lower
    midpoint_upper = 2 * max(abs(value - midpoint) for value in REAL_VALUES)
    packet_gap = abs(REAL_VALUES[-1] - REAL_VALUES[0])
    return {
        "essential_values": [int(value) for value in REAL_VALUES],
        "midpoint": midpoint,
        "diameter": diameter,
        "midpoint_upper_bound": midpoint_upper,
        "packet_gap": packet_gap,
    }


def complex_step_fixture() -> dict[str, Any]:
    squared = [
        sum((left[index] - right[index]) ** 2 for index in range(2))
        for left, right in combinations(COMPLEX_POINTS, 2)
    ]
    return {
        "essential_values": [[int(value) for value in point] for point in COMPLEX_POINTS],
        "pairwise_squared_distances": [int(value) for value in squared],
        "diameter_squared": max(squared),
        "scope": "lower-bound-only",
    }


def galilean_fixture() -> dict[str, Any]:
    delta = tuple(Y_POINT[index] - X_POINT[index] for index in range(2))
    boosts = [tuple(CHI * component / time for component in delta) for time in TIMES]
    displacements = [tuple(boost[index] * time / CHI for index in range(2)) for boost, time in zip(boosts, TIMES)]
    return {
        "chi": CHI,
        "x": [int(value) for value in X_POINT],
        "y": [int(value) for value in Y_POINT],
        "times": list(TIMES),
        "positive_displacement": [int(value) for value in displacements[0]],
        "negative_displacement": [int(value) for value in displacements[1]],
        "boosts_are_opposite": boosts[0] == tuple(-value for value in boosts[1]),
    }


def polynomial_fixture() -> dict[str, Any]:
    degree = len(POLY_COEFFICIENTS) - 1
    quartic_sum_factor = 2 ** max(degree - 1, 0)
    coefficient_l1 = sum(abs(value) for value in POLY_COEFFICIENTS)
    translation_factor = 1 + quartic_sum_factor * SEGMENT_RADIUS**degree
    safe_envelope = coefficient_l1 * translation_factor
    return {
        "degree": degree,
        "coefficients": list(POLY_COEFFICIENTS),
        "coefficient_l1": coefficient_l1,
        "segment_radius": SEGMENT_RADIUS,
        "safe_envelope": safe_envelope,
        "translation_factor": translation_factor,
    }


def joint_fixture() -> dict[str, Any]:
    modulation: Matrix2 = ((Fraction(1), Fraction(0)), (Fraction(0), MODULATION_PHASE))
    offdiagonal: Matrix2 = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)))
    multiplier: Matrix2 = ((REAL_VALUES[0], Fraction(0)), (Fraction(0), REAL_VALUES[1]))
    scalar: Matrix2 = ((SCALAR_VALUE, Fraction(0)), (Fraction(0), SCALAR_VALUE))

    def conjugation_distance(matrix: Matrix2) -> Fraction:
        conjugated = matrix_multiply(matrix_multiply(matrix_transpose(modulation), matrix), modulation)
        return operator_norm(matrix_subtract(conjugated, matrix))

    scalar_diagonal_range = max(scalar[index][index] for index in range(2)) - min(
        scalar[index][index] for index in range(2)
    )
    return {
        "offdiagonal_bond_distance": conjugation_distance(offdiagonal),
        "nonscalar_multiplier_bond_distance": conjugation_distance(multiplier),
        "nonscalar_multiplier_full_h_lower": real_step_fixture()["diameter"],
        "scalar_bond_distance": conjugation_distance(scalar),
        "scalar_full_h_distance": scalar_diagonal_range,
    }


def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    raise TypeError(f"unsupported fixture value: {type(value)!r}")


def independence_firewall() -> dict[str, Any]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "math",
        "os",
        "tempfile",
        "fractions",
        "itertools",
        "pathlib",
        "typing",
    }
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "compile"}:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "exec_module", "load_module"}:
                dynamic.append(node.func.attr)
    return {"unapproved": sorted(imports - allowed), "dynamic": dynamic, "imports": sorted(imports)}


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = {
        "real_step": real_step_fixture(),
        "complex_step": complex_step_fixture(),
        "galilean": galilean_fixture(),
        "polynomial_translation": polynomial_fixture(),
        "joint_truth_table": joint_fixture(),
    }
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.1"
        and manifest["exploration_id"] == "EXP-000835"
        and manifest["prior_exploration_id"] == "EXP-000834"
        and manifest["claim_bearing"] is False,
        (manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        (SLUG, "R-167 v3.1", "EXP-000835"),
        "identity",
    )
    audit.check(
        "one scoped child one negative five parents",
        len(manifest["closed_gate_ids"]) == 1
        and len(manifest["negative_ids"]) == 1
        and len(manifest["open_parent_gate_ids"]) == len(set(manifest["open_parent_gate_ids"])) == 5,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["open_parent_gate_ids"]),
        (1, 1, 5),
        "identity",
    )

    for group, oracle in manifest["exact_fixture"].items():
        fixture = derived[group]
        for key, expected in oracle.items():
            audit.check(
                f"{group} {key}",
                key in fixture and stringify(fixture[key]) == expected,
                stringify(fixture.get(key)),
                expected,
                group,
            )

    audit.check(
        "real exact lower upper match",
        derived["real_step"]["diameter"]
        == derived["real_step"]["midpoint_upper_bound"]
        == derived["real_step"]["packet_gap"],
        derived["real_step"],
        "equal derived real bounds",
        "theorem",
    )
    audit.check(
        "complex diameter independently maximized",
        derived["complex_step"]["diameter_squared"] == max(derived["complex_step"]["pairwise_squared_distances"]),
        derived["complex_step"]["diameter_squared"],
        "maximum pairwise square",
        "theorem",
    )
    audit.check(
        "Galilean both signs",
        derived["galilean"]["positive_displacement"] == derived["galilean"]["negative_displacement"]
        and derived["galilean"]["boosts_are_opposite"],
        derived["galilean"],
        "same displacement, opposite boosts",
        "theorem",
    )
    audit.check(
        "polynomial envelope exact multiplication",
        derived["polynomial_translation"]["safe_envelope"]
        == derived["polynomial_translation"]["coefficient_l1"]
        * derived["polynomial_translation"]["translation_factor"],
        derived["polynomial_translation"]["safe_envelope"],
        "product",
        "theorem",
    )
    audit.check(
        "joint truth table independently derived",
        derived["joint_truth_table"]["offdiagonal_bond_distance"] > 0
        and derived["joint_truth_table"]["nonscalar_multiplier_bond_distance"] == 0
        and derived["joint_truth_table"]["nonscalar_multiplier_full_h_lower"] > 0
        and derived["joint_truth_table"]["scalar_bond_distance"] == 0
        and derived["joint_truth_table"]["scalar_full_h_distance"] == 0,
        derived["joint_truth_table"],
        "only scalar survives both fixture tests",
        "theorem",
    )

    firewall = independence_firewall()
    audit.check(
        "stdlib non-importing independence firewall",
        not firewall["unapproved"] and not firewall["dynamic"],
        firewall,
        "stdlib allowlist and no dynamic import/execution",
        "independence",
    )
    audit.check(
        "source independent from primary",
        normalized_sha256(SCRIPT) != normalized_sha256(PRIMARY),
        normalized_sha256(SCRIPT),
        "different from primary",
        "independence",
    )

    required_tokens = (
        "D_ess(f)",
        "Lebesgue differentiation",
        "p_t = chi (y-x)/t",
        "diverging phase",
        "s/t in [0,1]",
        "C_epsilon |t|/hbar",
        "eta; x,y; fixed epsilon",
        "intersection equals the scalar multiples",
        "lower-bound theorem",
        "not a classification of the full continuous-element algebra",
        "All five active parent gates remain OPEN",
        "No v3.1 PDF is issued",
    )
    audit.check(
        "certificate independent proof tokens",
        all(token in certificate for token in required_tokens),
        [token for token in required_tokens if token not in certificate],
        [],
        "certificate",
    )
    audit.check(
        "certificate exact-Q3 missing-lemma boundary",
        "No exact-Q3 background-uniform bound" in certificate
        and "does not prove that a common thermodynamic action is impossible" in certificate
        and "physical Sector A, or Pre-A" in certificate,
        "boundary tokens",
        "present",
        "certificate",
    )

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_ok = (
            formal_text.count("EXP-000835") > 0
            and manifest["closed_gate_ids"][0] in formal_text
            and manifest["negative_ids"][0] in formal_text
            and "R-167 v3.1" in formal_text
        )
        audit.check("formal authority aggregate", formal_ok, formal_ok, True, "formal")

    serialized = stringify(derived)
    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": serialized,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.1 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
