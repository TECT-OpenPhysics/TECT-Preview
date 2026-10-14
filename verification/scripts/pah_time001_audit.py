"""Replay PAH-TIME-001 provenance and admission firewalls, not a proof oracle.

Reads the frozen source definitions and the reviewed missing-law certificate.
There are no dynamics simulations, fitted constants, or mathematical theorem
checks here. Human/in-session definition review is recorded separately.
Run with --write to store the deterministic audit receipt; --check replays it.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRE = "strategy/pa-hyp/PAH-TIME-001-prereg-v1.json"
ASSESS = "strategy/pa-hyp/PAH-TIME-001-assessment-v1.json"
REVIEW = "strategy/pa-hyp/PAH-TIME-001-review-v1.json"
OUTPUT = "claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-time001/audit.json"


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def firewall(data: dict) -> None:
    assert data["verdict"] == "HOLD_FOR_EVIDENCE"
    assert data["classification"] == "auxiliary_support"
    assert data["claim_bearing"] is False
    assert data["active_gate_change"] is False
    assert data["physical_promotion"] is False
    assert data["new_result_id"] is None
    assert data["missing_law"]["status"] == "NOT_SUPPLIED_OR_ADOPTED"
    assert data["follow_on"]["automatic_successor"] is False
    assert data["follow_on"]["attempts_remaining"] == 0


def selftest(data: dict) -> list[str]:
    """Named mutation oracles test the metadata checker, not physical truth."""
    tests = []
    for key, bad in (("claim_bearing", True), ("active_gate_change", True),
                     ("physical_promotion", True), ("new_result_id", "FORBIDDEN"),
                     ("verdict", "PROVED")):
        mutated = copy.deepcopy(data)
        mutated[key] = bad
        rejected = False
        try:
            firewall(mutated)
        except AssertionError:
            rejected = True
        assert rejected, key
        tests.append("reject_" + key)
    return tests


def audit() -> dict:
    if not __debug__:
        raise RuntimeError("Assertions must be enabled; optimized Python is not an admissible replay")
    pre, assessment, review = read(PRE), read(ASSESS), read(REVIEW)
    firewall(assessment)
    assert pre["attempt_budget"] == 1  # Tooling admission limit, not derived physics.
    assert pre["source_pins"] == assessment["source_pins"]
    assert assessment["preregistration"]["sha256"] == digest(PRE)
    checked = {}
    for path, expected in pre["source_pins"].items():
        actual = digest(path)
        assert actual == expected, path
        checked[path] = actual
    parent = read("strategy/pa-hyp/PAH-001-v1.json")
    v2 = read("strategy/pa-hyp/PAH-001-v2-r2.json")
    rd = read("strategy/pa-hyp/PAH-v2-RD-001-result-v1.1.json")
    assert "d tau_v=s_v^nu dt" in parent["dynamics"]["time"]
    assert "external stochastic time" in parent["dynamics"]["time"]
    assert "no quantum KMS or proper-time identity" in parent["dynamics"]["thermal_boundary"]
    assert v2["inherited_formula_locators"]["time"] == "/dynamics/time"
    assert "W=p^(-1) sum_(b in P) Re U_b" in rd["proof"]["variance_witness"]
    assert rd["proof"]["common_limit"].startswith("NOT_CONSTRUCTED")
    assert "Only r->infinity" in rd["exact_scope"]["order"]
    for path, result_id in (("strategy/pa-hyp/PAH-v2-GD-002-result-v1.1.json", "R-573"),
                            ("strategy/pa-hyp/PAH-v2-SG-001-result-v1.json", "R-574")):
        old = read(path)
        assert old["result_id"] == result_id
        assert old["verdict"] == "DISPROVED"
    assert review["assessment_sha256"] == digest(ASSESS)
    assert review["script_sha256"] == digest("verification/scripts/pah_time001_audit.py")
    assert {r["role"] for r in review["reviews"]} == {"independent", "hostile"}
    assert all(r["verdict"] == "ACCEPT_SCOPED_AUDIT" for r in review["reviews"])
    controls = selftest(assessment)
    return {
        "schema": "tect/pah-time-provenance-replay/1.0",
        "status": "PASS_PROVENANCE_AND_SCOPE_ONLY",
        "assessment_verdict": assessment["verdict"],
        "source_hashes": checked,
        "audit_hashes": {p: digest(p) for p in (PRE, ASSESS, REVIEW, "verification/scripts/pah_time001_audit.py")},
        "mutation_controls": controls,
        "source_checks": ["declared_external_and_local_clock", "no_proper_time_identification",
                          "v2_inherits_clock", "fixed_W", "r_only_scope", "no_common_limit",
                          "preserved_R573_R574", "reviewed_assessment_hash", "zero_successor_budget"],
        "non_claims": "No new analytic/Lean proof, dynamics calculation, empirical evidence, physical clock or mainline promotion. String/hash checks do not establish semantic completeness.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.write:
        out = ROOT / OUTPUT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        assert read(OUTPUT) == result, "stored audit differs from current deterministic replay"
    print(json.dumps({"status": result["status"], "source_count": len(result["source_hashes"]),
                      "mutation_controls": len(result["mutation_controls"]),
                      "verdict": result["assessment_verdict"]}, sort_keys=True))


if __name__ == "__main__":
    main()
