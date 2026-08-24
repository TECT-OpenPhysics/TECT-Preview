#!/usr/bin/env python3
"""Independent Fraction audit of the formal coefficient completion fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-bientire-coefficient-completion"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"
Coeff = dict[tuple[int, int], F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def norm(series: Coeff, field_radius: F, source_radius: F) -> F:
    return sum(abs(coefficient) * field_radius**m * source_radius**n for (m, n), coefficient in series.items())


def product(left: Coeff, right: Coeff) -> Coeff:
    result: Coeff = {}
    for (m, n), coefficient in left.items():
        for (k, ell), other in right.items():
            key = (m + k, n + ell)
            result[key] = result.get(key, F(0)) + coefficient * other
    return {key: value for key, value in result.items() if value}


def field_derivative(series: Coeff) -> Coeff:
    return {(m - 1, n): m * coefficient for (m, n), coefficient in series.items() if m > 0 and coefficient}


def source_derivative(series: Coeff) -> Coeff:
    return {(m, n - 1): n * coefficient for (m, n), coefficient in series.items() if n > 0 and coefficient}


def geometric_truncation(u: F, v: F, degree: int) -> F:
    total = F(0)
    for m in range(degree + 1):
        for n in range(degree + 1 - m):
            total += u**m * v**n
    return total


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    R, S = F(fixture["field_radius"]), F(fixture["source_radius"])
    Rp, Sp = F(fixture["reduced_field_radius"]), F(fixture["reduced_source_radius"])
    alpha, beta = F(fixture["geometric_field_ratio"]), F(fixture["geometric_source_ratio"])
    target = F(fixture["tail_target"])
    degree = int(fixture["truncation_degree"])
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001042" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001042/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("strict radius loss", 0 < Rp < R and 0 < Sp < S, [Rp, R, Sp, S], "0<R'<R and 0<S'<S", "scope")

    p: Coeff = {(0, 0): F(1), (1, 0): -F(1), (0, 1): F(1), (2, 1): F(2)}
    q: Coeff = {(0, 0): F(1), (1, 0): F(1), (0, 1): -F(1), (1, 2): F(1)}
    pq = product(p, q)
    p_norm, q_norm, pq_norm = norm(p, R, S), norm(q, R, S), norm(pq, R, S)
    product_bound = p_norm * q_norm
    audit.check("finite support inputs", len(p) == 4 and len(q) == 4, [len(p), len(q)], [4, 4], "algebra")
    audit.check("Cauchy product finite", len(pq) > 0, len(pq), ">0", "algebra")
    audit.check("Cauchy submultiplicativity", pq_norm <= product_bound, pq_norm, f"<={product_bound}", "algebra")

    dp, da = field_derivative(p), source_derivative(p)
    dp_norm, da_norm = norm(dp, Rp, Sp), norm(da, Rp, Sp)
    field_constant = R / (R - Rp) ** 2
    source_constant = S / (S - Sp) ** 2
    field_bound, source_bound = field_constant * p_norm, source_constant * p_norm
    audit.check("field derivative definition", dp == {(0, 0): -F(1), (1, 1): F(4)}, dp, "fixture derivative", "calculus")
    audit.check("source derivative definition", da == {(0, 0): F(1), (2, 0): F(2)}, da, "fixture derivative", "calculus")
    audit.check("field radius-loss bound", dp_norm <= field_bound, dp_norm, f"<={field_bound}", "calculus")
    audit.check("source radius-loss bound", da_norm <= source_bound, da_norm, f"<={source_bound}", "calculus")

    u, v = alpha * R, beta * S
    geometric_full = 1 / ((1 - u) * (1 - v))
    tail_rows: list[dict[str, Any]] = []
    previous_tail: F | None = None
    for truncation in range(degree + 1):
        partial = geometric_truncation(u, v, truncation)
        tail = geometric_full - partial
        audit.check(f"geometric tail nonnegative N={truncation}", tail >= 0, tail, ">=0", "density")
        if previous_tail is not None:
            audit.check(f"geometric tail monotone N={truncation}", tail <= previous_tail, tail, f"<={previous_tail}", "density")
        previous_tail = tail
        tail_rows.append({"degree": truncation, "partial": partial, "tail": tail})
    final_tail = tail_rows[-1]["tail"]
    audit.check("finite truncation crosses target", final_tail < target, final_tail, f"<{target}", "density")
    audit.check("geometric full norm identity", geometric_full == 1 / ((1 - alpha * R) * (1 - beta * S)), geometric_full, "product geometric norm", "completion")
    audit.check("formal completion scope", manifest["scope"]["formal_completion_closed"] is True and manifest["scope"]["operator_completion_closed"] is False, manifest["scope"], "formal closed/operator open", "scope")

    passed = len(audit.rows)
    derived = {
        "field_radius": R,
        "source_radius": S,
        "reduced_field_radius": Rp,
        "reduced_source_radius": Sp,
        "p_norm": p_norm,
        "q_norm": q_norm,
        "product_norm": pq_norm,
        "product_bound": product_bound,
        "field_derivative_norm": dp_norm,
        "source_derivative_norm": da_norm,
        "field_radius_loss_constant": field_constant,
        "source_radius_loss_constant": source_constant,
        "geometric_full_norm": geometric_full,
        "geometric_tail_degree": degree,
        "geometric_tail": final_tail,
        "tail_below_target": True,
        "finite_polynomials_dense_formally": True,
        "cauchy_product_submultiplicative": True,
        "radius_loss_derivative_bridge": True,
        "formal_completion_closed": True,
        "operator_completion_closed": False,
        "actual_q3_history_closed": False,
        "all_shape_exhaustion_closed": False,
        "common_alpha_closed": False,
    }
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "verdict": "PASS", "passed": passed, "total": passed, "failed": 0, "assertions": audit.rows, "tail_rows": tail_rows, "derived": derived, "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)}, "exploration_id": manifest["exploration_id"], "boundary": manifest["scope"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT BI-ENTIRE-COEFFICIENT-COMPLETION PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
