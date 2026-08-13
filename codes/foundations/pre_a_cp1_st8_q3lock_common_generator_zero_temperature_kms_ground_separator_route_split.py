#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.2 route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-generator-zero-temperature-kms-ground-separator-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-13-primary-{SLUG}/result.json"
)
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Labelled oracle inputs. All reported quantities are derived below.
GIBBS_RATIO_INPUT = 2
SEPARATOR_PLUS_WEIGHTS = (sp.Rational(1, 8), sp.Rational(7, 8))
COLLAPSE_SAMPLE_N = (2, 3, 5, 8)
ENTROPY_BOUNDARY_INPUTS = ((0, 3), (2, 0), (0, 0))


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


def expectation(density: sp.Matrix, observable: sp.Matrix) -> sp.Expr:
    return sp.simplify(sp.trace(density * observable))


def generator(hamiltonian: sp.Matrix, observable: sp.Matrix) -> sp.Matrix:
    # hbar=1 in this dimensionless exact fixture.
    return sp.simplify(sp.I * (hamiltonian * observable - observable * hamiltonian))


def entropy(x: sp.Expr, y: sp.Expr) -> sp.Expr:
    if x == 0:
        return sp.Integer(0)
    if y == 0:
        return sp.oo
    return sp.simplify(x * sp.log(x / y))


def differential_kms_fixture() -> dict[str, Any]:
    ratio = sp.Integer(GIBBS_RATIO_INPUT)
    beta_energy = sp.log(ratio)
    ground_weight = sp.simplify(ratio / (1 + ratio))
    excited_weight = sp.simplify(1 / (1 + ratio))
    density = sp.diag(ground_weight, excited_weight)
    hamiltonian = sp.diag(0, beta_energy)
    raising = sp.Matrix([[0, 0], [1, 0]])
    lowering = raising.H

    def one(operator: sp.Matrix) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
        x = expectation(density, operator.H * operator)
        y = expectation(density, operator * operator.H)
        lhs = sp.simplify(-sp.I * expectation(density, operator.H * generator(hamiltonian, operator)))
        return x, y, lhs, entropy(x, y)

    raising_x, raising_y, raising_lhs, raising_entropy = one(raising)
    lowering_x, lowering_y, lowering_lhs, lowering_entropy = one(lowering)
    return {
        "beta_energy": beta_energy,
        "ground_weight": ground_weight,
        "excited_weight": excited_weight,
        "raising_x": raising_x,
        "raising_y": raising_y,
        "raising_lhs": raising_lhs,
        "raising_entropy": raising_entropy,
        "lowering_x": lowering_x,
        "lowering_y": lowering_y,
        "lowering_lhs": lowering_lhs,
        "lowering_entropy": lowering_entropy,
        "safe_lower_bound": -lowering_y,
    }


def fixed_separator_fixture() -> dict[str, Any]:
    witness = sp.diag(-1, 1)
    plus_density = sp.diag(*SEPARATOR_PLUS_WEIGHTS)
    minus_density = sp.diag(*reversed(SEPARATOR_PLUS_WEIGHTS))
    witness_norm = max(abs(value) for value in witness.diagonal())
    plus_value = expectation(plus_density, witness)
    minus_value = expectation(minus_density, witness)
    m_zero = sp.simplify(plus_value)
    distance_lower = sp.simplify(abs(plus_value - minus_value) / witness_norm)
    return {
        "witness_norm": witness_norm,
        "m_0": m_zero,
        "plus_value": plus_value,
        "minus_value": minus_value,
        "state_distance_lower_bound": distance_lower,
    }


def clip(value: sp.Rational) -> sp.Rational:
    return max(sp.Rational(-1), min(sp.Rational(1), value))


def collapsing_kms_fixture() -> dict[str, Any]:
    sample = tuple(int(value) for value in COLLAPSE_SAMPLE_N)
    plus = [sp.Rational(1, value) for value in sample]
    minus = [-value for value in plus]
    fixed_gaps = [sp.simplify(left - right) for left, right in zip(plus, minus)]
    adaptive_gaps = [
        sp.simplify(clip(sp.Integer(n) * left) - clip(sp.Integer(n) * right))
        for n, left, right in zip(sample, plus, minus)
    ]
    symbolic_n = sp.symbols("n", positive=True, integer=True)
    common_limit = sp.limit(1 / symbolic_n, symbolic_n, sp.oo)
    fixed_gap_limit = sp.limit(2 / symbolic_n, symbolic_n, sp.oo)
    return {
        "sample_n": list(sample),
        "plus_points": plus,
        "minus_points": minus,
        "fixed_witness_gaps": fixed_gaps,
        "finite_state_norm_distance": min(adaptive_gaps),
        "common_weakstar_limit": common_limit,
        "uniform_fixed_witness_separator": bool(fixed_gap_limit > 0),
    }


def entropy_boundary_fixture() -> dict[str, Any]:
    values = [entropy(sp.Integer(x), sp.Integer(y)) for x, y in ENTROPY_BOUNDARY_INPUTS]
    return {"s_0_3": values[0], "s_2_0": values[1], "s_0_0": values[2]}


def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    if value == sp.oo:
        return "+infinity"
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    return str(value)


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

    serialized = stringify(derived)
    for group, expected in manifest["exact_fixture"].items():
        audit.check(f"exact {group} fixture", serialized[group] == expected, serialized[group], expected, group)

    matrix = derived["differential_kms_matrix"]
    audit.check(
        "raising differential KMS equality",
        sp.simplify(matrix["raising_lhs"] - matrix["raising_entropy"]) == 0,
        matrix["raising_lhs"],
        matrix["raising_entropy"],
        "kms",
    )
    audit.check(
        "lowering differential KMS equality",
        sp.simplify(matrix["lowering_lhs"] - matrix["lowering_entropy"]) == 0,
        matrix["lowering_lhs"],
        matrix["lowering_entropy"],
        "kms",
    )
    audit.check(
        "safe rational entropy lower bound",
        bool(matrix["lowering_entropy"] >= matrix["safe_lower_bound"]),
        matrix["lowering_entropy"],
        matrix["safe_lower_bound"],
        "kms",
    )
    separator = derived["fixed_separator"]
    audit.check(
        "fixed odd contraction separates",
        separator["witness_norm"] <= 1
        and separator["plus_value"] == -separator["minus_value"] == separator["m_0"]
        and separator["state_distance_lower_bound"] == 2 * separator["m_0"],
        separator,
        "normalized parity separator",
        "separator",
    )
    collapse = derived["collapsing_kms"]
    audit.check(
        "adaptive finite separators have norm distance two",
        collapse["finite_state_norm_distance"] == 2,
        collapse["finite_state_norm_distance"],
        2,
        "negative",
    )
    audit.check(
        "fixed witness collapses at common weakstar limit",
        collapse["common_weakstar_limit"] == 0 and collapse["uniform_fixed_witness_separator"] is False,
        (collapse["common_weakstar_limit"], collapse["uniform_fixed_witness_separator"]),
        (0, False),
        "negative",
    )
    boundary = derived["entropy_boundary"]
    audit.check(
        "extended entropy boundary",
        boundary == {"s_0_3": 0, "s_2_0": sp.oo, "s_0_0": 0},
        boundary,
        "0,+infinity,0",
        "kms",
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
    print(f"R-167 v3.2 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
