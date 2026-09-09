#!/usr/bin/env python3
"""Audit which registered results supply the PAH-OMC-020 K/D terms.

This is a source crosswalk, not a new dynamics construction.  It reads only
the hash-pinned PAH-OMC-020 records and separates finite/conditional formulae
from the common-space, uniform and target-process fields still needed by the
sequential gluing contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-kd-term-ledger/primary.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def text_of(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def compute() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": actual,
            "expected": expected,
        })
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    raw_contract = CONTRACT.read_bytes()
    check(
        "contract is UTF-8 LF",
        b"\r" not in raw_contract,
        True,
        b"\r" not in raw_contract and raw_contract.decode("utf-8").encode("utf-8") == raw_contract,
    )
    check(
        "contract schema",
        contract.get("schema"),
        "tect/pah-omc020-kd-term-ledger-contract/1.0",
        contract.get("schema") == "tect/pah-omc020-kd-term-ledger-contract/1.0",
    )
    check("contract version", contract.get("version"), "1.0.0", contract.get("version") == "1.0.0")
    check("contract task", contract.get("task_id"), "T-077", contract.get("task_id") == "T-077")
    for field in ("claim_bearing", "active_gate_change", "physical_promotion", "conditional"):
        expected = field == "conditional"
        check(f"firewall {field}", contract.get(field), expected, contract.get(field) is expected)
    check(
        "fixed j-before-n order",
        contract.get("fixed_scope", {}).get("order"),
        "j tends to infinity at fixed n first, followed by the declared anchored n exhaustion; no diagonal or reversed order.",
        contract.get("fixed_scope", {}).get("order")
        == "j tends to infinity at fixed n first, followed by the declared anchored n exhaustion; no diagonal or reversed order.",
    )
    check(
        "external-time firewall",
        "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""),
        True,
        "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""),
    )
    check(
        "no-new-map firewall",
        "do not construct a new map" in contract.get("fixed_scope", {}).get("comparison", ""),
        True,
        "do not construct a new map" in contract.get("fixed_scope", {}).get("comparison", ""),
    )

    pins = contract.get("source_pins", {})
    check("source pin set is nonempty", len(pins), 10, isinstance(pins, dict) and len(pins) == 10)
    source: dict[str, dict[str, Any]] = {}
    actual_hashes: dict[str, str] = {}
    for relative, expected_hash in sorted(pins.items()):
        path = ROOT / relative
        check(f"source exists {relative}", path.is_file(), True, path.is_file())
        actual = sha256(path)
        actual_hashes[relative] = actual
        check(f"source hash {relative}", actual, expected_hash, actual == expected_hash)
        if path.suffix == ".json":
            source[relative] = load_json(path)

    pah = source["strategy/pa-hyp/PAH-001-v1.json"]
    prereg = source["strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"]
    r510 = source["strategy/pa-hyp/PAH-OMC-017-result-v1.json"]
    r493 = source["strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"]
    r512 = source["strategy/pa-hyp/PAH-OMC-019-result-v1.json"]
    r514 = source["strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json"]
    r517 = source["strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json"]
    r534 = source["strategy/pa-hyp/PAH-OMC-020-sequential-gluing-result-v1.json"]
    r533 = source["strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json"]

    check("PAH identity is immutable", pah.get("schema"), "tect/pre-a-researcher-hypothesis/1.0", pah.get("schema") == "tect/pre-a-researcher-hypothesis/1.0")
    prereg_scope = prereg.get("scope", {})
    check("prereg has original functional", "Exact PAH-001 functional" in prereg_scope.get("model", ""), True, "Exact PAH-001 functional" in prereg_scope.get("model", ""))
    check("prereg retains order", "First j" in prereg_scope.get("regulator_order", ""), True, "First j" in prereg_scope.get("regulator_order", ""))
    check("prereg retains external Markov time", "external unaccelerated Markov time" in prereg_scope.get("time", ""), True, "external unaccelerated Markov time" in prereg_scope.get("time", ""))

    # These booleans are derived from the registered records.  They are not
    # numerical estimates and do not invent a source-owned process.
    fixed_n_passage = (
        r514.get("result_id") == "R-514"
        and r514.get("verdict") == "PASS"
        and "j->infinity" in text_of(r514.get("exact_scope"))
        and "uniformly" in r514.get("conclusion", "")
        and "finite T" in r514.get("conclusion", "")
    )
    state_formula = (
        r510.get("result_id") == "R-510"
        and r510.get("verdict") == "PASS"
        and isinstance(r510.get("conclusion"), dict)
        and isinstance(r510.get("conclusion", {}).get("cauchy_bound"), str)
        and isinstance(r510.get("conclusion", {}).get("explicit_stage"), str)
    )
    stabilization_formula = (
        r493.get("status", {}).get("exact_scope_closed") is True
        and r493.get("status", {}).get("stage2_status") == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP"
        and "eventual" in r493.get("schema", "")
    )
    boundary_formula = (
        r517.get("result_id") == "R-517"
        and r517.get("verdict") == "PASS"
        and "conditionally" in r517.get("conclusion", {}).get("n4_status", "")
        and "source-authorized common U_n" in " ".join(r517.get("missing_assumptions", []))
    )
    owner_empty = (
        r533.get("verdict") == "HOLD_FOR_EVIDENCE"
        and r533.get("owner_packet_contract", {}).get("strict_candidates") == []
        and "hash-pinned" in r533.get("owner_packet_contract", {}).get("admission", "")
        and "not authority" in r533.get("owner_packet_contract", {}).get("admission", "")
    )
    common_comparison = not owner_empty
    uniform_k_limit = False
    target_gates = " ".join(r512.get("remaining_gates", [])).lower()
    target_process_identification = not (
        "target-process/r-512" in " ".join(r534.get("missing_assumptions", [])).lower()
        or "minimal-form identification" in " ".join(r534.get("missing_assumptions", [])).lower()
        or "semigroup convergence" in target_gates
    )
    d_limit = target_process_identification

    flags = {
        "fixed_n_passage": fixed_n_passage,
        "state_formula": state_formula,
        "stabilization_formula": stabilization_formula,
        "boundary_formula": boundary_formula,
        "common_comparison": common_comparison,
        "uniform_K_limit": uniform_k_limit,
        "target_process_identification": target_process_identification,
        "D_limit": d_limit,
    }
    expected = contract.get("admission_predicate", {}).get("current_expected", {})
    check("required flag names", sorted(flags), sorted(contract.get("admission_predicate", {}).get("required_full_fields", [])), set(flags) == set(contract.get("admission_predicate", {}).get("required_full_fields", [])))
    check("current expected flags", flags, expected, flags == expected)
    check("R-534 keeps K open", "K" in " ".join(r534.get("missing_assumptions", [])), True, "K" in " ".join(r534.get("missing_assumptions", [])))
    check("R-534 keeps D open", "D_n" in " ".join(r534.get("missing_assumptions", [])), True, "D_n" in " ".join(r534.get("missing_assumptions", [])))
    check("R-512 target is not identified", target_process_identification, False, target_process_identification is False)
    check("owner packet remains empty", owner_empty, True, owner_empty)
    admitted = all(flags.values())
    check("full K/D admission is rejected", admitted, False, admitted is False)
    check("scientific verdict stays HOLD", r534.get("verdict"), "HOLD_FOR_EVIDENCE", r534.get("verdict") == "HOLD_FOR_EVIDENCE")

    coverage = {
        "J_fixed_n": {
            "status": "PASS_REGISTERED_R514" if fixed_n_passage else "MISSING",
            "formula": fixed_n_passage,
            "compact_time_uniformity": fixed_n_passage,
            "source": "R-514",
            "limitation": "fixed n only; does not identify R-512 target",
        },
        "K_state": {
            "status": "PARTIAL_LOCAL_R510" if state_formula else "MISSING",
            "formula": state_formula,
            "local_state_modulus": state_formula,
            "source": "R-510",
            "limitation": "stationary local-state passage is not a path or all-time anchored comparison",
        },
        "K_stabilization": {
            "status": "PARTIAL_EVENTUAL_R493" if stabilization_formula else "MISSING",
            "formula": stabilization_formula,
            "eventual_local_identity": stabilization_formula,
            "source": "R-493",
            "limitation": "finite pointwise generator identity lacks the common compact-time K bound",
        },
        "K_boundary": {
            "status": "CONDITIONAL_FINITE_R517" if boundary_formula else "MISSING",
            "formula": boundary_formula,
            "finite_word_tail": boundary_formula,
            "source": "R-517",
            "limitation": "conditional finite-fibre attribution lacks source-authorized varying-space control",
        },
        "K_uniform": {
            "status": "ABSENT_ALL_TERM_BOUND" if not uniform_k_limit else "PRESENT",
            "formula": uniform_k_limit,
            "source": "R-534 contract",
            "limitation": "no one K_(n,m) with lim_m limsup_n=0 is instantiated",
        },
        "D_target": {
            "status": "ABSENT_R512_PROCESS_LINK" if not target_process_identification else "PRESENT",
            "formula": target_process_identification,
            "source": "R-512 plus source-authorized owner packet",
            "limitation": "R-512 closes a fixed-H form, not identification of the finite process",
        },
    }
    for name, row in coverage.items():
        check(f"coverage row {name}", isinstance(row.get("status"), str) and isinstance(row.get("formula"), bool), True, isinstance(row.get("status"), str) and isinstance(row.get("formula"), bool))

    missing = [
        "one source-authorized common comparison (U_n or equivalent path/common-Hilbert realization)",
        "one all-cylinder compact-time K_(n,m) bound with lim_m limsup_n K_(n,m)=0",
        "one source-authorized target-process/R-512 minimal-form identification with D_n -> 0",
    ]
    return {
        "schema": "tect/pah-omc020-kd-term-ledger/1.0",
        "audit_id": "PAH-OMC-020-KD-TERM-LEDGER-001",
        "task_id": "T-077",
        "status": "PASS_TERM_COVERAGE_LEDGER",
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
        "source_hashes": actual_hashes,
        "coverage": coverage,
        "required_fields": flags,
        "full_kd_admitted": admitted,
        "finding": "The ledger separates registered finite/conditional inputs from the missing common comparison, all-cylinder uniform K bound and R-512 target-process defect. The current evidence therefore remains HOLD_FOR_EVIDENCE; no owner packet or process is synthesized.",
        "missing_assumptions": missing,
        "next_single_question": contract["next_single_question"],
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
        "code_sha256": sha256(Path(__file__)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 K/D term-ledger replay mismatch")
    else:
        atomic_write(destination, encoded)
    print(f"PAH-OMC-020 K/D TERM LEDGER: PASS {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
