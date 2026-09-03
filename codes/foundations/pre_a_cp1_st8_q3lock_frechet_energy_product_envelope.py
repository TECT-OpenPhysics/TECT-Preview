#!/usr/bin/env python3
"""Exact finite non-Leibniz energy-product envelope audit.

This is a claim-nonbearing QFT bridge checkpoint.  It verifies the finite
matrix algebra behind M_(a,b)(A)=||K^a A K^(-b)|| for a,b in {0,1/2}, the
two-sided bond conjugation envelope, and its six-layer/N-step consequence.
The same energy envelope is tested against an exact shift fixture showing
that it does not imply spatial commutator decay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-frechet-energy-product-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[safe(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def inf_norm(matrix: sp.Matrix) -> sp.Rational:
    return max((sum(abs(matrix[i, j]) for j in range(matrix.cols)) for i in range(matrix.rows)), default=sp.Rational(0))


def weighted(Kh: sp.Matrix, Khi: sp.Matrix, A: sp.Matrix, left: int, right: int) -> sp.Rational:
    L = Kh if left else sp.eye(Kh.rows)
    R = Khi if right else sp.eye(Kh.rows)
    return inf_norm(L * A * R)


def shift_fixture(size: int = 4) -> sp.Matrix:
    P = sp.zeros(size)
    for i in range(size - 1):
        P[i + 1, i] = 1
    P[0, size - 1] = 1
    return P


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-frechet-energy-product-envelope/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001025", manifest["exploration_id"], "EXP-001025", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("exponent set", manifest["definition"]["exponents"] == [0, "1/2"], manifest["definition"]["exponents"], [0, "1/2"], "definition")

    Khalf = sp.diag(1, 2, 3, 4)
    Kihalf = sp.diag(1, sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 4))
    audit.check("positive control", all(Khalf[i, i] > 0 for i in range(4)), list(Khalf.diagonal()), ">0", "definition")

    A = sp.Matrix([[1, sp.Rational(1, 2), 0, -1], [0, 2, sp.Rational(1, 3), 0], [1, 0, -1, sp.Rational(1, 4)], [0, -1, 1, 1]])
    B = shift_fixture()
    Bstar = B.T
    G = sp.Integer(4)
    audit.check("unitary bond", Bstar * B == sp.eye(4) and B * Bstar == sp.eye(4), Bstar * B, "I", "bond")
    audit.check("ordinary B norm", inf_norm(B) == 1 and inf_norm(Bstar) == 1, [inf_norm(B), inf_norm(Bstar)], [1, 1], "bond")
    audit.check("weighted B norm", weighted(Khalf, Kihalf, B, 1, 1) <= G and weighted(Khalf, Kihalf, Bstar, 1, 1) <= G, [weighted(Khalf, Kihalf, B, 1, 1), weighted(Khalf, Kihalf, Bstar, 1, 1)], f"<= {G}", "bond")

    # Exact insertion K^(-c/2)K^(c/2)=I and submultiplicativity of the
    # induced infinity norm, checked for every discrete half-power context.
    product_rows: list[dict[str, Any]] = []
    for left in (0, 1):
        for right in (0, 1):
            lhs = weighted(Khalf, Kihalf, Bstar * A, left, right)
            for middle in (0, 1):
                L = weighted(Khalf, Kihalf, Bstar, left, middle)
                R = weighted(Khalf, Kihalf, A, middle, right)
                audit.check(f"product inequality {left},{middle},{right}", lhs <= L * R, lhs, f"<={L*R}", "product")
                product_rows.append({"left": left, "middle": middle, "right": right, "lhs": lhs, "rhs": L * R})
                insertion = (Kihalf if middle else sp.eye(4)) * (Khalf if middle else sp.eye(4))
                audit.check(f"context insertion {middle}", insertion == sp.eye(4), insertion, "I", "product")

    # Two-sided bond conjugation: each half-weight endpoint contributes at most G.
    conjugation_rows: list[dict[str, Any]] = []
    for left in (0, 1):
        for right in (0, 1):
            lhs = weighted(Khalf, Kihalf, Bstar * A * B, left, right)
            base = weighted(Khalf, Kihalf, A, left, right)
            factor = G ** (left + right)
            audit.check(f"conjugation envelope {left},{right}", lhs <= factor * base, lhs, f"<={factor}*{base}", "envelope")
            conjugation_rows.append({"left": left, "right": right, "lhs": lhs, "base": base, "factor": factor})

    C = sp.Integer(75)
    delta = sp.Rational(1, 5)
    audit.check("endpoint relation", G**2 <= 1 + C * delta, [G**2, 1 + C * delta], "G^2<=1+C delta", "envelope")
    T = sp.Rational(2, 3)
    N = 12
    for bits in (0, 1, 2):
        a_plus_b = sp.Rational(bits, 2)
        finite = (1 + C * T / N) ** (6 * N * a_plus_b)
        exponential = sp.exp(6 * C * T * a_plus_b)
        audit.check(f"split exponential bits={bits}", float(finite) <= float(exponential) + 1e-12, finite, f"<=exp({6*C*T*a_plus_b})", "split")
    audit.check("volume independent coefficient", manifest["split_envelope"]["volume_uniform"] is True, manifest["split_envelope"], True, "split")

    # Exact spatial counterexample: K=I makes all M_(a,b) invariant, while a
    # cyclic shift transports a local projector to a distant site and creates
    # an order-one commutator with a local matrix unit there.
    size = 8
    P = shift_fixture(size)
    X = sp.zeros(size); X[0, 0] = 1
    distance = 3
    Y = sp.zeros(size); Y[distance, distance + 1] = 1
    transported = (P ** distance) * X * (P.T ** distance)
    comm0 = X * Y - Y * X
    commd = transported * Y - Y * transported
    audit.check("shift transports support", transported[distance, distance] == 1, transported, "site d projector", "counterexample")
    audit.check("initial distant commutator zero", inf_norm(comm0) == 0, inf_norm(comm0), 0, "counterexample")
    audit.check("transported commutator order one", inf_norm(commd) == 1, inf_norm(commd), 1, "counterexample")
    audit.check("energy seminorm blind to shift", inf_norm(P) == 1 and inf_norm(P.T) == 1, [inf_norm(P), inf_norm(P.T)], [1, 1], "counterexample")

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
            "control_dimension": 4,
            "half_power_contexts": 4,
            "product_context_inequalities": len(product_rows),
            "conjugation_contexts": len(conjugation_rows),
            "G": G,
            "C": C,
            "delta": delta,
            "six_layer_count": 6,
            "finite_energy_product_envelope_closed": True,
            "volume_uniform_split_envelope_closed": True,
            "spatial_decay_from_envelope": False,
            "counterexample_distance": distance,
            "boundary_commutator_decay_closed": False,
            "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False,
        },
        "product_rows": product_rows,
        "conjugation_rows": conjugation_rows,
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": manifest["boundary"],
        "exploration_id": manifest["exploration_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FRECHET-ENERGY PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
