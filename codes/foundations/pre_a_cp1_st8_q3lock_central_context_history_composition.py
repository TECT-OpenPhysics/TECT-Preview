#!/usr/bin/env python3
"""Primary exact audit for EXP-001048.

The package is a conditional composition checkpoint.  It recomputes the
actual EXP-001045 Q3 source rate, assumes a four-context A^(a) D A^(-b)
bound at that rate, and checks the central A-power insertion for finite
matrix words.  The factorial first-passage EGF is recorded as a separate
conditional scalar bridge; no Q3 history or unbounded-operator theorem is
claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-central-context-history-composition"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[safe(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
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


def inf_norm(matrix: sp.Matrix) -> sp.Rational:
    return max((sum(abs(matrix[i, j]) for j in range(matrix.cols)) for i in range(matrix.rows)), default=sp.Rational(0))


def weighted_rate(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], source_radius: sp.Rational, root_scale: sp.Integer, neighbour_root: sp.Integer, neighbour_index: int) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        field_degree = sum(monomial[:-1])
        source_degree = monomial[-1]
        total += abs(coefficient) * root_scale**field_degree * neighbour_root**monomial[neighbour_index] * source_radius**source_degree
    return sp.factor(total)


def product(factors: list[sp.Matrix]) -> sp.Matrix:
    result = sp.eye(factors[0].rows)
    for factor in factors:
        result = result * factor
    return result


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    fixture = upstream["fixture"]
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001048" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001048/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045", "provenance")
    audit.check("central exponent", manifest["central_context"]["energy_exponent"] == "s=3/4", manifest["central_context"]["energy_exponent"], "s=3/4", "hypothesis")
    audit.check("four contexts declared", len(manifest["central_context"]["contexts"]) == 4, len(manifest["central_context"]["contexts"]), 4, "hypothesis")

    gamma = sp.Rational(str(fixture["gamma"]))
    kappa = sp.Rational(str(fixture["kappa"]))
    root_scale = sp.Integer(str(fixture["root_scale"]))
    neighbour_root = sp.Integer(str(fixture["neighbor_factor_root"]))
    source_radius = sp.Rational(str(fixture["source_radius"]))
    lam = sp.Rational(str(fixture["lambda"]))
    coupling = sp.Rational(str(fixture["spatial_coupling"]))
    audit.check("positive upstream inputs", gamma > 0 and kappa > 0 and source_radius > 0, [gamma, kappa, source_radius], ">0", "input")
    audit.check("registered energy ratio", root_scale**4 == kappa / gamma, [root_scale**4, kappa / gamma], "equal", "input")

    q, v, r, a = sp.symbols("q v r a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    bond = coupling * (q - r) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - r) ** 2 / 2)
    onsite_q = sp.symbols("onsite_q")
    onsite = sp.Rational(3, 5) * (onsite_q**4 - (onsite_q - a) ** 4) / 4
    edge_rate = weighted_rate(edge_u, (q, v, a), source_radius, root_scale, neighbour_root, 1)
    bond_rate = weighted_rate(bond_u, (q, r, a), source_radius, root_scale, neighbour_root, 1)
    onsite_rate = weighted_rate(onsite, (onsite_q, a), source_radius, root_scale, sp.Integer(1), 0)
    B = sp.factor(onsite_rate + 3 * edge_rate + 6 * bond_rate)
    expected_B = sp.Rational(str(fixture["expected_local_rate"]))
    audit.check("source rate recomputed", B == expected_B, B, expected_B, "source-rate")
    audit.check("source components positive", all(value > 0 for value in (onsite_rate, edge_rate, bond_rate, B)), [onsite_rate, edge_rate, bond_rate, B], ">0", "source-rate")

    # Exact finite common-core fixture.  D_j=c_j A^(-s) satisfies all four
    # context inequalities with bound c_j; this tests composition bookkeeping,
    # not identification of D_j with the Q3 source differences.
    A = sp.diag(1, 16, 256)
    As = sp.diag(1, 8, 64)
    Ais = sp.diag(1, sp.Rational(1, 8), sp.Rational(1, 64))
    audit.check("fractional energy fixture", As * As * As * As == A**3, As * As * As * As, A**3, "fixture")
    audit.check("inverse energy fixture", As * Ais == sp.eye(3) and Ais * As == sp.eye(3), As * Ais, "I", "fixture")
    coefficients = [B / sp.Integer(index) for index in range(1, len(manifest["central_context"]["finite_fixture"]["factor_multipliers"]) + 1)]
    factors = [coefficient * Ais for coefficient in coefficients]
    context_pairs = [(0, 0), (0, 1), (1, 0), (1, 1)]
    context_rows: list[dict[str, Any]] = []
    for index, factor in enumerate(factors):
        for left_bit, right_bit in context_pairs:
            left = As if left_bit else sp.eye(3)
            right = Ais if right_bit else sp.eye(3)
            value = inf_norm(left * factor * right)
            audit.check(f"context bound D{index + 1} ({left_bit},{right_bit})", value <= B, value, f"<={B}", "central-context")
            context_rows.append({"factor": index + 1, "left": left_bit, "right": right_bit, "value": value})

    word_rows: list[dict[str, Any]] = []
    for length in range(1, len(factors) + 1):
        for left_bit, right_bit in context_pairs:
            left = As if left_bit else sp.eye(3)
            right = Ais if right_bit else sp.eye(3)
            word = product(factors[:length])
            direct = left * word * right
            if length == 1:
                inserted = direct
            else:
                pieces = [left * factors[0] * Ais]
                pieces.extend(As * factors[index] * Ais for index in range(1, length - 1))
                pieces.append(As * factors[length - 1] * right)
                inserted = product(pieces)
            norm_value = inf_norm(direct)
            audit.check(f"central insertion length={length} context={left_bit},{right_bit}", direct == inserted, direct, "inserted product", "insertion")
            audit.check(f"word bound length={length} context={left_bit},{right_bit}", norm_value <= B**length, norm_value, f"<={B**length}", "word-bound")
            word_rows.append({"length": length, "left": left_bit, "right": right_bit, "norm": norm_value, "bound": B**length})

    passage = manifest["first_passage_bridge"]
    orientations = sp.Integer(str(passage["orientations"]))
    degree = sp.Integer(str(passage["degree_bound"]))
    base = sp.Integer(str(passage["spatial_base"]))
    time = sp.Rational(str(passage["time"]))
    distance = int(passage["distance"])
    eta = sp.factor(orientations * degree * base * B * time)
    order = 32
    partial = sum((eta**n) / sp.factorial(n) for n in range(order + 1))
    exp_value = sp.exp(eta)
    distance_envelope = sp.factor(base ** (-distance)) * exp_value
    audit.check("factorial EGF exponent positive", eta > 0, eta, ">0", "first-passage")
    audit.check("finite EGF below exponential", float(partial) <= float(exp_value), partial, f"<=exp({eta})", "first-passage")
    audit.check("distance factor exact", base ** (-distance) == sp.Rational(1, base**distance), base ** (-distance), "exact", "first-passage")
    audit.check("conditional scope", manifest["scope"]["central_context_word_bound_closed_conditionally"] is True and manifest["scope"]["actual_q3_central_context_proved"] is False and manifest["scope"]["actual_q3_history_closed"] is False, manifest["scope"], "conditional/open", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "context_rows": context_rows,
        "word_rows": word_rows,
        "derived": {
            "energy_exponent": sp.Rational(3, 4),
            "source_rate_B": B,
            "onsite_rate": onsite_rate,
            "edge_rate": edge_rate,
            "bond_rate": bond_rate,
            "context_count": len(context_pairs),
            "word_lengths_checked": len(factors),
            "central_context_fixture_closed": True,
            "history_word_bound_closed_conditionally": True,
            "factorial_first_passage_envelope_closed_conditionally": True,
            "factorial_first_passage_hypothesis_supplied": False,
            "eta": eta,
            "partial_order": order,
            "distance": distance,
            "distance_envelope": distance_envelope,
            "actual_q3_central_context_proved": False,
            "actual_q3_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
            "upstream_manifest": str(UPSTREAM.relative_to(REPO)).replace("\\", "/"),
            "upstream_manifest_sha256": sha256(UPSTREAM),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY Q3-CENTRAL-CONTEXT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
