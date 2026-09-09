#!/usr/bin/env python3
"""Independent reconstruction of the PAH-OMC-020 K/D coverage ledger.

The implementation deliberately does not import the primary verifier.  It
reconstructs the source pins and the coverage decision from the frozen result
records, while keeping the external Markov-time and non-promotion firewalls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-contract-v1.json"
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-kd-term-ledger/independent.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def obj(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output

    contract = obj(CONTRACT)
    checks: list[dict[str, Any]] = []

    def verify(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    verify("contract schema", contract.get("schema"), "tect/pah-omc020-kd-term-ledger-contract/1.0", contract.get("schema") == "tect/pah-omc020-kd-term-ledger-contract/1.0")
    verify("contract version", contract.get("version"), "1.0.0", contract.get("version") == "1.0.0")
    verify("contract is auxiliary", contract.get("classification"), "auxiliary_support", contract.get("classification") == "auxiliary_support")
    verify("claim bearing firewall", contract.get("claim_bearing"), False, contract.get("claim_bearing") is False)
    verify("gate firewall", contract.get("active_gate_change"), False, contract.get("active_gate_change") is False)
    verify("physical firewall", contract.get("physical_promotion"), False, contract.get("physical_promotion") is False)
    verify("order firewall", "j tends to infinity at fixed n first" in contract.get("fixed_scope", {}).get("order", ""), True, "j tends to infinity at fixed n first" in contract.get("fixed_scope", {}).get("order", ""))
    verify("time firewall", "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""), True, "External stochastic Markov time" in contract.get("fixed_scope", {}).get("time", ""))

    pins = contract.get("source_pins", {})
    verify("ten pinned inputs", len(pins), 10, isinstance(pins, dict) and len(pins) == 10)
    values: dict[str, dict[str, Any]] = {}
    hashes: dict[str, str] = {}
    for rel, expected in sorted(pins.items()):
        path = ROOT / rel
        verify(f"exists {rel}", path.is_file(), True, path.is_file())
        actual = digest(path)
        hashes[rel] = actual
        verify(f"hash {rel}", actual, expected, actual == expected)
        values[rel] = obj(path)

    pa = values["strategy/pa-hyp/PAH-001-v1.json"]
    prereg = values["strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"]
    r510 = values["strategy/pa-hyp/PAH-OMC-017-result-v1.json"]
    r493 = values["strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"]
    r512 = values["strategy/pa-hyp/PAH-OMC-019-result-v1.json"]
    r514 = values["strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json"]
    r517 = values["strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json"]
    r534 = values["strategy/pa-hyp/PAH-OMC-020-sequential-gluing-result-v1.json"]
    r533 = values["strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json"]

    verify("PAH schema", pa.get("schema"), "tect/pre-a-researcher-hypothesis/1.0", pa.get("schema") == "tect/pre-a-researcher-hypothesis/1.0")
    verify("original model marker", "Exact PAH-001 functional" in prereg.get("scope", {}).get("model", ""), True, "Exact PAH-001 functional" in prereg.get("scope", {}).get("model", ""))
    verify("original rate marker", "original directed" in prereg.get("scope", {}).get("model", ""), True, "original directed" in prereg.get("scope", {}).get("model", ""))

    # Independent derivation: use field presence and exact result statuses,
    # not any boolean imported from the primary implementation.
    j_pass = (
        r514.get("result_id") == "R-514"
        and r514.get("verdict") == "PASS"
        and "j->infinity" in json.dumps(r514.get("exact_scope"), ensure_ascii=True)
        and "uniformly" in str(r514.get("conclusion"))
    )
    state_pass = (
        r510.get("result_id") == "R-510"
        and r510.get("verdict") == "PASS"
        and set((r510.get("conclusion") or {}).keys()) >= {"cauchy_bound", "explicit_stage"}
    )
    stabilization_pass = (
        r493.get("status", {}).get("exact_scope_closed") is True
        and r493.get("status", {}).get("weak_gibbs_l2") == "NOT_PROVED"
    )
    boundary_pass = (
        r517.get("result_id") == "R-517"
        and r517.get("verdict") == "PASS"
        and "conditionally" in r517.get("conclusion", {}).get("n4_status", "")
    )
    owner_contract = r533.get("owner_packet_contract", {})
    owner_absent = (
        r533.get("verdict") == "HOLD_FOR_EVIDENCE"
        and owner_contract.get("strict_candidates") == []
        and "hash-pinned" in owner_contract.get("admission", "")
    )
    missing_text = " ".join(str(item) for item in r534.get("missing_assumptions", []))
    target_gates = " ".join(str(item) for item in r512.get("remaining_gates", []))
    common = not owner_absent
    uniform = "lim_m" in missing_text and "K" not in missing_text
    # The explicit R-534 missing-assumption list is the authoritative source
    # for the aggregate flags; no alternate process is inferred here.
    uniform = not any("uniform" in item.lower() and "K" in item for item in r534.get("missing_assumptions", []))
    target = not any(marker in (missing_text + " " + target_gates).lower() for marker in ("minimal-form", "semigroup convergence", "process identification"))
    flags = {
        "fixed_n_passage": j_pass,
        "state_formula": state_pass,
        "stabilization_formula": stabilization_pass,
        "boundary_formula": boundary_pass,
        "common_comparison": common,
        "uniform_K_limit": uniform,
        "target_process_identification": target,
        "D_limit": target,
    }
    expected = contract.get("admission_predicate", {}).get("current_expected", {})
    verify("owner packet absence", owner_absent, True, owner_absent)
    verify("R-534 scientific hold", r534.get("verdict"), "HOLD_FOR_EVIDENCE", r534.get("verdict") == "HOLD_FOR_EVIDENCE")
    verify("independent flag partition", flags, expected, flags == expected)
    verify("full admission false", all(flags.values()), False, all(flags.values()) is False)
    verify("R-512 process link remains open", target, False, target is False)
    verify("R-534 K limit remains open", uniform, False, uniform is False)
    verify("R-534 comparison remains open", common, False, common is False)

    coverage = {
        "J_fixed_n": {"status": "PASS_REGISTERED_R514" if j_pass else "MISSING", "source": "R-514", "formula": j_pass},
        "K_state": {"status": "PARTIAL_LOCAL_R510" if state_pass else "MISSING", "source": "R-510", "formula": state_pass},
        "K_stabilization": {"status": "PARTIAL_EVENTUAL_R493" if stabilization_pass else "MISSING", "source": "R-493", "formula": stabilization_pass},
        "K_boundary": {"status": "CONDITIONAL_FINITE_R517" if boundary_pass else "MISSING", "source": "R-517", "formula": boundary_pass},
        "K_uniform": {"status": "ABSENT_ALL_TERM_BOUND" if not uniform else "PRESENT", "source": "R-534", "formula": uniform},
        "D_target": {"status": "ABSENT_R512_PROCESS_LINK" if not target else "PRESENT", "source": "R-512", "formula": target},
    }
    for name, row in coverage.items():
        verify(f"coverage {name}", isinstance(row["formula"], bool) and isinstance(row["status"], str), True, isinstance(row["formula"], bool) and isinstance(row["status"], str))

    payload = {
        "schema": "tect/pah-omc020-kd-term-ledger/1.0",
        "audit_id": "PAH-OMC-020-KD-TERM-LEDGER-INDEPENDENT-001",
        "task_id": "T-077",
        "status": "PASS_INDEPENDENT_TERM_COVERAGE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "source_hashes": hashes,
        "coverage": coverage,
        "required_fields": flags,
        "full_kd_admitted": all(flags.values()),
        "finding": "Independent reconstruction agrees that the registered finite and conditional terms do not supply the common comparison, uniform K limit or R-512 target-process defect.",
        "next_single_question": contract["next_single_question"],
        "reproduction": contract["reproduction"],
        "non_claims": contract["non_claims"],
        "implementation": "Fresh hash/field reconstruction; no import of the primary verifier.",
        "code_sha256": digest(Path(__file__)),
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 independent K/D ledger replay mismatch")
    else:
        write_atomic(destination, encoded)
    print(f"PAH-OMC-020 K/D INDEPENDENT: PASS {len(checks)}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
