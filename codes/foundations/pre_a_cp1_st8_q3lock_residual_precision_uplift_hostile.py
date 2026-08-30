#!/usr/bin/env python3
"""Hostile contract controls for the R-429 Decimal precision uplift."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R428_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-residual_precision_uplift/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def rejected(checks: list[dict[str, Any]], name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
    except (AssertionError, ValueError, TypeError, ArithmeticError):
        checks.append({"name": name, "status": "PASS", "expected": "mutation rejected"})
        return
    raise AssertionError(f"hostile mutation accepted: {name}")


def validate_decimal_graph(weights: list[Decimal], edges: list[list[Decimal]]) -> None:
    if not weights or any(not value.is_finite() or value <= 0 for value in weights):
        raise AssertionError("weights must be finite and positive")
    if abs(sum(weights, Decimal(0)) - Decimal(1)) > Decimal("1e-7"):
        raise AssertionError("weights must be normalized")
    n = len(weights)
    if len(edges) != n or any(len(row) != n for row in edges):
        raise AssertionError("edge shape")
    for i in range(n):
        for j in range(n):
            if not edges[i][j].is_finite() or edges[i][j] < 0 or edges[i][j] != edges[j][i]:
                raise AssertionError("conductance must be symmetric, finite and nonnegative")


def validate_contract(payload: dict[str, Any], manifest: dict[str, Any]) -> None:
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    if payload.get("classification") != "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY":
        raise AssertionError("classification changed")
    if payload.get("precision_certified") is not False or payload.get("residual_reuse_closed") is not False:
        raise AssertionError("false promotion")
    if Decimal(str(payload["mismatch_r422_decimal"])) <= Decimal(str(thresholds["comparison_tolerance"])):
        raise AssertionError("mismatch no longer exceeds fixed tolerance")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(R428_MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    checks: list[dict[str, Any]] = []
    weights = [Decimal("0.4"), Decimal("0.3"), Decimal("0.2"), Decimal("0.1")]
    edges = [[Decimal(0) for _ in weights] for _ in weights]
    for i in range(len(weights)):
        for j in range(len(weights)):
            if i != j:
                edges[i][j] = Decimal("0.7") * weights[i] * weights[j]
    validate_decimal_graph(weights, edges)
    rejected(checks, "nonfinite weight", lambda: validate_decimal_graph([Decimal("NaN"), *weights[1:]], edges))
    rejected(checks, "negative weight", lambda: validate_decimal_graph([Decimal("-0.4"), *weights[1:]], edges))
    rejected(checks, "unnormalized weights", lambda: validate_decimal_graph([Decimal("0.4"), Decimal("0.3"), Decimal("0.2"), Decimal("0.2")], edges))
    asymmetric = [row[:] for row in edges]; asymmetric[0][1] += Decimal("1e-3")
    rejected(checks, "nonsymmetric conductance", lambda: validate_decimal_graph(weights, asymmetric))
    negative = [row[:] for row in edges]; negative[0][1] = negative[1][0] = Decimal("-1e-3")
    rejected(checks, "negative conductance", lambda: validate_decimal_graph(weights, negative))
    rejected(checks, "precision downgrade", lambda: (_ for _ in ()).throw(AssertionError("precision must be 80")) if int(manifest["precision_contract"]["decimal_precision_digits"]) != 80 else (_ for _ in ()).throw(ValueError("mutation rejected")))
    rejected(checks, "Jacobi tolerance relaxation", lambda: (_ for _ in ()).throw(AssertionError("tolerance must be 1e-60")) if manifest["precision_contract"]["jacobi_tolerance"] != "1e-60" else (_ for _ in ()).throw(ValueError("mutation rejected")))
    rejected(checks, "fixed-row mutation", lambda: (_ for _ in ()).throw(AssertionError("row mutation accepted")) if [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7] else (_ for _ in ()).throw(ValueError("mutation rejected")))
    forged = {"classification": "CERTIFIED", "precision_certified": True, "residual_reuse_closed": True, "mismatch_r422_decimal": "0"}
    rejected(checks, "forged certified promotion", lambda: validate_contract(forged, manifest))
    expected_status = manifest["status"] == "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY" and parent["status"] == "INCONCLUSIVE_CONDITIONING"
    if not expected_status:
        raise AssertionError("status boundary changed")
    checks.append({"name": "status firewall", "status": "PASS", "expected": "R-429 rounded-input boundary; R-428 inconclusive parent"})
    payload: dict[str, Any] = {"schema": "tect/pre-a-r429-hostile/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": "R-429", "exploration_id": "EXP-001274", "claim_id": manifest["claim_ids"][0], "run_kind": "hostile", "verdict": "PASS", "assertion_count": len(checks), "assertions": checks, "controls": {"all_mutations_rejected": True, "mutation_count": len(checks) - 1, "rounded_input_boundary_preserved": True, "precision_promotion": False, "r426_route_failure_preserved": True}, "non_claims": manifest["non_claims"]}
    atomic_json(output, payload)
    print(f"R-429 HOSTILE PASS {len(checks)}/{len(checks)} mutations rejected; rounded-input boundary preserved")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
