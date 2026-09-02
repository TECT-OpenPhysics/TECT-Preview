#!/usr/bin/env python3
"""Non-importing independent audit of the PAH-OMC-002 contract.

The primary lane checks the contract by named sections.  This lane uses an
independent path/value inventory and does not import the primary verifier.
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
    "2026-09-02-pah-omc002-contract/independent.json"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
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

    contract_sha = digest(CONTRACT)
    parent_sha = digest(PARENT)
    finite_sha = digest(FINITE)
    check("manifest-contract", manifest.get("contract", {}).get("sha256") == contract_sha, contract_sha)
    check("manifest-parent", manifest.get("parent", {}).get("sha256") == parent_sha, parent_sha)
    check("manifest-finite", manifest.get("finite_completion", {}).get("sha256") == finite_sha, finite_sha)
    check("contract-schema", contract.get("schema") == "tect/pre-a-owner-morphism-successor-contract/1.0")
    check(
        "owner-status",
        contract.get("contract_id") == "PAH-OMC-002"
        and contract.get("status", {}).get("contract") == "CANDIDATE_NOT_ADMITTED"
        and contract.get("status", {}).get("conditional_projected_intertwining") == "PENDING_EXACT_AUDIT",
    )

    provenance = contract.get("provenance", {})
    check(
        "researcher-only",
        provenance.get("external_source") is False
        and provenance.get("constructed_hypothesis") is True
        and provenance.get("physical_authority") is False,
        provenance,
    )
    firewall = contract.get("preservation_firewall", {})
    check(
        "parent-firewall",
        firewall.get("functional_unchanged") is True
        and firewall.get("move_families_unchanged") is True
        and firewall.get("no_new_hamiltonian_or_counterterm") is True
        and firewall.get("no_q3lock_import") is True
        and firewall.get("no_physical_identification") is True,
        firewall,
    )

    parent = contract.get("parent", {})
    check(
        "parent-links",
        parent.get("packet_id") == "PAH-001"
        and parent.get("sha256") == parent_sha
        and parent.get("finite_completion_contract", {}).get("contract_id") == "PAH-OMC-001"
        and parent.get("finite_completion_contract", {}).get("sha256") == finite_sha,
        parent,
    )

    scope = contract.get("exact_scope", {})
    check(
        "scope-model",
        all(
            phrase in scope.get("fine_carrier", "")
            for phrase in ("relational two-cell complex", "anchor-preserving", "fine-only vertex")
        )
        and scope.get("time") == "External stochastic Markov time only."
        and "physical limit" in scope.get("limits", ""),
        scope,
    )

    transport = contract.get("parameter_transport", {})
    check(
        "transport-identity",
        transport.get("K") == "K'=K and the gauge map is the declared surjection on vertex labels."
        and transport.get("Q") == "Q'=Q; hidden matter occupation is part of the same fixed-Q sector."
        and transport.get("beta") == "beta'=beta>0; no fitted or post-hoc beta rescaling is allowed."
        and "inherited without counterterm" in transport.get("cell_couplings", ""),
        transport,
    )

    morphism = contract.get("coarse_map_and_kernel", {})
    check("morphism-id", morphism.get("morphism_id") == "PAH-COND-GIBBS-BLOCK-001")
    check(
        "kernel-is-finite-gibbs",
        all(
            phrase in morphism.get("conditional_kernel", "")
            for phrase in ("kappa", "exp[-beta F_(rho')", "Z_fib")
        )
        and "sum_y kappa(y|x)g(y)" in morphism.get("conditional_expectation", ""),
        morphism,
    )
    check(
        "map-preserves-cylinders",
        "forget" in morphism.get("configuration_map", "")
        and "f(p_Omega(y))" in morphism.get("observable_lift", "")
        and "E_kappa 1=1" in morphism.get("normalization_targets", ""),
    )
    check(
        "root-transport-explicit",
        "retained-root" in morphism.get("retained_root_transport", "")
        and "hidden leakage" in morphism.get("hidden_root_rule", "")
        and "directed-root" in morphism.get("root_measure", ""),
    )

    targets = contract.get("compatibility_targets", {})
    check(
        "strong-vs-projected-separated",
        targets.get("strong_mainline", "").startswith("L_(rho') I_p")
        and targets.get("conditional_projected", "").startswith("E_kappa L_(rho') I_p")
        and "weaker diagnostic" in targets.get("conditional_projected", ""),
    )
    check(
        "defect-and-uniform-rule",
        "d_(rho,rho')" in targets.get("defect", "")
        and "regulator, volume, shape, source, phase, and exhaustion" in targets.get("uniform_target", ""),
    )

    boundaries = contract.get("known_boundaries", {})
    check(
        "known-r480-boundary",
        "R-480/R-481" in boundaries.get("natural_pullback", "")
        and "does not change the strong lift" in boundaries.get("conditional_kernel_role", ""),
        boundaries,
    )
    missing = contract.get("missing_evidence", [])
    check("open-evidence-list", isinstance(missing, list) and bool(missing), missing)
    check(
        "physical-firewall",
        any("No physical Pre-A" in item for item in contract.get("non_claims", []))
        and any("Yang--Mills" in item for item in contract.get("non_claims", [])),
    )
    check(
        "ordered-limits-held",
        contract.get("ordered_limit_firewall", {}).get("interchange_claimed") is False
        and contract.get("ordered_limit_firewall", {}).get("status") == "NOT_ADMITTED",
    )
    check(
        "single-question",
        bool(str(contract.get("single_next_proof_question", "")).strip())
        and bool(str(contract.get("revisit_condition", "")).strip()),
    )

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc002-contract-structure-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-002-CONTRACT-AUDIT-001",
        "exploration_id": "EXP-001366",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": {
            "PAH-OMC-002": contract_sha,
            "PAH-001": parent_sha,
            "PAH-OMC-001": finite_sha,
        },
        "verdict": "CANDIDATE_NOT_ADMITTED",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "non_claims": [
            "This independent lane checks contract structure only; it does not prove conditional or strong intertwining.",
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
        ],
    }
    write_json(output, payload)
    print(
        "PAH-OMC-002-CONTRACT-AUDIT-001 INDEPENDENT "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}"
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
