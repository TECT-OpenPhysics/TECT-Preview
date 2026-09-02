#!/usr/bin/env python3
"""Primary structural audit for the PAH-OMC-002 successor morphism contract.

This audit checks only that the separately versioned conditional-kernel
contract is complete, hash-pinned, and explicitly held for evidence.  It does
not evaluate a generator, choose a physical sector, or claim an intertwining
theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-contract/primary.json"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_parent = manifest["parent"]["sha256"]
    expected_finite = manifest["finite_completion"]["sha256"]
    expected_contract = manifest["contract"]["sha256"]
    actual_parent = digest(PARENT)
    actual_finite = digest(FINITE)
    actual_contract = digest(CONTRACT)

    check("manifest-schema", manifest.get("schema") == "tect/pre-a-owner-morphism-manifest/1.0")
    check("contract-hash", actual_contract == expected_contract, actual_contract)
    check("parent-hash", actual_parent == expected_parent, actual_parent)
    check("finite-completion-hash", actual_finite == expected_finite, actual_finite)
    check("contract-identity", contract.get("contract_id") == "PAH-OMC-002")
    check(
        "successor-provenance",
        contract.get("provenance", {}).get("class")
        == "RESEARCHER_HYPOTHESIS_SUCCESSOR_CONTRACT"
        and contract.get("provenance", {}).get("physical_authority") is False,
    )
    check(
        "parent-composition-firewall",
        contract.get("parent", {}).get("sha256") == expected_parent
        and contract.get("parent", {}).get("finite_completion_contract", {}).get("sha256")
        == expected_finite
        and "not retroactive" in contract.get("parent", {}).get("composition_rule", ""),
    )

    firewall = contract.get("preservation_firewall", {})
    firewall_keys = (
        "functional_unchanged",
        "gauge_group_unchanged",
        "move_families_unchanged",
        "mobility_exponent_nu_unchanged",
        "candidate_projection_unchanged",
        "regulator_rule_unchanged",
        "limit_order_unchanged",
        "no_new_hamiltonian_or_counterterm",
        "no_q3lock_import",
        "no_physical_identification",
    )
    check("preservation-firewall", all(firewall.get(key) is True for key in firewall_keys), firewall)

    status = contract.get("status", {})
    check(
        "held-status",
        status.get("contract") == "CANDIDATE_NOT_ADMITTED"
        and status.get("strong_generator_intertwining") == "ROUTE_LOCAL_FAIL_FOR_NATURAL_PULLBACK"
        and status.get("conditional_projected_intertwining") == "PENDING_EXACT_AUDIT"
        and status.get("uniform_limit") == "NOT_ADMITTED",
        status,
    )

    scope = contract.get("exact_scope", {})
    check(
        "finite-relational-scope",
        "relational two-cell complex" in scope.get("coarse_carrier", "")
        and "No embedding coordinates" in scope.get("fine_carrier", "")
        and scope.get("time") == "External stochastic Markov time only."
        and scope.get("limits", "").startswith("No cutoff"),
        scope,
    )

    transport = contract.get("parameter_transport", {})
    required_transport = {
        "K",
        "Q",
        "M_s",
        "M_psi",
        "R_max",
        "epsilon",
        "a",
        "beta",
        "nu",
        "theta",
        "cell_couplings",
        "weights",
    }
    check("parameter-transport-complete", required_transport <= set(transport), sorted(transport))
    check(
        "no-parameter-fitting",
        "no fitted" in transport.get("beta", "").lower()
        and "without counterterm" in transport.get("cell_couplings", "").lower(),
    )

    mapping = contract.get("coarse_map_and_kernel", {})
    mapping_keys = {
        "morphism_id",
        "configuration_map",
        "observable_lift",
        "fibre_partition",
        "conditional_kernel",
        "conditional_expectation",
        "normalization_targets",
        "symmetry_target",
        "retained_root_transport",
        "hidden_root_rule",
        "root_measure",
    }
    check("map-kernel-fields", mapping_keys <= set(mapping), sorted(mapping))
    check(
        "kernel-normalization-formula",
        "Z_fib" in mapping.get("fibre_partition", "")
        and "exp[-beta F_(rho')" in mapping.get("conditional_kernel", "")
        and "E_kappa 1=1" in mapping.get("normalization_targets", ""),
    )
    check(
        "symmetry-root-contract",
        "kappa(h'y|hx)=kappa(y|x)" in mapping.get("symmetry_target", "")
        and "inverse labels" in mapping.get("retained_root_transport", "")
        and "directed-root measures" in mapping.get("root_measure", ""),
    )

    targets = contract.get("compatibility_targets", {})
    check(
        "compatibility-target-separation",
        "L_(rho') I_p" in targets.get("strong_mainline", "")
        and "E_kappa L_(rho') I_p" in targets.get("conditional_projected", "")
        and "normalized" in targets.get("defect", ""),
    )
    check(
        "uniform-target-firewall",
        "uniformly" in targets.get("uniform_target", "")
        and "not" not in targets.get("uniform_target", "").lower(),
    )

    missing = contract.get("missing_evidence", [])
    check("missing-evidence-explicit", isinstance(missing, list) and len(missing) > 0, missing)
    non_claims = " ".join(contract.get("non_claims", []))
    check(
        "physical-nonclaims",
        "No physical Pre-A" in non_claims
        and "QFT" in non_claims
        and "Yang--Mills" in non_claims,
    )
    check(
        "single-next-question",
        isinstance(contract.get("single_next_proof_question"), str)
        and bool(contract["single_next_proof_question"].strip()),
    )

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc002-contract-structure/1.0",
        "run_kind": "primary",
        "audit_id": "PAH-OMC-002-CONTRACT-AUDIT-001",
        "exploration_id": "EXP-001366",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": {
            "PAH-OMC-002": actual_contract,
            "PAH-001": actual_parent,
            "PAH-OMC-001": actual_finite,
        },
        "verdict": "CANDIDATE_NOT_ADMITTED",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "non_claims": [
            "This is a structural contract audit, not an intertwining theorem.",
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-OMC-002-CONTRACT-AUDIT-001 PRIMARY "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"verdict={payload['verdict']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
