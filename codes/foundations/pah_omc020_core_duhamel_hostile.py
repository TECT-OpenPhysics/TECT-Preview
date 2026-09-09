#!/usr/bin/env python3
"""Hostile review for the PAH-OMC-020 core Duhamel contract.

The checks target common shortcuts: dropping an initial or residual term,
promoting a named target to an identified process, and interpreting external
Markov time physically.
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
    "2026-09-08-pah-omc020-core-duhamel/hostile.json"
)


def digest(path: Path) -> str:
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


def budget(n_f: Fraction, i_f: Fraction, i_g: Fraction,
           residual: Fraction, n_g: Fraction) -> Fraction:
    return n_f * (i_g + residual) + i_f * n_g


def main_compute() -> dict[str, Any]:
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, actual: Any, expected: Any, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("contract is conditional", contract["status"], "RESEARCHER_OWNED_CONDITIONAL_CONTRACT",
          contract["status"] == "RESEARCHER_OWNED_CONDITIONAL_CONTRACT")
    check("source authorization is false", contract["provenance"]["source_authorized_packet_present"], False,
          contract["provenance"]["source_authorized_packet_present"] is False)
    check("no active gate mutation", contract["provenance"]["active_gate_change"], False,
          contract["provenance"]["active_gate_change"] is False)
    check("no physical promotion", contract["provenance"]["physical_promotion"], False,
          contract["provenance"]["physical_promotion"] is False)

    fixed = contract["fixed_scope"]
    check("model frozen", "Exactly PAH-001" in fixed["model"], True, "Exactly PAH-001" in fixed["model"])
    check("no diagonal order", "No diagonal" in fixed["order"], True, "No diagonal" in fixed["order"])
    check("external time firewall", "no quantum, proper or Lorentzian" in fixed["time"], True,
          "no quantum, proper or Lorentzian" in fixed["time"])
    forbidden_shortcuts = ("new process", "phasewise direct sum", "rate", "carrier")
    fixed_blob = json.dumps(fixed, ensure_ascii=True).lower()
    check("fixed scope contains no invented carrier", "new carrier" not in fixed_blob, True, "new carrier" not in fixed_blob)
    check("fixed scope retains original rates", "original directed" in fixed_blob, True, "original directed" in fixed_blob)

    owners = contract["current_status"]
    absent = [key for key, value in owners.items() if key not in ("target_contraction", "D_limit") and value is False]
    check("five owner inputs absent", len(absent), 5, len(absent) == 5)
    check("target contraction only inherited", owners["target_contraction"], True, owners["target_contraction"] is True)
    check("D limit not promoted", owners["D_limit"], False, owners["D_limit"] is False)

    fixture = contract["diagnostic_fixture"]["inputs"]
    n_f = Fraction(fixture["N_f"])
    i_f = Fraction(fixture["I_f"])
    i_g = Fraction(fixture["I_g"])
    residual = Fraction(fixture["R_g"])
    n_g = Fraction(fixture["norm_g"])
    correct = budget(n_f, i_f, i_g, residual, n_g)
    dropped_initial = n_f * (i_g + residual)
    dropped_residual = n_f * i_g + i_f * n_g
    check("dropping initial defect is unsafe", correct > dropped_initial, True, correct > dropped_initial)
    check("dropping residual is unsafe", correct > dropped_residual, True, correct > dropped_residual)
    check("correct bound equals oracle", correct, Fraction(23, 256), correct == Fraction(23, 256))

    theorem_blob = json.dumps(contract["conditional_theorem"], ensure_ascii=True)
    check("variation identity is stated", "variation_of_constants" not in theorem_blob or "integral_0^t" in theorem_blob, True,
          "integral_0^t" in theorem_blob)
    check("correlation norm factor retained", "N_f" in theorem_blob and "I_n(f)" in theorem_blob, True,
          "N_f" in theorem_blob and "I_n(f)" in theorem_blob)
    check("no static target shortcut", "not construct" in theorem_blob.lower() or "Implication only" in theorem_blob, True,
          "not construct" in theorem_blob.lower() or "Implication only" in theorem_blob)
    check("no physical claim in nonclaims", all(token not in " ".join(contract["non_claims"]) for token in ("physical Pre-A conclusion", "spacetime theorem")), True,
          all(token not in " ".join(contract["non_claims"]) for token in ("physical Pre-A conclusion", "spacetime theorem")))

    return {
        "schema": "tect/pah-omc020-core-duhamel-hostile/1.0",
        "audit_id": "PAH-OMC-020-CORE-DUHAMEL-HOSTILE-001",
        "task_id": "T-079",
        "status": "PASS_HOSTILE_CORE_DUHAMEL_BOUNDARY",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks": checks,
        "checks_passed": len(checks),
        "contract_sha256": digest(CONTRACT),
        "finding": "Hostile review confirms that initial and residual defects cannot be dropped and that the named R-512 target cannot be promoted while owner fields are absent.",
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
            raise SystemExit("PAH-OMC-020 core-duhamel hostile replay mismatch")
    else:
        write_json(destination, payload)
    print(f"PAH-OMC-020 CORE DUHAMEL HOSTILE: PASS {payload['checks_passed']}/{payload['checks_passed']}; verdict=HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
