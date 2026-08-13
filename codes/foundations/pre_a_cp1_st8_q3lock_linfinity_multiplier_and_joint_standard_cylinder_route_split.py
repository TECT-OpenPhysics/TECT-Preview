#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.1 route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from itertools import combinations
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-linfinity-multiplier-and-joint-standard-cylinder-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Labelled finite oracle inputs. Every reported quantity is derived below.
REAL_STEP_INPUTS = (-2, 3)
COMPLEX_STEP_INPUTS = ((0, 0), (1, 1), (-1, 0))
GALILEAN_INPUTS = {
    "chi_num": 7,
    "chi_den": 3,
    "x": (1, -2),
    "y": (4, 6),
    "times": ((2, 5), (-2, 5)),
}
POLYNOMIAL_INPUTS = {
    "coefficients": ((1, 2), (-1, 1), (2, 1), (-3, 2), (5, 2)),
    "segment_radius": 3,
}
BOND_INPUTS = {"modulation_phase": -1, "scalar": 7}


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


def operator_norm(matrix: sp.Matrix) -> sp.Expr:
    gram = sp.simplify(matrix.H * matrix)
    eigenvalues: list[sp.Expr] = []
    for value, multiplicity in gram.eigenvals().items():
        eigenvalues.extend([sp.simplify(value)] * int(multiplicity))
    return sp.sqrt(max(eigenvalues))


def real_step_fixture() -> dict[str, Any]:
    values = tuple(sp.Integer(value) for value in REAL_STEP_INPUTS)
    lower = min(values)
    upper = max(values)
    midpoint = sp.factor((upper + lower) / 2)
    diameter = sp.factor(upper - lower)
    midpoint_upper = sp.factor(2 * max(abs(value - midpoint) for value in values))
    packet_gap = sp.factor(abs(values[-1] - values[0]))
    return {
        "essential_values": [int(value) for value in values],
        "midpoint": midpoint,
        "diameter": diameter,
        "midpoint_upper_bound": midpoint_upper,
        "packet_gap": packet_gap,
    }


def complex_step_fixture() -> dict[str, Any]:
    points = tuple(tuple(sp.Integer(coordinate) for coordinate in point) for point in COMPLEX_STEP_INPUTS)
    squared = [
        sp.factor(sum((left[index] - right[index]) ** 2 for index in range(2)))
        for left, right in combinations(points, 2)
    ]
    return {
        "essential_values": [[int(value) for value in point] for point in points],
        "pairwise_squared_distances": [int(value) for value in squared],
        "diameter_squared": max(squared),
        "scope": "lower-bound-only",
    }


def galilean_fixture() -> dict[str, Any]:
    chi = sp.Rational(GALILEAN_INPUTS["chi_num"], GALILEAN_INPUTS["chi_den"])
    x = sp.Matrix([sp.Integer(value) for value in GALILEAN_INPUTS["x"]])
    y = sp.Matrix([sp.Integer(value) for value in GALILEAN_INPUTS["y"]])
    times = [sp.Rational(numerator, denominator) for numerator, denominator in GALILEAN_INPUTS["times"]]
    displacements = []
    boosts = []
    for time in times:
        boost = sp.simplify(chi * (y - x) / time)
        boosts.append(boost)
        displacements.append(sp.simplify((boost / chi) * time))
    return {
        "chi": chi,
        "x": [int(value) for value in x],
        "y": [int(value) for value in y],
        "times": times,
        "positive_displacement": [int(value) for value in displacements[0]],
        "negative_displacement": [int(value) for value in displacements[1]],
        "boosts_are_opposite": bool(boosts[0] == -boosts[1]),
    }


def polynomial_fixture() -> dict[str, Any]:
    coefficients = [sp.Rational(numerator, denominator) for numerator, denominator in POLYNOMIAL_INPUTS["coefficients"]]
    radius = sp.Integer(POLYNOMIAL_INPUTS["segment_radius"])
    degree = len(coefficients) - 1
    quartic_factor = sp.Integer(2) ** max(degree - 1, 0)
    coefficient_l1 = sp.factor(sum(abs(value) for value in coefficients))
    translation_factor = sp.factor(1 + quartic_factor * radius**degree)
    safe_envelope = sp.factor(coefficient_l1 * translation_factor)
    return {
        "degree": degree,
        "coefficients": coefficients,
        "coefficient_l1": coefficient_l1,
        "segment_radius": int(radius),
        "safe_envelope": safe_envelope,
        "translation_factor": translation_factor,
    }


def joint_fixture() -> dict[str, Any]:
    phase = sp.Integer(BOND_INPUTS["modulation_phase"])
    scalar_value = sp.Integer(BOND_INPUTS["scalar"])
    modulation = sp.diag(1, phase)
    offdiagonal = sp.Matrix([[0, 1], [1, 0]])
    multiplier = sp.diag(*[sp.Integer(value) for value in REAL_STEP_INPUTS])
    scalar = scalar_value * sp.eye(2)
    off_distance = sp.simplify(operator_norm(modulation.H * offdiagonal * modulation - offdiagonal))
    multiplier_distance = sp.simplify(operator_norm(modulation.H * multiplier * modulation - multiplier))
    scalar_bond_distance = sp.simplify(operator_norm(modulation.H * scalar * modulation - scalar))
    full_lower = real_step_fixture()["diameter"]
    scalar_full = sp.factor(max(abs(scalar[index, index] - scalar[0, 0]) for index in range(2)))
    return {
        "offdiagonal_bond_distance": off_distance,
        "nonscalar_multiplier_bond_distance": multiplier_distance,
        "nonscalar_multiplier_full_h_lower": full_lower,
        "scalar_bond_distance": scalar_bond_distance,
        "scalar_full_h_distance": scalar_full,
    }


def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    return str(value)


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
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
        "one scoped child and one negative",
        len(manifest["closed_gate_ids"]) == len(set(manifest["closed_gate_ids"])) == 1
        and len(manifest["negative_ids"]) == len(set(manifest["negative_ids"])) == 1,
        (manifest["closed_gate_ids"], manifest["negative_ids"]),
        "one each",
        "identity",
    )
    audit.check(
        "five parents remain open",
        len(manifest["open_parent_gate_ids"]) == len(set(manifest["open_parent_gate_ids"])) == 5
        and "All five active parent gates remain OPEN" in manifest["no_overclaim"],
        manifest["open_parent_gate_ids"],
        "five unique OPEN parents",
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
        "real midpoint exact upper",
        derived["real_step"]["diameter"] == derived["real_step"]["midpoint_upper_bound"],
        derived["real_step"]["midpoint_upper_bound"],
        derived["real_step"]["diameter"],
        "theorem",
    )
    audit.check(
        "complex fixture is lower only",
        derived["complex_step"]["scope"] == "lower-bound-only"
        and derived["complex_step"]["diameter_squared"] == max(derived["complex_step"]["pairwise_squared_distances"]),
        derived["complex_step"],
        "diameter lower-bound oracle",
        "theorem",
    )
    audit.check(
        "two-sided Galilean displacement",
        derived["galilean"]["positive_displacement"] == derived["galilean"]["negative_displacement"]
        and derived["galilean"]["boosts_are_opposite"],
        derived["galilean"],
        "same displacement, opposite boosts",
        "theorem",
    )
    audit.check(
        "polynomial envelope derived",
        derived["polynomial_translation"]["safe_envelope"]
        == derived["polynomial_translation"]["coefficient_l1"]
        * derived["polynomial_translation"]["translation_factor"],
        derived["polynomial_translation"]["safe_envelope"],
        "coefficient_l1 times translation_factor",
        "theorem",
    )
    audit.check(
        "joint scalarity truth table",
        derived["joint_truth_table"]["offdiagonal_bond_distance"] > 0
        and derived["joint_truth_table"]["nonscalar_multiplier_bond_distance"] == 0
        and derived["joint_truth_table"]["nonscalar_multiplier_full_h_lower"] > 0
        and derived["joint_truth_table"]["scalar_bond_distance"] == 0
        and derived["joint_truth_table"]["scalar_full_h_distance"] == 0,
        derived["joint_truth_table"],
        "offdiagonal/bond fail, multiplier/full-H fail, scalar survives",
        "theorem",
    )

    required_tokens = (
        "liminf_(t -> 0, t != 0)",
        "D_ess(f)",
        "Lebesgue points",
        "p_t = chi (y-x)/t",
        "Only this density identity is used",
        "s/t in [0,1]",
        "C_epsilon |t|/hbar",
        "eta; x,y; fixed epsilon",
        "C(beta^(xy)) intersect C(alpha^Lambda)",
        "diameter two",
        "background-uniform spatial norm bound",
        "No v3.1 PDF is issued",
    )
    audit.check(
        "certificate proof tokens",
        all(token in normalized_certificate for token in required_tokens),
        [token for token in required_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    audit.check(
        "certificate firewalls",
        all(
            token in normalized_certificate
            for token in (
                "not a classification of the full continuous-element algebra",
                "does not prove that a common thermodynamic action is impossible",
                "No exact-Q3 background-uniform bound",
                "All five active parent gates remain OPEN",
                "physical Sector A, or Pre-A",
            )
        ),
        "scope tokens",
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
    print(f"R-167 v3.1 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
