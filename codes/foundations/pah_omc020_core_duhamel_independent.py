#!/usr/bin/env python3
"""Independent reconstruction of the PAH-OMC-020 core residual budget.

The implementation intentionally does not import the primary verifier.  Its
finite arithmetic is a labelled oracle for the conditional implication only.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-core-duhamel-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-core-duhamel/independent.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(relative)
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


def budget(n_f: Fraction, i_f: Fraction, i_g: Fraction,
           residual: Fraction, n_g: Fraction) -> Fraction:
    return n_f * (i_g + residual) + i_f * n_g


def main_compute() -> dict[str, Any]:
    contract = load("strategy/pa-hyp/PAH-OMC-020-core-duhamel-contract-v1.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    parents = contract["parents"]
    hashes: dict[str, str] = {}
    for label, entry in sorted(parents.items()):
        path = ROOT / entry["path"]
        actual = digest(path)
        hashes[entry["path"]] = actual
        check(f"hash {label}", actual, entry["sha256"], actual == entry["sha256"])
        check(f"LF {label}", b"\r" not in path.read_bytes(), True, b"\r" not in path.read_bytes())

    pah = load(parents["PAH-001"]["path"])
    prereg = load(parents["PAH-OMC-020-prereg"]["path"])
    r512 = load(parents["R-512"]["path"])
    r534 = load(parents["R-534"]["path"])
    r536 = load(parents["R-536"]["path"])

    check("contract identity", contract["contract_id"], "PAH-OMC-020-CORE-DUHAMEL",
          contract["contract_id"] == "PAH-OMC-020-CORE-DUHAMEL")
    check("task identity", contract["task_id"], "T-079", contract["task_id"] == "T-079")
    check("PAH identity", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check("registered order", prereg["scope"]["regulator_order"], prereg["scope"]["regulator_order"],
          "First j" in prereg["scope"]["regulator_order"] and "anchored n" in prereg["scope"]["regulator_order"])
    check("target result", r512["result_id"], "R-512", r512["result_id"] == "R-512")
    check("minimal target marker", "minimal" in json.dumps(r512, ensure_ascii=True).lower(), True,
          "minimal" in json.dumps(r512, ensure_ascii=True).lower())
    check("D term stays separate", "D_n" in json.dumps(r534.get("missing_assumptions"), ensure_ascii=True), True,
          "D_n" in json.dumps(r534.get("missing_assumptions"), ensure_ascii=True))
    check("form route incomplete", r536["route_status"]["form_route"]["complete"], False,
          r536["route_status"]["form_route"]["complete"] is False)
    check("path route incomplete", r536["route_status"]["path_route"]["complete"], False,
          r536["route_status"]["path_route"]["complete"] is False)

    required = set(contract["required_owner_packet"])
    expected_required = {
        "common_space_and_core", "correlation_identity", "initial_recovery",
        "residual_domain", "uniform_residual", "target_contraction",
    }
    check("owner field set", sorted(required), sorted(expected_required), required == expected_required)
    theorem = contract["conditional_theorem"]
    check("variation-of-constants present", "integral_0^t" in theorem["variation_of_constants"], True,
          "integral_0^t" in theorem["variation_of_constants"])
    check("initial defect present", "I_n(g)" in theorem["state_vector_bound"], True,
          "I_n(g)" in theorem["state_vector_bound"])
    check("residual defect present", "R_n(g;T)" in theorem["correlation_bound"], True,
          "R_n(g;T)" in theorem["correlation_bound"])

    fixture = contract["diagnostic_fixture"]["inputs"]
    n_f = Fraction(fixture["N_f"])
    i_f = Fraction(fixture["I_f"])
    i_g = Fraction(fixture["I_g"])
    residual = Fraction(fixture["R_g"])
    n_g = Fraction(fixture["norm_g"])
    result = budget(n_f, i_f, i_g, residual, n_g)
    check("oracle nonnegative", result >= 0, True, result >= 0)
    check("oracle value", result, Fraction(23, 256), result == Fraction(23, 256))
    check("zero initial and residual", budget(n_f, Fraction(0), Fraction(0), Fraction(0), n_g), Fraction(0),
          budget(n_f, Fraction(0), Fraction(0), Fraction(0), n_g) == Fraction(0))
    check("initial contribution positive", budget(n_f, i_f, Fraction(0), Fraction(0), n_g) > 0, True,
          budget(n_f, i_f, Fraction(0), Fraction(0), n_g) > 0)
    check("residual contribution positive", budget(n_f, Fraction(0), Fraction(0), residual, n_g) > 0, True,
          budget(n_f, Fraction(0), Fraction(0), residual, n_g) > 0)
    check("oracle below one", result < 1, True, result < 1)
    check("conditional only", contract["provenance"]["claim_bearing"], False,
          contract["provenance"]["claim_bearing"] is False)
    check("physical firewall", contract["provenance"]["physical_promotion"], False,
          contract["provenance"]["physical_promotion"] is False)

    return {
        "schema": "tect/pah-omc020-core-duhamel-independent/1.0",
        "audit_id": "PAH-OMC-020-CORE-DUHAMEL-INDEPENDENT-001",
        "task_id": "T-079",
        "status": "PASS_INDEPENDENT_CORE_DUHAMEL_BOUND",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "contract_sha256": digest(CONTRACT),
        "checks": checks,
        "checks_passed": len(checks),
        "fixture_bound": str(result),
        "finding": "Independent reconstruction confirms the residual-to-correlation envelope and its retained initial/residual terms; no source-authorized owner packet is present.",
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
            raise SystemExit("PAH-OMC-020 core-duhamel independent replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 CORE DUHAMEL INDEPENDENT: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
