#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 Mosco-resolvent contract."""

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
    "2026-09-08-pah-omc020-mosco-resolvent/primary.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    if isinstance(value, set):
        return sorted(serial(item) for item in value)
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> bytes:
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return encoded


def objective(k: Fraction, lam: Fraction, f: Fraction, u: Fraction) -> Fraction:
    return k * u * u + lam * (u - f) * (u - f)


def minimizer(k: Fraction, lam: Fraction, f: Fraction) -> Fraction:
    denominator = k + lam
    if denominator <= 0:
        raise ValueError("resolvent parameter must be positive")
    return lam * f / denominator


def compute() -> tuple[dict[str, Any], bytes]:
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    raw = CONTRACT.read_bytes()
    check("contract UTF-8 LF", b"\r" not in raw, True, b"\r" not in raw)
    check("schema", contract.get("schema"), "tect/pah-omc020-mosco-resolvent-contract/1.0",
          contract.get("schema") == "tect/pah-omc020-mosco-resolvent-contract/1.0")
    check("contract id", contract.get("contract_id"), "PAH-OMC-020-MOSCO-RESOLVENT",
          contract.get("contract_id") == "PAH-OMC-020-MOSCO-RESOLVENT")
    check("task", contract.get("task_id"), "T-080", contract.get("task_id") == "T-080")
    check("conditional status", contract.get("status"), "RESEARCHER_OWNED_CONDITIONAL_CONTRACT",
          contract.get("status") == "RESEARCHER_OWNED_CONDITIONAL_CONTRACT")

    provenance = contract["provenance"]
    for field in ("source_authorized_packet_present", "claim_bearing", "active_gate_change", "physical_promotion"):
        check(f"provenance {field}", provenance.get(field), False, provenance.get(field) is False)
    check("constructed hypothesis", provenance.get("constructed_hypothesis"), True,
          provenance.get("constructed_hypothesis") is True)

    parents = contract["parents"]
    check("parent count", len(parents), 6, len(parents) == 6)
    source_hashes: dict[str, str] = {}
    sources: dict[str, dict[str, Any]] = {}
    for label, entry in sorted(parents.items()):
        path = ROOT / entry["path"]
        check(f"exists {label}", path.is_file(), True, path.is_file())
        check(f"LF {label}", b"\r" not in path.read_bytes(), True, b"\r" not in path.read_bytes())
        actual = digest(path)
        source_hashes[entry["path"]] = actual
        check(f"hash {label}", actual, entry["sha256"], actual == entry["sha256"])
        sources[entry["path"]] = load(path)

    pah = sources[parents["PAH-001"]["path"]]
    prereg = sources[parents["PAH-OMC-020-prereg"]["path"]]
    r512 = sources[parents["R-512"]["path"]]
    r530 = sources[parents["R-530"]["path"]]
    r536 = sources[parents["R-536"]["path"]]
    r537 = sources[parents["R-537"]["path"]]
    check("PAH identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    check("registered j then n", "First j" in prereg["scope"]["regulator_order"] and "anchored n" in prereg["scope"]["regulator_order"], True,
          "First j" in prereg["scope"]["regulator_order"] and "anchored n" in prereg["scope"]["regulator_order"])
    check("R-512 exact target", r512.get("result_id"), "R-512", r512.get("result_id") == "R-512")
    check("R-512 minimal marker", "minimal" in json.dumps(r512, ensure_ascii=True).lower(), True,
          "minimal" in json.dumps(r512, ensure_ascii=True).lower())
    check("R-530 target form", r530.get("result_id"), "R-530", r530.get("result_id") == "R-530")
    check("R-536 route still open", r536["route_status"]["form_route"]["complete"] is False and r536["route_status"]["path_route"]["complete"] is False, True,
          r536["route_status"]["form_route"]["complete"] is False and r536["route_status"]["path_route"]["complete"] is False)
    check("R-537 remains conditional", r537.get("verdict"), "HOLD_FOR_EVIDENCE", r537.get("verdict") == "HOLD_FOR_EVIDENCE")

    required = set(contract["required_owner_packet"])
    expected_required = {
        "common_space_equicoercivity", "arbitrary_sequence_liminf", "recovery_sequence",
        "data_recovery", "target_exact_unique", "norm_upgrade", "semigroup_bridge",
    }
    check("owner field set", sorted(required), sorted(expected_required), required == expected_required)
    theorem = contract["conditional_theorem"]
    check("energy sandwich marker", "liminf_n J_n" in theorem["energy_sandwich"] and "limsup_n" in theorem["energy_sandwich"], True,
          "liminf_n J_n" in theorem["energy_sandwich"] and "limsup_n" in theorem["energy_sandwich"])
    check("unique selection marker", "strict convexity" in theorem["cluster_selection"], True,
          "strict convexity" in theorem["cluster_selection"])
    check("semigroup firewall", "not called" in theorem["scope_boundary"], True, "not called" in theorem["scope_boundary"])
    check("generic theorem not imported", "without importing" in contract["purpose"] or "not import" in contract["purpose"], True,
          "without importing" in contract["purpose"] or "not import" in contract["purpose"])

    fixture = contract["diagnostic_fixture"]["inputs"]
    lam = Fraction(fixture["lambda"])
    k_limit = Fraction(fixture["k_limit"])
    f = Fraction(fixture["f"])
    k_values = [Fraction(value) for value in fixture["k_values"]]
    check("lambda positive", lam > 0, True, lam > 0)
    target = minimizer(k_limit, lam, f)
    values = [minimizer(k, lam, f) for k in k_values]
    errors = [abs(value - target) for value in values]
    check("target minimizer", target, Fraction(1), target == Fraction(1))
    check("oracle errors strictly decrease", errors[0] > errors[1] > errors[2], True, errors[0] > errors[1] > errors[2])
    check("oracle minimizer objective", objective(k_limit, lam, f, target) <= objective(k_limit, lam, f, Fraction(0)), True,
          objective(k_limit, lam, f, target) <= objective(k_limit, lam, f, Fraction(0)))
    check("oracle values", values, [Fraction(3, 4), Fraction(6, 7), Fraction(12, 13)], values == [Fraction(3, 4), Fraction(6, 7), Fraction(12, 13)])

    current = contract["current_status"]
    expected_current = {
        "common_space_equicoercivity": False,
        "arbitrary_sequence_liminf": False,
        "recovery_sequence": False,
        "data_recovery": False,
        "target_exact_unique": True,
        "norm_upgrade": False,
        "semigroup_bridge": False,
        "resolvent_limit": False,
    }
    check("current owner status", current, expected_current, current == expected_current)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-mosco-resolvent-primary/1.0",
        "audit_id": "PAH-OMC-020-MOSCO-RESOLVENT-PRIMARY-001",
        "task_id": "T-080",
        "status": "PASS_CONDITIONAL_MOSCO_RESOLVENT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": source_hashes,
        "contract_sha256": digest(CONTRACT),
        "owner_fields": current,
        "fixture": {
            "inputs": fixture,
            "target_minimizer": str(target),
            "minimizers": [str(value) for value in values],
            "errors": [str(error) for error in errors],
        },
        "conditional_result": {
            "energy_sandwich": "liminf J_n(u_n) >= J(u) and limsup inf J_n <= J(v)",
            "selection": "strict convexity of J identifies every weak cluster with R_min^lambda f",
            "upgrade": "a source-authorized norm-upgrade field yields strong resolvent convergence",
        },
        "finding": "The variational resolvent selection implication and scalar oracle are closed, but common-space equicoercivity, arbitrary-sequence liminf, recovery, norm upgrade and the separate semigroup bridge remain absent from the pinned corpus.",
        "missing_assumptions": [
            "Source-authorized common H/U_n with equicoercive source-resolvent minimizers.",
            "Arbitrary-sequence N2b liminf and all-local recovery with the terminal-square convention.",
            "Strong data recovery and a norm-upgrade argument for local resolvents.",
            "A separate resolvent-to-compact-time-correlation bridge for PAH-OMC-020.",
        ],
        "next_single_question": contract["single_next_question"],
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    return payload, encoded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload, encoded = compute()
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 Mosco-resolvent primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 MOSCO RESOLVENT PRIMARY: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
