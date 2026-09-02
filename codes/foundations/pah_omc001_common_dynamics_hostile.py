#!/usr/bin/env python3
"""Hostile mutation firewall for the PAH-OMC-001 admission boundary."""

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


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "strategy/pa-hyp/owner-morphism-audit-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r479-pah-omc001/hostile.json"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    baseline_audit = load(AUDIT_PATH)
    parent_path = ROOT / baseline_audit["parent"]["path"]
    contract_path = ROOT / baseline_audit["contract"]["path"]
    baseline_parent = load(parent_path)
    baseline_contract = load(contract_path)
    parent_digest = canonical_hash(baseline_parent)
    contract_digest = canonical_hash(baseline_contract)

    expected_statuses = {
        "PAH-OMC-C1": "PASSED",
        "PAH-OMC-C2": "PASSED",
        "PAH-OMC-C3": "PASSED",
        "PAH-OMC-C4": "PASSED",
        "PAH-OMC-C5": "PASSED_BOUNDARY",
    }

    def admissible(
        audit: dict[str, Any], parent: dict[str, Any], contract: dict[str, Any]
    ) -> bool:
        statuses = {
            item.get("id"): item.get("status")
            for item in audit.get("conditions", [])
            if isinstance(item, dict)
        }
        roots = contract.get("universal_directed_root_labels", {})
        conventions = contract.get("invalid_and_duplicate_conventions", {})
        symmetry = contract.get("symmetry_action_on_states_and_roots", {})
        root_space = contract.get("directed_root_hilbert_space", {})
        refinement = contract.get("refinement_contract", {})
        tested = refinement.get("tested_nontrivial_candidate", {})
        firewall = contract.get("preservation_firewall", {})
        return bool(
            canonical_hash(parent) == parent_digest
            and canonical_hash(contract) == contract_digest
            and audit.get("schema") == "tect/pah-owner-morphism-audit/1.0"
            and audit.get("audit_id") == "PAH-OMC-AUDIT-001"
            and audit.get("result_id") == "R-479"
            and audit.get("exploration_id") == "EXP-001361"
            and audit.get("parent", {}).get("sha256")
            == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
            and audit.get("contract", {}).get("sha256")
            == "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
            and audit.get("claim_bearing") is False
            and audit.get("active_gate_changed") is False
            and audit.get("finite_common_dynamics_verdict") == "MAINLINE_ADVANCE"
            and audit.get("uniform_refinement_verdict") == "HOLD_FOR_EVIDENCE"
            and audit.get("overall_programme_state") == "HOLD_FOR_EVIDENCE_AT_STAGE_2"
            and statuses == expected_statuses
            and parent.get("packet_id") == "PAH-001"
            and contract.get("contract_id") == "PAH-OMC-001"
            and contract.get("provenance", {}).get("physical_authority") is False
            and "not retroactive" in contract.get("parent", {}).get("composition_rule", "")
            and all(
                firewall.get(key) is True
                for key in (
                    "functional_unchanged",
                    "gauge_group_unchanged",
                    "move_families_unchanged",
                    "mobility_exponent_nu_unchanged",
                    "candidate_projection_unchanged",
                    "regulator_unchanged",
                    "limit_order_unchanged",
                    "no_new_hamiltonian_or_counterterm",
                    "no_q3lock_import",
                )
            )
            and set(roots) == {"phase", "matter_transfer", "link", "aperture"}
            and all("inverse" in roots[name] for name in roots)
            and "absent from D_rho" in conventions.get("invalid_partial_move", "")
            and "two distinct channels" in conventions.get("K_equals_2", "")
            and "exactly once" in conventions.get("channel_counting", "")
            and "commutes with the gauge action" in symmetry.get("gauge_on_roots", "")
            and "orientation_sign" in symmetry.get("automorphism_on_roots", "")
            and symmetry.get("rate_equivariance", "").startswith("c_(h.r)(h.x)=c_r(x)")
            and root_space.get("space") == "K_rho=C^(D_rho)."
            and "pi_(rho,Q)(x)" in root_space.get("inner_product", "")
            and "exact retained directed labels" in root_space.get("multiplicity", "")
            and root_space.get("domain_B") == "dom(B_rho)=C^(Omega_(rho,Q)); all functions are bounded because Omega is finite."
            and "sqrt(c_r(x)/2)" in root_space.get("definition_B", "")
            and root_space.get("domain_adjoint") == "dom(B_rho^*)=K_rho; B_rho^* is the unique finite-dimensional Hilbert adjoint under the displayed state and root inner products."
            and root_space.get("factorization_target", "").endswith("on C^(Omega) and on A_rho^inv.")
            and refinement.get("anchor_preserving_isomorphism_sanity_morphism", {}).get("boundary", "").startswith("This is relabelling naturality only")
            and tested.get("id") == "PAH-FREE-VERTEX-RESTRICTION"
            and tested.get("verdict") == "EXACT_INTERTWINING_FAILS_FOR_THIS_NATURAL_REFINEMENT"
            and "-kappa_s delta(z_1-z_2)!=0" in tested.get("obstruction", "")
            and refinement.get("status") == "HOLD_FOR_EVIDENCE"
            and audit.get("refinement_failure_boundary", {}).get("non_global") is True
            and "nontrivial anchor-preserving subdivision" in audit.get("single_next_question", "")
            and any("No physical Pre-A" in item for item in audit.get("non_claims", []))
            and any("quantum real time" in item for item in audit.get("non_claims", []))
            and any("No Q3LOCK" in item for item in audit.get("non_claims", []))
        )

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    check("baseline-admitted", admissible(baseline_audit, baseline_parent, baseline_contract))
    mutations: list[tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]] = []

    def mutate_audit(name: str, editor: Callable[[dict[str, Any]], None]) -> None:
        candidate = copy.deepcopy(baseline_audit)
        editor(candidate)
        mutations.append((name, candidate, copy.deepcopy(baseline_parent), copy.deepcopy(baseline_contract)))

    def mutate_parent(name: str, editor: Callable[[dict[str, Any]], None]) -> None:
        candidate = copy.deepcopy(baseline_parent)
        editor(candidate)
        mutations.append((name, copy.deepcopy(baseline_audit), candidate, copy.deepcopy(baseline_contract)))

    def mutate_contract(name: str, editor: Callable[[dict[str, Any]], None]) -> None:
        candidate = copy.deepcopy(baseline_contract)
        editor(candidate)
        mutations.append((name, copy.deepcopy(baseline_audit), copy.deepcopy(baseline_parent), candidate))

    mutate_audit("reject-parent-hash-drift", lambda value: value["parent"].update(sha256="0" * 64))
    mutate_audit("reject-contract-hash-drift", lambda value: value["contract"].update(sha256="0" * 64))
    mutate_audit("reject-stage1-hold", lambda value: value.update(finite_common_dynamics_verdict="HOLD_FOR_EVIDENCE"))
    mutate_audit("reject-stage1-negative", lambda value: value.update(finite_common_dynamics_verdict="NEGATIVE_RESULT"))
    mutate_audit("reject-uniform-promotion", lambda value: value.update(uniform_refinement_verdict="MAINLINE_ADVANCE"))
    mutate_audit("reject-physical-programme-promotion", lambda value: value.update(overall_programme_state="PHYSICAL_PRE_A"))
    mutate_audit("reject-c3-demotion", lambda value: value["conditions"][2].update(status="PARTIAL_NOT_CLOSED"))
    mutate_audit("reject-c4-demotion", lambda value: value["conditions"][3].update(status="PARTIAL_NOT_CLOSED"))
    mutate_audit("reject-c5-overpromotion", lambda value: value["conditions"][4].update(status="PASSED"))
    mutate_audit("reject-claim-bearing", lambda value: value.update(claim_bearing=True))
    mutate_audit("reject-gate-change", lambda value: value.update(active_gate_changed=True))
    mutate_audit("reject-global-no-go", lambda value: value["refinement_failure_boundary"].update(non_global=False))
    mutate_audit("reject-missing-next-contract", lambda value: value.update(single_next_question="Run a continuum calculation."))
    mutate_audit("reject-physical-nonclaim-loss", lambda value: value.update(non_claims=["Physical Pre-A follows."]))

    mutate_parent("reject-parent-functional-edit", lambda value: value["functional_or_action"].update(formula="edited"))
    mutate_parent("reject-parent-move-edit", lambda value: value["dynamics"]["move_set"].append("new carrier move"))

    mutate_contract("reject-physical-authority", lambda value: value["provenance"].update(physical_authority=True))
    mutate_contract("reject-retroactive-attribution", lambda value: value["parent"].update(composition_rule="PAH-001 always contained this theorem."))
    mutate_contract("reject-functional-change", lambda value: value["preservation_firewall"].update(functional_unchanged=False))
    mutate_contract("reject-new-hamiltonian", lambda value: value["preservation_firewall"].update(no_new_hamiltonian_or_counterterm=False))
    mutate_contract("reject-limit-reorder", lambda value: value["preservation_firewall"].update(limit_order_unchanged=False))
    mutate_contract("reject-q3lock-import", lambda value: value["preservation_firewall"].update(no_q3lock_import=False))
    mutate_contract("reject-missing-phase-family", lambda value: value["universal_directed_root_labels"].pop("phase"))
    mutate_contract("reject-phase-inverse-edit", lambda value: value["universal_directed_root_labels"]["phase"].update(inverse="identity"))
    mutate_contract("reject-invalid-reflection", lambda value: value["invalid_and_duplicate_conventions"].update(invalid_partial_move="Reflect at the boundary."))
    mutate_contract("reject-K2-merge", lambda value: value["invalid_and_duplicate_conventions"].update(K_equals_2="Merge the channels."))
    mutate_contract("reject-channel-double-count", lambda value: value["invalid_and_duplicate_conventions"].update(channel_counting="Count roots twice."))
    mutate_contract("reject-gauge-root-drift", lambda value: value["symmetry_action_on_states_and_roots"].update(gauge_on_roots="Gauge changes root type."))
    mutate_contract("reject-orientation-sign-loss", lambda value: value["symmetry_action_on_states_and_roots"].update(automorphism_on_roots="Relabel without orientation."))
    mutate_contract("reject-rate-equivariance-loss", lambda value: value["symmetry_action_on_states_and_roots"].update(rate_equivariance="not equivariant"))
    mutate_contract("reject-root-space-change", lambda value: value["directed_root_hilbert_space"].update(space="unweighted roots"))
    mutate_contract("reject-root-measure-change", lambda value: value["directed_root_hilbert_space"].update(inner_product="counting only"))
    mutate_contract("reject-root-multiplicity-merge", lambda value: value["directed_root_hilbert_space"].update(multiplicity="merge duplicates"))
    mutate_contract("reject-B-domain-restriction", lambda value: value["directed_root_hilbert_space"].update(domain_B="dense guess"))
    mutate_contract("reject-half-factor-loss", lambda value: value["directed_root_hilbert_space"].update(definition_B="sqrt(c_r(x))[f(rx)-f(x)]"))
    mutate_contract("reject-adjoint-domain-loss", lambda value: value["directed_root_hilbert_space"].update(domain_adjoint="unspecified"))
    mutate_contract("reject-factorization-sign", lambda value: value["directed_root_hilbert_space"].update(factorization_target="B^*B=L"))
    mutate_contract("reject-isomorphism-as-refinement", lambda value: value["refinement_contract"]["anchor_preserving_isomorphism_sanity_morphism"].update(boundary="This closes lattice refinement."))
    mutate_contract("reject-free-vertex-promotion", lambda value: value["refinement_contract"]["tested_nontrivial_candidate"].update(verdict="EXACT_INTERTWINING_PASSES"))
    mutate_contract("reject-obstruction-sign", lambda value: value["refinement_contract"]["tested_nontrivial_candidate"].update(obstruction="+kappa_s delta(z_1-z_2)=0"))
    mutate_contract("reject-refinement-hold-loss", lambda value: value["refinement_contract"].update(status="MAINLINE_ADVANCE"))

    for name, audit, parent, contract in mutations:
        check(name, not admissible(audit, parent, contract))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc001-hostile-run/1.0",
        "run_kind": "hostile",
        "audit_id": baseline_audit["audit_id"],
        "result_id": baseline_audit["result_id"],
        "exploration_id": baseline_audit["exploration_id"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "finite_common_dynamics_verdict": baseline_audit["finite_common_dynamics_verdict"],
        "uniform_refinement_verdict": baseline_audit["uniform_refinement_verdict"],
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(item["passed"] for item in checks[1:]),
        "checks": checks,
        "parent_object_digest": parent_digest,
        "contract_object_digest": contract_digest,
        "claim_bearing": False,
        "active_gate_changed": False,
        "physical_progress": False,
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "PAH-OMC-AUDIT-001 HOSTILE "
        f"{result['verification']} {result['passed']}/{result['assertion_count']}; "
        f"mutations={result['mutations_rejected']}/{result['mutations_attempted']}; "
        f"finite={result['finite_common_dynamics_verdict']}; "
        f"refinement={result['uniform_refinement_verdict']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
