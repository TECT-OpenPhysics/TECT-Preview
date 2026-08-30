#!/usr/bin/env python3
"""Adversarial firewall for the R-448 static-dynamic quotient contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pre-a-static-dynamic-equivalence-quotient-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-static_dynamic_equivalence_quotient/hostile.json"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def accepts(candidate: dict, baseline: dict) -> bool:
    finite = candidate.get("finite_contract", {})
    base_finite = baseline["finite_contract"]
    quotient = candidate.get("quotient_contract", {})
    scope = candidate.get("scope", {})
    base_scope = baseline["scope"]
    return (
        candidate.get("claim_bearing") is False
        and candidate.get("tier") == "T0"
        and finite.get("static_signature") == base_finite["static_signature"]
        and finite.get("maps") == base_finite["maps"]
        and finite.get("probe") == base_finite["probe"]
        and quotient.get("relation") == baseline["quotient_contract"]["relation"]
        and quotient.get("selection") == "NO_SELECTION_FROM_STATIC_DATA"
        and scope.get("static_identifiability") == "NON_IDENTIFIABLE"
        and scope.get("stability_under_observation_error") == "NOT_ASSESSED"
        and scope.get("stability_under_regulator_change") == "NOT_ASSESSED"
        and scope.get("holdout_prediction") == "NOT_ASSESSED"
        and scope.get("source_owner_admitted") is False
        and scope.get("physical_identity") is False
        and base_scope.get("no_tier_change") is True
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    baseline = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if not accepts(baseline, baseline):
        raise AssertionError("baseline contract rejected")
    mutations = []

    def reject(name: str, mutation: dict, candidate: dict) -> None:
        accepted = accepts(candidate, baseline)
        if accepted:
            raise AssertionError(f"hostile mutation accepted: {name}")
        mutations.append({"name": name, "status": "REJECTED", "mutation": mutation, "accepted": accepted})

    candidate = copy.deepcopy(baseline); candidate["quotient_contract"]["relation"] = "d1 ~ d2 iff full_dynamics_equal"; reject("full-dynamics relation", {"relation": "full_dynamics_equal"}, candidate)
    candidate = copy.deepcopy(baseline); candidate["finite_contract"]["probe"]["coordinates"] = ["0", "0"]; reject("non-separating probe", {"coordinates": ["0", "0"]}, candidate)
    candidate = copy.deepcopy(baseline); candidate["finite_contract"]["maps"]["B"]["factors"] = list(candidate["finite_contract"]["maps"]["A"]["factors"]); reject("equal representatives", {"B_factors": candidate["finite_contract"]["maps"]["B"]["factors"]}, candidate)
    candidate = copy.deepcopy(baseline); candidate["finite_contract"]["static_signature"]["covariance"][1] = "1"; reject("broken static inverse", {"covariance": candidate["finite_contract"]["static_signature"]["covariance"]}, candidate)
    candidate = copy.deepcopy(baseline); candidate["quotient_contract"]["selection"] = "UNIQUE_SELECTION"; reject("uniqueness promotion", {"selection": "UNIQUE_SELECTION"}, candidate)
    candidate = copy.deepcopy(baseline); candidate["scope"]["stability_under_observation_error"] = "PASS"; reject("stability promotion", {"stability_under_observation_error": "PASS"}, candidate)
    candidate = copy.deepcopy(baseline); candidate["claim_bearing"] = True; reject("claim-bearing promotion", {"claim_bearing": True}, candidate)
    candidate = copy.deepcopy(baseline); candidate["scope"]["source_owner_admitted"] = True; reject("unowned production admission", {"source_owner_admitted": True}, candidate)
    payload = {
        "schema": "tect/pre-a-static-dynamic-equivalence-quotient-hostile/1.0",
        "manifest": CONTRACT.relative_to(ROOT).as_posix(),
        "result_id": baseline["result_id"],
        "exploration_id": baseline["exploration_id"],
        "task_id": baseline["task_id"],
        "claim_id": baseline["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "passed": len(mutations),
        "assertion_count": len(mutations),
        "assertions": mutations,
        "mutations_rejected": len(mutations),
        "scope": {"claim_bearing": False, "static_selection_rejected": True, "physical_owner_promotion_rejected": True},
        "source_hashes": {"script": digest(Path(__file__)), "manifest": digest(CONTRACT)},
        "evidence_level": "T0 / EXECUTED ADVERSARIAL QUOTIENT FIREWALL",
        "non_claims": baseline["non_claims"],
        "boundary": baseline["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-448 HOSTILE {payload['verdict']} {len(mutations)}/{len(mutations)}", flush=True)
    if args.self_test:
        assert payload["mutations_rejected"] == 8
        print("R-448 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
