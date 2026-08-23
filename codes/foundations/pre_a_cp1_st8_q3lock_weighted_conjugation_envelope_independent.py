#!/usr/bin/env python3
"""Standard-library independent audit for the weighted-conjugation fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-24-primary-pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


Matrix = tuple[tuple[F, ...], ...]


def mat(rows: list[list[Any]]) -> Matrix:
    return tuple(tuple(item if isinstance(item, F) else F(item) for item in row) for row in rows)


def eye(n: int) -> Matrix:
    return tuple(tuple(F(int(i == j)) for j in range(n)) for i in range(n))


def transpose(a: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] for i in range(len(a))) for j in range(len(a)))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))) for i in range(len(a)))


def subtract(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] - b[i][j] for j in range(len(a[0]))) for i in range(len(a)))


def scale(c: F, a: Matrix) -> Matrix:
    return tuple(tuple(c * entry for entry in row) for row in a)


def determinant(a: Matrix) -> F:
    n = len(a)
    if n == 1:
        return a[0][0]
    if n == 2:
        return a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return sum((F((-1) ** j) * a[0][j] * determinant(tuple(tuple(a[i][k] for k in range(n) if k != j) for i in range(1, n))) for j in range(n)), F(0))


def principal_minors(a: Matrix) -> list[F]:
    out: list[F] = []
    for size in range(1, len(a) + 1):
        for indices in combinations(range(len(a)), size):
            out.append(determinant(tuple(tuple(a[i][j] for j in indices) for i in indices)))
    return out


def psd(a: Matrix) -> bool:
    return all(value >= 0 for value in principal_minors(a))


def fro_sq(a: Matrix) -> F:
    return sum((entry * entry for row in a for entry in row), F(0))


def transform(s: Matrix, r: Matrix, a: Matrix) -> Matrix:
    return multiply(multiply(s, a), r)


def symmetric_norm_sq(s: Matrix, r: Matrix, a: Matrix) -> F:
    return max(fro_sq(a), fro_sq(transform(s, r, a)), fro_sq(transform(s, r, transpose(a))))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        rows.append({"name": name, "group": group, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/1.0", manifest["schema"], "tect/pre-a-cp1-st8-q3lock-weighted-conjugation-envelope/1.0", "provenance")
    check("exploration", manifest["exploration_id"] == "EXP-001023", manifest["exploration_id"], "EXP-001023", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    source_lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    has_sympy_import = any(line.strip().startswith(("import sympy", "from sympy")) for line in source_lines)
    check("independent source policy", not has_sympy_import, has_sympy_import, False, "scope")

    S = mat([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
    R = mat([[1, 0, 0], [0, F(1, 2), 0], [0, 0, F(1, 3)]])
    K = multiply(S, S)
    U1 = mat([[F(3, 5), F(-4, 5), 0], [F(4, 5), F(3, 5), 0], [0, 0, 1]])
    U2 = mat([[1, 0, 0], [0, F(3, 5), F(-4, 5)], [0, F(4, 5), F(3, 5)]])
    U = multiply(U1, U2)
    I = eye(3)
    beta = lambda a: multiply(multiply(transpose(U), a), U)
    transform_local = lambda a: transform(S, R, a)
    inverse_transform = lambda a: transform(R, S, a)
    check("K fixture", K == mat([[1, 0, 0], [0, 4, 0], [0, 0, 9]]), K, "diag(1,4,9)", "fixture")
    check("S and R inverse", multiply(S, R) == I and multiply(R, S) == I, [multiply(S, R), multiply(R, S)], [I, I], "fixture")
    check("U orthogonal", multiply(transpose(U), U) == I and multiply(U, transpose(U)) == I, [multiply(transpose(U), U), multiply(U, transpose(U))], [I, I], "fixture")

    left = multiply(multiply(transpose(U), K), U)
    right = multiply(multiply(U, K), transpose(U))
    M_left = F(4)
    M_common = F(6)
    check("left form PSD", psd(subtract(scale(M_left, K), left)), principal_minors(subtract(scale(M_left, K), left)), ">=0", "two_orientation")
    check("right form PSD common", psd(subtract(scale(M_common, K), right)), principal_minors(subtract(scale(M_common, K), right)), ">=0", "two_orientation")
    T_U = transform_local(U)
    T_U_star = transform_local(transpose(U))
    check("weighted U Gram PSD", psd(subtract(scale(M_common, I), multiply(transpose(T_U), T_U))), principal_minors(subtract(scale(M_common, I), multiply(transpose(T_U), T_U))), ">=0", "two_orientation")
    check("weighted U-star Gram PSD", psd(subtract(scale(M_common, I), multiply(transpose(T_U_star), T_U_star))), principal_minors(subtract(scale(M_common, I), multiply(transpose(T_U_star), T_U_star))), ">=0", "two_orientation")

    fixtures = [
        I,
        mat([[1, 2, -1], [0, 3, 4], [2, -2, 1]]),
        mat([[F(1, 2), -2, 3], [4, 0, F(3, 2)], [-1, 5, 2]]),
    ]
    norm_rows: list[dict[str, Any]] = []
    for index, fixture in enumerate(fixtures):
        before = symmetric_norm_sq(S, R, fixture)
        after = symmetric_norm_sq(S, R, beta(fixture))
        direct = fro_sq(transform_local(beta(fixture)))
        source = fro_sq(transform_local(fixture))
        check(f"symmetric envelope fixture {index}", after <= M_common**2 * before, after, f"<={M_common**2}*before", "envelope")
        check(f"transported component fixture {index}", direct <= M_common**2 * source, [direct, source], f"direct<={M_common**2}*source", "envelope")
        check(f"unweighted orthogonal fixture {index}", fro_sq(beta(fixture)) == fro_sq(fixture), fro_sq(beta(fixture)), fro_sq(fixture), "envelope")
        norm_rows.append({"index": index, "before_sq": before, "after_sq": after, "direct_sq": direct, "source_sq": source})

    C = F(3, 2)
    deltas = [F(1, 4), F(1, 5), F(1, 7)]
    factors = [1 + C * delta for delta in deltas]
    product_factor = math.prod(factors)
    check("product factors positive", all(factor > 0 for factor in factors), factors, ">0", "product")
    check("product exponential envelope", float(product_factor) <= math.exp(float(C * sum(deltas))) + 1e-14, [product_factor, math.exp(float(C * sum(deltas)))], "product<=exp(C sum|delta|)", "product")

    for length in (1, 2, 3):
        bound = M_common**length
        for index, fixture in enumerate(fixtures):
            current = fixture
            for _ in range(length):
                current = beta(current)
            check(f"iterated envelope n={length} fixture={index}", symmetric_norm_sq(S, R, current) <= bound**2 * symmetric_norm_sq(S, R, fixture), symmetric_norm_sq(S, R, current), f"<={bound**2}*before", "product")

    omitted = subtract(scale(M_left, K), right)
    check("omitted reverse orientation fails", omitted[0][0] == F(-121, 125), omitted[0][0], F(-121, 125), "adversarial")
    check("omitted reverse witness negative", omitted[0][0] < 0, omitted[0][0], "<0", "adversarial")
    check("inverse transport samples", all(inverse_transform(transform_local(fixture)) == fixture for fixture in fixtures), True, True, "algebra")
    check("beta transport samples", all(transform_local(beta(fixture)) == multiply(multiply(transform_local(transpose(U)), transform_local(fixture)), transform_local(U)) for fixture in fixtures), True, True, "algebra")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": len(rows),
        "total": len(rows),
        "failed": 0,
        "assertions": rows,
        "derived": {
            "M_left": M_left,
            "M_common": M_common,
            "norm_rows": norm_rows,
            "product_factor": product_factor,
            "weighted_conjugation_closed": True,
            "finite_two_orientation_fixture_closed": True,
            "thermodynamic_common_alpha_closed": False,
            "qft_kms_closed": False,
        },
        "provenance": {"script": str(Path(__file__).relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(Path(__file__)), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"],
        "exploration_id": manifest["exploration_id"],
    }
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT WEIGHTED-CONJUGATION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
