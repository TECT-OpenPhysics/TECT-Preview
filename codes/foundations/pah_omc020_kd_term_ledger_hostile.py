#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 K/D term ledger.

The mutations are deliberately in-memory.  They test that a missing common
comparison, uniform limit, or target-process identification cannot be hidden
by relabelling a finite or conditional input.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-kd-term-ledger-contract-v1.json"
OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-kd-term-ledger/hostile.json"
)


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


def admit(flags: dict[str, bool], *, owner_authorized: bool = True, conditional: bool = False) -> bool:
    """The contract's fail-closed admission predicate, reconstructed locally."""
    return owner_authorized and not conditional and all(flags.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, condition: bool) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    fields = list(contract["admission_predicate"]["required_full_fields"])
    base = {field: True for field in fields}
    check("all fields admit only with owner", admit(base), True, admit(base))
    for field in fields:
        mutation = dict(base)
        mutation[field] = False
        check(f"drop {field} rejects", admit(mutation), False, not admit(mutation))

    # A conditional finite result may have every algebraic flag, but it is not
    # source-authorized for the anchored comparison.
    check("conditional finite result rejected", admit(base, conditional=True), False, not admit(base, conditional=True))
    check("unowned result rejected", admit(base, owner_authorized=False), False, not admit(base, owner_authorized=False))

    current = contract["admission_predicate"]["current_expected"]
    check("current contract is not admitted", all(current.values()), False, not all(current.values()))
    check("common comparison is currently absent", current["common_comparison"], False, current["common_comparison"] is False)
    check("uniform K limit is currently absent", current["uniform_K_limit"], False, current["uniform_K_limit"] is False)
    check("target process identification is currently absent", current["target_process_identification"], False, current["target_process_identification"] is False)
    check("D limit is currently absent", current["D_limit"], False, current["D_limit"] is False)

    # Naming a target or flipping a verdict cannot create the missing fields.
    relabel = dict(current)
    relabel["target_process_identification"] = True
    check("target relabel alone does not admit", all(relabel.values()), False, not all(relabel.values()))
    relabel["common_comparison"] = True
    check("common relabel without uniform K still rejects", all(relabel.values()), False, not all(relabel.values()))
    relabel["uniform_K_limit"] = True
    relabel["D_limit"] = True
    check("synthetic all-true fixture is separately marked", admit(relabel), True, admit(relabel))
    check("synthetic fixture is not current evidence", relabel == current, False, relabel != current)

    check("physical firewall remains false", contract["physical_promotion"], False, contract["physical_promotion"] is False)
    check("time text stays external", "External stochastic Markov time" in contract["fixed_scope"]["time"], True, "External stochastic Markov time" in contract["fixed_scope"]["time"])

    payload = {
        "schema": "tect/pah-omc020-kd-term-ledger-hostile/1.0",
        "audit_id": "PAH-OMC-020-KD-TERM-LEDGER-HOSTILE-001",
        "task_id": "T-077",
        "status": "PASS_HOSTILE_FAIL_CLOSED",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "assertion_count": len(checks),
        "passed": len(checks),
        "failed": 0,
        "checks": checks,
        "required_fields": fields,
        "finding": "Hostile mutations cannot promote a conditional finite term, relabel the target, or drop a common/K/D field; the contract remains fail-closed.",
        "next_single_question": contract["next_single_question"],
        "non_claims": contract["non_claims"],
        "implementation": "Fresh in-memory mutation suite; no source or primary-verifier import.",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if not destination.is_file() or destination.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 hostile K/D ledger replay mismatch")
    else:
        write_atomic(destination, encoded)
    print(f"PAH-OMC-020 K/D HOSTILE: PASS {len(checks)}/{len(checks)}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
