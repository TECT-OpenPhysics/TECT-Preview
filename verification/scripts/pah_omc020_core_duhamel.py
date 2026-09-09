#!/usr/bin/env python3
"""Primary replay for the PAH-OMC-020 common-core Duhamel contract.

This script checks the source-pinned conditional bound and a labelled rational
oracle.  It does not construct a comparison map, a process, or a physical
interpretation.
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
    "2026-09-08-pah-omc020-core-duhamel/primary.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
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


def as_fraction(value: str) -> Fraction:
    return Fraction(value)


def bound(norm_f: Fraction, init_f: Fraction, init_g: Fraction,
          residual: Fraction, norm_g: Fraction) -> Fraction:
    return norm_f * (init_g + residual) + init_f * norm_g


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


def compute() -> tuple[dict[str, Any], bytes]:
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    raw = CONTRACT.read_bytes()
    check("contract UTF-8 LF", b"\r" not in raw, True, b"\r" not in raw)
    check("schema", contract.get("schema"), "tect/pah-omc020-core-duhamel-contract/1.0",
          contract.get("schema") == "tect/pah-omc020-core-duhamel-contract/1.0")
    check("contract id", contract.get("contract_id"), "PAH-OMC-020-CORE-DUHAMEL",
          contract.get("contract_id") == "PAH-OMC-020-CORE-DUHAMEL")
    check("task", contract.get("task_id"), "T-079", contract.get("task_id") == "T-079")
    check("conditional status", contract.get("status"), "RESEARCHER_OWNED_CONDITIONAL_CONTRACT",
          contract.get("status") == "RESEARCHER_OWNED_CONDITIONAL_CONTRACT")

    provenance = contract.get("provenance", {})
    check("source packet absent", provenance.get("source_authorized_packet_present"), False,
          provenance.get("source_authorized_packet_present") is False)
    check("constructed hypothesis", provenance.get("constructed_hypothesis"), True,
          provenance.get("constructed_hypothesis") is True)
    for field in ("claim_bearing", "active_gate_change", "physical_promotion"):
        check(f"firewall {field}", provenance.get(field), False, provenance.get(field) is False)

    parents = contract.get("parents", {})
    check("parent count", len(parents), 6, isinstance(parents, dict) and len(parents) == 6)
    source_hashes: dict[str, str] = {}
    source_docs: dict[str, dict[str, Any]] = {}
    for label, entry in sorted(parents.items()):
        relative = entry["path"]
        path = ROOT / relative
        check(f"exists {label}", path.is_file(), True, path.is_file())
        check(f"LF {label}", b"\r" not in path.read_bytes(), True, b"\r" not in path.read_bytes())
        actual = sha256(path)
        source_hashes[relative] = actual
        check(f"hash {label}", actual, entry["sha256"], actual == entry["sha256"])
        source_docs[relative] = load(path)

    pah = source_docs[parents["PAH-001"]["path"]]
    prereg = source_docs[parents["PAH-OMC-020-prereg"]["path"]]
    r512 = source_docs[parents["R-512"]["path"]]
    r530 = source_docs[parents["R-530"]["path"]]
    r534 = source_docs[parents["R-534"]["path"]]
    r536 = source_docs[parents["R-536"]["path"]]

    check("PAH packet identity", pah.get("packet_id"), "PAH-001", pah.get("packet_id") == "PAH-001")
    fixed = contract.get("fixed_scope", {})
    check("immutable model marker", "Exactly PAH-001" in fixed.get("model", ""), True,
          "Exactly PAH-001" in fixed.get("model", ""))
    check("fixed j then n", "j-to-infinity" in fixed.get("order", "") and "anchored n" in fixed.get("order", ""), True,
          "j-to-infinity" in fixed.get("order", "") and "anchored n" in fixed.get("order", ""))
    check("external time marker", "External unaccelerated stochastic Markov time" in fixed.get("time", ""), True,
          "External unaccelerated stochastic Markov time" in fixed.get("time", ""))
    check("R-512 identity", r512.get("result_id"), "R-512", r512.get("result_id") == "R-512")
    check("R-512 target is minimal", "minimal" in json.dumps(r512, ensure_ascii=True).lower(), True,
          "minimal" in json.dumps(r512, ensure_ascii=True).lower())
    check("R-530 target retained", r530.get("result_id"), "R-530", r530.get("result_id") == "R-530")
    check("R-534 D term retained", "D_n" in json.dumps(r534.get("missing_assumptions"), ensure_ascii=True), True,
          "D_n" in json.dumps(r534.get("missing_assumptions"), ensure_ascii=True))
    route_status = r536.get("route_status", {})
    form_complete = bool(route_status.get("form_route", {}).get("complete"))
    path_complete = bool(route_status.get("path_route", {}).get("complete"))
    check("R-536 form route open", form_complete, False, form_complete is False)
    check("R-536 path route open", path_complete, False, path_complete is False)

    required = contract.get("required_owner_packet", {})
    required_names = {
        "common_space_and_core",
        "correlation_identity",
        "initial_recovery",
        "residual_domain",
        "uniform_residual",
        "target_contraction",
    }
    check("six owner fields", sorted(required), sorted(required_names), set(required) == required_names)
    theorem = contract.get("conditional_theorem", {})
    check("variation identity marker", "T_min(t)(U_n v_n(g)-g)" in theorem.get("variation_of_constants", ""), True,
          "T_min(t)(U_n v_n(g)-g)" in theorem.get("variation_of_constants", ""))
    check("correlation bound marker", "D_n(f,g;T)" in theorem.get("correlation_bound", ""), True,
          "D_n(f,g;T)" in theorem.get("correlation_bound", ""))
    check("target contraction is conditional", "contract" in theorem.get("status", "").lower() or "Implication" in theorem.get("status", ""), True,
          "contract" in theorem.get("status", "").lower() or "Implication" in theorem.get("status", ""))

    fixture = contract["diagnostic_fixture"]["inputs"]
    norm_f = as_fraction(fixture["N_f"])
    init_f = as_fraction(fixture["I_f"])
    init_g = as_fraction(fixture["I_g"])
    residual = as_fraction(fixture["R_g"])
    norm_g = as_fraction(fixture["norm_g"])
    values = (norm_f, init_f, init_g, residual, norm_g)
    check("fixture inputs nonnegative", all(value >= 0 for value in values), True,
          all(value >= 0 for value in values))
    derived = bound(*values)
    check("fixture derived bound", str(derived), contract["diagnostic_fixture"]["derived_bound"],
          str(derived) == contract["diagnostic_fixture"]["derived_bound"])
    check("zero defects give zero", bound(Fraction(3, 2), Fraction(0), Fraction(0), Fraction(0), Fraction(2)), Fraction(0),
          bound(Fraction(3, 2), Fraction(0), Fraction(0), Fraction(0), Fraction(2)) == Fraction(0))
    check("initial term is retained", bound(norm_f, init_f, Fraction(0), Fraction(0), norm_g) > 0, True,
          bound(norm_f, init_f, Fraction(0), Fraction(0), norm_g) > 0)
    check("residual term is retained", bound(norm_f, Fraction(0), Fraction(0), residual, norm_g) > 0, True,
          bound(norm_f, Fraction(0), Fraction(0), residual, norm_g) > 0)
    check("fixture below one", derived < 1, True, derived < 1)

    current = contract.get("current_status", {})
    expected_current = {
        "common_space_and_core": False,
        "correlation_identity": False,
        "initial_recovery": False,
        "residual_domain": False,
        "uniform_residual": False,
        "target_contraction": True,
        "D_limit": False,
    }
    check("current owner status", current, expected_current, current == expected_current)
    check("no physical promotion", provenance.get("physical_promotion"), False, provenance.get("physical_promotion") is False)

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-core-duhamel-primary/1.0",
        "audit_id": "PAH-OMC-020-CORE-DUHAMEL-PRIMARY-001",
        "task_id": "T-079",
        "status": "PASS_CONDITIONAL_CORE_DUHAMEL_BOUND",
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
        "contract_sha256": sha256(CONTRACT),
        "owner_fields": current,
        "fixture": {
            "inputs": fixture,
            "derived_bound": str(derived),
        },
        "conditional_result": {
            "state_vector": "sup_t ||u_n^g(t)-T_min(t)g|| <= I_n(g)+R_n(g;T)",
            "correlation": "D_n(f,g;T) <= N_f[I_n(g)+R_n(g;T)] + I_n(f)||g||",
        },
        "finding": "The exact Duhamel transfer bound is algebraically and provenance-wise closed as a conditional contract, but the current pinned corpus supplies neither the common U_n/core nor the vanishing anchored-n residual and initial-recovery estimates.",
        "missing_assumptions": [
            "Source-authorized common Hilbert space, U_n, invariant cylinder core and correlation identity.",
            "Anchored-n initial recovery I_n(f)->0 for every local cylinder.",
            "Domain/absolute-continuity packet defining r_n^g and a uniform residual integral R_n(g;T)->0.",
            "R-512 minimal-form target contraction and variation-of-constants applicability on the same core.",
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
            raise SystemExit("PAH-OMC-020 core-duhamel primary replay mismatch")
    else:
        atomic_json(destination, payload)
    print(f"PAH-OMC-020 CORE DUHAMEL PRIMARY: PASS {payload['passed']}/{payload['assertion_count']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
