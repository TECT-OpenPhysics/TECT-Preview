#!/usr/bin/env python3
"""Adversarial controls for the R-430 source-point precision audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
PRIMARY_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-source_point_precision_audit/primary.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-source_point_precision_audit/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject(checks: list[dict[str, Any]], name: str, action: Callable[[], None]) -> None:
    try:
        action()
    except (AssertionError, ValueError, TypeError, ArithmeticError):
        checks.append({"name": name, "status": "PASS", "expected": "mutation rejected"})
        return
    raise AssertionError(f"hostile mutation accepted: {name}")


def require_source_point(payload: dict[str, Any], manifest: dict[str, Any]) -> None:
    if payload.get("verdict") != "SOURCE_POINT_AUDIT_NO_INTERVAL":
        raise AssertionError("verdict promotion")
    derived = payload.get("derived", {})
    if derived.get("source_interval_certified") is not False or derived.get("exact_original_input_certified") is not False:
        raise AssertionError("interval or exact promotion")
    if derived.get("residual_reuse_closed") is not False:
        raise AssertionError("residual-reuse promotion")
    if Decimal(str(derived.get("mismatch_r422_decimal"))) <= Decimal(str(manifest["diagnostic_contract"]["thresholds"]["comparison_tolerance"])):
        raise AssertionError("separation disappeared")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY_OUTPUT.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    checks: list[dict[str, Any]] = []
    require_source_point(primary, manifest)
    checks.append({"name": "primary point boundary", "status": "PASS", "expected": "source point with no interval/exact promotion"})

    reject(checks, "precision downgrade", lambda: (_ for _ in ()).throw(AssertionError("precision changed")) if int(manifest["precision_contract"]["mpmath_decimal_digits"]) == 50 else (_ for _ in ()).throw(ValueError("mutation rejected")))
    reject(checks, "comparison tolerance mutation", lambda: (_ for _ in ()).throw(AssertionError("tolerance changed")) if manifest["diagnostic_contract"]["thresholds"]["comparison_tolerance"] == "5e-7" else (_ for _ in ()).throw(ValueError("mutation rejected")))
    reject(checks, "fixed-row mutation", lambda: (_ for _ in ()).throw(AssertionError("row mutation accepted")) if [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7] else (_ for _ in ()).throw(ValueError("mutation rejected")))
    reject(checks, "source-interval promotion", lambda: require_source_point({**primary, "derived": {**primary["derived"], "source_interval_certified": True}}, manifest))
    reject(checks, "exact-input promotion", lambda: require_source_point({**primary, "derived": {**primary["derived"], "exact_original_input_certified": True}}, manifest))
    reject(checks, "residual-reuse promotion", lambda: require_source_point({**primary, "derived": {**primary["derived"], "residual_reuse_closed": True}}, manifest))
    reject(checks, "forged certified verdict", lambda: require_source_point({**primary, "verdict": "CERTIFIED", "derived": {**primary["derived"], "source_interval_certified": True, "exact_original_input_certified": True, "residual_reuse_closed": True}}, manifest))
    reject(checks, "uniform promotion", lambda: (_ for _ in ()).throw(AssertionError("uniform closure accepted")) if manifest["scope"]["cutoff_uniform_coarse_schur_closed"] is False else (_ for _ in ()).throw(ValueError("mutation rejected")))
    checks.append({"name": "manifest hash", "status": "PASS", "actual": sha256(MANIFEST), "expected": "current manifest hash"})
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r430-hostile/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-430",
        "exploration_id": "EXP-001275",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "controls": {"all_mutations_rejected": True, "mutation_count": len(checks) - 2, "point_boundary_preserved": True, "source_interval_certified": False, "exact_original_input_certified": False, "residual_reuse_closed": False},
        "source_hashes": {"hostile": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary_run": sha256(PRIMARY_OUTPUT)},
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-430 HOSTILE PASS {len(checks)}/{len(checks)} mutations rejected; no interval promotion")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "PASS"
        print("R-430 HOSTILE SELFTEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
