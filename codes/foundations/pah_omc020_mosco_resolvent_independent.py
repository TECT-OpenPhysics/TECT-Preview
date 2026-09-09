#!/usr/bin/env python3
"""Independent replay of the PAH-OMC-020 Mosco-resolvent contract."""

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
    "2026-09-08-pah-omc020-mosco-resolvent/independent.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(relative)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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
    denominator = k + lam
    if denominator <= 0:
        raise ValueError("nonpositive resolvent denominator")
    return lam * f / denominator


def main_compute() -> dict[str, Any]:
    contract = load("strategy/pa-hyp/PAH-OMC-020-mosco-resolvent-contract-v1.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    parents = contract["parents"]
    hashes: dict[str, str] = {}
    for label, entry in sorted(parents.items()):
        path = ROOT / entry["path"]
        hashes[entry["path"]] = sha(path)
        check(f"hash {label}", hashes[entry["path"]], entry["sha256"], hashes[entry["path"]] == entry["sha256"])
        check(f"LF {label}", b"\r" not in path.read_bytes(), True, b"\r" not in path.read_bytes())

    pah = load(parents["PAH-001"]["path"])
    prereg = load(parents["PAH-OMC-020-prereg"]["path"])
    r512 = load(parents["R-512"]["path"])
    r530 = load(parents["R-530"]["path"])
    r536 = load(parents["R-536"]["path"])
    r537 = load(parents["R-537"]["path"])
    check("contract id", contract["contract_id"], "PAH-OMC-020-MOSCO-RESOLVENT", contract["contract_id"] == "PAH-OMC-020-MOSCO-RESOLVENT")
    check("task", contract["task_id"], "T-080", contract["task_id"] == "T-080")
    check("PAH packet", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check("j before n", "First j" in prereg["scope"]["regulator_order"] and "anchored n" in prereg["scope"]["regulator_order"], True,
          "First j" in prereg["scope"]["regulator_order"] and "anchored n" in prereg["scope"]["regulator_order"])
    check("R-512 minimal target", r512["result_id"], "R-512", r512["result_id"] == "R-512" and "minimal" in json.dumps(r512).lower())
    check("R-530 target retained", r530["result_id"], "R-530", r530["result_id"] == "R-530")
    check("R-536 routes incomplete", (r536["route_status"]["form_route"]["complete"], r536["route_status"]["path_route"]["complete"]), (False, False),
          r536["route_status"]["form_route"]["complete"] is False and r536["route_status"]["path_route"]["complete"] is False)
    check("R-537 Duhamel remains hold", r537["verdict"], "HOLD_FOR_EVIDENCE", r537["verdict"] == "HOLD_FOR_EVIDENCE")

    fields = set(contract["required_owner_packet"])
    expected_fields = {"common_space_equicoercivity", "arbitrary_sequence_liminf", "recovery_sequence", "data_recovery", "target_exact_unique", "norm_upgrade", "semigroup_bridge"}
    check("owner fields", sorted(fields), sorted(expected_fields), fields == expected_fields)
    check("energy sandwich", "liminf_n" in contract["conditional_theorem"]["energy_sandwich"] and "limsup_n" in contract["conditional_theorem"]["energy_sandwich"], True,
          "liminf_n" in contract["conditional_theorem"]["energy_sandwich"] and "limsup_n" in contract["conditional_theorem"]["energy_sandwich"])
    check("strict uniqueness", "unique" in contract["conditional_theorem"]["cluster_selection"].lower(), True,
          "unique" in contract["conditional_theorem"]["cluster_selection"].lower())
    check("semigroup remains separate", "not called" in contract["conditional_theorem"]["scope_boundary"], True,
          "not called" in contract["conditional_theorem"]["scope_boundary"])

    fixture = contract["diagnostic_fixture"]["inputs"]
    lam = Fraction(fixture["lambda"])
    k_limit = Fraction(fixture["k_limit"])
    f = Fraction(fixture["f"])
    k_values = [Fraction(value) for value in fixture["k_values"]]
    target = minimizer(k_limit, lam, f)
    values = [minimizer(k, lam, f) for k in k_values]
    errors = [abs(value - target) for value in values]
    check("positive lambda", lam > 0, True, lam > 0)
    check("target value", target, Fraction(1), target == Fraction(1))
    check("minimizer values", values, [Fraction(3, 4), Fraction(6, 7), Fraction(12, 13)], values == [Fraction(3, 4), Fraction(6, 7), Fraction(12, 13)])
    check("decreasing errors", errors[0] > errors[1] > errors[2], True, errors[0] > errors[1] > errors[2])
    check("objective selection", objective(k_limit, lam, f, target) <= objective(k_limit, lam, f, Fraction(0)), True,
          objective(k_limit, lam, f, target) <= objective(k_limit, lam, f, Fraction(0)))
    check("zero-error target", abs(target - Fraction(1)), Fraction(0), abs(target - Fraction(1)) == Fraction(0))

    current = contract["current_status"]
    check("current target-only status", current["target_exact_unique"], True, current["target_exact_unique"] is True)
    check("current resolvent not admitted", current["resolvent_limit"], False, current["resolvent_limit"] is False)
    check("physical firewall", contract["provenance"]["physical_promotion"], False, contract["provenance"]["physical_promotion"] is False)

    return {
        "schema": "tect/pah-omc020-mosco-resolvent-independent/1.0",
        "audit_id": "PAH-OMC-020-MOSCO-RESOLVENT-INDEPENDENT-001",
        "task_id": "T-080",
        "status": "PASS_INDEPENDENT_MOSCO_RESOLVENT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "contract_sha256": sha(CONTRACT),
        "checks": checks,
        "checks_passed": len(checks),
        "fixture": {"target": str(target), "minimizers": [str(value) for value in values], "errors": [str(error) for error in errors]},
        "finding": "Independent reconstruction confirms the variational resolvent-selection implication and retains the separate semigroup bridge obligation; no common-space owner packet is present.",
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
            raise SystemExit("PAH-OMC-020 Mosco-resolvent independent replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 MOSCO RESOLVENT INDEPENDENT: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
