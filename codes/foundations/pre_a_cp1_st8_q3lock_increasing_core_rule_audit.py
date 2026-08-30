#!/usr/bin/env python3
"""Audit a cutoff-adaptive threshold-four core rule on the R-435/R-436/R-438 rows.

The parent interval runs are the numerical authorities.  This script applies
one preregistered directed log-ratio rule to each already certified row and
records the finite support changes.  It does not infer a nested core or a
uniform tail modulus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any


getcontext().prec = 90
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-increasing-core-rule-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-increasing_core_rule_audit/primary.json"


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


def directed_classification(lower: list[Decimal], upper: list[Decimal], threshold: Decimal) -> dict[str, Any]:
    if len(lower) != len(upper) or not lower:
        raise AssertionError("row endpoint lengths are invalid")
    if any(value <= 0 for value in lower + upper):
        raise AssertionError("row endpoints must be positive")
    midpoint = [(lo + hi) / 2 for lo, hi in zip(lower, upper)]
    maximum_index = max(range(len(midpoint)), key=lambda index: midpoint[index])
    maximum_lower = lower[maximum_index]
    maximum_upper = upper[maximum_index]
    core: list[int] = []
    tail: list[int] = []
    ambiguous: list[int] = []
    intervals: list[list[str]] = []
    for index, (lo, hi) in enumerate(zip(lower, upper)):
        phi_lower = maximum_lower.ln() - hi.ln()
        phi_upper = maximum_upper.ln() - lo.ln()
        intervals.append([str(phi_lower), str(phi_upper)])
        if phi_upper < threshold:
            core.append(index)
        elif phi_lower > threshold:
            tail.append(index)
        else:
            ambiguous.append(index)
    return {
        "maximum_index": maximum_index,
        "core": core,
        "tail": tail,
        "ambiguous": ambiguous,
        "phi_intervals": intervals,
        "tail_mass_lower": str(sum(lower[index] for index in tail)),
        "tail_mass_upper": str(sum(upper[index] for index in tail)),
        "row_mass_lower": str(sum(lower)),
        "row_mass_upper": str(sum(upper)),
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    selection = manifest["selection_contract"]
    rule = manifest["rule"]
    check("manifest identity", manifest["result_id"] == "R-439" and manifest["exploration_id"] == "EXP-001284" and manifest["claim_bearing"] is False and manifest["status"] == "INCREASING_CORE_RULE_AUDITED", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"], manifest["status"]], "R-439/EXP-001284/false/finite", "provenance")
    check("selection contract", selection == {"volume": 2, "beta": "8", "orientation": "right", "row_kind": "unconditional_one_site_marginal", "target_emission_ordinal": 0, "tail_threshold": "4", "row_selection_frozen_before_classification": True, "no_gap_based_row_selection": True}, selection, "frozen V=2 beta=8 right ordinal-zero row", "contract")
    check("rule contract", rule["name"] == "directed-log-ratio-cutoff-adaptive-core" and rule["support_is_recomputed_per_cutoff"] is True and rule["ambiguous_criterion"] == "otherwise", rule, "directed cutoff-adaptive rule", "contract")
    cases: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        parent_manifest_path = REPO / case["manifest"]
        run_path = REPO / case["primary_run"]
        parent = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
        parent_run = json.loads(run_path.read_text(encoding="utf-8"))
        source = parent["source_contract"]
        check(f"d={case['cutoff_dimension']} parent identity", parent["result_id"] in {"R-435", "R-436", "R-438"} and parent_run["result_id"] == parent["result_id"] and parent_run["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED", [parent["result_id"], parent_run["result_id"], parent_run["verdict"]], "certified parent", "parent")
        common = (source["volume"], source["beta"], source["orientation"], source["row_kind"], source["target_emission_ordinal"], source["tail_threshold"])
        expected_common = (selection["volume"], selection["beta"], selection["orientation"], selection["row_kind"], selection["target_emission_ordinal"], selection["tail_threshold"])
        check(f"d={case['cutoff_dimension']} row identity", common == expected_common and source["cutoff_dimension"] == case["cutoff_dimension"], common, expected_common, "contract")
        lower = [Decimal(value) for value in parent_run["derived"]["conditional_row_lower"]]
        upper = [Decimal(value) for value in parent_run["derived"]["conditional_row_upper"]]
        check(f"d={case['cutoff_dimension']} row length", len(lower) == case["cutoff_dimension"] and len(upper) == case["cutoff_dimension"], [len(lower), len(upper)], case["cutoff_dimension"], "row")
        classified = directed_classification(lower, upper, Decimal(selection["tail_threshold"]))
        check(f"d={case['cutoff_dimension']} no threshold ambiguity", classified["ambiguous"] == [], classified["ambiguous"], [], "threshold")
        check(f"d={case['cutoff_dimension']} expected core", classified["core"] == case["expected_core"], classified["core"], case["expected_core"], "support")
        check(f"d={case['cutoff_dimension']} expected tail", classified["tail"] == case["expected_tail"], classified["tail"], case["expected_tail"], "support")
        check(f"d={case['cutoff_dimension']} partition", sorted(classified["core"] + classified["tail"]) == list(range(case["cutoff_dimension"])), sorted(classified["core"] + classified["tail"]), list(range(case["cutoff_dimension"])), "support")
        check(f"d={case['cutoff_dimension']} mass enclosure", Decimal(classified["row_mass_lower"]) <= 1 <= Decimal(classified["row_mass_upper"]), [classified["row_mass_lower"], classified["row_mass_upper"]], "interval contains one", "normalization")
        cases.append({"cutoff_dimension": case["cutoff_dimension"], "maximum_index": classified["maximum_index"], "core": classified["core"], "tail": classified["tail"], "ambiguous": classified["ambiguous"], "phi_intervals": classified["phi_intervals"], "tail_mass_lower": classified["tail_mass_lower"], "tail_mass_upper": classified["tail_mass_upper"], "row_mass_lower": classified["row_mass_lower"], "row_mass_upper": classified["row_mass_upper"], "parent_manifest": case["manifest"], "parent_run": case["primary_run"]})

    cardinalities = [len(case["core"]) for case in cases]
    expected_cardinalities = [len(case["expected_core"]) for case in manifest["cases"]]
    raw_sets = [set(case["core"]) for case in cases]
    nested = all(raw_sets[left] <= raw_sets[right] for left in range(len(raw_sets)) for right in range(left + 1, len(raw_sets)))
    monotone = all(cardinalities[index] <= cardinalities[index + 1] for index in range(len(cardinalities) - 1))
    check("adaptive support changes are recorded", cardinalities == expected_cardinalities, cardinalities, expected_cardinalities, "support")
    check("nonpromotion scope", all(value is False for key, value in manifest["scope"].items() if key.endswith("_closed")), manifest["scope"], "all promotion flags false", "scope")
    check("finite rule flags", manifest["scope"]["cutoff_adaptive_core_rule_defined"] is True and manifest["scope"]["directed_threshold_classification_certified"] is True and manifest["scope"]["all_coordinates_unambiguous"] is True, manifest["scope"], "finite adaptive rule certified", "scope")
    check("no silent nesting claim", manifest["scope"]["nested_core_certified"] is False and manifest["scope"]["core_cardinality_monotonicity_certified"] is False, [manifest["scope"]["nested_core_certified"], manifest["scope"]["core_cardinality_monotonicity_certified"]], [False, False], "scope")

    source_hashes: dict[str, str] = {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)}
    for case in manifest["cases"]:
        source_hashes[case["manifest"]] = sha256(REPO / case["manifest"])
        source_hashes[case["primary_run"]] = sha256(REPO / case["primary_run"])
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r439-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-439",
        "exploration_id": "EXP-001284",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": "INCREASING_CORE_RULE_AUDITED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"rule": rule, "selection_contract": selection, "cases": cases, "core_cardinalities": cardinalities, "raw_index_nested": nested, "core_cardinality_monotone": monotone, "cutoff_adaptive_core_rule_defined": True, "all_coordinates_unambiguous": True, "increasing_core_tail_modulus_closed": False},
        "source_hashes": source_hashes,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-439 PRIMARY INCREASING_CORE_RULE_AUDITED {len(checks)}/{len(checks)} cutoffs={len(cases)} core_cardinalities={cardinalities} nested={nested}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "INCREASING_CORE_RULE_AUDITED"
        assert payload["derived"]["all_coordinates_unambiguous"] is True
        assert payload["derived"]["increasing_core_tail_modulus_closed"] is False
        print("R-439 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
