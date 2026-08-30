#!/usr/bin/env python3
"""Hostile mutation firewall for the finite R-439 support-rule audit."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-increasing-core-rule-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-increasing_core_rule_audit/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


def baseline_valid(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    expected_cases = [(case["expected_core"], case["expected_tail"]) for case in baseline["cases"]]
    candidate_cases = [(case["expected_core"], case["expected_tail"]) for case in candidate["cases"]]
    finite_flags = (
        candidate["scope"]["row_contract_identity_checked"]
        and candidate["scope"]["directed_threshold_classification_certified"]
        and candidate["scope"]["cutoff_adaptive_core_rule_defined"]
        and candidate["scope"]["all_coordinates_unambiguous"]
        and candidate["scope"]["nested_core_certified"] is False
        and candidate["scope"]["core_cardinality_monotonicity_certified"] is False
    )
    closed_flags_false = all(not value for key, value in candidate["scope"].items() if key.endswith("_closed"))
    return (
        candidate["result_id"] == baseline["result_id"] == "R-439"
        and candidate["exploration_id"] == baseline["exploration_id"] == "EXP-001284"
        and candidate["claim_bearing"] is False
        and candidate["status"] == "INCREASING_CORE_RULE_AUDITED"
        and candidate["selection_contract"] == baseline["selection_contract"]
        and candidate["rule"] == baseline["rule"]
        and candidate_cases == expected_cases
        and finite_flags
        and closed_flags_false
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("baseline finite scope", baseline_valid(manifest, manifest), [manifest["result_id"], manifest["claim_bearing"], manifest["status"]], "R-439 finite non-claiming baseline", "scope")
    mutations: list[tuple[str, dict[str, Any], str]] = []

    candidate = copy.deepcopy(manifest)
    candidate["selection_contract"]["tail_threshold"] = "3.9"
    mutations.append(("threshold substitution", candidate, "tail threshold must remain four"))

    candidate = copy.deepcopy(manifest)
    candidate["rule"]["threshold"] = "4.1"
    mutations.append(("rule threshold drift", candidate, "rule threshold must match selection"))

    candidate = copy.deepcopy(manifest)
    candidate["rule"]["support_is_recomputed_per_cutoff"] = False
    mutations.append(("fixed-support substitution", candidate, "support must be recomputed per cutoff"))

    candidate = copy.deepcopy(manifest)
    candidate["cases"][1]["expected_core"] = candidate["cases"][1]["expected_core"] + [4]
    mutations.append(("support oracle alteration", candidate, "declared finite support oracle is immutable"))

    candidate = copy.deepcopy(manifest)
    candidate["scope"]["all_coordinates_unambiguous"] = False
    mutations.append(("ambiguity admission", candidate, "ambiguous threshold coordinates cannot be certified"))

    candidate = copy.deepcopy(manifest)
    candidate["scope"]["nested_core_certified"] = True
    mutations.append(("nested-core promotion", candidate, "nesting remains open"))

    candidate = copy.deepcopy(manifest)
    candidate["scope"]["increasing_core_tail_modulus_closed"] = True
    mutations.append(("uniform-tail promotion", candidate, "uniform tail modulus remains open"))

    candidate = copy.deepcopy(manifest)
    candidate["claim_bearing"] = True
    mutations.append(("claim promotion", candidate, "result is claim-nonbearing"))

    for name, candidate, reason in mutations:
        check(name, not baseline_valid(candidate, manifest), "rejected", reason, "adversarial")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r439-hostile/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-439",
        "exploration_id": "EXP-001284",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "assertions": checks,
        "mutations": [{"name": name, "reason": reason} for name, _candidate, reason in mutations],
        "scope": {"hostile_mutations_rejected": True, "uniform_promotion_rejected": True, "physical_promotion_rejected": True},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "evidence_level": "T0 / EXECUTED HOSTILE FINITE-SCOPE FIREWALL",
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-439 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        assert payload["assertion_count"] == 9
        print("R-439 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
