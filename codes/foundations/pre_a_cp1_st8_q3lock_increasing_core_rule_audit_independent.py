#!/usr/bin/env python3
"""Non-importing finite control for the R-439 adaptive support rule.

The control reads only the parent independent row outputs and the R-439
manifest.  It recomputes point log-ratios itself; it does not import or trust
the primary implementation and it makes no uniformity claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any


getcontext().prec = 70
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-increasing-core-rule-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-increasing_core_rule_audit/independent.json"


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


def classify(row: list[Decimal], threshold: Decimal) -> dict[str, Any]:
    if not row or any(value <= 0 for value in row):
        raise AssertionError("independent row must be nonempty and positive")
    maximum_index = max(range(len(row)), key=lambda index: row[index])
    maximum = row[maximum_index]
    phi = [maximum.ln() - value.ln() for value in row]
    core = [index for index, value in enumerate(phi) if value < threshold]
    tail = [index for index, value in enumerate(phi) if value > threshold]
    ambiguous = [index for index, value in enumerate(phi) if not (value < threshold or value > threshold)]
    return {
        "maximum_index": maximum_index,
        "core": core,
        "tail": tail,
        "ambiguous": ambiguous,
        "phi_values": [str(value) for value in phi],
        "row_sum": str(sum(row)),
        "tail_mass": str(sum(row[index] for index in tail)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selection = manifest["selection_contract"]
    rule = manifest["rule"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    expected_selection = {
        "volume": 2,
        "beta": "8",
        "orientation": "right",
        "row_kind": "unconditional_one_site_marginal",
        "target_emission_ordinal": 0,
        "tail_threshold": "4",
        "row_selection_frozen_before_classification": True,
        "no_gap_based_row_selection": True,
    }
    check("manifest identity", manifest["result_id"] == "R-439" and manifest["exploration_id"] == "EXP-001284" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-439/EXP-001284/false", "provenance")
    check("selection contract", selection == expected_selection, selection, expected_selection, "contract")
    check("rule contract", rule["name"] == "directed-log-ratio-cutoff-adaptive-core" and rule["support_is_recomputed_per_cutoff"] is True and rule["support_is_not_required_to_be_nested"] is True and rule["ambiguous_criterion"] == "otherwise", rule, "fixed adaptive rule", "contract")

    cases: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        parent_manifest_path = ROOT / case["manifest"]
        independent_path = ROOT / case["independent_run"]
        parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
        parent = json.loads(independent_path.read_text(encoding="utf-8"))
        check(f"d={case['cutoff_dimension']} parent identity", parent_manifest["result_id"] in {"R-435", "R-436", "R-438"} and parent["result_id"] == parent_manifest["result_id"] and parent["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS", [parent_manifest["result_id"], parent["result_id"], parent["verdict"]], "independent certified parent", "parent")
        fixed = parent["derived"]["fixed_row"]
        common = (fixed["volume"], fixed["beta"], fixed["orientation"], fixed["row_kind"], fixed["target_emission_ordinal"], fixed["tail_threshold"])
        expected_common = (selection["volume"], selection["beta"], selection["orientation"], selection["row_kind"], selection["target_emission_ordinal"], selection["tail_threshold"])
        check(f"d={case['cutoff_dimension']} row identity", common == expected_common and fixed["cutoff_dimension"] == case["cutoff_dimension"], common, expected_common, "contract")
        values = [Decimal(str(value)) for value in parent["derived"]["conditional_row"]]
        check(f"d={case['cutoff_dimension']} row length", len(values) == case["cutoff_dimension"], len(values), case["cutoff_dimension"], "row")
        check(f"d={case['cutoff_dimension']} finite values", all(value.is_finite() and value > 0 for value in values), "positive finite row", "positive finite row", "row")
        classified = classify(values, Decimal(selection["tail_threshold"]))
        check(f"d={case['cutoff_dimension']} normalization", abs(sum(values) - Decimal(1)) < Decimal("1e-12"), classified["row_sum"], "within 1e-12 of one", "normalization")
        check(f"d={case['cutoff_dimension']} no threshold ambiguity", classified["ambiguous"] == [], classified["ambiguous"], [], "threshold")
        check(f"d={case['cutoff_dimension']} expected core", classified["core"] == case["expected_core"], classified["core"], case["expected_core"], "support")
        check(f"d={case['cutoff_dimension']} expected tail", classified["tail"] == case["expected_tail"], classified["tail"], case["expected_tail"], "support")
        check(f"d={case['cutoff_dimension']} partition", sorted(classified["core"] + classified["tail"]) == list(range(case["cutoff_dimension"])), sorted(classified["core"] + classified["tail"]), list(range(case["cutoff_dimension"])), "support")
        cases.append({"cutoff_dimension": case["cutoff_dimension"], "maximum_index": classified["maximum_index"], "core": classified["core"], "tail": classified["tail"], "ambiguous": classified["ambiguous"], "phi_values": classified["phi_values"], "row_sum": classified["row_sum"], "tail_mass": classified["tail_mass"], "parent_manifest": case["manifest"], "parent_run": case["independent_run"]})

    cardinalities = [len(case["core"]) for case in cases]
    expected_cardinalities = [len(case["expected_core"]) for case in manifest["cases"]]
    check("adaptive cardinalities", cardinalities == expected_cardinalities, cardinalities, expected_cardinalities, "support")
    check("independent finite scope", manifest["scope"]["cutoff_adaptive_core_rule_defined"] and manifest["scope"]["directed_threshold_classification_certified"] and manifest["scope"]["all_coordinates_unambiguous"], manifest["scope"], "finite rule flags true", "scope")
    check("no uniform promotion", not manifest["scope"]["increasing_core_tail_modulus_closed"] and not manifest["scope"]["common_core_closed"] and not manifest["scope"]["c6_closed"] and not manifest["scope"]["pre_a_closed"], manifest["scope"], "uniform/common-core/physical flags false", "scope")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r439-independent/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-439",
        "exploration_id": "EXP-001284",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_ADAPTIVE_RULE_CONTROL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"selection_contract": selection, "rule": rule, "cases": cases, "core_cardinalities": cardinalities, "raw_index_nested": False, "core_cardinality_monotone": False, "all_coordinates_unambiguous": True},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), **{case["independent_run"]: sha256(ROOT / case["independent_run"]) for case in manifest["cases"]}},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED NON-IMPORTING FINITE CONTROL; NO UNIFORM OR PHYSICAL PROMOTION",
        "non_claims": manifest["non_claims"] + ["The independent point-log control is not a directed interval proof."],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-439 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} core_cardinalities={cardinalities}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_ADAPTIVE_RULE_CONTROL"
        assert payload["derived"]["all_coordinates_unambiguous"] is True
        print("R-439 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
