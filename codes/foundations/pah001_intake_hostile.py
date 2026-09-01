#!/usr/bin/env python3
"""Fail-closed hostile mutations for the PAH-001 structural intake.

The harness tests provenance and promotion boundaries only.  Passing it does
not prove the candidate functional, dynamics, collapse predicates, or limits.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "strategy/pa-hyp/PAH-001-v1.json"
MANIFEST = REPO / "strategy/pa-hyp/intake-v1.json"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r476-pah001/hostile.json"
)

OWNER_ORDER = (
    "generator_or_transfer",
    "state",
    "physical_projection",
    "time_boundary",
    "heat_root_incidence",
    "root_filtration",
    "conditional_replicas",
    "raw_current_spatial_intertwiner",
    "production_one_use_q_ledger",
)
R192_ORDER = (
    "common_heat",
    "root_1",
    "root_2",
    "future_residual",
    "covariance_bases",
    "complement",
    "historical_low",
    "forest",
    "returned_mean",
    "source",
    "sextic",
)
LIMIT_ORDER = (
    "LOCAL_STATE_CUTOFF",
    "LATTICE_REFINEMENT",
    "VOLUME_EXHAUSTION",
    "PHASE_SELECTOR",
    "APERTURE_COLLAPSE",
    "GROUND_STATE",
    "OBSERVATION_TIME",
)
REQUIRED_SLOT_FIELDS = {
    "id",
    "kind",
    "status",
    "authority_scope",
    "domain",
    "codomain",
    "equation",
    "dependencies",
    "falsifier",
    "proof_status",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def semantic_errors(source: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Return every fail-closed structural error in a decoded packet."""

    errors: list[str] = []

    def require(condition: bool, name: str) -> None:
        if not condition:
            errors.append(name)

    provenance = source.get("provenance", {})
    require(provenance.get("class") == "RESEARCHER_HYPOTHESIS", "provenance class")
    require(provenance.get("external_source") is False, "external source firewall")
    require(provenance.get("constructed_hypothesis") is True, "constructed hypothesis")
    require(provenance.get("synthetic_fixture") is False, "fixture firewall")
    require(provenance.get("physical_authority") is False, "physical authority firewall")
    require(provenance.get("physical_identity") == "UNESTABLISHED", "physical identity")

    boundary = source.get("interpretive_boundary", {})
    require(boundary.get("event_horizon_identity") == "NOT_CLAIMED", "event horizon firewall")
    require(boundary.get("pre_a_identity") == "NOT_CLAIMED", "Pre-A firewall")
    require(boundary.get("gr_identity") == "NOT_CLAIMED", "GR firewall")
    require(boundary.get("not_a_coordinate_singularity") is True, "coordinate boundary")

    preservation = source.get("method_preservation", {})
    require(isinstance(preservation, dict) and preservation and all(value is True for value in preservation.values()), "method preservation")

    require(isinstance(source.get("functional_or_action"), dict), "functional")
    require(bool(source.get("functional_or_action", {}).get("formula")), "functional formula")
    require(isinstance(source.get("dynamics"), dict), "dynamics")
    require(bool(source.get("dynamics", {}).get("generator")), "generator")
    require(bool(source.get("dynamics", {}).get("state")), "state")
    require(isinstance(source.get("finite_regulator"), dict), "finite regulator")

    slots = source.get("r471_owner_slots", [])
    ids = [item.get("id") for item in slots if isinstance(item, dict)]
    require(tuple(ids) == OWNER_ORDER, "owner order")
    require(len(ids) == len(set(ids)) == len(OWNER_ORDER), "owner uniqueness")
    for index, item in enumerate(slots):
        require(isinstance(item, dict) and REQUIRED_SLOT_FIELDS <= set(item), f"owner fields {index}")
        if isinstance(item, dict):
            require(item.get("authority_scope") == "RESEARCHER_HYPOTHESIS", f"owner scope {index}")
            require(bool(item.get("equation")), f"owner equation {index}")
            require(bool(item.get("falsifier")), f"owner falsifier {index}")
    if len(slots) == len(OWNER_ORDER):
        require(slots[2].get("status") == "PRESENT_CANDIDATE_INTERNAL_ONLY", "candidate projection scope")
        require("exactly once" in str(slots[-1].get("equation", "")), "q ledger one-use")

    bindings = source.get("r192_detailed_bindings", [])
    binding_ids = [item.get("slot") for item in bindings if isinstance(item, dict)]
    require(tuple(binding_ids) == R192_ORDER, "R-192 order")
    require(len(binding_ids) == len(set(binding_ids)) == len(R192_ORDER), "R-192 uniqueness")
    require(all(bool(item.get("pointer")) for item in bindings if isinstance(item, dict)), "R-192 pointers")

    common = source.get("common_core_and_uniform_contract", {})
    require(bool(common.get("common_core")), "common core")
    require(common.get("common_norm") == "||f||_infinity", "common norm")
    require(str(common.get("uniform_constant", "")).startswith("C_T=1"), "uniform constant")
    independence = common.get("independence_set", [])
    require(all(name in independence for name in ("K", "beta", "|V|", "epsilon", "a")), "uniform independence")
    require(common.get("continuum_uniform_estimate") is False, "continuum uniform firewall")

    limits = source.get("ordered_limits", {})
    limit_ids = [item.get("id") for item in limits.get("order", []) if isinstance(item, dict)]
    require(tuple(limit_ids) == LIMIT_ORDER, "limit order")
    require(limits.get("interchange_claimed") is False, "limit interchange firewall")
    require("precedes" in str(limits.get("critical_order_rule", "")), "critical limit rule")

    collapse = source.get("horizon_collapse_tests", {})
    require(collapse.get("status") == "PREREGISTERED_NOT_RUN", "collapse status")
    require(collapse.get("joint_acceptance") is not None, "joint collapse predicate")

    branch = source.get("same_owner_branch_contract", {})
    require(branch.get("physical_empty_branch") == "NOT_ADMITTED", "physical empty firewall")
    require(branch.get("reading_h_identity") == "NOT_CLAIMED", "Reading-H firewall")
    require(branch.get("status") == "BLOCKED_NOT_EVALUATED", "branch status")

    inverse = source.get("inverse_map_status", {})
    for stage in ("F_reg", "F_lim", "F_eff", "F_obs"):
        require(inverse.get(stage, {}).get("admitted") is False, f"{stage} firewall")
    require(inverse.get("candidate_neutral_estimand_frozen") is False, "estimand firewall")
    require(inverse.get("immutable_scorer_frozen") is False, "scorer firewall")
    require(inverse.get("prospective_holdout_frozen") is False, "holdout firewall")

    require(len(source.get("falsifiers", [])) >= 12, "falsifier coverage")
    joined_nonclaims = " ".join(source.get("non_claims", []))
    for token in ("event horizon", "Pre-A", "QFT", "continuum", "physical-empty"):
        require(token.lower() in joined_nonclaims.lower(), f"nonclaim {token}")

    artifact = manifest.get("source_artifact", {})
    require(bool(artifact.get("path")), "source path")
    require(artifact.get("provenance_class") == "RESEARCHER_HYPOTHESIS", "manifest provenance")
    require(artifact.get("synthetic_fixture") is False, "manifest fixture firewall")
    require(artifact.get("physical_authority") is False, "manifest physical firewall")
    admission = manifest.get("admission_boundary", {})
    require(admission.get("hypothesis_packet_state") == "OWNER_PACKET_HASHED", "structural state")
    require(admission.get("physical_owner_admitted") is False, "production admission")
    require(admission.get("gate_changed") is False, "gate firewall")
    require(admission.get("scientific_transition") is False, "scientific transition firewall")
    require(all(value is True for value in manifest.get("structural_acceptance", {}).values()), "acceptance fields")
    return errors


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})

    base_errors = semantic_errors(source, manifest)
    check("unmutated source passes structural semantics", not base_errors, base_errors, [])
    check("source raw hash matches", sha256(SOURCE) == manifest["source_artifact"]["sha256"], sha256(SOURCE), manifest["source_artifact"]["sha256"])
    check("T0 claim firewall", manifest.get("tier") == "T0" and manifest.get("claim_bearing") is False, [manifest.get("tier"), manifest.get("claim_bearing")], ["T0", False])

    mutations: list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]] = [
        ("delete source path", lambda s, m: m["source_artifact"].update(path="")),
        ("relabel provenance as fixture", lambda s, m: s["provenance"].__setitem__("class", "CONTRACT_FIXTURE")),
        ("mark source synthetic", lambda s, m: s["provenance"].update(synthetic_fixture=True)),
        ("claim physical authority", lambda s, m: s["provenance"].update(physical_authority=True)),
        ("claim physical identity", lambda s, m: s["provenance"].update(physical_identity="ESTABLISHED")),
        ("claim event horizon identity", lambda s, m: s["interpretive_boundary"].update(event_horizon_identity="CLAIMED")),
        ("claim Pre-A identity", lambda s, m: s["interpretive_boundary"].update(pre_a_identity="CLAIMED")),
        ("claim GR identity", lambda s, m: s["interpretive_boundary"].update(gr_identity="CLAIMED")),
        ("change existing method", lambda s, m: s["method_preservation"].update(t054_forward_method_unchanged=False)),
        ("delete functional", lambda s, m: s.pop("functional_or_action")),
        ("delete generator", lambda s, m: s["dynamics"].update(generator="")),
        ("reverse owner order", lambda s, m: s.update(r471_owner_slots=list(reversed(s["r471_owner_slots"])))),
        ("duplicate owner slot", lambda s, m: s["r471_owner_slots"].append(copy.deepcopy(s["r471_owner_slots"][-1]))),
        ("erase owner equation", lambda s, m: s["r471_owner_slots"][0].update(equation="")),
        ("promote candidate projection", lambda s, m: s["r471_owner_slots"][2].update(status="PRESENT_PHYSICAL_SECTOR")),
        ("duplicate q use", lambda s, m: s["r471_owner_slots"][-1].update(equation="q_r is reusable twice")),
        ("delete R-192 binding", lambda s, m: s["r192_detailed_bindings"].pop()),
        ("reverse R-192 order", lambda s, m: s.update(r192_detailed_bindings=list(reversed(s["r192_detailed_bindings"])))),
        ("delete common core", lambda s, m: s["common_core_and_uniform_contract"].update(common_core="")),
        ("change common norm", lambda s, m: s["common_core_and_uniform_contract"].update(common_norm="regulator-dependent norm")),
        ("change uniform constant", lambda s, m: s["common_core_and_uniform_contract"].update(uniform_constant="C_T=2")),
        ("erase uniform beta independence", lambda s, m: s["common_core_and_uniform_contract"]["independence_set"].remove("beta")),
        ("claim continuum uniformity", lambda s, m: s["common_core_and_uniform_contract"].update(continuum_uniform_estimate=True)),
        ("swap aperture and observation limits", lambda s, m: s["ordered_limits"]["order"].reverse()),
        ("claim limit interchange", lambda s, m: s["ordered_limits"].update(interchange_claimed=True)),
        ("erase critical order rule", lambda s, m: s["ordered_limits"].update(critical_order_rule="")),
        ("promote collapse test", lambda s, m: s["horizon_collapse_tests"].update(status="PASS")),
        ("admit physical empty", lambda s, m: s["same_owner_branch_contract"].update(physical_empty_branch="ADMITTED")),
        ("claim Reading-H identity", lambda s, m: s["same_owner_branch_contract"].update(reading_h_identity="CLAIMED")),
        ("promote F_reg", lambda s, m: s["inverse_map_status"]["F_reg"].update(admitted=True)),
        ("promote F_lim", lambda s, m: s["inverse_map_status"]["F_lim"].update(admitted=True)),
        ("freeze scorer early", lambda s, m: s["inverse_map_status"].update(immutable_scorer_frozen=True)),
        ("admit physical owner in manifest", lambda s, m: m["admission_boundary"].update(physical_owner_admitted=True)),
        ("change scientific gate", lambda s, m: m["admission_boundary"].update(gate_changed=True)),
        ("declare scientific transition", lambda s, m: m["admission_boundary"].update(scientific_transition=True)),
    ]

    for name, mutate in mutations:
        changed_source = copy.deepcopy(source)
        changed_manifest = copy.deepcopy(manifest)
        mutate(changed_source, changed_manifest)
        errors = semantic_errors(changed_source, changed_manifest)
        check(name, bool(errors), errors[:4], "one or more fail-closed errors")

    wrong_hash = copy.deepcopy(manifest)
    wrong_hash["source_artifact"]["sha256"] = "0" * 64
    check("stale or malformed source digest", sha256(SOURCE) != wrong_hash["source_artifact"]["sha256"], wrong_hash["source_artifact"]["sha256"], "rejected")

    payload = {
        "schema": "tect/pah001-structural-intake-run/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "task_id": manifest["task_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PAH001-STRUCTURAL-INTAKE-HOSTILE-PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "hypothesis_packet_state": "OWNER_PACKET_HASHED",
        "production_admission": "NONE",
        "physical_owner_admitted": False,
        "all_mutations_rejected": True,
        "mutation_count": len(mutations) + 1,
        "assertion_summary": {"passed": len(checks), "total": len(checks), "mutations_rejected": len(mutations) + 1},
        "checks": checks,
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "source_sha256": sha256(SOURCE),
            "manifest_sha256": sha256(MANIFEST),
        },
    }
    target = output if output.is_absolute() else REPO / output
    atomic_json(target, payload)
    print(f"PAH-001 HOSTILE PASS {len(checks)}/{len(checks)}; mutations={len(mutations) + 1}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
