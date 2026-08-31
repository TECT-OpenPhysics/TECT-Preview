#!/usr/bin/env python3
"""Fail-closed hostile mutation suite for the A5 R-475 contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any, Callable

__version__ = "1.0.0"
getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "claims" / "A5-SECTOR-A-SYNTHESIS" / "conditional_composition_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A5-SECTOR-A-SYNTHESIS" / "runs" / "2026-09-01-a5-r475-lean-crosscheck" / "hostile.json"

EXPECTED_HYPOTHESES = [
    "A5-H1-CANONICAL-KERNEL-MANIFEST",
    "A1-KERNEL-CONV",
    "A1-SHELL-POSITIVITY",
    "A2-H2-SEXTIC-COERCIVITY",
    "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    "A3-H1-DIM3-Q4-KERNEL",
    "A3-H2-IR-POSITIVITY",
]
EXPECTED_FULL = [
    "A1-PRODUCTION-FUNCTIONAL-REALISATION",
    "A2-FULL-PRODUCTION-WELLPOSED",
    "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
]
EXPECTED_SCALAR = [
    "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
    "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
]
ALIASES = (
    ("claims/a1k", "claims/A1-PRODUCTION-KERNEL-MANIFEST"),
    ("claims/a1f", "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION"),
    ("claims/a2", "claims/A2-FULL-PRODUCTION-WELLPOSED"),
    ("claims/a3f", "claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"),
    ("claims/a3p", "claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS"),
    ("claims/a4", "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"),
    ("claims/a5", "claims/A5-SECTOR-A-SYNTHESIS"),
)


def resolve(value: str) -> Path:
    for alias, canonical in sorted(ALIASES, key=lambda row: -len(row[0])):
        if value == alias or value.startswith(alias + "/"):
            return REPO / (canonical + value[len(alias) :])
    return REPO / value


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def validate(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = manifest.get("theorem_contract")
    if not isinstance(contract, dict):
        return ["theorem_contract missing"]
    if manifest.get("schema") != "tect/a5-t6-conditional-composition/1.1":
        errors.append("schema")
    if manifest.get("claim_id") != "A5-SECTOR-A-SYNTHESIS":
        errors.append("claim_id")
    if manifest.get("candidate_tier") != "T6":
        errors.append("candidate_tier")
    if manifest.get("publication_state") != "T6-PUBLISHED-OPERATOR-CONFIRMED":
        errors.append("publication_state")
    if digest(contract) != manifest.get("theorem_contract_sha256"):
        errors.append("theorem_contract_sha256")
    hypotheses = contract.get("named_hypotheses")
    if hypotheses != EXPECTED_HYPOTHESES or len(hypotheses) != len(set(hypotheses)):
        errors.append("named_hypotheses")
    lifts = contract.get("sub_t6_dependency_lifts")
    if lifts != {
        "A1-PRODUCTION-KERNEL-MANIFEST": "A5-H1-CANONICAL-KERNEL-MANIFEST",
        "A1-PRODUCTION-FUNCTIONAL-REALISATION": "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    }:
        errors.append("sub_t6_dependency_lifts")
    premises = contract.get("premises")
    if not isinstance(premises, list) or len(premises) != 6:
        errors.append("premises_count")
    else:
        tiers = {row.get("id"): row.get("tier") for row in premises if isinstance(row, dict)}
        if {key for key, value in tiers.items() if value == "T6"} != {
            "A2-FULL-PRODUCTION-WELLPOSED",
            "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
            "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
            "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
        }:
            errors.append("premise_t6_partition")
        if {key for key, value in tiers.items() if value != "T6"} != set(lifts or {}):
            errors.append("premise_lift_partition")
    branches = contract.get("branches", {})
    full = branches.get("full_production", {}).get("claim_chain")
    scalar = branches.get("scalar_continuum", {}).get("claim_conjunction")
    if full != EXPECTED_FULL or scalar != EXPECTED_SCALAR or set(full or ()) & set(scalar or ()):
        errors.append("branch_topology")
    try:
        kernel = json.loads(resolve(manifest["numeric_firewall"]["scalar_source"]).read_text(encoding="utf-8"))
        functional = json.loads(resolve(manifest["numeric_firewall"]["full_source"]).read_text(encoding="utf-8"))
        scalar_mass = Decimal(str(kernel["mu2_shell"]))
        p = functional["parameters"]
        full_mass = Decimal(str(p["r"])) - Decimal(str(p["Z"])) ** 2 / (Decimal(4) * Decimal(str(p["Y"])))
        firewall = manifest["numeric_firewall"]
        if scalar_mass != Decimal(firewall["expected_scalar_shell_mass_squared"]):
            errors.append("scalar_mass")
        if abs(full_mass - Decimal(firewall["expected_full_shell_mass_squared"])) >= Decimal(firewall["full_mass_match_tolerance"]):
            errors.append("full_mass")
        if abs(full_mass - scalar_mass) <= Decimal(firewall["required_absolute_difference_gt"]):
            errors.append("mass_separation")
    except (KeyError, OSError, json.JSONDecodeError, ArithmeticError):
        errors.append("numeric_firewall")
    exclusions = " | ".join(contract.get("exclusions", [])).lower()
    for token in ["parameter-identical", "derivative class-ii", "eta_shell", "t=0", "historical", "route-b", "unsmeared", "infinite-volume", "phase transition", "bcc", "sector-b", "t7"]:
        if token not in exclusions:
            errors.append("exclusion:" + token)
    confirmation = manifest.get("operator_confirmation", {})
    if confirmation.get("status") != "CONFIRMED" or confirmation.get("published_bundle_authorized") is not True:
        errors.append("operator_confirmation")
    for key, row in manifest.get("authority", {}).items():
        path = resolve(row.get("path", "__missing__"))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row.get("sha256"):
            errors.append("authority:" + key)
    # The source manifest keeps the weakness map beside (not inside) the theorem
    # contract.  Validate that canonical placement so the unmutated source is a
    # valid baseline while still failing closed if the map is removed or altered.
    weakness_ids = [row.get("id") for row in manifest.get("sector_a_weakness_map", []) if isinstance(row, dict)]
    if len(weakness_ids) != len(set(weakness_ids)) or "FULL-CLASSII-CONSTRUCTIVE-MEASURE" not in weakness_ids or "BCC-EXISTENCE-AND-SELECTION" not in weakness_ids:
        errors.append("weakness_map")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    baseline_errors = validate(baseline)
    checks.append({"name": "unmutated_contract_accepts", "status": "PASS" if not baseline_errors else "FAIL", "errors": baseline_errors})

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("remove_hypothesis", lambda x: x["theorem_contract"]["named_hypotheses"].pop()),
        ("reorder_hypotheses", lambda x: x["theorem_contract"]["named_hypotheses"].reverse()),
        ("promote_tier", lambda x: x.__setitem__("candidate_tier", "T7")),
        ("alter_publication_state", lambda x: x.__setitem__("publication_state", "T7-PUBLISHED")),
        ("tamper_contract_digest", lambda x: x.__setitem__("theorem_contract_sha256", "0" * 64)),
        ("merge_branch_topology", lambda x: x["theorem_contract"]["branches"]["scalar_continuum"]["claim_conjunction"].append(EXPECTED_FULL[0])),
        ("collapse_mass_fork", lambda x: x["numeric_firewall"].__setitem__("expected_full_shell_mass_squared", x["numeric_firewall"]["expected_scalar_shell_mass_squared"])),
        ("remove_t7_exclusion", lambda x: x["theorem_contract"]["exclusions"].__setitem__(-1, "")),
        ("tamper_authority_hash", lambda x: x["authority"]["referee_source"].__setitem__("sha256", "0" * 64)),
        ("remove_operator_confirmation", lambda x: x["operator_confirmation"].__setitem__("status", "UNCONFIRMED")),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        errors = validate(candidate)
        checks.append({"name": name, "status": "PASS" if errors else "FAIL", "errors": errors})

    passed = sum(row["status"] == "PASS" for row in checks)
    output = {
        "schema": "tect/a5-r475-lean-crosscheck-hostile/1.0",
        "claim_id": "A5-SECTOR-A-SYNTHESIS",
        "result_id": "R-475",
        "exploration_id": "EXP-001354",
        "script_version": __version__,
        "verdict": "R475-A5-CONTRACT-HOSTILE-PASS" if passed == len(checks) else "R475-A5-CONTRACT-HOSTILE-FAIL",
        "contract_fingerprint": digest(baseline["theorem_contract"]),
        "checks": checks,
        "assertion_summary": {"passed": passed, "total": len(checks), "mutations_rejected": len(mutations) if all(row["status"] == "PASS" for row in checks[1:]) else 0},
        "evidence_level": "T0 fail-closed hostile contract audit; no analytic or physical promotion",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"R-475 HOSTILE: {output['verdict']} ({passed}/{len(checks)} checks; mutations={len(mutations)})")
    print("Fingerprint:", output["contract_fingerprint"])
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
