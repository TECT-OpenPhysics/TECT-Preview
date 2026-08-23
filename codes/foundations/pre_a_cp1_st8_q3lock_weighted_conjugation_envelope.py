#!/usr/bin/env python3
"""Primary exact audit for the finite weighted-conjugation envelope fixture.

This is a claim-nonbearing QFT/common-alpha subgate audit.  It checks the
algebraic envelope on an exact rational three-dimensional fixture and records
the omitted-orientation failure.  It does not prove a thermodynamic limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-weighted-conjugation-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-24-primary-{SLUG}"
    / "primary.json"
)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[json_safe(item) for item in value.row(i)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def determinant(matrix: sp.Matrix) -> sp.Expr:
    return sp.factor(matrix.det())


def principal_minors(matrix: sp.Matrix) -> list[sp.Expr]:
    from itertools import combinations

    output: list[sp.Expr] = []
    for size in range(1, matrix.rows + 1):
        for indices in combinations(range(matrix.rows), size):
            output.append(determinant(matrix.extract(indices, indices)))
    return output


def psd_by_principal_minors(matrix: sp.Matrix) -> bool:
    return all(bool(value >= 0) for value in principal_minors(matrix))


def frobenius_sq(matrix: sp.Matrix) -> sp.Expr:
    return sp.factor(sum(entry * entry for entry in matrix))


def max_symmetric_norm_sq(matrix: sp.Matrix, S: sp.Matrix, R: sp.Matrix) -> sp.Expr:
    transform = lambda item: S * item * R
    return max(frobenius_sq(matrix), frobenius_sq(transform(matrix)), frobenius_sq(transform(matrix.T)))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def run_audit() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/1.0", manifest["schema"], "tect/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001023", manifest["exploration_id"], "EXP-001023", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim context", manifest["claim_id"] == "C6-SPACETIME-SIGNATURE", manifest["claim_id"], "C6-SPACETIME-SIGNATURE", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("Lean theorem boundary", manifest["lean_crosscheck"]["proposition"] == "conjugation multiplication and inverse identities", manifest["lean_crosscheck"]["proposition"], "conjugation multiplication and inverse identities", "scope")

    # Exact positive fixture.  K=S^2 and R=S^{-1}; all entries are rational.
    S = sp.diag(1, 2, 3)
    R = sp.diag(1, sp.Rational(1, 2), sp.Rational(1, 3))
    K = S * S
    U1 = sp.Matrix(
        [
            [sp.Rational(3, 5), -sp.Rational(4, 5), 0],
            [sp.Rational(4, 5), sp.Rational(3, 5), 0],
            [0, 0, 1],
        ]
    )
    U2 = sp.Matrix(
        [
            [1, 0, 0],
            [0, sp.Rational(3, 5), -sp.Rational(4, 5)],
            [0, sp.Rational(4, 5), sp.Rational(3, 5)],
        ]
    )
    U = U1 * U2
    identity = sp.eye(3)
    transform = lambda A: S * A * R
    inverse_transform = lambda A: R * A * S
    beta = lambda A: U.T * A * U
    audit.check("K positive diagonal", K == sp.diag(1, 4, 9), K, sp.diag(1, 4, 9), "fixture")
    audit.check("S inverse", S * R == identity and R * S == identity, [S * R, R * S], [identity, identity], "fixture")
    audit.check("U orthogonal", U.T * U == identity and U * U.T == identity, [U.T * U, U * U.T], [identity, identity], "fixture")

    # The two form inequalities are the finite-dimensional hypotheses.
    left_form = U.T * K * U
    right_form = U * K * U.T
    M_left = sp.Integer(4)
    M_common = sp.Integer(6)
    left_margin = M_left * K - left_form
    right_margin_common = M_common * K - right_form
    audit.check("left form bound", psd_by_principal_minors(left_margin), principal_minors(left_margin), ">=0", "two_orientation")
    audit.check("right form bound at common M", psd_by_principal_minors(right_margin_common), principal_minors(right_margin_common), ">=0", "two_orientation")
    audit.check("common M dominates left", psd_by_principal_minors(M_common * K - left_form), principal_minors(M_common * K - left_form), ">=0", "two_orientation")

    T_U = transform(U)
    T_U_star = transform(U.T)
    audit.check("weighted U Gram bound", psd_by_principal_minors(M_common * identity - T_U.T * T_U), principal_minors(M_common * identity - T_U.T * T_U), ">=0", "two_orientation")
    audit.check("weighted U-star Gram bound", psd_by_principal_minors(M_common * identity - T_U_star.T * T_U_star), principal_minors(M_common * identity - T_U_star.T * T_U_star), ">=0", "two_orientation")

    a_symbols = sp.symbols("a0:9")
    b_symbols = sp.symbols("b0:9")
    A_symbol = sp.Matrix(3, 3, a_symbols)
    B_symbol = sp.Matrix(3, 3, b_symbols)
    audit.check("generic conjugation multiplication", sp.simplify(transform(A_symbol * B_symbol) - transform(A_symbol) * transform(B_symbol)) == sp.zeros(3), "zero matrix", "zero matrix", "algebra")
    audit.check("generic inverse conjugation", sp.simplify(inverse_transform(transform(A_symbol)) - A_symbol) == sp.zeros(3), "zero matrix", "zero matrix", "algebra")
    audit.check("beta transport identity", sp.simplify(transform(beta(A_symbol)) - transform(U.T) * transform(A_symbol) * transform(U)) == sp.zeros(3), "zero matrix", "zero matrix", "algebra")
    audit.check("star transport identity", sp.simplify(beta(A_symbol).T - beta(A_symbol.T)) == sp.zeros(3), "zero matrix", "zero matrix", "algebra")

    fixtures = [
        sp.eye(3),
        sp.Matrix([[1, 2, -1], [0, 3, 4], [2, -2, 1]]),
        sp.Matrix([[sp.Rational(1, 2), -2, 3], [4, 0, sp.Rational(3, 2)], [-1, 5, 2]]),
    ]
    norm_rows: list[dict[str, Any]] = []
    for index, fixture in enumerate(fixtures):
        before = max_symmetric_norm_sq(fixture, S, R)
        after = max_symmetric_norm_sq(beta(fixture), S, R)
        direct = frobenius_sq(transform(beta(fixture)))
        source = frobenius_sq(transform(fixture))
        audit.check(f"symmetric envelope fixture {index}", after <= M_common**2 * before, after, f"<={M_common**2}*before", "envelope")
        audit.check(f"transported component fixture {index}", direct <= M_common**2 * source, [direct, source], f"direct<={M_common**2}*source", "envelope")
        audit.check(f"unweighted orthogonal fixture {index}", frobenius_sq(beta(fixture)) == frobenius_sq(fixture), frobenius_sq(beta(fixture)), frobenius_sq(fixture), "envelope")
        norm_rows.append({"index": index, "before_sq": before, "after_sq": after, "direct_sq": direct, "source_sq": source})

    # The bound composes over products.  The exponential comparison is scalar;
    # it is not a thermodynamic limit statement.
    C = sp.Rational(3, 2)
    deltas = [sp.Rational(1, 4), sp.Rational(1, 5), sp.Rational(1, 7)]
    factors = [1 + C * delta for delta in deltas]
    product_factor = sp.prod(factors)
    exponential_rhs = math.exp(float(C * sum(deltas)))
    audit.check("product factors positive", all(factor > 0 for factor in factors), factors, ">0", "product")
    audit.check("product exponential envelope", float(product_factor) <= exponential_rhs + 1e-14, [product_factor, exponential_rhs], "product<=exp(C sum|delta|)", "product")
    product_rows: list[dict[str, Any]] = []
    for length in (1, 2, 3):
        bound = M_common**length
        for index, fixture in enumerate(fixtures):
            current = fixture
            for _ in range(length):
                current = beta(current)
            audit.check(f"iterated envelope n={length} fixture={index}", max_symmetric_norm_sq(current, S, R) <= bound**2 * max_symmetric_norm_sq(fixture, S, R), max_symmetric_norm_sq(current, S, R), f"<={bound**2}*before", "product")
        product_rows.append({"length": length, "bound": bound})

    # Dropping the reverse orientation is not harmless on this nonnormal
    # weighted transport: the (0,0) principal witness is strictly negative.
    omitted_margin = M_left * K - right_form
    audit.check("omitted reverse orientation fails", omitted_margin[0, 0] == -sp.Rational(121, 125), omitted_margin[0, 0], -sp.Rational(121, 125), "adversarial")
    audit.check("omitted reverse witness is negative", omitted_margin[0, 0] < 0, omitted_margin[0, 0], "<0", "adversarial")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "S": S,
            "R": R,
            "K": K,
            "U": U,
            "left_form": left_form,
            "right_form": right_form,
            "M_left": M_left,
            "M_common": M_common,
            "norm_rows": norm_rows,
            "C": C,
            "deltas": deltas,
            "factors": factors,
            "product_factor": product_factor,
            "exponential_rhs": exponential_rhs,
            "product_rows": product_rows,
            "weighted_conjugation_closed": True,
            "finite_two_orientation_fixture_closed": True,
            "thermodynamic_common_alpha_closed": False,
            "qft_kms_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": normalized_sha256(MANIFEST),
        },
        "boundary": manifest["boundary"],
        "exploration_id": manifest["exploration_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run_audit()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY WEIGHTED-CONJUGATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
