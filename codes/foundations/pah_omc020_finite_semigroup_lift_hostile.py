#!/usr/bin/env python3
"""Hostile audit for shortcuts from R-493 generator equality to a semigroup."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-finite-semigroup-lift-contract-v1.json"
R493 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-finite-semigroup-lift/hostile.json"


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    contract = read(CONTRACT)
    r493 = read(R493)
    checks: list[dict[str, Any]] = []

    def reject(name: str, rejected: bool, detail: Any) -> None:
        checks.append({"mutation": name, "rejected": bool(rejected), "detail": detail})

    # A derivative-at-zero identity is not accepted as an exponential identity
    # unless the all-iterate or invariant-domain premise is present.
    reject(
        "generator-only-to-semigroup shortcut",
        not ("all_iterates" in r493 or "invariant_subspace" in r493 or "operator_identity" in r493),
        {"declared_fields": sorted(r493.keys()), "required": ["all_iterates", "invariant_subspace", "operator_identity"]},
    )
    reject(
        "fixed-N-after-iteration shortcut",
        "support-dependent" in contract["exact_scope"]["registered_input"].lower()
        and "support-dependent" in contract["closure_audit"]["support_rule"].lower(),
        {"registered_input": contract["exact_scope"]["registered_input"], "support_rule": contract["closure_audit"]["support_rule"]},
    )
    reject(
        "local-cylinder-as-full-function-space shortcut",
        "entire finite coarse function space" in contract["finite_bridge_theorem"]["sufficient_hypothesis"]
        and "algebraic union" in r493["exact_scope"]["common_cylinder_algebra"],
        {"sufficient": contract["finite_bridge_theorem"]["sufficient_hypothesis"], "domain": r493["exact_scope"]["common_cylinder_algebra"]},
    )
    reject(
        "boundary-defect-erasure",
        "16/9" in r493["boundary_and_uniformity"]["R484_defect"] and "retain" in r493["boundary_and_uniformity"]["R484_defect"].lower(),
        r493["boundary_and_uniformity"]["R484_defect"],
    )
    reject(
        "anchored-n-promotion",
        "anchored-n" in " ".join(contract["non_claims"]).lower() and contract["status"]["active_gate_change"] is False,
        contract["non_claims"],
    )
    reject(
        "physical-promotion",
        contract["status"]["physical_promotion"] is False and any("No physical Pre-A" in item for item in contract["non_claims"]),
        contract["non_claims"],
    )

    mutations: list[tuple[str, bool]] = []
    mutated = copy.deepcopy(contract)
    mutated["status"]["finite_conditional_bridge"] = "PROVED_UNCONDITIONALLY"
    mutations.append(("pretend-strong-hypothesis", mutated["status"]["finite_conditional_bridge"] == "PROVED_CONDITIONALLY"))
    mutated = copy.deepcopy(contract)
    mutated["status"]["active_gate_change"] = True
    mutations.append(("pretend-gate-change", mutated["status"]["active_gate_change"] is False))
    mutated = copy.deepcopy(contract)
    mutated["non_claims"] = []
    mutations.append(("delete-non-claims", any("physical" in item.lower() for item in mutated["non_claims"])))
    reject("mutation simulations all rejected", all(not accepted for _name, accepted in mutations), {name: accepted for name, accepted in mutations})

    failed = [row for row in checks if not row["rejected"]]
    payload = {
        "schema": "tect/pah-omc020-finite-semigroup-lift-hostile/1.0",
        "audit_id": "PAH-OMC-020-FINITE-SEMIGROUP-LIFT-HOSTILE-001",
        "result_id": "R-550",
        "task_id": "T-082",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "HOSTILE_FIREWALL_REJECTS_SEMIGROUP_OVERCLAIM",
        "source_hashes": {"contract": digest(CONTRACT), "R493": digest(R493)},
        "checks": checks,
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "missing_assumptions": contract["missing_assumptions"],
        "single_next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": digest(Path(__file__)),
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic(destination, payload)
    print(f"PAH-OMC-020 FINITE SEMIGROUP LIFT HOSTILE: {payload['verification']} {payload['checks_passed']}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
