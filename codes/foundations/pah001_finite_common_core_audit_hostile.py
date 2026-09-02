#!/usr/bin/env python3
"""Hostile mutation firewall for PAH-FCC-001."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "strategy/pa-hyp/finite-common-core-audit-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r478-pah001-common-core/hostile.json"
)


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    baseline_spec = load(SPEC_PATH)
    source_path = ROOT / baseline_spec["source"]["path"]
    baseline_source = load(source_path)
    baseline_source_object_digest = canonical_hash(baseline_source)

    expected_statuses = {
        "PAH-FCC-C1": "PASSED",
        "PAH-FCC-C2": "PASSED",
        "PAH-FCC-C3": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C4": "PARTIAL_NOT_CLOSED",
        "PAH-FCC-C5": "NOT_DEFINED",
    }

    def admissible(spec: dict[str, Any], source: dict[str, Any]) -> bool:
        conditions = spec.get("conditions")
        decision = spec.get("decision_rule")
        mutations = spec.get("model_mutation")
        nonclaims = spec.get("non_claims")
        if not isinstance(conditions, list) or not isinstance(decision, dict):
            return False
        if not isinstance(mutations, dict) or not isinstance(nonclaims, list):
            return False
        statuses = {item.get("id"): item.get("status") for item in conditions}
        return bool(
            canonical_hash(source) == baseline_source_object_digest
            and spec.get("schema") == "tect/pah001-finite-common-core-audit/1.0"
            and spec.get("audit_id") == "PAH-FCC-001"
            and spec.get("result_id") == "R-478"
            and spec.get("verdict") == "HOLD_FOR_EVIDENCE"
            and spec.get("classification") == "HOLD_FOR_EVIDENCE"
            and spec.get("claim_bearing") is False
            and spec.get("gate_changed") is False
            and spec.get("scientific_transition") is False
            and spec.get("negative_result_registered") is False
            and not any(mutations.values())
            and spec.get("source", {}).get("sha256")
            == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
            and source.get("packet_id") == "PAH-001"
            and source.get("version") == "0.1.0"
            and source.get("provenance", {}).get("physical_authority") is False
            and source.get("functional_or_action", {}).get("formula")
            == spec.get("exact_expressions", {}).get("functional")
            and source.get("dynamics", {}).get("generator")
            == spec.get("exact_expressions", {}).get("generator")
            and source.get("symmetry_and_constraint", {}).get(
                "candidate_internal_projection"
            )
            == spec.get("exact_expressions", {}).get("candidate_projection")
            and statuses == expected_statuses
            and decision.get("condition_vector")
            == [True, True, False, False, False]
            and decision.get("exact_counterexample_found") is False
            and decision.get("derived_verdict") == "HOLD_FOR_EVIDENCE"
            and "exact partial move maps" in spec.get("single_next_question", "")
            and "directed-root Hilbert measure"
            in spec.get("single_next_question", "")
            and "refinement embedding" in spec.get("single_next_question", "")
            and any("No physical Pre-A" in item for item in nonclaims)
            and any("No Q3LOCK" in item for item in nonclaims)
            and source.get("common_core_and_uniform_contract", {}).get(
                "continuum_uniform_estimate"
            )
            is False
            and source.get("ordered_limits", {}).get("interchange_claimed") is False
        )

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    check("baseline-admitted", admissible(baseline_spec, baseline_source))
    mutations: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    def mutate_spec(name: str, editor: Any) -> None:
        spec = copy.deepcopy(baseline_spec)
        editor(spec)
        mutations.append((name, spec, copy.deepcopy(baseline_source)))

    def mutate_source(name: str, editor: Any) -> None:
        source = copy.deepcopy(baseline_source)
        editor(source)
        mutations.append((name, copy.deepcopy(baseline_spec), source))

    mutate_spec("reject-source-hash-drift", lambda value: value["source"].update(sha256="0" * 64))
    mutate_spec("reject-mainline-promotion", lambda value: value.update(verdict="MAINLINE_ADVANCE"))
    mutate_spec("reject-negative-promotion", lambda value: value.update(verdict="NEGATIVE_RESULT", negative_result_registered=True))
    mutate_spec("reject-c3-promotion", lambda value: value["conditions"][2].update(status="PASSED"))
    mutate_spec("reject-c4-promotion", lambda value: value["conditions"][3].update(status="PASSED"))
    mutate_spec("reject-c5-promotion", lambda value: value["conditions"][4].update(status="PASSED"))
    mutate_spec("reject-vector-promotion", lambda value: value["decision_rule"].update(condition_vector=[True] * 5))
    mutate_spec("reject-false-counterexample", lambda value: value["decision_rule"].update(exact_counterexample_found=True))
    mutate_spec("reject-new-functional", lambda value: value["model_mutation"].update(functional_modified=True))
    mutate_spec("reject-new-move-set", lambda value: value["model_mutation"].update(move_set_modified=True))
    mutate_spec("reject-new-nu", lambda value: value["model_mutation"].update(mobility_exponent_modified=True))
    mutate_spec("reject-new-projection", lambda value: value["model_mutation"].update(projection_modified=True))
    mutate_spec("reject-limit-reorder", lambda value: value["model_mutation"].update(limit_order_modified=True))
    mutate_spec("reject-new-candidate", lambda value: value["model_mutation"].update(new_candidate_added=True))
    mutate_spec("reject-q3lock-import", lambda value: value["model_mutation"].update(q3lock_evidence_imported=True))
    mutate_spec("reject-physical-claim", lambda value: value.update(non_claims=["Physical Pre-A and gravity now follow."]))
    mutate_spec("reject-missing-root-question", lambda value: value.update(single_next_question="Supply a refinement embedding only."))
    mutate_spec("reject-claim-bearing", lambda value: value.update(claim_bearing=True))
    mutate_spec("reject-gate-change", lambda value: value.update(gate_changed=True))
    mutate_spec("reject-scientific-transition", lambda value: value.update(scientific_transition=True))

    mutate_source("reject-functional-edit", lambda value: value["functional_or_action"].update(formula=value["functional_or_action"]["formula"] + "+delta"))
    mutate_source("reject-generator-edit", lambda value: value["dynamics"].update(generator="modified generator"))
    mutate_source("reject-move-edit", lambda value: value["dynamics"]["move_set"].append("new move"))
    mutate_source("reject-mobility-edit", lambda value: value["dynamics"]["mobility_rule"].update(matter_phase="s_v^(nu+1)"))
    mutate_source("reject-projection-edit", lambda value: value["symmetry_and_constraint"].update(candidate_internal_projection="modified projection"))
    mutate_source("reject-refinement-invention", lambda value: value.update(refinement_embeddings={"invented": True}))
    mutate_source("reject-limit-order-edit", lambda value: value["ordered_limits"]["order"].reverse())
    mutate_source("reject-time-promotion", lambda value: value["dynamics"].update(time="Lorentzian proper time"))
    mutate_source("reject-physical-authority", lambda value: value["provenance"].update(physical_authority=True))
    mutate_source("reject-continuum-promotion", lambda value: value["common_core_and_uniform_contract"].update(continuum_uniform_estimate=True))

    for name, candidate_spec, candidate_source in mutations:
        check(name, not admissible(candidate_spec, candidate_source))

    failed = [item for item in checks if not item["passed"]]
    result = {
        "schema": "tect/pah001-finite-common-core-hostile-run/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-FCC-001",
        "result_id": "R-478",
        "exploration_id": "EXP-001359",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(item["passed"] for item in checks[1:]),
        "checks": checks,
        "source_object_digest": baseline_source_object_digest,
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
    }
    atomic_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "PAH-FCC-001 HOSTILE "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"mutations={result['mutations_rejected']}/{result['mutations_attempted']}; "
        f"verdict={result['verdict']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
