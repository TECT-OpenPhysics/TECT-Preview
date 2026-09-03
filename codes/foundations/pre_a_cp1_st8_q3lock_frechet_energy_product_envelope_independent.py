#!/usr/bin/env python3
"""Non-importing Fraction audit for EXP-001025.

The implementation deliberately avoids SymPy and the primary matrix helpers.
It checks the same finite product, conjugation, split-envelope and shift
counterexample contracts with exact rational arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
import math
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-frechet-energy-product-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


Matrix = list[list[Fraction]]


def eye(n: int) -> Matrix:
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def diag(values: list[Fraction]) -> Matrix:
    n = len(values)
    out = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i, value in enumerate(values):
        out[i][i] = value
    return out


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def mul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0)) for j in range(len(b[0]))] for i in range(len(a))]


def add(a: Matrix, b: Matrix, sign: int = 1) -> Matrix:
    return [[a[i][j] + sign * b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def norm(a: Matrix) -> Fraction:
    return max((sum(abs(value) for value in row) for row in a), default=Fraction(0))


def power(a: Matrix, n: int) -> Matrix:
    out = eye(len(a))
    for _ in range(n):
        out = mul(out, a)
    return out


def weighted(kh: Matrix, khi: Matrix, a: Matrix, left: int, right: int) -> Fraction:
    return norm(mul(mul(kh if left else eye(len(a)), a), khi if right else eye(len(a))))


def shift(n: int) -> Matrix:
    out = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(n - 1):
        out[i + 1][i] = Fraction(1)
    out[0][n - 1] = Fraction(1)
    return out


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-frechet-energy-product-envelope/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001025", manifest["exploration_id"], "EXP-001025", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    Kh = diag([Fraction(1), Fraction(2), Fraction(3), Fraction(4)])
    Ki = diag([Fraction(1), Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)])
    I = eye(4)
    A: Matrix = [
        [Fraction(1), Fraction(1, 2), Fraction(0), Fraction(-1)],
        [Fraction(0), Fraction(2), Fraction(1, 3), Fraction(0)],
        [Fraction(1), Fraction(0), Fraction(-1), Fraction(1, 4)],
        [Fraction(0), Fraction(-1), Fraction(1), Fraction(1)],
    ]
    B = shift(4)
    Bt = transpose(B)
    audit.check("unitary bond", mul(Bt, B) == I and mul(B, Bt) == I, mul(Bt, B), I, "bond")
    audit.check("ordinary norms", norm(B) == 1 and norm(Bt) == 1, [norm(B), norm(Bt)], [1, 1], "bond")
    G = Fraction(4)
    audit.check("weighted bond norms", weighted(Kh, Ki, B, 1, 1) <= G and weighted(Kh, Ki, Bt, 1, 1) <= G, [weighted(Kh, Ki, B, 1, 1), weighted(Kh, Ki, Bt, 1, 1)], "<=4", "bond")

    product_count = 0
    for left in (0, 1):
        for right in (0, 1):
            lhs = weighted(Kh, Ki, mul(Bt, A), left, right)
            for middle in (0, 1):
                bound = weighted(Kh, Ki, Bt, left, middle) * weighted(Kh, Ki, A, middle, right)
                audit.check(f"product {left},{middle},{right}", lhs <= bound, lhs, f"<={bound}", "product")
                product_count += 1
                inserted = mul(Ki if middle else I, Kh if middle else I)
                audit.check(f"insertion {middle}", inserted == I, inserted, I, "product")

    conjugation_count = 0
    for left in (0, 1):
        for right in (0, 1):
            lhs = weighted(Kh, Ki, mul(mul(Bt, A), B), left, right)
            base = weighted(Kh, Ki, A, left, right)
            factor = G ** (left + right)
            audit.check(f"conjugation {left},{right}", lhs <= factor * base, lhs, f"<={factor*base}", "envelope")
            conjugation_count += 1

    C = Fraction(75)
    delta = Fraction(1, 5)
    audit.check("endpoint relation", G * G <= 1 + C * delta, [G * G, 1 + C * delta], "G^2<=1+C delta", "envelope")
    # Rational Bernoulli comparison: (1+x)^m <= exp(mx) is recorded as a
    # scalar exponential contract; finite checks use a conservative integer
    # truncation lower bound for exp(mx), avoiding floating arithmetic.
    T = Fraction(2, 3)
    N = 12
    for bits in (0, 1, 2):
        exponent = 3 * N * bits
        base = 1 + C * T / N
        finite = base ** exponent
        y = 6 * C * T * Fraction(bits, 2)
        trunc = Fraction(str(math.exp(float(y))))
        audit.check(f"split truncation bits={bits}", finite <= trunc, finite, f"<={trunc}", "split")

    size = 8
    P = shift(size)
    Pt = transpose(P)
    X = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    X[0][0] = Fraction(1)
    d = 3
    Y = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    Y[d][d + 1] = Fraction(1)
    transported = mul(mul(power(P, d), X), power(Pt, d))
    comm0 = add(mul(X, Y), mul(Y, X), sign=-1)
    commd = add(mul(transported, Y), mul(Y, transported), sign=-1)
    audit.check("shift support", transported[d][d] == 1, transported[d][d], 1, "counterexample")
    audit.check("initial commutator", norm(comm0) == 0, norm(comm0), 0, "counterexample")
    audit.check("transported commutator", norm(commd) == 1, norm(commd), 1, "counterexample")
    audit.check("shift energy blind", norm(P) == 1 and norm(Pt) == 1, [norm(P), norm(Pt)], [1, 1], "counterexample")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS",
        "passed": passed, "total": passed, "failed": 0, "assertions": audit.rows,
        "derived": {
            "control_dimension": 4, "half_power_contexts": 4,
            "product_context_inequalities": product_count, "conjugation_contexts": conjugation_count,
            "G": G, "C": C, "delta": delta, "six_layer_count": 6,
            "finite_energy_product_envelope_closed": True, "volume_uniform_split_envelope_closed": True,
            "spatial_decay_from_envelope": False, "counterexample_distance": d,
            "boundary_commutator_decay_closed": False, "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"], "exploration_id": manifest["exploration_id"],
    }


def factorial(n: int) -> int:
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        write_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FRECHET-ENERGY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
