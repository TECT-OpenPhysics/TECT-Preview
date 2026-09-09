#!/usr/bin/env python3
"""Hostile checks for the PAH-OMC-020 Mosco-resolvent boundary.

The hostile lane rejects liminf-only, recovery-only, weak-only and
named-target shortcuts before any semigroup promotion.
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


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-mosco-resolvent-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-mosco-resolvent/hostile.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def objective(k: Fraction, lam: Fraction, f: Fraction, u: Fraction) -> Fraction:
    return k * u * u + lam * (u - f) * (u - f)


def minimizer(k: Fraction, lam: Fraction, f: Fraction) -> Fraction:
    return lam * f / (k + lam)


def main_compute() -> dict[str, Any]:
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    parents = contract["parents"]
    for label, entry in sorted(parents.items()):
        path = ROOT / entry["path"]
        check(f"hash {label}", sha(path), entry["sha256"], sha(path) == entry["sha256"])
    check("conditional contract", contract["status"], "RESEARCHER_OWNED_CONDITIONAL_CONTRACT", contract["status"] == "RESEARCHER_OWNED_CONDITIONAL_CONTRACT")
    check("no source owner", contract["provenance"]["source_authorized_packet_present"], False, contract["provenance"]["source_authorized_packet_present"] is False)
    check("no gate change", contract["provenance"]["active_gate_change"], False, contract["provenance"]["active_gate_change"] is False)
    check("no physical promotion", contract["provenance"]["physical_promotion"], False, contract["provenance"]["physical_promotion"] is False)

    fixed = json.dumps(contract["fixed_scope"], ensure_ascii=True).lower()
    check("PAH model frozen", "exactly pah-001" in fixed, True, "exactly pah-001" in fixed)
    check("order frozen", "no diagonal" in fixed and "anchored n" in fixed, True, "no diagonal" in fixed and "anchored n" in fixed)
    check("no new carrier", "new carrier" not in fixed, True, "new carrier" not in fixed)
    check("external Markov time", "external stochastic markov time" in fixed, True, "external stochastic markov time" in fixed)

    status = contract["current_status"]
    missing = [key for key, value in status.items() if key != "target_exact_unique" and value is False]
    check("seven open owner or bridge fields", len(missing), 7, len(missing) == 7)
    check("target exactness only inherited", status["target_exact_unique"], True, status["target_exact_unique"] is True)
    check("resolvent limit held", status["resolvent_limit"], False, status["resolvent_limit"] is False)
    check("semigroup bridge held", status["semigroup_bridge"], False, status["semigroup_bridge"] is False)

    theorem = json.dumps(contract["conditional_theorem"], ensure_ascii=True).lower()
    check("liminf and recovery both named", "liminf" in theorem and "recovery" in theorem, True, "liminf" in theorem and "recovery" in theorem)
    check("weak cluster is not enough", "norm-upgrade" in theorem or "norm upgrade" in theorem, True, "norm-upgrade" in theorem or "norm upgrade" in theorem)
    check("semigroup not inferred", "not called" in theorem, True, "not called" in theorem)
    check("target uniqueness is variational", "strict convexity" in theorem, True, "strict convexity" in theorem)

    lam = Fraction(contract["diagnostic_fixture"]["inputs"]["lambda"])
    k = Fraction(contract["diagnostic_fixture"]["inputs"]["k_limit"])
    f = Fraction(contract["diagnostic_fixture"]["inputs"]["f"])
    target = minimizer(k, lam, f)
    displaced = target + 1
    check("lambda positive", lam > 0, True, lam > 0)
    check("target is minimizer", objective(k, lam, f, target) < objective(k, lam, f, displaced), True,
          objective(k, lam, f, target) < objective(k, lam, f, displaced))
    check("displaced objective gap positive", objective(k, lam, f, displaced) - objective(k, lam, f, target) > 0, True,
          objective(k, lam, f, displaced) - objective(k, lam, f, target) > 0)

    return {
        "schema": "tect/pah-omc020-mosco-resolvent-hostile/1.0",
        "audit_id": "PAH-OMC-020-MOSCO-RESOLVENT-HOSTILE-001",
        "task_id": "T-080",
        "status": "PASS_HOSTILE_MOSCO_RESOLVENT_BOUNDARY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "checks_passed": len(checks),
        "contract_sha256": sha(CONTRACT),
        "finding": "Hostile review rejects liminf-only, recovery-only, weak-only and named-target shortcuts; the variational target remains conditional and the semigroup bridge remains open.",
        "non_claims": contract["non_claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = main_compute()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    if args.check:
        if not destination.is_file() or json.loads(destination.read_text(encoding="utf-8")) != payload:
            raise SystemExit("PAH-OMC-020 Mosco-resolvent hostile replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 MOSCO RESOLVENT HOSTILE: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
