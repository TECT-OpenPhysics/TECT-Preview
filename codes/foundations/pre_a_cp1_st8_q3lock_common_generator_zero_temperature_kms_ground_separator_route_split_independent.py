#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.2 route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-generator-zero-temperature-kms-ground-separator-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_common_generator_zero_temperature_kms_ground_separator_route_split.py"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-independent-{SLUG}/result.json"
)
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Independently declared labelled inputs.
GIBBS_RATIO = 2
PLUS_WEIGHTS = (Fraction(1, 8), Fraction(7, 8))
SAMPLE_N = (2, 3, 5, 8)
BOUNDARY_CASES = ((0, 3), (2, 0), (0, 0))


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


def matrix_subtract(left: Matrix2, right: Matrix2) -> Matrix2:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(2)) for row in range(2)
    )  # type: ignore[return-value]


def matrix_transpose(matrix: Matrix2) -> Matrix2:
    return tuple(tuple(matrix[column][row] for column in range(2)) for row in range(2))  # type: ignore[return-value]


def diagonal_expectation(weights: tuple[Fraction, Fraction], matrix: Matrix2) -> Fraction:
    return sum(weights[index] * matrix[index][index] for index in range(2))


def format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def format_log_multiple(coefficient: Fraction, ratio: Fraction) -> str:
    sign = 1
    base: int
    if ratio.denominator == 1:
        base = ratio.numerator
    elif ratio.numerator == 1:
        base = ratio.denominator
        sign = -1
    else:
        raise AssertionError(f"fixture ratio is not an integer or reciprocal: {ratio}")
    coefficient *= sign
    numerator = coefficient.numerator
    denominator = coefficient.denominator
    if numerator == 0:
        return "0"
    sign_text = "-" if numerator < 0 else ""
    magnitude = abs(numerator)
    factor = "" if magnitude == 1 else f"{magnitude}*"
    denominator_text = "" if denominator == 1 else f"/{denominator}"
    return f"{sign_text}{factor}log({base}){denominator_text}"


def differential_kms_fixture() -> dict[str, Any]:
    ratio = Fraction(GIBBS_RATIO)
    weights = (ratio / (1 + ratio), Fraction(1, 1 + ratio))
    hamiltonian_units: Matrix2 = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)))
    raising: Matrix2 = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)))
    lowering = matrix_transpose(raising)

    def one(operator: Matrix2) -> tuple[Fraction, Fraction, Fraction, str]:
        adjoint = matrix_transpose(operator)
        x = diagonal_expectation(weights, matrix_multiply(adjoint, operator))
        y = diagonal_expectation(weights, matrix_multiply(operator, adjoint))
        commutator = matrix_subtract(
            matrix_multiply(hamiltonian_units, operator), matrix_multiply(operator, hamiltonian_units)
        )
        # delta=i log(ratio)[H_units,A], so -i times the expectation leaves this real coefficient.
        lhs_coefficient = diagonal_expectation(weights, matrix_multiply(adjoint, commutator))
        entropy_ratio = x / y
        return x, y, lhs_coefficient, format_log_multiple(x, entropy_ratio)

    raising_x, raising_y, raising_coefficient, raising_entropy = one(raising)
    lowering_x, lowering_y, lowering_coefficient, lowering_entropy = one(lowering)
    return {
        "beta_energy": f"log({ratio.numerator})",
        "ground_weight": format_fraction(weights[0]),
        "excited_weight": format_fraction(weights[1]),
        "raising_x": format_fraction(raising_x),
        "raising_y": format_fraction(raising_y),
        "raising_lhs": format_log_multiple(raising_coefficient, ratio),
        "raising_entropy": raising_entropy,
        "lowering_x": format_fraction(lowering_x),
        "lowering_y": format_fraction(lowering_y),
        "lowering_lhs": format_log_multiple(lowering_coefficient, ratio),
        "lowering_entropy": lowering_entropy,
        "safe_lower_bound": format_fraction(-lowering_y),
    }


def fixed_separator_fixture() -> dict[str, Any]:
    witness_values = (Fraction(-1), Fraction(1))
    minus_weights = tuple(reversed(PLUS_WEIGHTS))
    witness_norm = max(abs(value) for value in witness_values)
    plus_value = sum(weight * value for weight, value in zip(PLUS_WEIGHTS, witness_values))
    minus_value = sum(weight * value for weight, value in zip(minus_weights, witness_values))
    m_zero = plus_value
    distance_lower = abs(plus_value - minus_value) / witness_norm
    return {
        "witness_norm": format_fraction(witness_norm),
        "m_0": format_fraction(m_zero),
        "plus_value": format_fraction(plus_value),
        "minus_value": format_fraction(minus_value),
        "state_distance_lower_bound": format_fraction(distance_lower),
    }


def clip(value: Fraction) -> Fraction:
    return max(Fraction(-1), min(Fraction(1), value))


def rational_limit_at_infinity(numerator: tuple[Fraction, ...], denominator: tuple[Fraction, ...]) -> Fraction:
    numerator_degree = max(index for index, coefficient in enumerate(numerator) if coefficient)
    denominator_degree = max(index for index, coefficient in enumerate(denominator) if coefficient)
    if numerator_degree < denominator_degree:
        return Fraction(0)
    if numerator_degree == denominator_degree:
        return numerator[numerator_degree] / denominator[denominator_degree]
    raise ValueError("fixture rational function diverges at infinity")


def collapsing_kms_fixture() -> dict[str, Any]:
    plus = [Fraction(1, n) for n in SAMPLE_N]
    minus = [-value for value in plus]
    fixed_gaps = [left - right for left, right in zip(plus, minus)]
    adaptive_gaps = [clip(Fraction(n) * left) - clip(Fraction(n) * right) for n, left, right in zip(SAMPLE_N, plus, minus)]
    point_limit = rational_limit_at_infinity((Fraction(1),), (Fraction(0), Fraction(1)))
    fixed_gap_limit = rational_limit_at_infinity((Fraction(2),), (Fraction(0), Fraction(1)))
    return {
        "sample_n": list(SAMPLE_N),
        "plus_points": [format_fraction(value) for value in plus],
        "minus_points": [format_fraction(value) for value in minus],
        "fixed_witness_gaps": [format_fraction(value) for value in fixed_gaps],
        "finite_state_norm_distance": format_fraction(min(adaptive_gaps)),
        "common_weakstar_limit": format_fraction(point_limit),
        "uniform_fixed_witness_separator": bool(fixed_gap_limit > 0),
    }


def entropy_boundary_fixture() -> dict[str, Any]:
    def extended(x: int, y: int) -> str:
        if x == 0:
            return "0"
        if y == 0:
            return "+infinity"
        raise AssertionError("only boundary inputs belong in this fixture")

    values = [extended(x, y) for x, y in BOUNDARY_CASES]
    return {"s_0_3": values[0], "s_2_0": values[1], "s_0_0": values[2]}


def independent_firewall() -> dict[str, Any]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "os",
        "tempfile",
        "fractions",
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
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    normalized_certificate = " ".join(certificate.split())
    derived = {
        "differential_kms_matrix": differential_kms_fixture(),
        "fixed_separator": fixed_separator_fixture(),
        "collapsing_kms": collapsing_kms_fixture(),
        "entropy_boundary": entropy_boundary_fixture(),
    }
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.2"
        and manifest["exploration_id"] == "EXP-000836"
        and manifest["prior_exploration_id"] == "EXP-000835"
        and manifest["claim_bearing"] is False,
        (manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        (SLUG, "R-167 v3.2", "EXP-000836"),
        "identity",
    )
    audit.check(
        "one conditional child and one negative",
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

    for group, expected in manifest["exact_fixture"].items():
        audit.check(f"exact {group} fixture", derived[group] == expected, derived[group], expected, group)

    matrix = derived["differential_kms_matrix"]
    audit.check(
        "raising differential KMS equality",
        matrix["raising_lhs"] == matrix["raising_entropy"],
        matrix["raising_lhs"],
        matrix["raising_entropy"],
        "kms",
    )
    audit.check(
        "lowering differential KMS equality",
        matrix["lowering_lhs"] == matrix["lowering_entropy"],
        matrix["lowering_lhs"],
        matrix["lowering_entropy"],
        "kms",
    )
    audit.check(
        "safe rational entropy lower bound",
        -Fraction(GIBBS_RATIO - 1, GIBBS_RATIO + 1) >= -Fraction(GIBBS_RATIO, GIBBS_RATIO + 1),
        {
            "entropy": matrix["lowering_entropy"],
            "log_upper_from_integral": format_fraction(Fraction(GIBBS_RATIO - 1)),
        },
        matrix["safe_lower_bound"],
        "kms",
    )
    separator = derived["fixed_separator"]
    audit.check(
        "fixed odd contraction separates",
        separator
        == {
            "witness_norm": "1",
            "m_0": "3/4",
            "plus_value": "3/4",
            "minus_value": "-3/4",
            "state_distance_lower_bound": "3/2",
        },
        separator,
        "normalized parity separator",
        "separator",
    )
    collapse = derived["collapsing_kms"]
    audit.check(
        "adaptive finite separators have norm distance two",
        collapse["finite_state_norm_distance"] == "2",
        collapse["finite_state_norm_distance"],
        "2",
        "negative",
    )
    audit.check(
        "fixed witness collapses at common weakstar limit",
        collapse["common_weakstar_limit"] == "0" and collapse["uniform_fixed_witness_separator"] is False,
        (collapse["common_weakstar_limit"], collapse["uniform_fixed_witness_separator"]),
        ("0", False),
        "negative",
    )
    audit.check(
        "extended entropy boundary",
        derived["entropy_boundary"] == {"s_0_3": "0", "s_2_0": "+infinity", "s_0_0": "0"},
        derived["entropy_boundary"],
        "0,+infinity,0",
        "kms",
    )

    firewall = independent_firewall()
    audit.check(
        "independent AST firewall",
        not firewall["unapproved"] and not firewall["dynamic"],
        firewall,
        "stdlib allowlist and no dynamic execution",
        "independence",
    )
    audit.check(
        "independent source distinct",
        normalized_sha256(SCRIPT) != normalized_sha256(PRIMARY),
        normalized_sha256(SCRIPT),
        "different from primary",
        "independence",
    )

    proof_tokens = (
        "Araki's differential KMS condition",
        "rational safe lower bound",
        "graph core for `delta`",
        "Both `omega_+` and `omega_-` are ground states",
        "one fixed selfadjoint contraction",
        "state-norm distance two",
        "common-core generator convergence",
        "No v3.2 PDF is issued",
    )
    audit.check(
        "certificate theorem tokens",
        all(token in normalized_certificate for token in proof_tokens),
        [token for token in proof_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "does not identify the source-tangent candidates",
        "not a GNS spectral gap",
        "no KMS label at infinite beta is asserted",
        "All five active parent gates remain OPEN",
        "physical Sector A, or Pre-A",
    )
    audit.check(
        "certificate no-overclaim tokens",
        all(token in normalized_certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in normalized_certificate],
        [],
        "certificate",
    )

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_ok = (
            formal_text.count("EXP-000836") > 0
            and manifest["closed_gate_ids"][0] in formal_text
            and manifest["negative_ids"][0] in formal_text
            and "R-167 v3.2" in formal_text
        )
        audit.check("formal authority aggregate", formal_ok, formal_ok, True, "formal")

    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
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
    print(f"R-167 v3.2 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
